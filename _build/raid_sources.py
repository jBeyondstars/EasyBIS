"""Locate legacy world-drop ranges with independent creature and instance records."""

from __future__ import annotations

import json
from pathlib import Path


def apply(db) -> None:
    """Keep newer observations and acquisition routes that ForeverDB names explicitly."""
    path = Path(__file__).parent / "corrections" / "verified_drops.json"
    records = json.loads(path.read_text(encoding="utf-8"))["items"]
    for number, record in records.items():
        item = db.items.get(int(number))
        world = [["w", *record["range"], "k"]]
        if not item or item["groups"] != frozenset("w") or item["sources"] != world:
            continue
        places = record["places"]
        if record.get("raid_only"):
            item["groups"] = frozenset("r")
            item["sources"] = places
        else:
            item["groups"] = frozenset(["w", *(source[0] for source in places)])
            item["sources"] = places + world
