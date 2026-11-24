"""Check faction rewards through the generator and the shipped PvP item browser."""
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS.parent))
sys.path.insert(0, str(TESTS))

import fdb
import ladders
import pvp_factions
from test_addon import Game, lupa


class PvpFactionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(TESTS.parent / "cache" / "ForeverDB")

    def test_each_reward_is_eligible_only_for_its_faction(self):
        sides = pvp_factions.SIDES
        covered = set()
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for slot, _ in ladders.SLOTS:
                    for entry in ladders.full_ladder(self.db, token, spec, "pvp", slot):
                        if entry.item_id not in sides:
                            continue
                        covered.add(entry.item_id)
                        for side in ("a", "h"):
                            self.assertEqual(entry.passes((side, True, False, 9, True)),
                                             sides[entry.item_id] == side, (token, spec, slot, entry.item_id))
        self.assertEqual(covered, set(sides))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_published_rows_for_both_factions(self):
        for faction, side in (("Alliance", "a"), ("Horde", "h")):
            game = Game(faction=faction)
            game.ns.SetAlternatives(game.ns, game.ns.MaxAlternatives())
            for available_now in (False, True):
                game.ns.SetOption(game.ns, "availableNow", available_now)
                game.ns.SetOption(game.ns, "unsourced", True)
                for token in self.db.classes:
                    for spec in game.ns.Ladders.Specs(token).values():
                        state = game.lua.table_from({"class": token, "spec": spec.index, "list": "pvp"})
                        rows, _ = game.ns.Rows.Items(state, True)
                        for row in rows.values():
                            if row.kind == "item" and row.id in pvp_factions.SIDES:
                                self.assertEqual(pvp_factions.SIDES[row.id], side, (token, spec.index, row.id))

    def test_rank_cap_and_observation_stay_specific_to_each_item(self):
        # The Alliance hunter chest was added from a capture. Both chests are blue honor gear.
        hunter = ladders.full_ladder(self.db, "HUNTER", 1, "pvp", "chest")
        for side, own, other in (("a", 272734, 272490), ("h", 272490, 272734)):
            visible = {e.shown(side) for e in hunter if e.passes((side, False, False, 0, True, 6))}
            self.assertIn(own, visible)
            self.assertNotIn(other, visible)
        # The Horde rogue helm has an observed vendor. Its Alliance counterpart does not.
        rogue = ladders.full_ladder(self.db, "ROGUE", 1, "pvp", "head")
        for side, item, observed in (("a", 272727, False), ("h", 272474, True)):
            visible = {e.shown(side) for e in rogue if e.passes((side, False, True, 0, True, 6))}
            self.assertEqual(item in visible, observed)


if __name__ == "__main__":
    unittest.main()
