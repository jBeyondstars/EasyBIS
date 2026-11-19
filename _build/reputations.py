"""Which items and enchants ask for a reputation, and what is known of how to earn one.

Three kinds of requirement:
  w  the item itself asks for it: the vendor sells it from that standing and the wearer needs it
     (ForeverDB's Items.lua, "r<faction>~<standing>");
  q  the only quests that reward the item ask for it (QuestieDB's requiredMinRep);
  r  the recipe is sold against it: the crafter needs it, not the wearer (ForeverDB's Recipes.lua). The
     recipe's own item is kept, and its vendor as QuestieDB places it: that is what the faction sells.

`build.py --import-reputations` reads them and keeps the result in corrections/reputations.json, as
`--import-questie` does for the sources: ForeverDB's Items.lua and Recipes.lua are not among the files the
build needs, and nothing here is needed to build. ForeverDB's data is GPL-3.0 with an attribution term,
QuestieDB's is GPL-3.0 (NOTICE.txt).

How a reputation is earned is QuestieDB's quest table and nothing else: the quests that reward it, their
amounts and whether they repeat. What no source says stays unknown. In particular the reputation creatures
give is in no data file, and the sum of the quests done once is a ceiling: it does not take out the quests
that exclude one another.
"""
from __future__ import annotations

import datetime
import json
import re
from collections import Counter
from pathlib import Path

import questie

FILE = Path(__file__).resolve().parent / "corrections" / "reputations.json"
ABOUT = ("The reputations listed items and enchants ask for, read in ForeverDB's Items.lua and Recipes.lua and in "
         "QuestieDB by _build/reputations.py. Written by `python build.py --import-reputations`: do not edit.")
SOURCE_FILES = ("Items.lua", "Recipes.lua")

WEAR, QUEST, RECIPE = "w", "q", "r"
METHODS_KEPT = 8           # quests kept per faction to name as a way to earn it: the addon keeps the player's class

# The factions the lists ask for: id -> (the name ForeverDB's data writes, the side that can earn it).
FACTIONS = {
    21: ("Booty Bay", ""),
    59: ("Thorium Brotherhood", ""),
    270: ("Zandalar Tribe", ""),
    369: ("Gadgetzan", ""),
    470: ("Ratchet", ""),
    509: ("The League of Arathor", "a"),
    510: ("The Defilers", "h"),
    529: ("Argent Dawn", ""),
    576: ("Timbermaw Hold", ""),
    577: ("Everlook", ""),
    609: ("Cenarion Circle", ""),
    729: ("Frostwolf Clan", "h"),
    730: ("Stormpike Guard", "a"),
    749: ("Hydraxian Waterlords", ""),
    910: ("Brood of Nozdormu", ""),
    2798: ("Darkspear Raiders", "h"),
    2799: ("Theramore Expeditionary Force", "a"),
    2819: ("The Watchers", ""),
    2827: ("Powderfuse", ""),
}
_BY_NAME = {name: number for number, (name, _) in FACTIONS.items()}

# QuestieDB's quest fields (src/meta), beyond the ones questie.py reads.
QUEST_CLASSES, QUEST_MIN_REPUTATION, QUEST_SPECIAL_FLAGS, QUEST_REPUTATION_REWARD = 7, 19, 24, 26
REPEATABLE = 1

_FACT = re.compile(r"^r([^~]+)~(\d+)$")
_ITEM_LINE = re.compile(r'\[(\d+)\]="([^"]*)"')
_PROFESSION = re.compile(r"(\w+)=\{\{")
_RECIPE = re.compile(r'\{(\d+),"([^"]*)",(\d+),\d+,\d+,\d+,(\d+),[\d.]+,"[^"]*","([^"]*)"')


def standing_of(value: int) -> int:
    """The standing (4 Friendly to 7 Exalted, 3 Neutral) a reputation amount counted from Neutral 0 is in."""
    for threshold, standing in ((42000, 7), (21000, 6), (9000, 5), (3000, 4)):
        if value >= threshold:
            return standing
    return 3


def read_item_facts(text: str) -> tuple[dict[int, tuple[int, int]], dict[int, str]]:
    """({item: (faction, standing)}, {item: the name of a faction the table above lacks}) from ForeverDB's
    Items.lua. The second part is for the build to refuse: a listed item must not lose its requirement."""
    facts, others = {}, {}
    for item_id, raw in _ITEM_LINE.findall(text[text.index("ns.items"):]):
        for part in raw.split("|"):
            found = _FACT.match(part)
            if found and found.group(1) in _BY_NAME:
                facts[int(item_id)] = (_BY_NAME[found.group(1)], int(found.group(2)))
            elif found:
                others[int(item_id)] = found.group(1)
    return facts, others


def read_recipes(text: str) -> tuple[dict[int, dict], dict[int, str]]:
    """({spell: {"profession", "skill", "makes", "learn"}}, {item: name}) from ForeverDB's Recipes.lua."""
    start, end = text.index("ns.recipes = {"), text.index("ns.names")
    body = text[start:end]
    marks = [(found.start(), found.group(1)) for found in _PROFESSION.finditer(body)]
    spells = {}
    for index, (at, profession) in enumerate(marks):
        block = body[at:marks[index + 1][0] if index + 1 < len(marks) else len(body)]
        for spell, _, skill, makes, learn in _RECIPE.findall(block):
            spells[int(spell)] = {"profession": profession, "skill": int(skill), "makes": int(makes), "learn": learn}
    line = text[end:text.index("\n", end)]
    return spells, {int(item): name for item, name in _ITEM_LINE.findall(line)}


class _Reader:
    def __init__(self, db, store, facts: dict, spells: dict, names: dict) -> None:
        self.db, self.store, self.facts, self.spells, self.names = db, store, facts, spells, names
        self.made = {}                # item -> the spells that make it
        for spell, recipe in spells.items():
            self.made.setdefault(recipe["makes"], []).append(spell)
        self.vendors = {}             # npc -> [name, uiMap, x, y]
        self._quests = {}

    def quest_gate(self, quest: int):
        """(faction, standing) the quest asks for, or None."""
        if quest not in self._quests:
            needed = self.store.table("Quest", quest, QUEST_MIN_REPUTATION)
            gate = None
            if needed and needed[0] in FACTIONS and standing_of(needed[1]) > 3:
                gate = (needed[0], standing_of(needed[1]))
            self._quests[quest] = gate
        return self._quests[quest]

    def vendor(self, item: dict):
        """(npc, price in copper) of the first vendor of an item, or (None, 0)."""
        for source in item["sources"]:
            if source[0] == "V":
                return self.keep_vendor(int(source[1])), int(source[2] or 0)
            if source[0] == "v" and source[1].isdigit():
                return self.keep_vendor(int(source[1]), source[2:5]), int(source[6] or 0)
        return None, 0

    def keep_vendor(self, npc: int, written=None) -> int:
        if npc not in self.vendors:
            name, ui_map, x, y = (list(written or self.db.vendors.get(npc) or []) + [""] * 4)[:4]
            if not name or re.fullmatch(r"NPC \d+", name):   # ForeverDB has the place of some vendors, not the name
                name = self.store.row("Npc", npc).get(questie.NPC_NAME) or ""
            self.vendors[npc] = [name, ui_map, x, y]
        return npc

    def wear(self, item_id: int, item: dict) -> list[dict]:
        faction, standing = self.facts[item_id]
        npc, price = self.vendor(item)
        record = {"side": "", "faction": faction, "standing": standing, "kind": WEAR}
        if npc:
            record.update(vendor=npc, price=price)
        return [record]

    def quest(self, item: dict) -> list[dict]:
        """One requirement per side the item's quests agree on. An item that also comes from anywhere else, or
        from a quest of that side that asks for nothing, needs no reputation."""
        quests = [source for source in item["sources"] if source[0] == "q" and source[1].isdigit()]
        if not quests or len(quests) != sum(1 for source in item["sources"] if source[0] != "r"):
            return []
        found = {}
        for side in ("a", "h"):
            open_to = [source for source in quests if (source + [""] * 5)[4] in ("", side)]
            gates = [self.quest_gate(int(source[1])) for source in open_to]
            if gates and all(gates):
                found[side] = (gates[0], open_to[0][2])
        if found.get("a") == found.get("h"):
            found = {"": found["a"]} if found.get("a") else {}
        return [{"side": side, "faction": gate[0], "standing": gate[1], "kind": QUEST, "via": title}
                for side, (gate, title) in found.items()]

    def recipe_of(self, spell: int) -> dict | None:
        """What a spell learned from a recipe sold against a reputation asks, or None: the faction, the standing,
        the recipe's item and name, the profession and its skill, and the recipe's vendor when QuestieDB has one."""
        recipe = self.spells.get(spell)
        learn = recipe["learn"] if recipe else ""
        if not learn.startswith("i") or int(learn[1:]) not in self.facts:
            return None
        recipe_id = int(learn[1:])
        faction, standing = self.facts[recipe_id]
        record = {"faction": faction, "standing": standing, "kind": RECIPE, "via": self.names.get(recipe_id, ""),
                  "recipe": recipe_id, "profession": recipe["profession"], "skill": recipe["skill"]}
        npc = self.recipe_vendor(recipe_id)
        if npc:
            record["vendor"] = npc
        return record

    def recipe_vendor(self, recipe_id: int) -> int | None:
        """The first vendor QuestieDB names for a recipe's item, kept with its place, or None. ForeverDB's data
        names the vendor and the zone but not the npc."""
        for npc in sorted(set(self.store.ids("Item", recipe_id, questie.ITEM_VENDORS))):
            row = self.store.row("Npc", npc)
            if not row.get(questie.NPC_NAME):
                continue
            zone = row.get(questie.NPC_ZONE) or 0
            spots = (self.store.table("Npc", npc, questie.NPC_SPAWNS) or {}).get(zone) or []
            x, y = (spots[0] + [0, 0])[:2] if spots and isinstance(spots[0], list) else (0, 0)
            ui_map = self.store.zones.ui_maps.get(zone, 0)
            place = [ui_map, round(x, 1), round(y, 1)] if ui_map and x > 0 and y > 0 else [ui_map or "", "", ""]
            # ForeverDB's own place of a vendor goes first, as for the pieces sold against a reputation
            return self.keep_vendor(npc, None if self.db.vendors.get(npc) else [row[questie.NPC_NAME], *place])
        return None

    def recipe(self, item_id: int, item: dict) -> list[dict]:
        crafted = [int(source[3]) for source in item["sources"] if source[0] == "c" and source[3].isdigit()]
        for spell in [spell for spell in crafted if spell in self.spells] or self.made.get(item_id, []):
            found = self.recipe_of(spell)
            if found:
                return [{"side": "", **found}]
        return []

    def item(self, item_id: int, item: dict) -> list[dict]:
        if item_id in self.facts:
            return self.wear(item_id, item)
        return self.quest(item) or self.recipe(item_id, item)

    def enchant(self, enchant: str, info: list) -> dict | None:
        number = int(enchant[1:])
        where = (info + ["", "", ""])[2]
        if enchant[0] == "s":
            record = self.recipe_of(number)
            if not record:
                return None
            if "scroll" in where:
                record["scroll"] = True
            return record
        if number in self.facts:
            faction, standing = self.facts[number]
            return {"faction": faction, "standing": standing, "kind": WEAR}
        quests = sorted(set(self.store.ids("Item", number, questie.ITEM_QUESTS)))
        gates = [self.quest_gate(quest) for quest in quests]
        if quests and all(gates):
            title = self.store.row("Quest", quests[0]).get(questie.QUEST_NAME, "")
            return {"faction": gates[0][0], "standing": gates[0][1], "kind": QUEST, "via": title}
        return None


def _quest_side(row: dict) -> str:
    races = row.get(questie.QUEST_RACES) or 0
    if races and not races & questie.HORDE_RACES:
        return "a"
    return "h" if races and not races & questie.ALLIANCE_RACES else ""


def earning(store) -> dict[int, dict]:
    """{faction: {"quests", "repeatable", "once": {"a", "h"}, "methods": [[title, amount, repeats, side, classes],
    ...]}}: the quests QuestieDB says reward each faction. classes: the game's mask of the classes that may take
    the quest, 0 for all. The repeatable ones come first among the methods, then the ones every class may take
    (a class's own quest is often a raid's token turned in), then the largest rewards. One quest of a family
    is kept: the others differ by what they ask for, not by what they give."""
    found = {number: [] for number in FACTIONS}
    for quest in store.numbers("Quest"):
        rewards = store.table("Quest", quest, QUEST_REPUTATION_REWARD)
        if not rewards:
            continue
        row = store.row("Quest", quest)
        repeats = bool((row.get(QUEST_SPECIAL_FLAGS) or 0) & REPEATABLE)
        for faction, amount in rewards:
            if faction in found and amount > 0:
                found[faction].append((row.get(questie.QUEST_NAME) or "", amount, repeats, _quest_side(row),
                                       row.get(QUEST_CLASSES) or 0))
    out = {}
    for faction, quests in found.items():
        once = [quest for quest in quests if not quest[2]]
        ranked, named = sorted(quests, key=lambda quest: (not quest[2], quest[4] != 0, -quest[1], quest[0])), set()
        methods = []
        for title, amount, repeats, side, classes in ranked:
            family = title.split(" - ")[0]   # "Craftsman's Writ - Runecloth Bag": one of a family is enough
            if title and family not in named and len(methods) < METHODS_KEPT:
                named.add(family)
                methods.append([title, amount, int(repeats), side, classes])
        out[faction] = {
            "quests": len(quests), "repeatable": len(quests) - len(once),
            "once": {side: sum(quest[1] for quest in once if quest[3] in ("", side)) for side in "ah"},
            "methods": methods,
        }
    return out


def collect(db, folder, store, shown=(), today: str | None = None) -> dict:
    """What corrections/reputations.json holds. folder: where ForeverDB's Items.lua and Recipes.lua are;
    shown: the ids the lists hold."""
    folder = Path(folder)
    facts, others = read_item_facts((folder / "Items.lua").read_text(encoding="utf-8"))
    listed = sorted({name for item_id, name in others.items() if item_id in shown})
    if listed:
        raise ValueError(f"listed items ask for factions reputations.FACTIONS lacks: {', '.join(listed)}")
    spells, names = read_recipes((folder / "Recipes.lua").read_text(encoding="utf-8"))
    reader = _Reader(db, store, facts, spells, names)
    items = {}
    for item_id, item in db.items.items():
        found = reader.item(item_id, item)
        if found:
            items[item_id] = found
    enchants = {}
    for enchant, info in db.enchant_info.items():
        found = reader.enchant(enchant, info)
        if found:
            enchants[enchant] = found
    return {
        "foreverdb": db.meta["version"], "questiedb": store.version, "commit": store.commit,
        "date": today or datetime.date.today().isoformat(),
        "factions": earning(store), "vendors": reader.vendors, "items": items, "enchants": enchants,
    }


def load(path=FILE) -> dict:
    """The reading kept by save(), with its numbers back as numbers; empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    for name in ("factions", "vendors", "items"):
        data[name] = {int(number): value for number, value in data.get(name, {}).items()}
    return data


def save(reading: dict, path=FILE) -> None:
    """One record per line, in id order, so another reading shows as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def rows(records: dict, key=int) -> str:
        return ",\n".join(f'    "{name}": {json.dumps(records[name], ensure_ascii=False, sort_keys=True)}'
                          for name in sorted(records, key=key))

    head = {name: reading.get(name, "") for name in ("foreverdb", "questiedb", "commit", "date")}
    text = ("{\n" + f'  "about": {json.dumps(ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(value)},\n' for name, value in head.items())
            + '  "factions": {\n' + rows(reading.get("factions", {})) + "\n  },\n"
            + '  "vendors": {\n' + rows(reading.get("vendors", {})) + "\n  },\n"
            + '  "enchants": {\n' + rows(reading.get("enchants", {}), lambda enchant: int(enchant[1:])) + "\n  },\n"
            + '  "items": {\n' + rows(reading.get("items", {})) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def faction_vendors(reading: dict, shown) -> dict[int, int]:
    """{faction: the npc that sells the most listed pieces of that faction}."""
    counts = {}
    for item_id in shown:
        for record in reading.get("items", {}).get(item_id, ()):
            if record["kind"] == WEAR and record.get("vendor"):
                counts.setdefault(record["faction"], Counter())[record["vendor"]] += 1
    return {faction: sorted(sold.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
            for faction, sold in counts.items()}
