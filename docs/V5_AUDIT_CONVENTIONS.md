# V5.1 : audit des conventions, données de marché et comparaison avec la V5.0

> Document généré par `scripts/v5_rapport_audit.py` à partir de `resultats/v5_0/` (résultats de la V5.0 publiée le 07/11/2026, conservés pour la comparaison), des résultats de la V5.1 (`resultats/v5_consolidation.json`, `v5_collecte.json`, `v5_synthese_finale.json`, `v5_reconciliation_collecte.json`), de `resultats/v5_audit_conventions.json` et de `data/v5/marche/spread_hypothetique_20261031.json`. Montants en unités de 10 M€. Profils fictifs ; indicateurs Solvabilité II simplifiés, qui ne sont pas des ratios réglementaires.

Un audit indépendant de la V5.0 a relevé deux questions actuarielles (participation aux résultats, impôt dans la projection) et des points de présentation (courbes de taux, précision des apports). La revue des données de marché a ajouté un point de conformité : la V5.0 utilisait des indices de taux de l'État dont la redistribution est soumise à autorisation. Ce document reprend chacun de ces points : textes ou conventions, vérification sur le code, mesure de l'effet, décision. La V5.1 change deux choses : la participation aux résultats (compte de participation avec sa composante technique) et le spread des obligations détenues (hypothèse construite à partir de paramètres publiés par l'EIOPA). Les V1 à V4 ne changent pas.

## 1. Synthèse

| Point | Constat initial | Vérification | Erreur ou limite | Correction | Effet économique |
| --- | --- | --- | --- | --- | --- |
| Participation aux résultats | minimum de 85 % de la quote-part des produits financiers seulement | articles A.132-11 à A.132-16 ; moteur, `src/strategie.py` | **erreur confirmée** : composante technique du compte absente | V5.1 : compte simplifié et plancher de la participation de l'exercice | valeur, à capital et marché identiques : A −2,2, B −7,0, C −10,6 ; taux servi en hausse |
| Données de marché | spread des obligations calé sur des indices de taux de l'État (TEC), dates différentes de la courbe EIOPA | conditions de réutilisation des sources | **conformité** : redistribution des indices soumise à l'autorisation de leur administrateur | V5.1 : spread hypothétique construit à partir des moyennes de long terme publiées par l'EIOPA ; plus aucune donnée d'indice | niveaux de valeur et de capital modifiés (section 4) ; comparaisons de stratégies sur un même marché |
| Impôt dans la projection | impôt calculé après coup, non décaissé | identités de flux, variante payée chaque année (tests) | **convention**, sans double comptage ; dividendes de la projection avant impôt | aucune : convention documentée, variante disponible | valeur : A +0,15, B +0,28, C +0,27 |
| Apports visant 100 % | indicateur recalculé de 99,5 % à 101,6 % (V5.0) | recalcul direct aux apports interpolés | **limite** : interpolation linéaire | formulation « apport estimé visant 100 % » | indicateur recalculé de 99,1 % à 102,7 % (V5.1) |

Valeur de l'existant recapitalisé à 100 %, gestion passive : A −21,5 en V5.0, −5,4 en V5.1, B 52,3 en V5.0, 57,8 en V5.1, C 74,7 en V5.0, 82,8 en V5.1. L'écart cumule les deux changements ; la section 4 sépare l'effet de la participation, mesuré à capital et marché identiques.

## 2. Participation aux résultats

### 2.1 Textes

Code des assurances (Légifrance ; versions en vigueur au 07/11/2026, lues dans leur traduction publiée par french-business-law.com, Légifrance n'étant pas accessible depuis l'environnement de calcul) :

- **A.132-11, I** : la participation minimale est déterminée globalement à partir d'un compte de participation aux résultats. Au crédit : les éléments techniques (solde de souscription, charges d'acquisition et de gestion nettes), 85 % du solde du compte financier, le solde de réassurance cédée. Au débit : la part de l'assureur dans les bénéfices techniques, égale au plus élevé de 10 % du solde créditeur des éléments techniques et de 4,5 % des primes des catégories 3 et 6, et, le cas échéant, le solde débiteur de l'exercice précédent.
- **A.132-12** : le montant minimal de la participation de l'exercice est le solde créditeur de ce compte, diminué des intérêts crédités aux provisions mathématiques (et augmenté, contrat par contrat, d'un complément pour les contrats dont le taux garanti dépasse le taux moyen servi).
- **A.132-13 et A.132-14** : solde financier et quote-part des produits afférente aux provisions techniques.
- **A.132-16** : la participation mise en provision (PPB) est redistribuée dans les huit exercices suivants.
- **A.344-2** : catégories de contrats ; 3 : contrats individuels d'assurance temporaire décès ; 6 : contrats collectifs en cas de décès. Les contrats d'épargne en euros modélisés relèvent des catégories 4 et 5 : le seuil de 4,5 % des primes ne s'applique pas.

### 2.2 Composantes réglementaires et moteur

| Composante | Règle | V5.0 | V5.1 |
| --- | --- | --- | --- |
| Solde financier | 85 % de la quote-part des produits nets afférente aux provisions | modélisé : 85 % x (PM + PPB) / actif comptable x produits positifs | identique ; les plus-values actions réalisées entrent au compte de l'exercice |
| Chargements prélevés | éléments techniques, au crédit | **absents du compte** : gardés en totalité par l'assureur | au compte (sur encours et sur primes) |
| Frais de gestion et d'acquisition | éléments techniques, au débit | absents du compte | au compte |
| Part de l'assureur | plus élevé de 10 % du solde technique créditeur et de 4,5 % des primes des catégories 3 et 6 | 100 % du solde technique | 10 % du solde créditeur ; solde débiteur en totalité au compte |
| Résultat de mortalité | solde de souscription | absent : le décès verse la PM | absent (simplification) |
| Réassurance cédée | au compte | absente | absente (simplification) |
| Solde débiteur du compte | reporté sur l'exercice suivant | absent | reporté ; un solde financier négatif n'est pas reporté (comme en V5.0) |
| Intérêts techniques et garanties | déduits du solde pour obtenir la participation | taux servi et TMG dans les intérêts crédités ; le complément de TMG est payé par l'assureur | idem, le complément de TMG compte dans la participation de l'exercice |
| Plancher | participation de l'exercice au moins égale au solde créditeur | plancher financier seulement | plancher sur intérêts crédités + dotation à la PPB - reprises de PPB |
| PPB | redistribution sous 8 ans | modélisée par génération | inchangée |
| Complément contrat par contrat (A.132-12) | contrats à taux garanti supérieur au taux moyen | absent | absent (un seul taux servi par ensemble de contrats) |

Les paramètres du modèle donnent un solde technique d'environ 0,23 % de la PM : chargements de 0,63 % (observés, moyenne de place) moins frais de 0,40 % (fictifs, valeur des V1 à V4), dont l'assureur garde 10 % quand le solde est créditeur. Ce solde n'est pas en lui-même un montant distribuable : il entre au compte, et le compte ne fixe qu'un minimum. Quand la participation que décide déjà la politique de taux servi (abandon de marge, complément de TMG, plus-values réalisées) dépasse le compte, la V5.1 ne change rien. Le complément ne joue que les années où la participation de l'exercice serait restée sous le compte : il sert d'abord le taux cible s'il n'est pas atteint, puis remplace des reprises volontaires de PPB, puis est doté à la PPB.

### 2.3 Effet à capital et marché identiques (gestion passive, mêmes scénarios)

Les deux conventions sont projetées avec les données de marché de la V5.1 et l'apport estimé de la V5.1 pour 100 % (A 101,0, B 25,4, C 0,0), sur 1 000 scénarios risque neutre ; écarts appariés scénario par scénario, avec leur intervalle à 95 % (incertitude Monte-Carlo de l'écart, distincte de l'incertitude de convention). « Convention V5.0 » : participation aux seuls produits financiers. Contrôle : la convention de la V5.1 reproduit les valeurs de `resultats/v5_consolidation.json` (écart maximal 1,4 × 10⁻¹³).

| Profil | Valeur nette, convention V5.0 | Valeur nette V5.1 | Écart | Écart relatif | BE | FDB | Taux servi, années 1 à 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | −3,2 | −5,4 | −2,18 ± 0,26 | −67,6 % | +2,8 | +6,1 | +3,7 pb |
| **B** | 64,8 | 57,8 | −6,98 ± 0,37 | −10,8 % | +8,9 | +16,0 | +6,7 pb |
| **C** | 93,4 | 82,8 | −10,63 ± 0,58 | −11,4 % | +13,8 | +21,5 | +9,3 pb |

| Profil | Dotation PPB / PM (an, 1 à 10) | Reprise PPB / PM | PPB / PM, année 10 | Marge abandonnée, cumul 1 à 10 | Années avec complément | Complément / PM (an) | Scénarios avec solde débiteur |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | 0,01 % → 0,02 % | 0,31 % → 0,31 % | 0,06 % → 0,18 % | 11,2 → 11,0 | 31 % | 0,046 % | 0,0 % |
| **B** | 0,08 % → 0,13 % | 0,49 % → 0,51 % | 0,56 % → 1,05 % | 9,1 → 8,1 | 65 % | 0,115 % | 0,0 % |
| **C** | 0,22 % → 0,31 % | 0,33 % → 0,36 % | 1,66 % → 2,46 % | 6,2 → 5,3 | 79 % | 0,150 % | 0,0 % |

Solde technique débiteur : avec collecte (frais d'acquisition des contrats nouveaux au compte), sur les huit stratégies, les trois profils et deux configurations (collecte centrale, collecte forte et élasticité forte), la part maximale d'années à solde technique négatif est de 0,0 % et celle des comptes débiteurs reportés de 0,0 % ; le solde technique annuel le plus bas vaut 0,030 % de la PM. Le cas débiteur ne se présente donc pas dans les configurations publiées ; il est vérifié par des tests dédiés (report du solde, participation minimale nulle, TMG respecté, reprise obligatoire de PPB faite). Le taux servi n'est jamais inférieur au TMG moyen du portefeuille : le plus petit écart vaut 4,3 × 10⁻¹⁸ en valeur absolue (arrondi numérique), le plancher du TMG étant atteint certaines années.

Lecture : la convention de la V5.0 laissait la participation de l'exercice sous le compte réglementaire simplifié dans une part importante des années ; le complément va surtout à la PPB et au taux servi, et réduit d'autant le résultat de l'assureur. L'effet est nettement supérieur à l'incertitude Monte-Carlo de l'écart : c'est un effet de convention, pas du bruit.

### 2.4 Sensibilité au niveau des frais (paramètre fictif)

| Frais de gestion sur encours (profil B) | Écart de valeur, V5.1 - convention V5.0 | Écart de taux servi |
| --- | ---: | ---: |
| 0,40 % (centre) | −6,98 | +6,7 pb |
| 0,50 % | −3,67 | +3,3 pb |
| 0,60 % | −0,80 | +0,7 pb |

Plus les frais sont proches des chargements (0,63 %), plus le solde technique et donc l'effet de la correction sont petits. Le niveau central de 0,40 % n'est pas calibré : l'effet mesuré dépend de cette hypothèse, pas seulement de la règle.

### 2.5 Stratégies : effet de la correction à capital constant

Pour chaque stratégie, à son apport estimé de la V5.1 pour 100 % et avec les données de marché de la V5.1 : valeur nette sous les deux conventions (écart apparié sur les mêmes scénarios), puis écart à la gestion passive sous chaque convention.

| Profil, stratégie | Apport pour 100 % (V5.1) | Valeur nette, convention V5.0 | Valeur nette V5.1 | Effet de la correction | Relatif |
| --- | ---: | ---: | ---: | ---: | ---: |
| A, Passive | 101,0 | −3,2 | −5,4 | −2,18 ± 0,26 | −67,6 % |
| A, Réinvestissement progressif | 101,8 | −2,9 | −5,0 | −2,14 ± 0,25 | −74,6 % |
| A, Repositionnement | 118,8 | −16,1 | −21,7 | −5,65 ± 0,28 | −35,1 % |
| A, Taux servi compétitif | 88,4 | −10,0 | −11,3 | −1,31 ± 0,24 | −13,1 % |
| A, Taux servi de marge | 107,1 | 4,5 | 0,4 | −4,08 ± 0,48 | −90,3 % |
| A, Liquidité défensive | 114,5 | −2,1 | −4,6 | −2,50 ± 0,17 | −120,2 % |
| A, Compétitif préservant la PPB | 99,6 | −8,3 | −9,5 | −1,23 ± 0,15 | −14,8 % |
| A, Rétention de capital | 100,7 | −4,3 | −6,5 | −2,23 ± 0,25 | −52,4 % |
| B, Passive | 25,4 | 64,8 | 57,8 | −6,98 ± 0,37 | −10,8 % |
| B, Réinvestissement progressif | 25,2 | 64,9 | 58,1 | −6,87 ± 0,36 | −10,6 % |
| B, Repositionnement | 45,5 | 55,9 | 46,1 | −9,83 ± 0,34 | −17,6 % |
| B, Taux servi compétitif | 24,3 | 51,8 | 47,8 | −4,08 ± 0,29 | −7,9 % |
| B, Taux servi de marge | 21,8 | 74,8 | 64,1 | −10,70 ± 0,41 | −14,3 % |
| B, Liquidité défensive | 26,2 | 65,6 | 59,0 | −6,60 ± 0,28 | −10,1 % |
| B, Compétitif préservant la PPB | 25,2 | 52,1 | 48,3 | −3,79 ± 0,25 | −7,3 % |
| B, Rétention de capital | 25,8 | 63,4 | 56,4 | −6,96 ± 0,36 | −11,0 % |
| C, Passive | 0,0 | 93,4 | 82,8 | −10,63 ± 0,58 | −11,4 % |
| C, Réinvestissement progressif | 0,0 | 93,4 | 82,8 | −10,57 ± 0,53 | −11,3 % |
| C, Repositionnement | 1,1 | 92,1 | 81,6 | −10,54 ± 0,52 | −11,4 % |
| C, Taux servi compétitif | 0,0 | 79,2 | 73,0 | −6,24 ± 0,44 | −7,9 % |
| C, Taux servi de marge | 0,0 | 100,1 | 85,9 | −14,20 ± 0,56 | −14,2 % |
| C, Liquidité défensive | 0,0 | 96,3 | 85,9 | −10,42 ± 0,35 | −10,8 % |
| C, Compétitif préservant la PPB | 0,0 | 78,9 | 73,1 | −5,80 ± 0,42 | −7,3 % |
| C, Rétention de capital | 0,0 | 92,1 | 81,5 | −10,58 ± 0,59 | −11,5 % |

| Écart à la gestion passive (portefeuille fermé) | Convention V5.0 | V5.1 |
| --- | ---: | ---: |
| A, Réinvestissement progressif | +0,4 ± 0,1 | +0,4 ± 0,2 |
| A, Repositionnement | −12,9 ± 1,0 | −16,3 ± 1,1 |
| A, Taux servi compétitif | −6,8 ± 0,4 | −5,9 ± 0,4 |
| A, Taux servi de marge | +7,7 ± 0,4 | +5,8 ± 0,4 |
| A, Liquidité défensive | +1,1 ± 1,1 | +0,8 ± 1,2 |
| A, Compétitif préservant la PPB | −5,1 ± 0,4 | −4,1 ± 0,4 |
| A, Rétention de capital | −1,0 ± 0,1 | −1,1 ± 0,1 |
| B, Réinvestissement progressif | +0,2 ± 0,2 | +0,3 ± 0,3 |
| B, Repositionnement | −8,9 ± 0,7 | −11,8 ± 0,7 |
| B, Taux servi compétitif | −13,0 ± 0,5 | −10,1 ± 0,5 |
| B, Taux servi de marge | +10,0 ± 0,6 | +6,2 ± 0,6 |
| B, Liquidité défensive | +0,8 ± 1,2 | +1,2 ± 1,4 |
| B, Compétitif préservant la PPB | −12,7 ± 0,5 | −9,5 ± 0,5 |
| B, Rétention de capital | −1,4 ± 0,1 | −1,4 ± 0,1 |
| C, Réinvestissement progressif | 0,0 ± 0,5 | 0,0 ± 0,5 |
| C, Repositionnement | −1,3 ± 0,5 | −1,2 ± 0,5 |
| C, Taux servi compétitif | −14,2 ± 0,6 | −9,8 ± 0,7 |
| C, Taux servi de marge | +6,7 ± 0,8 | +3,1 ± 0,7 |
| C, Liquidité défensive | +2,9 ± 1,4 | +3,1 ± 1,5 |
| C, Compétitif préservant la PPB | −14,5 ± 0,6 | −9,7 ± 0,7 |
| C, Rétention de capital | −1,4 ± 0,1 | −1,3 ± 0,1 |

Signe de l'écart à la gestion passive : 1 changement de signe sur 21 couples profil-stratégie du fait de la seule correction.

## 3. Données de marché

### 3.1 Courbe sans risque EIOPA (observée)

La courbe sans risque de l'EIOPA au 31/10/2026 (zéro-coupon, dérivée des swaps, ajustement pour risque de crédit déduit, extrapolée vers l'UFR) actualise les engagements ; la correction pour volatilité (VA) ne s'y ajoute que dans la vue prudentielle. Elle est reprise telle que publiée (archive contrôlée par son empreinte SHA-256). Les publications de l'EIOPA sont réutilisables avec mention de la source ; pour un contenu adapté, l'EIOPA demande en outre un avertissement, reproduit dans `data/v5/README.md` et dans la fiche du spread.

### 3.2 Spread des obligations détenues (hypothèse)

- **Point de départ.** La V5.0 calait le spread des obligations sur les TEC du 04/11/2026, indices de taux de l'État calculés et administrés par Euronext Paris, et une courbe zéro-coupon qui en était dérivée. Leur redistribution est soumise à une autorisation écrite préalable. Une transformation (conversion en zéro-coupon, écart à une autre courbe) ne lève pas cette condition : la V5.1 retire du dépôt les valeurs d'indice, les courbes dérivées et les figures qui permettaient de les reconstituer.
- **Sources examinées.** Les courbes de rendement de la zone euro publiées par la BCE (et reprises par Eurostat) sont estimées à partir de prix fournis par un tiers (EuroMTS) ; la politique de réutilisation des statistiques du SEBC exclut les données de tiers sans autorisation et n'autorise pas de modification : elles ne sont pas retenues. L'EIOPA publie, dans la même archive mensuelle que la courbe sans risque, les moyennes de long terme des spreads (LTAS) par notation, réutilisables avec mention de la source : elles servent d'ancrage.
- **Construction.** Les obligations du modèle représentent l'ensemble du portefeuille obligataire des assureurs (souverains et entreprises). Leur spread est une hypothèse de spread « normal », hors période de tension : la moyenne de long terme publiée par l'EIOPA pour la notation la plus représentée du portefeuille des assureurs français (A+ à A- : 61 % au T4 2025, ACPR, Analyses et synthèses n° 181). Aucune donnée d'indice de taux souverain n'est utilisée. Règle : LTAS = moyenne simple des séries EUR_Financials_2 et EUR_Non-Financials_2 (échelon de qualité de crédit 2, notation A) ; s(k) = ln(1 + r_EIOPA(k) + LTAS(k)) - ln(1 + r_EIOPA(k)), k = 1 à 30 ans ; plat au-delà de 30 ans.
- **Statut.** Les LTAS sont des paramètres publiés (observés) ; leur emploi comme spread courant, le choix de la notation et la moyenne des séries financières et non financières sont des hypothèses. Ce n'est pas un spread de marché observé au 31/10/2026 : en période de tension sur les spreads, le spread de marché serait plus élevé.

| Maturité | 1 an | 2 ans | 5 ans | 10 ans | 15 ans | 20 ans | 30 ans |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LTAS, obligations financières notées A (EIOPA) | 1,11 % | 1,11 % | 1,39 % | 1,57 % | 1,58 % | 1,58 % | 1,58 % |
| LTAS, obligations non financières notées A (EIOPA) | 0,56 % | 0,56 % | 0,80 % | 1,05 % | 1,08 % | 1,08 % | 1,08 % |
| Spread hypothétique du modèle (continu) | 81 pb | 81 pb | 105 pb | 126 pb | 128 pb | 128 pb | 128 pb |

- **Usage dans le moteur.** Le spread sert à trois choses : (1) le prix de marché à l'ouverture des obligations détenues, qui représentent tout le portefeuille obligataire, souverains et entreprises (simplification) ; (2) en risque neutre, une intensité de perte qui rend tout le spread coûteux (absence d'arbitrage) : une part kappa = 0,7 passe par des défauts de blocs d'émetteurs, le reste est une perte lissée ; (3) en probabilité réelle, seule une perte de défaut historique est constatée, l'écart étant une prime de risque. Le choc de spread de la vue prudentielle porte sur la part non souveraine. La part kappa est une hypothèse, testée de 0,55 à 1 ; ce n'est pas une estimation du risque de défaut des émetteurs, souverains ou entreprises : kappa répartit seulement le spread hypothétique entre une perte par défaut et une perte hors défaut.
- **Autres paramètres liés.** Le niveau initial de la référence des assurés (2,85 %) est une hypothèse, au milieu de la fourchette des taux servis attendus pour 2026 (2,8 % à 2,9 %, estimations de place) ; les coupons des générations d'obligations des profils fictifs sont des hypothèses d'ordre de grandeur, sans valeur d'indice reproduite.

Valeur économique simplifiée = valeur de marché des actifs - BE ; fonds propres prudentiels simplifiés = actifs - BE - marge de risque + fonds excédentaires - impôts différés passifs (le SCR est une exigence de capital, pas un passif). Leur réaction à une variation des taux dépend des sensibilités respectives des obligations et des engagements, ces dernières dépendant elles-mêmes de la participation, des garanties et des rachats : ce point est mesuré par la vue prudentielle (chocs de taux), pas par le niveau des courbes.

### 3.3 PPB et fonds excédentaires dans la vue prudentielle

Toute la PPB est dans le BE (reprises créditées puis prestations, stock final, extinction). La PPB d'ouverture est en outre admise en fonds excédentaires (FE) de niveau 1, valorisée par la méthode simplifiée de la fiche technique de l'ACPR (intégration aux PM au bout de huit ans, sortie au rythme des prestations de la projection centrale, actualisation sur la courbe EIOPA). Fonds propres de niveau 1 = actif − BE − marge de risque + FE − impôts différés passifs, ce qui équivaut à retirer FE du BE : le BE brut du moteur et le BE après reclassement sont donnés ci-dessous. La capacité d'absorption des provisions techniques est bornée par FDB − FE et le MCR utilise FDB − FE : la même PPB n'est pas comptée à la fois en fonds propres et en absorption ; le SCR brut ne dépend pas de FE (`docs/V5_METHODOLOGIE.md`, section 7).

**Réconciliation avec la fiche ACPR.** La fiche retire du montant admissible (1) la génération qui atteint huit ans l'exercice suivant, (2) les montants déjà affectés et (3) l'enveloppe de l'article A.132-3. Le modèle admet la PPB d'ouverture entière. Sous l'hypothèse de générations uniformes, l'exclusion (1) vaut un huitième du stock ; les exclusions (2) et (3) sont supposées nulles, car le modèle n'a ni participation affectée non créditée ni enveloppe A.132-3 : c'est une hypothèse, pas un fait vérifié. Les indicateurs ci-dessous sont re-agrégés sans scénario à partir des résultats stockés (même formule que le moteur ; contrôle : avec FE inchangé, la re-agrégation reproduit exactement les valeurs publiées). Gestion passive, sans apport, V5.1 :

| Profil | PPB comptable | Exclusion (1) : génération à échéance | PPB admissible | FE publiés (PPB entière) | FE corrigés | Taux de valorisation | BE brut (moteur) | BE après reclassement, publié | BE après reclassement, corrigé |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | 25,0 | 3,1 | 21,9 | 14,7 | 12,8 | 59 % | 885,4 | 870,8 | 872,6 |
| **B** | 40,0 | 5,0 | 35,0 | 17,0 | 14,9 | 43 % | 907,2 | 890,2 | 892,3 |
| **C** | 20,0 | 2,5 | 17,5 | 8,4 | 7,4 | 42 % | 924,9 | 916,5 | 917,5 |

| Profil | Fonds propres de niveau 1, publiés | corrigés | SCR simplifié, publié | corrigé | FE / fonds propres publiés | Couverture publiée | Couverture corrigée | Apport pour 100 %, publié | corrigé | Intervalle de rééchantillonnage publié (95 %) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | 15,8 | 13,9 | 121,3 | 119,4 | 93 % | 13,0 % | 11,7 % | 101,0 | 101,0 | 99,4 à 102,8 |
| **B** | 69,6 | 67,5 | 94,5 | 94,5 | 24 % | 73,7 % | 71,4 % | 25,4 | 27,6 | 23,9 à 30,4 |
| **C** | 87,5 | 86,4 | 83,9 | 83,9 | 10 % | 104,3 % | 103,0 % | 0,0 | 0,0 | 0,0 à 0,0 |

Lecture. Pour A, la capacité d'absorption est bornée par FDB − FE : la déduction réduit d'autant les fonds propres et le SCR, et l'apport visant 100 % est inchangé (101,0 contre 101,0). Pour B, le SCR ne bouge pas et l'apport visant 100 % passe de 25,4 à 27,6, à l'intérieur de l'intervalle de rééchantillonnage publié. Pour C, la couverture corrigée reste supérieure à 100 % (103,0 %) : C couvre son SCR simplifié sans apport avec ou sans cette déduction. Les résultats publiés gardent la convention du modèle (PPB d'ouverture admise en totalité) ; l'écart ci-dessus en mesure l'effet. Approximation à garder en tête : exclusions (2) et (3) supposées nulles, montant de FE figé dans tous les chocs.

## 4. Avant et après : V5.0 publiée et V5.1

Chaque version avec son propre capital et ses propres données de marché. La colonne « dont participation » reprend l'effet de la correction mesuré à capital et marché identiques (section 2.3) ; le reste de l'écart vient des données de marché et du recalibrage du capital.

| Gestion passive | V5.0 | V5.1 | Écart absolu | Écart relatif | dont participation |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** indicateur de couverture sans apport | 1,9 % | 13,0 % | +11,1 pt |  |  |
| A : SCR simplifié sans apport | 118,6 | 121,3 | +2,7 | +2,3 % |  |
| A : fonds propres simplifiés sans apport | 2,2 | 15,8 | +13,6 | +610,4 % |  |
| A : apport estimé pour 100 % | 110,4 | 101,0 | −9,3 | −8,5 % |  |
| A : apport estimé pour 150 % | 159,5 | 150,5 | −9,0 | −5,7 % |  |
| A : BE à 100 % | 902,7 | 901,8 | −0,9 | −0,1 % | +2,8 |
| A : taux servi moyen, années 1 à 10 (risque neutre) | 1,41 % | 1,44 % | +3 pb |  | +4 pb |
| A : valeur de l'existant avant recapitalisation | −10,8 | 4,5 | +15,3 | +141,5 % |  |
| A : valeur de l'existant recapitalisé à 100 % | −21,5 | −5,4 | +16,1 | +74,9 % | −2,2 |
| A : valeur des affaires nouvelles (c0 = 6 %, eta = 0,5) | 7,0 | 6,2 | −0,8 | −11,4 % |  |
| A : marge des affaires nouvelles | 3,0 % | 2,8 % | −0,3 pt |  |  |
| A : seuil de coût du capital des affaires nouvelles | 2,3 % | 2,0 % | −0,32 pt |  |  |
| **B** indicateur de couverture sans apport | 71,7 % | 73,7 % | +2,0 pt |  |  |
| B : SCR simplifié sans apport | 101,4 | 94,5 | −6,9 | −6,8 % |  |
| B : fonds propres simplifiés sans apport | 72,7 | 69,6 | −3,1 | −4,3 % |  |
| B : apport estimé pour 100 % | 29,5 | 25,4 | −4,1 | −13,8 % |  |
| B : apport estimé pour 150 % | 81,2 | 73,3 | −7,9 | −9,7 % |  |
| B : BE à 100 % | 914,8 | 919,8 | +4,9 | +0,5 % | +8,9 |
| B : taux servi moyen, années 1 à 10 (risque neutre) | 1,88 % | 2,00 % | +12 pb |  | +7 pb |
| B : valeur de l'existant avant recapitalisation | 56,2 | 61,4 | +5,2 | +9,3 % |  |
| B : valeur de l'existant recapitalisé à 100 % | 52,3 | 57,8 | +5,5 | +10,4 % | −7,0 |
| B : valeur des affaires nouvelles (c0 = 6 %, eta = 0,5) | 8,4 | 8,7 | +0,2 | +2,9 % |  |
| B : marge des affaires nouvelles | 2,7 % | 2,7 % | 0,0 pt |  |  |
| B : seuil de coût du capital des affaires nouvelles | 2,0 % | 2,1 % | +0,07 pt |  |  |
| **C** indicateur de couverture sans apport | 83,1 % | 104,3 % | +21,1 pt |  |  |
| C : SCR simplifié sans apport | 98,4 | 83,9 | −14,5 | −14,8 % |  |
| C : fonds propres simplifiés sans apport | 81,8 | 87,5 | +5,6 | +6,9 % |  |
| C : apport estimé pour 100 % | 17,1 | 0,0 | −17,1 | −100,0 % |  |
| C : apport estimé pour 150 % | 68,3 | 41,3 | −27,1 | −39,6 % |  |
| C : BE à 100 % | 922,0 | 934,8 | +12,8 | +1,4 % | +13,8 |
| C : taux servi moyen, années 1 à 10 (risque neutre) | 1,98 % | 2,16 % | +18 pb |  | +9 pb |
| C : valeur de l'existant avant recapitalisation | 77,0 | 82,8 | +5,8 | +7,6 % |  |
| C : valeur de l'existant recapitalisé à 100 % | 74,7 | 82,8 | +8,1 | +10,8 % | −10,6 |
| C : valeur des affaires nouvelles (c0 = 6 %, eta = 0,5) | 9,9 | 10,7 | +0,8 | +8,3 % |  |
| C : marge des affaires nouvelles | 2,8 % | 2,9 % | +0,1 pt |  |  |
| C : seuil de coût du capital des affaires nouvelles | 2,1 % | 2,5 % | +0,40 pt |  |  |

Lecture du besoin de capital (gestion passive, sans apport) : variations de la V5.0 à la V5.1 des FDB (A +9,3, B +22,7, C +34,5), de l'ajustement pour la capacité d'absorption des pertes des provisions techniques (A −9,7, B −16,4, C −17,6), du BSCR (A +12,4, B +9,5, C +5,1), des fonds propres (A +13,6, B −3,1, C +5,6) et du SCR (A +2,7, B −6,9, C −14,5). L'apport estimé pour 100 % résulte de ces deux derniers mouvements.

Valeur des affaires nouvelles sur toute la grille de collecte (gestion passive, trois profils) : de 0,3 à 31,9 en V5.0, de 0,3 à 34,1 en V5.1. Avec la composante technique, les frais d'acquisition des contrats nouveaux entrent au compte de participation : quand le complément joue, les assurés en supportent une partie.

### 4.1 Lectures de valeur totale (collecte et rachat)

Capital porté à 100 % pour chaque stratégie et chaque version ; lecture de l'écart de valeur totale à la gestion passive sur les 20 configurations de collecte et de rachat (critères fixés à l'avance, `strategies.json`).

| Profil, stratégie | Capital supplémentaire à l'ouverture, V5.0 / V5.1 | Valeur totale V5.0 (plage) | Valeur totale V5.1 (plage) | Lecture V5.0 | Lecture V5.1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A, Réinvestissement progressif | +0,2 / +0,7 | 0,1 à 1,2 | 0,1 à 1,0 | sans effet important | sans effet important |
| A, Repositionnement | +19,0 / +17,8 | −17,8 à −3,9 | −20,9 à −7,3 | défavorable, robuste | défavorable, robuste |
| A, Taux servi compétitif | −10,5 / −12,6 | −17,5 à −1,5 | −15,0 à −0,9 | toujours négatif, non robuste | toujours négatif, non robuste |
| A, Taux servi de marge | +8,3 / +6,1 | 3,6 à 15,0 | 2,7 à 9,8 | toujours positif, non robuste | toujours positif, non robuste |
| A, Liquidité défensive | +18,0 / +13,5 | −7,0 à 3,7 | −6,9 à 3,5 | change de signe selon les hypothèses | change de signe selon les hypothèses |
| A, Compétitif préservant la PPB | −1,6 / −1,4 | −19,1 à −0,6 | −17,0 à −0,6 | toujours négatif, non robuste | toujours négatif, non robuste |
| A, Rétention de capital | −0,8 / −0,4 | −2,1 à −0,6 | −2,1 à −0,6 | sans effet important | sans effet important |
| B, Réinvestissement progressif | −0,2 / −0,2 | 0,1 à 0,5 | 0,2 à 0,8 | sans effet important | sans effet important |
| B, Repositionnement | +24,9 / +20,1 | −14,8 à −4,9 | −15,4 à −7,8 | défavorable, robuste | défavorable, robuste |
| B, Taux servi compétitif | −2,3 / −1,1 | −26,8 à −4,3 | −24,1 à −2,6 | toujours négatif, non robuste | toujours négatif, non robuste |
| B, Taux servi de marge | −2,3 / −3,6 | 2,2 à 13,1 | 0,2 à 8,5 | toujours positif, non robuste | toujours positif, non robuste |
| B, Liquidité défensive | −0,2 / +0,8 | −0,1 à 3,1 | 0,4 à 3,1 | positif là où il est significatif, non robuste | toujours positif, non robuste **(changé)** |
| B, Compétitif préservant la PPB | −0,7 / −0,2 | −28,1 à −5,2 | −24,7 à −3,3 | défavorable, robuste | toujours négatif, non robuste **(changé)** |
| B, Rétention de capital | +0,6 / +0,4 | −2,7 à −1,1 | −2,3 à −1,0 | toujours négatif, non robuste | toujours négatif, non robuste |
| C, Réinvestissement progressif | +0,1 / 0,0 | 0,1 à 0,3 | 0,0 à 0,6 | sans effet important | toujours positif, non robuste **(changé)** |
| C, Repositionnement | +5,8 / +1,1 | −3,1 à −1,2 | −2,6 à −1,2 | toujours négatif, non robuste | toujours négatif, non robuste |
| C, Taux servi compétitif | −1,6 / 0,0 | −27,0 à −5,0 | −23,4 à −2,1 | défavorable, robuste | toujours négatif, non robuste **(changé)** |
| C, Taux servi de marge | −4,8 / 0,0 | 1,5 à 11,1 | −3,0 à 4,6 | toujours positif, non robuste | change de signe selon les hypothèses **(changé)** |
| C, Liquidité défensive | +1,7 / 0,0 | 2,9 à 4,1 | 3,1 à 5,1 | toujours positif, non robuste | toujours positif, non robuste |
| C, Compétitif préservant la PPB | +0,2 / 0,0 | −28,4 à −5,9 | −23,9 à −2,4 | défavorable, robuste | toujours négatif, non robuste **(changé)** |
| C, Rétention de capital | +0,4 / 0,0 | −2,7 à −1,3 | −2,2 à −1,0 | toujours négatif, non robuste | toujours négatif, non robuste |

Lectures modifiées : B, liquidité défensive : « positif là où il est significatif, non robuste » devient « toujours positif, non robuste » ; B, compétitif préservant la PPB : « défavorable, robuste » devient « toujours négatif, non robuste » ; C, réinvestissement progressif : « sans effet important » devient « toujours positif, non robuste » ; C, taux servi compétitif : « défavorable, robuste » devient « toujours négatif, non robuste » ; C, taux servi de marge : « toujours positif, non robuste » devient « change de signe selon les hypothèses » ; C, compétitif préservant la PPB : « défavorable, robuste » devient « toujours négatif, non robuste ».

Signe de l'écart moyen sur le portefeuille fermé, de la V5.0 à la V5.1 : aucun changement de signe sur 21 couples profil-stratégie.

## 5. Impôt sur les sociétés dans la projection

### 5.1 Fonctions et identités

| Fonction | Rôle | Constat |
| --- | --- | --- |
| `projection.projeter` | résultat avant impôt, fonds propres comptables, distribution | le résultat avant impôt alimente les fonds propres ; la distribution porte sur l'excédent avant impôt |
| `fiscalite.impot_annuel` | 25 %, contribution sociale, déficits reportables (art. 209) | règles vérifiées par les tests de la V5 |
| `strategies.impots_par_scenario`, `resume_risque_neutre`, `collecte.projection_risque_neutre` | impôt après coup, VA déduite de la valeur | déduit une seule fois ; le BE ne contient pas d'impôt |
| `strategies.resume_reel` | rentabilité après impôt en probabilité réelle | résultat net = résultat avant impôt - impôt, rapporté aux fonds propres d'ouverture avant impôt |
| `solvabilite_v5` | impôts différés à l'ouverture | indépendants de la convention de calendrier (bilan d'ouverture) |

Convention de référence (inchangée en V5.1) : valeur nette = VA des dividendes avant impôt + VA du résidu final - apport initial - VA des apports ultérieurs - VA de l'impôt + fuite. Aucun impôt n'est compté deux fois : il est soustrait une fois de la valeur et n'apparaît ni dans le BE ni dans les flux de la projection. La limite est de présentation : les fonds propres et les dividendes de la projection sont avant impôt, et l'impôt ne réduit pas l'actif investi.

Variante « impôt projeté » (`src/v5/variantes_audit.py`) : l'impôt de l'exercice est calculé dans la boucle (mêmes règles, déficits compris), déduit des fonds propres avant la distribution et payé par l'actif en fin d'exercice, à la date des prestations, donc avec le même déflateur que le calcul après coup ; la valeur déduit l'impôt payé, une fois. Tests (`tests/test_v5_audit_conventions.py`) : bilan équilibré chaque année et fuite nulle sur l'équivalent certain, impôt payé égal au calcul après coup sur les mêmes résultats, fonds propres(t) = fonds propres(t - 1) + résultat - impôt + apport - dividende déclaré, déficits reportables, sortie de trésorerie, identité de décomposition de la valeur.

### 5.2 Effets (V5.1, gestion passive, apports de la V5.1, mêmes scénarios)

| Profil | Écart de valeur nette | Relatif | BE | Taux servi | VA des dividendes | Rentabilité des fonds propres (réel) | Indicateur à l'apport de la V5.1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | +0,15 ± 0,01 | +2,9 % | −0,04 | −0,1 pb | 112,7 → 100,9 | 4,42 % → 4,38 % | 102,2 % → 102,2 % |
| **B** | +0,28 ± 0,01 | +0,5 % | −0,05 | −0,1 pb | 107,1 → 87,4 | 8,68 % → 8,60 % | 99,9 % → 100,0 % |
| **C** | +0,27 ± 0,02 | +0,3 % | −0,02 | 0,0 pb | 110,5 → 87,8 | 11,89 % → 11,77 % | 104,3 % → 104,3 % |

Stratégies (portefeuille fermé, 100 %) : l'écart à la gestion passive change au plus de 0,27 unité avec l'impôt projeté ; aucun changement de signe sur 21. Les dividendes de la variante sont après impôt, d'où leur baisse ; la valeur bouge peu, car le total des sorties (impôt et dividendes) est presque le même et que l'actif investi ne baisse que de l'impôt payé un an plus tôt.

Décision : la convention après coup est conservée. Elle ne crée ni double comptage ni omission dans la valeur, et la variante n'en change aucune conclusion. Les documents précisent que les dividendes et fonds propres projetés sont avant impôt.

## 6. Précision des apports visant 100 %

Le besoin est interpolé linéairement entre deux calculs de la vue prudentielle (sans apport et avec un apport proche du besoin à 125 %), puis vérifié par un recalcul direct au besoin obtenu. Écart d'apport estimé : (1 - indicateur) x SCR / (pente des fonds propres - pente du SCR) ; effet sur la valeur : cet écart multiplié par le coût de la recapitalisation par unité d'apport du profil (passive).

| Profil, stratégie, cible | Apport V5.1 | Indicateur recalculé V5.0 | Indicateur recalculé V5.1 | Écart d'apport estimé | Effet sur la valeur |
| --- | ---: | ---: | ---: | ---: | ---: |
| A, Passive, 100 % | 101,0 | 101,6 % | 102,2 % | −2,30 | +0,23 |
| A, Passive, 150 % | 150,5 | 149,5 % | 149,2 % | +0,78 | −0,08 |
| B, Passive, 100 % | 25,4 | 99,9 % | 99,9 % | +0,07 | −0,01 |
| B, Passive, 150 % | 73,3 | 149,4 % | 150,5 % | −0,50 | +0,07 |
| C, Passive, 100 % | 0,0 | 99,9 % | 104,3 % | sans objet | sans objet |
| C, Passive, 150 % | 41,3 | 150,0 % | 150,3 % | −0,24 | 0,00 |
| A, Taux servi de marge, 100 % | 107,1 | 100,7 % | 101,7 % | −1,95 | +0,19 |
| B, Taux servi de marge, 100 % | 21,8 | 99,8 % | 99,7 % | +0,25 | −0,03 |
| C, Taux servi de marge, 100 % | 0,0 | 99,9 % | 111,9 % | sans objet | sans objet |
| A, Réinvestissement progressif, 100 % | 101,8 | 101,4 % | 102,5 % | −2,61 | +0,26 |
| A, Repositionnement, 100 % | 118,8 | 99,5 % | 99,1 % | +1,04 | −0,10 |
| A, Taux servi compétitif, 100 % | 88,4 | 101,8 % | 102,6 % | −2,24 | +0,22 |
| A, Liquidité défensive, 100 % | 114,5 | 100,8 % | 101,6 % | −1,96 | +0,19 |
| A, Compétitif préservant la PPB, 100 % | 99,6 | 101,4 % | 102,0 % | −1,86 | +0,18 |
| A, Rétention de capital, 100 % | 100,7 | 102,0 % | 102,7 % | −2,70 | +0,26 |

Sans apport, l'indicateur dépasse déjà la cible pour C, passive (104,3 %), C, taux servi de marge (111,9 %) : l'apport estimé est nul et l'écart est sans objet.

Coût de la recapitalisation par unité d'apport (V5.1, passive) : A −0,098, B −0,141. L'effet sur la valeur ne dépasse pas 0,26 unité, bien en deçà du seuil d'importance (2 % du SCR, soit 2,4, 1,9, 1,7). Une recherche de racine coûterait plusieurs recalculs de la vue prudentielle par stratégie : la méthode est conservée et les apports sont présentés comme des **estimations visant 100 %**, pas comme des montants réglementaires exacts.

## 7. Nature des principales conclusions

A : identité mathématique ou comptable vérifiée ; B : résultat de simulation correct sous les hypothèses du modèle ; C : conclusion économique robuste dans les configurations testées ; D : hypothèse fictive, approximation ou résultat non calibré.

| Conclusion | Nature | V5.1 |
| --- | --- | --- |
| Bilan équilibré chaque année, fuite nulle sur l'équivalent certain, absence d'arbitrage, impôt compté une fois | A | vérifié par les tests |
| Participation de l'exercice au moins égale au compte simplifié (V5.1) | A | vérifié par les tests |
| Le bilan hérité conditionne le capital nécessaire et la valeur (valeur de A recapitalisé négative) | B | A −5,4, B 57,8, C 82,8 |
| Désavantages robustes (lecture de valeur totale) | C | A, repositionnement ; B, repositionnement |
| Aucune stratégie n'a d'avantage robuste | C | confirmé |
| Politique de marge : lecture sur la grille | C et D | lecture : A « toujours positif, non robuste », B « toujours positif, non robuste », C « change de signe selon les hypothèses » |
| Niveaux de valeur, de capital et de valeur des affaires nouvelles | B et D | dépendent des profils fictifs, du spread hypothétique, des frais fictifs et de l'élasticité |
| Indicateurs de couverture du SCR | D | simplifiés, pas des ratios réglementaires |
| Élasticité de la collecte, loi de rachat, référence des assurés | D | non calibrées ; grille et sensibilités |
| Spread des obligations | D | hypothèse : moyenne de long terme publiée par l'EIOPA (notation A), pas un spread de marché observé |

## 8. Ce qui reste simplifié

- Compte de participation : un seul canton, pas de résultat de mortalité ni de réassurance, solde financier négatif non reporté, pas de complément contrat par contrat ; frais de gestion fictifs, dont dépend l'ampleur de la composante technique.
- Spread des obligations : hypothèse de spread de long terme, identique pour toutes les obligations (souverains et entreprises), figé, sans dynamique propre ni migration de notation ; part de crédit kappa supposée.
- Impôt après coup : dividendes et fonds propres de la projection avant impôt (variante disponible, effet mesuré).
- Apports estimés par interpolation : indicateur recalculé entre 99,1 % et 102,7 % pour une cible de 100 %.
- Incertitude Monte-Carlo : intervalles par cellule, non simultanés ; incertitude de convention mesurée par les écarts de ce document, pas par ces intervalles.

