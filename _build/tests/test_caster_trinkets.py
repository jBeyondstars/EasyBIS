"""Caster trinket pairs must use the same faction, encounter and equipped partner."""
import sys
import unittest
from copy import copy
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import caster_trinkets
import fdb
import ladders


class CasterTrinketsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = caster_trinkets.tables()
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.db.pre_raid_trinkets = cls.tables

    def test_both_factions_measure_eye_and_reed_in_every_damage_profile(self):
        self.assertEqual(set(self.tables), {
            ("MAGE", 1), ("MAGE", 2), ("MAGE", 3), ("PRIEST", 3),
            ("WARLOCK", 1), ("WARLOCK", 2), ("WARLOCK", 3),
            ("DRUID", 1), ("SHAMAN", 1), ("PALADIN", 4),
        })
        for profile, slots in self.tables.items():
            for side in ("a", "h"):
                for item in ("12930", "13968"):
                    with self.subTest(profile=profile, side=side, item=item):
                        gain, error, iterations, model = slots["trinket"][side][item]
                        self.assertGreater(gain, 0)
                        self.assertGreaterEqual(error, 0)
                        self.assertEqual((iterations, model), (2000, "measured"))

    def test_all_reachable_first_picks_have_their_own_measured_partner(self):
        for (cls, spec), slots in self.tables.items():
            ladder = ladders.full_ladder(self.db, cls, spec, "pve", "trinket")
            for flt in (f for f in ladders.FILTERS if f[3] == 0):
                visible = ladders.visible_slots({"trinket": ladder}, flt)["trinket"]
                best, _ = ladders.picks("trinket", visible, 6)
                if len(best) < 2:
                    continue
                first, second = best
                side = flt[0]
                with self.subTest(profile=(cls, spec), filters=flt):
                    first_id, second_id = first.shown(side), second.shown(side)
                    self.assertEqual(second.paired_with, first_id)
                    self.assertNotEqual(first_id, second_id)
                    self.assertFalse(first.limit and first.limit == second.limit)
                    self.assertEqual(slots["trinket"][f"{side}:{first_id}"][str(second_id)][3], "measured")

    def test_raid_filters_use_the_original_score_and_partner(self):
        original = copy(self.db)
        original.pre_raid_trinkets = {}
        for cls, spec in self.tables:
            old = ladders.full_ladder(original, cls, spec, "pve", "trinket")
            new = ladders.full_ladder(self.db, cls, spec, "pve", "trinket")
            for side in ("a", "h"):
                for phase in (1, 9):
                    flt = (side, True, False, phase, True, None)
                    def shown(ladder):
                        rows = ladders.visible_slots({"trinket": ladder}, flt)["trinket"]
                        return [(entry.shown(side), entry.score, entry.paired_with) for entry in rows[:7]]
                    self.assertEqual(shown(new), shown(old), (cls, spec, flt))
