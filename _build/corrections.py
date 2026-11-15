"""Stats read in the game, laid over ForeverDB's where its data has a hole.

ForeverDB's Gear.lua (data 2026-11-14) holds no healing or spell damage for
most caster weapons, and gives them the damage per second of a melee weapon:
1.34 to 1.5 times what the game shows. So a level 28 scepter that kept its
healing came out as the best healer main hand at level 60. The weapons'
tooltips are read in the game by the developer's capture tool
(_build/capture_addon, installed by `build.py --capture-tool`) and kept in
corrections/weapons.json by `build.py --import-capture` (capture.py).

A correction fills a hole, so it retires by itself once ForeverDB's data has
the value:
  - healing and spell damage are added to a weapon that has none in the data;
  - the damage per second is replaced when the data's is at least DPS_TOO_HIGH
    times the one read in the game, on a weapon the game shows spell power for.
Where the data has a value and the game showed another, the game's replaces
it when it was read at the data's game build or a later one: the game is the
reference for its own build. That goes for the healing and spell damage, and
for the damage per second of any weapon (the staves that carry the damage of
one school only are too high in the data as well). Read at an older build,
the capture may be out of date: the data's values are kept and the difference
is reported, which means the weapons are to be read again (/ebiscapture).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

FILE = Path(__file__).resolve().parent / "corrections" / "weapons.json"
ABOUT = ("Weapon stats read in the game with the EasyBIS_Capture tool (_build/capture_addon), laid over "
         "ForeverDB's data by _build/corrections.py. Written by `python build.py --import-capture`: do not edit.")

HEALING, SPELL_DAMAGE, SPELL_POWER = 41, 42, 45  # ForeverDB's stat ids; spell power is healing and damage alike
POWER = (HEALING, SPELL_DAMAGE, SPELL_POWER)
WEAPONS = frozenset((13, 17, 21, 22))  # inventory types: one-hand, two-hand, main hand, off hand
DPS_TOO_HIGH = 1.25
DPS_TOLERANCE = 0.06  # the data keeps one decimal


@dataclass
class Report:
    """What apply() did with the observations."""
    observed: int = 0                             # weapons read in the game
    filled: list = field(default_factory=list)    # ids given the healing and spell damage the data lacks
    dps: list = field(default_factory=list)       # ids given the damage per second the game shows
    agree: int = 0                                # the data already has what the game shows
    replaced: list = field(default_factory=list)  # ids whose healing and spell damage the game showed otherwise
    differ: list = field(default_factory=list)    # (id, (healing, damage) in the game, the same in the data): kept
    unknown: list = field(default_factory=list)   # ids the data has no weapon for
    builds: set = field(default_factory=set)      # the game builds the corrections in use were read at

    @property
    def changed(self) -> set:
        return set(self.filled) | set(self.replaced) | set(self.dps)


def load(path=FILE) -> dict[int, dict]:
    """{item id: {"name", "healing", "damage", "dps", "build", "date"}}, empty without a file."""
    path = Path(path)
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(item_id): record for item_id, record in data["items"].items()}


def save(observations: dict[int, dict], path=FILE) -> None:
    """One weapon per line, in id order, so a new capture reads as a short difference."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [f'    "{item_id}": {json.dumps(observations[item_id], ensure_ascii=False, sort_keys=True)}'
            for item_id in sorted(observations)]
    text = "{\n  " + f'"about": {json.dumps(ABOUT)},\n  "items": {{\n' + ",\n".join(rows) + "\n  }\n}\n"
    path.write_bytes(text.encode("utf-8"))


def power_stats(healing: float, damage: float) -> dict[int, int]:
    """Healing and spell damage as ForeverDB writes them: one spell power stat when they are equal."""
    if healing == damage:
        return {SPELL_POWER: int(healing)} if healing else {}
    return {stat: int(value) for stat, value in ((HEALING, healing), (SPELL_DAMAGE, damage)) if value}


def _build_number(build: str) -> tuple:
    """"1.60.1.70938" as numbers, to tell which of two game builds is the later one."""
    return tuple(int(part) for part in build.split(".") if part.isdigit())


def apply(db, observations: dict[int, dict]) -> Report:
    """Fill the holes of db.gear from the observations; the report is kept as db.corrected."""
    report = Report(observed=len(observations))
    data_build = _build_number(db.meta.get("build", ""))
    for item_id in sorted(observations):
        seen = observations[item_id]
        gear = db.gear.get(item_id)
        if gear is None or gear["inv"] not in WEAPONS:
            report.unknown.append(item_id)
            continue
        healing, damage, dps = seen.get("healing", 0), seen.get("damage", 0), seen.get("dps", 0)
        current = bool(seen.get("build")) and _build_number(seen["build"]) >= data_build
        stats = gear["stats"]
        if not (healing or damage):
            pass  # the game shows no spell power either: nothing to add
        elif not any(stats.get(stat) for stat in POWER):
            stats.update(power_stats(healing, damage))
            report.filled.append(item_id)
            report.builds.add(seen.get("build", ""))
        else:
            has = (stats.get(HEALING, 0) + stats.get(SPELL_POWER, 0), stats.get(SPELL_DAMAGE, 0) + stats.get(SPELL_POWER, 0))
            if abs(has[0] - healing) <= 1 and abs(has[1] - damage) <= 1:
                report.agree += 1
            elif current:
                for stat in POWER:
                    stats.pop(stat, None)
                stats.update(power_stats(healing, damage))
                report.replaced.append(item_id)
                report.builds.add(seen["build"])
            else:
                report.differ.append((item_id, (healing, damage), has))
        if not dps:
            continue
        if abs(gear["dps"] - dps) > DPS_TOLERANCE if current else (healing or damage) and gear["dps"] >= dps * DPS_TOO_HIGH:
            gear["dps"] = float(dps)
            report.dps.append(item_id)
            report.builds.add(seen.get("build", ""))
    report.builds.discard("")
    db.corrected = report
    return report
