"""Offensive effects and fixed partners for AOE ring and trinket comparisons."""
import json
import math
from pathlib import Path


_data = json.loads((Path(__file__).parent / "corrections/aoe_trinkets.json").read_text(encoding="utf-8"))
ADDITIONAL_TRINKETS = {int(item_id): item for item_id, item in _data["items"].items()}


def include_trinkets(db):
    """Provide verified acquisition and tooltip facts for the AOE pool only."""
    for item_id, record in ADDITIONAL_TRINKETS.items():
        db.items.setdefault(item_id, {"name": record["name"], "groups": frozenset(record["group"]),
                            "side": "", "flags": "U", "twin": None, "limit": None, "sources": record["sources"]})
        db.gear.setdefault(item_id, {"inv": 12, "kind": "4.0", "req": record["level"],
                                    "stats": {int(k): v for k, v in record["stats"].items()},
                                    "dps": 0.0, "wand": False, "armor": 0.0})

# WoWSims Forever's game-file effects. These pieces have no passive offensive stat.
# The Emblem procs spell power on harmful spell hits, Flame Lash on weapon hits,
# and the Flamebreak Talisman grants agility on use.
EFFECTS = {19289: 23687, 22268: 1318930, 22321: 27655, 280032: 1311505, 280071: 1315878}
# The pinned simulator does not implement these summons, power-cost changes or charged effects.
UNMODELED_ACTIVATIONS = {11832, 13382, 19991, 19992, 20036, 276744, 277559}


def validate_candidate(profile, item_id, stats):
    import aoe_eligibility as rules

    key = f"{profile['class']} {profile['spec']}"
    caster = key in rules.CASTER_SCHOOLS
    melee = not caster or key in rules.HYBRID_MELEE
    if item_id in UNMODELED_ACTIVATIONS:
        raise ValueError(f"{key}: unmodeled offensive or resource activation on {item_id}")
    if item_id == 19289 and not stats and profile["class"] in ("WARRIOR", "ROGUE"):
        return  # Darkmoon Card: Maelstrom triggers from melee swings and specials.
    if key in rules.MELEE_PRIORITY:
        # Blackhand's Breadth gives melee crit via a passive aura, Heart of Wyrmthalak
        # procs on weapon hits, and Flamebreak Talisman grants agility on use.
        if item_id in (13965, 22321, 280071) and not stats:
            return
        return rules.validate_candidate(profile, item_id, stats)
    if (item_id == 280032 or (item_id in (13968, 22268) and caster)
            or (item_id in (13965, 22321, 280071) and melee)):
        if not stats:
            return
    if item_id == 249469 and not {"frost", "shadow"}.intersection(rules.item_schools(profile, item_id)):
        raise ValueError(f"{key}: item {item_id} boosts Frost and Shadow damage")
    # Hit, crit and haste on jewelry are shared ratings in Forever.
    if caster and stats.keys() <= {"hit", "crit", "haste"} and stats:
        return
    rules.validate_candidate(profile, item_id, stats)


def validate_pair_ids(slot, item, partner, category, partner_category):
    if item == partner or category and category == partner_category:
        raise ValueError(f"{slot}: {item} conflicts with the fixed partner {partner}")
    if {item, partner} <= {13965, 13966, 13968}:
        raise ValueError(f"{slot}: both {item} and {partner} require the same quest reward choice")


def validate_pair(profile, slot, item, companion, side=None):
    import aoe_references
    if not companion or aoe_references.paired_item(profile, side, slot) != companion.get("id"):
        raise ValueError(f"{slot}: missing or inconsistent fixed partner")
    validate_pair_ids(slot, item["id"], companion["id"], item.get("limitCategory"), companion.get("limitCategory"))
    facts = ADDITIONAL_TRINKETS.get(item["id"])
    if facts:
        pseudo = {str(i): v for i, v in enumerate(item.get("pseudoStats", [])) if v}
        if (facts["pseudoStats"] != pseudo or facts["level"] != item.get("reqLvl", 0)
                or sorted(facts["effects"]) != sorted(fx["buffId"] for fx in item.get("itemEffects", []))):
            raise ValueError(f"{slot}: native effects or critical strike bonuses changed for {item['id']}")
    for piece in (item, companion):
        effect = EFFECTS.get(piece["id"])
        if effect and not any(fx.get("buffId") == effect for fx in piece.get("itemEffects", [])):
            raise ValueError(f"{slot}: missing offensive effect {effect} on {piece['id']}")


def measured_buff(item_id, player, inactive=False):
    """The Emblem registers its proc under the spell ID, the Talisman under the item ID."""
    if item_id not in (22268, 280071):
        return {}
    field, action_id = ("itemId", item_id) if item_id == 280071 else ("spellId", EFFECTS[item_id])
    aura = next((a for a in player.get("auras", []) if a["id"].get(field) == action_id), {})
    if not aura:
        raise ValueError(f"Missing native offensive aura for item {item_id}")
    evidence = {"spellId": EFFECTS[item_id], "procsPerPack": round(aura.get("procsAvg", 0), 6),
                "secondsPerPack": round(aura.get("uptimeSecondsAvg", 0), 6)}
    validate_buff(item_id, evidence, inactive)
    return {"offensiveBuff": evidence}


def validate_buff(item_id, evidence, inactive=False):
    if inactive and item_id == 22268:
        if evidence != {"spellId": EFFECTS[22268], "procsPerPack": 0, "secondsPerPack": 0}:
            raise ValueError("Expected a registered Draconic Infused Emblem with zero short-pack procs")
        return
    if item_id in (22268, 280071) and (
        not evidence or evidence.get("spellId") != EFFECTS[item_id]
        or not 0 < evidence.get("procsPerPack", 0) < float("inf")
        or not 0 < evidence.get("secondsPerPack", 0) <= 15
    ):
        raise ValueError(f"Item {item_id} did not apply its offensive buff during the pack")


def validate_row(item_id, row, route_only=False):
    if route_only and (item_id not in (22268, 280032) or row["gain"] != 0 or row["se"] != 0):
        raise ValueError(f"Unexpected short-pack damage for dungeon-only effect {item_id}")
    if item_id == 280071 and row.get("usesPerRun") == 0:
        trial = row.get("activeTrial", {})
        delta, error = trial.get("gainOverPassive"), trial.get("seOverPassive")
        active, passive = row.get("activeGain"), row.get("passiveGain")
        if (not all(type(v) in (float, int) and math.isfinite(v) for v in (delta, error, active, passive))
                or error < 0 or delta > 3 * error + 0.0002 or not math.isclose(active - passive, delta, abs_tol=0.0002)
                or not 0 < trial.get("usesPerRun", 0) <= 1 or "offensiveBuff" in row):
            raise ValueError("Invalid passive Talisman result or missing activation trial")
        validate_buff(item_id, trial.get("offensiveBuff"))
    else:
        validate_buff(item_id, row.get("offensiveBuff"), inactive=route_only)
    spell = {22321: "27655", 280032: "1315996"}.get(item_id)
    if spell:
        hits = row.get("targetsHitPerPack", {}).get(spell, [])
        if route_only and item_id == 280032 and hits == [0]:
            return
        if route_only:
            raise ValueError(f"Expected zero short-pack targets for dungeon-only effect {item_id}")
        if len(hits) != 1 or type(hits[0]) is not int or not 1 <= hits[0] <= 4:
            raise ValueError(f"Item {item_id} has no measured damage from spell {spell} on the pack")


def dungeon_effect(item_id, result, pack_sizes):
    """Read the proc from the wearer and damage from encounters' actual enemy IDs."""
    player = result["raidMetrics"]["parties"][0]["players"][0]
    if item_id == 22268:
        aura = next((a for a in player["auras"] if a["id"].get("spellId") == EFFECTS[item_id]), {})
        return {"spellId": EFFECTS[item_id], "procsPerRoute": round(aura.get("procsAvg", 0), 6),
                "secondsPerRoute": round(aura.get("uptimeSecondsAvg", 0), 6)}
    if item_id != 280032:
        raise ValueError(f"Unknown dungeon trinket effect for {item_id}")
    targets = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
    by_target = dict.fromkeys(targets, 0.0)
    for action in player["actions"]:
        if action["id"].get("spellId") == 1315996:
            for hit in action["targets"]:
                if hit["unitIndex"] in by_target:
                    by_target[hit["unitIndex"]] += hit["damage"]
    by_pack, offset = [], 0
    for size in pack_sizes:
        damage = sum(by_target[t] for t in targets[offset:offset + size])
        by_pack.append(round(damage / result["iterationsDone"], 6))
        offset += size
    return {"spellId": 1315996, "damagePerPack": by_pack}


def validate_dungeon_effect(row, baseline):
    proof = row.get("routeEffect", {})
    item_id = row["id"]
    def finite(value):
        return type(value) in (int, float) and math.isfinite(value)
    if (not isinstance(proof, dict) or not finite(proof.get("meanDamage")) or not finite(proof.get("pairedSE"))
            or abs(proof["meanDamage"] - baseline - row["gain"]) > 0.0002
            or proof["pairedSE"] != row["se"]):
        raise ValueError(f"Missing or mismatched native dungeon replay for trinket {item_id}")
    if item_id == 22268:
        procs, seconds = proof.get("procsPerRoute"), proof.get("secondsPerRoute")
        if (proof.get("spellId") != EFFECTS[item_id] or not finite(procs) or not finite(seconds)
                or procs <= 0 or not 0 < seconds <= row["avgSeconds"] + 0.00001
                or seconds > 10 * procs + 0.00001):
            raise ValueError(f"Missing dungeon aura from {item_id}")
    elif item_id == 280032:
        values = proof.get("damagePerPack", [])
        if (proof.get("spellId") != 1315996 or not isinstance(values, list) or len(values) != len(row["packDamage"])
                or any(not finite(v) or not 0 <= v <= total + 0.0001
                       for v, total in zip(values, row["packDamage"]))
                or sum(values) <= 0):
            raise ValueError(f"Missing dungeon target damage from {item_id}")
    else:
        raise ValueError(f"Unknown dungeon trinket effect for {item_id}")
