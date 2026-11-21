"""Tests for the window, its filters and the minimap button, outside the game.

    python -P tests/test_ui.py

Needs the `lupa` package. The frames are stand-ins (wowstub.lua) that only
answer to real widget methods; what they are asked to show is compared with
what the generator's rules give.
"""
from __future__ import annotations

import dataclasses
import math
import re
import sys
import unittest
from pathlib import Path

TESTS = Path(__file__).resolve().parent
BUILD = TESTS.parent
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(TESTS))

import fdb  # noqa: E402
import ladders  # noqa: E402
import luaout  # noqa: E402
import phases  # noqa: E402
import reputations  # noqa: E402
import test_addon  # noqa: E402
from test_addon import (  # noqa: E402
    ATIESH, EVERYTHING, MAGEBLADE, VAULTED_SECRETS, WITH_PVP, Game, default_filter, for_list, strip_colors)

lupa = test_addon.lupa

EYE_OF_REND = 12587             # a drop of Warchief Rend Blackhand: Enhancement Shaman's second PvE head
DRAGONSCALE_HELM = 252605       # Black Dragonscale Helm, Leatherworking 300: Enhancement Shaman's best PvE head
TIMBERMAW_TUNIC = 252484        # crafted, Leatherworking 300
GRAND_MARSHALS_SUNDERER = 18830  # PvP rank 14
GENERALS_GREAVES = 231656       # no known source
ENHANCEMENT = "EasyBISCharDB = { class = 'SHAMAN', spec = 2, list = 'pve' }"
FIRE_MAGE = "EasyBISCharDB = { class = 'MAGE', spec = 2, list = 'pve' }"   # a spec with both weapon styles
OLD_CLIENT = "C_XMLUtil = nil; MenuUtil = nil; MenuResponse = nil"

# The window's sizes (UI\Browser.lua): its width, a row on two lines and on one, a slot's header, a note,
# the score bar
WIDTH, ROW, ONE_LINE, HEADER, NOTE, BAR = 960, 54, 36, 38, 28, 52


def plain(text: str) -> str:
    """A text without its colors and its pictures."""
    return re.sub(r"\|T[^|]*\|t\s*", "", strip_colors(text))


def find(menu, text):
    """The entry of a context menu whose text contains `text`."""
    for item in menu["items"].values():   # ["items"]: .items is the Lua table wrapper's own method
        if item.text and text in plain(item.text):
            return item
    raise AssertionError(f"no menu entry contains {text!r}: {texts(menu)}")


def texts(menu) -> list[str]:
    return [plain(item.text) for item in menu["items"].values() if item.text]


def label(control) -> str:
    """What a filter's button, or a plain button, reads."""
    button = control.button or control
    return strip_colors(button.Text.text if button.Text else button.GetText(button))


def look(control) -> str:
    """How a button is painted: idle, lit or active (gold)."""
    if control.label and list(control.label.color.values()) == [1, 0.82, 0]:
        return "active"
    return "lit" if control.highlightLocked else "idle"


def open_dropdown(game, button):
    if button.kind == "DropdownButton":
        game.stub.run(button, "OnMouseDown", "LeftButton")
    else:
        game.stub.run(button, "OnClick")


@unittest.skipIf(lupa is None, "lupa is not installed")
class WindowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.kept = ladders.build_all(cls.db)

    # -- reference ------------------------------------------------------------------------------

    @staticmethod
    def gap(score: float, reference: float) -> int:
        return math.floor((score - reference) / reference * 100 + 0.5)

    def reference_rows(self, token, spec, mode, flt=None, only_slot=None, alts=True,
                       count=ladders.ALTERNATIVES) -> list[tuple]:
        """(kind, id, slot, bis, gap) for every row the window should list, from the generator's rules.
        alts: False with the alternatives switched off. count: the alternatives a slot lists."""
        flt = for_list(flt or default_filter(), mode)
        side = flt[0]
        visible = {slot: [e for e in self.kept[token][spec][mode][slot] if e.passes(flt)]
                   for slot, _ in ladders.SLOTS}
        two = [e for e in visible["main"] if e.two_hand]
        one = [e for e in visible["main"] if not e.two_hand]
        lead = ladders.lead   # a placed item (flag e) is never a best pick
        two_hand = bool(two) and (not one or lead(two).stored >= lead(one).stored
                                  + (lead(visible["off"]).stored if visible["off"] else 0))
        shown = 1 + count
        other = {slot: entries[:shown] for slot, entries in
                 zip(("main", "off"), ladders.other_weapons(visible["main"], visible["off"]))}
        visible["main"], visible["off"] = ladders.weapon_lists(visible["main"], visible["off"])

        def other_gap(slot, entry) -> int | None:
            """A set against a set: one-hander + off hand against the two-hander, or the reverse. A placed
            item has no score of its own, so no gap; nor has one whose score is no full measure."""
            if entry.placed or entry.estimated:
                return None
            best_main, best_off = lead(visible["main"]), [lead(visible["off"])] if visible["off"] else []
            if two_hand:
                partner = [lead(other["off" if slot == "main" else "main"])] if other["off" if slot == "main" else "main"] else []
                return self.gap(entry.stored / 10 + (partner[0].stored / 10 if partner else 0), best_main.stored / 10)
            return self.gap(entry.stored / 10, best_main.stored / 10 + (best_off[0].stored / 10 if best_off else 0))

        rows = []
        for slot, _ in ladders.SLOTS:
            if only_slot and slot != only_slot:
                continue
            best, alternatives = ladders.picks(slot, visible[slot], count)
            for entry in best:
                rows.append(("item", entry.shown(side), slot, True, 0))
            for entry in alternatives if alts else []:
                rows.append(("item", entry.shown(side), slot, False,
                             None if entry.placed or entry.estimated
                             else self.gap(entry.stored / 10, best[0].stored / 10)))
            if alts and other.get(slot):
                rows.append(("note", None, slot, None, None))
                for entry in other[slot]:
                    rows.append(("item", entry.shown(side), slot, False, other_gap(slot, entry)))
            elif slot == "off" and two_hand:
                rows.append(("note", None, slot, None, None))
        return rows

    @staticmethod
    def shown_rows(game) -> list[tuple]:
        rows = []
        for row in game.ns.Browser.window.rowData.values():
            if row.kind == "header":
                continue
            if row.kind == "item":
                rows.append(("item", row.id, row.slot, bool(row.bis), row.gap))
            elif row.kind == "note":
                rows.append(("note", None, row.slot, None, None))
            else:
                rows.append(("enchant", row.enchant.id, row.key, bool(row.bis), None))
        return rows

    @staticmethod
    def frames(game) -> list:
        """The row frames in use, top to bottom, without the slot headers."""
        window = game.ns.Browser.window
        return [window.rows[index] for index in range(1, len(window.rowData) + 1)
                if window.rowData[index].kind != "header"]

    @staticmethod
    def all_frames(game) -> list:
        """Every row frame in use, headers included."""
        window = game.ns.Browser.window
        return [window.rows[index] for index in range(1, len(window.rowData) + 1)]

    def open(self, **options) -> Game:
        game = Game(**options)
        game.ns.Browser.Open()
        return game

    # -- opening ------------------------------------------------------------------------------

    def test_opens_on_the_players_class(self):
        game = self.open(cls="MAGE")
        window, state = game.ns.Browser.window, game.ns.Browser.state
        self.assertTrue(window.shown)
        self.assertEqual((state["class"], state.spec, state.list, state.tab), ("MAGE", 1, "pve", "items"))
        self.assertEqual(self.shown_rows(game), self.reference_rows("MAGE", 1, "pve"))
        self.assertEqual(label(window.spec), "Mage Arcane")
        self.assertIn("EasyBISWindow", list(game.lua.globals().UISpecialFrames.values()), "Escape will not close it")
        self.assertIn("ForeverDB.net", window.credit.text)
        self.assertIn(self.db.meta["build"], window.credit.text)

    def test_every_spec_and_list_shows_the_generators_rows(self):
        game = self.open()
        state = game.ns.Browser.state
        for token in test_addon.CLASSES:
            for spec in self.kept[token]:
                for mode in ladders.MODES:
                    state["class"], state.spec, state.list = token, spec, mode
                    game.ns.SetOption(game.ns, "minimap", not game.ns.db.minimap)  # any option change refreshes
                    self.assertEqual(self.shown_rows(game), self.reference_rows(token, spec, mode),
                                     f"{token} {spec} {mode}")

    def test_remembers_the_last_spec_and_list(self):
        game = self.open(saved="EasyBISCharDB = { class = 'ROGUE', spec = 2, list = 'pvp' }")
        state = game.ns.Browser.state
        self.assertEqual((state["class"], state.spec, state.list), ("ROGUE", 2, "pvp"))
        self.assertEqual(self.shown_rows(game), self.reference_rows("ROGUE", 2, "pvp"))

    def test_bad_saved_choice_falls_back(self):
        game = self.open(cls="DRUID", saved="EasyBISCharDB = { class = 'DEATHKNIGHT', spec = 9, list = 'arena' }")
        state = game.ns.Browser.state
        self.assertEqual((state["class"], state.spec, state.list), ("WARRIOR", 1, "pve"))

    def test_slash_command_opens_and_closes(self):
        game = Game()
        game.slash("")
        self.assertTrue(game.ns.Browser.window.shown)
        game.slash("")
        self.assertFalse(game.ns.Browser.window.shown)

    # -- what a row says --------------------------------------------------------------------

    def test_item_row_texts(self):
        game = Game(saved=ENHANCEMENT)
        game.stub.itemNames[DRAGONSCALE_HELM] = "Black Dragonscale Helm"
        game.stub.itemNames[EYE_OF_REND] = "Eye of Rend"
        game.ns.Browser.Open()
        row = self.frames(game)[0]
        # one line: name, score bar and rank, type, then a picture and the words for where it comes from
        self.assertEqual(row.name.text, "|cffa335eeBlack Dragonscale Helm|r",
                         "the name wears the quality color, and nothing else")
        self.assertEqual(strip_colors(row.rank.text), "BIS")
        self.assertTrue(row.bar.shown)
        self.assertEqual(row.bar.width, BAR, "the best pick's bar is full")
        self.assertEqual(row.sub.text, "Mail", "the header names the slot, the row says the item's type")
        self.assertEqual(row.sourceIcon.texture, "Interface\\Icons\\Trade_LeatherWorking", "a craft: its profession")
        self.assertFalse(row.kind.shown, "on one line the picture stands for the category")
        self.assertEqual(strip_colors(row.detail.text), "Leatherworking (300)")
        self.assertEqual(row.height, ONE_LINE)
        self.assertFalse(row.remove.shown)

        second = self.frames(game)[1]
        self.assertEqual(second.name.text, "|cffa335eeEye of Rend|r")
        self.assertRegex(strip_colors(second.rank.text), r"^-\d+%$")
        self.assertLess(second.bar.width, BAR, "an alternative's bar is shorter")
        self.assertEqual(second.sourceIcon.texture, "Interface\\TargetingFrame\\UI-RaidTargetingIcon_8")
        self.assertEqual(strip_colors(second.detail.text), "Warchief Rend Blackhand - Blackrock Spire (15%)",
                         "a drop counted in Forever wears no sign")
        third = self.frames(game)[2]
        self.assertEqual(strip_colors(third.name.text), "Backwood Helm")
        self.assertEqual(third.sub.text, "", "the item type is not known before the game loads the item")

        # what was seen or counted in Forever or read in its files wears no sign
        for frame in self.frames(game):
            if frame.data.kind == "item" and frame.data.source.origin in ("f", "s", "w"):
                self.assertNotIn("*", strip_colors(frame.detail.text))
                self.assertNotIn("Forever", strip_colors(frame.detail.text))

        # on two lines the category is written next to its picture
        game.ns.SetOption(game.ns, "compact", False)
        self.assertEqual(row.height, ROW)
        self.assertTrue(row.kind.shown)
        self.assertEqual(strip_colors(row.kind.text), "Crafted")
        self.assertEqual(strip_colors(row.rank.text), "BIS")
        self.assertEqual(strip_colors(second.kind.text), "Dungeon")
        self.assertEqual(second.detail.text, "Warchief Rend Blackhand - Blackrock Spire (15%)")

    def test_rows_use_larger_fonts(self):
        """A row's texts are the game's own fonts made larger, so the list reads at a glance."""
        game = Game(saved=ENHANCEMENT)
        game.ns.Browser.Open()
        fonts = game.lua.globals()

        def size(text):
            return fonts[text.fontObject].fontSize

        row = self.frames(game)[0]
        self.assertEqual((size(row.name), size(row.sub), size(row.rank), size(row.detail), size(row.header)),
                         (14, 12, 12, 12, 18))
        self.assertEqual(fonts[row.name.fontObject].fontFile, fonts.GameFontNormal.fontFile, "the game's own face")
        self.assertGreater(size(row.name), fonts.GameFontNormal.fontSize)
        self.assertGreater(size(row.detail), fonts.GameFontHighlightSmall.fontSize)
        self.assertGreater(size(row.header), fonts.GameFontNormalLarge.fontSize)
        self.assertEqual((row.icon.width, row.icon.height), (30, 30), "the picture grows with the row")
        game.ns.SetOption(game.ns, "compact", False)
        self.assertEqual((row.icon.width, row.icon.height), (44, 44))

        # a client without CreateFont keeps the game's fonts
        old = Game(saved="CreateFont = nil; " + ENHANCEMENT)
        old.ns.Browser.Open()
        row = self.frames(old)[0]
        self.assertEqual((row.name.fontObject, row.detail.fontObject), ("GameFontNormal", "GameFontHighlightSmall"))

    def test_item_types(self):
        """Necklaces, rings and trinkets have no type worth a word; a two-hander says it once on one line."""
        game = Game(cls="MAGE", saved=FIRE_MAGE)
        game.ns.SetPhase(game.ns, EVERYTHING)
        game.stub.itemNames[ATIESH] = "Atiesh"
        game.stub.itemTypes[ATIESH] = game.lua.table("Staves", "INVTYPE_2HWEAPON", 2, 10)
        game.ns.Browser.Open()
        rows = {frame.data.id: frame for frame in self.frames(game) if frame.data.kind == "item"}
        self.assertEqual(rows[ATIESH].sub.text, "Staves")
        neck = next(frame for frame in self.frames(game) if frame.data.slot == "neck")
        game.stub.itemNames[neck.data.id] = "A necklace"
        game.stub.itemTypes[neck.data.id] = game.lua.table("Miscellaneous", "INVTYPE_NECK", 4, 0)
        cloak = next(frame for frame in self.frames(game) if frame.data.slot == "back")
        game.stub.itemNames[cloak.data.id] = "A cloak"
        game.stub.itemTypes[cloak.data.id] = game.lua.table("Miscellaneous", "INVTYPE_CLOAK", 4, 0)
        game.ns.SetOption(game.ns, "compact", False)
        self.assertEqual(rows[ATIESH].sub.text, "Two-Hand - Staves")
        self.assertEqual(neck.sub.text, "")
        self.assertEqual(cloak.sub.text, "", "the armor type Miscellaneous says nothing, whatever the slot")

    def test_a_score_that_is_no_full_measure_shows_nothing(self):
        """An alternative the simulator could not measure in full keeps its place: no bar, no figure, no word."""
        game = self.open(saved=ENHANCEMENT)
        game.ns.SetOption(game.ns, "altCount", 6)
        tooltip = game.lua.globals().GameTooltip
        frames = [frame for frame in self.frames(game) if frame.data.kind == "item"]
        guessed = [frame for frame in frames if frame.data.estimated]
        self.assertTrue(guessed, "no alternative of the list has an estimated score")
        for frame in guessed:
            self.assertEqual((frame.rank.text, frame.bar.shown, frame.barBack.shown), ("", False, False))
            self.assertFalse(frame.data.bis)
            self.assertIsNone(frame.data.gap)
            game.stub.run(frame, "OnEnter")
            said = [strip_colors(line[1]) for line in tooltip.lines.values()]
            self.assertFalse(any("Score" in line or "Estimated" in line for line in said), said)
        measured = next(frame for frame in frames if not frame.data.estimated and not frame.data.bis and not frame.data.tie)
        self.assertRegex(strip_colors(measured.rank.text), r"^(-\d+%|<1%)$")
        self.assertTrue(measured.bar.shown)

    def test_a_slot_header_says_what_a_score_is(self):
        """Over the scores of each item slot, a mark whose tooltip says how the list is ranked."""
        game = self.open(saved=ENHANCEMENT)
        window, tooltip, state = game.ns.Browser.window, game.lua.globals().GameTooltip, game.ns.Browser.state
        headers = [frame for frame in self.all_frames(game) if frame.data.kind == "header"]
        self.assertTrue(headers and all(frame.info.shown for frame in headers), "a slot's header has no mark")
        self.assertFalse(any(frame.info.shown for frame in self.frames(game)), "the mark is the headers' own")
        mark = headers[0].info
        self.assertEqual((mark.text.text, mark.icon.texture), ("Score", "Interface\\FriendsFrame\\InformationIcon"))
        self.assertEqual(mark.points[1][4], 318, "over the bars of the rows on one line")

        def said():
            game.stub.run(mark, "OnEnter")
            return tooltip.text, [line[1] for line in tooltip.lines.values() if line[1] != " "]

        title, lines = said()
        self.assertEqual(title, "How this list is ranked")
        self.assertEqual(lines, [
            "Score: the damage per second the item adds, measured with the Forever simulator.",
            "Simulated fight: a raid boss, 3 minutes, one target, with raid buffs and debuffs, consumables, "
            "and the spec's default talents and rotation.",
            "The % is the gap to the best item of the slot, not a gap in total damage. Less than 1% apart, two items "
            "are as good as each other."])
        self.assertEqual((tooltip.points[1][1], tooltip.points[1][2].name), ("TOPLEFT", "EasyBISWindow"))
        game.stub.run(mark, "OnLeave")
        self.assertFalse(tooltip.shown)

        weights = ["Score: the item's stats, each weighted for this spec.", "The % is the gap to the best item of the slot."]
        state.list = "pvp"   # the PvP list is ranked on the weights
        self.assertEqual(said()[1], weights)
        state.list, state.spec = "pve", 3   # ... and so is a healer's PvE list
        self.assertEqual(said()[1], weights)

        game.ns.SetOption(game.ns, "compact", False)   # on two lines the bars sit further right, and the mark with them
        headers = [frame for frame in self.all_frames(game) if frame.data.kind == "header"]
        self.assertEqual(headers[0].info.points[1][4], 392)

    def test_the_mark_speaks_french(self):
        game = self.open(saved=ENHANCEMENT, locale="frFR")
        lines = game.ns.Browser.ScoreInfo("SHAMAN", 2, "pve")
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[2], "Combat simulé : un boss de raid, 3 minutes, une cible, avec les buffs et debuffs de "
                                   "raid, les consommables, et les talents et la rotation par défaut de la spécialisation.")
        pvp = game.ns.Browser.ScoreInfo("SHAMAN", 2, "pvp")
        self.assertEqual((len(pvp), pvp[1]), (2, "Score : les stats de l'objet, chacune pondérée pour cette spécialisation."))

    def test_rows_are_grouped_by_slot(self):
        """A header before each slot's rows, taller rows after it, nothing overlapping."""
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        data = list(window.rowData.values())
        reference = self.reference_rows("SHAMAN", 2, "pve")
        slots_in_order = list(dict.fromkeys(row[2] for row in reference))
        headers = [row for row in data if row.kind == "header"]
        self.assertEqual([row.group for row in headers], slots_in_order)
        self.assertEqual(headers[0].text, "Head")
        self.assertEqual(len(data), len(reference) + len(slots_in_order))
        self.assertEqual(data[0].kind, "header", "the list starts with a header")
        current = None
        for row in data:
            if row.kind == "header":
                current = row.group
            else:
                self.assertEqual(row.slot, current, "a row sits under another slot's header")

        offset = 0
        for frame in self.all_frames(game):
            header, note = frame.data.kind == "header", frame.data.kind == "note"
            self.assertEqual(frame.points[1][5], -offset)
            self.assertEqual(frame.height, HEADER if header else NOTE if note else ONE_LINE)
            self.assertEqual(frame.header.shown, header)
            self.assertEqual(frame.note.shown, note)
            self.assertEqual(frame.icon.shown, not (header or note))
            self.assertEqual(frame.name.shown, not (header or note))
            if header:
                self.assertEqual(frame.header.text, game.ns.SlotName(frame.data.group))
            offset += frame.height
        self.assertEqual(window.child.height, offset)

        # a frame that was a header is reused as an item row when the list changes
        open_dropdown(game, window.slot.button)
        find(game.stub.menu, "Legs").pick()
        kinds = [frame.data.kind for frame in self.all_frames(game)]
        self.assertEqual(kinds, ["header", "item", "item", "item"])
        self.assertTrue(self.all_frames(game)[1].icon.shown)
        self.assertFalse(self.all_frames(game)[1].header.shown)

    def test_enchants_are_grouped_by_slot(self):
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[2], "OnClick")
        data = list(window.rowData.values())
        headers = [row.text for row in data if row.kind == "header"]
        keys = list(dict.fromkeys(row.key for row in data if row.kind == "enchant"))
        self.assertEqual(headers, [game.ns.Enchants.KeyName(key) for key in keys])
        self.assertIn("Two-handed weapon", headers)
        self.assertEqual(data[0].kind, "header")

    def test_two_hander_note(self):
        game = self.open(saved=ENHANCEMENT)
        notes = [frame for frame in self.frames(game) if frame.data.kind == "note"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].note.text, "none, the two-hander wins")
        frames = self.all_frames(game)
        position = next(index for index, frame in enumerate(frames) if frame.data.kind == "note")
        self.assertEqual(frames[position - 1].data.kind, "header")
        self.assertEqual(frames[position - 1].header.text, "Off hand")

    def test_both_weapon_styles_are_listed(self):
        game = Game(cls="MAGE", saved=FIRE_MAGE + " " + WITH_PVP)   # the Mageblade is a PvP reward
        game.stub.itemNames[MAGEBLADE] = "Grand Marshal's Mageblade"
        game.stub.itemTypes[MAGEBLADE] = game.lua.table("One-Handed Swords", "INVTYPE_WEAPON")
        game.ns.Browser.Open()
        window = game.ns.Browser.window

        def rows_of(slot):
            return [frame for frame in self.all_frames(game) if frame.data.slot == slot]

        # before the raids a one-hander and an off hand are best: the two-handers follow, under a note
        main = rows_of("main")
        self.assertEqual([frame.data.kind for frame in main], ["item"] * 3 + ["note"] + ["item"] * 3)
        self.assertEqual(main[0].data.id, MAGEBLADE)
        self.assertEqual(main[0].sub.text, "One-Hand - One-Handed Swords")
        self.assertEqual(main[3].note.text, "Or a two-hander")
        self.assertFalse(main[3].icon.shown)
        self.assertEqual([bool(frame.data.other) for frame in main if frame.data.kind == "item"],
                         [False] * 3 + [True] * 3)
        for frame in main[4:]:
            self.assertFalse(frame.data.bis)
            self.assertRegex(strip_colors(frame.rank.text), r"^(-\d+%|<1%|Tied)$")
            self.assertLessEqual(frame.data.gap, 0)
        self.assertEqual([frame.data.kind for frame in rows_of("off")], ["item"] * 3)

        # with everything the data holds a staff is best: the one-handers and their off hands follow
        game.ns.SetPhase(game.ns, EVERYTHING)
        main, off = rows_of("main"), rows_of("off")
        self.assertEqual(main[0].data.id, ATIESH)
        self.assertEqual([frame.data.kind for frame in main], ["item"] * 3 + ["note"] + ["item"] * 3)
        self.assertEqual(main[3].note.text, "Or a one-hander with an off hand")
        self.assertEqual({main[4].data.id, main[5].data.id}, {MAGEBLADE, VAULTED_SECRETS},
                         "the two best one-handers once every raid counts, within a rounding of each other")
        self.assertEqual(off[0].note.text, "With a one-hander, in place of the two-hander")
        self.assertEqual([frame.data.kind for frame in off], ["note"] + ["item"] * 3)
        self.assertTrue(all(frame.data.other and not frame.data.bis for frame in off[1:]))
        # the best one-hander and the best off hand make one set: the same gap behind the staff
        self.assertEqual(main[4].data.gap, off[1].data.gap)
        self.assertLess(main[4].data.gap, 0)
        self.assertEqual(self.shown_rows(game),
                         self.reference_rows("MAGE", 2, "pve", default_filter(phase=EVERYTHING, pvp=True)))

        # a source filter keeps the items and drops the notes
        game.ns.Browser.state.source = "quest"
        game.ns.SetOption(game.ns, "minimap", False)
        self.assertTrue(all(row.kind != "note" for row in window.rowData.values()))

    def test_row_tooltip_and_link(self):
        game = Game(saved=ENHANCEMENT)
        game.stub.itemNames[DRAGONSCALE_HELM] = "Black Dragonscale Helm"
        game.ns.Browser.Open()
        row, tooltip = self.frames(game)[0], game.lua.globals().GameTooltip
        compare = game.lua.globals().ShoppingTooltip1
        game.stub.run(row, "OnEnter")
        self.assertEqual(tooltip.item, DRAGONSCALE_HELM)
        self.assertTrue(tooltip.shown)
        self.assertFalse(compare.shown, "the comparison with the gear worn waits for Shift")
        game.stub.shift = True
        game.stub.fire("MODIFIER_STATE_CHANGED", "LSHIFT", 1)
        self.assertTrue(compare.shown)
        game.stub.shift = False
        game.stub.fire("MODIFIER_STATE_CHANGED", "LSHIFT", 0)
        self.assertFalse(compare.shown)
        game.stub.shift = True
        game.stub.run(row, "OnLeave")
        game.stub.run(row, "OnEnter")
        self.assertTrue(compare.shown, "Shift already held: the comparison comes with the tooltip")
        game.stub.shift = False
        compare.Show(compare)
        game.stub.run(tooltip, "OnUpdate")
        self.assertFalse(compare.shown, "the game setting it again does not last")
        game.stub.run(row, "OnLeave")
        self.assertFalse(tooltip.shown)
        compare.Show(compare)
        game.stub.fire("MODIFIER_STATE_CHANGED", "LSHIFT", 0)
        game.stub.run(tooltip, "OnUpdate")
        self.assertTrue(compare.shown, "another addon's tooltip keeps its comparison")
        compare.Hide(compare)

        game.stub.run(row, "OnClick")
        self.assertIsNone(game.stub.linked, "a plain click must not link the item")
        game.stub.modifier = True
        game.stub.run(row, "OnClick")
        self.assertIn(f"item:{DRAGONSCALE_HELM}", game.stub.linked)

    def test_names_arrive_later(self):
        game = self.open(saved=ENHANCEMENT)
        row = self.frames(game)[0]
        self.assertEqual(strip_colors(row.name.text), "Black Dragonscale Helm")   # the data's English name
        game.stub.itemNames[DRAGONSCALE_HELM] = "Heaume en écailles de dragon noir"
        game.stub.fire("GET_ITEM_INFO_RECEIVED", DRAGONSCALE_HELM, True)
        game.stub.fire("GET_ITEM_INFO_RECEIVED", DRAGONSCALE_HELM, True)
        while game.stub.runTimers():
            pass
        self.assertEqual(strip_colors(row.name.text), "Heaume en écailles de dragon noir")
        game.ns.Browser.Close()
        game.stub.itemNames[DRAGONSCALE_HELM] = "Helm"
        game.stub.fire("GET_ITEM_INFO_RECEIVED", DRAGONSCALE_HELM, True)
        self.assertEqual(game.stub.runTimers(), 0, "a closed window keeps listening")

    # -- filters ------------------------------------------------------------------------------

    def test_spec_menu(self):
        game = self.open(cls="SHAMAN")
        window, state = game.ns.Browser.window, game.ns.Browser.state
        open_dropdown(game, window.spec.button)
        menu = game.stub.menu
        self.assertEqual(texts(menu)[0], "Shaman", "the player's class comes first")
        self.assertEqual(len(texts(menu)), 9)
        self.assertEqual(texts(find(menu, "Shaman")), ["Elemental", "Enhancement", "Restoration"])
        self.assertTrue(find(find(menu, "Shaman"), "Elemental").selected())

        fury = find(find(menu, "Warrior"), "Fury")
        fury.pick()
        self.assertEqual((state["class"], state.spec), ("WARRIOR", 2))
        self.assertTrue(fury.selected())
        self.assertEqual(label(window.spec), "Warrior Fury")
        self.assertEqual(self.shown_rows(game), self.reference_rows("WARRIOR", 2, "pve"))
        saved = game.lua.globals().EasyBISCharDB
        self.assertEqual((saved["class"], saved.spec, saved.list), ("WARRIOR", 2, "pve"))

    def test_list_buttons(self):
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        game.stub.run(window.list.buttons[2], "OnClick")
        self.assertEqual(game.ns.Browser.state.list, "pvp")
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pvp"))
        self.assertEqual(game.lua.globals().EasyBISCharDB.list, "pvp")

    def test_phase_filter(self):
        game = self.open(cls="MAGE", saved=FIRE_MAGE)
        window = game.ns.Browser.window
        self.assertEqual(window.phase.label.text, "Phase")
        self.assertEqual(label(window.phase), "Pre-raid")
        self.assertNotIn(ATIESH, [row[1] for row in self.shown_rows(game)])

        open_dropdown(game, window.phase.button)
        menu = game.stub.menu
        self.assertEqual(texts(menu), ["Pre-raid", "Phase 1", "Everything, Classic raids included"])
        self.assertTrue(find(menu, "Pre-raid").selected())
        find(menu, "Everything").pick()
        self.assertTrue(find(menu, "Everything").selected())
        self.assertEqual(label(window.phase), "Everything")
        self.assertEqual(game.lua.globals().EasyBISCharDB.phase, EVERYTHING)
        self.assertEqual(self.shown_rows(game), self.reference_rows("MAGE", 2, "pve", default_filter(phase=EVERYTHING)))
        self.assertIn(ATIESH, [row[1] for row in self.shown_rows(game)])

        find(menu, "Phase 1").pick()
        self.assertEqual(label(window.phase), "Phase 1")
        self.assertEqual(self.shown_rows(game), self.reference_rows("MAGE", 2, "pve", default_filter(phase=1)))
        self.assertNotIn(ATIESH, [row[1] for row in self.shown_rows(game)])

        # the choice comes back with the character
        again = self.open(cls="MAGE", saved="EasyBISCharDB = { class = 'MAGE', spec = 2, list = 'pve', phase = 9 }")
        self.assertEqual(label(again.ns.Browser.window.phase), "Everything")
        self.assertIn(ATIESH, [row[1] for row in self.shown_rows(again)])

    def test_every_phase_shows_the_generators_rows(self):
        game = self.open()
        state = game.ns.Browser.state
        for phase in phases.PHASES:
            game.ns.SetPhase(game.ns, phase)
            for token in test_addon.CLASSES:
                for spec in self.kept[token]:
                    for mode in ladders.MODES:
                        state["class"], state.spec, state.list = token, spec, mode
                        game.ns.SetOption(game.ns, "minimap", not game.ns.db.minimap)
                        self.assertEqual(self.shown_rows(game),
                                         self.reference_rows(token, spec, mode, default_filter(phase=phase)),
                                         f"{token} {spec} {mode} phase {phase}")

    def test_slot_filter(self):
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        open_dropdown(game, window.slot.button)
        self.assertEqual(texts(game.stub.menu)[:3], ["All", "Head", "Neck"])
        self.assertEqual(len(texts(game.stub.menu)), 16)
        find(game.stub.menu, "Finger").pick()
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve", only_slot="finger"))
        self.assertEqual(len(self.shown_rows(game)), 3, "the best ring and two picks after it, the second ring one of them")
        self.assertEqual(label(window.slot), "Finger")
        self.assertEqual(look(window.slot), "active", "a filter that narrows the list is gold")
        self.assertEqual(look(window.source), "idle")
        self.assertEqual(look(window.spec), "idle", "the spec and the phase always have a value: never gold")
        find(game.stub.menu, "All").pick()
        self.assertEqual(look(window.slot), "idle")
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve"))

    def test_source_and_zone_filters(self):
        game = self.open(saved=ENHANCEMENT)
        window, state = game.ns.Browser.window, game.ns.Browser.state
        everything = self.shown_rows(game)

        open_dropdown(game, window.source.button)
        offered = texts(game.stub.menu)
        self.assertEqual(offered[0], "All")
        self.assertIn("Dungeon", offered)
        self.assertIn("Crafted", offered)
        find(game.stub.menu, "Crafted").pick()
        rows = [row for row in window.rowData.values() if row.kind == "item"]
        self.assertTrue(rows)
        self.assertTrue(all(row.source.category == "crafted" for row in rows))
        self.assertLess(len(rows), len(everything))
        self.assertEqual(label(window.source), "Crafted")
        self.assertIn("|T", find(game.stub.menu, "Crafted").text, "the menu shows each category's picture")
        find(game.stub.menu, "All").pick()

        open_dropdown(game, window.zone.button)
        zones = texts(game.stub.menu)
        self.assertEqual(zones[0], "All")
        self.assertIn("Blackrock Spire", zones)
        self.assertEqual(zones[1:], sorted(zones[1:]))
        find(game.stub.menu, "Blackrock Spire").pick()
        rows = [row for row in window.rowData.values() if row.kind == "item"]
        self.assertTrue(rows)
        self.assertTrue(all(row.source.zone == "Blackrock Spire" for row in rows))
        self.assertIn(EYE_OF_REND, [row.id for row in rows])

        # another spec may not have that zone: the filter goes back to "all"
        state["class"], state.spec = "PRIEST", 2
        state.zone = "A zone nobody has"
        game.ns.SetOption(game.ns, "minimap", False)
        self.assertIsNone(state.zone)
        self.assertEqual(self.shown_rows(game), self.reference_rows("PRIEST", 2, "pve"))

    def test_nothing_to_show(self):
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        self.assertFalse(window.empty.shown)
        game.ns.SetOption(game.ns, "seenOnly", True)
        find_slot = "ranged"   # an Enhancement Shaman has no ranged pick
        game.ns.Browser.state.slot = find_slot
        game.ns.SetOption(game.ns, "seenOnly", False)
        self.assertEqual(len(window.rowData), 0)
        self.assertTrue(window.empty.shown)
        self.assertEqual(window.empty.text, "Nothing matches these filters.")

    # -- enchants -----------------------------------------------------------------------------

    def test_enchants_tab(self):
        import luaout
        game = self.open(saved=ENHANCEMENT)
        window = game.ns.Browser.window
        ladder = luaout.enchant_ladders(self.db, "SHAMAN", 2, self.kept["SHAMAN"][2])
        best = luaout.best_enchants(ladder, phases.CURRENT)
        wanted = next(enchant for enchant in best["chest"][1:] if enchant.startswith("s"))
        game.stub.spellNames[int(wanted[1:])] = "A chest enchant"
        game.stub.run(window.tabs.buttons[2], "OnClick")
        rows = self.shown_rows(game)
        self.assertEqual(len(rows), sum(len(ids) for ids in best.values()))
        self.assertTrue(all(row[0] == "enchant" for row in rows))
        chest = [row for row in rows if row[2] == "chest"]
        self.assertEqual([row[1] for row in chest], best["chest"])
        self.assertEqual([row[3] for row in chest], [True] + [False] * (len(chest) - 1))
        # the two lists, the item sources and adding an item do not apply; the phase does
        for control in (window.list, window.listLabel, window.source, window.zone, window.add):
            self.assertFalse(control.shown)
        self.assertTrue(window.slot.shown)
        self.assertTrue(window.phase.shown)

        frames = {frame.data.enchant.id: frame for frame in self.frames(game)}
        spell = frames[wanted]
        self.assertEqual(spell.name.text, "A chest enchant")
        self.assertEqual(strip_colors(spell.rank.text), "Alt")
        self.assertFalse(spell.bar.shown, "an enchant has no score: only the best one gets a bar")
        self.assertEqual(spell.height, ROW, "an enchant always takes two lines")
        self.assertEqual(spell.sub.text, self.db.enchant_info[wanted][1])
        self.assertTrue(strip_colors(spell.kind.text).startswith("Enchanting ("))
        first = frames[best["chest"][0]]
        self.assertEqual(strip_colors(first.rank.text), "BIS")
        self.assertTrue(first.bar.shown)
        game.stub.run(spell, "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertEqual(tooltip.spell, int(wanted[1:]))
        self.assertGreater(len(tooltip.lines), 1, "the effect and the source are added to the tooltip")

        open_dropdown(game, window.slot.button)
        find(game.stub.menu, "Main hand").pick()
        self.assertEqual({row[2] for row in self.shown_rows(game)}, {"w2h"},
                         "a spec that fights with a two-hander is not shown one-hander or shield enchants")

        game.stub.run(window.tabs.buttons[1], "OnClick")
        self.assertTrue(window.source.shown)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve", only_slot="main"))

    def test_enchants_follow_the_phase(self):
        import luaout
        game = self.open(cls="HUNTER", saved="EasyBISCharDB = { class = 'HUNTER', spec = 2, list = 'pve' }")
        window = game.ns.Browser.window
        ladder = luaout.enchant_ladders(self.db, "HUNTER", 2, self.kept["HUNTER"][2])
        game.stub.run(window.tabs.buttons[2], "OnClick")
        for phase in phases.PHASES:
            game.ns.SetPhase(game.ns, phase)
            best = luaout.best_enchants(ladder, phase)
            rows = self.shown_rows(game)
            self.assertEqual([row[1] for row in rows],
                             [enchant for key in game.ns.Enchants.KEYS.values() for enchant in best.get(key, [])],
                             f"phase {phase}")
        before = luaout.best_enchants(ladder, phases.PRE_RAID)
        self.assertNotIn("i23548", [e for ids in before.values() for e in ids], "Might of the Scourge needs Naxxramas")
        self.assertIn("i23548", luaout.best_enchants(ladder, EVERYTHING)["shoulder"])
        # a hunter carries no shield and holds nothing in the off hand
        keys = {row[2] for row in self.shown_rows(game)}
        self.assertFalse(keys & {"shield", "held"})
        self.assertIn("rng", keys)

    def test_enchant_sources_in_a_few_words(self):
        game = Game()
        info, kind, detail = game.ns.Enchants.Info, game.ns.Enchants.Kind, game.ns.Enchants.Detail
        cloak = info("s1219587")
        self.assertEqual((kind(cloak), detail(cloak)),
                         ("Enchanting (300)", "Formula sold by Alynsia (Redridge Mountains), or a scroll"))
        boots = info("s20023")
        self.assertEqual(detail(boots), "Formula drops in Stratholme, or a scroll")
        strength = info("s1248668")
        self.assertEqual(detail(strength), "Formula, source unknown")
        kit = info("i15564")
        self.assertEqual((kind(kit), detail(kit)), ("Leatherworking (225)", "Taught by trainers"))
        scroll = info("i273593")   # a scroll new in Forever: neither ForeverDB nor QuestieDB says where it is from
        self.assertEqual((kind(scroll), detail(scroll)), ("Item to apply", "Unknown source"))
        self.assertEqual(game.ns.Enchants.Category(scroll), "unknown")
        self.assertEqual(game.ns.Enchants.Where(scroll), "where it comes from isn't known yet")
        self.assertEqual((game.ns.Enchants.Category(cloak), game.ns.Enchants.Category(kit)), ("crafted", "crafted"))
        self.assertEqual(game.ns.Enchants.Where(kit), "Leatherworking 225: from a trainer")
        # the items to apply that a quest or a boss gives: the source read in QuestieDB, said as an item's is
        arcanum = info("i18331")
        self.assertEqual((kind(arcanum), detail(arcanum), arcanum.origin),
                         ("Quest", "Libram of Protection - Dire Maul", "t"))
        self.assertEqual(game.ns.Enchants.Category(arcanum), "quest")
        self.assertEqual(game.ns.Enchants.Where(arcanum), "Source: Quest - Libram of Protection - Dire Maul")
        voracity = info("i11645")
        self.assertEqual((kind(voracity), detail(voracity)), ("Quest", "Libram of Voracity"))
        scourge = info("i23548")
        self.assertEqual((kind(scourge), detail(scourge)), ("Raid", "Sapphiron"))
        self.assertEqual(game.ns.Sources.Icon(game.ns.Enchants.Category(scourge)), game.ns.Sources.Icon("raid"))
        # every sentence of the data is one this reads
        for enchant, fields in self.db.enchant_info.items():
            record = info(enchant)
            if record is None:
                continue   # not among the enchants the addon lists
            read = (record.trainer or record.recipe or record.category
                    or fields[2] == "where it comes from isn't known yet")
            self.assertTrue(read, f"{enchant}: {fields[2]!r} is a sentence Enchants.lua does not read")
            if fields[3] == "t":
                self.assertIsNotNone(record.category, f"{enchant}: {fields[2]!r}")
                self.assertNotEqual(game.ns.Sources.CategoryName(record.category), "SRC_" + record.category)
        # the row of the window: the quest's picture, its name, and the sign of a source not confirmed in Forever
        import luaout
        cls, spec = next((cls, spec) for cls in test_addon.CLASSES for spec in self.kept[cls]
                         if luaout.best_enchants(luaout.enchant_ladders(self.db, cls, spec, self.kept[cls][spec]),
                                                 phases.CURRENT).get("head", [""])[0] == "i18331")
        shown = self.open(cls=cls, saved=f"EasyBISCharDB = {{ class = '{cls}', spec = {spec}, list = 'pve' }}")
        shown.stub.run(shown.ns.Browser.window.tabs.buttons[2], "OnClick")
        row = {frame.data.enchant.id: frame for frame in self.frames(shown)}["i18331"]
        self.assertEqual((strip_colors(row.kind.text), row.detail.text), ("Quest *", "Libram of Protection - Dire Maul"))
        self.assertEqual(row.sourceIcon.texture, "Interface\\GossipFrame\\AvailableQuestIcon")
        shown.stub.run(row, "OnEnter")
        lines = [strip_colors(line[1]) for line in shown.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Source: Quest - Libram of Protection - Dire Maul", lines)
        self.assertIn("* Source from Questie's database, not confirmed in Forever.", lines)

        french = Game(locale="frFR")
        cloak = french.ns.Enchants.Info("s1219587")
        self.assertEqual(french.ns.Enchants.Kind(cloak), "Enchantement (300)")
        self.assertEqual(french.ns.Enchants.Detail(cloak),
                         "Formule : en vente chez Alynsia (Redridge Mountains), ou un parchemin")
        arcanum = french.ns.Enchants.Info("i18331")
        self.assertEqual((french.ns.Enchants.Kind(arcanum), french.ns.Enchants.Detail(arcanum)),
                         ("Quête", "Libram of Protection - Dire Maul"))
        self.assertEqual(french.ns.Enchants.Where(arcanum), "Provenance : Quête - Libram of Protection - Dire Maul")
        self.assertEqual(french.ns.Sources.OriginRemark("t"),
                         "* Provenance d'après la base de données de Questie, non confirmée dans Forever.")

    # -- options ------------------------------------------------------------------------------

    def test_alternatives_switch(self):
        game = self.open(cls="MAGE", saved=FIRE_MAGE)
        window = game.ns.Browser.window
        self.assertEqual(look(window.alts), "lit")
        game.stub.run(window.alts, "OnClick")
        self.assertFalse(game.ns.db.listAlts)
        self.assertEqual(look(window.alts), "idle")
        self.assertEqual(self.shown_rows(game), self.reference_rows("MAGE", 2, "pve", alts=False))
        self.assertTrue(all(row[3] for row in self.shown_rows(game)), "only best picks are left")
        # the enchants follow the switch
        game.stub.run(window.tabs.buttons[2], "OnClick")
        self.assertTrue(all(row[3] for row in self.shown_rows(game)))
        game.stub.run(window.alts, "OnClick")
        self.assertTrue(game.ns.db.listAlts)
        self.assertFalse(all(row[3] for row in self.shown_rows(game)))
        # the choice comes back
        again = self.open(saved="EasyBISDB = { listAlts = false }; " + ENHANCEMENT)
        self.assertEqual(self.shown_rows(again), self.reference_rows("SHAMAN", 2, "pve", alts=False))
        self.assertEqual(len([row for row in self.shown_rows(again) if row[0] == "note"]), 1,
                         "the off hand still says the two-hander wins")

    def test_available_now_checkbox(self):
        game = self.open(saved="EasyBISCharDB = { class = 'PRIEST', spec = 3, list = 'pvp', phase = 9 }")
        window = game.ns.Browser.window
        box = window.available
        self.assertEqual(box.text.text, "Available now")
        self.assertFalse(box.GetChecked(box))
        self.assertTrue(window.phase.button.IsEnabled(window.phase.button))
        # the filters fill their row: the box sits in the title bar, over the window's border and title
        self.assertEqual((box.points[1][1], box.points[1][2].name, box.points[1][3]),
                         ("TOPRIGHT", window.name, "TOPRIGHT"))
        self.assertGreater(box.GetFrameLevel(box), window.NineSlice.GetFrameLevel(window.NineSlice),
                           "under the border, its title bar hides the box")
        self.assertGreater(box.GetFrameLevel(box), window.TitleContainer.GetFrameLevel(window.TitleContainer))
        controls = [window.spec, window.list, window.phase, window.slot, window.source, window.zone]
        right = 66 + sum(control.width for control in controls) + 8 * 5
        self.assertLessEqual(right, WIDTH - 8, "the filters stay inside the window")
        chosen = label(window.phase)
        self.assertEqual(self.shown_rows(game), self.reference_rows("PRIEST", 3, "pvp", default_filter(phase=EVERYTHING)))

        game.stub.run(box, "OnClick")
        self.assertTrue(game.ns.db.availableNow)
        self.assertTrue(box.GetChecked(box))
        self.assertEqual(self.shown_rows(game), self.reference_rows("PRIEST", 3, "pvp",
                                                                    ("a", False, False, phases.CURRENT, True, 6)))
        self.assertEqual(label(window.phase), game.ns.PhaseName(phases.CURRENT))
        self.assertFalse(window.phase.button.IsEnabled(window.phase.button))
        game.stub.menu = None
        open_dropdown(game, window.phase.button)
        self.assertIsNone(game.stub.menu, "only the game's phase is available now")

        game.stub.run(box, "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertTrue(tooltip.shown)
        self.assertIn("rank 6", tooltip.lines[1][1])
        game.stub.run(box, "OnLeave")
        self.assertFalse(tooltip.shown)

        game.stub.run(box, "OnClick")
        self.assertFalse(box.GetChecked(box))
        self.assertTrue(window.phase.button.IsEnabled(window.phase.button))
        self.assertEqual(label(window.phase), chosen, "the phase the character picked comes back")

    def test_options_menu(self):
        game = self.open(saved="EasyBISCharDB = { class = 'SHAMAN', spec = 2, list = 'pvp' }")
        window = game.ns.Browser.window
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pvp"))
        open_dropdown(game, window.options)
        menu = game.stub.menu
        self.assertEqual(texts(menu), ["Options", "BIS lines in item tooltips", "Tooltips show my class only",
                                       "Tooltips show alternatives too", "Reputation needed in item tooltips",
                                       "Items with no known source",
                                       "Only items seen in Forever", "PvP rewards", "Alternatives per slot",
                                       "Faction", "Compact rows", "Short reputation lines", "Minimap button",
                                       "Auction house tab"])
        tooltips = find(menu, "BIS lines")
        self.assertTrue(tooltips.selected())
        tooltips.pick()
        self.assertFalse(game.ns.db.tooltip)
        self.assertEqual(game.tooltip(EYE_OF_REND), [])
        tooltips.pick()
        unsourced = find(menu, "no known source")
        self.assertFalse(unsourced.selected())
        unsourced.pick()
        self.assertTrue(unsourced.selected())
        self.assertTrue(game.ns.db.unsourced)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pvp", default_filter(unsourced=True)))
        # the PvP rewards: a submenu with a box per list. The PvP list counts them and the PvE list leaves
        # them out until the player says otherwise; the rows follow at once, whichever list the window shows
        rewards = find(menu, "PvP rewards")
        self.assertEqual(rewards.kind, "button")
        self.assertEqual(texts(rewards), ["PvE list", "PvP list"])
        in_pve, in_pvp = find(rewards, "PvE list"), find(rewards, "PvP list")
        self.assertEqual((in_pve.kind, bool(in_pve.selected()), bool(in_pvp.selected())), ("checkbox", False, True))
        with_them = self.reference_rows("SHAMAN", 2, "pvp", default_filter(unsourced=True, pvp=True))
        self.assertEqual(self.shown_rows(game), with_them)
        in_pvp.pick()
        self.assertFalse(in_pvp.selected())
        self.assertEqual(dict(game.ns.db.pvpRewards), {"pve": False, "pvp": False})
        without = self.reference_rows("SHAMAN", 2, "pvp", default_filter(unsourced=True, pvp=False))
        self.assertEqual(self.shown_rows(game), without)
        self.assertNotEqual(without, with_them)
        in_pve.pick()   # the other list's box: the PvP list the window shows has not moved
        self.assertTrue(in_pve.selected())
        self.assertEqual(dict(game.ns.db.pvpRewards), {"pve": True, "pvp": False})
        self.assertEqual(self.shown_rows(game), without)
        in_pve.pick()
        in_pvp.pick()
        self.assertEqual(self.shown_rows(game), with_them)
        # a window on a PvE list follows the PvE box
        other = self.open(cls="WARRIOR", saved="EasyBISCharDB = { class = 'WARRIOR', spec = 3, list = 'pve' }")
        open_dropdown(other, other.ns.Browser.window.options)
        box = find(find(other.stub.menu, "PvP rewards"), "PvE list")
        left_out = self.reference_rows("WARRIOR", 3, "pve")
        self.assertEqual(self.shown_rows(other), left_out)
        box.pick()
        self.assertTrue(box.selected())
        self.assertEqual(dict(other.ns.db.pvpRewards), {"pve": True, "pvp": True})
        counted = self.reference_rows("WARRIOR", 3, "pve", default_filter(pvp=True))
        self.assertEqual(self.shown_rows(other), counted)
        self.assertNotEqual(counted, left_out)
        # how many alternatives a slot lists: a submenu, from two to six, the rows following at once
        counts = find(menu, "Alternatives per slot")
        self.assertEqual(counts.kind, "button")
        self.assertEqual(texts(counts), ["2", "3", "4", "5", "6"])
        self.assertEqual([bool(item.selected()) for item in counts["items"].values()], [True, False, False, False, False])
        find(counts, "5").pick()
        self.assertEqual(game.ns.db.altCount, 5)
        self.assertTrue(find(counts, "5").selected())
        self.assertFalse(find(counts, "2").selected())
        five = self.reference_rows("SHAMAN", 2, "pvp", default_filter(unsourced=True, pvp=True), count=5)
        self.assertEqual(self.shown_rows(game), five)
        self.assertGreater(len(five), len(with_them))
        # the faction the lists are for: the character's, or the other one; the title says when it is not its own
        sides = find(menu, "Faction")
        self.assertEqual(sides.kind, "button")
        self.assertEqual(texts(sides), ["Alliance (my character)", "Horde"])
        self.assertEqual([bool(item.selected()) for item in sides["items"].values()], [True, False])
        self.assertEqual(window.titleShown, "Easy BIS")
        find(sides, "Horde").pick()
        self.assertEqual(game.ns.char.side, "h")
        self.assertTrue(find(sides, "Horde").selected())
        horde = self.reference_rows("SHAMAN", 2, "pvp", default_filter("h", unsourced=True, pvp=True), count=5)
        self.assertEqual(self.shown_rows(game), horde)
        self.assertNotEqual(horde, five)
        self.assertEqual(window.titleShown, "Easy BIS - Horde lists")
        find(sides, "Alliance (my character)").pick()
        self.assertIsNone(game.ns.char.side)
        self.assertEqual(self.shown_rows(game), five)
        self.assertEqual(window.titleShown, "Easy BIS")
        french = Game(locale="frFR")
        french.ns.Browser.Open()
        open_dropdown(french, french.ns.Browser.window.options)
        self.assertEqual(texts(find(french.stub.menu, "Récompenses JcJ")), ["Liste JcE", "Liste JcJ"])
        self.assertEqual(texts(find(french.stub.menu, "Faction")), ["Alliance (mon personnage)", "Horde"])
        find(find(french.stub.menu, "Faction"), "Horde").pick()
        self.assertEqual(french.ns.Browser.window.titleShown, "Easy BIS - listes Horde")
        self.assertEqual(french.ns.L.OPT_ALT_COUNT, "Alternatives par emplacement")

    def test_minimap_button(self):
        game = Game()
        button = game.lua.globals().EasyBISMinimapButton
        self.assertIsNotNone(button, "no minimap button after login")
        self.assertTrue(button.shown)
        game.stub.run(button, "OnClick")
        self.assertTrue(game.ns.Browser.window.shown)
        game.stub.run(button, "OnClick")
        self.assertFalse(game.ns.Browser.window.shown)
        game.stub.run(button, "OnEnter")
        self.assertEqual(game.lua.globals().GameTooltip.text, "Easy BIS")

        game.ns.SetOption(game.ns, "minimap", False)
        self.assertFalse(button.shown)
        hidden = Game(saved="EasyBISDB = { minimap = false }")
        self.assertIsNone(hidden.lua.globals().EasyBISMinimapButton, "the button was made although it is switched off")

    def test_addon_menu_entry(self):
        game = Game()
        game.lua.globals().EasyBIS_OnCompartmentClick()
        self.assertTrue(game.ns.Browser.window.shown)
        game.lua.globals().EasyBIS_OnCompartmentEnter(None, game.lua.globals().UIParent)
        self.assertEqual(game.lua.globals().GameTooltip.text, "Easy BIS")
        game.lua.globals().EasyBIS_OnCompartmentLeave()

    # -- sources ------------------------------------------------------------------------------

    def test_sources_in_words(self):
        game = Game()
        describe, line = game.ns.Sources.Describe, game.ns.Sources.Line
        eye = describe(EYE_OF_REND)
        self.assertEqual((eye.category, eye.detail, eye.zone, eye.percent, eye.origin),
                         ("dungeon", "Warchief Rend Blackhand", "Blackrock Spire", "15%", "w"))
        tunic = describe(TIMBERMAW_TUNIC)
        self.assertEqual((tunic.category, line(tunic), tunic.origin), ("crafted", "Leatherworking (300)", "f"))
        rank = describe(GRAND_MARSHALS_SUNDERER)
        self.assertEqual((rank.category, line(rank)), ("pvp", "Rank 14"))
        unknown = describe(GENERALS_GREAVES)
        self.assertEqual((unknown.category, line(unknown)), ("unknown", ""))
        pauldrons = describe(271955)   # sold by a vendor the data only knows by its number
        self.assertEqual((pauldrons.category, pauldrons.detail, line(pauldrons)), ("vendor", "", "Map 1413"))
        uther = describe(11302)   # a world epic the data knows two bosses for: a world drop, not Onyxia's
        self.assertEqual((uther.category, line(uther), uther.origin), ("world", "", "k"))
        self.assertEqual(game.ns.Sources.Short(uther), "World drop")
        self.assertEqual(game.ns.Sources.CategoryName("unknown"), "Unknown source")
        self.assertEqual(game.ns.Sources.OriginName("k"), "Classic data")
        self.assertEqual(game.ns.Sources.OriginMark("k"), "*")
        self.assertEqual(game.ns.Sources.OriginRemark("k"), "* Source from Classic's data, not confirmed in Forever.")
        self.assertEqual((game.ns.Sources.OriginMark("s"), game.ns.Sources.OriginRemark("s")), ("", None))
        self.assertEqual((game.ns.Sources.OriginMark("w"), game.ns.Sources.OriginRemark("w")), ("", None))
        # a source read in QuestieDB wears the sign Classic's data does, and says where it is from
        self.assertEqual(game.ns.Sources.OriginName("t"), "Questie's data")
        self.assertEqual(game.ns.Sources.OriginMark("t"), "*")
        self.assertEqual(game.ns.Sources.OriginRemark("t"), "* Source from Questie's database, not confirmed in Forever.")
        sash = describe(226772)   # a set piece sold in Ironforge and in Orgrimmar: the vendor of the player's side
        self.assertEqual((sash.category, sash.detail, sash.zone, sash.origin), ("vendor", "Deliana", "Map 1455", "t"))
        sash = Game(faction="Horde").ns.Sources.Describe(226772)
        self.assertEqual((sash.category, sash.detail, sash.zone), ("vendor", "Mokvar", "Map 1454"))
        # a picture per category; a crafted item gets its profession's
        self.assertEqual(game.ns.Sources.Icon("vendor"), ("Interface\\GossipFrame\\VendorGossipIcon", False))
        self.assertEqual(game.ns.Sources.Icon(tunic.category, tunic.profession),
                         ("Interface\\Icons\\Trade_LeatherWorking", True))
        self.assertEqual(game.ns.Sources.Icon("something new"), game.ns.Sources.Icon("unknown"))
        for category in game.ns.Sources.CATEGORIES.values():
            self.assertTrue(game.ns.Sources.Icon(category)[0].startswith("Interface\\"), category)
            self.assertNotEqual(game.ns.Sources.CategoryName(category), "SRC_" + category)
        self.assertEqual(game.ns.Sources.OriginName("c"), "Clue, unconfirmed")
        for letter in ("s", "f", "w", ""):
            self.assertIsNone(game.ns.Sources.OriginName(letter), f"origin {letter!r} needs no remark")

    def test_every_listed_item_can_be_described(self):
        import luaout
        game = Game()
        categories = set(game.ns.Sources.CATEGORIES.values())
        seen = set()
        for item_id in luaout.shown_ids(self.kept):
            source = game.ns.Sources.Describe(item_id)
            self.assertIn(source.category, categories, f"item {item_id}")
            self.assertIsInstance(game.ns.Sources.Line(source), str)
            seen.add(source.category)
        self.assertGreaterEqual(len(seen), 10, f"only {sorted(seen)} were met")

    def test_sources_in_french(self):
        game = Game(locale="frFR")
        game.stub.zoneNames[229] = "Pic Rochenoire"
        eye = game.ns.Sources.Describe(EYE_OF_REND)
        self.assertEqual(game.ns.Sources.Line(eye), "Warchief Rend Blackhand - Pic Rochenoire (15 %)")
        self.assertEqual(game.ns.Sources.CategoryName(eye.category), "Donjon")
        self.assertEqual(game.ns.Sources.Line(game.ns.Sources.Describe(TIMBERMAW_TUNIC)), "Travail du cuir (300)")
        game.ns.Browser.Open()
        self.assertEqual(game.ns.Browser.window.slot.label.text, "Emplacement")
        self.assertEqual(game.ns.Browser.window.empty.text, "Rien ne correspond à ces filtres.")

    # -- ties, the tooltip's place, the window's height ---------------------------------------

    def a_tie(self) -> tuple:
        """(class, spec, slot, item): the first alternative of the PvE lists that scores exactly as its
        slot's best pick. Weapons, rings and trinkets are left out: their best picks are sets."""
        for token in test_addon.CLASSES:
            for spec, modes in self.kept[token].items():
                for slot, _ in ladders.SLOTS:
                    if slot in ("main", "off") or slot in ladders.PAIRED:
                        continue
                    visible = [e for e in modes["pve"][slot] if e.passes(for_list(default_filter(), "pve"))]
                    if len(visible) > 1 and visible[0].stored == visible[1].stored:
                        return token, spec, slot, visible[1].shown("a")
        self.fail("no tie in the PvE lists: this test needs another example")

    def test_ties_read_as_equals(self):
        """An alternative that scores exactly as the best pick is its equal, in the window and in tooltips."""
        token, spec, slot, item_id = self.a_tie()
        game = self.open(cls=token, saved=f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}")
        row = next(frame for frame in self.frames(game) if frame.data.kind == "item" and frame.data.id == item_id)
        self.assertTrue(row.data.tie)
        self.assertFalse(row.data.bis)
        self.assertEqual(strip_colors(row.rank.text), "Tied")
        self.assertEqual(row.bar.width, BAR)
        name = self.db.classes[token]["specs"][spec]["name"]   # another spec of the class may want it less
        mine = [right for left, right in game.lines(item_id) if token.capitalize() in left and name in left]
        self.assertTrue(mine and all("BIS" in right for right in mine), "a tie is as good as the best in tooltips")

    def a_placed_item(self) -> tuple:
        """(class, spec, slot, item, prepare): an alternative a PvE list shows, with six alternatives asked for,
        that the data placed from a close spec's simulation (flag e). Weapons are left out: their lists are weighed
        first. Once the simulator has measured every spec the data places nothing: the last alternative of a list is
        then flagged e in the data the game loads (prepare), as the generator writes a placement."""
        flt = for_list(default_filter(), "pve")
        stand_in = None
        for token in test_addon.CLASSES:
            for spec, modes in self.kept[token].items():
                for slot, _ in ladders.SLOTS:
                    if slot in ("main", "off"):
                        continue
                    visible = [e for e in modes["pve"][slot] if e.passes(flt)]
                    _, alternatives = ladders.picks(slot, visible, ladders.MAX_ALTERNATIVES)
                    placed = next((e for e in alternatives if e.placed), None)
                    if placed:
                        return token, spec, slot, placed.shown("a"), None
                    if alternatives and not stand_in and alternatives[-1].shown("a"):
                        stand_in = token, spec, slot, alternatives[-1]
        self.assertIsNotNone(stand_in, "no alternative in the PvE lists")
        token, spec, slot, entry = stand_in
        token_text = luaout.encode_entry(entry)
        flagged = luaout.encode_entry(dataclasses.replace(entry, placed=True))

        def prepare(ns):
            head = f"L\t{spec}\tpve\t{slot}\t"
            lines = ns.data.lists[token].split("\n")
            hits = [i for i, line in enumerate(lines) if line.startswith(head)]
            self.assertEqual(len(hits), 1, head)
            tokens = lines[hits[0]][len(head):].split(" ")
            self.assertIn(token_text, tokens)
            tokens[tokens.index(token_text)] = flagged
            lines[hits[0]] = head + " ".join(tokens)
            ns.data.lists[token] = "\n".join(lines)
        return token, spec, slot, entry.shown("a"), prepare

    def test_a_placed_item_has_no_score(self):
        """An item placed from a close spec's simulation reads Estimated, with no bar and no figure."""
        token, spec, slot, item_id, prepare = self.a_placed_item()
        game = self.open(cls=token, prepare=prepare, saved=f"EasyBISDB = {{ altCount = {ladders.MAX_ALTERNATIVES} }} "
                                          f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}")
        row = next(frame for frame in self.frames(game) if frame.data.kind == "item" and frame.data.id == item_id)
        self.assertTrue(row.data.placed)
        self.assertFalse(row.data.bis)
        self.assertIsNone(row.data.gap)
        self.assertIsNone(row.data.ratio)
        self.assertEqual(strip_colors(row.rank.text), "Estimated")
        self.assertFalse(row.bar.shown, "no score, no bar")
        game.stub.run(row, "OnEnter")
        lines = [strip_colors(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn(game.ns.L.TIP_PLACED, lines)
        score = game.ns.L.TIP_SCORE.split("%")[0]
        self.assertFalse(any(line.startswith(score) for line in lines), "no score in its tooltip either")

    def test_tooltip_opens_beside_the_window(self):
        game = Game(saved=ENHANCEMENT)
        game.stub.itemNames[EYE_OF_REND] = "Eye of Rend"
        game.ns.Browser.Open()
        window, tooltip = game.ns.Browser.window, game.lua.globals().GameTooltip
        rows = self.frames(game)
        game.stub.run(rows[0], "OnEnter")
        self.assertEqual(tooltip.anchor, "ANCHOR_NONE")
        self.assertEqual((tooltip.points[1][1], tooltip.points[1][2].name, tooltip.points[1][3]),
                         ("TOPLEFT", "EasyBISWindow", "TOPRIGHT"))
        first = (tooltip.points[1][4], tooltip.points[1][5])
        game.stub.run(rows[5], "OnEnter")
        self.assertEqual((tooltip.points[1][4], tooltip.points[1][5]), first, "it does not move from row to row")
        self.assertEqual(len(tooltip.points), 1)
        # no room on the right: it opens on the left
        game.lua.globals().UIParent.right, window.right = 1600, 1500
        game.stub.run(rows[0], "OnEnter")
        self.assertEqual((tooltip.points[1][1], tooltip.points[1][3]), ("TOPRIGHT", "TOPLEFT"))
        # what the row shortens is in the tooltip in full
        game.stub.run(rows[1], "OnEnter")
        lines = [strip_colors(line[1]) for line in tooltip.lines.values()]
        self.assertIn("Source: Dungeon - Warchief Rend Blackhand - Blackrock Spire (15%)", lines)
        self.assertNotIn("* Source from Classic's data, not confirmed in Forever.", lines)
        self.assertTrue(any(re.match(r"Score for this slot: \d+% of the best pick's\.", line) for line in lines), lines)

    def test_window_height_is_kept(self):
        game = self.open()
        window = game.ns.Browser.window
        self.assertEqual((window.width, window.height), (WIDTH, 620))
        self.assertIsNotNone(window.grip)
        window.height = 803.6
        game.stub.run(window.grip, "OnMouseUp")
        self.assertEqual(game.lua.globals().EasyBISDB.windowHeight, 804)
        again = self.open(saved="EasyBISDB = { windowHeight = 804 }")
        self.assertEqual((again.ns.Browser.window.width, again.ns.Browser.window.height), (WIDTH, 804))
        tiny = self.open(saved="EasyBISDB = { windowHeight = 12 }")
        self.assertEqual(tiny.ns.Browser.window.height, 620, "a height too small to use is not restored")

    def test_notice_under_the_filters(self):
        """A known problem awaits its fix: a band says so between the filters and the list, on every page."""
        for locale, word in (("enUS", "weapons"), ("frFR", "armes")):
            game = self.open(locale=locale)
            window = game.ns.Browser.window
            notice = window.notice
            self.assertEqual(plain(notice.text.text), game.ns.L.NOTICE_WEAPONS, locale)
            self.assertIn(word, notice.text.text, locale)
            self.assertEqual((notice.points[1][1], notice.points[2][1]), ("TOPLEFT", "TOPRIGHT"), "across the window")
            top, list_top = -notice.points[1][3], -window.inset.points[1][3]
            self.assertGreaterEqual(top, 70, "under the filters")
            self.assertLessEqual(top + notice.height, list_top, "over the list, which starts lower")
            for tab in window.tabs.buttons.values():
                game.stub.run(tab, "OnClick")
                self.assertTrue(notice.shown)
            game.stub.run(window.pages.buttons[2], "OnClick")
            self.assertTrue(notice.shown, "on the dungeons too")

    def test_the_notices_cross_puts_it_away_until_the_window_opens_again(self):
        game = self.open(saved=ENHANCEMENT)
        window, tooltip = game.ns.Browser.window, game.lua.globals().GameTooltip
        notice, cross = window.notice, window.notice.close
        list_top = lambda: -window.inset.points[1][3]
        self.assertEqual((notice.shown, list_top()), (True, 98))
        rows_before = len(window.rowData)
        game.stub.run(cross, "OnEnter")
        self.assertEqual(tooltip.text, "Hide this notice. It comes back the next time the window is opened.")
        game.stub.run(cross, "OnClick")
        self.assertEqual((notice.shown, list_top()), (False, 70), "the list takes the room of the notice")
        self.assertEqual(len(window.inset.points), 2, "the list is anchored once")
        self.assertEqual(len(window.rowData), rows_before)
        for tab in window.tabs.buttons.values():   # it stays away from tab to tab
            game.stub.run(tab, "OnClick")
            self.assertFalse(notice.shown)
        game.ns.Browser.Close()
        game.ns.Browser.Open()
        self.assertEqual((notice.shown, list_top()), (True, 98), "back when the window opens again")
        game.stub.run(cross, "OnClick")
        game.ns.Browser.Toggle()
        game.ns.Browser.Toggle()
        self.assertTrue(notice.shown)

    # -- items added by hand --------------------------------------------------------------------

    def test_add_an_item_by_hand(self):
        crown, blade, potion = 990001, 990002, 990003
        game = Game(saved=ENHANCEMENT)
        stub = game.stub
        stub.equipLocs[crown], stub.itemNames[crown] = "INVTYPE_HEAD", "Crown of Tests"
        stub.equipLocs[blade], stub.itemNames[blade] = "INVTYPE_WEAPON", "Blade of Tests"
        stub.equipLocs[potion], stub.itemNames[potion] = "", "Potion of Tests"
        stub.equipLocs[EYE_OF_REND] = "INVTYPE_HEAD"
        game.ns.Browser.Open()
        window, add = game.ns.Browser.window, game.ns.AddItem
        self.assertEqual(label(window.add), "+ Add an item")
        game.stub.run(window.add, "OnClick")
        dialog = add.dialog
        self.assertTrue(dialog.shown)
        self.assertEqual(dialog.target.text, "To the list of Shaman Enhancement, PvE")
        self.assertTrue(dialog.box.focused)

        # typed: an ID that does not exist, something that is not worn, an item the list already has
        dialog.box.text = "424242"
        game.stub.run(dialog.box, "OnEnterPressed")
        self.assertIn("No such item", dialog.result.text)
        self.assertFalse(add.Submit(str(potion))[0])
        self.assertIn("is not something to wear", dialog.result.text)
        self.assertFalse(add.Submit(str(EYE_OF_REND))[0])
        self.assertIn("is already in this list", dialog.result.text)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve"))

        # typed by name, with the button
        dialog.box.text = "Crown of Tests"
        game.stub.run(dialog.add, "OnClick")
        self.assertIn("added to Shaman Enhancement, PvE (Head)", strip_colors(dialog.result.text))
        self.assertEqual(dialog.box.text, "", "the box is emptied for the next item")
        self.assertEqual(game.lua.globals().EasyBISDB.custom["SHAMAN:2:pve"].head[1], crown)
        head = [frame for frame in self.frames(game) if frame.data.slot == "head"]
        self.assertEqual([frame.data.id for frame in head][-1], crown, "it comes after the slot's picks")
        row = head[-1]
        self.assertTrue(row.data.custom)
        self.assertEqual(strip_colors(row.rank.text), "Added")
        self.assertFalse(row.bar.shown, "an item added by hand has no score")
        self.assertTrue(row.remove.shown)
        self.assertEqual(row.data.source.category, "manual")
        self.assertEqual(row.detail.text, "Added by hand")
        self.assertFalse(add.Submit(str(crown))[0], "the same item twice")

        # a Shift-click anywhere while the box has the focus, then an item dropped on the dialog
        game.lua.globals().ChatEdit_InsertLink(f"|cffa335ee|Hitem:{blade}::::::::60|h[Blade of Tests]|h|r")
        main = [frame.data.id for frame in self.frames(game) if frame.data.slot == "main"]
        self.assertEqual(main[-1], blade, "a one-handed weapon goes to the main hand")
        dialog.box.focused = False
        game.lua.globals().ChatEdit_InsertLink(f"|Hitem:{potion}|h[Potion of Tests]|h")
        self.assertIn("Blade of Tests", dialog.result.text, "a link is not for the dialog when its box has no focus")

        # the tooltip names the spec it was added for, and the Source filter knows the category
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "Added PvE"), game.lines(crown))
        open_dropdown(game, window.source.button)
        find(game.stub.menu, "Added by hand").pick()
        self.assertEqual({row[1] for row in self.shown_rows(game)}, {crown, blade})
        find(game.stub.menu, "All").pick()

        # the red button takes it out again
        game.stub.run(row.remove, "OnClick")
        self.assertNotIn(crown, [r[1] for r in self.shown_rows(game)])
        self.assertEqual(game.lines(crown), [])
        game.ns.Custom.Remove("SHAMAN", 2, "pve", blade)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve"))

        # dropped on the dialog; with the window on the off hand, a one-hander goes there
        game.ns.Browser.state.slot = "off"
        stub.cursor = game.lua.table("item", blade)
        game.stub.run(dialog, "OnReceiveDrag")
        self.assertIsNone(stub.cursor, "the item is put down")
        self.assertEqual(list(game.ns.Custom.List("SHAMAN", 2, "pve", "off").values()), [blade])
        self.assertEqual([r[1] for r in self.shown_rows(game) if r[0] == "item"], [blade])

        # another spec has its own list; the dialog follows the window, and closes with it
        game.ns.Browser.state.slot = None
        game.stub.run(window.list.buttons[2], "OnClick")
        self.assertEqual(dialog.target.text, "To the list of Shaman Enhancement, PvP")
        self.assertNotIn(blade, [r[1] for r in self.shown_rows(game)])
        game.ns.Browser.Close()
        self.assertFalse(dialog.shown)

    def test_shift_click_on_a_newer_client(self):
        """Where the game hands links to ChatFrameUtil.InsertLink, the dialog listens there."""
        game = Game(saved="ChatFrameUtil = { InsertLink = function() return false end }; " + ENHANCEMENT)
        game.stub.equipLocs[990001] = "INVTYPE_HEAD"
        game.ns.Browser.Open()
        game.stub.run(game.ns.Browser.window.add, "OnClick")
        game.lua.globals().ChatFrameUtil.InsertLink("|Hitem:990001|h[Crown of Tests]|h")
        self.assertEqual(list(game.ns.Custom.List("SHAMAN", 2, "pve", "head").values()), [990001])
        game.lua.globals().ChatEdit_InsertLink("|Hitem:990001|h[Crown of Tests]|h")
        self.assertNotIn("already", game.ns.AddItem.dialog.result.text, "the link was read twice")

    def test_add_an_item_by_name_search(self):
        legs, helm, shoulders, chest = 15052, 252605, 15051, 15050
        game = Game(saved=FIRE_MAGE)   # a list that does not have the helm
        stub = game.stub
        for item in (legs, helm, shoulders, chest):
            stub.equipLocs[item] = "INVTYPE_HEAD"
        game.ns.Browser.Open()
        stub.run(game.ns.Browser.window.add, "OnClick")
        dialog = game.ns.AddItem.dialog
        box, suggest = dialog.box, dialog.suggest
        self.assertFalse(suggest.shown)

        def type_text(text, typed=True):
            box.text = text
            stub.run(box, "OnTextChanged", typed)

        def names():
            return [strip_colors(row.name.text) for row in suggest.rows.values() if row.shown]

        def selected():
            return [i for i, row in enumerate(suggest.rows.values(), 1) if row.selected.shown]

        # a single letter, an ID or a text set by the addon asks for nothing
        for text in ("b", "15052"):
            type_text(text)
            self.assertFalse(suggest.shown, text)
        type_text("black dragonscale", typed=False)
        self.assertFalse(suggest.shown)

        # the names that start with the text, the highest required level first; the slot on the right
        type_text("Black Dragonscale")
        self.assertTrue(suggest.shown)
        self.assertEqual(names(), ["Black Dragonscale Leggings", "Black Dragonscale Helm",
                                   "Black Dragonscale Shoulders", "Black Dragonscale Breastplate"])
        self.assertEqual(suggest.rows[1].slot.text, "Head")
        self.assertTrue(suggest.rows[1].name.text.startswith("|cffffffff"), "white until the game has the item")
        stub.itemNames[legs] = "Black Dragonscale Leggings"
        stub.fire("GET_ITEM_INFO_RECEIVED", legs)
        self.assertTrue(suggest.rows[1].name.text.startswith("|cffa335ee"), "then in its quality's color")
        self.assertFalse(suggest.more.shown)
        self.assertEqual(selected(), [1], "the first one is chosen")

        # the arrows and Tab move the choice, round the list
        stub.run(box, "OnArrowPressed", "UP")
        self.assertEqual(selected(), [4])
        stub.run(box, "OnArrowPressed", "DOWN")
        stub.run(box, "OnTabPressed")
        self.assertEqual(selected(), [2])

        # Enter adds the one chosen, and the list goes away
        stub.run(box, "OnEnterPressed")
        self.assertIn("[Black Dragonscale Helm] added", strip_colors(dialog.result.text))
        self.assertFalse(suggest.shown)
        self.assertEqual(list(game.ns.Custom.List("MAGE", 2, "pve", "head").values()), [helm])

        # a click on a row adds it too; a word inside the name is found
        type_text("black dragonscale shoul")
        self.assertEqual(names(), ["Black Dragonscale Shoulders"])
        stub.run(suggest.rows[1], "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertEqual((tooltip.item, tooltip.shown), (shoulders, True))
        compare = game.lua.globals().ShoppingTooltip1
        self.assertFalse(compare.shown, "the comparison with the gear worn waits for Shift")
        stub.shift = True
        stub.fire("MODIFIER_STATE_CHANGED", "LSHIFT", 1)
        self.assertTrue(compare.shown)
        stub.shift = False
        stub.fire("MODIFIER_STATE_CHANGED", "LSHIFT", 0)
        self.assertFalse(compare.shown)
        stub.run(suggest.rows[1], "OnClick")
        self.assertIn(shoulders, list(game.ns.Custom.List("MAGE", 2, "pve", "head").values()))

        # more matches than rows: the line under them says how many more
        type_text("of the")
        self.assertEqual(len(names()), 8)
        self.assertTrue(suggest.more.shown)
        self.assertRegex(suggest.more.text, r"^and \d+ more")

        # Escape closes the list first, then the dialog
        stub.run(box, "OnEscapePressed")
        self.assertFalse(suggest.shown)
        self.assertTrue(dialog.shown)
        stub.run(box, "OnEscapePressed")
        self.assertFalse(dialog.shown)

    def test_name_search_twins_and_missing_items(self):
        classic, forever = 23464, 234551
        game = Game(saved=ENHANCEMENT)
        stub = game.stub
        stub.equipLocs[classic], stub.equipLocs[forever] = "INVTYPE_WEAPON", "INVTYPE_WEAPONMAINHAND"
        stub.itemNames[forever] = "High Warlord's Battle Mace"
        game.lua.globals().INVTYPE_WEAPONMAINHAND = "Main Hand"
        game.ns.Browser.Open()
        stub.run(game.ns.Browser.window.add, "OnClick")
        dialog = game.ns.AddItem.dialog
        box, suggest = dialog.box, dialog.suggest
        box.text = "high warlord's battle mace"
        stub.run(box, "OnTextChanged", True)
        rows = {row.id: row.slot.text for row in suggest.rows.values() if row.shown and row.id in (classic, forever)}
        # two items of one name: the item level once the game has it, the ID until then
        self.assertEqual(rows, {forever: "item level 60  Main Hand", classic: "ID 23464  One-Hand"})

        # the server has no such item: it leaves the list, and the next searches
        stub.fire("GET_ITEM_INFO_RECEIVED", classic, False)
        self.assertNotIn(classic, [row.id for row in suggest.rows.values() if row.shown])
        self.assertIn(("Main Hand"), [row.slot.text for row in suggest.rows.values() if row.id == forever],
                      "no twin left to tell apart")
        self.assertEqual(list(game.ns.Items.Find("battle mace")[0].values()).count(classic), 0)

    def test_name_search_in_the_games_language(self):
        """On a French game, the game's names count too, for the items the game already has."""
        game = Game(locale="frFR", saved="C_Item = { IsItemDataCachedByID = function(id) return id == 15052 end }; "
                    + ENHANCEMENT)
        game.stub.itemNames[15052] = "Jambières en écailles de dragon noir"
        find = game.ns.Items.Find
        self.assertEqual(list(find("jambières")[0].values()), [15052])
        self.assertEqual(list(find("Black Dragonscale Leg")[0].values()), [15052], "English names still count")

    def test_added_items_come_back(self):
        saved = "EasyBISDB = { custom = { ['SHAMAN:2:pve'] = { head = { 990001 }, junk = 4 }, other = 'x' } }; "
        game = Game(saved=saved + ENHANCEMENT)
        game.ns.Browser.Open()
        head = [frame for frame in self.frames(game) if frame.data.slot == "head"]
        self.assertEqual(head[-1].data.id, 990001)
        self.assertTrue(head[-1].data.custom)
        self.assertEqual(strip_colors(head[-1].name.text), "#990001", "an item the game has not loaded yet")
        self.assertIn(("<classicon-shaman> Shaman Enhancement", "Added PvE"), game.lines(990001))
        # with the alternatives switched off, the hand-added items stay
        game.ns.SetOption(game.ns, "listAlts", False)
        self.assertIn(990001, [frame.data.id for frame in self.frames(game) if frame.data.kind == "item"])

    # -- the character sheet --------------------------------------------------------------------

    SHEET = [("left", "head", 1), ("left", "neck", 1), ("left", "shoulder", 1), ("left", "back", 1),
             ("left", "chest", 1), ("left", "wrist", 1),
             ("right", "hands", 1), ("right", "waist", 1), ("right", "legs", 1), ("right", "feet", 1),
             ("right", "finger", 1), ("right", "finger", 2), ("right", "trinket", 1), ("right", "trinket", 2),
             ("bottom", "main", 1), ("bottom", "off", 1), ("bottom", "ranged", 1)]
    UNSEEN = ("neck", "finger", "trinket")   # what does not show on a character
    NO_MODEL = ("local make = CreateFrame; function CreateFrame(kind, ...) "
                "if kind == 'DressUpModel' then error('Unknown frame type') end return make(kind, ...) end")

    def reference_sheet(self, token, spec, mode, flt=None) -> list[tuple]:
        """(place, slot, rank, id) for every cell of the character sheet, from the generator's rules."""
        best = {}
        for kind, item_id, slot, bis, _ in self.reference_rows(token, spec, mode, flt, alts=False):
            if kind == "item" and bis:
                best.setdefault(slot, []).append(item_id)
        return [(place, slot, rank, (best.get(slot, []) + [None, None])[rank - 1])
                for place, slot, rank in self.SHEET]

    @staticmethod
    def sheet(game) -> list[tuple]:
        return [(cell.data.place, cell.data.slot, cell.data.rank, cell.data.id)
                for cell in game.ns.Character.view.cells.values()]

    def open_sheet(self, **options) -> tuple:
        """The game, and the cells of its character sheet by (slot, rank)."""
        game = self.open(**options)
        game.stub.run(game.ns.Browser.window.tabs.buttons[3], "OnClick")
        return game, {(cell.data.slot, cell.data.rank): cell for cell in game.ns.Character.view.cells.values()}

    def test_character_tab(self):
        game = Game(saved=ENHANCEMENT)
        game.stub.itemNames[DRAGONSCALE_HELM] = "Black Dragonscale Helm"
        game.ns.Browser.Open()
        window = game.ns.Browser.window
        self.assertEqual([label(button) for button in window.tabs.buttons.values()],
                         ["Items", "Enchants", "Character", "Consumables", "Reputations"])
        self.assertIsNone(game.ns.Character.view, "the sheet is made when it is first asked for")
        game.stub.run(window.tabs.buttons[3], "OnClick")
        view = game.ns.Character.view
        self.assertTrue(view.shown)
        self.assertFalse(window.scroll.shown)
        self.assertFalse(window.empty.shown)
        self.assertEqual(look(window.tabs.buttons[3]), "lit")
        # only the spec, the list and the phase apply
        for control in (window.spec, window.list, window.listLabel, window.phase):
            self.assertTrue(control.shown)
        for control in (window.slot, window.source, window.zone, window.add, window.alts):
            self.assertFalse(control.shown)
        self.assertEqual(strip_colors(view.title.text), "Shaman Enhancement")
        self.assertEqual(view.subtitle.text, "Level 60 PvE - Pre-raid")
        self.assertEqual(self.sheet(game), self.reference_sheet("SHAMAN", 2, "pve"))

        cells = list(view.cells.values())
        self.assertEqual(len(cells), 17)
        head = cells[0]
        self.assertEqual(head.name.text, "|cffa335eeBlack Dragonscale Helm|r", "the name wears the quality color")
        self.assertIn("Trade_BlackSmithing", head.where.text, "a picture says what kind of source it is")
        self.assertEqual(plain(head.where.text), "Leatherworking (300)", "where it comes from, in a few words")
        self.assertTrue(head.icon.shown)
        self.assertFalse(head.mirrored)
        self.assertEqual(head.points[1][1], "TOPLEFT")
        hands = cells[6]
        self.assertTrue(hands.mirrored, "the right column has its pictures on the outside, as in the game")
        self.assertEqual(hands.points[1][1], "TOPRIGHT")
        # an Enhancement Shaman's two-hander leaves the off hand empty, and its list has nothing at range
        off, ranged = cells[15], cells[16]
        self.assertTrue(off.data.twoHand)
        self.assertFalse(off.icon.shown)
        self.assertEqual((strip_colors(off.name.text), off.where.text), ("Off hand", "Taken by the two-hander"))
        self.assertIsNone(ranged.data.id)
        self.assertEqual((strip_colors(ranged.name.text), ranged.where.text), ("Ranged or relic", "Nothing listed"))

        # back to the list: the sheet goes, the rows and their filters come back
        game.stub.run(window.tabs.buttons[1], "OnClick")
        self.assertFalse(view.shown)
        self.assertTrue(window.scroll.shown)
        for control in (window.slot, window.source, window.zone, window.add, window.alts):
            self.assertTrue(control.shown)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve"))

    def test_character_sheet_of_every_spec(self):
        game = self.open()
        state = game.ns.Browser.state
        game.stub.run(game.ns.Browser.window.tabs.buttons[3], "OnClick")
        for phase in (phases.CURRENT, EVERYTHING):
            game.ns.SetPhase(game.ns, phase)
            for token in test_addon.CLASSES:
                for spec in self.kept[token]:
                    for mode in ladders.MODES:
                        state["class"], state.spec, state.list = token, spec, mode
                        game.ns.SetOption(game.ns, "minimap", not game.ns.db.minimap)
                        self.assertEqual(self.sheet(game),
                                         self.reference_sheet(token, spec, mode, default_filter(phase=phase)),
                                         f"{token} {spec} {mode} phase {phase}")

    def test_character_enchants(self):
        import luaout
        game, cells = self.open_sheet(saved=ENHANCEMENT)
        best = luaout.best_enchants(luaout.enchant_ladders(self.db, "SHAMAN", 2, self.kept["SHAMAN"][2]),
                                    phases.CURRENT)
        chest = cells[("chest", 1)]
        self.assertEqual(chest.data.enchant.id, best["chest"][0])
        self.assertTrue(chest.enchant.shown)
        self.assertTrue(chest.enchant.text.startswith("+ "))
        self.assertEqual(chest.name.points[1][5], -1, "three lines fill the cell")
        # a two-hander takes a two-hander's enchant; a belt, a ring and a trinket take none
        self.assertEqual(cells[("main", 1)].data.enchant.id, best["w2h"][0])
        for slot in ("waist", "finger", "trinket"):
            self.assertIsNone(cells[(slot, 1)].data.enchant)
            self.assertFalse(cells[(slot, 1)].enchant.shown)
        self.assertEqual(cells[("waist", 1)].name.points[1][5], -6, "two lines sit in the cell's middle")
        # the sheet follows the phase, as the Enchants tab does
        game.ns.SetPhase(game.ns, EVERYTHING)
        later = luaout.best_enchants(luaout.enchant_ladders(self.db, "SHAMAN", 2, self.kept["SHAMAN"][2]),
                                     EVERYTHING)
        for key in ("head", "shoulder", "chest", "legs"):
            enchant = cells[(key, 1)].data.enchant
            self.assertEqual(enchant.id if enchant else None, later.get(key, [None])[0], key)

        # a one-hander takes a one-hander's enchant; what the off hand takes depends on what it is
        mage, cells = self.open_sheet(cls="MAGE", saved=FIRE_MAGE)
        best = luaout.best_enchants(luaout.enchant_ladders(self.db, "MAGE", 2, self.kept["MAGE"][2]),
                                    phases.CURRENT)
        self.assertEqual(cells[("main", 1)].data.enchant.id, best["w1h"][0])
        off, wand = cells[("off", 1)], cells[("ranged", 1)]
        self.assertIsNone(off.data.enchant, "the game has not said what the item is yet")
        mage.stub.equipLocs[off.data.id] = "INVTYPE_HOLDABLE"
        mage.stub.equipLocs[wand.data.id] = "INVTYPE_RANGEDRIGHT"
        mage.stub.itemTypes[wand.data.id] = mage.lua.table("Wands", "INVTYPE_RANGEDRIGHT", 2, 19)
        mage.ns.SetOption(mage.ns, "minimap", False)
        self.assertEqual(off.data.enchant.id if off.data.enchant else None, best.get("held", [None])[0])
        self.assertIsNone(wand.data.enchant, "nothing goes on a wand")
        key = mage.ns.Enchants.KeyOf
        self.assertEqual(key("off", off.data.id, False), "held")
        self.assertIsNone(key("ranged", wand.data.id, False))
        mage.stub.itemTypes[wand.data.id] = mage.lua.table("Guns", "INVTYPE_RANGEDRIGHT", 2, 3)
        self.assertEqual(key("ranged", wand.data.id, False), "rng")
        self.assertEqual((key("main", 1, True), key("main", 1, False), key("legs", 1, False)), ("w2h", "w1h", "legs"))
        self.assertIsNone(key("off", 424242, False), "an item the game does not know")

        # an enchant's name, cut down to what sets it apart
        short = mage.ns.Enchants.ShortName
        record = mage.lua.table(kind="spell", number=990009, name="Enchant Chest - Greater Stats")
        self.assertEqual(short(record), "Greater Stats")
        mage.stub.spellNames[990009] = "Enchantement de plastron (Caractéristiques supérieures)"
        self.assertEqual(short(record), "Caractéristiques supérieures", "the game's name, in its language")
        self.assertEqual(short(mage.lua.table(kind="item", number=990010, name="Lesser Arcanum of Voracity")),
                         "Lesser Arcanum of Voracity")

    def test_character_ties(self):
        token, spec, slot, item_id = self.a_tie()
        saved = f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}"
        game, cells = self.open_sheet(cls=token, saved=saved)
        game.stub.itemNames[item_id] = "An equal"
        cell = cells[(slot, 1)]
        self.assertIn(item_id, list(cell.data.ties.values()))
        self.assertRegex(strip_colors(cell.name.text), r" \+\d$")
        game.stub.run(cell, "OnEnter")
        lines = [strip_colors(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertTrue(any(line.startswith("Tied with: ") and "An equal" in line for line in lines), lines)
        untied = next(c for c in cells.values() if c.data.id and len(c.data.ties) == 0)
        self.assertNotRegex(strip_colors(untied.name.text), r" \+\d$")

    def test_character_cell_tooltip_and_click(self):
        game = Game(saved=ENHANCEMENT)
        game.stub.itemNames[DRAGONSCALE_HELM] = "Black Dragonscale Helm"
        game.ns.Browser.Open()
        window, state, tooltip = game.ns.Browser.window, game.ns.Browser.state, game.lua.globals().GameTooltip
        game.stub.run(window.tabs.buttons[3], "OnClick")
        cells = list(game.ns.Character.view.cells.values())
        head, chest, ring, off = cells[0], cells[4], cells[10], cells[15]

        game.stub.run(head, "OnEnter")
        self.assertEqual(tooltip.item, DRAGONSCALE_HELM)
        self.assertTrue(tooltip.shown)
        self.assertEqual((tooltip.anchor, tooltip.points[1][2].name), ("ANCHOR_NONE", "EasyBISWindow"),
                         "the left column's opens beside the window, as a row's does")
        right = next(cell for cell in cells if cell.mirrored and cell.data.id)
        game.stub.run(right, "OnEnter")
        point = tooltip.points[1]
        same = game.lua.eval("rawequal")(point[2], right)
        self.assertEqual((point[1], same, point[3]), ("TOPRIGHT", True, "TOPLEFT"),
                         "the right column's opens on its left, over the model")
        self.assertFalse(game.lua.globals().ShoppingTooltip1.shown)
        game.stub.run(head, "OnEnter")
        lines = [strip_colors(line[1]) for line in tooltip.lines.values()]
        self.assertIn("Source: Crafted - Leatherworking (300)", lines)
        self.assertNotIn("* Source from Classic's data, not confirmed in Forever.", lines)
        self.assertEqual(lines[-1], "Click to see this slot's other picks.")
        self.assertFalse(any(line.startswith("Score for this slot") for line in lines))
        game.stub.run(chest, "OnEnter")
        lines = [strip_colors(line[1]) for line in tooltip.lines.values()]
        self.assertTrue(any(line.startswith("Enchant: ") for line in lines), lines)
        game.stub.run(off, "OnEnter")
        self.assertIsNone(tooltip.item)
        self.assertEqual(tooltip.text, "Off hand")
        self.assertEqual([line[1] for line in tooltip.lines.values()],
                         ["Taken by the two-hander", "Click to see this slot's other picks."])
        game.stub.run(off, "OnLeave")
        self.assertFalse(tooltip.shown)

        # Shift-click links the item and stays on the sheet; a plain click opens the slot's list
        game.stub.modifier = True
        game.stub.run(head, "OnClick")
        self.assertIn(f"item:{DRAGONSCALE_HELM}", game.stub.linked)
        self.assertEqual(state.tab, "character")
        game.stub.modifier = False
        game.stub.run(ring, "OnClick")
        self.assertEqual((state.tab, state.slot), ("items", "finger"))
        self.assertFalse(game.ns.Character.view.shown)
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve", only_slot="finger"))
        self.assertEqual(look(window.slot), "active")
        self.assertEqual(look(window.tabs.buttons[1]), "lit")
        # an empty slot opens its list too
        game.stub.run(window.tabs.buttons[3], "OnClick")
        game.stub.run(off, "OnClick")
        self.assertEqual((state.tab, state.slot), ("items", "off"))

    def test_character_model_wears_the_set(self):
        game, _ = self.open_sheet(saved=ENHANCEMENT)
        window, model = game.ns.Browser.window, game.ns.Character.view.model
        while game.stub.runTimers():
            pass
        self.assertEqual((model.kind, model.unit), ("DressUpModel", "player"))
        hands = {"main": "MAINHANDSLOT", "off": "SECONDARYHANDSLOT"}

        def worn(token, spec, mode):
            """The armour in the sheet's order, then the weapons: the off hand's before the main hand's."""
            shown = [(slot, item) for _, slot, _, item in self.reference_sheet(token, spec, mode)
                     if item and slot not in self.UNSEEN and slot != "ranged"]
            shown.sort(key=lambda pair: {"off": 1, "main": 2}.get(pair[0], 0))   # stable: the armour keeps its order
            return [(f"item:{item}", hands.get(slot)) for slot, item in shown]

        def tried():
            return [(entry[1], entry[2]) for entry in model.tried.values()]

        self.assertEqual(tried(), worn("SHAMAN", 2, "pve"), "what shows on a character, each weapon in its hand")
        self.assertEqual(model.undressed, 1, "the same set is not put on twice")
        game.ns.SetOption(game.ns, "minimap", False)
        self.assertEqual(model.undressed, 1)
        # an item the game has just loaded can be tried on at last
        game.stub.itemNames[DRAGONSCALE_HELM] = "Black Dragonscale Helm"
        game.stub.fire("GET_ITEM_INFO_RECEIVED", DRAGONSCALE_HELM, True)
        while game.stub.runTimers():
            pass
        self.assertEqual(model.undressed, 2)
        self.assertEqual(tried(), worn("SHAMAN", 2, "pve"))
        # another list, another set
        game.stub.run(window.list.buttons[2], "OnClick")
        self.assertEqual(model.undressed, 3)
        self.assertEqual(tried(), worn("SHAMAN", 2, "pvp"))
        # a model that was hidden is dressed again when it comes back
        game.stub.run(window.tabs.buttons[1], "OnClick")
        game.stub.run(window.tabs.buttons[3], "OnClick")
        self.assertEqual(model.undressed, 4)

        # dragging turns the character, and the turn outlives a change of set
        game.stub.cursorX = 100
        game.stub.run(model, "OnMouseDown", "LeftButton")
        game.stub.cursorX = 150
        game.stub.run(model, "OnUpdate")
        self.assertAlmostEqual(model.facing, 0.6)
        game.stub.mouseDown = False   # let go outside the model: the next move does not turn it
        game.stub.cursorX = 400
        game.stub.run(model, "OnUpdate")
        self.assertAlmostEqual(model.facing, 0.6)
        game.stub.run(window.list.buttons[1], "OnClick")
        self.assertAlmostEqual(model.facing, 0.6)

    def test_character_model_holds_what_the_class_fights_with(self):
        """The model holds the weapon tried on last, and a bow takes the melee weapons' place in its hands:
        a warrior is shown with the melee weapons, a hunter with the bow. The model is the player's own
        character, which without Dual Wield keeps one of two one-handers: the main hand's comes last."""
        for token, spec, at_range in (("WARRIOR", 2, False), ("HUNTER", 1, True)):
            game, _ = self.open_sheet(cls=token, saved=f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}")
            sheet = {slot: item for _, slot, rank, item in self.reference_sheet(token, spec, "pve") if rank == 1}
            self.assertTrue(sheet.get("ranged") and sheet.get("main"), f"{token}: a melee weapon and a ranged one")
            tried = [entry[1] for entry in game.ns.Character.view.model.tried.values()]
            main, ranged = f"item:{sheet['main']}", f"item:{sheet['ranged']}"
            weapons = [link for link in tried if link in (main, ranged) or link == f"item:{sheet.get('off')}"]
            if at_range:
                self.assertEqual(tried[-1], ranged, f"{token}: the ranged weapon is tried on last")
                self.assertEqual(tried[-2], main)
            else:
                self.assertNotIn(ranged, tried, f"{token}: the ranged weapon is not tried on")
                self.assertTrue(sheet.get("off"), f"{token}: two weapons")
                self.assertEqual(weapons, [f"item:{sheet['off']}", main], f"{token}: the off hand, then the main hand")
                self.assertEqual(tried[-1], main)

    def test_character_without_a_model(self):
        """A client that cannot make the model shows the class's icon; the cells are the same."""
        game, _ = self.open_sheet(cls="PRIEST", saved=self.NO_MODEL + "; " + ENHANCEMENT)
        view = game.ns.Character.view
        self.assertIsNone(view.model)
        self.assertTrue(view.crest.shown)
        self.assertEqual(self.sheet(game), self.reference_sheet("SHAMAN", 2, "pve"))
        game.lua.globals().CLASS_ICON_TCOORDS = None
        game.ns.SetOption(game.ns, "minimap", False)
        self.assertFalse(view.crest.shown, "no icon to show: the middle stays empty")

    def test_character_sheet_fits_the_window(self):
        game, _ = self.open_sheet(saved=ENHANCEMENT)
        window, view = game.ns.Browser.window, game.ns.Character.view
        cells = list(view.cells.values())
        # the notice under the filters takes 28 of the sheet's height (472 without it, a cell every 52)
        self.assertEqual((view.scale, view.width, view.height), (1, WIDTH - 32, 444))
        self.assertEqual([cells[index].points[1][5] for index in (0, 1, 5)], [0, -48, -240], "the left column")
        self.assertEqual([cells[index].points[1][5] for index in (6, 13)], [0, -336], "the right column")
        self.assertEqual([(cells[index].points[1][1], cells[index].points[1][4]) for index in (14, 15, 16)],
                         [("BOTTOMLEFT", 0), ("BOTTOMLEFT", 332), ("BOTTOMLEFT", 664)], "the weapons, under them")
        # a taller window gives the cells more air, up to a point
        window.height = 900
        game.stub.run(window.grip, "OnMouseUp")
        self.assertEqual((view.scale, view.height, cells[1].points[1][5]), (1, 724, -60))
        # too short for the sheet: it is drawn smaller, whole
        window.height = 380
        game.stub.run(window.grip, "OnMouseUp")
        self.assertAlmostEqual(view.scale, 204 / 424)
        self.assertEqual((view.height, cells[1].points[1][5]), (424, -46))

    def test_character_in_french(self):
        game, cells = self.open_sheet(locale="frFR", saved=ENHANCEMENT)
        self.assertEqual(label(game.ns.Browser.window.tabs.buttons[3]), "Personnage")
        self.assertEqual(game.ns.Character.view.subtitle.text, "Niveau 60 JcE - Pré-raid")
        self.assertEqual(cells[("off", 1)].where.text, "Prise par l'arme à deux mains")
        self.assertEqual(cells[("ranged", 1)].where.text, "Rien dans la liste")

    # -- a client without the newer frames and menus ---------------------------------------

    # -- reputations ---------------------------------------------------------------------------

    @staticmethod
    def earn(game, faction, reaction, value=0, low=0, high=3000):
        game.stub.factions[faction] = game.lua.table_from(
            {"reaction": reaction, "value": value, "low": low, "high": high, "name": f"Faction {faction}"})
        game.stub.fire("UPDATE_FACTION")
        game.stub.runTimers()

    @staticmethod
    def gated_rows(game) -> list:
        window = game.ns.Browser.window
        return [window.rows[index] for index in range(1, len(window.rowData) + 1)
                if window.rowData[index].reputation]

    def pvp_game(self, **options) -> Game:
        """A list where reputations stand in front of several pieces."""
        return self.open(saved="EasyBISCharDB = { class = 'WARRIOR', spec = 2, list = 'pvp' }", cls="WARRIOR", **options)

    def test_rows_say_what_a_reputation_asks(self):
        game = self.pvp_game()
        gated = self.gated_rows(game)
        self.assertTrue(gated)
        row = gated[0]
        requirement = row.data.reputation
        self.assertTrue(row.rep.shown and row.repState.shown)
        self.assertIn(game.ns.Reputation.StandingName(requirement.standing), row.rep.text)
        self.assertEqual(row.height, ONE_LINE, "a row on one line keeps its height")
        self.assertNotIn("|cffffd100", row.repState.text, "gold is for what is earned")
        # a row with no reputation says nothing of one
        free = next(frame for frame in self.frames(game) if frame.data.kind == "item" and not frame.data.reputation)
        self.assertFalse(free.rep.shown or free.repState.shown)
        # earned: the state turns gold, and the row follows the game without being asked
        self.earn(game, requirement.factionID, 8, 42000, 42000, 43000)
        row = next(frame for frame in self.gated_rows(game) if frame.data.id == row.data.id)
        self.assertEqual(strip_colors(row.repState.text), "Earned")
        self.assertIn("|cffffd100", row.repState.text)
        # on two lines the row grows by the reputation's line, and only that row
        game.ns.SetOption(game.ns, "compact", False)
        row = next(frame for frame in self.gated_rows(game) if frame.data.id == row.data.id)
        self.assertEqual(row.height, ROW + 16)
        free = next(frame for frame in self.frames(game) if frame.data.kind == "item" and not frame.data.reputation)
        self.assertEqual(free.height, ROW)

    def test_a_faction_nobody_knows_how_to_earn(self):
        """The Watchers' rings stay in the list, a grey "?" after their name that the tooltip explains."""
        game = self.open(cls="PRIEST")   # Discipline: a healer's list, which stays on the weights
        window = game.ns.Browser.window
        rows = self.frames(game)
        watchers = [row for row in rows if row.data.kind == "item" and row.data.reputation
                    and row.data.reputation.factionID == 2819]
        self.assertTrue(watchers, "the Discipline list keeps The Watchers' rings")
        for row in watchers:
            self.assertTrue(row.name.text.endswith(" |cff808080?|r"), row.name.text)
        others = [row for row in rows if row.data.kind == "item" and not (row.data.reputation
                  and row.data.reputation.factionID == 2819)]
        self.assertTrue(others)
        self.assertFalse(any(row.name.text.endswith("?|r") for row in others))
        game.stub.run(watchers[0], "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        lines = [strip_colors(line[1]) for line in tooltip.lines.values()]
        self.assertIn("? No source says how to earn this reputation, nor who sells its pieces.", lines)
        game.stub.run(others[0], "OnEnter")
        lines = [strip_colors(line[1]) for line in tooltip.lines.values()]
        self.assertFalse(any(line.startswith("? No source") for line in lines))

        # the character sheet: the same sign by the ring's name
        game.stub.run(window.tabs.buttons[3], "OnClick")
        cells = [cell for cell in game.ns.Character.view.cells.values() if cell.data and cell.data.id]
        marked = [cell for cell in cells if cell.data.reputation and cell.data.reputation.factionID == 2819]
        self.assertTrue(marked, "a Watchers ring is the Arcane sheet's best ring before the raids")
        self.assertTrue(all(" |cff808080?|r" in cell.name.text for cell in marked))
        self.assertFalse(any("|cff808080?|r" in cell.name.text for cell in cells if cell not in marked))

        # the Reputations tab: the "?" by the faction's name, in the list and over its side, and said in words
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        button = next(button for button in view.buttons.values() if button.group.factionID == 2819)
        self.assertTrue(button.name.text.endswith(" |cff808080?|r"))
        game.stub.run(button, "OnClick")
        self.assertEqual(view.chosen.factionID, 2819)
        self.assertTrue(view.title.text.endswith(" |cff808080?|r"))
        self.assertIn("? No source says how to earn this reputation", strip_colors(view.you.text))
        other = next(button for button in view.buttons.values() if button.group.factionID != 2819)
        self.assertFalse(other.name.text.endswith("?|r"))

    def test_reputation_filter(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        rows = lambda: [row for row in window.rowData.values() if row.kind == "item"]
        everything = rows()
        gated = [row.id for row in everything if row.reputation and row.reputation.kind != "r"]
        self.assertTrue(gated)
        self.assertEqual(label(window.reputation), "All")
        self.assertEqual(look(window.reputation), "idle")
        open_dropdown(game, window.reputation.button)
        self.assertEqual(texts(game.stub.menu), ["All", "Within reach", "To earn"])
        find(game.stub.menu, "To earn").pick()
        self.assertEqual(look(window.reputation), "active", "a filter that narrows the list is gold")
        self.assertEqual({row.id for row in rows()}, set(gated))
        open_dropdown(game, window.reputation.button)
        find(game.stub.menu, "Within reach").pick()
        self.assertFalse({row.id for row in rows()} & set(gated))
        self.assertEqual(len(rows()), len(everything) - len(gated))
        # once earned, a piece is within reach
        faction = game.ns.Reputation.Requirement(gated[0]).factionID
        self.earn(game, faction, 8, 42000, 42000, 43000)
        self.assertIn(gated[0], {row.id for row in rows()})
        # the enchants have the filter too, the character sheet does not
        game.stub.run(window.tabs.buttons[2], "OnClick")
        self.assertTrue(window.reputation.shown)
        game.stub.run(window.tabs.buttons[3], "OnClick")
        self.assertFalse(window.reputation.shown)

    def test_recipes_are_never_to_earn(self):
        game = self.open()
        rep = game.ns.Reputation
        recipe = game.lua.table_from({"factionID": 576, "standing": 7, "kind": "r"})
        worn = game.lua.table_from({"factionID": 576, "standing": 7, "kind": "w"})
        self.assertTrue(rep.Reachable(recipe), "the crafter's reputation is not the player's to earn")
        self.assertFalse(rep.Reachable(worn))
        self.assertTrue(rep.Reachable(None))

    def test_enchant_rows_say_what_a_reputation_asks(self):
        game = self.open(saved="EasyBISCharDB = { phase = 9 }")
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[2], "OnClick")
        state, gated = game.ns.Browser.state, []
        for cls in test_addon.CLASSES:
            for spec in range(1, int(game.ns.Index.SpecCount(cls)) + 1):
                if not gated:
                    state["class"], state.spec = cls, spec
                    game.ns.SetOption(game.ns, "listAlts", False)
                    game.ns.SetOption(game.ns, "listAlts", True)   # the window draws them again
                    gated = self.gated_rows(game)
        self.assertTrue(gated, "no enchant of any spec needs a reputation")
        row = gated[0]
        self.assertEqual(row.height, ROW + 16)
        game.stub.run(row, "OnEnter")
        lines = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertTrue(any(text.startswith("Requires ") for text in lines), lines)
        self.assertEqual(sum(1 for text in lines if text.startswith("Requires ")), 1)

    def test_reputations_tab(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        self.assertIsNone(game.ns.ReputationView.view, "the tab is made when it is first asked for")
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        self.assertTrue(view.shown)
        self.assertEqual(look(window.tabs.buttons[5]), "lit")
        for hidden in (window.slot, window.source, window.zone, window.reputation, window.add, window.alts, window.scroll):
            self.assertFalse(hidden.shown)
        for kept in (window.spec, window.list, window.phase):
            self.assertTrue(kept.shown)

        needs = view.factionData
        self.assertTrue(needs.own[1])
        first = needs.own[1]
        count = first.best + first.alts + first.other
        self.assertEqual(view.chosen.factionID, first.factionID)
        unsure = " ?" if game.ns.Reputation.Unknown(first.factionID) else ""
        self.assertEqual(strip_colors(view.title.text), f"Faction {first.factionID}{unsure}")
        # the faction chosen is lit in blue: gold is for what is earned
        button = view.buttons[1]
        self.assertTrue(button.selected.shown)
        self.assertEqual(list(button.selected.vertexColor.values())[:3], [0.35, 0.6, 1.0])
        # the text as large as the other tabs': their rows' fonts
        self.assertEqual(button.name.fontObject, "EasyBISRowName")
        self.assertEqual(view.title.fontObject, "EasyBISRowHeader")
        self.assertEqual(view.you.fontObject, "EasyBISRowText")
        self.assertFalse(view.buttons[2].selected.shown if view.buttons[2] else False)
        # the list shows the name, the standing and the pieces: no bar, no count
        self.assertTrue(button.icons[1].shown)
        self.assertTrue(button.state.shown)
        self.assertIsNone(button.way)
        self.assertIsNone(button.bestChip)
        self.assertEqual(button.height, 52)

        # a piece on the track for each piece the faction opens, and a line for each
        pieces = [piece for piece in view.pieces.values()]
        self.assertEqual(len(pieces), count)
        self.assertTrue(all(piece.shown for piece in pieces))
        lines = list(view.detailData.values())
        sections = [plain(line.text) for line in lines if line.kind == "section"]
        quests = ["Quests"] if game.ns.Reputation.Ways(first.factionID).listed > 0 else []   # none for The Watchers
        self.assertEqual(sections, ["Pieces for this spec", "Where", *quests, "Not known yet"])
        self.assertEqual(len([line for line in lines if line.kind == "entry"]), count)
        self.assertTrue([line for line in lines if line.kind == "seller"])
        self.assertTrue(all(line.evidence in ("data", "check", "unknown") for line in lines if line.kind in ("quest", "note")))
        self.assertTrue(any(line.kind == "note" and line.evidence == "unknown" for line in lines),
                        "what is not known of a reputation is said to be unknown")

        # never met: the whole way from Neutral is left, and nothing is gold
        cards = list(view.cardData.values())
        self.assertEqual(len(cards), 3)
        self.assertTrue(cards[0].label.startswith("Left for "))
        self.assertEqual(cards[0].note, "from Neutral")
        self.assertNotIn("|cffffd100", view.you.text)
        self.assertFalse(any("|cffffd100" in card.value for card in cards))
        self.assertFalse(any("|cffffd100" in (line.standing or "") for line in lines))
        self.assertFalse(any(piece.check.shown for piece in pieces))
        self.assertFalse(view.watch.shown, "a faction never met is not in the game's reputation pane")

        # the player earns it: the standings, the pieces and the card turn gold, and the tab follows by itself
        self.earn(game, first.factionID, 8, 42000, 42000, 43000)
        self.assertIn("|cffffd100", view.you.text)
        self.assertEqual(plain(view.cardData[1].value), "All unlocked")
        self.assertIn("|cffffd100", view.cardData[1].value)
        self.assertTrue(all(piece.check.shown for piece in view.pieces.values()))
        entries = [line for line in view.detailData.values() if line.kind == "entry"]
        self.assertTrue(all("|cffffd100" in line.standing for line in entries))

        # the game's reputation bar follows it on a click
        self.assertTrue(view.watch.shown)
        self.assertEqual(label(view.watch), "Watch")
        game.stub.run(view.watch, "OnClick")
        self.assertEqual(game.stub.watched, first.factionID)
        self.assertEqual(label(view.watch), "Stop watching")
        game.stub.run(view.watch, "OnClick")
        self.assertIsNone(game.stub.watched)

        # another faction, by a click
        if needs.own[2]:
            second = view.buttons[2]
            game.stub.run(second, "OnClick")
            self.assertEqual(view.chosen.factionID, needs.own[2].factionID)
            self.assertEqual(game.ns.Browser.state.faction, needs.own[2].factionID)
            self.assertTrue(view.buttons[2].selected.shown)
            self.assertFalse(view.buttons[1].selected.shown)

        # leaving the tab hides it
        game.stub.run(window.tabs.buttons[1], "OnClick")
        self.assertFalse(view.shown)
        self.assertTrue(window.scroll.shown)
        self.assertTrue(window.slot.shown)

    def test_reputation_pieces_open_their_slot_or_link(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        piece = next(piece for piece in view.pieces.values() if piece.entry.id)
        game.stub.run(piece, "OnEnter")
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Click: the pieces of this slot. Shift-click: link it.", said)
        game.stub.itemNames[piece.entry.id] = "Test piece"
        game.stub.modifier = True
        game.stub.run(piece, "OnClick")
        self.assertIn(f"item:{piece.entry.id}", game.stub.linked, "Shift-click links the item")
        self.assertEqual(game.ns.Browser.state.tab, "reputations")
        game.stub.modifier = False
        game.stub.run(piece, "OnClick")
        self.assertEqual(game.ns.Browser.state.tab, "items")
        self.assertEqual(game.ns.Browser.state.slot, piece.entry.slot)

    def test_reputation_sections_fold(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        kinds = lambda: [line.kind for line in view.detailData.values()]
        self.assertIn("entry", kinds())
        section = view.lines[1]
        self.assertEqual(section.data.key, "pieces")
        # each section has its picture: the pieces' is the first piece's
        self.assertTrue(section.badge.shown)
        self.assertEqual(section.badge.texture, view.pieces[1].icon.texture)
        others = [view.lines[i] for i in range(2, len(view.detailData) + 1) if view.detailData[i].kind == "section"]
        self.assertTrue(all(line.badge.shown and line.badge.texture for line in others))
        # under a section, every other line is lighter
        below = [view.lines[i] for i in range(2, len(view.detailData) + 1)]
        under = [line.data.kind for line in below]
        stop = under.index("section") if "section" in under else len(under)
        self.assertEqual([line.stripe.shown for line in below[:stop]], [i % 2 == 1 for i in range(stop)])
        self.assertEqual(section.fold.texture, "Interface\\Buttons\\UI-MinusButton-Up")
        game.stub.run(section, "OnClick")
        self.assertNotIn("entry", kinds())
        self.assertEqual(view.lines[1].fold.texture, "Interface\\Buttons\\UI-PlusButton-Up")
        self.assertEqual(len(list(view.pieces.values())), view.chosen.best + view.chosen.alts + view.chosen.other,
                         "the track keeps its pieces")
        # folded for the other factions too, until opened again
        game.stub.run(view.lines[1], "OnClick")
        self.assertIn("entry", kinds())

    def test_reputation_vendor_on_the_map(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        found = None
        for index in range(1, len(view.buttons) + 1):
            if found or not view.buttons[index].shown:
                continue
            game.stub.run(view.buttons[index], "OnClick")
            for line_index in range(1, len(view.detailData) + 1):
                data = view.detailData[line_index]
                if data.kind == "seller" and data.map:
                    found = view.lines[line_index]
                    break
        self.assertIsNotNone(found, "no faction of the list has a vendor whose place is known")
        self.assertTrue(found.map.shown)
        game.stub.run(found.map, "OnClick")
        self.assertEqual(game.stub.waypoint.uiMapID, found.data.map)
        self.assertAlmostEqual(game.stub.waypoint.x, found.data.x / 100)
        self.assertEqual(game.stub.openedMap, found.data.map)
        # a quest's reward or a recipe has no place: no button
        others = [view.lines[i] for i in range(1, len(view.detailData) + 1)
                  if view.detailData[i].kind == "seller" and not view.detailData[i].map]
        self.assertFalse(any(line.map.shown for line in others))

    def test_reputation_scroll_bars_only_when_needed(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        view.detail.height = 5000
        view.list.height = 5000
        game.ns.ReputationView.Update(game.ns.Browser.state)
        self.assertFalse(view.detail.ScrollBar.shown)
        self.assertFalse(view.list.ScrollBar.shown)
        view.detail.height = 50
        game.ns.ReputationView.Update(game.ns.Browser.state)
        self.assertTrue(view.detail.ScrollBar.shown)

    def test_recipes_are_kept_apart_in_the_tab(self):
        """In every spec, a recipe is counted in the artisans' group and in nobody's own total."""
        game = self.open()
        rep = game.ns.Reputation
        artisans = 0
        for cls in test_addon.CLASSES:
            for spec in range(1, int(game.ns.Index.SpecCount(cls)) + 1):
                for mode in ("pve", "pvp"):
                    needs = rep.Needs(cls, spec, mode)
                    for group in needs.own.values():
                        self.assertFalse(group.artisan)
                        for entries in group.steps.values():
                            self.assertFalse([e for e in entries.values() if e.requirement.kind == "r"])
                    for group in needs.artisan.values():
                        artisans += 1
                        self.assertTrue(group.artisan)
                        for entries in group.steps.values():
                            self.assertFalse([e for e in entries.values() if e.requirement.kind != "r"])
        self.assertGreater(artisans, 0)

    TIMBERMAW_PIECES = (15065, 19044, 19049)   # made from Timbermaw's patterns 20254, 19326 and 19327

    def shown_pieces(self, token, spec, count) -> tuple[set, set]:
        """(shown, best): the items a PvE list shows with that many alternatives, and its best picks."""
        flt = for_list(default_filter(), "pve")
        visible = {slot: [e for e in self.kept[token][spec]["pve"][slot] if e.passes(flt)] for slot, _ in ladders.SLOTS}
        visible["main"], visible["off"] = ladders.weapon_lists(visible["main"], visible["off"])
        shown, best = set(), set()
        for slot, _ in ladders.SLOTS:
            picks, alternatives = ladders.picks(slot, visible[slot], count)
            shown |= {e.shown("a") for e in picks + alternatives}
            best |= {e.shown("a") for e in picks}
        return shown, best

    def timbermaw_spec(self) -> tuple:
        """(class, spec, alternatives): the first PvE list that shows the pieces of Timbermaw's three
        leatherworking patterns, with the fewest alternatives it takes."""
        for count in range(ladders.ALTERNATIVES, ladders.MAX_ALTERNATIVES + 1):
            for token in test_addon.CLASSES:
                for spec in self.kept[token]:
                    if set(self.TIMBERMAW_PIECES) <= self.shown_pieces(token, spec, count)[0]:
                        return token, spec, count
        self.fail("no PvE list shows the pieces of Timbermaw's three patterns: these tests need another example")

    def timbermaw_best_pick(self) -> tuple:
        """(class, spec, profession): the first PvE list with a best pick made from a pattern Timbermaw sells,
        and that pattern's profession."""
        rep = Game().ns.Reputation
        for token in test_addon.CLASSES:
            for spec in self.kept[token]:
                for item_id in sorted(self.shown_pieces(token, spec, ladders.ALTERNATIVES)[1]):
                    requirement = rep.Requirement(item_id, "a")
                    if requirement and requirement.kind == "r" and requirement.factionID == 576:
                        return token, spec, requirement.profession
        self.fail("no best pick is made from a pattern Timbermaw sells: this test needs another example")

    def crafter_game(self, *professions, picked=None) -> Game:
        """A list where Timbermaw sells patterns: the one timbermaw_spec finds, or picked (class, spec,
        alternatives); the player has these professions."""
        token, spec, count = picked or self.timbermaw_spec()
        game = self.open(saved=f"EasyBISDB = {{ altCount = {count} }} "
                               f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}", cls=token)
        lua, stub = game.lua, game.stub
        stub.learn(lua.table_from({index: lua.table_from({1: name, 2: rank, 3: line})
                                   for index, (name, rank, line) in enumerate(professions, 1)}))
        for piece, recipe in ((15065, 20254), (19044, 19326), (19049, 19327)):
            stub.itemNames[piece], stub.bindings[piece] = f"Piece {piece}", 2
            stub.itemNames[recipe], stub.itemIcons[recipe] = f"Pattern {recipe}", 134939
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        return game

    @staticmethod
    def timbermaw(view):
        return next(button for button in view.buttons.values() if button.group.artisan and button.group.factionID == 576)

    def test_a_crafters_faction_for_another_profession(self):
        """A tailor reads Timbermaw's leatherworking patterns: no standing of theirs, how to get the pieces instead."""
        game = self.crafter_game(("Tailoring", 300, 197))
        view = game.ns.ReputationView.view
        button = self.timbermaw(view)
        self.assertEqual(button.group.craftStatus, "other")
        self.assertEqual(strip_colors(button.state.text), "Leatherworking")
        game.stub.run(button, "OnClick")
        self.assertEqual(strip_colors(view.you.text), "Leatherworking: not one of your professions")
        # the banner, in place of the cards
        self.assertTrue(view.banner.shown)
        self.assertFalse(any(card.shown for card in view.cards.values()))
        self.assertEqual(view.cardData[1].label, "Not your reputation: the crafter's counts")
        self.assertEqual(view.cardData[1].value, "These pieces bind when equipped: buy them at the auction house, "
                                                 "or have them made by a leatherworker who has the recipe.")
        # the lines name the patterns, with their icon, and what they make in the tooltip
        lines = list(view.detailData.values())
        entries = [line for line in lines if line.kind == "entry"]
        self.assertEqual([plain(line.text) for line in entries], ["Pattern 20254", "Pattern 19326", "Pattern 19327"])
        self.assertTrue(all(line.recipe and line.icon == 134939 for line in entries))
        self.assertEqual(view.lines[2].icon.texture, 134939)
        self.assertTrue(all(piece.craft.shown for piece in view.pieces.values()), "the track says they are recipes")
        game.stub.run(view.lines[2], "OnEnter")
        tips = [strip_colors(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Makes: Piece 15065", tips)
        self.assertIn("Leatherworking: not one of your professions", tips)
        # how to earn it is for whoever would learn them: folded, until opened
        sections = {line.key: line for line in lines if line.kind == "section"}
        self.assertEqual(plain(sections["pieces"].text), "Recipes for this spec")
        self.assertEqual(plain(sections["questsSelf"].text), "Quests")
        self.assertTrue(sections["questsSelf"].folded and sections["unknownSelf"].folded)
        self.assertNotIn("quest", [line.kind for line in lines])
        index = next(i for i in range(1, len(view.detailData) + 1) if view.detailData[i].key == "questsSelf")
        game.stub.run(view.lines[index], "OnClick")
        self.assertIn("quest", [line.kind for line in view.detailData.values()])
        # never gold, even exalted: the tailor's reputation does not make the pieces
        self.earn(game, 576, 8, 42000, 42000, 43000)
        self.assertFalse(any("|cffffd100" in (line.standing or "") for line in view.detailData.values()))
        self.assertNotIn("|cffffd100", view.you.text + button.state.text)
        self.assertFalse(any(piece.check.shown for piece in view.pieces.values()))

    def test_a_crafters_faction_for_the_crafter(self):
        game = self.crafter_game(("Leatherworking", 270, 165), ("Skinning", 300, 393))
        view = game.ns.ReputationView.view
        button = self.timbermaw(view)
        self.assertTrue(button.group.crafter)
        self.assertIs(view.buttons[len(view.factionData.own) + 1].group.crafter, True, "the crafter's come first")
        game.stub.run(button, "OnClick")
        self.assertFalse(view.banner.shown)
        self.assertTrue(all(card.shown for card in view.cards.values()))
        self.assertTrue(view.cardData[1].label.startswith("Left for "))
        self.assertTrue(strip_colors(view.you.text).endswith("  ·  Leatherworking 270 / 295"), view.you.text)
        self.assertNotIn("|cffffd100", view.you.text)
        sections = [line.key for line in view.detailData.values() if line.kind == "section"]
        self.assertEqual(sections, ["pieces", "sources", "quests", "unknown"])
        self.assertIn("quest", [line.kind for line in view.detailData.values()])
        # the skill reached: gold
        game.stub.learn(game.lua.table_from({1: game.lua.table_from({1: "Leatherworking", 2: 300, 3: 165})}))
        game.stub.fire("SKILL_LINES_CHANGED")
        game.stub.runTimers()
        self.assertIn("|cffffd100Leatherworking 300 / 295|r", view.you.text)

    def test_a_crafters_faction_when_the_game_gives_no_professions(self):
        game = self.open(saved="EasyBISCharDB = { class = 'WARRIOR', spec = 1, list = 'pve' }", cls="WARRIOR")
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        button = self.timbermaw(view)
        self.assertIsNone(button.group.craftStatus)
        game.stub.run(button, "OnClick")
        self.assertFalse(view.banner.shown)
        self.assertIn("Recipes: the crafter's reputation is what counts.", strip_colors(view.you.text))
        self.assertEqual(strip_colors(button.state.text), "Not met yet", "the player's own standing, as before")

    def test_faction_emblems(self):
        """An emblem the game has: faint behind the faction in the list, and by its name; none for the others."""
        game = self.crafter_game(("Leatherworking", 300, 165))
        view = game.ns.ReputationView.view
        button = self.timbermaw(view)
        self.assertFalse(button.emblem.shown, "the game gives the question mark: no emblem")
        game.stub.itemIcons[21377] = 236000   # the Deadwood Headdress Feather
        game.ns.ReputationView.Update(game.ns.Browser.state)
        button = self.timbermaw(view)
        self.assertTrue(button.emblem.shown)
        self.assertEqual(button.emblem.texture, 236000)
        self.assertEqual(button.emblem.alpha, 0.09, "without a gradient, an even fade")
        others = [b for b in view.buttons.values() if b.shown and b.group.factionID != 576]
        self.assertTrue(others)
        self.assertFalse(any(b.emblem.shown for b in others), "the other emblems' items are not known here")
        # by the name, at full colour; the title moves aside for it
        game.stub.run(button, "OnClick")
        self.assertTrue(view.emblem.shown)
        self.assertEqual(view.emblem.texture, 236000)
        self.assertEqual(view.title.points[1][4], 292 + 14 + 36 + 8)
        game.stub.run(others[0], "OnClick")
        self.assertFalse(view.emblem.shown)
        self.assertEqual(view.title.points[1][4], 292 + 14)

    def test_reputations_follow_the_faction_picked(self):
        """An Alliance character who picks the Horde sees the Darkspear Raiders where Theramore was."""
        game = self.open(cls="MAGE")
        rep, state = game.ns.Reputation, game.ns.Browser.state
        factions = lambda: {group.factionID for group in rep.Needs(state["class"], state.spec, state.list).own.values()}
        spec = next((cls, spec, mode) for cls in test_addon.CLASSES
                    for spec in range(1, int(game.ns.Index.SpecCount(cls)) + 1) for mode in ("pve", "pvp")
                    if 2799 in {g.factionID for g in rep.Needs(cls, spec, mode).own.values()})
        state["class"], state.spec, state.list = spec
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        shown = lambda: {button.group.factionID for button in view.buttons.values() if button.shown}
        self.assertIn(2799, shown())
        self.assertNotIn(2798, factions())
        game.ns.SetSide(game.ns, "h")
        self.assertIn(2798, factions())
        self.assertNotIn(2799, factions())
        self.assertIn(2798, shown(), "the tab follows at once")
        self.assertNotIn(2799, shown())

    def test_reputation_quests_ten_to_a_page(self):
        """Every quest the class can take, the repeatable ones that help first, ten to a page, each with the
        standings it is offered between; the arrows turn the pages."""
        game = self.open(cls="MAGE")
        rep, state = game.ns.Reputation, game.ns.Browser.state
        found = next((cls, spec, mode, group.factionID) for cls in test_addon.CLASSES
                     for spec in range(1, int(game.ns.Index.SpecCount(cls)) + 1) for mode in ("pve", "pvp")
                     for group in rep.Needs(cls, spec, mode).own.values()
                     if len(rep.Ways(group.factionID, cls).quests) > 20)
        cls, state.spec, state.list, faction = found
        state["class"] = cls
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        game.stub.run(next(b for b in view.buttons.values() if b.shown and b.group.factionID == faction), "OnClick")
        quests = [quest for quest in rep.Ways(faction, cls).quests.values()]
        name = lambda standing: rep.StandingName(standing)
        titles = [quest.quest + (f" from {name(quest['from'])}" if quest["from"] else "")
                  + (f" until {name(quest.upto)}" if quest.upto else "") for quest in quests]
        usable = lambda quest: (quest["from"] or 3) < 7 and (quest.upto is None or quest.upto > 3)
        ranks = [(not usable(quest), not quest.repeats) for quest in quests]
        self.assertEqual(ranks, sorted(ranks), "the repeatable ones that help first")
        last = (len(titles) + 9) // 10
        self.assertGreaterEqual(last, 3)
        shown = lambda: [plain(line.text) for line in view.detailData.values() if line.kind == "quest"]

        def pager():
            index = next(i for i in range(1, len(view.detailData) + 1) if view.detailData[i].kind == "pager")
            return view.lines[index]

        self.assertEqual(shown(), titles[:10])
        self.assertEqual(plain(pager().text.text), f"1-10 of {len(titles)}")
        self.assertTrue(pager().prev.shown and pager().next.shown)
        self.assertEqual((pager().prev.enabled, pager().next.enabled), (False, True))
        others = [view.lines[i] for i in range(1, len(view.detailData) + 1) if view.detailData[i].kind != "pager"]
        self.assertFalse(any(line.prev.shown or line.next.shown for line in others))
        game.stub.run(pager().next, "OnClick")
        self.assertEqual(shown(), titles[10:20])
        self.assertEqual((pager().prev.enabled, pager().next.enabled), (True, True))
        for _ in range(last - 2):
            game.stub.run(pager().next, "OnClick")
        self.assertEqual(shown(), titles[(last - 1) * 10:])
        self.assertEqual(plain(pager().text.text), f"{(last - 1) * 10 + 1}-{len(titles)} of {len(titles)}")
        self.assertEqual(pager().next.enabled, False)
        game.stub.run(pager().prev, "OnClick")
        self.assertEqual(shown(), titles[(last - 2) * 10:(last - 1) * 10])
        # the page is kept while the player looks at another faction
        other = next(b for b in view.buttons.values() if b.shown and b.group.factionID != faction)
        game.stub.run(other, "OnClick")
        game.stub.run(next(b for b in view.buttons.values() if b.shown and b.group.factionID == faction), "OnClick")
        self.assertEqual(shown(), titles[(last - 2) * 10:(last - 1) * 10])

    def test_reputations_sections_have_room_between_them(self):
        game = self.pvp_game()
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        count = len(view.detailData)
        tops = [-view.lines[i].points[1][5] for i in range(1, count + 1)]
        heights = [view.lines[i].height for i in range(1, count + 1)]
        kinds = [view.detailData[i].kind for i in range(1, count + 1)]
        self.assertGreater(kinds.count("section"), 2)
        self.assertEqual(kinds[0], "section")
        for index in range(1, count):
            gap = 14 if kinds[index] == "section" else 0
            self.assertEqual(tops[index], tops[index - 1] + heights[index - 1] + gap, (index, kinds[index]))

    def test_reputations_say_a_battleground(self):
        """A battleground's faction says so in the list, and its header names the battleground as the game does."""
        game = self.pvp_game()
        game.stub.areaNames[3358], game.stub.areaNames[2597] = "Arathi Basin", "Alterac Valley"
        game.stub.run(game.ns.Browser.window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        buttons = [button for button in view.buttons.values() if button.shown]
        states = {button.group.factionID: button.state.text for button in buttons}
        battle = [faction for faction in states if faction in reputations.BATTLEGROUNDS]
        self.assertTrue(battle, "the PvP list asks for a battleground's reputation")
        self.assertTrue(len(battle) < len(states), "and for another")
        for faction, text in states.items():
            self.assertEqual(plain(text).endswith("·  Battleground"), faction in reputations.BATTLEGROUNDS, (faction, text))
            self.assertNotIn("|cffffd100  ·", text, "gold stays for what is earned")
        names = {3358: "Arathi Basin", 2597: "Alterac Valley"}
        for button in buttons:
            game.stub.run(button, "OnClick")
            area = reputations.BATTLEGROUNDS.get(button.group.factionID)
            said = f"Battleground: {names[area]}" if area in names else "Battleground"
            self.assertEqual(said in plain(view.you.text), area is not None, plain(view.you.text))

    def test_reputations_tab_shows_a_piece_asking_for_neutral(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.lua.eval("""function(rep)
            local needs = rep.Needs
            rep.Needs = function(...)
                local result = needs(...)
                local group = result.own[1]
                group.steps[3] = { { id = 21196, slot = "finger", role = "alt",
                    requirement = { factionID = group.factionID, standing = 3, kind = "w" } } }
                return result
            end
        end""")(game.ns.Reputation)
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        entries = [line for line in view.detailData.values() if line.kind == "entry"]
        self.assertEqual(entries[0].entry.id, 21196, "Neutral comes first")
        self.assertEqual(plain(entries[0].standing), "Neutral")
        self.assertEqual(view.pieces[1].entry.id, 21196)

    def test_reputations_tab_with_nothing_to_earn(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        needs = game.lua.eval("function(rep) rep.Needs = function() return { own = {}, artisan = {} } end end")
        needs(game.ns.Reputation)
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        self.assertTrue(view.empty.shown)
        self.assertEqual(view.empty.text, "This spec needs no reputation for this list and this phase.")
        self.assertFalse(view.list.shown or view.detail.shown or view.title.shown)

    def test_a_piece_clicked_opens_its_slot_unfiltered(self):
        """The Reputation filter is set aside with the others: the piece clicked is in the list."""
        game = self.pvp_game()
        state = game.ns.Browser.state
        state.reputation, state.source = "ok", "vendor"
        game.ns.Browser.ShowSlot("finger")
        self.assertEqual((state.tab, state.slot, state.reputation, state.source), ("items", "finger", None, None))

    def test_character_sheet_a_crafters_piece_is_not_earned_by_another_profession(self):
        """A piece made from a recipe of another profession: the crafter's standing, so no gold on the sheet."""
        token, spec, craft = self.timbermaw_best_pick()
        lines = {"Leatherworking": 165, "Tailoring": 197}
        other = next(name for name in lines if name != craft)
        for profession, earned in (((other, 300, lines[other]), False), ((craft, 300, lines[craft]), True)):
            game = self.crafter_game(profession, picked=(token, spec, ladders.ALTERNATIVES))
            self.earn(game, 576, 8, 42000, 42000, 43000)
            game.stub.run(game.ns.Browser.window.tabs.buttons[3], "OnClick")
            view = game.ns.Character.view
            cells = [view.cells[index] for index in range(1, len(view.cellData) + 1)
                     if view.cellData[index].reputation and view.cellData[index].reputation.kind == "r"
                     and view.cellData[index].reputation.profession == craft]
            self.assertTrue(cells, "the sheet has a Timbermaw pattern's piece")
            for cell in cells:
                self.assertEqual("Earned" in plain(cell.where.text), earned, profession[0])
                self.assertEqual("|cffffd100" in cell.where.text, earned, profession[0])

    def test_character_sheet_sums_up_the_reputations(self):
        game = self.pvp_game()
        window = game.ns.Browser.window
        game.stub.run(window.tabs.buttons[3], "OnClick")
        view = game.ns.Character.view
        summary = list(view.reputationData.values())
        self.assertTrue(summary)
        self.assertTrue(view.reputationTitle.shown)
        cells = [cell for cell in view.cellData.values() if cell.reputation and cell.reputation.kind != "r"]
        self.assertEqual(sum(line.total for line in summary), len(cells), "the recipes are not counted")
        line = view.reputations[1]
        self.assertEqual(strip_colors(line.count.text), f"0 / {summary[0].total}")
        self.assertNotIn("|cffffd100", line.count.text)
        # a cell says what it asks for, and not where it comes from
        cell = next(view.cells[index] for index in range(1, len(view.cellData) + 1)
                    if view.cellData[index].reputation and view.cellData[index].reputation.factionID == summary[0].factionID)
        self.assertIn(game.ns.Reputation.StandingName(cell.data.reputation.standing), plain(cell.where.text))
        # earned: the count and the cell turn gold
        self.earn(game, summary[0].factionID, 8, 42000, 42000, 43000)
        self.assertEqual(strip_colors(line.count.text), f"{summary[0].total} / {summary[0].total}")
        self.assertIn("|cffffd100", line.count.text)
        self.assertIn("Earned", plain(cell.where.text))
        # a click opens the tab on that faction
        game.stub.run(line, "OnClick")
        self.assertEqual(game.ns.Browser.state.tab, "reputations")
        self.assertEqual(game.ns.ReputationView.view.chosen.factionID, summary[0].factionID)

    def test_reputations_in_french(self):
        game = self.open(locale="frFR", saved="EasyBISCharDB = { class = 'WARRIOR', spec = 2, list = 'pvp' }", cls="WARRIOR")
        window = game.ns.Browser.window
        self.assertEqual(label(window.tabs.buttons[5]), "Réputations")
        self.assertEqual(label(window.reputation), "Toutes")
        game.stub.run(window.tabs.buttons[5], "OnClick")
        view = game.ns.ReputationView.view
        sections = [plain(line.text) for line in view.detailData.values() if line.kind == "section"]
        quests = ["Quêtes"] if game.ns.Reputation.Ways(view.chosen.factionID).listed > 0 else []
        self.assertEqual(sections, ["Pièces pour cette spécialisation", "Où", *quests, "Pas encore connu"])
        other = next(b for b in view.buttons.values() if b.shown and game.ns.Reputation.Ways(b.group.factionID).listed > 0)
        game.stub.run(other, "OnClick")
        self.assertIn("Quêtes", [plain(line.text) for line in view.detailData.values() if line.kind == "section"])
        self.assertTrue(view.cardData[1].label.startswith("Reste pour "))

    def test_older_client(self):
        game = Game(saved=OLD_CLIENT + "; " + ENHANCEMENT)
        game.ns.Browser.Open()
        window, state = game.ns.Browser.window, game.ns.Browser.state
        self.assertEqual(window.template, "BackdropTemplate")
        self.assertEqual(self.shown_rows(game), self.reference_rows("SHAMAN", 2, "pve"))
        self.assertFalse(window.options.shown, "the options menu needs the menu API")
        # without menus, a click moves to the next choice
        open_dropdown(game, window.slot.button)
        self.assertEqual(state.slot, "head")
        open_dropdown(game, window.slot.button)
        self.assertEqual(state.slot, "neck")
        open_dropdown(game, window.spec.button)
        self.assertEqual((state["class"], state.spec), ("SHAMAN", 3))
        open_dropdown(game, window.source.button)
        open_dropdown(game, window.zone.button)
        open_dropdown(game, window.phase.button)
        self.assertEqual(game.ns.Phase(), 1, "without menus, a click on the phase moves to the next one")
        game.stub.run(window.tabs.buttons[3], "OnClick")
        self.assertEqual(self.sheet(game), self.reference_sheet("SHAMAN", 3, "pve", default_filter(phase=1)))


    # -- the Consumables tab ---------------------------------------------------------------------

    def open_consumables(self, token="WARRIOR", spec=2, **options) -> Game:
        game = self.open(cls=token, saved=f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}", **options)
        game.stub.run(game.ns.Browser.window.tabs.buttons[4], "OnClick")
        return game

    def consumable_rows(self, game) -> list:
        return [row for row in game.ns.Browser.window.rowData.values() if row.kind == "consumable"]

    def test_consumables_tab(self):
        game = self.open_consumables()
        window = game.ns.Browser.window
        self.assertEqual(look(window.tabs.buttons[4]), "lit")
        for control in (window.spec, window.list, window.listLabel, window.phase, window.slot, window.alts):
            self.assertTrue(control.shown)
        for control in (window.source, window.zone, window.add):
            self.assertFalse(control.shown)
        self.assertEqual(window.slot.label.text, "Category")
        data = list(window.rowData.values())
        self.assertEqual((data[0].kind, data[0].text), ("note", game.ns.L.CONS_NOTE))
        self.assertEqual((data[1].kind, data[1].text), ("header", "Flasks"))
        headers = [row.text for row in data if row.kind == "header"]
        self.assertEqual(headers, ["Flasks", "Elixirs", "Food", "Scrolls", "Weapon stones and oils", "Combat potions",
                                   "Healing potions", "Bandages", "Situational"], "a warrior has no mana to restore")

    def test_consumable_rows_show_rank_effect_and_source(self):
        game = self.open_consumables()
        window = game.ns.Browser.window
        frames = {window.rowData[index].id: window.rows[index] for index in range(1, len(window.rowData) + 1)
                  if window.rowData[index].kind == "consumable"}
        grizzly = frames[250351]
        self.assertEqual(plain(grizzly.rank.text), "Best", "the best of its category, never a BIS")
        self.assertEqual(grizzly.sub.text, "+25 Strength; +2% Critical Strike")
        self.assertEqual(grizzly.kind.text, "Alchemy (300)")
        self.assertTrue(grizzly.barBack.shown)
        titans = frames[13510]
        self.assertEqual(plain(titans.rank.text), "Not ranked")
        self.assertFalse(titans.barBack.shown)
        self.assertEqual(titans.sub.text, "+1200 Maximum Health")
        self.assertEqual(plain(frames[250329].rank.text), "Not ranked", "the Phalanx: armor has no weight for a Fury warrior")
        mongoose = frames[13452]
        self.assertRegex(plain(mongoose.rank.text), r"^-\d+%$")

    def test_consumable_tooltip(self):
        game = self.open_consumables()
        window = game.ns.Browser.window
        index = next(index for index in range(1, len(window.rowData) + 1) if window.rowData[index].id == 13510)
        game.stub.run(window.rows[index], "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertEqual(tooltip.item, 13510)
        said = [plain(line[1]) for line in tooltip.lines.values()]
        self.assertIn(game.ns.L.TIP_CONS_UNRANKED, said)
        self.assertIn("+1200 Maximum Health", said)

    def test_the_category_filter(self):
        game = self.open_consumables()
        window = game.ns.Browser.window
        open_dropdown(game, window.slot.button)
        self.assertEqual(texts(game.stub.menu)[0], "All")
        find(game.stub.menu, "Food").pick()
        self.assertEqual({row.key for row in self.consumable_rows(game)}, {"food"})
        self.assertEqual(look(window.slot), "active")
        # the slot filter of the other tabs is left as it was
        game.stub.run(window.tabs.buttons[1], "OnClick")
        self.assertEqual(window.slot.label.text, "Slot")
        self.assertEqual(label(window.slot.button), "All")

    def test_a_category_the_spec_lacks_goes_back_to_all(self):
        game = self.open_consumables("MAGE", 2)
        window = game.ns.Browser.window
        open_dropdown(game, window.slot.button)
        find(game.stub.menu, "Mana potions").pick()
        self.assertEqual({row.key for row in self.consumable_rows(game)}, {"mana"})
        state = game.ns.Browser.state
        state["class"], state.spec = "WARRIOR", 2
        game.stub.run(window.list.buttons[2], "OnClick")
        self.assertIsNone(state.category)
        self.assertGreater(len({row.key for row in self.consumable_rows(game)}), 1)

    def test_the_consumables_follow_the_list_and_the_phase(self):
        import consumable_lists
        game = self.open_consumables("HUNTER", 2)
        window = game.ns.Browser.window
        built = consumable_lists.build(self.db)["HUNTER"][2]
        food = lambda: [row.id for row in self.consumable_rows(game) if row.key == "food"]
        wanted = lambda mode: [entry[0] for entry in consumable_lists.shown(built[mode]["food"].ranked, phases.CURRENT)]
        self.assertEqual(food(), wanted("pve"))
        game.stub.run(window.list.buttons[2], "OnClick")
        self.assertEqual(food(), wanted("pvp"))
        game.ns.SetPhase(game.ns, EVERYTHING)
        self.assertEqual({row.key for row in self.consumable_rows(game)} >= {"flask", "food"}, True)

    def test_without_alternatives_a_category_shows_its_best(self):
        game = self.open_consumables()
        window = game.ns.Browser.window
        game.stub.run(window.alts, "OnClick")
        ranked = [row for row in self.consumable_rows(game) if not row.unranked and not row.twin]
        self.assertEqual(len(ranked), len({row.key for row in ranked}))

    def test_the_best_stone_is_shown_for_both_kinds_of_weapon(self):
        game = self.open_consumables("PALADIN", 3)
        game.stub.run(game.ns.Browser.window.alts, "OnClick")
        stones = [row for row in self.consumable_rows(game) if row.key == "weapon"]
        self.assertEqual([(row.id, row.bis) for row in stones], [(12404, True), (12643, True)])

    def test_compact_rows_apply_to_consumables(self):
        game = self.open_consumables()
        game.stub.run(game.ns.Browser.window.alts, "OnClick")

        def rows():
            return [frame for frame in self.frames(game) if frame.data.kind == "consumable"]

        taught = next(frame for frame in rows() if frame.data.consumable.trainer)
        for frame in rows():
            self.assertEqual((frame.height, frame.icon.width), (ONE_LINE, 30), frame.data.id)
            self.assertFalse(frame.kind.shown, "on one line the picture stands for the source")
        kind = game.ns.Consumables.Kind(taught.data.consumable)
        self.assertEqual(taught.detail.text, kind, "the skill it takes says more than who teaches it")

        game.ns.SetOption(game.ns, "compact", False)
        for frame in rows():
            self.assertEqual((frame.height, frame.icon.width), (ROW, 44), frame.data.id)
            self.assertTrue(frame.kind.shown)
        taught = next(frame for frame in rows() if frame.data.consumable.trainer)
        self.assertEqual((taught.kind.text, taught.detail.text), (kind, "Taught by trainers"))

    def test_a_consumable_tied_to_a_zone_stands_out(self):
        game = self.open_consumables("WARRIOR", 3)
        game.stub.run(game.ns.Browser.window.alts, "OnClick")
        frames = [frame for frame in self.frames(game) if frame.data.kind == "consumable"]
        marked = [frame for frame in frames if frame.zoneMark.shown]
        self.assertIn(274273, [frame.data.id for frame in marked])
        for frame in frames:
            zoned = frame.data.consumable.zone is not None
            self.assertEqual((bool(frame.zoneBack.shown), bool(frame.zoneMark.shown)), (zoned, zoned), frame.data.id)
        game.stub.run(marked[0], "OnEnter")

    def test_the_five_tabs_leave_the_credit_its_room(self):
        for locale in ("enUS", "frFR"):
            game = self.open(locale=locale)
            window = game.ns.Browser.window
            self.assertEqual(len(window.tabs.buttons), 5)
            self.assertLess(window.tabs.width, 400, locale)

    def test_the_new_tabs_are_marked_new(self):
        for locale in ("enUS", "frFR"):
            game = self.open(locale=locale)
            window = game.ns.Browser.window
            buttons = window.tabs.buttons
            for index in (1, 2, 3, 4):   # the consumables have had their day as a new tab
                self.assertIsNone(buttons[index].newBadge, (locale, index))
            for index in (5,):   # Reputations
                tab = buttons[index]
                self.assertEqual(tab.newBadge.text.text, "New", (locale, index))
                self.assertTrue(tab.newBadge.shown)
                game.stub.run(tab, "OnClick")
                self.assertTrue(tab.highlightLocked)
                self.assertTrue(tab.newBadge.shown, "the badge stays on the open tab")
                self.assertEqual(tab.newBadge.points[1][3], "TOPRIGHT", "on the corner, so the credit keeps its room")
            # the dungeons, on the window's side
            self.assertIsNone(window.pages.buttons[1].newBadge, locale)
            self.assertEqual(window.pages.buttons[2].newBadge.text.text, "New", locale)

    def test_the_side_tabs(self):
        """Down the window's right edge: the lists, and the dungeons, as the game's professions have their tabs."""
        game = self.open()
        window, state = game.ns.Browser.window, game.ns.Browser.state
        lists, dungeons = window.pages.buttons[1], window.pages.buttons[2]
        self.assertEqual(len(window.pages.buttons), 2)
        self.assertEqual(state.page, "lists")
        self.assertEqual((bool(lists.checked.shown), bool(dungeons.checked.shown)), (True, False))
        for tab in (lists, dungeons):
            self.assertEqual((tab.width, tab.height), (32, 32))
            self.assertEqual((tab.points[1][1], tab.points[1][2].name, tab.points[1][3], tab.points[1][4]),
                             ("TOPLEFT", "EasyBISWindow", "TOPRIGHT", 0), "outside the window, against its right edge")
            self.assertEqual(tab.back.texture, "Interface\\SpellBook\\SpellBook-SkillLineTab", "the game's own tab")
        self.assertGreaterEqual(lists.points[1][5] - dungeons.points[1][5], 32 + 8, "one under the other")
        self.assertEqual(lists.icon.texture, game.ns.ICON)
        self.assertTrue(dungeons.icon.texture.startswith("Interface\\Icons\\"))
        tooltip = game.lua.globals().GameTooltip
        game.stub.run(lists, "OnEnter")
        self.assertEqual((tooltip.text, tooltip.owner.value), ("Gear lists", "lists"))
        game.stub.run(dungeons, "OnEnter")
        self.assertEqual(tooltip.text, "Dungeons")
        game.stub.run(dungeons, "OnLeave")
        self.assertFalse(tooltip.shown)

        # the dungeons take the middle of the window; the lists' tabs go with the lists
        game.stub.run(window.tabs.buttons[2], "OnClick")
        game.stub.run(dungeons, "OnClick")
        self.assertEqual((state.page, state.tab), ("dungeons", "enchants"))
        self.assertEqual((bool(lists.checked.shown), bool(dungeons.checked.shown)), (False, True))
        self.assertTrue(game.ns.DungeonView.view.shown)
        for hidden in (window.tabs, window.scroll, window.slot, window.reputation, window.add):
            self.assertFalse(hidden.shown)
        for kept in (window.spec, window.list, window.listLabel, window.phase, window.alts, window.options, window.credit):
            self.assertTrue(kept.shown)
        game.stub.run(dungeons, "OnClick")   # the tab already open: nothing changes
        self.assertEqual(state.page, "dungeons")
        # back to the lists: the tab left open is there again
        game.stub.run(lists, "OnClick")
        self.assertEqual((state.page, state.tab), ("lists", "enchants"))
        self.assertFalse(game.ns.DungeonView.view.shown)
        self.assertTrue(window.tabs.shown and window.scroll.shown and window.slot.shown)
        self.assertFalse(window.list.shown, "the enchants have no list")
        self.assertEqual(look(window.tabs.buttons[2]), "lit")
        # the character sheet and the reputations give way to the dungeons too
        for index, shown in ((3, lambda: game.ns.Character.view), (5, lambda: game.ns.ReputationView.view)):
            game.stub.run(window.tabs.buttons[index], "OnClick")
            self.assertTrue(shown().shown)
            game.stub.run(dungeons, "OnClick")
            self.assertFalse(shown().shown)
            game.stub.run(lists, "OnClick")
            self.assertTrue(shown().shown)
        game.ns.Browser.ShowDungeons()
        self.assertEqual(state.page, "dungeons")
        # a tooltip of the window opens clear of the side tabs
        game.stub.run(lists, "OnClick")
        game.stub.run(window.tabs.buttons[1], "OnClick")
        game.stub.run(self.frames(game)[0], "OnEnter")
        self.assertGreaterEqual(tooltip.points[1][4], 32)

    def test_the_consumables_tab_in_french(self):
        game = self.open_consumables(locale="frFR")
        window = game.ns.Browser.window
        self.assertEqual(label(window.tabs.buttons[4]), "Consommables")
        self.assertEqual(window.slot.label.text, "Catégorie")
        data = list(window.rowData.values())
        self.assertEqual(data[1].text, "Flacons")

    # -- the Dungeons tab ---------------------------------------------------------------------

    DESTRUCTION = "EasyBISCharDB = { class = 'WARLOCK', spec = 3, list = 'pve' }"
    DISCIPLINE = "EasyBISCharDB = { class = 'PRIEST', spec = 1, list = 'pve' }"
    FERAL = "EasyBISCharDB = { class = 'DRUID', spec = 2, list = 'pve' }"
    # the view's sizes (UI\Dungeons.lua): what scrolls, a slot of the set, a piece of a run, a faded and a dimmed part
    PANE, TILE, CHIP, FADED, DIM, GREY = 904, 40, 213, 0.22, 0.45, 0.7

    def item_id(self, name: str) -> int:
        return next(item_id for item_id, item in self.db.items.items() if item["name"] == name)

    def open_dungeons(self, saved=DESTRUCTION, alts=False, grid=False, **options):
        """The game on the Dungeons tab, and the tab's view."""
        saved += f" EasyBISDB = {{ listAlts = {str(alts).lower()}, dungeonGrid = {str(grid).lower()} }}"
        game = Game(saved=saved, **options)
        game.ns.Browser.Open()
        game.stub.run(game.ns.Browser.window.pages.buttons[2], "OnClick")
        return game, game.ns.DungeonView.view

    @staticmethod
    def lanes(view) -> list:
        return [lane for lane in view.lanes.values() if lane.shown]

    @staticmethod
    def chips(lane) -> list:
        return [chip for chip in lane.chips.values() if chip.shown]

    def chip_of(self, view, name: str):
        wanted = self.item_id(name)
        return next(chip for lane in self.lanes(view) for chip in self.chips(lane) if chip.entry.piece.id == wanted)

    def test_dungeons_tab(self):
        game = Game(saved=self.DESTRUCTION + " EasyBISDB = { listAlts = false }")
        game.ns.Browser.Open()
        window = game.ns.Browser.window
        self.assertIsNone(game.ns.DungeonView.view, "the tab is made when it is first asked for")
        game.stub.run(window.pages.buttons[2], "OnClick")
        view = game.ns.DungeonView.view
        self.assertTrue(view.shown)
        self.assertTrue(window.pages.buttons[2].checked.shown)
        for hidden in (window.slot, window.source, window.zone, window.reputation, window.add, window.scroll, window.tabs):
            self.assertFalse(hidden.shown)
        for kept in (window.spec, window.list, window.phase, window.alts):
            self.assertTrue(kept.shown)

        model = view.model
        self.assertGreater(model.need, 0)
        self.assertEqual(plain(view.summary.text), f"{model.need} best picks to farm  ·  {model.dungeons} dungeons")
        self.assertEqual(look(view.mode.buttons[1]), "lit", "a band per dungeon until the player asks for the grid")
        self.assertTrue(view.runsPane.shown)
        self.assertFalse(view.gridPane.shown or view.gridHead.shown)
        self.assertFalse(view.empty.shown)

        # the set: every slot, a piece of no dungeon in black and white, and a little darker
        tiles = list(view.tiles.values())
        self.assertEqual([(tile.piece.slot, tile.piece.rank) for tile in tiles],
                         [(cell.slot, cell.rank) for cell in model.sheet.values()])
        self.assertEqual(len(tiles), 17)
        for tile in tiles:
            held = tile.piece.runs is not None
            self.assertEqual((tile.alpha, bool(tile.icon.art.desaturated), bool(tile.grey)),
                             (1 if held else self.GREY, not held, not held), tile.piece.slot)
            self.assertEqual(tile.rest, tile.alpha)
            self.assertFalse(tile.icon.check.shown or tile.glow.shown)
        self.assertTrue(any(tile.grey for tile in tiles) and any(not tile.grey for tile in tiles))
        lefts = [tile.points[1][4] for tile in tiles]
        self.assertTrue(all(after - before >= self.TILE + 5 for before, after in zip(lefts, lefts[1:])), lefts)
        self.assertGreater(lefts[10] - lefts[9], lefts[9] - lefts[8], "room before the rings")
        self.assertLessEqual(lefts[-1] + self.TILE, self.PANE)

        # a band per run, the one with the most to get first, each under the one before
        lanes = self.lanes(view)
        self.assertEqual([lane.run.key for lane in lanes], [run.key for run in model.runs.values()])
        offset = None
        for lane in lanes:
            run = lane.run
            self.assertEqual((lane.count.text, lane.count.shown), (str(len(self.chips(lane))), True),
                             f"{run.key}: the number of pieces the line shows")
            self.assertEqual(lane.name.text, run.name)
            self.assertEqual(lane.name.points[1][5], 8 if run.noWing else 0,
                             f"{run.key}: the name alone in the middle of its band, or over its note")
            self.assertIsNone(lane.pips, "no square under the name: the count and the pieces say it")
            top = -lane.points[1][5]
            if offset is not None:
                self.assertEqual(top, offset, run.key)
            offset = top + lane.height + 6
            chips = self.chips(lane)
            self.assertEqual([chip.entry.piece.id for chip in chips], [entry.piece.id for entry in run.entries.values()])
            for chip in chips:
                self.assertFalse(chip.tag.shown)
                self.assertLessEqual(chip.points[1][4] + self.CHIP, self.PANE)
                self.assertLessEqual(-chip.points[1][5] + chip.height, lane.height)
        turban = self.chip_of(view, "Spellweaver's Turban")
        self.assertEqual(turban.run.key, "229:u")
        self.assertEqual(strip_colors(turban.name.text), "Spellweaver's Turban")
        self.assertRegex(plain(turban.sub.text), r"^General Drakkisath  \d+%$")
        self.assertFalse(turban.icon.quest.shown)
        self.assertEqual(plain(self.chip_of(view, "Sublime Wristguards").sub.text).split("  ")[0], "2 bosses")

        # what no dungeon holds, in one line
        shown = [button for button in view.elsewhere.values() if button.shown]
        self.assertEqual([button.category for button in shown], [entry.category for entry in model.elsewhere.values()])
        total = sum(entry.count for entry in model.elsewhere.values())
        self.assertEqual(view.elsewhereLabel.text, f"{total} best picks from elsewhere:")
        self.assertEqual(plain(shown[0].text.text), f"{model.elsewhere[1].count} {game.ns.Sources.CategoryName(shown[0].category)}")
        self.assertEqual(model.need + model.got + total, sum(1 for cell in model.sheet.values() if cell.id))

        # leaving the tab hides it
        game.stub.run(window.pages.buttons[1], "OnClick")
        self.assertFalse(view.shown)
        self.assertTrue(window.scroll.shown and window.slot.shown and window.tabs.shown)

    def busy_spec(self) -> str:
        """The saved character of a spec with a run that holds two best picks: Destruction Warlock's, or else the
        first spec's that has one."""
        game = Game()
        game.ns.SetOption(game.ns, "listAlts", False)
        for token, spec in [("WARLOCK", 3)] + [(token, spec) for token in test_addon.CLASSES for spec in self.kept[token]]:
            model = game.ns.Dungeons.For(game.lua.table_from({"class": token, "spec": spec, "list": "pve"}))
            if any(run.need == 2 for run in model.runs.values()):
                return f"EasyBISCharDB = {{ class = '{token}', spec = {spec}, list = 'pve' }}"
        self.fail("no spec has a run that holds two best picks")

    def test_dungeons_light_what_the_mouse_is_on(self):
        game, view = self.open_dungeons(self.busy_spec())
        busy = next(lane for lane in self.lanes(view) if lane.run.need == 2)   # a run that holds two best picks
        key, name = busy.run.key, busy.run.name
        chip, sibling = self.chips(busy)
        tiles = {(tile.piece.slot, tile.piece.rank): tile for tile in view.tiles.values()}
        mine = tiles[chip.entry.piece.slot, chip.entry.piece.rank]
        same = tiles[sibling.entry.piece.slot, sibling.entry.piece.rank]
        other = next(tile for tile in view.tiles.values() if tile.piece.runs is not None and tile.piece.runs[key] is None)
        game.stub.run(chip, "OnEnter")
        self.assertEqual((mine.alpha, mine.glow.shown), (1, True))
        self.assertEqual((same.alpha, same.glow.shown), (self.FADED, False),
                         "another piece of the same run is not what the mouse is on")
        self.assertEqual(other.alpha, self.FADED)
        for lane in self.lanes(view):
            self.assertEqual(lane.alpha, 1 if lane.run.key == key else 0.35, lane.run.key)
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        where = r" - (.+ \(\d+(\.\d)?%\)|reward of the quest .+\. One run is enough\.)"   # a boss's drop, or a quest's reward
        self.assertTrue(any(re.fullmatch(re.escape(name) + where, text) for text in said), said)
        self.assertIn("Click: the pieces of this slot. Shift-click: link it.", said)
        game.stub.run(chip, "OnLeave")
        self.assertEqual([tile.alpha for tile in view.tiles.values()], [tile.rest for tile in view.tiles.values()])
        self.assertTrue(all(lane.alpha == 1 for lane in self.lanes(view)))
        self.assertFalse(any(tile.glow.shown for tile in view.tiles.values()))
        # a run lights every slot it holds; a slot of the set lights its run
        game.stub.run(busy, "OnEnter")
        self.assertEqual((mine.alpha, same.alpha, other.alpha), (1, 1, self.FADED))
        game.stub.run(busy, "OnLeave")
        game.stub.run(mine, "OnEnter")
        self.assertEqual(busy.alpha, 1)
        self.assertTrue(all(lane.alpha == 0.35 for lane in self.lanes(view) if lane.run.key != key))
        game.stub.run(mine, "OnLeave")
        # a slot of no dungeon lights nothing, and says where its piece comes from
        elsewhere = next(tile for tile in view.tiles.values() if tile.piece.id and tile.piece.runs is None)
        game.stub.run(elsewhere, "OnEnter")
        self.assertTrue(all(lane.alpha == 1 for lane in self.lanes(view)))
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertTrue(any(text.startswith("Source: ") for text in said), said)

    def test_dungeon_pieces_open_their_slot_or_link(self):
        game, view = self.open_dungeons()
        state = game.ns.Browser.state
        turban = self.item_id("Spellweaver's Turban")
        game.stub.itemNames[turban] = "Spellweaver's Turban"
        chip = self.chip_of(view, "Spellweaver's Turban")
        game.stub.modifier = True
        game.stub.run(chip, "OnClick")
        self.assertIn(f"item:{turban}", game.stub.linked, "Shift-click links the item")
        self.assertEqual(state.page, "dungeons")
        game.stub.modifier = False
        state.tab = "reputations"   # whatever the lists were left on
        game.stub.run(chip, "OnClick")
        self.assertEqual((state.page, state.tab, state.slot), ("lists", "items", "head"))
        self.assertFalse(view.shown)
        self.assertTrue(game.ns.Browser.window.tabs.shown)
        # from the set
        game.stub.run(game.ns.Browser.window.pages.buttons[2], "OnClick")
        tile = next(tile for tile in view.tiles.values() if tile.piece.slot == "neck")
        game.stub.run(tile, "OnClick")
        self.assertEqual((state.page, state.tab, state.slot), ("lists", "items", "neck"))

    def test_dungeons_elsewhere_opens_the_items(self):
        game, view = self.open_dungeons()
        state = game.ns.Browser.state
        state.slot = "head"
        button = view.elsewhere[1]
        game.stub.run(button, "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertEqual(tooltip.text, game.ns.Sources.CategoryName(button.category))
        self.assertEqual([plain(line[1]) for line in tooltip.lines.values()], ["Click: these pieces in the Items tab."])
        game.stub.run(button, "OnClick")
        self.assertEqual((state.page, state.tab, state.source, state.slot), ("lists", "items", button.category, None))
        rows = [row for row in game.ns.Browser.window.rowData.values() if row.kind == "item"]
        self.assertTrue(rows and all(row.source.category == button.category for row in rows))

    def test_dungeons_count_what_the_player_has(self):
        game, view = self.open_dungeons(self.busy_spec())
        before = view.model.need
        busy = next(lane for lane in self.lanes(view) if lane.run.need == 2)   # a run that holds two best picks
        key = busy.run.key
        first, second = (chip.entry.piece.id for chip in self.chips(busy))
        slot = self.chips(busy)[0].entry.piece.slot
        game.stub.itemCounts[first] = 1
        game.stub.fire("BAG_UPDATE_DELAYED")
        self.assertEqual(plain(view.summary.text),
                         f"{before - 1} best picks to farm  ·  {view.model.dungeons} dungeons  ·  1 already yours")
        lane = next(lane for lane in self.lanes(view) if lane.run.key == key)
        chip, sibling = self.chips(lane)
        self.assertEqual((chip.entry.piece.id, sibling.entry.piece.id), (first, second))
        self.assertTrue(chip.icon.check.shown)
        self.assertEqual((chip.name.alpha, chip.sub.alpha), (self.DIM, self.DIM))
        self.assertEqual(sibling.name.alpha, 1)
        self.assertEqual(lane.count.text, "2", "the line still shows both")
        tile = next(tile for tile in view.tiles.values() if tile.piece.id == first and tile.piece.slot == slot)
        self.assertTrue(tile.icon.check.shown)
        self.assertEqual(tile.alpha, 1)
        # the run done: its count gives way to a check, and it goes after the others
        game.stub.equipped[second] = True
        game.stub.fire("PLAYER_EQUIPMENT_CHANGED")
        last = self.lanes(view)[-1]
        self.assertEqual(last.run.key, key)
        self.assertEqual((last.count.text, last.band.shown), ("2", False), "its colour goes, its count stays")
        # every dungeon piece in hand
        for cell in view.model.sheet.values():
            if cell.id:
                game.stub.itemCounts[cell.id] = 1
        game.stub.fire("BAG_UPDATE_DELAYED")
        self.assertEqual(plain(view.summary.text), "Every best pick the dungeons hold is yours.")
        self.assertIn("|cffffd100", view.summary.text)
        # a hidden tab does not follow the bags
        game.stub.run(game.ns.Browser.window.pages.buttons[1], "OnClick")
        game.stub.fire("BAG_UPDATE_DELAYED")
        self.assertFalse(view.shown)

    def test_dungeons_alternatives(self):
        game, view = self.open_dungeons()
        window = game.ns.Browser.window
        without = len(self.lanes(view))
        self.assertFalse(any(chip.tag.shown for lane in self.lanes(view) for chip in self.chips(lane)))
        game.stub.run(window.alts, "OnClick")
        self.assertTrue(game.ns.db.listAlts)
        lanes = self.lanes(view)
        self.assertGreater(len(lanes), without)
        tagged = [chip for lane in lanes for chip in self.chips(lane) if chip.tag.shown]
        self.assertTrue(tagged)
        self.assertTrue(all(not chip.entry.piece.best and chip.tag.text == "Alt" for chip in tagged))
        self.assertTrue(all(chip.icon.border.width < 38 for chip in tagged), "an alternative's picture is smaller")
        self.assertEqual(self.chip_of(view, "Spellweaver's Turban").icon.border.width, 38)
        # a run that holds alternatives only says so in place of a count
        only = [lane for lane in lanes if lane.run.need == 0]
        self.assertTrue(only)
        self.assertTrue(all(lane.count.text == str(lane.run.alts) for lane in only), "the alternatives are in the line")
        # the number at the head of a line is the pieces the line shows, best picks and alternatives alike
        for lane in lanes:
            self.assertEqual(lane.count.text, str(len(self.chips(lane))), lane.run.key)
            self.assertEqual(lane.run.total, lane.run.need + lane.run.got + lane.run.alts)
        self.assertEqual(lanes[-1].run.need, 0, "after the runs with something to get")
        # more pieces than a line holds: the band grows, and the next one makes room
        tall = [lane for lane in lanes if len(self.chips(lane)) > 3]
        for lane in tall:
            self.assertGreaterEqual(lane.height, 2 * 46)
        tops = [-lane.points[1][5] for lane in lanes]
        for lane, top, after in zip(lanes, tops, tops[1:]):
            self.assertEqual(after, top + lane.height + 6)
        # the slot's best pick in hand: its alternatives fade
        game.stub.itemCounts[self.item_id("Spellweaver's Turban")] = 1
        game.stub.fire("BAG_UPDATE_DELAYED")
        heads = [chip for lane in self.lanes(view) for chip in self.chips(lane)
                 if chip.entry.piece.slot == "head" and not chip.entry.piece.best]
        self.assertTrue(heads)
        self.assertTrue(all(chip.name.alpha == self.DIM and chip.icon.art.alpha == self.DIM for chip in heads))

    def test_dungeons_grid(self):
        game, view = self.open_dungeons()
        model = view.model
        game.stub.run(view.mode.buttons[2], "OnClick")
        self.assertTrue(game.ns.db.dungeonGrid)
        self.assertTrue(game.lua.globals().EasyBISDB.dungeonGrid, "the choice is kept")
        self.assertEqual(look(view.mode.buttons[2]), "lit")
        self.assertTrue(view.gridPane.shown and view.gridHead.shown)
        self.assertFalse(view.runsPane.shown)
        model = view.model
        # a column per run, in the order of the bands
        headers = [header for header in view.headers.values() if header.shown]
        self.assertEqual([header.run.key for header in headers], [run.key for run in model.runs.values()])
        self.assertEqual([(header.count.text, header.short.text) for header in headers],
                         [(str(run.total), run.short) for run in model.runs.values()])
        lefts = [header.points[1][4] for header in headers]
        width = headers[0].width
        self.assertTrue(all(after - before == width + 3 for before, after in zip(lefts, lefts[1:])))
        self.assertGreaterEqual(lefts[0], 250)
        self.assertLessEqual(lefts[-1] + width + 150, self.PANE, "the last column keeps its room")
        # a line per piece, in the order of the character sheet
        rows = [row for row in view.rows.values() if row.shown]
        self.assertEqual([row.piece.id for row in rows], [piece.id for piece in model.rows.values()])
        self.assertEqual([-row.points[1][5] for row in rows], [index * 28 for index in range(len(rows))])
        turban = next(row for row in rows if row.piece.id == self.item_id("Spellweaver's Turban"))
        self.assertEqual(turban.used, 1)
        cell = turban.cells[1]
        self.assertTrue(cell.back.shown and cell.text.shown and not cell.check.shown)
        self.assertRegex(cell.text.text, r"^\d+%$")
        column = next(index for index, header in enumerate(headers) if header.run.key == "229:u")
        self.assertEqual((cell.back.points[1][4], cell.back.width), (lefts[column], width), "under its run's name")
        self.assertFalse(turban.where.shown)
        self.assertEqual(turban.name.alpha, 1)
        # a piece of no dungeon: dimmed, with where it comes from in the last column
        crafted = next(row for row in rows if row.piece.runs is None)
        self.assertEqual((crafted.used, crafted.name.alpha, crafted.icon.art.alpha), (0, self.DIM, self.DIM))
        self.assertTrue(crafted.where.shown)
        self.assertEqual(plain(crafted.where.text), game.ns.Sources.Short(crafted.piece.source)
                         + ("" if crafted.piece.source.origin in ("f", "s", "w") else " *"))
        self.assertGreater(crafted.where.points[1][4], lefts[-1] + width)
        self.assertEqual(sum(1 for row in rows if row.used == 0), sum(1 for row in rows if row.piece.runs is None))
        # the tooltip and the click are a piece's, as in the bands
        game.stub.run(turban, "OnEnter")
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertTrue(any(text.startswith("Upper Blackrock Spire - ") for text in said), said)
        game.stub.run(headers[column], "OnEnter")
        self.assertEqual(game.lua.globals().GameTooltip.text, "Upper Blackrock Spire", "a column's short name in full")
        game.stub.run(turban, "OnClick")
        self.assertEqual((game.ns.Browser.state.tab, game.ns.Browser.state.slot), ("items", "head"))
        # what the player has is checked in its cell
        game.stub.itemCounts[turban.piece.id] = 1
        game.stub.run(game.ns.Browser.window.pages.buttons[2], "OnClick")
        turban = next(row for row in view.rows.values() if row.shown and row.piece.id == turban.piece.id)
        self.assertTrue(turban.cells[1].check.shown and not turban.cells[1].text.shown)
        self.assertEqual(turban.name.alpha, self.DIM)
        # back to the bands, and the grid again for the next session
        game.stub.run(view.mode.buttons[1], "OnClick")
        self.assertTrue(view.runsPane.shown and not view.gridPane.shown and not view.gridHead.shown)
        again, grid = self.open_dungeons(grid=True)
        self.assertTrue(grid.gridPane.shown and not grid.runsPane.shown)
        self.assertEqual(look(grid.mode.buttons[2]), "lit")

    def test_dungeons_grid_with_alternatives(self):
        for count in (2, 6):
            game, view = self.open_dungeons(alts=True, grid=True)
            game.ns.SetAlternatives(game.ns, count)
            model = view.model
            headers = [header for header in view.headers.values() if header.shown]
            rows = [row for row in view.rows.values() if row.shown]
            self.assertEqual(len(rows), len(model.rows))
            self.assertGreater(len(rows), 17)
            width = headers[0].width
            self.assertGreaterEqual(width, 30)
            self.assertLessEqual(headers[-1].points[1][4] + width, self.PANE, f"{len(headers)} runs fit")
            # an alternative is set in from its slot's best pick; the first line of a slot is marked
            alternative = next(row for row in rows if not row.piece.best)
            best = next(row for row in rows if row.piece.best)
            self.assertGreater(alternative.icon.border.points[1][4], best.icon.border.points[1][4])
            self.assertEqual(sum(1 for row in rows if row.piece.first),
                             len({row.piece.slot for row in rows}))
            for row in rows:
                self.assertEqual(row.used, len(list(row.piece.order.values())) if row.piece.order else 0)

    def test_dungeons_say_a_quest(self):
        game, view = self.open_dungeons(saved=self.DISCIPLINE)
        rose = self.chip_of(view, "Penelope's Rose")
        self.assertEqual(rose.run.key, "289")
        self.assertTrue(rose.icon.quest.shown, "the game's quest mark on the piece")
        self.assertIn("AvailableQuestIcon", rose.sub.text)
        self.assertEqual(plain(rose.sub.text), "Kirtonos the Herald", "the quest's title in place of a boss, and no rate")
        self.assertIsNone(rose.entry.percent)
        lane = next(lane for lane in self.lanes(view) if lane.run.key == "289")
        self.assertEqual(rose.run.need, sum(1 for chip in self.chips(lane) if chip.entry.piece.best),
                         "a quest's reward counts as a piece to get there")
        game.stub.run(rose, "OnEnter")
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Scholomance - reward of the quest Kirtonos the Herald. One run is enough.", said)
        tile = next(tile for tile in view.tiles.values() if tile.piece.id == rose.entry.piece.id)
        self.assertFalse(tile.grey or tile.icon.art.desaturated, "a dungeon's piece in the set")
        # in the grid: the quest mark in the run's cell
        game.stub.run(view.mode.buttons[2], "OnClick")
        row = next(row for row in view.rows.values() if row.shown and row.piece.id == rose.entry.piece.id)
        self.assertEqual(row.used, 1)
        self.assertIn("AvailableQuestIcon", row.cells[1].text.text)
        self.assertTrue(row.icon.quest.shown)

    def test_dungeons_say_when_no_wing_is_named(self):
        """Stratholme alone, next to Stratholme: Undead, would pass for the other wing."""
        game, view = self.open_dungeons(saved=self.DISCIPLINE, alts=True)
        lanes = {lane.run.key: lane for lane in self.lanes(view)}
        if "329" not in lanes:
            self.skipTest("the data places every piece of Stratholme in a wing by now")
        whole = lanes["329"]
        self.assertEqual((whole.name.text, whole.note.shown, whole.note.text), ("Stratholme", True, "wing not named"))
        self.assertEqual(whole.note.points[1][4], whole.name.points[1][4], "under the name")
        self.assertGreater(whole.name.points[1][5], 0)
        self.assertLess(whole.note.points[1][5], 0)
        for key, lane in lanes.items():
            self.assertEqual(bool(lane.note.shown), key in ("329", "429", "229", "189"), key)
        game.stub.run(self.chips(whole)[0], "OnEnter")
        said = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertTrue(any(text.startswith("Stratholme (wing not named) - ") for text in said), said)
        # in the grid: the column's name in full says it too
        game.stub.run(view.mode.buttons[2], "OnClick")
        header = next(header for header in view.headers.values() if header.shown and header.run.key == "329")
        game.stub.run(header, "OnEnter")
        tooltip = game.lua.globals().GameTooltip
        self.assertEqual((tooltip.text, [line[1] for line in tooltip.lines.values()]), ("Stratholme", ["wing not named"]))

    def test_dungeons_tab_with_no_dungeon(self):
        game, view = self.open_dungeons(saved=self.FERAL, cls="DRUID")
        if view.model.need:
            self.skipTest("the data gives the Feral Druid a dungeon piece by now")
        self.assertEqual(self.lanes(view), [])
        self.assertEqual(view.summary.text, "")
        self.assertTrue(view.empty.shown)
        self.assertEqual(plain(view.empty.text), "No best pick of this spec comes from a dungeon.\n\n"
                         "Turn on Alternatives to see the dungeon pieces that come next.")
        self.assertTrue(all(tile.grey and tile.icon.art.desaturated for tile in view.tiles.values() if tile.piece.id))
        self.assertFalse(any(tile.grey for tile in view.tiles.values() if not tile.piece.id), "an empty slot has no picture")
        self.assertTrue(view.elsewhereLabel.shown)
        # with the alternatives, the dungeons that hold some
        game.stub.run(game.ns.Browser.window.alts, "OnClick")
        self.assertFalse(view.empty.shown)
        lanes = self.lanes(view)
        self.assertTrue(lanes and all(lane.run.need == 0 and lane.count.text == str(lane.run.alts) for lane in lanes))
        # the grid has its lines all the same, and no column
        game.stub.run(game.ns.Browser.window.alts, "OnClick")
        game.stub.run(view.mode.buttons[2], "OnClick")
        self.assertFalse(any(header.shown for header in view.headers.values()))
        self.assertTrue(all(row.where.shown for row in view.rows.values() if row.shown))

    def test_dungeons_follow_the_spec_the_list_and_the_phase(self):
        game, view = self.open_dungeons()
        state = game.ns.Browser.state
        before = [run.key for run in view.model.runs.values()]
        state["class"], state.spec = "WARRIOR", 2
        game.ns.SetOption(game.ns, "minimap", not game.ns.db.minimap)   # any option change refreshes
        self.assertNotEqual([run.key for run in view.model.runs.values()], before)
        self.assertEqual([lane.run.key for lane in self.lanes(view)], [run.key for run in view.model.runs.values()])
        for token in test_addon.CLASSES:
            for spec in self.kept[token]:
                for mode in ladders.MODES:
                    for grid in (False, True):
                        state["class"], state.spec, state.list = token, spec, mode
                        game.ns.SetOption(game.ns, "dungeonGrid", grid)
                        game.ns.SetOption(game.ns, "minimap", not game.ns.db.minimap)
                        self.assertEqual(bool(view.grid), grid)
                        self.assertEqual(len(self.lanes(view)) if not grid else
                                         len([header for header in view.headers.values() if header.shown]),
                                         len(view.model.runs), (token, spec, mode, grid))

    def test_dungeons_in_french(self):
        game, view = self.open_dungeons(locale="frFR")
        window = game.ns.Browser.window
        game.stub.run(window.pages.buttons[1], "OnEnter")
        self.assertEqual(game.lua.globals().GameTooltip.text, "Listes d'équipement")
        game.stub.run(window.pages.buttons[2], "OnEnter")
        self.assertEqual(game.lua.globals().GameTooltip.text, "Donjons")
        self.assertEqual([label(button) for button in view.mode.buttons.values()], ["Par donjon", "Par pièce"])
        self.assertEqual(plain(view.summary.text), f"{view.model.need} pièces BIS à farmer  ·  {view.model.dungeons} donjons")
        names = [lane.name.text for lane in self.lanes(view)]
        self.assertIn("Sommet du pic Blackrock", names)
        self.assertIn("Stratholme : Vivants", names)
        self.assertTrue(view.elsewhereLabel.text.endswith("pièces BIS viennent d'ailleurs :"))


@unittest.skipIf(lupa is None, "lupa is not installed")
class CostWindowTest(unittest.TestCase):
    """The price of what a vendor sells for a currency, in the window."""
    REAL, REAL_CURRENCY, CLOAK = 226404, 3469, 272411   # the best back of a Balance Druid, sold for 75 Reals
    BALANCE = "EasyBISCharDB = { class = 'DRUID', spec = 1, list = 'pve' }"

    def open(self, **options) -> Game:
        game = Game(cls="DRUID", saved=self.BALANCE, **options)
        game.ns.Browser.Open()
        return game

    def row(self, game, item_id):
        window = game.ns.Browser.window
        return next(window.rows[index] for index in range(1, len(window.rowData) + 1)
                    if window.rowData[index].id == item_id)

    def sheet(self, game):
        game.stub.run(game.ns.Browser.window.tabs.buttons[3], "OnClick")
        return game.ns.Character.view

    def test_a_row_says_the_price_first(self):
        game = self.open()
        self.assertEqual(plain(self.row(game, self.CLOAK).detail.text), "75 Reals · Pix Xizzix - Map 1434")
        self.assertIn("|T134400:", self.row(game, self.CLOAK).detail.text, "the currency's picture")
        game.ns.SetOption(game.ns, "compact", False)
        self.assertEqual(plain(self.row(game, self.CLOAK).detail.text), "75 Reals · Pix Xizzix - Map 1434")

    def test_the_tooltip_says_what_is_missing(self):
        game = self.open()
        game.stub.itemCounts[self.REAL] = 38
        game.stub.run(self.row(game, self.CLOAK), "OnEnter")
        lines = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Cost: 75 Reals (you have 38, 37 missing)", lines)
        self.assertNotIn("Price from the Forever beta, not confirmed in the game.", lines, "read at the vendor")

    def test_the_tooltip_says_when_the_price_is_the_betas(self):
        game = self.open()
        game.ns.Items.Get(self.CLOAK).sources[1][7] = f"{self.REAL}:75:b"
        game.ns.Browser.Open()
        game.stub.run(self.row(game, self.CLOAK), "OnEnter")
        lines = [plain(line[1]) for line in game.lua.globals().GameTooltip.lines.values()]
        self.assertIn("Price from the Forever beta, not confirmed in the game.", lines)

    def test_the_sheet_counts_what_is_left_to_pay(self):
        game = self.open()
        view = self.sheet(game)
        cells = {(cell.data.slot, cell.data.rank): cell for cell in view.cells.values()}
        self.assertEqual(plain(cells[("back", 1)].where.text), "75 Reals · Map 1434")
        priced = {cell.data.id: cell.data.source.cost.amount for cell in view.cells.values()
                  if cell.data.source and cell.data.source.cost}
        total = sum(priced.values())
        self.assertTrue(view.cost.shown)
        self.assertEqual(plain(view.cost.text), f"Reals for this set: {total} (you have 0)")
        self.assertIn("|T134400:", view.cost.text, "the currency's picture")

        game.stub.equipped[self.CLOAK] = True   # worn: paid for
        game.stub.currencies[self.REAL_CURRENCY] = 38
        game.stub.fire("BAG_UPDATE_DELAYED")
        self.assertEqual(plain(view.cost.text), f"Reals for this set: {total - 75} (you have 38)")

        for item_id in priced:                  # all of it in the bags: nothing is left to say
            game.stub.itemCounts[item_id] = 1
        game.stub.fire("CURRENCY_DISPLAY_UPDATE")
        self.assertFalse(view.cost.shown)

    def test_a_set_without_a_price_says_nothing(self):
        game = Game(saved=ENHANCEMENT)
        game.ns.Browser.Open()
        view = self.sheet(game)
        priced = [cell for cell in view.cells.values() if cell.data.source and cell.data.source.cost]
        self.assertEqual(view.cost.shown, bool(priced))


if __name__ == "__main__":
    unittest.main(verbosity=1)
