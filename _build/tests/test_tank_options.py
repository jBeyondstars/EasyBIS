import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(BUILD / "tests"), str(BUILD)]
import tank_options
from test_addon import Game, lupa, strip_colors


@unittest.skipIf(lupa is None, "lupa is not installed")
class TankOptionTest(unittest.TestCase):
    def test_protection_paladin_pre_raid_order(self):
        for faction, weapons in (
                ("Alliance", [22383, 2243, 18048, 18396, 227935, 11784, 279261]),
                ("Horde", [22383, 2243, 18048, 281586, 18396, 227935, 11784])):
            with self.subTest(faction=faction):
                game = Game(faction=faction)
                ns = game.ns
                ns.Alternatives = game.lua.eval("function() return 6 end")
                state = game.lua.table_from({"class": "PALADIN", "spec": 2, "list": "pve", "slot": "main"})
                rows, _ = ns.Rows.Items(state, True)
                self.assertEqual([r.id for r in rows.values() if r.kind == "item"][:7], weapons)
                state.slot = "trinket"
                for with_alts in (True, False):
                    rows, _ = ns.Rows.Items(state, with_alts)
                    gear = [r for r in rows.values() if r.kind == "item"]
                    self.assertEqual([r.id for r in gear[:3]], [14557, 272440, 272438])
                    self.assertEqual(gear[2].option.label, "Threat")
                    self.assertTrue(gear[2].option.exclusive)

    def test_measured_pairs_in_the_lists_and_item_tooltips(self):
        for side, faction in (("a", "Alliance"), ("h", "Horde")):
            game = Game(locale="frFR", faction=faction)
            ns = game.ns
            ns.SetOption(ns, "alternatives", False)
            for (cls, spec), duels in tank_options.DUELS.items():
                for slot, duel in duels.items():
                    with self.subTest(side=side, cls=cls, slot=slot):
                        self.assertIn(tank_options.record(spec, slot, duel), ns.data.lists[cls])
                        state = game.lua.table_from({"class": cls, "spec": spec, "list": "pve", "slot": slot})
                        for with_alts in (False, True):
                            rows, _ = ns.Rows.Items(state, with_alts)
                            gear = [r for r in rows.values() if r.kind == "item"]
                            annotated = {r.id: r for r in gear if r.option}
                            self.assertEqual(len(gear), len({r.id for r in gear}))
                            self.assertEqual(set(annotated), set(duel[:2]))
                            for item, label in zip(duel[:2], ("Threat", "Mitigation")):
                                row = annotated[item]
                                self.assertEqual(row.option.label, label)
                                self.assertIsNone(row.gap)
                                self.assertEqual(row.why, ns.Notes.For(item, cls, spec, "pve", slot))
                                self.assertIn(ns.Items.Name(row.option.rival), ns.Ladders.OptionNote(row.option))
                                self.assertTrue(any(label in text for _, text in game.lines(item)))
                            delta = duel[2 if side == "a" else 3]
                            self.assertEqual(list(annotated[duel[0]].option.delta.values()), list(delta))

    def test_scope_and_filtered_rival(self):
        game = Game()
        ns = game.ns
        self.assertIsNone(ns.Ladders.For("PALADIN", 2, "pve").off.options)
        self.assertIsNone(ns.Ladders.For("DRUID", 2, "pvp").hands.options)
        self.assertIsNone(ns.Ladders.For("DRUID", 4, "pve").hands.options)
        ns.SetOption(ns, "seenOnly", True)
        self.assertIsNone(ns.Ladders.For("WARRIOR", 3, "pve").back.options)
        ns.SetOption(ns, "seenOnly", False)
        self.assertIsNotNone(ns.Ladders.For("WARRIOR", 3, "pve").back.options)
        ns.SetPhase(ns, 1)
        self.assertIsNone(ns.Ladders.For("WARRIOR", 3, "pve").back.options)
        self.assertFalse(any("Threat" in text for _, text in game.lines(22411)))

    def test_bear_list_and_character_sheet_use_one_trinket_at_a_time(self):
        game = Game(saved="EasyBISCharDB = {class='DRUID',spec=2,list='pve'}")
        ns = game.ns
        ns.SetOption(ns, "listAlts", False)
        ns.Browser.Open()
        ns.Browser.ShowSlot("trinket")
        window = ns.Browser.window
        frames = [window.rows[i] for i in range(1, len(window.rowData) + 1)]
        ranked = {f.data.id: f for f in frames if f.data.option}
        self.assertEqual({i: strip_colors(f.rank.text) for i, f in ranked.items()},
                         {272437: "Threat", 272440: "Mitigation"})
        self.assertIn("Equip only one.", ns.Ladders.OptionNote(ranked[272437].data.option))
        cells = [c for c in ns.Rows.Character(ns.Browser.state).values() if c.slot == "trinket"]
        self.assertEqual(sum(c.id in ranked for c in cells), 1)
        cell = next(c for c in cells if c.id in ranked)
        self.assertEqual({p.id for p in cell.tankOptions.values()}, set(ranked) - {cell.id})
        game.stub.equipLocs[272437] = "INVTYPE_TRINKET"
        self.assertEqual(ns.Custom.Add("DRUID", 2, "pve", 272437, "trinket")[1], "listed")


if __name__ == "__main__":
    unittest.main()
