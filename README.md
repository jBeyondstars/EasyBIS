<img src="docs/logo.png" alt="Easy BIS" width="120" align="right">

# Easy BIS

Best-in-slot gear for every class and spec of **WoW Forever**, in a window and in item tooltips.

- **Items**: the best items of each slot at level 60, PvE and PvP, with their alternatives and sources. You can filter by phase, slot, source and zone, and add items to a list yourself. Survival Hunters use the Ranged profile. Its single-target list uses WoWSims’ ranged Hunter stat weights. Its dungeon list uses the Survival rotation simulated at 12 yards. The other PvE damage profiles use item simulations that count effects such as Hand of Justice.
- **Custom gear lists** are saved per class and specialization. Under Items → PvE, click **+** and name the new list, then use **Add an item** or **Import WoWSims**. In WoWSims Forever, select **Gear** and uncheck all other options before exporting the JSON. Paste the export to replace the selected list with its equipped items and enchants. Drag a custom tab onto another to take its position, or onto a page arrow to move it to the adjacent page. Right-click a custom tab to rename it, move it left or right, or delete it.
- **Character**: the BIS #1 of each slot laid out as a character sheet, with its best enchant, worn by your own character.
- **Enchants**: the best enchant of each slot and how to get it.
- **Auction house**: open the **EasyBis** tab, pick a class, a spec and the PvE or PvP list, and click **Scan auctions** to see the lowest available buyout for each BIS or alternative, in a list laid out as the game's own results. The scan asks the auction house for each piece of the list, the best picks first, and leaves out those that bind when picked up. Click an item to open its auctions. The tab comes after the other addons' tabs; Options > Auction house tab takes it away.
- **Consumables**: flasks, elixirs, food, scrolls, weapon stones and oils and potions, ranked category by category for each spec, in PvE and PvP.
- **Reputations**: what your spec needs of each faction, with its emblem where the game has the icon, on a track from Neutral to Exalted with each piece above the standing that unlocks it; what is left to earn, where the pieces come from (with the vendor on the map), the quests QuestieDB lists for your class and faction at level 60, the repeatable ones first and ten to a page, with the standings a quest is offered between (seasonal and profession quests are among them), and what no source says. The quests Questie says the game does not have are left out, and the variants of one quest count once. A battleground's faction says so, its header naming the battleground. A click follows the faction in the game's reputation bar. A faction that sells recipes (Timbermaw's patterns, for instance) counts for the crafter, apart from your own: the tab names the recipes and who sells them, and follows your professions. Your skill against what the recipes ask when the profession is yours; otherwise how to get the pieces, from how the game says they bind. A piece of a faction no source says how to earn (The Watchers) stays listed, with a grey ? after its name.
- **Dungeons**: the second tab on the window's right side, where the first is the lists above. Use **Tracked lists** to combine Raid, PvP, AoE / Dungeons when available, and your custom lists. Your selection is saved for this character and specialization. See which dungeons hold the tracked pieces, each dungeon in its own colour. By dungeon: the set, every slot over the colour of its dungeon (a piece no dungeon holds is in black and white), then a band per run with how many pieces it holds and each piece with its boss and its drop rate. By piece: a line per piece, a column per run, a coloured cell where the piece drops. A run is a dungeon, or a wing that is run on its own (Upper and Lower Blackrock Spire, the wings of Dire Maul, Stratholme and the Scarlet Monastery). A quest's reward sits with the dungeon its quest is done in, under the quest mark. What you have, worn, in your bags or in the bank, is checked and leaves the count at the top. The Alternatives button adds the alternatives, which count in their band's number and in nothing else.
- **Tooltips**: which classes and specs want an item, whether it is their BIS, and the reputation it asks for.
- **Faction**: the lists are your character's faction's, an item of the other faction replaced by its twin. Options > Faction (or `/easybis faction horde`) shows what the other faction would wear: the lists, the tooltips and the reputations follow, and the window's title says so.

Type `/easybis` (or `/ebis`) in the game, or `/easybis help` for the commands.

In **Items → PvE → AoE / Dungeons**, each item is tested in two scenarios. The first is a 15-second pull against four level-60 enemies. The second chains four elites, one elite with triple health, then three elites and four normal enemies. Players drink between pulls and start each at full mana. Cooldowns carry over. Each scenario contributes half of its percentage gain in character and pet damage over the reference gear. This average determines the order for armor, jewelry and relics.

Weapons have their own recommendation points. They account for base DPS, stats, set bonuses, procs and the damage the specialization’s rotation gains or loses when it changes weapons. The points use half of the rotation adjustment and the full value of base DPS, stats and procs. For example, a slow main hand can give Fury stronger Whirlwind and Cleave hits. For ranged hunters, melee stats can benefit shots. In Beast Mastery, main-hand DPS also contributes to the summoned hawks’ damage. Main-hand and off-hand choices are evaluated together. Hover over a weapon to see its partner, the breakdown in points and its measured damage gains in both scenarios. A higher-ranked weapon can have a smaller measured damage gain.

The AoE / Dungeons lists cover 21 damage profiles on both factions, including ranged Survival. Tank and healing specializations have Raid and PvP lists. Rings and trinkets keep their second slot equipped, and hunters keep a working bow for the ranged comparison. [Ranking changes by specialization](docs/design/comparatif-pack-donjon.md) · [Scenarios and measurements](docs/design/classement-aoe.md)

![The Items tab](docs/screenshots/items.png)

![The Character tab](docs/screenshots/character.png)

## Install

Put the `EasyBIS` folder in `World of Warcraft\_forever_\Interface\AddOns`, then restart the game.

## For developers

The addon's data (`Data/*.lua`) is generated from ForeverDB's addon data by the Python tool in `_build`:

```
python -I _build/build.py            # rebuild Data/*.lua from the cached ForeverDB files
python -I _build/build.py --check    # is newer ForeverDB data out?
python -I _build/build.py --update   # download what changed (SHA-256 checked) and rebuild
python -I _build/build.py --import-questie   # read in the QuestieDB addon the sources ForeverDB's data lacks
python -I _build/build.py --import-dungeon-quests   # read in QuestieDB the dungeon each quest is done in, for the Dungeons tab
python -I _build/build.py --import-reputations   # read the reputations items ask for (the capture's tooltips and vendors' windows, AtlasLoot Forever's tables too), and the quests that earn them
python -I _build/build.py --capture-tool     # install the tool that reads item tooltips and vendors' windows in the game (/ebiscapture)
python -I _build/build.py --import-capture   # keep what it read: weapons, and what each consumable does
python -I _build/tests/compare_coach.py      # compare the consumable lists with ForeverDB's coach
```

Offline tests (they need `lupa`, and `Pillow` for the textures):

```
python -P _build/tests/test_generator.py
python -P _build/tests/test_addon.py
python -P _build/tests/test_ui.py
python -P _build/tests/test_auctions.py
python -P _build/tests/test_consumables.py
```

`_build/art/make_textures.py` makes `Media/*.tga` from a logo. The release zip leaves out `_build` and `docs` (`.pkgmeta`).

## Licence and credits

**Data from [ForeverDB.net](https://foreverdb.net).** The sources ForeverDB's data lacks, and the dungeon a quest is done in, come from [QuestieDB](https://github.com/Questie/QuestieDB); what the Alterac Valley and Warsong Gulch quartermasters' pieces ask, from AtlasLoot Forever's tables, checked against ForeverDB and the game. The PvE lists of the damage specs are ranked with [WoWSims Forever](https://github.com/wowsims/forever). Easy BIS is free software under the GNU GPL, version 3 (`LICENSE.txt`). `NOTICE.txt` says where each part comes from and what reusing it requires.

Easy BIS is not affiliated with Blizzard Entertainment, ForeverDB.net, the Questie team, the WoWSims team or the AtlasLoot authors.
