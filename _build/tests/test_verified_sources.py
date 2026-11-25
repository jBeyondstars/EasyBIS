"""Check the reviewed acquisition routes in the generator and in the shipped addon."""

from pathlib import Path
import sys
import unittest

TESTS = Path(__file__).resolve().parent
sys.path[:0] = [str(TESTS.parent), str(TESTS)]

import fdb
import ladders
import phases
from test_addon import Game, lupa


class VerifiedSourcesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(TESTS.parent / "cache" / "ForeverDB")

    def test_all_reviewed_acquisitions_are_pre_raid(self):
        reviewed = self.db.verified_sources
        self.assertEqual(len(reviewed), 83)
        alliance = {270112, 270275, 270276, 272704, 272706, 272708, 272710, *range(272726, 272730),
                    277236, 279931}
        horde = {260196, 270126, 270225, *range(272548, 272554), 272630, 272643, 279932,
                 281586, 281587, 281588, 285346}
        for item, record in reviewed.items():
            with self.subTest(item=item):
                entry = self.db.items[item]
                side = "a" if item in alliance else "h" if item in horde else ""
                self.assertEqual(entry["side"], side)
                self.assertEqual(phases.item_phase(entry), phases.PRE_RAID)
                self.assertTrue(entry["sources"])
                self.assertIn("s", entry["flags"])
                self.assertNotIn("u", entry["groups"])
                for source in record["sources"]:
                    if side and source[0] in ("q", "V"):
                        self.assertEqual(source[4 if source[0] == "q" else 3], side)
        for item in (260211, 260212, 270123, 270124, 270125):
            self.assertEqual({source[4] for source in self.db.items[item]["sources"]}, {"a", "h"})

    def test_class_quest_rewards_only_appear_for_the_eligible_class(self):
        for item, slot in ((227935, "main"), (277236, "shoulder")):
            self.assertEqual(self.db.class_only[item], {"PALADIN"})
            entries = ladders.full_ladder(self.db, "WARRIOR", 2, "pve", slot)
            self.assertNotIn(item, {entry.item_id for entry in entries})

    def test_staff_of_jordan_is_not_recommended_to_hunters(self):
        for spec in self.db.classes["HUNTER"]["specs"]:
            for mode in ("pve", "pvp"):
                with self.subTest(spec=spec, mode=mode):
                    weapons = ladders.full_ladder(self.db, "HUNTER", spec, mode, "main")
                    self.assertNotIn(ladders.STAFF_OF_JORDAN, {entry.item_id for entry in weapons})

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_addon_has_all_reviewed_routes_and_keeps_its_rankings(self):
        for faction, side in (("Alliance", "a"), ("Horde", "h")):
            with self.subTest(faction=faction):
                game = Game(faction=faction)
                for item in self.db.verified_sources:
                    self.assertNotEqual(game.ns.Sources.Describe(item).category, "unknown", item)
                self.assertEqual(game.ns.Sources.Describe(873).detail, "Twilight Ritualist")
                self.assertNotRegex(game.ns.data.lists["HUNTER"], r"(?<!\S)873:")
                self.assertEqual(game.ns.Sources.Describe(281636).detail, "Greater Friend of the Library")
                self.assertEqual(game.ns.Sources.Describe(270123).detail,
                                 "Hurley Blackbreath" if side == "a" else "Lost Thunderbrew Recipe")
                self.assertEqual(game.ns.Sources.Describe(287025).category, "dungeon")
                self.assertEqual(game.ns.Sources.Describe(287018).detail, "Defias Truthfinder")
                self.assertEqual(game.ns.Sources.Describe(286556).detail, "Soul of Tanaris")
                assembly = game.ns.Sources.Describe(9372)
                self.assertEqual(assembly.zone, "Zul'Farrak")
                self.assertIn("Jang'thraze the Protector", assembly.detail)
                self.assertIn("Sang'thraze the Deflector", assembly.detail)
                self.assertEqual(assembly.percent, "")
                self.assertEqual(game.ns.Sources.Describe(227935).detail, "A Thane's Gratitude")
                self.assertEqual(game.ns.Sources.Runs(279932)[1].instance, 3001)
                self.assertEqual(game.ns.Sources.Describe(274420).cost.amount, 20)
                self.assertIsNotNone(game.ns.Reputation.Requirement(274420))
                flt = game.lua.table(side=side, phase=0, alternatives=6, pvpRewards=True, unsourced=False)
                ladders = game.ns.Ladders
                priest = ladders.Compute(ladders.Decode("PRIEST"), 3, "pvp", flt)
                self.assertIn(281636, {pick.id for pick in priest["neck"].alts.values()})
                flt.seenOnly = True
                priest = ladders.Compute(ladders.Decode("PRIEST"), 3, "pvp", flt)
                self.assertIn(287018, {pick.id for pick in priest["hands"].alts.values()})
                flt.seenOnly = False
                flt.pvpRewards = False
                mage = ladders.Compute(ladders.Decode("MAGE"), 1, "pve", flt)
                weapons = {pick.id for group in (mage["main"].best, mage["main"].alts, mage["main"].other)
                           if group for pick in group.values()}
                self.assertIn(873, weapons)


if __name__ == "__main__":
    unittest.main()
