# V5 : conventions de crédit et de comportement, comparaison croisée sur les trois profils fictifs

Généré par `scripts/v5_rapport_conventions.py` depuis `resultats/v5_comparaison_conventions.json` (`scripts/v5_comparaison_conventions.py`) et `resultats/v5_solvabilite_profils.json` (`scripts/v5_solvabilite_profils.py`). Unités fictives : 1 unité = 10 M€, PM initiale de 1 000. Valorisation risque neutre au 31/10/2026, 1 000 scénarios, base sans VA sauf mention, valeurs avant impôt. Paramètres et statuts : `data/v5/conventions/conventions.json`. **Les profils A, B et C sont fictifs** : ils ne décrivent aucun organisme réel. Aucune stratégie n'est optimisée ici.

## 1. Données de place utilisées

| Thème | Valeur | Source | Statut |
| --- | --- | --- | --- |
| Rachats, supports en euros | 4,4 % en 2025 (4,8 % en 2024), rachats rapportés aux provisions de N-1 ; écart interquartile entre organismes réduit de 78 pb | ACPR, Analyses et synthèses n° 179, L'assurance-vie en 2025, graphiques 7 et 8 | observé ; quartiles du graphique 8 non lisibles dans le PDF |
| Rachats rapportés aux cotisations | 39,9 % au premier semestre 2026, plus bas depuis quinze ans (moyenne de long terme 58,6 %) | ACPR n° 185, chiffres repris par Tripalio (presse.tripalio.fr) | observé (source secondaire) ; PDF du n° 185 non consulté |
| Taux servi moyen 2025, contrats individuels | 2,63 % ; premier quartile 2,3 %, troisième quartile 2,9 % (organismes représentant 50 % des encours) | ACPR, Analyses et synthèses n° 180, p. 7 | observé |
| Taux servi par type d'organisme | bancassureurs 2,70 %, assureurs traditionnels 2,48 % | ACPR n° 180, p. 9-10 | observé |
| Rendement de l'actif (TRA) | 2,8 % en 2025 (2,5 % en 2024) ; la moitié des organismes entre 2,4 % et 3,3 % | ACPR n° 180, p. 13-14 | observé |
| PPB | 4,0 % des provisions fin 2025 ; bancassureurs 4,2 %, assureurs traditionnels 3,6 % | ACPR n° 180, p. 14 | observé |
| Taux technique moyen | 0,32 % (bancassureurs 0,25 %, traditionnels 0,39 %) | ACPR n° 180, p. 17 | observé |
| Chargements sur encours | 0,63 % ; premier quartile environ 0,5 %, troisième quartile environ 0,8 % | ACPR n° 180, p. 18 | observé |
| Livret A | 1,7 % depuis le 01/08/2026 (1,5 % au 01/02/2026) | ACPR n° 179, p. 2 ; jechange.fr | observé |
| Solvabilité au 30/06/2026 | 250 % pour l'ensemble, 239 % pour les organismes vie et mixtes, 219 % pour les bancassureurs | ACPR n° 185, chiffres repris par Tripalio | observé (source secondaire) |
| Sensibilité aux taux | la hausse des taux longs réduit davantage la valeur actuelle des engagements que celle des actifs | ACPR n° 181, p. 4 et 22 | observé (qualitatif) |
| Moins-values latentes 2026 | « près de -11 % » sur la dette souveraine française pour les bancassureurs, attribution à l'ACPR non certaine | Tripalio, article sur le premier semestre 2026 | non retenu : attribution incertaine |
| Notation des obligations des assureurs | AAA à AA- 20 %, A 61 %, BBB 18 % | ACPR n° 181, graphique 14 (part AAA à AA- de 47 % au T4 2024) | observé |
| Défauts annuels moyens (entreprises, 1981-2024) | AA 0,02 %, A 0,05 %, BBB 0,14 % | S&P Global Ratings, 2024 Annual Global Corporate Default And Rating Transition Study (31/03/2025), tableau 4, moyennes pondérées de long terme | observé |
| Décote moyenne des restructurations souveraines | 37 % (180 restructurations, 68 pays, 1970-2010) | Cruces et Trebesch, « Sovereign Defaults: The Price of Haircuts » (VoxEU) | observé |
| Rapport des intensités de défaut risque neutre / réelles | 2 en moyenne (souverains de la zone euro) | Augustin, Chernov et Song, « Sovereign Credit Risk and Exchange Rates: Evidence from CDS Quanto Spreads », NBER w24506 | observé (estimation publiée) |

**Non consulté** : le PDF de l'ACPR n° 185 et le classeur de données des graphiques de l'ACPR n° 179 (quartiles de rachat par organisme). Les moins-values latentes au 30/06/2026, les durations de place, la réserve de capitalisation de place, la répartition des garanties et les quartiles de rachat restent donc des paramètres fictifs des profils, testés en sensibilité, sans calibration inventée.

## 2. Décomposition du spread des obligations : risque neutre et probabilité réelle

Spread hypothétique de 126 pb à 10 ans. Part de crédit risque neutre kappa : hypothèse (0,7 au centre, bornes 0,55 et 1) ; le reste (1 - kappa) regroupe liquidité et offre de titres, non liés au défaut. Perte attendue réelle : probabilité de défaut annuelle moyenne pondérée par les notations du portefeuille des assureurs (S&P, ACPR) x perte en cas de défaut de 50 %.

| Composante (10 ans) | Niveau | Mesure | Statut | Traitement |
| --- | ---: | --- | --- | --- |
| Spread des obligations au-dessus de la courbe EIOPA sans VA | 126 pb | hypothèse (moyenne de long terme publiée par l'EIOPA, notation A) | hypothèse | prix de marché des obligations, inchangés dans toutes les conventions |
| Perte attendue réelle | 3 pb par an | réelle | calibré | seule perte constatée dans les projections en probabilité réelle |
| Prime de risque de crédit | 98 pb | écart risque neutre - réel | hypothèse (kappa) | rémunère le risque de défaut, n'est pas de la valeur créée |
| Composante hors défaut (liquidité, offre de titres) | 25 pb | hypothèse | hypothèse | coût risque neutre lissé dans la valorisation, prime en probabilité réelle |

Probabilités de défaut d'un bloc d'émetteurs : risque neutre, 1,97 % par an vers 10 ans (15,5 % sur 10 ans) en convention décomposée, 2,46 % par an (19,0 % sur 10 ans) si tout le spread est du crédit ; réelle, 0,061 % par an (environ 0,6 % sur 10 ans). L'écart, d'un facteur proche de 32, est la prime de risque : il dépasse nettement le rapport de 2 estimé sur les souverains de la zone euro, ce qui indique que le spread retenu rémunère surtout autre chose qu'une perte attendue historique : une prime pour le risque de défaut et une composante hors défaut. Les deux probabilités ne portent pas exactement sur le même objet (la probabilité réelle est tirée des défauts d'entreprises par notation, appliqués à la composition du portefeuille de place) : seul l'ordre de grandeur compte.

**Pourquoi la valorisation garde tout le spread comme coût risque neutre** : sans frictions, si une partie du spread n'était pas un coût en risque neutre, un investisseur qui garde le titre jusqu'à l'échéance l'encaisserait sans risque. Ce serait une valeur actuelle nette positive à l'achat, ce que le test de non-arbitrage interdit. La décomposition ne change donc pas le prix. Elle change trois choses : la forme des pertes risque neutre (lissées ou par saut), les trajectoires en probabilité réelle (seule la perte attendue réelle y est constatée) et la vue réglementaire (une VA ou un ajustement égalisateur reconnaît une partie de la composante hors défaut, ce qui reste une convention prudentielle).

## 3. Conventions comparées

**Crédit (valorisation, toutes à prix de marché identiques, tests de non-arbitrage dans `tests/test_v5_conventions.py`)**

| Code | Convention | Part par saut | Recouvrement | Blocs | Statut |
| --- | --- | ---: | ---: | --- | --- |
| `lisse_integral` | Spread intégralement en perte lissée (convention initiale) | 0 % | sans objet | sans objet | convention de valorisation |
| `saut_integral` | Spread intégralement en défaut par saut, recouvrement 40 % | 100 % | 40 % | 26 % souverain + 20 blocs diversifiés | hypothèse |
| `decompose` | Spread décomposé : 80 % crédit par saut (recouvrement 40 %), 20 % hors défaut lissé | 80 % | 40 % | 26 % souverain + 20 blocs diversifiés | hypothèse |
| `decompose_recouvrement_63` | Spread décomposé, recouvrement 63 % | 80 % | 63 % | 26 % souverain + 20 blocs diversifiés | hypothèse ; recouvrement = 1 - décote moyenne de Cruces et Trebesch |
| `saut_bloc_unique` | Spread intégralement par saut, tout le portefeuille en un seul bloc | 100 % | 40 % | un seul bloc | sensibilité de concentration extrême |

**Référence des assurés (toutes au même niveau en t = 0, 2,85 % : hypothèse de modélisation, non observée)**

| Code | Référence | Dynamique |
| --- | --- | --- |
| `oat_moins_2` | Taux à 10 ans des obligations du modèle - 2 points (ancienne référence) | suit la courbe à terme des obligations du modèle, spread compris |
| `sans_risque` | Taux sans risque 10 ans, même niveau en t = 0 (référence provisoire) | suit le taux sans risque 10 ans, transmission totale et immédiate |
| `sans_risque_demi` | Taux sans risque 10 ans, transmission de 50 % | moitié des variations du taux sans risque 10 ans |
| `taux_servi_marche` | Proxy comportemental fictif : taux sans risque 10 ans lissé sur 7 ans | taux sans risque 10 ans lissé, renouvellement de 1/7 par an (proxy comportemental fictif, non observé) |
| `livret_a` | Épargne réglementée : livret A (formule €STR et inflation) | moitié des variations du taux court (formule du livret A), plancher de 0,5 % |
| `figee` | Référence figée à son niveau initial | constante |

**Probabilité réelle (trajectoires de plausibilité, sans valorisation)** : taux et spreads figés à leur niveau de marché (marche aléatoire), prime actions de 3 % (fictive), quatre niveaux de pertes de crédit effectives : 3 pb par an (central), 10 pb par an, 50 % du spread à 10 ans (stress, rapport d'intensités de 2) et 100 % du spread (stress).

## 4. Résultats

### 4.1 Valeur actionnaire (actif - BE stochastique)

**Profil A**

| Référence | Lissé intégral | Saut intégral | Décomposé | Équivalent certain |
| --- | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | −6,3 ± 7,6 | −15,3 ± 7,6 | −13,5 ± 7,5 | 30,6 |
| Sans risque | −8,8 ± 7,3 | −17,7 ± 7,3 | −16,1 ± 7,2 | 25,7 |
| Sans risque, 50 % | 3,8 ± 4,4 | −5,5 ± 4,5 | −3,9 ± 4,5 | 27,1 |
| Proxy lissé sur 7 ans | 11,7 ± 5,7 | 0,9 ± 5,9 | 3,1 ± 5,9 | 27,2 |
| Livret A | 0,5 ± 4,0 | −9,6 ± 4,3 | −7,9 ± 4,3 | 23,7 |
| Figée | 28,4 ± 1,5 | 17,1 ± 2,1 | 20,1 ± 2,0 | 28,4 |

**Profil B**

| Référence | Lissé intégral | Saut intégral | Décomposé | Équivalent certain |
| --- | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | 59,9 ± 6,5 | 43,2 ± 7,6 | 46,6 ± 7,2 | 103,4 |
| Sans risque | 57,2 ± 6,3 | 41,5 ± 7,3 | 44,5 ± 7,0 | 98,2 |
| Sans risque, 50 % | 76,3 ± 4,1 | 60,3 ± 4,4 | 63,2 ± 4,4 | 99,3 |
| Proxy lissé sur 7 ans | 83,0 ± 5,4 | 65,2 ± 5,4 | 68,4 ± 5,3 | 99,0 |
| Livret A | 71,4 ± 3,5 | 55,9 ± 4,0 | 58,6 ± 3,8 | 91,5 |
| Figée | 99,4 ± 2,0 | 77,6 ± 2,6 | 80,7 ± 2,5 | 99,1 |

**Profil C**

| Référence | Lissé intégral | Saut intégral | Décomposé | Équivalent certain |
| --- | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | 84,5 ± 6,7 | 66,9 ± 7,7 | 70,0 ± 7,5 | 125,9 |
| Sans risque | 81,8 ± 6,5 | 65,3 ± 7,5 | 68,2 ± 7,3 | 122,3 |
| Sans risque, 50 % | 103,7 ± 4,2 | 85,6 ± 4,8 | 89,0 ± 4,8 | 122,7 |
| Proxy lissé sur 7 ans | 109,7 ± 4,9 | 90,1 ± 5,8 | 93,8 ± 5,7 | 122,1 |
| Livret A | 98,5 ± 3,7 | 81,5 ± 4,3 | 84,7 ± 4,2 | 115,1 |
| Figée | 123,1 ± 2,3 | 103,1 ± 3,1 | 106,5 ± 2,9 | 121,1 |

### 4.2 BE et TVOG

Convention de crédit décomposée. TVOG = BE stochastique - BE équivalent certain (même référence, même base). L'équivalent certain est identique pour toutes les conventions de crédit (perte moyenne).

| Référence | BE A | BE B | BE C | TVOG A | TVOG B | TVOG C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | 921,8 | 951,0 | 970,7 | 44,1 | 56,7 | 55,9 |
| Sans risque | 924,4 | 953,2 | 972,5 | 41,7 | 53,7 | 54,2 |
| Sans risque, 50 % | 912,3 | 934,5 | 951,7 | 31,0 | 36,1 | 33,8 |
| Proxy lissé sur 7 ans | 905,3 | 929,2 | 946,9 | 24,1 | 30,6 | 28,2 |
| Livret A | 916,3 | 939,0 | 956,0 | 31,6 | 32,8 | 30,4 |
| Figée | 888,2 | 917,0 | 934,2 | 8,2 | 18,4 | 14,6 |

Effet de la forme des pertes sur la TVOG (référence : proxy lissé sur 7 ans) :

| Crédit | TVOG A | TVOG B | TVOG C |
| --- | ---: | ---: | ---: |
| Lissé intégral | 15,5 | 16,1 | 12,4 |
| Saut intégral | 26,3 | 33,8 | 32,0 |
| Décomposé | 24,1 | 30,6 | 28,2 |

### 4.3 Rachats

Taux de rachat observé sur les supports en euros : 4,4 % en 2025 (ACPR n° 179). Hypothèse structurelle des V1 à V4 : 5 %.

| Référence | A, risque neutre (moyenne 1-10) | B, risque neutre (moyenne 1-10) | C, risque neutre (moyenne 1-10) | A, q95 du maximum annuel | B, q95 du maximum annuel | C, q95 du maximum annuel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | 14,0 % | 10,3 % | 9,4 % | 35 % | 35 % | 35 % |
| Sans risque | 14,4 % | 10,6 % | 9,7 % | 35 % | 35 % | 35 % |
| Sans risque, 50 % | 12,2 % | 8,0 % | 7,3 % | 35 % | 35 % | 35 % |
| Proxy lissé sur 7 ans | 11,5 % | 7,5 % | 6,8 % | 35 % | 34 % | 35 % |
| Livret A | 12,9 % | 8,7 % | 7,9 % | 35 % | 35 % | 35 % |
| Figée | 9,8 % | 6,8 % | 6,1 % | 18 % | 20 % | 24 % |

Un maximum de 35 % correspond au plafond de la loi de rachat (5 % structurel et 30 % conjoncturel) : il est atteint au moins une année dans plus de 5 % des scénarios pour toutes les références qui suivent les taux.

En probabilité réelle (trajectoire centrale, perte attendue de 3 pb), les rachats restent au niveau structurel : 5,0 % (A), 5,0 % (B), 5,0 % (C). Les rachats risque neutre ne sont pas une prévision : en risque neutre, les produits comptables sont nets de tout le coût du spread et le taux servi baisse dans la plupart des scénarios.

### 4.4 Liquidité

Convention décomposée. Sorties = décès + rachats, rapportées à la PM de début d'année ; moins-values réalisées = moins-values obligataires constatées lors des ventes pour payer les sorties, cumulées sur 10 ans.

| Référence | Profil | Sorties max, q95 | Moins-values réalisées, moyenne | Moins-values réalisées, q95 | Scénarios où elles dépassent la réserve de capitalisation |
| --- | --- | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | A | 36 % | 64,4 | 177,9 | 87 % |
| Obligations - 2 pts | B | 37 % | 24,1 | 95,3 | 41 % |
| Obligations - 2 pts | C | 37 % | 24,1 | 96,6 | 63 % |
| Sans risque | A | 36 % | 66,2 | 178,4 | 88 % |
| Sans risque | B | 37 % | 24,7 | 95,6 | 42 % |
| Sans risque | C | 37 % | 24,5 | 97,8 | 63 % |
| Proxy lissé sur 7 ans | A | 36 % | 40,2 | 127,9 | 85 % |
| Proxy lissé sur 7 ans | B | 35 % | 9,5 | 43,0 | 18 % |
| Proxy lissé sur 7 ans | C | 36 % | 10,3 | 47,7 | 44 % |
| Figée | A | 19 % | 25,0 | 70,3 | 84 % |
| Figée | B | 22 % | 6,2 | 23,4 | 11 % |
| Figée | C | 25 % | 7,2 | 25,1 | 44 % |

### 4.5 Apports de capital

Valeur actuelle des apports de l'actionnaire, par scénario (risque neutre).

| Référence | Crédit | Profil | Scénarios avec apport | Moyenne | Médiane | q95 | q99 | Moyenne si apport | Apport avant 10 ans |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans risque | Lissé intégral | A | 53 % | 22,9 | 3,7 | 79,9 | 116,4 | 43,3 | 21 % |
| Sans risque | Lissé intégral | B | 8 % | 3,7 | 0,0 | 10,1 | 41,9 | 47,2 | 1 % |
| Sans risque | Lissé intégral | C | 5 % | 2,9 | 0,0 | 0,0 | 31,3 | 61,5 | 1 % |
| Sans risque | Décomposé | A | 59 % | 30,6 | 9,7 | 109,0 | 191,0 | 51,8 | 20 % |
| Sans risque | Décomposé | B | 17 % | 9,1 | 0,0 | 44,6 | 130,6 | 54,4 | 3 % |
| Sans risque | Décomposé | C | 13 % | 6,5 | 0,0 | 28,1 | 105,0 | 51,1 | 2 % |
| Proxy lissé sur 7 ans | Lissé intégral | A | 34 % | 10,3 | 0,0 | 47,7 | 75,9 | 30,0 | 6 % |
| Proxy lissé sur 7 ans | Lissé intégral | B | 2 % | 1,7 | 0,0 | 0,0 | 19,4 | 81,1 | 0 % |
| Proxy lissé sur 7 ans | Lissé intégral | C | 1 % | 1,0 | 0,0 | 0,0 | 1,3 | 80,8 | 0 % |
| Proxy lissé sur 7 ans | Décomposé | A | 42 % | 19,0 | 0,0 | 89,0 | 169,1 | 45,0 | 6 % |
| Proxy lissé sur 7 ans | Décomposé | B | 12 % | 5,6 | 0,0 | 33,8 | 115,4 | 48,2 | 1 % |
| Proxy lissé sur 7 ans | Décomposé | C | 7 % | 3,6 | 0,0 | 15,1 | 78,8 | 49,6 | 0 % |
| Proxy lissé sur 7 ans | Saut intégral | A | 45 % | 21,9 | 0,0 | 100,1 | 163,6 | 48,5 | 7 % |
| Proxy lissé sur 7 ans | Saut intégral | B | 14 % | 6,6 | 0,0 | 41,3 | 116,7 | 46,3 | 1 % |
| Proxy lissé sur 7 ans | Saut intégral | C | 10 % | 3,9 | 0,0 | 15,2 | 83,8 | 41,5 | 0 % |

### 4.6 Sensibilité aux taux (équivalent certain, choc parallèle de ±5 pb)

| Référence | Duration BE A | Duration BE B | Duration BE C | Valeur pour +1 pb, A | Valeur pour +1 pb, B | Valeur pour +1 pb, C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Obligations - 2 pts | −0,1 | 4,6 | 3,1 | −0,60 | −0,16 | −0,41 |
| Sans risque | 1,1 | 1,5 | 5,7 | −0,49 | −0,43 | −0,17 |
| Sans risque, 50 % | 3,8 | 5,4 | 7,4 | −0,26 | −0,09 | −0,02 |
| Proxy lissé sur 7 ans | 3,3 | 4,7 | 6,8 | −0,30 | −0,15 | −0,07 |
| Livret A | 3,9 | 6,3 | 9,1 | −0,25 | −0,00 | 0,14 |
| Figée | 6,7 | 10,9 | 11,8 | −0,00 | 0,41 | 0,39 |

Duration effective de l'actif : 6,5 (A), 5,7 (B), 6,7 (C). Observation de place (ACPR n° 181) : la hausse des taux longs réduit davantage la valeur des engagements que celle des actifs, donc la valeur des assureurs monte quand les taux montent.

### 4.7 Variantes complémentaires (référence sans risque)

| Variante | Valeur A | Valeur B | Valeur C | Rachat moyen 1-10, A | Rachat moyen 1-10, B | Rachat moyen 1-10, C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Lissé intégral | −8,8 ± 7,3 | 57,2 ± 6,3 | 81,8 ± 6,5 | 15,5 % | 11,4 % | 10,0 % |
| Décomposé | −16,1 ± 7,2 | 44,5 ± 7,0 | 68,2 ± 7,3 | 14,4 % | 10,6 % | 9,7 % |
| Décomposé, recouvrement 63 % | −14,1 ± 7,3 | 47,4 ± 7,0 | 71,6 ± 7,1 | 14,7 % | 10,8 % | 9,8 % |
| Saut intégral, bloc unique | −42,6 ± 7,9 | −1,3 ± 8,3 | 17,8 ± 8,7 | 12,4 % | 8,4 % | 7,9 % |
| Lissé, niveau initial 2,63 % | −2,3 ± 7,6 | 63,6 ± 6,6 | 87,7 ± 6,8 | 14,3 % | 10,3 % | 9,2 % |
| Décomposé, niveau initial 2,63 % | −10,0 ± 7,6 | 49,5 ± 7,3 | 72,6 ± 7,6 | 13,2 % | 9,7 % | 8,9 % |
| Lissé, rachat structurel 4,4 % | −7,0 ± 8,0 | 59,4 ± 6,8 | 84,0 ± 6,9 | 14,8 % | 10,7 % | 9,3 % |
| Décomposé, rachat structurel 4,4 % | −14,7 ± 7,9 | 46,0 ± 7,5 | 69,6 ± 7,8 | 13,7 % | 9,9 % | 9,0 % |
| Décomposé, base avec VA | −6,2 ± 7,0 | 52,9 ± 6,9 | 76,3 ± 7,1 | 13,9 % | 10,0 % | 9,1 % |

### 4.8 Trajectoires en probabilité réelle (plausibilité, aucune valeur)

Taux et spreads figés, référence des assurés constante (toutes les références coïncident sur ces trajectoires). Comparaison de place : rendement de l'actif 2,8 % en 2025 (la moitié des organismes entre 2,4 % et 3,3 %), taux servi 2,63 % (quartiles 2,3 % et 2,9 %), rachats 4,4 %. Lecture : les rendements comptables encadrent la place (A au niveau moyen, C au-dessus du troisième quartile, ce qui correspond à son récit) ; les taux servis restent sous la moyenne de place parce que la règle de taux servi des V1 à V4 vise la référence moins 0,5 point (2,38 %), paramètre de stratégie qui sera un levier de l'étape suivante.

| Profil | Pertes de crédit effectives | Rendement comptable 1-10 | Taux servi 1-10 | Rachat 1-10 | PM à 10 ans | Apports cumulés | Fonds propres min. 1-10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Perte attendue réelle de 3 pb par an | 2,76 % | 2,31 % | 5,0 % | 680 | 0,0 | 50,2 |
| A | Perte attendue réelle de 10 pb par an | 2,69 % | 2,28 % | 5,0 % | 679 | 0,0 | 50,2 |
| A | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 2,14 % | 1,80 % | 6,1 % | 573 | 0,0 | 50,2 |
| A | Stress : tout le spread à 10 ans en pertes effectives | 1,08 % | 0,94 % | 13,3 % | 236 | 0,0 | 48,2 |
| B | Perte attendue réelle de 3 pb par an | 3,12 % | 2,35 % | 5,0 % | 683 | 0,0 | 56,5 |
| B | Perte attendue réelle de 10 pb par an | 3,06 % | 2,35 % | 5,0 % | 683 | 0,0 | 56,4 |
| B | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 2,74 % | 2,35 % | 5,0 % | 683 | 0,0 | 55,4 |
| B | Stress : tout le spread à 10 ans en pertes effectives | 2,33 % | 2,14 % | 5,0 % | 669 | 0,0 | 54,2 |
| C | Perte attendue réelle de 3 pb par an | 3,86 % | 2,75 % | 5,0 % | 710 | 0,0 | 68,1 |
| C | Perte attendue réelle de 10 pb par an | 3,80 % | 2,69 % | 5,0 % | 706 | 0,0 | 68,0 |
| C | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 3,35 % | 2,35 % | 5,0 % | 683 | 0,0 | 67,0 |
| C | Stress : tout le spread à 10 ans en pertes effectives | 3,03 % | 2,35 % | 5,0 % | 683 | 0,0 | 66,0 |

### 4.9 Vue prudentielle simplifiée (base avec VA)

Calcul pédagogique inspiré de la formule standard (`src/v5/solvabilite_v5.py`) : taux, actions, spread (part non souveraine, notation A), rachat ; absorption par les FDB ; marge de risque à 6 %. Hors calcul : risque opérationnel, absorption par les impôts différés, fonds excédentaires (borne haute indicative donnée à part).

| Profil | Référence | Crédit | Actif | BE | Marge de risque | Fonds propres | SCR | dont marché net | dont rachat net | Ratio | Ratio après impôts différés | Fonds excédentaires, borne haute |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Sans risque, 50 % | Décomposé | 908,4 | 901,1 | 19,0 | −11,7 | 89,2 | 66,8 | 37,2 | −13 % | 5 % | 18,5 |
| A | Sans risque | Décomposé | 908,4 | 914,6 | 14,0 | −20,2 | 86,8 | 69,0 | 31,1 | −23 % | −2 % | 18,5 |
| A | Sans risque | Lissé intégral | 908,4 | 907,0 | 15,1 | −13,7 | 97,6 | 72,1 | 35,6 | −14 % | 3 % | 18,5 |
| A | Proxy lissé sur 7 ans | Décomposé | 908,4 | 894,4 | 21,1 | −7,1 | 88,5 | 65,0 | 39,1 | −8 % | 9 % | 18,5 |
| B | Sans risque, 50 % | Décomposé | 997,6 | 924,1 | 24,4 | 49,1 | 82,6 | 68,2 | 32,7 | 59 % | 64 % | 29,7 |
| B | Sans risque | Décomposé | 997,6 | 944,8 | 14,5 | 38,4 | 69,9 | 59,6 | 24,5 | 55 % | 65 % | 29,7 |
| B | Sans risque | Lissé intégral | 997,6 | 931,6 | 17,1 | 49,0 | 74,5 | 61,1 | 30,0 | 66 % | 71 % | 29,7 |
| B | Proxy lissé sur 7 ans | Décomposé | 997,6 | 919,1 | 26,0 | 52,5 | 80,2 | 64,2 | 34,5 | 65 % | 70 % | 29,7 |
| C | Sans risque, 50 % | Décomposé | 1 040,7 | 942,7 | 19,0 | 79,1 | 75,1 | 65,8 | 23,3 | 105 % | 100 % | 14,8 |
| C | Sans risque | Décomposé | 1 040,7 | 964,5 | 9,2 | 67,1 | 65,5 | 60,5 | 14,2 | 102 % | 102 % | 14,8 |
| C | Sans risque | Lissé intégral | 1 040,7 | 950,3 | 12,7 | 77,8 | 70,0 | 62,3 | 20,0 | 111 % | 106 % | 14,8 |
| C | Proxy lissé sur 7 ans | Décomposé | 1 040,7 | 938,2 | 20,5 | 82,0 | 74,6 | 64,2 | 25,1 | 110 % | 104 % | 14,8 |

Lecture :

- **Écart massif avec la place.** Ratios approchés dans la convention centrale : −8 % (A), 65 % (B), 110 % (C), contre 239 % pour les organismes vie et mixtes au 30/06/2026. B, conçu pour être proche de la place sur la PPB, le taux technique et le taux servi, en est très loin en solvabilité.
- **Ce qui manque au calcul et jouerait en faveur des profils** : fonds excédentaires (jusqu'à 18,5 pour A, 29,7 pour B, 14,8 pour C), absorption par les impôts différés, ajustement symétrique du choc actions. Ce qui est peut-être trop sévère : un choc de spread en notation A sur 66 % des obligations (40,0 pour A, 36,8 pour B, 37,0 pour C de perte nette), et la règle de taux servi des V1 à V4, qui fait renoncer l'assureur à sa marge pour suivre la référence, ce qui réduit l'absorption par les FDB.
- **Ce qui vient des profils** : à l'ouverture, l'actif en valeur de marché est inférieur à la PM et à la PPB pour A et B ; les moins-values obligataires (−18 % pour A, −13 % pour B, −6 % pour C de la VNC) et les fonds propres comptables (4,5 % à 6,0 % de la PM) sont des paramètres fictifs que la donnée de place 2026 (ACPR n° 185, non lue) permettrait de confronter.
- **Choc de taux** : la hausse des taux est le choc le plus coûteux dans 11 conventions calculées sur 12 ; au centre, perte nette en hausse et en baisse de 13,7 et 0,3 pour A, 6,9 et 5,5 pour B, 9,9 et 2,5 pour C. La place, elle, gagne quand les taux montent ; l'écart de sensibilité apparaît aussi dans les durations de la section 4.6.
- **Profil A** : fonds propres prudentiels négatifs dans toutes les conventions calculées ; en lecture réglementaire, ce serait un organisme à recapitaliser ou en plan de rétablissement, quelle que soit la convention de crédit ou de comportement retenue ici.

## 5. Résultats robustes et résultats fragiles

Sur les 25 combinaisons de convention calculées pour chaque profil :

| Constat | Vérifié dans | Lecture |
| --- | ---: | --- |
| Classement des valeurs A < B < C | 25 / 25 | robuste : le classement des bilans ne dépend d'aucune convention |
| Classement des rachats A > B > C | 25 / 25 | robuste |
| Classement des apports A > B > C (part des scénarios) | 25 / 25 | robuste |
| Défaut par saut intégral < lissé intégral (valeur) | 18 / 18 | robuste : concentrer les pertes réduit la valeur actionnaire |
| Décomposé entre les deux | 18 / 18 | robuste |
| TVOG positive | 52 / 54 | presque toujours ; exceptions : B, figée, lissé intégral (−0,3) ; C, figée, lissé intégral (−2,0). L'équivalent certain n'est pas la trajectoire moyenne d'un modèle non linéaire : sans rachat lié aux taux, la dispersion des taux peut jouer en faveur de l'actionnaire |
| Signe de la valeur du profil A | 8 positives / 25 | **fragile : change de signe** (de −42,6 à 28,4) |
| Signe de la valeur du profil B | 24 positives / 25 | **fragile : change de signe** (de −1,3 à 99,4) |
| Signe de la valeur du profil C | 25 positives / 25 | toujours positive (de 17,8 à 123,1) |
| Classement des références par valeur | 1 classement(s) différent(s) sur 9 | identique pour tous les profils et crédits |
| Signe de la sensibilité de la valeur aux taux | Obligations - 2 pts -, Sans risque -, Sans risque, 50 % -, Proxy lissé sur 7 ans -, Livret A ±, Figée ± | **fragile : change de signe avec la référence** |

Classement des références, de la valeur la plus basse à la plus haute (convention décomposée) : A : Sans risque < Obligations - 2 pts < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée ; B : Sans risque < Obligations - 2 pts < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée ; C : Sans risque < Obligations - 2 pts < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée.

## 6. Profil A : assureur en difficulté ou conséquence des hypothèses ?

Trois lectures, à ne pas confondre :

1. **Comptable** : le profil A est solvable. Ses fonds propres comptables (45) et sa réserve de capitalisation (5) sont positifs, et aucune perte n'est constatée à l'ouverture.
2. **Valeur de marché à l'ouverture** : l'actif en valeur de marché ne couvre pas la PM et la PPB. L'écart vaut −116,6 pour A (−42,4 pour B, 20,7 pour C). Comme un assuré qui rachète reçoit sa PM sans supporter les moins-values, A ne tient que si ses assurés restent : c'est la définition d'un assureur exposé au rachat massif.
3. **Valeur économique simplifiée** (actif - BE, sans VA, avant impôt et marge de risque) : de −42,6 à 28,4 selon les conventions. Elle est négative dans 17 combinaisons sur 25, et vaut 3,1 ± 5,9 dans la convention centrale proposée. Elle n'est positive qu'avec une référence figée (aucun rachat lié aux taux) ou avec un spread entièrement lissé et une référence lissée, et reste alors au plus de 28,4, soit moins de la moitié des fonds propres comptables.

**Apports de capital (risque neutre, convention centrale)** : un apport dans 42 % des scénarios ; valeur actuelle moyenne 19,0, médiane 0,0, q95 89,0, q99 169,1.
Les apports sont tardifs : 0 % des scénarios en ont un avant 5 ans, 6 % des scénarios en ont un avant 10 ans, première année médiane 16. Ils viennent surtout de deux sources. Dans les 17 % de scénarios où le bloc souverain fait défaut avant 10 ans (probabilité risque neutre), 91 % demandent un apport (moyenne 60,0), contre 32 % sans défaut (moyenne 10,5). Côté taux, 57 % des scénarios du tiers des taux 10 ans les plus hauts en année 5 demandent un apport, contre 36 % dans le tiers le plus bas : cela s'explique par la référence des assurés, qui suit les taux, et par les ventes d'obligations en moins-value pour payer les rachats.

**Probabilité réelle** : sur la trajectoire centrale (taux et spreads figés, perte attendue de 3 pb), A sert 2,31 % en moyenne sur 10 ans, au niveau du premier quartile de place (2,3 %). Ses rachats restent à 5,0 % et il n'a besoin d'aucun apport (fonds propres minimaux de 50,2). Même si tout le spread devenait une perte effective, il servirait 0,94 %, ses rachats monteraient à 13,3 % par an et sa PM tomberait à 236 en 10 ans, mais il garderait des fonds propres de 48,2 au minimum, sans apport sur cette trajectoire.

**Vue prudentielle simplifiée** (base avec VA, marge de risque, SCR approché) : fonds propres de −7,1, SCR de 88,5, ratio approché de −8 % (fonds excédentaires non comptés, borne haute indicative de 18,5). Le ratio de place est de 239 % pour les organismes vie et mixtes au 30/06/2026.

**Conclusion.** Le profil A n'est pas un assureur normalement viable, et il ne faut pas le présenter ainsi. Comptablement solvable et sans besoin de capital sur une trajectoire réelle centrale, il n'a plus de coussin économique : sa valeur est proche de zéro ou négative, et il demande des apports dans une large part des scénarios risque neutre, dans les scénarios de hausse des taux et de défaut souverain. Une partie de ce résultat est construite : ses moins-values obligataires (−18 % de la VNC) sont volontairement en haut de fourchette, et la donnée de place 2026 manque (ACPR n° 185 non lue). Une autre partie vient du modèle : en risque neutre, les produits comptables sont nets de tout le coût du spread, si bien que le taux servi et les rachats risque neutre ne sont pas des prévisions. Proposition : garder A comme profil de stress, qualifié d'**assureur fragile, au seuil de la recapitalisation**, et analyser ses stratégies sous contrainte de capital (apports, plan de redressement) plutôt que comme celles d'un assureur en régime normal.

## 7. Convention centrale proposée et stress à conserver

**Convention centrale proposée (à valider)**

| Élément | Choix | Justification |
| --- | --- | --- |
| Valorisation | Base sans VA ; VA en vue réglementaire seulement | Valeur économique sans effet réglementaire ; effet VA présenté à part (+9,9 pour A, +8,4 pour B, +8,1 pour C) |
| Forme des pertes de crédit | Décomposée : 80 % du spread en défaut par saut (recouvrement 40 %, bloc souverain de 26 %), 20 % en coût hors défaut lissé | Prix inchangés et absence d'arbitrage vérifiée ; forme cohérente avec un risque souverain concentré et peu probable, et avec un crédit d'entreprise diversifié ; part de crédit : hypothèse |
| Probabilité réelle | Perte attendue de 3 pb par an ; le reste du spread est une prime | Défauts historiques par notation et composition du portefeuille de place ; la prime n'est jamais comptée comme de la valeur |
| Référence des assurés | Proxy comportemental fictif (et non taux servi observé) : taux sans risque 10 ans lissé (1/7 par an), niveau initial 2,85 % (hypothèse) | Cohérente en risque neutre (un concurrent investi dans les mêmes titres gagne le taux sans risque et renouvelle progressivement son portefeuille). Les taux servis observés bougent lentement (2,63 % en 2024 et en 2025). Sensibilité aux taux intermédiaire : duration du BE de 3,3 à 6,8 ans, contre 1,1 à 5,7 avec une transmission immédiate |
| Rachat structurel | À trancher : 5 % (V1 à V4) ou 4,4 % (taux observé de 2025, identique pour les trois profils) | Effet sur la valeur stochastique dans l'erreur de Monte-Carlo (+1,4 pour A, +1,6 pour B, +1,4 pour C) ; aucun calage propre au profil A |

Valeurs dans cette convention : A 3,1 ± 5,9 (TVOG 24,1, apports dans 42 % des scénarios), B 68,4 ± 5,3 (TVOG 30,6, apports dans 12 % des scénarios), C 93,8 ± 5,7 (TVOG 28,2, apports dans 7 % des scénarios).

**Avant les métriques de rentabilité**, deux écarts avec la place restent à traiter. D'abord la solvabilité : les ratios approchés (section 4.9) sont très inférieurs aux 239 % de la place. Il faudra compléter la vue prudentielle (fonds excédentaires, impôts différés, ajustement symétrique) et confronter les fonds propres et les moins-values des profils à l'ACPR n° 185 dès que le document sera disponible.

Ensuite la sensibilité aux taux. Même la référence lissée donne une valeur qui baisse quand les taux montent (−0,30 par pb pour A, −0,15 par pb pour B, −0,07 par pb pour C), alors que la place observe l'inverse (ACPR n° 181). L'écart peut venir de la loi de rachat (paramètres des V1 à V4, non recalés), de la règle de taux servi (cible égale à la référence moins 0,5 point) ou de l'absence de fonds excédentaires et d'impôts différés. Il faudra le traiter avant d'optimiser les stratégies d'adossement.

**Stress à conserver pour la suite de la V5**

| Stress | Paramétrage | Ce qu'il teste |
| --- | --- | --- |
| Transmission immédiate des taux longs | Référence sans risque, beta = 1 | Rachats dynamiques en hausse des taux (valeur de A : −16,1 contre 3,1 au centre) |
| Référence figée | Pas de rachat lié aux taux | Borne opposée ; isole le risque de garantie et de taux servi |
| Livret A | Référence pilotée par le taux court | Concurrence de l'épargne réglementée (valeur de A : −7,9) |
| Spread intégralement lissé | Convention initiale | Transfert maximal des pertes de crédit aux assurés par le taux servi |
| Spread intégralement par saut, bloc unique | Tout le portefeuille fait défaut d'un coup | Concentration extrême (valeur de B : −1,3 ± 8,3) ; erreur de Monte-Carlo élevée, à recalculer avec plus de scénarios |
| Recouvrement 63 % | Décote souveraine moyenne de 37 % | Sensibilité au recouvrement (effet modéré) |
| Pertes effectives de 50 % du spread | Probabilité réelle, 10 ans | Assureur qui subit vraiment une partie du risque de crédit : taux servi, rachats, fonds propres |
| Défaut souverain déterministe | Défaut du bloc de 26 % en année 2, recouvrement 40 % (perte de 15,6 % des obligations) | Événement unique, lisible, pour comparer les stratégies (à construire) |
| Niveau initial de la référence à 2,63 % | Dernier taux servi moyen observé | Le niveau de 2,85 % est une hypothèse |
| Chocs de la formule standard | Taux, actions, spread, rachat massif (vue prudentielle) | Capital et absorption par les FDB |

## 8. Limites restantes

- **Monte-Carlo.** Le défaut par saut augmente la variance : la demi-largeur de l'intervalle de la fuite atteint 5,6 avec 1 000 scénarios, et de 11,2 à 15,0 pour le bloc unique. Les fuites sont positives dans 75 variantes sur 75 (mêmes tirages de taux et de défaut partout), toujours à l'intérieur de leur intervalle de confiance à 95 % (au plus 0,99 fois sa demi-largeur). Les écarts de valeur entre spread lissé et spread par saut (de 8,9 à 21,7) dépassent cette erreur ; le bloc unique demande plus de scénarios.
- **Rachats risque neutre et rachats observés.** Les rachats moyens risque neutre (de 5 % à 15 % par an sur 10 ans selon le profil et les conventions) dépassent le taux observé de 4,4 %. Ce n'est pas une contradiction : en risque neutre, les produits comptables sont nets du coût du spread. Mais la loi de rachat dynamique (paramètres des V1 à V4) n'est calée sur aucune donnée de place, et les quartiles de rachat par organisme (ACPR n° 179) n'ont pas pu être lus.
- **Part de crédit du spread (kappa = 0,8 dans ces premières conventions, 0,7 dans la convention centrale).** C'est une hypothèse, sans recoupement avec des cotations de marché : le spread des obligations est lui-même une hypothèse. Ce n'est pas une estimation du risque de défaut des émetteurs, souverains ou entreprises : kappa répartit seulement le spread hypothétique entre une perte par défaut et une perte hors défaut.
- **Défaut par saut simplifié.** Recouvrement de 40 % (convention de cotation non vérifiée en ligne), blocs indépendants, réinvestissement immédiat dans le même portefeuille (défauts répétés possibles), ni migration de notation ni spread stochastique : la courbe de spread reste figée, sans dynamique propre.
- **Un seul spread pour toutes les obligations.** Souverains, financières et entreprises partagent le même spread hypothétique (notation A).
- **Probabilité réelle.** Taux et spreads figés, prime actions fictive de 3 % : ces trajectoires servent à la plausibilité, pas à la prévision.
- **Vue prudentielle.** Choc de taux appliqué à la courbe avec VA, ajustement symétrique nul, spread en notation A sur 66 % des obligations, pas de risque opérationnel, pas d'absorption par les impôts différés ni de fonds excédentaires : c'est un ordre de grandeur, pas un ratio de solvabilité.
- **Données de place manquantes.** ACPR n° 185 (moins-values latentes au 30/06/2026) et quartiles de rachat de l'ACPR n° 179 : les paramètres correspondants des profils restent fictifs.
- **Avant impôt.** L'impôt est codé et testé mais pas appliqué.

