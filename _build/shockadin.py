"""The Shockadin: a Paladin list ForeverDB's data does not have.

ForeverDB's Paladin has three specs, Holy the healer, Protection the tank and Retribution the melee damage dealer.
This one is the Paladin who deals damage with Holy Shock, Judgement, Consecration and Seal of Righteousness in
spell damage gear. It is added as the Paladin's next spec (add, called by specs.apply). Its PvE list is ranked by
simulation, like the other damage dealers' (corrections/simulated.json: the build exists in WoWSims Forever); the
weights below rank its PvP list and its enchants, and estimate what the simulator cannot wear.

Where the weights come from
---------------------------
WoWSims Forever (https://github.com/wowsims/forever, MIT License) has no simulated Holy Paladin: its Holy spec is
a gear planner with no rotation. It does have this way of playing, as the "Holy Shock" build of its Retribution
Paladin (ui/specs/paladin/retribution at commit 21377c070b: builds/holy_shock.siml, apls/holy_shock.apl.siml,
gear_sets/holy_shock.gear.siml), and it publishes that build's stat weights, HolyShockEpWeights in presets.ts:
what a point of each stat adds to the build's damage, a point of attack power counting 1.

  the build     21 points in Holy (Improved Seals 5, Divine Precision 2, Holy Conduit 2, Divine Favor, Holy Shock)
                and 30 in Retribution (Conviction 3, Improved Judgement 2, Two-Handed Weapon Specialization 3,
                Vengeance 3, Champion of the Light 5), a two-hander in the hands
  the rotation  Judgement, Consecration, Seal of Righteousness kept up, Holy Strike, Holy Shock (with Divine
                Favor), Hammer of Wrath, Exorcism, in that order of priority

PVE is those weights divided by spell damage's 5.78, so that a point of spell damage counts 1 as in ForeverDB's
caster profiles. Stat by stat (ForeverDB's stat ids):

  42, 45 spell damage, spell power   5.78 -> 1       the reference
  84     Holy damage                 4.98 -> 0.862   as published; less than spell damage, probably because the
                                                     build's weapon oil (Shadow Oil) is of another school
  31     hit rating                 10.25 -> 1.773   one rating for the swings and the spells in Forever; 2.32 of it
                                                     is the Holy spells' share (PseudoStatSchoolHitPercentHoly)
  32     critical strike rating      4.66 -> 0.806   one rating for swings and spells
  36     haste rating                4.06 -> 0.702
  37     expertise rating            6.2  -> 1.073
  5      Intellect                   4.53 -> 0.784   Champion of the Light 5/5 turns 60% of Intellect into spell
                                                     damage; the rest is its critical strike chance and its mana
  4      Strength                    2.5  -> 0.433   2 attack power a point, raised by Divine Strength and Kings
  3      Agility                     3.11 -> 0.538   critical strike chance of the swings, the seal and Judgement
  38     attack power                1    -> 0.173
  43     mana per 5 seconds          0.01 -> 0.002   worth nothing there, which says the rotation does not run
                                                     out of mana in the simulator's 3-minute fight, with its raid
                                                     buffs, Judgement of Wisdom and potions
  47     spell penetration           0.01 -> 0.002   Holy damage is not resisted
  dps    the weapon's damage         13.04 -> 2.256  the swings, and Holy Strike's half of the weapon's damage
  7      Stamina                             0.1     not WoWSims': the 0.1 ForeverDB gives Stamina in the PvE
                                                     profiles of the Paladin's Holy and Retribution, as in 21 of
                                                     its 24 profiles that are not a tank's

Left out: armor penetration (0.26 -> 0.045), which ForeverDB's data has no stat id for among the listed items.

The weapon style is the two-hander ("2h"), and it is the build's own: Two-Handed Weapon Specialization adds 6% to
all its Physical and Holy damage, spells included, only while a two-hander is equipped; Holy Strike deals half
the weapon's damage; and a Seal of Righteousness hit is larger on a two-hander (sim/paladin/
seal_of_righteousness.go: weapon part x1.2 against x0.85, 0.12 of the spell damage a swing against 0.1). The
weights above are those of a build with a two-hander in the hands and say nothing of a one-hander with a shield,
so the list offers none: what such a set would do is not measured anywhere.

PVP is a guess, and named as one: nothing measures this build against players. It is PVE with three changes:
  7      Stamina 1 and 'armor' 0.02   what ForeverDB gives both the Paladin's Holy and Retribution PvP profiles
  31     hit rating 1.372             PVE's less the Holy spells' share (10.25 - 2.32, over 5.78): against a
                                      player of the same level a spell misses 4% of the time (sim/core/target.go)
                                      and Divine Precision gives the Holy spells 8%
Everything else keeps its PvE worth, mana per 5 seconds included, which is likely too low for a fight with no
raid buffs.

What weights cannot tell: the worth of hit is the one measured on WoWSims' set (about 40 rating); past the cap
(80 rating for the swings, 90 for the Holy spells against a level 63 target) it is worth nothing more, and a list
ranked item by item does not see it. An item's effect (a proc, a use) is not counted either.
"""
from __future__ import annotations

PALADIN = "PALADIN"
NAME, SLUG, ROLE, STYLE = "Shockadin", "shockadin", "Melee DPS", "2h"
SOURCE = "WoWSims Forever 21377c070b, ui/specs/paladin/retribution/presets.ts (HolyShockEpWeights)"

AGILITY, STRENGTH, INTELLECT, STAMINA = 3, 4, 5, 7
HIT, CRIT, HASTE, EXPERTISE, ATTACK_POWER = 31, 32, 36, 37, 38
SPELL_DAMAGE, MANA_PER_5, SPELL_POWER, SPELL_PENETRATION, HOLY_DAMAGE = 42, 43, 45, 47, 84

# HolyShockEpWeights as published: what a point of each stat is worth, attack power counting 1.
EP = {STRENGTH: 2.5, AGILITY: 3.11, INTELLECT: 4.53, SPELL_DAMAGE: 5.78, SPELL_POWER: 5.78, HOLY_DAMAGE: 4.98,
      SPELL_PENETRATION: 0.01, ATTACK_POWER: 1, HIT: 10.25, CRIT: 4.66, HASTE: 4.06, EXPERTISE: 6.2,
      MANA_PER_5: 0.01, "dps": 13.04}
EP_HOLY_SPELL_HIT = 2.32     # PseudoStatSchoolHitPercentHoly, per point of hit rating: the Holy spells' share of hit
REFERENCE = EP[SPELL_DAMAGE]

FOREVERDB_PVE_STAMINA = 0.1  # Stamina in the PvE profiles of the Paladin's Holy and Retribution
FOREVERDB_PVP_STAMINA = 1.0  # Stamina in the PvP profiles of the Paladin's Holy and Retribution
FOREVERDB_PVP_ARMOR = 0.02   # armor in those two profiles

PVE = {**{stat: round(value / REFERENCE, 3) for stat, value in EP.items()}, STAMINA: FOREVERDB_PVE_STAMINA}
PVP = {**PVE, HIT: round((EP[HIT] - EP_HOLY_SPELL_HIT) / REFERENCE, 3), STAMINA: FOREVERDB_PVP_STAMINA,
       "armor": FOREVERDB_PVP_ARMOR}


# The slots and the kinds of piece borrowed from the other classes' pools: armor and jewelry a Paladin can wear.
# Weapons stay the Paladin's own pool: which ones a Paladin can use is not in the data.
BORROWED_POOLS = ("head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "finger",
                  "trinket")
WEARABLE = frozenset(("4.0", "4.1", "4.2", "4.3", "4.4"))   # item class.subclass: miscellaneous, cloth to plate


def borrowed(db, data) -> dict:
    """{pool: [(item, level)]}: what the other classes' pools hold that the Paladin's lacks and a Paladin can wear.

    ForeverDB pools for a class what one of its three specs would wear, and none of the Paladin's is a caster who
    deals damage: WoWSims' own set for this build wears Magister's Leggings and Boots and Gauntlets of Elements,
    which the Paladin's pools do not hold. The class a piece is restricted to (corrections/classes.json) is checked
    where the list is built (ladders.full_ladder); a piece whose classes are not known (specs.load_class_unknown:
    the second dungeon sets, each a single class's in Classic) is not borrowed."""
    out = {}
    unknown = getattr(db, "class_unknown", None) or ()   # a class's own dungeon set, for all the data says: left out
    for pool in BORROWED_POOLS:
        own = {item_id for item_id, _ in data["pools"].get(pool, ())}
        found = {}
        for other in db.classes.values():
            for item_id, level in other["pools"].get(pool, ()):
                gear = db.gear.get(item_id)
                if item_id not in own and item_id not in unknown and gear and gear["kind"] in WEARABLE:
                    found[item_id] = min(level, found.get(item_id, level))
        out[pool] = sorted(found.items())
    return out


def add(db, enchants_for) -> tuple | None:
    """Add the Shockadin as the Paladin's next spec: (class, spec number), or None when the data has no Paladin.

    enchants_for(db, class, weights) ranks the enchants of a spec ForeverDB has no ranking for
    (specs.enchants_for): the Shockadin's are the ones ForeverDB lists for the Paladin's three specs, less the
    Zul'Gurub enchants of another class's quest, ranked on PVE. One whose effect is not plain stats (Crusader, a
    weapon's damage, an attack speed) is left out, its worth not being known."""
    data = db.classes.get(PALADIN)
    if not data or not data["specs"]:
        return None
    number = max(data["specs"]) + 1
    data["specs"][number] = {"name": NAME, "role": ROLE, "style": STYLE, "slug": SLUG,
                             "weights": {"lvl": dict(PVE), "raid": dict(PVE), "pvp": dict(PVP)}, "added": True}
    data["specs"][number]["pools"] = borrowed(db, data)
    per_spec = db.enchants.get(PALADIN)
    if per_spec is not None:
        # Only what ForeverDB lists for a Paladin: an enchant it lists for other classes alone is not known to be
        # one a Paladin can have. enchants_for itself leaves out another class's Zul'Gurub enchant (the Hunter's
        # Falcon's Call), which ForeverDB does list for the Paladin.
        own = {enchant for per_slot in per_spec.values() for entries in per_slot.values() for enchant, _ in entries}
        ranked = {key: [pair for pair in entries if pair[0] in own]
                  for key, entries in enchants_for(db, PALADIN, PVE).items()}
        for profile in ("lvl", "raid"):
            per_spec[(number, profile)] = {key: list(entries) for key, entries in ranked.items() if entries}
    return PALADIN, number
