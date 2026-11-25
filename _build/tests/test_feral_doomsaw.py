"""Blackhand Doomsaw gains only its isolated Fatal Wound damage on the cat's raid ladder."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import feral_gear
import ladders
import specs


class FeralDoomsawTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")

    def test_generator_converts_the_paired_proc_into_stat_points(self):
        data = json.loads((feral_gear.DATA / "feral_doomsaw.json").read_text())
        self.assertEqual(data["wowsims"], "07648faf129cd82f99f4dd9e63b015f59f8ec811")
        self.assertEqual(set(data["trials"]), {"a", "h"})
        for trial in data["trials"].values():
            self.assertGreater(trial["weapons"]["12583"][0], 2 * trial["weapons"]["12583"][1])
            self.assertGreater(trial["ap_dps"], 2 * trial["ap_se"])
        weights = self.db.classes["DRUID"]["specs"][4]["weights"]["raid"]
        expected = sum(row["weapons"]["12583"][0] / row["ap_dps"] for row in data["trials"].values()) / 2
        anchor = ladders.score(self.db, data["anchor_weapon"], weights, "DRUID")
        scores = feral_gear.calibrated_two_hand_scores(anchor, weights[specs.ATTACK_POWER])
        self.assertEqual(set(scores), {12583, 18725, 13393, 280059, 274419, 250615})
        self.assertAlmostEqual(scores[12583], anchor + expected * weights[specs.ATTACK_POWER] * data["calibration_ap"])

    def test_default_two_handed_list_and_scope(self):
        new = ladders.full_ladder(self.db, "DRUID", 4, "pve", "main")
        with patch.object(feral_gear, "calibrated_two_hand_scores", return_value={}):
            old = ladders.full_ladder(self.db, "DRUID", 4, "pve", "main")
        calibrated = {12583, 18725, 13393, 280059, 274419, 250615}
        self.assertEqual([e for e in old if e.item_id not in calibrated], [e for e in new if e.item_id not in calibrated])
        for side in "ah":
            flt = (side, False, False, 0, False, 6)
            two = [e for e in ladders.visible(new, flt) if e.two_hand]
            ordinary = [e for e in two if not e.pvp_utility]
            self.assertEqual([e.item_id for e in ordinary[:7]], [250619, 280018, 12583, 18725, 13393, 274419, 280059])
            self.assertEqual(ordinary[2].stored, 1295)
            self.assertEqual(two[1].item_id, 18420)
            self.assertTrue(two[1].pvp_utility)
        with patch.object(feral_gear, "calibrated_two_hand_scores", side_effect=AssertionError("wrong scope")):
            for cls, spec, mode, slot in (("DRUID", 4, "pvp", "main"), ("DRUID", 4, "pve", "off"),
                                         ("DRUID", 2, "pve", "main"), ("PALADIN", 2, "pve", "main")):
                ladders.full_ladder(self.db, cls, spec, mode, slot)
            ladders.full_ladder(self.db, "DRUID", 4, "pve", "main", level=59)
            ladders.full_ladder(self.db, "DRUID", 4, "pve", "main", rank_rewards=False)


if __name__ == "__main__":
    unittest.main()
