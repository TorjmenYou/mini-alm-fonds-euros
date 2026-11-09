# V5 : collecte nouvelle et stratégies ALM

Généré par `scripts/v5_rapport_collecte.py` depuis `resultats/v5_collecte.json` (`scripts/v5_collecte.py`), `resultats/v5_consolidation.json` et `resultats/v5_reconciliation_collecte.json` (`scripts/v5_reconciliation_collecte.py`). Spécification : `docs/V5_SPECIFICATION_COLLECTE.md`. Risque neutre : 1 000 scénarios, base sans VA, mêmes scénarios et mêmes tirages de défaut pour toutes les stratégies, intensités et élasticités. Unités fictives : 1 unité = 10 M€. **Profils fictifs, première version volontairement simple du modèle de collecte : analyse exploratoire, conditionnelle aux hypothèses, ce n'est pas une recommandation.**

**Base de capital commune.** Chaque stratégie garde l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (`docs/V5_STRATEGIES.md`, section 2). Cet apport est calculé sur l'existant en extinction, dans la frontière des contrats : la collecte ne le modifie pas (test `test_vue_prudentielle_dans_la_frontiere_des_contrats`). C'est une convention simplifiée : la vue prudentielle exclut les primes et les contrats futurs, mais aussi les effets que la collecte peut avoir sur les hypothèses de projection de l'existant (politique d'investissement, produits financiers, frais), que ce document analyse séparément dans la vue économique ; un calcul Solvabilité II complet peut devoir en tenir compte.

**Trois valeurs, toujours séparées** (risque neutre, nettes de l'apport, des apports ultérieurs et de l'impôt) :

- *valeur de l'existant* : portefeuille en extinction (c0 = 0), c'est la valeur nette des documents précédents ;
- *valeur des affaires nouvelles* (valeur de franchise, hors Solvabilité II) = valeur totale - valeur de l'existant, sur les mêmes scénarios ;
- *valeur totale* pour l'actionnaire, avec collecte.

La valeur des affaires nouvelles se répartit, scénario par scénario, entre trois termes : les **flux des contrats nouveaux** (VA des primes - BE des contrats nouveaux, c'est-à-dire ce que ces contrats reçoivent dans le fonds mutualisé), la **variation du BE de l'existant**, comptée pour l'actionnaire, et l'**impôt supplémentaire**. Seule la somme s'interprète comme une valeur : un transfert entre générations d'assurés (PPB d'ouverture, coupons anciens, garanties) déplace les deux premiers termes en sens inverse, sans changer la somme (section 6).

**Lecture des écarts** à la gestion passive (mêmes scénarios, intervalle apparié à 95 %) : « ns » non significatif ; « +, non important » ou « −, non important » significatif mais sous le seuil d'importance (2 % du SCR simplifié du profil : 2,4 pour A, 1,9 pour B, 1,7 pour C) ; **+** ou **−** au-delà du seuil, « borne sous le seuil » si la borne de l'intervalle ne le dépasse pas. « Robuste » : borne de l'intervalle au-delà du seuil dans toutes les configurations (trois intensités, cinq élasticités, et la loi de rachat ONC maximale à l'intensité centrale).

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
| e0 | 0,0 % ; sensibilité -0,5 point | fictif : un assureur qui sert le taux du marché collecte c0 x PM ; la référence des assurés vaut 2,85 % en t = 0 (hypothèse : milieu des taux servis attendus pour 2026), le taux servi moyen observé de 2025 est de 2,63 % (ACPR n° 180) ; c0 est dérivé des flux d'un marché qui sert, par définition, le taux du marché, d'où e0 = 0 au centre ; sensibilité e0 = -0,5 point |
| Contrats nouveaux | TMG 0,0 %, chargement sur prime 0,0 %, frais d'acquisition 1,0 % de la prime ; chargements et frais sur encours, loi de rachat et mortalité de l'existant | fictif |

Sources des agrégats observés : Cercle de l'Épargne, communiqué du 27/01/2026 citant France Assureurs : cotisations 2025 de 192,1 Md€, dont 116,9 Md€ sur les supports en euros ; collecte nette des supports en euros de +8,1 Md€ (https://cercledelepargne.com/wp-content/uploads/2026/01/Communique-de-presse-de-Philippe-Crevel-directeur-du-Cercle-de-lEpargne-resultats-Assurance-vie-2025.pdf, source secondaire) ; ACPR, Analyses et synthèses n° 180, revalorisation 2025, 30/06/2026 : encours des contrats en euros de 1 178 Md€ fin 2024 et 1 207 Md€ fin 2025 ; taux de revalorisation moyen 2025 de 2,63 % (https://acpr.banque-france.fr/system/files/2026-06/20260630_AS180_revalorisation_2025.pdf). Ces agrégats portent sur une seule année.

### Réconciliation avec les flux de la place en 2025

En % de la PM de début d'année. Place : encours des contrats individuels en euros (ACPR), flux des supports en euros (France Assureurs), périmètres non strictement identiques ; observé, sauf les intérêts crédités (taux moyen appliqué à la moyenne des PM de début et de fin, approximation), les prélèvements sociaux (17,2 % des intérêts, prélevés chaque année) et les autres mouvements (résidu de l'identité). Modèle : gestion passive, intensité centrale c0 = 6 %, eta = 0 (donc g = 1), probabilité réelle, 1 000 scénarios ; année 1 et moyenne des années 1 à 10. Calcul : `scripts/v5_reconciliation_collecte.py`, `resultats/v5_reconciliation_collecte.json`.

| Poste | Place 2025, Md€ | Place 2025, % PM | Modèle, année 1 (A / B / C) | Modèle, moyenne 1-10 (A / B / C) |
| --- | ---: | ---: | ---: | ---: |
| Collecte brute | 116,9 | 9,92 % | 6,00 % / 6,00 % / 6,00 % | 6,00 % / 6,00 % / 6,00 % |
| Prestations (décès et rachats) | −108,8 | −9,24 % | −5,41 % / −5,41 % / −5,41 % | −5,49 % / −5,42 % / −5,37 % |
| **Collecte nette** | 8,1 | 0,69 % | 0,59 % / 0,59 % / 0,59 % | 0,51 % / 0,58 % / 0,63 % |
| Intérêts crédités (avant prélèvements sociaux) | 31,4 | 2,66 % | 2,34 % / 2,36 % / 2,35 % | 2,44 % / 2,56 % / 2,75 % |
| Prélèvements sociaux | −5,4 | −0,46 % | non modélisé | non modélisé |
| Autres mouvements (résidu : périmètres, arbitrages, transferts) | −5,1 | −0,43 % | non modélisé | non modélisé |
| **Variation de la PM** | 29,0 | 2,46 % | 2,93 % / 2,95 % / 2,94 % | 2,95 % / 3,14 % / 3,38 % |
| PM de début ; de fin | 1 178 ; 1 207 | | | |

**Lecture.** Avec c0 = 6 % et g = 1, le modèle approche la collecte nette de la place à environ 0,1 point près, malgré des périmètres et des flux différents (0,59 % la première année, contre 0,69 %), mais avec des flux bruts plus faibles : 6,0 % de primes et environ 5,4 % de sorties, contre 9,9 % et 9,2 % pour la place. La PM du modèle croît d'environ 2,9 % la première année, contre 2,5 % observés : le modèle ne comprend ni prélèvements sociaux (0,46 % de la PM) ni autres mouvements (0,43 %), ce que compensent en partie des intérêts crédités plus faibles (2,34 % à 2,36 % de la PM d'ouverture pour la gestion passive, contre environ 2,66 % pour la place, approchés par le taux moyen de 2,63 % appliqué à la PM moyenne).

**Interprétation de c0 = 6 %.** c0 est l'intensité brute qui, compte tenu des sorties du modèle, redonne la collecte nette observée en 2025. Ce n'est ni un calibrage des flux bruts, ni un calibrage de la croissance de la PM, et une seule année ne mesure pas une collecte durable. Deux conséquences : la PM projetée, existant comme affaires nouvelles, est un peu surestimée, faute de prélèvements sociaux (qui réduiraient aussi les chargements futurs) ; le volume brut des entrées et des sorties est plus faible que sur le marché, ce qui réduit le rôle des primes dans la liquidité. À l'intensité forte (c0 = 10 %), les mêmes sorties donnent une collecte nette d'environ 4,6 % de la PM par an avec g = 1, soit bien plus que les 0,7 % observés : c'est une borne haute.

### Contrat sans marge explicite dans le fonds mutualisé : origine du résidu

Équivalent certain, gestion passive, participation de 100 %, sans PPB, chargement, frais, frais d'acquisition ni TMG, c0 = 6 %, eta = 0 (identifiant `contrat_equitable` dans les résultats). Sans marge explicite, la valeur pour l'actionnaire n'est pas nulle pour autant : elle dépend des conventions de partage et de liquidation du modèle. Le résidu mesuré, avant impôt, s'attribue exactement aux postes de fin de projection (VA des dividendes et valeurs actualisées des postes du bilan comptable final, écarts avec et sans affaires nouvelles) :

| Profil | VA des primes | Résidu | en % des primes | VA des dividendes | Fonds propres finaux | Dividende à payer final | Réserve de capitalisation finale | Plus-values latentes finales non partagées | Moins-values obligataires réalisées (VA) : extinction / avec collecte |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 559,0 | 2,68 | 0,48 % | 0,36 | 1,77 | 0,11 | 0,35 | 0,10 | −2,16 / 0,00 |
| B | 576,4 | 0,70 | 0,12 % | −1,09 | 1,59 | 0,09 | 0,00 | 0,10 | 0,00 / 0,00 |
| C | 587,7 | 1,88 | 0,32 % | −0,61 | 1,94 | 0,12 | 0,26 | 0,17 | −1,68 / 0,00 |

**Lecture.** Le résidu ne vient pas d'une création de valeur à l'actif (fuite nulle, primes investies au prix du marché) : c'est un transfert des assurés vers l'actionnaire, produit par des règles du modèle. (1) La politique de distribution garde les fonds propres comptables à leur ratio d'ouverture sur la PM : la croissance retient du capital, dont la quote-part des produits financiers revient à l'actionnaire, hors participation. (2) Les primes financent les sorties : le fonds vend moins d'obligations en moins-value ; la réserve de capitalisation n'absorbe plus ces pertes et son solde reste à l'actionnaire en fin de projection (A et C). (3) La part des plus-values latentes finales non rendue aux assurés croît avec l'actif. Cette réconciliation comptable montre où se trouve la valeur dans le modèle ; elle ne démontre pas, à elle seule, que son attribution est économiquement juste.

**Réserve de capitalisation.** Dans le modèle, les plus ou moins-values obligataires réalisées sont portées à la réserve de capitalisation, hors assiette de la participation ; au-delà de la réserve, les moins-values passent dans le résultat financier de l'année suivante ; en fin de projection, les assurés reçoivent la PM, la PPB et leur part des plus-values latentes, et le solde de la réserve reste à l'actionnaire. Ce traitement suit le principe de l'article R.351-2-1 du Code des assurances : le calcul du BE tient compte des dotations et reprises de la réserve constituée à la date de calcul pendant la durée des engagements, et la valeur actuelle attendue de son solde en fin d'engagements est intégrée à la réserve de réconciliation, en fonds propres de base de niveau 1. Le modèle n'en reproduit pas toutes les modalités : il ne distingue pas la réserve constituée à la date de calcul des dotations futures. L'attribution des postes ci-dessus résulte donc des conventions de partage et de liquidation retenues ; ce n'est pas une validation réglementaire de leur propriété.

**Variantes de liquidation.** Même cas, en retirant l'une ou l'autre des deux conventions : réserve de capitalisation d'ouverture reclassée en fonds propres comptables (actif inchangé), fonds propres comptables positifs distribués chaque année (la croissance ne retient plus de capital comptable), ou les deux. Les plus-values latentes d'ouverture restent celles du profil : les annuler demanderait un autre portefeuille, ce qui n'est pas fait. Résidu avant impôt (en % de la VA des primes) :

| Profil | Cas de base | Réserve initiale nulle | Sans rétention des fonds propres | Les deux | Les deux : apports évités (VA) |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 2,68 (0,48 %) | 0,64 (0,11 %) | 4,17 (0,75 %) | 0,90 (0,16 %) | 0,00 |
| B | 0,70 (0,12 %) | 0,48 (0,08 %) | 4,81 (0,84 %) | 0,06 (0,01 %) | 0,00 |
| C | 1,88 (0,32 %) | 0,31 (0,05 %) | 3,66 (0,62 %) | −0,01 (0,00 %) | 0,00 |

**Lecture.** Sans réserve de capitalisation initiale ni rétention de capital, le résidu disparaît pour B et C (0,01 % des primes pour B et 0,00 % des primes pour C) : il venait bien de ces deux conventions. Retirer la seule rétention l'augmente (A, B, C) : distribuer les fonds propres réduit l'actif, le fonds vend davantage d'obligations pour payer les sorties, et la réserve de capitalisation, qui absorbe ces moins-values en extinction, est davantage préservée par la collecte ; sa quote-part des produits financiers, hors participation (seule celle des provisions techniques y entre), revient à l'actionnaire. Pour A, le résidu persiste (0,16 %), surtout sous forme de fonds propres finaux (0,86) : en extinction, A vend des obligations en moins-value (VA −27,3, contre 0,0 avec collecte) ; reportées sur l'exercice suivant, ces moins-values rendent certains résultats financiers négatifs et, la participation ne pouvant être négative, l'actionnaire porte ces pertes : ses fonds propres comptables finissent négatifs dans le portefeuille fermé, sans apport. Les primes nouvelles financent les sorties et évitent ces ventes. C'est l'asymétrie du partage (participation jamais négative) appliquée aux moins-values latentes d'ouverture de A, les plus fortes des trois profils (−170,9) : un mécanisme contractuel du modèle, pas une fuite de valorisation. Ce test n'est pas une preuve complète de neutralité : un seul scénario, une seule intensité, sans élasticité ; le seuil de 1 % est un choix.

**Contrôles** (`tests/test_v5_collecte.py` et ce calcul) :

- **cas limites** : c0 = 0 redonne exactement le portefeuille fermé, colonne par colonne, pour trois élasticités ; eta = 0 et c0 > 0 donnent C(t) = c0 x PM(t - 1) exactement, pour deux politiques de taux servi différentes (deux tests distincts) ;
- **comptabilisation** (cas cantonné) : contrats crédités au taux sans risque du scénario, sans chargement, frais, garantie ni option, sur un compte séparé ; leur valeur est nulle par construction, ce qui contrôle la comptabilisation des primes, des prestations et de l'actualisation, sans exercer le fonds mutualisé ;
- **contrat sans marge explicite dans le fonds mutualisé** (équivalent certain, sans chargement, frais, TMG ni PPB, participation de 100 %) : valeur des affaires nouvelles inférieure à 1 % de la VA des primes avant impôt (0,48 % pour A, 0,12 % pour B, 0,32 % pour C), contre 3,1 % à 3,3 % après impôt pour les contrats réalistes (risque neutre, c0 = 6 %, eta = 0, gestion passive) ; le résidu est attribué ci-dessus, et la variante sans réserve initiale ni rétention le ramène sous 0,1 % pour B et C ;
- **absence d'arbitrage à l'actif** : sur l'équivalent certain, les primes investies au prix du marché ne créent ni ne détruisent de valeur (fuite inférieure à 1e-8), bilan équilibré chaque année ;
- **garanties** : quand le plancher de TMG du fonds est atteint exactement, la répartition de l'intérêt conserve l'intérêt décidé (test de non-régression ; une première version, corrigée depuis, créditait alors les contrats nouveaux au taux moyen, au-delà de l'intérêt décidé, dans 189 des 112 809 décisions d'un échantillon de contrôle des profils A et B, toutes pour le profil A ; les résultats ont été recalculés) ;
- **identité de la décomposition** : vraie par construction ; écart arithmétique maximal de 2e-12. Fuite moyenne au plus égale à 0,6 fois son demi-intervalle Monte-Carlo.

## 2. Gestion passive : valeur de l'existant, des affaires nouvelles et valeur totale

Moyennes risque neutre ± demi-intervalle à 95 %. Marge : valeur des affaires nouvelles rapportée à la VA des primes.

**Profil A** (apport 101,0, valeur de l'existant −5,4 ± 7,1)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 220,1 | 17,9 | −3,5 | −5,7 | **8,7 ± 1,7** | 3,9 % | 3,3 ± 8,6 | 257,0 | 588 |
| c0 3 %, eta 0,5 | 101,7 | 7,7 | −1,8 | −2,7 | **3,2 ± 1,1** | 3,1 % | −2,2 ± 8,2 | 113,5 | 473 |
| c0 3 %, eta 0,75 | 73,2 | 5,3 | −1,3 | −1,9 | **2,2 ± 0,9** | 2,9 % | −3,2 ± 8,0 | 80,8 | 447 |
| c0 3 %, eta 1,0 | 52,5 | 3,6 | −0,9 | −1,3 | **1,4 ± 0,8** | 2,6 % | −4,0 ± 7,9 | 57,5 | 429 |
| c0 3 %, eta 1,5 | 23,3 | 1,2 | −0,3 | −0,5 | **0,3 ± 0,6** | 1,4 % | −5,1 ± 7,7 | 25,2 | 405 |
| c0 6 %, eta 0,0 | 505,4 | 38,7 | −7,1 | −14,9 | **16,7 ± 3,7** | 3,3 % | 11,3 ± 10,6 | 597,0 | 883 |
| c0 6 %, eta 0,5 | 224,6 | 16,1 | −3,8 | −6,1 | **6,2 ± 2,5** | 2,8 % | 0,8 ± 9,5 | 253,0 | 581 |
| c0 6 %, eta 0,75 | 158,7 | 11,1 | −2,8 | −4,2 | **4,1 ± 2,0** | 2,6 % | −1,3 ± 9,0 | 176,5 | 520 |
| c0 6 %, eta 1,0 | 111,5 | 7,3 | −1,9 | −2,9 | **2,6 ± 1,7** | 2,3 % | −2,8 ± 8,8 | 122,6 | 478 |
| c0 6 %, eta 1,5 | 48,0 | 2,3 | −0,6 | −1,1 | **0,5 ± 1,2** | 1,1 % | −4,9 ± 8,3 | 52,1 | 425 |
| c0 10 %, eta 0,0 | 1 015,1 | 72,4 | −11,3 | −32,2 | **28,9 ± 7,3** | 2,8 % | 23,5 ± 14,1 | 1 216,1 | 1 429 |
| c0 10 %, eta 0,5 | 429,5 | 29,0 | −6,5 | −12,2 | **10,3 ± 5,0** | 2,4 % | 4,9 ± 12,0 | 489,4 | 774 |
| c0 10 %, eta 0,75 | 296,2 | 19,6 | −4,8 | −8,0 | **6,8 ± 3,8** | 2,3 % | 1,4 ± 10,8 | 332,1 | 642 |
| c0 10 %, eta 1,0 | 202,8 | 12,6 | −3,3 | −5,3 | **4,1 ± 3,2** | 2,0 % | −1,3 ± 10,2 | 224,2 | 556 |
| c0 10 %, eta 1,5 | 83,5 | 3,8 | −1,1 | −1,9 | **0,7 ± 2,2** | 0,9 % | −4,7 ± 9,2 | 90,7 | 454 |
| Extinction (c0 = 0) | - | - | - | - | - | - | −5,4 ± 7,1 | - | 387 |

**Profil B** (apport 27,6, valeur de l'existant 57,5 ± 5,9)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 237,1 | 14,9 | −0,8 | −6,5 | **7,6 ± 1,6** | 3,2 % | 65,1 ± 7,5 | 280,1 | 790 |
| c0 3 %, eta 0,5 | 147,9 | 8,2 | −0,3 | −3,9 | **4,0 ± 1,4** | 2,7 % | 61,5 ± 7,3 | 169,9 | 695 |
| c0 3 %, eta 0,75 | 118,7 | 6,1 | −0,1 | −3,1 | **3,0 ± 1,2** | 2,5 % | 60,5 ± 7,2 | 134,7 | 665 |
| c0 3 %, eta 1,0 | 94,5 | 4,4 | 0,0 | −2,4 | **2,1 ± 1,2** | 2,2 % | 59,6 ± 7,1 | 106,0 | 640 |
| c0 3 %, eta 1,5 | 55,9 | 1,9 | 0,2 | −1,3 | **0,8 ± 1,0** | 1,4 % | 58,3 ± 6,9 | 61,1 | 603 |
| c0 6 %, eta 0,0 | 539,7 | 33,2 | −1,6 | −14,9 | **16,6 ± 3,6** | 3,1 % | 74,1 ± 9,4 | 643,4 | 1 099 |
| c0 6 %, eta 0,5 | 324,4 | 17,9 | −0,7 | −8,6 | **8,6 ± 3,0** | 2,7 % | 66,1 ± 8,9 | 375,3 | 864 |
| c0 6 %, eta 0,75 | 255,9 | 13,1 | −0,3 | −6,6 | **6,2 ± 2,7** | 2,4 % | 63,7 ± 8,6 | 292,2 | 793 |
| c0 6 %, eta 1,0 | 200,8 | 9,4 | −0,1 | −5,0 | **4,3 ± 2,5** | 2,2 % | 61,8 ± 8,4 | 226,2 | 736 |
| c0 6 %, eta 1,5 | 115,6 | 3,9 | 0,3 | −2,6 | **1,6 ± 2,2** | 1,4 % | 59,1 ± 8,0 | 126,6 | 653 |
| c0 10 %, eta 0,0 | 1 073,2 | 64,3 | −2,4 | −29,9 | **32,1 ± 7,3** | 3,0 % | 89,6 ± 13,1 | 1 294,2 | 1 657 |
| c0 10 %, eta 0,5 | 612,3 | 33,3 | −1,1 | −16,3 | **15,9 ± 5,8** | 2,6 % | 73,4 ± 11,7 | 714,8 | 1 146 |
| c0 10 %, eta 0,75 | 472,3 | 24,0 | −0,6 | −12,2 | **11,2 ± 5,1** | 2,4 % | 68,7 ± 10,9 | 543,2 | 999 |
| c0 10 %, eta 1,0 | 363,0 | 16,7 | −0,2 | −9,0 | **7,5 ± 4,6** | 2,1 % | 65,0 ± 10,5 | 411,2 | 885 |
| c0 10 %, eta 1,5 | 201,9 | 6,7 | 0,4 | −4,6 | **2,6 ± 3,8** | 1,3 % | 60,1 ± 9,7 | 221,5 | 726 |
| Extinction (c0 = 0) | - | - | - | - | - | - | 57,5 ± 5,9 | - | 557 |

**Profil C** (apport 0,0, valeur de l'existant 82,8 ± 5,7)

| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| c0 3 %, eta 0,0 | 240,8 | 11,2 | 3,1 | −6,2 | **8,1 ± 1,5** | 3,4 % | 90,9 ± 7,2 | 285,0 | 842 |
| c0 3 %, eta 0,5 | 168,4 | 6,2 | 3,0 | −4,2 | **5,0 ± 1,5** | 2,9 % | 87,8 ± 7,2 | 194,1 | 761 |
| c0 3 %, eta 0,75 | 143,3 | 4,6 | 2,8 | −3,5 | **4,0 ± 1,4** | 2,8 % | 86,8 ± 7,1 | 163,3 | 734 |
| c0 3 %, eta 1,0 | 121,4 | 3,3 | 2,7 | −2,9 | **3,1 ± 1,3** | 2,6 % | 85,9 ± 7,0 | 136,6 | 710 |
| c0 3 %, eta 1,5 | 85,6 | 1,4 | 2,3 | −1,9 | **1,8 ± 1,2** | 2,1 % | 84,6 ± 6,9 | 93,9 | 673 |
| c0 6 %, eta 0,0 | 547,6 | 26,6 | 5,2 | −14,1 | **17,8 ± 3,5** | 3,2 % | 100,6 ± 9,1 | 654,0 | 1 156 |
| c0 6 %, eta 0,5 | 366,5 | 14,6 | 5,2 | −9,1 | **10,7 ± 3,2** | 2,9 % | 93,5 ± 8,8 | 425,1 | 951 |
| c0 6 %, eta 0,75 | 305,7 | 10,8 | 5,0 | −7,4 | **8,4 ± 3,0** | 2,8 % | 91,2 ± 8,6 | 349,9 | 885 |
| c0 6 %, eta 1,0 | 254,6 | 7,7 | 4,7 | −6,0 | **6,5 ± 2,8** | 2,5 % | 89,2 ± 8,5 | 287,4 | 831 |
| c0 6 %, eta 1,5 | 174,3 | 3,2 | 4,0 | −3,8 | **3,4 ± 2,6** | 2,0 % | 86,2 ± 8,3 | 191,2 | 748 |
| c0 10 %, eta 0,0 | 1 088,2 | 54,9 | 7,1 | −28,0 | **34,1 ± 7,1** | 3,1 % | 116,8 ± 12,6 | 1 314,5 | 1 725 |
| c0 10 %, eta 0,5 | 687,6 | 29,4 | 7,2 | −17,0 | **19,6 ± 6,1** | 2,9 % | 102,4 ± 11,7 | 804,2 | 1 266 |
| c0 10 %, eta 0,75 | 559,1 | 21,5 | 7,1 | −13,4 | **15,2 ± 5,5** | 2,7 % | 98,0 ± 11,1 | 644,1 | 1 125 |
| c0 10 %, eta 1,0 | 454,6 | 15,0 | 6,8 | −10,6 | **11,3 ± 5,1** | 2,5 % | 94,1 ± 10,7 | 515,4 | 1 013 |
| c0 10 %, eta 1,5 | 299,3 | 6,3 | 5,9 | −6,5 | **5,7 ± 4,7** | 1,9 % | 88,5 ± 10,2 | 328,7 | 853 |
| Extinction (c0 = 0) | - | - | - | - | - | - | 82,8 ± 5,7 | - | 602 |

**Lecture.** Les affaires nouvelles de la gestion passive ont une valeur positive dans toutes les configurations testées. La variation d'impôt représente 49 % (A), 50 % (B), 46 % (C) de la valeur avant impôt (intensité centrale, élasticité modérée), bien plus que le taux nominal de l'impôt sur les sociétés. L'origine de cet écart n'est pas isolée : une explication possible est l'impôt sur les revenus du capital que la politique de distribution retient avec la croissance, au ratio d'ouverture fonds propres et apport sur PM (14,6 % pour A, 7,8 % pour B, 6,0 % pour C) ; la décomposition ne sépare pas cet effet. C'est une valeur **avant coût explicite de mobilisation du capital additionnel** : seuls l'impôt et la participation sur les revenus des fonds propres conservés sont déduits ; pas de marge pour risques non couvrables, frais d'acquisition fictifs. Une charge frictionnelle annuelle de 2,0 % (A), 2,0 % (B), 2,5 % (C) du SCR proxy des affaires nouvelles suffirait à annuler la valeur centrale (analyse de seuil, section 8).

## 3. La politique de marge reste-t-elle avantageuse ?

Écarts de la politique de marge (taux servi visé égal à la référence moins 1 point) à la gestion passive, mêmes scénarios. « Majorant » : l'avantage en portefeuille fermé majore l'avantage avec collecte si l'écart de valeur des affaires nouvelles est significativement négatif (« oui ») ; « non » s'il est significativement positif ; « indéterminé » s'il reste dans son intervalle. Marge qui annulerait l'avantage : avantage en portefeuille fermé rapporté à la VA des primes perdues par la politique de marge, à comparer à la marge effective des affaires nouvelles de la gestion passive ; indicateur de premier ordre, qui ignore le gain de marge sur les contrats encore collectés.

**Profil A**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 5,8 ± 0,4 | 0,9 ± 0,3 | **6,8 ± 0,5** | **+** | non | 1,00 / 1,00 | - |
| c0 3 %, eta 0,5 | 5,8 ± 0,4 | −0,1 ± 0,3 | **5,7 ± 0,5** | **+** | indéterminé | 0,35 / 0,42 | 31,2 % / 3,1 % |
| c0 3 %, eta 0,75 | 5,8 ± 0,4 | −0,7 ± 0,3 | **5,2 ± 0,5** | **+** | oui | 0,18 / 0,30 | 20,4 % / 2,9 % |
| c0 3 %, eta 1,0 | 5,8 ± 0,4 | −0,8 ± 0,4 | **5,0 ± 0,6** | **+** | oui | 0,08 / 0,21 | 17,9 % / 2,6 % |
| c0 3 %, eta 1,5 | 5,8 ± 0,4 | −0,2 ± 0,4 | **5,7 ± 0,6** | **+** | indéterminé | 0,02 / 0,10 | 33,1 % / 1,4 % |
| c0 6 %, eta 0,0 | 5,8 ± 0,4 | 2,4 ± 0,6 | **8,3 ± 0,7** | **+** | non | 1,00 / 1,00 | 72,9 % / 3,3 % |
| c0 6 %, eta 0,5 | 5,8 ± 0,4 | −0,3 ± 0,6 | **5,5 ± 0,7** | **+** | indéterminé | 0,36 / 0,44 | 12,3 % / 2,8 % |
| c0 6 %, eta 0,75 | 5,8 ± 0,4 | −1,3 ± 0,7 | **4,5 ± 0,8** | **+** | oui | 0,18 / 0,31 | 8,8 % / 2,6 % |
| c0 6 %, eta 1,0 | 5,8 ± 0,4 | −1,5 ± 0,9 | **4,3 ± 1,0** | **+** | oui | 0,08 / 0,22 | 8,2 % / 2,3 % |
| c0 6 %, eta 1,5 | 5,8 ± 0,4 | −0,3 ± 0,8 | **5,6 ± 0,9** | **+** | indéterminé | 0,02 / 0,10 | 15,9 % / 1,1 % |
| c0 10 %, eta 0,0 | 5,8 ± 0,4 | 4,0 ± 1,0 | **9,8 ± 1,0** | **+** | non | 1,00 / 1,00 | 24,3 % / 2,8 % |
| c0 10 %, eta 0,5 | 5,8 ± 0,4 | −0,6 ± 1,2 | **5,2 ± 1,3** | **+** | indéterminé | 0,37 / 0,47 | 5,4 % / 2,4 % |
| c0 10 %, eta 0,75 | 5,8 ± 0,4 | −2,4 ± 1,5 | **3,5 ± 1,5** | **+**, borne sous le seuil | oui | 0,19 / 0,33 | 4,3 % / 2,3 % |
| c0 10 %, eta 1,0 | 5,8 ± 0,4 | −2,5 ± 1,8 | **3,4 ± 1,8** | **+**, borne sous le seuil | oui | 0,08 / 0,23 | 4,3 % / 2,0 % |
| c0 10 %, eta 1,5 | 5,8 ± 0,4 | −0,3 ± 1,4 | **5,5 ± 1,5** | **+** | indéterminé | 0,02 / 0,10 | 9,0 % / 0,9 % |
| ONC max., c0 6 %, eta 0,0 | 3,3 ± 0,6 | 0,3 ± 0,5 | **3,6 ± 1,1** | **+** | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,5 | 3,3 ± 0,6 | −0,3 ± 0,5 | **3,0 ± 1,1** | **+**, borne sous le seuil | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,75 | 3,3 ± 0,6 | −0,6 ± 0,5 | **2,7 ± 1,1** | **+**, borne sous le seuil | oui | - | - |
| ONC max., c0 6 %, eta 1,0 | 3,3 ± 0,6 | −0,6 ± 0,6 | **2,7 ± 1,2** | **+**, borne sous le seuil | indéterminé | - | - |
| ONC max., c0 6 %, eta 1,5 | 3,3 ± 0,6 | 0,1 ± 0,4 | **3,4 ± 1,1** | **+**, borne sous le seuil | indéterminé | - | - |

**Profil B**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 6,3 ± 0,6 | 0,9 ± 0,2 | **7,1 ± 0,7** | **+** | non | 1,00 / 1,00 | 146,6 % / 3,2 % |
| c0 3 %, eta 0,5 | 6,3 ± 0,6 | −0,4 ± 0,3 | **5,8 ± 0,6** | **+** | oui | 0,49 / 0,61 | 19,1 % / 2,7 % |
| c0 3 %, eta 0,75 | 6,3 ± 0,6 | −1,1 ± 0,3 | **5,2 ± 0,6** | **+** | oui | 0,29 / 0,49 | 13,1 % / 2,5 % |
| c0 3 %, eta 1,0 | 6,3 ± 0,6 | −1,2 ± 0,5 | **5,1 ± 0,6** | **+** | oui | 0,16 / 0,38 | 11,7 % / 2,2 % |
| c0 3 %, eta 1,5 | 6,3 ± 0,6 | −0,1 ± 0,5 | **6,2 ± 0,6** | **+** | indéterminé | 0,11 / 0,22 | 23,0 % / 1,4 % |
| c0 6 %, eta 0,0 | 6,3 ± 0,6 | 1,6 ± 0,5 | **7,9 ± 0,9** | **+** | non | 1,00 / 1,00 | 53,4 % / 3,1 % |
| c0 6 %, eta 0,5 | 6,3 ± 0,6 | −1,2 ± 0,6 | **5,0 ± 0,8** | **+** | oui | 0,49 / 0,62 | 7,7 % / 2,7 % |
| c0 6 %, eta 0,75 | 6,3 ± 0,6 | −2,5 ± 0,7 | **3,7 ± 0,8** | **+** | oui | 0,29 / 0,49 | 5,6 % / 2,4 % |
| c0 6 %, eta 1,0 | 6,3 ± 0,6 | −2,6 ± 1,0 | **3,7 ± 1,0** | **+** | oui | 0,16 / 0,39 | 5,2 % / 2,2 % |
| c0 6 %, eta 1,5 | 6,3 ± 0,6 | −0,2 ± 1,0 | **6,1 ± 1,0** | **+** | indéterminé | 0,11 / 0,22 | 10,6 % / 1,4 % |
| c0 10 %, eta 0,0 | 6,3 ± 0,6 | 2,3 ± 0,9 | **8,5 ± 1,3** | **+** | non | 1,00 / 1,00 | 22,5 % / 3,0 % |
| c0 10 %, eta 0,5 | 6,3 ± 0,6 | −3,2 ± 1,3 | **3,1 ± 1,4** | **+**, borne sous le seuil | oui | 0,48 / 0,63 | 3,6 % / 2,6 % |
| c0 10 %, eta 0,75 | 6,3 ± 0,6 | −5,1 ± 1,5 | **1,2 ± 1,5** | ns | oui | 0,28 / 0,50 | 2,8 % / 2,4 % |
| c0 10 %, eta 1,0 | 6,3 ± 0,6 | −4,8 ± 2,0 | **1,5 ± 1,9** | ns | oui | 0,15 / 0,39 | 2,7 % / 2,1 % |
| c0 10 %, eta 1,5 | 6,3 ± 0,6 | −0,4 ± 1,9 | **5,8 ± 1,8** | **+** | indéterminé | 0,10 / 0,22 | 5,8 % / 1,3 % |
| ONC max., c0 6 %, eta 0,0 | 1,7 ± 0,5 | 0,6 ± 0,9 | **2,3 ± 1,3** | **+**, borne sous le seuil | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,5 | 1,7 ± 0,5 | −0,9 ± 0,6 | **0,9 ± 1,1** | ns | oui | - | - |
| ONC max., c0 6 %, eta 0,75 | 1,7 ± 0,5 | −1,5 ± 0,5 | **0,3 ± 0,9** | ns | oui | - | - |
| ONC max., c0 6 %, eta 1,0 | 1,7 ± 0,5 | −1,3 ± 0,5 | **0,4 ± 1,0** | ns | oui | - | - |
| ONC max., c0 6 %, eta 1,5 | 1,7 ± 0,5 | 0,1 ± 0,4 | **1,8 ± 0,9** | +, non important | indéterminé | - | - |

**Profil C**

| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |
| c0 3 %, eta 0,0 | 3,1 ± 0,7 | 0,4 ± 0,3 | **3,6 ± 0,8** | **+** | non | 1,00 / 1,00 | 58,9 % / 3,4 % |
| c0 3 %, eta 0,5 | 3,1 ± 0,7 | −0,8 ± 0,3 | **2,4 ± 0,8** | **+**, borne sous le seuil | oui | 0,57 / 0,68 | 10,1 % / 2,9 % |
| c0 3 %, eta 0,75 | 3,1 ± 0,7 | −1,3 ± 0,3 | **1,8 ± 0,7** | **+**, borne sous le seuil | oui | 0,41 / 0,58 | 7,1 % / 2,8 % |
| c0 3 %, eta 1,0 | 3,1 ± 0,7 | −1,2 ± 0,3 | **1,9 ± 0,7** | **+**, borne sous le seuil | oui | 0,30 / 0,49 | 6,6 % / 2,6 % |
| c0 3 %, eta 1,5 | 3,1 ± 0,7 | 0,2 ± 0,3 | **3,3 ± 0,6** | **+** | indéterminé | 0,28 / 0,33 | 18,4 % / 2,1 % |
| c0 6 %, eta 0,0 | 3,1 ± 0,7 | 0,9 ± 0,6 | **4,0 ± 1,1** | **+** | non | 1,00 / 1,00 | 21,9 % / 3,2 % |
| c0 6 %, eta 0,5 | 3,1 ± 0,7 | −1,9 ± 0,5 | **1,3 ± 0,9** | +, non important | oui | 0,56 / 0,68 | 4,0 % / 2,9 % |
| c0 6 %, eta 0,75 | 3,1 ± 0,7 | −3,1 ± 0,6 | **0,0 ± 0,9** | ns | oui | 0,39 / 0,57 | 3,0 % / 2,8 % |
| c0 6 %, eta 1,0 | 3,1 ± 0,7 | −2,8 ± 0,7 | **0,3 ± 0,8** | ns | oui | 0,29 / 0,48 | 2,9 % / 2,5 % |
| c0 6 %, eta 1,5 | 3,1 ± 0,7 | 0,3 ± 0,6 | **3,5 ± 0,7** | **+** | indéterminé | 0,26 / 0,32 | 8,1 % / 2,0 % |
| c0 10 %, eta 0,0 | 3,1 ± 0,7 | 1,4 ± 1,1 | **4,6 ± 1,5** | **+** | non | 1,00 / 1,00 | 9,4 % / 3,1 % |
| c0 10 %, eta 0,5 | 3,1 ± 0,7 | −4,0 ± 1,2 | **−0,8 ± 1,3** | ns | oui | 0,55 / 0,68 | 1,8 % / 2,9 % |
| c0 10 %, eta 0,75 | 3,1 ± 0,7 | −6,2 ± 1,2 | **−3,0 ± 1,3** | **−** | oui | 0,37 / 0,57 | 1,4 % / 2,7 % |
| c0 10 %, eta 1,0 | 3,1 ± 0,7 | −5,3 ± 1,4 | **−2,1 ± 1,3** | **−**, borne sous le seuil | oui | 0,27 / 0,47 | 1,5 % / 2,5 % |
| c0 10 %, eta 1,5 | 3,1 ± 0,7 | 0,4 ± 1,1 | **3,5 ± 1,0** | **+** | indéterminé | 0,25 / 0,32 | 4,0 % / 1,9 % |
| ONC max., c0 6 %, eta 0,0 | 0,9 ± 0,5 | −0,2 ± 0,6 | **0,8 ± 1,0** | ns | indéterminé | - | - |
| ONC max., c0 6 %, eta 0,5 | 0,9 ± 0,5 | −0,9 ± 0,4 | **0,0 ± 0,8** | ns | oui | - | - |
| ONC max., c0 6 %, eta 0,75 | 0,9 ± 0,5 | −1,2 ± 0,4 | **−0,2 ± 0,8** | ns | oui | - | - |
| ONC max., c0 6 %, eta 1,0 | 0,9 ± 0,5 | −0,8 ± 0,4 | **0,1 ± 0,8** | ns | oui | - | - |
| ONC max., c0 6 %, eta 1,5 | 0,9 ± 0,5 | 0,6 ± 0,4 | **1,6 ± 0,7** | +, non important | non | - | - |

**Lecture.**

- **A** : toujours positif, non robuste ; écart de valeur totale à l'intensité centrale de 8,3 (eta 0,0), 5,5 (eta 0,5), 4,5 (eta 0,75), 4,3 (eta 1,0), 5,6 (eta 1,5), contre 5,8 en portefeuille fermé ; cas le moins favorable de la grille : 2,7 ± 1,2.
- **B** : toujours positif, non robuste ; écart de valeur totale à l'intensité centrale de 7,9 (eta 0,0), 5,0 (eta 0,5), 3,7 (eta 0,75), 3,7 (eta 1,0), 6,1 (eta 1,5), contre 6,3 en portefeuille fermé ; cas le moins favorable de la grille : 0,3 ± 0,9.
- **C** : change de signe selon les hypothèses ; écart de valeur totale à l'intensité centrale de 4,0 (eta 0,0), 1,3 (eta 0,5), 0,0 (eta 0,75), 0,3 (eta 1,0), 3,5 (eta 1,5), contre 3,1 en portefeuille fermé ; cas le moins favorable de la grille : −3,0 ± 1,3.

**Majorant**, par élasticité (neuf cas chacune : trois profils, trois intensités) : eta 0,0 : 0 oui, 9 non, 0 indéterminés ; eta 0,5 : 6 oui, 0 non, 3 indéterminés ; eta 0,75 : 9 oui, 0 non, 0 indéterminés ; eta 1,0 : 9 oui, 0 non, 0 indéterminés ; eta 1,5 : 0 oui, 0 non, 9 indéterminés. 
Avec une élasticité nulle, la politique de marge collecte presque autant que la gestion passive et gagne sa marge sur les contrats nouveaux : l'avantage fermé n'est pas un majorant. Aux élasticités plus fortes, l'écart de valeur des affaires nouvelles est le plus souvent négatif ou indéterminé. Il atteint au plus 197 % de l'avantage sur l'existant (médiane 25 %). L'avantage n'évolue pas de façon monotone avec l'élasticité dans 9 des 9 couples profil et intensité : les deux politiques servent sous la référence et perdent toutes deux de la collecte quand eta augmente.

## 4. Hypothèses du modèle de collecte qui peuvent conduire la conclusion

Trois choix peuvent produire mécaniquement la conclusion : e0 = 0 (la gestion passive, qui sert 0,5 point sous la référence, collecte déjà moins que c0), l'horizon de collecte de 10 ans, et g_min = 0. Les deux premiers sont testés ci-dessous (gestion passive et politiques de taux servi, intensités centrale et forte, élasticités modérée et soutenue) ; l'existant en extinction ne dépend pas de ces hypothèses. Avec e0 = −0,5 point, la collecte « normale » c0 x PM est atteinte en servant 0,5 point sous la référence, comme la gestion passive ; les horizons de 30 et 60 ans prolongent la collecte au-delà de 10 ans.

**Taux servi de marge**, écart de valeur totale à la gestion passive (écart de valeur des affaires nouvelles entre parenthèses)

| Profil | Hypothèse | c0 6 %, eta 0,5 | c0 6 %, eta 1,0 | c0 10 %, eta 0,5 | c0 10 %, eta 1,0 |
| --- | --- | ---: | ---: | ---: | ---: |
| A | centrale | 5,5 ± 0,7 (−0,3) | 4,3 ± 1,0 (−1,5) | 5,2 ± 1,3 (−0,6) | 3,4 ± 1,8 (−2,5) |
| A | e0 = −0,5 point | 6,1 ± 0,9 (0,3) | 4,2 ± 1,2 (−1,7) | 5,5 ± 1,7 (−0,3) | 2,3 ± 2,9 (−3,6) |
| A | collecte 30 ans | 5,7 ± 2,0 (−0,2) | 5,9 ± 4,2 (0,1) | 10,1 ± 15,9 (4,2) | 16,0 ± 26,9 (10,2) |
| A | collecte 60 ans | 6,6 ± 4,4 (0,8) | 9,4 ± 10,4 (3,5) | 47,8 ± 87,8 (42,0) | 99,3 ± 176,0 (93,5) |
| B | centrale | 5,0 ± 0,8 (−1,2) | 3,7 ± 1,0 (−2,6) | 3,1 ± 1,4 (−3,2) | 1,5 ± 1,9 (−4,8) |
| B | e0 = −0,5 point | 5,1 ± 1,0 (−1,1) | 2,4 ± 1,4 (−3,9) | 2,5 ± 1,8 (−3,7) | −2,6 ± 3,0 (−8,8) |
| B | collecte 30 ans | 5,8 ± 2,3 (−0,5) | 5,9 ± 4,1 (−0,3) | 7,4 ± 16,0 (1,2) | 15,4 ± 28,2 (9,2) |
| B | collecte 60 ans | 6,8 ± 4,9 (0,5) | 8,2 ± 10,1 (1,9) | 45,8 ± 89,5 (39,5) | 90,8 ± 184,0 (84,5) |
| C | centrale | 1,3 ± 0,9 (−1,9) | 0,3 ± 0,8 (−2,8) | −0,8 ± 1,3 (−4,0) | −2,1 ± 1,3 (−5,3) |
| C | e0 = −0,5 point | 1,3 ± 1,0 (−1,9) | −1,7 ± 1,2 (−4,8) | −1,5 ± 2,0 (−4,7) | −7,1 ± 3,4 (−10,3) |
| C | collecte 30 ans | 0,4 ± 2,2 (−2,7) | 0,2 ± 1,9 (−3,0) | −1,1 ± 8,4 (−4,2) | −2,2 ± 2,8 (−5,3) |
| C | collecte 60 ans | −1,2 ± 4,4 (−4,3) | −1,2 ± 4,3 (−4,4) | 10,8 ± 43,3 (7,6) | −4,0 ± 11,7 (−7,1) |

**Taux servi compétitif**, écart de valeur totale à la gestion passive (écart de valeur des affaires nouvelles entre parenthèses)

| Profil | Hypothèse | c0 6 %, eta 0,5 | c0 6 %, eta 1,0 | c0 10 %, eta 0,5 | c0 10 %, eta 1,0 |
| --- | --- | ---: | ---: | ---: | ---: |
| A | centrale | −6,9 ± 0,6 (−0,9) | −5,4 ± 0,9 (0,6) | −8,4 ± 1,0 (−2,4) | −5,4 ± 1,7 (0,6) |
| A | e0 = −0,5 point | −8,0 ± 0,7 (−2,0) | −6,9 ± 1,1 (−0,9) | −10,7 ± 1,2 (−4,7) | −8,1 ± 2,1 (−2,1) |
| A | collecte 30 ans | −9,3 ± 2,2 (−3,3) | −7,3 ± 4,0 (−1,3) | −17,1 ± 11,5 (−11,0) | −18,2 ± 27,8 (−12,2) |
| A | collecte 60 ans | −11,8 ± 5,0 (−5,8) | −10,7 ± 9,8 (−4,6) | −52,2 ± 61,0 (−46,2) | −106,5 ± 172,1 (−100,4) |
| B | centrale | −13,4 ± 1,1 (−3,3) | −10,7 ± 1,6 (−0,7) | −16,2 ± 1,9 (−6,1) | −11,0 ± 3,2 (−1,0) |
| B | e0 = −0,5 point | −15,3 ± 1,2 (−5,2) | −13,7 ± 2,0 (−3,7) | −19,6 ± 2,4 (−9,5) | −15,2 ± 4,4 (−5,1) |
| B | collecte 30 ans | −19,5 ± 4,4 (−9,4) | −15,4 ± 7,7 (−5,3) | −37,6 ± 28,6 (−27,6) | −35,4 ± 52,5 (−25,3) |
| B | collecte 60 ans | −25,5 ± 10,0 (−15,4) | −22,3 ± 18,9 (−12,3) | −116,8 ± 155,3 (−106,7) | −195,9 ± 333,6 (−185,9) |
| C | centrale | −12,9 ± 1,1 (−3,1) | −10,3 ± 1,7 (−0,5) | −15,2 ± 2,3 (−5,4) | −10,0 ± 4,1 (−0,2) |
| C | e0 = −0,5 point | −14,7 ± 1,3 (−4,9) | −12,9 ± 2,3 (−3,1) | −18,7 ± 2,8 (−8,9) | −13,9 ± 5,5 (−4,1) |
| C | collecte 30 ans | −21,0 ± 4,6 (−11,2) | −16,7 ± 8,5 (−6,9) | −44,6 ± 35,9 (−34,8) | −46,2 ± 70,4 (−36,4) |
| C | collecte 60 ans | −29,1 ± 10,4 (−19,3) | −25,0 ± 20,8 (−15,2) | −148,1 ± 192,7 (−138,3) | −258,1 ± 445,0 (−248,3) |

- **Taux servi de marge** sous ces hypothèses : A : toujours positif, non robuste (de 2,3 à 99,3) ; B : positif là où il est significatif, non robuste (de −2,6 à 90,8) ; C : change de signe selon les hypothèses (de −7,1 à 10,8).
- **Taux servi compétitif** sous ces hypothèses : A : toujours négatif, non robuste (de −106,5 à −6,9) ; B : toujours négatif, non robuste (de −195,9 à −13,7) ; C : toujours négatif, non robuste (de −258,1 à −12,9).

**Précision.** 27 cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à 445,0), dont 21 à l'intensité forte, toutes avec une collecte de 30 ans ou 60 ans. Sur plusieurs décennies de collecte, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche toute conclusion ; à l'intensité forte, la collecte nette atteint en outre environ 4,6 % de la PM par an quand g est proche de 1 (section 1), ce qui est peu plausible au regard des 0,7 % observés en 2025.

g_min = 0 n'est pas testé : une collecte négative reviendrait à des rachats supplémentaires, que la loi de rachat dynamique traite déjà. La conclusion dépend donc de e0 et de l'horizon de collecte dans la mesure indiquée ci-dessus, et de g_min par construction.

## 5. Les huit stratégies avec collecte

Écart de valeur totale à la gestion passive ± intervalle apparié, intensité centrale, puis robustesse sur toute la grille (trois intensités, cinq élasticités, loi de rachat ONC maximale à l'intensité centrale).

**Profil A**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,4 ± 0,2 | 0,8 ± 0,3 | 0,7 ± 0,3 | 0,6 ± 0,3 | 0,5 ± 0,2 | 0,5 ± 0,2 | 0,2 ± 0,1 | sans effet important |
| Repositionnement | −16,5 ± 1,1 | −20,7 ± 1,3 | −18,7 ± 1,3 | −17,8 ± 1,2 | −17,2 ± 1,1 | −16,7 ± 1,1 | −9,9 ± 0,9 | défavorable, robuste |
| Taux servi compétitif | −6,0 ± 0,4 | −9,4 ± 0,6 | −6,9 ± 0,6 | −6,1 ± 0,8 | −5,4 ± 0,9 | −4,4 ± 1,2 | −1,8 ± 0,7 | toujours négatif, non robuste |
| Taux servi de marge | 5,8 ± 0,4 | 8,3 ± 0,7 | 5,5 ± 0,7 | 4,5 ± 0,8 | 4,3 ± 1,0 | 5,6 ± 0,9 | 3,0 ± 1,1 | toujours positif, non robuste |
| Liquidité défensive | 0,8 ± 1,2 | −3,9 ± 2,0 | −1,6 ± 1,9 | −0,8 ± 1,8 | −0,4 ± 1,6 | 0,3 ± 1,4 | 3,2 ± 0,9 | change de signe selon les hypothèses |
| Compétitif préservant la PPB | −4,1 ± 0,4 | −10,2 ± 0,6 | −7,2 ± 0,6 | −6,2 ± 0,6 | −5,6 ± 0,7 | −4,5 ± 1,0 | −1,6 ± 0,6 | toujours négatif, non robuste |
| Rétention de capital | −1,1 ± 0,1 | −1,7 ± 0,1 | −1,4 ± 0,1 | −1,3 ± 0,1 | −1,3 ± 0,1 | −1,2 ± 0,1 | −0,6 ± 0,1 | sans effet important |

Plus forte valeur totale selon la configuration : Taux servi de marge (16 configurations sur 20), Liquidité défensive (4 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. **Le premier rang change avec les hypothèses.**

**Profil B**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,3 ± 0,3 | 0,6 ± 0,4 | 0,6 ± 0,4 | 0,6 ± 0,3 | 0,6 ± 0,3 | 0,4 ± 0,3 | 0,4 ± 0,2 | sans effet important |
| Repositionnement | −11,7 ± 0,7 | −13,7 ± 0,8 | −12,9 ± 0,9 | −12,5 ± 0,8 | −12,2 ± 0,8 | −11,7 ± 0,8 | −9,4 ± 0,8 | défavorable, robuste |
| Taux servi compétitif | −10,1 ± 0,5 | −17,0 ± 0,8 | −13,4 ± 1,1 | −11,9 ± 1,3 | −10,7 ± 1,6 | −9,1 ± 2,1 | −4,4 ± 1,7 | toujours négatif, non robuste |
| Taux servi de marge | 6,3 ± 0,6 | 7,9 ± 0,9 | 5,0 ± 0,8 | 3,7 ± 0,8 | 3,7 ± 1,0 | 6,1 ± 1,0 | 0,9 ± 1,1 | toujours positif, non robuste |
| Liquidité défensive | 1,2 ± 1,4 | 1,0 ± 1,9 | 0,9 ± 1,9 | 0,9 ± 1,8 | 1,0 ± 1,8 | 1,2 ± 1,6 | 2,9 ± 1,4 | toujours positif, non robuste |
| Compétitif préservant la PPB | −9,5 ± 0,5 | −17,2 ± 0,8 | −13,6 ± 1,1 | −12,3 ± 1,3 | −11,1 ± 1,5 | −9,4 ± 2,0 | −5,0 ± 1,6 | toujours négatif, non robuste |
| Rétention de capital | −1,4 ± 0,1 | −1,9 ± 0,1 | −1,7 ± 0,1 | −1,6 ± 0,1 | −1,6 ± 0,1 | −1,5 ± 0,1 | −1,1 ± 0,0 | toujours négatif, non robuste |

Plus forte valeur totale selon la configuration : Taux servi de marge (15 configurations sur 20), Liquidité défensive (5 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. **Le premier rang change avec les hypothèses.**

**Profil C**

| Stratégie | Portefeuille fermé | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 | ONC max., eta modérée | Robustesse de l'écart de valeur totale |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Réinvestissement progressif | 0,0 ± 0,5 | 0,4 ± 0,8 | 0,2 ± 0,8 | 0,2 ± 0,8 | 0,1 ± 0,7 | 0,1 ± 0,7 | 0,1 ± 0,5 | toujours positif, non robuste |
| Repositionnement | −1,4 ± 0,5 | −2,5 ± 0,6 | −2,4 ± 0,7 | −2,4 ± 0,6 | −2,3 ± 0,6 | −1,8 ± 0,5 | −1,9 ± 0,6 | toujours négatif, non robuste |
| Taux servi compétitif | −9,8 ± 0,7 | −16,8 ± 0,9 | −12,9 ± 1,1 | −11,5 ± 1,3 | −10,3 ± 1,7 | −8,3 ± 2,4 | −3,0 ± 1,8 | toujours négatif, non robuste |
| Taux servi de marge | 3,1 ± 0,7 | 4,0 ± 1,1 | 1,3 ± 0,9 | 0,0 ± 0,9 | 0,3 ± 0,8 | 3,5 ± 0,7 | 0,0 ± 0,8 | change de signe selon les hypothèses |
| Liquidité défensive | 3,1 ± 1,5 | 4,1 ± 2,4 | 3,7 ± 2,3 | 3,5 ± 2,2 | 3,3 ± 2,1 | 3,3 ± 2,0 | 4,0 ± 1,6 | toujours positif, non robuste |
| Compétitif préservant la PPB | −9,8 ± 0,7 | −17,1 ± 0,9 | −13,5 ± 1,1 | −12,0 ± 1,3 | −10,7 ± 1,6 | −8,7 ± 2,3 | −3,5 ± 1,8 | toujours négatif, non robuste |
| Rétention de capital | −1,3 ± 0,1 | −1,8 ± 0,1 | −1,6 ± 0,1 | −1,6 ± 0,1 | −1,5 ± 0,1 | −1,5 ± 0,1 | −1,1 ± 0,1 | toujours négatif, non robuste |

Plus forte valeur totale selon la configuration : Taux servi de marge (3 configurations sur 20), Liquidité défensive (17 configurations sur 20) ; en portefeuille fermé : Taux servi de marge. **Le premier rang change avec les hypothèses.**

## 6. Effet sur l'existant et répartition des garanties

Variation du BE de l'existant, comptée pour l'actionnaire : - (BE de l'existant avec collecte - BE en extinction). Négative : la collecte enrichit les assurés existants (primes placées à des taux supérieurs au rendement comptable, qui relèvent le taux servi commun) ; positive : elle les dilue. Gestion passive, intensité centrale :

| Profil | eta 0,0 | eta 0,5 | eta 0,75 | eta 1,0 | eta 1,5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | −7,1 ± 0,8 | −3,8 ± 0,4 | −2,8 ± 0,3 | −1,9 ± 0,2 | −0,6 ± 0,1 |
| B | −1,6 ± 0,8 | −0,7 ± 0,5 | −0,3 ± 0,4 | −0,1 ± 0,4 | 0,3 ± 0,3 |
| C | 5,2 ± 1,0 | 5,2 ± 0,8 | 5,0 ± 0,8 | 4,7 ± 0,7 | 4,0 ± 0,6 |

**Transferts entre générations d'assurés.** Les contrats nouveaux reçoivent le taux servi commun, donc une part de la PPB d'ouverture et du rendement des obligations anciennes. Quand le taux commun passe sous le TMG de l'existant, l'existant reçoit son TMG et les contrats nouveaux le reste : ils financent alors une partie de la garantie de l'existant. Part des années-scénarios 2 à 10 où les contrats nouveaux sont crédités sous l'existant (intensité centrale, élasticité modérée) : A 28 % en gestion passive, 27 % en politique de marge (écart moyen de 58 pb ces années-là) ; B 8 % en gestion passive, 5 % en politique de marge (écart moyen de 31 pb ces années-là) ; C 0 % en gestion passive, 0 % en politique de marge. Ces transferts apparaissent dans les flux des contrats nouveaux et, en sens inverse, dans la variation du BE de l'existant : ni l'un ni l'autre terme ne les isole, seule la valeur des affaires nouvelles (leur somme) est interprétable.

## 7. Probabilité réelle (intensité centrale)

Indicateurs non actualisés, conditionnels aux hypothèses (taux sans prime de terme, prime actions fictive, défauts aux probabilités réelles), base 100 %, c0 = 6 %. Sorties nettes : prestations et frais moins primes, rapportés à la PM de début d'année ; quantile 99 % du maximum sur 10 ans. Probabilité d'apport : sur tout l'horizon de projection (60 ans). Écart du taux servi : moyenne du fonds (tous contrats) et contrats nouveaux, ceux qui déterminent la collecte.

**Profil A**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 715 | 4,4 % | 109,2 | 104,4 | 1,0 % | −66 pb / - | 74,8 | 35,6 % |
| Passive | 0,0 | 684,6 | 1 340 | 5,0 % | 52,6 | 195,7 | 0,2 % | −52 pb / −52 pb | 3,0 | 10,7 % |
| Passive | 0,5 | 448,8 | 1 138 | 4,8 % | 71,8 | 166,2 | 0,2 % | −56 pb / −56 pb | 38,8 | 29,0 % |
| Passive | 0,75 | 341,5 | 1 052 | 4,7 % | 80,7 | 153,6 | 0,2 % | −58 pb / −59 pb | 51,5 | 33,2 % |
| Passive | 1,0 | 247,4 | 966 | 4,6 % | 88,6 | 141,1 | 0,4 % | −61 pb / −61 pb | 57,1 | 33,7 % |
| Passive | 1,5 | 109,9 | 823 | 4,5 % | 99,9 | 120,1 | 0,7 % | −65 pb / −66 pb | 72,5 | 35,6 % |
| Taux servi de marge | fermé | 0,0 | 666 | 4,5 % | 120,2 | 101,2 | 0,7 % | −94 pb / - | 101,5 | 35,6 % |
| Taux servi de marge | 0,0 | 653,7 | 1 218 | 5,1 % | 70,9 | 185,3 | 0,1 % | −91 pb / −91 pb | 2,5 | 11,8 % |
| Taux servi de marge | 0,5 | 309,5 | 922 | 4,8 % | 98,1 | 140,1 | 0,4 % | −93 pb / −93 pb | 66,4 | 33,5 % |
| Taux servi de marge | 0,75 | 173,5 | 798 | 4,6 % | 108,4 | 121,3 | 0,6 % | −94 pb / −95 pb | 81,0 | 35,6 % |
| Taux servi de marge | 1,0 | 87,0 | 709 | 4,5 % | 114,8 | 107,8 | 0,7 % | −95 pb / −96 pb | 90,4 | 35,6 % |
| Taux servi de marge | 1,5 | 46,9 | 677 | 4,5 % | 117,2 | 102,9 | 0,6 % | −95 pb / −96 pb | 98,2 | 35,6 % |
| Taux servi compétitif | fermé | 0,0 | 713 | 4,3 % | 102,9 | 96,0 | 1,6 % | −53 pb / - | 94,7 | 35,6 % |
| Taux servi compétitif | 0,0 | 693,1 | 1 377 | 4,8 % | 42,6 | 185,3 | 0,2 % | −20 pb / −20 pb | 3,6 | 12,4 % |
| Taux servi compétitif | 0,5 | 559,7 | 1 273 | 4,7 % | 54,7 | 171,4 | 0,2 % | −26 pb / −26 pb | 48,7 | 32,1 % |
| Taux servi compétitif | 0,75 | 494,3 | 1 218 | 4,7 % | 60,7 | 163,9 | 0,3 % | −30 pb / −30 pb | 60,4 | 33,2 % |
| Taux servi compétitif | 1,0 | 438,7 | 1 158 | 4,6 % | 65,7 | 155,8 | 0,5 % | −33 pb / −33 pb | 62,2 | 35,6 % |
| Taux servi compétitif | 1,5 | 360,5 | 1 058 | 4,6 % | 72,3 | 142,2 | 0,7 % | −37 pb / −38 pb | 70,8 | 35,6 % |
| Compétitif préservant la PPB | fermé | 0,0 | 725 | 4,2 % | 104,6 | 104,8 | 1,2 % | −48 pb / - | 82,2 | 35,6 % |
| Compétitif préservant la PPB | 0,0 | 691,7 | 1 379 | 4,6 % | 41,4 | 199,4 | 0,2 % | −21 pb / −21 pb | 5,5 | 11,9 % |
| Compétitif préservant la PPB | 0,5 | 552,2 | 1 267 | 4,5 % | 53,7 | 183,2 | 0,2 % | −27 pb / −27 pb | 39,9 | 30,2 % |
| Compétitif préservant la PPB | 0,75 | 481,1 | 1 207 | 4,5 % | 60,2 | 174,5 | 0,2 % | −30 pb / −31 pb | 59,8 | 33,1 % |
| Compétitif préservant la PPB | 1,0 | 416,9 | 1 146 | 4,4 % | 66,0 | 165,7 | 0,4 % | −34 pb / −34 pb | 70,2 | 33,4 % |
| Compétitif préservant la PPB | 1,5 | 327,3 | 1 038 | 4,3 % | 74,0 | 149,9 | 0,7 % | −39 pb / −39 pb | 78,2 | 35,6 % |

**Profil B**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 753 | 8,5 % | 87,0 | 58,4 | 0,3 % | −31 pb / - | 4,9 | 15,1 % |
| Passive | 0,0 | 688,7 | 1 360 | 8,9 % | 67,2 | 105,5 | 0,4 % | −41 pb / −41 pb | 0,0 | 2,4 % |
| Passive | 0,5 | 508,7 | 1 180 | 8,8 % | 72,7 | 91,5 | 0,4 % | −39 pb / −39 pb | 0,1 | 8,0 % |
| Passive | 0,75 | 427,3 | 1 095 | 8,7 % | 75,1 | 85,0 | 0,4 % | −39 pb / −39 pb | 0,8 | 10,7 % |
| Passive | 1,0 | 351,3 | 1 021 | 8,7 % | 77,3 | 79,2 | 0,4 % | −39 pb / −39 pb | 2,7 | 12,0 % |
| Passive | 1,5 | 229,4 | 896 | 8,6 % | 80,6 | 69,5 | 0,4 % | −38 pb / −38 pb | 4,4 | 14,5 % |
| Taux servi de marge | fermé | 0,0 | 722 | 8,9 % | 86,4 | 53,3 | 0,4 % | −39 pb / - | 11,2 | 13,5 % |
| Taux servi de marge | 0,0 | 664,3 | 1 283 | 9,3 % | 70,0 | 94,8 | 0,4 % | −56 pb / −56 pb | 0,0 | 5,3 % |
| Taux servi de marge | 0,5 | 431,9 | 1 093 | 9,1 % | 75,2 | 80,7 | 0,4 % | −53 pb / −53 pb | 3,8 | 11,1 % |
| Taux servi de marge | 0,75 | 335,6 | 1 014 | 9,0 % | 77,0 | 74,9 | 0,4 % | −52 pb / −52 pb | 10,9 | 12,3 % |
| Taux servi de marge | 1,0 | 270,6 | 953 | 8,9 % | 78,3 | 70,4 | 0,3 % | −50 pb / −50 pb | 12,1 | 12,4 % |
| Taux servi de marge | 1,5 | 237,8 | 916 | 8,9 % | 79,1 | 67,6 | 0,3 % | −49 pb / −49 pb | 11,9 | 12,6 % |
| Taux servi compétitif | fermé | 0,0 | 768 | 8,2 % | 84,2 | 58,7 | 0,4 % | −7 pb / - | 7,2 | 21,5 % |
| Taux servi compétitif | 0,0 | 701,8 | 1 406 | 8,5 % | 60,0 | 107,5 | 0,4 % | −2 pb / −2 pb | 0,0 | 5,9 % |
| Taux servi compétitif | 0,5 | 666,0 | 1 382 | 8,4 % | 61,1 | 105,6 | 0,4 % | −3 pb / −3 pb | 0,0 | 11,4 % |
| Taux servi compétitif | 0,75 | 648,0 | 1 372 | 8,4 % | 61,6 | 104,9 | 0,4 % | −3 pb / −3 pb | 0,7 | 13,0 % |
| Taux servi compétitif | 1,0 | 630,6 | 1 362 | 8,4 % | 62,2 | 104,1 | 0,4 % | −4 pb / −4 pb | 0,9 | 13,8 % |
| Taux servi compétitif | 1,5 | 601,3 | 1 335 | 8,3 % | 63,0 | 102,0 | 0,4 % | −4 pb / −4 pb | 1,9 | 14,4 % |
| Compétitif préservant la PPB | fermé | 0,0 | 770 | 8,1 % | 83,1 | 59,5 | 0,4 % | −6 pb / - | 7,1 | 18,1 % |
| Compétitif préservant la PPB | 0,0 | 700,9 | 1 407 | 8,3 % | 59,1 | 108,7 | 0,4 % | −3 pb / −3 pb | 0,0 | 5,1 % |
| Compétitif préservant la PPB | 0,5 | 661,3 | 1 377 | 8,3 % | 60,0 | 106,4 | 0,4 % | −4 pb / −4 pb | 0,5 | 11,3 % |
| Compétitif préservant la PPB | 0,75 | 641,2 | 1 366 | 8,2 % | 60,5 | 105,6 | 0,4 % | −4 pb / −4 pb | 2,0 | 13,1 % |
| Compétitif préservant la PPB | 1,0 | 621,3 | 1 353 | 8,2 % | 61,0 | 104,6 | 0,4 % | −4 pb / −4 pb | 2,6 | 13,7 % |
| Compétitif préservant la PPB | 1,5 | 585,3 | 1 323 | 8,2 % | 61,9 | 102,2 | 0,4 % | −5 pb / −5 pb | 3,0 | 13,9 % |

**Profil C**

| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Passive | fermé | 0,0 | 781 | 11,9 % | 88,3 | 46,9 | 0,6 % | 0 pb / - | 19,9 | 13,2 % |
| Passive | 0,0 | 692,3 | 1 385 | 12,0 % | 76,3 | 83,1 | 0,6 % | −22 pb / −22 pb | 0,6 | 1,2 % |
| Passive | 0,5 | 584,7 | 1 254 | 11,9 % | 78,0 | 75,2 | 0,6 % | −21 pb / −21 pb | 2,6 | 6,0 % |
| Passive | 0,75 | 532,7 | 1 212 | 11,8 % | 78,8 | 72,7 | 0,6 % | −20 pb / −20 pb | 5,4 | 8,4 % |
| Passive | 1,0 | 482,5 | 1 176 | 11,8 % | 79,5 | 70,6 | 0,5 % | −19 pb / −19 pb | 10,7 | 8,9 % |
| Passive | 1,5 | 400,6 | 1 110 | 11,8 % | 80,5 | 66,6 | 0,5 % | −17 pb / −17 pb | 17,8 | 12,4 % |
| Taux servi de marge | fermé | 0,0 | 764 | 11,9 % | 88,4 | 45,9 | 0,6 % | −2 pb / - | 39,2 | 14,7 % |
| Taux servi de marge | 0,0 | 674,4 | 1 336 | 12,0 % | 77,1 | 80,2 | 0,5 % | −29 pb / −29 pb | 3,7 | 5,0 % |
| Taux servi de marge | 0,5 | 545,3 | 1 238 | 11,9 % | 77,7 | 74,3 | 0,5 % | −26 pb / −26 pb | 24,1 | 11,0 % |
| Taux servi de marge | 0,75 | 486,6 | 1 199 | 11,8 % | 77,9 | 71,9 | 0,5 % | −25 pb / −25 pb | 38,0 | 13,5 % |
| Taux servi de marge | 1,0 | 447,9 | 1 168 | 11,8 % | 78,1 | 70,1 | 0,5 % | −23 pb / −23 pb | 40,1 | 13,5 % |
| Taux servi de marge | 1,5 | 445,0 | 1 163 | 11,8 % | 78,4 | 69,8 | 0,5 % | −23 pb / −23 pb | 40,1 | 13,5 % |
| Taux servi compétitif | fermé | 0,0 | 788 | 11,6 % | 87,0 | 47,3 | 1,2 % | 13 pb / - | 24,9 | 19,5 % |
| Taux servi compétitif | 0,0 | 703,5 | 1 419 | 11,5 % | 72,7 | 85,1 | 1,0 % | 5 pb / 5 pb | 0,6 | 3,4 % |
| Taux servi compétitif | 0,5 | 707,3 | 1 412 | 11,5 % | 72,7 | 84,7 | 1,0 % | 4 pb / 4 pb | 1,1 | 9,1 % |
| Taux servi compétitif | 0,75 | 706,8 | 1 409 | 11,5 % | 72,8 | 84,5 | 1,0 % | 4 pb / 4 pb | 1,9 | 11,5 % |
| Taux servi compétitif | 1,0 | 705,6 | 1 409 | 11,4 % | 72,9 | 84,5 | 1,0 % | 3 pb / 3 pb | 2,8 | 12,1 % |
| Taux servi compétitif | 1,5 | 703,8 | 1 407 | 11,4 % | 73,0 | 84,4 | 1,0 % | 3 pb / 3 pb | 4,8 | 12,6 % |
| Compétitif préservant la PPB | fermé | 0,0 | 788 | 11,5 % | 86,8 | 47,6 | 1,1 % | 13 pb / - | 25,9 | 24,1 % |
| Compétitif préservant la PPB | 0,0 | 703,4 | 1 418 | 11,4 % | 72,2 | 85,7 | 0,9 % | 5 pb / 5 pb | 0,6 | 3,2 % |
| Compétitif préservant la PPB | 0,5 | 707,0 | 1 411 | 11,4 % | 72,2 | 85,3 | 0,9 % | 4 pb / 4 pb | 1,1 | 7,8 % |
| Compétitif préservant la PPB | 0,75 | 706,3 | 1 408 | 11,3 % | 72,2 | 85,1 | 0,9 % | 4 pb / 4 pb | 2,1 | 10,5 % |
| Compétitif préservant la PPB | 1,0 | 704,8 | 1 406 | 11,3 % | 72,3 | 85,0 | 0,9 % | 3 pb / 3 pb | 3,6 | 11,3 % |
| Compétitif préservant la PPB | 1,5 | 702,0 | 1 404 | 11,3 % | 72,5 | 84,9 | 0,8 % | 3 pb / 3 pb | 4,8 | 12,7 % |

Autres stratégies : `resultats/v5_collecte.json`, rubrique `reel`. Les sorties nettes maximales identiques d'une ligne à l'autre pour A correspondent au plafond de la loi de rachat dynamique, atteint dans les scénarios les plus défavorables.

**Liquidité** (gestion passive, élasticité modérée) : A : moins-values réalisées q99 74,8 en extinction, 38,8 avec collecte ; sorties nettes max. q99 35,6 % et 29,0 % ; B : moins-values réalisées q99 4,9 en extinction, 0,1 avec collecte ; sorties nettes max. q99 15,1 % et 8,0 % ; C : moins-values réalisées q99 19,9 en extinction, 2,6 avec collecte ; sorties nettes max. q99 13,2 % et 6,0 %. Les primes financent une partie des sorties et réduisent les ventes d'obligations en moins-value.

**Écart de taux servi effectivement réalisé** entre la politique de marge et la gestion passive (moyenne du fonds, années 1 à 10, élasticité modérée) : −37 pb (A), −14 pb (B), −5 pb (C), bien moins que le point d'écart des cibles : la participation minimale (compte de participation simplifié) et les reprises de PPB limitent la baisse effective du taux servi, donc la perte de collecte.

## 8. Capital

- **Besoin à l'ouverture** : inchangé par la collecte, par construction (vue prudentielle simplifiée en extinction, section 1). Apports à 100 % : A : passive 101,0, taux servi de marge 107,1, taux servi compétitif 89,6, compétitif préservant la PPB 99,6 ; B : passive 27,6, taux servi de marge 23,9, taux servi compétitif 26,4, compétitif préservant la PPB 27,3 ; C : passive 0,0, taux servi de marge 0,0, taux servi compétitif 0,0, compétitif préservant la PPB 0,4.
- **Capital retenu par la croissance** (gestion passive, élasticité modérée, probabilité réelle) : la politique de distribution maintient les fonds propres à leur cible en % de la PM ; la croissance de la PM retient donc du capital et réduit les dividendes. A : fonds propres médians à 10 ans 104,4 en extinction, 166,2 avec collecte ; dividendes 1-10 109,2 et 71,8 ; B : fonds propres médians à 10 ans 58,4 en extinction, 91,5 avec collecte ; dividendes 1-10 87,0 et 72,7 ; C : fonds propres médians à 10 ans 46,9 en extinction, 75,2 avec collecte ; dividendes 1-10 88,3 et 78,0.
- **Capital de la croissance, ordre de grandeur** : en supposant le SCR simplifié proportionnel à la PM, au ratio d'ouverture de chaque stratégie (SCR à 100 % de couverture / PM d'ouverture), l'écart de PM médiane à 10 ans entre la collecte centrale et l'extinction (probabilité réelle) demanderait le SCR supplémentaire ci-dessous. Ce n'est pas une projection du SCR : le profil de risque change avec la duration, la PPB, les plus-values latentes et l'allocation. SCR à 100 % : contrôle direct quand il existe, sinon interpolation linéaire en fonction de l'apport, comme pour le besoin d'apport de la consolidation.

| Profil | Stratégie | Apport à l'ouverture (écart à la gestion passive) | SCR / PM d'ouverture | SCR supplémentaire à 10 ans : eta 0,0 / 0,5 / 0,75 / 1,0 / 1,5 | Écart à la gestion passive, eta modérée |
| --- | --- | ---: | ---: | ---: | ---: |
| A | Passive | 101,0 (-) | 10,5 % | 65,9 / 44,6 / 35,5 / 26,5 / 11,3 | - |
| A | Réinvestissement progressif | 101,7 (0,7) | 10,7 % | 66,6 / 45,0 / 35,8 / 26,7 / 11,4 | 0,4 |
| A | Repositionnement | 120,3 (19,2) | 9,9 % | 54,7 / 31,3 / 25,5 / 19,7 / 10,2 | −13,3 |
| A | Taux servi compétitif | 89,6 (−11,4) | 9,0 % | 59,5 / 50,2 / 45,2 / 39,9 / 30,9 | 5,6 |
| A | Taux servi de marge | 107,1 (6,1) | 11,6 % | 64,1 / 29,7 / 15,3 / 5,0 / 1,3 | −14,9 |
| A | Liquidité défensive | 114,5 (13,5) | 11,8 % | 72,5 / 49,5 / 38,8 / 27,6 / 10,1 | 4,9 |
| A | Compétitif préservant la PPB | 99,6 (−1,4) | 9,8 % | 64,3 / 53,2 / 47,3 / 41,4 / 30,7 | 8,6 |
| A | Rétention de capital | 100,7 (−0,4) | 10,4 % | 64,7 / 43,8 / 34,9 / 26,0 / 11,2 | −0,8 |
| B | Passive | 27,6 (-) | 9,4 % | 57,3 / 40,4 / 32,4 / 25,3 / 13,5 | - |
| B | Réinvestissement progressif | 27,4 (−0,1) | 9,5 % | 57,3 / 40,3 / 32,3 / 25,4 / 13,4 | −0,1 |
| B | Repositionnement | 47,7 (20,1) | 9,8 % | 56,4 / 42,6 / 35,3 / 30,8 / 25,1 | 2,2 |
| B | Taux servi compétitif | 26,4 (−1,1) | 8,6 % | 54,6 / 52,5 / 51,7 / 50,9 / 48,5 | 12,2 |
| B | Taux servi de marge | 23,9 (−3,7) | 9,3 % | 52,3 / 34,6 / 27,2 / 21,6 / 18,1 | −5,8 |
| B | Liquidité défensive | 28,4 (0,8) | 9,6 % | 58,3 / 41,1 / 33,0 / 25,8 / 13,5 | 0,7 |
| B | Compétitif préservant la PPB | 27,3 (−0,3) | 8,4 % | 53,4 / 50,9 / 50,0 / 48,9 / 46,4 | 10,5 |
| B | Rétention de capital | 27,9 (0,4) | 9,4 % | 57,3 / 40,3 / 32,3 / 25,3 / 13,5 | −0,1 |
| C | Passive | 0,0 (-) | 8,4 % | 50,7 / 39,6 / 36,1 / 33,1 / 27,6 | - |
| C | Réinvestissement progressif | 0,0 (0,0) | 8,4 % | 50,7 / 39,4 / 35,9 / 32,9 / 27,1 | −0,2 |
| C | Repositionnement | 2,2 (2,2) | 8,6 % | 52,6 / 42,4 / 39,8 / 37,1 / 30,9 | 2,8 |
| C | Taux servi compétitif | 0,0 (0,0) | 8,0 % | 50,6 / 50,1 / 49,9 / 49,8 / 49,7 | 10,4 |
| C | Taux servi de marge | 0,0 (0,0) | 7,9 % | 45,3 / 37,6 / 34,5 / 32,0 / 31,6 | −2,1 |
| C | Liquidité défensive | 0,0 (0,0) | 8,6 % | 51,3 / 39,5 / 35,4 / 32,1 / 26,8 | −0,1 |
| C | Compétitif préservant la PPB | 0,4 (0,4) | 8,1 % | 50,8 / 50,3 / 50,0 / 49,8 / 49,7 | 10,6 |
| C | Rétention de capital | 0,0 (0,0) | 8,4 % | 50,9 / 39,9 / 36,3 / 33,3 / 27,8 | 0,2 |

  La croissance demande un capital du même ordre que l'apport d'ouverture de B et C (eta modérée), et il dépend d'abord de l'élasticité. Pour Repositionnement (A : 19,2 à l'ouverture, −13,3 pour la croissance), Taux servi compétitif (A : −11,4 à l'ouverture, 5,6 pour la croissance), Taux servi de marge (A : 6,1 à l'ouverture, −14,9 pour la croissance), l'écart de capital à l'ouverture et l'écart de capital de la croissance vont en sens contraire : la comparaison des besoins à l'ouverture ne suffit pas à classer les stratégies en capital. La politique de distribution retient des fonds propres comptables au ratio d'ouverture (point précédent) : ce SCR supplémentaire n'appelle donc pas un apport du même montant, mais fonds propres comptables et fonds propres prudentiels ne coïncident pas (plus ou moins-values latentes, marge de risque, absorption par les provisions techniques, impôts différés).
- **Seuil de coût du capital des affaires nouvelles** (analyse de seuil, aucun coût retenu ; gestion passive, collecte centrale, eta modérée, mêmes scénarios risque neutre que la valeur publiée). Capital proxy, scénario par scénario : K(t) = SCR à 100 % / PM d'ouverture x (PM avec collecte - PM en extinction). Une charge frictionnelle kappa x K(t - 1), payée en fin d'année t et actualisée au déflateur, réduit la valeur des affaires nouvelles de kappa x S, avec S = somme sur t de E[D(t) K(t - 1)] ; le seuil kappa* = valeur / S est la charge annuelle qui l'annulerait. kappa est une charge supplémentaire hypothétique, nette des coûts déjà valorisés (impôt et participation sur les revenus du capital comptable retenu) : ce n'est ni le rendement exigé en probabilité réelle, ni le taux de la marge de risque Solvabilité II, qui ont d'autres usages (`docs/V5_METHODOLOGIE.md`, section 3).

| Profil | Valeur des affaires nouvelles ± IC 95 % | SCR / PM d'ouverture | S, VA du capital proxy | kappa* | kappa* aux bornes de l'intervalle |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 6,2 ± 2,5 | 10,5 % | 312 | 2,0 % | 1,2 % à 2,8 % |
| B | 8,6 ± 3,0 | 9,4 % | 423 | 2,0 % | 1,3 % à 2,7 % |
| C | 10,7 ± 3,2 | 8,4 % | 427 | 2,5 % | 1,8 % à 3,3 % |

  Lecture : une charge frictionnelle supérieure à environ 2,0 % à 2,5 % par an du capital proxy suffirait à annuler la valeur centrale des affaires nouvelles. Le seuil hérite des limites du proxy (SCR proportionnel à la PM, au ratio d'ouverture) et ne dit pas quelle charge est la bonne.
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

