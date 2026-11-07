# V5 : registre des données et des hypothèses

Généré par `scripts/v5_registre_hypotheses.py` à partir des seuls fichiers de `data/` : chaque valeur, chaque statut et chaque source sont recopiés tels qu'ils figurent dans ces fichiers. Pour modifier une hypothèse, on modifie le fichier de données, puis on relance les calculs concernés (`docs/V5_REPRODUCTION.md`).

**Statuts.** *Observé* : publié par une source officielle, daté, référencé. *Calibré* : choisi pour reproduire un ordre de grandeur observé, avec sa règle. *Hypothèse* : choix de modélisation justifié mais non observé. *Fictif* : sans ancrage, testé en sensibilité quand il conduit les conclusions. Les trois profils d'assureur sont fictifs : ils ne décrivent aucun organisme réel. Unité : 1 unité = 10 M€.

## 1. Données de marché au 31/10/2026

**Courbe sans risque EIOPA** (observé) : EIOPA, Risk-free interest rate term structures, publication mensuelle, date de référence 2026-10-31, publiée le 2026-11-05 ; identifiant `EUR_31_10_2026_SWP_LLP_20_EXT_40_UFR_3.30` ; archive `EIOPA_RFR_20261031.zip`, empreinte SHA-256 `fb2295695c42c874f1d851b81e3cc7519d47fd866b3eb3c5fd31dbb0a498a490`. Taux zéro-coupon actuariels (composition annuelle), maturités 1 à 150 ans, en décimal. Paramètres : UFR 3,3 %, LLP 20 ans, convergence 40 ans, ajustement pour risque de crédit 10 pb, correction pour volatilité 20 pb (alpha 0,068369 sans VA, 0,05 avec VA). Fichier : `data/v5/marche/eiopa_rfr_20261031_eur.csv`.

| Maturité | Sans VA | Avec VA |
| --- | --- | --- |
| 1 an | 3,14 % | 3,34 % |
| 2 ans | 3,27 % | 3,47 % |
| 5 ans | 3,29 % | 3,49 % |
| 10 ans | 3,35 % | 3,55 % |
| 20 ans | 3,36 % | 3,55 % |
| 30 ans | 3,30 % | 3,48 % |
| 50 ans | 3,28 % | 3,41 % |

**Taux de l'État français** (observé) : TEC du 04/11/2026, oblig.fr, relevé du 04/11/2026.

| Maturité | 2 ans | 5 ans | 10 ans | 15 ans | 20 ans | 30 ans |
| --- | --- | --- | --- | --- | --- | --- |
| TEC | 3,64 % | 4,24 % | 4,88 % | 5,17 % | 5,30 % | 5,41 % |
| Spread par bootstrap du TEC (convention centrale des résultats finaux) | 0,35 % | 0,95 % | 1,59 % | 1,88 % | 2,08 % | 2,28 % |
| Spread avec le TEC pris comme zéro-coupon (convention initiale) | 0,35 % | 0,92 % | 1,47 % | 1,70 % | 1,86 % | 2,02 % |

Spreads en composition continue au-dessus de la courbe EIOPA sans VA. **Convention centrale** (crédit `k70_granulaire_correle`, résultats finaux) : spread par bootstrap (calibré) : TEC interpolés linéairement entre les maturités observées (2, 5, 10, 15, 20 et 30 ans), coupons annuels, bootstrap des prix zéro-coupon ; s(k) = ln(1 + z_OAT(k)) - ln(1 + r_EIOPA(k)) ; plat en dessous de 2 ans et au-delà de 30 ans. **Convention initiale** (bilans initiaux et premières comparaisons de conventions, `docs/V5_CONVENTIONS.md`) : s(k) = ln(1 + TEC_k) - ln(1 + r_EIOPA(k)), le TEC (taux de rendement au pair) étant pris comme taux zéro-coupon OAT : approximation, l'écart reste faible sur une courbe peu pentue (calibré). TEC du 04/11/2026, courbe EIOPA du 31/10/2026 (un samedi : elle reflète les marchés du 30/10) : décalage de trois jours ouvrés, assumé ; le TEC du 30/10/2026 n'a pas été relevé, ce qui mêle deux dates de marché. Interpolation : linéaire entre les points, plate au-delà (2 ans en dessous, 30 ans au-dessus). Usage : prix de marché des obligations détenues ; en risque neutre, intensité de perte cumulée H(u) = s(u) x u.

## 2. Profils d'assureur (fictifs)

Trois profils d'assureur-vie FICTIFS, construits pour étudier comment la stratégie ALM dépend du bilan initial. Aucun ne représente un organisme réel ; leurs ordres de grandeur sont confrontés aux publications de place (data/v5/profils/confrontation_acpr.md). Date d'arrêté : 2026-10-31. Unité monétaire (fictif) : 1 unité = 10 M EUR, soit une PM de 10 Md EUR ; sert aux seuils fiscaux exprimés en euros.

| Profil | PM | PPB | Réserve de capitalisation | Fonds propres | TMG moyen | Taux servi initial | Obligations / actions / monétaire | Plus-values latentes actions | Maturité de réinvestissement | Générations d'obligations (part, maturités résiduelles) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A** : Assureur historique sous pression | 1 000 | 25 | 5 | 45 | 0,60 % | 2,30 % | 88 % / 8 % / 4 % | 5 % | 10 ans | avant-2012 12 % (2 à 10 ans), 2012-2014 15 % (2 à 8 ans), 2015-2021 50 % (4 à 18 ans), 2022-2023 13 % (7 à 12 ans), 2024-2025 10 % (9 à 12 ans) |
| **B** : Assureur intermédiaire | 1 000 | 40 | 15 | 50 | 0,32 % | 2,63 % | 85 % / 10 % / 5 % | 10 % | 10 ans | avant-2012 8 % (2 à 8 ans), 2012-2014 12 % (2 à 8 ans), 2015-2021 35 % (3 à 14 ans), 2022-2023 20 % (7 à 12 ans), 2024-2025 20 % (8 à 11 ans), 2026 5 % (9 à 11 ans) |
| **C** : Assureur plus récemment investi | 1 000 | 20 | 5 | 60 | 0,00 % | 3,00 % | 82 % / 12 % / 6 % | 6 % | 12 ans | 2015-2021 5 % (3 à 8 ans), 2022-2023 25 % (7 à 12 ans), 2024-2025 40 % (8 à 12 ans), 2026 30 % (10 à 15 ans) |

- **A** : Portefeuille obligataire ancien, investi massivement entre 2015 et 2021 à faibles coupons et à longue maturité ; réserves (PPB, réserve de capitalisation) en partie consommées ; garanties anciennes plus élevées ; liquidité faible.
- **B** : Générations d'obligations mélangées ; réserves et liquidité modérées, proches des ordres de grandeur de place (PPB, taux technique, chargements, taux servi 2025).
- **C** : Portefeuille constitué surtout depuis 2022, à coupons plus élevés et moins de moins-values ; réserves encore faibles ; contrats sans taux garanti ; politique de taux servi plus offensive (collecte nouvelle : docs/V5_COLLECTE.md).

**Statut des paramètres de profil** : *observé (marché)* : PPB de B (4,0 % des provisions, ACPR n° 180), taux technique de B (0,32 %), taux servi initial de B (2,63 %), chargements (0,63 %) ; *calibré* : coupons par génération, spread, taux de référence des assurés ; *fictif* : tout le reste : PM, répartition des générations et des maturités, réserves de A et C, fonds propres, allocations, plus-values actions, garanties de A et C, taux servis de A et C.

**Coupons d'achat par génération** : Coupon d'achat au pair d'une génération d'obligations, pris égal à l'ordre de grandeur du rendement de l'OAT 10 ans de la période. Statut calibré : ancrage sur des observations mensuelles ponctuelles de la série BCE IRS.M.FR.L.L40.CI.0000.EUR.N.Z (Banque de France), reprises par eco3min.fr (consulté le 06/11/2026), et non sur des moyennes annuelles officielles, non consultées. Les titres achetés à 15 ou 20 ans ont en pratique un coupon un peu supérieur : limite documentée, testée en sensibilité.

| Génération | Coupon | Statut | Observations |
| --- | --- | --- | --- |
| avant-2012 | 3,50 % | calibré | 08/2010 : 2,68 % ; 04/2011 : 3,69 % ; 11/2011 : 3,41 % ; moyenne des années 2000 : 4,28 % |
| 2012-2014 | 1,80 % | calibré | 07/2012 : 2,28 % ; 12/2014 : 0,92 % |
| 2015-2021 | 0,50 % | calibré | 08/2019 : -0,34 % ; 01/2022 : 0,31 % ; moyenne des années 2010 : 1,59 % (inclut 2010-2014) |
| 2022-2023 | 2,80 % | calibré | 10/2022 : 2,77 % ; 10/2023 : 3,45 % |
| 2024-2025 | 3,00 % | calibré | 12/2024 : 3,01 % |
| 2026 | 4,20 % | calibré | 02/2026 : 3,40 % ; 08/2026 : 4,00 % ; 09/2026 : 4,44 % ; TEC 10 du 04/11/2026 : 4,88 % |

Prime d'achat : 0,60 % (calibré) : Les assureurs achètent des maturités plus longues que 10 ans et une majorité d'obligations d'entreprises et financières (59 % des placements en obligations mi-2025, dont 20 % de souverains, ACPR n° 177) : leur rendement d'achat dépasse l'OAT 10 ans. Prime de 0,6 point retenue pour que le profil intermédiaire B retrouve un rendement comptable de l'ordre de celui de la place (rendement de l'actif de 2,8 % en 2025, ACPR n° 180, actions et immobilier compris). Sensibilités de -40 à +20 pb sur toutes les générations.

**Paramètres communs aux trois profils** :

- crédit : calibré : TEC du 04/11/2026 au-dessus de la courbe EIOPA sans VA ; les obligations du modèle représentent l'ensemble du portefeuille obligataire (souverains et entreprises), simplification documentée ;
- référence des assurés (ancienne convention) : calibré : taux de référence des assurés = OAT 10 ans - 2 points, pour situer la référence vers 2,9 %, ordre de grandeur des taux servis attendus en 2026 (2,8 % à 2,9 %, estimations de place, Meilleurtaux 04/09/2026), cohérent avec la collecte nette positive observée sur l'euro (+10,9 Md EUR de janvier à septembre 2026, France Assureurs). Hypothèse la plus incertaine : sensibilités de 0 à -3 points et livret A fixe ;
- chargements sur encours : 0,63 %, observé (marché) : 0,63 %, ACPR, Analyses et synthèses n° 180 (2026), exercice 2025 ;
- frais de gestion : fictif : 0,4 % de l'encours (valeur des V1 à V4).

## 3. Paramètres du moteur hérités des V1 à V4

Fichier `data/hypotheses.json`. Les profils remplacent le bilan, l'allocation, les garanties et les chargements ; la convention centrale de la V5 remplace le rachat structurel (section 4). Les autres paramètres sont repris tels quels.

| Paramètre | Valeur | Statut |
| --- | --- | --- |
| Horizon de projection | 60 ans | hypothèse V1 à V4 |
| Taux de décès | 1,00 % | fictif (V1 à V4) |
| Frais de gestion sur encours | 0,40 % | fictif (V1 à V4) |
| Rachat structurel des V1 à V4 (remplacé en V5) | 5,00 % | hypothèse V1 à V4 |
| Loi de rachat dynamique (paliers, ACPR 2013) | alpha −4,00 %, beta −1,00 %, gamma 1,00 %, delta 3,00 %, RC max 30 %, RC min −5 % | paramètres centraux fixés dans les V1 à V4 ; corridors ONC de 2013 en sensibilité |
| Écart du taux servi visé à la référence (gestion passive) | −0,50 % | fictif (V1 à V4) |
| Participation minimale aux produits financiers | 85 % | règle réglementaire, simplifiée (produits afférents aux provisions) |
| Durée maximale de la PPB, reprise annuelle maximale, plafond | 8 ans, 25 %, 6 % de la PM | durée réglementaire ; reprise et plafond fictifs |
| Générateur de scénarios | Hull-White a = 0,05, sigma = 0,01 ; volatilité actions 18 % ; 1 000 scénarios, graine 2026 | fictif (V1 à V4), calé sur la courbe de la base |
| Rendement de dividende des actions | 2,00 % | fictif (V1 à V4) |

## 4. Conventions de crédit, de comportement et de probabilité réelle

Fichier `data/v5/conventions/conventions.json` (Conventions de crédit et de comportement des assurés comparées en V5 (docs/V5_CONVENTIONS.md). Chaque paramètre porte un statut : observé (chiffre publié repris tel quel), calibré (dérivé de chiffres publiés par une règle écrite), hypothèse (choix de modélisation justifié, non observé), fictif (sans ancrage, testé en sensibilité)). Comparaison chiffrée : `docs/V5_CONVENTIONS.md`. Chaque ligne porte le statut écrit dans le fichier.

**Convention centrale des résultats finaux** (`scripts/v5_consolidation.py`, `scripts/v5_collecte.py`) : crédit `k70_granulaire_correle` (70 % du spread en défaut par saut, 50 blocs corrélés, recouvrement 40 %, spread par bootstrap) ; référence des assurés `taux_servi_marche` (taux sans risque 10 ans lissé sur 7 ans, niveau initial 2,88 %) ; rachat structurel converti du taux ACPR de 4,4 % ; valorisation sur la base sans VA, vue prudentielle sur la base avec VA. Les autres lignes sont des sensibilités.

| Entrée | Valeurs | Statut | Source ou règle |
| --- | --- | --- | --- |
| observations.spread_oat_sur_eiopa | 5_ans : 0,00917 ; 10_ans : 0,01471 ; 30_ans : 0,02024 | calibré | data/v5/marche/spread_oat_20261104.json (TEC du 04/11/2026 au-dessus de la courbe EIOPA sans VA du 31/10/2026) |
| observations.cds_france_5_ans | valeur : 0,00912 ; date : 2026-10-29 ; plus_haut_2026 : valeur : 0,01042 ; date : 2026-10-23 | observé (source secondaire) | epargnebourse.fr, suivi hebdomadaire du CDS France 5 ans, consulté le 06/11/2026 |
| observations.spread_oat_bund_10_ans | valeur : 0,0163 ; date : 2026-10-30 | observé (source secondaire) | epargnebourse.fr, consulté le 06/11/2026 |
| observations.part_souverain_francais_dans_les_obligations | valeur : 0,26 ; date : fin 2025 | observé | ACPR, Analyses et synthèses n° 181 (30/06/2026), commentaire du graphique 14 |
| observations.notations_des_obligations_des_assureurs | AAA_a_AA- : 0,2 ; A+_a_A- : 0,61 ; BBB+_a_BBB- : 0,18 ; sous_BBB- : 0,01 ; date : T4 2025 | observé | ACPR n° 181, graphique 14 (part AAA à AA- de 47 % au T4 2024) |
| observations.taux_defaut_annuel_moyen_entreprises | AA : 0,0002 ; A : 0,0005 ; BBB : 0,0014 ; periode : 1981-2024 | observé | S&P Global Ratings, 2024 Annual Global Corporate Default And Rating Transition Study (31/03/2025), tableau 4, moyennes pondérées de long terme |
| observations.decote_moyenne_restructurations_souveraines | valeur : 0,37 ; echantillon : 180 restructurations, 68 pays, 1970-2010 | observé | Cruces et Trebesch, « Sovereign Defaults: The Price of Haircuts » (VoxEU) |
| observations.rapport_intensites_risque_neutre_sur_reelles | valeur : 2 ; perimetre : souverains de la zone euro | observé (estimation publiée) | Augustin, Chernov et Song, « Sovereign Credit Risk and Exchange Rates: Evidence from CDS Quanto Spreads », NBER w24506 |
| observations.quanto_cds_relatif | france_1_an : 0,28 ; allemagne_5_ans : 0,44 ; definition : écart relatif entre CDS en dollars et CDS en euros, lu comme la dépréciation de l'euro attendue en cas de défaut | observé (estimation publiée) | Augustin, Chernov et Song, NBER w24506, section 4.3 et figure 9 |
| observations.tec_10_ans | valeur : 0,0488 ; date : 2026-11-04 | observé | oblig.fr, relevé du 04/11/2026 (data/v5/marche/spread_oat_20261104.json) |
| observations.corridors_onc_2013 | max : alpha : -0,04 ; beta : 0 ; gamma : 0,01 ; delta : 0,04 ; rc_min : -0,04 ; rc_max : 0,4 ; min : alpha : -0,06 ; beta : -0,02 ; gamma : 0,01 ; delta : 0,02 ; rc_min : -0,06 ; rc_max : 0,2 | observé (texte réglementaire ; correspondance des colonnes reconstituée, le tableau extrait du PDF ayant perdu ses en-têtes) | ACPR, Orientations nationales complémentaires aux spécifications techniques pour l'exercice 2013 de préparation à Solvabilité II, section 2.4 ; taux attendu : le TME peut servir d'estimateur ; réaction l'année suivante |
| decomposition_spread_10_ans.part_credit_risque_neutre | central : 0,8 ; bas : 0,7 ; haut : 1 | hypothèse |  |
| decomposition_spread_10_ans.probabilite_defaut_reelle_annuelle | valeur : 0,00061 | calibré | 0,20 x 0,02 % + 0,61 x 0,05 % + 0,19 x 0,14 % (sous BBB- compté en BBB) |
| decomposition_spread_10_ans.perte_en_cas_de_defaut_reelle | valeur : 0,5 | hypothèse | entre la décote souveraine moyenne de 37 % (Cruces et Trebesch) et une perte de 60 % usuelle pour la dette senior non garantie des entreprises (non sourcée) |
| decomposition_spread_10_ans.perte_attendue_reelle_annuelle | central : 0,0003 ; haute : 0,001 | calibré (central) ; hypothèse (haute, coûts de dégradation et perte en cas de défaut plus forte) |  |
| conventions_credit.lisse_integral | libelle : Spread intégralement en perte lissée (convention initiale) ; part_saut : 0 ; recouvrement : 0,4 ; blocs : un | convention de valorisation |  |
| conventions_credit.saut_integral | libelle : Spread intégralement en défaut par saut, recouvrement 40 % ; part_saut : 1 ; recouvrement : 0,4 ; blocs : souverain_et_diversifie | hypothèse |  |
| conventions_credit.decompose | libelle : Spread décomposé : 80 % crédit par saut (recouvrement 40 %), 20 % hors défaut lissé ; part_saut : 0,8 ; recouvrement : 0,4 ; blocs : souverain_et_diversifie | hypothèse |  |
| conventions_credit.decompose_recouvrement_63 | libelle : Spread décomposé, recouvrement 63 % ; part_saut : 0,8 ; recouvrement : 0,63 ; blocs : souverain_et_diversifie | hypothèse ; recouvrement = 1 - décote moyenne de Cruces et Trebesch |  |
| conventions_credit.saut_bloc_unique | libelle : Spread intégralement par saut, tout le portefeuille en un seul bloc ; part_saut : 1 ; recouvrement : 0,4 ; blocs : un | sensibilité de concentration extrême |  |
| conventions_credit.k70_granulaire_correle | libelle : 70 % crédit par saut, 50 blocs corrélés (copule, rho 0,2) ; part_saut : 0,7 ; recouvrement : 0,4 ; blocs : granulaire_50 ; correlation : 0,2 ; spread : bootstrap | hypothèse ; candidat central |  |
| conventions_credit.k70_granulaire_independant | libelle : 70 % crédit par saut, 50 blocs indépendants ; part_saut : 0,7 ; recouvrement : 0,4 ; blocs : granulaire_50 ; correlation : aucun ; spread : bootstrap | sensibilité de granularité |  |
| conventions_credit.k70_souverain_granulaire_correle | libelle : 70 % crédit par saut, bloc souverain de 26 % et 50 blocs, tous corrélés (rho 0,2) ; part_saut : 0,7 ; recouvrement : 0,4 ; blocs : souverain_et_granulaire_50 ; correlation : 0,2 ; spread : bootstrap | stress de concentration souveraine |  |
| conventions_credit.k70_souverain_bloc | libelle : 70 % crédit par saut, bloc souverain de 26 % et 20 blocs indépendants (défaut corrélé par bloc) ; part_saut : 0,7 ; recouvrement : 0,4 ; blocs : souverain_et_diversifie ; correlation : aucun ; spread : bootstrap | stress : défaut corrélé par bloc |  |
| conventions_credit.k70_bloc_unique | libelle : 70 % crédit par saut, tout le portefeuille en un bloc ; part_saut : 0,7 ; recouvrement : 0,4 ; blocs : un ; correlation : aucun ; spread : bootstrap | stress extrême de concentration |  |
| conventions_credit.k55_granulaire_correle | libelle : 55 % crédit par saut (quanto de 44 %), 50 blocs corrélés ; part_saut : 0,55 ; recouvrement : 0,4 ; blocs : granulaire_50 ; correlation : 0,2 ; spread : bootstrap | sensibilité de la part de crédit |  |
| conventions_credit.k100_granulaire_correle | libelle : 100 % crédit par saut (sans quanto), 50 blocs corrélés ; part_saut : 1 ; recouvrement : 0,4 ; blocs : granulaire_50 ; correlation : 0,2 ; spread : bootstrap | sensibilité de la part de crédit |  |
| conventions_credit.k70_granulaire_correle_r63 | libelle : 70 % crédit par saut, 50 blocs corrélés, recouvrement 63 % ; part_saut : 0,7 ; recouvrement : 0,63 ; blocs : granulaire_50 ; correlation : 0,2 ; spread : bootstrap | sensibilité au recouvrement |  |
| conventions_credit.k_lisse_bootstrap | libelle : Spread intégralement en perte lissée (spread zéro-coupon par bootstrap) ; part_saut : 0 ; recouvrement : 0,4 ; blocs : un ; correlation : aucun ; spread : bootstrap | convention initiale, spread corrigé |  |
| blocs.souverain_et_diversifie | souverain : 0,26 ; diversifie : part : 0,74 ; nombre_de_blocs : 20 | souverain : observé (ACPR n° 181) ; découpage du reste en 20 blocs indépendants : hypothèse |  |
| blocs.granulaire_50 | souverain : 0 ; diversifie : part : 1 ; nombre_de_blocs : 50 | hypothèse : portefeuille granulaire, aucun bloc isolé |  |
| blocs.souverain_et_granulaire_50 | souverain : 0,26 ; diversifie : part : 0,74 ; nombre_de_blocs : 50 | souverain : observé (ACPR n° 181) ; 50 blocs : hypothèse |  |
| conventions_reelles.prime_actions | valeur : 0,03 | fictif |  |
| references_assures._niveau_initial | valeur : 0,0288 | hypothèse | niveau en t = 0 de l'ancienne référence OAT 10 ans - 2 points ; ordre de grandeur des taux servis attendus pour 2026 (2,8 % à 2,9 %, estimations de place), non observé. Sensibilité : 2,63 %, dernier taux servi moyen observé (2025, ACPR n° 180) |
| references_assures.taux_servi_marche | libelle : Proxy comportemental fictif : taux sans risque 10 ans lissé sur 7 ans ; moteur : lisse ; lissage : 0,142857 ; statut_lissage : hypothèse : un portefeuille concurrent de duration voisine de 7 ans (profil B) renouvelle environ 1/7 de ses titres par an | proxy comportemental fictif, à ne pas lire comme le taux servi observé du marché |  |
| references_assures.livret_a | libelle : Épargne réglementée : livret A (formule €STR et inflation) ; moteur : livret_a ; livret_a_initial : 0,017 ; part_court : 0,5 ; plancher : 0,005 | taux de 1,7 % depuis le 01/08/2026 (observé, jechange.fr) ; formule : moyenne de l'€STR et de l'inflation, arrondie au dixième, plancher 0,5 % (arrêté du 27/01/2021) ; inflation figée et €STR assimilé au taux à 1 an (hypothèses) |  |
| references_assures.lisse_3 | libelle : Proxy comportemental fictif : taux sans risque 10 ans lissé sur 3 ans ; moteur : lisse ; lissage : 0,333333 | sensibilité du délai de transmission |  |
| references_assures.lisse_5 | libelle : Proxy comportemental fictif : taux sans risque 10 ans lissé sur 5 ans ; moteur : lisse ; lissage : 0,2 | sensibilité du délai de transmission |  |
| references_assures.lisse_10 | libelle : Proxy comportemental fictif : taux sans risque 10 ans lissé sur 10 ans ; moteur : lisse ; lissage : 0,1 | sensibilité du délai de transmission |  |
| references_assures.composite_observe | libelle : Référence composite à niveaux observés : fonds euros concurrents, livret A, OAT 10 ans ; moteur : composite ; composantes : nom : Fonds euros concurrents ; poids : 0,6 ; niveau_initial : 0,0263 ; moteur : zc10_sans_risque ; lissage : 0,142857 ; beta : 1 ; statut : niveau observé (taux servi moyen 2025, ACPR n° 180) ; transmission des taux longs sur 7 ans : hypothèse ; poids : fictif, nom : Livret A ; poids : 0,25 ; niveau_initial : 0,017 ; moteur : taux_1an ; lissage : 1 ; beta : 0,5 ; plancher : 0,005 ; statut : niveau observé (1,7 % depuis le 01/08/2026) ; réaction de 0,5 au taux court et plancher de 0,5 % : formule réglementaire, inflation figée ; révision semestrielle assimilée à une transmission dans l'année ; poids : fictif, nom : Placements obligataires directs (OAT 10 ans) ; poids : 0,15 ; niveau_initial : 0,0488 ; moteur : zc10_sans_risque ; lissage : 1 ; beta : 1 ; statut : niveau observé (TEC 10 ans du 04/11/2026) ; transmission immédiate des variations du taux sans risque (spread figé) ; poids : fictif | niveaux observés, délais et coefficients paramétrés, poids fictifs ; aucun calage sur le niveau de 2,88 % |  |
| references_assures.composite_observe.composantes[0] | nom : Fonds euros concurrents ; poids : 0,6 ; niveau_initial : 0,0263 ; moteur : zc10_sans_risque ; lissage : 0,142857 ; beta : 1 | niveau observé (taux servi moyen 2025, ACPR n° 180) ; transmission des taux longs sur 7 ans : hypothèse ; poids : fictif |  |
| references_assures.composite_observe.composantes[1] | nom : Livret A ; poids : 0,25 ; niveau_initial : 0,017 ; moteur : taux_1an ; lissage : 1 ; beta : 0,5 ; plancher : 0,005 | niveau observé (1,7 % depuis le 01/08/2026) ; réaction de 0,5 au taux court et plancher de 0,5 % : formule réglementaire, inflation figée ; révision semestrielle assimilée à une transmission dans l'année ; poids : fictif |  |
| references_assures.composite_observe.composantes[2] | nom : Placements obligataires directs (OAT 10 ans) ; poids : 0,15 ; niveau_initial : 0,0488 ; moteur : zc10_sans_risque ; lissage : 1 ; beta : 1 | niveau observé (TEC 10 ans du 04/11/2026) ; transmission immédiate des variations du taux sans risque (spread figé) ; poids : fictif |  |
| rachats.taux_rachat_structurel_v1_v4 | valeur : 0,05 | hypothèse V1 à V4 |  |
| rachats.taux_rachat_fonds_euros_marche | valeur : 0,044 ; annee : 2025 ; precedent : 0,048 | observé | ACPR, Analyses et synthèses n° 179, L'assurance-vie en 2025, graphique 7 (rachats rapportés aux provisions de N-1) |
| rachats.taux_rachat_structurel_central | valeur_acpr : 0,044 ; parametre_modele : 0,043306 | observé (taux de place), converti par une règle écrite | ACPR n° 179 : rachats de l'année rapportés aux provisions de N-1 (supports en euros rachetables, hors décès et arbitrages). Le modèle applique le taux aux PM revalorisées nettes des décès : rachats / PM d'ouverture = taux x (1 + taux servi) x (1 - taux de décès). Paramètre = 4,4 % / ((1 + 2,63 %) x (1 - 1 %)), avec le taux servi moyen de 2025 et le taux de décès du modèle. |
| calibration_kappa | d_france_1_an : d : 0,28 ; kappa : 0,691 ; d_allemagne_5_ans : d : 0,44 ; kappa : 0,538 ; sans_quanto : d : 0 ; kappa : 0,96 ; central : 0,7 ; bas : 0,55 ; haut : 1 ; spread_5_ans_bootstrap : 0,00949738 | calibré (central) ; bornes : hypothèses |  |
| correlation_copule | valeur : 0,2 | hypothèse ; ordre de grandeur des corrélations d'actifs de la formule de Bâle pour les entreprises (12 % à 24 %), non vérifié |  |

## 5. Stratégies ALM et règles de lecture (fictives)

Fichier `data/v5/strategies/strategies.json`. Stratégies ALM comparées en V5 (comparaison exploratoire). Toutes partent du même bilan initial (allocation initiale du profil) et des mêmes scénarios ; une stratégie ne modifie que les règles de gestion appliquées à partir de l'ouverture. Paramètres fictifs, choisis pour représenter chaque famille de stratégie, sans optimisation.

| Code | Stratégie | Description |
| --- | --- | --- |
| `passive` | Gestion passive (règles des V1 à V4) | Allocation constante, réinvestissement à la maturité du profil, taux servi visé égal à la référence moins 0,5 point, renoncement à la marge si besoin. |
| `reinvestissement_progressif` | Réinvestissement progressif sur une échelle de maturités | Les achats d'obligations sont répartis à parts égales sur 3, 5, 7, 10 et 15 ans au lieu d'une seule maturité. |
| `repositionnement` | Repositionnement obligataire | Vente à l'ouverture de 25 % de la VNC obligataire, en commençant par les plus petits coupons, et rachat aux taux du marché ; la moins-value réalisée passe par la réserve de capitalisation puis par le résultat. |
| `taux_servi_competitif` | Politique de taux servi compétitive | Taux servi visé égal à la référence (au lieu de la référence moins 0,5 point) ; reprise de PPB jusqu'à 50 % du stock par an. |
| `taux_servi_marge` | Politique de taux servi de marge | Taux servi visé égal à la référence moins 1 point ; pas de renoncement à la marge de l'assureur. |
| `liquidite_defensive` | Gestion défensive de la liquidité | Monétaire porté à 12 % de l'actif (aux dépens des actions), réinvestissement obligataire à 5 ans. |
| `taux_servi_competitif_preservant` | Politique de taux servi compétitive préservant la PPB | Taux servi visé égal à la référence, reprise de PPB limitée à 25 % par an de la part du stock qui dépasse un plancher égal à la moitié du ratio PPB / PM d'ouverture ; les reprises obligatoires (dotations de plus de 8 ans) restent appliquées. |
| `distribution_retention` | Gestion passive avec rétention de capital | Règles de la gestion passive ; seule la moitié de l'excédent annuel de fonds propres comptables sur la cible est distribuée, l'autre moitié est conservée. |

**Seuils de lecture.** Un écart est « statistiquement significatif » si son intervalle de confiance apparié à 95 % exclut zéro ; il est « économiquement important » s'il est significatif et si sa moyenne dépasse le seuil ci-dessous ; il est « robuste » sur une grille d'hypothèses si la borne de son intervalle dépasse le seuil, avec le même signe, dans toutes les configurations. Seuils conventionnels, fictifs, choisis avant de lire les résultats ; ils ne sont pas réglés pour obtenir un classement.

| Seuil | Valeur |
| --- | --- |
| valeur_nette_pct_scr | 0,02 |
| rendement_fonds_propres_pt | 0,0025 |
| ecart_taux_servi_pb | 5 |
| taux_rachat_pt | 0,0025 |
| probabilite_apport_pt | 0,005 |
| moins_values_realisees_pct_scr | 0,05 |
| apport_pct_scr | 0,02 |
| indicateur_scr_pt | 0,05 |

**Rendement exigé par l'actionnaire** : 8 %, fictif : repère de rendement exigé par l'actionnaire, jamais combiné aux flux risque neutre.

## 6. Collecte nouvelle

Fichier `data/v5/collecte/collecte.json`. Collecte nouvelle sensible au taux servi relatif (V5, première version volontairement simple). Spécification : docs/V5_SPECIFICATION_COLLECTE.md. Collecte brute de l'année t (1 <= t <= horizon_collecte_ans) : C(t) = c0 x PM(t - 1) x g(e(t - 1)), g(e) = min(g_max ; max(g_min ; 1 + eta x (e - e0) / 1 point)) hors d'une zone neutre de demi-largeur zone_neutre autour de e0, g = 1 dans la zone. e = taux servi sur les contrats nouveaux l'an dernier - référence des assurés de début d'année. Réconciliation avec les flux de 2025 : `docs/V5_COLLECTE.md`, section 1.

| Entrée | Valeurs | Statut | Source ou règle |
| --- | --- | --- | --- |
| reaction.e0 | valeur : 0 | fictif | un assureur qui sert le taux du marché collecte c0 x PM ; la référence des assurés vaut 2,88 % en t = 0 (hypothèse : taux servis attendus pour 2026), le taux servi moyen observé de 2025 est de 2,63 % (ACPR n° 180) ; c0 est dérivé des flux d'un marché qui sert, par définition, le taux du marché, d'où e0 = 0 au centre ; sensibilité e0 = -0,5 point |
| reaction.zone_neutre | valeur : 0 | fictif |  |
| reaction.g_min | valeur : 0 | fictif | pas de collecte négative : les sorties passent par les rachats |
| reaction.g_max | valeur : 2 | fictif |  |
| horizon_collecte_ans | valeur : 10 | fictif | dix générations de contrats nouveaux, puis extinction jusqu'à l'horizon de projection |
| contrats_nouveaux.tmg | valeur : 0 | fictif |  |
| contrats_nouveaux.chargement_prime | valeur : 0 | fictif |  |
| contrats_nouveaux.frais_acquisition_prime | valeur : 0,01 | fictif |  |
| intensites.faible | c0 : 0,03 | fictif | collecte nette d'environ -2,4 % de la PM par an avec g = 1 (sorties du modèle d'environ 5,4 %) |
| intensites.centrale | c0 : 0,06 | dérivé d'agrégats observés (une seule année) | collecte nette 2025 des supports en euros (+8,1 Md€, France Assureurs) rapportée à l'encours de début d'année (1 178 Md€, ACPR), soit environ +0,7 %, ajoutée aux sorties du modèle (décès 1 % et rachat structurel 4,33 % des survivants, soit environ 5,3 % de la PM revalorisée et 5,4 % de la PM de début d'année) : environ 6 %. Avec g = 1, le modèle redonne ainsi la collecte nette de la place (environ +0,6 % de la PM la première année, contre +0,7 % observés), pas ses flux bruts (environ 9,9 % de primes et 9,2 % de sorties) ni la croissance de la PM, qui comprend aussi les intérêts crédités, les prélèvements sociaux et d'autres mouvements (réconciliation : scripts/v5_reconciliation_collecte.py, docs/V5_COLLECTE.md, section 1) |
| intensites.forte | c0 : 0,1 | dérivé d'agrégats observés, borne haute (flux bruts) | collecte brute 2025 des supports en euros (116,9 Md€, France Assureurs) rapportée à l'encours de début d'année (1 178 Md€, ACPR) : environ 10 % ; périmètres non strictement identiques. Les sorties de la place (environ 9 % de l'encours) dépassent celles du modèle (environ 5,3 %) : avec g = 1, c0 = 10 % donne une collecte nette d'environ +4,6 % de la PM par an, bien au-delà des +0,7 % observés |
| elasticites.nulle | eta : 0 | fictif |  |
| elasticites.moderee | eta : 0,5 | fictif | un point de taux servi sous la référence réduit la collecte de moitié |
| elasticites.intermediaire | eta : 0,75 | fictif |  |
| elasticites.soutenue | eta : 1 | fictif | un point sous la référence supprime la collecte |
| elasticites.forte | eta : 1,5 | fictif |  |
| sensibilites.e0_moins_50pb | remplacements : e0 : -0,005 ; libelle : e0 = -0,5 point : la collecte « normale » est atteinte en servant 0,5 point sous la référence, comme la gestion passive | fictif |  |
| sensibilites.horizon_30 | remplacements : horizon_collecte_ans : 30 ; libelle : collecte pendant 30 ans | fictif |  |
| sensibilites.horizon_60 | remplacements : horizon_collecte_ans : 60 ; libelle : collecte jusqu'à l'horizon de projection (60 ans) | fictif |  |
| place_2025.pm_debut | valeur : 1178 ; unite : Md€ | observé | ACPR, Analyses et synthèses n° 180 : encours des contrats individuels en euros fin 2024 |
| place_2025.pm_fin | valeur : 1207 ; unite : Md€ | observé | ACPR, Analyses et synthèses n° 180 : encours des contrats individuels en euros fin 2025 |
| place_2025.collecte_brute | valeur : 116,9 ; unite : Md€ | observé (source secondaire) | France Assureurs, cité par le Cercle de l'Épargne : cotisations 2025 sur les supports en euros |
| place_2025.collecte_nette | valeur : 8,1 ; unite : Md€ | observé (source secondaire) | France Assureurs, cité par le Cercle de l'Épargne : collecte nette 2025 des supports en euros |
| place_2025.taux_revalorisation | valeur : 0,0263 | observé | ACPR, Analyses et synthèses n° 180 : taux moyen 2025, brut de prélèvements sociaux, net de chargements sur encours |
| place_2025.taux_prelevements_sociaux | valeur : 0,172 | observé (source secondaire) | 9,2 % de CSG, 0,5 % de CRDS, 7,5 % de prélèvement de solidarité, prélevés chaque année sur les intérêts du fonds en euros (maif.fr, guide de l'assurance vie) |

Sources : Cercle de l'Épargne, communiqué du 27/01/2026 citant France Assureurs : cotisations 2025 de 192,1 Md€, dont 116,9 Md€ sur les supports en euros ; collecte nette des supports en euros de +8,1 Md€ (https://cercledelepargne.com/wp-content/uploads/2026/01/Communique-de-presse-de-Philippe-Crevel-directeur-du-Cercle-de-lEpargne-resultats-Assurance-vie-2025.pdf, source secondaire) ; ACPR, Analyses et synthèses n° 180, revalorisation 2025, 30/06/2026 : encours des contrats en euros de 1 178 Md€ fin 2024 et 1 207 Md€ fin 2025 ; taux de revalorisation moyen 2025 de 2,63 % (https://acpr.banque-france.fr/system/files/2026-06/20260630_AS180_revalorisation_2025.pdf)

## 7. Observations de place (plausibilité, pas de calibrage des profils)

Fichier `data/v5/conventions/marche_acpr.json` et `data/v5/profils/confrontation_acpr.md`.

| Thème | Valeur | Statut | Source |
| --- | --- | --- | --- |
| Rachats, supports en euros | 4,4 % en 2025 (4,8 % en 2024), rachats rapportés aux provisions de N-1 ; écart interquartile entre organismes réduit de 78 pb | observé ; quartiles du graphique 8 non lisibles dans le PDF | ACPR, Analyses et synthèses n° 179, L'assurance-vie en 2025, graphiques 7 et 8 |
| Rachats rapportés aux cotisations | 39,9 % au premier semestre 2026, plus bas depuis quinze ans (moyenne de long terme 58,6 %) | observé (source secondaire) ; PDF du n° 185 non consulté | ACPR n° 185, chiffres repris par Tripalio (presse.tripalio.fr) |
| Taux servi moyen 2025, contrats individuels | 2,63 % ; premier quartile 2,3 %, troisième quartile 2,9 % (organismes représentant 50 % des encours) | observé | ACPR, Analyses et synthèses n° 180, p. 7 |
| Taux servi par type d'organisme | bancassureurs 2,70 %, assureurs traditionnels 2,48 % | observé | ACPR n° 180, p. 9-10 |
| Rendement de l'actif (TRA) | 2,8 % en 2025 (2,5 % en 2024) ; la moitié des organismes entre 2,4 % et 3,3 % | observé | ACPR n° 180, p. 13-14 |
| PPB | 4,0 % des provisions fin 2025 ; bancassureurs 4,2 %, assureurs traditionnels 3,6 % | observé | ACPR n° 180, p. 14 |
| Taux technique moyen | 0,32 % (bancassureurs 0,25 %, traditionnels 0,39 %) | observé | ACPR n° 180, p. 17 |
| Chargements sur encours | 0,63 % ; premier quartile environ 0,5 %, troisième quartile environ 0,8 % | observé | ACPR n° 180, p. 18 |
| Livret A | 1,7 % depuis le 01/08/2026 (1,5 % au 01/02/2026) | observé | ACPR n° 179, p. 2 ; jechange.fr |
| Solvabilité au 30/06/2026 | 250 % pour l'ensemble, 239 % pour les organismes vie et mixtes, 219 % pour les bancassureurs | observé (source secondaire) | ACPR n° 185, chiffres repris par Tripalio |
| Sensibilité aux taux | la hausse des taux longs réduit davantage la valeur actuelle des engagements que celle des actifs | observé (qualitatif) | ACPR n° 181, p. 4 et 22 |
| Moins-values latentes 2026 | « près de -11 % » sur la dette souveraine française pour les bancassureurs, attribution à l'ACPR non certaine | non retenu : attribution incertaine | Tripalio, article sur le premier semestre 2026 |

## 8. Ce que le modèle ne représente pas

- les prélèvements sociaux, les arbitrages entre supports et les transferts de contrats ;
- un SCR projeté : le besoin de capital est mesuré à l'ouverture, sur l'existant en extinction ;
- dans la vue prudentielle : la mesure transitoire sur les provisions techniques, les risques de contrepartie, de concentration, d'immobilier et de change, l'inflation des frais, l'ajustement symétrique actions et les impôts différés actifs ; le risque opérationnel n'y est calculé que par la formule sur provisions ;
- dans la valeur des affaires nouvelles : un coût explicite du capital additionnel (seulement un seuil, `docs/V5_COLLECTE.md`, section 8) et une marge pour risques non couvrables ;
- dans la vue prudentielle : les effets de la collecte sur les hypothèses de projection de l'existant (calcul en extinction) ;
- les effets commerciaux et de réputation d'un taux servi durablement inférieur à la référence, et le rachat de l'existant au-delà de la loi de rachat dynamique ;
- une calibration de l'élasticité de la collecte ou de la loi de rachat sur des données de 2026 : aucune n'a été trouvée.

