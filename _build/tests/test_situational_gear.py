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
        slots = list(game.ns.SLOTS.values())
        for cls in CLASSES:
            data = ladders.Decode(cls)
            for spec in data.order.values():
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
                                        promoted = set()
                                        for pick in shelf.best.values():
                                            self.assertFalse(ladders.HasFlag(pick.entry, "j"))
                                            if pick.baseEntry:
                                                self.assertEqual(phase, 0)
                                                self.assertGreater(pick.score, 0)
                                                self.assertFalse(ladders.Unscored(pick.entry))
                                                self.assertFalse(ladders.HasFlag(pick.entry, "q"))
                                                promoted.add(pick.id)
                                            ordinary.append(pick.id)
                                        for pick in shelf.alts.values():
                                            if ladders.HasFlag(pick.entry, "j"):
                                                self.assertTrue(ladders.Unscored(pick.entry))
                                                self.assertFalse(ladders.IsTie(shelf, pick))
                                                extras.append(pick.id)
                                            else:
                                                ordinary.append(pick.id)
                                        expected = set(gear.item_ids(cls, spec, mode, slot)) - promoted
                                        self.assertLessEqual(len(ordinary), 1 + count)
                                        if slot == "trinket":
                                            self.assertEqual(len(ordinary), 1 + count)
                                        if phase == 0:
                                            audited = gear.target_options() | {22321}
                                            self.assertCountEqual((item for item in extras if item not in audited and item != 12583),
                                                                  expected)
                                            self.assertTrue((audited - promoted).isdisjoint(ordinary))
                                        else:
                                            self.assertEqual(extras, [])
                                        self.assertTrue(set(expected).isdisjoint(ordinary))
                                        self.assertEqual(len(set(displayed)), len(displayed))
                                        rows = list(ladders.DisplayPicks(shelf, True).values())
                                        ranked = [pick for pick in rows if not ladders.HasFlag(pick.entry, "f")]
                                        for index, pick in enumerate(ranked):
                                            if ladders.HasFlag(pick.entry, "j"):
                                                self.assertEqual(index, sum(p.position < pick.position for p in ranked))
                                        if (cls, spec, mode, slot, phase) == ("DRUID", 2, "pve", "trinket", 0):
                                            regular_ids = [14557, 272440, 19024, 13966, 4130, 280065,
                                                           271903 if side == "a" else 272060]
                                            self.assertEqual(ordinary, regular_ids[:1 + count])
                                            self.assertEqual(rows[3].id, 11810)

    def test_combat_rogue_hand_of_justice_is_bis_only_with_a_comparable_score(self):
        for faction in ("Alliance", "Horde"):
            game = Game(cls="ROGUE", faction=faction, saved="EasyBISCharDB={class='ROGUE', spec=2, list='pve'}")
            browser = game.ns.Browser
            browser.Open()
            for mode in ("pve", "pvp"):
                browser.state.list = mode
                for count in range(2, 7):
                    game.ns.SetAlternatives(game.ns, count)
                    browser.ShowSlot("trinket")
                    rows = [row for row in browser.window.rowData.values() if row.kind == "item"]
                    self.assertEqual(rows[0].id, 11815)
                    self.assertEqual(bool(rows[0].bis), mode == "pve")
                    self.assertEqual(bool(rows[0].level), mode == "pvp")
                    self.assertEqual(rows[0].gap, 0 if mode == "pve" else None)
                    self.assertEqual(sum(row.bis is True for row in rows), 2)
                    if mode == "pve":
                        self.assertEqual(rows[1].id, 22321)
                        self.assertTrue(rows[1].level)
                        self.assertTrue(next(row.bis for row in rows if row.id == 280065))
                    else:
                        seal = next(row for row in rows if row.id == 18465)
                        self.assertTrue(seal.level, "the PvP score includes attack power against humanoids")
                        self.assertFalse(seal.bis)

    def test_faction_hit_trinkets_can_earn_pre_raid_bis_with_their_base_stats(self):
        for faction, side, item in (("Alliance", "a", 270275), ("Horde", "h", 19120)):
            game = Game(cls="WARRIOR", faction=faction, locale="frFR")
            game.ns.SetPhase(game.ns, 0)
            game.ns.Browser.Open()
            browser = game.ns.Browser
            browser.state["class"], browser.state.spec, browser.state.list = "WARRIOR", 1, "pve"
            browser.ShowSlot("trinket")
            choices = [(index, row) for index, row in browser.window.rowData.items() if row.id == item]
            self.assertEqual(len(choices), 1)
            index, row = choices[0]
            frame = browser.window.rows[index]
            self.assertEqual(strip_colors(frame.rank.GetText(frame.rank)), "BIS")
            self.assertTrue(row.bis)
            self.assertEqual(row.gap, 0)
            self.assertIn("cap de toucher", row.why)

            ladders = game.ns.Ladders
            data = ladders.Decode("WARRIOR")
            for phase, mode in ((1, "pve"), (1, "pvp"), (0, "pvp")):
                flt = game.lua.table(side=side, phase=phase, alternatives=6, pvpRewards=False, unsourced=False)
                trinkets = ladders.Compute(data, 1, mode, flt)["trinket"]
                picks = [pick for group in (trinkets.best, trinkets.alts) for pick in group.values() if pick.id == item]
                self.assertEqual(len(picks), 1)
                self.assertFalse(ladders.HasFlag(picks[0].entry, "j"))

    def test_survival_hunter_medallion_is_bis_and_heart_stays_situational(self):
        for faction, side, medal in (("Alliance", "a", 270275), ("Horde", "h", 19120)):
            game = Game(cls="HUNTER", faction=faction)
            ladders = game.ns.Ladders
            data = ladders.Decode("HUNTER")
            for mode in ("pve", "pvp"):
                flt = game.lua.table(side=side, phase=0, alternatives=2, pvpRewards=mode == "pvp")
                picks = ladders.Compute(data, 4, mode, flt).trinket
                optional = {pick.id for pick in picks.alts.values() if ladders.HasFlag(pick.entry, "j")}
                self.assertIn(22321, optional)
                self.assertIn(medal, {pick.id for pick in picks.best.values()})
                self.assertIn(280065, {pick.id for pick in picks.alts.values()})
            self.assertEqual(game.ns.Sources.Describe(22321).detail, "Overlord Wyrmthalak")

    def test_ranged_hunters_do_not_recommend_hand_of_justice(self):
        for faction, side in (("Alliance", "a"), ("Horde", "h")):
            game = Game(cls="HUNTER", faction=faction)
            api = game.ns.Ladders
            data = api.Decode("HUNTER")
            for spec in (1, 2, 4):
                for phase in (0, 1, 9):
                    for mode in ("pve", "pvp"):
                        flt = game.lua.table(side=side, phase=phase, alternatives=6, pvpRewards=True)
                        trinkets = api.Compute(data, spec, mode, flt).trinket
                        self.assertNotIn(11815, {pick.id for rows in (trinkets.best, trinkets.alts)
                                                for pick in rows.values()})
                samples = game.ns.Rows.AoeList("HUNTER", spec).trinket
                self.assertNotIn(11815, {samples[index][1] for index in range(1, len(samples) + 1)})
            self.assertFalse(any(row["class"] == "HUNTER" and row.spec in (1, 2, 4)
                                 for row in game.ns.Index.ForItem(11815).values()))

    def test_combat_rogues_skip_king_mosh_but_keep_ranked_offhand_daggers(self):
        game = Game(cls="ROGUE")
        api = game.ns.Ladders
        data = api.Decode("ROGUE")
        for side in "ah":
            for mode in ("pve", "pvp"):
                flt = game.lua.table(side=side, phase=0, alternatives=6, pvpRewards=mode == "pvp")
                picks = api.Compute(data, 2, mode, flt)
                for slot in ("main", "off"):
                    self.assertNotIn(286613, {pick.id for rows in (picks[slot].best, picks[slot].alts)
                                             for pick in rows.values()})
                if mode == "pve":
                    self.assertIn(12590, {pick.id for pick in picks.off.alts.values()}, "Felstriker remains an alternative")

    def test_browser_paints_the_situational_badge_in_both_locales(self):
        examples = (("DRUID", 2, "pve", "trinket", (11810, 17774)),
                    ("WARRIOR", 3, "pve", "off", (1168,)),
                    ("WARRIOR", 1, "pve", "ranged", (11628,)),
                    ("HUNTER", 1, "pve", "off", (286613,)),
                    ("PALADIN", 3, "pve", "trinket", (19812, 13209)),
                    ("MAGE", 1, "pvp", "trinket", (13515,)),
                    ("ROGUE", 1, "pvp", "trinket", (18465,)))
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

    def test_barbarous_blade_reports_the_aoe_target_type(self):
        for faction in ("Alliance", "Horde"):
            game = Game(cls="HUNTER", faction=faction, locale="frFR")
            for spec in (1, 2, 4):
                state = game.lua.table(slot="main", spec=spec)
                state["class"] = "HUNTER"
                rows, _ = game.ns.Rows.Aoe(state)
                blade = next(row for row in rows.values() if row.id == 18520)
                self.assertTrue(blade.bis)
                self.assertIn("packs d’humanoïdes", blade.why)
                self.assertIn("33 PA supplémentaires", blade.why)

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
                    added = gear.target_options() | {22321}
                    self.assertTrue(all(row.level and not row.bis for row in rows if row.id in added))
                    # The measured Threat option joins the two existing situational recommendations.
                    self.assertEqual(sum(row.id not in added for row in rows), 1 + count + 3)
                    self.assertEqual(rows[2].id, 272437)
                    self.assertEqual(rows[2].option.label, "Threat")
                    self.assertEqual(rows[3].id, 11810)
                    self.assertTrue(rows[3].level)
                    self.assertFalse(rows[3].bis or rows[3].tie)
                    self.assertEqual([row.id for row in rows if row.id not in added][-1], 17774)
