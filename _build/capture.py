"""The developer's capture: which items to read in the game, and what the game said.

    python build.py --capture-tool      install the EasyBIS_Capture addon next to Easy BIS, with the list of
                                        items to read (capture_ids: every piece of ForeverDB's pools, and the
                                        level 50+ pieces it has stats for and leaves out of its lists)
    in the game: /ebiscapture, then /reload
    python build.py --check-capture     compare what the game shows with the data, stat by stat
    python build.py --import-capture    read the saved variable, keep the weapons' healing, spell damage and
                                        damage per second in corrections/weapons.json, what the consumables do
                                        in corrections/consumables.json (consumables.py), and build
    in the game: open a vendor's window, then /reload
    python build.py --import-prices     keep what the vendors of corrections/costs.json ask, as their windows
                                        showed it, and build

The saved variable (WTF/Account/<account>/SavedVariables/EasyBIS_Capture.lua)
is the developer's own; it is parsed as text and never run. The tooltip lines
are understood in English (enUS). Where they say nothing of healing or spell
damage, and in another language, the game's own stat table is used instead,
which may not hold everything a tooltip says.
"""
from __future__ import annotations

import re
import shutil
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import consumables
import corrections

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "capture_addon"
ADDON = "EasyBIS_Capture"
SAVED = ADDON + ".lua"
FORMAT = 1
VENDOR_FORMAT = 1
POOLS = ("mh", "2h", "oh")
UNLISTED_FROM = 50   # required level from which a piece ForeverDB left out of its lists is worth reading
# The order the groups of capture_ids are read in. The server never answers for an item it does not have,
# though the client's own table lists it, and the tool takes a long silence for a server that no longer answers
# and stops: on 2026-11-18 and 2026-11-19 every capture stopped at the first of the "unlisted" pieces numbered
# from 220794 (665 of the 666 left), which the server does not answer for. So the pieces of the lists come first,
# then the weapons, and last the groups such items are in: the other faction's versions, read to learn whether
# the server has them, and the pieces left out of the lists.
ORDER = ("consumables", "pool", "weapons", "twins", "unlisted")
GEAR_GROUPS = ORDER[1:]   # the groups that say which pieces of gear the game has (game_reading)
COMPLETE = 0.85   # the share of its list a capture has to hold for the rest to be what the game does not have

_STRING = r'"((?:[^"\\]|\\.)*)"'
_META = re.compile(rf'\["?meta"?\]\s*=\s*{_STRING}')
_VENDOR = re.compile(rf'\["?v(\d+)"?\]\s*=\s*{_STRING}')
_ESCAPE = re.compile(r"\\(\d{1,3}|.)", re.S)
_ESCAPED = {"n": "\n", "r": "\r", "t": "\t", "a": "\a", "b": "\b", "f": "\f", "v": "\v"}
_MARKUP = re.compile(r"\|c[0-9a-fA-F]{8}|\|r|\|T[^|]*\|t|\|A[^|]*\|a")
_USE = "#use "   # a line of the saved variable: the spell an item casts, its name and its description, by tabs

_N = r"(\d+(?:\.\d+)?)"
_BOTH = re.compile(rf"^Equip: Increases damage and healing done by magical spells and effects by up to {_N}\.$")
_SPLIT = re.compile(rf"^Equip: Increases healing done by up to {_N} and damage done by up to {_N} "
                    r"for all magical spells and effects\.$")
_HEALING = re.compile(rf"^Equip: Increases healing done by (?:magical )?spells and effects by up to {_N}\.$")
_DAMAGE = re.compile(rf"^Equip: Increases damage done by magical spells and effects by up to {_N}\.$")
_ONE_SCHOOL = re.compile(r"^Equip: Increases damage done (by \w+ spells and effects|to \w+ by magical spells "
                         r"and effects) by up to \d+\.$")   # one school, or against one kind of creature
_DPS = re.compile(rf"^\({_N} damage per second\)$")
_LOOKS_LIKE_POWER = re.compile(r"^(Equip: Increases .*(healing|damage) done.*\d|\+\d+ .*(Spell|Healing))")

# The game's stat table, for a client that is not in English: key -> (healing, spell damage) it adds to.
_STAT_KEYS = {
    "ITEM_MOD_SPELL_POWER_SHORT": (1, 1),
    "ITEM_MOD_SPELL_HEALING_DONE_SHORT": (1, 0),
    "ITEM_MOD_SPELL_DAMAGE_DONE_SHORT": (0, 1),
}
_DPS_KEY = "ITEM_MOD_DAMAGE_PER_SECOND_SHORT"
_ARMOR_KEY = "RESISTANCE0_NAME"

# The game's item stat table (C_Item.GetItemStats): key -> ForeverDB's stat id, which is the game's own item
# stat number. Hit, critical strike and the like are ratings in both. Checked on the weapons read on
# 2026-11-15, except the block, haste and ranged attack power keys, which no weapon has.
GAME_KEYS = {
    "ITEM_MOD_AGILITY_SHORT": 3, "ITEM_MOD_STRENGTH_SHORT": 4, "ITEM_MOD_INTELLECT_SHORT": 5,
    "ITEM_MOD_SPIRIT_SHORT": 6, "ITEM_MOD_STAMINA_SHORT": 7,
    "ITEM_MOD_DEFENSE_SKILL_RATING_SHORT": 12, "ITEM_MOD_DODGE_RATING_SHORT": 13, "ITEM_MOD_PARRY_RATING_SHORT": 14,
    "ITEM_MOD_BLOCK_RATING_SHORT": 15, "ITEM_MOD_HIT_RATING_SHORT": 31, "ITEM_MOD_CRIT_RATING_SHORT": 32,
    "ITEM_MOD_HASTE_RATING_SHORT": 36, "ITEM_MOD_EXPERTISE_RATING_SHORT": 37,
    "ITEM_MOD_ATTACK_POWER_SHORT": 38, "ITEM_MOD_RANGED_ATTACK_POWER_SHORT": 39,
    "ITEM_MOD_SPELL_HEALING_DONE_SHORT": 41, "ITEM_MOD_SPELL_DAMAGE_DONE_SHORT": 42,
    "ITEM_MOD_MANA_REGENERATION_SHORT": 43, "ITEM_MOD_SPELL_POWER_SHORT": 45, "ITEM_MOD_HEALTH_REGEN_SHORT": 46,
    "ITEM_MOD_SPELL_PENETRATION_SHORT": 47, "ITEM_MOD_BLOCK_VALUE_SHORT": 48,
    "ITEM_MOD_FIRE_RESISTANCE_SHORT": 51, "ITEM_MOD_FROST_RESISTANCE_SHORT": 52,
    "ITEM_MOD_SHADOW_RESISTANCE_SHORT": 54, "ITEM_MOD_NATURE_RESISTANCE_SHORT": 55,
    "ITEM_MOD_ARCANE_RESISTANCE_SHORT": 56,
    "ITEM_MOD_HOLY_DAMAGE_DONE_SHORT": 84, "ITEM_MOD_FIRE_DAMAGE_DONE_SHORT": 85,
    "ITEM_MOD_NATURE_DAMAGE_DONE_SHORT": 86, "ITEM_MOD_FROST_DAMAGE_DONE_SHORT": 87,
    "ITEM_MOD_SHADOW_DAMAGE_DONE_SHORT": 88, "ITEM_MOD_ARCANE_DAMAGE_DONE_SHORT": 89,
}
# keys the comparison does without: the resistances come under two keys, the others are named here once
_NOT_COMPARED = frozenset((_DPS_KEY, _ARMOR_KEY, "RESISTANCE2_NAME", "RESISTANCE3_NAME", "RESISTANCE4_NAME",
                           "RESISTANCE5_NAME", "RESISTANCE6_NAME"))
STAT_NAMES = {
    3: "agility", 4: "strength", 5: "intellect", 6: "spirit", 7: "stamina", 12: "defense", 13: "dodge", 14: "parry",
    15: "block", 31: "hit", 32: "critical strike", 36: "haste", 37: "expertise", 38: "attack power",
    39: "ranged attack power", 43: "mana per 5 sec", 46: "health per 5 sec", 47: "spell penetration",
    48: "block value", 51: "fire resistance", 52: "frost resistance", 54: "shadow resistance",
    55: "nature resistance", 56: "arcane resistance", 84: "holy damage", 85: "fire damage", 86: "nature damage",
    87: "frost damage", 88: "shadow damage", 89: "arcane damage",
}
_SLOT_WORDS = frozenset((
    "Head", "Neck", "Shoulder", "Back", "Chest", "Wrist", "Hands", "Waist", "Legs", "Feet", "Finger", "Trinket",
    "Main Hand", "Off Hand", "One-Hand", "Two-Hand", "Held In Off-hand", "Ranged", "Thrown", "Relic"))


def weapon_ids(db) -> list[int]:
    """The weapons of ForeverDB's pools: what a list can rank, so what is worth reading in the game."""
    ids = set()
    for data in db.classes.values():
        for pool in POOLS:
            for item_id, _ in data["pools"].get(pool, ()):
                gear = db.gear.get(item_id)
                if gear and gear["inv"] in corrections.WEAPONS and item_id in db.items:
                    ids.add(item_id)
    return sorted(ids)


def capture_ids(db) -> dict[str, list[int]]:
    """What the capture reads, by group.

    weapons   the weapons of ForeverDB's pools (corrections.py fills their holes)
    pool      every other piece of its pools: armor, jewelry, off hands, ranged weapons
    unlisted  the pieces it has stats for and leaves out of its lists, of required level UNLISTED_FROM to
              the cap: raid sets and raid drops mostly, read to learn what they are and who can wear them
    twins     the other faction's version of a pooled piece (the lists show it to that faction), when it is
              not pooled itself: read to learn whether the server has it at all
    consumables  what the Consumables tab ranks: the rule is in consumables.py
    """
    weapons = weapon_ids(db)
    pooled = set()
    for data in db.classes.values():
        for pool in data["pools"].values():
            pooled.update(item_id for item_id, _ in pool if item_id in db.gear and item_id in db.items)
    cap = db.meta["cap"]
    unlisted = [item_id for item_id, gear in db.gear.items()
                if item_id not in db.items and UNLISTED_FROM <= gear["req"] <= cap]
    twins = {db.items[item_id]["twin"] for item_id in pooled if db.items[item_id].get("twin")} - pooled
    return {"weapons": weapons, "pool": sorted(pooled - set(weapons)), "unlisted": sorted(unlisted),
            "twins": sorted(twins - set(unlisted)), "consumables": consumables.consumable_ids(db.consumables)}


def write_tool(db, addons_dir) -> tuple[Path, dict[str, int]]:
    """Install the capture addon in the game's AddOns folder; returns (its folder, items listed per group)."""
    target = Path(addons_dir) / ADDON
    target.mkdir(parents=True, exist_ok=True)
    for name in ("EasyBIS_Capture.toc", "Capture.lua"):
        shutil.copyfile(SOURCE / name, target / name)
    groups = capture_ids(db)
    assert set(groups) == set(ORDER), "a group of capture_ids has no place in ORDER"
    ids = list(dict.fromkeys(item_id for name in ORDER for item_id in groups[name]))
    rows = [" ".join(map(str, ids[start:start + 16])) for start in range(0, len(ids), 16)]
    text = "\n".join([
        f"-- Generated by Easy BIS's _build/build.py --capture-tool from ForeverDB's addon data {db.meta['version']}.",
        f"-- The {len(ids)} items whose tooltip /ebiscapture reads, in this order: "
        + ", ".join(f"{len(groups[name])} {name}" for name in ORDER) + " (capture.capture_ids).",
        "local _, ns = ...",
        "ns.ids = [==[",
        *rows,
        "]==]",
    ]) + "\n"
    (target / "Ids.lua").write_bytes(text.encode("utf-8"))
    return target, {name: len(group) for name, group in groups.items()}


def find_saved(game_dir) -> Path | None:
    """The capture's saved variable: over the accounts of this game folder, the newest one that holds a capture.

    The game writes an empty one for every account that logs in with the tool enabled.
    """
    found = sorted(Path(game_dir).glob(f"WTF/Account/*/SavedVariables/{SAVED}"),
                   key=lambda path: path.stat().st_mtime, reverse=True)
    for path in found:
        if _META.search(path.read_text(encoding="utf-8", errors="replace")):
            return path
    return found[0] if found else None


def _unescape(text: str) -> str:
    def replace(match):
        code = match.group(1)
        if code.isdigit():
            return chr(int(code))
        return _ESCAPED.get(code, code)
    return _ESCAPE.sub(replace, text)


def parse_saved(text: str) -> dict:
    """{"game": "version.build", "locale", "date", "items": {id: (lines, stats)}, "uses": {id: [(spell, name,
    description)]}, "missing": [ids], "absent": [ids], "sample": (asked, answered) or None, "log": text}.

    The file is the game's rendering of EasyBISCaptureDB (see capture_addon/Capture.lua): "missing" are
    the items not read, "absent" the ones of them the game's own item table does not list, "sample" what
    became of the few absent ones that were asked for all the same. "uses" is what the game says of the
    spell an item casts when used; a capture made before the tool asked for it has none.
    """
    meta = _META.search(text)
    if not meta:
        raise ValueError("no capture in this file: run /ebiscapture in the game, then /reload")
    fields = _unescape(meta.group(1)).split("|")
    if len(fields) != 5 or fields[0] != str(FORMAT):
        raise ValueError(f"unknown capture format {fields[0]!r}: install the tool again (build.py --capture-tool)")
    items, uses = {}, {}
    for match in re.finditer(rf"\[(\d+)\]\s*=\s*{_STRING}", text, re.S):
        lines = [_MARKUP.sub("", line).strip() for line in _unescape(match.group(2)).split("\n")]
        stats = {}
        if lines and lines[-1].startswith("#stats"):
            for key, value in re.findall(r"(\w+)=(-?[\d.]+)", lines.pop()):
                stats[key] = float(value)
        for line in lines:
            if line.startswith(_USE):
                spell, _, rest = line[len(_USE):].partition("\t")
                name, _, description = rest.partition("\t")
                uses.setdefault(int(match.group(1)), []).append((int(spell), name, description))
        items[int(match.group(1))] = ([line for line in lines if line and not line.startswith(_USE)], stats)
    def field_text(name):
        found = re.search(rf'\["?{name}"?\]\s*=\s*{_STRING}', text)
        return _unescape(found.group(1)) if found else ""

    sample = re.fullmatch(r"(\d+):(\d+)", field_text("sample"))
    return {
        "game": f"{fields[1]}.{fields[2]}", "locale": fields[3], "date": fields[4][:10], "items": items, "uses": uses,
        "missing": [int(number) for number in re.findall(r"\d+", field_text("missing"))],
        "absent": [int(number) for number in re.findall(r"\d+", field_text("absent"))],
        "sample": (int(sample.group(1)), int(sample.group(2))) if sample else None,
        "log": field_text("log"),
    }


def _number(value: float):
    return int(value) if float(value).is_integer() else round(value, 2)


def observe(lines: list[str], stats: dict, locale: str) -> tuple[dict, list[str]]:
    """({"name", "healing", "damage", "dps", "from"}, the power lines not understood) for one weapon.

    "from" says where the healing and spell damage were read: "tooltip", or "stats" for the game's stat table.
    """
    healing = damage = dps = 0.0
    unread = []
    english = locale.startswith("en")
    for line in lines:
        left = line.split("\t", 1)[0]
        speed_line = _DPS.match(left)
        if speed_line:
            dps = float(speed_line.group(1))
        if not english:
            continue
        both, split, heal, harm = _BOTH.match(left), _SPLIT.match(left), _HEALING.match(left), _DAMAGE.match(left)
        if both:
            healing += float(both.group(1))
            damage += float(both.group(1))
        elif split:
            healing += float(split.group(1))
            damage += float(split.group(2))
        elif heal:
            healing += float(heal.group(1))
        elif harm:
            damage += float(harm.group(1))
        elif _LOOKS_LIKE_POWER.match(left) and not _ONE_SCHOOL.match(left):
            unread.append(re.sub(r"\d+", "N", left))
    read_from = "tooltip"
    if not (healing or damage):
        for key, (to_healing, to_damage) in _STAT_KEYS.items():
            healing += stats.get(key, 0) * to_healing
            damage += stats.get(key, 0) * to_damage
        read_from = "stats" if healing or damage else read_from
    dps = stats.get(_DPS_KEY) or dps   # the tooltip rounds it to one decimal, the stat table does not
    return {"name": lines[0] if lines else "", "healing": _number(healing), "damage": _number(damage),
            "dps": _number(dps), "from": read_from}, unread


@dataclass
class Import:
    """What a capture held."""
    game: str = ""
    locale: str = ""
    read: int = 0                                   # tooltips in the file
    weapons: int = 0                                # of which weapons the data knows
    with_power: int = 0                             # of which the game shows healing or spell damage for
    from_stats: int = 0                             # of which read in the stat table, not on the tooltip
    missing: int = 0                                # weapons the game did not show
    other_names: list = field(default_factory=list)  # (id, name in the game, name in the data)
    unread: Counter = field(default_factory=Counter)  # power lines not understood, numbers as N
    observations: dict = field(default_factory=dict)
    reading: dict | None = None                     # what the capture says of the game's items (game_reading)
    listed: int = 0                                 # items of the capture's list
    shown: int = 0                                  # of which the capture holds


def game_reading(db, parsed: dict) -> dict | None:
    """What a capture says the game has, as corrections.save_game keeps it; None when it cannot say.

    Every item of the capture's list that it does not hold is taken as one the game does not have, so the
    capture has to be whole: COMPLETE of its list at least, in English (the class and unique lines of the
    tooltips are read). db is ForeverDB's data as published. The consumables are no part of this: it speaks
    of the gear.
    """
    groups = capture_ids(db)
    listed = {item_id for name in GEAR_GROUPS for item_id in groups[name]}
    read = listed & set(parsed["items"])
    if len(read) < COMPLETE * len(listed) or not parsed["locale"].startswith("en"):
        return None
    unlisted = {}
    for item_id in groups["unlisted"]:
        if item_id not in read:
            continue
        info = item_info(parsed["items"][item_id][0])
        record = {"name": info["name"]}
        record.update({key: info[key] for key in ("classes", "unique", "limit") if info[key]})
        unlisted[item_id] = record
    return {"build": parsed["game"], "date": parsed["date"], "listed": len(listed), "read": len(read),
            "absent": sorted(listed - read), "unlisted": unlisted}


def read_capture(db, text: str) -> Import:
    """The observations of a saved variable's text, for the weapons db knows, and its reading of the game."""
    parsed = parse_saved(text)
    result = Import(game=parsed["game"], locale=parsed["locale"], read=len(parsed["items"]),
                    missing=len(parsed["missing"]), reading=game_reading(db, parsed))
    groups = capture_ids(db)
    listed = {item_id for name in GEAR_GROUPS for item_id in groups[name]}
    result.listed, result.shown = len(listed), len(listed & set(parsed["items"]))
    for item_id, (lines, stats) in sorted(parsed["items"].items()):
        gear = db.gear.get(item_id)
        if gear is None or gear["inv"] not in corrections.WEAPONS:
            continue
        seen, unread = observe(lines, stats, parsed["locale"])
        result.unread.update(unread)
        result.weapons += 1
        if seen["healing"] or seen["damage"]:
            result.with_power += 1
            result.from_stats += seen["from"] == "stats"
        known = db.items.get(item_id)
        if known and parsed["locale"].startswith("en") and seen["name"] != known["name"]:
            result.other_names.append((item_id, seen["name"], known["name"]))
        seen.update(build=parsed["game"], date=parsed["date"])
        result.observations[item_id] = seen
    return result


def import_capture(db, saved_file, corrections_file=corrections.FILE, game_file=None) -> Import:
    """Merge a capture into the corrections file: a weapon read again replaces what was kept for it.

    A whole capture (game_reading) also replaces the file that says which items the game has, next to
    the corrections file unless game_file names it; a partial one leaves that file as it is.
    """
    result = read_capture(db, Path(saved_file).read_text(encoding="utf-8", errors="replace"))
    if not result.weapons:
        raise ValueError("the capture holds no weapon of the data: was /ebiscapture left to finish?")
    if not result.with_power:
        raise ValueError(f"no weapon of the capture shows healing or spell damage (game language: {result.locale}): "
                         "the tooltip lines were not understood, nothing was kept")
    kept = corrections.load(corrections_file)
    kept.update(result.observations)
    corrections.save(kept, corrections_file)
    if result.reading:
        corrections.save_game(result.reading, game_file or Path(corrections_file).with_name(corrections.GAME_FILE.name))
    return result


# -- what the vendors ask ----------------------------------------------------------------------------------

def find_vendors(game_dir) -> Path | None:
    """The newest saved variable of this game folder that holds a vendor's window."""
    found = sorted(Path(game_dir).glob(f"WTF/Account/*/SavedVariables/{SAVED}"),
                   key=lambda path: path.stat().st_mtime, reverse=True)
    for path in found:
        if _VENDOR.search(path.read_text(encoding="utf-8", errors="replace")):
            return path
    return None


def parse_vendors(text: str) -> dict:
    """{npc: {"name", "game": "version.build", "locale", "date", "items": {item id: {"name", "copper", "costs":
    [(kind, what, amount)]}}}}, what the vendors' windows showed (capture_addon/Capture.lua).

    A cost's kind is "i" for an item, "c" for a currency, both with their id as text, or "n" with the name.
    """
    vendors = {}
    for match in _VENDOR.finditer(text):
        head, *rows = _unescape(match.group(2)).split("\n")
        fields = head.split("|", 5)
        if len(fields) != 6 or fields[0] != str(VENDOR_FORMAT):
            raise ValueError(f"unknown vendor format {fields[0]!r}: install the tool again (build.py --capture-tool)")
        items = {}
        for row in rows:
            item_id, name, copper, paid = row.split("\t")
            costs = []
            for cost in filter(None, paid.split(";")):
                what, _, amount = cost[1:].rpartition(":")
                costs.append((cost[0], what, int(amount)))
            items[int(item_id)] = {"name": name, "copper": int(copper), "costs": costs}
        vendors[int(match.group(1))] = {"name": fields[5], "game": f"{fields[1]}.{fields[2]}", "locale": fields[3],
                                        "date": fields[4][:10], "items": items}
    return vendors


@dataclass
class PriceReading:
    """What the vendors' windows said of corrections/costs.json."""
    game: str = ""
    date: str = ""
    confirmed: list = field(default_factory=list)   # item ids the window asks the file's price for
    changed: list = field(default_factory=list)     # (item id, name, the file's price, the window's)
    added: list = field(default_factory=list)       # (item id, name, price) the file did not have
    other: list = field(default_factory=list)       # (item id, name, what the window asks): left as they were
    unseen: list = field(default_factory=list)      # (item id, name) of the file no window showed
    strangers: list = field(default_factory=list)   # (npc, name, rows) of vendors the file does not have
    unread: int = 0                                 # items of the file no window has confirmed so far

    @property
    def read(self) -> int:
        return len(self.confirmed) + len(self.changed) + len(self.added)


def _asked(row: dict, paid_in: int, currency: dict):
    """What the row asks in the vendor's currency; None when it asks for anything else as well or instead."""
    if row["copper"] or len(row["costs"]) != 1:
        return None
    kind, what, amount = row["costs"][0]
    expected = {"i": str(paid_in), "c": str(currency.get("currency", "")), "n": currency.get("name", "")}
    return amount if expected.get(kind) == what else None


def _asked_text(row: dict) -> str:
    costs = [f"{amount} of {kind}{what}" for kind, what, amount in row["costs"]]
    return ", ".join(costs + ([f"{row['copper']} copper"] if row["copper"] else []))


def read_prices(costs: dict, vendors: dict, names: dict | None = None) -> PriceReading:
    """Lay what the windows showed over `costs` (corrections.load_costs).

    An item read holds the game build and the date of the reading, which is what tells the addon its price
    is not the beta's any more. An item no window showed stays as it was: a window may show a class only
    what it can use. Names stay in English whatever the game's language: `names` gives the ones of an item
    the file did not have.
    """
    reading = PriceReading()
    for npc, shown in sorted(vendors.items()):
        vendor = costs.get("vendors", {}).get(npc)
        if vendor is None:
            reading.strangers.append((npc, shown["name"], len(shown["items"])))
            continue
        reading.game, reading.date = shown["game"], shown["date"]
        read = {"build": shown["game"], "date": shown["date"]}
        currency = costs["currencies"][vendor["paid_in"]]
        for item_id, row in sorted(shown["items"].items()):
            record = vendor["items"].get(item_id)
            name = record["name"] if record else (names or {}).get(item_id, row["name"])
            amount = _asked(row, vendor["paid_in"], currency)
            if amount is None:
                if record or row["costs"]:
                    reading.other.append((item_id, name, _asked_text(row)))
            elif record is None:
                vendor["items"][item_id] = {"name": name, "price": amount, **read}
                reading.added.append((item_id, name, amount))
            else:
                if record["price"] == amount:
                    reading.confirmed.append(item_id)
                else:
                    reading.changed.append((item_id, name, record["price"], amount))
                record.update(price=amount, **read)
        reading.unseen += [(item_id, record["name"]) for item_id, record in sorted(vendor["items"].items())
                           if item_id not in shown["items"]]
    if reading.read:
        costs["date"] = reading.date
    reading.unread = sum("build" not in record for vendor in costs.get("vendors", {}).values()
                         for record in vendor["items"].values())
    return reading


def import_prices(db, saved_file, costs_file=corrections.COSTS_FILE) -> PriceReading:
    """Keep in the costs file what the saved variable holds of its vendors."""
    vendors = parse_vendors(Path(saved_file).read_text(encoding="utf-8", errors="replace"))
    if not vendors:
        raise ValueError("no vendor's window in this file: open it in the game, then /reload")
    costs = corrections.load_costs(costs_file)
    reading = read_prices(costs, vendors, {item_id: item["name"] for item_id, item in db.items.items()})
    if reading.read:
        corrections.save_costs(costs, costs_file)
    return reading


# -- the game against the data ----------------------------------------------------------------------------

def item_info(lines: list[str]) -> dict:
    """{"name", "slot", "kind", "classes", "set", "req", "unique", "limit"} from a tooltip's lines (English).

    "limit" is the category of a "Unique-Equipped: <category> (n)" line, written as ForeverDB writes its
    limit codes: letters and digits only, sixteen at most ("Watcher's Ring" is WatchersRing).
    """
    info = {"name": lines[0] if lines else "", "slot": None, "kind": None, "classes": [], "set": None, "req": 0,
            "unique": False, "limit": None}
    for line in lines[1:]:
        left, _, right = line.partition("\t")
        level = re.match(r"^Requires Level (\d+)$", left)
        in_set = re.match(r"^(.+) \(\d+/\d+\)$", left)
        category = re.match(r"^Unique-Equipped: (.+?)(?: \(\d+\))?$", left)
        if left == "Unique":
            info["unique"] = True
        elif category:
            info["limit"] = re.sub(r"[^A-Za-z0-9]", "", category.group(1))[:16] or None
        if left in _SLOT_WORDS and info["slot"] is None:
            info["slot"], info["kind"] = left, right or None
        elif left.startswith("Classes: "):
            info["classes"] = [word.strip() for word in left[len("Classes: "):].split(",")]
        elif level:
            info["req"] = int(level.group(1))
        elif in_set and info["set"] is None:
            info["set"] = in_set.group(1)
    return info


@dataclass
class Check:
    """The game's stat tables against the data's, for the items of a capture."""
    game: str = ""
    locale: str = ""
    asked: dict = field(default_factory=dict)        # group of capture_ids -> items it holds
    read: dict = field(default_factory=dict)         # group -> of which the game showed
    compared: int = 0                                # items with a stat table on both sides
    families: dict = field(default_factory=dict)     # stat family -> Counter of same, missing, extra, differs
    examples: dict = field(default_factory=dict)     # (family, kind) -> [(id, name, in the game, in the data)]
    other_keys: Counter = field(default_factory=Counter)  # keys of the game's table the check does not know
    unlisted: dict = field(default_factory=dict)     # id -> item_info of an unlisted piece the game showed
    absent: dict = field(default_factory=dict)       # group -> [(id, name in the data)] the game's table lacks
    sample: tuple | None = None                      # (absent items asked for all the same, of which answered)

    def problems(self, family: str) -> int:
        counts = self.families.get(family, Counter())
        return counts["missing"] + counts["extra"] + counts["differs"]


def check_capture(db, text: str, examples: int = 6, groups: dict | None = None) -> Check:
    """Compare a saved variable's text with db, stat family by stat family.

    For each item and family: "same", "missing" (the game shows it, the data has none), "extra" (only the
    data has it) or "differs". Healing and spell damage are compared as totals, since the data writes
    them in two ways. Pass the database the build ranks (corrections applied) to see what is left to fix,
    and then the groups of the published data (capture_ids), which are what the capture read.
    """
    parsed = parse_saved(text)
    groups = groups or capture_ids(db)
    check = Check(game=parsed["game"], locale=parsed["locale"],
                  asked={name: len(group) for name, group in groups.items()},
                  read={name: sum(1 for item_id in group if item_id in parsed["items"])
                        for name, group in groups.items()})
    absent = set(parsed["absent"]) - set(parsed["items"])
    check.absent = {name: [(item_id, db.items.get(item_id, {}).get("name", "")) for item_id in group if item_id in absent]
                    for name, group in groups.items()}
    check.sample = parsed["sample"]
    unlisted = set(groups["unlisted"])
    for item_id, (lines, stats) in sorted(parsed["items"].items()):
        gear = db.gear.get(item_id)
        if gear is None:
            continue
        if item_id in unlisted:
            check.unlisted[item_id] = item_info(lines)
        check.other_keys.update(key for key in stats if key not in GAME_KEYS and key not in _NOT_COMPARED)
        if not stats and (gear["stats"] or gear["dps"] or gear["armor"]):
            continue   # the game gave no table for it: nothing to compare with
        check.compared += 1
        in_game = {}
        for key, stat in GAME_KEYS.items():
            if key in stats:
                in_game[stat] = in_game.get(stat, 0) + stats[key]
        in_data = gear["stats"]
        power = corrections.SPELL_POWER
        pairs = {
            "healing": (in_game.get(corrections.HEALING, 0) + in_game.get(power, 0),
                        in_data.get(corrections.HEALING, 0) + in_data.get(power, 0), 0.51),
            "spell damage": (in_game.get(corrections.SPELL_DAMAGE, 0) + in_game.get(power, 0),
                             in_data.get(corrections.SPELL_DAMAGE, 0) + in_data.get(power, 0), 0.51),
            "damage per second": (stats.get(_DPS_KEY, 0), gear["dps"], 0.06),
            "armor": (stats.get(_ARMOR_KEY, 0), gear["armor"], 1.0),
        }
        for stat, name in STAT_NAMES.items():
            pairs[name] = (in_game.get(stat, 0), in_data.get(stat, 0), 0.51)
        for family, (shown, held, tolerance) in pairs.items():
            if not shown and not held:
                continue
            if abs(shown - held) <= tolerance:
                kind = "same"
            elif not held:
                kind = "missing"
            elif not shown:
                kind = "extra"
            else:
                kind = "differs"
            check.families.setdefault(family, Counter())[kind] += 1
            if kind != "same":
                rows = check.examples.setdefault((family, kind), [])
                if len(rows) < examples:
                    rows.append((item_id, lines[0] if lines else "?", _number(shown), _number(held)))
    return check
