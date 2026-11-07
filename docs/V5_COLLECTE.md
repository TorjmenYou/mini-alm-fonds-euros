# V5 : collecte nouvelle et stratégies ALM

Généré par `scripts/v5_rapport_collecte.py` depuis `resultats/v5_collecte.json` (`scripts/v5_collecte.py`), `resultats/v5_consolidation.json` et `resultats/v5_reconciliation_collecte.json` (`scripts/v5_reconciliation_collecte.py`). Spécification : `docs/V5_SPECIFICATION_COLLECTE.md`. Risque neutre : 1 000 scénarios, base sans VA, mêmes scénarios et mêmes tirages de défaut pour toutes les stratégies, intensités et élasticités. Unités fictives : 1 unité = 10 M€. **Profils fictifs, première version volontairement simple du modèle de collecte : analyse exploratoire, conditionnelle aux hypothèses, ce n'est pas une recommandation.**

**Base de capital commune.** Chaque stratégie garde l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (`docs/V5_STRATEGIES.md`, section 2). Cet apport est calculé sur l'existant en extinction, dans la frontière des contrats : la collecte ne le modifie pas (test `test_vue_prudentielle_dans_la_frontiere_des_contrats`). C'est une convention simplifiée : la vue prudentielle exclut les primes et les contrats futurs, mais aussi les effets que la collecte peut avoir sur les hypothèses de projection de l'existant (politique d'investissement, produits financiers, frais), que ce document analyse séparément dans la vue économique ; un calcul Solvabilité II complet peut devoir en tenir compte.

**Trois valeurs, toujours séparées** (risque neutre, nettes de l'apport, des apports ultérieurs et de l'impôt) :

- *valeur de l'existant* : portefeuille en extinction (c0 = 0), c'est la valeur nette des documents précédents ;
- *valeur des affaires nouvelles* (valeur de franchise, hors Solvabilité II) = valeur totale - valeur de l'existant, sur les mêmes scénarios ;
- *valeur totale* pour l'actionnaire, avec collecte.

La valeur des affaires nouvelles se répartit, scénario par scénario, entre trois termes : les **flux des contrats nouveaux** (VA des primes - BE des contrats nouveaux, c'est-à-dire ce que ces contrats reçoivent dans le fonds mutualisé), la **variation du BE de l'existant**, comptée pour l'actionnaire, et l'**impôt supplémentaire**. Seule la somme s'interprète comme une valeur : un transfert entre générations d'assurés (PPB d'ouverture, coupons anciens, garanties) déplace les deux premiers termes en sens inverse, sans changer la somme (section 6).

**Lecture des écarts** à la gestion passive (mêmes scénarios, intervalle apparié à 95 %) : « ns » non significatif ; « +, non important » ou « −, non important » significatif mais sous le seuil d'importance (2 % du SCR simplifié du profil : 2,4 pour A, 2,0 pour B, 2,0 pour C) ; **+** ou **−** au-delà du seuil, « borne sous le seuil » si la borne de l'intervalle ne le dépasse pas. « Robuste » : borne de l'intervalle au-delà du seuil dans toutes les configurations (trois intensités, cinq élasticités, et la loi de rachat ONC maximale à l'intensité centrale).

## 1. Hypothèses de collecte et contrôles

| Paramètre | Valeur | Statut |
| --- | --- | --- |
| Intensité faible c0 | 3 % de la PM par an | fictif : collecte nette d'environ -2,4 % de la PM par an avec g = 1 (sorties du modèle d'environ 5,4 %) |
| Intensité centrale c0 | 6 % de la PM par an | dérivé d'agrégats observés (une seule année) : collecte nette 2025 des supports en euros (+8,1 Md€, France Assureurs) rapportée à l'encours de début d'année (1 178 Md€, ACPR), soit environ +0,7 %, ajoutée aux sorties du modèle (décès 1 % et rachat structurel 4,33 % des survivants, soit environ 5,3 % de la PM revalorisée et 5,4 % de la PM de début d'année) : environ 6 %. Avec g = 1, le modèle redonne ainsi la collecte nette de la place (environ +0,6 % de la PM la première année, contre +0,7 % observés), pas ses flux bruts (environ 9,9 % de primes et 9,2 % de sorties) ni la croissance de la PM, qui comprend aussi les intérêts crédités, les prélèvements sociaux et d'autres mouvements (réconciliation : scripts/v5_reconciliation_collecte.py, docs/V5_COLLECTE.md, section 1) |
| Intensité forte c0 | 10 % de la PM par an | dérivé d'agrégats observés, borne haute (flux bruts) : collecte brute 2025 des supports en euros (116,9 Md€, France Assureurs) rapportée à l'encours de début d'année (1 178 Md€, ACPR) : environ 10 % ; périmètres non strictement identiques. Les sorties de la place (environ 9 % de l'encours) dépassent celles du modèle (environ 5,3 %) : avec g = 1, c0 = 10 % donne une collecte nette d'environ +4,6 % de la PM par an, bien au-delà des +0,7 % observés |
| Élasticité nulle eta | 0,0 par point de taux servi relatif | fictif |
| Élasticité modérée eta | 0,5 par point de taux servi relatif | fictif |
| Élasticité intermédiaire eta | 0,75 par point de taux servi relatif | fictif |
| Élasticité soutenue eta | 1,0 par point de taux servi relatif | fictif |
| Élasticité forte eta | 1,5 par point de taux servi relatif | fictif |
| Horizon de collecte | 10 ans, puis extinction ; sensibilités à 30 et 60 ans | fictif |
| Réaction g(e) | g = min(2 ; max(0 ; 1 + eta x (e - e0) / 1 point)), e = taux servi sur les contrats nouveaux - référence | fictif |
| e0 | 0,0 % ; sensibilité -0,5 point | fictif : un assureur qui sert le taux du marché collecte c0 x PM ; la référence des assurés vaut 2,88 % en t = 0 (hypothèse : taux servis attendus pour 2026), le taux servi moyen observé de 2025 est de 2,63 % (ACPR n° 180) ; c0 est dérivé des flux d'un marché qui sert, par définition, le taux du marché, d'où e0 = 0 au centre ; sensibilité e0 = -0,5 point |
| Contrats nouveaux | TMG 0,0 %, chargement sur prime 0,0 %, frais d'acquisition 1,0 % de la prime ; chargements et frais sur encours, loi de rachat et mortalité de l'existant | fictif |

Sources des agrégats observés : Cercle de l'Épargne, communiqué du 27/01/2026 citant France Assureurs : cotisations 2025 de 192,1 Md€, dont 116,9 Md€ sur les supports en euros ; collecte nette des supports en euros de +8,1 Md€ (https://cercledelepargne.com/wp-content/uploads/2026/01/Communique-de-presse-de-Philippe-Crevel-directeur-du-Cercle-de-lEpargne-resultats-Assurance-vie-2025.pdf, source secondaire) ; ACPR, Analyses et synthèses n° 180, revalorisation 2025, 30/06/2026 : encours des contrats en euros de 1 178 Md€ fin 2024 et 1 207 Md€ fin 2025 ; taux de revalorisation moyen 2025 de 2,63 % (https://acpr.banque-france.fr/system/files/2026-06/20260630_AS180_revalorisation_2025.pdf). Ces agrégats portent sur une seule année.

### Réconciliation avec les flux de la place en 2025

En % de la PM de début d'année. Place : encours des contrats individuels en euros (ACPR), flux des supports en euros (France Assureurs), périmètres non strictement identiques ; observé, sauf les intérêts crédités (taux moyen appliqué à la moyenne des PM de début et de fin, approximation), les prélèvements sociaux (17,2 % des intérêts, prélevés chaque année) et les autres mouvements (résidu de l'identité). Modèle : gestion passive, intensité centrale c0 = 6 %, eta = 0 (donc g = 1), probabilité réelle, 1 000 scénarios ; année 1 et moyenne des années 1 à 10. Calcul : `scripts/v5_reconciliation_collecte.py`, `resultats/v5_reconciliation_collecte.json`.

| Poste | Place 2025, Md€ | Place 2025, % PM | Modèle, année 1 (A / B / C) | Modèle, moyenne 1-10 (A / B / C) |
| --- | ---: | ---: | ---: | ---: |
| Collecte brute | 116,9 | 9,92 % | 6,00 % / 6,00 % / 6,00 % | 6,00 % / 6,00 % / 6,00 % |
| Prestations (décès et rachats) | −108,8 | −9,24 % | −5,41 % / −5,41 % / −5,41 % | −5,49 % / −5,43 % / −5,39 % |
| **Collecte nette** | 8,1 | 0,69 % | 0,59 % / 0,59 % / 0,59 % | 0,51 % / 0,57 % / 0,61 % |
| Intérêts crédités (avant prélèvements sociaux) | 31,4 | 2,66 % | 2,37 % / 2,39 % / 2,38 % | 2,47 % / 2,55 % / 2,70 % |
| Prélèvements sociaux | −5,4 | −0,46 % | non modélisé | non modélisé |
| Autres mouvements (résidu : périmètres, arbitrages, transferts) | −5,1 | −0,43 % | non modélisé | non modélisé |
| **Variation de la PM** | 29,0 | 2,46 % | 2,96 % / 2,97 % / 2,97 % | 2,99 % / 3,13 % / 3,31 % |
| PM de début ; de fin | 1 178 ; 1 207 | | | |

**Lecture.** Avec c0 = 6 % et g = 1, le modèle approche la collecte nette de la place à environ 0,1 point près, malgré des périmètres et des flux différents (0,59 % la première année, contre 0,69 %), mais avec des flux bruts plus faibles : 6,0 % de primes et environ 5,4 % de sorties, contre 9,9 % et 9,2 % pour la place. La PM du modèle croît d'environ 3,0 % la première année, contre 2,5 % observés : le modèle ne comprend ni prélèvements sociaux (0,46 % de la PM) ni autres mouvements (0,43 %), ce que compensent en partie des intérêts crédités plus faibles (2,37 % à 2,39 % de la PM d'ouverture pour la gestion passive, contre environ 2,66 % pour la place, approchés par le taux moyen de 2,63 % appliqué à la PM moyenne).

**Interprétation de c0 = 6 %.** c0 est l'intensité brute qui, compte tenu des sorties du modèle, redonne la collecte nette observée en 2025. Ce n'est ni un calibrage des flux bruts, ni un calibrage de la croissance de la PM, et une seule année ne mesure pas une collecte durable. Deux conséquences : la PM projetée, existant comme affaires nouvelles, est un peu surestimée, faute de prélèvements sociaux (qui réduiraient aussi les chargements futurs) ; le volume brut des entrées et des sorties est plus faible que sur le marché, ce qui réduit le rôle des primes dans la liquidité. À l'intensité forte (c0 = 10 %), les mêmes sorties donnent une collecte nette d'environ 4,6 % de la PM par an avec g = 1, soit bien plus que les 0,7 % observés : c'est une borne haute.

### Contrat sans marge explicite dans le fonds mutualisé : origine du résidu

Équivalent certain, gestion passive, participation de 100 %, sans PPB, chargement, frais, frais d'acquisition ni TMG, c0 = 6 %, eta = 0 (identifiant `contrat_equitable` dans les résultats). Sans marge explicite, la valeur pour l'actionnaire n'est pas nulle pour autant : elle dépend des conventions de partage et de liquidation du modèle. Le résidu mesuré, avant impôt, s'attribue exactement aux postes de fin de projection (VA des dividendes et valeurs actualisées des postes du bilan comptable final, écarts avec et sans affaires nouvelles) :

| Profil | VA des primes | Résidu | en % des primes | VA des dividendes | Fonds propres finaux | Dividende à payer final | Réserve de capitalisation finale | Plus-values latentes finales non partagées | Moins-values obligataires réalisées (VA) : extinction / avec collecte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 560,1 | 4,65 | 0,83 % | 1,32 | 2,32 | 0,16 | 0,72 | 0,13 | −6,50 / 0,00 |
| B | 579,7 | 0,92 | 0,16 % | −0,94 | 1,63 | 0,10 | 0,00 | 0,14 | 0,00 / 0,00 |
| C | 590,2 | 2,93 | 0,50 % | 0,19 | 1,97 | 0,13 | 0,44 | 0,20 | −2,75 / 0,00 |

**Lecture.** Le résidu ne vient pas d'une création de valeur à l'actif (fuite nulle, primes investies au prix du marché) : c'est un transfert des assurés vers l'actionnaire, produit par des règles du modèle. (1) La politique de distribution garde les fonds propres comptables à leur ratio d'ouverture sur la PM : la croissance retient du capital, dont la quote-part des produits financiers revient à l'actionnaire, hors participation. (2) Les primes financent les sorties : le fonds vend moins d'obligations en moins-value ; la réserve de capitalisation n'absorbe plus ces pertes et son solde reste à l'actionnaire en fin de projection (A et C). (3) La part des plus-values latentes finales non rendue aux assurés croît avec l'actif. Cette réconciliation comptable montre où se trouve la valeur dans le modèle ; elle ne démontre pas, à elle seule, que son attribution est économiquement juste.

**Réserve de capitalisation.** Dans le modèle, les plus ou moins-values obligataires réalisées sont portées à la réserve de capitalisation, hors assiette de la participation ; au-delà de la réserve, les moins-values passent dans le résultat financier de l'année suivante ; en fin de projection, les assurés reçoivent la PM, la PPB et leur part des plus-values latentes, et le solde de la réserve reste à l'actionnaire. Ce traitement suit le principe de l'article R.351-2-1 du Code des assurances : le calcul du BE tient compte des dotations et reprises de la réserve constituée à la date de calcul pendant la durée des engagements, et la valeur actuelle attendue de son solde en fin d'engagements est intégrée à la réserve de réconciliation, en fonds propres de base de niveau 1. Le modèle n'en reproduit pas toutes les modalités : il ne distingue pas la réserve constituée à la date de calcul des dotations futures. L'attribution des postes ci-dessus résulte donc des conventions de partage et de liquidation retenues ; ce n'est pas une validation réglementaire de leur propriété.

**Variantes de liquidation.** Même cas, en retirant l'une ou l'autre des deux conventions : réserve de capitalisation d'ouverture reclassée en fonds propres comptables (actif inchangé), fonds propres comptables positifs distribués chaque année (la croissance ne retient plus de capital comptable), ou les deux. Les plus-values latentes d'ouverture restent celles du profil : les annuler demanderait un autre portefeuille, ce qui n'est pas fait. Résidu avant impôt (en % de la VA des primes) :

| Profil | Cas de base | Réserve initiale nulle | Sans rétention des fonds propres | Les deux | Les deux : apports évités (VA) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 4,65 (0,83 %) | 3,69 (0,66 %) | 5,02 (0,91 %) | 3,68 (0,67 %) | 3,55 |
| B | 0,92 (0,16 %) | 0,51 (0,09 %) | 5,80 (1,00 %) | 0,08 (0,01 %) | 0,00 |
| C | 2,93 (0,50 %) | 0,46 (0,08 %) | 3,38 (0,57 %) | 0,04 (0,01 %) | 0,00 |

**Lecture.** Sans réserve de capitalisation initiale ni rétention de capital, le résidu disparaît pour B et C (0,01 % des primes pour B et 0,01 % des primes pour C) : il venait bien de ces deux conventions. Retirer la seule rétention l'augmente (A, B, C) : distribuer les fonds propres réduit l'actif, le fonds vend davantage d'obligations pour payer les sorties, et la réserve de capitalisation, qui absorbe ces moins-values en extinction, est davantage préservée par la collecte ; sa quote-part des produits financiers, hors participation (seule celle des provisions techniques y entre), revient à l'actionnaire. Pour A, le résidu persiste (0,67 %), presque entièrement sous forme d'apports évités (3,55) : en extinction, A vend des obligations en moins-value (VA −21,2), le taux servi atteint son plancher de 0 % et, la participation ne pouvant être négative, l'actionnaire porte les pertes au-delà de la réserve par des apports (chaque année à partir de l'année 34). Les primes nouvelles financent les sorties et évitent ces ventes. C'est l'asymétrie du partage (plancher du taux servi) appliquée aux fortes moins-values latentes d'ouverture de A (−185,5) : un mécanisme contractuel du modèle, pas une fuite de valorisation. Ce test n'est pas une preuve complète de neutralité : un seul scénario, une seule intensité, sans élasticité ; le seuil de 1 % est un choix.

**Contrôles** (`tests/test_v5_collecte.py` et ce calcul) :

- **cas limites** : c0 = 0 redonne exactement le portefeuille fermé, colonne par colonne, pour trois élasticités ; eta = 0 et c0 > 0 donnent C(t) = c0 x PM(t - 1) exactement, pour deux politiques de taux servi différentes (deux tests distincts) ;
- **comptabilisation** (cas cantonné) : contrats crédités au taux sans risque du scénario, sans chargement, frais, garantie ni option, sur un compte séparé ; leur valeur est nulle par construction, ce qui contrôle la comptabilisation des primes, des prestations et de l'actualisation, sans exercer le fonds mutualisé ;
- **contrat sans marge explicite dans le fonds mutualisé** (équivalent certain, sans chargement, frais, TMG ni PPB, participation de 100 %) : valeur des affaires nouvelles inférieure à 1 % de la VA des primes avant impôt (0,83 % pour A, 0,16 % pour B, 0,50 % pour C), contre plus de 5 % pour les contrats réalistes dans le même cas déterministe (eta = 0) ; le résidu est attribué ci-dessus, et la variante sans réserve initiale ni rétention le ramène sous 0,1 % pour B et C ;
- **absence d'arbitrage à l'actif** : sur l'équivalent certain, les primes investies au prix du marché ne créent ni ne détruisent de valeur (fuite inférieure à 1e-8), bilan équilibré chaque année ;
- **garanties** : quand le plancher de TMG du fonds est atteint exactement, la répartition de l'intérêt conserve l'intérêt décidé (test de non-régression ; une première version, corrigée depuis, créditait alors les contrats nouveaux au taux moyen, au-delà de l'intérêt décidé, dans 189 des 112 809 décisions d'un échantillon de contrôle des profils A et B, toutes pour le profil A ; les résultats ont été recalculés) ;
- **identité de la décomposition** : vraie par construction ; écart arithmétique maximal de 1e-12. Fuite moyenne au plus égale à 0,5 fois son demi-intervalle Monte-Carlo.

## 2. Gestion passive : valeur de l'existant, des affaires nouvelles et valeur totale

Moyennes risque neutre ± demi-intervalle à 95 %. Marge : valeur des affaires nouvelles rapportée à la VA des primes.

**Profil A** (apport 110,4, valeur de l'existant −21,5 ± 7,0)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 223,0 | 18,6 | −3,6 | −5,5 | **9,5 ± 1,7** | 4,3 % | −12,0 ± 8,6 | 260,5 | 567 |
| c0 3 %, eta 0,5 | 103,3 | 8,1 | −1,9 | −2,6 | **3,6 ± 1,1** | 3,5 % | −17,9 ± 8,1 | 114,8 | 451 |
| c0 3 %, eta 0,75 | 74,7 | 5,7 | −1,4 | −1,9 | **2,4 ± 0,9** | 3,3 % | −19,1 ± 7,9 | 82,2 | 426 |
| c0 3 %, eta 1,0 | 53,4 | 3,9 | −1,0 | −1,3 | **1,5 ± 0,8** | 2,9 % | −19,9 ± 7,8 | 58,3 | 408 |
| c0 3 %, eta 1,5 | 22,4 | 1,2 | −0,4 | −0,5 | **0,3 ± 0,5** | 1,4 % | −21,2 ± 7,5 | 24,2 | 384 |
| c0 6 %, eta 0,0 | 513,1 | 40,2 | −7,9 | −14,6 | **17,8 ± 3,7** | 3,5 % | −3,7 ± 10,5 | 606,4 | 863 |
| c0 6 %, eta 0,5 | 231,4 | 17,4 | −4,2 | −6,1 | **7,0 ± 2,5** | 3,0 % | −14,5 ± 9,4 | 259,8 | 565 |
| c0 6 %, eta 0,75 | 163,9 | 12,0 | −3,0 | −4,2 | **4,8 ± 2,0** | 2,9 % | −16,7 ± 8,9 | 181,5 | 502 |
| c0 6 %, eta 1,0 | 114,7 | 8,0 | −2,1 | −2,9 | **3,0 ± 1,7** | 2,6 % | −18,5 ± 8,7 | 125,7 | 458 |
| c0 6 %, eta 1,5 | 46,4 | 2,4 | −0,8 | −1,1 | **0,5 ± 1,2** | 1,2 % | −21,0 ± 8,1 | 50,2 | 403 |
| c0 10 %, eta 0,0 | 1 031,7 | 75,2 | −12,7 | −32,5 | **30,0 ± 7,2** | 2,9 % | 8,5 ± 14,0 | 1 236,7 | 1 412 |
| c0 10 %, eta 0,5 | 450,1 | 31,7 | −7,4 | −12,8 | **11,6 ± 4,9** | 2,6 % | −9,9 ± 11,8 | 511,9 | 767 |
| c0 10 %, eta 0,75 | 311,3 | 21,5 | −5,5 | −8,4 | **7,6 ± 3,9** | 2,5 % | −13,9 ± 10,8 | 348,2 | 633 |
| c0 10 %, eta 1,0 | 211,6 | 13,9 | −3,8 | −5,5 | **4,6 ± 3,2** | 2,2 % | −16,9 ± 10,2 | 233,4 | 541 |
| c0 10 %, eta 1,5 | 81,1 | 4,0 | −1,3 | −1,9 | **0,7 ± 2,1** | 0,9 % | −20,8 ± 9,0 | 87,8 | 430 |
| Extinction (c0 = 0) | - | - | - | - | - | - | −21,5 ± 7,0 | - | 367 |

**Profil B** (apport 29,5, valeur de l'existant 52,3 ± 5,7)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 236,4 | 16,5 | −2,3 | −6,6 | **7,6 ± 1,5** | 3,2 % | 60,0 ± 7,1 | 278,9 | 739 |
| c0 3 %, eta 0,5 | 143,5 | 9,2 | −1,3 | −3,9 | **4,0 ± 1,2** | 2,8 % | 56,3 ± 6,8 | 163,7 | 640 |
| c0 3 %, eta 0,75 | 114,8 | 7,0 | −1,0 | −3,1 | **2,9 ± 1,1** | 2,6 % | 55,3 ± 6,7 | 129,6 | 611 |
| c0 3 %, eta 1,0 | 91,2 | 5,2 | −0,7 | −2,4 | **2,1 ± 1,0** | 2,3 % | 54,4 ± 6,7 | 101,8 | 587 |
| c0 3 %, eta 1,5 | 53,3 | 2,3 | −0,3 | −1,3 | **0,7 ± 0,9** | 1,4 % | 53,1 ± 6,5 | 58,0 | 551 |
| c0 6 %, eta 0,0 | 539,8 | 36,2 | −4,4 | −15,3 | **16,4 ± 3,5** | 3,0 % | 68,8 ± 9,0 | 643,0 | 1 049 |
| c0 6 %, eta 0,5 | 317,3 | 19,9 | −2,7 | −8,8 | **8,4 ± 2,6** | 2,7 % | 60,8 ± 8,2 | 365,0 | 806 |
| c0 6 %, eta 0,75 | 249,7 | 15,0 | −2,1 | −6,7 | **6,2 ± 2,3** | 2,5 % | 58,5 ± 7,9 | 283,5 | 736 |
| c0 6 %, eta 1,0 | 195,1 | 10,9 | −1,5 | −5,1 | **4,3 ± 2,1** | 2,2 % | 56,6 ± 7,8 | 218,7 | 681 |
| c0 6 %, eta 1,5 | 110,7 | 4,8 | −0,7 | −2,7 | **1,4 ± 1,9** | 1,3 % | 53,8 ± 7,5 | 120,7 | 599 |
| c0 10 %, eta 0,0 | 1 077,1 | 69,2 | −6,4 | −31,1 | **31,7 ± 7,1** | 2,9 % | 84,0 ± 12,6 | 1 298,5 | 1 612 |
| c0 10 %, eta 0,5 | 604,4 | 36,7 | −4,3 | −16,8 | **15,6 ± 5,1** | 2,6 % | 67,9 ± 10,6 | 702,3 | 1 087 |
| c0 10 %, eta 0,75 | 465,3 | 27,1 | −3,4 | −12,6 | **11,0 ± 4,4** | 2,4 % | 63,4 ± 10,0 | 532,7 | 941 |
| c0 10 %, eta 1,0 | 356,0 | 19,2 | −2,5 | −9,3 | **7,4 ± 4,0** | 2,1 % | 59,7 ± 9,6 | 401,4 | 828 |
| c0 10 %, eta 1,5 | 194,6 | 8,1 | −1,2 | −4,7 | **2,3 ± 3,3** | 1,2 % | 54,6 ± 8,9 | 212,7 | 670 |
| Extinction (c0 = 0) | - | - | - | - | - | - | 52,3 ± 5,7 | - | 507 |

**Profil C** (apport 17,1, valeur de l'existant 74,7 ± 5,0)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 240,1 | 14,6 | 0,0 | −6,8 | **7,9 ± 1,5** | 3,3 % | 82,6 ± 6,4 | 283,8 | 779 |
| c0 3 %, eta 0,5 | 161,7 | 8,7 | 0,4 | −4,5 | **4,7 ± 1,2** | 2,9 % | 79,4 ± 6,2 | 185,1 | 691 |
| c0 3 %, eta 0,75 | 135,9 | 6,9 | 0,5 | −3,7 | **3,7 ± 1,1** | 2,7 % | 78,4 ± 6,1 | 153,6 | 663 |
| c0 3 %, eta 1,0 | 113,8 | 5,2 | 0,6 | −3,1 | **2,8 ± 1,1** | 2,4 % | 77,5 ± 6,0 | 127,0 | 640 |
| c0 3 %, eta 1,5 | 77,8 | 2,8 | 0,6 | −2,0 | **1,4 ± 1,0** | 1,8 % | 76,1 ± 5,9 | 84,4 | 602 |
| c0 6 %, eta 0,0 | 547,6 | 32,9 | −0,6 | −15,5 | **16,8 ± 3,5** | 3,1 % | 91,5 ± 8,3 | 653,4 | 1 096 |
| c0 6 %, eta 0,5 | 355,4 | 19,3 | 0,5 | −9,9 | **9,9 ± 2,7** | 2,8 % | 84,6 ± 7,7 | 409,7 | 876 |
| c0 6 %, eta 0,75 | 293,8 | 15,0 | 0,7 | −8,0 | **7,7 ± 2,5** | 2,6 % | 82,4 ± 7,4 | 334,1 | 810 |
| c0 6 %, eta 1,0 | 241,9 | 11,3 | 0,9 | −6,4 | **5,7 ± 2,3** | 2,4 % | 80,4 ± 7,2 | 271,1 | 755 |
| c0 6 %, eta 1,5 | 160,5 | 5,9 | 1,0 | −4,1 | **2,8 ± 2,0** | 1,8 % | 77,5 ± 6,9 | 174,5 | 671 |
| c0 10 %, eta 0,0 | 1 091,4 | 64,4 | −1,3 | −31,2 | **31,9 ± 7,2** | 2,9 % | 106,6 ± 11,9 | 1 317,6 | 1 671 |
| c0 10 %, eta 0,5 | 674,9 | 36,5 | 0,2 | −18,7 | **17,9 ± 5,3** | 2,7 % | 92,7 ± 10,2 | 785,5 | 1 190 |
| c0 10 %, eta 0,75 | 545,3 | 27,7 | 0,6 | −14,8 | **13,6 ± 4,7** | 2,5 % | 88,3 ± 9,5 | 625,0 | 1 049 |
| c0 10 %, eta 1,0 | 439,3 | 20,3 | 1,0 | −11,6 | **9,7 ± 4,4** | 2,2 % | 84,4 ± 9,2 | 495,1 | 936 |
| c0 10 %, eta 1,5 | 280,2 | 10,2 | 1,3 | −7,0 | **4,5 ± 3,7** | 1,6 % | 79,2 ± 8,6 | 305,3 | 772 |
| Extinction (c0 = 0) | - | - | - | - | - | - | 74,7 ± 5,0 | - | 537 |

**Lecture.** Les affaires nouvelles de la gestion passive ont une valeur positive dans toutes les configurations testées. La variation d'impôt représente 47 % (A), 51 % (B), 50 % (C) de la valeur avant impôt (intensité centrale, élasticité modérée), bien plus que le taux nominal de l'impôt sur les sociétés. L'origine de cet écart n'est pas isolée : une explication possible est l'impôt sur les revenus du capital que la politique de distribution retient avec la croissance, au ratio d'ouverture fonds propres et apport sur PM (15,5 % pour A, 7,9 % pour B, 7,7 % pour C) ; la décomposition ne sépare pas cet effet. C'est une valeur **avant coût explicite de mobilisation du capital additionnel** : seuls l'impôt et la participation sur les revenus des fonds propres conservés sont déduits ; pas de marge pour risques non couvrables, frais d'acquisition fictifs. Une charge frictionnelle annuelle de 2,3 % (A), 2,0 % (B), 2,1 % (C) du SCR proxy des affaires nouvelles suffirait à annuler la valeur centrale (analyse de seuil, section 8).

## 3. La politique de marge reste-t-elle avantageuse ?

Écarts de la politique de marge (taux servi visé égal à la référence moins 1 point) à la gestion passive, mêmes scénarios. « Majorant » : l'avantage en portefeuille fermé majore l'avantage avec collecte si l'écart de valeur des affaires nouvelles est significativement négatif (« oui ») ; « non » s'il est significativement positif ; « indéterminé » s'il reste dans son intervalle. Marge qui annulerait l'avantage : avantage en portefeuille fermé rapporté à la VA des primes perdues par la politique de marge, à comparer à la marge effective des affaires nouvelles de la gestion passive ; indicateur de premier ordre, qui ignore le gain de marge sur les contrats encore collectés.

**Profil A**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 8,3 ± 0,4 | 1,8 ± 0,4 | **10,1 ± 0,6** | **+** | non | 1,00 / 1,00 | 129,6 % / 4,3 % |
| c0 3 %, eta 0,5 | 8,3 ± 0,4 | −0,1 ± 0,3 | **8,2 ± 0,6** | **+** | indéterminé | 0,32 / 0,42 | 32,4 % / 3,5 % |
| c0 3 %, eta 0,75 | 8,3 ± 0,4 | −0,7 ± 0,4 | **7,6 ± 0,6** | **+** | oui | 0,16 / 0,30 | 24,7 % / 3,3 % |
| c0 3 %, eta 1,0 | 8,3 ± 0,4 | −0,9 ± 0,4 | **7,4 ± 0,7** | **+** | oui | 0,07 / 0,21 | 23,4 % / 2,9 % |
| c0 3 %, eta 1,5 | 8,3 ± 0,4 | −0,2 ± 0,3 | **8,1 ± 0,6** | **+** | indéterminé | 0,01 / 0,09 | 45,2 % / 1,4 % |
| c0 6 %, eta 0,0 | 8,3 ± 0,4 | 4,6 ± 0,7 | **12,9 ± 0,8** | **+** | non | 1,00 / 1,00 | 49,7 % / 3,5 % |
| c0 6 %, eta 0,5 | 8,3 ± 0,4 | −0,1 ± 0,7 | **8,2 ± 0,9** | **+** | indéterminé | 0,33 / 0,44 | 13,0 % / 3,0 % |
| c0 6 %, eta 0,75 | 8,3 ± 0,4 | −1,5 ± 0,8 | **6,8 ± 1,0** | **+** | oui | 0,17 / 0,31 | 10,6 % / 2,9 % |
| c0 6 %, eta 1,0 | 8,3 ± 0,4 | −1,7 ± 0,9 | **6,6 ± 1,1** | **+** | oui | 0,07 / 0,22 | 10,6 % / 2,6 % |
| c0 6 %, eta 1,5 | 8,3 ± 0,4 | −0,3 ± 0,7 | **8,0 ± 0,9** | **+** | indéterminé | 0,01 / 0,09 | 21,7 % / 1,2 % |
| c0 10 %, eta 0,0 | 8,3 ± 0,4 | 6,7 ± 1,1 | **15,0 ± 1,1** | **+** | non | 1,00 / 1,00 | 23,6 % / 2,9 % |
| c0 10 %, eta 0,5 | 8,3 ± 0,4 | −0,1 ± 1,5 | **8,2 ± 1,7** | **+** | indéterminé | 0,34 / 0,48 | 5,9 % / 2,6 % |
| c0 10 %, eta 0,75 | 8,3 ± 0,4 | −2,3 ± 1,8 | **6,0 ± 1,9** | **+** | oui | 0,17 / 0,34 | 5,2 % / 2,5 % |
| c0 10 %, eta 1,0 | 8,3 ± 0,4 | −2,6 ± 1,9 | **5,7 ± 2,1** | **+** | oui | 0,07 / 0,24 | 5,5 % / 2,2 % |
| c0 10 %, eta 1,5 | 8,3 ± 0,4 | −0,4 ± 1,4 | **7,9 ± 1,5** | **+** | indéterminé | 0,01 / 0,09 | 12,3 % / 0,9 % |
| ONC max., c0 6 %, eta 0,0 | 4,0 ± 0,6 | 1,0 ± 0,8 | **4,9 ± 1,3** | **+** | non | - | - |
| ONC max., c0 6 %, eta 0,5 | 4,0 ± 0,6 | 0,1 ± 0,7 | **4,1 ± 1,2** | **+** | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,75 | 4,0 ± 0,6 | −0,3 ± 0,7 | **3,7 ± 1,2** | **+** | indéterminé | - | - |
| ONC max., c0 6 %, eta 1,0 | 4,0 ± 0,6 | −0,4 ± 0,7 | **3,6 ± 1,3** | **+**, borne sous le seuil | indéterminé | - | - |
| ONC max., c0 6 %, eta 1,5 | 4,0 ± 0,6 | 0,2 ± 0,5 | **4,2 ± 1,1** | **+** | indéterminé | - | - |

**Profil B**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 9,6 ± 0,6 | 1,4 ± 0,3 | **11,0 ± 0,7** | **+** | non | 1,00 / 1,00 | 175,5 % / 3,2 % |
| c0 3 %, eta 0,5 | 9,6 ± 0,6 | −0,3 ± 0,3 | **9,3 ± 0,6** | **+** | indéterminé | 0,45 / 0,59 | 26,7 % / 2,8 % |
| c0 3 %, eta 0,75 | 9,6 ± 0,6 | −1,0 ± 0,3 | **8,5 ± 0,6** | **+** | oui | 0,26 / 0,46 | 18,8 % / 2,6 % |
| c0 3 %, eta 1,0 | 9,6 ± 0,6 | −1,1 ± 0,5 | **8,4 ± 0,6** | **+** | oui | 0,13 / 0,37 | 16,9 % / 2,3 % |
| c0 3 %, eta 1,5 | 9,6 ± 0,6 | 0,0 ± 0,5 | **9,6 ± 0,6** | **+** | indéterminé | 0,08 / 0,21 | 31,0 % / 1,4 % |
| c0 6 %, eta 0,0 | 9,6 ± 0,6 | 2,6 ± 0,6 | **12,2 ± 0,9** | **+** | non | 1,00 / 1,00 | 67,5 % / 3,0 % |
| c0 6 %, eta 0,5 | 9,6 ± 0,6 | −0,9 ± 0,6 | **8,6 ± 0,8** | **+** | oui | 0,45 / 0,60 | 10,9 % / 2,7 % |
| c0 6 %, eta 0,75 | 9,6 ± 0,6 | −2,3 ± 0,8 | **7,2 ± 0,8** | **+** | oui | 0,26 / 0,48 | 8,1 % / 2,5 % |
| c0 6 %, eta 1,0 | 9,6 ± 0,6 | −2,5 ± 1,0 | **7,1 ± 0,9** | **+** | oui | 0,13 / 0,37 | 7,6 % / 2,2 % |
| c0 6 %, eta 1,5 | 9,6 ± 0,6 | 0,0 ± 1,1 | **9,6 ± 0,9** | **+** | indéterminé | 0,08 / 0,21 | 14,5 % / 1,3 % |
| c0 10 %, eta 0,0 | 9,6 ± 0,6 | 3,5 ± 1,0 | **13,1 ± 1,3** | **+** | non | 1,00 / 1,00 | 29,8 % / 2,9 % |
| c0 10 %, eta 0,5 | 9,6 ± 0,6 | −2,7 ± 1,3 | **6,8 ± 1,3** | **+** | oui | 0,46 / 0,62 | 5,1 % / 2,6 % |
| c0 10 %, eta 0,75 | 9,6 ± 0,6 | −4,7 ± 1,7 | **4,8 ± 1,6** | **+** | oui | 0,26 / 0,49 | 4,1 % / 2,4 % |
| c0 10 %, eta 1,0 | 9,6 ± 0,6 | −4,5 ± 2,0 | **5,1 ± 1,8** | **+** | oui | 0,13 / 0,38 | 4,0 % / 2,1 % |
| c0 10 %, eta 1,5 | 9,6 ± 0,6 | 0,1 ± 2,1 | **9,7 ± 1,8** | **+** | indéterminé | 0,08 / 0,21 | 8,0 % / 1,2 % |
| ONC max., c0 6 %, eta 0,0 | 3,8 ± 0,5 | 0,6 ± 0,7 | **4,4 ± 1,1** | **+** | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,5 | 3,8 ± 0,5 | −1,0 ± 0,5 | **2,7 ± 1,0** | **+**, borne sous le seuil | oui | - | - |
| ONC max., c0 6 %, eta 0,75 | 3,8 ± 0,5 | −1,5 ± 0,6 | **2,2 ± 1,0** | **+**, borne sous le seuil | oui | - | - |
| ONC max., c0 6 %, eta 1,0 | 3,8 ± 0,5 | −1,3 ± 0,7 | **2,5 ± 1,1** | **+**, borne sous le seuil | oui | - | - |
| ONC max., c0 6 %, eta 1,5 | 3,8 ± 0,5 | 0,2 ± 0,6 | **3,9 ± 1,1** | **+** | indéterminé | - | - |

**Profil C**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 7,3 ± 0,9 | 1,1 ± 0,3 | **8,4 ± 1,1** | **+** | non | 1,00 / 1,00 | 114,8 % / 3,3 % |
| c0 3 %, eta 0,5 | 7,3 ± 0,9 | −0,5 ± 0,2 | **6,8 ± 0,9** | **+** | oui | 0,51 / 0,65 | 19,9 % / 2,9 % |
| c0 3 %, eta 0,75 | 7,3 ± 0,9 | −1,2 ± 0,3 | **6,1 ± 0,9** | **+** | oui | 0,34 / 0,54 | 14,3 % / 2,7 % |
| c0 3 %, eta 1,0 | 7,3 ± 0,9 | −1,2 ± 0,4 | **6,1 ± 0,8** | **+** | oui | 0,22 / 0,45 | 13,1 % / 2,4 % |
| c0 3 %, eta 1,5 | 7,3 ± 0,9 | 0,2 ± 0,4 | **7,5 ± 0,7** | **+** | indéterminé | 0,19 / 0,30 | 27,5 % / 1,8 % |
| c0 6 %, eta 0,0 | 7,3 ± 0,9 | 2,4 ± 0,6 | **9,7 ± 1,2** | **+** | non | 1,00 / 1,00 | 45,2 % / 3,1 % |
| c0 6 %, eta 0,5 | 7,3 ± 0,9 | −1,3 ± 0,5 | **6,0 ± 1,0** | **+** | oui | 0,51 / 0,66 | 8,1 % / 2,8 % |
| c0 6 %, eta 0,75 | 7,3 ± 0,9 | −2,8 ± 0,6 | **4,5 ± 0,9** | **+** | oui | 0,33 / 0,55 | 6,1 % / 2,6 % |
| c0 6 %, eta 1,0 | 7,3 ± 0,9 | −2,7 ± 0,8 | **4,7 ± 0,8** | **+** | oui | 0,22 / 0,45 | 5,9 % / 2,4 % |
| c0 6 %, eta 1,5 | 7,3 ± 0,9 | 0,4 ± 0,8 | **7,7 ± 0,6** | **+** | indéterminé | 0,19 / 0,29 | 12,6 % / 1,8 % |
| c0 10 %, eta 0,0 | 7,3 ± 0,9 | 3,8 ± 1,0 | **11,1 ± 1,5** | **+** | non | 1,00 / 1,00 | 20,3 % / 2,9 % |
| c0 10 %, eta 0,5 | 7,3 ± 0,9 | −2,7 ± 1,2 | **4,6 ± 1,2** | **+** | oui | 0,51 / 0,67 | 3,8 % / 2,7 % |
| c0 10 %, eta 0,75 | 7,3 ± 0,9 | −5,3 ± 1,4 | **2,0 ± 1,2** | **+**, borne sous le seuil | oui | 0,33 / 0,55 | 3,0 % / 2,5 % |
| c0 10 %, eta 1,0 | 7,3 ± 0,9 | −4,7 ± 1,7 | **2,7 ± 1,3** | **+**, borne sous le seuil | oui | 0,21 / 0,45 | 3,0 % / 2,2 % |
| c0 10 %, eta 1,5 | 7,3 ± 0,9 | 0,8 ± 1,5 | **8,1 ± 1,0** | **+** | indéterminé | 0,19 / 0,29 | 6,8 % / 1,6 % |
| ONC max., c0 6 %, eta 0,0 | 2,7 ± 0,4 | −0,1 ± 0,6 | **2,6 ± 0,8** | **+**, borne sous le seuil | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,5 | 2,7 ± 0,4 | −0,9 ± 0,5 | **1,8 ± 0,8** | +, non important | oui | - | - |
| ONC max., c0 6 %, eta 0,75 | 2,7 ± 0,4 | −1,2 ± 0,5 | **1,5 ± 0,8** | +, non important | oui | - | - |
| ONC max., c0 6 %, eta 1,0 | 2,7 ± 0,4 | −0,8 ± 0,5 | **1,9 ± 0,8** | +, non important | oui | - | - |
| ONC max., c0 6 %, eta 1,5 | 2,7 ± 0,4 | 0,5 ± 0,5 | **3,2 ± 0,7** | **+** | non | - | - |

**Lecture.**

- **A** : toujours positif, non robuste ; écart de valeur totale à l'intensité centrale de 12,9 (eta 0,0), 8,2 (eta 0,5), 6,8 (eta 0,75), 6,6 (eta 1,0), 8,0 (eta 1,5), contre 8,3 en portefeuille fermé ; cas le moins favorable de la grille : 3,6 ± 1,3.
- **B** : toujours positif, non robuste ; écart de valeur totale à l'intensité centrale de 12,2 (eta 0,0), 8,6 (eta 0,5), 7,2 (eta 0,75), 7,1 (eta 1,0), 9,6 (eta 1,5), contre 9,6 en portefeuille fermé ; cas le moins favorable de la grille : 2,2 ± 1,0.
- **C** : toujours positif, non robuste ; écart de valeur totale à l'intensité centrale de 9,7 (eta 0,0), 6,0 (eta 0,5), 4,5 (eta 0,75), 4,7 (eta 1,0), 7,7 (eta 1,5), contre 7,3 en portefeuille fermé ; cas le moins favorable de la grille : 1,5 ± 0,8.

**Majorant**, par élasticité (neuf cas chacune : trois profils, trois intensités) : eta 0,0 : 0 oui, 9 non, 0 indéterminés ; eta 0,5 : 5 oui, 0 non, 4 indéterminés ; eta 0,75 : 9 oui, 0 non, 0 indéterminés ; eta 1,0 : 9 oui, 0 non, 0 indéterminés ; eta 1,5 : 0 oui, 0 non, 9 indéterminés. 
Avec une élasticité nulle, la politique de marge collecte presque autant que la gestion passive et gagne sa marge sur les contrats nouveaux : l'avantage fermé n'est pas un majorant. Aux élasticités plus fortes, l'écart de valeur des affaires nouvelles est le plus souvent négatif ou indéterminé. Il atteint au plus 80 % de l'avantage sur l'existant (médiane 17 %). L'avantage n'évolue pas de façon monotone avec l'élasticité dans 9 des 9 couples profil et intensité : les deux politiques servent sous la référence et perdent toutes deux de la collecte quand eta augmente.

## 4. Hypothèses du modèle de collecte qui peuvent conduire la conclusion

Trois choix peuvent produire mécaniquement la conclusion : e0 = 0 (la gestion passive, qui sert 0,5 point sous la référence, collecte déjà moins que c0), l'horizon de collecte de 10 ans, et g_min = 0. Les deux premiers sont testés ci-dessous (gestion passive et politiques de taux servi, intensités centrale et forte, élasticités modérée et soutenue) ; l'existant en extinction ne dépend pas de ces hypothèses. Avec e0 = −0,5 point, la collecte « normale » c0 x PM est atteinte en servant 0,5 point sous la référence, comme la gestion passive ; les horizons de 30 et 60 ans prolongent la collecte au-delà de 10 ans.

**Taux servi de marge**, écart de valeur totale à la gestion passive (écart de valeur des affaires nouvelles entre parenthèses)

| Profil | Hypothèse | c0 6 %, eta 0,5 | c0 6 %, eta 1,0 | c0 10 %, eta 0,5 | c0 10 %, eta 1,0 |
| --- | --- | ---: | ---: | ---: | ---: |
| A | centrale | 8,2 ± 0,9 (−0,1) | 6,6 ± 1,1 (−1,7) | 8,2 ± 1,7 (−0,1) | 5,7 ± 2,1 (−2,6) |
| A | e0 = −0,5 point | 9,2 ± 1,1 (0,9) | 6,8 ± 1,6 (−1,5) | 8,9 ± 2,1 (0,6) | 5,1 ± 3,5 (−3,2) |
| A | collecte 30 ans | 8,8 ± 3,2 (0,5) | 8,4 ± 4,7 (0,1) | 16,5 ± 21,6 (8,2) | 20,4 ± 30,9 (12,1) |
| A | collecte 60 ans | 10,5 ± 7,4 (2,2) | 11,9 ± 11,6 (3,6) | 63,8 ± 115,1 (55,5) | 105,6 ± 190,1 (97,3) |
| B | centrale | 8,6 ± 0,8 (−0,9) | 7,1 ± 0,9 (−2,5) | 6,8 ± 1,3 (−2,7) | 5,1 ± 1,8 (−4,5) |
| B | e0 = −0,5 point | 8,9 ± 0,9 (−0,7) | 6,1 ± 1,3 (−3,5) | 6,8 ± 1,8 (−2,7) | 1,3 ± 2,9 (−8,2) |
| B | collecte 30 ans | 8,7 ± 1,9 (−0,9) | 8,5 ± 3,4 (−1,0) | 10,4 ± 14,8 (0,8) | 16,9 ± 25,9 (7,3) |
| B | collecte 60 ans | 9,7 ± 4,2 (0,2) | 10,7 ± 8,3 (1,2) | 45,1 ± 81,8 (35,5) | 87,3 ± 161,5 (77,7) |
| C | centrale | 6,0 ± 1,0 (−1,3) | 4,7 ± 0,8 (−2,7) | 4,6 ± 1,2 (−2,7) | 2,7 ± 1,3 (−4,7) |
| C | e0 = −0,5 point | 6,5 ± 1,0 (−0,8) | 3,2 ± 1,1 (−4,1) | 4,5 ± 1,6 (−2,8) | −1,6 ± 2,6 (−8,9) |
| C | collecte 30 ans | 5,1 ± 2,8 (−2,2) | 4,5 ± 1,8 (−2,8) | 3,5 ± 4,1 (−3,8) | 5,1 ± 5,6 (−2,2) |
| C | collecte 60 ans | 2,9 ± 5,5 (−4,4) | 2,8 ± 3,3 (−4,5) | 4,1 ± 24,8 (−3,2) | 13,4 ± 42,0 (6,1) |

**Taux servi compétitif**, écart de valeur totale à la gestion passive (écart de valeur des affaires nouvelles entre parenthèses)

| Profil | Hypothèse | c0 6 %, eta 0,5 | c0 6 %, eta 1,0 | c0 10 %, eta 0,5 | c0 10 %, eta 1,0 |
| --- | --- | ---: | ---: | ---: | ---: |
| A | centrale | −8,5 ± 0,7 (−1,5) | −6,6 ± 0,9 (0,4) | −10,4 ± 1,1 (−3,4) | −6,8 ± 1,8 (0,2) |
| A | e0 = −0,5 point | −9,8 ± 0,8 (−2,8) | −8,6 ± 1,1 (−1,6) | −13,3 ± 1,3 (−6,3) | −10,6 ± 2,5 (−3,6) |
| A | collecte 30 ans | −10,7 ± 2,4 (−3,7) | −8,5 ± 4,1 (−1,5) | −20,5 ± 14,4 (−13,5) | −20,6 ± 28,0 (−13,6) |
| A | collecte 60 ans | −12,4 ± 5,1 (−5,4) | −11,4 ± 9,7 (−4,4) | −64,8 ± 92,2 (−57,8) | −112,9 ± 198,1 (−105,9) |
| B | centrale | −15,3 ± 1,0 (−3,7) | −12,8 ± 1,5 (−1,2) | −18,7 ± 1,8 (−7,1) | −13,7 ± 3,0 (−2,1) |
| B | e0 = −0,5 point | −17,5 ± 1,2 (−5,9) | −16,2 ± 1,8 (−4,5) | −22,5 ± 2,2 (−10,9) | −18,5 ± 4,1 (−6,9) |
| B | collecte 30 ans | −19,9 ± 4,1 (−8,3) | −17,0 ± 7,2 (−5,3) | −37,6 ± 26,2 (−26,0) | −38,2 ± 49,9 (−26,6) |
| B | collecte 60 ans | −24,2 ± 8,9 (−12,5) | −22,6 ± 17,3 (−10,9) | −106,6 ± 151,5 (−95,0) | −183,0 ± 332,4 (−171,3) |
| C | centrale | −16,5 ± 1,1 (−4,3) | −13,7 ± 1,7 (−1,5) | −19,4 ± 2,1 (−7,2) | −14,0 ± 3,6 (−1,8) |
| C | e0 = −0,5 point | −18,5 ± 1,3 (−6,3) | −16,9 ± 2,1 (−4,7) | −23,1 ± 2,5 (−10,9) | −18,5 ± 4,9 (−6,3) |
| C | collecte 30 ans | −22,8 ± 4,5 (−10,6) | −19,3 ± 8,1 (−7,1) | −43,7 ± 29,9 (−31,5) | −45,6 ± 58,7 (−33,4) |
| C | collecte 60 ans | −28,1 ± 9,8 (−15,9) | −25,7 ± 19,0 (−13,4) | −120,0 ± 166,4 (−107,8) | −211,1 ± 379,7 (−198,9) |

- **Taux servi de marge** sous ces hypothèses : A : toujours positif, non robuste (de 5,1 à 105,6) ; B : toujours positif, non robuste (de 1,3 à 87,3) ; C : positif là où il est significatif, non robuste (de −1,6 à 13,4).
- **Taux servi compétitif** sous ces hypothèses : A : toujours négatif, non robuste (de −112,9 à −8,5) ; B : toujours négatif, non robuste (de −183,0 à −16,2) ; C : toujours négatif, non robuste (de −211,1 à −16,9).

**Précision.** 24 cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à 379,7), dont 22 à l'intensité forte, toutes avec une collecte de 30 ans ou 60 ans. Sur plusieurs décennies de collecte, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche toute conclusion ; à l'intensité forte, la collecte nette atteint en outre environ 4,6 % de la PM par an quand g est proche de 1 (section 1), ce qui est peu plausible au regard des 0,7 % observés en 2025.

g_min = 0 n'est pas testé : une collecte négative reviendrait à des rachats supplémentaires, que la loi de rachat dynamique traite déjà. La conclusion dépend donc de e0 et de l'horizon de collecte dans la mesure indiquée ci-dessus, et de g_min par construction.

## 5. Les huit stratégies avec collecte

Écart de valeur totale à la gestion passive ± intervalle apparié, intensité centrale, puis robustesse sur toute la grille (trois intensités, cinq élasticités, loi de rachat ONC maximale à l'intensité centrale).

**Profil A**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,5 ± 0,1 | 0,9 ± 0,3 | 0,9 ± 0,3 | 0,8 ± 0,2 | 0,8 ± 0,2 | 0,7 ± 0,2 | 0,3 ± 0,1 | sans effet important |
| Repositionnement | −12,3 ± 1,0 | −17,2 ± 1,2 | −15,2 ± 1,3 | −14,2 ± 1,2 | −13,5 ± 1,1 | −12,7 ± 1,0 | −6,3 ± 0,9 | défavorable, robuste |
| Taux servi compétitif | −7,0 ± 0,4 | −11,1 ± 0,6 | −8,5 ± 0,7 | −7,5 ± 0,8 | −6,6 ± 0,9 | −5,3 ± 1,3 | −2,3 ± 0,7 | toujours négatif, non robuste |
| Taux servi de marge | 8,3 ± 0,4 | 12,9 ± 0,8 | 8,2 ± 0,9 | 6,8 ± 1,0 | 6,6 ± 1,1 | 8,0 ± 0,9 | 4,1 ± 1,2 | toujours positif, non robuste |
| Liquidité défensive | 1,6 ± 1,1 | −3,5 ± 1,8 | −0,9 ± 1,7 | −0,3 ± 1,6 | 0,2 ± 1,4 | 1,1 ± 1,2 | 3,2 ± 0,8 | change de signe selon les hypothèses |
| Compétitif préservant la PPB | −4,6 ± 0,4 | −11,6 ± 0,6 | −8,0 ± 0,5 | −7,0 ± 0,6 | −6,3 ± 0,7 | −5,0 ± 1,0 | −1,7 ± 0,7 | toujours négatif, non robuste |
| Rétention de capital | −1,1 ± 0,1 | −1,8 ± 0,1 | −1,4 ± 0,1 | −1,3 ± 0,1 | −1,2 ± 0,1 | −1,1 ± 0,1 | −0,6 ± 0,1 | sans effet important |

Plus forte valeur totale selon la configuration : Taux servi de marge (20 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. Le premier rang ne change pas sur la grille.

**Profil B**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,1 ± 0,2 | 0,3 ± 0,3 | 0,4 ± 0,3 | 0,4 ± 0,3 | 0,3 ± 0,3 | 0,2 ± 0,2 | 0,2 ± 0,2 | sans effet important |
| Repositionnement | −9,1 ± 0,7 | −12,1 ± 0,8 | −11,1 ± 0,9 | −10,6 ± 0,9 | −10,3 ± 0,8 | −9,6 ± 0,7 | −7,0 ± 0,8 | défavorable, robuste |
| Taux servi compétitif | −11,6 ± 0,5 | −18,9 ± 0,8 | −15,3 ± 1,0 | −14,0 ± 1,2 | −12,8 ± 1,5 | −11,2 ± 2,1 | −6,1 ± 1,6 | toujours négatif, non robuste |
| Taux servi de marge | 9,6 ± 0,6 | 12,2 ± 0,9 | 8,6 ± 0,8 | 7,2 ± 0,8 | 7,1 ± 0,9 | 9,6 ± 0,9 | 2,7 ± 1,0 | toujours positif, non robuste |
| Liquidité défensive | 1,0 ± 1,2 | 0,6 ± 1,9 | 0,5 ± 1,8 | 0,5 ± 1,7 | 0,7 ± 1,6 | 1,0 ± 1,4 | 2,9 ± 1,1 | positif là où il est significatif, non robuste |
| Compétitif préservant la PPB | −11,7 ± 0,5 | −20,1 ± 0,9 | −16,3 ± 1,0 | −15,0 ± 1,2 | −13,8 ± 1,4 | −12,1 ± 1,9 | −6,8 ± 1,6 | défavorable, robuste |
| Rétention de capital | −1,5 ± 0,1 | −2,1 ± 0,1 | −1,9 ± 0,1 | −1,8 ± 0,1 | −1,8 ± 0,1 | −1,7 ± 0,1 | −1,1 ± 0,0 | toujours négatif, non robuste |

Plus forte valeur totale selon la configuration : Taux servi de marge (17 configurations sur 20), Liquidité défensive (3 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. **Le premier rang change avec les hypothèses.**

**Profil C**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,0 ± 0,5 | 0,1 ± 0,8 | 0,1 ± 0,7 | 0,2 ± 0,7 | 0,1 ± 0,6 | 0,1 ± 0,6 | 0,3 ± 0,4 | sans effet important |
| Repositionnement | −1,6 ± 0,5 | −2,7 ± 0,6 | −2,7 ± 0,7 | −2,8 ± 0,7 | −2,7 ± 0,6 | −2,2 ± 0,6 | −1,8 ± 0,6 | toujours négatif, non robuste |
| Taux servi compétitif | −12,2 ± 0,6 | −20,0 ± 1,0 | −16,5 ± 1,1 | −15,0 ± 1,4 | −13,7 ± 1,7 | −11,9 ± 2,4 | −5,8 ± 1,8 | défavorable, robuste |
| Taux servi de marge | 7,3 ± 0,9 | 9,7 ± 1,2 | 6,0 ± 1,0 | 4,5 ± 0,9 | 4,7 ± 0,8 | 7,7 ± 0,6 | 1,8 ± 0,8 | toujours positif, non robuste |
| Liquidité défensive | 2,8 ± 1,5 | 3,2 ± 2,3 | 3,0 ± 2,1 | 3,0 ± 2,0 | 3,0 ± 2,0 | 3,0 ± 1,8 | 4,1 ± 1,4 | toujours positif, non robuste |
| Compétitif préservant la PPB | −12,9 ± 0,7 | −21,2 ± 1,0 | −17,5 ± 1,2 | −16,0 ± 1,4 | −14,8 ± 1,7 | −13,0 ± 2,4 | −6,8 ± 1,8 | défavorable, robuste |
| Rétention de capital | −1,6 ± 0,1 | −2,2 ± 0,1 | −2,0 ± 0,1 | −1,9 ± 0,1 | −1,9 ± 0,1 | −1,8 ± 0,1 | −1,3 ± 0,1 | toujours négatif, non robuste |

Plus forte valeur totale selon la configuration : Taux servi de marge (13 configurations sur 20), Liquidité défensive (7 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. **Le premier rang change avec les hypothèses.**

## 6. Effet sur l'existant et répartition des garanties

Variation du BE de l'existant, comptée pour l'actionnaire : - (BE de l'existant avec collecte - BE en extinction). Négative : la collecte enrichit les assurés existants (primes placées à des taux supérieurs au rendement comptable, qui relèvent le taux servi commun) ; positive : elle les dilue. Gestion passive, intensité centrale :

| Profil | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | −7,9 ± 0,8 | −4,2 ± 0,5 | −3,0 ± 0,4 | −2,1 ± 0,3 | −0,8 ± 0,1 |
| B | −4,4 ± 0,7 | −2,7 ± 0,4 | −2,1 ± 0,4 | −1,5 ± 0,3 | −0,7 ± 0,2 |
| C | −0,6 ± 0,9 | 0,5 ± 0,7 | 0,7 ± 0,6 | 0,9 ± 0,5 | 1,0 ± 0,4 |

**Transferts entre générations d'assurés.** Les contrats nouveaux reçoivent le taux servi commun, donc une part de la PPB d'ouverture et du rendement des obligations anciennes. Quand le taux commun passe sous le TMG de l'existant, l'existant reçoit son TMG et les contrats nouveaux le reste : ils financent alors une partie de la garantie de l'existant. Part des années-scénarios 2 à 10 où les contrats nouveaux sont crédités sous l'existant (intensité centrale, élasticité modérée) : A 32 % en gestion passive, 36 % en politique de marge (écart moyen de 59 pb ces années-là) ; B 12 % en gestion passive, 10 % en politique de marge (écart moyen de 31 pb ces années-là) ; C 0 % en gestion passive, 0 % en politique de marge. Ces transferts apparaissent dans les flux des contrats nouveaux et, en sens inverse, dans la variation du BE de l'existant : ni l'un ni l'autre terme ne les isole, seule la valeur des affaires nouvelles (leur somme) est interprétable.

## 7. Probabilité réelle (intensité centrale)

Indicateurs non actualisés, conditionnels aux hypothèses (taux sans prime de terme, prime actions fictive, défauts aux probabilités réelles), base 100 %, c0 = 6 %. Sorties nettes : prestations et frais moins primes, rapportés à la PM de début d'année ; quantile 99 % du maximum sur 10 ans. Probabilité d'apport : sur tout l'horizon de projection (60 ans). Écart du taux servi : moyenne du fonds (tous contrats) et contrats nouveaux, ceux qui déterminent la collecte.

**Profil A**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 712 | 4,9 % | 124,7 | 110,7 | 0,6 % | −70 pb / - | 80,5 | 35,6 % |
| Passive | 0,0 | 685,6 | 1 344 | 5,5 % | 65,6 | 208,8 | 0,1 % | −52 pb / −53 pb | 2,9 | 10,6 % |
| Passive | 0,5 | 447,2 | 1 139 | 5,3 % | 85,5 | 177,0 | 0,1 % | −56 pb / −56 pb | 37,8 | 29,5 % |
| Passive | 0,75 | 337,4 | 1 050 | 5,2 % | 95,1 | 163,1 | 0,1 % | −59 pb / −59 pb | 51,7 | 33,4 % |
| Passive | 1,0 | 240,8 | 961 | 5,1 % | 103,6 | 149,4 | 0,2 % | −62 pb / −63 pb | 67,3 | 35,6 % |
| Passive | 1,5 | 102,1 | 816 | 4,9 % | 115,5 | 126,8 | 0,5 % | −68 pb / −68 pb | 79,1 | 35,6 % |
| Taux servi de marge | fermé | 0,0 | 654 | 5,2 % | 146,8 | 107,1 | 1,1 % | −110 pb / - | 127,9 | 35,6 % |
| Taux servi de marge | 0,0 | 652,0 | 1 212 | 5,7 % | 91,5 | 198,3 | 0,0 % | −96 pb / −96 pb | 11,3 | 16,6 % |
| Taux servi de marge | 0,5 | 291,1 | 907 | 5,5 % | 123,6 | 148,4 | 0,2 % | −102 pb / −103 pb | 85,4 | 35,6 % |
| Taux servi de marge | 0,75 | 151,1 | 780 | 5,3 % | 135,7 | 127,7 | 0,4 % | −106 pb / −108 pb | 111,9 | 35,6 % |
| Taux servi de marge | 1,0 | 64,0 | 693 | 5,3 % | 142,8 | 113,3 | 0,6 % | −108 pb / −110 pb | 123,1 | 35,7 % |
| Taux servi de marge | 1,5 | 23,9 | 661 | 5,2 % | 145,3 | 108,2 | 0,7 % | −110 pb / −112 pb | 126,0 | 35,6 % |
| Taux servi compétitif | fermé | 0,0 | 712 | 4,6 % | 116,0 | 103,1 | 1,1 % | −56 pb / - | 95,6 | 35,6 % |
| Taux servi compétitif | 0,0 | 694,2 | 1 383 | 5,1 % | 50,8 | 200,4 | 0,1 % | −20 pb / −20 pb | 1,9 | 11,8 % |
| Taux servi compétitif | 0,5 | 558,4 | 1 273 | 5,0 % | 63,8 | 184,4 | 0,1 % | −26 pb / −26 pb | 38,4 | 30,8 % |
| Taux servi compétitif | 0,75 | 489,6 | 1 214 | 5,0 % | 70,6 | 175,9 | 0,2 % | −30 pb / −30 pb | 53,8 | 33,5 % |
| Taux servi compétitif | 1,0 | 429,8 | 1 153 | 4,9 % | 76,3 | 167,1 | 0,3 % | −33 pb / −34 pb | 59,5 | 34,7 % |
| Taux servi compétitif | 1,5 | 345,5 | 1 045 | 4,8 % | 84,0 | 151,3 | 0,5 % | −39 pb / −39 pb | 71,3 | 35,6 % |
| Compétitif préservant la PPB | fermé | 0,0 | 727 | 4,5 % | 115,2 | 111,8 | 0,7 % | −48 pb / - | 85,9 | 35,6 % |
| Compétitif préservant la PPB | 0,0 | 693,0 | 1 386 | 5,0 % | 49,6 | 213,1 | 0,1 % | −19 pb / −19 pb | 5,3 | 12,2 % |
| Compétitif préservant la PPB | 0,5 | 555,4 | 1 274 | 4,8 % | 61,6 | 195,9 | 0,1 % | −25 pb / −25 pb | 33,8 | 28,7 % |
| Compétitif préservant la PPB | 0,75 | 483,1 | 1 213 | 4,8 % | 68,3 | 186,5 | 0,1 % | −29 pb / −29 pb | 57,8 | 33,1 % |
| Compétitif préservant la PPB | 1,0 | 416,2 | 1 151 | 4,7 % | 74,5 | 177,0 | 0,1 % | −33 pb / −33 pb | 71,0 | 33,7 % |
| Compétitif préservant la PPB | 1,5 | 322,4 | 1 039 | 4,6 % | 83,0 | 159,7 | 0,5 % | −38 pb / −39 pb | 80,2 | 35,6 % |

**Profil B**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 745 | 10,1 % | 103,4 | 59,2 | 0,3 % | −41 pb / - | 6,4 | 17,5 % |
| Passive | 0,0 | 688,9 | 1 358 | 10,3 % | 83,8 | 107,9 | 0,2 % | −44 pb / −44 pb | 0,0 | 3,2 % |
| Passive | 0,5 | 495,9 | 1 175 | 10,2 % | 89,7 | 93,3 | 0,2 % | −44 pb / −44 pb | 0,4 | 9,8 % |
| Passive | 0,75 | 408,1 | 1 090 | 10,2 % | 92,3 | 86,6 | 0,2 % | −44 pb / −44 pb | 1,6 | 11,8 % |
| Passive | 1,0 | 326,5 | 1 013 | 10,1 % | 94,7 | 80,5 | 0,2 % | −44 pb / −44 pb | 3,3 | 13,1 % |
| Passive | 1,5 | 194,9 | 880 | 10,1 % | 98,4 | 69,9 | 0,2 % | −44 pb / −44 pb | 5,6 | 16,8 % |
| Taux servi de marge | fermé | 0,0 | 698 | 10,7 % | 106,1 | 53,9 | 0,2 % | −58 pb / - | 15,1 | 20,7 % |
| Taux servi de marge | 0,0 | 661,6 | 1 264 | 10,7 % | 88,2 | 97,4 | 0,2 % | −66 pb / −66 pb | 0,0 | 6,5 % |
| Taux servi de marge | 0,5 | 392,5 | 1 029 | 10,6 % | 95,6 | 79,3 | 0,2 % | −65 pb / −65 pb | 4,9 | 15,3 % |
| Taux servi de marge | 0,75 | 281,0 | 936 | 10,6 % | 98,2 | 72,1 | 0,2 % | −64 pb / −64 pb | 13,5 | 18,3 % |
| Taux servi de marge | 1,0 | 207,2 | 864 | 10,6 % | 99,9 | 66,7 | 0,2 % | −63 pb / −63 pb | 15,9 | 19,3 % |
| Taux servi de marge | 1,5 | 174,2 | 826 | 10,6 % | 100,7 | 63,7 | 0,2 % | −63 pb / −63 pb | 15,7 | 20,1 % |
| Taux servi compétitif | fermé | 0,0 | 763 | 9,6 % | 96,8 | 58,8 | 0,4 % | −13 pb / - | 8,8 | 21,5 % |
| Taux servi compétitif | 0,0 | 702,3 | 1 409 | 9,7 % | 72,7 | 108,7 | 0,3 % | −3 pb / −3 pb | 0,0 | 6,1 % |
| Taux servi compétitif | 0,5 | 661,0 | 1 380 | 9,6 % | 73,8 | 106,5 | 0,3 % | −4 pb / −4 pb | 0,4 | 11,7 % |
| Taux servi compétitif | 0,75 | 639,9 | 1 370 | 9,6 % | 74,5 | 105,7 | 0,3 % | −4 pb / −5 pb | 1,2 | 12,9 % |
| Taux servi compétitif | 1,0 | 619,6 | 1 358 | 9,5 % | 75,1 | 104,8 | 0,3 % | −5 pb / −5 pb | 1,6 | 13,8 % |
| Taux servi compétitif | 1,5 | 584,7 | 1 324 | 9,5 % | 76,0 | 102,2 | 0,2 % | −6 pb / −6 pb | 3,2 | 15,8 % |
| Compétitif préservant la PPB | fermé | 0,0 | 769 | 9,2 % | 94,4 | 60,6 | 0,4 % | −10 pb / - | 8,2 | 18,3 % |
| Compétitif préservant la PPB | 0,0 | 701,6 | 1 410 | 9,4 % | 71,2 | 111,1 | 0,3 % | −4 pb / −4 pb | 0,0 | 5,1 % |
| Compétitif préservant la PPB | 0,5 | 658,0 | 1 376 | 9,3 % | 72,0 | 108,4 | 0,3 % | −4 pb / −4 pb | 0,5 | 11,2 % |
| Compétitif préservant la PPB | 0,75 | 635,7 | 1 363 | 9,3 % | 72,4 | 107,3 | 0,3 % | −5 pb / −5 pb | 2,1 | 13,0 % |
| Compétitif préservant la PPB | 1,0 | 613,5 | 1 349 | 9,3 % | 72,9 | 106,2 | 0,3 % | −5 pb / −5 pb | 3,1 | 13,4 % |
| Compétitif préservant la PPB | 1,5 | 572,7 | 1 314 | 9,2 % | 73,7 | 103,5 | 0,3 % | −6 pb / −6 pb | 3,7 | 13,6 % |

**Profil C**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 769 | 11,9 % | 114,7 | 59,3 | 0,5 % | −17 pb / - | 23,0 | 16,7 % |
| Passive | 0,0 | 691,5 | 1 379 | 11,6 % | 95,2 | 106,3 | 0,4 % | −30 pb / −30 pb | 0,7 | 1,7 % |
| Passive | 0,5 | 556,6 | 1 215 | 11,6 % | 99,3 | 93,7 | 0,5 % | −29 pb / −29 pb | 3,0 | 9,0 % |
| Passive | 0,75 | 492,4 | 1 137 | 11,6 % | 101,3 | 87,6 | 0,4 % | −28 pb / −28 pb | 6,0 | 11,0 % |
| Passive | 1,0 | 431,3 | 1 077 | 11,6 % | 103,1 | 83,0 | 0,4 % | −28 pb / −28 pb | 12,5 | 13,3 % |
| Passive | 1,5 | 332,3 | 992 | 11,6 % | 105,8 | 76,5 | 0,2 % | −26 pb / −26 pb | 19,7 | 14,6 % |
| Taux servi de marge | fermé | 0,0 | 742 | 12,6 % | 113,1 | 53,7 | 0,6 % | −23 pb / - | 49,3 | 23,5 % |
| Taux servi de marge | 0,0 | 669,8 | 1 315 | 12,2 % | 96,5 | 95,2 | 0,5 % | −40 pb / −40 pb | 4,6 | 5,6 % |
| Taux servi de marge | 0,5 | 496,9 | 1 176 | 12,2 % | 99,4 | 85,1 | 0,4 % | −39 pb / −39 pb | 27,8 | 13,3 % |
| Taux servi de marge | 0,75 | 420,7 | 1 116 | 12,2 % | 100,6 | 80,7 | 0,4 % | −37 pb / −37 pb | 43,7 | 20,5 % |
| Taux servi de marge | 1,0 | 371,1 | 1 075 | 12,2 % | 101,4 | 77,8 | 0,4 % | −36 pb / −36 pb | 46,3 | 21,9 % |
| Taux servi de marge | 1,5 | 362,4 | 1 058 | 12,3 % | 101,9 | 76,5 | 0,4 % | −35 pb / −35 pb | 46,1 | 21,8 % |
| Taux servi compétitif | fermé | 0,0 | 780 | 11,5 % | 110,0 | 58,9 | 0,6 % | 3 pb / - | 29,4 | 25,0 % |
| Taux servi compétitif | 0,0 | 703,9 | 1 419 | 11,2 % | 88,3 | 107,2 | 0,7 % | 2 pb / 2 pb | 0,7 | 3,8 % |
| Taux servi compétitif | 0,5 | 699,5 | 1 409 | 11,2 % | 88,6 | 106,4 | 0,7 % | 2 pb / 2 pb | 1,3 | 9,1 % |
| Taux servi compétitif | 0,75 | 696,0 | 1 407 | 11,1 % | 88,8 | 106,3 | 0,7 % | 1 pb / 1 pb | 2,3 | 11,7 % |
| Taux servi compétitif | 1,0 | 692,5 | 1 406 | 11,1 % | 89,0 | 106,1 | 0,7 % | 1 pb / 1 pb | 3,2 | 12,4 % |
| Taux servi compétitif | 1,5 | 687,3 | 1 402 | 11,1 % | 89,3 | 105,8 | 0,6 % | 1 pb / 1 pb | 5,4 | 13,4 % |
| Compétitif préservant la PPB | fermé | 0,0 | 781 | 11,2 % | 109,4 | 60,4 | 0,6 % | 5 pb / - | 26,0 | 22,4 % |
| Compétitif préservant la PPB | 0,0 | 703,9 | 1 420 | 10,9 % | 87,2 | 109,7 | 0,6 % | 3 pb / 3 pb | 0,7 | 3,7 % |
| Compétitif préservant la PPB | 0,5 | 700,7 | 1 411 | 10,9 % | 87,4 | 109,1 | 0,6 % | 2 pb / 2 pb | 1,3 | 8,5 % |
| Compétitif préservant la PPB | 0,75 | 697,8 | 1 408 | 10,9 % | 87,5 | 108,8 | 0,6 % | 2 pb / 2 pb | 2,0 | 10,3 % |
| Compétitif préservant la PPB | 1,0 | 694,7 | 1 405 | 10,9 % | 87,7 | 108,6 | 0,5 % | 2 pb / 2 pb | 3,1 | 11,0 % |
| Compétitif préservant la PPB | 1,5 | 689,5 | 1 400 | 10,8 % | 88,0 | 108,2 | 0,5 % | 1 pb / 1 pb | 5,4 | 12,0 % |

Autres stratégies : `resultats/v5_collecte.json`, rubrique `reel`. Les sorties nettes maximales identiques d'une ligne à l'autre pour A correspondent au plafond de la loi de rachat dynamique, atteint dans les scénarios les plus défavorables.

**Liquidité** (gestion passive, élasticité modérée) : A : moins-values réalisées q99 80,5 en extinction, 37,8 avec collecte ; sorties nettes max. q99 35,6 % et 29,5 % ; B : moins-values réalisées q99 6,4 en extinction, 0,4 avec collecte ; sorties nettes max. q99 17,5 % et 9,8 % ; C : moins-values réalisées q99 23,0 en extinction, 3,0 avec collecte ; sorties nettes max. q99 16,7 % et 9,0 %. Les primes financent une partie des sorties et réduisent les ventes d'obligations en moins-value.

**Écart de taux servi effectivement réalisé** entre la politique de marge et la gestion passive (moyenne du fonds, années 1 à 10, élasticité modérée) : −46 pb (A), −21 pb (B), −10 pb (C), bien moins que le point d'écart des cibles : la participation minimale de 85 % et les reprises de PPB limitent la baisse effective du taux servi, donc la perte de collecte.

## 8. Capital

- **Besoin à l'ouverture** : inchangé par la collecte, par construction (vue prudentielle simplifiée en extinction, section 1). Apports à 100 % : A : passive 110,4, taux servi de marge 118,6, taux servi compétitif 99,9, compétitif préservant la PPB 108,8 ; B : passive 29,5, taux servi de marge 27,1, taux servi compétitif 27,2, compétitif préservant la PPB 28,8 ; C : passive 17,1, taux servi de marge 12,3, taux servi compétitif 15,5, compétitif préservant la PPB 17,3.
- **Capital retenu par la croissance** (gestion passive, élasticité modérée, probabilité réelle) : la politique de distribution maintient les fonds propres à leur cible en % de la PM ; la croissance de la PM retient donc du capital et réduit les dividendes. A : fonds propres médians à 10 ans 110,7 en extinction, 177,0 avec collecte ; dividendes 1-10 124,7 et 85,5 ; B : fonds propres médians à 10 ans 59,2 en extinction, 93,3 avec collecte ; dividendes 1-10 103,4 et 89,7 ; C : fonds propres médians à 10 ans 59,3 en extinction, 93,7 avec collecte ; dividendes 1-10 114,7 et 99,3.
- **Capital de la croissance, ordre de grandeur** : en supposant le SCR simplifié proportionnel à la PM, au ratio d'ouverture de chaque stratégie (SCR à 100 % de couverture / PM d'ouverture), l'écart de PM médiane à 10 ans entre la collecte centrale et l'extinction (probabilité réelle) demanderait le SCR supplémentaire ci-dessous. Ce n'est pas une projection du SCR : le profil de risque change avec la duration, la PPB, les plus-values latentes et l'allocation. SCR à 100 % : contrôle direct quand il existe, sinon interpolation linéaire en fonction de l'apport, comme pour le besoin d'apport de la consolidation.

| Profil | Stratégie | Apport à l'ouverture (écart à la gestion passive) | SCR / PM d'ouverture | SCR supplémentaire à 10 ans : eta 0,0 / 0,5 / 0,75 / 1,0 / 1,5 | Écart à la gestion passive, eta modérée |
| --- | --- | ---: | ---: | ---: | ---: |
| A | Passive | 110,4 (-) | 10,6 % | 67,1 / 45,4 / 35,9 / 26,5 / 11,0 | - |
| A | Réinvestissement progressif | 110,6 (0,2) | 10,7 % | 67,7 / 45,5 / 35,9 / 26,1 / 10,8 | 0,1 |
| A | Repositionnement | 129,4 (19,0) | 10,1 % | 55,9 / 31,4 / 25,0 / 19,5 / 9,6 | −14,0 |
| A | Taux servi compétitif | 99,9 (−10,5) | 8,9 % | 59,5 / 49,7 / 44,5 / 39,1 / 29,5 | 4,3 |
| A | Taux servi de marge | 118,6 (8,3) | 12,4 % | 69,0 / 31,3 / 15,6 / 4,7 / 0,8 | −14,1 |
| A | Liquidité défensive | 128,4 (18,0) | 12,4 % | 77,3 / 52,1 / 39,9 / 27,4 / 9,0 | 6,7 |
| A | Compétitif préservant la PPB | 108,8 (−1,6) | 9,8 % | 64,7 / 53,8 / 47,8 / 41,7 / 30,6 | 8,4 |
| A | Rétention de capital | 109,6 (−0,8) | 10,5 % | 66,0 / 44,6 / 35,2 / 26,0 / 10,8 | −0,8 |
| B | Passive | 29,5 (-) | 10,1 % | 62,1 / 43,5 / 34,9 / 27,2 / 13,7 | - |
| B | Réinvestissement progressif | 29,3 (−0,2) | 10,1 % | 62,1 / 43,4 / 34,9 / 27,1 / 13,6 | −0,1 |
| B | Repositionnement | 54,4 (24,9) | 10,5 % | 61,0 / 45,1 / 36,8 / 29,3 / 18,9 | 1,6 |
| B | Taux servi compétitif | 27,2 (−2,3) | 8,9 % | 57,9 / 55,3 / 54,3 / 53,3 / 50,3 | 11,7 |
| B | Taux servi de marge | 27,1 (−2,3) | 10,3 % | 58,4 / 34,2 / 24,5 / 17,2 / 13,2 | −9,4 |
| B | Liquidité défensive | 29,3 (−0,2) | 10,1 % | 61,5 / 43,1 / 34,7 / 26,7 / 13,4 | −0,5 |
| B | Compétitif préservant la PPB | 28,8 (−0,7) | 8,7 % | 55,6 / 52,7 / 51,5 / 50,3 / 47,3 | 9,2 |
| B | Rétention de capital | 30,0 (0,6) | 10,1 % | 62,0 / 43,5 / 34,9 / 27,1 / 13,8 | 0,0 |
| C | Passive | 17,1 (-) | 9,9 % | 60,2 / 44,1 / 36,3 / 30,4 / 22,0 | - |
| C | Réinvestissement progressif | 17,2 (0,1) | 9,9 % | 60,2 / 43,7 / 35,8 / 29,6 / 20,5 | −0,3 |
| C | Repositionnement | 22,9 (5,8) | 10,1 % | 61,8 / 46,4 / 41,4 / 36,9 / 28,4 | 2,3 |
| C | Taux servi compétitif | 15,5 (−1,6) | 9,1 % | 58,5 / 57,6 / 57,4 / 57,2 / 56,9 | 13,5 |
| C | Taux servi de marge | 12,3 (−4,8) | 9,7 % | 55,4 / 41,9 / 36,1 / 32,1 / 30,5 | −2,1 |
| C | Liquidité défensive | 18,8 (1,7) | 10,1 % | 61,1 / 44,5 / 36,4 / 29,4 / 18,3 | 0,4 |
| C | Compétitif préservant la PPB | 17,3 (0,2) | 9,1 % | 58,4 / 57,6 / 57,3 / 57,1 / 56,6 | 13,6 |
| C | Rétention de capital | 17,5 (0,4) | 9,9 % | 60,4 / 44,3 / 36,5 / 30,6 / 22,2 | 0,2 |

  La croissance demande un capital du même ordre que l'apport d'ouverture de B et C (eta modérée), et il dépend d'abord de l'élasticité. Pour Repositionnement (A : 19,0 à l'ouverture, −14,0 pour la croissance), Taux servi compétitif (A : −10,5 à l'ouverture, 4,3 pour la croissance), Taux servi de marge (A : 8,3 à l'ouverture, −14,1 pour la croissance), Taux servi compétitif (B : −2,3 à l'ouverture, 11,7 pour la croissance), l'écart de capital à l'ouverture et l'écart de capital de la croissance vont en sens contraire : la comparaison des besoins à l'ouverture ne suffit pas à classer les stratégies en capital. La politique de distribution retient des fonds propres comptables au ratio d'ouverture (point précédent) : ce SCR supplémentaire n'appelle donc pas un apport du même montant, mais fonds propres comptables et fonds propres prudentiels ne coïncident pas (plus ou moins-values latentes, marge de risque, absorption par les provisions techniques, impôts différés).
- **Seuil de coût du capital des affaires nouvelles** (analyse de seuil, aucun coût retenu ; gestion passive, collecte centrale, eta modérée, mêmes scénarios risque neutre que la valeur publiée). Capital proxy, scénario par scénario : K(t) = SCR à 100 % / PM d'ouverture x (PM avec collecte - PM en extinction). Une charge frictionnelle kappa x K(t - 1), payée en fin d'année t et actualisée au déflateur, réduit la valeur des affaires nouvelles de kappa x S, avec S = somme sur t de E[D(t) K(t - 1)] ; le seuil kappa* = valeur / S est la charge annuelle qui l'annulerait. kappa est une charge supplémentaire hypothétique, nette des coûts déjà valorisés (impôt et participation sur les revenus du capital comptable retenu) : ce n'est ni le rendement exigé en probabilité réelle, ni le taux de la marge de risque Solvabilité II, qui ont d'autres usages (`docs/V5_METHODOLOGIE.md`, section 3).

| Profil | Valeur des affaires nouvelles ± IC 95 % | SCR / PM d'ouverture | S, VA du capital proxy | kappa* | kappa* aux bornes de l'intervalle |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 7,0 ± 2,5 | 10,6 % | 308 | 2,3 % | 1,5 % à 3,1 % |
| B | 8,4 ± 2,6 | 10,1 % | 425 | 2,0 % | 1,4 % à 2,6 % |
| C | 9,9 ± 2,7 | 9,9 % | 468 | 2,1 % | 1,5 % à 2,7 % |

  Lecture : une charge frictionnelle supérieure à environ 2,0 % à 2,3 % par an du capital proxy suffirait à annuler la valeur centrale des affaires nouvelles. Le seuil hérite des limites du proxy (SCR proportionnel à la PM, au ratio d'ouverture) et ne dit pas quelle charge est la bonne.
- **Aucune stratégie ne garantit la conformité prudentielle future.** L'apport à l'ouverture porte l'indicateur simplifié à 100 % pour l'existant en extinction, à la date d'évaluation ; le SCR n'est pas projeté, la couverture des années suivantes n'est pas mesurée, et un apport futur éventuel n'est compté qu'en probabilité réelle, sans lien avec un ratio cible.

## 9. Limites

- **Modèle volontairement simple** : collecte proportionnelle à la PM, réaction linéaire encadrée, une seule génération agrégée de contrats nouveaux, même taux servi au-dessus des garanties pour tous les contrats, même loi de rachat ; la perte de compétitivité ne fait pas racheter l'existant au-delà de la loi de rachat dynamique.
- **Élasticité fictive** : aucune donnée vérifiée ne mesure la réaction de la collecte au taux servi relatif ; la grille de 0 à 1,5 est une plage testée en cinq points, pas une estimation.
- **Intensités** : dérivées d'agrégats de place d'une seule année (France Assureurs, ACPR), aux périmètres non strictement identiques ; c0 = 6 % redonne la collecte nette de 2025, pas ses flux bruts ni la croissance de la PM ; 10 % est une borne haute ; elles ne calibrent aucun profil.
- **Flux absents du modèle** : prélèvements sociaux, arbitrages entre supports et transferts ; la PM projetée est un peu surestimée.
- **Valeur des affaires nouvelles** : hors Solvabilité II ; avant coût explicite de mobilisation du capital additionnel (seuil seulement, section 8), sans marge pour risques non couvrables, frais d'acquisition fictifs ; horizon de collecte de 10 ans au centre (30 et 60 ans en sensibilité).
- **Contrat sans marge explicite** : son résidu dépend des conventions de partage et de liquidation (réserve de capitalisation, plus-values latentes finales, rétention de capital, plancher du taux servi) ; le traitement de la réserve suit le principe de l'article R.351-2-1 du Code des assurances sans en reproduire toutes les modalités.
- **Vue prudentielle** : calculée en extinction ; les effets de la collecte sur les hypothèses de projection de l'existant n'y sont pas repris.
- **Décomposition** : seule la valeur des affaires nouvelles s'interprète ; ses termes déplacent les transferts entre générations d'assurés sans les isoler.
- **Capital** : besoin à l'ouverture en extinction ; SCR futur non projeté ; capital de la croissance estimé seulement en ordre de grandeur (SCR proportionnel à la PM) ; aucune stratégie ne garantit la conformité prudentielle future.

