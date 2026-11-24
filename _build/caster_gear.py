"""Pre-raid caster items missing from the ForeverDB pools.

Permanent stats and drops use the Forever tooltips (dataEnv=16, items 22315,
22319, 12930 and 13968). The Eye shares both faction quests with Mark of Tyranny.
"""

EYE = 13968
REED = 12930
SPELL_CRIT_RATING = 21

ITEMS = {
    22315: ("Hammer of Revitalization", "mh", 21, "2.4", 56, {7: 5, 41: 131, 42: 43, 43: 5}, 26.67,
            [["d", "429", "Isalien", "16.67", "0", "w"]]),
    22319: ("Tome of Divine Right", "oh", 23, "4.0", 56, {7: 6, 5: 6, 41: 26, 42: 9, 43: 4}, 0,
            [["d", "229", "Mor Grayhoof", "14.29", "0", "w"]]),
    REED: ("Briarwood Reed", "trinket", 12, "4.0", 55, {45: 15}, 0,
           [["d", "229", "Jed Runewatcher", "34.76", "0", "w"]]),
    EYE: ("Eye of the Beast", "trinket", 12, "4.0", 0, {SPELL_CRIT_RATING: 14}, 0,
          [["q", "4974", "For The Horde!", "55", "h", "k"],
           ["q", "5102", "General Drakkisath's Demise", "55", "a", "k"]]),
}


def include_items(db):
    for item_id, (name, pool, inv, kind, req, stats, dps, sources) in ITEMS.items():
        db.gear.setdefault(item_id, dict(inv=inv, kind=kind, req=req, stats=dict(stats), dps=dps, armor=0, wand=False))
        db.items.setdefault(item_id, dict(name=name, groups=frozenset("Q" if item_id == EYE else "d"),
                                          flags="U" if pool == "trinket" else "", side="", twin=None,
                                          limit=None, sources=[list(s) for s in sources]))


def include(db):
    """Add each item to the spellcasting profiles that can equip it."""
    for item_id, (_, pool, _, _, req, _, _, _) in ITEMS.items():
        for cls, data in db.classes.items():
            if pool == "mh" and cls not in {"DRUID", "PALADIN", "PRIEST", "SHAMAN"}:
                continue
            for spec in data["specs"].values():
                caster = spec["role"] in {"Caster DPS", "Healer"}
                if not (caster or spec["slug"] == "shockadin"):
                    continue
                if spec["style"] == "2h" and pool in {"mh", "oh"}:
                    continue
                candidates = spec.setdefault("pools", {}).setdefault(pool, [])
                if not any(i == item_id for i, _ in (*data["pools"].get(pool, ()), *candidates)):
                    candidates.append((item_id, max(req, 55 if item_id == EYE else 0)))
