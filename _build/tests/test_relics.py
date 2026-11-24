"""Cover the class relics, their source and phase filters, and the actual Lua selection."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from zipfile import ZipFile

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
import fdb
import ladders
import luaout
import relics
import test_addon


class RelicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.catalog = relics.read()
        cls.lists = {}
        for token in relics.CLASSES:
            cls.lists[token] = {}
            for spec in cls.db.classes[token]["specs"]:
                modes = {}
                for mode in ladders.MODES:
                    slots = {slot: [] for slot, _ in ladders.SLOTS}
                    rows = ladders.full_ladder(cls.db, token, spec, mode, "ranged")
                    slots["ranged"] = ladders.kept_ladder("ranged", rows)
                    modes[mode] = slots
                cls.lists[token][spec] = modes

    def test_catalogue_and_native_evidence_are_complete_and_scoped(self):
        ids = set(map(int, self.catalog["items"]))
        self.assertEqual(len(ids), 46)
        self.assertEqual(len(self.catalog["profiles"]), 11)
        for key, profile in self.catalog["profiles"].items():
            for mode in ("pve", "pvp"):
                self.assertTrue(profile[mode])
                for item in profile[mode]:
                    self.assertEqual(self.catalog["items"][str(item)]["class"], key.split()[0])
            for item, measurements in profile.get("dps", {}).items():
                self.assertIn(int(item), profile["pve"])
                for gain, error in measurements.values():
                    self.assertGreater(gain, 0)
                    self.assertGreaterEqual(error, 0)
        with ZipFile(relics.FILE.parent / self.catalog["evidence_archive"]) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            self.assertEqual(manifest["wowsims"], self.catalog["wowsims"])
            self.assertEqual(len(manifest["batches"]), 16)
            for batch in manifest["batches"]:
                for key in ("input", "output"):
                    self.assertEqual(hashlib.sha256(archive.read(batch[key])).hexdigest(), batch[key + "_sha256"])
                outputs = json.loads(archive.read(batch["output"]))
                if batch["profile"] == "DRUID 4":
                    self.assertTrue(all(abs(row["CatSeconds"] - row["DurationSeconds"]) < 0.001
                                        and row["CatActivations"] == 0 for row in outputs))
                by_id = {row["key"]: row for row in outputs}
                for key, measurements in self.catalog["profiles"][batch["profile"]].get("dps", {}).items():
                    gain, error = measurements[batch["side"]]
                    self.assertAlmostEqual(by_id[key]["diff"], gain, places=5)
                    self.assertAlmostEqual(by_id[key]["se"], error, places=5)

    def test_preserves_foreverdb_records_and_adds_each_pool_item_only_once(self):
        isolated = copy.deepcopy(self.db)
        item = isolated.items[22397]
        item["name"] = "Name from an updated client"
        relics.apply(isolated)
        self.assertEqual(item["name"], "Name from an updated client")
        for token in relics.CLASSES:
            pool = [i for i, _ in isolated.classes[token]["pools"]["ranged"]]
            self.assertEqual(len(pool), len(set(pool)))
        self.assertEqual(isolated.items[272431]["sources"], [["V", "227853", "226404:50", "", "s"]])
        self.assertEqual(isolated.gear[22401]["inv"], 28)
        self.assertEqual(isolated.class_only[22401], frozenset({"PALADIN"}))
        self.assertEqual(isolated.items[220606]["sources"], [["c", "Enchanting", "300", "1249128", "f"]])

    @unittest.skipIf(test_addon.lupa is None, "lupa is not installed")
    def test_lua_default_filters_and_situational_rows(self):
        game = test_addon.Game(login=False)
        load = game.lua.eval("function(s, ns) assert(load(s))('EasyBIS', ns) end")
        load(luaout.lists_file(self.db, self.lists), game.ns)
        scored = {"DRUID 1": 272430, "DRUID 4": 220606, "PALADIN 3": 23203,
                  "PALADIN 4": 23203, "SHAMAN 1": 23199}
        for key, profile in self.catalog["profiles"].items():
            token, number = key.split()
            decoded = game.ns.Ladders.Decode(token)
            for mode in ladders.MODES:
                for side in "ah":
                    flt = game.lua.table(side=side, phase=0, seenOnly=False, unsourced=False,
                                         alternatives=2, rankCap=6, pvpRewards=mode == "pvp")
                    result = game.ns.Ladders.Compute(decoded, int(number), mode, flt).ranged
                    with self.subTest(profile=key, mode=mode, side=side):
                        if mode == "pve" and key in scored:
                            self.assertEqual(result.best[1].id, scored[key])
                        else:
                            self.assertEqual(len(result.best), 0)
                            self.assertTrue(all("x" in row.entry.flags and "b" in row.entry.flags
                                                for row in result.alts.values()))
                        self.assertGreater(len(result.alts), 0)
                        self.assertTrue(all(row.id in profile[mode] for row in result.alts.values()))
                        self.assertFalse(any(self.catalog["items"][str(row.id)].get("unconfirmed_access")
                                             for row in (*result.best.values(), *result.alts.values())))

    def test_weight_only_and_missing_reading_never_assign_relic_dps(self):
        for enabled, reading in ((False, self.db.simulated), (True, None), (True, relics.simulated.Reading())):
            with self.subTest(enabled=enabled, reading=reading is None):
                with patch.object(relics.simulated, "IN_USE", enabled), patch.object(self.db, "simulated", reading):
                    rows = relics.ranking(self.db, "SHAMAN", 1, "pve", [])
                self.assertTrue(rows)
                self.assertTrue(all(row.score == 0 and row.alternative_only and row.level for row in rows))

    def test_wearing_requirements_are_separate_from_crafting_and_raid_access(self):
        tank = ladders.full_ladder(self.db, "DRUID", 2, "pve", "ranged")
        unknown = next(e for e in tank if e.item_id == 263435)
        self.assertFalse(unknown.passes(("a", True, False, 0, False, 6)))
        self.assertFalse(unknown.passes(("h", False, False, 9, False, 6)))
        self.assertTrue(unknown.passes(("h", True, False, 9, False, 6)))
        restoration = ladders.full_ladder(self.db, "SHAMAN", 3, "pve", "ranged")
        raid = next(e for e in restoration if e.item_id == 22396)
        self.assertFalse(raid.passes(("h", True, False, 0, False, 6)))
        self.assertTrue(raid.passes(("h", False, False, 9, False, 6)))
        seen = {e.item_id for e in restoration if e.passes(("h", False, True, 0, False, 6))}
        self.assertIn(272431, seen)
        self.assertNotIn(22345, seen)
        self.assertEqual([item["items"] for item in relics.notes({22397})], [[22397]])


if __name__ == "__main__":
    unittest.main()
