# V5 : synthèse exécutive des stratégies ALM

Trois profils fictifs de fonds euros, huit stratégies, une base de capital commune : chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 %, et sa valeur est nette de cet apport. Détail, méthode et limites : `docs/V5_STRATEGIES.md` ; généré par `scripts/v5_synthese_strategies.py` depuis `resultats/v5_consolidation.json`. Unités fictives : 1 unité = 10 M€.

**À lire avant les tableaux.** Analyse exploratoire, pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. Le portefeuille est fermé : la perte ou le gain de collecte d'une politique de taux servi n'y est pas compté (collecte nouvelle : `docs/V5_COLLECTE.md`). Les probabilités de recapitalisation sont conditionnelles aux hypothèses du modèle. Aucune stratégie n'est désignée gagnante.

**Cinq dimensions, écarts à la gestion passive.** Valeur actionnaire : valeur nette risque neutre (après apport, apports ultérieurs et impôt). Rentabilité : rendement des fonds propres comptables en probabilité réelle, années 1 à 10. Compétitivité : écart du taux servi à la référence des assurés (réel). Liquidité : moins-values réalisées sur 10 ans, quantile 99 % (réel). Capital : apport nécessaire pour 100 % du SCR simplifié. « Neutre » : écart sous le seuil d'importance fixé à l'avance (2 % du SCR pour la valeur et l'apport, 25 pb de rentabilité, 5 pb de taux servi, 5 % du SCR de moins-values) ou non significatif (ns : intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle n'ont pas d'intervalle). « Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital (100 % et 150 %) et sous les trois sensibilités testées (réaction forte des assurés (ONC max.), transmission immédiate des taux à la référence, défaut corrélé par bloc souverain).

## Constats communs aux trois profils

- **Capital** : aucune stratégie n'atteint 100 % du SCR simplifié sans apport. Apport nécessaire en gestion passive, avec son intervalle à 95 % : A 110,4 [108,9 ; 112,1] ; B 29,5 [27,9 ; 31,3] ; C 17,1 [15,6 ; 18,6]. Recapitaliser coûte de la valeur à l'actionnaire (impôt et participation sur les revenus du capital) : 10,7 (A), 3,8 (B), 2,3 (C).
- **MCR** : le plancher de 25 % du SCR s'applique (A, B, C) ; les indicateurs MCR élevés reflètent ce plancher, pas une marge de sécurité propre.
- **Réinvestissement progressif** : écarts de valeur 0,55 ± 0,13 (A), 0,10 ± 0,21 (B), 0,02 ± 0,47 (C) ; pour A, l'écart se retrouve sur des tirages indépendants (0,57 ± 0,10, 2 000 scénarios) ; tous sous le seuil d'importance de 2 % du SCR. Il n'est pas économiquement distinguable de la gestion passive, même quand l'écart est statistiquement significatif.
- **Politique de marge** : la plus forte valeur actionnaire au centre (A, B, C), au prix d'un taux servi plus bas ; écart de valeur au centre puis sous une réaction forte des assurés : 8,3 puis 4,0 (A), 9,6 puis 3,8 (B), 7,3 puis 2,7 (C). Le portefeuille fermé ne compte pas la collecte : ce résultat n'est ni une conclusion ni, par principe, un majorant (avec collecte : `docs/V5_COLLECTE.md` et `docs/V5_SYNTHESE_FINALE.md`).
- **Politique compétitive** : écart de valeur et gain de taux servi par rapport à la gestion passive : −7,0 et 13 pb (A), −11,6 et 28 pb (B), −12,2 et 20 pb (C).
- **Préserver la PPB** dans la politique compétitive (variante comparée à la version de base, mêmes scénarios) : 2,4 de valeur, 8 pb de taux servi, −35 pb de rachat (A) ; −0,1 de valeur, 3 pb de taux servi, −52 pb de rachat (B) ; −0,6 de valeur, 1 pb de taux servi, −17 pb de rachat (C). Les rachats baissent ; les gains de taux servi et de valeur restent modestes, sauf pour A (détail : `docs/V5_STRATEGIES.md`, section 5). Le coût en valeur de la politique compétitive par rapport à la gestion passive demeure.
- **Rétention de capital** : écart de valeur et de rentabilité −1,1 et −0,15 pt (A), −1,5 et −0,93 pt (B), −1,6 et −1,23 pt (C). Le capital conservé supporte l'impôt et partage ses revenus avec les assurés, et dilue le rendement des fonds propres. Son bénéfice attendu, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR.
- **Liquidité défensive** : écart de valeur risque neutre et de rentabilité réelle 1,6 et −1,21 pt (A), 1,0 et −0,46 pt (B), 2,8 et −0,40 pt (C). Les deux mesures vont en sens opposés : moins d'actions réduit le coût des options en risque neutre et fait perdre la prime actions en probabilité réelle ; le gain de valeur n'est important que pour C. Valeur risque neutre et rentabilité réelle sont donc présentées séparément, jamais combinées.

## Profil A

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 2,2 pour un SCR simplifié de 118,6, indicateur de 2 % [−1 % ; 4 %]. Apport pour 100 % : 110,4 ; pour 150 % : 159,5. À 100 %, valeur nette de −21,5, rendement réel des fonds propres de 4,9 % (sous le rendement exigé fictif de 8 %), taux servi moyen de 2,30 % (−70 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,5) | neutre (−0,07 pt) | neutre (−1 pb) | neutre (−5,0) | neutre (0,2) | non |
| Repositionnement | défavorable (−12,3) | défavorable (−2,69 pt) | favorable (10 pb) | favorable (−27,4) | défavorable (19,0) | oui, défavorable |
| Taux servi compétitif | défavorable (−7,0) | défavorable (−0,30 pt) | favorable (13 pb) | défavorable (15,0) | favorable (−10,5) | oui, défavorable |
| Taux servi de marge | favorable (8,3) | favorable (0,29 pt) | défavorable (−40 pb) | défavorable (47,4) | défavorable (8,3) | oui, favorable |
| Liquidité défensive | neutre (1,6) | défavorable (−1,21 pt) | neutre (−4 pb) | neutre (−4,9) | défavorable (18,0) | non |
| Compétitif préservant la PPB | défavorable (−4,6) | défavorable (−0,40 pt) | favorable (22 pb) | neutre (5,4) | neutre (−1,6) | oui, défavorable |
| Rétention de capital | neutre (−1,1) | neutre (−0,15 pt) | neutre (1 pb) | neutre (−3,4) | neutre (−0,8) | non |

**Lecture.**

- **Compromis** : Repositionnement améliore compétitivité, liquidité mais dégrade valeur actionnaire, rentabilité, capital ; Taux servi compétitif améliore compétitivité, capital mais dégrade valeur actionnaire, rentabilité, liquidité ; Taux servi de marge améliore valeur actionnaire, rentabilité mais dégrade compétitivité, liquidité, capital ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, rentabilité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Liquidité défensive.
- **Sans effet important** : Réinvestissement progressif, Rétention de capital.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », et ce rang tient sous les trois sensibilités testées. Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Profil B

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 72,7 pour un SCR simplifié de 101,4, indicateur de 72 % [70 % ; 73 %]. Apport pour 100 % : 29,5 ; pour 150 % : 81,2. À 100 %, valeur nette de 52,3, rendement réel des fonds propres de 10,1 % (au-dessus du rendement exigé fictif de 8 %), taux servi moyen de 2,58 % (−41 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,1, ns) | neutre (−0,10 pt) | neutre (−2 pb) | neutre (−0,3) | neutre (−0,2) | non |
| Repositionnement | défavorable (−9,1) | défavorable (−2,46 pt) | favorable (15 pb) | défavorable (18,6) | défavorable (24,9) | oui, défavorable |
| Taux servi compétitif | défavorable (−11,6) | défavorable (−0,54 pt) | favorable (28 pb) | neutre (2,4) | favorable (−2,3) | oui, défavorable |
| Taux servi de marge | favorable (9,6) | favorable (0,56 pt) | défavorable (−17 pb) | défavorable (8,7) | favorable (−2,3) | oui, favorable |
| Liquidité défensive | neutre (1,0, ns) | défavorable (−0,46 pt) | défavorable (−7 pb) | neutre (−0,2) | neutre (−0,2, ns) | non |
| Compétitif préservant la PPB | défavorable (−11,7) | défavorable (−0,92 pt) | favorable (31 pb) | neutre (1,8) | neutre (−0,7, ns) | oui, défavorable |
| Rétention de capital | neutre (−1,5) | défavorable (−0,93 pt) | neutre (0 pb) | neutre (−1,0) | neutre (0,6) | non |

**Lecture.**

- **Compromis** : Repositionnement améliore compétitivité mais dégrade valeur actionnaire, rentabilité, liquidité, capital ; Taux servi compétitif améliore compétitivité, capital mais dégrade valeur actionnaire, rentabilité ; Taux servi de marge améliore valeur actionnaire, rentabilité, capital mais dégrade compétitivité, liquidité ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, rentabilité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Liquidité défensive, Rétention de capital (pour la rétention, le bénéfice attendu sur la couverture des années suivantes n'est pas mesuré).
- **Sans effet important** : Réinvestissement progressif.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », et ce rang tient sous les trois sensibilités testées. Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Profil C

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 81,8 pour un SCR simplifié de 98,4, indicateur de 83 % [82 % ; 85 %]. Apport pour 100 % : 17,1 ; pour 150 % : 68,3. À 100 %, valeur nette de 74,7, rendement réel des fonds propres de 11,9 % (au-dessus du rendement exigé fictif de 8 %), taux servi moyen de 2,83 % (−17 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,0, ns) | neutre (−0,07 pt) | neutre (−1 pb) | neutre (−1,0) | neutre (0,1, ns) | non |
| Repositionnement | neutre (−1,6) | défavorable (−0,66 pt) | favorable (6 pb) | neutre (2,5) | défavorable (5,8) | non |
| Taux servi compétitif | défavorable (−12,2) | défavorable (−0,40 pt) | favorable (20 pb) | défavorable (6,4) | neutre (−1,6) | oui, défavorable |
| Taux servi de marge | favorable (7,3) | favorable (0,71 pt) | défavorable (−7 pb) | défavorable (26,2) | favorable (−4,8) | oui, favorable |
| Liquidité défensive | favorable (2,8) | défavorable (−0,40 pt) | défavorable (−9 pb) | favorable (−7,5) | neutre (1,7) | oui, favorable |
| Compétitif préservant la PPB | défavorable (−12,9) | défavorable (−0,73 pt) | favorable (21 pb) | neutre (3,0) | neutre (0,2, ns) | oui, défavorable |
| Rétention de capital | neutre (−1,6) | défavorable (−1,23 pt) | neutre (0 pb) | neutre (−3,6) | neutre (0,4) | non |

**Lecture.**

- **Compromis** : Repositionnement améliore compétitivité mais dégrade rentabilité, capital ; Taux servi compétitif améliore compétitivité mais dégrade valeur actionnaire, rentabilité, liquidité ; Taux servi de marge améliore valeur actionnaire, rentabilité, capital mais dégrade compétitivité, liquidité ; Liquidité défensive améliore valeur actionnaire, liquidité mais dégrade rentabilité, compétitivité ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, rentabilité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Rétention de capital (pour la rétention, le bénéfice attendu sur la couverture des années suivantes n'est pas mesuré).
- **Sans effet important** : Réinvestissement progressif.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », mais le premier rang change : « Liquidité défensive » sous réaction forte des assurés (ONC max.). Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Ce qui manque pour conclure

1. **Collecte nouvelle sensible au taux servi relatif** : traitée dans `docs/V5_COLLECTE.md` ; la synthèse économique finale (`docs/V5_SYNTHESE_FINALE.md`) réunit les deux vues.
2. **Comportement des assurés** : aucune donnée 2026 ne calibre la réaction aux écarts de taux ; les corridors ONC de 2013 restent une plage de sensibilité.
3. **Vue prudentielle complète** : modules non modélisés, mesure transitoire, ajustement symétrique, impôts différés actifs ; les indicateurs restent indicatifs.
4. **ACPR n° 185** : non consulté ; aucun chiffre de place n'a servi à ajuster les profils.

