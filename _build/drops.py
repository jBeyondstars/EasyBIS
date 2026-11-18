"""Which creature drops an item in Forever, read in the loot counts other addons hold.

ForeverDB's data knows the drops of the level 60 dungeons from Classic's data only: the boss and the
rate are Classic's, and the addon says so. Two addons players share hold what Wowhead Forever recorded:
  - DungeonJournal (ForeverDungeonJournal/Data/DropRates.lua): per boss, how many times each item
    dropped and how many kills were recorded;
  - GearQuest Forever (GearQuestForever_<CLASS>/AuditTips.lua): the item's tooltip on Wowhead Forever,
    which names one creature and sometimes a chance.

`build.py --import-drops` reads both addons, installed next to Easy BIS, and keeps what they say of the
items of the data in corrections/drops.json. The build then lays it over the sources that are not
confirmed (corrections.confirm): nothing here is needed to build. Nothing of those addons is executed:
their Lua files are read with regular expressions.

A boss the journal gives Classic's numbers for, because Wowhead Forever recorded too few kills of it, is
left out: those numbers say nothing of Forever.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

JOURNAL = "ForeverDungeonJournal"
RATES = Path("Data") / "DropRates.lua"
GEARQUEST = "GearQuestForever"
TIPS = "AuditTips.lua"
MIN_KILLS = 25   # the journal's own limit: below it, it shows Classic's numbers

_DUNGEON = re.compile(r'^FDJ\.DROP_RATES\["(.+)"\] = \{')
_BOSS = re.compile(r'^\s+\["(.+?)"\] = \{\s*(?:--\s*(.*))?$')
_COUNTED = re.compile(r"(?:(\d+) kills|opened (\d+) times) on Wowhead Forever")   # a chest is opened
_ITEM = re.compile(r"^\s+\[(\d+)\] = ([\d.]+),\s*--.*\((\d+)/(\d+)\)\s*$")
_TIP = re.compile(r'^\s*\[(\d+)\]="(.*)",?\s*$')
_DROPPED_BY = re.compile(r"Dropped by: ([^\n]+)")
_CHANCE = re.compile(r"Drop Chance: ([\d.]+)%")
_VERSION = re.compile(r"^## Version: (.+?)\s*$", re.M)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _counted(note: str) -> bool:
    """Whether a boss's note says its numbers are Forever's, from enough kills."""
    found = _COUNTED.search(note or "")
    return bool(found) and "Classic" not in note and int(found[1] or found[2]) >= MIN_KILLS


def read_journal(text: str) -> dict[int, list[dict]]:
    """DropRates.lua as {item id: [{"boss", "dungeon", "drops", "kills", "percent"}]}, the likeliest boss first."""
    items, dungeon, boss = {}, None, None
    for line in text.splitlines():
        found = _DUNGEON.match(line)
        if found:
            dungeon, boss = found[1], None
            continue
        found = _BOSS.match(line)
        if found:
            boss = found[1] if dungeon and _counted(found[2]) else None
            continue
        found = _ITEM.match(line)
        if found and boss:
            items.setdefault(int(found[1]), []).append({
                "boss": boss, "dungeon": dungeon, "drops": int(found[3]), "kills": int(found[4]),
                "percent": float(found[2])})
    for entries in items.values():
        entries.sort(key=lambda entry: (-entry["drops"], entry["boss"]))
    return items


def read_tips(text: str) -> dict[int, dict]:
    """An AuditTips.lua as {item id: {"boss", "percent"}}, for the tooltips that name a creature."""
    tips = {}
    for line in text.splitlines():
        found = _TIP.match(line)
        if not found:
            continue
        tooltip = found[2].replace("\\n", "\n")
        boss = _DROPPED_BY.search(tooltip)
        if boss:
            chance = _CHANCE.search(tooltip)
            tips[int(found[1])] = {"boss": boss[1].strip(), "percent": float(chance[1]) if chance else 0.0}
    return tips


def find(addons) -> Path | None:
    """The DungeonJournal addon folder among the game's addons, or None."""
    folder = Path(addons) / JOURNAL
    return folder if (folder / RATES).exists() else None


def _version(folder: Path, name: str) -> str:
    found = _VERSION.search(_text(folder / f"{name}.toc"))
    return found[1] if found else ""


def collect(db, addons, today: str | None = None) -> dict:
    """What corrections/drops.json holds (corrections.save_drops): what the two addons say of the data's items."""
    addons = Path(addons)
    journal = read_journal(_text(addons / JOURNAL / RATES))
    if not journal:
        raise ValueError(f"{RATES.as_posix()} holds no drop count: not a DungeonJournal of the kind this reader knows")
    tips = {}
    for path in sorted(addons.glob(f"{GEARQUEST}_*/{TIPS}")):
        tips.update(read_tips(_text(path)))
    items = {}
    for item_id in sorted((set(journal) | set(tips)) & set(db.items)):
        record = {"name": db.items[item_id]["name"]}
        if item_id in journal:
            record["seen"] = journal[item_id]
        if item_id in tips:
            record["tooltip"] = tips[item_id]
        items[item_id] = record
    return {
        "journal": _version(addons / JOURNAL, JOURNAL), "gearquest": _version(addons / GEARQUEST, GEARQUEST),
        "date": today or datetime.date.today().isoformat(), "items": items,
    }
