"""Dungeon route geometry, health accounting and optional native checks."""
import copy
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_encounter as route
import aoe_route_rotation as rotations
import simulate_aoe as sim


class DungeonRouteTest(unittest.TestCase):
    def test_pull_sizes_and_health(self):
        enemies = route.encounter()["targets"]
        self.assertEqual([row["stats"][29] for row in enemies], [7500] * 4 + [22500] + [7500] * 3 + [2500] * 4)
        self.assertEqual([row["disabledAtStart"] for row in enemies], [False] * 4 + [True] * 8)
        self.assertTrue(all(row["level"] == 60 for row in enemies))
        self.assertTrue(all(row["targetInputs"][3]["numberValue"] == 1 for row in enemies))
        self.assertEqual(len({row["id"] for row in enemies}), len(enemies))

    def test_damage_and_duration_are_paired_by_iteration(self):
        targets = [{
            "unitIndex": index, "name": config["name"],
            "resources": [{"id": {"spellId": route.GROUP_SPELL_ID}, "actualGain": -(2 * config["stats"][29] - 20)}],
        } for index, config in enumerate(route.encounter()["targets"])]
        targets[0]["threat"] = {"allValues": [1 / 40, 1 / 50]}
        actions = [{"targets": [{"unitIndex": t["unitIndex"], "damage": 20} for t in targets]}]
        result = {"iterationsDone": 2, "avgIterationDuration": 45, "encounterMetrics": {"targets": targets},
                  "raidMetrics": {"parties": [{"players": [{"actions": actions}]}], "dps": {"allValues": [2.5, 2.8]}}}
        self.assertEqual(route.route_samples(result, 2), ([100, 140], [40, 50]))
        targets[0]["resources"][0]["actualGain"] += 5
        with self.assertRaisesRegex(ValueError, "account for its health"):
            route.route_samples(result, 2)
        targets[0]["threat"]["allValues"][0] = 0
        with self.assertRaisesRegex(ValueError, "completion"):
            route.route_samples(result, 2)

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_ROUTE_CLI and EASYBIS_WOWSIMS for the native route smoke")
    def test_drinking_uses_current_capacity_and_keeps_pet_resources_and_cooldowns(self):
        cli, root = Path(os.environ["EASYBIS_ROUTE_CLI"]), Path(os.environ["EASYBIS_WOWSIMS"])
        cases = (("priest-shadow", "trinket", 18371), ("hunter-survival", "hands", 15063),
                 ("hunter-survival", "hands", 279257), ("warlock-demonology", "neck", 0),
                 ("druid-feral-bear", "neck", 0), ("druid-feral-cat", "neck", 0),
                 ("rogue-combat", "neck", 0), ("warrior-fury", "neck", 0))
        for slug, slot, item in cases:
            with self.subTest(slug=slug, item=item), tempfile.TemporaryDirectory() as temp:
                profile = sim.read(sim.PROFILES / (slug + ".json"))
                gear = sim.reference_equipment(root, cli, profile)
                raw = sim.read(sim.PROFILES / profile["dungeonRotation"]) if "dungeonRotation" in profile else (
                    sim.read_preset(root, cli, root / profile["rotation"]))
                req = sim.make_request(profile, profile["races"]["a"], raw, gear, slot, item, 16, item == 18371)
                player = req["raid"]["parties"][0]["players"][0]
                if item == 18371:
                    # Exercise drinking with a reduced mana cap, regardless of when
                    # the current damage set would normally reach the trinket's threshold.
                    use = next(row["action"] for row in player["rotation"]["priorityList"]
                               if row["action"].get("castSpell", {}).get("spellId", {}).get("itemId") == item)
                    use["condition"] = {"cmp": {"op": "OpGe", "lhs": {"currentTime": {}},
                                                "rhs": {"const": {"val": "1s"}}}}
                player["rotation"] = rotations.route_rotation(profile, player["rotation"], root)
                req["encounter"] = route.encounter()
                req["simOptions"].update(randomSeed="80000", debugFirstIteration=True)
                result = sim.run_request(cli, Path(temp), req)
                samples = route.route_samples(result, 16)
                player = result["raidMetrics"]["parties"][0]["players"][0]
                drinks = [row for row in player["resources"] if row["id"].get("spellId") == route.DRINK_SPELL_ID]
                for pet in player.get("pets", []):
                    self.assertFalse(any(row["id"].get("spellId") == route.DRINK_SPELL_ID for row in pet["resources"]))
                if profile["class"] in ("ROGUE", "WARRIOR"):
                    self.assertEqual(drinks, [])
                    for target in req["encounter"]["targets"]:
                        target["targetInputs"][3]["numberValue"] = 0
                    dry = sim.run_request(cli, Path(temp), req)
                    self.assertEqual(samples, route.route_samples(dry, 16))
                    continue
                self.assertEqual({row["id"]["tag"] for row in drinks}, {2, 3})
                for row in drinks:
                    self.assertEqual((row["events"], row["type"]), (16, "ResourceTypeMana"))
                    self.assertGreater(row["gain"], 0)
                    self.assertLessEqual(row["actualGain"], row["gain"])
                starts = re.findall(r"\[([\d.]+)\] .*?Dungeon pack (\d) starts at full mana: ([\d.]+) / ([\d.]+)",
                                    result["logs"])
                self.assertEqual([pack for _, pack, _, _ in starts], ["1", "2", "3"])
                self.assertTrue(all(actual == maximum for _, _, actual, maximum in starts))
                if slug == "priest-shadow":
                    # The trinket reduces maximum intellect/mana long after returning its own mana.
                    self.assertLess(float(starts[1][3]), float(starts[0][3]))
                    self.assertEqual(starts[1][3], starts[2][3])
                    for time, _, _, _ in starts:
                        self.assertIn(f"[{time}] [ (#1)] Casting {{SpellID: 10894}}", result["logs"])
                if slug == "hunter-survival":
                    shots = [a for a in player["actions"] if a["id"].get("otherId") == "OtherActionShoot"]
                    self.assertTrue(any(t["damage"] > 0 for a in shots for t in a["targets"]))

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_ROUTE_CLI and EASYBIS_WOWSIMS for the native route smoke")
    def test_native_transitions_missiles_pet_and_parallel_seeds(self):
        cli, root = Path(os.environ["EASYBIS_ROUTE_CLI"]), Path(os.environ["EASYBIS_WOWSIMS"])
        profile = sim.read(sim.PROFILES / "hunter-beast-mastery.json")
        gear = sim.reference_equipment(root, cli, profile)
        rotation = sim.read_preset(root, cli, sim.PROFILES / profile["dungeonRotation"])
        req = sim.make_request(profile, profile["races"]["a"], rotation, gear, "neck", 0, 6)
        req["encounter"] = route.encounter()
        req["simOptions"]["debugFirstIteration"] = True
        with tempfile.TemporaryDirectory() as temp:
            result = sim.run_request(cli, Path(temp), req)
            parallel = route.route_samples(result, 6)
            for index in range(6):
                single = copy.deepcopy(req)
                single["simOptions"].update(randomSeed=str(sim.SEED + index), iterations=1, debugFirstIteration=False)
                sample = route.route_samples(sim.run_request(cli, Path(temp), single), 1)
                for amounts, sample_amount in zip(parallel, sample, strict=True):
                    self.assertAlmostEqual(amounts[index], sample_amount[0], places=6)
        deaths, hits = {}, []
        for line in result["logs"].splitlines():
            match = re.search(r"^\[([\d.]+)\] \[(Pack (\d) (?:elite|normal) \d+)\] Died", line)
            if match:
                deaths[match[2]] = float(match[1])
            match = re.search(r"^\[([\d.]+)\] \[([^\]]+)\] \[(Pack (\d) (?:elite|normal) \d+)\].*?for ([\d.]+) damage", line)
            if match and float(match[5]) > 0:
                hits.append((float(match[1]), match[2], match[3], int(match[4])))
        self.assertEqual(len(deaths), 12)
        for pack in (1, 2, 3):
            pack_hits = [(t, actor, enemy) for t, actor, enemy, n in hits if n == pack]
            self.assertTrue(any("Raptor" in actor for _, actor, _ in pack_hits))
            self.assertTrue(any(actor.strip() == "(#1)" for _, actor, _ in pack_hits))
            self.assertTrue(all(t <= deaths[enemy] for t, _, enemy in pack_hits))
            if pack > 1:
                last = max(t for name, t in deaths.items() if name.startswith(f"Pack {pack - 1} "))
                self.assertTrue(all(t >= last + route.TRAVEL_SECONDS - 0.011 for t, _, _ in pack_hits))


if __name__ == "__main__":
    unittest.main()
