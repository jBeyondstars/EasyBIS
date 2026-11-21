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

The addon can leave the PvP rewards out again, of either list, with an option
it keeps per list: out of the PvE list and in the PvP list until the player
says otherwise. Every entry says whether it is one (pvp_reward), which is
wider than the site's rule: the Premier sets and the battlegrounds' rewards
count too.

One more choice differs from the site, for now: a Hunter's lists leave out what
is held in the off hand, until the game confirms what those pieces give a
Hunter. It is the developer's decision, and full_ladder's one line to remove.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product

import phases
import ranks
import simulated
import specs

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
PVP_RANK_GROUP = ranks.RANK_GROUP
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
PVP_SET = ranks.PREMIER
PVP_REWARDS = {"pve": False, "pvp": True}  # whether a list counts them until the player says otherwise
ALTERNATIVES = 2      # picks shown after the best one(s), until the player asks for more
MAX_ALTERNATIVES = 6  # ... up to this many: what the data files keep of a ladder

HEALING = 41
SPELL_DAMAGE = (42, 45, 84, 85, 86, 87, 88, 89)
HIT = 31
INV_SHIELD, INV_ONE_HAND, INV_OFF_HAND, INV_TWO_HAND, INV_THROWN, INV_HELD = 14, 13, 22, 17, 25, 23
RANGED_INV = (15, 25, 26)

# What the addon can filter on at run time: faction, items with no known source, items seen in Forever only,
# the content phase the list stops at, whether the PvP rewards count in the list (the addon's default:
# they do in the PvP list and not in the PvE one, PVP_REWARDS), and the PvP rank the week's cap allows
# (None: the list does not follow the cap).
RANK_CAPS = (None, *ranks.filter_caps())
FILTERS = tuple(product(("a", "h"), (False, True), (False, True), phases.PHASES, (True, False), RANK_CAPS))


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
    pvp: bool = False  # a PvP reward (pvp_reward): what the addon's option leaves out of a list
    rank: int = ranks.NO_RANK  # the PvP rank it needs (ranks.required)
    honor: bool = False  # a Premier piece: sold for honor, even when the data gives it no source
    placed: bool = False  # put at its rank from a close spec's measure (simulated.place): no score of its own
    level: bool = False  # most of its worth is an effect the weights cannot count (specs.unvalued): no score of its
    #                      own, it stands level with the best picks and is never one itself
    estimated: bool = False  # ranked by simulation on a score that is no full measure (SlotRanking.measured): the
    #                          simulator cannot wear it (a random bonus), or lacks its effect or its proc rate. It keeps
    #                          its rank, and the addon shows no score for it

    @property
    def stored(self) -> int:
        """The score as the data files hold it: tenths, rounded."""
        return round(self.score * 10)

    @property
    def unscored(self) -> bool:
        """Whether its score is a stand-in, not its own: it keeps the ladder in order and is never a best pick."""
        return self.placed or self.level

    def shown(self, side: str) -> int | None:
        """The item a character of that faction wears for this entry."""
        if self.side in ("", side):
            return self.item_id
        return self.twin

    def passes(self, flt) -> bool:
        """flt: (faction, with the items of no known source, seen in Forever only, phase), then whether the
        PvP rewards count in the list, which they do when the filter does not say, and the rank the week's
        cap allows, None when the list does not follow it. A list that follows the cap counts the Premier
        pieces it allows, source known or not: the honor quartermasters sell them."""
        side, with_unsourced, seen_only, phase, *rest = flt
        cap = rest[1] if len(rest) > 1 else None
        if self.shown(side) is None or self.phase > phase:
            return False
        if self.pvp and rest and not rest[0]:
            return False
        if cap is not None and self.rank > cap:
            return False
        if self.unsourced and not with_unsourced and not (cap is not None and self.honor):
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

    rank_rewards=False is foreverdb.net/bis's rule: the PvP-rank rewards are left out of the PvE list, and a
    Hunter's list keeps what is held in the off hand.
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
    # The specs a simulator ranked (simulated.py). The site's rule and other levels stay on the weights.
    ranked = simulated.ranking(db, cls, spec, mode, slot) if rank_rewards and level == db.meta["cap"] else None
    placed = getattr(db, "placed", None) or {}   # the items put by hand after another one (corrections/effects.json)
    class_only = getattr(db, "class_only", None) or {}   # the classes of an item the game restricts (corrections/classes.json)

    entries, seen_ids, weighed = [], set(), {}
    for pool in dict(SLOTS)[slot]:
        for item_id, item_level in data["pools"].get(pool, ()):
            if item_level > level or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            gear, item = db.gear.get(item_id), db.items.get(item_id)
            if gear is None or item is None:
                continue
            if cls not in class_only.get(item_id, (cls,)):
                continue   # another class's piece: ForeverDB pools by armor type
            stats = gear["stats"]
            if not _fits_style(pool, gear["inv"], spec_def["style"], dual_wields):
                continue
            if hunter and gear["inv"] == INV_THROWN:
                continue
            if hunter and rank_rewards and gear["inv"] == INV_HELD:
                continue
            if not healer and HEALING in stats and not any(stat in stats for stat in SPELL_DAMAGE):
                continue
            sourced = bool(item["groups"] & groups)
            if not sourced and "u" not in item["groups"]:
                continue
            value = score(db, item_id, weights, cls) or 0.0
            armour_only = gear["armor"] > 0 and not gear["dps"] and not stats
            # A list ranked by simulation also holds what the weights give nothing and the simulator measures: a
            # trinket that is all proc, a weapon a Hunter only holds. The weights say what to list only where they rank.
            measured = ranked is not None and (ranked.scores.get(item_id, 0) > 0 or item_id in placed)
            if not (value >= min_score or (value > 0 and armour_only) or measured):
                continue
            flags = item["flags"]
            weighed[item_id] = value
            entries.append(Entry(
                item_id=item_id, score=ranked.value(item_id, value) if ranked else value,
                side=item["side"], twin=item["twin"],
                seen="s" in flags, new="n" in flags, unsourced=not sourced, unique="U" in flags,
                two_hand=gear["inv"] == INV_TWO_HAND, random="r" in flags, limit=item["limit"],
                phase=phases.item_phase(item), pvp=pvp_reward(item),
                rank=ranks.required(item, gear), honor=ranks.sold_for_honor(item),
                estimated=ranked is not None and not ranked.measured(item_id)))

    # A few twin pairs have both ids in the pool: keep the Alliance one, which names the other as its twin.
    ids = {entry.item_id for entry in entries}
    entries = [entry for entry in entries if not (entry.side == "h" and entry.twin in ids)]
    entries.sort(key=lambda entry: (-entry.score, -weighed[entry.item_id], entry.item_id))
    if rank_rewards and level == db.meta["cap"]:
        entries = simulated.place(entries, simulated.placements(db, cls, spec, mode, slot))
        if ranked is None:
            entries = level_with_the_best(entries, specs.unvalued(db, cls, spec))
        else:
            entries = after_their_anchor(entries, placed)
    return entries


def after_their_anchor(entries: list[Entry], placed: dict) -> list[Entry]:
    """The ladder with each item placed by hand (db.placed) right after the item it follows, with that item's score
    for the ladder to stay in order, and flagged: no score of its own, never a best pick. Without the item it
    follows, the ladder does not hold it."""
    for item_id, anchor in placed.items():
        entry = next((e for e in entries if e.item_id == item_id), None)
        if entry is None:
            continue
        entries = [e for e in entries if e.item_id != item_id]
        at = next((i for i, e in enumerate(entries) if e.item_id == anchor), None)
        if at is not None:
            entries.insert(at + 1, replace(entry, score=entries[at].score, placed=True, estimated=False))
    return entries


def level_with_the_best(entries: list[Entry], unvalued) -> list[Entry]:
    """The ladder with the items the weights cannot value (specs.unvalued) moved to its head, in the order they
    had, each with the first score for the ladder to stay in order, and flagged: that score is not its own."""
    moved = [entry for entry in entries if entry.item_id in unvalued]
    if not moved or len(moved) == len(entries):
        return entries
    rest = [entry for entry in entries if entry.item_id not in unvalued]
    return [replace(entry, score=rest[0].score, level=True) for entry in moved] + rest


def lead(entries: list[Entry]) -> Entry | None:
    """The first entry that can be a best pick: one with no score of its own never is, unless the list has
    nothing else."""
    return next((entry for entry in entries if not entry.unscored), entries[0] if entries else None)


def picks(slot: str, visible: list[Entry], alternatives: int = ALTERNATIVES) -> tuple[list[Entry], list[Entry]]:
    """(best, alternatives) among the entries a character can see; alternatives: how many it asks for.

    Rings and trinkets have two best picks: the second is the next one that can
    be worn with the first (not from the same "only one of these" category).
    That second pick is one of the alternatives asked for: a slot lists the
    best pick and at most `alternatives` items after it, whatever the slot.
    """
    if not visible:
        return [], []
    first = lead(visible)
    best = [first]
    if slot in PAIRED:
        second = next((e for e in visible if e is not first and not e.unscored
                       and not (first.limit and e.limit == first.limit)), None)
        if second:
            best.append(second)
    others = [entry for entry in visible if entry not in best]
    return best, others[:alternatives - (len(best) - 1)]


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
    if two and (not one or lead(two).stored >= lead(one).stored + (lead(off).stored if off else 0)):
        return two, []
    if not one:
        return main, off
    return one, [entry for entry in off if entry.item_id != lead(one).item_id]


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
    if lead(two).stored >= lead(one).stored + (lead(off).stored if off else 0):
        return one, [entry for entry in off if entry.item_id != lead(one).item_id]
    return two, []


def _needed(slot: str, visible: list[Entry]) -> list[Entry]:
    """What the addon reads of a slot's ladder under one filter (see picks and weapon_lists), with as many
    alternatives as a player can ask for: what he sees with fewer is the start of it."""
    best, alternatives = picks(slot, visible, MAX_ALTERNATIVES)
    needed = best + alternatives
    placed = sum(1 for e in visible if e.unscored)   # such an item may stand before a weapon list's best pick
    if slot == "main":
        needed += [e for e in visible if e.two_hand][:1 + MAX_ALTERNATIVES + placed]
        needed += [e for e in visible if not e.two_hand][:1 + MAX_ALTERNATIVES + placed]
    elif slot == "off":
        needed = visible[:2 + MAX_ALTERNATIVES + placed]  # one more: the main hand's pick is left out
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
