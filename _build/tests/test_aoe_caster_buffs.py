"""Check the personal buffs actually applied by the two native PvE pack simulators."""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import simulate_aoe as sim
import simulate_dungeon as dungeon


# The keys are active player aura IDs, which can differ from the cast spell.
MAGE = (10157, 22783)  # Arcane Intellect, Mage Armor
TOTEMS = (10432, 10441, 10626, 10494)  # Lightning Shield, Strength, Grace, Mana Spring
EXPECTED = {
    "mage-arcane": MAGE, "mage-fire": MAGE, "mage-frost": MAGE,
    "paladin-retribution": (10301, 25782),
    "paladin-shockadin": (19746, 20293, 25898),
    "priest-shadow": (15473, 10952, 21564, 27681, 27683),
    "shaman-elemental": (*TOTEMS, 16342),
    "shaman-enhancement": (*TOTEMS, 16362),
    "warlock-affliction": (11735, 18791), "warlock-destruction": (11735,),
    "warlock-demonology": (11735, 18791, 19028, 11767, 23785),
}


class PersonalBuffTest(unittest.TestCase):
    def check_melee_damage(self, slug, result, player, active):
        targets = {target["unitIndex"] for target in result["encounterMetrics"]["targets"]}
        landed = [action["id"] for action in player["actions"]
                  if any(target["unitIndex"] in targets and target.get("damage", 0) > 0
                         for target in action["targets"])]
        self.assertTrue(any(action.get("otherId") == "OtherActionAttack" and action.get("tag") == 14
                            for action in landed), "No regular main-hand swing dealt damage")
        spells = {action.get("spellId") for action in landed}
        if slug == "paladin-retribution":
            self.assertRegex(result["logs"], r"\[-\d+\.\d+\] [^\n]*Aura gained: \{SpellID: 20920\}")
            self.assertGreater(active.get(20920, 0), 0)  # Command
            self.assertGreater(active.get(20293, 0), 0)  # Righteousness
            uptime = (active[20920] + active[20293]) / result["avgIterationDuration"]
            self.assertGreaterEqual(uptime, 0.99)
            self.assertLessEqual(uptime, 1.000001)
            self.assertIn(10333, spells)  # Holy Strike
            # Unsealed Wrath's replayed hits use the Echo aura ID as their action tag.
            self.assertTrue({1311703, 1311704} <= {action.get("tag") for action in landed})
        else:
            self.assertTrue({17364, 439440} <= spells, "Stormstrike or Windfury Weapon dealt no damage")

    def test_declared_group_buffs_are_supplied_by_the_character(self):
        ranked = sim.eligibility.ranked_specs(sim.fdb.load(sim.HERE / "cache" / "ForeverDB"))
        for path in sim.PROFILES.glob("*.json"):
            profile = sim.read(path)
            if f"{profile['class']} {profile['spec']}" not in ranked:
                continue
            with self.subTest(profile=path.stem):
                self.assertEqual(profile.get("selfRaidBuffs", {}),
                                 {"markOfTheWild": True} if profile["class"] == "DRUID" else {})
                player_buffs = profile["player"].get("buffs", {})
                if profile["class"] == "PALADIN":
                    self.assertEqual(len(player_buffs), 1)
                    self.assertIn(next(iter(player_buffs)), ("greaterBlessingOfMight", "greaterBlessingOfKings"))
                else:
                    self.assertFalse(player_buffs)

    def check_native(self, cli, route):
        root = Path(os.environ["EASYBIS_WOWSIMS"])
        for slug, expected in EXPECTED.items():
            profile = sim.read(sim.PROFILES / (slug + ".json"))
            preset = sim.PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile else root / profile["rotation"]
            rotation = sim.read_preset(root, cli, preset)
            gear = sim.reference_equipment(root, cli, profile)
            for race in profile["races"].values():
                with self.subTest(profile=slug, race=race), tempfile.TemporaryDirectory() as work:
                    iterations = 16
                    req = sim.make_request(profile, race, rotation, gear, None, 0, iterations)
                    if route:
                        req = dungeon.bind_request(req, profile, root, [], 0, sim.SEED)
                    req["simOptions"]["debugFirstIteration"] = True
                    result = sim.run_request(cli, Path(work), req)
                    if route:
                        dungeon.route.route_samples(result, iterations)
                        self.assertEqual(re.findall(r"Dungeon pack (\d) starts at full mana", result["logs"]),
                                         ["1", "2", "3"])
                    else:
                        sim.samples(result, iterations, profile["damageChecks"], profile.get("requiredPet"))
                    player = result["raidMetrics"]["parties"][0]["players"][0]
                    active = {a["id"].get("spellId"): a["uptimeSecondsAvg"] for a in player["auras"]
                              if a.get("uptimeSecondsAvg", 0) > 0}
                    for spell in expected:
                        self.assertAlmostEqual(active.get(spell, 0), result["avgIterationDuration"], places=6,
                                               msg=f"{slug} aura {spell} missing for part of the fight")
                    if slug.startswith("paladin-"):
                        self.assertEqual(set(active) & {10293, 10301, 19746}, set(expected) & {10293, 10301, 19746})
                        self.assertNotIn(25780, active)  # Righteous Fury belongs to Protection.
                    if slug in ("paladin-retribution", "shaman-enhancement"):
                        self.check_melee_damage(slug, result, player, active)
                    if slug.startswith("warlock-"):
                        targets = [t["unitIndex"] for t in result["encounterMetrics"]["targets"]]
                        fighting = {p["name"] for p in player["pets"] if sim.targets_hit_per_pack(p["actions"], targets)[0]}
                        self.assertEqual(fighting, {profile["requiredPet"]} if "requiredPet" in profile else set())

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "native pack CLI required")
    def test_native_short(self):
        self.check_native(Path(os.environ["EASYBIS_PACK_CLI"]), False)

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"), "native route CLI required")
    def test_native_route(self):
        self.check_native(Path(os.environ["EASYBIS_ROUTE_CLI"]), True)
