"""A hunter's hand slots must help while the player shoots from range."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import aoe_eligibility as eligibility
import aoe_weapons as weapons
import simulate_aoe as sim
import simulate_dungeon as dungeon
from test_addon import Game, lupa
from test_ui import find, open_dropdown, texts


class RangedHunterTest(unittest.TestCase):
    profiles = ("hunter-beast-mastery", "hunter-marksmanship", "hunter-survival")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_archived_melee_selection_opens_ranged_survival(self):
        for faction, mode in (("Alliance", "pve"), ("Horde", "pvp")):
            with self.subTest(faction=faction):
                saved = f"EasyBISCharDB = {{ class = 'HUNTER', spec = 3, list = '{mode}' }}"
                game = Game(locale="frFR", faction=faction, cls="HUNTER", saved=saved)
                ns = game.ns
                self.assertEqual(ns.Browser.Target(), ("HUNTER", 4, mode))
                self.assertEqual(ns.char.spec, 4)
                self.assertEqual(list(ns.Index.SpecOrder("HUNTER").values()), [1, 2, 4])
                self.assertIsNone(ns.Index.SpecName("HUNTER", 3))
                ns.Browser.Open()
                open_dropdown(game, ns.Browser.window.spec.button)
                choices = texts(find(game.stub.menu, ns.ClassName("HUNTER")))
                self.assertIn("Survie (distance)", choices)
                self.assertNotIn("Survie (mêlée)", choices)
                self.assertEqual(game.slash("list 3"), game.slash("list 4"))
                hits = ns.Index.ForItem(13285) or {}
                self.assertNotIn("HUNTER", [hit["class"] for hit in hits.values()])
                picks = ns.Ladders.For("HUNTER", 4, mode)
                self.assertTrue(picks.main.best[1].id)
                for slot in (picks.main, picks.off):
                    for group in (slot.best, slot.alts, slot.other):
                        self.assertNotIn(13285, [p.id for p in group.values()])
                self.assertIsNone(ns.Ladders.Measured("HUNTER", 4, "pve"))
                self.assertIsNone(ns.Rows.AoeList("HUNTER", 3))
                self.assertTrue(len(ns.Rows.AoeList("HUNTER", 4).main))

    def test_melee_stats_and_hit_procs_do_not_qualify_a_hunter_weapon(self):
        for spec in (1, 2, 3):
            profile = {"class": "HUNTER", "spec": spec, "itemDamageChecks": {"1728": {"29155": 1}}}
            for stats in ({}, {"strength": 20}, {"expertise": 12}, {"ap": 30}, {"spell": 20, "hit": 10}):
                with self.subTest(spec=spec, stats=stats), self.assertRaises(ValueError):
                    eligibility.validate_hunter_hand(profile, 1728, stats)
            for stats in ({"agility": 10}, {"rap": 25}, {"ap": 20, "rap": 20}, {"strength": 4, "crit": 14}):
                eligibility.validate_hunter_hand(profile, 1, stats)

    def test_dalrends_defensive_offhand_requires_the_complete_ranged_ap_bonus(self):
        for filename in self.profiles:
            profile = sim.read(sim.PROFILES / (filename + ".json"))
            pairs = [pair for pair in profile["weaponSets"] if 12939 in pair]
            self.assertEqual(pairs, [[12940, 12939]])
            eligibility.validate_hunter_hand(profile, 12939, {})
            for invalid in ([], [[12783, 12939]], [[12940, 12939], [12783, 12939]]):
                with self.subTest(profile=filename, pairs=invalid), self.assertRaises(ValueError):
                    eligibility.validate_hunter_hand(dict(profile, weaponSets=invalid), 12939, {})
            with self.assertRaisesRegex(ValueError, "12940"):
                weapons.validate_pair_client(None, profile, 12783, 12939)

    @unittest.skipUnless(os.getenv("EASYBIS_WOWSIMS") and os.getenv("EASYBIS_PACK_CLI"),
                         "native pack simulator required")
    def test_dalrends_two_pieces_match_fifty_ranged_attack_power(self):
        cli = Path(os.environ["EASYBIS_PACK_CLI"])
        p = sim.read(sim.PROFILES / "hunter-survival.json")
        gear = sim.reference_equipment(Path(os.environ["EASYBIS_WOWSIMS"]), cli, p)
        rotation = sim.read(sim.PROFILES / p["dungeonRotation"])
        damage = {}
        with tempfile.TemporaryDirectory() as work:
            for control, off, rap in (("empty", 0, 0), ("set", 12939, 0), ("ranged_ap", 0, 50)):
                req = weapons.request(p, p["races"]["a"], rotation, gear, (12940, off), 128)
                if rap:
                    index = eligibility.STAT_IDS["rap"][0]
                    req["raid"]["parties"][0]["players"][0]["bonusStats"] = {"stats": [0] * index + [rap]}
                result = sim.run_request(cli, Path(work), req)
                damage[control] = sim.samples(result, 128, p["damageChecks"])[0]
        self.assertEqual(damage["set"], damage["ranged_ap"])
        gain, error = sim.difference(damage["set"], damage["empty"])
        self.assertGreater(gain, 3 * error)

    @unittest.skipUnless(all(os.getenv(key) for key in ("EASYBIS_WOWSIMS", "EASYBIS_PACK_CLI", "EASYBIS_ROUTE_CLI")),
                         "native pack and dungeon simulators required")
    def test_player_deals_damage_from_range_on_the_pack_and_each_dungeon_wave(self):
        root = Path(os.environ["EASYBIS_WOWSIMS"])
        pack_cli = Path(os.environ["EASYBIS_PACK_CLI"])
        route_cli = Path(os.environ["EASYBIS_ROUTE_CLI"])
        for slug in self.profiles:
            p = sim.read(sim.PROFILES / (slug + ".json"))
            rotation = sim.read(sim.PROFILES / p["dungeonRotation"])
            gear = sim.reference_equipment(root, pack_cli, p)
            for race in p["races"].values():
                for route in (False, True):
                    with self.subTest(profile=slug, race=race, route=route), tempfile.TemporaryDirectory() as work:
                        req = sim.make_request(p, race, rotation, gear, None, 0, 64)
                        if route:
                            req = dungeon.bind_request(req, p, root, [], 0, dungeon.SEED)
                        result = sim.run_request(route_cli if route else pack_cli, Path(work), req)
                        player = result["raidMetrics"]["parties"][0]["players"][0]
                        self.assertGreaterEqual(req["raid"]["parties"][0]["players"][0]["distanceFromTarget"], 8)
                        for action in player["actions"]:
                            if action["id"].get("otherId") == "OtherActionAttack" or action["id"].get("spellId") in (
                                    14266, 14271, 20910, 1310536):
                                self.assertFalse(any(t.get("damage", 0) or t.get("casts", 0) for t in action["targets"]))
                        shot = next(a for a in player["actions"] if a["id"].get("otherId") == "OtherActionShoot")
                        hit = {t["unitIndex"] for t in shot["targets"] if t.get("damage", 0) > 0}
                        targets = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
                        for wave in ((targets[:4], targets[4:5], targets[5:]) if route else (targets,)):
                            self.assertTrue(hit.intersection(wave))
                        if route:
                            dungeon.route.route_samples(result, 64)
                        else:
                            sim.samples(result, 64, p["damageChecks"], p.get("requiredPet"))
