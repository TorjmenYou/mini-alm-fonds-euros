# V5 : synthèse économique finale

Trois profils fictifs de fonds euros, huit stratégies ALM, deux vues : le portefeuille fermé (`docs/V5_STRATEGIES.md`, `docs/V5_SYNTHESE_STRATEGIES.md`) et la collecte nouvelle sensible au taux servi relatif (`docs/V5_COLLECTE.md`). Généré par `scripts/v5_synthese_finale.py` depuis `resultats/v5_consolidation.json`, `resultats/v5_collecte.json` et `resultats/v5_reconciliation_collecte.json`. Unités fictives : 1 unité = 10 M€.

**Statut.** Étude exploratoire sur des profils fictifs, conditionnelle aux hypothèses ; ce n'est pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. Les probabilités de recapitalisation sont conditionnelles au modèle. Valeur risque neutre et rentabilité en probabilité réelle restent séparées. **Aucune stratégie n'est désignée optimale.**

**Base commune et lecture.** Chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (vue prudentielle sur la base avec VA) ; sa valeur (risque neutre, base sans VA) est nette de cet apport. Un écart est significatif si son intervalle apparié à 95 % exclut zéro ; il est important s'il est significatif et dépasse 2 % du SCR simplifié du profil pour la valeur et l'apport (2,4 pour A, 2,0 pour B, 2,0 pour C), 25 pb pour la rentabilité, 5 pb pour le taux servi, 5 % du SCR pour les moins-values réalisées. « Robuste » : la borne de l'intervalle apparié à 95 % dépasse le seuil d'importance, avec le même signe, dans toutes les configurations de la grille de collecte (c0 de 3 % à 10 %, eta en 5 points de 0,0 à 1,5) et sous la loi de rachat ONC maximale (intensité centrale). Les hypothèses du modèle de collecte lui-même (e0, horizon de collecte) sont testées à part (section 2).

## 1. Ce que l'étude établit

Effet mesuré, significativité statistique et robustesse économique sont lus séparément : l'**effet mesuré** est l'écart moyen de valeur totale à la gestion passive ; il est **significatif** si son intervalle apparié à 95 % exclut zéro ; il est **important** s'il est significatif et si sa moyenne dépasse le seuil d'importance ; il est **robuste** si la borne de l'intervalle dépasse ce seuil, avec le même signe, dans toutes les configurations. Un changement de signe n'est retenu que si des écarts significatifs de signes opposés existent.

- **Capital à l'ouverture** : aucune stratégie n'atteint 100 % du SCR simplifié sans apport. Apport de la gestion passive [intervalle à 95 %] : A 110,4 [108,9 ; 112,1] ; B 29,5 [27,9 ; 31,3] ; C 17,1 [15,6 ; 18,6]. La collecte ne change pas ce besoin : il est calculé sur l'existant en extinction, dans la frontière des contrats (vue simplifiée, qui ne reprend pas les effets de la collecte sur les hypothèses de projection de l'existant).
- **Coût de la recapitalisation** : un apport n'est jamais un profit ; recapitaliser à 100 % coûte à l'actionnaire 10,7 (A), 3,8 (B), 2,3 (C) de valeur (impôt et participation sur les revenus du capital).
- **Valeur de l'existant** (gestion passive, capital à 100 %) : −21,5 (A), 52,3 (B), 74,7 (C). A : l'existant détruit de la valeur pour l'actionnaire une fois recapitalisé.
- **Valeur des affaires nouvelles** (gestion passive) : A de 0,3 à 30,0, marge de 0,9 % à 4,3 % de la VA des primes ; B de 0,7 à 31,7, marge de 1,2 % à 3,2 % de la VA des primes ; C de 1,4 à 31,9, marge de 1,6 % à 3,3 % de la VA des primes. Elle dépend d'abord de l'intensité et de l'élasticité, qui fixent le volume collecté ; la variation d'impôt représente environ la moitié de la valeur avant impôt, bien plus que le taux nominal de l'impôt sur les sociétés, et l'origine de cet écart n'est pas isolée (une explication possible : l'impôt sur les revenus du capital retenu avec la croissance). C'est une valeur avant coût explicite de mobilisation du capital additionnel : une charge frictionnelle annuelle de 2,0 % à 2,3 % du SCR proxy des affaires nouvelles suffirait à l'annuler en collecte centrale (analyse de seuil, `docs/V5_COLLECTE.md`, section 8). Seule cette valeur s'interprète : sa répartition entre les flux des contrats nouveaux et la variation du BE de l'existant déplace les transferts entre générations d'assurés sans les isoler.
- **Réinvestissement progressif** : écart de valeur totale à la gestion passive sans effet important pour les trois profils ; en portefeuille fermé, l'écart de A est statistiquement significatif (contrôle sur tirages indépendants : 0,57 ± 0,10) mais économiquement négligeable.
- **Capital de la croissance** (ordre de grandeur, `docs/V5_COLLECTE.md`, section 8) : à SCR proportionnel à la PM, la collecte centrale demanderait à 10 ans un SCR supplémentaire de 11,0 à 67,1 (A), 13,7 à 62,1 (B), 22,0 à 60,2 (C) pour la gestion passive selon l'élasticité, du même ordre que l'apport d'ouverture de B et C. La politique de distribution retient en même temps des fonds propres comptables : 66,3 (A), 34,2 (B), 34,4 (C) de plus à 10 ans (médianes, élasticité modérée, contre un SCR supplémentaire de 45,4 (A), 43,5 (B), 44,1 (C)) : ce SCR n'appelle donc pas un apport du même montant, mais fonds propres comptables et prudentiels ne coïncident pas. **Aucune stratégie ne garantit la conformité prudentielle future** : l'apport d'ouverture couvre l'existant en extinction à la date d'évaluation, le SCR n'est pas projeté.
- **Intensité centrale** : c0 = 6 % redonne la collecte nette de la place en 2025 (0,59 % la première année dans le modèle, 0,69 % observés), pas ses flux bruts (9,9 % de primes, 9,2 % de sorties) ni la croissance de la PM ; le modèle n'a ni prélèvements sociaux ni arbitrages (`docs/V5_COLLECTE.md`, section 1).

**Écart de valeur totale à la gestion passive, sur la grille de collecte et sous ONC maximale** (15 configurations de collecte et 5 sous ONC maximale, soit 20 par profil) :

| Stratégie | Profil | Effet mesuré (de ... à ...) | Signe | Significatif | Important | Borne au-delà du seuil | Verdict |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| Réinvestissement progressif | A | de 0,1 à 1,2 | positif partout | 20 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Réinvestissement progressif | B | de 0,1 à 0,5 | positif partout | 13 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Réinvestissement progressif | C | de 0,1 à 0,3 | positif partout | 0 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Repositionnement | A | de −17,8 à −3,9 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Repositionnement | B | de −14,8 à −4,9 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Repositionnement | C | de −3,1 à −1,2 | négatif partout | 20 sur 20 | 15 sur 20 | 7 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | A | de −17,5 à −1,5 | négatif partout | 20 sur 20 | 16 sur 20 | 14 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | B | de −26,8 à −4,3 | négatif partout | 20 sur 20 | 20 sur 20 | 19 sur 20 | toujours négatif, non robuste |
| Taux servi compétitif | C | de −27,0 à −5,0 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Taux servi de marge | A | de 3,6 à 15,0 | positif partout | 20 sur 20 | 20 sur 20 | 19 sur 20 | toujours positif, non robuste |
| Taux servi de marge | B | de 2,2 à 13,1 | positif partout | 20 sur 20 | 20 sur 20 | 17 sur 20 | toujours positif, non robuste |
| Taux servi de marge | C | de 1,5 à 11,1 | positif partout | 20 sur 20 | 17 sur 20 | 14 sur 20 | toujours positif, non robuste |
| Liquidité défensive | A | de −7,0 à 3,7 | positif dans 12 sur 20 | 9 sur 20 | 8 sur 20 | 6 sur 20 | change de signe selon les hypothèses |
| Liquidité défensive | B | de −0,1 à 3,1 | positif dans 19 sur 20 | 5 sur 20 | 5 sur 20 | 1 sur 20 | positif là où il est significatif, non robuste |
| Liquidité défensive | C | de 2,9 à 4,1 | positif partout | 20 sur 20 | 20 sur 20 | 5 sur 20 | toujours positif, non robuste |
| Compétitif préservant la PPB | A | de −19,1 à −0,6 | négatif partout | 19 sur 20 | 16 sur 20 | 15 sur 20 | toujours négatif, non robuste |
| Compétitif préservant la PPB | B | de −28,1 à −5,2 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Compétitif préservant la PPB | C | de −28,4 à −5,9 | négatif partout | 20 sur 20 | 20 sur 20 | 20 sur 20 | défavorable, robuste |
| Rétention de capital | A | de −2,1 à −0,6 | négatif partout | 20 sur 20 | 0 sur 20 | 0 sur 20 | sans effet important |
| Rétention de capital | B | de −2,7 à −1,1 | négatif partout | 20 sur 20 | 3 sur 20 | 3 sur 20 | toujours négatif, non robuste |
| Rétention de capital | C | de −2,7 à −1,3 | négatif partout | 20 sur 20 | 5 sur 20 | 4 sur 20 | toujours négatif, non robuste |

## 2. La politique de marge avec collecte

- **A** : avantage de 8,3 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 12,9 ± 0,8 (eta 0,0), 8,2 ± 0,9 (eta 0,5), 6,8 ± 1,0 (eta 0,75), 6,6 ± 1,1 (eta 1,0), 8,0 ± 0,9 (eta 1,5) ; sous ONC maximale 4,9 (eta 0,0), 4,1 (eta 0,5), 3,7 (eta 0,75), 3,6 (eta 1,0), 4,2 (eta 1,5). Cas le moins favorable : 3,6 ± 1,3. Majorant (intensité centrale) : non pour eta 0,0, indéterminé pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **toujours positif, non robuste**.
- **B** : avantage de 9,6 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 12,2 ± 0,9 (eta 0,0), 8,6 ± 0,8 (eta 0,5), 7,2 ± 0,8 (eta 0,75), 7,1 ± 0,9 (eta 1,0), 9,6 ± 0,9 (eta 1,5) ; sous ONC maximale 4,4 (eta 0,0), 2,7 (eta 0,5), 2,2 (eta 0,75), 2,5 (eta 1,0), 3,9 (eta 1,5). Cas le moins favorable : 2,2 ± 1,0. Majorant (intensité centrale) : non pour eta 0,0, oui pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **toujours positif, non robuste**.
- **C** : avantage de 7,3 en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive 9,7 ± 1,2 (eta 0,0), 6,0 ± 1,0 (eta 0,5), 4,5 ± 0,9 (eta 0,75), 4,7 ± 0,8 (eta 1,0), 7,7 ± 0,6 (eta 1,5) ; sous ONC maximale 2,6 (eta 0,0), 1,8 (eta 0,5), 1,5 (eta 0,75), 1,9 (eta 1,0), 3,2 (eta 1,5). Cas le moins favorable : 1,5 ± 0,8. Majorant (intensité centrale) : non pour eta 0,0, oui pour eta 0,5, oui pour eta 0,75, oui pour eta 1,0, indéterminé pour eta 1,5. Verdict sur la grille : **toujours positif, non robuste**.

**Ce qui explique l'avantage mesuré sur la grille.** Trois éléments, mesurés. (1) L'écart de taux servi effectivement réalisé entre la politique de marge et la gestion passive est faible : −46 pb (A), −21 pb (B), −10 pb (C) en moyenne sur 10 ans (probabilité réelle, élasticité modérée), bien moins que le point d'écart des cibles, car la participation minimale de 85 % et les reprises de PPB limitent la baisse ; la perte de collecte en est d'autant réduite. (2) La marge des affaires nouvelles est mince : 3,0 % (A), 2,7 % (B), 2,8 % (C) de la VA des primes pour la gestion passive, alors que l'avantage ne serait annulé, au premier ordre, qu'avec une marge de 13,0 % (A), 10,9 % (B), 8,1 % (C) sur les primes perdues. (3) La gestion passive sert elle-même 0,5 point sous la référence : avec e0 = 0, une élasticité forte lui retire aussi une grande partie de sa collecte. Ce troisième point est une conséquence du choix de e0 et de la conception de la gestion passive, pas un mécanisme indépendant.

**Ce que l'avantage doit aux hypothèses du modèle de collecte** (écart de valeur totale à la gestion passive, intensités centrale et forte, élasticités modérée et soutenue) :

- **A** : e0 = −0,5 point : toujours positif, non robuste (de 5,1 à 9,2) ; collecte pendant 30 ans : toujours positif, non robuste (de 8,4 à 20,4) ; collecte pendant 60 ans : toujours positif, non robuste (de 10,5 à 105,6).
- **B** : e0 = −0,5 point : toujours positif, non robuste (de 1,3 à 8,9) ; collecte pendant 30 ans : toujours positif, non robuste (de 8,5 à 16,9) ; collecte pendant 60 ans : toujours positif, non robuste (de 9,7 à 87,3).
- **C** : e0 = −0,5 point : positif là où il est significatif, non robuste (de −1,6 à 6,5) ; collecte pendant 30 ans : toujours positif, non robuste (de 3,5 à 5,1) ; collecte pendant 60 ans : toujours positif, non robuste (de 2,8 à 13,4).

24 cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à 379,7), dont 22 à l'intensité forte, toutes avec une collecte de 30 ans ou 60 ans : la PM y croît pendant des décennies, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche de conclure dans un sens ou dans l'autre.

Sur l'ensemble des configurations testées (grille, ONC maximale, e0 et horizon de collecte), le verdict est : toujours positif, non robuste (A), toujours positif, non robuste (B), positif là où il est significatif, non robuste (C). g_min = 0 n'est pas testé. **La politique de marge n'est pas qualifiée d'optimale** : son avantage dépend de l'élasticité, non calibrée, de e0 et de l'horizon de collecte ; le modèle ne fait pas racheter l'existant au-delà de la loi de rachat dynamique quand la compétitivité baisse ; il ignore les effets commerciaux et de réputation d'un taux servi durablement inférieur à la référence (écart moyen de −102 pb (A), −65 pb (B), −39 pb (C) sur 10 ans en probabilité réelle) ; et la valeur actionnaire n'est qu'une des dimensions de la section 3.

**Politique compétitive sous ces hypothèses** : toujours négatif, non robuste (A, de −112,9 à −8,5), toujours négatif, non robuste (B, de −183,0 à −16,2), toujours négatif, non robuste (C, de −211,1 à −16,9).

**Déplacement moyen de l'écart de valeur totale** (trois profils, intensité centrale, élasticités modérée et soutenue), du centre à chaque hypothèse : la politique de marge : e0 = −0,5 point de 6,9 à 6,8, collecte pendant 30 ans de 6,9 à 7,3, collecte pendant 60 ans de 6,9 à 8,1 ; la politique compétitive : e0 = −0,5 point de −12,2 à −14,6, collecte pendant 30 ans de −12,2 à −16,4, collecte pendant 60 ans de −12,2 à −20,7. Un seul écart de signe contraire apparaît, sans être significatif (la politique de marge pour C, e0 = −0,5 point, c0 10 %, eta 1,0 : −1,6 ± 2,6) : il ne suffit pas à établir un changement de signe, mais l'avantage n'y est plus démontré.

## 3. Synthèse par profil

Tous les chiffres des tableaux sont des écarts à la gestion passive, capital à 100 %. Valeur de l'existant : portefeuille fermé (intervalle apparié). Affaires nouvelles et indicateurs réels : collecte centrale (c0 = 6 %), élasticité modérée (eta = 0,5). Valeur totale : verdict sur la grille et sous ONC maximale. Rentabilité, compétitivité (taux servi moyen du fonds) et liquidité en probabilité réelle, sans intervalle ; capital : apport à 100 % (intervalle de rééchantillonnage).

### Profil A

Indicateur de couverture simplifié du SCR sans apport : 2 %. Gestion passive avec collecte centrale modérée : valeur de l'existant −21,5, valeur des affaires nouvelles 7,0, rendement réel des fonds propres 5,3 % (sous le rendement exigé fictif de 8 %), écart du taux servi à la référence de −56 pb, collecte 1-10 de 447,2 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,5) | neutre (0,4) | sans effet important (de 0,1 à 1,2) | neutre (−0,17 pt) | neutre (−1 pb) | favorable (−14,0) | neutre (0,2) |
| Repositionnement | défavorable (−12,3) | défavorable (−2,9) | défavorable, robuste (de −17,8 à −3,9) | défavorable (−2,34 pt) | défavorable (−6 pb) | défavorable (14,8) | défavorable (19,0) |
| Taux servi compétitif | défavorable (−7,0) | neutre (−1,5) | toujours négatif, non robuste (de −17,5 à −1,5) | défavorable (−0,29 pt) | favorable (30 pb) | neutre (0,6) | favorable (−10,5) |
| Taux servi de marge | favorable (8,3) | neutre (−0,1, ns) | toujours positif, non robuste (de 3,6 à 15,0) | neutre (0,20 pt) | défavorable (−46 pb) | défavorable (47,6) | défavorable (8,3) |
| Liquidité défensive | neutre (1,6) | défavorable (−2,4) | change de signe selon les hypothèses (de −7,0 à 3,7) | défavorable (−1,24 pt) | neutre (−4 pb) | défavorable (9,9) | défavorable (18,0) |
| Compétitif préservant la PPB | défavorable (−4,6) | défavorable (−3,4) | toujours négatif, non robuste (de −19,1 à −0,6) | défavorable (−0,48 pt) | favorable (31 pb) | neutre (−4,0) | neutre (−1,6) |
| Rétention de capital | neutre (−1,1) | neutre (−0,3) | sans effet important (de −2,1 à −0,6) | neutre (−0,10 pt) | neutre (0 pb) | neutre (−5,3) | neutre (−0,8) |

**Lecture.**

- **Désavantage de valeur totale robuste** : Repositionnement.
- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Taux servi compétitif (toujours négatif, non robuste), Taux servi de marge (toujours positif, non robuste), Liquidité défensive (change de signe selon les hypothèses), Compétitif préservant la PPB (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (20 configurations sur 20). Même premier rang sur la grille, mais conditionnel aux hypothèses non calibrées (élasticité, e0, horizon de collecte, loi de rachat) : il n'est pas présenté comme optimal.

### Profil B

Indicateur de couverture simplifié du SCR sans apport : 72 %. Gestion passive avec collecte centrale modérée : valeur de l'existant 52,3, valeur des affaires nouvelles 8,4, rendement réel des fonds propres 10,2 % (au-dessus du rendement exigé fictif de 8 %), écart du taux servi à la référence de −44 pb, collecte 1-10 de 495,9 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,1, ns) | neutre (0,3) | sans effet important (de 0,1 à 0,5) | neutre (−0,20 pt) | neutre (−2 pb) | neutre (−0,1) | neutre (−0,2) |
| Repositionnement | défavorable (−9,1) | neutre (−2,0) | défavorable, robuste (de −14,8 à −4,9) | défavorable (−2,44 pt) | favorable (6 pb) | défavorable (19,7) | défavorable (24,9) |
| Taux servi compétitif | défavorable (−11,6) | défavorable (−3,7) | toujours négatif, non robuste (de −26,8 à −4,3) | défavorable (−0,65 pt) | favorable (40 pb) | neutre (0,0) | favorable (−2,3) |
| Taux servi de marge | favorable (9,6) | neutre (−0,9) | toujours positif, non robuste (de 2,2 à 13,1) | favorable (0,36 pt) | défavorable (−21 pb) | neutre (4,5) | favorable (−2,3) |
| Liquidité défensive | neutre (1,0, ns) | neutre (−0,5, ns) | positif là où il est significatif, non robuste (de −0,1 à 3,1) | défavorable (−0,52 pt) | défavorable (−5 pb) | neutre (0,7) | neutre (−0,2, ns) |
| Compétitif préservant la PPB | défavorable (−11,7) | défavorable (−4,6) | défavorable, robuste (de −28,1 à −5,2) | défavorable (−0,91 pt) | favorable (39 pb) | neutre (0,1) | neutre (−0,7, ns) |
| Rétention de capital | neutre (−1,5) | neutre (−0,3) | toujours négatif, non robuste (de −2,7 à −1,1) | défavorable (−0,68 pt) | neutre (0 pb) | neutre (−0,1) | neutre (0,6) |

**Lecture.**

- **Désavantage de valeur totale robuste** : Repositionnement, Compétitif préservant la PPB.
- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Taux servi compétitif (toujours négatif, non robuste), Taux servi de marge (toujours positif, non robuste), Liquidité défensive (positif là où il est significatif, non robuste), Rétention de capital (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (17 configurations sur 20), Liquidité défensive (3 configurations sur 20). **Il change avec les hypothèses.**

### Profil C

Indicateur de couverture simplifié du SCR sans apport : 83 %. Gestion passive avec collecte centrale modérée : valeur de l'existant 74,7, valeur des affaires nouvelles 9,9, rendement réel des fonds propres 11,6 % (au-dessus du rendement exigé fictif de 8 %), écart du taux servi à la référence de −29 pb, collecte 1-10 de 556,6 (réel).

| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,0, ns) | neutre (0,1, ns) | sans effet important (de 0,1 à 0,3) | neutre (−0,16 pt) | neutre (−3 pb) | neutre (−0,5) | neutre (0,1, ns) |
| Repositionnement | neutre (−1,6) | neutre (−1,1) | toujours négatif, non robuste (de −3,1 à −1,2) | défavorable (−0,67 pt) | neutre (4 pb) | neutre (1,3) | défavorable (5,8) |
| Taux servi compétitif | défavorable (−12,2) | défavorable (−4,3) | défavorable, robuste (de −27,0 à −5,0) | défavorable (−0,45 pt) | favorable (30 pb) | neutre (−1,6) | neutre (−1,6) |
| Taux servi de marge | favorable (7,3) | neutre (−1,3) | toujours positif, non robuste (de 1,5 à 11,1) | favorable (0,60 pt) | défavorable (−10 pb) | défavorable (24,8) | favorable (−4,8) |
| Liquidité défensive | favorable (2,8) | neutre (0,2, ns) | toujours positif, non robuste (de 2,9 à 4,1) | défavorable (−0,51 pt) | défavorable (−10 pb) | neutre (−2,2) | neutre (1,7) |
| Compétitif préservant la PPB | défavorable (−12,9) | défavorable (−4,6) | défavorable, robuste (de −28,4 à −5,9) | défavorable (−0,73 pt) | favorable (31 pb) | neutre (−1,7) | neutre (0,2, ns) |
| Rétention de capital | neutre (−1,6) | neutre (−0,4) | toujours négatif, non robuste (de −2,7 à −1,3) | défavorable (−0,86 pt) | neutre (0 pb) | neutre (−0,3) | neutre (0,4) |

**Lecture.**

- **Désavantage de valeur totale robuste** : Taux servi compétitif, Compétitif préservant la PPB.
- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : Repositionnement (toujours négatif, non robuste), Taux servi de marge (toujours positif, non robuste), Liquidité défensive (toujours positif, non robuste), Rétention de capital (toujours négatif, non robuste).
- **Premier rang de la valeur totale** : Taux servi de marge (13 configurations sur 20), Liquidité défensive (7 configurations sur 20). **Il change avec les hypothèses.**

## 4. Ce que l'étude ne permet pas de conclure

- **Élasticité de la collecte et forme de la réaction** : aucune donnée vérifiée. Sur l'ensemble des configurations testées (y compris les cellules imprécises à 30 et 60 ans), l'écart de valeur totale va de −1,6 à 105,6 pour la politique de marge ; de −211,1 à −1,5 pour la politique compétitive. Un seul écart de signe contraire apparaît, sans être significatif (la politique de marge pour C, e0 = −0,5 point, c0 10 %, eta 1,0 : −1,6 ± 2,6) : il ne suffit pas à établir un changement de signe, mais l'avantage n'y est plus démontré.
- **Comportement de rachat** : la loi centrale vient des V1 à V4, les corridors ONC de 2013 servent de sensibilité ; aucune donnée 2026 ne les calibre ; la perte de compétitivité ne fait pas racheter l'existant au-delà de cette loi.
- **Capital futur** : le SCR n'est pas projeté ; le capital de la croissance n'est estimé qu'en ordre de grandeur (SCR proportionnel à la PM) ; fonds propres comptables et prudentiels ne coïncident pas ; aucune stratégie ne garantit la conformité prudentielle future.
- **Flux de la place** : c0 = 6 % ne fait qu'approcher la collecte nette de 2025 (0,59 % de la PM contre 0,69 %), sur une seule année, avec des flux bruts plus faibles ; prélèvements sociaux et arbitrages ne sont pas modélisés.
- **Lecture statistique** : les intervalles à 95 % sont calculés cellule par cellule, ils ne sont pas simultanés : sur l'ensemble des stratégies, profils et hypothèses, quelques écarts peuvent paraître significatifs par hasard ; « robuste » est un critère descriptif, interne à la grille testée.
- **Liquidité** : quantiles à 99 % estimés sur 1 000 scénarios en probabilité réelle, soit une dizaine de scénarios dans la queue, sans intervalle de confiance ; les écarts proches du seuil sont fragiles.
- **Mécanismes absents** : inflation et attractivité du taux servi réel, arbitrages entre fonds euros et unités de compte, migration de notation des obligations, comportement de rachat propre aux contrats nouveaux (même loi que l'existant), politique de distribution fondée sur la couverture du SCR plutôt que sur un ratio comptable ; chacun peut modifier le classement des politiques de taux servi.
- **Date des données de marché** : courbe EIOPA du 31/10/2026 (marchés du 30/10) et TEC du 04/11/2026 ; l'écart de dates est assumé, non corrigé.
- **Vue prudentielle** : indicateurs simplifiés (base avec VA, risque opérationnel par la seule formule sur provisions, ni contrepartie, ni concentration, ni immobilier, ni change, impôts différés actifs non reconnus), pas de mesure transitoire ; ce ne sont pas des ratios réglementaires. Elle est calculée en extinction, sans les effets de la collecte sur les hypothèses de projection de l'existant ; la réserve de capitalisation suit le principe de l'article R.351-2-1 du Code des assurances sans en reproduire toutes les modalités.
- **Valeur des affaires nouvelles** : hors Solvabilité II, avant coût explicite de mobilisation du capital additionnel ; seuls les coûts frictionnels du capital comptable retenu (impôt et participation sur ses revenus) sont déduits ; le coût du capital immobilisé pour le SCR supplémentaire n'est mesuré que par un seuil, et aucune marge pour risques non couvrables n'est déduite.

## 5. Contrôles et corrections

**Reproductibilité.** Sur un clone propre du dépôt, tous les tests passent, les documents et les figures se régénèrent à l'identique depuis les résultats versionnés, et un échantillon de résultats recalculé sans cache est identique aux résultats versionnés (`docs/V5_REPRODUCTION.md`).

**Correction ayant modifié des résultats.** Une première version de la répartition de l'intérêt entre générations créditait les contrats nouveaux au-delà de l'intérêt décidé quand le plancher de TMG du fonds était juste atteint (profil A). Elle est corrigée, couverte par un test de non-régression, et les résultats concernés ont été recalculés.

**Contrôles complémentaires.** Grille d'élasticité densifiée (0,75 et 1,0), e0 et horizon de collecte testés à part, loi de rachat ONC maximale appliquée aux huit stratégies ; critères de lecture complets (significatif, important, robuste ; « non concluant » pour des signes mêlés sans écart significatif ; « sans effet important » seulement si l'intervalle entier reste sous le seuil ; changement de signe retenu seulement s'il repose sur des écarts significatifs) ; variantes de liquidation du contrat sans marge explicite, qui ramènent son résidu sous 0,1 % des primes pour B et C et en identifient la cause pour A ; seuil de coût du capital des affaires nouvelles ; traitement de la réserve de capitalisation confronté à l'article R.351-2-1 du Code des assurances.

Ces contrôles vérifient la cohérence interne du modèle et la reproductibilité des résultats ; ils ne constituent pas une validation actuarielle indépendante.

