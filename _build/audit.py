"""Look for rows of the lists that the data probably has wrong.

ForeverDB's data is read from the game's files, and a part of an item can be
missing there (see corrections.py). A list built on such a hole still looks
like a list, so the build checks every row the addon can show, for both
factions and every content phase, with the default options:

  low level       the item's required level is far under the level cap
  no spell power  a caster's or healer's weapon that has none of the healing
                  or spell damage the spec's weights value, and that was not
                  read in the game (corrections.py) to confirm it
  far ahead       the best pick is far ahead of the next one: a short ladder

The first two are what a hole in the data looks like; `build.py --audit`
lists them and ends with status 1 when there are any. The third is only a
hint. A finding is a row to look at, not always an error: Forever did change
some low level items into good ones.
"""
from __future__ import annotations

from dataclasses import dataclass

import corrections
import ladders
import phases

LOW_LEVEL_GAP = 15   # "far under the cap": that many levels
LONELY_LEAD = 0.4    # "far ahead": that share of the best pick's score
CASTER_ROLES = ("Healer", "Caster DPS")
SCHOOL_DAMAGE = tuple(range(84, 90))  # ForeverDB's stat ids for the damage of one school

LOW, POWERLESS, LONELY = "low level", "no spell power", "far ahead"
SUSPICIOUS = (LOW, POWERLESS)


@dataclass(frozen=True)
class Finding:
    kind: str
    cls: str
    spec: str        # the spec's name
    mode: str
    slot: str
    item_id: int
    name: str
    best: bool       # a best pick in at least one case, not only an alternative
    detail: str
    phases: tuple    # the content phases it shows up in

    def line(self) -> str:
        role = "best pick" if self.best else "alternative"
        where = "every phase" if self.phases == phases.PHASES else "phase " + ", ".join(map(str, self.phases))
        return (f"{self.cls} {self.spec} {self.mode} {self.slot}: {self.name} ({self.item_id}), {self.detail}, "
                f"{role}, {where}")


def shown_rows(slots: dict, flt) -> dict[str, tuple[list, list]]:
    """{slot: (best, alternatives)} as the addon shows a spec's list under one filter."""
    visible = {slot: [entry for entry in entries if entry.passes(flt)] for slot, entries in slots.items()}
    visible["main"], visible["off"] = ladders.weapon_lists(visible["main"], visible["off"])
    return {slot: ladders.picks(slot, entries) for slot, entries in visible.items()}


def run(db, all_ladders: dict, read_in_game=frozenset()) -> list[Finding]:
    """The findings over every list of ladders.build_all's result, each row once.

    read_in_game: the weapons whose tooltip was read in the game; their lack
    of spell power is the game's, not a hole.
    """
    cap = db.meta["cap"]
    found: dict[tuple, dict] = {}

    def note(kind, key, entry, best, detail, phase):
        record = found.setdefault((kind, *key, entry.item_id), {"best": False, "detail": detail, "phases": set()})
        record["best"] = record["best"] or best
        record["phases"].add(phase)

    for cls, specs in all_ladders.items():
        for spec, modes in specs.items():
            spec_def = db.classes[cls]["specs"][spec]
            for mode, slots in modes.items():
                weights = spec_def["weights"][ladders.MODES[mode]]
                wanted = [stat for stat in (*corrections.POWER, *SCHOOL_DAMAGE) if weights.get(stat, 0) > 0]
                caster = spec_def["role"] in CASTER_ROLES and wanted
                for side in ("a", "h"):
                    for phase in phases.PHASES:
                        for slot, (best, alternatives) in shown_rows(slots, (side, False, False, phase)).items():
                            key = (cls, spec, mode, slot)
                            for entry in best + alternatives:
                                gear = db.gear[entry.item_id]
                                if 0 < gear["req"] < cap - LOW_LEVEL_GAP:
                                    note(LOW, key, entry, entry in best, f"requires level {gear['req']}", phase)
                                if (caster and slot in ("main", "off") and gear["inv"] in corrections.WEAPONS
                                        and entry.item_id not in read_in_game
                                        and not any(gear["stats"].get(stat) for stat in wanted)):
                                    note(POWERLESS, key, entry, entry in best, "no healing or spell damage in the data",
                                         phase)
                            if best and alternatives and best[-1].stored:
                                lead = (best[-1].stored - alternatives[0].stored) / best[-1].stored
                                if lead > LONELY_LEAD:
                                    behind = db.items[alternatives[0].item_id]["name"]
                                    note(LONELY, key, best[-1], True, f"{lead:.0%} ahead of {behind}", phase)

    findings = []
    for (kind, cls, spec, mode, slot, item_id), record in found.items():
        findings.append(Finding(
            kind=kind, cls=cls, spec=db.classes[cls]["specs"][spec]["name"], mode=mode, slot=slot, item_id=item_id,
            name=db.items[item_id]["name"], best=record["best"], detail=record["detail"],
            phases=tuple(sorted(record["phases"]))))
    findings.sort(key=lambda f: (f.kind, f.cls, f.spec, f.mode, f.slot, not f.best, f.item_id))
    return findings


def suspicious(findings: list[Finding]) -> list[Finding]:
    """The findings a hole in the data would explain: a low level best pick, a caster's weapon with no spell power."""
    return [f for f in findings if f.kind == POWERLESS or (f.kind == LOW and f.best)]


def summary(findings: list[Finding]) -> str:
    counts = {kind: [f for f in findings if f.kind == kind] for kind in (LOW, POWERLESS, LONELY)}
    parts = [f"{len(rows)} {kind} ({len({f.item_id for f in rows})} items)" for kind, rows in counts.items() if rows]
    return ", ".join(parts) if parts else "nothing to look at"


def report(findings: list[Finding]) -> list[str]:
    titles = {
        LOW: f"Low level: a shown item requires a level more than {LOW_LEVEL_GAP} under the cap",
        POWERLESS: "No spell power: a caster's or healer's weapon with none of the stats the spec values",
        LONELY: f"Far ahead: the best pick leads the next one by more than {LONELY_LEAD:.0%} (a hint only)",
    }
    lines = []
    for kind, title in titles.items():
        rows = [f for f in findings if f.kind == kind]
        if rows:
            lines.append(f"{title} - {len(rows)} rows")
            lines += ["  " + f.line() for f in rows]
    return lines
