"""Faction-specific Beast Mastery PvE substitutions and conditional off-hand scores."""
from __future__ import annotations

import json
from dataclasses import replace
from functools import lru_cache
from math import isfinite
from pathlib import Path

import simulated

FILE = Path(__file__).parent / "corrections" / "hunter_bm.json"
SLOTS = frozenset(("neck", "back", "wrist", "hands", "waist", "feet", "main", "off"))
INELIGIBLE = {"faction", "class", "plate", "weapon", "not_in_current_faction_pool", "same_as_selected_main",
              "same_unique_category", "unique_conflict", "client_faction", "wowsims_faction",
              "class_restriction", "offhand_only", "mainhand_or_twohand_only"}


class ContextLadder(list):
    """Canonical entries and measured orders by faction and equipped companion item."""

    def __init__(self, entries, contexts):
        super().__init__(entries)
        self.contexts = contexts


@lru_cache(maxsize=1)
def read():
    return json.loads(FILE.read_text(encoding="utf-8"))


def contextual_ladder(entries, slot, weights):
    return rank_contexts(entries, slot, weights, read().get("slots", {}))


def rank_contexts(entries, slot, weights, slots):
    """Score each concrete faction item on its reference gear, with a companion when supplied."""
    tables = slots.get(slot)
    if not tables:
        return entries
    contexts = {}
    for key, records in sorted(tables.items()):
        side, _, companion = key.partition(":")
        anchor = int(companion) if companion else None
        main_gain = None
        if slot == "off" and anchor:
            main_result = slots["main"][side].get(companion)
            if main_result and main_result[3] == "measured":
                main_gain = main_result[0]
        rows = []
        for entry in entries:
            actual = entry.shown(side)
            if not actual or actual == anchor:
                continue
            result = records.get(str(actual), (None, None, 0, "unmeasured"))
            if result[3] in INELIGIBLE:
                continue
            # A known but unmeasurable candidate is an unscored alternative.
            # Its archived score can belong to a different hit or weapon context.
            gain, _, _, model = result
            partial = model != "measured" or entry.random
            if model in {"assumed_proc", "unverified_proc_rate"}:
                gain = None
            score = simulated.rounded(gain) if gain is not None else 0.0
            if main_gain is not None and gain is not None:
                # Rounding the two terms separately can reverse a close 2H vs dual-wield comparison.
                score = max(0.0, simulated.rounded(main_gain + gain) - simulated.rounded(main_gain))
            rows.append(replace(entry, score=score, estimated=partial, alternative_only=partial, model=model,
                                paired_with=anchor if slot in ("finger", "trinket") else None))
        rows.sort(key=lambda entry: (-entry.stored, entry.estimated, -weights[entry.item_id], entry.item_id))
        contexts[side, anchor] = rows
    return ContextLadder(entries, contexts)


def compact_record(result, model):
    """[gain over the actual empty slot, paired SE, iterations, model or exclusion]."""
    if "reason" in result:
        if result["reason"] == "pending":
            raise ValueError("Incomplete simulation batch")
        return [None, None, 0, result["reason"]]
    gain, se, count = result["gain"], result["se_gain"], result["iterations"]
    if (model not in {"measured", "unregistered_effect", "assumed_proc", "unverified_proc_rate"} or not isfinite(gain)
            or not isfinite(se) or se < 0 or count not in (2000, 20000)):
        raise ValueError(f"Invalid paired result: {result}")
    return [gain, se, count, model]


def import_measurements(calibration, offhands):
    """Build the small input used by the ordinary generator from two completed exports."""
    if not calibration["closed"] or calibration["pending_batches"] or calibration["profile"] != "HUNTER 1":
        raise ValueError("Beast Mastery calibration is incomplete")
    if set(offhands["anchors"]) != {"a", "h"} or not all(offhands["anchors"].values()):
        raise ValueError("Missing faction-specific weapon comparisons")
    if not offhands["final_filters_frozen"] or offhands["pending_requested_jobs"]:
        raise ValueError("Off-hand calibration is incomplete")
    if offhands["main_enchant"] != 2564 or offhands["off_enchant"] != 0:
        raise ValueError("Off-hand comparisons require the same +15 agility main-hand enchant")
    if offhands.get("engine", calibration["engine"]) != calibration["engine"]:
        raise ValueError("Weapon and armor measurements used different simulators")
    if offhands["catalogue_sha256"] != calibration["catalogue_sha256"]:
        raise ValueError("Weapon and armor measurements used different candidate lists")
    if {s: v["race"] for s, v in calibration["references"].items()} != {"a": "RaceDwarf", "h": "RaceOrc"}:
        raise ValueError("Unrecognised Beast Mastery reference")
    slots = {}
    controlled = {}
    corrected_binaries = set()

    def record(slot, context, item_id, result, model):
        if result.get("stats_model") == "client_corrected":
            sha = result["stats_model_sha256"]
            if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
                raise ValueError("Invalid executable hash for a corrected client stat")
            corrected_binaries.add(sha)
            controlled.setdefault(slot, {}).setdefault(context, []).append(int(item_id))
        return compact_record(result, model)

    required = SLOTS - {"feet"}
    if not required.issubset(calibration["slots"]):
        raise ValueError("Missing required Beast Mastery slot")
    for slot in sorted((SLOTS & calibration["slots"].keys()) - {"off"}):
        slots[slot] = {}
        for side in ("a", "h"):
            records = {}
            for item_id, item in calibration["slots"][slot].items():
                result = item["sides"][side]
                if result.get("catalogue") or result.get("reason") in INELIGIBLE:
                    records[item_id] = record(slot, side, item_id, result, item["status"])
            slots[slot][side] = records

    slots["off"] = {}
    for side, anchors in offhands["anchors"].items():
        for main, group in anchors.items():
            records = {}
            for item_id, item in calibration["slots"]["off"].items():
                base = item["sides"][side]
                if base.get("reason") in INELIGIBLE:
                    records[item_id] = compact_record(base, item["status"])
            for item_id, result in group["items"].items():
                if item_id == main:
                    continue
                records[item_id] = record("off", f"{side}:{main}", item_id, result, result.get("status"))
            slots["off"][f"{side}:{main}"] = records

    # The direct two-hand experiments include the actual totals for several combinations.
    # Their incremental off-hand gain and error come from the pair with its own main hand.
    for side, bridge in calibration["paired_weapon_sets_vs_both_hands_empty"].items():
        rows = {r["key"]: r for r in bridge["rows"]}
        for key, pair in rows.items():
            if key == "empty":
                continue
            main, off = key.split("+")
            if off == "0":
                record = slots["main"][side].get(main)
                if record and record[3] == "measured":
                    record[:3] = [round(pair["diff"], 6), round(pair["se"], 6), 20000]
                continue
            main_key = f"{main}+0"
            base = rows[main_key]
            record = slots["off"].get(f"{side}:{main}", {}).get(off)
            if not record or record[3] != "measured":
                continue
            error = pair.get("pairSe", {}).get(main_key, base.get("pairSe", {}).get(key))
            if error is None:
                raise ValueError(f"Missing paired standard error: {side}, {key}")
            record[:3] = [round(pair["dps"] - base["dps"], 6), round(error, 6), 20000]

    data = {"wowsims": calibration["engine"], "profile": calibration["profile"],
            "source_archive_sha256": calibration["archive_sha256"],
            "source_catalogue_sha256": calibration["catalogue_sha256"],
            "reference": calibration["references"], "seeds": calibration["independent_seeds"],
            "columns": ["gain_dps", "paired_se", "iterations", "model"], "slots": slots}
    engine_hash = calibration.get("calibration_engine_sha256")
    if engine_hash or offhands.get("calibration_engine_sha256"):
        if (not engine_hash or engine_hash != offhands.get("calibration_engine_sha256")
                or engine_hash != calibration["client_stat_provenance"]["client_corrected_engine_sha256"]):
            raise ValueError("Calibrations declared different client-stat executables")
        data["calibration_engine_sha256"] = engine_hash
    item_revisions = calibration.get("wowsims_by_item", {})
    item_engines = calibration.get("engine_sha256_by_item", {})
    def provenance_rows(mapping):
        return {(slot, side, item): value for slot, contexts in mapping.items()
                for side, records in contexts.items() for item, value in records.items()}
    revisions = provenance_rows(item_revisions)
    engines = provenance_rows(item_engines)
    if revisions.keys() != engines.keys():
        raise ValueError("Per-item WoWSims revisions and executables must identify the same cells")
    for (slot, side, item), revision in revisions.items():
        binary = engines[slot, side, item]
        if (len(revision) != 40 or len(binary) != 64 or
                any(c not in "0123456789abcdef" for c in revision + binary) or
                data["slots"][slot][side][item][0] is None):
            raise ValueError(f"Invalid per-item calibration provenance for {slot}/{side}/{item}")
    if revisions:
        data["wowsims_by_item"] = item_revisions
        data["engine_sha256_by_item"] = item_engines
    if controlled:
        if len(corrected_binaries) != 1:
            raise ValueError("Corrected client rows used inconsistent binaries")
        provenance = calibration["client_stat_provenance"]
        if provenance["client_corrected_engine_sha256"] not in corrected_binaries:
            raise ValueError("Corrected client rows do not match their provenance")
        for contexts in controlled.values():
            for ids in contexts.values():
                ids.sort()
        data["client_stat_controls"] = {"binary_sha256": corrected_binaries.pop(), "slots": controlled,
                                        "native_binary_sha256": provenance["native_engine_sha256"],
                                        "client_items_sha256": provenance["malus_source_sha256"],
                                        "affected_ids": provenance["corrected_ids"]}
    return data


def save(data, path):
    # One row per candidate keeps the numerical changes visible in a source diff.
    lines = [json.dumps({k: v for k, v in data.items() if k != "slots"}, ensure_ascii=False)[:-1] + ', "slots": {']
    for index, (slot, tables) in enumerate(sorted(data["slots"].items())):
        lines.append(f'"{slot}": {{')
        for n, (key, records) in enumerate(sorted(tables.items())):
            lines.append(f'"{key}": {{')
            lines.append(",\n".join(f'"{i}": {json.dumps(records[i])}' for i in sorted(records, key=int)))
            lines.append("}," if n + 1 < len(tables) else "}")
        lines.append("}," if index + 1 < len(data["slots"]) else "}")
    lines.append("}}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("calibration", type=Path)
    parser.add_argument("offhands", type=Path)
    parser.add_argument("--output", type=Path, default=FILE)
    args = parser.parse_args()
    save(import_measurements(json.loads(args.calibration.read_text(encoding="utf-8")),
                             json.loads(args.offhands.read_text(encoding="utf-8"))), args.output)
