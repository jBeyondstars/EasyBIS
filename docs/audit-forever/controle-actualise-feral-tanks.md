# Félin et tanks · WoWSims Forever sur huit tenues de référence

Au 22 novembre 2026, **2 234 des 2 272 propositions distinctes** du félin et des trois tanks ont une mesure sur le moteur `a73af71451`. **1 512** ont une voie d’obtention documentée dans les limites pré-raid et de rang de la semaine. **478** relèvent d’une phase ultérieure ou d’un rang supérieur. Pour **244** autres, la valeur est une projection sur une tenue vérifiée, l’obtention de la pièce restant incertaine. Les factions ont été simulées séparément sur une race et une tenue propres à chacune. [Révision de WoWSims](https://github.com/wowsims/forever/commit/a73af7145111ce19c621e3b5f678553adf326907) · [Données chiffrées](controle-actualise-feral-tanks.json)

## Couverture et disponibilité

| Profil | Pré-raid et rang atteint | Phase ou rang ultérieur | Ancien rang sans vendeur Forever | Obtention non vérifiée | ID absent | Suffixe indéterminé | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Félin](druid-feral-cat.md) | 432 | 114 | 39 | 28 | 0 | 0 | 613 |
| [Ours](druid-feral-bear.md) | 364 | 118 | 40 | 25 | 1 | 0 | 548 |
| [Guerrier Protection](warrior-protection.md) | 376 | 122 | 44 | 16 | 9 | 4 | 571 |
| [Paladin Protection](paladin-protection.md) | 340 | 124 | 30 | 22 | 21 | 3 | 540 |
| **Total** | 1512 | 478 | 153 | 91 | 31 | 7 | 2272 |

Les fiches du [registre](README.md) contiennent 1840 valeurs pour 1876 lignes PvE et 1944 pour 1975 lignes JcJ. Un même ID peut appartenir aux deux modes. Le total numérique couvre 3506 substitutions **spécialisation × emplacement × ID × faction**. Pour les lignes JcJ, « contrôle sur boss » rappelle que la mesure décrit un combat de raid. La robustesse, le contrôle, l’endurance et les adversaires joueurs relèvent du classement JcJ de l’addon.

Les deux bases officielles du moteur sont chargées. 31 propositions restent sans définition WoWSims et 7 demanderaient de connaître le suffixe aléatoire. Parmi les valeurs numériques, 114 incluent un effet absent du moteur et 2 utilisent une fréquence de proc supposée. Les cellules portent la réserve correspondante. [Chargeur WoWSims](https://github.com/wowsims/forever/blob/a73af7145111ce19c621e3b5f678553adf326907/assets/database/loader.go)

Le catalogue final a pour SHA-256 `3a8f1bdb895f78f6dea2bd0cd0b7c1449a07d6c5e82676e3565267aef20ffea0`. Le contrôle associe chaque ligne à son véritable ID, y compris lorsqu’EasyBIS affiche un jumeau de faction. Le code de phase 9 regroupe les phases ultérieures ou dont la date reste indéterminée. Le plafond retenu pour la semaine est le rang 6. [Progression JcJ de Blizzard](https://worldofwarcraft.blizzard.com/en-us/news/24303316) · [Rangs d’EasyBIS](../../_build/ranks.py) · [Phases d’EasyBIS](../../_build/phases.py)

## Références corrigées

Chaque tenue de contrôle a été vérifiée au niveau 60 pour sa classe, sa faction, ses conditions d’équipement et une source compatible avec la phase. Les profils sont elfe de la nuit et tauren pour les druides, humain et orc pour le guerrier, humain et réprouvé pour le paladin. Les essais vérifient chaque objet, ses conditions de métier, son type d’armure ou d’arme, les autres emplacements occupés, l’unicité et les récompenses de quête incompatibles. Les enchantements conservés ont une formule ou une quête identifiée et un emplacement compatible. [Capacités des classes](https://github.com/wowsims/forever/blob/a73af7145111ce19c621e3b5f678553adf326907/ui/sim/player/classes/capabilities_auto_gen.ts) · [Sources des objets, entrées et vérifications](protocole-actualise-feral-tanks.zip)

| Profil | Corrections apportées à la première tenue |
|---|---|
| Félin | Theramore Pauldrons (271955) sur l’elfe et Darkspear Pauldrons (272105) sur le tauren. Le félin porte Blackhand’s Breadth (13965) avec Mark of the Chosen (17774, Alliance) ou Rune of the Guard Captain (19120, Horde). La formule pré-raid appropriée aux gants pour l’effet 2564 reste à confirmer. Les gants sont testés sans cet enchantement. |
| Ours | Même distinction pour les épaules. Les jambes et l’insigne d’Alterac ont des ID propres à chaque camp. Les brassards, bottes, bagues et arme de rang ou de raid sont remplacés. L’arme de base est The Unstoppable Force (19323), récompense de réputation d’Alterac. Le « rang 6 » qui figure dans le nom de l’insigne désigne son étape de réputation. |
| Guerrier | Mark of Fordring (15411) et Boots of Valor (16734) remplacent deux objets à source incertaine dans les archives. Le bouclier de base porte zéro enchantement pour l’effet 7663, dont la formule appropriée restait incertaine. Le guerrier emploie les rangs du maître pour Cri de guerre (11551), Vengeance (11601) et Frappe héroïque (11567). |
| Paladin | Le collier est Mark of Fordring, les épaules Lightforge Spaulders (16729), l’arme Thrash Blade (17705) et le bouclier Draconian Deflector (12602). Le logement de libram reste vide. L’ancienne tenue comportait notamment une arme de progression de raid et des épaules de faction. |

Les épaules Theramore et Darkspear ont chacune leur réputation dans les infobulles Forever. Pour les ensembles bleus Premier, la vérification distingue les vendeurs retrouvés pour l’ID exact, l’appartenance à un ensemble et les ressemblances de famille. Une attribution par ensemble seule conserve la mention « projection, obtention non vérifiée ». Les cinq quêtes historiques du set Avenger’s ont un côté Alliance dans les données disponibles. La campagne garde une projection de phase Alliance pour ces cinq pièces. [Épaules Theramore](https://www.wowhead.com/forever/item=271955) · [Épaules Darkspear](https://www.wowhead.com/forever/item=272105) · [Fiche du vendeur des épaules Chevalier](https://raiddex.com/en/wow-forever/items/premier-chevalier-shoulders)

## Protocole et incertitude

Chaque valeur donne l’effet de la pièce face à l’emplacement vide, sur 2 000 combats de 180 secondes avec une variation de 5 secondes et la graine 4242. Les bagues et bijoux partent de deux emplacements vides. Une arme à deux mains libère la main gauche. Le druide évaluant une main gauche tient la masse à une main 11923. L’enchantement 1896, réservé aux armes à deux mains, est retiré sur les armes à une main. Une pièce exigeant un métier est essayée par un personnage qui le possède. Les deux configurations de la comparaison ont les mêmes métiers. [Pilote, huit profils et recettes de rejeu](protocole-actualise-feral-tanks.zip)

Le signe **±** donne une erreur standard de la différence appariée entre deux configurations à graine identique. Une différence voisine de deux erreurs standard mérite un contrôle supplémentaire. Les écarts de deux pièces face à un emplacement vide ne fournissent pas à eux seuls l’erreur de leur duel direct. Un signe positif signifie plus de dégâts infligés, plus de menace ou plus de dégâts reçus selon la colonne. Les deux tanks à bouclier et l’ours font face au boss. Les réserves sur les effets, la rotation et les buffs de la rencontre restent applicables aux deux factions.

## Félin · duels directs à 20 000 combats

| Remplacement, deuxième configuration moins première | Alliance · Δ DPS ± ES | Horde · Δ DPS ± ES |
|---|---:|---:|
| Tome of Knowledge → Scepter of Interminable Focus | +2,713 ± 0,169 | +3,118 ± 0,172 |
| Legionite Glaive → Bonecrusher | −5,195 ± 0,205 | −5,199 ± 0,205 |
| Outlaw’s Collar → Eye of Rend | −1,822 ± 0,174 | −2,190 ± 0,176 |
| Outlaw’s Collar → Wolfshead Helm | −12,818 ± 0,222 | −12,731 ± 0,220 |
| Blackveil Cape → Howler’s Furs | −2,217 ± 0,208 | −0,415 ± 0,204 |
| Cutthroat’s Signet → Warden’s Signet of Ferocity | +0,374 ± 0,064 | +0,231 ± 0,062 |
| Emplacement vide → Behemoth Bones, soin laissé hors rotation | +7,823 ± 0,002 | +7,728 ± 0,002 |
| Emplacement vide → Behemoth Bones, soin forcé | −8,242 ± 0,224 | −8,852 ± 0,222 |
| Behemoth Bones passif → Lucky Shovelnose Tuft, activation laissée à la rotation | +3,606 ± 0,198 | +2,740 ± 0,196 |
| Behemoth Bones passif → Lucky Shovelnose Tuft, activation forcée | −0,016 ± 0,229 | −1,178 ± 0,224 |

Le gain du Scepter et celui de Legionite Glaive sont résolus sur les deux tenues. Howler’s Furs perd du DPS dans cette rotation. L’écart sur le tauren atteint tout juste deux erreurs standard, contre plus de dix sur la référence elfe. Forcer le soin de Behemoth Bones coûte du DPS aux deux races. L’activation forcée de Lucky Shovelnose Tuft face à Behemoth Bones passif demeure indécidable pour la référence Alliance. [Fiche félin](druid-feral-cat.md)

## Ours · menace et dégâts reçus

| Bijou face à un emplacement vide | Alliance · Δ menace/s / Δ dégâts reçus/s | Horde · Δ menace/s / Δ dégâts reçus/s |
|---|---:|---:|
| Adaptive Combat Assistant | +56,50 ± 3,02 / −4,57 ± 1,44 | +52,65 ± 3,13 / −5,61 ± 1,38 |
| Defender's Grip Stabilizer | −2,15 ± 1,65 / −17,37 ± 0,80 | −4,55 ± 1,49 / −18,37 ± 0,72 |

Adaptive Combat Assistant augmente nettement la menace dans les deux configurations. Defender’s Grip Stabilizer réduit davantage les dégâts reçus. Leurs erreurs standard individuelles ne mesurent pas l’incertitude de la différence entre ces deux bijoux. [Fiche ours](druid-feral-bear.md)

## Boucliers · duels directs à 2 000 combats

Chaque ligne oppose le bouclier corrigé au **Draconian Deflector**. Pour Force Reactive Disk, la projection suppose un porteur avec Ingénierie 300 et l’accès futur à la pièce. La valeur de blocage intrinsèque est corrigée à partir des données du client dans les deux configurations. [Valeurs du client](../../_build/corrections/shields.json)

| Bouclier | Porteur | Alliance · Δ menace/s / Δ dégâts reçus/s | Horde · Δ menace/s / Δ dégâts reçus/s |
|---|---|---:|---:|
| Evergreen Shield | Guerrier Protection | +16,38 ± 1,78 / −5,03 ± 0,71 | +16,31 ± 1,80 / −5,11 ± 0,71 |
| Evergreen Shield | Paladin Protection | +14,69 ± 1,38 / −2,01 ± 0,81 | +15,59 ± 1,43 / −1,64 ± 0,81 |
| Force Reactive Disk | Guerrier Protection | +21,11 ± 2,47 / −8,60 ± 0,97 | +19,50 ± 2,42 / −8,41 ± 0,97 |
| Force Reactive Disk | Paladin Protection | +10,71 ± 1,62 / −2,83 ± 0,94 | +12,50 ± 1,58 / −3,20 ± 0,94 |
| Barrier Shield | Guerrier Protection | +16,58 ± 1,74 / +1,02 ± 0,70 | +16,02 ± 1,70 / +1,05 ± 0,70 |
| Barrier Shield | Paladin Protection | +8,00 ± 1,30 / +1,37 ± 0,78 | +6,85 ± 1,30 / +0,26 ± 0,79 |

Evergreen Shield augmente la menace et réduit les dégâts reçus sur les quatre porteurs. Sur le paladin réprouvé, son avantage de mitigation se situe à la limite de deux erreurs standard. La différence de dégâts reçus entre Barrier Shield et Draconian Deflector reste incertaine dans ces quatre duels. [Fiche guerrier](warrior-protection.md) · [Fiche paladin](paladin-protection.md)

Pour Evergreen Shield, le moteur brut applique 58 de blocage alors que l’infobulle Forever indique 44. Les témoins suivants portent exactement le même objet et conservent la même tenue. La seule variation est la correction de ces 14 points. Les valeurs donnent le résultat corrigé moins le moteur brut.

| Porteur · Evergreen Shield corrigé | Alliance · Δ menace/s / Δ dégâts reçus/s | Horde · Δ menace/s / Δ dégâts reçus/s |
|---|---:|---:|
| Guerrier Protection | −8,83 ± 0,02 / +4,11 ± 0,01 | −8,82 ± 0,08 / +4,04 ± 0,06 |
| Paladin Protection | +0,02 ± 0,00 / +4,39 ± 0,01 | +0,02 ± 0,00 / +4,39 ± 0,01 |

## Variation causée par la correction des références

La première campagne complète de la même révision utilisait une seule race par profil. Le tableau compare les valeurs de substitution de ce premier passage à celles du même camp sur la nouvelle tenue. Il donne la médiane des variations absolues et le cas le plus éloigné sur chaque critère applicable. Ces écarts regroupent les changements simultanés de tenue, d’enchantement et, pour le guerrier, de rangs de sorts. Les témoins à équipement identique isolent la correction du blocage. [Première campagne et témoins archivés](protocole-actualise-feral-tanks.zip)

| Profil · camp de départ | Cas communs | Critère | Variation absolue médiane | Plus grande variation signée |
|---|---:|---|---:|---|
| Félin · Horde | 471 | DPS | 0,333 | −19,141 · Persuader (22384) |
| Ours · Horde | 422 | menace/s | 2,832 | −28,504 · Neltharion's Tear (19379) |
| Ours · Horde | 422 | dégâts reçus/s | 1,169 | −9,554 · Warlord's Dragonhide Hauberk (16549) |
| Paladin Protection · Alliance | 411 | menace/s | 0,999 | −16,683 · Premier Chevalier Leggings (272744) |
| Paladin Protection · Alliance | 411 | dégâts reçus/s | 0,515 | +4,009 · Premier Grand Marshal's Aegis (272838) |
| Guerrier Protection · Horde | 430 | menace/s | 1,439 | −99,545 · Scarlet Kris (5267) |
| Guerrier Protection · Horde | 430 | dégâts reçus/s | 0,403 | +3,141 · Legplates of Vigilance (22328) |

Les projections de faction, les mesures de survie sur boss et les poids de classement répondent à des questions différentes. Les deux colonnes de tank et les duels directs permettent de repérer un choix de menace ou de mitigation même lorsque l’ordre du score statique ne les départage pas. [Registre détaillé](README.md)
