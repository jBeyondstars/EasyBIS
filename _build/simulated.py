"""The PvE lists ranked by simulation instead of by stat weights.

_build/simulate.py runs WoWSims Forever (https://github.com/wowsims/forever, MIT License) and writes what it
measured to corrections/simulated.json. This module only reads that file, so a build needs neither Go nor the
simulator. A spec the file does not name keeps ForeverDB's weights, and so does every PvP list.

An item's simulated score is the damage per second it adds to a reference set, against the same set with the
slot empty. An item the simulator did not measure is worth its weighted score times the slot's scale, and
never more than the lowest item that was measured. An item it cannot measure in full (a random bonus, an effect it
does not implement, a proc whose rate is assumed) stays below the best items measured: a guess is never a best pick.

Until every damage spec is measured, corrections/placed.json puts a few items with an effect (Hand of Justice...)
in the PvE lists of the specs the simulator has not measured yet: where a close spec's measure ranks them, as
alternatives, right after the item the spec's own list has at the rank before (place). Such an item has no score of its own: it keeps its neighbour's for the order and is flagged
e, the addon shows no figure for it and never makes it a best pick. A spec's placements stop counting once the
simulator has measured it.

IN_USE says whether the build ranks on the files.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "simulated.json"
PLACED = Path(__file__).resolve().parent / "corrections" / "placed.json"
IN_USE = True   # False: every list stays on ForeverDB's weights, whatever the files hold
STEP = 0.5   # the DPS a score is rounded to: closer than this, two items are equals
ABOUT = ("What WoWSims Forever (https://github.com/wowsims/forever, MIT License) measured for the PvE lists of these "
         "specs: the DPS each item adds to a reference set. Written by `python _build/simulate.py`: do not edit.")


def rounded(value: float) -> float:
    """A score as the lists keep it: never below zero, in steps of STEP."""
    return max(0.0, round(value / STEP) * STEP)


@dataclass(frozen=True)
class SlotRanking:
    scores: dict                # item id of the ladder -> its score
    scale: float = 0.0          # DPS per point of weighted score, the median of the items measured
    floor: float = 0.0          # the lowest score measured, the most an item left unmeasured can get
    estimated: frozenset = frozenset()   # scores of the file that are not a full measure: an item the simulator
    #                                      cannot wear (a random bonus) or whose effect it does not implement

    def value(self, item_id: int, weight: float) -> float:
        """The score of an item whose weighted score is `weight`."""
        known = self.scores.get(item_id)
        if known is not None:
            return known
        return rounded(min(weight * self.scale, self.floor))


@dataclass(frozen=True)
class SpecRanking:
    slots: dict                 # slot -> SlotRanking
    record: dict = field(default_factory=dict)   # the rest of what the file says of the spec


@dataclass(frozen=True)
class Placement:
    item_id: int
    rank: int                   # its place in the slot's whole ladder, 1 for the first
    origin: dict = field(default_factory=dict)   # the close specs it is read from -> the rank it has there
    after: int | None = None    # the item it follows: the one at the rank before when the file was made


@dataclass(frozen=True)
class Reading:
    commit: str = ""            # the WoWSims Forever commit that measured them
    date: str = ""
    specs: dict = field(default_factory=dict)    # (class token, spec index) -> SpecRanking
    placed: dict = field(default_factory=dict)   # (class token, spec index) -> {slot: [Placement]}, placed.json

    @property
    def commits(self) -> str:
        """The commits that measured the specs, the file's own last: one, or several while the specs are measured
        again a few at a time. A spec's record names its own ("wowsims"); one that names none has the file's."""
        found = {ranking.record.get("wowsims") or self.commit for ranking in self.specs.values()}
        return " and ".join(sorted(found, key=lambda commit: (commit == self.commit, commit))) or self.commit


def parse_spec(record: dict) -> SpecRanking:
    slots = {slot: SlotRanking(scores={int(item_id): value for item_id, value in data["scores"].items()},
                               scale=data["scale"], floor=data["floor"],
                               estimated=frozenset(data.get("estimated", ())))
             for slot, data in record["slots"].items()}
    return SpecRanking(slots=slots, record={key: value for key, value in record.items() if key != "slots"})


def load_placed(path=PLACED) -> dict:
    """{(class token, spec index): {slot: [Placement]}} as placed.json holds them; nothing without the file."""
    path = Path(path)
    if not path.exists():
        return {}
    placed = {}
    for key, record in json.loads(path.read_text(encoding="utf-8")).get("specs", {}).items():
        token, spec = key.split()
        placed[token, int(spec)] = {
            slot: [Placement(item_id=entry["item"], rank=entry["rank"], origin=entry.get("from", {}),
                             after=entry.get("after"))
                   for entry in entries]
            for slot, entries in record["slots"].items()}
    return placed


def load(path=FILE, placed_path=PLACED) -> Reading:
    """What the files hold; nothing without them, and the lists stay on the weights."""
    path = Path(path)
    placed = load_placed(placed_path)
    if not path.exists():
        return Reading(placed=placed)
    data = json.loads(path.read_text(encoding="utf-8"))
    specs = {}
    for key, record in data.get("specs", {}).items():
        token, spec = key.split()
        specs[token, int(spec)] = parse_spec(record)
    return Reading(commit=data.get("wowsims", ""), date=data.get("date", ""), specs=specs, placed=placed)


def save(commit: str, date: str, records: dict, path=FILE) -> None:
    """records: {"WARRIOR 2": record}. One item per line, in id order, so that another run reads as a short difference."""
    specs = {key: records[key] for key in sorted(records)}
    for record in specs.values():
        for slot in record["slots"].values():
            slot["scores"] = {str(item_id): slot["scores"][item_id]
                              for item_id in sorted(slot["scores"], key=int)}
    text = json.dumps({"about": ABOUT, "wowsims": commit, "date": date, "specs": specs}, indent=1, ensure_ascii=False)
    Path(path).write_bytes((text + "\n").encode("utf-8"))


def ranking(db, cls: str, spec: int, mode: str, slot: str) -> SlotRanking | None:
    """How the simulator ranks that list; None when the list stays on the weights."""
    reading = getattr(db, "simulated", None)
    if not reading or mode != "pve":
        return None
    ranked = reading.specs.get((cls, spec))
    return ranked.slots.get(slot) if ranked else None


def placements(db, cls: str, spec: int, mode: str, slot: str) -> list:
    """The items placed.json puts in that list: none once the simulator has measured the spec, none in PvP."""
    reading = getattr(db, "simulated", None)
    if not reading or mode != "pve" or (cls, spec) in reading.specs:
        return []
    return reading.placed.get((cls, spec), {}).get(slot, [])


def place(entries: list, placed: list) -> list:
    """The ladder (best first) with each placed item moved up to just after the item it follows, or to its rank
    when the ladder lacks that one: an item that comes or goes above it does not move it among the others. An item
    already that high, or that the ladder does not have, stays as it is. A placed item takes the score of the one
    above it, so the ladder stays in order, and is flagged: that score is not its own."""
    entries = list(entries)
    find = lambda item_id: next((i for i, entry in enumerate(entries) if entry.item_id == item_id), None)
    for placement in sorted(placed, key=lambda p: p.rank):
        index = find(placement.item_id)
        if index is None:
            continue
        anchor = find(placement.after) if placement.after is not None else None
        at = anchor + 1 if anchor is not None else max(1, placement.rank - 1)   # never first: no best pick
        if index <= at:
            continue
        entry = entries.pop(index)
        entries.insert(at, replace(entry, score=entries[at - 1].score, placed=True))
    return entries
