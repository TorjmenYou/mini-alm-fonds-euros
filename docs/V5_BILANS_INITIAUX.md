# V5 : bilans initiaux des trois profils fictifs

Généré par `scripts/v5_rapport_bilans.py` depuis `resultats/v5_bilans_initiaux.json` (`scripts/v5_bilans_initiaux.py`). Unités fictives : 1 unité = 10 M€, PM de 1 000 = 10 Md€. Valorisation risque neutre au 31/10/2026, base sans VA sauf mention. **Les trois profils sont fictifs** : ils ne décrivent aucun organisme réel.

Les valeurs économiques sont **avant impôt différé** : l'impôt n'entrera qu'avec les métriques de l'étape suivante.

## 1. Bilans comptables

| | A | B | C |
| --- | ---: | ---: | ---: |
| Obligations (VNC) | 946,0 | 939,2 | 889,7 |
| Actions (VNC) | 86,0 | 110,5 | 130,2 |
| Monétaire | 43,0 | 55,2 | 65,1 |
| **Total actif** | **1 075,0** | **1 105,0** | **1 085,0** |
| Provision mathématique | 1 000,0 | 1 000,0 | 1 000,0 |
| PPB | 25,0 | 40,0 | 20,0 |
| Réserve de capitalisation | 5,0 | 15,0 | 5,0 |
| Fonds propres comptables | 45,0 | 50,0 | 60,0 |
| **Total passif** | **1 075,0** | **1 105,0** | **1 085,0** |
| Écart actif - passif | 0e+00 | 0e+00 | 0e+00 |

## 2. Bilans économiques et passage des fonds propres comptables à la valeur actionnaire

| | A | B | C |
| --- | ---: | ---: | ---: |
| Obligations (valeur de marché) | 775,1 | 820,8 | 837,6 |
| Actions (valeur de marché) | 90,3 | 121,6 | 138,0 |
| Monétaire | 43,0 | 55,2 | 65,1 |
| **Actif en valeur de marché** | **908,4** | **997,6** | **1 040,7** |
| BE stochastique (1 000 scénarios) | 914,7 ± 7,6 | 937,7 ± 6,5 | 956,2 ± 6,7 |
| BE équivalent certain | 877,8 | 894,3 | 914,8 |
| TVOG du modèle (BE stochastique - BE équivalent certain) | 36,9 | 43,4 | 41,4 |
| **Valeur actionnaire (actif - BE stochastique)** | **−6,3 ± 7,6** | **59,9 ± 6,5** | **84,5 ± 6,7** |
| Base avec VA : BE stochastique | 904,4 ± 7,1 | 929,2 ± 6,4 | 948,2 ± 6,6 |
| Base avec VA : valeur actionnaire | 4,0 ± 7,1 | 68,4 ± 6,4 | 92,5 ± 6,6 |
| Effet VA sur le BE (réglementaire, pas de la valeur économique) | −10,3 | −8,5 | −8,1 |

**Réconciliation, équivalent certain** (identité exacte en t = 0) : fonds propres comptables + plus ou moins-values latentes + (provisions comptables - BE) = actif en valeur de marché - BE.

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fonds propres comptables | 45,0 | 50,0 | 60,0 |
| Moins-values latentes obligataires | −170,9 | −118,4 | −52,1 |
| Plus-values latentes actions | 4,3 | 11,1 | 7,8 |
| Provisions comptables (PM + PPB + réserve) - BE | 152,2 | 160,7 | 110,2 |
| **Valeur actionnaire, équivalent certain** | **30,6** | **103,4** | **125,9** |
| Écart avec actif - BE | 4e-14 | -6e-14 | -1e-13 |

**Contrôles de cohérence, stochastique (1 000 scénarios)** :

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fuite, base sans va (doit contenir 0) | 0,29 ± 2,58 | 1,29 ± 2,96 | 2,18 ± 3,77 |
| Fuite, base avec va (doit contenir 0) | 0,54 ± 2,66 | 1,28 ± 3,00 | 2,22 ± 3,81 |
| Identité de valeur, écart maximal par scénario | 5e-13 | 3e-13 | 5e-13 |
| Part des scénarios avec apport de capital | 50,4 % | 7,5 % | 4,2 % |

## 3. Construction et indicateurs des profils

| | A | B | C |
| --- | ---: | ---: | ---: |
| Coupon moyen des obligations | 2,20 % | 2,64 % | 3,79 % |
| Moins-values latentes obligataires (% de la VNC) | −18,1 % | −12,6 % | −5,9 % |
| Duration de Macaulay des obligations (ans) | 7,8 | 7,2 | 8,6 |
| Duration de Macaulay des flux du passif (ans) | 7,4 | 13,4 | 14,7 |
| Duration effective de l'actif (ans) | 6,5 | 5,7 | 6,7 |
| Duration effective du BE (ans) | −0,1 | 4,6 | 3,1 |
| Duration effective du BE, référence des assurés figée à son niveau de l'année 1 (ans) | 7,1 | 7,8 | 8,3 |
| Variation de la valeur actionnaire pour +1 pb de taux sans risque | −0,60 | −0,16 | −0,41 |
| Variation de la valeur actionnaire pour +1 pb, référence figée | 0,03 | 0,12 | 0,05 |
| PPB (% de la PM) | 2,5 % | 4,0 % | 2,0 % |
| Réserve de capitalisation (% de la PM) | 0,5 % | 1,5 % | 0,5 % |
| Fonds propres comptables (% de la PM) | 4,5 % | 5,0 % | 6,0 % |
| Monétaire (% de l'actif en valeur de marché) | 4,7 % | 5,5 % | 6,3 % |
| Taux garanti | 0,60 % | 0,32 % | 0,00 % |
| Taux servi de l'année écoulée | 2,30 % | 2,63 % | 3,00 % |
| Produits financiers de l'année 1 (% de la VNC), pertes de crédit risque neutre déduites | 2,01 % | 2,10 % | 2,93 % |
| Taux de référence des assurés, année 1 | 2,66 % | 2,66 % | 2,66 % |
| Taux servi, année 1 | 2,16 % | 2,16 % | 2,16 % |
| Taux de rachat, année 1 | 5,0 % | 5,0 % | 5,0 % |
| Taux servi moyen, années 1 à 20 (équivalent certain) | 1,12 % | 1,96 % | 2,19 % |
| Taux de rachat moyen, années 1 à 20 (équivalent certain) | 11,8 % | 5,6 % | 5,0 % |
| PM à 10 ans (équivalent certain) | 226,3 | 574,9 | 681,3 |

## 4. Sensibilités (équivalent certain, base sans VA sauf mention)

**Profil A : Assureur historique sous pression**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 908,4 | −18,1 % | 877,8 | 30,6 | 2,16 % | 5,0 % | 1,12 % | 11,8 % |
| spread +50 pb | 878,7 | −21,2 % | 898,0 | −19,3 | 1,83 % | 5,0 % | 0,68 % | 19,6 % |
| spread -50 pb | 939,5 | −14,8 % | 855,9 | 83,7 | 1,63 % | 5,0 % | 1,51 % | 5,2 % |
| coupons 2015-2021 +50 pb | 927,9 | −16,0 % | 877,6 | 50,3 | 2,16 % | 5,0 % | 1,32 % | 10,1 % |
| coupons 2015-2021 -25 pb | 898,6 | −19,1 % | 877,8 | 20,8 | 2,16 % | 5,0 % | 1,04 % | 12,4 % |
| prime d'achat -40 pb (toutes générations) | 881,1 | −20,9 % | 876,1 | 5,1 | 1,93 % | 5,0 % | 0,95 % | 13,1 % |
| prime d'achat +20 pb (toutes générations) | 922,0 | −16,6 % | 877,4 | 44,5 | 2,16 % | 5,0 % | 1,23 % | 10,8 % |
| PPB x 0,5 | 897,8 | −18,1 % | 875,3 | 22,5 | 1,83 % | 5,0 % | 1,05 % | 12,2 % |
| PPB x 1,5 | 918,9 | −18,1 % | 878,6 | 40,4 | 2,16 % | 5,0 % | 1,21 % | 11,0 % |
| référence assurés : obligations à 10 ans du modèle (ajustement 0) | 908,4 | −18,1 % | 940,7 | −32,4 | 2,29 % | 18,6 % | 0,80 % | 32,2 % |
| référence assurés : obligations à 10 ans du modèle - 1 pt | 908,4 | −18,1 % | 917,2 | −8,8 | 2,29 % | 8,6 % | 0,72 % | 23,9 % |
| référence assurés : obligations à 10 ans du modèle - 3 pts | 908,4 | −18,1 % | 827,9 | 80,4 | 1,16 % | 5,0 % | 1,32 % | 5,0 % |
| référence assurés : livret A 1,7 % fixe | 908,4 | −18,1 % | 827,9 | 80,5 | 1,20 % | 5,0 % | 1,32 % | 5,0 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 908,4 | −18,1 % | 872,3 | 36,1 | 2,16 % | 5,0 % | 1,14 % | 11,1 % |
| taux garanti +0,30 pt | 908,4 | −18,1 % | 878,0 | 30,3 | 2,16 % | 5,0 % | 1,30 % | 10,1 % |
| base avec VA | 908,4 | −18,1 % | 865,6 | 42,7 | 2,16 % | 5,0 % | 1,26 % | 10,6 % |

**Profil B : Assureur intermédiaire**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 997,6 | −12,6 % | 894,3 | 103,4 | 2,16 % | 5,0 % | 1,96 % | 5,6 % |
| spread +50 pb | 968,7 | −15,7 % | 912,2 | 56,5 | 2,68 % | 5,0 % | 1,81 % | 11,0 % |
| spread -50 pb | 1 027,9 | −9,4 % | 900,7 | 127,2 | 1,63 % | 5,0 % | 2,16 % | 5,0 % |
| coupons 2015-2021 +50 pb | 1 008,8 | −11,4 % | 898,6 | 110,2 | 2,16 % | 5,0 % | 2,03 % | 5,2 % |
| coupons 2015-2021 -25 pb | 992,1 | −13,2 % | 892,3 | 99,8 | 2,16 % | 5,0 % | 1,91 % | 5,9 % |
| prime d'achat -40 pb (toutes générations) | 972,6 | −15,3 % | 887,4 | 85,2 | 2,16 % | 5,0 % | 1,78 % | 6,9 % |
| prime d'achat +20 pb (toutes générations) | 1 010,2 | −11,3 % | 898,9 | 111,3 | 2,16 % | 5,0 % | 2,04 % | 5,1 % |
| PPB x 0,5 | 979,6 | −12,6 % | 888,3 | 91,3 | 2,16 % | 5,0 % | 1,79 % | 6,8 % |
| PPB x 1,5 | 1 015,7 | −12,6 % | 904,5 | 111,2 | 2,16 % | 5,0 % | 2,10 % | 5,0 % |
| référence assurés : obligations à 10 ans du modèle (ajustement 0) | 997,6 | −12,6 % | 957,2 | 40,4 | 3,91 % | 15,3 % | 1,99 % | 21,2 % |
| référence assurés : obligations à 10 ans du modèle - 1 pt | 997,6 | −12,6 % | 938,2 | 59,4 | 3,16 % | 5,3 % | 2,09 % | 11,8 % |
| référence assurés : obligations à 10 ans du modèle - 3 pts | 997,6 | −12,6 % | 876,9 | 120,8 | 1,16 % | 5,0 % | 2,01 % | 4,8 % |
| référence assurés : livret A 1,7 % fixe | 997,6 | −12,6 % | 877,9 | 119,7 | 1,20 % | 5,0 % | 2,04 % | 4,9 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 997,6 | −12,6 % | 892,0 | 105,7 | 2,16 % | 5,0 % | 1,95 % | 5,4 % |
| taux garanti +0,30 pt | 997,6 | −12,6 % | 894,3 | 103,4 | 2,16 % | 5,0 % | 1,96 % | 5,6 % |
| base avec VA | 997,6 | −12,6 % | 885,7 | 112,0 | 2,16 % | 5,0 % | 2,07 % | 5,1 % |

**Profil C : Assureur plus récemment investi**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 1 040,7 | −5,9 % | 914,8 | 125,9 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| spread +50 pb | 1 005,5 | −9,8 % | 926,3 | 79,2 | 2,68 % | 5,0 % | 2,18 % | 7,9 % |
| spread -50 pb | 1 077,7 | −1,7 % | 930,2 | 147,5 | 1,63 % | 5,0 % | 2,47 % | 5,0 % |
| coupons 2015-2021 +50 pb | 1 041,8 | −5,7 % | 914,9 | 126,9 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| coupons 2015-2021 -25 pb | 1 040,2 | −5,9 % | 914,7 | 125,4 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| prime d'achat -40 pb (toutes générations) | 1 011,9 | −9,1 % | 899,3 | 112,6 | 2,16 % | 5,0 % | 2,05 % | 5,2 % |
| prime d'achat +20 pb (toutes générations) | 1 055,1 | −4,2 % | 919,1 | 136,0 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| PPB x 0,5 | 1 031,1 | −5,9 % | 909,0 | 122,1 | 2,16 % | 5,0 % | 2,14 % | 5,0 % |
| PPB x 1,5 | 1 050,3 | −5,9 % | 918,5 | 131,8 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| référence assurés : obligations à 10 ans du modèle (ajustement 0) | 1 040,7 | −5,9 % | 975,1 | 65,6 | 3,86 % | 11,6 % | 2,40 % | 17,8 % |
| référence assurés : obligations à 10 ans du modèle - 1 pt | 1 040,7 | −5,9 % | 958,1 | 82,6 | 3,16 % | 5,0 % | 2,50 % | 7,9 % |
| référence assurés : obligations à 10 ans du modèle - 3 pts | 1 040,7 | −5,9 % | 902,4 | 138,3 | 1,16 % | 4,1 % | 2,26 % | 4,7 % |
| référence assurés : livret A 1,7 % fixe | 1 040,7 | −5,9 % | 903,4 | 137,3 | 1,20 % | 4,3 % | 2,27 % | 4,9 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 1 040,7 | −5,9 % | 910,8 | 129,9 | 2,16 % | 5,0 % | 2,13 % | 5,0 % |
| taux garanti +0,30 pt | 1 040,7 | −5,9 % | 914,8 | 125,9 | 2,16 % | 5,0 % | 2,19 % | 5,0 % |
| base avec VA | 1 040,7 | −5,9 % | 905,0 | 135,7 | 2,16 % | 5,0 % | 2,24 % | 5,0 % |

## 5. Confrontation aux ordres de grandeur de place

Sources et statut de chaque chiffre de place : `data/v5/profils/confrontation_acpr.md`. Les profils sont fictifs : un écart n'est pas une erreur s'il découle du récit du profil, mais il doit être expliqué.

| Indicateur | A | B | C | Place | Lecture |
| --- | ---: | ---: | ---: | --- | --- |
| PPB (% de la PM) | 2,5 % | 4,0 % | 2,0 % | 4,0 % des provisions (fin 2025, ACPR n° 180) | B au niveau de place ; A (réserves consommées) et C (assureur plus jeune) en dessous, par construction |
| Taux garanti | 0,60 % | 0,32 % | 0,00 % | 0,32 % de taux technique moyen (2025, ACPR n° 180) | B au niveau de place ; A plus élevé (contrats anciens), C sans garantie |
| Taux servi de l'année écoulée | 2,30 % | 2,63 % | 3,00 % | 2,63 % (2025, ACPR n° 180) | B au niveau de place ; A en dessous, C au-dessus (politique plus offensive) |
| Coupon moyen des obligations | 2,20 % | 2,64 % | 3,79 % | Non publié ; rendement de l'actif de 2,8 % en 2025, actions et immobilier compris (ACPR n° 180) | Le coupon de B est calé pour un rendement comptable de cet ordre (prime d'achat de 0,6 point) |
| Moins-values latentes obligataires (% de la VNC) | −18,1 % | −12,6 % | −5,9 % | -2,7 % à -3,4 % au 30/06/2025 (dérivé de l'ACPR n° 177) ; donnée 2026 (ACPR n° 185) non lue | Les moins-values des profils dépendent du spread hypothétique des obligations (moyenne de long terme publiée par l'EIOPA) et des coupons de chaque génération ; à revoir dès que le n° 185 est accessible |
| Sorties annuelles (rachats et décès), année 1 | 6,0 % | 6,0 % | 6,0 % | Environ 6,7 % de l'encours, tous supports, décès compris (dérivé de France Assureurs, 2026) | Ordre de grandeur cohérent ; la collecte nette positive de 2026 justifie l'absence de vague de rachats |

## 6. Limites méthodologiques restantes

- **Lissage des pertes de crédit risque neutre : limite principale.** En risque neutre, tout le spread des obligations (126 pb à 10 ans, 128 pb à 30 ans, hypothèse) devient une perte annuelle lissée, retirée chaque année et dans chaque scénario des produits financiers, donc de l'assiette de la participation. La valeur actuelle nette d'un achat reste nulle (tests). Mais la participation et les rachats sont non linéaires : cette répartition lisse des pertes déprime le taux servi partout. En équivalent certain, le profil A, au rendement comptable faible, sert en moyenne 1,1 % sur les années 1 à 20, avec des rachats moyens de 11,8 %, pour une valeur actionnaire de 30,6. Un modèle de défaut par saut, avec perte en cas de défaut, donnerait la même valeur des actifs, mais concentrerait les pertes sur peu de scénarios et changerait le partage entre assurés et actionnaire. Le marché ne tranche pas entre les deux : c'est un risque de modèle à traiter avant les métriques de rentabilité.
- **Valeurs avant impôt.** L'impôt (25 %, contribution sociale de 3,3 % au-delà de l'abattement) est codé et testé, mais pas encore appliqué : les valeurs économiques sont donc présentées avant impôt différé.
- **Pas encore de capital.** Ni SCR ni marge de risque par profil, et pas encore de coût du capital : ils arrivent à l'étape suivante, avec la distinction entre coût réglementaire, coûts frictionnels et rendement exigé.
- **Générateur de scénarios non recalé.** Les paramètres de Hull-White (a = 0,05, sigma = 1 %) et la volatilité actions (18 %) restent ceux des V1 à V4, sans calage sur les volatilités implicites de marché : la TVOG en dépend directement.
- **Un seul model point par profil.** Le taux garanti est une moyenne ; la V4 multi-model points n'est pas couplée à l'actif. Le portefeuille est fermé : pas encore de collecte nouvelle, ni de politique de collecte pour C.
- **Crédit simplifié.** Toutes les obligations sont valorisées avec un même spread (souverains et entreprises confondus), sans notation ni migration, avec une perte en convention de recouvrement en valeur de marché. Ce spread est une hypothèse : la moyenne de long terme des spreads publiée par l'EIOPA pour la notation A, et non un spread de marché observé au 31/10/2026.
- **Pertes risque neutre dans les produits comptables.** En valorisation, la perte risque neutre réduit les produits financiers, donc la participation : c'est cohérent avec le marché, mais la trajectoire comptable n'est pas une prévision.
- **Coupons par génération.** Ce sont des hypothèses : l'ordre de grandeur du rendement à 10 ans de l'État de chaque période, arrondi, plus une prime d'achat.
- **Comportement des assurés.** La référence « taux à 10 ans des obligations du modèle - 2 points » reste l'hypothèse la plus incertaine. Ses sensibilités changent fortement la valeur actionnaire. Elle suit la courbe à terme des obligations, qui inclut le spread : une référence fondée sur le taux sans risque, recalée au même niveau en t = 0, ramène le rachat moyen des années 1 à 20 à 11,1 % (A), 5,4 % (B), 5,0 % (C) et la valeur actionnaire en équivalent certain à 36,1 (A), 105,7 (B), 129,9 (C). La même convention commande la sensibilité aux taux : la référence suit le choc, une hausse accélère les rachats et raccourcit le passif. Duration effective du BE, en années : −0,1 (A), 4,6 (B), 3,1 (C), contre 7,1 (A), 7,8 (B), 8,3 (C) avec une référence figée. Ce point conditionnera directement les stratégies d'adossement.
- **Correction pour volatilité.** La VA est figée à 20 pb, sans VA dynamique ni ajustement égalisateur.
- **Données de place manquantes.** Moins-values latentes 2026, durations, réserve de capitalisation, répartition des garanties, rachats sur l'euro et dispersion entre organismes : voir `data/v5/profils/confrontation_acpr.md`.

