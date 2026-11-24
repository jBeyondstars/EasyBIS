# Pourquoi certains écarts de DPS changent de signe

Un résultat différent de l’archive peut venir de la tenue de référence, de la faction, d’un objet précédemment estimé ou du moteur. Les essais ci-dessous changent un seul paramètre à la fois. Ils mesurent du DPS sur un boss unique en 180 ± 5 secondes. Le signe ± exprime l’erreur standard de la différence appariée entre deux tenues. Les requêtes, les deux révisions et les résultats numériques sont dans [l’annexe de reproduction](controle-actualise-dps-causes.json).

## Chasseur Maîtrise des bêtes · la valeur du toucher dépend de la tenue

Le classement historique pré-raid donnait **19,5 DPS au Pendant of Celerity contre 17 à la Mark of Fordring**. Sur le nouveau profil, l’avantage change de côté. Pour en déterminer la cause, les deux colliers ont été essayés sur la même tenue légale de chaque faction. Le contrôle a ensuite été répété avec **10 points de score de toucher en moins** sur le personnage pour les deux candidats. Même méthode pour les deux dagues en main gauche, derrière **Ironwood Blade** (279259) à droite.

| Duel, seconde pièce moins première | Faction du profil | Tenue de référence | Avec 10 toucher en moins | Avec 10 toucher en plus |
|---|---|---:|---:|---:|
| Pendant of Celerity → **Mark of Fordring** | Alliance, nain | +5,82 ± 0,55 | −3,28 ± 0,76 | +7,52 ± 0,36 |
| Même duel | Horde, orc | +4,40 ± 0,69 | −2,86 ± 0,76 | +7,06 ± 0,34 |
| Shadowblade → **Tooth of the Matriarch** | Alliance, nain | +5,80 ± 0,51 | −2,54 ± 0,74 | +7,63 ± 0,31 |
| Même duel | Horde, orc | +4,91 ± 0,67 | −2,57 ± 0,74 | +7,52 ± 0,29 |

Le pendentif et la Shadowblade donnent chacun 10 au score de toucher. La marque offre 14 de critique et 26 de puissance d’attaque. La dent donne 10 d’Agilité et 7 de critique, contre 5 d’Agilité sur la Shadowblade. Le familier du chasseur hérite également de son toucher à distance dans WoWSims. Avec moins de toucher sur le reste de l’équipement, remettre les dix points sur le collier ou la dague suffit à renverser les deux duels. Un seuil identique de toucher pour tous les chasseurs ne découle pas de ces essais. [Pendentif](https://www.wowhead.com/forever/item=22340/pendant-of-celerity) · [Marque](https://www.wowhead.com/forever/item=15411/mark-of-fordring) · [Shadowblade](https://www.wowhead.com/forever/item=2163/shadowblade) · [Dent](https://foreverdb.net/item/280021) · [Transmission du toucher au familier](https://github.com/wowsims/forever/blob/a73af71451/sim/hunter/hunter_test.go#L310-L324)

Les quatre duels de la colonne « tenue de référence » ont été rejoués à **2 000 itérations sur chacune des deux révisions**, avec la même graine et les mêmes entrées. Les deux moteurs donnent les mêmes différences. L’archive utilisait une tenue comprenant les gants et les épaules de Theramore sur son profil orc. Le nouveau contrôle respecte les restrictions de faction. On peut donc attribuer au toucher le changement de signe obtenu dans le contre-test, sans attribuer à une seule pièce tous les écarts entre l’archive et la campagne actuelle.

Les gants illustrent aussi la limite d’une règle commune aux deux factions. Sur le nain, **Theramore Gloves** (271948) devance Gauntlets of Accuracy (18349) de **7,26 ± 0,58 DPS**. Sur l’orc, **Raider Gloves** (272099), aux mêmes caractéristiques que les gants de Theramore, donne **−1,34 ± 0,78 DPS** contre Gauntlets of Accuracy. Cette dernière différence inclut zéro dans son intervalle approximatif à 95 %. Les deux tenues de faction ont des pièces différentes, donc cet écart ne permet pas d’isoler l’effet d’un racial.

## Druide Équilibre · les 10 dégâts de Nature d’une paire de gants

**Gloves of the Greatfather** (17721) offre 24 dégâts des sorts et **10 dégâts de Nature supplémentaires**. **Hands of Power** (13253) donne 23 puissance des sorts, 9 Intelligence et 8 Esprit. La fiche de 17721 se trouvait déjà dans la base secondaire des deux révisions de WoWSims. L’ancien présélecteur ne lisait que la base principale et EasyBIS estimait donc la paire à 26 DPS. Le nouveau contrôle la mesure directement. [Fiche de la recette et de l’objet fabriqué](https://www.wowhead.com/forever/spell=21943/gloves-of-the-greatfather) · [Base secondaire de l’ancien moteur](https://github.com/wowsims/forever/blob/21377c070b/assets/database/leftover_db.json) · [Rotation Équilibre](https://github.com/wowsims/forever/blob/a73af71451/ui/specs/druid/balance/apls/default.apl.json)

| Gain par rapport à Hands of Power, 4 000 combats appariés | Alliance, elfe de la nuit | Horde, tauren |
|---|---:|---:|
| Gloves of the Greatfather tel quel | +1,55 ± 0,28 DPS | +1,25 ± 0,30 DPS |
| Même paire après retrait expérimental des seuls 10 dégâts de Nature | −0,78 ± 0,28 DPS | −1,06 ± 0,30 DPS |
| Valeur isolée des 10 dégâts de Nature sur cette tenue | +2,329 ± 0,002 DPS | +2,311 ± 0,002 DPS |

**Accès au 22 novembre 2026.** Les gants sont liés quand équipés. Un travailleur du cuir à 165 qui connaît le patron 17722 peut les fabriquer avec huit cuirs lourds, quatre terres élémentaires et un fil de soie. La voie saisonnière documentée passe par un cadeau des Gourmandises Fumebois pendant le Voile d’hiver. Les royaumes Forever ont ouvert le 4 novembre, avant leur premier mois de décembre. La source qui mentionne un très rare butin sur le flibustier des mers du Sud l’identifie comme une donnée Classic à confirmer. Sur le marché européen Normal Alliance consulté le 22 novembre, les matériaux étaient cotés, mais le relevé ne donnait aucun prix pour le patron ni pour les gants. Nous n’avons trouvé aucune confirmation d’une fabrication ou vente sur ces royaumes à cette date. **Hands of Power, obtenu sur le quartier-maître Zigris, reste le choix pré-raid dont l’accès est documenté.** Le léger avantage de Greatfather devient pertinent dès qu’un artisan ou une paire en vente est effectivement disponible. [Lancement par Blizzard](https://worldofwarcraft.blizzard.com/en-us/news/24315820/world-of-warcraft-forever-now-live) · [Récompense du Voile d’hiver](https://www.wowhead.com/forever/quest=7045/a-smokywood-pastures-thank-you) · [Patron et qualité des sources de butin](https://forevermastery.com/en/items/17722-pattern-gloves-of-the-greatfather) · [Relevé de l’hôtel des ventes et composants](https://forevermastery.com/en/recipes/21943-gloves-of-the-greatfather) · [Hands of Power](https://www.wowhead.com/forever/item=13253/hands-of-power)

## Duels directs à 20 000 combats dans la campagne générale

Les adversaires de chaque duel portent les mêmes pièces aux autres emplacements. Une seconde graine, indépendante de la sélection initiale, sert à tester la paire. Les chiffres indiquent le gain de la pièce nommée en premier dans le tableau.

| Duel | Faction | Gain de DPS ± erreur standard |
|---|---|---:|
| Gloves of the Greatfather contre Hands of Power | Alliance | +1,77 ± 0,12 |
| Gloves of the Greatfather contre Hands of Power | Horde | +1,57 ± 0,13 |
| Mark of Fordring contre Pendant of Celerity | Alliance | +5,94 ± 0,17 |
| Mark of Fordring contre Pendant of Celerity | Horde | +4,35 ± 0,21 |
| Tooth of the Matriarch contre Shadowblade | Alliance | +6,31 ± 0,16 |
| Tooth of the Matriarch contre Shadowblade | Horde | +4,87 ± 0,21 |
