"""Verified faction rewards for PvP lists.

Set names and item IDs: WoWSims Forever, assets/database/db.json (07648faf).
Dungeon quest rewards: https://forevertavern.net/zones/kalimdor/the-shapers-terrace
"""
import phases

# (Alliance, Horde), by slot. WoWSims Forever's item set IDs distinguish the
# Lieutenant Commander's and Champion's sets. The cuffs and belts match the
# same class, armor family and slot on their already faction-tagged epic sets.
# Keep the two records independent: a vendor, observation or score on one ID
# need not apply to the other (e.g. Leather / Shadowhide).
PREMIER_ARMOR = (
    # Druid: Beasthide / Dragonhide, Dreamhide / Kodohide, Lunarhide / Wyrmhide
    (272733, 272471), (272732, 272469), (272730, 272472), (272707, 272582),
    (272709, 272614), (272711, 272463), (272731, 272470), (272705, 272462),
    (273374, 272641), (273375, 272642), (273380, 272626), (272834, 272461),
    (273377, 272464), (273378, 273367), (273373, 272627), (273379, 272606),
    (272669, 273386), (272670, 273387), (273371, 273384), (272835, 273381),
    (273368, 273382), (273369, 273388), (272656, 273385), (273370, 273383),
    # Hunter: Chainmail / Chain
    (272737, 272491), (272736, 272640), (272734, 272490), (272830, 272483),
    (272715, 272495), (272712, 272494), (272735, 272492), (272713, 272496),
    # Mage: Silk / Magus
    (272725, 272457), (272724, 272680), (272722, 272459), (272702, 272454),
    (272703, 272455), (272700, 272456), (272723, 272458), (272701, 272453),
    # Paladin: Chevalier / Scaled, Luminous / Lamellar
    (272743, 274231), (272745, 274233), (272742, 274230), (272721, 274229),
    (272719, 274227), (272720, 274228), (272744, 274232), (272718, 274226),
    (272854, 274246), (272855, 274247), (272852, 274244), (273364, 274257),
    (273363, 274256), (273366, 274259), (272853, 274245), (273365, 274258),
    # Rogue: Leather / Shadowhide
    (272727, 272474), (272729, 272475), (272726, 272473), (272706, 272465),
    (272708, 272467), (272710, 272468), (272728, 272476), (272704, 272608),
    # Shaman: Flatmail / Linked, Scalemail / Mail, Linkmail / Ringmail
    (274196, 272647), (274181, 272489), (274194, 272625), (274182, 272497),
    (274177, 272485), (274214, 273352), (274180, 272488), (274192, 272609),
    (274178, 272486), (274197, 272648), (274179, 272487), (274215, 273353),
    (274193, 272617), (274225, 273372), (274195, 272636), (274176, 272484),
    (274218, 273356), (274222, 273360), (274219, 273357), (274223, 273361),
    (274220, 273358), (274224, 273362), (274221, 273359), (274217, 273355),
    # Warlock: Dreadweave / Felweave
    (272671, 272643), (272801, 272549), (272800, 272548), (272795, 272551),
    (272796, 272553), (272797, 272550), (272657, 272630), (272794, 272552),
    # Warrior: Plate / Mortarplate
    (272738, 272480), (272741, 272637), (272739, 272479), (272828, 272579),
    (272717, 272478), (273325, 273324), (272740, 272481), (272716, 272477),
)

QUEST_REWARDS = (
    # Shaper's Terrace: Panic at the Digsite / Crystalline Elements
    (279903, 279904),
    # Digestible Research / Essence of Seeping Slimes
    (279901, 279902), (279931, 279932),
    # Hinterlands: Saving Sharpbeak / Job Opening: Guard Captain of Revantusk Village
    (270275, 19120), (270276, 270225),
)

SIDES = {item_id: side for pair in (*PREMIER_ARMOR, *QUEST_REWARDS)
         for item_id, side in zip(pair, ("a", "h"))}


def for_list(item_id, item):
    side = SIDES.get(item_id)
    if not side or item["twin"] or item["side"] not in ("", side):
        return item
    item = dict(item, side=side)
    if (item.get("added") and item.get("phase") == phases.LATER
            and not item["sources"] and item["name"].startswith("Premier ")):
        # align() defaults uncatalogued gear to the last phase. These verified
        # level-55 honor rewards are available alongside the rest of their set.
        item["phase"] = phases.PRE_RAID
    return item
