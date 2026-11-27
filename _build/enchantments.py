"""Acquisition and utility options verified in the 2026-11-25 enchant audit."""

COMMERCE_FACTIONS = {"a": (2586, "Azeroth Commerce Authority"), "h": (2587, "Durotar Supply and Logistics")}
COMMERCE_VENDORS = {"a": (256732, "Alynsia", 1433, 11.2, 71.5), "h": (248199, "Beneris", 1413, 49.7, 29.8)}
COMMERCE_SOURCE = "Alynsia (Redridge Mountains, Alliance) or Beneris (The Barrens, Horde)"

UNAVAILABLE = frozenset({"i273596"})  # PTR-only application item

_SOURCE = {
    "i252462": ("Leatherworking 185: recipe Pattern: Mystic Thick Armor Kit, from the quest Leather Technique", "s"),
    "i252488": ("Leatherworking 235: recipe Pattern: Forceful Rugged Armor Kit, sold by "
                "Nioma (The Hinterlands, Alliance) or Jangdor Swiftstrider (Feralas, Horde)", "s"),
    "i18283": ("Engineering 300: recipe Schematic: Biznicks 247x128 Accurascope, drops in Molten Core", "k"),
    "i279272": ("Engineering 300: recipe Schematic: SAF-T Ultra Precision Scope", "c"),
    "i273592": ("Enchanting 300: recipe Formula: Enchant Shield - Law of Nature; "
                "requires Revered with Timbermaw Hold. Meilosh's stock is unconfirmed", "c"),
    "i273593": ("Enchanting 300: recipe Formula: Enchant Chest - Living Stats; "
                "requires Ahn'Qiraj reagents. No live recipe source confirmed", "c"),
    "i273597": ("where it comes from isn't known yet", "c"),
    "s1248498": ("Enchanting 205: recipe Formula: Enchant Bracer - Lesser Healing Power, from the quest Mysterious "
                 "Mysticism; also sold by Gorhak (Desolace)", "s"),
    "s1219580": ("Enchanting 300: recipe Formula: Enchant 2H Weapon - Spellblasting, sold by "
                 + COMMERCE_SOURCE + "; 240 Merchant's Favor", "s"),
}

_OPTIONS = {
    "s1328948": ("Enchant Boots - Speed", "+8% Movement Speed", "Enchanting 280: recipe Formula: "
                 "Enchant Boots - Speed, sold by " + COMMERCE_SOURCE + "; 180 Merchant's Favor", "s"),
    "s13890": ("Enchant Boots - Minor Speed", "+4% Movement Speed", "Enchanting 225: from a trainer", "f"),
    "s1248805": ("Enchant Weapon - Revelation", "A non-critical direct spell can grant critical chance to your next "
                 "direct spell", "Enchanting 140: recipe Formula: Enchant Weapon - Revelation, sold by "
                 + COMMERCE_SOURCE + "; 45 Merchant's Favor", "s"),
    "s1248757": ("Enchant Weapon - Insight", "Chance to temporarily increase Spirit when casting a spell",
                 "Enchanting 140: recipe Formula: Enchant Weapon - Insight, sold by "
                 + COMMERCE_SOURCE + "; 45 Merchant's Favor", "s"),
    "s1248760": ("Enchant Weapon - Recovery", "Heals for 5% of maximum health when your attack is dodged or parried. "
                 "10 sec cooldown", "Enchanting 140: recipe Formula: Enchant Weapon - Recovery, sold by "
                 + COMMERCE_SOURCE + "; 45 Merchant's Favor", "s"),
}

REPUTATION_RECIPES = {
    "s1219580": (274394, "Formula: Enchant 2H Weapon - Spellblasting", 300),
    "s1328948": (289560, "Formula: Enchant Boots - Speed", 280),
}


def info(db, enchant):
    if enchant in _OPTIONS:
        return _OPTIONS[enchant]
    name, effect, where, origin = (db.enchant_info[enchant] + [""] * 4)[:4]
    return name, effect, *_SOURCE.get(enchant, (where, origin))


def options(cls, role):
    weapons = []
    if cls not in ("WARRIOR", "ROGUE"):
        weapons.extend(("s1248805", "s1248757"))
    if role in ("Melee DPS", "Tank"):
        weapons.append("s1248760")
    return {"feet": ("s1328948", "s13890"), "w1h": weapons, "w2h": weapons}
