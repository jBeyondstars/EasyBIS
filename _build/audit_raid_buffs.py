"""Verify native class buffs for the boss profiles actually consumed by the Raid rankings.

Without arguments, checks the portable evidence against the current scoring inputs.
With --dps-engine and --tank-engine, also replays every request on the pinned 64-bit engines.
"""
import argparse
import copy
import hashlib
import json
import os
import struct
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import notes
import tank_options


BUILD = Path(__file__).resolve().parent
DOCS = BUILD.parent / "docs" / "audit-forever"
ARCHIVE = DOCS / "protocole-buffs-raid.zip"
DPS = "21377c070b5ea111a9bb5e36eb766193270b0cc7"
TANK = "a73af7145111ce19c621e3b5f678553adf326907"
SLOTS = ("head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet",
         "finger1", "finger2", "trinket1", "trinket2", "main", "off", "ranged")
HEALERS = {"DRUID 3", "PALADIN 1", "PRIEST 1", "PRIEST 2", "SHAMAN 3"}
TANK_DUELS = {"bear": ("DRUID", 2), "pal": ("PALADIN", 2), "war": ("WARRIOR", 3)}
# IDs of personal, talent, rotational and group effects discussed in the report.
AURAS = {71, 768, 2457, 2458, 6774, 9634, 9885, 10157, 10301, 10432, 10438, 10441, 10494,
         10587, 10612, 10614, 10626, 10938, 10952, 11551, 11735, 11767, 14322, 15473, 16342,
         16362, 18789, 18791, 19028, 20293, 20423, 20906, 20920, 22783, 23785, 24858, 24907,
         24932, 25296, 25780, 25782, 25894, 25898, 27681, 408510, 412732, 1239570}
# Poison damage, lightning shield orb, and Flametongue weapon proc.
ACTIONS = {11337, 11354, 26363, 16343, 16344, 16368}
NATIVE_MAIN = """package main
import (
    "os"
    "github.com/wowsims/forever/sim"
    "github.com/wowsims/forever/sim/core"
    "github.com/wowsims/forever/sim/core/proto"
    "google.golang.org/protobuf/encoding/protojson"
)
func main() {
    sim.RegisterAll()
    registerEffects()
    data, err := os.ReadFile(os.Args[1]); if err != nil { panic(err) }
    req := &proto.RaidSimRequest{}
    if err = protojson.Unmarshal(data, req); err != nil { panic(err) }
    res := core.RunRaidSim(req)
    if res.Error != nil { panic(res.Error.Message) }
    data, err = protojson.Marshal(res); if err != nil { panic(err) }
    if err = os.WriteFile(os.Args[2], data, 0644); err != nil { panic(err) }
}
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def jsonfile(path):
    return json.loads(path.read_bytes())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_archive():
    with zipfile.ZipFile(ARCHIVE) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        requests = {}
        for key, row in manifest.items():
            raw = archive.read("requests/" + key + ".json")
            require(digest(raw) == row["sha256"], f"{key}: input digest")
            requests[key] = json.loads(raw)
    return manifest, requests


def player(request):
    [character] = [unit for party in request["raid"]["parties"] for unit in party.get("players", [])]
    return character


def summary(result):
    [unit] = [u for party in result["raidMetrics"]["parties"] for u in party.get("players", [])]
    [boss] = result["encounterMetrics"]["targets"]
    duration = result["avgIterationDuration"]
    n = result["iterationsDone"]
    samples = result["raidMetrics"]["dps"]["allValues"]
    require(len(samples) == n, "Missing samples")
    actions = {}
    for action in unit["actions"]:
        spell = action["id"].get("spellId")
        if spell in ACTIONS:
            total = sum(t.get("damage", 0) for t in action["targets"])
            actions[str(spell)] = actions.get(str(spell), 0) + total / n
    boss_damage = sum(t.get("damage", 0) for a in boss.get("actions", []) for t in a.get("targets", []))
    return {
        "iterations": n, "dps": round(result["raidMetrics"]["dps"]["avg"], 7),
        "threat": round(unit["threat"].get("avg", 0), 7), "dtps": round(unit["dtps"].get("avg", 0), 7),
        "bossDamagePerFight": round(boss_damage / n, 6),
        "sampleSha256": digest(struct.pack(f"<{n}d", *samples)),
        "pets": {p["name"]: round(p["dps"]["avg"], 5) for p in unit.get("pets", []) if p["dps"].get("avg", 0) > 0},
        "auras": sorted([[a["id"]["spellId"], a["id"].get("tag", 0),
                          round(100 * a.get("uptimeSecondsAvg", 0) / duration, 3)]
                         for a in unit["auras"] if a["id"].get("spellId") in AURAS]),
        "damagePerFight": {i: round(v, 6) for i, v in actions.items()},
    }


def check_buffs(key, measured):
    required = {}
    if key.startswith("dps/DRUID"):
        required = {24858: 99.9, 24907: 99.9}
    elif key.startswith("dps/HUNTER"):
        required = {14322: 99.9, 20906: 99.9}
        pets = set(measured["pets"])
        require(pets == ({"Raptor", "Hawk 1", "Hawk 2"} if key.endswith("-1") else set()), key + ": pets")
    elif key.startswith("dps/MAGE"):
        required = {22783: 99.9}
    elif key.startswith("dps/PALADIN"):
        required = {10301: 99.9, 20293: 24.0 if key.endswith("-3") else 98.0}
        if key.endswith("-3"):
            required[20920] = 72
    elif key.startswith("dps/PRIEST"):
        required = {10952: 99.9, 15473: 99.9}
    elif key.startswith("dps/ROGUE"):
        required = {6774: 90}
        require(all(measured["damagePerFight"].get(str(i), 0) > 0 for i in (11337, 11354)), key + ": poisons")
    elif key.startswith("dps/SHAMAN"):
        required = {10494: 99.9, 10612: 99.9}
        required.update({10438: 98} if key.endswith("-1") else {10587: 99, 16362: 99.9})
    elif key.startswith("dps/WARLOCK"):
        required = {11735: 99.9}
        summoned = {"1": set(), "2": {"Imp"}, "3": {"Succubus"}}[key[-1]]
        require(set(measured["pets"]) == summoned, key + ": demons")
        if key.endswith("-1"):
            required[18789] = 99.9
        if key.endswith("-2"):
            required.update({18791: 99.9, 19028: 99.9, 412732: 99.9})
    elif key.startswith("dps/WARRIOR"):
        required = {11551: 98, 2457: 99.9 if key.endswith("-1") else 13}
        if key.endswith("-2"):
            required[2458] = 85
    elif key.startswith("cat/"):
        required = {768: 99}
    elif key.startswith("tank/bear"):
        required = {9634: 99.9}
    elif key.startswith("tank/war"):
        required = {71: 95, 11551: 98}
    elif key.startswith("tank/pal"):
        required = {10301: 99.9, 25780: 99.9, 20423: 98, 1239570: 85}
    for spell, minimum in required.items():
        uptimes = [rate for i, _, rate in measured["auras"] if i == spell]
        require(uptimes and max(uptimes) >= minimum, f"{key}: aura {spell}")


def check_inputs(manifest, requests):
    records = jsonfile(BUILD / "corrections/simulated.json")
    comparisons = jsonfile(BUILD / "corrections/comparisons.json")
    cat = jsonfile(BUILD / "corrections/feral_offhands.json")
    require(records["wowsims"] == comparisons["wowsims"] == DPS[:10] and cat["wowsims"] == TANK, "Source revision")
    general = {k.removeprefix("dps/").replace("-", " "): v for k, v in manifest.items() if k.startswith("dps/")}
    require(general.keys() == records["specs"].keys() == comparisons["profiles"].keys(), "DPS coverage")
    partial = {"DRUID 4", *(" ".join(map(str, spec)) for spec in TANK_DUELS.values())}
    require(len(general.keys() | partial | HEALERS) == 29, "Role coverage")
    for key, row in manifest.items():
        req = requests[key]
        s = req["simOptions"]
        require(int(s["randomSeed"]) == 4242 and s["iterations"] == row["measure"]["iterations"], key)
        require(req["encounter"]["duration"] == 180 and req["encounter"]["durationVariation"] == 5 and
                len(req["encounter"]["targets"]) == 1, key)
        player(req)
        check_buffs(key, row["measure"])
    for spec, row in general.items():
        record = records["specs"][spec]
        req = requests["dps/" + spec.replace(" ", "-")]
        equipped = [i.get("id", 0) for i in player(req)["equipment"]["items"]]
        require([record["reference"][i] for i in SLOTS] == equipped and
                record["side"] == row["gearSide"] and row["measure"]["iterations"] == record["iterations"] and
                record["dps"]["reference"] == round(row["measure"]["dps"], 1) and
                notes.profile_key(record) == comparisons["profiles"][spec], spec + ": archived reference")
    for cls, spec in TANK_DUELS.items():
        for slot, (high, low, a, h) in tank_options.DUELS[spec].items():
            for side, expected in (("a", a), ("h", h)):
                prefix = f"tank/{cls}-{side}-{slot}/"
                new, old = (manifest[prefix + str(i)]["measure"] for i in (high, low))
                got = tuple(round(new[k] - old[k], 1) for k in ("dps", "threat", "dtps"))
                require(got == expected and new["iterations"] == old["iterations"] == 2000, prefix + str(got))
    for side in ("a", "h"):
        prefix = f"cat/cat-{side}-off/"
        new, old = (manifest[prefix + i]["measure"] for i in ("ap40", "empty"))
        require(abs(new["dps"] - old["dps"] - cat["calibration"][side][0]) < 0.00001, prefix)
    for probe in ("SHAMAN-1", "SHAMAN-2"):
        req = copy.deepcopy(requests["dps/" + probe])
        corrected = requests[f"probe/{probe}-shield"]
        pos = player(req)["rotation"]["prepullActions"][0]
        action = pos["action"]["castSpell"]["spellId"]
        require(action == {"spellId": 408510}, probe + ": historical shield")
        # Only the unlearned shield is replaced in the exported future profile.
        action["spellId"] = 10432
        require(req == corrected, probe + ": corrected shield")
        m = manifest[f"probe/{probe}-shield"]["measure"]
        require(max(a[2] for a in m["auras"] if a[0] == 10432) >= 99.9 and m["bossDamagePerFight"] == 0 and
                m["damagePerFight"].get("26363", 0) == 0, probe + ": reactive shield")
        ready = manifest[f"probe/{probe}-ready"]["measure"]
        require(ready["sampleSha256"] == manifest["dps/" + probe]["measure"]["sampleSha256"] and
                max(a[2] for a in ready["auras"] if a[0] == 10432) >= 99.9 and
                ready["damagePerFight"].get("26363", 0) == 0 and ready["bossDamagePerFight"] == 0,
                probe + ": pre-applied shield")
    flame = manifest["probe/SHAMAN-1-flame"]["measure"]
    require(flame["sampleSha256"] == general["SHAMAN 1"]["measure"]["sampleSha256"], "Elemental Flametongue")


def build_runner(engine, kind, work):
    path = work / ("runner-" + kind)
    path.mkdir(parents=True, exist_ok=True)
    main = path / "main.go"
    main.write_text(NATIVE_MAIN, encoding="utf8")
    files = [main]
    bundle = {"dps": ARCHIVE, "prepared": ARCHIVE, "tank": DOCS / "protocole-actualise-feral-tanks.zip",
              "cat": DOCS / "protocole-main-gauche-felin.zip"}[kind]
    with zipfile.ZipFile(bundle) as archive:
        for name in ("effects.go", "veildust.go") if kind == "cat" else ("effects.go",):
            target = path / name
            target.write_bytes(archive.read("runner/" + name))
            files.append(target)
    binary = path / ("replay.exe" if os.name == "nt" else "replay")
    env = dict(os.environ, CGO_ENABLED="0", GOARCH="amd64", GOAMD64="v1")
    flags = ["-tags=with_db"]
    if kind == "prepared":
        # Controlled counterfactual: the ordinary spell is already up; leave all resources,
        # random rolls, action timers and the historical APL alone.
        original = engine / "sim/shaman/shields.go"
        source = original.read_text(encoding="utf8")
        line = "shaman.LightningShieldAura = shaman.RegisterAura(spelldata.AuraConfig(lightningShieldRank))"
        require(source.count(line) == 1, "Unknown native shield implementation")
        source = source.replace(line, line + """
    shaman.LightningShieldAura.ApplyOnReset(func(aura *core.Aura, sim *core.Simulation) {
        aura.Activate(sim)
        aura.SetStacks(sim, aura.MaxStacks)
    })
""")
        patched = path / "shields.go"
        patched.write_text(source, encoding="utf8")
        overlay = path / "overlay.json"
        overlay.write_text(json.dumps({"Replace": {str(original): str(patched)}}), encoding="utf8")
        flags += ["-overlay", str(overlay)]
    subprocess.run(["go", "build", *flags, "-o", binary, *files], cwd=engine, env=env, check=True)
    return binary


def replay(args, manifest, requests):
    selected = {k: v for k, v in manifest.items() if k.startswith(args.prefix)}
    require(selected, "No matching request")
    work = args.work.resolve()
    runners = {}
    for kind in sorted({v["engine"] for v in selected.values()}):
        engine = args.dps_engine if kind in ("dps", "prepared") else args.tank_engine
        require(engine and engine.is_dir(), f"{kind}: missing --dps-engine or --tank-engine")
        runners[kind] = build_runner(engine.resolve(), kind, work)

    def run(item):
        key, row = item
        req = work / (key + ".request.json")
        res = req.with_suffix(".result.json")
        req.parent.mkdir(parents=True, exist_ok=True)
        req.write_text(json.dumps(requests[key]), encoding="utf8")
        subprocess.run([runners[row["engine"]], req, res], check=True, env=dict(os.environ, GOMAXPROCS="2"))
        require(summary(jsonfile(res)) == row["measure"], key + ": native results changed")
        return key

    with ThreadPoolExecutor(args.workers) as pool:
        for key in pool.map(run, selected.items()):
            print(key, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dps-engine", type=Path, help="WoWSims Forever " + DPS)
    parser.add_argument("--tank-engine", type=Path, help="WoWSims Forever " + TANK)
    parser.add_argument("--work", type=Path, default=Path(tempfile.gettempdir()) / "easybis-raid-buff-replay")
    parser.add_argument("--prefix", default="", help="Replay only matching keys, e.g. dps/PRIEST-3 or probe/")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    manifest, requests = read_archive()
    check_inputs(manifest, requests)
    if args.dps_engine or args.tank_engine:
        replay(args, manifest, requests)
    print(f"{len(manifest)} requests checked, 29 specializations covered")


if __name__ == "__main__":
    main()
