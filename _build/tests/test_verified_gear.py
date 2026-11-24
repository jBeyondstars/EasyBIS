"""Client checks for the stat lines that affect healing or PvP choices."""
import copy
import sys
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import ladders
import specs
import verified_gear


class VerifiedGearTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")

    def test_healing_weapon_soulforge_and_passive_territory_bonuses(self):
        gear = self.db.gear
        self.assertEqual((gear[22333]["dps"], gear[22333]["weapon_hit"]), (39.29, (66, 99, 2.1)))
        self.assertEqual(gear[22333]["stats"], {5: 26, 7: 21, 41: 135, 42: 45})
        self.assertEqual(gear[19101]["stats"], gear[19102]["stats"])
        self.assertEqual(gear[226991]["stats"], {5: 12, 7: 26, 12: 3, 45: 8})
        self.assertEqual(gear[19120]["stats"].get(38), 14)
        self.assertEqual(gear[271903]["stats"].get(43), 5)
        self.assertEqual(gear[21565]["stats"].get(47), 3)
        for item in (12960, 22225):
            self.assertIn('r', self.db.items[item]['flags'])

    def test_feral_attack_power_follows_the_active_form(self):
        for number, spec in self.db.classes['DRUID']['specs'].items():
            for mode, profile in ladders.MODES.items():
                weights = spec['weights'][profile]
                if number in (2, 4):
                    self.assertEqual(weights[specs.FERAL_ATTACK_POWER], weights[specs.ATTACK_POWER])
                    gear = {e.item_id: e for e in ladders.full_ladder(self.db, 'DRUID', number, mode, 'main')}
                    for item, power in ((21407, 140), (22632, 420)):
                        self.assertIn(item, gear)
                        without = {stat: value for stat, value in weights.items() if stat != specs.FERAL_ATTACK_POWER}
                        delta = ladders.score(self.db, item, weights, 'DRUID') - ladders.score(self.db, item, without, 'DRUID')
                        self.assertAlmostEqual(delta, power * weights[specs.ATTACK_POWER])
                else:
                    self.assertNotIn(specs.FERAL_ATTACK_POWER, weights)

    def test_preserve_newer_independent_observations_and_apply_only_once(self):
        db = copy.copy(self.db)
        db.gear = {19102: {'stats': {5: 25, 7: 28, 45: 103}}}
        db.items = {12960: {'flags': 'r'}}
        for _ in range(2):
            verified_gear.apply(db)
        self.assertEqual(db.gear[19102]['stats'], {5: 25, 7: 28, 45: 103})
        self.assertEqual(db.items[12960]['flags'], 'r')

    def test_pvp_humanoid_attack_power_keeps_the_permanent_and_conditional_lines_separate(self):
        gear = self.db.gear[18502]["stats"]
        self.assertEqual((gear[specs.ATTACK_POWER], gear[specs.HUMANOID_ATTACK_POWER]), (24, 36))
        for cls, number in (("PALADIN", 3), ("HUNTER", 1), ("HUNTER", 3), ("WARRIOR", 1)):
            spec = self.db.classes[cls]["specs"][number]
            pvp = spec["weights"]["pvp"]
            ordinary = {stat: value for stat, value in pvp.items() if stat != specs.HUMANOID_ATTACK_POWER}
            extra = ladders.score(self.db, 18502, pvp, cls) - ladders.score(self.db, 18502, ordinary, cls)
            self.assertAlmostEqual(extra, 36 * pvp[specs.ATTACK_POWER])
            self.assertNotIn(specs.HUMANOID_ATTACK_POWER, spec["weights"]["raid"])

    def test_enhancement_keeps_its_published_humanoid_weight_with_site_rules(self):
        weights = self.db.classes["SHAMAN"]["specs"][2]["weights"]["pvp"]
        self.assertEqual(weights[specs.HUMANOID_ATTACK_POWER], 0.3)
        rows = ladders.full_ladder(self.db, "SHAMAN", 2, "pvp", "feet", rank_rewards=False)
        greaves = next(e for e in rows if e.item_id == 18694)
        self.assertEqual(greaves.score, ladders.score(self.db, 18694, weights, "SHAMAN"))
