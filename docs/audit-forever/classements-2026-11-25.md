# Contrôle des classements EasyBIS du 25 novembre 2026

Le contrôle a parcouru **26 330 combinaisons objet, spécialisation, mode et emplacement** dans les listes Raid et PvP, auxquelles s’ajoutent **3 028 entrées AoE** sur 21 profils. Cela couvre **3 394 objets distincts**. Les variantes de faction qui ont un autre identifiant comptent séparément. Le chasseur Survie mêlée, conservé dans les données pour les archives, a aussi été contrôlé. Le catalogue inspecté contient 29 profils actifs et ce profil archivé.

Le lecteur Lua de l’addon a calculé les deux modes de chaque profil avec six alternatives et **432 combinaisons de filtres par liste**. Le contrôle a vérifié la disponibilité par phase et faction, les restrictions de classe, le niveau maximal et la compatibilité des deux bagues ou bijoux proposés. Aucune violation de ces règles n’a été détectée. Le contrôle existant signale 34 entrées de niveau requis bas et 28 fortes avances, dont plusieurs expliquées par un bonus de set, un effet propre à une technique ou la phase Archives. Il n’a détecté aucune arme de lanceur de sorts sans la puissance attendue selon ses critères. [Règles du contrôle](../../_build/audit.py) · [Analyse précédente des alertes](alertes.md)

## Bijoux dont l’ordre change avec l’équipement

Les écarts donnent les DPS du premier objet moins ceux du second. Les deux objets sont testés sur le même profil et avec le même bijou compagnon. Le toucher est relevé avec ce compagnon équipé et l’emplacement comparé vide. Les essais ignorent les bonus géographiques, durent 180 s et utilisent la révision WoWSims `07648faf` avec les mêmes tirages entre concurrents.

| Profil et duel | Toucher | Écart moyen | Lecture |
| --- | ---: | ---: | --- |
| Guerrier Armes Alliance, **Cleansed Vilebranch Medallion** face à **Behemoth Bones**, avec Hand of Justice | 70 / 75 / 80 | +3,66 / +1,96 / −5,34 DPS | Médaillon situationnel en pré-raid PvE. Même traitement pour la Rune Horde, dont le duel suit le même ordre. 20 000 combats par point. |
| Guerrier Armes Alliance, **Smolderweb’s Eye** face à **Behemoth Bones**, avec Hand of Justice | 70 / 75 / 80 | +4,26 / −1,78 / −9,09 DPS | L’œil est le deuxième BiS après la mise en situationnel du médaillon. Son avantage dépend lui aussi du toucher. Comparaison monocible du moteur pour ce bijou. 20 000 combats par point. |
| Chasseur Maîtrise des bêtes Alliance, **Cleansed Vilebranch Medallion** face à **Behemoth Bones**, avec Smolderweb’s Eye | 60 / 80 | +1,27 / −4,62 DPS | Le bijou que la liste affiche en BiS perd au cap du profil. 8 000 combats par point. |
| Chasseur Maîtrise des bêtes Horde, **Rune of the Guard Captain** face à **Behemoth Bones**, avec Smolderweb’s Eye | 70 / 80 | +1,98 / −4,74 DPS | Même inversion côté Horde. 8 000 combats par point. |
| Chaman Amélioration Alliance, **Frozen Heart of the Mountain** face à **Behemoth Bones**, avec Smolderweb’s Eye | 50 / 65 | −2,66 / −3,71 DPS | Les os devancent le deuxième BiS affiché dans les deux essais. 8 000 combats par point. |
| Chaman Amélioration Horde, **Frozen Heart of the Mountain** face à **Behemoth Bones**, avec Smolderweb’s Eye | 50 / 65 | +5,32 / −3,43 DPS | Le cœur garde un avantage sur la tenue orque à 50 de toucher, puis l’ordre s’inverse. 12 000 combats par point. |
| Guerrier Fureur Alliance, **Cleansed Vilebranch Medallion** face à **Behemoth Bones**, avec Hand of Justice | 70 / 90 | +4,30 / −1,07 DPS | Avantage du médaillon à 70. À 90, l’écart est inférieur à deux erreurs standard. 8 000 combats par point. |

Le médaillon offre 14 PA et 0,7 % de toucher, avec 42 PA quand son bonus de forêt ou de plaine s’applique. Les os offrent 34 PA et un soin. Frozen Heart offre 0,9 % de toucher ainsi qu’un bonus temporaire aux sorts de Givre et d’Ombre, doublé en zone enneigée. Le résultat du Chaman combine la tenue, la race et le toucher de chaque profil. Il ne permet pas d’attribuer la différence entre factions à un seul de ces paramètres. [Médaillon](https://www.wowhead.com/forever/item=270275/cleansed-vilebranch-medallion) · [Behemoth Bones](https://zephras.com/forever/enUS/item/280065/) · [Frozen Heart](https://www.wowhead.com/forever/item=249469/frozen-heart-of-the-mountain)

## Main gauche alternative du Chasseur Maîtrise des bêtes

Sur **192 des 432 combinaisons de filtres** testées, le lecteur Lua et le générateur divergent sur les alternatives de main gauche. L’addon peut reprendre un classement générique lorsqu’aucune mesure ne correspond à la main droite retenue. Avec les objets vus dans Forever, l’Alliance, le pré-raid et le plafond de grade 3, cette main droite est **King Mosh’s Tooth**. Le générateur laisse alors la main gauche alternative vide. L’addon propose notamment **Sentinel’s Blade** et **Jhordy’s Misplaced Screwdriver**. Le test de parité global s’arrête sur cet écart. [Lecture des groupes d’armes](../../Ladders.lua) · [Classement des partenaires](../../_build/ladders.py)

La 1.10.3 applique le même choix que le générateur. Une main gauche classée par partenaire s’affiche si la main droite retenue a une liste mesurée ou si une liste par faction est disponible. Sans mesure correspondante, l’alternative de main droite reste visible avec la mention « Estimé ».

## Effets partiellement mesurés

L’archive indique un effet absent sur **146 scores de base** concernant 56 objets et une fréquence de proc supposée sur **9 scores de base** concernant 3 objets. Les scores de base peuvent être remplacés par une mesure contextuelle lors de l’affichage. **Sept** de ces entrées restent proposées en BiS pré-raid avec les filtres habituels.

- **Darkmantle Footpads** chez les trois Voleurs. L’effet propre aux bottes est un point de camouflage. Ses 24 Agilité et 0,7 % de toucher restent pertinents en DPS. [Fiche Forever](https://www.wowhead.com/forever/item=226831/darkmantle-footpads)
- **Robe of the Void** dans les trois spécialisations Démoniste. La robe a 46 de puissance des sorts. L’effet de soin du familier ne constitue pas un gain DPS direct. [Fiche Forever](https://www.wowhead.com/forever/item=14153/robe-of-the-void)
- **Teebu’s Blazing Longsword** en Voleur Combat. Le duel avec Flurry Axe en main gauche donne encore l’avantage à Teebu lorsque son proc est désactivé. Il devance Persuader de **1,96 ± 0,48 DPS** en Alliance et **1,47 ± 0,47 DPS** en Horde. Avec la fréquence supposée de 1,9 déclenchement par minute, l’avance passe à **17,67** et **16,88 DPS**. Le rang résiste à ce contrôle et l’ampleur de l’écart dépend du proc. Chaque essai utilise 10 000 combats. [Fiche Forever](https://www.wowhead.com/forever/item=1728/teebus-blazing-longsword)

Le générateur dispose de [notes de repli pour les effets incomplets](../../_build/notes.py), que l’[export des notes](../../_build/luaout.py) n’appelle pas. Dans les listes actuelles, **135 des 146 entrées** repérées pour un effet absent n’ont aucune note correspondante. La nature de l’effet détermine l’impact sur le rang. Le rapprochement avec les corrections de stats permanentes donne aussi 98 cas sur 15 objets dans des emplacements sans mesure par faction. Une correction des données de l’addon ne signifie pas nécessairement que WoWSims possédait la même erreur.

## Couverture par spécialisation

| Spécialisation | Raid | PvP | AoE |
| --- | ---: | ---: | ---: |
| Druide Équilibre | 362 | 447 | 126 |
| Druide Farouche félin | 415 | 470 | 139 |
| Druide Farouche ours | 479 | 469 | — |
| Druide Restauration | 346 | 425 | — |
| Chasseur Maîtrise des bêtes | 529 | 533 | 154 |
| Chasseur Précision | 485 | 532 | 150 |
| Chasseur Survie mêlée, archives | 398 | 446 | — |
| Chasseur Survie distance | 483 | 545 | 171 |
| Mage Arcanes | 395 | 445 | 142 |
| Mage Feu | 389 | 444 | 131 |
| Mage Givre | 394 | 445 | 135 |
| Paladin Sacré | 364 | 445 | — |
| Paladin Protection | 462 | 485 | — |
| Paladin Vindicte | 368 | 421 | 157 |
| Paladin Shockadin | 370 | 436 | 160 |
| Prêtre Discipline | 384 | 460 | — |
| Prêtre Sacré | 385 | 451 | — |
| Prêtre Ombre | 372 | 447 | 134 |
| Voleur Assassinat | 418 | 461 | 152 |
| Voleur Combat | 434 | 492 | 152 |
| Voleur Finesse | 433 | 494 | 152 |
| Chaman Élémentaire | 380 | 498 | 122 |
| Chaman Amélioration | 401 | 425 | 140 |
| Chaman Restauration | 372 | 463 | — |
| Démoniste Affliction | 410 | 442 | 132 |
| Démoniste Démonologie | 412 | 448 | 135 |
| Démoniste Destruction | 410 | 444 | 135 |
| Guerrier Armes | 397 | 445 | 149 |
| Guerrier Fureur | 454 | 505 | 160 |
| Guerrier Protection | 471 | 495 | — |
| **Total** | **12 372** | **13 958** | **3 028** |

Le contrôle exhaustif porte sur les entrées livrées, les règles d’affichage et la provenance des scores. Les nouveaux combats portent sur les duels ci-dessus. Les listes PvP et les listes de soin restent des évaluations de leurs pondérations et des effets documentés.

## Bonus liés au type de cible

Le rapprochement du catalogue EasyBIS et des effets de WoWSims Forever `07648faf` donne **118 objets** à examiner. Il combine les statistiques conditionnelles du catalogue et les effets qui déclarent un type de créature dans les données du simulateur. Parmi eux, **56** figurent dans un classement Raid, PvP ou AoE et **25** apparaissent dans les listes pré-raid Raid ou PvP avec les filtres par défaut et six alternatives. Le contrôle a évalué 1 440 configurations de liste couvrant les 30 profils livrés, les deux factions, les trois phases et les filtres « vus dans Forever » et récompenses PvP. Les effets dont la condition figure seulement dans un texte absent des deux bases peuvent échapper à ce décompte.

| Type de cible | Les 25 objets affichés lors de l’audit |
| --- | --- |
| Bêtes | Houndmaster’s Bow, Huntsman’s Harpoon, Beastslayer’s Trident, King Mosh’s Tooth |
| Démons | Shard of the Splithooves, Royal Seal of Eldre’Thalas (Chasseur, 18473), Demon Worshipper’s Necklace |
| Draconiens | Wyrmhide Spaulders, Draconic Infused Emblem |
| Élémentaires | Satyr’s Bow |
| Humanoïdes | Royal Seal of Eldre’Thalas (Voleur, 18465), Monstrous Glaive, Barbarous Blade, Shadowy Mail Greaves, The Jaw Breaker, Nama’s Cherished Necklace |
| Morts-vivants | Seal of the Dawn, Argent Crusader, Cannonball Runner, Verdant Footpads, Threadbare Trousers, Bonecrusher, Bone Slicing Hatchet, Rune of the Dawn, Tenets of the Silver Hand |

En Raid, la pondération ignore la PA et la puissance des sorts réservées à un type de créature. Le profil monocible WoWSims de référence utilise une cible générique. En PvP, 15 profils livrés pondèrent explicitement la PA contre les humanoïdes. En AoE, les deux scénarios d’EasyBIS utilisent des humanoïdes. [Pondérations PvP](../../_build/specs.py) · [Scénario court](../../_build/simulate_aoe.py) · [Parcours de donjon](../../_build/aoe_encounter.py)

| Objet | Où il ressort | Conclusion du contrôle |
| --- | --- | --- |
| **Royal Seal of Eldre’Thalas** (18465), Voleur | Ancien premier bijou PvP en Assassinat, Combat et Finesse dans les deux factions. Il passe en « Situationnel » en pré-raid. | En retirant uniquement les **45 PA contre humanoïdes** du modèle, le sceau sort des deux BiS dans les six configurations. Behemoth Bones passe premier, devant le médaillon de faction. Le sceau garde **1 % de toucher**. [Fiche Forever](https://www.wowhead.com/forever/item=18465/royal-seal-of-eldrethalas) |
| **Barbarous Blade** (18520), Chasseur | Première arme de mêlée AoE en Maîtrise des bêtes, Précision et Survie distance, dans les deux factions. Alternative en Raid. | L’aide du score et la note de l’arme indiquent les packs humanoïdes. Ses **33 PA supplémentaires** contre eux entrent dans la mesure. Elle possède **50 PA permanentes et 1 % de critique**. [Fiche Forever](https://www.wowhead.com/forever/item=18520/barbarous-blade) |
| **Royal Seal of Eldre’Thalas** (18473), Chasseur | Deuxième bijou pré-raid en Précision côté Alliance et alternative en Maîtrise des bêtes. | **10 Agilité** permanente et **45 PA contre les démons**. Le rang Raid utilise la valeur générique du bijou. Le libellé anti-démons est déjà présent. [Fiche Forever et comparaison Classic](https://zephras.com/forever/enUS/item/18473/) |
| **Draconic Infused Emblem** (22268), lanceurs de sorts | Alternative Raid en Équilibre, Arcanes, Feu, Ombre, Élémentaire, Démonologie et Destruction. Premier bijou AoE en Arcanes. | Le proc donne **35 dégâts des sorts** sur une cible ordinaire et **70** contre les draconiens. Il contribue déjà au rang AoE sur les humanoïdes. [Fiche Forever](https://www.wowhead.com/forever/item=22268/draconic-infused-emblem) |
| **Flamebreak Talisman** (280071), profils physiques | Première place AoE notamment en Druide félin, chez les trois profils Chasseur actifs et chez les trois Voleurs. | L’utilisation donne **33 Agilité** en général et **66** en présence d’un élémentaire. Les mesures sur les packs humanoïdes expliquent son rang générique. [Fiche Forever](https://www.wowhead.com/forever/item=280071/flamebreak-talisman) |
| **Demon Worshipper’s Necklace** (287035) et **Threadbare Trousers** (18346) | Alternatives en Amélioration, Démonologie ou Destruction pour le collier, et en Destruction pour le pantalon. | Le collier a **11 puissance des sorts** et **11 dégâts des sorts supplémentaires contre les démons**. Le pantalon a **23 puissance des sorts** et **23 dégâts des sorts supplémentaires contre les morts-vivants**. Les rangs génériques valorisent leur part permanente. [Collier](https://www.wowhead.com/forever/item=287035/demon-worshippers-necklace) · [Pantalon](https://www.wowhead.com/forever/item=18346/threadbare-trousers) |
| **King Mosh’s Tooth** (286613) | Alternative de mêlée pour Chasseur et Voleur en Raid selon la spé et le filtre. | Ses **11 Agilité et 13 PA** restent actives sur toutes les cibles. Les **15 PA contre les bêtes** s’ajoutent en situation. [Fiche Forever](https://www.wowhead.com/forever/item=286613/king-moshs-tooth) |
| **Satyr’s Bow** (18323) et **Verdant Footpads** (13954) | L’arc est premier en Assassinat et Armes PvE. Les bottes sont premières pour Druide Restauration, Paladin Sacré et Chaman Restauration PvE. | Le premier rang de l’arc s’appuie sur **1 % de toucher et 4 PA**. Les bottes ont **38 soins** et leur bonus anti-morts-vivants concerne les dégâts. Les deux rangs sont cohérents avec les statistiques permanentes. [Arc](https://www.wowhead.com/forever/item=18323/satyrs-bow) · [Bottes](https://www.wowhead.com/forever/item=13954/verdant-footpads) |

Les **25 objets** s’affichent en « Situationnel » dans toutes leurs listes pré-raid Raid et PvP éligibles. La même règle couvre les deux bijoux de faction dont la PA augmente en forêt et en plaine, Frozen Heart et Molten Heart of the Mountain ainsi que Flamebreak Talisman. Les options s’ajoutent aux alternatives classées, y compris dans les configurations d’armes secondaires. **Heart of Wyrmthalak** s’affiche aussi pour les profils qui peuvent déclencher son effet en mêlée ou à distance. Les dégâts de son proc triplent contre les Orcs. **Seal of the Dawn**, **Rune of the Dawn** et **Tenets of the Silver Hand** utilisent leurs règles existantes. En Paladin Protection, **Tenets of the Silver Hand** apparaît à partir de cinq alternatives. [Objets de l’audit](../../_build/corrections/target_situational.json) · [Options situationnelles](../../_build/corrections/situational_gear.json) · [Heart of Wyrmthalak](https://www.wowhead.com/forever/item=22321/heart-of-wyrmthalak) · [Librams](../../_build/corrections/relics.json)

## Variantes d’armure chez un même vendeur

| Variantes comparées | Alliance | Horde | Avantage de la version plus protectrice |
| --- | --- | --- | --- |
| Épaules Agilité, cuir et mailles | 271955 et 271956 | 272105 et 272106 | +164 armure, mêmes autres statistiques |
| Épaules lanceur de sorts, tissu et cuir | 271953 et 271954 | 272103 et 272104 | +73 armure, mêmes autres statistiques |
| Ceintures d’Arathi de niveau requis 48, cuir et mailles | 20115 et 20088 | 20193 et 20151 | +42 armure et +2 Endurance, mêmes statistiques offensives |

Les listes Raid et PvP retiennent la variante plus protectrice lorsque la spécialisation peut l’équiper et qu’elle est disponible avec les mêmes filtres. Le prix en or peut différer. Les ceintures d’Arathi de niveau requis 58 appartiennent à deux ensembles distincts. [Épaules en mailles](https://www.wowhead.com/forever/item=271956/theramore-epaulets) · [Épaules en cuir](https://www.wowhead.com/forever/item=272104/darkspear-shoulders) · [Ceinture niveau 48](https://www.wowhead.com/forever/item=20088/highlanders-chain-girdle) · [Set cuir](https://www.wowhead.com/forever/item=20045/highlanders-leather-girdle) · [Set mailles](https://www.wowhead.com/forever/item=20043/highlanders-chain-girdle)

## Totems du Chaman

En Amélioration, **Totem of Rage** est recommandé en Raid et PvP pour ses dégâts de Horion. Le totem de Maelström (272432) est une alternative pour les profils qui utilisent le talent et lancent Éclair. En Restauration, **Tidal Totem** est recommandé pour les profils qui utilisent Vague de soins. En Élémentaire, **Totem of the Storm** (23199) conserve son score mesuré en Raid et devient le choix recommandé en PvP. Les recommandations sans mesure et leurs alternatives n’affichent pas de pourcentage. [Rage](https://www.wowhead.com/forever/item=22395/totem-of-rage) · [Maelström](https://foreverdb.net/item/272432) · [Tidal](https://www.wowhead.com/forever/item=272431/tidal-totem) · [Storm](https://www.wowhead.com/forever/item=23199/totem-of-the-storm) · [Tests et effets](../../_build/corrections/relics.json)
