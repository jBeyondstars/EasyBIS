<img src="docs/logo.png" alt="Easy BIS" width="120" align="right">

# Easy BIS

Best-in-slot gear for every class and spec of **WoW Forever**, in a window and in item tooltips.

- **Items**: the best items of each slot at level 60, PvE and PvP, with their alternatives and sources. You can filter by phase, slot, source and zone, and add items to a list yourself.
- **Character**: the BIS #1 of each slot laid out as a character sheet, with its best enchant, worn by your own character.
- **Enchants**: the best enchant of each slot and how to get it.
- **Consumables**: flasks, elixirs, food, scrolls, weapon stones and oils and potions, ranked category by category for each spec, in PvE and PvP.
- **Reputations**: what your spec needs of each faction, with its emblem where the game has the icon, on a track from Neutral to Exalted with each piece above the standing that unlocks it; what is left to earn, where the pieces come from (with the vendor on the map), the quests QuestieDB lists for your class and faction at level 60, the repeatable ones first and ten to a page, with the standings a quest is offered between (seasonal and profession quests are among them), and what no source says. The quests Questie says the game does not have are left out, and the variants of one quest count once. A battleground's faction says so, its header naming the battleground. A click follows the faction in the game's reputation bar. A faction that sells recipes (Timbermaw's patterns, for instance) counts for the crafter, apart from your own: the tab names the recipes and who sells them, and follows your professions. Your skill against what the recipes ask when the profession is yours; otherwise how to get the pieces, from how the game says they bind. A piece of a faction no source says how to earn (The Watchers) stays listed, with a grey ? after its name.
- **Tooltips**: which classes and specs want an item, whether it is their BIS, and the reputation it asks for.
- **Faction**: the lists are your character's faction's, an item of the other faction replaced by its twin. Options > Faction (or `/easybis faction horde`) shows what the other faction would wear: the lists, the tooltips and the reputations follow, and the window's title says so.

Type `/easybis` (or `/ebis`) in the game, or `/easybis help` for the commands.

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
python -P _build/tests/test_consumables.py
```

`_build/art/make_textures.py` makes `Media/*.tga` from a logo. The release zip leaves out `_build` and `docs` (`.pkgmeta`).

## Licence and credits

**Data from [ForeverDB.net](https://foreverdb.net).** The sources ForeverDB's data lacks come from [QuestieDB](https://github.com/Questie/QuestieDB); what the Alterac Valley and Warsong Gulch quartermasters' pieces ask, from AtlasLoot Forever's tables, checked against ForeverDB and the game. Easy BIS is free software under the GNU GPL, version 3 (`LICENSE.txt`). `NOTICE.txt` says where each part comes from and what reusing it requires.

Easy BIS is not affiliated with Blizzard Entertainment, ForeverDB.net, the Questie team or the AtlasLoot authors.
