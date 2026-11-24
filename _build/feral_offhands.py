"""Cat-form PvE off-hands at level 60, measured with a one-handed mace.

The cat's main hands use ForeverDB points. Express the measured DPS in those
same units via the attack power weight and a paired +40 AP test. This keeps
the existing comparison of a two-hander against main hand plus off-hand.
"""
from __future__ import annotations

import json
from functools import lru_cache
from math import inf
from pathlib import Path

import simulated
import specs


FILE = Path(__file__).parent / "corrections" / "feral_offhands.json"


class _OffhandRanking(simulated.SlotRanking):
    def value(self, item_id: int, weight: float) -> float:
        # Both figures are already in ForeverDB points. The half-DPS fallback
        # used by the simulated DPS profiles would change an unmeasured item.
        return self.scores.get(item_id, weight)


@lru_cache(maxsize=1)
def _read() -> dict:
    return json.loads(FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def _ranking(attack_power_weight: float, minimum: float) -> simulated.SlotRanking:
    data = _read()
    factors = {side: attack_power_weight * data["calibration_ap"] / values[0]
               for side, values in data["calibration"].items()}
    scores = {}
    for group in data["candidates"]:
        # Each row is [actual item ID, side, DPS versus empty, paired SE,
        # iterations]. A paired faction entry has one client-visible score.
        trials = group["trials"]
        points = sum(dps * factors[side] for _, side, dps, _, _ in trials) / len(trials)
        if points < minimum and not group.get("weighted_candidate"):
            continue
        for item_id, _, _, _, _ in trials:
            scores[item_id] = round(points, 3)

    # Future additions without a measurement keep their unscaled stat weights.
    return _OffhandRanking(scores, 1.0, inf, frozenset(data["estimated"]))


def ranking(db, cls: str, spec: int, mode: str, slot: str) -> simulated.SlotRanking | None:
    """Called alongside simulated.ranking for the cap-level EasyBIS rules."""
    if (cls, spec, mode, slot) != ("DRUID", 4, "pve", "off"):
        return None
    druid = db.classes[cls]
    cat = druid["specs"][spec]
    if cat.get("slug") != "feral-cat":
        return None
    return _ranking(cat["weights"]["raid"][specs.ATTACK_POWER], druid["min"].get("raid", 1))
