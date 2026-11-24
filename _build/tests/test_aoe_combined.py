"""Offline comparisons of the same equipment in a single pack and a dungeon route."""
import copy
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_combined as combined
import aoe_weapon_priority as priority


CAPS = (2000, 2000, 2000)


def archived_sets(triples, baseline, dungeon=False):
    sets = [{"main": m, "off": o, "gain": gain, "se": 1} for m, o, gain in triples]
    slots = {}
    for pos, slot in enumerate(("main", "off")):
        entries = {}
        for m, o, gain in sorted(triples, key=lambda x: (-x[2], x[0], x[1])):
            pair = (m, o)
            entries.setdefault(pair[pos], {"id": pair[pos], "partner": pair[1-pos], "gain": gain, "se": 1,
                                           "schoolPct": {"physical": 100}, "petPct": 5})
        slots[slot] = {"baseline": baseline, "referenceWeapons": [77, 88], "items": list(entries.values())}
        if dungeon:
            slots[slot]["baselinePackDamage"] = [baseline / 3] * 3
    if dungeon:
        for row in sets:
            row["packDamage"] = [(baseline + row["gain"]) / 3] * 3
    slots["main"]["setMeasurements"] = sets
    return slots


class AoeCombinedTest(unittest.TestCase):
    def test_weapon_measurements_require_the_same_requests_as_the_damage_campaign(self):
        short = {"wowsims": "test-revision", "specs": {"ROGUE 2": {}}}
        fixture = {**short, "iterations": priority.ITERATIONS, "seed": priority.SEED,
                   "sourceSha256": priority.generator_hash(), "requestSourceSha256": priority.request_source_hashes()}
        priority.validate_campaign(fixture, short)
        for field, stale in (("sourceSha256", "old"), ("requestSourceSha256", {}), ("iterations", 1),
                             ("seed", 0), ("specs", {}), ("wowsims", "other-revision")):
            with self.subTest(field=field), self.assertRaises(ValueError):
                priority.validate_campaign({**fixture, field: stale}, short)

    def test_intrinsic_priority_controls_hand_and_companion_but_preserves_measured_damage(self):
        cases = [(1, 10, 12), (1, 11, 3), (2, 10, 5)]
        short = archived_sets(cases, 100)
        route = archived_sets(cases, 100, True)
        profile = {"class": "ROGUE", "spec": 2, "weaponSets": [[m, o] for m, o, _ in cases],
                   "slots": {"ranged": [99]}}
        proof = {"pointStat": "ap", "controlGain": 400, "controlSE": 2, "sets": [
            {"main": m, "off": o, "baseDps": dps, "gain": gain, "se": se, "rotationGain": 0, "rotationSE": 0}
            for m, o, dps, gain, se in [(1, 10, 40, 0, 0), (1, 11, 43, 100, 5), (2, 10, 45, 2, 7)]],
            "ranged": [{"id": 99, "baseDps": 0, "gain": 12, "se": 0.3, "rotationGain": 0, "rotationSE": 0}]}
        hands, ranged = priority.ratings(profile, proof)
        ranked = combined._weapon_items(short, route, CAPS, hands)
        best, other = ranked["main"]["items"]
        self.assertEqual((best["id"], best["weaponPriority"], best["weaponBonusPoints"]), (2, 630, 0))
        self.assertEqual((other["id"], other["partner"], other["weaponPriority"]), (1, 11, 627))
        self.assertEqual((best["score"], other["score"], other["shortGain"], other["shortRank"]), (5, 3, 3, 1))
        self.assertEqual(ranged[99,]["weaponPriority"], 3)
        # A fast main hand can have more base DPS but weaken the attacks in this rotation.
        proof["sets"][2].update(rotationGain=-104, rotationSE=3)
        proof["sets"][1].update(rotationGain=18, rotationSE=10)
        hands, _ = priority.ratings(profile, proof)
        corrected = combined._weapon_items(short, route, CAPS, hands)["main"]["items"]
        self.assertEqual([(r["id"], r["weaponRotationPoints"], r["weaponPriority"]) for r in corrected],
                         [(1, 0, 627), (2, -13, 617)])
        self.assertEqual([r["score"] for r in corrected], [3, 5])
        for changes in ({"controlGain": 4}, {"pointStat": "rap"}, {"sets": proof["sets"][1:]},
                        {"sets": proof["sets"] + [proof["sets"][0]]},
                        {"sets": [dict(r, rotationGain=None) for r in proof["sets"]]},
                        {"sets": [dict(r, rotationSE=-1) for r in proof["sets"]]},
                        {"ranged": [dict(proof["ranged"][0], baseDps=30)]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                priority.ratings(profile, {**proof, **changes})

    def test_hunter_gets_base_damage_from_the_bow_only(self):
        profile = {"class": "HUNTER", "spec": 3, "weaponSets": [[1, 0]], "slots": {"ranged": [2]}}
        proof = {"pointStat": "rap", "controlGain": 500, "controlSE": 1,
                 "sets": [{"main": 1, "off": 0, "baseDps": 0, "gain": 250, "se": 3, "rotationGain": 0, "rotationSE": 0}],
                 "ranged": [{"id": 2, "baseDps": 32, "gain": 50, "se": 1, "rotationGain": 40, "rotationSE": 1}]}
        hands, ranged = priority.ratings(profile, proof)
        self.assertEqual(hands[1, 0]["weaponPriority"], 50)
        self.assertEqual(ranged[2,]["weaponPriority"], 462)
        proof["sets"][0]["baseDps"] = 60
        with self.assertRaisesRegex(ValueError, "base weapon damage"):
            priority.ratings(profile, proof)

    def test_fire_helm_budget_preserves_passive_stats_and_single_pull_results(self):
        helm = {"id": 8348, "gain": 500, "se": 5, "schoolPct": {"fire": 10}, "usesPerRun": 1,
                "passiveGain": 100, "passiveSE": 1}
        passive = {"activation": [], "usePack": 0, "useAfterSeconds": 0, "usesPerRun": {}}
        active = dict(passive, activation=[8348], usePack=2, usesPerRun={"8348": 1})
        dungeon = {"id": 8348, "gain": 900, "se": 10, "packDamage": [600, 600, 700], **active,
                   "activationTrials": [dict(passive, gain=0, se=0), dict(active, gain=600, se=5)]}
        short = {"baseline": 1000, "items": [helm, {"id": 5, "gain": 250, "se": 1, "schoolPct": {}}]}
        route = {"baseline": 1000, "baselineAvgSeconds": 45, "baselinePackDamage": [500, 200, 300],
                 "items": [dungeon, {"id": 5, "gain": 400, "se": 1, "packDamage": [500, 300, 600]}]}
        first, second = combined._single_items(short, route, CAPS)["items"]
        self.assertEqual((first["id"], second["id"]), (5, 8348))
        self.assertEqual((second["shortRank"], second["routeRank"]), (1, 1))
        self.assertEqual((second["shortAverageGain"], second["routeAverageGain"]), (120, 390))
        self.assertAlmostEqual(second["score"], 25.5)
        self.assertAlmostEqual(second["scoreSE"], .05 * (1.2 + 14.25))
        unused = dict(dungeon, **passive, gain=300)
        self.assertEqual(combined.precision.helm_gains(dict(helm, usesPerRun=0, gain=100), unused, 45)[::2],
                         (100, 300))
        self.assertEqual(combined.precision.helm_gains(dict(helm, usesPerRun=.01), dungeon, 301)[::2],
                         (500, 900))

    def test_current_campaign_rejects_a_disqualified_candidate_or_reference(self):
        gear = {"items": [{} for _ in range(17)]}
        for fields in ({"slots": {"main": [9449]}}, {"referenceWeapons": [9449, 0]},
                       {"pairedItems": {"trinket": 9449}}):
            profile = {"class": "DRUID", "slots": {}, **fields}
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, "Disqualified AoE equipment"):
                combined.simulate_aoe.validate_equipment(profile, gear, {}, {})
        gear["items"][0] = {"id": 9449}
        with self.assertRaisesRegex(ValueError, "Disqualified AoE equipment"):
            combined.simulate_aoe.validate_equipment({"class": "DRUID", "slots": {}}, gear, {}, {})

    def test_disqualified_weapons_are_removed_before_selecting_partners_and_ranks(self):
        trials = [(1, 9449, 50), (1, 10, 3), (2, 10, 4), (9449, 12, 90)]
        short = archived_sets(trials, 100)
        route = archived_sets(trials, 200, True)
        result = combined._weapon_items(short, route, CAPS)
        self.assertEqual([(r["id"], r["partner"], r["shortRank"], r["routeRank"]) for r in result["main"]["items"]],
                         [(2, 10, 1, 1), (1, 10, 2, 2)])
        self.assertEqual([r["id"] for r in result["off"]["items"]], [10])
        for slots in (short, route):
            slots["main"]["referenceWeapons"] = [9449, 0]
        with self.assertRaisesRegex(ValueError, "Disqualified reference"):
            combined._weapon_items(short, route, CAPS)

    def test_optimal_pair_can_differ_from_both_separate_winners(self):
        # (1, 10) wins the short fight, (1, 12) wins the route. (1, 11)
        # wins the equally weighted score, with no per-action details in the pack archive.
        short = archived_sets([(1, 10, 10), (1, 11, 7), (1, 12, 0), (2, 11, 8)], 100)
        route = archived_sets([(1, 10, 0), (1, 11, 9), (1, 12, 12), (2, 11, -2)], 200, True)
        result = combined._weapon_items(short, route, CAPS)
        best, other = result["main"]["items"]
        self.assertEqual((best["id"], best["partner"], best["shortGain"], best["routeGain"]), (1, 11, 7, 9))
        self.assertAlmostEqual(best["score"], 5.75)
        self.assertAlmostEqual(best["scoreSE"], .75)
        self.assertNotIn("shortSchools", best)
        self.assertNotIn("shortPetPct", best)
        self.assertEqual(other["shortPetPct"], 5)
        off = {row["id"]: row for row in result["off"]["items"]}
        self.assertEqual((off[11]["shortRank"], off[11]["routeRank"], off[11]["partner"]), (2, 2, 1))
        self.assertEqual(off[10]["shortRank"], 1)
        self.assertEqual(off[12]["routeRank"], 1)

    def test_stable_ties_and_pair_completeness(self):
        ds = [(2, 11, 2), (1, 11, 2), (1, 10, 2), (3, 12, 0)]
        short = archived_sets(ds, 100)
        route = archived_sets(list(reversed(ds)), 100, True)
        result = combined._weapon_items(short, route, CAPS)
        self.assertEqual([(r["id"], r["partner"]) for r in result["main"]["items"]], [(1, 10), (2, 11), (3, 12)])
        for slot in ("main", "off"):
            for field in ("shortRank", "routeRank"):
                self.assertEqual([r[field] for r in result[slot]["items"]], [1, 1, 3])
        route["main"]["setMeasurements"].pop()
        with self.assertRaisesRegex(ValueError, "weapon configurations"):
            combined._weapon_items(short, route, CAPS)

    def test_single_slot_gain_is_normalized_with_its_own_reference(self):
        short = {"baseline": 100, "items": [{"id": i, "gain": gain, "se": .5, "schoolPct": {"frost": 100}}
                                             for i, gain in ((5, 10), (7, 2))], "pairedItem": 3}
        route = {"baseline": 2000, "baselinePackDamage": [700, 600, 700], "pairedItem": 3, "items": [
            {"id": 5, "gain": -40, "se": 4, "packDamage": [650, 610, 700]},
            {"id": 7, "gain": 160, "se": 4, "packDamage": [850, 610, 700],
             "activation": [7], "usesPerRun": {"7": 1}, "usePack": 2}]}
        best, next_row = combined._single_items(short, route, CAPS)["items"]
        self.assertEqual((best["id"], best["shortRank"], best["routeRank"]), (7, 2, 1))
        self.assertAlmostEqual(best["score"], 5)
        self.assertAlmostEqual(next_row["score"], 4)
        self.assertEqual(best["routeUsePack"], 2)
        self.assertEqual(best["routeUses"], {7: 1})
        for changes, error in (({"pairedItem": 8}, "reference"), ({"baseline": float("nan")}, "Reference damage")):
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, error):
                combined._single_items(short, {**route, **changes}, CAPS)
        for changes, error in (({"packDamage": [2200, 0, 0]}, "wave damage"),
                               ({"se": -0.1}, "standard error"), ({"gain": float("inf")}, "damage gain"),
                               ({"activation": [3], "usesPerRun": {"3": 1}}, "activation")):
            bad = copy.deepcopy(route)
            bad["items"][0].update(changes)
            with self.subTest(changes=changes), self.assertRaisesRegex(ValueError, error):
                combined._single_items(short, bad, CAPS)

    def test_archive_identity_and_scenario_sources_bind_the_results(self):
        schedule = {"packs": [{"health": [100]}] * 3, "manaBetweenPacks": "full"}
        engine = SimpleNamespace(schedule=lambda: schedule, source_hashes=lambda: {"engine.go": "hash"},
                                 SEED=42430, PILOT_SEED=4243, REFINEMENT_ITERATIONS=4096)
        short = {"specs": {}, "wowsims": "revision", "seed": 4242, "iterations": 20000}
        route = {"mode": "dungeon", "metric": "dungeonDamage", "schedule": schedule, "iterations": 1024,
                 "seed": 42430, "pilotSeed": 4243, "refinementIterations": 4096, "refinedBlocks": [],
                 "specs": {}, "sourceSha256": engine.source_hashes(), "wowsims": "revision",
                 "scenarioSha256": combined.digest(schedule), "shortArchiveSha256": combined.digest(short)}
        with patch.dict(sys.modules, simulate_dungeon=engine):
            self.assertEqual(combined.rankings(short, route), {})
            for key in ("sourceSha256", "shortArchiveSha256", "scenarioSha256", "wowsims", "iterations", "pilotSeed"):
                with self.subTest(key=key), self.assertRaises(ValueError):
                    combined.rankings(short, {**route, key: None})
            for mana in ({}, {"manaBetweenPacks": "carry"}):
                stale = {"packs": schedule["packs"], **mana}
                with self.subTest(mana=mana), patch.object(engine, "schedule", return_value=stale):
                    with self.assertRaisesRegex(ValueError, "full mana"):
                        combined.rankings(short, {**route, "schedule": stale, "scenarioSha256": combined.digest(stale)})

    def test_dungeon_evidence_covers_each_wave_and_named_pet(self):
        row = {"packDamage": [20, 10, 15], "packHits": [4096, 4000, 4096], "avgSeconds": 41, "petDamage": 7}
        combined._route_evidence(row, 4096, "Raptor")
        for patch_row in ({"packHits": [4096, 0, 4096]}, {"packHits": [4097, 10, 20]},
                          {"avgSeconds": float("inf")}, {"petDamage": 46}):
            with self.subTest(patch_row=patch_row), self.assertRaises(ValueError):
                combined._route_evidence({**row, **patch_row}, 4096, "Raptor")
        with_mana = {**row, "manaRefillEvents": [4096, 4096], "manaRestored": [530.5, 0]}
        combined._route_evidence(with_mana, 4096, "Raptor", uses_mana=True)
        for patch_row in ({"manaRefillEvents": [4095, 4096]}, {"manaRestored": [-3, 100]}, {}):
            sample = {**with_mana, **patch_row} if patch_row else row
            with self.subTest(patch_row=patch_row), self.assertRaisesRegex(ValueError, "mana refills"):
                combined._route_evidence(sample, 4096, "Raptor", uses_mana=True)
        with self.assertRaisesRegex(ValueError, "class without mana"):
            combined._route_evidence(with_mana, 4096, None, uses_mana=False)


if __name__ == "__main__":
    unittest.main()
