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
| Obligations (valeur de marché) | 766,5 | 816,0 | 825,7 |
| Actions (valeur de marché) | 90,3 | 121,6 | 138,0 |
| Monétaire | 43,0 | 55,2 | 65,1 |
| **Actif en valeur de marché** | **899,8** | **992,8** | **1 028,8** |
| BE stochastique (1 000 scénarios) | 929,9 ± 6,5 | 949,0 ± 5,5 | 961,1 ± 5,2 |
| BE équivalent certain | 905,8 | 926,2 | 939,9 |
| TVOG du modèle (BE stochastique - BE équivalent certain) | 24,1 | 22,8 | 21,2 |
| **Valeur actionnaire (actif - BE stochastique)** | **−30,1 ± 6,5** | **43,7 ± 5,5** | **67,7 ± 5,2** |
| Base avec VA : BE stochastique | 920,6 ± 6,1 | 941,3 ± 5,2 | 953,6 ± 5,0 |
| Base avec VA : valeur actionnaire | −20,8 ± 6,1 | 51,4 ± 5,2 | 75,2 ± 5,0 |
| Effet VA sur le BE (réglementaire, pas de la valeur économique) | −9,3 | −7,7 | −7,5 |

**Réconciliation, équivalent certain** (identité exacte en t = 0) : fonds propres comptables + plus ou moins-values latentes + (provisions comptables - BE) = actif en valeur de marché - BE.

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fonds propres comptables | 45,0 | 50,0 | 60,0 |
| Moins-values latentes obligataires | −179,5 | −123,3 | −64,0 |
| Plus-values latentes actions | 4,3 | 11,1 | 7,8 |
| Provisions comptables (PM + PPB + réserve) - BE | 124,2 | 128,8 | 85,1 |
| **Valeur actionnaire, équivalent certain** | **−6,0** | **66,6** | **88,9** |
| Écart avec actif - BE | 6e-14 | 6e-14 | -1e-13 |

**Contrôles de cohérence, stochastique (1 000 scénarios)** :

| | A | B | C |
| --- | ---: | ---: | ---: |
| Fuite, base sans va (doit contenir 0) | −0,19 ± 2,07 | 0,81 ± 2,46 | 1,31 ± 3,26 |
| Fuite, base avec va (doit contenir 0) | −0,08 ± 2,11 | 0,93 ± 2,55 | 1,57 ± 3,35 |
| Identité de valeur, écart maximal par scénario | 2e-13 | 3e-13 | 5e-13 |
| Part des scénarios avec apport de capital | 75,0 % | 12,4 % | 6,8 % |

## 3. Construction et indicateurs des profils

| | A | B | C |
| --- | ---: | ---: | ---: |
| Coupon moyen des obligations | 2,20 % | 2,64 % | 3,79 % |
| Moins-values latentes obligataires (% de la VNC) | −19,0 % | −13,1 % | −7,2 % |
| Duration de Macaulay des obligations (ans) | 7,7 | 7,2 | 8,5 |
| Duration de Macaulay des flux du passif (ans) | 5,7 | 8,1 | 10,1 |
| Duration effective de l'actif (ans) | 6,4 | 5,7 | 6,6 |
| Duration effective du BE (ans) | 1,2 | 1,8 | 3,9 |
| Duration effective du BE, référence des assurés figée à son niveau de l'année 1 (ans) | 7,0 | 10,1 | 13,0 |
| Variation de la valeur actionnaire pour +1 pb de taux sans risque | −0,47 | −0,40 | −0,32 |
| Variation de la valeur actionnaire pour +1 pb, référence figée | 0,04 | 0,34 | 0,50 |
| PPB (% de la PM) | 2,5 % | 4,0 % | 2,0 % |
| Réserve de capitalisation (% de la PM) | 0,5 % | 1,5 % | 0,5 % |
| Fonds propres comptables (% de la PM) | 4,5 % | 5,0 % | 6,0 % |
| Monétaire (% de l'actif en valeur de marché) | 4,8 % | 5,6 % | 6,3 % |
| Taux garanti | 0,60 % | 0,32 % | 0,00 % |
| Taux servi de l'année écoulée | 2,30 % | 2,63 % | 3,00 % |
| Produits financiers de l'année 1 (% de la VNC), pertes de crédit risque neutre déduites | 2,41 % | 2,50 % | 3,32 % |
| Taux de référence des assurés, année 1 | 2,88 % | 2,88 % | 2,88 % |
| Taux servi, année 1 | 2,38 % | 2,38 % | 2,38 % |
| Taux de rachat, année 1 | 5,0 % | 5,0 % | 5,0 % |
| Taux servi moyen, années 1 à 20 (équivalent certain) | 0,78 % | 2,00 % | 2,29 % |
| Taux de rachat moyen, années 1 à 20 (équivalent certain) | 22,4 % | 11,5 % | 8,8 % |
| PM à 10 ans (équivalent certain) | 110,4 | 245,9 | 376,9 |

## 4. Sensibilités (équivalent certain, base sans VA sauf mention)

**Profil A : Assureur historique sous pression**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 899,8 | −19,0 % | 905,8 | −6,0 | 2,38 % | 5,0 % | 0,78 % | 22,4 % |
| spread +50 pb | 870,8 | −22,0 % | 918,2 | −47,4 | 2,24 % | 6,1 % | 0,73 % | 27,8 % |
| spread -50 pb | 930,2 | −15,8 % | 889,0 | 41,2 | 1,86 % | 5,0 % | 1,19 % | 14,7 % |
| coupons 2015-2021 +50 pb | 919,2 | −16,9 % | 907,7 | 11,5 | 2,38 % | 5,0 % | 1,06 % | 20,5 % |
| coupons 2015-2021 -25 pb | 890,0 | −20,0 % | 905,5 | −15,4 | 2,38 % | 5,0 % | 0,77 % | 22,5 % |
| prime d'achat -40 pb (toutes générations) | 872,6 | −21,9 % | 904,2 | −31,6 | 2,34 % | 5,0 % | 0,74 % | 22,8 % |
| prime d'achat +20 pb (toutes générations) | 913,4 | −17,5 % | 907,3 | 6,1 | 2,38 % | 5,0 % | 1,03 % | 20,8 % |
| PPB x 0,5 | 889,3 | −19,0 % | 904,0 | −14,7 | 2,24 % | 5,0 % | 0,75 % | 22,6 % |
| PPB x 1,5 | 910,2 | −19,0 % | 909,4 | 0,9 | 2,38 % | 5,0 % | 1,02 % | 21,0 % |
| référence assurés : OAT 10 ans (ajustement 0) | 899,8 | −19,0 % | 945,7 | −46,0 | 2,70 % | 20,8 % | 0,81 % | 33,1 % |
| référence assurés : OAT 10 ans - 1 pt | 899,8 | −19,0 % | 931,5 | −31,7 | 2,70 % | 10,8 % | 0,76 % | 31,7 % |
| référence assurés : OAT 10 ans - 3 pts | 899,8 | −19,0 % | 859,7 | 40,0 | 1,38 % | 5,0 % | 1,07 % | 11,6 % |
| référence assurés : livret A 1,7 % fixe | 899,8 | −19,0 % | 805,5 | 94,2 | 1,20 % | 5,0 % | 1,08 % | 5,0 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 899,8 | −19,0 % | 883,9 | 15,9 | 2,38 % | 5,0 % | 1,03 % | 13,9 % |
| taux garanti +0,30 pt | 899,8 | −19,0 % | 908,7 | −9,0 | 2,38 % | 5,0 % | 1,04 % | 20,0 % |
| base avec VA | 899,8 | −19,0 % | 897,0 | 2,8 | 2,38 % | 5,0 % | 1,04 % | 20,7 % |

**Profil B : Assureur intermédiaire**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 992,8 | −13,1 % | 926,2 | 66,6 | 2,38 % | 5,0 % | 2,00 % | 11,5 % |
| spread +50 pb | 964,2 | −16,2 % | 928,0 | 36,1 | 2,91 % | 5,0 % | 1,64 % | 19,7 % |
| spread -50 pb | 1 022,7 | −9,9 % | 916,2 | 106,5 | 1,86 % | 5,0 % | 2,30 % | 5,7 % |
| coupons 2015-2021 +50 pb | 1 003,9 | −11,9 % | 929,0 | 74,9 | 2,38 % | 5,0 % | 2,08 % | 10,8 % |
| coupons 2015-2021 -25 pb | 987,2 | −13,7 % | 923,4 | 63,8 | 2,38 % | 5,0 % | 1,94 % | 12,1 % |
| prime d'achat -40 pb (toutes générations) | 967,7 | −15,8 % | 913,8 | 53,8 | 2,38 % | 5,0 % | 1,67 % | 14,7 % |
| prime d'achat +20 pb (toutes générations) | 1 005,3 | −11,8 % | 929,4 | 75,9 | 2,38 % | 5,0 % | 2,09 % | 10,7 % |
| PPB x 0,5 | 974,8 | −13,1 % | 915,1 | 59,7 | 2,38 % | 5,0 % | 1,73 % | 14,1 % |
| PPB x 1,5 | 1 010,7 | −13,1 % | 934,2 | 76,5 | 2,38 % | 5,0 % | 2,15 % | 10,2 % |
| référence assurés : OAT 10 ans (ajustement 0) | 992,8 | −13,1 % | 965,9 | 26,9 | 4,32 % | 17,5 % | 1,84 % | 28,3 % |
| référence assurés : OAT 10 ans - 1 pt | 992,8 | −13,1 % | 947,8 | 45,0 | 3,38 % | 7,5 % | 1,79 % | 22,0 % |
| référence assurés : OAT 10 ans - 3 pts | 992,8 | −13,1 % | 870,5 | 122,3 | 1,38 % | 5,0 % | 1,95 % | 5,3 % |
| référence assurés : livret A 1,7 % fixe | 992,8 | −13,1 % | 850,7 | 142,0 | 1,20 % | 5,0 % | 1,75 % | 5,0 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 992,8 | −13,1 % | 897,6 | 95,1 | 2,38 % | 5,0 % | 1,92 % | 7,2 % |
| taux garanti +0,30 pt | 992,8 | −13,1 % | 926,2 | 66,6 | 2,38 % | 5,0 % | 2,00 % | 11,5 % |
| base avec VA | 992,8 | −13,1 % | 917,8 | 75,0 | 2,38 % | 5,0 % | 2,19 % | 10,2 % |

**Profil C : Assureur plus récemment investi**

| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Référence | 1 028,8 | −7,2 % | 939,9 | 88,9 | 2,38 % | 5,0 % | 2,29 % | 8,8 % |
| spread +50 pb | 994,4 | −11,1 % | 933,3 | 61,2 | 2,91 % | 5,0 % | 1,80 % | 18,1 % |
| spread -50 pb | 1 065,0 | −3,1 % | 934,0 | 131,0 | 1,86 % | 5,0 % | 2,51 % | 5,0 % |
| coupons 2015-2021 +50 pb | 1 029,9 | −7,1 % | 940,2 | 89,7 | 2,38 % | 5,0 % | 2,29 % | 8,8 % |
| coupons 2015-2021 -25 pb | 1 028,3 | −7,3 % | 939,6 | 88,7 | 2,38 % | 5,0 % | 2,28 % | 8,9 % |
| prime d'achat -40 pb (toutes générations) | 1 000,0 | −10,4 % | 923,3 | 76,7 | 2,38 % | 5,0 % | 1,95 % | 12,0 % |
| prime d'achat +20 pb (toutes générations) | 1 043,2 | −5,6 % | 945,5 | 97,7 | 2,38 % | 5,0 % | 2,40 % | 7,8 % |
| PPB x 0,5 | 1 019,4 | −7,2 % | 932,5 | 86,8 | 2,38 % | 5,0 % | 2,18 % | 9,7 % |
| PPB x 1,5 | 1 038,3 | −7,2 % | 943,8 | 94,5 | 2,38 % | 5,0 % | 2,36 % | 8,1 % |
| référence assurés : OAT 10 ans (ajustement 0) | 1 028,8 | −7,2 % | 970,4 | 58,4 | 4,25 % | 13,8 % | 2,05 % | 27,1 % |
| référence assurés : OAT 10 ans - 1 pt | 1 028,8 | −7,2 % | 959,4 | 69,4 | 3,38 % | 5,0 % | 2,11 % | 19,4 % |
| référence assurés : OAT 10 ans - 3 pts | 1 028,8 | −7,2 % | 879,1 | 149,7 | 1,38 % | 4,7 % | 2,07 % | 5,0 % |
| référence assurés : livret A 1,7 % fixe | 1 028,8 | −7,2 % | 870,8 | 158,0 | 1,20 % | 4,3 % | 1,98 % | 4,9 % |
| référence assurés : sans risque 10 ans, même niveau en t = 0 | 1 028,8 | −7,2 % | 907,2 | 121,6 | 2,38 % | 5,0 % | 2,19 % | 5,4 % |
| taux garanti +0,30 pt | 1 028,8 | −7,2 % | 939,9 | 88,9 | 2,38 % | 5,0 % | 2,29 % | 8,8 % |
| base avec VA | 1 028,8 | −7,2 % | 932,3 | 96,5 | 2,38 % | 5,0 % | 2,50 % | 7,4 % |

## 5. Confrontation aux ordres de grandeur de place

Sources et statut de chaque chiffre de place : `data/v5/profils/confrontation_acpr.md`. Les profils sont fictifs : un écart n'est pas une erreur s'il découle du récit du profil, mais il doit être expliqué.

| Indicateur | A | B | C | Place | Lecture |
| --- | ---: | ---: | ---: | --- | --- |
| PPB (% de la PM) | 2,5 % | 4,0 % | 2,0 % | 4,0 % des provisions (fin 2025, ACPR n° 180) | B au niveau de place ; A (réserves consommées) et C (assureur plus jeune) en dessous, par construction |
| Taux garanti | 0,60 % | 0,32 % | 0,00 % | 0,32 % de taux technique moyen (2025, ACPR n° 180) | B au niveau de place ; A plus élevé (contrats anciens), C sans garantie |
| Taux servi de l'année écoulée | 2,30 % | 2,63 % | 3,00 % | 2,63 % (2025, ACPR n° 180) | B au niveau de place ; A en dessous, C au-dessus (politique plus offensive) |
| Coupon moyen des obligations | 2,20 % | 2,64 % | 3,79 % | Non publié ; rendement de l'actif de 2,8 % en 2025, actions et immobilier compris (ACPR n° 180) | Le coupon de B est calé pour un rendement comptable de cet ordre (prime d'achat de 0,6 point) |
| Moins-values latentes obligataires (% de la VNC) | −19,0 % | −13,1 % | −7,2 % | -2,7 % à -3,4 % au 30/06/2025 (dérivé de l'ACPR n° 177) ; donnée 2026 (ACPR n° 185) non lue | Les profils intègrent la hausse d'environ 130 pb du TEC 10 en 2026 et le spread OAT élargi ; à revoir dès que le n° 185 est accessible |
| Sorties annuelles (rachats et décès), année 1 | 6,0 % | 6,0 % | 6,0 % | Environ 6,7 % de l'encours, tous supports, décès compris (dérivé de France Assureurs, 2026) | Ordre de grandeur cohérent ; la collecte nette positive de 2026 justifie l'absence de vague de rachats |

## 6. Limites méthodologiques restantes

- **Lissage des pertes de crédit risque neutre : limite principale.** En risque neutre, tout le spread OAT (147 pb à 10 ans, 202 pb à 30 ans) devient une perte annuelle lissée, retirée chaque année et dans chaque scénario des produits financiers, donc de l'assiette de la participation. La valeur actuelle nette d'un achat reste nulle (tests). Mais la participation et les rachats sont non linéaires : cette répartition lisse des pertes déprime le taux servi partout. Le profil A, au rendement comptable faible, entre ainsi dans une spirale de rachats en équivalent certain (taux servi moyen de 0,8 % et rachats moyens de 22 % sur les années 1 à 20), et sa valeur devient négative. Un modèle de défaut par saut, avec perte en cas de défaut, donnerait la même valeur des actifs, mais concentrerait les pertes sur peu de scénarios et changerait le partage entre assurés et actionnaire. Le marché ne tranche pas entre les deux : c'est un risque de modèle à traiter avant les métriques de rentabilité.
- **Valeurs avant impôt.** L'impôt (25 %, contribution sociale de 3,3 % au-delà de l'abattement) est codé et testé, mais pas encore appliqué : les valeurs économiques sont donc présentées avant impôt différé.
- **Pas encore de capital.** Ni SCR ni marge de risque par profil, et pas encore de coût du capital : ils arrivent à l'étape suivante, avec la distinction entre coût réglementaire, coûts frictionnels et rendement exigé.
- **Générateur de scénarios non recalé.** Les paramètres de Hull-White (a = 0,05, sigma = 1 %) et la volatilité actions (18 %) restent ceux des V1 à V4, sans calage sur les volatilités implicites de marché : la TVOG en dépend directement.
- **Un seul model point par profil.** Le taux garanti est une moyenne ; la V4 multi-model points n'est pas couplée à l'actif. Le portefeuille est fermé : pas encore de collecte nouvelle, ni de politique de collecte pour C.
- **Crédit simplifié.** Toutes les obligations sont valorisées sur le spread OAT (souverains et entreprises confondus), sans notation ni migration, avec une perte en convention de recouvrement en valeur de marché. Le TEC est pris comme taux zéro-coupon, et la courbe EIOPA (31/10) est décalée de quatre jours avec le TEC (04/11).
- **Pertes risque neutre dans les produits comptables.** En valorisation, la perte risque neutre réduit les produits financiers, donc la participation : c'est cohérent avec le marché, mais la trajectoire comptable n'est pas une prévision.
- **Coupons par génération.** Ils sont ancrés sur des observations mensuelles ponctuelles et sur une prime d'achat calibrée. Les moyennes annuelles officielles n'ont pas été accessibles.
- **Comportement des assurés.** La référence « OAT 10 ans - 2 points », calée sur la situation de 2026, reste l'hypothèse la plus incertaine. Ses sensibilités changent la valeur actionnaire de plusieurs dizaines d'unités. Elle suit la courbe à terme de l'OAT, qui monte avec le spread : une référence fondée sur le taux sans risque, recalée au même niveau en t = 0, ramène le rachat moyen des années 1 à 20 à 13,9 % (A), 7,2 % (B), 5,4 % (C) et la valeur actionnaire en équivalent certain à 15,9 (A), 95,1 (B), 121,6 (C). La même convention commande la sensibilité aux taux : la référence suit le choc, une hausse accélère les rachats et raccourcit le passif. Duration effective du BE, en années : 1,2 (A), 1,8 (B), 3,9 (C), contre 7,0 (A), 10,1 (B), 13,0 (C) avec une référence figée. Ce point conditionnera directement les stratégies d'adossement.
- **Correction pour volatilité.** La VA est figée à 20 pb, sans VA dynamique ni ajustement égalisateur.
- **Données de place manquantes.** Moins-values latentes 2026, durations, réserve de capitalisation, répartition des garanties, rachats sur l'euro et dispersion entre organismes : voir `data/v5/profils/confrontation_acpr.md`.

