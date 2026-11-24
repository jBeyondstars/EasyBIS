# Les 52 alertes du générateur

Au 22 novembre 2026, **28 lignes de niveau bas concernent huit objets**, et **24 lignes de forte avance en concernent huit autres**. Les 16 identifiants sont distincts. Le contrôle parcourt les deux factions et les phases 0, 1 et 9, avec source connue, sans filtre « vu en jeu », avec les récompenses JcJ admises et sans plafond de grade. Cette dernière condition permet aussi des comparaisons avec d’anciennes récompenses JcJ. Les rangs ci-dessous décrivent les scénarios ayant déclenché l’alerte. [Règles du contrôle](../../_build/audit.py)

### Niveau requis inférieur à 45

| Objet (ID) | Lignes | Verdict |
|---|---:|---|
| Flurry Axe (871), niveau 42 | 1 | Main gauche du Voleur Combat, 1re ou 2e suivant le scénario. L’attaque supplémentaire est documentée dans les journaux Forever. Elle explique qu’une hache de 35,3 DPS apparaisse à ce rang. [Mesure de la fréquence de déclenchement](https://github.com/wowsims/forever/blob/21377c070b/docs/evidence/EV-0120-flurry-axe-rate-from-log-order.md) |
| Stormcloth Vest (10020), niveau 40 | 9 | 58 soins, 8 Esprit et 8 Endurance. Premier torse des profils pondérés Paladin Sacré et Chaman Restauration en JcE, 1er ou 2e en JcJ Druide Restauration. Alternative pour les autres lignes de soin. [Fiche Forever](https://foreverdb.net/item/10020) |
| Skibi’s Pendant (13089), niveau 44 | 1 | 3e collier du félin en pré-raid. Les 13 Agilité et 5 Force valent 11,48 points, contre 13,43 pour Mark of Fordring. [Fiche Forever](https://foreverdb.net/item/13089) |
| Cassandra’s Grace (13102), niveau 42 | 3 | 3e tête de Druide Restauration, Prêtre Discipline et Chaman Restauration dans ce contrôle JcE. Ses 44 soins, 9 Esprit et 7 Endurance justifient une alternative malgré le niveau. [Fiche Forever](https://foreverdb.net/item/13102) |
| Gloves of the Greatfather (17721), niveau 33 | 2 | 2es en Équilibre (+26 DPS) et Élémentaire (+30). Les gants réunissent 24 dégâts des sorts et 10 dégâts de Nature. Ils suivent de 0,5 DPS le premier de chaque profil. [Fiche Forever](https://foreverdb.net/item/17721) |
| Forest Stalker’s Bracers (19590), niveau 40 | 1 | 3es aux poignets du félin en phases 0 et 1. Les versions de niveau 60 (19587) et 50 (19589) du même vendeur les devancent. Cette version offre encore 14 Agilité et 8 Force. [Fiche Forever](https://foreverdb.net/item/19590) |
| Dryad’s Wrist Bindings (19597), niveau 40 | 9 | 3es de neuf profils de dégâts magiques. Les versions 60 (19595) et 50 (19596) passent devant. Les 16 puissance et 6 Intelligence restent utilisables. Ces deux séries de poignets supposent que les récompenses de champ de bataille sont autorisées. [Fiche Forever et vendeurs observés](https://foreverdb.net/item/19597) |
| Beastslayer’s Trident (279910), niveau requis enregistré 1 | 2 | Classé **2e** en Maîtrise des bêtes et Précision. L’objet est de niveau d’objet **62**, avec 26 Agilité, 16 toucher et un bonus de PA contre les bêtes. La quête d’Alliance enregistrée par EasyBIS exige le niveau **55**. Le niveau technique de port n’est donc pas le niveau auquel on obtient la récompense. [Fiche de l’objet](https://foreverdb.net/item/279910) · [Quêtes par faction](https://infinitysims.org/items/beastslayers-trident-279910/) |

### Plus de 40 % d’écart

Le pourcentage représente la part du score du premier perdue en équipant l’alternative, soit **(premier − alternative) / premier**. Pour un emplacement double, le contrôle compare le dernier des deux meilleurs au premier remplaçant.

| Objet (ID) | Lignes | Verdict |
|---|---:|---|
| Stormshroud Pants (15057), Shoulders (15058), Gloves (21278) | 9 | Chacun est premier dans les trois profils JcE du Voleur. Les écarts sont de 51–73 % pour les jambes, 66–82 % aux épaules et 67–82 % aux mains dans les comparaisons signalées. La référence porte les deux autres pièces et chaque substitution active le troisième bonus (4 % pour 30 points d’énergie dans l’archive, 3 % pour 18 après le correctif du 20 novembre). Ne pas additionner trois fois ce bonus. [Contrôles par spécialisation](physiques.md) · [Correctif Blizzard](https://worldofwarcraft.blizzard.com/en-us/news/24315281/wow-forever-hotfixes-november-20-2026) |
| Arcanoweave Cloak (272411) | 7 | Première en Équilibre, Arcanes, Feu, Givre, Élémentaire, Démonologie et Destruction. Les 16 puissance, 10 toucher et 8 Intelligence expliquent son avance dans les profils de référence. Exemple pré-raid en Givre, +22 DPS contre +10,5 pour Hide of the Wild. Comparer avec le toucher déjà porté. [Objet et vendeur observé](https://foreverdb.net/item/272411) |
| Cloak of the Fallen God (21710) | 1 | Première en JcE félin uniquement en **phase 9**, qui inclut le contenu Classic sans date Forever annoncée. Ses 26 Agilité et 11 Force expliquent presque intégralement les 23,56 points, contre 12,73 pour Blackveil Cape. La quête dépend de C’Thun. [Source de quête](https://foreverdb.net/item/21710) |
| Atiesh démoniste (22630) | 1 | Arme JcE Affliction de phase 9, +203 DPS contre +118,5 pour Ironbark Staff dans le cas Alliance. 150 puissance et 28 critique permanents, avec une aura de puissance mentionnée sur la fiche. [Variante démoniste](https://foreverdb.net/item/22630) |
| Atiesh prêtre (22631) | 4 | Premier bâton des prêtres Discipline et Sacré en JcE et JcJ, phase 9. Le modèle additionne 120 puissance polyvalente et 180 soins. En Discipline JcE cela donne 331,75 points avec les caractéristiques de base, contre 158,10 pour Argent Crusader. [Variante prêtre](https://foreverdb.net/item/22631) |
| Atiesh druide (22632) | 2 | Premier en Restauration JcE et JcJ, phase 9. Les 300 soins permanents dominent le score. En JcE, 330,30 points contre 158,60 pour Redemption. Ces trois variantes d’Atiesh se lisent comme projections de raid et n’entrent pas dans les pré-BiS actuels. [Phases des quêtes d’Atiesh](../../_build/phases.py) |

Les caractéristiques et les effets connus soutiennent le maintien des 16 objets dans ces conditions. Les trois réserves importantes concernent le seuil du set Stormshroud, l’accès réel au trident et l’ouverture des anciens raids.
