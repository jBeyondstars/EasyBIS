"""Read ForeverDB's addon data files (https://foreverdb.net) as plain text.

Nothing in those files is executed: they are Lua sources, parsed here with
regular expressions. The formats are the ones ForeverDB's own GearFinder.lua
and Auto.lua decode. ForeverDB's data is GPL-3.0 with an attribution term:
"Data from ForeverDB.net (https://foreverdb.net)".

load() lays what was read in the game over ForeverDB's data (corrections.py):
the stats its data lacks, the pieces its lists leave out, and it drops the
items the game does not have. Then it gives the items that have no source in
the data the one read in QuestieDB (corrections.fill), and checks the drops
that are not confirmed against the ones counted in Forever (corrections.confirm),
and writes what the vendors ask in a currency (corrections.price). It notes which dungeon each quest
is done in (runs.quest_places). Last, it completes the tanks' weights and adds the specs ForeverDB's data does not
have, the Feral Druid's cat next to its bear and the Paladin's Shockadin (specs.apply). So the build and the tests
rank the same database; load(..., corrected=False)
is ForeverDB's data as published.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import caster_gear
import caster_trinkets
import corrections
import raid_sources
import verified_sources
import relics
import aoe_eligibility
import aoe_jewelry
import aoe_ranged
import runs
import simulated
import situational_gear
import specs
import verified_gear

DATA_FILES = ("GearFinder.lua", "Gear.lua", "GearSources.lua", "Enhance.lua", "Meta.lua")
# What the Consumables tab reads. A build of the gear lists does without them: see Database.consumables.
CONSUMABLE_FILES = ("Consumables.lua", "Recipes.lua", "Items.lua", "Coach.lua")
HEADER_PREFIX = "-- Data: ForeverDB.net (https://foreverdb.net)"

_PAIR = re.compile(r'\[(\d+)\]="([^"]*)"')
_BLOCK = re.compile(r"^([A-Z]+)=\[==\[\n(.*?)\]==\]", re.S | re.M)
_TEXT = r'"((?:[^"\\]|\\.)*)"'
_NUMBER = r"(-?\d+(?:\.\d+)?)"
_CATALOGUE_ROW = re.compile(rf'\{{(\d+),{_TEXT},{_TEXT},{_TEXT},{_NUMBER},{_NUMBER},(\d+),(\d+),(\d+)\}}')
_RECIPE_ROW = re.compile(rf'\{{(\d+),{_TEXT},(\d+),(\d+),(\d+),(\d+),(\d+),{_NUMBER},{_TEXT},{_TEXT},(\d+),(\d+),(\d+)'
                         rf'(?:,{_NUMBER},{_NUMBER})?\}}')
_PROFESSION = re.compile(r'(?:\{|,)(?:\["([^"]+)"\]|([A-Z][A-Za-z]*))=\{\{')   # ["First Aid"]={{ or Alchemy={{
_FACTS = re.compile(rf'\[(\d+)\]={_TEXT}')
_COACH_PROFILE = re.compile(r'^ns\.coachData\.profiles\["([\w-]+)"\] = (.*)$', re.M)
_COACH_ENTRY = re.compile(rf'\{{kind="consumable",id=(\d+),name={_TEXT},value={_NUMBER}')


def b36(text: str) -> int:
    return int(text, 36)


def _stat_key(text: str):
    """Stat ids are numbers; "dps", "armor" and "wand" stay names."""
    return int(text) if text.isdigit() else text


def _unquote(text: str) -> str:
    """A Lua string's text: its \\" and \\\\ as the characters they stand for."""
    return re.sub(r"\\(.)", r"\1", text)


def _table_line(text: str, name: str) -> str:
    """The single line that holds `ns.<name> = {...}`."""
    prefix = f"ns.{name} = "
    for line in text.split("\n"):
        if line.startswith(prefix):
            if '\\"' in line:
                raise ValueError(f"ns.{name} holds an escaped quote, which this reader does not handle")
            return line
    raise ValueError(f"ns.{name} not found")


@dataclass
class Consumables:
    """ForeverDB's consumables data, as published. It says what exists and where it comes from; what an item
    does is read in the game (consumables.py), because this catalogue keeps one effect and one number per item."""
    catalogue: dict = field(default_factory=dict)  # item -> {"name", "kind", "family", "level", "strength",
    #                                                 "profession" (a name, or ""), "vendor", "leftover"}
    recipes: dict = field(default_factory=dict)    # item made -> [{"profession", "spell", "name", "skill", "count",
    #                                                 "reagents": {item: n}, "learned", "camp", "new"}]
    facts: dict = field(default_factory=dict)      # item -> {"made": [(profession, skill)], "vendors": [(count,
    #                                                 first vendor, zone)], "drops": [names], "quests": [names]}
    coach: dict = field(default_factory=dict)      # "warrior-fury" -> {"role", "class", "spec", "entries": [(item,
    #                                                 name, share of the damage lost without it)]}, at the level cap


class Database:
    """Everything the generator needs from ForeverDB's data files."""

    def __init__(self) -> None:
        self.header = ""        # the credit line every data file starts with
        self.meta = {}          # version, build, cap
        self.classes = {}       # token -> {"specs": {index: spec}, "pools": {pool: [(id, level)]}, "min": {profile: n}};
        #                         a class specs.apply added a spec to also has "order", the specs as the addon lists them;
        #                         a spec that is not ForeverDB's (specs.apply) also has "added"
        self.gear = {}          # id -> {"inv", "kind": "item class.subclass", "req": required level,
        #                                "stats": {stat: value}, "dps", "armor", "wand"}
        self.items = {}         # id -> {"name", "groups", "flags", "side", "twin", "limit", "sources"}; a piece
        #                         corrections.align added also has "added" and "phase", an item corrections.fill
        #                         gave a source "filled", and "phase" when it is one of ForeverDB's lists
        self.extra = {}         # id -> {"hit": n, "set": {stat: value}}
        self.dual_wield = {}    # token -> level from which the class dual wields (99: never)
        self.instances = {}     # id -> fields of ForeverDB's gfInst
        self.vendors = {}       # npc id -> [name, uiMap, x, y]
        self.enchants = {}      # token -> {(spec, profile): {slot key: [(enchant id, level)]}}
        self.enchant_info = {}  # enchant id ("s<spell>" or "i<item>") -> [name, effect, where, label]
        self.enchant_raids = {}  # enchant id -> the raid its source needs, for the ones corrections.fill placed
        self.corrected = None   # what corrections.apply changed (a corrections.Report), None for the published data
        self.included = None    # the pieces corrections.include added (their ids), None for the published data
        self.aligned = None     # what corrections.align changed (a corrections.Alignment), None for the published data
        self.filled = None      # what corrections.fill changed (a corrections.Filled), None for the published data
        self.confirmed = None   # what corrections.confirm changed (a corrections.Confirmed), None for the published data
        self.boss_wings = {}    # instance -> {boss, in lower-case words: wing key} (runs.boss_wings)
        self.quest_places = {}  # quest -> (instance, wing key or "") for the quests done in a dungeon (runs.quest_places)
        self.priced = None      # what corrections.price changed (a corrections.Priced), None for the published data
        self.simulated = None   # the PvE lists WoWSims Forever ranked (a simulated.Reading), None for the published data
        self.pre_raid_trinkets = {}  # additional faction and partner scores in the pre-raid phase
        self.specs = None       # what specs.apply changed in the specs (a specs.Report), None for the published data
        self.effects = {}       # item -> the roles whose weights cannot value it (corrections/effects.json)
        self.data_dir = None    # the folder this was read from
        self._consumables = None

    @property
    def consumables(self):
        """ForeverDB's consumables data, read the first time it is asked for; None without its files."""
        if self._consumables is None and self.data_dir is not None:
            self._consumables = read_consumables(self.data_dir)
        return self._consumables


def load(data_dir, corrected: bool = True) -> Database:
    db = _read(data_dir)
    if corrected:
        caster_gear.include_items(db)
        corrections.apply(db, corrections.load())
        corrections.include(db)
        corrections.align(db, corrections.load_game())
        corrections.complete_shields(db)
        corrections.complete_weapon_hits(db)
        corrections.fill(db, corrections.load_sources())
        corrections.confirm(db, corrections.load_drops())
        corrections.price(db, corrections.load_costs())
        db.verified_sources = verified_sources.apply(db)
        corrections.assign_sides(db)
        corrections.pair_faction_items(db)
        corrections.assign_reward_sides(db)
        raid_sources.apply(db)
        verified_gear.apply(db)
        db.quest_places = runs.quest_places(db, runs.load_quests())
        db.specs = specs.apply(db)
        caster_gear.include(db)
        relics.apply(db)
        situational_gear.include(db)
        aoe_ranged.include_relics(db)
        aoe_jewelry.include_trinkets(db)
        aoe_eligibility.include_darkmantle(db)
        db.simulated = simulated.load() if simulated.IN_USE else simulated.Reading()
        if simulated.IN_USE:
            db.pre_raid_trinkets = caster_trinkets.tables()
    return db


def load_for_capture(data_dir):
    """Start with the published catalogue and also request the caster items verified in Forever."""
    db = load(data_dir, corrected=False)
    caster_gear.include_items(db)
    caster_gear.include(db)
    return db


def _read(data_dir) -> Database:
    data_dir = Path(data_dir)
    texts = {name: (data_dir / name).read_text(encoding="utf-8") for name in DATA_FILES}
    for name, text in texts.items():
        if not text.startswith(HEADER_PREFIX):
            raise ValueError(f"{name} does not start with ForeverDB's credit line")

    db = Database()
    db.data_dir = data_dir
    db.header = texts["GearFinder.lua"].split("\n", 1)[0]
    meta = texts["Meta.lua"]
    db.meta = {
        "version": re.search(r'version="([^"]+)"', meta).group(1),
        "build": re.search(r'build="([^"]+)"', meta).group(1),
        "cap": int(re.search(r"cap=(\d+)", meta).group(1)),
    }
    _read_finder(db, texts["GearFinder.lua"])
    _read_gear(db, texts["Gear.lua"])
    _read_sources(db, texts["GearSources.lua"])
    _read_enchants(db, texts["Enhance.lua"])
    return db


def _read_finder(db: Database, text: str) -> None:
    for token, body in _BLOCK.findall(text):
        cls = {"specs": {}, "pools": {}, "min": {}}
        for line in body.split("\n"):
            fields = line.split("\t")
            kind = fields[0]
            if kind == "S":
                cls["specs"][int(fields[1])] = {
                    "name": fields[2], "role": fields[3], "style": fields[4], "slug": fields[5], "weights": {}}
            elif kind == "W":
                weights = {_stat_key(k): float(v) for k, v in re.findall(r"(\w+)=([-\d.]+)", fields[3])}
                cls["specs"][int(fields[1])]["weights"][fields[2]] = weights
            elif kind == "M":
                cls["min"][fields[1]] = float(fields[2])
            elif kind == "P":
                cls["pools"][fields[1]] = [(b36(i), b36(lv)) for i, lv in re.findall(r"(\w+):(\w+)", fields[2])]
        db.classes[token] = cls


def _read_gear(db: Database, text: str) -> None:
    for item_id, raw in _PAIR.findall(_table_line(text, "gear")):
        inv, class_id, sub_id, required, stats, dps, armor = raw.split(";")
        record = {
            "inv": int(inv),
            "kind": f"{class_id}.{sub_id}",
            "req": int(required) if required else 0,
            "stats": {},
            "dps": (float(dps) if dps else 0.0) / 10,
            "armor": float(armor) if armor else 0.0,
            "wand": class_id == "2" and sub_id == "19",
        }
        for stat, value in re.findall(r"(\d+):(-?\d+)", stats):
            record["stats"][int(stat)] = record["stats"].get(int(stat), 0) + int(value)
        db.gear[int(item_id)] = record

    for token, level in re.findall(r"([A-Z]+)=\{armor=.*?dw=(\w+)\}", _table_line(text, "prof")):
        db.dual_wield[token] = int(level) if level.isdigit() else 99


def _read_sources(db: Database, text: str) -> None:
    item_text = re.search(r"ns\.gfItemText = \[==\[\n(.*?)\]==\]", text, re.S).group(1)
    for line in item_text.split("\n"):
        if "|" not in line:
            continue
        f = line.split("|")
        f += [""] * (8 - len(f))
        db.items[b36(f[0])] = {
            "name": f[1],
            "groups": frozenset(f[2]),
            "flags": f[3],
            "side": f[4],
            "twin": int(f[5]) if f[5] else None,
            "limit": next((token[1:] for token in f[6].split() if token.startswith("L")), None),
            "sources": [source.split("^") for source in f[7].split("~") if source],
        }

    for item_id, raw in _PAIR.findall(_table_line(text, "gfExtra")):
        extra = {}
        for token in raw.split():
            if token[0] == "h":
                extra["hit"] = float(token[1:])
            elif token[0] == "s":
                extra["set"] = {_stat_key(k): float(v) for k, v in re.findall(r"(\w+):([\d.]+)", token[1:])}
        db.extra[int(item_id)] = extra

    for inst_id, raw in _PAIR.findall(_table_line(text, "gfInst")):
        db.instances[int(inst_id)] = raw.split("^")
    for npc_id, raw in _PAIR.findall(_table_line(text, "gfVendor")):
        db.vendors[int(npc_id)] = raw.split("^")


def _read_enchants(db: Database, text: str) -> None:
    lists, info = text.split("ns.gfEnhInfo", 1)
    for token, body in _BLOCK.findall(lists):
        per_spec = {}
        for line in body.split("\n"):
            fields = line.split("\t")
            if fields[0] != "E":
                continue
            per_slot = {}
            for key, entries in re.findall(r"(\w+)=([^;]+)", fields[3]):
                per_slot[key] = [(enchant, b36(level)) for enchant, level in re.findall(r"(\w+)\.(\w+)", entries)]
            per_spec[(int(fields[1]), fields[2])] = per_slot
        db.enchants[token] = per_spec
    for enchant, raw in re.findall(r'\["([si]\d+)"\]="([^"]*)"', info):
        db.enchant_info[enchant] = raw.split("|")


# -- the consumables --------------------------------------------------------------------------------------

def read_consumables(data_dir) -> Consumables | None:
    """The four files of the Consumables tab, parsed as text; None while one of them is not there yet."""
    data_dir = Path(data_dir)
    if not all((data_dir / name).exists() for name in CONSUMABLE_FILES):
        return None
    texts = {name: (data_dir / name).read_text(encoding="utf-8") for name in CONSUMABLE_FILES}
    for name, text in texts.items():
        if not text.startswith(HEADER_PREFIX):
            raise ValueError(f"{name} does not start with ForeverDB's credit line")
    professions = re.findall(_TEXT, re.search(r"^ns\.professions = (.*)$", texts["Items.lua"], re.M).group(1))
    return Consumables(catalogue=_read_catalogue(texts["Consumables.lua"], professions),
                       recipes=_read_recipes(texts["Recipes.lua"]),
                       facts=_read_facts(texts["Items.lua"], professions),
                       coach=_read_coach(texts["Coach.lua"]))


def _whole_line(text: str, name: str) -> str:
    """The line of `ns.<name> = ...`; unlike _table_line, it may hold escaped quotes."""
    found = re.search(rf"^ns\.{name} = (.*)$", text, re.M)
    if not found:
        raise ValueError(f"ns.{name} not found")
    return found.group(1)


def _read_catalogue(text: str, professions: list) -> dict:
    line = _whole_line(text, "consumables")
    rows = _CATALOGUE_ROW.findall(line)
    if len(rows) != line.count("},{") + 1:
        raise ValueError("Consumables.lua: a row of ns.consumables has a form this reader does not know")
    catalogue = {}
    for item, name, kind, family, level, strength, made, vendor, leftover in rows:
        catalogue[int(item)] = {
            "name": _unquote(name), "kind": kind, "family": _unquote(family), "level": int(float(level)),
            "strength": float(strength), "profession": professions[int(made) - 1] if int(made) else "",
            "vendor": vendor == "1", "leftover": leftover == "1"}
    return catalogue


def _read_recipes(text: str) -> dict:
    line = _whole_line(text, "recipes")
    marks = list(_PROFESSION.finditer(line))
    recipes, seen = {}, 0
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(line)
        for row in _RECIPE_ROW.findall(line[mark.end() - 2:end]):
            seen += 1
            recipes.setdefault(int(row[6]), []).append({
                "profession": mark.group(1) or mark.group(2), "spell": int(row[0]), "name": _unquote(row[1]), "skill": int(row[2]),
                "count": float(row[7]), "reagents": {int(item): int(count) for item, count in
                                                     re.findall(r"(\d+):(\d+)", row[8])},
                "learned": row[9], "camp": int(row[10]), "new": row[11] == "1"})
    if seen != line.count("},{") + len(marks):
        raise ValueError("Recipes.lua: a row of ns.recipes has a form this reader does not know")
    return recipes


def _read_facts(text: str, professions: list) -> dict:
    facts = {}
    for item, raw in _FACTS.findall(_whole_line(text, "items")):
        record = {"made": [], "vendors": [], "drops": [], "quests": []}
        for fact in _unquote(raw).split("|"):
            kind, fields = fact[:1], fact[1:].split("~")
            if kind == "m" and len(fields) >= 2 and fields[0].isdigit():
                record["made"].append((professions[int(fields[0])], int(fields[1])))
            elif kind == "v" and len(fields) >= 3:
                record["vendors"].append((int(fields[0]) if fields[0].isdigit() else 0, fields[1], fields[2]))
            elif kind == "d":
                record["drops"].append(fields[0])
            elif kind == "q":
                record["quests"].append(fields[0])
        facts[int(item)] = record
    return facts


def _read_coach(text: str) -> dict:
    """What ForeverDB's simulator asks each spec to have up before the pull, in the bracket of the level cap."""
    coach = {}
    for slug, body in _COACH_PROFILE.findall(text):
        start = body.find("levels={60,60}")
        if start < 0:
            continue
        end = body.find("levels={", start + 1)
        bracket = body[start:end if end > 0 else len(body)]
        field_of = lambda name: (re.search(rf'{name}="([^"]*)"', body) or [None, ""])[1]
        coach[slug] = {"role": field_of("role"), "class": field_of("class"), "spec": field_of("specName"),
                       "entries": [(int(item), _unquote(name), float(value))
                                   for item, name, value in _COACH_ENTRY.findall(bracket)]}
    return coach
