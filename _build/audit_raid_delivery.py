"""Verify the per-faction Raid layers actually shipped in Data/Lists.lua, and replay their native inputs."""
import argparse
import json
import os
import re
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from audit_raid_buffs import BUILD, DOCS, digest, jsonfile, require, summary


ARCHIVE = DOCS / "protocole-buffs-raid-livraison.zip"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def live_rows(path):
    rows = []
    cls = None
    for line in path.read_text(encoding="utf8").splitlines():
        if match := re.fullmatch(r"(\w+) = \[==\[", line):
            cls = match[1]
        fields = line.split("\t")
        if len(fields) >= 3 and fields[0] in {"F", "L", "T", "M"} and "pve" in fields[:3]:
            rows.append(cls + "\t" + line)
    return rows


def check_effects(row):
    spec, m = row["spec"], row["measure"]
    cls = spec.split()[0]
    full = {"MAGE": [22783], "HUNTER": [14322, 20906], "PALADIN": [10301],
            "PRIEST": [10952, 15473], "WARLOCK": [11735], "SHAMAN": [10612]}
    by_spec = {"DRUID 1": [24858], "WARLOCK 1": [18789], "WARLOCK 2": [18791, 19028, 412732],
               "SHAMAN 2": [16362], "WARRIOR 1": [2457]}
    for spell in full.get(cls, []) + by_spec.get(spec, []):
        require(any(i == spell and u >= 99.9 for i, _, u in m["auras"]), f"{spec}: aura {spell}")
    if spec == "DRUID 4":
        floor = 99.9 if row["source"] in ("feral_trinkets", "relics") else 99
        require(any(i == 768 and u >= floor for i, _, u in m["auras"]), "Cat Form in release")
    if cls in ("HUNTER", "WARLOCK"):
        pets = {"HUNTER 1": {"Raptor", "Hawk 1", "Hawk 2"}, "WARLOCK 2": {"Imp"}, "WARLOCK 3": {"Succubus"}}
        require(set(m["pets"]) == pets.get(spec, set()), spec + ": pets")
    if cls == "ROGUE":
        require(all(m["damagePerFight"].get(str(i), 0) > 0 for i in (11337, 11354)), spec + ": poisons")


def verify(release=None):
    with zipfile.ZipFile(ARCHIVE) as archive:
        data = json.loads(archive.read("index.json"))
        actual = live_rows(BUILD.parent / "Data/Lists.lua")
        require(digest(canonical(actual)) == data["clientRowsSha256"], "Installed Raid rows differ from audit")
        excluded = set(data["disqualifiedItems"])
        for row in actual:
            fields = row.split("\t")
            entries = fields[-1].split()
            if fields[1] in ("L", "F"):
                ids = {int(entry.split(":", 1)[0]) for entry in entries}
            elif fields[1] == "T":
                ids = {int(i) for i in entries[:2]}  # Measured tank comparison and its rival.
            else:
                continue
            require(not excluded.intersection(ids), "Disqualified item in Raid row " + " ".join(fields[:-1]))
        objects = set()
        for desc in data["drivers"].values():
            objects.update(desc["source"].values())
            objects.update(desc["overlays"].values())
        for key, row in data["runs"].items():
            objects.add(row["job"])
            m = row["measure"]
            check_effects(row)
            require(m["iterations"] >= 2000, key + ": native iterations")
            if "expectedDps" in row:
                require(abs(m["dps"] - row["expectedDps"]) < 0.00001, key + ": published native replay")
            if "comparison" in row:
                o = data["runs"][row["comparison"]]["measure"]
                require(o["sampleSha256"] == m["sampleSha256"] and m["bossDamagePerFight"] == 0 and
                        any(i == 10432 and u >= 99.9 for i, _, u in m["auras"]) and
                        m["damagePerFight"].get("26363", 0) == 0, key + ": pre-applied shield")
        for h in objects:
            require(digest(archive.read("blobs/" + h)) == h, "Corrupt release replay object " + h)
        if release:
            for name, hashed in data["sourceRecordSha256"].items():
                require(digest(canonical(jsonfile(release / "_build/corrections" / (name + ".json")))) == hashed,
                        "Release archive differs: " + name)
        return data


def export_shaman_jobs(data, destination):
    """Emit the normal driver input with the learned shield selected in its prepull APL."""
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in data["runs"].values():
            if "comparison" not in row:
                continue
            original = data["runs"][row["comparison"]]
            job = json.loads(archive.read("blobs/" + original["job"]))
            [character] = [p for g in job["base"]["raid"]["parties"] for p in g.get("players", [])]
            count = 0
            for entry in character["rotation"]["prepullActions"]:
                spell = entry["action"].get("castSpell", {}).get("spellId", {})
                if spell.get("spellId") == 408510:
                    spell["spellId"] = 10432
                    count += 1
            require(count == 1, "Expected exactly one unavailable Water Shield prepull")
            target = destination / (row["comparison"] + ".json")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(canonical(job))


def compile_driver(archive, data, kind, root, work):
    desc = data["drivers"][kind]
    require(root.is_dir(), f"Missing checkout for {desc['revision']}")
    path = work / ("runner-" + kind)
    path.mkdir(parents=True, exist_ok=True)
    files = []
    for name, h in desc["source"].items():
        target = path / name
        target.write_bytes(archive.read("blobs/" + h))
        files.append(target)
    replacements = {}
    for relative, h in desc["overlays"].items():
        target = path / ("overlay-" + h + ".go")
        target.write_bytes(archive.read("blobs/" + h))
        replacements[str(root / relative)] = str(target)
    overlay = path / "overlay.json"
    overlay.write_bytes(canonical({"Replace": replacements}))
    exe = path / ("replay.exe" if os.name == "nt" else "replay")
    subprocess.run(["go", "build", "-tags=with_db", "-overlay", overlay, "-o", exe, *files], cwd=root,
                   env=dict(os.environ, GOARCH="amd64", GOAMD64="v1", CGO_ENABLED="0"), check=True)
    return exe


def replay(data, engines, prefix, work, workers):
    runs = {k: v for k, v in data["runs"].items() if k.startswith(prefix)}
    require(runs, "No matching release run")
    with zipfile.ZipFile(ARCHIVE) as archive:
        binaries = {}
        for kind in sorted({v["kind"] for v in runs.values()}):
            rev = data["drivers"][kind]["revision"]
            root = engines.get(rev[:8], engines.get(rev))
            require(root is not None, "Missing --engine " + rev + "=PATH")
            binaries[kind] = compile_driver(archive, data, kind, root, work)
        jobs = {k: archive.read("blobs/" + v["job"]) for k, v in runs.items()}

    def run(key):
        row = runs[key]
        folder = work / key
        folder.mkdir(exist_ok=True, parents=True)
        source = folder / "job.json"
        source.write_bytes(jobs[key])
        target = folder / "reference"
        subprocess.run([binaries[row["kind"]], "evidence", target, source], check=True,
                       env=dict(os.environ, GOMAXPROCS="2"))
        req = jsonfile(folder / "reference.request.json")
        res = jsonfile(folder / "reference.result.json")
        require(digest(canonical(req)) == row["requestSha256"], key + ": effective request")
        require(summary(res) == row["measure"], key + ": native outcome")
        return key

    with ThreadPoolExecutor(workers) as pool:
        for key in pool.map(run, runs):
            print(key, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, help="Optional EasyBIS 1.9.5 checkout with the source scoring records")
    parser.add_argument("--engine", action="append", default=[], metavar="REV=PATH", help="Pinned WoWSims checkout")
    parser.add_argument("--export-shaman", type=Path, help="Write the six corrected driver jobs for the learned shield")
    parser.add_argument("--prefix", default="")
    parser.add_argument("--work", type=Path, default=Path(tempfile.gettempdir()) / "easybis-raid-release-replay")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    data = verify(args.release)
    if args.export_shaman:
        export_shaman_jobs(data, args.export_shaman)
    if args.engine:
        engines = {rev: Path(root).resolve() for rev, root in (s.split("=", 1) for s in args.engine)}
        replay(data, engines, args.prefix, args.work.resolve(), args.workers)
    print(f"{len(data['runs'])} release requests checked against installed Raid rows")


if __name__ == "__main__":
    main()
