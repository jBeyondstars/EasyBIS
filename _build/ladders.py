"""Rank ForeverDB's gear pools into best-in-slot ladders.

The scoring and the eligibility rules follow ForeverDB's addon (GearFinder.lua
GF.candidates, Auto.lua ns.gearScore), which is GPL-3.0 with an attribution
term. The two choices that differ from the addon's defaults follow the
foreverdb.net/bis pages instead, so the ladders match the site:
  - the PvE list leaves PvP-rank rewards out (source group "p");
  - items with no known source stay in, flagged, so the addon can hide them.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import phases

# Easy BIS slot -> the ForeverDB pools it reads. Rings and trinkets fill two slots from one pool.
SLOTS = (
    ("head", ("head",)), ("neck", ("neck",)), ("shoulder", ("shoulder",)), ("back", ("back",)),
    ("chest", ("chest",)), ("wrist", ("wrist",)), ("hands", ("hands",)), ("waist", ("waist",)),
    ("legs", ("legs",)), ("feet", ("feet",)), ("finger", ("finger",)), ("trinket", ("trinket",)),
    ("main", ("mh", "2h")), ("off", ("oh",)), ("ranged", ("ranged",)),
)
PAIRED = frozenset(("finger", "trinket"))
MODES = {"pve": "raid", "pvp": "pvp"}  # Easy BIS list -> ForeverDB weight profile

SOURCE_GROUPS = frozenset("qQvcdrwRpex")  # ForeverDB's source groups, minus "u" (no known source)
PVP_RANK_GROUP = "p"
ALTERNATIVES = 2  # picks shown after the best one(s)

HEALING = 41
SPELL_DAMAGE = (42, 45, 84, 85, 86, 87, 88, 89)
HIT = 31
INV_SHIELD, INV_ONE_HAND, INV_OFF_HAND, INV_TWO_HAND, INV_THROWN = 14, 13, 22, 17, 25
RANGED_INV = (15, 25, 26)

# What the addon can filter on at run time: faction, items with no known source, items seen in Forever only,
# and the content phase the list stops at.
FILTERS = tuple(product(("a", "h"), (False, True), (False, True), phases.PHASES))


@dataclass(frozen=True)
class Entry:
    item_id: int     # the id in ForeverDB's pool
    score: float
    side: str        # "": both factions wear item_id; "a" or "h": only that faction does
    twin: int | None  # the same piece for the other faction
    seen: bool       # seen in Forever by ForeverDB players
    new: bool        # new in Forever
    unsourced: bool  # no known source
    unique: bool
    two_hand: bool
    random: bool     # random bonus ("of the Bear")
    limit: str | None  # only one item of this category can be worn
    phase: int = phases.PRE_RAID  # the content phase it arrives with (phases.py)

    @property
    def stored(self) -> int:
        """The score as the data files hold it: tenths, rounded."""
        return round(self.score * 10)

    def shown(self, side: str) -> int | None:
        """The item a character of that faction wears for this entry."""
        if self.side in ("", side):
            return self.item_id
        return self.twin

    def passes(self, flt) -> bool:
        side, with_unsourced, seen_only, phase = flt
        if self.shown(side) is None or self.phase > phase:
            return False
        if self.unsourced and not with_unsourced:
            return False
        return self.seen or not seen_only


def score(db, item_id: int, weights: dict, cls: str) -> float | None:
    """ForeverDB's ns.gearScore for an item id."""
    gear = db.gear.get(item_id)
    if gear is None:
        return None
    stats = gear["stats"]
    total = sum(weights[stat] * value for stat, value in stats.items() if stat in weights)
    ranged = gear["inv"] in RANGED_INV
    if gear["dps"] > 0 and "dps" in weights and ranged == (cls == "HUNTER"):
        total += weights["dps"] * gear["dps"]
    elif gear["wand"] and gear["dps"] and "wand" in weights:
        total += weights["wand"] * gear["dps"]
    if gear["armor"] and "armor" in weights:
        total += weights["armor"] * gear["armor"]
    extra = db.extra.get(item_id)
    if extra:
        if extra.get("hit") and HIT not in stats and HIT in weights:
            total += weights[HIT] * extra["hit"]
        for stat, value in extra.get("set", {}).items():
            if stat in weights:
                total += weights[stat] * value
    return total


def _fits_style(pool: str, inv: int, style: str, dual_wields: bool) -> bool:
    if pool == "2h":
        return not (style == "shield" or (style == "dw" and dual_wields))
    if pool == "mh":
        return style != "2h"
    if pool == "oh":
        if style == "2h":
            return False
        if style == "shield":
            return inv == INV_SHIELD
        if style == "dw":
            return inv in (INV_ONE_HAND, INV_OFF_HAND)
    return True


def full_ladder(db, cls: str, spec: int, mode: str, slot: str, level: int | None = None) -> list[Entry]:
    """Every pick for the slot, best first, with no faction or source filter applied."""
    level = level or db.meta["cap"]
    data = db.classes[cls]
    spec_def = data["specs"][spec]
    profile = MODES[mode]
    weights = spec_def["weights"][profile]
    groups = SOURCE_GROUPS - {PVP_RANK_GROUP} if mode == "pve" else SOURCE_GROUPS
    healer, hunter = spec_def["role"] == "Healer", cls == "HUNTER"
    dual_wields = level >= db.dual_wield.get(cls, 99)
    min_score = data["min"].get(profile, 1)

    entries, seen_ids = [], set()
    for pool in dict(SLOTS)[slot]:
        for item_id, item_level in data["pools"].get(pool, ()):
            if item_level > level or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            gear, item = db.gear.get(item_id), db.items.get(item_id)
            if gear is None or item is None:
                continue
            stats = gear["stats"]
            if not _fits_style(pool, gear["inv"], spec_def["style"], dual_wields):
                continue
            if hunter and gear["inv"] == INV_THROWN:
                continue
            if not healer and HEALING in stats and not any(stat in stats for stat in SPELL_DAMAGE):
                continue
            sourced = bool(item["groups"] & groups)
            if not sourced and "u" not in item["groups"]:
                continue
            value = score(db, item_id, weights, cls) or 0.0
            armour_only = gear["armor"] > 0 and not gear["dps"] and not stats
            if not (value >= min_score or (value > 0 and armour_only)):
                continue
            flags = item["flags"]
            entries.append(Entry(
                item_id=item_id, score=value, side=item["side"], twin=item["twin"],
                seen="s" in flags, new="n" in flags, unsourced=not sourced, unique="U" in flags,
                two_hand=gear["inv"] == INV_TWO_HAND, random="r" in flags, limit=item["limit"],
                phase=phases.item_phase(item)))

    # A few twin pairs have both ids in the pool: keep the Alliance one, which names the other as its twin.
    ids = {entry.item_id for entry in entries}
    entries = [entry for entry in entries if not (entry.side == "h" and entry.twin in ids)]
    entries.sort(key=lambda entry: (-entry.score, entry.item_id))
    return entries


def picks(slot: str, visible: list[Entry]) -> tuple[list[Entry], list[Entry]]:
    """(best, alternatives) among the entries a character can see.

    Rings and trinkets have two best picks: the second is the next one that can
    be worn with the first (not from the same "only one of these" category).
    """
    if not visible:
        return [], []
    best = [visible[0]]
    if slot in PAIRED:
        first = visible[0]
        second = next((e for e in visible[1:] if not (first.limit and e.limit == first.limit)), None)
        if second:
            best.append(second)
    others = [entry for entry in visible if entry not in best]
    return best, others[:ALTERNATIVES]


def weapon_lists(main: list[Entry], off: list[Entry]) -> tuple[list[Entry], list[Entry]]:
    """The main-hand and off-hand ladders once weighed against each other, as foreverdb.net/bis lays them out.

    When the best two-hander beats the best main hand plus the best off hand,
    the main hand lists two-handers only and the off hand is empty. Otherwise
    the main hand lists one-handers, and the off hand leaves out the weapon
    already picked for the main hand. Scores are weighed as the data files
    hold them, so the addon (Ladders.lua) decides the same way.
    """
    two = [entry for entry in main if entry.two_hand]
    one = [entry for entry in main if not entry.two_hand]
    if two and (not one or two[0].stored >= one[0].stored + (off[0].stored if off else 0)):
        return two, []
    if not one:
        return main, off
    return one, [entry for entry in off if entry.item_id != one[0].item_id]


def other_weapons(main: list[Entry], off: list[Entry]) -> tuple[list[Entry], list[Entry]]:
    """The weapons of the style weapon_lists set aside, to offer as alternatives: (main hand, off hand).

    When the two-handers win: the one-handers, and the off hands that go with
    them (the best one-hander itself left out, as in weapon_lists). When the
    one-handers win: the two-handers, and no off hand. A spec that only has one
    of the two styles has nothing else to offer.
    """
    two = [entry for entry in main if entry.two_hand]
    one = [entry for entry in main if not entry.two_hand]
    if not two or not one:
        return [], []
    if two[0].stored >= one[0].stored + (off[0].stored if off else 0):
        return one, [entry for entry in off if entry.item_id != one[0].item_id]
    return two, []


def _needed(slot: str, visible: list[Entry]) -> list[Entry]:
    """What the addon reads of a slot's ladder under one filter (see picks and weapon_lists)."""
    best, alternatives = picks(slot, visible)
    needed = best + alternatives
    if slot == "main":
        needed += [e for e in visible if e.two_hand][:1 + ALTERNATIVES]
        needed += [e for e in visible if not e.two_hand][:1 + ALTERNATIVES]
    elif slot == "off":
        needed = visible[:2 + ALTERNATIVES]  # one more: the main hand's pick is left out
    return needed


def kept_ladder(slot: str, ladder: list[Entry]) -> list[Entry]:
    """The part of the ladder the addon needs, whatever it filters on."""
    keep = set()
    for flt in FILTERS:
        keep.update(_needed(slot, [entry for entry in ladder if entry.passes(flt)]))
    return [entry for entry in ladder if entry in keep]


def build_all(db) -> dict:
    """{class: {spec: {mode: {slot: [Entry]}}}} with the kept ladders."""
    out = {}
    for cls, data in db.classes.items():
        out[cls] = {}
        for spec in sorted(data["specs"]):
            out[cls][spec] = {
                mode: {slot: kept_ladder(slot, full_ladder(db, cls, spec, mode, slot)) for slot, _ in SLOTS}
                for mode in MODES}
    return out
