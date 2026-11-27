"""What a PvP rank buys in Forever, and the highest rank each week of a season allows.

The ranks of a season are capped, and the cap rises every week (WEEKLY_CAPS). Blizzard says there is a
weekly cap and does not publish it: the curve was read in the game's client before launch, and players
saw its first values on their rank bar once the game was out (2,700 points the first week, 5,250 from the
reset of 2026-11-10). The season began with the game; its second week starts at the first weekly reset.

What a rank buys is Blizzard's list (https://worldofwarcraft.blizzard.com/en-us/news/24303316). Forever's
PvP gear is the Premier sets, sold for honor:
  - the blue set (level 55) needs no rank;
  - the epic set (level 60) needs an Emboldened Seal of the slot, sold from a rank that depends on the slot;
  - the epic weapons need rank 14, the cloaks rank 3 and the necklaces rank 4.

The rank rewards of Classic ("Field Marshal's Headdress") are still in the game's files, and no vendor of
Forever has been seen selling one, when the vendors of the same rank 14 weapons list the Premier ones.

To maintain: when a new season opens, change SEASON_START, and WEEKLY_CAPS if its curve is another.
"""
from __future__ import annotations

import pvp_insignia

SEASON_START = 1793833200  # 2026-11-04 23:00 UTC: the game's launch
WEEKLY_CAPS = (3, 5, 6, 7, 8, 9, 11, 12, 13, 14)  # the highest rank of each week; the last one stays

NO_RANK = 0
NOT_SOLD = 99  # above every rank: a list that follows the cap never shows it

RANK_GROUP = "p"     # ForeverDB's source group of the rank rewards
PREMIER = "Premier "  # the name of every piece of Forever's PvP sets
EPIC_LEVEL = 60       # a Premier piece of this required level is of the epic set

CLOAK, NECK = 16, 2   # inventory types
BLUE_RANKS = {CLOAK: 3, NECK: 4}
WEAPON_RANK = 14
# Inventory type -> the rank that sells its Emboldened Seal.
SEAL_RANKS = {9: 8, 6: 8, 8: 9, 10: 10, 7: 12, 3: 12, 5: 13, 20: 13, 1: 13}  # wrist and waist, feet, hands,
#                                                                              legs and shoulders, chest and head
NEEDED = (NO_RANK, *sorted({pvp_insignia.RANK, *BLUE_RANKS.values(), *SEAL_RANKS.values(), WEAPON_RANK}))

# Prices read from Dirgehammer, Biggins and O'Neal in build 1.60.1.71139 (2026-11-26).
# The armor prices apply by slot. The epic armor upgrade consumes the matching rare piece and seal.
# https://worldofwarcraft.blizzard.com/en-us/news/24303316
HONOR_CURRENCY = 1792
WARSONG, ARATHI, ALTERAC, DARKSPEAR = 20558, 20559, 20560, 274895  # mark item IDs
RARE_PRICES = {
    1: (9000, ALTERAC, 15),   # head
    3: (6350, ARATHI, 10),    # shoulders
    5: (9350, ARATHI, 15),    # chest, including robes (inventory type 20)
    6: (6000, ARATHI, 10),    # waist
    7: (9000, WARSONG, 15),   # legs
    8: (7500, DARKSPEAR, 10), # feet
    9: (4500, WARSONG, 10),   # wrists
    10: (7500, WARSONG, 10),  # hands
    CLOAK: (4500, ARATHI, 10),
    NECK: (7500, DARKSPEAR, 10),
}
SEALS = {  # inventory type: (Emboldened Seal item ID, honor)
    1: (275241, 2650), 3: (275229, 2250), 5: (275238, 2650), 6: (275244, 1500),
    7: (275242, 2650), 8: (275243, 1500), 9: (275240, 1200), 10: (275239, 2250),
}
SEAL_PRICES = {slot: price for slot, (_, price) in SEALS.items()}
WEAPON_PRICES = {
    **dict.fromkeys((13, 15, 21, 22, 26), (12000, DARKSPEAR, 10)),
    **dict.fromkeys((14, 23), (10500, DARKSPEAR, 10)),
    17: (22500, ALTERAC, 20),
}


def sold_for_honor(item: dict) -> bool:
    """Whether an item of the source list is a piece of the Premier sets, which the data often gives no
    source for: the honor quartermasters sell them."""
    return bool(item.get("honor_rank")) or item["name"].startswith(PREMIER)


def required(item: dict, gear: dict | None) -> int:
    """The rank an item of the source list needs: NO_RANK, a rank, or NOT_SOLD."""
    if item.get("honor_rank"):
        return item["honor_rank"]
    if sold_for_honor(item):
        gear = gear or {}
        if gear.get("req", 0) >= EPIC_LEVEL:
            return SEAL_RANKS.get(gear.get("inv"), WEAPON_RANK)
        return BLUE_RANKS.get(gear.get("inv"), NO_RANK)
    return NOT_SOLD if RANK_GROUP in item["groups"] else NO_RANK


def honor_price(item_id: int, item: dict, gear: dict) -> dict:
    """The full price of a Premier piece or the rank-two insignia, in vendor currencies."""
    if item_id in (pvp_insignia.ALLIANCE, pvp_insignia.HORDE):
        return {"honor": 5250, "copper": 15000}
    if not sold_for_honor(item):
        return {}
    slot = 5 if gear.get("inv") == 20 else gear.get("inv")
    level = gear.get("req")
    seal = 0
    if level == EPIC_LEVEL:
        seal = SEAL_PRICES.get(slot, 0)
        price = RARE_PRICES.get(slot) if seal else WEAPON_PRICES.get(slot)
    else:
        price = RARE_PRICES.get(slot) if level == 55 else None
    if not price:
        return {}
    honor, mark, marks = price
    fields = {"honor": honor, "mark": mark, "marks": marks}
    if seal:
        fields["seal"] = seal
    return fields


def filter_caps() -> tuple[int, ...]:
    """The weekly caps that show different items: the generator keeps what each of them needs."""
    caps, shown = [], set()
    for cap in WEEKLY_CAPS:
        allowed = frozenset(rank for rank in NEEDED if rank <= cap)
        if allowed not in shown:
            shown.add(allowed)
            caps.append(cap)
    return tuple(caps)
