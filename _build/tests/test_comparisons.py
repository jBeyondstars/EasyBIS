"""Paired PvE comparisons must survive a rebuild only for the exact pair, profile and slot tested."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD))
sys.path.insert(0, str(BUILD / "tests"))

import fdb
import ladders
import notes
from test_addon import Game, lupa


class ComparisonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = fdb.load(BUILD / "cache" / "ForeverDB")
        cls.hands = ladders.full_ladder(cls.db, "HUNTER", 1, "pve", "hands")

    def test_import_uses_the_original_pair_and_longest_run(self):
        key = "HUNTER/1/pve/hands/16463/16571"
        pairs = {key: [16571, 13255, 10.5]}
        def batch(dps):
            return {key: {"item": 16571, "rival": 13255, "dps_se": {"item": [dps, 1], "all_stats": [23.795, 1]}}}
        batches = [(500, batch(12.319)), (5000, batch(10)), (20000, batch(9.5))]
        imported = notes.import_trials(pairs, batches, self.db.simulated, "21377c070b")
        self.assertEqual(imported["groups"]["HUNTER 1 hands"], [[16463, 16571, 13255, 10.5, 9.5, 1, 23.795, 20000]])
        with self.assertRaisesRegex(ValueError, "original item pair"):
            notes.import_trials({key: [16571, 111, 10.5]}, batches, self.db.simulated, "21377c070b")
        with self.assertRaisesRegex(ValueError, "Missing"):
            notes.import_trials(pairs, [], self.db.simulated, "21377c070b")

    def test_only_the_tested_faction_id_in_the_original_inversion_can_get_the_note(self):
        profile = self.db.simulated.specs["HUNTER", 1].record
        row = [16463, 16571, 13255, 10.5, 12.319, 1.523, 23.795, 500]
        source = {"wowsims": "21377c070b", "profiles": {"HUNTER 1": notes.profile_key(profile)},
                  "groups": {"HUNTER 1 hands": [row]}}
        slot = {"hands": self.hands}
        tree = {"HUNTER": {1: {"pve": slot}}}
        def values(specific=()):
            return notes.comparisons(self.db, tree, specific, source)
        self.assertFalse(values(), "an archived duel cannot explain a faction-specific replacement")
        slot["hands"] = list(self.hands)  # the canonical ladder that used the archived scores
        self.assertEqual(values(), {("HUNTER", 1, "hands"): [(16571, 13255, 1232, 2380, 500, "c")]})
        self.assertTrue(values([{"items": [16463]}]), "an editorial note for the other faction is separate")
        self.assertTrue(values([{"items": [16571], "list": "pvp"}]))
        self.assertFalse(values([{"items": [16571], "specs": ["HUNTER 1"], "slot": "hands"}]))
        with patch.dict(profile, {"without_effect": [16571]}):
            self.assertFalse(values())
        with patch.dict(profile, {"without_effect": [13255], "assumed_rate": [13255]}):
            self.assertEqual(values()[("HUNTER", 1, "hands")][0][-1], "cma")
        # An inconclusive swap only warrants a tooltip if the model has a known limitation.
        source["groups"]["HUNTER 1 hands"] = [row[:4] + [0.2] + row[5:]]
        self.assertFalse(values())
        with patch.dict(profile, {"without_effect": [13255]}):
            self.assertEqual(values()[("HUNTER", 1, "hands")][0][-1], "nm")
        for column, invalid in ((0, 999), (1, 16463), (2, 999), (3, -10.5)):
            with self.subTest(column=column):
                source["groups"]["HUNTER 1 hands"] = [row[:column] + [invalid] + row[column + 1:]]
                self.assertFalse(values())
        source["groups"]["HUNTER 1 hands"] = [row]
        source["profiles"]["HUNTER 1"] = "another reference set"
        self.assertFalse(values())
        source["profiles"]["HUNTER 1"] = notes.profile_key(profile)
        source["wowsims"] = "another simulator revision"
        self.assertFalse(values())

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_archived_duels_never_create_tooltips_in_either_language(self):
        for locale in ("frFR", "enUS"):
            with self.subTest(locale=locale):
                game = Game(locale=locale)
                self.assertIsNone(game.ns.data.comparisons)
                # Even data from a prior build must not turn a duel into a tooltip.
                game.ns.data.comparisons = game.lua.table_from({
                    "HUNTER1_hands": " 911:13255:-2:0:20000:nma 912:13255:-12:-5:5000:r"
                                     " 913:13255:2:3:2000:n 914:13255:4:3:2000:ca 915:13255:12:12:500:c",
                })
                for item in range(911, 916):
                    self.assertIsNone(game.ns.Notes.For(item, "HUNTER", 1, "pve", "hands"))
                self.assertIn("200", game.ns.Notes.For(647, "WARRIOR", 1, "pve", "main"))

    @unittest.skipIf(lupa is None, "lupa is not installed")
    def test_destruction_shoulders_show_their_gaps_without_circular_notes(self):
        for locale in ("frFR", "enUS"):
            with self.subTest(locale=locale):
                game = Game(locale=locale, cls="WARLOCK", saved="EasyBISDB = { altCount = 6 }")
                state = game.lua.table_from({"class": "WARLOCK", "spec": 3, "list": "pve", "slot": "shoulder"})
                rows, _ = game.ns.Rows.Items(state)
                shoulders = {row.id: (row.gap, row.why) for row in rows.values() if row.id in (19059, 18681)}
                self.assertEqual(shoulders, {19059: (-11, None), 18681: (-15, None)})


if __name__ == "__main__":
    unittest.main()
