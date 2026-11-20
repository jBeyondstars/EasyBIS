# Unreleased

## New

- **Dungeons.** Which dungeons to run for your spec's best picks, each dungeon in its own colour. The window has two tabs on its right side, as the game's professions do: the lists, and the dungeons.
  - **By dungeon**: your set, every slot over the colour of its dungeon (a piece no dungeon holds is in black and white), then a band per run with how many pieces it holds. Each piece shows its boss and its drop rate.
  - **By piece**: a line per piece and a column per run, with a coloured cell where the piece drops.
  - A run is a dungeon, or a wing that is run on its own: Upper and Lower Blackrock Spire, Stratholme Living and Undead, the three wings of Dire Maul, the four of the Scarlet Monastery.
  - A quest's reward sits with the dungeon its quest is done in, under the quest mark: one run is enough for it.
  - What you already have, worn, in your bags or in the bank, is checked and leaves the count at the top.
  - The **Alternatives** button adds the alternatives. They fade once the slot's best pick is yours.
  - Point at a run to light its slots, click a piece to see its slot in the Items tab.

## Changed

- **Bosses the data left without a dungeon.** About a hundred listed items now name the dungeon their boss is in: the arena of Blackrock Depths, and the dungeons of Forever the data had no place for (Blackmaw Hold, The Drowned City, Krol'dok Stronghold). The Items tab shows them as dungeon drops, and the Zone filter finds them.
- **Items that had no known source.** 60 items of the lists now have one: the boss Wowhead Forever counted them on, mostly in Shaper's Terrace, Alcaz Prison, Blackmaw Hold and Krol'dok Stronghold. They no longer need the option **Items with no known source** to show, so a few best picks change:
  - Obsidian Bauble (Pusillin, Dire Maul East) is the best PvE off hand of the three Mage specs, Demonology and Destruction Warlock, Balance Druid and Elemental Shaman.
  - Robes of Dark Summons (Impaan the Imprisoner, Blackmaw Hold) is the best PvE chest of Shadow Priest and Elemental Shaman.
  - Frostfang Mail Vest (Shaper's Terrace) is the best PvP chest of Restoration Shaman, and of a Horde Holy Paladin.
  - Deep Jungle Rifle (Thunderhoof, Shaper's Terrace) is the best PvE ranged weapon of Subtlety Rogue.

# Easy BIS 1.6.0

## New

- **Auction house tab.** An **EasyBis** tab at the auction house shows which pieces of your list are on sale, each with its lowest buyout.
  - Pick a class, a spec and the PvE or PvP list in the tab, then click **Scan auctions**. The choice is the window's own: changing one changes the other.
  - The results read like the game's own list: price, item, BIS or alternative, and slot. The best picks come first, then the cheapest.
  - Click an item to open its auctions in the game's Buy tab.
  - The scan asks the auction house for each piece of your list, the best picks first, and shows how far along it is. Pieces that bind when picked up are left out, as they are never on sale.
  - A piece sold with several random enchantments shows its cheapest one. Bids without a buyout and your own auctions don't count as a price.
  - The tab comes after the other addons' tabs, Auctionator's included. **Options > Auction house tab** takes it away.

# Easy BIS 1.5.0

## New

- **Lists ranked by simulation.** The PvE lists of nine damage specs are now ranked with WoWSims Forever's simulator instead of stat weights: Arms and Fury Warrior, Combat and Subtlety Rogue, Arcane, Fire and Frost Mage, Balance Druid and Beast Mastery Hunter. An item's score is the damage per second it adds, so items with an effect finally count: Hand of Justice, Thunderfury, Destiny and the like.
- **Estimated items.** Until the simulator has measured them, the PvE lists of Retribution Paladin, Assassination Rogue and Enhancement Shaman take the items with an effect where a close spec's simulation ranks them. They read **Estimated**, with no score and no bar, and are never a best pick. Their own score comes with their spec's simulation.
- The other damage specs come in a later version. Tanks and healers keep ForeverDB's weights.

# Easy BIS 1.4.0

## New

- **Reputations tab.** The factions your spec, list and phase ask for, and where you stand with each of them.
  - Each faction's pieces sit on a track from Neutral to Exalted, above the standing that unlocks them.
  - The tab shows how much reputation is left to earn, where the pieces come from (click a vendor to see it on the map), and the quests your class and faction can take at level 60, the repeatable ones first and ten to a page.
  - A quest offered only between two standings says so: "until Friendly", "from Honored".
  - A battleground's faction says so, and its header names the battleground: Arathi Basin, Alterac Valley, Warsong Gulch or the Darkspear Islands.
  - The Alterac Valley and Warsong Gulch quartermasters' pieces say which standing they need on your side, as AtlasLoot Forever's tables list it, checked against ForeverDB. Their tooltips don't show it: only the vendor's window does.
  - What no source says is written as unknown, such as the reputation creatures give.
  - Factions that sell recipes, such as Timbermaw Hold's patterns, count for the crafter: the tab names the recipes and their vendors, and follows your professions.
  - Click a faction to follow it in the game's reputation bar.
- **Reputations everywhere else.** Items, Enchants, the Character sheet and item tooltips say which reputation a piece asks for and where you stand. A Reputation filter narrows the lists, and the Character sheet counts what you have earned with each faction.
- **Faction.** The lists follow your character's faction, with each item of the other faction replaced by its counterpart. **Options > Faction**, or `/easybis faction horde`, shows what the other faction would wear, and the window's title says so.

## Changed

- Theramore Expeditionary Force's pieces are now for the Alliance only, since their vendor and quests are the Alliance's. Horde lists take other pieces in their place.

# Easy BIS 1.3.0

## Changed

- **A new look.** The window now uses the game's own artwork, so it fits in with the rest of your interface.
  - The filters are the game's dropdown menus, with submenus for the specs and a scroll bar for long lists.
  - The tabs, the PvE and PvP switch and the Alternatives button take the game's buttons, and the checkboxes are the game's checkboxes.
  - The Options button opens its menu like the game's filter buttons.
  - Rows light up like the game's quest list when you hover them, on every tab and on the character sheet.
  - The Add an item dialog takes the game's dialog frame and search box, and its suggestions show in a tooltip.
- A filter that narrows the list still shows its label in gold.
- The Phase menu is greyed out while **Available now** is checked, since only the game's current phase is available then.
