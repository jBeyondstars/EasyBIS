"""The pre-raid Survival weave set and the weapon pairs measured with it."""
from __future__ import annotations

import json
from pathlib import Path

import ladders
import phases
import ranks

FILE = Path(__file__).resolve().parent / "corrections" / "hunter_weave.json"


def load(db):
    hunters = db.classes.get("HUNTER", {}).get("specs", {})
    spec = next((index for index, data in hunters.items() if data["slug"] == "survival-ranged"), None)
    if spec is None:
        return None
    data = json.loads(FILE.read_text(encoding="utf-8"))
    pairs = data["pairs"]
    slots = data["gear"] | {slot: list(dict.fromkeys(pair[slot] for pair in pairs)) for slot in ("main", "ranged")}
    return spec, {slot: [entry(db, slot, item_id) for item_id in ids] for slot, ids in slots.items()}, pairs


def entry(db, slot, item_id):
    item, gear = db.items.get(item_id), db.gear.get(item_id)
    if not item or not gear or not item["sources"] or item["side"] or phases.item_phase(item) != phases.PRE_RAID:
        raise ValueError(f"Survival weave {slot}: item {item_id} needs a pre-raid source for both factions")
    two_hand = gear["inv"] == ladders.INV_TWO_HAND
    if (slot == "main" and not two_hand) or (slot == "ranged" and gear["inv"] not in ladders.RANGED_INV):
        raise ValueError(f"Survival weave {slot}: item {item_id} is not a weapon for this slot")
    flags = item["flags"]
    return ladders.Entry(item_id=item_id, score=0, side="", twin=None,
                         seen="s" in flags, new="n" in flags, unique="U" in flags, unsourced=False,
                         two_hand=two_hand, random=False, limit=item["limit"], pvp=ladders.pvp_reward(item),
                         rank=ranks.required(item, gear), recommended=True)
