"""Dungeon priorities. The historical 15-second rotations are kept separately."""
import copy
import json
from functools import lru_cache


# The short-pack versions of these builds are dedicated AoE rotations. When
# there is one enemy left, use the priority list for the same build in WoWSims.
SINGLE_TARGET = {
    ("DRUID", 1): "druid/balance/apls/default.apl.json",
    ("MAGE", 1): "mage/dps/apls/arcane.apl.json",
    ("MAGE", 2): "mage/dps/apls/deepFire.apl.json",
    ("WARLOCK", 1): "warlock/dps/builds/aff_wrack.build.json",
    ("WARLOCK", 2): "warlock/dps/builds/demo_fire_brand.build.json",
    ("WARLOCK", 3): "warlock/dps/builds/destro.build.json",
}


def _compare(value, operator, threshold):
    return {"cmp": {"lhs": value, "op": operator, "rhs": {"const": {"val": threshold}}}}


def _current_target(value):
    # Raid presets may address the first boss by index. That unit is already
    # dead on the second pull. All these actions run against a single survivor.
    if isinstance(value, list):
        return [_current_target(v) for v in value]
    if isinstance(value, dict):
        if value.get("type") == "Target":
            return {"type": "CurrentTarget"}
        return {k: _current_target(v) for k, v in value.items()}
    return value


def _class_actions(rows):
    # Candidate/companion use and external consumables are controlled by the
    # equipment request, including the explicit passive comparison.
    return [row for row in rows if not (
        {"itemId", "otherId"} & row["action"].get("castSpell", {}).get("spellId", {}).keys()
        or "autocastOtherCooldowns" in row["action"])]


@lru_cache
def _preset(root, path):
    source = json.loads((root / "ui" / "specs" / path).read_text(encoding="utf-8"))
    rotation = source["player"]["rotation"] if "player" in source else source
    return _current_target(rotation)


def route_rotation(profile, request_rotation, wowsims_root):
    apl = copy.deepcopy(request_rotation)
    cls, spec = profile["class"], profile["spec"]
    multi = _compare({"numberTargets": {}}, "OpGe", "2")
    for entries in [apl["priorityList"], *(g["actions"] for g in apl.get("groups", []))]:
        for row in entries:
            action = row["action"]
            spell = action.get("castSpell", {}).get("spellId", {}).get("spellId")
            if cls == "SHAMAN" and spell == 10587:
                expired = _compare({"totemRemainingTime": {"totemType": "Fire"}}, "OpLe", "0s")
                action["condition"] = {"and": {"vals": [multi, expired]}}
            if cls == "HUNTER" and spell == 14295:  # Volley needs multiple targets.
                action["condition"] = {"and": {"vals": [multi, action["condition"]]}}

    if (cls, spec) == ("PRIEST", 3):
        # Shoot can start on the GCD and clip Mind Flay. Only fill an actual
        # low-mana gap, and yield to higher-priority spells when mana recovers.
        flay = {"spellId": 18807}
        needs_mana = {"cmp": {"op": "OpLt", "lhs": {"currentMana": {}},
                              "rhs": {"spellCurrentCost": {"spellId": flay}}}}
        guards = [{"gcdIsReady": {}}, {"not": {"val": {"spellIsChanneling": {"spellId": flay}}}}, needs_mana]
        apl["priorityList"].append({"action": {
            "condition": {"and": {"vals": guards}},
            "channelSpell": {"spellId": {"spellId": 5019}, "interruptIf": {"const": {"val": "true"}}},
        }})

    path = SINGLE_TARGET.get((cls, spec))
    if path is None:
        return apl
    preset = copy.deepcopy(_preset(wowsims_root, path))
    group = "Dungeon single target"
    single = _compare({"numberTargets": {}}, "OpEq", "1")
    groups = apl.setdefault("groups", [])
    groups.extend(dict(g, actions=_class_actions(g["actions"])) for g in preset.get("groups", []))
    groups.append({"name": group, "actions": _class_actions(preset["priorityList"])})
    apl.setdefault("valueVariables", []).extend(preset.get("valueVariables", []))
    # Keep the request's item activations and cooldowns ahead of the new branch.
    priorities = apl["priorityList"]
    pos = next((n for n, row in enumerate(priorities)
                if "autocastOtherCooldowns" not in row["action"]
                and "itemId" not in row["action"].get("castSpell", {}).get("spellId", {})), len(priorities))
    priorities.insert(pos, {"action": {"condition": single, "groupReference": {"groupName": group}}})
    if cls == "DRUID":
        # Cast Wrath during a gap in Hurricane availability, including on packs.
        priorities.append({"action": {"castSpell": {"spellId": {"spellId": 9912}}}})
    return apl
