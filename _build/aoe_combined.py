"""Rank the same pre-raid equipment against two independently measured AOE references."""
import hashlib
import json
import math

import aoe_dungeon_precision as precision
import aoe_eligibility
import aoe_encounter
import aoe_jewelry
import aoe_weapons
import aoe_weapon_priority as weapon_priority
import ladders
import simulate_aoe


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def measured_profile(profile, record, directory):
    """Check the original simulation inputs even when a weapon has since been retired."""
    excluded = ladders.DISQUALIFIED_ITEMS
    if (excluded.intersection(simulate_aoe.references.comparison_ids(profile))
            or excluded.intersection(profile.get("referenceItems", {}).values())
            or any(excluded.intersection(ids) for ids in profile["slots"].values())
            or any(excluded.intersection(pair) for pair in profile["weaponSets"])):
        raise ValueError("Disqualified item in active AoE profile")
    if aoe_eligibility.profile_digest(profile, directory) == record["profileSha256"]:
        return profile
    # Historical weapon shortlists were sorted by item ID and by (main, off).
    # Restore only the retired trials, then require the exact measured digest.
    faction = next(iter(record["factions"].values()))
    retired = [[r["main"], r["off"]] for r in faction["main"]["setMeasurements"]
               if excluded.intersection((r["main"], r["off"]))]
    historical = dict(profile, slots=dict(profile["slots"]), weaponSets=sorted(profile["weaponSets"] + retired))
    for pos, hand in enumerate(("main", "off")):
        if hand in profile["slots"]:
            old = {pair[pos] for pair in retired if pair[pos]}
            historical["slots"][hand] = sorted(set(profile["slots"][hand]) | old)
    if not retired or aoe_eligibility.profile_digest(historical, directory) != record["profileSha256"]:
        raise ValueError("AoE archive uses a stale profile")
    return historical


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _ids(rows, fields):
    result = {}
    for row in rows:
        key = tuple(row[k] for k in fields)
        if (any(type(i) is not int or i < (0 if field == "off" else 1) for field, i in zip(fields, key))
                or key in result):
            raise ValueError(f"Invalid or duplicate equipment measurement {key}")
        result[key] = row
    return result


def _wave_damage(values, total, caps):
    # Independent rounding of a baseline, a delta and three wave means.
    if (not isinstance(values, list) or len(values) != len(caps)
            or any(not _number(d) or not 0 <= d <= cap + 0.001 for d, cap in zip(values, caps))
            or not math.isclose(sum(values), total, abs_tol=0.001, rel_tol=0)):
        raise ValueError("Dungeon wave damage is inconsistent with useful damage and pack health")


def _measurement(row, baseline):
    gain, se = row.get("gain"), row.get("se")
    # For nonnegative samples, SE(mean) <= mean. By the triangle inequality the
    # SE of a paired difference is bounded by the sum of the two damage means.
    if (not _number(gain) or not _number(se) or baseline + gain < -0.0001 or se < 0
            or se > 2 * baseline + gain + 0.0002):
        raise ValueError("Invalid paired damage gain or standard error")


def _route_activation(row, equipment):
    if "activation" not in row and "usesPerRun" not in row:
        return {}
    active, uses = row.get("activation", []), row.get("usesPerRun", {})
    if (not isinstance(active, list) or not isinstance(uses, dict)
            or any(type(i) is not int or i not in equipment for i in active) or len(set(active)) != len(active)
            or any(str(i) not in {str(v) for v in equipment} or not _number(n) or n < 0 for i, n in uses.items())
            or {str(i) for i in active} != {str(i) for i, n in uses.items() if n > 0}):
        raise ValueError("Dungeon activation does not match the measured equipment")
    details = {"routeActivated": sorted(active), "routeUses": {int(i): n for i, n in uses.items()}}
    if row.get("usePack") is not None:
        pack = row["usePack"]
        if type(pack) is not int or not 0 <= pack <= 3:
            raise ValueError("Invalid dungeon activation wave")
        if pack:
            details["routeUsePack"] = pack
    if row.get("useAfterSeconds") is not None:
        after = row["useAfterSeconds"]
        if not _number(after) or after < 0:
            raise ValueError("Invalid dungeon activation time")
        if after:
            details["routeUseAfter"] = after
    trials = row.get("activationTrials", [])
    if trials:
        first = trials[0]
        if first["activation"] or first["usesPerRun"] or first["gain"] != 0 or first["se"] != 0:
            raise ValueError("Missing passive dungeon activation trial")
        selected = []
        for trial in trials:
            if (not _number(trial["gain"]) or not _number(trial["se"]) or trial["se"] < 0
                    or not set(trial["activation"]) <= equipment or not isinstance(trial["usesPerRun"], dict)
                    or any(i not in {str(v) for v in trial["activation"]} or not _number(n) or n <= 0
                           for i, n in trial["usesPerRun"].items())):
                raise ValueError("Invalid dungeon activation trial")
            if all(trial[k] == row[k] for k in ("activation", "usesPerRun", "usePack", "useAfterSeconds")):
                selected.append(trial)
        if len(selected) != 1:
            raise ValueError("Dungeon activation has no unique matching trial")
        chosen = selected[0]
        # Means and errors are archived independently to four decimal places.
        if ((active and chosen["gain"] < 3 * chosen["se"] - 0.0002) or any(
                t["usesPerRun"] and t["gain"] > 3 * t["se"] + 0.0002 and t["gain"] > chosen["gain"] + 0.0001
                for t in trials)):
            raise ValueError("Dungeon activation differs from the best significant paired trial")
    return details


def _score(short, route, sb, rb, caps, equipment):
    _measurement(short, sb)
    _measurement(route, rb)
    _wave_damage(route.get("packDamage"), rb + route["gain"], caps)
    return {"score": 50 * (short["gain"] / sb + route["gain"] / rb),
            # Baselines are the recorded means. Summing component SEs supplies an
            # upper bound for unknown covariance of the two normalized gain estimates.
            "scoreSE": 50 * (short["se"] / sb + route["se"] / rb),
            "shortGain": short["gain"], "shortSE": short["se"], "routeGain": route["gain"], "routeSE": route["se"],
            "routePackDamage": route["packDamage"], **_route_activation(route, equipment)}


def _short_details(row):
    if row is None:
        return {}
    details = {"shortSchools": sorted(row["schoolPct"].items(), key=lambda x: (-x[1], x[0]))}
    for src, dest in (("petPct", "shortPetPct"), ("useAfterSeconds", "shortUseAfter"),
                      ("usesPerRun", "shortUses"), ("activatedWeapons", "shortActivated")):
        if src in row:
            details[dest] = row[src]
    if row.get("usesPerRun", 0) > 0:
        details["shortPassiveGain"] = row["passiveGain"]
    elif "activeGain" in row:
        details["shortActiveGain"] = row["activeGain"]
    return details


def _slot_info(short, route, caps):
    sb, rb = short.get("baseline"), route.get("baseline")
    if any(not _number(v) or v <= 0 for v in (sb, rb)):
        raise ValueError("Reference damage must be finite and positive")
    _wave_damage(route.get("baselinePackDamage"), rb, caps)
    result = {"shortBaseline": sb, "routeBaseline": rb, "routeBaselinePackDamage": route["baselinePackDamage"]}
    for field in ("comparisonItem", "pairedItem", "referenceWeapons"):
        if short.get(field) != route.get(field):
            raise ValueError(f"Different equipment reference for {field}")
        if field in short:
            result[field] = short[field]
    return result


def _finish(rows, short_best, route_best):
    if set(short_best) != set(route_best) or len(short_best) != len(rows):
        raise ValueError("Different candidates in the two scenarios")
    for prop, gains in (("shortRank", short_best), ("routeRank", route_best)):
        positions = {}
        previous_gain = None
        for index, iid in enumerate(sorted(gains, key=lambda i: (-gains[i], i)), 1):
            if gains[iid] != previous_gain:
                rank = index
                previous_gain = gains[iid]
            positions[iid] = rank
        for row in rows:
            row[prop] = positions[row["id"]]
    return sorted(rows, key=lambda row: (-row.get("weaponPriority", row["score"]), -row["score"], row["id"]))


def _single_items(short, route, caps, priorities=None):
    result = _slot_info(short, route, caps)
    first = _ids(short["items"], ["id"])
    second = _ids(route["items"], ["id"])
    if set(first) != set(second):
        raise ValueError("Different candidates in the two scenarios")
    rows = []
    for (iid,), source in first.items():
        if iid in ladders.DISQUALIFIED_ITEMS:
            continue
        dungeon = second[iid,]
        sb, rb = result["shortBaseline"], result["routeBaseline"]
        stats = _score(source, dungeon, sb, rb, caps, {iid})
        if priorities is not None:
            stats.update(priorities[iid,])
        if iid == simulate_aoe.HELM_OF_FIRE:
            sg, ss, rg, rs = precision.helm_gains(source, dungeon, route["baselineAvgSeconds"])
            stats.update(score=50 * (sg / sb + rg / rb), scoreSE=50 * (ss / sb + rs / rb),
                         shortAverageGain=sg, routeAverageGain=rg, cooldownSeconds=simulate_aoe.HELM_OF_FIRE_COOLDOWN)
        rows.append({"id": iid, **stats, **_short_details(source)})
    result["items"] = _finish(rows, {r["id"]: r["shortGain"] for r in rows}, {r["id"]: r["routeGain"] for r in rows})
    return result


def _weapon_items(short, route, caps, priorities=None, *, two_handed_only=False):
    first = _ids(short["main"]["setMeasurements"], ["main", "off"])
    second = _ids(route["main"]["setMeasurements"], ["main", "off"])
    if not first or set(first) != set(second):
        raise ValueError("Missing or different weapon configurations in the two scenarios")
    sb, rb = short["main"]["baseline"], route["main"]["baseline"]
    reference = tuple(short["main"]["referenceWeapons"])
    if ladders.DISQUALIFIED_ITEMS.intersection(reference):
        raise ValueError("Disqualified reference weapon")
    _slot_info(short["main"], route["main"], caps)
    if reference in first and any(m[reference][k] != 0 for m in (first, second) for k in ("gain", "se")):
        raise ValueError("The reference weapon configuration must have zero gain and SE")
    details = {}
    for slot in ("main", "off"):
        for row in short.get(slot, {}).get("items", []):
            pair = (row["id"], row["partner"]) if slot == "main" else (row["partner"], row["id"])
            details[pair] = _short_details(row)
    scores = {p: _score(v, second[p], sb, rb, caps, set(p) - {0}) for p, v in first.items()
              if not ladders.DISQUALIFIED_ITEMS.intersection(p)}
    if priorities is not None:
        if scores.keys() != priorities.keys():
            raise ValueError("Weapon priorities differ from the tested damage configurations")
        for pair, record in scores.items():
            record.update(priorities[pair])
    if two_handed_only:
        # Validated weapon sets use an empty off hand exclusively for two-handers.
        scores = {pair: value for pair, value in scores.items() if pair[1] == 0}
        if not scores:
            raise ValueError("No measured two-handed weapon sets")

    def preference(pair):
        row = scores[pair]
        return row.get("weaponPriority", row["score"]), row["score"]
    slots = {}
    for pos, slot in enumerate(("main", "off")):
        if slot not in short or (two_handed_only and slot == "off"):
            continue
        result = _slot_info(short[slot], route[slot], caps)
        if (short[slot]["baseline"] != sb or route[slot]["baseline"] != rb
                or result["routeBaselinePackDamage"] != route["main"]["baselinePackDamage"]):
            raise ValueError("Inconsistent weapon baselines between hands")
        best, short_best, route_best = {}, {}, {}
        for pair in sorted(scores):
            iid = pair[pos]
            if iid:
                if iid not in best or preference(pair) > preference(best[iid]):
                    best[iid] = pair
                short_best[iid] = max(short_best.get(iid, -math.inf), first[pair]["gain"])
                route_best[iid] = max(route_best.get(iid, -math.inf), second[pair]["gain"])
        rows = [{"id": iid, "partner": pair[1-pos], **scores[pair], **details.get(pair, {})}
                for iid, pair in best.items()]
        result["items"] = _finish(rows, short_best, route_best)
        slots[slot] = result
    return slots


def _route_evidence(row, trials, required_pet, baseline=False, uses_mana=None):
    def value(field):
        return row.get("baseline" + field[0].upper() + field[1:] if baseline else field)
    hits = value("packHits")
    if (not isinstance(hits, list) or len(hits) != 3
            or any(type(n) is not int or not 1 <= n <= trials for n in hits)):
        raise ValueError("Dungeon damage was not observed in each wave")
    elapsed = value("avgSeconds")
    if not _number(elapsed) or not 0 < elapsed <= aoe_encounter.TIME_LIMIT:
        raise ValueError("Invalid dungeon encounter duration")
    pet, waves = value("petDamage"), value("packDamage")
    if required_pet and (not _number(pet) or not isinstance(waves, list) or not all(_number(v) for v in waves)
                         or not 0 < pet <= sum(waves) + 0.001):
        raise ValueError("Missing dungeon pet damage")
    refills, restored = value("manaRefillEvents"), value("manaRestored")
    if uses_mana is True and (refills != [trials, trials] or not all(type(n) is int for n in refills)
                              or not isinstance(restored, list) or len(restored) != 2
                              or any(not _number(v) or v < 0 for v in restored)):
        raise ValueError("Missing measured mana refills between dungeon pulls")
    if uses_mana is False and (refills is not None or restored is not None):
        raise ValueError("Unexpected mana refill for a class without mana")


def rankings(short, route, directory=None, priorities=None, *, damage_only=False):
    """Validate the dungeon campaign and return per-item scores, gains, SEs and independent ranks."""
    import simulate_dungeon

    directory = directory or simulate_aoe.PROFILES
    schedule = simulate_dungeon.schedule()
    declared = route.get("schedule")
    if not isinstance(declared, dict) or declared.get("manaBetweenPacks") != "full":
        raise ValueError("Dungeon comparison requires full mana at the start of each pull")
    if (route.get("mode") != "dungeon" or route.get("metric") != "dungeonDamage"
            or route.get("schedule") != schedule or route.get("scenarioSha256") != digest(schedule)
            or route.get("sourceSha256") != simulate_dungeon.source_hashes()
            or route.get("shortArchiveSha256") != digest(short) or route.get("wowsims") != short["wowsims"]):
        raise ValueError("Dungeon archive does not match the short archive, campaign sources or encounter")
    trials = route.get("iterations")
    refinement = route.get("refinementIterations")
    if (type(trials) is not int or type(refinement) is not int or trials != 1024
            or refinement != simulate_dungeon.REFINEMENT_ITERATIONS or type(route.get("seed")) is not int
            or route["seed"] != simulate_dungeon.SEED or route.get("pilotSeed") != simulate_dungeon.PILOT_SEED
            or route["seed"] < short["seed"] + short["iterations"]
            or set(route["specs"]) != set(short["specs"])):
        raise ValueError("Incomplete specializations or insufficient dungeon trials")
    if short["specs"] and not damage_only:
        if priorities is None:
            priorities = simulate_aoe.read(simulate_aoe.HERE / "corrections" / "aoe_weapon_priority.json")
        weapon_priority.validate_campaign(priorities, short)
    refined = set(route.get("refinedBlocks", []))
    if len(refined) != len(route.get("refinedBlocks", [])):
        raise ValueError("Duplicate refined dungeon block")
    actual_refined = set()
    caps = [sum(pack["health"]) for pack in schedule["packs"]]
    result = {}
    for key, src in sorted(short["specs"].items()):
        rec = route["specs"][key]
        active = simulate_aoe.read(directory / src["profile"])
        profile = measured_profile(active, src, directory)
        if not damage_only:
            priority_record = priorities["specs"][key]
            weapon_priority.validate_profile(priority_record, active, directory)
        if (key != f"{profile['class']} {profile['spec']}" or rec.get("profileSha256") != src["profileSha256"]
                or set(rec["factions"]) != set(src["factions"]) or set(rec["factions"]) != set(profile["races"])):
            raise ValueError(f"{key}: incorrect profile or faction coverage")
        factions = {}
        for side, orig in src["factions"].items():
            new = rec["factions"][side]
            if set(new) != set(orig) or set(new) != set(profile["slots"]):
                raise ValueError(f"{key} {side}: incomplete dungeon slots")
            for sl, block in new.items():
                block_name = f"{key}/{side}/{sl}"
                n = block.get("iterations")
                if type(n) is not int or n != (refinement if block_name in refined else trials):
                    raise ValueError(f"{block_name}: incorrect dungeon trial count")
                if sorted(row["id"] for row in block["items"]) != sorted(profile["slots"][sl]):
                    raise ValueError(f"{block_name}: incomplete dungeon equipment")
                if sl == "trinket":
                    expected = set(profile.get("routeOnlyTrinkets", []))
                    if {r["id"] for r in block["items"] if "routeEffect" in r} != expected:
                        raise ValueError(f"{block_name}: incomplete dungeon trinket effect evidence")
                    for row in block["items"]:
                        if row["id"] in expected:
                            aoe_jewelry.validate_dungeon_effect(row, block["baseline"])
                if n == refinement:
                    actual_refined.add(block_name)
                uses_mana = profile["class"] not in {"WARRIOR", "ROGUE"}
                _route_evidence(block, n, profile.get("requiredPet"), baseline=True, uses_mana=uses_mana)
                for sample in block.get("setMeasurements", block["items"]):
                    _route_evidence(sample, n, profile.get("requiredPet"), uses_mana=uses_mana)
            if "off" in new and new["off"]["iterations"] != new["main"]["iterations"]:
                raise ValueError("Different iteration counts for the same weapon pair")
            aoe_weapons.validate_rows(profile, new["main"], new.get("off"))
            hands, ranged = None, None
            if not damage_only:
                hands, ranged = weapon_priority.ratings(active, priority_record["factions"][side])
            two_handed_only = key == "SHAMAN 2"
            slots = _weapon_items(orig, new, caps, hands, two_handed_only=two_handed_only)
            if not damage_only:
                for block in slots.values():
                    block["pointStat"] = weapon_priority.point_stat(active)
                if key == "WARRIOR 2":
                    # Curated Fury main-hand placement for Dragon's Call.
                    weapons = slots["main"]["items"]
                    for index, row in enumerate(weapons):
                        if row["id"] == 10847:
                            weapons.insert(4, weapons.pop(index))
                            break
            for slot in orig:
                if two_handed_only and slot == "off":
                    continue
                if slot not in slots:
                    priority = ranged if slot == "ranged" and ranged else None
                    slots[slot] = _single_items(orig[slot], new[slot], caps, priority)
                    if priority is not None:
                        slots[slot]["pointStat"] = weapon_priority.point_stat(active)
                slots[slot]["routeIterations"] = new[slot]["iterations"]
            if not damage_only and key == "DRUID 4":
                # Keep Blue Suede Hat behind the two leading alternatives for Feral Cat.
                helmets = slots["head"]["items"]
                for index, helm in enumerate(helmets[:2]):
                    if helm["id"] == 252482:
                        helmets.insert(2, helmets.pop(index))
                        break
            if not damage_only and key == "PALADIN 4":
                wrists = slots["wrist"]["items"]
                # Identical damage: prefer the bracers with additional Stamina and Spirit.
                if [row["id"] for row in wrists[:2]] == [18458, 18497] and wrists[0]["score"] == wrists[1]["score"]:
                    wrists[0], wrists[1] = wrists[1], wrists[0]
            factions[side] = slots
        result[key] = factions
    if refined != actual_refined:
        raise ValueError("Unknown refined dungeon block")
    return result
