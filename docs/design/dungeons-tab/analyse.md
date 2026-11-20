# Onglet « Dungeons » : analyse, décisions et réalisation

Objectif : montrer, pour une spé, **quels donjons farmer et pour quelles pièces**, comme la feuille Excel où chaque
pièce porte la couleur de son donjon. Très visuel, peu de texte.

[`maquette.html`](maquette.html) montre ce qui est implémenté, avec les pièces, les runs et les couleurs sortis du
modèle de l'addon pour 8 spés. Elle s'ouvre dans un navigateur ; les icônes viennent de Wowhead, il faut donc être
en ligne. Les objets propres à Forever n'ont pas d'icône sur Wowhead Classic : 103 des 348 pièces portent une icône
générique et la couleur « rare ».

## 1. Ce que disent les données

Mesuré en chargeant l'addon dans le banc de test (`_build/tests`), listes PvE pré-raid, 27 spés.

| | min | médiane | max |
|---|---|---|---|
| Pièces BIS qui tombent en donjon, par spé | 0 (Druide Féral) | 5 | 8 (Démoniste Destruction) |
| Runs différents pour ces BIS (ailes comptées à part) | 0 | 4 | 6 |
| Runs différents, BIS + 2 alternatives | 5 | 8 | 11 |
| Runs différents, BIS + 6 alternatives | 9 | 13 | 17 |

- **29 % des BIS viennent d'un donjon** (129 sur 443). Le reste : craft 28 %, vendeur 23 %, quête 9 %,
  réputation 5 %, autres 7 %. Ces chiffres datent d'avant le rangement des quêtes de donjon et des objets sans
  source (section 4) : avec eux, quelques spés gagnent une pièce ou un run (Paladin Sacré passe de 3 à 4 pièces,
  Démoniste Destruction de 6 à 7 runs).
- Six donjons portent presque tous les BIS : Blackrock Spire, Stratholme, Dire Maul, Scholomance, Blackrock
  Depths, Maraudon, plus Blackmaw Hold.
- **Les taux sont fiables** : 88 % des drops listés sont des comptages faits dans Forever (label `w`), 9 % viennent
  des données Classic (`k`, marqués `*` dans l'addon).

## 2. Décisions

| Question | Décision |
|---|---|
| Vue par donjon ou grille façon Excel ? | **Les deux**, avec un bouton pour basculer (`By dungeon` / `By piece`). Le choix est mémorisé. |
| Où placer l'onglet ? | **Sur le côté de la fenêtre**, comme le panneau des métiers : un onglet pour les listes, un pour les donjons. Les onglets du bas sont ceux des listes et disparaissent sur les donjons. |
| Pièces qui ne viennent pas d'un donjon | **En noir et blanc**, un peu assombries, dans la tenue (vue par donjon) ; assombries sur leur ligne (grille). |
| Estimation « ≈ N runs » | **Retirée.** L'onglet ne montre que ce que les données disent : le boss et son taux. |
| Quêtes de donjon | **Rangées avec leur donjon**, sous le « ! » des quêtes, le titre de la quête à la place du boss. |
| Raids | Hors de l'onglet. |

## 3. Ce que l'onglet montre

En haut : `8 best picks to farm · 6 dungeons`, et le bouton des deux vues.

**Par donjon**
1. La tenue : les 17 emplacements du BIS dans l'ordre de la fiche de personnage, chacun souligné de la couleur de
   son donjon. Une pièce hors donjon est en noir et blanc, sa barre grise.
2. Un bandeau par run, du plus rentable au moins rentable : le nombre de pièces du bandeau (BIS et alternatives) sur la couleur du
   run, son nom, puis les pièces avec icône, nom, boss et taux.
3. Une ligne pour le reste : `9 best picks from elsewhere: 5 Crafted · 2 Vendor…`. Un clic ouvre l'onglet Items
   filtré sur ce type de source.

**Par pièce** : une ligne par pièce, une colonne par run, une case dans la couleur du run là où la pièce tombe, avec
son taux. La dernière colonne dit d'où vient une pièce hors donjon.

Dans les deux vues :
- **Un run** = un donjon, ou une aile qui se fait seule (UBRS et LBRS, Strat Vivants et Morts-vivants, les trois
  ailes de Hache-Tripes, les quatre du Monastère).
- **Survol** d'un bandeau : ses emplacements s'allument dans la tenue. Survol d'une pièce : l'infobulle de
  l'objet, avec ses runs.
- **Clic** sur une pièce : son emplacement dans l'onglet Items. Maj-clic : lien dans le chat.
- **Pièce possédée** (portée, sac ou banque) : cochée et grisée, elle sort des compteurs. Un run terminé passe
  sous les autres.
- **Alternatives** : le bouton du pied de fenêtre. Plus petites, étiquetées `Alt`, elles ne comptent dans aucun
  chiffre et s'effacent quand le BIS de l'emplacement est obtenu.

## 4. Ce qui a changé dans les données

Tout est dans `_build`. Les points 1 à 4 ne changent aucun classement ; le point 5 en change quelques-uns.

1. **Ailes.** `corrections/drops.json` gardait déjà le nom du journal (« Upper Blackrock Spire »). `runs.py` en
   tire l'aile de chaque boss, et une table écrite à la main (45 boss) place ceux que les comptages ne situent
   pas. Un boss sans nom dans les données reste sous le donjon entier (« Dire Maul », « Stratholme »).
2. **Donjons de Forever absents de la table des instances** : Blackmaw Hold, The Drowned City, Krol'dok
   Stronghold, Alcaz Prison, Shaper's Terrace. Leurs numéros d'instance viennent de l'addon Forever Dungeon Routes.
3. **Créatures replacées dans leur donjon** : arène de Blackrock Depths, boss que ForeverDB a vus sans les nommer
   (« NPC 258905 » devient Zul'Alai, The Drowned City). 160 objets, dont 93 dans les listes. L'onglet Items les
   montre désormais comme des drops de donjon, et son filtre Zone les trouve.
4. **Quêtes de donjon** : `build.py --import-dungeon-quests` lit dans QuestieDB le donjon de chaque quête
   (`corrections/quests.json`, 136 quêtes en donjon). L'aile de 16 d'entre elles est écrite à la main dans
   `runs.py` ; les livres de classe de Hache-Tripes, qui tombent dans toutes les ailes, restent sous « Dire Maul ».
5. **Objets sans source.** 79 objets que ForeverDB laisse sans source prennent le boss que le journal a compté
   (Shaper's Terrace, Alcaz Prison, Blackmaw Hold, Krol'dok Stronghold surtout). Les 60 qui sont dans les listes de
   ForeverDB ne sont plus « sans source connue » : ils comptent par défaut. Les 19 pièces ajoutées depuis le jeu
   gardent leur statut, comme celles dont la source vient de QuestieDB. Quatre BIS changent avec les options par
   défaut :
   - Obsidian Bauble (Pusillin, Hache-Tripes Est) : main gauche PvE des trois Mages, Démoniste Démonologie et
     Destruction, Druide Équilibre, Chaman Élémentaire ;
   - Robes of Dark Summons (Blackmaw Hold) : torse PvE de Prêtre Ombre et Chaman Élémentaire ;
   - Frostfang Mail Vest (Shaper's Terrace) : torse PvP de Chaman Restauration et de Paladin Sacré Horde ;
   - Deep Jungle Rifle (Shaper's Terrace) : arme à distance PvE de Voleur Finesse.

   Vingt objets sans source n'ont qu'une infobulle de GearQuest (une créature, pas de lieu) : ils restent sans
   source.

## 5. Fichiers

| Fichier | Rôle |
|---|---|
| `_build/runs.py` | Ailes, donjons manquants, donjon des quêtes. |
| `_build/corrections.py`, `fdb.py`, `luaout.py`, `build.py` | Créatures replacées, tables `wings` et `questRuns` dans `Data/Items.lua`, commande d'import. |
| `Sources.lua` | `Sources.Runs(id)`, `RunName`, `Owned`. |
| `Dungeons.lua` | Le modèle, en tables simples : runs, pièces, compteurs, tenue, lignes de la grille. |
| `UI/Dungeons.lua` | La vue et ses deux modes. |
| `UI/Browser.lua`, `UI/Widgets.lua`, `Core.lua`, `Locales.lua`, `EasyBIS.toc` | Les deux onglets de côté (`Widgets.SideTabs`), option `dungeonGrid`, textes en/fr. |
| `_build/tests` | Générateur, modèle (contre les données du générateur, pour chaque objet et chaque spé), vue. |

## 6. Limites connues

- **Jamais lancé dans le jeu.** Tout est vérifié dans le banc de test hors ligne, qui ne dessine rien : les
  positions sont testées, pas le rendu (couleurs, transparences, polices).
- Les noms de boss et de quêtes restent en anglais, comme partout dans l'addon.
- Avec 6 alternatives par emplacement, la grille peut dépasser 12 colonnes : leurs noms courts sont alors tronqués
  (le nom complet est dans l'infobulle de la colonne).
