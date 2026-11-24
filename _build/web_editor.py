"""Generate the local editor snapshot using the addon's own browsing and scoring logic.

python _build/web_editor.py
Requires lupa and GearQuestForever installed beside EasyBIS. Reads ForeverDB item metadata
and supplements GearQuest tooltips from Wowhead Forever. Cached inputs may be supplied.
"""
import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_build/tests"))
from test_addon import CLASSES, Game, no_pictures, strip_colors

ARMOR = {0: "Accessory", 1: "Cloth", 2: "Leather", 3: "Mail", 4: "Plate",
         6: "Shield", 7: "Libram", 8: "Idol", 9: "Totem"}
WEAPON = {0: "Axe", 1: "Two-Handed Axe", 2: "Bow", 3: "Gun", 4: "Mace",
          5: "Two-Handed Mace", 6: "Polearm", 7: "Sword", 8: "Two-Handed Sword",
          10: "Staff", 13: "Fist Weapon", 14: "Miscellaneous", 15: "Dagger",
          16: "Thrown", 18: "Crossbow", 19: "Wand", 20: "Fishing Pole"}
ACCESSORIES = {2: "Neck", 11: "Ring", 12: "Trinket", 16: "Cloak", 23: "Held In Off-hand"}


def load_audit(addons):
    tooltips = {}
    sources = addons / "GearQuestForever"
    audit = sources / "_generated/Data.ForeverAudit.generated.lua"
    for line in audit.read_text(encoding="utf-8").splitlines():
        match = re.match(r'\s*\[(\d+)\]=\{status="ok",.*?tip=("(?:[^"\\]|\\.)*")', line)
        if match:
            tooltips[int(match[1])] = json.loads(match[2]).splitlines()
    for path in sorted(addons.glob("GearQuestForever_*/AuditTips.lua")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = re.match(r'\s*\[(\d+)\]=("(?:[^"\\]|\\.)*"),', line)
            if match:
                tooltips[int(match[1])] = json.loads(match[2]).splitlines()
    # Blizzard's C_Map is unavailable in the standalone runtime.
    zones = (sources / "Locales/Zones.lua").read_text(encoding="utf-8")
    maps = {int(number): name for name, number in re.findall(r'\["([^"]+)"\]\s*=\s*-(\d+)', zones)}
    return tooltips, maps


def read_json(path, url):
    if path and path.is_file():
        return json.loads(path.read_bytes())
    with urlopen(url, timeout=30) as response:
        raw = response.read()
    result = json.loads(raw)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return result


def item_metadata(item, catalog, tips, cache):
    record = catalog[item]
    kind = ACCESSORIES.get(record["inv"]) or (ARMOR if record["c"] == 4 else WEAPON)[record["sc"]]
    lines = tips.get(item)
    if not lines:
        path = cache / f"{item}.json" if cache else None
        tip = read_json(path, f"https://nether.wowhead.com/tooltip/item/{item}?dataEnv=16&locale=0")
        # Keep the display lines and use EasyBIS as the authority on where an item drops.
        html = re.split(r'<div class="whtt-(?:sellprice|extra)', tip["tooltip"])[0]
        html = re.sub(r"</?(?:td|th|br|div|li)\b[^>]*>", "\n", html, flags=re.I)
        plain = unescape(re.sub(r"<[^>]+>", "", html))
        lines = [line.strip() for line in plain.splitlines() if line.strip() and line.strip() != tip["name"]]
    lines = [s for s in lines if not s.startswith(("Sell Price:", "Durability "))]
    return {"type": kind, "quality": record["q"], "lines": lines, "icon": f'icons/{record["ic"]}.webp'}


def generate(catalog_path=None, tooltip_cache=None):
    tips, maps = load_audit(ROOT.parent)
    catalog = {r["id"]: r for r in read_json(catalog_path, "https://foreverdb.net/data/items.json")}
    game = Game(locale="frFR")
    ns = game.ns
    # Nine alternatives plus the best pick. The in-game slider stops at six.
    ns.Alternatives = game.lua.eval("function() return 9 end")
    game.lua.globals().C_Map.GetMapInfo = lambda i: game.lua.table_from({"name": maps[i]}) if i in maps else None
    classes, profiles, items = {}, {}, {}
    for token in CLASSES:
        classes[token] = [{"id": s.index, "name": s.name} for s in ns.Ladders.Specs(token).values()]
        for spec in classes[token]:
            for side in ("a", "h"):
                ns.SetSide(ns, side)
                for mode in ("pve", "pvp"):
                    key = f'{token}:{spec["id"]}:{mode}:{side}'
                    slots = {s: [] for s in ns.SLOTS.values()}
                    profiles[key] = slots
                    state = game.lua.table_from({"class": token, "spec": spec["id"], "list": mode})
                    rows, _ = ns.Rows.Items(state, True)
                    for row in rows.values():
                        if row.kind != "item":
                            continue
                        picks = slots[row.slot]
                        item = row.id
                        if len(picks) == 10 or any(pick["id"] == item for pick in picks):
                            continue
                        pick = {"id": item, "score": 100 + row.gap if row.gap is not None else None}
                        if row.bis:
                            pick["bis"] = True
                        if row.option:
                            pick["option"] = row.option.label
                            pick["duel"] = ns.Ladders.OptionNote(row.option)
                        picks.append(pick)
                        src = row.source
                        source_type = ns.Sources.CategoryName(src.category)
                        detail = ns.Sources.WithCost(ns.Sources.Line(src), src.cost)
                        detail = no_pictures(strip_colors(detail))
                        if item not in items:
                            items[item] = dict(item_metadata(item, catalog, tips, tooltip_cache),
                                               name=ns.Items.Get(item).name, source=detail, sourceType=source_type)
                        for field, value in (("source", detail), ("sourceType", source_type)):
                            if value != items[item][field]:
                                pick[field] = value
    return dict(version=ns.data.meta.version, classes=classes, profiles=profiles, items=items)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--tooltip-cache", type=Path)
    args = parser.parse_args()
    result = generate(args.catalog, args.tooltip_cache)
    output = ROOT / "docs/bis-editor/data.js"
    output.parent.mkdir(parents=True, exist_ok=True)
    credit = ("// Data from ForeverDB.net (https://foreverdb.net). See NOTICE.txt. "
              "Tooltips from GearQuest Forever and Wowhead Forever.\n")
    output.write_text(credit + "window.BIS_DATA=" + json.dumps(result, ensure_ascii=False, separators=(",", ":"))
                      + ";\n", encoding="utf-8")
    print(f'{len(result["profiles"])} profiles, {len(result["items"])} distinct items')
