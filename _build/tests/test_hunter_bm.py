"""Regression coverage for context-specific ranks, eligibility, and weapon sets."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
import fdb
import hunter_bm
import ladders
from test_addon import Game, lupa


class HunterBmTest(unittest.TestCase):
    def test_off_hand_rounds_the_measured_set_once_and_excludes_its_main_hand(self):
        raw = [ladders.Entry(i, 100, "", None, True, False, False, False, False, False, None) for i in (10, 11)]
        measured = lambda value: [value, 0.1, 20000, "measured"]
        data = {"slots": {"main": {"a": {"10": measured(40.24)}},
                          "off": {"a:10": {"10": measured(90), "11": measured(10.24)}}}}
        with patch.object(hunter_bm, "read", return_value=data):
            main = hunter_bm.contextual_ladder(raw, "main", {10: 1, 11: 1})
            off = hunter_bm.contextual_ladder(raw, "off", {10: 1, 11: 1})
        flt = ("a", False, False, 0)
        main_score = ladders.lead(ladders.visible(main, flt)).score
        left = ladders.visible(off, flt, 10)
        self.assertEqual([e.item_id for e in left], [11])
        self.assertEqual(main_score + left[0].score, 50.5)
        self.assertEqual(ladders.visible(off, flt, 99), [])

    def test_partial_measurement_is_an_alternative_even_if_its_proc_scores_highly(self):
        raw = [ladders.Entry(i, 100, "", None, True, False, False, False, False, False, None) for i in (1, 2, 3, 4)]
        records = {"a": {"1": [3, 0.1, 2000, "measured"], "2": [90, 0.1, 2000, "assumed_proc"],
                         "3": [8, 0.1, 2000, "unregistered_effect"],
                         "4": [88, 0.1, 2000, "unverified_proc_rate"]}}
        with patch.object(hunter_bm, "read", return_value={"slots": {"hands": records}}):
            ladder = hunter_bm.contextual_ladder(raw, "hands", {i: 5 for i in (1, 2, 3, 4)})
        visible = ladders.visible(ladder, ("a", False, False, 0))
        best, alts = ladders.picks("hands", visible, 6)
        self.assertEqual([item.item_id for item in best], [1])
        self.assertEqual([item.item_id for item in alts], [3, 2, 4])
        self.assertEqual(alts[1].score, 0)
        self.assertEqual(alts[2].score, 0)
        self.assertTrue(all(item.estimated and item.unscored for item in alts))
        self.assertEqual(ladders.picks("hands", alts, 6), ([], alts))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_lua_uses_the_main_hand_that_passes_the_filter(self):
        def prepare(ns):
            ns.data.lists.HUNTER = "\n".join((
                "S\t1\tBeast Mastery\tRanged DPS\tany", "L\t1\tpve\tmain\t10:90:t 11:65:p 12:60",
                "L\t1\tpve\toff\t20:10 21:40", "F\t1\tpve\tmain\ta\t10:90:t 11:65:p 12:60",
                "F\t1\tpve\toff\ta:11\t20:40 21:10", "F\t1\tpve\toff\ta:12\t21:20 20:10"))
        game = Game(cls="HUNTER", prepare=prepare)
        data = game.ns.Ladders.Decode("HUNTER")
        for rewards, two, main, off in ((True, False, 11, 20), (False, True, 10, 21)):
            select = game.lua.table(side="a", phase=0, pvpRewards=rewards, alternatives=6)
            result = game.ns.Ladders.Compute(data, 1, "pve", select)
            self.assertEqual(result.twoHand, two)
            self.assertEqual(result.main.best[1].id, main)
            self.assertEqual((result.off.other if two else result.off.best)[1].id, off)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_other_classes_can_use_faction_ranks_for_two_trinkets(self):
        def prepare(ns):
            ns.data.lists.MAGE = "\n".join((
                "S\t3\tFrost\tRanged DPS\tany", "L\t3\tpve\ttrinket\t1:90 2:75 3:60",
                "F\t3\tpve\ttrinket\ta\t2:90 1:75 3:60", "F\t3\tpve\ttrinket\th\t3:90 1:75 2:60"))
        game = Game(cls="MAGE", prepare=prepare)
        data = game.ns.Ladders.Decode("MAGE")
        for side, leader in (("a", 2), ("h", 3)):
            result = game.ns.Ladders.Compute(data, 3, "pve", game.lua.table(side=side, phase=0))
            self.assertEqual([p.id for p in result.trinket.best.values()], [leader, 1])

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_lua_keeps_main_hand_option_without_inventing_an_off_hand(self):
        def prepare(ns):
            ns.data.lists.HUNTER = "\n".join((
                "S\t1\tBeast Mastery\tRanged DPS\tany",
                "L\t1\tpve\tmain\t10:90:t 11:65 12:60 13:50 14:40:k",
                "L\t1\tpve\toff\t20:40",
                "F\t1\tpve\tmain\ta\t10:90:t 11:65 12:60 13:50 14:40:k",
                "F\t1\tpve\toff\ta:12\t20:40"))
        game = Game(cls="HUNTER", faction="Alliance", prepare=prepare)
        api = game.ns.Ladders
        data = api.Decode("HUNTER")
        flt = game.lua.table(side="a", phase=0, alternatives=2)
        slots = api.Compute(data, 1, "pve", flt)
        candidate = slots.main.other[1]
        self.assertEqual(candidate.id, 11)
        self.assertTrue(candidate.partialSet)
        self.assertIsNone(candidate.partner)
        self.assertFalse(list(slots.off.other.values()))
        self.assertEqual([pick.id for pick in slots.main.other.values()], [11, 12, 13, 14])
        self.assertTrue(api.HasFlag(slots.main.other[4].entry, "j"))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_beast_weapons_are_situational_in_pre_raid_bm_without_using_alternative_slots(self):
        options = {22314, 279910}
        for side in ("a", "h"):
            game = Game(cls="HUNTER")
            api = game.ns.Ladders
            data = api.Decode("HUNTER")
            for count in (2, 6):
                flt = game.lua.table(side=side, phase=0, pvpRewards=False, alternatives=count, unsourced=False)
                slots = api.Compute(data, 1, "pve", flt)
                self.assertTrue(slots.twoHand)
                self.assertTrue(options.isdisjoint(pick.id for pick in slots.main.best.values()))
                situational = [pick for pick in slots.main.alts.values() if api.HasFlag(pick.entry, "j")]
                self.assertTrue(options <= {pick.id for pick in situational})
                self.assertEqual(len(slots.main.alts) - len(situational), count)

    def test_pre_raid_hands_and_other_confirmed_choices(self):
        self.assertTrue(hunter_bm.read(), "the numerical input is part of the build")
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        full = {s: ladders.full_ladder(db, "HUNTER", 1, "pve", s) for s in hunter_bm.SLOTS}
        kept = {s: ladders.kept_ladder(s, v) for s, v in full.items()}
        for side, gloves in (("a", 271948), ("h", 18349)):
            expected = {"hands": gloves, "back": 13340, "waist": 272397, "neck": 15411, "wrist": 18375}
            if "feet" in hunter_bm.read()["slots"]:
                expected["feet"] = 226881
            flt = (side, False, False, 0, False, 6)
            visible = ladders.visible_slots(kept, flt)
            for slot, item_id in expected.items():
                self.assertEqual(ladders.lead(visible[slot]).shown(side), item_id, (side, slot))
            main, off = ladders.weapon_lists(visible["main"], visible["off"])
            other_main, other_off = ladders.other_weapons(visible["main"], visible["off"])
            self.assertEqual((main[0].shown(side), off), (250619, []))
            self.assertEqual(other_main[0].shown(side), 279259)
            self.assertEqual(other_off[0].shown(side), 286613)
            self.assertTrue(other_off[0].pvp_utility)
            self.assertEqual(next(e.shown(side) for e in other_off if not e.pvp_utility), 280021)
            self.assertAlmostEqual(main[0].score - other_main[0].score - other_off[0].score, 22.5, delta=0.5)
        for source in (full, kept):
            for flt in ladders.FILTERS:
                one = ladders.lead([e for e in ladders.visible(source["main"], flt) if not e.two_hand])
                if one:
                    key = (flt[0], one.shown(flt[0]))
                    left = source["off"].contexts.get(key, ())
                    self.assertNotIn(key[1], [e.shown(key[0]) for e in left])
                    if key not in source["off"].contexts:
                        self.assertEqual(ladders.visible_slots(source, flt)["off"], [])
        self.assertFalse(hasattr(ladders.full_ladder(db, "HUNTER", 1, "pvp", "hands"), "contexts"))
        self.assertFalse(hasattr(ladders.full_ladder(db, "HUNTER", 2, "pve", "hands"), "contexts"))
        self.assertFalse(hasattr(ladders.full_ladder(db, "HUNTER", 1, "pve", "hands", rank_rewards=False), "contexts"))
