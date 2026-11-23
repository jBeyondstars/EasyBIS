"""Pre-raid boss duels, WoWSims Forever a73af71451, 2,000 paired fights of 180 s.

Each row gives the threat item, the mitigation item, then the Alliance and Horde
changes in (DPS, threat/s, damage taken/s) when equipping the threat item.
Both sides resolve both sides of the trade-off. The bear trinket duels keep
Blackhand's Breadth (Alliance) or Rune of the Guard Captain (Horde) equipped.
The paladin trinket duel keeps The Lion Horn of Stormwind equipped on both sides.
"""

DUELS = {
    ("WARRIOR", 3): {
        "head": (22411, 226869, (8.7, 26.0, 6.9), (8.8, 26.4, 6.6)),
        "back": (272414, 18511, (9.7, 30.4, 11.5), (10.0, 31.0, 11.0)),
    },
    ("DRUID", 2): {
        "main": (250619, 18531, (21.6, 100.4, 51.4), (16.9, 81.9, 59.0)),
        "hands": (19049, 226802, (5.5, 27.2, 14.5), (6.8, 33.3, 14.3)),
        "trinket": (272437, 272440, (13.5, 58.9, 12.4), (12.3, 53.6, 14.6)),
    },
    ("PALADIN", 2): {
        "back": (272411, 18511, (10.3, 26.4, 7.3), (8.0, 21.6, 6.2)),
        "trinket": (272438, 272440, (7.5, 18.3, 9.4), (5.5, 14.0, 9.7)),
    },
}


def record(spec, slot, duel):
    threat, mitigation, alliance, horde = duel
    values = " ".join(f"{value:.1f}" for value in (*alliance, *horde))
    return f"T\t{spec}\tpve\t{slot}\t{threat} {mitigation} {values}"
