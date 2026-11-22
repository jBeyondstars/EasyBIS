"""Calibrate the cat's level-60 PvE off-hands and trinkets from faction-specific boss DPS.

Each slot has a paired +40 AP control to express its gains in the same points as
the rest of the cat's gear. For off-hands this preserves the two-handed weapon comparison.
"""
from __future__ import annotations

import json
from dataclasses import replace
from functools import lru_cache
from math import inf
from pathlib import Path

import simulated
import specs


DATA = Path(__file__).parent / "corrections"
FILES = {"off": DATA / "feral_offhands.json", "trinket": DATA / "feral_trinkets.json"}


class PreRaidTrinkets(list):
    """Keep the measured raid ladder and the requested pre-raid recommendations."""

    def __init__(self, entries):
        super().__init__(entries)
        eligible = [entry for entry in entries if entry.phase == 0]
        by_id = {entry.item_id: entry for entry in eligible}
        # Hand, Bones, Tuft, Flamehoof, Heart. The Hand/Tuft tie is editorial.
        order = (11815, 280065, 280060, 280074, 22321)
        if 11815 in by_id and 280060 in by_id:
            by_id[11815] = replace(by_id[11815], score=by_id[280060].score)
        self.pre_raid = [by_id[item] for item in order if item in by_id]
        self.pre_raid.extend(entry for entry in eligible if entry.item_id not in order)


class _CalibratedRanking(simulated.SlotRanking):
    def value(self, item_id: int, weight: float) -> float:
        # Both figures are already in ForeverDB points. The half-DPS fallback
        # used by the simulated DPS profiles would change an unmeasured item.
        return self.scores.get(item_id, weight)


@lru_cache(maxsize=1)
def calibrated_two_hand_scores(anchor_points: float, attack_power_weight: float) -> dict[int, float]:
    """Price the pre-raid alternatives against Doomsaw with its proc removed, in cat stat points."""
    data = json.loads((DATA / "feral_doomsaw.json").read_text(encoding="utf-8"))
    trials = data["trials"]
    scores = {}
    for item_id in trials["a"]["weapons"]:
        gains = [row["weapons"][item_id][0] * data["calibration_ap"] * attack_power_weight / row["ap_dps"]
                 for row in trials.values()]
        scores[int(item_id)] = anchor_points + sum(gains) / len(gains)
    return scores


@lru_cache(maxsize=2)
def _read(slot: str) -> dict:
    return json.loads(FILES[slot].read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def _ranking(slot: str, attack_power_weight: float, minimum: float) -> simulated.SlotRanking:
    data = _read(slot)
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
    return _CalibratedRanking(scores, 1.0, inf, frozenset(data["estimated"]))


def ranking(db, cls: str, spec: int, mode: str, slot: str) -> simulated.SlotRanking | None:
    """Called alongside simulated.ranking for the cap-level EasyBIS rules."""
    if (cls, spec, mode) != ("DRUID", 4, "pve") or slot not in FILES:
        return None
    druid = db.classes[cls]
    cat = druid["specs"][spec]
    if cat.get("slug") != "feral-cat":
        return None
    return _ranking(slot, cat["weights"]["raid"][specs.ATTACK_POWER], druid["min"].get("raid", 1))
