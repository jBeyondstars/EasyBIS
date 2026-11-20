"""Build Easy BIS's data files from ForeverDB's addon data.

    python build.py                    build ../Data from the local copy
    python build.py --check            say whether ForeverDB published newer data (one request)
    python build.py --update           download what changed, then build
    python build.py --update-consumables
                                       download only the data files of the Consumables tab, without building
    python build.py --import FOLDER    copy the data from an unpacked ForeverDB addon folder, then build
    python build.py --audit            build, then list the rows the data probably has wrong (audit.py)
    python build.py --capture-tool     install the EasyBIS_Capture addon, which reads item tooltips in the game
    python build.py --check-capture [FILE]
                                       compare what /ebiscapture read with the data, stat by stat and the
                                       reputations asked for (no build)
    python build.py --import-capture [FILE]
                                       keep what the capture read (corrections.py, consumables.py), then build
    python build.py --import-prices [FILE]
                                       keep what the vendors' windows showed in the game (corrections/costs.json),
                                       then build
    python build.py --audit-consumables
                                       list where the game disagrees with ForeverDB's catalogue of consumables
    python build.py --import-questie [FOLDER]
                                       keep the sources QuestieDB has for the items the data gives none
                                       (questie.py), then build; FOLDER defaults to the QuestieDB addon
                                       installed next to Easy BIS
    python build.py --import-drops [FOLDER]
                                       keep the drops Wowhead Forever counted, as the DungeonJournal and GearQuest
                                       Forever addons hold them (drops.py), then build; FOLDER defaults to the
                                       AddOns folder Easy BIS is in
    python build.py --import-dungeon-quests [FOLDER]
                                       keep the dungeon QuestieDB sorts each quest of the data's items under
                                       (runs.py), then build; FOLDER defaults to the QuestieDB addon installed
                                       next to Easy BIS
    python build.py --import-reputations [FOLDER]
                                       keep the reputations items and enchants ask for (reputations.py), then build;
                                       FOLDER holds ForeverDB's Items.lua and Recipes.lua and defaults to the local
                                       copy; QuestieDB, and the quests the Questie addon hides, are read in the
                                       addons installed next to Easy BIS; the newest capture gives the requirement
                                       of a piece ForeverDB gives none (its "Requires <faction> - <standing>")

The local copy is _build/cache/ForeverDB. Data from ForeverDB.net
(https://foreverdb.net), GPL-3.0 with an attribution term: see NOTICE.txt.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import audit  # noqa: E402
import capture  # noqa: E402
import consumables  # noqa: E402
import corrections  # noqa: E402
import drops  # noqa: E402
import fdb  # noqa: E402
import ladders  # noqa: E402
import luaout  # noqa: E402
import phases  # noqa: E402
import questie  # noqa: E402
import reputations  # noqa: E402
import runs  # noqa: E402
import source  # noqa: E402

CACHE = HERE / "cache" / "ForeverDB"
OUT = HERE.parent / "Data"
ADDONS = HERE.parent.parent   # Interface/AddOns
GAME = HERE.parents[3]        # the game folder, which holds Interface and WTF


def build(cache_dir: Path = CACHE, out_dir: Path = OUT, details: bool = False) -> int:
    """Write the data files; returns the number of suspicious rows the audit found."""
    db = fdb.load(cache_dir)
    all_ladders = ladders.build_all(db)
    sizes = luaout.write_all(db, all_ladders, out_dir)

    specs = sum(len(specs) for specs in all_ladders.values())
    entries = sum(len(slot) for specs in all_ladders.values() for modes in specs.values()
                  for slots in modes.values() for slot in slots.values())
    print(f"ForeverDB data {db.meta['version']}, game build {db.meta['build']}, level {db.meta['cap']}")
    print(f"{len(all_ladders)} classes, {specs} specs, {entries} list entries, "
          f"{len(luaout.shown_ids(all_ladders))} items")
    for name, size in sizes.items():
        print(f"  {out_dir.name}/{name:13s} {size / 1024:7.1f} KB")

    per_phase = {phase: 0 for phase in phases.PHASES}
    for specs in all_ladders.values():
        for modes in specs.values():
            for slots in modes.values():
                for slot in slots.values():
                    for entry in slot:
                        per_phase[entry.phase] += 1
    print("List entries per phase: " + ", ".join(f"{phase}: {count}" for phase, count in per_phase.items())
          + f" (the game is in phase {phases.CURRENT})")
    for number, name in phases.unknown_raids(db):
        print(f"  New raid in the data: {name} (instance {number}), taken for phase "
              f"{phases.raid_phase(phases.NEW_RAID)}. Name it in _build/phases.py.")

    observed = corrections.load()
    fixes = db.corrected
    if not observed:
        print("Corrections: none. No weapon was read in the game yet (--capture-tool, /ebiscapture, --import-capture).")
    else:
        print(f"Corrections: {fixes.observed} weapons read in the game (build {', '.join(sorted(fixes.builds)) or '-'}): "
              f"{len(fixes.filled)} given the healing and spell damage the data lacks, {len(fixes.replaced)} given "
              f"the game's instead of the data's, {len(fixes.dps)} the damage per second the game shows; "
              f"{fixes.agree} already right in the data, {len(fixes.unknown)} not in the data.")
        if fixes.differ:
            print(f"  {len(fixes.differ)} weapons differ from a capture older than the data and were left alone: "
                  "read them again in the game (/ebiscapture all).")
        for item_id, in_game, in_data in fixes.differ[:10] if details else ():
            print(f"  {item_id} {db.items.get(item_id, {}).get('name', '?')}: healing and damage {in_game} in the game, "
                  f"{in_data} in the data")

    game = db.aligned
    if not game or not game.build:
        print("Game: not read yet. Which items the game has is not known (--capture-tool, /ebiscapture, --import-capture).")
    else:
        print(f"Game (build {game.build}): {game.absent} items of the data are not in the game, {len(game.dropped)} of "
              f"them left out of the lists; {len(game.added)} pieces the game has and ForeverDB does not list are "
              f"added, with no known source and for the last phase"
              + (f"; {len(game.listed)} more are listed by ForeverDB now" if game.listed else "")
              + (f"; {len(game.withheld)} more that no player gets are not (corrections.NOT_FOR_PLAYERS, withdrawn)"
                 if game.withheld else "")
              + ".")
        if game.stale:
            print(f"  The data is of game build {db.meta['build']}, later than that reading: read the game again "
                  "(/ebiscapture all).")

    filled = db.filled
    if not filled or not filled.known:
        print("Sources: none read in QuestieDB yet. The items the data gives no source stay without one "
              "(--import-questie).")
    else:
        shown = luaout.shown_ids(all_ladders)
        unknown = sum(1 for item_id in shown if item_id in db.items and not db.items[item_id]["sources"])
        print(f"Sources (QuestieDB {filled.version}, read {filled.date}): {len(filled.items)} items the data gives no "
              f"source have one, {len(filled.added)} of them pieces added from the game (still shown with the items "
              f"of no known source), and {len(filled.enchants)} enchants; {len(set(filled.items) & shown)} of those "
              f"items are in the lists, where {unknown} still have no source at all"
              + (f"; {len(filled.listed)} more have a source in ForeverDB's data by now" if filled.listed else "")
              + ".")

    confirmed = db.confirmed
    if not confirmed or not confirmed.known:
        print("Drops: none counted in Forever yet. The bosses and the rates stay Classic's (--import-drops).")
    else:
        print(f"Drops (DungeonJournal {confirmed.journal}, read {confirmed.date}): {len(confirmed.items)} items have their "
              f"boss confirmed and the rate counted in Forever, {len(confirmed.named)} of them with a boss the data did "
              f"not name; {len(confirmed.moved)} take the boss counted in place of the data's; "
              f"{len(confirmed.disputed)} are named for another creature on too little to change them.")
        print(f"  {len(confirmed.placed)} of them have a creature the data gives no place written as a boss of the "
              f"dungeon it was counted in, {len(confirmed.dungeons)} dungeons of Forever the data lacks among them "
              f"(runs.py); {len(confirmed.sourced)} items the data gives no source take the bosses counted for them.")
    quests = runs.load_quests()
    if not quests:
        print("Dungeon quests: none read in QuestieDB yet. The Dungeons tab lists no quest (--import-dungeon-quests).")
    else:
        print(f"Dungeon quests (QuestieDB {quests['questiedb']}, read {quests['date']}): {len(db.quest_places)} quests "
              f"of the data's items are done in a dungeon, {sum(1 for _, wing in db.quest_places.values() if wing)} "
              "of them in a wing named by hand (runs.QUEST_WINGS).")

    reading = reputations.load()
    if not reading:
        print("Reputations: none read yet. The addon says no item asks for one (--import-reputations).")
    else:
        shown = luaout.shown_ids(all_ladders)
        kinds = {kind: sum(1 for item_id in shown for record in reading["items"].get(item_id, ())
                           if record["kind"] == kind) for kind in (reputations.WEAR, reputations.QUEST, reputations.RECIPE)}
        seen = {source: len({item_id for item_id in shown for record in reading["items"].get(item_id, ())
                             if record.get("read") == source}) for source in ("game", "atlasloot")}
        print(f"Reputations (QuestieDB {reading['questiedb']}, read {reading['date']}): of the listed items, "
              f"{kinds[reputations.WEAR]} ask the wearer for one ({seen['game']} of them read in the game's tooltips, "
              f"{seen['atlasloot']} in AtlasLoot's tables), {kinds[reputations.QUEST]} come from a quest that does and "
              f"{kinds[reputations.RECIPE]} from a recipe sold against one.")
        for line in reputations.check_lines(reading.get("checks", {})):
            print("  " + line)
        enchants = {enchant for specs in (db.enchants or {}).values() for lists in specs.values()
                    for entries in lists.values() for enchant, _ in entries}
        outside, unasked = reputations.gaps(reading, db, shown, enchants)
        if unasked:
            counts = ", ".join(f"{reputations.FACTIONS[faction][0]} {len(pieces)}"
                               for faction, pieces in sorted(unasked.items(), key=lambda pair: (-len(pair[1]), pair[0])))
            print(f"  {sum(map(len, unasked.values()))} listed pieces a faction's quartermaster sells have no requirement "
                  f"any source gives ({counts}): the addon says they ask for none. On Forever the quartermaster "
                  "asks for a standing their tooltips do not carry: only his window shows it (AtlasLoot's tables "
                  f"give it: install AtlasLoot Forever, then --import-reputations).")
        if outside:
            print("  Factions reputations.FACTIONS lacks, asked for by a quest or a recipe of what the lists show "
                  "(left out, the addon says nothing is asked): " + "; ".join(
                      f"{faction} ({', '.join(map(str, owners[:5]))}{', ...' if len(owners) > 5 else ''})"
                      for faction, owners in sorted(outside.items())))
        differ = {item_id: pair for item_id, pair in reading.get("differ", {}).items() if item_id in shown}
        if differ:
            print(f"  {len(differ)} listed pieces ask in the game for another reputation than ForeverDB says; its is kept: "
                  + ", ".join(f"{item_id} {data} / game {game}" for item_id, (data, game) in sorted(differ.items())[:5]))
    priced = db.priced
    if priced and priced.changed:
        print(f"Prices (written down {priced.date}): {len(priced.items)} items carry what their vendor asks in a currency, "
              f"{len(priced.read)} of them read at the vendor and the others the beta's, {len(priced.freed)} of a neutral "
              f"vendor count for both factions; {len(priced.absent)} of the file are not items the data says that vendor "
              "sells.")

    reading = db.simulated
    if reading and reading.specs:
        names = ", ".join(f"{db.classes[cls]['specs'][spec]['name']} {cls.title()}" for cls, spec in sorted(reading.specs))
        print(f"Simulation (WoWSims Forever {reading.commit}, {reading.date}): the PvE lists of {names} are ranked on the "
              "damage measured, every other list on ForeverDB's weights.")
    placed = [(cls, spec, slot, entry.item_id) for cls, specs in all_ladders.items() for spec, modes in specs.items()
              for slot, entries in modes["pve"].items() for entry in entries if entry.placed]
    if placed:
        names = ", ".join(f"{db.classes[cls]['specs'][spec]['name']} {cls.title()}"
                          for cls, spec in sorted({(cls, spec) for cls, spec, _, _ in placed}))
        print(f"  Placed from a close spec's simulation, with no score of their own, until theirs: {len(placed)} items "
              f"in the PvE lists of {names} (corrections/placed.json).")

    findings = audit.run(db, all_ladders, read_in_game=frozenset(observed))
    suspicious = audit.suspicious(findings)
    print(f"Audit: {audit.summary(findings)}." + ("" if details or not findings else " Details: build.py --audit"))
    if details:
        for line in audit.report(findings):
            print(line)
    return len(suspicious)


def check_report(check) -> list[str]:
    """What capture.check_capture found, as lines to print."""
    lines = [f"Capture of game build {check.game} ({check.locale}): the game showed "
             + ", ".join(f"{check.read[name]} of {count} {name}" for name, count in check.asked.items()) + "."]
    if any(check.absent.values()):
        lines.append("Not in the game's own item table, so not asked for: "
                     + ", ".join(f"{len(rows)} {name}" for name, rows in check.absent.items() if rows) + "."
                     + (f" Of {check.sample[0]} of them asked for all the same, {check.sample[1]} answered."
                        if check.sample else ""))
        for name, rows in check.absent.items():
            if rows:
                lines.append(f"  {name}: " + ", ".join(f"{label or '?'} ({item_id})" for item_id, label in rows[:8])
                             + (", ..." if len(rows) > 8 else ""))
    lines.append(f"The game against the data the build ranks, {check.compared} items compared:")
    lines.append(f"  {'stat':20s} {'same':>6} {'missing':>8} {'only in data':>13} {'differs':>8}")
    for family, counts in sorted(check.families.items(), key=lambda kv: -check.problems(kv[0])):
        lines.append(f"  {family:20s} {counts['same']:>6} {counts['missing']:>8} {counts['extra']:>13} "
                     f"{counts['differs']:>8}")
    words = {"missing": "the game shows it, the data has none", "extra": "only the data has it",
             "differs": "another value"}
    for (family, kind), rows in sorted(check.examples.items(), key=lambda kv: (-check.problems(kv[0][0]), kv[0])):
        shown = "; ".join(f"{name} ({item_id}): {in_game} in the game, {in_data} in the data"
                          for item_id, name, in_game, in_data in rows)
        lines.append(f"  {family}, {words[kind]}: {shown}")
    if check.other_keys:
        lines.append("  Keys of the game's stat table that are not compared: "
                     + ", ".join(f"{key} ({count})" for key, count in check.other_keys.most_common(12)))
    pieces = list(check.unlisted.values())
    if pieces:
        sets = {}
        for piece in pieces:
            if piece["set"]:
                sets[piece["set"]] = sets.get(piece["set"], 0) + 1
        biggest = sorted(sets.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
        lines.append(f"Pieces the data leaves out of its lists that the game showed: {len(pieces)}, of which "
                     f"{sum(1 for piece in pieces if piece['classes'])} for some classes only and "
                     f"{sum(sets.values())} of {len(sets)} sets"
                     + (" (" + ", ".join(f"{name} {count}" for name, count in biggest) + ")" if biggest else "") + ".")
    return lines


def reputation_report(parsed: dict) -> list[str]:
    """What reputations.check_capture found, as lines to print."""
    if parsed["locale"] != "enUS":
        return [f"Reputations: the capture is in {parsed['locale']}, the tooltips are read in English only."]
    facts, _ = reputations.read_item_facts((CACHE / "Items.lua").read_text(encoding="utf-8"))
    found = reputations.check_capture(parsed, facts, reputations.load())
    name = lambda fact: (f"{reputations.FACTIONS[fact[0]][0]} {fact[1]}" if isinstance(fact, (tuple, list))
                         else fact or "none")
    lines = [f"Reputations the game's tooltips ask for, against the data: {len(found['same'])} the same, "
             f"{len(found['missing'])} the data has not yet (--import-reputations keeps them), {len(found['differs'])} "
             f"another, {len(found['extra'])} the data asks and the item's tooltip does not (its vendor may), {len(found['outside'])} of a faction "
             "reputations.FACTIONS lacks."]
    words = {"missing": "the data has none", "differs": "another", "extra": "the item's tooltip shows none",
             "outside": "a faction the table lacks"}
    for kind, word in words.items():
        if found[kind]:
            lines.append(f"  {word}: " + "; ".join(f"{item_id}: data {name(data)}, game {name(game)}"
                                                  for item_id, data, game in found[kind][:6])
                         + ("; ..." if len(found[kind]) > 6 else ""))
    return lines


def consumables_report(result, kept: dict, catalogue: dict) -> list[str]:
    """What consumables.read_capture found, as lines to print."""
    lines = [f"Consumables: {result.read} of the {result.listed} on the capture's list were read, {result.understood} "
             f"understood whole; {len(result.absent)} the game did not show."]
    if not result.locale.startswith("en"):
        lines.append(f"  The capture is in {result.locale}: the phrases are understood in English only, nothing was kept.")
    if result.by_category:
        lines.append("  By category: " + ", ".join(f"{name} {count}" for name, count in sorted(result.by_category.items())))
    if result.unread:
        lines.append(f"  Not understood: {len(result.unread)} phrases, the most frequent first (numbers as N):")
        lines.extend(f"    {count:3d} items: {phrase}" for phrase, count in result.unread.most_common(40))
    if result.other_unread:
        lines.append(f"  {result.other_unread} items the tab does not list (bombs, keys, fireworks) hold phrases not understood.")
    found = consumables.audit(kept, catalogue)
    lines.append(f"  The game against ForeverDB's catalogue: {consumables.audit_summary(found)}. "
                 "Details: build.py --audit-consumables")
    return lines


def prices_report(reading) -> list[str]:
    """What the vendors' windows said of the costs file, to print."""
    lines = [f"Prices read at the vendor (game build {reading.game or '-'}, {reading.date or '-'}): "
             f"{len(reading.confirmed)} confirmed, {len(reading.changed)} changed, {len(reading.added)} added; "
             f"{reading.unread} of the file are still the beta's."]
    lines += [f"  Changed: {name} ({item_id}), {old} -> {new}" for item_id, name, old, new in reading.changed]
    lines += [f"  Added: {name} ({item_id}), {price}" for item_id, name, price in reading.added]
    lines += [f"  Left as it was, the window asks {asked}: {name} ({item_id})" for item_id, name, asked in reading.other]
    if reading.unseen:
        lines.append(f"  {len(reading.unseen)} items of the file were not in the window, and stay as they were: "
                     + ", ".join(name for _, name in reading.unseen))
    lines += [f"  Not in {corrections.COSTS_FILE.name}, so not kept: {name} (npc {npc}), {rows} items"
              for npc, name, rows in reading.strangers]
    return lines


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build Easy BIS's data files from ForeverDB's addon data.")
    parser.add_argument("--check", action="store_true", help="compare the local copy with ForeverDB's manifest")
    parser.add_argument("--update", action="store_true", help="download the data files that changed, then build")
    parser.add_argument("--update-consumables", action="store_true",
                        help="download only the data files of the Consumables tab, without building")
    parser.add_argument("--audit-consumables", action="store_true",
                        help="list where the game disagrees with ForeverDB's catalogue of consumables, and stop")
    parser.add_argument("--import", dest="addon", metavar="FOLDER",
                        help="copy the data from an unpacked ForeverDB addon folder, then build")
    parser.add_argument("--audit", action="store_true",
                        help="list the rows the data probably has wrong; status 1 when there are suspicious ones")
    parser.add_argument("--capture-tool", action="store_true",
                        help="install the EasyBIS_Capture addon next to Easy BIS (reads item tooltips in the game)")
    parser.add_argument("--check-capture", nargs="?", const="", metavar="FILE",
                        help="compare what /ebiscapture read with the data, stat by stat, and stop")
    parser.add_argument("--import-capture", nargs="?", const="", metavar="FILE",
                        help="keep what /ebiscapture read; FILE defaults to the newest EasyBIS_Capture.lua of WTF")
    parser.add_argument("--import-prices", nargs="?", const="", metavar="FILE",
                        help="keep what the vendors' windows showed in the game; FILE defaults to the newest "
                             "EasyBIS_Capture.lua of WTF that holds one")
    parser.add_argument("--import-questie", nargs="?", const="", metavar="FOLDER",
                        help="keep the sources QuestieDB has for the items the data gives none; FOLDER defaults "
                             "to the QuestieDB addon installed next to Easy BIS")
    parser.add_argument("--import-drops", nargs="?", const="", metavar="FOLDER",
                        help="keep the drops Wowhead Forever counted, read in the DungeonJournal and GearQuest Forever "
                             "addons; FOLDER defaults to the AddOns folder Easy BIS is in")
    parser.add_argument("--import-dungeon-quests", nargs="?", const="", metavar="FOLDER",
                        help="keep the dungeon QuestieDB sorts each quest of the data's items under; FOLDER defaults "
                             "to the QuestieDB addon installed next to Easy BIS")
    parser.add_argument("--import-reputations", nargs="?", const="", metavar="FOLDER",
                        help="keep the reputations items and enchants ask for; FOLDER holds ForeverDB's Items.lua and "
                             "Recipes.lua and defaults to the local copy")
    args = parser.parse_args(argv)

    if args.update_consumables:
        fetched = source.update(CACHE, source.read_manifest(), only=fdb.CONSUMABLE_FILES)
        print(f"Downloaded: {', '.join(fetched) if fetched else 'nothing, the local copy is current'}")
        return 0
    if args.audit_consumables:
        kept = consumables.load()
        data = fdb.read_consumables(CACHE)
        if not kept or data is None:
            print("No consumables read yet: run /ebiscapture in the game, /reload, then --import-capture.")
            return 1
        found = consumables.audit(kept["items"], data.catalogue)
        print(f"Consumables read in game build {kept['build']}: {consumables.audit_summary(found)}.")
        for entry in found:
            print("  " + entry.line())
        return 0
    if args.addon:
        copied = source.import_addon(Path(args.addon), CACHE)
        print(f"Copied {len(copied)} files into {CACHE}")
    if args.check or args.update:
        manifest = source.read_manifest()
        states = source.check(CACHE, manifest)
        print(f"ForeverDB publishes data {manifest['version']}")
        for name, state in states.items():
            print(f"  {name:16s} {state}")
        if args.check and not args.update:
            return 0 if all(state == "current" for state in states.values()) else 1
        fetched = source.update(CACHE, manifest)
        print(f"Downloaded: {', '.join(fetched) if fetched else 'nothing, the local copy is current'}")
    if args.capture_tool:
        folder, counts = capture.write_tool(fdb.load(CACHE, corrected=False), ADDONS)
        print(f"Installed {folder.name} in {folder.parent} with {sum(counts.values())} items to read: "
              + ", ".join(f"{count} {name}" for name, count in counts.items()) + ".")
        print("In the game: enable it, type /reload if the game was running, type /ebiscapture, wait for it to")
        print("finish, type /reload, then run: python -I _build/build.py --check-capture")
        return 0
    if args.check_capture is not None:
        saved = Path(args.check_capture) if args.check_capture else capture.find_saved(GAME)
        if saved is None or not saved.exists():
            print(f"No {capture.SAVED} under {GAME / 'WTF'}: run /ebiscapture in the game, then /reload.")
            return 1
        print(f"Capture: {saved}")
        try:
            check = capture.check_capture(fdb.load(CACHE), saved.read_text(encoding="utf-8", errors="replace"),
                                          groups=capture.capture_ids(fdb.load(CACHE, corrected=False)))
        except ValueError as error:
            print(f"{saved.name}: {error}")
            return 1
        for line in check_report(check):
            print(line)
        for line in reputation_report(capture.parse_saved(saved.read_text(encoding="utf-8", errors="replace"))):
            print(line)
        return 0
    if args.import_capture is not None:
        saved = Path(args.import_capture) if args.import_capture else capture.find_saved(GAME)
        if saved is None or not saved.exists():
            print(f"No {capture.SAVED} under {GAME / 'WTF'}: run /ebiscapture in the game, then /reload.")
            return 1
        print(f"Capture: {saved}")
        published = fdb.load(CACHE, corrected=False)
        eaten = None
        try:
            parsed = capture.parse_saved(saved.read_text(encoding="utf-8", errors="replace"))
        except ValueError as error:
            print(f"{saved.name}: {error}")
            return 1
        if published.consumables is not None:
            eaten = consumables.read_capture(published, parsed)
            if eaten.readings:
                consumables.save(eaten, parsed["date"])
            for line in consumables_report(eaten, consumables.load().get("items", {}), published.consumables.catalogue):
                print(line)
        try:
            result = capture.import_capture(published, saved)
        except ValueError as error:
            if not (eaten and eaten.readings):
                print(f"{saved.name}: {error}")
                return 1
            # the game stopped answering after the consumables, which come first: they are kept all the same
            result = None
            print(f"Gear: nothing kept from this capture, the corrections stay as they are ({error}).")
        if result:
            print(f"Capture of game build {result.game} ({result.locale}): {result.read} tooltips, {result.weapons} weapons "
                  f"of the data, {result.with_power} with healing or spell damage ({result.from_stats} of them read in the "
                  f"game's stat table, not on the tooltip); {result.missing} the game did not show.")
            if result.other_names:
                print(f"  {len(result.other_names)} weapons have another name in the game than in the data, "
                      f"for example {result.other_names[0]}.")
            for template, count in result.unread.most_common(5):
                print(f"  Not understood ({count} weapons): {template}")
            print(f"Kept in {corrections.FILE.relative_to(HERE.parent)}.")
            if result.reading:
                print(f"The capture holds {result.shown} of the {result.listed} items of its list: the "
                      f"{len(result.reading['absent'])} others are taken as items the game does not have, and the "
                      f"{len(result.reading['unlisted'])} pieces it showed that ForeverDB does not list are kept. "
                      f"In {corrections.GAME_FILE.relative_to(HERE.parent)}.")
            else:
                print(f"The capture holds {result.shown} of the {result.listed} items of its list, in {result.locale}: not "
                      f"enough to say which items the game has ({capture.COMPLETE:.0%} in English are needed). "
                      f"{corrections.GAME_FILE.name} is left as it is.")
    if args.import_prices is not None:
        saved = Path(args.import_prices) if args.import_prices else capture.find_vendors(GAME)
        if saved is None or not saved.exists():
            print(f"No vendor's window read under {GAME / 'WTF'}: open it in the game with {capture.ADDON} enabled, "
                  "then /reload.")
            return 1
        print(f"Capture: {saved}")
        try:
            reading = capture.import_prices(fdb.load(CACHE, corrected=False), saved)
        except ValueError as error:
            print(f"{saved.name}: {error}")
            return 1
        for line in prices_report(reading):
            print(line)
        if not reading.read:
            print(f"Nothing kept: {corrections.COSTS_FILE.name} is left as it is.")
            return 1
        print(f"Kept in {corrections.COSTS_FILE.relative_to(HERE.parent)}.")
    if args.import_questie is not None:
        folder = Path(args.import_questie) if args.import_questie else questie.find(ADDONS)
        if folder is None or not (folder / questie.TOC).exists():
            print(f"No {questie.TOC} in {folder or ADDONS / questie.ADDON}: install the QuestieDB addon, or name "
                  "its folder.")
            return 1
        try:
            reading = questie.collect(fdb.load(CACHE, corrected=False), corrections.load_game(), questie.Store(folder))
        except ValueError as error:
            print(f"{folder}: {error}")
            return 1
        corrections.save_sources(reading, corrections.SOURCES_FILE)
        print(f"QuestieDB {reading['questiedb']} ({folder}): of the {reading['asked']['items']} items and "
              f"{reading['asked']['enchants']} enchants the data gives no source, it has one for "
              f"{len(reading['items'])} and {len(reading['enchants'])}. "
              f"Kept in {corrections.SOURCES_FILE.relative_to(HERE.parent)}.")
    if args.import_drops is not None:
        folder = Path(args.import_drops) if args.import_drops else ADDONS
        if drops.find(folder) is None:
            print(f"No {drops.JOURNAL} addon in {folder}: install it, or name the AddOns folder that has it.")
            return 1
        try:
            reading = drops.collect(fdb.load(CACHE), folder)
        except ValueError as error:
            print(f"{folder}: {error}")
            return 1
        corrections.save_drops(reading, corrections.DROPS_FILE)
        print(f"DungeonJournal {reading['journal']} and GearQuest Forever {reading['gearquest']}: drops counted for "
              f"{len(reading['items'])} items of the data. Kept in {corrections.DROPS_FILE.name}.")
    if args.import_dungeon_quests is not None:
        folder = Path(args.import_dungeon_quests) if args.import_dungeon_quests else questie.find(ADDONS)
        if folder is None or not (folder / questie.TOC).exists():
            print(f"No {questie.TOC} in {folder or ADDONS / questie.ADDON}: install the QuestieDB addon, or name "
                  "its folder.")
            return 1
        try:
            reading = runs.collect_quests(fdb.load(CACHE), questie.Store(folder))
        except ValueError as error:
            print(f"{folder}: {error}")
            return 1
        runs.save_quests(reading, runs.FILE)
        print(f"QuestieDB {reading['questiedb']} ({folder}): {len(reading['quests'])} quests of the data's items are "
              f"sorted under an instance. Kept in {runs.FILE.name}.")
    if args.import_reputations is not None:
        folder = Path(args.import_reputations) if args.import_reputations else CACHE
        missing = [name for name in reputations.SOURCE_FILES if not (folder / name).exists()]
        if missing:
            print(f"No {' or '.join(missing)} in {folder}: name the folder of ForeverDB's data files that has them.")
            return 1
        store = questie.find(ADDONS)
        if store is None:
            print(f"No {questie.TOC} in {ADDONS / questie.ADDON}: install the QuestieDB addon.")
            return 1
        hider = ADDONS / reputations.QUESTIE
        if reputations.hidden_quests(hider) is None:
            print(f"No {reputations.BLACKLIST} in {hider}: install the Questie addon, whose list of the quests the "
                  f"game does not have is read.")
            return 1
        db = fdb.load(CACHE)
        saved, captured, asks = capture.find_saved(GAME), None, {}
        if saved:
            text = saved.read_text(encoding="utf-8", errors="replace")
            try:
                captured = capture.parse_saved(text)
            except ValueError as error:
                print(f"{saved}: {error}. The tooltips are not read.")
            try:
                asks = capture.parse_asks(text)
            except ValueError as error:
                print(f"{saved}: {error}. The vendors' windows are not read.")
        atlas, atlas_version = reputations.atlasloot(ADDONS)
        try:
            reading = reputations.collect(db, folder, questie.Store(store), luaout.shown_ids(ladders.build_all(db)),
                                          questie_folder=hider, captured=captured, atlas=atlas,
                                          atlas_version=atlas_version, asks=asks)
        except ValueError as error:
            print(f"{folder}: {error}")
            return 1
        reputations.save(reading)
        read = sum(1 for records in reading["items"].values() for record in records if record.get("read") == "game")
        if not captured:
            print("Capture: none. A piece ForeverDB gives no requirement asks for none (--capture-tool, /ebiscapture).")
        elif captured["locale"] != "enUS":
            print(f"Capture ({captured['date']}) in {captured['locale']}: the tooltips are read in English only, none "
                  "was read.")
        else:
            print(f"Capture ({captured['date']}, {len(captured['items'])} items): {read} items take their requirement from "
                  f"the game's tooltip, {len(reading['differ'])} say otherwise than ForeverDB, whose is kept.")
        if not atlas:
            print(f"AtlasLoot: none in {ADDONS} ({', '.join(reputations.ATLASLOOT)}). A piece a vendor sells that "
                  "ForeverDB gives no requirement asks for none.")
        else:
            taken = sum(1 for records in reading["items"].values() for record in records
                        if record.get("read") == "atlasloot")
            print(f"AtlasLoot ({atlas_version}): {len(atlas)} items in its tables, {taken} requirements taken for "
                  "pieces a vendor sells that ForeverDB gives none.")
            for line in reputations.check_lines(reading["checks"]):
                print("  " + line)
        print(f"Reputations: {len(reading['items'])} items and {len(reading['enchants'])} enchants of the data ask for "
              f"one; {reading['hidden']} quests Questie {reading['questie']} says the game does not have are left "
              f"out. Kept in {reputations.FILE.name}.")
    suspicious = build(details=args.audit)
    return 1 if args.audit and suspicious else 0


if __name__ == "__main__":
    sys.exit(main())
