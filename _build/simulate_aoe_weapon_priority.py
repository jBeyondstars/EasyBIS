"""Measure weapon stats, set bonuses and passive effects against matching bare weapons.

Run with --wowsims CHECKOUT --pack-cli EXE --output FILE. The checkout, CLI,
gear presets and database must be from the short-pack campaign's pinned revision.
"""
import argparse
import copy
import json
import math
import tempfile
from pathlib import Path

import aoe_weapon_priority as priority
import aoe_weapons as weapons
import simulate_aoe as pack

CLONE_OFFSET = 970_000_000
ROTATION_BLOCKS = 8
ROTATION_BLOCK_SIZE = 256
# The fields retained by the pinned native ItemFromProto loader on bare weapons.
WEAPON_FIELDS = ("type", "armorType", "weaponType", "handType", "rangedWeaponType",
                 "weaponSpeed", "qualityModifier", "spellSchool", "unique", "limitCategory", "classAllowlist")
DAMAGE_FIELDS = ("weaponDamageMin", "weaponDamageMax", "unroundedDps", "ilvl", "randPropPoints")


def neutral_request(request, slots, items):
    """Replace only the specified slots with distinct, statless native item IDs."""
    control = copy.deepcopy(request)
    player = control["raid"]["parties"][0]["players"][0]
    database = player.setdefault("database", {}).setdefault("items", [])
    reserved = {entry["id"] for entry in database}
    clones = {}
    for slot in slots:
        index = pack.EQUIPMENT_SLOTS.index(slot)
        equipped = player["equipment"]["items"][index]
        item_id = equipped.get("id", 0)
        if not item_id:
            continue
        clone_id = CLONE_OFFSET + item_id
        if clone_id in reserved or clone_id in items or clone_id > 2**31 - 1:
            raise ValueError(f"Native priority control ID collides for {item_id}")
        if item_id not in clones:
            source = items[item_id]
            clone = {k: copy.deepcopy(source[k]) for k in WEAPON_FIELDS if k in source}
            clone.update(id=clone_id, name=f"Bare control {item_id}", scalingOptions={
                level: {k: props[k] for k in DAMAGE_FIELDS if k in props}
                for level, props in source["scalingOptions"].items()
            })
            database.append(clone)
            clones[item_id] = clone_id
        equipped["id"] = clone_id
    return control


def damaging_attacks(player):
    """Count only this player's white attacks or wand shots that dealt damage."""
    present = set()
    for act in player["actions"]:
        if not any(t.get("damage", 0) > 0 for t in act["targets"]):
            continue
        action = act["id"]
        if action.get("otherId") == "OtherActionAttack":
            if action.get("tag") in (14, 15):
                present.add("main" if action["tag"] == 14 else "off")
        elif action.get("otherId") == "OtherActionShoot" or action.get("spellId") == 5019:
            present.add("ranged")
    return present


def offhand_factor(profile):
    # Native tree indices, and the per-rank off-hand damage curves of spells 13715
    # (Rogue) and 23584 (Warrior). Ordinary off-hand attacks start at half damage.
    cls = profile["class"]
    tree, pos, bonus, maximum = {"ROGUE": (1, 14, .25, 2), "WARRIOR": (1, 8, .05, 5)}[cls]
    trees = profile["player"]["talentsString"].split("-")
    ranks = trees[tree] if len(trees) > tree else ""
    rank = int(ranks[pos]) if len(ranks) > pos else 0
    if not 0 <= rank <= maximum:
        raise ValueError(f"Invalid {cls} Dual Wield Specialization rank {rank}")
    return .5 * (1 + rank * bonus)


def base_dps(profile, items, setup, actions):
    """Sheet damage of the actually attacking weapon, including its hand penalty."""
    value = 0.0
    for slot, iid in setup.items():
        if not iid or slot not in actions:
            continue
        item = items[iid]
        props = item["scalingOptions"]["0"]
        if (profile["class"], profile["spec"]) == ("DRUID", 4) and slot == "main":
            # In Forever, feralWeapon() derives paw damage from the item's table DPS.
            value += props["unroundedDps"]
            continue
        if (slot == "ranged" and profile["class"] != "HUNTER"
                and not (profile["class"] == "PRIEST" and item.get("rangedWeaponType") == 5)):
            raise ValueError(f"Unexpected active non-Hunter ranged weapon {iid}")
        speed = item["weaponSpeed"]
        dps = (props["weaponDamageMin"] + props["weaponDamageMax"]) / (2 * speed)
        value += dps * (offhand_factor(profile) if slot == "off" else 1)
    return value


def on_use(item):
    return any("onUse" in effect for effect in item.get("itemEffects", []))


def rotation_damage(result, slots, iterations, required_pet=None):
    """Mean pack damage other than the player's ordinary swings of the compared weapons."""
    pack.samples(result, iterations, {}, required_pet)
    targets = {target["unitIndex"] for target in result["encounterMetrics"]["targets"]}
    player = result["raidMetrics"]["parties"][0]["players"][0]
    ranged = "ranged" in slots
    hand_tags = {tag for slot, tag in (("main", 14), ("off", 15)) if slot in slots}
    damage = []
    for unit in (player, *player.get("pets", [])):
        for action in unit["actions"]:
            ident = action["id"]
            if unit is player:
                if ident.get("otherId") == "OtherActionAttack" and ident.get("tag") in hand_tags:
                    continue
                if ranged and (ident.get("otherId") == "OtherActionShoot" or ident.get("spellId") == 5019):
                    continue
            damage.extend(t["damage"] for t in action["targets"] if t["unitIndex"] in targets)
    return math.fsum(damage) / iterations


def add_rotation_measurements(profile, side, rotation, gear, items, record, simulate):
    """Compare bare weapon types and damage ranges using eight paired block means.

    Blocks use SEED + 256 * block, with 256 iterations each. The block means
    preserve the pairing even though native action damage is only aggregated
    over a run. Each faction and equipment scope gets its own bare reference.
    """
    n = ROTATION_BLOCK_SIZE
    baseline = pack.make_request(profile, profile["races"][side], rotation, gear, None, 0, n)
    equipped = baseline["raid"]["parties"][0]["players"][0]["equipment"]["items"]

    def blocks(slots, ids):
        request = copy.deepcopy(baseline)
        loadout = request["raid"]["parties"][0]["players"][0]["equipment"]["items"]
        for slot, iid in zip(slots, ids, strict=True):
            loadout[pack.EQUIPMENT_SLOTS.index(slot)] = {"id": iid} if iid else {}
        request = neutral_request(request, slots, items)
        means = []
        for block in range(ROTATION_BLOCKS):
            request["simOptions"]["randomSeed"] = str(priority.SEED + block * n)
            means.append(rotation_damage(simulate(request), slots, n, profile.get("requiredPet")))
        return means

    def compare(slots, reference, rows, id_fields):
        reference_means = blocks(slots, reference)
        for row in rows:
            ids = tuple(row[field] for field in id_fields)
            candidate = reference_means if ids == reference else blocks(slots, ids)
            row["rotationGain"], row["rotationSE"] = pack.difference(candidate, reference_means)

    compare(("main", "off"), tuple(profile["referenceWeapons"]), record["sets"], ("main", "off"))
    if record["ranged"]:
        ranged = equipped[pack.EQUIPMENT_SLOTS.index("ranged")].get("id", 0)
        reference = profile.get("comparisonItems", {}).get("ranged", ranged)
        compare(("ranged",), (reference,), record["ranged"], ("id",))


def measure_faction(profile, side, rotation, gear, items, simulate):
    """Measure one faction using a callable that returns standard native raid results."""
    race = profile["races"][side]
    n = priority.ITERATIONS

    def hands(main, off):
        held = {i for i in (main, off) if i and on_use(items[i])}
        return weapons.request(profile, race, rotation, gear, (main, off), n, (), held)

    def run(request):
        request["simOptions"]["randomSeed"] = str(priority.SEED)
        result = simulate(request)
        if abs(result["avgIterationDuration"] - pack.SECONDS) > .00001:
            raise ValueError("Priority measurement did not use the 15-second encounter")
        values = pack.samples(result, n, {}, profile.get("requiredPet"))[0]
        player = result["raidMetrics"]["parties"][0]["players"][0]
        return values, damaging_attacks(player)

    control = hands(*profile["referenceWeapons"])
    base, _ = run(control)
    unit = priority.point_stat(profile)
    player = control["raid"]["parties"][0]["players"][0]
    bonus = player.setdefault("bonusStats", {}).setdefault("stats", [])
    stat_index = pack.eligibility.STAT_IDS[unit][0]
    bonus.extend([0] * max(0, stat_index + 1 - len(bonus)))
    bonus[stat_index] += 100
    boosted, _ = run(control)
    gain, error = pack.difference(boosted, base)
    if gain <= 3 * error:
        raise ValueError(f"{profile['class']} {side}: unsupported +100 {unit} control, {gain} +/- {error}")
    proof = {"pointStat": unit, "controlGain": gain, "controlSE": error, "sets": [], "ranged": []}

    def measure(request, setup):
        complete, attacks = run(request)
        bare, _ = run(neutral_request(request, setup, items))
        delta, se = pack.difference(complete, bare)
        return {"baseDps": base_dps(profile, items, setup, attacks), "gain": delta, "se": se}

    for main, off in profile["weaponSets"]:
        pair = {"main": main, "off": off}
        proof["sets"].append({**pair, **measure(hands(main, off), pair)})
    if profile["class"] not in priority.RELIC_CLASSES:
        for iid in profile["slots"]["ranged"]:
            request = pack.make_request(profile, race, rotation, gear, "ranged", iid, n,
                                        on_use=on_use(items[iid]), passive_only=True)
            proof["ranged"].append({"id": iid, **measure(request, {"ranged": iid})})
    return proof


def campaign(root, exe, work):
    revision = pack.revision(root)
    client = pack.fdb.load(pack.HERE / "cache" / "ForeverDB")
    ranked = pack.eligibility.ranked_specs(client)
    native = {item["id"]: item for name in ("leftover_db.json", "db.json")
              for item in pack.read(root / "assets/database" / name)["items"]}
    records = {}
    for path in sorted(pack.PROFILES.glob("*.json")):
        profile = pack.read(path)
        key = f"{profile['class']} {profile['spec']}"
        if key not in ranked:
            continue
        rot_path = (pack.PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile
                    else root / profile["rotation"])
        rotation = pack.read_preset(root, exe, rot_path)
        gear = pack.reference_equipment(root, exe, profile)
        pack.validate_equipment(profile, gear, native, client.items, client.gear)
        weapons.validate_profile(profile, gear, native, client)
        record = {"profileSha256": pack.eligibility.profile_digest(profile, pack.PROFILES), "factions": {}}
        for side in profile["races"]:
            def simulate(request):
                return pack.run_request(exe, work, request)

            faction = measure_faction(profile, side, rotation, gear, native, simulate)
            add_rotation_measurements(profile, side, rotation, gear, native, faction, simulate)
            record["factions"][side] = faction
        records[key] = record
    if set(records) != ranked:
        raise ValueError("Incomplete priority campaign")
    return {"wowsims": revision, "seed": priority.SEED, "iterations": priority.ITERATIONS,
            "sourceSha256": priority.generator_hash(), "requestSourceSha256": priority.request_source_hashes(),
            "specs": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wowsims", type=Path, required=True)
    parser.add_argument("--pack-cli", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        archive = campaign(args.wowsims.resolve(), args.pack_cli.resolve(), Path(tmp))
    with tempfile.NamedTemporaryFile("w", dir=args.output.parent, encoding="utf-8",
                                     newline="\n", delete=False) as temp:
        json.dump(archive, temp, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        temp.write("\n")
    Path(temp.name).replace(args.output)
