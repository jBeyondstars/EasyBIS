"""Tests for the data generator.

    python -P tests/test_generator.py

The Lua test needs the `lupa` package and is skipped without it.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

TESTS = Path(__file__).resolve().parent
BUILD = TESTS.parent
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(TESTS))

import audit  # noqa: E402
import build  # noqa: E402
import capture  # noqa: E402
import compare_site  # noqa: E402
import consumable_lists  # noqa: E402
import consumables  # noqa: E402
import corrections  # noqa: E402
import drops  # noqa: E402
import fdb  # noqa: E402
import ladders  # noqa: E402
import luaout  # noqa: E402
import notes  # noqa: E402
import phases  # noqa: E402
import pvp_insignia  # noqa: E402
import ranks  # noqa: E402
import questie  # noqa: E402
import reputations  # noqa: E402
import runs  # noqa: E402
import shockadin  # noqa: E402
import simulated  # noqa: E402
import specs  # noqa: E402

try:
    import lupa
except ImportError:  # pragma: no cover
    lupa = None

CACHE = BUILD / "cache" / "ForeverDB"
GOLDEN = TESTS / "golden" / "site_2026-11-14.json"

# What the addon will do with a data file: run it with (addon name, namespace).
LUA_READER = r"""
local ns = {}
local function run(source, name)
    local chunk = assert(load(source, name))
    chunk("EasyBIS", ns)
end
local function lists()
    local out = {}
    for cls, text in pairs(ns.data.lists) do
        for line in text:gmatch("[^\n]+") do
            local kind, spec, list, slot, entries = line:match("^(%a)\t(%d+)\t([^\t]*)\t([^\t]*)\t?(.*)$")
            if kind == "L" then
                for entry in entries:gmatch("%S+") do
                    local id, score, flags, twin, limit, rank = entry:match("^(%d+):(%d+):?([%a%d]*):?(%d*):?([%a%d]*):?(%d*)$")
                    out[#out + 1] = table.concat({ cls, spec, list, slot, id, score, flags, twin, limit, rank }, ",")
                end
            end
        end
    end
    return table.concat(out, "\n")
end
local function items()
    local out = {}
    for line in ns.data.items:gmatch("[^\n]+") do
        local id, name, groups, flags, sources = line:match("^(%d+)|([^|]*)|([^|]*)|([^|]*)|(.*)$")
        out[#out + 1] = id .. "|" .. name
    end
    return table.concat(out, "\n")
end
local function enchants()
    local count, missing = 0, 0
    local known = {}
    for line in ns.data.enchantInfo:gmatch("[^\n]+") do known[line:match("^([^|]+)|")] = true end
    for _, text in pairs(ns.data.enchants) do
        for line in text:gmatch("[^\n]+") do
            local ids = line:match("^E\t%d+\t%w+\t(.*)$")
            for token in ids:gmatch("%S+") do
                local id = token:match("^([si]%d+):?%d*$")   -- "s20025", or "s20025:1" with the phase it needs
                count = count + 1
                if not id or not known[id] then missing = missing + 1 end
            end
        end
    end
    return count, missing
end
return run, lists, items, enchants, ns
"""


class GeneratorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(CACHE)                        # what the build ranks: with the corrections in use
        cls.published = fdb.load(CACHE, corrected=False)  # ForeverDB's data as the site has it
        cls.full = {
            (token, spec, mode, slot): ladders.full_ladder(cls.db, token, spec, mode, slot)
            for token, data in cls.db.classes.items() for spec in data["specs"]
            for mode in ladders.MODES for slot, _ in ladders.SLOTS}
        cls.kept = ladders.build_all(cls.db)

    def test_reads_every_class_and_spec(self):
        self.assertEqual(len(self.db.classes), 9)
        self.assertEqual(sum(len(data["specs"]) for data in self.published.classes.values()), 27)
        self.assertEqual(sum(len(data["specs"]) for data in self.db.classes.values()), 29,
                         "ForeverDB's, the cat and the Shockadin")
        for token, data in self.db.classes.items():
            for spec in data["specs"].values():
                self.assertEqual(set(spec["weights"]), {"lvl", "raid", "pvp"}, f"{token} {spec['name']}")
        self.assertEqual(self.db.meta["cap"], 60)

    # -- a spec ForeverDB's data does not have: the Paladin's Shockadin (specs.py, shockadin.py) --------------

    SHOCKADIN = ("PALADIN", 4)
    STALWART_HELM = 250599        # Strength, 2% hit and 38 spell power: the Shockadin's best head before the raids
    SPELLBLASTING = "s1219580"    # Enchant 2H Weapon - Spellblasting, +65 spell power
    HOLY_POWER_GLOVES = "Enchant Gloves - Holy Power"

    def test_the_shockadin_is_the_paladins_fourth_spec(self):
        self.assertEqual(self.db.specs.shockadin, self.SHOCKADIN)
        ours, theirs = self.db.classes["PALADIN"]["specs"], self.published.classes["PALADIN"]["specs"]
        self.assertEqual(sorted(theirs), [1, 2, 3], "ForeverDB's own")
        self.assertEqual(sorted(ours), [1, 2, 3, 4])
        for number, spec in theirs.items():
            self.assertEqual((ours[number]["name"], ours[number]["role"], ours[number]["style"]),
                             (spec["name"], spec["role"], spec["style"]), f"ForeverDB's spec {number} is left as it is")
            self.assertNotIn("added", ours[number])
        for number in (1, 3):
            expected = copy.deepcopy(theirs[number])
            pvp = expected["weights"]["pvp"]
            if specs.ATTACK_POWER in pvp:
                pvp[specs.HUMANOID_ATTACK_POWER] = pvp[specs.ATTACK_POWER]
            self.assertEqual(ours[number], expected)
        added = ours[4]
        self.assertEqual((added["name"], added["role"], added["style"], added["slug"]),
                         ("Shockadin", "Melee DPS", "2h", "shockadin"))
        self.assertTrue(added["added"])
        pvp = {**shockadin.PVP, specs.HUMANOID_ATTACK_POWER: shockadin.PVP[specs.ATTACK_POWER]}
        self.assertEqual(added["weights"], {"lvl": shockadin.PVE, "raid": shockadin.PVE, "pvp": pvp})
        self.assertEqual([number for number, spec in ours.items() if spec.get("added")], [4])

    def test_the_shockadins_weights_are_the_simulators(self):
        """PvE: WoWSims Forever's Holy Shock weights, a point of spell damage counting 1. PvP: the same, with
        ForeverDB's stamina and armor for a Paladin and without the Holy spells' share of hit."""
        pve, pvp, ep = shockadin.PVE, shockadin.PVP, shockadin.EP
        self.assertEqual((pve[42], pve[45]), (1, 1))
        for stat, value in ep.items():
            self.assertAlmostEqual(pve[stat], value / ep[45], places=3, msg=f"stat {stat}")
        self.assertEqual(set(pve) - set(ep), {7}, "stamina is ForeverDB's, the rest is the simulator's")
        paladin = self.published.classes["PALADIN"]["specs"]
        for number in (1, 3):   # Holy and Retribution
            self.assertEqual(paladin[number]["weights"]["raid"][7], pve[7], "ForeverDB's PvE stamina for a Paladin")
        self.assertGreater(pve[31], pve[45], "a point of hit rating is worth more than one of spell damage")
        self.assertGreater(pve[45], pve[84])
        self.assertLess(pve[43], 0.01, "mana per 5 seconds is worth nothing to it in a raid")
        self.assertEqual({stat for stat in set(pve) | set(pvp) if pve.get(stat) != pvp.get(stat)}, {7, 31, "armor"})
        for number in (1, 3):
            self.assertEqual(paladin[number]["weights"]["pvp"][7], pvp[7])
            self.assertEqual(paladin[number]["weights"]["pvp"]["armor"], shockadin.FOREVERDB_PVP_ARMOR)
        # ... but for armor, which counts more: plate matters to this build in PvP, said the addon's author, and at
        # ForeverDB's 0.02 a cloth belt led the waists over a plate one with 331 more armor and 14 more Stamina.
        self.assertEqual(pvp["armor"], 0.05)
        flt = ("a", False, False, phases.CURRENT, True, None)
        waists = [e.item_id for e in self.full[*self.SHOCKADIN, "pvp", "waist"] if e.passes(flt) and not e.rank]
        redeemer, soulforge, vindicator, archmage = 272405, 226986, 272404, 18405
        self.assertEqual(waists[:4], [redeemer, soulforge, vindicator, archmage])
        self.assertAlmostEqual(pvp[31], (ep[31] - shockadin.EP_HOLY_SPELL_HIT) / ep[45], places=3)

    def test_the_shockadin_changes_no_other_list(self):
        with mock.patch.object(shockadin, "add", return_value=None):
            without = fdb.load(CACHE)
        count = lambda db: sum(len(data["specs"]) for data in db.classes.values())
        self.assertEqual(count(without), count(self.db) - 1)
        self.assertEqual(sorted(without.classes["PALADIN"]["specs"]), [1, 2, 3])
        self.assertEqual(without.enchants["PALADIN"].keys() | {(4, "lvl"), (4, "raid")}, self.db.enchants["PALADIN"].keys())
        for key in without.enchants["PALADIN"]:
            self.assertEqual(without.enchants["PALADIN"][key], self.db.enchants["PALADIN"][key], key)
        for spec in (1, 2, 3):
            for mode in ladders.MODES:
                for slot, _ in ladders.SLOTS:
                    self.assertEqual(ladders.full_ladder(without, "PALADIN", spec, mode, slot),
                                     self.full["PALADIN", spec, mode, slot], f"PALADIN {spec} {mode} {slot}")

    def test_the_shockadin_holds_a_two_hander(self):
        for mode in ladders.MODES:
            main, off = self.full[*self.SHOCKADIN, mode, "main"], self.full[*self.SHOCKADIN, mode, "off"]
            self.assertTrue(main)
            self.assertTrue(all(entry.two_hand for entry in main), f"{mode}: a one-hander in the main hand")
            self.assertEqual(off, [], f"{mode}: an off hand")
            self.assertEqual(self.full[*self.SHOCKADIN, mode, "ranged"], [], "ForeverDB's data has no libram")

    def test_the_shockadin_borrows_the_caster_pieces_a_paladin_can_wear(self):
        """ForeverDB pools for a Paladin what a healer, a tank or a melee fighter wears. WoWSims' own set for the Holy
        Shock build wears Magister's Leggings and Gauntlets of Elements, which are in other classes' pools only: the
        Shockadin lists them too. Not another class's own piece, nor one whose classes the data cannot tell (the
        second dungeon sets, which the simulator's database lacks), and never a weapon."""
        cls, spec = self.SHOCKADIN
        leggings, gauntlets, deathmist, bonescythe = 16687, 16672, 22074, 22477
        pools = self.db.classes[cls]["pools"]
        self.assertNotIn(leggings, {item for item, _ in pools["legs"]})
        self.assertIn(leggings, {entry.item_id for entry in self.full[cls, spec, "pve", "legs"]})
        self.assertIn(gauntlets, {entry.item_id for entry in self.full[cls, spec, "pve", "hands"]})
        self.assertIn(deathmist, self.db.class_unknown)
        for slot, _ in ladders.SLOTS:
            ids = {entry.item_id for entry in self.full[cls, spec, "pve", slot]}
            self.assertFalse(ids & self.db.class_unknown - {item for pool in pools.values() for item, _ in pool}, slot)
            self.assertNotIn(bonescythe, ids)
        borrowed = self.db.classes[cls]["specs"][spec]["pools"]
        self.assertEqual({pool for pool in borrowed if pool in ("mh", "2h", "oh", "ranged")}, set())
        for other in (1, 2, 3):   # the Paladin's other lists are ForeverDB's pools, as before
            self.assertNotIn("pools", self.db.classes[cls]["specs"][other])
            self.assertNotIn(leggings, {entry.item_id for entry in self.full[cls, other, "pve", "legs"]})

    def test_hand_of_justice_is_not_a_shockadins(self):
        """Measured on WoWSims' Holy Shock build it adds 5 DPS where the best trinkets add 9: it is listed on its 12
        attack power or not at all, not level with the best as for the other melee damage dealers."""
        cls, spec = self.SHOCKADIN
        self.assertIn("shockadin", self.db.effects_but[11815])
        for mode in ladders.MODES:
            self.assertFalse([entry for entry in self.full[cls, spec, mode, "trinket"] if entry.level], mode)

    def test_the_shockadins_pve_list_is_ranked_by_simulation(self):
        """WoWSims has the build (Holy Shock, of its Retribution Paladin), so the PvE list is measured like the other
        damage dealers'. It puts the fast two-handers first, which the weights could not see: Seal of Righteousness
        adds a share of the spell power to every swing, whatever the weapon's speed."""
        cls, spec = self.SHOCKADIN
        self.assertIn((cls, spec), self.db.simulated.specs)
        main = [entry for entry in self.full[cls, spec, "pve", "main"] if entry.passes(("a", False, False, 0, False, None))]
        self.assertEqual(main[0].item_id, 2801, "Blade of Hanna, 2.0 a swing")
        zealous = next(place for place, entry in enumerate(main) if entry.item_id == 276397)   # the weights' first
        self.assertGreater(zealous, 10, "Hand of the Zealous, 3.7 a swing and 68 spell power")
        self.assertIsNone(simulated.ranking(self.db, cls, spec, "pvp", "main"))

    def test_the_shockadins_pvp_list_is_ranked_on_its_weights(self):
        cls, spec = self.SHOCKADIN
        pvp = {**shockadin.PVP, specs.HUMANOID_ATTACK_POWER: shockadin.PVP[specs.ATTACK_POWER]}
        for mode, weights in (("pvp", pvp),):
            for slot, _ in ladders.SLOTS:
                for entry in self.full[cls, spec, mode, slot]:
                    if entry.pvp_utility:
                        self.assertEqual((slot, entry.item_id), ("trinket", pvp_insignia.ALLIANCE))
                        continue
                    if entry.level:
                        continue   # Hand of Justice: no score of its own, level with the best (specs.unvalued)
                    self.assertAlmostEqual(entry.score, ladders.score(self.db, entry.item_id, weights, cls),
                                           msg=f"{mode} {slot} {entry.item_id}")
                    self.assertFalse(entry.estimated or entry.placed, "no simulation ranks it")
                    stats = self.db.gear[entry.item_id]["stats"]
                    self.assertFalse(ladders.HEALING in stats and not any(s in stats for s in ladders.SPELL_DAMAGE),
                                     f"{entry.item_id} only heals")
        flt = (*("a", False, False, phases.CURRENT), True, None)
        head = [entry for entry in self.full[cls, spec, "pvp", "head"] if entry.passes(flt) and not entry.pvp]
        self.assertEqual(head[0].item_id, self.STALWART_HELM)
        # a PvP reward is ranked on its stats in both lists, as everywhere
        self.assertTrue(any(entry.pvp for entry in self.full[cls, spec, "pve", "main"]))

    def test_the_shockadins_enchants_are_a_paladins(self):
        cls, spec = self.SHOCKADIN
        ladder = self.enchant_ladder(cls, spec)
        self.assertEqual(ladder["w2h"][0][0], self.SPELLBLASTING)
        self.assertEqual(self.db.enchant_info[ladder["hands"][0][0]][0], self.HOLY_POWER_GLOVES)
        self.assertFalse({"w1h", "shield", "held", "rng"} & set(ladder), "it holds a two-hander and nothing else")
        own = {enchant for (number, _), per_slot in self.db.enchants[cls].items() if number != spec
               for entries in per_slot.values() for enchant, _ in entries}
        listed = {enchant for entries in self.db.enchants[cls][spec, "raid"].values() for enchant, _ in entries}
        self.assertTrue(listed)
        self.assertLessEqual(listed, own, "an enchant ForeverDB lists for no Paladin")
        for key, entries in self.db.enchants[cls][spec, "raid"].items():
            worth = [sum(shockadin.PVE.get(stat, 0) * amount
                         for stat, amount in specs.enchant_stats(self.db.enchant_info[enchant][1]).items())
                     for enchant, _ in entries]
            self.assertEqual(worth, sorted(worth, reverse=True), key)
            self.assertGreater(worth[-1], 0, key)

    def test_an_enchants_sentence_is_read_as_stats(self):
        read = specs.enchant_stats
        self.assertEqual(read("Agility +15"), {3: 15})
        self.assertEqual(read("+65 Spell Power"), {45: 65})
        self.assertEqual(read("Attack Power +28/Dodge +1%"), {38: 28, 13: 12})
        self.assertEqual(read("Attack Power +26 and +1% Critical Strike"), {38: 26, 32: 14})
        self.assertEqual(read("All Stats +4"), {3: 4, 4: 4, 5: 4, 6: 4, 7: 4})
        self.assertEqual(read("Holy Damage +20"), {84: 20})
        self.assertEqual(read("Healing Spells +100, Damage Spells +34"), {41: 100, 42: 34})
        self.assertEqual(read("+18 Spell Damage and Healing"), {45: 18})
        self.assertEqual(read("Healing and Spell Damage +8"), {45: 8})
        self.assertEqual(read("Healing +31 and 5 mana per 5 sec."), {41: 31, 43: 5})
        for unknown in ("Crusader", "Weapon Damage +9", "Counterweight +3% Attack Speed", "Living Stats"):
            self.assertIsNone(read(unknown), unknown)

    def test_the_data_files_hold_the_shockadin(self):
        text = luaout.lists_file(self.db, self.kept)
        block = text.split("PALADIN = [==[\n", 1)[1].split("]==]", 1)[0]
        specs_written = [line.split("\t") for line in block.split("\n") if line.startswith("S\t")]
        self.assertEqual(specs_written, [["S", "1", "Holy", "Healer", "any"], ["S", "2", "Protection", "Tank", "shield"],
                                         ["S", "3", "Retribution", "Melee DPS", "2h"],
                                         ["S", "4", "Shockadin", "Melee DPS", "2h"]])
        slots = {(fields[2], fields[3]) for fields in (line.split("\t") for line in block.split("\n"))
                 if fields[0] == "L" and fields[1] == "4"}
        core = [slot for slot, _ in ladders.SLOTS if slot not in ("off", "ranged")]
        self.assertEqual(slots, {(mode, slot) for mode in ladders.MODES for slot in core})
        self.assertIn("M\t4\t", block, "its PvE list is ranked by simulation")
        self.assertIn("-- Added to ForeverDB's specs: Shockadin Paladin, spec 4", text)
        self.assertIn(shockadin.SOURCE, text)
        enchants = luaout.enchants_file(self.db, self.kept).split("PALADIN = [==[\n", 1)[1].split("]==]", 1)[0]
        self.assertIn(f"E\t4\tw2h\t{self.SPELLBLASTING}", enchants)
        lists = consumable_lists.build(self.db)["PALADIN"]
        self.assertEqual(sorted(lists), [1, 2, 3, 4])
        for mode in consumable_lists.MODES:
            self.assertTrue(lists[4][mode]["flask"].ranked, f"{mode}: no flask")

    def test_every_pool_item_is_described(self):
        for token, data in self.db.classes.items():
            for pool in data["pools"].values():
                for item_id, _ in pool:
                    self.assertIn(item_id, self.db.gear, f"{token}: no stats for {item_id}")
                    self.assertIn(item_id, self.db.items, f"{token}: no source line for {item_id}")

    def test_matches_the_site(self):
        """Every slot of every page read from foreverdb.net/bis has the same picks."""
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        published = self.published
        if published.meta["version"] != golden["data_version"]:
            # ForeverDB added items between snapshots of the same client build.
            if not shutil.which("git"):
                self.skipTest("Git is needed to read this earlier ForeverDB snapshot")
            with tempfile.TemporaryDirectory() as temp:
                for name in fdb.DATA_FILES:
                    ref = f"{golden['data_revision']}:_build/cache/ForeverDB/{name}"
                    result = subprocess.run(["git", "show", ref], cwd=BUILD.parent, capture_output=True)
                    if result.returncode:
                        self.skipTest(f"Historical ForeverDB data unavailable: {ref}")
                    (Path(temp) / name).write_bytes(result.stdout)
                published = fdb.load(temp, corrected=False)
        self.assertEqual(published.meta["version"], golden["data_version"])
        self.assertEqual(published.meta["build"], golden["build"])
        for page in golden["pages"]:
            with self.subTest(cls=page["cls"], spec=page["spec"], mode=page["mode"]):
                self.assertEqual(compare_site.compare(published, page), [])

    def test_pvp_rewards_are_marked(self):
        """Every entry says whether it is a PvP reward, so the addon can leave those out of a list: a PvP
        rank's, the honor quartermasters', a battleground's, a Premier set's."""
        is_reward = lambda item_id: ladders.pvp_reward(self.db.items[item_id])   # noqa: E731
        self.assertTrue(is_reward(16478), "Field Marshal's Plate Helm, of rank 13")
        self.assertTrue(is_reward(20057), "Highlander's Plate Spaulders, of Arathi Basin")
        for item_id in (17904, 17909, 19106, 19107, 19108, 20648):
            self.assertTrue(is_reward(item_id), self.db.items[item_id]["name"])
        self.assertTrue(is_reward(272787), "Premier Field Marshal's Plate Helm, which the data has no source for")
        for item_id, name in ((12620, "Enchanted Thorium Helm"), (271959, "Theramore Spaulders"),
                              (19491, "Amulet of the Darkmoon"), (226869, "Faceguard of Heroism")):
            self.assertEqual(self.db.items[item_id]["name"], name)
            self.assertFalse(is_reward(item_id), name)
        # the vendors are the ones the data names so, and no quartermaster is missing: whoever sells a
        # PvP-rank reward or a Premier piece is one
        for npc, name in ladders.PVP_VENDORS.items():
            if npc in self.db.vendors:
                self.assertEqual(self.db.vendors[npc][0], name)
        for item_id, item in self.db.items.items():
            if "p" in item["groups"] or item["name"].startswith(ladders.PVP_SET):
                self.assertTrue(ladders.pvp_reward(item))
                for source in item["sources"]:
                    if source[0] == "V":
                        self.assertIn(int(source[1]), ladders.PVP_VENDORS, f"{item['name']}: who sells it")
        marked = {"pve": 0, "pvp": 0}
        for (token, spec, mode, slot), ladder in self.full.items():
            for entry in ladder:
                self.assertEqual(entry.pvp, is_reward(entry.item_id))
                marked[mode] += entry.pvp
                # they count until a filter says otherwise, and then the list leaves them out
                self.assertEqual(entry.passes(("a", True, False, phases.LATER)),
                                 entry.passes(("a", True, False, phases.LATER, True)))
                self.assertEqual(entry.passes(("a", True, False, phases.LATER, False)),
                                 entry.passes(("a", True, False, phases.LATER)) and not entry.pvp)
        self.assertTrue(marked["pve"] and marked["pvp"])
        self.assertEqual(ladders.PVP_REWARDS, {"pve": False, "pvp": True})
        # without them every spec still has something for every slot it fills with them
        without = ("a", False, False, phases.CURRENT, False)
        for (token, spec, mode, slot), ladder in self.full.items():
            if slot not in ("main", "off", "ranged") and any(e.passes(without[:4]) for e in ladder):
                self.assertTrue(any(e.passes(without) for e in ladder), f"{token} {spec} {mode} {slot} is empty")
        self.assertIn("p a PvP reward", luaout.lists_file(self.db, self.kept))

    def test_pvp_rank_rewards_are_ranked_in_both_lists(self):
        """A PvP-rank reward is an item like any other, in the PvE list too: it is ranked on its stats.
        Only the site's rule (rank_rewards=False) leaves it out of PvE."""
        rewards = {"pve": set(), "pvp": set()}
        for (token, spec, mode, slot), ladder in self.full.items():
            for entry in ladder:
                item = self.db.items[entry.item_id]
                groups = item["groups"]
                missing_source = not (groups - {"u"}) or reputations.unconfirmed_watcher_ring(item)
                self.assertEqual(entry.unsourced, missing_source, f"{token} {spec} {mode} {slot}: {entry.item_id}")
                if groups == {"p"}:
                    rewards[mode].add(entry.item_id)
        self.assertTrue(rewards["pve"], "no PvP-rank reward is in a PvE list")
        self.assertTrue(rewards["pvp"], "no PvP-rank reward is in a PvP list")
        for (token, spec, mode, slot) in self.full:
            if mode != "pve":
                continue
            for entry in ladders.full_ladder(self.db, token, spec, mode, slot, rank_rewards=False):
                groups = self.db.items[entry.item_id]["groups"]
                self.assertTrue(groups - {"p"}, f"{token} {spec} {slot}: {entry.item_id} is a PvP-rank reward")
                self.assertEqual(entry.unsourced, not (groups - {"u", "p"}))

    def test_ladders_are_sorted_and_free_of_duplicates(self):
        for key, ladder in self.full.items():
            scores = [entry.score for entry in ladder]
            self.assertEqual(scores, sorted(scores, reverse=True), key)
            ids = [entry.item_id for entry in ladder]
            self.assertEqual(len(ids), len(set(ids)), key)
            twins = {entry.twin for entry in ladder if entry.twin}
            self.assertFalse(twins & set(ids), f"{key}: both ids of a twin pair are listed")

    def test_kept_ladder_shows_what_the_full_one_would(self):
        """Under every filter the addon can apply, the shortened ladder gives the same picks."""
        def shown(ladder_of, token, spec, mode, flt):
            visible = ladders.visible_slots({slot: ladder_of(token, spec, mode, slot) for slot, _ in ladders.SLOTS}, flt)
            others = [entries[:1 + ladders.ALTERNATIVES]
                      for entries in ladders.other_weapons(visible["main"], visible["off"])]
            visible["main"], visible["off"] = ladders.weapon_lists(visible["main"], visible["off"])
            return {slot: ladders.picks(slot, entries) for slot, entries in visible.items()}, others

        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for mode in ladders.MODES:
                    for flt in ladders.FILTERS:
                        full = shown(lambda *key: self.full[key], token, spec, mode, flt)
                        kept = shown(lambda t, s, m, slot: self.kept[t][s][m][slot], token, spec, mode, flt)
                        self.assertEqual(kept, full, f"{token} {spec} {mode} {flt}")

    def test_every_spec_has_a_usable_list(self):
        core = ("head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet",
                "finger", "trinket", "main")
        for token, specs in self.kept.items():
            for spec, modes in specs.items():
                for mode, slots in modes.items():
                    for flt in ladders.FILTERS:
                        if flt[2]:
                            continue  # "seen in Forever only" may leave a slot empty
                        for slot in core:
                            visible = [e for e in slots[slot] if e.passes(flt)]
                            self.assertTrue(visible, f"{token} {spec} {mode} {slot} {flt}: nothing to show")

    def test_the_second_trinket_is_one_of_the_alternatives(self):
        """With three alternatives asked for, a trinket slot lists four items: the two best and two more."""
        def trinket(item_id, score, limit=None):
            return ladders.Entry(item_id=item_id, score=score, side="", twin=None, seen=True, new=False,
                                 unsourced=False, unique=False, two_hand=False, random=False, limit=limit)
        ladder = [trinket(20071, 12.0, "TalismanofBattle"), trinket(271903, 12.0),
                  trinket(21117, 11.0, "TalismanofBattle"), trinket(271906, 11.0), trinket(1490, 9.0)]
        best, alternatives = ladders.picks("trinket", ladder, 3)
        self.assertEqual([e.item_id for e in best], [20071, 271903])
        self.assertEqual([e.item_id for e in alternatives], [21117, 271906], "the fifth item is left out")
        best, alternatives = ladders.picks("head", ladder, 3)
        self.assertEqual(len(best) + len(alternatives), 4, "a slot with one best pick lists three after it")

    def test_a_placed_item_is_never_a_best_pick(self):
        """An item placed from a close spec's simulation (simulated.place) can stand first once a filter hides
        what was above it: the best pick is still the first one that is not placed, in every slot and weapon list."""
        def entry(item_id, score, placed=False, two_hand=False, limit=None):
            return ladders.Entry(item_id=item_id, score=score, side="", twin=None, seen=True, new=False,
                                 unsourced=False, unique=False, two_hand=two_hand, random=False, limit=limit,
                                 placed=placed)
        ladder = [entry(1, 30.0, placed=True), entry(2, 30.0), entry(3, 29.0, placed=True), entry(4, 28.0)]
        best, alternatives = ladders.picks("head", ladder, 6)
        self.assertEqual([e.item_id for e in best], [2])
        self.assertEqual([e.item_id for e in alternatives], [1, 3, 4], "placed items stay alternatives")
        best, alternatives = ladders.picks("trinket", ladder, 6)
        self.assertEqual([e.item_id for e in best], [2, 4], "nor is it the second trinket")
        self.assertEqual(ladders.lead([entry(5, 1.0, placed=True)]).item_id, 5, "unless there is nothing else")
        self.assertIsNone(ladders.lead([]))
        # weapons: the two-hander placed first does not weigh against the one-handers
        main = [entry(10, 99.0, placed=True, two_hand=True), entry(11, 40.0, two_hand=True), entry(12, 30.0)]
        off = [entry(13, 20.0)]
        self.assertEqual([e.item_id for e in ladders.weapon_lists(main, off)[0]], [12], "40 < 30 + 20")
        self.assertEqual([e.item_id for e in ladders.other_weapons(main, off)[0]], [10, 11])

    def test_place_moves_an_item_up_to_its_rank(self):
        """simulated.place: up to its rank with the score above it, never first; an item already that high, or
        that the ladder lacks, stays as it is."""
        def entry(item_id, score):
            return ladders.Entry(item_id=item_id, score=score, side="", twin=None, seen=True, new=False,
                                 unsourced=False, unique=False, two_hand=False, random=False, limit=None)
        ladder = [entry(i, 100.0 - i) for i in range(1, 9)]
        placed = simulated.place(ladder, [simulated.Placement(item_id=7, rank=3), simulated.Placement(item_id=2, rank=5),
                                          simulated.Placement(item_id=99, rank=2), simulated.Placement(item_id=8, rank=1)])
        self.assertEqual([e.item_id for e in placed], [1, 8, 7, 2, 3, 4, 5, 6], "rank 1 is second: never first")
        moved = {e.item_id: e for e in placed if e.placed}
        self.assertEqual(sorted(moved), [7, 8], "item 2 was already above its rank")
        self.assertEqual(moved[8].score, 99.0, "the score of the item above: the ladder stays in order")
        self.assertEqual(moved[7].score, 99.0)
        self.assertEqual([e.score for e in placed], sorted((e.score for e in placed), reverse=True))
        self.assertEqual([e.item_id for e in ladder], list(range(1, 9)), "the ladder given is left alone")
        # the item it follows rules over the rank: an item more above it does not push it down among the others
        follows = simulated.Placement(item_id=7, rank=3, after=2)
        self.assertEqual([e.item_id for e in simulated.place(ladder, [follows])], [1, 2, 7, 3, 4, 5, 6, 8])
        more = [entry(0, 100.0)] + ladder
        self.assertEqual([e.item_id for e in simulated.place(more, [follows])], [0, 1, 2, 7, 3, 4, 5, 6, 8])
        gone = [e for e in ladder if e.item_id != 2]
        self.assertEqual([e.item_id for e in simulated.place(gone, [follows])], [1, 3, 7, 4, 5, 6, 8],
                         "without the item it follows: its rank")

    def test_placements_count_until_the_spec_is_measured(self):
        """placed.json counts in the PvE lists of a spec the simulator has not measured, and nowhere else."""
        hand = [simulated.Placement(item_id=11815, rank=5)]
        reading = simulated.Reading(specs={("WARRIOR", 2): simulated.SpecRanking(slots={})},
                                    placed={("WARRIOR", 2): {"trinket": hand}, ("PALADIN", 3): {"trinket": hand}})
        db = types.SimpleNamespace(simulated=reading)
        self.assertEqual(simulated.placements(db, "PALADIN", 3, "pve", "trinket"), hand)
        self.assertEqual(simulated.placements(db, "PALADIN", 3, "pvp", "trinket"), [])
        self.assertEqual(simulated.placements(db, "PALADIN", 3, "pve", "neck"), [])
        self.assertEqual(simulated.placements(db, "WARRIOR", 2, "pve", "trinket"), [], "measured: its own scores")

    def test_the_placed_items_are_in_their_lists(self):
        """Every placement of placed.json for a spec not yet measured is in its PvE list at its rank, flagged."""
        reading = self.db.simulated
        checked = 0
        for (token, spec), slots in reading.placed.items():
            if (token, spec) in reading.specs:
                continue
            for slot, placements in slots.items():
                ladder = ladders.full_ladder(self.db, token, spec, "pve", slot)
                ids = [e.item_id for e in ladder]
                for placement in placements:
                    self.assertIn(placement.item_id, ids, f"{token} {spec} {slot}")
                    index = ids.index(placement.item_id)
                    where = f"{token} {spec} {slot} {placement.item_id}"
                    self.assertIn(placement.after, ids, f"{where}: the item it follows left the list")
                    self.assertLessEqual(index, ids.index(placement.after) + 1, where)
                    self.assertLessEqual(index + 1, placement.rank, f"{where}: higher than its rank")
                    self.assertGreater(index, 0, "never first")
                    checked += 1
                kept = self.kept[token][spec]["pve"][slot]
                self.assertTrue(any(e.placed for e in kept), f"{token} {spec} {slot}: the data keeps it")
        if not checked:
            self.skipTest("placed.json places nothing: every spec it would name is measured")

    def test_the_rank_an_item_needs(self):
        """Forever's PvP gear by slot, and the rank rewards of Classic, which no vendor sells."""
        def needs(item_id):
            return ranks.required(self.db.items[item_id], self.db.gear.get(item_id))
        self.assertEqual(needs(272453), ranks.NO_RANK, "Premier Magus Footwraps, of the blue set")
        self.assertEqual(needs(272578), 3, "Premier Sergeant's Cloak")
        self.assertEqual(needs(274969), 4, "Premier Master Sergeant's Insignia")
        self.assertEqual(needs(272787), 13, "Premier Field Marshal's Plate Helm")
        self.assertEqual(needs(272856), 14, "Premier Grand Marshal's Mageblade")
        self.assertEqual(needs(17602), ranks.NOT_SOLD, "Field Marshal's Headdress")
        self.assertEqual(needs(23451), ranks.NOT_SOLD, "Grand Marshal's Mageblade")
        self.assertEqual(needs(16342), ranks.NOT_SOLD, "Sergeant's Cape")
        self.assertEqual(needs(19595), ranks.NO_RANK, "Dryad's Wrist Bindings, of a battleground's faction")
        epic = {self.db.gear[i]["inv"]: needs(i) for i, item in self.db.items.items()
                if item["name"].startswith(ranks.PREMIER) and self.db.gear.get(i, {}).get("req") == 60
                and self.db.gear[i]["inv"] in ranks.SEAL_RANKS}
        self.assertEqual(epic, ranks.SEAL_RANKS, "every armor slot of the epic set has its seal's rank")

    def test_the_rank_cap_leaves_out_what_the_week_does_not_allow(self):
        def entry(**fields):
            return ladders.Entry(item_id=1, score=1.0, side="", twin=None, seen=True, new=False, unsourced=False,
                                 unique=False, two_hand=False, random=False, limit=None, **fields)
        everything = ("a", False, False, phases.PRE_RAID, True, None)
        week_3 = ("a", False, False, phases.PRE_RAID, True, 6)
        self.assertTrue(entry(rank=13).passes(everything))
        self.assertFalse(entry(rank=13).passes(week_3))
        self.assertTrue(entry(rank=13).passes((*week_3[:5], 13)))
        self.assertTrue(entry(rank=4).passes(week_3))
        self.assertFalse(entry(rank=ranks.NOT_SOLD).passes((*week_3[:5], 14)), "not even at rank 14")
        blue = ladders.Entry(
            item_id=1, score=1.0, side="", twin=None, seen=False, new=True, unsourced=True, unique=False,
            two_hand=False, random=False, limit=None, honor=True)
        self.assertFalse(blue.passes(everything), "with no source, it stays out of a list that ignores the cap")
        self.assertTrue(blue.passes(week_3), "the honor quartermasters sell it")
        self.assertEqual(ranks.filter_caps(), (3, 5, 8, 9, 11, 12, 13, 14))

    def test_entry_encoding_with_a_rank(self):
        entry = ladders.Entry(item_id=272787, score=50.0, side="a", twin=272788, seen=False, new=True,
                              unsourced=True, unique=False, two_hand=False, random=False, limit=None,
                              pvp=True, rank=13, honor=True)
        self.assertEqual(luaout.encode_entry(entry), "272787:500:anupv:272788::13")

    def test_entry_encoding(self):
        entry = ladders.Entry(item_id=22748, score=51.24, side="a", twin=22747, seen=True, new=False,
                              unsourced=False, unique=False, two_hand=False, random=False, limit=None)
        self.assertEqual(luaout.encode_entry(entry), "22748:512:as:22747")
        plain = ladders.Entry(item_id=12587, score=44.2, side="", twin=None, seen=False, new=False,
                              unsourced=False, unique=False, two_hand=False, random=False, limit=None)
        self.assertEqual(luaout.encode_entry(plain), "12587:442")
        ring = ladders.Entry(item_id=21205, score=38.3, side="", twin=None, seen=False, new=False,
                             unsourced=False, unique=True, two_hand=False, random=False, limit="SignetRingoftheB",
                             phase=phases.LATER)
        self.assertEqual(luaout.encode_entry(ring), "21205:383:U9::SignetRingoftheB")
        pendant = ladders.Entry(item_id=18404, score=30.0, side="", twin=None, seen=False, new=False,
                                unsourced=False, unique=False, two_hand=False, random=False, limit=None, phase=1)
        self.assertEqual(luaout.encode_entry(pendant), "18404:300:1")
        helm = ladders.Entry(item_id=16478, score=117.1, side="a", twin=16542, seen=False, new=False,
                             unsourced=False, unique=True, two_hand=False, random=False, limit=None, pvp=True)
        self.assertEqual(luaout.encode_entry(helm), "16478:1171:aUp:16542")

    # -- phases ------------------------------------------------------------------------------

    def phase_of(self, item_id: int) -> int:
        return phases.item_phase(self.db.items[item_id])

    def test_phase_of_known_items(self):
        before_the_raids = {
            12587: "Eye of Rend, a dungeon boss",
            22006: "a dungeon set 2 piece, from its quest chain",
            12640: "Lionheart Helm, crafted from ordinary materials",
            11302: "Uther's Strength: Onyxia has it, and so does the rest of the world",
            16341: "a PvP rank reward",
        }
        for item_id, what in before_the_raids.items():
            self.assertEqual(self.phase_of(item_id), phases.PRE_RAID, what)
        first_raids = {18404: "Onyxia Tooth Pendant, for her head", 18348: "Quel'Serrar, forged in her breath"}
        for item_id, what in first_raids.items():
            self.assertEqual(self.phase_of(item_id), 1, what)
        classic_raids = {
            22589: "Atiesh", 19384: "Master Dragonslayer's Ring, for Nefarian's head", 21205: "a Brood of Nozdormu ring",
            18543: "Ring of Entropy, from Lord Kazzak", 19140: "Cauterizing Band, from Molten Core's Flamewakers",
            23025: "Seal of the Damned, from the Four Horsemen's chest", 19683: "Bloodvine Leggings, made of Bloodvine",
            22670: "Icebane Gauntlets, made of Frozen Runes", 19167: "Blackfury, made of Molten Core's cores",
            17193: "Sulfuron Hammer, made from eight Sulfuron Ingots",
        }
        for item_id, what in classic_raids.items():
            self.assertEqual(self.phase_of(item_id), phases.LATER, what)

    def test_phases_are_consistent(self):
        self.assertEqual(phases.PHASES[0], phases.PRE_RAID)
        self.assertEqual(phases.PHASES[-1], phases.LATER)
        self.assertEqual(list(phases.PHASES), sorted(set(phases.PHASES)))
        self.assertIn(phases.CURRENT, phases.PHASES)
        self.assertTrue(all(0 < phase < phases.LATER for phase in phases.RAID_PHASE.values()))
        self.assertEqual(phases.unknown_raids(self.db), [], "the data has a raid phases.py does not name")
        for ladder in self.full.values():
            for entry in ladder:
                self.assertIn(entry.phase, phases.PHASES)
        # every crafted piece named in phases.py is spelled as the data spells it, when the data has it
        crafted = {item["name"] for item in self.db.items.values() if any(s[0] == "c" for s in item["sources"])}
        named = set(phases.RAID_CRAFTS)
        self.assertGreater(len(named & crafted), 30, "few of the crafted pieces named in phases.py are in the data")

    def test_a_list_before_the_raids_needs_no_raid(self):
        """An item whose every listed source needs a raid, and that no other source group could
        provide, is never counted as available before the raids."""
        checked = 0
        for ladder in self.full.values():
            for entry in ladder:
                item = self.db.items[entry.item_id]
                raids = [phases.source_raid(source, item["name"]) for source in item["sources"]]
                if raids and all(raids) and len(item["groups"] - {"u"}) == 1:
                    self.assertGreater(entry.phase, phases.PRE_RAID, f"{item['name']} ({entry.item_id})")
                    checked += 1
        self.assertGreater(checked, 100)

    def test_first_source_is_one_of_the_items_phase(self):
        """The addon says an item's first source. It must not need a later phase than the item itself,
        and a world drop is not named after a boss nobody can go and kill."""
        late = []
        for item_id in luaout.shown_ids(self.kept):
            item = self.db.items.get(item_id)
            if not item or not item["sources"]:
                continue
            first = phases.shown_sources(item)[0]
            if phases.source_phase(first, item["name"]) > phases.item_phase(item):
                late.append(item["name"])
        self.assertEqual(late, [], "listed for a way the data does not spell out: shown_sources needs a rule for it")
        uther = self.db.items[11302]
        self.assertEqual([source[0] for source in uther["sources"]], ["d", "m"], "the data changed: pick another example")
        self.assertEqual(phases.shown_sources(uther)[0], ["w", "0", "0", "k"],
                         "Uther's Strength is a world drop: Onyxia has it, as every boss does")
        self.assertEqual(phases.shown_sources(uther)[1][:3], ["d", "249", "Onyxia"])
        text = luaout.items_file(self.db, self.kept)
        self.assertIn("\n11302|Uther's Strength|rwx||w^0^0^k~d^249^Onyxia^", text)
        self.assertNotIn("Colossus of", text)
        # sources that agree with the item's phase keep the data's order
        eye = self.db.items[12587]
        self.assertEqual(phases.shown_sources(eye), eye["sources"])
        # the phases themselves do not move: a world dropper was already taken for an ordinary creature
        self.assertEqual(self.phase_of(11302), phases.PRE_RAID)

    def test_later_phases_only_add_items(self):
        for (token, spec, mode, slot), ladder in self.full.items():
            previous = None
            for phase in phases.PHASES:
                visible = {e.item_id for e in ladder if e.passes(("a", True, False, phase))}
                if previous is not None:
                    self.assertLessEqual(previous, visible, f"{token} {spec} {mode} {slot} phase {phase}")
                previous = visible

    # -- the two weapon styles ---------------------------------------------------------------

    def test_other_weapons_are_the_style_that_lost(self):
        # Derive the expected winner from the paired DPS observations, independently of
        # the generator's per-entry weapon-set flags and the W rows it emits for Lua.
        source = BUILD / "corrections" / "balance_weapon_sets.json"
        controls = json.loads(source.read_text(encoding="utf-8"))
        observed = {(side, staff, main, off): (gain, error)
                    for side, rows in controls["by_side"].items() for staff, main, off, gain, error in rows}
        self.assertTrue(observed)
        enchants = luaout.best_enchants(self.enchant_ladder("DRUID", 1), phases.PRE_RAID)
        self.assertIn(controls["spellblasting"], enchants["w2h"])
        compared = set()
        seen = {"one": 0, "two": 0, "none": 0}
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for mode in ladders.MODES:
                    for flt in ladders.FILTERS:
                        slots = ladders.visible_slots({s: self.full[token, spec, mode, s] for s in ("main", "off")}, flt)
                        main, off = slots["main"], slots["off"]
                        best_main, best_off = ladders.weapon_lists(main, off)
                        other_main, other_off = ladders.other_weapons(main, off)
                        self.assertFalse(set(best_main) & set(other_main))
                        two = ladders.lead([e for e in main if e.two_hand])
                        one = ladders.lead([e for e in main if not e.two_hand])
                        if two and one:
                            partner = ladders.lead([e for e in off if e.item_id != one.item_id])
                            expect_two = two.stored >= one.stored + (partner.stored if partner else 0)
                            if partner and (token, spec, mode, flt[3]) == ("DRUID", 1, "pve", phases.PRE_RAID):
                                side = flt[0]
                                key = (side, two.shown(side), one.shown(side), partner.shown(side))
                                if key in observed:
                                    gain, error = observed[key]
                                    self.assertGreater(gain, 2 * error, key)
                                    expect_two = True
                                    compared.add(key)
                            self.assertEqual(best_main[0].two_hand, expect_two, (token, spec, mode, flt))
                        if not other_main:
                            self.assertEqual(other_off, [])
                            seen["none"] += 1
                        elif best_main[0].two_hand:
                            self.assertTrue(all(not e.two_hand for e in other_main))
                            self.assertEqual(best_off, [])
                            if one:
                                self.assertNotIn(one.item_id, [e.item_id for e in other_off])
                            seen["one"] += 1
                        else:
                            self.assertTrue(all(e.two_hand for e in other_main))
                            self.assertEqual(other_off, [])
                            seen["two"] += 1
        self.assertEqual(compared, set(observed), "every measured faction and equipment set was exercised")
        self.assertTrue(all(seen.values()), f"a case never came up: {seen}")

    def test_files_keep_the_credit_line(self):
        for text in (luaout.meta_file(self.db), luaout.lists_file(self.db, self.kept),
                     luaout.items_file(self.db, self.kept), luaout.enchants_file(self.db, self.kept)):
            self.assertTrue(text.startswith(fdb.HEADER_PREFIX))
            self.assertIn("see NOTICE.txt", text.split("\n", 1)[0])

    def test_every_listed_item_has_a_line(self):
        text = luaout.items_file(self.db, self.kept)
        described = {int(line.split("|", 1)[0]) for line in text.split("\n") if line[:1].isdigit() and "|" in line}
        missing = luaout.shown_ids(self.kept) - described
        self.assertFalse(missing, f"no source line for {sorted(missing)[:10]}")

    def enchant_ladder(self, token: str, spec: int) -> dict:
        return luaout.enchant_ladders(self.db, token, spec, self.kept[token][spec])

    def test_enchants_cover_every_spec(self):
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                ladder = self.enchant_ladder(token, spec)
                previous = None
                for phase in phases.PHASES:
                    best = luaout.best_enchants(ladder, phase)
                    for key in ("chest", "wrist", "hands", "feet"):
                        self.assertIn(key, best, f"{token} {spec} phase {phase}: no enchant for {key}")
                    self.assertTrue({"w1h", "w2h"} & set(best), f"{token} {spec} phase {phase}: no weapon enchant")
                    for key, enchants in best.items():
                        self.assertLessEqual(len(enchants), luaout.ENCHANTS_PER_SLOT)
                        needed = dict(ladder[key])
                        self.assertTrue(all(needed[enchant] <= phase for enchant in enchants))
                    if previous is not None:
                        self.assertLessEqual(set(previous), set(best), "a later phase lost a slot's enchants")
                    previous = best

    def test_enchant_phases(self):
        phase = lambda enchant: phases.enchant_phase(self.db, enchant)  # noqa: E731
        before_the_raids = {
            "s23800": "Enchant Weapon - Agility, sold by the Timbermaw",
            "s23804": "Enchant Weapon - Mighty Intellect, sold by the Thorium Brotherhood",
            "i18329": "Arcanum of Rapidity, a Dire Maul libram",
            "s20023": "a formula that drops in Stratholme",
            "i273593": "an enchant of Forever with no known source",
        }
        for enchant, what in before_the_raids.items():
            self.assertEqual(phase(enchant), phases.PRE_RAID, what)
        self.assertEqual(phase("s20025"), 1, "a formula the data says drops in Onyxia's Lair")
        classic_raids = {
            "i23548": "Might of the Scourge, from Sapphiron", "i19785": "Falcon's Call, from Zul'Gurub's idols",
            "i20077": "a Zandalar signet", "s22749": "Enchant Weapon - Spell Power, a Molten Core formula",
            "s25080": "Enchant Gloves - Superior Agility, an Ahn'Qiraj formula",
        }
        for enchant, what in classic_raids.items():
            self.assertEqual(phase(enchant), phases.LATER, what)
        # every enchant phases.py names that the data has is still one the data knows by that id
        named = set(phases.RAID_ENCHANTS) & set(self.db.enchant_info)
        self.assertGreater(len(named), 15, "few of the enchants named in phases.py are in the data")
        # before the raids, no spec is shown an enchant that needs one
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for enchants in luaout.best_enchants(self.enchant_ladder(token, spec), phases.PRE_RAID).values():
                    self.assertFalse(set(enchants) & set(phases.RAID_ENCHANTS), f"{token} {spec}")

    def test_a_hunter_holds_nothing_in_the_off_hand(self):
        for spec in self.db.classes["HUNTER"]["specs"]:
            for mode in ladders.MODES:
                held = [entry.item_id for entry in self.full[("HUNTER", spec, mode, "off")]
                        if self.db.gear[entry.item_id]["inv"] == ladders.INV_HELD]
                self.assertEqual(held, [], f"Hunter {spec} {mode}")
        site = ladders.full_ladder(self.db, "HUNTER", 1, "pve", "off", rank_rewards=False)
        self.assertIn(22329, [entry.item_id for entry in site], "the site's rule keeps them")

    def test_enchant_groups_fit_the_spec(self):
        """A weapon, shield, held or ranged enchant is listed only for a spec whose PvE list holds such an item."""
        specs = {(token, spec["name"]): set(self.enchant_ladder(token, index))
                 for token, data in self.db.classes.items() for index, spec in data["specs"].items()}
        shields = {key for key, keys in specs.items() if "shield" in keys}
        self.assertEqual({token for token, _ in shields}, {"WARRIOR", "PALADIN", "SHAMAN"},
                         "only three classes carry a shield")
        self.assertIn(("WARRIOR", "Protection"), shields)
        self.assertNotIn(("WARRIOR", "Arms"), shields)
        for name in ("Beast Mastery", "Marksmanship", "Survival"):
            self.assertFalse(specs[("HUNTER", name)] & {"shield", "held"}, f"Hunter {name}")
            self.assertIn("rng", specs[("HUNTER", name)])
        self.assertEqual(specs[("ROGUE", "Combat")] & {"w1h", "w2h", "shield", "held", "rng"}, {"w1h"})
        self.assertIn("held", specs[("PRIEST", "Shadow")])
        self.assertEqual({key for key, keys in specs.items() if "rng" in keys}, {k for k in specs if k[0] == "HUNTER"})
        # the armor slots are everyone's
        for key, keys in specs.items():
            self.assertLessEqual({"chest", "wrist", "hands", "feet"}, keys, key)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_lua_reads_the_files_back(self):
        """The files load as Lua and decode to exactly what was written."""
        lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        run, lists, items, enchants, ns = lua.execute(LUA_READER)
        files = {"Meta.lua": luaout.meta_file(self.db), "Lists.lua": luaout.lists_file(self.db, self.kept),
                 "Items.lua": luaout.items_file(self.db, self.kept), "Enchants.lua": luaout.enchants_file(self.db, self.kept)}
        for name, text in files.items():
            run(text, "=" + name)

        self.assertEqual(ns.data.meta.level, 60)
        self.assertEqual(ns.data.meta.build, self.db.meta["build"])
        self.assertEqual(ns.data.meta.credit, luaout.CREDIT)
        self.assertEqual(list(ns.data.meta.phases.values()), list(phases.PHASES))
        self.assertEqual(ns.data.meta.phase, phases.CURRENT)

        expected = []
        for token, specs in self.kept.items():
            for spec, modes in specs.items():
                for mode, slots in modes.items():
                    for slot, entries in slots.items():
                        for entry in entries:
                            fields = (luaout.encode_entry(entry).split(":") + [""] * 6)[:6]
                            expected.append(",".join([token, str(spec), mode, slot] + fields))
        self.assertEqual(sorted(lists().split("\n")), sorted(expected))

        read_items = dict(line.split("|", 1) for line in items().split("\n"))
        for item_id in luaout.shown_ids(self.kept):
            self.assertEqual(read_items[str(item_id)], self.db.items[item_id]["name"])

        count, missing = enchants()
        self.assertGreater(count, 27 * 8)
        self.assertEqual(missing, 0)

    def test_the_audit_runs_on_the_real_lists(self):
        findings = audit.run(self.db, self.kept, read_in_game=frozenset(corrections.load()))
        self.assertEqual(len(audit.report(findings)), len(findings) + len({f.kind for f in findings}))
        for finding in findings:
            self.assertIn(finding.kind, (audit.LOW, audit.POWERLESS, audit.LONELY, audit.ADDED))
            self.assertEqual(finding.name, self.db.items[finding.item_id]["name"])
            self.assertTrue(set(finding.phases) <= set(phases.PHASES))
        self.assertLessEqual(len(audit.suspicious(findings)), len(findings))

    def test_gear_keeps_the_required_level(self):
        levels = [gear["req"] for gear in self.published.gear.values()]
        self.assertTrue(all(0 <= level <= self.published.meta["cap"] for level in levels))
        self.assertGreater(sum(1 for level in levels if level >= 50), 1000)

    def test_the_capture_reads_the_pools_weapons(self):
        ids = capture.weapon_ids(self.published)
        self.assertEqual(ids, sorted(set(ids)))
        self.assertGreater(len(ids), 1000)
        for item_id in ids:
            self.assertIn(self.published.gear[item_id]["inv"], corrections.WEAPONS)
        ranked = {entry.item_id for (_, _, _, slot), ladder in self.full.items() if slot == "main" for entry in ladder}
        read = set(ids) | set(capture.capture_ids(self.published)["unlisted"])   # the weapons added from the game
        read |= set(corrections.HAND_LISTED)   # ... and the ones written by hand, under the level the capture reads from
        self.assertLessEqual(ranked, read, "a main-hand entry of a ladder is not on the capture's list")

    def test_the_data_says_which_lists_the_simulator_ranked(self):
        """An M line for each PvE list ranked by simulation, with the day of its measure; none for any other list."""
        found, token = {}, None
        for line in luaout.lists_file(self.db, self.kept).splitlines():
            block = re.match(r"^(\w+) = \[==\[$", line)
            if block:
                token = block.group(1)
            elif line.startswith("M\t"):
                kind, spec, mode, day = line.split("\t")
                found[token, int(spec), mode] = day
        reading = self.db.simulated
        self.assertTrue(reading.specs, "no list is ranked by simulation")
        self.assertEqual(found, {(token, spec, "pve"): ranking.record.get("date") or reading.date
                                 for (token, spec), ranking in reading.specs.items()})
        self.assertTrue(all(re.fullmatch(r"\d{4}-\d\d-\d\d", day) for day in found.values()), found)

    def test_a_score_that_is_no_full_measure_is_flagged(self):
        """Flag g: an entry of a list ranked by simulation whose score the file does not hold as a full measure."""
        reading = self.db.simulated
        flagged = plain = 0
        for (token, spec, mode, slot), ladder in self.full.items():
            slot_ranking = ladders.slot_ranking(self.db, token, spec, mode, slot)
            for entry in ladder:
                expected = slot_ranking is not None and not slot_ranking.measured(entry.item_id) and not entry.placed
                self.assertEqual(entry.estimated, expected, (token, spec, mode, slot, entry.item_id))
                self.assertEqual("g" in luaout.encode_entry(entry).split(":")[2:3][0] if entry.estimated else False,
                                 entry.estimated)
                flagged += entry.estimated
                plain += not entry.estimated
        self.assertGreater(flagged, 0)
        self.assertGreater(plain, flagged, "most scores are full measures")
        ranking = next(iter(reading.specs.values()))
        slot = next(iter(ranking.slots.values()))
        self.assertFalse(slot.measured(-1), "an item the file does not hold is not measured")

    def test_a_piece_written_by_hand_is_listed(self):
        """corrections.include: Flurry Axe, which neither ForeverDB's lists nor the capture hold, is in the lists."""
        self.assertEqual(self.db.included, sorted(corrections.HAND_LISTED))
        for item_id, (name, sources) in corrections.HAND_LISTED.items():
            self.assertNotIn(item_id, self.published.items)
            item = self.db.items[item_id]
            self.assertEqual((item["name"], item["groups"]), (name, frozenset(source[0] for source in sources)))
            self.assertTrue(all(source[-1] == corrections.SOURCE_LABEL for source in item["sources"]))
            self.assertNotIn("added", item)   # listed as ForeverDB lists an item: a source, and the phase it needs
        default = ("a", False, False, phases.CURRENT, True, None)
        for slot in ("main", "off"):
            shown = [entry.item_id for entry in self.full["ROGUE", 2, "pve", slot] if entry.passes(default)]
            self.assertIn(871, shown, slot)
        self.assertNotIn(871, [entry.item_id for entry in self.full["MAGE", 2, "pve", "main"]])
        listed = types.SimpleNamespace(gear={871: self.db.gear[871]}, items={871: {"name": "as the data has it"}}, classes={})
        self.assertEqual(corrections.include(listed), [])   # a piece the data comes to list is left alone
        self.assertEqual(listed.items[871], {"name": "as the data has it"})

    def test_the_lists_follow_what_the_game_has(self):
        """corrections.align on the real data: with the default options the lists only lose what the game lacks."""
        game = self.db.aligned
        if not game.build:
            self.skipTest("the game was not read yet (corrections/game.json)")
        pooled = {item_id for data in self.db.classes.values() for pool in data["pools"].values() for item_id, _ in pool}
        absent = set(corrections.load_game()["absent"])
        self.assertFalse(pooled & absent, "an item the game does not have is still in a pool")
        self.assertLessEqual(set(game.dropped), absent)
        settled = set(self.db.confirmed.settled)
        self.assertTrue(settled and settled <= set(game.added))
        for item_id in settled:
            item = self.db.items[item_id]
            self.assertTrue(any(source[0] == "d" and source[-1] == corrections.DROP_LABEL for source in item["sources"]))
            self.assertTrue(item["groups"] <= frozenset("dr") and item["phase"] != phases.LATER or "r" in item["groups"], item["name"])
        for item_id in game.added:
            self.assertNotIn(item_id, self.published.items)
            self.assertIn(item_id, pooled)
            if item_id in settled:
                continue   # its drop was counted in Forever (corrections._settle_added): a dungeon's item, or a raid's
            self.assertEqual((self.db.items[item_id]["groups"], self.db.items[item_id]["phase"]), (frozenset("u"), phases.LATER))
        self.assertFalse(set(game.added) & set(corrections.NOT_FOR_PLAYERS))
        shown = luaout.shown_ids(self.kept)
        self.assertFalse(shown & absent, "an item the game does not have is in a list, or is a list item's twin")
        self.assertTrue(shown & set(game.added), "no added piece makes a list")

        before = fdb.load(CACHE, corrected=False)
        corrections.apply(before, corrections.load())   # the weapons' stats, not the game's items
        fdb.verified_gear.apply(before)  # the independently verified level-60 stats are common to both sides
        corrections.complete_shields(before)   # compare the same block values on both sides of the item-presence check
        corrections.complete_weapon_hits(before)
        corrections.include(before)   # ... and the pieces written by hand, which no capture says anything of
        corrections.fill(before, corrections.load_sources())   # ... and the sources read in QuestieDB
        corrections.confirm(before, corrections.load_drops())  # ... and the bosses counted in Forever, a source too
        corrections.price(before, corrections.load_costs())    # ... and who the neutral vendors sell to
        # ... and what the simulator ranked; placed.json is made on the corrected lists, so both sides leave it out
        unplaced = dataclasses.replace(self.db.simulated, placed={})
        before.simulated = unplaced
        corrections.assign_sides(before)   # ... and the side of Theramore's pieces
        corrections.pair_basin_mail_shoulders(before)
        corrections.assign_reward_sides(before)
        fdb.raid_sources.apply(before)   # keep the same documented acquisition routes on both sides
        fdb.specs.apply(before)   # ... and the tanks' weights and the Feral cat: the same items, ranked another way
        was = ladders.build_all(before)
        after = copy.copy(self.db)
        after.simulated = unplaced
        gone = set(game.dropped)
        for token, specs in ladders.build_all(after).items():
            for spec, modes in specs.items():
                for mode, slots in modes.items():
                    for flt in ladders.FILTERS:
                        if flt[1]:
                            continue   # with the items of no known source: the added pieces show there
                        now, then = audit.shown_rows(slots, flt), audit.shown_rows(was[token][spec][mode], flt)
                        # an item level with the best picks carries the ladder's first score, whatever is first
                        own = lambda shown: [[dataclasses.replace(entry, score=0.0) if entry.level else entry
                                              for entry in rows] for rows in shown]
                        for slot in now:
                            if any(entry.item_id in settled or entry.item_id in self.db.placed
                                   for rows in now[slot] for entry in rows):
                                continue   # a piece added from the game takes a row there: its drop was counted
                            if own(now[slot]) != own(then[slot]):
                                lost = {entry.item_id for rows in then[slot] for entry in rows} & gone
                                self.assertTrue(lost, f"{token} {spec} {mode} {slot} {flt} changed with nothing dropped")


    def test_theramores_pieces_are_the_alliances(self):
        """corrections.assign_sides: no piece sold against Theramore is left to both sides, and no other piece moves."""
        raw = fdb.load(CACHE, corrected=False)
        sold = {item_id for item_id, item in raw.items.items()
                if any(source[0] == "r" and source[1] == "2799" for source in item["sources"])}
        self.assertTrue(sold)
        open_to_both = {item_id for item_id in sold if not raw.items[item_id]["side"]}
        self.assertEqual(set(corrections.assign_sides(raw)), open_to_both)
        self.assertEqual({raw.items[item_id]["side"] for item_id in sold}, {"a"})
        self.assertEqual(corrections.assign_sides(raw), [], "a second pass finds nothing left to do")

    def test_a_simulated_list_holds_what_the_simulator_measures(self):
        """A list ranked by simulation holds an item ForeverDB's weights give nothing when the file has a measure for
        it (a trinket that is all proc): the weights say what to list only where they rank. A list on the weights
        holds no such item."""
        held = 0
        for (token, spec, mode, slot), ladder in self.full.items():
            weights = self.db.classes[token]["specs"][spec]["weights"][ladders.MODES[mode]]
            ranking = ladders.slot_ranking(self.db, token, spec, mode, slot)
            melee = (token, mode) == ("HUNTER", "pvp") and self.db.classes[token]["specs"][spec]["role"] == ladders.MELEE
            for entry in ladder:
                if ladders.score(self.db, entry.item_id, weights, token, melee) or entry.level or entry.pvp_utility:
                    continue   # entry.level: what the weights cannot value, listed by hand (specs.unvalued)
                self.assertIsNotNone(ranking, f"{token} {spec} {mode} {slot}: {entry.item_id} weighs nothing")
                self.assertTrue(ranking.scores.get(entry.item_id, 0) > 0 or entry.item_id in self.db.placed, entry.item_id)
                held += 1
        self.assertGreater(held, 20)

    def test_an_item_the_weights_give_nothing_is_placed_after_another(self):
        """Heart of Wyrmthalak is all proc, and ForeverDB's weights give it nothing: by hand (corrections/effects.json)
        it stands right after Hand of Justice in the lists ranked by simulation that hold that one, with its score for
        the ladder to stay in order, flagged as no score of its own, and is never a best pick. No other list holds it."""
        heart, justice = 22321, 11815
        self.assertEqual(self.db.placed[heart], justice)
        self.assertIn(heart, self.db.confirmed.settled)
        self.assertEqual((self.db.items[heart]["groups"], self.db.items[heart]["phase"]), (frozenset("d"), phases.PRE_RAID),
                         "its drop was counted in Forever: not kept with the pieces of no known source")
        held = []
        for (token, spec, mode, slot), ladder in self.full.items():
            ids = [entry.item_id for entry in ladder]
            if heart not in ids:
                continue
            held.append((token, spec, mode, slot))
            at = ids.index(heart)
            self.assertEqual((mode, slot), ("pve", "trinket"))
            self.assertIsNotNone(ladders.slot_ranking(self.db, token, spec, mode, slot), "a list on the weights does not hold it")
            self.assertEqual(ids[at - 1], justice)
            self.assertTrue(ladder[at].placed and not ladder[at].estimated)
            self.assertEqual(ladder[at].score, ladder[at - 1].score)
            best, _ = ladders.picks(slot, ladder)
            self.assertNotIn(heart, [entry.item_id for entry in best])
        self.assertIn(("ROGUE", 2, "pve", "trinket"), held)
        self.assertIn(("DRUID", 4, "pve", "trinket"), held)
        self.assertGreaterEqual(len(held), 6)

        entry = lambda item_id, score: dataclasses.replace(self.full["ROGUE", 2, "pve", "trinket"][0], item_id=item_id, score=score)
        ladder = [entry(1, 9.0), entry(2, 5.0), entry(3, 0.0)]
        moved = ladders.after_their_anchor(ladder, {3: 1})
        self.assertEqual([(e.item_id, e.score, e.placed) for e in moved], [(1, 9.0, False), (3, 9.0, True), (2, 5.0, False)])
        self.assertEqual([e.item_id for e in ladders.after_their_anchor(ladder, {3: 7})], [1, 2],
                         "without the item it follows, the ladder does not hold it")

    def test_a_note_is_checked_before_it_is_written(self):
        """A note the addon could not show as written stops the build: a spec that does not exist, a text that is
        missing or on two lines, an item no list shows."""
        shown = luaout.shown_ids(self.kept)
        good = {"items": [647], "specs": ["WARRIOR 1"], "simulated": True, "en": "A word.", "fr": "Un mot."}
        self.assertEqual(notes.shown(self.db, shown, [good]), [good])
        for change in ({"specs": ["WARRIOR 9"]}, {"specs": ["Arms"]}, {"fr": " "}, {"en": "two\nlines"},
                       {"items": []}, {"items": [1]}, {"comment": "x"}, {"slot": "left hand"}, {"list": "raid"}):
            with self.assertRaises(ValueError, msg=change):
                notes.shown(self.db, shown, [{**good, **change}])
        self.assertEqual(notes.shown(self.db, shown, [{**good, "items": [1, 647]}])[0]["items"], [647],
                         "of several items, the ones the lists show")

    def test_partial_measure_note_follows_the_faction_variant_used_by_the_sim(self):
        entry = dataclasses.replace(self.full["ROGUE", 2, "pve", "head"][0], item_id=101, side="a", twin=202)
        record = types.SimpleNamespace(record={"side": "h", "without_effect": [202]})
        db = types.SimpleNamespace(simulated=types.SimpleNamespace(specs={("ROGUE", 2): record}))
        limits = notes.simulation_limits(db, {"ROGUE": {2: {"pve": {"head": [entry]}}}})
        self.assertEqual(len(limits), 1)
        self.assertEqual(limits[0]["items"], [202])
        self.assertEqual(limits[0]["specs"], ["ROGUE 2"])
        self.assertTrue(limits[0]["simulated"])

    def test_the_notes_file_holds_what_was_written_by_hand(self):
        """Data/Notes.lua holds corrections/notes.json note by note, in both languages, as the build left it."""
        written = notes.load()
        self.assertTrue(written, "corrections/notes.json holds no note")
        text = luaout.notes_file(self.db, self.kept)
        self.assertEqual(text, (BUILD.parent / "Data" / "Notes.lua").read_text(encoding="utf-8"),
                         "Data/Notes.lua is not what the build writes: run _build/build.py")
        for note in written:
            for key in notes.LANGUAGES:
                self.assertIn(json.dumps(note[key], ensure_ascii=False), text)
        destiny = "\n".join(line for line in text.splitlines() if line.startswith("    { items = { 647 },"))
        self.assertIn("specs = { WARRIOR1 = true }", destiny)
        self.assertIn("specs = { PALADIN3 = true }", destiny, "an item can have a note for each spec")
        self.assertRegex(text, r'slot = "off", simulated = true', "and one for a slot alone")
        self.assertIn("simulated = true", destiny)
        self.assertIn('enUS = "Its proc, 200 Strength', destiny)
        self.assertIn('frFR = "Son proc, 200 de Force', destiny)

    def test_watcher_standings_are_preserved_with_unconfirmed_sources(self):
        watchers = {item_id: item for item_id, item in self.db.items.items() if item["limit"] == "WatchersRing"}
        self.assertEqual(len(watchers), 16)
        levels = [item["sources"][0][2] for item in watchers.values()]
        self.assertEqual([levels.count(str(level)) for level in range(4, 8)], [4, 4, 4, 4])
        for item in watchers.values():
            self.assertTrue(reputations.unconfirmed_watcher_ring(item))
            self.assertFalse(reputations.unconfirmed_watcher_ring(dict(item, flags=item["flags"] + "s")))
            self.assertFalse(reputations.unconfirmed_watcher_ring(dict(item, groups={"e", "v"})))
        rings = [entry for entry in self.full["PRIEST", 1, "pve", "finger"] if entry.item_id in watchers]
        self.assertTrue(rings)
        for ring in rings:
            for side in ("a", "h"):
                self.assertFalse(ring.passes((side, False, False, phases.PRE_RAID)))
                self.assertTrue(ring.passes((side, True, False, phases.PRE_RAID)))

    def test_reputation_file_matches_the_reading(self):
        """Data/Reputation.lua says what corrections/reputations.json holds, for the items the lists show."""
        reading = reputations.load()
        if not reading:
            self.skipTest("the reputations were not read yet (corrections/reputations.json)")
        text = luaout.reputation_file(self.db, self.kept, reading)
        block = lambda name: re.search(name + r" = \[==\[\n(.*?)\]==\]", text, re.S).group(1).splitlines()
        factions = {int(line.split("|")[0]): line.split("|") for line in block("factions")}
        self.assertEqual(set(factions), set(reputations.FACTIONS) & set(factions))
        self.assertEqual(factions[2819][3:5], ["0", "0"], "nothing is known of how to earn The Watchers")
        self.assertEqual({number: fields[9] for number, fields in factions.items() if fields[9]},
                         {number: str(area) for number, area in reputations.BATTLEGROUNDS.items()},
                         "the battlegrounds' factions name their battleground")
        shown = luaout.shown_ids(self.kept)
        for line in block("items"):
            fields = line.split("|")
            self.assertIn(int(fields[0]), shown)
            self.assertIn(int(fields[2]), factions)
            self.assertIn(fields[3], {"3", "4", "5", "6", "7"})
            self.assertIn(fields[4], {reputations.WEAR, reputations.QUEST, reputations.RECIPE})
            if fields[4] == reputations.RECIPE:
                self.assertTrue(fields[8] and fields[9].isdigit(), f"{fields[0]}: a recipe says its profession and skill")
                self.assertTrue(fields[10].isdigit(), f"{fields[0]}: a recipe names its recipe item")
        # a recipe's vendor is the one that sells the recipe: Timbermaw's patterns are Meilosh's, in Felwood
        rows = {line.split("|")[0]: line.split("|") for line in block("items") + block("enchants")}
        vendors = {line.split("|")[0]: line.split("|") for line in block("vendors")}
        if "15065" in rows:
            self.assertEqual(rows["15065"][4:], ["r", "11557", "", "Pattern: Warbear Woolies", "Leatherworking", "260",
                                                 "20254"])
            self.assertEqual(vendors["11557"], ["11557", "Meilosh", "1448", "65.7", "2.8"])
        if "s23800" in rows:
            self.assertEqual(rows["s23800"][1:], ["576", "5", "r", "1", "Formula: Enchant Weapon - Agility", "11557",
                                                  "19445", "Enchanting", "290"])
        for fields in rows.values():
            vendor = fields[5] if fields[0][0] != "s" else fields[6]
            if fields[3 if fields[0][0] == "s" else 4] == reputations.RECIPE and vendor:
                self.assertIn(vendor, vendors, f"{fields[0]}: the recipe's vendor is in the vendors block")

    def test_sources_read_in_questiedb_fill_the_data(self):
        """corrections.fill on the real data: an item of ForeverDB's lists gets a source and its phase, a piece
        added from the game the source alone."""
        filled = self.db.filled
        if not filled.known:
            self.skipTest("QuestieDB was not read yet (corrections/sources.json)")
        reading = corrections.load_sources()
        self.assertTrue(filled.items and filled.enchants)
        self.assertLessEqual(set(filled.added), set(self.db.aligned.added))
        for item_id in filled.items:
            item, was = self.db.items[item_id], self.published.items.get(item_id)
            self.assertTrue(item["sources"] and all(source[-1] in ("t", corrections.DROP_LABEL)
                                                    for source in item["sources"]), item_id)
            if item_id in filled.added:
                self.assertIsNone(was)
                if item_id not in self.db.confirmed.settled:   # but for the ones a counted drop settles
                    self.assertEqual((item["groups"], item["phase"]), (frozenset("u"), phases.LATER), item["name"])
            else:
                self.assertEqual((was["groups"], was["sources"]), (frozenset("u"), []), item["name"])
                self.assertTrue(item["groups"] and item["groups"] <= ladders.SOURCE_GROUPS, item["name"])
                self.assertEqual(phases.item_phase(item), item["phase"])
                raids = [corrections._raid(self.db, source, where, item["name"]) for source, where in
                         zip(reading["items"][item_id]["sources"], reading["items"][item_id].get("at") or [None] * 9)]
                self.assertEqual(item["phase"] == phases.PRE_RAID, not all(raids),
                                 f"{item['name']} counts before the raids, or does not, against its sources")
        for item_id in filled.listed:
            self.assertEqual(self.db.items[item_id]["sources"], self.published.items[item_id]["sources"],
                             "a source of ForeverDB's data was replaced")
        # every source of the file is one the data files can hold and the addon reads
        for record in reading["items"].values():
            for source in record["sources"]:
                self.assertIn(source[0], "qdvmRox")
                self.assertFalse(any(mark in text for text in source for mark in "|^~\n"), source)
        # the instance of a boss is one the data files name
        named = {int(source[1]) for item_id in filled.items for source in self.db.items[item_id]["sources"]
                 if source[0] == "d"}
        self.assertLessEqual(named, set(self.db.instances))
        self.assertEqual(phases.unknown_raids(self.db), phases.unknown_raids(self.published))
        for number in filled.instances:
            self.assertEqual(self.db.instances[number][1], "raid", "a Classic instance ForeverDB lacks is a raid")
            self.assertEqual(phases.raid_phase(phases.RAID_INSTANCES[number]), phases.LATER)

        # the arcanum of the head and legs: a quest of Dire Maul, to be had before the raids
        arcanum = self.db.enchant_info["i18331"]
        self.assertEqual(arcanum[2:4], ["Quest: Libram of Protection (Dire Maul)", "t"])
        self.assertEqual(phases.enchant_phase(self.db, "i18331"), phases.PRE_RAID)
        # an enchant of Zul'Gurub or of Sapphiron still needs its raid
        for enchant in ("i19782", "i20076", "i23545"):
            self.assertEqual(self.db.enchant_info[enchant][3], "t")
            self.assertEqual(phases.enchant_phase(self.db, enchant), phases.LATER, enchant)
        for enchant in filled.enchants:
            self.assertEqual(self.published.enchant_info[enchant][2], corrections.UNKNOWN_WHERE)
            self.assertRegex(self.db.enchant_info[enchant][2], r"^(Quest|Raid drop|Dungeon drop|Drop|Rare drop|Vendor|"
                                                               r"Chest|Container): [^|]+$")
        self.assertIn("read in QuestieDB", luaout.items_file(self.db, self.kept))
        self.assertIn("read in QuestieDB", luaout.enchants_file(self.db, self.kept))


# -- a hole in the data: the audit that shows it, the corrections that fill it, the capture they come from --------

SCEPTER, MACE, ROD, STAFF, WAND, ORB = 1, 2, 3, 7, 8, 9
ROBE = 20   # a raid set piece the data has stats for and leaves out of its lists
VEST = 30   # a cloth chest of the lists, for the tests that need a chest pool


def tiny_db():
    """A healer with four weapons, as ForeverDB's data has them: the level 28 scepter kept its healing,
    the level 57 mace and the level 54 rod lost theirs, and so did the staff."""
    db = fdb.Database()
    db.header = fdb.HEADER_PREFIX + ", build 1.0.0.1."
    db.meta = {"version": "test", "build": "1.0.0.1", "cap": 60}
    weights = {41: 1.0, 45: 1.0, 5: 0.5, "dps": 0.1}
    db.classes["PRIEST"] = {
        "specs": {1: {"name": "Holy", "role": "Healer", "style": "any", "slug": "holy",
                      "weights": {"lvl": weights, "raid": weights, "pvp": weights}}},
        "pools": {"mh": [(SCEPTER, 28), (MACE, 57), (ROD, 54)], "2h": [(STAFF, 53)], "oh": [(ORB, 55)],
                  "ranged": [(WAND, 50)]},
        "min": {"raid": 1.0, "pvp": 1.0},
    }

    def gear(inv, req, stats, dps=0.0):
        return {"inv": inv, "req": req, "stats": dict(stats), "dps": dps, "armor": 0.0, "wand": inv == 26}

    db.gear = {
        SCEPTER: gear(21, 28, {41: 68}, 21.4), MACE: gear(13, 57, {5: 13}, 45.0), ROD: gear(21, 54, {5: 5}, 38.7),
        STAFF: gear(17, 53, {5: 18}, 49.6), WAND: gear(26, 50, {45: 9}, 40.0), ORB: gear(23, 55, {41: 20}),
    }
    names = {SCEPTER: "Low Scepter", MACE: "Odd Mace", ROD: "Lively Rod", STAFF: "Channeling Staff",
             WAND: "Thin Wand", ORB: "Glowing Orb"}
    db.items = {item_id: {"name": name, "groups": frozenset("d"), "flags": "", "side": "", "twin": None,
                          "limit": None, "sources": [["d", "47", "A Boss", "20", "0", "k"]]}
                for item_id, name in names.items()}
    return db


READ = {"build": "1.0.0.1", "date": "2026-11-15", "from": "tooltip"}
IN_THE_GAME = {
    MACE: {"name": "Odd Mace", "healing": 90, "damage": 90, "dps": 29.69, **READ},
    ROD: {"name": "Lively Rod", "healing": 124, "damage": 41, "dps": 25.87, **READ},
    SCEPTER: {"name": "Low Scepter", "healing": 68, "damage": 0, "dps": 14.29, **READ},
}

# The game's stand-ins the capture tool needs, and what the game "knows" about each item.
CAPTURE_STUB = r"""
local stub = { loaded = {}, never = {}, asked = {}, unknown = {}, tooltips = {}, stats = {}, chat = {}, requests = 0 }
function print(text) stub.chat[#stub.chat + 1] = text end
C_TooltipInfo = { GetItemByID = function(id)
    if not stub.loaded[id] then return { lines = { { leftText = "Retrieving item information" } } } end
    local lines = {}
    for index, pair in ipairs(stub.tooltips[id]) do lines[index] = { leftText = pair[1], rightText = pair[2] } end
    return { lines = lines }
end }
C_Item = {
    IsItemDataCachedByID = function(id) return stub.loaded[id] == true end,
    RequestLoadItemDataByID = function(id)
        stub.requests = stub.requests + 1
        if stub.never[id] or stub.unknown[id] then return end
        if stub.quota then   -- the server answers that many requests, then none
            if stub.quota <= 0 then return end
            stub.quota = stub.quota - 1
        end
        if stub.slow then stub.asked[#stub.asked + 1] = id else stub.loaded[id] = true end
    end,
    GetItemInfo = function(id) if stub.loaded[id] then return "a name" end end,
    GetItemInfoInstant = function(id) if not stub.unknown[id] then return id end end,
    GetItemStats = function(link) return stub.stats[tonumber(link:match("%d+"))] end,
}
function GetBuildInfo() return "1.0.0", "1", "Nov 13 2026", 16001 end
function GetLocale() return stub.locale or "enUS" end
function InCombatLockdown() return stub.combat end
function CreateFrame()
    return { RegisterEvent = function() end, SetScript = function(_, kind, script)
        if kind == "OnEvent" then stub.event = script else stub.script = script end
    end }
end
function date() return "2026-11-15 12:30" end
SlashCmdList = {}
function stub.add(id, loaded, lines, stats)
    stub.loaded[id], stub.tooltips[id], stub.stats[id] = loaded, lines, stats
end
-- With stub.slow the game answers a moment after it is asked, as the real one does: what was asked for arrives.
function stub.arrive()
    for _, id in ipairs(stub.asked) do stub.loaded[id] = true end
    stub.asked = {}
end
function stub.pieces(first, last)
    for id = first, last do stub.add(id, false, { { "Piece " .. id }, { "Chest", "Cloth" } }, nil) end
end
function stub.run(source, ids)
    local ns = { ids = ids }
    assert(load(source, "=Capture.lua"))("EasyBIS_Capture", ns)
    return ns
end
return stub
"""


def saved_variable(db) -> str:
    """EasyBISCaptureDB as the game writes it to the saved variables file."""
    def quoted(text):
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    lines = ["", "EasyBISCaptureDB = {", f'["meta"] = {quoted(db.meta)},', f'["missing"] = {quoted(db.missing)},']
    lines += [f'["{name}"] = {quoted(db[name])},' for name in ("absent", "sample", "log") if db[name] is not None]
    lines.append('["items"] = {')
    lines += [f"[{item_id}] = {quoted(text)}," for item_id, text in sorted(db["items"].items())]
    return "\n".join(lines + ["},", "}", ""])


class SpecsTest(unittest.TestCase):
    """specs.py: the tanks' weights completed, and the Feral Druid split into a bear and a cat."""

    SAGEBLADE, MASTERSMITHS_HAMMER = 22383, 18048
    TANKS = (("PALADIN", 2), ("WARRIOR", 3), ("DRUID", 2))
    DEFAULT = ("a", False, False, phases.CURRENT, False, None)   # what a new player sees of a PvE list

    def test_shield_block_includes_the_base_once(self):
        gear = {279262: {"inv": 14, "stats": {}}, 18499: {"inv": 14, "stats": {48: 23}},
                18696: {"inv": 14, "stats": {48: 32}}}
        db = types.SimpleNamespace(gear=gear)
        corrections.complete_shields(db)
        corrections.complete_shields(db)
        self.assertEqual(gear[279262]["stats"][48], 44)
        self.assertEqual(gear[18499]["stats"][48], 62)  # 39 from the shield, 23 from the equip bonus
        self.assertEqual(gear[18696]["stats"][48], 32)  # unfamiliar upstream value

    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(CACHE)
        cls.published = fdb.load(CACHE, corrected=False)

    def ladder(self, token, spec, mode="pve", slot="main", db=None):
        return ladders.full_ladder(db or self.db, token, spec, mode, slot)

    def test_another_class_s_piece_is_not_listed(self):
        """ForeverDB pools by armor type, so a Rogue's Bonescythe was first in a Druid's and a Warrior's lists and a
        Mage's Frostfire in a Priest's. The game restricts those pieces (corrections/classes.json): only their class
        lists them. Most are pieces added from the game (corrections.align), which go to every pool of their armor type."""
        helmet, circlet = 22478, 22498   # Bonescythe Helmet (Rogue), Frostfire Circlet (Mage)
        self.assertEqual(self.db.class_only[helmet], frozenset(("ROGUE",)))
        self.assertEqual(self.db.class_only[circlet], frozenset(("MAGE",)))
        ids = lambda token, spec, mode: {entry.item_id for entry in self.ladder(token, spec, mode, "head")}   # noqa: E731
        self.assertIn(helmet, ids("ROGUE", 2, "pve"))
        self.assertIn(circlet, ids("MAGE", 2, "pve"))
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for mode in ladders.MODES:
                    for slot, _ in ladders.SLOTS:
                        for entry in self.ladder(token, spec, mode, slot):
                            self.assertIn(token, self.db.class_only.get(entry.item_id, (token,)),
                                          f"{token} {spec} {mode} {slot}: {entry.item_id}")
                            self.assertIn(token, self.db.class_only.get(entry.twin, (token,)),
                                          f"{token} {spec} {mode} {slot}: faction twin {entry.twin}")

    def test_a_survival_hunter_s_melee_weapon_counts_its_damage_in_pvp(self):
        """ForeverDB counts a Hunter's ranged weapon only, so a caster's staff led a Survival Hunter's PvP main hands
        on its critical strike. That spec fights in melee: its weapon's damage per second counts there. The other
        Hunters' main hands stay on their stats."""
        sunderer, staff = 18830, 20069   # Grand Marshal's Sunderer, 77.4 a second; Ironbark Staff, 42.1 and 88 spell power
        survival = {entry.item_id: entry.score for entry in self.ladder("HUNTER", 3, "pvp")}
        self.assertEqual(self.db.classes["HUNTER"]["specs"][3]["role"], "Melee DPS")
        self.assertGreater(survival[sunderer], survival[staff] + 100)
        marksman = {entry.item_id: entry.score for entry in self.ladder("HUNTER", 2, "pvp")}
        self.assertLess(marksman[sunderer], 100)

    def test_an_assassination_rogue_s_pvp_weapons_are_daggers(self):
        """Mutilate asks for a dagger in each hand: the Assassination PvP list holds no sword, mace or fist weapon.
        Subtlety has Hemorrhage, which any weapon deals: its list keeps them."""
        for slot in ("main", "off"):
            kinds = {self.db.gear[entry.item_id]["kind"] for entry in self.ladder("ROGUE", 1, "pvp", slot)}
            self.assertEqual(kinds, {ladders.DAGGER}, slot)
        self.assertEqual(self.db.classes["ROGUE"]["specs"][1]["slug"], "assassination")
        others = {self.db.gear[entry.item_id]["kind"] for entry in self.ladder("ROGUE", 3, "pvp")}
        self.assertGreater(len(others), 1)

    def test_hand_of_justice_is_in_the_melee_pvp_lists(self):
        """Its 12 attack power left it out of every list ranked on the weights. Its extra attacks are what it is worn
        for (corrections/effects.json): there it stands level with the best picks, without a score, never the pick."""
        justice = 11815
        self.assertIn("Melee DPS", self.db.effects[justice])
        for token, data in self.db.classes.items():
            for spec, definition in data["specs"].items():
                with self.subTest(token=token, spec=definition["name"]):
                    ladder = self.ladder(token, spec, "pvp", "trinket")
                    entry = next((e for e in ladder if e.item_id == justice), None)
                    if definition["role"] == "Melee DPS" and definition["slug"] != "shockadin":
                        self.assertIsNotNone(entry)
                        self.assertTrue(entry.level and entry.unscored)
                        self.assertNotEqual(ladders.lead(ladder).item_id, justice)
                    else:
                        self.assertFalse(entry and entry.level)
        self.assertNotIn(justice, {e.item_id for e in self.ladder("MAGE", 2, "pvp", "trinket")})

    def test_valthalak_s_staff_has_its_spell_power(self):
        """ForeverDB gives Lord Valthalak's Staff of Command no spell power; the game's tooltip shows 72."""
        self.assertNotIn(45, self.published.gear[22335]["stats"])
        self.assertEqual(self.db.gear[22335]["stats"][45], 72)

    def test_a_hunter_s_attack_power_is_ranged_too(self):
        """An item's attack power is ranged attack power as well: a Hunter's weights count it at least as much
        (specs.ranged_power). ForeverDB's Marksmanship PvP weights gave it nothing, and Drake Fang Talisman's 56
        scored 0."""
        power, ranged, talisman = 38, 39, 19406
        for spec, data in self.db.classes["HUNTER"]["specs"].items():
            for profile, weights in data["weights"].items():
                if weights.get(ranged):
                    self.assertGreaterEqual(weights[power], weights[ranged], f"HUNTER {spec} {profile}")
                    self.assertEqual(self.db.specs.ranged["HUNTER", spec, profile], weights[power])
        self.assertNotIn(power, self.published.classes["HUNTER"]["specs"][2]["weights"]["pvp"])
        trinkets = [entry.item_id for entry in self.ladder("HUNTER", 2, "pvp", "trinket")]
        self.assertEqual(trinkets[0], talisman)

    def test_arms_pvp_compares_base_damage_per_mortal_strike(self):
        weapons = self.db.classes["WARRIOR"]["specs"][1]["weights"]
        hanna, reaper = 2801, 12784
        self.assertEqual(self.db.gear[hanna]["weapon_hit"], (96, 145, 2.0))
        self.assertEqual(self.db.gear[reaper]["weapon_hit"], (153, 256, 3.8))
        self.assertGreater(ladders.score(self.db, reaper, weapons["pvp"], "WARRIOR"),
                           ladders.score(self.db, hanna, weapons["pvp"], "WARRIOR"))
        self.assertNotIn("weapon_hit", weapons["raid"])
        self.assertNotIn("weapon_hit", self.db.classes["PALADIN"]["specs"][4]["weights"]["pvp"])

    def test_basin_mail_pauldrons_follow_the_wearers_faction(self):
        shoulders = ladders.full_ladder(self.db, "SHAMAN", 2, "pvp", "shoulder")
        matches = [entry for entry in shoulders if entry.item_id in (20056, 20203)]
        self.assertEqual([(entry.shown("a"), entry.shown("h")) for entry in matches], [(20056, 20203)])

    def test_bound_quest_and_honor_rewards_require_the_documented_source(self):
        self.assertEqual(self.db.items[272589]["side"], "h")
        self.assertEqual(self.db.items[272699]["side"], "a")
        self.assertEqual(self.db.items[279839]["side"], "a")
        both = copy.deepcopy(self.db.items[272699])
        both.update(side="", sources=both["sources"] + [["V", "12793", "0", "", "s"]])
        corrections.assign_reward_sides(types.SimpleNamespace(items={272699: both}))
        self.assertEqual(both["side"], "")

    def test_trueaim_hit_counts_for_shots(self):
        for spec, expected in ((1, 36), (2, 39), (3, 0)):
            weights = self.db.classes["HUNTER"]["specs"][spec]["weights"]["raid"]
            self.assertEqual(ladders.score(self.db, 13255, weights, "HUNTER"), expected)

    def shown(self, token, spec, slot="main", count=7):
        return [entry.item_id for entry in self.ladder(token, spec, slot=slot) if entry.passes(self.DEFAULT)][:count]

    # -- the weights ------------------------------------------------------------------------------

    def test_the_tanks_are_the_three_specs_expected(self):
        tanks = {(token, number) for token, data in self.published.classes.items()
                 for number, spec in data["specs"].items() if spec["role"] == specs.TANK}
        self.assertEqual(tanks, set(self.TANKS))

    def test_what_a_profile_lacks_comes_from_the_ones_it_has(self):
        warrior = {4: 0.4, 3: 0.5, 13: 1.0, "armor": 0.1}
        self.assertEqual(specs.complete(warrior, "WARRIOR"), {38: 0.2, "dps": 1.06}, "5.3 attack power a point")
        shielded = {**warrior, 48: 0.6}   # 0.05 block value a point of Strength comes off first
        self.assertEqual(specs.complete(shielded, "WARRIOR"), {38: 0.185, "dps": 0.98})
        paladin = {4: 0.4, 13: 0.9, "armor": 0.1, 45: 0.6}
        self.assertEqual(specs.complete(paladin, "PALADIN"),
                         {38: 0.2, "dps": 2.8, 42: 0.6, 3: round(0.9 * 12 * 0.0506 + 0.2, 3)}, "a white swing's 14")
        bear = {4: 0.5, 38: 0.3, 3: 0.9}
        self.assertEqual(specs.complete(bear, "DRUID"), {"dps": 4.2}, "the attack power it gives is the one that counts")
        self.assertEqual(self.db.classes["PALADIN"]["specs"][2]["weights"]["raid"][42], 0.6, "spell damage as spell power")

    def test_a_weight_foreverdb_gives_is_never_changed(self):
        self.assertEqual(specs.complete({4: 0.6, 38: 0.3, 3: 0.6, "dps": 3.0}, "WARRIOR"), {})
        self.assertEqual(specs.complete({7: 1.0, 12: 1.5}, "WARRIOR"), {}, "nothing to read a weapon's damage from")
        for token, number in self.TANKS:
            for profile, weights in self.published.classes[token]["specs"][number]["weights"].items():
                mine = self.db.classes[token]["specs"][number]["weights"][profile]
                self.assertEqual({stat: mine[stat] for stat in weights}, weights, f"{token} {number} {profile}")

    def test_every_tank_weighs_a_weapons_damage(self):
        for token, number in self.TANKS:
            for profile, weights in self.db.classes[token]["specs"][number]["weights"].items():
                self.assertGreater(weights.get("dps", 0), 0, f"{token} {number} {profile}")
                self.assertGreater(weights.get(38, 0), 0, f"{token} {number} {profile}: attack power")
                self.assertGreater(weights.get(3, 0), 0, f"{token} {number} {profile}: agility")

    def test_no_other_spec_is_touched(self):
        for token, data in self.published.classes.items():
            for number, spec in data["specs"].items():
                if (token, number) not in self.TANKS:
                    expected = copy.deepcopy(spec["weights"])
                    if token == "WARRIOR" and number == 1:
                        expected["pvp"]["weapon_hit"] = expected["pvp"]["dps"] / (6 + 3.3)
                    if token == "HUNTER":   # its attack power is ranged attack power too (specs.ranged_power)
                        for weights in expected.values():
                            if spec["role"] == "Ranged DPS" and 31 in weights:
                                weights["ranged_hit"] = 10 * weights[31]
                            if weights.get(39):
                                weights[38] = round(weights.get(38, 0) + weights[39], 3)
                    if specs.ATTACK_POWER in expected["pvp"]:
                        expected["pvp"].setdefault(specs.HUMANOID_ATTACK_POWER, expected["pvp"][specs.ATTACK_POWER])
                    self.assertEqual(self.db.classes[token]["specs"][number]["weights"], expected,
                                     f"{token} {spec['name']}")

    # -- what the user saw: caster weapons among a Protection Warrior's main hands ------------------

    def test_a_weapon_is_ranked_on_its_damage_too(self):
        """A caster's blade has the stamina and the hit of a tank's weapon and two thirds of its damage."""
        db = copy.deepcopy(self.db)
        token, number = "WARRIOR", 3
        blade, mace = 900001, 900002
        for item_id, stats, dps in ((blade, {7: 14, 31: 10, 45: 94}, 31.1), (mace, {7: 12, 31: 10}, 47.4)):
            db.gear[item_id] = {"inv": 21, "kind": "2.7", "req": 60, "stats": stats, "dps": dps, "armor": 0.0, "wand": False}
            db.items[item_id] = {"name": f"Test {item_id}", "groups": frozenset("d"), "flags": "", "side": "",
                                 "twin": None, "limit": None, "sources": [["d", "1", "Boss", "10", "", "s"]]}
        db.classes[token]["pools"]["mh"] = [(blade, 60), (mace, 60)]
        db.classes[token]["pools"]["2h"] = []
        self.assertEqual([entry.item_id for entry in self.ladder(token, number, db=db)], [mace, blade])
        published = copy.deepcopy(db)
        published.classes[token]["specs"][number]["weights"] = copy.deepcopy(
            self.published.classes[token]["specs"][number]["weights"])
        self.assertEqual([entry.item_id for entry in self.ladder(token, number, db=published)], [blade, mace],
                         "on ForeverDB's weights alone the blade's two more stamina win: the cause")

    def test_no_caster_weapon_among_the_warriors_and_the_bears_main_hands(self):
        """Neither spec has any use for spell power: none of the weapons it shows carries some."""
        power = set(ladders.SPELL_DAMAGE) | {ladders.HEALING}
        for token, number in (("WARRIOR", 3), ("DRUID", 2)):
            for item_id in self.shown(token, number):
                stats = self.db.gear[item_id]["stats"]
                self.assertFalse(power & set(stats), f"{token}: {self.db.items[item_id]['name']} {stats}")
        everything = self.shown("WARRIOR", 3, count=1 + ladders.MAX_ALTERNATIVES)   # all a player can ask for
        self.assertNotIn(self.SAGEBLADE, everything)
        self.assertNotIn(self.MASTERSMITHS_HAMMER, everything)
        published = copy.copy(self.db)
        published.classes = copy.deepcopy(self.db.classes)
        published.classes["WARRIOR"]["specs"][3]["weights"] = copy.deepcopy(
            self.published.classes["WARRIOR"]["specs"][3]["weights"])
        before = [entry.item_id for entry in self.ladder("WARRIOR", 3, db=published) if entry.passes(self.DEFAULT)][:7]
        self.assertIn(self.SAGEBLADE, before, "what the user saw, on ForeverDB's weights alone")
        self.assertIn(self.MASTERSMITHS_HAMMER, before)

    def test_of_two_weapons_alike_every_tank_takes_the_one_that_hits_harder(self):
        """The cause, for the three of them: on ForeverDB's PvE weights a weapon's damage counted for nothing."""
        light, heavy = 900003, 900004
        for token, number in self.TANKS:
            db = copy.deepcopy(self.db)
            for item_id, dps in ((light, 30.0), (heavy, 50.0)):
                db.gear[item_id] = {"inv": 17, "kind": "2.5", "req": 60, "stats": {7: 10}, "dps": dps, "armor": 0.0,
                                    "wand": False}
                db.items[item_id] = {"name": f"Test {item_id}", "groups": frozenset("d"), "flags": "", "side": "",
                                     "twin": None, "limit": None, "sources": [["d", "1", "Boss", "10", "", "s"]]}
            db.classes[token]["specs"][number]["style"] = "any"
            db.classes[token]["pools"]["mh"], db.classes[token]["pools"]["2h"] = [], [(light, 60), (heavy, 60)]
            ranked = self.ladder(token, number, db=db)
            self.assertEqual([entry.item_id for entry in ranked], [heavy, light], token)
            self.assertGreater(ranked[0].score, ranked[1].score, token)
            db.classes[token]["specs"][number]["weights"] = copy.deepcopy(
                self.published.classes[token]["specs"][number]["weights"])
            tied = self.ladder(token, number, db=db)
            self.assertEqual(tied[0].score, tied[1].score, f"{token}: equals on ForeverDB's weights")

    def test_applying_twice_adds_nothing(self):
        db = copy.deepcopy(self.db)
        again = specs.apply(db)
        self.assertEqual(sorted(db.classes["DRUID"]["specs"]), [1, 2, 3, 4])
        self.assertEqual(specs.order(db, "DRUID"), [1, 4, 2, 3])
        self.assertEqual((again.completed, again.unbound, again.cat), ({}, {}, None))
        for token, data in self.db.classes.items():
            for number, spec in data["specs"].items():
                self.assertEqual(db.classes[token]["specs"][number]["weights"], spec["weights"], f"{token} {number}")

    # -- an item whose effect the weights cannot count ---------------------------------------------

    LION_HORN, INSIGNIA, STABILIZER = 14557, 17904, 272440
    MARK_OF_TYRANNY, ARENA_GRAND_MASTER, QUEL_SERRAR, FORCE_REACTIVE_DISK = 13966, 19024, 18348, 18168
    HAND_OF_JUSTICE = 11815   # a melee damage dealer's, where the others are a tank's

    def test_an_item_worth_its_effect_has_no_score_and_stands_with_the_best(self):
        """The Lion Horn of Stormwind: 8 defense, half of the best trinket's score, and an armor proc worth nothing."""
        tank = frozenset({"Tank"})
        self.assertEqual(self.db.effects, {self.LION_HORN: tank, self.MARK_OF_TYRANNY: tank, self.ARENA_GRAND_MASTER: tank,
                                           self.QUEL_SERRAR: tank, self.FORCE_REACTIVE_DISK: tank,
                                           self.HAND_OF_JUSTICE: frozenset({"Melee DPS"})})
        trinkets = {self.LION_HORN, self.MARK_OF_TYRANNY, self.ARENA_GRAND_MASTER}
        for token, number in self.TANKS:
            for mode in ladders.MODES:
                ladder = self.ladder(token, number, mode, "trinket")
                level = [entry for entry in ladder if entry.level]
                expected = {self.ARENA_GRAND_MASTER} if mode == "pve" else trinkets
                self.assertEqual({entry.item_id for entry in level}, expected, f"{token} {mode}")
                self.assertEqual(ladder[:len(level)], level, "at the head of the ladder")
                first = ladder[len(level)]
                for entry in level:
                    self.assertTrue(entry.unscored)
                    self.assertEqual(entry.score, first.score, "a stand-in: the ladder stays in order")
                    self.assertIn(":x", luaout.encode_entry(entry))
                self.assertIs(ladders.lead(ladder), first, "never a best pick")
        for token, number in self.TANKS:
            pool = self.ladder(token, number, "pve", "trinket")
            for side in ("a", "h"):
                visible = [entry for entry in pool if entry.passes((side, False, False, 0, False, 6))]
                best, _ = ladders.picks("trinket", visible)
                self.assertEqual([entry.shown(side) for entry in best], [self.LION_HORN, self.STABILIZER])
                scores = {entry.item_id: entry.stored for entry in visible}
                self.assertGreater(scores[self.MARK_OF_TYRANNY], scores[4130])
        for slot, item_id in (("main", self.QUEL_SERRAR), ("off", self.FORCE_REACTIVE_DISK)):
            for token, number in (("PALADIN", 2), ("WARRIOR", 3)):
                ladder = self.ladder(token, number, "pve", slot)
                self.assertEqual([entry.item_id for entry in ladder if entry.level], [item_id], f"{token} {slot}")
                self.assertIs(ladder[0].level, True)
        visible = [entry for entry in self.ladder("PALADIN", 2, slot="trinket") if entry.passes(self.DEFAULT)]
        best, alternatives = ladders.picks("trinket", visible)
        self.assertEqual([entry.item_id for entry in best], [self.LION_HORN, self.STABILIZER])
        self.assertNotIn(self.INSIGNIA, [entry.item_id for entry in visible], "Alterac Valley rewards are hidden")
        self.assertEqual(alternatives[0].item_id, self.ARENA_GRAND_MASTER)
        _, more = ladders.picks("trinket", visible, ladders.MAX_ALTERNATIVES)
        self.assertIn(self.MARK_OF_TYRANNY, [entry.item_id for entry in more])
        by_id = {entry.item_id: entry for entry in visible}
        self.assertGreater(by_id[self.MARK_OF_TYRANNY].stored, by_id[4130].stored)
        self.assertFalse(by_id[self.MARK_OF_TYRANNY].unscored)
        kept = ladders.kept_ladder("trinket", self.ladder("PALADIN", 2, slot="trinket"))
        self.assertIn(self.LION_HORN, [entry.item_id for entry in kept])

    def test_only_a_weights_list_of_that_role_does_so(self):
        for token, number in (("DRUID", 4), ("WARRIOR", 2), ("PALADIN", 1)):   # the cat, Fury (simulated), Holy
            for mode in ladders.MODES:
                ladder = self.ladder(token, number, mode, "trinket")
                self.assertFalse([entry for entry in ladder if entry.level and entry.item_id != self.HAND_OF_JUSTICE],
                                 f"{token} {number} {mode}")
        self.assertEqual(specs.unvalued(self.db, "WARRIOR", 3), frozenset(self.db.effects) - {self.HAND_OF_JUSTICE})
        self.assertEqual(specs.unvalued(self.db, "WARRIOR", 2), frozenset({self.HAND_OF_JUSTICE}))
        entries = self.ladder("WARRIOR", 3, slot="neck")
        self.assertIs(ladders.level_with_the_best(entries, frozenset({self.LION_HORN})), entries, "not in that slot")

    # -- the Feral Druid ----------------------------------------------------------------------------

    def test_the_feral_druid_is_a_bear_and_a_cat(self):
        druid = self.db.classes["DRUID"]
        self.assertEqual(self.db.specs.bear, ("DRUID", 2))
        self.assertEqual(self.db.specs.cat, ("DRUID", 4))
        self.assertEqual({number: (spec["name"], spec["role"]) for number, spec in druid["specs"].items()},
                         {1: ("Balance", "Caster DPS"), 2: ("Feral (Bear)", "Tank"), 3: ("Restoration", "Healer"),
                          4: ("Feral (Cat)", "Melee DPS")})
        self.assertEqual(specs.order(self.db, "DRUID"), [1, 4, 2, 3], "the two Feral specs stand together")
        self.assertEqual(specs.order(self.db, "WARRIOR"), [1, 2, 3])
        self.assertEqual(self.published.classes["DRUID"]["specs"][2]["name"], "Feral Combat")

    def test_the_cat_is_ranked_on_damage_and_the_bear_on_survival(self):
        cat, bear = (self.db.classes["DRUID"]["specs"][number]["weights"]["raid"] for number in (4, 2))
        self.assertEqual(cat, specs.CAT_PVE)
        for stat in (7, 12, 13, "armor"):   # stamina, defense, dodge, armor
            self.assertNotIn(stat, cat)
            self.assertGreater(bear[stat], 0)
        self.assertGreater(cat["dps"], 0)
        differ = [slot for slot, _ in ladders.SLOTS
                  if self.shown("DRUID", 4, slot) != self.shown("DRUID", 2, slot)]
        self.assertGreaterEqual(len(differ), 11, "the two lists are not the same list twice")

    def test_the_cats_pvp_list_is_the_bears(self):
        druid = self.db.classes["DRUID"]["specs"]
        self.assertEqual(druid[4]["weights"]["pvp"], druid[2]["weights"]["pvp"])
        for slot, _ in ladders.SLOTS:
            scored = lambda number: sorted((-entry.score, entry.item_id) for entry in
                                           self.ladder("DRUID", number, "pvp", slot) if entry.item_id not in self.db.effects)
            self.assertEqual(scored(4), scored(2), f"{slot}: but for what only a tank stands level with the best")

    def test_a_feral_spec_foreverdb_changed_is_left_alone(self):
        db = copy.deepcopy(self.published)
        db.classes["DRUID"]["specs"][2]["role"] = "Melee DPS"
        report = specs.apply(db)
        self.assertIsNone(report.cat)
        self.assertEqual(sorted(db.classes["DRUID"]["specs"]), [1, 2, 3])

    # -- the cat's enchants -------------------------------------------------------------------------

    def test_an_enchants_sentence_gives_its_stats(self):
        self.assertEqual(specs.enchant_stats("Agility +15"), {3: 15})
        self.assertEqual(specs.enchant_stats("+9 Agility"), {3: 9})
        self.assertEqual(specs.enchant_stats("Attack Power +28/Dodge +1%"), {38: 28, 13: 12})
        self.assertEqual(specs.enchant_stats("Attack Power +26 and +1% Critical Strike"), {38: 26, 32: 14})
        self.assertEqual(specs.enchant_stats("All Stats +4"), {4: 4, 3: 4, 7: 4, 5: 4, 6: 4})
        self.assertEqual(specs.enchant_stats("Stamina +5 and Armor +40"), {7: 5, "armor": 40})
        for unknown in ("Crusader", "Living Stats", "Weapon Damage +5", "Counterweight +3% Attack Speed",
                        "Attack Speed +1%", ""):
            self.assertIsNone(specs.enchant_stats(unknown), unknown)
        self.assertEqual(specs.enchant_stats("Healing Spells +55"), {41: 55})   # read since the Shockadin's enchants

    def test_the_cats_enchants_are_for_damage(self):
        cat = self.db.enchants["DRUID"][(4, "raid")]
        effect = lambda enchant: self.db.enchant_info[enchant][1]
        self.assertEqual(effect(cat["w2h"][0][0]), "Agility +25")
        self.assertEqual(effect(cat["hands"][0][0]), "Agility +15")
        self.assertEqual(effect(cat["head"][0][0]), "Agility +8", "not the Rogue's Death's Embrace")
        for key, entries in cat.items():
            for enchant, _ in entries:
                stats = specs.enchant_stats(effect(enchant))
                self.assertTrue(set(stats) & set(specs.CAT_PVE), f"{key}: {effect(enchant)}")
        bear, was = self.db.enchants["DRUID"][(2, "raid")], self.published.enchants["DRUID"][(2, "raid")]
        self.assertEqual(bear, {key: [pair for pair in entries if pair[0] not in specs.CLASS_ENCHANTS]
                                for key, entries in was.items()}, "the bear keeps ForeverDB's, but another class's")
        self.assertEqual(effect(bear["wrist"][0][0]), "Defense +9")

    def test_a_tank_is_listed_its_own_class_enchant_only(self):
        """ForeverDB gives the Rogue's Death's Embrace to the bear and the Warrior's Presence of Might to the Paladin."""
        self.assertIn("i19784", {enchant for enchant, _ in self.published.enchants["DRUID"][(2, "raid")]["head"]})
        self.assertIn("i19782", {enchant for enchant, _ in self.published.enchants["PALADIN"][(2, "raid")]["head"]})
        for token, number in (*self.TANKS, ("DRUID", 4)):
            for profile in ("lvl", "raid"):
                for key, entries in self.db.enchants[token][(number, profile)].items():
                    for enchant, _ in entries:
                        self.assertEqual(specs.CLASS_ENCHANTS.get(enchant, token), token, f"{token} {number} {key}")
        self.assertIn("i19782", {enchant for enchant, _ in self.db.enchants["WARRIOR"][(3, "raid")]["head"]}, "its own")
        self.assertEqual(self.db.specs.unbound, {("DRUID", 2): {"i19784"}, ("PALADIN", 2): {"i19782"}})
        for token, per_spec in self.published.enchants.items():   # the other specs: as ForeverDB has them
            for key, per_slot in per_spec.items():
                if (token, key[0]) not in self.TANKS:
                    self.assertEqual(self.db.enchants[token][key], per_slot, f"{token} {key}")

    # -- the data file ------------------------------------------------------------------------------

    def test_the_lists_file_names_the_specs_in_the_order_to_show_them(self):
        kept = {token: {number: {mode: {slot: [] for slot, _ in ladders.SLOTS} for mode in ladders.MODES}
                        for number in data["specs"]} for token, data in self.db.classes.items()}
        text = luaout.lists_file(self.db, kept)
        druid = text.split("DRUID = [==[\n", 1)[1].split("]==]", 1)[0]
        self.assertEqual([line.split("\t")[1:4] for line in druid.splitlines() if line.startswith("S\t")],
                         [["1", "Balance", "Caster DPS"], ["4", "Feral (Cat)", "Melee DPS"],
                          ["2", "Feral (Bear)", "Tank"], ["3", "Restoration", "Healer"]])
        self.assertIn("Added to ForeverDB's specs: Feral (Cat) Druid", text)
        self.assertIn("Changed from ForeverDB's weights: the tanks (Feral (Bear) Druid, Protection Paladin, "
                      "Protection Warrior)", text)
        self.assertIn(specs.CAT_SOURCE, text)


class HoleTest(unittest.TestCase):
    def shown(self, db, phase=phases.PRE_RAID):
        rows = audit.shown_rows(ladders.build_all(db)["PRIEST"][1]["pve"], ("a", False, False, phase))
        return [entry.item_id for entry in rows["main"][0] + rows["main"][1]]

    def test_the_audit_shows_a_hole(self):
        db = tiny_db()
        self.assertEqual(self.shown(db), [SCEPTER, MACE, ROD], "the level 28 scepter comes out first, as in the data")
        findings = audit.run(db, ladders.build_all(db))
        found = {(f.kind, f.slot, f.item_id): f for f in findings if f.mode == "pve"}
        low = found[(audit.LOW, "main", SCEPTER)]
        self.assertTrue(low.best)
        self.assertIn("requires level 28", low.line())
        self.assertEqual(low.phases, phases.PHASES)
        self.assertIn((audit.POWERLESS, "main", MACE), found)
        self.assertIn((audit.POWERLESS, "main", ROD), found)
        self.assertIn((audit.LONELY, "main", SCEPTER), found)
        self.assertNotIn((audit.POWERLESS, "off", ORB), found, "an orb is not a weapon, and this one has healing")
        self.assertNotIn((audit.POWERLESS, "ranged", WAND), found)
        self.assertEqual({f.item_id for f in audit.suspicious(findings)}, {SCEPTER, MACE, ROD})
        self.assertIn("low level", audit.summary(findings))
        # a weapon read in the game that shows no spell power there either is not a hole
        confirmed = audit.run(db, ladders.build_all(db), read_in_game=frozenset({MACE}))
        self.assertNotIn(MACE, {f.item_id for f in confirmed if f.kind == audit.POWERLESS})

    def test_corrections_fill_the_hole(self):
        db = tiny_db()
        report = corrections.apply(db, IN_THE_GAME)
        self.assertIs(db.corrected, report)
        self.assertEqual(report.filled, [MACE, ROD])
        self.assertEqual(db.gear[MACE]["stats"], {5: 13, 45: 90}, "equal healing and damage are one spell power stat")
        self.assertEqual(db.gear[ROD]["stats"], {5: 5, 41: 124, 42: 41})
        self.assertEqual(report.dps, [SCEPTER, MACE, ROD], "a caster weapon's damage per second is the game's")
        self.assertEqual(db.gear[MACE]["dps"], 29.69)
        self.assertEqual(report.agree, 1, "the scepter's healing was right in the data")
        self.assertEqual(report.builds, {"1.0.0.1"})
        self.assertEqual(self.shown(db), [ROD, MACE, SCEPTER], "the scepter is now behind the level 54 and 57 weapons")
        findings = audit.run(db, ladders.build_all(db), read_in_game=frozenset(IN_THE_GAME))
        self.assertEqual([f for f in audit.suspicious(findings) if f.slot == "main" and f.item_id != STAFF], [])

    def test_corrections_only_fill_holes(self):
        db = tiny_db()
        before = copy.deepcopy(db.gear)
        self.assertEqual(corrections.apply(db, {}).changed, set())
        self.assertEqual(db.gear, before)

        seen = {
            SCEPTER: {"healing": 99, "damage": 0, "dps": 20.0, "build": "1.0.0.0"},   # read before the data's build
            MACE: {"healing": 0, "damage": 0, "dps": 29.69},       # the game shows no spell power: nothing to add
            ORB: {"healing": 50, "damage": 50, "dps": 0},          # not a weapon
            404: {"healing": 10, "damage": 10, "dps": 5.0},        # not in the data
        }
        report = corrections.apply(db, seen)
        self.assertEqual(db.gear, before)
        self.assertEqual(report.differ, [(SCEPTER, (99, 0), (68, 0))])
        self.assertEqual(report.unknown, [ORB, 404])
        self.assertEqual((report.filled, report.dps, report.agree), ([], [], 0))
        self.assertEqual(corrections.power_stats(0, 12), {42: 12})
        self.assertEqual(corrections.power_stats(0, 0), {})

    def test_the_game_wins_at_its_own_build(self):
        """A value the data has, and that the game showed otherwise: the later of the two is the one to trust."""
        for build, replaced in (("1.0.0.1", True), ("1.0.1.0", True), ("1.0.0.0", False), ("", False)):
            db = tiny_db()
            db.gear[MACE]["stats"] = {5: 13, 45: 25}   # as Classic had it; the game shows 99
            report = corrections.apply(db, {MACE: {"healing": 99, "damage": 99, "dps": 0, "build": build}})
            if replaced:
                self.assertEqual((report.replaced, report.differ), ([MACE], []), build)
                self.assertEqual(db.gear[MACE]["stats"], {5: 13, 45: 99})
                self.assertIn(MACE, report.changed)
            else:
                self.assertEqual((report.replaced, report.differ), ([], [(MACE, (99, 99), (25, 25))]), build)
                self.assertEqual(db.gear[MACE]["stats"], {5: 13, 45: 25})
        # the damage per second too, for a weapon with no spell power at all, in either direction
        for build, data, expected in (("1.0.0.1", 49.6, 36.79), ("1.0.0.1", 30.0, 36.79), ("1.0.0.1", 36.8, 36.8),
                                      ("1.0.0.0", 49.6, 49.6)):
            db = tiny_db()
            db.gear[STAFF]["dps"] = data
            report = corrections.apply(db, {STAFF: {"healing": 0, "damage": 0, "dps": 36.79, "build": build}})
            self.assertEqual(db.gear[STAFF]["dps"], expected, (build, data))
            self.assertEqual(report.dps, [STAFF] if expected != data else [])
        db = tiny_db()
        db.gear[ROD]["stats"] = {5: 5, 45: 41, 41: 83}   # healing 124 and damage 41, written the other way
        report = corrections.apply(db, {ROD: {"healing": 124, "damage": 41, "dps": 0, "build": "1.0.0.1"}})
        self.assertEqual((report.agree, report.replaced), (1, []))

    def test_corrections_are_kept_in_a_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sub" / "weapons.json"
            self.assertEqual(corrections.load(path), {})
            corrections.save(IN_THE_GAME, path)
            self.assertEqual(corrections.load(path), IN_THE_GAME)
            text = path.read_bytes()
            self.assertNotIn(b"\r", text)
            self.assertEqual(text.count(b"\n"), len(IN_THE_GAME) + 5, "one weapon per line")
            self.assertLess(text.index(b'"1":'), text.index(b'"2":'))

    def test_the_lists_say_what_was_corrected(self):
        db = tiny_db()
        plain = luaout.lists_file(db, ladders.build_all(db))
        self.assertNotIn("Changed from ForeverDB's data", plain)
        corrections.apply(db, IN_THE_GAME)
        text = luaout.lists_file(db, ladders.build_all(db))
        self.assertTrue(text.startswith(fdb.HEADER_PREFIX))
        self.assertIn("-- Changed from ForeverDB's data: 3 caster weapons", text)
        self.assertIn("build 1.0.0.1", text)

    # -- the capture ---------------------------------------------------------------------------

    def test_the_tool_is_installed_with_its_list(self):
        db = tiny_db()
        self.assertEqual(capture.weapon_ids(db), [SCEPTER, MACE, ROD, STAFF])
        db.gear[ROBE] = {"inv": 20, "req": 60, "stats": {7: 20}, "dps": 0.0, "armor": 0.0, "wand": False}
        db.gear[404] = dict(db.gear[ROBE], req=30)   # left out of the lists, and of too low a level to matter
        self.assertEqual(capture.capture_ids(db), {"weapons": [SCEPTER, MACE, ROD, STAFF], "pool": [WAND, ORB],
                                                   "unlisted": [ROBE], "twins": [], "consumables": []})
        with tempfile.TemporaryDirectory() as folder:
            target, counts = capture.write_tool(db, folder)
            self.assertEqual((target.name, counts), ("EasyBIS_Capture", {"weapons": 4, "pool": 2, "unlisted": 1, "twins": 0,
                                                                  "consumables": 0}))
            self.assertEqual(sorted(path.name for path in target.iterdir()),
                             ["Capture.lua", "EasyBIS_Capture.toc", "Ids.lua"])
            # the pieces of the lists first, then the weapons; the raid piece left out of the lists last: the server
            # does not answer for an item it lacks, and the capture stops on a long silence
            self.assertIn("\n8 9 1 2 3 7 20\n", (target / "Ids.lua").read_text(encoding="utf-8"))
            listed = [line for line in (target / "EasyBIS_Capture.toc").read_text(encoding="utf-8").splitlines()
                      if line and not line.startswith("#")]
            self.assertEqual(listed, ["Ids.lua", "Capture.lua"])
            for path in target.iterdir():
                self.assertNotIn(b"\r", path.read_bytes(), path.name)

    def test_the_saved_capture_is_the_newest_that_holds_one(self):
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder)
            self.assertIsNone(capture.find_saved(game))
            written = {}
            for age, (account, text) in enumerate((
                    ("C", "\nEasyBISCaptureDB = nil\n"),    # an account that logged in and read nothing
                    ("B", '\nEasyBISCaptureDB = {\n["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",\n}\n'),
                    ("A", '\nEasyBISCaptureDB = {\n["meta"] = "1|1.0.0|1|enUS|2026-11-14 09:00",\n}\n'))):
                path = game / "WTF" / "Account" / account / "SavedVariables" / "EasyBIS_Capture.lua"
                path.parent.mkdir(parents=True)
                path.write_text(text, encoding="utf-8")
                os.utime(path, (1_800_000_000 - age * 60, 1_800_000_000 - age * 60))
                written[account] = path
            self.assertEqual(capture.find_saved(game), written["B"])
            written["A"].unlink()
            written["B"].unlink()
            self.assertEqual(capture.find_saved(game), written["C"], "an empty one is still named, to say so")

    def test_a_saved_capture_is_understood(self):
        text = "\n".join([
            "", "EasyBISCaptureDB = {", '["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",', '["missing"] = "7 404",',
            '["items"] = {',
            r'[2] = "|cffa335eeOdd Mace|r\nBinds when equipped\nOne-Hand\tMace\n33 - 62 Damage\tSpeed 1.60\n'
            r'(29.69 damage per second)\n+13 Intellect\nEquip: Increases damage and healing done by magical spells '
            r'and effects by up to 90.\nChance on hit: a \"quoted\" word.\n#stats ITEM_MOD_INTELLECT_SHORT=13",',
            r'[3] = "Lively Rod\nMain Hand\tMace\n(25.87 damage per second)\nEquip: Increases healing done by up to 124 '
            r'and damage done by up to 41 for all magical spells and effects.\n(2) Set : Increases damage and healing '
            r'done by magical spells and effects by up to 23.\n#stats ",',
            r'[1] = "Low Scepter\n(14.29 damage per second)\nEquip: Increases healing done by magical spells and '
            r'effects by up to 68.\nEquip: Increases damage done by Shadow spells and effects by up to 28.\n'
            r'Equip: Increases healing done by Holy Light by up to 30.\n#stats ",',
            r'[9] = "Glowing Orb\nHeld In Off-hand\n#stats ",',
            "},", "}", ""])
        parsed = capture.parse_saved(text)
        self.assertEqual((parsed["game"], parsed["locale"], parsed["date"]), ("1.0.0.1", "enUS", "2026-11-15"))
        self.assertEqual(parsed["missing"], [7, 404])
        self.assertEqual(parsed["items"][2][0][0], "Odd Mace", "the colour of the name is left out")
        self.assertEqual(parsed["items"][2][1], {"ITEM_MOD_INTELLECT_SHORT": 13.0})

        result = capture.read_capture(tiny_db(), text)
        self.assertEqual((result.read, result.weapons, result.with_power, result.missing), (4, 3, 3, 2))
        seen = result.observations
        self.assertEqual(seen[MACE], IN_THE_GAME[MACE])
        self.assertEqual((seen[ROD]["healing"], seen[ROD]["damage"]), (124, 41), "a set bonus is not the item's")
        self.assertEqual((seen[SCEPTER]["healing"], seen[SCEPTER]["damage"]), (68, 0), "one school is not all of them")
        self.assertEqual(dict(result.unread), {"Equip: Increases healing done by Holy Light by up to N.": 1})
        self.assertEqual(result.other_names, [])
        self.assertNotIn(ORB, seen)

        with self.assertRaises(ValueError):
            capture.parse_saved("EasyBISCaptureDB = nil\n")
        with self.assertRaises(ValueError):
            capture.parse_saved(text.replace('"1|1.0.0', '"2|1.0.0'))

    def test_the_game_is_compared_with_the_data_stat_by_stat(self):
        text = "\n".join([
            "EasyBISCaptureDB = {", '["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",', '["missing"] = "3 7",',
            '["absent"] = "7",', '["sample"] = "1:0",', '["log"] = "12:30 10:4:5:0:0 20:5:6:1:0",',
            '["items"] = {',
            r'[2] = "Odd Mace\nOne-Hand\tMace\n#stats ITEM_MOD_DAMAGE_PER_SECOND_SHORT=29.6875;'
            r'ITEM_MOD_INTELLECT_SHORT=13;ITEM_MOD_SPELL_POWER_SHORT=90;ITEM_MOD_STRANGE_SHORT=4",',
            r'[1] = "Low Scepter\nMain Hand\tMace\n#stats ITEM_MOD_DAMAGE_PER_SECOND_SHORT=21.4;'
            r'ITEM_MOD_SPELL_HEALING_DONE_SHORT=68;ITEM_MOD_HEALTH_REGEN_SHORT=12",',
            r'[9] = "Glowing Orb\nHeld In Off-hand\n#stats ITEM_MOD_SPELL_HEALING_DONE_SHORT=22;'
            r'ITEM_MOD_FIRE_RESISTANCE_SHORT=5;RESISTANCE2_NAME=5",',
            r'[8] = "Thin Wand\nRanged\tWand\n#stats ",',   # no stat table: not compared
            r'[20] = "Robe of Tests\nBinds when picked up\nChest\tCloth\n120 Armor\n+20 Stamina\nClasses: Priest, Mage\n'
            r'Requires Level 60\n\nVestments of Tests (0/8)\n  Crown of Tests\n#stats ITEM_MOD_STAMINA_SHORT=20;'
            r'RESISTANCE0_NAME=120",',
            "},", "}", ""])
        db = tiny_db()
        db.gear[ROBE] = {"inv": 20, "req": 60, "stats": {7: 20}, "dps": 0.0, "armor": 120.0, "wand": False}
        check = capture.check_capture(db, text)
        self.assertEqual(check.asked, {"weapons": 4, "pool": 2, "unlisted": 1, "twins": 0, "consumables": 0})
        self.assertEqual(check.read, {"weapons": 2, "pool": 2, "unlisted": 1, "twins": 0, "consumables": 0})
        # the staff is not in the game's own item table: it was not asked for, and the report names it
        self.assertEqual(check.absent, {"weapons": [(STAFF, "Channeling Staff")], "pool": [], "unlisted": [], "twins": [],
                                        "consumables": []})
        self.assertEqual(check.sample, (1, 0))
        report = "\n".join(build.check_report(check))
        self.assertIn("Not in the game's own item table, so not asked for: 1 weapons. Of 1 of them asked for all "
                      "the same, 0 answered.\n  weapons: Channeling Staff (7)\n", report)
        self.assertEqual(check.compared, 4)
        self.assertEqual(dict(check.families["healing"]), {"missing": 1, "same": 1, "differs": 1})
        self.assertEqual(check.examples[("healing", "missing")], [(MACE, "Odd Mace", 90, 0)])
        self.assertEqual(check.examples[("healing", "differs")], [(ORB, "Glowing Orb", 22, 20)])
        self.assertEqual(dict(check.families["spell damage"]), {"missing": 1})
        self.assertEqual(dict(check.families["damage per second"]), {"differs": 1, "same": 1})
        self.assertEqual(dict(check.families["intellect"]), {"same": 1})
        self.assertEqual(dict(check.families["health per 5 sec"]), {"missing": 1})
        self.assertEqual(dict(check.families["fire resistance"]), {"missing": 1}, "counted once, though under two keys")
        self.assertEqual(dict(check.families["stamina"]), {"same": 1})
        self.assertEqual(dict(check.families["armor"]), {"same": 1})
        self.assertEqual(check.problems("healing"), 2)
        self.assertEqual(dict(check.other_keys), {"ITEM_MOD_STRANGE_SHORT": 1})
        self.assertEqual(check.unlisted, {ROBE: {"name": "Robe of Tests", "slot": "Chest", "kind": "Cloth",
                                                 "classes": ["Priest", "Mage"], "set": "Vestments of Tests",
                                                 "req": 60, "unique": False, "limit": None}})
        # with the corrections in use, the mace's hole is filled: only what is left shows
        corrections.apply(db, IN_THE_GAME)
        fixed = capture.check_capture(db, text)
        self.assertEqual(dict(fixed.families["spell damage"]), {"same": 1})
        self.assertEqual(dict(fixed.families["damage per second"]), {"same": 1, "differs": 1})

    def test_another_language_falls_back_on_the_stat_table(self):
        lines = ["Masse étrange", "(29.69 dégâts par seconde)", "Équipé : Augmente les dégâts et les soins."]
        french, unread = capture.observe(lines, {"ITEM_MOD_SPELL_POWER_SHORT": 90.0, "ITEM_MOD_DAMAGE_PER_SECOND_SHORT": 29.69},
                                         "frFR")
        self.assertEqual((french["healing"], french["damage"], french["dps"], unread), (90, 90, 29.69, []))
        self.assertEqual(french["from"], "stats")
        # in English too, when the tooltip has no line the generator knows: the line is reported, the table used
        english, unread = capture.observe(["Odd Mace", "+90 Spell Power"], {"ITEM_MOD_SPELL_POWER_SHORT": 90.0}, "enUS")
        self.assertEqual((english["healing"], english["damage"], english["from"]), (90, 90, "stats"))
        self.assertEqual(unread, ["+N Spell Power"])
        plain, unread = capture.observe(["Odd Mace", "+13 Intellect"], {"ITEM_MOD_INTELLECT_SHORT": 13.0}, "enUS")
        self.assertEqual((plain["healing"], plain["damage"], plain["from"], unread), (0, 0, "tooltip", []))
        split, _ = capture.observe(lines, {"ITEM_MOD_SPELL_HEALING_DONE_SHORT": 124.0,
                                           "ITEM_MOD_SPELL_DAMAGE_DONE_SHORT": 41.0}, "frFR")
        self.assertEqual((split["healing"], split["damage"]), (124, 41))

    def test_an_import_merges_and_refuses_an_empty_capture(self):
        def capture_of(*rows):
            return "\n".join(["EasyBISCaptureDB = {", '["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",',
                              '["missing"] = "",', '["items"] = {', *rows, "},", "}", ""])
        mace = (r'[2] = "Odd Mace\n(29.69 damage per second)\nEquip: Increases damage and healing done by magical '
                r'spells and effects by up to 90.\n#stats ",')
        rod = r'[3] = "Lively Rod\n(25.87 damage per second)\n#stats ",'
        with tempfile.TemporaryDirectory() as folder:
            saved, kept = Path(folder) / "EasyBIS_Capture.lua", Path(folder) / "weapons.json"
            saved.write_text(capture_of(rod), encoding="utf-8")
            with self.assertRaises(ValueError):
                capture.import_capture(tiny_db(), saved, kept)   # no weapon with spell power: nothing understood
            self.assertFalse(kept.exists())
            corrections.save({SCEPTER: IN_THE_GAME[SCEPTER], MACE: {"name": "Odd Mace", "healing": 1, "damage": 1}}, kept)
            saved.write_text(capture_of(mace, rod), encoding="utf-8")
            result = capture.import_capture(tiny_db(), saved, kept)
            self.assertEqual((result.weapons, result.with_power), (2, 1))
            merged = corrections.load(kept)
            self.assertEqual(sorted(merged), [SCEPTER, MACE, ROD])
            self.assertEqual(merged[MACE]["healing"], 90, "a weapon read again replaces what was kept")
            self.assertEqual(merged[ROD]["healing"], 0, "a weapon the game shows no spell power for is kept as such")
            self.assertEqual(merged[SCEPTER], IN_THE_GAME[SCEPTER])
            self.assertFalse((Path(folder) / "game.json").exists(), "two weapons of six do not say what the game has")

    # -- the items the game has ---------------------------------------------------------------------

    def game_db(self):
        """tiny_db with a chest pool for a Priest and a Mage: a cloth vest of the lists; the robe is not listed."""
        db = tiny_db()
        db.classes["MAGE"] = copy.deepcopy(db.classes["PRIEST"])
        for data in db.classes.values():
            data["pools"]["chest"] = [(VEST, 50)]
        db.gear[VEST] = {"inv": 5, "kind": "4.1", "req": 50, "stats": {5: 10}, "dps": 0.0, "armor": 60.0, "wand": False}
        db.items[VEST] = dict(db.items[ORB], name="Plain Vest")
        db.gear[ROBE] = {"inv": 20, "kind": "4.1", "req": 60, "stats": {5: 20, 45: 50}, "dps": 0.0, "armor": 120.0,
                         "wand": False}
        return db

    GAME = {"build": "1.0.0.1", "date": "2026-11-15", "listed": 9, "read": 7, "absent": [999, MACE],
            "unlisted": {ROBE: {"name": "Robe of Tests", "classes": ["Priest"], "unique": True, "limit": "TestRobes"},
                         ORB: {"name": "Glowing Orb"},    # ForeverDB lists it by now
                         404: {"name": "Gone"}}}          # the data no longer has it

    def test_the_lists_follow_the_game(self):
        db = self.game_db()
        db.items[SCEPTER]["twin"] = MACE
        report = corrections.align(db, self.GAME)
        self.assertIs(db.aligned, report)
        self.assertEqual((report.build, report.absent, report.dropped, report.added, report.listed, report.stale),
                         ("1.0.0.1", 2, [MACE], [ROBE], [ORB], False))
        self.assertTrue(report.changed)
        # the mace the game does not have leaves the pools; its name stays, the scepter's link to it goes
        self.assertEqual([item_id for item_id, _ in db.classes["PRIEST"]["pools"]["mh"]], [SCEPTER, ROD])
        self.assertIn(MACE, db.items)
        self.assertIsNone(db.items[SCEPTER]["twin"])
        self.assertEqual(self.shown(db), [SCEPTER, ROD], "the list shown by default only lost the mace")
        # the robe goes where cloth chests already are, but for the classes its tooltip leaves out
        self.assertEqual(db.classes["PRIEST"]["pools"]["chest"], [(VEST, 50), (ROBE, 60)])
        self.assertEqual(db.classes["MAGE"]["pools"]["chest"], [(VEST, 50)])
        self.assertEqual(sum(1 for data in db.classes.values() for pool in data["pools"].values()
                             for item_id, _ in pool if item_id == ROBE), 1)
        self.assertEqual(db.items[ROBE], {"name": "Robe of Tests", "groups": frozenset("u"), "flags": "U", "side": "",
                                          "twin": None, "limit": "TestRobes", "sources": [], "phase": phases.LATER,
                                          "added": True})
        # it shows with the items of no known source, once every phase counts
        robe = ladders.full_ladder(db, "PRIEST", 1, "pve", "chest")[0]
        self.assertEqual((robe.item_id, robe.unsourced, robe.phase, robe.stored), (ROBE, True, phases.LATER, 600))
        self.assertTrue(robe.passes(("a", True, False, phases.LATER)))
        self.assertFalse(robe.passes(("a", False, False, phases.LATER)))
        self.assertFalse(robe.passes(("a", True, False, phases.PRE_RAID)))

        kept = ladders.build_all(db)
        lists = luaout.lists_file(db, kept)
        self.assertIn("(build 1.0.0.1): 1 items the game does not have are left out", lists)
        self.assertIn("and 1 pieces it has that ForeverDB does not list are added", lists)
        self.assertIn(f"\tchest\t{ROBE}:600:uU9::TestRobes {VEST}:50", lists)
        self.assertIn(f"\n{ROBE}|Robe of Tests|u|U|\n", luaout.items_file(db, kept))
        names = luaout.names_file(db)
        self.assertIn("Odd Mace", names, "the search by name is still ForeverDB's list")
        self.assertNotIn("Robe of Tests", names)
        # the build points at an added piece that comes out several times ahead of what ForeverDB lists
        findings = audit.run(db, kept)
        hints = [f for f in findings if f.kind == audit.ADDED]
        self.assertEqual({(f.cls, f.slot, f.item_id) for f in hints}, {("PRIEST", "chest", ROBE)})
        self.assertIn("12.0 times Plain Vest, the best piece ForeverDB lists", hints[0].line())
        self.assertNotIn(ROBE, {f.item_id for f in audit.suspicious(findings)})
        self.assertIn("added, far ahead", audit.summary(findings))
        # an added piece brings no enchant row of its own: those show whatever the options
        staff = ladders.Entry(item_id=STAFF, score=1.0, side="", twin=None, seen=False, new=False, unsourced=False,
                              unique=False, two_hand=True, random=False, limit=None)
        self.assertTrue(luaout.enchant_fits(db, "w2h", {"pve": {"main": [staff]}}))
        db.items[STAFF]["added"] = True
        self.assertFalse(luaout.enchant_fits(db, "w2h", {"pve": {"main": [staff]}}))

        # a piece no player gets is not added; a reading older than the data's game build is said to be
        db = self.game_db()
        db.meta["build"] = "1.0.0.2"
        with mock.patch.dict(corrections.NOT_FOR_PLAYERS, {ROBE: "a test"}):
            report = corrections.align(db, self.GAME)
        self.assertEqual((report.added, report.withheld, report.stale), ([], [ROBE], True))
        self.assertNotIn(ROBE, db.items)
        # nor is one the game itself names as withdrawn
        db = self.game_db()
        withdrawn = {**self.GAME, "unlisted": {ROBE: {"name": "Robe of Tests DEPRECATED"}}}
        self.assertEqual(corrections.align(db, withdrawn).withheld, [ROBE])
        # without a reading of the game the data stays as it is
        db = self.game_db()
        report = corrections.align(db, {})
        self.assertEqual((report.build, report.changed, len(db.classes["PRIEST"]["pools"]["mh"])), ("", False, 3))
        self.assertEqual(luaout._corrections_note(db), ())

    def test_a_whole_capture_says_which_items_the_game_has(self):
        def capture_of(*rows, locale="enUS"):
            return "\n".join(["EasyBISCaptureDB = {", f'["meta"] = "1|1.0.0|1|{locale}|2026-11-15 12:30",',
                              '["missing"] = "7",', '["items"] = {', *rows, "},", "}", ""])
        rows = [
            r'[1] = "Low Scepter\nMain Hand\tMace\n(14.29 damage per second)\nEquip: Increases healing done by '
            r'spells and effects by up to 68.\n#stats ",',
            r'[2] = "Odd Mace\n(29.69 damage per second)\nEquip: Increases damage and healing done by magical '
            r'spells and effects by up to 90.\n#stats ",',
            r'[3] = "Lively Rod\n(25.87 damage per second)\n#stats ",',
            r'[8] = "Thin Wand\nRanged\tWand\n#stats ",',
            r'[9] = "Glowing Orb\nHeld In Off-hand\n#stats ",',
            r'[20] = "Robe of Tests\nBinds when picked up\nUnique\nUnique-Equipped: Test Robes (1)\nChest\tCloth\n'
            r'Classes: Priest, Mage\nRequires Level 60\n#stats ",',
        ]
        db = tiny_db()
        db.gear[ROBE] = {"inv": 20, "kind": "4.1", "req": 60, "stats": {7: 20}, "dps": 0.0, "armor": 0.0, "wand": False}
        reading = capture.game_reading(db, capture.parse_saved(capture_of(*rows)))
        robe = {"name": "Robe of Tests", "classes": ["Priest", "Mage"], "unique": True, "limit": "TestRobes"}
        self.assertEqual(reading, {"build": "1.0.0.1", "date": "2026-11-15", "listed": 7, "read": 6, "absent": [STAFF],
                                   "unlisted": {ROBE: robe}})
        # a capture that stopped early cannot say what the game lacks, nor one in another language
        self.assertIsNone(capture.game_reading(db, capture.parse_saved(capture_of(*rows[:4]))))
        self.assertIsNone(capture.game_reading(db, capture.parse_saved(capture_of(*rows, locale="frFR"))))
        self.assertEqual(capture.item_info(["A Ring", "Unique-Equipped: Signet Ring of the Bronze Dragonflight (1)"])
                         ["limit"], "SignetRingoftheB", "the category as ForeverDB writes its limit codes")

        with tempfile.TemporaryDirectory() as folder:
            saved, kept, game = (Path(folder) / name for name in ("EasyBIS_Capture.lua", "weapons.json", "game.json"))
            self.assertEqual(corrections.load_game(game), {})
            saved.write_text(capture_of(*rows), encoding="utf-8")
            result = capture.import_capture(db, saved, kept)
            self.assertEqual((result.listed, result.shown, result.reading["absent"]), (7, 6, [STAFF]))
            written = game.read_bytes()
            self.assertNotIn(b"\r", written)
            self.assertIn(f'\n    "{ROBE}": {{"classes": ["Priest", "Mage"], "limit": "TestRobes", "name": "Robe of Tests", '
                          '"unique": true}\n', written.decode("utf-8"), "one piece per line")
            self.assertEqual(corrections.load_game(game), {**reading, "about": corrections.GAME_ABOUT})
            # a partial capture read later leaves that file alone
            saved.write_text(capture_of(*rows[:2]), encoding="utf-8")
            self.assertIsNone(capture.import_capture(db, saved, kept).reading)
            self.assertEqual(game.read_bytes(), written)

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_the_tool_reads_tooltips_and_the_generator_reads_its_capture(self):
        """Capture.lua runs against stand-ins of the game; its saved variable goes through the importer."""
        lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        stub = lua.execute(CAPTURE_STUB)
        table = lua.table_from

        def tooltip(*pairs):
            return table([table(list(pair)) for pair in pairs])

        stub.add(MACE, True, tooltip(("Odd Mace",), ("One-Hand", "Mace"), ("33 - 62 Damage", "Speed 1.60"),
                                     ("(29.69 damage per second)",),
                                     ("Equip: Increases damage and healing done by magical spells and effects by up to 90.",)),
                 table({"ITEM_MOD_INTELLECT_SHORT": 13}))
        stub.add(ROD, False, tooltip(("Lively Rod",), ("(25.87 damage per second)",),
                                     ("Equip: Increases healing done by up to 124 and damage done by up to 41 "
                                      "for all magical spells and effects.",)), None)
        stub.add(STAFF, False, tooltip(("Channeling Staff",), ("Two-Hand", "Staff")), None)
        stub.never[STAFF] = True   # the game never shows it
        source = (BUILD / "capture_addon" / "Capture.lua").read_text(encoding="utf-8")
        stub.run(source, "2 3\n7")
        slash = lua.globals().SlashCmdList.EASYBISCAPTURE

        def play(until=None, seconds=1.0):
            """Lets the game run, a step at a time, to the capture's end or to a line that holds `until`."""
            for _ in range(4000):
                if stub.script is None:
                    return
                if until and until in stub.chat[len(stub.chat)]:
                    return
                stub.arrive()
                stub.script(None, seconds)
            self.fail("the capture never ended")

        def start(ids=None):
            """Runs /ebiscapture, on another list when `ids` is given; returns the place of its first line."""
            if ids is not None:
                stub.run(source, " ".join(str(item_id) for item_id in ids))
            said = len(stub.chat)
            lua.globals().SlashCmdList.EASYBISCAPTURE("")
            return said

        def lines(said):
            return [stub.chat[index] for index in range(said + 1, len(stub.chat) + 1)]

        stub.combat = True
        slash("")
        self.assertIsNone(stub.script, "a capture started in combat")
        stub.combat = False
        slash("")
        play()
        db = lua.globals().EasyBISCaptureDB
        self.assertEqual(db.meta, "1|1.0.0|1|enUS|2026-11-15 12:30")
        self.assertEqual(sorted(db["items"].keys()), [MACE, ROD], "the rod was asked for, then read")
        self.assertEqual((db.missing, db.absent), ("7", ""))
        self.assertIn("One-Hand\tMace\n33 - 62 Damage\tSpeed 1.60\n", db["items"][MACE])
        self.assertTrue(db["items"][MACE].endswith("\n#stats ITEM_MOD_INTELLECT_SHORT=13")
                        or db["items"][MACE].endswith("\n#stats ITEM_MOD_INTELLECT_SHORT=13.0"))
        chat = "\n".join(stub.chat.values())
        self.assertIn("1 items were not answered for: asking once more.", chat)
        self.assertIn("done: 2 items read now, 2 in all, 1 not read.", chat)
        self.assertIn("--check-capture", chat)
        self.assertEqual(stub.requests, 3, "the mace was there already; the rod once, the staff twice")

        # going on where it stopped: only the staff is asked for again, and what was read is kept
        slash("")
        play()
        self.assertEqual(sorted(lua.globals().EasyBISCaptureDB["items"].keys()), [MACE, ROD])
        slash("status")
        self.assertIn("2 items kept", stub.chat[len(stub.chat)])

        result = capture.read_capture(tiny_db(), saved_variable(lua.globals().EasyBISCaptureDB))
        self.assertEqual((result.game, result.weapons, result.with_power, result.missing), ("1.0.0.1", 2, 2, 1))
        self.assertEqual(result.observations[MACE], IN_THE_GAME[MACE])
        self.assertEqual((result.observations[ROD]["healing"], result.observations[ROD]["damage"],
                          result.observations[ROD]["dps"]), (124, 41, 25.87))

        parsed = capture.parse_saved(saved_variable(lua.globals().EasyBISCaptureDB))
        self.assertEqual((parsed["missing"], parsed["absent"], parsed["sample"]), ([STAFF], [], None))
        self.assertRegex(parsed["log"], r"^2026-11-15 12:30( \d+:\d+:\d+:\d+:\d+)+\n2026-11-15 12:30( \d+:\d+:\d+:\d+:\d+)+$")

        # a long list, in a game that answers a moment after it is asked: a few items are waited for at a
        # time, so it is never asked for more than it answers, and a line says where the capture is
        stub.slow = True
        stub.pieces(1000, 1599)
        stub.requests = 0
        said = start(range(1000, 1600))
        waited = []
        while stub.script is not None:
            stub.arrive()
            stub.script(None, 0.25)
            waited.append(len(stub.asked))
        told = lines(said)
        self.assertIn("reading 600 items, a few at a time, about 50 seconds if the game answers well", told[0])
        self.assertLessEqual(max(waited), 8, "more items waited for at once than the game is asked for")
        pace = [int(match.group(1)) for line in told
                for match in [re.search(r"\d+ read, \d+ to go: (\d+) a minute, about \d+ seconds left", line)] if match]
        self.assertEqual(len(pace), 1, told)
        self.assertTrue(600 <= pace[0] <= 720, "about twelve items a second")
        self.assertIn("done: 600 items read now, 602 in all, 0 not read.", told[-2])
        self.assertEqual(stub.requests, 600)

        # the server answers forty requests, then none: the capture says so, waits longer each time before
        # trying again, and stops by itself, having asked for little
        stub.pieces(2000, 2399)
        stub.requests, stub.quota = 0, 40
        said = start(range(2000, 2400))
        play()
        told = lines(said)
        silences = [line for line in told if "the game has not answered for" in line]
        self.assertIn("for 45 seconds (40 read so far): trying again in 15 seconds.", silences[0])
        self.assertEqual([re.search(r"again in (\d+)", line).group(1) for line in silences], ["15", "30", "60"])
        self.assertIn("stopped, the game does not answer: 40 items read now, 642 in all, 360 not read.", told[-2])
        self.assertIn("What was read is kept. Type /reload to save.", told[-1])
        self.assertLess(stub.requests, 200, "it went on asking a game that does not answer")
        self.assertEqual(len(lua.globals().EasyBISCaptureDB.missing.split()), 360)

        # the game answers again after a while: the capture goes on by itself
        stub.requests, stub.quota = 0, 10
        said = start()
        play(until="trying again in 15 seconds")
        stub.quota = None
        play()
        told = lines(said)
        self.assertTrue(any("the game answers again." in line for line in told), told)
        self.assertIn("done: 360 items read now, 1002 in all, 0 not read.", told[-2])

        # items the game's own item table does not list are not asked for, but for a few, as a check
        stub.pieces(3000, 3039)
        for item_id in range(3020, 3040):
            stub.unknown[item_id] = True
        stub.requests = 0
        said = start(range(3000, 3040))
        play()
        told = lines(said)
        self.assertIn("reading 20 items", told[0])
        self.assertIn("20 more are not in the game's item table: they are not asked for.", told[1])
        self.assertIn("done: 20 items read now, 1022 in all, 20 not read.", told[-2])
        db = lua.globals().EasyBISCaptureDB
        self.assertEqual(db.absent, " ".join(str(item_id) for item_id in range(3020, 3040)))
        self.assertEqual((db.sample, stub.requests), ("16:0", 36))
        # ... unless that table lists next to nothing: then it is of no help, and every item is asked for
        stub.pieces(4000, 4009)
        for item_id in range(4001, 4010):
            stub.unknown[item_id] = True
            stub.never[item_id] = None
        said = start(range(4000, 4010))
        self.assertEqual(lua.globals().EasyBISCaptureDB.absent, "")
        self.assertIn("reading 10 items", lines(said)[0])
        slash("stop")
        db = tiny_db()
        corrections.apply(db, result.observations)
        self.assertEqual(self.shown(db), [ROD, MACE, SCEPTER])


# -- the sources the data lacks, read in QuestieDB ------------------------------------------------------------

def cbor(value) -> bytes:
    """A CBOR value as QuestieDB stores them: enough of the format for the test's rows."""
    def head(major, number):
        if number < 24:
            return bytes([major << 5 | number])
        size = 1 if number < 256 else 2 if number < 65536 else 4 if number < 1 << 32 else 8
        return bytes([major << 5 | {1: 24, 2: 25, 4: 26, 8: 27}[size]]) + number.to_bytes(size, "big")
    if value is None:
        return b"\xf6"
    if isinstance(value, float):
        import struct
        return b"\xfb" + struct.pack(">d", value)
    if isinstance(value, int):
        return head(0, value) if value >= 0 else head(1, -1 - value)
    if isinstance(value, str):
        return head(3, len(value.encode())) + value.encode()
    if isinstance(value, list):
        return head(4, len(value)) + b"".join(map(cbor, value))
    return head(5, len(value)) + b"".join(cbor(key) + cbor(item) for key, item in value.items())


def questie_addon(folder: Path, rows: dict, chunked=()) -> Path:
    """A QuestieDB addon folder holding rows {(entity, id, field): value}; the fields named in chunked are
    cut in two parts, as the addon cuts a long value."""
    import base64
    lines = ["## Interface: 16001", "## Title: QuestieDB", "## Version: 9.9.9", "## X-Flavor: Forever",
             "## X-BUILD-COMMIT: abc123"]
    for (entity, number, name), value in rows.items():
        text = base64.b64encode(cbor(value)).decode()
        key = f"## X-{entity}-{number}-{name}"
        if (entity, number, name) in chunked:
            half = len(text) // 2
            lines += [f"{key}: ~2~", f"{key}-1: {text[:half]}", f"{key}-2: {text[half:]}"]
        else:
            lines.append(f"{key}: {text}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / questie.TOC).write_text("\n".join(lines) + "\n", encoding="utf-8")
    zones = folder / "support" / "Forever" / "Zones"
    zones.mkdir(parents=True)
    (folder / "src" / "corrections" / "enum").mkdir(parents=True)
    (folder / "src" / "corrections" / "enum" / "zones.lua").write_text(
        "constants.zoneIDs = {\n  RAZORFEN_KRAUL = 491,\n  NAXXRAMAS = 3456,\n  KARAZHAN = 3457,\n}\n", encoding="utf-8")
    (zones / "instanceIdToAreaId.lua").write_text(
        "ZoneDB.instanceIdToAreaId = {\n    [47] = ZoneDB.zoneIDs.RAZORFEN_KRAUL,\n"
        "    [533] = ZoneDB.zoneIDs.NAXXRAMAS,\n    [532] = ZoneDB.zoneIDs.KARAZHAN,\n}\n", encoding="utf-8")
    (zones / "dungeons.lua").write_text(
        'local dungeons = {\n    [491] = {"Razorfen Kraul",{1717},17,{{17, 42.9, 90.2}}},\n'
        '    [3456] = {"Naxxramas",{10062, 10063},65,{{139, 34.25, 19.45}}},\n'
        '    [3457] = {"Karazhan",nil,41,{{41, 46.8, 74.7}}},\n}\n', encoding="utf-8")
    (zones / "areaIdToUiMapId.lua").write_text(
        "ZoneDB.private.areaIdToUiMapIdOverride = [[return {\n    [1537] = 1455, -- an override comes first\n}]]\n"
        "ZoneDB.private.areaIdToUiMapId = [[return {\n    [1537] = 9999,\n    [1637] = 1454,\n}]]\n", encoding="utf-8")
    return folder


HOOD, BELT, GEM, CHARM, SEAL, RELIC, CLOAK = 40, 41, 42, 43, 44, 45, 46
ARCANUM, SIGIL, RUNE = "i50", "i51", "i52"

# What a QuestieDB knows of the test's items. Fields: questie.ITEM_*, QUEST_*, NPC_*.
QUESTIE_ROWS = {
    # a quest of a dungeon, for the Horde, and the same quest for both factions
    ("Item", HOOD, "S"): {1: "Hood of Tests", "p": 32}, ("Item", HOOD, "6"): [701, 700],
    ("Quest", 700, "S"): {1: "A Dungeon Errand", 4: 55, 5: 60, 17: 1717, 6: 178},
    ("Quest", 701, "S"): {1: "An Errand", 4: 50, 5: 60, 17: 40},
    # two vendors, one per faction, and a guard QuestieDB's drop tables hold; a container
    ("Item", BELT, "S"): {1: "Belt of Tests"}, ("Item", BELT, "14"): [801, 800], ("Item", BELT, "2"): [802],
    ("Item", BELT, "4"): [60],
    ("Item", 60, "S"): ["Box of Belts"],   # a row whose first fields are all set is a list
    ("Npc", 800, "S"): {1: "Deliana", 9: 1537, 13: "A"}, ("Npc", 800, "7"): {1537: [[43.44, 52.13]]},
    ("Npc", 801, "S"): {1: "Mokvar", 9: 1637, 13: "H"}, ("Npc", 801, "7"): {1637: [[-1, -1]]},
    ("Npc", 802, "S"): {1: "City Guard", 9: 1537, 13: "A"}, ("Npc", 802, "7"): {1537: [[40.0, 50.0]]},
    # a boss of a raid ForeverDB's table lacks, its trash, and a rare of the open world
    ("Item", GEM, "S"): {1: "Gem of Tests"}, ("Item", GEM, "2"): [902, 901, 900],
    ("Npc", 900, "S"): {1: "A Frost Wyrm", 6: 3, 9: 3456}, ("Npc", 901, "S"): {1: "Crypt Guard", 6: 1, 9: 10062},
    ("Npc", 902, "S"): {1: "Lone Stalker", 6: 4, 9: 40}, ("Npc", 902, "7"): {40: [[10.0, 20.0]]},
    # a boss QuestieDB does not place, and a creature with no place either
    ("Item", CHARM, "S"): {1: "Charm of Tests"}, ("Item", CHARM, "2"): [910, 911],
    ("Npc", 910, "S"): ["Sapphiron", None, None, 63, 63, 3], ("Npc", 911, "S"): {1: "Nowhere Man", 6: 1},
    # a creature of an instance nothing knows: not kept, and the item stays without a source
    ("Item", SEAL, "S"): {1: "Seal of Tests"}, ("Item", SEAL, "2"): [920],
    ("Npc", 920, "S"): {1: "Tower Ghost", 6: 1, 9: 3457},
    # a chest of a dungeon; QuestieDB has two chests of that name
    ("Item", RELIC, "S"): {1: "Relic of Tests"}, ("Item", RELIC, "3"): [70, 71],
    ("Object", 70, "S"): {1: "Old Chest", 5: 491}, ("Object", 71, "S"): {1: "Old Chest", 5: 491},
    # a name the data files cannot hold
    ("Item", CLOAK, "S"): {1: "Cloak of Tests"}, ("Item", CLOAK, "6"): [702],
    ("Quest", 702, "S"): {1: "One | Two", 4: 1, 5: 1},
    # the items to apply
    ("Item", 50, "S"): {1: "Arcanum of Tests"}, ("Item", 50, "6"): [700],
    ("Item", 51, "S"): {1: "Sigil of Tests"}, ("Item", 51, "2"): [900],
    ("Item", 52, "S"): {1: "Rune of Tests"}, ("Item", 52, "2"): [910],
}


def sourceless_db():
    """tiny_db with the items ForeverDB's data gives no source: pieces of its lists, and three enchants."""
    db = tiny_db()
    db.instances = {47: ["Razorfen Kraul", "dungeon", "1413", "42", "89", "The Barrens", "f", "A Boss"]}
    for item_id, name in ((HOOD, "Hood of Tests"), (BELT, "Belt of Tests"), (GEM, "Gem of Tests"),
                          (CHARM, "Charm of Tests"), (SEAL, "Seal of Tests"), (RELIC, "Relic of Tests"),
                          (CLOAK, "Cloak of Tests")):
        db.items[item_id] = {"name": name, "groups": frozenset("u"), "flags": "", "side": "", "twin": None,
                             "limit": None, "sources": []}
    db.enchant_info = {ARCANUM: ["Arcanum of Tests", "Dodge +1%", corrections.UNKNOWN_WHERE, "f"],
                       SIGIL: ["Sigil of Tests", "Armor +1", corrections.UNKNOWN_WHERE, "f"],
                       RUNE: ["Rune of Tests", "Armor +2", corrections.UNKNOWN_WHERE, "f"],
                       "i53": ["Kit of Tests", "Armor +3", "Leatherworking 225: from a trainer", "k"],
                       "s54": ["Enchant Tests", "Armor +4", corrections.UNKNOWN_WHERE, "f"]}
    return db


class SourcesTest(unittest.TestCase):
    def reading(self, folder, db=None, game=None, chunked=()):
        store = questie.Store(questie_addon(Path(folder) / "QuestieDB", QUESTIE_ROWS, chunked))
        return questie.collect(db or sourceless_db(), game or {}, store, today="2026-11-17")

    def test_questiedb_is_read_as_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(questie.find(folder))
            reading = self.reading(folder)
            self.assertEqual(questie.find(folder), Path(folder) / "QuestieDB")
            store = questie.Store(Path(folder) / "QuestieDB")
            self.assertEqual((store.version, store.commit, store.flavor), ("9.9.9", "abc123", "Forever"))
            self.assertEqual(store.row("Item", 60), {1: "Box of Belts"})
            self.assertEqual(store.row("Npc", 910), {1: "Sapphiron", 4: 63, 5: 63, 6: 3})
            self.assertEqual(store.row("Npc", 12345), {})
        self.assertEqual({name: reading[name] for name in ("questiedb", "commit", "date", "asked")},
                         {"questiedb": "9.9.9", "commit": "abc123", "date": "2026-11-17",
                          "asked": {"items": 7, "enchants": 3}})
        items = reading["items"]
        # the quest of both factions first; the dungeon a quest belongs to is said beside it
        self.assertEqual(items[HOOD], {"name": "Hood of Tests", "at": [None, 47], "sources": [
            ["q", "701", "An Errand", "50", "", "t"], ["q", "700", "A Dungeon Errand", "55", "h", "t"]]})
        # a vendor with the map and the spot QuestieDB has, the faction it serves; no guard; the container last
        self.assertEqual(items[BELT], {"name": "Belt of Tests", "sources": [
            ["v", "800", "Deliana", "1455", "43.44", "52.13", "", "a", "t"],
            ["v", "801", "Mokvar", "1454", "", "", "", "h", "t"], ["x", "60", "Box of Belts", "t"]]})
        # the boss before the trash, as bosses of the raid; a part of an instance is that instance; the rare
        self.assertEqual(items[GEM]["sources"], [
            ["d", "533", "A Frost Wyrm", "", "1", "t"], ["d", "533", "Crypt Guard", "", "1", "t"]])
        self.assertEqual(reading["instances"], {533: "Naxxramas"})
        # a boss with no place is one of some raid; a creature with no place is not said
        self.assertEqual(items[CHARM], {"name": "Charm of Tests", "at": ["boss"],
                                        "sources": [["m", "910", "Sapphiron", "", "t"]]})
        self.assertNotIn(SEAL, items, "Karazhan is an instance neither ForeverDB nor phases.py knows")
        self.assertEqual(items[RELIC], {"name": "Relic of Tests", "at": [47], "sources": [["o", "Old Chest", "", "t"]]})
        self.assertNotIn(CLOAK, items, "a quest title with a separator of the data files is not written")
        self.assertEqual(reading["enchants"], {
            ARCANUM: {"where": "Quest: A Dungeon Errand (Razorfen Kraul)", "at": 47},
            SIGIL: {"where": "Raid drop: A Frost Wyrm (Naxxramas)", "at": 533},
            RUNE: {"where": "Raid drop: Sapphiron", "at": "boss"}})
        # a piece the game showed that ForeverDB does not list is asked for too, an item the game does not
        # have is not; a value cut in parts reads the same
        with tempfile.TemporaryDirectory() as folder:
            db = sourceless_db()
            del db.items[GEM]
            again = self.reading(folder, db, {"unlisted": {GEM: {"name": "Gem of Tests"}}, "absent": [HOOD]},
                                 chunked={("Item", GEM, "2"), ("Npc", 900, "S")})
        self.assertEqual(again["items"], {item_id: record for item_id, record in items.items() if item_id != HOOD})
        # a rare, when no boss drops the piece
        rows = {**QUESTIE_ROWS, ("Item", GEM, "2"): [902]}
        with tempfile.TemporaryDirectory() as folder:
            store = questie.Store(questie_addon(Path(folder) / "QuestieDB", rows))
            rare = questie.collect(sourceless_db(), {}, store)["items"][GEM]
        self.assertEqual(rare["sources"], [["R", "902", "Lone Stalker", "", "t"]])
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / questie.TOC).write_text("## Title: Something else\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                questie.Store(folder)

    def test_sources_fill_the_data(self):
        with tempfile.TemporaryDirectory() as folder:
            reading = self.reading(folder)
            path = Path(folder) / "sources.json"
            self.assertEqual(corrections.load_sources(path), {})
            corrections.save_sources(reading, path)
            written = path.read_bytes()
            self.assertNotIn(b"\r", written)
            self.assertIn(f'\n    "{CHARM}": {{"at": ["boss"], "name": "Charm of Tests", "sources": '
                          '[["m", "910", "Sapphiron", "", "t"]]}', written.decode("utf-8"), "one item per line")
            self.assertEqual(corrections.load_sources(path), {**reading, "about": corrections.SOURCES_ABOUT})
            reading = corrections.load_sources(path)

        db = sourceless_db()
        db.items[RELIC].update(groups=frozenset("u"), phase=phases.LATER, added=True)   # a piece added from the game
        db.items[BELT].update(groups=frozenset("v"), sources=[["V", "5", "10", "", "s"]])   # ForeverDB says by now
        db.enchant_info[RUNE][2] = "Enchanting 300: from a trainer"                        # ... and for this one too
        report = corrections.fill(db, reading)
        self.assertIs(db.filled, report)
        self.assertEqual((report.version, report.date, report.known), ("9.9.9", "2026-11-17", 5))
        self.assertEqual((report.items, report.added, report.listed, report.enchants, report.instances),
                         ([HOOD, GEM, CHARM, RELIC], [RELIC], [BELT], [ARCANUM, SIGIL], [533]))
        self.assertTrue(report.changed)
        # a quest of the open world and one of a dungeon: to be had before the raids
        hood = db.items[HOOD]
        self.assertEqual((hood["groups"], hood["phase"], hood["sources"][0][:3]),
                         (frozenset("qQ"), phases.PRE_RAID, ["q", "701", "An Errand"]))
        # the raid ForeverDB's table lacks is named, as a Classic raid: its drops count once every phase does
        self.assertEqual(db.instances[533], ["Naxxramas", "raid", "", "", "", "", "t"])
        self.assertEqual((db.items[GEM]["groups"], db.items[GEM]["phase"]), (frozenset("r"), phases.LATER))
        self.assertEqual((db.items[CHARM]["groups"], db.items[CHARM]["phase"]), (frozenset("w"), phases.LATER))
        # a piece added from the game gets the source to show, and stays where it showed
        relic = db.items[RELIC]
        self.assertEqual((relic["groups"], relic["phase"], relic["sources"]),
                         (frozenset("u"), phases.LATER, [["o", "Old Chest", "", "t"]]))
        # what ForeverDB's data says is left alone
        self.assertEqual(db.items[BELT]["sources"], [["V", "5", "10", "", "s"]])
        self.assertEqual(db.enchant_info[RUNE][2:], ["Enchanting 300: from a trainer", "f"])
        self.assertEqual(db.items[SEAL]["sources"], [])
        # the enchants: a sentence, the label, and the raid the source needs
        self.assertEqual(db.enchant_info[ARCANUM][2:], ["Quest: A Dungeon Errand (Razorfen Kraul)", "t"])
        self.assertEqual(db.enchant_info[SIGIL][2:], ["Raid drop: A Frost Wyrm (Naxxramas)", "t"])
        self.assertEqual((phases.enchant_phase(db, ARCANUM), phases.enchant_phase(db, SIGIL)),
                         (phases.PRE_RAID, phases.LATER))

        # in the lists: no longer an item of no known source, from the phase of its source
        db.classes["PRIEST"]["pools"]["head"] = [(HOOD, 60), (GEM, 60), (RELIC, 60)]
        for item_id, power in ((HOOD, 10), (GEM, 30), (RELIC, 20)):
            db.gear[item_id] = {"inv": 1, "kind": "4.1", "req": 60, "stats": {45: power}, "dps": 0.0, "armor": 0.0,
                                "wand": False}
        ladder = {entry.item_id: entry for entry in ladders.full_ladder(db, "PRIEST", 1, "pve", "head")}
        self.assertEqual([(entry.item_id, entry.unsourced, entry.phase) for entry in ladder.values()],
                         [(GEM, False, phases.LATER), (RELIC, True, phases.LATER), (HOOD, False, phases.PRE_RAID)])
        self.assertTrue(ladder[HOOD].passes(("a", False, False, phases.PRE_RAID)))
        self.assertFalse(ladder[GEM].passes(("a", False, False, phases.PRE_RAID)))
        self.assertTrue(ladder[GEM].passes(("a", False, False, phases.LATER)))
        self.assertFalse(ladder[RELIC].passes(("a", False, False, phases.LATER)))
        # in the data files: the sources, the raid's name, and what was added to ForeverDB's data
        kept = ladders.build_all(db)
        items_file = luaout.items_file(db, kept)
        self.assertIn(f"\n{HOOD}|Hood of Tests|Qq||q^701^An Errand^50^^t~q^700^A Dungeon Errand^55^h^t\n", items_file)
        self.assertIn(f"\n{GEM}|Gem of Tests|r||d^533^A Frost Wyrm^^1^t~d^533^Crypt Guard^^1^t\n", items_file)
        self.assertIn(f"\n{RELIC}|Relic of Tests|u||o^Old Chest^^t\n", items_file)
        self.assertIn('\n[533]="Naxxramas^raid^^",\n', items_file)
        for text in (items_file, luaout.lists_file(db, kept), luaout.enchants_file(db, kept)):
            self.assertIn("4 items and 2 enchants it gives no source have the one read in QuestieDB 9.9.9", text)
            self.assertIn("the 1 pieces added from the game among them stay flagged u and 9", text)
        self.assertNotIn("QuestieDB", luaout.lists_file(tiny_db(), ladders.build_all(tiny_db())))
        # nothing read yet: nothing changes
        untouched = sourceless_db()
        self.assertFalse(corrections.fill(untouched, {}).changed)
        self.assertEqual(untouched.items, sourceless_db().items)

    def test_the_build_imports_questiedb(self):
        with tempfile.TemporaryDirectory() as folder:
            addon = questie_addon(Path(folder) / "QuestieDB", QUESTIE_ROWS)
            kept = Path(folder) / "sources.json"
            said = []
            with mock.patch.object(corrections, "SOURCES_FILE", kept), \
                    mock.patch.object(build, "build", lambda details=False: 0), \
                    mock.patch.object(fdb, "load", lambda cache, corrected=True: sourceless_db()), \
                    mock.patch.object(corrections, "load_game", lambda: {}), \
                    mock.patch.object(build, "HERE", Path(folder) / "_build"), \
                    mock.patch("builtins.print", lambda *words: said.append(" ".join(map(str, words)))):
                self.assertEqual(build.main(["--import-questie", str(addon)]), 0)
                self.assertTrue(kept.exists())
                self.assertEqual(build.main(["--import-questie", str(Path(folder) / "nowhere")]), 1)
            self.assertIn("of the 7 items and 3 enchants the data gives no source, it has one for 5 and 3", said[0])
            self.assertIn("No QuestieDB_Forever.toc", said[-1])


DROP_RATES = f"""FDJ.DROP_RATES = FDJ.DROP_RATES or {{}}
FDJ.DROP_RATES["Upper Blackrock Spire"] = {{
    ["Pyroguard Emberseer"] = {{ -- NPC 9816, 301 kills on Wowhead Forever
        [{HOOD}] = 15.6, -- Hood of Tests (47/301)
        [{CLOAK}] = 0.3, -- Cloak of Tests (1/301)
    }},
    ["Lord Valthalak"] = {{ -- NPC 16042, only 3 kills on Wowhead Forever: Classic Wowhead's numbers (1049 kills)
        [{BELT}] = 9, -- Belt of Tests (94/1049)
    }},
}}
FDJ.DROP_RATES["Blackrock Depths"] = {{
    ["Theldren"] = {{ -- Arena Spoils (object 181074), opened 172 times on Wowhead Forever
        [{GEM}] = 31.4, -- Gem of Tests (54/172)
    }},
}}
"""
AUDIT_TIPS = (f'    [{CHARM}]="Charm of Tests\\nDropped by: Mizzle the Crafty\\nDrop Chance: 2.5%",\n'
              f'    [{SEAL}]="Seal of Tests\\nSell Price: 1 2 3",\n')


def drop_addons(folder) -> Path:
    """An AddOns folder holding the two addons drops.py reads."""
    addons = Path(folder)
    (addons / drops.JOURNAL / "Data").mkdir(parents=True)
    (addons / drops.JOURNAL / drops.RATES).write_text(DROP_RATES, encoding="utf-8")
    (addons / drops.JOURNAL / f"{drops.JOURNAL}.toc").write_text("## Version: 2.0.11\n", encoding="utf-8")
    (addons / drops.GEARQUEST).mkdir()
    (addons / drops.GEARQUEST / f"{drops.GEARQUEST}.toc").write_text("## Version: 1.2.2\n", encoding="utf-8")
    (addons / f"{drops.GEARQUEST}_ROGUE").mkdir()
    (addons / f"{drops.GEARQUEST}_ROGUE" / drops.TIPS).write_text(AUDIT_TIPS, encoding="utf-8")
    return addons


class DropsTest(unittest.TestCase):
    def db(self, **sources):
        db = sourceless_db()
        db.instances = {229: ["Blackrock Spire", "dungeon"], 230: ["Blackrock Depths", "dungeon"]}
        for name, listed in sources.items():
            db.items[globals()[name]].update(sources=listed, groups=frozenset("w"))
        return db

    def reading(self, **records):
        return {"journal": "2.0.11", "date": "2026-11-18",
                "items": {globals()[name]: record for name, record in records.items()}}

    EMBERSEER = {"boss": "Pyroguard Emberseer", "dungeon": "Upper Blackrock Spire", "drops": 47, "kills": 301,
                 "percent": 15.6}
    THELDREN = {"boss": "Theldren", "dungeon": "Blackrock Depths", "drops": 54, "kills": 172, "percent": 31.4}

    def test_the_counts_are_read_in_the_addons(self):
        journal = drops.read_journal(DROP_RATES)
        self.assertEqual(journal[HOOD], [self.EMBERSEER])
        self.assertEqual(journal[GEM], [self.THELDREN], "a chest is counted by the times it was opened")
        self.assertNotIn(BELT, journal, "Classic's numbers say nothing of Forever")
        self.assertEqual(drops.read_tips(AUDIT_TIPS), {CHARM: {"boss": "Mizzle the Crafty", "percent": 2.5}})
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(drops.find(folder))
            with self.assertRaises(ValueError):
                drops.collect(sourceless_db(), folder)
            addons = drop_addons(folder)
            self.assertEqual(drops.find(addons), addons / drops.JOURNAL)
            reading = drops.collect(sourceless_db(), addons, today="2026-11-18")
        self.assertEqual((reading["journal"], reading["gearquest"], reading["date"]), ("2.0.11", "1.2.2", "2026-11-18"))
        self.assertEqual(sorted(reading["items"]), sorted((HOOD, CLOAK, GEM, CHARM)))
        self.assertEqual(reading["items"][CHARM], {"name": "Charm of Tests",
                                                   "tooltip": {"boss": "Mizzle the Crafty", "percent": 2.5}})

    def test_a_counted_drop_confirms_the_source(self):
        db = self.db(HOOD=[["d", "229", "Other Boss", "9", "0", "k"], ["d", "229", "Pyroguard Emberseer", "20", "0", "k"]],
                     BELT=[["d", "229", "Ras Frostwhisperer", "20", "0", "t"]],
                     GEM=[["d", "229", "", "5", "0", "k"]],
                     CHARM=[["m", "7", "Mizzle the Crafty", "1", "c"]])
        frost = {**self.EMBERSEER, "boss": "Ras Frostwhisper"}
        report = corrections.confirm(db, self.reading(HOOD={"seen": [self.EMBERSEER]}, BELT={"seen": [frost]},
                                                      GEM={"seen": [self.EMBERSEER]},
                                                      CHARM={"tooltip": {"boss": "Mizzle the Crafty", "percent": 2.5}}))
        self.assertIs(db.confirmed, report)
        self.assertEqual(db.items[HOOD]["sources"], [["d", "229", "Pyroguard Emberseer", "15.6", "0", "w"],
                                                     ["d", "229", "Other Boss", "9", "0", "k"]],
                         "the addon shows the first source: the one counted")
        self.assertEqual(db.items[BELT]["sources"], [["d", "229", "Ras Frostwhisperer", "15.6", "0", "w"]])
        self.assertEqual(db.items[GEM]["sources"], [["d", "229", "Pyroguard Emberseer", "15.6", "0", "w"]])
        self.assertEqual(db.items[CHARM]["sources"], [["m", "7", "Mizzle the Crafty", "2.5", "w"]])
        self.assertEqual((sorted(report.items), report.named, report.moved, report.disputed),
                         (sorted((HOOD, BELT, GEM, CHARM)), [GEM], [], []))
        self.assertTrue(report.changed)

    def test_another_boss_needs_more_than_a_stray_record(self):
        db = self.db(HOOD=[["m", "8", "Deep Stinger", "0.02", "k"]],
                     BELT=[["m", "8", "Deep Stinger", "0.02", "k"]],
                     GEM=[["m", "8", "Deep Stinger", "0.02", "k"]],
                     CHARM=[["d", "229", "Seen Boss", "4", "0", "s"], ["m", "8", "Deep Stinger", "0.02", "k"]])
        db.items[RELIC].update(sources=[["d", "230", "A Guard", "", "0", "t"]], groups=frozenset("u"), added=True,
                               phase=phases.LATER)
        db.items[SEAL].update(sources=[["d", "229", "", "0", "0", "c"]], groups=frozenset("d"))
        stray = {**self.EMBERSEER, "drops": 1, "percent": 0.3}
        elsewhere = {"boss": "Bonesnout the Unbroken", "dungeon": "Halls of Nowhere", "drops": 77, "kills": 221, "percent": 34.8}
        report = corrections.confirm(db, self.reading(
            HOOD={"seen": [self.THELDREN]}, BELT={"seen": [stray]},
            GEM={"tooltip": {"boss": "Mizzle the Crafty", "percent": 2.5}}, CHARM={"seen": [self.THELDREN]},
            RELIC={"seen": [self.THELDREN]}, SEAL={"seen": [elsewhere]}))
        self.assertEqual(db.items[SEAL]["sources"], [["m", "0", "Bonesnout the Unbroken", "34.8", "w"]],
                         "a dungeon the data does not have: the boss, and not the wrong dungeon")
        db.instances[34] = ["Stormwind Stockade", "dungeon"]
        self.assertEqual(corrections._instance(db, "The Stockade"), 34)
        self.assertEqual(db.items[HOOD]["sources"], [["d", "230", "Theldren", "31.4", "0", "w"]])
        self.assertEqual(db.items[HOOD]["groups"], frozenset("d"), "no longer a world drop")
        self.assertEqual(db.items[BELT]["sources"], [["m", "8", "Deep Stinger", "0.02", "k"]])
        self.assertEqual(db.items[GEM]["sources"], [["m", "8", "Deep Stinger", "0.02", "k"]], "a tooltip names one creature")
        self.assertEqual(db.items[CHARM]["sources"][0], ["d", "229", "Seen Boss", "4", "0", "s"], "ForeverDB saw it itself")
        self.assertEqual(db.items[RELIC]["sources"], [["d", "230", "Theldren", "31.4", "0", "w"]])
        self.assertEqual((db.items[RELIC]["groups"], db.items[RELIC]["phase"], report.settled), (frozenset("d"), phases.PRE_RAID, [RELIC]),
                         "a piece added from the game whose drop was counted is a dungeon's item: players loot it")
        self.assertEqual((report.items, report.moved, report.disputed),
                         ([], sorted((HOOD, RELIC, SEAL)), sorted((BELT, GEM))))
        # nothing read yet: nothing changes
        untouched = self.db(HOOD=[["m", "8", "Deep Stinger", "0.02", "k"]])
        self.assertFalse(corrections.confirm(untouched, {}).changed)
        self.assertEqual(untouched.items[HOOD]["sources"], [["m", "8", "Deep Stinger", "0.02", "k"]])

    def test_the_data_files_say_where_the_drops_come_from(self):
        db = self.db(HOOD=[["d", "229", "Pyroguard Emberseer", "20", "0", "k"]])
        db.classes["PRIEST"]["pools"]["head"] = [(HOOD, 60)]
        db.gear[HOOD] = {"inv": 1, "kind": "4.1", "req": 60, "stats": {45: 10}, "dps": 0.0, "armor": 0.0, "wand": False}
        corrections.confirm(db, self.reading(HOOD={"seen": [self.EMBERSEER]}))
        kept = ladders.build_all(db)
        text = luaout.items_file(db, kept)
        self.assertIn(f"\n{HOOD}|Hood of Tests|w||d^229^Pyroguard Emberseer^15.6^0^w\n", text)
        self.assertIn("Confirmed in Forever: 1 items take the boss and the rate Wowhead Forever counted", text)
        self.assertNotIn("Confirmed in Forever", luaout.lists_file(db, kept), "the lists do not depend on it")

    def test_the_build_imports_the_drops(self):
        with tempfile.TemporaryDirectory() as folder:
            addons = drop_addons(Path(folder) / "AddOns")
            kept = Path(folder) / "drops.json"
            said = []
            with mock.patch.object(corrections, "DROPS_FILE", kept), \
                    mock.patch.object(build, "build", lambda details=False: 0), \
                    mock.patch.object(fdb, "load", lambda cache, corrected=True: sourceless_db()), \
                    mock.patch("builtins.print", lambda *words: said.append(" ".join(map(str, words)))):
                self.assertEqual(build.main(["--import-drops", str(addons)]), 0)
                self.assertEqual(build.main(["--import-drops", str(Path(folder) / "nowhere")]), 1)
            self.assertIn("drops counted for 4 items of the data", said[0])
            self.assertIn("No ForeverDungeonJournal addon", said[-1])
            written = kept.read_bytes()
            self.assertNotIn(b"\r", written)
            loaded = corrections.load_drops(kept)
        self.assertEqual(loaded["about"], corrections.DROPS_ABOUT)
        self.assertEqual(loaded["items"][HOOD]["seen"], [self.EMBERSEER])
        self.assertEqual(corrections.load_drops(Path(folder) / "gone.json"), {})


class RunsTest(unittest.TestCase):
    """The runs of the Dungeons tab: the dungeons the data lacks, the creatures the counts place in one, the
    wing of a boss and the dungeon of a quest."""

    def db(self, **sources):
        db = sourceless_db()
        db.instances = {33: ["Shadowfang Keep", "dungeon"], 189: ["Scarlet Monastery", "dungeon"],
                        229: ["Blackrock Spire", "dungeon"], 230: ["Blackrock Depths", "dungeon"],
                        289: ["Scholomance", "dungeon"], 533: ["Naxxramas", "raid"]}
        for name, listed in sources.items():
            db.items[globals()[name]].update(sources=listed, groups=frozenset("w"))
        return db

    @staticmethod
    def seen(boss, dungeon, percent, drops=50):
        return {"seen": [{"boss": boss, "dungeon": dungeon, "drops": drops, "kills": 300, "percent": percent}]}

    def test_the_dungeons_the_data_lacks_are_added(self):
        db = self.db()
        self.assertEqual(sorted(runs.add_dungeons(db)), sorted(runs.DUNGEONS.values()))
        self.assertEqual(db.instances[2974], ["Blackmaw Hold", "dungeon", "", "", "", "", "w"])
        self.assertEqual(runs.add_dungeons(db), [], "once")
        # a dungeon the data names by now, whatever the article, is its own
        named = self.db()
        named.instances[7] = ["The Hall of Thanes", "dungeon"]
        self.assertNotIn(3065, runs.add_dungeons(named))
        self.assertEqual(corrections._instance(named, "Hall of Thanes"), 7)
        # nothing counted yet: the data is left as it is
        untouched = self.db()
        self.assertEqual(corrections.confirm(untouched, {}).dungeons, [])
        self.assertNotIn(2974, untouched.instances)

    def test_a_creature_counted_in_a_dungeon_is_a_boss_of_it(self):
        db = self.db(
            HOOD=[["m", "9027", "Gorosh the Dervish", "10", "k"]],                       # Classic's, with no place
            BELT=[["m", "258905", "NPC 258905", "0", "s"]],                              # seen, and not named
            GEM=[["m", "6487", "Arcanist Doan", "0", "s"], ["w", "0", "0", "k"]],        # seen, with no rate
            CHARM=[["d", "289", "Kirtonos", "20", "0", "k"], ["m", "10506", "Kirtonos the Herald", "20", "k"]],
            SEAL=[["d", "229", "", "0", "0", "c"]],                                      # the wrong dungeon
            RELIC=[["m", "3864", "Fel Steed", "8.24", "s"]],                             # seen, with its rate
            CLOAK=[["m", "1", "NPC 1", "0", "s"], ["m", "2", "NPC 2", "0", "s"]])        # two creatures of no name
        db.items[SEAL]["groups"] = frozenset("d")
        report = corrections.confirm(db, {"journal": "2.0.11", "date": "2026-11-18", "items": {
            HOOD: self.seen("Gorosh the Dervish", "Blackrock Depths", 10.3),
            BELT: self.seen("Zul'Alai", "The Drowned City", 34.2),
            GEM: self.seen("Arcanist Doan", "Scarlet Monastery: Library", 29.2),
            CHARM: self.seen("Kirtonos the Herald", "Scholomance", 24),
            SEAL: self.seen("Bonesnout the Unbroken", "Blackmaw Hold", 34.8),
            RELIC: self.seen("Fel Steed / Shadow Charger", "Shadowfang Keep", 18.6),
            CLOAK: self.seen("Zul'Alai", "The Drowned City", 34.2)}})
        self.assertEqual(db.items[HOOD]["sources"], [["d", "230", "Gorosh the Dervish", "10.3", "0", "w"]])
        self.assertEqual(db.items[HOOD]["groups"], frozenset("d"), "no longer a world drop")
        self.assertEqual(db.items[BELT]["sources"], [["d", "2970", "Zul'Alai", "34.2", "0", "w"]],
                         "the journal names the creature the data could not, in a dungeon the data lacked")
        self.assertEqual(db.items[GEM]["sources"], [["d", "189", "Arcanist Doan", "29.2", "0", "w"], ["w", "0", "0", "k"]],
                         "the rate the data lacks is the one counted")
        self.assertEqual(db.items[GEM]["groups"], frozenset("dw"), "a world drop while another source says so")
        self.assertEqual(db.items[CHARM]["sources"], [["d", "289", "Kirtonos", "24", "0", "w"]],
                         "one boss under two names is one source")
        self.assertEqual(db.items[SEAL]["sources"], [["d", "2974", "Bonesnout the Unbroken", "34.8", "0", "w"]])
        self.assertEqual(db.items[RELIC]["sources"], [["d", "33", "Fel Steed", "8.24", "0", "s"]],
                         "what ForeverDB saw keeps its rate and its label")
        self.assertEqual(db.items[CLOAK]["sources"], [["m", "1", "NPC 1", "0", "s"], ["m", "2", "NPC 2", "0", "s"]],
                         "nothing says which of two creatures the journal counted")
        self.assertEqual((sorted(report.placed), report.moved), (sorted((HOOD, BELT, GEM, CHARM, RELIC)), [SEAL]))
        self.assertEqual(sorted(report.dungeons), sorted(runs.DUNGEONS.values()))
        self.assertIn("For 5 of them a creature the data gives no place is written as a boss", "\n".join(luaout._drops_note(db)))
        # a tooltip names a creature and no dungeon: the creature stays one
        alone = self.db(HOOD=[["m", "7", "Mizzle the Crafty", "1", "c"]])
        corrections.confirm(alone, {"items": {HOOD: {"tooltip": {"boss": "Mizzle the Crafty", "percent": 2.5}}}})
        self.assertEqual(alone.items[HOOD]["sources"], [["m", "7", "Mizzle the Crafty", "2.5", "w"]])
        # a line that names the dungeon alone gives way to the one that names its boss
        self.assertEqual(corrections._one_per_boss([["d", "189", "", "0", "0", "s"], ["d", "189", "Ironspine", "33", "0", "s"],
                                                    ["d", "229", "", "0", "0", "s"]]),
                         [["d", "189", "Ironspine", "33", "0", "s"], ["d", "229", "", "0", "0", "s"]])

    def test_an_item_with_no_source_takes_the_bosses_counted(self):
        db = self.db()
        db.items[RELIC].update(added=True, phase=phases.LATER)   # a piece added from the game
        count = lambda boss, drops, percent: {"boss": boss, "dungeon": "Shaper's Terrace", "drops": drops, "kills": 116,
                                              "percent": percent}
        report = corrections.confirm(db, {"journal": "2.0.11", "date": "2026-11-18", "items": {
            HOOD: {"seen": [count("Thunderhoof", 38, 32.8), count("Bolt / Cinder", 5, 4.3), count("A Stray", 1, 0.9)]},
            BELT: self.seen('\\"Pyromancer\\" Braxton', "Halls of Nowhere", 44.9),
            GEM: {"tooltip": {"boss": "Thora Feathermoon", "percent": 6.24}},
            CHARM: self.seen("Pusillin", "Dire Maul: East", 24.4, drops=2),
            RELIC: self.seen("Blazeroar", "Alcaz Prison", 28.6)}})
        hood = db.items[HOOD]
        self.assertEqual(hood["sources"], [["d", "3001", "Thunderhoof", "32.8", "0", "w"], ["d", "3001", "Bolt", "4.3", "0", "w"]],
                         "every boss counted often enough, the likeliest first")
        self.assertEqual((hood["groups"], phases.item_phase(hood)), (frozenset("d"), phases.PRE_RAID))
        self.assertEqual(db.items[BELT]["sources"], [["m", "0", '"Pyromancer" Braxton', "44.9", "w"]],
                         "a dungeon nothing has: the boss, as a creature")
        self.assertEqual((db.items[GEM]["sources"], db.items[GEM]["groups"]), ([], frozenset("u")),
                         "a tooltip names a creature and no place")
        self.assertEqual(db.items[CHARM]["sources"], [], "two drops may be a stray record")
        relic = db.items[RELIC]
        self.assertEqual((relic["sources"], relic["groups"], relic["phase"]),
                         ([["d", "2994", "Blazeroar", "28.6", "0", "w"]], frozenset("d"), phases.PRE_RAID),
                         "a piece added from the game gets the source counted, and is a dungeon's item from then on")
        self.assertEqual(report.settled, [RELIC])
        self.assertEqual((report.sourced, report.items, report.moved, report.placed), ([HOOD, BELT, RELIC], [], [], []))
        self.assertTrue(report.changed)
        # in the lists: no longer an item of no known source
        db.classes["PRIEST"]["pools"]["head"] = [(HOOD, 60), (RELIC, 60)]
        for item_id in (HOOD, RELIC):
            db.gear[item_id] = {"inv": 1, "kind": "4.1", "req": 60, "stats": {45: 10}, "dps": 0.0, "armor": 0.0, "wand": False}
        ladder = {entry.item_id: entry for entry in ladders.full_ladder(db, "PRIEST", 1, "pve", "head")}
        self.assertEqual([(ladder[item_id].unsourced, ladder[item_id].phase) for item_id in (HOOD, RELIC)],
                         [(False, phases.PRE_RAID), (False, phases.PRE_RAID)], "the added piece like the listed one")
        text = luaout.items_file(db, ladders.build_all(db))
        self.assertIn(f"\n{HOOD}|Hood of Tests|d||d^3001^Thunderhoof^32.8^0^w~d^3001^Bolt^4.3^0^w\n", text)
        self.assertIn("3 items it gives no source take the bosses counted for them", text)

    def test_the_counts_say_the_wing_of_a_boss(self):
        self.assertEqual(runs.wing_key("Dire Maul: North"), (429, "n"))
        self.assertIsNone(runs.wing_key("Scholomance"))
        reading = {"items": {
            HOOD: self.seen("Pyroguard Emberseer", "Upper Blackrock Spire", 15.6),
            BELT: self.seen("Ras Frostwhisper", "Scholomance", 20),
            GEM: self.seen("Guard Mol'dar / Guard Slip'kik", "Dire Maul: North", 4.8),
            CHARM: self.seen("Wandering Ogre", "Dire Maul: North", 2),
            SEAL: self.seen("Wandering Ogre", "Dire Maul: West", 3)}}
        wings = runs.boss_wings(reading)
        self.assertEqual(runs.wing_of(wings, 229, "Pyroguard Emberseer"), "u")
        self.assertEqual(runs.wing_of(wings, 429, "Guard Slip'kik"), "n", "a line of the journal may name two bosses")
        self.assertEqual(runs.wing_of(wings, 429, "Wandering Ogre"), "", "counted in two wings: in neither for sure")
        self.assertEqual(runs.wing_of(wings, 229, "Lord Valthalak"), "u", "the counts say nothing of him: written by hand")
        self.assertEqual(runs.wing_of(wings, 229, "Warchief Rend"), "",  "nobody of that name")
        self.assertEqual(runs.wing_of(wings, 289, "Ras Frostwhisper"), "", "Scholomance has no wing")
        self.assertEqual(runs.wing_of(wings, 229, ""), "")
        # two spellings of one boss
        self.assertEqual(runs.wing_of({229: {"pyroguard emberseer": "u"}}, 229, "Pyroguard"), "u")
        db = self.db()
        corrections.confirm(db, reading)
        self.assertEqual(db.boss_wings, wings, "kept for the data files")
        for instance, bosses in runs.BOSS_WINGS.items():
            self.assertLessEqual(set(bosses.values()), set(runs.WINGS[instance]), instance)

    def quest_db(self):
        db = sourceless_db()
        db.instances[533] = ["Naxxramas", "raid"]
        db.items[HOOD]["sources"] = [["q", "700", "A Dungeon Errand", "55", "h", "t"], ["q", "701", "An Errand", "50", "", "t"]]
        db.items[GEM]["sources"] = [["q", "703", "A Raid Errand", "60", "", "t"], ["v", "5", "A Vendor", "", "", "", "", "", "s"]]
        return db

    def test_the_dungeon_of_a_quest_is_read_in_questiedb(self):
        rows = {**QUESTIE_ROWS, ("Quest", 703, "S"): {1: "A Raid Errand", 4: 60, 5: 60, 17: 3456}}
        with tempfile.TemporaryDirectory() as folder:
            store = questie.Store(questie_addon(Path(folder) / "QuestieDB", rows))
            reading = runs.collect_quests(self.quest_db(), store, today="2026-11-20")
            self.assertEqual(reading, {"questiedb": "9.9.9", "date": "2026-11-20", "quests": {
                700: {"name": "A Dungeon Errand", "instance": 47}, 703: {"name": "A Raid Errand", "instance": 533}}},
                "a quest of the open world is no dungeon's")
            path = Path(folder) / "quests.json"
            self.assertEqual(runs.load_quests(path), {})
            runs.save_quests(reading, path)
            written = path.read_bytes()
            self.assertNotIn(b"\r", written)
            self.assertIn('\n    "700": {"instance": 47, "name": "A Dungeon Errand"}', written.decode("utf-8"), "one quest per line")
            self.assertEqual(runs.load_quests(path), {**reading, "about": runs.ABOUT})
        db = self.quest_db()
        self.assertEqual(runs.quest_places(db, reading), {700: (47, "")}, "a raid is not run again and again")
        self.assertEqual(runs.quest_places(db, {}), {})
        # the wing is written by hand, and only a wing of that instance counts
        db.instances[229] = ["Blackrock Spire", "dungeon"]
        with mock.patch.dict(runs.QUEST_WINGS, {700: "u", 4903: "l"}, clear=True), \
                mock.patch.dict(runs.QUEST_INSTANCES, {4903: 229}, clear=True):
            self.assertEqual(runs.quest_places(db, reading), {700: (47, ""), 4903: (229, "l")})

    def test_the_data_files_name_the_wings_and_the_dungeon_quests(self):
        db = self.quest_db()
        db.instances[229] = ["Blackrock Spire", "dungeon"]
        db.items[BELT].update(groups=frozenset("d"), sources=[["d", "229", "Pyroguard Emberseer", "20", "0", "k"],
                                                              ["d", "229", "A Stray Orc", "1", "0", "k"]])
        db.classes["PRIEST"]["pools"]["head"] = [(HOOD, 60), (BELT, 60)]
        for item_id in (HOOD, BELT):
            db.gear[item_id] = {"inv": 1, "kind": "4.1", "req": 60, "stats": {45: 10}, "dps": 0.0, "armor": 0.0, "wand": False}
        corrections.confirm(db, {"journal": "2.0.11", "date": "2026-11-18", "items": {
            BELT: self.seen("Pyroguard Emberseer", "Upper Blackrock Spire", 15.6)}})
        db.quest_places = {700: (47, ""), 701: (229, "l"), 999: (229, "u")}
        text = luaout.items_file(db, ladders.build_all(db))
        self.assertIn('\nns.data.wings = {\n[229]="l^Lower Blackrock Spire|u^Upper Blackrock Spire^Pyroguard Emberseer",\n}\n',
                      text, "a boss nothing places is in no wing")
        self.assertIn('\nns.data.questRuns = {\n[700]="47",\n[701]="229:l",\n}\n', text, "the quests of the items written")
        self.assertIn('\n[47]="Razorfen Kraul^dungeon^1413^The Barrens",\n', text, "a quest's dungeon is named")
        self.assertNotIn("a creature the data gives no place", text, "none was placed")
        # no wing and no quest: two empty tables, which the addon reads as nothing
        plain = luaout.items_file(tiny_db(), ladders.build_all(tiny_db()))
        self.assertIn("\nns.data.wings = {\n}\n", plain)
        self.assertIn("\nns.data.questRuns = {\n}\n", plain)

    def test_the_build_imports_the_dungeon_quests(self):
        with tempfile.TemporaryDirectory() as folder:
            addon = questie_addon(Path(folder) / "QuestieDB", QUESTIE_ROWS)
            kept = Path(folder) / "quests.json"
            said = []
            with mock.patch.object(runs, "FILE", kept), \
                    mock.patch.object(build, "build", lambda details=False: 0), \
                    mock.patch.object(fdb, "load", lambda cache, corrected=True: self.quest_db()), \
                    mock.patch("builtins.print", lambda *words: said.append(" ".join(map(str, words)))):
                self.assertEqual(build.main(["--import-dungeon-quests", str(addon)]), 0)
                self.assertEqual(sorted(runs.load_quests(kept)["quests"]), [700])
                self.assertEqual(build.main(["--import-dungeon-quests", str(Path(folder) / "nowhere")]), 1)
            self.assertIn("1 quests of the data's items are sorted under an instance", said[0])
            self.assertIn("No QuestieDB_Forever.toc", said[-1])

    def test_the_real_data_places_its_runs(self):
        db = fdb.load(CACHE)
        for quest, (instance, wing) in db.quest_places.items():
            self.assertEqual(db.instances[instance][1], "dungeon", quest)
            self.assertTrue(wing == "" or wing in runs.WINGS[instance], quest)
        self.assertLessEqual({quest for quest in runs.QUEST_WINGS}, set(db.quest_places), "a quest written by hand is placed")
        for name, number in runs.DUNGEONS.items():
            self.assertEqual(corrections._instance(db, name), number, name)
        text = luaout.items_file(db, ladders.build_all(db))
        # every wing the data files name is one of runs.WINGS, and no boss is in two
        for instance, value in re.findall(r'^\[(\d+)\]="([a-z]\^[^"]*)",$', text.split("ns.data.wings = {")[1].split("}")[0], re.M):
            bosses = [boss for wing in value.split("|") for boss in wing.split("^")[2:]]
            self.assertEqual(len(bosses), len(set(bosses)), instance)
            self.assertEqual([wing.split("^")[0] for wing in value.split("|")], list(runs.WINGS[int(instance)]))
        # no item is said to drop twice from one boss of one dungeon
        for line in text.split("ns.data.items = [==[")[1].split("]==]")[0].splitlines():
            drops = [source.split("^") for source in line.split("|")[-1].split("~") if source.startswith("d^")]
            for index, source in enumerate(drops):
                for other in drops[:index]:
                    self.assertFalse(other[1] == source[1] and source[2] and corrections._same_boss(other[2], source[2]), line)


class ConsumableListTest(unittest.TestCase):
    TITANS, WISDOM, SUPREME_POWER, NATURAL_SWIFTNESS = 13510, 13511, 13512, 274276
    ELEMENTAL_STONE, DENSE_STONE, WIZARD_OIL = 18262, 12404, 20749
    MAJOR_MANA, REJUVENATION, MCWEAKSAUCE = 13444, 18253, 23579
    HEAVY_RUNECLOTH, ARATHI_BANDAGE, DRAUGHT = 14530, 20234, 17348
    ALTERAC_BANDAGE, MIGHTY_RAGE, IMBUE_FLAME, CRYOBLAST = 19307, 13442, 277500, 277499
    AGILITY_III, AGILITY_IV = 4425, 10309
    DENSE_WEIGHTSTONE, SOLID_STONE, SOLID_WEIGHTSTONE, HEAVY_STONE, HEAVY_WEIGHTSTONE = 12643, 7964, 7965, 2871, 3241

    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(CACHE)
        cls.lists = consumable_lists.build(cls.db)

    def shelf(self, token, spec, mode, category):
        return self.lists[token][spec][mode][category]

    def ranked(self, token, spec, mode, category):
        return [entry[0] for entry in self.shelf(token, spec, mode, category).ranked]

    def test_the_score_is_weight_times_stat(self):
        weights = {3: 1.0, 32: 0.5, "armor": 0.1, "dps": 5.0}
        self.assertEqual(consumable_lists.score({"stats": {"3": 25, "32": 28, "armor": 100, "7": 50}}, weights, "Melee DPS"), 49)

    def test_a_condition_counts_for_nothing(self):
        record = {"stats": {"7": 30}, "conditional": {"32": 28}, "condition": {"kind": "zone", "what": "Mount Hyjal"}}
        self.assertEqual(consumable_lists.score(record, {7: 1.0, 32: 1.0}, "Melee DPS"), 30)
        self.assertEqual(consumable_lists.effect(record), "+30 Stamina; +2% Critical Strike in Mount Hyjal only")

    def test_what_holds_for_spells_counts_for_casters(self):
        record = {"stats": {"45": 36}, "spell_stats": {"32": 14}}
        weights = {45: 1.0, 32: 1.0}
        self.assertEqual(consumable_lists.score(record, weights, "Caster DPS"), 50)
        self.assertEqual(consumable_lists.score(record, weights, "Melee DPS"), 36)

    def test_what_goes_on_a_melee_weapon_counts_for_melee(self):
        stone = {"stats": {"32": 28}, "text": "Increase critical chance on a melee weapon by 2% for 30 minutes."}
        for role, value in (("Melee DPS", 28), ("Tank", 28), ("Caster DPS", 0), ("Healer", 0), ("Ranged DPS", 0)):
            self.assertEqual(consumable_lists.score(stone, {32: 1.0}, role), value, role)

    def test_weapon_damage_counts_as_damage_per_second(self):
        stone = {"extras": {consumables.WEAPON_DAMAGE: 8}, "text": "Increase the damage of a blunt weapon by 8."}
        self.assertEqual(consumable_lists.score(stone, {"dps": 5.0}, "Melee DPS"), 5.0 * 8 / consumable_lists.WEAPON_SPEED)
        self.assertIn(self.DENSE_STONE, self.ranked("WARRIOR", 1, "pve", "weapon"))

    def test_shown_keeps_what_ties_with_the_last(self):
        entries = [(1, 0, 50), (2, 0, 40), (3, 0, 30), (4, 0, 30), (5, 0, 20)]
        self.assertEqual([entry[0] for entry in consumable_lists.shown(entries, 0)], [1, 2, 3, 4])
        later = [(1, 9, 50), (2, 0, 40), (3, 0, 30), (4, 0, 20), (5, 0, 10)]
        self.assertEqual([entry[0] for entry in consumable_lists.shown(later, 0)], [2, 3, 4])
        self.assertEqual([entry[0] for entry in consumable_lists.shown(later, 9)], [1, 2, 3])

    def test_every_spec_has_its_lists(self):
        for token, specs in self.lists.items():
            for spec, modes in specs.items():
                for mode in consumable_lists.MODES:
                    for category in ("flask", "elixir", "food", "scroll", "combat", "healing", "bandage"):
                        with self.subTest(token=token, spec=spec, mode=mode, category=category):
                            self.assertIn(category, modes[mode])

    def test_each_phase_shows_the_best_of_what_it_has(self):
        records = consumables.load()["items"]
        for token, spec, mode in (("WARRIOR", 2, "pve"), ("MAGE", 2, "pvp"), ("PRIEST", 2, "pve")):
            for category, shelf in self.lists[token][spec][mode].items():
                scores = [entry[2] for entry in shelf.ranked]
                self.assertEqual(scores, sorted(scores, reverse=True), category)
                self.assertTrue(all(not records[entry[0]].get("unread") for entry in shelf.ranked))

    def test_maximum_health_and_mana_are_listed_without_rank(self):
        for token, spec in (("WARRIOR", 3), ("MAGE", 2), ("PRIEST", 2)):
            flasks = self.shelf(token, spec, "pve", "flask")
            self.assertNotIn(self.TITANS, [entry[0] for entry in flasks.ranked])
            self.assertIn(self.TITANS, [item for item, _ in flasks.unranked])
        self.assertIn(self.WISDOM, [item for item, _ in self.shelf("MAGE", 2, "pve", "flask").unranked])

    def test_no_mana_for_who_has_none(self):
        for token in consumable_lists.NO_MANA:
            for spec, modes in self.lists[token].items():
                self.assertNotIn("mana", modes["pve"])
                self.assertNotIn(self.WISDOM, [item for item, _ in modes["pve"]["flask"].unranked])
        self.assertIn(self.MAJOR_MANA, self.ranked("MAGE", 2, "pve", "mana"))

    def test_a_potion_that_restores_both_is_on_both_lists(self):
        self.assertIn(self.REJUVENATION, self.ranked("MAGE", 2, "pve", "healing"))
        self.assertIn(self.REJUVENATION, self.ranked("MAGE", 2, "pve", "mana"))

    def test_the_condition_of_a_flask_stays_in_its_effect(self):
        rows = consumable_lists.info_rows(self.db, [self.NATURAL_SWIFTNESS])
        self.assertIn("Mount Hyjal", rows[self.NATURAL_SWIFTNESS][1])
        self.assertIn(self.NATURAL_SWIFTNESS, self.ranked("WARRIOR", 3, "pve", "flask"))

    def test_the_recipes_placed_by_hand_are_recipes_of_the_data(self):
        data = self.db.consumables
        origins = consumable_lists.load_origins()
        self.assertEqual(len(origins), 16)
        for item, origin in origins.items():
            with self.subTest(item=item):
                self.assertEqual(data.catalogue[item]["name"], origin["name"])
                self.assertEqual(bool(data.recipes.get(item)), "container" not in origin, "a recipe makes it, or it is held")
                self.assertEqual(len(set(origin) & {*consumable_lists._ORIGIN_SAID, "container"}), 1, "one way to have it")

    def test_where_a_recipe_placed_by_hand_is_learned(self):
        said = {item: row[2] for item, row in consumable_lists.info_rows(self.db, [249870, 250071, 13446, 286152]).items()}
        self.assertEqual(said[249870], "Cooking 250: recipe drops from Deadwind Ogre Mage (Deadwind Pass)")
        self.assertEqual(said[250071], "Cooking 275: recipe from the quest Now We're Cooking (Mount Hyjal)")
        self.assertEqual(said[13446], "First Aid 275: recipe sold by Pexmit (Mount Hyjal)")
        self.assertEqual(said[286152], "Cooking 225: recipe found in Deadwind Pass")

    def test_what_players_cannot_get_is_not_listed(self):
        left_out = consumable_lists.unobtainable()
        self.assertEqual(left_out, {23684, 23578, 23579, 13460})
        self.assertFalse(left_out & consumable_lists.used_ids(self.lists, consumable_lists.situational(self.db)))
        self.assertIn(self.NATURAL_SWIFTNESS, self.ranked("WARRIOR", 3, "pve", "flask"), "an unknown source is not a reason")

    def test_a_scroll_held_in_a_bundle(self):
        scroll = 277492
        self.assertEqual(consumable_lists.info_rows(self.db, [scroll])[scroll][2], "Container: Bundle of Scrolls")
        bosses = consumable_lists._raid_bosses(self.db)
        self.assertEqual(consumable_lists.item_phase(scroll, self.db.consumables, bosses), phases.PRE_RAID)
        self.assertEqual(consumable_lists.item_phase(277499, self.db.consumables, bosses), phases.LATER, "nothing says where this one is")

    def test_the_data_goes_before_a_recipe_placed_by_hand(self):
        recipe = {"profession": "Alchemy", "skill": 300, "learned": "i7"}
        data = types.SimpleNamespace(recipes={5: [recipe]}, facts={7: {"drops": ["A Named Boss"]}})
        self.assertEqual(consumable_lists.where(5, data, {5: {"drops": "Somebody Else"}}),
                         "Alchemy 300: recipe drops from A Named Boss")

    def test_an_unknown_recipe_does_not_hide_a_known_source(self):
        rows = consumable_lists.info_rows(self.db, [9030, 274276])
        self.assertEqual(rows[9030][2], "Quest: Uldaman Reagent Run")
        self.assertEqual(rows[274276][2], "Alchemy 300: recipe, source unknown")

    def test_what_is_tied_to_a_zone_says_so(self):
        rows = consumable_lists.info_rows(self.db, [19066, self.NATURAL_SWIFTNESS, 13446])
        self.assertEqual(rows[19066][4], "only:Warsong Gulch")
        self.assertEqual(rows[self.NATURAL_SWIFTNESS][4], "bonus:Mount Hyjal, Hyjal Summit, and the Barrow Deeps")
        self.assertEqual(rows[13446][4], "")
        slayer = {"conditional": {"38": 45}, "condition": {"kind": "creature", "what": "Demons"}}
        self.assertEqual(consumable_lists.zone_rule(slayer), "", "a kind of creature is not a place")

    def test_what_works_in_one_place_is_for_the_pvp_list(self):
        self.assertNotIn(self.DRAUGHT, self.ranked("MAGE", 2, "pve", "healing"))
        self.assertIn(self.DRAUGHT, self.ranked("HUNTER", 2, "pvp", "healing"))

    def test_a_tie_goes_to_what_works_everywhere(self):
        ranked = self.ranked("HUNTER", 2, "pvp", "bandage")
        self.assertIn(self.HEAVY_RUNECLOTH, ranked)
        self.assertNotIn(self.ARATHI_BANDAGE, ranked)

    def test_a_bandage_for_one_battleground_is_not_for_the_pve_list(self):
        for token, specs in self.lists.items():
            for spec in specs:
                self.assertNotIn(self.ALTERAC_BANDAGE, self.ranked(token, spec, "pve", "bandage"), (token, spec))

    def test_what_a_class_cannot_use_is_not_listed_for_it(self):
        records = consumables.load()["items"]
        for token, specs in self.lists.items():
            for spec, modes in specs.items():
                for mode, shelves in modes.items():
                    for category, shelf in shelves.items():
                        for item in [entry[0] for entry in shelf.ranked] + [item for item, _ in shelf.unranked]:
                            allowed = records[item].get("classes", [token])
                            self.assertIn(token, allowed, (token, spec, mode, category, item))
        self.assertIn(self.MIGHTY_RAGE, self.ranked("WARRIOR", 2, "pve", "combat"))
        self.assertNotIn(self.MIGHTY_RAGE, self.ranked("PALADIN", 3, "pve", "combat"))
        self.assertIn(self.IMBUE_FLAME, self.ranked("MAGE", 2, "pve", "weapon"))
        self.assertNotIn(self.IMBUE_FLAME, self.ranked("WARLOCK", 3, "pve", "weapon"))

    def test_situational_holds_what_the_class_can_use(self):
        self.assertIn(self.CRYOBLAST, dict(consumable_lists.situational(self.db, "MAGE")))
        self.assertNotIn(self.CRYOBLAST, dict(consumable_lists.situational(self.db, "WARRIOR")))
        self.assertIn(self.CRYOBLAST, dict(consumable_lists.situational(self.db)), "the data's rows hold every class's")

    def test_an_item_the_game_holds_twice_is_listed_once(self):
        records = {1: {"name": "Steak"}, 2: {"name": "Steak"}, 4: {"name": "Soup"}}
        entries = [(1, 0, 150), (2, 9, 150), (4, 0, 150)]
        self.assertEqual(consumable_lists._distinct(entries, records), [(1, 0, 150), (4, 0, 150)])
        names = consumables.load()["items"]
        for token, specs in self.lists.items():
            for spec, modes in specs.items():
                for mode, shelves in modes.items():
                    for category, shelf in shelves.items():
                        listed = [(names[entry[0]]["name"], entry[2]) for entry in shelf.ranked]
                        self.assertEqual(len(listed), len(set(listed)), (token, spec, mode, category))

    def test_a_weaker_rank_gives_way_to_the_stronger_one(self):
        records = {1: {"name": "Scroll of Agility IV"}, 2: {"name": "Scroll of Agility III"}, 3: {"name": "Scroll of Wit IV"},
                   4: {"name": "Scroll of Wit III"}}
        entries = [(1, 0, 170), (2, 0, 130), (3, 9, 160), (4, 0, 120)]
        self.assertEqual(consumable_lists._distinct(entries, records), [(1, 0, 170), (3, 9, 160), (4, 0, 120)],
                         "Wit III stays for the phases before Wit IV")
        self.assertNotIn(self.AGILITY_III, self.ranked("ROGUE", 2, "pve", "scroll"))
        self.assertIn(self.AGILITY_IV, self.ranked("ROGUE", 2, "pve", "scroll"))

    def test_no_list_shows_two_ranks_of_a_scroll(self):
        names = consumables.load()["items"]
        for token, specs in self.lists.items():
            for spec, modes in specs.items():
                for mode, shelves in modes.items():
                    for phase in phases.PHASES:
                        listed = [names[entry[0]]["name"].rsplit(" ", 1)[0] for entry in
                                  consumable_lists.shown(shelves["scroll"].ranked, phase)]
                        self.assertEqual(len(listed), len(set(listed)), (token, spec, mode, phase))

    def test_a_sharp_and_a_blunt_stone_share_a_place(self):
        entries = [(1, 0, 50), (2, 0, 50), (3, 0, 40), (4, 0, 30), (5, 0, 30), (6, 0, 20)]
        self.assertEqual([entry[0] for entry in consumable_lists.shown(entries, 0, twins=frozenset({2, 5}))], [1, 2, 3, 4, 5])
        shelf = self.shelf("PALADIN", 3, "pve", "weapon")
        self.assertEqual(shelf.twins, frozenset({self.DENSE_WEIGHTSTONE, self.SOLID_WEIGHTSTONE, self.HEAVY_WEIGHTSTONE}))
        shows = lambda phase: [entry[0] for entry in consumable_lists.shown(shelf.ranked, phase, twins=shelf.twins)]
        self.assertEqual(shows(phases.PRE_RAID), [self.DENSE_STONE, self.DENSE_WEIGHTSTONE, self.SOLID_STONE,
                                                  self.SOLID_WEIGHTSTONE, self.HEAVY_STONE, self.HEAVY_WEIGHTSTONE])
        self.assertEqual(shows(phases.LATER), [self.DENSE_STONE, self.DENSE_WEIGHTSTONE, self.ELEMENTAL_STONE,
                                               self.SOLID_STONE, self.SOLID_WEIGHTSTONE])

    def test_the_phase_of_a_consumable(self):
        data, bosses = self.db.consumables, consumable_lists._raid_bosses(self.db)
        phase = lambda item: consumable_lists.item_phase(item, data, bosses)
        self.assertEqual(phase(self.ELEMENTAL_STONE), phases.raid_phase("mc"), "its recipe drops from Molten Core's bosses")
        self.assertEqual(phase(self.REJUVENATION), phases.PRE_RAID, "a quest gives it too")
        self.assertEqual(phase(self.MCWEAKSAUCE), phases.LATER, "no known source")
        self.assertEqual(phase(self.TITANS), phases.PRE_RAID, "a dungeon boss drops the recipe")

    def test_situational_is_listed_without_rank(self):
        listed = dict(consumable_lists.situational(self.db))
        names = consumable_lists.info_rows(self.db, listed)
        found = {row[0] for row in names.values()}
        self.assertLessEqual({"Limited Invulnerability Potion", "Greater Fire Protection Potion", "Free Action Potion"}, found)
        self.assertFalse([name for name in found if name.startswith("Potion of Experience")],
                         "a potion that gives levels is nothing to bring to a fight at the level cap")

    def test_the_tooltips_to_read_include_what_the_tab_names(self):
        self.assertLessEqual(set(consumables.ALWAYS_READ), set(consumables.consumable_ids(self.db.consumables)))

    def test_the_data_file(self):
        text = luaout.consumables_file(self.db)
        self.assertTrue(text.startswith(self.db.header))
        self.assertNotRegex(text.lower().replace("easy bis", ""), r"\bbis\b|best set|optimal")
        info = {int(number) for number in re.findall(r"^(\d+)\|", text, re.M)}
        named = {int(number) for number in re.findall(r"(?:^|[\t ])(\d+)(?::\d*:\d+|:\d+)?(?= |$)", text, re.M)
                 if int(number) > 100}
        self.assertLessEqual(consumable_lists.used_ids(self.lists), info)
        self.assertTrue(info)
        self.assertTrue(named)
        for line in re.findall(r"^\d+\|.*$", text, re.M):
            self.assertEqual(line.count("|"), 5, line)

    def test_every_difference_with_the_coach_has_a_reason(self):
        compared, found = consumable_lists.coach_differences(self.db, self.lists)
        self.assertGreater(compared, 0)
        self.assertLess(len(found), compared)
        for difference in found:
            self.assertTrue(difference.why, difference.line())


class PricesTest(unittest.TestCase):
    """What the vendors ask in a currency, and who they sell to (corrections.price)."""
    PIX, REAL = 227853, 226404
    CLOAK, BELT = 272411, 272393   # a piece ForeverDB keeps for the Horde; one it gives no source for
    RELICS = {228175, 228176, *range(272427, 272437)}
    CRATE = 272151   # sold for 5 Reals, seen at the vendor: no piece of gear, so not in the data

    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(CACHE)
        cls.published = fdb.load(CACHE, corrected=False)
        cls.costs = corrections.load_costs()

    def flag(self, item_id) -> str:
        """What follows a price in the data: nothing once the vendor's window has shown it."""
        return "" if "build" in self.costs["vendors"][self.PIX]["items"][item_id] else ":b"

    def sold_by_pix(self, item) -> list:
        return [source for source in item["sources"] if source[0] in ("V", "v") and source[1] == str(self.PIX)]

    def test_the_vendor_of_the_reals_sells_to_both_factions(self):
        self.assertEqual(self.published.items[self.CLOAK]["side"], "h", "the data changed: this may have retired")
        sold = [item for item in self.db.items.values() if self.sold_by_pix(item)]
        self.assertGreaterEqual(len(sold), 24)
        for item in sold:
            self.assertEqual(item["side"], "", item["name"])
            for source in self.sold_by_pix(item):
                self.assertEqual(source[{"V": 3, "v": 7}[source[0]]], "", item["name"])

    def test_every_price_is_on_its_item(self):
        prices = self.costs["vendors"][self.PIX]["items"]
        self.assertGreaterEqual(len(prices), 38)
        for item_id, record in prices.items():
            item = self.db.items.get(item_id)
            if item is None:
                continue
            self.assertEqual(item["name"], record["name"])
            for source in self.sold_by_pix(item):
                self.assertEqual(source[{"V": 2, "v": 6}[source[0]]], f"{self.REAL}:{record['price']}{self.flag(item_id)}", item["name"])
        self.assertEqual(set(self.db.priced.absent), self.RELICS | {self.CRATE}, "the data has no entry for a relic")
        self.assertEqual(len(self.db.priced.items), 25)

    def test_the_data_file_says_the_price_and_the_currency(self):
        text = luaout.items_file(self.db, ladders.build_all(self.db))
        self.assertIn(f"{self.CLOAK}|Arcanoweave Cloak|v|sn|v^{self.PIX}^Pix Xizzix^1434^28.5^75.8^{self.REAL}:75{self.flag(self.CLOAK)}^^s", text)
        self.assertIn(f"{self.BELT}|Magician's Cord|v|n|v^{self.PIX}^Pix Xizzix^1434^28.52^75.86^{self.REAL}:100{self.flag(self.BELT)}^^t", text)
        self.assertIn(f'[{self.REAL}]="3469^Tarnished Undermine Real",', text)

    def test_a_price_moves_no_score(self):
        """The lists rank on stats: the same pieces come in the same order, with the same scores."""
        with mock.patch.object(corrections, "load_costs", return_value={}):
            unpriced = fdb.load(CACHE)
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for slot, _ in ladders.SLOTS:
                    ours, theirs = (ladders.full_ladder(db, token, spec, "pve", slot) for db in (self.db, unpriced))
                    self.assertEqual([(e.item_id, e.stored) for e in ours], [(e.item_id, e.stored) for e in theirs])

    def test_only_what_the_neutral_vendor_alone_sells_is_opened(self):
        def vendor(npc):
            return ["V", str(npc), "0", "h", "s"]

        def item(sources, twin=None):
            return {"name": "Piece", "side": "h", "twin": twin, "sources": sources}

        db = types.SimpleNamespace(items={
            1: item([vendor(5)]), 2: item([vendor(5)], twin=9), 3: item([vendor(5), vendor(6)]),
            4: item([vendor(6)]), 5: item([["d", "1", "Boss", "1", "0", "s"]]), 6: item([]),
        })
        costs = {"date": "today", "currencies": {7: {"name": "Coin", "currency": 8}},
                 "vendors": {5: {"neutral": True, "paid_in": 7, "items": {1: {"price": 3}, 4: {"price": 3}}}}}
        report = corrections.price(db, costs)
        self.assertEqual(report.freed, [1])
        self.assertEqual({key: db.items[key]["side"] for key in db.items}, {1: "", 2: "h", 3: "h", 4: "h", 5: "h", 6: "h"})
        self.assertEqual(db.items[1]["sources"], [["V", "5", "7:3:b", "", "s"]])
        self.assertEqual((report.items, report.absent, list(report.currencies)), ([1], [4], [7]))

    def test_a_price_read_at_the_vendor_is_not_the_betas_any_more(self):
        db = types.SimpleNamespace(items={1: {"name": "Piece", "side": "", "twin": None, "sources": [["V", "5", "0", "", "s"]]},
                                          2: {"name": "Piece", "side": "", "twin": None, "sources": [["V", "5", "0", "", "s"]]}})
        costs = {"currencies": {7: {"name": "Coin", "currency": 8}}, "vendors": {5: {"paid_in": 7, "items": {
            1: {"price": 3, "build": "1.0.0.1", "date": "2026-11-18"}, 2: {"price": 4}}}}}
        report = corrections.price(db, costs)
        self.assertEqual([db.items[key]["sources"][0][2] for key in (1, 2)], ["7:3", "7:4:b"])
        self.assertEqual((report.items, report.read), ([1, 2], [1]))

    def test_the_costs_file_is_written_as_it_was_read(self):
        written = corrections.COSTS_FILE.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "costs.json"
            corrections.save_costs(corrections.load_costs(), path)
            self.assertEqual(path.read_bytes(), written)


# What a vendor's window shows, in the stand-ins of the capture tool's game.
VENDOR_STUB = r"""
local stub = ...
stub.window, stub.timers = {}, {}
C_Timer = { After = function(_, callback) stub.timers[#stub.timers + 1] = callback end }
function UnitGUID() return stub.guid end
function UnitName() return "Pix Xizzix" end
function GetMerchantNumItems() return #stub.window end
function GetMerchantItemID(index) return stub.window[index].id end
function GetMerchantItemInfo(index)
    local row = stub.window[index]
    return row.name, 1, row.copper or 0, 1, -1, true, true, row.cost ~= nil
end
function GetMerchantItemCostInfo(index) return stub.window[index].cost and #stub.window[index].cost or 0 end
function GetMerchantItemCostItem(index, slot)
    local cost = stub.window[index].cost[slot]
    return 1, cost[1], cost[2], cost[3]
end
function stub.wait()
    local timers = stub.timers
    stub.timers = {}
    for _, callback in ipairs(timers) do callback() end
end
-- the tooltip of a row: its name, then "Requires <asks>" when the row has asks
function C_TooltipInfo.GetMerchantItem(index)
    local row = stub.window[index]
    if not row then return nil end
    local lines = { { leftText = row.name }, { leftText = "Requires Level 60" } }
    if row.asks then lines[#lines + 1] = { leftText = "Requires " .. row.asks } end
    return { lines = lines }
end
"""
REAL_LINK = "|cffffffff|Hitem:226404::::::::60:::::|h[Tarnished Undermine Real]|h|r"


@unittest.skipIf(lupa is None, "lupa is not installed")
class VendorToolTest(unittest.TestCase):
    """Capture.lua in front of a vendor's window."""
    GUID = "Creature-0-5250-0-1434-227853-00004F2A1B"   # kind-0-server-instance-zone-npc-spawn

    def setUp(self):
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)
        self.stub = self.lua.execute(CAPTURE_STUB)
        self.lua.eval("function(code, stub) assert(load(code))(stub) end")(VENDOR_STUB, self.stub)
        self.stub.guid = self.GUID
        self.source = (BUILD / "capture_addon" / "Capture.lua").read_text(encoding="utf-8")
        self.stub.run(self.source, "")

    def show(self, *rows):
        """Fills the window; a row is (item id, name, copper, costs), a cost (amount, link, name)."""
        table = self.lua.table_from
        self.stub.window = table([self.lua.table(
            id=item_id, name=name, copper=copper,
            cost=table([table(list(cost)) for cost in costs]) if costs is not None else None)
            for item_id, name, copper, costs in rows])

    def kept(self):
        db = self.lua.globals().EasyBISCaptureDB
        return db.vendors.v227853 if db and db.vendors else None

    def chat(self):
        return "\n".join(str(line) for line in self.stub.chat.values())

    def test_the_window_keeps_what_each_row_asks(self):
        """Only the window's tooltip says what the Alterac and Warsong quartermasters ask: it is kept, and read."""
        self.show((19325, "Don Rodrigo's Band", 0, [(2, REAL_LINK, "Real")]), (17348, "Major Healing Draught", 900, None))
        self.stub.window[1].asks = "Stormpike Guard - Exalted"
        self.stub.event(None, "MERCHANT_SHOW")
        db = self.lua.globals().EasyBISCaptureDB
        kept = db.asks.a227853
        self.assertEqual(kept.split("\n"), ["1|1.0.0|1|enUS|2026-11-15 12:30|Pix Xizzix", "17348\t",
                                            "19325\tStormpike Guard - Exalted"])
        self.assertIn("Pix Xizzix: 2 items read in the window, 1 of them ask for a reputation.", self.chat())
        self.assertIn("--import-reputations", self.chat())
        saved = ('EasyBISCaptureDB = {\n["asks"] = {\n["a227853"] = "' + kept.replace("\n", "\\n") + '",\n},\n'
                 '["vendors"] = {\n["v227853"] = "' + self.kept().replace("\n", "\\n") + '",\n},\n}\n')
        asks = capture.parse_asks(saved)
        self.assertEqual(asks[227853]["name"], "Pix Xizzix")
        self.assertEqual(asks[227853]["items"], {19325: "Stormpike Guard - Exalted", 17348: ""})
        self.assertEqual(set(capture.parse_vendors(saved)), {227853}, "the prices and the reputations do not mix")
        self.assertEqual(reputations.read_windows(asks), {19325: (730, 7), 17348: None})
        self.assertEqual(reputations.read_windows({1: {**asks[227853], "locale": "frFR"}}), {}, "English only")

    def test_a_window_that_asks_for_nothing_is_not_kept(self):
        self.show((17348, "Major Healing Draught", 900, None))
        self.stub.event(None, "MERCHANT_SHOW")
        db = self.lua.globals().EasyBISCaptureDB
        self.assertFalse(db and db.asks)
        self.assertNotIn("ask for a reputation", self.chat())

    def test_the_window_is_kept_as_the_importer_reads_it(self):
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]),
                  (272393, "Magician's Cord", 0, [(100, "|Hcurrency:3469:0|h[Real]|h", "Real")]),
                  (5, "Odd; Thing", 300, [(2, None, "Odd; Coin")]), (6, "Thread", 40, None))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertEqual(self.kept().split("\n"), [
            "1|1.0.0|1|enUS|2026-11-15 12:30|Pix Xizzix", "5\tOdd; Thing\t300\tnOdd  Coin:2", "6\tThread\t40\t",
            "272393\tMagician's Cord\t0\tc3469:100", "272411\tArcanoweave Cloak\t0\ti226404:75"])
        self.assertIn("Pix Xizzix: the prices of 4 items are kept.", self.chat())
        self.assertIn("--import-prices", self.chat())
        saved = 'EasyBISCaptureDB = {\n["vendors"] = {\n["v227853"] = "' + self.kept().replace("\n", "\\n") + '",\n},\n}\n'
        vendor = capture.parse_vendors(saved)[227853]
        self.assertEqual((vendor["name"], vendor["game"], vendor["locale"], vendor["date"]),
                         ("Pix Xizzix", "1.0.0.1", "enUS", "2026-11-15"))
        self.assertEqual(vendor["items"][272411], {"name": "Arcanoweave Cloak", "copper": 0, "costs": [("i", "226404", 75)]})
        self.assertEqual(vendor["items"][272393]["costs"], [("c", "3469", 100)])
        self.assertEqual(vendor["items"][5]["costs"], [("n", "Odd  Coin", 2)])
        self.assertEqual(vendor["items"][6], {"name": "Thread", "copper": 40, "costs": []})

    def test_what_the_game_has_not_said_is_waited_for(self):
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]), (272393, None, 0, [(100, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertNotIn("272393", self.kept())
        self.assertNotIn("are kept", self.chat(), "nothing is said while the window loads")
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]),
                  (272393, "Magician's Cord", 0, [(100, REAL_LINK, "Real")]))
        self.stub.wait()
        self.assertIn("272393\tMagician's Cord", self.kept())
        self.assertEqual(self.chat().count("are kept"), 1)

    def test_a_window_that_never_loads_says_so(self):
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]), (272393, "Magician's Cord", 0, [(0, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        for _ in range(12):
            self.stub.wait()
        self.assertIn("1 items of the window did not load", self.chat())
        self.assertEqual(len(self.stub.timers), 0, "it stops asking")

    def test_a_vendor_who_takes_only_money_is_not_kept(self):
        self.show((6, "Thread", 40, None))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertIsNone(self.kept())
        self.assertEqual(self.chat(), "")

    def test_the_windows_of_two_classes_add_up_in_one_game_build(self):
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.stub.event(None, "MERCHANT_CLOSED")
        self.show((272393, "Magician's Cord", 0, [(100, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertIn("272411\t", self.kept())
        self.assertIn("272393\t", self.kept())
        self.stub.event(None, "MERCHANT_CLOSED")
        self.stub.locale = "frFR"   # another reading of the game: what the other one said does not add up with it
        self.show((272393, "Magician's Cord", 0, [(100, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertNotIn("272411\t", self.kept())

    def test_a_filtered_window_says_so(self):
        globals_ = self.lua.globals()
        globals_.LE_LOOT_FILTER_ALL = 1
        globals_.GetMerchantFilter = self.lua.eval("function() return 2 end")
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.assertIn("The window is filtered", self.chat())

    def test_starting_a_capture_again_keeps_the_vendors(self):
        self.show((272411, "Arcanoweave Cloak", 0, [(75, REAL_LINK, "Real")]))
        self.stub.event(None, "MERCHANT_SHOW")
        self.lua.globals().SlashCmdList.EASYBISCAPTURE("all")
        self.assertIn("272411\t", self.kept())


class PriceImportTest(unittest.TestCase):
    """What the vendors' windows say of corrections/costs.json (capture.read_prices)."""

    def costs(self):
        return {"about": "test", "date": "2026-11-01", "currencies": {7: {"name": "Coin", "currency": 8}},
                "vendors": {5: {"name": "Pix", "neutral": True, "paid_in": 7, "items": {
                    1: {"name": "Same", "price": 10}, 2: {"name": "Dearer", "price": 10}, 3: {"name": "Unseen", "price": 10},
                    4: {"name": "Strange", "price": 10}}}}}

    @staticmethod
    def window(items, npc=5):
        rows = {item_id: {"name": name, "copper": copper, "costs": costs} for item_id, (name, copper, costs) in items.items()}
        return {npc: {"name": "Pix", "game": "1.60.1.70938", "locale": "frFR", "date": "2026-11-18", "items": rows}}

    def test_every_case_of_a_window(self):
        costs = self.costs()
        reading = capture.read_prices(costs, self.window({
            1: ("Pareil", 0, [("i", "7", 10)]), 2: ("Plus cher", 0, [("c", "8", 12)]), 4: ("Bizarre", 0, [("i", "99", 10)]),
            9: ("Nouveau", 0, [("n", "Coin", 30)]), 10: ("Fil", 40, []),
        }), {9: "New Piece"})
        items = costs["vendors"][5]["items"]
        self.assertEqual(reading.confirmed, [1])
        self.assertEqual(reading.changed, [(2, "Dearer", 10, 12)])
        self.assertEqual(reading.added, [(9, "New Piece", 30)])
        self.assertEqual(reading.other, [(4, "Strange", "10 of i99")])
        self.assertEqual(reading.unseen, [(3, "Unseen")])
        self.assertEqual(reading.read, 3)
        self.assertEqual(reading.unread, 2, "the one not shown and the one asked for in something else")
        read = {"build": "1.60.1.70938", "date": "2026-11-18"}
        self.assertEqual(items[1], {"name": "Same", "price": 10, **read}, "the English name stays")
        self.assertEqual(items[2], {"name": "Dearer", "price": 12, **read})
        self.assertEqual(items[3], {"name": "Unseen", "price": 10}, "not shown: neither read nor taken away")
        self.assertEqual(items[4], {"name": "Strange", "price": 10})
        self.assertEqual(items[9], {"name": "New Piece", "price": 30, **read})
        self.assertNotIn(10, items, "what only money buys is none of the file's business")
        self.assertEqual(costs["date"], "2026-11-18")

    def test_money_on_top_of_the_currency_is_not_a_price_the_file_can_say(self):
        costs = self.costs()
        reading = capture.read_prices(costs, self.window({1: ("Same", 500, [("i", "7", 10)])}))
        self.assertEqual((reading.read, reading.other), (0, [(1, "Same", "10 of i7, 500 copper")]))
        self.assertEqual(costs["date"], "2026-11-01")

    def test_a_vendor_the_file_does_not_have_is_named_and_left_out(self):
        costs = self.costs()
        reading = capture.read_prices(costs, self.window({1: ("Same", 0, [("i", "7", 10)])}, npc=6))
        self.assertEqual((reading.read, reading.strangers), (0, [(6, "Pix", 1)]))
        self.assertEqual(costs, self.costs())

    def saved(self, *rows):
        body = "\\n".join(("1|1.60.1|70938|enUS|2026-11-18 12:30|Pix",) + rows)
        return f'\nEasyBISCaptureDB = {{\n["vendors"] = {{\n["v5"] = "{body}",\n}},\n}}\n'

    def test_the_file_is_written_when_something_was_read(self):
        db = types.SimpleNamespace(items={})
        with tempfile.TemporaryDirectory() as folder:
            kept, saved = Path(folder) / "costs.json", Path(folder) / "EasyBIS_Capture.lua"
            corrections.save_costs(self.costs(), kept)
            before = kept.read_bytes()
            saved.write_text(self.saved("1\\tSame\\t0\\ti99:10"), encoding="utf-8")
            self.assertEqual(capture.import_prices(db, saved, kept).read, 0)
            self.assertEqual(kept.read_bytes(), before, "nothing read, nothing written")
            saved.write_text(self.saved("1\\tSame\\t0\\ti7:10"), encoding="utf-8")
            self.assertEqual(capture.import_prices(db, saved, kept).confirmed, [1])
            self.assertEqual(corrections.load_costs(kept)["vendors"][5]["items"][1]["build"], "1.60.1.70938")
            saved.write_text("EasyBISCaptureDB = nil\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                capture.import_prices(db, saved, kept)

    def test_the_vendors_do_not_pass_for_tooltips(self):
        text = self.saved("1\\tSame\\t0\\ti7:10").replace("EasyBISCaptureDB = {",
                                                               'EasyBISCaptureDB = {\n["meta"] = "1|1.0.0|1|enUS|2026-11-15 12:30",')
        self.assertEqual(capture.parse_saved(text)["items"], {})

    def test_the_saved_variable_with_the_vendors_is_found(self):
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder)
            self.assertIsNone(capture.find_vendors(game))
            for account, text in (("A", self.saved("1\\tSame\\t0\\ti7:10")), ("B", "EasyBISCaptureDB = nil\n")):
                path = game / "WTF" / "Account" / account / "SavedVariables" / capture.SAVED
                path.parent.mkdir(parents=True)
                path.write_text(text, encoding="utf-8")
            self.assertEqual(capture.find_vendors(game).parent.parent.name, "A")

    def test_an_unknown_format_asks_for_the_tool_again(self):
        with self.assertRaises(ValueError):
            capture.parse_vendors(self.saved().replace('"1|1.60.1', '"2|1.60.1'))


# -- how a reputation is earned, read in QuestieDB --------------------------------------------------------------

EARNING_ROWS = {
    # a chain whose two steps share a title: two quests
    ("Quest", 1, "S"): {1: "The Bloodsail Buccaneers", 4: 37, 17: 33, 22: 2}, ("Quest", 1, "26"): [[21, 75]],
    ("Quest", 2, "S"): {1: "The Bloodsail Buccaneers", 4: 37, 17: 33}, ("Quest", 2, "13"): [1],
    ("Quest", 2, "26"): [[21, 75]],
    # offered only below Neutral, and only at Exalted: listed last, counted nowhere
    ("Quest", 30, "S"): {1: "Traitor", 4: 40, 17: 33, 24: 1}, ("Quest", 30, "20"): [21, 0],
    ("Quest", 30, "26"): [[21, 499]],
    ("Quest", 31, "S"): {1: "Late", 4: 60, 17: 33}, ("Quest", 31, "19"): [21, 42000], ("Quest", 31, "26"): [[21, 200]],
    # the same repeatable quest at three givers: one
    **{key: value for number in (3, 4, 5) for key, value in (
        (("Quest", number, "S"), {1: "Scourgestones", 4: 50, 17: 28, 24: 1}), (("Quest", number, "13"), [9]),
        (("Quest", number, "26"), [[529, 25]]))},
    # a quest the game does not have, and one offered only below level 60
    ("Quest", 40, "S"): {1: "DND FLAG", 4: 60, 17: 1}, ("Quest", 40, "26"): [[529, 500]],
    ("Quest", 41, "S"): {1: "Bracket", 4: 30, 17: 1, 32: 39}, ("Quest", 41, "26"): [[529, 100]],
    # two paths that exclude one another, the first with a step after it: the path that gives the most counts
    ("Quest", 10, "S"): {1: "Path A", 4: 60, 17: 440}, ("Quest", 10, "16"): [20], ("Quest", 10, "26"): [[910, 100]],
    ("Quest", 11, "S"): {1: "Path A", 4: 60, 17: 440}, ("Quest", 11, "13"): [10], ("Quest", 11, "16"): [20],
    ("Quest", 11, "19"): [910, 3000], ("Quest", 11, "26"): [[910, 100]],
    ("Quest", 20, "S"): {1: "Path B", 4: 60, 17: 440}, ("Quest", 20, "16"): [10], ("Quest", 20, "26"): [[910, 150]],
    # a row with neither level nor zone beside the full quest: an unfinished copy
    ("Quest", 42, "S"): {1: "Clash", 4: 60, 17: 16606, 24: 1}, ("Quest", 42, "26"): [[2799, 100]],
    ("Quest", 43, "S"): {1: "Clash"}, ("Quest", 43, "26"): [[2799, 100]],
    # Forever's Skyborne of the Horde only
    ("Quest", 50, "S"): {1: "Moonglade", 4: 10, 17: 493, 6: 1 << 33}, ("Quest", 50, "26"): [[609, 25]],
}

BLACKLIST_LUA = """local QuestieQuestBlacklist = QuestieLoader:CreateModule("QuestieQuestBlacklist")
function QuestieQuestBlacklist:Load()
    local questsToBlacklist = {
        [40] = true, -- not in the game
        [7704] = Expansions.Current ~= Expansions.Wotlk, -- Only implemented in Wrath
        [8614] = Expansions.Current >= Expansions.Tbc,
        [78124] = HIDE_ON_MAP, -- Nar'thalas Almanac
        [1374] = Expansions.Current >= Expansions.Cata or Questie.IsForever, -- replaced on Forever
        [2358] = Expansions.Current == Expansions.Era or Expansions.Current >= Expansions.Wotlk,
        --[302] = true,
        [78132] = not Questie.IsSoD,
        [17] = false,
    }

    return questsToBlacklist
end
"""


class EarningTest(unittest.TestCase):
    def test_questies_list_is_read_as_on_forever(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertIsNone(reputations.hidden_quests(folder))
            path = Path(folder) / reputations.BLACKLIST
            path.parent.mkdir(parents=True)
            path.write_text(BLACKLIST_LUA, encoding="utf-8")
            self.assertEqual(reputations.hidden_quests(folder), {40, 7704, 1374, 2358, 78132})
            path.write_text(BLACKLIST_LUA.replace("[17] = false", "[17] = SomeCall(1)"), encoding="utf-8")
            with self.assertRaises(ValueError):
                reputations.hidden_quests(folder)

    def test_the_quests_one_character_can_do(self):
        with tempfile.TemporaryDirectory() as folder:
            store = questie.Store(questie_addon(Path(folder) / "QuestieDB", EARNING_ROWS))
            found = reputations.earning(store, hidden={40})
        rows = lambda faction: [row[:3] + row[5:] for row in found[faction]["methods"]]
        # the steps of a chain stay apart; what helps only below Neutral or at Exalted comes last
        self.assertEqual(rows(21), [["The Bloodsail Buccaneers", 75, 0, "", "", ""],
                                    ["The Bloodsail Buccaneers", 75, 0, "", "", ""],
                                    ["Traitor", 499, 1, "", 3, ""], ["Late", 200, 0, 7, "", ""]])
        self.assertEqual({name: found[21][name] for name in ("quests", "repeatable", "once")},
                         {"quests": 4, "repeatable": 0, "once": {"a": 150, "h": 150}})
        # one quest at three givers; the hidden one and the one below level 60 are left out
        self.assertEqual(rows(529), [["Scourgestones", 25, 1, "", "", ""]])
        # the paths: each step knows its branch, and the most one path gives counts
        self.assertEqual(rows(910), [["Path B", 150, 0, "", "", "10:20"], ["Path A", 100, 0, "", "", "10:10"],
                                     ["Path A", 100, 0, 4, "", "10:10"]])
        self.assertEqual(found[910]["once"], {"a": 200, "h": 200})
        # the unfinished copy is not a quest of its own
        self.assertEqual(rows(2799), [["Clash", 100, 1, "", "", ""]])
        # the Skyborne of the Horde are the Horde
        self.assertEqual(found[609]["methods"][0][3], "h")

    def test_a_battleground_faction_earned_elsewhere_stops_the_import(self):
        rows = dict(EARNING_ROWS)
        rows[("Quest", 42, "S")] = {**rows[("Quest", 42, "S")], 17: 1}
        with tempfile.TemporaryDirectory() as folder:
            store = questie.Store(questie_addon(Path(folder) / "QuestieDB", rows))
            with self.assertRaisesRegex(ValueError, "BATTLEGROUNDS"):
                reputations.earning(store)


class CapturedReputationTest(unittest.TestCase):
    PARSED = {"locale": "enUS", "game": "1.60.1.70959", "date": "2026-11-19", "items": {
        1: (["Sentinel's Chain Leggings", "Requires Level 60", "Requires Silverwing Sentinels - Honored"], {}),
        2: (["Outrider's Bow", "Requires Level 58"], {}),
        3: (["Night Claw", "Requires Nightclaw Druids - Friendly"], {}),
        4: (["Highlander's Pauldrons", "Requires The League of Arathor - Exalted"], {}),
        5: (["Stormpike Ring", "Requires Stormpike Guard - Revered"], {}),
    }}

    def test_the_tooltips_say_what_a_piece_asks(self):
        facts, others, plain = reputations.read_capture(self.PARSED)
        self.assertEqual(facts, {1: (890, 5), 4: (509, 7), 5: (730, 6)})
        self.assertEqual(others, {3: "Nightclaw Druids"})
        self.assertEqual(plain, {2})
        self.assertEqual(reputations.read_capture({**self.PARSED, "locale": "frFR"}), ({}, {}, set()),
                         "the phrase is read in English only")

    def test_the_tooltips_against_the_data(self):
        reading = {"items": {2: [{"kind": "w", "faction": 889, "standing": 4}],
                             5: [{"kind": "q", "faction": 730, "standing": 5}]}}
        found = reputations.check_capture(self.PARSED, {4: (509, 6)}, reading)
        self.assertEqual(found["same"], [])
        self.assertEqual(found["differs"], [(4, (509, 6), (509, 7))])
        self.assertEqual([row[0] for row in found["missing"]], [1, 5], "a quest's gate is not the wearer's")
        self.assertEqual(found["extra"], [(2, (889, 4), None)])
        self.assertEqual(found["outside"], [(3, None, "Nightclaw Druids")])

    ATLAS = """
data["AlteracValley"] = {
	items = {
		{ -- Exalted
			name = ALIL["Exalted"],
			[ALLIANCE_DIFF] = {
				{ 1, "f730rep8" },
				{ 2, 19325 }, -- Don Rodrigo's Band
			},
			[HORDE_DIFF] = {
				{ 1, "f729rep8" },
				{ 2, 19325 }, -- Don Julio's Band
			},
		},
		{ -- Honored
			name = ALIL["Honored"],
			[HORDE_DIFF] = {
				{ 1, "f729rep6" },
				{ 2, 19083 }, -- Frostwolf Legionnaire's Cloak
			},
		},
		{
			name = "No standing",
			[NORMAL_DIFF] = {
				{ 1, 12345 },
			},
		},
		{
			name = ALIL["Revered"],
			[NORMAL_DIFF] = {
				{ 1, "f576rep7" },
				{ 2, 19218 },
				{ 3, "f576rep2" },
				{ 4, 999 },
			},
		},
	},
}
"""

    def test_atlasloot_tables_say_a_standing_per_side(self):
        found = reputations.read_atlasloot(self.ATLAS)
        self.assertEqual(found, {19325: {"a": (730, 7), "h": (729, 7)}, 19083: {"h": (729, 5)},
                                 19218: {"": (576, 6)}}, "a piece under no standing, or below Neutral, is left out")
        self.assertEqual(reputations.by_side(found[19325]), {"a": (730, 7), "h": (729, 7)})
        self.assertEqual(reputations.by_side(found[19083]), {"": (729, 5)}, "one side's piece")
        self.assertEqual(reputations.by_side({"a": (1234, 5), "h": (729, 5)}), {"": (729, 5)}, "FACTIONS only")
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(reputations.atlasloot(folder), ({}, ""))
            addon = Path(folder) / "AtlasLootClassic_PvP"
            addon.mkdir()
            (addon / "data.lua").write_text(self.ATLAS, encoding="utf-8")
            (addon / "AtlasLootClassic_PvP_Forever.toc").write_text("## Version: Forever 1.60.1\n", encoding="utf-8")
            self.assertEqual(reputations.atlasloot(folder), (found, "AtlasLootClassic_PvP Forever 1.60.1"))

    def test_atlasloot_is_checked_against_the_other_sources(self):
        atlas = {1: {"a": (730, 7), "h": (729, 7)}, 2: {"": (889, 5)}, 3: {"": (890, 6)}}
        found = reputations.cross_check(atlas, {"foreverdb": {1: (729, 7), 2: (889, 6), 9: (21, 4)},
                                                "windows": {3: None}, "tooltips": {}})
        self.assertEqual(found["foreverdb"], {"agree": 1, "differ": [[2, [889, 6], {"": [889, 5]}]]})
        self.assertEqual(found["windows"], {"agree": 0, "differ": [[3, None, {"": [890, 6]}]]},
                         "a window that asks for none disagrees")
        lines = reputations.check_lines(found)
        self.assertEqual(len(lines), 2, "a source that speaks of none of AtlasLoot's pieces says nothing")
        self.assertTrue(lines[0].startswith("AtlasLoot against ForeverDB: 1 items agree, 1 differ (2 [889, 6]"))
        self.assertIn("3 none", lines[1])

    def test_atlasloot_fills_what_a_quartermaster_asks(self):
        class Store:
            zones = types.SimpleNamespace(ui_maps={})

            def ids(self, kind, item_id, field):
                return [13217, 13218] if item_id == 19325 else []

            def row(self, kind, npc):
                return {13217: {questie.NPC_NAME: "Thanthaldis Snowgleam"},
                        13218: {questie.NPC_NAME: "Grunnda Wolfheart"}}.get(npc, {})

            def table(self, kind, npc, field):
                return {}

        db = types.SimpleNamespace(vendors={13217: ["Thanthaldis Snowgleam", 1459, 50.0, 50.0]}, items={
            19325: {"sources": [["V", "13217", "0"]]},       # ForeverDB names the Alliance's quartermaster only
            19083: {"sources": [["V", "13219", "500"]]},
            30: {"sources": [["q", "7", "A quest"]]},          # not sold: AtlasLoot is not read for it
            31: {"sources": [["V", "99", "0"]]},
        })
        atlas = {19325: {"a": (730, 7), "h": (729, 7)}, 19083: {"h": (729, 5)}, 30: {"": (729, 5)},
                 31: {"": (1234, 5)}}
        reader = reputations._Reader(db, Store(), {}, {}, {}, None, atlas)
        base = {"kind": "w", "read": "atlasloot", "price": 0}
        self.assertEqual(reader.from_atlas(19325, db.items[19325]), [
            {**base, "side": "a", "faction": 730, "standing": 7, "vendor": 13217},
            {**base, "side": "h", "faction": 729, "standing": 7, "vendor": 13218}])
        self.assertEqual(reader.vendors[13218][0], "Grunnda Wolfheart", "QuestieDB names the Horde's")
        self.assertEqual(reader.from_atlas(19083, db.items[19083]),
                         [{**base, "side": "", "faction": 729, "standing": 5, "vendor": 13219, "price": 500}])
        self.assertEqual(reader.from_atlas(30, db.items[30]), [])
        self.assertEqual(reader.from_atlas(31, db.items[31]), [])
        self.assertEqual(reader.outside, {"1234": {31}})

    def test_what_the_build_cannot_place_is_reported(self):
        db = types.SimpleNamespace(items={
            10: {"sources": [["V", "14753", "0"]]},        # Silverwing's quartermaster, nothing says the requirement
            11: {"sources": [["V", "14753", "0"]]},        # the same, read in the game: it asks for one
            12: {"sources": [["V", "14753", "0"]]},        # the same, its tooltip says nothing: his window may
            13: {"sources": [["v", "15127", "", "", "", "", "0"]]},   # a vendor a requirement was read for
            14: {"sources": [["V", "99", "0"]]},           # any other vendor
            15: {"sources": [["q", "7", "A quest"]]},
        })
        reading = {"items": {11: [{"kind": "w", "faction": 890, "standing": 5, "vendor": 14753}],
                             20: [{"kind": "w", "faction": 509, "standing": 7, "vendor": 15127}]},
                   "outside": {"Nightclaw Druids": [15, "s9", 16], "1234": [99]}}
        outside, unasked = reputations.gaps(reading, db, shown={10, 11, 12, 13, 14, 15}, enchants={"s9"})
        self.assertEqual(outside, {"Nightclaw Druids": [15, "s9"]}, "only what the lists show")
        self.assertEqual(unasked, {890: [10, 12], 509: [13]})


if __name__ == "__main__":
    unittest.main(verbosity=1)
