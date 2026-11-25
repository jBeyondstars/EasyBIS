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

    def test_arms_uses_the_mail_crit_shoulders_for_both_factions(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        full = ladders.full_ladder(db, "WARRIOR", 1, "pve", "shoulder")
        for side, leather, mail in (("a", 271955, 271956), ("h", 272105, 272106)):
            rows = ladders.visible(full, (side, False, False, 0, False, 6))
            best, alts = ladders.picks("shoulder", rows, 6)
            self.assertEqual(best[0].shown(side), mail)
            self.assertEqual(sum(entry.shown(side) == mail for entry in rows), 1)
            self.assertNotIn(leather, {entry.shown(side) for entry in best + alts})

    def test_equivalent_shoulders_follow_the_armor_a_class_can_wear(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        variants = ladders.HEAVIER_ARMOR["shoulder"]
        for light, heavy in variants.items():
            self.assertEqual(db.gear[light]["stats"], db.gear[heavy]["stats"])
            self.assertGreater(db.gear[heavy]["armor"], db.gear[light]["armor"])
            self.assertEqual(db.items[light]["sources"][0][:2], db.items[heavy]["sources"][0][:2])
            self.assertEqual(db.items[light]["sources"][1], db.items[heavy]["sources"][1])
        for cls, spec, mode, alliance, horde in (
                ("HUNTER", 1, "pve", 271956, 272106),
                ("SHAMAN", 2, "pve", 271956, 272106),
                ("WARRIOR", 3, "pvp", 271956, 272106),
                ("PALADIN", 4, "pve", 271954, 272104),
                ("DRUID", 3, "pvp", 271954, 272104),
                ("ROGUE", 1, "pve", 271955, 272105),
                ("MAGE", 1, "pve", 271953, 272103)):
            pool = ladders.full_ladder(db, cls, spec, mode, "shoulder")
            for side, wanted in (("a", alliance), ("h", horde)):
                with self.subTest(cls=cls, spec=spec, mode=mode, side=side):
                    rows = ladders.visible(pool, (side, False, True, 0, ladders.PVP_REWARDS[mode], 6))
                    ids = {entry.shown(side) for entry in rows}
                    self.assertIn(wanted, ids)
                    self.assertTrue(all(light not in ids or heavy not in ids
                                        for light, heavy in variants.items()))

    def test_arathi_belts_keep_the_best_level_48_armor_and_the_distinct_sets(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        hunter = ladders.full_ladder(db, "HUNTER", 1, "pvp", "waist")
        rogue = ladders.full_ladder(db, "ROGUE", 1, "pvp", "waist")
        for side, light, heavy, set_belts in (("a", 20115, 20088, {20045, 20043}),
                                              ("h", 20193, 20151, {20190, 20150})):
            flt = (side, False, False, 0, True, 6)
            hunter_ids = {e.shown(side) for e in ladders.visible(hunter, flt)}
            rogue_ids = {e.shown(side) for e in ladders.visible(rogue, flt)}
            self.assertTrue({heavy} | set_belts <= hunter_ids)
            self.assertNotIn(light, hunter_ids)
            self.assertIn(light, rogue_ids)
            self.assertNotIn(heavy, rogue_ids)
