"""Confirm drop sources and locate legacy world-drop ranges."""

from __future__ import annotations

import json
from pathlib import Path


def apply(db) -> None:
    """Keep newer observations and acquisition routes that ForeverDB names explicitly."""
    path = Path(__file__).parent / "corrections" / "verified_drops.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    for number, record in evidence["observed"].items():
        item = db.items.get(int(number))
        if not item or item["groups"] != frozenset("u") or item["sources"]:
            continue
        item["groups"] = frozenset("w")
        item["sources"] = [record["source"]]
        if "s" not in item["flags"]:
            item["flags"] = "s" + item["flags"]

    for number, record in evidence["items"].items():
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
