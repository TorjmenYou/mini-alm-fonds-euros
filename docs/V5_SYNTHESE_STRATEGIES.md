# V5 : synthèse exécutive des stratégies ALM

Trois profils fictifs de fonds euros, huit stratégies, une base de capital commune : chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 %, et sa valeur est nette de cet apport. Détail, méthode et limites : `docs/V5_STRATEGIES.md` ; généré par `scripts/v5_synthese_strategies.py` depuis `resultats/v5_consolidation.json`. Unités fictives : 1 unité = 10 M€.

**À lire avant les tableaux.** Analyse exploratoire, pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. Le portefeuille est fermé : la perte ou le gain de collecte d'une politique de taux servi n'y est pas compté (collecte nouvelle : `docs/V5_COLLECTE.md`). Les probabilités de recapitalisation sont conditionnelles aux hypothèses du modèle. Aucune stratégie n'est désignée gagnante.

**Cinq dimensions, écarts à la gestion passive.** Valeur actionnaire : valeur nette risque neutre (après apport, apports ultérieurs et impôt). Rentabilité : rendement des fonds propres comptables en probabilité réelle, années 1 à 10. Compétitivité : écart du taux servi à la référence des assurés (réel). Liquidité : moins-values réalisées sur 10 ans, quantile 99 % (réel). Capital : apport nécessaire pour 100 % du SCR simplifié. « Neutre » : écart sous le seuil d'importance fixé à l'avance (2 % du SCR pour la valeur et l'apport, 25 pb de rentabilité, 5 pb de taux servi, 5 % du SCR de moins-values) ou non significatif (ns : intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle n'ont pas d'intervalle). « Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital (100 % et 150 %) et sous les trois sensibilités testées (réaction forte des assurés (ONC max.), transmission immédiate des taux à la référence, défaut corrélé par bloc souverain).

## Constats communs aux trois profils

- **Capital** : sans apport, l'indicateur atteint 100 % du SCR simplifié pour 6 couples profil-stratégie sur 24 (profil C : 6 stratégies), dont l'apport estimé est donc nul. Apport nécessaire en gestion passive, avec son intervalle à 95 % : A 101,0 [99,4 ; 102,8] ; B 27,6 [26,1 ; 32,5] ; C 0,0 [0,0 ; 0,0]. Recapitaliser coûte de la valeur à l'actionnaire (impôt et participation sur les revenus du capital) : 9,9 (A), 3,9 (B), 0,0 (C).
- **MCR** : le plancher de 25 % du SCR s'applique (A, B, C) ; les indicateurs MCR élevés reflètent ce plancher, pas une marge de sécurité propre.
- **Réinvestissement progressif** : écarts de valeur 0,39 ± 0,16 (A), 0,26 ± 0,26 (B), 0,04 ± 0,55 (C) ; pour A, l'écart se retrouve sur des tirages indépendants (0,41 ± 0,12, 2 000 scénarios) ; tous sous le seuil d'importance de 2 % du SCR. Il n'est pas économiquement distinguable de la gestion passive, même quand l'écart est statistiquement significatif.
- **Politique de marge** : la plus forte valeur actionnaire au centre (A, B, C), au prix d'un taux servi plus bas ; écart de valeur au centre puis sous une réaction forte des assurés : 5,8 puis 3,3 (A), 6,3 puis 1,7 (B), 3,1 puis 0,9 (C). Le portefeuille fermé ne compte pas la collecte : ce résultat n'est ni une conclusion ni, par principe, un majorant (avec collecte : `docs/V5_COLLECTE.md` et `docs/V5_SYNTHESE_FINALE.md`).
- **Politique compétitive** : écart de valeur et gain de taux servi par rapport à la gestion passive : −6,0 et 13 pb (A), −10,1 et 24 pb (B), −9,8 et 13 pb (C).
- **Préserver la PPB** dans la politique compétitive (variante comparée à la version de base, mêmes scénarios) : 1,9 de valeur, 5 pb de taux servi, −26 pb de rachat (A) ; 0,6 de valeur, 1 pb de taux servi, −32 pb de rachat (B) ; 0,0 de valeur, 0 pb de taux servi, −1 pb de rachat (C). Les rachats baissent ; les gains de taux servi et de valeur restent modestes (détail : `docs/V5_STRATEGIES.md`, section 5). Le coût en valeur de la politique compétitive par rapport à la gestion passive demeure.
- **Rétention de capital** : écart de valeur et de rentabilité −1,1 et −0,12 pt (A), −1,4 et −0,64 pt (B), −1,3 et −1,18 pt (C). Le capital conservé supporte l'impôt et partage ses revenus avec les assurés, et dilue le rendement des fonds propres. Son bénéfice attendu, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR.
- **Liquidité défensive** : écart de valeur risque neutre et de rentabilité réelle 0,8 et −0,70 pt (A), 1,2 et −0,31 pt (B), 3,1 et −0,20 pt (C). Les deux mesures vont en sens opposés : moins d'actions réduit le coût des options en risque neutre et fait perdre la prime actions en probabilité réelle ; le gain de valeur n'est important que pour C. Valeur risque neutre et rentabilité réelle sont donc présentées séparément, jamais combinées.

## Profil A

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 13,9 pour un SCR simplifié de 119,4, indicateur de 12 % [9 % ; 14 %]. Apport pour 100 % : 101,0 ; pour 150 % : 149,7. À 100 %, valeur nette de −5,4, rendement réel des fonds propres de 4,4 % (sous le rendement exigé fictif de 8 %), taux servi moyen de 2,30 % (−66 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,4) | neutre (−0,02 pt) | neutre (0 pb) | favorable (−10,4) | neutre (0,7) | non |
| Repositionnement | défavorable (−16,5) | défavorable (−2,50 pt) | favorable (11 pb) | favorable (−18,3) | défavorable (19,2) | oui, défavorable |
| Taux servi compétitif | défavorable (−6,0) | neutre (−0,11 pt) | favorable (13 pb) | défavorable (19,9) | favorable (−11,4) | oui, défavorable |
| Taux servi de marge | favorable (5,8) | neutre (0,05 pt) | défavorable (−27 pb) | défavorable (26,7) | défavorable (6,1) | oui, favorable |
| Liquidité défensive | neutre (0,8, ns) | défavorable (−0,70 pt) | neutre (−3 pb) | neutre (−3,2) | défavorable (13,5) | non |
| Compétitif préservant la PPB | défavorable (−4,1) | neutre (−0,20 pt) | favorable (19 pb) | défavorable (7,4) | neutre (−1,4) | oui, défavorable |
| Rétention de capital | neutre (−1,1) | neutre (−0,12 pt) | neutre (1 pb) | neutre (−3,5) | neutre (−0,4) | non |

**Lecture.**

- **Compromis** : Repositionnement améliore compétitivité, liquidité mais dégrade valeur actionnaire, rentabilité, capital ; Taux servi compétitif améliore compétitivité, capital mais dégrade valeur actionnaire, liquidité ; Taux servi de marge améliore valeur actionnaire mais dégrade compétitivité, liquidité, capital ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, liquidité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Liquidité défensive.
- **Sans effet important** : Rétention de capital.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », mais le premier rang change : « Liquidité défensive » sous réaction forte des assurés (ONC max.). Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Profil B

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 67,5 pour un SCR simplifié de 94,5, indicateur de 71 % [67 % ; 73 %]. Apport pour 100 % : 27,6 ; pour 150 % : 75,4. À 100 %, valeur nette de 57,5, rendement réel des fonds propres de 8,5 % (au-dessus du rendement exigé fictif de 8 %), taux servi moyen de 2,66 % (−31 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,3) | neutre (−0,03 pt) | neutre (−1 pb) | neutre (−0,2) | neutre (−0,1, ns) | non |
| Repositionnement | défavorable (−11,7) | défavorable (−1,81 pt) | favorable (18 pb) | défavorable (11,9) | défavorable (20,1) | oui, défavorable |
| Taux servi compétitif | défavorable (−10,1) | défavorable (−0,27 pt) | favorable (24 pb) | neutre (2,2) | neutre (−1,1) | oui, défavorable |
| Taux servi de marge | favorable (6,3) | favorable (0,35 pt) | défavorable (−8 pb) | défavorable (6,2) | favorable (−3,7) | oui, favorable |
| Liquidité défensive | neutre (1,2, ns) | défavorable (−0,31 pt) | défavorable (−9 pb) | neutre (−1,0) | neutre (0,8, ns) | non |
| Compétitif préservant la PPB | défavorable (−9,5) | défavorable (−0,44 pt) | favorable (24 pb) | neutre (2,1) | neutre (−0,3, ns) | oui, défavorable |
| Rétention de capital | neutre (−1,4) | défavorable (−0,64 pt) | neutre (0 pb) | neutre (−0,6) | neutre (0,4) | non |

**Lecture.**

- **Compromis** : Repositionnement améliore compétitivité mais dégrade valeur actionnaire, rentabilité, liquidité, capital ; Taux servi compétitif améliore compétitivité mais dégrade valeur actionnaire, rentabilité ; Taux servi de marge améliore valeur actionnaire, rentabilité, capital mais dégrade compétitivité, liquidité ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, rentabilité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Liquidité défensive, Rétention de capital (pour la rétention, le bénéfice attendu sur la couverture des années suivantes n'est pas mesuré).
- **Sans effet important** : Réinvestissement progressif.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », mais le premier rang change : « Liquidité défensive » sous réaction forte des assurés (ONC max.) ; « Liquidité défensive » sous transmission immédiate des taux à la référence. Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Profil C

Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de 86,4 pour un SCR simplifié de 83,9, indicateur de 103 % [101 % ; 105 %]. Apport pour 100 % : 0,0 ; pour 150 % : 42,4. À 100 %, valeur nette de 82,8, rendement réel des fonds propres de 11,9 % (au-dessus du rendement exigé fictif de 8 %), taux servi moyen de 2,97 % (0 pb sous la référence).

| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |
| --- | --- | --- | --- | --- | --- | --- |
| Réinvestissement progressif | neutre (0,0, ns) | neutre (−0,02 pt) | neutre (−1 pb) | neutre (−1,1) | neutre (0,0, ns) | non |
| Repositionnement | neutre (−1,4) | défavorable (−0,43 pt) | neutre (4 pb) | neutre (3,6) | défavorable (2,2) | non |
| Taux servi compétitif | défavorable (−9,8) | défavorable (−0,32 pt) | favorable (13 pb) | défavorable (5,0) | neutre (0,0, ns) | oui, défavorable |
| Taux servi de marge | favorable (3,1) | neutre (0,03 pt) | neutre (−2 pb) | défavorable (19,3) | neutre (0,0, ns) | oui, favorable |
| Liquidité défensive | favorable (3,1) | neutre (−0,20 pt) | défavorable (−7 pb) | favorable (−5,8) | neutre (0,0, ns) | oui, favorable |
| Compétitif préservant la PPB | défavorable (−9,8) | défavorable (−0,44 pt) | favorable (13 pb) | défavorable (6,0) | neutre (0,4, ns) | oui, défavorable |
| Rétention de capital | neutre (−1,3) | défavorable (−1,18 pt) | neutre (0 pb) | neutre (−1,9) | neutre (0,0, ns) | non |

**Lecture.**

- **Compromis** : Taux servi compétitif améliore compétitivité mais dégrade valeur actionnaire, rentabilité, liquidité ; Taux servi de marge améliore valeur actionnaire mais dégrade liquidité ; Liquidité défensive améliore valeur actionnaire, liquidité mais dégrade compétitivité ; Compétitif préservant la PPB améliore compétitivité mais dégrade valeur actionnaire, rentabilité, liquidité.
- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : Repositionnement, Rétention de capital (pour la rétention, le bénéfice attendu sur la couverture des années suivantes n'est pas mesuré).
- **Sans effet important** : Réinvestissement progressif.
- **Valeur** : la plus forte valeur nette au centre est celle de « Taux servi de marge », mais le premier rang change : « Liquidité défensive » sous réaction forte des assurés (ONC max.) ; « Liquidité défensive » sous transmission immédiate des taux à la référence ; « Liquidité défensive » sous défaut corrélé par bloc souverain. Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`). Aucune stratégie n'est désignée gagnante.

## Ce qui manque pour conclure

1. **Collecte nouvelle sensible au taux servi relatif** : traitée dans `docs/V5_COLLECTE.md` ; la synthèse économique finale (`docs/V5_SYNTHESE_FINALE.md`) réunit les deux vues.
2. **Comportement des assurés** : aucune donnée 2026 ne calibre la réaction aux écarts de taux ; les corridors ONC de 2013 restent une plage de sensibilité.
3. **Vue prudentielle complète** : modules non modélisés, mesure transitoire, ajustement symétrique, impôts différés actifs ; les indicateurs restent indicatifs.
4. **ACPR n° 185** : non consulté ; aucun chiffre de place n'a servi à ajuster les profils.

