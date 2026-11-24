import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_jewelry as jewelry


class AoeJewelryTest(unittest.TestCase):
    def test_maelstrom_requires_melee_hits_and_its_native_proc_as_a_fixed_partner(self):
        melee = {"class": "WARRIOR", "spec": 2, "pairedItems": {"trinket": 19289}}
        jewelry.validate_candidate(melee, 19289, {})
        for spec in (1, 2, 3):
            with self.assertRaisesRegex(ValueError, "19289"):
                jewelry.validate_candidate({"class": "HUNTER", "spec": spec}, 19289, {})
        with self.assertRaisesRegex(ValueError, "23687"):
            jewelry.validate_pair(melee, "trinket", {"id": 1}, {"id": 19289})
        jewelry.validate_pair(melee, "trinket", {"id": 1},
                              {"id": 19289, "itemEffects": [{"buffId": 23687}]})

    def test_hunter_and_frost_selection(self):
        hunter = {"class": "HUNTER", "spec": 2}
        frost = {"class": "MAGE", "spec": 3}
        jewelry.validate_candidate(hunter, 13965, {})
        jewelry.validate_candidate(frost, 13968, {})
        for profile, item_id, stats in (
            (hunter, 13968, {}), (hunter, 12930, {"spell": 15, "healing": 15}),
            (frost, 13965, {}), (frost, 1, {"fire": 12}),
        ):
            with self.subTest(item_id=item_id), self.assertRaises(ValueError):
                jewelry.validate_candidate(profile, item_id, stats)

    def test_partner_equipment_conflicts(self):
        for left, right in (
            ({"id": 1}, {"id": 1}),
            ({"id": 1, "limitCategory": 707}, {"id": 2, "limitCategory": 707}),
            ({"id": 13965}, {"id": 13968}),
        ):
            with self.subTest(left=left, right=right), self.assertRaises(ValueError):
                jewelry.validate_pair({"pairedItems": {"trinket": right["id"]}}, "trinket", left, right)

    def test_eye_of_the_beast_has_spell_crit(self):
        profile = {"pairedItems": {"trinket": 11832}}
        companion = {"id": 11832}
        item = {"id": 13968, "pseudoStats": [0] * 15 + [1], "itemEffects": [{"buffId": 1287840}]}
        jewelry.validate_pair(profile, "trinket", item, companion)
        with self.assertRaises(ValueError):
            jewelry.validate_pair(profile, "trinket", dict(item, pseudoStats=[0] * 14 + [1]), companion)

    def test_damage_buffs_must_proc_in_the_pack(self):
        for item_id, key, action_id in ((22268, "spellId", 1318930), (280071, "itemId", 280071)):
            with self.subTest(item_id=item_id):
                with self.assertRaises(ValueError):
                    jewelry.measured_buff(item_id, {"auras": []})
                player = {"auras": [{"id": {key: action_id}, "procsAvg": 0.2, "uptimeSecondsAvg": 2.5}]}
                self.assertEqual(jewelry.measured_buff(item_id, player)["offensiveBuff"]["secondsPerPack"], 2.5)

    def test_sources_preserve_raid_pools_and_faction_quests(self):
        db = SimpleNamespace(items={}, gear={}, classes={})
        jewelry.include_trinkets(db)
        self.assertEqual(db.classes, {})
        self.assertEqual(db.gear[12930]["stats"], {45: 15})
        self.assertEqual({(s[1], s[4]) for s in db.items[13968]["sources"]}, {("4974", "h"), ("5102", "a")})

    def test_carried_proc_damage_must_hit_an_enemy(self):
        for item, spell in ((22321, "27655"), (280032, "1315996")):
            jewelry.validate_row(item, {"targetsHitPerPack": {spell: [1]}})
            for hits in ([], [0], [5]):
                with self.subTest(item=item, hits=hits), self.assertRaises(ValueError):
                    jewelry.validate_row(item, {"targetsHitPerPack": {spell: hits}})

    def test_hurricane_only_pack_records_zero_for_route_only_procs(self):
        aura = {"id": {"spellId": 1318930}, "procsAvg": 0, "uptimeSecondsAvg": 0}
        evidence = jewelry.measured_buff(22268, {"auras": [aura]}, inactive=True)
        emblem = dict(evidence, gain=0, se=0)
        eyeball = {"targetsHitPerPack": {"1315996": [0]}, "gain": 0, "se": 0}
        for item, row in ((22268, emblem), (280032, eyeball)):
            jewelry.validate_row(item, row, route_only=True)
            with self.assertRaises(ValueError):
                jewelry.validate_row(item, row)
            with self.assertRaises(ValueError):
                jewelry.validate_row(item, dict(row, gain=10), route_only=True)
        with self.assertRaises(ValueError):
            jewelry.measured_buff(22268, {"auras": []}, inactive=True)

    def test_dungeon_only_effect_needs_its_own_proc_and_the_scored_replay(self):
        for item, proof in (
            (22268, {"spellId": 1318930, "procsPerRoute": 0.4, "secondsPerRoute": 3.5}),
            (280032, {"spellId": 1315996, "damagePerPack": [0.0, 38.0, 12.0]}),
        ):
            row = {"id": item, "gain": 20.1, "se": 4.2, "avgSeconds": 44,
                   "packDamage": [3000, 2500, 4500], "routeEffect": dict(proof, meanDamage=10000, pairedSE=4.2)}
            jewelry.validate_dungeon_effect(row, 9979.9)
            with self.assertRaises(ValueError):
                jewelry.validate_dungeon_effect(dict(row, se=3), 9979.9)
            wrong = dict(row["routeEffect"], secondsPerRoute=0, damagePerPack=[0, 0, 0])
            with self.assertRaises(ValueError):
                jewelry.validate_dungeon_effect(dict(row, routeEffect=wrong), 9979.9)

    def test_losing_talisman_activation_retains_evidence_from_the_active_trial(self):
        buff = {"spellId": 1315878, "procsPerPack": 1, "secondsPerPack": 15}
        trial = {"usesPerRun": 1, "gainOverPassive": -143.4157, "seOverPassive": 3.0763, "offensiveBuff": buff}
        passive = {"usesPerRun": 0, "gain": 0, "passiveGain": 0, "activeGain": -143.4157, "activeTrial": trial}
        jewelry.validate_row(280071, passive)
        for row in (dict(passive, offensiveBuff=buff), dict(passive, activeTrial={}),
                    dict(passive, activeGain=100, activeTrial=dict(trial, gainOverPassive=100)),
                    dict(passive, activeTrial=dict(trial, offensiveBuff=None))):
            with self.subTest(row=row), self.assertRaises(ValueError):
                jewelry.validate_row(280071, row)
