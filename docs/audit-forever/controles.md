# Contre-mesures du félin et des trois tanks

EasyBIS classe ces quatre profils sur les statistiques. Les mesures de cette page ont été faites pour contrôler ces classements. Chaque fiche de spécialisation donne le résultat pour chaque substitution testée. Les réglages, les références par emplacement et les résultats numériques sont disponibles dans le [fichier de mesures](controles-wowsims.json).

## Combat et équipement

WoWSims Forever, révision `21377c070b`, simule un boss de niveau 63 à 3 731 d’armure avec 320 de puissance d’attaque. Les combats durent 180 secondes avec une variation de 5 secondes. Chaque substitution et sa référence utilisent la graine 4242 et 2 000 itérations. Les tanks combattent de face, reçoivent les attaques du boss, dont les coups physiques partent toutes les 2 secondes, et utilisent un modèle de soins entrants. La race, les talents, les buffs, les débuffs et la rotation de chaque essai figurent dans le JSON. [Moteur et cible](https://github.com/wowsims/forever/blob/21377c070b/sim/core/test_utils.go)

| Spécialisation | Référence et rotation | Mesures à lire |
|---|---|---|
| Druide Farouche, félin | Tauren, tenue pré-raid et rotation adaptative du moteur. Saignement allié supposé actif. | Gain de DPS et erreur standard appariée |
| Druide Farouche, ours | Tauren, tenue de référence en cuir du moteur, rotation adaptative. | Variation de menace/s et de dégâts reçus/s |
| Guerrier Protection | Orc, talents et tenue pré-raid *Balanced*, posture défensive. | Variation de menace/s et de dégâts reçus/s |
| Paladin Protection | Humain, configuration Protection fournie par WoWSims, incluant sa rotation et ses buffs. | Variation de menace/s et de dégâts reçus/s |

Le félin, l’ours et le guerrier partagent les buffs de raid du scénario physique et ont été testés sans consommables. Le paladin suit son preset. Les conditions diffèrent entre classes. Les deux valeurs du tank décrivent un arbitrage. Un bijou d’absorption ou d’augmentation des PV peut aider à survivre à un coup précis avec très peu de variation du débit moyen de dégâts. [Félin](https://github.com/wowsims/forever/tree/21377c070b/ui/specs/druid/feralcat) · [Ours](https://github.com/wowsims/forever/tree/21377c070b/ui/specs/druid/feralbear) · [Guerrier](https://github.com/wowsims/forever/tree/21377c070b/ui/specs/warrior/protection) · [Paladin](https://github.com/wowsims/forever/tree/21377c070b/ui/specs/paladin/protection)

Chaque objet remplace un emplacement vide, avec l’enchantement du preset lorsque la pièce est portée. Pour les bagues et les bijoux, les deux emplacements sont vidés avant de remettre une pièce. Pour tester une main gauche du druide, la main droite porte The Hammer of Grace. Pour tester l’arme principale d’un tank à bouclier, son bouclier reste équipé. Les variantes de faction sont testées par identifiant sur une même race témoin. La projection pour l’autre faction conserve les restrictions d’accès du catalogue. Les suffixes non déterminés sont exclus de la mesure. Un astérisque signale un effet manquant dans le moteur.

### Comparaisons félines à 20 000 itérations

Ces essais opposent directement les objets sur le même personnage. L’erreur standard est celle de leur différence, mesurée avec les mêmes graines. Le signe positif favorise la deuxième configuration.

| Première configuration | Deuxième configuration | Différence de DPS ± erreur standard | Décision |
|---|---|---:|---|
| Tome of Knowledge | Scepter of Interminable Focus | +3,61 ± 0,18 | Pour l’alternative à une main, le sceptre gagne sur ce set. Ses 5 de toucher et 14 de critique passent devant les 8 de Force et 8 d’Agilité du tome. |
| Legionite Glaive | Bonecrusher | −5,19 ± 0,21 | Conserver la première place du glaive entre ces deux armes. |
| Outlaw’s Collar | Eye of Rend | −1,99 ± 0,18 | Le collier de tête garde l’avantage sur cette référence. |
| Outlaw’s Collar | Wolfshead Helm | −12,91 ± 0,22 | Le casque du preset manque au catalogue. Sa présence dans le preset ne suffit pas à déclasser Outlaw’s Collar. |
| Blackveil Cape | Howler’s Furs | −0,30 ± 0,20 | L’essai ne départage pas les capes au seuil indicatif de deux erreurs standard. |
| Cutthroat’s Signet | Warden’s Signet of Ferocity | +0,20 ± 0,06 | Léger avantage individuel au sceau du gardien. Les deux bagues occupent deux emplacements. |
| Emplacement de bijou vide | Behemoth Bones, porté pour sa PA | +7,78 ± 0,002 | Les 34 de PA ont une valeur offensive. |
| Emplacement de bijou vide | Behemoth Bones, soin forcé dans la rotation | −9,08 ± 0,23 | Distinguer le bénéfice passif du coût en DPS d’un usage systématique du soin. |
| Behemoth Bones passif | Lucky Shovelnose Tuft, usage laissé à la rotation | +2,68 ± 0,20 | La gestion des activations peut inverser l’ordre des deux bijoux. |
| Behemoth Bones passif | Lucky Shovelnose Tuft, usage forcé | −1,35 ± 0,23 | Dans cette variante, l’ordre du barème est retrouvé. |

Les deux bijoux illustrent pourquoi l’ordre marginal des pièces ne suffit pas à prévoir l’effet d’une rotation qui déclenche toutes leurs activations. Les contrôles à 2 000 itérations laissent le soin de Behemoth Bones hors des actions ajoutées à la rotation féline. Les essais complémentaires font varier explicitement ce choix.

## Contrôle du score à distance en Survie

Sur la tenue de référence Survie, le moteur produit **1,85 DPS** si on retire l’arme à distance. Il atteint **1 176,73 DPS** avec Deep Jungle Rifle et **1 124,56 DPS** avec Hyper Deluxe Sniper Rifle Mk XVII, sur 2 000 itérations par configuration. Le gain proche de 1 174 DPS dans la liste embarquée inclut la reprise de la rotation entière. L’écart entre les deux armes équipées est d’environ **52 DPS** sur ce profil. Cette distinction figure désormais dans l’info des armes de cet emplacement. [Mesures brutes](controles-wowsims.json) · [Rotation de référence](https://github.com/wowsims/forever/tree/21377c070b/ui/specs/hunter/dps/builds)
