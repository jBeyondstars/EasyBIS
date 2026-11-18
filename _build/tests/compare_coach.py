"""Print how the Consumables tab's lists compare with what ForeverDB's coach recommends.

    python -I tests/compare_coach.py

A diagnostic, not a test: the coach simulates damage for 19 specs, the lists add up stat weights for all of them.
Each recommendation the spec's PvE list does not keep is printed with the reason. The lists are not bent to agree.
"""
from __future__ import annotations

import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BUILD))

import consumable_lists  # noqa: E402
import fdb  # noqa: E402


def main() -> int:
    db = fdb.load(BUILD / "cache" / "ForeverDB")
    compared, found = consumable_lists.coach_differences(db, consumable_lists.build(db))
    print(f"{compared} recommendations of the coach compared, {compared - len(found)} kept in the spec's PvE list, "
          f"{len(found)} not:")
    for difference in found:
        print("  " + difference.line())
    return 0


if __name__ == "__main__":
    sys.exit(main())
