"""AoE selection for Retribution and Enhancement uses the actual Forever item stats."""
import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import aoe_eligibility as rules
import aoe_jewelry
import aoe_references
import aoe_weapons
import fdb


class MeleeHybridEligibilityTest(unittest.TestCase):
    specs = (("PALADIN", 3), ("SHAMAN", 2))

    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache/ForeverDB")
        aoe_jewelry.include_trinkets(cls.db)

    def stats(self, item):
        return rules.client_stats(self.db.gear[item]["stats"])

    def test_caster_only_items_are_ineligible_even_with_shared_hit_or_a_damage_proc(self):
        for cls, spec in self.specs:
            for slot, item in (("neck", 19426), ("back", 272411), ("finger", 272406),
                               ("trinket", 12930), ("trinket", 13968), ("trinket", 22268),
                               ("trinket", 280032), ("trinket", 272438)):
                profile = {"class": cls, "spec": spec, "itemDamageChecks": {str(item): [1]}}
                with self.subTest(cls=cls, item=item), self.assertRaisesRegex(ValueError, str(item)):
                    rules.validate_slot_candidate(profile, slot, item, self.stats(item))

    def test_melee_stats_and_weapon_triggered_effects_still_qualify(self):
        for cls, spec in self.specs:
            for slot, item in (("neck", 15411), ("back", 13340), ("legs", 252606),
                               ("trinket", 13965), ("trinket", 22321), ("trinket", 280071)):
                with self.subTest(cls=cls, item=item):
                    rules.validate_slot_candidate({"class": cls, "spec": spec}, slot, item, self.stats(item))
        rules.validate_slot_candidate({"class": "SHAMAN", "spec": 1}, "neck", 19426, self.stats(19426))

    def test_weapon_base_damage_and_offhand_type_are_checked_separately(self):
        enhance = {"class": "SHAMAN", "spec": 2}
        aoe_weapons.validate_client(self.db, enhance, "main", 13285, self.stats(13285))
        for slot, item in (("main", 13937), ("off", 18316)):
            with self.subTest(item=item), self.assertRaisesRegex(ValueError, str(item)):
                aoe_weapons.validate_client(self.db, enhance, slot, item, self.stats(item))

    def test_fixed_ring_partner_is_subject_to_the_same_check(self):
        ring = {"scalingOptions": {"0": {"stats": {"3": 14, "5": 9, "4": 9, "17": 10}}}}
        for cls, spec in self.specs:
            profile = {"class": cls, "spec": spec, "pairedItems": {"finger": 272406}}
            with self.subTest(cls=cls), self.assertRaisesRegex(ValueError, "272406"):
                aoe_references.validate(profile, {"items": [{"id": 272406}]}, ["finger2"],
                                        {272406: ring}, self.db.items)

    def test_feral_held_items_must_have_more_than_incidental_melee_stats(self):
        for spec in (2, 4):
            profile = {"class": "DRUID", "spec": spec}
            for item in (13385, 13524, 15963):
                aoe_weapons.validate_client(self.db, profile, "off", item, self.stats(item))
            for item in (15930, 15962, 15965):
                with self.subTest(spec=spec, item=item), self.assertRaisesRegex(ValueError, str(item)):
                    aoe_weapons.validate_client(self.db, profile, "off", item, self.stats(item))

    def test_reference_cannot_reintroduce_an_alterac_reward(self):
        for cls, spec, slot, item in (("MAGE", 3, "ranged", 19108),
                                      ("HUNTER", 1, "ranged", 19107),
                                      ("WARRIOR", 2, "finger2", 19325)):
            with self.subTest(item=item), self.assertRaisesRegex(ValueError, f"{item}.*PvP"):
                aoe_references.validate({"class": cls, "spec": spec}, {"items": [{"id": item}]},
                                        [slot], {item: {}}, self.db.items)

    def test_warlock_shadow_candidates_are_screened_for_each_build(self):
        profile = {"class": "WARLOCK", "spec": 1}
        with self.assertRaisesRegex(ValueError, "279269"):
            rules.validate_candidate(profile, 279269, self.stats(279269))
        rules.validate_candidate(dict(profile, secondarySchoolItems=[279269]), 279269, self.stats(279269))
        with self.assertRaisesRegex(ValueError, "279269"):
            rules.validate_candidate({"class": "MAGE", "spec": 3, "secondarySchoolItems": [279269]},
                                     279269, self.stats(279269))


if __name__ == "__main__":
    unittest.main()
