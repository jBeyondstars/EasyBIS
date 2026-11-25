"""The cat's trinkets use the combat rotations and retain the requested Heart placement."""
import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import feral_gear
import ladders
import specs


class FeralTrinketsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.ranking = ladders.slot_ranking(cls.db, "DRUID", 4, "pve", "trinket")
        cls.ladder = ladders.full_ladder(cls.db, "DRUID", 4, "pve", "trinket")

    def test_only_feral_cat_pve_uses_this_calibration(self):
        for cls, spec, mode in (("DRUID", 4, "pvp"), ("DRUID", 2, "pve"), ("ROGUE", 1, "pve")):
            with self.subTest(cls=cls, spec=spec, mode=mode):
                self.assertIsNone(feral_gear.ranking(self.db, cls, spec, mode, "trinket"))
        self.assertEqual(feral_gear._read("trinket")["reference"]["fingers"], [272408, 17713])
        source = feral_gear._read("trinket")
        self.assertFalse(source["reference"]["pvp_rewards_equipped"])
        self.assertEqual(source["reference"]["cat_uptime_fraction"], 1)
        self.assertEqual(source["reference"]["starting_trinkets"], [0, 0])
        trials = next(group["trials"] for group in source["candidates"] if group["item"] == 11815)
        weight = self.db.classes["DRUID"]["specs"][4]["weights"]["raid"][specs.ATTACK_POWER]
        points = [dps * weight * source["calibration_ap"] / source["calibration"][side][0]
                  for _, side, dps, _, _ in trials]
        self.assertAlmostEqual(self.ranking.value(11815, 0), sum(points) / len(points), places=3)
        self.assertEqual(self.ranking.value(999999, 1.25), 1.25)

    def test_bear_force_of_will_is_fourth_across_pre_raid_filters_and_list_lengths(self):
        full = ladders.full_ladder(self.db, "DRUID", 2, "pve", "trinket")
        kept = ladders.kept_ladder("trinket", full)
        for side in "ah":
            for ladder in (full, kept):
                visible = ladders.visible(ladder, (side, False, False, 0, False, 6))
                for count in (2, 3, 5, 6):
                    best, alts = ladders.picks("trinket", visible, count)
                    self.assertEqual([e.item_id for e in best], [14557, 272440])
                    displayed = best + alts
                    self.assertEqual(displayed[3].item_id, 11810)
                    self.assertTrue(displayed[3].level and displayed[3].pvp_utility)
            raid = ladders.visible(full, (side, False, False, 1, False, 6))
            self.assertFalse(next(e for e in raid if e.item_id == 11810).unscored)

    def test_pre_raid_pair_and_mana_alternatives(self):
        for side in "ah":
            with self.subTest(side=side):
                visible = ladders.visible(self.ladder, (side, False, False, 0, False, 6))
                best, _ = ladders.picks("trinket", visible)
                self.assertEqual([entry.shown(side) for entry in best], [280065, 280060])
                known = {entry.shown(side): entry for entry in visible}
                self.assertTrue(known[11815].pvp_utility)
                for mana_trinket in (11832, 1713, 10659):
                    self.assertGreater(known[280060].score, known[mana_trinket].score)
                self.assertTrue(known[10659].pvp_utility)
                self.assertGreater(known[18371].score, 0)

    def test_pre_raid_hand_and_heart_are_situational_and_raid_uses_measured_scores(self):
        for side in "ah":
            for phase in (0, 1):
                with self.subTest(side=side, phase=phase):
                    visible = ladders.visible(self.ladder, (side, False, False, phase, False, 6))
                    best, alts = ladders.picks("trinket", visible, ladders.MAX_ALTERNATIVES)
                    ids = [entry.shown(side) for entry in best + alts]
                    hand = next(entry for entry in visible if entry.item_id == 11815)
                    if phase == 0:
                        self.assertEqual(ids[:3], [280065, 280060, 280074])
                        situational = {entry.shown(side) for entry in alts if entry.pvp_utility}
                        self.assertLessEqual({11815, 22321}, situational)
                    else:
                        self.assertFalse(hand.unscored)
                        self.assertEqual(hand.score, self.ranking.scores[11815])
                        self.assertEqual([e.item_id for e in visible], [e.item_id for e in self.ladder
                                         if e.passes((side, False, False, phase, False, 6))])

    def test_measured_heart_retains_placement_immediately_after_hand(self):
        self.assertGreater(self.ranking.scores[22321], self.ranking.scores[11815])
        ids = [entry.item_id for entry in self.ladder]
        hand = ids.index(11815)
        heart = self.ladder[hand + 1]
        self.assertEqual(heart.item_id, 22321)
        self.assertTrue(heart.placed)
        self.assertEqual(heart.stored, self.ladder[hand].stored)


if __name__ == "__main__":
    unittest.main()
