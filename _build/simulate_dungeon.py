"""Measure the damage of pre-raid loadouts over the continuous three-pull route.

    python _build/simulate_dungeon.py --wowsims PATH --work CHECKPOINT_DIRECTORY

Run with the Go toolchain and generated protobufs of the short archive's checkout.
Completed slot comparisons are reusable only for identical requests and native code.
The default publication first measures a 1,024-route selection pilot. Production
uses a disjoint seed range and measures close combined leaders on 4,096 routes.
"""

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aoe_encounter as route
import aoe_dungeon_precision
import aoe_jewelry
import aoe_route_rotation
import aoe_weapons as weapons
import simulate_aoe as short

HERE = short.HERE
SEED = 42430
PILOT_SEED = 4243
REFINEMENT_ITERATIONS = 4096
NATIVE = "aoe/dungeon_batch.go"
EFFECT_REPLAY = "aoe/dungeon_effects.go"
SCENARIO_FILES = ("aoe_encounter.py", "aoe/dungeon_route.go", NATIVE)


def schedule():
    packs = [
        {
            "elites": sum(h != route.NORMAL_HP for h in hp),
            "normal": hp.count(route.NORMAL_HP),
            "health": list(hp),
        }
        for hp in route.PACKS
    ]
    return {
        "packs": packs,
        "travelSeconds": route.TRAVEL_SECONDS,
        "manaBetweenPacks": "full",
        "partyDps": route.GROUP_DPS,
        "level": short.LEVEL,
        "armor": 3000,
    }


def digest(data):
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def source_hashes():
    return {
        name: hashlib.sha256((HERE / name).read_text(encoding="utf-8").encode()).hexdigest()
        for name in (
            *SCENARIO_FILES, EFFECT_REPLAY, "aoe_jewelry.py",
            "aoe_route_rotation.py",
            "aoe_dungeon_precision.py",
            "simulate_dungeon.py",
            "simulate_aoe.py",
            "aoe_weapons.py",
            "aoe_references.py",
            "aoe_eligibility.py",
        )
    }


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", newline="\n", delete=False) as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        fh.write("\n")
    Path(fh.name).replace(path)


def bind_request(req, profile, root, active, wave, seed):
    player = req["raid"]["parties"][0]["players"][0]
    apl = player["rotation"]
    if wave:
        # Claim every explicitly requested use so the preset cannot use it sooner.
        actions = {i: None for i in active}
        for entries in [apl["priorityList"], *(g["actions"] for g in apl.get("groups", []))]:
            kept = []
            for row in entries:
                act = row.get("action", {})
                iid = act.get("castSpell", {}).get("spellId", {}).get("itemId")
                if iid not in actions:
                    kept.append(row)
                elif actions[iid] is None:
                    actions[iid] = act
            entries[:] = kept
        gate = {
            "targetIsActive": {
                "targetUnit": {"type": "Target", "index": sum(map(len, route.PACKS[: wave - 1]))}
            }
        }
        for iid in reversed(active):
            act = actions[iid]
            if act is None:
                raise ValueError(f"Missing active item {iid} in APL")
            cond = act.get("condition")
            act["condition"] = {"and": {"vals": [cond, gate]}} if cond else gate
            apl["priorityList"].insert(0, {"action": act})
    player["rotation"] = aoe_route_rotation.route_rotation(profile, apl, root)
    req["encounter"] = route.encounter()
    req["simOptions"]["randomSeed"] = str(seed)
    return req


def variants(root, profile, race, rot, gear, slot, config, n, items, seed):
    pair = isinstance(config, tuple)
    equipped = config if pair else (config,)
    effects = {
        i: {fx["buffId"] for fx in items[i].get("itemEffects", []) if "onUse" in fx} for i in equipped if i
    }
    usable = tuple(i for i, buffs in effects.items() if buffs)
    offensive = tuple(
        i
        for i in usable
        if (
            effects[i] - weapons.UTILITY_EFFECTS
            if pair
            else i not in short.eligibility.PASSIVE_ITEM_ACTIVATIONS
        )
    )
    choices = [((), 0, 0)]
    for count in range(1, len(offensive) + 1):
        for active in itertools.combinations(offensive, count):
            choices.extend((active, 0, wave) for wave in (0, 2, 3))
            if 8348 in active:
                choices.extend((active, at, 0) for at in (3, 6, 9, 12))
    for active, after, wave in choices:
        if pair:
            req = weapons.request(profile, race, rot, gear, config, n, active, set(usable) - set(active))
        else:
            req = short.make_request(
                profile, race, rot, gear, slot, config, n, bool(usable), bool(usable) and not active, after
            )
        yield (
            {"activation": list(active), "useAfterSeconds": after, "usePack": wave},
            {"Watch": usable, "Request": bind_request(req, profile, root, active, wave, seed)},
        )


def measure_options(options, observations):
    passive = observations[0]["Damage"]
    best, best_gain = 0, 0
    proofs = []
    for pos, (opt, obs) in enumerate(zip(options, observations, strict=True)):
        if obs.get("Error"):
            raise ValueError(obs["Error"])
        casts = {i: v for i, v in obs["Casts"].items() if v}
        if set(map(int, casts)) - set(opt["activation"]):
            raise ValueError(f"Unrequested item activated: {casts} vs {opt}")
        gain, se = short.difference(obs["Damage"], passive)
        proofs.append(
            {
                **opt,
                "gain": round(gain, 4),
                "se": round(se, 4),
                "usesPerRun": {k: round(v, 6) for k, v in casts.items()},
            }
        )
        if casts and set(map(int, casts)) == set(opt["activation"]) and gain > 3 * se and gain > best_gain:
            best, best_gain = pos, gain
    obs = observations[best]
    info = {
        "packDamage": [round(x, 4) for x in obs["PackDamage"]],
        "packHits": obs["PackHits"],
        "avgSeconds": round(obs["Seconds"], 6),
    }
    if obs["PetDamage"]:
        info["petDamage"] = round(obs["PetDamage"], 4)
    if "ManaRestored" in obs:
        info["manaRestored"] = [round(v, 4) for v in obs["ManaRestored"]]
        info["manaRefillEvents"] = obs["ManaRefillEvents"]
    if len(options) > 1 or options and observations[0]["Casts"]:
        info.update(
            activation=proofs[best]["activation"],
            usesPerRun=proofs[best]["usesPerRun"],
            usePack=proofs[best]["usePack"],
            useAfterSeconds=proofs[best]["useAfterSeconds"],
            activationTrials=proofs,
        )
    return obs["Damage"], info


def rows_for(configs, result, baseline, key):
    ordered = sorted(configs, key=lambda c: (-statistics.mean(result[c][0]), c))
    seen = set()
    rows, previous = [], None
    for config in ordered:
        iid, partner = key(config)
        if not iid or iid in seen:
            continue
        seen.add(iid)
        values, details = result[config]
        gain, se = short.difference(values, baseline)
        row = {"id": iid, "gain": round(gain, 4), "se": round(se, 4), **details}
        if partner is not None:
            row["partner"] = partner
        if previous is not None:
            gap, error = short.difference(previous, values)
            row.update(gap=round(gap, 4), gapSE=round(error, 4))
        rows.append(row)
        previous = values
    return rows


def block(root, runner, work, profile, side, rot, gear, slot, n, items, signature, workers, seed):
    pair = slot == "main"
    configs = [tuple(p) for p in profile["weaponSets"]] if pair else profile["slots"][slot]
    reference = tuple(profile["referenceWeapons"]) if pair else 0
    keys = list(dict.fromkeys([reference, *configs]))
    options, requests = {}, []
    for config in keys:
        plans = list(variants(root, profile, profile["races"][side], rot, gear, slot, config, n, items, seed))
        options[config] = [info for info, _ in plans]
        requests.extend(req for _, req in plans)
    payload = {
        "Trials": requests,
        "Mana": profile["class"] not in ("ROGUE", "WARRIOR"),
        "Packs": [len(p) for p in route.PACKS],
        "Pet": profile.get("requiredPet", ""),
    }
    fingerprint = digest([signature, payload])
    path = work / "blocks" / (profile["class"] + str(profile["spec"])) / side / (slot + ".json")
    if path.exists():
        checkpoint = short.read(path)
        if checkpoint["signature"] == fingerprint:
            return checkpoint["blocks"]
    run = subprocess.run(
        [runner],
        input=json.dumps(payload),
        capture_output=True,
        encoding="utf-8",
        env={**os.environ, "GOMAXPROCS": str(workers)},
    )
    if run.returncode:
        raise RuntimeError(f"{profile['class']} {slot}: {run.stderr[-3000:]}")
    obs = json.loads(run.stdout)
    if len(obs) != len(requests):
        raise RuntimeError("Incomplete route batch")
    result, offset = {}, 0
    for config in keys:
        count = len(options[config])
        try:
            result[config] = measure_options(options[config], obs[offset : offset + count])
        except ValueError as error:
            raise ValueError(f"{profile['class']} {profile['spec']} {side} {slot} {config}: {error}") from error
        offset += count
    samples, details = result[reference]
    base = {
        "iterations": n,
        "baseline": round(statistics.mean(samples), 4),
        "baselinePackDamage": details["packDamage"],
        "baselinePackHits": details["packHits"],
        "baselineAvgSeconds": details["avgSeconds"],
    }
    if "petDamage" in details:
        base["baselinePetDamage"] = details["petDamage"]
    if "manaRestored" in details:
        base["baselineManaRestored"] = details["manaRestored"]
        base["baselineManaRefillEvents"] = details["manaRefillEvents"]
    if pair:
        base["referenceWeapons"] = list(reference)
        blocks = {
            name: {**base, "items": rows_for(configs, result, samples, lambda c: (c[pos], c[1 - pos]))}
            for pos, name in enumerate(("main", "off"))
            if name in profile["slots"]
        }
        measured = []
        for main, off in configs:
            values, info = result[main, off]
            delta, error = short.difference(values, samples)
            measured.append({"main": main, "off": off, "gain": round(delta, 4), "se": round(error, 4), **info})
        blocks["main"]["setMeasurements"] = measured
    else:
        if slot in short.PAIRED_SLOTS:
            base["pairedItem"] = short.references.paired_item(profile, side, slot)
        if slot in profile.get("comparisonItems", {}):
            base["comparisonItem"] = profile["comparisonItems"][slot]
        blocks = {slot: {**base, "items": rows_for(configs, result, samples, lambda i: (i, None))}}
    save(path, {"signature": fingerprint, "blocks": blocks})
    return blocks


def record_trinket_effects(root, runner, profile, side, rot, gear, items, seed, block):
    """Prove conditional procs using the same native trial, seeds, and serial iteration order as the batch."""
    watched = profile.get("routeOnlyTrinkets", [])
    if not watched:
        return
    iterations = block["iterations"]
    def replay(item_id):
        plans = list(variants(root, profile, profile["races"][side], rot, gear, "trinket", item_id,
                              iterations, items, seed))
        if len(plans) != 1 or plans[0][0]["activation"]:
            raise ValueError(f"Expected a passive dungeon trinket for replay: {item_id}")
        run = subprocess.run([runner], input=json.dumps(plans[0][1]["Request"]), capture_output=True,
                             encoding="utf-8", check=True)
        result = json.loads(run.stdout)
        return result, route.route_samples(result, iterations)[0]

    _, reference = replay(0)
    if round(statistics.mean(reference), 4) != block["baseline"]:
        raise ValueError("Dungeon trinket replay differs from the archived baseline")
    rows = {row["id"]: row for row in block["items"]}
    for item_id in watched:
        row = rows[item_id]
        result, values = replay(item_id)
        gain, se = short.difference(values, reference)
        if (round(gain, 4), round(se, 4)) != (row["gain"], row["se"]):
            raise ValueError(f"Dungeon trinket replay differs from the measured gain for {item_id}")
        proof = aoe_jewelry.dungeon_effect(item_id, result, [len(pack) for pack in route.PACKS])
        row["routeEffect"] = dict(proof, meanDamage=round(statistics.mean(values), 4), pairedSE=round(se, 4))
        aoe_jewelry.validate_dungeon_effect(row, block["baseline"])


def campaign(root, work, output, n, jobs, workers, names=(), only_slots=(), pilot_path=None, seed=SEED):
    root, work = root.resolve(), work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    archive = short.read(HERE / "corrections/aoe.json")
    client = short.fdb.load(HERE / "cache/ForeverDB")
    if set(archive["specs"]) != short.eligibility.ranked_specs(client):
        raise ValueError("Short archive must cover the current damage specializations")
    refined = set()
    if pilot_path is not None:
        pilot = short.read(pilot_path)
        if (
            pilot["wowsims"] != archive["wowsims"]
            or pilot["shortArchiveSha256"] != digest(archive)
            or pilot["seed"] != PILOT_SEED
            or pilot["schedule"] != schedule()
            or pilot["scenarioSha256"] != digest(schedule())
            or pilot["sourceSha256"] != source_hashes()
            or pilot["iterations"] != 1024
            or set(pilot["specs"]) != set(archive["specs"])
        ):
            raise ValueError("Pilot campaign differs from the intended dungeon scenario")
        refined = aoe_dungeon_precision.refinement_blocks(archive, pilot)
    revision = short.revision(root)
    if archive["wowsims"] != revision:
        raise ValueError("Short encounter and dungeon must use the same WoWSims revision")
    hashes = source_hashes()
    signature = [revision, schedule(), {f: hashes[f] for f in SCENARIO_FILES}, hashes["simulate_dungeon.py"]]
    overlay = route.write_overlay(root, work)
    suffix = ".exe" if os.name == "nt" else ""
    runner, cli = work / ("route-batch" + suffix), work / ("route-cli" + suffix)
    for out, source in [(runner, HERE / NATIVE), (cli, "./cmd/wowsimcli")]:
        short.build_native(root, overlay, out, source)
    items = {
        it["id"]: it
        for file in ("leftover_db.json", "db.json")
        for it in short.read(root / "assets/database" / file)["items"]
    }
    profiles = {}
    for key, rec in archive["specs"].items():
        path = short.PROFILES / rec["profile"]
        if names and path.stem not in names:
            continue
        p = short.read(path)
        digest_profile = short.eligibility.profile_digest(p, short.PROFILES)
        if rec["profileSha256"] != digest_profile:
            raise ValueError(f"Profile {path} differs from short encounter")
        gear = short.reference_equipment(root, cli, p)
        short.validate_equipment(p, gear, items, client.items, client.gear)
        weapons.validate_profile(p, gear, items, client)
        rot_path = short.PROFILES / p["dungeonRotation"] if "dungeonRotation" in p else root / p["rotation"]
        rot = short.read_preset(root, cli, rot_path)
        if (
            rec["inputsSha256"]
            != hashlib.sha256(json.dumps([p, rot, gear], sort_keys=True).encode()).hexdigest()
        ):
            raise ValueError(f"Reference gear or base rotation for {path} differs from short encounter")
        profiles[key] = (p, rot, gear)
    if not profiles:
        raise ValueError("No matching profiles")
    effect_runner = work / ("route-effects" + suffix)
    if (not only_slots or "trinket" in only_slots) and any(p.get("routeOnlyTrinkets") for p, _, _ in profiles.values()):
        short.build_native(root, overlay, effect_runner, HERE / EFFECT_REPLAY)
    records = {
        key: {"profileSha256": archive["specs"][key]["profileSha256"], "factions": {"a": {}, "h": {}}}
        for key in profiles
    }
    tasks = [
        (key, side, slot)
        for key, (p, _, _) in profiles.items()
        for side in p["races"]
        for slot in p["slots"]
        if slot != "off" and (not only_slots or slot in only_slots)
    ]

    def run(task):
        key, side, slot = task
        p, rot, gear = profiles[key]
        count = REFINEMENT_ITERATIONS if task in refined else n
        blocks = block(root, runner, work, p, side, rot, gear, slot, count, items, signature, workers, seed)
        if slot == "trinket":
            record_trinket_effects(root, effect_runner, p, side, rot, gear, items, seed, blocks[slot])
        return key, side, blocks

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for key, side, blocks in pool.map(run, tasks):
            records[key]["factions"][side].update(blocks)
    refined_names = sorted(
        f"{key}/{side}/{slot}"
        for key, side, group in refined
        if (key, side, group) in tasks
        for slot in (("main", "off") if group == "main" and "off" in profiles[key][0]["slots"] else (group,))
    )
    result = {
        "mode": "dungeon",
        "metric": "dungeonDamage",
        "seed": seed,
        "iterations": n,
        "wowsims": revision,
        "schedule": schedule(),
        "scenarioSha256": digest(schedule()),
        "sourceSha256": hashes,
        "pilotSeed": PILOT_SEED,
        "refinementIterations": REFINEMENT_ITERATIONS,
        "refinedBlocks": refined_names,
        "shortArchiveSha256": digest(archive),
        "specs": records,
    }
    if output.resolve() == (HERE / "corrections/aoe_dungeon.json").resolve() and (
        names or only_slots or n < 1024 or seed != SEED or set(records) != set(archive["specs"])
    ):
        raise ValueError("Publication requires all active profiles and slots, and 1024 iterations")
    save(output, result)
    print(f"Saved {len(tasks)} dungeon comparisons to {output}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wowsims", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=HERE / "corrections/aoe_dungeon.json")
    parser.add_argument("--iterations", type=int, default=1024)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--profiles", nargs="+", default=[])
    parser.add_argument("--slots", nargs="+", default=[])
    parser.add_argument("--pilot", type=Path, help="Complete 1,024-run pilot archive for adaptive precision")
    parser.add_argument("--seed", type=int, default=SEED, help="Use 4243 when generating the selection pilot")
    args = parser.parse_args()
    if min(args.jobs, args.workers) < 1 or args.iterations < 2:
        parser.error("Use positive worker counts and at least two iterations")
    if (
        args.pilot is None
        and args.output.resolve() == (HERE / "corrections/aoe_dungeon.json").resolve()
        and args.iterations == 1024
        and not args.profiles
        and not args.slots
    ):
        args.pilot = args.work / "selection-pilot.json"
        campaign(args.wowsims, args.work / "pilot", args.pilot, 1024, args.jobs, args.workers, seed=PILOT_SEED)
    campaign(
        args.wowsims,
        args.work,
        args.output,
        args.iterations,
        args.jobs,
        args.workers,
        args.profiles,
        args.slots,
        args.pilot,
        args.seed,
    )
