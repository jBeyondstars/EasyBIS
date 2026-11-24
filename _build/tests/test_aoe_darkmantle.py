"""The Forever Darkmantle set is eligible on the IDs measured by WoWSims."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import aoe_eligibility as rules  # noqa: E402
import fdb  # noqa: E402
import simulate_aoe as sim  # noqa: E402
import simulate_dungeon as dungeon  # noqa: E402


class DarkmantleTest(unittest.TestCase):
    def test_three_rogue_profiles_measure_every_forever_piece_on_both_sides(self):
        db = fdb.load(BUILD / "cache/ForeverDB")
        self.assertEqual(rules.client_stats(db.gear[226829]["stats"]), {"agility": 25, "spirit": 10, "crit": 14})
        self.assertEqual(rules.client_stats(db.gear[22005]["stats"]), {"agility": 26, "strength": 13, "crit": 14})
        for name in ("assassination", "combat", "subtlety"):
            profile = sim.read(sim.PROFILES / f"rogue-{name}.json")
            for slot, (item, _) in rules.DARKMANTLE.items():
                with self.subTest(name=name, slot=slot, item=item):
                    self.assertIn(item, profile["slots"][slot])
                    vendors = {source[7]: int(source[1]) for source in db.items[item]["sources"] if source[0] == "v"}
                    self.assertEqual(vendors, {"a": 230319, "h": 230317})
                    for side in profile["races"]:
                        self.assertIn(item, rules.candidates_for_slot(db, profile, slot, side))

    @unittest.skipUnless(all(os.getenv(key) for key in ("EASYBIS_WOWSIMS", "EASYBIS_PACK_CLI", "EASYBIS_ROUTE_CLI")),
                         "native pack and dungeon simulators required")
    def test_cap_only_grants_energy_when_it_completes_four_pieces(self):
        root = Path(os.environ["EASYBIS_WOWSIMS"])
        pack_cli = Path(os.environ["EASYBIS_PACK_CLI"])
        route_cli = Path(os.environ["EASYBIS_ROUTE_CLI"])
        profile = sim.read(sim.PROFILES / "rogue-combat.json")
        rotation = sim.read(sim.PROFILES / profile["dungeonRotation"])
        gear = sim.reference_equipment(root, pack_cli, profile)
        equipped = {piece.get("id") for piece in gear["items"]}
        self.assertEqual(equipped & {item for item, _ in rules.DARKMANTLE.values()}, {226829, 226826, 226830, 226831})
        iterations = 128
        with tempfile.TemporaryDirectory() as work:
            for route in (False, True):
                for keep_bracers in (False, True):
                    with self.subTest(route=route, keep_bracers=keep_bracers):
                        samples = []
                        for cap in (False, True):
                            req = sim.make_request(profile, profile["races"]["a"], rotation, gear,
                                                   "head", 226829 if cap else 0, iterations)
                            player = req["raid"]["parties"][0]["players"][0]
                            if not keep_bracers:
                                player["equipment"]["items"][sim.EQUIPMENT_SLOTS.index("wrist")] = {}
                            if not cap:
                                # Control: every stat on item 226829, without its set ID.
                                stats = [0] * 28
                                stats[1], stats[2], stats[13], stats[18], stats[27] = 25, 21, 10, 14, 150
                                player["bonusStats"] = {"stats": stats}
                            if route:
                                req = dungeon.bind_request(req, profile, root, [], 0, dungeon.SEED)
                            result = sim.run_request(route_cli if route else pack_cli, Path(work), req)
                            unit = result["raidMetrics"]["parties"][0]["players"][0]
                            energy = [r for r in unit["resources"] if r["id"].get("spellId") == 27788]
                            if keep_bracers and cap:
                                self.assertEqual(len(energy), 1)
                                self.assertGreater(energy[0]["actualGain"], 0)
                                self.assertEqual(energy[0]["gain"], 20 * energy[0]["events"])
                            else:
                                self.assertFalse(energy)
                            samples.append(dungeon.route.route_samples(result, iterations)[0] if route
                                           else sim.samples(result, iterations, profile["damageChecks"])[0])
                        if not keep_bracers:
                            self.assertEqual(*samples)
