"""Compare damage dealt during one dungeon pack using the native WoWSims Forever CLI.

    python -I _build/simulate_aoe.py --wowsims CHECKOUT --output results.json

CHECKOUT needs its generated Go protobufs. Build the CLI from that checkout so its
engine, gear database and rotation presets belong to the same revision.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aoe_eligibility as eligibility
import aoe_references as references
import fdb
import ladders

PROFILES = HERE / "aoe"
SEED = 4242
TARGETS = 4
SECONDS = 15
HELM_OF_FIRE = 8348
HELM_OF_FIRE_COOLDOWN = 300  # seconds, verified against WoWSims item effect 10578
LEVEL = 60
# WoWSims SpellSchool is a bit mask in ActionMetrics.
SCHOOLS = ("physical", "holy", "fire", "nature", "frost", "shadow", "arcane")
ARMOR_SLOTS = ("head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet")
EQUIPMENT_SLOTS = (*ARMOR_SLOTS, "finger1", "finger2", "trinket1", "trinket2", "main", "off", "ranged")
PAIRED_SLOTS = {"finger": "finger2", "trinket": "trinket2"}
ITEM_TYPES = {**{slot: pos + 1 for pos, slot in enumerate(ARMOR_SLOTS)}, "finger": 11, "trinket": 12, "ranged": 14}
CLASS_IDS = {"WARRIOR": 1, "PALADIN": 2, "HUNTER": 3, "ROGUE": 4, "PRIEST": 5,
             "SHAMAN": 7, "MAGE": 8, "WARLOCK": 9, "DRUID": 11}
MAX_ARMOR_TYPE = {"MAGE": 1, "PRIEST": 1, "WARLOCK": 1, "DRUID": 2, "ROGUE": 2,
                  "HUNTER": 3, "SHAMAN": 3, "PALADIN": 4, "WARRIOR": 4}
PROFESSION_IDS = {"Alchemy": 1, "Blacksmithing": 2, "Enchanting": 3, "Engineering": 4,
                  "Herbalism": 5, "Inscription": 6, "Leatherworking": 8, "Mining": 9,
                  "Skinning": 10, "Tailoring": 11}


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_preset(root, exe, path):
    if path.suffix == ".siml":
        return json.loads(subprocess.check_output([exe, "siml", "parse", "-json", path], cwd=root))
    return read(path)


def reference_equipment(root, exe, profile):
    preset = read_preset(root, exe, root / profile["gear"])
    gear = preset["player"]["equipment"] if profile["gear"].endswith(".build.json") else preset
    for slot, item in profile.get("referenceItems", {}).items():
        replacement = {"id": item} if item else {}
        if slot in profile.get("referenceEnchants", {}):
            if not item:
                raise ValueError(f"Cannot enchant empty reference slot {slot}")
            replacement["enchant"] = profile["referenceEnchants"][slot]
        gear["items"][EQUIPMENT_SLOTS.index(slot)] = replacement
    references.validate_suffixes(root, profile, EQUIPMENT_SLOTS, gear)
    return gear


def revision(root):
    if (root / ".git").exists():
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    # GitHub's source archive stores the exporting commit in its ZIP comment.
    archive = root.parent / "source.zip"
    if archive.is_file():
        with zipfile.ZipFile(archive) as source:
            commit = source.comment.decode("ascii")
            if len(commit) == 40 and root.name == f"forever-{commit}":
                return commit
    raise ValueError("Use a WoWSims git checkout or an extracted GitHub archive next to source.zip")


def encounter():
    # WoWSims StatArmor = 27, StatHealth = 29. All enemies are active at the pull.
    stats = [0] * 30
    stats[27], stats[29] = 3000, 100000
    targets = []
    for _ in range(TARGETS):
        targets.append({"id": 900001, "level": LEVEL, "mobType": "MobTypeHumanoid",
                        "stats": stats.copy(), "tankIndex": -1,
                        "targetInputs": [{"numberValue": 0}, {"numberValue": SECONDS}]})
    return {"duration": SECONDS, "durationVariation": 0, "executeProportion20": 0.2,
            "executeProportion35": 0.35, "targets": targets}


def dungeon_rotation(profile, rotation):
    apl = copy.deepcopy(rotation)
    # Raid openers may include trinkets, consumables or attacks. Each dungeon
    # profile declares the personal buffs it actually prepares before the pull.
    apl.pop("prepullActions", None)
    if profile.get("prepullBuffs"):
        apl["prepullActions"] = [
            {"doAtValue": {"const": {"val": buff["at"]}},
             "action": {"castSpell": {"spellId": {"spellId": buff["spell"]}}}}
            for buff in profile["prepullBuffs"]
        ]
    finisher = profile.get("packFinisher")
    if finisher:
        actions = next((g["actions"] for g in apl["groups"] if g["name"] == finisher["group"]), [])
        at = next((i for i, row in enumerate(actions)
                   if row["action"].get("castSpell", {}).get("spellId", {}).get("spellId") == finisher["beforeSpell"]), None)
        if at is None:
            raise ValueError(f"Missing spell {finisher['beforeSpell']} in APL group {finisher['group']}")
        remaining = {"timeUntilTargetDies": {"targetUnit": {"type": "CurrentTarget"}}}
        actions.insert(at, {"action": {
            "condition": {"cmp": {"op": "OpLe", "lhs": remaining, "rhs": {"const": {"val": f"{finisher['secondsLeft']}s"}}}},
            "castSpell": {"spellId": {"spellId": finisher["spell"]}}}})
    return apl


def make_request(profile, race, rotation, equipment, slot, item, iterations, on_use=False, passive_only=False,
                 use_after=0):
    player = copy.deepcopy(profile["player"])
    gear = references.equipment(profile, race, equipment, EQUIPMENT_SLOTS)
    # Isolate the piece and any set bonus it completes. Enchants on the rest of the set stay equipped.
    if slot is not None:
        pos = EQUIPMENT_SLOTS.index(slot + "1" if slot in PAIRED_SLOTS else slot)
        equipped_id = item or profile.get("comparisonItems", {}).get(slot, 0)
        gear["items"][pos] = {"id": equipped_id} if equipped_id else {}
    apl = dungeon_rotation(profile, rotation)
    if on_use:
        cast = {"castSpell": {"spellId": {"itemId": item}}}
        if passive_only:
            # Claim the item in the APL so autocastOtherCooldowns cannot activate it.
            cast["condition"] = {"const": {"val": "false"}}
        elif item in (14152, 18371):
            # Spend mana before using Robe of the Archmage or Mindtap Talisman.
            cast["condition"] = {"cmp": {"op": "OpLe", "lhs": {"currentManaPercent": {}},
                                         "rhs": {"const": {"val": "75%"}}}}
        elif use_after:
            cast["condition"] = {"cmp": {"op": "OpGe", "lhs": {"currentTime": {}},
                                         "rhs": {"const": {"val": f"{use_after}s"}}}}
        if passive_only or item in (14152, 18371) or use_after:
            # A preset may explicitly cast the same item later in its priority list or in a group.
            groups = [apl["priorityList"], *(group["actions"] for group in apl.get("groups", []))]
            for entries in groups:
                entries[:] = [row for row in entries if row.get("action", {}).get("castSpell", {})
                              .get("spellId", {}).get("itemId") != item]
        apl["priorityList"].insert(0, {"action": cast})
    player.update(race=race, equipment=gear, rotation=apl)
    raid = {"parties": [{"players": [player]}]}
    if profile.get("selfRaidBuffs"):
        raid["buffs"] = copy.deepcopy(profile["selfRaidBuffs"])
    return {"type": "SimTypeIndividual", "raid": raid,
            "encounter": encounter(),
            "simOptions": {"iterations": iterations, "randomSeed": str(SEED), "saveAllValues": True}}


def matches_damage_action(action, key):
    if key.startswith("item:"):
        return action.get("itemId") == int(key.removeprefix("item:"))
    return action.get("spellId") == int(key)


def targets_hit_per_pack(actions, targets, spell=None):
    hit = {t["unitIndex"] for a in actions if spell is None or matches_damage_action(a["id"], spell)
           for t in a["targets"] if t["damage"] > 0}
    return [len(hit.intersection(targets))]


def samples(result, iterations, checks, required_pet=None):
    if result.get("error") or result.get("iterationsDone") != iterations:
        raise ValueError(f"Incomplete WoWSims run: {result.get('error') or result.get('iterationsDone')}")
    if not math.isclose(result["avgIterationDuration"], SECONDS):
        raise ValueError(f"Expected a {SECONDS}-second pack")
    targets = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
    if len(targets) != TARGETS or len(set(targets)) != TARGETS:
        raise ValueError(f"Expected {TARGETS} distinct enemies")
    player = result["raidMetrics"]["parties"][0]["players"][0]
    hits = {}
    for spell, minimum in checks.items():
        spell_id = spell.removesuffix(":secondary")
        checked_targets = targets if spell_id == spell else targets[1:]
        hits[spell] = targets_hit_per_pack(player["actions"], checked_targets, spell_id)
        if not 1 <= minimum <= hits[spell][0]:
            raise ValueError(f"Spell {spell} did not damage {minimum} distinct enemies in the pack")
    if required_pet:
        pet = next((p for p in player.get("pets", []) if p["name"] == required_pet), None)
        hits[required_pet] = targets_hit_per_pack(pet["actions"] if pet else [], targets)
        if not hits[required_pet][0]:
            raise ValueError(f"{required_pet} did not damage the pack")
    values = result["raidMetrics"]["dps"]["allValues"]
    if len(values) != iterations or not all(math.isfinite(v) for v in values):
        raise ValueError("Missing or non-finite per-iteration DPS")
    # The encounter duration is fixed. Convert each individual sample before
    # computing paired differences, so gains and errors are both in damage per pack.
    damage = [dps * SECONDS for dps in values]
    recorded = sum(t["damage"] for unit in (player, *player.get("pets", [])) for action in unit["actions"]
                   for t in action["targets"] if t["unitIndex"] in targets)
    if not math.isclose(statistics.mean(damage), recorded / iterations, rel_tol=1e-8, abs_tol=0.001):
        raise ValueError("Pack damage does not match damage recorded against its four targets")
    return damage, hits


def difference(values, baseline):
    deltas = [v - b for v, b in zip(values, baseline, strict=True)]
    return statistics.mean(deltas), statistics.stdev(deltas) / math.sqrt(len(deltas))


def validate_equipment(profile, gear, items, client_items, client_gear=None):
    if len(gear["items"]) != 17:
        raise ValueError("Expected 17 equipment slots in the reference set")
    class_id = CLASS_IDS[profile["class"]]
    equipped = {piece["id"] for piece in gear["items"] if piece.get("id")}
    candidates = {item_id for slot in profile["slots"].values() for item_id in slot}
    disqualified = ladders.DISQUALIFIED_ITEMS.intersection(equipped | candidates | references.comparison_ids(profile))
    if disqualified:
        raise ValueError(f"Disqualified AoE equipment: {sorted(disqualified)}")
    professions = {PROFESSION_IDS.get(value, value) for value in
                   (profile["player"].get("profession1"), profile["player"].get("profession2"))}
    for item_id in equipped | candidates:
        item = items.get(item_id, {})
        classes = item.get("classAllowlist")
        if ((classes and class_id not in classes) or item.get("reqLvl", 0) > LEVEL
                or (1 <= item.get("type", 0) <= len(ARMOR_SLOTS)
                    and item.get("armorType", 0) > MAX_ARMOR_TYPE[profile["class"]])
                or (item.get("requiredProfession") and item["requiredProfession"] not in professions)):
            raise ValueError(f"{profile['class']} cannot equip WoWSims item {item_id}")
    for first in ("finger1", "trinket1"):
        index = EQUIPMENT_SLOTS.index(first)
        left, right = (items.get(piece.get("id"), {}) for piece in gear["items"][index:index + 2])
        category = left.get("limitCategory")
        if category and category == right.get("limitCategory"):
            raise ValueError(f"Reference {first} pair shares unique-equipped category {category}")
    references.validate(profile, gear, EQUIPMENT_SLOTS, items, client_items)
    for slot, candidates in profile["slots"].items():
        if not candidates or len(set(candidates)) != len(candidates):
            raise ValueError(f"Empty or duplicate candidate list for {slot}")
        if slot in ("main", "off"):
            continue  # Both hands are validated together by aoe_weapons.validate_profile.
        if slot in PAIRED_SLOTS:
            companion = gear["items"][EQUIPMENT_SLOTS.index(PAIRED_SLOTS[slot])].get("id", 0)
            if not companion or profile.get("pairedItems", {}).get(slot) != companion or companion in candidates:
                raise ValueError(f"Invalid fixed companion for {slot}")
        benchmark = profile.get("comparisonItems", {}).get(slot)
        if benchmark:
            if (slot != "ranged" or benchmark not in items or items[benchmark].get("factionRestriction")
                    or client_items.get(benchmark, {}).get("side")):
                raise ValueError(f"Invalid reference item for {slot}")
            import aoe_ranged
            aoe_ranged.validate_native(profile, items[benchmark], client_gear[benchmark] if client_gear is not None else None)
        for item_id in candidates:
            item = items.get(item_id)
            if not item or item.get("type") != ITEM_TYPES[slot] or not all(
                    references.allows_side(item_id, side, item, client_items.get(item_id, {})) for side in ("a", "h")):
                raise ValueError(f"WoWSims has no {slot} item {item_id}")
            if item_id == HELM_OF_FIRE and not any(
                fx.get("buffId") == 10578 and fx.get("onUse", {}).get("cooldownMs") == 1000 * HELM_OF_FIRE_COOLDOWN
                for fx in item.get("itemEffects", [])
            ):
                raise ValueError("Helm of Fire's on-use cooldown differs from the scoring model")
            if slot == "ranged":
                import aoe_ranged
                aoe_ranged.validate_native(profile, item, client_gear[item_id] if client_gear is not None else None)
            if slot in PAIRED_SLOTS:
                import aoe_jewelry
                for side in profile["races"]:
                    partner = references.paired_item(profile, side, slot)
                    aoe_jewelry.validate_pair(profile, slot, item, items[partner], side)
            eligibility.validate_slot_candidate(profile, slot, item_id, eligibility.native_stats(item))
            checks = profile.get("itemDamageChecks", {}).get(str(item_id), {})
            if checks and (not item.get("itemEffects") or any(not 1 <= n <= TARGETS for n in checks.values())):
                raise ValueError(f"{item_id}: invalid item damage check")


def run_request(exe, work, request):
    infile, outfile = work / "request.json", work / "result.json"
    infile.write_text(json.dumps(request), encoding="utf-8")
    subprocess.run([exe, "sim", "--infile", infile, "--outfile", outfile], check=True, stdout=subprocess.DEVNULL)
    return read(outfile)


def item_casts(player, item):
    return sum(t["casts"] for a in player["actions"] if a["id"].get("itemId") == item for t in a["targets"])


def scaling_controls(exe, work, profile, race, rotation, gear, iterations):
    key = f"{profile['class']} {profile['spec']}"
    positive, neutral = eligibility.STAT_CONTROLS[key]
    count = min(2000, iterations)
    slot = next(iter(profile["slots"]))
    request = make_request(profile, race, rotation, gear, slot, 0, count)
    def simulate():
        return samples(run_request(exe, work, request), count, profile["damageChecks"], profile.get("requiredPet"))[0]
    baseline = simulate()
    controls = {}
    for stat in (positive, neutral):
        index = eligibility.STAT_IDS[stat][0]
        player = request["raid"]["parties"][0]["players"][0]
        bonus = player.setdefault("bonusStats", {}).setdefault("stats", [])
        original = bonus.copy()
        bonus.extend([0] * max(0, index + 1 - len(bonus)))
        bonus[index] += eligibility.CONTROL_BONUS
        values = simulate()
        player["bonusStats"]["stats"] = original
        gain, se = difference(values, baseline)
        if (stat == neutral and values != baseline) or (stat == positive and gain <= 3 * se):
            raise ValueError(f"{key} {race}: unexpected scaling with +{eligibility.CONTROL_BONUS} {stat}: {gain} +/- {se}")
        controls[stat] = {"gain": round(gain, 4), "se": round(se, 4)}
    return {"iterations": count, "bonus": eligibility.CONTROL_BONUS, "emptySlot": slot, "stats": controls}


def compare_activation(exe, work, profile, race, rotation, gear, slot, item, iterations, baseline):
    def simulate(passive=False, after=0):
        request = make_request(profile, race, rotation, gear, slot, item, iterations, True, passive, after)
        result = run_request(exe, work, request)
        values, _ = samples(result, iterations, {})
        player = result["raidMetrics"]["parties"][0]["players"][0]
        return result, values, item_casts(player, item) / iterations

    control, passive, uses = simulate(passive=True)
    if uses:
        raise ValueError(f"Item {item} activated in its passive comparison")
    gain, se = difference(passive, baseline)
    details = {"usesPerRun": 0, "passiveGain": round(gain, 4), "passiveSE": round(se, 4)}
    # Helm of Fire can displace an attack or a cooldown at the pull. Test later openings, too.
    timings = (0, 3, 6, 9, 12) if item == 8348 else (0,)
    best_gain = -math.inf
    best = None
    for after in timings:
        result, values, uses = simulate(after=after)
        if uses:
            benefit, error = difference(values, passive)
            if benefit > best_gain:
                best_gain = benefit
                best = result, values, uses, error, after
    if best is None:
        return control, details
    result, values, uses, error, after = best
    if after:
        details["useAfterSeconds"] = after
    if best_gain > 3 * error:
        details["usesPerRun"] = uses
        return result, details
    gain, se = difference(values, baseline)
    details.update(activeGain=round(gain, 4), activeSE=round(se, 4))
    if item == 280071:
        # The equipped Talisman has no passive stats. Preserve the observed Agility
        # aura from the activation trial even when another cooldown wins the pack.
        import aoe_jewelry
        player = result["raidMetrics"]["parties"][0]["players"][0]
        details["activeTrial"] = {"usesPerRun": uses, "gainOverPassive": round(best_gain, 4),
                                  "seOverPassive": round(error, 4), **aoe_jewelry.measured_buff(item, player)}
    return control, details


def compare(exe, work, profile, race, rotation, gear, slot, iterations, items):
    results = {}
    breakdowns = {}
    for item in [0, *profile["slots"][slot]]:
        effects = [effect for effect in items.get(item, {}).get("itemEffects", []) if "onUse" in effect]
        passive_only = item in eligibility.PASSIVE_ITEM_ACTIVATIONS
        if passive_only and {fx.get("buffId") for fx in effects} != {eligibility.PASSIVE_ITEM_ACTIVATIONS[item]}:
            raise ValueError(f"Unexpected activation on utility item {item}")
        activation = {}
        if effects and not passive_only:
            result, activation = compare_activation(exe, work, profile, race, rotation, gear, slot, item,
                                                    iterations, results[0])
        else:
            request = make_request(profile, race, rotation, gear, slot, item, iterations, bool(effects), passive_only)
            result = run_request(exe, work, request)
        results[item], hits = samples(result, iterations, profile["damageChecks"], profile.get("requiredPet"))
        player = result["raidMetrics"]["parties"][0]["players"][0]
        actions = [action for unit in (player, *player.get("pets", [])) for action in unit["actions"]]
        units = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
        damages = {}
        for action in actions:
            damage = sum(t["damage"] for t in action["targets"] if t["unitIndex"] in units)
            if damage:
                mask = action["spellSchool"]
                school = "+".join(name for bit, name in enumerate(SCHOOLS) if mask & (1 << bit)) or "unknown"
                damages[school] = damages.get(school, 0) + damage
        total = sum(damages.values())
        breakdowns[item] = {"schoolPct": {s: round(100 * v / total, 3) for s, v in sorted(damages.items())}, **activation}
        if slot == "trinket" and item and "activeTrial" not in activation:
            import aoe_jewelry
            route_only = item in profile.get("routeOnlyTrinkets", ())
            breakdowns[item].update(aoe_jewelry.measured_buff(item, player, inactive=route_only))
            if route_only and item == 280032:
                breakdowns[item]["targetsHitPerPack"] = {"1315996": targets_hit_per_pack(actions, units, "1315996")}
        if not item:
            baseline_hits = hits
            baseline_actions = [a["id"] for a in actions if any(t["damage"] > 0 for t in a["targets"])]
        if profile.get("requiredPet"):
            pet_damage = sum(t["damage"] for p in player["pets"] for a in p["actions"] for t in a["targets"]
                             if t["unitIndex"] in units)
            breakdowns[item]["petPct"] = round(100 * pet_damage / total, 3)
        if passive_only:
            if item_casts(player, item):
                raise ValueError(f"Utility item {item} activated during the offensive rotation")
            breakdowns[item]["usesPerRun"] = 0
        for spell, minimum in profile.get("itemDamageChecks", {}).get(str(item), {}).items():
            per_pack = targets_hit_per_pack(actions, units, spell)
            if any(matches_damage_action(action, spell) for action in baseline_actions) or max(per_pack) < minimum:
                raise ValueError(f"Item {item}: missing AOE damage from {spell}")
            breakdowns[item].setdefault("targetsHitPerPack", {})[spell] = per_pack
    baseline = results.pop(0)
    ordered = sorted(results, key=lambda item: (-statistics.mean(results[item]), item))
    rows = []
    for at, item in enumerate(ordered):
        gain, error = difference(results[item], baseline)
        row = {"id": item, "gain": round(gain, 4), "se": round(error, 4), **breakdowns[item]}
        if at:
            gap, gap_error = difference(results[ordered[at - 1]], results[item])
            row.update(gap=round(gap, 4), gapSE=round(gap_error, 4))
        rows.append(row)
    result = {"baseline": round(statistics.mean(baseline), 4), "baselineSchoolPct": breakdowns[0]["schoolPct"],
              "baselineTargetsHitPerPack": baseline_hits, "items": rows}
    if slot in PAIRED_SLOTS:
        # Report the companion actually sent to WoWSims for this race.
        worn = references.equipment(profile, race, gear, EQUIPMENT_SLOTS)
        result["pairedItem"] = worn["items"][EQUIPMENT_SLOTS.index(PAIRED_SLOTS[slot])]["id"]
    if slot in profile.get("comparisonItems", {}):
        result["comparisonItem"] = profile["comparisonItems"][slot]
    return result


def comparison_names(profiles, items):
    ids = {i for profile in profiles for i in references.comparison_ids(profile)}
    return {str(i): items[i]["name"] for i in sorted(ids)}


def build_native(root, overlay, output, source):
    # WoWSims sorts prepull deadlines by casting a nanosecond difference to int.
    # On 386 even two actions four seconds apart can run in reverse order.
    subprocess.run(["go", "build", "-overlay", str(overlay), "-tags=with_db", "-o", str(output), str(source)],
                   cwd=root, env={**os.environ, "GOARCH": "amd64", "CGO_ENABLED": "0"}, check=True)


def campaign(root, work, iterations):
    commit = revision(root)
    exe = work / ("wowsimcli.exe" if os.name == "nt" else "wowsimcli")
    encounter_ai = PROFILES / "dungeon_target.go"
    overlay = work / "overlay.json"
    overlay.write_text(json.dumps({"Replace": {str(root / "sim/core/easybis_pack.go"): str(encounter_ai)}}),
                       encoding="utf-8")
    build_native(root, overlay, exe, "./cmd/wowsimcli")
    items = {item["id"]: item for file in ("leftover_db.json", "db.json")
             for item in read(root / "assets" / "database" / file)["items"]}
    client = fdb.load(HERE / "cache" / "ForeverDB")
    records, item_stats, profiles = {}, {}, []
    expected = eligibility.ranked_specs(client)
    for path in sorted(PROFILES.glob("*.json")):
        profile = read(path)
        key = f"{profile['class']} {profile['spec']}"
        if key not in expected:
            continue
        eligibility.validate_profile_selection(profile)
        profiles.append(profile)
        if key in records:
            raise ValueError(f"Duplicate profile for {key}")
        rotation_path = PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile else root / profile["rotation"]
        rotation = read_preset(root, exe, rotation_path)
        gear = reference_equipment(root, exe, profile)
        validate_equipment(profile, gear, items, client.items, client.gear)
        if "weaponSets" in profile:
            import aoe_weapons
            aoe_weapons.validate_profile(profile, gear, items, client)
        for slot, candidates in profile["slots"].items():
            if slot in ("main", "off"):
                for item_id in candidates:
                    stats = eligibility.native_stats(items[item_id])
                    aoe_weapons.validate_client(client, profile, slot, item_id, stats)
                    item_stats[str(item_id)] = stats
                continue
            for side in profile["races"]:
                excluded = set(candidates) - eligibility.candidates_for_slot(client, profile, slot, side)
                if excluded:
                    raise ValueError(f"{key} {side} {slot}: {sorted(excluded)} outside the pre-raid comparison")
            for item_id in candidates:
                item_stats[str(item_id)] = eligibility.native_stats(items[item_id])
                eligibility.validate_sources(profile, item_id, item_stats[str(item_id)], client.gear[item_id]["stats"], slot)
        digest = hashlib.sha256(json.dumps([profile, rotation, gear], sort_keys=True).encode()).hexdigest()
        factions, controls = {}, {}
        for side, race in profile["races"].items():
            controls[side] = scaling_controls(exe, work, profile, race, rotation, gear, iterations)
            factions[side] = {}
            for slot in profile["slots"]:
                if slot in ("main", "off"):
                    continue
                print(f"{key}, {race}, {slot}", flush=True)
                factions[side][slot] = compare(exe, work, profile, race, rotation, gear, slot, iterations, items)
            if "weaponSets" in profile:
                factions[side].update(aoe_weapons.compare(exe, work, profile, race, rotation, gear, iterations, items))
        records[key] = {"profile": path.name, "profileSha256": eligibility.profile_digest(profile, PROFILES),
                        "inputsSha256": digest, "scalingControls": controls, "factions": factions}
    if set(records) != expected:
        raise ValueError(f"Missing dungeon profiles: {sorted(expected - records.keys())}")
    return {"mode": "aoe", "metric": "packDamage", "wowsims": commit, "encounter": encounter(), "iterations": iterations,
            "schedule": {"packs": 1, "perPack": TARGETS, "seconds": SECONDS, "travel": 0},
            "encounterAiSha256": hashlib.sha256(encounter_ai.read_text(encoding="utf-8").encode()).hexdigest(),
            "seed": SEED, "itemStats": item_stats, "comparisonNames": comparison_names(profiles, items), "specs": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wowsims", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=20000)
    args = parser.parse_args()
    if args.iterations < 2:
        parser.error("--iterations must be at least 2")
    with tempfile.TemporaryDirectory() as folder:
        result = campaign(args.wowsims.resolve(), Path(folder), args.iterations)
    # Replace only after every comparison succeeded, including on a rerun.
    with tempfile.NamedTemporaryFile("w", dir=args.output.parent, encoding="utf-8",
                                     newline="\n", delete=False) as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    Path(output.name).replace(args.output)


if __name__ == "__main__":
    main()
