"""Weapon and relic eligibility for the single-pack ranged comparison."""
import json
from pathlib import Path


_records = json.loads((Path(__file__).parent / "corrections/aoe_relics.json").read_text(encoding="utf-8"))
RELICS = {int(item): record for item, record in _records["items"].items()}
# WoWSims RangedWeaponType. Hunters need a bow, crossbow or gun to use their shots.
RANGED_TYPES = {
    "HUNTER": {1, 2, 3}, "ROGUE": {1, 2, 3, 4}, "WARRIOR": {1, 2, 3, 4},
    "MAGE": {5}, "PRIEST": {5}, "WARLOCK": {5}, "DRUID": {6}, "PALADIN": {7}, "SHAMAN": {8},
}
# ForeverDB class.subclass identifiers, indexed by WoWSims RangedWeaponType.
CLIENT_KIND = {1: "2.2", 2: "2.18", 3: "2.3", 4: "2.16", 5: "2.19", 6: "4.8", 7: "4.7", 8: "4.9"}
# Effects that can apply to these builds' offensive spells, forms, or mana.
_SPEC_RELICS = {
    "DRUID": {1: (23197, 249441), 2: (23198, 272428),
              3: (23197, 249396, 249441, 272430), 4: (22397,)},
    "PALADIN": {1: (23203, 228175, 249442, 272435, 279248), 2: (249442, 272435),
                3: (249442, 272435), 4: (249442, 272435, 279248)},
    "SHAMAN": {1: (22395, 23199, 228176), 2: (22395, 23199, 228176, 272432),
               3: (22395, 23199, 228176, 249398, 272432, 272433)},
}


def relic_candidates(profile):
    return set(_SPEC_RELICS.get(profile["class"], {}).get(profile["spec"], ()))


def include_relics(db):
    """Make the relics' sources available without adding entries to any raid gear pool."""
    armor_kind = {"DRUID": "4.8", "PALADIN": "4.7", "SHAMAN": "4.9"}
    for item_id, record in RELICS.items():
        db.items.setdefault(item_id, {"name": record["name"], "groups": frozenset(record["group"]),
                            "side": "", "flags": "", "twin": None, "limit": None, "sources": [record["source"]]})
        db.gear.setdefault(item_id, {"inv": 28, "kind": armor_kind[record["class"]], "req": record["level"],
                                     "stats": {}, "dps": 0.0, "wand": False, "armor": 0.0})


def validate_candidate(profile, item_id, stats):
    import aoe_eligibility as rules
    cls = profile["class"]
    if cls in _SPEC_RELICS:
        if item_id not in relic_candidates(profile) or stats:
            raise ValueError(f"{cls}: unexpected relic or passive stats on {item_id}")
    elif cls == "HUNTER":
        if {"spell", "healing", "arcane", "fire", "frost", "nature", "shadow", "holy", "piercing"}.intersection(stats):
            raise ValueError(f"HUNTER: item {item_id} has caster stats")
    else:
        rules.validate_candidate(profile, item_id, stats)


def validate_client(profile, item_id, gear):
    allowed = {CLIENT_KIND[t] for t in RANGED_TYPES[profile["class"]]}
    if gear["kind"] not in allowed or gear["inv"] not in (15, 25, 26, 28) or gear["req"] > 60:
        raise ValueError(f"{profile['class']}: invalid ForeverDB ranged item {item_id}")


def validate_native(profile, item, client_gear=None):
    item_id = item["id"]
    if (item.get("type") != 14 or item.get("rangedWeaponType") not in RANGED_TYPES[profile["class"]]
            or item.get("reqLvl", 0) > 60):
        raise ValueError(f"{profile['class']}: invalid ranged weapon type for {item_id}")
    if client_gear is not None:
        validate_client(profile, item_id, client_gear)
        if client_gear["kind"] != CLIENT_KIND[item["rangedWeaponType"]]:
            raise ValueError(f"Ranged weapon type differs between WoWSims and ForeverDB for {item_id}")
    if item_id in RELICS:
        effects = sorted(effect.get("buffId") for effect in item.get("itemEffects", []))
        if effects != RELICS[item_id]["effects"]:
            raise ValueError(f"Native relic effects changed for {item_id}")
    elif item.get("rangedWeaponType") <= 5:
        damage = item.get("scalingOptions", {}).get("0", {})
        low, high = damage.get("weaponDamageMin", 0), damage.get("weaponDamageMax", 0)
        speed = item.get("weaponSpeed", 0)
        if speed <= 0 or low <= 0 or high < low:
            raise ValueError(f"Missing native ranged weapon damage for {item_id}")
        if client_gear is not None and abs((low + high) / (2 * speed) - client_gear["dps"]) > 0.051:
            raise ValueError(f"Ranged weapon DPS differs between WoWSims and ForeverDB for {item_id}")
