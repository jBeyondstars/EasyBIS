"""Single-target priorities, target gates and equipment activations on the dungeon route."""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_encounter as encounter
import aoe_route_rotation as rotations
import simulate_aoe as sim


def cast(**action_id):
    return {"action": {"castSpell": {"spellId": action_id}}}


class RouteRotationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.profile = sim.read(sim.PROFILES / "warlock-affliction.json")
        self.rotation = sim.read(sim.PROFILES / self.profile["dungeonRotation"])
        self.cached_spell = cast(spellId=11713)
        self.cached_spell["action"]["castSpell"]["target"] = {"type": "Target", "index": 0}
        self.cached_spell["action"]["condition"] = {"dotIsActive": {"targetUnit": {"type": "Target", "index": 0}}}
        self.preset = {
            "priorityList": [cast(itemId=1234), cast(otherId="OtherActionPotion"),
                             {"action": {"autocastOtherCooldowns": {}}},
                             {"action": {"groupReference": {"groupName": "Dots"}}}],
            "groups": [{"name": "Dots", "actions": [cast(itemId=1234), self.cached_spell]}],
            "valueVariables": [{"name": "time left", "value": {"timeUntilTargetDies": {
                "targetUnit": {"type": "Target", "index": 0}}}}],
        }
        path = self.root / "ui/specs" / rotations.SINGLE_TARGET[("WARLOCK", 1)]
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"player": {"rotation": self.preset}}), encoding="utf8")

    def test_native_request_activation_survives_before_the_single_target_branch(self):
        gear = {"items": [{} for _ in sim.EQUIPMENT_SLOTS]}
        for passive, wait in ((False, 0), (False, 4), (True, 0)):
            with self.subTest(passive=passive, wait=wait):
                req = sim.make_request(self.profile, self.profile["races"]["a"], self.rotation, gear,
                                       "trinket", 1234, 2, True, passive, wait)
                original = req["raid"]["parties"][0]["players"][0]["rotation"]
                before = copy.deepcopy(original)
                routed = rotations.route_rotation(self.profile, original, self.root)
                rows = routed["priorityList"]
                self.assertEqual(rows[:2], before["priorityList"][:2])
                self.assertEqual(rows[0]["action"]["castSpell"]["spellId"], {"itemId": 1234})
                branch = rows[2]["action"]
                self.assertEqual(branch["groupReference"]["groupName"], "Dungeon single target")
                self.assertEqual(branch["condition"], {"cmp": {"op": "OpEq", "lhs": {"numberTargets": {}},
                                                               "rhs": {"const": {"val": "1"}}}})
                self.assertEqual(rows[3:], before["priorityList"][2:])
                groups = {g["name"]: g["actions"] for g in routed["groups"]}
                self.assertEqual(groups["Dungeon single target"], [self.preset["priorityList"][-1]])
                self.assertEqual(len(groups["Dots"]), 1)
                action = groups["Dots"][0]["action"]
                self.assertEqual(action["castSpell"]["target"], {"type": "CurrentTarget"})
                self.assertEqual(action["condition"]["dotIsActive"]["targetUnit"], {"type": "CurrentTarget"})
                self.assertEqual(routed["valueVariables"][0]["value"]["timeUntilTargetDies"]["targetUnit"],
                                 {"type": "CurrentTarget"})
                self.assertEqual(original, before)

    def test_independent_results_cannot_change_the_cached_class_actions(self):
        first = rotations.route_rotation(self.profile, self.rotation, self.root)
        expected = copy.deepcopy(first)
        first["groups"][0]["actions"][0]["action"]["castSpell"]["spellId"]["spellId"] = 0
        first["valueVariables"][0]["value"] = {}
        second = rotations.route_rotation(self.profile, self.rotation, self.root)
        self.assertEqual(second, expected)

    def test_shaman_and_hunter_gates_match_the_pack_and_spell(self):
        for slug in ("shaman-elemental", "shaman-enhancement", "hunter-beast-mastery", "hunter-marksmanship"):
            with self.subTest(slug=slug):
                profile = sim.read(sim.PROFILES / (slug + ".json"))
                raw = sim.read(sim.PROFILES / profile["dungeonRotation"])
                before = copy.deepcopy(raw)
                after = rotations.route_rotation(profile, raw, self.root)
                old_rows = [*before["priorityList"], *(r for g in before.get("groups", []) for r in g["actions"])]
                new_rows = [*after["priorityList"], *(r for g in after.get("groups", []) for r in g["actions"])]
                gated = 0
                for old, new in zip(old_rows, new_rows, strict=True):
                    spell = old["action"].get("castSpell", {}).get("spellId", {}).get("spellId")
                    if spell not in (10587, 14295):
                        self.assertEqual(old, new)
                        continue
                    gated += 1
                    first, second = new["action"]["condition"]["and"]["vals"]
                    self.assertEqual(first, {"cmp": {"op": "OpGe", "lhs": {"numberTargets": {}},
                                                     "rhs": {"const": {"val": "2"}}}})
                    if spell == 10587:
                        self.assertEqual(second, {"cmp": {"op": "OpLe", "lhs": {"totemRemainingTime": {"totemType": "Fire"}},
                                                          "rhs": {"const": {"val": "0s"}}}})
                    else:
                        self.assertEqual(second, old["action"]["condition"])
                self.assertEqual(gated, 1)
                self.assertEqual(before, raw)

    def test_shadow_wand_is_last_and_only_fills_a_mana_gap(self):
        profile = sim.read(sim.PROFILES / "priest-shadow.json")
        raw = sim.read(sim.PROFILES / profile["dungeonRotation"])
        rows = rotations.route_rotation(profile, raw, self.root)["priorityList"]
        self.assertEqual(rows[:-1], raw["priorityList"])
        flay = {"spellId": 18807}
        action = rows[-1]["action"]
        self.assertEqual(action["channelSpell"], {"spellId": {"spellId": 5019},
                                                  "interruptIf": {"const": {"val": "true"}}})
        self.assertCountEqual(action["condition"]["and"]["vals"], [
            {"gcdIsReady": {}}, {"not": {"val": {"spellIsChanneling": {"spellId": flay}}}},
            {"cmp": {"op": "OpLt", "lhs": {"currentMana": {}}, "rhs": {"spellCurrentCost": {"spellId": flay}}}},
        ])

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_ROUTE_CLI and EASYBIS_WOWSIMS for native wand smoke")
    def test_shadow_resumes_mind_flay_in_a_controlled_mana_shortage(self):
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_ROUTE_CLI"])
        profile = sim.read(sim.PROFILES / "priest-shadow.json")
        gear = sim.reference_equipment(root, cli, profile)
        raw = sim.read(sim.PROFILES / profile["dungeonRotation"])
        for wand in (0, 13938):
            with self.subTest(wand=wand):
                req = sim.make_request(profile, profile["races"]["a"], raw, gear, "ranged", wand, 16)
                player = req["raid"]["parties"][0]["players"][0]
                player["rotation"] = rotations.route_rotation(profile, player["rotation"], root)
                req["encounter"] = encounter.encounter()
                # Limit this control's mana by 1,200 and omit the two drinks so a
                # Shadowformed priest runs out in time to resume casting after Shoot.
                player["bonusStats"] = {"stats": [0, 0, 0, -80]}
                for target in req["encounter"]["targets"]:
                    target["targetInputs"][3]["numberValue"] = 0
                req["simOptions"].update(randomSeed="80000", debugFirstIteration=True)
                out = sim.run_request(cli, self.root, req)
                encounter.route_samples(out, 16)
                actions = out["raidMetrics"]["parties"][0]["players"][0]["actions"]
                shots = sum(target["damage"] for action in actions if action["id"].get("spellId") == 5019
                            for target in action["targets"])
                casts = re.findall(r" Casting \{SpellID: (5019|18807)\}", out["logs"])
                self.assertIn("18807", casts)
                if wand:
                    self.assertGreater(shots, 0)
                    self.assertIn("18807", casts[casts.index("5019") + 1:])
                else:
                    self.assertEqual(shots, 0)
                    self.assertNotIn("5019", casts)

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"),
                         "set EASYBIS_ROUTE_CLI and EASYBIS_WOWSIMS for native rotation smoke")
    def test_native_priorities_on_single_elite_and_multi_target_packs(self):
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_ROUTE_CLI"])
        # Direct damage from the appropriate single-target spell on the central elite.
        profiles = {"druid-balance": 9912, "mage-fire": 10199, "mage-arcane": 1326082,
                    "warlock-affliction": 11713, "warlock-demonology": 17923, "warlock-destruction": 1293813,
                    "hunter-beast-mastery": 2643, "shaman-elemental": 15208}
        for slug, single_spell in profiles.items():
            with self.subTest(slug=slug):
                profile = sim.read(sim.PROFILES / (slug + ".json"))
                gear = sim.reference_equipment(root, cli, profile)
                raw = sim.read(sim.PROFILES / profile["dungeonRotation"])
                req = sim.make_request(profile, profile["races"]["a"], raw, gear, "neck", 0, 16)
                player = req["raid"]["parties"][0]["players"][0]
                player["rotation"] = rotations.route_rotation(profile, player["rotation"], root)
                req["encounter"] = encounter.encounter()
                req["simOptions"]["debugFirstIteration"] = True
                result = sim.run_request(cli, self.root, req)
                encounter.route_samples(result, 16)
                targets = result["encounterMetrics"]["targets"]
                units = result["raidMetrics"]["parties"][0]["players"][0]
                def damage(spell, indices):
                    ids = {targets[i]["unitIndex"] for i in indices}
                    return sum(t["damage"] for a in units["actions"] if a["id"].get("spellId") == spell
                               for t in a["targets"] if t["unitIndex"] in ids)
                self.assertGreater(damage(single_spell, (4,)), 0)
                if slug == "hunter-beast-mastery":
                    self.assertEqual(damage(1279715, (4,)), 0)
                    for pack in (range(4), range(5, 12)):
                        self.assertGreater(damage(1279715, pack), 0)
                if slug == "shaman-elemental":
                    # The totem can continue ticking through a transition; the gate is on summons.
                    logs = result["logs"]
                    casts = re.findall(r"\[([\d.]+)\].*? Casting \{SpellID: 10587\}", logs)
                    self.assertTrue(casts)
                    last_first = max(float(t) for t in re.findall(r"\[([\d.]+)\] \[Pack 1 elite \d+\] Died", logs))
                    end_single = float(re.search(r"\[([\d.]+)\] \[Pack 2 elite 1\] Died", logs)[1])
                    self.assertFalse(any(last_first < float(t) <= end_single for t in casts))


if __name__ == "__main__":
    unittest.main()
