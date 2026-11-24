"""Native dungeon damage for complete main-hand/off-hand configurations."""
import itertools
import math
import statistics

import aoe_eligibility as rules
import simulate_aoe as sim


# ForeverDB item class/subclass and WoWSims WeaponType, at level 60.
WEAPON_TYPES = {"2.0": 1, "2.1": 1, "2.15": 2, "2.13": 3, "2.4": 4, "2.5": 4,
                "2.6": 6, "4.6": 7, "2.10": 8, "2.7": 9, "2.8": 9}
PROFICIENCIES = {"WARRIOR": {1, 2, 3, 4, 5, 6, 7, 8, 9}, "PALADIN": {1, 4, 5, 6, 7, 9},
                 "HUNTER": {1, 2, 3, 6, 8, 9}, "ROGUE": {1, 2, 3, 4, 5, 9},
                 "PRIEST": {2, 4, 5, 8}, "SHAMAN": {1, 2, 3, 4, 5, 7, 8},
                 "MAGE": {2, 5, 8, 9}, "WARLOCK": {2, 5, 8, 9}, "DRUID": {2, 3, 4, 5, 6, 8}}
# WoWSims Forever CLASS_WEAPON_TYPES distinguishes a one-handed skill from its two-handed version.
TWO_HANDED = {"WARRIOR": {1, 4, 6, 8, 9}, "PALADIN": {1, 4, 6, 9}, "HUNTER": {1, 6, 8, 9},
              "ROGUE": set(), "PRIEST": {8}, "SHAMAN": {1, 4, 8}, "MAGE": {8},
              "WARLOCK": {8}, "DRUID": {4, 6, 8}}
HAND_TYPES = {21: 1, 13: 2, 22: 3, 14: 3, 23: 3, 17: 4}
DUAL_WIELD = {"WARRIOR", "HUNTER", "ROGUE"}
MELEE_GRIDS = {"WARRIOR 1", "WARRIOR 2", "ROGUE 1", "ROGUE 2", "ROGUE 3",
               "PALADIN 3", "PALADIN 4", "SHAMAN 2", "DRUID 4"}
# These uses neither hurt the pack nor improve the player's offensive stats:
# Drink, Flee, Stealth, Skinning, Gift of Stone (armor) and Restore Life.
UTILITY_EFFECTS = {1135, 5024, 1300180, 1300763, 16470, 18956, 18957}


def client_types(db, item_id):
    piece = db.gear[item_id]
    return (5 if piece["inv"] == 23 else WEAPON_TYPES.get(piece["kind"], 0), HAND_TYPES.get(piece["inv"], 0))


def fits(profile, slot, weapon, hand):
    cls, spec = profile["class"], profile["spec"]
    if weapon not in PROFICIENCIES[cls] or (hand == 4 and weapon not in TWO_HANDED[cls]):
        return False
    if (cls, spec) in (("PALADIN", 3), ("WARRIOR", 1)) and hand != 4:
        return False
    tank = (cls, spec) in (("WARRIOR", 3), ("PALADIN", 2))
    if slot == "main":
        if hand not in (1, 2, 4) or weapon in (5, 7) or (tank and hand == 4):
            return False
    else:
        if hand not in (2, 3) or (tank and weapon != 7):
            return False
        if (cls, spec) == ("SHAMAN", 2) and weapon != 7:
            return False  # This Windfury build can equip a shield with a one-hander.
        if cls in ("ROGUE", "HUNTER") or (cls, spec) == ("WARRIOR", 2):
            if weapon in (5, 7):
                return False
        if weapon not in (5, 7) and cls not in DUAL_WIELD:
            return False
    if cls == "ROGUE" and spec == 1:
        return weapon == 2
    if cls == "WARRIOR" and spec == 2 and hand == 4:
        return False
    return True


def validate_client(db, profile, slot, item_id, stats):
    raw = db.gear.get(item_id)
    if not raw or rules.client_stats(raw["stats"]) != stats:
        raise ValueError(f"Weapon {item_id}: offensive stats differ between the simulator and the client")
    weapon, hand = client_types(db, item_id)
    if raw["req"] > sim.LEVEL or not fits(profile, slot, weapon, hand):
        raise ValueError(f"{profile['class']} {profile['spec']}: illegal {slot} weapon {item_id}")
    if profile["class"] == "HUNTER":
        return rules.validate_hunter_hand(profile, item_id, stats)
    key = f"{profile['class']} {profile['spec']}"
    if slot == "main" and key == "DRUID 4" and raw["dps"] > 0:
        # Forever cat/bear paw damage uses the equipped weapon's DPS at form
        # speed (WoWSims druid.feralWeapon). A passive stat is not required.
        if (not stats.keys() & rules.CASTER_ITEM_STATS
                or stats.keys() & {"strength", "agility", "ap", "physical", "expertise"}):
            return
    if (item_id == 279260 and profile["class"] == "WARRIOR" and slot == "main"
            and weapon == 1 and hand == 4 and stats.get("strength", 0) >= 18 and raw["dps"] >= 61):
        # Forest Defender's Axe also has spell power. Its 162–244 weapon
        # damage and 18 strength are both used by the Arms attack table.
        return
    if key in ("DRUID 2", "DRUID 4") and slot == "off":
        martial_attributes = stats.get("strength", 0) + stats.get("agility", 0)
        caster_attribute = max(stats.get("intellect", 0), stats.get("spirit", 0))
        if (caster_attribute > martial_attributes
                and not stats.keys() & ({"ap", "physical", "expertise"} | rules.SHARED_RATINGS)):
            raise ValueError(f"{key}: caster off-hand {item_id} has only incidental feral stats")
    if key in rules.MELEE_PRIORITY:
        if slot == "main" and raw["dps"] > 0 and not rules.CASTER_ITEM_STATS.intersection(stats):
            return  # Weapon damage (including a weapon with only a melee proc).
        return rules.validate_candidate(profile, item_id, stats)
    # The listed martial builds attack with the weapon itself. A sword's base damage
    # and hit-triggered effects still matter when its tooltip has no offensive stats.
    hits_with_weapon = profile["class"] in ("WARRIOR", "ROGUE") or key in rules.HYBRID_MELEE
    if hits_with_weapon and weapon not in (5, 7) and raw["dps"] > 0 and not stats.keys() & rules.CASTER_ITEM_STATS:
        return
    # Shield Slam adds twice the equipped shield block value to its damage.
    if (key == "WARRIOR 3" and weapon == 7 and raw["stats"].get(48, 0) > 0
            and not stats.keys() & rules.CASTER_ITEM_STATS):
        return
    rules.validate_candidate(profile, item_id, stats)


def validate_pair_client(db, profile, main, off):
    if profile["class"] == "HUNTER" and 12939 in (main, off) and (main, off) != (12940, 12939):
        raise ValueError("Hunter off-hand 12939 requires its +50 attack power set partner 12940")
    if not main or not fits(profile, "main", *client_types(db, main)):
        raise ValueError(f"Illegal main-hand weapon {main}")
    two_handed = client_types(db, main)[1] == 4
    if (two_handed and off) or (not two_handed and not off):
        raise ValueError(f"Invalid companion for weapon {main}: {off}")
    if off and not fits(profile, "off", *client_types(db, off)):
        raise ValueError(f"Illegal off-hand weapon {off}")
    if off and ((main == off and "U" in db.items[main]["flags"]) or
                (db.items[main]["limit"] and db.items[main]["limit"] == db.items[off]["limit"])):
        raise ValueError(f"Unique weapon conflict: {main}, {off}")


def candidates_for_slot(db, profile, slot, side):
    candidates = rules.candidates_for_slot(db, profile, slot, side)
    if (profile["class"], profile["spec"], slot) == ("DRUID", 4, "main"):
        # ForeverDB's druid suggestions omit proc weapons with no passive stats,
        # including Ironfoe and Felstriker. Both trigger on the cat's attacks.
        # Start from the warrior's source-checked pool, then apply druid skills
        # and class restrictions to every candidate below.
        candidates |= rules.candidates_for_slot(db, {"class": "WARRIOR", "spec": 2}, slot, side)
    class_only = getattr(db, "class_only", {})
    return {i for i in candidates if profile["class"] in class_only.get(i, (profile["class"],))
            and i in db.gear and fits(profile, slot, *client_types(db, i))}


def validate_availability(db, profile):
    for slot in ("main", "off"):
        ids = set(profile["slots"].get(slot, []))
        for side in profile["races"]:
            excluded = ids - candidates_for_slot(db, profile, slot, side)
            if excluded:
                raise ValueError(f"{profile['class']} {side}: unavailable pre-raid {slot} weapons {sorted(excluded)}")


def _check_weapon_damage(item, raw):
    if item["weaponType"] == 7:
        block = item.get("scalingOptions", {}).get("0", {}).get("stats", {}).get("24", 0)
        if block != raw["stats"].get(48, 0):
            raise ValueError(f"Shield {item['id']}: client and simulator disagree about block value")
    if item["weaponType"] in (5, 7):
        return
    damage = item.get("scalingOptions", {}).get("0", {})
    minimum, maximum = damage.get("weaponDamageMin", 0), damage.get("weaponDamageMax", 0)
    speed = item.get("weaponSpeed", 0)
    # ForeverDB prints rounded tooltip DPS. When it provides the actual hit range and
    # attack time, compare those exactly as well (the damage distribution matters).
    if (not 0 < minimum <= maximum or speed <= 0 or abs((minimum + maximum) / (2 * speed) - raw["dps"]) > 0.2
            or ("weapon_hit" in raw and tuple(raw["weapon_hit"]) != (minimum, maximum, speed))):
        raise ValueError(f"Weapon {item['id']}: client and simulator disagree about base damage or speed")


def complete_melee_sets(profile, items, db):
    """Give each shortlisted main hand every legal shortlisted off-hand partner."""
    pairs = set()
    for main in profile["slots"]["main"]:
        if items[main]["handType"] == 4:
            pairs.add((main, 0))
            continue
        for off in profile["slots"].get("off", ()):
            if main == off and (items[main].get("unique") or "U" in db.items[main]["flags"]):
                continue
            client_limit = db.items[main]["limit"]
            native_limit = items[main].get("limitCategory")
            if ((client_limit and client_limit == db.items[off]["limit"])
                    or (native_limit and native_limit == items[off].get("limitCategory"))):
                continue
            pairs.add((main, off))
    return pairs


def validate_profile(profile, gear, items, db):
    validate_availability(db, profile)
    professions = {sim.PROFESSION_IDS.get(value, value) for value in
                   (profile["player"].get("profession1"), profile["player"].get("profession2"))}
    sets = [tuple(pair) for pair in profile["weaponSets"]]
    if not sets or len(set(sets)) != len(sets):
        raise ValueError("Missing or duplicate weapon sets")
    slots = gear["items"]
    reference = [slots[sim.EQUIPMENT_SLOTS.index(slot)].get("id", 0) for slot in ("main", "off")]
    if reference != profile["referenceWeapons"]:
        raise ValueError("Weapon comparison uses a different reference from the profile")
    validate_pair_client(db, profile, *reference)
    for pos, slot in enumerate(("main", "off")):
        if reference[pos]:
            item = items[reference[pos]]
            if (item["weaponType"], item["handType"]) != client_types(db, reference[pos]):
                raise ValueError(f"Reference {reference[pos]}: different {slot} weapon types in the simulator and client")
            _check_weapon_damage(item, db.gear[reference[pos]])
            key = f"{profile['class']} {profile['spec']}"
            if (profile["class"] in ("WARRIOR", "ROGUE", "HUNTER") or key in rules.MELEE_PRIORITY
                    or (key in ("DRUID 2", "DRUID 4") and slot == "off")):
                validate_client(db, profile, slot, reference[pos], rules.native_stats(item))
        configured = profile["slots"].get(slot, [])
        ids = {p[pos] for p in sets if p[pos]}
        if ids != set(configured) or len(ids) != len(configured):
            raise ValueError(f"Weapon sets disagree with the {slot} list")
        for iid in ids:
            item = items[iid]
            if (item.get("type") != 13 or (item.get("weaponType"), item.get("handType")) != client_types(db, iid)
                    or item.get("factionRestriction") or item.get("reqLvl", 0) > sim.LEVEL
                    or (item.get("requiredProfession") and item["requiredProfession"] not in professions)
                    or (item.get("classAllowlist") and sim.CLASS_IDS[profile["class"]] not in item["classAllowlist"])):
                raise ValueError(f"Illegal simulator {slot} weapon {iid}")
            validate_client(db, profile, slot, iid, rules.native_stats(item))
            _check_weapon_damage(item, db.gear[iid])
    for main, off in sets:
        validate_pair_client(db, profile, main, off)
        if profile["class"] == "HUNTER" and off == 12939 and (
                items[main].get("setId") != 41 or items[off].get("setId") != 41):
            raise ValueError("Hunter weapons do not complete Dal'Rend's Arms in WoWSims")
        if main == off and items[main].get("unique"):
            raise ValueError(f"Duplicate unique simulator weapon {main}")
    if f"{profile['class']} {profile['spec']}" in MELEE_GRIDS and set(sets) != complete_melee_sets(profile, items, db):
        raise ValueError("Each melee weapon must be compared with every legal shortlisted partner")


def request(profile, race, rotation, gear, pair, iterations, activations=(), held=()):
    # Preserve all non-weapon slots including their enchants and random suffixes.
    req = sim.make_request(profile, race, rotation, gear, None, 0, iterations)
    player = req["raid"]["parties"][0]["players"][0]
    equipment = player["equipment"]
    for slot, iid in zip(("main", "off"), pair, strict=True):
        equipment["items"][sim.EQUIPMENT_SLOTS.index(slot)] = {"id": iid} if iid else {}
    casts = []
    for iid in activations:
        action = {"castSpell": {"spellId": {"itemId": iid}}}
        if iid == 7515:  # Celestial Orb replenishes mana.
            action["condition"] = {"cmp": {"op": "OpLe", "lhs": {"currentManaPercent": {}},
                                           "rhs": {"const": {"val": "75%"}}}}
        casts.append({"action": action})
    for iid in held:
        casts.append({"action": {"condition": {"const": {"val": "false"}},
                                 "castSpell": {"spellId": {"itemId": iid}}}})
    claimed = set(held) | set(activations)
    if claimed:
        apl = player["rotation"]
        for entries in [apl["priorityList"], *(group["actions"] for group in apl.get("groups", []))]:
            entries[:] = [row for row in entries if row.get("action", {}).get("castSpell", {})
                          .get("spellId", {}).get("itemId") not in claimed]
    player["rotation"]["priorityList"][:0] = casts
    return req


def _samples(result, profile, iterations):
    values, hits = sim.samples(result, iterations, profile["damageChecks"], profile.get("requiredPet"))
    player = result["raidMetrics"]["parties"][0]["players"][0]
    units = {t["unitIndex"] for t in result["encounterMetrics"]["targets"]}
    schools = {}
    pet_damage = 0
    for unit in (player, *player.get("pets", [])):
        for action in unit["actions"]:
            damage = sum(t["damage"] for t in action["targets"] if t["unitIndex"] in units)
            if damage:
                school = "+".join(name for bit, name in enumerate(sim.SCHOOLS) if action["spellSchool"] & (1 << bit))
                schools[school] = schools.get(school, 0) + damage
                if unit is not player:
                    pet_damage += damage
    total = sum(schools.values())
    details = {"schoolPct": {k: round(100 * v / total, 3) for k, v in sorted(schools.items())}}
    if profile.get("requiredPet"):
        details["petPct"] = round(100 * pet_damage / total, 3)
    return values, hits, details


def _measure_pair(exe, work, profile, race, rotation, gear, pair, iterations, items):
    effects = {i: {fx.get("buffId") for fx in items[i].get("itemEffects", []) if "onUse" in fx}
               for i in pair if i}
    usable = tuple(i for i, buffs in effects.items() if buffs)
    offensive = [i for i in usable if effects[i] - UTILITY_EFFECTS]

    def run(cast):
        held = set(usable) - set(cast)
        req = request(profile, race, rotation, gear, pair, iterations, cast, held)
        result = sim.run_request(exe, work, req)
        player = result["raidMetrics"]["parties"][0]["players"][0]
        if any(sim.item_casts(player, i) for i in held):
            raise ValueError(f"Unrequested weapon activation in {pair}")
        uses = sum(sim.item_casts(player, i) for i in cast) / iterations
        return _samples(result, profile, iterations), uses

    passive, _ = run(())
    choice, alternative = passive, None
    best_activation = (False, -math.inf)
    for count in range(1, len(offensive) + 1):
        for cast in itertools.combinations(offensive, count):
            trial, uses = run(cast)
            if not uses:
                continue
            gain, err = sim.difference(trial[0], passive[0])
            improves_damage = gain > 3 * err
            if (improves_damage, gain) > best_activation:
                best_activation = (improves_damage, gain)
                if improves_damage:
                    choice = trial
                    choice[2].update(usesPerRun=uses, activatedWeapons=list(cast))
                    alternative = ("passive", passive[0])
                else:
                    choice = passive
                    choice[2]["usesPerRun"] = 0
                    alternative = ("active", trial[0])
    return choice, alternative


def compare(exe, work, profile, race, rotation, gear, iterations, items):
    reference = tuple(profile["referenceWeapons"])
    pairs = [tuple(pair) for pair in profile["weaponSets"]]
    samples = {}
    means = {}
    alternatives = {}
    for pair in dict.fromkeys([reference, *pairs]):
        samples[pair], alternatives[pair] = _measure_pair(exe, work, profile, race, rotation, gear, pair, iterations, items)
        means[pair] = statistics.mean(samples[pair][0])
    base, hits, details = samples[reference]
    measurements = []
    for pair in pairs:
        gain, se = sim.difference(samples[pair][0], base)
        measurements.append({"main": pair[0], "off": pair[1], "gain": round(gain, 4), "se": round(se, 4)})
        if alternatives[pair]:
            name, values = alternatives[pair]
            gain, se = sim.difference(values, base)
            samples[pair][2].update({name + "Gain": round(gain, 4), name + "SE": round(se, 4)})
            if name == "active":
                samples[pair][2]["passiveGain"] = measurements[-1]["gain"]
    slots = {}
    for pos, slot in enumerate(("main", "off")):
        best = {}
        for pair in sorted(pairs, key=lambda p: (-means[p], p)):
            if pair[pos]:
                best.setdefault(pair[pos], pair)
        if not best:
            continue
        rows = []
        prev = None
        for iid in sorted(best, key=lambda i: (-means[best[i]], i)):
            pair = best[iid]
            values, _, info = samples[pair]
            gain, se = sim.difference(values, base)
            row = {"id": iid, "partner": pair[1-pos], "gain": round(gain, 4), "se": round(se, 4), **info}
            if prev is not None:
                gap, err = sim.difference(prev, values)
                row.update(gap=round(gap, 4), gapSE=round(err, 4))
            rows.append(row)
            prev = values
        slots[slot] = {"baseline": round(means[reference], 4), "referenceWeapons": list(reference),
                       "baselineSchoolPct": details["schoolPct"], "baselineTargetsHitPerPack": hits, "items": rows}
    slots["main"]["setMeasurements"] = measurements
    return slots


def validate_rows(profile, main_block, off_block=None):
    sets = {tuple(pair) for pair in profile["weaponSets"]}
    table = main_block.get("setMeasurements", [])
    measured = {(row["main"], row["off"]): (row["gain"], row["se"]) for row in table}
    if (set(measured) != sets or len(measured) != len(table)
            or any(not math.isfinite(g) or not math.isfinite(se) or se < 0 for g, se in measured.values())):
        raise ValueError("Missing or invalid weapon-set measurements")
    if measured.get(tuple(profile["referenceWeapons"]), (0, 0)) != (0, 0):
        raise ValueError("The reference weapon set must have zero paired gain and uncertainty")
    for pos, block in enumerate((main_block, off_block)):
        expected = {p[pos] for p in sets if p[pos]}
        if not expected and block is None:
            continue
        if (not block or block.get("referenceWeapons") != profile["referenceWeapons"]
                or block["baseline"] != main_block["baseline"]
                or len(block["items"]) != len(expected) or {row["id"] for row in block["items"]} != expected):
            raise ValueError("Incomplete weapon ranking or inconsistent weapon reference")
        for row in block["items"]:
            pair = (row["id"], row["partner"]) if pos == 0 else (row["partner"], row["id"])
            if (measured.get(pair) != (row["gain"], row["se"])
                    or row["gain"] != max(val[0] for p, val in measured.items() if p[pos] == row["id"])):
                raise ValueError(f"Wrong companion or score for weapon {row['id']}")
