# Guerrier Armes JcJ · Blade of Hanna et dégâts des armes à deux mains

**Blade of Hanna passe du 4e au 45e rang et la Déchireuse en arcanite du 11e au 3e rang.** Ces positions valent en pré-raid, au niveau 60, en Alliance comme en Horde, avec les sources connues, les récompenses JcJ autorisées jusqu’au grade 6 et le filtre « vu en jeu » désactivé. Le résultat s’explique dès le premier coup. Avec le même Guerrier, une Frappe mortelle critique inflige en moyenne **684 dégâts avec Hanna, contre 825 avec la Déchireuse**. [Mesures et configurations](armes-jcj-wowsims.json)

## Ce que fait l’arme sur le premier coup

Hanna affiche 60,25 DPS, mais frappe toutes les 2,00 secondes pour **96 à 145 dégâts**, soit 120,5 par coup en moyenne. La Déchireuse affiche 53,82 DPS et frappe toutes les 3,80 secondes pour **153 à 256 dégâts**, soit 204,5 en moyenne. Son attaque de base gagne 84 dégâts par coup et ses 62 points de puissance d’attaque s’appliquent aussi aux techniques. L’effet de Hanna se déclenche à 30 charges. Il inflige alors 490 dégâts physiques et augmente toutes les caractéristiques de 20 pendant 20 secondes. Un engagement commencé à zéro charge ne bénéficie pas de cet effet au premier coup. [Hanna sur Wowhead Forever](https://www.wowhead.com/forever/item=2801/blade-of-hanna) · [La Déchireuse](https://www.wowhead.com/forever/item=12784/arcanite-reaper) · [Implémentation des 30 charges](https://github.com/wowsims/forever/blob/a73af71451/sim/common/forever/items_weapons.go#L156-L199)

WoWSims ajoute au jet de l’arme **3,3 × puissance d’attaque / 14** pour ces deux techniques avec une arme à deux mains. Le facteur 3,3 est commun aux deux armes. Le jet propre à chaque arme conserve sa plage d’origine. Au niveau 60, **Frappe mortelle** ajoute 160 dégâts et **Fulgurance** en ajoute 35, avant les modificateurs du personnage et l’armure de la cible. Dans le profil contrôlé, Empaler porte le multiplicateur critique à 2,2. [Normalisation des armes à deux mains](https://github.com/wowsims/forever/blob/a73af71451/sim/core/attack.go#L71-L91) · [Calcul du jet normalisé](https://github.com/wowsims/forever/blob/a73af71451/sim/core/attack.go#L146-L171) · [Frappe mortelle](https://github.com/wowsims/forever/blob/a73af71451/sim/warrior/talents_arms.go#L204-L221) · [Fulgurance](https://github.com/wowsims/forever/blob/a73af71451/sim/warrior/overpower.go#L28-L44)

## Influence du temps passé au contact

Les 390 deux-mains admissibles ont aussi été reclassées en faisant varier le nombre de secondes de coups blancs pour une Frappe mortelle. Trois secondes représentent une fenêtre de contact courte au cours du délai de recharge. Douze ou vingt-quatre secondes représentent des attaques davantage espacées, par exemple lorsque la rage manque. Les autres poids et les filtres restent identiques.

| Hypothèse | Rang de Hanna | Rang de la Déchireuse |
|---|---:|---:|
| Ancien barème basé sur le DPS de l’arme | 4 | 11 |
| 3 secondes de coups blancs et une Frappe mortelle | 62 | 3 |
| **6 secondes et une Frappe mortelle, barème retenu** | **45** | **3** |
| 12 secondes et une Frappe mortelle | 29 | 6 |
| 24 secondes et une Frappe mortelle | 15 | 8 |

## Mesures dans WoWSims Forever

Le contrôle utilise la révision déployée `a73af71451`, un Guerrier Armes orc de niveau 60 en posture de combat et une cible humanoïde de niveau 60 avec 3 500 d’armure. Seule l’arme change. Chaque ligne repose sur 100 000 jets par technique, sans consommable, buff de raid, enchantement d’arme ni déclenchement préalable. Les colonnes donnent les **dégâts moyens d’un coup normal réussi** ou d’un **critique réussi**, après armure et sans blocage. Pour Fulgurance, on mesure le coup lorsque l’esquive adverse donne accès à la technique.

| Arme | Dégâts de base | Vitesse | Frappe mortelle normale | Critique | Fulgurance normale | Critique |
|---|---:|---:|---:|---:|---:|---:|
| Blade of Hanna (2801) | 96–145 | 2,00 | 311 | **684** | 230 | **507** |
| Arcanite Reaper (12784) | 153–256 | 3,80 | 375 | **825** | 294 | **647** |
| Forest Defender’s Axe (279260) | 162–244 | 3,30 | 370 | **814** | 289 | **636** |
| The Unstoppable Force (19323) | 152–255 | 3,60 | 393 | **865** | 308 | **676** |
| Hammer of Thundering Hooves (280018) | 142–214 | 3,30 | 378 | **831** | 292 | **642** |
| Blackblade of Shahram (12592) | 166–250 | 3,50 | 368 | **809** | 287 | **631** |
| Treant’s Bane (18538) | 128–193 | 2,70 | 340 | **748** | 259 | **570** |
| Nightfall (19169) | 187–282 | 3,50 | 385 | **847** | 304 | **669** |

Par rapport à la Déchireuse, Hanna perd **17 %** sur la Frappe mortelle critique et **22 %** sur la Fulgurance critique. Le talent *Weaponmaster* ajoute cinq points de chance de critique avec une hache dans cette configuration. Il permet aux masses d’ignorer une partie de l’armure. La cible laisse ainsi passer 61,11 % des dégâts d’épée ou de hache, contre 64,90 % des dégâts de masse. Cela explique pourquoi The Unstoppable Force dépasse même la Déchireuse sur le critique réussi malgré leurs plages de dégâts proches. [Spécialisation d’arme](https://github.com/wowsims/forever/blob/a73af71451/sim/warrior/talents_arms.go#L283-L340) · [Mitigation par l’armure](https://github.com/wowsims/forever/blob/a73af71451/sim/core/spell_resistances.go#L151-L163)

## Comment lire le nouveau rang

L’ancien barème valorisait principalement les DPS de l’arme. Le nouveau barème conserve les poids JcJ des statistiques et évalue la part de l’arme sur **six secondes d’attaques automatiques et une Frappe mortelle**. Il tient ainsi compte à la fois des dégâts soutenus et du jet d’une attaque instantanée. Dans les filtres indiqués en tête, Forest Defender’s Axe reste première, The Unstoppable Force monte de la troisième à la deuxième place et la Déchireuse monte de la onzième à la troisième. Les 494 identifiants des armes candidates et de leurs variantes de faction disposent d’une vitesse et d’une plage de dégâts. [Données utilisées par le classement](../../_build/corrections/arms_weapons.json)

Les mesures de coups isolés servent à vérifier le sens du classement. Le protocole utilise une cible de caractéristiques comparables à celles d’un joueur. Il ne modélise ni duel complet, ni contrôles, ni temps passé hors de portée, ni charges de Hanna conservées avant l’engagement. Ces facteurs, ainsi que le type d’arme, les statistiques défensives et les déclenchements sur la durée, expliquent qu’une arme puisse produire le plus gros critique sans occuper le premier rang JcJ. [Entrées, code de reproduction et distributions des douze armes testées](armes-jcj-wowsims.json)
