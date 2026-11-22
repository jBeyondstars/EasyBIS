"""The pre-raid healer weapons have real sources and rank through the equipped weapon style."""
import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import caster_gear
import fdb
import ladders
from test_addon import Game, lupa


class CasterGearTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")

    def test_eligibility_and_permanent_stats(self):
        caster_gear.include(self.db)
        self.assertEqual(self.db.gear[12930]["stats"], {45: 15})
        for cls, data in self.db.classes.items():
            for spec in data["specs"].values():
                pools = spec.get("pools", {})
                for pool in pools.values():
                    for item in caster_gear.ITEMS:
                        self.assertLessEqual(sum(i == item for i, _ in pool), 1)
                if spec["role"] != "Healer" and spec["role"] != "Caster DPS" and spec["slug"] != "shockadin":
                    self.assertNotIn(13968, [i for i, _ in pools.get("trinket", ())])
                if cls in {"MAGE", "WARLOCK"}:
                    self.assertNotIn(22315, [i for i, _ in pools.get("mh", ())])

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_drakkisath_quest_rewards_show_the_selected_factions_quest(self):
        for faction, quest in (("Alliance", "General Drakkisath's Demise"), ("Horde", "For The Horde!")):
            game = Game(faction=faction)
            for item in (13968, 13966):
                with self.subTest(faction=faction, item=item):
                    self.assertEqual(game.ns.Sources.Describe(item).detail, quest)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_both_factions_see_the_correct_healer_weapon_set(self):
        game = Game()
        for cls, spec in (("DRUID", 3), ("PALADIN", 1), ("PRIEST", 1), ("PRIEST", 2), ("SHAMAN", 3)):
            data = game.ns.Ladders.Decode(cls)
            for side in "ah":
                with self.subTest(cls=cls, spec=spec, side=side):
                    selected = game.ns.Ladders.Compute(data, spec, "pve", game.lua.table(
                        side=side, phase=0, pvpRewards=False, rankCap=6, alternatives=2))
                    self.assertEqual(selected.off.best[1].id, 22319)
                    hammer = selected.main.best[1] if cls == "PALADIN" else selected.main.alts[1]
                    self.assertEqual(hammer.id, 22315)
