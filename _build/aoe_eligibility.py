"""Candidate selection shared by the native AOE campaign and the offline addon build."""
import hashlib
import json
import ladders
import phases


# Native WoWSims Stat enum and ForeverDB client stat IDs for the supported profiles.
STAT_IDS = {
    "strength": (0, 4), "agility": (1, 3), "intellect": (3, 5), "healing": (4, 41),
    "spell": (5, 42), "arcane": (6, 89), "fire": (7, 85), "frost": (8, 87),
    "holy": (9, 84), "nature": (10, 86), "shadow": (11, 88), "piercing": (12, 47),
    "spirit": (13, 6), "ap": (14, 38), "rap": (15, 39), "hit": (17, 31),
    "crit": (18, 32), "haste": (19, 36), "expertise": (21, 37),
    "mp5": (31, 43), "physical": (37, 83),
}
# Positive and neutral controls for each reference rotation.
STAT_CONTROLS = {"HUNTER 1": ("rap", "spell"), "WARRIOR 2": ("ap", "healing"), "ROGUE 2": ("ap", "healing"),
                 "MAGE 1": ("arcane", "shadow"), "MAGE 2": ("fire", "shadow"), "MAGE 3": ("frost", "fire"),
                 "HUNTER 2": ("rap", "spell"), "HUNTER 3": ("rap", "spell"),
                 "WARRIOR 1": ("ap", "healing"), "WARRIOR 3": ("ap", "healing"),
                 "ROGUE 1": ("ap", "healing"), "ROGUE 3": ("ap", "healing"),
                 "DRUID 1": ("nature", "shadow"), "DRUID 2": ("ap", "healing"),
                 "DRUID 3": ("nature", "shadow"), "DRUID 4": ("ap", "healing"),
                 "PRIEST 1": ("holy", "fire"), "PRIEST 2": ("holy", "fire"), "PRIEST 3": ("shadow", "fire"),
                 "PALADIN 1": ("holy", "shadow"), "PALADIN 2": ("holy", "shadow"),
                 "PALADIN 3": ("ap", "shadow"), "PALADIN 4": ("holy", "shadow"),
                 "SHAMAN 1": ("nature", "shadow"), "SHAMAN 2": ("ap", "shadow"), "SHAMAN 3": ("nature", "shadow"),
                 "WARLOCK 1": ("fire", "frost"), "WARLOCK 2": ("fire", "frost"), "WARLOCK 3": ("fire", "frost")}
# Schools used to shortlist passive gear. Item activations are checked separately.
CASTER_SCHOOLS = {"MAGE 1": {"arcane"}, "MAGE 2": {"fire", "arcane"}, "MAGE 3": {"frost", "arcane"},
                  "DRUID 1": {"nature"}, "DRUID 3": {"nature"},
                  "PRIEST 1": {"holy"}, "PRIEST 2": {"holy"}, "PRIEST 3": {"shadow"},
                  **{f"PALADIN {s}": {"holy"} for s in (1, 2, 3, 4)},
                  **{f"SHAMAN {s}": {"nature", "fire"} for s in (1, 2, 3)},
                  **{f"WARLOCK {s}": {"fire"} for s in (1, 2, 3)}}
HYBRID_MELEE = {"PALADIN 1", "PALADIN 2", "PALADIN 3", "PALADIN 4", "SHAMAN 2"}
# Special-purpose items for a secondary school enter a profile after a comparison
# against its ordinary candidates on both the short pack and the dungeon route.
SECONDARY_SCHOOLS = {"DRUID 1": {"arcane"}, "MAGE 1": {"fire"}, "MAGE 2": {"frost"},
                     **{f"WARLOCK {s}": {"shadow"} for s in (1, 2, 3)}}
MELEE_PRIORITY = {"PALADIN 3", "SHAMAN 2"}
MELEE_OFFENSE = {"strength", "agility", "ap", "expertise", "physical"}
SHARED_RATINGS = {"hit", "crit", "haste"}
CASTER_ITEM_STATS = {"spell", "healing", "arcane", "frost", "fire", "holy", "nature", "shadow",
                     "piercing", "intellect", "spirit", "mp5"}
CONTROL_BONUS = 100
# Heal, Heal Pet and Escape Root have no offensive use on this pack.
PASSIVE_ITEM_ACTIVATIONS = {
    8346: 10577, 14153: 18386, 273089: 1291758,
    13213: 1308917, 18370: 1302264, 20534: 25112, 275009: 1315972, 280060: 1315844,
    280065: 1315849, 280074: 1309551, 272437: 1291097, 18537: 1302356,
}

# Darkmantle Armor in the native Forever database is set 1676. The older
# Classic pieces share names but have different IDs, stats and set membership.
DARKMANTLE = {
    "head": (226829, "Darkmantle Cap"), "shoulder": (226826, "Darkmantle Spaulders"),
    "chest": (226825, "Darkmantle Tunic"), "wrist": (226830, "Darkmantle Bracers"),
    "hands": (226828, "Darkmantle Grips"), "waist": (226832, "Darkmantle Belt"),
    "legs": (226827, "Darkmantle Pants"), "feet": (226831, "Darkmantle Footpads"),
}


def include_darkmantle(db):
    """Supply missing vendor records without placing any piece in a Raid pool."""
    # QuestieDB Forever 1.1.5 (47a4756b) lists both vendors on each of these
    # exact item IDs. WoWSims Forever 07648faf independently lists both sellers.
    for item_id, name in DARKMANTLE.values():
        if item_id in db.gear:
            db.items.setdefault(item_id, {
                "name": name, "groups": frozenset("v"), "side": "", "flags": "", "twin": None, "limit": None,
                "sources": [["v", "230317", "Mokvar", "1454", "34.96", "38.26", "", "h", "t"],
                            ["v", "230319", "Deliana", "1455", "43.56", "52.65", "", "a", "t"]],
            })


def dungeon_specializations(db):
    """Map each measured campaign profile to the specialization that plays its rotation."""
    return {f"{cls} {spec.get('dungeon_profile', number)}": number for cls, entry in db.classes.items()
            for number, spec in entry["specs"].items() if spec["role"] in {"Caster DPS", "Ranged DPS", "Melee DPS"}
            and spec.get("dungeon_profile", number) is not None}


def ranked_specs(db):
    return set(dungeon_specializations(db))


def candidates_for_slot(db, profile, slot, side):
    cls = profile["class"]
    by_class = db.classes[cls]
    by_spec = by_class["specs"][profile["spec"]]
    class_only = getattr(db, "class_only", {})
    entries = []
    for pool in dict(ladders.SLOTS)[slot]:
        entries.extend(by_class["pools"].get(pool, ()))
        entries.extend(by_spec.get("pools", {}).get(pool, ()))
    if cls == "ROGUE" and slot in DARKMANTLE:
        item_id, _ = DARKMANTLE[slot]
        if item_id in db.gear:
            entries.append((item_id, db.gear[item_id]["req"]))
    allowed = set()
    for item_id, level in entries:
        item = db.items.get(item_id)
        if (item and level <= db.meta["cap"] and cls in class_only.get(item_id, (cls,))
                and item["side"] in ("", side) and phases.item_phase(item) == 0
                and item["groups"] & ladders.SOURCE_GROUPS and not ladders.pvp_reward(item)
                and "r" not in item["flags"]):
            allowed.add(item_id)
    if (cls, profile["spec"], slot) == ("DRUID", 1, "back"):
        # ForeverDB lists this crafted cloth cape for mages. Balance can wear it
        # and its activation hits the pack independently of Hurricane's school.
        cape = 14134
        if (cls in class_only.get(cape, (cls,))
                and cape in candidates_for_slot(db, {"class": "MAGE", "spec": 2}, slot, side)):
            allowed.add(cape)
    if slot == "ranged":
        import aoe_ranged
        allowed.update(aoe_ranged.relic_candidates(profile))
    if slot == "trinket":
        import aoe_jewelry
        allowed.update(aoe_jewelry.ADDITIONAL_TRINKETS)
    return allowed - ladders.DISQUALIFIED_ITEMS


def native_stats(item):
    raw = item.get("scalingOptions", {}).get("0", {}).get("stats", {})
    return {name: raw[str(index)] for name, (index, _) in STAT_IDS.items() if raw.get(str(index), 0) > 0}


def client_stats(raw):
    stats = {name: raw[index] for name, (_, index) in STAT_IDS.items() if raw.get(index, 0) > 0}
    # ForeverDB's spell power increases both damage and healing. Its general AP also applies at range.
    for name, index in (("spell", 45), ("healing", 45), ("rap", 38)):
        if raw.get(index, 0) > 0:
            stats[name] = stats.get(name, 0) + raw[index]
    return stats


def validate_sources(profile, item_id, measured, raw, slot=None):
    stats = client_stats(raw)
    if measured != stats:
        raise ValueError(f"{profile['class']} {profile['spec']}: offensive stats for {item_id} differ between WoWSims and ForeverDB")
    validate_slot_candidate(profile, slot, item_id, stats)


def validate_slot_candidate(profile, slot, item_id, stats):
    if slot in ("finger", "trinket"):
        import aoe_jewelry
        aoe_jewelry.validate_candidate(profile, item_id, stats)
    elif slot == "ranged":
        import aoe_ranged
        aoe_ranged.validate_candidate(profile, item_id, stats)
    else:
        validate_candidate(profile, item_id, stats)


def item_schools(profile, item_id):
    key = f"{profile['class']} {profile['spec']}"
    primary = CASTER_SCHOOLS.get(key, set())
    if item_id in profile.get("secondarySchoolItems", ()):
        return primary | SECONDARY_SCHOOLS.get(key, set())
    return primary


def validate_profile_selection(profile):
    key = f"{profile['class']} {profile['spec']}"
    secondary = profile.get("secondarySchoolItems", ())
    candidates = {i for ids in profile["slots"].values() for i in ids}
    if (len(set(secondary)) != len(secondary) or set(secondary) - candidates
            or (secondary and key not in SECONDARY_SCHOOLS)):
        raise ValueError(f"{key}: invalid secondary-school candidate list")
    route_only = profile.get("routeOnlyTrinkets", ())
    if (len(set(route_only)) != len(route_only)
            or set(route_only) - ({22268, 280032} & set(profile["slots"].get("trinket", ())))
            or any(str(i) in profile.get("itemDamageChecks", {}) for i in route_only)):
        raise ValueError(f"{key}: invalid dungeon-only trinket list")


def validate_candidate(profile, item_id, stats):
    key = f"{profile['class']} {profile['spec']}"
    if key not in STAT_CONTROLS:
        raise ValueError(f"{key}: missing AOE candidate rules and scaling controls")
    if key in MELEE_PRIORITY:
        if MELEE_OFFENSE.intersection(stats) or (SHARED_RATINGS.intersection(stats)
                                                 and not CASTER_ITEM_STATS.intersection(stats)):
            return
        raise ValueError(f"{key}: item {item_id} has no qualifying melee offense")
    mana = {"intellect", "spirit", "mp5"}
    if key in CASTER_SCHOOLS:
        schools = item_schools(profile, item_id)
        damage = stats.get("spell", 0) + sum(stats.get(school, 0) for school in schools)
        other_school = max(stats.get(school, 0) for school in {"fire", "frost", "arcane", "shadow", "holy", "nature"} - schools)
        caster_resources = mana.intersection(stats) and not {"strength", "agility", "ap", "rap"}.intersection(stats)
        suitable = damage >= other_school and stats.get("healing", 0) <= damage and (damage > 0 or caster_resources)
        if stats and stats.keys() <= SHARED_RATINGS:
            suitable = True
        if key in HYBRID_MELEE and not other_school and stats.get("healing", 0) <= damage:
            suitable = suitable or bool({"strength", "agility", "ap", "expertise", "physical"}.intersection(stats))
    else:
        magic = {"spell", "healing", "arcane", "frost", "fire", "holy", "nature", "shadow", "piercing"}
        if magic.intersection(stats):
            raise ValueError(f"{key}: item {item_id} has caster stats in the physical DPS selection")
        attack = {"agility", "physical", "rap"} if profile["class"] == "HUNTER" else MELEE_OFFENSE
        ratings = SHARED_RATINGS.intersection(stats)
        shared_rating = ratings and not (mana | {"strength", "rap"}).intersection(stats)
        # Both offensive ratings on Battleborn Armbraces work for weapon damage.
        # Its incidental Spirit does not erase its hit and crit.
        multiple_ratings = len(ratings) >= 2 and stats.keys() <= SHARED_RATINGS | {"spirit"}
        suitable = attack.intersection(stats) or shared_rating or multiple_ratings
    if not suitable and not profile.get("itemDamageChecks", {}).get(str(item_id)):
        raise ValueError(f"{key}: item {item_id} has no qualifying offensive stats or documented damage effect")


def validate_hunter_hand(profile, item_id, stats):
    """The ranged build carries its melee slots for their ranged stats."""
    if stats.keys() & (CASTER_ITEM_STATS - {"intellect", "spirit", "mp5"}):
        raise ValueError(f"HUNTER: caster stats on weapon {item_id}")
    if item_id == 12939 and not stats:
        pairs = [p for p in profile.get("weaponSets", ()) if item_id in p]
        if pairs and all(tuple(p) == (12940, 12939) for p in pairs):
            return  # Dal'Rend's Arms grants 50 attack power only for the complete pair.
    if (stats.keys() & {"agility", "physical", "rap"}
            or (stats.keys() & SHARED_RATINGS and not stats.keys() & {"intellect", "spirit", "mp5"})):
        return
    raise ValueError(f"HUNTER {profile['spec']}: weapon {item_id} provides no ranged offense")


def profile_digest(profile, directory):
    inputs = [profile]
    if "dungeonRotation" in profile:
        inputs.append(json.loads((directory / profile["dungeonRotation"]).read_text(encoding="utf-8")))
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
