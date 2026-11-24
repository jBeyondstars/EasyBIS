"""Regressions for weapon sets in the 15-second AOE ranking."""
import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_weapons as weapons


class AoeWeaponTest(unittest.TestCase):
    def test_rotation_weapon_requirements(self):
        rogue = {"class": "ROGUE", "spec": 1}
        for slot in ("main", "off"):
            self.assertTrue(weapons.fits(rogue, slot, 2, 2))
            self.assertFalse(weapons.fits(rogue, slot, 9, 2))
        tank = {"class": "WARRIOR", "spec": 3}
        self.assertTrue(weapons.fits(tank, "off", 7, 3))
        self.assertFalse(weapons.fits(tank, "main", 9, 4))
        self.assertFalse(weapons.fits(tank, "off", 2, 2))
        self.assertFalse(weapons.fits({"class": "HUNTER", "spec": 2}, "off", 5, 3))

    def test_two_hand_and_unique_conflicts(self):
        profile = {"class": "HUNTER", "spec": 3}
        db = SimpleNamespace(gear={1: {"inv": 17, "kind": "2.1"}, 2: {"inv": 13, "kind": "2.7"}},
                             items={2: {"flags": "U", "limit": None}})
        weapons.validate_pair_client(db, profile, 1, 0)
        for pair in ((1, 2), (2, 2), (2, 0)):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                weapons.validate_pair_client(db, profile, *pair)

    def test_one_handed_proficiency_cannot_equip_the_two_handed_weapon(self):
        for cls, weapon in (("ROGUE", 1), ("ROGUE", 9), ("MAGE", 9), ("PRIEST", 4)):
            with self.subTest(cls=cls, weapon=weapon):
                profile = {"class": cls, "spec": 2}
                self.assertTrue(weapons.fits(profile, "main", weapon, 2))
                self.assertFalse(weapons.fits(profile, "main", weapon, 4))

    def test_retribution_and_arms_only_accept_two_handed_melee_weapons(self):
        for cls, spec in (("PALADIN", 3), ("WARRIOR", 1)):
            profile = {"class": cls, "spec": spec}
            for weapon in weapons.PROFICIENCIES[cls]:
                self.assertEqual(weapons.fits(profile, "main", weapon, 4), weapon in weapons.TWO_HANDED[cls])
                self.assertFalse(weapons.fits(profile, "off", weapon, 4))
                for hand in (1, 2, 3):
                    self.assertFalse(weapons.fits(profile, "main", weapon, hand))
                    self.assertFalse(weapons.fits(profile, "off", weapon, hand))
        fury = {"class": "WARRIOR", "spec": 2}
        self.assertTrue(all(weapons.fits(fury, slot, 9, 2) for slot in ("main", "off")))

    def test_base_damage_does_not_admit_a_caster_weapon_for_the_hunter(self):
        profile = {"class": "HUNTER", "spec": 3}
        db = SimpleNamespace(gear={5: {"inv": 13, "kind": "2.7", "dps": 53, "req": 60, "stats": {42: 60}}})
        with self.assertRaisesRegex(ValueError, "caster stats"):
            weapons.validate_client(db, profile, "main", 5, {"spell": 60})
        db.gear[5]["stats"] = {}
        with self.assertRaisesRegex(ValueError, "no ranged offense"):
            weapons.validate_client(db, profile, "main", 5, {})

    def test_plain_weapon_damage_does_not_admit_a_resource_only_weapon(self):
        db = SimpleNamespace(gear={5: {"inv": 13, "kind": "2.7", "dps": 50, "req": 60, "stats": {5: 15}}})
        for cls, spec in (("WARRIOR", 2), ("ROGUE", 2)):
            profile = {"class": cls, "spec": spec}
            raw = db.gear[5]
            with self.subTest(cls=cls):
                raw["stats"] = {5: 15}
                with self.assertRaisesRegex(ValueError, "offensive stats"):
                    weapons.validate_client(db, profile, "main", 5, {"intellect": 15})
                raw["stats"][3] = 14
                weapons.validate_client(db, profile, "main", 5, {"intellect": 15, "agility": 14})
                raw["stats"] = {}
                weapons.validate_client(db, profile, "main", 5, {})

    def test_both_rows_point_to_the_best_measured_companion(self):
        profile = {"weaponSets": [[1, 2], [1, 3], [4, 0]], "referenceWeapons": [1, 2]}
        records = [{"main": m, "off": o, "gain": gain, "se": 0.1 if gain else 0}
                   for m, o, gain in ((1, 2, 0), (1, 3, 85), (4, 0, 50))]
        def block(rows):
            return {"referenceWeapons": [1, 2], "baseline": 10000,
                    "items": [{"id": i, "partner": partner, "gain": gain, "se": 0.1 if gain else 0}
                              for i, partner, gain in rows]}
        main = dict(block([(1, 3, 85), (4, 0, 50)]), setMeasurements=records)
        off = block([(3, 1, 85), (2, 1, 0)])
        weapons.validate_rows(profile, main, off)
        wrong = copy.deepcopy(main)
        wrong["items"][0].update(partner=2, gain=0)
        with self.assertRaisesRegex(ValueError, "companion"):
            weapons.validate_rows(profile, wrong, off)
        with self.assertRaisesRegex(ValueError, "measurements"):
            weapons.validate_rows(profile, dict(main, setMeasurements=records[1:]), off)

    def test_shield_slam_counts_verified_block_value(self):
        profile = {"class": "WARRIOR", "spec": 3}
        raw = {"inv": 14, "kind": "4.6", "dps": 0, "req": 60, "stats": {48: 40}}
        shield = {"id": 12602, "weaponType": 7, "scalingOptions": {"0": {"stats": {"24": 40}}}}
        weapons.validate_client(SimpleNamespace(gear={12602: raw}), profile, "off", 12602, {})
        caster_shield = dict(raw, stats={48: 40, 5: 25})
        with self.assertRaisesRegex(ValueError, "offensive stats"):
            weapons.validate_client(SimpleNamespace(gear={12602: caster_shield}), profile, "off", 12602,
                                    {"intellect": 25})
        weapons._check_weapon_damage(shield, raw)
        with self.assertRaisesRegex(ValueError, "block value"):
            weapons._check_weapon_damage(shield, dict(raw, stats={48: 10}))


if __name__ == "__main__":
    unittest.main()
