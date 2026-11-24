"""Faction quest rewards must change consistently in pack simulations and published companions."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_references as refs
import aoe_jewelry as jewelry
import aoe_weapons as weapons
import simulate_aoe as sim


class FactionReferenceTest(unittest.TestCase):
    def setUp(self):
        self.profile = {"races": {"a": "RaceDwarf", "h": "RaceOrc"}, "player": {}, "damageChecks": {},
                        "pairedItems": {"trinket": 270275}, "slots": {"trinket": [9]},
                        "factionReferenceItems": {"h": {"trinket2": 19120}}}
        self.gear = {"items": [{} for _ in sim.EQUIPMENT_SLOTS]}
        self.gear["items"][1] = {"id": 2, "enchant": 3}
        self.gear["items"][13] = {"id": 270275}
        item = {"type": 12, "unique": True, "scalingOptions": {"0": {"stats": {"17": 7}}}}
        self.items = {2: {"id": 2}, **{i: dict(item, id=i, name=str(i)) for i in refs.QUEST_TWINS}}
        self.items[19120].update(factionRestriction=2, sources=[{"quest": {"id": 7862}}])

    def test_damage_reference_uses_real_bonus_of_random_suffix(self):
        shadow = {"class": "PRIEST", "spec": 3}
        piece = {"items": [{"id": 15942, "randomSuffix": 12761}]}
        native = {"id": 15942, "scalingOptions": {"0": {"randPropPoints": 16}}, "randomSuffixOptions": [12761]}
        def suffix(stat):
            return {"id": 12761, "stats": [0] * stat + [14300]}
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            source = root / "assets/database"
            source.mkdir(parents=True)
            (source / "leftover_db.json").write_text('{"items": []}', encoding="utf-8")
            for stat in (11, 4):  # shadow damage, then healing
                (source / "db.json").write_text(json.dumps({"items": [native], "randomSuffixes": [suffix(stat)]}))
                if stat == 11:
                    refs.validate_suffixes(root, shadow, ["off"], piece)
                else:
                    with self.assertRaisesRegex(ValueError, "15942"):
                        refs.validate_suffixes(root, shadow, ["off"], piece)
            piece["items"][0]["randomSuffix"] = 12345
            with self.assertRaisesRegex(ValueError, "Invalid reference suffix"):
                refs.validate_suffixes(root, shadow, ["off"], piece)

    def test_tank_can_keep_a_defensive_shield_but_not_a_healers_weapon(self):
        prot = {"class": "PALADIN", "spec": 2}
        shield = {"scalingOptions": {"0": {"stats": {"24": 40}}}}
        refs.validate_reference_stats(prot, "off", 12602, shield, {})
        with self.assertRaisesRegex(ValueError, "11923"):
            refs.validate_reference_stats(prot, "main", 11923, {}, {"healing": 124, "spell": 41})

    def test_real_quest_side_and_functional_parity(self):
        def validate(p, gear, items):
            refs.validate(p, gear, sim.EQUIPMENT_SLOTS, items, {})
        validate(self.profile, self.gear, self.items)
        wrong = copy.deepcopy(self.items)
        wrong[19120]["scalingOptions"] = {"0": {"stats": {"17": 7}, "areaStats": [{"areaType": 1}]}}
        with self.assertRaisesRegex(ValueError, "native simulation properties"):
            validate(self.profile, self.gear, wrong)
        with self.assertRaisesRegex(ValueError, "faction-restricted item 270275"):
            validate(dict(self.profile, factionReferenceItems={}), self.gear, self.items)
        reverse = dict(self.profile, factionReferenceItems={"a": {"trinket1": 270276}})
        other_gear = copy.deepcopy(self.gear)
        other_gear["items"][12:14] = [{"id": 270225}, {}]
        validate(reverse, other_gear, self.items)
        with self.assertRaisesRegex(ValueError, "faction-restricted item 270225"):
            validate(dict(reverse, factionReferenceItems={"h": {"trinket1": 270276}}), other_gear, self.items)

    def test_pack_weapons_and_scaling_requests_keep_the_correct_equipment(self):
        for side, correct in (("a", 270275), ("h", 19120)):
            race = self.profile["races"][side]
            rotation = {"priorityList": []}
            for slot in ("head", "trinket", "ranged"):
                req = sim.make_request(self.profile, race, rotation, self.gear, slot, 10, 2)
                pieces = req["raid"]["parties"][0]["players"][0]["equipment"]["items"]
                self.assertEqual(pieces[13], {"id": correct})
            req = weapons.request(self.profile, race, rotation, self.gear, (99, 100), 2)
            pieces = req["raid"]["parties"][0]["players"][0]["equipment"]["items"]
            self.assertEqual(pieces[13:16], [{"id": correct}, {"id": 99}, {"id": 100}])
            self.assertEqual(pieces[1], {"id": 2, "enchant": 3})
        self.assertEqual(self.gear["items"][13], {"id": 270275})

    def test_recorded_partner_and_localized_name_table(self):
        targets = [{"unitIndex": i} for i in range(4)]
        action = {"id": {"spellId": 42}, "spellSchool": 1, "targets": [dict(t, damage=15) for t in targets]}
        result = {"iterationsDone": 2, "avgIterationDuration": 15, "encounterMetrics": {"targets": targets},
                  "raidMetrics": {"parties": [{"players": [{"actions": [action]}]}], "dps": {"allValues": [2, 2]}}}
        with patch.object(sim, "run_request", return_value=result):
            for side, race in self.profile["races"].items():
                block = sim.compare(None, None, self.profile, race, {"priorityList": []}, self.gear, "trinket", 2, {})
                self.assertEqual(block["pairedItem"], refs.paired_item(self.profile, side, "trinket"))
                self.assertEqual(block["pairedItem"], {"a": 270275, "h": 19120}[side])
        self.assertEqual(sim.comparison_names([self.profile], self.items), {"19120": "19120", "270275": "270275"})
        jewelry.validate_pair(self.profile, "trinket", {"id": 42}, self.items[19120], "h")
        with self.assertRaisesRegex(ValueError, "fixed partner"):
            jewelry.validate_pair(self.profile, "trinket", {"id": 42}, self.items[19120], "a")


if __name__ == "__main__":
    unittest.main()
