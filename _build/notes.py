"""Notes on rankings that surprise: a few words, written by hand, that the addon shows by a mark on the item's row.

A list ranked by simulation puts Destiny before weapons with more damage per second, and Treant's Bane far under
what its stats promise. The reason is a fact the row does not show: a proc that is up half of the fight, a weapon
speed, an effect the simulator lacks. corrections/notes.json holds those facts, in English and French; each one is
checked against the game data or the simulator before it is written down.
"""

from __future__ import annotations

import json
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "notes.json"
LANGUAGES = {"en": "enUS", "fr": "frFR"}   # the file's key -> the game's locale code


def load(path=FILE) -> list[dict]:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))["notes"] if path.exists() else []


def check(db, notes: list[dict]) -> None:
    """Raise on a note the addon could not show as written."""
    for number, note in enumerate(notes, 1):
        where = f"notes.json, note {number}"
        if not note.get("items"):
            raise ValueError(f"{where}: no item")
        for key in LANGUAGES:
            text = note.get(key, "")
            if not text.strip() or "\n" in text or "|" in text:
                raise ValueError(f"{where}: the {key} text is empty or holds a line break or a |")
        for spec in note.get("specs", ()):
            cls, _, index = spec.partition(" ")
            if not index.isdigit() or int(index) not in db.classes.get(cls, {}).get("specs", {}):
                raise ValueError(f"{where}: no spec {spec!r}")
        unknown = set(note) - {"items", "specs", "simulated", *LANGUAGES}
        if unknown:
            raise ValueError(f"{where}: unknown field {sorted(unknown)}")


def shown(db, shown_ids: set[int], notes: list[dict] | None = None) -> list[dict]:
    """The notes with the items the lists show; a note none of whose items is shown is a mistake."""
    notes = load() if notes is None else notes
    check(db, notes)
    out = []
    for number, note in enumerate(notes, 1):
        items = sorted(item for item in note["items"] if item in shown_ids)
        if not items:
            raise ValueError(f"notes.json, note {number}: none of {note['items']} is in a list")
        out.append({**note, "items": items})
    return out
