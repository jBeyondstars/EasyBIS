"""The Consumables tab's lists: per class, spec, list and category, what the weights make of each consumable.

    build(db)                   {class: {spec: {"pve" or "pvp": {category: Shelf}}}}
    shown(entries, phase)       what a character of that content phase sees of a Shelf's ranked entries
    situational(db, cls)        the protection and utility potions a class can use, listed without rank
    info_rows(db, ids)          {item: (name, effect, where it comes from, origin label, zone rule)}
    coach_differences(db, ...)  ForeverDB's coach against these lists (tests/compare_coach.py prints it)

What is ranked. A flask, elixir, food, scroll, weapon stone or oil and combat potion scores the sum of weight x stat
of the spec's "raid" weights in the PvE list and "pvp" weights in the PvP list. A healing potion, a mana potion and
a bandage score the amount they restore. The PER_CATEGORY best are kept for each content phase, and what ties with
the last of them, since nothing tells those apart.

The rules that go with that score:
  - A conditional effect (one zone, one kind of creature) counts for nothing; the effect's text keeps the condition.
  - An effect on spells alone counts for casters and healers, one on a melee weapon for melee and tanks.
  - Flat weapon damage counts as WEAPON_SPEED makes it: damage per second, at the spec's "dps" weight.
  - What the weights do not cover (maximum health, maximum mana, resistances) is not converted into a stat: an item
    whose whole worth is that is listed without rank, the strongest of each kind.
  - An item usable in one place only (a battleground's bandage) is in the PvP list alone.
  - An item whose tooltip names the classes that can use it is listed for those classes alone.
  - An item the game holds twice is listed once, the one that is easiest to get, and a weaker rank of a scroll is left
    out as soon as the stronger one can be had.
  - A stone for sharp weapons and one for blunt weapons of the same worth share a place: the weapon decides which is
    of use, so both are shown and they count as one of the PER_CATEGORY.
  - Warriors and rogues have no mana: nothing that only gives mana is listed for them.
  - What players cannot get (corrections/recipe_origins.json, unobtainable) is not listed.

Every list stands alone. Nothing here says how the categories stack or that they make a set: how consumables stack
in Forever is only partly known.

A content phase is that of the easiest way to get the item. A recipe that only raid bosses drop needs that raid. An
item with no known source at all counts once every phase does, as the pieces added from the game do.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import consumables
import phases

PER_CATEGORY = 3
WEAPON_SPEED = 2.5   # seconds: an average weapon's, to turn flat damage into damage per second
MODES = {"pve": "raid", "pvp": "pvp"}
SCORED = ("flask", "elixir", "food", "scroll", "weapon", "combat")
RESTORED = {"healing": "health", "mana": "mana", "bandage": "health"}
SITUATIONAL = "situational"
CATEGORIES = (*SCORED, *RESTORED, SITUATIONAL)   # the order the tab shows them in
UNRANKED_IN = ("flask", "elixir", "combat")      # where an effect the weights do not cover is listed without rank

NO_MANA = frozenset({"WARRIOR", "ROGUE"})
CASTERS = frozenset({"Caster DPS", "Healer"})
MELEE = frozenset({"Melee DPS", "Tank"})
NOT_FOR_THE_CAP = frozenset({"Level boosts"})   # a family of no use to a character of the lists' level
UNKNOWN_WHERE = "where it comes from isn't known yet"
ORIGIN = "f"   # read from the game client
ORIGINS_FILE = Path(__file__).resolve().parent / "corrections" / "recipe_origins.json"
_ORIGIN_SAID = {"sold": "recipe sold by", "quest": "recipe from the quest", "drops": "recipe drops from",
                "found": "recipe found in"}

_RESISTANCES = frozenset(consumables.RESISTANCES.values())
# Molten Core is not among the instances of ForeverDB's data, which names the others' bosses.
_MOLTEN_CORE = ("Lucifron", "Magmadar", "Gehennas", "Garr", "Shazzrah", "Baron Geddon", "Golemagg the Incinerator",
                "Sulfuron Harbinger", "Majordomo Executus", "Ragnaros")
_ON_A_MELEE_WEAPON = re.compile(r"\b(?:melee|blunt|sharp|sharpened) weapon\b", re.I)
_EDGE = re.compile(r"\b(sharp|blunt) weapon\b", re.I)
_RANK = re.compile(r" (?:II|III|IV|V|VI)$")


@dataclass
class Shelf:
    """One category of one list."""
    ranked: list = field(default_factory=list)     # (item, phase, score x 10), best first
    unranked: list = field(default_factory=list)   # (item, phase)
    twins: frozenset = frozenset()                 # the ranked items that share the place of the entry before them


def _key(stat: str):
    return int(stat) if stat.isdigit() else stat


def score(record: dict, weights: dict, role: str) -> float:
    """Weight x stat of what a consumable gives everywhere and to everyone."""
    melee_only = bool(_ON_A_MELEE_WEAPON.search(record.get("text", "")))
    if melee_only and role not in MELEE:
        return 0.0
    total = sum(weights.get(_key(stat), 0) * value for stat, value in record.get("stats", {}).items())
    if role in CASTERS:
        total += sum(weights.get(_key(stat), 0) * value for stat, value in record.get("spell_stats", {}).items())
    damage = record.get("extras", {}).get(consumables.WEAPON_DAMAGE, 0)
    return total + weights.get("dps", 0) * damage / WEAPON_SPEED


def _uncovered(record: dict, cls: str) -> dict:
    """What a consumable gives that no weight covers: {kind: strength}."""
    extras = record.get("extras", {})
    found = {}
    if extras.get(consumables.MAX_HEALTH):
        found["health"] = extras[consumables.MAX_HEALTH]
    if extras.get(consumables.MAX_MANA) and cls not in NO_MANA:
        found["mana"] = extras[consumables.MAX_MANA]
    resistances = [value for stat, value in record.get("stats", {}).items() if _key(stat) in _RESISTANCES]
    if resistances:
        found["resistance"] = sum(resistances)
    return found


# -- where it comes from ------------------------------------------------------------------------------------

def _raid_bosses(db) -> dict:
    """{boss name: raid}, from the raids' boss lists and the drops of the gear's source list."""
    bosses = dict.fromkeys(_MOLTEN_CORE, "mc")
    for number, fields in db.instances.items():
        if len(fields) > 7 and fields[1] == "raid":
            for name in fields[7].split(";"):
                bosses[name] = phases.RAID_INSTANCES.get(number, phases.NEW_RAID)
    for item in db.items.values():
        for source in item["sources"]:
            if source[0] == "d" and len(source) > 4 and source[4] == "1" and source[1].isdigit():
                bosses[source[2]] = phases.RAID_INSTANCES.get(int(source[1]), phases.NEW_RAID)
    return bosses


def _recipe_phase(facts: dict, bosses: dict) -> int:
    """The phase a recipe item needs: that of a raid when raid bosses are the only ones to drop it."""
    drops = facts.get("drops", ())
    if not drops or facts.get("vendors") or facts.get("quests") or not all(name in bosses for name in drops):
        return phases.PRE_RAID
    return min(phases.raid_phase(bosses[name]) for name in drops)


def item_phase(item: int, data, bosses: dict) -> int:
    """The content phase of a consumable (phases.enchant_phase's rule, for what recipes and sources say)."""
    facts = data.facts.get(item) or {}
    if facts.get("vendors") or facts.get("quests") or facts.get("drops"):
        return phases.PRE_RAID
    recipes = data.recipes.get(item, ())
    if not recipes:
        return phases.PRE_RAID if item in load_origins() else phases.LATER
    return min(_recipe_phase(data.facts.get(_recipe_item(recipe)) or {}, bosses) for recipe in recipes)


def _recipe_item(recipe: dict) -> int:
    learned = recipe["learned"]
    return int(learned[1:]) if learned[:1] == "i" and learned[1:].isdigit() else 0


@lru_cache(maxsize=None)
def load_origins(path=ORIGINS_FILE) -> dict:
    """{consumable: how corrections/recipe_origins.json says it is had}"""
    return {int(item): entry for item, entry in json.loads(path.read_text(encoding="utf-8"))["recipes"].items()}


@lru_cache(maxsize=None)
def unobtainable(path=ORIGINS_FILE) -> frozenset:
    """The consumables players cannot get, whatever they are worth."""
    return frozenset(int(item) for item in json.loads(path.read_text(encoding="utf-8"))["unobtainable"])


def _learned(recipe: dict, data, origin: dict) -> str:
    """How a recipe is learned, ForeverDB's data first; empty when nothing says."""
    if recipe["learned"] in ("t", "a"):
        return "from a trainer"
    taught = data.facts.get(_recipe_item(recipe)) or {}
    if taught.get("vendors"):
        _, vendor, zone = taught["vendors"][0]
        return f"recipe sold by {vendor} ({zone})"
    if taught.get("quests"):
        return f"recipe from the quest {taught['quests'][0]}"
    if taught.get("drops"):
        return f"recipe drops from {taught['drops'][0]}"
    return next((f"{said} {origin[key]}" for key, said in _ORIGIN_SAID.items() if key in origin), "")


def where(item: int, data, origins=None) -> str:
    """Where a consumable comes from, in the sentence Consumables.lua reads.

    A recipe nobody can place does not hide a vendor, a quest or a drop that gives the item itself."""
    facts = data.facts.get(item) or {}
    recipes = data.recipes.get(item, ())
    lead = ""
    if recipes:
        recipe = recipes[0]
        made = max((skill for _, skill in facts.get("made", ())), default=0)
        lead = f"{recipe['profession']} {recipe['skill'] or made}: "
        learned = _learned(recipe, data, (origins or {}).get(item, {}))
        if learned:
            return lead + learned
    if facts.get("vendors"):
        _, vendor, zone = facts["vendors"][0]
        return f"Vendor: {vendor} ({zone})"
    if facts.get("quests"):
        return f"Quest: {facts['quests'][0]}"
    if facts.get("drops"):
        return f"Drop: {facts['drops'][0]}"
    if recipes:
        return lead + "recipe, source unknown"
    container = (origins or {}).get(item, {}).get("container")
    return f"Container: {container}" if container else UNKNOWN_WHERE


# -- what it does, in a few words ------------------------------------------------------------------------------

_NAMES = {
    consumables.AGILITY: "Agility", consumables.STRENGTH: "Strength", consumables.INTELLECT: "Intellect",
    consumables.SPIRIT: "Spirit", consumables.STAMINA: "Stamina", consumables.ARMOR: "Armor",
    consumables.DODGE: "Dodge", consumables.PARRY: "Parry", consumables.BLOCK: "Block", consumables.HIT: "Hit",
    consumables.CRIT: "Critical Strike", consumables.HASTE: "Haste", consumables.ATTACK_POWER: "Attack Power",
    consumables.RANGED_ATTACK_POWER: "Ranged Attack Power", consumables.HEALING: "Healing",
    consumables.SPELL_DAMAGE: "Spell Damage", consumables.SPELL_POWER: "Spell Damage and Healing",
    consumables.MANA_REGEN: "Mana per 5 sec", consumables.HEALTH_REGEN: "Health per 5 sec",
    consumables.BLOCK_VALUE: "Block Value", consumables.LESS_DODGED: "less chance to be dodged or parried",
}
_NAMES.update({stat: f"{school.capitalize()} Resistance" for school, stat in consumables.RESISTANCES.items()})
_NAMES.update({stat: f"{school.capitalize()} Spell Damage" for school, stat in consumables.SCHOOLS.items()})
_EXTRAS = {consumables.MAX_HEALTH: "Maximum Health", consumables.MAX_MANA: "Maximum Mana",
           consumables.WEAPON_DAMAGE: "Weapon Damage", consumables.RAGE: "Rage"}


def _amount(stat, value, spells: bool = False) -> str:
    name = _NAMES.get(stat, str(stat))
    if stat == consumables.LESS_DODGED:
        return f"{consumables._number(value)}% {name}"
    if spells:
        name = f"Spell {name}"
    rate = consumables.RATING_PER_PERCENT.get(stat)
    if rate:
        return f"{value / rate:+g}% {name}"
    return f"{value:+g} {name}"


def _stat_parts(block: dict, spells: bool = False) -> list:
    stats = {_key(stat): value for stat, value in block.items()}
    parts = []
    shared = {stats[stat] for stat in _RESISTANCES if stat in stats}
    if len(shared) == 1 and all(stat in stats for stat in _RESISTANCES):
        parts.append(f"{shared.pop():+g} All Resistances")
        stats = {stat: value for stat, value in stats.items() if stat not in _RESISTANCES}
    # what is in percent comes after the flat stats, whatever the order the reading keeps them in
    ordered = sorted(stats.items(), key=lambda pair: pair[0] in consumables.RATING_PER_PERCENT)
    return parts + [_amount(stat, value, spells) for stat, value in ordered]


def _restored(record: dict) -> list:
    parts = []
    for what, amount in record.get("restores", {}).items():
        low, high = record.get("ranges", {}).get(what, (amount, amount))
        parts.append(f"Restores {low} to {high} {what}" if low != high else f"Restores {consumables._number(amount)} {what}")
    return parts


def effect(record: dict) -> str:
    """What a consumable does, with the condition its bonus depends on."""
    parts = [*_stat_parts(record.get("stats", {})), *_stat_parts(record.get("spell_stats", {}), spells=True)]
    parts += [f"{value:+g} {_EXTRAS[name]}" for name, value in record.get("extras", {}).items() if name in _EXTRAS]
    if record.get("conditional"):
        condition = record.get("condition") or {}
        link = "against" if condition.get("kind") == "creature" else "in"
        parts.append(f"{', '.join(_stat_parts(record['conditional']))} {link} {condition.get('what', '?')} only")
    parts += _restored(record) + list(record.get("utility", ()))
    if record.get("only"):
        parts.append(f"usable only in {record['only']}")
    return re.sub(r"\s+", " ", "; ".join(parts)).replace("|", "/")


def zone_rule(record: dict) -> str:
    """"only:<place>" for what can be used nowhere else, "bonus:<place>" for a bonus that works there alone."""
    if record.get("only"):
        return f"only:{record['only']}"
    condition = record.get("condition") or {}
    if record.get("conditional") and condition.get("kind") == "zone":
        return f"bonus:{condition['what']}"
    return ""


# -- the lists ----------------------------------------------------------------------------------------------

def shown(entries: list, phase: int, count: int = PER_CATEGORY, twins=frozenset()) -> list:
    """The ranked entries a content phase sees: the `count` best, and what ties with the last of them. An item of
    `twins` goes with the entry before it and takes no place of its own."""
    kept, places = [], 0
    for entry in entries:
        if entry[1] > phase:
            continue
        if entry[0] not in twins:
            if places >= count and entry[2] != kept[-1][2]:
                break
            places += 1
        kept.append(entry)
    return kept


def _keep(entries: list, twins=frozenset()) -> list:
    """What some content phase shows of entries that are sorted best first."""
    kept = set()
    for phase in phases.PHASES:
        kept.update(shown(entries, phase, twins=twins))
    return [entry for entry in entries if entry in kept]


def _readable(records: dict) -> dict:
    """The readings a list may use: an item with a phrase that was not understood is not ranked on a part of it,
    and what players cannot get is not offered."""
    return {item: record for item, record in records.items() if not record.get("unread") and item not in unobtainable()}


def _for_class(record: dict, cls: str) -> bool:
    return cls in record.get("classes", (cls,))


def _usable(record: dict, mode: str, cls: str) -> bool:
    return (mode == "pvp" or not record.get("only")) and _for_class(record, cls)


def _distinct(entries: list, records: dict) -> list:
    """Of entries sorted best first, what nothing above replaces: an entry of the same name, or a stronger rank of it,
    that can be had no later. A weaker rank that comes earlier stays for the phases before the stronger one."""
    available, kept = {}, []
    for entry in entries:
        base = _RANK.sub("", records[entry[0]]["name"])
        if available.get(base, entry[1] + 1) > entry[1]:
            available[base] = entry[1]
            kept.append(entry)
    return kept


def _edge(record: dict) -> str | None:
    found = _EDGE.search(record.get("text", ""))
    return found[1].lower() if found else None


def _twins(entries: list, records: dict) -> frozenset:
    """Of entries sorted best first, the second of each pair of a sharp and a blunt stone of the same worth and phase."""
    twins = set()
    for before, entry in zip(entries, entries[1:]):
        edges = {_edge(records[before[0]]), _edge(records[entry[0]])}
        if edges == {"sharp", "blunt"} and before[1:] == entry[1:] and before[0] not in twins:
            twins.add(entry[0])
    return frozenset(twins)


def _shelf(cls: str, role: str, weights: dict, mode: str, category: str, records: dict, item_phases: dict) -> Shelf:
    shelf = Shelf()
    scored, strongest = [], {}
    restored = RESTORED.get(category)
    for item, record in records.items():
        if not _usable(record, mode, cls):
            continue
        if restored:
            # a potion that restores both counts on both lists
            amount = record.get("restores", {}).get(restored, 0)
            home = record["category"] == category or (category == "mana" and record["category"] == "healing")
            value = amount if home else 0
        else:
            value = score(record, weights, role) if record["category"] == category else 0
        if value > 0:
            scored.append((item, item_phases[item], round(value * 10)))
        elif category in UNRANKED_IN and record["category"] == category:
            for kind, strength in _uncovered(record, cls).items():
                if strength > strongest.get(kind, (0, 0))[0]:
                    strongest[kind] = (strength, item)
    # usable in one place, and no better than what is usable everywhere: the other one says it all
    free = {(entry[2], entry[1]) for entry in scored if not records[entry[0]].get("only")}
    scored = [entry for entry in scored if not records[entry[0]].get("only")
              or not any(value == entry[2] and phase <= entry[1] for value, phase in free)]
    ordered = _distinct(sorted(scored, key=lambda entry: (-entry[2], entry[1], entry[0])), records)
    twins = _twins(ordered, records)
    shelf.ranked = _keep(ordered, twins)
    shelf.twins = twins & {entry[0] for entry in shelf.ranked}
    listed = {entry[0] for entry in shelf.ranked}
    shelf.unranked = [(item, item_phases[item]) for item in sorted({item for _, item in strongest.values()}) if item not in listed]
    return shelf


def _waiting(data, records: dict) -> list:
    """The potions always read that the capture on file does not hold yet: listed by name until it does."""
    return [item for item in consumables.ALWAYS_READ if item in data.catalogue and item not in records]


def _kept_readings(db) -> tuple:
    data = db.consumables
    records = consumables.load().get("items", {}) if data is not None else {}
    if not records:
        return data, {}, {}
    bosses = _raid_bosses(db)
    return data, _readable(records), {item: item_phase(item, data, bosses) for item in (*records, *_waiting(data, records))}


def build(db) -> dict:
    """{class: {spec: {mode: {category: Shelf}}}}; a category with nothing to show is left out."""
    data, records, item_phases = _kept_readings(db)
    lists = {}
    for cls, class_def in db.classes.items():
        lists[cls] = {}
        for spec, spec_def in class_def["specs"].items():
            modes = lists[cls][spec] = {}
            for mode, profile in MODES.items():
                shelves = modes[mode] = {}
                for category in (*SCORED, *RESTORED):
                    if category == "mana" and cls in NO_MANA:
                        continue
                    shelf = _shelf(cls, spec_def["role"], spec_def["weights"][profile], mode, category, records, item_phases)
                    if shelf.ranked or shelf.unranked:
                        shelves[category] = shelf
    return lists


def situational(db, cls: str | None = None) -> list:
    """[(item, phase)] by name: what protects or helps, for a fight that asks for it. Without a class, every class's."""
    data, records, item_phases = _kept_readings(db)
    if not records:
        return []
    found = {item: record["name"] for item, record in records.items() if record["category"] == SITUATIONAL
             and data.catalogue.get(item, {}).get("family") not in NOT_FOR_THE_CAP
             and (cls is None or _for_class(record, cls))}
    found.update({item: data.catalogue[item]["name"] for item in _waiting(data, records)})
    return [(item, item_phases[item]) for item in sorted(found, key=lambda item: (found[item], item))]


def info_rows(db, ids) -> dict:
    """{item: (name, effect, where it comes from, origin label, zone rule)}"""
    data, records, _ = _kept_readings(db)
    origins = load_origins()
    rows = {}
    for item in ids:
        record = records.get(item)
        name = record["name"] if record else data.catalogue[item]["name"]
        rows[item] = (name, effect(record) if record else "", where(item, data, origins), ORIGIN,
                      zone_rule(record) if record else "")
    return rows


def used_ids(lists: dict, others=()) -> set:
    """Every item the lists name."""
    ids = {item for item, _ in others}
    for specs in lists.values():
        for modes in specs.values():
            for shelves in modes.values():
                for shelf in shelves.values():
                    ids.update(entry[0] for entry in shelf.ranked)
                    ids.update(item for item, _ in shelf.unranked)
    return ids


# -- ForeverDB's coach, as a second opinion ----------------------------------------------------------------------

@dataclass
class Difference:
    """A consumable the coach recommends that the spec's PvE list does not keep, and why."""
    cls: str
    spec: str
    item: int
    name: str
    category: str
    why: str

    def line(self) -> str:
        return f"{self.cls} {self.spec}: {self.name} ({self.item}), {self.category}: {self.why}"


def _spec_of(db, profile: str) -> tuple:
    """(class, spec number) of a coach's profile name ("hunter-beast-mastery"), or (None, None)."""
    token, _, slug = profile.partition("-")
    specs = db.classes.get(token.upper(), {}).get("specs", {})
    return next(((token.upper(), number) for number, spec in specs.items() if spec["slug"] == slug), (None, None))


def _gives_all_of(other: dict, record: dict) -> bool:
    """Whether `other` gives at least as much of every stat `record` gives, and something more."""
    theirs, mine = other.get("stats", {}), record.get("stats", {})
    return bool(mine) and theirs != mine and all(theirs.get(stat, 0) >= value for stat, value in mine.items())


def coach_differences(db, lists: dict) -> tuple:
    """(recommendations compared, [Difference]): each recommendation of the coach that is not kept, with the reason."""
    data, records, _ = _kept_readings(db)
    compared, found = 0, []
    for profile, coach in sorted(data.coach.items()):
        cls, spec = _spec_of(db, profile)
        if cls is None:
            continue
        spec_def = db.classes[cls]["specs"][spec]
        shelves = lists[cls][spec]["pve"]
        for item, name, _value in coach["entries"]:
            compared += 1
            record = records.get(item)
            note = lambda category, why: found.append(Difference(cls, spec_def["name"], item, name, category, why))
            if record is None:
                note("?", "its tooltip was not understood or not read in the game")
                continue
            category = record["category"]
            shelf = shelves.get(category)
            if shelf and any(entry[0] == item for entry in shelf.ranked):
                continue
            mine = score(record, spec_def["weights"]["raid"], spec_def["role"])
            kept = [entry[0] for entry in shelf.ranked] if shelf else []
            better = next((records[other]["name"] for other in kept if _gives_all_of(records[other], record)), None)
            note(category, (f"{better} gives all of it and more; " if better else "")
                 + f"scores {mine:g} on the spec's weights; kept instead: "
                 + (", ".join(f"{records[other]['name']} ({entry / 10:g})" for other, _, entry in shelf.ranked) if kept else "nothing"))
    return compared, found
