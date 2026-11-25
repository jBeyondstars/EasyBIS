"""Pre-raid alternatives with a target or encounter condition, outside the scored ladder."""

import json
from functools import lru_cache
from pathlib import Path


FILE = Path(__file__).parent / "corrections" / "situational_gear.json"


@lru_cache(maxsize=1)
def _options():
    return json.loads(FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def item_ids(cls: str, spec: int, mode: str, slot: str) -> tuple[int, ...]:
    """Applicable options in display order. A missing spec list means every spec."""
    profile = f"{cls} {spec}"
    return tuple(row["id"] for row in _options() if row["mode"] == mode and row["slot"] == slot
                 and ("specs" not in row or profile in row["specs"]))


@lru_cache(maxsize=1)
def target_options() -> frozenset[int]:
    """Ranked items with target or terrain bonuses, independent of class and spec."""
    data = json.loads(FILE.with_name("target_situational.json").read_text(encoding="utf-8"))
    return frozenset(map(int, data["items"]))


def include(db):
    """Supply the missing trinket and source records without changing the normal gear pools."""
    for row in _options():
        record = row.get("missing_trinket")
        if record is None:
            continue
        item_id = row["id"]
        db.items.setdefault(item_id, dict(name=row["name"], groups=frozenset(record["group"]),
                                          flags=record["flags"], side="", twin=None, limit=record.get("limit"),
                                          sources=[record["source"].copy()]))
        db.gear.setdefault(item_id, dict(inv=12, kind="4.0", req=record["required_level"],
                                         stats={}, dps=0.0, armor=0.0, wand=False))
        if "quest_place" in record:
            db.quest_places.setdefault(int(record["source"][1]), tuple(record["quest_place"]))


def notes() -> list[dict]:
    """Localized item notes in the same format and scope as notes.shown()."""
    result = []
    for row in _options():
        note = dict(items=[row["id"]], list=row["mode"], slot=row["slot"], en=row["en"], fr=row["fr"])
        if "specs" in row:
            note["specs"] = row["specs"].copy()
        result.append(note)
    return result
