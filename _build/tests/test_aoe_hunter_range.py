"""A hunter's hand slots must help while the player shoots from range."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))

import aoe_eligibility as eligibility
import aoe_weapons as weapons
import simulate_aoe as sim
import simulate_dungeon as dungeon
from test_addon import Game, lupa, strip_colors
from test_ui import find, open_dropdown, texts


class RangedHunterTest(unittest.TestCase):
    profiles = ("hunter-beast-mastery", "hunter-marksmanship", "hunter-survival")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_archived_melee_selection_opens_ranged_survival(self):
        for faction, mode, locale, label in (("Alliance", "pve", "enUS", "Survival"),
                                             ("Horde", "pvp", "frFR", "Survie")):
            with self.subTest(faction=faction, locale=locale):
                saved = f"EasyBISCharDB = {{ class = 'HUNTER', spec = 3, list = '{mode}' }}"
                game = Game(locale=locale, faction=faction, cls="HUNTER", saved=saved)
                ns = game.ns
                self.assertEqual(ns.ActiveSpec("HUNTER", 3), 4)
                self.assertEqual(list(ns.Index.SpecOrder("HUNTER").values()), [1, 2, 4])
                self.assertIsNone(ns.Index.SpecName("HUNTER", 3))
                ns.Browser.Open()
                open_dropdown(game, ns.Browser.window.spec.button)
                menu = find(game.stub.menu, ns.ClassName("HUNTER"))
                self.assertEqual(texts(menu), [ns.SpecName("Beast Mastery"), ns.SpecName("Marksmanship"), label])
                find(menu, label).pick()
                self.assertEqual(ns.Browser.Target(), ("HUNTER", 4, mode))
                self.assertEqual(game.slash("list 3"), game.slash("list 4"))
                hits = ns.Index.ForItem(13285) or {}
                self.assertNotIn("HUNTER", [hit["class"] for hit in hits.values() if hit.list != "weave"])
                picks = ns.Ladders.For("HUNTER", 4, mode)
                self.assertTrue(picks.main.best[1].id)
                for slot in (picks.main, picks.off):
                    for group in (slot.best, slot.alts, slot.other):
                        self.assertNotIn(13285, [p.id for p in group.values()])
                self.assertIsNone(ns.Ladders.Measured("HUNTER", 4, "pve"))
                self.assertIsNone(ns.Rows.AoeList("HUNTER", 3))
                self.assertTrue(len(ns.Rows.AoeList("HUNTER", 4).main))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_melee_weaving_pve_tab_uses_its_own_gear_and_tracks_it(self):
        for faction in ("Alliance", "Horde"):
            with self.subTest(faction=faction):
                game = Game(locale="frFR", faction=faction, cls="HUNTER")
                ns, stub = game.ns, game.stub
                self.assertFalse(ns.Ladders.HasList("HUNTER", 1, "weave"))
                ns.Browser.Open()
                window = ns.Browser.window

                def choose_spec(name):
                    open_dropdown(game, window.spec.button)
                    find(find(stub.menu, ns.ClassName("HUNTER")), name).pick()

                choose_spec("Survie")
                tabs = {b.value: b for b in window.scenario.buttons.values() if b.shown}
                self.assertEqual(list(tabs), ["pve", "weave", "aoe"])
                self.assertEqual(ns.Browser.state.itemList, "pve")
                stub.run(tabs["weave"], "OnClick")
                self.assertEqual(ns.Browser.AddTarget(), ("HUNTER", 4, "weave"))
                self.assertTrue(ns.char.weave)

                self.assertFalse(any(row.kind == "note" or row.why or row.scored for row in window.rowData.values()))
                rows = [row for row in window.rowData.values() if row.kind == "item" and row.bis]
                self.assertEqual(len(rows), 16)
                self.assertEqual([row.id for row in rows if row.slot in ("main", "ranged")], [12784, 280020])
                self.assertEqual([row.id for row in rows if row.slot == "trinket"], [13965, 22321])
                for row in rows:
                    hits = ns.Index.ForItem(row.id)
                    self.assertTrue(any(hit["class"] == "HUNTER" and hit.spec == 4 and hit.list == "weave"
                                        and hit.slot == row.slot and hit.bis for hit in hits.values()), row.id)
                ns.Browser.ShowSlot("main", "weave")
                frame = next(frame for frame in window.rows.values() if frame.data and frame.data.id == 12784)
                self.assertEqual(strip_colors(frame.rank.text), ns.L.RANK_BIS)
                tooltip_rank = f"{ns.L.RANK_BIS} {ns.L.LIST_WEAVE}"
                self.assertTrue(any(tooltip_rank in right for _, right in game.lines(12784)))
                ns.SetListShown(ns, "weave", False)
                self.assertFalse(any("Melee Weaving" in right for _, right in game.lines(12784)))

                state = ns.Browser.state
                ns.Dungeons.ToggleList(state, "pve")
                ns.Dungeons.ToggleList(state, "weave")
                model = ns.Dungeons.For(state)
                self.assertEqual(model.tracked, 1)
                self.assertTrue(any(piece.id == 280020 for piece in model.rows.values()))

                stub.run(window.list.buttons[2], "OnClick")
                self.assertEqual(ns.Browser.state.itemList, "pvp")
                self.assertFalse(window.scenario.shown)
                stub.run(window.list.buttons[1], "OnClick")
                self.assertEqual(ns.Browser.state.itemList, "weave")
                stub.run(tabs["pve"], "OnClick")
                self.assertEqual(ns.Browser.state.itemList, "pve")

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_melee_weaving_keeps_only_eligible_complete_weapon_pairs(self):
        game = Game(cls="HUNTER")
        ns = game.ns
        picks = ns.Ladders.For("HUNTER", 4, "weave")
        self.assertEqual(picks.main.alts[1].id, 13285)
        self.assertEqual([pick.id for pick in picks.ranged.alts.values()], [18738])

        ns.SetPvPRewards(ns, "pve", True)
        picks = ns.Ladders.For("HUNTER", 4, "weave")
        self.assertEqual([pick.id for pick in picks.main.alts.values()], [13285])
        self.assertEqual([pick.id for pick in picks.ranged.alts.values()], [19107, 18738])

        data = ns.Ladders.Decode("HUNTER")
        entries = data.lists[4].weave.ranged
        rejected = next(entry for entry in entries.values() if entry.id == 280020)
        rejected.phase = 1
        filters = ns.Filter()
        filters.phase = 0
        picks = ns.Ladders.Compute(data, 4, "weave", filters)
        self.assertEqual((picks.main.best[1].id, picks.ranged.best[1].id), (13285, 19107))
        self.assertEqual(len(picks.main.alts), 0)

    def test_melee_stats_and_hit_procs_do_not_qualify_a_hunter_weapon(self):
        for spec in (1, 2, 3):
            profile = {"class": "HUNTER", "spec": spec, "itemDamageChecks": {"1728": {"29155": 1}}}
            for stats in ({}, {"strength": 20}, {"expertise": 12}, {"ap": 30}, {"spell": 20, "hit": 10}):
                with self.subTest(spec=spec, stats=stats), self.assertRaises(ValueError):
                    eligibility.validate_hunter_hand(profile, 1728, stats)
            for stats in ({"agility": 10}, {"rap": 25}, {"ap": 20, "rap": 20}, {"strength": 4, "crit": 14}):
                eligibility.validate_hunter_hand(profile, 1, stats)

    def test_dalrends_defensive_offhand_requires_the_complete_ranged_ap_bonus(self):
        for filename in self.profiles:
            profile = sim.read(sim.PROFILES / (filename + ".json"))
            pairs = [pair for pair in profile["weaponSets"] if 12939 in pair]
            self.assertEqual(pairs, [[12940, 12939]])
            eligibility.validate_hunter_hand(profile, 12939, {})
            for invalid in ([], [[12783, 12939]], [[12940, 12939], [12783, 12939]]):
                with self.subTest(profile=filename, pairs=invalid), self.assertRaises(ValueError):
                    eligibility.validate_hunter_hand(dict(profile, weaponSets=invalid), 12939, {})
            with self.assertRaisesRegex(ValueError, "12940"):
                weapons.validate_pair_client(None, profile, 12783, 12939)

    @unittest.skipUnless(os.getenv("EASYBIS_WOWSIMS") and os.getenv("EASYBIS_PACK_CLI"),
                         "native pack simulator required")
    def test_dalrends_two_pieces_match_fifty_ranged_attack_power(self):
        cli = Path(os.environ["EASYBIS_PACK_CLI"])
        p = sim.read(sim.PROFILES / "hunter-survival.json")
        gear = sim.reference_equipment(Path(os.environ["EASYBIS_WOWSIMS"]), cli, p)
        rotation = sim.read(sim.PROFILES / p["dungeonRotation"])
        damage = {}
        with tempfile.TemporaryDirectory() as work:
            for control, off, rap in (("empty", 0, 0), ("set", 12939, 0), ("ranged_ap", 0, 50)):
                req = weapons.request(p, p["races"]["a"], rotation, gear, (12940, off), 128)
                if rap:
                    index = eligibility.STAT_IDS["rap"][0]
                    req["raid"]["parties"][0]["players"][0]["bonusStats"] = {"stats": [0] * index + [rap]}
                result = sim.run_request(cli, Path(work), req)
                damage[control] = sim.samples(result, 128, p["damageChecks"])[0]
        self.assertEqual(damage["set"], damage["ranged_ap"])
        gain, error = sim.difference(damage["set"], damage["empty"])
        self.assertGreater(gain, 3 * error)

    @unittest.skipUnless(all(os.getenv(key) for key in ("EASYBIS_WOWSIMS", "EASYBIS_PACK_CLI", "EASYBIS_ROUTE_CLI")),
                         "native pack and dungeon simulators required")
    def test_player_deals_damage_from_range_on_the_pack_and_each_dungeon_wave(self):
        root = Path(os.environ["EASYBIS_WOWSIMS"])
        pack_cli = Path(os.environ["EASYBIS_PACK_CLI"])
        route_cli = Path(os.environ["EASYBIS_ROUTE_CLI"])
        for slug in self.profiles:
            p = sim.read(sim.PROFILES / (slug + ".json"))
            rotation = sim.read(sim.PROFILES / p["dungeonRotation"])
            gear = sim.reference_equipment(root, pack_cli, p)
            for race in p["races"].values():
                for route in (False, True):
                    with self.subTest(profile=slug, race=race, route=route), tempfile.TemporaryDirectory() as work:
                        req = sim.make_request(p, race, rotation, gear, None, 0, 64)
                        if route:
                            req = dungeon.bind_request(req, p, root, [], 0, dungeon.SEED)
                        result = sim.run_request(route_cli if route else pack_cli, Path(work), req)
                        player = result["raidMetrics"]["parties"][0]["players"][0]
                        self.assertGreaterEqual(req["raid"]["parties"][0]["players"][0]["distanceFromTarget"], 8)
                        for action in player["actions"]:
                            if action["id"].get("otherId") == "OtherActionAttack" or action["id"].get("spellId") in (
                                    14266, 14271, 20910, 1310536):
                                self.assertFalse(any(t.get("damage", 0) or t.get("casts", 0) for t in action["targets"]))
                        shot = next(a for a in player["actions"] if a["id"].get("otherId") == "OtherActionShoot")
                        hit = {t["unitIndex"] for t in shot["targets"] if t.get("damage", 0) > 0}
                        targets = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
                        for wave in ((targets[:4], targets[4:5], targets[5:]) if route else (targets,)):
                            self.assertTrue(hit.intersection(wave))
                        if route:
                            dungeon.route.route_samples(result, 64)
                        else:
                            sim.samples(result, 64, p["damageChecks"], p.get("requiredPet"))
