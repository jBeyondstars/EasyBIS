"""The mage chest comparisons cover the faction grids and their published protocols."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest
import zipfile

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import ladders


class MageArcaneChestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.source = json.loads((BUILD / "corrections" / "mage_arcane_chest.json").read_text("utf-8"))
        cls.ladder = ladders.full_ladder(cls.db, "MAGE", 1, "pve", "chest")

    def test_each_faction_has_a_result_or_an_explicit_limit_for_each_actual_item(self):
        for side, models in self.source["chest"].items():
            with self.subTest(side=side):
                candidates = {row.shown(side) for row in self.ladder} - {None}
                self.assertEqual(set(map(int, models)), candidates)
                missing = {item for item, row in models.items() if row[3] == "unmeasured"}
                self.assertEqual(missing, {"22069"} if side == "a" else {"16491", "22069"})
                self.assertTrue(all(models[item][:3] == [None, None, 0] for item in missing))
                self.assertEqual(models["940"][3], "unregistered_effect")
                self.assertTrue(all(row[2] == 2000 and row[1] >= 0
                                    for item, row in models.items() if item not in missing))

    def test_pre_raid_arcane_keeps_its_first_choice_and_ranks_the_two_measured_alternatives(self):
        for side in "ah":
            with self.subTest(side=side):
                rows = ladders.visible(self.ladder, (side, False, False, 0, False, 6))
                self.assertEqual([r.shown(side) for r in rows[:3]], [14152, 13314, 280057])
                self.assertGreater(rows[1].score, rows[2].score)
                self.assertIn(self.source["engine"], self.db.simulated.commits)
                reference = self.source["reference"][side]["equipment"]
                self.assertEqual([piece["id"] for piece in reference[10:12]], [272406, 22339])
        self.assertNotIn("chest", self.db.simulated.by_faction.get(("MAGE", 2), {}))
        self.assertIsNone(ladders.slot_ranking(self.db, "MAGE", 1, "pvp", "chest"))

    def test_archive_contains_the_inputs_and_outputs_that_supply_the_scores(self):
        with zipfile.ZipFile(BUILD.parent / self.source["protocol"]) as archive:
            manifest = json.loads(archive.read("calibration.json"))
            self.assertEqual(manifest["slots"]["chest"], self.source["chest"])
            self.assertEqual(manifest["engine"], self.source["engine"])
            for side in "ah":
                for batch in manifest["sources"][side]:
                    for filename, expected in ((batch["input"], batch["sha256"]),
                                               (batch["output"], batch["output_sha256"])):
                        self.assertEqual(hashlib.sha256(archive.read(filename)).hexdigest(), expected)

    def test_frost_uses_its_own_measures_and_protocol(self):
        source = json.loads((BUILD / "corrections" / "mage_frost_chest.json").read_text("utf-8"))
        ladder = ladders.full_ladder(self.db, "MAGE", 3, "pve", "chest")
        with zipfile.ZipFile(BUILD.parent / source["protocol"]) as archive:
            manifest = json.loads(archive.read("calibration.json"))
        self.assertEqual(manifest["slots"]["chest"], source["chest"])
        for side in "ah":
            with self.subTest(side=side):
                self.assertEqual(set(map(int, source["chest"][side])), {e.shown(side) for e in ladder} - {None})
                rows = ladders.visible(ladder, (side, False, False, 0, False, 6))
                self.assertEqual(rows[0].shown(side), 14152)
                self.assertEqual([e.shown(side) for e in rows[3:5]], [13314, 13535])


if __name__ == "__main__":
    unittest.main()
