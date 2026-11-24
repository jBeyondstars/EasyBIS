"""Eligibility regressions for bows, wands and class relics on the 15-second pack."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_ranged as ranged
import aoe_references as references


class AoeRangedTest(unittest.TestCase):
    def test_elemental_uses_lightning_and_shock_relics(self):
        elemental = {"class": "SHAMAN", "spec": 1}
        self.assertEqual(ranged.relic_candidates(elemental), {22395, 23199, 228176})
        for item in (249398, 272432, 272433):  # Meditation, Maelstrom Weapon, Flame Shock.
            with self.subTest(item=item), self.assertRaises(ValueError):
                ranged.validate_candidate(elemental, item, {})

    def test_melee_hybrids_compare_relics_for_the_spells_they_use(self):
        for cls, spec, allowed, unused in (
            ("PALADIN", 3, {249442, 272435}, {23203, 228175, 279248}),
            ("SHAMAN", 2, {22395, 23199, 228176, 272432}, {272431, 272433, 279249}),
        ):
            profile = {"class": cls, "spec": spec}
            self.assertEqual(ranged.relic_candidates(profile), allowed)
            for relic in allowed:
                ranged.validate_candidate(profile, relic, {})
            for relic in unused:
                with self.subTest(relic=relic), self.assertRaises(ValueError):
                    ranged.validate_candidate(profile, relic, {})

    def test_retribution_can_wear_fervor_as_a_neutral_reference(self):
        ret = {"class": "PALADIN", "spec": 3}
        gear = {"items": [{"id": 23203}]}
        fervor = {"id": 23203, "type": 14, "rangedWeaponType": 7,
                  "itemEffects": [{"buffId": 28852}]}
        references.validate(ret, gear, ["ranged"], {23203: fervor}, {})
        with self.assertRaisesRegex(ValueError, "offensive stats"):
            references.validate(ret, gear, ["ranged"],
                                {23203: dict(fervor, scalingOptions={"0": {"stats": {"14": 10}}})}, {})

    def test_hunter_reference_requires_a_functional_weapon(self):
        hunter = {"class": "HUNTER", "spec": 2}
        gear = {"inv": 15, "kind": "2.2", "req": 3, "dps": 2.4}
        bow = {"id": 2506, "type": 14, "rangedWeaponType": 1, "reqLvl": 3,
               "weaponSpeed": 2.1, "scalingOptions": {"0": {"weaponDamageMin": 3, "weaponDamageMax": 7}}}
        ranged.validate_candidate(hunter, 2506, {})
        ranged.validate_native(hunter, bow, gear)
        for bad in (dict(bow, rangedWeaponType=4), dict(bow, rangedWeaponType=5),
                    dict(bow, weaponSpeed=0), dict(bow, scalingOptions={}), dict(bow, reqLvl=61)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ranged.validate_native(hunter, bad)
        for bad in (dict(gear, dps=12), dict(gear, kind="2.3"), dict(gear, inv=12)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                ranged.validate_native(hunter, bow, bad)
        for stats in ({"spell": 12}, {"fire": 10, "agility": 8}, {"healing": 10}):
            with self.subTest(stats=stats), self.assertRaisesRegex(ValueError, "caster stats"):
                ranged.validate_candidate(hunter, 12345, stats)

    def test_wand_uses_stats_of_its_wearer(self):
        mage = {"class": "MAGE", "spec": 3}
        ranged.validate_candidate(mage, 1, {"frost": 12})
        ranged.validate_candidate(mage, 1, {"arcane": 12})
        with self.assertRaises(ValueError):
            ranged.validate_candidate(mage, 1, {"fire": 12})
        with self.assertRaises(ValueError):
            ranged.validate_candidate({"class": "WARRIOR", "spec": 1}, 1, {"spell": 12})

    def test_relic_class_build_effects_and_sources(self):
        db = SimpleNamespace(items={}, gear={}, classes={})
        ranged.include_relics(db)
        druid = {"class": "DRUID", "spec": 4}
        self.assertIn(22397, ranged.relic_candidates(druid))
        self.assertNotIn(22397, ranged.relic_candidates({"class": "DRUID", "spec": 1}))
        self.assertNotIn(22397, ranged.relic_candidates({"class": "PALADIN", "spec": 1}))
        idol = {"id": 22397, "type": 14, "rangedWeaponType": 6, "reqLvl": 52,
                "itemEffects": [{"buffId": 27851}]}
        ranged.validate_candidate(druid, 22397, {})
        ranged.validate_native(druid, idol, db.gear[22397])
        with self.assertRaises(ValueError):
            ranged.validate_native(druid, dict(idol, itemEffects=[]))
        with self.assertRaises(ValueError):
            ranged.validate_candidate(druid, 272432, {})
        self.assertEqual(db.items[22397]["sources"][0][2], "Lord Roccor")
        self.assertEqual(db.classes, {})


if __name__ == "__main__":
    unittest.main()
