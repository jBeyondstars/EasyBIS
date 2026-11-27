"""Offline checks for the dungeon-pull campaign, its packaged scores and the Items tab."""
import copy
import hashlib
import sys
import unittest
from functools import cache
from pathlib import Path
from unittest.mock import patch

TESTS = Path(__file__).resolve().parent
BUILD = TESTS.parent
sys.path[:0] = [str(BUILD), str(TESTS)]

import fdb
import aoe_combined
import aoe_eligibility as rules
import aoe_weapon_priority
import ladders
import luaout
import simulate_aoe as aoe
from test_addon import Game, lupa
from test_ui import find, open_dropdown, texts


@cache
def combined_rankings():
    short = aoe.read(BUILD / "corrections" / "aoe.json")
    route = aoe.read(BUILD / "corrections" / "aoe_dungeon.json")
    return aoe_combined.rankings(short, route)


class AoeTest(unittest.TestCase):
    def assert_scores(self, displayed, expected):
        self.assertEqual([i for i, _ in displayed], [r["id"] for r in expected])
        for (_, score), row in zip(displayed, expected):
            self.assertAlmostEqual(score, row["score"], places=9)

    def assert_aoe_tooltip(self, game, lines, block, item):
        fmt = game.lua.globals().string.format
        rank = game.ns.L.RANK_BIS if item["id"] == block["items"][0]["id"] else game.ns.L.RANK_ALT
        self.assertTrue(any(rank in line and "AoE/Dung" in line for line in lines), lines)
        def number(style, value):
            text = fmt(style, value)
            return text.replace(".", ",") if game.ns.locale == "frFR" else text
        for label, prefix in (("AOE_SHORT_RESULT", "short"), ("AOE_ROUTE_RESULT", "route")):
            gain = item[prefix + "Gain"]
            self.assertNotIn(fmt(game.ns.L[label], number("%+.1f", gain),
                              number("%+.2f", 100 * gain / block[prefix + "Baseline"]), item[prefix + "Rank"]), lines)
        deltas = [number("%+.0f", n - b) for n, b in zip(item["routePackDamage"], block["routeBaselinePackDamage"])]
        self.assertNotIn(fmt(game.ns.L.AOE_ROUTE_PACKS, *deltas), lines)
        self.assertNotIn(fmt(game.ns.L.AOE_ERROR, number("%.2f", item["scoreSE"])), lines)

    def test_native_preflight_checks_the_specializations_offensive_stats(self):
        gear = {"items": [{} for _ in range(17)]}
        examples = [
            ("hunter-beast-mastery", 18317, "neck", {3: 6, 4: 7, 5: 2, 13: 6, 18: 14}, False),
            ("hunter-beast-mastery", 18496, "back", {3: 10, 18: 14}, False),
            ("hunter-beast-mastery", 279269, "back", {11: 15, 18: 14}, False),
            ("hunter-beast-mastery", 279257, "hands", {1: 21, 3: 14}, True),
            ("hunter-beast-mastery", 21278, "hands", {17: 10, 18: 14}, True),
            ("mage-frost", 18408, "hands", {3: 9, 7: 33}, False),
            ("mage-frost", 18510, "back", {3: 10, 4: 42, 5: 14}, False),
            ("mage-frost", 12968, "back", {3: 13, 8: 13, 34: 10}, True),
            ("mage-fire", 18408, "hands", {3: 9, 7: 33}, True),
            ("mage-fire", 12968, "back", {3: 13, 8: 13}, False),
            ("mage-arcane", 254103, "hands", {3: 10, 6: 19, 13: 8}, True),
            ("mage-arcane", 18408, "hands", {3: 9, 7: 33}, False),
            ("rogue-combat", 18317, "neck", {3: 6, 4: 7, 5: 2, 13: 6, 18: 14}, False),
            ("rogue-combat", 226828, "hands", {0: 9, 1: 22, 13: 8}, True),
            ("warrior-fury", 12929, "neck", {4: 6, 5: 6, 18: 14}, False),
            ("warrior-fury", 12936, "wrist", {13: 7, 17: 10, 18: 14}, True),
            ("warrior-fury", 13212, "neck", {14: 20, 15: 20}, True),
            ("hunter-marksmanship", 18317, "neck", {3: 6, 4: 7, 5: 2, 13: 6, 18: 14}, False),
            ("hunter-survival", 18496, "back", {3: 10, 18: 14}, False),
            ("priest-shadow", 18408, "hands", {3: 9, 7: 33}, False),
            ("druid-restoration", 254103, "hands", {3: 10, 6: 19, 13: 8}, False),
            ("warlock-affliction", 18408, "hands", {3: 9, 7: 33}, True),
        ]
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        for filename, item, slot, stats, allowed in examples:
            with self.subTest(profile=filename, item=item):
                profile = aoe.read(aoe.PROFILES / (filename + ".json"))
                profile["slots"] = {slot: [item]}
                profile.pop("factionReferenceItems", None)  # This fixture equips only the candidate.
                piece = {"type": aoe.ARMOR_SLOTS.index(slot) + 1,
                         "scalingOptions": {"0": {"stats": {str(k): v for k, v in stats.items()}}}}
                if allowed:
                    aoe.validate_equipment(profile, gear, {item: piece}, db.items)
                    rules.validate_candidate(profile, item, rules.client_stats(db.gear[item]["stats"]))
                else:
                    with self.assertRaisesRegex(ValueError, str(item)):
                        aoe.validate_equipment(profile, gear, {item: piece}, db.items)
                    with self.assertRaisesRegex(ValueError, str(item)):
                        rules.validate_candidate(profile, item, rules.client_stats(db.gear[item]["stats"]))
        with self.assertRaisesRegex(ValueError, "missing AOE candidate rules"):
            rules.validate_candidate({"class": "MAGE", "spec": 99}, 18408, {"fire": 33})

    def test_shared_reference_checks_client_faction_on_rings(self):
        profile = aoe.read(aoe.PROFILES / "mage-arcane.json")
        gear = {"items": [{} for _ in range(17)]}
        gear["items"][aoe.EQUIPMENT_SLOTS.index("finger2")] = {"id": 12543}
        ring = {"scalingOptions": {"0": {"stats": {"3": 7, "4": 18, "5": 18, "12": 2}}}}
        with self.assertRaisesRegex(ValueError, "faction-restricted item 12543"):
            aoe.validate_equipment(profile, gear, {12543: ring}, {12543: {"side": "a"}})

    def test_reference_trinkets_cannot_share_a_unique_equipped_category(self):
        profile = aoe.read(aoe.PROFILES / "druid-balance.json")
        gear = {"items": [{} for _ in aoe.EQUIPMENT_SLOTS]}
        ids = (272438, 272439)
        for name, item_id in zip(("trinket1", "trinket2"), ids):
            gear["items"][aoe.EQUIPMENT_SLOTS.index(name)] = {"id": item_id}
        with self.assertRaisesRegex(ValueError, "unique-equipped category 707"):
            aoe.validate_equipment(profile, gear, {i: {"id": i, "limitCategory": 707} for i in ids}, {})

    def test_embedded_preset_uses_equipment_and_keeps_the_dungeon_build(self):
        profile = aoe.read(aoe.PROFILES / "shaman-restoration.json")
        source = {"player": {"equipment": {"items": [{} for _ in aoe.EQUIPMENT_SLOTS]},
                             "talentsString": "different upstream build"}}
        with patch.object(aoe, "read_preset", return_value=source):
            gear = aoe.reference_equipment(Path("."), None, profile)
        request = aoe.make_request(profile, profile["races"]["h"], {"priorityList": []}, gear, "back", 0, 2)
        player = request["raid"]["parties"][0]["players"][0]
        self.assertEqual(player["talentsString"], profile["player"]["talentsString"])
        self.assertIn("restorationShaman", player)
        self.assertEqual(player["equipment"]["items"][aoe.EQUIPMENT_SLOTS.index("main")],
                         {"id": profile["referenceItems"]["main"]})

    def test_cannot_compare_another_class_set_gloves(self):
        profile = aoe.read(aoe.PROFILES / "rogue-combat.json")
        profile["slots"] = {"hands": [226883]}
        piece = {"type": 7, "classAllowlist": [3], "scalingOptions": {"0": {"stats": {"1": 14}}}}
        with self.assertRaisesRegex(ValueError, "ROGUE cannot equip"):
            aoe.validate_equipment(profile, {"items": [{} for _ in range(17)]}, {226883: piece}, {})

    def test_blade_flurry_must_damage_a_secondary_target(self):
        targets = [{"unitIndex": i} for i in range(4)]
        strikes = {"id": {"spellId": 11294}, "targets": [{"unitIndex": 0, "damage": 240}]}
        copied_hit = {"id": {"spellId": 22482}, "targets": [{"unitIndex": 0, "damage": 60}]}
        player = {"actions": [strikes, copied_hit]}
        result = {"iterationsDone": 2, "avgIterationDuration": 15, "encounterMetrics": {"targets": targets},
                  "raidMetrics": {"parties": [{"players": [player]}], "dps": {"allValues": [10, 10]}}}
        checks = aoe.read(aoe.PROFILES / "rogue-combat.json")["damageChecks"]
        with self.assertRaisesRegex(ValueError, "22482:secondary"):
            aoe.samples(result, 2, checks)
        copied_hit["targets"][0]["unitIndex"] = 1
        self.assertEqual(aoe.samples(result, 2, checks)[1], {"11294": [1], "22482:secondary": [1]})

    def test_damage_from_helm_activation_is_measured_as_an_item_action(self):
        actions = [{"id": {"spellId": 8348}, "targets": [{"unitIndex": 1, "damage": 40}]},
                   {"id": {"itemId": 8348}, "targets": [{"unitIndex": 2, "damage": 250}]}]
        self.assertEqual(aoe.targets_hit_per_pack(actions, [1], "item:8348"), [0])
        self.assertEqual(aoe.targets_hit_per_pack(actions, [2], "item:8348"), [1])

    def test_publication_rejects_bad_candidates_even_with_positive_dps(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        source = aoe.read(BUILD / "corrections" / "aoe.json")
        bad = copy.deepcopy(source)
        first = bad["specs"]["HUNTER 1"]["factions"]["a"]["neck"]["items"][0]
        first.update(id=18317, gain=1000)
        with self.assertRaisesRegex(ValueError, "measured candidates differ"):
            luaout.aoe_file(db, bad)
        bad = copy.deepcopy(source)
        item = bad["specs"]["HUNTER 1"]["factions"]["a"]["neck"]["items"][0]["id"]
        bad["itemStats"][str(item)]["spell"] = 20
        with self.assertRaisesRegex(ValueError, "differ between WoWSims and ForeverDB"):
            luaout.aoe_file(db, bad)
        db.gear[item]["stats"][42] = 20
        with self.assertRaisesRegex(ValueError, "caster stats"):
            luaout.aoe_file(db, bad)

    def test_publication_rejects_wrong_comparison_even_with_valid_scores(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        slots = archive["specs"]["HUNTER 1"]["factions"]["a"]
        for slot, field, error in (("finger", "pairedItem", "fixed companion"),
                                   ("ranged", "comparisonItem", "comparison item")):
            original = slots[slot][field]
            slots[slot][field] = 1
            with self.subTest(slot=slot), self.assertRaisesRegex(ValueError, error):
                luaout.aoe_file(db, archive)
            slots[slot][field] = original
        archive["specs"]["PRIEST 1"] = archive["specs"]["PRIEST 3"]
        with self.assertRaisesRegex(ValueError, "specializations"):
            luaout.aoe_file(db, archive)

    def test_scaling_controls_reject_canceling_changes_between_iterations(self):
        profile = aoe.read(aoe.PROFILES / "hunter-beast-mastery.json")
        targets = [{"unitIndex": i} for i in range(4)]
        actions = [{"id": {"spellId": int(spell)}, "targets": [dict(t, damage=1) for t in targets]}
                   for spell in profile["damageChecks"]]
        player = {"actions": actions, "pets": [{"name": "Raptor", "actions": actions}]}

        def run(exe, work, request):
            stats = request["raid"]["parties"][0]["players"][0].get("bonusStats", {}).get("stats", [])
            values = [50, 50]
            if len(stats) > 15 and stats[15]:
                values = [60, 60]
            if len(stats) > 5 and stats[5]:
                values = [49, 51]
            # The same two damage actions are present on both the hunter and the pet.
            for action in actions:
                for target in action["targets"]:
                    target["damage"] = sum(values) * 15 / (2 * len(actions) * len(targets))
            return {"iterationsDone": 2, "avgIterationDuration": 15, "encounterMetrics": {"targets": targets},
                    "raidMetrics": {"parties": [{"players": [player]}], "dps": {"allValues": values}}}

        with patch.object(aoe, "run_request", side_effect=run):
            with self.assertRaisesRegex(ValueError, "unexpected scaling with .* spell"):
                aoe.scaling_controls(None, None, profile, "RaceDwarf", {"priorityList": []},
                                     {"items": [{} for _ in range(17)]}, 2)

    def test_publication_requires_scaling_controls_and_item_effect_evidence(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        bad = copy.deepcopy(archive)
        bad["specs"]["HUNTER 1"]["scalingControls"]["h"]["stats"]["spell"]["gain"] = 0.5
        with self.assertRaisesRegex(ValueError, "invalid scaling control"):
            luaout.aoe_file(db, bad)
        for spec, slot, item in (("MAGE 1", "back", 14134), ("MAGE 2", "back", 14134),
                                ("MAGE 3", "back", 14134), ("WARRIOR 2", "hands", 18383)):
            with self.subTest(spec=spec):
                bad = copy.deepcopy(archive)
                row = next(r for r in bad["specs"][spec]["factions"]["h"][slot]["items"] if r["id"] == item)
                row.pop("targetsHitPerPack")
                with self.assertRaisesRegex(ValueError, "missing item damage"):
                    luaout.aoe_file(db, bad)
        archive["specs"]["MAGE 3"]["profileSha256"] = "obsolete"
        with self.assertRaisesRegex(ValueError, "stale profile"):
            luaout.aoe_file(db, archive)

    def test_healing_gloves_leave_the_damage_rotation_available(self):
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        for key in ("DRUID 1", "SHAMAN 1"):
            for slots in archive["specs"][key]["factions"].values():
                hands = slots["hands"]
                gloves = next(item for item in hands["items"] if item["id"] == 8346)
                self.assertEqual(gloves["usesPerRun"], 0)
                self.assertGreater(gloves["gain"], 3 * gloves["se"])
        gloves["usesPerRun"] = 1
        with self.assertRaisesRegex(ValueError, "utility activation"):
            luaout.aoe_file(fdb.load(BUILD / "cache" / "ForeverDB"), archive)

    def test_armor_level_and_profession_match_the_character(self):
        profile = aoe.read(aoe.PROFILES / "mage-frost.json")
        profile["slots"] = {"head": [123]}
        piece = {"type": 1, "armorType": 1, "reqLvl": 60, "requiredProfession": 11,
                 "scalingOptions": {"0": {"stats": {"8": 12}}}}
        gear = {"items": [{} for _ in aoe.EQUIPMENT_SLOTS]}
        aoe.validate_equipment(profile, gear, {123: piece}, {})
        for change in ({"armorType": 2}, {"reqLvl": 61}, {"requiredProfession": 2}):
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, "cannot equip"):
                aoe.validate_equipment(profile, gear, {123: {**piece, **change}}, {})

    def test_robe_waits_for_missing_mana_even_with_an_explicit_cast_in_the_preset(self):
        profile = aoe.read(aoe.PROFILES / "mage-fire.json")
        cast = {"action": {"castSpell": {"spellId": {"itemId": 14152}}}}
        rotation = {"priorityList": [cast], "groups": [{"name": "Mana", "actions": [cast]}]}
        gear = {"items": [{} for _ in aoe.EQUIPMENT_SLOTS]}
        for passive in (False, True):
            req = aoe.make_request(profile, profile["races"]["a"], rotation, gear, "chest", 14152, 2, True, passive)
            apl = req["raid"]["parties"][0]["players"][0]["rotation"]
            self.assertEqual(len(apl["priorityList"]), 1)
            self.assertEqual(apl["groups"][0]["actions"], [])
            condition = apl["priorityList"][0]["action"]["condition"]
            if passive:
                self.assertEqual(condition, {"const": {"val": "false"}})
            else:
                self.assertEqual(condition["cmp"]["lhs"], {"currentManaPercent": {}})
        self.assertEqual(rotation["groups"][0]["actions"], [cast])

    def test_pack_and_gear_swap(self):
        profile = aoe.read(aoe.PROFILES / "mage-frost.json")
        gear = {"items": [{"id": 25, "enchant": 3} for _ in range(17)]}
        blizzard = {"action": {"castSpell": {"spellId": {"spellId": 10187}}}}
        rotation = {"prepullActions": [{}], "priorityList": [], "groups": [{"name": "AOE", "actions": [blizzard]}]}
        for item in (0, 14134):
            request = aoe.make_request(profile, "RaceTroll", rotation, gear, "back", item, 30, on_use=bool(item))
            targets = request["encounter"]["targets"]
            self.assertEqual(len(targets), 4)
            self.assertEqual(request["encounter"]["duration"], 15)
            self.assertEqual({t["level"] for t in targets}, {60})
            for target in targets:
                self.assertFalse(target.get("disabledAtStart"))
                self.assertEqual([x["numberValue"] for x in target["targetInputs"]], [0, 15])
            player = request["raid"]["parties"][0]["players"][0]
            worn = player["equipment"]["items"]
            self.assertEqual(worn[:3] + worn[4:], gear["items"][:3] + gear["items"][4:])
            self.assertEqual(worn[3], {"id": item} if item else {})
            self.assertNotIn("prepullActions", player["rotation"])
            priorities = player["rotation"]["priorityList"]
            self.assertEqual(len(priorities), int(bool(item)))
            if item:
                self.assertEqual(priorities[0]["action"]["castSpell"]["spellId"]["itemId"], item)
            finisher, channel = player["rotation"]["groups"][0]["actions"]
            self.assertEqual(channel, blizzard)
            self.assertEqual(finisher["action"]["castSpell"]["spellId"]["spellId"], 10202)
            condition = finisher["action"]["condition"]["cmp"]
            self.assertEqual(condition["lhs"]["timeUntilTargetDies"]["targetUnit"]["type"], "CurrentTarget")
            self.assertEqual((condition["op"], condition["rhs"]["const"]["val"]), ("OpLe", "6s"))
        self.assertEqual(gear["items"][3]["id"], 25)
        self.assertIn("prepullActions", rotation)
        self.assertEqual(rotation["groups"][0]["actions"], [blizzard])

    def test_rejects_single_target_damage_in_a_pack(self):
        targets = [{"unitIndex": i} for i in range(4)]
        action = {"id": {"spellId": 42}, "targets": [{"unitIndex": 0, "damage": 3}]}
        result = {"iterationsDone": 2, "avgIterationDuration": 15, "encounterMetrics": {"targets": targets},
                  "raidMetrics": {"parties": [{"players": [{"actions": [action]}]}], "dps": {"allValues": [5, 6]}}}
        with self.assertRaisesRegex(ValueError, "did not damage"):
            aoe.samples(result, 2, {"42": 4})
        action["targets"] = [dict(t, damage=41.25) for t in targets]
        self.assertEqual(aoe.samples(result, 2, {"42": 4}), ([75, 90], {"42": [4]}))
        action["targets"][0]["damage"] -= 10
        with self.assertRaisesRegex(ValueError, "Pack damage does not match"):
            aoe.samples(result, 2, {"42": 4})
        with self.assertRaisesRegex(ValueError, "Raptor"):
            aoe.samples(result, 2, {"42": 4}, "Raptor")
        self.assertEqual(aoe.difference([5, 6], [3, 4]), (2, 0))
        with self.assertRaises(ValueError):
            aoe.samples(result, 3, {"42": 4})
        result["avgIterationDuration"] = 110
        with self.assertRaisesRegex(ValueError, "15-second"):
            aoe.samples(result, 2, {"42": 4})

    def test_paired_slots_keep_the_companion_and_hunter_keeps_a_functional_reference(self):
        profile = aoe.read(aoe.PROFILES / "hunter-marksmanship.json")
        gear = {"items": [{"id": 100 + n} for n in range(len(aoe.EQUIPMENT_SLOTS))]}
        for slot, index in (("finger", 10), ("trinket", 12), ("ranged", 16)):
            for candidate in (0, 999):
                request = aoe.make_request(profile, profile["races"]["h"], {"priorityList": []},
                                           gear, slot, candidate, 2)
                equipped = request["raid"]["parties"][0]["players"][0]["equipment"]["items"]
                expected = list(gear["items"])
                item_id = candidate or profile.get("comparisonItems", {}).get(slot)
                expected[index] = {"id": item_id} if item_id else {}
                self.assertEqual(equipped, expected)
                if slot == "ranged":
                    self.assertGreater(equipped[index]["id"], 0)

    def test_rejects_route_or_dps_archive(self):
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        route = copy.deepcopy(archive)
        route["schedule"].update(packs=3, seconds=30, travel=10)
        with self.assertRaisesRegex(ValueError, "single pack"):
            luaout.aoe_file(None, route)
        archive.pop("metric")
        with self.assertRaisesRegex(ValueError, "total damage"):
            luaout.aoe_file(None, archive)

    def test_hunter_spends_mana_on_this_pack(self):
        profile = aoe.read(aoe.PROFILES / "hunter-beast-mastery.json")
        rotation = aoe.read(aoe.PROFILES / profile["dungeonRotation"])
        spend = next(row["action"] for row in rotation["priorityList"]
                     if row["action"].get("groupReference", {}).get("groupName") == "Spend mana")
        self.assertNotIn("condition", spend)

    def test_package_matches_measurements_and_has_sources(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        self.assertEqual(archive["encounter"], aoe.encounter())
        ai_source = (aoe.PROFILES / "dungeon_target.go").read_text(encoding="utf-8")
        self.assertEqual(archive["encounterAiSha256"], hashlib.sha256(ai_source.encode()).hexdigest())
        route = aoe.read(BUILD / "corrections" / "aoe_dungeon.json")
        rendered, used = luaout.combined_aoe_file(db, archive, route)
        self.assertEqual((BUILD.parent / "Data" / "Aoe.lua").read_text(encoding="utf-8"), rendered)
        packaged = (BUILD.parent / "Data" / "Items.lua").read_text(encoding="utf-8")
        generated = luaout.items_file(db, {}, used)
        for item in used:
            self.assertIn(f"\n{item}|", packaged)
            self.assertIn(f"\n{item}|", generated)
        definitions = (aoe.read(path) for path in aoe.PROFILES.glob("*.json"))
        profiles = [p for p in definitions if db.classes[p["class"]]["specs"][p["spec"]]["role"].endswith(" DPS")]
        self.assertEqual(set(archive["specs"]), {f"{p['class']} {p['spec']}" for p in profiles})
        self.assertEqual(set(archive["specs"]), rules.ranked_specs(db))
        for p in profiles:
            record = archive["specs"][f"{p['class']} {p['spec']}"]
            self.assertEqual(set(record["factions"]), {"a", "h"})
            self.assertTrue({*aoe.ARMOR_SLOTS, "finger", "trinket", "ranged", "main"} <= set(p["slots"]))
            self.assertEqual("off" in p["slots"], any(off for _, off in p["weaponSets"]))
            if (p["class"], p["spec"]) == ("ROGUE", 1):
                # Mutilate strikes the same target with both daggers. The native weapon test checks both hits.
                self.assertEqual(p["damageChecks"]["1241584"], 1)
            else:
                self.assertTrue(any(n > 1 or spell.endswith(":secondary") for spell, n in p["damageChecks"].items()))
            if p["class"] == "HUNTER":
                for control in record["scalingControls"].values():
                    self.assertEqual(control["stats"]["spell"], {"gain": 0, "se": 0})
            for side, slots in record["factions"].items():
                self.assertEqual(set(slots), set(p["slots"]))
                short_pairs = {}
                for hand in ("main", "off"):
                    for row in slots.get(hand, {}).get("items", []):
                        pair = (row["id"], row["partner"]) if hand == "main" else (row["partner"], row["id"])
                        short_pairs[pair] = row
                mixed = combined_rankings()[f"{p['class']} {p['spec']}"][side]
                for hand in ("main", "off"):
                    for row in mixed.get(hand, {}).get("items", []):
                        pair = (row["id"], row["partner"]) if hand == "main" else (row["partner"], row["id"])
                        if pair in short_pairs:
                            self.assertEqual(dict(row["shortSchools"]), short_pairs[pair]["schoolPct"])
                        else:
                            self.assertFalse({"shortSchools", "shortUses", "shortPetPct", "shortActivated"} & row.keys())
                for slot, result in slots.items():
                    rows = result["items"]
                    self.assertCountEqual([x["id"] for x in rows if x["id"] not in luaout.ladders.DISQUALIFIED_ITEMS],
                                          p["slots"][slot])
                    self.assertEqual(rows, sorted(rows, key=lambda x: -x["gain"]))
                    hits = result["baselineTargetsHitPerPack"]
                    for spell, minimum in p["damageChecks"].items():
                        self.assertEqual(len(hits[spell]), 1)
                        self.assertGreaterEqual(min(hits[spell]), minimum)
                    if "requiredPet" in p:
                        self.assertGreater(min(hits[p["requiredPet"]]), 0)
                        self.assertTrue(all(0 < x["petPct"] < 100 for x in rows))
        for faction in archive["specs"]["MAGE 3"]["factions"].values():
            rows = faction["back"]["items"]
            shares = faction["back"]["baselineSchoolPct"]
            self.assertEqual(set(shares), {"frost", "arcane"})
            self.assertTrue(all(pct > 0 for pct in shares.values()))
            cloak = next(row for row in rows if row["id"] == 14134)
            self.assertEqual(cloak["usesPerRun"], 1)
            self.assertEqual((cloak["passiveGain"], cloak["passiveSE"]), (0, 0))
            self.assertEqual(cloak["targetsHitPerPack"]["18374"], [4])
            self.assertGreater(cloak["schoolPct"]["fire"], 0)
            self.assertGreater(cloak["schoolPct"]["frost"] + cloak["schoolPct"]["arcane"], 90)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_items_toggle_faction_filters_and_saved_choice(self):
        game = Game(locale="frFR", cls="MAGE", saved="EasyBISCharDB = { class = 'MAGE', spec = 3 }")
        ns = game.ns
        ns.Browser.Open()
        window = ns.Browser.window
        def gains():
            return [(row.id, row.gain) for row in window.rowData.values() if row.gain is not None]
        def click(button):
            game.stub.run(button, "OnClick")
        self.assertEqual(gains(), [])
        self.assertEqual([b.Text.text for b in window.list.buttons.values()], ["PvE", "PvP"])
        self.assertEqual([b.Text.text for b in window.scenario.buttons.values()], ["Raid", "AoE / Dungeons"])
        self.assertTrue(window.scenario.buttons[1].highlightLocked)
        self.assertIsNone(window.scenario.summary)
        raid_titles = {r.group: r.text for r in window.rowData.values() if r.kind == "header"}
        click(window.scenario.buttons[2])
        self.assertIsNone(window.scenario.summary)
        expected = combined_rankings()["MAGE 3"]
        for side, command in (("a", "alliance"), ("h", "horde")):
            game.slash("faction " + command)
            expected_rows = [r for slot in (*aoe.ARMOR_SLOTS, "finger", "trinket", "main", "off", "ranged")
                             if slot in expected[side] for r in expected[side][slot]["items"][:3]]
            self.assert_scores(gains(), expected_rows)
            titles = {r.group: r.text for r in window.rowData.values() if r.kind == "header"}
            self.assertEqual(titles, {slot: ns.SlotName(slot) for slot in expected[side]})
            self.assertEqual(titles["head"], raid_titles["head"])
            self.assertEqual(titles["neck"], raid_titles["neck"])
        info = ns.Browser.ScoreInfo("MAGE", 3, "aoe")
        self.assertIn("15", info[2])
        self.assertEqual(info[3], ns.L.AOE_ROUTE_FIGHT)
        self.assertEqual(info[4], game.lua.globals().string.format(ns.L.AOE_ROUTE_GROUP, 7500, 2500, 1500)
                         + " " + ns.L.AOE_ROUTE_MANA)
        self.assertIn("100 % de mana", info[4])
        self.assertFalse(window.rows[1].info.shown)
        labels = {"frost": "Givre", "arcane": "Arcanes", "fire": "Feu"}
        items = expected["h"]["back"]["items"]
        open_dropdown(game, window.slot.button)
        find(game.stub.menu, ns.SlotName("back")).pick()
        for item in (next(row for row in items if "shortUses" not in row),
                     next(row for row in items if row["id"] == 14134)):
            index = next(i for i, row in window.rowData.items() if row.id == item["id"])
            game.stub.run(window.rows[index], "OnEnter")
            lines = [line[1] for line in game.lua.globals().GameTooltip.lines.values()]
            self.assert_aoe_tooltip(game, lines, expected["h"]["back"], item)
            if item["id"] == 14134:
                self.assertNotIn(game.lua.globals().string.format(ns.L.AOE_ON_USE, "+0,0"), lines)
            parts = []
            for school, share in item["shortSchools"]:
                pct = f"{share:.1f}".replace(".", ",")
                parts.append(f"{labels[school]} {pct} %")
            self.assertNotIn(game.lua.globals().string.format(ns.L.AOE_DAMAGE, ", ".join(parts)), lines)
            game.stub.run(window.rows[index], "OnLeave")
        for index, label in ((2, ns.L.RANK_BIS), (3, ns.L.RANK_ALT), (4, ns.L.RANK_ALT)):
            self.assertRegex(window.rows[index].rank.text, rf"^\|c[0-9a-fA-F]{{8}}{label}\|r$")
            self.assertFalse(window.rows[index].bar.shown)
        self.assertFalse(window.add.shown)
        self.assertTrue(window.alts.shown)
        click(window.scenario.buttons[1])
        self.assertEqual(ns.Browser.state.slot, "back")
        self.assertEqual(gains(), [])
        click(window.scenario.buttons[2])
        self.assert_scores(gains(), items[:3])
        ns.SetAlternatives(ns, 6)
        self.assert_scores(gains(), items[:7])
        ns.SetOption(ns, "listAlts", False)
        self.assert_scores(gains(), items[:1])
        ns.SetOption(ns, "listAlts", True)
        ns.SetAlternatives(ns, 2)
        open_dropdown(game, window.slot.button)
        find(game.stub.menu, texts(game.stub.menu)[0]).pick()
        click(window.tabs.buttons[3])
        self.assertFalse(window.scenario.shown)
        self.assertTrue(window.list.buttons[1].highlightLocked)
        click(window.tabs.buttons[1])
        self.assertTrue(window.scenario.buttons[2].highlightLocked)
        self.assertEqual(len(gains()), len(expected_rows))
        game.slash("seen")
        self.assertTrue(gains())
        self.assertNotIn(14134, [i for i, _ in gains()])
        click(window.list.buttons[2])
        self.assertEqual(gains(), [])
        self.assertTrue(window.list.buttons[2].highlightLocked)
        self.assertFalse(window.scenario.shown)
        click(window.list.buttons[1])
        self.assertTrue(window.scenario.shown)
        self.assertTrue(window.scenario.buttons[2].highlightLocked)
        self.assertTrue(gains())
        click(window.scenario.buttons[1])
        self.assertEqual(gains(), [])
        self.assertTrue(window.add.shown)
        click(window.tabs.buttons[3])
        self.assertFalse(window.scenario.shown)
        warrior = Game(cls="WARRIOR", saved="EasyBISCharDB = { aoe = true }")
        warrior.ns.Browser.Open()
        self.assertFalse(warrior.ns.Browser.window.empty.shown)
        self.assertTrue(any(row.gain is not None for row in warrior.ns.Browser.window.rowData.values()))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_healers_and_tanks_open_their_raid_list_and_keep_the_last_dps_scenario(self):
        game = Game(cls="MAGE", saved="EasyBISCharDB = { class = 'PRIEST', spec = 1, aoe = true }")
        ns = game.ns
        ns.Browser.Open()
        window = ns.Browser.window
        for cls, spec in (("PRIEST", 1), ("PRIEST", 2), ("PALADIN", 1), ("SHAMAN", 3), ("DRUID", 3),
                          ("PALADIN", 2), ("WARRIOR", 3), ("DRUID", 2), ("DRUID", 4), ("PALADIN", 4)):
            open_dropdown(game, window.spec.button)
            find(find(game.stub.menu, cls.title()), ns.SpecName(ns.Index.SpecName(cls, spec))).pick()
            eligible = (cls, spec) in (("DRUID", 4), ("PALADIN", 4))
            self.assertEqual(bool(window.scenario.shown and window.scenario.buttons[2].shown), eligible)
            self.assertEqual(any(r.gain is not None for r in window.rowData.values()), eligible)
            self.assertEqual(ns.Rows.AoeList(cls, spec) is not None, eligible)
            self.assertTrue(game.lua.globals().EasyBISCharDB.aoe)
            self.assertTrue(window.list.buttons[1].highlightLocked)
            self.assertTrue(any(r.kind == "item" for r in window.rowData.values()))
            game.stub.run(window.list.buttons[2], "OnClick")
            self.assertFalse(window.scenario.shown)
            self.assertTrue(window.list.buttons[2].highlightLocked)
            game.stub.run(window.list.buttons[1], "OnClick")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_ranked_armor_slots_and_unused_activation_in_the_browser(self):
        archive = combined_rankings()
        game = Game(cls="MAGE", saved="EasyBISCharDB = { class = 'MAGE', spec = 3, aoe = true }")
        game.ns.Browser.Open()
        window = game.ns.Browser.window
        self.assertIn("full mana", game.ns.Browser.ScoreInfo("MAGE", 3, "aoe")[4])
        for side, faction in (("a", "alliance"), ("h", "horde")):
            game.slash("faction " + faction)
            for slot in aoe.ARMOR_SLOTS:
                open_dropdown(game, window.slot.button)
                find(game.stub.menu, game.ns.SlotName(slot)).pick()
                measured = archive["MAGE 3"][side][slot]["items"]
                rows = [r for r in window.rowData.values() if r.kind == "item"]
                self.assert_scores([(r.id, r.gain) for r in rows], measured[:3])
                if slot == "chest":
                    robe = next(r for r in measured if r["id"] == 14152)
                    self.assertEqual(robe["shortUses"], 0)
                    self.assertGreater(robe["shortGain"], robe["shortActiveGain"])
                    index = next(i for i, row in window.rowData.items() if row.id == robe["id"])
                    game.stub.run(window.rows[index], "OnEnter")
                    lines = [line[1] for line in game.lua.globals().GameTooltip.lines.values()]
                    self.assertNotIn(game.lua.globals().string.format(game.ns.L.AOE_UNUSED, f"{robe['shortActiveGain']:+.1f}"), lines)
                    game.stub.run(window.rows[index], "OnLeave")

    def test_shockadin_bracers(self):
        ranks = combined_rankings()
        wrists = ranks["PALADIN 4"]["a"]["wrist"]["items"]
        self.assertEqual([row["id"] for row in wrists[:2]], [18497, 18458])
        self.assertEqual(wrists[0]["score"], wrists[1]["score"])

    def test_feral_cat_published_helm_order(self):
        factions = combined_rankings()["DRUID 4"]
        for side, leaders in (("a", [252485, 279253]), ("h", [279253, 252485])):
            self.assertEqual([row["id"] for row in factions[side]["head"]["items"][:3]],
                             leaders + [252482])

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_published_feral_cat_helm_keeps_activation_and_cooldown_measurements(self):
        game = Game(cls="DRUID")
        game.slash("faction alliance")
        head = game.ns.Rows.AoeList("DRUID", 4).head
        row = next(head[i] for i in range(1, len(head) + 1) if head[i][1] == 8348)
        item = next(r for r in combined_rankings()["DRUID 4"]["a"]["head"]["items"] if r["id"] == 8348)
        self.assertGreater(item["shortUseAfter"], 0)
        self.assertEqual(row.shortUseAfter, item["shortUseAfter"])
        self.assertGreater(row.shortGain, row.shortPassiveGain)
        self.assertEqual(row.cooldownSeconds, 300)
        self.assertAlmostEqual(row.shortAverageGain, item["shortAverageGain"])
        self.assertAlmostEqual(row.routeAverageGain, item["routeAverageGain"])

    def test_physical_techniques_affect_the_recommended_main_hand(self):
        short = aoe.read(BUILD / "corrections" / "aoe.json")
        proofs = aoe.read(BUILD / "corrections" / "aoe_weapon_priority.json")["specs"]
        for key, better, worse in (("WARRIOR 2", (22384, 279261), (12590, 279261)),
                                   ("ROGUE 2", (279259, 12590), (12590, 279259))):
            profile = aoe.read(aoe.PROFILES / short["specs"][key]["profile"])
            for side in ("a", "h"):
                with self.subTest(spec=key, faction=side):
                    hands, _ = aoe_weapon_priority.ratings(profile, proofs[key]["factions"][side])
                    self.assertGreater(hands[better]["weaponRotationPoints"], hands[worse]["weaponRotationPoints"])
                    self.assertGreater(hands[better]["weaponPriority"], hands[worse]["weaponPriority"])
                    ranked = [r["id"] for r in combined_rankings()[key][side]["main"]["items"]]
                    self.assertLess(ranked.index(better[0]), ranked.index(worse[0]))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_published_weapon_points_and_damage_percentages_for_every_specialization(self):
        game = Game()
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        display_specs = rules.dungeon_specializations(db)
        for key, factions in combined_rankings().items():
            cls, _ = key.split()
            spec = display_specs[key]
            ranged_hunter = cls == "HUNTER" and db.classes[cls]["specs"][spec]["role"] == "Ranged DPS"
            for faction, slots in factions.items():
                published = game.ns.data.aoe.lists[f"{cls}:{spec}:{faction}"]
                for slot, block in slots.items():
                    weapon = slot in ("main", "off") or (slot == "ranged" and cls not in ("DRUID", "PALADIN", "SHAMAN"))
                    with self.subTest(spec=key, faction=faction, slot=slot):
                        display = published[slot]
                        items = block["items"]
                        if ranged_hunter and slot == "trinket":
                            items = [item for item in items if item["id"] != ladders.HAND_OF_JUSTICE]
                        self.assertEqual(len(display), len(items))
                        self.assertEqual(display.pointStat is not None, weapon)
                        previous = float("inf")
                        for i, item in enumerate(items, 1):
                            row = display[i]
                            self.assertEqual(row[1], item["id"])
                            self.assertAlmostEqual(row[2], item["score"], places=8)
                            if weapon:
                                self.assertAlmostEqual(row.weaponPriority, item["weaponPriority"], places=7)
                                self.assertAlmostEqual(row.weaponPriority, row.weaponBasePoints + row.weaponBonusPoints
                                                       + row.weaponRotationPoints, places=7)
                                if key == "WARRIOR 2" and slot == "main" and i == 5:
                                    self.assertEqual(row[1], 10847)
                                else:
                                    self.assertLessEqual(row.weaponPriority, previous)
                                    previous = row.weaponPriority
                            else:
                                self.assertIsNone(row.weaponPriority)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_weapon_and_jewelry_tooltips_show_the_measured_configuration(self):
        archive = aoe.read(BUILD / "corrections" / "aoe.json")
        game = Game(cls="HUNTER", saved="EasyBISCharDB = { class = 'HUNTER', spec = 4, aoe = true }")
        game.ns.Browser.Open()
        window = game.ns.Browser.window
        for side, faction in (("a", "alliance"), ("h", "horde")):
            game.slash("faction " + faction)
            blocks = combined_rankings()["HUNTER 3"][side]
            for slot in ("finger", "trinket", "main", "off", "ranged"):
                block = blocks[slot]
                open_dropdown(game, window.slot.button)
                find(game.stub.menu, game.ns.SlotName(slot)).pick()
                rows = [r for r in window.rowData.values() if r.kind == "item"]
                self.assert_scores([(r.id, r.gain) for r in rows], block["items"][:3])
                game.stub.run(window.rows[2], "OnEnter")
                lines = [line[1] for line in game.lua.globals().GameTooltip.lines.values()]
                self.assert_aoe_tooltip(game, lines, block, block["items"][0])
                if slot in ("main", "off", "ranged"):
                    detail = block["items"][0]
                    self.assertIn(game.ns.L.RANK_BIS, window.rows[2].rank.text)
                    self.assertNotIn(game.lua.globals().string.format(game.ns.L.AOE_WEAPON_PRIORITY,
                                  f"{detail['weaponBasePoints']:.1f}", f"{detail['weaponBonusPoints']:+.1f}",
                                  f"{detail['weaponRotationPoints']:+.1f}", game.ns.L.AOE_POWER_rap), lines)
                    self.assertNotIn(game.lua.globals().string.format(game.ns.L.AOE_MEASURED_GAIN,
                                  f"{detail['score']:+.2f}"), lines)
                    self.assertEqual(block["pointStat"], "rap")
                if slot in ("finger", "trinket"):
                    name = archive["comparisonNames"][str(block["pairedItem"])]
                    self.assertIn(f"Compared with this slot empty and {name} still equipped in the other slot.", lines)
                elif slot == "ranged":
                    self.assertIn("Compared with Hornwood Recurve Bow.", lines)
                else:
                    reference = " + ".join(archive["comparisonNames"][str(i)] for i in block["referenceWeapons"] if i)
                    self.assertIn(f"Compared with {reference}.", lines)
                    row = block["items"][0]
                    pair = (row["id"], row["partner"]) if slot == "main" else (row["partner"], row["id"])
                    names = " + ".join(game.ns.Items.Name(i) for i in pair if i)
                    self.assertIn(f"Tested together · {names}.", lines)
                game.stub.run(window.rows[2], "OnLeave")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_melee_hybrids_display_melee_items_in_both_factions(self):
        game = Game()
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        for faction in ("alliance", "horde"):
            game.slash("faction " + faction)
            for cls, spec in (("PALADIN", 3), ("SHAMAN", 2)):
                slots = game.ns.Rows.AoeList(cls, spec)
                for slot, rejected in (("neck", 19426), ("back", 272411), ("trinket", 12930)):
                    with self.subTest(faction=faction, cls=cls, slot=slot):
                        rows = slots[slot]
                        ids = [rows[n][1] for n in range(1, len(rows) + 1)]
                        self.assertNotIn(rejected, ids)
                        self.assertGreater(len(ids), 1)
                        if slot != "trinket":
                            for iid in ids:
                                rules.validate_candidate({"class": cls, "spec": spec}, iid,
                                                         rules.client_stats(db.gear[iid]["stats"]))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_two_handed_specs_switch_from_off_hand_to_main_hand(self):
        db = fdb.load(BUILD / "cache" / "ForeverDB")
        for cls, spec, name in (("PALADIN", 3, "Retribution"), ("WARRIOR", 1, "Arms"), ("SHAMAN", 2, "Enhancement")):
            with self.subTest(spec=name):
                game = Game(cls="WARRIOR", saved="EasyBISCharDB = { class = 'WARRIOR', spec = 2, aoe = true }")
                ns = game.ns
                ns.Browser.Open()
                window = ns.Browser.window
                open_dropdown(game, window.slot.button)
                find(game.stub.menu, ns.SlotName("off")).pick()
                open_dropdown(game, window.spec.button)
                find(find(game.stub.menu, cls.title()), name).pick()
                self.assertEqual(ns.Browser.state.slot, "main")
                for faction in ("alliance", "horde"):
                    game.slash("faction " + faction)
                    rows = [row for row in window.rowData.values() if row.kind == "item"]
                    self.assertTrue(rows)
                    for row in rows:
                        self.assertEqual((db.gear[row.id]["inv"], row.weaponPartner), (17, 0))
                    published = ns.Rows.AoeList(cls, spec)
                    self.assertIsNone(published.off)
                    for i in range(1, len(published.main) + 1):
                        item = published.main[i]
                        self.assertEqual((db.gear[item[1]]["inv"], item.partner), (17, 0))
                    open_dropdown(game, window.slot.button)
                    self.assertNotIn(ns.SlotName("off"), texts(game.stub.menu))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_new_specs_show_measured_slots_and_pet_contribution(self):
        archive = combined_rankings()
        game = Game(cls="HUNTER", saved="EasyBISCharDB = { class = 'HUNTER', spec = 1, aoe = true }")
        game.ns.Browser.Open()
        window = game.ns.Browser.window
        open_dropdown(game, window.slot.button)
        hunter_slots = archive["HUNTER 1"]["a"]
        self.assertEqual(texts(game.stub.menu), ["All", *(game.ns.SlotName(sl) for sl in (
            *aoe.ARMOR_SLOTS, "finger", "trinket", "main", "off", "ranged") if sl in hunter_slots)])
        find(game.stub.menu, "Hands").pick()
        display_specs = rules.dungeon_specializations(fdb.load(BUILD / "cache" / "ForeverDB"))
        for key in sorted(archive):
            cls, _ = key.split()
            spec = display_specs[key]
            label = game.ns.SpecName(game.ns.Index.SpecName(cls, spec))
            open_dropdown(game, window.spec.button)
            find(find(game.stub.menu, cls.title()), label).pick()
            self.assertTrue(window.scenario.buttons[2].highlightLocked)
            for side, command in (("a", "alliance"), ("h", "horde")):
                game.slash("faction " + command)
                block = archive[key][side]["hands"]
                expected = block["items"]
                rows = [r for r in window.rowData.values() if r.kind == "item"]
                self.assert_scores([(r.id, r.gain) for r in rows], expected[:3])
                game.stub.run(window.rows[2], "OnEnter")
                lines = [line[1] for line in game.lua.globals().GameTooltip.lines.values()]
                self.assert_aoe_tooltip(game, lines, block, expected[0])
                if (cls, spec) in (("HUNTER", 1), ("HUNTER", 2), ("WARLOCK", 2), ("WARLOCK", 3)):
                    self.assertNotIn(game.lua.globals().string.format(game.ns.L.AOE_PET, f"{expected[0]['shortPetPct']:.1f}"), lines)
                else:
                    self.assertNotIn("shortPetPct", expected[0])
                game.stub.run(window.rows[2], "OnLeave")


if __name__ == "__main__":
    unittest.main()
