# EasyBIS · audit des équipements au 22 novembre 2026

Le contrôle du 25 novembre recense les objets écartés par le filtre de provenance et les sources depuis observées dans ForeverDB. [Inventaire des objets masqués](sources-inconnues.md)

La revue des classements du 25 novembre couvre aussi le catalogue Raid, PvP et AoE actuel, avec de nouveaux duels sur les effets de toucher et de proc. [Résultats de la revue](classements-2026-11-25.md)

Les **29 spécialisations** et les **deux modes** du catalogue livré ont été examinés. Avant correction, le registre comportait **25 674 combinaisons objet, spécialisation, mode et emplacement**, variantes de faction comprises (3 183 identifiants). Après correction, il en compte **25 811**, soit 12 037 en PvE et 13 774 en JcJ, pour **3 194 objets distincts**. Les 22 486 entrées de classement Lua se dédoublent lorsqu’une faction porte un autre identifiant. 163 combinaisons sont conservées en réserve par le générateur sans apparaître dans les configurations de jeu parcourues.

**Campagne sur le simulateur du 21 novembre.** Le détail des tests par faction, des changements de premier choix et des résultats indécis accompagne les lignes des 29 fiches. [Résultats sur WoWSims à jour](campagne-wowsims.md) · [Druide félin et trois tanks](controle-actualise-feral-tanks.md)

**Pour consulter une pièce**, ouvrir la fiche de la spécialisation ci-dessous et chercher son nom ou son ID. Chaque fiche commence par les premiers choix disponibles en pré-raid pour les deux factions, puis compare les objets emplacement par emplacement. Les trois analyses de classe expliquent les choix de priorités ainsi que les écarts importants. [Guerrier, voleur, chasseur](physiques.md) · [Mage, démoniste, prêtre](magie.md) · [Druide, chaman, paladin](hybrides.md)

L’audit a commencé sur `95570fe` (28 spés) et intègre les changements de `main` `af5c74c`, dont le Shockadin (29ᵉ spé), puis la révision `06d4202` qui porte son coefficient d’armure JcJ de 0,02 à 0,05. La PR nº 6 apportait déjà les restrictions de classe, la PA du chasseur, les dagues du voleur, Main de justice et la fiche du bâton de Valthalak. Les corrections de filtres, blocage, toucher réservé aux tirs, mesures de la chope et des capes, ainsi que les contrôles ci-dessous ont été vérifiés sur ce socle. [PR nº 6](https://github.com/jBeyondstars/EasyBIS/pull/6) · [Audit du Shockadin](shockadin.md)

## Corrections qui changent le choix en jeu

- **Restrictions de classe intégrées par la PR nº 6.** Sur la révision 95570fe qui précédait la PR, 749 anciennes propositions associaient une pièce ou sa variante de faction à une classe qui ne pouvait pas l’obtenir ou la porter. Les pièces Bonescythe d’une quête de voleur en sont un exemple. Une pièce de cuir figurant dans les fichiers du jeu ne devient pas automatiquement accessible au chasseur ou au druide. [Restrictions et provenance](../../_build/corrections/classes.json) · [Registre des retraits](retraits.md)
- **Faction d’obtention.** Douze récompenses liées à leur vendeur d’honneur et sept récompenses liées à une quête de l’Alliance apparaissent désormais pour la faction qui peut les obtenir. Les vérifications restantes et leurs limites figurent dans le relevé. [Objets et sources](factions.md)
- **Guerrier Armes JcJ.** Le score des deux-mains compte le jet de dégâts de Frappe mortelle. Au plafond de rang 6, Blade of Hanna passe de la 4ᵉ à la 45ᵉ place pré-raid, et la Déchireuse en arcanite passe de la 11ᵉ à la 3ᵉ place. Les épaulières en mailles d’Arathi du chaman respectent désormais les deux factions. [Mesures des coups en JcJ](armes-jcj.md)
- **Chaman Amélioration.** Sulfuron Hammer demandait huit lingots de sulfuron issus du Cœur du Magma. Forest Defender’s Axe passe en tête du pré-raid à **383 DPS** dans le profil embarqué. Les récompenses de quêtes de la vallée d’Alterac, dont Ice Barbed Spear, respectent aussi le filtre JcJ. [Détail du chaman](hybrides.md)
- **Démonistes.** Lapidis Tankard remontait dans les recommandations parce que le moteur activait sa boisson en combat. En neutralisant cette activation, sa valeur passe de **16 à 1,5 DPS en Affliction** et de **16,5 à 3,5 en Destruction**. La chope quitte les listes affichables. En Destruction, Sandstorm Cover reprend sa place devant Glowing Thresher Cape : **4 contre 3 DPS** après vérification contre un emplacement vide. La capture du bâton de Valthalak rétablit également ses **72 de puissance des sorts**. [Contre-mesures et comparaison des références](magie.md)
- **Chasseurs et voleurs.** La puissance d’attaque générale du chasseur contribue à ses tirs. Le toucher réservé aux tirs de Trueaim Gauntlets est désormais distingué du toucher de mêlée. En Précision, changer les jambières inverse l’ordre entre Trueaim et les gants du diablosaure. La paire de dagues du profil JcJ Assassinat respecte les armes demandées par Estropier. [Profils physiques](physiques.md)
- **Tanks.** Les 301 boucliers du catalogue prennent désormais en compte leur valeur de blocage intrinsèque en plus de l’éventuel bonus explicite. Evergreen Shield apporte 44 de blocage et 2 468 d’armure sur son infobulle Forever. WoWSims lui donne 58 de blocage. Cette divergence est signalée sur les lignes de contrôle. L’évaluation compare aussi les dégâts reçus et la menace pour le guerrier, le paladin et l’ours. [Données de blocage](../../_build/corrections/shields.json) · [Protocole des tanks](controles.md)
- **Druide félin.** En comparant les pièces directement, Legionite Glaive garde **5,19 DPS** d’avance sur Bonecrusher. Avec une masse à une main, Scepter of Interminable Focus devance Tome of Knowledge de **2,71 DPS en Alliance et 3,12 en Horde** avec la masse 11923 sur les tenues pré-raid. Une seconde campagne portant sur tout l’emplacement donne aussi l’avantage au sceptre avec Persuader. La main gauche PvE du félin applique désormais les mesures ramenées à l’échelle des autres armes grâce à un contrôle de +40 PA pour chaque faction. [Protocole spécifique](protocole-main-gauche-felin.zip) [Comparaisons par faction](controle-actualise-feral-tanks.md)
- **Info des objets.** 67 notes bilingues ont été ajoutées ou révisées par rapport à `main` `06d4202`. Ces notes documentent notamment les effets activables, la cible, l’arme, le set et le toucher. Le générateur ajoute aussi des notes de repli ciblées lorsqu’un effet ou sa fréquence manque au moteur. [Notes des objets](../../_build/corrections/notes.json)
- **Comparaisons dans l’info des objets.** 1 983 annotations additionnelles nomment la pièce rivale, le gain ou la perte de DPS mesuré, le résultat du transfert des statistiques fixes et, selon le cas, l’incertitude de l’essai. Elles sont limitées à la spécialisation, au mode PvE et à l’emplacement réellement testés. [Source des comparaisons](../../_build/corrections/comparisons.json)

## Fiches par spécialisation

| Spécialisation | Lignes PvE | Lignes JcJ | Mesures embarquées directes¹ | Contrôles supplémentaires² | Présences dans le guide pré-raid³ |
|---|---:|---:|---:|---:|---:|
| [Druide · Équilibre](druid-balance.md) | 370 | 460 | 316 | 0 | 43 |
| [Druide · Farouche (ours)](druid-feral-bear.md) | 497 | 487 | 0 | 482 | 29 |
| [Druide · Restauration](druid-restoration.md) | 350 | 428 | 0 | 0 | 33 |
| [Druide · Farouche (félin)](druid-feral-cat.md) | 421 | 488 | 0 | 376 | 32 |
| [Chasseur · Maîtrise des bêtes](hunter-beast-mastery.md) | 505 | 559 | 392 | 0 | 38 |
| [Chasseur · Précision](hunter-marksmanship.md) | 504 | 558 | 390 | 0 | 36 |
| [Chasseur · Survie](hunter-survival.md) | 409 | 459 | 325 | 0 | 31 |
| [Mage · Arcanes](mage-arcane.md) | 403 | 456 | 336 | 0 | 49 |
| [Mage · Feu](mage-fire.md) | 397 | 449 | 327 | 0 | 47 |
| [Mage · Givre](mage-frost.md) | 398 | 451 | 328 | 0 | 48 |
| [Paladin · Sacré](paladin-holy.md) | 373 | 454 | 0 | 0 | 37 |
| [Paladin · Protection](paladin-protection.md) | 479 | 489 | 0 | 443 | 26 |
| [Paladin · Vindicte](paladin-retribution.md) | 377 | 425 | 306 | 0 | 31 |
| [Paladin · Shockadin](paladin-shockadin.md) | 367 | 448 | 293 | 0 | 0 |
| [Prêtre · Discipline](priest-discipline.md) | 392 | 464 | 0 | 0 | 42 |
| [Prêtre · Sacré](priest-holy.md) | 389 | 457 | 0 | 0 | 37 |
| [Prêtre · Ombre](priest-shadow.md) | 380 | 458 | 309 | 0 | 47 |
| [Voleur · Assassinat](rogue-assassination.md) | 425 | 482 | 331 | 0 | 37 |
| [Voleur · Combat](rogue-combat.md) | 445 | 517 | 348 | 0 | 36 |
| [Voleur · Finesse](rogue-subtlety.md) | 454 | 515 | 348 | 0 | 39 |
| [Chaman · Élémentaire](shaman-elemental.md) | 383 | 503 | 324 | 0 | 43 |
| [Chaman · Amélioration](shaman-enhancement.md) | 373 | 431 | 311 | 0 | 31 |
| [Chaman · Restauration](shaman-restoration.md) | 383 | 457 | 0 | 0 | 36 |
| [Démoniste · Affliction](warlock-affliction.md) | 403 | 456 | 329 | 0 | 45 |
| [Démoniste · Démonologie](warlock-demonology.md) | 408 | 462 | 331 | 0 | 47 |
| [Démoniste · Destruction](warlock-destruction.md) | 406 | 457 | 332 | 0 | 45 |
| [Guerrier · Armes](warrior-arms.md) | 403 | 466 | 326 | 0 | 31 |
| [Guerrier · Fureur](warrior-fury.md) | 464 | 527 | 376 | 0 | 35 |
| [Guerrier · Protection](warrior-protection.md) | 479 | 511 | 0 | 448 | 28 |

¹ Les **20 profils DPS** embarqués utilisent la révision WoWSims `21377c070b`, un combat monocible de 180 s et 20 000 itérations. La colonne compte 6 678 lignes où l’ID présenté correspond à l’ID mesuré, hors effet explicitement absent, fréquence supposée, estimation ou placement manuel. Les simulations utilisent une race et une tenue de référence. Le compte porte sur les lignes des fiches, pas sur les combats. [Archive et références](../../_build/corrections/simulated.json)

² Le félin et les trois tanks ont fait l’objet de **1 754 substitutions supplémentaires réussies** à 2 000 itérations sur les identifiants testables, avec des comparaisons ciblées à 20 000 itérations. Ces essais sont des contrôles distincts du barème que l’addon emploie pour ces quatre spés. Les cinq profils de soin n’ont aucune rotation de soin étalon dans cette version du moteur. Les listes JcJ utilisent leurs propres poids. Les colonnes de simulation restent vides dans ces cas. [Mesures supplémentaires](controles.md) · [Vérification des rotations de soin](hybrides.md)

³ Les **56 fiches Forever BiS** des deux factions ont été lues pour les 28 spécialisations que ce guide couvre. Le Shockadin possède sa propre [analyse Holy Shock](shockadin.md). La colonne compte les objets également proposés dans la sélection numérotée du guide pour la faction du contexte affiché. Sa sélection privilégie le pré-raid et sépare notamment certains objets difficiles à obtenir. Les références, les buffs et les candidats diffèrent de ceux d’EasyBIS. Pour un DPS, le chiffre entre parenthèses est l’écart au meilleur objet de ce guide. Pour un tank, c’est l’écart de son indice de menace/survie. Pour un soigneur, c’est un rang sur une autre pondération. Un tiret signifie que l’objet ne figurait pas dans cette sélection pour cette faction. [Méthode du guide](https://foreverbis.net/about/)

## Comment lire une ligne

1. **Lire les stats avant le sim.** Le score sur fiche est la somme des statistiques multipliées par les poids publiés pour le profil. Les poids et la fiche de l’objet sont donnés dans chaque section. Les ajouts du modèle de base, par exemple une quote-part de set, sont signalés. Le barème félin provient des poids statistique par statistique publiés par WoWSims. Cette étape ne consulte pas le résultat de substitution de l’objet. Les points de pondération ne sont pas des DPS. [Source des statistiques](https://foreverdb.net/bis) · [Profils et adaptations](../../_build/specs.py)
2. **Comparer à population égale.** Le rang stats couvre les concurrents admis du même emplacement, de la même configuration de filtres et du même type de main droite (une ou deux mains). Le rang du sim embarqué ne couvre que les concurrents dotés d’un score propre dans son archive. Si les deux ordres divergent, la décision donne le rang stats recalculé sur ces concurrents mesurés ou un rival qui inverse l’ordre. Les ex æquo de score ont le même rang. Le moteur embarqué arrondit au demi-DPS. Pour les nouveaux essais félins, le rang ne couvre que les propositions testées, avec leur erreur standard.
3. **Vérifier l’écart.** Une info de proc, un essai avec et sans activation ou un essai apparié permet d’isoler certaines causes. Sur les armures et bijoux sans effet, sans set, sans suffixe et sans supplément de stats, un ajustement linéaire local par spé et emplacement aide à expliquer les inversions. Ses coefficients sont estimés sur les mesures, avec validation croisée en cinq groupes. Une attribution n’est publiée que si les erreurs et l’écart entre les deux objets le permettent. Elle décrit une contribution plausible. Là où les données ne permettent pas d’isoler une cause, le rapport le dit. Un astérisque ou la mention « jumeau » qualifie une mesure partielle ou transposée.
4. **Vérifier l’accès et la place en jeu.** Chaque ligne donne un exemple de filtres où l’objet apparaît, avec jusqu’à six alternatives. « Alt. 1 » désigne la première alternative après le ou les BiS, et « autre » le style d’arme alternatif. Les deux premiers anneaux ou bijoux doivent pouvoir être portés ensemble. Le tableau de synthèse utilise le rang maximum 6 de la semaine avec les récompenses JcJ exclues en PvE. Dans le registre complet, le plafond n’est appliqué que s’il est indiqué. « JcJ+ » ajoute les récompenses en PvE, « JcJ− » les écarte en JcJ et « vus » exige une observation en jeu. Le registre privilégie le pré-raid et les options habituelles, puis cherche un exemple parmi les autres combinaisons de faction, phase, visibilité, plafond et sources.
5. **Interpréter la phase.** « Pré » signifie qu’EasyBIS classe la pièce avant les raids. « P1 » correspond à la première phase de raid, annoncée pour le **9 décembre 2026**. « Archives » couvre notamment les pièces d’anciens raids Classic, les pièces ajoutées sans source certaine et les options de projection. Un classement dans cette phase n’établit pas une possibilité de farm actuelle. Les sources issues de Classic et les objets à suffixe restent identifiés dans les données. [Calendrier de Blizzard](https://worldofwarcraft.blizzard.com/en-us/news/24303862/world-of-warcraft-forever-whats-next-panel-recap) · [Définition des phases](../../_build/phases.py)

## Portée et décisions en suspens

Les 31 anciennes combinaisons qui quittent les listes sont détaillées dans une annexe. 168 combinaisons entrent dans les places conservées après recalcul. Les retraits incluent les variantes de faction. L’annexe donne la pièce qui occupe désormais la place dans les mêmes conditions de jeu. [Anciennes propositions et motifs](retraits.md)

**Tenues de référence.** Les anciennes simulations Horde de Guerrier Armes et Fureur, des trois chasseurs et du Chaman Amélioration portaient une ou deux pièces de Theramore réservées à l’Alliance. Leurs anciennes mesures sont conservées avec cette réserve. Les nouveaux essais remplacent les pièces indisponibles préalablement à la comparaison. Les identifiants sont donnés sur les six fiches. Les nouvelles variantes à une main de l’Équilibre et des chasseurs portent aussi un enchantement compatible avec leur type d’arme. [Restrictions de faction dans les données WoWSims](https://github.com/wowsims/forever/tree/a73af7145111ce19c621e3b5f678553adf326907/assets/database)

Une place peut être validée pour un profil de dégâts précis tout en restant conditionnelle au toucher, à la composition d’un set, à l’usage d’un bijou ou au type de cible. Pour les soins et le JcJ, l’examen valide la cohérence avec les priorités affichées et identifie les effets oubliés. Il ne produit pas de classement HPS ni de probabilité de victoire. La position entre deux performances trop proches est signalée comme indéterminée dans les analyses.

Le registre couvre les objets livrés avec EasyBIS. Certains équipements extérieurs au catalogue, notamment les reliques des hybrides et Wolfshead Helm, limitent la portée d’une affirmation de BiS absolu. Le casque a été ajouté au contrôle félin comme témoin extérieur. Les objets personnels ajoutés par un joueur dépendent de ses sauvegardes. [Lacunes identifiées](hybrides.md) · [Contrôle du casque](controles.md)

**Data from ForeverDB.net (https://foreverdb.net)**, version des données de l’addon 2026-11-17.f52e5099, build 1.60.1.70938, avec les captures et les corrections du projet. WoWSims Forever est distribué sous licence MIT. [Crédits et licences](../../NOTICE.txt)

**Contre-épreuves des inversions.** 2 005 lignes ont fait l’objet d’essais supplémentaires sur le moteur. Pour les 18 premiers ou seconds BiS pré-raid les moins évidents, chaque configuration a été jouée 5 000 fois. Sur l’ensemble des fiches, 1 022 comparaisons supplémentaires ne départagent pas les concurrents à deux erreurs standard. Pour 172 lignes une part du différentiel subsiste après transfert des stats et sa mécanique exacte reste ouverte. [Tableau des 18 choix pré-raid et protocole](inversions.md) · [Toutes les contre-épreuves](inversions-wowsims.json)

Les alertes automatiques de niveau et de très forte avance ont été relues séparément. [Objets signalés par le générateur](alertes.md)

**Version du simulateur.** Les chiffres ci-dessus utilisent `21377c070b` du 20 novembre. Le 22 novembre, la branche `master` de WoWSims Forever pointait sur `a73af71451`, 138 commits plus loin. Les contrôles de la nouvelle version sont identifiés séparément. [Vérification de version et portée des changements](version-wowsims.md) · [Comparaison amont](https://github.com/wowsims/forever/compare/21377c070b...a73af71451)
