-- Data: ForeverDB.net (https://foreverdb.net), build 1.60.1.70938. Reuse requires this credit: see NOTICE.txt (GPL-3.0 section 7(b)).
local _, ns = ...
-- Where each item in the gear finder comes from (tools/build_addon_gearfinder.py): a line per item,
-- "id (base 36)|name|groups|flags|side|twin|limit|sources", indexed on first use (GearFinder.lua).
-- Labels: s Seen in Forever, c Clue (unconfirmed), f Forever client, k Classic data.
ns.gfItemText = [==[
1o|Layered Tunic|q|s|a|11851||q^6^Bounty on Garrick Padfoot^2^a^s
1p|Dwarven Leather Pants|q|s|a|3272||q^183^The Boar Hunter^1^a^s
27|Dwarven Cloth Britches|q|s|a|6713||q^183^The Boar Hunter^1^a^s
28|Soft Fur-lined Shoes|q|s|a|4915||q^33^Wolves Across the Border^1^a^s
2d|Dirty Leather Vest|v|s|h|||V^3160^62^h^s
3w|Brawler's Boots|d|||||d^229^Spire Spider^0.48^0^k
5d|Tattered Cloth Vest|v|s|h|||V^3160^48^h^s
5e|Tattered Cloth Pants|v|s|h|||V^3160^49^h^s
5f|Tattered Cloth Boots|v|s|h|||V^3160^36^h^s
5k|Thick Cloth Vest|v|s||||V^2849^2270^^s
5l|Thick Cloth Pants|v|s||||V^2849^2278^^s
5m|Thick Cloth Shoes|v|s||||V^251981^1714^^s
5n|Thick Cloth Gloves|v|s||||V^2849^1147^^s
5t|Dirty Leather Pants|v|s|h|||V^3160^60^h^s
5u|Dirty Leather Boots|v|s|h|||V^3160^45^h^s
6k|Cured Leather Armor|v|s||||V^3536^2795^^s
6l|Cured Leather Pants|v|s||||V^3536^2805^^s
6m|Cured Leather Boots|v|s||||V^3536^2112^^s
6n|Cured Leather Gloves|v|s||||V^3536^1413^^s
7x|Scalemail Vest|v|s||||V^3493^3555^^s
7y|Scalemail Pants|v|s||||V^3493^3229^^s
7z|Scalemail Boots|v|s||||V^3493^2441^^s
hz|Destiny|w|||||w^0^0^k
jq|Bracers of the People's Militia|q|s|a|||q^102^Patrolling Westfall^9^a^s
jr|Tattered Cloth Gloves|v|s|h|||V^3160^25^h^s
ju|Dirty Leather Gloves|v|s|h|||V^3160^32^h^s
jy|Scalemail Gloves|v|s||||V^3493^1614^^s
jz|Rabbit Handler Gloves|q|s|a|3275||q^179^Dwarven Outfitters^1^a^s
k0|Brawler Gloves|dw|s||||d^2959^Atrexis the Grave Knight^14.29^0^s~m^10896^Arnak Grimtotem^0^s
k7|Notched Shortsword|w|sr||||m^474^Defias Rogue Wizard^0^s~m^480^Rusty Harvest Golem^0^s
ko|Thunderbrew's Boot Flask|q||a|||q^53^Sweet Amber^40^a^k
kx|Dragonmaw Shortsword|w|||||w^0^0^k
ky|Shortsword of Vengeance|w|||||w^0^0^k
l0|Tunnel Pick|w|s||||m^1053^Dark Iron Tunneler^0^s
l7|Ice-covered Bracers|Rw|s||||R^1119^Hammerspine^0^s
la|Flanged Mace|Rw|s||||m^1196^Ice Claw Bear^0^s~m^43^Mine Spider^0^s
lc|Lumberjack Axe|w|s||||m^822^Young Forest Bear^0^s~m^116^Defias Bandit^0^s
lk|Vendetta|dwx|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
lm|Kobold Excavation Pick|w|s||||m^476^Kobold Geomancer^5.98^s
lp|Stone Gnoll Hammer|w|s||||m^478^Riverpaw Outrunner^7.88^s~m^97^Riverpaw Runt^7.8^s
lx|Stout Battlehammer|dwx|sr||||d^36^^0^0^s~m^3840^Druid of the Fang^0^s
m0|Knitted Sandals|vw|s||||V^251981^207^^s~m^3530^Pyrewood Tailor^83.42^k
m1|Knitted Gloves|vw|s||||V^3952^139^^s~m^3530^Pyrewood Tailor^84.02^k
m2|Knitted Pants|vw|s||||V^3952^279^^s~m^3530^Pyrewood Tailor^83.18^k
m3|Knitted Tunic|vw|s||||V^3952^280^^s~m^3530^Pyrewood Tailor^82.56^k
m4|Rough Leather Boots|vw|s||||V^3953^264^^s~m^3532^Pyrewood Leatherworker^65.82^k
m5|Rough Leather Gloves|vw|s||||V^3953^176^^s~m^3532^Pyrewood Leatherworker^65.82^k
m6|Rough Leather Pants|vw|s||||V^3953^354^^s~m^3532^Pyrewood Leatherworker^65.32^k
m7|Rough Leather Vest|vw|s||||V^3953^355^^s~m^3532^Pyrewood Leatherworker^65.82^k
mj|Axe of the Deep Woods|w|||||w^0^0^k
mo|Small Hand Blade|w|s||||m^36^Harvest Golem^0^s
ms|Slicer Blade|w|||||w^0^0^k
mt|Riverpaw Leather Vest|w|s||||m^123^Riverpaw Mongrel^0^s
my|Brutish Riverpaw Axe|w|s||||m^124^Riverpaw Brute^0^s
mz|Wicked Blackjack|w|s||||m^122^Defias Highwayman^0^s
n4|Silver Defias Belt|w|s||||m^121^Defias Pathstalker^0^s
n5|Lifestone|w|||||w^0^0^k
n9|Heavy Weave Armor|v|s||||V^3683^1124^^s
na|Heavy Weave Pants|v|s||||V^3683^1128^^s
nb|Heavy Weave Gloves|v|s||||V^3683^566^^s
nc|Heavy Weave Shoes|v|s||||V^251981^853^^s
nf|Tanned Leather Boots|v|s||||V^3684^1077^^s
ng|Tanned Leather Gloves|v|s||||V^3684^720^^s
nh|Tanned Leather Pants|v|s||||V^3684^1447^^s
ni|Tanned Leather Jerkin|v|s||||V^3684^1452^^s
nj|Chainmail Armor|vw|s||||V^4187^1749^^s~m^3528^Pyrewood Armorer^100^k
nk|Chainmail Pants|vw|s||||V^4187^1755^^s~m^3528^Pyrewood Armorer^100^k
nl|Chainmail Boots|vw|s||||V^4187^1326^^s~m^3528^Pyrewood Armorer^100^k
nm|Chainmail Gloves|vw|s||||V^4187^883^^s~m^3528^Pyrewood Armorer^100^k
nn|Cutlass|v|s||||V^275623^2023^^s
no|Mace|v|s||||V^3534^1739^^s
np|Hatchet|v|s||||V^3534^2409^^s
nq|Quarter Staff|v|s||||V^3534^3022^^s
nw|Cavalier's Boots|q|s|a|||q^416^Rat Catching^10^a^s
ny|Runed Ring|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
nz|Gloom Reaper|dwx|sr||||d^189^^0^0^s~m^689^Crystal Spine Basilisk^0^s
o0|Knightly Longsword|wx|sr||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
o1|Leaden Mace|Rdwx|sr||||m^4427^Ward Guardian^0^s~m^4673^Hatefury Betrayer^0^s
o2|Monk's Staff|wx|sr||||m^7011^Earthen Rocksmasher^0^s
o3|Gloves of Holy Might|u|||||
o6|Fiery War Axe|u|||||
o8|Rockslicer|d|sU||||d^36^Rhahk'Zor^36.84^0^s
o9|Staff of Jordan|u|||||
oc|Worn Wooden Buckler|v|s||||V^252000^7^^s
ol|Black Metal Axe|w|s||||m^3^Flesh Eater^0^s
oo|Naga Battle Gloves|d|s||||d^48^Lady Sarevess^41.67^0^s
oq|Twisted Chanter's Staff|w|||||w^0^0^k
os|Gnoll Casting Gloves|w|s||||m^1009^Mosshide Mistweaver^0^s
ox|Madwolf Bracers|w|s||||m^206^Nightbane Vile Fang^0^s
oz|Venom Web Fang|w|sr||||m^217^Venom Web Spider^0^s
pe|Large Ogre Chain Armor|w|||||w^0^0^k
pm|Dacian Falx|v|s||||V^275623^12038^^s
pn|Longsword|v|s||||V^275623^8743^^s
po|Maul|v|s||||V^4086^10972^^s
pp|Flail|v|s||||V^4086^7797^^s
pq|Battle Axe|v|s||||V^4086^9784^^s
pr|Double Axe|v|s||||V^4086^6953^^s
ps|Long Staff|v|s||||V^4086^9860^^s
py|Stalvan's Reaper|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
pz|Night Watch Shortsword|w|||||w^0^0^k
q0|Midnight Mace|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
q1|Black Duskwood Staff|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
q4|Robes of Insight|u|||||
q6|Freezing Band|u|||||
q8|Elemental Mage Staff|w|||||w^0^0^k
rb|Red Linen Sash|q|s|a|||q^83^Red Linen Goods^4^a^s
s1|Compact Hammer|q|s|a|||q^417^A Pilot's Revenge^8^a^s
s2|Gnarled Short Staff|q|s|a|||q^320^Return to Bellowfiz^3^a^s
s3|Sharp Axe|q|s|a|||q^320^Return to Bellowfiz^3^a^s
tw|Defias Renegade Ring|dw|s||||d^34^Targorr the Dread^20^0^s~d^34^Dextren Ward^6.25^0^s
tx|Defias Mage Ring|w|U||||w^0^0^k
v0|Ring of Pure Silver|q||a|||q^1046^Raene's Cleansing^25^a^k
v5|Feet of the Lynx|w|||||w^0^0^k
w2|Belt of the People's Militia|q|s|a|||q^102^Patrolling Westfall^9^a^s
w3|Rod of the Sleepwalker|d|s||||d^48^Twilight Lord Kelris^41.67^0^s
w4|Lavishly Jeweled Ring|d|s||||d^36^Gilnid^23.81^0^s
w9|Militia Shortsword|q|s|a|||q^18^Brotherhood of Thieves^2^a^s
wg|Skullflame Shield|w|||||w^0^0^k
wh|Blackskull Shield|u|||||
wk|Grayson's Torch|q|s||||q^104^The Coastal Menace^15^^s
wl|Weather-worn Boots|q|s|a|||q^88^Princess Must Die!^6^a^s
wu|Brass-studded Bracers|q|s|a|4969||q^88^Princess Must Die!^6^a^s
wv|Elastic Wristguards|q|s|a|6062||q^147^Manhunt^7^a^s
x2|Overseer's Cloak|w|||||w^0^0^k
x6|Bastard Sword|v|s||||V^251364^104^^s
x8|Tabar|v|s||||V^3534^2214^^s
x9|Giant Mace|v|s||||V^3534^2666^^s
xa|Claymore|v|s||||V^275623^2676^^s
xc|Large Wooden Shield|v|s|h|||V^3161^82^h^s
xd|Dull Heater Shield|v|s|a|2376||V^4240^473^a^s
xe|Wall Shield|vw|s||||V^4187^1839^^s~m^3528^Pyrewood Armorer^100^k
xf|Aegis of Stormwind|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
xg|The Green Tower|u|||||
xj|Murphstar|wx|sr||||m^258687^NPC 258687^0^s
xn|Gnoll War Harness|w|s||||m^423^Redridge Mongrel^0^s
xp|Gnoll Kindred Bracers|w|s||||m^712^Redridge Thrasher^1.07^s
xr|Support Girdle|w|||||w^0^0^k
xu|Heavy Gnoll War Club|w|s||||m^445^Redridge Alpha^0^s
xv|Redridge Machete|w|s||||m^424^Redridge Poacher^0^s
xw|Lupine Axe|w|s||||m^580^Redridge Drudger^0^s
z3|Brain Hacker|w|||||w^0^0^k
z4|Headbasher|Q|s|a|||q^378^The Fury Runs Deep^22^a^s
z5|Scorpion Sting|wx|s||||m^258818^NPC 258818^0^s
za|Finely Woven Cloak|q|s|a|10821||q^116^Dry Times^12^a^s
zd|Forest Chain|q|s|a|||q^275^Blisters on The Land^21^a^s
zf|Deputy Chain Coat|q|s|a|||q^219^Missing In Action^20^a^s
zg|Fire Hardened Buckler|q|s|a|||q^19^Tharil'zun^20^a^s
zk|Cloaked Hood|w|||||w^0^0^k
zm|Sparkmetal Coif|q|s|a|||q^55^Morbent Fel^27^a^s
zr|Giant Tarantula Fang|w|s||||m^442^Tarantula^0^s
zw|Butcher's Cleaver|d|s||||d^33^Razorclaw the Butcher^55.56^0^s
101|Robes of the Shadowcaster|Rw|s||||m^2553^Witherbark Shadowcaster^0^s~R^12433^Krethis Shadowspinner^0^s
103|Lesser Belt of the Spire|w|s||||w^0^0^k
104|Lesser Staff of the Spire|w|s||||m^436^Blackrock Shadowcaster^0^s
106|Black Whelp Gloves|q|s|a|||q^122^Underbelly Scales^14^a^s
107|Bridgeworker's Gloves|q|s|a|||q^89^The Everstill Bridge^15^a^s
108|Riding Gloves|q|s|a|||q^89^The Everstill Bridge^15^a^s
10a|Wolfmane Wristguards|q|s|h|||q^6481^Earthen Arise^15^h^s
10e|Smith's Trousers|q|s|a|||q^89^The Everstill Bridge^15^a^s
10i|Ghoul Fingers|w|||||w^0^0^k
10l|Hardened Root Staff|Q|s|a|||q^386^What Comes Around...^22^a^s
10m|Night Reaver|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
10n|Ring of Iron Will|q|s|a|||q^126^Howling in the Hills^20^a^s
11j|Fingerbone Bracers|w|||||w^0^0^k
11n|Buckskin Cape|w|||||w^0^0^k
11r|Lion-stamped Gloves|q|s|a|4962||q^87^Goldtooth^5^a^s
11s|Stormwind Chain Gloves|q|s|a|||q^147^Manhunt^7^a^s
12e|Rock Mace|dq|s||||q^757^Rite of Strength^1^h^s~d^289^Splintered Skeleton^0.02^0^k
12f|Stone Tomahawk|q|s|h|||q^757^Rite of Strength^1^h^s
12k|Crooked Staff|w|||||m^2953^Bristleback Shaman^0.97^k
12l|Kobold Mining Mallet|w|s||||m^40^Kobold Miner^4.04^s
12n|Riverpaw Mystic Staff|w|||||w^0^0^k
12q|Driftwood Club|w|s||||m^171^Murloc Warrior^0^s
131|Foamspittle Staff|w|||||w^0^0^k
132|Pearl-encrusted Spear|w|||||w^0^0^k
13w|Frontier Britches|q|s|a|||q^217^In Defense of the King's Lands^12^a^s
13y|Warrior's Shield|w|s||||m^1537^Scarlet Zealot^0^s~m^1538^Scarlet Friar^0^s
140|Gnoll Skull Basher|w|s||||m^446^Redridge Basher^0^s
143|Jeweled Amulet of Cainwyn|w|||||w^0^0^k
145|Blackrock Pauldrons|w|s||||m^615^Blackrock Tracker^3.12^s~m^4462^Blackrock Hunter^2.27^k
146|Blackrock Boots|w|s||||m^440^Blackrock Grunt^0^s
147|Ring of Saviors|u|||||
148|Blackrock Gauntlets|w|s||||m^485^Blackrock Outrunner^0^s~m^4064^Blackrock Scout^0^s
149|Minor Channeling Ring|q|s|a|||q^256^WANTED: Chok'sul^17^a^s
14e|Axe of the Enforcer|dw|s||||d^48^^0^0^s~m^4825^Aku'mai Snapjaw^0^s
14h|Shadowhide Mace|w|s||||m^433^Shadowhide Gnoll^0^s
14i|Shadowhide Maul|w|s||||m^432^Shadowhide Brute^0^s
14k|Shadowhide Two-handed Sword|w|s||||m^434^Rabid Shadowhide Gnoll^0^s
14p|Tigerbane|wx|s||||m^255769^Redridge Brute^0^s~m^258804^NPC 258804^0^s
14t|Scimitar of Atun|w|s||||m^578^Murloc Scout^0^s
14x|Riverside Staff|w|||||w^0^0^k
153|Salma's Oven Mitts|q|s|a|||q^38^Westfall Stew^9^a^s
154|Fist of the People's Militia|q|s|a|||q^14^The People's Militia^12^a^s
155|Grimclaw|dw|||||d^48^Aku'mai^0.02^0^k~d^48^Twilight Lord Kelris^0.02^0^k
156|Shadowfang|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
157|Face Smasher|dw|s||||d^33^Odo the Blindwatcher^11.11^0^s~m^4279^Odo the Blindwatcher^0^s
158|Witching Stave|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
15a|Tree Bark Jacket|dw|s||||d^48^^0^0^s~m^4810^Twilight Reaver^0^s
15c|Avenger's Armor|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
15d|Gloomshroud Armor|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
15e|Guardian Talisman|Q|||||q^1445^The Temple of Atal'Hakkar^45^h^k~q^1475^Into The Temple of Atal'Hakkar^45^a^k
15f|Ring of Precision|dw|||||d^48^Aku'mai^0.02^0^k~d^48^Twilight Lord Kelris^0.02^0^k
15h|Heavy Marauder Scimitar|w|||||w^0^0^k
16a|Headhunting Spear|w|||||w^0^0^k
16b|Huge Stone Club|w|||||w^0^0^k
16r|Gnarled Hermit's Staff|w|||||w^0^0^k
16z|Shield of the Faith|q|s|a|||q^223^Worgen in the Woods^26^a^s
179|Buckler of the Seas|q|s||||q^104^The Coastal Menace^15^^s
17c|Bluegill Sandals|w|||||w^0^0^k
17d|Harvester's Robe|q|s|a|||q^9^The Killing Fields^10^a^s
17i|Edge of the People's Militia|q|s|a|||q^14^The People's Militia^12^a^s
18i|Sickle Axe|w|||||w^0^0^k
18k|Chromatic Sword|w|||||w^0^0^k
18n|Soulkeeper|x|||||x^5758^Mithril Lockbox^k
18o|Skullcrusher Mace|wx|r||||x^4638^Reinforced Steel Lockbox^k~w^40^49^k
18t|Spiritchaser Staff|wx|sr||||m^7269^Scarab^0^s
194|Skullsplitter Helm|w|||||w^0^0^k
195|Exquisite Flamberge|wx|sr||||o^Ancient Treasure^2.7^k~o^Captain's Chest^0.8^k
19j|Grinning Axe|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
1a3|Engineering Gloves|w|||||w^0^0^k
1a8|Spellforce Rod|w|||||w^0^0^k
1al|Drake-scale Vest|w|||||w^0^0^k
1am|Black Ogre Kickers|w|||||w^0^0^k
1ao|Headchopper|w|||||w^0^0^k
1bl|Ankh of Life|w|||||w^0^0^k
1bm|Necklace of Calisea|wx|||||x^4637^Steel Lockbox^k~w^0^0^k
1bn|Polished Jazeraint Armor|w|||||w^0^0^k
1bo|Robe of the Magi|wx|s||||m^4329^Firemane Scout^0^s
1bp|Double Link Tunic|w|||||w^0^0^k
1bq|Basilisk Hide Pants|w|||||w^0^0^k
1bs|Tanglewood Staff|w|||||w^0^0^k
1bt|Viking Warhammer|x|||||x^5758^Mithril Lockbox^k
1bu|Thornstone Sledgehammer|w|||||w^0^0^k
1by|Poison-tipped Bone Spear|wx|s||||m^250187^NPC 250187^0^s
1bz|Sword of Decay|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1c0|Teebu's Blazing Longsword|wx|||||x^16885^Heavy Junkbox^k~w^0^0^k
1ew|Lucky Trousers|q|s|a|||q^217^In Defense of the King's Lands^12^a^s
1ez|Dirty Leather Belt|v|s|h|||V^3160^31^h^s
1f0|Dirty Leather Bracers|v|s|h|||V^3160^31^h^s
1f3|Rough Leather Belt|vw|s||||V^3953^184^^s~m^3532^Pyrewood Leatherworker^65.82^k
1f4|Rough Leather Bracers|vw|s||||V^3953^185^^s~m^3532^Pyrewood Leatherworker^65.82^k
1f7|Tanned Leather Belt|v|s||||V^3684^725^^s
1f8|Tanned Leather Bracers|v|s||||V^3684^728^^s
1f9|Chainmail Belt|vw|s||||V^4187^877^^s~m^3528^Pyrewood Armorer^100^k
1fa|Chainmail Bracers|vw|s||||V^4187^880^^s~m^3528^Pyrewood Armorer^100^k
1fd|Cured Leather Belt|v|s||||V^3536^1388^^s
1fe|Cured Leather Bracers|v|s||||V^3536^1393^^s
1fg|Scalemail Bracers|v|s||||V^3493^1684^^s
1fh|Scalemail Belt|v|s||||V^3493^1690^^s
1gl|Miner's Revenge|Q|s|a|||q^167^Oh Brother. . .^15^a^s
1h5|Studded Blackjack|w|||||w^0^0^k
1h9|Jeweled Dagger|w|||||w^0^0^k
1hh|Defias Rapier|dw|s||||d^36^^0^0^s~m^1725^Defias Watchman^0^s
1hi|Weighted Sap|w|s||||w^0^0^k
1hj|Deadmines Cleaver|w|s||||m^594^Defias Henchman^0^s
1hk|Defias Mage Staff|w|||||w^0^0^k
1hl|Silk-threaded Trousers|dw|s||||d^36^^0^0^s~m^1729^Defias Evoker^0^s
1hm|Stonemason Cloak|dw|s||||d^36^Rhahk'Zor^26.32^0^s~m^598^Defias Miner^0^s
1hp|Staff of Conjuring|w|sr||||m^619^Defias Conjurer^0^s
1hq|Stonemason Trousers|dw|s||||d^36^^0^0^s~m^636^Defias Blackguard^0^s
1hr|Assassin's Blade|dw|s||||d^33^Wolf Master Nandos^11.11^0^s
1hs|Goblin Screwdriver|w|s||||w^0^0^k
1ht|Buzz Saw|d|s||||d^36^Sneed^42.86^0^s
1hu|Block Mallet|w|||||w^0^0^k
1hz|Goblin Mail Leggings|dw|s||||d^36^^0^0^s~m^3947^Goblin Shipbuilder^0^s
1i0|Metalworking Gloves|dw|s||||d^36^Gilnid^14.29^0^s~m^1731^Goblin Craftsman^0^s
1i1|Woodworking Gloves|dw|s||||d^36^Sneed^4.76^0^s~m^641^Goblin Woodcarver^0^s
1i7|Blackwater Cutlass|dw|s||||d^36^^0^0^s~m^657^Defias Pirate^0^s
1ib|Dragonmaw Chain Boots|w|s||||m^271351^Dragonmaw Reclaimer^0^s
1ie|Petrified Shinbone|w|s||||m^625^Undead Dynamiter^0^s
1if|Cold Iron Pick|w|s||||m^623^Skeletal Miner^0^s
1il|White Wolf Gloves|Rw|s||||R^1132^Timber^0^s
1iu|Mindthrust Bracers|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
1iv|Pysan's Old Greatsword|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1iw|Slaghammer|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1iy|Wolfclaw Gloves|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1j0|Underworld Band|u|||||
1j1|Icemail Jerkin|u|||||
1j8|Chief Brigadier Gauntlets|wx|s||||m^2570^Boulderfist Shaman^0^s~m^263899^NPC 263899^0^s
1ja|Ballast Maul|dwx|sr||||m^1096^Venture Co. Geologist^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
1jc|Swampchill Fetish|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
1jd|Ogremind Ring|w|s||||m^2255^Crushridge Mage^0^s
1je|Ebonclaw Reaver|wx|r||||x^4638^Reinforced Steel Lockbox^k~w^40^48^k
1jg|Voodoo Band|w|||||w^0^0^k
1jh|Pressed Felt Robe|w|s||||m^701^Bloodscalp Mystic^0^s
1ji|Bloodscalp Channeling Staff|w|||||w^0^0^k
1jk|Archeus|q|s|a|||q^231^A Daughter's Love^30^a^s
1jv|Twisted Sabre|Rw|s||||R^211965^NPC 211965^0^s
1jx|Cryptbone Staff|w|s||||m^787^Skeletal Healer^0^s
1k1|Glowing Leather Bracers|w|s||||w^0^0^k
1k2|Skeletal Longsword|w|||||w^0^0^k
1k4|Hollowfang Blade|w|s||||m^539^Pygmy Venom Web Spider^0^s
1k5|Green Carapace Shield|w|||||w^0^0^k
1k8|Espadon|v|s||||V^275623^6078^^s
1k9|Bearded Axe|v|s||||V^3491^5304^^s
1ka|Rock Hammer|v|s||||V^3491^6286^^s
1kb|Scimitar|v|s||||V^275623^3815^^s
1kc|Hammer|v|s||||V^3491^5065^^s
1kd|Cleaver|v|s||||V^3491^4419^^s
1ke|Gnarled Staff|v|s||||V^3491^5544^^s
1kg|Gallan Cuffs|q|s|h|||q^1164^To Steal From Thieves^31^h^s
1kh|Ambassador's Boots|Q|s|a|||q^377^Crime and Punishment^22^a^s
1ki|Scholarly Robes|dw|s||||d^48^^0^0^s~m^4814^Twilight Elementalist^0^s
1kj|Sword of the Night Sky|w|s||||w^0^0^k
1kk|Dusty Mining Gloves|Q|s|a|||q^168^Collecting Memories^14^a^s
1kl|Tunneler's Boots|Q|s|a|||q^168^Collecting Memories^14^a^s
1kn|Plains Ring|dw|s||||m^4442^Razorfen Defender^0^s~d^47^Overlord Ramtusk^0.03^0^k
1ko|Troll Protector|dx|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
1kp|Tunic of Westfall|Q|s|a|||q^166^The Defias Brotherhood^17^a^s
1kq|Staff of Westfall|Q|s|a|||q^166^The Defias Brotherhood^17^a^s
1kr|Ring of Forlorn Spirits|q|s|a|||q^98^The Legend of Stalvan^30^a^s
1ks|Crescent of Forlorn Spirits|q|s|a|||q^98^The Legend of Stalvan^30^a^s
1kv|Anvilmar Hand Axe|q|s|a|||q^182^The Troll Cave^1^a^s
1kw|Anvilmar Hammer|q|s|a|4924||q^182^The Troll Cave^1^a^s
1l2|Trogg Hand Axe|w|||||m^1718^Rockjaw Raider^2.04^k
1l3|Small Wooden Hammer|w|s||||m^80^Kobold Laborer^2.04^s
1l5|Pitted Defias Shortsword|w|s||||m^38^Defias Thug^1.96^s~m^251160^Al'Aketh Convert^0^s
1l7|Sentry Cloak|dw|s||||d^90^^0^0^s~m^4024^Bloodfury Slayer^0^s
1le|Skull Hatchet|w|s||||m^1115^Rockjaw Skullthumper^4^s
1lf|Frostbit Staff|w|s||||m^1117^Rockjaw Bonesnapper^7.98^s
1lh|Black Bear Hide Vest|w|||||w^0^0^k
1lk|Dwarven Magestaff|dwx|sr||||d^48^Twilight Lord Kelris^16.67^0^s~d^47^^0^0^s
1ll|Dwarven Hatchet|dw|sr||||d^389^Taragaman the Hungerer^18.75^0^s~m^3277^Witchwing Roguefeather^0^s
1lm|Solid Shortblade|Q|s|a|||q^214^Red Silk Bandanas^14^a^s
1ln|Priest's Mace|dw|sr||||d^389^^0^0^s~m^590^Defias Looter^0^s
1lp|Magician Staff|dwx|sr||||m^206^Nightbane Vile Fang^0^s~m^255069^NPC 255069^0^s
1lq|Northern Shortsword|dw|sr||||d^43^Skum^25^0^s~d^36^Gilnid^14.29^0^s
1lr|Sergeant's Warhammer|dw|sr||||d^36^Rhahk'Zor^15.79^0^s~d^2999^Viktor the Vile^10^0^s
1ls|Hillborne Axe|dwx|sr||||d^189^Interrogator Vishas^18.18^0^s~m^11563^Drysnap Pincer^0^s
1lz|Hard Crawler Carapace|w|||||w^0^0^k
1m0|Long Crawler Limb|w|||||w^0^0^k
1m1|Scrimshaw Dagger|Q|s|a|||q^214^Red Silk Bandanas^14^a^s
1ma|Double-barreled Shotgun|w|s||||w^0^0^k
1mb|Dwarven Hand Cannon|w|||||w^0^0^k
1mc|Precisely Calibrated Boomstick|u|||||
1mk|Frostmane Leather Vest|w|s||||m^706^Frostmane Troll Whelp^0.97^s
1ml|Frostmane Chain Vest|w|||||m^808^Grik'nir the Cold^0.83^k
1mm|Light Magesmith Robe|w|||||m^946^Frostmane Novice^1.13^k
1mo|Lumberjack Jerkin|w|||||m^1689^Scarred Crag Boar^5^k
1mq|Snowy Robe|w|||||m^1133^Starving Winter Wolf^3.97^k
1mt|Thin Cloth Shoes|v|s||||V^251981^36^^s
1mv|Thin Cloth Gloves|v|s||||V^251365^24^^s
1mw|Thin Cloth Pants|v|s||||V^251365^50^^s
1mx|Thin Cloth Armor|v|s||||V^251365^50^^s
1my|Cracked Leather Belt|v|s||||V^251365^32^^s
1mz|Cracked Leather Boots|v|s||||V^251365^48^^s
1n0|Cracked Leather Bracers|v|s||||V^251365^32^^s
1n1|Cracked Leather Gloves|v|s||||V^251365^32^^s
1n2|Cracked Leather Pants|v|s||||V^251365^59^^s
1n3|Cracked Leather Vest|v|s||||V^251365^60^^s
1n5|Large Round Shield|vw|s||||V^251965^77^^s~m^11040^Watcher Brownell^0.02^k
1n7|Shortsword|v|s||||V^251364^54^^s
1n8|Short Staff|v|s||||V^251364^102^^s
1na|Hand Axe|v|s||||V^251364^82^^s
1nd|Whittling Knife|q|s|h|||q^757^Rite of Strength^1^h^s
1nf|Dirk|v|s||||V^251364^57^^s
1ng|Carving Knife|w|sr||||m^95^Defias Smuggler^0^s~m^474^Defias Rogue Wizard^0^s
1nh|Cuirboulli Vest|v|s||||V^3953^5223^^s
1ni|Cuirboulli Belt|v|s||||V^3953^2620^^s
1nj|Cuirboulli Boots|vw|s||||V^3953^3944^^s
1nl|Cuirboulli Gloves|v|s||||V^3953^2648^^s
1nm|Cuirboulli Pants|v|s||||V^3953^4809^^s
1no|Polished Scale Belt|v|s||||V^4085^2907^^s
1np|Polished Scale Boots|v|s||||V^251981^4397^^s
1nq|Polished Scale Bracers|v|s||||V^4085^2930^^s
1nr|Polished Scale Gloves|v|s||||V^4085^2941^^s
1ns|Polished Scale Leggings|v|s||||V^4085^5906^^s
1nt|Polished Scale Vest|v|s||||V^4085^5927^^s
1nw|Padded Boots|v|s||||V^2849^3077^^s
1ny|Padded Gloves|v|s||||V^2849^2066^^s
1nz|Padded Pants|v|s||||V^2849^4148^^s
1o0|Padded Armor|v|s||||V^2849^4163^^s
1o3|Shadowblade|x|||||x^16885^Heavy Junkbox^k
1o4|Gut Ripper|x|||||x^16884^Sturdy Junkbox^k
1o6|Foreman's Leggings|w|||||w^0^0^k
1o7|Foreman's Gloves|w|||||w^0^0^k
1o8|Foreman's Boots|w|||||w^0^0^k
1o9|Buzzer Blade|d|s||||d^36^Sneed^19.05^0^s
1oc|Rustic Belt|q|s|a|4913||q^170^A New Threat^1^a^s
1of|Shadowhide Battle Axe|w|s||||m^568^Shadowhide Warrior^0^s
1oq|Outfitter Belt|q|s|a|4954||q^21^Skirmish at Echo Ridge^1^a^s
1oy|Diamond Hammer|w|sU||||m^1258^Black Ravager Mastiff^0^s~m^1707^Defias Captive^0^s
1oz|Anvilmar Knife|q|s|a|3268||q^182^The Troll Cave^1^a^s
1p7|Brashclaw's Chopper|w|||||w^0^0^k
1p8|Brashclaw's Skewer|w|||||w^0^0^k
1p9|Duskbringer|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
1pb|Jambiya|v|s||||V^275625^2390^^s
1pc|Poniard|v|s||||V^275625^3650^^s
1pd|Kris|v|s||||V^275625^7115^^s
1pm|Craftsman's Dagger|q|s|a|||q^417^A Pilot's Revenge^8^a^s
1ps|Militia Dagger|q|s|a|257283||q^18^Brotherhood of Thieves^2^a^s
1py|Gloves of Brawn|q|s|h|||q^501^Elixir of Pain^21^h^s
1pz|Inferno Robe|q||h|||q^566^WANTED: Baron Vardus^35^h^k
1q0|Dark Runner Boots|w|s||||m^205^Nightbane Dark Runner^0^s
1q2|Nightwalker Armor|w|||||w^0^0^k
1q3|Brackclaw|Rw|s||||R^520^Brack^0^s
1q4|Blackfang|w|sU||||m^4038^Burning Destroyer^0^s
1q5|Patched Pants|q|s|a|||q^59^Cloth and Leather Armor^7^a^s
1q6|Urchin's Pants|q|s|a|||q^11^Riverpaw Gnoll Bounty^6^a^s
1q8|Rugged Cape|q|s|a|||q^385^Crocolisk Hunting^10^a^s
1q9|Desperado Cape|w|||||w^0^0^k
1qb|Hand of Edward the Odd|w|U||||w^0^0^k
1qc|Krol Blade|w|||||w^0^0^k
1qd|Helm of Narv|w|||||w^0^0^k
1qe|Myrmidon's Signet|w|U||||w^0^0^k
1qh|Militia Buckler|q|s|a|||q^11^Riverpaw Gnoll Bounty^6^a^s
1qm|Icepane Warhammer|w|||||w^0^0^k
1qo|Skeletal Club|w|s||||w^0^0^k
1qq|Frostmane Shortsword|w|s||||m^1120^Frostmane Troll^7.98^s
1qr|Frostmane Club|w|s||||m^1121^Frostmane Snowstrider^8.04^s
1qu|Mark of Kern|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
1qw|Mantle of Thieves|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1qx|Stonesplinter Axe|w|s||||m^1163^Stonesplinter Skullthumper^0^s
1qy|Stonesplinter Dagger|w|s||||m^1166^Stonesplinter Seer^0^s
1qz|Stonesplinter Mace|w|s||||w^0^0^k
1r0|Stonesplinter Blade|w|s||||m^1162^Stonesplinter Scout^4.08^s~m^1161^Stonesplinter Trogg^3.96^s
1r3|Staff of the Blessed Seer|dw|s||||d^48^^0^0^s~m^4809^Twilight Acolyte^0^s
1r6|Sapper's Gloves|w|||||w^0^0^k
1r8|Swampwalker Boots|wx|s||||x^6827^Box of Supplies^k~w^0^0^k
1r9|Necromancer Leggings|wx|||||x^6827^Box of Supplies^k~w^0^0^k
1ra|Forest Tracker Epaulets|w|||||w^0^0^k
1rc|Kam's Walking Stick|d|s||||d^34^Kam Deepfury^29.41^0^s
1rd|Rodentia Flint Axe|w|s||||m^1202^Tunnel Rat Kobold^0^s
1re|Rodentia Shortsword|w|s||||m^1172^Tunnel Rat Vermin^4.1^s~m^1173^Tunnel Rat Scout^3.9^k
1rf|Rat Cloth Belt|w|s||||m^1177^Tunnel Rat Surveyor^0^s
1rg|Rat Cloth Cloak|w|s||||w^0^0^k
1ro|Necrology Robes|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
1rv|Burning War Axe|w|s||||w^0^0^k
1rw|Embossed Leather Vest|c|s||||c^Leatherworking^40^2160^f
1ry|Handstitched Leather Boots|c|s||||c^Leatherworking^1^2149^f
1rz|Handstitched Leather Pants|c|s||||c^Leatherworking^15^2153^f
1s3|Fine Leather Boots|c|s||||c^Leatherworking^65^2158^f
1s4|Fine Leather Cloak|c|s||||c^Leatherworking^70^2159^f
1s5|Embossed Leather Boots|c|s||||c^Leatherworking^55^2161^f
1s6|Embossed Leather Cloak|c|s||||c^Leatherworking^60^2162^f
1s7|White Leather Jerkin|c|s||||c^Leatherworking^40^2163^f
1s8|Fine Leather Gloves|c|s||||c^Leatherworking^50^2164^f
1sb|Gray Leather Boots|c|s||||c^Leatherworking^100^2167^f
1sc|Dark Leather Cloak|c|s||||c^Leatherworking^110^2168^f
1sd|Dark Leather Tunic|c|s||||c^Leatherworking^75^2169^f
1sm|Ivy-weave Bracers|q|s|a|||q^315^The Perfect Stout^5^a^s
1sn|Sturdy Leather Bracers|Rw|s||||m^480^Rusty Harvest Golem^2.03^s~R^276061^NPC 276061^0^s
1tm|Worn Wooden Shield|v|s||||V^252000^7^^s
1to|Woven Vest|v|s|h|||V^3166^296^h^s
1tq|Woven Pants|v|s|h|||V^3166^298^h^s
1tr|Woven Boots|v|s|h|||V^3166^223^h^s
1tt|Woven Gloves|v|s|h|||V^3166^150^h^s
1tu|Battered Leather Harness|v|s|h|||V^3166^377^h^s
1tv|Battered Leather Belt|v|s|h|||V^3166^189^h^s
1tw|Battered Leather Pants|v|s|h|||V^3166^343^h^s
1tx|Battered Leather Boots|v|s|h|||V^3166^259^h^s
1ty|Battered Leather Bracers|v|s|h|||V^3166^173^h^s
1tz|Battered Leather Gloves|v|s|h|||V^3166^173^h^s
1u0|Worn Heater Shield|v||h|1201||V^3167^447^h^s
1u3|Tarnished Chain Vest|vw|s||||V^251965^75^^s~m^11040^Watcher Brownell^0.02^k
1u4|Tarnished Chain Belt|vw|s||||V^251965^37^^s~m^11040^Watcher Brownell^0.02^k
1u5|Tarnished Chain Leggings|vw|s||||V^251965^75^^s~m^11040^Watcher Brownell^0.02^k
1u7|Tarnished Chain Boots|vw|s||||V^251965^57^^s~m^11040^Watcher Brownell^0.02^k
1u8|Tarnished Chain Bracers|vw|s||||V^251965^37^^s~m^11040^Watcher Brownell^0.02^k
1u9|Tarnished Chain Gloves|vw|s||||V^251965^37^^s~m^11040^Watcher Brownell^0.02^k
1ua|Rusted Chain Vest|v|s|h|||V^3161^77^h^s
1ub|Rusted Chain Belt|v|s|h|||V^3161^38^h^s
1uc|Rusted Chain Leggings|v|s|h|||V^3161^77^h^s
1ud|Rusted Chain Boots|v|s|h|||V^3161^59^h^s
1ue|Rusted Chain Bracers|v|s|h|||V^3161^38^h^s
1uf|Rusted Chain Gloves|v|s|h|||V^3161^38^h^s
1ug|Light Mail Armor|v|s||||V^4164^413^^s
1uh|Light Mail Belt|v|s||||V^4164^206^^s
1ui|Light Mail Leggings|v|s||||V^4164^416^^s
1uj|Light Mail Boots|v|s||||V^4164^322^^s
1uk|Light Mail Bracers|vw|s||||V^4164^215^^s~m^299^Young Wolf^0.02^k
1ul|Light Mail Gloves|v|s||||V^4164^215^^s
1um|Light Chain Armor|vw|s||||V^3167^434^h^s~m^299^Young Wolf^0.02^k
1un|Light Chain Belt|v|s|h|||V^3167^217^h^s
1uo|Light Chain Leggings|v|s|h|||V^3167^437^h^s
1up|Light Chain Boots|v|s|h|||V^3167^330^h^s
1uq|Light Chain Bracers|v|s|h|||V^3167^219^h^s
1ur|Light Chain Gloves|v|s|h|||V^3167^220^h^s
1v5|Augmented Chain Vest|v|s||||V^272435^15673^^s
1v6|Augmented Chain Leggings|v|s||||V^272435^15731^^s
1v9|Augmented Chain Bracers|v|s||||V^272435^7952^^s
1va|Augmented Chain Gloves|v|s||||V^272435^7981^^s
1vb|Brigandine Vest|v|s||||V^8129^42770^^s
1vd|Brigandine Leggings|v|s||||V^8129^43077^^s
1vg|Brigandine Gloves|v|s||||V^8129^20222^^s
1vh|Russet Vest|vw|s||||V^251980^10138^^s
1vj|Russet Pants|vw|s||||V^251980^10215^^s
1vk|Russet Boots|vw|s||||V^251980^7690^^s
1vm|Russet Gloves|vw|s||||V^251980^5165^^s
1vn|Embroidered Armor|v|s||||V^251980^27683^^s
1vp|Embroidered Pants|v|s||||V^251980^27890^^s
1vs|Embroidered Gloves|v|s||||V^251980^14099^^s
1vx|Large Metal Shield|v|s||||V^3493^3433^^s
1vy|Kite Shield|v|s||||V^4240^6182^^s
1w0|Heavy Pavise|v|s||||V^272435^16158^^s
1w3|Crested Heater Shield|v|s||||V^8129^43629^^s
1wf|Studded Doublet|v|s||||V^272435^13695^^s
1wl|Studded Gloves|v|s||||V^272435^6334^^s
1wm|Reinforced Leather Vest|v|s||||V^12023^33952^^s
1wr|Reinforced Leather Gloves|v|s||||V^12023^17298^^s
1wv|Broad Axe|v|s||||V^251364^107^^s
1ww|Large Club|v|s||||V^251364^72^^s
1x4|Gladius|vw|s||||V^257422^536^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1x5|Two-handed Sword|vw|s||||V^257422^342^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1x6|Tomahawk|vw|s||||V^257422^540^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1x7|Large Axe|vw|s||||V^257422^484^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1x8|Cudgel|vw|s||||V^257422^284^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1x9|Wooden Mallet|vw|s||||V^257422^701^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1xa|Stiletto|vw|s||||V^257422^401^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1xb|Walking Stick|vw|s||||V^256507^504^^s~m^2265^Hillsbrad Apprentice Blacksmith^2^k
1xk|Worn Shortbow|v|s||||V^28989^29^^s
1xl|Polished Shortbow|v|s||||V^28989^60^^s
1xm|Hornwood Recurve Bow|v|s||||V^28989^285^^s
1xn|Laminated Recurve Bow|v|s||||V^28989^1751^^s
1xp|Ornate Blunderbuss|v|s||||V^1243^414^^s
1xq|Solid Blunderbuss|v|s||||V^1243^41^^s
1xr|Hunter's Boomstick|v|s||||V^7976^1324^^s
1y0|Broadsword|v|s||||V^255897^24628^^s
1y1|Flamberge|v|s||||V^255897^30896^^s
1y2|Crescent Axe|v|s||||V^255897^22548^^s
1y3|Bullova|v|s||||V^255897^28285^^s
1y4|Truncheon|v|s||||V^255897^19192^^s
1y7|Battle Staff|v|s||||V^255897^29356^^s
1y9|Zweihander|v|s||||V^12024^65031^^s
1ya|Francisca|v|s||||V^12024^52219^^s
1yb|Great Axe|v|s||||V^12024^56169^^s
1yc|Morning Star|v|s||||V^12024^52608^^s
1yd|War Maul|v|s||||V^12024^61107^^s
1ye|Rondel|v|s||||V^12024^45431^^s
1yp|Malleable Chain Leggings|q|s|a|||q^471^Apprentice's Duties^21^a^s
1yq|Royal Frostmane Girdle|Rw|s||||R^1260^Great Father Arctikus^0^s
1yr|Boar Handler Gloves|q|s|a|4910||q^179^Dwarven Outfitters^1^a^s
1yt|Staff of the Shade|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
1z8|Elven Spirit Claws|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
1z9|Rod of Molten Fire|wx|||||x^6827^Box of Supplies^k~w^0^0^k
1zb|Evocator's Blade|dw|s||||d^48^Aku'mai^0.02^0^k~d^48^Twilight Lord Kelris^0.02^0^k
1zc|Brown Linen Vest|c|s||||c^Tailoring^10^2385^f
1zd|Linen Boots|c|s||||c^Tailoring^65^2386^f
1ze|Linen Cloak|c|s||||c^Tailoring^1^2387^f
1zf|Viny Wrappings|q|s|a|||q^932^Twisted Hatred^4^a^s
1zg|Red Linen Robe|c|||||c^Tailoring^25^2389^f
1zm|Barbaric Linen Vest|c|s||||c^Tailoring^65^2395^f
1zo|Reinforced Linen Cape|c|s||||c^Tailoring^60^2397^f
1zq|Green Woolen Vest|c|s||||c^Tailoring^85^2399^f
1zr|Woolen Boots|c|s||||c^Tailoring^95^2401^f
1zs|Woolen Cape|c|s||||c^Tailoring^75^2402^f
1zt|Gray Woolen Robe|c|||||c^Tailoring^80^2403^f
20k|Plain Robe|v|s||||V^1309^163^^s
20l|Double-Stitched Robes|v|s||||V^1309^607^^s
20m|Robe of Apprenticeship|v|s||||V^1309^1161^^s
20n|Chromatic Robe|v|s||||V^1309^5091^^s
20o|Shimmering Silk Robes|v|s||||V^1309^2659^^s
20p|Burning Robes|v|s||||V^1309^10991^^s
20q|Silver Dress Robes|v|s||||V^1309^26639^^s
20s|Augural Shroud|w|||||w^0^0^k
20t|Cowl of Necromancy|w|||||w^0^0^k
20u|Nimar's Tribal Headdress|Rw|s||||R^2606^Nimar the Slayer^0^s
20v|Holy Diadem|w|||||w^0^0^k
20w|Thinking Cap|w|||||w^0^0^k
214|Curved Dagger|dw|sr||||d^2999^Witherfang^10^0^s~d^3065^Faldrim Anvilmar^10^0^s
22q|Latched Belt|q|s|a|||q^3905^Grape Manifest^2^a^s
22r|Outfitter Boots|q|s|a|||q^21^Skirmish at Echo Ridge^1^a^s
22u|Settler's Leggings|q|s|h|||q^3281^Stolen Silver^13^h^s
23l|Holy Shroud|x|||||x^4634^Iron Lockbox^k
24i|Tarnished Bastard Sword|w|s||||m^1506^Scarlet Convert^1.9^s
25s|Black Velvet Robes|dw|s||||d^34^^0^0^s~m^1706^Defias Prisoner^0^s
25t|Blade of Hanna|w|||||w^0^0^k
25x|Yeti Fur Cloak|q|s|a|||q^565^Bartolo's Yeti Fur Cloak^29^a^s
25z|Guillotine Axe|dw|||||d^33^Razorclaw the Butcher^0.02^0^k~d^33^Baron Silverlaine^0.02^0^k
267|Curve-bladed Ripper|w|||||w^0^0^k
268|Death Speaker Scepter|d|s||||d^47^Death Speaker Jargba^40^0^s
269|Soft Leather Tunic|q|s|a|||q^314^Protecting the Herd^7^a^s
26a|Stretched Leather Trousers|q|s|h|||q^452^Pyrewood Ambush^12^h^s
26b|Cross Dagger|dwx|sr||||d^90^^0^0^s~m^206^Nightbane Vile Fang^0^s
26d|Mo'grosh Masher|w|||||w^0^0^k
26e|Mo'grosh Toothpick|w|||||w^0^0^k
26f|Mo'grosh Can Opener|w|s||||m^1180^Mo'grosh Brute^0^s
26g|Hurricane|u|||||
26h|Bow of Searing Arrows|u|||||
270|Copper Mace|c|s||||c^Blacksmithing^15^2737^f
271|Copper Axe|c|s||||c^Blacksmithing^20^2738^f
273|Copper Shortsword|c|s||||c^Blacksmithing^40^2739^f
274|Bronze Mace|c|||||c^Blacksmithing^75^2740^f
275|Bronze Axe|c|||||c^Blacksmithing^85^2741^f
276|Bronze Shortsword|c|s||||c^Blacksmithing^95^2742^f
277|Copper Chain Belt|c|s||||c^Blacksmithing^35^2661^f
278|Copper Chain Pants|c|s||||c^Blacksmithing^40^2662^f
279|Copper Bracers|c|s||||c^Blacksmithing^1^2663^f
27a|Runed Copper Bracers|c|s||||c^Blacksmithing^90^2664^f
27d|Runed Copper Belt|c|s||||c^Blacksmithing^80^2666^f
27k|Runed Copper Breastplate|c|s||||c^Blacksmithing^90^2667^f
27l|Rough Bronze Leggings|c|s||||c^Blacksmithing^95^2668^f
27m|Rough Bronze Cuirass|c|s||||c^Blacksmithing^105^2670^f
27n|Rough Bronze Bracers|c|||||c^Blacksmithing^115^2671^f
27o|Patterned Bronze Bracers|c|s||||c^Blacksmithing^120^2672^f
27q|Shining Silver Breastplate|c|s||||c^Blacksmithing^135^2675^f
27x|Combatant Claymore|w|s||||w^0^0^k
27y|Bearded Boneaxe|w|||||w^0^0^k
27z|Antipodean Rod|dw|sU||||d^48^Geilhast^16.67^0^s~m^2261^Syndicate Watchman^0^s
28i|Mountaineer Chestpiece|w|s||||m^1196^Ice Claw Bear^5.24^s
28j|Wendigo Collar|w|||||w^0^0^k
28k|Stone Buckler|q|s|a|||q^287^Frostmane Hold^7^a^s
28l|Mining Pick|dqvw|s||||q^79192^Stepping Stones^19^^s~V^9179^10^^s
28m|Cloak of the Faith|q|s|a|||q^223^Worgen in the Woods^26^a^s
28n|Daryl's Hunting Bow|q|s|a|||q^257^A Hunter's Boast^11^a^s
28o|Daryl's Hunting Rifle|q|s|a|||q^257^A Hunter's Boast^11^a^s
28p|Goat Fur Cloak|q|s|a|||q^315^The Perfect Stout^5^a^s
28q|Darkshire Mail Leggings|Q|s|a|||q^377^Crime and Punishment^22^a^s
28r|Dwarven Tree Chopper|q|s|a|||q^283^A Dark Threat Looms^16^a^s
28s|Thornblade|q|s|a|||q^283^A Dark Threat Looms^16^a^s
28u|Gold Militia Boots|q|s|a|||q^126^Howling in the Hills^20^a^s
28v|Keller's Girdle|w|s||||w^0^0^k
28x|Silk Mantle of Gamn|q|s|a|||q^299^Uncovering the Past^25^a^s
28z|Taran Icebreaker|u|||||
290|Gold Lion Shield|q|s|a|||q^304^A Grim Task^29^a^s
291|Tranquil Ring|q|s|a|||q^304^A Grim Task^29^a^s
29h|Seal of Wrynn|q|s|a|||q^396^An Audience with the King^26^a^s
29p|Prison Shank|d|||||d^34^^33.33^0^k
29r|Eye of Paleth|q|s|a|||q^293^Cleansing the Eye^25^a^s
29x|Mariner Boots|q|s|a|||q^286^Return the Statuette^20^a^s
29y|Icicle Rod|q|s|a|||q^286^Return the Statuette^20^a^s
29z|Ring of the Underwood|wx|U||||x^6827^Box of Supplies^k~w^0^0^k
2a1|Watch Master's Cloak|q|s|a|||q^55^Morbent Fel^27^a^s
2a2|Night Watch Pantaloons|q|s|a|||q^55^Morbent Fel^27^a^s
2a3|First Mate Hat|w|||||w^0^0^k
2a5|Journeyman's Vest|w|s||||m^1195^Forest Lurker^0^s~m^478^Riverpaw Outrunner^0^s
2a7|Journeyman's Boots|vw|s||||V^251981^164^^s~m^474^Defias Rogue Wizard^0^s
2a8|Journeyman's Gloves|w|s||||m^118^Prowler^0^s~m^478^Riverpaw Outrunner^0^s
2a9|Burnt Leather Vest|w|s||||m^95^Defias Smuggler^0^s~m^36^Harvest Golem^0^s
2aa|Burnt Leather Breeches|w|s||||m^478^Riverpaw Outrunner^0^s~m^480^Rusty Harvest Golem^0^s
2ab|Burnt Leather Boots|w|s||||m^46^Murloc Forager^0^s~m^478^Riverpaw Outrunner^0^s
2ac|Burnt Leather Gloves|w|s||||m^478^Riverpaw Outrunner^0^s~m^480^Rusty Harvest Golem^0^s
2ad|Warrior's Tunic|w|s||||m^118^Prowler^0^s~m^515^Murloc Raider^0^s
2ae|Warrior's Pants|w|s||||m^46^Murloc Forager^0^s~m^480^Rusty Harvest Golem^0^s
2af|Warrior's Boots|w|s||||m^46^Murloc Forager^0^s~m^95^Defias Smuggler^0^s
2ag|Warrior's Gloves|w|s||||m^116^Defias Bandit^0^s~m^1532^Wandering Spirit^0^s
2ah|Spellbinder Vest|dw|s||||d^43^^0^0^s~m^122^Defias Highwayman^0^s
2ai|Spellbinder Pants|dwx|s||||d^2999^Viktor the Vile^10^0^s~m^423^Redridge Mongrel^0^s
2aj|Spellbinder Boots|vw|s||||V^251981^544^^s~m^589^Defias Pillager^0^s
2ak|Spellbinder Gloves|dw|s||||d^2999^^0^0^s~m^1912^Dalaran Protector^0^s
2al|Hunting Tunic|dw|s||||d^3065^^0^0^s~d^36^^0^0^s
2am|Hunting Pants|dw|s||||d^2999^Witherfang^10^0^s~d^36^^0^0^s
2an|Hunting Boots|wx|s||||m^590^Defias Looter^0^s~m^454^Young Goretusk^0^s
2ao|Hunting Gloves|dwx|s||||d^2999^^0^0^s~m^114^Harvest Watcher^0^s
2ap|Veteran Armor|dwx|s||||d^36^Rhahk'Zor^10.53^0^s~d^2999^Viktor the Vile^10^0^s
2aq|Veteran Leggings|dw|s||||d^2999^Witherfang^10^0^s~d^2999^Viktor the Vile^10^0^s
2ar|Veteran Boots|w|s||||m^114^Harvest Watcher^0^s~m^124^Riverpaw Brute^0^s
2as|Veteran Gloves|dw|s||||d^3065^^0^0^s~m^589^Defias Pillager^0^s
2at|Seer's Robe|Rdw|s||||d^33^^0^0^s~m^428^Dire Condor^0^s
2au|Seer's Pants|dw|s||||d^36^Rhahk'Zor^10.53^0^s~d^36^Sneed^9.52^0^s
2av|Seer's Boots|dw|s||||d^36^^0^0^s~m^426^Redridge Brute^0^s
2aw|Seer's Gloves|dw|s||||d^36^Sneed^9.52^0^s~d^33^^0^0^s
2ax|Inscribed Leather Breastplate|dwx|s||||d^36^Mr. Smite^4.76^0^s~m^440^Blackrock Grunt^0^s
2ay|Inscribed Leather Pants|dwx|s||||d^33^^0^0^s~d^36^^0^0^s
2az|Inscribed Leather Boots|dw|s||||d^36^^0^0^s~m^115^Harvest Reaper^0^s
2b0|Inscribed Leather Gloves|dw|s||||d^33^Razorclaw the Butcher^11.11^0^s~d^36^^0^0^s
2b1|Burnished Tunic|dwx|s||||m^434^Rabid Shadowhide Gnoll^0^s~m^485^Blackrock Outrunner^0^s
2b2|Burnished Leggings|dwx|s||||m^565^Rabid Dire Wolf^0^s~m^598^Defias Miner^0^s
2b3|Burnished Boots|dwx|s||||m^440^Blackrock Grunt^0^s~m^505^Greater Tarantula^0^s
2b4|Burnished Gloves|dw|s||||m^115^Harvest Reaper^0^s~m^1417^Young Wetlands Crocolisk^0^s
2bc|Brood Mother Carapace|Rw|s||||R^471^Mother Fang^0^s
2bk|Wendigo Fur Cloak|w|||||w^0^0^k
2bn|Feathered Headdress|w|||||w^0^0^k
2bu|Hide of Lupos|Rw|s||||R^521^Lupos^0^s
2bv|Noble's Robe|w|s||||w^0^0^k
2bw|Enduring Cap|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
2bx|Ranger Bow|w|s||||m^1034^Dragonmaw Raider^0^s
2by|Bluegill Breeches|w|||||w^0^0^k
2bz|Large Bore Blunderbuss|v|s||||V^260566^3771^^s
2c0|BKP 2700 "Enforcer"|v|s||||V^260566^7098^^s
2c2|Reinforced Bow|v|s||||V^28989^3812^^s
2c3|Heavy Recurve Bow|v|s||||V^28989^6349^^s
2cc|Heavy Shortbow|dw|s||||d^2999^Witherfang^10^0^s~d^389^^0^0^s
2cd|Whipwood Recurve Bow|dwx|s||||d^90^^0^0^s~m^6227^Mechano-Frostwalker^0^s
2cf|Short Ash Bow|dwx|s||||d^48^Lady Sarevess^8.33^0^s~d^34^Kam Deepfury^5.88^0^s
2cg|Hunter's Muzzle Loader|dw|s||||d^43^Skum^25^0^s~d^36^Gilnid^19.05^0^s
2ch|"Mage-Eye" Blunderbuss|Rdw|s||||m^681^Young Stranglethorn Tiger^0^s~m^1051^Dark Iron Dwarf^0^s
2ci|BKP "Sparrow" Smallbore|Rdw|s||||d^47^Overlord Ramtusk^20^0^s~m^4420^Overlord Ramtusk^0^s
2cl|Lambent Scale Boots|dwx|s||||d^2959^^0^0^s~m^2269^Hillsbrad Miner^0^s
2cn|Lambent Scale Gloves|dwx|s||||m^1051^Dark Iron Dwarf^0^s~d^34^Targorr the Dread^0.01^0^k
2co|Lambent Scale Legguards|dwx|s||||m^1715^Defias Insurgent^0^s~m^2427^Jailor Eston^0^s
2cp|Lambent Scale Breastplate|dwx|s||||d^90^Grubbis^20^0^s~d^34^Bazil Thredd^6.25^0^s
2ct|Humbert's Chestpiece|w|s||||m^2344^Dun Garok Mountaineer^0^s
2cv|Forest Leather Chestpiece|dwx|s||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
2cw|Forest Leather Pants|dwx|s||||d^2998^^0^0^s~m^435^Blackrock Champion^0^s
2cx|Forest Leather Boots|dwx|s||||d^34^Dextren Ward^6.25^0^s~m^202^Skeletal Horror^0^s
2cy|Forest Leather Gloves|dwx|s||||m^1715^Defias Insurgent^0^s~d^34^Targorr the Dread^0.01^0^k
2d5|Bright Boots|dwx|s||||d^34^^0^0^s~m^1706^Defias Prisoner^0^s
2d6|Bright Gloves|dwx|s||||d^34^^0^0^s~m^2265^Hillsbrad Apprentice Blacksmith^0^s
2d7|Bright Pants|dwx|s||||d^34^Dextren Ward^6.25^0^s~m^1157^Cursed Sailor^0^s
2d9|Bright Robe|dwx|s||||d^2959^^0^0^s
2da|Ensign Cloak|q|s|a|11847||q^6^Bounty on Garrick Padfoot^2^a^s
2dc|Smoldering Robe|w|||||w^0^0^k
2dd|Smoldering Pants|w|||||w^0^0^k
2de|Smoldering Gloves|w|||||w^0^0^k
2dg|Smoldering Boots|w|||||w^0^0^k
2di|Naga Heartpiercer|d|s||||d^48^Lady Sarevess^8.33^0^s
2dj|Skorn's Rifle|q|s|h|||q^770^The Demon Scarred Cloak^7^h^s
2e7|Coldridge Hammer|q|s|a|||q^314^Protecting the Herd^7^a^s
2fj|Siege Brigade Vest|q|s|a|||q^419^The Lost Pilot^8^a^s
2fk|Driving Gloves|q|s|a|||q^412^Operation Recombobulation^7^a^s
2fl|Oil-stained Cloak|q|s|a|4933||q^412^Operation Recombobulation^7^a^s
2fm|Thelsamar Axe|q|s|a|||q^297^Gathering Idols^13^a^s
2fq|Burnt Hide Bracers|q|s|a|||q^416^Rat Catching^10^a^s
2fs|Ironplate Buckler|q|s|a|||q^307^Filthy Paws^10^a^s
2ft|Robe of the Keeper|q|s|a|||q^307^Filthy Paws^10^a^s
2fy|Ironheart Chain|q|s|a|||q^307^Filthy Paws^10^a^s
2gg|Hook Dagger|dw|sr||||d^36^Sneed^9.52^0^s~d^36^Rhahk'Zor^5.26^0^s
2gh|Acrobatic Staff|dwx|sr||||m^588^Bloodscalp Scout^0^s~m^11563^Drysnap Pincer^0^s
2gi|Viking Sword|dwx|sr||||d^2998^Shadetooth^25^0^s~d^90^^0^0^s
2gj|Sacrificial Kris|wx|sr||||o^Ancient Treasure^1.4^k~x^4637^Steel Lockbox^k
2gk|Coral Claymore|w|||||w^0^0^k
2gl|Wood Chopper|w|s||||m^822^Young Forest Bear^0^s~m^3129^Kul Tiras Marine^0^s
2gm|Beatstick|Rw|s||||m^40^Kobold Miner^0^s~m^478^Riverpaw Outrunner^0^s
2gn|Arced War Axe|d|s||||d^33^Commander Springvale^77.78^0^s
2go|Short Bastard Sword|Rw|sr||||m^6123^Dark Iron Spy^0^s~m^46^Murloc Forager^0^s
2gp|Oak Mallet|dwx|sr||||d^33^Baron Silverlaine^22.22^0^s~d^33^Commander Springvale^11.11^0^s
2gq|Black Malice|dw|s||||m^3877^Wailing Guardsman^0^s~d^33^Razorclaw the Butcher^0.02^0^k
2gr|Barbaric Battle Axe|dw|sr||||d^36^Sneed^9.52^0^s~d^2999^^0^0^s
2gs|Edged Bastard Sword|dw|sr||||d^43^Lord Pythas^22.22^0^s~d^36^Gilnid^4.76^0^s
2gt|Stonecutter Claymore|dwx|sr||||d^189^Interrogator Vishas^18.18^0^s
2gv|Battle Slayer|dwx|sr||||d^43^Skum^12.5^0^s~d^33^Baron Silverlaine^11.11^0^s
2gw|Burnt Leather Bracers|w|s||||m^277730^Rabid Forest Wolf^0^s~m^478^Riverpaw Outrunner^0^s
2gx|Barbarian War Axe|dwx|sr||||d^47^^0^0^s~d^90^^0^0^s
2gy|Forest Leather Bracers|dwx|s||||d^189^Interrogator Vishas^9.09^0^s~d^34^^0^0^s
2gz|Dense Triangle Mace|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
2h0|Deepwood Bracers|w|||||w^0^0^k
2h1|Inscribed Leather Bracers|dw|s||||d^36^^0^0^s~m^634^Defias Overseer^0^s
2h2|Cavalier Two-hander|Rdwx|sr||||d^2998^^0^0^s~R^4015^Pridewing Patriarch^0^s
2h3|Hunting Bracers|w|s||||m^36^Harvest Golem^0^s~m^95^Defias Smuggler^0^s
2h4|Conk Hammer|wx|r||||x^4638^Reinforced Steel Lockbox^k~w^43^50^k
2h5|Ancient War Sword|q|s|a|||q^474^Defeat Nek'rosh^27^a^s
2h6|Brutal War Axe|dwx|sr||||d^2959^^0^0^s~m^2559^Highland Strider^0^s
2h7|Burnished Bracers|dw|s||||m^1956^Elder Lake Creeper^0^s~m^4416^Defias Strip Miner^0^s
2h8|Lambent Scale Bracers|dwx|s||||d^34^Hamhock^5.88^0^s~m^3887^Baron Silverlaine^0^s
2h9|Veteran Bracers|wx|s||||m^589^Defias Pillager^0^s~m^263396^NPC 263396^0^s
2ha|Warrior's Bracers|w|s||||m^116^Defias Bandit^0^s~m^474^Defias Rogue Wizard^0^s
2hd|Foreman Belt|q|s|a|||q^309^Protecting the Shipment^10^a^s
2hj|Frostmane Scepter|w|||||w^0^0^k
2hk|Silver-lined Bracers|Rw|s||||R^1132^Timber^0^s
2hl|Bloodstained Knife|w|||||w^0^0^k
2ho|Jimmied Handcuffs|d|||||d^34^^33.33^0^k
2hp|Tarantula Silk Sash|w|||||w^0^0^k
2hq|Black Wolf Bracers|d|s||||d^33^Fenrus the Devourer^44.44^0^s
2hr|Cutthroat Pauldrons|w|||||w^0^0^k
2hv|Ring of Scorn|q|s|h|||q^530^A Husband's Revenge^15^h^s
2ik|Scarlet Initiate Robes|w|s||||m^1507^Scarlet Initiate^1.1^s
2il|Webbed Cloak|w|s||||m^1688^Night Web Matriarch^78.7^s
2in|Webbed Pants|w|s||||m^1505^Night Web Spider^1.03^s
2ir|Forsaken Shortsword|q|s|h|||q^381^The Scarlet Crusade^2^h^s
2is|Forsaken Dagger|q||h|2195||q^381^The Scarlet Crusade^2^h^s
2iu|Flax Vest|q|s|h|||q^380^Night Web's Hollow^2^h^s
2iw|Zombie Skin Leggings|q||h|61||q^380^Night Web's Hollow^2^h^s
2ix|Rugged Mail Vest|q||h|10656||q^380^Night Web's Hollow^2^h^s
2iy|Flax Boots|q||h|6173||q^3901^Rattling the Rattlecages^1^h^s
2iz|Flax Gloves|q||h|719||q^364^The Mindless Ones^1^h^s
2j0|Deathguard Buckler|q||h|5395||q^382^The Red Messenger^2^h^s
2j1|Executor Staff|q|s|h|||q^382^The Red Messenger^2^h^s
2j3|Battle Chain Boots|w|s||||m^3269^Razormane Geomancer^0^s~m^10158^Moonkin^0^s
2j4|Battle Chain Bracers|w|s||||m^2015^Bloodfeather Harpy^0^s~m^3110^Dreadmaw Crocolisk^0^s
2j5|Battle Chain Gloves|w|s||||m^2190^Wild Grell^0^s~m^3198^Burning Blade Apprentice^0^s
2j6|Battle Chain Pants|w|s||||m^3244^Greater Plainstrider^0^s~m^3265^Razormane Hunter^0^s
2j7|Battle Chain Tunic|dw|s||||d^389^Bazzalan^12.5^0^s~m^11318^Ragefire Trogg^0^s
2j8|Tribal Boots|w|s||||m^2190^Wild Grell^0^s~m^3118^Dustwind Storm Witch^0^s
2j9|Tribal Bracers|w|s||||m^2011^Gnarlpine Augur^0^s~m^2231^Pygmy Tide Crawler^0^s
2ja|Tribal Gloves|w|s||||m^2321^Foreststrider Fledgling^0^s~m^3272^Kolkar Wrangler^0^s
2jb|Tribal Pants|dw|s||||d^389^Oggleflint^6.25^0^s~m^3130^Thunder Lizard^0^s
2jc|Tribal Vest|w|s||||m^3131^Lightning Hide^0^s~m^2069^Moonstalker^0^s
2jd|Ancestral Boots|w|s||||m^3130^Thunder Lizard^0^s
2je|Ancestral Gloves|Rw|s||||m^2164^Rabid Thistle Bear^0^s~m^3198^Burning Blade Apprentice^0^s
2jf|Ancestral Woollies|w|s||||m^2202^Greymist Coastrunner^0^s~m^2212^Deth'ryll Satyr^0^s
2jg|Ancestral Tunic|w|||||w^8^15^k
2jq|Brackwater Boots|dw|s||||d^389^^0^0^s~m^2167^Blackwood Pathfinder^0^s
2jr|Brackwater Bracers|dw|s||||d^389^^0^0^s~m^2015^Bloodfeather Harpy^0^s
2js|Brackwater Gauntlets|w|s||||m^2069^Moonstalker^0^s~m^2201^Greymist Raider^0^s
2jt|Brackwater Leggings|dw|s||||d^389^^0^0^s~m^2235^Reef Crawler^0^s
2ju|Brackwater Vest|dw|s||||d^43^Kresh^22.22^0^s~m^2158^Gravelflint Scout^0^s
2jv|Barbaric Cloth Boots|dw|s||||d^389^Oggleflint^6.25^0^s~m^3272^Kolkar Wrangler^0^s
2jw|Barbaric Cloth Gloves|dw|s||||d^389^^0^0^s~m^3277^Witchwing Roguefeather^0^s
2jx|Barbaric Loincloth|dw|s||||m^11318^Ragefire Trogg^0^s~m^2185^Darkshore Thresher^0^s
2jy|Barbaric Cloth Vest|dw|s||||d^43^^0^0^s~m^3637^Deviate Guardian^0^s
2jz|Ceremonial Leather Ankleguards|dw|s||||d^389^^0^0^s~m^3241^Savannah Patriarch^0^s
2k0|Ceremonial Leather Bracers|dw|s||||d^389^^0^0^s~m^2164^Rabid Thistle Bear^0^s
2k1|Ceremonial Leather Harness|dw|s||||d^43^^0^0^s~m^2168^Blackwood Warrior^0^s
2k2|Ceremonial Leather Gloves|dw|s||||d^389^^0^0^s~m^3425^Savannah Prowler^0^s
2k3|Ceremonial Leather Loincloth|dw|s||||d^389^Jergosh the Invoker^12.5^0^s~m^11322^Searing Blade Cultist^0^s
2k7|Short Sabre|w|s||||m^1529^Bleeding Horror^8.06^s
2k9|Gray Fur Booties|w|s||||m^1549^Ravenous Darkhound^4.18^s
2ka|Wispy Cloak|w|||||w^0^0^k
2kc|Ghostly Mantle|Q|s|h|||q^1098^Deathstalkers in Shadowfang^20^h^s
2kd|Vile Fin Battle Axe|w|s||||m^250283^Vile Fin Attacker^0^s~m^1545^Vile Fin Muckdweller^8.12^k
2kf|Vile Fin Oracle Staff|w|s||||m^1544^Vile Fin Minor Oracle^8.12^s
2kg|Spider Web Robe|w|s||||m^1555^Vicious Night Web Spider^5.03^s
2ki|Dargol's Hauberk|w|||||w^0^0^k
2kj|Melrache's Cape|w|||||m^1665^Captain Melrache^4.08^k
2kk|Perrine's Boots|w|||||m^1662^Captain Perrine^6.9^k
2km|Farmer's Shovel|qw|s||||q^79192^Stepping Stones^19^^s~m^1934^Tirisfal Farmer^0^s
2kt|Gauntlets of Ogre Strength|w|||||w^0^0^k
2kw|Captain Sander's Sash|q|s||||q^140^Captain Sander's Hidden Treasure^11^^s
2kx|Silk Wizard Hat|w|||||w^0^0^k
2m8|Ringed Helm|Rw|s||||R^2108^Garneg Charskull^0^s
2mg|Lucine Longsword|Q|s|a|||q^386^What Comes Around...^22^a^s
2mt|Doomspike|dw|s||||d^48^^0^0^s~m^4798^Fallenroot Shadowstalker^0^s
2mu|Crested Scepter|dw|||||d^48^Aku'mai^0.02^0^k~d^48^Twilight Lord Kelris^0.02^0^k
2mv|Staff of the Friar|dw|s||||d^48^^0^0^s~m^4813^Twilight Shadowmage^0^s
2mw|Martyr's Chain|dw|||||d^48^Aku'mai^0.02^0^k~d^48^Twilight Lord Kelris^0.02^0^k
2mx|Onyx Claymore|dw|s||||m^4813^Twilight Shadowmage^0^s~d^48^Aku'mai^0.02^0^k
2n9|Guardsman Belt|w|||||w^0^0^k
2na|Sniper Rifle|wx|sr||||o^Ancient Treasure^2.3^k~o^Captain's Chest^2.1^k
2nb|Bone-studded Leather|q|s|a|||q^219^Missing In Action^20^a^s
2nf|Zombie Skin Bracers|q|s|h|||q^374^Proof of Demise^5^h^s
2nh|Clasped Belt|q|s|h|||q^374^Proof of Demise^5^h^s
2nj|Zombie Skin Boots|q|s|h|||q^358^Graverobbers^4^h^s
2nk|Bonecracker|q|s|h|||q^408^The Family Crypt^8^h^s
2nm|Apprentice Sash|q|s|h|||q^369^A New Plague^6^h^s
2nn|Ceremonial Tomahawk|q|s|h|||q^98435^Thunderhorn's Report^5^h^s~q^760^Wildmane Cleansing^5^h^s
2no|Tiller's Vest|q|s|h|||q^398^Wanted: Maggot Eye^6^h^s
2nq|Darkwood Staff|q|s|h|||q^408^The Family Crypt^8^h^s
2nt|Mystic Shawl|q|s|h|||q^452^Pyrewood Ambush^12^h^s
2nu|Faerleia's Shield|q|s|h|||q^452^Pyrewood Ambush^12^h^s
2nv|Nightglow Concoction|q|s|h|||q^451^A Recipe For Death^13^h^s
2nw|Ceranium Rod|q|s|h|||q^480^The Weaver^17^h^s
2nx|Quilted Bracers|q|s|h|||q^425^Ivar the Foul^10^h^s
2ny|Reconnaissance Boots|q||h|15398||q^437^The Dead Fields^10^h^s
2o1|Stamped Trousers|q|s|h|||q^491^Wand to Bethor^13^h^s
2o2|Rugged Mail Gloves|q|s|h|||q^491^Wand to Bethor^13^h^s
2o5|High Robe of the Adjudicator|q|s|h|||q^442^Assault on Fenris Isle^19^h^s
2o6|Talonstrike|q|s|h|||q^442^Assault on Fenris Isle^19^h^s
2o7|Silver Star|q|s||||q^1370^Stealing Supplies^30^^s
2od|Copper Chain Boots|c|s||||c^Blacksmithing^20^3319^f
2of|Copper Chain Vest|cw|||||c^Blacksmithing^30^3321^f
2og|Runed Copper Gauntlets|c|s||||c^Blacksmithing^40^3323^f
2oh|Runed Copper Pants|c|s||||c^Blacksmithing^45^3324^f
2oi|Gemmed Copper Gauntlets|c|r||||c^Blacksmithing^35^3325^f
2oj|Cloak of Flames|w|||||w^0^0^k
2oo|Rough Bronze Shoulders|c|s||||c^Blacksmithing^110^3328^f
2op|Silvered Bronze Shoulders|c|s||||c^Blacksmithing^100^3330^f
2oq|Silvered Bronze Boots|c|s||||c^Blacksmithing^130^3331^f
2or|Silvered Bronze Gauntlets|c|s||||c^Blacksmithing^135^3333^f
2os|Green Iron Boots|c|s||||c^Blacksmithing^120^3334^f
2ot|Green Iron Gauntlets|c|||||c^Blacksmithing^125^3336^f
2ov|Heavy Copper Broadsword|c|||||c^Blacksmithing^90^3292^f
2ow|Copper Battle Axe|c|||||c^Blacksmithing^35^3293^f
2ox|Thick War Axe|c|||||c^Blacksmithing^70^3294^f
2oy|Deadly Bronze Poniard|c|||||c^Blacksmithing^100^3295^f
2oz|Heavy Bronze Mace|c|||||c^Blacksmithing^130^3296^f
2p0|Mighty Iron Hammer|c|||||c^Blacksmithing^120^3297^f
2p1|Raptor's End|q|s|a|||q^296^Ormer's Revenge^24^a^s
2pj|Cloak of the People's Militia|q|s|a|||q^153^Red Leather Bandanas^10^a^s
2qr|Robe of Solomon|q|s|a|||q^219^Missing In Action^20^a^s
2qs|Dread Mage Hat|q||a|||q^397^You Have Served Us Well^25^a^k
2qu|Fen Keeper Robe|q|s|a|||q^275^Blisters on The Land^21^a^s
2qv|Night Watch Gauntlets|q|s|a|||q^245^Eight-Legged Menaces^17^a^s
2qw|Mantle of Honor|q|s|a|||q^253^Bride of the Embalmer^25^a^s
2qx|Resilient Poncho|q|s|a|||q^471^Apprentice's Duties^21^a^s
2qy|Belt of Vindication|Q|s|a|||q^378^The Fury Runs Deep^22^a^s
2qz|Seafarer's Pantaloons|w|||||w^0^0^k
2r1|Beerstained Gloves|q|s|a|||q^466^Search for Incendicite^20^a^s
2r2|Raptorbane Armor|q|s|a|||q^296^Ormer's Revenge^24^a^s
2r3|Dwarven Fishing Pole|q|s|a|||q^150^Murloc Poachers^20^a^s
2r5|Vicar's Robe|w|||||w^0^0^k
2r6|Bonegrinding Pestle|q|s|h|||q^99^Arugal's Folly^10^h^s
2r7|Trogg Beater|w|||||w^0^0^k
2r8|Daryl's Shortsword|q|s|a|||q^258^A Hunter's Challenge^12^a^s
2re|Harvester's Pants|q|s|a|||q^9^The Killing Fields^10^a^s
2rh|Serrated Knife|q|s|h|||q^491^Wand to Bethor^13^h^s
2ri|Acidproof Cloak|q|s|h|||q^451^A Recipe For Death^13^h^s
2rj|Weathered Belt|q|s|h|||q^425^Ivar the Foul^10^h^s
2rl|Camouflaged Tunic|q|s|h|||q^480^The Weaver^17^h^s
2rm|Logsplitter|q|s|h|||q^99^Arugal's Folly^10^h^s
2ro|Embroidered Bracers|v|s||||V^251980^14365^^s
2rp|Heavy Weave Belt|v|s||||V^3683^576^^s
2rq|Heavy Weave Bracers|v|s||||V^3683^578^^s
2rr|Padded Belt|v|s||||V^2849^2097^^s
2rs|Padded Bracers|v|s||||V^2849^2104^^s
2ru|Russet Bracers|vw|s||||V^251980^5497^^s
2rv|Tattered Cloth Belt|v|s|h|||V^3160^23^h^s
2rw|Tattered Cloth Bracers|v|s|h|||V^3160^23^h^s
2rx|Thick Cloth Belt|v|s||||V^2849^1081^^s
2ry|Thick Cloth Bracers|v|s||||V^2849^1085^^s
2rz|Thin Cloth Belt|v|s||||V^251365^24^^s
2s0|Thin Cloth Bracers|v|s||||V^251365^24^^s
2s2|Knitted Belt|vw|s||||V^3952^145^^s~m^3530^Pyrewood Tailor^84.14^k
2s3|Knitted Bracers|vw|s||||V^3952^145^^s~m^3530^Pyrewood Tailor^84.26^k
2s6|Woven Belt|v|s|h|||V^3166^147^h^s
2s7|Woven Bracers|v|s|h|||V^3166^148^h^s
2t5|Journeyman's Bracers|w|s||||m^116^Defias Bandit^0^s~m^260157^Elder Snow Leopard^0^s
2t6|Ancestral Bracers|w|s||||m^3268^Razormane Thornweaver^0^s~m^253511^Al'Aketh Pillager^0^s
2t7|Spellbinder Bracers|dw|s||||d^2999^^0^0^s~m^95^Defias Smuggler^0^s
2t8|Barbaric Cloth Bracers|w|s||||m^3254^Sunscale Lashtail^0^s~m^3266^Razormane Defender^0^s
2t9|Seer's Cuffs|dw|s||||d^36^Rhahk'Zor^10.53^0^s~d^2999^Bjork^10^0^s
2tb|Bright Bracers|Rdwx|s||||d^34^Dextren Ward^6.25^0^s~d^34^Hamhock^5.88^0^s
2td|Tribal Buckler|w|s||||m^2013^Gnarlpine Avenger^0^s~m^2021^Bloodfeather Matriarch^0^s
2te|Battle Shield|w|s||||m^3100^Elder Mottled Boar^0^s~m^3206^Voodoo Troll^0^s
2tf|Veteran Shield|dw|s||||d^3065^^0^0^s~m^114^Harvest Watcher^0^s
2tg|Hunting Buckler|w|s||||m^95^Defias Smuggler^0^s~m^590^Defias Looter^0^s
2th|Ceremonial Buckler|dw|s||||d^389^Oggleflint^6.25^0^s~m^2164^Rabid Thistle Bear^0^s
2ti|Brackwater Shield|dw|s||||d^389^Jergosh the Invoker^6.25^0^s~m^11322^Searing Blade Cultist^0^s
2tj|Burnished Shield|dwx|s||||m^505^Greater Tarantula^0^s~m^657^Defias Pirate^0^s
2tk|Lambent Scale Shield|dwx|s||||m^202^Skeletal Horror^0^s~d^34^Targorr the Dread^0.01^0^k
2vb|Hillman's Cloak|c|s||||c^Leatherworking^145^3760^f
2vo|Hooded Cowl|q|s|h|||q^567^Dangerous!^23^h^s
2vp|Orcish War Chain|q|s|h|||q^498^The Rescue^17^h^s
2vv|Skull Ring|q|s|h|||q^546^Souvenirs of Death^20^h^s
2vw|Decapitating Sword|Rdw|sr||||d^34^Dextren Ward^6.25^0^s~d^33^^0^0^s
2vx|Stomping Boots|q|s|h|||q^501^Elixir of Pain^21^h^s
2vy|Bow of Plunder|q|s|h|||q^567^Dangerous!^23^h^s
2vz|Sentry Buckler|q|s|h|||q^567^Dangerous!^23^h^s
2w3|Meditative Sash|q|s|h|||q^515^Elixir of Agony^25^h^s
2w4|Feline Mantle|d|s||||d^33^Wolf Master Nandos^33.33^0^s
2w5|High Apothecary Cloak|q|s|h|||q^515^Elixir of Agony^25^h^s
2w6|Ribbed Breastplate|q|s|h|||q^547^Humbert's Sword^26^h^s
2w7|Mercenary Leggings|q|s|h|||q^547^Humbert's Sword^26^h^s
2w8|Grunt Vest|q|s|h|||q^498^The Rescue^17^h^s
2w9|Shepherd's Girdle|q|s|a|||q^564^Costly Menace^30^a^s
2wa|Shepherd's Gloves|q|s|a|||q^564^Costly Menace^30^a^s
2wb|Fish Gutter|q|s|a|||q^562^Stormwind Ho!^27^a^s
2we|Crusader Belt|q|s|a|||q^505^Syndicate Assassins^28^a^s
2wf|Insulated Sage Gloves|q|s|a|||q^505^Syndicate Assassins^28^a^s
2wg|Band of the Undercity|q|s|h|||q^550^Battle of Hillsbrad^27^h^s
2wh|Deadskull Shield|q|s|h|||q^550^Battle of Hillsbrad^27^h^s
2wj|Lunar Buckler|q|s|a|||q^504^Crushridge Warmongers^35^a^s
2wl|Brigand's Pauldrons|q||h|||q^508^Taretha's Gift^35^h^k
2y6|Runic Darkblade|q|s|h|||q^550^Battle of Hillsbrad^27^h^s
2yh|Adept's Cloak|q|s|h|||q^375^The Chill of Death^7^h^s
2yi|Sturdy Cloth Trousers|q|s|h|||q^426^The Mills Overrun^6^h^s
2yj|Green Iron Bracers|c|s||||c^Blacksmithing^165^3501^f
2yl|Golden Scale Coif|c|||||c^Blacksmithing^165^3503^f
2yo|Green Iron Shoulders|c|s||||c^Blacksmithing^135^3504^f
2yp|Golden Scale Shoulders|cw|||||c^Blacksmithing^150^3505^f
2ys|Green Iron Hauberk|c|s||||c^Blacksmithing^180^3508^f
2yt|Golden Scale Cuirass|c|||||c^Blacksmithing^170^3511^f
2yu|Polished Steel Boots|c|||||c^Blacksmithing^160^3513^f
2yv|Golden Scale Boots|c|||||c^Blacksmithing^175^3515^f
2yw|Big Bronze Knife|c|s||||c^Blacksmithing^100^3491^f
2yx|Hardened Iron Shortsword|c|||||c^Blacksmithing^135^3492^f
2yy|Jade Serpentblade|c|||||c^Blacksmithing^150^3493^f
2yz|Solid Iron Maul|c|||||c^Blacksmithing^130^3494^f
2z0|Golden Iron Destroyer|c|||||c^Blacksmithing^145^3495^f
2z1|Moonsteel Broadsword|c|||||c^Blacksmithing^155^3496^f
2z2|Frost Tiger Blade|c|||||c^Blacksmithing^175^3497^f
2z3|Massive Iron Axe|c|||||c^Blacksmithing^160^3498^f
2z4|Shadow Crescent Axe|c|||||c^Blacksmithing^175^3500^f
301|Russet Hat|vw|s||||V^251980^7922^^s
302|Studded Hat|v|s||||V^272435^10201^^s
303|Augmented Chain Helm|v|s||||V^272435^12284^^s
304|Embroidered Hat|v|s||||V^251980^21940^^s
305|Reinforced Leather Cap|v|s||||V^12023^27523^^s
306|Brigandine Helm|v|s||||V^8129^29986^^s
30e|Staff of Nobles|Rw|s||||R^596^Brainwashed Noble^0^s
32p|Monogrammed Sash|w|U||||m^1493^Mok'rash^86.5^k
343|Silver-thread Robe|Rdwx|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
344|Silver-thread Cuffs|dwx|s||||d^2959^^0^0^s~m^2344^Dun Garok Mountaineer^0^s
345|Silver-thread Pants|dwx|s||||m^2408^Snapjaw^0^s~m^246890^NPC 246890^0^s
346|Nightsky Robe|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
347|Nightsky Cowl|dwx|s||||d^189^^0^0^s~m^4292^Scarlet Protector^0^s
348|Nightsky Gloves|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
349|Aurora Cowl|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
34a|Aurora Gloves|wx|s||||m^259987^NPC 259987^0^s
34b|Aurora Bracers|wx|s||||m^2567^Boulderfist Magus^0^s~m^258792^NPC 258792^0^s
34c|Aurora Pants|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
34d|Mistscape Bracers|wx|||||o^Ancient Treasure^1.5^k~x^4637^Steel Lockbox^k
34e|Mistscape Pants|wx|||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
34f|Mistscape Boots|wx|||||o^Ancient Treasure^1.5^k~x^4637^Steel Lockbox^k
34g|Emblazoned Hat|Rdwx|s||||m^270892^NPC 270892^0^s~d^90^Grubbis^0.39^0^k
34h|Emblazoned Bracers|dwx|s||||d^2959^^0^0^s
34i|Emblazoned Leggings|Rdwx|s||||m^2371^Daggerspine Siren^0^s~d^90^Grubbis^0.39^0^k
34j|Emblazoned Boots|dwx|s||||m^570^Brain Eater^0^s~m^2344^Dun Garok Mountaineer^0^s
34k|Insignia Cap|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
34m|Insignia Leggings|dwx|s||||m^736^Panther^0^s~m^1085^Elder Stranglethorn Tiger^0^s
34n|Insignia Boots|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
34p|Insignia Chestguard|dwx|s||||m^258573^Mudfin Oracle^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
34q|Glyphed Breastplate|wx|s||||o^Ancient Treasure^0.7^k~x^4637^Steel Lockbox^k
34r|Glyphed Bracers|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k
34s|Glyphed Leggings|wx|s||||m^258687^NPC 258687^0^s
34t|Imperial Leather Bracers|wx|s||||m^2734^Ridge Stalker Patriarch^0^s
34u|Imperial Leather Pants|wx|||||o^Ancient Treasure^0.6^k~o^Large Solid Chest^0.75^k
34v|Imperial Leather Gloves|wx|||||o^Ancient Treasure^1^k~x^4637^Steel Lockbox^k
34w|Emblazoned Buckler|dwx|s||||d^90^Crowd Pummeler 9-60^40^0^s~m^1715^Defias Insurgent^0^s
34x|Combat Shield|dwx|s||||d^189^Bloodmage Thalnos^18.18^0^s
34y|Insignia Buckler|dwx|s||||m^258792^NPC 258792^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
34z|Glyphed Buckler|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
350|Chief Brigadier Shield|wx|||||o^Ancient Treasure^0.7^k~x^4636^Strong Iron Lockbox^k
351|Blackforge Buckler|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
352|Jouster's Crest|dwx|s||||d^189^Herod^33.33^0^s~m^4301^Scarlet Centurion^0^s
353|Glimmering Mail Breastplate|Rdwx|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
354|Glimmering Mail Gauntlets|dwx|s||||m^2408^Snapjaw^0^s~m^7603^Leprous Assistant^0^s
355|Glimmering Mail Greaves|Rdwx|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
356|Mail Combat Armor|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
357|Mail Combat Gauntlets|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
358|Mail Combat Boots|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
359|Mail Combat Headguard|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
35a|Chief Brigadier Coif|wx|s||||m^263899^NPC 263899^0^s
35b|Chief Brigadier Leggings|wx|s||||m^257888^NPC 257888^0^s
35c|Blackforge Cowl|wx|||||o^Ancient Treasure^0.6^k~o^Large Solid Chest^0.75^k
35e|Blackforge Breastplate|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10479^Kovic's Trading Satchel^k
35g|Blackforge Leggings|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10752^Emerald Encrusted Chest^k
35i|Flash Rifle|q|s||||q^705^Pearl Diving^32^^s
35j|Trueshot Bow|wx|sr||||m^5237^Gordunni Ogre Mage^0^s
35l|Ricochet Blunderbuss|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
35m|Mug O' Hurt|wx|||||x^4638^Reinforced Steel Lockbox^k~w^0^0^k
35n|Widowmaker|wx|U||||x^4638^Reinforced Steel Lockbox^k~x^16884^Sturdy Junkbox^k
363|Tiger Hunter Gloves|q|s||||q^188^Tiger Mastery^32^^s
364|Panther Hunter Leggings|q|s||||q^193^Panther Mastery^35^^s
365|Excelsior Boots|q|s||||q^628^Excelsior^33^^s
368|Choker of the High Shaman|q||h|||q^573^Mok'thardin's Enchantment^39^h^k
369|Medicine Blanket|q|||||q^348^Stranglethorn Fever^40^^k
36a|Darktide Cape|q|s||||q^576^Keep An Eye Out^37^^s
36b|Grom'gol Buckler|q||h|||q^569^The Defense of Grom'gol^33^h^k
36d|Scorching Sash|q|s||||q^617^Akiris by the Bundle^38^^s
36e|Poobah's Nose Ring|q|||||q^630^Message in a Bottle^46^^k
36f|Raptor Hunter Tunic|q|s||||q^197^Raptor Mastery^38^^s
36g|Robe of Crystal Waters|q||a|||q^611^The Curse of the Tides^35^a^k
36h|Gemmed Gloves|q|s||||q^213^Hostile Takeover^31^^s
36i|Bookmaker's Scepter|q|s|a|||q^328^The Hidden Key^32^a^s
36j|Frost Metal Pauldrons|q|s|a|||q^331^Report to Doren^32^a^s
36k|Cap of Harmony|q|s|a|||q^622^Return to Corporal Kaleb^32^a^s
36l|Tranquil Orb|q|s|a|||q^206^Mai'Zoth^41^a^s
36m|Guerrilla Cleaver|q|s|a|||q^204^Bad Medicine^30^a^s
36n|Shrapnel Blaster|q|s|a|||q^202^Colonel Kurzen^35^a^s
36o|Silver Spade|q|s||||q^600^Venture Company Mining^36^^s
36p|Collection Plate|q|||||q^613^Cracking Maury's Foot^39^^k
36q|Smotts' Compass|q|||||q^618^Facing Negolash^45^^k~q^8554^Facing Negolash^45^^k
36r|Belt of Corruption|q|s||||q^621^Zanzil's Secret^39^^s
36s|Darkspear Armsplints|q|s|h|||q^582^Headhunting^32^h^s
36t|Darkspear Cuffs|q|s|h|||q^582^Headhunting^32^h^s
36u|Nimboya's Mystical Staff|q||h|||q^592^Saving Yenniku^41^h^k
36v|Bloodbone Band|q||h|||q^596^Bloody Bone Necklaces^32^h^k
36w|Darkspear Boots|q||h|||q^598^Split Bone Necklace^37^h^k
36x|Darkspear Shoes|q||h|||q^598^Split Bone Necklace^37^h^k
36y|Blackwater Tunic|q|s||||q^608^The Bloodsail Buccaneers^40^^s
36z|Junglewalker Sandals|q|s|a|||q^331^Report to Doren^32^a^s
370|Palm Frond Mantle|q|s|a|||q^204^Bad Medicine^30^a^s
38l|Berylline Pads|Q|s||||q^1101^The Crone of the Kraul^29^a^s~q^1102^A Vengeful Fate^29^h^s
39p|Handstitched Leather Belt|c|s||||c^Leatherworking^25^3753^f
39r|Embossed Leather Gloves|c|s||||c^Leatherworking^55^3756^f
39u|Embossed Leather Pants|c|s||||c^Leatherworking^75^3759^f
39v|Fine Leather Tunic|c|s||||c^Leatherworking^85^3761^f
39w|Hillman's Leather Vest|c|s||||c^Leatherworking^75^3762^f
39y|Fine Leather Belt|c|s||||c^Leatherworking^80^3763^f
39z|Hillman's Leather Gloves|c|s||||c^Leatherworking^145^3764^f
3a1|Dark Leather Belt|c|s||||c^Leatherworking^125^3766^f
3a2|Hillman's Belt|c|s||||c^Leatherworking^95^3767^f
3a3|Hillman's Shoulders|c|s||||c^Leatherworking^130^3768^f
3a4|Dark Leather Shoulders|c|s||||c^Leatherworking^115^3769^f
3a5|Toughened Leather Gloves|c|s||||c^Leatherworking^135^3770^f
3a6|Barbaric Gloves|c|||||c^Leatherworking^125^3771^f
3a7|Green Leather Armor|c|s||||c^Leatherworking^130^3772^f
3a8|Guardian Armor|c|||||c^Leatherworking^150^3773^f
3a9|Green Leather Belt|c|||||c^Leatherworking^155^3774^f
3aa|Guardian Belt|c|||||c^Leatherworking^145^3775^f
3ab|Green Leather Bracers|c|||||c^Leatherworking^175^3776^f
3ac|Guardian Leather Bracers|c|||||c^Leatherworking^170^3777^f
3ad|Solliden's Trousers|Rw|s||||R^1936^Farmer Solliden^0^s
3af|Standard Issue Shield|w|s||||m^1660^Scarlet Bodyguard^4.07^k
3b6|Dust Bowl|w|||||w^0^0^k
3bi|Small Green Dagger|w|||||w^0^0^k
3bj|Cranial Thumper|w|||||w^0^0^k
3bn|Heavy Linen Gloves|c|s||||c^Tailoring^35^3840^f
3bo|Green Linen Bracers|c|s||||c^Tailoring^60^3841^f
3bp|Handstitched Linen Britches|c|s||||c^Tailoring^70^3842^f
3bq|Heavy Woolen Gloves|c|s||||c^Tailoring^85^3843^f
3br|Heavy Woolen Cloak|c|||||c^Tailoring^80^3844^f
3bs|Soft-soled Linen Boots|c|s||||c^Tailoring^80^3845^f
3bt|Red Woolen Boots|c|||||c^Tailoring^75^3847^f
3bu|Double-Stitched Woolen Shoulders|c|s||||c^Tailoring^110^3848^f
3bv|Reinforced Woolen Shoulders|c|||||c^Tailoring^95^3849^f
3bw|Heavy Woolen Pants|c|s||||c^Tailoring^110^3850^f
3bx|Phoenix Pants|c|||||c^Tailoring^100^3851^f
3by|Gloves of Meditation|c|s||||c^Tailoring^125^3852^f
3bz|Azure Silk Gloves|c|||||c^Tailoring^120^3854^f
3c0|Spidersilk Boots|c|s||||c^Tailoring^125^3855^f
3c1|Spider Silk Slippers|c|s||||c^Tailoring^115^3856^f
3c2|Enchanter's Cowl|c|||||c^Tailoring^130^3857^f
3c3|Shadow Hood|c|||||c^Tailoring^135^3858^f
3c5|Boots of the Enchanter|c|||||c^Tailoring^140^3860^f
3c6|Long Silken Cloak|c|||||c^Tailoring^170^3861^f
3c7|Icy Cloak|c|||||c^Tailoring^165^3862^f
3c9|Star Belt|c|||||c^Tailoring^165^3864^f
3cb|Phoenix Gloves|c|||||c^Tailoring^100^3868^f
3cn|Brown Linen Pants|c|s||||c^Tailoring^30^3914^f
3d6|Rough Boomstick|c|s||||c^Engineering^50^3925^f
3dd|Deadly Blunderbuss|c|s||||c^Engineering^105^3936^f
3dg|Lovingly Crafted Boomstick|c|||||c^Engineering^120^3939^f
3dn|Silver-plated Shotgun|c|||||c^Engineering^130^3949^f
3dr|Moonsight Rifle|c|||||c^Engineering^145^3954^f
3f2|Ethereal Talisman|q||h|||q^521^The Crown of Will^38^h^k
3f8|Jewel-encrusted Sash|w|||||w^0^0^k
3f9|Channeler's Staff|w|||||w^0^0^k
3fa|Pugilist Bracers|dw|||||d^47^Overlord Ramtusk^0.03^0^k~d^47^Aggem Thorncurse^0.03^0^k
3fb|Bruiser Club|w|s||||w^0^0^k
3ff|Grim Pauldrons|q|s|h|||q^1164^To Steal From Thieves^31^h^s
3fg|Black Husk Shield|w|||||w^0^0^k
3fh|Flesh Carver|w|||||w^0^0^k
3fi|Blackvenom Blade|w|||||w^0^0^k
3fj|Cloak of Night|w|||||w^0^0^k
3fk|Husk of Naraxis|w|||||w^0^0^k
3fq|Talon of Vultros|w|U||||w^0^0^k
3fs|Raptor Hide Belt|c|||||c^Leatherworking^140^4097^f
3fy|Cloak of Rot|w|||||w^0^0^k
3fz|Beaded Raptor Collar|w|||||w^0^0^k
3g0|Trouncing Boots|w|||||w^0^0^k
3g1|Bonefist Gauntlets|w|||||w^0^0^k
3gd|Nefarious Buckler|w|||||w^0^0^k
3h4|Dwarven Guard Cloak|q|s|a|||q^633^The Thandol Span^28^a^s
3h5|Swampland Trousers|q|s|a|||q^633^The Thandol Span^28^a^s
3h7|Pit Fighter's Shield|q||h|||q^646^Trol'kalar^37^h^k
3h8|Blood-tinged Armor|q||h|||q^646^Trol'kalar^37^h^k
3h9|Seawolf Gloves|q|s||||q^664^Drowned Sorrows^35^^s
3hb|Black Water Hammer|q|s||||q^662^Deep Sea Salvage^35^^s
3hy|Steel-clasped Bracers|Q|s|h|||q^1013^The Book of Ur^21^h^s
3hz|Ironforge Memorial Ring|q|s|a|||q^700^A King's Tribute^26^a^s
3i7|White Drakeskin Cap|q||h|||q^673^Foul Magics^35^h^k
3i9|Radiant Silver Bracers|q||h|||q^673^Foul Magics^35^h^k
3ib|Gnomish Zapper|q|s||||q^666^Sunken Treasure^35^^s
3id|Seafire Band|q|||||q^667^Death From Below^39^^k
3ie|Coldwater Ring|q|||||q^667^Death From Below^39^^k
3io|Fine Scimitar|w|s||||m^43^Mine Spider^0^s~m^251918^Highlands Bandit^0^s
3ip|Scalping Tomahawk|w|sr||||m^117^Riverpaw Gnoll^0^s~m^515^Murloc Raider^0^s
3iq|Severing Axe|Rw|sr||||m^2189^Vile Sprite^0^s~m^3129^Kul Tiras Marine^0^s
3ir|Billy Club|w|s||||m^822^Young Forest Bear^0^s~m^260157^Elder Snow Leopard^0^s
3is|Spiked Club|dw|sr||||d^389^Oggleflint^6.25^0^s~d^389^Jergosh the Invoker^6.25^0^s
3it|Simple Dagger|w|s||||m^390^Porcine Entourage^0^s~m^1536^Scarlet Missionary^0^s
3iu|Sturdy Quarterstaff|dw|sr||||d^389^Taragaman the Hungerer^6.25^0^s~m^126^Murloc Coastrunner^0^s
3iv|Merc Sword|dw|sr||||d^2999^The Butcher^10^0^s~d^36^^0^0^s
3ix|Staunch Hammer|Rdw|sr||||d^3065^Infurnus^10^0^s~d^389^Oggleflint^6.25^0^s
3iy|Birchwood Maul|dw|sr||||d^2999^Witherfang^10^0^s~d^2999^The Butcher^10^0^s
3iz|War Knife|Rdw|sr||||d^2999^Bjork^20^0^s~d^36^Sneed^4.76^0^s
3j3|Medicine Staff|dw|sr||||d^33^Rethilgore^12.5^0^s~d^33^Razorclaw the Butcher^11.11^0^s
3j4|Light Bow|dwx|s||||d^43^Lady Anacondra^10^0^s~d^36^^0^0^s
3j5|Compact Shotgun|dw|s||||d^389^Bazzalan^6.25^0^s~m^117^Riverpaw Gnoll^0^s
3k6|Pendant of Myzrael|wx|sU||||m^4301^Scarlet Centurion^0^s~m^4673^Hatefury Betrayer^0^s
3k8|Ryedol's Lucky Pick|Rw|sU||||m^2740^Shadowforge Darkweaver^15^s~m^2739^Shadowforge Tunneler^15^s
3kz|Grimsteel Cape|Q|s|h|||q^1051^Vorrel's Revenge^28^h^s
3l8|Salbac Shield|q|s|a|||q^733^Scrounging^35^a^s
3l9|Ironheel Boots|q|s|a|||q^733^Scrounging^35^a^s
3le|Warrior's Cloak|w|s||||m^260157^Elder Snow Leopard^0^s
3lf|Warrior's Girdle|w|s||||m^732^Murloc Lurker^0^s~m^1115^Rockjaw Skullthumper^0^s
3lg|Walking Boots|w|||||w^0^0^k
3lh|Bright Mantle|dwx|s||||m^1023^Mottled Razormaw^0^s~d^34^Targorr the Dread^0.01^0^k
3li|Journeyman's Cloak|vw|s||||V^251997^123^^s~m^1529^Bleeding Horror^0^s
3lj|Journeyman's Belt|wx|s||||m^474^Defias Rogue Wizard^0^s~m^46^Murloc Forager^0^s
3ll|Burnt Cloak|w|s||||m^118^Prowler^0^s~m^474^Defias Rogue Wizard^0^s
3lm|Burnt Leather Belt|w|s||||m^199^Young Fleshripper^0^s~m^46^Murloc Forager^0^s
3lo|Battle Chain Cloak|w|s||||m^2020^Bloodfeather Wind Witch^0^s~m^2189^Vile Sprite^0^s
3lp|Battle Chain Girdle|w|s||||m^3117^Dustwind Savage^0^s~m^3198^Burning Blade Apprentice^0^s
3lr|Ancestral Cloak|w|s||||m^3130^Thunder Lizard^0^s~m^3131^Lightning Hide^0^s
3ls|Ancestral Belt|w|s||||m^3267^Razormane Water Seeker^0^s~m^2012^Gnarlpine Pathfinder^0^s
3lu|Tribal Cloak|w|s||||m^3127^Venomtail Scorpid^0^s~m^251707^Ornery Galestrider^0^s
3lv|Tribal Belt|w|s||||m^2964^Windfury Sorceress^0^s~m^252763^Al'Aketh Spiritcaller^0^s
3lw|Skeletal Gauntlets|w|s||||m^624^Undead Excavator^0^s
3lx|Veteran Cloak|wx|s||||m^126^Murloc Coastrunner^0^s~m^95^Defias Smuggler^0^s
3ly|Veteran Girdle|wx|s||||m^263438^NPC 263438^0^s~m^157^Goretusk^0^s
3m0|Brackwater Cloak|w|s||||m^3273^Kolkar Stormer^0^s~m^2185^Darkshore Thresher^0^s
3m1|Brackwater Girdle|w|s||||m^2203^Greymist Seer^0^s~m^3397^Kolkar Bloodcharger^0^s
3m3|Spellbinder Cloak|vw|s||||V^251997^461^^s~m^36^Harvest Golem^0^s
3m4|Spellbinder Belt|w|s||||m^263389^NPC 263389^0^s~m^589^Defias Pillager^0^s
3m6|Barbaric Cloth Cloak|w|s||||m^3244^Greater Plainstrider^0^s~m^3381^Southsea Brigand^0^s
3m7|Barbaric Cloth Belt|dw|s||||d^389^^0^0^s~m^11323^Searing Blade Enforcer^0^s
3m9|Hunting Cloak|wx|s||||m^589^Defias Pillager^0^s~m^1892^Moonrage Watcher^0^s
3ma|Hunting Belt|w|s||||m^126^Murloc Coastrunner^0^s~m^454^Young Goretusk^0^s
3mc|Ceremonial Cloak|w|s||||m^2164^Rabid Thistle Bear^0^s~m^2234^Young Reef Crawler^0^s
3md|Ceremonial Leather Belt|dw|s||||d^389^^0^0^s~m^2190^Wild Grell^0^s
3me|Burnished Pauldrons|wx|s||||m^1732^Defias Squallshaper^0^s
3mf|Burnished Cloak|dw|s||||d^36^Rhahk'Zor^10.53^0^s~m^114^Harvest Watcher^0^s
3mg|Lapidis Tankard of Tidesippe|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
3mh|Burnished Girdle|dw|s||||d^36^Mr. Smite^9.52^0^s~m^428^Dire Condor^0^s
3mi|Seer's Mantle|wx|s||||m^622^Goblin Engineer^0^s
3mj|Seer's Belt|dw|s||||d^36^Captain Greenskin^9.52^0^s~d^36^Rhahk'Zor^5.26^0^s
3mk|Inscribed Leather Spaulders|wx|s||||m^122^Defias Highwayman^0^s~m^641^Goblin Woodcarver^0^s
3ml|Inscribed Cloak|dwx|s||||d^2999^^0^0^s~d^36^^0^0^s
3mp|Lambent Scale Pauldrons|dwx|s||||m^246890^NPC 246890^0^s~m^533^Nightbane Shadow Weaver^0^s
3mq|Lambent Scale Cloak|dwx|s||||d^34^^0^0^s~m^1708^Defias Inmate^0^s
3mr|Lambent Scale Girdle|dwx|s||||d^90^^0^0^s~m^6329^Irradiated Pillager^0^s
3ms|Bright Belt|dwx|s||||d^33^^0^0^s~m^1031^Crimson Ooze^0^s
3mt|Forest Leather Mantle|dwx|s||||m^435^Blackrock Champion^0^s~m^531^Skeletal Fiend^0^s
3mu|Forest Cloak|dwx|s||||d^33^^0^0^s~m^437^Blackrock Renegade^0^s
3mv|Glimmering Cloak|dwx|s||||d^2959^^0^0^s~m^1110^Skeletal Raider^0^s
3mw|Glimmering Mail Girdle|dwx|s||||m^1715^Defias Insurgent^0^s~m^246600^NPC 246600^0^s
3mx|Silver-thread Cloak|dwx|s||||d^34^Kam Deepfury^11.76^0^s~d^90^^0^0^s
3my|Silver-thread Sash|dwx|s||||d^2959^Unstable Sentinel^14.29^0^s~m^1717^Hamhock^0^s
3mz|Emblazoned Cloak|dwx|s||||d^34^^0^0^s~m^604^Plague Spreader^0^s
3n0|Combat Cloak|Rdx|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
3n1|Mail Combat Belt|dwx|s||||m^4287^Scarlet Gallant^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
3n2|Nightsky Mantle|dwx|s||||m^1096^Venture Co. Geologist^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
3n3|Nightsky Cloak|Rdwx|s||||m^570^Brain Eater^0^s~m^2406^Mountain Lion^0^s
3n4|Nightsky Sash|Rdwx|s||||m^736^Panther^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
3n5|Insignia Mantle|dwx|s||||m^2907^Dustbelcher Mystic^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
3n6|Insignia Cloak|Rdwx|s||||d^2959^^0^0^s~m^1108^Mistvale Gorilla^0^s
3n7|Humbert's Pants|w|s||||m^2346^Dun Garok Priest^0^s
3n8|Humbert's Helm|w|||||w^0^0^k
3n9|Chief Brigadier Pauldrons|dwx|s||||d^189^^0^0^s~m^4295^Scarlet Myrmidon^0^s
3na|Chief Brigadier Cloak|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k
3nb|Chief Brigadier Girdle|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
3nc|Twain's Shoulder|u|||||
3nd|Aurora Mantle|wx|s||||m^258849^NPC 258849^0^s
3nf|Glyphed Epaulets|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
3ng|Glyphed Cloak|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k
3nh|Blackforge Pauldrons|wx|||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
3ni|Mistscape Mantle|wx|||||o^Ancient Treasure^0.8^k~o^Captain's Chest^0.8^k
3nj|Mistscape Cloak|wx|s||||m^262473^Cinderscale Whelp^0^s
3nk|Mistscape Sash|wx|||||o^Ancient Treasure^1.2^k~x^4637^Steel Lockbox^k
3nl|Imperial Leather Spaulders|wx|s||||o^Ancient Treasure^1.7^k~o^Captain's Chest^1.3^k
3nm|Imperial Leather Belt|wx|s||||o^Ancient Treasure^1.9^k~o^Captain's Chest^0.8^k
3np|Stromgarde Cavalry Leggings|q|s|a|||q^682^Stromgarde Badges^32^a^s
3nr|Pulsating Crystalline Shard|q|||||q^656^Summoning the Princess^45^^k
3ns|Arcane Runed Bracers|q|s|a|||q^684^Wanted!  Marez Cowl^34^a^s
3nt|War Rider Bracers|q|s|a|||q^685^Wanted!  Otto and Falconcrest^35^a^s
3nu|Doomsayer's Robe|Q|s||||q^709^Solution to Doom^35^^s
3od|Enamelled Broadsword|v|s||||V^3658^2877^^s
3oe|Feral Blade|vw|s||||V^3658^2407^^s
3of|Coppercloth Gloves|w|||||w^0^0^k
3og|Adept's Gloves|R|s||||R^3270^Elder Mystic Razorsnout^50^s
3oj|Harvest Cloak|w|||||w^0^0^k
3ok|Warm Cloak|R|||||R^5785^Sister Hatelash^46.2^k
3op|Ironwood Maul|v|s||||V^2840^7040^^s
3oq|Heavy Spiked Mace|v|s||||V^3658^7350^^s
3ot|Whispering Vest|v|s||||V^3683^2735^^s
3ou|Solstice Robe|v|s||||V^3683^2076^^s
3ox|Brimstone Belt|w|||||w^0^0^k
3oy|Wise Man's Belt|v|s||||V^3683^1393^^s
3p0|Agile Boots|v|s||||V^3684^2633^^s
3p1|Stable Boots|v|s||||V^3684^1998^^s
3p4|Spirit Cloak|v|s||||V^3096^3279^^s
3p5|Sylvan Cloak|v|s||||V^3096^3720^^s
3p6|Wolf Bracers|v|s||||V^3536^3515^^s
3p7|Bear Bracers|v|s||||V^3536^3528^^s
3p8|Owl Bracers|v|s||||V^3536^3540^^s
3pa|Heavy Runed Cloak|v|s||||V^3493^5832^^s
3pb|Antiquated Cloak|v|s||||V^3493^3042^^s
3pc|Mighty Chain Pants|v|s||||V^3493^6109^^s
3pm|Boulder Pads|w|||||w^0^0^k
3ps|Legionnaire's Leggings|v|s||||V^3493^7518^^s
3pt|Blessed Claymore|v|s||||V^4086^12311^^s
3pu|Executioner's Sword|v|s||||V^4890^14273^^s
3pw|Guardian Buckler|v|s||||V^3493^8320^^s
3px|Bear Buckler|v|s||||V^3493^6541^^s
3py|Owl's Disk|v|s||||V^3493^6746^^s
3q0|Blurred Axe|v|s||||V^3180^16856^^s
3q1|Callous Axe|v|s||||V^3180^20472^^s
3q2|Marauder Axe|v|s||||V^4890^15436^^s
3q3|Wizard's Belt|v|s||||V^3537^3748^^s
3q4|Nightwind Belt|v|s||||V^3134^3420^^s
3q5|Dreamer's Belt|v|s||||V^3134^4153^^s
3q6|Saber Leggings|v|s||||V^3536^9474^^s
3q7|Stalking Pants|v|s||||V^3536^7858^^s
3q8|Mystic Sarong|v|s||||V^3536^10497^^s
3q9|Glorious Shoulders|v|s||||V^4890^8658^^s
3qb|Elite Shoulders|v|s||||V^4085^10550^^s
3qd|Strength of Will|v|s||||V^3134^8002^^s
3qe|Orb of Power|v|s||||V^3134^8002^^s
3qu|Demon Scarred Cloak|R|sU||||R^3056^Ghost Howl^100^s
3r1|Sleek Feathered Tunic|w|||||w^0^0^k
3sa|Rainwalker Boots|q|s|h|||q^772^Rite of Vision^3^h^s
3sb|Woodland Tunic|q|s|a|6059||q^917^Webwood Egg^1^a^s
3sc|Nomadic Bracers|q||h|6070||q^750^The Hunt Continues^1^h^s
3sd|Kodo Hunter's Leggings|q|s|h|||q^776^Rites of the Earthmother^9^h^s
3se|Painted Chain Gloves|q||h|2547||q^747^The Hunt Begins^1^h^s
3sf|Thick Bark Buckler|q||h|6078||q^781^Attack on Camp Narache^1^h^s
3sh|Painted Chain Belt|q||h|2172||q^750^The Hunt Continues^1^h^s
3si|Battleworn Leather Gloves|q||h|5394||q^788^Cutting Teeth^1^h^s
3sj|Soft Wool Boots|q||h|80||q^788^Cutting Teeth^1^h^s
3sk|Soft Wool Vest|q|s|h|||q^804^Sarkoth^1^h^s
3sl|Battleworn Chain Leggings|q|s|h|||q^804^Sarkoth^1^h^s
3sn|Soft Wool Belt|q|s|h|||q^789^Sting of the Scorpid^1^h^s
3so|Battleworn Cape|q||h|5405||q^789^Sting of the Scorpid^1^h^s
3sp|Dust-covered Leggings|q||h|5398||q^794^Burning Blade Medallion^1^h^s
3sq|Jagged Chain Vest|q|s|h|||q^794^Burning Blade Medallion^1^h^s
3sr|Primitive Hatchet|q|s|h|||q^792^Vile Familiars^2^h^s
3ss|Primitive Club|q||h|2048||q^792^Vile Familiars^2^h^s
3sw|Sandrunner Wristguards|q|s|h|||q^825^From The Wreckage....^3^h^s
3sz|Hickory Shortbow|q|s|h|||q^835^Securing the Lines^7^h^s
3t1|Seasoned Fighter's Cloak|q||h|3153||q^786^Thwarting Kolkar Aggression^5^h^s
3t3|Wide Metal Girdle|q|s|h|||q^825^From The Wreckage....^3^h^s
3t4|Dirt-trodden Boots|q|s|h|||q^825^From The Wreckage....^3^h^s
3t5|Charging Buckler|q|s|h|||q^812^Need for a Cure^7^h^s
3t7|Steady Bastard Sword|q|s|h|||q^827^Skull Rock^7^h^s
3t8|Veiled Grips|q|s|h|||q^826^Zalazane^5^h^s
3ta|Tiger Hide Boots|q||h|9601||q^806^Dark Storms^7^h^s
3tc|Handsewn Cloak|q|s|h|||q^816^Lost But Not Forgotten^8^h^s
3te|Lightweight Boots|q|s|h|||q^826^Zalazane^5^h^s
3tf|Jagged Dagger|q|s|h|||q^827^Skull Rock^7^h^s
3tg|Stinging Mace|q|s|h|||q^827^Skull Rock^7^h^s
3tj|Squealer's Belt|w|s||||m^3229^"Squealer" Thornmantle^100^s
3tm|Nomadic Belt|q||h|2186||q^747^The Hunt Begins^1^h^s
3tq|Sun-beaten Cloak|q|s|h|||q^772^Rite of Vision^3^h^s
3tt|Dreamwatcher Staff|q|s|h|||q^98435^Thunderhorn's Report^5^h^s~q^760^Wildmane Cleansing^5^h^s
3tu|Double-layered Gloves|q||h|1359||q^768^Gathering Leather^4^h^s
3tv|Thunderhorn Cloak|q|s|h|||q^758^Thunderhorn Cleansing^4^h^s
3tw|Goblin Smasher|q|s|h|||q^765^Supervisor Fizsprocket^7^h^s
3tz|Tribal Warrior's Shield|q||h|5593||q^744^Preparation for Ceremony^7^h^s
3u0|Bound Harness|q|s|h|||q^744^Preparation for Ceremony^7^h^s
3u1|Fortified Bindings|q||h|1182||q^746^Dwarven Digging^6^h^s
3u2|Rough-hewn Kodo Leggings|q|s|h|||q^746^Dwarven Digging^6^h^s
3u3|Skorn's Hammer|q|s|h|||q^770^The Demon Scarred Cloak^7^h^s
3u4|Cliff Runner Boots|q|s|h|||q^766^Mazzranache^5^h^s
3u5|Plains Hunter Wristguards|q|s|h|||q^766^Mazzranache^5^h^s
3u6|Compact Fighting Knife|q|s|h|||q^765^Supervisor Fizsprocket^7^h^s
3u7|Vigilant Buckler|q||a|||q^697^Malin's Request^34^a^k
3u8|Mistspray Kilt|q|s|h|||q^680^The Real Threat^35^h^s
3u9|Sword of Hammerfall|q|s|h|||q^680^The Real Threat^35^h^s
3ub|Enchanted Stonecloth Bracers|q|||||q^716^Stone Is Better than Cloth^37^^k
3uc|Prospector Gloves|Q|s|a|||q^704^Agmond's Fate^33^a^s
3uf|Rock Pulverizer|q|s|a|||q^739^Murdaloc^37^a^s
3ug|Skull of Impending Doom|q|||||q^737^Forbidden Knowledge^35^^k
3uj|Dwarf Captain's Sword|q|s|a|||q^762^An Ambassador of Evil^39^a^s
3uu|Blood Ring|dwx|s||||m^435^Blackrock Champion^0^s~m^1707^Defias Captive^0^s
3uv|Azora's Will|dwx|s||||d^90^Grubbis^20^0^s~d^34^Targorr the Dread^10^0^s
3ux|Heart Ring|dwx|s||||m^533^Nightbane Shadow Weaver^0^s~d^34^Targorr the Dread^0.01^0^k
3uy|Glowing Green Talisman|dwx|s||||m^7603^Leprous Assistant^0^s~d^34^Kam Deepfury^0.01^0^k
3uz|Crystal Starfire Medallion|Rdwx|s||||m^4306^Scarlet Torturer^0^s~m^4664^Burning Blade Reaver^0^s
3v3|Band of Thorns|Rdwx|s||||d^47^Aggem Thorncurse^40^0^s~m^4424^Aggem Thorncurse^0^s
3v5|Mindbender Loop|dwx|s||||m^2588^Syndicate Prowler^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
3v7|Welken Ring|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
3vc|Artisan's Trousers|q|||||q^1203^Jarl Needs a Blade^30^^k
3vp|Talisman of the Naga Lord|w|||||w^0^0^k
3wt|Fire Wand|w|s||||m^454^Young Goretusk^0^s~m^500^Riverpaw Scout^0^s
3wv|Shadow Wand|dw|s||||d^2999^The Abandoned^10^0^s~d^3065^Faldrim Anvilmar^10^0^s
3xg|Charred Razormane Wand|w|s||||m^3458^Razormane Seer^9.72^s
3xx|Stonesplinter Rags|Rw|s||||m^1161^Stonesplinter Trogg^0^s~m^1162^Stonesplinter Scout^0^s
3xz|Rathorian's Cape|w|||||w^0^0^k
3y0|Ritual Blade|w|||||w^0^0^k
3zw|Necklace of Harmony|w|||||w^0^0^k
3zx|Vibrant Silk Cape|w|||||w^0^0^k
3zy|Shiver Blade|Rw|sr||||R^3398^Gesharahan^0^s
3zz|Pulsating Hydra Heart|R|s||||R^3398^Gesharahan^25^s
403|Rhahk'Zor's Hammer|d|s||||d^36^Rhahk'Zor^36.84^0^s
407|Cruel Barb|d|s||||d^36^Edwin VanCleef^28.57^0^s
408|Thief's Blade|d|s||||d^36^Mr. Smite^38.1^0^s
409|Cape of the Brotherhood|d|s||||d^36^Edwin VanCleef^19.05^0^s
40a|Taskmaster Axe|d|s||||d^36^Sneed^14.29^0^s
40b|Gold-flecked Gloves|d|s||||d^36^Sneed^33.33^0^s
40c|Smite's Reaver|d|s||||d^36^Mr. Smite^33.33^0^s
40d|Cookie's Tenderizer|d|s||||d^36^Cookie^28.57^0^s
40e|Cookie's Stirring Rod|d|s||||d^36^Cookie^47.62^0^s
40f|Smelting Pants|d|s||||d^36^Gilnid^61.9^0^s
40g|Impaling Harpoon|d|s||||d^36^Captain Greenskin^52.38^0^s
40h|Emberstone Staff|d|s||||d^36^Captain Greenskin^23.81^0^s~d^36^Edwin VanCleef^4.76^0^s
40i|Corsair's Overshirt|d|s||||d^36^Edwin VanCleef^38.1^0^s
40n|Opaque Wand|dw|s||||d^2999^Bjork^10^0^s~d^36^Sneed^9.52^0^s
40o|Smoldering Wand|v|s||||V^5816^3340^^s
40p|Gloom Wand|v|s||||V^5816^3855^^s
40q|Burning Wand|v|s||||V^5816^5808^^s
40r|Dusk Wand|v|s||||V^5816^5830^^s
40s|Blazing Wand|dw|s||||d^2999^^0^0^s~d^36^^0^0^s
40t|Scorching Wand|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
40u|Wand of Eventide|Rdwx|s||||d^90^^0^0^s~m^6226^Mechano-Flamewalker^0^s
40v|Ember Wand|wx|sr||||m^258038^NPC 258038^0^s
40w|Umbral Wand|wx|r||||o^Ancient Treasure^2^k~o^Captain's Chest^1.7^k
41g|Combustible Wand|v|s||||V^5816^14394^^s
41i|Pitchwood Wand|v|s||||V^5816^35727^^s
41j|Blackbone Wand|v|s||||V^5816^38731^^s
41k|Torchlight Wand|q|s||||q^104^The Coastal Menace^15^^s
41l|Dwarven Flamestick|q|s|a|||q^297^Gathering Idols^13^a^s
41m|Cinder Wand|q|s|h|||q^99^Arugal's Folly^10^h^s
41n|Firebelcher|d|s||||d^43^^0^0^s
41o|Consecrated Wand|q|s|a|||q^223^Worgen in the Woods^26^a^s
41p|Summoner's Wand|w|||||w^0^0^k
41q|Excavation Rod|q|s|a|||q^296^Ormer's Revenge^24^a^s
41r|Rod of Sorrow|q|s|a|||q^685^Wanted!  Otto and Falconcrest^35^a^s
41s|Flash Wand|q|s||||q^705^Pearl Diving^32^^s
41t|Burning Sliver|q|s|a|||q^504^Crushridge Warmongers^35^a^s
41u|Charred Wand|q|s|h|||q^567^Dangerous!^23^h^s
41w|Wand of Decay|q|s|h|||q^516^Beren's Peril^16^h^s
41x|Goblin Igniter|q|s||||q^600^Venture Company Mining^36^^s
41y|Rugged Spaulders|d|s||||d^33^Rethilgore^87.5^0^s
420|Kovork's Rattle|w|||||w^0^0^k
421|Dark Hooded Cape|w|||||w^0^0^k
42a|Eye of Adaegus|rwx|U||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
42b|Scarlet Kris|rw|U||||d^249^Onyxia^2.52^1^k~m^11447^Mushgog^5.19^k
42i|Rose Mantle|q|s|a|||q^249^Morganth^22^a^s
42j|Binding Girdle|q|s|h|||q^872^The Disruption Ends^10^h^s
42n|Harpy Skinner|q|s|h|||q^876^Serena Bloodfeather^15^h^s
437|Gloves of the Moon|q|s|h|||q^913^Cry of the Thunderhawk^15^h^s
43a|Cobalt Buckler|q|s|h|||q^913^Cry of the Thunderhawk^15^h^s
43e|Wind Rider Staff|q|s|h|||q^913^Cry of the Thunderhawk^15^h^s
43h|Privateer Musket|q|s|h|||q^891^The Guns of Northwatch^15^h^s
43i|Sea Dog Britches|q|s|h|||q^891^The Guns of Northwatch^15^h^s
43j|Buckled Boots|q|s|h|||q^898^Free From the Hold^15^h^s
43k|Riveted Gauntlets|q|s|h|||q^898^Free From the Hold^15^h^s
43l|Totemic Clan Ring|q|s|h|||q^849^Revenge of Gann^21^h^s
43m|Boar Hunter's Cape|q|s|h|||q^899^Consumed by Hatred^15^h^s
43n|Timberland Armguards|q|s|a|||q^4740^WANTED: Murkdeep!^15^a^s
43o|Barkshell Tunic|q|s|h|||q^906^Betrayal from Within^20^h^s
43p|Dry Moss Tunic|q|s|h|||q^906^Betrayal from Within^20^h^s
43q|Zhovur Axe|q|s|h|||q^876^Serena Bloodfeather^15^h^s
43r|Bashing Pauldrons|w|||||m^2478^Haren Swifthoof^100^k
43s|Padded Lamellar Boots|q|s||||q^888^Stolen Booty^11^^s
43t|Elegant Shortsword|q|s|h|||q^876^Serena Bloodfeather^15^h^s
43u|Demolition Hammer|q|s|h|||q^893^Weapons of Choice^19^h^s
43v|Everglow Lantern|q|s||||q^893^Weapons of Choice^19^h^s~q^976^Supplies to Auberdine^19^a^s
43w|Engineer's Hammer|q|s||||q^902^Samophlange^11^^s
43x|Welding Shield|q|s||||q^902^Samophlange^11^^s
43y|Flaring Baton|q|s||||q^863^The Escape^13^^s
43z|Greasy Tinker's Pants|q|s||||q^863^The Escape^13^^s
440|Cinched Belt|q|s|h|||q^872^The Disruption Ends^10^h^s
449|Wayfaring Gloves|q|s||||q^888^Stolen Booty^11^^s
44c|Cauldron Stirrer|q|s|h|||q^853^Apothecary Zamah^10^h^s
44d|Spore-covered Tunic|q|s||||q^866^Root Samples^11^^s
44f|Barkeeper's Cloak|q|s||||q^865^Raptor Horns^13^^s
44g|Pointed Axe|q|s|h|||q^855^Centaur Bracers^9^h^s
44h|Stonewood Hammer|q|s|h|||q^855^Centaur Bracers^9^h^s
44i|Orcish Battle Bow|q|s|h|||q^855^Centaur Bracers^9^h^s
44j|Pestilent Wand|v|s||||V^5816^15713^^s
44n|Bounty Hunter's Ring|q|s|h|||q^852^Hezrul Bloodmark^14^h^s
44r|Beastmaster's Girdle|q|s|h|||q^873^Isha Awak^22^h^s
44s|Branding Rod|q|s|h|||q^873^Isha Awak^22^h^s
44t|Ward of the Vale|q|s|h|||q^873^Isha Awak^22^h^s
45u|Archery Training Gloves|q|s|a|4914||q^456^The Balance of Nature^1^a^s
45v|Woodland Shield|q|s|a|3276||q^917^Webwood Egg^1^a^s
45y|Canopy Leggings|q|s|a|4921||q^459^The Woodland Protector^1^a^s
45z|Tracking Boots|q|s|a|||q^459^The Woodland Protector^1^a^s
464|Serpent's Shoulders|d|s||||d^43^Lady Anacondra^0^0^s
465|Draped Cloak|q|s|a|4920||q^457^The Balance of Nature^1^a^s
46j|Feral Bracers|q|s|a|||q^932^Twisted Hatred^4^a^s
46k|Banshee Armor|q|s|h|||q^924^The Demon Seed^9^h^s
46m|Brambleweed Leggings|w|||||w^0^0^k
46n|Boahn's Fang|w|||||w^0^0^k
46p|Runescale Girdle|w|||||w^0^0^k
46q|Serpent's Kiss|w|||||w^0^0^k
477|Gold-plated Buckler|d|s||||d^36^Miner Johnson^0^0^s
478|Miner's Cape|d|s||||d^36^Miner Johnson^0^0^s
47m|Dirtwood Belt|q|s|a|||q^2499^Oakenscowl^4^a^s
47n|Defender Axe|q|s|a|||q^486^Ursal the Mauler^7^a^s
49w|Pearl-handled Dagger|c|s||||c^Blacksmithing^110^6517^f
49x|Iridescent Hammer|c|||||c^Blacksmithing^115^6518^f
49y|Pearl-clasped Cloak|c|s||||c^Tailoring^90^6521^f
4az|Militia Warhammer|q|s|a|||q^18^Brotherhood of Thieves^2^a^s
4b0|Militia Hammer|q|s|a|||q^18^Brotherhood of Thieves^2^a^s
4b1|Smooth Walking Staff|q|s|a|||q^218^The Stolen Journal^1^a^s
4b7|Thornroot Club|q|s|a|||q^486^Ursal the Mauler^7^a^s
4b9|Moss-covered Gauntlets|q|s|a|||q^2499^Oakenscowl^4^a^s
4ba|Cord Bracers|q|s|a|||q^938^Mist^7^a^s
4bb|Rain-spotted Cape|q|s|a|||q^937^The Enchanted Glade^6^a^s
4bc|Shackled Girdle|q|s|a|||q^937^The Enchanted Glade^6^a^s
4bd|Crag Buckler|q|s|a|4967||q^938^Mist^7^a^s
4bg|Ashwood Bow|q|s|a|||q^935^Crown of the Earth^6^a^s
4bo|Elven Wand|q|s|a|||q^957^Bashal'Aran^8^a^s
4bq|Gardening Gloves|q|s|a|||q^919^Timberling Sprouts^4^a^s
4bs|Living Cowl|w|||||w^0^0^k
4bt|Steadfast Cinch|q|s|a|||q^994^Escape Through Force^17^a^s
4bu|Gustweald Cloak|q|s|a|10638||q^947^Cave Mushrooms^12^a^s
4bv|Tear of Grief|q|s|a|||q^963^For Love Eternal^11^a^s
4bw|Ivy Cuffs|q|s|a|||q^958^Tools of the Highborne^9^a^s
4bx|Staff of the Purifier|q|s|a|||q^973^The Tower of Althalaxx^19^a^s
4by|Seraph's Strike|q||a|||q^981^The Tower of Althalaxx^26^a^k
4bz|Woodsman Sword|q|s|a|||q^951^Mathystra Relics^15^a^s
4c0|Gutwrencher|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
4c1|Vagabond Leggings|q|s|a|||q^957^Bashal'Aran^8^a^s
4c2|Scout's Cloak|q|s|a|||q^938^Mist^7^a^s
4c6|Clergy Ring|q|s|a|||q^973^The Tower of Althalaxx^19^a^s
4c8|Circlet of the Order|w|||||w^0^0^k
4ca|Skullchipper|q|s|a|||q^943^The Absent Minded Prospector^19^a^s
4cb|Relic Blade|q|s|a|||q^943^The Absent Minded Prospector^19^a^s
4cd|Hammerfist Gloves|q|s|a|||q^741^The Absent Minded Prospector^15^a^s
4ce|Windfelt Gloves|q|s|a|||q^741^The Absent Minded Prospector^15^a^s
4ff|Barbaric Harness|c|s||||c^Leatherworking^185^6661^f
4fk|Pale Skinner|w|||||w^0^0^k
4fp|Scythe Axe|Rw|s||||R^2090^Ma'ruk Wyrmscale^0^s
4fq|Warchief's Girdle|w|s||||w^0^0^k
4fr|Webwing Cloak|Rw|s||||R^4015^Pridewing Patriarch^0^s
4fs|Wyvern Tailspike|Rw|sr||||R^4015^Pridewing Patriarch^0^s
4ft|Ruffled Chaplet|w|||||w^0^0^k
4fu|Wolfpack Medallion|w|||||w^0^0^k
4fw|Sliverblade|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
4fx|Hardwood Cudgel|q|s|a|||q^951^Mathystra Relics^15^a^s
4g1|Anvilmar Sledge|q|s|a|||q^182^The Troll Cave^1^a^s
4g6|Lesser Wizard's Robe|c|||||c^Tailoring^130^6690^f
4g7|Violet Robes|w|s||||m^1397^Frostmane Seer^3.89^s
4ga|Robes of Arcana|c|||||c^Tailoring^125^6692^f
4gg|Elder's Cane|q|s|h|||q^757^Rite of Strength^1^h^s
4gh|Brave's Axe|q|s|h|||q^757^Rite of Strength^1^h^s
4gj|Forsaken Bastard Sword|q|s|h|||q^381^The Scarlet Crusade^2^h^s
4gk|Murloc Scale Belt|c|s||||c^Leatherworking^65^6702^f
4gl|Murloc Scale Breastplate|c|s||||c^Leatherworking^70^6703^f
4gm|Thick Murloc Armor|c|||||c^Leatherworking^145^6704^f
4gn|Murloc Scale Bracers|c|||||c^Leatherworking^165^6705^f
4hg|Robes of Antiquity|q|s|a|||q^1009^Ruuzel^20^a^s
4hh|Emil's Brand|q|s|a|||q^1012^Insane Druids^27^a^s
4hi|Snapbrook Armor|q|s|a|||q^1035^Fallen Sky Lake^25^a^s
4hj|Glacial Stone|q||a|||q^1046^Raene's Cleansing^25^a^k
4hl|Lunaris Bow|q|s|a|||q^1044^Answered Questions^25^a^s
4hm|Moonbeam Wand|q|s|a|||q^1044^Answered Questions^25^a^s
4hn|Sunblaze Coif|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
4ho|Faerie Mantle|q|s|a|||q^1031^The Branch of Cenarius^27^a^s
4kw|Animal Skin Belt|q|s|h|||q^768^Gathering Leather^4^h^s
4kz|Sewing Gloves|q|s|h|||q^375^The Chill of Death^7^h^s
4l0|Bone Buckler|q|s|h|||q^411^The Prodigal Lich Returns^7^h^s
4l1|Brass Scale Pants|q|s|h|||q^398^Wanted: Maggot Eye^6^h^s
4l3|Rift Bracers|dw|s||||d^33^Fenrus the Devourer^11.11^0^s~m^4627^Arugal's Voidwalker^3.39^s
4l4|Greaves of the People's Militia|q|s|a|||q^153^Red Leather Bandanas^10^a^s
4lg|Blacksmith Hammer|dvw|s||||V^9179^18^^s~d^90^Tink Sprocketwhistle^0.02^0^k
4lh|Handstitched Leather Vest|c|s||||c^Leatherworking^1^7126^f
4li|Fine Leather Pants|c|s||||c^Leatherworking^80^7133^f
4ll|Dark Leather Pants|c|s||||c^Leatherworking^115^7135^f
4lm|Guardian Pants|c|s||||c^Leatherworking^155^7147^f
4ln|Barbaric Leggings|c|s||||c^Leatherworking^145^7149^f
4lo|Barbaric Shoulders|c|s||||c^Leatherworking^170^7151^f
4lp|Guardian Cloak|c|||||c^Leatherworking^160^7153^f
4lq|Guardian Gloves|c|s||||c^Leatherworking^185^7156^f
4lr|Girdle of Nobility|w|s||||w^0^0^k
4lt|Regent's Cloak|w|||||w^0^0^k
4lu|Serpent Gloves|d|s||||d^43^Lord Serpentis^28.57^0^s
4lv|Feathered Cape|u|||||
4lz|Ruffian Belt|w|||||w^0^0^k
4ns|Golden Scale Bracers|c|||||c^Blacksmithing^185^7223^f
4oa|Blackened Leather Belt|q|s|a|||q^457^The Balance of Nature^1^a^s
4ob|Nomadic Vest|q||h|4907||q^780^The Battleboars^1^h^s
4oc|Flax Bracers|q||h|11187||q^376^The Damned^2^h^s
4od|Graystone Bracers|q|s|a|||q^919^Timberling Sprouts^4^a^s
4oe|Heavy Cord Bracers|q||h|1183||q^786^Thwarting Kolkar Aggression^5^h^s
4of|Cold Steel Gauntlets|q|s|h|||q^358^Graverobbers^4^h^s
4om|Wolfskin Bracers|q|s|a|4908||q^33^Wolves Across the Border^1^a^s
4os|Tapered Pants|q|s|a|||q^6^Bounty on Garrick Padfoot^2^a^s
4ou|Pikeman Shield|q|s|a|4911||q^54^Report to Goldshire^1^a^s
4p0|Stormwind Guard Leggings|q|s|a|||q^176^Wanted:  "Hogger"^6^a^s
4p1|Footman Tunic|q|s|a|||q^176^Wanted:  "Hogger"^6^a^s
4p3|Chausses of Westfall|Q|s|a|||q^166^The Defias Brotherhood^17^a^s
4p8|Black Whelp Boots|q|s|a|||q^122^Underbelly Scales^14^a^s
4p9|Orc Crusher|q|s|a|||q^19^Tharil'zun^20^a^s
4pa|Piercing Axe|Q|s|a|||q^214^Red Silk Bandanas^14^a^s
4pb|Wandering Boots|q|s|a|||q^346^Return to Kristoff^20^a^s
4qr|Ratty Old Belt|Rw|s||||R^79^Narg the Taskmaster^0^s
4qs|Web-covered Boots|R|s||||R^471^Mother Fang^90^s
4rf|Wolf Handler Gloves|q|s|a|10636||q^179^Dwarven Outfitters^1^a^s
4rh|Snow Boots|q|s|a|3274||q^170^A New Threat^1^a^s
4rk|Dwarven Kite Shield|q|s|a|||q^218^The Stolen Journal^1^a^s
4rl|Ironwrought Bracers|q|s|a|||q^312^Tundra MacGrann's Stolen Stash^7^a^s
4rn|Privateer's Cape|w|||||w^0^0^k
4ro|Slarkskin|w|||||w^0^0^k
4rt|Bear Shawl|q|s|a|11850||q^170^A New Threat^1^a^s
4ru|Trogg Slicer|q|s|a|||q^297^Gathering Idols^13^a^s
4rv|Dwarven Defender|q|s|a|||q^217^In Defense of the King's Lands^12^a^s
4rw|Mud Stompers|q|s|a|||q^309^Protecting the Shipment^10^a^s
4rx|Durable Chain Shoulders|q|s|a|||q^256^WANTED: Chok'sul^17^a^s
4rz|Kimbra Boots|q|s|a|||q^256^WANTED: Chok'sul^17^a^s
4s2|Barreling Reaper|q|s|a|||q^474^Defeat Nek'rosh^27^a^s
4s3|Wax-polished Armor|w|||||w^0^0^k
4s5|Loch Croc Hide Vest|w|||||w^0^0^k
4s6|Jurassic Wristguards|w|||||w^0^0^k
4s7|Black Widow Band|w|U||||w^0^0^k
4s8|Garneg's War Belt|w|s||||w^0^0^k
4s9|Lithe Boots|w|||||w^0^0^k
4sa|Fingerless Gloves|w|||||w^0^0^k
4sb|Thuggish Shield|w|||||w^0^0^k
4sc|Tribal Worg Helm|w|||||w^0^0^k
4sd|Burrowing Shovel|w|||||w^0^0^k
4se|Rock Chipper|R|||||R^1424^Master Digger^75^k
4sm|Heavy Copper Maul|c|s||||c^Blacksmithing^65^7408^f
4sn|Balanced Fighting Stick|q|s|a|||q^176^Wanted:  "Hogger"^6^a^s
4ss|Meteor Shard|d|s||||d^33^Archmage Arugal^44.44^0^s
4sv|Crest of Darkshire|q|s|a|||q^253^Bride of the Embalmer^25^a^s
4sy|Bloody Apron|d|s||||d^33^Razorclaw the Butcher^22.22^0^s
4ta|Brown Linen Robe|c|s||||c^Tailoring^30^7623^f
4tb|Red Linen Vest|c|||||c^Tailoring^35^7629^f
4tc|Blue Linen Vest|c|||||c^Tailoring^35^7630^f
4td|White Linen Robe|c|s||||c^Tailoring^30^7624^f
4te|Blue Linen Robe|c|s||||c^Tailoring^45^7633^f
4tf|Green Woolen Robe|c|||||c^Tailoring^90^7636^f
4u2|Disciple's Vest|w|sr||||m^504^Defias Trapper^0^s~m^454^Young Goretusk^0^s
4u3|Disciple's Pants|w|sr||||m^126^Murloc Coastrunner^0^s~m^1162^Stonesplinter Scout^0^s
4u4|Pioneer Tunic|dwx|sr||||d^3065^Plunder^10^0^s~m^95^Defias Smuggler^0^s
4u5|Pioneer Trousers|wx|sr||||m^263390^NPC 263390^0^s~m^126^Murloc Coastrunner^0^s
4ui|Sacred Burial Trousers|q|s|h|||q^550^Battle of Hillsbrad^27^h^s
4ve|Wolfmaster Cape|d|s||||d^33^Wolf Master Nandos^44.44^0^s
4vi|Odo's Ley Staff|d|s||||d^33^Odo the Blindwatcher^33.33^0^s
4vj|Girdle of the Blindwatcher|d|s||||d^33^Odo the Blindwatcher^11.11^0^s
4vk|Commander's Crest|d|s||||d^33^Commander Springvale^11.11^0^s
4vl|Silverlaine's Family Seal|d|s||||d^33^Baron Silverlaine^22.22^0^s
4vn|Baron's Scepter|d|s||||d^33^Baron Silverlaine^55.56^0^s
4vo|Robes of Arugal|d|s||||d^33^Archmage Arugal^55.56^0^s
4vr|The Pacifier|w|||||w^0^0^k
4vv|Howling Blade|w|U||||w^0^0^k
4vw|Black Pearl Ring|w|U||||w^0^0^k
4vx|Spikelash Dagger|w|||||w^0^0^k
4vz|Grizzled Boots|Q|s|h|||q^1013^The Book of Ur^21^h^s
4w0|Infantry Tunic|dwx|sr||||d^3065^^0^0^s~m^118^Prowler^0^s
4w1|Infantry Leggings|w|sr||||m^36^Harvest Golem^0^s~m^500^Riverpaw Scout^0^s
4w4|Fenrus' Hide|d|s||||d^33^Fenrus the Devourer^44.44^0^s
4w5|Eerie Stable Lantern|w|s||||m^3864^Fel Steed^8.24^s
4we|Rough Bronze Boots|c|s||||c^Blacksmithing^95^7817^f
4x6|Seer's Cape|dw|s||||d^2999^Bjork^10^0^s~d^36^^0^0^s
4x7|Inscribed Leather Belt|Rdw|s||||d^36^Rhahk'Zor^5.26^0^s~m^598^Defias Miner^0^s
4x8|Inscribed Buckler|dw|s||||d^2999^Bjork^10^0^s~m^623^Skeletal Miner^0^s
4x9|Bright Cloak|dwx|s||||d^33^^0^0^s~m^1706^Defias Prisoner^0^s
4xa|Forest Leather Belt|dwx|s||||d^33^Archmage Arugal^11.11^0^s~m^1708^Defias Inmate^0^s
4xb|Forest Buckler|dwx|s||||m^1708^Defias Inmate^0^s~m^3859^Shadowfang Ragetooth^0^s
4xe|Glimmering Mail Legguards|dwx|s||||m^2248^Cave Yeti^0^s~d^34^Kam Deepfury^0.01^0^k
4xf|Glimmering Mail Bracers|dwx|s||||m^1053^Dark Iron Tunneler^0^s~m^6222^Leprous Technician^0^s
4xg|Glimmering Mail Pauldrons|dwx|s||||m^269134^NPC 269134^0^s~d^34^Kam Deepfury^0.01^0^k
4xh|Glimmering Mail Coif|Rdwx|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
4xk|Belt of Arugal|d|s||||d^33^Archmage Arugal^0^0^s
4xl|Silver-thread Gloves|dwx|s||||d^2998^^0^0^s~d^90^^0^0^s
4xm|Silver-thread Boots|dwx|s||||d^2998^^0^0^s~d^90^^0^0^s
4xn|Silver-thread Amice|dwx|s||||m^206^Nightbane Vile Fang^0^s~m^2335^Magistrate Burnside^0^s
4xo|Emblazoned Chestpiece|Rdwx|s||||d^189^Interrogator Vishas^9.09^0^s~m^7079^Viscous Fallout^0^s
4xp|Emblazoned Gloves|dwx|s||||m^260800^NPC 260800^0^s~d^34^Dextren Ward^0.01^0^k
4xq|Emblazoned Belt|dwx|s||||m^271351^Dragonmaw Reclaimer^0^s~m^6230^Peacekeeper Security Suit^0^s
4xr|Emblazoned Shoulders|dwx|s||||m^2248^Cave Yeti^0^s~m^2271^Dalaran Shield Guard^0^s
4xs|Glimmering Shield|Rdwx|s||||m^2554^Witherbark Axe Thrower^0^s~m^6234^Mechanized Guardian^0^s
4xu|Mail Combat Leggings|dwx|s||||m^691^Lesser Water Elemental^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
4xv|Mail Combat Armguards|Rdwx|s||||m^2345^Dun Garok Rifleman^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
4xw|Mail Combat Spaulders|dwx|s||||d^90^Mekgineer Thermaplugg^14.29^0^s~m^701^Bloodscalp Mystic^0^s
4xx|Nightsky Trousers|dwx|s||||m^686^Lashtail Raptor^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
4xy|Nightsky Boots|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
4xz|Nightsky Wristbands|Rdwx|s||||d^2959^Unstable Sentinel^14.29^0^s~m^685^Stranglethorn Raptor^0^s
4y0|Insignia Gloves|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
4y1|Insignia Belt|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
4y2|Insignia Bracers|Rdx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
4y3|Chief Brigadier Armor|wx|s||||o^Ancient Treasure^1.3^k~o^Captain's Chest^0.8^k
4y4|Chief Brigadier Boots|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
4y5|Chief Brigadier Bracers|dwx|s||||m^258818^NPC 258818^0^s~m^691^Lesser Water Elemental^0^s
4y6|Seal of Sylvanas|Q|s|h|||q^1014^Arugal Must Die^22^h^s
4y8|Aurora Boots|wx|||||x^4634^Iron Lockbox^k~x^4636^Strong Iron Lockbox^k
4y9|Aurora Cloak|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
4ya|Aurora Sash|dwx|s||||m^258792^NPC 258792^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
4yb|Glyphed Mitts|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
4yc|Glyphed Boots|wx|s||||m^2588^Syndicate Prowler^0^s~m^258799^NPC 258799^0^s
4yd|Glyphed Belt|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
4ye|Glyphed Helm|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
4yf|Blackforge Greaves|wx|||||x^4637^Steel Lockbox^k~w^40^47^k
4yg|Blackforge Cape|wx|s||||m^254560^Twilight Shadowmancer^0^s
4yh|Blackforge Girdle|wx|||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
4yi|Blackforge Bracers|wx|s||||o^Ancient Treasure^0.9^k~x^4636^Strong Iron Lockbox^k
4yj|Mistscape Robe|wx|||||x^4637^Steel Lockbox^k~x^4638^Reinforced Steel Lockbox^k
4yk|Mistscape Gloves|wx|||||o^Ancient Treasure^2.1^k~x^4637^Steel Lockbox^k
4yl|Mistscape Wizard Hat|wx|||||o^Ancient Treasure^1.5^k~x^4637^Steel Lockbox^k
4ym|Imperial Leather Breastplate|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10479^Kovic's Trading Satchel^k
4yn|Imperial Leather Boots|wx|||||o^Ancient Treasure^1.2^k~x^4637^Steel Lockbox^k
4yo|Imperial Cloak|wx|s||||o^Ancient Treasure^0.9^k~x^4637^Steel Lockbox^k
4yp|Imperial Leather Helm|wx|s||||m^258687^NPC 258687^0^s
4yw|Brainlash|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
4z3|Worn Turtle Shell Shield|d|s||||d^43^Kresh^22.22^0^s
4z4|Tail Spike|d|s||||d^43^Skum^50^0^s
4z5|Glowing Lizardscale Cloak|d|s||||d^43^Skum^37.5^0^s
4zf|Savage Trodders|d|s||||d^43^Lord Serpentis^42.86^0^s
4zg|Cobrahn's Grasp|d|s||||d^43^Lord Cobrahn^22.22^0^s
4zh|Slime-encrusted Pads|d|s||||d^43^Mutanus the Devourer^57.14^0^s
4zj|Deep Fathom Ring|d|s||||d^43^Mutanus the Devourer^28.57^0^s
4zl|Robe of the Moccasin|d|s||||d^43^Lord Cobrahn^33.33^0^s
4zm|Deviate Scale Cloak|c|s||||c^Leatherworking^65^7953^f
4zn|Deviate Scale Gloves|c|||||c^Leatherworking^80^7954^f
4zo|Deviate Scale Belt|c|s||||c^Leatherworking^90^7955^f
4zp|Venomstrike|d|s||||d^43^Lord Serpentis^28.57^0^s
4zs|Stinging Viper|d|s||||d^43^Lord Pythas^22.22^0^s
4zt|Armor of the Fang|d|s||||d^43^Lord Pythas^55.56^0^s
4zx|Grassland Sash|q|s|h|||q^899^Consumed by Hatred^15^h^s
500|Slick Deviate Leggings|Q|s||||q^1486^Deviate Hides^13^^s
501|Dagmire Gauntlets|Q|s||||q^1487^Deviate Eradication^16^^s
502|Firewalker Boots|q|s|h|||q^501^Elixir of Pain^21^h^s
50m|Violet Scale Armor|q|s|h|||q^868^Egg Hunt^17^h^s
50n|Harlequin Robes|q|s|h|||q^868^Egg Hunt^17^h^s
50o|Wingblade|Q|s|h|||q^914^Leaders of the Fang^17^h^s
50p|Crescent Staff|Q|s|h|||q^914^Leaders of the Fang^17^h^s
50q|Infantry Boots|w|s||||m^515^Murloc Raider^0^s
50r|Infantry Bracers|w|s||||m^95^Defias Smuggler^0^s~m^199^Young Fleshripper^0^s
50t|Infantry Belt|w|s||||m^118^Prowler^0^s~m^36^Harvest Golem^0^s
50u|Infantry Gauntlets|w|s||||m^1769^Moonrage Whitescalp^0^s~m^478^Riverpaw Outrunner^0^s
50v|Journeyman's Robe|w|s||||m^95^Defias Smuggler^0^s~m^1529^Bleeding Horror^0^s
50x|Disciple's Sash|w|s||||m^474^Defias Rogue Wizard^0^s~m^1172^Tunnel Rat Vermin^0^s
50y|Disciple's Cloak|w|s||||m^1117^Rockjaw Bonesnapper^0^s~m^474^Defias Rogue Wizard^0^s
50z|Disciple's Gloves|w|s||||m^199^Young Fleshripper^0^s~m^480^Rusty Harvest Golem^0^s
511|Pioneer Belt|w|s||||m^478^Riverpaw Outrunner^0^s~m^1190^Mountain Boar^0^s
512|Pioneer Boots|w|s||||m^448^Hogger^0^s~m^1116^Rockjaw Ambusher^0^s
514|Pioneer Cloak|Rw|s||||m^97^Riverpaw Runt^0^s~m^118^Prowler^0^s
515|Pioneer Gloves|w|s||||m^36^Harvest Golem^0^s~m^95^Defias Smuggler^0^s
517|Buckled Harness|v|s|h|||V^3359^1422^h^s
518|Studded Leather Harness|v|s|h|||V^3359^2870^h^s
519|Grunt's Harness|v|s|h|||V^3359^5167^h^s
51a|Battle Harness|v|s|h|||V^3359^12487^h^s
51b|Ancestral Robe|w|s||||m^3266^Razormane Defender^0^s~m^11321^Molten Elemental^0^s
51c|Spellbinder Robe|dw|s||||m^127^Murloc Tidehunter^0^s~m^634^Defias Overseer^0^s
51f|Barbaric Cloth Robe|dw|s||||m^3258^Bristleback Hunter^0^s~m^3261^Bristleback Thornweaver^0^s
51k|Willow Vest|Rdwx|sr||||d^36^Gilnid^9.52^0^s~m^446^Redridge Basher^0^s
51l|Willow Boots|dwx|sr||||d^2999^Rath'mael^10^0^s~m^124^Riverpaw Brute^0^s
51m|Willow Robe|dwx|sr||||m^1955^Lake Creeper^0^s~d^36^Rhahk'Zor^0.07^0^k
51n|Willow Belt|Rdwx|sr||||d^3065^^0^0^s~m^712^Redridge Thrasher^0^s
51o|Willow Pants|dwx|sr||||d^36^Captain Greenskin^9.52^0^s~m^442^Tarantula^0^s
51p|Willow Gloves|dwx|sr||||d^2999^The Abandoned^10^0^s~d^3065^Durgen Dirgehammer^10^0^s
51q|Willow Cape|dwx|sr||||d^2999^Rath'mael^20^0^s~d^2999^Witherfang^10^0^s
51r|Willow Bracers|dw|sr||||d^3065^Faldrim Anvilmar^10^0^s~d^3065^Infurnus^10^0^s
51t|Soldier's Armor|Rdw|sr||||d^33^Rethilgore^12.5^0^s~d^2999^Bjork^10^0^s
51u|Soldier's Leggings|dw|sr||||m^589^Defias Pillager^0^s~m^114^Harvest Watcher^0^s
51v|Soldier's Gauntlets|Rdw|sr||||d^3065^Durgen Dirgehammer^10^0^s~d^36^^0^0^s
51w|Soldier's Girdle|dw|sr||||d^36^Captain Greenskin^9.52^0^s~m^114^Harvest Watcher^0^s
51x|Soldier's Cloak|w|s||||m^1175^Tunnel Rat Digger^0^s~m^250654^NPC 250654^0^s
51y|Soldier's Wristguards|dw|sr||||d^3065^Plunder^10^0^s~m^712^Redridge Thrasher^0^s
51z|Soldier's Boots|dw|sr||||d^2999^Viktor the Vile^10^0^s~m^712^Redridge Thrasher^0^s
520|Bard's Tunic|Rdw|sr||||d^33^Wolf Master Nandos^11.11^0^s~m^485^Blackrock Outrunner^0^s
521|Bard's Trousers|dw|sr||||d^3065^Faldrim Anvilmar^10^0^s~d^36^^0^0^s
522|Bard's Gloves|dw|sr||||d^3065^Faldrim Anvilmar^10^0^s~m^422^Murloc Flesheater^0^s
523|Bard's Cloak|w|s||||m^263396^NPC 263396^0^s~m^114^Harvest Watcher^0^s
524|Bard's Bracers|dw|sr||||m^263438^NPC 263438^0^s~m^250626^NPC 250626^0^s
525|Bard's Boots|dw|sr||||d^36^Rhahk'Zor^5.26^0^s~m^114^Harvest Watcher^0^s
526|Bard's Belt|dw|sr||||d^2999^^0^0^s~m^423^Redridge Mongrel^0^s
527|Bard's Buckler|dw|sr||||m^122^Defias Highwayman^0^s~m^1797^Giant Grizzled Bear^0^s
528|Soldier's Shield|Rdw|sr||||m^598^Defias Miner^0^s~m^624^Undead Excavator^0^s
529|Seer's Padded Armor|dw|s||||d^36^^0^0^s~m^422^Murloc Flesheater^0^s
52a|Shimmering Boots|Rdwx|sr||||d^36^Gilnid^9.52^0^s~d^34^^0^0^s
52b|Shimmering Bracers|Rdwx|sr||||d^36^Captain Greenskin^9.52^0^s~d^33^^0^0^s
52c|Shimmering Cloak|dwx|sr||||d^36^Edwin VanCleef^4.76^0^s~m^203^Skeletal Mage^0^s
52d|Shimmering Gloves|dwx|sr||||m^3654^Mutanus the Devourer^0^s~m^436^Blackrock Shadowcaster^0^s
52e|Shimmering Amice|dwx|s||||d^43^Mutanus the Devourer^14.29^0^s~m^485^Blackrock Outrunner^0^s
52f|Shimmering Armor|dwx|sr||||m^203139^Son of Arugal^0^s~m^1707^Defias Captive^0^s
52g|Shimmering Trousers|Rdwx|sr||||d^34^Bazil Thredd^6.25^0^s~d^34^Targorr the Dread^5^0^s
52h|Shimmering Robe|dwx|sr||||m^1708^Defias Inmate^0^s~d^34^Targorr the Dread^0.01^0^k
52i|Shimmering Sash|dwx|sr||||d^34^Targorr the Dread^5^0^s~m^1706^Defias Prisoner^0^s
52j|Scouting Buckler|dwx|sr||||d^33^Commander Springvale^11.11^0^s~d^34^Bazil Thredd^6.25^0^s
52k|Defender Shield|dwx|sr||||d^36^Captain Greenskin^9.52^0^s~m^48^Skeletal Warrior^0^s
52l|Defender Boots|dwx|sr||||d^34^Dextren Ward^6.25^0^s~d^34^Kam Deepfury^5.88^0^s
52m|Defender Bracers|dwx|sr||||m^4463^Blackrock Summoner^0^s~d^36^Rhahk'Zor^0.07^0^k
52n|Defender Cloak|Rdwx|sr||||d^33^Baron Silverlaine^22.22^0^s~d^36^Mr. Smite^9.52^0^s
52o|Defender Girdle|dwx|sr||||d^36^Mr. Smite^4.76^0^s~m^1732^Defias Squallshaper^0^s
52p|Defender Gauntlets|dwx|sr||||m^432^Shadowhide Brute^0^s~m^1030^Black Slime^0^s
52q|Defender Leggings|dwx|sr||||d^43^Mutanus the Devourer^28.57^0^s~d^34^Dextren Ward^6.25^0^s
52r|Defender Spaulders|dwx|s||||m^1708^Defias Inmate^0^s~m^6221^Addled Leper^0^s
52s|Defender Tunic|dwx|sr||||m^485^Blackrock Outrunner^0^s~m^1007^Mosshide Gnoll^0^s
52t|Scouting Belt|dwx|sr||||d^36^^0^0^s~m^2244^Syndicate Shadow Mage^0^s
52v|Scouting Bracers|Rdwx|sr||||m^213^Starving Dire Wolf^0^s~m^3654^Mutanus the Devourer^0^s
52w|Scouting Tunic|dwx|sr||||d^34^Dextren Ward^6.25^0^s~d^34^Bazil Thredd^6.25^0^s
52x|Scouting Cloak|Rdwx|sr||||m^422^Murloc Flesheater^0^s~m^1731^Goblin Craftsman^0^s
52y|Scouting Gloves|dwx|sr||||m^657^Defias Pirate^0^s~m^3654^Mutanus the Devourer^0^s
52z|Scouting Trousers|dwx|sr||||d^34^^0^0^s~m^202^Skeletal Horror^0^s
530|Scouting Spaulders|Rdwx|s||||m^1707^Defias Captive^0^s~R^1948^Snarlmane^0^s
532|Battleforge Boots|dwx|sr||||d^90^^0^0^s~m^6218^Irradiated Slime^0^s
533|Battleforge Wristguards|dwx|sr||||d^2998^^0^0^s~m^1707^Defias Captive^0^s
534|Battleforge Armor|dwx|sr||||m^1270^Fetid Corpse^0^s~m^7603^Leprous Assistant^0^s
535|Battleforge Cloak|Rdwx|sr||||d^2959^^0^0^s~m^1708^Defias Inmate^0^s
536|Battleforge Girdle|dwx|sr||||d^2998^^0^0^s
537|Battleforge Gauntlets|dwx|sr||||m^260801^NPC 260801^0^s~m^2344^Dun Garok Mountaineer^0^s
538|Battleforge Legguards|dwx|sr||||m^2356^Elder Gray Bear^0^s~m^7603^Leprous Assistant^0^s
539|Battleforge Shoulderguards|dwx|sr||||d^34^Hamhock^11.76^0^s~d^34^Kam Deepfury^5.88^0^s
53a|Dervish Buckler|dwx|sr||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
53b|Battleforge Shield|dwx|sr||||m^4306^Scarlet Torturer^0^s~d^34^Dextren Ward^0.01^0^k
53c|Dervish Belt|Rdwx|sr||||m^1708^Defias Inmate^0^s~R^4015^Pridewing Patriarch^0^s
53d|Dervish Boots|dwx|sr||||d^47^Roogug^50^0^s~m^2344^Dun Garok Mountaineer^0^s
53e|Dervish Bracers|Rdwx|sr||||m^1057^Dragonmaw Bonewarder^0^s~R^4015^Pridewing Patriarch^0^s
53f|Dervish Tunic|dwx|sr||||m^7603^Leprous Assistant^0^s~m^785^Skeletal Warder^0^s
53h|Dervish Gloves|dwx|sr||||m^205^Nightbane Dark Runner^0^s~m^260808^NPC 260808^0^s
53j|Dervish Leggings|dwx|sr||||m^7603^Leprous Assistant^0^s~d^34^Kam Deepfury^0.01^0^k
53k|Bright Armor|dwx|s||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
53n|Sage's Sash|dwx|sr||||m^1051^Dark Iron Dwarf^0^s~d^34^Dextren Ward^0.01^0^k
53o|Sage's Boots|dwx|sr||||m^1023^Mottled Razormaw^0^s~m^2346^Dun Garok Priest^0^s
53p|Sage's Bracers|dwx|sr||||d^90^^0^0^s~m^6233^Mechanized Sentry^0^s
53r|Sage's Gloves|dwx|sr||||d^2959^Atrexis the Grave Knight^14.29^0^s~m^205^Nightbane Dark Runner^0^s
53s|Sage's Pants|Rdx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
53t|Sage's Mantle|dwx|sr||||d^189^Interrogator Vishas^9.09^0^s~d^2959^^0^0^s
53y|Sword of Zeal|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
543|Mutant Scale Breastplate|d|s||||d^43^Mutanus the Devourer^14.29^0^s
544|Raven's Claws|w|||||w^0^0^k
545|Sporid Cape|d|s||||d^43^Verdan the Everliving^14.29^0^s
546|Seedcloud Buckler|d|s||||d^43^Verdan the Everliving^0^0^s
547|Living Root|d|s||||d^43^Verdan the Everliving^85.71^0^s
548|Feyscale Cloak|d|s||||d^43^^0^0^s
549|Butcher's Slicer|d|s||||d^33^Razorclaw the Butcher^22.22^0^s
54h|Haunting Blade|d|s||||d^33^^0^0^s
54i|Phantom Armor|d|s||||d^33^Odo the Blindwatcher^33.33^0^s
54z|Scarab Trousers|q|s|a|||q^995^Escape Through Stealth^15^a^s
550|Julie's Dagger|x|||||x^5758^Mithril Lockbox^k
554|Voodoo Mantle|q|s|h|||q^1058^Jin'Zil's Forest Magic^21^h^s
555|Hexed Bracers|q|s|h|||q^1058^Jin'Zil's Forest Magic^21^h^s
556|Dredge Boots|q|s||||q^1092^Gerenzo's Orders^17^^s
557|Engineer's Cloak|q|s||||q^1096^Gerenzo Wrenchwhistle^22^^s
558|Draftsman Boots|q|s||||q^1096^Gerenzo Wrenchwhistle^22^^s
559|Sacred Band|q|s|h|||q^1089^The Den^24^h^s
55a|Panther Armor|q|s|h|||q^1089^The Den^24^h^s
55b|Juggernaut Leggings|q|s|h|||q^1089^The Den^24^h^s
55f|Tempered Bracers|q||a|||q^1059^Reclaiming the Charred Vale^22^a^k
55g|Constable Buckler|q||a|||q^1059^Reclaiming the Charred Vale^22^a^k
55h|Spellcrafter Wand|q|s|a|||q^1078^Retrieval for Mauren^21^a^s
55i|Band of Elven Grace|q||a|||q^1081^Reception from Tyrande^23^a^k
55j|Armor Piercer|d|s||||d^47^Overlord Ramtusk^60^0^s
55l|Thornspike|d|s||||d^47^Aggem Thorncurse^80^0^s
55m|Death Speaker Robes|d|s||||d^47^Death Speaker Jargba^20^0^s
55p|Death Speaker Mantle|d|s||||d^47^Death Speaker Jargba^40^0^s
55q|Tusken Helm|d|s||||d^47^Overlord Ramtusk^40^0^s
55r|Corpsemaker|d|s||||d^47^Overlord Ramtusk^20^0^s
55s|Whisperwind Headdress|d|s||||d^47^^0^0^s
55t|Wind Spirit Staff|d|s||||d^47^^50^0^k
55u|Ferine Leggings|d|s||||d^47^Agathelos the Raging^20^0^s
55v|Swinetusk Shank|d|s||||d^47^Agathelos the Raging^0^0^s
55w|Pronged Reaver|d|s||||d^47^Charlga Razorflank^20^0^s
55x|Agamaggan's Clutch|d|s||||d^47^Charlga Razorflank^0^0^s
55y|Heart of Agamaggan|d|s||||d^47^Charlga Razorflank^80^0^s
55z|Stygian Bone Amulet|d|s||||d^47^^33.33^0^k
560|Nightstalker Bow|d|s||||d^47^^0^0^s
561|Batwing Mantle|d|||||d^47^^33.33^0^k
56d|Moonglow Vest|c|||||c^Leatherworking^65^8322^f
56h|Ripped Pants|q||h|79||q^794^Burning Blade Medallion^1^h^s
56n|Windborne Belt|q|s|a|||q^1135^Highperch Venom^25^a^s
56o|Spirit Hunter Headdress|q|s|h|||q^1136^Frostmaw^32^h^s
56p|Chestplate of Kor|q|s|a|||q^976^Supplies to Auberdine^19^a^s
56q|Beastial Manacles|q|s|a|||q^1035^Fallen Sky Lake^25^a^s
56r|Medal of Courage|Qq|||||q^592^Saving Yenniku^41^h^k~q^1139^The Lost Tablets of Will^40^a^k
56t|Marbled Buckler|Q|s||||q^1101^The Crone of the Kraul^29^a^s~q^1102^A Vengeful Fate^29^h^s
56u|Razzeric's Customized Seatbelt|q|s||||q^1189^Safety First^36^^s
56v|Razzeric's Racing Grips|q|s||||q^1189^Safety First^36^^s
56x|Fizzle's Zippy Lighter|q|||||q^1137^News for Fizzle^33^^k
56y|Ironforge Chain|c|||||c^Blacksmithing^80^8366^f
575|Dryleaf Pants|q||h|||q^1184^Parts of the Swarm^30^h^k
576|Bleeding Crescent|q||h|||q^1184^Parts of the Swarm^30^h^k
577|Cliffrunner's Aim|q|s|h|||q^1197^The Sacred Flame^24^h^s
578|Azure Sash|q|s|h|||q^1197^The Sacred Flame^24^h^s
579|Orcish War Sword|q|s|h|||q^1153^A New Ore Sample^25^h^s
57a|Stonefist Girdle|Q|s||||q^1101^The Crone of the Kraul^29^a^s~q^1102^A Vengeful Fate^29^h^s
57b|Sustaining Ring|Q|s|a|||q^971^Knowledge in the Deeps^18^a^s
57c|Gloves of Kapelan|q||h|||q^1436^Alliance Relations^30^h^k
57d|Swiftrunner Cape|q||h|||q^1436^Alliance Relations^30^h^k
57e|Basalt Buckler|q||h|||q^1488^The Corrupter^35^h^k
57f|Enforcer Pauldrons|q||h|||q^1488^The Corrupter^35^h^k
57g|Monkey Ring|Q|s||||q^1144^Willix the Importer^25^^s
57h|Tiger Band|Q|s||||q^1144^Willix the Importer^25^^s
57i|Snake Hoop|Q|s||||q^1144^Willix the Importer^25^^s
57j|Mourning Shawl|Q|s|a|||q^1142^Mortality Wanes^25^a^s
57k|Lancer Boots|Q|s|a|||q^1142^Mortality Wanes^25^a^s
57p|Jaina's Signet Ring|q|s|a|||q^1267^The Missing Diplomat^33^a^s
585|Kolkar Marauder Chain|q|s||||q^96222^Khan Hratha^37^^s~q^1380^Khan Hratha^37^^s
586|Traitor's Finger|q|s||||q^96222^Khan Hratha^37^^s~q^1380^Khan Hratha^37^^s
58c|Lilac Sash|q|s|h|||q^1366^Centaur Bounty^30^h^s
58g|Braced Handguards|q|s|h|||q^1366^Centaur Bounty^30^h^s
58j|White Woolen Dress|c|s||||c^Tailoring^110^8467^f
58k|Kolkar Hunter's Belt|q|s||||q^96222^Khan Hratha^37^^s~q^1381^Khan Hratha^37^^s
58l|Ceremonial Centaur Blanket|q|s||||q^96222^Khan Hratha^37^^s~q^1381^Khan Hratha^37^^s
58n|Hellion Boots|q|s|a|||q^1457^The Karnitol Shipwreck^34^a^s
58o|Sanguine Pauldrons|q|s|a|||q^1457^The Karnitol Shipwreck^34^a^s
58p|Auric Bracers|q||a|||q^1467^Reagents for Reclaimers Inc.^35^a^k
58t|Eyepoker|q||h|||q^1273^Questioning Reethe^32^h^k
58u|Blasting Hackbut|q||h|||q^1273^Questioning Reethe^32^h^k
58x|Baroque Apron|q|s|a|||q^1258^... and Bugs^35^a^s
58y|Sword of Omen|Q|s|h|||q^1048^Into The Scarlet Monastery^37^h^s
58z|Prophetic Cane|Q|s|h|||q^1048^Into The Scarlet Monastery^37^h^s
590|Windstorm Hammer|q||h|||q^1394^Final Passage^31^h^k
592|Dancing Flame|q||h|||q^1394^Final Passage^31^h^k
59o|Visionary Buckler|q|||||q^1393^Galen's Escape^33^^k
59p|Sword of Serenity|Q|s|a|||q^1053^In the Name of the Light^35^a^s
59q|Bonebiter|Q|s|a|||q^1053^In the Name of the Light^35^a^s
59r|Black Menace|Q|s|a|||q^1053^In the Name of the Light^35^a^s
59s|Cloak of Blight|q||h|||q^1383^Nothing But The Truth^37^h^k
59u|Black Tuxedo|w|||||o^Brightly Colored Egg^0.6^k
5bm|Orb of Soran'ruk|Q|s||||q^1740^The Orb of Soran'ruk^20^^s
5bo|Enchanted Gold Bloodrobe|q|||||q^4786^The Completed Robe^33^^k
5bp|Glowing Thresher Cape|d|s||||d^48^Old Serra'kis^62.5^0^s
5bq|Bands of Serra'kis|d|s||||d^48^Old Serra'kis^12.5^0^s
5br|Gaze Dreamer Pants|d|s||||d^48^Twilight Lord Kelris^50^0^s
5bs|Bite of Serra'kis|d|s||||d^48^Old Serra'kis^25^0^s
5bt|Reef Axe|d|s||||d^48^Geilhast^16.67^0^s
5bu|Algae Fists|d|s||||d^48^Geilhast^33.33^0^s
5bw|Ghamoo-ra's Bind|d|s||||d^48^Ghamoo-ra^25^0^s
5bx|Strike of the Hydra|d|s||||d^48^Aku'mai^50^0^s
5by|Leech Pants|d|s||||d^48^Aku'mai^33.33^0^s
5bz|Moss Cinch|d|s||||d^48^Aku'mai^16.67^0^s
5d5|Verigan's Fist|q|s|a|||q^1806^The Test of Righteousness^20^a^s
5di|Elunite Axe|q|s|a|7115||q^1693^Weapons of Elunite^10^a^s
5dj|Elunite Sword|q|s|a|7118||q^1693^Weapons of Elunite^10^a^s
5dk|Elunite Hammer|q|s|a|7117||q^1693^Weapons of Elunite^10^a^s
5dl|Elunite Dagger|q|s|a|7116||q^1693^Weapons of Elunite^10^a^s
5dm|Furen's Favor|q|s|a|7120||q^1702^The Shieldsmith^20^a^s
5dn|Fire Hardened Coif|q||a|7130||q^1706^Grimand's Armor^25^a^k
5do|Fire Hardened Hauberk|q||a|7133||q^1782^Furen's Armor^23^a^k
5dp|Fire Hardened Leggings|q||a|7132||q^1711^Mathiel's Armor^25^a^k
5dq|Fire Hardened Gauntlets|q|s|a|7129||q^1709^Klockmort's Creation^25^a^s
5dr|Whirlwind Axe|q|||||q^1792^Whirlwind Weapon^35^^k
5ds|Whirlwind Warhammer|q|||||q^1792^Whirlwind Weapon^35^^k
5dt|Whirlwind Sword|q|||||q^1792^Whirlwind Weapon^35^^k
5du|Umbral Axe|q||a|7326||q^1682^Grey Iron Weapons^10^a^k
5dv|Haggard's Axe|q|s|a|||q^1667^Dead-tooth Jack^10^a^s
5dw|Haggard's Dagger|q|s|a|7327||q^1667^Dead-tooth Jack^10^a^s
5ee|Nimbus Boots|Q|s|a|||q^1199^Twilight Falls^20^a^s
5eg|Heartwood Girdle|Q|s|a|||q^1199^Twilight Falls^20^a^s
5eh|Gravestone Scepter|Q|s||||q^1200^Blackfathom Villainy^22^a^s~q^6561^Blackfathom Villainy^22^h^s
5ei|Arctic Buckler|Q|s||||q^1200^Blackfathom Villainy^22^a^s~q^6561^Blackfathom Villainy^22^h^s
5ej|Beetle Clasps|Q|s|a|||q^1275^Researching the Corruption^19^a^s
5ek|Prelacy Cape|Q|s|a|||q^1275^Researching the Corruption^19^a^s
5el|Skinning Knife|v|s||||V^12245^10^^s
5f6|Linen Belt|c|s||||c^Tailoring^10^8776^f
5f7|Boots of Darkness|c|||||c^Tailoring^135^8778^f
5fq|Azure Silk Pants|c|||||c^Tailoring^135^8758^f
5fr|Hands of Darkness|c|||||c^Tailoring^120^8780^f
5fs|Azure Silk Hood|c|s||||c^Tailoring^130^8760^f
5ft|Truefaith Gloves|c|||||c^Tailoring^125^8782^f
5fu|Silk Headband|c|s||||c^Tailoring^135^8762^f
5fx|Azure Silk Cloak|c|s||||c^Tailoring^140^8786^f
5fy|Robe of Power|c|||||c^Tailoring^175^8770^f
5fz|Crimson Silk Belt|c|||||c^Tailoring^160^8772^f
5g0|Crimson Silk Cloak|c|||||c^Tailoring^145^8789^f
5g1|Green Silken Shoulders|c|s||||c^Tailoring^165^8774^f
5g2|Crimson Silk Vest|c|||||c^Tailoring^170^8791^f
5g3|Crimson Silk Shoulders|c|||||c^Tailoring^155^8793^f
5g4|Azure Shoulders|c|||||c^Tailoring^155^8795^f
5g5|Earthen Silk Belt|c|||||c^Tailoring^160^8797^f
5g6|Crimson Silk Pantaloons|c|||||c^Tailoring^180^8799^f
5g8|Crimson Silk Gloves|c|||||c^Tailoring^190^8804^f
5g9|Green Silk Armor|c|||||c^Tailoring^130^8784^f
5h3|Bog Boots|w|s||||m^2029^Timberling Mire Beast^1.83^s
5he|Zodiac Gloves|q|s|a|||q^181^Look To The Stars^25^a^s
5hf|Belt of the Stars|q|s|a|||q^181^Look To The Stars^25^a^s
5hg|Infantry Shield|w|sr||||m^116^Defias Bandit^0^s~m^1172^Tunnel Rat Vermin^0^s
5hh|Pioneer Buckler|w|s||||m^97^Riverpaw Runt^0^s~m^118^Prowler^0^s
5hi|Silver-thread Armor|Rdwx|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
5hj|Nightsky Armor|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
5hn|Heirloom Axe|q||h|6966||q^1822^Heirloom Weapon^10^h^k
5ho|Heirloom Dagger|q||h|6969||q^1822^Heirloom Weapon^10^h^k
5hp|Heirloom Hammer|q||h|6968||q^1822^Heirloom Weapon^10^h^k
5hq|Heirloom Sword|q||h|6967||q^1822^Heirloom Weapon^10^h^k
5hs|Ruga's Bulwark|q||h|6970||q^1824^Trial at the Field of Giants^20^h^s
5i1|Brutal Gauntlets|q||h|6974||q^1843^Brutal Gauntlets^25^h^k
5i2|Brutal Helm|q||h|6971||q^1845^Brutal Helm^25^h^k
5i4|Brutal Legguards|q||h|6973||q^1847^Brutal Legguards^25^h^k
5i5|Brutal Hauberk|q||h|6972||q^1848^Brutal Hauberk^25^h^k
5j2|Copper Dagger|c|s||||c^Blacksmithing^30^8880^f
5kt|Explorer's Vest|q|s|a|||q^957^Bashal'Aran^8^a^s
5ku|Smite's Mighty Hammer|d|s||||d^36^Mr. Smite^23.81^0^s
5m4|Handstitched Leather Cloak|c|s||||c^Leatherworking^1^9058^f
5m5|Handstitched Leather Bracers|c|s||||c^Leatherworking^1^9059^f
5m8|Rugged Leather Pants|cw|||||c^Leatherworking^30^9064^f
5m9|Light Leather Bracers|c|s||||c^Leatherworking^70^9065^f
5ma|Light Leather Pants|c|s||||c^Leatherworking^95^9068^f
5mb|Black Whelp Cloak|c|s||||c^Leatherworking^75^9070^f
5md|Nimble Leather Gloves|c|s||||c^Leatherworking^120^9074^f
5mq|Blade of Cunning|q|sU||||q^1858^The Shattered Hand^10^h^s~q^1978^The Deathstalkers^10^h^s
5ni|Thun'grim's Axe|q||h|6978||q^1503^Forged Steel^10^h^s
5nj|Thun'grim's Dagger|q||h|6980||q^1503^Forged Steel^10^h^s
5nm|Infiltrator Buckler|Rdwx|sr||||d^189^^0^0^s~m^587^Bloodscalp Warrior^0^s
5nn|Phalanx Shield|dwx|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
5nq|Efflorescent Robe|q||a|||q^1081^Reception from Tyrande^23^a^k
5nr|Grizzly Tunic|q||a|||q^1081^Reception from Tyrande^23^a^k
5ns|Wildwood Chain|q||a|||q^1081^Reception from Tyrande^23^a^k
5o4|Fletcher's Gloves|c|||||c^Leatherworking^125^9145^f
5o6|Disciple's Bracers|w|s||||m^36^Harvest Golem^0^s~m^474^Defias Rogue Wizard^0^s
5o7|Disciple's Boots|w|s||||m^454^Young Goretusk^0^s~m^1534^Wailing Ancestor^0^s
5o8|Earthen Leather Shoulders|c|||||c^Leatherworking^110^9147^f
5oa|Elder's Boots|Rdwx|sr||||m^206^Nightbane Vile Fang^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5ob|Elder's Bracers|Rdwx|sr||||m^683^Young Panther^0^s~d^90^Grubbis^0.39^0^k
5od|Elder's Hat|dwx|sr||||d^90^Mekgineer Thermaplugg^14.29^0^s
5oe|Pilferer's Gloves|c|||||c^Leatherworking^115^9148^f
5of|Heavy Earthen Gloves|c|||||c^Leatherworking^120^9149^f
5om|Elder's Gloves|Rdwx|sr||||d^2959^^0^0^s~m^775^Kurzen's Agent^0^s
5on|Elder's Mantle|Rdwx|sr||||d^90^Mekgineer Thermaplugg^0^0^s~m^2563^Plains Creeper^0^s
5oq|Elder's Sash|Rdwx|sr||||d^90^^0^0^s~m^2408^Snapjaw^0^s
5ot|Dusky Leather Leggings|c|s||||c^Leatherworking^140^9195^f
5ou|Dusky Leather Armor|c|||||c^Leatherworking^170^9196^f
5ox|Frost Leather Cloak|c|||||c^Leatherworking^175^9198^f
5oy|Dusky Bracers|c|||||c^Leatherworking^180^9201^f
5p6|Green Whelp Bracers|c|||||c^Leatherworking^165^9202^f
5p7|Dusky Belt|c|||||c^Leatherworking^190^9206^f
5pa|Dusky Boots|c|||||c^Leatherworking^175^9207^f
5pb|Swift Boots|c|||||c^Leatherworking^175^9208^f
5pq|Infiltrator Cord|Rdwx|sr||||m^6223^Leprous Defender^0^s~m^6234^Mechanized Guardian^0^s
5ps|Infiltrator Shoulders|Rdx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
5pt|Infiltrator Boots|Rdwx|sr||||m^6212^Dark Iron Agent^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5pu|Infiltrator Bracers|Rdwx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
5pv|Infiltrator Cloak|Rdwx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
5pw|Infiltrator Gloves|Rdwx|sr||||d^90^^0^0^s~m^6212^Dark Iron Agent^0^s
5px|Infiltrator Cap|Rdx|sr||||d^90^Mekgineer Thermaplugg^0^0^s~R^1037^Dragonmaw Battlemaster^0.46^k
5pz|Dervish Spaulders|dwx|sr||||d^2959^Fel Ancient^14.29^0^s~d^90^^0^0^s
5q0|Phalanx Bracers|Rdwx|sr||||m^1418^Bluegill Raider^0^s~d^90^Grubbis^0.39^0^k
5q2|Phalanx Breastplate|dwx|sr||||m^689^Crystal Spine Basilisk^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5q4|Phalanx Headguard|Rdwx|sr||||d^90^Electrocutioner 6000^40^0^s~m^6225^Mechano-Tank^0^s
5q5|Phalanx Gauntlets|Rdwx|sr||||m^2407^Hulking Mountain Lion^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5q6|Phalanx Girdle|Rdwx|sr||||m^271346^Dragonmaw Infiltrator^0^s~d^90^Grubbis^0.39^0^k
5q8|Phalanx Spaulders|Rdx|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
5qg|Twilight Cowl|wx|sr||||m^2573^Drywhisker Surveyor^0^s
5qh|Twilight Gloves|dwx|sr||||m^4851^Stonevault Rockchewer^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5qp|Sentinel Cap|wx|sr||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
5qw|Sentinel Girdle|dwx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k
5r2|Knight's Breastplate|wx|sr||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
5r4|Knight's Headguard|wx|sr||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
5r6|Knight's Boots|Rdwx|sr||||R^2258^Stone Fury^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
5rd|Knight's Crest|wx|sr||||m^2253^Crushridge Brute^0^s
5ri|Regal Wizard Hat|wx|sr||||o^Ancient Treasure^1.2^k~x^4637^Steel Lockbox^k
5rr|Ranger Helm|wx|sr||||o^Ancient Treasure^1.7^k~x^4637^Steel Lockbox^k
5ry|Captain's Breastplate|wx|sr||||o^Ancient Treasure^0.9^k~o^Captain's Chest^0.8^k
5s7|Captain's Buckler|wx|r||||o^Ancient Treasure^0.7^k~x^4637^Steel Lockbox^k
5s8|Field Plate Shield|wx|r||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
5sl|Manaweave Robe|q|s|a|7510||q^1941^Manaweave Robe^15^a^s
5sm|Lesser Spellfire Robes|q||h|7509||q^1962^Spellfire Robes^15^h^s
5sn|Astral Knot Robe|q||a|7512||q^1942^Astral Knot Garment^26^a^k
5so|Nether-lace Robe|q||h|7511||q^1946^Nether-lace Garment^26^h^k
5sp|Ragefire Wand|q|||||q^1952^Mage's Wand^35^^k
5sq|Icefury Wand|q|||||q^1952^Mage's Wand^35^^k
5sr|Celestial Orb|q|||||q^1958^Celestial Power^35^^k
5td|Gothic Shield|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
5ts|Falcon's Hook|wx|||||o^Ancient Treasure^1.6^k~x^4637^Steel Lockbox^k
5tt|Band of the Unicorn|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
5tz|Runic Cane|w|||||w^0^0^k
5va|Polar Gauntlets|Q|s|a|||q^2040^Underground Assault^15^a^s
5vb|Sable Wand|Q|s|a|||q^2040^Underground Assault^15^a^s
5vc|Seer's Fine Stein|dw|s||||m^213^Starving Dire Wolf^0^s~m^3851^Shadowfang Whitescalp^0^s
5ve|Aurora Sphere|wx|||||o^Captain's Chest^0.8^k~x^4636^Strong Iron Lockbox^k
5vf|Mistscape Stave|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
5x5|Talvash's Enhancing Necklace|Q||a|7888||q^2361^Restoring the Necklace^39^a^k
5xe|Torturing Poker|d|s||||d^189^Interrogator Vishas^81.82^0^s
5xf|Bloody Brass Knuckles|d|s||||d^189^Interrogator Vishas^18.18^0^s
5xg|Bloodmage Mantle|d|s||||d^189^Bloodmage Thalnos^54.55^0^s
5xh|Orb of the Forgotten Seer|d|s||||d^189^Bloodmage Thalnos^45.45^0^s
5xi|Ironspine's Eye|R|||||R^6489^Ironspine^33.33^k
5xj|Ironspine's Fist|R|||||R^6489^Ironspine^33.33^k
5xk|Ironspine's Ribcage|Rd|s||||d^189^^0^0^s~R^6489^Ironspine^33.33^s
5xl|Morbid Dawn|R|||||R^6488^Fallen Champion^33.33^k
5xm|Ebon Vise|R|||||R^6488^Fallen Champion^33.33^k
5xn|Embalmed Shroud|Rd|s||||d^189^^0^0^s~R^6488^Fallen Champion^33.33^s
5y4|Necrotic Wand|R|s||||R^6490^Azshir the Sleepless^33.33^k
5y5|Blighted Leggings|Rd|s||||d^189^^0^0^s~R^6490^Azshir the Sleepless^33.33^s
5y6|Loksey's Training Stick|d|s||||d^189^Houndmaster Loksey^0^0^s
5y7|Robe of Doan|d|s||||d^189^Arcanist Doan^0^0^s
5y8|Mantle of Doan|d|s||||d^189^Arcanist Doan^25^0^k
5y9|Illusionary Rod|d|s||||d^189^Arcanist Doan^25^0^k
5ya|Hypnotic Blade|d|||||d^189^Arcanist Doan^25^0^k
5yd|Ravager|d|s||||d^189^Herod^0^0^s
5ye|Herod's Shoulder|d|s||||d^189^Herod^33.33^0^s
5yf|Raging Berserker's Helm|d|s||||d^189^Herod^66.67^0^s
5yg|Whitemane's Chapeau|d|||||d^189^High Inquisitor Whitemane^40^0^k
5yh|Hand of Righteousness|d|s||||d^189^High Inquisitor Whitemane^100^0^s
5yi|Triune Amulet|d|s||||d^189^High Inquisitor Whitemane^0^0^s
5yj|Mograine's Might|d|||||d^189^^22.5^0^k
5yk|Gauntlets of Divinity|d|||||d^189^^22.5^0^k
5ym|Aegis of the Scarlet Commander|d|||||d^189^^40^0^k
5yn|Watchman Pauldrons|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5yo|Beguiler Robes|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5yp|Chesterfall Musket|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5yq|Cobalt Crusher|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5yr|Ghostshard Talisman|R|||||R^6490^Azshir the Sleepless^33.33^k
5yw|Fight Club|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5yy|Evergreen Gloves|q|s|a|||q^2139^Tharnariun's Hope^13^a^s
5yz|Timberland Cape|q|s|a|||q^2139^Tharnariun's Hope^13^a^s
5z6|Explorers' League Commendation|Q|s|a|||q^1050^Mythology of the Titans^33^a^s
5z7|Vile Protector|Q|s|h|||q^1049^Compendium of the Fallen^33^h^s
5z9|Omega Orb|Q|s|h|||q^1049^Compendium of the Fallen^33^h^s
5za|Mantle of Woe|Q|s|h|||q^1051^Vorrel's Revenge^28^h^s
5zb|Vorrel's Boots|Q|s|h|||q^1051^Vorrel's Revenge^28^h^s
5zc|Dreamslayer|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zd|Bloodspiller|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5ze|Harbinger Boots|dw|s||||m^4308^Unfettered Spirit^0^s~d^189^Houndmaster Loksey^0.01^0^k
5zf|Flintrock Shoulders|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zg|Dog Training Gloves|d|s||||d^189^Houndmaster Loksey^0^0^s
5zh|Windweaver Staff|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zi|Ruthless Shiv|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zj|Archon Chestpiece|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zk|Warchief Kilt|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
5zl|Steelclaw Reaver|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
60a|Headsplitter|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
60b|Resplendent Guardian|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
634|Jarkal's Enhancing Necklace|Q||h|7673||q^2341^Necklace Recovery, Take 3^40^h^k
63t|Barbaric Iron Shoulders|c|||||c^Blacksmithing^135^9811^f
63u|Barbaric Iron Breastplate|c|||||c^Blacksmithing^135^9813^f
63v|Barbaric Iron Helm|c|||||c^Blacksmithing^150^9814^f
63w|Barbaric Iron Boots|c|||||c^Blacksmithing^155^9818^f
63x|Barbaric Iron Gloves|c|||||c^Blacksmithing^160^9820^f
63y|Heavy Mithril Shoulder|c|||||c^Blacksmithing^200^9926^f
641|Heavy Mithril Pants|c|||||c^Blacksmithing^185^9933^f
642|Steel Plate Helm|c|||||c^Blacksmithing^210^9935^f
644|Mithril Plate Bracers|c|||||c^Blacksmithing^190^9937^f
646|Ornate Mithril Pants|c|||||c^Blacksmithing^195^9945^f
648|Ornate Mithril Shoulders|c|||||c^Blacksmithing^200^9952^f
649|Orcish War Leggings|c|||||c^Blacksmithing^225^9957^f
64a|Heavy Mithril Breastplate|c|||||c^Blacksmithing^225^9959^f
64e|Heavy Mithril Helm|c|||||c^Blacksmithing^220^9970^f
64f|Ornate Mithril Breastplate|c|||||c^Blacksmithing^235^9972^f
64h|Ornate Mithril Helm|c|||||c^Blacksmithing^240^9980^f
64i|Truesilver Gauntlets|c|||||c^Blacksmithing^220^9954^f
64j|Truesilver Breastplate|c|||||c^Blacksmithing^240^9974^f
64l|Heavy Mithril Axe|c|||||c^Blacksmithing^210^9993^f
64m|Blue Glittering Axe|c|||||c^Blacksmithing^195^9995^f
64n|Wicked Mithril Blade|c|||||c^Blacksmithing^200^9997^f
64o|Dazzling Mithril Rapier|c|||||c^Blacksmithing^215^10005^f
64p|Big Black Mace|c|||||c^Blacksmithing^230^10001^f
64q|Runed Mithril Hammer|c|||||c^Blacksmithing^220^10009^f
64r|Ebon Shiv|c|||||c^Blacksmithing^230^10013^f
64y|The Shatterer|c|||||c^Blacksmithing^235^10003^f
64z|Copper Claymore|c|s||||c^Blacksmithing^30^9983^f
650|Bronze Warhammer|c|s||||c^Blacksmithing^125^9985^f
651|Bronze Greatsword|c|||||c^Blacksmithing^130^9986^f
652|Bronze Battle Axe|c|||||c^Blacksmithing^135^9987^f
653|Blight|c|||||c^Blacksmithing^250^10011^f
654|Truesilver Champion|c|||||c^Blacksmithing^260^10015^f
655|Phantom Blade|c|||||c^Blacksmithing^245^10007^f
657|Steel Breastplate|c|||||c^Blacksmithing^200^9916^f
66e|The Ziggler|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
687|Sizzle Stick|Q|s||||q^1487^Deviate Eradication^16^^s
68o|Platemail Belt|v|s||||V^8129^13335^^s
68p|Platemail Boots|v|s||||V^8129^20081^^s
68q|Platemail Bracers|v|s||||V^8129^13439^^s
68r|Platemail Gloves|v|s||||V^8129^13489^^s
68s|Platemail Helm|v|s||||V^8129^20312^^s
68t|Platemail Leggings|v|s||||V^8129^27186^^s
68u|Platemail Armor|v|s||||V^8129^27290^^s
696|Hibernal Armor|dwx|||||d^349^Princess Theradras^0.19^0^k
697|Hibernal Boots|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
698|Hibernal Bracers|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
699|Hibernal Cloak|wx|s||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
69a|Hibernal Gloves|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69b|Hibernal Mantle|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
69c|Hibernal Pants|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69d|Hibernal Robe|dwx|||||d^349^Princess Theradras^0.19^0^k
69e|Hibernal Sash|wx|||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
69f|Hibernal Cowl|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
69g|Heraldic Belt|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69h|Heraldic Boots|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69i|Heraldic Bracers|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
69j|Heraldic Breastplate|dwx|||||d^349^Princess Theradras^0.19^0^k
69k|Heraldic Cloak|wx|||||o^Ancient Treasure^0.6^k~x^4637^Steel Lockbox^k
69l|Heraldic Gloves|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69m|Heraldic Headpiece|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10479^Kovic's Trading Satchel^k
69n|Heraldic Leggings|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
69o|Heraldic Spaulders|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
69q|Myrmidon's Breastplate|dwx|||||d^349^Princess Theradras^0.19^0^k
69r|Myrmidon's Cape|wx|||||x^4638^Reinforced Steel Lockbox^k~w^40^49^k
69s|Myrmidon's Gauntlets|wx|||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
69t|Myrmidon's Girdle|wx|||||x^4638^Reinforced Steel Lockbox^k~w^45^51^k
69u|Myrmidon's Greaves|wx|||||x^5758^Mithril Lockbox^k~x^19035^Lard's Special Picnic Basket^k
69v|Myrmidon's Helm|dwx|||||d^349^Princess Theradras^0.19^0^k
69w|Myrmidon's Leggings|dwx|||||d^349^Princess Theradras^0.19^0^k
69x|Myrmidon's Pauldrons|dwx|||||d^349^Princess Theradras^0.19^0^k
69y|Myrmidon's Defender|dwx|||||d^349^Princess Theradras^0.19^0^k
69z|Chromite Shield|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
6a1|Chromite Bracers|wx|||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
6a2|Chromite Chestplate|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
6a3|Chromite Gauntlets|wx|||||o^Ancient Treasure^0.5^k~o^Captain's Chest^0.8^k
6a4|Chromite Girdle|wx|s||||m^4855^Stonevault Brawler^0^s~m^258687^NPC 258687^0^s
6a5|Chromite Greaves|wx|||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
6a6|Chromite Barbute|wx|||||o^Ancient Treasure^1.3^k~x^4637^Steel Lockbox^k
6a7|Chromite Legplates|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
6a8|Chromite Pauldrons|wx|||||o^Ancient Treasure^0.9^k~x^4637^Steel Lockbox^k
6ak|Jouster's Wristguards|wx|s||||m^2287^Crushridge Warmonger^0^s
6al|Jouster's Chestplate|wx|||||o^Ancient Treasure^0.5^k~x^4637^Steel Lockbox^k
6am|Jouster's Gauntlets|wx|s||||m^258687^NPC 258687^0^s
6ao|Jouster's Greaves|wx|||||x^4634^Iron Lockbox^k~x^4636^Strong Iron Lockbox^k
6ap|Jouster's Visor|wx|s||||m^258102^NPC 258102^0^s
6aq|Jouster's Legplates|wx|s||||m^7011^Earthen Rocksmasher^0^s
6ar|Jouster's Pauldrons|wx|||||o^Ancient Treasure^2.3^k~x^4637^Steel Lockbox^k
6b2|Comfortable Leather Hat|c|||||c^Leatherworking^175^10490^f
6b3|Nightscape Tunic|c|s||||c^Leatherworking^200^10499^f
6b4|Nightscape Headband|c|s||||c^Leatherworking^200^10507^f
6b5|Practice Sword|w|s||||m^40^Kobold Miner^0^s~m^1131^Winter Wolf^0^s
6b6|Training Sword|w|sr||||m^3267^Razormane Water Seeker^0^s~m^271530^Elder Wendigo^0^s
6b7|Cadet's Bow|w|s||||m^1127^Elder Crag Boar^0^s~m^1131^Winter Wolf^0^s
6b8|Hunting Bow|w|s||||m^95^Defias Smuggler^0^s~m^454^Young Goretusk^0^s
6b9|Hunting Rifle|w|s||||m^251707^Ornery Galestrider^0^s~m^46^Murloc Forager^0^s
6ba|Pellet Rifle|w|s||||m^40^Kobold Miner^0^s~m^1196^Ice Claw Bear^0^s
6bb|Precision Bow|dwx|s||||d^34^^0^0^s~m^4805^Blackfathom Sea Witch^0^s
6bc|Firestarter|dwx|s||||d^47^Aggem Thorncurse^20^0^s~d^2959^^0^0^s
6bd|Turtle Scale Leggings|c|||||c^Leatherworking^230^10556^f
6be|Dire Wand|dwx|s||||m^923^Young Black Ravager^0^s~m^3771^Bleakheart Hellcaller^0^s
6bg|Explosive Shotgun|dwx|s||||m^4657^Maraudine Windchaser^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
6bh|Turtle Scale Breastplate|c|||||c^Leatherworking^205^10511^f
6bi|Hanzo Sword|x|||||x^5758^Mithril Lockbox^k
6bj|Turtle Scale Helm|c|||||c^Leatherworking^225^10552^f
6bk|Nightscape Shoulders|c|||||c^Leatherworking^185^10516^f
6bl|Nightscape Pants|c|||||c^Leatherworking^225^10548^f
6bm|Goblin Nutcracker|wx|r||||o^Ancient Treasure^1.6^k~o^Captain's Chest^1.3^k
6bn|Nightscape Cloak|c|||||c^Leatherworking^205^10550^f
6bo|Ebon Scimitar|wx|sr||||m^257885^NPC 257885^0^s
6bp|Nightscape Boots|c|||||c^Leatherworking^230^10558^f
6bq|Turtle Scale Bracers|c|||||c^Leatherworking^205^10518^f
6br|Battlefield Destroyer|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
6bs|Big Voodoo Robe|c|||||c^Leatherworking^190^10520^f
6bt|Big Voodoo Mask|c|||||c^Leatherworking^195^10531^f
6bu|Big Voodoo Pants|c|||||c^Leatherworking^215^10560^f
6bv|Tough Scorpid Breastplate|c|||||c^Leatherworking^195^10525^f
6bw|Tough Scorpid Gloves|c|||||c^Leatherworking^200^10542^f
6bx|Tough Scorpid Bracers|c|||||c^Leatherworking^195^10533^f
6by|Tough Scorpid Leggings|c|||||c^Leatherworking^220^10568^f
6bz|Tough Scorpid Shoulders|c|||||c^Leatherworking^215^10564^f
6c0|Tough Scorpid Helm|c|||||c^Leatherworking^225^10570^f
6c1|Tough Scorpid Boots|c|||||c^Leatherworking^210^10554^f
6c8|Big Voodoo Cloak|c|||||c^Leatherworking^215^10562^f
6cf|Blade of the Basilisk|w|U||||w^0^0^k
6ch|Tainted Pierce|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
6ci|The Butcher|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
6d1|Imperial Red Tunic|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
6d2|Imperial Red Boots|dwx|||||d^349^Princess Theradras^0.19^0^k
6d3|Imperial Red Bracers|dwx|||||d^349^Princess Theradras^0.19^0^k
6d4|Imperial Red Cloak|dwx|||||d^349^Princess Theradras^0.19^0^k
6d5|Imperial Red Gloves|dwx|||||d^349^Princess Theradras^0.19^0^k
6d6|Imperial Red Mantle|dwx|||||d^349^Princess Theradras^0.19^0^k
6d7|Imperial Red Pants|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6d9|Imperial Red Sash|dwx|||||d^349^Princess Theradras^0.19^0^k
6db|Serpentskin Girdle|dwx|||||d^349^Princess Theradras^0.19^0^k
6dc|Serpentskin Boots|dwx|||||d^349^Princess Theradras^0.19^0^k
6dd|Serpentskin Bracers|dwx|||||d^349^Princess Theradras^0.19^0^k
6de|Serpentskin Armor|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
6df|Serpentskin Cloak|dwx|||||d^349^Princess Theradras^0.19^0^k
6dg|Serpentskin Gloves|dwx|||||d^349^Princess Theradras^0.19^0^k
6di|Serpentskin Leggings|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6dj|Serpentskin Spaulders|dwx|||||d^349^Princess Theradras^0.19^0^k
6dk|Ebonhold Wristguards|dwx|||||d^349^Princess Theradras^0.19^0^k
6dl|Ebonhold Armor|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.05^0^k
6dm|Ebonhold Cloak|dwx|||||d^349^Princess Theradras^0.19^0^k
6dn|Ebonhold Gauntlets|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6do|Ebonhold Girdle|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6dp|Ebonhold Boots|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6dq|Ebonhold Helmet|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6dr|Ebonhold Leggings|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
6ds|Ebonhold Shoulderpads|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6dt|Valorous Wristguards|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
6du|Valorous Chestguard|dwx|||||d^349^Princess Theradras^0.19^0^k
6dv|Ebonhold Buckler|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
6dw|Valorous Gauntlets|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
6dx|Valorous Girdle|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10752^Emerald Encrusted Chest^k
6dy|Valorous Greaves|wx|||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
6dz|Valorous Helm|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10479^Kovic's Trading Satchel^k
6e0|Valorous Legguards|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9541^Box of Goodies^k
6e1|Valorous Pauldrons|wx|||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
6e2|Valorous Shield|dwx|||||d^349^Princess Theradras^0.19^0^k
6e3|Arcane Armor|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
6e4|Arcane Boots|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.07^0^k
6e5|Arcane Bands|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.06^0^k
6e6|Arcane Cloak|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6e7|Arcane Gloves|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.08^0^k
6e8|Arcane Pads|dwx|||||d^289^Darkmaster Gandling^0.07^0^k~d^289^Marduk Blackpool^0.02^0^k
6e9|Arcane Leggings|dwx|||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Darkmaster Gandling^0.08^0^k
6eb|Arcane Sash|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.1^0^k
6ec|Arcane Cover|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.06^0^k
6ed|Traveler's Belt|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.01^0^k
6ee|Traveler's Boots|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.07^0^k
6ef|Traveler's Bracers|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6eg|Traveler's Jerkin|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
6eh|Traveler's Cloak|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6ei|Traveler's Gloves|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.07^0^k
6ej|Traveler's Helm|dwx|||||d^289^Darkmaster Gandling^0.03^0^k~d^289^Marduk Blackpool^0.02^0^k
6ek|Traveler's Leggings|dwx|||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Darkmaster Gandling^0.11^0^k
6el|Traveler's Spaulders|dwx|||||d^289^Marduk Blackpool^0.02^0^k
6em|Hero's Bracers|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
6eo|Hero's Cape|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
6ep|Hero's Gauntlets|dwx|||||d^289^Marduk Blackpool^0.02^0^k
6eq|Hero's Belt|dwx|||||d^289^Marduk Blackpool^0.02^0^k
6er|Hero's Boots|dwx|||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Marduk Blackpool^0.02^0^k
6es|Hero's Band|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
6et|Hero's Leggings|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
6eu|Hero's Pauldrons|dwx|||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Darkmaster Gandling^0.03^0^k
6ev|Alabaster Plate Vambraces|dwx|||||d^349^Princess Theradras^0.19^0^k
6ew|Alabaster Breastplate|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.05^0^k
6ex|Hero's Buckler|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
6ey|Alabaster Plate Gauntlets|dwx|||||d^349^Princess Theradras^0.19^0^k
6ez|Alabaster Plate Girdle|dwx|||||d^349^Princess Theradras^0.19^0^k
6f0|Alabaster Plate Greaves|dwx|||||d^349^Princess Theradras^0.19^0^k~d^289^Darkmaster Gandling^0.01^0^k
6f1|Alabaster Plate Helmet|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
6f2|Alabaster Plate Leggings|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.06^0^k
6f3|Alabaster Plate Pauldrons|dwx|||||d^230^Plugger Spazzring^0.2^0^k
6f4|Alabaster Shield|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
6fu|Gauntlets of the Sea|c|||||c^Leatherworking^225^10630^f
6fv|Dragonscale Gauntlets|c|||||c^Leatherworking^220^10619^f
6fw|Helm of Fire|c|||||c^Leatherworking^245^10632^f
6fx|Feathered Breastplate|c|||||c^Leatherworking^245^10647^f
6pw|Hammer of Expertise|u|U||||
74r|Shriveled Heart|dw|U||||d^209^Antu'sul^2^0^k~d^209^Witch Doctor Zum'rah^2^0^k
75y|Field Plate Armor|wx|r||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
761|Field Plate Boots|wx|sr||||m^258042^NPC 258042^0^s
763|Field Plate Leggings|wx|sr||||m^4855^Stonevault Brawler^0^s
764|Field Plate Pauldrons|wx|sr||||o^Ancient Treasure^0.6^k~x^4637^Steel Lockbox^k
77z|Southsea Lamp|wx|||||o^Captain's Chest^0.8^k~x^9276^Pirate's Footlocker^k
78c|Sul'thraze the Lasher|u|U||||
78f|Expert Goldminer's Helmet|w|||||w^0^0^k
78i|Shovelphlange's Mining Axe|w|U||||w^0^0^k
78j|Sang'thraze the Deflector|d|U||||d^209^Antu'sul^10^0^k
78l|Earthen Rod|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78m|Tromping Miner's Boots|w|||||w^0^0^k
78n|Obsidian Cleaver|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78o|Stonevault Shiv|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78p|Archaic Defender|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
78q|Excavator's Brand|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78v|The Shoveler|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78w|Annealed Blade|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78x|Beacon of Hope|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
78y|Horned Viking Helmet|d|||||d^70^^50^0^k
78z|Gloves of Old|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
790|Legguards of the Vault|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
791|Energy Cloak|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
792|Worn Running Boots|d|||||d^70^^50^0^k
794|Baelog's Shortbow|d|||||d^70^The Lost Dwarves^90^0^k
795|Nordic Longshank|d|||||d^70^The Lost Dwarves^10^0^k
796|Earthborn Kilt|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
797|Battered Viking Shield|d|||||d^70^^50^0^k
798|Olaf's All Purpose Shield|d|||||d^70^^50^0^k
799|Girdle of Golem Strength|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
79a|Spirewind Fetter|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79b|Stoneweaver Leggings|d|s||||d^70^Ironaya^0^0^s
79c|Ironshod Bludgeon|d|s||||d^70^Ironaya^0^0^s
79d|Ironaya's Bracers|d|s||||d^70^Ironaya^0^0^s
79e|Cragfists|d|s||||d^70^Ancient Stone Keeper^0^0^s
79f|Rockshard Pauldrons|d|s||||d^70^Ancient Stone Keeper^0^0^s
79g|Galgann's Fireblaster|d|s||||d^70^Galgann Firehammer^0^0^s
79h|The Rockpounder|d|s||||d^70^Archaedas^0^0^s
79i|Oilskin Leggings|d|s||||d^70^Grimlok^0^0^s
79j|Grimlok's Tribal Vestments|d|s||||d^70^Grimlok^0^0^s
79k|Grimlok's Charge|d|s||||d^70^Grimlok^0^0^s
79m|Stoneslayer|d|s||||d^70^Archaedas^0^0^s
79n|Galgann's Firehammer|d|||||d^70^Galgann Firehammer^20^0^k
79o|Adventurer's Pith Helmet|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79q|Shadowforge Bushmaster|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79r|The Jackhammer|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79s|Ginn-su Sword|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79t|Pendulum of Doom|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79u|Monolithic Bow|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79v|Stonevault Bonebreaker|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79w|Unearthed Bands|dw|s||||m^4855^Stonevault Brawler^0^s~d^70^Shadowforge Relic Hunter^0.01^0^k
79x|Miner's Hat of the Deep|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79y|Spaulders of a Lost Age|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
79z|Papal Fez|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
7a0|Skullplate Bracers|d|||||d^70^Shadowforge Relic Hunter^0.01^0^k~d^70^Shadowforge Darkcaster^0.01^0^k
7a1|Forgotten Wraps|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10752^Emerald Encrusted Chest^k
7a2|Elemental Raiment|wx|||||x^4637^Steel Lockbox^k~w^0^0^k
7a3|Reticulated Bone Gauntlets|wx|s||||x^6827^Box of Supplies^k~w^0^0^k
7ad|Grubbis Paws|d|s||||d^90^Grubbis^40^0^s
7ae|Electrocutioner Leg|d|s||||d^90^Electrocutioner 6000^0^0^s
7af|Electrocutioner Lagnut|d|s||||d^90^Electrocutioner 6000^40^0^k
7ag|Spidertank Oilrag|d|s||||d^90^Electrocutioner 6000^100^0^s
7ah|Manual Crowd Pummeler|d|sU||||d^90^Crowd Pummeler 9-60^60^0^s
7ai|Gnomebot Operating Boots|d|s||||d^90^Crowd Pummeler 9-60^20^0^s
7ak|Hydrocane|d|s||||d^90^Viscous Fallout^16.67^0^s
7al|Toxic Revenger|d|s||||d^90^Viscous Fallout^66.67^0^s
7am|Acidic Walkers|d|s||||d^90^Viscous Fallout^16.67^0^s
7ao|Glass Shooter|d|||||d^90^^33.33^0^k
7ap|Royal Diplomatic Scepter|d|s||||d^90^^33.33^0^k
7aq|Thermaplugg's Central Core|d|s||||d^90^Mekgineer Thermaplugg^0^0^s
7ar|Thermaplugg's Left Arm|d|s||||d^90^Mekgineer Thermaplugg^14.29^0^s
7az|Gahz'rilla Fang|d|s||||d^209^Gahz'rilla^0^0^s
7b1|Gahz'rilla Scale Armor|d|||||d^209^Gahz'rilla^50^0^k
7b2|Bad Mojo Mask|d|||||d^209^Shadowpriest Sezz'ziz^25^0^k
7b5|Jinxed Hoodoo Skin|d|||||d^209^Shadowpriest Sezz'ziz^25^0^k
7b6|Jinxed Hoodoo Kilt|d|||||d^209^Shadowpriest Sezz'ziz^25^0^k
7b8|Big Bad Pauldrons|d|||||d^209^Chief Ukorz Sandscalp^30^0^k
7b9|The Chief's Enforcer|d|||||d^209^Chief Ukorz Sandscalp^20^0^k
7ba|Ripsaw|d|||||d^209^Chief Ukorz Sandscalp^20^0^k
7bb|Embrace of the Lycan|d|||||d^209^Chief Ukorz Sandscalp^20^0^k
7bc|Eyegouger|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7bd|The Minotaur|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7be|Witch Doctor's Cane|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7bf|Flaming Incinerator|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7bg|Spellshock Leggings|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7bh|Vibroblade|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bj|Hi-Tech Supergun|dw|s||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bk|Oscillating Power Hammer|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bl|Gyromatic Icemaker|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bm|Gizmotron Megachopper|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bn|Hotshot Pilot's Gloves|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7bo|Electromagnetic Gigaflux Reactivator|d|s||||d^90^Mekgineer Thermaplugg^57.14^0^s
7c5|Petrolspill Leggings|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7c6|Caverndeep Trudgers|dw|||||d^90^Dark Iron Agent^0.03^0^k~d^90^Leprous Defender^0.03^0^k
7c7|Bloodletter Scalpel|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7c8|Blackmetal Cape|d|||||d^209^Chief Ukorz Sandscalp^0.02^0^k~d^209^Witch Doctor Zum'rah^0.02^0^k
7cb|Nether-lace Tunic|q||h|9516||q^1946^Nether-lace Garment^26^h^k
7cc|Astral Knot Blouse|q||a|9515||q^1942^Astral Knot Garment^26^a^k
7cd|Celestial Stave|q|||||q^1958^Celestial Power^35^^k
7ce|Mud's Crushers|q|s||||q^1177^Hungry!^32^^s
7cf|Durtfeet Stompers|q|s||||q^1177^Hungry!^32^^s
7cg|Silent Hunter|q|s|h|||q^679^Call to Arms^35^h^s
7ch|Skullsplitter|q|s|h|||q^679^Call to Arms^35^h^s
7ci|Energized Stone Circle|Q|s||||q^2418^Power Stones^31^^s
7cn|Spellshifter Rod|Q|s||||q^2846^Tiara of the Deep^41^^s
7cr|Gemshale Pauldrons|Q|s||||q^2846^Tiara of the Deep^41^^s
7ct|Masons Fraternity Ring|Q|s||||q^2768^Divino-matic Rod^42^^s
7cu|Engineer's Guild Headpiece|Q|s||||q^2768^Divino-matic Rod^42^^s
7cv|Fire-welded Bracers|Q|s||||q^2904^A Fine Mess^25^^s
7cw|Fairywing Mantle|Q|s||||q^2904^A Fine Mess^25^^s
7cy|Talvash's Gold Ring|q|s|a|9588||q^2948^Gnome Improvement^30^a^s
7ec|Nogg's Gold Ring|q||h|9538||q^2950^Nogg's Ring Redo^30^h^k
7em|Sleeping Robes|q|s|a|||q^2561^Druid of the Claw^5^a^s
7en|Barkmail Leggings|q|s|a|||q^483^The Relics of Wakening^4^a^s
7eo|Lace Pants|q|s|a|||q^2520^Sathrah's Sacrifice^7^a^s
7ep|Cushioned Boots|q|s|a|4942||q^2520^Sathrah's Sacrifice^7^a^s
7er|Gritroot Staff|q|s|a|||q^483^The Relics of Wakening^4^a^s
7es|Mechanic's Pipehammer|Q|s|a|||q^2930^Data Rescue^25^a^s
7et|Repairman's Cape|Q|s|a|||q^2930^Data Rescue^25^a^s
7ev|Bastion of Stormwind|q|s|a|||q^1652^The Tome of Valor^20^a^s
7ew|Shoni's Disarming Tool|Q|s|a|||q^2928^Gyrodrillmatic Excavationators^25^a^s
7ex|Shilly Mitts|Q|s|a|||q^2928^Gyrodrillmatic Excavationators^25^a^s
7fa|Reedknot Ring|q|||||q^1203^Jarl Needs a Blade^30^^k
7fb|Civinad Robes|Q|s||||q^2841^Rig Wars^30^h^s~q^2929^The Grand Betrayal^30^a^s
7fc|Triprunner Dungarees|Q|s||||q^2841^Rig Wars^30^h^s~q^2929^The Grand Betrayal^30^a^s
7fd|Dual Reinforced Leggings|Q|s||||q^2841^Rig Wars^30^h^s~q^2929^The Grand Betrayal^30^a^s
7fe|Dwarven Charge|Q|s|a|||q^2240^The Hidden Chamber^35^a^s
7ff|Explorer's League Lodestar|Q|s|a|||q^2240^The Hidden Chamber^35^a^s
7fi|Pratt's Handcrafted Boots|q||a|9633||q^2821^The Mark of Quality^41^a^k
7fj|Pratt's Handcrafted Gloves|q||a|9632||q^2821^The Mark of Quality^41^a^k
7fk|Jangdor's Handcrafted Gloves|q||h|9631||q^2822^The Mark of Quality^41^h^k
7fl|Jangdor's Handcrafted Boots|q||h|9630||q^2822^The Mark of Quality^41^h^k
7fm|Skilled Handling Gloves|q||h|||q^864^Return to Apothecary Zinge^41^h^k
7fo|Swashbuckler Sash|q|||||q^2874^Deliver to MacKinley^40^^k
7fp|Shinkicker Boots|q|||||q^2874^Deliver to MacKinley^40^^k
7fq|Chelonian Cuffs|q|||||q^1560^Tooga's Quest^45^^k
7fr|The Hand of Antu'sul|d|s||||d^209^Antu'sul^0^0^s
7ft|Lifeblood Amulet|d|||||d^209^Antu'sul^35^0^k
7fu|Band of the Great Tortoise|q|||||q^1560^Tooga's Quest^45^^k
7fv|Optomatic Deflector|q|||||q^648^Rescue OOX-17/TN!^43^^k
7fw|Thermotastic Egg Timer|q|||||q^648^Rescue OOX-17/TN!^43^^k
7fx|Gnomish Inventor Boots|q|s||||q^836^Rescue OOX-09/HL!^43^^s
7fy|Gnomish Water Sinking Device|q|s||||q^836^Rescue OOX-09/HL!^43^^s
7fz|Failed Flying Experiment|q|||||q^2767^Rescue OOX-22/FE!^40^^k
7g0|Chainlink Towel|q|||||q^2767^Rescue OOX-22/FE!^40^^k
7g2|Honorguard Chestpiece|q||h|||q^2938^Venom to the Undercity^50^h^k
7g3|Gryphon Rider's Stormhammer|q||a|||q^2994^Saving Sharpbeak^48^a^k
7g4|Gryphon Rider's Leggings|q||a|||q^2994^Saving Sharpbeak^48^a^k
7g6|Cairnstone Sliver|q||a|||q^2942^The Morrow Stone^45^a^k
7g8|Granite Grips|q||a|||q^2845^Wandering Shay^44^a^k
7g9|Vinehedge Cinch|q||a|||q^2845^Wandering Shay^44^a^k
7ga|Boots of the Maharishi|q||h|||q^2987^Gordunni Cobalt^38^h^k
7gd|Earthclasp Barrier|q||h|||q^2903^The Battle Plans^39^h^k
7ge|Rushridge Boots|q||h|||q^2903^The Battle Plans^39^h^k
7gf|Dawnrider's Chestpiece|q||a|||q^2871^Delivering the Relic^40^a^k
7gg|Sentinel's Guard|q||a|||q^2871^Delivering the Relic^40^a^k
7gh|Wingcrest Gloves|q||h|||q^3062^Dark Heart^45^h^k
7gi|Stronghorn Girdle|q||h|||q^3062^Dark Heart^45^h^k
7gu|Tok'kar's Murloc Basher|q||h|||q^1427^Threat From the Sea^38^h^k
7gv|Tok'kar's Murloc Chopper|q||h|||q^1427^Threat From the Sea^38^h^k
7gw|Tok'kar's Murloc Shanker|q||h|||q^1427^Threat From the Sea^38^h^k
7gy|Leather Chef's Belt|q||h|||q^1430^Fresh Meat^39^h^k
7gz|Strength of the Treant|q||h|||q^3129^Weapons of Spirit^45^h^k
7h0|Force of the Hippogryph|q||h|||q^3129^Weapons of Spirit^45^h^k
7h2|Spirit of the Faerie Dragon|q||h|||q^3129^Weapons of Spirit^45^h^k
7h3|Grappler's Belt|q|s|a|||q^1440^Return to Vahlarriel^30^a^s
7he|Gloves of Insight|q|s|a|||q^1440^Return to Vahlarriel^30^a^s
7hf|Garrison Cloak|q|s|a|||q^1440^Return to Vahlarriel^30^a^s
7hk|Rustler Gloves|q||h|||q^1169^Identifying the Brood^38^h^k
7hl|Tharg's Shoelace|q||h|||q^1168^Army of the Black Dragon^38^h^k
7hm|Tharg's Disk|q||h|||q^1168^Army of the Black Dragon^38^h^k
7im|Simple Cord|w|s||||m^199^Young Fleshripper^0^s~m^480^Rusty Harvest Golem^0^s
7in|Simple Shoes|vw|s||||V^251981^335^^s~m^95^Defias Smuggler^0^s
7io|Simple Bands|Rw|s||||m^126^Murloc Coastrunner^0^s~m^504^Defias Trapper^0^s
7ip|Simple Cape|wx|s||||m^478^Riverpaw Outrunner^0^s~m^6123^Dark Iron Spy^0^s
7iq|Simple Gloves|wx|s||||m^590^Defias Looter^0^s~m^454^Young Goretusk^0^s
7ir|Simple Britches|dwx|sr||||d^3065^^0^0^s~m^589^Defias Pillager^0^s
7is|Simple Robe|dwx|sr||||d^2999^Rath'mael^10^0^s~d^3065^Durgen Dirgehammer^10^0^s
7it|Simple Blouse|dwx|sr||||d^2999^Witherfang^10^0^s~m^1164^Stonesplinter Bonesnapper^0^s
7iu|Nomad Sash|w|s||||m^504^Defias Trapper^0^s~m^126^Murloc Coastrunner^0^s
7iv|Nomad Sandals|w|s||||m^95^Defias Smuggler^0^s~m^36^Harvest Golem^0^s
7iw|Nomad Bands|wx|s||||m^117^Riverpaw Gnoll^0^s~m^474^Defias Rogue Wizard^0^s
7ix|Nomad Buckler|Rw|sr||||m^199^Young Fleshripper^0^s~m^834^Coyote^0^s
7iy|Nomad Cloak|vwx|s||||V^251997^350^^s~m^95^Defias Smuggler^0^s
7iz|Nomad Gloves|wx|s||||m^95^Defias Smuggler^0^s~m^454^Young Goretusk^0^s
7j0|Nomad Trousers|Rdwx|sr||||d^3065^^0^0^s~m^36^Harvest Golem^0^s
7j1|Nomad Tunic|Rdwx|sr||||d^2999^The Abandoned^20^0^s~m^1892^Moonrage Watcher^0^s
7j2|Cadet Belt|w|s||||m^480^Rusty Harvest Golem^0^s~m^504^Defias Trapper^0^s
7j3|Cadet Boots|Rwx|s||||m^123^Riverpaw Mongrel^0^s~m^834^Coyote^0^s
7j4|Cadet Bracers|w|s||||m^118^Prowler^0^s~m^1186^Elder Black Bear^0^s
7j5|Cadet Cloak|Rw|s||||m^1689^Scarred Crag Boar^0^s~m^504^Defias Trapper^0^s
7j6|Cadet Gauntlets|wx|s||||m^114^Harvest Watcher^0^s~m^1117^Rockjaw Bonesnapper^0^s
7j7|Cadet Leggings|dwx|sr||||d^2999^Viktor the Vile^10^0^s~m^1163^Stonesplinter Skullthumper^0^s
7j8|Cadet Shield|dw|sr||||d^2999^The Butcher^10^0^s~d^2999^Rath'mael^10^0^s
7j9|Cadet Vest|Rdwx|sr||||d^3065^Faldrim Anvilmar^10^0^s~m^36^Harvest Golem^0^s
7ja|Greenweave Sash|dwx|sr||||d^43^^0^0^s~d^48^^0^0^s
7jb|Greenweave Sandals|dwx|sr||||m^5755^Deviate Viper^0^s~m^3424^Thunderhawk Cloudscraper^0^s
7jc|Greenweave Bracers|dwx|sr||||d^43^^0^0^s~m^3250^Silithid Creeper^0^s
7jf|Greenweave Gloves|Rdwx|sr||||d^48^Geilhast^8.33^0^s~m^3458^Razormane Seer^0^s
7jj|Bandit Cinch|dwx|sr||||m^213^Starving Dire Wolf^0^s~m^505^Greater Tarantula^0^s
7jk|Bandit Boots|dwx|sr||||d^36^^0^0^s~m^3875^Haunted Servitor^0^s
7jl|Bandit Bracers|dwx|sr||||m^646^Mr. Smite^0^s~m^657^Defias Pirate^0^s
7jm|Bandit Buckler|dw|sr||||d^36^^0^0^s~m^1731^Goblin Craftsman^0^s
7jn|Bandit Cloak|Rdwx|sr||||d^2999^Witherfang^10^0^s~m^1083^Murloc Shorestriker^0^s
7jo|Bandit Gloves|dwx|sr||||d^36^^0^0^s~m^213^Starving Dire Wolf^0^s
7jp|Bandit Pants|dwx|sr||||d^48^Geilhast^16.67^0^s~m^433^Shadowhide Gnoll^0^s
7jq|Bandit Jerkin|dwx|sr||||d^34^Dextren Ward^6.25^0^s~d^33^^0^0^s
7jr|Raider's Chestpiece|dw|sr||||d^36^Cookie^0^0^s~m^422^Murloc Flesheater^0^s
7jt|Raider's Bracers|Rdw|sr||||d^2999^Viktor the Vile^10^0^s~d^36^Rhahk'Zor^5.26^0^s
7ju|Raider's Cloak|Rdw|sr||||d^2999^^0^0^s~m^114^Harvest Watcher^0^s
7jv|Raider's Gauntlets|dw|sr||||m^1731^Goblin Craftsman^0^s~m^624^Undead Excavator^0^s
7jw|Raider's Belt|dw|sr||||d^36^Gilnid^9.52^0^s~m^539^Pygmy Venom Web Spider^0^s
7jy|Raider's Shield|dw|sr||||d^36^^0^0^s~m^446^Redridge Basher^0^s
7jz|Ivycloth Tunic|dwx|sr||||d^2959^^0^0^s
7k0|Ivycloth Boots|dwx|sr||||m^3863^Lupine Horror^0^s~d^34^Targorr the Dread^0.01^0^k
7k1|Ivycloth Bracelets|Rdwx|sr||||m^1022^Mottled Scytheclaw^0^s~m^1400^Wetlands Crocolisk^0^s
7k2|Ivycloth Cloak|Rdwx|sr||||d^34^^0^0^s~m^3654^Mutanus the Devourer^0^s
7k3|Ivycloth Gloves|Rdwx|sr||||m^1708^Defias Inmate^0^s~R^5849^Digger Flameforge^0^s
7k4|Ivycloth Mantle|Rdwx|sr||||m^1034^Dragonmaw Raider^0^s~m^2349^Giant Moss Creeper^0^s
7k5|Ivycloth Pants|dwx|sr||||m^1069^Crimson Whelp^0^s~d^34^Hamhock^0.01^0^k
7k7|Ivycloth Sash|dwx|sr||||d^2959^Arcane Anomaly^14.29^0^s~d^90^^0^0^s
7k9|Superior Belt|Rdwx|sr||||m^1706^Defias Prisoner^0^s~m^1707^Defias Captive^0^s
7ka|Superior Boots|Rdwx|sr||||d^34^Hamhock^5.88^0^s~R^584^Kazon^0^s
7kb|Superior Bracers|dwx|sr||||m^1707^Defias Captive^0^s~m^6206^Caverndeep Burrower^0^s
7kc|Superior Buckler|dwx|sr||||d^34^Hamhock^5.88^0^s~m^1708^Defias Inmate^0^s
7ke|Superior Gloves|dwx|sr||||d^34^Bazil Thredd^6.25^0^s~m^2503^Hillsbrad Foreman^0^s
7kf|Superior Shoulders|Rdwx|sr||||d^2959^^0^0^s~m^604^Plague Spreader^0^s
7kg|Superior Leggings|dwx|sr||||d^90^^0^0^s~m^533^Nightbane Shadow Weaver^0^s
7kh|Superior Tunic|dwx|sr||||d^90^^0^0^s~m^1715^Defias Insurgent^0^s
7ki|Fortified Boots|Rdwx|sr||||d^34^Targorr the Dread^5^0^s~d^90^^0^0^s
7kj|Fortified Bracers|dwx|sr||||d^34^Kam Deepfury^5.88^0^s~d^34^Hamhock^5.88^0^s
7kk|Fortified Cloak|dwx|sr||||m^436^Blackrock Shadowcaster^0^s~m^1010^Mosshide Fenrunner^0^s
7kl|Fortified Gauntlets|dwx|sr||||d^33^^0^0^s~d^34^^0^0^s
7km|Fortified Belt|dwx|sr||||d^34^Bazil Thredd^12.5^0^s~d^33^Wolf Master Nandos^11.11^0^s
7kn|Fortified Leggings|dwx|sr||||d^34^Kam Deepfury^5.88^0^s
7ko|Fortified Shield|dwx|sr||||d^34^Targorr the Dread^0.01^0^k~d^34^Hamhock^0.01^0^k
7kp|Fortified Spaulders|Rdwx|sr||||d^2998^^0^0^s~R^5849^Digger Flameforge^0^s
7kq|Fortified Chain|dwx|sr||||d^34^^0^0^s~m^568^Shadowhide Warrior^0^s
7ks|Durable Boots|Rdwx|sr||||m^4306^Scarlet Torturer^0^s~m^2371^Daggerspine Siren^0^s
7kt|Durable Bracers|dwx|sr||||m^269134^NPC 269134^0^s~d^34^Kam Deepfury^0.01^0^k
7kv|Durable Gloves|Rdwx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
7kw|Durable Shoulders|Rdwx|sr||||m^2358^Dalaran Summoner^0^s~d^90^Grubbis^0.39^0^k
7kx|Durable Pants|Rdx|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
7kz|Scaled Leather Belt|dwx|sr||||m^2376^Torn Fin Oracle^0^s~m^271351^Dragonmaw Reclaimer^0^s
7l0|Scaled Leather Boots|Rdwx|sr||||m^205^Nightbane Dark Runner^0^s~d^90^Grubbis^0.39^0^k
7l1|Scaled Leather Bracers|dwx|sr||||d^34^Dextren Ward^0.01^0^k~d^34^Kam Deepfury^0.01^0^k
7l2|Scaled Shield|Rdx|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
7l4|Scaled Leather Gloves|Rdwx|sr||||d^90^^0^0^s~m^1038^Dragonmaw Shadowwarder^0^s
7l6|Scaled Leather Shoulders|Rdwx|sr||||m^2359^Elemental Slave^0^s~d^90^Grubbis^0.39^0^k
7l7|Scaled Leather Tunic|Rdwx|sr||||d^90^^0^0^s~R^14277^Lady Zephris^0^s
7l8|Banded Armor|Rdwx|sr||||m^2240^Syndicate Footpad^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
7lb|Banded Gauntlets|Rdwx|sr||||d^90^^0^0^s~m^6220^Irradiated Horror^0^s
7lc|Banded Girdle|Rdwx|sr||||m^271348^Dragonmaw Soulbinder^0^s~d^90^Grubbis^0.39^0^k
7ld|Banded Leggings|Rdx|sr||||d^2959^^0^0^s~R^1037^Dragonmaw Battlemaster^0.46^k
7le|Banded Pauldrons|Rdx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
7lf|Banded Shield|Rdx|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
7lk|Conjurer's Gloves|Rdwx|sr||||R^14221^Gravis Slipknot^0^s~m^258804^NPC 258804^0^s
7ll|Conjurer's Hood|dwx|sr||||d^189^^0^0^s~m^4292^Scarlet Protector^0^s
7ls|Archer's Boots|Rdwx|sr||||m^4540^Scarlet Monk^0^s~R^5935^Ironeye the Invincible^0^s
7lu|Archer's Buckler|dwx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k
7lv|Archer's Cap|dwx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k
7lz|Archer's Shoulderpads|dwx|sr||||d^90^Mekgineer Thermaplugg^0^0^s
7m4|Renegade Gauntlets|Rdwx|sr||||d^90^Mekgineer Thermaplugg^0^0^s~R^14277^Lady Zephris^0^s
7m6|Renegade Circlet|dwx|sr||||m^2907^Dustbelcher Mystic^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
7m9|Renegade Shield|dwx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k
7mz|Jazeraint Shield|wx|r||||o^Ancient Treasure^0.9^k~x^4636^Strong Iron Lockbox^k
7nf|Royal Headband|wx|sr||||m^4853^Stonevault Geomancer^0^s
7ni|Brigade Defender|wx|r||||o^Ancient Treasure^1.3^k~x^4637^Steel Lockbox^k
7nz|Embossed Plate Shield|wx|r||||o^Ancient Treasure^0.5^k~x^4637^Steel Lockbox^k
7om|Warmonger's Buckler|dwx|r||||d^349^Princess Theradras^0.19^0^k
7ou|Embossed Plate Armor|wx|r||||o^Ancient Treasure^1.3^k~o^Captain's Chest^1.3^k
7ov|Embossed Plate Gauntlets|wx|sr||||o^Ancient Treasure^0.6^k~x^4637^Steel Lockbox^k
7ox|Embossed Plate Helmet|wx|sr||||m^4855^Stonevault Brawler^0^s
7oy|Embossed Plate Leggings|wx|r||||o^Ancient Treasure^0.7^k~x^4637^Steel Lockbox^k
7oz|Embossed Plate Pauldrons|wx|r||||o^Ancient Treasure^1.2^k~o^Captain's Chest^0.8^k
7p2|Overlord's Shield|dwx|r||||d^349^Princess Theradras^0.19^0^k
7pq|Black Mageweave Vest|c|||||c^Tailoring^185^12048^f
7pu|Shadoweave Pants|c|||||c^Tailoring^190^12052^f
7pv|Black Mageweave Gloves|c|||||c^Tailoring^195^12053^f
7pw|Shadoweave Robe|c|||||c^Tailoring^195^12055^f
7q0|White Bandit Mask|c|||||c^Tailoring^180^12059^f
7q1|Red Mageweave Pants|c|||||c^Tailoring^180^12060^f
7q2|Stormcloth Pants|c|||||c^Tailoring^185^12062^f
7q3|Stormcloth Gloves|c|||||c^Tailoring^185^12063^f
7qa|Red Mageweave Gloves|c|||||c^Tailoring^190^12066^f
7qb|Dreamweave Gloves|c|||||c^Tailoring^205^12067^f
7qc|Stormcloth Vest|c|||||c^Tailoring^190^12068^f
7qd|Dreamweave Vest|c|||||c^Tailoring^205^12070^f
7qf|Shadoweave Gloves|c|||||c^Tailoring^205^12071^f
7qg|Black Mageweave Headband|c|||||c^Tailoring^205^12072^f
7qh|Shadoweave Mask|c|||||c^Tailoring^200^12086^f
7qi|Black Mageweave Boots|cx|||||c^Tailoring^205^12073^f
7qj|Black Mageweave Shoulders|c|||||c^Tailoring^205^12074^f
7qk|Shadoweave Shoulders|c|||||c^Tailoring^210^12076^f
7ql|Red Mageweave Shoulders|c|||||c^Tailoring^195^12078^f
7qn|Shadoweave Boots|c|||||c^Tailoring^215^12082^f
7qo|Stormcloth Headband|c|||||c^Tailoring^200^12083^f
7qp|Red Mageweave Headband|c|||||c^Tailoring^200^12084^f
7qu|Stormcloth Shoulders|c|||||c^Tailoring^200^12087^f
7qv|Stormcloth Boots|c|||||c^Tailoring^205^12090^f
7qx|Dreamweave Circlet|c|||||c^Tailoring^220^12092^f
7qy|Cindercloth Robe|c|||||c^Tailoring^205^12069^f
7qz|Pious Legwraps|q||a|||q^981^The Tower of Althalaxx^26^a^k
7r0|Cindercloth Boots|c|||||c^Tailoring^215^12088^f
7r1|Simple Linen Pants|c|s||||c^Tailoring^1^12044^f
7r2|Simple Linen Boots|c|||||c^Tailoring^20^12045^f
7r3|Simple Kilt|c|s||||c^Tailoring^75^12046^f
7r4|Colorful Kilt|c|||||c^Tailoring^70^12047^f
7ry|Lord's Crest|dwx|r||||d^349^Princess Theradras^0.19^0^k
7s6|Gothic Plate Armor|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
7s7|Gothic Plate Gauntlets|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
7s8|Gothic Plate Girdle|wx|r||||o^Ancient Treasure^1.6^k~x^4637^Steel Lockbox^k
7s9|Gothic Sabatons|wx|r||||o^Ancient Treasure^0.8^k~x^4637^Steel Lockbox^k
7sa|Gothic Plate Helmet|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
7sb|Gothic Plate Leggings|wx|sr||||x^4638^Reinforced Steel Lockbox^k~x^9265^Cuergo's Hidden Treasure^k
7sc|Gothic Plate Spaulders|wx|sr||||m^7291^Galgann Firehammer^0^s
7sd|Revenant Deflector|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
7se|Gothic Plate Vambraces|wx|sr||||o^Ancient Treasure^0.9^k~x^4637^Steel Lockbox^k
7tb|Revenant Bracers|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^12122^Kum'isha's Junk^k
7td|Revenant Gauntlets|dwx|r||||d^349^Princess Theradras^0.19^0^k
7te|Revenant Girdle|dwx|r||||d^349^Princess Theradras^0.19^0^k
7tf|Revenant Boots|dwx|r||||d^349^Princess Theradras^0.19^0^k
7tg|Revenant Helmet|dwx|r||||d^349^Princess Theradras^0.19^0^k
7ti|Revenant Shoulders|dwx|r||||d^349^Princess Theradras^0.19^0^k
7tj|High Councillor's Tunic|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7u6|Mercurial Guard|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7ud|Templar Gauntlets|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
7v7|Crusader's Shield|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
7ve|Overlord's Vambraces|wx|r||||x^4638^Reinforced Steel Lockbox^k~w^43^50^k
7vf|Overlord's Chestplate|dwx|r||||d^349^Princess Theradras^0.19^0^k
7vh|Overlord's Gauntlets|wx|r||||x^4638^Reinforced Steel Lockbox^k~w^45^51^k
7vj|Overlord's Crown|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^12122^Kum'isha's Junk^k
7vk|Overlord's Legplates|dwx|r||||d^349^Princess Theradras^0.19^0^k
7vl|Overlord's Spaulders|dwx|r||||d^349^Princess Theradras^0.19^0^k
7we|Heavy Lamellar Boots|dwx|r||||d^349^Princess Theradras^0.19^0^k
7wf|Heavy Lamellar Vambraces|dwx|r||||d^349^Princess Theradras^0.19^0^k
7wh|Heavy Lamellar Helm|dwx|r||||d^349^Princess Theradras^0.19^0^k
7wi|Heavy Lamellar Gauntlets|dwx|r||||d^349^Princess Theradras^0.19^0^k
7wj|Heavy Lamellar Girdle|dwx|r||||d^349^Princess Theradras^0.19^0^k
7wk|Heavy Lamellar Leggings|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
7wm|Master's Vest|rwx|r||||d^249^Onyxia^0.83^1^k
7wn|Master's Boots|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wo|Master's Bracers|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wp|Master's Cloak|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
7wq|Master's Hat|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wr|Master's Gloves|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7ws|Master's Leggings|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wt|Master's Mantle|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wv|Master's Belt|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7ww|Adventurer's Bracers|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
7wx|Adventurer's Boots|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7wy|Adventurer's Cape|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Marduk Blackpool^0.02^0^k
7wz|Adventurer's Belt|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x0|Adventurer's Gloves|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x1|Adventurer's Bandana|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x2|Adventurer's Legguards|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x3|Adventurer's Shoulders|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x7|Masterwork Cape|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
7x8|Masterwork Gauntlets|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7x9|Masterwork Girdle|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7xa|Masterwork Boots|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7xb|Masterwork Shield|rwx|r||||d^249^Onyxia^0.83^1^k
7xc|Masterwork Circlet|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7xd|Masterwork Legplates|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7xe|Masterwork Pauldrons|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
7xh|Emerald Gauntlets|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
7xr|Greenweave Mantle|dw|sr||||d^48^Twilight Lord Kelris^8.33^0^s
7xs|Sage's Circlet|Rdwx|sr||||m^6232^Arcane Nullifier X-21^0^s~d^90^Grubbis^0.39^0^k
7xt|Durable Hat|Rdx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
7yw|Scarlet Chestpiece|w|||||w^0^0^k
7yx|Scarlet Belt|dw|s||||d^189^^0^0^s~m^4295^Scarlet Myrmidon^0^s
7yy|Scarlet Leggings|d|s||||d^189^High Inquisitor Whitemane^100^0^s~d^189^Herod^15^0^k
7yz|Scarlet Gauntlets|w|s||||w^0^0^k
7z0|Scarlet Boots|dw|||||d^189^Houndmaster Loksey^0.01^0^k~d^189^Herod^0.01^0^k
7z1|Scarlet Wristguards|dw|s||||d^189^^0^0^s~m^4292^Scarlet Protector^0^s
7zq|Duracin Bracers|Q|s||||q^2418^Power Stones^31^^s
7zr|Everlast Boots|Q|s||||q^2418^Power Stones^31^^s
7zu|Ornate Shield|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
7zy|Demon Guard|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
7zz|Hyperion Shield|rwx|r||||d^249^Onyxia^0.83^1^k
800|Imbued Plate Armor|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
801|Imbued Plate Gauntlets|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
802|Imbued Plate Girdle|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.05^0^k
803|Imbued Plate Greaves|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.04^0^k
804|Imbued Plate Helmet|dwx|||||d^289^Darkmaster Gandling^0.04^0^k~d^289^Marduk Blackpool^0.02^0^k
805|Imbued Plate Leggings|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
806|Imbued Plate Pauldrons|dwx|||||d^289^Darkmaster Gandling^0.04^0^k~d^289^Marduk Blackpool^0.02^0^k
807|Imbued Plate Vambraces|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.07^0^k
80g|Hyperion Armor|rwx|r||||d^249^Onyxia^0.83^1^k
80h|Hyperion Greaves|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
80i|Hyperion Gauntlets|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
80j|Hyperion Girdle|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
80k|Hyperion Helm|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
80l|Hyperion Legplates|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
80m|Hyperion Pauldrons|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
80n|Hyperion Vambraces|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Darkmaster Gandling^0.08^0^k
80v|Blackened Defias Armor|d|s||||d^36^Edwin VanCleef^14.29^0^s
80w|Blackened Defias Leggings|d|s||||d^36^^0^0^s
80x|Blackened Defias Gloves|dw|s||||d^36^^0^0^s~m^634^Defias Overseer^0^s
80y|Blackened Defias Boots|d|s||||d^36^Gilnid^19.05^0^s
80z|Blackened Defias Belt|d|s||||d^36^Captain Greenskin^23.81^0^s
810|Durable Belt|Rdwx|sr||||d^2959^^0^0^s~m^205^Nightbane Dark Runner^0^s
811|Bandit Shoulders|wx|s||||m^505^Greater Tarantula^0^s~m^436^Blackrock Shadowcaster^0^s
812|Scaled Leather Headband|Rdwx|sr||||m^1053^Dark Iron Tunneler^0^s~d^90^Grubbis^0.39^0^k
813|Raider's Shoulderpads|wx|s||||m^4416^Defias Strip Miner^0^s
814|Banded Helm|Rdx|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
815|Banded Boots|Rdx|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
816|Leggings of the Fang|d|s||||d^43^Lord Cobrahn^44.44^0^s
817|Footpads of the Fang|d|s||||d^43^Lord Serpentis^0^0^s
818|Belt of the Fang|d|s||||d^43^Lady Anacondra^20^0^s
819|Gloves of the Fang|dw|s||||d^43^^0^0^s~m^3840^Druid of the Fang^0^s
81h|Rough Copper Vest|c|s||||c^Blacksmithing^1^12260^f
81j|Silvered Bronze Leggings|c|s||||c^Blacksmithing^130^12259^f
82m|Shadowy Belt|q|||||q^3385^The Undermarket^46^^k
83w|Mithril Blunderbuss|c|||||c^Engineering^205^12595^f
83y|Mithril Heavy-bore Rifle|c|||||c^Engineering^220^12614^f
84z|Camping Knife|q|s|a|||q^320^Return to Bellowfiz^3^a^s
851|Rancher's Trousers|q|s|a|||q^314^Protecting the Herd^7^a^s
852|Wooly Mittens|q|s|a|||q^312^Tundra MacGrann's Stolen Stash^7^a^s
855|Foreman Vest|w|||||w^0^0^k
856|Foreman Pants|w|||||w^0^0^k
85j|Quillshooter|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85m|Manslayer|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85n|Ebony Boneclub|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85o|Freezing Shard|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85p|Boneslasher|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85q|Corpseshroud|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85u|Thoughtcast Boots|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85x|Death's Head Vestment|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85y|Briar Tredders|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
85z|Quillward Harness|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
860|Stormgale Fists|dw|||||d^129^Withered Warrior^0.02^0^k~d^129^Withered Reaver^0.02^0^k
873|Winter's Bite|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
874|Stinging Bow|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
875|Stealthblade|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
876|Ragehammer|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
877|Bludgeon of the Grinning Dog|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
878|Deathblow|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
879|Mistwalker Boots|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87a|Soulcatcher Halo|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87b|Murkwater Gauntlets|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87c|Slimescale Bracers|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87d|Silvershell Leggings|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87e|Mindseye Circle|dw|||||d^109^Shade of Eranikus^0.02^0^k~d^109^Jammal'an the Prophet^0.02^0^k
87f|Painted Chain Leggings|q|s|h|||q^3376^Break Sharptusk!^3^h^s
87g|Nomadic Gloves|q||h|6171||q^3376^Break Sharptusk!^3^h^s
87h|Brewer's Gloves|q|s|h|||q^1358^Sample for Helbrim^10^h^s
87i|Long Draping Cape|q||h|5610||q^1358^Sample for Helbrim^10^h^s
87w|Will of the Mountain Giant|q||h|||q^3129^Weapons of Spirit^45^h^k
87x|Trailblazer Boots|q|s|h|||q^3514^Horde Presence^24^h^s
87y|Jutebraid Gloves|q|s|h|||q^3514^Horde Presence^24^h^s
87z|Sedgeweed Britches|q|s|a|||q^3522^Iverron's Antidote^2^a^s
880|Barkmail Vest|q|s|a|3273||q^3522^Iverron's Antidote^2^a^s
881|Talbar Mantle|q|s||||q^3369^In Nightmares^20^h^s~q^3370^In Nightmares^20^a^s
882|Quagmire Galoshes|q|s||||q^3369^In Nightmares^20^h^s~q^3370^In Nightmares^20^a^s
883|Shard of the Splithooves|q|||||q^2701^Heroes of Old^52^^k
88u|Aegis of Battle|q||h|||q^2938^Venom to the Undercity^50^h^k
894|Enchanted Azsharite Felbane Sword|q|||||q^3625^Enchanted Azsharite Fel Weaponry^53^^k
895|Enchanted Azsharite Felbane Dagger|q|||||q^3625^Enchanted Azsharite Fel Weaponry^53^^k
896|Enchanted Azsharite Felbane Staff|q|||||q^3625^Enchanted Azsharite Fel Weaponry^53^^k
898|Encarmine Boots|q||h|||q^1172^The Brood of Onyxia^40^h^k
899|Boots of Zua'tec|q||h|||q^1172^The Brood of Onyxia^40^h^k
89a|Enormous Ogre Boots|q||h|||q^1166^Overlord Mok'Morokk's Concern^38^h^k
89b|Fiendish Skiv|q||h|||q^1173^Challenge Overlord Mok'Morokk^40^h^k
89c|Chillnail Splinter|q||h|||q^1173^Challenge Overlord Mok'Morokk^40^h^k
89d|Firwillow Wristbands|q||a|||q^2972^Doling Justice^42^a^k
89e|Nightscale Girdle|q||a|||q^2972^Doling Justice^42^a^k
89f|Steelsmith Greaves|q||a|||q^3461^Return to Tymor^47^a^k
89g|Skullspell Orb|q||a|||q^3461^Return to Tymor^47^a^k
89h|Pyrestone Orb|q||h|||q^3507^Betrayed^51^h^k
89i|Dragonclaw Ring|Q|s||||q^3525^Extinguishing the Idol^32^^s
89j|Dragon's Blood Necklace|Q|s|h|||q^1048^Into The Scarlet Monastery^37^h^s
8ab|Ring of Fortitude|q||a|11869||q^3566^Rise, Obsidion!^47^a^k
8ac|Centurion Legplates|q||a|||q^3566^Rise, Obsidion!^47^a^k
8ad|Lordrec Helmet|q||a|||q^3566^Rise, Obsidion!^47^a^k
8ae|Dragonflight Leggings|q|||||q^3463^Set Them Ablaze!^47^^k
8af|Drakefire Headguard|q|||||q^3463^Set Them Ablaze!^47^^k
8ag|Axe of the Ebon Drake|q|||||q^3463^Set Them Ablaze!^47^^k
8ah|Kaylari Shoulders|q||a|||q^3378^Prayer to Elune^45^a^k
8ai|Runesteel Vambraces|q||a|||q^3378^Prayer to Elune^45^a^k
8aj|Teacher's Sash|q|s|a|||q^1364^Mazen's Behest^37^a^s
8ak|Wanderlust Boots|q|s|a|||q^1364^Mazen's Behest^37^a^s
8al|Avenguard Helm|Q|||||q^3528^The God Hakkar^48^^k
8am|Lifeforce Dirk|Q|||||q^3528^The God Hakkar^48^^k
8an|Gemburst Circlet|Q|||||q^3528^The God Hakkar^48^^k
8au|X'caliboar|d|||||d^129^Ragglesnout^20^0^k
8aw|Swine Fists|d|||||d^129^Plaguemaw the Rotting^60^0^k
8ax|Coldrage Dagger|d|s||||d^129^Amnennar the Coldbringer^20^0^k
8ay|Robes of the Lich|d|s||||d^129^Amnennar the Coldbringer^0^0^s
8az|Icemetal Barbute|d|s||||d^129^Amnennar the Coldbringer^100^0^s
8b0|Deathchill Armor|d|s||||d^129^Amnennar the Coldbringer^0^0^s
8b1|Bonefingers|d|s||||d^129^Amnennar the Coldbringer^20^0^k
8b2|Plaguerot Sprig|d|s||||d^129^Plaguemaw the Rotting^100^0^s
8b3|Savage Boar's Guard|d|s||||d^129^Ragglesnout^100^0^s
8b4|Boar Champion's Belt|d|||||d^129^Ragglesnout^40^0^k
8b5|Glowing Eye of Mordresh|d|s||||d^129^Mordresh Fire Eye^100^0^s
8b6|Mordresh's Lifeless Skull|d|s||||d^129^Mordresh Fire Eye^0^0^s
8b7|Deathmage Sash|d|||||d^129^Mordresh Fire Eye^33.33^0^k
8b8|Glutton's Cleaver|d|s||||d^129^Glutton^100^0^s
8ba|Fleshhide Shoulders|d|s||||d^129^Glutton^50^0^k
8bb|Carapace of Tuten'kash|d|||||d^129^Tuten'kash^33.33^0^k
8bc|Silky Spider Cape|d|s||||d^129^Tuten'kash^50^0^s
8bg|Mark of Hakkar|x|||||x^10773^Hakkari Urn^k
8bh|Hakkari Breastplate|x|||||x^10773^Hakkari Urn^k
8bi|Hakkari Shroud|x|||||x^10773^Hakkari Urn^k
8bj|Atal'ai Spaulders|w|||||m^5712^Zolo^4^k~m^5713^Gasher^4^k
8bx|Firebreather|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
8by|Atal'alarion's Tusk Ring|d|||||d^109^Atal'alarion^40^0^k
8bz|Headspike|d|||||d^109^Atal'alarion^20^0^k
8c1|Slitherscale Boots|d|||||d^109^^50^0^k
8c2|Wingveil Cloak|d|||||d^109^Spawn of Hakkar^25^0^k
8c4|Fist of the Damned|d|||||d^109^^33.33^0^k
8c5|Eater of the Dead|d|||||d^109^^33.33^0^k
8c6|Vestments of the Atal'ai Prophet|d|||||d^109^Jammal'an the Prophet^33.33^0^k
8c7|Kilt of the Atal'ai Prophet|d|||||d^109^Jammal'an the Prophet^33.33^0^k
8c8|Gloves of the Atal'ai Prophet|d|||||d^109^Jammal'an the Prophet^33.33^0^k
8ck|Jackseed Belt|q|s|h|||q^3301^Mura Runetotem^10^h^s
8cl|Sower's Cloak|q||h|1270||q^3301^Mura Runetotem^10^h^s
8cn|Vanquisher's Sword|Q|s||||q^3341^Bring the End^37^h^s~q^3636^Bring the Light^39^a^s
8co|Amberglow Talisman|Q|s||||q^3341^Bring the End^37^h^s~q^3636^Bring the Light^39^a^s
8cq|Staff of Lore|q|||||q^3161^Gahz'ridian^43^^k
8cr|Surveyor's Tunic|q|||||q^3161^Gahz'ridian^43^^k
8ct|Dragon's Eye|d|||||d^109^Shade of Eranikus^40^0^k
8cx|Horns of Eranikus|d|||||d^109^Shade of Eranikus^40^0^k
8cz|Crest of Supremacy|d|||||d^109^Shade of Eranikus^39.75^0^k
8d0|Rod of Corrosion|d|||||d^109^Shade of Eranikus^39.75^0^k
8d1|Tooth of Eranikus|d|||||d^109^Shade of Eranikus^20^0^k
8d2|Might of Hakkar|d|||||d^109^Avatar of Hakkar^20^0^k
8d6|Windscale Sarong|d|||||d^109^Avatar of Hakkar^40^0^k
8d7|Featherskin Cape|d|||||d^109^Avatar of Hakkar^40^0^k
8d8|Spire of Hakkar|d|||||d^109^Avatar of Hakkar^20^0^k
8d9|Warrior's Embrace|d|||||d^109^Avatar of Hakkar^39.75^0^k
8da|Bloodshot Greaves|d|||||d^109^Avatar of Hakkar^39.75^0^k
8db|Dragon's Call|d|||||d^109^Shade of Eranikus^0.5^0^k
8fb|Apothecary Gloves|Qq|s|h|||q^862^Dig Rat Stew^18^h^s~q^962^Serpentbloom^14^h^s
8jy|Jang'thraze the Protector|d|U||||d^209^Chief Ukorz Sandscalp^10^0^k
8ku|Archaedic Stone|d|s||||d^70^Archaedas^0^0^s
8kw|Belgrom's Hammer|q||h|||q^3507^Betrayed^51^h^k
8kx|Darkwater Talwar|d|s||||d^48^Lady Sarevess^50^0^s
8kz|Rainstrider Leggings|Q|||||q^1446^Jammal'an the Prophet^48^^k
8l0|Helm of Exile|Q|||||q^1446^Jammal'an the Prophet^48^^k
8mr|Stemleaf Bracers|q|s|a|6060||q^456^The Balance of Nature^1^a^s
8mt|Woodland Robes|q|s|a|||q^917^Webwood Egg^1^a^s
8mu|Viny Gloves|q|s|a|||q^459^The Woodland Protector^1^a^s
8mv|Farmer's Boots|q|s|a|||q^88^Princess Must Die!^6^a^s
8mw|Outfitter Gloves|q|s|a|||q^21^Skirmish at Echo Ridge^1^a^s
8mx|Blazewind Breastplate|q|||||q^717^Tremors of the Earth^45^a^k~q^793^Broken Alliances^45^h^k
8mz|Warforged Chestplate|q|||||q^717^Tremors of the Earth^45^a^k~q^793^Broken Alliances^45^h^k
8n0|Mindburst Medallion|q|||||q^717^Tremors of the Earth^45^a^k~q^793^Broken Alliances^45^h^k
8nx|Brightscale Girdle|q|s|a|||q^1031^The Branch of Cenarius^27^a^s
8ou|Orb of Lorica|Q|s|a|||q^1053^In the Name of the Light^35^a^s
8ov|Nether Force Wand|q|||||q^1952^Mage's Wand^35^^k
8ox|Cragwood Maul|q||h|||q^1383^Nothing But The Truth^37^h^k
8pj|Lesser Magic Wand|c|s||||c^Enchanting^10^14293^f
8pk|Greater Magic Wand|c|s||||c^Enchanting^70^14807^f
8pl|Lesser Mystic Wand|c|||||c^Enchanting^155^14809^f
8py|Uther's Strength|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
8pz|Fine Shortbow|v|s||||V^14846^3184^^s
8q0|Fine Longbow|v|s||||V^228^4861^^s
8q1|Dense Shortbow|v|s||||V^14846^25814^^s
8q2|Sturdy Recurve|v|s||||V^14846^19467^^s
8q3|Massive Longbow|v|s||||V^5122^67952^^s
8q4|Sylvan Shortbow|v|s||||V^14846^78828^^s
8q6|Flameseer Mantle|d|||||d^70^Galgann Firehammer^20^0^k
8q7|Emberscale Cape|d|s||||d^70^Galgann Firehammer^0^0^s
8ul|Bloodband Bracers|q|s||||q^614^The Captain's Chest^46^a^s~q^8551^The Captain's Chest^42^^s
8vi|Loreskin Shoulders|q||h|||q^864^Return to Apothecary Zinge^41^h^k
8yc|Dark Iron Plate|c|||||c^Blacksmithing^260^15296^f
8yd|Dark Iron Shoulders|c|||||c^Blacksmithing^255^15295^f
8ye|Dark Iron Mail|c|||||c^Blacksmithing^245^15293^f
8yf|Dark Iron Sunderer|c|||||c^Blacksmithing^250^15294^f
8yg|Dark Iron Pulverizer|c|||||c^Blacksmithing^240^15292^f
8yv|Spritecaster Cape|d|||||d^230^Houndmaster Grebmar^35^0^k
8yw|Kentic Amice|d|||||d^230^High Interrogator Gerstahn^25^0^k
8yx|Enthralled Sphere|d|||||d^230^High Interrogator Gerstahn^25^0^k
8yy|Blackveil Cape|d|||||d^230^High Interrogator Gerstahn^25^0^k
8yz|Fleetfoot Greaves|d|||||d^230^Houndmaster Grebmar^35^0^k
8z0|Houndmaster's Bow|d|||||d^230^Houndmaster Grebmar^15^0^k
8z1|Houndmaster's Rifle|d|||||d^230^Houndmaster Grebmar^15^0^k
8z3|Stoneshell Guard|d|||||d^230^Lord Roccor^25^0^k
8z4|Earthslag Shoulders|d|||||d^230^Lord Roccor^25^0^k
8z5|Spiderfang Carapace|w|||||m^9032^Hedrum the Creeper^35^k
8z6|Silkweb Gloves|w|||||m^9032^Hedrum the Creeper^35^k
8z7|Hookfang Shanker|w|||||m^9032^Hedrum the Creeper^15^k
8zy|Ban'thok Sash|w|||||m^9030^Ok'thor the Breaker^35^k
901|Ogreseer Fists|w|||||m^9030^Ok'thor the Breaker^35^k
905|Naglering|d|||||d^230^Golem Lord Argelmach^30.67^0^k
90b|Shadefiend Boots|w|||||m^9031^Anub'shiah^42.5^k
90d|Graverot Cape|w|||||m^9031^Anub'shiah^42.5^k
90e|Carapace of Anub'shiah|w|||||m^9031^Anub'shiah^15^k
90f|Rubicund Armguards|w|||||m^9029^Eviscerator^35^k
90k|Ironfoe|d|||||d^230^Emperor Dagran Thaurissan^1^0^k
90l|Splinthide Shoulders|w|||||m^9029^Eviscerator^35^k
90m|Girdle of Beastial Fury|w|||||m^9029^Eviscerator^15^k
912|Grizzle's Skinner|w|U||||m^9028^Grizzle^35^k
913|Stonewall Girdle|w|||||m^9028^Grizzle^35^k
91m|Dregmetal Spaulders|w|||||m^9028^Grizzle^15^k
91q|Savage Gladiator Chain|w|||||m^9027^Gorosh the Dervish^15^k
91s|Savage Gladiator Leggings|w|||||m^9030^Ok'thor the Breaker^15^k
91t|Savage Gladiator Helm|w|||||m^9032^Hedrum the Creeper^15^k
91u|Savage Gladiator Grips|w|||||m^9029^Eviscerator^15^k
91v|Savage Gladiator Greaves|w|||||m^9031^Anub'shiah^15^k
91z|Ragefury Eyepatch|d|||||d^230^Hurley Blackbreath^9^0^k
928|Bloodfist|d|||||d^230^Phalanx^33.33^0^k
929|Fists of Phalanx|d|||||d^230^Phalanx^33.33^0^k
92a|Golem Skull Helm|d|||||d^230^Magmus^20^0^k
92b|Flamestrider Robes|d|||||d^230^Pyromancer Loregrain^26.67^0^k
92c|Pyric Caduceus|d|||||d^230^Pyromancer Loregrain^26.67^0^k
92d|Searingscale Leggings|d|||||d^230^Pyromancer Loregrain^26.67^0^k
92e|Kindling Stave|d|||||d^230^Pyromancer Loregrain^20^0^k
92j|Verek's Collar|d|||||d^230^^12^0^k
93a|Boreal Mantle|d|||||d^230^Warder Stilgiss^25^0^k
93b|Chillsteel Girdle|d|||||d^230^Warder Stilgiss^25^0^k
93c|Arbiter's Blade|d|||||d^230^Warder Stilgiss^25^0^k
93d|Rock Golem Bulwark|d|||||d^230^^25^0^k
93e|Stone of the Earth|d|||||d^230^^25^0^k
93f|Shalehusk Boots|d|||||d^230^^25^0^k
93u|Lavacrest Leggings|d|||||d^230^Bael'Gar^32^0^k
93v|Force of Magma|d|||||d^230^Bael'Gar^32^0^k
93x|Rubidium Hammer|d|||||d^230^Bael'Gar^18^0^k
93z|Sash of the Burning Heart|d|||||d^230^Bael'Gar^18^0^k
941|Flame Wrath|d|||||d^230^Ambassador Flamelash^20^0^k
942|Force of Will|d|||||d^230^General Angerforge^20^0^k
944|Cape of the Fire Salamander|d|||||d^230^Ambassador Flamelash^31^0^k
946|Molten Fists|d|||||d^230^Ambassador Flamelash^31^0^k
947|Hand of Justice|d|||||d^230^Emperor Dagran Thaurissan^19.8^0^k
948|Angerforge's Battle Axe|d|||||d^230^General Angerforge^20^0^k
949|Lord General's Sword|d|||||d^230^General Angerforge^20^0^k
94b|Second Wind|d|||||d^230^Golem Lord Argelmach^8^0^k
94c|Royal Decorated Armor|d|||||d^230^General Angerforge^20^0^k
94d|Warstrife Leggings|d|||||d^230^General Angerforge^20^0^k
94e|Omnicast Boots|d|||||d^230^Golem Lord Argelmach^30.67^0^k
94f|Luminary Kilt|d|||||d^230^Golem Lord Argelmach^30.67^0^k
94g|Cyclopean Band|w|||||m^9030^Ok'thor the Breaker^15^k
94o|Burst of Knowledge|d|||||d^230^Ambassador Flamelash^17^0^k
94v|Chief Architect's Monocle|d|||||d^230^Fineous Darkvire^25^0^k
94x|Senior Designer's Pantaloons|d|||||d^230^Fineous Darkvire^25^0^k
94y|Lead Surveyor's Mantle|d|||||d^230^Fineous Darkvire^25^0^k
953|Battered Cloak|q||h|3070||q^364^The Mindless Ones^1^h^s
954|Flax Belt|q|s|h|||q^3902^Scavenging Deathknell^2^h^s
955|Rustmetal Bracers|q|s|h|||q^3902^Scavenging Deathknell^2^h^s
956|Short Duskbat Cape|q||h|6185||q^3902^Scavenging Deathknell^2^h^s
957|Scavenger Tunic|q||h|60||q^3901^Rattling the Rattlecages^1^h^s
958|Roamer's Leggings|q|s|h|||q^3901^Rattling the Rattlecages^1^h^s
959|Rambling Boots|q|s|h|||q^3281^Stolen Silver^13^h^s
95a|Samophlange Screwdriver|q|s|h|||q^3924^Samophlange Manual^14^h^s
95b|Tork Wrench|q|s|h|||q^3924^Samophlange Manual^14^h^s
95c|Ceremonial Elven Blade|q||a|||q^4266^A Hero's Welcome^41^a^k
95d|Sanctimonial Rod|q||a|||q^4266^A Hero's Welcome^41^a^k
95e|Battlehard Cape|q||h|||q^2976^A Grim Discovery^40^h^k
95f|Jademoon Orb|q||h|||q^2976^A Grim Discovery^40^h^k
95g|Charged Lightning Rod|q|||||q^4450^Ledger from Tanaris^43^^k
95h|Girdle of Reprisal|q|||||q^4450^Ledger from Tanaris^43^^k
95i|White Bone Band|q||h|||q^4300^Bone-Bladed Weapons^48^h^k
95j|White Bone Shredder|q||h|||q^4300^Bone-Bladed Weapons^48^h^k
95k|White Bone Spear|q||h|||q^4300^Bone-Bladed Weapons^48^h^k
95l|Rancor Boots|Q|||||q^4136^Ribbly Screwspigot^48^^k
95m|Nagmara's Whipping Belt|Q|||||q^4201^The Love Potion^50^^k
95n|Maddening Gauntlets|q||a|||q^3825^Ogre Head On A Stick = Party^48^a^k
95o|Choking Band|q||a|||q^3825^Ogre Head On A Stick = Party^48^a^k
95p|Sha'ni's Ring|q||h|10739||q^3822^Krom'Grul^48^h^k
95q|Oblivion Orb|q|||||q^4510^Calm Before the Storm^50^a^k~q^4511^Calm Before the Storm^50^h^k
95r|Snarkshaw Spaulders|q|||||q^4510^Calm Before the Storm^50^a^k~q^4511^Calm Before the Storm^50^h^k
95s|Eschewal Greaves|q|||||q^4510^Calm Before the Storm^50^a^k~q^4511^Calm Before the Storm^50^h^k
95u|Clouddrift Mantle|q||a|||q^4261^Ancient Spirit^51^a^k
95w|Plainstalker Tunic|q|||||q^4292^The Bait for Lar'korwi^51^^k
962|Outrider Leggings|q|||||q^4292^The Bait for Lar'korwi^51^^k
964|Moonlit Amice|q|s|a|||q^1440^Return to Vahlarriel^30^a^s
968|Quintis' Research Gloves|q||a|||q^3791^The Mystery of Morrowgrain^47^a^k
969|Bark Iron Pauldrons|q||a|||q^3791^The Mystery of Morrowgrain^47^a^k
96m|Linken's Sword of Mastery|q|||||q^3962^It's Dangerous to Go Alone^51^^k
96o|Spirit of Aquementas|q|||||q^3962^It's Dangerous to Go Alone^51^^k
96q|Beastsmasher|q|||||q^4301^The Mighty U'cha^50^^k
96r|Beastslayer|q|||||q^4301^The Mighty U'cha^50^^k
96s|Archaeologist's Quarry Boots|q|||||q^3882^Roll the Bones^49^^k
96t|Excavator's Utility Belt|q|||||q^3882^Roll the Bones^49^^k
96u|Bejeweled Legguards|q|||||q^4491^A Little Help From My Friends^50^^k
96v|Treetop Leggings|q|||||q^4491^A Little Help From My Friends^50^^k
96x|Clayridge Helm|q|||||q^4491^A Little Help From My Friends^50^^k
96z|Shizzle's Drizzle Blocker|q|||||q^4503^Shizzle's Flyer^49^^k
970|Shizzle's Muzzle|q|||||q^4503^Shizzle's Flyer^49^^k
971|Shizzle's Nozzle Wiper|q|||||q^4503^Shizzle's Flyer^49^^k
972|Grotslab Gloves|q|||||q^4501^Beware of Pterrordax^50^^k
973|Cragplate Greaves|q|||||q^4501^Beware of Pterrordax^50^^k
974|Wraith Scythe|w|||||o^Chest of The Seven^25^k
975|Impervious Giant|w|||||o^Chest of The Seven^25^k
976|Blood-Etched Blade|w|||||o^Chest of The Seven^25^k
978|Robes of the Royal Crown|d|||||d^230^Emperor Dagran Thaurissan^20^0^k
979|Ghostshroud|w|||||o^Chest of The Seven^25^k
97a|Deathdealer Breastplate|w|||||o^Chest of The Seven^25^k
97b|Legplates of the Eternal Guardian|w|||||o^Chest of The Seven^25^k
97c|Thaurissan's Royal Scepter|d|||||d^230^Emperor Dagran Thaurissan^20^0^k
97d|Haunting Specter Leggings|w|||||o^Chest of The Seven^25^k
97e|The Emperor's New Cape|d|||||d^230^Emperor Dagran Thaurissan^19.8^0^k
97f|Dreadforge Retaliator|d|||||d^230^Emperor Dagran Thaurissan^19.8^0^k
97g|Guiding Stave of Wisdom|d|||||d^230^Emperor Dagran Thaurissan^20^0^k
97h|Imperial Jewel|d|||||d^230^Emperor Dagran Thaurissan^19.8^0^k
97j|Magmus Stone|d|||||d^230^Magmus^20^0^k
97k|Relic Hunter Belt|q|s|a|||q^741^The Absent Minded Prospector^15^a^s
98a|Manacle Cuffs|Q|||||q^4201^The Love Potion^50^^k
98b|Penance Spaulders|Q|||||q^4136^Ribbly Screwspigot^48^^k
98c|Swiftstrike Cudgel|Q|||||q^4126^Hurley Blackbreath^50^a^k~q^4134^Lost Thunderbrew Recipe^50^h^k
99c|Limb Cleaver|Q|||||q^4126^Hurley Blackbreath^50^a^k~q^4134^Lost Thunderbrew Recipe^50^h^k
99u|Conservator Helm|Q||a|||q^4242^Abandoned Hope^49^a^k
99x|Shieldplate Sabatons|Q||a|||q^4242^Abandoned Hope^49^a^k
9ae|Lagrave's Seal|Q||h|||q^7201^The Last Element^49^h^k
9ah|Windshear Leggings|Q||a|||q^4242^Abandoned Hope^49^a^k
9ap|Splintsteel Armor|Q|||||q^4136^Ribbly Screwspigot^48^^k
9ar|Brazen Gauntlets|q||a|||q^4513^A Little Slime Goes a Long Way^49^a^k
9as|Ring of the Moon|dwx|s||||m^580^Redridge Drudger^0^s~d^36^Rhahk'Zor^0.07^0^k
9at|Volcanic Rock Ring|dwx|s||||d^36^Cookie^9.52^0^s~d^36^Edwin VanCleef^0^0^s
9au|Demon Band|dwx|s||||d^34^Targorr the Dread^5^0^s~m^1040^Fen Creeper^0^s
9av|Stardust Band|dwx|||||d^349^Princess Theradras^0.19^0^k
9aw|Ring of the Heavens|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.03^0^k
9ax|Dragonscale Band|dwx|||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Darkmaster Gandling^0.05^0^k
9ay|Demonic Bone Ring|drwx|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
9az|Conqueror's Medallion|Q||h|||q^4132^Operation: Death to Angerforge^53^h^k
9b1|Blade of Reckoning|Q||a|||q^4322^Jail Break!^53^a^k
9b2|Skilled Fighting Blade|Q||a|||q^4322^Jail Break!^53^a^k
9b6|Shaleskin Cape|Q|||||q^4024^A Taste of Flame^53^^k
9bm|Wyrmhide Spaulders|Q|||||q^4024^A Taste of Flame^53^^k
9bn|Valconian Sash|Q|||||q^4024^A Taste of Flame^53^^k
9c6|Ring of the Aristocrat|q||a|||q^3701^The Smoldering Ruins of Thaurissan^50^a^k
9c7|Star of Mystaria|d|||||d^329^Balnazzar^20^0^k
9cc|Basaltscale Armor|Q||h|||q^4063^The Rise of the Machines^53^h^k
9cd|Azure Moon Amice|Q||h|||q^4063^The Rise of the Machines^53^h^k
9ce|Raincaster Drape|Q||h|||q^4063^The Rise of the Machines^53^h^k
9cf|Lavaplate Gauntlets|Q||h|||q^4063^The Rise of the Machines^53^h^k
9cg|Crypt Demon Bracers|Q|||||q^3907^Disharmony of Fire^51^h^k~q^4263^Incendius!^51^a^k
9ch|Sunborne Cape|Q|||||q^3907^Disharmony of Fire^51^h^k~q^4263^Incendius!^51^a^k
9ci|Nightfall Gloves|Q|||||q^3907^Disharmony of Fire^51^h^k~q^4263^Incendius!^51^a^k
9cj|Stalwart Clutch|Q|||||q^3907^Disharmony of Fire^51^h^k~q^4263^Incendius!^51^a^k
9g3|Smoldering Claw|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
9g7|Broad Bladed Knife|v|s||||V^225^28372^^s
9g8|Daring Dirk|v|s||||V^14846^32029^^s
9g9|Merciless Axe|v|s||||V^225^30195^^s
9ga|Midnight Axe|v|sr||||V^4884^40341^^s
9gb|Big Stick|v|s||||V^14846^53896^^s
9gc|Staff of Protection|v|||||V^2482^63095^^k
9gd|Brilliant Red Cloak|v|||||V^11874^17728^^k
9ge|Well Oiled Cloak|v|s||||V^12023^22416^^s
9gf|Pale Leggings|v|s|h|||V^3315^34987^h^s
9gg|Cindercloth Leggings|v|s||||V^3316^43828^^s
9gj|Glinting Steel Dagger|c|||||c^Blacksmithing^180^15972^f
9gk|Searing Golden Blade|c|||||c^Blacksmithing^165^15973^f
9hj|Leggings of the People's Militia|q|s|a|||q^153^Red Leather Bandanas^10^a^s
9hk|Spark of the People's Militia|q|s|a|||q^14^The People's Militia^12^a^s
9hn|Netted Gloves|q|s|h|||q^374^Proof of Demise^5^h^s
9kl|Thorium Armor|c|||||c^Blacksmithing^225^16642^f
9km|Thorium Belt|c|||||c^Blacksmithing^225^16643^f
9kq|Thorium Helm|c|||||c^Blacksmithing^255^16653^f
9l2|Imperial Plate Chest|c|||||c^Blacksmithing^275^16663^f
9l4|Imperial Plate Belt|c|||||c^Blacksmithing^240^16647^f
9l5|Imperial Plate Bracers|c|||||c^Blacksmithing^245^16649^f
9l7|Imperial Plate Helm|c|||||c^Blacksmithing^270^16658^f
9l8|Imperial Plate Shoulders|c|||||c^Blacksmithing^240^16646^f
9l9|Imperial Plate Leggings|c|||||c^Blacksmithing^280^16730^f
9m6|Embrace of the Wind Serpent|d|||||d^109^Avatar of Hakkar^0.5^0^k
9m7|Drakefang Butcher|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
9m8|Bloodfire Talons|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
9m9|Nightfall Drape|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
9ma|Dawnspire Cord|d|||||d^109^Hazzas^6.25^0^k~d^109^Morphaz^6.25^0^k
9me|Sandstalker Ankleguards|d|||||d^209^^18.69^0^k
9mf|Desertwalker Cane|d|||||d^209^^18.55^0^k
9nu|Bingles' Flying Gloves|q|s|a|||q^2038^Bingles' Missing Supplies^12^a^s
9nz|Ribsplitter|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9o0|The Judge's Gavel|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9o3|Searing Needle|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9o4|Spire of the Stoneshaper|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9o7|Doomforged Straightedge|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9oe|Funeral Pyre Vestment|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9of|Songstone of Ironforge|Q||a|12545||q^4363^The Princess's Surprise^54^a^k
9og|Thrall's Resolve|Q||h|||q^4004^The Princess Saved?^55^h^k
9oh|Eye of Orgrimmar|Q||h|12543||q^4004^The Princess Saved?^55^h^k
9oi|Aristocratic Cuffs|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9oj|Mar Alom's Grip|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9ok|Magni's Will|Q||a|||q^4363^The Princess's Surprise^54^a^k
9ol|Braincage|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9om|Runed Golem Shackles|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9on|Stoneshield Cloak|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9oo|Blisterbane Wrap|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9op|Swiftwalker Boots|d|||||d^230^Princess Moira Bronzebeard^25^0^k
9oq|Hands of the Exalted Herald|d|||||d^230^Princess Moira Bronzebeard^25^0^k
9or|Battlechaser's Greaves|dw|||||d^230^Golem Lord Argelmach^0.02^0^k~d^230^Bael'Gar^0.02^0^k
9ot|Ebonsteel Spaulders|d|||||d^230^Princess Moira Bronzebeard^25^0^k
9pk|Grand Marshal's Longsword|p||a|16345||p^14^a^f
9pn|Eye of Rend|d|||||d^229^Warchief Rend Blackhand^16.67^0^k
9pp|Dustfeather Sash|w|||||m^10264^Solakar Flamewreath^20^k
9pq|Felstriker|d|||||d^229^Warchief Rend Blackhand^1^0^k
9ps|Blackblade of Shahram|d|||||d^229^General Drakkisath^1^0^k
9q2|Draconian Deflector|d|||||d^229^General Drakkisath^24.75^0^k
9q3|Nightbrace Tunic|w|||||m^10264^Solakar Flamewreath^20^k
9q4|Starfire Tiara|d|||||d^229^^33.33^0^k
9q5|Serpentine Skuller|d|||||d^229^^33.33^0^k
9q6|Crystallized Girdle|w|||||m^10264^Solakar Flamewreath^20^k
9q8|Butcher's Apron|d|||||d^229^^50^0^k
9qi|Enchanted Thorium Breastplate|c|||||c^Blacksmithing^300^16745^f
9qj|Enchanted Thorium Leggings|c|||||c^Blacksmithing^300^16744^f
9qk|Enchanted Thorium Helm|c|||||c^Blacksmithing^300^16742^f
9ql|Demonfork|d|||||d^229^^33.33^0^k
9qo|Wildthorn Mail|c|||||c^Leatherworking^245^16650^f
9qp|Dawnbringer Shoulders|c|||||c^Blacksmithing^265^16660^f
9qq|Funeral Cuffs|d|||||d^229^Shadow Hunter Vosh'gajin^21^0^k
9qs|Demon Forged Breastplate|c|||||c^Blacksmithing^260^16667^f
9qv|Fiery Plate Gauntlets|cq|||||c^Blacksmithing^265^16655^f~q^5124^Fiery Plate Gauntlets^55^^k
9qw|Storm Gauntlets|c|||||c^Leatherworking^270^16661^f
9qx|Whitesoul Helm|c|||||c^Blacksmithing^290^16724^f
9qy|Chiselbrand Girdle|d|||||d^229^^33.33^0^k
9r1|Backusarian Gauntlets|d|||||d^229^^33.33^0^k
9r3|Stronghold Gauntlets|c|||||c^Blacksmithing^300^16741^f
9r4|Lionheart Helm|c|||||c^Blacksmithing^300^16729^f
9rf|Blackcrow|d|||||d^229^Shadow Hunter Vosh'gajin^8^0^k
9rh|Riphook|d|||||d^229^Shadow Hunter Vosh'gajin^8^0^k
9t1|Pip's Skinner|d|||||d^229^The Beast^20^0^k
9uk|Thorium Greatsword|c|||||c^Blacksmithing^260^16960^f
9up|Bleakwood Hew|c|||||c^Blacksmithing^270^16965^f
9us|Inlaid Thorium Hammer|c|||||c^Blacksmithing^270^16967^f
9ut|Ornate Thorium Handaxe|c|||||c^Blacksmithing^250^16969^f
9uu|Dawn's Edge|c|||||c^Blacksmithing^250^16970^f
9uw|Enchanted Battlehammer|c|||||c^Blacksmithing^255^16973^f
9ux|Blazing Rapier|c|||||c^Blacksmithing^255^16978^f
9v1|Serenity|c|||||c^Blacksmithing^260^16983^f
9v2|Corruption|c|||||c^Blacksmithing^265^16985^f
9v3|Heartseeker|c|||||c^Blacksmithing^300^16995^f
9v4|Arcanite Reaper|c|||||c^Blacksmithing^300^16994^f
9vb|Barman Shanker|d|||||d^230^Plugger Spazzring^33.33^0^k
9vc|Volcanic Hammer|c|r||||c^Blacksmithing^265^16984^f
9vd|Mixologist's Tunic|d|||||d^230^Plugger Spazzring^33.33^0^k
9ve|Masterwork Stormhammer|c|||||c^Blacksmithing^300^16993^f
9vf|Blood Talon|c|||||c^Blacksmithing^325^16986^f
9vg|Hammer of the Titans|c|||||c^Blacksmithing^300^16988^f
9vh|Frostguard|c|||||c^Blacksmithing^300^16992^f
9vi|Annihilator|c|||||c^Blacksmithing^300^16991^f
9vm|Darkspear|c|||||c^Blacksmithing^325^16987^f
9y7|Breastplate of the Chromatic Flight|Q|||||q^5166^Breastplate of the Chromatic Flight^57^^k
9yf|Legguards of the Chromatic Defier|Q|||||q^5167^Legplates of the Chromatic Defier^57^^k
9z2|Flaming Band|d|||||d^229^Pyroguard Emberseer^20^0^k
9z3|Truestrike Shoulders|d|||||d^229^Pyroguard Emberseer^20^0^k
9z5|Emberfury Talisman|d|||||d^229^Pyroguard Emberseer^20^0^k
9zb|Warmaster Legguards|d|||||d^229^Warchief Rend Blackhand^19.8^0^k
9zc|Battleborn Armbraces|d|||||d^229^Warchief Rend Blackhand^19.8^0^k
9zf|Dal'Rend's Tribal Guardian|d|||||d^229^Warchief Rend Blackhand^19.8^0^k
9zg|Dal'Rend's Sacred Charge|d|||||d^229^Warchief Rend Blackhand^16.67^0^k
9zl|Legplates of the Chromatic Defier|Q|||||q^5167^Legplates of the Chromatic Defier^57^^k
9zs|Gyth's Skull|w|||||m^10339^Gyth^20^k
9zt|Dragoneye Coif|w|||||m^10339^Gyth^20^k
a00|Tribal War Feathers|w|||||m^10339^Gyth^20^k
a03|Blademaster Leggings|d|||||d^229^The Beast^20^0^k
a04|Tristam Legguards|d|||||d^229^The Beast^20^0^k
a05|Spiritshroud Leggings|d|||||d^229^The Beast^20^0^k
a06|Blackmist Armguards|d|||||d^229^The Beast^20^0^k
a07|Bloodmoon Cloak|d|||||d^229^The Beast^20^0^k
a08|Frostweaver Cape|d|||||d^229^The Beast^20^0^k
a0e|The Black Knight|x|||||x^4634^Iron Lockbox^k
a0f|Prospector Axe|dw|s||||d^36^^0^0^s~m^485^Blackrock Outrunner^0^s
a0g|Ironpatch Blade|w|s||||m^5763^Nightmare Ectoplasm^0^s
a0h|Magefist Gloves|w|s||||m^2261^Syndicate Watchman^0^s
a0i|Stormbringer Belt|w|s||||w^0^0^k
a0j|Firebane Cloak|dw|s||||d^43^Skum^25^0^s~m^3674^Skum^0^s
a0m|Silver-linked Footguards|w|s||||m^3928^Rotting Slime^0^s~m^2260^Syndicate Rogue^0^s
a0n|Rakzur Club|w|||||w^0^0^k
a0o|Skycaller|w|s||||m^485^Blackrock Outrunner^0^s
a0p|Ring of Defense|w|U||||w^0^0^k
a0r|Darkweave Breeches|w|||||w^0^0^k
a0s|Starsight Tunic|w|s||||w^0^0^k
a0t|Gargoyle's Bite|w|s||||m^2354^Vicious Gray Bear^0^s~m^3457^Razormane Stalker^0^s
a0u|Razor's Edge|w|s||||m^3434^Nak^0^s
a0w|Searing Blade|w|||||w^0^0^k
a0y|Thorbia's Gauntlets|w|||||w^0^0^k
a10|Band of Purification|wx|sU||||m^202^Skeletal Horror^0^s
a11|Redbeard Crest|wx|||||x^4632^Ornate Bronze Lockbox^k~w^0^0^k
a12|Magician's Mantle|w|||||w^0^0^k
a13|Drakewing Bands|w|||||w^0^0^k
a14|Staff of Hale Magefire|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a15|Maiden's Circle|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a16|Lady Alizabeth's Pendant|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a17|Lord Alexander's Battle Axe|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a18|Torch of Austen|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a19|Amy's Blanket|w|||||w^0^0^k
a1a|Mass of McGowan|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1b|Mageflame Cloak|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1c|Dalewind Trousers|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1d|Cow King's Hide|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1e|Dreamsinger Legguards|wx|s||||x^4633^Heavy Bronze Lockbox^k~x^21510^Ahn'Qiraj War Effort Supplies^k
a1f|Silver-lined Belt|w|||||w^0^0^k
a1g|Yorgen Bracers|w|s||||m^3377^Bael'dun Rifleman^0^s
a1h|Elder Wizard's Mantle|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1i|Axe of Rin'ji|x|||||x^5758^Mithril Lockbox^k
a1j|Serathil|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a1k|Killmaim|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
a1l|Hellslayer Battle Axe|w|||||w^0^0^k
a1m|Executioner's Cleaver|w|||||w^0^0^k
a1n|Harpyclaw Short Bow|x|||||x^4634^Iron Lockbox^k
a1o|Skystriker Bow|wx|s||||m^258042^NPC 258042^0^s
a1p|Needle Threader|w|||||w^0^0^k
a1q|Gryphonwing Long Bow|x|||||x^5758^Mithril Lockbox^k
a1r|Eaglehorn Long Bow|w|||||w^0^0^k
a1s|Beazel's Basher|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
a1t|Deadwood Sledge|wx|||||x^6827^Box of Supplies^k~w^0^0^k
a1u|Heaven's Light|w|||||w^0^0^k
a1v|Bonesnapper|x|||||x^5758^Mithril Lockbox^k~x^10752^Emerald Encrusted Chest^k
a1w|Bludstone Hammer|w|||||w^0^0^k
a1x|Umbral Crystal|wx|||||x^4637^Steel Lockbox^k~x^21512^Ahn'Qiraj War Effort Supplies^k
a1z|Orb of Mistmantle|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
a20|Sword of Corruption|wx|s||||m^7603^Leprous Assistant^0^s
a21|Zealot Blade|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
a22|Speedsteel Rapier|w|||||w^0^0^k
a23|Serpent Slicer|w|||||w^0^0^k
a24|Assassination Blade|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a25|Crystalpine Stinger|x|||||x^4634^Iron Lockbox^k
a26|Swiftwind|w|||||w^0^0^k
a27|Skull Splitting Crossbow|w|||||w^0^0^k
a28|Heartseeking Crossbow|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a29|Guardian Blade|w|||||w^0^0^k
a2a|Sword of the Magistrate|w|||||w^0^0^k
a2b|Blade of the Titans|w|||||w^0^0^k
a2c|Demonslayer|dwx|||||d^289^Darkmaster Gandling^0.01^0^k~m^11447^Mushgog^5.19^k
a2d|Viscous Hammer|wx|||||x^4634^Iron Lockbox^k~x^6827^Box of Supplies^k
a2e|Blanchard's Stout|rw|||||d^249^Onyxia^2.52^1^k~m^15816^Qiraji Major He'al-ie^4^k
a2f|Twig of the World Tree|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a2g|Looming Gavel|x|s||||x^4634^Iron Lockbox^k~x^4637^Steel Lockbox^k
a2h|Deanship Claymore|w|||||w^0^0^k
a2j|Witchfury|w|s||||m^7397^Earthen Stonecarver^0^s
a2k|Warmonger|wx|||||x^5758^Mithril Lockbox^k~w^0^0^k
a2l|Doombringer|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a2n|Bonechewer|wx|||||x^4638^Reinforced Steel Lockbox^k~w^0^0^k
a2o|Frenzied Striker|dx|||||d^289^Darkmaster Gandling^0.04^0^k
a2p|Bloodpike|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
a2q|Khoo's Point|w|||||w^0^0^k
a2r|Stoneraven|wx|||||x^5758^Mithril Lockbox^k~w^0^0^k
a2s|The Needler|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a2u|Thunderwood|w|s||||w^0^0^k
a2v|Starfaller|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
a2w|Jaina's Firestarter|wx|s||||x^4637^Steel Lockbox^k~w^0^0^k
a2x|Wand of Allistarj|rw|||||d^249^Onyxia^2.52^1^k~m^15816^Qiraji Major He'al-ie^4^k
a2y|Wyrmslayer Spaulders|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a2z|Hydralick Armor|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a30|Obsidian Greaves|wx|||||x^4637^Steel Lockbox^k~w^0^0^k
a32|Sapphiron's Scale Boots|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a33|Plated Fist of Hakoo|w|||||w^0^0^k
a34|Stonegrip Gauntlets|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a35|Mugthol's Helm|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a36|Golem Shard Leggings|wx|||||x^10752^Emerald Encrusted Chest^k~w^0^0^k
a37|Direwing Legguards|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a38|Giantslayer Bracers|w|||||w^0^0^k
a39|Girdle of Uther|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a3b|Shield of Thorsen|wx|s||||m^4664^Burning Blade Reaver^0^s
a3d|Skullance Shield|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a3e|Mountainside Buckler|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10752^Emerald Encrusted Chest^k
a3f|Garrett Family Crest|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a3g|Kaleidoscope Chain|wx|||||x^4634^Iron Lockbox^k~x^6827^Box of Supplies^k
a3h|Horizon Choker|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a3j|River Pride Choker|wx|s||||x^4634^Iron Lockbox^k~w^0^0^k
a3k|Gazlowe's Charm|wx|||||x^4637^Steel Lockbox^k~w^0^0^k
a3l|Skibi's Pendant|wx|||||x^4638^Reinforced Steel Lockbox^k~w^0^0^k
a3n|Medallion of Grand Marshal Morris|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a3p|Blush Ember Ring|wx|U||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a3q|The Queen's Jewel|w|sU||||m^4142^Sparkleshell Tortoise^0^s
a3r|Assault Band|wx|sU||||m^4331^Firemane Ash Tail^0^s
a3s|Band of the Hierophant|rwx|U||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a3t|Thunderbrow Ring|w|U||||w^0^0^k
a3u|Painweaver Band|d|||||d^229^General Drakkisath^24.75^0^k
a3v|Moccasins of the White Hare|w|||||w^0^0^k
a3w|Furen's Boots|wx|||||x^4637^Steel Lockbox^k~w^0^0^k
a3x|Wolfrunner Shoes|dwx|||||d^289^Darkmaster Gandling^0.01^0^k~m^11447^Mushgog^5.19^k
a3y|Cassandra's Grace|wx|||||x^10752^Emerald Encrusted Chest^k~w^0^0^k
a3z|Pads of the Venom Spider|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a41|Sutarn's Ring|wx|||||x^6827^Box of Supplies^k~w^0^0^k
a42|Glowing Magical Bracelets|x|||||x^4634^Iron Lockbox^k
a43|Magiskull Cuffs|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a44|Tigerstrike Mantle|w|||||w^0^0^k
a45|Blackflame Cape|wx|||||x^4638^Reinforced Steel Lockbox^k~x^10752^Emerald Encrusted Chest^k
a46|Wolffear Harness|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a47|Sandals of the Insurgent|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a48|Winged Helm|wx|||||x^10752^Emerald Encrusted Chest^k~w^0^0^k
a49|Feathermoon Headdress|rwx|||||d^249^Onyxia^2.52^1^k~m^11447^Mushgog^5.19^k
a4a|Troll's Bane Leggings|wx|||||x^4633^Heavy Bronze Lockbox^k~w^0^0^k
a4b|Sheepshear Mantle|wx|s||||x^4637^Steel Lockbox^k~w^0^0^k
a4c|Spaulders of the Unseen|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4d|Ogron's Sash|wx|||||x^4637^Steel Lockbox^k~x^6354^Small Locked Chest^k
a4e|Serpentine Sash|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4f|Enchanted Kodo Bracers|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a4g|Deepfury Bracers|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4h|Wing of the Whelpling|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a4i|Dark Phantom Cape|x|||||x^5758^Mithril Lockbox^k~x^10752^Emerald Encrusted Chest^k
a4j|Dreamwalker Armor|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4k|Ravasaur Scale Boots|wx|||||x^4634^Iron Lockbox^k~x^6827^Box of Supplies^k
a4l|Elven Chain Boots|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4m|Battlecaller Gauntlets|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4n|Frostreaver Crown|x|||||x^4634^Iron Lockbox^k
a4o|High Bergg Helm|wx|||||x^10752^Emerald Encrusted Chest^k~w^0^0^k
a4p|Firemane Leggings|wx|||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
a4q|Windrunner Legguards|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4r|Sparkleshell Mantle|wx|||||x^4633^Heavy Bronze Lockbox^k~x^21510^Ahn'Qiraj War Effort Supplies^k
a4s|Skeletal Shoulders|w|||||w^0^0^k
a4t|Drakesfire Epaulets|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4u|Belt of the Gladiator|wx|||||x^10752^Emerald Encrusted Chest^k~w^0^0^k
a4v|Lordly Armguards|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a4w|Lil Timmy's Peashooter|w|s||||m^626^Foreman Thistlenettle^0^s
a4x|Ironweaver|wx|||||x^4634^Iron Lockbox^k~w^0^0^k
a4y|The Silencer|w|||||w^0^0^k
a4z|Guttbuster|rw|||||d^249^Onyxia^2.52^1^k~m^15816^Qiraji Major He'al-ie^4^k
a51|Tooth of Gnarr|d|||||d^229^General Drakkisath^24.75^0^k
a52|Brigam Girdle|d|||||d^229^General Drakkisath^24.75^0^k
a54|Serenity Belt|rwx|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a55|Enormous Ogre Belt|wx|||||x^10569^Hoard of the Black Dragonflight^k~x^19297^Lesser Darkmoon Prize^k
a56|Shell Launcher Shotgun|rw|||||d^249^Onyxia^2.52^1^k~m^15740^Colossus of Zora^10^k
a5l|Trindlehaven Staff|d|||||d^229^Overlord Wyrmthalak^20^0^k
a5m|Reiver Claws|d|||||d^229^Overlord Wyrmthalak^20^0^k
a5n|Relentless Scythe|d|||||d^229^Overlord Wyrmthalak^20^0^k
a5q|Slamshot Shoulders|d|||||d^229^Highlord Omokk^16.67^0^k
a5r|Fist of Omokk|d|||||d^229^Highlord Omokk^16.67^0^k
a5s|Plate of the Shaman King|d|||||d^229^Highlord Omokk^16.67^0^k
a5t|Tressermane Leggings|d|||||d^229^Highlord Omokk^16.67^0^k
a5u|Skyshroud Leggings|d|||||d^229^Highlord Omokk^16.67^0^k
a61|Talisman of Evasion|d|||||d^229^War Master Voone^20^0^k
a62|Rosewine Circle|d|||||d^229^Urok Doomhowl^25^0^k
a63|Brazecore Armguards|d|||||d^229^War Master Voone^20^0^k
a65|Demonskin Gloves|w|||||m^10263^Burning Felguard^50^k
a66|Phase Blade|w|||||m^10263^Burning Felguard^50^k
a68|Fallbrush Handgrips|d|||||d^229^^33.33^0^k
a6n|Crushridge Bindings|w|||||w^0^0^k
a6r|Armswake Cloak|d|||||d^229^^33.33^0^k
a6s|Bashguuder|d|||||d^229^^33.33^0^k
a6t|Rhombeard Protector|d|||||d^229^Gizrul the Slavener^28.33^0^k
a6w|Bleak Howler Armguards|d|||||d^229^Gizrul the Slavener^28.33^0^k
a6y|Pads of the Dread Wolf|d|||||d^229^Halycon^14^0^k
a6z|Slashclaw Bracers|d|||||d^229^Halycon^28.67^0^k
a70|Halycon's Spiked Collar|d|||||d^229^Halycon^28.67^0^k
a71|Smolderweb's Eye|d|||||d^229^Mother Smolderweb^35^0^k
a74|Crown of the Penitent|Q|||||q^5243^Houses of the Holy^55^^k
a75|Band of the Penitent|Q|||||q^5243^Houses of the Holy^55^^k
a7v|Argent Defender|q|||||q^5265^The Argent Hold^55^^k
a7w|Gilded Gauntlets|d|||||d^229^Mother Smolderweb^35^0^k
a7x|Kresh's Back|d|s||||d^43^Kresh^77.78^0^s
a7y|Argent Avenger|q|||||q^5265^The Argent Hold^55^^k
a81|Argent Crusader|q|||||q^5265^The Argent Hold^55^^k
a84|Cloudrunner Girdle|d|||||d^229^Quartermaster Zigris^16^0^k
a85|Hands of Power|d|||||d^229^Quartermaster Zigris^14^0^k
a89|Demonic Runed Spaulders|d|||||d^229^Shadow Hunter Vosh'gajin^21^0^k
a8b|Ribsteel Footguards|d|||||d^229^Urok Doomhowl^25^0^k
a8d|Globe of D'sak|d|||||d^229^^33.33^0^k
a8y|Ogreseer Tower Boots|d|||||d^229^^33.33^0^k
a8z|Magus Ring|d|||||d^229^^33.33^0^k
a90|Swiftdart Battleboots|d|||||d^229^^40^0^k
a92|Rivenspike|d|||||d^229^^50^0^k
a9u|Alanna's Embrace|d|||||d^289^Ras Frostwhisperer^2^0^k
aak|Cape of the Black Baron|d|||||d^329^Baron Rivendare^14.14^0^k
aao|Dracorian Gauntlets|d|||||d^329^Baron Rivendare^14.14^0^k
aaq|Robes of the Exalted|d|||||d^329^Baron Rivendare^14.14^0^k
aat|Scepter of the Unholy|d|||||d^329^Baron Rivendare^14.14^0^k
aax|Book of the Dead|d|||||d^329^Balnazzar^1^0^k
ab2|Wyrmtongue Shoulders|d|||||d^329^Balnazzar^19.8^0^k
ab3|Crown of Tyranny|d|||||d^329^Balnazzar^20^0^k
ab4|Gift of the Elven Magi|d|||||d^329^Balnazzar^19.8^0^k
abc|Bonescraper|d|||||d^329^Baron Rivendare^14.14^0^k
abd|Fire Striders|d|||||d^329^Balnazzar^20^0^k
abg|Slavedriver's Cane|d|||||d^329^Ramstein the Gorger^14.67^0^k
abh|Band of Flesh|d|||||d^329^Ramstein the Gorger^14.67^0^k
abi|Soulstealer Mantle|d|||||d^329^Ramstein the Gorger^14.67^0^k
abj|Crest of Retribution|d|||||d^329^Ramstein the Gorger^14.67^0^k
abk|Royal Tribunal Cloak|d|||||d^329^Magistrate Barthilas^16.67^0^k
abm|Songbird Blouse|d|||||d^329^Hearthsinger Forresten^20^0^k
abo|Willey's Portable Howitzer|d|||||d^329^Cannon Master Willey^20^0^k
abp|Master Cannoneer Boots|d|||||d^329^Cannon Master Willey^20^0^k
abq|Cannonball Runner|d|||||d^329^Cannon Master Willey^20^0^k
abr|Woollies of the Prancing Minstrel|d|||||d^329^Hearthsinger Forresten^20^0^k
abs|Rainbow Girdle|d|||||d^329^Hearthsinger Forresten^20^0^k
abt|Tome of Knowledge|d|||||d^329^Archivist Galford^12^0^k
abw|The Postmaster's Tunic|d|||||d^329^Postmaster Malown^19.4^0^k
abx|The Postmaster's Trousers|d|||||d^329^Postmaster Malown^19.4^0^k
aby|The Postmaster's Band|d|||||d^329^Postmaster Malown^3^0^k
abz|The Postmaster's Treads|d|||||d^329^Postmaster Malown^19.4^0^k
ac0|The Postmaster's Seal|d|||||d^329^Postmaster Malown^19.4^0^k
ac2|Skul's Cold Embrace|d|||||d^329^Skul^33.33^0^k
ac3|Skul's Fingerbone Claws|d|||||d^329^Skul^33.33^0^k
ac4|Skul's Ghastly Touch|d|||||d^329^Skul^33.33^0^k
ac5|Stoneskin Gargoyle Cape|d|||||d^329^Stonespine^33.33^0^k
ac8|Vambraces of the Sadist|d|||||d^329^Timmy the Cruel^20^0^k
aca|Timmy's Galoshes|d|||||d^329^Timmy the Cruel^20^0^k
acb|Grimgore Noose|d|||||d^329^Timmy the Cruel^20^0^k
acc|Mask of the Unforgiven|d|||||d^329^The Unforgiven^20^0^k
acd|Wailing Nightbane Pauldrons|d|||||d^329^The Unforgiven^20^0^k
acg|Soul Breaker|d|||||d^329^The Unforgiven^20^0^k
aea|Farmer Dalson's Shotgun|q|||||q^5060^Locked Away^52^^k
aeb|Dalson Family Wedding Ring|q|||||q^5060^Locked Away^52^^k
aey|Handcrafted Mastersmith Leggings|d|||||d^229^^14.29^0^k
af2|Handcrafted Mastersmith Girdle|d|||||d^229^^14.29^0^k
af5|Runeblade of Baron Rivendare|d|||||d^329^Baron Rivendare^1^0^k
afo|Skull of Burning Shadows|d|||||d^329^Maleki the Pallid^20^0^k
aft|Husk of Nerub'enkan|d|||||d^329^Nerub'enkan^20^0^k
afy|Banshee Finger|d|||||d^329^Baroness Anastari^20^0^k
afz|Coldtouch Phantom Wraps|d|||||d^329^Baroness Anastari^20^0^k
aow|Runecloth Belt|c|||||c^Tailoring^225^18402^f
aox|Runecloth Tunic|c|||||c^Tailoring^215^18407^f
ap0|Runecloth Cloak|c|||||c^Tailoring^220^18409^f
ap3|Runecloth Gloves|c|||||c^Tailoring^230^18417^f
ap5|Runecloth Pants|c|||||c^Tailoring^240^18438^f
ap6|Runecloth Headband|c|||||c^Tailoring^250^18444^f
ap8|Frostweave Robe|c|||||c^Tailoring^210^18404^f
ap9|Frostweave Tunic|c|||||c^Tailoring^210^18403^f
apa|Frostweave Gloves|c|||||c^Tailoring^215^18411^f
apb|Frostweave Pants|c|||||c^Tailoring^235^18424^f
ar5|Headmaster's Charge|d|||||d^289^Darkmaster Gandling^2^0^k
ar6|Bonecreeper Stylus|d|||||d^289^Darkmaster Gandling^14.29^0^k
arc|Tombstone Breastplate|d|||||d^289^Darkmaster Gandling^14.29^0^k
arj|Vigorsteel Vambraces|d|||||d^289^Darkmaster Gandling^14.29^0^k
arm|Verdant Footpads|d|||||d^329^Stonespine^33.33^0^k
arn|Stoneform Shoulders|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
aro|Clutch of Andros|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
arp|Gargoyle Slashers|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
arq|Wyrmthalak's Shackles|Q|||||q^4903^Warlord's Command^55^h^k~q^5081^Maxwell's Mission^55^a^k
arr|Omokk's Girth Restrainer|Q|||||q^4903^Warlord's Command^55^h^k~q^5081^Maxwell's Mission^55^a^k
ars|Heart of the Fiend|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
art|Halycon's Muzzle|Q|||||q^4903^Warlord's Command^55^h^k~q^5081^Maxwell's Mission^55^a^k
aru|Vosh'gajin's Strand|Q|||||q^4903^Warlord's Command^55^h^k~q^5081^Maxwell's Mission^55^a^k
arv|Voone's Vice Grips|Q|||||q^4903^Warlord's Command^55^h^k~q^5081^Maxwell's Mission^55^a^k
ary|Mark of Tyranny|Q|||||q^4974^For The Horde!^55^h^k~q^5102^General Drakkisath's Demise^55^a^k
arz|Windreaver Greaves|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
as1|Loomguard Armbraces|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
ase|Warblade of Caer Darrow|Q|||||q^5466^The Lich, Ras Frostwhisper^57^^k
asg|Darrowspike|Q|||||q^5466^The Lich, Ras Frostwhisper^57^^k
asi|Crown of Caer Darrow|Q|||||q^5466^The Lich, Ras Frostwhisper^57^^k
asy|Darrowshire Strongguard|Q|||||q^5466^The Lich, Ras Frostwhisper^57^^k
atk|Frightalon|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
atl|Mystic's Belt|dw|s||||m^3640^Evolving Ectoplasm^0^s~m^3258^Bristleback Hunter^0^s
au2|Cindercloth Vest|c|||||c^Tailoring^215^18408^f
au3|Cindercloth Gloves|c|||||c^Tailoring^225^18412^f
au4|Cindercloth Cloak|c|||||c^Tailoring^230^18418^f
au5|Cindercloth Pants|c|||||c^Tailoring^235^18434^f
ava|Beaded Sandals|w|s||||m^256092^Shadowgale Shriekling^0^s~m^252664^Al'Aketh Stormchaser^0^s
avb|Beaded Cuffs|w|s||||m^2017^Bloodfeather Rogue^0^s~m^253282^Shriekling Fledgling^0^s
avd|Beaded Gloves|w|s||||m^2163^Thistle Bear^0^s~m^272096^Befouled Webwood^0^s
ave|Beaded Britches|w|sr||||m^2176^Cursed Highborne^0^s~m^2231^Pygmy Tide Crawler^0^s
avf|Beaded Robe|w|sr||||m^3244^Greater Plainstrider^0^s~m^3272^Kolkar Wrangler^0^s
avh|Beaded Cord|w|s||||m^2017^Bloodfeather Rogue^0^s~m^2189^Vile Sprite^0^s
avi|Beaded Wraps|w|sr||||m^2070^Moonstalker Runt^0^s~m^3127^Venomtail Scorpid^0^s
avj|Native Bands|w|s||||m^2012^Gnarlpine Pathfinder^0^s~m^2070^Moonstalker Runt^0^s
avk|Native Vest|dw|sr||||d^389^^0^0^s~m^3640^Evolving Ectoplasm^0^s
avl|Native Pants|w|sr||||m^3382^Southsea Cannoneer^0^s~m^11322^Searing Blade Cultist^0^s
avm|Native Cloak|w|s||||m^2027^Timberling Trampler^0^s~m^2189^Vile Sprite^0^s
avn|Native Sash|w|s||||m^2965^Windfury Matriarch^0^s~m^3244^Greater Plainstrider^0^s
avo|Brightcloth Robe|c|||||c^Tailoring^225^18414^f
avq|Native Handwraps|w|s||||m^2069^Moonstalker^0^s~m^2201^Greymist Raider^0^s
avs|Brightcloth Pants|c|||||c^Tailoring^245^18439^f
avu|Felcloth Robe|c|||||c^Tailoring^260^18451^f
avv|Felcloth Pants|c|||||c^Tailoring^230^18419^f
avw|Felcloth Boots|c|||||c^Tailoring^240^18437^f
avx|Native Robe|dw|sr||||d^389^^0^0^s~m^3638^Devouring Ectoplasm^0^s
avy|Native Sandals|dw|s||||d^389^^0^0^s~m^2164^Rabid Thistle Bear^0^s
avz|Felcloth Hood|c|||||c^Tailoring^245^18442^f
aw0|Felcloth Shoulders|c|||||c^Tailoring^265^18453^f
aw1|Aboriginal Sash|dw|sr||||m^3284^Venture Co. Drudger^0^s~m^11318^Ragefire Trogg^0^s
aw2|Aboriginal Footwraps|dw|sr||||d^389^^0^0^s~m^2165^Grizzled Thistle Bear^0^s
aw3|Aboriginal Bands|w|s||||m^2021^Bloodfeather Matriarch^0^s~m^2164^Rabid Thistle Bear^0^s
aw4|Aboriginal Cape|w|s||||m^2201^Greymist Raider^0^s~m^3269^Razormane Geomancer^0^s
aw5|Aboriginal Gloves|dw|sr||||m^2164^Rabid Thistle Bear^0^s~m^2069^Moonstalker^0^s
aw7|Aboriginal Loincloth|dw|sr||||d^389^^0^0^s~m^2165^Grizzled Thistle Bear^0^s
awa|Ritual Bands|dw|sr||||m^3277^Witchwing Roguefeather^0^s~m^3280^Witchwing Windcaller^0^s
awc|Ritual Gloves|dw|sr||||d^43^Lady Anacondra^10^0^s~m^2157^Stone Behemoth^0^s
awe|Ritual Amice|dw|s||||m^3456^Razormane Pathfinder^0^s~m^4128^Hecklefang Stalker^0^s
awi|Wizardweave Turban|c|||||c^Tailoring^260^18450^f
awj|Ritual Belt|dw|sr||||d^43^^0^0^s~m^3239^Thunderhead^0^s
awk|Wizardweave Leggings|c|||||c^Tailoring^230^18421^f
awl|Ritual Tunic|Rdw|sr||||m^4026^Bloodfury Windcaller^0^s~R^5834^Azzere the Skyblade^0^s
awm|Cloak of Fire|c|||||c^Tailoring^235^18422^f
awo|Robe of Winter Night|c|||||c^Tailoring^245^18436^f
awp|Mooncloth Leggings|c|||||c^Tailoring^245^18440^f
awq|Mooncloth Vest|c|||||c^Tailoring^270^18447^f
awr|Mooncloth Shoulders|c|||||c^Tailoring^275^18448^f
aws|Mooncloth Circlet|c|||||c^Tailoring^280^18452^f
awt|Ghostweave Vest|c|||||c^Tailoring^225^18416^f
aww|Ghostweave Pants|c|||||c^Tailoring^245^18441^f
awx|Cursed Felblade|d|s||||d^389^Taragaman the Hungerer^56.25^0^s
awy|Gloves of Spell Mastery|cw|||||c^Tailoring^295^18454^f
awz|Cavedweller Bracers|d|s||||d^389^Jergosh the Invoker^18.75^0^s
ax0|Crystalline Cuffs|d|s||||d^389^Taragaman the Hungerer^25^0^s
ax1|Subterranean Cape|d|s||||d^389^Taragaman the Hungerer^18.75^0^s
ax2|Robe of Evocation|d|s||||d^389^Jergosh the Invoker^43.75^0^s
ax3|Chanting Blade|d|s||||d^389^Jergosh the Invoker^37.5^0^s~d^389^Bazzalan^6.25^0^s
ax4|Robe of the Archmage|c|||||c^Tailoring^295^18457^f
ax5|Robe of the Void|c|||||c^Tailoring^295^18458^f
ax6|Truefaith Vestments|c|||||c^Tailoring^295^18456^f
ax9|Pagan Mantle|dw|s||||m^4054^Laughing Sister^0^s~m^4812^Twilight Loreseeker^0^s
axc|Pagan Bands|dw|sr||||d^43^Lord Cobrahn^22.22^0^s~m^3840^Druid of the Fang^0^s
axg|Pagan Belt|dw|sr||||m^3840^Druid of the Fang^0^s~m^5048^Deviate Adder^0^s
axk|Buccaneer's Gloves|dw|sr||||d^33^^0^0^s~m^565^Rabid Dire Wolf^0^s
axl|Aboriginal Shoulder Pads|w|s||||m^3928^Rotting Slime^0^s~m^5762^Deviate Moccasin^0^s
axm|Buccaneer's Mantle|wx|s||||m^565^Rabid Dire Wolf^0^s~m^2261^Syndicate Watchman^0^s
axp|Buccaneer's Cord|dw|sr||||d^33^Commander Springvale^11.11^0^s~d^36^^0^0^s
axu|Watcher's Cap|Rdw|sr||||m^4119^Elder Cloud Serpent^0^s~d^90^Grubbis^0.39^0^k
axy|Watcher's Mantle|dw|sr||||d^47^^0^0^s~d^48^^0^0^s
ay5|Raincaller Cap|Rd|sr||||d^47^Agathelos the Raging^40^0^s~R^1037^Dragonmaw Battlemaster^0.46^k
ay9|Raincaller Pants|Rdw|sr||||d^47^^0^0^s~m^4522^Razorfen Dustweaver^0^s
ayc|Thistlefur Sandals|Rdw|sr||||m^4140^Scorpid Reaver^0^s~d^90^Grubbis^0.39^0^k
aye|Thistlefur Cloak|Rdw|sr||||m^4140^Scorpid Reaver^0^s~d^90^Grubbis^0.39^0^k
ayf|Thistlefur Gloves|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
ayg|Thistlefur Cap|dw|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
ayl|Thistlefur Belt|Rd|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
aym|Vital Bracelets|Rd|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
ayo|Vital Headband|dwx|sr||||m^4133^Silithid Hive Drone^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
ayp|Vital Sash|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b21|Eternal Boots|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b22|Eternal Bindings|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
b23|Eternal Cloak|drwx|r||||d^249^Onyxia^0.83^1^k~d^230^Plugger Spazzring^0.2^0^k
b24|Eternal Crown|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b25|Eternal Gloves|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b26|Eternal Sarong|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b27|Eternal Spaulders|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b29|Eternal Cord|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
b2c|Freezing Lich Robes|d|||||d^289^Ras Frostwhisperer^16.67^0^k
b30|Mystic's Slippers|dw|s||||d^389^^0^0^s~m^3637^Deviate Guardian^0^s
b31|Mystic's Cape|dw|s||||m^11318^Ragefire Trogg^0^s~m^2163^Thistle Bear^0^s
b32|Mystic's Bracelets|dw|s||||d^389^^0^0^s~d^43^^0^0^s
b33|Mystic's Gloves|dw|s||||m^3840^Druid of the Fang^0^s~m^3279^Witchwing Ambusher^0^s
b34|Mystic's Shoulder Pads|w|s||||m^3457^Razormane Stalker^0^s~m^3637^Deviate Guardian^0^s
b35|Mystic's Wrap|dw|s||||m^4805^Blackfathom Sea Witch^0^s~d^36^Edwin VanCleef^0.02^0^k
b36|Mystic's Woolies|dw|s||||d^43^^0^0^s~m^5048^Deviate Adder^0^s
b37|Mystic's Robe|dw|s||||m^4799^Fallenroot Hellcaller^0^s~m^4805^Blackfathom Sea Witch^0^s
b38|Sanguine Armor|dw|s||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
b39|Sanguine Belt|dw|s||||d^48^Old Serra'kis^12.5^0^s~m^4074^XT:9^0^s
b3a|Sanguine Sandals|dw|s||||d^36^Edwin VanCleef^0.02^0^k~d^34^Targorr the Dread^0.01^0^k
b3b|Sanguine Cuffs|dw|s||||m^4094^Galak Scout^0^s~m^4805^Blackfathom Sea Witch^0^s
b3c|Sanguine Cape|dw|s||||d^48^Geilhast^8.33^0^s~m^5755^Deviate Viper^0^s
b3d|Sanguine Handwraps|dw|s||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
b3e|Sanguine Mantle|dw|s||||m^4517^Death's Head Priest^0^s~m^4811^Twilight Aquamancer^0^s
b3x|Resilient Mantle|Rd|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
b3y|Resilient Tunic|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b3z|Resilient Boots|Rdw|s||||m^11683^Horde Shaman^0^s~d^90^Grubbis^0.39^0^k
b40|Resilient Cape|dw|s||||d^34^Dextren Ward^0.01^0^k~d^34^Kam Deepfury^0.01^0^k
b41|Resilient Cap|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b42|Resilient Bands|dw|s||||d^47^Aggem Thorncurse^20^0^s~m^264079^Gloomrise Hatchling^0^s
b43|Resilient Handgrips|Rdw|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
b44|Resilient Leggings|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b45|Resilient Robe|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b46|Resilient Cord|dw|s||||d^47^^0^0^s~m^4104^Screeching Windcaller^0^s
b47|Stonecloth Vest|wx|||||x^6827^Box of Supplies^k~w^34^43^k
b48|Stonecloth Boots|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b49|Stonecloth Cape|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b4a|Stonecloth Circlet|wx|s||||x^6827^Box of Supplies^k~w^33^40^k
b4b|Stonecloth Gloves|dw|s||||d^129^^0^0^s~m^7327^Withered Warrior^0^s
b4c|Stonecloth Epaulets|dwx|s||||m^4640^Magram Wrangler^0^s~d^90^Mekgineer Thermaplugg^0.43^0^k
b4e|Stonecloth Belt|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b4f|Stonecloth Britches|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
b4g|Stonecloth Bindings|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b4i|Silksand Boots|wx|||||x^6827^Box of Supplies^k~w^34^43^k
b4j|Silksand Bracers|wx|||||x^6827^Box of Supplies^k~w^33^40^k
b4k|Silksand Cape|wx|||||x^6827^Box of Supplies^k~w^33^40^k
b4l|Silksand Circlet|w|||||w^38^44^k
b4m|Silksand Gloves|wx|s||||x^6827^Box of Supplies^k~w^36^43^k
b4n|Silksand Shoulder Pads|wx|||||x^6827^Box of Supplies^k~w^36^43^k
b4o|Silksand Legwraps|w|||||w^38^44^k
b4q|Silksand Girdle|wx|||||x^6827^Box of Supplies^k~w^34^43^k
b4t|Windchaser Cuffs|w|||||w^39^45^k
b4v|Windchaser Handguards|w|||||w^40^46^k
b4w|Windchaser Amice|w|||||w^40^47^k
b4x|Windchaser Woolies|w|||||w^40^48^k
b4z|Windchaser Cinch|w|||||w^39^45^k
b52|Venomshroud Boots|w|||||w^43^50^k
b53|Venomshroud Armguards|w|||||w^40^49^k
b56|Venomshroud Mitts|w|||||w^45^51^k
b57|Venomshroud Mantle|w|||||w^45^51^k
b58|Venomshroud Leggings|dw|||||d^349^Princess Theradras^0.19^0^k
b59|Venomshroud Silk Robes|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
b5a|Venomshroud Belt|w|||||w^43^50^k
b5b|Highborne Footpads|dw|||||d^349^Princess Theradras^0.19^0^k
b5c|Highborne Bracelets|dw|||||d^349^Princess Theradras^0.19^0^k
b5d|Highborne Crown|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
b5e|Highborne Cloak|dw|||||d^349^Princess Theradras^0.19^0^k
b5f|Highborne Gloves|dw|||||d^349^Princess Theradras^0.19^0^k
b5g|Highborne Pauldrons|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
b5h|Highborne Robes|dwx|||||d^289^Marduk Blackpool^0.02^0^k
b5i|Highborne Cord|dw|||||d^349^Princess Theradras^0.19^0^k
b5k|Elunarian Vest|drw|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b5l|Elunarian Cuffs|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
b5m|Elunarian Boots|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
b5n|Elunarian Cloak|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
b5o|Elunarian Diadem|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
b5q|Elunarian Sarong|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
b5r|Elunarian Spaulders|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
b5s|Elunarian Silk Robes|drw|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
b5t|Elunarian Belt|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
b6u|Frostbite Girdle|d|||||d^289^Ras Frostwhisperer^16.67^0^k
b6v|Death's Clutch|d|||||d^289^Ras Frostwhisperer^16.67^0^k
b7e|Maelstrom Leggings|d|||||d^289^Ras Frostwhisperer^16.67^0^k
b7h|Boneclenched Gauntlets|d|||||d^289^Ras Frostwhisperer^16.67^0^k
b7k|Rattlecage Buckler|d|||||d^289^Rattlegore^14^0^k
b7s|Bonebrace Hauberk|w|||||w^0^0^k
b7u|Deadwalker Mantle|d|||||d^289^Rattlegore^14^0^k
b7v|Bone Ring Helm|d|||||d^289^Rattlegore^14^0^k
b81|Ghostloom Leggings|d|||||d^289^Jandice Barov^11.86^0^k
b84|Royal Cap Spaulders|d|||||d^289^Jandice Barov^11.86^0^k
b85|Boots of Avoidance|u|||||
b88|Stockade Pauldrons|u|||||
b89|Sash of Mercy|w|||||w^0^0^k
b8a|Cloudkeeper Legplates|w|||||w^0^0^k
b8b|Alcor's Sunrazor|wx|||||x^16885^Heavy Junkbox^k~w^0^0^k
b8d|The Lion Horn of Stormwind|w|||||w^0^0^k
b8e|Lady Maye's Pendant|w|||||w^0^0^k
b8f|Prospector's Sash|dw|s||||m^2069^Moonstalker^0^s~m^3717^Wrathtail Sorceress^0^s
b8g|Prospector's Boots|dw|s||||d^43^Kresh^22.22^0^s~m^3240^Stormsnout^0^s
b8h|Prospector's Cuffs|dw|s||||d^389^^0^0^s~m^3260^Bristleback Water Seeker^0^s
b8i|Prospector's Chestpiece|dw|s||||d^48^^0^0^s~m^3457^Razormane Stalker^0^s
b8j|Prospector's Cloak|dw|s||||m^3278^Witchwing Slayer^0^s~m^11322^Searing Blade Cultist^0^s
b8k|Prospector's Mitts|dw|s||||d^43^^0^0^s~m^3416^Savannah Matriarch^0^s
b8l|Prospector's Woolies|dw|s||||d^43^^0^0^s~m^5053^Deviate Crocolisk^0^s
b8m|Prospector's Pads|dw|s||||d^48^^0^0^s~m^4799^Fallenroot Hellcaller^0^s
b8n|Bristlebark Belt|dw|s||||m^3376^Bael'dun Soldier^0^s~m^3840^Druid of the Fang^0^s
b8o|Bristlebark Boots|dw|s||||m^3673^Lord Serpentis^0^s~m^5763^Nightmare Ectoplasm^0^s
b8p|Bristlebark Bindings|dw|s||||m^3238^Stormhide^0^s~m^3261^Bristleback Thornweaver^0^s
b8q|Bristlebark Blouse|dw|s||||m^264081^Gloomrise Spinner^0^s~d^34^Hamhock^0.01^0^k
b8r|Bristlebark Cape|dw|s||||m^3454^Cannoneer Smythe^0^s~m^3991^Venture Co. Deforester^0^s
b8s|Bristlebark Gloves|dw|s||||d^48^^0^0^s~m^4026^Bloodfury Windcaller^0^s
b8t|Bristlebark Amice|dw|s||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
b8u|Bristlebark Britches|dw|||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
b8x|Skullsmoke Pants|d|||||d^289^Vectus^7^0^k
b8z|Dokebi Boots|Rdw|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
b90|Dokebi Bracers|dw|s||||m^4814^Twilight Elementalist^0^s~d^34^Targorr the Dread^0.01^0^k
b91|Dokebi Chestguard|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b92|Dokebi Cape|dw|||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
b93|Dokebi Gloves|Rd|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
b94|Dokebi Hat|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b95|Dokebi Leggings|Rdw|s||||m^4101^Screeching Roguefeather^0^s~d^90^Grubbis^0.39^0^k
b97|Dokebi Mantle|Rdw|s||||m^4636^Kolkar Battle Lord^0^s~m^4647^Gelkis Scout^0^s
b98|Hawkeye's Cord|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
b99|Hawkeye's Shoes|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
b9a|Hawkeye's Bracers|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b9b|Hawkeye's Helm|wx|||||x^6827^Box of Supplies^k~w^36^43^k
b9c|Hawkeye's Tunic|wx|||||x^6827^Box of Supplies^k~w^36^43^k
b9d|Hawkeye's Cloak|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
b9e|Hawkeye's Gloves|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
b9f|Hawkeye's Breeches|wx|||||x^6827^Box of Supplies^k~w^33^40^k
b9g|Hawkeye's Epaulets|wx|||||x^6827^Box of Supplies^k~w^33^40^k
b9i|Warden's Waistband|wx|||||x^6827^Box of Supplies^k~w^36^43^k
b9k|Warden's Wristbands|wx|||||x^6827^Box of Supplies^k~w^36^43^k
b9l|Warden's Wraps|w|||||w^40^46^k
b9m|Warden's Cloak|dwx|s||||d^129^Mordresh Fire Eye^100^0^s~m^7357^Mordresh Fire Eye^0^s
b9n|Warden's Mantle|w|||||w^37^43^k
b9o|Warden's Wizard Hat|w|s||||m^12219^Barbed Lasher^0^s
b9p|Warden's Woolies|w|||||w^39^45^k
b9q|Warden's Gloves|w|||||w^37^43^k
b9r|Hawkeye's Buckler|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k
b9s|Dokebi Buckler|Rdw|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
b9w|Bloodmail Legguards|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
b9y|Bloodmail Belt|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
b9z|Bloodmail Gauntlets|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba0|Bloodmail Boots|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba4|Deathbone Girdle|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba5|Deathbone Sabatons|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba6|Deathbone Gauntlets|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba7|Deathbone Legguards|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ba8|Deathbone Chestplate|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
baa|Necropile Robe|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bad|Necropile Cuffs|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
baf|Necropile Boots|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bag|Necropile Leggings|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bah|Necropile Mantle|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bak|Cadaverous Belt|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bal|Cadaverous Armor|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bam|Cadaverous Leggings|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bao|Cadaverous Gloves|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bap|Cadaverous Walkers|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
bb0|Scorpashi Sash|w|||||w^40^47^k
bb1|Scorpashi Slippers|w|||||w^40^48^k
bb2|Scorpashi Wristbands|w|||||w^40^46^k
bb3|Scorpashi Breastplate|w|||||w^45^51^k
bb4|Scorpashi Cape|w|||||w^40^46^k
bb6|Scorpashi Skullcap|w|||||w^45^51^k
bb7|Scorpashi Leggings|w|||||w^40^49^k
bb8|Scorpashi Shoulder Pads|w|||||w^40^49^k
bba|Keeper's Hooves|dw|||||d^349^Princess Theradras^0.19^0^k
bbb|Keeper's Bindings|w|||||w^43^50^k
bbd|Keeper's Cloak|w|||||w^43^50^k
bbe|Keeper's Gloves|dw|||||d^349^Princess Theradras^0.19^0^k
bbf|Keeper's Wreath|dw|||||d^349^Princess Theradras^0.19^0^k
bbg|Keeper's Woolies|dw|||||d^349^Princess Theradras^0.19^0^k
bbh|Keeper's Mantle|dw|||||d^349^Princess Theradras^0.19^0^k
bbi|Pridelord Armor|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bbj|Pridelord Boots|dwx|||||d^230^Plugger Spazzring^0.2^0^k
bbk|Pridelord Bands|dw|||||d^349^Princess Theradras^0.19^0^k
bbl|Pridelord Cape|dw|||||d^349^Princess Theradras^0.19^0^k
bbm|Pridelord Girdle|dw|||||d^230^Plugger Spazzring^0.2^0^k
bbn|Pridelord Gloves|dwx|||||d^230^Plugger Spazzring^0.2^0^k
bbo|Pridelord Halo|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bbp|Pridelord Pants|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bbq|Pridelord Pauldrons|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bbs|Indomitable Vest|drw|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bbt|Indomitable Boots|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bbu|Indomitable Armguards|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bbv|Indomitable Cloak|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bbw|Indomitable Belt|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bc0|Indomitable Epaulets|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bcy|War Paint Anklewraps|dw|s||||m^2164^Rabid Thistle Bear^0^s~m^3278^Witchwing Slayer^0^s
bcz|War Paint Bindings|dw|s||||m^2339^Twilight Thug^0^s~m^3240^Stormsnout^0^s
bd0|War Paint Cloak|dw|s||||m^2165^Grizzled Thistle Bear^0^s~m^3242^Zhevra Runner^0^s
bd1|War Paint Waistband|dw|s||||m^2235^Reef Crawler^0^s~m^3256^Sunscale Scytheclaw^0^s
bd2|War Paint Gloves|dw|s||||m^5048^Deviate Adder^0^s~m^3632^Deviate Creeper^0^s
bd3|War Paint Legguards|dw|s||||d^43^Lady Anacondra^20^0^s~d^43^Lord Pythas^11.11^0^s
bd4|War Paint Shoulder Pads|w|s||||w^17^25^k
bd5|War Paint Shield|dw|s||||d^43^^0^0^s~m^3258^Bristleback Hunter^0^s
bd6|War Paint Chestpiece|dw|s||||d^48^^0^0^s~m^3376^Bael'dun Soldier^0^s
bdi|Hulking Boots|dw|s||||d^48^^0^0^s~m^4799^Fallenroot Hellcaller^0^s
bdj|Hulking Bands|Rdw|s||||m^3653^Kresh^0^s~m^3809^Ashenvale Bear^0^s
bdk|Hulking Chestguard|dw|s||||m^4119^Elder Cloud Serpent^0^s~m^264083^Gloomrise Soldier^0^s
bdl|Hulking Cloak|dw|s||||m^2182^Stormscale Sorceress^0^s~m^3840^Druid of the Fang^0^s
bdm|Hulking Belt|dw|s||||d^48^^0^0^s~m^3653^Kresh^0^s
bdn|Hulking Gauntlets|dw|s||||m^5762^Deviate Moccasin^0^s~m^4798^Fallenroot Shadowstalker^0^s
bdo|Hulking Leggings|dw|s||||m^3435^Lok Orcbane^0^s~d^34^Targorr the Dread^0.01^0^k
bdp|Hulking Spaulders|dw|s||||d^48^Lady Sarevess^16.67^0^s~m^4813^Twilight Shadowmage^0^s
bdq|Slayer's Cuffs|dw|s||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
bdr|Slayer's Surcoat|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
bds|Slayer's Cape|dw|s||||d^48^Aku'mai^8.33^0^s~m^4829^Aku'mai^0^s
bdt|Slayer's Skullcap|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
bdu|Slayer's Gloves|dw|s||||d^34^Dextren Ward^0.01^0^k~d^34^Kam Deepfury^0.01^0^k
bdv|Slayer's Sash|dw|||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
bdw|Slayer's Slippers|dw|s||||m^264079^Gloomrise Hatchling^0^s~d^34^Dextren Ward^0.01^0^k
bdx|Slayer's Pants|Rd|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bdy|Slayer's Shoulder Pads|Rdw|s||||m^4107^Highperch Wyvern^0^s~d^90^Grubbis^0.39^0^k
bdz|Enduring Bracers|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
be0|Enduring Breastplate|wx|||||x^6827^Box of Supplies^k~w^34^43^k
be2|Enduring Boots|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
be3|Enduring Cape|Rd|s||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
be4|Enduring Gauntlets|dw|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
be5|Enduring Circlet|wx|||||x^6827^Box of Supplies^k~w^33^40^k
be6|Enduring Breeches|dwx|||||d^90^Mekgineer Thermaplugg^0.43^0^k
be7|Enduring Pauldrons|wx|||||x^6827^Box of Supplies^k~w^33^40^k
bea|Ravager's Armguards|wx|||||x^6827^Box of Supplies^k~w^36^43^k
beb|Ravager's Cloak|wx|||||x^6827^Box of Supplies^k~w^34^43^k
bec|Ravager's Handwraps|wx|||||x^6827^Box of Supplies^k~w^36^43^k
bed|Ravager's Cord|wx|||||x^6827^Box of Supplies^k~w^34^43^k
bee|Ravager's Crown|w|||||w^39^45^k
bef|Ravager's Woolies|w|||||w^39^45^k
beh|Ravager's Shield|w|||||w^40^46^k
bei|Khan's Bindings|w|||||w^40^47^k
bek|Khan's Buckler|w|||||w^45^51^k
bel|Khan's Cloak|w|||||w^40^46^k
bem|Khan's Gloves|w|||||w^40^47^k
ben|Khan's Belt|w|||||w^40^48^k
beo|Khan's Greaves|w|||||w^40^48^k
bep|Khan's Helmet|w|s||||m^12219^Barbed Lasher^0^s
beq|Khan's Legguards|w|||||w^40^49^k
ber|Khan's Mantle|w|||||w^40^49^k
bes|Protector Armguards|w|||||w^45^51^k
bet|Protector Breastplate|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
beu|Protector Buckler|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bev|Protector Cape|w|||||w^43^50^k
bex|Protector Waistband|dw|||||d^349^Princess Theradras^0.19^0^k
bey|Protector Ankleguards|dw|||||d^349^Princess Theradras^0.19^0^k
bez|Protector Helm|dw|||||d^349^Princess Theradras^0.19^0^k
bf2|Bloodlust Breastplate|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bf3|Bloodlust Boots|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bf4|Bloodlust Buckler|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bf5|Bloodlust Cape|dw|||||d^349^Princess Theradras^0.19^0^k
bf6|Bloodlust Gauntlets|dw|||||d^230^Plugger Spazzring^0.2^0^k
bf9|Bloodlust Britches|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bfa|Bloodlust Epaulets|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bfb|Bloodlust Bracelets|dw|||||d^349^Princess Theradras^0.19^0^k
bfc|Warstrike Belt|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bfd|Warstrike Sabatons|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bff|Warstrike Chestguard|drw|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bfg|Warstrike Buckler|drw|||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bfh|Warstrike Cape|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bfp|Symbolic Breastplate|w|||||w^39^45^k
bft|Symbolic Crest|w|||||w^39^45^k
bfx|Symbolic Legplates|w|||||w^38^44^k
bfz|Symbolic Crown|w|||||w^39^45^k
bg1|Tyrant's Gauntlets|w|s||||m^4331^Firemane Ash Tail^0^s
bg2|Tyrant's Armguards|w|||||w^39^45^k
bg3|Tyrant's Chestpiece|w|||||w^43^50^k
bg7|Tyrant's Greaves|w|||||w^40^46^k
bg8|Tyrant's Legplates|w|||||w^40^49^k
bg9|Tyrant's Epaulets|w|||||w^40^46^k
bga|Tyrant's Shield|w|||||w^43^50^k
bgb|Tyrant's Helm|w|||||w^40^48^k
bgc|Sunscale Chestguard|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bge|Sunscale Gauntlets|dw|||||d^349^Princess Theradras^0.19^0^k
bgf|Sunscale Belt|w|||||w^45^51^k
bgg|Sunscale Sabatons|dw|||||d^349^Princess Theradras^0.19^0^k
bgh|Sunscale Helmet|dw|||||d^349^Princess Theradras^0.19^0^k
bgi|Sunscale Legplates|dw|||||d^349^Princess Theradras^0.19^0^k
bgj|Sunscale Spaulders|dw|||||d^349^Princess Theradras^0.19^0^k
bgk|Sunscale Shield|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bgl|Sunscale Wristguards|w|||||w^43^50^k
bgm|Vanguard Breastplate|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bgn|Vanguard Gauntlets|dw|||||d^230^Plugger Spazzring^0.2^0^k
bgo|Vanguard Girdle|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bgp|Vanguard Sabatons|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bgq|Vanguard Headdress|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bgr|Vanguard Legplates|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bgs|Vanguard Pauldrons|dwx|||||d^230^Plugger Spazzring^0.2^0^k
bgt|Vanguard Vambraces|dw|||||d^349^Princess Theradras^0.19^0^k
bgu|Warleader's Breastplate|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bgv|Warleader's Gauntlets|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bgw|Warleader's Belt|dwx|||||d^289^Marduk Blackpool^0.02^0^k
bgx|Warleader's Greaves|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bgy|Warleader's Crown|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bh0|Warleader's Shoulders|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bh1|Warleader's Bracers|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bhy|Saltstone Shield|w|r||||w^37^43^k
bi0|Brutish Breastplate|dw|r||||d^349^Princess Theradras^0.19^0^k
bi8|Brutish Shield|dw|r||||d^349^Princess Theradras^0.19^0^k
bib|Jade Breastplate|dw|r||||d^349^Princess Theradras^0.19^0^k
bic|Jade Deflector|dw|r||||d^349^Princess Theradras^0.19^0^k
big|Jade Legplates|dw|r||||d^349^Princess Theradras^0.19^0^k
bih|Jade Epaulets|w|sr||||m^9162^Young Diemetradon^0^s
bij|Lofty Armguards|dw|r||||d^349^Princess Theradras^0.19^0^k
bj5|Warbringer's Legguards|w|r||||w^40^47^k
bj7|Warbringer's Shield|w|r||||w^40^48^k
bj8|Bloodforged Chestpiece|dw|r||||d^349^Princess Theradras^0.19^0^k
bjh|High Chief's Sabatons|dw|r||||d^349^Princess Theradras^0.19^0^k
bjo|High Chief's Shield|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
bjr|Glorious Gauntlets|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
bjz|Exalted Harness|rw|r||||d^249^Onyxia^0.83^1^k
bk0|Exalted Gauntlets|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
bk1|Exalted Girdle|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
bk2|Exalted Sabatons|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bk3|Exalted Helmet|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bk4|Exalted Legplates|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bk5|Exalted Epaulets|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bk7|Exalted Armsplints|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Marduk Blackpool^0.02^0^k
bkr|Primal Belt|w|s||||m^252820^Bandit Highwayman^0^s~m^3197^Burning Blade Fanatic^0^s
bks|Primal Boots|w|s||||m^2018^Bloodfeather Sorceress^0^s~m^2019^Bloodfeather Fury^0^s
bkt|Primal Bands|w|s||||m^2176^Cursed Highborne^0^s~m^3227^Corrupted Bloodtalon Scythemaw^0^s
bku|Primal Buckler|w|s||||m^2189^Vile Sprite^0^s~m^254626^Al'Aketh Assassin^0^s
bkw|Primal Mitts|w|s||||m^251707^Ornery Galestrider^0^s~m^3131^Lightning Hide^0^s
bkx|Primal Leggings|Rw|sr||||m^2189^Vile Sprite^0^s~m^3197^Burning Blade Fanatic^0^s
bky|Primal Wraps|w|sr||||m^3272^Kolkar Wrangler^0^s~m^256092^Shadowgale Shriekling^0^s
bkz|Lupine Cord|dw|sr||||d^389^^0^0^s~m^2202^Greymist Coastrunner^0^s
bl0|Lupine Slippers|dw|sr||||d^389^Jergosh the Invoker^6.25^0^s~m^3255^Sunscale Screecher^0^s
bl2|Lupine Buckler|dw|sr||||m^2165^Grizzled Thistle Bear^0^s~m^4129^Hecklefang Snarler^0^s
bl4|Lupine Handwraps|dw|sr||||d^43^Lord Serpentis^28.57^0^s~d^389^^0^0^s
bl5|Lupine Leggings|dw|sr||||d^43^Lady Anacondra^20^0^s~m^3636^Deviate Ravager^0^s
bl6|Lupine Vest|dw|sr||||d^43^^0^0^s~m^3240^Stormsnout^0^s
bl7|Lupine Mantle|w|s||||m^3840^Druid of the Fang^0^s~m^3674^Skum^0^s
blx|Green Dragonscale Breastplate|c|||||c^Leatherworking^235^19050^f
bly|Green Dragonscale Leggings|c|||||c^Leatherworking^245^19060^f
blz|Red Dragonscale Breastplate|c|||||c^Leatherworking^290^19054^f
bm0|Blue Dragonscale Breastplate|c|||||c^Leatherworking^260^19077^f
bm1|Blue Dragonscale Shoulders|c|||||c^Leatherworking^270^19089^f
bm2|Black Dragonscale Breastplate|c|||||c^Leatherworking^265^19085^f
bm3|Black Dragonscale Shoulders|c|||||c^Leatherworking^270^19094^f
bm4|Black Dragonscale Leggings|c|||||c^Leatherworking^290^19107^f
bm8|Stormshroud Armor|c|||||c^Leatherworking^260^19079^f
bm9|Stormshroud Pants|c|||||c^Leatherworking^250^19067^f
bma|Stormshroud Shoulders|c|||||c^Leatherworking^270^19090^f
bmb|Living Breastplate|c|||||c^Leatherworking^290^19095^f
bmc|Living Leggings|c|||||c^Leatherworking^260^19078^f
bmd|Living Shoulders|c|||||c^Leatherworking^245^19061^f
bme|Devilsaur Leggings|c|||||c^Leatherworking^290^19097^f
bmf|Devilsaur Gauntlets|c|||||c^Leatherworking^265^19084^f
bmg|Warbear Harness|c|||||c^Leatherworking^250^19068^f
bmh|Warbear Woolies|c|||||c^Leatherworking^260^19080^f
bmi|Ironfeather Breastplate|c|||||c^Leatherworking^265^19086^f
bmj|Ironfeather Shoulders|c|||||c^Leatherworking^245^19062^f
bms|Heavy Scorpid Vest|c|||||c^Leatherworking^240^19051^f
bmt|Heavy Scorpid Bracers|c|||||c^Leatherworking^255^19048^f
bmu|Heavy Scorpid Gauntlet|c|||||c^Leatherworking^250^19064^f
bmv|Heavy Scorpid Leggings|c|||||c^Leatherworking^260^19075^f
bmw|Heavy Scorpid Helm|c|||||c^Leatherworking^270^19088^f
bmx|Heavy Scorpid Shoulders|c|||||c^Leatherworking^280^19100^f
bmy|Heavy Scorpid Belt|c|||||c^Leatherworking^255^19070^f
bmz|Wicked Leather Gauntlets|c|||||c^Leatherworking^235^19049^f
bn0|Wicked Leather Bracers|c|||||c^Leatherworking^240^19052^f
bn1|Wicked Leather Armor|c|||||c^Leatherworking^280^19098^f
bn2|Wicked Leather Headband|c|||||c^Leatherworking^255^19071^f
bn3|Wicked Leather Pants|c|||||c^Leatherworking^265^19083^f
bn4|Wicked Leather Belt|c|||||c^Leatherworking^275^19092^f
bn8|Runic Leather Bracers|c|||||c^Leatherworking^250^19065^f
bnb|Runic Leather Pants|c|||||c^Leatherworking^275^19091^f
bnk|Wingborne Boots|q||a|||q^697^Malin's Request^34^a^k
bnl|Staff of Noh'Orahil|q|||||q^4975^The Completed Orb of Noh'Orahil^35^^k
bnm|Staff of Dar'Orahil|q|||||q^4964^The Completed Orb of Dar'Orahil^35^^k
bnn|Orb of Noh'Orahil|q|||||q^4975^The Completed Orb of Noh'Orahil^35^^k
bno|Orb of Dar'Orahil|q|||||q^4964^The Completed Orb of Dar'Orahil^35^^k
bnp|Staff of Soran'ruk|Q|s||||q^1740^The Orb of Soran'ruk^20^^s
bnq|Rigid Belt|dw|sr||||d^43^^0^0^s~m^5763^Nightmare Ectoplasm^0^s
bns|Rigid Bracelets|dw|sr||||m^2236^Raging Reef Crawler^0^s~m^2339^Twilight Thug^0^s
bnt|Rigid Buckler|dw|sr||||d^43^^0^0^s~m^3840^Druid of the Fang^0^s
bnz|Highborne Pants|dwx|||||d^230^Plugger Spazzring^0.2^0^k
bo8|Robust Tunic|Rdw|sr||||R^3792^Terrowulf Packlord^0^s~d^90^Grubbis^0.39^0^k
bo9|Robust Helm|Rdw|sr||||m^4142^Sparkleshell Tortoise^0^s~m^4525^Razorfen Earthbreaker^0^s
bob|Cutthroat's Boots|Rdw|sr||||m^4635^Kolkar Windchaser^0^s~d^90^Grubbis^0.39^0^k
boe|Cutthroat's Hat|dwx|sr||||d^90^Mekgineer Thermaplugg^0.43^0^k
bog|Cutthroat's Belt|Rdw|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
boh|Cutthroat's Mitts|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
boi|Onyxia Scale Cloak|c|||||c^Leatherworking^320^19093^f
bol|Onyxia Scale Breastplate|c|||||c^Leatherworking^320^19106^f
bon|Ghostwalker Bindings|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
bou|Ghostwalker Pads|dwx|r||||d^90^Mekgineer Thermaplugg^0.43^0^k
bq8|Senior Sergeant's Insignia|pv|U|h|18442||p^4^h^f
bqa|Wildkeeper Leggings|q|s|a|||q^4763^The Blackwood Corrupted^15^a^s
bqb|Guststorm Legguards|q|s|a|||q^4763^The Blackwood Corrupted^15^a^s
bqc|Moonstone Wand|q|s|a|||q^4763^The Blackwood Corrupted^15^a^s
bqd|Owlsight Rifle|q|s|a|||q^5321^The Sleeper Has Awakened^17^a^s
bqe|Jadefinger Baton|q|s|a|||q^5321^The Sleeper Has Awakened^17^a^s
bqf|Steelcap Shield|q|s|a|||q^5321^The Sleeper Has Awakened^17^a^s
bqi|Raider Shortsword|dw|sr||||d^2999^The Butcher^10^0^s~m^547^Great Goretusk^0^s
bqk|Fighter Broadsword|dwx|sr||||d^2998^Saltspine^25^0^s~d^90^^0^0^s
bql|Mercenary Blade|dwx|sr||||d^189^^0^0^s~m^4695^Carrion Horror^0^s
bqm|Nobles Brand|dwx|sr||||d^189^^0^0^s~m^4295^Scarlet Myrmidon^0^s
bqn|Furious Falchion|wx|r||||o^Ancient Treasure^3.4^k~o^Captain's Chest^1.3^k
bqo|Rune Sword|dwx|r||||d^349^Princess Theradras^0.19^0^k
bqp|Widow Blade|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bqs|Battlefell Sabre|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bqt|Holy War Sword|rw|r||||d^249^Onyxia^0.83^1^k
bqu|Barbed Club|dw|sr||||d^36^Gilnid^9.52^0^s~d^33^^0^0^s
bqv|Jagged Star|dwx|sr||||d^33^Fenrus the Devourer^44.44^0^s~d^34^^0^0^s
bqw|Battlesmasher|dwx|sr||||d^34^Hamhock^11.76^0^s~d^34^Bazil Thredd^6.25^0^s
bqx|Sequoia Hammer|Rdwx|sr||||d^90^^0^0^s~m^6426^Anguished Dead^0^s
bqy|Giant Club|dwx|sr||||d^189^^0^0^s~m^691^Lesser Water Elemental^0^s
bqz|Diamond-Tip Bludgeon|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^5758^Mithril Lockbox^k
br0|Smashing Star|dwx|r||||d^349^Princess Theradras^0.19^0^k
br1|Blesswind Hammer|drwx|r||||d^249^Onyxia^0.83^1^k~d^230^Plugger Spazzring^0.2^0^k
br3|Splitting Hatchet|Rdwx|sr||||d^47^^0^0^s~m^314^Eliza^0^s
br4|Hacking Cleaver|Rdwx|sr||||d^129^^0^0^s~m^2271^Dalaran Shield Guard^0^s
br5|Savage Axe|wx|sr||||m^2246^Syndicate Assassin^0^s~m^258804^NPC 258804^0^s
br6|Greater Scythe|wx|sr||||m^262067^NPC 262067^0^s
br7|Crescent Edge|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
br8|Moon Cleaver|dwx|r||||d^349^Princess Theradras^0.19^0^k
brb|Felstone Reaver|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
brc|Demon's Claw|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
brd|Battle Knife|dwx|sr||||d^48^Lorgus Jett^0^0^s~m^12902^Lorgus Jett^0^s
bre|Honed Stiletto|dwx|sr||||d^90^^0^0^s~m^2559^Highland Strider^0^s
brf|Deadly Kris|Rdwx|sr||||m^2242^Syndicate Spy^0^s~m^2588^Syndicate Prowler^0^s
brg|Razor Blade|wx|sr||||m^257900^NPC 257900^0^s~m^258042^NPC 258042^0^s
bri|Demon Blade|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
brj|Bloodstrike Dagger|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
brk|Gleaming Claymore|dw|sr||||d^43^Lady Anacondra^20^0^s~d^33^^0^0^s
brl|Polished Zweihander|dwx|sr||||d^2998^Saltspine^25^0^s~m^1034^Dragonmaw Raider^0^s
brm|Glimmering Flamberge|Rdwx|sr||||m^2248^Cave Yeti^0^s~m^2377^Torn Fin Tidehunter^0^s
brn|Headstriker Sword|wx|r||||o^Ancient Treasure^3.2^k~x^4637^Steel Lockbox^k
bro|Tusker Sword|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
bru|Divine Warblade|rwx|r||||d^249^Onyxia^0.83^1^k
brv|Hefty Battlehammer|Rdwx|sr||||d^33^Odo the Blindwatcher^11.11^0^s~d^48^Geilhast^8.33^0^s
brw|Stone Hammer|wx|sr||||x^6827^Box of Supplies^k~w^33^40^k
brx|Sequoia Branch|wx|r||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
bry|Greater Maul|wx|r||||x^4636^Strong Iron Lockbox^k~x^4638^Reinforced Steel Lockbox^k
brz|Royal Mallet|dwx|r||||d^349^Princess Theradras^0.19^0^k
bs0|Backbreaker|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
bs1|Painbringer|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bs2|Fierce Mauler|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bs4|Twin-bladed Axe|dw|sr||||d^389^^0^0^s~d^43^^0^0^s
bs5|Massive Battle Axe|Rdwx|sr||||d^34^^0^0^s~d^47^^0^0^s
bs6|Gigantic War Axe|wx|r||||x^4638^Reinforced Steel Lockbox^k~x^19035^Lard's Special Picnic Basket^k
bs7|Colossal Great Axe|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.02^0^k
bs8|Razor Axe|dwx|r||||d^289^Marduk Blackpool^0.02^0^k~d^289^Darkmaster Gandling^0.01^0^k
bs9|Death Striker|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bsa|Diviner Long Staff|dwx|r||||d^349^Princess Theradras^0.19^0^k
bsb|Thaumaturgist Staff|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
bsc|Magus Long Staff|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bse|Solstice Staff|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Marduk Blackpool^0.02^0^k
bsf|Ivory Wand|dwx|r||||d^349^Princess Theradras^0.19^0^k
bsg|Wizard's Hand|dwx|r||||d^349^Princess Theradras^0.19^0^k
bsh|Glowstar Rod|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Marduk Blackpool^0.02^0^k
bsi|Dragon Finger|dwx|r||||d^329^Ramstein the Gorger^0.19^0^k~d^289^Marduk Blackpool^0.02^0^k
bsj|Lunar Wand|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bsk|Long Battle Bow|dwx|s||||d^47^Aggem Thorncurse^40^0^s~d^48^^0^0^s
bsl|Archer's Longbow|Rdwx|s||||d^90^Viscous Fallout^16.67^0^s~d^189^^0^0^s
bsm|Long Redwood Bow|dwx|s||||d^189^Interrogator Vishas^9.09^0^s
bsn|Crusader Bow|wx|sr||||o^Ancient Treasure^2.4^k~o^Large Solid Chest^0.75^k
bso|Blasthorn Bow|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bsp|Archstrike Bow|rwx|r||||d^249^Onyxia^0.83^1^k
bsr|Harpy Needler|dwx|r||||d^349^Princess Theradras^0.19^0^k
bsu|Siege Bow|dwx|r||||d^349^Princess Theradras^0.19^0^k
bsv|Quillfire Bow|dwx|r||||d^230^Plugger Spazzring^0.2^0^k
bsw|Hawkeye Bow|dwx|r||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
bsx|Grizzly Bracers|w|s||||m^3118^Dustwind Storm Witch^0^s~m^3207^Hexed Troll^0^s
bsy|Grizzly Buckler|dw|sr||||d^389^Oggleflint^6.25^0^s~d^389^Jergosh the Invoker^6.25^0^s
bsz|Grizzly Cape|w|s||||m^2189^Vile Sprite^0^s~m^272044^Windmistress Gaedress^0^s
bt0|Grizzly Gloves|w|s||||m^2178^Wailing Highborne^0^s~m^11318^Ragefire Trogg^0^s
bt1|Grizzly Slippers|dw|s||||d^389^^0^0^s~m^2069^Moonstalker^0^s
bt2|Grizzly Belt|w|s||||m^2201^Greymist Raider^0^s~m^3117^Dustwind Savage^0^s
bt3|Grizzly Pants|dw|sr||||d^389^^0^0^s~m^2185^Darkshore Thresher^0^s
bt4|Grizzly Jerkin|dw|sr||||m^3255^Sunscale Screecher^0^s~m^4008^Cliff Stormer^0^s
bt5|Feral Shoes|dw|sr||||d^43^Verdan the Everliving^28.57^0^s~m^3425^Savannah Prowler^0^s
bt6|Feral Bindings|dw|sr||||d^389^^0^0^s~m^2164^Rabid Thistle Bear^0^s
bt7|Feral Buckler|dw|sr||||d^43^^0^0^s~m^3840^Druid of the Fang^0^s
bt8|Feral Cord|Rdw|sr||||m^2339^Twilight Thug^0^s~m^3276^Witchwing Harpy^0^s
bt9|Feral Cloak|dw|sr||||d^389^^0^0^s~m^3284^Venture Co. Drudger^0^s
btd|Feral Shoulder Pads|dw|s||||m^4798^Fallenroot Shadowstalker^0^s~m^4819^Blindlight Muckdweller^0^s
btm|Smoothbore Gun|wx|s||||x^4636^Strong Iron Lockbox^k~x^6827^Box of Supplies^k
btn|Percussion Shotgun|dwx|r||||d^349^Princess Theradras^0.19^0^k
bto|Burnside Rifle|dwx|r||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.01^0^k
btp|Sharpshooter Harquebus|drwx|r||||d^249^Onyxia^0.83^1^k~d^289^Marduk Blackpool^0.02^0^k
btw|Wrangler's Buckler|dw|sr||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
btz|Briarsteel Shortsword|q|s|a|||q^4813^The Fragments Within^12^a^s
bu5|Pathfinder Footpads|dwx|r||||d^34^Kam Deepfury^0.01^0^k
bu8|Pathfinder Pants|Rdw|sr||||m^4101^Screeching Roguefeather^0^s~d^90^Grubbis^0.39^0^k
bu9|Pathfinder Shoulder Pads|Rdw|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bua|Pathfinder Vest|Rd|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bud|Headhunter's Belt|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
buh|Headhunter's Headdress|wx|sr||||x^6827^Box of Supplies^k~w^33^40^k
buv|Trickster's Protector|wx|sr||||x^6827^Box of Supplies^k~w^34^43^k
bvo|Curvewood Dagger|q|s|a|||q^4813^The Fragments Within^12^a^s
bvp|Oakthrush Staff|q|s|a|||q^4813^The Fragments Within^12^a^s
bvq|Sandcomber Boots|q|s|a|3454||q^4681^Washed Ashore^11^a^s
bvr|Dryweed Belt|q|s|a|||q^4681^Washed Ashore^11^a^s
bvs|Clamshell Bracers|q|s|a|||q^4681^Washed Ashore^11^a^s
bvt|Welldrip Gloves|q|s|a|||q^982^Deep Ocean, Vast Sea^13^a^s
bvu|Noosegrip Gauntlets|q|s|a|||q^982^Deep Ocean, Vast Sea^13^a^s
bvv|Ridgeback Bracers|q|s|a|||q^4740^WANTED: Murkdeep!^15^a^s
bvw|Breakwater Girdle|q|s|a|||q^4740^WANTED: Murkdeep!^15^a^s
bvx|Shucking Gloves|q|s|a|||q^1138^Fruit of the Sea^15^a^s
bvy|Crustacean Boots|q|s|a|||q^1138^Fruit of the Sea^15^a^s
bw3|Mark of Fordring|q|||||q^5944^In Dreams^55^^k
bw5|Ornate Adamantium Breastplate|q|||||q^5944^In Dreams^55^^k
bwa|Shimmering Platinum Warhammer|q|||||q^5944^In Dreams^55^^k
bwd|Shroud of the Exile|q|||||q^5944^In Dreams^55^^k
bwg|Axe of Orgrimmar|q|s|h|||q^5730^Hidden Enemies^11^h^s
bwq|Supreme Sash|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
bwr|Supreme Shoes|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bws|Supreme Bracers|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
bwt|Supreme Cape|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
bwu|Supreme Gloves|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bwv|Supreme Crown|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bww|Supreme Leggings|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bwx|Supreme Shoulders|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
bwz|Kris of Orgrimmar|q|s|h|||q^5730^Hidden Enemies^11^h^s
bx0|Staff of Orgrimmar|q|s|h|||q^5730^Hidden Enemies^11^h^s
bx1|Hammer of Orgrimmar|q|s|h|||q^5730^Hidden Enemies^11^h^s
bx5|Ghastly Trousers|Q|s|h|||q^5725^The Power to Destroy...^11^h^s
bx6|Dredgemire Leggings|Q|s|h|||q^5725^The Power to Destroy...^11^h^s
bx7|Gargoyle Leggings|Q|s|h|||q^5725^The Power to Destroy...^11^h^s
bx8|Featherbead Bracers|Q|s|h|||q^5724^Returning the Lost Satchel^11^h^s
bx9|Savannah Bracers|Q|s|h|||q^5724^Returning the Lost Satchel^11^h^s
bxb|Dustfall Robes|q|s|a|||q^661^Hints of a New Plague?^32^a^s
bxc|Lightstep Leggings|q|s|a|||q^661^Hints of a New Plague?^32^a^s
bxd|Desert Shoulders|q|s|h|||q^5064^Grimtotem Spying^24^h^s
bxe|Tundra Boots|q|s|h|||q^5064^Grimtotem Spying^24^h^s
bxf|Grimtoll Wristguards|q|s|h|||q^5064^Grimtotem Spying^24^h^s
bxh|Lightheel Boots|q|s|h|||q^4966^Protect Kanati Greycloud^23^h^s
bxi|Loamflake Bracers|q|s|h|||q^4966^Protect Kanati Greycloud^23^h^s
bxj|Palestrider Gloves|q|s|h|||q^4966^Protect Kanati Greycloud^23^h^s
bxk|Brute Hammer|q|s|h|||q^5088^Arikara^24^h^s
bxl|Stingshot Wand|q|s|h|||q^5088^Arikara^24^h^s
bxm|Clink Shield|q|s|h|||q^5088^Arikara^24^h^s
bxn|Inventor's League Ring|q|s|h|||q^5151^Hypercapacitor Gizmo^25^h^s
bxo|Windsong Drape|q|s|h|||q^4904^Free at Last^25^h^s
bxp|Windsong Cinch|q|s|h|||q^4904^Free at Last^25^h^s
bxq|Plainsguard Leggings|q|s|h|||q^5147^Wanted - Arnak Grimtotem^25^h^s
bxr|Brawnhide Armor|q|s|h|||q^5147^Wanted - Arnak Grimtotem^25^h^s
bxs|Charger's Belt|w|s||||m^2027^Timberling Trampler^0^s~m^3114^Razormane Battleguard^0^s
bxt|Charger's Boots|w|s||||m^2189^Vile Sprite^0^s~m^3110^Dreadmaw Crocolisk^0^s
bxu|Charger's Bindings|w|s||||m^2027^Timberling Trampler^0^s~m^3114^Razormane Battleguard^0^s
bxw|Charger's Handwraps|w|s||||m^2189^Vile Sprite^0^s~m^3114^Razormane Battleguard^0^s
bxx|Charger's Pants|w|sr||||m^3127^Venomtail Scorpid^0^s~m^252820^Bandit Highwayman^0^s
bxy|Charger's Shield|w|s||||m^2033^Elder Nightsaber^0^s~m^2979^Venture Co. Supervisor^0^s
bxz|Charger's Armor|w|sr||||m^2163^Thistle Bear^0^s~m^2234^Young Reef Crawler^0^s
by0|War Torn Girdle|w|s||||m^3268^Razormane Thornweaver^0^s~m^3276^Witchwing Harpy^0^s
by1|War Torn Greaves|w|s||||m^11319^Ragefire Shaman^0^s
by2|War Torn Bands|w|s||||m^3113^Razormane Dustrunner^0^s~m^3131^Lightning Hide^0^s
by4|War Torn Handgrips|w|s||||m^2190^Wild Grell^0^s~m^3272^Kolkar Wrangler^0^s
by5|War Torn Pants|dw|sr||||d^389^Jergosh the Invoker^6.25^0^s~m^3242^Zhevra Runner^0^s
by6|War Torn Shield|w|sr||||m^3268^Razormane Thornweaver^0^s~m^251676^Wind Hollow^0^s
by7|War Torn Tunic|dw|sr||||d^389^Jergosh the Invoker^6.25^0^s~m^4007^Deepmoss Venomspitter^0^s
by9|Bloodspattered Sabatons|dw|sr||||d^389^^0^0^s~m^2336^Dark Strand Fanatic^0^s
byb|Bloodspattered Gloves|Rdw|sr||||d^389^Taragaman the Hungerer^6.25^0^s~d^389^Bazzalan^6.25^0^s
byc|Bloodspattered Sash|dw|sr||||m^2167^Blackwood Pathfinder^0^s~m^2168^Blackwood Warrior^0^s
byd|Bloodspattered Loincloth|dw|sr||||m^3640^Evolving Ectoplasm^0^s~m^3840^Druid of the Fang^0^s
bye|Bloodspattered Shield|dw|sr||||m^2181^Stormscale Myrmidon^0^s~d^36^Rhahk'Zor^0.07^0^k
byf|Bloodspattered Wristbands|dw|sr||||d^389^^0^0^s~m^3255^Sunscale Screecher^0^s
byg|Bloodspattered Shoulder Pads|dw|s||||d^48^^0^0^s~m^3374^Bael'dun Excavator^0^s
byh|Outrunner's Cord|dw|sr||||m^3840^Druid of the Fang^0^s~m^3261^Bristleback Thornweaver^0^s
byj|Outrunner's Cuffs|dw|sr||||d^43^^0^0^s~m^2235^Reef Crawler^0^s
bym|Outrunner's Gloves|dw|r||||d^36^Rhahk'Zor^0.07^0^k~d^36^Edwin VanCleef^0.02^0^k
byo|Outrunner's Shield|dw|sr||||m^3459^Razormane Warfrenzy^0^s~m^4799^Fallenroot Hellcaller^0^s
byp|Outrunner's Pauldrons|dw|s||||d^34^Targorr the Dread^0.14^0^k~d^48^Old Serra'kis^0.14^0^k
byr|Grunt's Bracers|dw|sr||||m^3240^Stormsnout^0^s~m^3278^Witchwing Slayer^0^s
byt|Grunt's Handwraps|dw|sr||||m^3653^Kresh^0^s~m^4128^Hecklefang Stalker^0^s
byw|Grunt's Shield|dw|sr||||d^36^Edwin VanCleef^0.02^0^k~d^34^Targorr the Dread^0.01^0^k
byx|Grunt's Pauldrons|Rdw|sr||||R^3253^Silithid Harvester^0^s~m^4798^Fallenroot Shadowstalker^0^s
bz6|Spiked Chain Shield|dw|sr||||m^3757^Xavian Hellcaller^0^s~m^4671^Hatefury Trickster^0^s
bz7|Spiked Chain Shoulder Pads|dw|sr||||m^3435^Lok Orcbane^0^s~d^34^Targorr the Dread^0.01^0^k
bz8|Sentry's Surcoat|Rdw|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bze|Sentry's Shield|Rdw|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bzh|Sentry's Headdress|Rdw|r||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bzi|Wicked Chain Boots|Rdw|sr||||d^47^^0^0^s~m^4635^Kolkar Windchaser^0^s
bzp|Wicked Chain Legguards|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
bzq|Wicked Chain Shoulder Pads|Rd|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
bzs|Thick Scale Sabatons|Rdw|sr||||d^47^^0^0^s~m^4548^Steelsnap^0^s
bzw|Thick Scale Gauntlets|Rdw|sr||||m^4623^Quilguard Champion^0^s~d^90^Grubbis^0.39^0^k
bzx|Thick Scale Belt|Rdw|sr||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
c02|Pillager's Girdle|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
c03|Pillager's Boots|Rd|r||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
c04|Pillager's Bracers|Rdw|sr||||d^47^Death Speaker Jargba^40^0^s~m^4428^Death Speaker Jargba^0^s
c0f|Marauder's Tunic|wx|sr||||m^11559^Outcast Necromancer^0^s
c0h|Marauder's Crest|wx|r||||x^6827^Box of Supplies^k~w^36^43^k
c0w|Sparkleshell Shield|w|r||||w^37^43^k
c0x|Pardoc Grips|q|s|h|||q^6142^Clam Bait^31^h^s
c0z|Ringtail Girdle|q|s|h|||q^6142^Clam Bait^31^h^s
c10|Bracesteel Belt|q|s|h|||q^6142^Clam Bait^31^h^s
c14|Steadfast Buckler|w|r||||w^39^45^k
c1g|Ancient Defender|w|r||||w^40^48^k
c1u|Bonelink Wall Shield|w|r||||w^40^49^k
c3i|Triumphant Sabatons|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
c3j|Triumphant Bracers|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
c3l|Triumphant Cloak|drwx|r||||d^249^Onyxia^0.83^1^k~d^230^Plugger Spazzring^0.2^0^k
c3m|Triumphant Gauntlets|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
c3n|Triumphant Girdle|drwx|r||||d^249^Onyxia^0.83^1^k~d^329^Ramstein the Gorger^0.19^0^k
c3o|Triumphant Skullcap|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
c3p|Triumphant Legplates|drw|r||||d^249^Onyxia^0.83^1^k~d^289^Jandice Barov^0.47^0^k
c3t|Trader's Ring|q|s||||q^5821^Bodyguard for Hire ^30^^s
c3u|Kodobone Necklace|q|s||||q^5501^Bone Collector^34^^s
c3v|Sidegunner Shottie|q|||||q^5943^Gizelton Caravan^33^^k
c3w|Kodo Brander|q|||||q^5943^Gizelton Caravan^33^^k
c3z|Studded Ring Shield|q|||||q^5943^Gizelton Caravan^33^^k
c41|Kodo Rustler Boots|q|s||||q^5561^Kodo Roundup^30^^s
c42|Wrangling Spaulders|q|s||||q^5561^Kodo Roundup^30^^s
c46|Chemist's Ring|q||h|||q^4642^Melding of Influences^50^h^k
c47|Chemist's Smock|q||h|||q^4642^Melding of Influences^50^h^k
c48|Hunter's Insignia Medal|q|||||q^5057^Past Endeavors^55^^k
c49|Tidecrest Blade|q|||||q^5385^The Remains of Trey Lightforge^52^^k
c4a|Hunt Tracker Blade|q|||||q^5385^The Remains of Trey Lightforge^52^^k
c4b|Brantwood Sash|q|||||q^5242^A Final Blow^53^^k
c4c|Blight Leather Gloves|q|||||q^5242^A Final Blow^53^^k
c4d|Gearforge Girdle|q|||||q^5242^A Final Blow^53^^k
c6e|Beaststalker Blade|q||h|||q^5056^Shy-Rotam^55^h^k
c6f|Beasthunter Dagger|q||h|||q^5056^Shy-Rotam^55^h^k
c6g|Crystal Breeze Mantle|q|||||q^5121^High Chief Winterfall^54^^k
c6i|Fernpulse Jerkin|q|||||q^5121^High Chief Winterfall^54^^k
c6j|Willow Band Hauberk|q|||||q^5121^High Chief Winterfall^54^^k
c6l|Deep River Cloak|q|||||q^4842^Strange Sources^51^^k
c6n|Turquoise Sash|q||a|||q^5253^The Crystal of Zin-Malor^53^a^k
c6o|Plow Wood Spaulders|q||a|||q^5253^The Crystal of Zin-Malor^53^a^k
c6r|Emerald Mist Gauntlets|q||a|||q^5253^The Crystal of Zin-Malor^53^a^k
c6s|Seaspray Bracers|q||h|||q^4883^Guarding Secrets^54^h^k
c6t|Shining Armplates|q||h|||q^4883^Guarding Secrets^54^h^k
c6v|Heroic Commendation Medal|q|||||q^5237^Mission Accomplished!^53^a^k~q^5238^Mission Accomplished!^53^h^k
c6w|Intrepid Shortsword|q|||||q^5237^Mission Accomplished!^53^a^k~q^5238^Mission Accomplished!^53^h^k
c6x|Valiant Shortsword|q|||||q^5237^Mission Accomplished!^53^a^k~q^5238^Mission Accomplished!^53^h^k
c6y|Mooncloth Boots|c|||||c^Tailoring^285^19435^f
c70|Cerise Drape|q|||||q^4986^Glyphed Oaken Branch^51^a^k~q^4987^Glyphed Oaken Branch^51^h^k
c71|Penelope's Rose|Q|||||q^5384^Kirtonos the Herald^55^^k
c72|Mirah's Song|Q|||||q^5384^Kirtonos the Herald^55^^k
c73|Light Crossbow|v|s||||V^7976^294^^s
c74|Fine Light Crossbow|v|s||||V^7976^3640^^s
c75|Heavy Crossbow|v|s||||V^7976^14691^^s
c76|Short Spear|v|s||||V^1289^10145^^s
c78|Orchid Amice|q|||||q^4971^A Matter of Time^53^^k
c79|Gold Link Belt|q|||||q^4971^A Matter of Time^53^^k
c7a|Hameya's Slayer|q|||||q^6024^Hameya's Plea^55^^k
c7i|Shadowskin Spaulders|q|||||q^6031^Runecloth^50^^k
c7j|Bricksteel Gauntlets|q|||||q^6031^Runecloth^50^^k
c7k|Astoria Robes|Q|||||q^4701^Put Her Down^55^a^k~q^4724^The Pack Mistress^55^h^k
c7l|Traphook Jerkin|Q|||||q^4701^Put Her Down^55^a^k~q^4724^The Pack Mistress^55^h^k
c7n|Jadescale Breastplate|Q|||||q^4701^Put Her Down^55^a^k~q^4724^The Pack Mistress^55^h^k
c8d|Windreaper|Q|||||q^4771^Dawn's Gambit^57^^k
c8e|Dancing Sliver|Q|||||q^4771^Dawn's Gambit^57^^k
c8f|Ring of Protection|q|||||q^5942^Hidden Treasures^55^^k
c8g|Archlight Talisman|q|||||q^5942^Hidden Treasures^55^^k
c8i|Freewind Gloves|Q||h|||q^4983^Bijou's Reconnaissance Report^55^h^k
c8j|Seapost Girdle|Q||h|||q^4983^Bijou's Reconnaissance Report^55^h^k
c8k|Blinkstrike Armguards|Q|||||q^4765^Delivery to Ridgewell^57^a^k~q^4768^The Darkstone Tablet^57^h^k
c8l|Swiftfoot Treads|Q|||||q^4765^Delivery to Ridgewell^57^a^k~q^4768^The Darkstone Tablet^57^h^k
c8m|Blitzcleaver|q|||||q^4810^Return to Tinkee^50^^k
c8n|Grave Scepter|q|||||q^4810^Return to Tinkee^50^^k
c8o|Condor Bracers|q|s||||q^6134^Ghost-o-plasm Round Up^34^^s
c8p|Anchorhold Buckler|q|s||||q^6134^Ghost-o-plasm Round Up^34^^s
c8q|Veildust Medicine Bag|q|s||||q^6124^Curing the Sick^14^a^s~q^6129^Curing the Sick^14^h^s
c9e|Vanguard Shield|dwx|||||d^289^Marduk Blackpool^0.02^0^k
c9f|Hulking Shield|dw|s||||d^34^Targorr the Dread^0.01^0^k~d^34^Dextren Ward^0.01^0^k
c9g|Slayer's Shield|Rd|||||d^90^Grubbis^0.39^0^k~d^90^Crowd Pummeler 9-60^0.01^0^k
c9h|Prospector's Buckler|dw|s||||d^43^^0^0^s~m^3251^Silithid Grub^0^s
c9i|Bristlebark Buckler|dw|||||d^34^Targorr the Dread^0.01^0^k~d^34^Hamhock^0.01^0^k
c9j|Burnt Buckler|w|s||||m^822^Young Forest Bear^0^s
c9r|Right-Handed Claw|v|s||||V^275625^8117^^s
c9s|Right-Handed Blades|v|s||||V^275625^21708^^s
c9t|Right-Handed Brass Knuckles|v|s||||V^275625^2130^^s
c9u|Left-Handed Brass Knuckles|v|s||||V^275625^2138^^s
c9v|Left-Handed Claw|v|s||||V^275625^8237^^s
c9x|Left-Handed Blades|v|s||||V^275625^22107^^s
cad|Journeyman's Stave|w|s||||m^1172^Tunnel Rat Vermin^0^s~m^833^Coyote Packleader^0^s
cae|Spellbinder Orb|dw|s||||d^2999^Witherfang^10^0^s~d^2999^The Butcher^10^0^s
caf|Bright Sphere|dwx|s||||m^2268^Hillsbrad Footman^0^s~d^34^Targorr the Dread^0.01^0^k
cag|Silver-thread Rod|Rdwx|s||||m^6211^Caverndeep Reaver^0^s~d^90^Grubbis^0.39^0^k
cah|Nightsky Orb|dwx|s||||d^90^Mekgineer Thermaplugg^0.43^0^k
cai|Imperial Red Scepter|dwx|||||d^230^Plugger Spazzring^0.2^0^k~d^289^Darkmaster Gandling^0.03^0^k
caj|Arcane Star|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
cap|Hibernal Sphere|dwx|||||d^349^Princess Theradras^0.19^0^k
cav|Imbued Shield|dwx|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
cax|Runic Stave|dw|s||||d^389^^0^0^s~m^3258^Bristleback Hunter^0^s
cay|Mystic's Sphere|dw|s||||d^48^^0^0^s~m^4807^Blackfathom Myrmidon^0^s
caz|Sanguine Star|dw|s||||d^34^Hamhock^0.01^0^k~d^34^Dextren Ward^0.01^0^k
cbe|Satyr's Rod|Rd|||||d^90^Mekgineer Thermaplugg^0.43^0^k~d^90^Grubbis^0.39^0^k
cbf|Stonecloth Branch|wx|||||x^6827^Box of Supplies^k~w^34^43^k
cbg|Silksand Star|w|||||w^40^46^k
cbh|Windchaser Orb|w|||||w^45^51^k
cbi|Venomshroud Orb|dw|||||d^230^Plugger Spazzring^0.2^0^k~d^349^Princess Theradras^0.19^0^k
cbj|Highborne Star|dwx|||||d^289^Marduk Blackpool^0.02^0^k
cbk|Elunarian Sphere|rw|||||d^249^Onyxia^0.83^1^k~m^6109^Azuregos^2.46^k
cc6|Enduring Shield|wx|||||x^6827^Box of Supplies^k~w^34^43^k
cc7|Warleader's Shield|dw|||||d^289^Jandice Barov^0.47^0^k~d^329^Ramstein the Gorger^0.19^0^k
ccb|Thorium Rifle|c|||||c^Engineering^260^19792^f
cck|Dark Iron Rifle|c|||||c^Engineering^275^19796^f
ccn|Flawless Arcanite Rifle|c|||||c^Engineering^300^19833^f
cdj|Ta'Kierthan Songblade|w|||||w^0^0^k
ce2|Fordring's Seal|q|||||q^5944^In Dreams^55^^k
cl1|Drakefire Amulet|Q|U||||q^6502^Drakefire Amulet^55^a^k~q^6602^Blood of the Black Dragon Champion^55^h^k
cl7|Sergeant Major's Cape|p|U|a|||p^5^a^f
clr|Senior Sergeant's Insignia|pv|U|h|18443||p^4^h^f
cls|Sergeant Major's Cape|p|U|a|||p^5^a^f
clt|Sergeant Major's Cape|p|U|a|||p^5^a^f
clx|Sergeant's Cloak|pv|U|h|18441||p^3^^f
cly|Sergeant's Cape|pv|U|a|18461||p^3^^f~V^12805^44154^a^k
cm1|High Warlord's Blade|p||h|12584||p^14^h^f
cmn|Knight-Captain's Silk Sash|p|U|a|16488||p^8^a^f
cmp|Knight-Lieutenant's Silk Boots|p|U|a|16485||p^7^a^f
cmq|Knight-Captain's Silk Cuffs|p|U|a|||p^8^a^f
cnb|Knight-Lieutenant's Silk Gloves|p|U|a|16487||p^7^a^f
cnc|Knight-Lieutenant's Leather Boots|p|U|a|16498||p^7^a^f
cnd|Knight-Lieutenant's Dragonhide Footwraps|p|U|a|16494||p^7^a^f
cne|Knight-Captain's Leather Bracers|p|U|a|||p^8^a^f
cnf|Knight-Captain's Dragonhide Armsplints|p|U|a|16493||p^8^a^f
cng|Knight-Lieutenant's Leather Gauntlets|p|U|a|16499||p^7^a^f
cnh|Knight-Lieutenant's Dragonhide Gloves|p|U|a|16496||p^7^a^f
cni|Knight-Captain's Leather Belt|p|U|a|16500||p^8^a^f
cnj|Knight-Captain's Dragonhide Girdle|p|U|a|16495||p^8^a^f
cnk|Knight-Captain's Chain Girdle|p|U|a|16529||p^8^a^f
cnl|Knight-Lieutenant's Chain Boots|p|U|a|16531||p^7^a^f
cnm|Knight-Captain's Chain Armguards|p|U|a|16517||p^8^a^f
cnn|Knight-Lieutenant's Chain Gauntlets|p|U|a|16530||p^7^a^f
cno|Knight-Captain's Plate Wristguards|p|U|a|16512||p^8^a^f
cnp|Knight-Lieutenant's Plate Boots|p|U|a|16509||p^7^a^f
cnq|Knight-Lieutenant's Plate Gauntlets|p|U|a|16510||p^7^a^f
cnr|Knight-Captain's Plate Girdle|p|U|a|16511||p^8^a^f
cnt|Knight-Lieutenant's Lamellar Sabatons|p|U|a|||p^7^a^f
cnu|Knight-Lieutenant's Lamellar Gauntlets|p|U|a|||p^7^a^f
cnv|Knight-Captain's Lamellar Cinch|p|U|a|||p^8^a^f
cnw|Knight-Captain's Lamellar Armsplints|p|U|a|||p^8^a^f
cnx|Knight-Captain's Silk Raiment|p|U|a|16491||p^8^a^f
cny|Knight-Captain's Silk Leggings|p|U|a|16490||p^8^a^f
cnz|Lieutenant Commander's Silk Spaulders|p|U|a|16492||p^10^a^f
co0|Lieutenant Commander's Crown|p|U|a|16489||p^10^a^f
co1|Knight-Captain's Leather Armor|p|U|a|16505||p^8^a^f
co2|Lieutenant Commander's Leather Veil|p|U|a|16506||p^10^a^f
co3|Knight-Captain's Leather Legguards|p|U|a|16508||p^8^a^f
co4|Lieutenant Commander's Leather Spaulders|p|U|a|16507||p^10^a^f
co5|Knight-Captain's Dragonhide Tunic|p|U|a|16504||p^8^a^f
co6|Knight-Captain's Dragonhide Leggings|p|U|a|16502||p^8^a^f
co7|Lieutenant Commander's Dragonhide Epaulets|p|U|a|16501||p^10^a^f
co8|Lieutenant Commander's Dragonhide Shroud|p|U|a|16503||p^10^a^f
co9|Knight-Captain's Chain Hauberk|p|U|a|16525||p^8^a^f
coa|Knight-Captain's Chain Leggings|p|U|a|16527||p^8^a^f
cob|Lieutenant Commander's Chain Pauldrons|p|U|a|16528||p^10^a^f
coc|Lieutenant Commander's Chain Helmet|p|U|a|||p^10^a^f
cod|Lieutenant Commander's Plate Helm|p|U|a|16514||p^10^a^f
coe|Knight-Captain's Plate Chestguard|p|U|a|16513||p^8^a^f
cof|Knight-Captain's Plate Leggings|p|U|a|16515||p^8^a^f
cog|Lieutenant Commander's Plate Pauldrons|p|U|a|16516||p^10^a^f
coh|Knight-Captain's Lamellar Breastplate|p|U|a|||p^8^a^f
coi|Lieutenant Commander's Lamellar Headguard|p|U|a|||p^10^a^f
coj|Knight-Captain's Lamellar Leggings|p|U|a|||p^8^a^f
cok|Lieutenant Commander's Lamellar Shoulders|p|U|a|||p^10^a^f
col|Marshal's Silk Footwraps|p|U|a|16539||p^12^a^f
com|Marshal's Silk Bracers|p|U|a|16538||p^12^a^f
con|Marshal's Silk Sash|p|U|a|16537||p^12^a^f
coo|Marshal's Silk Gloves|p|U|a|16540||p^12^a^f
cop|Field Marshal's Coronet|p|U|a|16533||p^13^a^f
coq|Marshal's Silk Leggings|p|U|a|16534||p^12^a^f
cor|Field Marshal's Silk Vestments|p|U|a|16535||p^13^a^f
cos|Field Marshal's Silk Spaulders|p|U|a|16536||p^13^a^f
cot|Marshal's Dragonhide Bracers|p|U|a|16553||p^12^a^f
cou|Marshal's Leather Footguards|p|U|a|16558||p^12^a^f
cov|Marshal's Dragonhide Waistguard|p|U|a|16556||p^12^a^f
cow|Marshal's Dragonhide Gauntlets|p|U|a|16555||p^12^a^f
cox|Field Marshal's Dragonhide Spaulders|p|U|a|16551||p^13^a^f
coy|Marshal's Dragonhide Legguards|p|U|a|16552||p^12^a^f
coz|Field Marshal's Dragonhide Helmet|p|U|a|16550||p^13^a^f
cp0|Field Marshal's Dragonhide Breastplate|p|U|a|16549||p^13^a^f
cp1|Field Marshal's Leather Chestpiece|p|U|a|16563||p^13^a^f
cp2|Marshal's Leather Handgrips|p|U|a|16560||p^12^a^f
cp3|Field Marshal's Leather Mask|p|U|a|16561||p^13^a^f
cp4|Marshal's Leather Leggings|p|U|a|16564||p^12^a^f
cp5|Field Marshal's Leather Epaulets|p|U|a|16562||p^13^a^f
cp6|Marshal's Leather Cinch|p|U|a|16557||p^12^a^f
cp7|Marshal's Dragonhide Boots|p|U|a|16554||p^12^a^f
cp8|Marshal's Leather Armsplints|p|U|a|16559||p^12^a^f
cp9|Marshal's Chain Bracers|p|U|a|16570||p^12^a^f
cpa|Marshal's Chain Boots|p|U|a|16569||p^12^a^f
cpb|Marshal's Chain Grips|p|U|a|16571||p^12^a^f
cpc|Marshal's Chain Girdle|p|U|a|16572||p^12^a^f
cpd|Field Marshal's Chain Helm|p|U|a|16566||p^13^a^f
cpe|Field Marshal's Chain Breastplate|p|U|a|16565||p^13^a^f
cpf|Marshal's Chain Legguards|p|U|a|16567||p^12^a^f
cpg|Field Marshal's Chain Spaulders|p|U|a|16568||p^13^a^f
cph|Marshal's Lamellar Armguards|p|U|a|||p^12^a^f
cpi|Marshal's Lamellar Belt|p|U|a|||p^12^a^f
cpj|Marshal's Lamellar Gloves|p|U|a|||p^12^a^f
cpk|Marshal's Lamellar Boots|p|U|a|||p^12^a^f
cpl|Field Marshal's Lamellar Chestplate|p|U|a|||p^13^a^f
cpm|Field Marshal's Lamellar Faceguard|p|U|a|||p^13^a^f
cpn|Marshal's Lamellar Legplates|p|U|a|||p^12^a^f
cpo|Field Marshal's Lamellar Pauldrons|p|U|a|||p^13^a^f
cpp|Field Marshal's Plate Armor|p|U|a|16541||p^13^a^f
cpq|Field Marshal's Plate Helm|p|U|a|16542||p^13^a^f
cpr|Marshal's Plate Legguards|p|U|a|16543||p^12^a^f
cps|Field Marshal's Plate Shoulderguards|p|U|a|16544||p^13^a^f
cpt|Marshal's Plate Bracers|p|U|a|16546||p^12^a^f
cpu|Marshal's Plate Girdle|p|U|a|16547||p^12^a^f
cpv|Marshal's Plate Boots|p|U|a|16545||p^12^a^f
cpw|Marshal's Plate Gauntlets|p|U|a|16548||p^12^a^f
cpx|Blood Guard's Silk Footwraps|p|U|h|16369||p^7^h^f
cpy|First Sergeant's Silk Cuffs|pv|U|h|18456||p^5^h^f
cpz|Blood Guard's Silk Gloves|p|U|h|16391||p^7^h^f
cq0|Legionnaire's Silk Belt|p|U|h|16367||p^8^h^f
cq1|Champion's Silk Hood|p|U|h|16416||p^10^h^f
cq2|Legionnaire's Silk Pants|p|U|h|16414||p^8^h^f
cq3|Legionnaire's Silk Robes|p|U|h|16413||p^8^h^f
cq4|Champion's Silk Shoulderpads|p|U|h|16415||p^10^h^f
cq5|Legionnaire's Dragonhide Armguards|p|U|h|16395||p^8^h^f
cq6|Blood Guard's Dragonhide Boots|p|U|h|16393||p^7^h^f
cq7|Legionnaire's Dragonhide Waistband|p|U|h|16399||p^8^h^f
cq8|Blood Guard's Dragonhide Gauntlets|p|U|h|16397||p^7^h^f
cq9|First Sergeant's Leather Armguards|pv|U|h|18452||p^5^h^f
cqa|Blood Guard's Leather Treads|p|U|h|16392||p^7^h^f
cqb|Blood Guard's Leather Vices|p|U|h|16396||p^7^h^f
cqc|Legionnaire's Leather Girdle|p|U|h|16398||p^8^h^f
cqd|Champion's Dragonhide Spaulders|p|U|h|16423||p^10^h^f
cqe|Legionnaire's Dragonhide Trousers|p|U|h|16422||p^8^h^f
cqf|Champion's Dragonhide Helm|p|U|h|16424||p^10^h^f
cqg|Legionnaire's Dragonhide Breastplate|p|U|h|16421||p^8^h^f
cqh|Legionnaire's Leather Hauberk|p|U|h|16417||p^8^h^f
cqi|Champion's Leather Headguard|p|U|h|16418||p^10^h^f
cqj|Champion's Leather Mantle|p|U|h|16420||p^10^h^f
cqk|Legionnaire's Leather Leggings|p|U|h|16419||p^8^h^f
cql|Blood Guard's Plate Boots|p|U|h|16405||p^7^h^f
cqm|Blood Guard's Plate Gloves|p|U|h|16406||p^7^h^f
cqn|Legionnaire's Plate Cinch|p|U|h|16407||p^8^h^f
cqo|Legionnaire's Plate Bracers|p|U|h|16404||p^8^h^f
cqp|Legionnaire's Plate Armor|p|U|h|16430||p^8^h^f
cqq|Champion's Plate Headguard|p|U|h|16429||p^10^h^f
cqr|Legionnaire's Plate Legguards|p|U|h|16431||p^8^h^f
cqs|Champion's Plate Pauldrons|p|U|h|16432||p^10^h^f
cqt|Legionnaire's Chain Bracers|p|U|h|16402||p^8^h^f
cqu|Blood Guard's Mail Walkers|p|U|h|||p^7^h^f
cqv|Blood Guard's Mail Grips|p|U|h|||p^7^h^f
cqw|Legionnaire's Mail Cinch|p|U|h|||p^8^h^f
cqx|Champion's Mail Helm|p|U|h|||p^10^h^f
cqy|Legionnaire's Mail Chestpiece|p|U|h|||p^8^h^f
cqz|Legionnaire's Mail Leggings|p|U|h|||p^8^h^f
cr0|Champion's Mail Shoulders|p|U|h|||p^10^h^f
cr1|Legionnaire's Chain Breastplate|p|U|h|16425||p^8^h^f
cr3|Legionnaire's Chain Leggings|p|U|h|16426||p^8^h^f
cr4|Champion's Chain Pauldrons|p|U|h|16427||p^10^h^f
cr5|Legionnaire's Chain Girdle|p|U|h|16400||p^8^h^f
cr6|Blood Guard's Chain Gauntlets|p|U|h|16403||p^7^h^f
cr7|Blood Guard's Chain Boots|p|U|h|16401||p^7^h^f
cr8|First Sergeant's Mail Wristguards|pv|U|h|||p^5^h^f~V^12799^44802^h^k
cr9|Warlord's Silk Cowl|p|U|h|16441||p^13^h^f
cra|General's Silk Trousers|p|U|h|16442||p^12^h^f
crb|Warlord's Silk Raiment|p|U|h|16443||p^13^h^f
crc|Warlord's Silk Amice|p|U|h|16444||p^13^h^f
crd|General's Silk Sash|p|U|h|16439||p^12^h^f
cre|General's Silk Cuffs|p|U|h|16438||p^12^h^f
crf|General's Silk Boots|p|U|h|16437||p^12^h^f
crg|General's Silk Handguards|p|U|h|16440||p^12^h^f
crh|Warlord's Plate Armor|p|U|h|16477||p^13^h^f
cri|Warlord's Plate Headpiece|p|U|h|16478||p^13^h^f
crj|General's Plate Leggings|p|U|h|16479||p^12^h^f
crk|Warlord's Plate Shoulders|p|U|h|16480||p^13^h^f
crl|General's Plate Boots|p|U|h|16483||p^12^h^f
crm|General's Plate Armguards|p|U|h|16481||p^12^h^f
crn|General's Plate Girdle|p|U|h|16482||p^12^h^f
cro|General's Plate Gauntlets|p|U|h|16484||p^12^h^f
crp|Warlord's Dragonhide Hauberk|p|U|h|16452||p^13^h^f
crq|Warlord's Dragonhide Helmet|p|U|h|16451||p^13^h^f
crr|Warlord's Dragonhide Epaulets|p|U|h|16449||p^13^h^f
crs|General's Dragonhide Leggings|p|U|h|16450||p^12^h^f
crt|General's Dragonhide Bracers|p|U|h|16445||p^12^h^f
cru|General's Dragonhide Boots|p|U|h|16459||p^12^h^f
crv|General's Dragonhide Gloves|p|U|h|16448||p^12^h^f
crw|General's Dragonhide Belt|p|U|h|16447||p^12^h^f
crx|General's Leather Girdle|p|U|h|16458||p^12^h^f
cry|General's Leather Treads|p|U|h|16446||p^12^h^f
crz|General's Leather Armsplints|p|U|h|16460||p^12^h^f
cs0|General's Leather Mitts|p|U|h|16454||p^12^h^f
cs1|Warlord's Leather Helm|p|U|h|16455||p^13^h^f
cs2|Warlord's Leather Spaulders|p|U|h|16457||p^13^h^f
cs3|Warlord's Leather Breastplate|p|U|h|16453||p^13^h^f
cs4|General's Leather Legguards|p|U|h|16456||p^12^h^f
cs5|Warlord's Chain Chestpiece|p|U|h|16466||p^13^h^f
cs6|Warlord's Chain Helmet|p|U|h|16465||p^13^h^f
cs7|General's Chain Legguards|p|U|h|16467||p^12^h^f
cs8|Warlord's Chain Shoulders|p|U|h|16468||p^13^h^f
cs9|General's Chain Sabatons|p|U|h|16462||p^12^h^f
csa|General's Chain Wristguards|p|U|h|16461||p^12^h^f
csb|General's Chain Gloves|p|U|h|16463||p^12^h^f
csc|General's Chain Girdle|p|U|h|16464||p^12^h^f
csd|General's Mail Boots|p|U|h|||p^12^h^f
cse|General's Mail Gauntlets|p|U|h|||p^12^h^f
csf|General's Mail Waistband|p|U|h|||p^12^h^f
csg|General's Mail Bracers|p|U|h|||p^12^h^f
csh|Warlord's Mail Armor|p|U|h|||p^13^h^f
csi|Warlord's Mail Helm|p|U|h|||p^13^h^f
csj|General's Mail Leggings|p|U|h|||p^12^h^f
csk|Warlord's Mail Spaulders|p|U|h|||p^13^h^f
ctc|Aquarius Belt|q|s||||q^31^Aquatic Form^16^h^s~q^5061^Aquatic Form^16^a^s
ctq|Thornflinger|q||a|||q^4902^Wildkin of Elune^52^a^k
ctr|Opaline Medallion|q||a|||q^4902^Wildkin of Elune^52^a^k
cuq|Wildhunter Cloak|q|s|h|||q^247^The Hunt Completed^25^h^s
cur|Deftkin Belt|q|s|h|||q^824^Je'neu of the Earthen Ring^23^h^s
cus|Driftmire Shield|q|s|h|||q^824^Je'neu of the Earthen Ring^23^h^s
cut|Soft Willow Cape|q|s|h|||q^824^Je'neu of the Earthen Ring^23^h^s
cuy|Vest of Elements|d|||||d^229^General Drakkisath^11.11^0^k
cuz|Coif of Elements|d|||||d^289^Darkmaster Gandling^11.11^0^k
cv1|Pauldrons of Elements|w|||||m^10339^Gyth^20^k
cv3|Bindings of Elements|w|||||w^0^0^k
cv4|Gauntlets of Elements|d|||||d^229^Pyroguard Emberseer^20^0^k
cv6|Beaststalker's Tunic|d|||||d^229^General Drakkisath^11.11^0^k
cv7|Beaststalker's Boots|d|||||d^329^Nerub'enkan^20^0^k
cv8|Beaststalker's Gloves|d|||||d^229^War Master Voone^20^0^k
cv9|Beaststalker's Cap|d|||||d^289^Darkmaster Gandling^11.11^0^k
cva|Beaststalker's Pants|d|||||d^329^Baron Rivendare^11.11^0^k
cvb|Beaststalker's Mantle|d|||||d^229^Overlord Wyrmthalak^20^0^k
cvc|Beaststalker's Belt|w|||||w^0^0^k
cvd|Beaststalker's Bindings|w|||||w^0^0^k
cve|Magister's Boots|d|||||d^329^Hearthsinger Forresten^20^0^k
cvf|Magister's Bindings|w|||||w^0^0^k
cvg|Magister's Gloves|d|||||d^289^Doctor Theolen Krastinov^14^0^k
cvh|Magister's Belt|w|||||w^0^0^k
cvj|Magister's Leggings|d|||||d^329^Baron Rivendare^11.11^0^k
cvl|Magister's Mantle|d|||||d^289^Ras Frostwhisperer^16.67^0^k
cvm|Devout Robe|d|||||d^229^General Drakkisath^11.11^0^k
cvo|Devout Gloves|d|||||d^329^Archivist Galford^22^0^k
cvp|Devout Crown|d|||||d^289^Darkmaster Gandling^11.11^0^k
cvq|Devout Skirt|d|||||d^329^Baron Rivendare^11.11^0^k
cvr|Devout Mantle|w|||||m^10264^Solakar Flamewreath^20^k
cvs|Devout Belt|w|||||w^0^0^k
cvt|Devout Bracers|w|||||w^0^0^k
cvu|Dreadmist Mask|d|||||d^289^Darkmaster Gandling^11.11^0^k
cvx|Dreadmist Mantle|d|||||d^289^Jandice Barov^17^0^k
cvy|Dreadmist Belt|w|||||w^0^0^k
cvz|Dreadmist Bracers|w|||||w^0^0^k
cw0|Dreadmist Sandals|d|||||d^329^Baroness Anastari^20^0^k
cw1|Dreadmist Wraps|d|||||d^289^Lorekeeper Polkelt^17^0^k
cw3|Shadowcraft Cap|d|||||d^289^Darkmaster Gandling^11.11^0^k
cw4|Shadowcraft Spaulders|d|||||d^329^Cannon Master Willey^20^0^k
cw5|Shadowcraft Pants|d|||||d^329^Baron Rivendare^11.11^0^k
cw6|Shadowcraft Bracers|dw|||||d^289^Instructor Malicia^5^0^k~d^329^^1.4^0^k
cw7|Shadowcraft Boots|d|||||d^289^Rattlegore^16^0^k
cw8|Shadowcraft Gloves|d|||||d^229^Shadow Hunter Vosh'gajin^21^0^k
cw9|Shadowcraft Belt|w|||||w^0^0^k
cwa|Wildheart Bracers|w|||||w^0^0^k
cwc|Wildheart Belt|d|||||d^289^The Ravenian^4^0^k~d^229^^1.11^0^k
cwe|Wildheart Spaulders|d|||||d^229^Gizrul the Slavener^15^0^k
cwh|Shadowcraft Tunic|d|||||d^229^General Drakkisath^11.11^0^k
cwi|Lightforge Bracers|dw|||||d^289^Lord Alexei Barov^5^0^k~m^10409^Rockwing Screecher^0.7^k
cwj|Lightforge Belt|w|||||w^0^0^k
cwk|Lightforge Gauntlets|d|||||d^329^Timmy the Cruel^20^0^k
cwl|Lightforge Boots|d|||||d^329^Balnazzar^19.8^0^k
cwm|Lightforge Breastplate|d|||||d^229^General Drakkisath^11.11^0^k
cwn|Lightforge Helm|d|||||d^289^Darkmaster Gandling^11.11^0^k
cwo|Lightforge Legplates|d|||||d^329^Baron Rivendare^11.11^0^k
cwp|Lightforge Spaulders|d|||||d^229^The Beast^20^0^k
cwq|Breastplate of Valor|d|||||d^229^General Drakkisath^11.11^0^k
cwr|Helm of Valor|d|||||d^289^Darkmaster Gandling^11.11^0^k
cws|Legplates of Valor|d|||||d^329^Baron Rivendare^11.11^0^k
cwt|Spaulders of Valor|d|||||d^229^Warchief Rend Blackhand^19.8^0^k
cwu|Boots of Valor|dw|||||d^289^Kirtonos^11.11^0^k~m^10506^Kirtonos the Herald^11.11^k
cwv|Bracers of Valor|w|||||w^0^0^k
cww|Belt of Valor|w|||||w^0^0^k
cwx|Gauntlets of Valor|d|||||d^329^Ramstein the Gorger^12^0^k
cwy|Witherseed Gloves|q|s||||q^5863^The Dunemaul Compound^44^^s
cwz|Rugwood Mantle|q|s||||q^5863^The Dunemaul Compound^44^^s
cx0|Shredder Operating Gloves|q|s|h|||q^6504^The Lost Pages^25^h^s
cx1|Oilrag Handwraps|q|s|h|||q^6504^The Lost Pages^25^h^s
cxs|Furbolg Medicine Pouch|v|||||V^11555^150000^^k
cxt|Furbolg Medicine Totem|v|||||V^11555^133081^^k
cyc|Captain Rackmore's Wheel|q|s||||q^6161^Claim Rackmore's Treasure!^31^^s
cyd|Captain Rackmore's Tiller|q|s||||q^6161^Claim Rackmore's Treasure!^31^^s
cyf|Silkstream Cuffs|q|s||||q^6027^Book of the Ancients^33^^s
cyh|Arcmetal Shoulders|q|s||||q^6027^Book of the Ancients^33^^s
cyi|Gripsteel Wristguards|q|s|h|||q^5581^Portals of the Legion^33^h^s
d0p|Braidfur Gloves|q|s|h|||q^5581^Portals of the Legion^33^h^s
d12|Outlaw Sabre|q|s|h|||q^6922^Baron Aquanis^25^h^s
d13|Witch's Finger|q|s|h|||q^6922^Baron Aquanis^25^h^s
d15|Polished Walking Staff|q|s|h|||q^6544^Torek's Assault^20^h^s
d16|Slatemetal Cutlass|q|s|h|||q^6544^Torek's Assault^20^h^s
d17|Claystone Shortsword|q|s|h|||q^6284^Arachnophobia^16^h^s
d1a|Clear Crystal Rod|q|s|h|||q^6284^Arachnophobia^16^h^s
d3j|Warsong Sash|q|s|h|||q^6571^Warsong Supplies^22^h^s
d3l|Warsong Boots|q|s|h|||q^6571^Warsong Supplies^22^h^s
d3m|Warsong Gauntlets|q|s|h|||q^6571^Warsong Supplies^22^h^s
d3p|Owlbeard Bracers|q|s|h|||q^6481^Earthen Arise^15^h^s
d3r|Molten Helm|c|||||c^Leatherworking^300^20854^f
d3t|Windseeker Boots|q|s|h|||q^6381^New Life^20^h^s
d3u|Sandspire Gloves|q|s|h|||q^6381^New Life^20^h^s
d3v|Screecher Belt|q|s|h|||q^6283^Bloodfury Bloodline^21^h^s
d3y|Spritekin Cloak|q|s|h|||q^6283^Bloodfury Bloodline^21^h^s
d40|Smokey's Explosive Launcher|q|||||q^6041^When Smokey Sings, I Get Violent^54^^k
d41|Smokey's Fireshooter|q|||||q^6041^When Smokey Sings, I Get Violent^54^^k
d42|Duskwing Gloves|q||h|||q^6135^Duskwing, Oh How I Hate Thee...^56^h^k
d43|Duskwing Mantle|q||h|||q^6135^Duskwing, Oh How I Hate Thee...^56^h^k
d44|Gorewood Bow|q|||||q^6148^The Scarlet Oracle, Demetria^56^h^k~q^6187^Order Must Be Restored^56^a^k
d45|Stormrager|q|||||q^6148^The Scarlet Oracle, Demetria^56^h^k~q^6187^Order Must Be Restored^56^a^k
d46|Sacred Protector|q|||||q^6148^The Scarlet Oracle, Demetria^56^h^k~q^6187^Order Must Be Restored^56^a^k
d4b|Skullstone Hammer|q||h|||q^6136^The Corpulent One^56^h^k
d4c|Sarah's Guide|q||h|||q^6136^The Corpulent One^56^h^k
d4d|Boorguard Tunic|q|s|h|||q^6621^King of the Foulweald^21^h^s
d4e|Cobalt Legguards|q|s|h|||q^6621^King of the Foulweald^21^h^s
d4f|Stonerender Gauntlets|u|||||
d4l|Dark Iron Leggings|c|||||c^Blacksmithing^300^20876^f
d4m|Dark Iron Bracers|c|||||c^Blacksmithing^270^20874^f
d4n|Dark Iron Reaver|c|||||c^Blacksmithing^300^20890^f
d5b|Skullbreaker|Q|s|h|||q^6521^An Unholy Alliance^31^h^s
d5e|Nail Spitter|Q|s|h|||q^6521^An Unholy Alliance^31^h^s
d5f|Zealot's Robe|Q|s|h|||q^6521^An Unholy Alliance^31^h^s
d5g|Will of the Martyr|Q|||||q^5125^Aurius' Reckoning^55^^k
d5h|Blood of the Martyr|Q|||||q^5125^Aurius' Reckoning^55^^k
d5i|Gutterblade|q||a|||q^1046^Raene's Cleansing^25^a^k
d5j|Luminescent Amice|q|s|a|||q^1035^Fallen Sky Lake^25^a^s
d5m|Chan's Imperial Robes|w|||||w^0^0^k
d5r|Changuk Smasher|w|||||w^0^0^k
d7b|Blazefury Medallion|w|||||m^12397^Lord Kazzak^19^k
d9b|Dented Buckler|v|s|h|||V^3161^34^h^s
d9c|Small Shield|vw|s||||V^251965^34^^s~m^11040^Watcher Brownell^0.02^k
d9d|Round Buckler|v||h|17186||V^3167^243^h^s
d9e|Small Targe|v|s|a|17185||V^4240^243^a^s
d9f|Banded Buckler|vw|s||||V^4187^1078^^s~m^3528^Pyrewood Armorer^100^k
d9g|Ringed Buckler|v|s||||V^3493^2265^^s
d9h|Metal Buckler|v|s||||V^272435^12043^^s
d9i|Ornate Buckler|v|s||||V^8129^34609^^s
d9k|Reinforced Targe|v|s||||V^4240^4399^^s
d9l|Sulfuron Hammer|c|||||c^Blacksmithing^300^21161^f
dic|Forcestone Buckler|Q|s|h|||q^1049^Compendium of the Fallen^33^h^s
dir|Smokey's Drape|q|||||q^6041^When Smokey Sings, I Get Violent^54^^k
dju|Knight-Lieutenant's Dreadweave Boots|p|U|a|||p^7^a^f
djv|Knight-Captain's Dreadweave Bracers|p|U|a|17575||p^8^a^f
djw|Knight-Lieutenant's Dreadweave Gloves|p|U|a|||p^7^a^f
djx|Knight-Captain's Dreadweave Belt|p|U|a|17574||p^8^a^f
djy|Lieutenant Commander's Headguard|p|U|a|17570||p^10^a^f
djz|Knight-Captain's Dreadweave Leggings|p|U|a|||p^8^a^f
dk0|Knight-Captain's Dreadweave Robe|p|U|a|17572||p^8^a^f
dk1|Lieutenant Commander's Dreadweave Mantle|p|U|a|17573||p^10^a^f
dk2|Champion's Dreadweave Hood|p|U|h|17566||p^10^h^f
dk3|Legionnaire's Dreadweave Leggings|p|U|h|||p^8^h^f
dk4|Legionnaire's Dreadweave Robe|p|U|h|17568||p^8^h^f
dk5|Champion's Dreadweave Shoulders|p|U|h|17569||p^10^h^f
dk6|Legionnaire's Dreadweave Belt|p|U|h|17565||p^8^h^f
dk7|Legionnaire's Dreadweave Bracers|p|U|h|17563||p^8^h^f
dk8|Blood Guard's Dreadweave Boots|p|U|h|||p^7^h^f
dk9|Blood Guard's Dreadweave Gloves|p|U|h|||p^7^h^f
dka|Field Marshal's Coronal|p|U|a|17591||p^13^a^f
dkb|Marshal's Dreadweave Leggings|p|U|a|17593||p^12^a^f
dkc|Field Marshal's Dreadweave Shoulders|p|U|a|17590||p^13^a^f
dkd|Field Marshal's Dreadweave Robe|p|U|a|17592||p^13^a^f
dke|Marshal's Dreadweave Cuffs|p|U|a|17587||p^12^a^f
dkf|Marshal's Dreadweave Boots|p|U|a|17586||p^12^a^f
dkg|Marshal's Dreadweave Gloves|p|U|a|17588||p^12^a^f
dkh|Marshal's Dreadweave Sash|p|U|a|17589||p^12^a^f
dki|General's Dreadweave Boots|p|U|h|17583||p^12^h^f
dkj|General's Dreadweave Bracers|p|U|h|17582||p^12^h^f
dkk|General's Dreadweave Gloves|p|U|h|17584||p^12^h^f
dkl|General's Dreadweave Belt|p|U|h|17585||p^12^h^f
dkm|Warlord's Dreadweave Mantle|p|U|h|17580||p^13^h^f
dkn|Warlord's Dreadweave Hood|p|U|h|17578||p^13^h^f
dko|Warlord's Dreadweave Robe|p|U|h|17581||p^13^h^f
dkp|General's Dreadweave Pants|p|U|h|17579||p^12^h^f
dkq|Knight-Lieutenant's Satin Boots|p|U|a|17616||p^7^a^f
dkr|Knight-Captain's Satin Cuffs|p|U|a|17615||p^8^a^f
dks|Knight-Lieutenant's Satin Gloves|p|U|a|17617||p^7^a^f
dkt|Knight-Captain's Satin Cord|p|U|a|17614||p^8^a^f
dku|Lieutenant Commander's Diadem|p|U|a|17610||p^10^a^f
dkv|Knight-Captain's Satin Leggings|p|U|a|17611||p^8^a^f
dkw|Knight-Captain's Satin Robes|p|U|a|17612||p^8^a^f
dkx|Lieutenant Commander's Satin Amice|p|U|a|17613||p^10^a^f
dky|Field Marshal's Headdress|p|U|a|17623||p^13^a^f
dkz|Marshal's Satin Pants|p|U|a|17625||p^12^a^f
dl0|Field Marshal's Satin Mantle|p|U|a|17622||p^13^a^f
dl1|Field Marshal's Satin Vestments|p|U|a|17624||p^13^a^f
dl2|Marshal's Satin Bracers|p|U|a|17619||p^12^a^f
dl3|Marshal's Satin Sandals|p|U|a|17618||p^12^a^f
dl4|Marshal's Satin Gloves|p|U|a|17620||p^12^a^f
dl5|Marshal's Satin Sash|p|U|a|17621||p^12^a^f
dl6|Champion's Satin Cowl|p|U|h|17598||p^10^h^f
dl7|Legionnaire's Satin Trousers|p|U|h|17599||p^8^h^f
dl8|Legionnaire's Satin Vestments|p|U|h|17600||p^8^h^f
dl9|Champion's Satin Shoulderpads|p|U|h|17601||p^10^h^f
dla|Legionnaire's Satin Sash|p|U|h|17597||p^8^h^f
dlb|Legionnaire's Satin Cuffs|p|U|h|17595||p^8^h^f
dlc|Blood Guard's Satin Boots|p|U|h|17594||p^7^h^f
dld|Blood Guard's Satin Gloves|p|U|h|17596||p^7^h^f
dle|General's Satin Boots|p|U|h|17607||p^12^h^f
dlf|General's Satin Bracers|p|U|h|17606||p^12^h^f
dlg|General's Satin Gloves|p|U|h|17608||p^12^h^f
dlh|General's Satin Cinch|p|U|h|17609||p^12^h^f
dli|Warlord's Satin Mantle|p|U|h|17604||p^13^h^f
dlj|Warlord's Satin Cowl|p|U|h|17602||p^13^h^f
dlk|Warlord's Satin Robes|p|U|h|17605||p^13^h^f
dll|General's Satin Leggings|p|U|h|17603||p^12^h^f
dna|Master Hunter's Bow|q|s||||q^208^Big Game Hunter^38^^s
dnb|Master Hunter's Rifle|q|s||||q^208^Big Game Hunter^38^^s
dnc|Jungle Boots|q|s||||q^338^The Green Hills of Stranglethorn^35^^s
dng|Horn Ring|q|s|h|||q^6641^Vorsha the Lasher^20^h^s
dni|Band of the Fist|Q|s|h|||q^6565^Allegiance to the Old Gods^21^h^s
dnj|Chestnut Mantle|Q|s|h|||q^6565^Allegiance to the Old Gods^21^h^s
dns|Edge of Winter|c|||||c^Blacksmithing^165^21913^f
dnt|Thrash Blade|Q|||||q^7064^Corruption of Earth and Seed^46^h^k~q^7065^Corruption of Earth and Seed^46^a^k
dnv|Gemshard Heart|d|||||d^349^Princess Theradras^20^0^k
dny|Charstone Dirk|d|||||d^349^Princess Theradras^20^0^k
dnz|Elemental Rockridge Leggings|d|s||||d^349^Princess Theradras^0^0^s
do1|Blackstone Ring|d|s||||d^349^Princess Theradras^0^0^s
do2|Bracers of the Stone Princess|d|s||||d^349^Princess Theradras^0^0^s
do3|Eye of Theradras|d|s||||d^349^Princess Theradras^0^0^s
do5|Megashot Rifle|d|||||d^349^Tinkerer Gizlock^33.33^0^k
do6|Gizlock's Hypertech Buckler|d|s||||d^349^Tinkerer Gizlock^0^0^s
do7|Inventor's Focal Sword|d|||||d^349^Tinkerer Gizlock^33.33^0^k
do9|Gloves of the Greatfather|c|||||c^Leatherworking^165^21943^f
dog|Albino Crocscale Boots|d|||||d^349^Rotgrip^40^0^k
doi|Gatorbite Axe|d|||||d^349^Rotgrip^20^0^k
dok|Rotgrip Mantle|d|s||||d^349^Rotgrip^0^0^s
dom|Helm of the Mountain|d|||||d^349^Landslide^25^0^k
doo|Rockgrip Gauntlets|d|s||||d^349^Landslide^0^0^s
dop|Cloud Stone|d|||||d^349^Landslide^25^0^k
doq|Claw of Celebras|d|||||d^349^Celebras the Cursed^33.33^0^k
dor|Grovekeeper's Drape|d|||||d^349^Celebras the Cursed^33.33^0^k
dos|Soothsayer's Headdress|d|s||||d^349^Celebras the Cursed^0^0^s
dot|Nature's Embrace|d|||||d^349^^33.33^0^k
dou|Fungus Shroud Armor|d|||||d^349^^33.33^0^k
dov|Resurgence Rod|Q|||||q^7064^Corruption of Earth and Seed^46^h^k~q^7065^Corruption of Earth and Seed^46^a^k
dox|Noxious Shooter|d|s||||d^349^Noxxion^0^0^s
doy|Noxxion's Shackles|d|||||d^349^Noxxion^40^0^k
dp0|Vinerot Sandals|d|||||d^349^Razorlash^25^0^k
dp1|Phytoskin Spaulders|d|||||d^349^Razorlash^25^0^k
dp3|Brusslehide Leggings|d|||||d^349^Razorlash^25^0^k
dp4|Satyr's Lash|d|||||d^349^Lord Vyletongue^33.33^0^k
dp5|Verdant Keeper's Aim|Q|||||q^7064^Corruption of Earth and Seed^46^h^k~q^7065^Corruption of Earth and Seed^46^a^k
dp6|Infernal Trickster Leggings|d|||||d^349^Lord Vyletongue^33.33^0^k
dp7|Satyrmane Sash|d|||||d^349^Lord Vyletongue^33.33^0^k
dpi|Princess Theradras' Scepter|d|||||d^349^Princess Theradras^20^0^k
dpj|Bloomsprout Headpiece|d|||||d^349^^33.33^0^k
dpk|Woodseed Hoop|Q|||||q^7029^Vyletongue Corruption^42^h^k~q^7041^Vyletongue Corruption^42^a^k
dpm|Branchclaw Gauntlets|Q|||||q^7029^Vyletongue Corruption^42^h^k~q^7041^Vyletongue Corruption^42^a^k
dpo|Zealous Shadowshard Pendant|Q|||||q^7068^Shadowshard Fragments^38^h^k~q^7070^Shadowshard Fragments^38^a^k
dpp|Prodigious Shadowshard Pendant|Q|||||q^7068^Shadowshard Fragments^38^h^k~q^7070^Shadowshard Fragments^38^a^k
dpr|Acumen Robes|Q|||||q^7028^Twisted Evils^42^^k
dps|Sprightring Helm|Q|||||q^7028^Twisted Evils^42^^k
dpt|Relentless Chain|Q|||||q^7028^Twisted Evils^42^^k
dpu|Sagebrush Girdle|Q|||||q^7029^Vyletongue Corruption^42^h^k~q^7041^Vyletongue Corruption^42^a^k
dpv|Hulkstone Pauldrons|Q|||||q^7028^Twisted Evils^42^^k
dpw|Blade of Eternal Darkness|d|||||d^349^Princess Theradras^0.5^0^k
dt9|Stormpike Insignia Rank 3|q|U|a|17906||q^7169^Honored Amongst the Guard^55^a^k
dta|Stormpike Insignia Rank 4|q|U|a|17907||q^7170^Earned Reverence^55^a^k
dtb|Stormpike Insignia Rank 5|q|U|a|17908||q^7171^Legendary Heroes^55^a^k
dtc|Stormpike Insignia Rank 6|q|U|a|17909||q^7172^The Eye of Command^55^a^k
dte|Frostwolf Insignia Rank 3|q|U|h|17901||q^7164^Honored Amongst the Clan^55^h^k
dtf|Frostwolf Insignia Rank 4|q|U|h|17902||q^7165^Earned Reverence^55^h^k
dtg|Frostwolf Insignia Rank 5|q|U|h|17903||q^7166^Legendary Heroes^55^h^k
dth|Frostwolf Insignia Rank 6|q|U|h|17904||q^7167^The Eye of Command^55^h^k
dtu|Lionfur Armor|w|||||w^0^0^k
duf|Fist of Stone|d|||||d^349^Landslide^25^0^k
dwm|Royal Seal of Alexis|Q||h|||q^6163^Ramstein^56^h^k
dx7|Coal Miner Boots|d|||||d^230^Hurley Blackbreath^30.33^0^k
dx8|Hurley's Tankard|d|||||d^230^Hurley Blackbreath^30.33^0^k
dxc|Mastersmith's Hammer|d|||||d^229^^14.29^0^k
dya|Zum'rah's Vexing Cane|d|||||d^209^Witch Doctor Zum'rah^20^0^k
dyb|Jumanza Grips|d|||||d^209^Witch Doctor Zum'rah^40^0^k
dyu|Dragonrider Boots|d|||||d^229^Warchief Rend Blackhand^19.8^0^k
dyv|Band of Rumination|d|||||d^229^Warchief Rend Blackhand^16.67^0^k
e2m|Shadowskin Gloves|c|||||c^Leatherworking^175^22711^f
e3b|Flarecore Wraps|c|||||c^Tailoring^300^22759^f
e3u|Core Marksman Rifle|c|||||c^Engineering^300^22795^f
e41|Barbed Thorn Necklace|w|||||w^0^0^k
e48|Marksman Bands|w|||||w^0^0^k
e4a|Unbridled Leggings|w|||||w^0^0^k
e4d|Lethtendris's Wand|d|||||d^429^Lethtendris^30^0^k
e4e|Band of Vigor|d|||||d^429^Lethtendris^30^0^k
e4g|Greenroot Mail|u|||||
e4h|Breakwater Legguards|d|||||d^429^Hydrospawn^25^0^k
e4i|Gloves of Shadowy Mist|d|||||d^429^Zevrim Thornhoof^20^0^k
e4j|Riptide Shoes|d|||||d^429^Hydrospawn^25^0^k
e4l|Gloves of Restoration|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4m|Fiendish Machete|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4n|Quel'dorai Channeling Rod|d|||||d^429^Lethtendris^10^0^k
e4o|Energized Chestplate|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4p|Helm of Awareness|d|||||d^429^Zevrim Thornhoof^20^0^k
e4q|Ring of Demonic Guile|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4r|Ring of Demonic Potency|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4s|Obsidian Bauble|u|||||
e4t|Tempest Talisman|d|||||d^429^Hydrospawn^20^0^k
e4u|Merciful Greaves|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4w|Demondash Spaulders|u|||||
e4x|Energetic Rod|d|||||d^429^Alzzin the Wildshaper^20^0^k
e4y|Waterspout Boots|d|||||d^429^Hydrospawn^20^0^k
e4z|Satyr's Bow|d|||||d^429^Zevrim Thornhoof^20^0^k
e50|Waveslicer|d|||||d^429^Hydrospawn^10^0^k
e51|Felhide Cap|d|||||d^429^Lethtendris^30^0^k
e53|Whipvine Cord|d|||||d^429^Alzzin the Wildshaper^20^0^k
e54|Shadewood Cloak|d|||||d^429^Alzzin the Wildshaper^20^0^k
e5d|Orphic Bracers|w|||||w^0^0^k
e5e|Wand of Arcane Potency|w|||||w^0^0^k
e5k|Stonebark Gauntlets|w|||||w^0^0^k
e5m|Threadbare Trousers|d|||||d^429^Tsu'zee^33.33^0^k
e5n|Well Balanced Axe|d|||||d^429^Illyanna Ravenoak^25^0^k
e5o|Quel'Serrar|Q|U||||q^7509^The Forging of Quel'Serrar^60^^k
e5p|Gauntlets of Accuracy|d|||||d^429^Illyanna Ravenoak^25^0^k
e5q|Amplifying Cloak|d|||||d^429^Magister Kalendris^20^0^k
e5r|Magically Sealed Bracers|d|||||d^429^Magister Kalendris^20^0^k
e5s|Petrified Bark Shield|d|||||d^429^Tendris Warpwood^25^0^k
e5t|Stoneflower Staff|d|||||d^429^Tendris Warpwood^25^0^k
e5u|Pimgib's Collar|d|||||d^429^^14^0^k
e66|Gordok's Handguards|Q|||||q^1318^Unfinished Gordok Business^56^^k~q^7703^Unfinished Gordok Business^56^^k
e67|Gordok's Gauntlets|Q|||||q^1318^Unfinished Gordok Business^56^^k~q^7703^Unfinished Gordok Business^56^^k
e68|Gordok's Gloves|Q|||||q^1318^Unfinished Gordok Business^56^^k~q^7703^Unfinished Gordok Business^56^^k
e69|Gordok's Handwraps|Q|||||q^1318^Unfinished Gordok Business^56^^k~q^7703^Unfinished Gordok Business^56^^k
e6a|Vigilance Charm|d|||||d^429^Immol'thar^20^0^k
e6b|Mindtap Talisman|d|||||d^429^Magister Kalendris^20^0^k
e6c|Blade of the New Moon|d|||||d^429^Immol'thar^20^0^k
e6d|Chestplate of Tranquility|d|||||d^429^Prince Tortheldrin^20^0^k
e6f|Bracers of the Eclipse|d|||||d^429^Prince Tortheldrin^20^0^k
e6g|Timeworn Mace|d|||||d^429^Prince Tortheldrin^20^0^k
e6h|Quickdraw Gloves|d|||||d^429^Immol'thar^20^0^k
e6i|Silvermoon Leggings|d|||||d^429^Prince Tortheldrin^20^0^k
e6j|Odious Greaves|d|||||d^429^Immol'thar^20^0^k
e6k|Eldritch Reinforced Legplates|d|||||d^429^Prince Tortheldrin^20^0^k
e6l|Evil Eye Pendant|d|||||d^429^Immol'thar^20^0^k
e6n|Force Imbued Gauntlets|d|||||d^429^Illyanna Ravenoak^25^0^k
e6o|Bile-etched Spaulders|d|||||d^429^Immol'thar^20^0^k
e6p|Robe of Everlasting Night|d|||||d^429^Immol'thar^20^0^k
e6q|Padre's Trousers|d|||||d^429^Illyanna Ravenoak^25^0^k
e6r|Brightspark Gloves|d|||||d^429^Tsu'zee^33.33^0^k
e6t|Cloak of the Cosmos|d|||||d^429^Immol'thar^20^0^k
e6v|Eyestalk Cord|d|||||d^429^Immol'thar^20^0^k
e6w|Distracting Dagger|d|||||d^429^Prince Tortheldrin^20^0^k
e6x|Warpwood Binding|d|||||d^429^Tendris Warpwood^25^0^k
e6y|Demon Howl Wristguards|d|||||d^429^Immol'thar^20^0^k
e6z|Emerald Flame Ring|d|||||d^429^Prince Tortheldrin^20^0^k
e73|Ocean's Breeze|q|||||q^7486^A Hero's Reward^60^^k
e74|Ring of Living Stone|q|||||q^6845^Uncovering Past Secrets^54^^k
e76|Glowing Crystal Ring|q|||||q^6845^Uncovering Past Secrets^54^^k
e77|Dragonslayer's Signet|q|||||q^7491^For All To See^60^h^k~q^7496^Celebrating Good Times^60^a^k
e78|Onyxia Tooth Pendant|q|||||q^7491^For All To See^60^h^k~q^7496^Celebrating Good Times^60^a^k
e79|Belt of the Archmage|c|||||c^Tailoring^295^22866^f
e7b|Felcloth Gloves|c|||||c^Tailoring^280^22867^f
e7c|Inferno Gloves|c|||||c^Tailoring^280^22868^f
e7d|Mooncloth Gloves|c|||||c^Tailoring^280^22869^f
e7e|Sprinter's Sword|Q|||||q^7441^Pusillin and the Elder Azj'Tordin^54^^k
e7f|Spry Boots|Q|||||q^7441^Pusillin and the Elder Azj'Tordin^54^^k
e7h|Cloak of Warding|c|||||c^Tailoring^280^22870^f
e7o|Bonecrusher|Q|||||q^7462^The Treasure of the Shen'dralar^56^a^k~q^7877^The Treasure of the Shen'dralar^56^h^k
e7p|Backwood Helm|Q|||||q^7462^The Treasure of the Shen'dralar^56^a^k~q^7877^The Treasure of the Shen'dralar^56^h^k
e7s|Sedge Boots|Q|||||q^7462^The Treasure of the Shen'dralar^56^a^k~q^7877^The Treasure of the Shen'dralar^56^h^k
e7t|Kreeg's Mug|d|||||d^429^Stomper Kreeg^40^0^k
e7v|Sergeant's Cloak|pv|U|h|18440||p^3^^f
e7w|Senior Sergeant's Insignia|pv|U|h|18444||p^4^h^f
e7x|First Sergeant's Plate Bracers|pv|U|h|18445||p^5^h^f
e7y|First Sergeant's Plate Bracers|pv|U|h|18447||p^5^h^f
e80|First Sergeant's Mail Wristguards|pv|U|h|||p^5^h^f~V^12799^21742^h^k
e82|First Sergeant's Dragonhide Armguards|pv|U|h|18454||p^5^h^f
e83|First Sergeant's Leather Armguards|pv|U|h|18453||p^5^h^f
e84|First Sergeant's Dragonhide Armguards|pv|U|h|18455||p^5^h^f
e85|First Sergeant's Silk Cuffs|pv|U|h|18457||p^5^h^f
e88|Sergeant's Cape|pv|U|a|18427||p^3^^f~V^12805^6443^a^k
e89|Sergeant's Cape|pv|U|a|16341||p^3^^f~V^12805^20891^a^k
e8a|Master Sergeant's Insignia|pv|U|a|15200||p^4^a^f~V^12805^20000^a^k
e8b|Master Sergeant's Insignia|pv|U|a|16335||p^4^a^f~V^12805^40000^a^k
e8c|Master Sergeant's Insignia|pv|U|a|18428||p^4^a^f~V^12805^30000^a^k
e8d|Sergeant Major's Plate Wristguards|pv|U|a|18429||p^5^a^f~V^12805^29021^a^k
e8f|Sergeant Major's Plate Wristguards|pv|U|a|18430||p^5^a^f~V^12805^14235^a^k
e8g|Sergeant Major's Chain Armguards|pv|U|a|16532||p^5^a^f~V^12805^44007^a^k
e8h|Sergeant Major's Chain Armguards|pv|U|a|18432||p^5^a^f~V^12805^21507^a^k
e8i|Robe of Combustion|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8j|Hyena Hide Belt|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8k|Sergeant Major's Leather Armsplints|pv|U|a|16497||p^5^a^f~V^12805^34553^a^k
e8l|Sergeant Major's Leather Armsplints|pv|U|a|18435||p^5^a^f~V^12805^16890^a^k
e8m|Sergeant Major's Dragonhide Armsplints|pv|U|a|18434||p^5^a^f~V^12805^34815^a^k
e8n|Sergeant Major's Dragonhide Armsplints|pv|U|a|18436||p^5^a^f~V^12805^17020^a^k
e8o|Sergeant Major's Silk Cuffs|pv|U|a|16486||p^5^a^f~V^12805^28065^a^k
e8p|Sergeant Major's Silk Cuffs|pv|U|a|18437||p^5^a^f~V^12805^13373^a^k
e8q|Modest Armguards|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8r|Gallant's Wristguards|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8t|Sergeant's Cloak|pv|U|h|16342||p^3^^f
e8v|Ogre Pocket Knife|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8w|Gordok Nose Ring|d|||||d^429^Guard Fengus^12.5^0^k~d^429^Guard Mol'dar^7.69^0^k
e8x|Royal Seal of Eldre'Thalas|Q|U||||q^7498^Garona: A Study on Stealth and Treachery^55^^k
e8y|Royal Seal of Eldre'Thalas|Q|U||||q^7499^Codex of Defense^55^^k
e90|Royal Seal of Eldre'Thalas|Q|U||||q^7500^The Arcanist's Cookbook^55^^k
e91|Royal Seal of Eldre'Thalas|Q|U||||q^7504^Holy Bologna: What the Light Won't Tell You^55^^k
e92|Royal Seal of Eldre'Thalas|Q|U||||q^7506^The Emerald Dream...^55^^k
e94|Royal Seal of Eldre'Thalas|Q|U||||q^7501^The Light and How To Swing It^55^^k
e95|Royal Seal of Eldre'Thalas|Q|U||||q^7503^The Greatest Race of Hunters^55^^k
e97|Oddly Magical Belt|dw|||||d^429^Gordok Mastiff^0.02^0^k
e98|Mud Stained Boots|w|||||o^Gordok Tribute^25^k
e99|Shaggy Leggings|dw|||||d^429^Gordok Mastiff^0.02^0^k
e9a|Hyena Hide Jerkin|w|||||o^Gordok Tribute^25^k
e9b|Carrion Scorpid Helm|dw|||||d^429^Gordok Mastiff^0.02^0^k
e9c|Scarab Plate Helm|w|||||o^Gordok Tribute^25^k
e9e|Ogre Toothpick Shooter|w|||||o^Gordok Tribute^25^k
e9f|Mana Channeling Wand|d|||||d^429^Cho'Rush the Observer^25^0^k
e9g|Cho'Rush's Blade|d|||||d^429^Cho'Rush the Observer^25^0^k
e9h|Observer's Shield|d|||||d^429^Cho'Rush the Observer^25^0^k
e9i|Mooncloth Robe|c|||||c^Tailoring^275^22902^f
e9m|Insightful Hood|d|||||d^429^Cho'Rush the Observer^25^0^k
e9n|Lorespinner|Q|||||q^7488^Lethtendris's Web^54^a^k~q^7489^Lethtendris's Web^54^h^k
e9p|Bulky Iron Spaulders|d|||||d^429^Guard Mol'dar^7.69^0^k~d^429^Guard Slip'kik^7.69^0^k
e9q|Denwatcher's Shoulders|d|||||d^429^Guard Mol'dar^7.69^0^k~d^429^Guard Slip'kik^7.69^0^k
e9r|Redoubt Cloak|w|||||o^Gordok Tribute^24.75^k
e9s|Heliotrope Cloak|d|||||d^429^Guard Mol'dar^7.69^0^k~d^429^Guard Slip'kik^7.69^0^k
e9t|Sublime Wristguards|d|||||d^429^Guard Mol'dar^7.69^0^k~d^429^Guard Slip'kik^7.69^0^k
e9u|Hedgecutter|d|||||d^429^Guard Mol'dar^7.69^0^k~d^429^Guard Slip'kik^7.69^0^k
e9v|Barrier Shield|w|||||o^Gordok Tribute^20^k
e9w|Tarnished Elven Ring|w|||||o^Gordok Tribute^33.33^k
e9y|Monstrous Glaive|d|||||d^429^Captain Kromcrush^25^0^k
e9z|Kromcrush's Chestplate|d|||||d^429^Captain Kromcrush^25^0^k
ea0|Girdle of Insight|c|||||c^Leatherworking^290^22921^f
ea1|Mugger's Belt|d|||||d^429^Captain Kromcrush^25^0^k
ea2|Mongoose Boots|c|||||c^Leatherworking^290^22922^f
ea3|Boots of the Full Moon|d|||||d^429^Captain Kromcrush^25^0^k
ea4|Swift Flight Bracers|c|||||c^Leatherworking^290^22923^f
ea5|Chromatic Cloak|c|||||c^Leatherworking^300^22926^f
ea6|Hide of the Wild|c|||||c^Leatherworking^300^22927^f
ea7|Shifting Cloak|c|||||c^Leatherworking^300^22928^f
eag|Barbarous Blade|d|||||d^429^King Gordok^25^0^k
eah|Grimy Metal Boots|d|||||d^429^King Gordok^25^0^k
eai|Band of the Ogre King|d|||||d^429^King Gordok^25^0^k
eaj|Brightly Glowing Stone|d|||||d^429^King Gordok^25^0^k
eak|Leggings of Destruction|d|||||d^429^King Gordok^25^0^k
eal|Bracers of Prosperity|d|||||d^429^King Gordok^25^0^k
ean|Harmonious Gauntlets|d|||||d^429^King Gordok^25^0^k
eao|Cyclone Spaulders|dw|||||d^429^Gordok Mastiff^0.02^0^k
eap|Elemental Plate Girdle|w|||||o^Gordok Tribute^33.33^k
eaq|Ogre Forged Hauberk|dw|||||d^429^Gordok Mastiff^0.02^0^k
ear|Unyielding Maul|w|||||o^Gordok Tribute^20^k
eas|Mindsurge Robe|w|||||o^Gordok Tribute^20^k
eat|Gordok Bracers of Power|dw|||||d^429^Gordok Mastiff^0.02^0^k
eau|Rod of the Ogre Magi|w|||||o^Gordok Tribute^24.75^k
eav|Milli's Shield|q|||||q^5526^Shards of the Felvine^56^^k
eaw|Milli's Lexicon|q|||||q^5526^Shards of the Felvine^56^^k
eay|Treant's Bane|w|||||o^Gordok Tribute^1^k
eb3|Ring of Entropy|w|||||m^12397^Lord Kazzak^19^k
ec9|Band of Allegiance|q||h|||q^7541^Service to the Horde^40^h^k
eca|Lonetree's Circle|q||h|||q^7541^Service to the Horde^40^h^k
ecq|Tome of Sacrifice|q|U||||q^7583^Suppression^60^^k
ecw|Benediction|u|U||||
ecx|Anathema|u|U||||
ecy|Keen Machete|w|||||w^0^0^k
ecz|Gnarlpine Leggings|w|||||w^0^0^k
ed0|Bloody Chain Boots|w|||||w^0^0^k
een|Baron Charr's Sceptre|w|||||w^0^0^k
eeo|Elemental Ember|w|||||w^0^0^k
eeq|Hardened Stone Band|w|||||w^0^0^k
ees|Sash of the Windreaver|w|||||w^0^0^k
eev|Frigid Ring|w|||||w^0^0^k
eew|Ancient Bone Bow|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
eex|Burial Shawl|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
eey|Ghoul Skin Leggings|d|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
eez|Hammer of the Vesper|dx|||||d^289^Lord Alexei Barov^3.7^0^k~d^289^Instructor Malicia^1.11^0^k
ef2|Bone Golem Shoulders|d|||||d^289^Rattlegore^14^0^k
ef5|Phantasmal Cloak|d|||||d^289^Jandice Barov^11.86^0^k
ef6|Wraithplate Leggings|d|||||d^289^Jandice Barov^11.86^0^k
ef7|Dark Advisor's Pendant|d|||||d^289^Vectus^7^0^k
ef8|Death Knight Sabatons|d|||||d^289^Marduk Blackpool^7^0^k
ef9|Shivery Handwraps|d|||||d^289^Ras Frostwhisperer^16.67^0^k
efb|Spellbound Tome|d|||||d^289^Ras Frostwhisperer^16.67^0^k
efc|Intricately Runed Shield|d|||||d^289^Ras Frostwhisperer^16.67^0^k
efd|Coldstone Slippers|w|||||w^0^0^k
efe|Tattered Leather Hood|w|||||w^0^0^k
eff|Icy Tomb Spaulders|w|||||w^0^0^k
efg|Malefic Bracers|w|||||w^0^0^k
efh|Innervating Band|w|||||w^0^0^k
efi|Belt of the Ordained|w|||||w^0^0^k
efm|Arena Master|w||||LArenaMaster|o^Arena Treasure Chest^100^k
efp|Arena Wristguards|w|||||o^Arena Treasure Chest^7^k
efq|Arena Bracers|w|||||o^Arena Treasure Chest^7^k
efr|Arena Bands|w|||||o^Arena Treasure Chest^7^k
efs|Arena Vambraces|w|||||o^Arena Treasure Chest^7^k
efw|Ash Covered Boots|d|||||d^329^Archivist Galford^22^0^k
eg0|Shroud of the Nathrezim|d|||||d^329^Balnazzar^20^0^k
eg1|Barrage Girdle|d|||||d^329^Cannon Master Willey^20^0^k
eg2|Death Grips|d|||||d^329^Magistrate Barthilas^16.67^0^k
eg3|Animated Chain Necklace|d|||||d^329^Ramstein the Gorger^14.67^0^k
eg5|Peacemaker|d|||||d^329^Magistrate Barthilas^16.67^0^k
eg6|Magistrate's Cuffs|d|||||d^329^Magistrate Barthilas^16.67^0^k
eg7|Crimson Felt Hat|d|||||d^329^Magistrate Barthilas^16.67^0^k
eg8|Anastari Heirloom|d|||||d^329^Baroness Anastari^20^0^k
eg9|Screeching Bow|d|||||d^329^Baroness Anastari^20^0^k
ega|Shadowy Laced Handwraps|d|||||d^329^Baroness Anastari^20^0^k
ege|Pale Moon Cloak|d|||||d^329^Maleki the Pallid^20^0^k
egf|Maleki's Footwraps|d|||||d^329^Maleki the Pallid^20^0^k
egg|Plaguehound Leggings|w|||||w^0^0^k
egh|Bone Slicing Hatchet|d|||||d^329^Maleki the Pallid^20^0^k
egi|Carapace Spine Crossbow|d|||||d^329^Nerub'enkan^20^0^k
egj|Chitinous Plate Legguards|d|||||d^329^Nerub'enkan^20^0^k
egk|Thuzadin Sash|d|||||d^329^Nerub'enkan^20^0^k
egl|Morlune's Bracer|w|||||w^0^0^k
egm|Stratholme Militia Shoulderguard|dw|||||d^329^Malor the Zealous^0.02^0^k
egn|Gracious Cape|w|||||w^55^61^k
ego|Plaguebat Fur Gloves|w|||||w^55^61^k
egp|Sacred Cloth Leggings|dw|||||d^329^Malor the Zealous^0.02^0^k
egy|Fel Hardened Bracers|d|||||d^429^Lord Hel'nurath^25^0^k
egz|Xorothian Firestick|d|||||d^429^Lord Hel'nurath^25^0^k
eh0|Dreadguard's Protector|d|||||d^429^Lord Hel'nurath^25^0^k
eh1|Diabolic Mantle|d|||||d^429^Lord Hel'nurath^25^0^k
eh2|Specter's Blade|w|||||m^14516^Death Knight Darkreaver^25^k
eh3|Malicious Axe|w|||||m^14516^Death Knight Darkreaver^25^k
eh5|Oblivion's Touch|w|||||m^14516^Death Knight Darkreaver^25^k
eh6|Shard of the Green Flame|q|||||q^7603^Kroshius' Infernal Core^50^^k
eix|Grand Marshal's Aegis|p||a|18826||p^14^a^f
eiy|High Warlord's Shield Wall|p||h|18825||p^14^h^f
eiz|Grand Marshal's Handaxe|p||a|18828||p^14^a^f
ej0|High Warlord's Cleaver|p||h|18827||p^14^h^f
ej2|Grand Marshal's Sunderer|p||a|18831||p^14^a^f
ej3|High Warlord's Battle Axe|p||h|18830||p^14^h^f
ej5|Grand Marshal's Bullseye|p||a|18835||p^14^a^f
ej7|High Warlord's Recurve|p||h|18833||p^14^h^f
ej8|Grand Marshal's Repeater|p||a|18837||p^14^a^f
ej9|High Warlord's Crossbow|p||h|18836||p^14^h^f
eja|Grand Marshal's Dirk|p||a|18840||p^14^a^f
ejc|High Warlord's Razor|p||h|18838||p^14^h^f
ejf|Grand Marshal's Right Hand Blade|p||a|18844||p^14^a^f
ejg|High Warlord's Right Claw|p||h|18843||p^14^h^f
ejj|Grand Marshal's Left Hand Blade|p||a|18848||p^14^a^f
ejk|High Warlord's Left Claw|p||h|18847||p^14^h^f
ejr|Grand Marshal's Hand Cannon|p||a|18860||p^14^a^f
ejw|High Warlord's Street Sweeper|p||h|18855||p^14^h^f
ek1|Grand Marshal's Punisher|p||a|18866||p^14^a^f
ek2|High Warlord's Bludgeon|p||h|18865||p^14^h^f
ek3|Grand Marshal's Battle Hammer|p||a|18868||p^14^a^f
ek4|High Warlord's Pulverizer|p||h|18867||p^14^h^f
ek5|Grand Marshal's Glaive|p||a|18871||p^14^a^f
ek7|High Warlord's Pig Sticker|p||h|18869||p^14^h^f
ek9|Grand Marshal's Stave|p||a|||p^14^a^f
eka|High Warlord's War Staff|p||h|||p^14^h^f
ekc|Grand Marshal's Claymore|p||a|18877||p^14^a^f
ekd|High Warlord's Greatsword|p||h|18876||p^14^h^f
emc|Barbaric Bracers|c|||||c^Leatherworking^130^23399^f
emf|Evonice's Landin' Pilla|q|||||q^7704^Look at the Size of It!^45^^k
eml|Brushwood Blade|q|s|a|||q^2561^Druid of the Claw^5^a^s
eob|Thunderfury, Blessed Blade of the Windseeker|q|U||||q^7787^Rise, Thunderfury!^60^^k
eog|Arena Grand Master|u||||LArenaMaster|
eot|Emerald Peak Spaulders|q||h|||q^7732^Zukk'ash Report^43^h^k
eou|Ring of Subtlety|q||h|||q^7732^Zukk'ash Report^43^h^k
eov|Zorbin's Water Resistant Hat|q|s||||q^7721^Fuel for the Zapping^45^^s
eow|Zorbin's Mega-Slicer|q|s||||q^7003^Zapped Giants^45^^s
eox|Pratt's Handcrafted Tunic|q||a|19042||q^7733^Improved Quality^43^a^k
eoy|Jangdor's Handcrafted Tunic|q||h|19041||q^7734^Improved Quality^43^h^k
eoz|Heavy Timbermaw Belt|c|||||c^Leatherworking^265^23628^f
ep0|Might of the Timbermaw|c|||||c^Leatherworking^265^23703^f
ep3|Wisdom of the Timbermaw|c|||||c^Tailoring^255^23662^f
ep4|Heavy Timbermaw Boots|c|||||c^Leatherworking^295^23629^f
ep5|Timbermaw Brawlers|c|||||c^Leatherworking^295^23704^f
ep6|Mantle of the Timbermaw|c|||||c^Tailoring^290^23663^f
ep7|Girdle of the Dawn|c|||||c^Blacksmithing^265^23632^f
ep8|Dawn Treaders|c|||||c^Leatherworking^265^23705^f
epc|Argent Boots|c|||||c^Tailoring^255^23664^f
epd|Gloves of the Dawn|c|||||c^Blacksmithing^300^23633^f
epe|Golden Mantle of the Dawn|c|||||c^Leatherworking^295^23706^f
epf|Argent Shoulders|c|||||c^Tailoring^290^23665^f
eq3|Frostwolf Legionnaire's Cloak|v||h|19084||V^13219^75224^h^k
eq4|Stormpike Soldier's Cloak|v|s|a|19083||V^13217^75500^a^s
eq5|Frostwolf Advisor's Cloak|v||h|19086||V^13219^75776^h^k
eq6|Stormpike Sage's Cloak|v|s|a|19085||V^13217^76045^a^s
eq7|Frostwolf Plate Belt|v||h|19091||V^13219^50881^h^k
eq8|Frostwolf Mail Belt|v||h|19092||V^13219^76597^h^k
eq9|Frostwolf Leather Belt|v||h|19093||V^13219^59304^h^k
eqa|Frostwolf Cloth Belt|v||h|19094||V^13219^51428^h^k
eqb|Stormpike Plate Girdle|v|s|a|19087||V^13217^47443^a^s
eqc|Stormpike Mail Girdle|v|s|a|19088||V^13217^71165^a^s
eqd|Stormpike Leather Girdle|v|s|a|19089||V^13217^59304^a^s
eqe|Stormpike Cloth Girdle|v|s|a|19090||V^13217^47443^a^s
eqf|Frostwolf Legionnaire's Pendant|v||h|19097||V^13219^71648^h^k
eqg|Frostwolf Advisor's Pendant|v||h|19098||V^13219^71648^h^k
eqh|Stormpike Soldier's Pendant|v|s|a|19095||V^13217^71648^a^s
eqi|Stormpike Sage's Pendant|v|s|a|19096||V^13217^71648^a^s
eql|Whiteout Staff|vw|U|h|||V^13219^397057^h^k~m^13218^Grunnda Wolfheart^0.02^k
eqm|Crackling Staff|v|sU|a|||V^13217^398525^a^s
eqn|Frostbite|vw|U|h|||V^13219^319995^h^k~m^13218^Grunnda Wolfheart^0.02^k
eqq|Ice Barbed Spear|q|||||q^7181^The Legend of Korrak^55^h^k~q^7202^Korrak the Bloodrager^55^a^k
eqr|Bloodseeker|q|||||q^7181^The Legend of Korrak^55^h^k~q^7202^Korrak the Bloodrager^55^a^k
eqs|Wand of Biting Cold|q|||||q^7181^The Legend of Korrak^55^h^k~q^7202^Korrak the Bloodrager^55^a^k
eqt|Deep Rooted Ring|w|||||m^13419^Ivus the Forest Lord^33.8^k~m^13256^Lokholar the Ice Lord^26.88^k
eqy|Highland Bow|q||h|||q^7847^Return to Primal Torntusk^46^h^k
eqz|Flask of Forest Mojo|q||h|||q^7847^Return to Primal Torntusk^46^h^k
er0|Greenleaf Handwraps|q||h|||q^7849^Separation Anxiety^46^h^k
er1|Laquered Wooden Plate Legplates|q||h|||q^7849^Separation Anxiety^46^h^k
er2|Nature's Breath|q||h|||q^7850^Dark Vessels^46^h^k
er3|Owlbeast Hide Gloves|q||h|||q^7843^The Final Message to the Wildhammer^45^h^k
er4|Rune of the Guard Captain|q||h|||q^7862^Job Opening: Guard Captain of Revantusk Village^46^h^k
er5|Deep Woodlands Cloak|q||h|||q^7861^Wanted: Vile Priestess Hexx and Her Minions^46^h^k
er7|Everwarm Handwraps|q|||||q^7728^STOLEN: Smithing Tuyere and Lookout's Spyglass^45^^k
er8|Slagplate Leggings|q|||||q^7728^STOLEN: Smithing Tuyere and Lookout's Spyglass^45^^k
er9|Seared Mail Girdle|q|||||q^7724^Fiery Menace!^45^^k
era|Slagplate Gauntlets|q|||||q^7723^Curse These Fat Fingers^45^^k
erb|Charred Leather Tunic|q|||||q^7701^WANTED: Overseer Maltorius^45^^k
erc|Seared Mail Vest|q|||||q^7701^WANTED: Overseer Maltorius^45^^k
ero|Cauterizing Band|w|||||m^11664^Flamewaker Elite^0.46^k~m^11663^Flamewaker Healer^0.14^k
erw|Dark Iron Helm|c|||||c^Blacksmithing^300^23636^f
erx|Lava Belt|c|||||c^Leatherworking^300^23707^f
es4|Flarecore Robe|c|||||c^Tailoring^300^23666^f
es5|Chromatic Gauntlets|c|||||c^Leatherworking^300^23708^f
es7|Woven Ivy Necklace|q||h|||q^7861^Wanted: Vile Priestess Hexx and Her Minions^46^h^k
esa|Corehound Belt|c|||||c^Leatherworking^300^23709^f
esb|Molten Belt|c|||||c^Leatherworking^300^23710^f
esd|Flarecore Leggings|c|||||c^Tailoring^300^23667^f
ese|Black Amnesty|c|||||c^Blacksmithing^300^23638^f
esf|Blackfury|c|||||c^Blacksmithing^300^23639^f
esg|Blackguard|c|||||c^Blacksmithing^300^23652^f
esh|Nightfall|c|||||c^Blacksmithing^300^23653^f
esi|Ebon Hand|c|||||c^Blacksmithing^300^23650^f
evw|Last Month's Mutton|v|s||||V^14828^0^^s
evx|Last Year's Mutton|v|s||||V^14828^0^^s
ew6|Darkmoon Ring|v|s||||V^14846^75763^^s
ew7|Darkmoon Necklace|v|s||||V^14846^50000^^s
ewc|Tome of Arcane Domination|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewd|Tome of Shadow Force|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewe|Tome of the Ice Lord|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewf|Tome of Fiery Arcana|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewg|Lei of the Lifegiver|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewj|Therazane's Touch|vw|sU||||V^13217^500000^^s~m^13218^Grunnda Wolfheart^0.02^k
ewp|The Immovable Object|vw|sU||||V^13217^795297^^s~m^13218^Grunnda Wolfheart^0.02^k
ewr|The Unstoppable Force|vw|sU||||V^13217^1564900^^s~m^13218^Grunnda Wolfheart^0.02^k
ews|The Lobotomizer|vw|sU||||V^13217^1256618^^s~m^13218^Grunnda Wolfheart^0.02^k
ewt|Don Julio's Band|vw|sU||||V^13217^755555^^s~m^13218^Grunnda Wolfheart^0.02^k
exy|Master Dragonslayer's Orb|q|||||q^7782^The Lord of Blackrock^60^a^k~q^7784^The Lord of Blackrock^60^h^k
eyf|Master Dragonslayer's Medallion|q|U||||q^7782^The Lord of Blackrock^60^a^k~q^7784^The Lord of Blackrock^60^h^k
eyg|Master Dragonslayer's Ring|q|U||||q^7782^The Lord of Blackrock^60^a^k~q^7784^The Lord of Blackrock^60^h^k
ezm|Orb of the Darkmoon|v|s||||V^14828^0^^s
f1f|Amulet of the Darkmoon|v|s||||V^14828^0^^s
f1v|Inquisitor's Shawl|d|s||||d^189^High Inquisitor Fairbanks^0^0^s
f1w|Branded Leather Bracers|d|s||||d^189^High Inquisitor Fairbanks^100^0^s
f1x|Dusty Mail Boots|d|s||||d^189^High Inquisitor Fairbanks^33.33^0^k
f1y|Legionnaire's Band|v|U|h|19514||V^14754^75000^h^s
f1z|Legionnaire's Band|v|U|h|19516||V^14754^60000^h^s
f20|Legionnaire's Band|v|U|h|19515||V^14754^45000^h^s
f21|Legionnaire's Band|v|U|h|19517||V^14754^20000^h^s
f22|Protector's Band|v|sU|a|19510||V^14753^75000^a^s
f23|Protector's Band|v|sU|a|19512||V^14753^45000^a^s
f24|Protector's Band|v|sU|a|19511||V^14753^60000^a^s
f25|Protector's Band|v|sU|a|19513||V^14753^20000^a^s
f26|Advisor's Ring|v|U|h|19522||V^14754^75000^h^s
f27|Advisor's Ring|v|U|h|19523||V^14754^60000^h^s
f28|Advisor's Ring|v|U|h|19524||V^14754^45000^h^s
f29|Advisor's Ring|v|U|h|19525||V^14754^20000^h^s
f2a|Lorekeeper's Ring|v|sU|a|19518||V^14753^75000^a^s
f2b|Lorekeeper's Ring|v|sU|a|19519||V^14753^60000^a^s
f2c|Lorekeeper's Ring|v|sU|a|19520||V^14753^45000^a^s
f2d|Lorekeeper's Ring|v|sU|a|19521||V^14753^20000^a^s
f2e|Battle Healer's Cloak|v|U|h|19530||V^14754^90580^h^s
f2f|Battle Healer's Cloak|v|U|h|19531||V^14754^48159^h^s
f2g|Battle Healer's Cloak|v|U|h|19532||V^14754^23904^h^s
f2h|Battle Healer's Cloak|v|U|h|19533||V^14754^10613^h^s
f2i|Caretaker's Cape|v|sU|a|19526||V^14753^85492^a^s
f2j|Caretaker's Cape|v|sU|a|19527||V^14753^50242^a^s
f2k|Caretaker's Cape|v|sU|a|19528||V^14753^24934^a^s
f2l|Caretaker's Cape|v|sU|a|19529||V^14753^10772^a^s
f2m|Scout's Medallion|v|U|h|19538||V^14754^75000^h^s
f2n|Scout's Medallion|v|U|h|19539||V^14754^60000^h^s
f2o|Scout's Medallion|v|U|h|19540||V^14754^45000^h^s
f2p|Scout's Medallion|v|U|h|19541||V^14754^20000^h^s
f2q|Sentinel's Medallion|v|sU|a|19534||V^14753^75000^a^s
f2r|Sentinel's Medallion|v|sU|a|19535||V^14753^60000^a^s
f2s|Sentinel's Medallion|v|sU|a|19536||V^14753^45000^a^s
f2t|Sentinel's Medallion|v|sU|a|19537||V^14753^20000^a^s
f2u|Scout's Blade|v|U|h|19546||V^14754^297673^h^s
f2v|Scout's Blade|v|U|h|19547||V^14754^174910^h^s
f2w|Scout's Blade|v|U|h|19548||V^14754^86791^h^s
f2x|Scout's Blade|v|U|h|19549||V^14754^34845^h^s
f2y|Sentinel's Blade|v|sU|a|19542||V^14753^280715^a^s
f2z|Sentinel's Blade|v|sU|a|19543||V^14753^164981^a^s
f30|Sentinel's Blade|v|sU|a|19544||V^14753^81882^a^s
f31|Sentinel's Blade|v|sU|a|19545||V^14753^35372^a^s
f32|Legionnaire's Sword|v|U|h|19554||V^14754^274611^h^s
f33|Legionnaire's Sword|v|U|h|19555||V^14754^160783^h^s
f34|Legionnaire's Sword|v|U|h|19556||V^14754^79498^h^s
f35|Legionnaire's Sword|v|U|h|19557||V^14754^34217^h^s
f36|Protector's Sword|v|sU|a|19550||V^14753^274611^a^s
f37|Protector's Sword|v|sU|a|19551||V^14753^160783^a^s
f38|Protector's Sword|v|sU|a|19552||V^14753^79498^a^s
f39|Protector's Sword|v|sU|a|19553||V^14753^36427^a^s
f3a|Outrider's Bow|v||h|19562||V^14754^220059^h^s
f3b|Outrider's Bow|v||h|19563||V^14754^120587^h^s
f3c|Outrider's Bow|v||h|19564||V^14754^59624^h^s
f3d|Outrider's Bow|v||h|19565||V^14754^25663^h^s
f3e|Outrunner's Bow|v|s|a|19558||V^14753^205958^a^s
f3f|Outrunner's Bow|v|s|a|19559||V^14753^120587^a^s
f3g|Outrunner's Bow|v|s|a|19560||V^14753^59624^a^s
f3h|Outrunner's Bow|v|s|a|19561||V^14753^25663^a^s
f3i|Advisor's Gnarled Staff|v||h|19570||V^14754^350857^h^s
f3j|Advisor's Gnarled Staff|v||h|19571||V^14754^200979^h^s
f3k|Advisor's Gnarled Staff|v||h|19572||V^14754^99373^h^s
f3l|Advisor's Gnarled Staff|v||h|19573||V^14754^42771^h^s
f3m|Lorekeeper's Staff|v|s|a|19566||V^14753^356148^a^s
f3n|Lorekeeper's Staff|v|s|a|19567||V^14753^209282^a^s
f3o|Lorekeeper's Staff|v|s|a|19568||V^14753^103864^a^s
f3p|Lorekeeper's Staff|v|s|a|19569||V^14753^44870^a^s
f3s|Strength of Mugamba|Q|U||||q^8043^Strength of Mount Mugamba^60^^k
f3t|Rage of Mugamba|Q|U||||q^8044^The Rage of Mount Mugamba^60^^k
f3u|Berserker Bracers|v|sU||||V^14753^88497^^s
f3w|Berserker Bracers|v|sU||||V^14753^48175^^s
f3x|Berserker Bracers|v|sU||||V^14753^24727^^s
f3y|Windtalker's Wristguards|v|s||||V^14753^121103^^s
f3z|Windtalker's Wristguards|v|s||||V^14753^72262^^s
f40|Windtalker's Wristguards|v|s||||V^14753^37090^^s
f43|Forest Stalker's Bracers|v|s||||V^14753^100919^^s
f45|Forest Stalker's Bracers|v|s||||V^14753^60218^^s
f46|Forest Stalker's Bracers|v|s||||V^14753^30909^^s
f4b|Dryad's Wrist Bindings|v|s||||V^14753^87549^^s
f4c|Dryad's Wrist Bindings|v|s||||V^14753^52427^^s
f4d|Dryad's Wrist Bindings|v|s||||V^14753^27006^^s
f4g|Pebble of Kajaro|Q|U||||q^8103^The Pebble of Kajaro^60^^k
f4k|Kezan's Taint|Q|U||||q^8108^Kezan's Taint^60^^k
f4l|Kezan's Unstoppable Taint|Q|U||||q^8109^Kezan's Unstoppable Taint^60^^k
f4w|Zandalarian Shadow Talisman|Q|U||||q^8143^Zandalarian Shadow Talisman^60^^k
f4z|Maelstrom's Tendril|Q|U||||q^8146^The Maelstrom's Tendril^60^^k
f50|Maelstrom's Tendril|Q|U||||q^8147^The Maelstrom's Tendril^60^^k
f51|Maelstrom's Wrath|Q|U||||q^8148^The Maelstrom's Wrath^60^^k
f6q|Bloodvine Vest|c|||||c^Tailoring^300^24091^f
f6r|Bloodvine Leggings|c|||||c^Tailoring^300^24092^f
f6s|Bloodvine Boots|c|||||c^Tailoring^300^24093^f
f6t|Primal Batskin Jerkin|c|||||c^Leatherworking^300^24121^f
f6u|Primal Batskin Gloves|c|||||c^Leatherworking^300^24122^f
f6v|Primal Batskin Bracers|c|||||c^Leatherworking^300^24123^f
f6x|Blood Tiger Shoulders|c|||||c^Leatherworking^300^24125^f
f6y|Bloodsoul Breastplate|c|||||c^Blacksmithing^300^24136^f
f6z|Bloodsoul Shoulders|c|||||c^Blacksmithing^300^24137^f
f70|Bloodsoul Gauntlets|c|||||c^Blacksmithing^300^24138^f
f71|Darksoul Breastplate|c|||||c^Blacksmithing^300^24139^f
f72|Darksoul Leggings|c|||||c^Blacksmithing^300^24140^f
f73|Darksoul Shoulders|c|||||c^Blacksmithing^300^24141^f
fam|Zandalar Vindicator's Breastplate|Q|||||q^8079^Paragons of Power: The Vindicator's Breastplate^60^^k
fan|Zandalar Vindicator's Belt|Q|||||q^8078^Paragons of Power: The Vindicator's Belt^60^^k
fao|Zandalar Vindicator's Armguards|Q|||||q^8058^Paragons of Power: The Vindicator's Armguards^60^^k
fap|Zandalar Freethinker's Breastplate|Q|||||q^8055^Paragons of Power: The Freethinker's Breastplate^60^^k
faq|Zandalar Freethinker's Belt|Q|||||q^8054^Paragons of Power: The Freethinker's Belt^60^^k
far|Zandalar Freethinker's Armguards|Q|||||q^8053^Paragons of Power: The Freethinker's Armguards^60^^k
fas|Zandalar Augur's Hauberk|Q|||||q^8075^Paragons of Power: The Augur's Hauberk^60^^k
fat|Zandalar Augur's Belt|Q|||||q^8074^Paragons of Power: The Augur's Belt^60^^k
fau|Zandalar Augur's Bracers|Q|||||q^8056^Paragons of Power: The Augur's Bracers^60^^k
fav|Zandalar Predator's Mantle|Q|||||q^8067^Paragons of Power: The Predator's Mantle^60^^k
faw|Zandalar Predator's Belt|Q|||||q^8066^Paragons of Power: The Predator's Belt^60^^k
fax|Zandalar Predator's Bracers|Q|||||q^8062^Paragons of Power: The Predator's Bracers^60^^k
fay|Zandalar Madcap's Tunic|Q|||||q^8073^Paragons of Power: The Madcap's Tunic^60^^k
faz|Zandalar Madcap's Mantle|Q|||||q^8072^Paragons of Power: The Madcap's Mantle^60^^k
fb0|Zandalar Madcap's Bracers|Q|||||q^8063^Paragons of Power: The Madcap's Bracers^60^^k
fb2|Zandalar Haruspex's Tunic|Q|||||q^8065^Paragons of Power: The Haruspex's Tunic^60^^k
fb3|Zandalar Haruspex's Belt|Q|||||q^8064^Paragons of Power: The Haruspex's Belt^60^^k
fb4|Zandalar Haruspex's Bracers|Q|||||q^8057^Paragons of Power: The Haruspex's Bracers^60^^k
fb5|Zandalar Confessor's Mantle|Q|||||q^8071^Paragons of Power: The Confessor's Mantle^60^^k
fb6|Zandalar Confessor's Bindings|Q|||||q^8070^Paragons of Power: The Confessor's Bindings^60^^k
fb7|Zandalar Confessor's Wraps|Q|||||q^8061^Paragons of Power: The Confessor's Wraps^60^^k
fb9|Zandalar Illusionist's Mantle|Q|||||q^8068^Paragons of Power: The Illusionist's Mantle^60^^k
fba|Zandalar Illusionist's Wraps|Q|||||q^8060^Paragons of Power: The Illusionist's Wraps^60^^k
fbc|Zandalar Demoniac's Wraps|Q|||||q^8059^Paragons of Power: The Demoniac's Wraps^60^^k
fbd|Zandalar Demoniac's Mantle|Q|||||q^8076^Paragons of Power: The Demoniac's Mantle^60^^k
ff2|Duskbat Drape|q|||||q^8236^The Azure Key^50^^k
ff4|Ebon Mask|q|||||q^8236^The Azure Key^50^^k
ffa|Blessed Prayer Beads|Q|U||||q^8257^Blood of Morphaz^50^^k
ffb|Devilsaur Eye|q|U||||q^8232^The Green Drake^50^^k
ffc|Devilsaur Tooth|q|U||||q^8232^The Green Drake^50^^k
fgh|Zandalar Demoniac's Robe|Q|||||q^8077^Paragons of Power: The Demoniac's Robes^60^^k
fgi|Zandalar Illusionist's Robe|Q|||||q^8069^Paragons of Power: The Illusionist's Robes^60^^k
fgj|Glacial Spike|q|||||q^8253^Destroy Morphaz^50^^k
fgk|Fire Ruby|q|U||||q^8253^Destroy Morphaz^50^^k
fgl|Arcane Crystal Pendant|q|||||q^8253^Destroy Morphaz^50^^k
fgn|Dark Iron Boots|c|||||c^Blacksmithing^300^24399^f
fgp|Highlander's Plate Girdle|ev|sU|a|20204||V^15127^56764^a^s~r^509^5^The League of Arathor^f
fgq|Highlander's Lamellar Girdle|ev|sU|a|20177||V^15127^56972^a^s~r^509^5^The League of Arathor^f
fgr|Highlander's Chain Girdle|ev|sU|a|20150||V^15127^88066^a^s~r^509^5^The League of Arathor^f
fgs|Highlander's Mail Girdle|e|U|a|20195||r^509^5^The League of Arathor^f
fgt|Highlander's Leather Girdle|ev|sU|a|20190||V^15127^73921^a^s~r^509^5^The League of Arathor^f
fgu|Highlander's Lizardhide Girdle|ev|sU|a|20171||V^15127^74180^a^s~r^509^5^The League of Arathor^f
fgv|Highlander's Cloth Girdle|ev|sU|a|20163||V^15127^59557^a^s~r^509^5^The League of Arathor^f
fgw|Highlander's Plate Greaves|ev|sU|a|20208||V^15127^89656^a^s~r^509^6^The League of Arathor^f
fgx|Highlander's Lamellar Greaves|ev|sU|a|20181||V^15127^89975^a^s~r^509^6^The League of Arathor^f
fgy|Highlander's Chain Greaves|ev|sU|a|20154||V^15127^136031^a^s~r^509^6^The League of Arathor^f
fgz|Highlander's Mail Greaves|e|U|a|20199||r^509^6^The League of Arathor^f
fh0|Highlander's Leather Boots|ev|sU|a|20186||V^15127^102849^a^s~r^509^6^The League of Arathor^f
fh1|Highlander's Lizardhide Boots|ev|sU|a|20167||V^15127^103238^a^s~r^509^6^The League of Arathor^f
fh2|Highlander's Cloth Boots|ev|sU|a|20159||V^15127^82910^a^s~r^509^6^The League of Arathor^f
fh3|Highlander's Chain Pauldrons|ev|sU|a|20158||V^15127^184337^a^s~r^509^7^The League of Arathor^f
fh5|Highlander's Plate Spaulders|ev|sU|a|20212||V^15127^123274^a^s~r^509^7^The League of Arathor^f
fh6|Highlander's Lamellar Spaulders|ev|sU|a|20184||V^15127^123744^a^s~r^509^7^The League of Arathor^f
fh7|Highlander's Leather Shoulders|ev|sU|a|20194||V^15127^159473^a^s~r^509^7^The League of Arathor^f
fh8|Highlander's Lizardhide Shoulders|ev|sU|a|20175||V^15127^160061^a^s~r^509^7^The League of Arathor^f
fh9|Highlander's Epaulets|ev|sU|a|20176||V^15127^128505^a^s~r^509^7^The League of Arathor^f
fhg|Deathguard's Cloak|ev||h|20073||V^15126^131769^h^k
fhh|Ironbark Staff|ev|s|a|20220||V^15127^550995^a^s~r^509^7^The League of Arathor^f
fhi|Sageclaw|ev|s|a|20214||V^15127^442362^a^s~r^509^7^The League of Arathor^f
fhj|Talisman of Arathor|ev|s|a|20072|LTalismanofBattle|V^15127^41230^a^s~r^509^4^The League of Arathor^f
fhk|Defiler's Talisman|ev||h|20071|LTalismanofBattle|V^15126^41230^h^k
fhl|Cloak of the Honor Guard|ev|s|a|20068||V^15127^121395^a^s~r^509^7^The League of Arathor^f
fhu|Woestave|Q|||||q^8257^Blood of Morphaz^50^^k
fhv|Hunting Spear|q|||||q^8232^The Green Drake^50^^k
fhy|Dusksteel Throwing Knife|q|||||q^8249^Junkboxes Needed^55^^k
fi0|Highlander's Chain Girdle|ev|sU|a|20151||V^15127^52478^a^s~r^509^5^The League of Arathor^f
fi1|Highlander's Chain Girdle|ev|sU|a|20153||V^15127^26040^a^s~r^509^5^The League of Arathor^f
fi2|Highlander's Chain Girdle|ev|sU|a|20152||V^15127^9373^a^s~r^509^5^The League of Arathor^f
fi3|Highlander's Chain Greaves|ev|sU|a|20155||V^15127^74297^a^s~r^509^6^The League of Arathor^f
fi4|Highlander's Chain Greaves|ev|sU|a|20156||V^15127^36875^a^s~r^509^6^The League of Arathor^f
fi5|Highlander's Chain Greaves|ev|sU|a|20157||V^15127^13217^a^s~r^509^6^The League of Arathor^f
fi6|Highlander's Cloth Boots|ev|sU|a|20160||V^15127^49873^a^s~r^509^6^The League of Arathor^f
fi7|Highlander's Cloth Boots|ev|sU|a|20161||V^15127^24749^a^s~r^509^6^The League of Arathor^f
fi8|Highlander's Cloth Boots|ev|sU|a|20162||V^15127^10692^a^s~r^509^6^The League of Arathor^f
fi9|Highlander's Cloth Girdle|ev|sU|a|20165||V^15127^33619^a^s~r^509^5^The League of Arathor^f
fia|Highlander's Cloth Girdle|ev|sU|a|20166||V^15127^16684^a^s~r^509^5^The League of Arathor^f
fib|Highlander's Cloth Girdle|ev|sU|a|20164||V^15127^7207^a^s~r^509^5^The League of Arathor^f
fic|Highlander's Lizardhide Boots|ev|sU|a|20170||V^15127^63732^a^s~r^509^6^The League of Arathor^f
fid|Highlander's Lizardhide Boots|ev|sU|a|20168||V^15127^31628^a^s~r^509^6^The League of Arathor^f
fie|Highlander's Lizardhide Boots|ev|sU|a|20169||V^15127^13661^a^s~r^509^6^The League of Arathor^f
fif|Highlander's Lizardhide Girdle|ev|sU|a|20174||V^15127^42952^a^s~r^509^5^The League of Arathor^f
fig|Highlander's Lizardhide Girdle|ev|sU|a|20173||V^15127^21314^a^s~r^509^5^The League of Arathor^f
fih|Highlander's Lizardhide Girdle|ev|sU|a|20172||V^15127^9207^a^s~r^509^5^The League of Arathor^f
fii|Highlander's Lamellar Girdle|ev|sU|a|20179||V^15127^34732^a^s~r^509^5^The League of Arathor^f
fij|Highlander's Lamellar Girdle|ev|sU|a|20180||V^15127^16008^a^s~r^509^5^The League of Arathor^f
fik|Highlander's Lamellar Girdle|ev|sU|a|20178||V^15127^10375^a^s~r^509^5^The League of Arathor^f
fil|Highlander's Lamellar Greaves|ev|sU|a|20185||V^15127^48938^a^s~r^509^6^The League of Arathor^f
fim|Highlander's Lamellar Greaves|ev|sU|a|20183||V^15127^24287^a^s~r^509^6^The League of Arathor^f
fin|Highlander's Lamellar Greaves|ev|sU|a|20182||V^15127^15810^a^s~r^509^6^The League of Arathor^f
fio|Highlander's Leather Boots|ev|sU|a|20189||V^15127^61868^a^s~r^509^6^The League of Arathor^f
fip|Highlander's Leather Boots|ev|sU|a|20187||V^15127^30705^a^s~r^509^6^The League of Arathor^f
fiq|Highlander's Leather Boots|ev|sU|a|20188||V^15127^13264^a^s~r^509^6^The League of Arathor^f
fir|Highlander's Leather Girdle|ev|sU|a|20193||V^15127^41708^a^s~r^509^5^The League of Arathor^f
fis|Highlander's Leather Girdle|ev|sU|a|20192||V^15127^20699^a^s~r^509^5^The League of Arathor^f
fit|Highlander's Leather Girdle|ev|sU|a|20191||V^15127^8941^a^s~r^509^5^The League of Arathor^f
fiu|Highlander's Mail Girdle|e|U|a|20196||r^509^5^The League of Arathor^f
fiv|Highlander's Mail Girdle|e|U|a|20198||r^509^5^The League of Arathor^f
fiw|Highlander's Mail Girdle|e|U|a|20197||r^509^5^The League of Arathor^f
fix|Highlander's Mail Greaves|e|U|a|20202||r^509^6^The League of Arathor^f
fiy|Highlander's Mail Greaves|e|U|a|20200||r^509^6^The League of Arathor^f
fiz|Highlander's Mail Greaves|e|U|a|20201||r^509^6^The League of Arathor^f
fj0|Highlander's Plate Girdle|ev|sU|a|20205||V^15127^35376^a^s~r^509^5^The League of Arathor^f
fj1|Highlander's Plate Girdle|ev|sU|a|20206||V^15127^15883^a^s~r^509^5^The League of Arathor^f
fj2|Highlander's Plate Girdle|ev|sU|a|20207||V^15127^10294^a^s~r^509^5^The League of Arathor^f
fj3|Highlander's Plate Greaves|ev|sU|a|20211||V^15127^48558^a^s~r^509^6^The League of Arathor^f
fj4|Highlander's Plate Greaves|ev|sU|a|20209||V^15127^24102^a^s~r^509^6^The League of Arathor^f
fj5|Highlander's Plate Greaves|ev|sU|a|20210||V^15127^15688^a^s~r^509^6^The League of Arathor^f
fja|Skyfury Helm|q||h|||q^8258^The Darkreaver Menace^60^h^k
fjq|Defiler's Chain Girdle|ev|U|h|20043||V^15126^83877^h^k
fjr|Defiler's Chain Girdle|ev|U|h|20088||V^15126^49292^h^k
fjs|Defiler's Chain Girdle|ev|U|h|20090||V^15126^8774^h^k
fjt|Defiler's Chain Girdle|ev|U|h|20089||V^15126^24557^h^k
fju|Defiler's Chain Greaves|ev|U|h|20050||V^15126^128288^h^k
fjv|Defiler's Chain Greaves|ev|U|h|20091||V^15126^75386^h^k
fjw|Defiler's Chain Greaves|ev|U|h|20092||V^15126^38412^h^k
fjx|Defiler's Chain Greaves|ev|U|h|20093||V^15126^13766^h^k
fjy|Defiler's Chain Pauldrons|ev|U|h|20055||V^15126^196466^h^k
fjz|Defiler's Cloth Boots|ev|U|h|20054||V^15126^89016^h^k
fk0|Defiler's Cloth Boots|ev|U|h|20094||V^15126^52306^h^k
fk1|Defiler's Cloth Boots|ev|U|h|20095||V^15126^25955^h^k
fk2|Defiler's Cloth Boots|ev|U|h|20096||V^15126^11211^h^k
fk3|Defiler's Cloth Girdle|ev|U|h|20047||V^15126^60191^h^k
fk4|Defiler's Cloth Girdle|ev|U|h|20099||V^15126^7526^h^k
fk5|Defiler's Cloth Girdle|ev|U|h|20097||V^15126^32116^h^k
fk6|Defiler's Cloth Girdle|ev|U|h|20098||V^15126^15939^h^k
fk7|Defiler's Lizardhide Boots|ev|U|h|20053||V^15126^103637^h^k
fk8|Defiler's Lizardhide Boots|ev|U|h|20101||V^15126^30118^h^k
fk9|Defiler's Lizardhide Boots|ev|U|h|20102||V^15126^13013^h^k
fka|Defiler's Lizardhide Boots|ev|U|h|20100||V^15126^61374^h^k
fkb|Defiler's Lizardhide Girdle|ev|U|h|20046||V^15126^70149^h^k
fkc|Defiler's Lizardhide Girdle|ev|U|h|20105||V^15126^9011^h^k
fkd|Defiler's Lizardhide Girdle|ev|U|h|20104||V^15126^21014^h^k
fke|Defiler's Lizardhide Girdle|ev|U|h|20103||V^15126^42652^h^k
fkf|Defiler's Lizardhide Shoulders|ev|U|h|20060||V^15126^161219^h^k
fkg|Defiler's Epaulets|ev|U|h|20061||V^15126^129445^h^k
fkh|Defiler's Lamellar Girdle|ev|U|h|20042||r^510^5^The Defilers^f
fki|Defiler's Lamellar Girdle|ev|U|h|20108||r^510^5^The Defilers^f
fkj|Defiler's Lamellar Girdle|ev|U|h|20106||r^510^5^The Defilers^f
fkk|Defiler's Lamellar Girdle|ev|U|h|20107||r^510^5^The Defilers^f
fkl|Defiler's Lamellar Greaves|ev|U|h|20049||r^510^6^The Defilers^f
fkm|Defiler's Lamellar Greaves|ev|U|h|20111||r^510^6^The Defilers^f
fkn|Defiler's Lamellar Greaves|ev|U|h|20110||r^510^6^The Defilers^f
fko|Defiler's Lamellar Spaulders|ev|U|h|20058||r^510^7^The Defilers^f
fkp|Defiler's Lamellar Greaves|ev|U|h|20109||r^510^6^The Defilers^f
fkq|Defiler's Leather Boots|ev|U|h|20052||V^15126^103227^h^k
fkr|Defiler's Leather Boots|ev|U|h|20113||V^15126^29999^h^k
fks|Defiler's Leather Boots|ev|U|h|20114||V^15126^13318^h^k
fkt|Defiler's Leather Boots|ev|U|h|20112||V^15126^62809^h^k
fku|Defiler's Leather Girdle|ev|U|h|20045||V^15126^71783^h^k
fkv|Defiler's Leather Girdle|ev|U|h|20117||V^15126^8977^h^k
fkw|Defiler's Leather Girdle|ev|U|h|20116||V^15126^20935^h^k
fkx|Defiler's Leather Girdle|ev|U|h|20115||V^15126^42492^h^k
fky|Defiler's Leather Shoulders|ev|U|h|20059||V^15126^160616^h^k
fkz|Defiler's Mail Girdle|e|U|h|20044||V^15126^87729^h^k
fl0|Defiler's Mail Girdle|e|U|h|20118||V^15126^51547^h^k
fl1|Defiler's Mail Girdle|e|U|h|20120||V^15126^9174^h^k
fl2|Defiler's Mail Girdle|e|U|h|20119||V^15126^25672^h^k
fl3|Defiler's Mail Greaves|e|U|h|20051||V^15126^134092^h^k
fl4|Defiler's Mail Greaves|e|U|h|20122||V^15126^38954^h^k
fl5|Defiler's Mail Greaves|e|U|h|20123||V^15126^13960^h^k
fl6|Defiler's Mail Greaves|e|U|h|20121||V^15126^79348^h^k
fl8|Defiler's Plate Girdle|ev|U|h|20041||V^15126^56148^h^k
fl9|Defiler's Plate Girdle|ev|U|h|20124||V^15126^32999^h^k
fla|Defiler's Plate Girdle|ev|U|h|20125||V^15126^16378^h^k
flb|Defiler's Plate Girdle|ev|U|h|20126||V^15126^10613^h^k
flc|Defiler's Plate Greaves|ev|U|h|20048||V^15126^85492^h^k
fld|Defiler's Plate Greaves|ev|U|h|20128||V^15126^24842^h^k
fle|Defiler's Plate Greaves|ev|U|h|20129||V^15126^16170^h^k
flf|Defiler's Plate Greaves|ev|U|h|20127||V^15126^50612^h^k
flg|Defiler's Plate Spaulders|ev|U|h|20057||V^15126^127540^h^k
flh|Belt of Shrunken Heads|Q|||||q^8201^A Collection of Heads^58^^k
fli|Mindfang|ev||h|20070||V^15126^428268^h^k
flj|Belt of Shriveled Heads|Q|||||q^8201^A Collection of Heads^58^^k
flk|Belt of Preserved Heads|Q|||||q^8201^A Collection of Heads^58^^k
fll|Belt of Tiny Heads|Q|||||q^8201^A Collection of Heads^58^^k
flm|Faded Hakkari Cloak|Q|||||q^8181^Confront Yeh'kinya^53^^k
fln|Tattered Hakkari Cape|Q|||||q^8181^Confront Yeh'kinya^53^^k
flo|Ironbark Staff|ev||h|20069||V^15126^504598^h^k
fmn|Whisperwalk Boots|q|||||q^8236^The Azure Key^50^^k
fnr|Blue Dragonscale Leggings|c|||||c^Leatherworking^300^24654^f
fns|Green Dragonscale Gauntlets|c|||||c^Leatherworking^275^24655^f
fpt|Azurite Fists|q||h|||q^8413^Da Voodoo^50^h^k
fqu|Twilight Cultist Mantle|Rw|||||m^11880^Twilight Avenger^8^k~m^11881^Twilight Geolord^8^k
frd|Advisor's Gnarled Staff|v||h|20434||V^14754^15211^h^s
fre|Advisor's Ring|v|U|h|20431||V^14754^20000^h^s
frf|Battle Healer's Cloak|v|U|h|20428||V^14754^3650^h^s
frg|Caretaker's Cape|v|sU|a|20427||V^14753^3650^a^s
frh|Legionnaire's Band|v|U|h|20439||V^14754^20000^h^s
fri|Legionnaire's Sword|v|U|h|20440||V^14754^12169^h^s
frj|Lorekeeper's Ring|v|sU|a|20426||V^14753^20000^a^s
frm|Lorekeeper's Staff|v|s|a|20425||V^14753^15211^a^s
frp|Outrider's Bow|v||h|20438||V^14754^9126^h^s
frq|Outrunner's Bow|v|s|a|20437||V^14753^9126^a^s
frr|Protector's Band|v|sU|a|20429||V^14753^20000^a^s
frs|Protector's Sword|v|sU|a|20430||V^14753^12910^a^s
frt|Scout's Blade|v|U|h|20443||V^14754^12169^h^s
fru|Scout's Medallion|v|U|h|20444||V^14754^20000^h^s
frv|Sentinel's Blade|v|sU|a|20441||V^14753^13050^a^s
frw|Sentinel's Medallion|v|sU|a|20442||V^14753^20000^a^s
ftj|Enamored Water Spirit|q|U|h|||q^8413^Da Voodoo^50^h^k
ftk|Lightforged Blade|q||a|||q^8418^Forging the Mightstone^50^a^k
ftl|Chivalrous Signet|q|U|a|||q^8418^Forging the Mightstone^50^a^k
fts|Sanctified Orb|q|U|a|||q^8418^Forging the Mightstone^50^a^k
ftx|Razorsteel Shoulders|q|||||q^8425^Voodoo Feathers^50^^k
fu1|Fury Visor|q|||||q^8425^Voodoo Feathers^50^^k
fua|Robes of Servitude|q|||||q^8422^Trolls of a Feather^50^^k
fue|Abyss Shard|q|U||||q^8422^Trolls of a Feather^50^^k
fug|Soul Harvester|q|||||q^8422^Trolls of a Feather^50^^k
fui|Runed Stygian Leggings|c|||||c^Tailoring^285^24901^f
fv0|Wildstaff|q||h|||q^8413^Da Voodoo^50^h^k
fvo|Hammer of Bestial Fury|w|U||||m^14889^Emeriss^13.78^k~m^14890^Taerar^13.78^k
fwu|Dragonheart Necklace|w|||||m^14889^Emeriss^13.78^k
fww|Ring of the Unliving|w|U||||m^14889^Emeriss^13.78^k
fx4|Mindtear Band|w|U||||m^14890^Taerar^13.78^k
fxb|Strangely Glyphed Legplates|w|||||m^14887^Ysondre^12.89^k
fxc|Southsea Head Bucket|q|s||||q^8366^Southsea Shakedown^40^^s
fxd|Southsea Mojo Boots|q|s||||q^8366^Southsea Shakedown^40^^s
fxe|Antiquated Nobleman's Tunic|q||h|||q^8273^Oran's Gratitude^42^h^k
fxf|Undercity Reservist's Cap|q||h|||q^8273^Oran's Gratitude^42^h^k
fxi|Sandstrider's Mark|q|||||q^8283^Wanted - Deathclasp, Terror of the Sands^54^^k
fxj|Black Crystal Dagger|q|U||||q^8283^Wanted - Deathclasp, Terror of the Sands^54^^k
fxk|Cold Forged Hammer|q|U||||q^8271^Hero of the Stormpike^55^a^k~q^8272^Hero of the Frostwolf^55^h^k
fxl|Sunprism Pendant|q|U||||q^8321^Vyral the Vile^60^^k
fxm|Desert Wind Gauntlets|q|||||q^8321^Vyral the Vile^60^^k
fyi|Elemental Focus Band|w|U||||m^15203^Prince Skaldrenox^33.98^k
fyl|Wavefront Necklace|w|||||m^15305^Lord Skwol^30.48^k
fys|Multicolored Band|x|||||x^20603^Bag of Spoils^k
fyv|Abyssal War Beads|x|||||x^20601^Sack of Spoils^k
fyz|Cenarion Reservist's Legplates|q|||||q^8316^Armaments of War^58^^k
fz0|Cenarion Reservist's Legplates|q||a|||q^8376^Armaments of War^58^a^k
fz1|Cenarion Reservist's Legguards|q||h|||q^8380^Armaments of War^58^h^k
fz2|Cenarion Reservist's Legguards|q|||||q^8377^Armaments of War^58^^k
fz3|Cenarion Reservist's Leggings|q|||||q^8378^Armaments of War^58^^k
fz4|Cenarion Reservist's Leggings|q|||||q^8382^Armaments of War^58^^k
fz5|Cenarion Reservist's Pants|q|||||q^8381^Armaments of War^58^^k
fz7|Cenarion Reservist's Pants|q|||||q^8379^Armaments of War^58^^k
fza|Crystal Encrusted Greaves|q|||||q^8316^Armaments of War^58^^k
fzb|Crystal Lined Greaves|q||a|||q^8376^Armaments of War^58^a^k
fzc|Wastewalker's Gauntlets|q||h|||q^8380^Armaments of War^58^h^k
fzd|Desertstalkers's Gauntlets|q|||||q^8377^Armaments of War^58^^k
fze|Sandstorm Boots|q|||||q^8382^Armaments of War^58^^k
fzf|Dunestalker's Boots|q|||||q^8378^Armaments of War^58^^k
fzg|Sandworm Skin Gloves|q|||||q^8381^Armaments of War^58^^k
fzh|Desert Bloom Gloves|q|||||q^8379^Armaments of War^58^^k
fzn|Brann's Trusty Pick|q|||||q^8308^Brann Bronzebeard's Lost Letter^58^^k
fzo|Corrupted Blackwood Staff|q|||||q^8306^Into The Maw of Madness^58^^k
gaj|Defiler's Talisman|ev||h|21117|LTalismanofBattle|V^15126^28230^h^k
gak|Defiler's Talisman|ev||h|21118|LTalismanofBattle|V^15126^15230^h^k
gal|Talisman of Arathor|ev|s|a|21115|LTalismanofBattle|V^15127^28230^a^s~r^509^4^The League of Arathor^f
gam|Talisman of Arathor|ev|s|a|21116|LTalismanofBattle|V^15127^15230^a^s~r^509^4^The League of Arathor^f
gan|Talisman of Arathor|ev|s|a|21120|LTalismanofBattle|V^15127^7230^a^s~r^509^4^The League of Arathor^f
gao|Defiler's Talisman|ev||h|21119|LTalismanofBattle|V^15126^7230^h^k
gcs|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8747^The Path of the Protector^60^^k~r^910^3^Brood of Nozdormu^f
gct|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8748^The Path of the Protector^60^^k~r^910^4^Brood of Nozdormu^f
gcu|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8749^The Path of the Protector^60^^k~r^910^5^Brood of Nozdormu^f
gcv|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8750^The Path of the Protector^60^^k~r^910^6^Brood of Nozdormu^f
gcw|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8751^The Protector of Kalimdor^60^^k~r^910^7^Brood of Nozdormu^f
gcx|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8752^The Path of the Conqueror^60^^k~r^910^3^Brood of Nozdormu^f
gcy|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8753^The Path of the Conqueror^60^^k~r^910^4^Brood of Nozdormu^f
gcz|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8754^The Path of the Conqueror^60^^k~r^910^5^Brood of Nozdormu^f
gd0|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8755^The Path of the Conqueror^60^^k~r^910^6^Brood of Nozdormu^f
gd1|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8756^The Qiraji Conqueror^60^^k~r^910^7^Brood of Nozdormu^f
gd2|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8757^The Path of the Invoker^60^^k~r^910^3^Brood of Nozdormu^f
gd3|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8758^The Path of the Invoker^60^^k~r^910^4^Brood of Nozdormu^f
gd4|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8759^The Path of the Invoker^60^^k~r^910^5^Brood of Nozdormu^f
gd5|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8760^The Path of the Invoker^60^^k~r^910^6^Brood of Nozdormu^f
gd6|Signet Ring of the Bronze Dragonflight|eq|U|||LSignetRingoftheB|q^8761^The Grand Invoker^60^^k~r^910^7^Brood of Nozdormu^f
gf2|Stormshroud Gloves|c|||||c^Leatherworking^290^26279^f
gfz|Earth Warder's Vest|q|||||q^8460^Timbermaw Ally^45^^k
gg0|Belt of the Den Watcher|q|||||q^8460^Timbermaw Ally^45^^k
gg4|Leggings of the Ursa|q|||||q^8461^Deadwood of the North^50^^k
gg5|Helm of the Pathfinder|q|||||q^8461^Deadwood of the North^50^^k
gg6|Earth Warder's Gloves|q|||||q^8464^Winterfall Activity^53^^k
gg7|Gloves of the Pathfinder|q|||||q^8464^Winterfall Activity^53^^k
gg8|Vest of the Den Watcher|q|||||q^8464^Winterfall Activity^53^^k
gga|Ursa's Embrace|q|||||q^8464^Winterfall Activity^53^^k
gi8|Sickle of Unyielding Strength|Q|||||q^8558^Sickle of Unyielding Strength^60^^k
gi9|Signet of Unyielding Strength|Q|U||||q^8556^Signet of Unyielding Strength^60^^k
gia|Drape of Unyielding Strength|Q|||||q^8557^Drape of Unyielding Strength^60^^k
gib|Blade of Eternal Justice|Q||a|||q^8711^Blade of Eternal Justice^60^a^k
gic|Ring of Eternal Justice|Q|U|a|||q^8703^Ring of Eternal Justice^60^a^k
gid|Cape of Eternal Justice|Q||a|||q^8695^Cape of Eternal Justice^60^a^k
gie|Hammer of the Gathering Storm|Q||h|||q^8706^Hammer of the Gathering Storm^60^h^k
gif|Ring of the Gathering Storm|Q|U|h|||q^8698^Ring of the Gathering Storm^60^h^k
gig|Cloak of the Gathering Storm|Q||h|||q^8690^Cloak of the Gathering Storm^60^h^k
gih|Scythe of the Unseen Path|Q|||||q^8712^Scythe of the Unseen Path^60^^k
gii|Signet of the Unseen Path|Q|U||||q^8704^Signet of the Unseen Path^60^^k
gij|Cloak of the Unseen Path|Q|||||q^8696^Cloak of the Unseen Path^60^^k
gik|Dagger of Veiled Shadows|Q|||||q^8709^Dagger of Veiled Shadows^60^^k
gil|Band of Veiled Shadows|Q|U||||q^8701^Band of Veiled Shadows^60^^k
gim|Cloak of Veiled Shadows|Q|||||q^8693^Cloak of Veiled Shadows^60^^k
gin|Mace of Unending Life|Q|||||q^8708^Mace of Unending Life^60^^k
gio|Band of Unending Life|Q|U||||q^8700^Band of Unending Life^60^^k
gip|Cloak of Unending Life|Q|||||q^8692^Cloak of Unending Life^60^^k
giq|Gavel of Infinite Wisdom|Q|||||q^8705^Gavel of Infinite Wisdom^60^^k
gir|Ring of Infinite Wisdom|Q|U||||q^8697^Ring of Infinite Wisdom^60^^k
gis|Shroud of Infinite Wisdom|Q|||||q^8689^Shroud of Infinite Wisdom^60^^k
git|Blade of Vaulted Secrets|Q|||||q^8707^Blade of Vaulted Secrets^60^^k
giu|Band of Vaulted Secrets|Q|U||||q^8699^Band of Vaulted Secrets^60^^k
giv|Drape of Vaulted Secrets|Q|||||q^8691^Drape of Vaulted Secrets^60^^k
giw|Kris of Unspoken Names|Q|||||q^8710^Kris of Unspoken Names^60^^k
gix|Ring of Unspoken Names|Q|U||||q^8702^Ring of Unspoken Names^60^^k
giy|Shroud of Unspoken Names|Q|||||q^8694^Shroud of Unspoken Names^60^^k
glc|Charm of the Shifting Sands|Q|||||q^8791^The Fall of Ossirian^60^^k
gld|Choker of the Shifting Sands|Q|||||q^8791^The Fall of Ossirian^60^^k
gle|Pendant of the Shifting Sands|Q|||||q^8791^The Fall of Ossirian^60^^k
glf|Amulet of the Shifting Sands|Q|||||q^8791^The Fall of Ossirian^60^^k
glp|Gnomish Turban of Psychic Might|q|||||q^8620^The Only Prescription^60^^k
gls|Ravencrest's Legacy|q|U||||q^8745^Treasure of the Timeless One^60^^k
glt|Runesword of the Red|q|U||||q^8745^Treasure of the Timeless One^60^^k
glu|Shadowsong's Sorrow|q|U||||q^8745^Treasure of the Timeless One^60^^k
glv|Fang of Korialstrasz|q|U||||q^8745^Treasure of the Timeless One^60^^k
glw|Red Winter Hat|d|||||d^229^War Master Voone^100^0^k~d^230^Emperor Dagran Thaurissan^100^0^k
glx|Green Winter Hat|d|||||d^289^Darkmaster Gandling^100^0^k~d^429^Prince Tortheldrin^100^0^k
gly|Band of Icy Depths|q|U||||q^8729^The Wrath of Neptulon^60^^k
glz|Darkwater Robes|q|||||q^8729^The Wrath of Neptulon^60^^k
gm1|Amulet of Shadow Shielding|Q|||||q^8730^Nefarius's Corruption^60^^k
gm2|Onyx Embedded Leggings|Q|||||q^8730^Nefarius's Corruption^60^^k
gm3|Drake Tooth Necklace|q|||||q^8736^The Nightmare Manifests^60^^k
gm4|Drudge Boots|q|||||q^8736^The Nightmare Manifests^60^^k
gmz|Don Rodrigo's Band|v|sU||||V^13217^755555^^s
gn1|Rune of Perfection|v|s|||LRuneofBattle|V^14753^40000^^s
gn2|Rune of Perfection|v|s|||LRuneofBattle|V^14753^20000^^s
gn3|Rune of Duty|v|s|||LRuneofBattle|V^14753^40000^^s
gn4|Rune of Duty|v|s|||LRuneofBattle|V^14753^20000^^s
gr1|Ring of the Fallen God|Q|U||||q^8802^The Savior of Kalimdor^60^^k
gr2|Cloak of the Fallen God|Q|||||q^8802^The Savior of Kalimdor^60^^k
gr4|Amulet of the Fallen God|Q|||||q^8802^The Savior of Kalimdor^60^^k
guk|Ritssyn's Ring of Chaos|w|U||||m^15249^Qiraji Lasher^0.31^k
gyy|Belt of Heroism|q|||||q^8937^Just Compensation^58^a^k~q^8944^Just Compensation^58^h^k
gyz|Boots of Heroism|q|||||q^8959^Anthion's Parting Words^58^a^k~q^9022^Anthion's Parting Words^58^h^k
gz0|Bracers of Heroism|q|||||q^8912^An Earnest Proposition^58^a^k~q^8920^An Earnest Proposition^58^h^k
gz1|Breastplate of Heroism|q|||||q^9006^Saving the Best for Last^58^a^k~q^9013^Saving the Best for Last^58^h^k
gz2|Gauntlets of Heroism|q|||||q^8937^Just Compensation^58^a^k~q^8944^Just Compensation^58^h^k
gz3|Helm of Heroism|q|||||q^9006^Saving the Best for Last^58^a^k~q^9013^Saving the Best for Last^58^h^k
gz4|Legplates of Heroism|q|||||q^8959^Anthion's Parting Words^58^a^k~q^9022^Anthion's Parting Words^58^h^k
gz5|Spaulders of Heroism|q|||||q^8959^Anthion's Parting Words^58^a^k~q^9022^Anthion's Parting Words^58^h^k
gz6|Darkmantle Belt|q|||||q^8935^Just Compensation^58^a^k~q^8941^Just Compensation^58^h^k
gz7|Darkmantle Boots|q|||||q^8956^Anthion's Parting Words^58^a^k~q^9020^Anthion's Parting Words^58^h^k
gz8|Darkmantle Bracers|q|||||q^8910^An Earnest Proposition^58^a^k~q^8917^An Earnest Proposition^58^h^k
gz9|Darkmantle Cap|q|||||q^9004^Saving the Best for Last^58^a^k~q^9010^Saving the Best for Last^58^h^k
gza|Darkmantle Gloves|q|||||q^8935^Just Compensation^58^a^k~q^8941^Just Compensation^58^h^k
gzb|Darkmantle Pants|q|||||q^8956^Anthion's Parting Words^58^a^k~q^9020^Anthion's Parting Words^58^h^k
gzc|Darkmantle Spaulders|q|||||q^8956^Anthion's Parting Words^58^a^k~q^9020^Anthion's Parting Words^58^h^k
gzd|Darkmantle Tunic|q|||||q^9004^Saving the Best for Last^58^a^k~q^9010^Saving the Best for Last^58^h^k
gze|Beastmaster's Belt|q|||||q^8931^Just Compensation^58^a^k~q^8938^Just Compensation^58^h^k
gzf|Beastmaster's Bindings|q|||||q^8906^An Earnest Proposition^58^a^k~q^8914^An Earnest Proposition^58^h^k
gzh|Beastmaster's Cap|q|||||q^9000^Saving the Best for Last^58^a^k~q^9008^Saving the Best for Last^58^h^k
gzj|Beastmaster's Gloves|q|||||q^8931^Just Compensation^58^a^k~q^8938^Just Compensation^58^h^k
gzk|Beastmaster's Mantle|q|||||q^8952^Anthion's Parting Words^58^a^k~q^9017^Anthion's Parting Words^58^h^k
gzl|Beastmaster's Pants|q|||||q^8952^Anthion's Parting Words^58^a^k~q^9017^Anthion's Parting Words^58^h^k
h0s|Beastmaster's Tunic|q|||||q^9000^Saving the Best for Last^58^a^k~q^9008^Saving the Best for Last^58^h^k
h0t|Beastmaster's Boots|q|||||q^8952^Anthion's Parting Words^58^a^k~q^9017^Anthion's Parting Words^58^h^k
h0u|Sorcerer's Belt|q|||||q^8932^Just Compensation^58^a^k~q^8939^Just Compensation^58^h^k
h0v|Sorcerer's Bindings|q|||||q^8907^An Earnest Proposition^58^a^k~q^8915^An Earnest Proposition^58^h^k
h0w|Sorcerer's Boots|q|||||q^8953^Anthion's Parting Words^58^a^k~q^9018^Anthion's Parting Words^58^h^k
h0x|Sorcerer's Crown|q|||||q^9001^Saving the Best for Last^58^a^k~q^9014^Saving the Best for Last^58^h^k
h0y|Sorcerer's Gloves|q|||||q^8932^Just Compensation^58^a^k~q^8939^Just Compensation^58^h^k
h0z|Sorcerer's Leggings|q|||||q^8953^Anthion's Parting Words^58^a^k~q^9018^Anthion's Parting Words^58^h^k
h10|Sorcerer's Mantle|q|||||q^8953^Anthion's Parting Words^58^a^k~q^9018^Anthion's Parting Words^58^h^k
h11|Sorcerer's Robes|q|||||q^9001^Saving the Best for Last^58^a^k~q^9014^Saving the Best for Last^58^h^k
h12|Deathmist Belt|q|||||q^8936^Just Compensation^58^a^k~q^8943^Just Compensation^58^h^k
h13|Deathmist Bracers|q|||||q^8911^An Earnest Proposition^58^a^k~q^8919^An Earnest Proposition^58^h^k
h14|Deathmist Leggings|q|||||q^8958^Anthion's Parting Words^58^a^k~q^9021^Anthion's Parting Words^58^h^k
h15|Deathmist Mantle|q|||||q^8958^Anthion's Parting Words^58^a^k~q^9021^Anthion's Parting Words^58^h^k
h16|Deathmist Mask|q|||||q^9005^Saving the Best for Last^58^a^k~q^9012^Saving the Best for Last^58^h^k
h17|Deathmist Robe|q|||||q^9005^Saving the Best for Last^58^a^k~q^9012^Saving the Best for Last^58^h^k
h18|Deathmist Sandals|q|||||q^8958^Anthion's Parting Words^58^a^k~q^9021^Anthion's Parting Words^58^h^k
h19|Deathmist Wraps|q|||||q^8936^Just Compensation^58^a^k~q^8943^Just Compensation^58^h^k
h1a|Virtuous Belt|q|||||q^8934^Just Compensation^58^a^k~q^8940^Just Compensation^58^h^k
h1b|Virtuous Bracers|q|||||q^8909^An Earnest Proposition^58^a^k~q^8916^An Earnest Proposition^58^h^k
h1c|Virtuous Crown|q|||||q^9003^Saving the Best for Last^58^a^k~q^9009^Saving the Best for Last^58^h^k
h1d|Virtuous Gloves|q|||||q^8934^Just Compensation^58^a^k~q^8940^Just Compensation^58^h^k
h1e|Virtuous Mantle|q|||||q^8955^Anthion's Parting Words^58^a^k~q^9019^Anthion's Parting Words^58^h^k
h1f|Virtuous Robe|q|||||q^9003^Saving the Best for Last^58^a^k~q^9009^Saving the Best for Last^58^h^k
h1g|Virtuous Sandals|q|||||q^8955^Anthion's Parting Words^58^a^k~q^9019^Anthion's Parting Words^58^h^k
h1h|Virtuous Skirt|q|||||q^8955^Anthion's Parting Words^58^a^k~q^9019^Anthion's Parting Words^58^h^k
h1i|Soulforge Belt|q||a|||q^8933^Just Compensation^58^a^k
h1j|Soulforge Boots|q||a|||q^8954^Anthion's Parting Words^58^a^k
h1k|Soulforge Bracers|q||a|||q^8908^An Earnest Proposition^58^a^k
h1l|Soulforge Breastplate|q||a|||q^9002^Saving the Best for Last^58^a^k
h1m|Soulforge Gauntlets|q||a|||q^8933^Just Compensation^58^a^k
h1n|Soulforge Helm|q||a|||q^9002^Saving the Best for Last^58^a^k
h1o|Soulforge Legplates|q||a|||q^8954^Anthion's Parting Words^58^a^k
h1p|Soulforge Spaulders|q||a|||q^8954^Anthion's Parting Words^58^a^k
h1r|Bindings of The Five Thunders|q||h|||q^8918^An Earnest Proposition^58^h^k
h1s|Boots of The Five Thunders|q||h|||q^8957^Anthion's Parting Words^58^h^k
h1t|Coif of The Five Thunders|q||h|||q^9011^Saving the Best for Last^58^h^k
h1u|Cord of The Five Thunders|q||h|||q^8942^Just Compensation^58^h^k
h1v|Gauntlets of The Five Thunders|q||h|||q^8942^Just Compensation^58^h^k
h1w|Kilt of The Five Thunders|q||h|||q^8957^Anthion's Parting Words^58^h^k
h1x|Pauldrons of The Five Thunders|q||h|||q^8957^Anthion's Parting Words^58^h^k
h1y|Vest of The Five Thunders|q||h|||q^9011^Saving the Best for Last^58^h^k
h22|Feralheart Belt|q|||||q^8926^Just Compensation^58^a^k~q^8927^Just Compensation^58^h^k
h23|Feralheart Boots|q|||||q^8951^Anthion's Parting Words^58^a^k~q^9016^Anthion's Parting Words^58^h^k
h24|Feralheart Bracers|q|||||q^8905^An Earnest Proposition^58^a^k~q^8913^An Earnest Proposition^58^h^k
h25|Feralheart Cowl|q|||||q^8999^Saving the Best for Last^58^a^k~q^9007^Saving the Best for Last^58^h^k
h26|Feralheart Gloves|q|||||q^8926^Just Compensation^58^a^k~q^8927^Just Compensation^58^h^k
h27|Feralheart Kilt|q|||||q^8951^Anthion's Parting Words^58^a^k~q^9016^Anthion's Parting Words^58^h^k
h28|Feralheart Spaulders|q|||||q^8951^Anthion's Parting Words^58^a^k~q^9016^Anthion's Parting Words^58^h^k
h29|Feralheart Vest|q|||||q^8999^Saving the Best for Last^58^a^k~q^9007^Saving the Best for Last^58^h^k
h39|Beads of Ogre Mojo|Q|||||q^8949^Falrin's Vendetta^58^^k
h3a|Beads of Ogre Might|Q|||||q^8949^Falrin's Vendetta^58^^k
h4f|Obsidian Mail Tunic|c|||||c^Blacksmithing^300^27590^f
h4j|Light Obsidian Belt|c|||||c^Blacksmithing^320^27588^f
h4k|Thick Obsidian Breastplate|c|||||c^Blacksmithing^300^27587^f
h4l|Heavy Obsidian Belt|c|||||c^Blacksmithing^320^27585^f
h4m|Jagged Obsidian Shield|c|||||c^Blacksmithing^300^27586^f
h4s|Wristguards of Renown|d|||||d^230^Emperor Dagran Thaurissan^19.8^0^k
h4t|Black Steel Bindings|dw|||||d^230^Warbringer Construct^0.1^0^k~d^230^Doomforge Craftsman^0.02^0^k
h4v|Sash of the Grand Hunt|d|||||d^230^Emperor Dagran Thaurissan^20^0^k
h4w|Lavastone Hammer|d|||||d^230^Magmus^20^0^k
h50|Golem Fitted Pauldrons|d|||||d^230^Phalanx^33.33^0^k
h5b|Foreman's Head Protector|d|||||d^230^Fineous Darkvire^25^0^k
h5d|Dragonskin Cowl|w|||||m^10339^Gyth^20^k
h5j|Kayser's Boots of Precision|d|||||d^229^War Master Voone^20^0^k
h5k|Marksman's Girdle|d|||||d^229^Urok Doomhowl^25^0^k
h5m|Mantle of Lost Hope|d|||||d^230^Lord Roccor^25^0^k
h5s|Greaves of Withering Despair|d|||||d^230^High Interrogator Gerstahn^25^0^k
h5t|Dark Warder's Pauldrons|d|||||d^230^Warder Stilgiss^25^0^k
h5u|Verek's Leash|d|||||d^230^^13^0^k
h5x|Soot Encrusted Footwear|d|||||d^230^^25^0^k
h5z|Faith Healer's Boots|d|||||d^229^Warchief Rend Blackhand^16.67^0^k
h65|Tome of the Lost|d|||||d^229^General Drakkisath^25^0^k
h66|Wand of Eternal Light|dw|||||d^230^Warbringer Construct^0.09^0^k~m^9476^Watchman Doomgrip^0.75^k
h67|Magma Forged Band|dw|||||d^230^Warbringer Construct^0.02^0^k~m^9476^Watchman Doomgrip^0.22^k
h68|Mana Shaping Handwraps|dw|||||d^230^Warbringer Construct^0.18^0^k~m^9476^Watchman Doomgrip^1.91^k
h69|Bloodclot Band|w|||||m^9027^Gorosh the Dervish^35^k
h6i|Flarethorn|w|||||m^9027^Gorosh the Dervish^15^k
h6j|Spellweaver's Turban|d|||||d^229^General Drakkisath^25^0^k
h6l|Shadow Prowler's Cloak|d|||||d^229^General Drakkisath^25^0^k
h6m|Entrenching Boots|w|||||m^9028^Grizzle^15^k
h6n|Leggings of Frenzied Magic|w|||||m^9027^Gorosh the Dervish^35^k
h6o|Forest's Embrace|q|||||q^9053^A Better Ingredient^50^^k
h6q|Grizzled Pelt|q|||||q^9053^A Better Ingredient^50^^k
h6r|Firemoss Boots|d|||||d^230^Hurley Blackbreath^30.33^0^k
h7h|Ironweave Robe|w|||||m^16101^Jarien^35.2^k~m^16102^Sothos^20^k
h7i|Ironweave Cowl|d|||||d^229^Lord Valthalak^44.66^0^k
h7j|Ironweave Pants|d|||||d^289^Kormok^20^0^k
h7k|Ironweave Gloves|w|||||m^16097^Isalien^16.67^k
h7l|Ironweave Mantle|w|||||m^8926^Deep Stinger^0.02^k
h7m|Ironweave Belt|w|||||m^16080^Mor Grayhoof^20^k
h7r|Ironweave Boots|d|||||d^229^The Beast^20^0^k
h7t|Ironweave Bracers|d|||||d^229^Halycon^28.67^0^k
h7u|Huntsman's Harpoon|w|||||m^16097^Isalien^16.67^k
h7x|Lefty's Brass Knuckle|w|||||m^16095^Gnashjaw^1.96^k~m^8933^Cave Creeper^0.03^k
h7y|Malgen's Long Bow|w|||||m^8925^Dredge Worm^0.03^k~m^8927^Dark Screecher^0.02^k
h82|The Jaw Breaker|w|||||m^16080^Mor Grayhoof^20^k
h85|Belt of the Trickster|w|||||m^16080^Mor Grayhoof^20^k
h87|Amulet of the Redeemed|w|||||m^16101^Jarien^20^k~m^16102^Sothos^20^k
h88|Legplates of Vigilance|w|||||m^16101^Jarien^20^k~m^16102^Sothos^20^k
h89|Scepter of Interminable Focus|w|||||m^16101^Jarien^20^k~m^16102^Sothos^20^k
h8a|Shroud of Arcane Mastery|w|||||m^8932^Borer Beetle^0.02^k
h8d|Hammer of Divine Might|d|||||d^289^Kormok^20^0^k
h8e|Band of Mending|w|||||m^16101^Jarien^20^k~m^16102^Sothos^20^k
h8f|Lord Valthalak's Staff of Command|d|||||d^229^Lord Valthalak^34.67^0^k
h8j|Rune Band of Wizardry|d|||||d^229^Lord Valthalak^35.3^0^k
h8k|Pendant of Celerity|d|||||d^229^Lord Valthalak^36.96^0^k
h8m|Leggings of Torment|d|||||d^229^Lord Valthalak^41.12^0^k
h8r|Fahrad's Reloading Repeater|Q|||||q^9023^The Perfect Poison^60^^k
h8s|Doomulus Prime|Q|||||q^9023^The Perfect Poison^60^^k
h9l|The Thunderwood Poker|Q|U||||q^9023^The Perfect Poison^60^^k
h9m|Ravenholdt Slicer|Q|||||q^9023^The Perfect Poison^60^^k
h9n|Shivsprocket's Shiv|Q|||||q^9023^The Perfect Poison^60^^k
h9o|Simone's Cultivating Hammer|Q|||||q^9023^The Perfect Poison^60^^k
h9r|Sageblade|c|||||c^Blacksmithing^300^27832^f
h9s|Persuader|c|||||c^Blacksmithing^300^27830^f
h9t|Titanic Leggings|c|||||c^Blacksmithing^300^27829^f
ha2|Staff of Metanoia|d|||||d^289^Jandice Barov^11.86^0^k
hab|Nacreous Shell Necklace|d|||||d^329^Cannon Master Willey^20^0^k
hac|Willey's Back Scratcher|d|||||d^329^Cannon Master Willey^20^0^k
had|Mantle of the Scarlet Crusade|d|||||d^329^Cannon Master Willey^20^0^k
hae|Redemption|d|||||d^329^Cannon Master Willey^20^0^k
haf|Helm of the New Moon|d|||||d^329^Cannon Master Willey^20^0^k
hag|Ritssyn's Wand of Bad Mojo|d|||||d^329^Baron Rivendare^20^0^k
hah|Tunic of the Crescent Moon|d|||||d^329^Baron Rivendare^20^0^k
hai|Gauntlets of Deftness|d|||||d^329^Baron Rivendare^20^0^k
haj|Helm of the Executioner|d|||||d^329^Baron Rivendare^20^0^k
hak|Thuzadin Mantle|d|||||d^329^Baron Rivendare^20^0^k
hb5|Don Mauricio's Band of Domination|d|||||d^289^Darkmaster Gandling^14.29^0^k
hbu|Moonshadow Stave|q|||||q^9053^A Better Ingredient^50^^k
hfh|Atiesh, Greatstaff of the Guardian|q|||||q^9270^Atiesh, Greatstaff of the Guardian^60^^k
hgm|Atiesh, Greatstaff of the Guardian|q|||||q^9271^Atiesh, Greatstaff of the Guardian^60^^k
hgn|Atiesh, Greatstaff of the Guardian|q|||||q^9257^Atiesh, Greatstaff of the Guardian^60^^k
hgo|Atiesh, Greatstaff of the Guardian|q|||||q^9269^Atiesh, Greatstaff of the Guardian^60^^k
hh7|Outrider's Plate Legguards|v||h|22672||V^14754^165737^h^s
hh8|Glacial Vest|Qc|||||c^Tailoring^315^28207^f~q^9240^Glacial Vest^60^^k
hha|Glacial Gloves|Qc|||||c^Tailoring^315^28205^f~q^9239^Glacial Gloves^60^^k
hhb|Glacial Wrists|Qc|||||c^Tailoring^315^28209^f~q^9238^Glacial Wrists^60^^k
hhe|Glacial Cloak|Qc|||||c^Tailoring^315^28208^f~q^9237^Glacial Cloak^60^^k
hhh|Polar Tunic|Qc|||||c^Leatherworking^320^28219^f~q^9243^Polar Tunic^60^^k
hhi|Polar Gloves|Qc|||||c^Leatherworking^320^28220^f~q^9242^Polar Gloves^60^^k
hhj|Polar Bracers|Qc|||||c^Leatherworking^320^28221^f~q^9241^Polar Bracers^60^^k
hhk|Icy Scale Breastplate|Qc|||||c^Leatherworking^320^28222^f~q^9246^Icy Scale Breastplate^60^^k
hhl|Icy Scale Bracers|Qc|||||c^Leatherworking^320^28224^f~q^9244^Icy Scale Bracers^60^^k
hhm|Icy Scale Gauntlets|Qc|||||c^Leatherworking^320^28223^f~q^9245^Icy Scale Gauntlets^60^^k
hhp|Icebane Breastplate|Qc|||||c^Blacksmithing^300^28242^f~q^9236^Icebane Breastplate^60^^k
hhq|Icebane Gauntlets|Qc|||||c^Blacksmithing^300^28243^f~q^9234^Icebane Gauntlets^60^^k
hhr|Icebane Bracers|Qc|||||c^Blacksmithing^300^28244^f~q^9235^Icebane Bracers^60^^k
hhs|Sentinel's Plate Legguards|v|s|a|22651||V^14753^166347^a^s
hht|Outrider's Chain Leggings|v||h|22748||V^14754^250460^h^s
hhw|Outrider's Mail Leggings|v|s|h|||V^14754^253253^h^s
hij|Icebane Leggings|Q|||||q^9232^The Only Song I Know...^60^^k
hik|Glacial Leggings|Q|||||q^9232^The Only Song I Know...^60^^k
hil|Polar Leggings|Q|||||q^9232^The Only Song I Know...^60^^k
him|Icy Scale Leggings|Q|||||q^9232^The Only Song I Know...^60^^k
hir|Ramaladni's Icy Grasp|Q|U||||q^9230^Ramaladni's Icy Grasp^60^^k
hj9|Band of Cenarius|q|U||||q^9248^A Humble Offering^58^^k
hjo|Outrider's Leather Pants|v||h|22749||V^14754^219678^h^s
hjp|Outrider's Lizardhide Pants|v||h|22750||V^14754^220461^h^s
hjv|Outrider's Silk Leggings|v|U|h|22752||V^14754^167633^h^s
hjw|Sentinel's Chain Leggings|v|s|a|22673||V^14753^242207^a^s
hjx|Sentinel's Leather Pants|v|s|a|22740||V^14753^211086^a^s
hjy|Sentinel's Lizardhide Pants|v|s|a|22741||V^14753^211869^a^s
hk0|Sentinel's Silk Leggings|v|sU|a|22747||V^14753^170748^a^s
hk1|Sentinel's Lamellar Legguards|v|s|a|||V^14753^171358^a^s
hk5|Sylvan Crown|c|||||c^Tailoring^300^28481^f
hk6|Sylvan Shoulders|c|||||c^Tailoring^300^28482^f
hmj|Blood Guard's Chain Greaves|p|U|h|23278||p^7^h^f
hms|Blood Guard's Dragonhide Treads|p|U|h|23281||p^7^h^f
hmv|Blood Guard's Dreadweave Walkers|p|U|h|23283||p^7^h^f
hmw|Blood Guard's Leather Walkers|p|U|h|23285||p^7^h^f
hmx|Blood Guard's Mail Greaves|p|U|h|||p^7^h^f
hmy|Blood Guard's Plate Greaves|p|U|h|23287||p^7^h^f
hmz|Blood Guard's Satin Walkers|p|U|h|23289||p^7^h^f
hn0|Blood Guard's Silk Walkers|p|U|h|23291||p^7^h^f
hn2|Blood Guard's Chain Vices|p|U|h|23279||p^7^h^f
hn3|Blood Guard's Dragonhide Grips|p|U|h|23280||p^7^h^f
hn4|Blood Guard's Leather Grips|p|U|h|23284||p^7^h^f
hn5|Blood Guard's Dreadweave Handwraps|p|U|h|23282||p^7^h^f
hn7|Blood Guard's Mail Vices|p|U|h|||p^7^h^f
hn8|Blood Guard's Plate Gauntlets|p|U|h|23286||p^7^h^f
hn9|Blood Guard's Satin Handwraps|p|U|h|23288||p^7^h^f
hna|Blood Guard's Silk Handwraps|p|U|h|23290||p^7^h^f
hnc|Legionnaire's Plate Hauberk|p|U|h|23300||p^8^h^f
hnd|Legionnaire's Plate Leggings|p|U|h|23301||p^8^h^f
hne|Legionnaire's Chain Hauberk|p|U|h|23292||p^8^h^f
hnf|Legionnaire's Chain Legguards|p|U|h|23293||p^8^h^f
hng|Legionnaire's Mail Hauberk|p|U|h|||p^8^h^f
hnh|Legionnaire's Dragonhide Chestpiece|p|U|h|23294||p^8^h^f
hni|Legionnaire's Dragonhide Leggings|p|U|h|23295||p^8^h^f
hnj|Legionnaire's Leather Chestpiece|p|U|h|23298||p^8^h^f
hnk|Legionnaire's Leather Legguards|p|U|h|23299||p^8^h^f
hnl|Legionnaire's Dreadweave Legguards|p|U|h|23296||p^8^h^f
hnm|Legionnaire's Satin Legguards|p|U|h|23302||p^8^h^f
hnn|Legionnaire's Silk Legguards|p|U|h|23304||p^8^h^f
hno|Legionnaire's Dreadweave Tunic|p|U|h|23297||p^8^h^f
hnp|Legionnaire's Satin Tunic|p|U|h|23303||p^8^h^f
hnq|Legionnaire's Silk Tunic|p|U|h|23305||p^8^h^f
hnr|Legionnaire's Mail Legguards|p|U|h|||p^8^h^f
hrl|Seal of the Damned|w|U||||o^Four Horsemen Chest^16.67^k
hrn|Warmth of Forgiveness|w|U||||o^Four Horsemen Chest^16.67^k
hud|Chains of the Lich|d|||||d^329^^33.33^0^k
hvl|Scorn's Icy Choker|w|||||m^14693^Scorn^33.33^k
hxh|Ring of the Eternal Flame|w|U||||w^60^63^k
hxn|Champion's Plate Shoulders|p|U|h|23315||p^10^h^f
hxo|Champion's Plate Helm|p|U|h|23314||p^10^h^f
hxv|Champion's Chain Helm|p|U|h|23306||p^10^h^f
hxw|Champion's Chain Shoulders|p|U|h|23307||p^10^h^f
hxx|Champion's Dragonhide Headguard|p|U|h|23308||p^10^h^f
hxy|Champion's Dragonhide Shoulders|p|U|h|23309||p^10^h^f
hxz|Champion's Dreadweave Cowl|p|U|h|23310||p^10^h^f
hy0|Champion's Dreadweave Spaulders|p|U|h|23311||p^10^h^f
hy1|Champion's Leather Helm|p|U|h|23312||p^10^h^f
hy2|Champion's Leather Shoulders|p|U|h|23313||p^10^h^f
hy3|Champion's Mail Headguard|p|U|h|||p^10^h^f
hy4|Champion's Mail Pauldrons|p|U|h|||p^10^h^f
hy5|Champion's Satin Hood|p|U|h|23316||p^10^h^f
hy6|Champion's Satin Mantle|p|U|h|23317||p^10^h^f
hy7|Champion's Silk Cowl|p|U|h|23318||p^10^h^f
hy8|Champion's Silk Mantle|p|U|h|23319||p^10^h^f
hyg|Knight-Captain's Lamellar Breastplate|p|U|a|||p^8^a^f
hyh|Knight-Captain's Lamellar Leggings|p|U|a|||p^8^a^f
hyi|Knight-Lieutenant's Lamellar Gauntlets|p|U|a|||p^7^a^f
hyj|Knight-Lieutenant's Lamellar Sabatons|p|U|a|||p^7^a^f
hyk|Lieutenant Commander's Lamellar Headguard|p|U|a|||p^10^a^f
hyl|Lieutenant Commander's Lamellar Shoulders|p|U|a|||p^10^a^f
hym|Knight-Lieutenant's Chain Greaves|p|U|a|22843||p^7^a^f
hyn|Knight-Lieutenant's Chain Vices|p|U|a|22862||p^7^a^f
hyo|Knight-Lieutenant's Dragonhide Grips|p|U|a|22863||p^7^a^f
hyp|Knight-Lieutenant's Dragonhide Treads|p|U|a|22852||p^7^a^f
hyq|Knight-Lieutenant's Dreadweave Handwraps|p|U|a|22865||p^7^a^f
hyr|Knight-Lieutenant's Dreadweave Walkers|p|U|a|22855||p^7^a^f
hys|Knight-Lieutenant's Leather Grips|p|U|a|22864||p^7^a^f
hyt|Knight-Lieutenant's Leather Walkers|p|U|a|22856||p^7^a^f
hyu|Knight-Lieutenant's Plate Gauntlets|p|U|a|22868||p^7^a^f
hyv|Knight-Lieutenant's Plate Greaves|p|U|a|22858||p^7^a^f
hyw|Knight-Lieutenant's Satin Handwraps|p|U|a|22869||p^7^a^f
hyx|Knight-Lieutenant's Satin Walkers|p|U|a|22859||p^7^a^f
hyy|Knight-Lieutenant's Silk Handwraps|p|U|a|22870||p^7^a^f
hyz|Knight-Lieutenant's Silk Walkers|p|U|a|22860||p^7^a^f
hz0|Knight-Captain's Chain Hauberk|p|U|a|22874||p^8^a^f
hz1|Knight-Captain's Chain Legguards|p|U|a|22875||p^8^a^f
hz2|Knight-Captain's Dragonhide Chestpiece|p|U|a|22877||p^8^a^f
hz3|Knight-Captain's Dragonhide Leggings|p|U|a|22878||p^8^a^f
hz4|Knight-Captain's Dreadweave Legguards|p|U|a|22881||p^8^a^f
hz5|Knight-Captain's Dreadweave Tunic|p|U|a|22884||p^8^a^f
hz6|Knight-Captain's Leather Chestpiece|p|U|a|22879||p^8^a^f
hz7|Knight-Captain's Leather Legguards|p|U|a|22880||p^8^a^f
hz8|Knight-Captain's Plate Hauberk|p|U|a|22872||p^8^a^f
hz9|Knight-Captain's Plate Leggings|p|U|a|22873||p^8^a^f
hza|Knight-Captain's Satin Legguards|p|U|a|22882||p^8^a^f
hzb|Knight-Captain's Satin Tunic|p|U|a|22885||p^8^a^f
hzc|Knight-Captain's Silk Legguards|p|U|a|22883||p^8^a^f
hzd|Knight-Captain's Silk Tunic|p|U|a|22886||p^8^a^f
hze|Lieutenant Commander's Chain Helm|p|U|a|23251||p^10^a^f
hzf|Lieutenant Commander's Chain Shoulders|p|U|a|23252||p^10^a^f
hzg|Lieutenant Commander's Dragonhide Headguard|p|U|a|23253||p^10^a^f
hzh|Lieutenant Commander's Dragonhide Shoulders|p|U|a|23254||p^10^a^f
hzi|Lieutenant Commander's Dreadweave Cowl|p|U|a|23255||p^10^a^f
hzj|Lieutenant Commander's Dreadweave Spaulders|p|U|a|23256||p^10^a^f
hzk|Lieutenant Commander's Leather Helm|p|U|a|23257||p^10^a^f
hzl|Lieutenant Commander's Leather Shoulders|p|U|a|23258||p^10^a^f
hzm|Lieutenant Commander's Plate Helm|p|U|a|23244||p^10^a^f
hzn|Lieutenant Commander's Plate Shoulders|p|U|a|23243||p^10^a^f
hzo|Lieutenant Commander's Satin Hood|p|U|a|23261||p^10^a^f
hzp|Lieutenant Commander's Satin Mantle|p|U|a|23262||p^10^a^f
hzq|Lieutenant Commander's Silk Cowl|p|U|a|23263||p^10^a^f
hzr|Lieutenant Commander's Silk Mantle|p|U|a|23264||p^10^a^f
i3f|Grand Marshal's Mageblade|p||a|23466||p^14^a^f
i3g|Grand Marshal's Tome of Power|p||a|23468||p^14^a^f
i3h|Grand Marshal's Tome of Restoration|p||a|23469||p^14^a^f
i3i|Grand Marshal's Warhammer|p||a|23464||p^14^a^f
i3j|Grand Marshal's Demolisher|p||a|23465||p^14^a^f
i3k|Grand Marshal's Swiftblade|p||a|23467||p^14^a^f
i3s|High Warlord's Battle Mace|p||h|23454||p^14^h^f
i3t|High Warlord's Destroyer|p||h|23455||p^14^h^f
i3u|High Warlord's Spellblade|p||h|23451||p^14^h^f
i3v|High Warlord's Quickblade|p||h|23456||p^14^h^f
i3w|High Warlord's Tome of Destruction|p||h|23452||p^14^h^f
i3x|High Warlord's Tome of Mending|p||h|23453||p^14^h^f
iou|The Shadowfoot Stabber|w|||||w^0^0^k
2vhb|Hidden Cloak|u|n||||
4kfl|Shawarmageddon|q|s||||q^79678^Taste Testing^35^^s
4m6m|Ancestral Sword|u|s||||
4qeg|First Sergeant's Inscribed Sabatons|u||h|||
4qem|First Sergeant's Pulsing Greaves|u||h|||
4qf0|Sergeant Major's Leather Boots|u||a|220861||
4qf1|First Sergeant's Leather Boots|u||h|220860||
4qsg|Personal Spellbook|u|U||||
4qxa|Whisper|u|||||
4uz8|Feralheart Sash|u|||||
4uza|Feralheart Galoshes|u|||||
4uzb|Feralheart Wraps|u|||||
4uzd|Feralheart Hands|u|||||
4uzg|Feralheart Cord|u|||||
4uzh|Feralheart Sandals|u|||||
4uzi|Feralheart Bindings|u|||||
4uzj|Feralheart Embrace|u|||||
4uzk|Feralheart Gauntlets|u|||||
4uzl|Feralheart Mantle|u|||||
4uzm|Feralheart Headdress|u|||||
4uzn|Feralheart Pants|u|||||
4uzs|Feralheart Cap|u|||||
4uzt|Feralheart Fists|u|||||
4uzv|Feralheart Tunic|u|||||
4uzw|Feralheart Wristguards|u|||||
4uzx|Feralheart Waistguard|u|||||
4uzy|Feralheart Pauldrons|u|||||
4uzz|Feralheart Legguards|u|||||
4v01|Feralheart Faceguard|u|||||
4v02|Feralheart Grips|u|||||
4v03|Feralheart Treads|u|||||
4v04|Feralheart Armor|u|||||
4v0s|Darkmantle Grips|u|||||
4v0v|Darkmantle Footpads|u|||||
4v1l|Battleboots of Heroism|u|||||
4v1o|Crown of Heroism|u|||||
4v1t|Wristguards of Heroism|u|||||
4v1u|Waistguard of Heroism|u|||||
4v1v|Pauldrons of Heroism|u|||||
4v1w|Legguards of Heroism|u|||||
4v1x|Faceguard of Heroism|u|||||
4v1y|Handguards of Heroism|u|||||
4v1z|Sabatons of Heroism|u|||||
4v20|Chestguard of Heroism|u|||||
4v29|Beastmaster's Treads|u|||||
4v2b|Beastmaster's Gauntlets|u|||||
4v3m|Sorcerer's Gauntlets|u|||||
4v3n|Sorcerer's Sandals|u|||||
4v46|Virtuous Mitts|u|||||
4v49|Virtuous Wraps|u|||||
4v4a|Virtuous Cord|u|||||
4v4b|Virtuous Epaulets|u|||||
4v4c|Virtuous Leggings|u|||||
4v4d|Virtuous Cowl|u|||||
4v4e|Virtuous Hands|u|||||
4v4f|Virtuous Slippers|u|||||
4v4g|Virtuous Gown|u|||||
4v4u|Soulforge Warboots|u|||||
4v4w|Soulforge Greathelm|u|||||
4v4x|Soulforge Bindings|u|||||
4v4y|Soulforge Cord|u|||||
4v4z|Soulforge Epaulets|u|||||
4v50|Soulforge Leggings|u|||||
4v51|Soulforge Crown|u|||||
4v52|Soulforge Fists|u|||||
4v53|Soulforge Treads|u|||||
4v54|Soulforge Embrace|u|||||
4v55|Soulforge Wristguards|u|||||
4v56|Soulforge Waistguard|u|||||
4v57|Soulforge Pauldrons|u|||||
4v58|Soulforge Legguards|u|||||
4v59|Soulforge Faceguard|u|||||
4v5a|Soulforge Handguards|u|||||
4v5b|Soulforge Sabatons|u|||||
4v5c|Soulforge Chestguards|u|||||
4v5r|Slippers of The Five Thunders|u|||||
4v5t|Bracers of The Five Thunders|u|||||
4v5u|Sash of The Five Thunders|u|||||
4v5v|Mantle of The Five Thunders|u|||||
4v5w|Leggings of The Five Thunders|u|||||
4v5x|Crown of The Five Thunders|u|||||
4v5y|Grasp of The Five Thunders|u|||||
4v5z|Greaves of The Five Thunders|u|||||
4v60|Tunic of The Five Thunders|u|||||
4v61|Bands of The Five Thunders|u|||||
4v62|Girdle of The Five Thunders|u|||||
4v64|Legplates of The Five Thunders|u|||||
4v65|Face of The Five Thunders|u|||||
4v66|Fists of The Five Thunders|u|||||
4v67|Treads of The Five Thunders|u|||||
4v68|Chain of The Five Thunders|u|||||
4v7t|Blood Guard's Chain Grips|u||h|227087||
4v7z|Knight-Lieutenant's Chain Grips|u||a|227081||
4v99|Blood Guard's Satin Grips|u||h|227139||
4v9f|Knight-Lieutenant's Satin Grips|u||a|227133||
4v9s|Knight-Lieutenant's Lamellar Gloves|u||a|||
4va4|Blood Guard's Mail Sabatons|u||h|||
4vaa|Blood Guard's Mail Boots|u||h|||
4var|Blood Guard's Dragonhide Gloves|u||h|||
4vb2|Knight-Lieutenant's Dragonhide Gauntlets|u||a|||
4vvj|Hammer of the Fallen Thane|u|||||
4yoh|General's Chain Grips|u||h|||
4yon|General's Chain Vices|u||h|231578||
4yoq|Marshal's Chain Vices|u||a|231575||
4ypb|General's Silk Gauntlets|u||h|231608||
4ypc|General's Silk Handwraps|u||h|231609||
4ypk|Marshal's Silk Gauntlets|u||a|231599||
4ypl|Marshal's Silk Handwraps|u||a|231600||
4ypp|General's Satin Grips|u||h|231617||
4ypt|Marshal's Satin Grips|u||a|231613||
4ypz|Marshal's Satin Handwraps|u||a|231633||
4yq9|General's Satin Handwraps|u||h|231623||
4yqq|Marshal's Lamellar Gauntlets|u||a|||
4yqw|General's Mail Greaves|u||h|||
4yr1|General's Mail Sabatons|u||h|||
4yrg|General's Dragonhide Gauntlets|u||h|||
4yrs|General's Dragonhide Grips|u||h|231694||
4yry|Marshal's Dragonhide Grips|u||a|231688||
4ys4|Marshal's Dragonhide Gloves|u||a|||
50z8|High Warlord's Pig Poker|u||h|234570||
50zb|High Warlord's Battle Mace|u||h|234576||
50zu|Grand Marshal's Polearm|u||a|234548||
5100|Grand Marshal's Warhammer|u||a|234551||
51ox|Grand Marshal's Barricade|u||a|235474||
51oy|High Warlord's Barricade|u||h|235473||
51p0|High Warlord's Hacker|u||h|235481||
51p1|High Warlord's Bonecracker|u||h|235480||
51p2|High Warlord's Shiv|u||h|235479||
51p3|Grand Marshal's Shiv|u||a|235478||
51p4|Grand Marshal's Bonecracker|u||a|235477||
51p5|Grand Marshal's Hacker|u||a|235476||
54ul|Garb of Revelation|u|||||
54us|Boots of Revelation|u|||||
54uu|Hands of Revelation|u|||||
54uv|Crown of Revelation|u|||||
54ux|Pants of Revelation|u|||||
54v1|Mantle of Revelation|u|||||
54v2|Girdle of Revelation|u|||||
54v3|Wrists of Revelation|u|||||
59xw|Skullthumper|q|sn||||q^91285^Murlocs at the Gates^6^^s
59xx|Driftwood Smasher|q|sn||||q^91285^Murlocs at the Gates^6^^s
5a0p|Salvaged Wooden Tower Shield|q|sn||||q^91316^Making Repairs^6^^s
5b71|Novice's Practice Wand|c|sn||||c^Enchanting^1^1245321^f
5bd1|Northshire Hammer|q|sn|a|||q^91777^Rare Books^2^a^s
5bd2|Militia Sword|q|sn|a|||q^91777^Rare Books^2^a^s
5bd3|Militia Shortblade|q|snU|a|||q^91777^Rare Books^2^a^s
5bd4|Apprentice's Spellstaff|q|sn|a|||q^91777^Rare Books^2^a^s
5c8o|Twisted Nether Wand|c|n||||c^Enchanting^185^1248461^f
5cb4|Lesser Eternal Wand|c|n||||c^Enchanting^245^1248505^f
5cb6|Dreambough Wand|c|n||||c^Enchanting^215^1248509^f
5cb9|Greater Eternal Wand|c|n||||c^Enchanting^275^1248515^f
5cfd|Brilliant Wand|c|n||||c^Enchanting^275^1248650^f
5cfk|Glimmering Staff|c|n||||c^Enchanting^140^1248703^f
5cfl|Soulstaff|c|n||||c^Enchanting^140^1248739^f
5cfm|Orb of Mystic Insight|c|n||||c^Enchanting^140^1248745^f
5cfn|Orb of Souls|c|n||||c^Enchanting^140^1248748^f
5ch9|Radiant Staff|c|n||||c^Enchanting^220^1249061^f
5cha|Dreamstaff|c|n||||c^Enchanting^220^1249064^f
5chb|Truesilver Conduit|c|n||||c^Enchanting^220^1249069^f
5chc|Twisting Essence Jar|c|n||||c^Enchanting^220^1249070^f
5chp|Frozen Heart of the Mountain|c|n||||c^Enchanting^265^1249107^f
5d9u|Glowing Copper Boots|c|sn||||c^Blacksmithing^35^1252231^f
5d9y|Sterling Silver Shoulders|c|n||||c^Blacksmithing^110^1252235^f
5da0|Veteran's Chain Shirt|c|n||||c^Blacksmithing^80^1252237^f
5da1|Guard's Chain Shirt|c|n||||c^Blacksmithing^80^1252238^f
5da2|Protector's Chain Shirt|c|n||||c^Blacksmithing^80^1252239^f
5da3|Acolyte's Chain Shirt|c|n||||c^Blacksmithing^80^1252240^f
5da4|Crusader's Chain Shirt|c|n||||c^Blacksmithing^80^1252241^f
5da5|Veteran's Chain Leggings|c|n||||c^Blacksmithing^95^1252242^f
5da6|Guard's Chain Leggings|c|n||||c^Blacksmithing^95^1252243^f
5da7|Protector's Chain Leggings|c|n||||c^Blacksmithing^95^1252244^f
5da8|Acolyte's Chain Leggings|c|n||||c^Blacksmithing^95^1252245^f
5da9|Crusader's Chain Leggings|c|n||||c^Blacksmithing^95^1252246^f
5daa|Veteran's Chain Helm|c|n||||c^Blacksmithing^125^1252247^f
5dab|Guard's Chain Helm|c|n||||c^Blacksmithing^125^1252248^f
5dac|Protector's Chain Helm|c|n||||c^Blacksmithing^125^1252249^f
5dad|Acolyte's Chain Helm|c|n||||c^Blacksmithing^125^1252250^f
5dae|Crusader's Chain Helm|c|n||||c^Blacksmithing^125^1252251^f
5daf|Veteran's Boots|c|n||||c^Blacksmithing^85^1252252^f
5dag|Guard's Boots|c|n||||c^Blacksmithing^85^1252253^f
5dah|Protector's Boots|c|n||||c^Blacksmithing^85^1252254^f
5dai|Acolyte's Boots|c|n||||c^Blacksmithing^85^1252255^f
5daj|Crusader's Boots|c|n||||c^Blacksmithing^85^1252256^f
5dak|Veteran's Gloves|c|n||||c^Blacksmithing^80^1252257^f
5dal|Guard's Gloves|c|n||||c^Blacksmithing^80^1252258^f
5dam|Protector's Gloves|c|n||||c^Blacksmithing^80^1252259^f
5dan|Acolyte's Gloves|c|n||||c^Blacksmithing^80^1252260^f
5dao|Crusader's Gloves|c|n||||c^Blacksmithing^80^1252261^f
5dap|Veteran's Chain Belt|c|n||||c^Blacksmithing^45^1252262^f
5daq|Guard's Chain Belt|c|n||||c^Blacksmithing^45^1252263^f
5dar|Protector's Chain Belt|c|n||||c^Blacksmithing^45^1252264^f
5das|Acolyte's Chain Belt|c|n||||c^Blacksmithing^45^1252265^f
5dat|Crusader's Chain Belt|c|n||||c^Blacksmithing^45^1252266^f
5dau|Veteran's Silvered Chain Shirt|c|n||||c^Blacksmithing^110^1252267^f
5dav|Guard's Silvered Chain Shirt|c|n||||c^Blacksmithing^110^1252268^f
5daw|Protector's Silvered Chain Shirt|c|sn||||c^Blacksmithing^110^1252269^f
5dax|Acolyte's Silvered Chain Shirt|c|n||||c^Blacksmithing^110^1252270^f
5day|Crusader's Silvered Chain Shirt|c|sn||||c^Blacksmithing^110^1252271^f
5daz|Veteran's Silvered Chain Leggings|c|n||||c^Blacksmithing^125^1252272^f
5db0|Guard's Silvered Chain Leggings|c|n||||c^Blacksmithing^125^1252273^f
5db1|Protector's Silvered Chain Leggings|c|sn||||c^Blacksmithing^125^1252274^f
5db2|Acolyte's Silvered Chain Leggings|c|n||||c^Blacksmithing^125^1252275^f
5db3|Crusader's Silvered Chain Leggings|c|n||||c^Blacksmithing^125^1252276^f
5db4|Veteran's Silvered Chain Helm|c|sn||||c^Blacksmithing^95^1252277^f
5db5|Guard's Silvered Chain Helm|c|n||||c^Blacksmithing^95^1252278^f
5db6|Protector's Silvered Chain Helm|c|sn||||c^Blacksmithing^95^1252279^f
5db7|Acolyte's Silvered Chain Helm|c|n||||c^Blacksmithing^95^1252280^f
5db8|Crusader's Silvered Chain Helm|c|n||||c^Blacksmithing^95^1252281^f
5db9|Hard Gold Cuirass|c|n||||c^Blacksmithing^145^1252282^f
5dba|Hard Gold Boots|c|n||||c^Blacksmithing^150^1252283^f
5dbb|Hard Gold Bracers|c|n||||c^Blacksmithing^160^1252284^f
5dbc|Hard Gold Leggings|c|n||||c^Blacksmithing^165^1252285^f
5dbd|Hard Gold Coif|c|n||||c^Blacksmithing^170^1252286^f
5dbf|Hard Gold Pauldrons|c|n||||c^Blacksmithing^175^1252288^f
5dbg|Shining Mithril Breastplate|c|n||||c^Blacksmithing^195^1252289^f
5dbh|Shining Mithril Pauldrons|c|n||||c^Blacksmithing^195^1252290^f
5dbj|Shining Mithril Helm|c|n||||c^Blacksmithing^215^1252292^f
5dbk|Shining Mithril Pants|c|n||||c^Blacksmithing^220^1252293^f
5dbl|Shining Mithril Gauntlet|c|n||||c^Blacksmithing^220^1252294^f
5dbm|Officer's Boots|c|n||||c^Blacksmithing^200^1252295^f
5dbn|Sentinel's Boots|c|n||||c^Blacksmithing^200^1252296^f
5dbo|Warder's Boots|c|n||||c^Blacksmithing^200^1252297^f
5dbp|Prefect's Boots|c|n||||c^Blacksmithing^200^1252298^f
5dbq|Justicar's Boots|c|n||||c^Blacksmithing^200^1252299^f
5dbr|Officer's Gloves|c|n||||c^Blacksmithing^250^1252300^f
5dbs|Sentinel's Gloves|c|n||||c^Blacksmithing^250^1252301^f
5dbt|Warder's Gloves|c|n||||c^Blacksmithing^250^1252302^f
5dbu|Prefect's Gloves|c|n||||c^Blacksmithing^250^1252303^f
5dbv|Justicar's Gloves|c|n||||c^Blacksmithing^250^1252304^f
5dbw|Officer's Belt|c|n||||c^Blacksmithing^150^1252305^f
5dbx|Sentinel's Belt|c|n||||c^Blacksmithing^150^1252306^f
5dby|Warder's Belt|c|sn||||c^Blacksmithing^150^1252307^f
5dbz|Prefect's Belt|c|n||||c^Blacksmithing^150^1252308^f
5dc0|Justicar's Belt|c|sn||||c^Blacksmithing^150^1252309^f
5dc1|Officer's Sabatons|c|n||||c^Blacksmithing^240^1252310^f
5dc2|Sentinel's Sabatons|c|n||||c^Blacksmithing^240^1252311^f
5dc3|Warder's Sabatons|c|n||||c^Blacksmithing^240^1252312^f
5dc4|Prefect's Sabatons|c|n||||c^Blacksmithing^240^1252313^f
5dc5|Justicar's Sabatons|c|n||||c^Blacksmithing^240^1252314^f
5dc6|Officer's Gauntlet|c|n||||c^Blacksmithing^175^1252315^f
5dc7|Sentinel's Gauntlet|c|n||||c^Blacksmithing^175^1252316^f
5dc8|Warder's Gauntlet|c|n||||c^Blacksmithing^175^1252317^f
5dc9|Prefect's Gauntlet|c|n||||c^Blacksmithing^175^1252318^f
5dca|Justicar's Gauntlet|c|n||||c^Blacksmithing^175^1252319^f
5dcb|Officer's Waistguard|c|n||||c^Blacksmithing^250^1252320^f
5dcc|Sentinel's Waistguard|c|n||||c^Blacksmithing^250^1252321^f
5dcd|Warder's Waistguard|c|n||||c^Blacksmithing^250^1252322^f
5dce|Prefect's Waistguard|c|n||||c^Blacksmithing^250^1252323^f
5dcf|Justicar's Waistguard|c|n||||c^Blacksmithing^250^1252324^f
5dcg|Officer's Pauldrons|c|n||||c^Blacksmithing^210^1252325^f
5dch|Sentinel's Pauldrons|c|n||||c^Blacksmithing^210^1252326^f
5dci|Warder's Pauldrons|c|n||||c^Blacksmithing^210^1252327^f
5dcj|Prefect's Pauldrons|c|n||||c^Blacksmithing^210^1252328^f
5dck|Justicar's Pauldrons|c|n||||c^Blacksmithing^210^1252329^f
5dcl|Officer's Wristguards|c|n||||c^Blacksmithing^225^1252330^f
5dcm|Sentinel's Wristguards|c|n||||c^Blacksmithing^225^1252331^f
5dcn|Warder's Wristguards|c|n||||c^Blacksmithing^225^1252332^f
5dco|Prefect's Wristguards|c|n||||c^Blacksmithing^225^1252333^f
5dcp|Justicar's Wristguards|c|n||||c^Blacksmithing^225^1252334^f
5dcq|Blessed Plate Pauldrons|c|n||||c^Blacksmithing^240^1252335^f
5dcs|Blessed Plate Gauntlet|c|n||||c^Blacksmithing^245^1252337^f
5dct|Imperial Plate Gauntlets|c|n||||c^Blacksmithing^255^1252338^f
5dcu|Blessed Plate Bracers|c|n||||c^Blacksmithing^255^1252339^f
5dcv|Blessed Plate Leggings|c|n||||c^Blacksmithing^270^1252340^f
5dcx|Blessed Plate Helm|c|n||||c^Blacksmithing^275^1252342^f
5dcy|Blessed Plate Chest|c|n||||c^Blacksmithing^280^1252343^f
5dcz|Enriched Thorium Breastplate|c|n||||c^Blacksmithing^300^1252344^f
5dd0|Enriched Thorium Leggings|c|n||||c^Blacksmithing^300^1252345^f
5dd1|Enriched Thorium Helm|c|n||||c^Blacksmithing^300^1252346^f
5dd2|Champion's Legplates|c|n|h|||c^Blacksmithing^300^1252347^f
5dd3|Stalwart Helm|c|n||||c^Blacksmithing^300^1252348^f
5dd4|Martyr's Legplates|c|n||||c^Blacksmithing^300^1252349^f
5dd5|Breastplate of Salvation|c|n||||c^Blacksmithing^300^1252350^f
5dd6|Brass Knuckles|c|n||||c^Blacksmithing^80^1252351^f
5dd7|Bronze Dory|c|n||||c^Blacksmithing^95^1252352^f
5dd8|Iron Fists|c|n||||c^Blacksmithing^130^1252353^f
5dd9|Steel Spear|c|n||||c^Blacksmithing^160^1252354^f
5dda|Iron Morningstar|c|n||||c^Blacksmithing^165^1252355^f
5ddb|Mithril Shortsword|c|n||||c^Blacksmithing^180^1252356^f
5ddc|Mithril Warhammer|c|n||||c^Blacksmithing^190^1252357^f
5ddd|Mithril Claws|c|n||||c^Blacksmithing^195^1252358^f
5dde|Mithril Claymore|c|n||||c^Blacksmithing^195^1252359^f
5ddf|Mithril Stiletto|c|n||||c^Blacksmithing^210^1252360^f
5ddg|Charged Mithril Battleaxe|c|n||||c^Blacksmithing^215^1252361^f
5ddh|Thorium Greatmace|c|n||||c^Blacksmithing^250^1252362^f
5ddi|Thorium Cestus|c|n||||c^Blacksmithing^250^1252363^f
5ddj|Thorium Poleaxe|c|n||||c^Blacksmithing^260^1252364^f
5ddk|Bold Dirk|c|n||||c^Blacksmithing^270^1252365^f
5ddl|Stormcarver|c|n||||c^Blacksmithing^300^1252366^f
5ddm|Bagh Nakh|c|n||||c^Blacksmithing^300^1252367^f
5ddn|Legionite Glaive|c|n||||c^Blacksmithing^300^1252368^f
5ddo|Gemmed Copper Boots|c|sn||||c^Blacksmithing^35^1252229^f
5ddp|Strange Copper Boots|c|sn||||c^Blacksmithing^35^1252230^f
5e1p|Edward's Knife|Q|sn||||q^92401^A Frightened Request^17^^s
5e1q|Tabitha's Cuffs|Q|sn||||q^92401^A Frightened Request^17^^s
5e31|Forsaken Greataxe|Q|sn||||q^92422^The Wrath of Rath'mael^17^^s
5e32|Gnarled Necromancer's Staff|Q|sn||||q^92422^The Wrath of Rath'mael^17^^s
5ee4|Sharpened Cirrusfly Stinger|w|sn||||m^251402^Cirrusfly Soldier^0^s
5eew|Yngwe's Axe|u|n||||
5eey|Violet Sash|Q|sn|a|||q^92489^Power Overwhelming^28^a^s
5eez|Gravewalker Boots|Q|sn|h|||q^96986^The Grave Knight^28^h^s
5ef1|Undead Knight's Bracers|Q|sn|h|||q^96986^The Grave Knight^28^h^s
5ers|Black Whelp Slippers|c|n||||c^Leatherworking^35^1255146^f
5ert|Dark Leather Boots|c|sn||||c^Leatherworking^35^1255145^f
5eru|Murloc Scale Shoes|c|sn||||c^Leatherworking^35^1255144^f
5erv|Moonglow Boots|c|sn||||c^Leatherworking^35^1255143^f
5erw|Brawler's Leather Belt|c|n||||c^Leatherworking^60^1255142^f
5erx|Trapper's Leather Belt|c|n||||c^Leatherworking^60^1255141^f
5ery|Defender's Leather Belt|c|n||||c^Leatherworking^60^1255140^f
5erz|Totemic Leather Belt|c|n||||c^Leatherworking^60^1255139^f
5es0|Stormrider's Leather Belt|c|n||||c^Leatherworking^60^1255138^f
5es1|Wisdom's Leather Belt|c|n||||c^Leatherworking^60^1255137^f
5es2|Defender's Leather Armor|c|n||||c^Leatherworking^75^1255134^f
5es3|Totemic Leather Armor|c|n||||c^Leatherworking^75^1255133^f
5es7|Brawler's Leather Boots|c|n||||c^Leatherworking^85^1255121^f
5es8|Trapper's Leather Boots|c|n||||c^Leatherworking^85^1255120^f
5es9|Defender's Leather Boots|c|n||||c^Leatherworking^85^1255119^f
5esa|Totemic Leather Boots|c|n||||c^Leatherworking^85^1255118^f
5esb|Stormrider's Leather Boots|c|n||||c^Leatherworking^85^1255117^f
5esc|Wisdom's Leather Boots|c|n||||c^Leatherworking^85^1255116^f
5esd|Defender's Leather Pants|c|n||||c^Leatherworking^100^1255113^f
5ese|Totemic Leather Pants|c|n||||c^Leatherworking^100^1255112^f
5esf|Defender's Leather Hood|c|sn||||c^Leatherworking^100^1255107^f
5esg|Totemic Leather Hood|c|n||||c^Leatherworking^100^1255106^f
5esh|Hillman's Leather Boots|c|n||||c^Leatherworking^110^1255103^f
5esi|Defender's Leather Tunic|c|n||||c^Leatherworking^110^1255100^f
5esj|Totemic Leather Tunic|c|n||||c^Leatherworking^110^1255099^f
5esn|Defender's Leather Helm|c|n||||c^Leatherworking^125^1255091^f
5eso|Totemic Leather Helm|c|n||||c^Leatherworking^125^1255090^f
5esp|Defender's Leather Kilt|c|n||||c^Leatherworking^125^1255085^f
5esq|Totemic Leather Leggings|c|sn||||c^Leatherworking^125^1255084^f
5esr|Prowler's Leather Belt|c|n||||c^Leatherworking^150^1255081^f
5ess|Warden's Leather Belt|c|n||||c^Leatherworking^150^1255078^f
5est|Skirmisher's Leather Belt|c|n||||c^Leatherworking^150^1255077^f
5esx|Prowler's Leather Shoes|c|n||||c^Leatherworking^200^1255064^f
5esy|Warden's Leather Shoes|c|n||||c^Leatherworking^200^1255062^f
5et0|Prowler's Leather Boots|c|n||||c^Leatherworking^235^1255047^f
5et1|Skulker's Leather Boots|c|n||||c^Leatherworking^235^1255046^f
5et2|Warden's Leather Boots|c|n||||c^Leatherworking^235^1255045^f
5et3|Skycaller's Leather Boots|c|n||||c^Leatherworking^235^1255044^f
5et4|Mender's Leather Boots|c|n||||c^Leatherworking^235^1255043^f
5et5|Prowler's Leather Waistguard|c|n||||c^Leatherworking^250^1255035^f
5et6|Skulker's Leather Waistguard|c|n||||c^Leatherworking^250^1255034^f
5et7|Warden's Leather Waistguard|c|n||||c^Leatherworking^250^1255033^f
5et8|Skycaller's Leather Waistguard|c|n||||c^Leatherworking^250^1255032^f
5et9|Mender's Leather Waistguard|c|n||||c^Leatherworking^250^1255031^f
5eta|Blue Suede Pants|c|n||||c^Leatherworking^255^1255029^f
5etb|Wicked Leather Boots|c|n||||c^Leatherworking^260^1255028^f
5etc|Blue Suede Armor|c|n||||c^Leatherworking^265^1255024^f
5ete|Blue Suede Hat|c|n||||c^Leatherworking^280^1255017^f
5etf|Dawn Armor|c|n||||c^Leatherworking^300^1255015^f
5etg|Timbermaw Tunic|c|n||||c^Leatherworking^300^1255014^f
5eth|Warbear Helm|c|n||||c^Leatherworking^300^1255013^f
5eti|Ironfeather Leggings|c|n||||c^Leatherworking^300^1255012^f
5etm|Brawler's Leather Armor|c|n||||c^Leatherworking^75^1255136^f
5etn|Trapper's Leather Armor|c|n||||c^Leatherworking^75^1255135^f
5eto|Stormrider's Leather Armor|c|n||||c^Leatherworking^75^1255132^f
5etp|Wisdom's Leather Armor|c|sn||||c^Leatherworking^75^1255131^f
5etq|Brawler's Leather Gloves|c|sn||||c^Leatherworking^75^1255130^f
5etr|Trapper's Leather Gloves|c|sn||||c^Leatherworking^75^1255129^f
5ets|Defender's Leather Gloves|c|n||||c^Leatherworking^75^1255128^f
5ett|Totemic Leather Gloves|c|n||||c^Leatherworking^75^1255127^f
5etu|Stormrider's Leather Gloves|c|n||||c^Leatherworking^75^1255126^f
5etv|Wisdom's Leather Gloves|c|n||||c^Leatherworking^75^1255125^f
5etw|Brawler's Leather Pants|c|n||||c^Leatherworking^100^1255115^f
5etx|Trapper's Leather Pants|c|n||||c^Leatherworking^100^1255114^f
5ety|Stormrider's Leather Pants|c|n||||c^Leatherworking^100^1255111^f
5etz|Wisdom's Leather Pants|c|n||||c^Leatherworking^100^1255110^f
5eu0|Brawler's Leather Hood|c|sn||||c^Leatherworking^100^1255109^f
5eu1|Trapper's Leather Hood|c|n||||c^Leatherworking^100^1255108^f
5eu3|Wisdom's Leather Hood|c|sn||||c^Leatherworking^100^1255104^f
5eu4|Brawler's Leather Tunic|c|sn||||c^Leatherworking^110^1255102^f
5eu5|Trapper's Leather Tunic|c|n||||c^Leatherworking^110^1255101^f
5eu6|Stormrider's Leather Tunic|c|n||||c^Leatherworking^110^1255098^f
5eu7|Wisdom's Leather Tunic|c|n||||c^Leatherworking^110^1255097^f
5eu8|Brawler's Leather Helm|c|sn||||c^Leatherworking^125^1255093^f
5eu9|Trapper's Leather Helm|cdw|sn||||d^48^Old Serra'kis^25^0^s~m^4830^Old Serra'kis^0^s
5eub|Wisdom's Leather Helm|cdw|sn||||d^189^Bloodmage Thalnos^18.18^0^s~m^4543^Bloodmage Thalnos^0^s
5euc|Brawler's Leather Legguards|c|n||||c^Leatherworking^125^1255087^f
5eud|Trapper's Leather Legguards|c|n||||c^Leatherworking^125^1255086^f
5euf|Wisdom's Leather Leggings|c|n||||c^Leatherworking^125^1255082^f
5eug|Skulker's Leather Belt|c|sn||||c^Leatherworking^150^1255080^f
5euh|Stalker's Leather Belt|c|sn||||c^Leatherworking^150^1255079^f
5eui|Skycaller's Leather Belt|c|n||||c^Leatherworking^150^1255076^f
5euj|Mender's Leather Belt|c|n||||c^Leatherworking^150^1255075^f
5euk|Prowler's Leather Gloves|c|n||||c^Leatherworking^175^1255071^f
5eul|Skulker's Leather Gloves|c|n||||c^Leatherworking^175^1255070^f
5eum|Stalker's Leather Gloves|c|n||||c^Leatherworking^175^1255069^f
5eun|Warden's Leather Gloves|c|n||||c^Leatherworking^175^1255068^f
5eup|Skycaller's Leather Gloves|c|n||||c^Leatherworking^175^1255066^f
5euq|Mender's Leather Gloves|c|n||||c^Leatherworking^175^1255065^f
5eur|Skulker's Leather Shoes|c|n||||c^Leatherworking^200^1255063^f
5eus|Skycaller's Leather Shoes|c|n||||c^Leatherworking^200^1255061^f
5eut|Mender's Leather Shoes|c|n||||c^Leatherworking^200^1255060^f
5euu|Prowler's Leather Shoulders|c|n||||c^Leatherworking^210^1255059^f
5euv|Skulker's Leather Shoulder|c|n||||c^Leatherworking^210^1255058^f
5euw|Warden's Leather Shoulders|c|n||||c^Leatherworking^210^1255057^f
5eux|Skycaller's Leather Shoulders|c|n||||c^Leatherworking^210^1255056^f
5euy|Mender's Leather Shoulders|c|n||||c^Leatherworking^210^1255055^f
5euz|Prowler's Leather Bracers|c|n||||c^Leatherworking^225^1255054^f
5ev0|Skulker's Leather Bracers|c|n||||c^Leatherworking^225^1255053^f
5ev1|Warden's Leather Bracers|c|n||||c^Leatherworking^225^1255052^f
5ev2|Skycaller's Leather Bracers|c|n||||c^Leatherworking^225^1255051^f
5ev3|Mender's Leather Bracers|c|n||||c^Leatherworking^225^1255050^f
5ev4|Tooled Leather Belt|c|n||||c^Leatherworking^235^1255049^f
5ev7|Prowler's Leather Gauntlets|c|n||||c^Leatherworking^250^1255040^f
5ev8|Skulker's Leather Gauntlets|c|n||||c^Leatherworking^250^1255039^f
5ev9|Warden's Leather Gauntlets|c|n||||c^Leatherworking^250^1255038^f
5eva|Skycaller's Leather Gauntlets|c|n||||c^Leatherworking^250^1255037^f
5evb|Mender's Leather Gauntlets|c|n||||c^Leatherworking^250^1255036^f
5eve|Blue Suede Shoulders|c|n||||c^Leatherworking^260^1255026^f
5evf|Tooled Leather Crown|c|n||||c^Leatherworking^265^1255025^f
5evg|Wicked Leather Shoulders|c|n||||c^Leatherworking^270^1255023^f
5evi|Tooled Leather Epaulets|c|n||||c^Leatherworking^275^1255020^f
5evj|Blue Suede Bracers|c|n||||c^Leatherworking^275^1255019^f
5evk|Tooled Leather Pants|c|n||||c^Leatherworking^280^1255018^f
5evl|Living Crown|c|n||||c^Leatherworking^300^1255016^f
5evm|Stalker's Mail Boots|c|n||||c^Leatherworking^200^1255011^f
5evn|Skycaller's Mail Boots|c|n||||c^Leatherworking^200^1255010^f
5evo|Skirmisher's Mail Boots|c|n||||c^Leatherworking^200^1255009^f
5evp|Mender's Mail Boots|c|n||||c^Leatherworking^200^1255008^f
5evq|Stalker's Mail Shoulders|c|n||||c^Leatherworking^210^1255007^f
5evr|Skycaller's Mail Shoulders|c|n||||c^Leatherworking^210^1255006^f
5evs|Skirmisher's Mail Shoulders|c|n||||c^Leatherworking^210^1255005^f
5evt|Mender's Mail Shoulders|c|n||||c^Leatherworking^210^1255004^f
5evu|Stalker's Mail Bracers|c|n||||c^Leatherworking^225^1255003^f
5evv|Skycaller's Mail Bracers|c|n||||c^Leatherworking^225^1255002^f
5evw|Skirmisher's Mail Bracers|c|n||||c^Leatherworking^225^1255001^f
5evx|Mender's Mail Bracers|c|n||||c^Leatherworking^225^1255000^f
5ew0|Stalker's Mail Sabatons|c|n||||c^Leatherworking^235^1254997^f
5ew1|Skycaller's Mail Sabatons|c|n||||c^Leatherworking^235^1254996^f
5ew2|Skirmisher's Mail Sabatons|c|n||||c^Leatherworking^235^1254995^f
5ew3|Mender's Mail Sabatons|c|n||||c^Leatherworking^235^1254994^f
5ew4|Supple Scorpid Leggings|c|n||||c^Leatherworking^240^1254993^f
5ew5|Charged Scorpid Helm|c|n||||c^Leatherworking^240^1254992^f
5ew8|Stalker's Mail Gauntlets|c|n||||c^Leatherworking^250^1254989^f
5ew9|Skycaller's Mail Gauntlets|c|n||||c^Leatherworking^250^1254988^f
5ewa|Skirmisher's Mail Gauntlets|c|n||||c^Leatherworking^250^1254987^f
5ewb|Mender's Mail Gauntlets|c|n||||c^Leatherworking^250^1254986^f
5ewc|Stalker's Mail Belt|c|n||||c^Leatherworking^250^1254985^f
5ewd|Skycaller's Mail Belt|c|n||||c^Leatherworking^250^1254984^f
5ewe|Skirmisher's Mail Belt|c|n||||c^Leatherworking^250^1254983^f
5ewf|Mender's Mail Belt|c|n||||c^Leatherworking^250^1254982^f
5ewi|Heavy Scorpid Boots|c|n||||c^Leatherworking^255^1254979^f
5ewl|Supple Scorpid Helm|c|n||||c^Leatherworking^260^1254976^f
5ewn|Supple Scorpid Vest|c|n||||c^Leatherworking^270^1254974^f
5ewo|Charged Scorpid Leggings|c|n||||c^Leatherworking^270^1254973^f
5ews|Blue Dragonscale Helm|c|n||||c^Leatherworking^300^1254969^f
5ewt|Black Dragonscale Helm|c|n||||c^Leatherworking^300^1254968^f
5ewu|Pristine Scorpid Leggings|c|n||||c^Leatherworking^300^1254967^f
5fwd|Novice Arcanist's Sash|c|sn||||c^Tailoring^50^1257368^f
5fwf|Novice Ardent's Sash|c|sn||||c^Tailoring^50^1257369^f
5fwh|Pristine Boots|c|n||||c^Tailoring^60^1257370^f
5fwj|Silky Boots|c|n||||c^Tailoring^60^1257371^f
5fwl|Flame Boots|c|n||||c^Tailoring^60^1257372^f
5fwn|Shadow Boots|c|n||||c^Tailoring^60^1257373^f
5fwp|Pearly Boots|c|n||||c^Tailoring^60^1257374^f
5fwr|Shining Boots|c|n||||c^Tailoring^60^1257375^f
5fwt|Filigreed Pristine Gown|c|n||||c^Tailoring^75^1257376^f
5fwv|Filigreed Silky Gown|c|sn||||c^Tailoring^75^1257377^f
5fwx|Filigreed Flame Gown|c|n||||c^Tailoring^75^1257378^f
5fwz|Filigreed Shadow Gown|c|n||||c^Tailoring^75^1257379^f
5fx1|Filigreed Pearly Gown|c|n||||c^Tailoring^75^1257380^f
5fx5|Pristine Gloves|c|sn||||c^Tailoring^75^1257382^f
5fx7|Silky Gloves|c|n||||c^Tailoring^75^1257383^f
5fx9|Flame Gloves|c|n||||c^Tailoring^75^1257384^f
5fxb|Shadow Gloves|c|n||||c^Tailoring^75^1257385^f
5fxd|Pearly Gloves|c|n||||c^Tailoring^75^1257386^f
5fxh|Pristine Sash|c|n||||c^Tailoring^85^1257388^f
5fxj|Silky Sash|c|n||||c^Tailoring^85^1257389^f
5fxl|Flame Sash|c|n||||c^Tailoring^85^1257390^f
5fxn|Shadow Sash|c|n||||c^Tailoring^85^1257391^f
5fxp|Pearly Sash|c|n||||c^Tailoring^85^1257392^f
5fxt|Filigreed Pristine Leggings|c|n||||c^Tailoring^100^1257394^f
5fxv|Filigreed Silky Leggings|c|sn||||c^Tailoring^100^1257395^f
5fxx|Filigreed Flame Leggings|c|n||||c^Tailoring^100^1257396^f
5fxz|Filigreed Shadow Leggings|c|n||||c^Tailoring^100^1257397^f
5fy1|Filigreed Pearly Leggings|c|n||||c^Tailoring^100^1257398^f
5fy5|Pristine Circlet|c|n||||c^Tailoring^100^1257400^f
5fy7|Silky Circlet|c|n||||c^Tailoring^100^1257401^f
5fy9|Flame Circlet|c|n||||c^Tailoring^100^1257402^f
5fyb|Shadow Circlet|c|n||||c^Tailoring^100^1257403^f
5fyd|Pearly Circlet|c|n||||c^Tailoring^100^1257404^f
5fyh|Pristine Gown|c|n||||c^Tailoring^110^1257406^f
5fyj|Silky Gown|c|n||||c^Tailoring^110^1257407^f
5fyl|Flame Gown|c|n||||c^Tailoring^110^1257408^f
5fyn|Shadow Gown|c|n||||c^Tailoring^110^1257409^f
5fyp|Pearly Gown|c|n||||c^Tailoring^110^1257410^f
5fyv|Filigreed Pristine Circlet|c|n||||c^Tailoring^125^1257413^f
5fyx|Filigreed Silky Circlet|c|n||||c^Tailoring^125^1257414^f
5fyz|Filigreed Flame Circlet|c|n||||c^Tailoring^125^1257415^f
5fz1|Filigreed Shadow Circlet|c|n||||c^Tailoring^125^1257416^f
5fz3|Filigreed Pearly Circlet|c|n||||c^Tailoring^125^1257417^f
5fz7|Pristine Leggings|c|n||||c^Tailoring^125^1257419^f
5fz9|Silky Leggings|c|n||||c^Tailoring^125^1257420^f
5fzb|Flame Leggings|c|n||||c^Tailoring^125^1257421^f
5fzd|Shadow Leggings|c|n||||c^Tailoring^125^1257422^f
5fzf|Pearly Leggings|c|n||||c^Tailoring^125^1257423^f
5fzj|Earthen Leggings|c|n||||c^Tailoring^140^1257425^f
5fzl|Gilded Slippers|c|n||||c^Tailoring^140^1257426^f
5fzn|Frothing Slippers|c|n||||c^Tailoring^140^1257427^f
5fzp|Fiery Slippers|c|n||||c^Tailoring^140^1257428^f
5fzr|Black Slippers|c|n||||c^Tailoring^140^1257429^f
5fzt|Golden Slippers|c|n||||c^Tailoring^140^1257430^f
5fzx|Earthen Silk Slippers|c|n||||c^Tailoring^145^1257432^f
5fzz|Earthen Silk Hood|c|n||||c^Tailoring^150^1257433^f
5g01|Earthen Silk Gloves|c|n||||c^Tailoring^160^1257434^f
5g03|Earthen Silk Cuffs|c|n||||c^Tailoring^165^1257435^f
5g05|Gilded Handwraps|c|n||||c^Tailoring^165^1257436^f
5g07|Frothing Handwraps|c|n||||c^Tailoring^165^1257437^f
5g09|Fiery Handwraps|c|n||||c^Tailoring^165^1257438^f
5g0b|Black Handwraps|c|n||||c^Tailoring^165^1257439^f
5g0d|Golden Handwraps|c|n||||c^Tailoring^165^1257440^f
5g0h|Earthen Silk Shoulders|c|n||||c^Tailoring^170^1257442^f
5g0l|Gilded Cord|c|n||||c^Tailoring^190^1257444^f
5g0n|Frothing Cord|c|n||||c^Tailoring^190^1257445^f
5g0p|Fiery Cord|c|n||||c^Tailoring^190^1257446^f
5g0r|Black Cord|c|n||||c^Tailoring^190^1257447^f
5g0t|Golden Cord|c|n||||c^Tailoring^190^1257448^f
5g0x|Nethergeld Shoulders|c|n||||c^Tailoring^195^1257450^f
5g0z|Netherfroth Shoulders|c|n||||c^Tailoring^195^1257451^f
5g11|Netherflame Shoulders|c|n||||c^Tailoring^195^1257452^f
5g13|Netherpearl Shoulders|c|n||||c^Tailoring^195^1257453^f
5g15|Nethershine Shoulders|c|n||||c^Tailoring^195^1257454^f
5g19|Nethergeld Cuffs|c|n||||c^Tailoring^205^1257456^f
5g1b|Netherfroth Cuffs|c|n||||c^Tailoring^205^1257457^f
5g1d|Netherflame Cuffs|c|n||||c^Tailoring^205^1257458^f
5g1f|Netherpearl Cuffs|c|n||||c^Tailoring^205^1257459^f
5g1h|Nethershine Cuffs|c|n||||c^Tailoring^205^1257460^f
5g1l|Ghostweave Cord|c|n||||c^Tailoring^215^1257462^f
5g1n|Earthenweave Gloves|c|n||||c^Tailoring^215^1257463^f
5g1p|Earthenweave Cord|c|n||||c^Tailoring^215^1257464^f
5g1t|Gilded Waistcord|c|n||||c^Tailoring^215^1257466^f
5g1v|Frothing Waistcord|c|n||||c^Tailoring^215^1257467^f
5g1x|Fiery Waistcord|c|n||||c^Tailoring^215^1257468^f
5g1z|Black Waistcord|c|n||||c^Tailoring^215^1257469^f
5g21|Golden Waistcord|c|n||||c^Tailoring^215^1257470^f
5g25|Earthenweave Boots|c|n||||c^Tailoring^225^1257472^f
5g27|Gilded Gloves|c|n||||c^Tailoring^235^1257473^f
5g29|Frothing Gloves|c|n||||c^Tailoring^235^1257474^f
5g2b|Fiery Gloves|c|n||||c^Tailoring^235^1257475^f
5g2d|Black Gloves|c|n||||c^Tailoring^235^1257476^f
5g2f|Golden Gloves|c|n||||c^Tailoring^235^1257477^f
5g2j|Gilded Sandals|c|n||||c^Tailoring^235^1257479^f
5g2l|Frothing Sandals|c|n||||c^Tailoring^235^1257480^f
5g2n|Fiery Sandals|c|n||||c^Tailoring^235^1257481^f
5g2p|Black Sandals|c|n||||c^Tailoring^235^1257482^f
5g2r|Golden Sandals|c|n||||c^Tailoring^235^1257483^f
5g2v|Earthenweave Mantle|c|n||||c^Tailoring^240^1257485^f
5g2x|Earthenweave Vest|c|n||||c^Tailoring^250^1257486^f
5g2z|Runecloth Cuffs|c|n||||c^Tailoring^250^1257487^f
5g31|Earthenweave Leggings|c|n||||c^Tailoring^245^1257488^f
5g33|Ghostweave Mantle|c|n||||c^Tailoring^250^1257489^f
5g35|Ghostweave Boots|c|n||||c^Tailoring^255^1257490^f
5g37|Earthenweave Cuffs|c|n||||c^Tailoring^255^1257491^f
5g3b|Ghostweave Hood|c|n||||c^Tailoring^260^1257493^f
5g3d|Earthenweave Crown|c|n||||c^Tailoring^260^1257494^f
5gl7|A'sharahm, the Roiling Tempest|u|n||||
5ihz|Highlands Defender's Shield|q|sn||||q^93318^WANTED: Vulgara the Insatiable^4^^s
5ii1|Thendal Ranger's Shoes|q|sn||||q^92473^Aggressive Encroachment^3^^s
5ii7|Thendal Ranger's Belt|q|sn||||q^92473^Aggressive Encroachment^3^^s
5ii8|Thendal Ranger's Gloves|q|sn||||q^92473^Aggressive Encroachment^3^^s
5iig|Skychain Belt|q|sn||||q^92469^Return to Rorian^3^^s
5iih|Worn Greatblade|u|n||||
5iii|Flowing Tunic|u|n||||
5iij|Ranger-Apprentice Cape|u|n||||
5iim|Plain Skirt|u|n||||
5iio|Vuldren Hide Bracers|q|sn||||q^92461^Harmony in Balance^1^^s
5iip|Fur-Lined Shoes|q|sn||||q^92461^Harmony in Balance^1^^s
5iiq|Novice's Quarterstaff|q|sn||||q^92470^Foul Matriarch^2^^s
5iir|Scout Ranger's Dagger|q||h|2224||q^92470^Foul Matriarch^2^^s
5ik0|Highlander Gloves|u|n||||
5ik1|Smooth Waistband|u|n||||
5ik2|Homestitched Robe|u|n||||
5ik3|Brass-Banded Bracers|q|sn||||q^92684^Ornery Ornery Galestriders^4^^s
5ik4|Stained Ritual Dagger|q|sn||||q^92528^Among the Faithful^3^^s
5ik5|Curved Scimitar|q|sn||||q^92528^Among the Faithful^3^^s
5ik6|Well-Worn Pants|q|sn||||q^92684^Ornery Ornery Galestriders^4^^s
5ik7|Windblown Kilt|u|n||||
5ik8|Peacekeeper's Buckler|u|n||||
5ik9|Solid Copper Club|u|n||||
5ika|Valanaar Chain Gloves|u|n||||
5ikb|Skysilk Wristguards|u|n||||
5ikc|Farmer's Field Boots|q|sn||||q^92684^Ornery Ornery Galestriders^4^^s
5ikd|Wind-Worn Boots|u|n||||
5ike|Elite Peacekeeper's Leggings|q|sn||||q^92640^Desperate Times^6^^s
5ikf|Balanced Quarterstaff|q|sn||||q^92880^Return to Valanaar^6^^s
5ikg|Skywatcher's Vestments|q|sn||||q^92640^Desperate Times^6^^s
5ikh|Honed Greathammer|q|sn||||q^92880^Return to Valanaar^6^^s
5iki|Quickblade's Dagger|q|sn||||q^92880^Return to Valanaar^6^^s
5iza|Highlander's Chain Vest|u|n||||
5izb|Prideclaw Hide Armor|u|n||||
5j13|Hunter's Simple Cloak|q|sn||||q^93318^WANTED: Vulgara the Insatiable^4^^s
5jr6|Worn Greatsword|q|sn||||q^92470^Foul Matriarch^2^^s
5kj6|Deep-Sea Waders|u|n||||
5kj8|Feardred's Cleansed Amulet|u|n||||
5kqv|Adventurer's Lost Boots|u|n||||
5kqw|Mourner's Shroud|u|n||||
5kqx|Amice of Sorrow|u|n||||
5kqz|Timbermaw Prayer Beads|u|n||||
5kr0|Assassin's Dagger|u|n||||
5kr6|Honor Guard's Plate|u|n||||
5kr7|Barkwoven Belt|u|n||||
5kr8|Scout's Dagger|u|n|h|||
5kr9|Sentinel's Plate|u|n||||
5kra|Elunar Belt|u|n||||
5krb|Sacred Bangle|u|n||||
5krc|Cliff Walker's Cinch|u|n||||
5krd|Hippogryph Hide Boots|u|n||||
5krn|Headdress of the Damned|u|n||||
5kro|Belt of Shadows|u|n||||
5krt|Highborne Memory Crystal|u|n||||
5krz|Staff of Archmage Selwyn|u|n||||
5ks1|Truesong's Hammer|u|n||||
5ks2|A Bigger Shield|u|n||||
5ks3|Panic Hands|u|n||||
5ks4|Bad Hat|u|n||||
5ks5|Great Bear Claw|u|n||||
5ks6|Staff of Wild Beasts|u|n||||
5ks8|Ouroboros Ring|u|n||||
5ks9|Eagle's Head Signet|u|n||||
5ksa|Malefactor's End|u|n||||
5ksb|Engraved Band|u|n||||
5mxp|Thendal Watcher's Vest|u|n||||
5mxq|Scout Ranger's Tunic|u|n|h|||
5mxr|Skyseer's Vest|u|n||||
5mxz|Skyseer's Pants|u|n||||
5my0|Scout Ranger's Leggings|u|n|h|||
5my1|Thendal Watcher's Leggings|u|n||||
5n61|Windshaped Shield|q|sn||||q^93746^A Firm Response^4^^s
5n62|Nightclaw Gloves|q|sn||||q^93165^Mercy Falls on Deaf Ears^8^^s
5n63|Shadowgale Pants|q|sn||||q^93165^Mercy Falls on Deaf Ears^8^^s
5n64|Cult Hunter's Boots|q|sn||||q^93165^Mercy Falls on Deaf Ears^8^^s
5n65|Freedom Walkers|q|sn||||q^93172^Free the Hollows^8^^s
5n66|Sorrowsong Gloves|q|sn||||q^93172^Free the Hollows^8^^s
5n67|Scuffed Cuffs|q|sn||||q^93172^Free the Hollows^8^^s
5n68|Planting Shovel|q|sn||||q^92703^Deliver the News^4^^s
5n69|Trusty Wrench|q|sn||||q^92703^Deliver the News^4^^s
5n6a|Roofing Hammer|q|sn||||q^92703^Deliver the News^4^^s
5n6p|Flutterfly Swatter|q|sn||||q^92683^Flutterfly Dust^4^^s
5n6q|Tracker's Pants|q|sn||||q^92644^Unfortunate News^6^^s
5n6s|Elder's Tunic|q|sn||||q^92644^Unfortunate News^6^^s
5n6t|Peacekeeper's Mail|q|sn||||q^92644^Unfortunate News^6^^s
5n6v|Hunter's Cord|q|sn||||q^92645^Breaking the Breaker^6^^s
5n6w|Windsong Bangles|q|sn||||q^92645^Breaking the Breaker^6^^s
5n6x|Breaker's Gauntlets|q|sn||||q^92645^Breaking the Breaker^6^^s
5n6y|Defender's Bracers|q|sn||||q^93320^Tower Defense^6^^s
5n6z|Windswept Slippers|q|sn||||q^93320^Tower Defense^6^^s
5n70|Peacekeeper's Legguards|q|sn||||q^93320^Tower Defense^6^^s
5n8p|Martyr's Armor|q|sn||||q^92834^Quest 92834^6^^s
5n8q|Sash of Sorrow|q|sn||||q^92834^Quest 92834^6^^s
5n8r|Cilice of Regret|q|sn||||q^92834^Quest 92834^6^^s
5n8s|Bow of Hours|q|sn||||q^92840^Catching Wind^6^^s
5n8t|Belt of Blades|q|sn||||q^93835^Quest 93835^7^^s~q^92646^Confront Lorthuna^7^^s
5n8u|Empyrean Shoes|q|sn||||q^93835^Quest 93835^7^^s~q^92646^Confront Lorthuna^7^^s
5n8v|Empyrean Greatsword|q|sn||||q^93835^Quest 93835^7^^s~q^92646^Confront Lorthuna^7^^s
5n8w|Exterminator's Vest|q|sn||||q^92463^The Cirrusfly Queen^2^^s
5n8x|Gardening Pants|q|sn||||q^92463^The Cirrusfly Queen^2^^s
5n8y|Watcher's Mail Chest|q|sn||||q^92463^The Cirrusfly Queen^2^^s
5n92|Traveler's Wraps|q|sn||||q^92579^To Valanaar^6^^s
5n95|Adventurer's Cloak|q|sn||||q^92579^To Valanaar^6^^s
5n98|Hiking Boots|q|sn||||q^92579^To Valanaar^6^^s
5n99|Bandit's Jerkin|q|sn||||q^92517^The Criminal Element^4^^s
5n9a|Patchwork Leggings|q|sn||||q^92517^The Criminal Element^4^^s
5n9b|Highlands Mail Legguards|q|sn||||q^92517^The Criminal Element^4^^s
5n9c|Wolfhide Belt|q|sn||||q^92550^Havoc in the Highlands^5^^s
5n9d|Elegant Cuffs|q|sn||||q^92550^Havoc in the Highlands^5^^s
5n9e|Ex-Commander's Gauntlets|q|sn||||q^92550^Havoc in the Highlands^5^^s
5n9g|Dowsing Rod|q|sn||||q^94413^A Magical Affront^1^^s
5n9i|Windbough Wand|q|sn||||q^93797^Boughs in the Wind^5^^s
5n9j|Defender's Aegis|u|n||||
5n9k|Skulker's Shiv|u|n||||
5n9m|Winged Beast Staff|u|n||||
5nnj|Elunar Longstaff|u|n||||
5nnk|Windforged Shortblade|u|n||||
5nnl|Skyseeker's Greatstaff|u|n||||
5o39|Ancient Skyborne Blade|u|nU||||
5q36|Semblance of Twilight|u|n||||
5qax|Wolfsbane|q|sn||||q^95140^Old Fire-Eye^21^^s~q^0^Forever Paladin quest chain (Danitha Morr)^15^^c
5r5w|Moonsilver Blade|q|sn|h|||q^95126^The Moonsilver Blade^20^h^s
5ry5|Elven Chain Wristguards|u|n||||
5ry6|Dwarven Plate|u|n||||
5s44|Keen Skinning Knife|q|sn||||q^95508^Unwelcome Guests^13^^s
5s45|Wildgore Greatsword|q|sn||||q^95508^Unwelcome Guests^13^^s
5s4u|Walton's Second-Favorite Gun|q|sn||||q^95508^Unwelcome Guests^13^^s
5sc0|Apprentice Wizard's Gown|q|sn|a|||q^176^WANTED: "Hogger"^6^a^s
5sc1|Rusty Cutlass|u|sn||||
5sc2|Midshipman's Worn Boots|u|sn||||
5sc3|Garrison Cuffs|Q|sn|h|||q^5724^Returning the Lost Satchel^11^h^s
5sc4|Murloc-hide Gloves|q|sn|a|||q^982^Deep Ocean, Vast Sea^13^a^s
5sc5|Monastic Hammer|Q|sn|a|||q^214^Red Silk Bandanas^14^a^s
5sc6|Boots of the People's Militia|q|sn|a|||q^14^The People's Militia^12^a^s
5sc7|Worn Miner's Waistcord|Q|sn|a|||q^168^Collecting Memories^14^a^s
5sc8|Heat Resistant Mitts|Q|sn|h|||q^962^Serpentbloom^14^h^s
5sc9|Safety Boots|Q|sn|h|||q^962^Serpentbloom^14^h^s
5sca|Raptorcrest Bracers|q|sn|h|||q^6481^Earthen Arise^15^h^s
5scb|Embroidered Leggings|q|sn|h|||q^898^Free From the Hold^15^h^s
5scc|Miner's Workgloves|Q|sn|a|||q^167^Oh Brother...^15^a^s
5scd|Miner's Workboots|Q|sn|a|||q^167^Oh Brother...^15^a^s
5sce|Deerhide Pants|q|sn|a|||q^5321^Quest 5321^17^a^s
5scf|Bravo's Armbands|Q|sn|a|||q^2040^Underground Assault^15^a^s
5scg|Dreamer's Leggings|Q|sn|a|||q^2040^Underground Assault^15^a^s
5sci|Hammerbone|Q|sn|h|||q^914^Leaders of the Fang^17^h^s
5scj|Loch Walkers|q|sn|a|||q^256^WANTED: Chok'sul^17^a^s
5sck|Gnollhide Pants|q|sn|h|||q^442^Assault on Fenris Isle^19^h^s
5scl|Staghide Armguards|Q|sn|a|||q^1275^Researching the Corruption^19^a^s
5scm|Archaeologist's Gown|q|sn|a|||q^943^Quest 943^19^a^s
5scn|Tanned Shoulderpads|Q|sn|h|||q^1098^Deathstalkers in Shadowfang^20^h^s
5sco|Bronzed Shoulderguards|Q|sn|h|||q^1098^Deathstalkers in Shadowfang^20^h^s
5scp|Silvered Gauntlets|Q|sn|a|||q^1199^Twilight Falls^20^a^s
5scr|Ursine Hammer|Q|sn|a|||q^386^What Comes Around...^22^a^s
5scs|Harpy Bangles|q|sn|h|||q^6283^Bloodfury Bloodline^21^h^s
5sct|Town Clerk's Mittens|Q|sn|a|||q^377^Crime and Punishment^22^a^s
5scu|Tattered Mittens|Q|sn|h|||q^1013^The Book of Ur^21^h^s
5scv|Dark Ritual Leggings|Q|sn||||q^6561^Blackfathom Villainy^22^h^s~q^1200^Blackfathom Villainy^22^a^s
5scw|Cultist's Armguards|Q|sn||||q^6561^Blackfathom Villainy^22^h^s~q^1200^Blackfathom Villainy^22^a^s
5scx|Demonhide Bracers|q|sn|a|||q^249^Quest 249^22^a^s
5scy|Shadow Gauntlets|q|sn|a|||q^249^Quest 249^22^a^s
5scz|Reclaimer's Robes|u|n||||
5sd0|Magistrate's Pantaloons|Q|sn|a|||q^378^The Fury Runs Deep^22^a^s
5sd1|Smouldering Leggings|q|sn|h|||q^5088^Arikara^24^h^s
5sd2|Runed Gauntlets|q|sn|h|||q^3514^Horde Presence^24^h^s
5sd3|Raptorclaw Shoulders|q|sn|a|||q^296^Ormer's Revenge^24^a^s
5sd6|Technician's Bracers|Q|sn||||q^2904^A Fine Mess^25^^s
5sd7|Dreamer's Chestguard|q|sn|h|||q^6922^Baron Aquanis^25^h^s
5sd8|Darkshire Shoulderguards|q|sn|a|||q^253^Bride of the Embalmer^25^a^s
5sd9|Operator's Gloves|Q|sn|a|||q^2928^Gyrodrillmatic Excavationators^25^a^s
5sda|Ethereal Mantle|q|sn|h|||q^547^Humbert's Sword^26^h^s
5sdb|Sentinel's Boots|Q|sn|a|||q^1142^Mortality Wanes^25^a^s
5sdc|Uthil's Cudgel|q|sn|a|||q^1012^Insane Druids^27^a^s
5sdd|Mavoris's Warstaff|q|sn|a|||q^1012^Insane Druids^27^a^s
5sde|Fury Ring|q|sn|a|||q^304^A Grim Task^29^a^s
5sdf|Ladimore Heirloom Ring|q|sn|a|||q^231^A Daughter's Love^30^a^s
5sdg|Swamp Ring|u|n||||
5sdh|Ring of Ruin|q|sn|a|||q^98^The Legend of Stalvan^30^a^s
5sdi|Cultist's Chestguard|Q|sn|h|||q^6521^An Unholy Alliance^31^h^s
5sdj|Charged Leather Bracers|Q|sn||||q^2418^Power Stones^31^^s
5sdk|Stromgarde Librarian Leggings|q|sn|a|||q^682^Stromgarde Badges^32^a^s
5sdl|Stromgarde Operative Pants|q|sn|a|||q^682^Stromgarde Badges^32^a^s
5sdn|Restorer's Fine Gloves|Q|sn|a|||q^704^Agmond's Fate^33^a^s
5sdo|Excavator Gauntlets|Q|sn|a|||q^704^Agmond's Fate^33^a^s
5sdt|Farseer's Forgotten Shield|u|n||||
5sdu|Tower Boots|u|n||||
5sdv|Wild Headdress|q|sn|a|||q^684^WANTED: Marez Cowl^34^a^s
5sdw|Stromgarde Bracers|q|sn|a|||q^684^WANTED: Marez Cowl^34^a^s
5sdx|Mindslicer|q|sn|h|||q^679^Call to Arms^35^h^s
5sdy|Madman's Blade|q|sn|a|||q^202^Colonel Kurzen^35^a^s
5sdz|Dark Hearted Hammer|q|sn|a|||q^202^Colonel Kurzen^35^a^s
5se0|Alterac Assassin's Gloves|q|sn|a|||q^504^Quest 504^35^a^s
5se1|Stromgarde Cuffs|u|n||||
5se2|Doomcaller's Pants|Q|sn||||q^709^Solution to Doom^35^^s
5se3|Fists of Impending Doom|Q|sn||||q^709^Solution to Doom^35^^s
5se4|Tidal Bracers|u|n||||
5se5|Undertow Legguards|u|n||||
5se6|Guardian Staff|Q|sn|a|||q^2240^Quest 2240^35^a^s
5se7|Witchdoctor's Dress|q|sn|h|||q^680^The Real Threat^35^h^s
5se8|Arathi Armbands|q|sn|a|||q^685^WANTED: Otto and Falconcrest^35^a^s
5se9|Purified Ring|Q|sn||||q^3636^Bring the Light^39^a^s~q^3341^Quest 3341^37^h^s
5sea|Ceremonial Gown|u|n||||
5seb|Blooded Pants|u|n||||
5sec|Master Hunter's Wand|q|sn||||q^208^Quest 208^38^^s
5sed|Master Hunter's Spellsword|q|sn||||q^208^Quest 208^38^^s
5see|Oversized Ogre's Mittens|u|n||||
5sef|Thick Ogre's Belt|u|n||||
5seg|Thane's Hammer|q|sn|a|||q^762^Quest 762^39^a^s
5seh|Ironforge Agent's Gloves|q|sn|a|||q^762^Quest 762^39^a^s
5sei|Beggar's Leggings|u|n||||
5sej|Seadog's Battered Cuffs|u|n||||
5sek|Blackwater Scimitar|q|sn||||q^608^Quest 608^37^^s
5sel|Blackwater Cap|q|sn||||q^608^Quest 608^37^^s
5sem|Black Whelp Boots|u|n||||
5sen|Medal of Valor|u|n||||
5seo|Rebel Breastplate|q|sn|a|||q^206^Quest 206^41^a^s
5sep|Archer's Leggings|q|sn|a|||q^206^Quest 206^41^a^s
5seq|Dank Shoulderpads|Q|sn||||q^2846^Quest 2846^41^^s
5ser|Magister Cowl|Q|sn||||q^2768^Quest 2768^42^^s
5ses|Freebooter's Armband|q|sn||||q^8551^The Captain's Chest^42^^s
5set|Gnomish Floatation Device|q|sn||||q^836^Quest 836^43^^s
5seu|Projectile Redirectors|u|n||||
5sev|Reloading Assist Armbands|u|n||||
5sew|Stonewalker's Slippers|u|n||||
5sex|Protector's Armguards|u|n||||
5sey|Vicious Throwing Stars|u|n||||
5sez|Bloodstained Longbow|u|n||||
5sf0|Bloodied Longmace|u|n||||
5sf1|Smotts' Pinky Ring|u|n||||
5sf2|First Mate's Armguards|u|n||||
5sf3|Forest Troll Leggings|u|n||||
5sf4|Gryphon Rider's Crop|u|n||||
5sf5|Singed Cloth Robe|u|n||||
5sf6|Dragonscale Pants|u|n||||
5sf7|Leggings of Freedom and Sorrow|u|n||||
5sf9|Shapeshifter's Helm|u|n||||
5sfa|Cindercloth Gown|u|n||||
5sfb|Dark Iron Signet|u|n||||
5sfc|Boots of Requite|u|n||||
5sfd|Private Rocknot's Spare Bracers|u|n|a|||
5sfe|Yesterday's Pants|u|n||||
5sff|Ragnar's Favorite Hat|u|n||||
5sfg|Warpwood Bracers|u|n||||
5sfh|Satyrhide Armbands|u|n||||
5sfi|Conqueror's Pendant|u|n||||
5sfj|Incanter's Pantaloons|u|n||||
5si9|Jewel of the Guard Captain|u|n||||
5sib|Ephemeral Choker|d|sn||||d^3065^Faldrim Anvilmar^30^0^s
5sic|Golemheart Stave|d|sn||||d^3065^Plunder^10^0^s
5sid|Treads of the Protector Golem|d|sn||||d^3065^Plunder^10^0^s
5sie|Kindlegem Girdle|d|sn||||d^3065^Infurnus^30^0^s
5sif|Flamefist Grips|d|sn||||d^3065^Infurnus^20^0^s
5sj4|Durgen's Crescent Axe|w|sn||||m^261319^NPC 261319^0^s
5sj8|Direhammer Leggings|d|sn||||d^3065^Durgen Dirgehammer^50^0^s
5sj9|Robes of the Disgraced Thane|d|sn||||d^3065^Durgen Dirgehammer^50^0^s
5sji|Scale of the Tidebender|u|n||||
5sjn|Cleansed Vilebranch Medallion|u|n||||
5sjo|Cleansed Vilebranch Icon|u|n||||
5t6f|Fang of Magmatus|d|sn||||d^3065^Infurnus^50^0^s
5t6g|Aetherwisp Bracers|d|sn||||d^3065^Faldrim Anvilmar^40^0^s
5t6h|Spiritwraith Drape|d|sn||||d^3065^Faldrim Anvilmar^30^0^s
5t6i|Golemguard Chest|d|sn||||d^3065^Plunder^80^0^s
5t9d|Atrophic Girdle|dw|sn||||d^2999^Witherfang^20^0^s~m^250483^Witherfang^0^s
5t9e|Witherbite Bracers|dw|sn||||d^2999^Witherfang^50^0^s~m^250483^Witherfang^0^s
5t9f|Segmented Spider Leg|dw|sn||||d^2999^Witherfang^30^0^s~m^250483^Witherfang^0^s
5t9g|Meathook Slicer|d|sn||||d^2999^The Butcher^40^0^s
5t9h|Abomination Bones|d|sn||||d^2999^The Butcher^10^0^s
5t9i|Leftover Abomination Skin|d|sn||||d^2999^The Butcher^50^0^s
5t9j|Rotmender's Leggings|dw|sn||||d^2999^The Abandoned^30^0^s~m^250631^The Abandoned^0^s
5t9k|Grip of Fear|dw|sn||||d^2999^The Abandoned^30^0^s~m^250631^The Abandoned^0^s
5t9l|Bonerust Leggings|dw|sn||||d^2999^Bjork^20^0^s~m^256097^Bjork^0^s
5t9m|Tuskwrap Belt|dw|sn||||d^2999^Bjork^40^0^s~m^256097^Bjork^0^s
5t9n|Vilewalkers|dw|sn||||d^2999^Viktor the Vile^10^0^s~m^256035^Viktor the Vile^0^s
5t9o|Bloodied Chestwraps|dw|sn||||d^2999^Viktor the Vile^30^0^s~m^256035^Viktor the Vile^0^s
5t9p|Mirror of Rath'mael|dw|sn||||d^2999^Rath'mael^50^0^s~m^250657^Rath'mael^0^s
5t9q|Rotmender's Treads|dw|sn||||d^2999^Rath'mael^20^0^s~m^250657^Rath'mael^0^s
5t9r|Coldspire Staff|dw|sn||||d^2999^Rath'mael^30^0^s~m^250657^Rath'mael^0^s
5t9s|Scepter of the Abandoned|dw|sn||||d^2999^The Abandoned^40^0^s~m^250631^The Abandoned^0^s
5t9t|Corpse Chopper|dw|sn||||d^2999^Bjork^40^0^s~m^256097^Bjork^0^s
5t9u|Vileblood Scimitar|dw|sn||||d^2999^Viktor the Vile^60^0^s~m^256035^Viktor the Vile^0^s
5tm3|Thendal Apprentice's Boots|u|n||||
5tm5|Thendal Novice's Boots|u|n||||
5tm8|Hornbeam Heft|Q|sn|a|||q^95646^Horrors in the Highland^26^a^s
5tm9|Thendal Survivalist's Boots|u|n||||
5tmb|Ironwood Destroyer|Q|sn|a|||q^95646^Horrors in the Highland^26^a^s
5tme|Curl of Life|Q|sn|a|||q^95646^Horrors in the Highland^26^a^s
5tno|Explorer's League Dustcover|Q|sn|a|||q^98824^Prehistoric Prism^26^a^s
5tnq|Linken's Boots of Iron|u|n||||
5tnr|Furs of the Earthen Ring|Q|sn|h|||q^98823^Earthen Echo^26^h^s
5tns|Crocolisk Skin Gaiter|u|nU||||
5tnw|Shen'dorei Magister's Cloak|u|nU||||
5to4|Dirt-Heavy Bracers|Q|sn|h|||q^95682^Open the Maw^26^h^s
5toc|Knife-Polishing Rag|Q|sn|h|||q^95682^Open the Maw^26^h^s
5tp2|Heavehammer|Q|sn||||q^98824^Prehistoric Prism^26^a^s~q^98823^Earthen Echo^26^h^s
5tp3|Healer's Staff|Q|sn||||q^98824^Prehistoric Prism^26^a^s~q^98823^Earthen Echo^26^h^s
5tp4|Songblade Stabilizer|Q|sn|a|||q^95795^Fallen in the Fen^26^a^s
5tp5|Daewyn's Girdle|Q|sn|a|||q^95795^Fallen in the Fen^26^a^s
5tpv|Wanderer's Broadsword|u|n||||
5tpw|Blade of the Magram Clan|u|n||||
5tpx|Staff of Revelations|u|n||||
5tpy|Desperate Barrier|u|n||||
5tpz|Desert Crawler's Claw|u|n||||
5tq0|Scavenged Magram Armament|u|n||||
5tq1|Abandoned Ferocity|u|n||||
5tq2|Bludgeon of Betrayed Virtues|u|n||||
5tq3|Greatstaff of the Necrokhans|u|n||||
5tq4|Soulsplatter Mace|u|n||||
5tq5|Thrice-Damned Effigy|u|n||||
5tq6|Survivor's Amulet|u|n||||
5tq7|Weathered Necklace|u|n||||
5tq8|Scavenger's Ring|u|n||||
5tq9|Desolate Band|u|n||||
5tqa|Corpsefeeder's Shedding|u|n||||
5tqb|Clacking Carapace Spaulders|u|n||||
5tqc|Discarded Circlet|u|n||||
5tsv|Enriched Seal|ev|sn|||LSealofBattle|V^263569^69357^h^s~r^2799^4^Theramore Expeditionary Force^f
5tsw|Volunteer's Lucky Seal|ev|sn|||LSealofBattle|V^263569^23423^h^s~r^2799^4^Theramore Expeditionary Force^f
5tsx|Enriched Seal|ev|sn|||LSealofBattle|V^263569^23507^h^s~r^2799^4^Theramore Expeditionary Force^f
5tsy|Volunteer's Lucky Seal|ev|sn|||LSealofBattle|V^263569^70106^h^s~r^2799^4^Theramore Expeditionary Force^f
5tsz|Expeditionary's Cape|ev|sn||||V^263569^90114^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt0|Theramore Signet|ev|snU||||V^263569^120578^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt1|Theramore Signet|ev|snU||||V^263569^64098^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt2|Theramore Signet|ev|snU||||V^263569^31813^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt3|Theramore Signet|e|nU|a|272067||r^2799^5^Theramore Expeditionary Force^f
5tt5|Militant's Band|ev|snU||||V^263569^111169^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt6|Militant's Band|ev|snU||||V^263569^65332^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt7|Militant's Band|ev|snU||||V^263569^32426^h^s~r^2799^5^Theramore Expeditionary Force^f
5tt8|Militant's Band|e|nU|a|272071||r^2799^5^Theramore Expeditionary Force^f
5tt9|Seal of the Expedition|ev|sn||||V^263569^112862^h^s~r^2799^5^Theramore Expeditionary Force^f
5tta|Seal of the Expedition|ev|sn||||V^263569^66323^h^s~r^2799^5^Theramore Expeditionary Force^f
5ttb|Seal of the Expedition|ev|sn||||V^263569^33800^h^s~r^2799^5^Theramore Expeditionary Force^f
5ttc|Seal of the Expedition|e|n|a|272075||r^2799^5^Theramore Expeditionary Force^f
5ttd|Expeditionary's Cape|ev|sn||||V^263569^51644^h^s~r^2799^5^Theramore Expeditionary Force^f
5tte|Expeditionary's Cape|ev|sn||||V^263569^25625^h^s~r^2799^5^Theramore Expeditionary Force^f
5ttf|Expeditionary's Cape|e|n|a|272078||r^2799^5^Theramore Expeditionary Force^f
5ttg|Rebels' Rugged Reaper|ev|sn||||V^263569^371479^h^s~r^2799^6^Theramore Expeditionary Force^f
5tth|Rebels' Rugged Reaper|ev|sn||||V^263569^218257^h^s~r^2799^6^Theramore Expeditionary Force^f
5tti|Rebels' Rugged Reaper|ev|sn||||V^263569^108301^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttj|Rebels' Rugged Reaper|e|n|a|272082||r^2799^6^Theramore Expeditionary Force^f
5ttk|Clever Expeditionary's Spellblade|ev|sn||||V^263569^301416^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttl|Clever Expeditionary's Spellblade|ev|sn||||V^263569^160210^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttm|Clever Expeditionary's Spellblade|ev|sn||||V^263569^79523^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttn|Clever Expeditionary's Spellblade|e|n|a|272086||r^2799^6^Theramore Expeditionary Force^f
5tto|Insurgent's Manifesto|ev|sn||||V^263569^110731^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttp|Insurgent's Manifesto|ev|sn||||V^263569^65076^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttq|Insurgent's Manifesto|ev|sn||||V^263569^32300^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttr|Insurgent's Manifesto|e|n|a|272090||r^2799^6^Theramore Expeditionary Force^f
5tts|Guerrilla's Jagged Mace|ev|sn||||V^263569^288690^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttt|Guerrilla's Jagged Mace|ev|sn||||V^263569^169633^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttu|Guerrilla's Jagged Mace|ev|sn||||V^263569^84182^h^s~r^2799^6^Theramore Expeditionary Force^f
5ttv|Guerrilla's Jagged Mace|e|n|a|272094||r^2799^6^Theramore Expeditionary Force^f
5ttw|Theramore Gauntlets|ev|sn||||V^263569^151569^h^s~r^2799^7^Theramore Expeditionary Force^f
5ttx|Theramore Gauntlets|ev|sn||||V^263569^90762^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu1|Theramore Handwraps|ev|sn||||V^263569^87667^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu2|Theramore Handwraps|ev|sn||||V^263569^52499^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu4|Theramore Gloves|ev|sn||||V^263569^111634^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu5|Theramore Gloves|ev|sn||||V^263569^60478^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu6|Theramore Handguards|ev|sn||||V^263569^121128^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu7|Theramore Handguards|ev|sn||||V^263569^74566^h^s~r^2799^7^Theramore Expeditionary Force^f
5tu9|Theramore Shoulderpads|ev|sn||||V^263569^125889^h^s~r^2799^7^Theramore Expeditionary Force^f
5tua|Theramore Shoulders|ev|sn||||V^263569^158370^h^s~r^2799^7^Theramore Expeditionary Force^f
5tub|Theramore Pauldrons|ev|sn||||V^263569^158959^h^s~r^2799^7^Theramore Expeditionary Force^f
5tuc|Theramore Epaulets|ev|sn||||V^263569^191778^h^s~r^2799^7^Theramore Expeditionary Force^f
5tud|Theramore Mantle|ev|sn||||V^263569^223147^h^s~r^2799^7^Theramore Expeditionary Force^f
5tuf|Theramore Spaulders|ev|sn||||V^263569^224766^h^s~r^2799^7^Theramore Expeditionary Force^f
5tx7|Darkspear Voodoo Seal|ev|sn|h||LSealofBattle|V^263570^23584^h^s~r^2798^4^Darkspear Raiders^f
5tx8|Relentless Raider's Seal|ev|sn|h||LSealofBattle|V^263570^70335^h^s~r^2798^4^Darkspear Raiders^f
5tx9|Darkspear Voodoo Seal|ev|sn|h||LSealofBattle|V^263570^70578^h^s~r^2798^4^Darkspear Raiders^f
5txa|Relentless Raider's Seal|ev|sn|h||LSealofBattle|V^263570^21562^h^s~r^2798^4^Darkspear Raiders^f
5txb|Darkspear Raider's Cloak|ev|sn|h|||V^263570^84689^h^s~r^2798^5^Darkspear Raiders^f
5txc|Insurgent's Band|ev|snU|h|||V^263570^113345^h^s~r^2798^5^Darkspear Raiders^f
5txd|Insurgent's Band|ev|snU|h|||V^263570^66606^h^s~r^2798^5^Darkspear Raiders^f
5txe|Insurgent's Band|ev|snU|h|||V^263570^33057^h^s~r^2798^5^Darkspear Raiders^f
5txf|Insurgent's Band|e|U|h|271911||r^2798^5^Darkspear Raiders^f
5txg|Darkspear Signet|ev|snU|h|||V^263570^115038^h^s~r^2798^5^Darkspear Raiders^f
5txh|Darkspear Signet|ev|snU|h|||V^263570^67598^h^s~r^2798^5^Darkspear Raiders^f
5txi|Darkspear Signet|ev|snU|h|||V^263570^33547^h^s~r^2798^5^Darkspear Raiders^f
5txj|Darkspear Signet|e|U|h|271916||r^2798^5^Darkspear Raiders^f
5txk|Darkspear Warding Pendant|ev|sn|h|||V^263570^116720^h^s~r^2798^5^Darkspear Raiders^f
5txl|Darkspear Warding Pendant|ev|sn|h|||V^263570^68589^h^s~r^2798^5^Darkspear Raiders^f
5txm|Darkspear Warding Pendant|ev|sn|h|||V^263570^34037^h^s~r^2798^5^Darkspear Raiders^f
5txn|Darkspear Warding Pendant|e||h|271920||r^2798^5^Darkspear Raiders^f
5txo|Darkspear Raider's Cloak|ev|sn|h|||V^263570^51998^h^s~r^2798^5^Darkspear Raiders^f
5txp|Darkspear Raider's Cloak|ev|sn|h|||V^263570^25803^h^s~r^2798^5^Darkspear Raiders^f
5txq|Darkspear Raider's Cloak|e||h|271923||r^2798^5^Darkspear Raiders^f
5txr|Darkspear Raider's Reaper|ev|sn|h|||V^263570^347547^h^s~r^2798^6^Darkspear Raiders^f
5txs|Darkspear Raider's Reaper|ev|sn|h|||V^263570^204245^h^s~r^2798^6^Darkspear Raiders^f
5txt|Darkspear Raider's Reaper|ev|sn|h|||V^263570^101373^h^s~r^2798^6^Darkspear Raiders^f
5txu|Darkspear Raider's Reaper|e||h|271927||r^2798^6^Darkspear Raiders^f
5txv|Darkspear Insurgent's Spellblade|ev|sn|h|||V^263570^282269^h^s~r^2798^6^Darkspear Raiders^f
5txw|Darkspear Insurgent's Spellblade|ev|sn|h|||V^263570^165874^h^s~r^2798^6^Darkspear Raiders^f
5txx|Darkspear Insurgent's Spellblade|ev|sn|h|||V^263570^82323^h^s~r^2798^6^Darkspear Raiders^f
5txy|Darkspear Insurgent's Spellblade|e||h|271931||r^2798^6^Darkspear Raiders^f
5txz|Tome of the Darkspear Prophecy|ev|sn|h|||V^263570^114589^h^s~r^2798^6^Darkspear Raiders^f
5ty0|Tome of the Darkspear Prophecy|ev|sn|h|||V^263570^67341^h^s~r^2798^6^Darkspear Raiders^f
5ty1|Tome of the Darkspear Prophecy|ev|sn|h|||V^263570^33420^h^s~r^2798^6^Darkspear Raiders^f
5ty2|Tome of the Darkspear Prophecy|e||h|271935||r^2798^6^Darkspear Raiders^f
5ty3|Darkspear Skirmisher's Bludgeon|ev|sn|h|||V^263570^290705^h^s~r^2798^6^Darkspear Raiders^f
5ty4|Darkspear Skirmisher's Bludgeon|ev|sn|h|||V^263570^170830^h^s~r^2798^6^Darkspear Raiders^f
5ty5|Darkspear Skirmisher's Bludgeon|ev|sn|h|||V^263570^84774^h^s~r^2798^6^Darkspear Raiders^f
5ty6|Darkspear Skirmisher's Bludgeon|e||h|271939||r^2798^6^Darkspear Raiders^f
5ty7|Raider Gauntlets|ev|sn|h|||V^263570^141647^h^s~r^2798^7^Darkspear Raiders^f
5ty8|Raider Gauntlets|ev|sn|h|||V^263570^84851^h^s~r^2798^7^Darkspear Raiders^f
5ty9|Raider Handwraps|ev|sn|h|||V^263570^81107^h^s~r^2798^7^Darkspear Raiders^f
5tya|Raider Handwraps|ev|sn|h|||V^263570^48584^h^s~r^2798^7^Darkspear Raiders^f
5tyb|Raider Gloves|ev|sn|h|||V^263570^102974^h^s~r^2798^7^Darkspear Raiders^f
5tyc|Raider Gloves|ev|sn|h|||V^263570^61681^h^s~r^2798^7^Darkspear Raiders^f
5tyd|Raider Handguards|ev|sn|h|||V^263570^123528^h^s~r^2798^7^Darkspear Raiders^f
5tye|Raider Handguards|ev|sn|h|||V^263570^73983^h^s~r^2798^7^Darkspear Raiders^f
5tyf|Darkspear Shoulderpads|ev|sn|h|||V^263570^124455^h^s~r^2798^7^Darkspear Raiders^f
5tyg|Darkspear Shoulders|ev|sn|h|||V^263570^156572^h^s~r^2798^7^Darkspear Raiders^f
5tyh|Darkspear Pauldrons|ev|sn|h|||V^263570^157161^h^s~r^2798^7^Darkspear Raiders^f
5tyi|Darkspear Epaulets|ev|sn|h|||V^263570^189616^h^s~r^2798^7^Darkspear Raiders^f
5tyj|Darkspear Mantle|ev|sn|h|||V^263570^220641^h^s~r^2798^7^Darkspear Raiders^f
5tyk|Darkspear Spaulders|ev|sn|h|||V^263570^221462^h^s~r^2798^7^Darkspear Raiders^f
5u0j|Greatsword of Great Pasts|u|n||||
5u0k|Spectral Magister's Commission|u|n||||
5u0l|Phantasmal Shiv|u|n||||
5u0o|Amulet of Vengeance|u|n||||
5u0p|Amulet of Forgiveness|u|n||||
5u0q|Overgrown Cuffs|u|n||||
5u0r|Thornplated Cord|u|n||||
5u6h|Magician's Cord|u|n||||
5u6i|Penitent's Cinch|u|n||||
5u6j|Assassin's Waistguard|u|n||||
5u6k|Shifter's Belt|v|sn|h|||V^227853^0^h^s
5u6l|Ranger's Belt|u|n||||
5u6m|Caretaker's Cord|v|sn|h|||V^227853^0^h^s
5u6n|Stormseeker's Girdle|u|n||||
5u6p|Elunite Cord|v|sn|h|||V^227853^0^h^s
5u6r|Valiant's Waistguard|u|n||||
5u6s|Vindicator's Belt|u|n||||
5u6t|Redeemer's Waistcord|u|n||||
5u6u|Channeler's Ring|v|snU|h|||V^227853^0^h^s
5u6v|Blessed Band of Light|v|snU|h|||V^227853^0^h^s
5u6w|Cutthroat's Signet|v|snU|h|||V^227853^0^h^s
5u6x|Ring of Awareness|v|snU|h|||V^227853^0^h^s
5u6y|Windseeker's Belt|u|n||||
5u6z|Arcanoweave Cloak|v|sn|h|||V^227853^0^h^s
5u71|Drape of Recovery|v|sn|h|||V^227853^0^h^s
5u72|Howler's Furs|v|sn|h|||V^227853^0^h^s
5u73|Stalwart Cloak|v|sn|h|||V^227853^0^h^s
5u7p|Adaptive Combat Assistant|v|sn|h||LUndermineTrinket|V^227853^0^h^s
5u7q|Weakness Analyzer|v|sn|h||LUndermineTrinket|V^227853^0^h^s
5u7r|Serenity Field|v|sn|h||LUndermineTrinket|V^227853^0^h^s
5u7s|Defender's Grip Stabilizer|v|sn|h||LUndermineTrinket|V^227853^0^h^s
5u83|Sergeant's Cloak|u|nU||||
5u84|Premier High Warlord's Blade|v||h|272693||V^14581^0^^s
5u85|Premier Magus Footwraps|u|n||||
5u86|Premier Magus Cuffs|u|n||||
5u87|Premier Magus Gloves|u|n||||
5u88|Premier Magus Belt|u|n||||
5u89|Premier Magus Hood|u|n||||
5u8a|Premier Magus Pants|u|n||||
5u8b|Premier Magus Robes|u|n||||
5u8d|Premier Kodohide Armguards|u|n||||
5u8e|Premier Dragonhide Boots|u|n||||
5u8f|Premier Dragonhide Waistband|u|n||||
5u8g|Premier Kodohide Gauntlets|u|n||||
5u8h|Premier Shadowhide Armguards|v|sn||||V^12792^0^^s
5u8j|Premier Shadowhide Vices|v|sn||||V^12792^0^^s
5u8k|Premier Shadowhide Girdle|v|sn||||V^12792^0^^s
5u8l|Premier Dragonhide Spaulders|u|n||||
5u8m|Premier Dragonhide Trousers|u|n||||
5u8n|Premier Dragonhide Helm|u|n||||
5u8o|Premier Dragonhide Breastplate|u|n||||
5u8p|Premier Shadowhide Hauberk|v|sn||||V^12792^0^^s
5u8q|Premier Shadowhide Headguard|v|sn||||V^12792^0^^s
5u8r|Premier Shadowhide Mantle|v|sn||||V^12792^0^^s
5u8s|Premier Shadowhide Leggings|v|sn||||V^12792^0^^s
5u8t|Premier Mortarplate Boots|u|n||||
5u8u|Premier Mortarplate Gloves|u|n||||
5u8v|Premier Mortarplate Armor|u|n||||
5u8w|Premier Mortarplate Headguard|u|n||||
5u8x|Premier Mortarplate Legguards|u|n||||
5u8z|Premier Chain Bracers|u|n||||
5u90|Premier Mail Walkers|u|n||||
5u91|Premier Linked Grips|u|n||||
5u92|Premier Mail Helm|u|n||||
5u93|Premier Mail Chestpiece|u|n||||
5u94|Premier Linked Leggings|u|n||||
5u95|Premier Linked Shoulders|u|n||||
5u96|Premier Chain Breastplate|u|n||||
5u97|Premier Chain Headguard|u|n||||
5u98|Premier Chain Leggings|u|n||||
5u9a|Premier Chain Girdle|u|n||||
5u9b|Premier Chain Gauntlets|u|n||||
5u9c|Premier Chain Boots|u|n||||
5u9d|Premier Linked Wristguards|u|n||||
5u9e|Premier Warlord's Magus Cowl|u||h|272750||
5u9f|Premier General's Magus Trousers|u||h|272751||
5u9g|Premier Warlord's Magus Raiment|u||h|272752||
5u9h|Premier General's Magus Amice|u||h|272753||
5u9i|Premier Legionnaire's Magus Sash|u||h|272748||
5u9j|Premier Legionnaire's Magus Cuffs|u||h|272747||
5u9k|Premier Centurion's Magus Boots|u||h|272746||
5u9l|Premier Champion's Magus Handguards|u||h|272749||
5u9m|Premier Warlord's Mortarplate Armor|u||h|272786||
5u9n|Premier Warlord's Mortarplate Headpiece|u||h|272787||
5u9o|Premier General's Mortarplate Leggings|u||h|272788||
5u9p|Premier General's Mortarplate Shoulders|u||h|272789||
5u9q|Premier Centurion's Mortarplate Boots|u||h|272792||
5u9r|Premier Legionnaire's Mortarplate Armguards|u||h|272790||
5u9s|Premier Legionnaire's Mortarplate Girdle|u||h|272791||
5u9t|Premier Champion's Mortarplate Gauntlets|u||h|272793||
5u9u|Premier Warlord's Dragonhide Hauberk|u||h|272761||
5u9v|Premier Warlord's Dragonhide Helmet|u||h|272760||
5u9w|Premier General's Dragonhide Epaulets|u||h|272758||
5u9x|Premier General's Dragonhide Leggings|u||h|272759||
5u9y|Premier Legionnaire's Dragonhide Bracers|u||h|272754||
5u9z|Premier Centurion's Dragonhide Boots|u||h|272768||
5ua0|Premier Champion's Dragonhide Gloves|u||h|272757||
5ua1|Premier Legionnaire's Dragonhide Belt|u||h|272756||
5ua2|Premier Legionnaire's Shadowhide Girdle|u||h|272767||
5ua3|Premier Centurion's Shadowhide Treads|u||h|272755||
5ua4|Premier Legionnaire's Shadowhide Armsplints|u||h|272769||
5ua5|Premier Champion's Shadowhide Mitts|u||h|272763||
5ua6|Premier Warlord's Shadowhide Helm|u||h|272764||
5ua7|Premier General's Shadowhide Spaulders|u||h|272766||
5ua8|Premier Warlord's Shadowhide Breastplate|u||h|272762||
5ua9|Premier General's Shadowhide Legguards|u||h|272765||
5uaa|Premier Warlord's Chain Chestpiece|u||h|272775||
5uab|Premier Warlord's Chain Helmet|u||h|272774||
5uac|Premier General's Chain Legguards|u||h|272776||
5uad|Premier General's Chain Shoulders|u||h|272777||
5uae|Premier Centurion's Chain Sabatons|u||h|272771||
5uaf|Premier Legionnaire's Chain Wristguards|u||h|272770||
5uag|Premier Champion's Chain Gloves|u||h|272772||
5uah|Premier Legionnaire's Chain Girdle|u||h|272773||
5uai|Premier Centurion's Linked Boots|u||h|274183||
5uaj|Premier Champion's Linked Gauntlets|u||h|274184||
5uak|Premier Legionnaire's Linked Waistband|u||h|274185||
5ual|Premier Legionnaire's Linked Bracers|u||h|274186||
5uam|Premier Warlord's Linked Armor|u||h|274187||
5uan|Premier Warlord's Linked Helm|u||h|274188||
5uao|Premier General's Linked Leggings|u||h|274189||
5uap|Premier General's Linked Spaulders|u||h|274190||
5uas|Premier Felweave Robe|u|n||||
5uat|Premier Felweave Shoulders|u|n||||
5uau|Premier Felweave Belt|u|n||||
5uav|Premier Felweave Bracers|u|n||||
5uaw|Premier Felweave Boots|u|n||||
5uax|Premier Felweave Gloves|u|n||||
5uay|Premier Centurion's Felweave Boots|u||h|272807||
5uaz|Premier Legionnaire's Felweave Bracers|u||h|272806||
5ub0|Premier Champion's Felweave Gloves|u||h|272808||
5ub1|Premier Legionnaire's Felweave Belt|u||h|272809||
5ub2|Premier General's Felweave Mantle|u||h|272804||
5ub3|Premier Warlord's Felweave Hood|u||h|272802||
5ub4|Premier Warlord's Felweave Robe|u||h|272805||
5ub5|Premier General's Felweave Pants|u||h|272803||
5ub6|Premier Satin Cowl|u|n||||
5ub7|Premier Satin Trousers|u|n||||
5ub8|Premier Satin Vestments|u|n||||
5ub9|Premier Satin Shoulderpads|u|n||||
5uba|Premier Satin Sash|u|n||||
5ubb|Premier Satin Cuffs|u|n||||
5ubc|Premier Satin Boots|u|n||||
5ubd|Premier Satin Gloves|u|n||||
5ube|Premier Centurion's Satin Boots|u||h|272823||
5ubf|Premier Legionnaire's Satin Bracers|u||h|272822||
5ubg|Premier Champion's Satin Gloves|u||h|272824||
5ubh|Premier Legionnaire's Satin Cinch|u||h|272825||
5ubi|Premier General's Satin Mantle|u||h|272820||
5ubj|Premier Warlord's Satin Cowl|u||h|272818||
5ubk|Premier Warlord's Satin Robes|u||h|272821||
5ubl|Premier General's Satin Leggings|u||h|272819||
5ubm|Premier Sergeant's Cloak|v|sn||||V^12793^0^^s
5ubn|Premier Mortarplate Bracers|u|n||||
5ubo|First Sergeant's Plate Bracers|u|nU|h|||
5ubp|First Sergeant's Mail Wristguards|u|nU|h|||
5ubq|Premier Dragonhide Armguards|u|n||||
5ubx|Premier Sergeant's Cape|v|sn||||V^12793^0^^s
5ubz|Premier High Warlord's Shield Wall|v||h|272838||V^14581^0^^s
5uc0|Premier High Warlord's Cleaver|v||h|272839||V^14581^0^^s
5uc1|Premier High Warlord's Battle Axe|v||h|272840||V^14581^0^^s
5uc2|Premier High Warlord's Recurve|v||h|272841||V^14581^0^^s
5uc3|Premier High Warlord's Crossbow|v||h|272842||V^14581^0^^s
5uc4|Premier High Warlord's Razor|v||h|272843||V^14581^0^^s
5uc5|Premier High Warlord's Right Claw|v||h|272844||V^14581^0^^s
5uc6|Premier High Warlord's Left Claw|v||h|272845||V^14581^0^^s
5uc7|Premier High Warlord's Street Sweeper|v||h|272846||V^14581^0^^s
5uc8|Premier High Warlord's Bludgeon|v||h|272847||V^14581^0^^s
5uc9|Premier High Warlord's Pulverizer|v||h|272848||V^14581^0^^s
5uca|Premier High Warlord's Pig Sticker|v||h|272849||V^14581^0^^s
5ucb|Premier High Warlord's War Staff|v||h|272850||V^14581^0^^s
5ucc|Premier High Warlord's Greatsword|v||h|272851||V^14581^0^^s
5uce|Premier Kodohide Treads|u|n||||
5ucg|Premier Shadowhide Walkers|v|sn||||V^12792^0^^s
5uch|Premier Linked Greaves|u|n||||
5ucj|Premier Silken Walkers|u|n||||
5ucm|Premier Dragonhide Grips|u|n||||
5ucp|Premier Mail Vices|u|n||||
5ucr|Premier Silken Handwraps|u|n||||
5ucx|Premier Linked Hauberk|u|n||||
5ucy|Premier Kodohide Chestpiece|u|n||||
5ucz|Premier Kodohide Leggings|u|n||||
5ud2|Premier Felweave Legguards|u|n||||
5ud6|Premier Silken Tunic|u|n||||
5ud8|Premier Mail Legguards|u|n||||
5ud9|Premier Mortarplate Shoulders|u|n||||
5udc|Premier Chain Shoulders|u|n||||
5udd|Premier Kodohide Headguard|u|n||||
5ude|Premier Kodohide Shoulders|u|n||||
5udf|Premier Felweave Cowl|u|n||||
5udj|Premier Linked Headguard|u|n||||
5udk|Premier Mail Pauldrons|u|n||||
5udl|Premier Silken Hood|u|n||||
5udm|Premier Silken Mantle|u|n||||
5uds|Premier Lunarhide Leggings|u|n||||
5udt|Premier Dreadweave Legguards|u|n||||
5udz|Premier Silken Legguards|u|n||||
5ue5|Premier Lunarhide Headguard|u|n||||
5ue6|Premier Lunarhide Shoulders|u|n||||
5ue7|Premier Dreadweave Cowl|u|n||||
5ued|Premier Mooncloth Hood|u|n||||
5uee|Premier Mooncloth Mantle|u|n||||
5ueg|Premier Magus Mantle|u|n||||
5ueh|Premier High Warlord's Battle Mace|v||h|272857||V^14581^0^^s
5uei|Premier High Warlord's Destroyer|v||h|272858||V^14581^0^^s
5uej|Premier High Warlord's Spellblade|v||h|272856||V^14581^0^^s
5uek|Premier High Warlord's Quickblade|v||h|272859||V^14581^0^^s
5uel|Premier High Warlord's Tome of Destruction|v||h|278158||V^14581^0^^s
5uem|Premier High Warlord's Tome of Mending|v||h|278157||V^14581^0^^s
5uet|Premier Grand Marshal's Longsword|v|sn|a|272452||V^12782^0^^s
5uey|Premier Sergeant's Cloak|v|sn||||V^12781^0^^s
5uez|Premier Sergeant's Cape|v|sn||||V^12781^0^^s
5uf0|Premier Silk Sash|u|n||||
5uf1|Premier Silk Boots|u|n||||
5uf2|Premier Silk Cuffs|u|n||||
5uf3|Premier Silk Gloves|u|n||||
5uf4|Premier Leather Boots|u|n||||
5uf5|Premier Beasthide Footwraps|u|n||||
5uf6|Premier Leather Bracers|u|n||||
5uf7|Premier Beasthide Armsplints|u|n||||
5uf8|Premier Leather Gauntlets|u|n||||
5uf9|Premier Beasthide Gloves|u|n||||
5ufa|Premier Leather Belt|u|n||||
5ufb|Premier Beasthide Girdle|u|n||||
5ufc|Premier Chainmail Girdle|u|n||||
5ufd|Premier Chainmail Boots|u|n||||
5uff|Premier Chainmail Gauntlets|u|n||||
5ufg|Premier Plate Boots|v|sn||||V^12777^0^^s
5ufh|Premier Plate Gauntlets|v|sn||||V^12777^0^^s
5ufi|Premier Chevalier Sabatons|u|n||||
5ufj|Premier Chevalier Gauntlets|u|n||||
5ufk|Premier Chevalier Cinch|u|n||||
5ufl|Premier Chevalier Armsplints|u|n||||
5ufm|Premier Silk Raiment|u|n||||
5ufn|Premier Silk Leggings|u|n||||
5ufo|Premier Silk Spaulders|u|n||||
5ufp|Premier Silk Crown|u|n||||
5ufq|Premier Leather Armor|u|n||||
5ufr|Premier Leather Veil|u|n||||
5ufs|Premier Leather Legguards|u|n||||
5uft|Premier Leather Spaulders|u|n||||
5ufv|Premier Beasthide Leggings|u|n||||
5ufw|Premier Beasthide Epaulets|u|n||||
5ufx|Premier Beasthide Shroud|u|n||||
5ufz|Premier Chainmail Leggings|u|n||||
5ug0|Premier Chainmail Pauldrons|u|n||||
5ug1|Premier Chainmail Helmet|u|n||||
5ug2|Premier Plate Helm|v|sn||||V^12777^0^^s
5ug3|Premier Plate Chestguard|v|sn||||V^12777^0^^s
5ug4|Premier Plate Leggings|v|sn||||V^12777^0^^s
5ug5|Premier Plate Pauldrons|v|sn||||V^12777^0^^s
5ug6|Premier Chevalier Breastplate|u|n||||
5ug7|Premier Chevalier Headguard|u|n||||
5ug8|Premier Chevalier Leggings|u|n||||
5ug9|Premier Chevalier Shoulders|u|n||||
5uga|Premier Knight-Champion's Silk Footwraps|u|n|a|272504||
5ugb|Premier Knight-Captain's Silk Bracers|u|n|a|272503||
5ugc|Premier Knight-Captain's Silk Sash|u|n|a|272502||
5ugd|Premier Lieutenant Commander's Silk Gloves|u|n|a|272505||
5uge|Premier Field Marshal's Silk Coronet|u|n|a|272498||
5ugf|Premier Marshal's Silk Leggings|u|n|a|272499||
5ugg|Premier Field Marshal's Silk Vestments|u|n|a|272500||
5ugh|Premier Marshal's Silk Spaulders|u|n|a|272501||
5ugi|Premier Knight-Captain's Beasthide Bracers|u|n|a|272518||
5ugj|Premier Knight-Champion's Leather Footguards|u|n|a|272523||
5ugk|Premier Knight-Captain's Beasthide Waistguard|u|n|a|272521||
5ugl|Premier Lieutenant Commander's Beasthide Gauntlets|u|n|a|272520||
5ugm|Premier Marshal's Beasthide Spaulders|u|n|a|272516||
5ugn|Premier Marshal's Beasthide Legguards|u|n|a|272517||
5ugo|Premier Field Marshal's Beasthide Helmet|u|n|a|272515||
5ugp|Premier Field Marshal's Beasthide Breastplate|u|n|a|272514||
5ugq|Premier Field Marshal's Leather Chestpiece|u|n|a|272528||
5ugr|Premier Lieutenant Commander's Leather Handgrips|u|n|a|272525||
5ugs|Premier Field Marshal's Leather Mask|u|n|a|272526||
5ugt|Premier Marshal's Leather Leggings|u|n|a|272529||
5ugu|Premier Marshal's Leather Epaulets|u|n|a|272527||
5ugv|Premier Knight-Captain's Leather Cinch|u|n|a|272522||
5ugw|Premier Knight-Champion's Beasthide Boots|u|n|a|272519||
5ugx|Premier Knight-Captain's Leather Armsplints|u|n|a|272524||
5ugy|Premier Knight-Captain's Chainmail Bracers|u|n|a|272535||
5ugz|Premier Knight-Champion's Chainmail Boots|u|n|a|272534||
5uh0|Premier Lieutenant Commander's Chainmail Grips|u|n|a|272536||
5uh1|Premier Knight-Captain's Chainmail Girdle|u|n|a|272537||
5uh2|Premier Field Marshal's Chainmail Helm|u|n|a|272531||
5uh3|Premier Field Marshal's Chainmail Breastplate|u|n|a|272530||
5uh4|Premier Marshal's Chainmail Legguards|u|n|a|272532||
5uh5|Premier Marshal's Chainmail Spaulders|u|n|a|272533||
5uh6|Premier Knight-Captain's Chevalier Armguards|u|n|a|274234||
5uh7|Premier Knight-Captain's Chevalier Belt|u|n|a|274235||
5uh8|Premier Lieutenant Commander's Chevalier Gloves|u|n|a|274236||
5uh9|Premier Knight-Champion's Chevalier Boots|u|n|a|274237||
5uha|Premier Field Marshal's Chevalier Chestplate|u|n|a|274238||
5uhb|Premier Field Marshal's Chevalier Faceguard|u|n|a|274239||
5uhc|Premier Marshal's Chevalier Legplates|u|n|a|274240||
5uhd|Premier Marshal's Chevalier Pauldrons|u|n|a|274241||
5uhe|Premier Field Marshal's Plate Armor|u|n|a|272506||
5uhf|Premier Field Marshal's Plate Helm|u|n|a|272507||
5uhg|Premier Marshal's Plate Legguards|u|n|a|272508||
5uhh|Premier Marshal's Plate Shoulderguards|u|n|a|272509||
5uhi|Premier Knight-Captain's Plate Bracers|u|n|a|272511||
5uhj|Premier Knight-Captain's Plate Girdle|u|n|a|272512||
5uhk|Premier Knight-Champion's Plate Boots|u|n|a|272510||
5uhl|Premier Lieutenant Commander's Plate Gauntlets|u|n|a|272513||
5uhm|Premier Dreadweave Boots|u|n||||
5uhn|Premier Dreadweave Bracers|u|n||||
5uho|Premier Dreadweave Gloves|u|n||||
5uhp|Premier Dreadweave Belt|u|n||||
5uhs|Premier Dreadweave Robe|u|n||||
5uht|Premier Dreadweave Mantle|u|n||||
5uhu|Premier Field Marshal's Dreadweave Coronal|u|n|a|272559||
5uhv|Premier Marshal's Dreadweave Leggings|u|n|a|272561||
5uhw|Premier Marshal's Dreadweave Shoulders|u|n|a|272558||
5uhx|Premier Field Marshal's Dreadweave Robe|u|n|a|272560||
5uhy|Premier Knight-Captain's Dreadweave Cuffs|u|n|a|272555||
5uhz|Premier Knight-Champion's Dreadweave Boots|u|n|a|272554||
5ui0|Premier Lieutenant Commander's Dreadweave Gloves|u|n|a|272556||
5ui1|Premier Knight-Captain's Dreadweave Sash|u|n|a|272557||
5ui2|Premier Voidcloth Boots|u|n||||
5ui3|Premier Voidcloth Cuffs|u|n||||
5ui4|Premier Voidcloth Gloves|u|n||||
5ui5|Premier Voidcloth Cord|u|n||||
5ui6|Premier Voidcloth Diadem|u|n||||
5ui7|Premier Voidcloth Leggings|u|n||||
5ui8|Premier Voidcloth Robes|u|n||||
5ui9|Premier Voidcloth Amice|u|n||||
5uia|Premier Field Marshal's Voidcloth Headdress|u|n|a|272575||
5uib|Premier Marshal's Voidcloth Pants|u|n|a|272577||
5uic|Premier Marshal's Voidcloth Mantle|u|n|a|272574||
5uid|Premier Field Marshal's Voidcloth Vestments|u|n|a|272576||
5uie|Premier Knight-Captain's Voidcloth Bracers|u|n|a|272571||
5uif|Premier Knight-Champion's Voidcloth Sandals|u|n|a|272570||
5uig|Premier Lieutenant Commander's Voidcloth Gloves|u|n|a|272572||
5uih|Premier Knight-Captain's Voidcloth Sash|u|n|a|272573||
5uik|Premier Plate Wristguards|v|sn||||V^12777^0^^s
5uim|Premier Chainmail Armguards|u|n||||
5uiq|Premier Dreamhide Armsplints|u|n||||
5uir|Premier Lunarhide Armsplints|u|n||||
5uiu|Premier Grand Marshal's Aegis|v|sn|a|272591||V^12782^0^^s
5uiv|Premier Grand Marshal's Handaxe|v|sn|a|272592||V^12782^0^^s
5uiw|Premier Grand Marshal's Sunderer|v|sn|a|272593||V^12782^0^^s
5uix|Premier Grand Marshal's Bullseye|v|sn|a|272594||V^12782^0^^s
5uiy|Premier Grand Marshal's Repeater|v|sn|a|272595||V^12782^0^^s
5uiz|Premier Grand Marshal's Dirk|v|sn|a|272596||V^12782^0^^s
5uj0|Premier Grand Marshal's Right Hand Blade|v|sn|a|272597||V^12782^0^^s
5uj1|Premier Grand Marshal's Left Hand Blade|v|sn|a|272598||V^12782^0^^s
5uj2|Premier Grand Marshal's Hand Cannon|v|sn|a|272599||V^12782^0^^s
5uj3|Premier Grand Marshal's Punisher|v|sn|a|272600||V^12782^0^^s
5uj4|Premier Grand Marshal's Battle Hammer|v|sn|a|272601||V^12782^0^^s
5uj5|Premier Grand Marshal's Glaive|v|sn|a|272602||V^12782^0^^s
5uj6|Premier Grand Marshal's Stave|v|sn|a|272603||V^12782^0^^s
5uj7|Premier Grand Marshal's Claymore|v|sn|a|272604||V^12782^0^^s
5uj8|Premier Luminous Breastplate|u|n||||
5uj9|Premier Luminous Leggings|u|n||||
5uja|Premier Luminous Headguard|u|n||||
5ujb|Premier Luminous Shoulders|u|n||||
5ujc|Premier Grand Marshal's Mageblade|v|sn|a|272683||V^12782^0^^s
5ujd|Premier Grand Marshal's Warhammer|v|sn|a|272681||V^12782^0^^s
5uje|Premier Grand Marshal's Demolisher|v|sn|a|272682||V^12782^0^^s
5ujf|Premier Grand Marshal's Swiftblade|v|sn|a|272684||V^12782^0^^s
5um5|Theramore Shoulderguards|ev|sn||||V^263569^194609^h^s~r^2799^7^Theramore Expeditionary Force^f
5um6|Darkspear Shoulderguards|ev|sn|h|||V^263570^195317^h^s~r^2798^7^Darkspear Raiders^f
5un8|Trogg Scepter|dw|sn||||d^389^Oggleflint^12.5^0^s~m^11517^Oggleflint^0^s
5una|Bone Knuckles|dw|sn||||d^389^Oggleflint^50^0^s~m^11517^Oggleflint^0^s
5unb|Barbaric Crossbow|dw|sn||||d^389^Oggleflint^37.5^0^s~m^11517^Oggleflint^0^s
5unf|Searing Dagger|dw|sn||||d^389^Bazzalan^43.75^0^s~m^11519^Bazzalan^0^s
5unh|Satyrskin Cloak|dw|sn||||d^389^Bazzalan^37.5^0^s~m^11519^Bazzalan^0^s
5unj|Chasm Walkers|dw|sn||||d^389^Bazzalan^18.75^0^s~m^11519^Bazzalan^0^s
5uny|Supple Bellyskin Leggings|d|sn||||d^2998^Saltspine^75^0^s
5unz|Saltscale Girdle|w|sn||||m^260322^NPC 260322^0^s
5uo0|Glinteye Slippers|d|sn||||d^2998^Saltspine^25^0^s
5uo1|Raptorclaw Greaves|d|sn||||d^2998^Shadetooth^50^0^s
5uo2|Garb of Florid Feathers|d|sn||||d^2998^Shadetooth^25^0^s
5uo3|Raptor's Gaze|d|sn||||d^2998^Shadetooth^25^0^s
5uo4|Reliquary Mantle|d|sn||||d^2998^Relic Guardian^50^0^s
5uo5|Golemsight Long Gun|d|sn||||d^2998^Relic Guardian^25^0^s
5uo6|Ring of Power Regulation|d|sn||||d^2998^Relic Guardian^25^0^s
5uo7|Runemender's Seal|d|sn||||d^2959^Arcane Anomaly^28.57^0^s
5uo8|Bonebinder's Signet|d|sn||||d^2959^Atrexis the Grave Knight^42.86^0^s
5uo9|Gravespike Repeater|d|sn||||d^2959^Atrexis the Grave Knight^42.86^0^s
5uoa|Ephemeral Grips|d|sn||||d^2959^Arcane Anomaly^42.86^0^s
5uob|Mana-Warped Chain Shirt|d|sn||||d^2959^Arcane Anomaly^28.57^0^s
5uoc|Graveweave Bindings|d|sn||||d^2959^Atrexis the Grave Knight^14.29^0^s
5uod|Felbough Arm|d|sn||||d^2959^Fel Ancient^42.86^0^s
5uoe|Garb of Fallen Felbark|d|sn||||d^2959^Fel Ancient^14.29^0^s
5uof|Blightleaf Rope|d|sn||||d^2959^Fel Ancient^42.86^0^s
5uog|Spine of the Devourer|d|sn||||d^2959^Mana Devourer^33.33^0^s
5uoh|Slitherwrap Girdle|d|sn||||d^2959^Mana Devourer^16.67^0^s
5uoi|Manascale Treads|d|sn||||d^2959^Mana Devourer^50^0^s
5uoj|Wand of Mana Concentration|d|sn||||d^2959^Mana Elemental^28.57^0^s
5uok|Violet Sorcerer's Robes|d|sn||||d^2959^Mana Elemental^14.29^0^s
5uol|Drape of Shifting Energy|d|sn||||d^2959^Mana Elemental^57.14^0^s
5uom|Guardian's Dualblade|d|sn||||d^2959^Unstable Sentinel^71.43^0^s
5uon|Unstable Crystalline Shoulderpads|d|sn||||d^2959^^0^0^c
5uoo|Refractory Scaleguards|d|sn||||d^2959^Unstable Sentinel^28.57^0^s
5uop|Archmagister's Faceted Pendant|d|sn||||d^2959^Shade of the Archmage^42.86^0^s
5uor|Violet Sorcerer's Mantle|d|sn||||d^2959^Shade of the Archmage^42.86^0^s
5uos|Ponderous Orb|d|sn||||d^2959^Shade of the Archmage^14.29^0^s
5uot|Tendonscraper Dagger|d|sn||||d^2959^Lyn the Ignored^50^0^s
5uou|Cartilage Shapers|d|sn||||d^2959^Lyn the Ignored^25^0^s
5uov|Bonepile Gaze|d|sn||||d^2959^Lyn the Ignored^25^0^s
5ups|Snake Eye Kaleidoscope|dw|sn||||d^43^Lady Anacondra^80^0^s~m^3671^Lady Anacondra^0^s
5upt|Slither Cord|dw|sn||||d^43^Lord Pythas^22.22^0^s~m^3670^Lord Pythas^0^s
5ur5|Skum's Bucket|dw|sn||||d^43^Skum^12.5^0^s~m^3674^Skum^0^s
5uvd|Ogre Loincloth|dw|sn||||d^36^Rhahk'Zor^26.32^0^s~m^644^Rhahk'Zor^0^s
5uvh|Bandsaw Wristbands|dw|sn||||d^36^Sneed^52.38^0^s~m^643^Sneed^0^s
5uvl|Goblin Hammer|dw|sn||||d^36^Gilnid^14.29^0^s~m^1763^Gilnid^0^s
5uwc|Premier Mortarplate Girdle|u|n||||
5uwd|Premier Plate Girdle|v|sn||||V^12777^0^^s
5uwf|Premier Knight-Captain's Luminous Armguards|u|n|a|274248||
5uwg|Premier Knight-Captain's Luminous Belt|u|n|a|274249||
5uwh|Premier Lieutenant Commander's Luminous Gloves|u|n|a|274250||
5uwi|Premier Knight-Champion's Luminous Boots|u|n|a|274251||
5uwj|Premier Field Marshal's Luminous Chestplate|u|n|a|274252||
5uwk|Premier Field Marshal's Luminous Faceguard|u|n|a|274253||
5uwl|Premier Marshal's Luminous Legplates|u|n|a|274254||
5uwm|Premier Marshal's Luminous Pauldrons|u|n|a|274255||
5uwo|Premier Centurion's Mail Boots|u||h|274198||
5uwp|Premier Champion's Mail Gauntlets|u||h|274199||
5uwq|Premier Legionnaire's Mail Waistband|u||h|274200||
5uwr|Premier Legionnaire's Mail Bracers|u||h|274201||
5uws|Premier Warlord's Mail Armor|u||h|274202||
5uwt|Premier Warlord's Mail Helm|u||h|274203||
5uwu|Premier General's Mail Leggings|u||h|274204||
5uwv|Premier General's Mail Spaulders|u||h|274205||
5uww|Premier Centurion's Ringmail Boots|u||h|274206||
5uwx|Premier Champion's Ringmail Gauntlets|u||h|274207||
5uwy|Premier Legionnaire's Ringmail Waistband|u||h|274208||
5uwz|Premier Legionnaire's Ringmail Bracers|u||h|274209||
5ux0|Premier Warlord's Ringmail Armor|u||h|274210||
5ux1|Premier Warlord's Ringmail Helm|u||h|274211||
5ux2|Premier General's Ringmail Leggings|u||h|274212||
5ux3|Premier General's Ringmail Spaulders|u||h|274213||
5ux4|Premier Linked Girdle|u|n||||
5ux5|Premier Mail Wristguards|u|n||||
5ux7|Premier Ringmail Walkers|u|n||||
5ux8|Premier Ringmail Helm|u|n||||
5ux9|Premier Ringmail Chestpiece|u|n||||
5uxa|Premier Ringmail Vices|u|n||||
5uxb|Premier Ringmail Legguards|u|n||||
5uxc|Premier Ringmail Pauldrons|u|n||||
5uxd|Premier Ringmail Wristguards|u|n||||
5uxe|Premier Ringmail Girdle|u|n||||
5uxf|Premier Luminous Gauntlets|u|n||||
5uxg|Premier Luminous Armsplints|u|n||||
5uxh|Premier Luminous Sabatons|u|n||||
5uxi|Premier Luminous Cinch|u|n||||
5uxj|Premier Kodohide Waistband|u|n||||
5uxk|Premier Lunarhide Gloves|u|n||||
5uxl|Premier Lunarhide Girdle|u|n||||
5uxm|Premier Lunarhide Footwraps|u|n||||
5uxn|Premier Lunarhide Tunic|u|n||||
5uxo|Premier Mail Girdle|u|n||||
5uxp|Premier Dreamhide Leggings|u|n||||
5uxq|Premier Dreamhide Headguard|u|n||||
5uxr|Premier Dreamhide Shoulders|u|n||||
5uxu|Premier Dreamhide Girdle|u|n||||
5uxw|Premier Dreamhide Tunic|u|n||||
5uxx|Premier Wyrmhide Armguards|u|n||||
5uxy|Premier Wyrmhide Gauntlets|u|n||||
5uxz|Premier Wyrmhide Treads|u|n||||
5uy0|Premier Wyrmhide Chestpiece|u|n||||
5uy1|Premier Wyrmhide Leggings|u|n||||
5uy2|Premier Wyrmhide Headguard|u|n||||
5uy3|Premier Wyrmhide Shoulders|u|n||||
5uy4|Premier Wyrmhide Waistband|u|n||||
5uy5|Premier Knight-Captain's Lunarhide Bracers|u|n|a|273409||
5uy6|Premier Knight-Captain's Lunarhide Waistguard|u|n|a|273412||
5uy7|Premier Lieutenant Commander's Lunarhide Gauntlets|u|n|a|273411||
5uy8|Premier Marshal's Lunarhide Spaulders|u|n|a|273407||
5uy9|Premier Marshal's Lunarhide Legguards|u|n|a|273408||
5uya|Premier Field Marshal's Lunarhide Helmet|u|n|a|273406||
5uyb|Premier Field Marshal's Lunarhide Breastplate|u|n|a|273405||
5uyc|Premier Knight-Champion's Lunarhide Boots|u|n|a|273410||
5uyd|Premier Knight-Captain's Dreamhide Bracers|u|n|a|273417||
5uye|Premier Knight-Captain's Dreamhide Waistguard|u|n|a|273420||
5uyf|Premier Lieutenant Commander's Dreamhide Gauntlets|u|n|a|273419||
5uyg|Premier Marshal's Dreamhide Spaulders|u|n|a|273415||
5uyh|Premier Marshal's Dreamhide Legguards|u|n|a|273416||
5uyi|Premier Field Marshal's Dreamhide Helmet|u|n|a|273414||
5uyj|Premier Field Marshal's Dreamhide Breastplate|u|n|a|273413||
5uyk|Premier Knight-Champion's Dreamhide Boots|u|n|a|273418||
5uyl|Premier Warlord's Wyrmhide Hauberk|u||h|273395||
5uym|Premier Warlord's Wyrmhide Helmet|u||h|273394||
5uyn|Premier General's Wyrmhide Epaulets|u||h|273392||
5uyo|Premier General's Wyrmhide Leggings|u||h|273393||
5uyp|Premier Legionnaire's Wyrmhide Bracers|u||h|273389||
5uyq|Premier Centurion's Wyrmhide Boots|u||h|273396||
5uyr|Premier Champion's Wyrmhide Gloves|u||h|273391||
5uys|Premier Legionnaire's Wyrmhide Belt|u||h|273390||
5uyt|Premier Warlord's Kodohide Hauberk|u||h|273403||
5uyu|Premier Warlord's Kodohide Helmet|u||h|273402||
5uyv|Premier General's Kodohide Epaulets|u||h|273400||
5uyw|Premier General's Kodohide Leggings|u||h|273401||
5uyx|Premier Legionnaire's Kodohide Bracers|u||h|273397||
5uyy|Premier Centurion's Kodohide Boots|u||h|273404||
5uyz|Premier Champion's Kodohide Gloves|u||h|273399||
5uz0|Premier Legionnaire's Kodohide Belt|u||h|273398||
5uz1|Premier Field Marshal's Mooncloth Headdress|u|n|a|273434||
5uz2|Premier Marshal's Mooncloth Pants|u|n|a|273436||
5uz3|Premier Marshal's Mooncloth Mantle|u|n|a|273433||
5uz4|Premier Field Marshal's Mooncloth Vestments|u|n|a|273435||
5uz5|Premier Knight-Captain's Mooncloth Bracers|u|n|a|273430||
5uz6|Premier Knight-Champion's Mooncloth Sandals|u|n|a|273429||
5uz7|Premier Lieutenant Commander's Mooncloth Gloves|u|n|a|273431||
5uz8|Premier Knight-Captain's Mooncloth Sash|u|n|a|273432||
5uz9|Premier Centurion's Silken Boots|u||h|273426||
5uza|Premier Legionnaire's Silken Bracers|u||h|273425||
5uzb|Premier Champion's Silken Gloves|u||h|273427||
5uzc|Premier Legionnaire's Silken Cinch|u||h|273428||
5uzd|Premier General's Silken Mantle|u||h|273423||
5uze|Premier Warlord's Silken Cowl|u||h|273421||
5uzf|Premier Warlord's Silken Robes|u||h|273424||
5uzg|Premier General's Silken Leggings|u||h|273422||
5uzn|Premier Mooncloth Boots|u|n||||
5uzo|Premier Mooncloth Cuffs|u|n||||
5uzp|Premier Mooncloth Gloves|u|n||||
5uzr|Premier Mooncloth Leggings|u|n||||
5uzs|Premier Mooncloth Robes|u|n||||
5uzt|Premier Mooncloth Cord|u|n||||
5uzu|Premier Silken Cuffs|u|n||||
5v00|Cell Keeper's Claws|dw|sn||||d^33^Rethilgore^25^0^s~m^3914^Rethilgore^0^s
5v01|Sorcerer Collar|dw|sn||||d^33^Rethilgore^0^0^s~m^3914^Rethilgore^0^s
5v51|Blade of Silverlaine|dw|sn||||d^33^Baron Silverlaine^33.33^0^s~m^3887^Baron Silverlaine^0^s
5v57|Worgenbane Talisman|dw|sn||||d^33^Commander Springvale^22.22^0^s~m^4278^Commander Springvale^0^s
5v59|Blindwatcher's Sight|dw|sn||||d^33^Odo the Blindwatcher^55.56^0^s~m^4279^Odo the Blindwatcher^0^s
5v5a|Half-Eaten Boots|dw|sn||||d^33^Fenrus the Devourer^11.11^0^s~m^4274^Fenrus the Devourer^0^s
5v5b|Worgpelt Leggings|dw|sn||||d^33^Wolf Master Nandos^33.33^0^s~m^3927^Wolf Master Nandos^0^s
5v5i|Crystal Thread Cloak|q|sn||||q^96260^Stronger than Steel^24^^s
5v9o|Executioner Mantle|dw|sn||||d^34^Targorr the Dread^25^0^s~m^1696^Targorr the Dread^0^s
5v9p|Blackrock Harness|dw|sn||||d^34^Targorr the Dread^50^0^s~m^1696^Targorr the Dread^0^s
5v9q|Dark Horde Band|dw|sn||||d^34^Targorr the Dread^25^0^s~m^1696^Targorr the Dread^0^s
5v9r|Demolition Girdle|dw|sn||||d^34^Kam Deepfury^17.65^0^s~m^1666^Kam Deepfury^0^s
5v9s|Bridgebreaker Bindings|dw|sn||||d^34^Kam Deepfury^52.94^0^s~m^1666^Kam Deepfury^0^s
5v9t|Hamhock's Cleaver|dw|sn||||d^34^Hamhock^41.18^0^s~m^1717^Hamhock^0^s
5v9u|Ogre Grips|dw|sn||||d^34^Hamhock^17.65^0^s~m^1717^Hamhock^0^s
5v9v|Repurposed Rack|dw|sn||||d^34^Hamhock^41.18^0^s~m^1717^Hamhock^0^s
5va0|Apprentice's Blouse|u|n||||
5va1|Graverobber's Shovel|dw|snU||||d^34^Dextren Ward^25^0^s~m^1663^Dextren Ward^0^s
5va8|Defias Jailbreakers|dw|sn||||d^34^Bazil Thredd^50^0^s~m^1716^Bazil Thredd^0^s
5va9|Red Wool Cloak|dw|sn||||d^34^Bazil Thredd^12.5^0^s~m^1716^Bazil Thredd^0^s
5vab|Debt Collector|dw|sn||||d^34^Bazil Thredd^0^0^s~m^1716^Bazil Thredd^0^s
5vad|Concealed Hand Crossbow|dw|sn||||d^34^Bazil Thredd^43.75^0^s~m^1716^Bazil Thredd^0^s
5van|Spiked Shell Band|dw|sn||||d^48^Ghamoo-ra^16.67^0^s~m^4887^Ghamoo-ra^0^s
5vap|Twilight Maul|dw|sn||||d^48^Lorgus Jett^0^0^s~m^12902^Lorgus Jett^0^s
5vaq|Treacherous Treads|dw|sn||||d^48^Lorgus Jett^0^0^s~m^12902^Lorgus Jett^0^s
5var|Fallenroot Longbow|dw|sn||||d^48^Lorgus Jett^0^0^s~m^12902^Lorgus Jett^0^s
5vau|Twilight Lord Girdle|dw|sn||||d^48^Twilight Lord Kelris^8.33^0^s~m^4832^Twilight Lord Kelris^0^s
5vbn|Empyrean Treads|q|sn||||q^93835^Quest 93835^7^^s~q^92646^Confront Lorthuna^7^^s
5vbo|Broken Cultist Gloves|q|sn||||q^92640^Desperate Times^6^^s
5vbp|Windswept Shortbow|q|sn||||q^92528^Among the Faithful^3^^s
5vbr|Refined Shortbow|q|sn||||q^92470^Foul Matriarch^2^^s
5vg3|Staghide Drape|u|n||||
5vga|Skullduggery Belt|w|sn||||m^7361^Grubbis^0^s
5vgb|Irradiated Shield|dw|sn||||d^90^Grubbis^60^0^s~m^7361^Grubbis^0^s
5vh0|Thermaplugg Medal of Honor|dw|sn||||d^90^Crowd Pummeler 9-60^20^0^s~m^6229^Crowd Pummeler 9-60^0^s
5vha|Boar Signet|Q|sn||||q^1144^Willix the Importer^25^^s
5vhg|Quilboar Blaster|Q|sn||||q^1102^A Vengeful Fate^29^h^s~q^1101^The Crone of the Kraul^29^a^s
5vj9|Thornweaver Drape|w|sn||||m^6168^Roogug^0^s
5vjc|Roogug's Severed Head|dw|sn||||d^47^Roogug^50^0^s~m^6168^Roogug^0^s
5vjf|Geomancer Headdress|d|sn||||d^47^Roogug^50^0^s
5vji|Death Prophet Spine|d|sn||||d^47^^0^0^c
5vjj|Thorncursed Grips|dw|sn||||d^47^Aggem Thorncurse^20^0^s~m^4424^Aggem Thorncurse^0^s
5vjk|Quilrager Throwing Axe|dw|sn||||d^47^Agathelos the Raging^80^0^s~m^4422^Agathelos the Raging^0^s
5vjl|Quillord Mail Leggings|dw|sn||||d^47^Overlord Ramtusk^40^0^s~m^4420^Overlord Ramtusk^0^s
5vk0|Premier Scalemail Walkers|v|sn||||V^12777^0^^s
5vk1|Premier Flatmail Grips|v|sn||||V^12777^0^^s
5vk2|Premier Scalemail Helm|v|sn||||V^12777^0^^s
5vk3|Premier Scalemail Chestpiece|v|sn||||V^12777^0^^s
5vk4|Premier Flatmail Leggings|v|sn||||V^12777^0^^s
5vk5|Premier Flatmail Shoulders|v|sn||||V^12777^0^^s
5vk6|Premier Flatmail Wristguards|v|sn||||V^12777^0^^s
5vk7|Premier Knight-Champion's Flatmail Boots|u|n|a|272538||
5vk8|Premier Lieutenant Commander's Flatmail Gauntlets|u|n|a|272539||
5vk9|Premier Knight-Captain's Flatmail Waistband|u|n|a|272540||
5vka|Premier Knight-Captain's Flatmail Bracers|u|n|a|272541||
5vkb|Premier Field Marshal's Flatmail Armor|u|n|a|272542||
5vkc|Premier Field Marshal's Flatmail Helm|u|n|a|272543||
5vkd|Premier Marshal's Flatmail Leggings|u|n|a|272544||
5vke|Premier Marshal's Flatmail Spaulders|u|n|a|272545||
5vkg|Premier Flatmail Greaves|v|sn||||V^12777^0^^s
5vkh|Premier Scalemail Vices|v|sn||||V^12777^0^^s
5vki|Premier Flatmail Hauberk|v|sn||||V^12777^0^^s
5vkj|Premier Scalemail Legguards|v|sn||||V^12777^0^^s
5vkk|Premier Flatmail Headguard|v|sn||||V^12777^0^^s
5vkl|Premier Scalemail Pauldrons|v|sn||||V^12777^0^^s
5vkm|Premier Knight-Champion's Scalemail Boots|u|n|a|273336||
5vkn|Premier Lieutenant Commander's Scalemail Gauntlets|u|n|a|273337||
5vko|Premier Knight-Captain's Scalemail Waistband|u|n|a|273338||
5vkp|Premier Knight-Captain's Scalemail Bracers|u|n|a|273339||
5vkq|Premier Field Marshal's Scalemail Armor|u|n|a|273340||
5vkr|Premier Field Marshal's Scalemail Helm|u|n|a|273341||
5vks|Premier Marshal's Scalemail Leggings|u|n|a|273342||
5vkt|Premier Marshal's Scalemail Spaulders|u|n|a|273343||
5vku|Premier Knight-Champion's Linkmail Boots|u|n|a|273344||
5vkv|Premier Lieutenant Commander's Linkmail Gauntlets|u|n|a|273345||
5vkw|Premier Knight-Captain's Linkmail Waistband|u|n|a|273346||
5vkx|Premier Knight-Captain's Linkmail Bracers|u|n|a|273347||
5vky|Premier Field Marshal's Linkmail Armor|u|n|a|273348||
5vkz|Premier Field Marshal's Linkmail Helm|u|n|a|273349||
5vl0|Premier Marshal's Linkmail Leggings|u|n|a|273350||
5vl1|Premier Marshal's Linkmail Spaulders|u|n|a|273351||
5vl2|Premier Flatmail Girdle|v|sn||||V^12777^0^^s
5vl3|Premier Scalemail Wristguards|v|sn||||V^12777^0^^s
5vl5|Premier Linkmail Walkers|v|sn||||V^12777^0^^s
5vl6|Premier Linkmail Helm|v|sn||||V^12777^0^^s
5vl7|Premier Linkmail Chestpiece|v|sn||||V^12777^0^^s
5vl8|Premier Linkmail Vices|v|sn||||V^12777^0^^s
5vl9|Premier Linkmail Legguards|v|sn||||V^12777^0^^s
5vla|Premier Linkmail Pauldrons|v|sn||||V^12777^0^^s
5vlb|Premier Linkmail Wristguards|v|sn||||V^12777^0^^s
5vlc|Premier Linkmail Girdle|v|sn||||V^12777^0^^s
5vld|Premier Scalemail Girdle|v|sn||||V^12777^0^^s
5vle|Premier Scaled Sabatons|u|n||||
5vlf|Premier Scaled Gauntlets|u|n||||
5vlg|Premier Scaled Cinch|u|n||||
5vlh|Premier Scaled Armsplints|u|n||||
5vli|Premier Scaled Breastplate|u|n||||
5vlk|Premier Scaled Leggings|u|n||||
5vll|Premier Scaled Shoulders|u|n||||
5vlm|Premier Legionnaire's Scaled Armguards|u||h|272778||
5vln|Premier Legionnaire's Scaled Belt|u||h|272779||
5vlo|Premier Champion's Scaled Gloves|u||h|272780||
5vlp|Premier Centurion's Scaled Boots|u||h|272781||
5vlq|Premier Warlord's Scaled Chestplate|u||h|272782||
5vlr|Premier Warlord's Scaled Faceguard|u||h|272783||
5vls|Premier General's Scaled Legplates|u||h|272784||
5vlt|Premier General's Scaled Pauldrons|u||h|272785||
5vlw|Premier Lamellar Breastplate|u|n||||
5vlx|Premier Lamellar Leggings|u|n||||
5vly|Premier Lamellar Headguard|u|n||||
5vlz|Premier Lamellar Shoulders|u|n||||
5vm0|Premier Legionnaire's Lamellar Armguards|u||h|273327||
5vm1|Premier Legionnaire's Lamellar Belt|u||h|273328||
5vm2|Premier Champion's Lamellar Gloves|u||h|273329||
5vm3|Premier Centurion's Lamellar Boots|u||h|273330||
5vm4|Premier Warlord's Lamellar Chestplate|u||h|273331||
5vm5|Premier Warlord's Lamellar Faceguard|u||h|273332||
5vm6|Premier General's Lamellar Legplates|u||h|273333||
5vm7|Premier General's Lamellar Pauldrons|u||h|273334||
5vm8|Premier Lamellar Gauntlets|u|n||||
5vm9|Premier Lamellar Armsplints|u|n||||
5vma|Premier Lamellar Sabatons|u|n||||
5vmb|Premier Lamellar Cinch|u|n||||
5vmh|Brush Cutter|u|n||||
5vn6|Painwalker Buckler|dw|sn||||d^189^Interrogator Vishas^9.09^0^s~m^3983^Interrogator Vishas^0^s
5vn7|Polished Skullcap|dw|sn||||d^189^Bloodmage Thalnos^9.09^0^s~m^4543^Bloodmage Thalnos^0^s
5vn8|Houndmaster Boomerang|dw|sn||||d^189^Houndmaster Loksey^0^0^s~m^3974^Houndmaster Loksey^0^s
5vn9|Spellsever Crossbow|dw|sn||||d^189^Arcanist Doan^0^0^s~m^6487^Arcanist Doan^0^s
5vna|Library Walkers|w|sn||||m^6487^Arcanist Doan^0^s
5vnb|Band of Crimson Light|dw|sn||||d^189^Herod^0^0^s~m^3975^Herod^0^s
5vpo|Decaying Flesh Bands|d|sn||||d^129^^0^0^c
5vpp|Coldbringer Spine|dw|sn||||d^129^Amnennar the Coldbringer^100^0^s~m^7358^Amnennar the Coldbringer^0^s
5vpr|Kanai's Knife|u|n||||
5vps|Illegible Dogtags|u|n||||
5vpt|Abomination Chain|d|sn||||d^129^^0^0^c
5vpu|Toy Soldier|u|n||||
5vqp|Barkskin Baubles|u|n||||
5vqq|Burrow Barricade|u|n||||
5vqr|Bear Poking Stick|u|n||||
5vqs|Wisepaw Totem|u|n||||
5vqx|White Obsidian Wand|dw|sn||||d^70^Obsidian Sentinel^0^0^s~m^7023^Obsidian Sentinel^0^s
5vr0|Dark Golem Breastplate|u|n||||
5vr2|Rock Sentinel Slicer|w|sn||||m^7023^Obsidian Sentinel^0^s
5vr3|Sandstorm Staff|u|n||||
5vr4|Stone Keeper Spire|dw|sn||||d^70^Archaedas^0^0^s~m^2748^Archaedas^0^s
5vsl|Axe of Lingering Dread|u|n||||
5vsq|Centaur Hoofwarmers|u|n||||
5vvq|Bloodslash Axe|w|sn||||m^258905^NPC 258905^0^s
5vvr|Oathbound Bracers|w|sn||||m^258905^NPC 258905^0^s
5vvs|Berserker Shackles|w|sn||||m^258905^NPC 258905^0^s
5vvt|Harpoon of Command|w|sn||||m^258924^NPC 258924^0^s
5vvu|Brinebelly Leggings|w|sn||||m^258924^NPC 258924^0^s
5vvv|Dreadfrost Saber|w|sn||||m^260042^NPC 260042^0^s
5vvw|Frosty Blunderbuss|w|sn||||m^260042^NPC 260042^0^s
5vvx|Briny Sash|w|sn||||m^260042^NPC 260042^0^s
5vvy|Bloodspine Staff|w|sn||||m^260202^NPC 260202^0^s
5vvz|Viscera Spaulders|w|sn||||m^260202^NPC 260202^0^s
5vw0|Maw of Min'loth|w|sn||||m^260243^NPC 260243^0^s
5vw1|Serpentbane Crown|u|n||||
5vw2|Ritual-Binder's Gloves|w|sn||||m^260243^NPC 260243^0^s
5vw3|Robe of the Drowned|u|n||||
5vw4|Waterlogged Burial Shroud|w|sn||||m^263886^NPC 263886^0^s
5vw5|Priestess Cloak|w|sn||||m^258924^NPC 258924^0^s
5vw6|Knucklebone Ring|w|sn||||m^260202^NPC 260202^0^s
5vwu|Sandfury Pauldrons|d|n||||d^209^^0^0^c
5vwv|Sacrificial Chain Vest|d|n||||d^209^^0^0^c
5vwx|Theka's Last Breath|d|n||||d^209^Theka the Martyr^0^0^c
5vwy|Blood Ritual Ring|d|n||||d^209^^0^0^c
5vwz|Gutcutter Hatchet|d|n||||d^209^^0^0^c
5vx0|Undying Headdress|d|n||||d^209^^0^0^c
5vx1|Desert Ziggurat Drape|d|n||||d^209^^0^0^c
5vx2|Arch of the Covenant|d|n||||d^209^^0^0^c
5vx3|Farraki Kris|d|n||||d^209^^0^0^c
5vx7|Zealot Plate|u|n||||
5vx8|Wall of Water|w|sn||||m^7795^Hydromancer Velratha^0^s
5vx9|Deep Ritual Girdle|u|n||||
5vxa|Sandfury Guillotine|u|n||||
5vxb|Peacekeeper Wand|u|n||||
5vxd|Hydra Leather Legs|u|n||||
5vxe|Dune Hacker|u|n||||
5vxf|Bloodsand Belt|u|n||||
5vxg|Sandarr's Shoulders|u|n||||
5vz2|Lost Veteran's Sabatons|u|n||||
5vz3|Forgotten Trompers|u|n||||
5vz5|Tattered Sandals|u|n||||
5vzo|Quilted Cloak|ev|sn||||V^265574^4068^h^s~r^470^4^Ratchet^f
5vzp|Rumpled Kilt|ev|sn||||V^265574^5445^h^s~r^470^4^Ratchet^f
5vzq|Ratchet Wristwraps|ev|sn||||V^265574^3442^h^s~r^470^4^Ratchet^f
5vzr|Defective Samophlange|ev|sn||||V^265574^6581^h^s~r^470^5^Ratchet^f
5vzs|Barrens Basher|ev|sn||||V^265574^16516^h^s~r^470^5^Ratchet^f
5vzt|Deckswabber's Mitts|ev|sn||||V^265575^11042^h^s~r^21^4^Booty Bay^f
5vzu|Sea Giant's Toe Ring|ev|sn||||V^265575^14775^h^s~r^21^4^Booty Bay^f
5vzv|Soggy Boots|ev|sn||||V^265575^10322^h^s~r^21^4^Booty Bay^f
5vzw|Booty Bay Bruiser's Buckshot|ev|sn||||V^265575^31088^h^s~r^21^5^Booty Bay^f
5vzx|Souvenir Sea Shell|ev|sn||||V^265575^16643^h^s~r^21^5^Booty Bay^f
5vzy|Reflective Wristguards|ev|sn||||V^265576^27439^^s~r^369^4^Gadgetzan^f
5vzz|Sunburn Spaulders|ev|sn||||V^265576^29423^^s~r^369^4^Gadgetzan^f
5w00|Sandstorm Cover|ev|sn||||V^265576^23565^^s~r^369^4^Gadgetzan^f
5w01|Jhordy's Misplaced Screwdriver|ev|sn||||V^265576^94614^^s~r^369^5^Gadgetzan^f
5w02|Suspicious Spare Part|ev|sn||||V^265576^37989^^s~r^369^5^Gadgetzan^f
5w03|Steamwheedle Grips|e|n||||r^577^4^Everlook^f
5w04|Impractical Headwarmer|e|n||||r^577^4^Everlook^f
5w05|Substandard Belt Chain|e|n||||r^577^4^Everlook^f
5w06|Coldmetal Guard|e|n||||r^577^4^Everlook^f
5w4j|Sacristan Band|q|sn||||q^95615^In Memoriam^33^^s
5w4k|Verger Greaves|q|sn||||q^95615^In Memoriam^33^^s
5w4n|Neophyte's Wand|q|sn||||q^94877^Saving Sunnyglade^35^^s
5w4o|Twilight Carver|q|sn||||q^94877^Saving Sunnyglade^35^^s
5w4w|Curly's Chopper|q|sn||||q^94861^Helping Hands^34^^s
5w4x|Hurley's Felling Axe|q|sn||||q^94861^Helping Hands^34^^s
5w4z|Fur-Lined Bracers|q|sn||||q^95913^Fit for a Princess^33^^s
5w50|Coyote Hide Wraps|q|sn||||q^95913^Fit for a Princess^33^^s
5w56|Gnollhide Tunic|q|sn||||q^94679^Snargl's Snout^35^^s
5w57|Southern Watch Leggings|q|sn||||q^94679^Snargl's Snout^35^^s
5w58|Unbalanced Fighting Stick|q|sn||||q^94679^Snargl's Snout^35^^s
5w59|Bristle Hills Mystic Robe|q|sn||||q^94679^Snargl's Snout^35^^s
5w5a|Bristlepelt Vest|u|n||||
5w5b|Gnoll Crusher Leggings|u|n||||
5w5c|Bloodsnout Striker|u|n||||
5w5e|Gnollblood Robe|u|n||||
5w5g|Bottle of Powderfuse Port|q|sn||||q^95267^Quest 95267^37^^s
5w5k|Jom-jom's Gabbar|q|sn||||q^94556^Quest 94556^37^^s
5w5n|Clobrok's Block Rock|q|sn||||q^94556^Quest 94556^37^^s
5w5p|Lumber Luggers|q|sn||||q^96009^High Stakes^33^^s
5w5r|Farholde Horns|q|sn||||q^95064^Preventative Measures^34^^s
5w5t|Brute Slayer Band|q|sn||||q^95064^Preventative Measures^34^^s
5w5u|Crocskin Waders|q|sn||||q^95991^WANTED: Ghostmaw^37^^s
5w60|Premier Senior Sergeant's Insignia|v||h|274969||V^12793^0^^s
5w61|Premier Master Sergeant's Insignia|v|sn|a|274968||V^12781^0^^s
5w6r|Slavecrusher Scepter|u|sn||||
5w6s|Resistance Breaker Spaulder|w|sn||||m^258966^NPC 258966^0^s
5w6t|Chain of Binding|u|n||||
5w6u|Shadowlight Athame|w|sn||||m^258972^NPC 258972^0^s
5w6v|Shadecaster's Leggings|u|n||||
5w6w|Zarmok's Plated Signet|w|sn||||m^258972^NPC 258972^0^s
5w6x|Bloodied Gutslicer|w|sn||||m^259281^NPC 259281^0^s
5w6y|War Handler's Gaze|u|n||||
5w6z|Worgbinder's Treads|u|n||||
5w70|Chain of the Corruptor|w|sn||||m^258964^NPC 258964^0^s
5w71|Krol'dok Warplate Chest|w|sn||||m^258964^NPC 258964^0^s
5w72|Krol'dok Warplate Helmet|u|sn||||
5w73|Mugg's Jabber|u|n||||
5w74|Mugg's Crosser|w|sn||||m^258968^NPC 258968^0^s
5w75|Emblem of Slamming|w|sn||||m^258968^NPC 258968^0^s
5w76|Strongly Scented Hood|w|sn||||m^258968^NPC 258968^0^s
5w77|Thud Hammer|u|n||||
5w7h|Prisoner Handwraps|q|sn||||q^94927^Quest 94927^39^^s
5w7j|Bolder'ok Loincloth|q|sn||||q^94927^Quest 94927^39^^s
5w7l|Dunston's Ogre Duster|q|sn||||q^94927^Quest 94927^39^^s
5w7o|Twilight Mine Light|q|sn||||q^96015^Quest 96015^38^^s
5w7w|Pauldron of Order|u|n||||
5w80|Head-Harvest Crossbow|u|n||||
5w81|Bloodied Sash|u|n||||
5w83|Bloodmaster's Ring|u|n||||
5w84|Bloodsport Band|u|n||||
5w85|Ogre Horn Ring|u|n||||
5w86|Twilight Overlord Drape|q|sn||||q^94890^Quest 94890^41^^s
5w89|Farholde Bastion|q|sn||||q^94890^Quest 94890^41^^s
5w8a|Cloak of the Cult|u|n||||
5w8b|Twilight Barrier|u|n||||
5w8c|Orc Bone Bow|q|sn||||q^95066^The Rog'mar Situation^34^^s
5wey|Stormforged Protector|u|n||||
5wez|Staff of the Deeproar|u|n||||
5wf1|Barkskin Scepter|u|n||||
5wf4|Deadwood Boomstick|u|n||||
5whq|Shallow Bindings|u|n||||
5wiy|Murkborn Girdle|u|n||||
5wj1|Premier Silken Sash|u|n||||
5wj2|Greaves of Mourning|u|n||||
5wno|Venomspew Gloves|c|n||||c^Tailoring^285^1297120^f
5wnp|Venomspew Cord|c|n||||c^Tailoring^290^1297121^f
5wnq|Venomspew Footpads|c|n||||c^Tailoring^295^1297122^f
5wnr|Swarmtender's Gloves|c|n||||c^Tailoring^285^1297123^f
5wns|Swarmtender's Cord|c|n||||c^Tailoring^290^1297124^f
5wnt|Swarmtender's Footpads|c|n||||c^Tailoring^295^1297125^f
5wnw|Bileblister Boots|c|n||||c^Leatherworking^295^1297128^f
5wnx|Hivethrasher's Claws|c|n||||c^Leatherworking^285^1297129^f
5wny|Hivethrasher's Girdle|c|n||||c^Leatherworking^290^1297130^f
5wnz|Hivethrasher's Boots|c|n||||c^Leatherworking^295^1297131^f
5wo0|Scalegut Clenchers|c|n||||c^Leatherworking^285^1297132^f
5wo1|Scalegut Belt|c|n||||c^Leatherworking^290^1297133^f
5wo2|Scalegut Treaders|c|n||||c^Leatherworking^295^1297134^f
5wo4|Broodwatcher's Belt|c|n||||c^Leatherworking^290^1297136^f
5wo5|Broodwatcher's Treaders|c|n||||c^Leatherworking^295^1297137^f
5wo6|Goregasher Grips|c|n||||c^Blacksmithing^285^1297138^f
5wo7|Goregasher Support|c|n||||c^Blacksmithing^290^1297139^f
5wo8|Goregasher Stompers|c|n||||c^Blacksmithing^295^1297140^f
5woa|Clutchlord's Support|c|n||||c^Blacksmithing^290^1297142^f
5wob|Clutchlord's Stompers|c|n||||c^Blacksmithing^295^1297143^f
5woe|Depleted Eye of Influence|u|n||||
5wow|Purified Gnarlybark Staff|u|n||||
5wpe|Whitemane's Plateau|u|n||||
5wpg|Summit Drape|u|n||||
5wpx|Stormwind Intelligence Seal|u|n||||
5wqa|Yaely's Mending Tool|u|n||||
5wqc|Glaive Thrower Muffler|u|n||||
5wqd|Copper Plated Pipe|u|n||||
5wqk|Ghansurok Hide Tunic|u|n||||
5wqn|Chimaera Wing Cape|u|n||||
5wqr|Rocket Pilot Gloves|u|n||||
5wrc|Horn of Ve'han|u|n||||
5wrd|Hermit's Pauldron|u|n||||
5wre|Jereman's Bauble|u|n||||
5wrf|Wild Wristguards|u|n||||
5wrg|Ring of Nature's Cycles|u|n||||
5wrh|Ketharas' Linked Belt|u|n||||
5wtv|Wool-Stitched Waistband|u|n||||
5wtz|Highfeather Bangle|u|n||||
5wu0|Crowfeather Tunic|u|n||||
5wu4|Acolyte Blade|u|n||||
5wu5|Felflick's Fire Flicker|u|n||||
5wuw|Putridus Wall|u|n||||
5wxs|Initiate's Signet of Ferocity|e|n|||LWatchersRing|r^2819^4^The Watchers^f
5wxt|Initiate's Signet of Brilliance|e|n|||LWatchersRing|r^2819^4^The Watchers^f
5wxu|Initiate's Signet of Resolve|e|n|||LWatchersRing|r^2819^4^The Watchers^f
5wxv|Initiate's Signet of Vigilance|e|n|||LWatchersRing|r^2819^4^The Watchers^f
5wxw|Tracker's Signet of Ferocity|e|n|||LWatchersRing|r^2819^5^The Watchers^f
5wxx|Tracker's Signet of Brilliance|e|n|||LWatchersRing|r^2819^5^The Watchers^f
5wxy|Tracker's Signet of Resolve|e|n|||LWatchersRing|r^2819^5^The Watchers^f
5wxz|Tracker's Signet of Vigilance|e|n|||LWatchersRing|r^2819^5^The Watchers^f
5wy0|Watcher's Signet of Ferocity|e|n|||LWatchersRing|r^2819^6^The Watchers^f
5wy1|Watcher's Signet of Brilliance|e|n|||LWatchersRing|r^2819^6^The Watchers^f
5wy3|Watcher's Signet of Resolve|e|n|||LWatchersRing|r^2819^6^The Watchers^f
5wy4|Watcher's Signet of Vigilance|e|n|||LWatchersRing|r^2819^6^The Watchers^f
5wy5|Warden's Signet of Ferocity|e|n|||LWatchersRing|r^2819^7^The Watchers^f
5wy6|Warden's Signet of Brilliance|e|n|||LWatchersRing|r^2819^7^The Watchers^f
5wy7|Warden's Signet of Resolve|e|n|||LWatchersRing|r^2819^7^The Watchers^f
5wy8|Warden's Signet of Vigilance|e|n|||LWatchersRing|r^2819^7^The Watchers^f
5x0l|Gravetoll Gavel|u|n||||
5x0n|The Black Helm|u|n||||
5x0o|Soulwoven Drape|u|n||||
5x0p|Band of the Damned|u|n||||
5x1i|Bladewind|q|sn||||q^95912^WANTED: Blademaster Kaijo^37^^s
5x1l|Scoutmaster's Eyepatch|u|n||||
5x3w|Eluvi'ana|u|nU||||
5x48|Crawler's Clackers|ev|sn||||V^255897^27439^^s~r^2827^4^Powderfuse^f
5x49|Misplaced Pantaloons|ev|sn||||V^255897^47136^^s~r^2827^4^Powderfuse^f
5x4a|Disengagement Ring|ev|sn||||V^255897^31544^^s~r^2827^4^Powderfuse^f
5x4b|Primitive Fishing Pole|ev|sn||||V^255897^118729^^s~r^2827^5^Powderfuse^f
5x4c|Thrash's Trash|ev|sn||||V^255897^61019^^s~r^2827^5^Powderfuse^f
5x6a|Surfer Shoes|u|n||||
5x7w|Abigail's Hope|u|n||||
5x7x|Sawyer Family Seal|u|n||||
5x7y|Hand-Hewn Buckler|u|n||||
5x7z|Polished Doomguard Edge|u|n||||
5x80|Yashiro's Spirit Bead|u|n||||
5x81|Thaelemaches' Talisman|u|n||||
5x83|Cured Staghide Leggings|u|n||||
5x84|Blademaster Hakama|u|n||||
5x85|Plaguecrusher Greaves|u|n||||
5x9m|Luxurious Smoking Jacket|u|n||||
5x9n|Grimm's Packing Gloves|d|n||||d^329^Ezra Grimm^0^0^c
5x9o|Ezra's Seal of Authenticity|d|n||||d^329^Ezra Grimm^0^0^c
5x9p|Hand of the Zealous|d|n||||d^329^Malor the Zealous^0^0^c
5x9q|Scarlet Malice|d|n||||d^329^^0^0^c
5x9r|Plate of the Scarlet Bastion|d|n||||d^329^^0^0^c
5x9v|Scarlet Bonebreaker|d|n||||d^329^^0^0^c
5x9w|Masterwork Crimson Hammer|d|n||||d^329^^0^0^c
5xab|Lightcrest Hammer|u|n||||
5xaq|Black Guard Skullcap|u|n||||
5xbc|Plague Defiled Buckler|d|n||||d^329^^0^0^c
5xg7|Coldflame Saber|u|n||||
5xhp|Militia Bow|q|sn|a|||q^91777^Rare Books^2^a^s
5xhq|Junior's Hunting Bow|q|sn|a|||q^46^Bounty on Murlocs^7^a^s
5xhy|Captain Sander's Lucky Shooter|u|sn||||
5xhz|Harvester's Pestslayer|q|sn|a|||q^9^The Killing Fields^10^a^s
5xio|Criminal's Pauldrons|q|sn|h|||q^549^WANTED: Syndicate Personnel^17^h^s
5xiq|Gnoll Shackles|q|sn|h|||q^442^Assault on Fenris Isle^19^h^s
5xir|Wise Gauntlets|q|sn|h|||q^451^A Recipe For Death^13^h^s
5xis|Trophy Belt|q|sn|h|||q^501^Elixir of Pain^21^h^s
5xiv|Glistening Stompers|q|sn|h|||q^515^Elixir of Agony^25^h^s
5xj0|Alcaz Willcrusher|u|n||||
5xj1|Grips of Control|u|n||||
5xj2|Wrex's Pinky Ring|u|n||||
5xj3|Tidesong Wand|u|n||||
5xj4|Seascale Bracers|u|n||||
5xj5|Cloak of the Tidemistress|u|n||||
5xj6|Katerina's Shanker|u|n||||
5xj7|Cutthroat Chestguard|u|n||||
5xj8|Sentimental Locket|u|n||||
5xj9|Defias Enforcer's Shoulderpads|u|n||||
5xja|Girdle of Extracted Answers|u|n||||
5xjb|Fingerbreaker Stamp|u|n||||
5xjc|Zarla's Snack Pouch|u|n||||
5xje|Defias Enforcer's Legguards|u|n||||
5xjm|Sunderbark Vigil|u|n||||
5xn1|Brewmancer Nightcap|u|n||||
5xn3|Backroom Bulwark|u|n||||
5xn8|Verek's Loyal Wraps|u|n||||
5xna|Chol'aruk's Trophy Sword|q|sn||||q^97005^Chol'aruk the Ravener^16^^s~q^97003^Chol'aruk the Ravener^16^^s
5xnb|Big Bad Basher|q|sn||||q^97005^Chol'aruk the Ravener^16^^s~q^97003^Chol'aruk the Ravener^16^^s
5xnc|Quilboar Toothpick|q|sn||||q^97005^Chol'aruk the Ravener^16^^s~q^97003^Chol'aruk the Ravener^16^^s
5xnd|Thornwoven Shield|q|sn||||q^97005^Chol'aruk the Ravener^16^^s~q^97003^Chol'aruk the Ravener^16^^s
5xnl|A Lesson in Destruction|u|n||||
5xnm|Salve and Salvation|Q|sn||||q^96800^Past Due^33^^s
5xnn|Knucklebound Thimble|Q|sn||||q^96800^Past Due^33^^s
5xno|Denric's Dog Tags|u|n||||
5xnp|Uncle's Heroism|u|n||||
5xnq|Youngster's First Bow|u|n||||
5xnr|Shimmerwine Shanker|q|sn||||q^96609^Quest 96609^47^^s
5xns|Shimmerwine Spirits|q|sn||||q^96609^Quest 96609^47^^s
5xq8|Cloudy Skyforged Chainmail|c|n||||c^Blacksmithing^60^1301421^f
5xq9|Cloudy Skyforged Wristguards|c|n||||c^Blacksmithing^50^1301422^f
5xqa|Cloudy Skyforged Gauntlets|c|n||||c^Blacksmithing^55^1301423^f
5xqb|Cloudy Skyforged Chain|c|n||||c^Blacksmithing^50^1301424^f
5xqc|Cloudy Skyforged Legguards|c|n||||c^Blacksmithing^60^1301425^f
5xqd|Cloudy Skyforged Greaves|c|n||||c^Blacksmithing^55^1301426^f
5xqe|Cloudy Gustwoven Harness|c|n||||c^Leatherworking^60^1301427^f
5xqf|Cloudy Gustwoven Bracers|c|n||||c^Leatherworking^50^1301428^f
5xqg|Cloudy Gustwoven Gloves|c|n||||c^Leatherworking^55^1301429^f
5xqh|Cloudy Gustwoven Belt|c|n||||c^Leatherworking^50^1301430^f
5xqi|Cloudy Gustwoven Trousers|c|n||||c^Leatherworking^60^1301431^f
5xqj|Cloudy Gustwoven Boots|c|n||||c^Leatherworking^55^1301432^f
5xqk|Cloudy Windraveled Jerkin|c|n||||c^Leatherworking^60^1301433^f
5xql|Cloudy Windraveled Armguards|c|n||||c^Leatherworking^50^1301434^f
5xqm|Cloudy Windraveled Mitts|c|n||||c^Leatherworking^55^1301435^f
5xqn|Cloudy Windraveled Strap|c|n||||c^Leatherworking^50^1301436^f
5xqo|Cloudy Windraveled Pants|c|n||||c^Leatherworking^60^1301437^f
5xqp|Cloudy Windraveled Footwraps|c|n||||c^Leatherworking^55^1301438^f
5xqq|Cloudy Stormsewn Vest|c|n||||c^Tailoring^60^1301439^f
5xqt|Cloudy Stormsewn Cord|c|n||||c^Tailoring^50^1301442^f
5xqu|Cloudy Stormsewn Leggings|c|n||||c^Tailoring^60^1301443^f
5xqw|Azure Skyforged Chainmail|c|n||||c^Blacksmithing^60^1301445^f
5xqx|Azure Skyforged Wristguards|c|n||||c^Blacksmithing^50^1301446^f
5xqy|Azure Skyforged Gauntlets|c|n||||c^Blacksmithing^55^1301447^f
5xqz|Azure Skyforged Chain|c|n||||c^Blacksmithing^50^1301448^f
5xr0|Azure Skyforged Legguards|c|n||||c^Blacksmithing^60^1301449^f
5xr1|Azure Skyforged Greaves|c|n||||c^Blacksmithing^55^1301450^f
5xr2|Azure Gustwoven Harness|c|n||||c^Leatherworking^60^1301451^f
5xr3|Azure Gustwoven Bracers|c|n||||c^Leatherworking^50^1301452^f
5xr4|Azure Gustwoven Gloves|c|n||||c^Leatherworking^55^1301453^f
5xr5|Azure Gustwoven Belt|c|n||||c^Leatherworking^50^1301454^f
5xr6|Azure Gustwoven Trousers|c|n||||c^Leatherworking^60^1301455^f
5xr7|Azure Gustwoven Boots|c|n||||c^Leatherworking^55^1301456^f
5xr8|Azure Windraveled Jerkin|c|n||||c^Leatherworking^60^1301457^f
5xr9|Azure Windraveled Armguards|c|n||||c^Leatherworking^50^1301458^f
5xra|Azure Windraveled Mitts|c|n||||c^Leatherworking^55^1301459^f
5xrd|Azure Windraveled Footwraps|c|n||||c^Leatherworking^55^1301462^f
5xrh|Azure Stormsewn Cord|c|n||||c^Tailoring^50^1301466^f
5xri|Azure Stormsewn Leggings|c|n||||c^Tailoring^60^1301468^f
5xrl|Cloudy Skyforged Pauldrons|c|n||||c^Blacksmithing^175^1301527^f
5xrm|Cloudy Gustwoven Hood|c|n||||c^Leatherworking^175^1301528^f
5xrn|Cloudy Gustwoven Spaulders|c|n||||c^Leatherworking^175^1301529^f
5xrp|Cloudy Windraveled Drapes|c|n||||c^Leatherworking^175^1301531^f
5xrr|Cloudy Stormsewn Epaulets|c|n||||c^Tailoring^175^1301533^f
5xrt|Azure Skyforged Pauldrons|c|n||||c^Blacksmithing^175^1301535^f
5xru|Azure Gustwoven Hood|c|n||||c^Leatherworking^175^1301536^f
5xrv|Azure Gustwoven Spaulders|c|n||||c^Leatherworking^175^1301537^f
5xrx|Azure Windraveled Drapes|c|n||||c^Leatherworking^175^1301539^f
5xrz|Azure Stormsewn Epaulets|c|n||||c^Tailoring^175^1301541^f
5xs0|Al'Aketh Chainmail|u|n||||
5xs1|Al'Aketh Wristguards|u|n||||
5xs2|Al'Aketh Gauntlets|u|n||||
5xs3|Al'Aketh Chain|u|n||||
5xs4|Al'Aketh Legguards|u|n||||
5xs5|Al'Aketh Greaves|u|n||||
5xs6|Al'Aketh Harness|u|n||||
5xs7|Al'Aketh Bracers|u|n||||
5xs8|Al'Aketh Gloves|u|n||||
5xs9|Al'Aketh Belt|u|n||||
5xsa|Al'Aketh Trousers|u|n||||
5xsb|Al'Aketh Boots|u|n||||
5xsc|Al'Aketh Jerkin|u|n||||
5xsd|Al'Aketh Armguards|u|n||||
5xse|Al'Aketh Mitts|u|n||||
5xsf|Al'Aketh Strap|u|n||||
5xsg|Al'Aketh Pants|u|n||||
5xsh|Al'Aketh Footwraps|u|n||||
5xsi|Al'Aketh Vestments|u|n||||
5xsk|Al'Aketh Handwraps|u|n||||
5xsl|Al'Aketh Cord|u|n||||
5xsm|Al'Aketh Leggings|u|n||||
5xsn|Al'Aketh Shoes|u|n||||
5xso|Zephrali Chainmail|v|sn||||V^271478^1009^^s
5xsp|Zephrali Wristguards|v|sn||||V^271478^506^^s
5xsq|Zephrali Gauntlets|v|sn||||V^271478^508^^s
5xsr|Zephrali Chain|v|sn||||V^271478^510^^s
5xss|Zephrali Legguards|v|sn||||V^271478^1024^^s
5xst|Zephrali Greaves|v|sn||||V^271478^775^^s
5xsu|Zephrali Harness|v|sn||||V^271483^860^^s
5xsv|Zephrali Bracers|v|sn||||V^271483^435^^s
5xsw|Zephrali Gloves|v|sn||||V^271483^437^^s
5xsx|Zephrali Belt|v|sn||||V^271483^438^^s
5xsy|Zephrali Trousers|v|sn||||V^271483^873^^s
5xsz|Zephrali Boots|v|sn||||V^271483^659^^s
5xt0|Zephrali Jerkin|v|sn||||V^271483^880^^s
5xt1|Zephrali Armguards|v|sn||||V^271483^445^^s
5xt2|Zephrali Mitts|v|sn||||V^271483^458^^s
5xt3|Zephrali Strap|v|sn||||V^271483^460^^s
5xt4|Zephrali Pants|v|sn||||V^271483^916^^s
5xt5|Zephrali Footwraps|v|sn||||V^271483^691^^s
5xt6|Zephrali Vest|v|sn||||V^271480^738^^s
5xt7|Zephrali Cuffs|v|sn||||V^271480^370^^s
5xt8|Zephrali Handwraps|v|sn||||V^271480^336^^s
5xt9|Zephrali Cord|v|sn||||V^271480^337^^s
5xta|Zephrali Leggings|v|sn||||V^271480^678^^s
5xtb|Zephrali Shoes|v|sn||||V^271480^510^^s
5xtc|Zephrali Greatsword|v|sn||||V^271465^2135^^s
5xte|Zephrali Smasher|v|sn||||V^271465^2151^^s
5xtf|Zephrali Bludgeon|v|sn||||V^271465^1727^^s
5xtg|Zephrali Knife|v|sn||||V^271465^1734^^s
5xth|Zephrali Greatstaff|v|sn||||V^271465^2176^^s
5xti|Zephrali Bow|v|sn||||V^271465^1345^^s
5xtj|Zephrali Crossbow|v|sn||||V^271465^1350^^s
5xtp|Savage Gladiator Shoulders|u|n||||
5xw2|Artifact Seeker's Pendant|u|n||||
5xw3|Scholarly Pendant|u|sn||||
5xw4|Erudite's Amulet|u|sn||||
5xw5|Cloak of the Divine Storm|u|n||||
5xw6|Brilliant Cloak|q|sn|a|||q^95534^Quest 95534^31^a^s
5xw7|Well-Weathered Cloak|q|sn||||q^78830^Terror of the Desert Skies^35^^s
5xw8|Determined Band|q|sn||||q^79242^No Honor Among Thieves^35^^s
5xw9|Ponderous Loop|q|sn||||q^78830^Terror of the Desert Skies^35^^s
5xwa|Pyrewood Signet Ring|q|sn||||q^78307^The Horn of Xelthos^^^s
5xwb|Dudd's Thinkin' Cap|q|sn||||q^95385^Quest 95385^38^^s
5xwc|Soulwoven Epaulets|u|n||||
5xwd|Dro'zem's Tunic|u|n||||
5xwe|Crusty Cuffs|q|sn||||q^97048^Returning to Port^33^^s
5xwf|Plain Handwraps|u|n||||
5xwg|Cross-Stitched Cord|u|n||||
5xwh|Patchy Pants|u|n||||
5xwi|Incinerator's Boots|q|sn|a|||q^95999^WANTED: Incinerator Gar'im^20^a^s
5xwj|Solomon's Comfortable Hat|u|n||||
5xwk|Shabby Spaulders|u|n||||
5xwl|Grimtotem Naturalist's Tunic|u|n||||
5xwm|War Painted Cuffs|u|n||||
5xwn|Traveled Gloves|q|sn||||q^79242^No Honor Among Thieves^35^^s
5xwo|Kurzen Headshrinker's Cinch|q|sn||||q^97048^Returning to Port^33^^s
5xwp|Feathered Leggings|u|n||||
5xwq|Disjointed Shoes|q|sn|a|||q^95999^WANTED: Incinerator Gar'im^20^a^s
5xwr|Magistrate's Chain Hood|u|n||||
5xwu|Grayscale Bracers|u|n||||
5xwv|Conductive Gauntlets|u|n||||
5xww|Jailer's Discarded Chain|q|sn||||q^97048^Returning to Port^33^^s
5xwx|Clinking Mail Legguards|u|n||||
5xwy|Alacritous Treads|q|sn|a|||q^95999^WANTED: Incinerator Gar'im^20^a^s
5xwz|Soldier's Visor|q|sn||||q^79242^No Honor Among Thieves^35^^s
5xx0|Pauldrons of Vindication|u|n||||
5xx1|Inspiring Chestplate|u|n||||
5xx2|Shimmering Bracers|u|n||||
5xx3|Bejeweled Punchers|u|n||||
5xx4|Gilded Plate Belt|u|n||||
5xx5|Double-Plated Legplates|u|n||||
5xx6|Silverrune Greaves|u|n||||
5xx7|Silverbane Slicer|u|n||||
5xx8|Guardian's Maulers|u|n||||
5xx9|Swampspine Crusher|u|n||||
5xxa|Ruby-Adorned Blade|u|n||||
5xxb|Mug of Muddled Memories|q|sn||||q^98545^Leonid's Letter^10^^s
5xxc|Notched Ritual Rib|u|n||||
5xxe|The Skullcracker|u|n||||
5xxh|Staff of Brutal Cunning|u|n||||
5xxi|Truthseeker's Bow|u|n||||
5xxj|Misplaced Shooter|q|sn||||q^98545^Leonid's Letter^10^^s
5xxk|Dudd's Second-Favorite Wand|q|sn||||q^95384^Quest 95384^35^^s
5xxl|Raven Hill Crest|u|n||||
5xxm|Crest of Elucidation|u|n||||
5xxn|Fermented Restoration Potion|u|n||||
5xxo|Researcher's Night Light|u|n||||
5xye|Encroacher's Claim|q|sn|h|||q^97250^Wrongly Blamed, Justly Corrected^18^h^s
5xyg|Pathfinder's Clearway|q|sn|h|||q^97250^Wrongly Blamed, Justly Corrected^18^h^s
5xyh|Traveler's Shawl|q|sn|h|||q^97250^Wrongly Blamed, Justly Corrected^18^h^s
5y4q|Aka'rai's Tattered Vestments|q|sn||||q^97265^Hate the Hatefury^28^^s
5y4r|Dagger of Deals|q|sn||||q^97265^Hate the Hatefury^28^^s
5y5z|Shen'dralar Relic|d|n||||d^429^^0^0^c
5y94|Rough Copper Chain Boots|c|n||||c^Blacksmithing^50^1302598^f
5yhn|Mauler's Mutton|u|n||||
5yho|Ogre Bone|u|n||||
5yhp|Souvenir Ogre Tooth|u|n||||
5yhw|Hoof-Holstered Blade|q|sn||||q^76240^Stalk With The Earthmother^6^^s
5yia|Valley Cosh|q|sn||||q^76240^Stalk With The Earthmother^6^^s
5yip|Refunded Ring|q|sn||||q^97332^Quest 97332^36^^s
5yiq|Renegotiated Ring|q|sn||||q^97332^Quest 97332^36^^s
5yir|Apology Ring|q|sn||||q^97332^Quest 97332^36^^s
5yml|Premier Grand Marshal's Tome of Restoration|v|sn|a|272686||V^12782^0^^s
5ymm|Premier Grand Marshal's Tome of Power|v|sn|a|272685||V^12782^0^^s
5yv8|Premier Grand Marshal's Barricade|v|sn|a|278469||V^12782^0^^s
5yv9|Premier High Warlord's Barricade|v||h|278468||V^14581^0^^s
5yxz|Stromgarde Hood|q|sn|a|||q^92867^Quest 92867^34^a^s
5zgu|Torch of Light|c|n||||c^Enchanting^300^1306520^f
5zh0|Elderwild Waistcord|c|n||||c^Leatherworking^300^1306526^f
5zh1|Outlaw's Collar|c|n||||c^Leatherworking^300^1306527^f
5zh2|Elderwild Pants|c|n||||c^Leatherworking^300^1306528^f
5zh3|Eternity Pauldrons|c|n||||c^Leatherworking^300^1306529^f
5zh4|Tranquil Wristguards|c|n||||c^Leatherworking^300^1306530^f
5zh5|Mourning Handguards|c|n||||c^Leatherworking^300^1306531^f
5zh7|Ironwood Blade|c|n||||c^Blacksmithing^300^1306533^f
5zh8|Forest Defender's Axe|c|n||||c^Blacksmithing^300^1306534^f
5zh9|Greenhammer|c|n||||c^Blacksmithing^300^1306535^f
5zha|Evergreen Shield|c|n||||c^Blacksmithing^300^1306536^f
5zhb|Depleted Thorium Sabatons|c|n||||c^Blacksmithing^300^1306537^f
5zhc|Heavy Thorium Gauntlets|c|n||||c^Blacksmithing^300^1306538^f
5zhd|Azerothium Legplates|c|n||||c^Blacksmithing^300^1306539^f
5zhe|Robes of Fiery Devastation|c|n||||c^Tailoring^300^1306540^f
5zhf|Mana-infused Cord|c|n||||c^Tailoring^300^1306541^f
5zhg|Rime-encrusted Boots|c|n||||c^Tailoring^300^1306542^f
5zhh|Fel Cape|c|n||||c^Tailoring^300^1306543^f
5zhi|Cloak of Earth and Sky|c|n||||c^Tailoring^300^1306544^f
5zhl|Hyper Deluxe Sniper Rifle Mk XVII|c|n||||c^Engineering^300^1306547^f
5zks|Brewer's Bracers|q|sn|a|||q^98071^Brewer's Trade^22^a^s
5zkv|Taurajo Headband|q|sn|h|||q^98093^Field to Clear^18^h^s
5zkw|Glimmer|u|n||||
5zkx|Frostfall|u|n||||
5zmg|Bloodsplattered Bandana|u|n||||
5zn5|Makeshift Belt|u|n||||
5zn6|Dustwallow Dirk|u|n||||
5znc|Bigger Rock on Bigger Stick|q|sn||||q^94982^Quest 94982^40^^s
5zww|Kor'kron Battle Gauntlets|u|n||||
5zwx|Theramore Defender's Gauntlets|u|n||||
5zwy|Marshdweller's Pants|u|n||||
5zx1|Naga Scale Spaulders|u|n||||
5zx3|Fatebound Buckler|u|n||||
5zx5|Courier's Clasp|u|n||||
5zx7|Vine Pruner's Cloak|Q|sn|a|||q^92456^A Green Sample^28^a^s
5zx8|Thorn Protecting Girdle|Q|sn|a|||q^92456^A Green Sample^28^a^s
5zx9|Fallen Guard's Pendant|Q|sn||||q^92457^Starving Arcane^28^^s
5zxa|Arcane Infused Rod|Q|sn||||q^92457^Starving Arcane^28^^s
5zxb|Spellguard Pauldrons|Q|sn||||q^92458^Heart of Disruption^28^^s
5zxc|Renewing Footpads|Q|sn||||q^92458^Heart of Disruption^28^^s
5zxd|Defender of Dalaran|Q|sn||||q^92458^Heart of Disruption^28^^s
5zxe|Battle Spaulders|Q|sn|h|||q^96984^Heart of Disruption^28^h^s
5zxf|Enchanted Sandals|Q|sn|h|||q^96984^Heart of Disruption^28^h^s
5zxg|Striking Staff|Q|sn|h|||q^96984^Heart of Disruption^28^h^s
5zxh|Solid Gold Band|Q|sn||||q^96987^Opportunistic Education^28^^s
5zxi|Larcenist's Belt|Q|sn||||q^96987^Opportunistic Education^28^^s
5zxj|Unstable Power Core|Q|sn|h|||q^96988^Source of Power^28^h^s
5zxk|Construct Cloak|Q|sn|h|||q^96988^Source of Power^28^h^s
5zxl|Runebound Gloves|Q|sn|a|||q^92489^Power Overwhelming^28^a^s
5zxm|Curio-Adorned Necklace|q|sn||||q^94998^Quest 94998^37^^s
5zxo|Rock on Stick|q|sn||||q^94982^Quest 94982^40^^s
5zxp|Stick No Rock|q|sn||||q^94982^Quest 94982^40^^s
5zxq|Twilight Initiate's Belt|q|sn||||q^94984^Quest 94984^39^^s
5zxr|Torn Cultist Cloak|q|sn||||q^94984^Quest 94984^39^^s
5zxt|Kroog's Backscratcher|u|n||||
5zxv|Indoctrinated Choker|u|n||||
5zxw|Convert's Bindings|u|n||||
5zxz|Black Horn Necklace|w|sn||||m^262716^NPC 262716^0^s
5zy0|Monstrous Cleaver|Qq|sn||||q^97290^Unending Torment^16^h^s~q^95250^Abominable Creatures^16^^s
5zy1|Grave Shroud|Qq|sn||||q^97290^Unending Torment^16^h^s~q^95250^Abominable Creatures^16^^s
5zy3|Slain Baron's Signet|Qq|sn||||q^97290^Unending Torment^16^h^s~q^95250^Abominable Creatures^16^^s
5zy4|Duty Bound Leggings|Q|sn|a|||q^95195^Bloodied Insignia^17^a^s
5zy5|Remembrance Armor|Q|sn|a|||q^95195^Bloodied Insignia^17^a^s
5zy6|Tarnished Locket|q|sn|a|||q^95161^Remember That I Love You^17^a^s
5zya|The Stitcher|Q|sn||||q^92421^Light's Justice^17^^s
5zyb|Spare Part Bindings|Q|sn||||q^92421^Light's Justice^17^^s
5zyc|Plaguefang|Q|sn||||q^95216^The New Plague^17^^s
5zyd|Blight Gloves|Q|sn||||q^95216^The New Plague^17^^s
5zye|Apprentice Sorcerer's Slacks|u|n||||
5zyf|Rune-Etched Epaulets|u|n||||
5zyg|Ancient Voodoo Pouch|u|n||||
5zyh|Intrepid Explorer's Chainmail|u|n||||
5zyi|Rusted Troll War Belt|q|sn||||q^95789^Shady Saltseers^35^^s
5zyj|Mutinous Cuffs|q|sn||||q^95791^The Saltseer Captain^35^^s
5zyk|South Seas Shroud|q|sn||||q^95791^The Saltseer Captain^35^^s
5zyl|Ceremonial Mallet|q|sn|h|||q^96078^A Tale Spun Around the Fire^35^h^s
5zym|Sacrificial Sword|q|sn|h|||q^96078^A Tale Spun Around the Fire^35^h^s
5zyn|I'lalai Flayer|q|sn|h|||q^96078^A Tale Spun Around the Fire^35^h^s
5zyo|Tidesoaked Leggings|q|sn|h|||q^95776^The Only Good Brinescale...^33^h^s
5zyp|Naga Priestess's Mantle|q|sn|h|||q^95776^The Only Good Brinescale...^33^h^s
5zyr|Guidance of Ursoc|u|n||||
5zys|Wisdom of Ursol|u|n||||
5zyt|Nama's Cherished Necklace|u|n||||
5zyu|Calibrated Blunderbuss|Q|sn|a|||q^96393^Old Ironforge Incursion^11^a^s
5zyv|Ironforge Greathammer|Q|sn|a|||q^96393^Old Ironforge Incursion^11^a^s
5zyw|Deepblaze|Q|sn|a|||q^96393^Old Ironforge Incursion^11^a^s
5zyx|Dusty Belt|Q|sn||||q^96394^The Restless Dead^10^^s
5zyy|Dwarven Tome|Q|sn||||q^96403^Important Heirlooms^10^^s
5zyz|Catacomb Cloak|Q|sn||||q^96395^An Ancient Grudge^10^^s
5zz0|Deepgrave Trousers|Q|sn||||q^96395^An Ancient Grudge^10^^s
5zz1|Expeditionary Legplates|u|n||||
5zz2|Reinforced Muck Protectors|u|n||||
5zz3|Diemetradon Scale Spaulders|u|n||||
5zz4|Crystalline Pauldrons|u|n||||
5zz8|Crystal-Infused Cleaver|u|n||||
5zza|Beastslayer's Trident|u|n||||
5zzc|Faintly Glowing Orb|u|n||||
5zzu|Saltseer's Helm|q|sn||||q^95789^Shady Saltseers^35^^s
5zzv|Lost Researcher's Hood|u|n||||
5zzw|Slime-Resistant Shroud|u|n||||
6022|Gargantuan Wristguards|u|n||||
6023|Deeproar Cord|u|n||||
6024|Talon of Tor'Rel|u|n||||
6025|Frostfang Mail Vest|u|n||||
6026|Raptorscale Bulwark|u|n||||
6027|Venomvessel Ring|u|n||||
602a|Hammer of Thundering Hooves|u|n||||
602b|Dinofrill Casque|u|n||||
602c|Deep Jungle Rifle|u|n||||
602d|Tooth of the Matriarch|u|n||||
602e|Scaleguard Scimitar|u|n||||
602f|Nanaya's Control Spire|u|n||||
602g|Legplates of Reinforced Crystal|u|n||||
602h|Leggings of Curation|u|n||||
602i|Albinofur Grips|u|n||||
602j|Crownroar Chestplate|u|n||||
602k|Heartflame Gauntlets|u|n||||
602l|Cinderedge Crescent|u|n||||
602n|Sparklance Wand|u|n||||
6031|Regal Direhorn Drape|u|n||||
603c|Flameslash Crescent|u|n||||
603d|Robes of Dark Summons|u|n||||
603e|Impish Chain Hood|u|n||||
603f|Tuskblade Halberd|u|n||||
603g|Lucky Shovelnose Tuft|d|n||||d^329^^0^0^c
603h|Spike Crested Bracers|d|n||||d^329^^0^0^c
603j|Bloodfur Bulwark|d|n||||d^329^^0^0^c
603k|Withering Grips|d|n||||d^329^^0^0^c
603l|Behemoth Bones|d|n||||d^329^^0^0^c
603m|Trousers of the Ebon Giant|d|n||||d^329^^0^0^c
603n|Blackmaw Chain Belt|d|n||||d^329^^0^0^c
603o|Bloody Claws of Attack|d|n||||d^329^^0^0^c
603q|Veilpiercer Girdle|d|n||||d^329^^0^0^c
603s|Cowl of Dark Ambition|d|n||||d^329^^0^0^c
603t|Burnished Pridescales|d|n||||d^329^^0^0^c
603u|Scalding Flamehoof|d|n||||d^329^^0^0^c
603w|Horns of Varrox|d|n||||d^329^^0^0^c
603x|Fist of Revelation|u|n||||
603y|Apprentice's Protective Treads|u|n||||
6040|Claymore of Two Moons|u|n||||
6041|Sad-Sack Sandals|u|n||||
6042|Staff of Sorrow|u|n||||
6043|Truesight Rifle|u|n||||
6044|Furbolg Rib Protector|u|n||||
6045|Tunnelweb Pincer|u|n||||
6046|Octofinger Gauntlets|u|n||||
604f|Cryptwalker Bracers|Q|sn||||q^96394^The Restless Dead^10^^s
604g|Tomb Robber's Gloves|Q|sn||||q^96403^Important Heirlooms^10^^s
60a8|Invisible Dagger|u|n||||
60ik|Rage of the Storm|q|sn||||q^96016^The Tempest's Weapons^35^^s
60il|Tidebringer's Claw|q|sn||||q^96016^The Tempest's Weapons^35^^s
60in|Lightning's Grasp|q|sn||||q^96016^The Tempest's Weapons^35^^s
60l4|Elementalist's Guard|q|sn||||q^96016^The Tempest's Weapons^35^^s
60o5|Serrated Raptor Claw|Q|sn|h|||q^95697^Changing Tastes^26^h^s
610i|Forest Oracle's Cloak|q|sn|a|||q^940^Teldrassil^6^a^s
610j|Courier's Wristguards|q|sn|a|||q^86574^Quest 86574^19^a^s
610k|Harpy Claw Ring|q|sn|h|||q^86576^Bloodfury Trinkets^21^h^s
610l|Mountaineer's Greataxe|q|sn|a|||q^86585^Banner of the Fallen^12^a^s
610m|Invader's Mace|q|sn|a|||q^86585^Banner of the Fallen^12^a^s
610o|Repurposed Hair Band|q|sn|a|||q^86614^Silver of the Waves^15^a^s
610p|Daggerfang's Daggerfang|q|sn|a|||q^86758^Quest 86758^11^a^s
610q|Essene's Hope|u|n||||
610r|Stonard Stompers|u|n||||
610s|Ancestral Waistcord|u|n||||
610t|Crystal-flecked Cord|u|n||||
610v|Wicked Lich's Finger|u|n||||
610w|Ghastly Bow|u|n||||
610x|Roadwatcher's Confidence|q|sn|h|||q^95981^Watching the Roads^15^h^s
610y|Furred Belt|q|sn|h|||q^96130^Chakuyak^1^h^s
610z|Raptorscale Pants|q|sn|h|||q^97223^Bloodtalon Matriarch^5^h^s
6110|Depleted Ritual Band|q|sn|h|||q^97225^Forgotten Loa Idols^4^h^s
6112|Thra's Friendship Bracelet|q|sn||||q^97326^Rocks to Rests^10^^s
6113|Puk's Friendship Bracelet|q|sn||||q^97326^Rocks to Rests^10^^s
6114|Brog's Friendship Bracelet|q|sn||||q^97326^Rocks to Rests^10^^s
6115|Migi's Friendship Bracelet|q|sn||||q^97326^Rocks to Rests^10^^s
6116|Makeshift Stormcaller|q|sn||||q^97282^Stormy Potential^5^^s
6117|Mantle of Scaleslaying|u|n||||
6118|Pauldrons of Scaleslaying|u|n||||
6119|Shoulders of Scaleslaying|u|n||||
611a|Shoulderplates of Scaleslaying|u|n||||
611f|Patchwing Pants|q|sn|h|||q^97558^Hides for the Forsaken^6^h^s
611g|Howlhide Vest|q|sn|h|||q^97558^Hides for the Forsaken^6^h^s
611h|Finscale Soles|q|sn|h|||q^97558^Hides for the Forsaken^6^h^s
611i|High Order Pendant|u|n||||
611j|Windshaper Pendant|u|n||||
611l|Swordfeather Cloak|q|sn|a|||q^98025^WANTED: Jai'vhanel^8^a^s
611m|Replica Crescent Necklace|q|sn|a|||q^98027^Gleaming Crescent Necklace^21^a^s
611n|Mathystra Channeling Orb|q|sn|a|||q^98028^Quest 98028^16^a^s
611o|Onu's Patience|q|sn|a|||q^98028^Quest 98028^16^a^s
611p|Weathered Deathstalker's Blade|q|sn||||q^98095^Valuable Vantages^20^^s
611q|Expended Apothecary Vial|q|sn||||q^98095^Valuable Vantages^20^^s
611r|Pelt Pants|q|sn|a|||q^98156^Packaged Pristine Pelts^24^a^s
611s|Knight's Lance|q|sn|a|||q^98191^A Friend of the Family^20^a^s
611t|Royal Dagger|q|sn|a|||q^98191^A Friend of the Family^20^a^s
611u|Ti'ik's Tattered Trousers|u|n||||
611v|Profane Ritual Robes|u|n||||
611x|Sacrificial Shackles|u|n||||
611y|Whelpscale Necklace|u|n||||
611z|Bleached Scale Vest|u|n||||
6120|Prospector's Signet|q|sn|a|||q^98216^Understanding Our Present^26^a^s
6121|Excavation Cloak|q|sn|a|||q^98216^Understanding Our Present^26^a^s
6122|Flamescarred Spellbook|q|sn|a|||q^98223^Old Habits^26^a^s
6123|Dragonmaw Buckler|q|sn|a|||q^98223^Old Habits^26^a^s
6125|Razormaw Shorts|q|sn|a|||q^98283^Carnage^25^a^s
6126|Carnage Trousers|q|sn|a|||q^98283^Carnage^25^a^s
6128|Fallen Dragon's Scepter|q|sn||||q^98297^Stopping the Cycle^29^^s
6129|Trusty Sword|q|sn||||q^98297^Stopping the Cycle^29^^s
612a|Subdued Dragon's Fang|q|sn||||q^98297^Stopping the Cycle^29^^s
612b|Foulfur Gloves|u|n||||
612c|Glimmerchain Trousers|u|n||||
612d|Redstone Boots|u|n||||
612e|Bouquet of Auberdine Flowers|q|sn||||q^98208^Bloom of the Heavens^24^^s
612f|Golem War Cloak|q|sn|a|||q^98310^Gleaning Our Future^27^a^s
612g|Rune-Etched Ring|q|sn|a|||q^98310^Gleaning Our Future^27^a^s
612h|Giantstone Medallion|q|sn|a|||q^98310^Gleaning Our Future^27^a^s
612i|Frosthowl's Footwarmers|q|sn|a|||q^98326^Frosthowl^4^a^s
612j|Spirit-buckle Belt|u|n||||
612k|Sailing Tunic|u|n||||
618i|Matriarch's Mantle|u|n||||
618j|Bear Fur Cowl|u|n||||
619u|Elderwild Construction Hammer|u|n||||
619v|Greatflank Flayer|u|n||||
619w|Nature's Cull|u|n||||
61a6|Rusthowl's Worn Collar|u|n||||
61a7|Ragged Colors|u|n||||
61a8|Wail of Death|u|n||||
61b0|Blade of Bandarion|u|n||||
61b6|Field Researcher's Loop|u|sn||||
61b7|Philanthropist's Ring|u|sn||||
61b8|Museum Keeper's Chain|u|n||||
61b9|Antique Bulwark|u|n||||
61bk|Gul'gash's Greathammer|u|n||||
61bm|Dragonscale Buckler|u|n||||
61bt|Corrupted Riverglades Pendant|u|n||||
61bw|Iron Star|q|sn||||q^79980^Scramble^19^^s
61bx|Well-Worn Pitchfork|u|n||||
61c1|Twilight Forgehammer|u|n||||
61c2|Robes of the Blind Cultist|u|n||||
61c9|Loop of Sacrifice|q|sn||||q^95885^The Offering of Blood^18^^s
61cb|Lakeshire Firefighter's Headband|u|n||||
61cc|Rog'mar Trainee Shoulderpads|u|n||||
61cl|Restored Cloth Helm|u|n||||
61cm|Restored Cloth Shoulders|u|n||||
61cn|Restored Cloth Vest|u|n||||
61co|Restored Cloth Bracers|u|n||||
61cp|Restored Cloth Handwraps|u|n||||
61cq|Restored Cloth Belt|u|n||||
61cr|Restored Cloth Pants|u|n||||
61ct|Restored Leather Hood|u|n||||
61cu|Restored Leather Spaulders|u|n||||
61cw|Restored Leather Wristcuffs|u|n||||
61cx|Restored Leather Gloves|u|n||||
61cy|Restored Leather Strap|u|n||||
61cz|Restored Leather Chaps|u|n||||
61d0|Restored Leather Boots|u|n||||
61d1|Restored Mail Coif|u|n||||
61d2|Restored Mail Shoulderguards|u|n||||
61d3|Restored Mail Chestpiece|u|n||||
61d4|Restored Mail Wristguards|u|n||||
61d5|Restored Mail Clasps|u|n||||
61d6|Restored Mail Belt|u|n||||
61d7|Restored Mail Legguards|u|n||||
61d8|Restored Mail Boots|u|n||||
61dh|Restored Cloak|u|n||||
61dk|Restored Chopper|u|n||||
61dl|Restored Cleaver|u|n||||
61dm|Restored Dagger|u|n||||
61dn|Restored Basher|u|n||||
61do|Restored Smasher|u|n||||
61ds|Restored Shortsword|u|n||||
61dv|Restored Buckler|u|n||||
61dw|Restored Bow|u|n||||
61dx|Restored Wand|u|n||||
61ea|Kurmokk's Pelt|u|n||||
61ee|Murloc Oracle's Dagger|u|n||||
61ib|Fishscale Hauberk|u|n||||
61ig|Surveyor's Gloves|u|n||||
61j9|Whelpfire Wand|R|sn||||R^14272^Snarlflare^0^s
61ja|Bound Bracers|u|n||||
61jb|Boulderheart Band|u|n||||
61l5|Gnoll Hide Boots|u|n||||
61lg|Flesheater's Scales|u|n||||
61lh|Saltwater Shawl|u|n||||
61lj|Emerald Watcher's Dreamstaff|u|n||||
61lk|Wyrmak's Cuirass|u|n||||
61ll|Ravaged Leather Leggings|u|n||||
61lm|Tusk of Grunter|u|nU||||
61lo|Corsepickers|u|n||||
61lq|Twisted Shadow Staff|u|n||||
61lv|Braided Seer Stones|u|n||||
61lw|Stonegaze Wand|u|n||||
61lx|Dreadscorn's Spaulders|u|n||||
61lz|Clack's Claw|u|n||||
61m3|Scales of the Devourer|u|n||||
61mo|Ragged Dark Iron Cuffs|u|n||||
61mp|Deathmaw's Guise|u|n||||
61n4|Tim's Lost Rib|q|sn||||q^98545^Leonid's Letter^10^^s
61nb|Shin Slicers|u|n||||
61ne|Ogre Sorcerer Belt|u|n||||
61nk|Flame Seared Signet|u|n||||
61np|Dragonblood Greatsword|u|n||||
61ns|Heart of Smoldar|u|n||||
61ny|Blackheart's Vest|u|n||||
61o1|Unbreakable Golem Grips|u|n||||
61t7|Malignant Root|u|sn||||
61t8|Webwood Slicer|q|sn|a|||q^98403^Twisted Hatred^7^a^s
620m|Combat Tuning Wrench|u|n||||
620n|Golem Fist|R|snr||||R^2751^War Golem^0^s
620r|Shadowforge Shield|u|n||||
620s|Groundshaker's Bindings|u|n||||
620t|Broken Tooth's Flayed Hide|u|n||||
620u|Firebird's Cowl|u|n||||
620w|Earth-Infused Rockguards|u|n||||
620x|Siegebreaker's Blaster|u|n||||
6214|Fireflare Handwraps|u|n||||
622v|Xorothian Footwraps|u|n||||
622x|Mastrogonde's Sinister Gown|u|n||||
6230|Silkspun Gloves|u|n||||
6233|Emogg's "Crusher"|u|n||||
6236|Feather-Stitched Moccasins|u|n||||
623h|Dissolved Locket|u|n||||
623i|Gnawed Bone|u|nU||||
623j|Bog Pickers|u|n||||
623m|Dragonmaw Battle Shroud|u|n||||
624u|Molok's Masher|u|n||||
624v|Needletooth's Needletooth|u|nr||||
624w|Shadow Council Apprentice's Mantle|u|n||||
624x|Ruul's Secondstone|u|n||||
624y|Rotting Meat|u|n||||
6252|Dun Garok Rifle|u|sn||||
6253|Naga Maiden's Gown|u|n||||
6255|Bloodstained Pants|u|n||||
6258|Imbued Scaled Cuffs|u|n||||
6259|Durable Bearhide Pauldrons|R|sn||||R^14280^Big Samras^0^s
625d|Gnoll Shaman's Staff|u|n||||
62k5|Denmother's Hide|u|n||||
62k6|Heart of Alterac|u|n||||
62k7|Syndicate Executioner's Slicer|u|n||||
62kb|Bearhide Vicegrips|u|sn||||
62n5|Gorefang's Runners|u|n||||
62pw|Decaying Flesh Belt|R|sn||||R^271080^NPC 271080^0^s
62py|Bayne's Bite|u|n||||
62q7|Fellicent's Bindings|u|n||||
62q9|Batwing Bindings|u|n||||
62qg|Cracked Carapace Hauberk|u|n||||
62s9|Moonchaser's Headdress|u|n||||
6360|Cliff Jumpers|u|n||||
6361|Ironback Signet|u|n||||
6363|Dissolved Link Legguards|u|n||||
6366|Witherheart's Stabber|u|n||||
636l|Berserker's Wraps|u|n||||
636n|Witherbark Hatecleaver|u|n||||
636o|Cliffbreaker's Pauldrons|u|n||||
636p|Crown of Maldazzar|u|n||||
636q|Husk of the Husk|u|n||||
636r|Rusted Family Memento|u|n||||
636u|Dreadwhisper's Touch|u|n||||
6373|High Clerist's Seal|u|n||||
637a|Scarlet Executioner's Guise|u|n||||
637f|Scarlet Forgemaster's Bindings|u|n||||
637l|Everstaring Abomination Eye|u|n||||
637o|Horseman's Unyielding Shroud|u|n||||
637p|Blade of Senseless Slaughter|u|n||||
637q|Signet of the Soulless Rider|u|n||||
637s|Cultist's Cuffs|u|n||||
637t|Wildhammer Soldier's Spaulders|u|n||||
6396|Unmovable Sabatons|u|n||||
6399|Ranger Lord's Longsword|u|n||||
639a|Mossflayer Warlord's Girdle|u|n||||
639d|Treads of Rotting Flesh|u|n||||
639h|Duskstalker's Hide|u|n||||
639i|Gnarlpine War Staff|u|sn||||
639j|Blackmoss Robes|u|n||||
639p|Impcaster's Staff|u|n||||
639q|Serrated Shadowclaw|u|n||||
639t|Sinslayer's Smasher|R|sn||||R^7017^Lord Sinslayer^0^s
63a1|Greymist Gauntlets|u|n||||
63a3|Crazed Firecaller's Cloak|u|n||||
63a8|Furbolg Loincloth|u|n||||
63a9|Moongazer's Wand|u|nr||||
63ad|Hide of Mongress|u|n||||
63af|Death Howl's Guise|u|n||||
63av|Ancient Lichen Vestments|u|n||||
63ay|Slime-Coated Gloves|u|n||||
63b8|Vial of Vile Liquid|u|n||||
63ba|Rage Paw|u|n||||
63bx|Eternally Frozen Band|u|nU||||
63c1|Icesworn Decapitator|u|n||||
63c5|Magically Fortified Legguards|u|n||||
63c6|Howling Hide|u|n||||
63cq|Queen Guard's Royal Seal|u|n||||
63cr|Horn of Antilos|u|n||||
63ct|Feardred's Gauntlets|u|n||||
63cu|Battleguard Captain's Sticker|u|n||||
63cv|Felweaver's Staff|R|sn||||R^5822^Felweaver Scornn^0^s
63ds|Flayed Scorpid Bands|u|n||||
63dt|Centaur Raider's Axe|u|n||||
63du|Invading Marine's Shield|u|n||||
63dv|Geolord's Mitts|u|n||||
63ex|Venture Company Legguards|u|sn||||
63fi|Budding Leaf Belt|u|n||||
63fj|Faerie Dragon's Skin|u|n||||
63fm|Whipfang's Skinsearer|u|n||||
63fz|Seared Grove Shoulderpads|u|n||||
63g0|Foreman's Helm|u|n||||
63g1|Sorrow's Shroud|u|n||||
63g3|Shapeshifting Sentinel's Strides|u|n||||
63hn|Dendweller's Hammer|u|n||||
63kt|Ursol'lok's Paws|u|n||||
63ku|Snapped Branch Wand|u|n||||
63l7|Ankle Slicers|u|n||||
63nf|Flame Seared Sword|u|n||||
63ng|Apothecary's Concoction|u|n||||
63o8|Carved Furbolg Tooth|u|n||||
63o9|Arcane Charged Robes|u|n||||
63ob|Still Water Band|u|n||||
63oc|Den Guardian's Crusher|u|n||||
63oe|Slimy Sword|u|n||||
63og|Frostbitten Staff|u|n||||
63oj|Basilisk Sinew Belt|u|n||||
63ok|Demonstrike Emblem|u|n||||
63oo|Hyena Hide Helm|u|n||||
63op|Accursed Legguards|u|n||||
63or|First Mate Band|dw|sn||||d^36^Mr. Smite^4.76^0^s~m^646^Mr. Smite^0^s
63os|Band of the Better Half|u|n||||
63ot|Royal Satyr Slicer|u|n||||
63sb|Sturdy Bearhide Legguards|u|n||||
63sf|Hippogryph Down Leggings|u|n||||
63sg|Diamond Studded Belt|u|n||||
63si|Naga Caster's Staff|u|n||||
63sr|Silithid Sinew Crossbow|u|n||||
63sy|Windserpent Scaled Cloak|u|n||||
63xv|Snarling Fang|u|n||||
63xz|Yeti Hide Stompers|u|n||||
63yf|Black Brood Battleguards|u|n||||
63yi|Ooze Rummagers|u|n||||
63z4|Ooze Dripping Robes|u|n||||
63z5|Swamp Roamer's Band|u|n||||
63z9|Ripscaled Cuffs|u|n||||
63zb|Twitching Eye|u|n||||
63zg|Serrated Raptor Teeth|u|n||||
63zh|Rot-Fused Greaves|u|n||||
63zi|Darkmist Dirk|u|n||||
63zj|Marsh Serpent's Scales|u|n||||
641l|Nature's Sting Legguards|u|n||||
641y|Wyvern Heart Band|u|n||||
641z|Banished Centaur's Pauldrons|u|n||||
6420|Kobold Firestarter|u|n||||
642k|Foulmountain Family Hammer|u|n||||
6430|Mystmane's Pelt|u|n||||
6438|Worn Ranger's Dagger|u|n||||
643a|Chipped Spellstaff|u|n||||
643b|Explorer's Shortsword|R|sn||||R^255887^NPC 255887^0^s
643p|Skyseer's Gloves|u|n||||
643q|Scout Ranger's Gloves|u|n|h|||
643r|Thendal Watcher's Gloves|R|sn||||R^259398^NPC 259398^0^s
6440|Skyseer's Slippers|u|n||||
6444|Scout Ranger's Boots|u|n|h|||
6445|Thendal Watcher's Boots|u|n||||
6448|Skyseer's Belt|u|n||||
6449|Scout Ranger's Belt|u|n|h|||
644a|Thendal Watcher's Belt|u|n||||
644f|Cracked Blacksmith Hammer|c|n||||c^Blacksmithing^110^1317962^f
644s|Dull Sawblade|dw|sn||||d^36^Sneed^38.1^0^s~m^642^Sneed's Shredder^0^s
645s|Taurenbane's Family Cleaver|u|n||||
645t|Raptor Hide Cloak|u|n||||
645u|Signet of the Zhevra|R|sn||||R^5831^Swiftmane^0^s
645v|Mark of the Pack Leader|u|n||||
645w|Puncturing Spear|u|n||||
6462|Kodohide Legguards|R|sn||||R^5827^Brontus^0^s
6463|Centaur War Chain|R|sn||||R^5841^Rocklance^0^s
6468|Guard Captain's Barrier|R|sn||||R^5851^Captain Gerogg Hammertoe^0^s
6469|Feather Padded Treads|u|n||||
646a|Alliance Outrunner's Sword|u|sn||||
646b|Alliance Outrunner Bow|u|n||||
646c|Alliance Outrunner Healing Rod|R|sn||||R^5799^Hannah Bladeleaf^0^s
646e|Alliance Outrunner Staff|u|n||||
646f|Foreman's Enforcers|u|n||||
64zs|Sword of Mourning|u|n||||
650a|Honorbound Cloak|q||h|286427||q^93739^Exploring the Horde^8^h^s
650b|Cloak of the Honored Guest|q|sn|a|286426||q^93963^Exploring the Alliance^8^a^s
650c|Band of Bossman|w|sn||||m^264773^NPC 264773^0^s
650d|Big-Belly Belt|w|sn||||m^264773^NPC 264773^0^s
650e|Toofbreaker|u|n||||
6539|Cheetah Hide Grips|u|n||||
653a|Silithid Piercer|R|sn||||R^3253^Silithid Harvester^0^s
653b|Sludge-Stained Band|u|n||||
653c|Heckler's Hide|R|sn||||R^5829^Snort the Heckler^0^s
653d|Thunderstomp's Horn|R|snr||||R^5832^Thunderstomp^0^s
653g|The Skyblade|u|n||||
653h|Bael'dun Tankard|u|n||||
653s|Sandcaster's Mantle|u|n||||
653u|Warleader's Signet|u|n||||
653w|Winds of Tanaris|u|n||||
6549|Firebird Leggings|u|n||||
654a|Silithid Flesh Bindings|u|n||||
654b|Silithid Hauberk|u|n||||
654c|Ogre Casting Cloak|u|n||||
654u|Silithid Queen's Husk|u|n||||
6551|Calm Air Band|u|nU||||
655g|Sand-Covered Silk Sash|u|n||||
655h|King Mosh's Tooth|u|n||||
655k|Matriarch's Prowlers|u|n||||
655m|Clutchmother's Guards|u|n||||
655n|Big Basher's Belt|u|n||||
6567|Ambassador's Bloodrobes|u|n||||
6568|High Priestess's Kilt|u|n||||
656e|Gill's Gills|w|sn||||m^264177^NPC 264177^0^s
656h|Tidebound Dagger|u|n||||
656i|Pyromancer's Baton|u|n||||
656j|Flamestarter's Signet|w|sn||||m^260468^NPC 260468^0^s
656q|Umbral Scaled Belt|u|n||||
656u|Deep-Dweller's Grips|u|n||||
658o|Kolkar Hammer|q|sn|h|||q^99123^Lost in the Shadows^3^h^s
658p|Kolkar Bow|q|sn|h|||q^99123^Lost in the Shadows^3^h^s
658q|Pristine Orcish Dagger|q|sn|h|||q^99052^Threat from Below^10^h^s
658r|Aggor's Refitted Belt|q|sn|h|||q^99052^Threat from Below^10^h^s
6590|Proud Brave's Guard|q|sn|h|||q^99082^The High Chieftain^6^h^s
6591|Centaur Skull Basher|q|sn|h|||q^99082^The High Chieftain^6^h^s
6592|Riptear's Cleaver|q|sn|h|||q^99156^Rear Guard Patrol^8^h^s
6593|Riptear's Spare Arm|q|sn|h|||q^99156^Rear Guard Patrol^8^h^s
6594|Thrice-Stitched Flesh|q|sn|h|||q^99156^Rear Guard Patrol^8^h^s
6595|Furlfeather Ring|R|sn||||R^276194^Dustwind Eggtender^0^s
6596|Shal'ma's Shawl|R|sn||||R^276198^NPC 276198^0^s
6598|Bristlebark Bow|u|n||||
6599|Wrathroot|u|n||||
659a|Wisesight Wand|u|n||||
659b|Ghostfang's Steps|u|n||||
659c|Igleggings|u|n||||
659d|Snarlsnout Shooter|u|n||||
659e|Ukta's Conduit|u|n||||
659f|Helm Splitter|u|n||||
65fl|Sword of the Fallen|d|sn||||d^2999^Bjork^20^0^s~d^2999^Viktor the Vile^10^0^s
65fm|Rotmender's Garb|d|sn||||d^2999^Witherfang^20^0^s~d^2999^The Abandoned^10^0^s
65fn|Rotmender's Gloves|d|sn||||d^2999^Witherfang^20^0^s~d^2999^Viktor the Vile^10^0^s
65fo|Rotmender's Sash|d|sn||||d^2999^The Abandoned^10^0^s~d^2999^Bjork^10^0^s
65fp|Death Bindings|d|sn||||d^2999^Viktor the Vile^10^0^s
65fq|Unearthed Barrier|u|n||||
65fr|Ancient Cleaver|u|n||||
65fs|Mark of the Marsh|u|n||||
65ft|Thicket Bindings|u|n||||
65fu|Abandoned Leggings|u|n||||
65fv|Violet Sorcerer's Sandals|w|sn||||m^255072^NPC 255072^0^s
65fw|Violet Sorcerer's Leggings|d|n||||d^2959^^0^0^c
65fx|Violet Sorcerer's Wraps|d|sn||||d^2959^Arcane Anomaly^14.29^0^s
65fy|Arcane Remnant Leggings|d|n||||d^2959^^0^0^c
65fz|Roused Nature Footwraps|d|n||||d^2959^^0^0^c
65g0|Construct's Grips|w|sn||||m^246664^NPC 246664^0^s
65g1|Suffused Bindings|d|n||||d^2959^^0^0^c
65g2|Tattered Kirin Tor Cloak|d|sn||||d^2959^^0^0^c
65g3|Guardian's Emblem|d|sn||||d^2959^^0^0^s
65g4|City Guard's Tarnished Blade|d|sn||||d^2959^^0^0^s
65g5|Depth-Risen Leggings|d|sn||||d^2959^^0^0^c
65g6|Deep Flora Bindings|d|sn||||d^2959^^0^0^c
65g7|Deathcrawler's Chest|d|n||||d^2959^^0^0^c
65g8|Skin-Flayed Footguards|d|n||||d^2959^^0^0^c
65g9|Waterlogged Shoulderpads|u|n||||
65ga|Risen Sentry's Links|d|n||||d^2959^^0^0^c
65gb|Corroded Handguards|d|n||||d^2959^^0^0^c
65gc|Touch of the Depths|d|n||||d^2959^^0^0^c
65ge|Resurged Axe|u|n||||
65gf|Stretched Footpads|u|n||||
65gg|Ogre Magi's Mantle|u|n||||
65gh|Twilight Enforcer's Legs|w|sn||||m^258042^NPC 258042^0^s
65gi|Outrider's Gloves|u|n||||
65gj|Guise of Battle|u|n||||
65gk|Krol'dok Warplate Gauntlets|w|sn||||m^258042^NPC 258042^0^s
65gl|Krol'dok Warplate Legplates|u|n||||
65gm|Krol'dok Warplate Pauldrons|u|sn||||
65gn|Supreme Smasher|u|n||||
65go|Shadow-Seer Orb|u|n||||
65gp|Chaplain's Mitre|u|n||||
65gq|Compound Gloves|u|n||||
65gr|Defias Enforcer's Mask|u|n||||
65gs|Defias Enforcer's Chest|u|n||||
65gt|Defias Enforcer's Prowlers|u|n||||
65gu|Spaulders of Containment|u|n||||
65gv|Iron-Wrought Cuffs|u|n||||
65gw|Mark of Captivity|u|n||||
65gx|Enchantresses' Spire|u|n||||
65gy|Escape Plan|u|n||||
65h0|Tormented Cuffs|u|n||||
65h1|Nature Guardian's Legguards|u|n||||
65h2|Blackmaw Bindings|u|n||||
65h3|Spearfisher's Waders|u|n||||
65h4|Den Champion's Binding|u|n||||
65h5|Furbolg Berserker's Boots|u|n||||
65h6|Grove Subjugator's Blade|u|n||||
65h7|Demon Worshipper's Necklace|u|n||||
65h8|Satyr's Touch|u|n||||
65h9|Shaper's Robe|u|n||||
65ha|Naturopathy Footpads|u|n||||
65hb|Tattered Explorer's Cuffs|u|n||||
65hc|Dinosaur Hide Belt|u|n||||
65hd|Time-Forgotten Bindings|u|n||||
65he|Pauldrons of the Stone Guardian|u|n||||
65hf|Predaceous Band|u|n||||
65hg|Predator's Shroud|u|n||||
65hh|Ancient Mattock|u|n||||
65hi|Pylon Poker|u|n||||
65hv|Footman's Pocketknife|q|sn|a|||q^11^Riverpaw Gnoll Bounty^6^a^s
65hx|Cheese Knife|q|sn|a|||q^224^In Defense of the King's Lands^10^a^s
65hy|Darnassian Knife|q|sn|a|||q^98025^WANTED: Jai'vhanel^8^a^s
65hz|Serrated Knife|v|sn||||V^257422^3612^^s
65i0|Beastculler's Knife|q|sn|h|||q^98093^Field to Clear^18^h^s
65i2|Wizlo's Tuning Wrench|q|sn|h|||q^5151^Hypercapacitor Gizmo^25^h^s
65i3|Dragonmaw Skinflayer|q|sn|a|||q^474^Defeat Nek'rosh^27^a^s
65i4|Excavated Dagger|u|n||||
65i5|Yeti Skinner|q|sn|a|||q^565^Bartolo's Yeti Fur Cloak^29^a^s
65i6|Skypierce Javelin|u|n||||
65i7|Goblin Switchblade|q|sn||||q^600^Venture Company Mining^36^^s
65i8|Bladewhisper's Namesake|q|sn||||q^95912^WANTED: Blademaster Kaijo^37^^s
65i9|Orwin's Axe|u|n||||]==]
ns.gfVendor = {[225]="Gavin Gnarltree^1431^73.7^48.9",[228]="Avette Fellwood^1431^73.1^44.6",[1243]="Hegnar Rumbleshot^1426^40.8^65.1",[1289]="Gunther Weller^1453^64^68.8",[1309]="Wynne Larson^1453^52.1^83.6",[2482]="Zarena Cromwind^1434^28.4^75.4",[2840]="Kizz Bluntstrike^1434^28.3^75.2",[2849]="Qixdi Goodstitch^1434^28.2^77.5",[3096]="Captured Servant of Azora^1433^69.2^79.5",[3134]="Kzixx^1431^81.9^19.9",[3160]="Huklah^1411^40.6^67.9",[3161]="Rarc^1411^40.5^67.9",[3166]="Cutac^1411^53.2^40.9",[3167]="Wuark^1411^51.9^41.2",[3180]="Dark Iron Entrepreneur^1437^46.6^18.2",[3315]="Tor'phan^1454^62.6^50.4",[3316]="Handor^1454^62.8^44.8",[3359]="Kiro^1454^73^42.1",[3491]="Ironzar^1413^62.2^37.5",[3493]="Grazlix^1413^62.2^38.4",[3534]="Wallace the Blind^1421^43.8^84.5",[3536]="Kris Legace^1424^80^38.7",[3537]="Zixil^1424^52^39.2",[3658]="Lizzarik^1413^54.3^32.8",[3683]="Kiknikle^1413^41.8^38.6",[3684]="Pizznukle^1413^41.8^38.6",[3952]="Aeolynn^1440^34.5^49.6",[3953]="Tandaan Lightmane^1440^34.5^49.8",[4085]="Nizzik^1442^62.8^40.2",[4086]="Veenix^1442^58.3^51.7",[4164]="Cylania^1457^59.1^45.8",[4187]="Harlon Thornguard^1439^37.1^41.3",[4240]="Caynrus^1457^56.9^76.1",[4884]="Zulrg^1445^36.2^31.7",[4890]="Piter Verance^1445^67.4^47.9",[5122]="Skolmin Goldfury^1455^71.7^66.1",[5816]="Katis^1454^44.4^48.6",[7976]="Thalgus Thunderfist^1455^61.4^89.1",[8129]="Wrinkle Goodsteel^1446^50.8^27.7",[9179]="Jazzrik^1418^42.5^52.7",[11555]="Gorn One Eye^1448^65.2^2.7",[11874]="Masat T'andr^1435^26.5^31.5",[12023]="Kharedon^1450^56.6^29.8",[12024]="Meliri^1450^51.2^42.3",[12245]="Vendor-Tron 1000^1443^60.4^38.1",[12777]="Captain Dirgehammer^1453^75.9^67",[12781]="Master Sergeant Biggins^1453^75.2^67.2",[12782]="Captain O'Neal^1453^74.4^67.7",[12792]="Lady Palanseer^1454^37.2^64.7",[12793]="Brave Stonehide^1454^36.6^65.9",[12799]="Sergeant Ba'sha^1454^41.5^68.6",[12805]="Officer Areyn^1453^76.8^65.9",[13217]="Thanthaldis Snowgleam^1416^39.5^81.7",[13219]="Jekyll Flandring^1416^62.8^59.3",[14581]="Sergeant Thunderhorn^1454^36.9^67.1",[14753]="Illiyana Moonblaze^1440^61.5^83.8",[14754]="Kelm Hargunth^1413^46.7^8.4",[14828]="Gelvas Grimegate^1429^41.5^69",[14846]="Lhara^1429^41.3^69.8",[15126]="Rutherford Twing^1417^73.4^29.7",[15127]="Samuel Hawke^1417^46^45.4",[28989]="Aemara^1416^17.2^71.4",[227853]="Pix Xizzix^1434^28.5^75.8",[251364]="Destin Thriceforged^2521^43.4^23.6",[251365]="Jolee Brightmeadows^2521^43.5^23.6",[251965]="Fevrath Skyhammer^2521^43.4^23.5",[251980]="Rueben Lauren^1416^15.9^65.2",[251981]="Sheddle Glossgleam^1416^16.5^65.5",[251997]="Norvin Alderman^1416^16^65.5",[252000]="Brammold Deepmine^1416^15.9^68.7",[255897]="Friz Frazzlespark^2548^77.1^52.9",[256507]="Belann Windwood^2521^62.9^77.4",[257422]="Railee Thriceforged^2521^58.9^75.4",[260566]="Fizzix Boomshot^2548^78.6^53.6",[263569]="NPC 263569^1413^63.4^58.7",[263570]="Creeg Bothunk^1413^65^34.6",[265574]="Winklespark^1413^62.5^37.6",[265575]="Gezzy Gunkgear^1434^28.4^74.8",[265576]="Rettrick^1446^51.7^28.8",[271465]="Falfaan Halfwind^2521^59.4^75.8",[271478]="Elaria Anvilwind^2521^59.6^76.1",[271480]="Taliaa Brightsky^2521^59.3^76.2",[271483]="Ergaan Eastwind^2521^59.6^75.9",[272435]="Goren Grayfellow^2548^37.8^76.1",[275623]="Valaden Silverblade^1416^14.7^71.3",[275625]="Bartram Haller^1416^14.7^71.2"}
ns.gfExtra = {[6473]="s38:2,5:2",[10410]="s38:2,5:2",[10411]="s38:2,5:2",[10412]="s38:2,5:2",[10413]="s38:2,5:2",[11726]="s32:0.17,38:3.33",[11728]="s32:0.17,38:3.33",[11729]="s32:0.17,38:3.33",[11730]="s32:0.17,38:3.33",[11731]="s32:0.17,38:3.33",[12939]="s38:25",[12940]="s38:25",[13388]="s31:0.2,45:4.6",[13389]="s31:0.2,45:4.6",[13390]="s31:0.2,45:4.6",[13391]="s31:0.2,45:4.6",[13392]="s31:0.2,45:4.6",[14612]="s38:2",[14614]="s38:2",[14615]="s38:2",[14616]="s38:2",[14620]="s12:0.6",[14621]="s12:0.6",[14622]="s12:0.6",[14623]="s12:0.6",[14624]="s12:0.6",[14626]="s45:4.6",[14629]="s45:4.6",[14631]="s45:4.6",[14632]="s45:4.6",[14633]="s45:4.6",[14636]="s31:0.4,38:2",[14637]="s31:0.4,38:2",[14638]="s31:0.4,38:2",[14640]="s31:0.4,38:2",[14641]="s31:0.4,38:2",[15045]="s43:1",[15046]="s43:1",[15048]="s45:9.33",[15049]="s45:9.33",[15050]="s31:0.33",[15051]="s31:0.33",[15052]="s31:0.33",[15062]="s31:1",[15063]="s31:1",[15066]="s45:10",[15067]="s45:10",[19682]="s32:0.67",[19683]="s32:0.67",[19684]="s32:0.67",[19689]="s32:0.5",[19690]="s43:4",[19691]="s43:4",[19692]="s43:4",[19693]="s12:6.67",[19694]="s12:6.67",[19695]="s12:6.67",[20041]="s7:1.67",[20042]="s7:1.67",[20043]="s7:1.67",[20044]="s32:0.33,7:1.67",[20045]="s7:1.67",[20046]="s32:0.33,7:1.67",[20047]="s32:0.33,7:1.67",[20048]="s7:1.67",[20049]="s7:1.67",[20050]="s7:1.67",[20051]="s32:0.33,7:1.67",[20052]="s7:1.67",[20053]="s32:0.33,7:1.67",[20054]="s32:0.33,7:1.67",[20055]="s7:1.67",[20057]="s7:1.67",[20058]="s7:1.67",[20059]="s7:1.67",[20060]="s32:0.33,7:1.67",[20061]="s32:0.33,7:1.67",[20150]="s7:1.67",[20154]="s7:1.67",[20158]="s7:1.67",[20159]="s32:0.33,7:1.67",[20163]="s32:0.33,7:1.67",[20167]="s32:0.33,7:1.67",[20171]="s32:0.33,7:1.67",[20175]="s32:0.33,7:1.67",[20176]="s32:0.33,7:1.67",[20177]="s7:1.67",[20181]="s7:1.67",[20184]="s7:1.67",[20186]="s7:1.67",[20190]="s7:1.67",[20194]="s7:1.67",[20195]="s32:0.33,7:1.67",[20199]="s32:0.33,7:1.67",[20204]="s7:1.67",[20208]="s7:1.67",[20212]="s7:1.67",[20295]="s45:9.33",[20296]="s43:1",[22301]="s45:2.88,armor:25",[22302]="s45:2.88,armor:25",[22303]="s45:2.88,armor:25",[22304]="s45:2.88,armor:25",[22305]="s45:2.88,armor:25",[22306]="s45:2.88,armor:25",[22311]="s45:2.88,armor:25",[22313]="s45:2.88,armor:25",[22843]="s3:3.33,7:3.33",[22855]="s45:3.83,7:3.33",[22856]="s38:6.67,7:3.33",[22857]="s38:6.67,7:3.33",[22858]="s38:6.67,7:3.33",[22862]="s3:3.33,7:3.33",[22864]="s38:6.67,7:3.33",[22865]="s45:3.83,7:3.33",[22867]="s38:6.67,7:3.33",[22868]="s38:6.67,7:3.33",[22872]="s38:6.67,7:3.33",[22873]="s38:6.67,7:3.33",[22874]="s3:3.33,7:3.33",[22875]="s3:3.33,7:3.33",[22876]="s38:6.67,7:3.33",[22879]="s38:6.67,7:3.33",[22880]="s38:6.67,7:3.33",[22881]="s45:3.83,7:3.33",[22884]="s45:3.83,7:3.33",[22887]="s38:6.67,7:3.33",[23243]="s38:6.67,7:3.33",[23244]="s38:6.67,7:3.33",[23251]="s3:3.33,7:3.33",[23252]="s3:3.33,7:3.33",[23255]="s45:3.83,7:3.33",[23256]="s45:3.83,7:3.33",[23257]="s38:6.67,7:3.33",[23258]="s38:6.67,7:3.33",[23259]="s38:6.67,7:3.33",[23260]="s38:6.67,7:3.33",[23272]="s45:3.83,7:3.33",[23273]="s45:3.83,7:3.33",[23274]="s45:3.83,7:3.33",[23275]="s45:3.83,7:3.33",[23276]="s45:3.83,7:3.33",[23277]="s45:3.83,7:3.33",[23278]="s3:3.33,7:3.33",[23279]="s3:3.33,7:3.33",[23282]="s45:3.83,7:3.33",[23283]="s45:3.83,7:3.33",[23284]="s38:6.67,7:3.33",[23285]="s38:6.67,7:3.33",[23286]="s38:6.67,7:3.33",[23287]="s38:6.67,7:3.33",[23292]="s3:3.33,7:3.33",[23293]="s3:3.33,7:3.33",[23296]="s45:3.83,7:3.33",[23297]="s45:3.83,7:3.33",[23298]="s38:6.67,7:3.33",[23299]="s38:6.67,7:3.33",[23300]="s38:6.67,7:3.33",[23301]="s38:6.67,7:3.33",[23306]="s3:3.33,7:3.33",[23307]="s3:3.33,7:3.33",[23310]="s45:3.83,7:3.33",[23311]="s45:3.83,7:3.33",[23312]="s38:6.67,7:3.33",[23313]="s38:6.67,7:3.33",[23314]="s38:6.67,7:3.33",[23315]="s38:6.67,7:3.33",[220840]="s41:5.5,7:2.5",[220846]="s45:3,7:2.5",[220860]="s38:5,7:2.5",[220861]="s38:5,7:2.5",[227081]="s38:6.67,7:3.33",[227087]="s38:6.67,7:3.33",[227133]="s45:3.83,7:3.33",[227139]="s45:3.83,7:3.33",[227152]="s41:7.33,7:3.33",[227164]="s45:3.83,7:3.33",[227170]="s41:7.33,7:3.33",[227187]="s45:3.83,7:3.33",[227198]="s41:7.33,7:3.33",[231569]="s38:6.67,7:3.33",[231575]="s3:3.33,7:3.33",[231578]="s3:3.33,7:3.33",[231613]="s45:3.83,7:3.33",[231617]="s45:3.83,7:3.33",[231623]="s7:3.33",[231633]="s7:3.33",[231650]="s38:6.67,7:3.33",[231656]="s38:6.67,7:3.33",[231661]="s45:3.83,7:3.33",[231676]="s7:3.33",[231688]="s38:6.67,7:3.33",[231694]="s38:6.67,7:3.33",[231700]="s45:3.83,7:3.33",[271207]="s5:2",[271214]="s5:2",[272453]="s45:3.83,7:3.33",[272455]="s45:3.83,7:3.33",[272457]="s45:3.83,7:3.33",[272458]="s45:3.83,7:3.33",[272459]="s45:3.83,7:3.33",[272462]="s38:6.67,7:3.33",[272464]="s7:3.33",[272467]="s38:6.67,7:3.33",[272469]="s38:6.67,7:3.33",[272470]="s38:6.67,7:3.33",[272471]="s38:6.67,7:3.33",[272472]="s38:6.67,7:3.33",[272473]="s38:6.67,7:3.33",[272474]="s38:6.67,7:3.33",[272475]="s38:6.67,7:3.33",[272476]="s38:6.67,7:3.33",[272477]="s38:6.67,7:3.33",[272478]="s38:6.67,7:3.33",[272479]="s38:6.67,7:3.33",[272480]="s38:6.67,7:3.33",[272481]="s38:6.67,7:3.33",[272484]="s45:3.83,7:3.33",[272485]="s38:6.67,7:3.33",[272486]="s45:3.83,7:3.33",[272487]="s45:3.83,7:3.33",[272488]="s38:6.67,7:3.33",[272489]="s38:6.67,7:3.33",[272490]="s3:3.33,7:3.33",[272491]="s3:3.33,7:3.33",[272492]="s3:3.33,7:3.33",[272495]="s3:3.33,7:3.33",[272496]="s3:3.33,7:3.33",[272498]="s45:3.83,7:3.33",[272499]="s45:3.83,7:3.33",[272500]="s45:3.83,7:3.33",[272501]="s45:3.83,7:3.33",[272504]="s45:3.83,7:3.33",[272505]="s45:3.83,7:3.33",[272506]="s38:6.67,7:3.33",[272507]="s38:6.67,7:3.33",[272508]="s38:6.67,7:3.33",[272509]="s38:6.67,7:3.33",[272510]="s38:6.67,7:3.33",[272513]="s38:6.67,7:3.33",[272514]="s38:6.67,7:3.33",[272515]="s38:6.67,7:3.33",[272516]="s38:6.67,7:3.33",[272517]="s38:6.67,7:3.33",[272519]="s38:6.67,7:3.33",[272520]="s38:6.67,7:3.33",[272523]="s38:6.67,7:3.33",[272525]="s38:6.67,7:3.33",[272526]="s38:6.67,7:3.33",[272527]="s38:6.67,7:3.33",[272528]="s38:6.67,7:3.33",[272529]="s38:6.67,7:3.33",[272530]="s3:3.33,7:3.33",[272531]="s3:3.33,7:3.33",[272532]="s3:3.33,7:3.33",[272533]="s3:3.33,7:3.33",[272534]="s3:3.33,7:3.33",[272536]="s3:3.33,7:3.33",[272538]="s38:6.67,7:3.33",[272539]="s38:6.67,7:3.33",[272542]="s38:6.67,7:3.33",[272543]="s38:6.67,7:3.33",[272544]="s38:6.67,7:3.33",[272545]="s38:6.67,7:3.33",[272548]="s45:3.83,7:3.33",[272549]="s45:3.83,7:3.33",[272552]="s45:3.83,7:3.33",[272553]="s45:3.83,7:3.33",[272554]="s45:3.83,7:3.33",[272556]="s45:3.83,7:3.33",[272558]="s45:3.83,7:3.33",[272559]="s45:3.83,7:3.33",[272560]="s45:3.83,7:3.33",[272561]="s45:3.83,7:3.33",[272562]="s45:3.83,7:3.33",[272563]="s45:3.83,7:3.33",[272564]="s45:3.83,7:3.33",[272565]="s45:3.83,7:3.33",[272568]="s45:3.83,7:3.33",[272569]="s45:3.83,7:3.33",[272570]="s45:3.83,7:3.33",[272572]="s45:3.83,7:3.33",[272574]="s45:3.83,7:3.33",[272575]="s45:3.83,7:3.33",[272576]="s45:3.83,7:3.33",[272577]="s45:3.83,7:3.33",[272606]="s7:3.33",[272608]="s38:6.67,7:3.33",[272609]="s38:6.67,7:3.33",[272611]="s7:3.33",[272614]="s38:6.67,7:3.33",[272617]="s45:3.83,7:3.33",[272619]="s7:3.33",[272625]="s38:6.67,7:3.33",[272626]="s7:3.33",[272627]="s7:3.33",[272630]="s45:3.83,7:3.33",[272634]="s7:3.33",[272636]="s45:3.83,7:3.33",[272637]="s38:6.67,7:3.33",[272640]="s3:3.33,7:3.33",[272641]="s7:3.33",[272642]="s7:3.33",[272643]="s45:3.83,7:3.33",[272647]="s38:6.67,7:3.33",[272648]="s45:3.83,7:3.33",[272649]="s7:3.33",[272650]="s7:3.33",[272656]="s45:3.83,7:3.33",[272657]="s45:3.83,7:3.33",[272663]="s7:3.33",[272669]="s45:3.83,7:3.33",[272670]="s45:3.83,7:3.33",[272671]="s45:3.83,7:3.33",[272677]="s7:3.33",[272678]="s7:3.33",[272680]="s45:3.83,7:3.33",[272701]="s45:3.83,7:3.33",[272703]="s45:3.83,7:3.33",[272704]="s38:6.67,7:3.33",[272705]="s38:6.67,7:3.33",[272708]="s38:6.67,7:3.33",[272709]="s38:6.67,7:3.33",[272713]="s3:3.33,7:3.33",[272715]="s3:3.33,7:3.33",[272716]="s38:6.67,7:3.33",[272717]="s38:6.67,7:3.33",[272718]="s45:3.83,7:3.33",[272719]="s45:3.83,7:3.33",[272722]="s45:3.83,7:3.33",[272723]="s45:3.83,7:3.33",[272724]="s45:3.83,7:3.33",[272725]="s45:3.83,7:3.33",[272726]="s38:6.67,7:3.33",[272727]="s38:6.67,7:3.33",[272728]="s38:6.67,7:3.33",[272729]="s38:6.67,7:3.33",[272731]="s38:6.67,7:3.33",[272732]="s38:6.67,7:3.33",[272733]="s38:6.67,7:3.33",[272735]="s3:3.33,7:3.33",[272736]="s3:3.33,7:3.33",[272737]="s3:3.33,7:3.33",[272738]="s38:6.67,7:3.33",[272739]="s38:6.67,7:3.33",[272740]="s38:6.67,7:3.33",[272741]="s38:6.67,7:3.33",[272742]="s45:3.83,7:3.33",[272743]="s45:3.83,7:3.33",[272744]="s45:3.83,7:3.33",[272745]="s45:3.83,7:3.33",[272746]="s45:3.83,7:3.33",[272749]="s45:3.83,7:3.33",[272750]="s45:3.83,7:3.33",[272751]="s45:3.83,7:3.33",[272752]="s45:3.83,7:3.33",[272753]="s45:3.83,7:3.33",[272755]="s38:6.67,7:3.33",[272757]="s38:6.67,7:3.33",[272758]="s38:6.67,7:3.33",[272759]="s38:6.67,7:3.33",[272760]="s38:6.67,7:3.33",[272761]="s38:6.67,7:3.33",[272762]="s38:6.67,7:3.33",[272763]="s38:6.67,7:3.33",[272764]="s38:6.67,7:3.33",[272765]="s38:6.67,7:3.33",[272766]="s38:6.67,7:3.33",[272768]="s38:6.67,7:3.33",[272771]="s3:3.33,7:3.33",[272772]="s3:3.33,7:3.33",[272774]="s3:3.33,7:3.33",[272775]="s3:3.33,7:3.33",[272776]="s3:3.33,7:3.33",[272777]="s3:3.33,7:3.33",[272780]="s45:3.83,7:3.33",[272781]="s45:3.83,7:3.33",[272782]="s45:3.83,7:3.33",[272783]="s45:3.83,7:3.33",[272784]="s45:3.83,7:3.33",[272785]="s45:3.83,7:3.33",[272786]="s38:6.67,7:3.33",[272787]="s38:6.67,7:3.33",[272788]="s38:6.67,7:3.33",[272789]="s38:6.67,7:3.33",[272792]="s38:6.67,7:3.33",[272793]="s38:6.67,7:3.33",[272794]="s45:3.83,7:3.33",[272796]="s45:3.83,7:3.33",[272800]="s45:3.83,7:3.33",[272801]="s45:3.83,7:3.33",[272802]="s45:3.83,7:3.33",[272803]="s45:3.83,7:3.33",[272804]="s45:3.83,7:3.33",[272805]="s45:3.83,7:3.33",[272807]="s45:3.83,7:3.33",[272808]="s45:3.83,7:3.33",[272810]="s45:3.83,7:3.33",[272812]="s45:3.83,7:3.33",[272814]="s45:3.83,7:3.33",[272815]="s45:3.83,7:3.33",[272816]="s45:3.83,7:3.33",[272817]="s45:3.83,7:3.33",[272818]="s45:3.83,7:3.33",[272819]="s45:3.83,7:3.33",[272820]="s45:3.83,7:3.33",[272821]="s45:3.83,7:3.33",[272823]="s45:3.83,7:3.33",[272824]="s45:3.83,7:3.33",[272852]="s7:3.33",[272853]="s7:3.33",[272854]="s7:3.33",[272855]="s7:3.33",[273044]="s6:2",[273051]="s6:2",[273329]="s7:3.33",[273330]="s7:3.33",[273331]="s7:3.33",[273332]="s7:3.33",[273333]="s7:3.33",[273334]="s7:3.33",[273336]="s45:3.83,7:3.33",[273337]="s45:3.83,7:3.33",[273340]="s45:3.83,7:3.33",[273341]="s45:3.83,7:3.33",[273342]="s45:3.83,7:3.33",[273343]="s45:3.83,7:3.33",[273344]="s7:3.33",[273345]="s7:3.33",[273348]="s7:3.33",[273349]="s7:3.33",[273350]="s7:3.33",[273351]="s7:3.33",[273355]="s7:3.33",[273356]="s7:3.33",[273357]="s7:3.33",[273358]="s7:3.33",[273359]="s7:3.33",[273360]="s7:3.33",[273363]="s7:3.33",[273365]="s7:3.33",[273368]="s45:3.83,7:3.33",[273370]="s45:3.83,7:3.33",[273371]="s45:3.83,7:3.33",[273373]="s7:3.33",[273374]="s7:3.33",[273375]="s7:3.33",[273380]="s7:3.33",[273382]="s45:3.83,7:3.33",[273383]="s45:3.83,7:3.33",[273384]="s45:3.83,7:3.33",[273385]="s45:3.83,7:3.33",[273386]="s45:3.83,7:3.33",[273387]="s45:3.83,7:3.33",[273391]="s45:3.83,7:3.33",[273392]="s45:3.83,7:3.33",[273393]="s45:3.83,7:3.33",[273394]="s45:3.83,7:3.33",[273395]="s45:3.83,7:3.33",[273396]="s45:3.83,7:3.33",[273399]="s7:3.33",[273400]="s7:3.33",[273401]="s7:3.33",[273402]="s7:3.33",[273403]="s7:3.33",[273404]="s7:3.33",[273405]="s45:3.83,7:3.33",[273406]="s45:3.83,7:3.33",[273407]="s45:3.83,7:3.33",[273408]="s45:3.83,7:3.33",[273410]="s45:3.83,7:3.33",[273411]="s45:3.83,7:3.33",[273413]="s7:3.33",[273414]="s7:3.33",[273415]="s7:3.33",[273416]="s7:3.33",[273418]="s7:3.33",[273419]="s7:3.33",[273421]="s7:3.33",[273422]="s7:3.33",[273423]="s7:3.33",[273424]="s7:3.33",[273426]="s7:3.33",[273427]="s7:3.33",[273429]="s7:3.33",[273431]="s7:3.33",[273433]="s7:3.33",[273434]="s7:3.33",[273435]="s7:3.33",[273436]="s7:3.33",[273443]="s7:3.33",[273445]="s7:3.33",[273447]="s7:3.33",[273448]="s7:3.33",[274176]="s45:3.83,7:3.33",[274177]="s38:6.67,7:3.33",[274178]="s45:3.83,7:3.33",[274179]="s45:3.83,7:3.33",[274180]="s38:6.67,7:3.33",[274181]="s38:6.67,7:3.33",[274183]="s38:6.67,7:3.33",[274184]="s38:6.67,7:3.33",[274187]="s38:6.67,7:3.33",[274188]="s38:6.67,7:3.33",[274189]="s38:6.67,7:3.33",[274190]="s38:6.67,7:3.33",[274192]="s38:6.67,7:3.33",[274193]="s45:3.83,7:3.33",[274194]="s38:6.67,7:3.33",[274195]="s45:3.83,7:3.33",[274196]="s38:6.67,7:3.33",[274197]="s45:3.83,7:3.33",[274198]="s45:3.83,7:3.33",[274199]="s45:3.83,7:3.33",[274202]="s45:3.83,7:3.33",[274203]="s45:3.83,7:3.33",[274204]="s45:3.83,7:3.33",[274205]="s45:3.83,7:3.33",[274206]="s7:3.33",[274207]="s7:3.33",[274210]="s7:3.33",[274211]="s7:3.33",[274212]="s7:3.33",[274213]="s7:3.33",[274217]="s7:3.33",[274218]="s7:3.33",[274219]="s7:3.33",[274220]="s7:3.33",[274221]="s7:3.33",[274222]="s7:3.33",[274226]="s45:3.83,7:3.33",[274227]="s45:3.83,7:3.33",[274230]="s45:3.83,7:3.33",[274232]="s45:3.83,7:3.33",[274233]="s45:3.83,7:3.33",[274236]="s45:3.83,7:3.33",[274237]="s45:3.83,7:3.33",[274238]="s45:3.83,7:3.33",[274239]="s45:3.83,7:3.33",[274240]="s45:3.83,7:3.33",[274241]="s45:3.83,7:3.33",[274244]="s7:3.33",[274245]="s7:3.33",[274246]="s7:3.33",[274247]="s7:3.33",[274250]="s7:3.33",[274251]="s7:3.33",[274252]="s7:3.33",[274253]="s7:3.33",[274254]="s7:3.33",[274255]="s7:3.33",[274256]="s7:3.33",[274258]="s7:3.33",[275005]="s12:1,armor:20",[275006]="s12:1,armor:20",[276741]="s7:3",[276746]="s7:3",[277117]="s32:0.17,38:3.33",[286978]="s5:2",[286979]="s5:2",[286980]="s5:2",[286987]="s6:2",[286988]="s6:2",[286989]="s6:2",[287012]="s12:1,armor:20",[287013]="s12:1,armor:20",[287014]="s12:1,armor:20",[287019]="s7:3",[287020]="s7:3",[287021]="s7:3"}
ns.gfInst = {[33]="Shadowfang Keep^dungeon^1421^44.72^67.77^Silverpine Forest^f^Rethilgore;Razorclaw the Butcher;Baron Silverlaine;Commander Springvale;Odo the Blindwatcher;Fenrus the Devourer;Wolf Master Nandos;Archmage Arugal",[34]="Stormwind Stockade^dungeon^1429^19.81^35.55^Elwynn Forest^f^Targorr the Dread;Kam Deepfury;Hamhock;Dextren Ward;Bazil Thredd",[36]="Deadmines^dungeon^1436^38.16^77.48^Westfall^f^Rhahk'Zor;Sneed;Miner Johnson;Gilnid;Captain Greenskin;Mr. Smite;Cookie;Edwin VanCleef",[43]="Wailing Caverns^dungeon^1413^47.69^34.98^The Barrens^f^Lady Anacondra;Lord Cobrahn;Kresh;Lord Pythas;Skum;Lord Serpentis;Verdan the Everliving;Mutanus the Devourer",[47]="Razorfen Kraul^dungeon^1413^42.27^89.87^The Barrens^f^Roogug;Aggem Thorncurse;Death Speaker Jargba;Overlord Ramtusk;Agathelos the Raging;Charlga Razorflank",[48]="Blackfathom Deeps^dungeon^1440^16.5^11.03^Ashenvale^f^Ghamoo-ra;Lady Sarevess;Geilhast;Lorgus Jett;Old Serra'kis;Twilight Lord Kelris;Aku'mai",[70]="Uldaman^dungeon^1418^35.21^10.29^Badlands^f^Revelosh;The Lost Dwarves;Ironaya;Obsidian Sentinel;Ancient Stone Keeper;Galgann Firehammer;Grimlok;Archaedas",[90]="Gnomeregan^dungeon^1426^17.67^39.15^Dun Morogh^f^Viscous Fallout;Electrocutioner 6000;Crowd Pummeler 9-60;Mekgineer Thermaplugg;Grubbis",[109]="Sunken Temple^dungeon^1435^77.3^35.92^Swamp of Sorrows^f^Atal'alarion;Avatar of Hakkar;Shade of Eranikus;Hazzas;Morphaz;Weaver;Dreamscythe;Jammal'an the Prophet",[129]="Razorfen Downs^dungeon^1413^50.91^92.88^The Barrens^f^Tuten'kash;Plaguemaw the Rotting;Mordresh Fire Eye;Ragglesnout;Glutton;Amnennar the Coldbringer",[189]="Scarlet Monastery^dungeon^1420^85.08^31.38^Tirisfal Glades^f^Interrogator Vishas;Bloodmage Thalnos;Houndmaster Loksey;Arcanist Doan;Herod;High Inquisitor Fairbanks;High Inquisitor Whitemane",[209]="Zul'Farrak^dungeon^1446^38.73^19.9^Tanaris^f^Hydromancer Velratha;Gahz'rilla;Antu'sul;Theka the Martyr;Witch Doctor Zum'rah;Nekrum Gutchewer;Shadowpriest Sezz'ziz;Chief Ukorz Sandscalp",[229]="Blackrock Spire^dungeon^1428^32.99^25.17^Burning Steppes^f^Highlord Omokk;Shadow Hunter Vosh'gajin;War Master Voone;Mother Smolderweb;Urok Doomhowl;Quartermaster Zigris;Halycon;Gizrul the Slavener;Overlord Wyrmthalak;Pyroguard Emberseer;Warchief Rend Blackhand;The Beast;General Drakkisath;Lord Valthalak",[230]="Blackrock Depths^dungeon^1427^27.15^72.48^Searing Gorge^f^High Interrogator Gerstahn;Lord Roccor;Houndmaster Grebmar;Ring of Law;Pyromancer Loregrain;Lord Incendius;Warder Stilgiss;Fineous Darkvire;Bael'Gar;General Angerforge;Golem Lord Argelmach;Hurley Blackbreath;Phalanx;Ribbly Screwspigot;Plugger Spazzring;The Vault;Ambassador Flamelash;The Seven;Magmus;Princess Moira Bronzebeard;Emperor Dagran Thaurissan",[249]="Onyxia's Lair^raid^1445^52.9^77.71^Dustwallow Marsh^f^Onyxia",[289]="Scholomance^dungeon^1422^69.05^72.97^Western Plaguelands^f^Kirtonos;Jandice Barov;Rattlegore;Marduk Blackpool;Vectus;Kormok;Ras Frostwhisperer;Instructor Malicia;Doctor Theolen Krastinov;Lorekeeper Polkelt;The Ravenian;Lord Alexei Barov;Lady Illucia Barov;Darkmaster Gandling",[329]="Stratholme^dungeon^1423^26.09^10.44^Eastern Plaguelands^f^Hearthsinger Forresten;Timmy the Cruel;Malor the Zealous;Cannon Master Willey;Archivist Galford;Balnazzar;The Unforgiven;Baroness Anastari;Nerub'enkan;Maleki the Pallid;Magistrate Barthilas;Ramstein the Gorger;Baron Rivendare;Black Guard Swordsmith;Crimson Hammersmith;Ezra Grimm;Postmaster Malown;Skul;Stonespine",[349]="Maraudon^dungeon^1443^29.1^62.87^Desolace^f^Noxxion;Razorlash;Tinkerer Gizlock;Lord Vyletongue;Celebras the Cursed;Landslide;Rotgrip;Princess Theradras",[389]="Ragefire Chasm^dungeon^1454^52.96^48.87^Orgrimmar^f^Oggleflint;Taragaman the Hungerer;Jergosh the Invoker;Bazzalan",[429]="Dire Maul^dungeon^1444^62.04^33.27^Feralas^f^Zevrim Thornhoof;Hydrospawn;Lethtendris;Pusillin;Alzzin the Wildshaper;Tendris Warpwood;Illyanna Ravenoak;Magister Kalendris;Immol'thar;Prince Tortheldrin;Guard Mol'dar;Stomper Kreeg;Guard Fengus;Guard Slip'kik;Captain Kromcrush;Cho'Rush the Observer;King Gordok;Lord Hel'nurath;Tsu'zee",[2959]="City of Dalaran^dungeon^1421^69.6^46.1^Silverpine Forest^f^Arcane Anomaly;Fel Ancient;Mana Devourer;Mana Elemental;Unstable Sentinel;Lyn the Ignored;Atrexis the Grave Knight;Mana Wraith;Shade of the Archmage",[2998]="Excavation Site: Wetlands^dungeon^1437^24.5^73.4^Wetlands^f^Saltspine;Shadetooth;Highland Horror;Relic Guardian",[2999]="Ruins of Lordaeron^dungeon^1420^63.3^67.5^Tirisfal Glades^f^Witherfang;The Abandoned;The Butcher;Lordaeron Captain;Viktor the Vile;Bjork;Rath'mael",[3065]="The Hall of Thanes^dungeon^1455^77.1^51.3^Ironforge^f^Faldrim Anvilmar;Infurnus;Plunder;Durgen Dirgehammer"}
ns.gfRare = {[79]="Narg the Taskmaster^1429,40.9,77.5",[471]="Mother Fang^1429,62.1,48.1",[520]="Brack^1436,27.3,44.5",[521]="Lupos^1431,32.6,25.8;1431,70.6,26.6;1431,67.3,26.8;1431,64.5,26.7;1431,62,24.9;1431,61.2,22.8;1431,38.3,25.3;1431,36.3,24.4",[584]="Kazon^1433,29.8,8.3;1433,31.8,12;1433,31.3,9.4;1433,29.9,6.7",[596]="Brainwashed Noble^1436,44,78.3",[1037]="Dragonmaw Battlemaster^1437,52.9,54",[1119]="Hammerspine^1426,71.5,51.3",[1132]="Timber^1426,34.2,41.8;1426,33.5,43.7;1426,34.1,42.6",[1260]="Great Father Arctikus^1426,22.8,52.1;1426,21.6,51.8;1426,22.5,54.2;1426,23.8,51;1426,24.2,52.6;1426,23.5,54.6",[1424]="Master Digger^1436,46.4,19.1",[1936]="Farmer Solliden^1420,38,49.6;1420,34.1,52.1;1420,37.1,49.5;1420,38,52.2",[1948]="Snarlmane^1421,65.1,25.1",[2090]="Ma'ruk Wyrmscale^1437,48.1,74.7",[2108]="Garneg Charskull^1437,38.4,46.1",[2258]="Stone Fury^1416,64.7,44.8",[2606]="Nimar the Slayer^1417,64.6,73.2;1417,64.4,74.7;1417,61.3,72.5;1417,60.2,72.3;1417,63.9,68.6;1417,63.2,67.7;1417,66.4,64;1417,65.6,63.5",[2751]="War Golem^1418,52.4,19.5;1418,49.4,12.1;1418,45.4,33.5",[3056]="Ghost Howl^1412,34.7,34.2;1412,47.1,47.8;1412,46.7,25.5",[3253]="Silithid Harvester^1413,43.1,70.1",[3270]="Elder Mystic Razorsnout^1413,59.2,24.4",[3398]="Gesharahan^1413,46.5,39.5",[3792]="Terrowulf Packlord^1440,49.8,39.6",[4015]="Pridewing Patriarch^1442,53.8,36.3;1442,47.8,46.7",[5785]="Sister Hatelash^1443,90,37.1",[5799]="Hannah Bladeleaf^1413,48.5,79.7",[5822]="Felweaver Scornn^1411,52.8,9;1411,53,7.3;1411,51.7,9.6",[5827]="Brontus^1413,47.3,73.2",[5829]="Snort the Heckler^1413,41.2,22.2",[5831]="Swiftmane^1413,61.2,34.5",[5832]="Thunderstomp^1413,48.1,79.8",[5834]="Azzere the Skyblade^1413,44.8,64.1",[5841]="Rocklance^1413,53.6,45.5",[5849]="Digger Flameforge^1413,47.5,85.5",[5851]="Captain Gerogg Hammertoe^1413,49.5,83.9",[5935]="Ironeye the Invincible^1441,87.2,78.4",[6488]="Fallen Champion^",[6489]="Ironspine^",[6490]="Azshir the Sleepless^",[7017]="Lord Sinslayer^1439,56.6,34.9;1439,55.5,36.3",[12433]="Krethis Shadowspinner^1420,24,79.7",[14221]="Gravis Slipknot^1416,58.2,41.9",[14272]="Snarlflare^1433,37.4,31;1433,42.6,33.5;1433,42.9,35.1;1433,44.5,33.1;1433,39.1,33.3;1433,37.6,33.4;1433,35.1,32.7;1433,38.9,29.7",[14277]="Lady Zephris^1424,64.5,79.7",[14280]="Big Samras^1424,86,39.9",[211965]="Carrodin^",[255887]="Slydris^",[259398]="Rare #259398^",[271080]="Rare #271080^",[276061]="Rare #276061^",[276194]="Dustwind Eggtender^",[276198]="Shal'ma^"}
