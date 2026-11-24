# Quelle version de WoWSims Forever a servi à l’audit ?

**Au 22 novembre 2026, le site WoWSims Forever déployait `a73af71451`. Les scores historiques d’EasyBIS utilisent `21377c070b`, 138 commits plus tôt.** La différence modifie sensiblement le résultat du Voleur Assassinat. Les contrôles du Démoniste et des deux fusils du Chasseur Survie reproduisent les résultats antérieurs. Ce document porte sur les configurations effectivement rejouées. [Comparaison des révisions](https://github.com/wowsims/forever/compare/21377c070b...a73af71451) · [Déploiement du site](https://github.com/wowsims/forever/actions/runs/44957933461)

| Repère | Date UTC | Révision |
|---|---|---|
| Moteur de l’archive EasyBIS | 20 novembre à 20 h 36 | `21377c070b5ea111a9bb5e36eb766193270b0cc7` |
| Tête de la branche amont `master` | 21 novembre à 22 h 40 | `a73af7145111ce19c621e3b5f678553adf326907` |
| Fin du déploiement réussi de cette tête | 21 novembre à 22 h 46 | Workflow GitHub Actions « Build and Deploy » |
| Étiquette la plus récente, `v0.0.140` | Commit du 18 septembre | `f02667f7bcc542d600a3cb924dc7b86a9e856495` |

Les deux révisions de novembre sont sans étiquette. GitHub ne publiait aucune *release* pour ce dépôt lors du contrôle. Le numéro de septembre ne permet donc pas d’identifier le moteur en ligne. [Étiquettes](https://github.com/wowsims/forever/tags) · [Releases du dépôt](https://github.com/wowsims/forever/releases) · [Commit déployé](https://github.com/wowsims/forever/commit/a73af7145111ce19c621e3b5f678553adf326907)

## Contrôles sur les deux révisions

Chaque paire utilise le même équipement hors de la substitution, les mêmes enchantements applicables, un boss unique, une durée de 180 ± 5 secondes et la graine 4242. Les valeurs sont des différences de DPS. Le signe ± donne une **erreur standard** calculée à partir des écarts appariés par itération. La configuration et les résultats plus précis figurent dans [l’annexe JSON](version-wowsims.json).

| Profil et comparaison | Itérations | Archive | Révision déployée |
|---|---:|---:|---:|
| Démoniste Affliction, chope 4696 contre main gauche vide, boisson activable en combat | 20 000 | +16,23 ± 0,24 | +16,23 ± 0,24 |
| Même équipement, activation de la boisson entièrement désactivée | 20 000 | +1,72 ± 0,12 | +1,72 ± 0,12 |
| Démoniste Destruction, même chope avec la boisson activable | 20 000 | +16,46 ± 0,35 | +16,46 ± 0,35 |
| Même équipement, activation entièrement désactivée | 20 000 | +3,54 ± 0,27 | +3,54 ± 0,27 |
| Destruction, Glowing Thresher Cape (6901) contre dos vide | 20 000 | +3,04 ± 0,20 | +3,04 ± 0,20 |
| Destruction, Sandstorm Cover (274752) contre dos vide | 20 000 | +3,81 ± 0,20 | +3,81 ± 0,20 |
| Chasseur Survie, Deep Jungle Rifle (280020) contre emplacement à distance vide | 2 000 | +1 174,88 ± 1,01 | +1 174,88 ± 1,01 |
| Chasseur Survie, Hyper Deluxe Sniper Rifle Mk XVII (279273) contre emplacement à distance vide | 2 000 | +1 122,71 ± 0,99 | +1 122,71 ± 0,99 |
| Voleur Assassinat, gants Stormshroud (21278) contre gants Devilsaur (15063), rotation historique | 5 000 | +103,19 ± 0,79 | +41,30 ± 0,70 |

**Démoniste.** La chope conserve l’activation fautive sur la version déployée. L’effet exige de s’asseoir hors combat. En supprimant à la fois son enregistrement dans le moteur et l’action dans la rotation, on mesure ses seules statistiques. Pour les capes, la main gauche reste Obsidian Bauble (18316). En duel direct, Sandstorm apporte 0,7710 ± 0,0003 DPS de plus. Sa puissance des sorts supplémentaire explique cet écart. Les scores arrondis +4 et +3 restent cohérents. [Données du sort de la chope](https://www.wowhead.com/forever/spell=1135/drink) · [Enregistrement de la boisson dans la version déployée](https://github.com/wowsims/forever/blob/a73af71451/sim/common/forever/stat_bonus_cds_auto_gen.go) · [Contre-tests de l’audit magie](magie.md)

**Chasseur Survie.** La comparaison donne 52,17 DPS d’avance au Deep Jungle Rifle dans les deux versions. Le fusil retiré, la rotation de ce profil tombe à 1,85 DPS, ce qui explique les très gros écarts contre l’emplacement vide. On obtient les mêmes DPS pour les deux fusils en remplaçant ensuite les talents historiques par le nouveau préréglage Survie. Ce contrôle porte uniquement sur ces armes dans cet équipement. [Modification du préréglage Survie](https://github.com/wowsims/forever/commit/d70543f47a5f46035e56794214e5e635f6e2625e)

**Voleur Assassinat.** Les gants Stormshroud complètent trois pièces. Avec le moteur actuel et sa nouvelle rotation, ils donnent +43,11 ± 0,73 DPS contre Devilsaur et +61,94 ± 0,73 contre les mains vides. Ces comparaisons cumulent les statistiques des gants et le franchissement du palier. Blizzard a réduit le déclenchement du bonus de 4 % à 3 % et l’énergie rendue de 30 à 18. Le changement de moteur comprend aussi une correction de la tentative de déclenchement de Furie-des-vents par Estropier. La baisse observée à rotation fixe ne peut donc pas être attribuée entièrement au seul ensemble. [Correctifs Blizzard du 20 novembre](https://worldofwarcraft.blizzard.com/en-us/news/24315281/wow-forever-hotfixes-november-20-2026) · [Ensemble Stormshroud dans le moteur](https://github.com/wowsims/forever/blob/a73af71451/sim/common/forever/item_sets_auto_gen.go#L55-L67) · [Correction d’Estropier](https://github.com/wowsims/forever/commit/bd717cfa80a98e6d3313c4d90ad2cb5617dddb7d)

### Valeur du seul bonus Stormshroud sur le moteur déployé

Pour mesurer le seul bonus, deux exécutions gardent exactement les mêmes trois pièces et les mêmes statistiques. La seconde retire uniquement le sort 23863 au palier trois pièces dans la définition de l’ensemble. Chaque spécialisation utilise sa rotation de la version déployée et 10 000 combats appariés.

| Voleur | DPS avec le palier | DPS sans le palier | Gain du seul palier |
|---|---:|---:|---:|
| Assassinat | 847,30 | 801,97 | **+45,33 ± 0,51** |
| Combat | 814,20 | 787,71 | **+26,49 ± 0,46** |
| Finesse | 858,42 | 827,40 | **+31,02 ± 0,42** |

Chaque chiffre décrit la tenue de référence de la spécialisation concernée. La valeur d’une première ou deuxième pièce seule exclut le déclenchement associé au troisième morceau.

## Données d’objets et soins

Sur 3 177 identifiants du catalogue, 2 970 figurent dans les deux fichiers principaux `assets/database/db.json` et 207 sont absents des deux fichiers. Le fichier complémentaire `leftover_db.json` contient aussi des objets. Trois fiches présentes changent de fréquence de déclenchement par minute. Brain Hacker passe de 1 à 0,95, Sword of Zeal de 1,8 à 1,95 et Sul’thraze the Lasher de 1,4 à 1,45. Cette comparaison porte sur les fiches d’objets. Les sorts, les ensembles et les rotations disposent de leurs propres implémentations. [Base de la révision historique](https://github.com/wowsims/forever/blob/21377c070b/assets/database/db.json) · [Base de la révision déployée](https://github.com/wowsims/forever/blob/a73af71451/assets/database/db.json)

Les cinq profils de soins restent des planificateurs d’équipement. Druide Restauration, Paladin Sacré, Chaman Restauration et le module commun aux Prêtres Discipline et Sacré déclarent explicitement l’absence de rotation de soins. Les préréglages de talents et les tests de sorts individuels ne fournissent pas de mesure de HPS pour le classement de leurs objets. [Druide](https://github.com/wowsims/forever/blob/a73af71451/sim/druid/restoration/restoration_test.go#L16) · [Paladin](https://github.com/wowsims/forever/blob/a73af71451/sim/paladin/holy/holy_test.go#L16) · [Chaman](https://github.com/wowsims/forever/blob/a73af71451/sim/shaman/restoration/restoration_test.go#L16) · [Prêtre](https://github.com/wowsims/forever/blob/a73af71451/sim/priest/healer/healer_test.go#L19) · [Préréglages Discipline et Sacré](https://github.com/wowsims/forever/blob/a73af71451/ui/specs/priest/healer/presets.ts)
