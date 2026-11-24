"""Native weapon controls used to assign AoE recommendation points."""
import copy
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import simulate_aoe_weapon_priority as generator
import aoe_ranged


def equipment(**slots):
    return {"items": [slots.get(slot, {}) for slot in generator.pack.EQUIPMENT_SLOTS]}


def pack_result(n, damage_per_pack, player):
    return {"iterationsDone": n, "avgIterationDuration": 15,
            "raidMetrics": {"parties": [{"players": [player]}], "dps": {"allValues": [damage_per_pack / 15] * n}},
            "encounterMetrics": {"targets": [{"unitIndex": i} for i in (2, 3, 4, 5)]}}


def native_items(root, ids):
    return {item["id"]: item for name in ("leftover_db.json", "db.json")
            for item in generator.pack.read(root / "assets/database" / name)["items"] if item["id"] in ids}


def native_profile(root, cli, slug):
    pack = generator.pack
    profile = pack.read(pack.PROFILES / (slug + ".json"))
    path = pack.PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile else root / profile["rotation"]
    return profile, pack.read_preset(root, cli, path), pack.reference_equipment(root, cli, profile)


def weapon(item_id):
    return {
        "id": item_id, "name": "Test weapon", "type": 13, "weaponType": 2, "handType": 2,
        "weaponSpeed": 2.0, "qualityModifier": 1.5, "spellSchool": 4,
        "setId": 41, "setName": "Test set", "itemEffects": [{"buffId": 7, "onUse": {}}],
        "pseudoStats": {"1": 17},
        "scalingOptions": {
            "0": {"weaponDamageMin": 20, "weaponDamageMax": 60, "unroundedDps": 25, "ilvl": 55,
                  "stats": {"3": 8}, "areaStats": [{"stats": {"1": 40}}],
                  "mobTypeStats": [{"stats": {"1": 75}}], "weaponSkills": [{"value": 5}]},
            "1": {"weaponDamageMin": 10, "weaponDamageMax": 30, "stats": {"3": 4}},
        },
    }


class WeaponPriorityGeneratorTest(unittest.TestCase):
    def test_neutral_copy_preserves_both_damage_tables_and_removes_all_bonuses(self):
        source = weapon(101)
        gear = equipment(main={"id": 101}, off={"id": 101}, ranged={"id": 47, "enchant": 87})
        player = {"equipment": gear, "database": {"items": [{"id": 42}], "enchants": [{"effectId": 87}]},
                  "rotation": {"priorityList": []}, "bonusStats": {"stats": [13]}}
        request = {"raid": {"parties": [{"players": [player]}]}, "simOptions": {"randomSeed": "8"}}
        old_request, old_source = copy.deepcopy(request), copy.deepcopy(source)
        neutral = generator.neutral_request(request, ("main", "off"), {101: source})
        control = neutral["raid"]["parties"][0]["players"][0]
        self.assertEqual(request, old_request)
        self.assertEqual(source, old_source)
        clone_id = generator.CLONE_OFFSET + 101
        self.assertEqual(control["equipment"], equipment(main={"id": clone_id}, off={"id": clone_id},
                                                         ranged={"id": 47, "enchant": 87}))
        keep, clone = control["database"]["items"]
        self.assertEqual(keep, {"id": 42})
        self.assertEqual(control["database"]["enchants"], player["database"]["enchants"])
        self.assertEqual(control["rotation"], player["rotation"])
        self.assertEqual(control["bonusStats"], player["bonusStats"])
        self.assertEqual(neutral["simOptions"], request["simOptions"])
        self.assertEqual(clone["id"], clone_id)
        for field in ("type", "weaponType", "handType", "weaponSpeed", "qualityModifier", "spellSchool"):
            self.assertEqual(clone[field], source[field])
        self.assertEqual(clone["scalingOptions"], {
            "0": {"weaponDamageMin": 20, "weaponDamageMax": 60, "unroundedDps": 25, "ilvl": 55},
            "1": {"weaponDamageMin": 10, "weaponDamageMax": 30},
        })
        self.assertFalse({"itemEffects", "pseudoStats", "setId", "setName"}.intersection(clone))

    def test_two_hander_has_no_offhand_clone_and_a_duplicate_id_errors(self):
        item_id = 101
        clone_id = generator.CLONE_OFFSET + item_id
        player = {"equipment": equipment(main={"id": item_id})}
        request = {"raid": {"parties": [{"players": [player]}]}}
        items = {item_id: weapon(item_id)}
        control = generator.neutral_request(request, ("main", "off"), items)["raid"]["parties"][0]["players"][0]
        self.assertEqual(len(control["database"]["items"]), 1)
        self.assertEqual(control["equipment"], equipment(main={"id": clone_id}))
        with self.assertRaisesRegex(ValueError, "collides"):
            generator.neutral_request(request, ("main",), {**items, clone_id: {}})
        player["database"] = {"items": [{"id": clone_id}]}
        with self.assertRaisesRegex(ValueError, "collides"):
            generator.neutral_request(request, ("main",), items)

    def test_only_landed_player_weapon_attacks_contribute_base_damage(self):
        def action(key, damage):
            return {"id": key, "targets": [{"damage": damage, "casts": 3}]}

        physical = {"otherId": "OtherActionAttack"}
        unit = {"actions": [action(dict(physical, tag=14), 0), action(dict(physical, tag=15), 30),
                            action(dict(physical, tag=15494), 25), action({"spellId": 2643}, 200),
                            action({"spellId": 5019}, 0)],
                "pets": [{"actions": [action(dict(physical, tag=14), 150)]}]}
        self.assertEqual(generator.damaging_attacks(unit), {"off"})
        for shot in ({"otherId": "OtherActionShoot"}, {"spellId": 5019, "tag": 1}):
            with self.subTest(shot=shot):
                self.assertEqual(generator.damaging_attacks({"actions": [action(shot, 7)]}), {"ranged"})
        self.assertEqual(generator.damaging_attacks({"actions": [action(dict(physical, tag=14), 10)]}), {"main"})

    def test_actual_hand_damage_talents_feral_scaling_and_wand(self):
        item = weapon(101)
        items = {101: item}
        pair = {"main": 101, "off": 101}
        for cls, talents, off_factor in (("ROGUE", "", .5), ("ROGUE", "-" + "0" * 14 + "2", .75),
                                        ("WARRIOR", "-" + "0" * 8 + "5", .625)):
            with self.subTest(cls=cls, talents=talents):
                profile = {"class": cls, "spec": 2, "player": {"talentsString": talents}}
                self.assertEqual(generator.base_dps(profile, items, pair, {"main", "off"}), 20 + 20 * off_factor)
                self.assertEqual(generator.base_dps(profile, items, pair, {"off"}), 20 * off_factor)
        self.assertEqual(generator.base_dps({"class": "DRUID", "spec": 4}, items, {"main": 101}, {"main"}), 25)
        hunter = {"class": "HUNTER", "spec": 3}
        self.assertEqual(generator.base_dps(hunter, items, pair, {"ranged"}), 0)
        self.assertEqual(generator.base_dps(hunter, items, {"ranged": 101}, {"ranged"}), 20)
        priest = {"class": "PRIEST", "spec": 3}
        wand = {101: dict(item, type=14, rangedWeaponType=5)}
        self.assertEqual(generator.base_dps(priest, wand, {"ranged": 101}, set()), 0)
        self.assertEqual(generator.base_dps(priest, wand, {"ranged": 101}, {"ranged"}), 20)

    def test_rotation_damage_keeps_other_slots_techniques_extra_attacks_and_pets(self):
        n = 2

        def action(ident, damage):
            return {"id": ident, "targets": [{"unitIndex": 2, "damage": damage * n / 2},
                                             {"unitIndex": 5, "damage": damage * n / 2},
                                             {"unitIndex": 99, "damage": 1000}]}

        white = {"otherId": "OtherActionAttack"}
        shoot = {"otherId": "OtherActionShoot"}
        player = {"actions": [action(dict(white, tag=14), 100), action(dict(white, tag=15), 60),
                              action(dict(white, tag=13960), 20), action(shoot, 30), action({"spellId": 5019}, 40),
                              action({"spellId": 11294}, 70), action({"spellId": 22482}, 50)],
                  "pets": [{"name": "Raptor", "actions": [action(dict(white, tag=14), 80), action(shoot, 10)]}]}
        result = pack_result(n, 460, player)
        expected = {(): 460, ("main",): 360, ("off",): 400, ("main", "off"): 300, ("ranged",): 390}
        for slots, damage in expected.items():
            with self.subTest(slots=slots):
                self.assertEqual(generator.rotation_damage(result, slots, n, "Raptor"), damage)

    def test_rotation_gain_and_standard_error_follow_paired_blocks_for_each_equipment_scope(self):
        profile = {"class": "HUNTER", "spec": 1, "player": {}, "races": {"h": "RaceOrc"},
                   "referenceWeapons": [101, 102], "comparisonItems": {"ranged": 105}}
        gear = equipment(main={"id": 101}, off={"id": 102}, ranged={"id": 103}, head={"id": 107, "enchant": 87})
        rotation = {"priorityList": []}
        items = {i: weapon(i) for i in range(101, 107)}
        record = {"sets": [{"main": 101, "off": 102}, {"main": 104, "off": 102}],
                  "ranged": [{"id": 105}, {"id": 106}]}
        requests = {}
        n = generator.ROTATION_BLOCK_SIZE
        first_seed = generator.priority.SEED
        seeds = [first_seed + block * n for block in range(8)]

        def simulate(req):
            config = req["simOptions"]
            self.assertEqual(config["iterations"], n)
            seed = int(config["randomSeed"])
            block = seeds.index(seed)
            player = req["raid"]["parties"][0]["players"][0]
            self.assertEqual(player["race"], "RaceOrc")
            slots = dict(zip(generator.pack.EQUIPMENT_SLOTS, player["equipment"]["items"], strict=True))
            self.assertEqual(slots["head"], {"id": 107, "enchant": 87})
            offset = generator.CLONE_OFFSET
            main, off, ranged = (slots[slot]["id"] for slot in ("main", "off", "ranged"))
            if ranged > offset:
                self.assertEqual((main, off), (101, 102))
                self.assertIn(ranged - offset, (105, 106))
                key = ("ranged", ranged - offset)
                delta = 2 * block - 10 if ranged == offset + 106 else 0
            else:
                self.assertEqual((off, ranged), (offset + 102, 103))
                self.assertIn(main - offset, (101, 104))
                key = ("main", main - offset)
                delta = 10 + block if main == offset + 104 else 0
            requests.setdefault(key, []).append(seed)
            # This large variation between seeds cancels only with correct pairing.
            damage = 100 + 500 * (block % 2) + delta
            spell = {"id": {"spellId": 2643}, "targets": [{"unitIndex": 3, "damage": n * damage}]}
            return pack_result(n, damage, {"actions": [spell]})

        generator.add_rotation_measurements(profile, "h", rotation, gear, items, record, simulate)
        expected_configs = (("main", 101), ("main", 104), ("ranged", 105), ("ranged", 106))
        self.assertEqual(requests, {key: seeds for key in expected_configs})
        for row in (record["sets"][0], record["ranged"][0]):
            self.assertEqual((row["rotationGain"], row["rotationSE"]), (0, 0))
        self.assertEqual(record["sets"][1]["rotationGain"], 13.5)
        self.assertAlmostEqual(record["sets"][1]["rotationSE"], math.sqrt(6 / 8))
        self.assertEqual(record["ranged"][1]["rotationGain"], -3)
        self.assertAlmostEqual(record["ranged"][1]["rotationSE"], 2 * math.sqrt(6 / 8))

    def test_faction_measures_paired_weapon_bonus_and_independent_stat_control(self):
        profile = {"class": "HUNTER", "spec": 1, "player": {}, "races": {"a": "RaceDwarf"},
                   "referenceWeapons": [101, 0], "weaponSets": [[101, 0]], "slots": {"ranged": [102]}}
        items = {101: weapon(101), 102: dict(weapon(102), type=14, rangedWeaponType=1)}
        gear = equipment(main={"id": 101}, ranged={"id": 102})
        rotation = {"priorityList": [{"action": {"autocastOtherCooldowns": {}}}]}
        requests = []
        rap_index = generator.pack.eligibility.STAT_IDS["rap"][0]

        def simulate(req):
            requests.append(copy.deepcopy(req))
            player = req["raid"]["parties"][0]["players"][0]
            equipped = {w.get("id") for w in player["equipment"]["items"]}
            bonus = player.get("bonusStats", {}).get("stats", [])
            damage = 100 + 5 * (101 in equipped) + 8 * (102 in equipped)
            if len(bonus) > rap_index:
                damage += bonus[rap_index] / 2
            n = req["simOptions"]["iterations"]
            shot = {"id": {"otherId": "OtherActionShoot"}, "targets": [{"unitIndex": 3, "damage": damage * n}]}
            return pack_result(n, damage, {"actions": [shot]})

        with patch.object(generator.priority, "ITERATIONS", 4):
            result = generator.measure_faction(profile, "a", rotation, gear, items, simulate)
            generator.add_rotation_measurements(profile, "a", rotation, gear, items, result, simulate)
        self.assertEqual(result, {"pointStat": "rap", "controlGain": 50, "controlSE": 0,
                                  "sets": [{"main": 101, "off": 0, "baseDps": 0, "gain": 5, "se": 0,
                                            "rotationGain": 0, "rotationSE": 0}],
                                  "ranged": [{"id": 102, "baseDps": 20, "gain": 8, "se": 0,
                                              "rotationGain": 0, "rotationSE": 0}]})
        self.assertEqual(len(requests), 6 + 2 * generator.ROTATION_BLOCKS)
        for req in requests[:6]:
            self.assertEqual(req["simOptions"]["randomSeed"], str(generator.priority.SEED))
            self.assertEqual(req["simOptions"]["iterations"], 4)
        for req in requests:
            self.assertEqual(req["raid"]["parties"][0]["players"][0]["race"], "RaceDwarf")
        for inactive, item_id in ((requests[2], 101), (requests[4], 102)):
            entries = inactive["raid"]["parties"][0]["players"][0]["rotation"]["priorityList"]
            first = entries[0]["action"]
            self.assertEqual(first["castSpell"]["spellId"], {"itemId": item_id})
            self.assertEqual(first["condition"], {"const": {"val": "false"}})

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "native pack CLI required")
    def test_native_clone_preserves_bare_bow_shots_and_removes_ironfoe_extra_attacks(self):
        pack = generator.pack
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_PACK_CLI"])
        items = native_items(root, {2506, 11684})
        client = pack.fdb.load(pack.HERE / "cache" / "ForeverDB")
        aoe_ranged.validate_native({"class": "HUNTER"}, items[2506], client.gear[2506])
        generator.weapons._check_weapon_damage(items[11684], client.gear[11684])
        self.assertFalse(items[2506].get("itemEffects"))
        self.assertFalse(items[2506]["scalingOptions"]["0"].get("stats"))
        self.assertIn(15494, [effect["buffId"] for effect in items[11684]["itemEffects"]])
        n = 256
        for slug, slot in (("hunter-survival", "ranged"), ("warrior-fury", "main")):
            p, rotation, gear = native_profile(root, cli, slug)
            race = p["races"]["a"]
            if slot == "ranged":
                request = pack.make_request(p, race, rotation, gear, slot, 2506, n)
            else:
                request = generator.weapons.request(p, race, rotation, gear, (11684, 10847), n)
            with self.subTest(profile=slug), tempfile.TemporaryDirectory() as directory:
                real, bare = [pack.run_request(cli, Path(directory), trial)
                              for trial in (request, generator.neutral_request(request, (slot,), items))]
                players = [r["raidMetrics"]["parties"][0]["players"][0] for r in (real, bare)]
                for player in players:
                    self.assertIn(slot, generator.damaging_attacks(player))
                if slot == "ranged":
                    samples = [pack.samples(r, n, p["damageChecks"], p.get("requiredPet"))[0] for r in (real, bare)]
                    self.assertEqual(*samples)
                else:
                    extra_swings = [sum(t["damage"] for a in player["actions"]
                                        if a["id"].get("otherId") == "OtherActionAttack" and a["id"].get("tag") == 15494
                                        for t in a["targets"]) for player in players]
                    self.assertGreater(extra_swings[0], 0)
                    self.assertEqual(extra_swings[1], 0)

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "native pack CLI required")
    def test_bare_main_hands_change_fury_and_combat_rotation_damage_with_the_same_offhand(self):
        root, cli = Path(os.environ["EASYBIS_WOWSIMS"]), Path(os.environ["EASYBIS_PACK_CLI"])
        felstriker = 12590
        cases = (("warrior-fury", 22384, 10847), ("rogue-combat", 279259, 279261))
        items = native_items(root, {felstriker, 22384, 10847, 279259, 279261})
        for slug, alternative, offhand in cases:
            with self.subTest(profile=slug), tempfile.TemporaryDirectory() as directory:
                profile, rotation, gear = native_profile(root, cli, slug)
                profile["referenceWeapons"] = [felstriker, offhand]
                record = {"sets": [{"main": felstriker, "off": offhand}, {"main": alternative, "off": offhand}],
                          "ranged": []}

                def simulate(request):
                    return generator.pack.run_request(cli, Path(directory), request)

                generator.add_rotation_measurements(profile, "a", rotation, gear, items, record, simulate)
                ref, changed = record["sets"]
                self.assertEqual((ref["rotationGain"], ref["rotationSE"]), (0, 0))
                self.assertGreater(changed["rotationSE"], 0)
                self.assertGreater(changed["rotationGain"], 3 * changed["rotationSE"])


if __name__ == "__main__":
    unittest.main()
