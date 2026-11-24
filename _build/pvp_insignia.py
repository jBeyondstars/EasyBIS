"""Rank-two Forever trinkets missing from ForeverDB's stat-based gear pools.

Blizzard: https://worldofwarcraft.blizzard.com/en-us/news/24303316
Tooltips and quartermasters: https://www.wowhead.com/forever/item=274445 and
https://www.wowhead.com/forever/item=274444 (spell 438273).
"""

ALLIANCE = 274445
HORDE = 274444
RANK = 2


def include(db):
    for item_id, side, faction, vendor, twin in ((ALLIANCE, "a", "Alliance", 12781, HORDE),
                                                (HORDE, "h", "Horde", 12793, ALLIANCE)):
        item = db.items.setdefault(item_id, {})
        item.update(name=f"Greater Insignia of the {faction}", side=side, twin=twin,
                    groups=frozenset("pv"), flags="snU", limit=None, honor_rank=RANK,
                    sources=[["V", str(vendor), "", side, "w"], ["p", str(RANK), side, "f"]])
        db.gear.setdefault(item_id, dict(inv=12, kind="4.0", req=0, stats={}, dps=0.0, armor=0.0, wand=False))
