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
| Moins-values latentes obligataires | −185,5 | −128,4 | −71,4 |
| Plus-values latentes actions | 4,3 | 11,1 | 7,8 |
| PM + PPB - BE (base avec VA) | 140,2 | 139,7 | 110,4 |
| - Marge de risque (6 %) | −21,9 | −33,6 | −35,9 |
| + Fonds excédentaires | 15,1 | 19,0 | 8,7 |
| - Impôts différés passifs | 0,0 | 0,0 | −2,8 |
| **Fonds propres de niveau 1** | 2,2 | 72,7 | 81,8 |
| Intervalle à 95 % des fonds propres de niveau 1 (erreur Monte-Carlo) | [−1,3 ; 4,8] | [70,0 ; 74,8] | [80,0 ; 83,4] |

Identité vérifiée par le générateur : actif - BE - marge de risque + fonds excédentaires - impôts différés passifs = somme des lignes ci-dessus.

### 1.2 Le SCR simplifié et ce qui le détermine

| | A | B | C |
| --- | ---: | ---: | ---: |
| Taux (sens retenu) | 13,2 | 9,4 | 14,4 |
| Actions (39 %) | 30,7 | 37,0 | 38,4 |
| Spread (part non souveraine) | 46,5 | 44,6 | 46,4 |
| Marché après diversification | 73,6 | 77,0 | 80,7 |
| Rachat (sens retenu) | 44,8 | 40,7 | 34,8 |
| Mortalité + frais | 4,4 | 5,8 | 6,2 |
| Vie après diversification | 46,7 | 43,3 | 37,5 |
| BSCR net (après actions de gestion) | 96,5 | 97,3 | 97,1 |
| BSCR brut (FDB figées) | 164,1 | 204,6 | 242,5 |
| Ajustement pour absorption par les FDB | −49,5 | −107,3 | −145,3 |
| Risque opérationnel | 4,0 | 4,1 | 4,1 |
| Ajustement pour impôts différés | 0,0 | 0,0 | −2,8 |
| **SCR simplifié** | 118,6 | 101,4 | 98,4 |
| Intervalle à 95 % du SCR | [116,1 ; 120,9] | [99,9 ; 102,8] | [96,9 ; 100,0] |
| **Indicateur de couverture simplifié du SCR** | 2 % | 72 % | 83 % |
| Intervalle à 95 % de l'indicateur | [−1 ; 4] % | [70 ; 73] % | [82 ; 85] % |
| Insuffisance (SCR - fonds propres de niveau 1) | 116,3 | 28,7 | 16,6 |

**Ce qui détermine les insuffisances :**

- **A** : fonds propres comptables de 4,5 % de la PM, moins-values obligataires latentes de 19,6 % de la VNC obligataire (−185,5), partiellement compensées par l'écart provisions - BE (140,2) ; marge de risque de 21,9. SCR dominé par le spread (46,5), les actions (30,7) et le rachat (44,8, rachat massif de 40 %). L'absorption par les FDB atteint son plafond (FDB - fonds excédentaires) : le SCR dépend directement du niveau des FDB.
- **B** : fonds propres comptables de 5,0 % de la PM, moins-values obligataires latentes de 13,7 % de la VNC obligataire (−128,4), partiellement compensées par l'écart provisions - BE (139,7) ; marge de risque de 33,6. SCR dominé par le spread (44,6), les actions (37,0) et le rachat (40,7, rachat massif de 40 %). L'absorption par les FDB n'atteint pas son plafond.
- **C** : fonds propres comptables de 6,0 % de la PM, moins-values obligataires latentes de 8,0 % de la VNC obligataire (−71,4), partiellement compensées par l'écart provisions - BE (110,4) ; marge de risque de 35,9. SCR dominé par le spread (46,4), les actions (38,4) et le rachat (34,8, rachat massif de 40 %). L'absorption par les FDB n'atteint pas son plafond.

### 1.3 Le MCR : formule linéaire, corridor et minimum absolu

MCR linéaire = max(0 ; 3,7 % x (BE - FDB) - 5,2 % x (FDB - fonds excédentaires)) ; MCR combiné = MCR linéaire encadré entre 25 % et 45 % du SCR ; MCR = max(MCR combiné ; 0,4 unité). Chaque terme est calculé, puis comparé au corridor et au minimum absolu (test `test_mcr_encadre`, qui couvre les quatre contraintes possibles).

| | A | B | C |
| --- | ---: | ---: | ---: |
| 3,7 % x (BE - FDB) | 30,3 | 27,7 | 26,6 |
| - 5,2 % x FDB hors fonds excédentaires | −2,6 | −6,9 | −9,5 |
| MCR linéaire | 27,8 | 20,8 | 17,1 |
| 25 % du SCR | 29,6 | 25,3 | 24,6 |
| 45 % du SCR | 53,4 | 45,6 | 44,3 |
| Minimum absolu | 0,4 | 0,4 | 0,4 |
| **MCR simplifié** | 29,6 | 25,3 | 24,6 |
| Contrainte active | plancher de 25 % du SCR | plancher de 25 % du SCR | plancher de 25 % du SCR |
| Indicateur de couverture simplifié du MCR [IC 95 %] | 7 % [−5 ; 16] | 287 % [280 ; 293] | 333 % [327 ; 338] |

**Lecture.** Pour A, B, C, le MCR linéaire est inférieur à 25 % du SCR : le plancher s'applique, et l'indicateur MCR vaut alors quatre fois l'indicateur SCR. Le terme des FDB abaisse le MCR linéaire d'autant plus que la participation future est importante. Le minimum absolu ne joue pour aucun profil. Les indicateurs MCR élevés ne témoignent donc pas d'une marge de sécurité propre : ils reflètent le plancher du corridor.

### 1.4 Rapprochement avec les calculs précédents

| | A | B | C |
| --- | ---: | ---: | ---: |
| Indicateur SCR, synthèse avant optimisation (1 000 scénarios, sans distribution) | 0 % | 68 % | 79 % |
| Indicateur SCR, première comparaison des stratégies (500 scénarios) | 2 % | 73 % | 83 % |
| Indicateur SCR, ce document (2 000 scénarios) [IC 95 %] | 2 % [−1 ; 4] | 72 % [70 ; 73] | 83 % [82 ; 85] |
| Effet de la politique de distribution sur le BE (mêmes scénarios) | −1,7 ± 0,3 | −1,6 ± 0,4 | −0,9 ± 0,5 |

Les écarts entre ces trois calculs viennent de l'erreur Monte-Carlo du niveau du BE (même générateur, jeux de scénarios de tailles différentes) et de la politique de distribution introduite avec les stratégies. Mécanisme de cette dernière : la participation est calculée sur la quote-part des produits financiers, au rendement comptable moyen de tout l'actif. Sans distribution, les résultats conservés sont réinvestis aux taux du marché, qui dépassent en moyenne les coupons anciens dans les scénarios risque neutre ; le rendement comptable moyen monte, et les assurés en reçoivent leur quote-part. La distribution supprime cet effet : taux servi un peu plus bas les années de hausse des taux, FDB et BE plus faibles (profil B, année 10 : rendement comptable −39 pb, taux servi −13 pb). Aucun paramètre n'a été ajusté pour se rapprocher d'un repère de place.

## 2. Capital nécessaire, par stratégie

L'apport est versé en trésorerie à l'ouverture et investi ensuite au prix du marché ; le portefeuille existant ne change pas. Pour chaque stratégie, les fonds propres de niveau 1 et le SCR sont calculés pour deux apports, puis interpolés linéairement. L'intervalle à 95 % vient du rééchantillonnage des paires de scénarios (mêmes rééchantillons pour les deux apports, pour tous les chocs et pour toutes les stratégies).

**Profil A**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 2 % [−1 ; 4] | 110,4 [108,9 ; 112,1] | - | 159,5 [157,7 ; 161,2] | - |
| Réinvestissement progressif | 2 % [−1 ; 4] | 110,6 [109,2 ; 112,3] | 0,2 [0,0 ; 0,4] | 160,4 [158,6 ; 162,1] | 0,9 [0,5 ; 1,3] |
| Repositionnement | −12 % [−15 ; −9] | 129,4 [128,1 ; 130,9] | 19,0 [17,7 ; 20,2] | 183,8 [182,3 ; 185,2] | 24,3 [21,6 ; 27,0] |
| Taux servi compétitif | −4 % [−7 ; −1] | 99,9 [98,6 ; 101,5] | −10,5 [−11,3 ; −9,4] | 141,4 [140,2 ; 142,8] | −18,1 [−19,7 ; −16,2] |
| Taux servi de marge | 7 % [5 ; 9] | 118,6 [117,3 ; 120,4] | 8,3 [7,7 ; 8,9] | 177,1 [175,2 ; 179,1] | 17,7 [16,5 ; 18,8] |
| Liquidité défensive | 2 % [0 ; 4] | 128,4 [127,1 ; 129,9] | 18,0 [16,8 ; 19,3] | 188,7 [186,6 ; 190,8] | 29,3 [27,1 ; 31,4] |
| Compétitif préservant la PPB | −2 % [−5 ; 0] | 108,8 [107,4 ; 110,4] | −1,6 [−2,2 ; −1,1] | 152,8 [151,3 ; 154,5] | −6,6 [−7,7 ; −5,7] |
| Rétention de capital | 2 % [−1 ; 4] | 109,6 [108,2 ; 111,2] | −0,8 [−0,9 ; −0,6] | 157,6 [155,9 ; 159,2] | −1,9 [−2,3 ; −1,5] |

**Profil B**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 72 % [70 ; 73] | 29,5 [27,9 ; 31,3] | - | 81,2 [79,3 ; 83,0] | - |
| Réinvestissement progressif | 72 % [70 ; 74] | 29,3 [27,8 ; 31,0] | −0,2 [−0,3 ; −0,1] | 81,5 [79,6 ; 83,3] | 0,2 [0,0 ; 0,5] |
| Repositionnement | 50 % [48 ; 51] | 54,4 [53,3 ; 55,7] | 24,9 [24,1 ; 25,8] | 109,9 [108,7 ; 111,2] | 28,7 [27,2 ; 30,3] |
| Taux servi compétitif | 71 % [66 ; 72] | 27,2 [25,7 ; 30,3] | −2,3 [−2,8 ; −0,7] | 72,9 [71,2 ; 74,7] | −8,3 [−10,5 ; −6,9] |
| Taux servi de marge | 75 % [73 ; 76] | 27,1 [25,8 ; 28,6] | −2,3 [−2,9 ; −1,8] | 79,5 [77,8 ; 81,2] | −1,7 [−2,7 ; −0,7] |
| Liquidité défensive | 72 % [71 ; 74] | 29,3 [28,1 ; 30,6] | −0,2 [−0,9 ; 0,5] | 82,6 [81,1 ; 84,1] | 1,4 [0,0 ; 2,7] |
| Compétitif préservant la PPB | 68 % [63 ; 70] | 28,8 [27,2 ; 34,1] | −0,7 [−1,3 ; 3,0] | 72,9 [71,0 ; 79,2] | −8,3 [−10,3 ; −3,2] |
| Rétention de capital | 71 % [69 ; 73] | 30,0 [28,5 ; 31,9] | 0,6 [0,5 ; 0,7] | 82,1 [80,2 ; 83,9] | 0,9 [0,7 ; 1,1] |

**Profil C**

| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |
| --- | ---: | ---: | ---: | ---: | ---: |
| Passive | 83 % [82 ; 85] | 17,1 [15,6 ; 18,6] | - | 68,3 [66,1 ; 70,5] | - |
| Réinvestissement progressif | 83 % [82 ; 85] | 17,2 [15,7 ; 18,7] | 0,1 [−0,1 ; 0,3] | 69,2 [66,9 ; 71,2] | 0,8 [0,4 ; 1,3] |
| Repositionnement | 78 % [76 ; 79] | 22,9 [21,4 ; 24,5] | 5,8 [4,8 ; 6,6] | 74,0 [71,7 ; 76,2] | 5,7 [4,3 ; 6,8] |
| Taux servi compétitif | 84 % [82 ; 85] | 15,5 [14,0 ; 17,2] | −1,6 [−2,4 ; −0,7] | 64,6 [62,6 ; 66,6] | −3,7 [−5,2 ; −2,2] |
| Taux servi de marge | 87 % [86 ; 89] | 12,3 [10,8 ; 13,9] | −4,8 [−5,6 ; −3,9] | 61,9 [59,7 ; 64,0] | −6,5 [−7,9 ; −5,1] |
| Liquidité défensive | 82 % [81 ; 83] | 18,8 [17,5 ; 20,0] | 1,7 [0,8 ; 2,5] | 72,3 [70,3 ; 74,1] | 4,0 [2,7 ; 5,2] |
| Compétitif préservant la PPB | 82 % [80 ; 84] | 17,3 [15,6 ; 18,9] | 0,2 [−0,5 ; 1,0] | 66,1 [63,9 ; 68,2] | −2,3 [−3,6 ; −1,0] |
| Rétention de capital | 83 % [81 ; 84] | 17,5 [15,9 ; 19,0] | 0,4 [0,3 ; 0,5] | 69,0 [66,8 ; 71,1] | 0,7 [0,4 ; 1,0] |

**Vérification de l'interpolation** (vue prudentielle recalculée à l'apport obtenu, mêmes scénarios). L'erreur d'apport est estimée au premier ordre : (indicateur obtenu - cible) x SCR obtenu / (pente des fonds propres - cible x pente du SCR) ; positive, l'apport interpolé est trop élevé.

| Profil, stratégie, cible | Apport interpolé | Indicateur obtenu | Erreur d'apport estimée |
| --- | ---: | ---: | ---: |
| A, Passive, 100 % | 110,4 | 101,6 % | 1,6 |
| A, Passive, 150 % | 159,5 | 149,5 % | −0,4 |
| B, Passive, 100 % | 29,5 | 99,9 % | −0,1 |
| B, Passive, 150 % | 81,2 | 149,4 % | −0,6 |
| C, Passive, 100 % | 17,1 | 99,9 % | −0,1 |
| C, Passive, 150 % | 68,3 | 150,0 % | 0,0 |
| A, Taux servi de marge, 100 % | 118,6 | 100,7 % | 0,8 |
| B, Taux servi de marge, 100 % | 27,1 | 99,8 % | −0,2 |
| C, Taux servi de marge, 100 % | 12,3 | 99,9 % | −0,1 |
| A, Repositionnement, 100 % | 129,4 | 99,5 % | −0,6 |
| A, Réinvestissement progressif, 100 % | 110,6 | 101,4 % | 1,4 |
| A, Taux servi compétitif, 100 % | 99,9 | 101,8 % | 1,5 |
| A, Liquidité défensive, 100 % | 128,4 | 100,8 % | 1,0 |
| A, Compétitif préservant la PPB, 100 % | 108,8 | 101,4 % | 1,3 |
| A, Rétention de capital, 100 % | 109,6 | 102,0 % | 2,0 |

**Aucune stratégie n'atteint 100 % sans apport, pour aucun profil.** Deux erreurs entourent les besoins d'apport. L'erreur Monte-Carlo (demi-largeur des intervalles ci-dessus) va de 1,2 à 4,1 unités. L'erreur d'interpolation atteint au plus 0,6 unité pour B et C ; elle est plus forte pour A (2,0 au plus, pour « Rétention de capital »), dont la relation entre apport et indicateur n'est pas linéaire (plafond de l'absorption par les FDB, section 8). Les apports utilisés ensuite sont les apports interpolés, non corrigés, pour garder une règle identique pour toutes les stratégies. Ces erreurs pèsent peu sur la valeur : le coût net de portage de la gestion passive est d'environ 0,10 par unité d'apport pour A (section 2.1), soit moins de 0,2 de valeur nette pour l'erreur d'interpolation la plus forte. Les **écarts** de besoin entre stratégies, calculés sur les mêmes rééchantillons, sont plus précis que les besoins eux-mêmes.

### 2.1 Fonds propres existants, apports, distributions et coûts de financement

Quatre flux sont tenus séparément : (1) les fonds propres existants, déjà dans l'actif d'ouverture ; (2) les apports, initial et ultérieurs (le modèle apporte la trésorerie manquante quand tous les actifs ont été vendus), qui sont des sorties pour l'actionnaire et jamais des produits ; (3) les distributions : les fonds propres comptables sont ramenés chaque année à leur niveau d'ouverture rapporté à la PM, apport compris, l'excédent étant versé l'année suivante (la variante « rétention » n'en verse que la moitié) ; (4) le coût de financement : impôt sur les revenus du capital immobilisé et participation sur ces revenus. Aucun coût d'émission n'est appliqué. Valeur nette = actif - BE - apport initial - VA de l'impôt = VA des dividendes + VA du résidu final - apport initial - VA des apports ultérieurs - VA de l'impôt (à l'écart Monte-Carlo près).

| Profil, base (gestion passive) | VA des dividendes | VA du résidu final | - Apport initial | - VA des apports ultérieurs | - VA de l'impôt | Écart Monte-Carlo | **Valeur nette** | Coût net de portage de l'apport |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A, bilan initial, sans apport | 32,1 | −2,5 | 0,0 | −34,7 | −6,1 | 0,4 | **−10,8** | - |
| A, capital porté à 100 % du SCR simplifié | 110,0 | −1,7 | −110,4 | −7,5 | −12,5 | 0,6 | **−21,5** | 10,7 |
| A, capital porté à 150 % du SCR simplifié | 153,8 | −1,2 | −159,5 | −4,5 | −15,9 | 0,6 | **−26,6** | 15,8 |
| B, bilan initial, sans apport | 83,2 | −1,2 | 0,0 | −8,6 | −17,6 | 0,5 | **56,2** | - |
| B, capital porté à 100 % du SCR simplifié | 108,5 | −0,7 | −29,5 | −6,0 | −20,5 | 0,5 | **52,3** | 3,8 |
| B, capital porté à 150 % du SCR simplifié | 155,5 | 0,2 | −81,2 | −3,9 | −25,8 | 0,6 | **45,4** | 10,8 |
| C, bilan initial, sans apport | 108,1 | −1,0 | 0,0 | −8,2 | −22,8 | 0,9 | **77,0** | - |
| C, capital porté à 100 % du SCR simplifié | 123,2 | −0,7 | −17,1 | −6,9 | −24,7 | 0,9 | **74,7** | 2,3 |
| C, capital porté à 150 % du SCR simplifié | 170,0 | 0,0 | −68,3 | −4,4 | −30,2 | 1,0 | **68,0** | 8,9 |

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
| Passive | 110,4 | −21,5 | - | - | 4,9 % | 124,7 | 0,6 % | 2,30 % | −70 pb | 10,8 % / 5,2 % | 34 % | 80,5 |
| Réinvestissement progressif | 110,6 | −20,9 | 0,5 ± 0,1 | significatif, non important | 4,8 % | 124,0 | 0,7 % | 2,29 % | −71 pb | 10,8 % / 5,2 % | 34 % | 75,5 |
| Repositionnement | 129,4 | −33,8 | −12,3 ± 1,0 | important | 2,2 % | 87,6 | 0,0 % | 2,39 % | −60 pb | 9,4 % / 5,5 % | 31 % | 53,2 |
| Taux servi compétitif | 99,9 | −28,5 | −7,0 ± 0,4 | important | 4,6 % | 116,0 | 1,1 % | 2,43 % | −56 pb | 11,4 % / 5,8 % | 34 % | 95,6 |
| Taux servi de marge | 118,6 | −13,2 | 8,3 ± 0,4 | important | 5,2 % | 146,8 | 1,1 % | 1,89 % | −110 pb | 11,3 % / 6,4 % | 34 % | 127,9 |
| Liquidité défensive | 128,4 | −19,9 | 1,6 ± 1,1 | significatif, non important | 3,7 % | 118,2 | 0,4 % | 2,26 % | −73 pb | 11,3 % / 5,2 % | 31 % | 75,6 |
| Compétitif préservant la PPB | 108,8 | −26,1 | −4,6 ± 0,4 | important | 4,5 % | 115,2 | 0,7 % | 2,52 % | −48 pb | 11,0 % / 5,2 % | 34 % | 85,9 |
| Rétention de capital | 109,6 | −22,6 | −1,1 ± 0,1 | significatif, non important | 4,7 % | 113,4 | 0,3 % | 2,31 % | −68 pb | 10,7 % / 5,1 % | 34 % | 77,2 |

**Profil B**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 29,5 | 52,3 | - | - | 10,1 % | 103,4 | 0,3 % | 2,58 % | −41 pb | 7,9 % / 4,4 % | 16 % | 6,4 |
| Réinvestissement progressif | 29,3 | 52,5 | 0,1 ± 0,2 | non significatif | 10,0 % | 102,5 | 0,2 % | 2,57 % | −43 pb | 7,9 % / 4,4 % | 16 % | 6,1 |
| Repositionnement | 54,4 | 43,3 | −9,1 ± 0,7 | important | 7,7 % | 105,4 | 0,2 % | 2,74 % | −26 pb | 7,2 % / 4,8 % | 18 % | 25,0 |
| Taux servi compétitif | 27,2 | 40,7 | −11,6 ± 0,5 | important | 9,6 % | 96,8 | 0,4 % | 2,87 % | −13 pb | 8,8 % / 4,6 % | 20 % | 8,8 |
| Taux servi de marge | 27,1 | 61,9 | 9,6 ± 0,6 | important | 10,7 % | 106,1 | 0,2 % | 2,41 % | −58 pb | 8,0 % / 4,9 % | 19 % | 15,1 |
| Liquidité défensive | 29,3 | 53,3 | 1,0 ± 1,2 | non significatif | 9,7 % | 100,0 | 0,4 % | 2,52 % | −48 pb | 8,0 % / 4,4 % | 15 % | 6,2 |
| Compétitif préservant la PPB | 28,8 | 40,7 | −11,7 ± 0,5 | important | 9,2 % | 94,4 | 0,4 % | 2,90 % | −10 pb | 8,2 % / 4,4 % | 16 % | 8,2 |
| Rétention de capital | 30,0 | 50,8 | −1,5 ± 0,1 | significatif, non important | 9,2 % | 94,7 | 0,2 % | 2,59 % | −41 pb | 7,8 % / 4,4 % | 15 % | 5,4 |

**Profil C**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 17,1 | 74,7 | - | - | 11,9 % | 114,7 | 0,5 % | 2,83 % | −17 pb | 7,6 % / 4,3 % | 15 % | 23,0 |
| Réinvestissement progressif | 17,2 | 74,7 | 0,0 ± 0,5 | non significatif | 11,9 % | 114,5 | 0,6 % | 2,81 % | −18 pb | 7,5 % / 4,3 % | 15 % | 22,0 |
| Repositionnement | 22,9 | 73,1 | −1,6 ± 0,5 | significatif, non important | 11,3 % | 116,5 | 0,6 % | 2,89 % | −10 pb | 7,4 % / 4,2 % | 16 % | 25,5 |
| Taux servi compétitif | 15,5 | 62,5 | −12,2 ± 0,6 | important | 11,5 % | 110,0 | 0,6 % | 3,03 % | 3 pb | 8,3 % / 4,4 % | 23 % | 29,4 |
| Taux servi de marge | 12,3 | 82,0 | 7,3 ± 0,9 | important | 12,6 % | 113,1 | 0,6 % | 2,76 % | −23 pb | 7,7 % / 4,7 % | 22 % | 49,3 |
| Liquidité défensive | 18,8 | 77,5 | 2,8 ± 1,5 | important | 11,5 % | 114,7 | 0,5 % | 2,74 % | −25 pb | 7,4 % / 4,3 % | 10 % | 15,5 |
| Compétitif préservant la PPB | 17,3 | 61,8 | −12,9 ± 0,7 | important | 11,2 % | 109,4 | 0,6 % | 3,04 % | 5 pb | 8,2 % / 4,4 % | 20 % | 26,0 |
| Rétention de capital | 17,5 | 73,1 | −1,6 ± 0,1 | significatif, non important | 10,7 % | 106,0 | 0,4 % | 2,83 % | −17 pb | 7,5 % / 4,3 % | 15 % | 19,4 |

### 3.2 Capital porté à 150 % du SCR simplifié

**Profil A**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 159,5 | −26,6 | - | - | 4,5 % | 152,0 | 0,1 % | 2,35 % | −64 pb | 10,4 % / 5,0 % | 34 % | 70,9 |
| Réinvestissement progressif | 160,4 | −25,8 | 0,8 ± 0,2 | significatif, non important | 4,4 % | 151,2 | 0,4 % | 2,34 % | −65 pb | 10,3 % / 4,9 % | 34 % | 55,7 |
| Repositionnement | 183,8 | −38,6 | −12,1 ± 1,1 | important | 2,6 % | 123,6 | 0,0 % | 2,42 % | −57 pb | 9,2 % / 5,4 % | 31 % | 52,6 |
| Taux servi compétitif | 141,4 | −33,1 | −6,5 ± 0,4 | important | 4,3 % | 138,8 | 0,4 % | 2,50 % | −49 pb | 11,1 % / 5,4 % | 34 % | 86,4 |
| Taux servi de marge | 177,1 | −18,2 | 8,3 ± 0,4 | important | 4,6 % | 182,3 | 0,2 % | 1,97 % | −103 pb | 10,8 % / 6,0 % | 34 % | 111,8 |
| Liquidité défensive | 188,7 | −26,4 | 0,2 ± 1,1 | non significatif | 3,5 % | 149,5 | 0,3 % | 2,34 % | −66 pb | 10,7 % / 4,9 % | 25 % | 56,8 |
| Compétitif préservant la PPB | 152,8 | −31,1 | −4,5 ± 0,4 | important | 4,2 % | 138,6 | 0,2 % | 2,58 % | −41 pb | 10,7 % / 5,0 % | 34 % | 75,3 |
| Rétention de capital | 157,6 | −27,9 | −1,3 ± 0,1 | significatif, non important | 4,4 % | 137,6 | 0,0 % | 2,36 % | −63 pb | 10,3 % / 4,9 % | 34 % | 65,7 |

**Profil B**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 81,2 | 45,4 | - | - | 7,4 % | 132,0 | 0,0 % | 2,61 % | −39 pb | 7,6 % / 4,4 % | 14 % | 5,5 |
| Réinvestissement progressif | 81,5 | 45,6 | 0,2 ± 0,2 | non significatif | 7,3 % | 131,2 | 0,2 % | 2,59 % | −41 pb | 7,6 % / 4,4 % | 14 % | 5,3 |
| Repositionnement | 109,9 | 36,1 | −9,3 ± 0,7 | important | 6,2 % | 139,2 | 0,0 % | 2,77 % | −23 pb | 7,1 % / 4,7 % | 18 % | 20,3 |
| Taux servi compétitif | 72,9 | 34,3 | −11,1 ± 0,6 | important | 7,2 % | 121,8 | 0,1 % | 2,89 % | −10 pb | 8,5 % / 4,5 % | 19 % | 7,2 |
| Taux servi de marge | 79,5 | 54,8 | 9,4 ± 0,6 | important | 7,6 % | 136,2 | 0,0 % | 2,46 % | −53 pb | 7,7 % / 4,8 % | 15 % | 14,4 |
| Liquidité défensive | 82,6 | 46,2 | 0,8 ± 1,3 | non significatif | 7,0 % | 129,0 | 0,3 % | 2,53 % | −47 pb | 7,7 % / 4,4 % | 12 % | 2,7 |
| Compétitif préservant la PPB | 72,9 | 34,2 | −11,2 ± 0,6 | important | 7,0 % | 118,2 | 0,2 % | 2,92 % | −7 pb | 8,0 % / 4,4 % | 15 % | 6,0 |
| Rétention de capital | 82,1 | 43,4 | −2,0 ± 0,1 | significatif, non important | 6,9 % | 121,2 | 0,0 % | 2,61 % | −38 pb | 7,5 % / 4,4 % | 14 % | 4,2 |

**Profil C**

| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | 68,3 | 68,0 | - | - | 8,5 % | 144,1 | 0,3 % | 2,84 % | −15 pb | 7,4 % / 4,3 % | 15 % | 21,0 |
| Réinvestissement progressif | 69,2 | 68,1 | 0,0 ± 0,5 | non significatif | 8,4 % | 144,1 | 0,5 % | 2,82 % | −17 pb | 7,3 % / 4,3 % | 13 % | 17,2 |
| Repositionnement | 74,0 | 66,1 | −2,0 ± 0,6 | significatif, non important | 8,3 % | 145,9 | 0,2 % | 2,91 % | −8 pb | 7,3 % / 4,2 % | 15 % | 26,3 |
| Taux servi compétitif | 64,6 | 56,2 | −11,8 ± 0,6 | important | 8,4 % | 138,2 | 0,4 % | 3,04 % | 4 pb | 8,1 % / 4,4 % | 19 % | 25,4 |
| Taux servi de marge | 61,9 | 75,6 | 7,5 ± 0,9 | important | 8,9 % | 142,3 | 0,3 % | 2,79 % | −21 pb | 7,5 % / 4,7 % | 20 % | 46,7 |
| Liquidité défensive | 72,3 | 70,6 | 2,5 ± 1,5 | important | 8,2 % | 145,2 | 0,3 % | 2,74 % | −25 pb | 7,2 % / 4,3 % | 7 % | 14,3 |
| Compétitif préservant la PPB | 66,1 | 55,6 | −12,5 ± 0,6 | important | 8,2 % | 137,5 | 0,4 % | 3,05 % | 6 pb | 8,0 % / 4,4 % | 17 % | 21,9 |
| Rétention de capital | 69,0 | 66,0 | −2,1 ± 0,1 | important | 7,9 % | 133,5 | 0,2 % | 2,84 % | −15 pb | 7,3 % / 4,3 % | 14 % | 18,1 |

Rendement des fonds propres : résultat net d'impôt rapporté aux fonds propres comptables d'ouverture de chaque année, agrégé sur les scénarios, à comparer à un rendement exigé fictif de 8 %. Les indicateurs réels n'ont pas d'intervalle apparié ; leurs écarts entre stratégies portent sur les mêmes scénarios.

## 4. Réinvestissement progressif : significativité et importance

Écart de valeur nette à la gestion passive ± intervalle apparié à 95 % :

| Profil | Bilan initial | Base 100 % | Base 150 % |
| --- | ---: | ---: | ---: |
| A | 0,08 ± 0,09 | 0,55 ± 0,13 | 0,75 ± 0,17 |
| B | 0,04 ± 0,20 | 0,10 ± 0,21 | 0,18 ± 0,23 |
| C | 0,01 ± 0,47 | 0,02 ± 0,47 | 0,02 ± 0,48 |

Contrôle sur des tirages indépendants (profil A, base 100 %, 2 000 scénarios, autres graines pour les scénarios et les défauts) : 0,57 ± 0,10.

- **Statistiquement**, l'écart du profil A sur la base 100 % (0,55 ± 0,13) est significatif et se retrouve sur des tirages indépendants.
- **Économiquement**, il est faible : 0,06 % du BE et 0,5 % du SCR simplifié, pour un seuil d'importance de 2,4 (2 % du SCR). Il est aussi petit devant l'incertitude du besoin d'apport du profil (intervalle de largeur 3,1) et devant les écarts des politiques de taux servi.
- **Mécanisme** : l'écart n'apparaît que lorsque des achats obligataires importants passent par l'échelle de maturités, comme le réinvestissement de l'apport de A ; sur le bilan initial, les flux réinvestis sont faibles devant le stock obligataire.
- **Conclusion** : le réinvestissement progressif est statistiquement distinguable de la gestion passive pour A recapitalisé, mais pas économiquement distinguable avec les seuils retenus.

## 5. Deux variantes : politique compétitive préservant la PPB, rétention de capital

Politique compétitive préservant la PPB : même cible que la politique compétitive (la référence), mais reprises volontaires limitées à 25 % par an de la part de la PPB qui dépasse la moitié du ratio PPB / PM d'ouverture. Rétention : règles de la gestion passive, la moitié seulement de l'excédent annuel de fonds propres est distribuée. Base 100 %, écarts à la gestion passive :

| Profil | Stratégie | Valeur nette ± IC | Lecture | Apport à 100 % | Écart du taux servi à la référence (réel) | Rachat 1-10 RN | Probabilité d'apport sur 60 ans (réel) | Rendement des fonds propres (réel) |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| A | Taux servi compétitif | −7,0 ± 0,4 | important | −10,5 | 13 pb | 56 pb | 0,5 pt | −0,30 pt |
| A | Compétitif préservant la PPB | −4,6 ± 0,4 | important | −1,6 | 22 pb | 21 pb | 0,1 pt | −0,40 pt |
| A | Rétention de capital | −1,1 ± 0,1 | significatif, non important | −0,8 | 1 pb | −13 pb | −0,3 pt | −0,15 pt |
| B | Taux servi compétitif | −11,6 ± 0,5 | important | −2,3 | 28 pb | 86 pb | 0,1 pt | −0,54 pt |
| B | Compétitif préservant la PPB | −11,7 ± 0,5 | important | −0,7 | 31 pb | 35 pb | 0,1 pt | −0,92 pt |
| B | Rétention de capital | −1,5 ± 0,1 | significatif, non important | 0,6 | 0 pb | −7 pb | −0,1 pt | −0,93 pt |
| C | Taux servi compétitif | −12,2 ± 0,6 | important | −1,6 | 20 pb | 78 pb | 0,1 pt | −0,40 pt |
| C | Compétitif préservant la PPB | −12,9 ± 0,7 | important | 0,2 | 21 pb | 60 pb | 0,1 pt | −0,73 pt |
| C | Rétention de capital | −1,6 ± 0,1 | significatif, non important | 0,4 | 0 pb | −8 pb | −0,1 pt | −1,23 pt |

Trajectoires risque neutre (bilan initial), gestion passive / compétitive / compétitive préservant la PPB :

| Profil | Année | PPB / PM | Part des scénarios hors zone neutre | Taux de rachat |
| --- | ---: | ---: | ---: | ---: |
| A | 1 | 1,81 % / 1,25 % / 2,03 % | 10 % / 8 % / 11 % | 4,3 % / 4,3 % / 4,3 % |
| A | 5 | 0,80 % / 0,11 % / 1,40 % | 84 % / 89 % / 85 % | 12,2 % / 12,8 % / 13,1 % |
| A | 8 | 0,06 % / 0,00 % / 0,03 % | 79 % / 85 % / 78 % | 17,1 % / 17,8 % / 16,9 % |
| A | 10 | 0,03 % / 0,00 % / 0,01 % | 82 % / 84 % / 83 % | 18,4 % / 18,8 % / 18,5 % |
| A | 20 | 0,50 % / 0,12 % / 0,20 % | 65 % / 67 % / 66 % | 17,8 % / 18,3 % / 17,9 % |
| B | 1 | 3,57 % / 3,01 % / 3,37 % | 2 % / 0 % / 6 % | 4,3 % / 4,3 % / 4,3 % |
| B | 5 | 1,65 % / 0,37 % / 2,06 % | 42 % / 52 % / 45 % | 7,3 % / 7,7 % / 8,1 % |
| B | 8 | 0,60 % / 0,04 % / 0,30 % | 47 % / 63 % / 48 % | 11,1 % / 13,4 % / 11,1 % |
| B | 10 | 0,43 % / 0,03 % / 0,21 % | 54 % / 63 % / 58 % | 12,4 % / 14,1 % / 13,2 % |
| B | 20 | 2,66 % / 0,81 % / 1,56 % | 28 % / 36 % / 36 % | 9,8 % / 11,0 % / 10,7 % |
| C | 1 | 2,20 % / 1,69 % / 1,82 % | 2 % / 1 % / 2 % | 4,3 % / 4,3 % / 4,3 % |
| C | 5 | 1,95 % / 0,50 % / 1,32 % | 28 % / 34 % / 34 % | 6,4 % / 6,8 % / 6,9 % |
| C | 8 | 1,67 % / 0,25 % / 0,69 % | 42 % / 52 % / 47 % | 10,8 % / 12,4 % / 11,8 % |
| C | 10 | 1,31 % / 0,23 % / 0,56 % | 42 % / 54 % / 53 % | 11,7 % / 13,5 % / 13,0 % |
| C | 20 | 2,85 % / 0,98 % / 1,67 % | 29 % / 39 % / 38 % | 10,3 % / 12,0 % / 11,9 % |

**Lecture.**

- **Préserver la PPB, par rapport à la politique compétitive de base** (A : 2,4 de valeur, 8 pb de taux servi, −35 pb de rachat ; B : −0,1 de valeur, 3 pb de taux servi, −52 pb de rachat ; C : −0,6 de valeur, 1 pb de taux servi, −17 pb de rachat ; mêmes scénarios, sans intervalle calculé pour cet écart) : garder une partie de la PPB pour les années où la référence monte réduit nettement les rachats (A, B) ; le gain d'écart à la référence n'est important que pour A, et la valeur ne s'améliore nettement que pour A. Le coût en valeur par rapport à la gestion passive demeure : la politique reste compétitive, donc moins de participation non servie revient à l'actionnaire.
- **Rétention** : la valeur baisse un peu (impôt et participation sur les revenus du capital conservé, rendement comptable relevé et partagé avec les assurés, section 1.4) ; l'écart ne dépasse le seuil d'importance que pour C à 150 %, au niveau du seuil. Le rendement des fonds propres baisse davantage, car le capital conservé dilue le résultat. Le bénéfice attendu de la rétention, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR. La rétention ne réduit pas l'apport initial nécessaire ; elle réduit un peu la probabilité d'apport ultérieur.

## 6. Matrice de décision exploratoire

Écarts à la gestion passive sur la base de capital commune, A / B / C. En gras : écart important (au-delà du seuil de lecture) ; « ns » : écart non significatif (intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle et de rachat n'ont pas d'intervalle). « Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital et sous les trois sensibilités de la section 7.

**Capital porté à 100 % du SCR simplifié**

| Stratégie | Valeur actionnaire (RN) | Rentabilité (réel) | Compétitivité : taux servi (réel) | Rachats (RN) | Liquidité : moins-values réalisées q99 (réel) | Capital : apport nécessaire | Capital : probabilité d'apport ultérieur sur 60 ans (réel) | Écart de valeur robuste (profils) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,5 / 0,1 ns / 0,0 ns | −0,07 pt / −0,10 pt / −0,07 pt | −1 pb / −2 pb / −1 pb | −6 pb / −1 pb / −2 pb | −5,0 / −0,3 / −1,0 | 0,2 / −0,2 / 0,1 ns | 0,1 pt / −0,1 pt / 0,1 pt | aucun profil |
| Repositionnement | **−12,3** / **−9,1** / −1,6 | **−2,69 pt** / **−2,46 pt** / **−0,66 pt** | **10 pb** / **15 pb** / **6 pb** | **−139 pb** / **−68 pb** / −12 pb | **−27,4** / **18,6** / 2,5 | **19,0** / **24,9** / **5,8** | **−0,6 pt** / −0,1 pt / 0,1 pt | A, B |
| Taux servi compétitif | **−7,0** / **−11,6** / **−12,2** | **−0,30 pt** / **−0,54 pt** / **−0,40 pt** | **13 pb** / **28 pb** / **20 pb** | **56 pb** / **86 pb** / **78 pb** | **15,0** / 2,4 / **6,4** | **−10,5** / **−2,3** / −1,6 | 0,5 pt / 0,1 pt / 0,1 pt | A, B, C |
| Taux servi de marge | **8,3** / **9,6** / **7,3** | **0,29 pt** / **0,56 pt** / **0,71 pt** | **−40 pb** / **−17 pb** / **−7 pb** | **45 pb** / 12 pb / 16 pb | **47,4** / **8,7** / **26,2** | **8,3** / **−2,3** / **−4,8** | 0,5 pt / −0,1 pt / 0,1 pt | A, B, C |
| Liquidité défensive | 1,6 / 1,0 ns / **2,8** | **−1,21 pt** / **−0,46 pt** / **−0,40 pt** | −4 pb / **−7 pb** / **−9 pb** | **48 pb** / 12 pb / −11 pb | −4,9 / −0,2 / **−7,5** | **18,0** / −0,2 ns / 1,7 | −0,2 pt / 0,1 pt / 0,0 pt | C |
| Compétitif préservant la PPB | **−4,6** / **−11,7** / **−12,9** | **−0,40 pt** / **−0,92 pt** / **−0,73 pt** | **22 pb** / **31 pb** / **21 pb** | 21 pb / **35 pb** / **60 pb** | 5,4 / 1,8 / 3,0 | −1,6 / −0,7 ns / 0,2 ns | 0,1 pt / 0,1 pt / 0,1 pt | A, B, C |
| Rétention de capital | −1,1 / −1,5 / −1,6 | −0,15 pt / **−0,93 pt** / **−1,23 pt** | 1 pb / 0 pb / 0 pb | −13 pb / −7 pb / −8 pb | −3,4 / −1,0 / −3,6 | −0,8 / 0,6 / 0,4 | −0,3 pt / −0,1 pt / −0,1 pt | aucun profil |

**Capital porté à 150 % du SCR simplifié**

| Stratégie | Valeur actionnaire (RN) | Rentabilité (réel) | Compétitivité : taux servi (réel) | Rachats (RN) | Liquidité : moins-values réalisées q99 (réel) | Capital : apport nécessaire | Capital : probabilité d'apport ultérieur sur 60 ans (réel) | Écart de valeur robuste (profils) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,8 / 0,2 ns / 0,0 ns | −0,08 pt / −0,10 pt / −0,08 pt | −1 pb / −2 pb / −2 pb | −13 pb / −4 pb / −6 pb | **−15,3** / −0,1 / −3,8 | 0,9 / 0,2 / 0,8 | 0,3 pt / 0,2 pt / 0,2 pt | aucun profil |
| Repositionnement | **−12,1** / **−9,3** / −2,0 | **−1,85 pt** / **−1,17 pt** / −0,23 pt | **7 pb** / **16 pb** / **7 pb** | **−120 pb** / **−49 pb** / −8 pb | **−18,3** / **14,8** / **5,3** | **24,3** / **28,7** / **5,7** | −0,1 pt / 0,0 pt / −0,1 pt | A, B |
| Taux servi compétitif | **−6,5** / **−11,1** / **−11,8** | −0,20 pt / −0,17 pt / −0,18 pt | **15 pb** / **29 pb** / **19 pb** | **66 pb** / **87 pb** / **79 pb** | **15,5** / 1,8 / 4,5 | **−18,1** / **−8,3** / **−3,7** | 0,3 pt / 0,1 pt / 0,1 pt | A, B, C |
| Taux servi de marge | **8,3** / **9,4** / **7,5** | 0,16 pt / 0,21 pt / **0,34 pt** | **−38 pb** / **−15 pb** / **−6 pb** | **38 pb** / 11 pb / 16 pb | **40,9** / **9,0** / **25,7** | **17,7** / −1,7 / **−6,5** | 0,1 pt / 0,0 pt / 0,0 pt | A, B, C |
| Liquidité défensive | 0,2 ns / 0,8 ns / **2,5** | **−1,00 pt** / **−0,39 pt** / **−0,35 pt** | −1 pb / **−8 pb** / **−10 pb** | 23 pb / 7 pb / −18 pb | **−14,1** / −2,8 / **−6,7** | **29,3** / 1,4 / **4,0** | 0,2 pt / 0,3 pt / 0,0 pt | C |
| Compétitif préservant la PPB | **−4,5** / **−11,2** / **−12,5** | **−0,29 pt** / **−0,34 pt** / **−0,32 pt** | **23 pb** / **31 pb** / **21 pb** | 24 pb / **42 pb** / **63 pb** | 4,3 / 0,5 / 0,9 | **−6,6** / **−8,3** / **−2,3** | 0,1 pt / 0,2 pt / 0,1 pt | A, B, C |
| Rétention de capital | −1,3 / −2,0 / **−2,1** | −0,11 pt / **−0,46 pt** / **−0,60 pt** | 1 pb / 0 pb / 0 pb | −16 pb / −8 pb / −9 pb | −5,3 / −1,3 / −2,9 | −1,9 / 0,9 / 0,7 | −0,1 pt / 0,0 pt / −0,1 pt | aucun profil |

Sens de lecture : une valeur, une rentabilité ou un écart de taux servi positifs sont favorables ; des rachats, des moins-values réalisées, un apport ou une probabilité d'apport positifs sont défavorables.

## 7. Sensibilité de la valeur aux hypothèses fragiles (base 100 %)

Écart de valeur nette à la gestion passive ± intervalle apparié, avec les apports du centre. Les besoins d'apport ne sont pas recalculés sous chaque sensibilité.

**Profil A**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,5 ± 0,1 | 0,1 ± 0,0 | 0,4 ± 0,1 | 0,5 ± 0,2 |
| Repositionnement | −12,3 ± 1,0 | −3,5 ± 0,7 | −9,6 ± 1,0 | −12,9 ± 1,1 |
| Taux servi compétitif | −7,0 ± 0,4 | −3,9 ± 0,3 | −6,1 ± 0,4 | −7,1 ± 0,4 |
| Taux servi de marge | 8,3 ± 0,4 | 4,0 ± 0,6 | 6,4 ± 0,6 | 9,0 ± 0,5 |
| Liquidité défensive | 1,6 ± 1,1 | 3,4 ± 0,5 | 2,4 ± 0,8 | 1,0 ± 1,1 |
| Compétitif préservant la PPB | −4,6 ± 0,4 | −1,3 ± 0,4 | −4,2 ± 0,4 | −5,2 ± 0,4 |
| Rétention de capital | −1,1 ± 0,1 | −0,8 ± 0,1 | −1,0 ± 0,1 | −1,3 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Taux servi de marge ; Transmission immédiate des taux : Taux servi de marge ; Défaut corrélé par bloc souverain : Taux servi de marge. Le premier rang ne change pas sous ces trois sensibilités.

**Profil B**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,1 ± 0,2 | 0,0 ± 0,1 | 0,4 ± 0,2 | 0,2 ± 0,2 |
| Repositionnement | −9,1 ± 0,7 | −4,2 ± 0,6 | −9,2 ± 0,7 | −10,3 ± 0,8 |
| Taux servi compétitif | −11,6 ± 0,5 | −4,5 ± 0,7 | −7,0 ± 0,5 | −11,7 ± 0,6 |
| Taux servi de marge | 9,6 ± 0,6 | 3,8 ± 0,5 | 5,7 ± 0,5 | 9,3 ± 0,6 |
| Liquidité défensive | 1,0 ± 1,2 | 2,7 ± 0,8 | 3,7 ± 1,0 | 1,0 ± 1,2 |
| Compétitif préservant la PPB | −11,7 ± 0,5 | −4,7 ± 0,8 | −7,5 ± 0,5 | −11,5 ± 0,7 |
| Rétention de capital | −1,5 ± 0,1 | −1,0 ± 0,1 | −1,4 ± 0,1 | −1,7 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Taux servi de marge ; Transmission immédiate des taux : Taux servi de marge ; Défaut corrélé par bloc souverain : Taux servi de marge. Le premier rang ne change pas sous ces trois sensibilités.

**Profil C**

| Stratégie | Centre | Réaction forte (ONC max.) | Transmission immédiate des taux | Défaut corrélé par bloc souverain |
| --- | ---: | ---: | ---: | ---: |
| Réinvestissement progressif | 0,0 ± 0,5 | 0,1 ± 0,3 | 0,6 ± 0,4 | 0,3 ± 0,5 |
| Repositionnement | −1,6 ± 0,5 | −0,9 ± 0,4 | −2,0 ± 0,4 | −2,2 ± 0,5 |
| Taux servi compétitif | −12,2 ± 0,6 | −4,8 ± 0,7 | −6,0 ± 0,5 | −11,7 ± 0,7 |
| Taux servi de marge | 7,3 ± 0,9 | 2,7 ± 0,4 | 4,9 ± 0,5 | 6,7 ± 0,6 |
| Liquidité défensive | 2,8 ± 1,5 | 3,5 ± 1,0 | 4,4 ± 1,2 | 3,0 ± 1,5 |
| Compétitif préservant la PPB | −12,9 ± 0,7 | −5,4 ± 0,7 | −6,7 ± 0,5 | −12,8 ± 0,7 |
| Rétention de capital | −1,6 ± 0,1 | −1,2 ± 0,1 | −1,5 ± 0,1 | −1,9 ± 0,1 |

Plus forte valeur nette : Centre : Taux servi de marge ; Réaction forte (ONC max.) : Liquidité défensive ; Transmission immédiate des taux : Taux servi de marge ; Défaut corrélé par bloc souverain : Taux servi de marge. **Le premier rang change avec les hypothèses.**

## 8. Mécanismes

- **Politique de marge** : transfert de la participation non servie vers l'actionnaire, dont le seul coût en portefeuille fermé est le surcroît de rachats dynamiques, borné par la zone neutre et le plafond de la loi de rachat. L'avantage fermé n'est pas, par principe, un majorant : avec une collecte sensible au taux servi, il l'est seulement si la valeur des affaires nouvelles de la politique de marge est inférieure à celle de la gestion passive (`docs/V5_COLLECTE.md`, section 3).
- **Politique compétitive** : la PPB est consommée tôt ; quand la référence monte, l'écart sort plus souvent de la zone neutre et les rachats remontent (profil B, année 8 : PPB de 0,04 % de la PM contre 0,60 %, 63 % des scénarios hors zone neutre contre 47 %). La variante préservant la PPB garde un stock plus élevé les premières années (année 5 : 2,06 % contre 0,37 %) ; le plancher ne limite que les reprises volontaires, et la reprise obligatoire des dotations de plus de 8 ans fait ensuite fortement baisser le stock (0,30 % à l'année 8), ce qui borne l'effet de la variante (section 5).
- **Repositionnement** : vente au prix de marché, mais la moins-value réalisée passe par la réserve de capitalisation puis par le résultat, tandis que les coupons plus élevés rachetés ensuite reviennent pour au moins 85 % aux assurés : l'actionnaire supporte la perte et partage le gain.
- **Liquidité défensive** : en risque neutre, moins de volatilité réduit le coût des options (garantie et asymétrie de la participation) ; en probabilité réelle, la prime actions fictive est perdue.
- **Rétention de capital** : plus de fonds propres conservés, donc moins d'apports ultérieurs, mais davantage d'impôt sur leurs revenus et un rendement comptable plus élevé partagé avec les assurés (section 1.4).
- **Plafond de l'absorption par les FDB** (profil A) : quand l'absorption atteint son plafond (FDB - fonds excédentaires), le SCR vaut le BSCR brut moins ce plafond, plus le risque opérationnel ; toute baisse des FDB l'augmente à l'unité. La politique compétitive abaisse le BSCR brut de A (149,4 contre 164,1) et demande moins de capital ; la politique de marge abaisse les FDB (51,0 contre 64,6) et en demande davantage. Pour B et C, l'absorption n'est pas plafonnée et la politique de marge demande moins de capital. Le sens de l'effet d'une stratégie sur le capital dépend donc du profil.

## 9. Limites

- **Indicateurs simplifiés** : pas de mesure transitoire, ajustement symétrique nul, modules non modélisés (contrepartie, concentration, immobilier, change), marge de risque probablement surestimée, fonds excédentaires par l'approche simplifiée, impôts différés actifs non reconnus.
- **Portefeuille fermé** : aucune collecte nouvelle dans ce document. La collecte sensible au taux servi relatif est traitée dans `docs/V5_COLLECTE.md` (spécification : `docs/V5_SPECIFICATION_COLLECTE.md`).
- **Comportement des assurés** : loi de rachat dynamique des V1 à V4 au centre, corridors ONC de 2013 en sensibilité ; aucune donnée 2026 ne calibre la réaction des assurés.
- **Stratégies non optimisées** : un jeu de paramètres par famille et deux variantes ; une seule politique de distribution de base.
- **Interpolation des besoins d'apport** entre deux points, vérifiée par recalcul pour passive (A, B, C), réinvestissement progressif (A), repositionnement (A), taux servi compétitif (A), taux servi de marge (A, B, C), liquidité défensive (A), compétitif préservant la PPB (A), rétention de capital (A) ; apports interpolés non corrigés ; les sensibilités de la section 7 gardent les apports du centre.
- **Probabilité réelle** : taux sans prime de terme, spreads figés, prime actions fictive de 3 %, défauts aux taux historiques ; probabilités de recapitalisation conditionnelles à ces hypothèses ; écarts réels sans intervalle apparié.
- **Coûts de financement** : impôt et participation sur les revenus du capital ; ni coût d'émission, ni dette subordonnée, ni prime de rendement exigée intégrée à la valeur risque neutre.
- **ACPR n° 185** non lu.

