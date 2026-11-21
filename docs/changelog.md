# Easy BIS 1.8.3

## Fixed

- **Four more specs measured again.** The PvE lists of Subtlety Rogue, Enhancement Shaman, Retribution Paladin and Arms Warrior are measured again on the current version of WoWSims Forever, every item of each slot. Leaving the PvP rewards aside:
  - Subtlety Rogue: Distracting Dagger is the best off hand, ahead of Felstriker and Alcor's Sunrazor. Felstriker stays the best main hand.
  - Enhancement Shaman: measured with the setup WoWSims Forever's site starts from. Sulfuron Hammer is the best weapon, ahead of Forest Defender's Axe. Bloodmail Gauntlets and Tranquil Wristguards are the best hands and wrists.
  - Retribution Paladin: Lionheart Helm is the best head in place of Black Dragonscale Helm, and Tranquil Wristguards the best wrists in place of Battleborn Armbraces. Titanic Leggings leave the first place to Champion's Legplates and Pristine Scorpid Leggings. Smolderweb's Eye and Frozen Heart of the Mountain are the best trinkets. Destiny stays the best weapon.
  - Arms Warrior: no best pick changes.
- **An item whose effect is not simulated is ranked on what was measured.** Such an item took its place from ForeverDB's stat weights, which know nothing of a weapon's speed, and could stand far too high: Treant's Bane was second in the two-hander lists of Enhancement Shaman, Retribution Paladin and Arms Warrior, where it does 19 to 97 damage per second less than the first. It is now ranked on its measure without that effect, in the seven lists measured again so far, Combat and Assassination Rogue and Fury Warrior included. It still shows no figure.
  - Retribution Paladin: Treant's Bane and Runeblade of Baron Rivendare leave the weapons shown, and Forest Defender's Axe is back among them.
  - Arms Warrior: Blackblade of Shahram is second, ahead of Runeblade of Baron Rivendare; Treant's Bane leaves the weapons shown.
  - Enhancement Shaman: Forest Defender's Axe is second, Treant's Bane fourth.
  - Rogues: Frightalon goes down the weapon lists.

## Known issue

- **Twelve damage specs are next.** Elemental Shaman, the Mages, the Hunters, Shadow Priest, Balance Druid and the Warlocks keep the earlier measure. Their lists follow a few specs at a time. Until the last one is out, the notice under the window's filters stays.

# Easy BIS 1.8.2

## New

- **What a score is.** Over the scores of each slot, a mark opens a tooltip that says how the list is ranked. For a list ranked by simulation: what is measured, the fight simulated (a raid boss, 3 minutes, one target, raid buffs and debuffs, consumables, the spec's default talents and rotation) and what the % means. For the others: the weighted stats.
- **No figure for a score that is not a full measure.** In a list ranked by simulation, an alternative the simulator cannot measure in full keeps its place and shows neither a bar nor a %: an item with a random bonus, or one whose effect or proc rate the simulator lacks. That is about one listed item in twelve.
- **The notice can be put away.** A cross at the right of the notice under the filters hides it and gives its room to the list. It is back the next time the window is opened.

## Fixed

- **Rogue and Fury Warrior weapons.** The PvE lists of Combat Rogue, Assassination Rogue and Fury Warrior are measured again, on the current version of WoWSims Forever. The version used so far did not know that the armor procs of Bashguuder and Annihilator never land while Faerie Fire or Curse of Recklessness is on the target, which Forever's logs show, and it ranked both weapons far too high. Leaving the PvP rewards aside:
  - Combat Rogue: Flurry Axe is the best off hand, ahead of Bone Slicing Hatchet, Felstriker and Alcor's Sunrazor. Teebu's Blazing Longsword is the best main hand, ahead of Persuader and Sword of Zeal.
  - Assassination Rogue: daggers again. Its best weapons were Persuader and Bashguuder, two maces Mutilate cannot be used with; they are Felstriker and Distracting Dagger now.
  - Fury Warrior: Flurry Axe is the best off hand in place of Bashguuder, and Annihilator leaves the picks. Persuader stays the best main hand.
- **Every item is measured.** The simulation measured the items with an effect or a set and the best ones by ForeverDB's stat weights; the others stayed under them, whatever they were worth. All the items of a slot are measured now: Distracting Dagger, for one, had never been.
- **Flurry Axe is in the lists.** ForeverDB's data leaves it out. It is the off hand of the Rogue and Warrior sets WoWSims Forever itself starts from. Its source, a world drop, is Classic's: not confirmed in Forever.

## Known issue

- **The other damage specs are next.** Their lists are measured again the same way and follow a few specs at a time, Subtlety Rogue first. Until the last one is out, the notice under the window's filters stays.

# Easy BIS 1.8.1

## Known issue

- **Some weapons are ranked wrong.** I know some weapons are currently not where they should be in the lists. A fix is on its way and will be out shortly. Until then, a notice under the window's filters says so.

# Easy BIS 1.8.0

## Changed

- **Every damage spec ranked by simulation.** The PvE lists of the last ten damage specs are now ranked with WoWSims Forever's simulator too: Marksmanship and Survival Hunter, Retribution Paladin, Shadow Priest, Assassination Rogue, Elemental and Enhancement Shaman, Affliction, Demonology and Destruction Warlock. In the simulator, the best set of their new lists does 0.7 % (Shadow Priest, Destruction Warlock) to 8.9 % (Assassination Rogue) more damage than the set ForeverDB's stat weights gave.
- **No more Estimated items.** The items with an effect have their own score in every damage spec's list now:
  - Hand of Justice is a best trinket of Retribution Paladin and Assassination Rogue, and an alternative for Enhancement Shaman.
  - Destiny is the best two-hander of Retribution Paladin.
- Many best picks of these ten lists change. For example, Robe of Winter Night is now the best PvE chest of Shadow Priest and Ironfeather Breastplate that of Elemental Shaman, in place of Robes of Dark Summons.
- Tanks and healers keep ForeverDB's weights.

# Easy BIS 1.7.0

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
