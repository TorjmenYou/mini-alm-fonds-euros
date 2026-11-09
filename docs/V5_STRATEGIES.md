# V5 : capital et stratégies ALM, comparaison consolidée

Généré par `scripts/v5_rapport_strategies.py` depuis `resultats/v5_consolidation.json` (`scripts/v5_consolidation.py`). Unités fictives : 1 unité = 10 M€. Vue prudentielle simplifiée : 2 000 scénarios, base avec VA, incertitude par 1 000 rééchantillonnages des paires antithétiques. Risque neutre et probabilité réelle : 1 000 scénarios. Conventions centrales : `docs/V5_SYNTHESE_AVANT_OPTIMISATION.md`, section 1. Synthèse courte : `docs/V5_SYNTHESE_STRATEGIES.md`. **Profils fictifs. Analyse exploratoire, conditionnelle aux hypothèses : ce n'est pas une recommandation.**

**Aucun indicateur de ce document n'est un ratio réglementaire.** L'« indicateur de couverture simplifié » est un calcul pédagogique inspiré de la formule standard, sans mesure transitoire, sans modèle interne et sans les modules non modélisés (section 9).

**ACPR n° 185** : la page officielle (https://acpr.banque-france.fr/en/node/1925405) et le PDF n'ont pas pu être consultés. Aucun chiffre n'en est tiré ; les repères de place cités ailleurs viennent de l'ACPR n° 181 et, pour le 30/06/2026, de chiffres repris par la presse. Les profils ne sont pas ajustés pour reproduire la moyenne sectorielle.

**Lecture des écarts.** Un écart à la gestion passive est *statistiquement significatif* s'il dépasse son intervalle de confiance apparié à 95 % (mêmes scénarios pour toutes les stratégies). Il est *économiquement important* s'il dépasse aussi un seuil fixé avant la lecture des résultats (`data/v5/strategies/strategies.json`, rubrique `lecture`) : 2 % du SCR simplifié du profil pour la valeur nette et l'apport, 25 pb pour le rendement des fonds propres, 5 pb pour le taux servi, 25 pb pour le taux de rachat, 0,5 point pour une probabilité d'apport, 5 % du SCR pour les moins-values réalisées.

## 1. SCR et MCR simplifiés (gestion passive, bilan initial)

### 1.1 Des fonds propres comptables aux fonds propres de niveau 1

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fonds propres comptables et réserve de capitalisation | 50,0 | 65,0 | 65,0 |
| Moins-values latentes obligataires | −170,9 | −118,4 | −52,1 |
| Plus-values latentes actions | 4,3 | 11,1 | 7,8 |
| PM + PPB - BE (base avec VA) | 139,6 | 132,8 | 95,1 |
| - Marge de risque (6 %) | −21,8 | −37,8 | −31,9 |
| + Fonds excédentaires | 12,8 | 14,9 | 7,4 |
| - Impôts différés passifs | 0,0 | 0,0 | −4,9 |
| **Fonds propres de niveau 1** | 13,9 | 67,5 | 86,4 |
| Intervalle à 95 % des fonds propres de niveau 1 (erreur Monte-Carlo) | [10,3 ; 16,8] | [64,9 ; 69,6] | [84,6 ; 88,0] |

Identité vérifiée par le générateur : actif - BE - marge de risque + fonds excédentaires - impôts différés passifs = somme des lignes ci-dessus.

### 1.2 Le SCR simplifié et ce qui le détermine

| | A | B | C |
| --- | ---: | ---: | ---: |
| Taux (sens retenu) | 15,2 | 7,6 | 11,3 |
| Actions (39 %) | 29,8 | 33,0 | 32,2 |
| Spread (part non souveraine) | 47,0 | 42,6 | 42,9 |
| Marché après diversification | 73,7 | 71,2 | 71,3 |
| Rachat (sens retenu) | 44,5 | 39,2 | 29,9 |
| Mortalité + frais | 4,1 | 4,0 | 3,6 |
| Vie après diversification | 46,2 | 40,7 | 31,1 |
| BSCR net (après actions de gestion) | 96,3 | 90,4 | 84,6 |
| BSCR brut (FDB figées) | 176,5 | 214,1 | 247,6 |
| Ajustement pour absorption par les FDB | −61,1 | −123,7 | −162,9 |
| Risque opérationnel | 4,0 | 4,1 | 4,2 |
| Ajustement pour impôts différés | 0,0 | 0,0 | −4,9 |
| **SCR simplifié** | 119,4 | 94,5 | 83,9 |
| Intervalle à 95 % du SCR | [116,8 ; 122,0] | [93,3 ; 97,9] | [82,2 ; 85,5] |
| **Indicateur de couverture simplifié du SCR** | 12 % | 71 % | 103 % |
| Intervalle à 95 % de l'indicateur | [9 ; 14] % | [67 ; 73] % | [101 ; 105] % |
| Insuffisance (SCR - fonds propres de niveau 1) | 105,5 | 27,0 | −2,5 |

**Ce qui détermine les insuffisances :**

- **A** : fonds propres comptables de 4,5 % de la PM, moins-values obligataires latentes de 18,1 % de la VNC obligataire (−170,9), partiellement compensées par l'écart provisions - BE (139,6) ; marge de risque de 21,8. SCR dominé par le spread (47,0), les actions (29,8) et le rachat (44,5, rachat massif de 40 %). L'absorption par les FDB atteint son plafond (FDB - fonds excédentaires) : le SCR dépend directement du niveau des FDB.
- **B** : fonds propres comptables de 5,0 % de la PM, moins-values obligataires latentes de 12,6 % de la VNC obligataire (−118,4), partiellement compensées par l'écart provisions - BE (132,8) ; marge de risque de 37,8. SCR dominé par le spread (42,6), les actions (33,0) et le rachat (39,2, rachat massif de 40 %). L'absorption par les FDB n'atteint pas son plafond.
- **C** : fonds propres comptables de 6,0 % de la PM, moins-values obligataires latentes de 5,9 % de la VNC obligataire (−52,1), partiellement compensées par l'écart provisions - BE (95,1) ; marge de risque de 31,9. SCR dominé par le spread (42,9), les actions (32,2) et le rachat (29,9, rachat massif de 40 %). L'absorption par les FDB n'atteint pas son plafond.

### 1.3 Le MCR : formule linéaire, corridor et minimum absolu

MCR linéaire = max(0 ; 3,7 % x (BE - FDB) - 5,2 % x (FDB - fonds excédentaires)) ; MCR combiné = MCR linéaire encadré entre 25 % et 45 % du SCR ; MCR = max(MCR combiné ; 0,4 unité). Chaque terme est calculé, puis comparé au corridor et au minimum absolu (test `test_mcr_encadre`, qui couvre les quatre contraintes possibles).

| | A | B | C |
| --- | ---: | ---: | ---: |
| 3,7 % x (BE - FDB) | 30,0 | 27,1 | 25,9 |
| - 5,2 % x FDB hors fonds excédentaires | −3,2 | −8,3 | −11,4 |
| MCR linéaire | 26,8 | 18,8 | 14,5 |
| 25 % du SCR | 29,9 | 23,6 | 21,0 |
| 45 % du SCR | 53,7 | 42,5 | 37,8 |
| Minimum absolu | 0,4 | 0,4 | 0,4 |
| **MCR simplifié** | 29,9 | 23,6 | 21,0 |
| Contrainte active | plancher de 25 % du SCR | plancher de 25 % du SCR | plancher de 25 % du SCR |
| Indicateur de couverture simplifié du MCR [IC 95 %] | 47 % [35 ; 55] | 286 % [267 ; 292] | 412 % [403 ; 422] |

**Lecture.** Pour A, B, C, le MCR linéaire est inférieur à 25 % du SCR : le plancher s'applique, et l'indicateur MCR vaut alors quatre fois l'indicateur SCR. Le terme des FDB abaisse le MCR linéaire d'autant plus que la participation future est importante. Le minimum absolu ne joue pour aucun profil. Les indicateurs MCR élevés ne témoignent donc pas d'une marge de sécurité propre : ils reflètent le plancher du corridor.

### 1.4 Rapprochement avec les calculs précédents

| | A | B | C |
| --- | ---: | ---: | ---: |
| Indicateur SCR, synthèse avant optimisation (1 000 scénarios, sans distribution) | 9 % | 69 % | 97 % |
| Indicateur SCR, première comparaison des stratégies (500 scénarios) | 12 % | 72 % | 101 % |
| Indicateur SCR, ce document (2 000 scénarios) [IC 95 %] | 12 % [9 ; 14] | 71 % [67 ; 73] | 103 % [101 ; 105] |
| Effet de la politique de distribution sur le BE (mêmes scénarios) | −1,4 ± 0,3 | −0,6 ± 0,4 | 0,2 ± 0,5 |

Les écarts entre ces trois calculs viennent de l'erreur Monte-Carlo du niveau du BE (même générateur, jeux de scénarios de tailles différentes) et de la politique de distribution introduite avec les stratégies. Mécanisme de cette dernière : la participation est calculée sur la quote-part des produits financiers, au rendement comptable moyen de tout l'actif. Sans distribution, les résultats conservés sont réinvestis aux taux du marché, qui dépassent en moyenne les coupons anciens dans les scénarios risque neutre ; le rendement comptable moyen monte, et les assurés en reçoivent leur quote-part. La distribution supprime cet effet : taux servi un peu plus bas les années de hausse des taux, FDB et BE plus faibles (profil B, année 10 : rendement comptable −16 pb, taux servi −8 pb). Aucun paramètre n'a été ajusté pour se rapprocher d'un repère de place.

## 2. Capital nécessaire, par stratégie

L'apport est versé en trésorerie à l'ouverture et investi ensuite au prix du marché ; le portefeuille existant ne change pas. Pour chaque stratégie, les fonds propres de niveau 1 et le SCR sont calculés pour deux apports, puis interpolés linéairement. L'intervalle à 95 % vient du rééchantillonnage des paires de scénarios (mêmes rééchantillons pour les deux apports, pour tous les chocs et pour toutes les stratégies).

**Profil A**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 12 % [9 ; 14] | 101,0 [99,4 ; 102,8] | - | 149,7 [147,5 ; 151,9] | - |
| Réinvestissement progressif | 12 % [9 ; 14] | 101,7 [100,1 ; 103,7] | 0,7 [0,5 ; 0,9] | 151,4 [149,1 ; 153,6] | 1,7 [1,3 ; 2,1] |
| Repositionnement | −7 % [−11 ; −5] | 120,3 [118,9 ; 121,8] | 19,2 [17,6 ; 20,9] | 178,2 [176,3 ; 180,1] | 28,5 [25,0 ; 31,6] |
| Taux servi compétitif | 8 % [4 ; 10] | 89,6 [88,3 ; 91,2] | −11,4 [−12,7 ; −10,3] | 131,4 [130,2 ; 132,7] | −18,3 [−20,5 ; −16,2] |
| Taux servi de marge | 15 % [12 ; 17] | 107,1 [105,4 ; 109,3] | 6,1 [5,5 ; 6,8] | 161,5 [158,9 ; 164,2] | 11,8 [10,6 ; 13,0] |
| Liquidité défensive | 12 % [9 ; 13] | 114,5 [112,9 ; 116,2] | 13,5 [12,0 ; 14,9] | 171,6 [169,2 ; 174,0] | 21,9 [19,3 ; 24,3] |
| Compétitif préservant la PPB | 8 % [5 ; 11] | 99,6 [98,2 ; 101,3] | −1,4 [−2,0 ; −0,9] | 144,1 [142,2 ; 146,0] | −5,6 [−6,7 ; −4,7] |
| Rétention de capital | 12 % [9 ; 14] | 100,7 [99,1 ; 102,5] | −0,4 [−0,5 ; −0,2] | 148,1 [146,0 ; 150,2] | −1,6 [−1,9 ; −1,2] |

**Profil B**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 71 % [67 ; 73] | 27,6 [26,1 ; 32,5] | - | 75,4 [72,8 ; 80,8] | - |
| Réinvestissement progressif | 72 % [67 ; 73] | 27,4 [26,0 ; 32,3] | −0,1 [−0,5 ; 0,0] | 75,5 [72,9 ; 80,8] | 0,1 [−0,3 ; 0,5] |
| Repositionnement | 54 % [52 ; 55] | 47,7 [46,4 ; 49,1] | 20,1 [16,3 ; 21,0] | 100,8 [99,5 ; 102,2] | 25,4 [20,3 ; 27,9] |
| Taux servi compétitif | 70 % [65 ; 72] | 26,4 [25,1 ; 30,9] | −1,1 [−2,3 ; −0,3] | 70,1 [67,8 ; 74,5] | −5,4 [−8,4 ; −4,2] |
| Taux servi de marge | 74 % [69 ; 76] | 23,9 [22,4 ; 29,4] | −3,7 [−4,2 ; −1,6] | 69,1 [66,1 ; 75,3] | −6,4 [−8,8 ; 0,5] |
| Liquidité défensive | 71 % [67 ; 72] | 28,4 [27,3 ; 32,7] | 0,8 [−1,2 ; 1,5] | 77,6 [75,3 ; 82,2] | 2,2 [0,2 ; 4,4] |
| Compétitif préservant la PPB | 68 % [63 ; 70] | 27,3 [25,8 ; 31,6] | −0,3 [−2,0 ; 0,4] | 69,4 [67,1 ; 74,1] | −6,0 [−11,2 ; −4,5] |
| Rétention de capital | 71 % [67 ; 73] | 27,9 [26,5 ; 32,9] | 0,4 [0,3 ; 0,5] | 76,0 [73,2 ; 81,3] | 0,5 [0,3 ; 0,7] |

**Profil C**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 103 % [101 ; 105] | 0,0 [0,0 ; 0,0] | - | 42,4 [39,8 ; 45,0] | - |
| Réinvestissement progressif | 103 % [101 ; 105] | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 42,9 [40,4 ; 45,4] | 0,5 [0,1 ; 1,0] |
| Repositionnement | 98 % [96 ; 100] | 2,2 [0,3 ; 4,0] | 2,2 [0,3 ; 4,0] | 47,5 [45,0 ; 50,0] | 5,1 [4,1 ; 6,2] |
| Taux servi compétitif | 100 % [98 ; 102] | 0,0 [0,0 ; 1,3] | 0,0 [0,0 ; 1,3] | 43,8 [41,3 ; 46,1] | 1,4 [−0,1 ; 3,0] |
| Taux servi de marge | 111 % [108 ; 114] | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 33,4 [30,4 ; 36,1] | −9,0 [−10,3 ; −7,9] |
| Liquidité défensive | 102 % [101 ; 104] | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 42,9 [40,9 ; 44,8] | 0,4 [−1,1 ; 2,0] |
| Compétitif préservant la PPB | 99 % [97 ; 102] | 0,4 [0,0 ; 2,2] | 0,4 [0,0 ; 2,2] | 44,6 [42,0 ; 47,3] | 2,2 [1,0 ; 3,5] |
| Rétention de capital | 103 % [100 ; 105] | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 43,1 [40,6 ; 45,7] | 0,7 [0,5 ; 1,0] |

**Vérification de l'interpolation** (vue prudentielle recalculée à l'apport obtenu, mêmes scénarios). L'erreur d'apport est estimée au premier ordre : (indicateur obtenu - cible) x SCR obtenu / (pente des fonds propres - cible x pente du SCR) ; positive, l'apport interpolé est trop élevé.

| Profil, stratégie, cible | Apport interpolé | Indicateur obtenu | Erreur d'apport estimée |
| --- | ---: | ---: | ---: |
| A, Passive, 100 % | 101,0 | 102,3 % | 2,3 |
| A, Passive, 150 % | 149,7 | 149,2 % | −0,8 |
| B, Passive, 100 % | 27,6 | 99,9 % | −0,1 |
| B, Passive, 150 % | 75,4 | 150,5 % | 0,5 |
| C, Passive, 100 % | 0,0 | 103,0 % | sans objet (cible atteinte sans apport) |
| C, Passive, 150 % | 42,4 | 150,3 % | 0,2 |
| A, Taux servi de marge, 100 % | 107,1 | 101,7 % | 1,9 |
| B, Taux servi de marge, 100 % | 23,9 | 99,7 % | −0,2 |
| C, Taux servi de marge, 100 % | 0,0 | 110,5 % | sans objet (cible atteinte sans apport) |
| A, Réinvestissement progressif, 100 % | 101,7 | 102,5 % | 2,6 |
| A, Repositionnement, 100 % | 120,3 | 99,1 % | −1,0 |
| A, Taux servi compétitif, 100 % | 89,6 | 102,3 % | 2,0 |
| A, Liquidité défensive, 100 % | 114,5 | 101,7 % | 1,9 |
| A, Compétitif préservant la PPB, 100 % | 99,6 | 102,0 % | 1,8 |
| A, Rétention de capital, 100 % | 100,7 | 102,7 % | 2,7 |

Stratégies à 100 % sans apport : Passive (C), Réinvestissement progressif (C), Taux servi compétitif (C), Taux servi de marge (C), Liquidité défensive (C), Rétention de capital (C). Deux erreurs entourent les besoins d'apport. L'erreur Monte-Carlo (demi-largeur des intervalles ci-dessus) va de 0,0 à 4,6 unités. L'erreur d'interpolation atteint au plus 0,5 unité pour B et C ; elle est plus forte pour A (2,7 au plus, pour « Rétention de capital »), dont la relation entre apport et indicateur n'est pas linéaire (plafond de l'absorption par les FDB, section 8). Les apports utilisés ensuite sont les apports interpolés, non corrigés, pour garder une règle identique pour toutes les stratégies. Ces erreurs pèsent peu sur la valeur : le coût net de portage de la gestion passive est d'environ 0,10 par unité d'apport pour A (section 2.1), soit moins de 0,3 de valeur nette pour l'erreur d'interpolation la plus forte. Les **écarts** de besoin entre stratégies, calculés sur les mêmes rééchantillons, sont plus précis que les besoins eux-mêmes.

### 2.1 Fonds propres existants, apports, distributions et coûts de financement

Quatre flux sont tenus séparément : (1) les fonds propres existants, déjà dans l'actif d'ouverture ; (2) les apports, initial et ultérieurs (le modèle apporte la trésorerie manquante quand tous les actifs ont été vendus), qui sont des sorties pour l'actionnaire et jamais des produits ; (3) les distributions : les fonds propres comptables sont ramenés chaque année à leur niveau d'ouverture rapporté à la PM, apport compris, l'excédent étant versé l'année suivante (la variante « rétention » n'en verse que la moitié) ; (4) le coût de financement : impôt sur les revenus du capital immobilisé et participation sur ces revenus. Aucun coût d'émission n'est appliqué. Valeur nette = actif - BE - apport initial - VA de l'impôt = VA des dividendes + VA du résidu final - apport initial - VA des apports ultérieurs - VA de l'impôt (à l'écart Monte-Carlo près).

| Profil, base (gestion passive) | VA des dividendes | VA du résidu final | - Apport initial | - VA des apports ultérieurs | - VA de l'impôt | Écart Monte-Carlo | **Valeur nette** | Coût net de portage de l'apport |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A, bilan initial, sans apport | 33,5 | −2,5 | 0,0 | −21,6 | −5,8 | 0,9 | **4,5** | - |
| A, capital porté à 100 % du SCR simplifié | 112,7 | −1,3 | −101,0 | −4,9 | −11,9 | 1,2 | **−5,4** | 9,9 |
| A, capital porté à 150 % du SCR simplifié | 157,2 | −0,7 | −149,7 | −3,1 | −15,5 | 1,2 | **−10,6** | 15,1 |
| B, bilan initial, sans apport | 84,4 | −0,8 | 0,0 | −5,5 | −17,4 | 0,7 | **61,4** | - |
| B, capital porté à 100 % du SCR simplifié | 109,0 | −0,1 | −27,6 | −4,2 | −20,3 | 0,7 | **57,5** | 3,9 |
| B, capital porté à 150 % du SCR simplifié | 153,0 | 0,9 | −75,4 | −3,0 | −25,6 | 0,7 | **50,6** | 10,8 |
| C, bilan initial, sans apport | 110,5 | −0,6 | 0,0 | −5,3 | −23,1 | 1,3 | **82,8** | - |
| C, capital porté à 100 % du SCR simplifié | 110,5 | −0,6 | 0,0 | −5,3 | −23,1 | 1,3 | **82,8** | 0,0 |
| C, capital porté à 150 % du SCR simplifié | 149,7 | 0,4 | −42,4 | −3,9 | −28,3 | 1,5 | **77,0** | 5,8 |

Le coût net de portage est la valeur nette perdue en recapitalisant : impôt et participation sur les revenus du capital supplémentaire, diminués de la baisse des apports ultérieurs. Positif, il signifie que l'apport réduit la valeur risque neutre de l'actionnaire, même s'il est nécessaire pour respecter la contrainte.

## 3. Comparaison sur une base de capital commune

| Code | Stratégie | Règles |
| --- | --- | --- |
| `passive` | Gestion passive (règles des V1 à V4) | Allocation constante, réinvestissement à la maturité du profil, taux servi visé égal à la référence moins 0,5 point, renoncement à la marge si besoin. |
| `reinvestissement_progressif` | Réinvestissement progressif sur une échelle de maturités | Les achats d'obligations sont répartis à parts égales sur 3, 5, 7, 10 et 15 ans au lieu d'une seule maturité. |
| `repositionnement` | Repositionnement obligataire | Vente à l'ouverture de 25 % de la VNC obligataire, en commençant par les plus petits coupons, et rachat aux taux du marché ; la moins-value réalisée passe par la réserve de capitalisation puis par le résultat. |
| `taux_servi_competitif` | Politique de taux servi compétitive | Taux servi visé égal à la référence (au lieu de la référence moins 0,5 point) ; reprise de PPB jusqu'à 50 % du stock par an. |
| `taux_servi_marge` | Politique de taux servi de marge | Taux servi visé égal à la référence moins 1 point ; pas de renoncement à la marge de l'assureur. |
| `liquidite_defensive` | Gestion défensive de la liquidité | Monétaire porté à 12 % de l'actif (aux dépens des actions), réinvestissement obligataire à 5 ans. |
| `taux_servi_competitif_preservant` | Politique de taux servi compétitive préservant la PPB | Taux servi visé égal à la référence, reprise de PPB limitée à 25 % par an de la part du stock qui dépasse un plancher égal à la moitié du ratio PPB / PM d'ouverture ; les reprises obligatoires (dotations de plus de 8 ans) restent appliquées. |
| `distribution_retention` | Gestion passive avec rétention de capital | Règles de la gestion passive ; seule la moitié de l'excédent annuel de fonds propres comptables sur la cible est distribuée, l'autre moitié est conservée. |

**Base de capital commune** : pour une cible donnée (100 % ou 150 % du SCR simplifié), chaque stratégie reçoit l'apport qui porte *son propre* indicateur à la cible (section 2). La valeur nette déduit cet apport : une stratégie qui consomme plus de capital le paie. Mêmes bilans initiaux, mêmes scénarios économiques et mêmes tirages de défaut pour toutes les stratégies. Portefeuille fermé : aucune collecte nouvelle ; la collecte sensible au taux servi est traitée dans `docs/V5_COLLECTE.md`.

### 3.1 Capital porté à 100 % du SCR simplifié

**Profil A**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 101,0 | −5,4 | - | - | 4,4 % | 109,2 | 1,0 % | 2,30 % | −66 pb | 10,5 % / 5,1 % | 34 % | 74,8 |
| Réinvestissement progressif | 101,7 | −5,0 | 0,4 ± 0,2 | significatif, non important | 4,4 % | 109,2 | 0,7 % | 2,30 % | −66 pb | 10,4 % / 5,1 % | 34 % | 64,4 |
| Repositionnement | 120,3 | −21,9 | −16,5 ± 1,1 | important | 1,9 % | 79,3 | 0,1 % | 2,41 % | −55 pb | 8,8 % / 5,5 % | 31 % | 56,5 |
| Taux servi compétitif | 89,6 | −11,4 | −6,0 ± 0,4 | important | 4,3 % | 102,9 | 1,6 % | 2,43 % | −53 pb | 11,0 % / 5,7 % | 34 % | 94,7 |
| Taux servi de marge | 107,1 | 0,4 | 5,8 ± 0,4 | important | 4,5 % | 120,2 | 0,7 % | 2,03 % | −94 pb | 10,2 % / 5,6 % | 34 % | 101,5 |
| Liquidité défensive | 114,5 | −4,6 | 0,8 ± 1,2 | non significatif | 3,7 % | 107,7 | 0,5 % | 2,27 % | −69 pb | 10,8 % / 5,1 % | 31 % | 71,6 |
| Compétitif préservant la PPB | 99,6 | −9,5 | −4,1 ± 0,4 | important | 4,2 % | 104,6 | 1,2 % | 2,49 % | −48 pb | 10,8 % / 5,2 % | 34 % | 82,2 |
| Rétention de capital | 100,7 | −6,5 | −1,1 ± 0,1 | significatif, non important | 4,3 % | 99,2 | 0,3 % | 2,31 % | −65 pb | 10,3 % / 5,0 % | 34 % | 71,3 |

**Profil B**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 27,6 | 57,5 | - | - | 8,5 % | 87,0 | 0,3 % | 2,66 % | −31 pb | 7,0 % / 4,3 % | 14 % | 4,9 |
| Réinvestissement progressif | 27,4 | 57,8 | 0,3 ± 0,3 | significatif, non important | 8,5 % | 86,6 | 0,3 % | 2,65 % | −32 pb | 7,0 % / 4,3 % | 14 % | 4,8 |
| Repositionnement | 47,7 | 45,8 | −11,7 ± 0,7 | important | 6,7 % | 88,7 | 0,3 % | 2,84 % | −13 pb | 6,4 % / 4,6 % | 16 % | 16,9 |
| Taux servi compétitif | 26,4 | 47,4 | −10,1 ± 0,5 | important | 8,2 % | 84,2 | 0,4 % | 2,89 % | −7 pb | 7,8 % / 4,5 % | 20 % | 7,2 |
| Taux servi de marge | 23,9 | 63,8 | 6,3 ± 0,6 | important | 8,9 % | 86,4 | 0,4 % | 2,57 % | −39 pb | 6,8 % / 4,7 % | 12 % | 11,2 |
| Liquidité défensive | 28,4 | 58,7 | 1,2 ± 1,4 | non significatif | 8,2 % | 86,0 | 0,4 % | 2,57 % | −39 pb | 7,0 % / 4,3 % | 11 % | 4,0 |
| Compétitif préservant la PPB | 27,3 | 48,0 | −9,5 ± 0,5 | important | 8,1 % | 83,1 | 0,4 % | 2,90 % | −6 pb | 7,5 % / 4,4 % | 16 % | 7,1 |
| Rétention de capital | 27,9 | 56,1 | −1,4 ± 0,1 | significatif, non important | 7,9 % | 79,4 | 0,3 % | 2,66 % | −30 pb | 7,0 % / 4,3 % | 13 % | 4,4 |

**Profil C**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 0,0 | 82,8 | - | - | 11,9 % | 88,3 | 0,6 % | 2,97 % | 0 pb | 6,5 % / 4,2 % | 12 % | 19,9 |
| Réinvestissement progressif | 0,0 | 82,8 | 0,0 ± 0,5 | non significatif | 11,9 % | 88,2 | 0,6 % | 2,96 % | 0 pb | 6,5 % / 4,2 % | 12 % | 18,8 |
| Repositionnement | 2,2 | 81,4 | −1,4 ± 0,5 | significatif, non important | 11,5 % | 88,1 | 0,8 % | 3,01 % | 4 pb | 6,5 % / 4,2 % | 15 % | 23,5 |
| Taux servi compétitif | 0,0 | 73,0 | −9,8 ± 0,7 | important | 11,6 % | 87,0 | 1,2 % | 3,09 % | 13 pb | 7,2 % / 4,3 % | 18 % | 24,9 |
| Taux servi de marge | 0,0 | 85,9 | 3,1 ± 0,7 | important | 11,9 % | 88,4 | 0,6 % | 2,95 % | −2 pb | 6,5 % / 4,5 % | 13 % | 39,2 |
| Liquidité défensive | 0,0 | 85,9 | 3,1 ± 1,5 | important | 11,7 % | 87,7 | 0,4 % | 2,90 % | −7 pb | 6,3 % / 4,3 % | 7 % | 14,1 |
| Compétitif préservant la PPB | 0,4 | 73,0 | −9,8 ± 0,7 | important | 11,5 % | 86,8 | 1,1 % | 3,09 % | 13 pb | 7,2 % / 4,3 % | 22 % | 25,9 |
| Rétention de capital | 0,0 | 81,5 | −1,3 ± 0,1 | significatif, non important | 10,7 % | 81,3 | 0,5 % | 2,97 % | 0 pb | 6,5 % / 4,2 % | 11 % | 18,1 |

### 3.2 Capital porté à 150 % du SCR simplifié

**Profil A**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 149,7 | −10,6 | - | - | 4,0 % | 135,1 | 0,3 % | 2,35 % | −62 pb | 10,1 % / 4,9 % | 34 % | 67,5 |
| Réinvestissement progressif | 151,4 | −10,2 | 0,4 ± 0,2 | significatif, non important | 4,0 % | 135,3 | 0,4 % | 2,35 % | −61 pb | 9,9 % / 4,8 % | 32 % | 43,5 |
| Repositionnement | 178,2 | −27,9 | −17,3 ± 1,1 | important | 2,4 % | 115,9 | 0,1 % | 2,45 % | −52 pb | 8,6 % / 5,4 % | 31 % | 56,0 |
| Taux servi compétitif | 131,4 | −16,0 | −5,4 ± 0,4 | important | 4,0 % | 125,3 | 0,5 % | 2,50 % | −46 pb | 10,7 % / 5,4 % | 34 % | 86,6 |
| Taux servi de marge | 161,5 | −5,2 | 5,4 ± 0,4 | important | 4,0 % | 151,8 | 0,3 % | 2,08 % | −88 pb | 9,8 % / 5,5 % | 34 % | 72,4 |
| Liquidité défensive | 171,6 | −11,2 | −0,6 ± 1,3 | non significatif | 3,5 % | 137,4 | 0,3 % | 2,34 % | −62 pb | 10,2 % / 4,8 % | 24 % | 49,9 |
| Compétitif préservant la PPB | 144,1 | −14,7 | −4,0 ± 0,4 | important | 3,9 % | 127,8 | 0,3 % | 2,55 % | −42 pb | 10,4 % / 5,0 % | 34 % | 75,7 |
| Rétention de capital | 148,1 | −12,1 | −1,4 ± 0,1 | significatif, non important | 3,9 % | 122,2 | 0,2 % | 2,36 % | −61 pb | 9,9 % / 4,8 % | 33 % | 55,6 |

**Profil B**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 75,4 | 50,6 | - | - | 6,4 % | 112,3 | 0,2 % | 2,68 % | −28 pb | 6,8 % / 4,3 % | 13 % | 4,8 |
| Réinvestissement progressif | 75,5 | 51,0 | 0,4 ± 0,3 | significatif, non important | 6,4 % | 112,1 | 0,2 % | 2,67 % | −29 pb | 6,8 % / 4,3 % | 12 % | 4,8 |
| Repositionnement | 100,8 | 38,3 | −12,3 ± 0,7 | important | 5,5 % | 119,5 | 0,2 % | 2,86 % | −10 pb | 6,3 % / 4,6 % | 16 % | 16,6 |
| Taux servi compétitif | 70,1 | 41,1 | −9,5 ± 0,5 | important | 6,3 % | 107,1 | 0,3 % | 2,92 % | −5 pb | 7,6 % / 4,4 % | 18 % | 6,1 |
| Taux servi de marge | 69,1 | 56,9 | 6,3 ± 0,5 | important | 6,6 % | 111,2 | 0,2 % | 2,61 % | −35 pb | 6,6 % / 4,7 % | 11 % | 12,1 |
| Liquidité défensive | 77,6 | 51,5 | 0,9 ± 1,4 | non significatif | 6,1 % | 112,2 | 0,3 % | 2,58 % | −38 pb | 6,7 % / 4,3 % | 8 % | 2,3 |
| Compétitif préservant la PPB | 69,4 | 41,7 | −8,9 ± 0,5 | important | 6,3 % | 105,1 | 0,3 % | 2,92 % | −4 pb | 7,3 % / 4,4 % | 16 % | 5,5 |
| Rétention de capital | 76,0 | 48,7 | −1,9 ± 0,1 | significatif, non important | 6,1 % | 102,8 | 0,1 % | 2,69 % | −28 pb | 6,7 % / 4,3 % | 12 % | 3,9 |

**Profil C**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 42,4 | 77,0 | - | - | 8,3 % | 111,6 | 0,5 % | 2,98 % | 1 pb | 6,4 % / 4,2 % | 11 % | 18,8 |
| Réinvestissement progressif | 42,9 | 76,9 | −0,1 ± 0,6 | non significatif | 8,3 % | 111,9 | 0,4 % | 2,97 % | 0 pb | 6,4 % / 4,2 % | 10 % | 16,4 |
| Repositionnement | 47,5 | 74,9 | −2,2 ± 0,5 | important | 8,0 % | 113,1 | 0,6 % | 3,02 % | 6 pb | 6,4 % / 4,2 % | 15 % | 24,2 |
| Taux servi compétitif | 43,8 | 67,3 | −9,7 ± 0,7 | important | 8,1 % | 111,3 | 0,8 % | 3,10 % | 14 pb | 7,1 % / 4,3 % | 16 % | 21,2 |
| Taux servi de marge | 33,4 | 81,2 | 4,2 ± 0,7 | important | 8,8 % | 107,2 | 0,5 % | 2,96 % | −1 pb | 6,4 % / 4,5 % | 12 % | 39,5 |
| Liquidité défensive | 42,9 | 79,7 | 2,7 ± 1,6 | important | 8,2 % | 111,5 | 0,3 % | 2,90 % | −6 pb | 6,2 % / 4,3 % | 5 % | 12,6 |
| Compétitif préservant la PPB | 44,6 | 67,2 | −9,8 ± 0,6 | important | 8,0 % | 111,4 | 0,7 % | 3,10 % | 14 pb | 7,1 % / 4,3 % | 18 % | 21,4 |
| Rétention de capital | 43,1 | 75,2 | −1,8 ± 0,1 | important | 7,8 % | 103,4 | 0,5 % | 2,98 % | 1 pb | 6,3 % / 4,2 % | 11 % | 16,9 |

Rendement des fonds propres : résultat net d'impôt rapporté aux fonds propres comptables d'ouverture de chaque année, agrégé sur les scénarios, à comparer à un rendement exigé fictif de 8 %. Les indicateurs réels n'ont pas d'intervalle apparié ; leurs écarts entre stratégies portent sur les mêmes scénarios.

## 4. Réinvestissement progressif : significativité et importance

Écart de valeur nette à la gestion passive ± intervalle apparié à 95 % :

| Profil | Bilan initial | Base 100 % | Base 150 % |
| --- | ---: | ---: | ---: |
| A | 0,13 ± 0,11 | 0,39 ± 0,16 | 0,44 ± 0,21 |
| B | 0,15 ± 0,25 | 0,26 ± 0,26 | 0,39 ± 0,28 |
| C | 0,04 ± 0,55 | 0,04 ± 0,55 | −0,08 ± 0,55 |

Contrôle sur des tirages indépendants (profil A, base 100 %, 2 000 scénarios, autres graines pour les scénarios et les défauts) : 0,41 ± 0,12.

- **Statistiquement**, l'écart du profil A sur la base 100 % (0,39 ± 0,16) est significatif et se retrouve sur des tirages indépendants.
- **Économiquement**, il est faible : 0,04 % du BE et 0,3 % du SCR simplifié, pour un seuil d'importance de 2,4 (2 % du SCR). Il est aussi petit devant l'incertitude du besoin d'apport du profil (intervalle de largeur 3,4) et devant les écarts des politiques de taux servi.
- **Mécanisme** : l'écart n'apparaît que lorsque des achats obligataires importants passent par l'échelle de maturités, comme le réinvestissement de l'apport de A ; sur le bilan initial, les flux réinvestis sont faibles devant le stock obligataire.
- **Conclusion** : le réinvestissement progressif est statistiquement distinguable de la gestion passive pour A recapitalisé, mais pas économiquement distinguable avec les seuils retenus.

## 5. Deux variantes : politique compétitive préservant la PPB, rétention de capital

Politique compétitive préservant la PPB : même cible que la politique compétitive (la référence), mais reprises volontaires limitées à 25 % par an de la part de la PPB qui dépasse la moitié du ratio PPB / PM d'ouverture. Rétention : règles de la gestion passive, la moitié seulement de l'excédent annuel de fonds propres est distribuée. Base 100 %, écarts à la gestion passive :

| Profil | Stratégie | Valeur nette ± IC | Lecture | Apport à 100 % | Écart du taux servi à la référence (réel) | Rachat 1-10 RN | Probabilité d'apport sur 60 ans (réel) | Rendement des fonds propres (réel) |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| A | Taux servi compétitif | −6,0 ± 0,4 | important | −11,4 | 13 pb | 58 pb | 0,6 pt | −0,11 pt |
| A | Compétitif préservant la PPB | −4,1 ± 0,4 | important | −1,4 | 19 pb | 32 pb | 0,2 pt | −0,20 pt |
| A | Rétention de capital | −1,1 ± 0,1 | significatif, non important | −0,4 | 1 pb | −13 pb | −0,7 pt | −0,12 pt |
| B | Taux servi compétitif | −10,1 ± 0,5 | important | −1,1 | 24 pb | 81 pb | 0,1 pt | −0,27 pt |
| B | Compétitif préservant la PPB | −9,5 ± 0,5 | important | −0,3 | 24 pb | 49 pb | 0,1 pt | −0,44 pt |
| B | Rétention de capital | −1,4 ± 0,1 | significatif, non important | 0,4 | 0 pb | −5 pb | 0,0 pt | −0,64 pt |
| C | Taux servi compétitif | −9,8 ± 0,7 | important | 0,0 | 13 pb | 69 pb | 0,6 pt | −0,32 pt |
| C | Compétitif préservant la PPB | −9,8 ± 0,7 | important | 0,4 | 13 pb | 68 pb | 0,5 pt | −0,44 pt |
| C | Rétention de capital | −1,3 ± 0,1 | significatif, non important | 0,0 | 0 pb | −4 pb | −0,1 pt | −1,18 pt |

Trajectoires risque neutre (bilan initial), gestion passive / compétitive / compétitive préservant la PPB :

| Profil | Année | PPB / PM | Part des scénarios hors zone neutre | Taux de rachat |
| --- | ---: | ---: | ---: | ---: |
| A | 1 | 1,86 % / 1,30 % / 2,08 % | 18 % / 15 % / 20 % | 4,3 % / 4,3 % / 4,3 % |
| A | 5 | 0,94 % / 0,15 % / 1,48 % | 79 % / 86 % / 80 % | 12,0 % / 12,5 % / 12,9 % |
| A | 8 | 0,14 % / 0,02 % / 0,11 % | 70 % / 79 % / 69 % | 15,8 % / 16,9 % / 15,8 % |
| A | 10 | 0,12 % / 0,02 % / 0,12 % | 75 % / 79 % / 77 % | 16,8 % / 17,5 % / 17,1 % |
| A | 20 | 0,74 % / 0,14 % / 0,27 % | 53 % / 57 % / 55 % | 15,2 % / 15,9 % / 15,5 % |
| B | 1 | 3,57 % / 2,98 % / 3,44 % | 6 % / 2 % / 13 % | 4,3 % / 4,3 % / 4,3 % |
| B | 5 | 1,91 % / 0,51 % / 2,20 % | 34 % / 44 % / 38 % | 6,9 % / 7,3 % / 7,7 % |
| B | 8 | 1,02 % / 0,14 % / 0,61 % | 35 % / 51 % / 36 % | 9,2 % / 11,5 % / 9,4 % |
| B | 10 | 1,01 % / 0,15 % / 0,64 % | 38 % / 49 % / 45 % | 9,7 % / 11,4 % / 10,7 % |
| B | 20 | 3,11 % / 0,89 % / 1,67 % | 18 % / 25 % / 24 % | 7,5 % / 8,7 % / 8,5 % |
| C | 1 | 2,20 % / 1,69 % / 1,88 % | 6 % / 5 % / 7 % | 4,3 % / 4,3 % / 4,3 % |
| C | 5 | 2,48 % / 0,76 % / 1,58 % | 21 % / 26 % / 27 % | 5,9 % / 6,2 % / 6,5 % |
| C | 8 | 2,50 % / 0,64 % / 1,25 % | 26 % / 37 % / 33 % | 8,2 % / 9,8 % / 9,4 % |
| C | 10 | 2,46 % / 0,73 % / 1,30 % | 25 % / 35 % / 34 % | 8,3 % / 10,2 % / 9,8 % |
| C | 20 | 3,66 % / 1,43 % / 2,11 % | 18 % / 28 % / 28 % | 7,6 % / 9,1 % / 8,8 % |

**Lecture.**

- **Préserver la PPB, par rapport à la politique compétitive de base** (A : 1,9 de valeur, 5 pb de taux servi, −26 pb de rachat ; B : 0,6 de valeur, 1 pb de taux servi, −32 pb de rachat ; C : 0,0 de valeur, 0 pb de taux servi, −1 pb de rachat ; mêmes scénarios, sans intervalle calculé pour cet écart) : garder une partie de la PPB pour les années où la référence monte réduit nettement les rachats (A, B) ; le gain d'écart à la référence n'est important que pour A, sans gain de valeur important. Le coût en valeur par rapport à la gestion passive demeure : la politique reste compétitive, donc moins de participation non servie revient à l'actionnaire.
- **Rétention** : la valeur baisse un peu (impôt et participation sur les revenus du capital conservé, rendement comptable relevé et partagé avec les assurés, section 1.4) ; l'écart ne dépasse le seuil d'importance que pour C à 150 %, au niveau du seuil. Le rendement des fonds propres baisse davantage, car le capital conservé dilue le résultat. Le bénéfice attendu de la rétention, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR. La rétention ne réduit pas l'apport initial nécessaire ; elle réduit un peu la probabilité d'apport ultérieur.

## 6. Matrice de décision exploratoire

Écarts à la gestion passive sur la base de capital commune, A / B / C. En gras : écart important (au-delà du seuil de lecture) ; « ns » : écart non significatif (intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle et de rachat n'ont pas d'intervalle). « Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital et sous les trois sensibilités de la section 7.

**Capital porté à 100 % du SCR simplifié**

| Stratégie | Valeur actionnaire (RN) | Rentabilité (réel) | Compétitivité : taux servi (réel) | Rachats (RN) | Liquidité : moins-values réalisées q99 (réel) | Capital : apport nécessaire | Capital : probabilité d'apport ultérieur sur 60 ans (réel) | Écart de valeur robuste (profils) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,4 / 0,3 / 0,0 ns | −0,02 pt / −0,03 pt / −0,02 pt | 0 pb / −1 pb / −1 pb | −10 pb / −2 pb / −1 pb | **−10,4** / −0,2 / −1,1 | 0,7 / −0,1 ns / 0,0 ns | −0,3 pt / 0,0 pt / 0,0 pt | aucun profil |
| Repositionnement | **−16,5** / **−11,7** / −1,4 | **−2,50 pt** / **−1,81 pt** / **−0,43 pt** | **11 pb** / **18 pb** / 4 pb | **−167 pb** / **−66 pb** / 0 pb | **−18,3** / **11,9** / 3,6 | **19,2** / **20,1** / **2,2** | **−0,9 pt** / 0,0 pt / 0,2 pt | A, B |
| Taux servi compétitif | **−6,0** / **−10,1** / **−9,8** | −0,11 pt / **−0,27 pt** / **−0,32 pt** | **13 pb** / **24 pb** / **13 pb** | **58 pb** / **81 pb** / **69 pb** | **19,9** / 2,2 / **5,0** | **−11,4** / −1,1 / 0,0 ns | **0,6 pt** / 0,1 pt / **0,6 pt** | A, B, C |
| Taux servi de marge | **5,8** / **6,3** / **3,1** | 0,05 pt / **0,35 pt** / 0,03 pt | **−27 pb** / **−8 pb** / −2 pb | −23 pb / −19 pb / −5 pb | **26,7** / **6,2** / **19,3** | **6,1** / **−3,7** / 0,0 ns | −0,3 pt / 0,1 pt / 0,0 pt | A, B, C |
| Liquidité défensive | 0,8 ns / 1,2 ns / **3,1** | **−0,70 pt** / **−0,31 pt** / −0,20 pt | −3 pb / **−9 pb** / **−7 pb** | **36 pb** / −3 pb / −19 pb | −3,2 / −1,0 / **−5,8** | **13,5** / 0,8 ns / 0,0 ns | **−0,5 pt** / 0,1 pt / −0,2 pt | C |
| Compétitif préservant la PPB | **−4,1** / **−9,5** / **−9,8** | −0,20 pt / **−0,44 pt** / **−0,44 pt** | **19 pb** / **24 pb** / **13 pb** | **32 pb** / **49 pb** / **68 pb** | **7,4** / 2,1 / **6,0** | −1,4 / −0,3 ns / 0,4 ns | 0,2 pt / 0,1 pt / 0,5 pt | A, B, C |
| Rétention de capital | −1,1 / −1,4 / −1,3 | −0,12 pt / **−0,64 pt** / **−1,18 pt** | 1 pb / 0 pb / 0 pb | −13 pb / −5 pb / −4 pb | −3,5 / −0,6 / −1,9 | −0,4 / 0,4 / 0,0 ns | **−0,7 pt** / 0,0 pt / −0,1 pt | aucun profil |

**Capital porté à 150 % du SCR simplifié**

| Stratégie | Valeur actionnaire (RN) | Rentabilité (réel) | Compétitivité : taux servi (réel) | Rachats (RN) | Liquidité : moins-values réalisées q99 (réel) | Capital : apport nécessaire | Capital : probabilité d'apport ultérieur sur 60 ans (réel) | Écart de valeur robuste (profils) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,4 / 0,4 / −0,1 ns | −0,02 pt / −0,03 pt / −0,04 pt | 1 pb / −1 pb / −1 pb | −17 pb / −3 pb / −3 pb | **−24,0** / −0,1 / −2,4 | 1,7 / 0,1 ns / 0,5 | 0,1 pt / 0,0 pt / −0,1 pt | aucun profil |
| Repositionnement | **−17,3** / **−12,3** / **−2,2** | **−1,67 pt** / **−0,89 pt** / **−0,30 pt** | **10 pb** / **18 pb** / 5 pb | **−150 pb** / **−50 pb** / 3 pb | **−11,5** / **11,8** / **5,4** | **28,5** / **25,4** / **5,1** | −0,2 pt / 0,0 pt / 0,1 pt | A, B |
| Taux servi compétitif | **−5,4** / **−9,5** / **−9,7** | −0,05 pt / −0,06 pt / −0,24 pt | **15 pb** / **23 pb** / **12 pb** | **67 pb** / **82 pb** / **67 pb** | **19,1** / 1,3 / 2,4 | **−18,3** / **−5,4** / 1,4 ns | 0,2 pt / 0,1 pt / 0,3 pt | A, B, C |
| Taux servi de marge | **5,4** / **6,3** / **4,2** | 0,00 pt / 0,21 pt / **0,50 pt** | **−27 pb** / **−7 pb** / −2 pb | **−28 pb** / −14 pb / −2 pb | 4,9 / **7,3** / **20,8** | **11,8** / −6,4 ns / **−9,0** | 0,0 pt / 0,0 pt / 0,0 pt | A, B, C |
| Liquidité défensive | −0,6 ns / 0,9 ns / **2,7** | **−0,54 pt** / −0,24 pt / −0,16 pt | −1 pb / **−10 pb** / **−7 pb** | 10 pb / −8 pb / −23 pb | **−17,6** / −2,5 / **−6,2** | **21,9** / **2,2** / 0,4 ns | 0,0 pt / 0,1 pt / −0,2 pt | C |
| Compétitif préservant la PPB | **−4,0** / **−8,9** / **−9,8** | −0,12 pt / −0,11 pt / **−0,31 pt** | **20 pb** / **24 pb** / **13 pb** | **34 pb** / **52 pb** / **67 pb** | **8,3** / 0,7 / 2,6 | **−5,6** / **−6,0** / **2,2** | 0,0 pt / 0,1 pt / 0,2 pt | A, B, C |
| Rétention de capital | −1,4 / −1,9 / **−1,8** | −0,08 pt / **−0,33 pt** / **−0,58 pt** | 1 pb / 0 pb / 0 pb | −17 pb / −6 pb / −6 pb | **−11,9** / −1,0 / −1,9 | −1,6 / 0,5 / 0,7 | −0,1 pt / −0,1 pt / 0,0 pt | aucun profil |

Sens de lecture : une valeur, une rentabilité ou un écart de taux servi positifs sont favorables ; des rachats, des moins-values réalisées, un apport ou une probabilité d'apport positifs sont défavorables.

## 7. Sensibilité de la valeur aux hypothèses fragiles (base 100 %)

Écart de valeur nette à la gestion passive ± intervalle apparié, avec les apports du centre. Les besoins d'apport ne sont pas recalculés sous chaque sensibilité.

**Profil A**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,4 ± 0,2 | 0,0 ± 0,0 | 0,4 ± 0,1 | 0,4 ± 0,2 |
| Repositionnement | −16,5 ± 1,1 | −7,0 ± 0,7 | −13,9 ± 1,0 | −16,6 ± 1,3 |
| Taux servi compétitif | −6,0 ± 0,4 | −3,0 ± 0,3 | −4,9 ± 0,4 | −6,2 ± 0,5 |
| Taux servi de marge | 5,8 ± 0,4 | 3,3 ± 0,6 | 4,1 ± 0,6 | 6,3 ± 0,4 |
| Liquidité défensive | 0,8 ± 1,2 | 3,5 ± 0,6 | 2,5 ± 1,0 | 0,3 ± 1,3 |
| Compétitif préservant la PPB | −4,1 ± 0,4 | −1,1 ± 0,3 | −3,1 ± 0,4 | −4,4 ± 0,6 |
| Rétention de capital | −1,1 ± 0,1 | −0,7 ± 0,1 | −0,9 ± 0,1 | −1,3 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Liquidité défensive ; Transmission immédiate des taux : Taux servi de marge ; Défaut corrélé par bloc souverain : Taux servi de marge. **Le premier rang change avec les hypothèses.**

**Profil B**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,3 ± 0,3 | 0,1 ± 0,2 | 0,6 ± 0,2 | 0,3 ± 0,3 |
| Repositionnement | −11,7 ± 0,7 | −7,3 ± 0,6 | −11,1 ± 0,8 | −12,8 ± 0,8 |
| Taux servi compétitif | −10,1 ± 0,5 | −3,1 ± 0,7 | −4,8 ± 0,4 | −10,1 ± 0,6 |
| Taux servi de marge | 6,3 ± 0,6 | 1,7 ± 0,5 | 3,3 ± 0,4 | 5,8 ± 0,6 |
| Liquidité défensive | 1,2 ± 1,4 | 3,0 ± 1,0 | 4,0 ± 1,2 | 1,3 ± 1,4 |
| Compétitif préservant la PPB | −9,5 ± 0,5 | −3,1 ± 0,7 | −5,1 ± 0,4 | −9,6 ± 0,6 |
| Rétention de capital | −1,4 ± 0,1 | −0,9 ± 0,0 | −1,2 ± 0,1 | −1,6 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Liquidité défensive ; Transmission immédiate des taux : Liquidité défensive ; Défaut corrélé par bloc souverain : Taux servi de marge. **Le premier rang change avec les hypothèses.**

**Profil C**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,0 ± 0,5 | 0,1 ± 0,4 | 0,6 ± 0,5 | 0,2 ± 0,6 |
| Repositionnement | −1,4 ± 0,5 | −0,8 ± 0,4 | −1,7 ± 0,4 | −1,8 ± 0,7 |
| Taux servi compétitif | −9,8 ± 0,7 | −2,7 ± 0,7 | −4,6 ± 0,5 | −9,5 ± 0,7 |
| Taux servi de marge | 3,1 ± 0,7 | 0,9 ± 0,5 | 2,3 ± 0,4 | 2,3 ± 0,6 |
| Liquidité défensive | 3,1 ± 1,5 | 3,6 ± 1,1 | 4,7 ± 1,4 | 3,4 ± 1,5 |
| Compétitif préservant la PPB | −9,8 ± 0,7 | −2,8 ± 0,7 | −4,7 ± 0,5 | −9,7 ± 0,6 |
| Rétention de capital | −1,3 ± 0,1 | −1,0 ± 0,0 | −1,2 ± 0,1 | −1,5 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Liquidité défensive ; Transmission immédiate des taux : Liquidité défensive ; Défaut corrélé par bloc souverain : Liquidité défensive. **Le premier rang change avec les hypothèses.**

## 8. Mécanismes

- **Politique de marge** : transfert de la participation non servie vers l'actionnaire, dont le seul coût en portefeuille fermé est le surcroît de rachats dynamiques, borné par la zone neutre et le plafond de la loi de rachat. L'avantage fermé n'est pas, par principe, un majorant : avec une collecte sensible au taux servi, il l'est seulement si la valeur des affaires nouvelles de la politique de marge est inférieure à celle de la gestion passive (`docs/V5_COLLECTE.md`, section 3).
- **Politique compétitive** : la PPB est consommée tôt ; quand la référence monte, l'écart sort plus souvent de la zone neutre et les rachats remontent (profil B, année 8 : PPB de 0,14 % de la PM contre 1,02 %, 51 % des scénarios hors zone neutre contre 35 %). La variante préservant la PPB garde un stock plus élevé les premières années (année 5 : 2,20 % contre 0,51 %) ; le plancher ne limite que les reprises volontaires, et la reprise obligatoire des dotations de plus de 8 ans fait ensuite fortement baisser le stock (0,61 % à l'année 8), ce qui borne l'effet de la variante (section 5).
- **Repositionnement** : vente au prix de marché, mais la moins-value réalisée passe par la réserve de capitalisation puis par le résultat, tandis que les coupons plus élevés rachetés ensuite reviennent pour au moins 85 % de leur quote-part aux assurés : l'actionnaire supporte la perte et partage le gain.
- **Liquidité défensive** : en risque neutre, moins de volatilité réduit le coût des options (garantie et asymétrie de la participation) ; en probabilité réelle, la prime actions fictive est perdue.
- **Rétention de capital** : plus de fonds propres conservés, donc moins d'apports ultérieurs, mais davantage d'impôt sur leurs revenus et un rendement comptable plus élevé partagé avec les assurés (section 1.4).
- **Plafond de l'absorption par les FDB** (profil A) : quand l'absorption atteint son plafond (FDB - fonds excédentaires), le SCR vaut le BSCR brut moins ce plafond, plus le risque opérationnel ; toute baisse des FDB l'augmente à l'unité. La politique compétitive abaisse le BSCR brut de A (160,1 contre 176,5) et demande moins de capital ; la politique de marge abaisse les FDB (68,9 contre 73,9) et en demande davantage. 

## 9. Limites

- **Indicateurs simplifiés** : pas de mesure transitoire, ajustement symétrique nul, modules non modélisés (contrepartie, concentration, immobilier, change), marge de risque probablement surestimée, fonds excédentaires par l'approche simplifiée, impôts différés actifs non reconnus.
- **Portefeuille fermé** : aucune collecte nouvelle dans ce document. La collecte sensible au taux servi relatif est traitée dans `docs/V5_COLLECTE.md` (spécification : `docs/V5_SPECIFICATION_COLLECTE.md`).
- **Comportement des assurés** : loi de rachat dynamique des V1 à V4 au centre, corridors ONC de 2013 en sensibilité ; aucune donnée 2026 ne calibre la réaction des assurés.
- **Stratégies non optimisées** : un jeu de paramètres par famille et deux variantes ; une seule politique de distribution de base.
- **Interpolation des besoins d'apport** entre deux points, vérifiée par recalcul pour passive (A, B, C), réinvestissement progressif (A), repositionnement (A), taux servi compétitif (A), taux servi de marge (A, B, C), liquidité défensive (A), compétitif préservant la PPB (A), rétention de capital (A) ; apports interpolés non corrigés ; les sensibilités de la section 7 gardent les apports du centre.
- **Probabilité réelle** : taux sans prime de terme, spreads figés, prime actions fictive de 3 %, défauts aux taux historiques ; probabilités de recapitalisation conditionnelles à ces hypothèses ; écarts réels sans intervalle apparié.
- **Coûts de financement** : impôt et participation sur les revenus du capital ; ni coût d'émission, ni dette subordonnée, ni prime de rendement exigée intégrée à la valeur risque neutre.
- **ACPR n° 185** non lu.

