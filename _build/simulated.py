"""The PvE lists ranked by simulation instead of by stat weights.

_build/simulate.py runs WoWSims Forever (https://github.com/wowsims/forever, MIT License) and writes what it
measured to corrections/simulated.json. This module only reads that file, so a build needs neither Go nor the
simulator. A spec the file does not name keeps ForeverDB's weights, and so does every PvP list.

An item's simulated score is the damage per second it adds to a reference set, against the same set with the
slot empty. An item the simulator did not measure is worth its weighted score times the slot's scale, and
never more than the lowest item that was measured. An item it cannot measure in full (a random bonus, an effect it
does not implement) may keep that estimate, but stays below the best items measured: a guess is never a best pick.

IN_USE says whether the build ranks on the file. It is off: the developer has not released these rankings.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "simulated.json"
IN_USE = False   # False: every list stays on ForeverDB's weights, whatever the file holds
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
class Reading:
    commit: str = ""            # the WoWSims Forever commit that measured them
    date: str = ""
    specs: dict = field(default_factory=dict)    # (class token, spec index) -> SpecRanking


def parse_spec(record: dict) -> SpecRanking:
    slots = {slot: SlotRanking(scores={int(item_id): value for item_id, value in data["scores"].items()},
                               scale=data["scale"], floor=data["floor"],
                               estimated=frozenset(data.get("estimated", ())))
             for slot, data in record["slots"].items()}
    return SpecRanking(slots=slots, record={key: value for key, value in record.items() if key != "slots"})


def load(path=FILE) -> Reading:
    """What the file holds; nothing without a file, and the lists stay on the weights."""
    path = Path(path)
    if not path.exists():
        return Reading()
    data = json.loads(path.read_text(encoding="utf-8"))
    specs = {}
    for key, record in data.get("specs", {}).items():
        token, spec = key.split()
        specs[token, int(spec)] = parse_spec(record)
    return Reading(commit=data.get("wowsims", ""), date=data.get("date", ""), specs=specs)


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
