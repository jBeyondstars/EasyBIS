"""Read ForeverDB's addon data files (https://foreverdb.net) as plain text.

Nothing in those files is executed: they are Lua sources, parsed here with
regular expressions. The formats are the ones ForeverDB's own GearFinder.lua
and Auto.lua decode. ForeverDB's data is GPL-3.0 with an attribution term:
"Data from ForeverDB.net (https://foreverdb.net)".

load() lays the stats read in the game over ForeverDB's where its data has a
hole (corrections.py), so the build and the tests rank the same database;
load(..., corrected=False) is ForeverDB's data as published.
"""
from __future__ import annotations

import re
from pathlib import Path

import corrections

DATA_FILES = ("GearFinder.lua", "Gear.lua", "GearSources.lua", "Enhance.lua", "Meta.lua")
HEADER_PREFIX = "-- Data: ForeverDB.net (https://foreverdb.net)"

_PAIR = re.compile(r'\[(\d+)\]="([^"]*)"')
_BLOCK = re.compile(r"^([A-Z]+)=\[==\[\n(.*?)\]==\]", re.S | re.M)


def b36(text: str) -> int:
    return int(text, 36)


def _stat_key(text: str):
    """Stat ids are numbers; "dps", "armor" and "wand" stay names."""
    return int(text) if text.isdigit() else text


def _table_line(text: str, name: str) -> str:
    """The single line that holds `ns.<name> = {...}`."""
    prefix = f"ns.{name} = "
    for line in text.split("\n"):
        if line.startswith(prefix):
            if '\\"' in line:
                raise ValueError(f"ns.{name} holds an escaped quote, which this reader does not handle")
            return line
    raise ValueError(f"ns.{name} not found")


class Database:
    """Everything the generator needs from ForeverDB's data files."""

    def __init__(self) -> None:
        self.header = ""        # the credit line every data file starts with
        self.meta = {}          # version, build, cap
        self.classes = {}       # token -> {"specs": {index: spec}, "pools": {pool: [(id, level)]}, "min": {profile: n}}
        self.gear = {}          # id -> {"inv", "req": required level, "stats": {stat: value}, "dps", "armor", "wand"}
        self.items = {}         # id -> {"name", "groups", "flags", "side", "twin", "limit", "sources"}
        self.extra = {}         # id -> {"hit": n, "set": {stat: value}}
        self.dual_wield = {}    # token -> level from which the class dual wields (99: never)
        self.instances = {}     # id -> fields of ForeverDB's gfInst
        self.vendors = {}       # npc id -> [name, uiMap, x, y]
        self.enchants = {}      # token -> {(spec, profile): {slot key: [(enchant id, level)]}}
        self.enchant_info = {}  # enchant id ("s<spell>" or "i<item>") -> [name, effect, where, label]
        self.corrected = None   # what corrections.apply changed (a corrections.Report), None for the published data


def load(data_dir, corrected: bool = True) -> Database:
    db = _read(data_dir)
    if corrected:
        corrections.apply(db, corrections.load())
    return db


def _read(data_dir) -> Database:
    data_dir = Path(data_dir)
    texts = {name: (data_dir / name).read_text(encoding="utf-8") for name in DATA_FILES}
    for name, text in texts.items():
        if not text.startswith(HEADER_PREFIX):
            raise ValueError(f"{name} does not start with ForeverDB's credit line")

    db = Database()
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
