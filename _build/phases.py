"""Which content phase an item arrives with.

ForeverDB's data has no phase: it lists the items the game's files hold and
where each one comes from. Many level 60 items come from Classic raids that
Forever does not have; their sources carry the label "Classic data". The phase
is worked out here, from an item's source groups and its listed sources (the
data lists two at most):

    0    before the raids: one way to get the item needs no raid
    1+   needs a raid of that Forever phase
    9    needs a raid known from Classic data only, not announced for Forever

Phase 1 is Forever's first raids, announced for 2026-12-09: Barrow Deeps,
Hyjal Summit and Onyxia's Lair. A list for a phase holds every item of that
phase and of the ones before.

Enchants get a phase the same way (enchant_phase): the ones applied from a
raid reward, and the ones whose formula drops in a raid.

To maintain: when ForeverDB's data brings a new raid, name its instance in
RAID_INSTANCES and give the raid a phase in RAID_PHASE; when a phase opens in
the game, raise CURRENT. Which quest, creature or formula belongs to which
Classic raid is Classic's own history, written down below by hand.
"""
from __future__ import annotations

import re

PRE_RAID = 0
LATER = 9

# The Forever phase each raid opens in. A raid missing here is a Classic one: LATER.
RAID_PHASE = {"onyxia": 1}

# The phase the game is in: what the addon shows until the player picks another.
CURRENT = PRE_RAID

PHASES = (PRE_RAID, *sorted(set(RAID_PHASE.values())), LATER)

# The game's instance id -> raid. A raid instance missing here is taken for the newest Forever phase.
# ForeverDB's data names Onyxia's Lair only; the Classic raids are named by the sources read in QuestieDB
# (questie.py): Molten Core, Blackwing Lair, Zul'Gurub, the two Ahn'Qiraj, Naxxramas.
RAID_INSTANCES = {249: "onyxia", 409: "mc", 469: "bwl", 309: "zg", 509: "aq", 531: "aq", 533: "naxx"}
NEW_RAID = "new"


def _by_id(raids: dict) -> dict:
    return {number: raid for raid, numbers in raids.items() for number in numbers}


# Quests that need a raid kill or a raid drop.
RAID_QUESTS = _by_id({
    # Onyxia's head (For All To See, Celebrating Good Times); Quel'Serrar is forged in her breath
    "onyxia": (7491, 7496, 7509),
    # A Hero's Reward (Hydraxian Waterlords)
    "mc": (7486,),
    # The Lord of Blackrock, Rise Thunderfury!, The Only Prescription, Nefarius's Corruption
    "bwl": (7782, 7784, 7787, 8620, 8730),
    # Mount Mugamba, Paragons of Power, the class necklaces, A Collection of Heads
    "zg": (8043, 8044, *range(8053, 8080), 8103, 8108, 8109, 8143, 8146, 8147, 8148, 8201),
    # the class sets of Ahn'Qiraj, the scepter chain, the Brood of Nozdormu rings, Ossirian, C'Thun, The Perfect Poison
    "aq": (8556, 8557, 8558, *range(8689, 8713), 8729, 8736, 8745, *range(8747, 8762), 8791, 8802, 9023),
    # Ramaladni's Icy Grasp, the frost resistance pieces, Atiesh
    "naxx": (9230, 9232, *range(9234, 9247), 9257, 9269, 9270, 9271),
})

# Creatures of a raid, and the world bosses a raid group kills.
RAID_CREATURES = _by_id({
    "mc": (11663, 11664),                                # Flamewaker Healer, Flamewaker Elite
    "aq": (15249,),                                      # Qiraji Lasher
    "world": (6109, 12397, 14887, 14888, 14889, 14890),  # Azuregos, Lord Kazzak, the four Emerald dragons
})

RAID_FACTIONS = {910: "aq"}  # Brood of Nozdormu
RAID_CHESTS = {"Four Horsemen Chest": "naxx"}

# Crafted pieces whose materials drop in a raid, by the name the data gives them. The data says which
# profession makes an item, not from what: this is Classic's recipes, and only the ones that are certain.
RAID_CRAFTS = _by_id({
    "onyxia": ("Onyxia Scale Breastplate", "Onyxia Scale Cloak"),
    # Fiery Core, Lava Core, Core Leather
    "mc": ("Black Amnesty", "Blackfury", "Blackguard", "Ebon Hand", "Nightfall",
           "Dark Iron Boots", "Dark Iron Bracers", "Dark Iron Destroyer", "Dark Iron Gauntlets", "Dark Iron Helm",
           "Dark Iron Leggings", "Dark Iron Reaver", "Fiery Chain Girdle", "Fiery Chain Shoulders",
           "Chromatic Gauntlets", "Corehound Belt", "Corehound Boots", "Lava Belt", "Molten Belt", "Molten Helm",
           "Wild Growth Spaulders", "Core Marksman Rifle", "Sulfuron Hammer",  # eight Sulfuron Ingots
           "Flarecore Gloves", "Flarecore Leggings", "Flarecore Mantle", "Flarecore Robe", "Flarecore Wraps"),
    # Bloodvine, Souldarite, Primal Bat and Tiger Leather
    "zg": ("Bloodvine Boots", "Bloodvine Leggings", "Bloodvine Vest",
           "Bloodsoul Breastplate", "Bloodsoul Gauntlets", "Bloodsoul Shoulders",
           "Darksoul Breastplate", "Darksoul Leggings", "Darksoul Shoulders",
           "Primal Batskin Bracers", "Primal Batskin Gloves", "Primal Batskin Jerkin",
           "Blood Tiger Breastplate", "Blood Tiger Shoulders"),
    # Obsidian shards
    "aq": ("Jagged Obsidian Shield", "Obsidian Mail Tunic", "Thick Obsidian Breastplate",
           "Heavy Obsidian Belt", "Light Obsidian Belt"),
    # Frozen Runes
    "naxx": ("Icebane Bracers", "Icebane Breastplate", "Icebane Gauntlets",
             "Icy Scale Bracers", "Icy Scale Breastplate", "Icy Scale Gauntlets",
             "Polar Bracers", "Polar Gloves", "Polar Tunic",
             "Glacial Cloak", "Glacial Gloves", "Glacial Vest", "Glacial Wrists"),
})

# Enchants that need a raid, by ForeverDB's id (s<spell>, i<item>): what is applied is a raid reward, or the
# formula drops from raid bosses. Classic's history again, and only what is certain.
RAID_ENCHANTS = _by_id({
    # Enchant Weapon - Spell Power, Healing Power: formulas from Molten Core's bosses
    "mc": ("s22749", "s22750"),
    # the class enchants made from Zul'Gurub's idols, the Zandalar signets (exalted with the Zandalar Tribe)
    "zg": (*(f"i{number}" for number in range(19782, 19791)), "i20076", "i20077", "i20078"),
    # Enchant Gloves - Threat, Shadow, Frost, Fire and Healing Power, Superior Agility; Enchant Cloak - Stealth,
    # Subtlety, Dodge: formulas from Ahn'Qiraj's bosses
    "aq": ("s25072", "s25073", "s25074", "s25078", "s25079", "s25080", "s25083", "s25084", "s25086"),
    # Sapphiron's shoulder enchants
    "naxx": ("i23545", "i23547", "i23548", "i23549"),
})

# Creatures whose name does not say where to look for an item, by the name the data gives them. The
# colossi of the Ahn'Qiraj war came once, for the opening of the gates, and dropped the world's epics as
# any boss does: ForeverDB lists one as a likely dropper of many world drops. Such a source means
# "world drop".
WORLD_DROPPERS = frozenset({"Colossus of Zora", "Colossus of Regal", "Colossus of Ashi"})

# Source kind -> the source groups it can stand for (an instance boss is "d", or "r" in a raid).
_STANDS_FOR = {
    "q": "qQ", "V": "ve", "v": "ve", "c": "c", "w": "w", "m": "wR", "R": "Rw", "o": "wxd", "x": "x", "p": "pv",
    "r": "e", "a": "d",
}


def raid_phase(raid: str) -> int:
    if raid == NEW_RAID:
        return max(RAID_PHASE.values())
    return RAID_PHASE.get(raid, LATER)


def source_raid(source: list[str], name: str = "") -> str | None:
    """The raid a source needs, or None when it needs none. name: the item's, for what a profession makes."""
    kind = source[0]
    number = int(source[1]) if len(source) > 1 and source[1].isdigit() else None
    if kind == "d":
        if len(source) > 4 and source[4] == "1":
            return RAID_INSTANCES.get(number, NEW_RAID)
        return None
    if kind == "q":
        return RAID_QUESTS.get(number)
    if kind in ("m", "R"):
        return RAID_CREATURES.get(number)
    if kind == "r":
        return RAID_FACTIONS.get(number)
    if kind == "o":
        return RAID_CHESTS.get(source[1])
    if kind == "c":
        return RAID_CRAFTS.get(name)
    return None


def source_phase(source: list[str], name: str = "") -> int:
    """The phase a source needs: PRE_RAID when it needs no raid."""
    raid = source_raid(source, name)
    return raid_phase(raid) if raid else PRE_RAID


def shown_sources(item: dict) -> list[list[str]]:
    """An item's sources in the order to show them: the addon says the first one of the item.

    The data lists the likeliest source first, and that one may need a raid when the item is listed
    for another way to get it: a source of a later phase goes after the others. A world dropper's line
    (WORLD_DROPPERS) is written as the data writes a world drop, w^0^0^label.
    """
    sources = []
    for source in item["sources"]:
        if source[0] in ("m", "R") and len(source) > 2 and source[2] in WORLD_DROPPERS:
            source = ["w", "0", "0", source[-1]]
        if source not in sources:
            sources.append(source)
    return sorted(sources, key=lambda source: source_phase(source, item["name"]))


def item_phase(item: dict) -> int:
    """The phase of an item of ForeverDB's source list (fdb.Database.items).

    The listed sources are the two most likely ones. A source group none of
    them stands for means there is another way to get the item, and the ways
    left out are ordinary ones (world drops, containers, vendors).

    A piece that is not of that list, added because the game has it (corrections.align), comes with its
    phase: nothing says where it is from, so it counts only once every phase does. So does an item of
    the list whose source was read in QuestieDB (corrections.fill): the phase that source needs.
    """
    if item.get("phase") is not None:
        return item["phase"]
    found, covered = [], set()
    for source in item["sources"]:
        raid = source_raid(source, item["name"])
        if source[0] == "d":
            covered.add("r" if raid else "d")
        else:
            covered.update(_STANDS_FOR.get(source[0], ""))
        found.append(raid_phase(raid) if raid else PRE_RAID)
    hidden = item["groups"] - covered - {"u", "r"}
    if hidden or not found:
        return PRE_RAID
    return min(found)


def enchant_phase(db, enchant: str) -> int:
    """The phase of an enchant of ForeverDB's list (fdb.Database.enchant_info).

    Besides RAID_ENCHANTS, an enchant whose source text says its recipe "drops
    in" a raid instance needs that raid, and so does one whose source, read in
    QuestieDB, is in a raid (corrections.fill, db.enchant_raids).
    """
    raid = RAID_ENCHANTS.get(enchant) or getattr(db, "enchant_raids", {}).get(enchant)
    if raid is None:
        where = (db.enchant_info.get(enchant) or ["", "", ""])[2]
        dropped = re.search(r"drops in ([^;]+)", where)
        if dropped:
            place = dropped.group(1).strip()
            for number, fields in db.instances.items():
                if fields[0] == place and len(fields) > 1 and fields[1] == "raid":
                    raid = RAID_INSTANCES.get(number, NEW_RAID)
    return raid_phase(raid) if raid else PRE_RAID


def unknown_raids(db) -> list[tuple[int, str]]:
    """Raid instances the data lists and RAID_INSTANCES does not: (id, name)."""
    return sorted((number, fields[0]) for number, fields in db.instances.items()
                  if len(fields) > 1 and fields[1] == "raid" and number not in RAID_INSTANCES)
