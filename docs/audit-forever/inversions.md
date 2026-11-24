# Inversions contrôlées par substitution

Les cas ci-dessous faisaient partie des premiers choix pré-raid et restaient inexpliqués après lecture du barème, des seuils de toucher et des effets connus. Chaque essai compare les deux pièces équipées, puis garde la pièce rivale en lui donnant les statistiques fixes de l’autre. Des essais supplémentaires font varier un seul attribut. Le différentiel inclut les interactions de la rotation et de la tenue. [Retour au rapport](README.md) · [Résultats de toutes les comparaisons](inversions-wowsims.json)

| Profil | Objet | Rival | Δ DPS des pièces ± erreur standard | Δ DPS des stats fixes seules | Lecture |
|---|---|---|---:|---:|---|
| HUNTER Marksmanship | Bracers of the Eclipse | Marksman Bands | 2,55 ± 0,34 | 5,46 | Les stats fixes expliquent une partie du résultat. Les propriétés propres aux objets contribuent aussi. |
| MAGE Arcane | Oblivion's Touch | Wand of Arcane Potency | 0,70 ± 0,21 | 0,70 | Le transfert des stats reproduit l’essentiel de la différence. |
| MAGE Fire | Fire Striders | Sorcerer's Sandals | 0,09 ± 0,41 | 0,09 | Ordre indéterminé à deux erreurs standard. |
| MAGE Fire | Bonecreeper Stylus | Pyric Caduceus | -0,18 ± 0,25 | -0,18 | Ordre indéterminé à deux erreurs standard. |
| MAGE Frost | Riptide Shoes | Sorcerer's Sandals | 0,16 ± 0,31 | 0,16 | Ordre indéterminé à deux erreurs standard. |
| PALADIN Retribution | Mantle of the Timbermaw | Theramore Pauldrons | 0,90 ± 0,09 | 0,90 | Le transfert des stats reproduit l’essentiel de la différence. |
| PALADIN Retribution | Tranquil Wristguards | Vambraces of the Sadist | 0,38 ± 0,08 | 0,38 | Le transfert des stats reproduit l’essentiel de la différence. |
| PRIEST Shadow | Gloves of Spell Mastery | Virtuous Hands | 7,04 ± 0,30 | 6,98 | Le transfert des stats reproduit l’essentiel de la différence. |
| PRIEST Shadow | Obsidian Bauble | Book of the Dead | 1,96 ± 0,19 | 1,96 | Le transfert des stats reproduit l’essentiel de la différence. |
| SHAMAN Enhancement | Warden's Signet of Ferocity | Channeler's Ring | -2,81 ± 1,10 | -2,81 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARLOCK Affliction | Mantle of the Timbermaw | Felcloth Shoulders | 4,39 ± 0,30 | 4,39 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARLOCK Affliction | Omnicast Boots | Black Sandals | 1,02 ± 0,16 | 1,02 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARLOCK Affliction | Obsidian Bauble | Spirit of Aquementas | 1,18 ± 0,27 | 1,18 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARLOCK Demonology | Sublime Wristguards | Necropile Cuffs | 4,86 ± 0,14 | 4,86 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARLOCK Destruction | Omnicast Boots | Fire Striders | 3,40 ± 0,54 | 3,40 | Le transfert des stats reproduit l’essentiel de la différence. |
| WARRIOR Fury | Persuader | Ironwood Blade | 23,02 ± 0,94 | 5,87 | Les stats fixes expliquent une partie du résultat. Les propriétés propres aux objets contribuent aussi. |
| PALADIN Shockadin | Mantle of the Timbermaw | Ironfeather Shoulders | 4,74 ± 0,21 | 4,74 | Le transfert des stats reproduit l’essentiel de la différence. |
| PALADIN Shockadin | Dawn Armor | Robes of Dark Summons | 4,22 ± 0,38 | 4,22 | Le transfert des stats reproduit l’essentiel de la différence. |

Ces 18 comparaisons utilisent 5 000 itérations par configuration. Les autres comparaisons exploratoires utilisent 500 itérations et servent à distinguer les effets mesurables des ordres trop serrés. Les deux bijoux ou les deux anneaux sont vidés avant de tester une pièce. La graine commune est 4242. Les effets déclenchés, les ensembles, les statistiques spéciales, le type, la vitesse et les dégâts propres de l’arme restent ceux de la pièce rivale pendant le transfert. Les effets des changements individuels ne sont pas forcément additifs. En Destruction, les contrôles des inversions reprennent la référence archivée ; la sensibilité à la correction de la chope est étudiée séparément. [Analyse Destruction](magie.md)


## Vérification des inversions de signe

Sept lignes ont fait l’objet d’une vérification après un changement de signe à 500 combats. Trois comparaisons de mains gauches de Finesse, dont une parmi ces sept, ont aussi été rejouées avec Heartseeker en main droite après vérification des mains autorisées. Les résultats ci-dessous proviennent de **20 000 combats à graine indépendante, 4243**. Les deux différences sont orientées de la pièce rivale vers la pièce examinée. La différence archivée est calculée à partir des deux scores arrondis au demi-DPS avant ces contre-épreuves. Un score effectivement corrigé depuis cette comparaison apparaît dans la fiche de la spécialisation. Une arme peut déclencher un effet différent selon l’arme portée dans l’autre main.

| Profil | Pièce | Rivale | Δ archivé | Δ au nouveau test ± erreur standard |
|---|---|---|---:|---:|
| HUNTER Marksmanship | Lefty's Brass Knuckle | Tunnelweb Pincer | 0,50 | -0,42 ± 0,03 |
| MAGE Fire | Blackwater Cap | Electromagnetic Gigaflux Reactivator | 0,50 | 0,30 ± 0,19 |
| PRIEST Shadow | Don Mauricio's Band of Domination | Songstone of Ironforge | 1,00 | 0,86 ± 0,23 |
| ROGUE Subtlety | Shadowsong's Sorrow | Felstriker | -0,50 | 4,06 ± 0,30 |
| SHAMAN Elemental | Burrower Bracers | Wristguards of Elemental Fury | 0,50 | 0,34 ± 0,15 |
| SHAMAN Elemental | Wristguards of Elemental Fury | Burrower Bracers | -0,50 | -0,34 ± 0,15 |
| WARLOCK Destruction | Glowing Thresher Cape | Sandstorm Cover | 0,50 | -0,77 ± 0,00 |
| ROGUE Subtlety | Felstriker | Bonescraper | 4,00 | -0,73 ± 0,30 |
| ROGUE Subtlety | Bonescraper | Felstriker | -4,00 | 0,73 ± 0,30 |

- **Destruction.** Sandstorm Cover donne 4 de dégâts des sorts contre 3 pour Glowing Thresher Cape. Le transfert de ce point reproduit l’écart. Le contrôle contre le dos vide sur la référence corrigée donne 3,81 et 3,04 DPS. Les scores intégrés sont désormais 4 et 3. [Protocole et mesures](magie.md)
- **Précision.** Avec Sageblade, Tunnelweb Pincer devance Lefty’s Brass Knuckle. La sélection des armes à une main du profil retrouve Shadowblade comme référence. Avec cette dague, Lefty’s reprend 0,32 DPS, ce qui confirme l’ordre affiché dans ce profil. [Contrôle du choix de main droite](physiques.md)
- **Finesse.** Les trois contrôles de mains gauches utilisent Heartseeker comme main droite commune. Les mesures initiales de ces paires avec Distracting Dagger en main droite ont été écartées, car cette arme est réservée à la main gauche. Les marges de l’archive peuvent employer une main droite différente lorsque l’objet testé serait porté deux fois. [Comparaison de mains droites légales](physiques.md)
