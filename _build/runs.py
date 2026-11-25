"""The runs of the Dungeons tab: which part of a dungeon a boss is in, and which dungeon a quest is done in.

ForeverDB's data places a drop in an instance. A player runs less than that: Blackrock Spire is two runs,
Dire Maul three, Stratholme two, the Scarlet Monastery four. The DungeonJournal addon counts the drops
wing by wing, and corrections/drops.json keeps the name it gives each one ("Upper Blackrock Spire",
"Dire Maul: North"): boss_wings reads the wing of a boss there, and in BOSS_WINGS for the few the counts
do not place.

The journal also counts six dungeons of Forever that ForeverDB's table of instances lacks (DUNGEONS):
corrections.confirm adds them, so their bosses are bosses of a dungeon and not creatures of nowhere.

A quest's source says nothing of where the quest is done. QuestieDB sorts each quest under a zone, and
that zone is the instance for a quest done in one: `build.py --import-dungeon-quests` reads it for the
quests of the data's items and keeps it in corrections/quests.json. Nothing here is needed to build.
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "quests.json"
ABOUT = ("The instance each quest of the data's items is done in, when QuestieDB (https://github.com/Questie/QuestieDB, "
         "GPL-3.0) sorts the quest under one, read by _build/runs.py. Written by "
         "`python build.py --import-dungeon-quests`: do not edit.")

# The wings of an instance, as the DungeonJournal names them: instance -> {key: name}. The key is what the data
# files write; the addon has the names in its own languages.
WINGS = {
    189: {"g": "Scarlet Monastery: Graveyard", "l": "Scarlet Monastery: Library", "a": "Scarlet Monastery: Armory",
          "c": "Scarlet Monastery: Cathedral"},
    229: {"l": "Lower Blackrock Spire", "u": "Upper Blackrock Spire"},
    329: {"l": "Stratholme: Living", "u": "Stratholme: Undead"},
    429: {"e": "Dire Maul: East", "w": "Dire Maul: West", "n": "Dire Maul: North"},
}

# The dungeons of Forever the journal counts drops in and ForeverDB's data has no instance for: the name the
# journal gives -> the instance id GetInstanceInfo returns, as the ForeverDungeonRoutes addon lists them
# (Data/Dungeons.lua, 2026-11-20).
DUNGEONS = {
    "Hall of Thanes": 3065, "The Drowned City": 2970, "Krol'dok Stronghold": 3039, "Alcaz Prison": 2994,
    "Blackmaw Hold": 2974, "Shaper's Terrace": 3001,
}
LABEL = "w"   # corrections.DROP_LABEL: the journal's counts

# Bosses the counts do not place in a wing (too few kills recorded, or named by a tooltip alone): instance ->
# {boss: wing key}. Classic's own geography, written down by hand.
BOSS_WINGS = {
    229: {"Lord Valthalak": "u", "Mor Grayhoof": "l", "Burning Felguard": "l", "Spirestone Butcher": "l",
          "Spirestone Battle Lord": "l", "Spirestone Lord Magus": "l", "Bannok Grimaxe": "l", "Crystal Fang": "l",
          "Ghok Bashguud": "l", "Jed Runewatcher": "u", "Goraluk Anvilcrack": "u", "Solakar Flamewreath": "u"},
    329: {"Malor the Zealous": "l", "Skul": "l", "Stonespine": "u", "Hearthsinger Forresten": "l",
          "Postmaster Malown": "l", "Fras Siabi": "l", "Sothos": "l", "Jarien": "l", "Black Guard Swordsmith": "u",
          "Crimson Hammersmith": "l"},
    429: {"Gordok Mastiff": "n", "Lethtendris": "e", "Pimgib": "e", "Zevrim Thornhoof": "e", "Hydrospawn": "e",
          "Alzzin the Wildshaper": "e", "Isalien": "e", "Pusillin": "e", "Lord Hel'nurath": "w", "Tsu'zee": "w",
          "Tendris Warpwood": "w", "Illyanna Ravenoak": "w", "Magister Kalendris": "w", "Immol'thar": "w",
          "Prince Tortheldrin": "w", "Guard Mol'dar": "n", "Stomper Kreeg": "n", "Guard Fengus": "n",
          "Guard Slip'kik": "n", "Captain Kromcrush": "n", "Cho'Rush the Observer": "n", "King Gordok": "n",
          "Knot Thimblejack": "n"},
}

# Quests done in a dungeon that has wings: quest -> wing key. QuestieDB gives the instance and no more; this
# is where the quest's creatures are in Classic, and only the quests one wing is enough for. The class books
# of Dire Maul drop in every wing, and the quests against the Scarlet Crusade's leaders need three of them.
QUEST_WINGS = {
    4903: "l", 5081: "l",    # Warlord's Command, Maxwell's Mission: Omokk, Voone, Wyrmthalak
    4974: "u", 5102: "u",    # For The Horde!, General Drakkisath's Demise
    5166: "u", 5167: "u",    # the Chromatic Carapace is Gyth's
    5125: "u",               # Aurius' Reckoning: Baron Rivendare
    1318: "n", 7703: "n",    # Unfinished Gordok Business: the king's tribute
    8949: "n",               # Falrin's Vendetta: the warbeads of the Gordok ogres
    7462: "w", 7877: "w",    # The Treasure of the Shen'dralar: after Immol'thar and the prince
    7488: "e", 7489: "e",    # Lethtendris's Web
    1049: "l",               # Compendium of the Fallen
    1051: "g",               # Vorrel's Revenge: Vorrel Sengutz waits in the graveyard
    79970: "c",              # Aeonas the Vindicated: Scarlet Monastery cathedral
}

# Quests done in a dungeon that QuestieDB sorts elsewhere: quest -> instance.
QUEST_INSTANCES = {
    5166: 229, 5167: 229,    # Breastplate of the Chromatic Flight, Legplates of the Chromatic Defier
    8257: 109,               # Blood of Morphaz
    79970: 189,              # Aeonas the Vindicated
    82084: 209,              # A Lesson in Literacy: Farraki Papyrus
    84332: 329,              # A Thane's Gratitude
    92065: 2974,             # Blackmaw Reclamation
    92070: 2974,             # A Lost Memento
    93404: 349,              # Rot and Regret: Vial of Earth Song Water in Maraudon
    95790: 3001,             # Digestible Research
    97049: 3001,             # Essence of Seeping Slimes
}


def _place(name: str) -> str:
    """A dungeon's name without what tells its wings apart or what only one source calls it by: the same
    rule as corrections._place, which this module cannot import."""
    return re.sub(r"^(the|upper|lower|stormwind) ", "", name.split(":")[0].strip().lower())


def add_dungeons(db) -> list[int]:
    """Give the data the dungeons of DUNGEONS it has no instance for; returns the ids added."""
    known = {_place(fields[0]) for fields in db.instances.values()}
    added = []
    for name, number in sorted(DUNGEONS.items(), key=lambda pair: pair[1]):
        if number not in db.instances and _place(name) not in known:
            db.instances[number] = [name, "dungeon", "", "", "", "", LABEL]
            added.append(number)
    return added


def wing_key(dungeon: str) -> tuple[int, str] | None:
    """(instance, wing key) for a wing's name as the journal writes it, or None for a name that is no wing."""
    for instance, wings in WINGS.items():
        for key, name in wings.items():
            if name == dungeon:
                return instance, key
    return None


def _words(name: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", name.lower().replace("'", "")).split())


def boss_wings(reading: dict) -> dict[int, dict[str, str]]:
    """{instance: {boss, in lower-case words: wing key}}: the journal's counts first, then BOSS_WINGS.

    A boss the journal counts in two wings of one instance is in neither for sure: the counts say nothing
    of it."""
    found, twice = {}, set()
    for record in reading.get("items", {}).values():
        for entry in record.get("seen", ()):
            wing = wing_key(entry["dungeon"])
            if wing is None:
                continue
            instance, key = wing
            for boss in entry["boss"].split(" / "):
                boss = _words(boss)
                if found.setdefault(instance, {}).setdefault(boss, key) != key:
                    twice.add((instance, boss))
    for instance, boss in twice:
        del found[instance][boss]
    for instance, bosses in BOSS_WINGS.items():
        for boss, key in bosses.items():
            found.setdefault(instance, {}).setdefault(_words(boss), key)
    return found


def wing_of(wings: dict, instance: int, boss: str) -> str:
    """The wing key of a boss as a source names it, or "" when nothing places it. Names differ a little
    from one source to the other (Ras Frostwhisper, Ras Frostwhisperer): a name that begins another is it."""
    known = wings.get(instance) or {}
    words = _words(boss)
    if not words:
        return ""
    if words in known:
        return known[words]
    close = {key for name, key in known.items() if name.startswith(words) or words.startswith(name)}
    return close.pop() if len(close) == 1 else ""


# -- the quests done in a dungeon --------------------------------------------------------------------------

def collect_quests(db, store, today: str | None = None) -> dict:
    """What corrections/quests.json holds: for the quests that are a source of the data's items, the instance
    QuestieDB sorts them under. store: a questie.Store."""
    import questie   # here: questie imports phases, and a build needs neither

    add_dungeons(db)
    names = {}   # the data's instances by name, and without the article QuestieDB gives some of them
    for number, fields in db.instances.items():
        names[fields[0]] = number
        names.setdefault(re.sub(r"^The ", "", fields[0]), number)
    quests = {}
    for item in db.items.values():
        for source in item["sources"]:
            if source[0] != "q" or not source[1].isdigit() or int(source[1]) in quests:
                continue
            quest = int(source[1])
            row = store.row("Quest", quest)
            zone = row.get(questie.QUEST_ZONE) or 0
            if zone <= 0:
                continue
            name = store.zones.names.get(zone)
            if name is None:
                continue
            instance = names.get(name, names.get(re.sub(r"^The ", "", name), store.zones.by_name.get(name)))
            if instance in db.instances:
                quests[quest] = {"name": row.get(questie.QUEST_NAME) or source[2], "instance": instance}
    return {"questiedb": store.version, "date": today or datetime.date.today().isoformat(), "quests": quests}


def load_quests(path=FILE) -> dict:
    """{"questiedb", "date", "quests": {id: {"name", "instance"}}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["quests"] = {int(quest): record for quest, record in data.get("quests", {}).items()}
    return data


def save_quests(reading: dict, path=FILE) -> None:
    """One quest per line, in id order, so another reading shows as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [f'    "{quest}": {json.dumps(reading["quests"][quest], ensure_ascii=False, sort_keys=True)}'
            for quest in sorted(reading.get("quests", {}))]
    text = ("{\n" + f'  "about": {json.dumps(ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(reading.get(name, ""))},\n' for name in ("questiedb", "date"))
            + '  "quests": {\n' + ",\n".join(rows) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def quest_places(db, reading: dict) -> dict[int, tuple[int, str]]:
    """{quest: (instance, wing key or "")} for the quests done in a dungeon the data knows: QuestieDB's
    reading, then QUEST_INSTANCES, and the wing QUEST_WINGS gives. A raid's quests are left out: a raid
    is not run again and again."""
    places = {quest: record["instance"] for quest, record in reading.get("quests", {}).items()}
    places.update(QUEST_INSTANCES)
    found = {}
    for quest, instance in places.items():
        fields = db.instances.get(instance)
        if not fields or (fields + ["", ""])[1] == "raid":
            continue
        wing = QUEST_WINGS.get(quest, "")
        found[quest] = (instance, wing if wing in WINGS.get(instance, {}) else "")
    return found
