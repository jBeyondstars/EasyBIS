"""Personal buffs in the active AoE builds, using the actual pack and dungeon requests."""
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aoe_encounter as dungeon
import aoe_route_rotation
import simulate_aoe as sim


# Spell IDs of the opening stance, trained aspect or permanent form and associated aura.
WARRIORS = {"warrior-arms": 2457, "warrior-fury": 2458}
HUNTERS = {"hunter-beast-mastery": 14322, "hunter-marksmanship": 14322, "hunter-survival": 14322}
DRUIDS = {"druid-balance": (24858, 24907), "druid-feral-cat": (768, 24932)}
ROGUES = ("rogue-assassination", "rogue-combat", "rogue-subtlety")
PROFILES = (*WARRIORS, *HUNTERS, *DRUIDS, *ROGUES)
ITERATIONS = 32


def request(slug, side, cli, route, prepull=None):
    root = Path(os.environ["EASYBIS_WOWSIMS"])
    profile = sim.read(sim.PROFILES / (slug + ".json"))
    if prepull is not None:
        profile["prepullBuffs"] = prepull
    path = sim.PROFILES / profile["dungeonRotation"] if "dungeonRotation" in profile else root / profile["rotation"]
    rotation = sim.read_preset(root, cli, path)
    gear = sim.reference_equipment(root, cli, profile)
    req = sim.make_request(profile, profile["races"][side], rotation, gear, None, 0, ITERATIONS)
    req["simOptions"].update(randomSeed="90320", debugFirstIteration=True)
    if route:
        req["encounter"] = dungeon.encounter()
        player = req["raid"]["parties"][0]["players"][0]
        player["rotation"] = aoe_route_rotation.route_rotation(profile, player["rotation"], root)
    return req


def damage(unit, **action_id):
    actions = (a for a in unit["actions"] if all(a["id"].get(k) == v for k, v in action_id.items()))
    return sum(t["damage"] for action in actions for t in action["targets"])


class MartialBuffsTest(unittest.TestCase):
    def test_native_build_overrides_a_32_bit_go_default(self):
        with patch.dict(os.environ, {"GOARCH": "386", "CGO_ENABLED": "1"}), patch("subprocess.run") as build:
            sim.build_native(Path("checkout"), Path("overlay.json"), Path("runner"), "main.go")
        env = build.call_args.kwargs["env"]
        self.assertEqual((env["GOARCH"], env["CGO_ENABLED"]), ("amd64", "0"))

    def assert_prepull_timestamps(self, cli, route):
        # Four billion nanoseconds overflow the pinned engine's signed 32-bit deadline comparator.
        prepull = [{"spell": 2687, "at": "-7s"}, {"spell": 11551, "at": "-3s"}]
        req = request("warrior-fury", "a", cli, route, prepull)
        with tempfile.TemporaryDirectory() as work:
            result = sim.run_request(cli, Path(work), req)
        casts = re.findall(r"^\[(-?[\d.]+)\] \[ \(#1\)\] Casting \{SpellID: (\d+)\}.* APL: prepull \d+", result["logs"], re.M)
        self.assertEqual(casts, [("-7.00", "2687"), ("-3.00", "11551")])

    def test_personal_sources_in_active_profiles(self):
        for slug in PROFILES:
            with self.subTest(slug=slug):
                p = sim.read(sim.PROFILES / (slug + ".json"))
                self.assertEqual(bool(p.get("selfRaidBuffs", {}).get("markOfTheWild")), slug in DRUIDS)
                if slug in WARRIORS:
                    self.assertEqual(p["prepullBuffs"], [{"spell": 2687, "at": "-4s"}, {"spell": 11551, "at": "-3s"}])
                elif slug in HUNTERS:
                    self.assertEqual(p["prepullBuffs"], [{"spell": HUNTERS[slug], "at": "-20s"}])
                elif slug in ROGUES:
                    items = p["player"]["consumables"]
                    self.assertEqual((items["mhWeaponImbueId"], items["ohWeaponImbueId"]), (8928, 8928))

    def check_native(self, cli, route):
        with tempfile.TemporaryDirectory() as work:
            for slug in PROFILES:
                for side in ("a", "h"):
                    with self.subTest(profile=slug, faction=side):
                        result = sim.run_request(cli, Path(work), request(slug, side, cli, route))
                        if route:
                            dungeon.route_samples(result, ITERATIONS)
                        else:
                            sim.samples(result, ITERATIONS, {})
                        logs = result["logs"]
                        unit = result["raidMetrics"]["parties"][0]["players"][0]
                        auras = {(a["id"].get("spellId"), a["id"]["tag"]): a for a in unit["auras"]}
                        permanent = []
                        if slug in WARRIORS:
                            permanent = [(11551, 0)]
                            self.assertRegex(logs, r"\[-4\.00\].*Gained [1-9][\d.]* rage from \{SpellID: 2687\}")
                            self.assertRegex(logs, r"\[-4\.00\].*Spent [1-9][\d.]* health from \{SpellID: 2687\}")
                            self.assertRegex(logs, r"\[-3\.00\].*Spent [1-9][\d.]* rage from \{SpellID: 11551\}")
                            self.assertIn(f"[0.00] [ (#1)] Aura gained: {{SpellID: {WARRIORS[slug]}}}", logs)
                            stances = sum(a["uptimeSecondsAvg"] for (spell, _), a in auras.items() if spell in (71, 2457, 2458))
                            self.assertAlmostEqual(stances, result["avgIterationDuration"], places=7)
                        elif slug in HUNTERS:
                            aspect = HUNTERS[slug]
                            permanent = [(aspect, 0)]
                            self.assertIn(f"[-20.00] [ (#1)] Aura gained: {{SpellID: {aspect}}}", logs)
                            mana_ticks = re.findall(r"^\[-[\d.]+\] \[ \(#1\)\] Gained .*? mana .*? --> ([\d.]+)\) of (\d+) total", logs, re.M)
                            self.assertTrue(mana_ticks)
                            self.assertEqual(float(mana_ticks[-1][0]), float(mana_ticks[-1][1]), "mana at the pull")
                            permanent.append((20906, -1))  # Trueshot Aura from the hunter's own talents
                            self.assertGreater(damage(unit, otherId="OtherActionShoot"), 0)
                            self.assertEqual(damage(unit, otherId="OtherActionAttack"), 0)
                        elif slug in DRUIDS:
                            form, group_aura = DRUIDS[slug]
                            permanent = [(form, 0), (group_aura, -1), (9885, -1)]
                        else:
                            self.assertGreater(damage(unit, spellId=11337), 0)
                            self.assertEqual(auras[(1787, 0)]["procsAvg"], 1)  # Opens stealthed, breaks on action.
                            if slug != "rogue-assassination":
                                self.assertGreater(auras[(13877, 0)]["uptimeSecondsAvg"], 0)  # Blade Flurry
                        for key in permanent:
                            self.assertEqual(auras[key]["procsAvg"], 1, key)
                            self.assertAlmostEqual(auras[key]["uptimeSecondsAvg"], result["avgIterationDuration"],
                                                   places=7, msg=str(key))
                        if route and slug in (*HUNTERS, *DRUIDS):
                            self.assertEqual(re.findall(r"Dungeon pack (\d) starts at full mana", logs), ["1", "2", "3"])

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "requires the native pack CLI")
    def test_short_pack(self):
        cli = Path(os.environ["EASYBIS_PACK_CLI"])
        self.assert_prepull_timestamps(cli, route=False)
        self.check_native(cli, route=False)

    @unittest.skipUnless(os.getenv("EASYBIS_ROUTE_CLI") and os.getenv("EASYBIS_WOWSIMS"), "requires the native dungeon CLI")
    def test_full_dungeon(self):
        cli = Path(os.environ["EASYBIS_ROUTE_CLI"])
        self.assert_prepull_timestamps(cli, route=True)
        self.check_native(cli, route=True)

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "requires the native pack CLI")
    def test_each_poisoned_hand_can_trigger_instant_poison(self):
        cli = Path(os.environ["EASYBIS_PACK_CLI"])
        req = request("rogue-assassination", "a", cli, route=False)
        consumables = req["raid"]["parties"][0]["players"][0]["consumables"]
        with tempfile.TemporaryDirectory() as work:
            for main, off in ((8928, 0), (0, 8928), (0, 0)):
                with self.subTest(main=main, off=off):
                    consumables.update(mhWeaponImbueId=main, ohWeaponImbueId=off)
                    result = sim.run_request(cli, Path(work), req)
                    unit = result["raidMetrics"]["parties"][0]["players"][0]
                    self.assertEqual(damage(unit, spellId=11337) > 0, bool(main or off))

    @unittest.skipUnless(os.getenv("EASYBIS_PACK_CLI") and os.getenv("EASYBIS_WOWSIMS"), "requires the native pack CLI")
    def test_thorns_needs_incoming_strikes(self):
        cli = Path(os.environ["EASYBIS_PACK_CLI"])
        req = request("druid-balance", "a", cli, route=False, prepull=[{"spell": 9910, "at": "-90s"}])
        with tempfile.TemporaryDirectory() as work:
            for incoming in (False, True):
                with self.subTest(incoming=incoming):
                    if incoming:
                        req["raid"]["tanks"] = [{"type": "Player", "index": 0}]
                        for target in req["encounter"]["targets"]:
                            target.update(tankIndex=0, swingSpeed=2, minBaseDamage=140, damageSpread=0.1)
                    result = sim.run_request(cli, Path(work), req)
                    unit = result["raidMetrics"]["parties"][0]["players"][0]
                    aura = next(a for a in unit["auras"] if a["id"].get("spellId") == 9910)
                    self.assertEqual(aura["uptimeSecondsAvg"], sim.SECONDS)
                    self.assertEqual(unit["dtps"]["avg"] > 0, incoming)
                    self.assertEqual(damage(unit, spellId=9910) > 0, incoming)


if __name__ == "__main__":
    unittest.main()
