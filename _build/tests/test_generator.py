"""Tests for the data generator.

    python -P tests/test_generator.py

The Lua test needs the `lupa` package and is skipped without it.
"""
from __future__ import annotations

import copy
import json
import os
import re
import sys
import tempfile
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
import corrections  # noqa: E402
import drops  # noqa: E402
import fdb  # noqa: E402
import ladders  # noqa: E402
import luaout  # noqa: E402
import phases  # noqa: E402
import questie  # noqa: E402

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
                    local id, score, flags, twin, limit = entry:match("^(%d+):(%d+):?([%a%d]*):?(%d*):?(.*)$")
                    out[#out + 1] = table.concat({ cls, spec, list, slot, id, score, flags, twin, limit }, ",")
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
        self.assertEqual(sum(len(data["specs"]) for data in self.db.classes.values()), 27)
        for token, data in self.db.classes.items():
            for spec in data["specs"].values():
                self.assertEqual(set(spec["weights"]), {"lvl", "raid", "pvp"}, f"{token} {spec['name']}")
        self.assertEqual(self.db.meta["cap"], 60)

    def test_every_pool_item_is_described(self):
        for token, data in self.db.classes.items():
            for pool in data["pools"].values():
                for item_id, _ in pool:
                    self.assertIn(item_id, self.db.gear, f"{token}: no stats for {item_id}")
                    self.assertIn(item_id, self.db.items, f"{token}: no source line for {item_id}")

    def test_matches_the_site(self):
        """Every slot of every page read from foreverdb.net/bis has the same picks."""
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(golden["build"], self.db.meta["build"],
                         "the golden pages were read for another game build: read them again")
        for page in golden["pages"]:
            with self.subTest(cls=page["cls"], spec=page["spec"], mode=page["mode"]):
                self.assertEqual(compare_site.compare(self.published, page), [])

    def test_pvp_rewards_are_marked(self):
        """Every entry says whether it is a PvP reward, so the addon can leave those out of a list: a PvP
        rank's, the honor quartermasters', a battleground's, a Premier set's."""
        is_reward = lambda item_id: ladders.pvp_reward(self.db.items[item_id])   # noqa: E731
        self.assertTrue(is_reward(16478), "Field Marshal's Plate Helm, of rank 13")
        self.assertTrue(is_reward(20057), "Highlander's Plate Spaulders, of Arathi Basin")
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
                groups = self.db.items[entry.item_id]["groups"]
                self.assertEqual(entry.unsourced, not (groups - {"u"}), f"{token} {spec} {mode} {slot}: {entry.item_id}")
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
            visible = {slot: [e for e in ladder_of(token, spec, mode, slot) if e.passes(flt)]
                       for slot, _ in ladders.SLOTS}
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
        seen = {"one": 0, "two": 0, "none": 0}
        for token, data in self.db.classes.items():
            for spec in data["specs"]:
                for mode in ladders.MODES:
                    for flt in ladders.FILTERS:
                        main = [e for e in self.full[(token, spec, mode, "main")] if e.passes(flt)]
                        off = [e for e in self.full[(token, spec, mode, "off")] if e.passes(flt)]
                        best_main, best_off = ladders.weapon_lists(main, off)
                        other_main, other_off = ladders.other_weapons(main, off)
                        self.assertFalse(set(best_main) & set(other_main))
                        if not other_main:
                            self.assertEqual(other_off, [])
                            seen["none"] += 1
                        elif best_main[0].two_hand:
                            self.assertTrue(all(not e.two_hand for e in other_main))
                            self.assertEqual(best_off, [])
                            self.assertNotIn(other_main[0].item_id, [e.item_id for e in other_off])
                            self.assertGreaterEqual(best_main[0].stored, other_main[0].stored
                                                    + (off[0].stored if off else 0))
                            seen["one"] += 1
                        else:
                            self.assertTrue(all(e.two_hand for e in other_main))
                            self.assertEqual(other_off, [])
                            seen["two"] += 1
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
                            fields = (luaout.encode_entry(entry).split(":") + [""] * 5)[:5]
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
        self.assertLessEqual(ranked, read, "a main-hand entry of a ladder is not on the capture's list")

    def test_the_lists_follow_what_the_game_has(self):
        """corrections.align on the real data: with the default options the lists only lose what the game lacks."""
        game = self.db.aligned
        if not game.build:
            self.skipTest("the game was not read yet (corrections/game.json)")
        pooled = {item_id for data in self.db.classes.values() for pool in data["pools"].values() for item_id, _ in pool}
        absent = set(corrections.load_game()["absent"])
        self.assertFalse(pooled & absent, "an item the game does not have is still in a pool")
        self.assertLessEqual(set(game.dropped), absent)
        for item_id in game.added:
            self.assertNotIn(item_id, self.published.items)
            self.assertIn(item_id, pooled)
            self.assertEqual((self.db.items[item_id]["groups"], self.db.items[item_id]["phase"]), (frozenset("u"), phases.LATER))
        self.assertFalse(set(game.added) & set(corrections.NOT_FOR_PLAYERS))
        shown = luaout.shown_ids(self.kept)
        self.assertFalse(shown & absent, "an item the game does not have is in a list, or is a list item's twin")
        self.assertTrue(shown & set(game.added), "no added piece makes a list")

        before = fdb.load(CACHE, corrected=False)
        corrections.apply(before, corrections.load())   # the weapons' stats, not the game's items
        corrections.fill(before, corrections.load_sources())   # ... and the sources read in QuestieDB
        was = ladders.build_all(before)
        gone = set(game.dropped)
        for token, specs in self.kept.items():
            for spec, modes in specs.items():
                for mode, slots in modes.items():
                    for flt in ladders.FILTERS:
                        if flt[1]:
                            continue   # with the items of no known source: the added pieces show there
                        now, then = audit.shown_rows(slots, flt), audit.shown_rows(was[token][spec][mode], flt)
                        for slot in now:
                            if now[slot] != then[slot]:
                                lost = {entry.item_id for rows in then[slot] for entry in rows} & gone
                                self.assertTrue(lost, f"{token} {spec} {mode} {slot} {flt} changed with nothing dropped")


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
function CreateFrame() return { SetScript = function(_, _, script) stub.script = script end } end
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
                                                   "unlisted": [ROBE], "twins": []})
        with tempfile.TemporaryDirectory() as folder:
            target, counts = capture.write_tool(db, folder)
            self.assertEqual((target.name, counts), ("EasyBIS_Capture", {"weapons": 4, "pool": 2, "unlisted": 1, "twins": 0}))
            self.assertEqual(sorted(path.name for path in target.iterdir()),
                             ["Capture.lua", "EasyBIS_Capture.toc", "Ids.lua"])
            # the raid piece first, the weapons last: the game may stop answering before the end
            self.assertIn("\n20 8 9 1 2 3 7\n", (target / "Ids.lua").read_text(encoding="utf-8"))
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
        self.assertEqual(check.asked, {"weapons": 4, "pool": 2, "unlisted": 1, "twins": 0})
        self.assertEqual(check.read, {"weapons": 2, "pool": 2, "unlisted": 1, "twins": 0})
        # the staff is not in the game's own item table: it was not asked for, and the report names it
        self.assertEqual(check.absent, {"weapons": [(STAFF, "Channeling Staff")], "pool": [], "unlisted": [], "twins": []})
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
        size = 1 if number < 256 else 2 if number < 65536 else 4
        return bytes([major << 5 | {1: 24, 2: 25, 4: 26}[size]]) + number.to_bytes(size, "big")
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
        elsewhere = {"boss": "Bonesnout the Unbroken", "dungeon": "Blackmaw Hold", "drops": 77, "kills": 221, "percent": 34.8}
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
        self.assertEqual(db.items[RELIC]["groups"], frozenset("u"), "a piece added from the game stays unsourced in the lists")
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


if __name__ == "__main__":
    unittest.main(verbosity=1)
