"""The Shadow Priest must stay in Shadowform on the short pack and the entire dungeon."""
import copy
import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_encounter as dungeon
import aoe_route_rotation
import simulate_aoe as sim


class ShadowformTest(unittest.TestCase):
    def test_profile_starts_in_shadowform(self):
        profile = sim.read(sim.PROFILES / "priest-shadow.json")
        self.assertIs(profile["player"]["dpsPriest"]["options"]["classOptions"].get("preShadowform"), True)

    def assert_shadowform(self, result, durations):
        player = result["raidMetrics"]["parties"][0]["players"][0]
        auras = [a for a in player["auras"] if a["id"].get("spellId") == 15473]
        self.assertEqual(len(auras), 1)
        aura = auras[0]
        self.assertAlmostEqual(aura["procsAvg"], 1, msg="Shadowform must activate once per iteration")
        self.assertEqual(aura["aggregatorData"]["n"], len(durations))
        self.assertAlmostEqual(aura["uptimeSecondsAvg"], result["avgIterationDuration"], places=7)
        self.assertTrue(math.isclose(aura["aggregatorData"]["sumSq"], sum(t*t for t in durations), rel_tol=1e-8))
        events = re.findall(r"^\[([\d.]+)\] \[ [^(]*\(#1\)\] Aura (gained|faded): \{SpellID: 15473\}",
                            result["logs"], re.MULTILINE)
        self.assertEqual([event for _, event in events], ["gained", "faded"])
        self.assertEqual(float(events[0][0]), 0)
        self.assertAlmostEqual(float(events[1][0]), result["firstIterationDuration"], delta=0.006)

    def check_native(self, cli, route):
        root = Path(os.environ["EASYBIS_WOWSIMS"])
        profile = sim.read(sim.PROFILES / "priest-shadow.json")
        gear = sim.reference_equipment(root, cli, profile)
        rotation = sim.read(sim.PROFILES / profile["dungeonRotation"])
        for race in profile["races"].values():
            req = sim.make_request(profile, race, rotation, gear, "neck", 0, 48)
            req["simOptions"].update(randomSeed="89000", debugFirstIteration=True)
            if route:
                req["encounter"] = dungeon.encounter()
                player = req["raid"]["parties"][0]["players"][0]
                player["rotation"] = aoe_route_rotation.route_rotation(profile, player["rotation"], root)
            with self.subTest(race=race), tempfile.TemporaryDirectory() as work:
                result = sim.run_request(cli, Path(work), req)
                if route:
                    _, durations = dungeon.route_samples(result, 48)
                    starts = re.findall(r"Dungeon pack (\d) starts at full mana", result["logs"])
                    self.assertEqual(starts, ["1", "2", "3"])
                else:
                    sim.samples(result, 48, profile["damageChecks"])
                    durations = [sim.SECONDS] * 48
                self.assert_shadowform(result, durations)

                # The native engine still registers an inactive aura. Finding the ID alone is insufficient.
                control = copy.deepcopy(req)
                options = control["raid"]["parties"][0]["players"][0]["dpsPriest"]["options"]["classOptions"]
                options.pop("preShadowform")
                absent = sim.run_request(cli, Path(work), control)
                absent_aura = next(a for a in absent["raidMetrics"]["parties"][0]["players"][0]["auras"]
                                   if a["id"].get("spellId") == 15473)
                self.assertEqual((absent_aura["procsAvg"], absent_aura["uptimeSecondsAvg"]), (0, 0))
                with self.assertRaisesRegex(AssertionError, "Shadowform must activate"):
                    self.assert_shadowform(absent, durations)

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_PACK_CLI and EASYBIS_WOWSIMS for the native 15-second pack")
    def test_native_short_pack(self):
        self.check_native(Path(os.environ["EASYBIS_PACK_CLI"]), route=False)

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_ROUTE_CLI and EASYBIS_WOWSIMS for the native dungeon")
    def test_native_whole_dungeon_including_transitions(self):
        self.check_native(Path(os.environ["EASYBIS_ROUTE_CLI"]), route=True)


if __name__ == "__main__":
    unittest.main()
