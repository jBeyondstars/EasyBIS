"""What the lists change in ForeverDB's specs: the tanks' weights, and a Feral Druid that is a cat.

ForeverDB's data has three tank specs (role "Tank"): Protection Paladin, Protection Warrior and the Druid's
Feral Combat, which its weights, its enchants and its coach all treat as a bear. Two things are laid over them
(fdb.load, so the build and the tests rank the same database).

1. A tank's weights are completed (complete). ForeverDB's PvE profiles of the tanks weigh no weapon damage at
   all, so a weapon was ranked on its stamina and hit alone and a caster's blade stood among a Warrior's main
   hands. A weight ForeverDB gives is never changed; one it does not give takes what the game's own conversions
   say it is worth by the weights the profile does have:
     attack power   = (strength - 0.05 * block value) / 2
                                            a point of Strength is 2 attack power for the three classes, and
                                            0.05 block value, which is taken off first where the profile weighs it
     weapon damage  = attack power * the attack power a point of damage per second is worth (DPS_IN_ATTACK_POWER)
                                            14 for a white swing: 14 attack power add 1 damage per second to it, and
                                            in Forever a Druid's paw is built from its weapon's damage per second
                                            too. That is the most it can be: attack power also feeds abilities a
                                            weapon's damage does not. Where WoWSims Forever publishes weights for
                                            the spec, the ratio between its two weights is used instead: 5.3 for the
                                            Protection Warrior (14.0 for the bear, the same; none for the Paladin)
     agility        = dodge * 12 * the dodge a point of Agility gives, in percent, + armor * 2
                                            12 dodge rating are 1% dodge, a point of Agility is 2 armor
     spell damage   = spell power           spell power is spell damage and healing: to a tank's threat they are
                                            the same thing (ForeverDB's Paladin weighs the one and not the other)
   The conversions are WoWSims Forever's at commit 21377c070b: 2 attack power per Strength in sim/druid/druid.go,
   sim/paladin/paladin.go and sim/warrior/warrior.go, the block value and the armor in sim/core/character.go, 14
   attack power per damage per second in sim/core/constants.go, the dodge in sim/core/base_stats.go
   (dodgePerAgility), the ratings in sim/core/base_stats_auto_gen.go, the paw in sim/druid/forms.go and
   docs/evidence/EV-0041. The weights do not count an item's proc or on-use effect. corrections.complete_shields
   supplies the intrinsic block value in addition to the equip bonus of shields.

2. The Feral Druid is two specs (split_feral). ForeverDB's stays what it is, the bear, under the name
   "Feral (Bear)" and its number. A new spec, "Feral (Cat)", takes the next number: its PvE weights are the damage
   per second a point of each stat adds to a cat, as WoWSims Forever publishes them (CAT_PVE), its PvP weights
   are ForeverDB's Feral ones, which are one profile for both forms, and its enchants are ForeverDB's, ranked on
   the cat's weights (enchants_for). Only two weapons carry attack power "in Cat, Bear and Dire Bear forms" in
   WoWSims Forever's item database, both from raids, and ForeverDB's data has that stat on no item: it is not
   weighed.

3. A tank is listed its own class's Zul'Gurub enchant only (own_enchants), and so is the cat. ForeverDB's lists
   give the head and leg enchants of that raid's class quests to several classes each (the Rogue's Death's
   Embrace to the Druid, the Warrior's Presence of Might to the Paladin); WoWSims Forever's item database binds
   each to one class (CLASS_ENCHANTS), as Classic does, and nothing read in Forever says otherwise. The other
   specs' lists have the same flaw and are left as ForeverDB has them here: this module is about the tanks.

4. An item whose worth to a role is mostly an effect is not given a figure it does not have (unvalued).
   corrections/effects.json names them by hand (for the tanks: The Lion Horn of Stormwind, whose 8 defense score
   half of the best trinket and whose armor proc scores nothing, Mark of Tyranny, Arena Grand Master, Quel'Serrar
   and Force Reactive Disk). In the lists of that role that are ranked on the
   weights, such an item has no score and stands level with the best picks, flag x: it is never a best pick
   itself, the addon shows it as their equal and prints no figure.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from dataclasses import dataclass, field

import shockadin

TANK = "Tank"
EFFECTS_FILE = Path(__file__).resolve().parent / "corrections" / "effects.json"
CLASSES_FILE = EFFECTS_FILE.with_name("classes.json")
HUNTER = "HUNTER"
MORTAL_STRIKE_COOLDOWN = 6.0
TWO_HAND_NORMALIZED_SPEED = 3.3
RANGED_ATTACK_POWER = 39
# Separate from hit rating: only attacks with ranged weapons benefit. These are the five items in
# the Hunter's pools with PseudoStatRangedHitPercent in WoWSims Forever 21377c070b, db.json.
RANGED_HIT_PERCENT = {13255: 3, 17754: 1, 18296: 1, 18388: 1, 22207: 1}
STRENGTH, AGILITY, STAMINA, INTELLECT, SPIRIT = 4, 3, 7, 5, 6
DEFENSE, DODGE, HIT, CRIT, HASTE, EXPERTISE, ATTACK_POWER, RANGED_ATTACK_POWER = 12, 13, 31, 32, 36, 37, 38, 39
SPELL_DAMAGE, SPELL_POWER, BLOCK_VALUE = 42, 45, 48
HEALING, MANA_PER_5, HOLY_DAMAGE = 41, 43, 84

ATTACK_POWER_PER_STRENGTH = 2
BLOCK_VALUE_PER_STRENGTH = 0.05
ATTACK_POWER_PER_DPS = 14   # a white swing's
# The attack power a point of a weapon's damage per second is worth, where WoWSims Forever 21377c070b publishes
# weights for the tank: MainHandDps over AttackPower. ui/specs/warrior/protection/presets.ts: 1.45 / 0.27 and
# 1.42 / 0.27 (its two builds), 5.3 between them; ui/specs/druid/feral_ep.ts (BearEp): 3.093 / 0.2209, 14.0.
DPS_IN_ATTACK_POWER = {"WARRIOR": 5.3, "DRUID": 14.0}
ARMOR_PER_AGILITY = 2
RATING_PER_PERCENT = {DODGE: 12, HIT: 10, CRIT: 14, HASTE: 10}
DODGE_PERCENT_PER_AGILITY = {"DRUID": 0.05, "PALADIN": 0.0506, "WARRIOR": 0.05}

DRUID, FERAL = "DRUID", "feral"       # the class, and the slug ForeverDB gives its Feral Combat spec
BEAR_NAME, CAT_NAME, CAT_SLUG = "Feral (Bear)", "Feral (Cat)", "feral-cat"
# CatEp of ui/specs/druid/feral_ep.ts, WoWSims Forever 21377c070b (MIT License): "Cat is DPS per stat", measured on
# its reference build at 7 to 8% hit. The stats ForeverDB's data has; the weapon's damage per second is its
# PseudoStatMainHandDps.
CAT_SOURCE = "WoWSims Forever 21377c070b, ui/specs/druid/feral_ep.ts (CatEp)"
CAT_PVE = {STRENGTH: 0.594, AGILITY: 0.655, ATTACK_POWER: 0.244, HIT: 0.521, CRIT: 0.506, HASTE: 0.393,
           EXPERTISE: 0.490, "dps": 2.142}
CAT_ROLE = "Melee DPS"

# The head and leg enchants of Zul'Gurub's class quests, by the item that applies them, and the one class each is
# for: classAllowlist of the enchants of WoWSims Forever's item database (assets/database/db.json, 21377c070b).
CLASS_ENCHANTS = {"i19782": "WARRIOR", "i19783": "PALADIN", "i19784": "ROGUE", "i19785": "HUNTER", "i19786": "SHAMAN",
                  "i19787": "MAGE", "i19788": "WARLOCK", "i19789": "PRIEST", "i19790": "DRUID"}


@dataclass
class Report:
    completed: dict = field(default_factory=dict)   # (class, spec, profile) -> {stat: the weight it was given}
    bear: tuple | None = None                       # (class, spec) of ForeverDB's Feral Combat
    cat: tuple | None = None                        # (class, spec) of the cat added next to it
    shockadin: tuple | None = None                  # (class, spec) of the Shockadin added to the Paladin
    ranged: dict = field(default_factory=dict)      # (class, spec, profile) of a Hunter -> the weight its attack
    #                                                 power got, the ranged attack power's added
    unbound: dict = field(default_factory=dict)     # (class, spec) of a tank -> the other classes' enchants its
    #                                                 lists no longer hold


def load_effects(path=EFFECTS_FILE) -> dict:
    """{item id: the roles whose weights cannot say what it is worth}, as corrections/effects.json holds them."""
    path = Path(path)
    if not path.exists():
        return {}
    return {int(item_id): frozenset(record["roles"])
            for item_id, record in json.loads(path.read_text(encoding="utf-8")).get("items", {}).items()}


def load_effects_but(path=EFFECTS_FILE) -> dict:
    """{item id: the specs of its roles it is not for, by slug} ("but" in corrections/effects.json): Hand of Justice
    is a melee damage dealer's and adds 5 DPS to a Shockadin, measured, where its best trinkets add 9."""
    path = Path(path)
    if not path.exists():
        return {}
    return {int(item_id): frozenset(record["but"])
            for item_id, record in json.loads(path.read_text(encoding="utf-8")).get("items", {}).items() if record.get("but")}


def load_placed(path=EFFECTS_FILE) -> dict:
    """{item id: the item it follows}: the items placed by hand in the lists ranked by simulation (the "placed" part of
    corrections/effects.json)."""
    path = Path(path)
    if not path.exists():
        return {}
    return {int(item_id): int(record["after"])
            for item_id, record in json.loads(path.read_text(encoding="utf-8")).get("placed", {}).items()}


def load_class_only(path=CLASSES_FILE) -> dict:
    """item -> the classes that can wear it, for the pooled items the game restricts to some (corrections/classes.json).
    ForeverDB sorts its pools by armor type: without this a Rogue's tier piece is listed for a Druid."""
    path = Path(path)
    if not path.exists():
        return {}
    items = json.loads(path.read_text(encoding="utf-8"))["items"]
    return {int(item_id): frozenset(entry["classes"]) for item_id, entry in items.items()}


def load_class_unknown(path=CLASSES_FILE) -> frozenset:
    """The pooled items whose classes are not known: the simulator's database does not have them (classes.json)."""
    path = Path(path)
    return frozenset(json.loads(path.read_text(encoding="utf-8")).get("unknown", ())) if path.exists() else frozenset()


def ranged_power(db, report: Report) -> None:
    """Count an item's attack power as the ranged attack power it also is, in a Hunter's weights. ForeverDB weighs
    "ranged attack power" and gives "attack power" next to nothing, or nothing: a Drake Fang Talisman's 56 scored 0."""
    for number, spec in db.classes.get(HUNTER, {}).get("specs", {}).items():
        for profile, weights in spec["weights"].items():
            if spec["role"] == "Ranged DPS" and HIT in weights:
                weights["ranged_hit"] = weights[HIT] * RATING_PER_PERCENT[HIT]
            if weights.get(RANGED_ATTACK_POWER):
                melee = spec.setdefault("melee_power", {})   # ForeverDB's own weight, kept: applying twice adds once
                melee.setdefault(profile, weights.get(ATTACK_POWER, 0))
                weights[ATTACK_POWER] = round(melee[profile] + weights[RANGED_ATTACK_POWER], 3)
                report.ranged[HUNTER, number, profile] = weights[ATTACK_POWER]


# The Lion Horn grants 725 armor. In 20,000 simulations per faction against a frontal physical boss
# (2 s swings) with Defender's Grip Stabilizer, its 30 s buff was active 23.72% of the time on both
# level-60 Protection Paladins. That gives 172 average armor outside Strongholds (WoWSims a73af71451).
LION_HORN_AVERAGE_ARMOR = 172


def protection_trinket_bonuses(weights: dict) -> dict:
    """Stat-weight contributions beyond the permanent defense or dodge already on the tooltip."""
    # The Mark gives 620 maximum health for 15 s every five minutes. Ten base health correspond to
    # one point of Stamina at this level. A planned use against a burst gives the full health buffer.
    stamina = 620 / 10 * 15 / 300
    return {14557: LION_HORN_AVERAGE_ARMOR * weights.get("armor", 0), 13966: stamina * weights.get(STAMINA, 0)}


def unvalued(db, cls: str, spec: int) -> frozenset:
    """The items a spec's weights cannot value: most of their worth to its role is an effect (db.effects). In a list
    ranked on the weights they get no score and stand level with the best picks (ladders.full_ladder)."""
    role, slug = db.classes[cls]["specs"][spec]["role"], db.classes[cls]["specs"][spec].get("slug")
    left_out = getattr(db, "effects_but", None) or {}   # item -> the specs of the role it is not for, by slug
    return frozenset(item_id for item_id, roles in (getattr(db, "effects", None) or {}).items()
                     if role in roles and slug not in left_out.get(item_id, ()))


def complete(weights: dict, cls: str) -> dict:
    """What a tank's weights lack, from the ones they have: {stat: weight}. Nothing ForeverDB gives is changed."""
    added = {}
    have = lambda stat: weights.get(stat, added.get(stat, 0))
    if ATTACK_POWER not in weights and have(STRENGTH):
        power = have(STRENGTH) - BLOCK_VALUE_PER_STRENGTH * have(BLOCK_VALUE)
        added[ATTACK_POWER] = round(power / ATTACK_POWER_PER_STRENGTH, 3)
    if "dps" not in weights and have(ATTACK_POWER):
        added["dps"] = round(have(ATTACK_POWER) * DPS_IN_ATTACK_POWER.get(cls, ATTACK_POWER_PER_DPS), 3)
    if SPELL_DAMAGE not in weights and have(SPELL_POWER):
        added[SPELL_DAMAGE] = have(SPELL_POWER)
    if AGILITY not in weights and cls in DODGE_PERCENT_PER_AGILITY and (have(DODGE) or have("armor")):
        dodge = have(DODGE) * RATING_PER_PERCENT[DODGE] * DODGE_PERCENT_PER_AGILITY[cls]
        added[AGILITY] = round(dodge + have("armor") * ARMOR_PER_AGILITY, 3)
    return added


def split_feral(db, report: Report) -> None:
    """Name ForeverDB's Feral Combat the bear it is, and add the cat as the Druid's next spec."""
    specs = db.classes.get(DRUID, {}).get("specs", {})
    bear = next((number for number, spec in specs.items() if spec["slug"] == FERAL and spec["role"] == TANK), None)
    if bear is None or any(spec["slug"] == CAT_SLUG for spec in specs.values()):
        return   # ForeverDB changed its Feral spec, or the cat is there already: nothing more is split
    cat = max(specs) + 1
    specs[bear]["name"] = BEAR_NAME
    pvp = dict(specs[bear]["weights"].get("pvp", {}))
    specs[cat] = {"name": CAT_NAME, "role": CAT_ROLE, "style": specs[bear]["style"], "slug": CAT_SLUG,
                  "weights": {"lvl": dict(CAT_PVE), "raid": dict(CAT_PVE), "pvp": pvp}, "added": True}
    db.classes[DRUID]["order"] = [number for spec in sorted(specs) if spec != cat
                                  for number in ((cat, spec) if spec == bear else (spec,))]
    per_spec = db.enchants.get(DRUID)
    if per_spec is not None:
        for profile in ("lvl", "raid"):
            per_spec[(cat, profile)] = enchants_for(db, DRUID, specs[cat]["weights"][profile])
    report.bear, report.cat = (DRUID, bear), (DRUID, cat)


def own_enchants(db, report: Report) -> None:
    """Take out of a tank's enchant lists the Zul'Gurub enchants that are another class's (CLASS_ENCHANTS)."""
    for cls, per_spec in db.enchants.items():
        for (number, _), per_slot in per_spec.items():
            if db.classes.get(cls, {}).get("specs", {}).get(number, {}).get("role") != TANK:
                continue
            for key, entries in per_slot.items():
                kept = [(enchant, level) for enchant, level in entries if CLASS_ENCHANTS.get(enchant, cls) == cls]
                if len(kept) != len(entries):
                    report.unbound.setdefault((cls, number), set()).update(
                        enchant for enchant, _ in entries if CLASS_ENCHANTS.get(enchant, cls) != cls)
                    per_slot[key] = kept


def apply(db) -> Report:
    """Complete the tanks' weights, leave them their own class's enchants, then split the Feral Druid: the cat's
    PvP weights are the completed ones, and its enchants are ranked among the ones a Druid can have."""
    report = Report()
    db.effects = load_effects()
    db.effects_but = load_effects_but()
    db.placed = load_placed()
    db.class_only = load_class_only()
    db.class_unknown = load_class_unknown()
    own_enchants(db, report)
    for cls, data in db.classes.items():
        for number, spec in data["specs"].items():
            if spec["role"] != TANK:
                continue
            for profile, weights in spec["weights"].items():
                added = complete(weights, cls)
                if added:
                    weights.update(added)
                    report.completed[cls, number, profile] = added
    ranged_power(db, report)
    # Preserve the published DPS weight for a 3.3-second weapon. A two-hander with the same
    # DPS but a different base damage roll gains or loses that difference on one Mortal Strike.
    arms = db.classes.get("WARRIOR", {}).get("specs", {}).get(1)
    if arms and arms.get("slug") == "arms":
        pvp = arms["weights"]["pvp"]
        pvp["weapon_hit"] = pvp["dps"] / (MORTAL_STRIKE_COOLDOWN + TWO_HAND_NORMALIZED_SPEED)
    split_feral(db, report)
    paladin = db.classes.get(shockadin.PALADIN, {}).get("specs", {})
    if not any(spec.get("slug") == shockadin.SLUG for spec in paladin.values()):   # applying twice adds it once
        report.shockadin = shockadin.add(db, enchants_for)
    return report


def order(db, cls: str) -> list:
    """A class's specs in the order the addon lists them: ForeverDB's, the cat before the bear."""
    data = db.classes[cls]
    return list(data.get("order") or sorted(data["specs"]))


# -- enchants for a spec ForeverDB has no ranking for -------------------------------------------------------------

_STAT_WORDS = {"agility": AGILITY, "strength": STRENGTH, "stamina": STAMINA, "intellect": INTELLECT, "spirit": SPIRIT,
               "attack power": ATTACK_POWER, "ranged attack power": RANGED_ATTACK_POWER, "defense": DEFENSE,
               "armor": "armor", "spell power": SPELL_POWER}
# What a caster's enchants add to those: a school's damage, the damage and the healing of spells written apart or
# together ("+18 Spell Damage and Healing" is one stat, spell power: named before the sentence is cut at its
# "and"), and mana regeneration ("5 mana per 5 sec.").
_SPELL_WORDS = {"holy damage": HOLY_DAMAGE, "damage spells": SPELL_DAMAGE, "healing spells": HEALING,
                "healing": HEALING, "mana regen": MANA_PER_5}
_TOGETHER = ("spell damage and healing", "healing and spell damage")
_MANA = re.compile(r"^(\d+) mana per 5 sec$")
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


def enchants_for(db, cls: str, weights: dict) -> dict:
    """{slot key: [(enchant, level)], best first} for a spec ForeverDB ranks no enchant for: every enchant its lists
    hold for a slot key, whatever the class (they are one vocabulary for all, but for the enchants of another
    class, CLASS_ENCHANTS), ranked on the spec's weights. One whose effect is not plain stats, or is worth nothing
    to the spec, is left out."""
    seen = {}   # slot key -> {enchant: (level, its first place in ForeverDB's lists)}
    for per_spec in db.enchants.values():
        for (_, profile), per_slot in sorted(per_spec.items()):
            if profile != "raid":
                continue
            for key, entries in per_slot.items():
                known = seen.setdefault(key, {})
                for place, (enchant, level) in enumerate(entries):
                    if CLASS_ENCHANTS.get(enchant, cls) != cls:
                        continue
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
