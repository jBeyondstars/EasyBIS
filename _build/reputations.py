"""Which items and enchants ask for a reputation, and what is known of how to earn one.

Three kinds of requirement:
  w  the item itself asks for it: the vendor sells it from that standing and the wearer needs it
     (ForeverDB's Items.lua, "r<faction>~<standing>"; for a piece it gives none, the game's own tooltip,
     "Requires <faction> - <standing>", as the capture tool read it: read_capture);
  q  the only quests that reward the item ask for it (QuestieDB's requiredMinRep);
  r  the recipe is sold against it: the crafter needs it, not the wearer (ForeverDB's Recipes.lua). The
     recipe's own item is kept, and its vendor as QuestieDB places it: that is what the faction sells.
A piece ForeverDB names no vendor for takes the one QuestieDB names, without a price, or else the quest
ForeverDB says rewards it.

`build.py --import-reputations` reads them and keeps the result in corrections/reputations.json, as
`--import-questie` does for the sources: ForeverDB's Items.lua and Recipes.lua are not among the files the
build needs, and nothing here is needed to build. ForeverDB's data is GPL-3.0 with an attribution term,
QuestieDB's and Questie's are GPL-3.0 (NOTICE.txt).

What the build cannot place is reported, not left out in silence (gaps): a faction outside FACTIONS that a quest
or a recipe of a listed piece asks for, and a listed piece a quartermaster sells that nothing says the
requirement of.

How a reputation is earned is QuestieDB's quest table and nothing else: the quests that reward it, their
amounts, whether they repeat, and the standings they are offered between. The quests the Questie addon hides
because the game does not have them (its QuestieQuestBlacklist.lua, read as on Forever) are left out. What
no source says stays unknown. In particular the reputation creatures give is in no data file, and the sum of
the quests done once is a ceiling: of quests that exclude one another (QuestieDB's exclusiveTo) and of the
quests that follow each of them, it counts the branch that gives the most.
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
    889: ("Warsong Outriders", "h"),
    890: ("Silverwing Sentinels", "a"),
    910: ("Brood of Nozdormu", ""),
    2798: ("Darkspear Raiders", "h"),
    2799: ("Theramore Expeditionary Force", "a"),
    2819: ("The Watchers", ""),
    2827: ("Powderfuse", ""),
}
_BY_NAME = {name: number for number, (name, _) in FACTIONS.items()}
# The battleground whose quests earn a faction: the area QuestieDB places most of them in (earning checks it).
# The addon names it in the game's language.
BATTLEGROUNDS = {509: 3358, 510: 3358, 729: 2597, 730: 2597, 889: 3277, 890: 3277, 2798: 16606, 2799: 16606}
# The battlegrounds' quartermasters ForeverDB's data names no requirement for any piece of (QuestieDB's npcs, the
# "Supply Officers"): with the vendors of the pieces that have one, what gaps watches.
QUARTERMASTERS = {13216: 730, 13217: 730, 13218: 729, 13219: 729, 14753: 890, 14754: 889}

# QuestieDB's quest fields (src/meta), beyond the ones questie.py reads.
QUEST_CLASSES, QUEST_PRE_GROUP, QUEST_PRE_SINGLE, QUEST_EXCLUSIVE = 7, 12, 13, 16
QUEST_MIN_REPUTATION, QUEST_MAX_REPUTATION, QUEST_NEXT = 19, 20, 22
QUEST_SPECIAL_FLAGS, QUEST_REPUTATION_REWARD, QUEST_MAX_LEVEL = 24, 26, 32
REPEATABLE = 1
NEUTRAL, EXALTED = 3, 7
LEVEL_CAP = 60      # the lists are for level 60: a quest offered only below it is left out

# The Questie addon, installed next to QuestieDB, lists the quests its database holds and the game does not.
QUESTIE = "Questie"
BLACKLIST = Path("Database", "Corrections", "QuestieQuestBlacklist.lua")
# How its conditions read on Forever: Questie takes Forever for Classic Era (Modules/Expansions.lua, where the
# expansions are numbered in this order); HIDE_ON_MAP keeps a quest, only off the map.
_CONDITION_WORDS = {
    "true": "True", "false": "False", "and": "and", "or": "or", "not": "not",
    "Expansions.Current": "1", "Expansions.Era": "1", "Expansions.Tbc": "2", "Expansions.Wotlk": "3",
    "Expansions.Cata": "4", "Expansions.MoP": "5", "Questie.IsForever": "True", "HIDE_ON_MAP": "False",
    "ContentPhases.activePhases.TBC": "0",
}
_HIDDEN_ROW = re.compile(r"^\s*\[(\d+)\]\s*=\s*(.+?),?\s*(?:--.*)?$")
_WORD = re.compile(r"[A-Za-z_][\w.]*")

_FACT = re.compile(r"^r([^~]+)~(\d+)$")
_ITEM_LINE = re.compile(r'\[(\d+)\]="([^"]*)"')
_PROFESSION = re.compile(r"(\w+)=\{\{")
_RECIPE = re.compile(r'\{(\d+),"([^"]*)",(\d+),\d+,\d+,\d+,(\d+),[\d.]+,"[^"]*","([^"]*)"')
# The line of an English tooltip that says the reputation an item asks for.
_REQUIRES = re.compile(r"^Requires (.+) - (Neutral|Friendly|Honored|Revered|Exalted)$")
_STANDING_WORDS = {"Neutral": 3, "Friendly": 4, "Honored": 5, "Revered": 6, "Exalted": 7}


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


def read_capture(parsed: dict) -> tuple[dict[int, tuple[int, int]], dict[int, str], set[int]]:
    """({item: (faction, standing)}, {item: the name of a faction the table above lacks}, {the items read without
    one}) from what /ebiscapture read (capture.parse_saved): the line "Requires <faction> - <standing>" of the
    game's tooltip. The phrase is read in English only: another language gives nothing."""
    facts, others, plain = {}, {}, set()
    if parsed.get("locale") != "enUS":
        return facts, others, plain
    for item_id, (lines, _) in parsed["items"].items():
        found = next((match for match in map(_REQUIRES.match, lines) if match), None)
        if not found:
            plain.add(item_id)
        elif found.group(1) in _BY_NAME:
            facts[item_id] = (_BY_NAME[found.group(1)], _STANDING_WORDS[found.group(2)])
        else:
            others[item_id] = found.group(1)
    return facts, others, plain


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
    def __init__(self, db, store, facts: dict, spells: dict, names: dict, others: dict | None = None) -> None:
        self.db, self.store, self.facts, self.spells, self.names = db, store, facts, spells, names
        self.others = others or {}    # item -> a faction outside FACTIONS it asks for
        self.made = {}                # item -> the spells that make it
        for spell, recipe in spells.items():
            self.made.setdefault(recipe["makes"], []).append(spell)
        self.vendors = {}             # npc -> [name, uiMap, x, y]
        self.outside = {}             # a faction outside FACTIONS -> the items and enchants that need it
        self._quests, self._beyond = {}, {}

    def quest_gate(self, quest: int):
        """(faction, standing) the quest asks for, or None. A gate of a faction outside FACTIONS is kept apart
        (beyond)."""
        if quest not in self._quests:
            needed = self.store.table("Quest", quest, QUEST_MIN_REPUTATION)
            gate = None
            if needed and standing_of(needed[1]) > 3:
                if needed[0] in FACTIONS:
                    gate = (needed[0], standing_of(needed[1]))
                else:
                    self._beyond[quest] = needed[0]
            self._quests[quest] = gate
        return self._quests[quest]

    def beyond(self, quests, owner) -> None:
        """Notes the factions outside FACTIONS these quests ask for, for owner (an item or an enchant), when every
        one of them asks for a reputation: a quest that asks for none opens owner to everyone."""
        if not all(self.quest_gate(quest) or quest in self._beyond for quest in quests):
            return
        for quest in quests:
            if quest in self._beyond:
                self.outside.setdefault(str(self._beyond[quest]), set()).add(owner)

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
        """The wearer's requirement, with ForeverDB's vendor and price; else QuestieDB's vendor, whose price is
        not known; else the quest ForeverDB says rewards the piece."""
        faction, standing = self.facts[item_id]
        npc, price = self.vendor(item)
        record = {"side": "", "faction": faction, "standing": standing, "kind": WEAR}
        if npc:
            record.update(vendor=npc, price=price)
            return [record]
        npc = self.questie_vendor(item_id)
        if npc:
            record["vendor"] = npc
            return [record]
        quest = next((source for source in item["sources"] if source[0] == "q" and len(source) > 2), None)
        if quest and quest[2]:
            record["via"] = quest[2]
        return [record]

    def quest(self, item_id: int, item: dict) -> list[dict]:
        """One requirement per side the item's quests agree on. An item that also comes from anywhere else, or
        from a quest of that side that asks for nothing, needs no reputation."""
        quests = [source for source in item["sources"] if source[0] == "q" and source[1].isdigit()]
        if not quests or len(quests) != sum(1 for source in item["sources"] if source[0] != "r"):
            return []
        self.beyond([int(source[1]) for source in quests], item_id)
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

    def recipe_of(self, spell: int, owner) -> dict | None:
        """What a spell learned from a recipe sold against a reputation asks, or None: the faction, the standing,
        the recipe's item and name, the profession and its skill, and the recipe's vendor when QuestieDB has one.
        owner: the item or enchant the spell makes, noted when the recipe's faction is outside FACTIONS."""
        recipe = self.spells.get(spell)
        learn = recipe["learn"] if recipe else ""
        if learn.startswith("i") and int(learn[1:]) in self.others:
            self.outside.setdefault(self.others[int(learn[1:])], set()).add(owner)
        if not learn.startswith("i") or int(learn[1:]) not in self.facts:
            return None
        recipe_id = int(learn[1:])
        faction, standing = self.facts[recipe_id]
        record = {"faction": faction, "standing": standing, "kind": RECIPE, "via": self.names.get(recipe_id, ""),
                  "recipe": recipe_id, "profession": recipe["profession"], "skill": recipe["skill"]}
        npc = self.questie_vendor(recipe_id)
        if npc:
            record["vendor"] = npc
        return record

    def questie_vendor(self, item_id: int) -> int | None:
        """The first vendor QuestieDB names for an item (a recipe's: ForeverDB's data names the vendor and the
        zone but not the npc), kept with its place, or None."""
        for npc in sorted(set(self.store.ids("Item", item_id, questie.ITEM_VENDORS))):
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
            found = self.recipe_of(spell, item_id)
            if found:
                return [{"side": "", **found}]
        return []

    def item(self, item_id: int, item: dict) -> list[dict]:
        if item_id in self.facts:
            return self.wear(item_id, item)
        return self.quest(item_id, item) or self.recipe(item_id, item)

    def enchant(self, enchant: str, info: list) -> dict | None:
        number = int(enchant[1:])
        where = (info + ["", "", ""])[2]
        if enchant[0] == "s":
            record = self.recipe_of(number, enchant)
            if not record:
                return None
            if "scroll" in where:
                record["scroll"] = True
            return record
        if number in self.facts:
            faction, standing = self.facts[number]
            return {"faction": faction, "standing": standing, "kind": WEAR}
        quests = sorted(set(self.store.ids("Item", number, questie.ITEM_QUESTS)))
        self.beyond(quests, enchant)
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


def hidden_quests(folder) -> set[int] | None:
    """The quests the Questie addon in folder hides because the game does not have them (duplicates, quests never
    put in the game, quests of a later expansion), its conditions read as on Forever; None without that addon."""
    path = Path(folder) / BLACKLIST
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.index("local questsToBlacklist = {")
    end = text.index("\n    }\n", start)
    hidden = set()
    for line in text[start:end].splitlines()[1:]:
        found = _HIDDEN_ROW.match(line)
        if found and _hides(found.group(2)):
            hidden.add(int(found.group(1)))
    return hidden


def _hides(condition: str) -> bool:
    """A condition of Questie's list, read as on Forever. A word this reader does not know stops the import: the
    list changed, and a guess could hide a quest the game has."""
    def word(found):
        name = found.group(0)
        if name in _CONDITION_WORDS:
            return _CONDITION_WORDS[name]
        if name.startswith("Questie.Is"):     # Season of Discovery, Titan Reforged, the China region...: not Forever
            return "False"
        raise ValueError(f"{BLACKLIST.name}: a condition this reader does not know: {condition}")

    expression = _WORD.sub(word, condition.replace("~=", "!="))
    if not re.fullmatch(r"[\w\s().<>=!]*", expression):
        raise ValueError(f"{BLACKLIST.name}: a condition this reader does not know: {condition}")
    return bool(eval(expression, {"__builtins__": {}}, {}))   # only the words above, numbers and comparisons


def _gate(store, quest: int, field: int, faction: int):
    """The reputation with that faction a quest asks for at least (QUEST_MIN_REPUTATION) or is offered up to
    (QUEST_MAX_REPUTATION), counted from Neutral 0, or None."""
    gate = store.table("Quest", quest, field)
    return gate[1] if isinstance(gate, list) and len(gate) == 2 and gate[0] == faction else None


class _Links:
    """How QuestieDB ties quests: the ones a quest needs done first (preQuestGroup, preQuestSingle), the one it
    leads to (nextQuestInChain), the ones it excludes (exclusiveTo)."""

    def __init__(self, store) -> None:
        self.store = store
        self._before, self._earlier = {}, {}

    def before(self, quest: int) -> frozenset:
        if quest not in self._before:
            self._before[quest] = frozenset(self.store.ids("Quest", quest, QUEST_PRE_GROUP)
                                            + self.store.ids("Quest", quest, QUEST_PRE_SINGLE))
        return self._before[quest]

    def earlier(self, quest: int) -> frozenset:
        """Every quest before this one, however far back."""
        if quest not in self._earlier:
            seen, todo = set(), list(self.before(quest))
            while todo:
                other = todo.pop()
                if other not in seen:
                    seen.add(other)
                    todo.extend(self.before(other))
            self._earlier[quest] = frozenset(seen)
        return self._earlier[quest]

    def excludes(self, quest: int) -> set[int]:
        return set(self.store.ids("Quest", quest, QUEST_EXCLUSIVE))

    def chained(self, one: int, other: int) -> bool:
        """One leads to the other: a player does both."""
        return (one in self.earlier(other) or other in self.earlier(one)
                or self.store.row("Quest", one).get(QUEST_NEXT) == other
                or self.store.row("Quest", other).get(QUEST_NEXT) == one)

    def variants(self, one: int, other: int) -> bool:
        """The same quest twice: one excludes the other, or both need the same quests first and neither leads to
        the other (the same quest at another giver, or for other races)."""
        if other in self.excludes(one) or one in self.excludes(other):
            return True
        return self.before(one) == self.before(other) and not self.chained(one, other)


def usable(quest: dict) -> bool:
    """The quest helps on the way from Neutral to Exalted: it is not offered only below Neutral, nor only at
    Exalted."""
    return (quest["from"] or NEUTRAL) < EXALTED and (quest["until"] is None or quest["until"] > NEUTRAL)


def _merge(quests: list[dict], links: _Links) -> list[dict]:
    """The quests, the variants of one quest (same title, reward, standings, side and classes) as one: the first,
    whose "ids" are all of them. The steps of a chain that share a title stay apart."""
    groups = {}
    for quest in quests:
        key = (quest["title"], quest["amount"], quest["repeats"], quest["side"], quest["classes"], quest["from"],
               quest["until"])
        groups.setdefault(key, []).append(quest)
    kept = []
    for group in groups.values():
        merged = []
        for quest in group:
            same = next((one for one in merged if any(links.variants(quest["id"], other) for other in one["ids"])),
                        None)
            if same:
                same["ids"].append(quest["id"])
            else:
                merged.append({**quest, "ids": [quest["id"]]})
        kept.extend(merged)
    return kept


def _branches(kept: list[dict], links: _Links) -> None:
    """Sets "choice" to "<set>:<quest>" on the quests of a branch: set is the first of quests that exclude one
    another, quest the one of them the quest is or follows. A player takes one branch of a set."""
    owner = {number: quest["ids"][0] for quest in kept for number in quest["ids"]}
    near = {}
    for quest in kept:
        first = quest["ids"][0]
        for number in quest["ids"]:
            for other in links.excludes(number):
                # each excludes the other: the first quests of the branches, not the steps that follow one
                if other in owner and owner[other] != first and number in links.excludes(other):
                    near.setdefault(first, set()).add(owner[other])
                    near.setdefault(owner[other], set()).add(first)
    sets, placed = [], set()
    for first in sorted(near):
        if first in placed:
            continue
        found, todo = set(), [first]
        while todo:
            one = todo.pop()
            if one not in found:
                found.add(one)
                todo.extend(near.get(one, ()))
        placed |= found
        sets.append(found)
    for quest in kept:
        before = set(quest["ids"]).union(*(links.earlier(number) for number in quest["ids"]))
        for found in sets:
            hits = {owner[number] for number in before if number in owner and owner[number] in found}
            if len(hits) == 1:
                quest["choice"] = f"{min(found)}:{hits.pop()}"
                break


def once_total(quests: list[dict], side: str) -> int:
    """The most the quests done once give from Neutral to Exalted on a side: of a set of branches, the one that
    gives the most."""
    plain, branches = 0, {}
    for quest in quests:
        if quest["repeats"] or not usable(quest) or quest["side"] not in ("", side):
            continue
        if quest.get("choice"):
            group, member = quest["choice"].split(":")
            branches.setdefault(group, Counter())[member] += quest["amount"]
        else:
            plain += quest["amount"]
    return plain + sum(max(totals.values()) for totals in branches.values())


def earning(store, hidden=frozenset()) -> dict[int, dict]:
    """{faction: {"quests", "repeatable", "once": {"a", "h"}, "methods": [[title, amount, repeats, side, classes,
    from, until, choice], ...]}}: the quests QuestieDB says reward each faction, but the hidden ones.
    classes: the game's mask of the classes that may take the quest, 0 for all; from, until: the standings
    (3 Neutral to 7 Exalted) the quest is offered from and up to, when it says, else ""; choice: "<set>:<quest>"
    for a quest of one of the branches that exclude one another (_branches), else "".
    A quest offered only below LEVEL_CAP (one of a battleground's level brackets) is left out, and so is a row
    QuestieDB holds with neither level nor zone when another row has the same title, reward, side and classes:
    an unfinished copy of that quest.
    Every other quest is kept, the addon pages through them: the ones that help from Neutral to Exalted first (usable),
    the repeatable ones first among them, then the ones every class may take (a class's own quest is often a raid's
    token turned in), then the largest rewards. The variants of one quest are named and counted once (_merge).
    repeatable counts the repeatable quests that help; once is once_total for each side.
    A faction of BATTLEGROUNDS whose quests are mostly elsewhere stops the import: the table is wrong."""
    links = _Links(store)
    found = {number: [] for number in FACTIONS}
    for quest in store.numbers("Quest"):
        if quest in hidden:
            continue
        rewards = store.table("Quest", quest, QUEST_REPUTATION_REWARD)
        if not rewards:
            continue
        row = store.row("Quest", quest)
        for faction, amount in rewards:
            if faction in found and amount > 0 and row.get(questie.QUEST_NAME):
                capped = bool(row.get(QUEST_MAX_LEVEL)) and row[QUEST_MAX_LEVEL] < LEVEL_CAP
                low = _gate(store, quest, QUEST_MIN_REPUTATION, faction)
                high = _gate(store, quest, QUEST_MAX_REPUTATION, faction)
                found[faction].append({
                    "id": quest, "title": row[questie.QUEST_NAME], "amount": amount,
                    "repeats": bool((row.get(QUEST_SPECIAL_FLAGS) or 0) & REPEATABLE), "side": _quest_side(row),
                    "classes": row.get(QUEST_CLASSES) or 0,
                    "from": standing_of(low) if low is not None and standing_of(low) > NEUTRAL else None,
                    "until": standing_of(high + 1) if high is not None else None,   # offered while below that
                    "capped": capped, "zone": row.get(questie.QUEST_ZONE) or 0,
                    "stub": not row.get(questie.QUEST_REQUIRED_LEVEL) and not row.get(questie.QUEST_ZONE),
                })
    out = {}
    for faction, quests in found.items():
        full = {(quest["title"], quest["amount"], quest["side"], quest["classes"]) for quest in quests
                if not quest["stub"]}
        quests = [quest for quest in quests if not quest["capped"]
                  and not (quest["stub"] and (quest["title"], quest["amount"], quest["side"], quest["classes"]) in full)]
        kept = _merge(quests, links)
        _branches(kept, links)
        zones = Counter(quest["zone"] for quest in kept if quest["zone"])
        if faction in BATTLEGROUNDS and zones and zones.most_common(1)[0][0] != BATTLEGROUNDS[faction]:
            raise ValueError(f"faction {faction}: most of its quests are in area {zones.most_common(1)[0][0]}, not "
                             f"in its battleground {BATTLEGROUNDS[faction]} (reputations.BATTLEGROUNDS)")
        kept.sort(key=lambda quest: (not usable(quest), not quest["repeats"], quest["classes"] != 0,
                                     -quest["amount"], quest["title"]))
        out[faction] = {
            "quests": len(kept), "repeatable": sum(1 for quest in kept if quest["repeats"] and usable(quest)),
            "once": {side: once_total(kept, side) for side in "ah"},
            "methods": [[quest["title"], quest["amount"], int(quest["repeats"]), quest["side"], quest["classes"],
                         quest["from"] or "", quest["until"] or "", quest.get("choice", "")] for quest in kept],
        }
    return out


def questie_version(folder) -> str:
    """The Questie addon's version, as its Forever TOC says, or ""."""
    toc = Path(folder) / "Questie_Forever.toc" if folder else None
    if not toc or not toc.exists():
        return ""
    found = re.search(r"^## Version: (.+)$", toc.read_text(encoding="utf-8", errors="replace"), re.M)
    return found.group(1).strip() if found else ""


def first_vendor(item: dict) -> int | None:
    """The npc of an item's first vendor in ForeverDB's sources, or None."""
    for source in item.get("sources", ()):
        if source[0] in ("V", "v") and source[1].isdigit():
            return int(source[1])
    return None


def quartermasters(items: dict) -> dict[int, int]:
    """{npc: faction}: QUARTERMASTERS and the vendors of the pieces the wearer's reputation opens."""
    found = {}
    for records in items.values():
        for record in records:
            if record["kind"] == WEAR and record.get("vendor"):
                found.setdefault(record["vendor"], record["faction"])
    return {**found, **QUARTERMASTERS}


def collect(db, folder, store, shown=(), today: str | None = None, questie_folder=None, captured=None) -> dict:
    """What corrections/reputations.json holds. folder: where ForeverDB's Items.lua and Recipes.lua are;
    shown: the ids the lists hold; questie_folder: the Questie addon, whose list of the quests the game does not
    have is read (hidden_quests), or None to read none; captured: what /ebiscapture read (capture.parse_saved),
    whose tooltips give the requirement of a piece ForeverDB gives none (read_capture), or None.
    A capture that says otherwise than ForeverDB changes nothing: "differ" names those pieces."""
    folder = Path(folder)
    facts, others = read_item_facts((folder / "Items.lua").read_text(encoding="utf-8"))
    seen, plain, differ = {}, set(), {}
    if captured:
        game, strange, plain = read_capture(captured)
        seen = {item_id: fact for item_id, fact in game.items() if item_id not in facts}
        differ = {item_id: [list(facts[item_id]), list(fact)] for item_id, fact in game.items()
                  if item_id in facts and facts[item_id] != fact}
        others.update({item_id: name for item_id, name in strange.items() if item_id not in facts})
        facts = {**facts, **seen}
    listed = sorted({name for item_id, name in others.items() if item_id in shown})
    if listed:
        raise ValueError(f"listed items ask for factions reputations.FACTIONS lacks: {', '.join(listed)}")
    spells, names = read_recipes((folder / "Recipes.lua").read_text(encoding="utf-8"))
    reader = _Reader(db, store, facts, spells, names, others)
    hidden = (hidden_quests(questie_folder) or set()) if questie_folder else set()
    items = {}
    for item_id, item in db.items.items():
        found = reader.item(item_id, item)
        for record in found:
            if item_id in seen and record["kind"] == WEAR:
                record["read"] = "game"
        if found:
            items[item_id] = found
    sellers = quartermasters(items)
    plain = sorted(item_id for item_id in plain if item_id in db.items and item_id not in items
                   and first_vendor(db.items[item_id]) in sellers)
    enchants = {}
    for enchant, info in db.enchant_info.items():
        found = reader.enchant(enchant, info)
        if found:
            enchants[enchant] = found
    return {
        "foreverdb": db.meta["version"], "questiedb": store.version, "commit": store.commit,
        "date": today or datetime.date.today().isoformat(),
        "questie": questie_version(questie_folder), "hidden": len(hidden),
        "capture": f"{captured['game']} {captured['locale']} {captured['date']}" if captured else "",
        "factions": earning(store, hidden), "vendors": reader.vendors, "items": items, "enchants": enchants,
        "outside": {faction: sorted(owners, key=str) for faction, owners in reader.outside.items()},
        "plain": plain, "differ": differ,
    }


def load(path=FILE) -> dict:
    """The reading kept by save(), with its numbers back as numbers; empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    for name in ("factions", "vendors", "items", "differ"):
        data[name] = {int(number): value for number, value in data.get(name, {}).items()}
    data.setdefault("outside", {})
    data.setdefault("plain", [])
    return data


def save(reading: dict, path=FILE) -> None:
    """One record per line, in id order, so another reading shows as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def rows(records: dict, key=int) -> str:
        return ",\n".join(f'    "{name}": {json.dumps(records[name], ensure_ascii=False, sort_keys=True)}'
                          for name in sorted(records, key=key))

    head = {name: reading.get(name, "") for name in ("foreverdb", "questiedb", "commit", "questie", "hidden", "capture",
                                                     "date")}
    text = ("{\n" + f'  "about": {json.dumps(ABOUT)},\n'
            + "".join(f'  "{name}": {json.dumps(value)},\n' for name, value in head.items())
            + f'  "plain": {json.dumps(reading.get("plain", []))},\n'
            + '  "outside": {\n' + rows(reading.get("outside", {}), str) + "\n  },\n"
            + '  "differ": {\n' + rows(reading.get("differ", {})) + "\n  },\n"
            + '  "factions": {\n' + rows(reading.get("factions", {})) + "\n  },\n"
            + '  "vendors": {\n' + rows(reading.get("vendors", {})) + "\n  },\n"
            + '  "enchants": {\n' + rows(reading.get("enchants", {}), lambda enchant: int(enchant[1:])) + "\n  },\n"
            + '  "items": {\n' + rows(reading.get("items", {})) + "\n  }\n}\n")
    path.write_bytes(text.encode("utf-8"))


def check_capture(parsed: dict, facts: dict, reading: dict) -> dict[str, list]:
    """The game's tooltips against what the data says a piece asks of its wearer: ForeverDB's facts
    (read_item_facts) and what --import-reputations kept. {"same", "missing" (the game asks, the data has nothing
    yet), "extra" (the data asks, the game's tooltip does not), "differs", "outside" (a faction FACTIONS lacks)}:
    lists of (item, the data's (faction, standing) or None, the game's or its faction's name)."""
    known = dict(facts)
    for item_id, records in reading.get("items", {}).items():
        wear = next((record for record in records if record["kind"] == WEAR), None)
        if wear and item_id not in known:
            known[item_id] = (wear["faction"], wear["standing"])
    game, others, plain = read_capture(parsed)
    found = {"same": [], "missing": [], "extra": [], "differs": [], "outside": []}
    for item_id, fact in sorted(game.items()):
        data = known.get(item_id)
        kind = "missing" if data is None else "same" if tuple(data) == fact else "differs"
        found[kind].append((item_id, data, fact))
    found["outside"] = [(item_id, known.get(item_id), name) for item_id, name in sorted(others.items())]
    found["extra"] = [(item_id, known[item_id], None) for item_id in sorted(plain) if item_id in known]
    return found


def gaps(reading: dict, db, shown, enchants=()) -> tuple[dict[str, list], dict[int, list[int]]]:
    """What the build reports of the listed pieces and enchants: ({a faction outside FACTIONS, its id or the name
    ForeverDB writes: [what asks for it]}, {faction: [the listed pieces one of its quartermasters sells that
    nothing says the requirement of]}). A piece the game was read to ask for nothing is not one of them."""
    listed = set(shown) | set(enchants)
    outside = {faction: [owner for owner in owners if owner in listed]
               for faction, owners in reading.get("outside", {}).items()}
    sellers = quartermasters(reading.get("items", {}))
    plain = set(reading.get("plain", ()))
    unasked = {}
    for item_id in sorted(shown):
        npc = first_vendor(db.items.get(item_id) or {})
        if npc in sellers and item_id not in reading.get("items", {}) and item_id not in plain:
            unasked.setdefault(sellers[npc], []).append(item_id)
    return {faction: owners for faction, owners in outside.items() if owners}, unasked


def faction_vendors(reading: dict, shown) -> dict[int, int]:
    """{faction: the npc that sells the most listed pieces of that faction}."""
    counts = {}
    for item_id in shown:
        for record in reading.get("items", {}).get(item_id, ()):
            if record["kind"] == WEAR and record.get("vendor"):
                counts.setdefault(record["faction"], Counter())[record["vendor"]] += 1
    return {faction: sorted(sold.items(), key=lambda pair: (-pair[1], pair[0]))[0][0]
            for faction, sold in counts.items()}
