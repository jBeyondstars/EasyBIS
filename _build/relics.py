"""Class relics missing from ForeverDB's level-60 ranged pools.

All relic effects modify spells or abilities. A healer's spell mix, a tank's objective
and a PvP opponent are not specified by the corresponding stat weights. Relics
can have an editorial recommendation based on their spell effects. Measured
DPS comes from paired empty-slot trials.
"""
from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path

import hunter_bm
import phases
import simulated


CLASSES = frozenset(("DRUID", "PALADIN", "SHAMAN"))
FILE = Path(__file__).parent / "corrections" / "relics.json"
ARMOR_SUBCLASS = {"DRUID": "4.8", "PALADIN": "4.7", "SHAMAN": "4.9"}


@lru_cache(maxsize=1)
def read():
    return json.loads(FILE.read_text(encoding="utf-8"))


def apply(db):
    """Populate the class pools and the item/source records, retaining newer native data."""
    for key, record in read()["items"].items():
        item_id = int(key)
        cls = record["class"]
        level = record["requires"]
        if cls not in db.classes:
            continue
        pool = db.classes[cls]["pools"].setdefault("ranged", [])
        if not any(existing == item_id for existing, _ in pool):
            pool.append((item_id, level))
        db.class_only.setdefault(item_id, frozenset((cls,)))
        db.gear.setdefault(item_id, {"inv": 28, "kind": ARMOR_SUBCLASS[cls], "req": level, "stats": {},
                                     "dps": 0.0, "armor": 0.0, "wand": False})
        sources = record["sources"]
        groups = frozenset("r" if source[0] == "d" and phases.source_raid(source) else source[0].lower()
                           for source in sources) or frozenset("u")
        if item_id not in db.items:
            db.items[item_id] = {"name": record["name"], "groups": groups, "flags": record["flags"],
                                 "side": "", "twin": None, "limit": None, "sources": sources}
        elif sources and not db.items[item_id]["sources"]:
            db.items[item_id]["sources"] = sources
            db.items[item_id]["groups"] = groups


def ranking(db, cls, spec, mode, entries):
    """Merge the role's spell-specific choices with future native candidates for this slot."""
    import ladders  # Entry is defined in the caller, which also imports this module.

    catalog = read()
    profile = catalog["profiles"].get(f"{cls} {spec}")
    if not profile:
        return entries
    ids = profile[mode]
    recommended = profile.get("recommended", {}).get(mode, [])
    native = [entry for entry in entries if str(entry.item_id) not in catalog["items"]]
    reading = getattr(db, "simulated", None)
    use_dps = mode == "pve" and simulated.IN_USE and reading and reading.specs
    gains = profile.get("dps", {}) if use_dps else {}
    contexts = {}
    for side in "ah":
        scored = list(native)
        choices = []
        situational = []
        for item_id in ids:
            item = db.items.get(item_id)
            if not item:
                continue
            record = catalog["items"][str(item_id)]
            uncertain_access = record.get("unconfirmed_access", False) and all(
                source in record["sources"] for source in item["sources"])
            trial = gains.get(str(item_id), {}).get(side)
            choice = not trial and item_id in recommended
            score = simulated.rounded(trial[0]) if trial else 0.0
            flags = item["flags"]
            entry = ladders.Entry(item_id=item_id, score=score, side=item["side"], twin=item["twin"],
                                  seen="s" in flags, new="n" in flags, unique="U" in flags,
                                  two_hand=False, random=False, limit=item["limit"],
                                  unsourced=uncertain_access or not item["sources"],
                                  phase=phases.LATER if uncertain_access else phases.item_phase(item),
                                  level=not trial and not choice, alternative_only=not trial and not choice,
                                  recommended=choice)
            if trial:
                scored.append(entry)
            elif choice:
                choices.append(entry)
            else:
                situational.append(entry)
        scored.sort(key=lambda entry: -entry.stored)
        contexts[side, None] = scored + choices + situational
    if not gains:
        return contexts["a", None]
    return hunter_bm.ContextLadder(contexts["a", None], contexts)


def notes(shown_ids):
    """Produce notes for listed relics, leaving Shaman effects to the item tooltip."""
    return [{"items": [int(key)], "slot": "ranged", "en": item["en"], "fr": item["fr"]}
            for key, item in read()["items"].items() if int(key) in shown_ids and item["class"] != "SHAMAN"]
