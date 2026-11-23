"""Scope, loot sources and item constraints for alternatives outside the normal ranking."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import fdb
import notes
import situational_gear as gear
from test_addon import CLASSES, Game, lupa, strip_colors


class SituationalGearTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        gear.include(cls.db)

    def test_dawn_rewards_are_scoped_to_offensive_profiles_and_the_same_equip_limit(self):
        self.assertEqual(gear.item_ids("PALADIN", 3, "pve", "trinket"), (19812, 13209))
        for player_class, index, wanted in (
                ("DRUID", 4, 13209), ("HUNTER", 2, 13209), ("ROGUE", 3, 13209),
                ("SHAMAN", 2, 13209), ("DRUID", 1, 19812), ("PALADIN", 4, 19812),
                ("PRIEST", 3, 19812), ("MAGE", 2, 19812), ("WARLOCK", 3, 19812)):
            with self.subTest(player_class=player_class, index=index):
                self.assertEqual(gear.item_ids(player_class, index, "pve", "trinket"), (wanted,))
        for player_class, index in (("DRUID", 3), ("PALADIN", 1), ("PRIEST", 1), ("PRIEST", 2), ("SHAMAN", 3)):
            self.assertEqual(gear.item_ids(player_class, index, "pve", "trinket"), ())
        self.assertEqual(self.db.quest_places[5213], (329, "u"))
        for item in (19812, 13209):
            self.assertEqual(self.db.gear[item]["stats"], {})
            self.assertEqual(self.db.items[item]["limit"], "TrinketoftheDawn")
            self.assertEqual(self.db.items[item]["sources"][0][0:2], ["q", "5213"])
            self.assertEqual(self.db.items[item]["side"], "")

    def test_defensive_and_threat_options_keep_their_tested_role_and_slot(self):
        self.assertEqual(gear.item_ids("DRUID", 2, "pve", "trinket"), (11810, 17774))
        self.assertEqual(gear.item_ids("PALADIN", 2, "pve", "trinket"), (11810,))
        self.assertEqual(gear.item_ids("WARRIOR", 3, "pve", "trinket"), (11810, 13209))
        self.assertEqual(gear.item_ids("WARRIOR", 3, "pve", "off"), (1168,))
        self.assertEqual(gear.item_ids("PALADIN", 2, "pve", "off"), ())
        self.assertEqual(gear.item_ids("WARRIOR", 3, "pve", "main"), ())
        self.assertEqual(gear.item_ids("WARRIOR", 3, "pvp", "off"), ())
        self.assertEqual(self.db.quest_places[7067], (349, ""))

    def test_ramstein_is_a_pvp_control_from_a_dungeon_for_every_spec(self):
        for cls, entry in self.db.classes.items():
            for spec in entry["specs"]:
                with self.subTest(cls=cls, spec=spec):
                    self.assertEqual(gear.item_ids(cls, spec, "pvp", "trinket"), (13515,))
                    self.assertNotIn(13515, gear.item_ids(cls, spec, "pve", "trinket"))
        drop = self.db.items[13515]
        self.assertEqual((drop["side"], drop["groups"]), ("", frozenset("d")))
        self.assertEqual(drop["sources"][0][:3], ["d", "329", "Ramstein the Gorger"])

    def test_import_leaves_native_gear_pools_and_upstream_facts_intact(self):
        db = fdb.Database()
        db.classes["WARRIOR"] = {"pools": {"trinket": []}}
        db.items[13515] = {"name": "Newer native record"}
        db.gear[13515] = {"req": 56}
        db.quest_places[5213] = (329, "")
        gear.include(db)
        first_import = deepcopy((db.items, db.gear, db.quest_places))
        gear.include(db)
        self.assertEqual((db.items, db.gear, db.quest_places), first_import)
        self.assertEqual(db.items[13515], {"name": "Newer native record"})
        self.assertEqual(db.gear[13515], {"req": 56})
        self.assertEqual(db.quest_places[5213], (329, ""))
        self.assertEqual(db.classes["WARRIOR"]["pools"], {"trinket": []})

    def test_each_option_has_a_bilingual_note_in_its_own_mode_and_slot(self):
        written = gear.notes()
        notes.check(self.db, written)
        for cls, entry in self.db.classes.items():
            for spec in entry["specs"]:
                for mode in ("pve", "pvp"):
                    for slot in ("trinket", "off"):
                        matching = [row["items"][0] for row in written if row["list"] == mode
                                    and row["slot"] == slot and ("specs" not in row or f"{cls} {spec}" in row["specs"])]
                        with self.subTest(cls=cls, spec=spec, mode=mode, slot=slot):
                            self.assertEqual(tuple(matching), gear.item_ids(cls, spec, mode, slot))
                            self.assertEqual(len(matching), len(set(matching)))


@unittest.skipIf(lupa is None, "lupa is not installed")
class SituationalGearClientTest(unittest.TestCase):
    def test_lua_keeps_the_requested_number_of_picks_alongside_pre_raid_options(self):
        game = Game()
        ladders = game.ns.Ladders
        for cls in CLASSES:
            data = ladders.Decode(cls)
            for spec in data.order.values():
                slots = ("trinket", "off") if (cls, spec) == ("WARRIOR", 3) else ("trinket",)
                for mode in ("pve", "pvp"):
                    for side in ("a", "h"):
                        for count in (2, 6):
                            for phase in (0, 1):
                                flt = game.lua.table(side=side, phase=phase, alternatives=count, pvpRewards=False,
                                                     rankCap=6, seenOnly=False, unsourced=False)
                                picks = ladders.Compute(data, spec, mode, flt)
                                for slot in slots:
                                    with self.subTest(cls=cls, spec=spec, mode=mode, slot=slot, faction=side,
                                                      count=count, phase=phase):
                                        ordinary = []
                                        extras = []
                                        shelf = picks[slot]
                                        displayed = [pick.id for group in (shelf.best, shelf.alts) for pick in group.values()]
                                        for pick in shelf.best.values():
                                            self.assertFalse(ladders.HasFlag(pick.entry, "j"))
                                            ordinary.append(pick.id)
                                        for pick in shelf.alts.values():
                                            if ladders.HasFlag(pick.entry, "j"):
                                                self.assertTrue(ladders.Unscored(pick.entry))
                                                self.assertFalse(ladders.IsTie(shelf, pick))
                                                extras.append(pick.id)
                                            else:
                                                ordinary.append(pick.id)
                                        expected = gear.item_ids(cls, spec, mode, slot)
                                        self.assertEqual(len(ordinary), 1 + count)
                                        self.assertEqual(tuple(extras), expected if phase == 0 else ())
                                        self.assertTrue(set(expected).isdisjoint(ordinary))
                                        self.assertEqual(len(set(displayed)), len(displayed))
                                        if (cls, spec, mode, phase) == ("DRUID", 2, "pve", 0):
                                            # Preserve the bear's regular choices around Force of Will at #4.
                                            regular_ids = [14557, 272440, 19024, 13966, 4130, 280065,
                                                           271903 if side == "a" else 272060]
                                            self.assertEqual(ordinary, regular_ids[:1 + count])
                                            self.assertEqual(displayed, ordinary[:3] + [11810] + ordinary[3:] + [17774])
                                        else:
                                            self.assertEqual(displayed, ordinary + extras)

    def test_browser_paints_the_situational_badge_in_both_locales(self):
        examples = (("DRUID", 2, "pve", "trinket", (11810, 17774)),
                    ("WARRIOR", 3, "pve", "off", (1168,)),
                    ("PALADIN", 3, "pve", "trinket", (19812, 13209)),
                    ("MAGE", 1, "pvp", "trinket", (13515,)))
        for locale, badge in (("enUS", "Situational"), ("frFR", "Situationnel")):
            game = Game(locale=locale, saved="EasyBISDB = { altCount=6, pvpRewards={pve=false, pvp=false} }")
            game.ns.SetPhase(game.ns, 0)
            game.ns.Browser.Open()
            browser = game.ns.Browser
            for cls, spec, mode, slot, wanted in examples:
                with self.subTest(locale=locale, cls=cls, spec=spec, mode=mode, slot=slot):
                    browser.state["class"], browser.state.spec, browser.state.list = cls, spec, mode
                    browser.ShowSlot(slot)
                    found = []
                    for index, row in browser.window.rowData.items():
                        if row.id in wanted:
                            frame = browser.window.rows[index]
                            self.assertEqual(strip_colors(frame.rank.GetText(frame.rank)), badge)
                            self.assertFalse(row.bis or row.tie)
                            self.assertIsNone(row.gap)
                            self.assertIsNone(row.ratio)
                            found.append(row.id)
                    self.assertCountEqual(found, wanted)

    def test_fourth_bear_trinket_in_the_open_window_with_two_or_six_alternatives(self):
        for faction in ("Alliance", "Horde"):
            game = Game(cls="DRUID", faction=faction, saved="EasyBISDB = { pvpRewards={pve=false} }")
            game.ns.SetPhase(game.ns, 0)
            game.ns.Browser.Open()
            browser = game.ns.Browser
            browser.state["class"], browser.state.spec, browser.state.list = "DRUID", 2, "pve"
            for count in (2, 6):
                with self.subTest(faction=faction, alternatives=count):
                    game.ns.SetAlternatives(game.ns, count)
                    browser.ShowSlot("trinket")
                    rows = [row for row in browser.window.rowData.values() if row.kind == "item"]
                    # The measured Threat option joins the two existing situational recommendations.
                    self.assertEqual(len(rows), 1 + count + 3)
                    self.assertEqual(rows[2].id, 272437)
                    self.assertEqual(rows[2].option.label, "Threat")
                    self.assertEqual(rows[3].id, 11810)
                    self.assertTrue(rows[3].level)
                    self.assertFalse(rows[3].bis or rows[3].tie)
                    self.assertEqual(rows[-1].id, 17774)
