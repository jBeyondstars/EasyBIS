"""Melee weapons compete with the same partners and keep their real effects."""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import aoe_eligibility as eligibility  # noqa: E402
import aoe_weapons as weapons  # noqa: E402
import fdb  # noqa: E402
import simulate_aoe as sim  # noqa: E402


class MeleeWeaponComparisonTest(unittest.TestCase):
    def test_grid_keeps_two_handers_and_excludes_unique_conflicts(self):
        profile = {"slots": {"main": [1, 2, 3], "off": [2, 4, 5]}}
        native = {1: {"handType": 4}, 2: {"handType": 2, "unique": True},
                  3: {"handType": 1, "limitCategory": 107}, 4: {"handType": 3, "limitCategory": 107},
                  5: {"handType": 2}}
        db = SimpleNamespace(items={i: {"flags": "", "limit": None} for i in native})
        self.assertEqual(weapons.complete_melee_sets(profile, native, db),
                         {(1, 0), (2, 4), (2, 5), (3, 2), (3, 5)})

    def test_rare_eligible_weapons_share_partners_across_rogues_and_fury(self):
        for slug in ("rogue-combat", "rogue-subtlety", "warrior-fury"):
            profile = sim.read(sim.PROFILES / f"{slug}.json")
            pairs = set(map(tuple, profile["weaponSets"]))
            with self.subTest(profile=slug):
                # Ironfoe and Sword of Zeal are main-hand only. Flurry Axe can be worn twice.
                for main in (11684, 6622, 279259, 871, 12590):
                    self.assertIn((main, 871), pairs)
                    if main != 12590:
                        self.assertIn((main, 12590), pairs)
                self.assertNotIn((12590, 12590), pairs)
                self.assertIn((12940, 12939), pairs)
                self.assertFalse({11684, 6622} & set(profile["slots"]["off"]))

    def test_feral_paw_procs_and_hybrid_two_hander_remain_legal(self):
        db = fdb.load(BUILD / "cache/ForeverDB")
        cat = sim.read(sim.PROFILES / "druid-feral-cat.json")
        for side in cat["races"]:
            pool = weapons.candidates_for_slot(db, cat, "main", side)
            # Include the high Agility/hit trident and the Strength mace as
            # well as the unusual proc weapons when choosing finalists.
            finalists = {11684, 12590, 279910, 13167}
            self.assertTrue(finalists.issubset(pool))
            self.assertTrue(finalists.issubset(cat["slots"]["main"]))
            self.assertFalse({871, 6622, 279259, 9449} & pool)
        arms = sim.read(sim.PROFILES / "warrior-arms.json")
        stats = eligibility.client_stats(db.gear[279260]["stats"])
        self.assertGreater(stats["spell"], 0)
        self.assertEqual(stats["strength"], 18)
        weapons.validate_client(db, arms, "main", 279260, stats)
        for slug in ("warrior-arms", "paladin-retribution"):
            profile = sim.read(sim.PROFILES / f"{slug}.json")
            self.assertIn([279260, 0], profile["weaponSets"])
            self.assertTrue(all(off == 0 for _, off in profile["weaponSets"]))

    @unittest.skipUnless(os.getenv("EASYBIS_WOWSIMS") and os.getenv("EASYBIS_PACK_CLI"), "native pack simulator required")
    def test_mutilate_uses_both_daggers_on_its_primary_target(self):
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_PACK_CLI"])
        profile = sim.read(sim.PROFILES / "rogue-assassination.json")
        gear = sim.reference_equipment(root, cli, profile)
        rotation = sim.read_preset(root, cli, sim.PROFILES / profile["dungeonRotation"])
        pair = (2163, 11635)
        self.assertIn(list(pair), profile["weaponSets"])
        request = weapons.request(profile, profile["races"]["a"], rotation, gear, pair, 128)
        with tempfile.TemporaryDirectory() as work:
            result = sim.run_request(cli, Path(work), request)
        sim.samples(result, 128, profile["damageChecks"])
        primary = result["encounterMetrics"]["targets"][0]["unitIndex"]
        player = result["raidMetrics"]["parties"][0]["players"][0]
        strikes = {a["id"]["tag"] for a in player["actions"] if a["id"].get("spellId") == 1241584
                   and any(t["unitIndex"] == primary and t["damage"] > 0 for t in a["targets"])}
        self.assertEqual(strikes, {14, 15})

    @unittest.skipUnless(os.getenv("EASYBIS_WOWSIMS") and os.getenv("EASYBIS_PACK_CLI"), "native pack simulator required")
    def test_native_extra_attacks_and_auras_on_real_pack_rotations(self):
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_PACK_CLI"])
        cases = (("warrior-fury", (11684, 871), (15494, 18797), ()),
                 ("warrior-fury", (6622, 12590), (), (8191, 16551)),
                 ("druid-feral-cat", (11684, 13385), (15494,), ()),
                 ("druid-feral-cat", (12590, 13385), (), (16551,)))
        with tempfile.TemporaryDirectory() as work:
            for slug, pair, extra, buffs in cases:
                profile = sim.read(sim.PROFILES / f"{slug}.json")
                gear = sim.reference_equipment(root, cli, profile)
                rotation_path = sim.PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile else root / profile["rotation"]
                rotation = sim.read_preset(root, cli, rotation_path)
                request = weapons.request(profile, profile["races"]["a"], rotation, gear, pair, 128)
                result = sim.run_request(cli, Path(work), request)
                sim.samples(result, 128, profile["damageChecks"])
                player = result["raidMetrics"]["parties"][0]["players"][0]
                with self.subTest(profile=slug, pair=pair):
                    for tag in extra:
                        swings = [a for a in player["actions"] if a["id"].get("otherId") == "OtherActionAttack"
                                  and a["id"].get("tag") == tag]
                        self.assertGreater(sum(t["damage"] for a in swings for t in a["targets"]), 0)
                    for spell in buffs:
                        procs = [a for a in player["auras"] if a["id"].get("spellId") == spell]
                        self.assertGreater(sum(a["uptimeSecondsAvg"] for a in procs), 0)
