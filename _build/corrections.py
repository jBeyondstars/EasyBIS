"""Stats read in the game, laid over ForeverDB's where its data has a hole.

ForeverDB's Gear.lua (data 2026-11-14) holds no healing or spell damage for
most caster weapons, and gives them the damage per second of a melee weapon:
1.34 to 1.5 times what the game shows. So a level 28 scepter that kept its
healing came out as the best healer main hand at level 60. The weapons'
tooltips are read in the game by the developer's capture tool
(_build/capture_addon, installed by `build.py --capture-tool`) and kept in
corrections/weapons.json by `build.py --import-capture` (capture.py).

A correction fills a hole, so it retires by itself once ForeverDB's data has
the value:
  - healing and spell damage are added to a weapon that has none in the data;
  - the damage per second is replaced when the data's is at least DPS_TOO_HIGH
    times the one read in the game, on a weapon the game shows spell power for.
Where the data has a value and the game showed another, the game's replaces
it when it was read at the data's game build or a later one: the game is the
reference for its own build. That goes for the healing and spell damage, and
for the damage per second of any weapon (the staves that carry the damage of
one school only are too high in the data as well). Read at an older build,
the capture may be out of date: the data's values are kept and the difference
is reported, which means the weapons are to be read again (/ebiscapture).

The same capture says which items the game has (corrections/game.json, align):
  - ForeverDB's data holds items the game does not show, mostly numbers left
    from another version of the game. The capture asked for each of them four
    times and got nothing: they are dropped from the lists. A few may be
    pieces of an event or a phase to come, which the server keeps to itself
    until then: the game is to be read again when one opens (/ebiscapture all).
  - ForeverDB's lists leave out pieces it has stats for and the game does have
    (raid sets and raid drops mostly). They are added to the pools of the
    classes that already hold that kind of piece, as items with no known
    source, counted only once every phase is: nothing says where they are from.
A piece ForeverDB comes to list is no longer added: that part retires by itself.

The capture reads the game from level 50 up, so a lower piece players still wear at the cap is in neither
list. The few known ones are written by hand (HAND_LISTED, include), each with what says players have it.

Where an item comes from is laid over the data the same way (corrections/sources.json, fill):
ForeverDB's data gives no source for many items, the pieces added above among them, and QuestieDB
knows the quest, the creature or the vendor of a good part of them. `build.py --import-questie`
reads it (questie.py). An item of ForeverDB's lists that gets a source this way is no longer one
"with no known source", and counts from the content phase its source needs. A piece added above gets
the source to show and nothing else: it stays flagged and of the last phase (see fill). The source
carries the label t, which the addon marks like Classic data: read in another database, not confirmed
in Forever. A source ForeverDB comes to give is used instead: that part retires by itself too.

A drop that is not confirmed is checked against the loot counts of Wowhead Forever two other addons hold
(corrections/drops.json, confirm): `build.py --import-drops` reads them (drops.py). The boss they name
and the rate they count replace Classic's, with the label w, which the addon shows like a source seen in
Forever. A source ForeverDB saw itself stays as it is. The counts are kept dungeon by dungeon, so they also
say where a creature is: one the data names with no place becomes a boss of the dungeon it was counted in,
the dungeons of Forever the data has no instance for among them (runs.py). And an item the data gives no
source at all takes the bosses it was counted on: it is no longer an item "with no known source".

What a vendor asks in a currency is laid over the data as well (corrections/costs.json, price): the data
says 0 for it. The same file names the vendors who sell to both factions, whose items the data keeps for
one. Neither changes a score: the lists rank on stats, and the price is there to be read.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import phases
import runs

FILE = Path(__file__).resolve().parent / "corrections" / "weapons.json"
GAME_FILE = FILE.with_name("game.json")
SOURCES_FILE = FILE.with_name("sources.json")
DROPS_FILE = FILE.with_name("drops.json")
COSTS_FILE = FILE.with_name("costs.json")
SHIELDS_FILE = FILE.with_name("shields.json")
ARMS_WEAPONS_FILE = FILE.with_name("arms_weapons.json")
ABOUT = ("Weapon stats read in the game with the EasyBIS_Capture tool (_build/capture_addon), laid over "
         "ForeverDB's data by _build/corrections.py. Written by `python build.py --import-capture`: do not edit.")

HEALING, SPELL_DAMAGE, SPELL_POWER = 41, 42, 45  # ForeverDB's stat ids; spell power is healing and damage alike
POWER = (HEALING, SPELL_DAMAGE, SPELL_POWER)
WEAPONS = frozenset((13, 17, 21, 22))  # inventory types: one-hand, two-hand, main hand, off hand
DPS_TOO_HIGH = 1.25
DPS_TOLERANCE = 0.06  # the data keeps one decimal


ALLIANCE_FACTIONS = frozenset({"2799"})   # Theramore Expeditionary Force


def complete_weapon_hits(db) -> None:
    """The level-60 Arms PvP model needs the tooltip's base damage per swing."""
    for item, values in json.loads(ARMS_WEAPONS_FILE.read_text(encoding="utf-8"))["items"].items():
        gear = db.gear.get(int(item))
        low, high, speed = values
        if gear and gear["inv"] == 17 and abs((low + high) / (2 * speed) - gear["dps"]) <= DPS_TOLERANCE:
            gear["weapon_hit"] = tuple(values)


def complete_shields(db) -> None:
    """Add the shield's intrinsic block to stat 48 when ForeverDB only counts its equip bonus.
    The recorded bonus guards both an already complete value and a later change in the upstream data."""
    values = json.loads(SHIELDS_FILE.read_text(encoding="utf-8"))["items"]
    for item, (base, bonus) in values.items():
        gear = db.gear.get(int(item))
        if gear and gear["inv"] == 14 and gear["stats"].get(48, 0) == bonus:
            gear["stats"][48] = base + bonus


def assign_sides(db) -> list[int]:
    """ForeverDB's data leaves the pieces of Theramore Expeditionary Force to both sides, and marks their vendor
    as a Horde one, while the vendor is friendly to the Alliance alone and every quest of the faction is an
    Alliance quest (QuestieDB). A Horde character could never buy them: they are the Alliance's. Returns the
    items changed; once the data gives them a side, there are none."""
    changed = []
    for item_id, item in db.items.items():
        if not item["side"] and any(source[0] == "r" and source[1] in ALLIANCE_FACTIONS for source in item["sources"]):
            item["side"] = "a"
            changed.append(item_id)
    return changed


# (Alliance, Horde). Each pair occupies the same slot and has the same stats.
FACTION_PAIRS = (
    (20056, 20203),  # Arathi Basin mail pauldrons
    (271954, 272104), (271956, 272106),  # Theramore / Darkspear leather and mail shoulders
    # Rare Premier priest armor, Voidcloth / Satin (Lieutenant Commander's / Champion's Raiment).
    (272814, 272562), (272817, 272565), (272816, 272564), (272812, 272569),
    (272815, 272563), (272810, 272568), (272811, 272567), (272813, 272566),
    # Mooncloth / Silken (Lieutenant Commander's / Champion's Investiture), same slot order.
    (272677, 272649), (272678, 272650), (273448, 272634), (273445, 272619),
    (273447, 272663), (273443, 272611), (273444, 273450), (273449, 275437),
)


def pair_faction_items(db) -> None:
    """Fill missing faction links when both records agree with the known pair."""
    for alliance_id, horde_id in FACTION_PAIRS:
        alliance, horde = db.items.get(alliance_id), db.items.get(horde_id)
        if (alliance and horde and alliance["side"] in ("", "a") and horde["side"] in ("", "h")
                and alliance["twin"] in (None, horde_id) and horde["twin"] in (None, alliance_id)):
            alliance.update(side="a", twin=horde_id)
            horde.update(side="h", twin=alliance_id)


# Each item binds on pickup. The quests carry a faction in WoWSims' Forever database.
# The three honor quartermasters sell their listed IDs inside their own faction's hall.
# Source references and the date checked are in docs/audit-forever/factions.md.
FACTION_REWARDS = (
    ("h", "v", 12793, (272578, 272589)),
    ("a", "v", 12781, (272698, 272699)),
    ("a", "v", 12777, (272716, 272717, 272738, 272739, 272740, 272741, 272828, 273325)),
    ("a", "q", 92458, (279839,)),
    ("a", "q", 94927, (275025,)),
    ("a", "q", 94984, (279854,)),
    ("a", "q", 95064, (274959,)),
    ("a", "q", 95925, (279912,)),
    ("a", "q", 96609, (276903, 276904)),
)


def assign_reward_sides(db) -> None:
    """Use the verified faction while the bound item still has only the documented source."""
    for side, kind, source_id, rewards in FACTION_REWARDS:
        for item_id in rewards:
            item = db.items.get(item_id)
            if not item or item["side"] or item["twin"]:
                continue
            sources = {(src[0].lower(), src[1]) for src in item["sources"]}
            if sources == {(kind, str(source_id))}:
                item["side"] = side


@dataclass
class Report:
    """What apply() did with the observations."""
    observed: int = 0                             # weapons read in the game
    filled: list = field(default_factory=list)    # ids given the healing and spell damage the data lacks
    dps: list = field(default_factory=list)       # ids given the damage per second the game shows
    agree: int = 0                                # the data already has what the game shows
    replaced: list = field(default_factory=list)  # ids whose healing and spell damage the game showed otherwise
    differ: list = field(default_factory=list)    # (id, (healing, damage) in the game, the same in the data): kept
    unknown: list = field(default_factory=list)   # ids the data has no weapon for
    builds: set = field(default_factory=set)      # the game builds the corrections in use were read at

    @property
    def changed(self) -> set:
        return set(self.filled) | set(self.replaced) | set(self.dps)


def load(path=FILE) -> dict[int, dict]:
    """{item id: {"name", "healing", "damage", "dps", "build", "date"}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(item_id): record for item_id, record in data["items"].items()}


def save(observations: dict[int, dict], path=FILE) -> None:
    """One weapon per line, in id order, so a new capture reads as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [f'    "{item_id}": {json.dumps(observations[item_id], ensure_ascii=False, sort_keys=True)}'
            for item_id in sorted(observations)]
    text = "{\n  " + f'"about": {json.dumps(ABOUT)},\n  "items": {{\n' + ",\n".join(rows) + "\n  }\n}\n"
    path.write_bytes(text.encode("utf-8"))


def power_stats(healing: float, damage: float) -> dict[int, int]:
    """Healing and spell damage as ForeverDB writes them: one spell power stat when they are equal."""
    if healing == damage:
        return {SPELL_POWER: int(healing)} if healing else {}
    return {stat: int(value) for stat, value in ((HEALING, healing), (SPELL_DAMAGE, damage)) if value}


def _build_number(build: str) -> tuple:
    """"1.60.1.70938" as numbers, to tell which of two game builds is the later one."""
    return tuple(int(part) for part in build.split(".") if part.isdigit())


def apply(db, observations: dict[int, dict]) -> Report:
    """Fill the holes of db.gear from the observations; the report is kept as db.corrected."""
    report = Report(observed=len(observations))
    data_build = _build_number(db.meta.get("build", ""))
    for item_id in sorted(observations):
        seen = observations[item_id]
        gear = db.gear.get(item_id)
        if gear is None or gear["inv"] not in WEAPONS:
            report.unknown.append(item_id)
            continue
        healing, damage, dps = seen.get("healing", 0), seen.get("damage", 0), seen.get("dps", 0)
        current = bool(seen.get("build")) and _build_number(seen["build"]) >= data_build
        stats = gear["stats"]
        if not (healing or damage):
            pass  # the game shows no spell power either: nothing to add
        elif not any(stats.get(stat) for stat in POWER):
            stats.update(power_stats(healing, damage))
            report.filled.append(item_id)
            report.builds.add(seen.get("build", ""))
        else:
            has = (stats.get(HEALING, 0) + stats.get(SPELL_POWER, 0), stats.get(SPELL_DAMAGE, 0) + stats.get(SPELL_POWER, 0))
            if abs(has[0] - healing) <= 1 and abs(has[1] - damage) <= 1:
                report.agree += 1
            elif current:
                for stat in POWER:
                    stats.pop(stat, None)
                stats.update(power_stats(healing, damage))
                report.replaced.append(item_id)
                report.builds.add(seen["build"])
            else:
                report.differ.append((item_id, (healing, damage), has))
        if not dps:
            continue
        if abs(gear["dps"] - dps) > DPS_TOLERANCE if current else (healing or damage) and gear["dps"] >= dps * DPS_TOO_HIGH:
            gear["dps"] = float(dps)
            report.dps.append(item_id)
            report.builds.add(seen.get("build", ""))
    report.builds.discard("")
    db.corrected = report
    return report


# -- the items the game has -----------------------------------------------------------------------------

GAME_ABOUT = ("What the game showed of the items of ForeverDB's data, read with the EasyBIS_Capture tool "
              "(_build/capture_addon): the ids it does not have, and the pieces it has that ForeverDB's lists leave "
              "out. Laid over the data by _build/corrections.py. Written by `python build.py --import-capture`: "
              "do not edit.")
# Chest and robe go to the same pool, and so do the three kinds of ranged weapon.
_FAMILY = {5: "chest", 20: "chest", 15: "ranged", 25: "ranged", 26: "ranged"}

# Pieces the game shows that no player gets: they are not added. Written by hand, and only what is
# certain; `build.py --audit` names the added pieces that come out far ahead of everything else.
NOT_FOR_PLAYERS = {
    17142: "Shard of the Defiler: a dagger with 15% critical strike and 15% haste, never given out",
}
# ... and the ones the game itself names as withdrawn ("Mandokir's Sting DEPRECATED").
_WITHDRAWN = re.compile(r"\b(DEPRECATED|DEP|OLD|UNUSED|TEST)\b|^Monster - ")


@dataclass
class Alignment:
    """What align() did with the reading of the game."""
    build: str = ""                               # the game build it was read at
    absent: int = 0                               # ids of the data the game does not have
    dropped: list = field(default_factory=list)   # of which ForeverDB's pools held: left out of the lists
    added: list = field(default_factory=list)     # pieces the game has, added to the pools with no known source
    listed: list = field(default_factory=list)    # pieces of the reading ForeverDB lists by now: left to its data
    withheld: list = field(default_factory=list)  # pieces no player gets (NOT_FOR_PLAYERS, withdrawn): not added
    stale: bool = False                           # the data is of a later game build than the reading

    @property
    def changed(self) -> bool:
        return bool(self.dropped or self.added)


def load_game(path=GAME_FILE) -> dict:
    """{"build", "date", "listed", "read", "absent": [ids], "unlisted": {id: {"name", "classes", "unique",
    "limit"}}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["unlisted"] = {int(item_id): record for item_id, record in data.get("unlisted", {}).items()}
    return data


def save_game(game: dict, path=GAME_FILE) -> None:
    """One piece per line, in id order, so another capture reads as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    absent = sorted(game["absent"])
    rows = [", ".join(map(str, absent[start:start + 16])) for start in range(0, len(absent), 16)]
    pieces = [f'    "{item_id}": {json.dumps(game["unlisted"][item_id], ensure_ascii=False, sort_keys=True)}'
              for item_id in sorted(game["unlisted"])]
    head = {name: game[name] for name in ("build", "date", "listed", "read")}
    text = ("{\n" + f'  "about": {json.dumps(GAME_ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(value)},\n' for name, value in head.items())
            + '  "absent": [\n' + ",\n".join("    " + row for row in rows) + "\n  ],\n"
            + '  "unlisted": {\n' + ",\n".join(pieces) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def _kind(gear: dict) -> tuple:
    """What tells whether a pool takes a piece: where it is worn, and the game's kind of item."""
    return _FAMILY.get(gear["inv"], gear["inv"]), gear.get("kind")


def align(db, game: dict) -> Alignment:
    """Drop the items the game does not have, add the pieces it has that the lists leave out; the report is
    kept as db.aligned.

    A piece goes to every pool that already holds its kind of piece (a plate chest to the chest pool of
    the classes that have plate chests in theirs), but for the classes its tooltip leaves out. An item
    the game does not have leaves the pools, and stays in db.items: the search by name (Names.lua) is
    still ForeverDB's list of names. An added piece is marked "added", and comes with its phase: the last
    one, until something says where it is from (fill).
    """
    report = Alignment(build=game.get("build", ""))
    db.aligned = report
    if not game:
        return report
    report.stale = _build_number(db.meta.get("build", "")) > _build_number(report.build)
    absent = set(game.get("absent", ()))
    report.absent = len(absent)
    holds = {(cls, pool): {_kind(db.gear[item_id]) for item_id, _ in entries if item_id in db.gear}
             for cls, data in db.classes.items() for pool, entries in data["pools"].items()}

    dropped = set()
    for data in db.classes.values():
        for pool, entries in data["pools"].items():
            dropped.update(item_id for item_id, _ in entries if item_id in absent)
            data["pools"][pool] = [entry for entry in entries if entry[0] not in absent]
    for item in db.items.values():
        if item["twin"] in absent:
            item["twin"] = None   # the other faction has no such piece
    report.dropped = sorted(dropped)

    for item_id in sorted(game.get("unlisted", {})):
        seen, gear = game["unlisted"][item_id], db.gear.get(item_id)
        if gear is None:
            continue   # the data no longer has it
        if item_id in db.items:
            report.listed.append(item_id)
            continue
        if item_id in NOT_FOR_PLAYERS or _WITHDRAWN.search(seen["name"]):
            report.withheld.append(item_id)
            continue
        allowed = {word.upper() for word in seen.get("classes", ())}
        kind, placed = _kind(gear), False
        for (cls, pool), kinds in holds.items():
            if kind in kinds and (not allowed or cls in allowed):
                db.classes[cls]["pools"][pool].append((item_id, gear["req"]))
                placed = True
        if placed:
            db.items[item_id] = {
                "name": seen["name"], "groups": frozenset("u"), "flags": "U" if seen.get("unique") else "",
                "side": "", "twin": None, "limit": seen.get("limit"), "sources": [], "phase": phases.LATER,
                "added": True}
            report.added.append(item_id)
    return report


# Pieces players wear that ForeverDB's lists leave out and the capture never asks the game for (it reads from level
# 50 up). Written by hand, each with what says players have it, and where it is from as ForeverDB writes a source;
# include gives that source the label of one read outside Forever.
#   871  Flurry Axe, required level 42: the off hand of WoWSims Forever's Fury and Combat sets, whose proc rate was
#        measured on wearers in Forever's logs (wowsims/forever, docs/evidence/EV-0120). A world drop in Classic.
HAND_LISTED = {
    871: ("Flurry Axe", (("w", "0", "0"),)),
}


def include(db) -> list:
    """Add the pieces written by hand (HAND_LISTED) as ForeverDB lists an item, to every pool that already holds
    their kind of piece; kept as db.included. One the data comes to list is left as the data has it: this retires
    by itself. It runs before align, which then finds them listed."""
    holds = {(cls, pool): {_kind(db.gear[item_id]) for item_id, _ in entries if item_id in db.gear}
             for cls, data in db.classes.items() for pool, entries in data["pools"].items()}
    db.included = []
    for item_id, (name, sources) in sorted(HAND_LISTED.items()):
        gear = db.gear.get(item_id)
        if gear is None or item_id in db.items:
            continue
        placed = False
        for (cls, pool), kinds in holds.items():
            if _kind(gear) in kinds:
                db.classes[cls]["pools"][pool].append((item_id, gear["req"]))
                placed = True
        if placed:
            db.items[item_id] = {"name": name, "groups": frozenset(source[0] for source in sources), "flags": "",
                                 "side": "", "twin": None, "limit": None,
                                 "sources": [[*source, SOURCE_LABEL] for source in sources]}
            db.included.append(item_id)
    return db.included


# -- where the items come from ----------------------------------------------------------------------------

SOURCES_ABOUT = ("Where the items ForeverDB's data gives no source come from, read in QuestieDB "
                 "(https://github.com/Questie/QuestieDB, GPL-3.0) by _build/questie.py and laid over the data by "
                 "_build/corrections.py. Sources are written as ForeverDB writes them, with the label t; \"at\" is "
                 "the instance a quest or a creature belongs to, or \"boss\" for a raid boss QuestieDB does not "
                 "place. Written by `python build.py --import-questie`: do not edit.")
SOURCE_LABEL = "t"
BOSS = "boss"   # questie.BOSS: a boss of some raid
UNKNOWN_WHERE = "where it comes from isn't known yet"   # ForeverDB's sentence for an enchant with no source
# Source kind -> the source group it stands for; a quest or a chest of an instance is told apart in _group.
_GROUP = {"q": "q", "d": "d", "v": "v", "V": "v", "m": "w", "R": "R", "o": "x", "x": "x"}


@dataclass
class Filled:
    """What fill() did with the sources read in QuestieDB."""
    version: str = ""                              # the QuestieDB they were read in
    date: str = ""
    known: int = 0                                 # items the file holds a source for
    items: list = field(default_factory=list)      # ids given a source
    added: list = field(default_factory=list)      # of which pieces added from the game (align)
    listed: list = field(default_factory=list)     # ids ForeverDB gives a source by now: left to its data
    enchants: list = field(default_factory=list)   # enchants given a source sentence
    instances: list = field(default_factory=list)  # Classic instances named for those sources

    @property
    def changed(self) -> bool:
        return bool(self.items or self.enchants)


def load_sources(path=SOURCES_FILE) -> dict:
    """{"questiedb", "commit", "date", "asked", "instances": {id: name}, "items": {id: {"name", "sources", "at"}},
    "enchants": {enchant: {"where", "at"}}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["items"] = {int(item_id): record for item_id, record in data.get("items", {}).items()}
    data["instances"] = {int(number): name for number, name in data.get("instances", {}).items()}
    return data


def save_sources(reading: dict, path=SOURCES_FILE) -> None:
    """One item per line, in id order, so another reading of QuestieDB shows as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def rows(records: dict, key) -> str:
        return ",\n".join(f'    "{name}": {json.dumps(records[name], ensure_ascii=False, sort_keys=True)}'
                          for name in sorted(records, key=key))

    head = {name: reading.get(name, "") for name in ("questiedb", "commit", "date", "asked")}
    instances = {str(number): name for number, name in sorted(reading.get("instances", {}).items())}
    text = ("{\n" + f'  "about": {json.dumps(SOURCES_ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(value)},\n' for name, value in head.items())
            + f'  "instances": {json.dumps(instances, ensure_ascii=False)},\n'
            + '  "enchants": {\n' + rows(reading.get("enchants", {}), lambda enchant: int(enchant[1:])) + "\n  },\n"
            + '  "items": {\n' + rows(reading.get("items", {}), int) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def _raid(db, source: list, where, name: str):
    """The raid a source of the file needs, or None: the instance it is said to be in, else what phases.py
    knows of the source itself."""
    if where == BOSS:
        return BOSS   # no raid of that name: phases.raid_phase takes it for a Classic one
    if isinstance(where, int) and (db.instances.get(where) or ["", ""])[1] == "raid":
        return phases.RAID_INSTANCES.get(where, phases.NEW_RAID)
    return phases.source_raid(source, name)


def _group(db, source: list, where, raid) -> str:
    kind = source[0]
    if kind == "d":
        return "r" if raid else "d"
    if kind == "q" and isinstance(where, int):
        return "Q"   # the quest of a dungeon or a raid
    if kind == "o" and isinstance(where, int):
        return "r" if raid else "d"
    return _GROUP.get(kind, "w")


def fill(db, reading: dict) -> Filled:
    """Give the items and the enchants ForeverDB's data has no source for the one read in QuestieDB; the
    report is kept as db.filled.

    An item takes the sources, the source groups they stand for (in place of "u") and the phase of the
    earliest one: a quest of Ahn'Qiraj needs that raid, whether or not phases.py lists the quest. The
    sources that need no raid go first, as phases.shown_sources orders ForeverDB's. The Classic instances
    the sources name join db.instances, so the data files can say them.

    A piece added from the game (align) gets the sources to show, and keeps its group "u" and the last
    phase: it shows where it did, with the items of no known source. ForeverDB's lists leave it out,
    and QuestieDB's drop tables for such a piece are Classic's: a dungeon set Forever may have
    replaced, a vendor whose price nothing gives. And align pools it by its kind of armor, for every
    class when the game's tooltip names none: a list shown by default would offer a rogue's helmet to
    a warrior. The source says where to look; it does not make the piece a pick.
    """
    report = Filled(version=reading.get("questiedb", ""), date=reading.get("date", ""),
                    known=len(reading.get("items", {})))
    db.filled = report
    for number, name in sorted(reading.get("instances", {}).items()):
        if number not in db.instances:
            kind = "raid" if number in phases.RAID_INSTANCES else "dungeon"
            db.instances[number] = [name, kind, "", "", "", "", SOURCE_LABEL]
            report.instances.append(number)

    for item_id in sorted(reading.get("items", {})):
        record, item = reading["items"][item_id], db.items.get(item_id)
        if item is None:
            continue   # not in the data, and not a piece the lists took from the game
        if item["sources"] or "u" not in item["groups"]:
            report.listed.append(item_id)
            continue
        places = record.get("at") or [None] * len(record["sources"])
        found = []
        for source, where in zip(record["sources"], places):
            raid = _raid(db, source, where, item["name"])
            found.append((phases.raid_phase(raid) if raid else phases.PRE_RAID, _group(db, source, where, raid),
                          list(source)))
        found.sort(key=lambda entry: entry[0])
        item["sources"] = [source for _, _, source in found]
        item["filled"] = True
        report.items.append(item_id)
        if item.get("added"):
            report.added.append(item_id)
        else:
            item["groups"] = frozenset(group for _, group, _ in found)
            item["phase"] = found[0][0]

    for enchant in sorted(reading.get("enchants", {})):
        record, info = reading["enchants"][enchant], db.enchant_info.get(enchant)
        if info is None:
            continue
        info += [""] * (4 - len(info))
        if info[2] not in ("", UNKNOWN_WHERE):
            continue   # ForeverDB says where it is from by now
        info[2], info[3] = record["where"], SOURCE_LABEL
        where = record.get("at")
        if where == BOSS:
            db.enchant_raids[enchant] = BOSS
        elif isinstance(where, int) and (db.instances.get(where) or ["", ""])[1] == "raid":
            db.enchant_raids[enchant] = phases.RAID_INSTANCES.get(where, phases.NEW_RAID)
        report.enchants.append(enchant)
    return report


# -- what the vendors ask in a currency --------------------------------------------------------------------

# Where a vendor's source holds its price and the faction it sells to: V is ForeverDB's short form, v the full one.
_PRICE_FIELD = {"V": 2, "v": 6}
_SIDE_FIELD = {"V": 3, "v": 7}


@dataclass
class Priced:
    """What price() did with the vendors of corrections/costs.json."""
    date: str = ""                                   # when the prices were written down
    currencies: dict = field(default_factory=dict)   # the currency's item id -> {"name", "currency"}
    items: list = field(default_factory=list)        # ids given a price
    read: list = field(default_factory=list)         # of those, the ones whose price was read at the vendor
    freed: list = field(default_factory=list)        # ids the data kept for one faction, sold to both
    absent: list = field(default_factory=list)       # ids of the file the data does not say that vendor sells

    @property
    def changed(self) -> bool:
        return bool(self.items or self.freed)


def load_costs(path=COSTS_FILE) -> dict:
    """{"date", "currencies": {item: {"name", "currency"}}, "vendors": {npc: {"name", "neutral", "paid_in",
    "items": {item: {"name", "price", and once read at the vendor "build" and "date"}}}}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["currencies"] = {int(item_id): record for item_id, record in data.get("currencies", {}).items()}
    data["vendors"] = {int(npc): {**vendor, "items": {int(item_id): record for item_id, record in vendor["items"].items()}}
                       for npc, vendor in data.get("vendors", {}).items()}
    return data


def save_costs(costs: dict, path=COSTS_FILE) -> None:
    """Write the costs file, an item to a line."""
    def text(value):
        return json.dumps(value, ensure_ascii=False)

    def block(records, indent):
        return ",\n".join(f'{indent}"{key}": {text(record)}' for key, record in sorted(records.items()))

    vendors = []
    for npc, vendor in sorted(costs["vendors"].items()):
        fields = "".join(f"      {text(key)}: {text(value)},\n" for key, value in vendor.items() if key != "items")
        vendors.append(f'    "{npc}": {{\n{fields}      "items": {{\n{block(vendor["items"], " " * 8)}\n      }}\n    }}')
    Path(path).write_text(
        f'{{\n  "about": {text(costs["about"])},\n  "date": {text(costs["date"])},\n'
        f'  "currencies": {{\n{block(costs["currencies"], " " * 4)}\n  }},\n'
        '  "vendors": {\n' + ",\n".join(vendors) + "\n  }\n}\n", encoding="utf-8", newline="\n")


def _seller(source: list):
    """The npc id of a vendor's source, None for any other source."""
    return int(source[1]) if source[0] in _PRICE_FIELD and source[1].isdigit() else None


def price(db, costs: dict) -> Priced:
    """Open the items of a neutral vendor to both factions and write what the vendors ask in a currency;
    the report is kept as db.priced.

    An item only that vendor sells loses the faction the data keeps it for. One with a twin, or another
    source, has a reason for it that this file knows nothing of, and stays as it is. A price goes in the
    price field of the vendor's source as "<currency's item id>:<amount>", followed by ":b" while it is the
    beta's and no window of the vendor has shown it (capture.read_prices).
    """
    report = Priced(date=costs.get("date", ""))
    db.priced = report
    vendors = costs.get("vendors", {})
    neutral = {npc for npc, vendor in vendors.items() if vendor.get("neutral")}
    for item_id, item in sorted(db.items.items()):
        sellers = [_seller(source) for source in item["sources"]]
        if item["side"] and not item["twin"] and sellers and all(npc in neutral for npc in sellers):
            item["side"] = ""
            for source in item["sources"]:
                source[_SIDE_FIELD[source[0]]] = ""
            report.freed.append(item_id)

    used = set()
    for npc, vendor in sorted(vendors.items()):
        for item_id, record in sorted(vendor["items"].items()):
            sold = [source for source in db.items.get(item_id, {}).get("sources", ()) if _seller(source) == npc]
            if not sold:
                report.absent.append(item_id)
                continue
            beta = "" if "build" in record else ":b"
            for source in sold:
                source[_PRICE_FIELD[source[0]]] = f"{vendor['paid_in']}:{record['price']}{beta}"
            report.items.append(item_id)
            if not beta:
                report.read.append(item_id)
            used.add(vendor["paid_in"])
    report.currencies = {item_id: costs["currencies"][item_id] for item_id in sorted(used)}
    return report


# -- the drops counted in Forever -------------------------------------------------------------------------

DROPS_ABOUT = ("What Wowhead Forever recorded of the items' drops, read in the DungeonJournal addon (seen: per boss, "
               "the drops, the kills and the percent) and in the GearQuest Forever addon (tooltip: the creature it "
               "names) by _build/drops.py, and laid over the data by _build/corrections.py. Written by "
               "`python build.py --import-drops`: do not edit.")
DROP_LABEL = "w"
UNSURE = frozenset("kct")        # Classic's data, a clue, QuestieDB: not seen in Forever
MIN_DROPS = 3                    # what it takes to say another boss drops an item: one drop may be a stray record
_CREATURES = ("d", "m", "R")     # the sources whose third field names a creature and the fourth its rate
_CERTAIN_FIRST = {"s": 0, "f": 0, DROP_LABEL: 1}


@dataclass
class Confirmed:
    """What confirm() did with the drops counted in Forever."""
    journal: str = ""                               # the DungeonJournal they were read in
    date: str = ""
    known: int = 0                                  # items the file says something of
    items: list = field(default_factory=list)       # ids with a drop confirmed
    named: list = field(default_factory=list)       # of which the data named the dungeon and not the boss
    moved: list = field(default_factory=list)       # ids whose boss was another one: the counted one replaces it
    disputed: list = field(default_factory=list)    # ids named for another creature, on too little to replace it
    placed: list = field(default_factory=list)      # ids whose creature became a boss of the dungeon it is counted in
    sourced: list = field(default_factory=list)     # ids the data gave no source at all, given the bosses counted
    dungeons: list = field(default_factory=list)    # the instances added for the dungeons the data lacks (runs.py)
    settled: list = field(default_factory=list)     # pieces added from the game that a counted drop makes a dungeon's

    @property
    def changed(self) -> bool:
        return bool(self.items or self.moved or self.sourced)


def load_drops(path=DROPS_FILE) -> dict:
    """{"journal", "gearquest", "date", "items": {id: {"name", "seen": [...], "tooltip": {...}}}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["items"] = {int(item_id): record for item_id, record in data.get("items", {}).items()}
    return data


def save_drops(reading: dict, path=DROPS_FILE) -> None:
    """One item per line, in id order, so another reading shows as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    head = {name: reading.get(name, "") for name in ("journal", "gearquest", "date")}
    rows = [f'    "{item_id}": {json.dumps(reading["items"][item_id], ensure_ascii=False, sort_keys=True)}'
            for item_id in sorted(reading.get("items", {}))]
    text = ("{\n" + f'  "about": {json.dumps(DROPS_ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(value)},\n' for name, value in head.items())
            + '  "items": {\n' + ",\n".join(rows) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def _boss_words(name: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", name.lower().replace("'", "")).split())


def _same_boss(name: str, counted: str) -> bool:
    """Whether two names are one creature, however each source spells it (Ras Frostwhisper, Ras Frostwhisperer)
    and when one names a pair (Morphaz and Hazzas) or the journal gives two names for one line (A / B)."""
    one = _boss_words(name)
    for other in map(_boss_words, counted.split(" / ")):
        if one and other and (one.startswith(other) or other.startswith(one)
                              or set(one.split()) <= set(other.split()) or set(other.split()) <= set(one.split())):
            return True
    return False


def _place(name: str) -> str:
    """A dungeon's name without what tells its wings apart (Upper Blackrock Spire, Dire Maul: East) or what only
    one source calls it by (The Stockade, Stormwind Stockade)."""
    return re.sub(r"^(the|upper|lower|stormwind) ", "", name.split(":")[0].strip().lower())


def _instance(db, dungeon: str):
    """The id of the data's dungeon the journal names, or None."""
    wanted = _place(dungeon)
    return next((number for number, fields in sorted(db.instances.items())
                 if _place(fields[0]) == wanted and (fields + ["", ""])[1] != "raid"), None)


def _number(text: str):
    return int(text) if text.isdigit() else None


def _counted_drop(db, source: list, seen: list, tooltip) -> dict | None:
    """What was counted of this source: an entry of the journal or the tooltip, or None."""
    if source[2]:
        return next((entry for entry in seen if _same_boss(source[2], entry["boss"])),
                    tooltip if tooltip and _same_boss(source[2], tooltip["boss"]) else None)
    # the data names the dungeon alone: a boss of that dungeon; a boss of another one says the dungeon is wrong
    return next((entry for entry in seen if _instance(db, entry["dungeon"]) == _number(source[1])),
                None if seen else tooltip)


_NAMELESS = re.compile(r"^NPC \d+$")   # a creature ForeverDB saw drop an item and has no name for


def _place_seen(db, item: dict, seen: list) -> bool:
    """Write the creatures ForeverDB saw itself as bosses of the dungeon the journal counts them in; True
    when one was. What the data saw stays as it saw it: the journal only says where the creature is, names
    the one the data could not (when the item has no other creature), and gives the rate the data lacks."""
    creatures = [source for source in item["sources"] if source[0] in ("m", "R") and source[-1] not in UNSURE]
    placed = False
    for source in creatures:
        nameless = bool(_NAMELESS.match(source[2]))
        if nameless:
            entry = next((entry for entry in seen if entry["drops"] >= MIN_DROPS), None) if len(creatures) == 1 else None
        else:
            entry = next((entry for entry in seen if _same_boss(source[2], entry["boss"])), None)
        number = _instance(db, entry["dungeon"]) if entry else None
        if not number:
            continue
        rate, label = source[3], source[-1]
        if not rate or float(rate) <= 0:
            rate, label = f"{entry['percent']:g}", DROP_LABEL
        source[:] = ["d", str(number), entry["boss"].split(" / ")[0] if nameless else source[2], rate, "0", label]
        placed = True
    return placed


def _give_sources(db, item: dict, seen: list) -> bool:
    """Give an item the data has no source for the bosses the journal counted it on; True when it counted one.

    An item of ForeverDB's lists is then a dungeon's and no longer one "with no known source": the lists
    count it. A piece added from the game (align) gets the sources to show and stays where it showed, as it
    does with a source read in QuestieDB (fill). A tooltip alone gives nothing: it names a creature and no
    place, and such an item stays without a source.
    """
    counted = [entry for entry in seen if entry["drops"] >= MIN_DROPS]
    if not counted:
        return False
    sources = []
    for entry in counted:
        number = _instance(db, entry["dungeon"])
        boss, percent = entry["boss"].split(" / ")[0].replace("\\", ""), f"{entry['percent']:g}"
        sources.append(["d", str(number), boss, percent, "0", DROP_LABEL] if number
                       else ["m", "0", boss, percent, DROP_LABEL])
    item["sources"] = sources
    if not item.get("added"):
        item["groups"] = frozenset(set(item["groups"]) - {"u"} | {"d"})
    return True


def _one_per_boss(sources: list) -> list:
    """The sources without the second line of a boss of one dungeon: the data may hold a boss twice, as a boss
    and as a creature, under two spellings (Kirtonos, Kirtonos the Herald), or name the dungeon alone on one
    line and its boss on the next."""
    named = {source[1] for source in sources if source[0] == "d" and source[2]}
    kept = []
    for source in sources:
        if source[0] == "d" and (
                (not source[2] and source[1] in named)
                or any(other[0] == "d" and other[1] == source[1] and _same_boss(other[2], source[2]) for other in kept)):
            continue
        kept.append(source)
    return kept


def _dungeon_groups(item: dict, others: list) -> None:
    """An item a boss was counted for is a dungeon's, and a world drop only while one of its other sources
    says so. A piece added from the game stays with the items of no known source (fill)."""
    if item.get("added"):
        return
    groups = set(item["groups"]) | {"d"}
    if not any(source[0] in ("m", "R", "w") for source in others):
        groups -= {"w", "R"}
    item["groups"] = frozenset(groups)


def confirm(db, reading: dict) -> Confirmed:
    """Lay the drops counted in Forever over the sources that are not confirmed; the report is kept as db.confirmed.

    A source whose boss was counted takes the rate counted and the label w, and comes first among the
    item's sources: the addon shows the first one. Where the journal counts another boss, often enough to
    be no stray record, that boss replaces the creatures the data names: as a boss of its dungeon, or as a
    creature when nothing has such a dungeon. A tooltip alone replaces nothing: it names one creature,
    when several may drop the item. What ForeverDB saw itself is left alone.

    The journal counts dungeon by dungeon. A creature the data gives no place (the bosses of an arena, of a
    dungeon ForeverDB's table lacks) is written as a boss of the dungeon it was counted in, the ones
    ForeverDB saw itself among them (_place_seen); the dungeons of Forever the data has no instance for are
    added first (runs.add_dungeons). db.boss_wings keeps the wing of each boss (runs.boss_wings), for the
    data files.

    An item the data gives no source at all takes the bosses the journal counted it on (_give_sources), and
    is then an item of the lists like any other.
    """
    report = Confirmed(journal=reading.get("journal", ""), date=reading.get("date", ""),
                       known=len(reading.get("items", {})))
    db.confirmed = report
    db.boss_wings = runs.boss_wings(reading)
    if reading.get("items"):
        report.dungeons = runs.add_dungeons(db)
    for item_id in sorted(reading.get("items", {})):
        item, record = db.items.get(item_id), reading["items"][item_id]
        if item is None:
            continue
        seen, tooltip, found = record.get("seen", []), record.get("tooltip"), False
        if not item["sources"]:
            if _give_sources(db, item, seen):
                report.sourced.append(item_id)
            continue
        placed = _place_seen(db, item, seen)
        unsure = [source for source in item["sources"] if source[0] in _CREATURES and source[-1] in UNSURE]
        if not unsure:
            if placed:
                item["sources"] = _one_per_boss(item["sources"])
                _dungeon_groups(item, [source for source in item["sources"] if source[0] != "d"])
                report.placed.append(item_id)
            continue
        for source in unsure:
            counted = _counted_drop(db, source, seen, tooltip)
            if counted is None:
                continue
            if not source[2]:
                source[2] = counted["boss"].split(" / ")[0]
                report.named.append(item_id)
            source[3], source[-1] = f"{counted['percent']:g}", DROP_LABEL
            number = _instance(db, counted.get("dungeon", "")) if source[0] != "d" else None
            if number:
                source[:] = ["d", str(number), source[2], source[3], "0", DROP_LABEL]
                placed = True
            found = True
        if found:
            item["sources"].sort(key=lambda source: _CERTAIN_FIRST.get(source[-1], 2))
            report.items.append(item_id)
        if found or placed:
            if placed:
                item["sources"] = _one_per_boss(item["sources"])
                _dungeon_groups(item, [source for source in item["sources"] if source[0] != "d"])
                report.placed.append(item_id)
            continue
        if any(source[0] in _CREATURES and source[-1] not in UNSURE for source in item["sources"]):
            continue
        best = next((entry for entry in seen if entry["drops"] >= MIN_DROPS), None)
        if best is None:
            report.disputed.append(item_id)
            continue
        rest = [source for source in item["sources"] if source not in unsure]
        number, boss, percent = _instance(db, best["dungeon"]), best["boss"].split(" / ")[0], f"{best['percent']:g}"
        counted = ["d", str(number), boss, percent, "0", DROP_LABEL] if number else ["m", "0", boss, percent, DROP_LABEL]
        item["sources"] = [counted, *rest]
        _dungeon_groups(item, rest)
        report.moved.append(item_id)
    report.settled = _settle_added(db)
    return report


def _settle_added(db) -> list:
    """A piece added from the game (align) whose drop the journal counted in Forever is a dungeon's item, or a raid's,
    of the phase that source needs: players loot it. It used to stay with the items of no known source, hidden until
    the last phase, whatever was counted: The Blackrock Slicer, the best melee weapon the simulator measures for a
    Survival Hunter, and Heart of Wyrmthalak were in no list a player sees. A source read in QuestieDB alone settles
    nothing: it is Classic's. Returns the ids settled."""
    settled = []
    for item_id, item in db.items.items():
        if not item.get("added"):
            continue
        counted = [source for source in item["sources"] if source[0] == "d" and source[-1] == DROP_LABEL]
        if not counted:
            continue
        raids = [phases.source_raid(source, item["name"]) for source in counted]
        item["groups"] = frozenset("r" if raid else "d" for raid in raids)
        item["phase"] = min(phases.raid_phase(raid) if raid else phases.PRE_RAID for raid in raids)
        settled.append(item_id)
    return sorted(settled)
