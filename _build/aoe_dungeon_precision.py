"""Allocate extra dungeon iterations for statistically close combined leaders."""

import math
import simulate_aoe as pack


def helm_gains(short, route, route_seconds):
    """Retain the passive gain on every pull and budget Fireball at one use per cooldown."""
    cooldown = pack.HELM_OF_FIRE_COOLDOWN
    uses = short["usesPerRun"]
    if not 0 <= uses <= 1 or not math.isfinite(route_seconds) or route_seconds <= 0:
        raise ValueError("Invalid Helm of Fire usage or dungeon duration")
    weight = min(1, pack.SECONDS / (cooldown * uses)) if uses else 0
    short_gain = weight * short["gain"] + (1 - weight) * short["passiveGain"]
    short_se = weight * short["se"] + (1 - weight) * short["passiveSE"]

    uses = route["usesPerRun"].get(str(pack.HELM_OF_FIRE), 0)
    route_gain, route_se = route["gain"], route["se"]
    if uses:
        # Dungeon activation trials store paired differences from the equipped, unused helm.
        chosen = [trial for trial in route["activationTrials"] if all(
            trial[k] == route[k] for k in ("usePack", "useAfterSeconds", "activation", "usesPerRun"))]
        if not 0 < uses <= 1 or len(chosen) != 1:
            raise ValueError("Invalid Helm of Fire activation trial")
        unavailable = 1 - min(1, route_seconds / (cooldown * uses))
        route_gain -= unavailable * chosen[0]["gain"]
        # Covariance of the archived paired estimates is unknown.
        route_se += unavailable * chosen[0]["se"]
    return short_gain, short_se, route_gain, route_se


def _error(block, left, right, rows):
    """Use the paired gap when both configurations are adjacent in this ranking."""
    if rows[left].get("cooldownAdjusted") or rows[right].get("cooldownAdjusted"):
        return rows[left]["se"] + rows[right]["se"]
    ranked = block["items"]
    for first, second in zip(ranked, ranked[1:]):
        if {(first["id"], first.get("partner")), (second["id"], second.get("partner"))} == {
            left,
            right,
        } and "gapSE" in second:
            return second["gapSE"]
    # Covariance with the same baseline is unknown for nonadjacent comparisons.
    return rows[left]["se"] + rows[right]["se"]


def close_leaders(short_slot, route_slot, slot, short_pairs=None, route_pairs=None):
    if slot in ("main", "off"):

        def pair_keys(rows):
            hand, partner = ("main", "off") if slot == "main" else ("off", "main")
            return {(x[hand], x[partner]): x for x in rows if x[hand]}

        a, b = pair_keys(short_pairs), pair_keys(route_pairs)
    else:
        a, b = ({(row["id"], None): row for row in block["items"]} for block in (short_slot, route_slot))
        helm = (pack.HELM_OF_FIRE, None)
        if helm in a:
            sg, ss, rg, rs = helm_gains(a[helm], b[helm], route_slot["baselineAvgSeconds"])
            a[helm] = dict(a[helm], gain=sg, se=ss, cooldownAdjusted=True)
            b[helm] = dict(b[helm], gain=rg, se=rs, cooldownAdjusted=True)
    sb, rb = short_slot["baseline"], route_slot["baseline"]
    score = {k: a[k]["gain"] / sb + b[k]["gain"] / rb for k in a}
    ranked = sorted(a, key=lambda k: (-score[k], k))
    if not ranked:
        return False
    best = ranked[0]
    for other in ranked[1:]:
        if best[0] == other[0]:
            continue
        # Exact replicas yield identical samples on both encounters.
        if all(
            data[best]["gain"] == data[other]["gain"] and data[best]["se"] == data[other]["se"]
            for data in (a, b)
        ):
            continue
        gap = score[best] - score[other]
        short_error = _error(short_slot, best, other, a) / sb
        route_error = _error(route_slot, best, other, b) / rb
        if (
            route_error > 0
            and route_error >= short_error
            and gap <= 1.96 * math.hypot(short_error, route_error)
        ):
            return True
    return False


def refinement_blocks(short, pilot):
    selected = set()
    for key, record in pilot["specs"].items():
        for side, new in record["factions"].items():
            original = short["specs"][key]["factions"][side]
            for slot, block in new.items():
                if close_leaders(
                    original[slot],
                    block,
                    slot,
                    original["main"]["setMeasurements"],
                    new["main"]["setMeasurements"],
                ):
                    selected.add((key, side, "main" if slot == "off" else slot))
    return selected
