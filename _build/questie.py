"""Where an item comes from, read in QuestieDB, for the items ForeverDB's data gives no source.

ForeverDB's data lists many items with no source at all: the items a quest of a Classic raid rewards,
the head and leg arcanums, the enchants of Zul'Gurub, the pieces the game has that its lists leave out
(corrections.align). QuestieDB (https://github.com/Questie/QuestieDB), the database the Questie addon
reads, says which quest rewards an item, which creatures drop it, who sells it and what contains it.
Its content is under the GPL-3.0, as its LICENSE.md says and with the reservation it makes; Easy BIS
is under the same licence (NOTICE.txt).

`build.py --import-questie` reads the QuestieDB addon installed next to Easy BIS and keeps, in
corrections/sources.json, the sources of the items that have none in ForeverDB's data. The build then
lays them over the data (corrections.fill): nothing here is needed to build, and a source ForeverDB
comes to give replaces the one kept.

The addon's data is its TOC file: one line per value,
    ## X-<Item|Quest|Npc|Object>-<id>-<field>: <base64 of a CBOR value>
where field is S for the row of plain values ({field number: value}) or the number of a table field.
A long value is cut in parts: "~3~" in its place, and the parts on the lines <field>-1 to <field>-3.
Nothing of QuestieDB is executed: its Lua files (zone tables) are read with regular expressions.

What is kept is only what places an item for certain:
  - a quest, with the instance it belongs to when its zone is one;
  - a creature of an instance ForeverDB's data or phases.RAID_INSTANCES knows, as a boss of that
    instance; a boss with no place in QuestieDB (Sapphiron), as a raid boss; a creature of the open
    world, as a creature's drop;
  - a vendor, a chest, a container.
A creature or a quest of an instance neither ForeverDB nor phases.py knows is left out: nothing says
which content phase it belongs to.
"""
from __future__ import annotations

import base64
import datetime
import re
import struct
from pathlib import Path

import phases

ADDON = "QuestieDB"
TOC = "QuestieDB_Forever.toc"
LABEL = "t"            # the label of a source read here, next to ForeverDB's s, c, f and k
UNKNOWN_WHERE = "where it comes from isn't known yet"   # ForeverDB's sentence for an enchant with no source
BOSS = "boss"          # where a boss is when QuestieDB does not place it: some raid
PER_KIND = 2           # sources kept of each kind
PER_ITEM = 4           # sources kept in all

# QuestieDB's field numbers (src/meta/*.lua).
ITEM_NAME, ITEM_NPCS, ITEM_OBJECTS, ITEM_CONTAINERS, ITEM_QUESTS, ITEM_VENDORS = 1, 2, 3, 4, 6, 14
QUEST_NAME, QUEST_REQUIRED_LEVEL, QUEST_RACES, QUEST_ZONE = 1, 4, 6, 17
NPC_NAME, NPC_RANK, NPC_SPAWNS, NPC_ZONE, NPC_FRIENDLY = 1, 6, 7, 9, 13
OBJECT_NAME, OBJECT_ZONE = 1, 5
RANK_RARE_ELITE, RANK_BOSS, RANK_RARE = 2, 3, 4
ALLIANCE_RACES = 1 | 4 | 8 | 64 | 1024 | 2097152   # human, dwarf, night elf, gnome, draenei, worgen
HORDE_RACES = 2 | 16 | 32 | 128 | 256 | 512        # orc, undead, tauren, troll, goblin, blood elf

_ROW = re.compile(r"^## X-(Item|Quest|Npc|Object)-(\d+)-(S|\d+)(?:-(\d+))?: (.*)$")
_META = re.compile(r"^## (Version|X-BUILD-COMMIT|X-Flavor): (.*)$")
_CHUNKED = re.compile(r"^~(\d+)~$")


def decode(data: bytes, pos: int = 0):
    """One CBOR value and the position after it. Text and byte strings both come out as str."""
    head = data[pos]
    major, low = head >> 5, head & 31
    pos += 1
    if low < 24:
        value = low
    elif low in (24, 25, 26, 27):
        size = 1 << (low - 24)
        value = int.from_bytes(data[pos:pos + size], "big")
        pos += size
    else:
        raise ValueError(f"CBOR value of an unknown length ({low})")
    if major == 0:
        return value, pos
    if major == 1:
        return -1 - value, pos
    if major in (2, 3):
        return data[pos:pos + value].decode("utf-8", "replace"), pos + value
    if major == 4:
        items = []
        for _ in range(value):
            item, pos = decode(data, pos)
            items.append(item)
        return items, pos
    if major == 5:
        pairs = {}
        for _ in range(value):
            key, pos = decode(data, pos)
            pairs[key], pos = decode(data, pos)
        return pairs, pos
    if major == 7:
        if low in (25, 26, 27):
            size = 1 << (low - 24)
            return struct.unpack({2: ">e", 4: ">f", 8: ">d"}[size], value.to_bytes(size, "big"))[0], pos
        return {20: False, 21: True}.get(value), pos
    raise ValueError(f"CBOR value of an unknown kind ({major})")


class Store:
    """QuestieDB's rows, decoded when asked for."""

    def __init__(self, folder) -> None:
        self.folder = Path(folder)
        self.version = self.commit = ""
        self.flavor = "Forever"
        self._rows = {}     # (entity, id) -> {field: text}
        self._parts = {}    # (entity, id, field) -> {part number: text}
        with open(self.folder / TOC, encoding="utf-8", errors="replace") as lines:
            for line in lines:
                found = _ROW.match(line.rstrip("\r\n"))
                if found:
                    entity, number, name, part, text = found.groups()
                    if part:
                        self._parts.setdefault((entity, int(number), name), {})[int(part)] = text
                    else:
                        self._rows.setdefault((entity, int(number)), {})[name] = text
                    continue
                found = _META.match(line.rstrip("\r\n"))
                if found:
                    key, text = found.groups()
                    if key == "Version":
                        self.version = text.strip()
                    elif key == "X-BUILD-COMMIT":
                        self.commit = text.strip()
                    else:
                        self.flavor = text.strip()
        if not self._rows:
            raise ValueError(f"{TOC} holds no row: not a QuestieDB of the kind this reader knows")
        self.zones = Zones(self.folder, self.flavor)

    def has(self, entity: str, number: int) -> bool:
        return (entity, number) in self._rows

    def numbers(self, entity: str) -> list[int]:
        """Every id QuestieDB has a row for, in order."""
        return sorted(number for kind, number in self._rows if kind == entity)

    def _value(self, entity: str, number: int, name: str):
        text = self._rows.get((entity, number), {}).get(name)
        if text is None:
            return None
        chunked = _CHUNKED.match(text)
        if chunked:
            parts = self._parts.get((entity, number, name), {})
            text = "".join(parts[index] for index in range(1, int(chunked.group(1)) + 1))
        return decode(base64.b64decode(text))[0]

    def row(self, entity: str, number: int) -> dict:
        """The plain values of an entity: {field number: value}, empty when QuestieDB has no such entity.

        A row whose first fields are all set is stored as a list, the first field first."""
        row = self._value(entity, number, "S") or {}
        if isinstance(row, list):
            row = {index: value for index, value in enumerate(row, 1) if value is not None}
        return row

    def table(self, entity: str, number: int, field: int):
        """A table field (a list of ids, the spawns), or None."""
        return self._value(entity, number, str(field))

    def ids(self, entity: str, number: int, field: int) -> list[int]:
        """A field that lists ids, flattened: quests list their givers as [[npc, ...], [object, ...]]."""
        out = []

        def walk(value):
            if isinstance(value, int) and not isinstance(value, bool):
                out.append(value)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(self.table(entity, number, field))
        return out


class Zones:
    """QuestieDB's zone tables: which instance an area is, and the map the game shows for an area."""

    def __init__(self, folder: Path, flavor: str) -> None:
        zones = folder / "support" / flavor / "Zones"
        symbols = dict(re.findall(r"^\s*([A-Z][A-Z0-9_]*) = (\d+),", _text(folder / "src/corrections/enum/zones.lua"),
                                  re.M))
        self.names = {}        # area -> the name of the instance it is, or is a part of
        for area, name, others in re.findall(r'^\s*\[(\d+)\] = \{"([^"]+)",(nil|\{[\d, ]*\})',
                                             _text(zones / "dungeons.lua"), re.M):
            self.names[int(area)] = name
            for other in re.findall(r"\d+", others):
                self.names.setdefault(int(other), name)
        self.by_name = {}      # instance name -> the game's instance id (the lowest, when a later version reuses it)
        for instance, symbol in re.findall(r"\[(\d+)\] = ZoneDB\.zoneIDs\.([A-Z0-9_]+)",
                                           _text(zones / "instanceIdToAreaId.lua")):
            name = self.names.get(int(symbols.get(symbol, -1)))
            if name and int(instance) < self.by_name.get(name, 1 << 30):
                self.by_name[name] = int(instance)
        self.ui_maps = {}      # area -> uiMap; the overrides come first in the file and win
        for area, ui_map in re.findall(r"^\s*\[(\d+)\] = (\d+),", _text(zones / "areaIdToUiMapId.lua"), re.M):
            self.ui_maps.setdefault(int(area), int(ui_map))

    def instance(self, area, known: dict[str, int]) -> tuple[int | None, bool]:
        """(the instance an area is, whether the area is an instance at all). known: ForeverDB's instances by
        name, which come first: QuestieDB names the ones Forever adds and has no id for them."""
        name = self.names.get(area)
        if name is None:
            return None, False
        return known.get(name, self.by_name.get(name)), True


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def find(addons) -> Path | None:
    """The QuestieDB addon folder among the game's addons, or None."""
    folder = Path(addons) / ADDON
    return folder if (folder / TOC).exists() else None


def wanted(db, game: dict) -> tuple[list[int], list[str]]:
    """The items and the enchants ForeverDB's data (as published) gives no source: (item ids, enchant ids).

    The pieces the game showed that ForeverDB does not list (corrections.align) are among them; the items
    the game does not have are not, whatever QuestieDB says of them: it holds numbers of another version
    of the game too.
    """
    items = {item_id for item_id, item in db.items.items() if not item["sources"]}
    items.update(item_id for item_id in game.get("unlisted", {}) if item_id not in db.items)
    items.difference_update(game.get("absent", ()))
    enchants = [enchant for enchant, info in db.enchant_info.items()
                if enchant.startswith("i") and (info + ["", "", ""])[2] in ("", UNKNOWN_WHERE)]
    return sorted(items), sorted(enchants, key=lambda enchant: int(enchant[1:]))


class _Reader:
    """Turns QuestieDB's rows into sources as ForeverDB writes them (luaout.items_file's legend)."""

    def __init__(self, db, store: Store) -> None:
        self.store = store
        self.kinds = {number: (fields + ["", ""])[1] for number, fields in db.instances.items()}
        self.known = {fields[0]: number for number, fields in db.instances.items()}
        self.named = {}   # instances the sources name that ForeverDB's table lacks: id -> name

    def place(self, area) -> tuple[int | None, bool]:
        """(the instance to say, whether to keep the source). An instance nothing knows is not kept."""
        instance, is_instance = self.store.zones.instance(area, self.known)
        if not is_instance:
            return None, True
        if instance is None or (instance not in self.kinds and instance not in phases.RAID_INSTANCES):
            return None, False
        if instance not in self.kinds:
            self.named[instance] = self.store.zones.names[area]
        return instance, True

    def is_raid(self, instance: int) -> bool:
        return self.kinds.get(instance) == "raid" or instance in phases.RAID_INSTANCES

    def instance_name(self, instance) -> str:
        if instance in self.named:
            return self.named[instance]
        return next((name for name, number in self.known.items() if number == instance), "")

    def quests(self, item_id: int) -> list[tuple[list[str], object]]:
        found = []
        for quest in sorted(set(self.store.ids("Item", item_id, ITEM_QUESTS))):
            row = self.store.row("Quest", quest)
            if not row.get(QUEST_NAME):
                continue
            zone = row.get(QUEST_ZONE) or 0
            instance, keep = self.place(zone) if zone > 0 else (None, True)
            if not keep:
                continue
            races = row.get(QUEST_RACES) or 0
            side = "a" if races and not races & HORDE_RACES else "h" if races and not races & ALLIANCE_RACES else ""
            source = ["q", str(quest), row[QUEST_NAME], str(row.get(QUEST_REQUIRED_LEVEL) or 0), side, LABEL]
            found.append((source, instance))
        found.sort(key=lambda pair: (pair[0][4] != "", pair[0][4]))   # the quest of both factions first
        return found

    def creatures(self, item_id: int) -> list[tuple[list[str], object]]:
        bosses, rares, others = [], [], []
        for npc in sorted(set(self.store.ids("Item", item_id, ITEM_NPCS))):
            row = self.store.row("Npc", npc)
            name, rank = row.get(NPC_NAME), row.get(NPC_RANK) or 0
            if not name or row.get(NPC_FRIENDLY):
                continue   # a city guard is in QuestieDB's drop tables too: not where a player looks
            spawns = self.store.table("Npc", npc, NPC_SPAWNS)
            # the zone it is in; a creature with spawns and no zone is where its first spawn is
            zone = row.get(NPC_ZONE) or (min(spawns) if isinstance(spawns, dict) and spawns else 0)
            instance, keep = self.place(zone) if zone > 0 else (None, True)
            if not keep:
                continue
            if instance is not None:
                raid = "1" if self.is_raid(instance) else "0"
                bosses.append(((-rank, npc), (["d", str(instance), name, "", raid, LABEL], None)))
            elif not zone:
                if rank == RANK_BOSS:   # a boss QuestieDB does not place: one of a raid
                    bosses.append(((-rank, npc), (["m", str(npc), name, "", LABEL], BOSS)))
                # any other creature with no place: nothing says where it is
            elif rank in (RANK_RARE, RANK_RARE_ELITE):
                rares.append((npc, (["R", str(npc), name, "", LABEL], None)))
            else:
                others.append((npc, (["m", str(npc), name, "", LABEL], BOSS if rank == RANK_BOSS else None)))
        return [pair for _, pair in sorted(bosses)] + [pair for _, pair in rares] + [pair for _, pair in others]

    def vendors(self, item_id: int) -> list[tuple[list[str], object]]:
        found = []
        for npc in sorted(set(self.store.ids("Item", item_id, ITEM_VENDORS))):
            row = self.store.row("Npc", npc)
            if not row.get(NPC_NAME):
                continue
            zone = row.get(NPC_ZONE) or 0
            spots = (self.store.table("Npc", npc, NPC_SPAWNS) or {}).get(zone) or []
            x, y = (spots[0] + [0, 0])[:2] if spots and isinstance(spots[0], list) else (0, 0)
            ui_map = self.store.zones.ui_maps.get(zone, 0)
            friendly = row.get(NPC_FRIENDLY) or ""
            side = "a" if friendly == "A" else "h" if friendly == "H" else ""
            where = [str(ui_map), f"{x:g}", f"{y:g}"] if ui_map and x > 0 and y > 0 else [str(ui_map or ""), "", ""]
            found.append((["v", str(npc), row[NPC_NAME], *where, "", side, LABEL], None))
        return found

    def chests(self, item_id: int) -> list[tuple[list[str], object]]:
        found = []
        for number in sorted(set(self.store.ids("Item", item_id, ITEM_OBJECTS))):
            row = self.store.row("Object", number)
            if not row.get(OBJECT_NAME):
                continue
            zone = row.get(OBJECT_ZONE) or 0
            instance, keep = self.place(zone) if zone > 0 else (None, True)
            if keep and not any(source[1] == row[OBJECT_NAME] for source, _ in found):   # one chest per name
                found.append((["o", row[OBJECT_NAME], "", LABEL], instance))
        return found

    def containers(self, item_id: int) -> list[tuple[list[str], object]]:
        found = []
        for number in sorted(set(self.store.ids("Item", item_id, ITEM_CONTAINERS))):
            name = self.store.row("Item", number).get(ITEM_NAME)
            if name:
                found.append((["x", str(number), name, LABEL], None))
        return found

    def sources(self, item_id: int) -> list[tuple[list[str], object]]:
        """[(source, where)], the likeliest first. where: the instance a quest, a creature or a chest belongs
        to when the source does not say it, BOSS for a raid boss with no place, else None."""
        found = []
        for kind in (self.quests, self.creatures, self.vendors, self.chests, self.containers):
            found += kind(item_id)[:PER_KIND]
        return [(source, where) for source, where in found[:PER_ITEM] if _writable(source)]

    def sentence(self, source: list[str], where) -> str:
        """An enchant's source in a sentence, as ForeverDB's data holds the ones it knows (Enchants.lua reads it)."""
        kind = source[0]
        if kind == "q":
            place = self.instance_name(where)
            return f"Quest: {source[2]}" + (f" ({place})" if place else "")
        if kind == "d":
            place = self.instance_name(int(source[1]))
            return ("Raid drop: " if source[4] == "1" else "Dungeon drop: ") + source[2] + (f" ({place})" if place else "")
        if kind == "m":
            return ("Raid drop: " if where == BOSS else "Drop: ") + source[2]
        if kind == "R":
            return f"Rare drop: {source[2]}"
        if kind == "v":
            return f"Vendor: {source[2]}"
        if kind == "o":
            return f"Chest: {source[1]}"
        return f"Container: {source[2]}"


def _writable(source: list[str]) -> bool:
    """Whether the data files can hold the source: their separators are | ^ ~ and the line break."""
    return not any(mark in text for text in source for mark in "|^~\n\t")


def collect(db, game: dict, store: Store, today: str | None = None) -> dict:
    """What corrections/sources.json holds (corrections.save_sources), from ForeverDB's data as published,
    the reading of the game and QuestieDB."""
    reader = _Reader(db, store)
    item_ids, enchant_ids = wanted(db, game)
    items, enchants = {}, {}
    for item_id in item_ids:
        found = reader.sources(item_id)
        if found:
            record = {"name": store.row("Item", item_id).get(ITEM_NAME, ""),
                      "sources": [source for source, _ in found]}
            if any(where is not None for _, where in found):
                record["at"] = [where for _, where in found]
            items[item_id] = record
    for enchant in enchant_ids:
        found = reader.sources(int(enchant[1:]))
        if found:
            source, where = found[0]
            record = {"where": reader.sentence(source, where)}
            at = int(source[1]) if source[0] == "d" else where
            if at is not None:
                record["at"] = at
            enchants[enchant] = record
    return {
        "questiedb": store.version, "commit": store.commit,
        "date": today or datetime.date.today().isoformat(),
        "asked": {"items": len(item_ids), "enchants": len(enchant_ids)},
        "instances": {number: reader.named[number] for number in sorted(reader.named)},
        "items": items, "enchants": enchants,
    }
