"""The specs the lists add to ForeverDB's: on this branch, the Paladin's Shockadin (shockadin.py).

ForeverDB's data defines three specs per class. A list for another way of playing is a spec laid over them once
the data is read (apply, called by fdb.load, so the build and the tests rank the same database): it takes the
class's next number, is flagged "added", carries its own weights, and the class's pools, which are ForeverDB's,
are ranked on them like any other spec's. Nothing else tells an added spec from ForeverDB's: the ladders, the
data files and the addon read it as the class's fourth spec.

Branch tank-lists has a module of the same name with the same apply and enchants_for, which adds the Feral
Druid's cat and completes the tanks' weights. The enchant functions below are copied from it as they stood on
2026-11-21, so that the two merge into one: keep that branch's module, add shockadin.add to its apply, and keep
what this copy reads more than that one, which a caster's enchants need: Holy damage, the damage and the healing
of spells written apart or together, and mana regeneration (_SPELL_WORDS, _TOGETHER, _MANA).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import shockadin

STRENGTH, AGILITY, STAMINA, INTELLECT, SPIRIT = 4, 3, 7, 5, 6
DEFENSE, DODGE, HIT, CRIT, HASTE, EXPERTISE, ATTACK_POWER, RANGED_ATTACK_POWER = 12, 13, 31, 32, 36, 37, 38, 39
HEALING, SPELL_DAMAGE, MANA_PER_5, SPELL_POWER, HOLY_DAMAGE = 41, 42, 43, 45, 84
RATING_PER_PERCENT = {DODGE: 12, HIT: 10, CRIT: 14, HASTE: 10}


@dataclass
class Report:
    shockadin: tuple | None = None   # (class, spec) of the Shockadin added to the Paladin


def apply(db) -> Report:
    """Add the specs ForeverDB's data does not have."""
    return Report(shockadin=shockadin.add(db, enchants_for))


# -- enchants for a spec ForeverDB has no ranking for -------------------------------------------------------------

_STAT_WORDS = {"agility": AGILITY, "strength": STRENGTH, "stamina": STAMINA, "intellect": INTELLECT, "spirit": SPIRIT,
               "attack power": ATTACK_POWER, "ranged attack power": RANGED_ATTACK_POWER, "defense": DEFENSE,
               "armor": "armor", "spell power": SPELL_POWER}
_SPELL_WORDS = {"holy damage": HOLY_DAMAGE, "damage spells": SPELL_DAMAGE, "healing spells": HEALING,
                "healing": HEALING, "mana regen": MANA_PER_5}
# "+18 Spell Damage and Healing" is one stat, spell power: named before the sentence is cut at its "and".
_TOGETHER = ("spell damage and healing", "healing and spell damage")
_MANA = re.compile(r"^(\d+) mana per 5 sec$")              # "5 mana per 5 sec."
_PERCENT_WORDS = {"dodge": DODGE, "hit": HIT, "critical strike": CRIT, "critical strike chance": CRIT, "haste": HASTE}
_ALL_STATS = (STRENGTH, AGILITY, STAMINA, INTELLECT, SPIRIT)
_AMOUNT_LAST = re.compile(r"^([a-z ]+?) \+(\d+)(%?)$")     # "Agility +15", "Dodge +1%"
_AMOUNT_FIRST = re.compile(r"^\+(\d+)(%?) ([a-z ]+)$")     # "+9 Agility", "+1% Critical Strike"


def enchant_stats(effect: str) -> dict | None:
    """The stats of an enchant, read in ForeverDB's sentence for it ("Attack Power +28/Dodge +1%"); None when a part
    of it is not a plain stat this module knows (Crusader, Living Stats, weapon damage, attack speed): what such an
    enchant is worth to a spec is not known here, and it is left out rather than guessed."""
    stats = {}
    effect = effect.lower()
    for words in _TOGETHER:
        effect = effect.replace(words, "spell power")
    for part in re.split(r"/|,| and ", effect):
        part = part.strip().rstrip(".")
        mana = _MANA.match(part)
        if mana:
            stats[MANA_PER_5] = stats.get(MANA_PER_5, 0) + int(mana.group(1))
            continue
        found = _AMOUNT_LAST.match(part)
        if found:
            name, amount, percent = found.group(1), int(found.group(2)), found.group(3)
        else:
            found = _AMOUNT_FIRST.match(part)
            if not found:
                return None
            amount, percent, name = int(found.group(1)), found.group(2), found.group(3)
        if name == "all stats" and not percent:
            keys, per_point = _ALL_STATS, 1
        elif percent and name in _PERCENT_WORDS:
            keys, per_point = (_PERCENT_WORDS[name],), RATING_PER_PERCENT[_PERCENT_WORDS[name]]
        elif not percent and name in _STAT_WORDS:
            keys, per_point = (_STAT_WORDS[name],), 1
        elif not percent and name in _SPELL_WORDS:
            keys, per_point = (_SPELL_WORDS[name],), 1
        else:
            return None
        for key in keys:
            stats[key] = stats.get(key, 0) + amount * per_point
    return stats


def enchants_for(db, weights: dict) -> dict:
    """{slot key: [(enchant, level)], best first} for a spec ForeverDB ranks no enchant for: every enchant its lists
    hold for a slot key, whatever the class (they are the same vocabulary for all), ranked on the spec's weights.
    One whose effect is not plain stats, or is worth nothing to the spec, is left out."""
    seen = {}   # slot key -> {enchant: (level, its first place in ForeverDB's lists)}
    for per_spec in db.enchants.values():
        for (_, profile), per_slot in sorted(per_spec.items()):
            if profile != "raid":
                continue
            for key, entries in per_slot.items():
                known = seen.setdefault(key, {})
                for place, (enchant, level) in enumerate(entries):
                    old = known.get(enchant)
                    known[enchant] = (min(level, old[0]), min(place, old[1])) if old else (level, place)
    ranked = {}
    for key, known in seen.items():
        scored = []
        for enchant, (level, place) in known.items():
            stats = enchant_stats((db.enchant_info.get(enchant) or ["", ""])[1])
            value = sum(weights.get(stat, 0) * amount for stat, amount in (stats or {}).items())
            if value > 0:
                scored.append((-round(value, 3), place, enchant, level))
        if scored:
            ranked[key] = [(enchant, level) for _, _, enchant, level in sorted(scored)]
    return ranked
