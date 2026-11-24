"""Notes on rankings that surprise: a few words, written by hand, that the addon shows by a mark on the item's row.

A list ranked by simulation puts Destiny before weapons with more damage per second, and Treant's Bane far under
what its stats promise. The reason is a fact the row does not show: a proc that is up half of the fight, a weapon
speed, an effect the simulator lacks. corrections/notes.json holds those facts, in English and French; each one is
checked against the game data or the simulator before it is written down. A note is for every spec or the ones it
names, for any slot or one (a weapon's proc is not worth the same in each hand), and the first of an item's notes
that fits a row is the one shown.

For the offline audit, the CLI imports paired PvE swaps into corrections/comparisons.json.
Only the written item notes are shipped in the addon.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import ladders
import relics
import situational_gear

FILE = Path(__file__).resolve().parent / "corrections" / "notes.json"
COMPARISONS = FILE.with_name("comparisons.json")
LANGUAGES = {"en": "enUS", "fr": "frFR"}   # the file's key -> the game's locale code
SLOTS = frozenset(slot for slot, _ in ladders.SLOTS)


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
        if note.get("slot") is not None and note["slot"] not in SLOTS:
            raise ValueError(f"{where}: no slot {note['slot']!r}")
        if note.get("list") is not None and note["list"] not in ladders.MODES:
            raise ValueError(f"{where}: no list {note['list']!r}")
        unknown = set(note) - {"items", "specs", "slot", "list", "simulated", *LANGUAGES}
        if unknown:
            raise ValueError(f"{where}: unknown field {sorted(unknown)}")


def shown(db, shown_ids: set[int], notes: list[dict] | None = None) -> list[dict]:
    """The notes with the items the lists show; a note none of whose items is shown is a mistake."""
    if notes is None:
        options = [n for n in situational_gear.notes() if shown_ids.intersection(n["items"])]
        notes = load() + options + relics.notes(shown_ids)
    check(db, notes)
    out = []
    for number, note in enumerate(notes, 1):
        items = sorted(item for item in note["items"] if item in shown_ids)
        if not items:
            raise ValueError(f"notes.json, note {number}: none of {note['items']} is in a list")
        out.append({**note, "items": items})
    return out


def simulation_limits(db, all_ladders) -> list[dict]:
    """Fallbacks for partial measures that can have a numeric score, scoped to the original run."""
    messages = {
        "without_effect": ("The simulator omits an effect on this item.",
                           "Le simulateur omet un effet de cet objet."),
        "assumed_rate": ("The uncertain proc rate limits how precisely this item can be ranked.",
                         "La fréquence incertaine du proc limite la précision du classement."),
    }
    result = []
    if not db.simulated:
        return result
    for (cls, spec), measured in sorted(db.simulated.specs.items()):
        entries = all_ladders.get(cls, {}).get(spec, {}).get("pve", {})
        for slot, ladder in entries.items():
            limits = defaultdict(set)
            if hasattr(ladder, "contexts"):
                # A note shared by both factions and all partners must hold whenever this ID appears.
                models = defaultdict(set)
                for (faction, _), rows in ladder.contexts.items():
                    for entry in rows:
                        models[entry.shown(faction)].add(entry.model)
                for item, reasons in models.items():
                    if reasons == {"unregistered_effect"}:
                        limits["without_effect"].add(item)
                    elif reasons <= {"unverified_proc_rate", "assumed_proc"}:
                        limits["assumed_rate"].add(item)
            else:
                candidates = {item for entry in ladder for item in (entry.item_id, entry.twin) if item}
                for field in messages:
                    # A faction counterpart can have a different effect or be absent from the simulator.
                    affected = candidates.intersection(measured.record.get(field, ()))
                    if affected:
                        limits[field] = affected
            for field, items in limits.items():
                en, fr = messages[field]
                result.append({"items": sorted(items), "specs": [f"{cls} {spec}"], "slot": slot,
                               "simulated": True, "en": en, "fr": fr})
    return result


def profile_key(record: dict) -> str:
    """The exact reference set, race, faction and fight length used for the paired substitutions."""
    profile = {key: record.get(key) for key in ("name", "race", "side", "seconds", "reference", "date")}
    return hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()


def import_trials(pairs, batches, reading, revision):
    """Cross-check the original inversion keys before accepting any longer rerun of the same trial."""
    trials = {}
    for runs, batch in batches:
        for key, trial in batch.items():
            cls, spec, mode, slot, canonical, actual = key.split("/")
            identity = [trial["item"], trial["rival"]]
            if (mode != "pve" or slot not in SLOTS or int(actual) != identity[0]
                    or identity[0] == identity[1] or pairs.get(key, [])[:2] != identity):
                raise ValueError(f"Trial differs from the original item pair: {key}")
            count = trial.get("iterations", runs)
            if key in trials and count < trials[key][-1]:
                continue
            dps, error = trial["dps_se"]["item"]
            stats, _ = trial["dps_se"]["all_stats"]
            trials[key] = [int(canonical), *identity, pairs[key][2], dps, error, stats, count]
    missing = pairs.keys() - trials.keys()
    if missing:
        raise ValueError(f"Missing {len(missing)} paired trials, including {min(missing)}")
    profiles, groups = {}, {}
    for key, row in sorted(trials.items()):
        cls, spec, _, slot, *_ = key.split("/")
        profile = f"{cls} {spec}"
        record = reading.specs[cls, int(spec)].record
        if (record.get("wowsims") or reading.commit) != revision:
            raise ValueError(f"{profile} uses another simulator revision")
        if profile not in profiles:
            profiles[profile] = profile_key(record)
        groups.setdefault(f"{profile} {slot}", []).append(row)
    return {"wowsims": revision, "profiles": profiles,
            "columns": ["pool_id", "measured_id", "rival_id", "archived_dps_difference",
                        "swap_dps", "paired_standard_error", "fixed_stats_dps", "iterations"], "groups": groups}


def comparisons(db, all_ladders, specific, source=None):
    """Only direct item measures whose published inversion still stands. Identify a rival's model limits."""
    if not db.simulated:
        return {}
    if source is None:
        source = json.loads(COMPARISONS.read_text(encoding="utf-8"))
    out = {}
    for group, rows in source["groups"].items():
        cls, number, slot = group.split()
        spec = int(number)
        profile = f"{cls} {spec}"
        measured = db.simulated.specs.get((cls, spec))
        kept = all_ladders.get(cls, {}).get(spec, {}).get("pve", {}).get(slot, ())
        # These duels refer to one archived race and gear set. A newer
        # faction-specific comparison can reverse both the order and the cause.
        if not kept or hasattr(kept, "contexts") or not measured or slot not in measured.slots:
            continue
        record = measured.record
        if ((record.get("wowsims") or db.simulated.commit) != source["wowsims"]
                or profile_key(record) != source["profiles"][profile]):
            continue
        covered = {item for note in specific if profile in note.get("specs", (profile,))
                   and note.get("slot", slot) == slot and note.get("list", "pve") == "pve" for item in note["items"]}
        visible = {entry.item_id for entry in kept}
        eligible = [row for row in rows if row[0] in visible and row[1] not in covered]
        if not eligible:
            continue
        # A compared item can lie below the displayed alternatives. Verify both against the current full ladder.
        ranked = measured.slots[slot]
        missing_effect = set(record.get("without_effect", ()))
        assumed_rate = set(record.get("assumed_rate", ()))
        actuals = {}
        for entry in ladders.full_ladder(db, cls, spec, "pve", slot):
            actual = entry.shown(record.get("side", "a")) or entry.item_id
            if ranked.measured(entry.item_id) and not entry.unscored and not entry.random:
                actuals[actual] = entry
        weights = db.classes[cls]["specs"][spec]["weights"]["raid"]

        def points(entry):
            return ladders.score(db, entry.item_id, weights, cls, melee=cls == "HUNTER" and spec == 3) or 0

        for canonical, actual, rival, archived, dps, error, stats, count in eligible:
            left, right = actuals.get(actual), actuals.get(rival)
            if (not left or not right or left.item_id != canonical or left.two_hand != right.two_hand
                    or actual in missing_effect or actual in assumed_rate):
                continue
            if ranked.scores[canonical] - ranked.scores[right.item_id] != archived:
                continue
            if archived * (points(left) - points(right)) >= -0.001:
                continue
            status = "n" if abs(dps) <= 2 * error else "r" if dps * archived < 0 else "c"
            if rival in missing_effect:
                status += "m"
            if rival in assumed_rate:
                status += "a"
            if status == "n":
                # A noisy duel alone does not explain either item's displayed rank.
                continue
            # The game loads one string per slot. Hundredths suffice for tooltip text.
            out.setdefault((cls, spec, slot), []).append((actual, rival, round(dps * 100),
                                                         round(stats * 100), count, status))
    return out


if __name__ == "__main__":
    import argparse
    import simulated

    parser = argparse.ArgumentParser(description="Refresh paired PvE comparisons from the original keys and trial logs.")
    parser.add_argument("pairs", type=Path, help="Original key -> [item id, rival id, published DPS difference]")
    parser.add_argument("all", type=Path, help="All paired trials at 500 iterations")
    parser.add_argument("ablation", type=Path, help="Reruns at 5,000 iterations")
    parser.add_argument("recheck", type=Path, help="Reruns at 20,000 iterations")
    parser.add_argument("--revision", required=True, help="WoWSims revision used to run these trials")
    parser.add_argument("--archive", type=Path, default=simulated.FILE, help="simulated.json used to run these trials")
    parser.add_argument("--out", type=Path, default=COMPARISONS)
    args = parser.parse_args()

    def read(path):
        return json.loads(path.read_text(encoding="utf-8-sig"))

    source = import_trials(read(args.pairs), [(500, read(args.all)), (5000, read(args.ablation)),
                                              (20000, read(args.recheck))], simulated.load(args.archive), args.revision)
    # Keep each slot on a separate line so that rerunning a single profile produces a small diff.
    groups = source.pop("groups")
    header = json.dumps(source, indent=1)[:-2] + ',\n "groups": {\n'
    lines = [f'  "{key}": ' + json.dumps(sorted(rows), separators=(",", ":")) for key, rows in groups.items()]
    args.out.write_bytes((header + ",\n".join(lines) + "\n }\n}\n").encode("utf-8"))
    print(f"{sum(map(len, groups.values()))} paired observations, {len(groups)} slots")
