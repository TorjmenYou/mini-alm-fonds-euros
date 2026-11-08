# V5 : synthèse économique finale

Trois profils fictifs de fonds euros, huit stratégies ALM, deux vues : le portefeuille fermé (`docs/V5_STRATEGIES.md`, `docs/V5_SYNTHESE_STRATEGIES.md`) et la collecte nouvelle sensible au taux servi relatif (`docs/V5_COLLECTE.md`). Généré par `scripts/v5_synthese_finale.py` depuis `resultats/v5_consolidation.json`, `resultats/v5_collecte.json` et `resultats/v5_reconciliation_collecte.json`. Unités fictives : 1 unité = 10 M€.

**Statut.** Étude exploratoire sur des profils fictifs, conditionnelle aux hypothèses ; ce n'est pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. Les probabilités de recapitalisation sont conditionnelles au modèle. Valeur risque neutre et rentabilité en probabilité réelle restent séparées. **Aucune stratégie n'est désignée optimale.**

**Base commune et lecture.** Chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (vue prudentielle sur la base avec VA) ; sa valeur (risque neutre, base sans VA) est nette de cet apport. Un écart est significatif si son intervalle apparié à 95 % exclut zéro ; il est important s'il est significatif et dépasse 2 % du SCR simplifié du profil pour la valeur et l'apport (2,4 pour A, 1,9 pour B, 1,7 pour C), 25 pb pour la rentabilité, 5 pb pour le taux servi, 5 % du SCR pour les moins-values réalisées. « Robuste » : la borne de l'intervalle apparié à 95 % dépasse le seuil d'importance, avec le même signe, dans toutes les configurations de la grille de collecte (c0 de 3 % à 10 %, eta en 5 points de 0,0 à 1,5) et sous la loi de rachat ONC maximale (intensité centrale). Les hypothèses du modèle de collecte lui-même (e0, horizon de collecte) sont testées à part (section 2).

## 1. Ce que l'étude établit

Effet mesuré, significativité statistique et robustesse économique sont lus séparément : l'**effet mesuré** est l'écart moyen de valeur totale à la gestion passive ; il est **significatif** si son intervalle apparié à 95 % exclut zéro ; il est **important** s'il est significatif et si sa moyenne dépasse le seuil d'importance ; il est **robuste** si la borne de l'intervalle dépasse ce seuil, avec le même signe, dans toutes les configurations. Un changement de signe n'est retenu que si des écarts significatifs de signes opposés existent.

- **Capital à l'ouverture** : sans apport, l'indicateur simplifié dépasse déjà 100 % pour C (7 stratégies sur 8), dont l'apport estimé est nul. Apport de la gestion passive [intervalle à 95 %] : A 101,0 [99,4 ; 102,8] ; B 25,4 [23,9 ; 30,4] ; C 0,0 [0,0 ; 0,0]. La collecte ne change pas ce besoin : il est calculé sur l'existant en extinction, dans la frontière des contrats (vue simplifiée, qui ne reprend pas les effets de la collecte sur les hypothèses de projection de l'existant).
- **Coût de la recapitalisation** : un apport n'est jamais un profit ; recapitaliser à 100 % coûte à l'actionnaire 9,9 (A), 3,6 (B), 0,0 (C) de valeur (impôt et participation sur les revenus du capital).
- **Valeur de l'existant** (gestion passive, capital à 100 %) : −5,4 (A), 57,8 (B), 82,8 (C). A : l'existant détruit de la valeur pour l'actionnaire une fois recapitalisé.
- **Valeur des affaires nouvelles** (gestion passive) : A de 0,3 à 28,9, marge de 0,9 % à 3,9 % de la VA des primes ; B de 0,8 à 32,3, marge de 1,3 % à 3,2 % de la VA des primes ; C de 1,8 à 34,1, marge de 1,9 % à 3,4 % de la VA des primes. Elle dépend d'abord de l'intensité et de l'élasticité, qui fixent le volume collecté ; la variation d'impôt représente 46 % à 49 % de la valeur avant impôt (collecte centrale modérée), bien plus que le taux nominal de l'impôt sur les sociétés, et l'origine de cet écart n'est pas isolée (une explication possible : l'impôt sur les revenus du capital retenu avec la croissance). C'est une valeur avant coût explicite de mobilisation du capital additionnel : une charge frictionnelle annuelle de 2,0 % à 2,5 % du SCR proxy des affaires nouvelles suffirait à l'annuler en collecte centrale (analyse de seuil, `docs/V5_COLLECTE.md`, section 8). Seule cette valeur s'interprète : sa répartition entre les flux des contrats nouveaux et la variation du BE de l'existant déplace les transferts entre générations d'assurés sans les isoler.
- **Réinvestissement progressif** : écart de valeur totale à la gestion passive : sans effet important (A), sans effet important (B), toujours positif, non robuste (C) ; en portefeuille fermé, l'écart de A est statistiquement significatif (contrôle sur tirages indépendants : 0,41 ± 0,12) mais économiquement négligeable.
- **Capital de la croissance** (ordre de grandeur, `docs/V5_COLLECTE.md`, section 8) : à SCR proportionnel à la PM, la collecte centrale demanderait à 10 ans un SCR supplémentaire de 11,5 à 67,0 (A), 13,5 à 57,4 (B), 27,6 à 50,7 (C) pour la gestion passive selon l'élasticité, à comparer à l'apport d'ouverture (101,0 (A), 25,4 (B), 0,0 (C)). La politique de distribution retient en même temps des fonds propres comptables : 61,8 (A), 32,2 (B), 28,3 (C) de plus à 10 ans (médianes, élasticité modérée, contre un SCR supplémentaire de 45,4 (A), 40,4 (B), 39,6 (C)) : ce SCR n'appelle donc pas un apport du même montant, mais fonds propres comptables et prudentiels ne coïncident pas. **Aucune stratégie ne garantit la conformité prudentielle future** : l'apport d'ouverture couvre l'existant en extinction à la date d'évaluation, le SCR n'est pas projeté.
- **Intensité centrale** : c0 = 6 % redonne la collecte nette de la place en 2025 (0,59 % la première année dans le modèle, 0,69 % observés), pas ses flux bruts (9,9 % de primes, 9,2 % de sorties) ni la croissance de la PM ; le modèle n'a ni prélèvements sociaux ni arbitrages (`docs/V5_COLLECTE.md`, section 1).

**Écart de valeur totale à la gestion passive, sur la grille de collecte et sous ONC maximale** (15 configurations de collecte et 5 sous ONC maximale, soit 20 par profil) :

| Stratégie | Profil | Effet mesuré (de ... à ...) | Signe | Significatif | Important | Borne au-delà du seuil | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Réinvestissement progressif | A | de 0,1 à 1,0 | positif partout | 20 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Réinvestissement progressif | B | de 0,2 à 0,8 | positif partout | 20 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Réinvestissement progressif | C | de 0,0 à 0,6 | positif partout | 0 sur 20 | 0 sur 20 | 0 sur 20 | toujours positif, non robuste |
| Repositionnement | A | de −20,9 à −7,3 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Repositionnement | B | de −15,4 à −7,8 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Repositionnement | C | de −2,6 à −1,2 | négatif partout | 20 sur 20 | 16 sur 20 | 2 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | A | de −15,0 à −0,9 | négatif partout | 19 sur 20 | 15 sur 20 | 14 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | B | de −24,1 à −2,6 | négatif partout | 20 sur 20 | 20 sur 20 | 18 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | C | de −23,4 à −2,1 | négatif partout | 19 sur 20 | 19 sur 20 | 15 sur 20 | toujours négatif, non robuste |
| Taux servi de marge | A | de 2,7 à 9,8 | positif partout | 20 sur 20 | 20 sur 20 | 14 sur 20 | toujours positif, non robuste |
| Taux servi de marge | B | de 0,2 à 8,5 | positif partout | 15 sur 20 | 14 sur 20 | 12 sur 20 | toujours positif, non robuste |
| Taux servi de marge | C | de −3,0 à 4,6 | positif dans 16 sur 20 | 13 sur 20 | 11 sur 20 | 7 sur 20 | change de signe selon les hypothèses |
| Liquidité défensive | A | de −6,9 à 3,5 | positif dans 10 sur 20 | 8 sur 20 | 8 sur 20 | 4 sur 20 | change de signe selon les hypothèses |
| Liquidité défensive | B | de 0,4 à 3,1 | positif partout | 5 sur 20 | 5 sur 20 | 0 sur 20 | toujours positif, non robuste |
| Liquidité défensive | C | de 3,1 à 5,1 | positif partout | 20 sur 20 | 20 sur 20 | 7 sur 20 | toujours positif, non robuste |
| Compétitif préservant la PPB | A | de −17,0 à −0,6 | négatif partout | 19 sur 20 | 15 sur 20 | 15 sur 20 | toujours négatif, non robuste |
| Compétitif préservant la PPB | B | de −24,7 à −3,3 | négatif partout | 20 sur 20 | 20 sur 20 | 19 sur 20 | toujours négatif, non robuste |
| Compétitif préservant la PPB | C | de −23,9 à −2,4 | négatif partout | 19 sur 20 | 19 sur 20 | 16 sur 20 | toujours négatif, non robuste |
| Rétention de capital | A | de −2,1 à −0,6 | négatif partout | 20 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Rétention de capital | B | de −2,3 à −1,0 | négatif partout | 20 sur 20 | 1 sur 20 | 1 sur 20 | toujours négatif, non robuste |
| Rétention de capital | C | de −2,2 à −1,0 | négatif partout | 20 sur 20 | 4 sur 20 | 4 sur 20 | toujours négatif, non robuste |

## 2. La politique de marge avec collecte

- **A** : avantage de 5,8 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 8,3 ± 0,7 (eta 0,0), 5,5 ± 0,7 (eta 0,5), 4,5 ± 0,8 (eta 0,75), 4,3 ± 1,0 (eta 1,0), 5,6 ± 0,9 (eta 1,5) ; sous ONC maximale 3,6 (eta 0,0), 3,0 (eta 0,5), 2,7 (eta 0,75), 2,7 (eta 1,0), 3,4 (eta 1,5). Cas le moins favorable : 2,7 ± 1,2. Majorant (intensité centrale) : non pour eta 0,0, indéterminé pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **toujours positif, non robuste**.
- **B** : avantage de 6,2 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 7,8 ± 0,9 (eta 0,0), 5,0 ± 0,8 (eta 0,5), 3,7 ± 0,8 (eta 0,75), 3,7 ± 1,0 (eta 1,0), 6,1 ± 1,0 (eta 1,5) ; sous ONC maximale 2,3 (eta 0,0), 0,9 (eta 0,5), 0,2 (eta 0,75), 0,4 (eta 1,0), 1,8 (eta 1,5). Cas le moins favorable : 0,2 ± 0,9. Majorant (intensité centrale) : non pour eta 0,0, oui pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **toujours positif, non robuste**.
- **C** : avantage de 3,1 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 4,0 ± 1,1 (eta 0,0), 1,3 ± 0,9 (eta 0,5), 0,0 ± 0,9 (eta 0,75), 0,3 ± 0,8 (eta 1,0), 3,5 ± 0,7 (eta 1,5) ; sous ONC maximale 0,8 (eta 0,0), 0,0 (eta 0,5), −0,2 (eta 0,75), 0,1 (eta 1,0), 1,6 (eta 1,5). Cas le moins favorable : −3,0 ± 1,3. Majorant (intensité centrale) : non pour eta 0,0, oui pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **change de signe selon les hypothèses**.

**Ce qui explique l'avantage mesuré sur la grille.** Trois éléments, mesurés. (1) L'écart de taux servi effectivement réalisé entre la politique de marge et la gestion passive est faible : −37 pb (A), −14 pb (B), −5 pb (C) en moyenne sur 10 ans (probabilité réelle, élasticité modérée), bien moins que le point d'écart des cibles, car la participation minimale (compte de participation simplifié) et les reprises de PPB limitent la baisse ; la perte de collecte en est d'autant réduite. (2) La marge des affaires nouvelles est mince : 2,8 % (A), 2,7 % (B), 2,9 % (C) de la VA des primes pour la gestion passive, alors que l'avantage ne serait annulé, au premier ordre, qu'avec une marge de 12,3 % (A), 7,7 % (B), 4,0 % (C) sur les primes perdues. (3) La gestion passive sert elle-même 0,5 point sous la référence : avec e0 = 0, une élasticité forte lui retire aussi une grande partie de sa collecte. Ce troisième point est une conséquence du choix de e0 et de la conception de la gestion passive, pas un mécanisme indépendant.

**Ce que l'avantage doit aux hypothèses du modèle de collecte** (écart de valeur totale à la gestion passive, intensités centrale et forte, élasticités modérée et soutenue) :

- **A** : e0 = −0,5 point : toujours positif, non robuste (de 2,3 à 6,2) ; collecte pendant 30 ans : toujours positif, non robuste (de 5,7 à 16,0) ; collecte pendant 60 ans : toujours positif, non robuste (de 6,6 à 99,3).
- **B** : e0 = −0,5 point : positif là où il est significatif, non robuste (de −2,7 à 5,1) ; collecte pendant 30 ans : toujours positif, non robuste (de 5,8 à 15,3) ; collecte pendant 60 ans : toujours positif, non robuste (de 6,7 à 90,4).
- **C** : e0 = −0,5 point : change de signe selon les hypothèses (de −7,1 à 1,3) ; collecte pendant 30 ans : non concluant (aucun écart significatif, signes mêlés) (de −2,2 à 0,4) ; collecte pendant 60 ans : non concluant (aucun écart significatif, signes mêlés) (de −4,0 à 10,8).

27 cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à 445,0), dont 21 à l'intensité forte, toutes avec une collecte de 30 ans ou 60 ans : la PM y croît pendant des décennies, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche de conclure dans un sens ou dans l'autre.

Sur l'ensemble des configurations testées (grille, ONC maximale, e0 et horizon de collecte), le verdict est : toujours positif, non robuste (A), positif là où il est significatif, non robuste (B), change de signe selon les hypothèses (C). g_min = 0 n'est pas testé. **La politique de marge n'est pas qualifiée d'optimale** : son avantage dépend de l'élasticité, non calibrée, de e0 et de l'horizon de collecte ; le modèle ne fait pas racheter l'existant au-delà de la loi de rachat dynamique quand la compétitivité baisse ; il ignore les effets commerciaux et de réputation d'un taux servi durablement inférieur à la référence (écart moyen de −93 pb (A), −53 pb (B), −26 pb (C) sur 10 ans en probabilité réelle) ; et la valeur actionnaire n'est qu'une des dimensions de la section 3.

**Politique compétitive sous ces hypothèses** : toujours négatif, non robuste (A, de −105,7 à −6,8), toujours négatif, non robuste (B, de −195,5 à −13,7), toujours négatif, non robuste (C, de −258,1 à −12,9).

**Déplacement moyen de l'écart de valeur totale** (trois profils, intensité centrale, élasticités modérée et soutenue), du centre à chaque hypothèse : la politique de marge : e0 = −0,5 point de 3,4 à 2,9, collecte pendant 30 ans de 3,4 à 4,0, collecte pendant 60 ans de 3,4 à 4,7 ; la politique compétitive : e0 = −0,5 point de −9,9 à −11,9, collecte pendant 30 ans de −9,9 à −14,8, collecte pendant 60 ans de −9,9 à −20,6. Le signe de l'écart change, avec des écarts significatifs de part et d'autre, pour la politique de marge (C) : le classement de portefeuille fermé n'y est pas une conclusion générale. Un seul écart de signe contraire apparaît, sans être significatif (la politique de marge pour B, e0 = −0,5 point, c0 10 %, eta 1,0 : −2,7 ± 3,0) : il ne suffit pas à établir un changement de signe, mais l'avantage n'y est plus démontré.

## 3. Synthèse par profil

Tous les chiffres des tableaux sont des écarts à la gestion passive, capital à 100 %. Valeur de l'existant : portefeuille fermé (intervalle apparié). Affaires nouvelles et indicateurs réels : collecte centrale (c0 = 6 %), élasticité modérée (eta = 0,5). Valeur totale : verdict sur la grille et sous ONC maximale. Rentabilité, compétitivité (taux servi moyen du fonds) et liquidité en probabilité réelle, sans intervalle ; capital : apport à 100 % (intervalle de rééchantillonnage).

### Profil A

Indicateur de couverture simplifié du SCR sans apport : 13 %. Gestion passive avec collecte centrale modérée : valeur de l'existant −5,4, valeur des affaires nouvelles 6,2, rendement réel des fonds propres 4,8 % (sous le rendement exigé fictif de 8 %), écart du taux servi à la référence de −56 pb, collecte 1-10 de 448,8 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,4) | neutre (0,3) | sans effet important (de 0,1 à 1,0) | neutre (−0,05 pt) | neutre (0 pb) | favorable (−16,6) | neutre (0,7) |
| Repositionnement | défavorable (−16,3) | neutre (−2,1) | défavorable, robuste (de −20,9 à −7,3) | défavorable (−2,18 pt) | neutre (−5 pb) | défavorable (17,0) | défavorable (17,8) |
| Taux servi compétitif | défavorable (−5,9) | neutre (−0,9) | toujours négatif, non robuste (de −15,0 à −0,9) | neutre (−0,08 pt) | favorable (29 pb) | défavorable (10,0) | favorable (−12,6) |
| Taux servi de marge | favorable (5,8) | neutre (−0,3, ns) | toujours positif, non robuste (de 2,7 à 9,8) | neutre (−0,01 pt) | défavorable (−37 pb) | défavorable (27,5) | défavorable (6,1) |
| Liquidité défensive | neutre (0,8, ns) | neutre (−2,4) | change de signe selon les hypothèses (de −6,9 à 3,5) | défavorable (−0,64 pt) | neutre (−3 pb) | neutre (3,5) | défavorable (13,5) |
| Compétitif préservant la PPB | défavorable (−4,1) | défavorable (−3,0) | toujours négatif, non robuste (de −17,0 à −0,6) | défavorable (−0,29 pt) | favorable (29 pb) | neutre (1,1) | neutre (−1,4) |
| Rétention de capital | neutre (−1,1) | neutre (−0,3) | sans effet important (de −2,1 à −0,6) | neutre (−0,08 pt) | neutre (0 pb) | neutre (−0,2) | neutre (−0,4) |

**Lecture.**

- **Désavantage de valeur totale robuste** : Repositionnement.
- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Taux servi compétitif (toujours négatif, non robuste), Taux servi de marge (toujours positif, non robuste), Liquidité défensive (change de signe selon les hypothèses), Compétitif préservant la PPB (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (16 configurations sur 20), Liquidité défensive (4 configurations sur 20). **Il change avec les hypothèses.**

### Profil B

Indicateur de couverture simplifié du SCR sans apport : 74 %. Gestion passive avec collecte centrale modérée : valeur de l'existant 57,8, valeur des affaires nouvelles 8,7, rendement réel des fonds propres 9,0 % (au-dessus du rendement exigé fictif de 8 %), écart du taux servi à la référence de −40 pb, collecte 1-10 de 508,5 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,3, ns) | neutre (0,4) | sans effet important (de 0,2 à 0,8) | neutre (−0,06 pt) | neutre (−1 pb) | neutre (0,0) | neutre (−0,2) |
| Repositionnement | défavorable (−11,8) | neutre (−1,1) | défavorable, robuste (de −15,4 à −7,8) | défavorable (−1,89 pt) | favorable (8 pb) | défavorable (16,7) | défavorable (20,1) |
| Taux servi compétitif | défavorable (−10,1) | défavorable (−3,3) | toujours négatif, non robuste (de −24,1 à −2,6) | défavorable (−0,39 pt) | favorable (37 pb) | neutre (−0,1) | neutre (−1,1) |
| Taux servi de marge | favorable (6,2) | neutre (−1,2) | toujours positif, non robuste (de 0,2 à 8,5) | favorable (0,27 pt) | défavorable (−14 pb) | neutre (3,8) | favorable (−3,6) |
| Liquidité défensive | neutre (1,2, ns) | neutre (−0,3, ns) | toujours positif, non robuste (de 0,4 à 3,1) | défavorable (−0,31 pt) | défavorable (−6 pb) | neutre (0,0) | neutre (0,8, ns) |
| Compétitif préservant la PPB | défavorable (−9,5) | défavorable (−4,1) | toujours négatif, non robuste (de −24,7 à −3,3) | défavorable (−0,55 pt) | favorable (36 pb) | neutre (0,6) | neutre (−0,2, ns) |
| Rétention de capital | neutre (−1,4) | neutre (−0,2) | toujours négatif, non robuste (de −2,3 à −1,0) | défavorable (−0,48 pt) | neutre (0 pb) | neutre (−0,1) | neutre (0,4) |

**Lecture.**

- **Désavantage de valeur totale robuste** : Repositionnement.
- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Taux servi compétitif (toujours négatif, non robuste), Taux servi de marge (toujours positif, non robuste), Liquidité défensive (toujours positif, non robuste), Compétitif préservant la PPB (toujours négatif, non robuste), Rétention de capital (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (15 configurations sur 20), Liquidité défensive (5 configurations sur 20). **Il change avec les hypothèses.**

### Profil C

Indicateur de couverture simplifié du SCR sans apport : 104 %. Gestion passive avec collecte centrale modérée : valeur de l'existant 82,8, valeur des affaires nouvelles 10,7, rendement réel des fonds propres 11,9 % (au-dessus du rendement exigé fictif de 8 %), écart du taux servi à la référence de −21 pb, collecte 1-10 de 584,7 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,0, ns) | neutre (0,2, ns) | toujours positif, non robuste (de 0,0 à 0,6) | neutre (−0,05 pt) | neutre (−1 pb) | neutre (−0,4) | neutre (0,0, ns) |
| Repositionnement | neutre (−1,2) | neutre (−1,0) | toujours négatif, non robuste (de −2,6 à −1,2) | défavorable (−0,30 pt) | neutre (4 pb) | neutre (0,9) | neutre (1,1, ns) |
| Taux servi compétitif | défavorable (−9,8) | défavorable (−3,1) | toujours négatif, non robuste (de −23,4 à −2,1) | défavorable (−0,40 pt) | favorable (25 pb) | neutre (−1,5) | neutre (0,0, ns) |
| Taux servi de marge | favorable (3,1) | défavorable (−1,9) | change de signe selon les hypothèses (de −3,0 à 4,6) | neutre (−0,01 pt) | défavorable (−5 pb) | défavorable (21,4) | neutre (0,0, ns) |
| Liquidité défensive | favorable (3,1) | neutre (0,6, ns) | toujours positif, non robuste (de 3,1 à 5,1) | neutre (−0,20 pt) | défavorable (−7 pb) | neutre (−2,1) | neutre (0,0, ns) |
| Compétitif préservant la PPB | défavorable (−9,7) | défavorable (−3,7) | toujours négatif, non robuste (de −23,9 à −2,4) | défavorable (−0,46 pt) | favorable (25 pb) | neutre (−1,5) | neutre (0,0, ns) |
| Rétention de capital | neutre (−1,3) | neutre (−0,3) | toujours négatif, non robuste (de −2,2 à −1,0) | défavorable (−0,86 pt) | neutre (0 pb) | neutre (−0,2) | neutre (0,0, ns) |

**Lecture.**

- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Réinvestissement progressif (toujours positif, non robuste), Repositionnement (toujours négatif, non robuste), Taux servi compétitif (toujours négatif, non robuste), Taux servi de marge (change de signe selon les hypothèses), Liquidité défensive (toujours positif, non robuste), Compétitif préservant la PPB (toujours négatif, non robuste), Rétention de capital (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (3 configurations sur 20), Liquidité défensive (17 configurations sur 20). **Il change avec les hypothèses.**

## 4. Ce que l'étude ne permet pas de conclure

- **Élasticité de la collecte et forme de la réaction** : aucune donnée vérifiée. Sur l'ensemble des configurations testées (y compris les cellules imprécises à 30 et 60 ans), l'écart de valeur totale va de −7,1 à 99,3 pour la politique de marge ; de −258,1 à −0,9 pour la politique compétitive. Le signe de l'écart change, avec des écarts significatifs de part et d'autre, pour la politique de marge (C) : le classement de portefeuille fermé n'y est pas une conclusion générale. Un seul écart de signe contraire apparaît, sans être significatif (la politique de marge pour B, e0 = −0,5 point, c0 10 %, eta 1,0 : −2,7 ± 3,0) : il ne suffit pas à établir un changement de signe, mais l'avantage n'y est plus démontré.
- **Comportement de rachat** : la loi centrale vient des V1 à V4, les corridors ONC de 2013 servent de sensibilité ; aucune donnée 2026 ne les calibre ; la perte de compétitivité ne fait pas racheter l'existant au-delà de cette loi.
- **Capital futur** : le SCR n'est pas projeté ; le capital de la croissance n'est estimé qu'en ordre de grandeur (SCR proportionnel à la PM) ; fonds propres comptables et prudentiels ne coïncident pas ; aucune stratégie ne garantit la conformité prudentielle future.
- **Flux de la place** : c0 = 6 % ne fait qu'approcher la collecte nette de 2025 (0,59 % de la PM contre 0,69 %), sur une seule année, avec des flux bruts plus faibles ; prélèvements sociaux et arbitrages ne sont pas modélisés.
- **Lecture statistique** : les intervalles à 95 % sont calculés cellule par cellule, ils ne sont pas simultanés : sur l'ensemble des stratégies, profils et hypothèses, quelques écarts peuvent paraître significatifs par hasard ; « robuste » est un critère descriptif, interne à la grille testée.
- **Liquidité** : quantiles à 99 % estimés sur 1 000 scénarios en probabilité réelle, soit une dizaine de scénarios dans la queue, sans intervalle de confiance ; les écarts proches du seuil sont fragiles.
- **Mécanismes absents** : inflation et attractivité du taux servi réel, arbitrages entre fonds euros et unités de compte, migration de notation des obligations, comportement de rachat propre aux contrats nouveaux (même loi que l'existant), politique de distribution fondée sur la couverture du SCR plutôt que sur un ratio comptable ; chacun peut modifier le classement des politiques de taux servi.
- **Données de marché** : courbe sans risque EIOPA du 31/10/2026 (observée) ; spread des obligations hypothétique, égal à la moyenne de long terme des spreads publiée par l'EIOPA pour la notation A, et non un spread de marché observé à cette date : les niveaux de valeur et de capital en dépendent, les comparaisons de stratégies partagent le même marché.
- **Vue prudentielle** : indicateurs simplifiés (base avec VA, risque opérationnel par la seule formule sur provisions, ni contrepartie, ni concentration, ni immobilier, ni change, impôts différés actifs non reconnus), pas de mesure transitoire ; ce ne sont pas des ratios réglementaires. Elle est calculée en extinction, sans les effets de la collecte sur les hypothèses de projection de l'existant ; la réserve de capitalisation suit le principe de l'article R.351-2-1 du Code des assurances sans en reproduire toutes les modalités.
- **Valeur des affaires nouvelles** : hors Solvabilité II, avant coût explicite de mobilisation du capital additionnel ; seuls les coûts frictionnels du capital comptable retenu (impôt et participation sur ses revenus) sont déduits ; le coût du capital immobilisé pour le SCR supplémentaire n'est mesuré que par un seuil, et aucune marge pour risques non couvrables n'est déduite.

## 5. Contrôles et corrections

**Reproductibilité.** Sur un clone propre du dépôt, tous les tests passent, les documents et les figures se régénèrent à l'identique depuis les résultats versionnés, et un échantillon de résultats recalculé sans cache est identique aux résultats versionnés (`docs/V5_REPRODUCTION.md`).

**Correction ayant modifié des résultats.** Une première version de la répartition de l'intérêt entre générations créditait les contrats nouveaux au-delà de l'intérêt décidé quand le plancher de TMG du fonds était juste atteint (profil A). Elle est corrigée, couverte par un test de non-régression, et les résultats concernés ont été recalculés.

**Contrôles complémentaires.** Grille d'élasticité densifiée (0,75 et 1,0), e0 et horizon de collecte testés à part, loi de rachat ONC maximale appliquée aux huit stratégies ; critères de lecture complets (significatif, important, robuste ; « non concluant » pour des signes mêlés sans écart significatif ; « sans effet important » seulement si l'intervalle entier reste sous le seuil ; changement de signe retenu seulement s'il repose sur des écarts significatifs) ; variantes de liquidation du contrat sans marge explicite, qui ramènent son résidu sous 0,1 % des primes pour B et C et en identifient la cause pour A ; seuil de coût du capital des affaires nouvelles ; traitement de la réserve de capitalisation confronté à l'article R.351-2-1 du Code des assurances.

Ces contrôles vérifient la cohérence interne du modèle et la reproductibilité des résultats ; ils ne constituent pas une validation actuarielle indépendante.

