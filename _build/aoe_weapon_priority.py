"""Weapon recommendation points, separate from the measured dungeon damage percentages."""
import hashlib
import math
from pathlib import Path

import aoe_eligibility
import ladders

ITERATIONS = 2048
SEED = 118042
POWER_PER_DPS = 14
# Recommendation policy: keep full intrinsic weapon value and give half weight to the
# rotation-dependent adjustment. The scenario damage percentages use the full measurements.
ROTATION_WEIGHT = 0.5
MELEE_CLASSES = {"WARRIOR", "ROGUE", "PALADIN"}
RELIC_CLASSES = {"DRUID", "PALADIN", "SHAMAN"}


def point_stat(profile):
    cls = profile["class"]
    if cls == "HUNTER":
        return "rap"
    if cls in MELEE_CLASSES or (cls, profile["spec"]) in (("DRUID", 4), ("SHAMAN", 2)):
        return "ap"
    return "spell"


def generator_hash():
    source = Path(__file__).with_name("simulate_aoe_weapon_priority.py").read_text(encoding="utf-8")
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def request_source_hashes():
    root = Path(__file__).parent
    return {name: hashlib.sha256((root / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
            for name in ("simulate_aoe.py", "aoe_weapons.py", "aoe_references.py", "aoe_eligibility.py")}


def validate_campaign(archive, short):
    if (archive.get("wowsims") != short["wowsims"] or archive.get("seed") != SEED
            or archive.get("iterations") != ITERATIONS or archive.get("sourceSha256") != generator_hash()
            or archive.get("requestSourceSha256") != request_source_hashes()
            or set(archive.get("specs", {})) != set(short["specs"])):
        raise ValueError("Weapon priority measurements do not match the simulator, seed, generator or profiles")


def validate_profile(archive, profile, directory):
    if (archive.get("profileSha256") != aoe_eligibility.profile_digest(profile, directory)
            or set(archive.get("factions", {})) != set(profile["races"])):
        raise ValueError("Weapon priority uses a stale profile or an incomplete faction list")


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _equivalent_points(gain, se, control_gain):
    if not _finite(gain) or not _finite(se) or se < 0:
        raise ValueError("Invalid paired weapon priority estimate")
    return 100 * gain / control_gain if abs(gain) > 3 * se else 0


def _points(proof, fields, expected, control_gain, has_weapon_damage, reference):
    result = {}
    for row in proof:
        key = tuple(row.get(k) for k in fields)
        if (any(type(i) is not int for i in key) or key not in expected or key in result
                or ladders.DISQUALIFIED_ITEMS.intersection(key)):
            raise ValueError(f"Invalid or duplicate weapon priority configuration {key}")
        if key == reference and (row.get("rotationGain") != 0 or row.get("rotationSE") != 0):
            raise ValueError(f"Weapon rotation reference must have zero gain and error for {key}")
        dps = row.get("baseDps")
        if not _finite(dps) or dps < 0 or (not has_weapon_damage and dps != 0):
            raise ValueError(f"Invalid base weapon damage for {key}")
        base = POWER_PER_DPS * dps
        # Real vs bare isolates item bonuses. Bare vs bare isolates the change in rotation damage
        # when switching weapons. Ordinary swings of the compared slot already have base DPS points.
        bonuses = _equivalent_points(row.get("gain"), row.get("se"), control_gain)
        rotation = ROTATION_WEIGHT * _equivalent_points(row.get("rotationGain"), row.get("rotationSE"), control_gain)
        result[key] = {"weaponPriority": base + bonuses + rotation, "weaponBasePoints": base,
                       "weaponBonusPoints": bonuses, "weaponRotationPoints": rotation}
    if set(result) != expected:
        raise ValueError("Missing weapon priority measurements for eligible candidates")
    return result


def ratings(profile, side):
    unit = point_stat(profile)
    gain, se = side.get("controlGain"), side.get("controlSE")
    if (side.get("pointStat") != unit or not all(_finite(n) for n in (gain, se)) or se < 0 or gain <= 3 * se):
        raise ValueError("Weapon priority requires a significant calibration for the specialization")
    pairs = {tuple(pair) for pair in profile["weaponSets"]}
    hands = _points(side["sets"], ("main", "off"), pairs, gain, unit == "ap", tuple(profile.get("referenceWeapons", ())))
    cls = profile["class"]
    ranged = set() if cls in RELIC_CLASSES else {(i,) for i in profile["slots"]["ranged"]}
    ranged_reference = profile.get("comparisonItems", {}).get("ranged", profile.get("referenceItems", {}).get("ranged"))
    missiles = _points(side.get("ranged", []), ("id",), ranged, gain, cls == "HUNTER", (ranged_reference,))
    return hands, missiles
