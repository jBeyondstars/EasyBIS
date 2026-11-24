"""Permanent item stats cross-checked against the Forever client and WoWSims.

Only replace recorded input values. A future independent change to one of the
verified fields leaves the complete item to the newer source.
"""
import json
from pathlib import Path

FILE = Path(__file__).parent / "corrections" / "verified_gear.json"


def apply(db):
    evidence = json.loads(FILE.read_text(encoding="utf-8"))
    for item_id, record in evidence["items"].items():
        gear = db.gear.get(int(item_id))
        if gear is None:
            continue
        stats = gear["stats"]
        fields = {int(stat): pair for stat, pair in record["fields"].items()}
        if any(stats.get(stat, 0) not in (old, new) for stat, (old, new) in fields.items()):
            continue
        for stat, (_, new) in fields.items():
            if new:
                stats[stat] = new
            else:
                stats.pop(stat, None)
        if "weapon" in record:
            old_dps, low, high, speed = record["weapon"]
            dps = round((low + high) / (2 * speed), 2)
            if gear["dps"] in (old_dps, dps):
                gear.update(dps=dps, weapon_hit=(low, high, speed))
    for item_id in evidence["random_suffix"]:
        item = db.items.get(item_id)
        if item and "r" not in item["flags"]:
            item["flags"] += "r"
