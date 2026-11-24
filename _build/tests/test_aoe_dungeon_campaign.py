import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import simulate_dungeon as sim


class DungeonCampaignTest(unittest.TestCase):
    @staticmethod
    def obs(values, casts=None):
        return {
            "Damage": values,
            "Casts": casts or {},
            "PackDamage": [10, 20, 30],
            "PackHits": [len(values)] * 3,
            "Seconds": 43,
            "PetDamage": 0,
        }

    def test_uncertainty_of_matched_differences(self):
        base = [20, 150, 75, 200]
        options = [{"activation": ids, "usePack": 0, "useAfterSeconds": 0} for ids in ([], [99])]
        values, info = sim.measure_options(
            options, [self.obs(base), self.obs([v + 5 for v in base], {"99": 1})]
        )
        self.assertEqual(values, [v + 5 for v in base])
        self.assertEqual(info["activationTrials"][1]["gain"], 5)
        self.assertEqual(info["activationTrials"][1]["se"], 0)

    def test_no_use_or_uncertain_benefit_retains_passive_policy(self):
        base = [20, 150, 75, 200]
        options = [{"activation": ids, "usePack": 0, "useAfterSeconds": 0} for ids in ([], [99])]
        for obs in (self.obs([v + 10 for v in base]), self.obs([19, 155, 70, 210], {"99": 1})):
            _, info = sim.measure_options(options, [self.obs(base), obs])
            self.assertEqual(info["activation"], [])
        with self.assertRaises(ValueError):
            sim.measure_options([{"activation": []}], [self.obs(base, {"22": 1})])

    def test_weapon_partner_is_measured_on_the_same_pair(self):
        configs = [(12, 15), (12, 16), (14, 16)]
        result = {p: ([v, v], {}) for p, v in zip(configs, (110, 120, 125))}
        rows = sim.rows_for(configs, result, [100, 100], lambda p: p)
        self.assertEqual([(r["id"], r["partner"], r["gain"]) for r in rows], [(14, 16, 25), (12, 16, 20)])
        self.assertEqual(rows[-1]["gap"], 5)

    def test_schedule_matches_enemy_types_and_healths(self):
        spec = sim.schedule()
        targets = sim.route.encounter()["targets"]
        self.assertEqual([hp for p in spec["packs"] for hp in p["health"]], [t["stats"][29] for t in targets])
        self.assertEqual([(p["elites"], p["normal"]) for p in spec["packs"]], [(4, 0), (1, 0), (3, 4)])
        self.assertEqual(spec["manaBetweenPacks"], "full")
        self.assertTrue(all(t["targetInputs"][3]["numberValue"] == 1 for t in targets))

    def test_mana_refills_follow_the_selected_activation(self):
        options = [{"activation": ids, "usePack": 0, "useAfterSeconds": 0} for ids in ([], [99])]
        passive = dict(self.obs([20, 30]), ManaRestored=[300, 400], ManaRefillEvents=[2, 2])
        active = dict(self.obs([25, 35], {"99": 1}), ManaRestored=[250, 390], ManaRefillEvents=[2, 2])
        _, info = sim.measure_options(options, [passive, active])
        self.assertEqual(info["manaRestored"], [250, 390])
        self.assertEqual(info["manaRefillEvents"], [2, 2])

    def test_identical_items_do_not_trigger_extra_trials(self):
        def block(second_gain):
            return {
                "baseline": 100,
                "items": [{"id": 1, "gain": 3, "se": 1}, {"id": 2, "gain": second_gain, "se": 1, "gapSE": 0.5}],
            }

        self.assertFalse(sim.aoe_dungeon_precision.close_leaders(block(3), block(3), "finger"))
        self.assertTrue(sim.aoe_dungeon_precision.close_leaders(block(2.9), block(2.9), "finger"))
        self.assertFalse(sim.aoe_dungeon_precision.close_leaders(block(1), block(1), "finger"))

    def test_published_seed_range_is_disjoint_from_short_campaign(self):
        archive = sim.short.read(sim.HERE / "corrections/aoe.json")
        self.assertGreaterEqual(sim.SEED, archive["seed"] + archive["iterations"])
        self.assertGreaterEqual(sim.SEED, sim.PILOT_SEED + 1024)
