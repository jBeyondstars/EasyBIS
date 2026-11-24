"""Check the cat's level-60 PvE off-hand calibration and its scope."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import feral_gear
import ladders
import specs


class FeralOffhandsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.ranking = feral_gear.ranking(cls.db, "DRUID", 4, "pve", "off")

    def test_only_cat_pve_off_hands(self):
        for cls, spec, mode, slot in (
            ("DRUID", 4, "pvp", "off"), ("DRUID", 4, "pve", "main"),
            ("DRUID", 2, "pve", "off"), ("PALADIN", 2, "pve", "off"),
            ("ROGUE", 2, "pve", "off"),
        ):
            with self.subTest(cls=cls, spec=spec, mode=mode, slot=slot):
                self.assertIsNone(feral_gear.ranking(self.db, cls, spec, mode, slot))

    def test_scepter_and_tome_use_the_main_hands_attack_power_scale(self):
        source = feral_gear._read("off")
        self.assertEqual(source["reference"]["fingers"], [272408, 17713])
        weight = self.db.classes["DRUID"]["specs"][4]["weights"]["raid"][specs.ATTACK_POWER]
        for item in (13385, 22329):
            trials = next(group["trials"] for group in source["candidates"] if group["id"] == item)
            self.assertEqual({row[1] for row in trials}, {"a", "h"})
            self.assertTrue(all(row[4] == 20000 for row in trials))
            values = [dps * 40 * weight / source["calibration"][side][0] for _, side, dps, _, _ in trials]
            self.assertAlmostEqual(self.ranking.value(item, 0), sum(values) / 2, places=3)
        self.assertGreater(self.ranking.value(22329, 0), self.ranking.value(13385, 0))
        for comparisons in source["duels_scepter_minus_tome"].values():
            self.assertTrue(all(mean > 2 * se for mean, se in comparisons.values()))

    def test_drink_is_unavailable_and_an_unmeasured_item_keeps_its_weight(self):
        source = feral_gear._read("off")
        tankard = next(group for group in source["candidates"] if group["id"] == 4696)
        self.assertTrue(all(mean < -2 * se for _, _, mean, se, _ in tankard["trials"]))
        self.assertNotIn(4696, self.ranking.scores)
        self.assertFalse(self.ranking.measured(15866))  # Mana Rejuvenation in cat form is unverified.
        self.assertEqual(self.ranking.value(99999999, 3.2), 3.2)

    def test_faction_twins_have_trials_on_the_actual_ids(self):
        source = feral_gear._read("off")
        paired = next(group for group in source["candidates"] if group["id"] == 278157)
        self.assertEqual({(row[0], row[1]) for row in paired["trials"]}, {(278157, "a"), (272686, "h")})
        self.assertEqual(self.ranking.value(278157, 0), self.ranking.value(272686, 0))

    def test_published_cap_list_and_the_original_site_rule(self):
        def pair(entries):
            return [entry.item_id for entry in entries if entry.item_id in (22329, 13385)]

        cap = ladders.full_ladder(self.db, "DRUID", 4, "pve", "off")
        self.assertEqual(pair(ladders.kept_ladder("off", cap)), [22329, 13385])
        self.assertEqual(pair(ladders.full_ladder(self.db, "DRUID", 4, "pve", "off", rank_rewards=False)),
                         [13385, 22329])
        self.assertEqual(pair(ladders.full_ladder(self.db, "DRUID", 4, "pvp", "off")), [13385, 22329])


if __name__ == "__main__":
    unittest.main()
