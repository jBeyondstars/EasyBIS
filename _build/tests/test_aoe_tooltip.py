"""AoE item-tooltip memberships use the slot ranking and the tooltip preferences."""
import unittest

from test_addon import Game, lupa


@unittest.skipIf(lupa is None, "lupa is not installed")
class AoeTooltipTest(unittest.TestCase):
    def test_rank_faction_count_and_tooltip_options(self):
        game = Game(cls="MAGE")
        ns = game.ns
        # Isolate tooltip-only candidates from the real Raid and PvP memberships.
        ns.data.aoe.lists = game.lua.eval("""{
            ["MAGE:3:a"] = {head = {{910001}, {910002}, {910003}, {910004}}, off = {{910002}}},
            ["MAGE:3:h"] = {head = {{910005}}},
            ["ROGUE:2:a"] = {head = {{910001}}}
        }""")
        ns.Index.Reset()
        self.assertEqual(len(game.lines(910001)), 2)
        self.assertTrue(all(right == "BIS AoE/Dung" for _, right in game.lines(910001)))
        self.assertIn(("<classicon-mage> Mage Frost", "BIS AoE/Dung"), game.tooltip(910001))
        self.assertEqual(game.lines(910002)[0][1], "BIS AoE/Dung")  # best of both slots
        self.assertEqual(game.lines(910003)[0][1], "Alt AoE/Dung")
        self.assertEqual(game.lines(910004), [])
        ns.SetAlternatives(ns, 3)
        self.assertEqual(game.lines(910004)[0][1], "Alt AoE/Dung")
        ns.SetOption(ns, "onlyMyClass", True)
        self.assertEqual(game.lines(910001), [("<classicon-mage> Mage Frost", "BIS AoE/Dung")])
        ns.SetOption(ns, "alternatives", False)
        self.assertEqual(game.lines(910004), [])
        self.assertTrue(game.lines(910001))
        game.slash("faction horde")
        self.assertEqual(game.lines(910001), [])
        self.assertTrue(game.lines(910005))
        ns.SetListShown(ns, "pve", False)
        ns.SetListShown(ns, "pvp", False)
        self.assertTrue(game.lines(910005))
        ns.SetListShown(ns, "aoe", False)
        self.assertEqual(game.lines(910005), [])

    def test_raid_and_dungeon_labels_when_both_apply(self):
        game = Game(cls="SHAMAN")
        ns = game.ns
        helm = 252605
        ns.data.aoe.lists["SHAMAN:2:a"] = game.lua.eval("{head = {{252605}}}")
        ns.Index.Reset()
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "BIS Raid · BIS AoE/Dung"),
                      game.lines(helm))
        ns.SetListShown(ns, "aoe", False)
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "BIS PvE"), game.lines(helm))


if __name__ == "__main__":
    unittest.main()
