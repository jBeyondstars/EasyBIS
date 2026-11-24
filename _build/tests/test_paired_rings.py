"""Filtering the first ring can change the gain, order and ties of the second."""
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hunter_bm
import ladders
import notes
from test_addon import Game, lupa


class PairedRingsTest(unittest.TestCase):
    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_weapon_style_uses_the_off_hand_actually_displayed(self):
        # The dagger (12) has a score in both slots. The displayed pair is 12 + 13.
        one = ladders.Entry(12, 30, "", None, True, False, False, False, False, False, None)
        two = replace(one, item_id=11, score=45, two_hand=True)
        off = [replace(one, score=25), replace(one, item_id=13, score=10)]
        self.assertEqual(ladders.weapon_lists([two, one], off), ([two], []))
        self.assertEqual(ladders.other_weapons([two, one], off), ([one], [off[1]]))
        def prepare(ns):
            ns.data.lists.HUNTER = "\n".join(("S\t1\tBeast Mastery\tRanged DPS\tany",
                "L\t1\tpvp\tmain\t11:450:t 12:300", "L\t1\tpvp\toff\t12:250 13:100"))
        game = Game(cls="HUNTER", prepare=prepare)
        view = game.ns.Ladders.Compute(game.ns.Ladders.Decode("HUNTER"), 1, "pvp", game.lua.table(side="a"))
        self.assertTrue(view.twoHand)
        self.assertEqual([row.id for row in view.main.best.values()], [11])
        self.assertEqual([row.id for row in view.off.other.values()], [13])

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_two_bis_slots_do_not_promote_an_incomplete_archived_measure(self):
        estimated, measured = [ladders.Entry(i, 1, "", None, True, False, False, False, False, False, None)
                               for i in (11, 22)]
        estimated = replace(estimated, estimated=True)
        for entries, expected in (([estimated, measured], [22]), ([estimated], [])):
            best, alts = ladders.picks("trinket", entries)
            self.assertEqual([entry.item_id for entry in best], expected)
            self.assertEqual([entry.item_id for entry in alts], [11])
            def prepare(ns):
                tokens = "11:100:sg" + (" 22:90:s" if len(entries) == 2 else "")
                ns.data.lists.MAGE = "S\t2\tFire\tRanged DPS\tany\nL\t2\tpve\ttrinket\t" + tokens
            game = Game(cls="MAGE", prepare=prepare)
            result = game.ns.Ladders.Compute(game.ns.Ladders.Decode("MAGE"), 2, "pve", game.lua.table(side="a"))
            self.assertEqual([pick.id for pick in result.trinket.best.values()], expected)
            self.assertEqual([pick.id for pick in result.trinket.alts.values()], [11])

    def test_a_model_note_requires_the_same_limit_in_all_visible_contexts(self):
        raw = [ladders.Entry(i, 0, "", None, True, False, False, True, False, False, None) for i in (1, 2)]
        def contexts(model):
            return {"1": [1, 0.1, 2000, model], "2": [2, 0.1, 2000, "unverified_proc_rate"]}
        scores = {"finger": {"a": contexts("measured"), "h": contexts("unregistered_effect")}}
        ladder = hunter_bm.rank_contexts(raw, "finger", {1: 1, 2: 1}, scores)
        db = SimpleNamespace(simulated=SimpleNamespace(specs={("WARLOCK", 2): SimpleNamespace(record={})}))
        found = notes.simulation_limits(db, {"WARLOCK": {2: {"pve": {"finger": ladder}}}})
        self.assertEqual([(n["slot"], n["items"]) for n in found], [("finger", [2])])

    def test_generator_keeps_the_first_ring_and_reselects_the_companion(self):
        def measured(gain):
            return [gain, 0.05, 20000, "measured"]

        raw = [ladders.Entry(i, 0, "", None, True, False, False, True, False, False, None)
               for i in (10, 20, 30)]
        raw[0] = replace(raw[0], pvp=True)
        scores = {"finger": {"a": {"10": measured(15), "20": measured(12), "30": measured(11)},
                             "a:10": {"20": measured(9), "30": measured(12)}}}
        full = hunter_bm.rank_contexts(raw, "finger", {i.item_id: 1 for i in raw}, scores)
        for ladder in (full, ladders.kept_ladder("finger", full)):
            for rewards, expected in ((True, [10, 30, 20]), (False, [20, 30])):
                result = ladders.visible_slots({"finger": ladder}, ("a", False, False, 0, rewards, 6))
                best, alts = ladders.picks("finger", result["finger"], 6)
                self.assertEqual([e.item_id for e in best + alts], expected)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_lua_matches_the_equipped_companion_for_order_and_ties(self):
        def prepare(ns):
            ns.data.lists.WARLOCK = "\n".join((
                "S\t2\tDemonology\tRanged DPS\tany", "L\t2\tpve\tfinger\t10:100:p 20:90 30:85 40:85",
                "F\t2\tpve\tfinger\ta\t10:100:p 20:90 30:85 40:85",
                "F\t2\tpve\tfinger\ta:10\t30:120 40:120 20:100"))
        game = Game(cls="WARLOCK", prepare=prepare)
        data = game.ns.Ladders.Decode("WARLOCK")
        for rewards, expected in ((True, (10, 30)), (False, (20, 30))):
            flt = game.lua.table(side="a", phase=0, pvpRewards=rewards, alternatives=6)
            result = game.ns.Ladders.Compute(data, 2, "pve", flt)
            picks = result.finger
            self.assertEqual(tuple(row.id for row in picks.best.values()), expected)
            self.assertTrue(game.ns.Ladders.IsTie(picks, picks.alts[1]))
            if rewards:
                self.assertEqual(picks.alts[1].pairedWith, 10)
                self.assertFalse(game.ns.Ladders.IsTie(picks, picks.alts[2]))
                game.ns.Ladders.For = lambda *args: result
                state = game.lua.table_from({"class": "WARLOCK", "spec": 2, "list": "pve", "slot": "finger"})
                rows, _ = game.ns.Rows.Items(state, True)
                displayed = {row.id: row for row in rows.values()}
                self.assertEqual(displayed[20].gap, -17)
                self.assertFalse(displayed[20].tie)
                self.assertTrue(displayed[40].tie)
