"""Acquisition sources cross-checked against Forever's observed loot and quests."""

import json
from pathlib import Path


FILE = Path(__file__).parent / "corrections" / "verified_sources.json"


def _route(source):
    if source[0] == "d":
        return tuple(source[:3])
    return source[0].lower(), source[1]


def apply(db) -> dict:
    """Fill source gaps and refine the same routes if a later export includes them."""
    evidence = json.loads(FILE.read_text(encoding="utf-8"))
    verified = {}
    for number, record in evidence["items"].items():
        item_id = int(number)
        item = db.items.get(item_id)
        if item is None:
            continue
        sources = [source.copy() for source in record["sources"]]
        reviewed = {_route(source) for source in sources}
        reviewed.update(map(tuple, record.get("reported_sources", ())))
        existing = {_route(source): source for source in item["sources"]}
        if not existing.keys() <= reviewed:
            continue
        for source in sources:
            prior = existing.get(_route(source))
            if prior and source[0] in ("d", "m", "R") and prior[3] not in ("", "0"):
                source[3] = prior[3]
        item["groups"] = frozenset(record["groups"])
        item["sources"] = sources
        if record["side"]:
            item["side"] = record["side"]
        if "s" not in item["flags"]:
            item["flags"] = "s" + item["flags"]
        item.pop("phase", None)
        verified[item_id] = record

    for number, vendor in evidence["vendors"].items():
        db.vendors.setdefault(int(number), vendor)
    for number, currency in evidence["currencies"].items():
        db.priced.currencies.setdefault(int(number), currency)
    return verified


def add_reputations(db, reading: dict) -> dict:
    """Fill the standing requirement for the verified quartermaster purchases."""
    items, vendors = dict(reading.get("items", {})), dict(reading.get("vendors", {}))
    for item_id, record in getattr(db, "verified_sources", {}).items():
        if "reputation" not in record or any(row["kind"] == "w" for row in items.get(item_id, ())):
            continue
        faction, standing = record["reputation"]
        vendor = int(record["sources"][0][1])
        vendors.setdefault(vendor, db.vendors[vendor])
        requirement = {"faction": faction, "standing": standing, "side": record["side"],
                       "kind": "w", "vendor": vendor}
        items[item_id] = [*items.get(item_id, ()), requirement]
    return {**reading, "vendors": vendors, "items": items}
