"""Continuous level-60 dungeon route and native per-iteration damage samples."""
import json
import math
import statistics
from pathlib import Path

SOURCE = Path(__file__).parent / "aoe/dungeon_route.go"
ELITE_HP = 7500
NORMAL_HP = 2500
GROUP_DPS = 1500
TRAVEL_SECONDS = 2
TIME_LIMIT = 90
GROUP_SPELL_ID = 900070
DRINK_SPELL_ID = 900071
PACKS = ((ELITE_HP,) * 4, (3 * ELITE_HP,), (ELITE_HP,) * 3 + (NORMAL_HP,) * 4)


def encounter():
    targets = []
    for pack, healths in enumerate(PACKS, 1):
        for index, health in enumerate(healths, 1):
            kind = "normal" if health == NORMAL_HP else "elite"
            stats = [0] * 30
            stats[27], stats[29] = 3000, health
            targets.append({"id": 900010 + len(targets), "name": f"Pack {pack} {kind} {index}",
                            "level": 60, "mobType": "MobTypeHumanoid", "stats": stats, "tankIndex": -1,
                            "disabledAtStart": pack != 1, "targetInputs": [
                                {"numberValue": pack}, {"numberValue": GROUP_DPS}, {"numberValue": TRAVEL_SECONDS},
                                {"numberValue": 1}]})
    return {"duration": TIME_LIMIT, "durationVariation": 0, "targets": targets}


def write_overlay(root, work):
    """Patch the native damage delivery hook in the build directory only."""
    root, work = Path(root).resolve(), Path(work).resolve()
    core = root / "sim/core"
    original = core / "spell_result.go"
    signature = "func (spell *Spell) dealDamageInternal(sim *Simulation, isPeriodic bool, result *SpellResult) {"
    source = original.read_text(encoding="utf8")
    if source.count(signature) != 1:
        raise ValueError("WoWSims damage delivery changed; verify the route impact hook")
    patched = work / "route_spell_result.go"
    patched.write_text(source.replace(signature, signature + """
	if !routeImpact(sim, spell, result) {
		spell.DisposeResult(result)
		return
	}
"""), encoding="utf8")
    overlay = work / "route_overlay.json"
    overlay.write_text(json.dumps({"Replace": {str(core / "easybis_route.go"): str(SOURCE.resolve()),
                                               str(original): str(patched)}}), encoding="utf8")
    return overlay


def route_samples(result, iterations):
    if result.get("error") or result.get("iterationsDone") != iterations:
        raise ValueError(f"Incomplete dungeon route: {result.get('error') or result.get('iterationsDone')}")
    targets = result["encounterMetrics"]["targets"]
    if len(targets) != sum(map(len, PACKS)) or len({t["unitIndex"] for t in targets}) != len(targets):
        raise ValueError("Dungeon route requires twelve distinct enemies")
    clock = targets[0]["threat"].get("allValues", [])
    rates = result["raidMetrics"]["dps"].get("allValues", [])
    if len(clock) != iterations or len(rates) != iterations or any(x <= 0 or not math.isfinite(x) for x in clock):
        raise ValueError("Missing dungeon completion or per-iteration damage samples")
    durations = [1 / value for value in clock]
    if max(durations) >= TIME_LIMIT or not math.isclose(statistics.mean(durations), result["avgIterationDuration"],
                                                       rel_tol=1e-8, abs_tol=1e-7):
        raise ValueError("Dungeon completion times differ from native iteration durations")
    damage = [rate * duration for rate, duration in zip(rates, durations, strict=True)]
    if any(not math.isfinite(v) or v < 0 for v in damage):
        raise ValueError("Invalid dungeon damage")
    player = result["raidMetrics"]["parties"][0]["players"][0]
    by_target = {target["unitIndex"]: 0.0 for target in targets}
    for unit in (player, *player.get("pets", [])):
        for action in unit.get("actions", []):
            for hit in action["targets"]:
                index = hit["unitIndex"]
                if index in by_target:
                    by_target[index] += hit["damage"]
    for target, config in zip(targets, encounter()["targets"], strict=True):
        if target["name"] != config["name"]:
            raise ValueError("Unexpected dungeon target order")
        credited = by_target[target["unitIndex"]]
        group_damage = -sum(row.get("actualGain", 0) for row in target.get("resources", [])
                            if row["id"].get("spellId") == GROUP_SPELL_ID)
        expected = config["stats"][29] * iterations
        if not math.isclose(credited + group_damage, expected, rel_tol=1e-8, abs_tol=0.001):
            raise ValueError(f"{target['name']}: player and allied damage do not account for its health")
    if not math.isclose(statistics.mean(damage), sum(by_target.values()) / iterations, rel_tol=1e-8, abs_tol=0.001):
        raise ValueError("Dungeon samples do not match credited player and pet actions")
    return damage, durations
