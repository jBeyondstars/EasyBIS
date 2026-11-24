"""The Arms pre-raid crafting shortlist shares its ordinary raid measurements."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
import fdb
import ladders


class ArmsHelmsTest(unittest.TestCase):
    def test_stalwart_is_only_removed_from_the_arms_pre_raid_shortlist(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        arms = ladders.full_ladder(db, "WARRIOR", 1, "pve", "head")
        kept = ladders.kept_ladder("head", arms)
        self.assertIn(250599, {e.item_id for e in arms})
        for side in "ah":
            pre = (side, False, False, 0, False, 6)
            for source in (arms, kept):
                entries = ladders.visible(source, pre)
                self.assertEqual(ladders.lead(entries).item_id, 12640)
                self.assertNotIn(250599, {e.item_id for e in entries})
            raid = (side, False, False, 1, False, 6)
            self.assertIn(250599, {e.item_id for e in ladders.visible(arms, raid)})
        for cls, number, mode in (("WARRIOR", 1, "pvp"), ("WARRIOR", 2, "pve"), ("PALADIN", 4, "pve")):
            other = ladders.full_ladder(db, cls, number, mode, "head")
            self.assertIn(250599, {e.item_id for e in ladders.visible(other, pre)})

        # If Lionheart becomes restricted to one side, preserve the alternative.
        pair = {e.item_id: e for e in arms if e.item_id in (12640, 250599)}
        restricted = ladders.ArmsHelms([replace(pair[12640], side="a"), pair[250599]])
        self.assertIn(250599, {e.item_id for e in ladders.visible(restricted, pre)})

    def test_both_factions_offer_their_leather_and_mail_crit_shoulders_once(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        full = ladders.full_ladder(db, "WARRIOR", 1, "pve", "shoulder")
        for side, leather, mail in (("a", 271955, 271956), ("h", 272105, 272106)):
            rows = ladders.visible(full, (side, False, False, 0, False, 6))
            best, alts = ladders.picks("shoulder", rows, 6)
            self.assertEqual({entry.shown(side) for entry in (best + alts)[:2]}, {leather, mail})
            self.assertEqual(best[0].stored, alts[0].stored)
            self.assertEqual(sum(entry.shown(side) == mail for entry in rows), 1)
