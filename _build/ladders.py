"""Rank ForeverDB's gear pools into best-in-slot ladders.

The scoring and the eligibility rules follow ForeverDB's addon (GearFinder.lua
GF.candidates, Auto.lua ns.gearScore), which is GPL-3.0 with an attribution
term. One choice differs from the addon's defaults and follows the
foreverdb.net/bis pages instead: items with no known source stay in, flagged,
so the addon can hide them.

One choice differs from the site: a PvP-rank reward (source group "p") is
ranked in the PvE list as well, on its stats like any other item. A rank 14
weapon can be the best PvE weapon there is; what a list is for does not say
what an item is worth. The site's pages leave those out of PvE:
full_ladder(..., rank_rewards=False) is the site's rule, kept to check the
ranking against the site (tests/compare_site.py).

The addon leaves the PvP rewards out again, of both lists, until an option of
its own says to count them: every entry says whether it is one (pvp_reward),
which is wider than the site's rule: the Premier sets and the battlegrounds'
rewards count too.
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
# What else is a PvP reward, besides the PvP-rank rewards: what the honor quartermasters and the
# battlegrounds' supply officers sell, by the npc id the data gives them, what a battleground's faction
# gives, and Forever's Premier sets. The quartermasters sell 80 Premier pieces in the data, which has no
# source for the 450 others: the name says what they are.
PVP_VENDORS = {
    12777: "Captain Dirgehammer", 12781: "Master Sergeant Biggins", 12782: "Captain O'Neal",    # Stormwind
    12805: "Officer Areyn",
    14581: "Sergeant Thunderhorn", 12792: "Lady Palanseer", 12793: "Brave Stonehide",           # Orgrimmar
    12799: "Sergeant Ba'sha",
    15127: "Samuel Hawke", 15126: "Rutherford Twing",              # Arathi Basin
    14753: "Illiyana Moonblaze", 14754: "Kelm Hargunth",           # Warsong Gulch
    13217: "Thanthaldis Snowgleam", 13219: "Jekyll Flandring",     # Alterac Valley
}
# The League of Arathor, The Defilers, Frostwolf Clan, Stormpike Guard, Warsong Outriders, Silverwing Sentinels
PVP_FACTIONS = frozenset((509, 510, 729, 730, 889, 890))
PVP_SET = "Premier "
ALTERNATIVES = 2      # picks shown after the best one(s), until the player asks for more
MAX_ALTERNATIVES = 6  # ... up to this many: what the data files keep of a ladder

HEALING = 41
SPELL_DAMAGE = (42, 45, 84, 85, 86, 87, 88, 89)
HIT = 31
INV_SHIELD, INV_ONE_HAND, INV_OFF_HAND, INV_TWO_HAND, INV_THROWN = 14, 13, 22, 17, 25
RANGED_INV = (15, 25, 26)

# What the addon can filter on at run time: faction, items with no known source, items seen in Forever only,
# the content phase the list stops at, and whether the PvP rewards count.
FILTERS = tuple(product(("a", "h"), (False, True), (False, True), phases.PHASES, (True, False)))


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
    pvp: bool = False  # a PvP reward (pvp_reward)

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
        """flt: (faction, with the items of no known source, seen in Forever only, phase), and whether the
        PvP rewards count, which they do when the filter does not say."""
        side, with_unsourced, seen_only, phase, *rest = flt
        if self.shown(side) is None or self.phase > phase:
            return False
        if self.pvp and rest and not rest[0]:
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


def pvp_reward(item: dict) -> bool:
    """Whether an item of the source list is a PvP reward: of a PvP rank, of the honor quartermasters, of a
    battleground, or a piece of the Premier sets."""
    if PVP_RANK_GROUP in item["groups"] or item["name"].startswith(PVP_SET):
        return True
    for source in item["sources"]:
        number = int(source[1]) if len(source) > 1 and source[1].isdigit() else None
        if (source[0] in ("V", "v") and number in PVP_VENDORS) or (source[0] == "r" and number in PVP_FACTIONS):
            return True
    return False


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


def full_ladder(db, cls: str, spec: int, mode: str, slot: str, level: int | None = None,
                rank_rewards: bool = True) -> list[Entry]:
    """Every pick for the slot, best first, with no faction or source filter applied.

    rank_rewards=False leaves the PvP-rank rewards out of the PvE list, as foreverdb.net/bis does.
    """
    level = level or db.meta["cap"]
    data = db.classes[cls]
    spec_def = data["specs"][spec]
    profile = MODES[mode]
    weights = spec_def["weights"][profile]
    groups = SOURCE_GROUPS if rank_rewards or mode != "pve" else SOURCE_GROUPS - {PVP_RANK_GROUP}
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
                phase=phases.item_phase(item), pvp=pvp_reward(item)))

    # A few twin pairs have both ids in the pool: keep the Alliance one, which names the other as its twin.
    ids = {entry.item_id for entry in entries}
    entries = [entry for entry in entries if not (entry.side == "h" and entry.twin in ids)]
    entries.sort(key=lambda entry: (-entry.score, entry.item_id))
    return entries


def picks(slot: str, visible: list[Entry], alternatives: int = ALTERNATIVES) -> tuple[list[Entry], list[Entry]]:
    """(best, alternatives) among the entries a character can see; alternatives: how many it asks for.

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
    return best, others[:alternatives]


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
    """What the addon reads of a slot's ladder under one filter (see picks and weapon_lists), with as many
    alternatives as a player can ask for: what he sees with fewer is the start of it."""
    best, alternatives = picks(slot, visible, MAX_ALTERNATIVES)
    needed = best + alternatives
    if slot == "main":
        needed += [e for e in visible if e.two_hand][:1 + MAX_ALTERNATIVES]
        needed += [e for e in visible if not e.two_hand][:1 + MAX_ALTERNATIVES]
    elif slot == "off":
        needed = visible[:2 + MAX_ALTERNATIVES]  # one more: the main hand's pick is left out
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
