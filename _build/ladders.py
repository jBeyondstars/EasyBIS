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
from functools import lru_cache
import json
from pathlib import Path
from itertools import product

import caster_gear
import feral_gear
import hunter_bm
import phases
import pvp_insignia
import ranks
import reputations
import relics
import simulated
import situational_gear
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
# Alterac Valley quest rewards: the insignia upgrades, Korrak, and Hero of the Stormpike/Frostwolf.
# These sources are recorded as quests, without a quartermaster or a reputation source.
PVP_QUESTS = frozenset((*range(7161, 7173), 7181, 7202, 8271, 8272))
PVP_SET = ranks.PREMIER
# Short melee windows on a level-60 humanoid, measured separately from ordinary PvP stat weights.
PRERAID_MELEE_OPTIONS = {("WARRIOR", 1): (12583,), ("PALADIN", 3): (12583,), ("HUNTER", 3): (12583, 13348)}
PVP_REWARDS = {"pve": False, "pvp": True}  # whether a list counts them until the player says otherwise
ALTERNATIVES = 2      # picks shown after the best one(s), until the player asks for more
MAX_ALTERNATIVES = 6  # ... up to this many: what the data files keep of a ladder

HEALING = 41
SPELL_DAMAGE = (42, 45, 84, 85, 86, 87, 88, 89)
HIT = 31
INV_SHIELD, INV_ONE_HAND, INV_OFF_HAND, INV_TWO_HAND, INV_THROWN, INV_HELD = 14, 13, 22, 17, 25, 23
RANGED_INV = (15, 25, 26)
MELEE = "Melee DPS"
DAGGER = "2.15"   # item class.subclass
# The specs whose PvP list holds daggers only, by slot: Mutilate asks for one in each hand (WoWSims Forever,
# sim/rogue/talents_assassination.go). Backstab and Ambush ask for one in the main hand, and Subtlety has Hemorrhage.
DAGGERS_ONLY = {("ROGUE", "assassination"): ("main", "off")}

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
    alternative_only: bool = False  # partial measurement in a faction-specific list
    pvp_utility: bool = False  # a situational extra, after the ordinary alternatives
    paired_with: int | None = None  # the first ring or trinket held constant for a companion score
    model: str | None = None  # model or exclusion recorded for this faction and companion
    preraid_option: bool = False  # scored normally in later phases, situational in pre-raid

    # Complete pre-raid sets beaten with this two-hander's recommended enchant.
    pre_raid_weapon_sets: tuple[tuple[str, int, int], ...] = ()
    weapon_set_side: str | None = None  # set only in the pre-raid view
    fourth_option: bool = False  # display this situational option fourth, including at the default list length

    @property
    def stored(self) -> int:
        """The score as the data files hold it: tenths, rounded."""
        return round(self.score * 10)

    @property
    def unscored(self) -> bool:
        """Whether its score is a stand-in, not its own: it keeps the ladder in order and is never a best pick."""
        return self.placed or self.level or self.estimated or self.alternative_only or self.pvp_utility

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


def score(db, item_id: int, weights: dict, cls: str, melee: bool = False) -> float | None:
    """Weighted item stats. For a melee Hunter with corrected weights, value melee weapon DPS by the
    attack power that adds as much damage to white swings. Ranged weapons keep their published weight."""
    gear = db.gear.get(item_id)
    if gear is None:
        return None
    stats = gear["stats"]
    total = sum(weights[stat] * value for stat, value in stats.items() if stat in weights)
    total += weights.get("ranged_hit", 0) * specs.RANGED_HIT_PERCENT.get(item_id, 0)
    ranged = gear["inv"] in RANGED_INV
    if gear["dps"] > 0 and "dps" in weights and ranged == (cls == "HUNTER"):
        total += weights["dps"] * gear["dps"]
        if "weapon_hit" in weights and "weapon_hit" in gear:
            # Six seconds of white weapon damage plus one Mortal Strike. Normalization changes
            # the attack-power term of the strike; it leaves the weapon's own damage roll intact.
            low, high, _ = gear["weapon_hit"]
            total += weights["weapon_hit"] * ((low + high) / 2 - specs.TWO_HAND_NORMALIZED_SPEED * gear["dps"])
    elif gear["dps"] > 0 and melee and cls == "HUNTER" and not ranged:
        # ranged_power adds the ranged contribution to generic AP. Only its original melee part
        # applies here. This white-swing estimate cannot capture individual strikes or weapon speed.
        melee_power = weights[specs.ATTACK_POWER] - weights.get(specs.RANGED_ATTACK_POWER, 0)
        total += gear["dps"] * specs.ATTACK_POWER_PER_DPS * melee_power
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
        if (source[0] in ("V", "v") and number in PVP_VENDORS
                or source[0] == "r" and number in PVP_FACTIONS
                or source[0] == "q" and number in PVP_QUESTS):
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


def slot_ranking(db, cls: str, spec: int, mode: str, slot: str) -> simulated.SlotRanking | None:
    """The measured scores used in this cap-level EasyBIS slot, including the cat’s calibrated gear."""
    if not simulated.IN_USE or not getattr(db, "simulated", None):
        return None
    return simulated.ranking(db, cls, spec, mode, slot) or feral_gear.ranking(db, cls, spec, mode, slot)


@lru_cache(maxsize=1)
def _balance_weapon_sets():
    source = Path(__file__).parent / "corrections" / "balance_weapon_sets.json"
    return json.loads(source.read_text(encoding="utf-8"))


class ArmsHelms(list):
    """Keep the raid ranking and recommend one costly hit helm to craft for pre-raid Arms."""

    def __init__(self, entries):
        super().__init__(entries)
        self.pre_raid = [entry for entry in entries if entry.phase == phases.PRE_RAID]
        helms = {entry.item_id: entry for entry in self.pre_raid}
        lionheart, stalwart = helms.get(12640), helms.get(250599)
        if lionheart and stalwart and lionheart.score > stalwart.score:
            # Keep Stalwart if it offers a route to hit for someone who cannot get Lionheart.
            if all(not stalwart.passes(flt) or lionheart.passes(flt)
                   for flt in FILTERS if flt[3] == phases.PRE_RAID):
                self.pre_raid = [entry for entry in self.pre_raid if entry != stalwart]


def full_ladder(db, cls: str, spec: int, mode: str, slot: str, level: int | None = None,
                rank_rewards: bool = True) -> list[Entry]:
    entries = _ranked_ladder(db, cls, spec, mode, slot, level, rank_rewards)
    if not rank_rewards or (level is not None and level != db.meta["cap"]):
        return entries
    if slot == "ranged" and cls in relics.CLASSES:
        return relics.ranking(db, cls, spec, mode, entries)
    options = []
    for item_id in situational_gear.item_ids(cls, spec, mode, slot):
        if (cls, spec, item_id) == ("DRUID", 2, 11810):
            # The bear has a dedicated fourth-place pre-raid recommendation.
            continue
        item = db.items.get(item_id)
        gear = db.gear.get(item_id)
        if not item or not gear or gear["req"] > db.meta["cap"]:
            continue
        flags = item["flags"]
        options.append(Entry(item_id=item_id, score=0, side=item["side"], twin=item["twin"],
                             seen="s" in flags, new="n" in flags, unique="U" in flags, random="r" in flags,
                             unsourced=not bool(item["groups"] & SOURCE_GROUPS), two_hand=False, limit=item["limit"],
                             phase=phases.item_phase(item), pvp=pvp_reward(item), rank=ranks.required(item, gear),
                             honor=ranks.sold_for_honor(item), pvp_utility=True))
    if options:
        entries = _annotatable(entries)
        entries.options = options
    return entries


def _ranked_ladder(db, cls: str, spec: int, mode: str, slot: str, level: int | None, rank_rewards: bool):
    """Every pick for the slot, best first, with no faction or source filter applied.

    rank_rewards=False is foreverdb.net/bis's rule: the PvP-rank rewards are left out of the PvE list, and a
    Hunter's list keeps what is held in the off hand.
    """
    level = level or db.meta["cap"]
    data = db.classes[cls]
    spec_def = data["specs"][spec]
    profile = MODES[mode]
    weights = spec_def["weights"][profile]
    if slot == "trinket" and spec_def["role"] in {"Healer", "Caster DPS"} and 32 in weights:
        # These profiles get their crit value from spells. Never credit a melee crit for the Eye.
        weights = {caster_gear.SPELL_CRIT_RATING: weights[32], **weights}
    if mode == "pvp" and (level != db.meta["cap"] or not rank_rewards):
        weights = dict(weights)
        weights.pop("weapon_hit", None)
        if db.specs and (cls, spec) in db.specs.humanoid_power:
            weights.pop(specs.HUMANOID_ATTACK_POWER, None)
    groups = SOURCE_GROUPS if rank_rewards or mode != "pve" else SOURCE_GROUPS - {PVP_RANK_GROUP}
    healer, hunter = spec_def["role"] == "Healer", cls == "HUNTER"
    dual_wields = level >= db.dual_wield.get(cls, 99)
    min_score = data["min"].get(profile, 1)
    # The specs a simulator ranked (simulated.py). The site's rule and other levels stay on the weights.
    ours = rank_rewards and level == db.meta["cap"]
    ranked = slot_ranking(db, cls, spec, mode, slot) if ours else None
    trinkets = (getattr(db, "pre_raid_trinkets", {}).get((cls, spec), {})
                if ranked and mode == "pve" and slot == "trinket" else {})
    pre_measured = {int(item) for side in ("a", "h") for item, row in trinkets.get(slot, {}).get(side, {}).items()
                    if row[3] == "measured" and row[0] is not None}
    arm_epaulets = {}
    if ours and (cls, spec, mode, slot) == ("WARRIOR", 1, "pve", "shoulder"):
        # The Warrior pool only includes the Alliance mail shoulders. Both factions' versions
        # have identical stats and acquisition flags, and matched exactly in the paired Arms run.
        alliance, horde = db.items.get(271956), db.items.get(272106)
        if (alliance and horde and (alliance["side"], horde["side"]) == ("a", "h")
                and db.gear.get(271956) and db.gear[271956] == db.gear.get(272106)
                and all(alliance[key] == horde[key] for key in ("flags", "limit", "groups"))
                and phases.item_phase(alliance) == phases.item_phase(horde)):
            arm_epaulets = {271956: 272106, 272106: 271956}
    placed = getattr(db, "placed", None) or {}   # the items put by hand after another one (corrections/effects.json)
    class_only = getattr(db, "class_only", None) or {}   # the classes of an item the game restricts (corrections/classes.json)
    # In a PvP list, which no simulator ranks: a Survival Hunter fights in melee, so its weapon's damage counts, and
    # an Assassination Rogue's Mutilate asks for a dagger in each hand.
    melee = ours and mode == "pvp" and hunter and spec_def["role"] == MELEE
    daggers = ours and mode == "pvp" and slot in DAGGERS_ONLY.get((cls, spec_def.get("slug")), ())
    # What the weights cannot value (specs.unvalued) is listed whatever they give it: it stands level with the best.
    level_ids = specs.unvalued(db, cls, spec) if ours and ranked is None else frozenset()
    bonuses = {}
    if ours and ranked is None and (mode, slot) == ("pve", "trinket"):
        bonuses = specs.tank_trinket_bonuses(cls, spec, weights)
        level_ids = level_ids.difference(bonuses)
    two_hand_scores = {}
    if (ours and simulated.IN_USE and (cls, spec_def.get("slug"), mode, slot)
            == ("DRUID", "feral-cat", "pve", "main")):
        anchor = score(db, 12583, weights, cls)
        if anchor is not None:
            two_hand_scores = feral_gear.calibrated_two_hand_scores(anchor, weights[specs.ATTACK_POWER])

    entries, seen_ids, weighed = [], set(), {}
    for pool in dict(SLOTS)[slot]:
        # A spec that is not ForeverDB's may have candidates of its own next to the class's (shockadin.borrowed).
        for item_id, item_level in (*data["pools"].get(pool, ()), *spec_def.get("pools", {}).get(pool, ())):
            if item_level > level or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            gear, item = db.gear.get(item_id), db.items.get(item_id)
            if gear is None or item is None:
                continue
            if cls not in class_only.get(item_id, (cls,)):
                continue   # another class's piece: ForeverDB pools by armor type
            if daggers and gear["kind"] != DAGGER:
                continue
            stats = gear["stats"]
            if not _fits_style(pool, gear["inv"], spec_def["style"], dual_wields):
                continue
            if hunter and gear["inv"] == INV_THROWN:
                continue
            if hunter and rank_rewards and gear["inv"] == INV_HELD:
                continue
            if (not healer and HEALING in stats and not any(stat in stats for stat in SPELL_DAMAGE)
                    and not (specs.FERAL_ATTACK_POWER in stats and specs.FERAL_ATTACK_POWER in weights)):
                continue
            sourced = bool(item["groups"] & groups)
            if not sourced and "u" not in item["groups"]:
                continue
            value = (score(db, item_id, weights, cls, melee) or 0.0) + bonuses.get(item_id, 0)
            value = two_hand_scores.get(item_id, value)
            armour_only = gear["armor"] > 0 and not gear["dps"] and not stats
            # A list ranked by simulation also holds what the weights give nothing and the simulator measures: a
            # trinket that is all proc, a weapon a Hunter only holds. The weights say what to list only where they rank.
            measured = ranked is not None and (ranked.scores.get(item_id, 0) > 0 or item_id in placed)
            if not (value >= min_score or (value > 0 and armour_only) or measured or item_id in level_ids
                    or item_id in pre_measured):
                continue
            flags = item["flags"]
            twin = item["twin"] or arm_epaulets.get(item_id)
            if cls not in class_only.get(twin, (cls,)):
                twin = None
            weighed[item_id] = value
            entries.append(Entry(
                item_id=item_id, score=ranked.value(item_id, value) if ranked else value,
                side=item["side"], twin=twin,
                seen="s" in flags, new="n" in flags, unique="U" in flags,
                unsourced=not sourced or (rank_rewards and reputations.unconfirmed_watcher_ring(item)),
                two_hand=gear["inv"] == INV_TWO_HAND, random="r" in flags, limit=item["limit"],
                phase=phases.item_phase(item), pvp=pvp_reward(item),
                preraid_option=(ours and mode == "pvp" and slot == "main" and
                                item_id in PRERAID_MELEE_OPTIONS.get((cls, spec), ())),
                rank=ranks.required(item, gear), honor=ranks.sold_for_honor(item),
                estimated=ranked is not None and not ranked.measured(item_id)))

    # A few twin pairs have both ids in the pool: keep the Alliance one, which names the other as its twin.
    ids = {entry.item_id for entry in entries}
    entries = [entry for entry in entries if not (entry.side == "h" and entry.twin in ids)]
    entries.sort(key=lambda entry: (-entry.score, -weighed[entry.item_id], entry.item_id))
    if rank_rewards and level == db.meta["cap"]:
        entries = simulated.place(entries, simulated.placements(db, cls, spec, mode, slot))
        if ranked is None:
            entries = level_with_the_best(entries, level_ids)
        else:
            entries = after_their_anchor(entries, placed)
    if ours and mode == "pvp" and slot == "trinket" and pvp_insignia.ALLIANCE in db.items:
        entries = [entry for entry in entries if entry.item_id not in (pvp_insignia.ALLIANCE, pvp_insignia.HORDE)]
        entries.append(Entry(item_id=pvp_insignia.ALLIANCE, side="a", twin=pvp_insignia.HORDE, score=0,
                             seen=True, new=True, unique=True, two_hand=False, random=False, unsourced=False,
                             limit=None, pvp=True, rank=pvp_insignia.RANK, honor=True, pvp_utility=True))
    if ranked and (cls, spec, mode, slot) == ("DRUID", 1, "pve", "main"):
        rules = _balance_weapon_sets()
        enchants = db.enchants.get(cls, {}).get((spec, "raid"), {}).get("w2h", [])
        spell = rules["spellblasting"]
        if any(key == spell and required <= level for key, required in enchants) and phases.enchant_phase(db, spell) == phases.PRE_RAID:
            wins = [(side, staff, one, off) for side, tests in rules["by_side"].items()
                    for staff, one, off, gain, error in tests if gain > 2 * error]
            entries = [replace(e, pre_raid_weapon_sets=tuple(
                (side, one, off) for side, staff, one, off in wins if e.shown(side) == staff
            )) if e.two_hand else e for e in entries]
    if ranked and (cls, spec, mode, slot) == ("DRUID", 4, "pve", "trinket"):
        return feral_gear.PreRaidTrinkets(entries)
    if ours and ranked is None and (cls, spec, mode, slot) == ("DRUID", 2, "pve", "trinket"):
        return feral_gear.BearTrinkets(entries)
    if ours and (cls, spec, mode, slot) == ("WARRIOR", 1, "pve", "head"):
        return ArmsHelms(entries)
    if ranked and (cls, spec, mode) == ("HUNTER", 1, "pve") and slot in hunter_bm.SLOTS:
        return hunter_bm.contextual_ladder(entries, slot, weighed)
    if ranked and mode == "pve":
        calibrated = db.simulated.by_faction.get((cls, spec), {})
        pre_contexts = hunter_bm.rank_contexts(entries, slot, weighed, trinkets).contexts if trinkets else None
        if slot in calibrated:
            result = hunter_bm.rank_contexts(entries, slot, weighed, calibrated)
            if placed and any(entry.placed for entry in entries):
                result.contexts = {key: after_their_anchor(rows, placed) for key, rows in result.contexts.items()}
            entries = result
        if pre_contexts:
            entries = _annotatable(entries)
            entries.pre_contexts = pre_contexts
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
    first = next((entry for entry in entries if not entry.unscored), None)
    if first:
        return first
    if entries and not (entries[0].estimated or entries[0].alternative_only or entries[0].pvp_utility):
        return entries[0]
    return None


def picks(slot: str, visible: list[Entry], alternatives: int = ALTERNATIVES) -> tuple[list[Entry], list[Entry]]:
    """(best, alternatives) among the entries a character can see; alternatives: how many it asks for.

    Rings and trinkets have two best picks: the second is the next one that can
    be worn with the first (not from the same "only one of these" category).
    That second pick is one of the alternatives asked for: a slot lists the
    best pick and at most `alternatives` items after it, whatever the slot.
    """
    if not visible:
        return [], []
    if visible[-1].pvp_utility:
        best, others = picks(slot, visible[:-1], alternatives)
        position = max(0, 3 - len(best)) if visible[-1].fourth_option else len(others)
        others.insert(position, visible[-1])
        return best, others
    first = lead(visible)
    if first is None:
        return [], visible[:alternatives]
    best = [first]
    if slot in PAIRED:
        second = next((e for e in visible if e is not first and not e.unscored
                       and not (first.limit and e.limit == first.limit)), None)
        if second:
            best.append(second)
    others = [entry for entry in visible if entry not in best]
    return best, others[:alternatives - (len(best) - 1)]


def _weapon_styles(main: list[Entry], off: list[Entry]):
    """Score the same distinct main-hand and off-hand picks that the addon offers together."""
    two = [entry for entry in main if entry.two_hand]
    one = [entry for entry in main if not entry.two_hand]
    two_best, one_best = lead(two), lead(one)
    others = [entry for entry in off if entry.item_id != one_best.item_id] if one_best else []
    off_best = lead(others)
    side = two_best.weapon_set_side if two_best else None
    measured = bool(side and one_best and off_best and
                    (side, one_best.shown(side), off_best.shown(side)) in two_best.pre_raid_weapon_sets)
    if two_best and (not one_best or measured or two_best.stored >= one_best.stored + (off_best.stored if off_best else 0)):
        return (two, []), (one, others)
    if not one_best:
        return (main, off), ([], [])
    return (one, others), (two, [])


def weapon_lists(main: list[Entry], off: list[Entry]) -> tuple[list[Entry], list[Entry]]:
    """Main-hand and off-hand lists for the higher scoring weapon style."""
    return _weapon_styles(main, off)[0]


def other_weapons(main: list[Entry], off: list[Entry]) -> tuple[list[Entry], list[Entry]]:
    """The weapons of the style weapon_lists set aside, to offer as alternatives: (main hand, off hand).

    When the two-handers win: the one-handers, and the off hands that go with
    them (the best one-hander itself left out, as in weapon_lists). When the
    one-handers win: the two-handers, and no off hand. A spec that only has one
    of the two styles has nothing else to offer.
    """
    return _weapon_styles(main, off)[1]


def _needed(slot: str, visible: list[Entry]) -> list[Entry]:
    """What the addon reads of a slot's ladder under one filter (see picks and weapon_lists), with as many
    alternatives as a player can ask for: what he sees with fewer is the start of it."""
    best, alternatives = picks(slot, visible, MAX_ALTERNATIVES)
    needed = best + alternatives
    if slot == "main":
        for two_hand in (True, False):
            style = [entry for entry in visible if entry.two_hand == two_hand]
            needed.extend(style[:1 + MAX_ALTERNATIVES])  # also offered when this style loses
            first = lead(style)
            if first:
                needed.append(first)
    elif slot == "off":
        # A main-hand pick can remove either a displayed alternative or the first measured off-hand.
        needed = visible[:2 + MAX_ALTERNATIVES]
        needed.extend([entry for entry in visible if not entry.unscored][:2])
    return needed


def _contexts(entries, phase):
    if phase == phases.PRE_RAID and hasattr(entries, "pre_contexts"):
        return entries.pre_contexts
    return getattr(entries, "contexts", {})


def visible(entries: list[Entry], flt, companion: int | None = None) -> list[Entry]:
    """Ordered entries for a filter and its equipped companion, if one was measured."""
    pre_raid = flt[3] == phases.PRE_RAID
    extra = [e for e in getattr(entries, "options", ()) if pre_raid and e.passes(flt)]
    replaced = {e.shown(flt[0]) for e in extra}
    contexts = _contexts(entries, flt[3])
    if contexts:
        entries = contexts.get((flt[0], companion), ())
    elif pre_raid and hasattr(entries, "pre_raid"):
        entries = entries.pre_raid
    eligible = [replace(e, weapon_set_side=flt[0]) if e.pre_raid_weapon_sets and pre_raid else e
                for e in entries if e.passes(flt) and e.shown(flt[0]) not in replaced]
    if pre_raid:
        options = [replace(e, score=0, pvp_utility=True) for e in eligible if e.preraid_option]
        if options:
            eligible = [e for e in eligible if not e.preraid_option] + options
    return eligible + extra


def visible_slots(slots: dict, flt) -> dict:
    """Visible entries before the comparison of one-handed and two-handed sets."""
    result = {slot: visible(entries, flt) for slot, entries in slots.items()}
    for slot in PAIRED:
        ladder = slots.get(slot)
        contexts = _contexts(ladder, flt[3])
        if not contexts:
            continue
        first = lead(result[slot])
        if first and (flt[0], first.shown(flt[0])) in contexts:
            result[slot] = [first, *visible(ladder, flt, first.shown(flt[0]))]
    if isinstance(slots.get("off"), hunter_bm.ContextLadder):
        main = lead([entry for entry in result.get("main", ()) if not entry.two_hand])
        main_id = main.shown(flt[0]) if main else None
        if main_id and (flt[0], main_id) in slots["off"].contexts:
            result["off"] = visible(slots["off"], flt, main_id)
    return result


class OptionLadder(list):
    """Ordinary entries with additional pre-raid recommendations."""


def _annotatable(entries):
    return OptionLadder(entries) if type(entries) is list else entries


def kept_ladder(slot: str, ladder: list[Entry]) -> list[Entry]:
    """The part of the ladder the addon needs, whatever it filters on."""
    kept = _kept_ladder(slot, ladder)
    if hasattr(ladder, "pre_contexts"):
        kept = _annotatable(kept)
        kept.pre_contexts = _keep_contexts(slot, ladder.pre_contexts, pre_raid=True)
    if hasattr(ladder, "options"):
        kept = _annotatable(kept)
        kept.options = ladder.options
    return kept


def _keep_contexts(slot, source, pre_raid=False):
    contexts = {}
    for key, candidates in source.items():
        keep = set()
        for flt in FILTERS:
            if flt[0] != key[0] or (pre_raid and flt[3] != phases.PRE_RAID):
                continue
            eligible = [entry for entry in candidates if entry.passes(flt)]
            groups = ([e for e in eligible if e.two_hand], [e for e in eligible if not e.two_hand]) \
                if slot == "main" else (eligible,)
            for group in groups:
                best, alts = picks(slot, group, MAX_ALTERNATIVES)
                keep.update(best + alts)
                if slot in ("main", "off"):
                    keep.update(group[:1 + MAX_ALTERNATIVES])
        contexts[key] = [entry for entry in candidates if entry in keep]
    return contexts


def _kept_ladder(slot, ladder):
    if isinstance(ladder, hunter_bm.ContextLadder):
        # Older clients read only L rows. Keep every entry their original order needs,
        # as well as all new entries selected by any supported faction or weapon.
        contexts = _keep_contexts(slot, ladder.contexts)
        ids = {entry.item_id for entry in kept_ladder(slot, list(ladder))}
        ids.update(e.item_id for rows in contexts.values() for e in rows)
        return hunter_bm.ContextLadder([entry for entry in ladder if entry.item_id in ids], contexts)
    if hasattr(ladder, "pre_raid"):
        ids = {e.item_id for flt in FILTERS for e in _needed(slot, visible(ladder, flt))}
        return type(ladder)([e for e in ladder if e.item_id in ids])
    keep = {entry for entry in ladder if entry.preraid_option}
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
