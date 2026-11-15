"""Print how the generator's ladders compare with the pages read from foreverdb.net/bis.

    python tests/compare_site.py

A diagnostic, not a test: it lists every slot where the site's picks and ours
differ, with our scores for the site's items, so a rule can be worked out.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUILD))

import fdb  # noqa: E402
import ladders  # noqa: E402

TIE = 0.1  # scores closer than this are a tie: either order is right


def site_order(slot: str, ladder: list) -> tuple[list, object]:
    """Our picks laid out as the site lays them out: ([top, next, next], second ring or trinket)."""
    best, alternatives = ladders.picks(slot, ladder)
    second = best[1] if len(best) > 1 else None
    return best[:1] + alternatives, second


def slot_ladder(db, cls: str, spec: int, mode: str, slot: str) -> list:
    """The slot's full ladder; the two weapon slots are weighed against each other first."""
    if slot in ("main", "off"):
        main, off = ladders.weapon_lists(ladders.full_ladder(db, cls, spec, mode, "main"),
                                         ladders.full_ladder(db, cls, spec, mode, "off"))
        return main if slot == "main" else off
    return ladders.full_ladder(db, cls, spec, mode, slot)


def same_pick(ours, site_id: int, scores: dict) -> bool:
    if ours is None:
        return False
    if ours.item_id == site_id:
        return True
    theirs = scores.get(site_id)
    return theirs is not None and abs(theirs - ours.score) < TIE


def compare(db, page: dict) -> list[str]:
    cls, spec, mode = page["cls"], page["spec"], page["mode"]
    problems = []
    for slot, _ in ladders.SLOTS:
        site = page["slots"].get(slot, "absent")
        if site == "absent":
            continue
        ladder = slot_ladder(db, cls, spec, mode, slot)
        scores = {entry.item_id: entry.score for entry in ladders.full_ladder(db, cls, spec, mode, slot)}
        if site is None:
            if ladder:
                problems.append(f"{slot}: the site shows none, we list {ladder[0].item_id}")
            continue
        ours, second = site_order(slot, ladder)
        wrong = [i for i, site_id in enumerate(site["ids"])
                 if not same_pick(ours[i] if i < len(ours) else None, site_id, scores)]
        if "second" in site and not same_pick(second, site["second"], scores):
            wrong.append("second")
        top_gap = abs(ladder[0].score - site["score"]) if ladder else None
        if top_gap is None or top_gap > max(0.06, site["score"] * 0.001):
            wrong.append("score")
        if wrong:
            mine = [f"{entry.item_id} {entry.score:.1f}" for entry in ours]
            mine_second = f", second {second.item_id} {second.score:.1f}" if second else ""
            theirs = [f"{site_id} {scores.get(site_id, float('nan')):.1f}" for site_id in site["ids"]]
            problems.append(f"{slot}: differs at {wrong}\n      site {site['score']} {theirs} "
                            f"second {site.get('second')}\n      ours {mine}{mine_second}")
    return problems


def main() -> int:
    db = fdb.load(BUILD / "cache" / "ForeverDB", corrected=False)  # the site has ForeverDB's data as published
    golden = json.loads((BUILD / "tests" / "golden" / "site_2026-11-14.json").read_text(encoding="utf-8"))
    total = bad = 0
    for page in golden["pages"]:
        problems = compare(db, page)
        slots = len(page["slots"])
        total += slots
        bad += len(problems)
        name = db.classes[page["cls"]]["specs"][page["spec"]]["name"]
        print(f"{page['cls']} {name} {page['mode']}: {slots - len(problems)}/{slots} slots match")
        for problem in problems:
            print("   " + problem)
    print(f"\n{total - bad}/{total} slots match the site")
    return 0


if __name__ == "__main__":
    sys.exit(main())
