"""Faction-specific equivalents in the reference gear for a single dungeon pack."""
import copy
import json
import math

import aoe_eligibility as eligibility
import ladders
import phases

# Forever quest 2994 (Saving Sharpbeak) is Alliance. Quest 7862 (Job Opening:
# Guard Captain of Revantusk Village) is Horde. Some rewards lack DB faction tags.
QUEST_TWINS = {270275: ("a", 19120), 19120: ("h", 270275),
               270276: ("a", 270225), 270225: ("h", 270276)}
DISPLAY_AND_SOURCE = {"id", "name", "icon", "sources", "factionRestriction"}


def side_for_race(profile, race):
    sides = [side for side, value in profile["races"].items() if value == race]
    if len(sides) != 1:
        raise ValueError(f"Cannot identify one reference faction for {race}")
    return sides[0]


def equipment(profile, race, gear, slots):
    """Copy the preset, retaining suffixes and enchants when a quest reward changes ID."""
    result = copy.deepcopy(gear)
    if profile.get("factionReferenceItems"):
        side = side_for_race(profile, race)
        for slot, item_id in profile["factionReferenceItems"].get(side, {}).items():
            result["items"][slots.index(slot)]["id"] = item_id
    return result


def paired_item(profile, side, slot):
    overrides = profile.get("factionReferenceItems", {}).get(side, {})
    return overrides.get(slot + "2", profile.get("pairedItems", {}).get(slot))


def comparison_ids(profile):
    ids = set(profile.get("referenceWeapons", [])) | set(profile.get("comparisonItems", {}).values())
    ids.update(profile.get("pairedItems", {}).values())
    for overrides in profile.get("factionReferenceItems", {}).values():
        ids.update(overrides.values())
    return ids - {0}


def allows_side(item_id, side, native, client):
    allowed = QUEST_TWINS.get(item_id, (side,))[0]
    faction = native.get("factionRestriction")
    return (side == allowed and faction in (None, 0, {"a": 1, "h": 2}[side])
            and client.get("side") in (None, "", side))


def validate_reference_stats(profile, slot, item_id, item, stats):
    key = f"{profile.get('class')} {profile.get('spec')}"
    if key not in eligibility.STAT_CONTROLS:
        return
    if slot == "ranged" and (key, item_id) == ("PALADIN 3", 23203):
        import aoe_ranged
        aoe_ranged.validate_native(profile, item)
        if stats:
            raise ValueError("Retribution's neutral reference 23203 has offensive stats")
        return
    # Tanks can wear defensive reference pieces even when swapping them out
    # increases damage. Additional armor, block, defense, parry and dodge apply.
    if key in {"DRUID 2", "PALADIN 2", "WARRIOR 3"} and not stats.keys() & eligibility.CASTER_ITEM_STATS:
        full_stats = item.get("scalingOptions", {}).get("0", {}).get("stats", {})
        if any(full_stats.get(str(index), 0) > 0 for index in (22, 23, 24, 25, 26, 28)):
            return
    if slot in ("main", "off") and (key in eligibility.MELEE_PRIORITY or profile["class"] in {"HUNTER", "ROGUE", "WARRIOR"}):
        return  # The weapon validator checks the client's base damage and hand requirements.
    eligibility.validate_slot_candidate(profile, slot.rstrip("12"), item_id, stats)


def validate_suffixes(root, profile, slots, gear):
    affixed = [(slot, piece) for slot, piece in zip(slots, gear["items"]) if piece.get("randomSuffix")]
    if not affixed:
        return
    wanted_items = {piece["id"] for _, piece in affixed}
    wanted_suffixes = {piece["randomSuffix"] for _, piece in affixed}
    items, suffixes = {}, {}
    for name in ("leftover_db.json", "db.json"):
        data = json.loads((root / "assets/database" / name).read_text(encoding="utf-8"))
        items.update((i["id"], i) for i in data["items"] if i["id"] in wanted_items)
        suffixes.update((v["id"], v) for v in data.get("randomSuffixes", ()) if v["id"] in wanted_suffixes)
    for slot, piece in affixed:
        item_id, suffix_id = piece["id"], piece["randomSuffix"]
        item, suffix = items.get(item_id, {}), suffixes.get(suffix_id)
        if not suffix or suffix_id not in item.get("randomSuffixOptions", ()):
            raise ValueError(f"Invalid reference suffix {suffix_id} for {item_id}")
        stats = eligibility.native_stats(item)
        points = item["scalingOptions"]["0"]["randPropPoints"]
        for stat, (index, _) in eligibility.STAT_IDS.items():
            raw = suffix.get("stats", ())
            bonus = math.floor(raw[index] * points / 10000 + 0.5) if index < len(raw) else 0
            if bonus:
                stats[stat] = stats.get(stat, 0) + bonus
        validate_reference_stats(profile, slot, item_id, item, stats)


def validate(profile, gear, slots, items, client_items):
    overrides = profile.get("factionReferenceItems", {})
    if set(overrides) - {"a", "h"}:
        raise ValueError("Unknown faction in reference equipment")
    for side in ("a", "h"):
        side_items = overrides.get(side, {})
        if set(side_items) - {"trinket1", "trinket2"}:
            raise ValueError(f"Unrecognized faction reference slot for {side}")
        for slot, piece in zip(slots, gear["items"], strict=True):
            original = piece.get("id", 0)
            item_id = side_items.get(slot, original)
            if slot in side_items:
                if QUEST_TWINS.get(item_id) != (side, original) or item_id not in items or original not in items:
                    raise ValueError(f"Invalid faction reference twin {original}/{item_id} in {slot} for {side}")
                item, twin = items[original], items[item_id]
                if ({k: v for k, v in item.items() if k not in DISPLAY_AND_SOURCE}
                        != {k: v for k, v in twin.items() if k not in DISPLAY_AND_SOURCE}):
                    raise ValueError(f"Reference twins {original}/{item_id} differ in native simulation properties")
            if item_id and item_id not in items:
                raise ValueError(f"Reference item {item_id} missing from WoWSims")
            if item_id and not allows_side(item_id, side, items[item_id], client_items.get(item_id, {})):
                raise ValueError(f"Reference has faction-restricted item {item_id} in {slot} for {side}")
            if item_id:
                client = client_items.get(item_id, {})
                if "sources" in client and (ladders.pvp_reward(client) or phases.item_phase(client) > 0):
                    raise ValueError(f"Reference item {item_id} in {slot} needs PvP or a later phase")
                if not piece.get("randomSuffix"):
                    validate_reference_stats(profile, slot, item_id, items[item_id], eligibility.native_stats(items[item_id]))
