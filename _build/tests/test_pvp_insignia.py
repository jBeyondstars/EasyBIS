"""The rank-two control break is visible without replacing either ordinary trinket."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import fdb
import ladders
import pvp_insignia
import ranks
from test_addon import Game, lupa


class InsigniaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(HERE.parent / "cache" / "ForeverDB")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_survival_melee_option_keeps_the_ranked_picks_and_obeys_the_filters(self):
        game = Game(cls="HUNTER")
        data = game.ns.Ladders.Decode("HUNTER")
        ladder = ladders.kept_ladder("main", ladders.full_ladder(self.db, "HUNTER", 3, "pvp", "main"))
        for side in "ah":
            for phase, seen in ((0, False), (0, True), (9, False), (0, False)):
                flt = (side, False, seen, phase, True, 6)
                rows = ladders.visible(ladder, flt)
                expected, alts = ladders.picks("main", rows, 3)
                picks = game.ns.Ladders.Compute(data, 3, "pvp", game.lua.table(
                    side=side, seenOnly=seen, phase=phase, pvpRewards=True, rankCap=6, alternatives=3)).main
                self.assertEqual([p.id for p in picks.best.values()], [e.shown(side) for e in expected])
                self.assertEqual([p.id for p in picks.alts.values()], [e.shown(side) for e in alts])
                extra = [p for p in picks.alts.values() if p.id == 12583 and game.ns.Ladders.HasFlag(p.entry, "j")]
                self.assertEqual(bool(extra), phase == 0 and not seen)
                if extra:
                    self.assertTrue(game.ns.Ladders.HasFlag(extra[0].entry, "x"))
                    self.assertEqual({e.item_id for e in alts if e.pvp_utility}, {12583, 13348})
                    self.assertEqual(len([e for e in alts if not e.pvp_utility]), 3)
                    self.assertFalse(any(e.item_id == 12583 for e in expected))

    def test_all_specs_offer_an_additional_pvp_choice_at_rank_two(self):
        count = 0
        for cls, data in self.db.classes.items():
            for spec in data["specs"]:
                count += 1
                pve = ladders.full_ladder(self.db, cls, spec, "pve", "trinket")
                self.assertFalse(any(e.pvp_utility for e in pve))
                pvp = ladders.full_ladder(self.db, cls, spec, "pvp", "trinket")
                self.assertEqual([e.item_id for e in pvp if e.pvp_utility], [pvp_insignia.ALLIANCE])
                for side, item_id in (("a", pvp_insignia.ALLIANCE), ("h", pvp_insignia.HORDE)):
                    with self.subTest(cls=cls, spec=spec, side=side):
                        eligible = [e for e in pvp if e.passes((side, False, False, 0, True, 2))]
                        control = eligible[-1]
                        self.assertEqual(control.shown(side), item_id)
                        self.assertTrue(control.unscored and control.pvp and control.honor)
                        self.assertFalse(control.passes((side, True, True, 0, True, 1)))
                        self.assertFalse(control.passes((side, True, True, 0, False, 14)))
                        self.assertEqual(ranks.required(self.db.items[item_id], self.db.gear[item_id]), 2)
                        for limit in (ladders.ALTERNATIVES, ladders.MAX_ALTERNATIVES):
                            best, ordinary = ladders.picks("trinket", eligible[:-1], limit)
                            self.assertEqual(ladders.picks("trinket", eligible, limit), (best, ordinary + [control]))
        self.assertEqual(count, 29)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_shipped_lua_and_localized_note(self):
        for faction, item_id, locale, term in (("Alliance", 274445, "frFR", "pertes de contrôle"),
                                               ("Horde", 274444, "enUS", "loss of control")):
            game = Game(locale=locale, faction=faction)
            for cls, data in self.db.classes.items():
                for spec in data["specs"]:
                    result = game.ns.Ladders.For(cls, spec, "pvp").trinket
                    seen = [pick.id for pick in result.alts.values()]
                    self.assertEqual(seen.count(item_id), 1)
                    self.assertNotIn(item_id, [pick.id for pick in result.best.values()])
                    pick = next(pick for pick in result.alts.values() if pick.id == item_id)
                    self.assertTrue(game.ns.Ladders.HasFlag(pick.entry, "x"))
                    self.assertFalse(game.ns.Ladders.IsTie(result, pick))
                    self.assertIn(term, game.ns.Notes.For(item_id, cls, spec, "pvp", "trinket"))
                    self.assertIsNone(game.ns.Notes.For(item_id, cls, spec, "pve", "trinket"))
                    state = game.lua.table_from({"class": cls, "spec": spec, "list": "pvp", "slot": "trinket"})
                    rows, _ = game.ns.Rows.Items(state)
                    row = next(r for r in rows.values() if r.id == item_id)
                    self.assertTrue(row.level)
                    self.assertFalse(row.bis or row.tie)
                    self.assertIsNone(row.gap)
                    self.assertIn(term, row.why)
