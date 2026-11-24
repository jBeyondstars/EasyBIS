# Buffs de classe dans les simulations Raid

Le boss est une cible unique. Les vingt références DPS de la campagne initiale retrouvent le DPS publié au dixième près sur 20 000 combats de 180 ± 5 secondes, graine 4242. Dans le profil Prêtre Ombre, **Forme d’ombre et Feu intérieur sont actifs pendant 100 % du combat**. Chaque requête contient un seul personnage. Son familier et ses invocations contribuent au DPS du personnage. Les buffs fournis par le raid, le groupe ou un autre joueur sont des réglages du scénario. Les archives conservent les auras, les effets et la race réellement employés. [Simulations historiques](../../_build/corrections/simulated.json) · [Requêtes natives et mesures](protocole-buffs-raid.zip)

## Références historiques des classements DPS

| Spécialisation | Effet personnel observé sur le boss | DPS de la référence |
|---|---|---:|
| Druide Équilibre | Forme de sélénien et Aura de sélénien à 100 %. Le raid a également l’option Aura de sélénien. | 828,5 |
| Chasseur Maîtrise des bêtes | Aspect du faucon VI et Aura de précision à 100 %. Raptor 195,6 DPS, deux faucons invoqués 64,6 et 62,1 DPS. | 1 005,1 |
| Chasseur Précision / Survie | Aspect du faucon VI et Aura de précision à 100 %. Les deux profils prennent Loup solitaire et jouent sans familier. Le moteur applique le multiplicateur du talent au personnage. | 1 071,2 / 1 174,1 |
| Mage Arcane / Feu / Givre | Armure du mage à 100 % dans les trois spécialisations. Les profils incluent aussi des buffs de raid, notamment Intelligence des arcanes. | 808,9 / 938,6 / 811,8 |
| Paladin Vindicte | Aura de vindicte à 100 %. Sceau d’autorité 73,0 % et Sceau de piété 25,9 %. | 931,4 |
| Shockadin | Aura de vindicte à 100 %, Sceau de piété 98,9 %. | 892,6 |
| Prêtre Ombre | Forme d’ombre (15473) et Feu intérieur VI (10952) à 100 %. | 806,0 |
| Voleur Assassinat / Combat / Finesse | Poison instantané VI en main droite et Poison mortel IV en main gauche. Les deux infligent des dégâts dans chaque spécialisation. Débiter actif pendant 91,9 / 92,4 / 95,0 % du temps. | 927,1 / 845,2 / 893,6 |
| Chaman Élémentaire | Totem incendiaire 98,5 %, Fontaine de mana et Furie-des-vents 100 %. Huile de sorcier en main droite. Le bouclier fait l’objet du contrôle ci-dessous. | 796,5 |
| Chaman Amélioration | Arme Furie-des-vents à 100 %, Totem de magma 99,7 %. | 932,3 |
| Démoniste Affliction | Armure du démon et effet du sacrifice de diablotin (18789, *Burning Shadow*) à 100 %. Le preset configure le sacrifice sans démon actif. | 938,9 |
| Démoniste Démonologie | Armure du démon, sacrifice de succube (18791), Lien spirituel et Connaissance démoniaque à 100 %. Le preset Forever configure un diablotin actif, mesuré à 189,8 DPS. | 914,9 |
| Démoniste Destruction | Armure du démon à 100 %, succube active à 63,4 DPS. | 895,7 |
| Guerrier Armes / Fureur | Cri de guerre 98,3 / 98,2 %. Armes combat en Posture de combat. Fureur passe 86,0 % en Posture berserker et 14,0 % en Posture de combat. | 889,9 / 952,0 |

Le rang VII d’Aspect du faucon (25296) s’apprend avec le *Guide: Aspect of the Hawk VII* (21307), qu’attribue ForeverDB à Ossirian dans les Ruines d’Ahn’Qiraj. Le rang VI (14322) correspond au meilleur rang de l’entraîneur dans ce périmètre pré-raid. Les rotations Précision et Survie sélectionnent explicitement Loup solitaire. [Livre de Faucon VII](https://www.wowhead.com/forever/item=21307/) · [Rangs du chasseur dans WoWSims](https://github.com/wowsims/forever/blob/21377c070b5ea111a9bb5e36eb766193270b0cc7/ui/specs/hunter/dps/spec.ts) · [Implémentation de Loup solitaire](https://github.com/wowsims/forever/blob/21377c070b5ea111a9bb5e36eb766193270b0cc7/sim/hunter/talents_marksmanship.go)

## Les boucliers du chaman

Les rotations historiques Élémentaire et Amélioration demandent Bouclier d’eau avant le pull. Aucune des deux répartitions de talents n’apprend ce sort. Les deux requêtes corrigées dans le protocole remplacent cet ordre par Bouclier de foudre VII (10432). Il reste actif sur tout le combat. Le boss frappe le tank extérieur, avec zéro dégât direct du boss au chaman et zéro décharge du bouclier. Les dépenses de vie de certains consommables apparaissent séparément dans les métriques du joueur. [Boucliers dans cette révision du moteur](https://github.com/wowsims/forever/blob/21377c070b5ea111a9bb5e36eb766193270b0cc7/sim/shaman/shields.go)

| Contrôle apparié, 20 000 combats par ligne | Élémentaire | Amélioration |
|---|---:|---:|
| Bouclier de foudre lancé à −5,5 s, Δ DPS ± erreur standard | −0,038 ± 0,254 | −0,458 ± 0,555 |
| Bouclier chargé avant la préparation, mêmes ressources et délais au pull | 20 000 / 20 000 DPS individuels identiques | 20 000 / 20 000 DPS individuels identiques |
| Langue de feu en plus de l’huile prévue, sans frappe de mêlée | 20 000 / 20 000 DPS individuels identiques | Arme Furie-des-vents déjà active |

Le deuxième essai active l’aura native à ses trois charges au début de l’itération. Les décisions de rotation, le mana et les temporisations conservent leur état historique. Cela isole l’effet du bouclier de son coût de préparation. Le build actuel du mode Raid lit les scores archivés. Les requêtes corrigées se trouvent sous `requests/probe/SHAMAN-1-shield.json` et `requests/probe/SHAMAN-2-shield.json` pour rejouer une préparation complète. [Protocole et échantillons vérifiables](protocole-buffs-raid.zip)

## Félin, tanks et soins

| Spécialisation | Périmètre et résultat du rejeu historique |
|---|---|
| Druide Farouche félin | Mains gauches étalonnées derrière *Persuader*, 20 000 combats par faction. Forme de félin 99,14 % pour l’elfe et le tauren. L’ancienne rotation lance une Innervation et reprend une fois la forme. Le test de +40 PA retrouve +9,31477 et +9,24579 DPS. |
| Druide Farouche ours | Forme d’ours redoutable à 100 % sur les deux factions pour les trois duels équipement. |
| Paladin Protection | Aura de vindicte et Fureur vertueuse à 100 %, Sceau de fureur près de 99 %, Bouclier sacré autour de 91 %. Les duels cape et bijou ont été rejoués pour le personnage humain et le réprouvé. |
| Guerrier Protection | Posture défensive près de 98 % et Cri de guerre près de 100 % dans les duels tête et cape, sur l’humain et l’orc. |
| Druide Restauration, Paladin Sacré, Prêtre Discipline, Prêtre Sacré, Chaman Restauration | Les listes de soins n’ont pas de simulation Raid de référence pour classer globalement les pièces. Elles emploient des pondérations et corrections par rôle. Il n’existe pas d’uptime de forme ou de buff à déduire de ces pondérations. |

Les quatorze comparaisons tank (sept duels, deux factions) reproduisent les trois écarts publiés, en DPS, menace/s et dégâts reçus/s. L’ancienne campagne hybride est distincte de la campagne félin permanent employée par des listes livrées plus récentes. [Duels tank historiques](../../_build/tank_options.py) · [Étalonnage félin historique](../../_build/corrections/feral_offhands.json) · [Protocole des huit tenues](protocole-actualise-feral-tanks.zip)

## Ce que les listes installées ajoutent par faction

Les listes Raid du client contiennent 430 lignes de classement, 205 variantes de contexte, 20 lignes de métadonnées et 7 duels tank. Le second protocole rattache les requêtes aux listes effectivement installées. **88 replays** retrouvent le DPS individuel de la tenue enregistré dans les campagnes de publication. Ils couvrent des combats de 2 000 à 20 000 itérations, pour les deux factions. Six contre-épreuves supplémentaires isolent l’effet des boucliers. Les fichiers contiennent la race, la tenue, le partenaire éventuel, l’activation, la rotation, les buffs de groupe et la graine pour chaque exemple. [Requêtes et résultats de livraison](protocole-buffs-raid-livraison.zip)

| Couche de classement | Ce que le rejeu confirme |
|---|---|
| Reclassements par faction de 15 spés et armes du chasseur Maîtrise des bêtes | Les recalages de certains emplacements utilisent les révisions 3289d831, 56473177 et 07648faf. Les profils de chasseur Précision et Maîtrise des bêtes ont aussi été rejoués avec un partenaire d’arme. Le chasseur porte Faucon VI dans les deux factions. Le prêtre possède Forme d’ombre et Feu intérieur à 100 % sur l’humain comme sur le réprouvé. |
| Bijoux de dix profils offensifs et reliques à score DPS de cinq profils | Révision 8f0e65e5, requêtes réelles de chaque faction. Armure du mage, Forme de sélénien, auras paladin, armure et sacrifices du démoniste suivent les profils. En Affliction, le sacrifice de diablotin est actif à 100 %. En Démonologie, le sacrifice de succube, le Lien spirituel et le diablotin actif sont présents. Les reliques de soin ont un ordre de recommandation sans colonne DPS native. |
| Torses Mage Arcane/Givre et armes du druide Équilibre | Le contrôle des deux factions retrouve Armure du mage avec les torses (ceb0e99b) et Forme de sélénien avec les armes (07648faf). |
| Félin | Les campagnes de bijoux (07648faf) et de reliques DPS (8f0e65e5) maintiennent la forme pendant 100 % du combat. La calibration de la main gauche livrée (3289d831) donne 99,14 % et retrouve le gain de +40 PA des deux populations. Le contrôle spécifique de *Blackhand Doomsaw* (07648faf) donne 99,03 à 99,08 % avec son propre profil. |
| Tanks | Les sept lignes de duel installées sont celles du protocole a73af714 vérifié ci-dessus. La sélection pré-raid de main droite du paladin Protection inclut aussi une priorité éditoriale. La liste standard installée ajoute l’objet 19168 avec un score de 1601 aux entrées de la release 1.9.5. Les 42 autres entrées de cette main droite gardent leurs scores. |

Le registre DPS historique utilise une seule tenue et une seule race de référence par spécialisation. Le Chaman Amélioration illustre la limite de cette convention. Le registre indique « h » pour la sélection de l’équipement, mais la requête native emploie un nain. Les recalages ultérieurs pour le torse, les épaules, les poignets, la taille et les bijoux utilisent bien un nain en Alliance et un orc en Horde. Les fiches de chaque camp filtrent également les pièces selon leur obtention. [Fiche de faction Amélioration](shaman-enhancement.md) · [Vérificateur des variantes livrées](../../_build/audit_raid_delivery.py)

Sur les entrées publiées de chaque faction, ajouter Bouclier de foudre à pleine charge avant la préparation reproduit **12 000 / 12 000 DPS individuels** pour les trois campagnes contrôlées (bijoux et reliques Élémentaire, substitution d’armure Amélioration). Elles s’ajoutent aux 40 000 tirages identiques des deux tenues historiques. Le témoin reçoit les mêmes buffs et possède les mêmes ressources. Le compteur des dégâts du boss au joueur et celui des décharges du bouclier valent zéro dans ces six essais.

## Rejeu

Exécuter `python _build/audit_raid_buffs.py` pour vérifier hors ligne les requêtes, les références d’équipement, les profils des notes de comparaison, les duels et la présence des effets cités. Pour rejouer les combats, passer `--dps-engine <checkout-21377c070b>` et `--tank-engine <checkout-a73af71451>`. Les deux checkouts doivent contenir les protobuf Go demandés par WoWSims et ses bases embarquées. Le programme compile pour amd64, restitue les résultats natifs et contrôle les empreintes des séries individuelles. L’option `--prefix probe/` limite le rejeu aux contre-épreuves chamans. [Script](../../_build/audit_raid_buffs.py) · [Moteur DPS historique](https://github.com/wowsims/forever/tree/21377c070b5ea111a9bb5e36eb766193270b0cc7) · [Moteur historique des duels](https://github.com/wowsims/forever/tree/a73af7145111ce19c621e3b5f678553adf326907)


Pour vérifier les couches de livraison, exécuter `python _build/audit_raid_delivery.py`. L’option `--release <checkout-EasyBIS-1.9.5>` vérifie aussi les empreintes des registres correctifs sources. Pour le rejeu complet, fournir une fois `--engine <révision>=<chemin>` pour chacune des révisions 3289d831, 56473177, 07648faf, 8f0e65e5 et ceb0e99b. La commande `python _build/audit_raid_delivery.py --export-shaman <dossier>` produit aussi les six entrées des pilotes avec le sort appris, Bouclier de foudre VII, dans la préparation. Les pilotes et leurs adaptations d’origine sont inclus dans le protocole. [Vérificateur](../../_build/audit_raid_delivery.py) · [Protocole de livraison](protocole-buffs-raid-livraison.zip)
