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
| CDS France 5 ans | 91 pb le 29/10/2026 (plus haut 104 pb le 23/10) | epargnebourse.fr, suivi hebdomadaire du CDS France 5 ans, consulté le 06/11/2026 | observé (source secondaire) |
| Spread OAT-Bund 10 ans | 163 pb le 30/10/2026 | epargnebourse.fr, consulté le 06/11/2026 | observé (source secondaire) |
| Notation des obligations des assureurs | AAA à AA- 20 %, A 61 %, BBB 18 % | ACPR n° 181, graphique 14 (part AAA à AA- de 47 % au T4 2024) | observé |
| Défauts annuels moyens (entreprises, 1981-2024) | AA 0,02 %, A 0,05 %, BBB 0,14 % | S&P Global Ratings, 2024 Annual Global Corporate Default And Rating Transition Study (31/03/2025), tableau 4, moyennes pondérées de long terme | observé |
| Décote moyenne des restructurations souveraines | 37 % (180 restructurations, 68 pays, 1970-2010) | Cruces et Trebesch, « Sovereign Defaults: The Price of Haircuts » (VoxEU) | observé |
| Rapport des intensités de défaut risque neutre / réelles | 2 en moyenne (souverains de la zone euro) | Augustin, Chernov et Song, « Sovereign Credit Risk and Exchange Rates: Evidence from CDS Quanto Spreads », NBER w24506 | observé (estimation publiée) |

**Non consulté** : le PDF de l'ACPR n° 185 et le classeur de données des graphiques de l'ACPR n° 179 (quartiles de rachat par organisme). Les moins-values latentes au 30/06/2026, les durations de place, la réserve de capitalisation de place, la répartition des garanties et les quartiles de rachat restent donc des paramètres fictifs des profils, testés en sensibilité, sans calibration inventée.

## 2. Décomposition du spread OAT : risque neutre et probabilité réelle

Spread de 147 pb à 10 ans. Part de crédit risque neutre kappa : le CDS France à 5 ans (91 pb le 29/10/2026) couvre presque tout le spread à 5 ans (92 pb le 04/11/2026), mais sa cotation en dollars surestime la composante de crédit en euros ; kappa central 0,8, bornes 0,7 et 1. Le reste (1 - kappa) regroupe liquidité, offre de titres et effets de change non liés au défaut. Perte attendue réelle : probabilité de défaut annuelle moyenne pondérée par les notations du portefeuille des assureurs (S&P, ACPR) x perte en cas de défaut de 50 %.

| Composante (10 ans) | Niveau | Mesure | Statut | Traitement |
| --- | ---: | --- | --- | --- |
| Spread OAT au-dessus de la courbe EIOPA sans VA | 147 pb | marché | calibré | prix de marché des obligations, inchangés dans toutes les conventions |
| Perte attendue réelle | 3 pb par an | réelle | calibré | seule perte constatée dans les projections en probabilité réelle |
| Prime de risque de crédit | 115 pb | écart risque neutre - réel | hypothèse (kappa) | rémunère le risque de défaut, n'est pas de la valeur créée |
| Composante hors défaut (liquidité, offre, change) | 29 pb | marché | hypothèse | coût risque neutre lissé dans la valorisation, prime en probabilité réelle |

Probabilités de défaut d'un bloc d'émetteurs : risque neutre, 3,26 % par an vers 10 ans (17,9 % sur 10 ans) en convention décomposée, 4,06 % par an (21,9 % sur 10 ans) si tout le spread est du crédit ; réelle, 0,061 % par an (environ 0,6 % sur 10 ans). L'écart, d'un facteur proche de 53, est la prime de risque : il dépasse nettement le rapport de 2 estimé sur les souverains de la zone euro, ce qui indique que le spread français de 2026 rémunère surtout autre chose qu'une perte attendue historique : une prime pour un risque de queue (politique et budgétaire) et une composante hors défaut. Les deux probabilités ne portent pas exactement sur le même objet (la probabilité réelle est tirée des défauts d'entreprises par notation, appliqués à la composition du portefeuille de place) : seul l'ordre de grandeur compte.

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

**Référence des assurés (toutes au même niveau en t = 0, 2,88 % : hypothèse de modélisation, non observée)**

| Code | Référence | Dynamique |
| --- | --- | --- |
| `oat_moins_2` | OAT 10 ans - 2 points (ancienne référence) | suit la courbe à terme de l'OAT, spread à terme compris |
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
| OAT - 2 pts | −30,1 ± 6,5 | −37,0 ± 6,4 | −35,9 ± 6,4 | −6,0 |
| Sans risque | −18,3 ± 7,2 | −25,9 ± 7,4 | −24,5 ± 7,3 | 15,9 |
| Sans risque, 50 % | −6,5 ± 4,3 | −14,9 ± 4,5 | −13,5 ± 4,5 | 17,2 |
| Proxy lissé sur 7 ans | 1,3 ± 5,7 | −7,9 ± 5,9 | −5,9 ± 5,9 | 17,4 |
| Livret A | −9,3 ± 3,8 | −18,7 ± 4,2 | −17,2 ± 4,2 | 13,7 |
| Figée | 18,2 ± 1,2 | 9,2 ± 1,9 | 12,1 ± 1,7 | 18,6 |

**Profil B**

| Référence | Lissé intégral | Saut intégral | Décomposé | Équivalent certain |
| --- | ---: | ---: | ---: | ---: |
| OAT - 2 pts | 43,7 ± 5,5 | 30,4 ± 6,1 | 33,2 ± 5,9 | 66,6 |
| Sans risque | 59,2 ± 6,2 | 42,4 ± 7,0 | 46,0 ± 6,7 | 95,1 |
| Sans risque, 50 % | 76,4 ± 4,0 | 59,7 ± 4,3 | 63,3 ± 4,2 | 94,8 |
| Proxy lissé sur 7 ans | 82,6 ± 5,3 | 64,7 ± 5,5 | 68,5 ± 5,4 | 95,2 |
| Livret A | 71,6 ± 3,2 | 55,2 ± 3,8 | 58,6 ± 3,6 | 88,0 |
| Figée | 101,3 ± 1,9 | 77,7 ± 2,5 | 81,5 ± 2,3 | 94,2 |

**Profil C**

| Référence | Lissé intégral | Saut intégral | Décomposé | Équivalent certain |
| --- | ---: | ---: | ---: | ---: |
| OAT - 2 pts | 67,7 ± 5,2 | 54,0 ± 6,2 | 56,5 ± 5,9 | 88,9 |
| Sans risque | 84,0 ± 6,0 | 65,1 ± 7,1 | 68,7 ± 6,9 | 121,6 |
| Sans risque, 50 % | 103,8 ± 3,9 | 84,5 ± 4,6 | 88,8 ± 4,4 | 119,9 |
| Proxy lissé sur 7 ans | 110,1 ± 4,7 | 89,7 ± 5,3 | 94,2 ± 5,1 | 120,3 |
| Livret A | 98,4 ± 3,3 | 80,2 ± 4,1 | 84,0 ± 3,9 | 109,8 |
| Figée | 126,2 ± 2,3 | 103,1 ± 3,0 | 107,4 ± 2,8 | 118,1 |

### 4.2 BE et TVOG

Convention de crédit décomposée. TVOG = BE stochastique - BE équivalent certain (même référence, même base). L'équivalent certain est identique pour toutes les conventions de crédit (perte moyenne).

| Référence | BE A | BE B | BE C | TVOG A | TVOG B | TVOG C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OAT - 2 pts | 935,7 | 959,6 | 972,4 | 29,9 | 33,4 | 32,5 |
| Sans risque | 924,2 | 946,7 | 960,1 | 40,3 | 49,1 | 52,9 |
| Sans risque, 50 % | 913,2 | 929,4 | 940,0 | 30,7 | 31,5 | 31,1 |
| Proxy lissé sur 7 ans | 905,7 | 924,2 | 934,6 | 23,4 | 26,7 | 26,0 |
| Livret A | 917,0 | 934,2 | 944,8 | 30,9 | 29,4 | 25,7 |
| Figée | 887,6 | 911,3 | 921,4 | 6,5 | 12,7 | 10,6 |

Effet de la forme des pertes sur la TVOG (référence : proxy lissé sur 7 ans) :

| Crédit | TVOG A | TVOG B | TVOG C |
| --- | ---: | ---: | ---: |
| Lissé intégral | 16,1 | 12,6 | 10,2 |
| Saut intégral | 25,3 | 30,5 | 30,5 |
| Décomposé | 23,4 | 26,7 | 26,0 |

### 4.3 Rachats

Taux de rachat observé sur les supports en euros : 4,4 % en 2025 (ACPR n° 179). Hypothèse structurelle des V1 à V4 : 5 %.

| Référence | A, risque neutre (moyenne 1-10) | B, risque neutre (moyenne 1-10) | C, risque neutre (moyenne 1-10) | A, q95 du maximum annuel | B, q95 du maximum annuel | C, q95 du maximum annuel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OAT - 2 pts | 17,8 % | 13,9 % | 12,8 % | 35 % | 35 % | 35 % |
| Sans risque | 14,6 % | 11,2 % | 10,5 % | 35 % | 35 % | 35 % |
| Sans risque, 50 % | 12,5 % | 8,7 % | 8,0 % | 35 % | 35 % | 35 % |
| Proxy lissé sur 7 ans | 11,8 % | 8,1 % | 7,5 % | 35 % | 35 % | 35 % |
| Livret A | 13,1 % | 9,3 % | 8,6 % | 35 % | 35 % | 35 % |
| Figée | 10,2 % | 7,4 % | 6,8 % | 18 % | 21 % | 24 % |

Un maximum de 35 % correspond au plafond de la loi de rachat (5 % structurel et 30 % conjoncturel) : il est atteint au moins une année dans plus de 5 % des scénarios pour toutes les références qui suivent les taux.

En probabilité réelle (trajectoire centrale, perte attendue de 3 pb), les rachats restent au niveau structurel : 5,0 % (A), 5,0 % (B), 5,0 % (C). Les rachats risque neutre ne sont pas une prévision : en risque neutre, les produits comptables sont nets de tout le coût du spread et le taux servi baisse dans la plupart des scénarios.

### 4.4 Liquidité

Convention décomposée. Sorties = décès + rachats, rapportées à la PM de début d'année ; moins-values réalisées = moins-values obligataires constatées lors des ventes pour payer les sorties, cumulées sur 10 ans.

| Référence | Profil | Sorties max, q95 | Moins-values réalisées, moyenne | Moins-values réalisées, q95 | Scénarios où elles dépassent la réserve de capitalisation |
| --- | --- | ---: | ---: | ---: | ---: |
| OAT - 2 pts | A | 36 % | 90,2 | 200,2 | 95 % |
| OAT - 2 pts | B | 37 % | 37,1 | 117,9 | 59 % |
| OAT - 2 pts | C | 37 % | 38,5 | 125,9 | 77 % |
| Sans risque | A | 36 % | 74,3 | 194,2 | 90 % |
| Sans risque | B | 37 % | 28,7 | 107,0 | 47 % |
| Sans risque | C | 37 % | 31,8 | 116,6 | 72 % |
| Proxy lissé sur 7 ans | A | 36 % | 45,2 | 141,5 | 87 % |
| Proxy lissé sur 7 ans | B | 36 % | 11,8 | 49,8 | 24 % |
| Proxy lissé sur 7 ans | C | 36 % | 14,3 | 63,5 | 57 % |
| Figée | A | 19 % | 26,9 | 71,8 | 89 % |
| Figée | B | 22 % | 8,0 | 30,2 | 17 % |
| Figée | C | 25 % | 10,0 | 34,2 | 57 % |

### 4.5 Apports de capital

Valeur actuelle des apports de l'actionnaire, par scénario (risque neutre).

| Référence | Crédit | Profil | Scénarios avec apport | Moyenne | Médiane | q95 | q99 | Moyenne si apport | Apport avant 10 ans |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sans risque | Lissé intégral | A | 61 % | 28,5 | 13,4 | 87,6 | 127,3 | 47,1 | 23 % |
| Sans risque | Lissé intégral | B | 9 % | 4,0 | 0,0 | 13,4 | 48,7 | 45,6 | 1 % |
| Sans risque | Lissé intégral | C | 6 % | 2,8 | 0,0 | 2,3 | 37,3 | 48,8 | 1 % |
| Sans risque | Décomposé | A | 66 % | 36,4 | 20,4 | 116,8 | 188,9 | 55,1 | 23 % |
| Sans risque | Décomposé | B | 19 % | 8,7 | 0,0 | 46,7 | 108,7 | 45,1 | 4 % |
| Sans risque | Décomposé | C | 13 % | 6,0 | 0,0 | 31,9 | 86,9 | 44,7 | 3 % |
| Proxy lissé sur 7 ans | Lissé intégral | A | 46 % | 14,4 | 0,0 | 57,1 | 82,1 | 31,4 | 7 % |
| Proxy lissé sur 7 ans | Lissé intégral | B | 3 % | 1,7 | 0,0 | 0,0 | 18,6 | 66,7 | 0 % |
| Proxy lissé sur 7 ans | Lissé intégral | C | 2 % | 1,0 | 0,0 | 0,0 | 8,3 | 65,6 | 0 % |
| Proxy lissé sur 7 ans | Décomposé | A | 50 % | 23,6 | 0,9 | 98,5 | 175,2 | 46,7 | 7 % |
| Proxy lissé sur 7 ans | Décomposé | B | 12 % | 5,5 | 0,0 | 31,1 | 99,5 | 44,5 | 1 % |
| Proxy lissé sur 7 ans | Décomposé | C | 8 % | 3,3 | 0,0 | 14,6 | 63,4 | 39,7 | 1 % |
| Proxy lissé sur 7 ans | Saut intégral | A | 52 % | 26,1 | 2,0 | 104,4 | 174,6 | 50,8 | 8 % |
| Proxy lissé sur 7 ans | Saut intégral | B | 15 % | 6,4 | 0,0 | 38,6 | 97,7 | 41,7 | 1 % |
| Proxy lissé sur 7 ans | Saut intégral | C | 10 % | 3,8 | 0,0 | 20,6 | 75,6 | 37,3 | 1 % |

### 4.6 Sensibilité aux taux (équivalent certain, choc parallèle de ±5 pb)

| Référence | Duration BE A | Duration BE B | Duration BE C | Valeur pour +1 pb, A | Valeur pour +1 pb, B | Valeur pour +1 pb, C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OAT - 2 pts | 1,2 | 1,8 | 3,9 | −0,47 | −0,40 | −0,32 |
| Sans risque | 0,1 | 0,8 | 1,9 | −0,56 | −0,50 | −0,51 |
| Sans risque, 50 % | 3,5 | 5,7 | 7,3 | −0,27 | −0,05 | −0,02 |
| Proxy lissé sur 7 ans | 3,2 | 3,9 | 4,7 | −0,29 | −0,21 | −0,26 |
| Livret A | 3,5 | 5,5 | 7,7 | −0,26 | −0,07 | 0,03 |
| Figée | 7,0 | 10,1 | 13,0 | 0,04 | 0,34 | 0,50 |

Duration effective de l'actif : 6,4 (A), 5,7 (B), 6,6 (C). Observation de place (ACPR n° 181) : la hausse des taux longs réduit davantage la valeur des engagements que celle des actifs, donc la valeur des assureurs monte quand les taux montent.

### 4.7 Variantes complémentaires (référence sans risque)

| Variante | Valeur A | Valeur B | Valeur C | Rachat moyen 1-10, A | Rachat moyen 1-10, B | Rachat moyen 1-10, C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Lissé intégral | −18,3 ± 7,2 | 59,2 ± 6,2 | 84,0 ± 6,0 | 15,5 % | 12,1 % | 11,0 % |
| Décomposé | −24,5 ± 7,3 | 46,0 ± 6,7 | 68,7 ± 6,9 | 14,6 % | 11,2 % | 10,5 % |
| Décomposé, recouvrement 63 % | −22,4 ± 7,2 | 49,0 ± 6,5 | 72,8 ± 6,6 | 14,9 % | 11,4 % | 10,5 % |
| Saut intégral, bloc unique | −53,8 ± 8,0 | −12,7 ± 8,5 | 3,7 ± 9,0 | 12,8 % | 8,7 % | 8,3 % |
| Lissé, niveau initial 2,63 % | −10,1 ± 7,6 | 68,3 ± 6,4 | 92,3 ± 6,4 | 14,2 % | 10,9 % | 9,9 % |
| Décomposé, niveau initial 2,63 % | −16,5 ± 7,7 | 52,8 ± 7,2 | 74,8 ± 7,3 | 13,3 % | 10,1 % | 9,5 % |
| Lissé, rachat structurel 4,4 % | −16,3 ± 7,9 | 61,6 ± 6,7 | 86,6 ± 6,4 | 14,9 % | 11,4 % | 10,2 % |
| Décomposé, rachat structurel 4,4 % | −23,1 ± 7,9 | 47,7 ± 7,3 | 70,3 ± 7,4 | 13,8 % | 10,5 % | 9,8 % |
| Décomposé, base avec VA | −13,6 ± 7,0 | 55,1 ± 6,7 | 77,4 ± 6,8 | 14,1 % | 10,6 % | 9,8 % |

### 4.8 Trajectoires en probabilité réelle (plausibilité, aucune valeur)

Taux et spreads figés, référence des assurés constante (toutes les références coïncident sur ces trajectoires). Comparaison de place : rendement de l'actif 2,8 % en 2025 (la moitié des organismes entre 2,4 % et 3,3 %), taux servi 2,63 % (quartiles 2,3 % et 2,9 %), rachats 4,4 %. Lecture : les rendements comptables encadrent la place (A au niveau moyen, C au-dessus du troisième quartile, ce qui correspond à son récit) ; les taux servis restent sous la moyenne de place parce que la règle de taux servi des V1 à V4 vise la référence moins 0,5 point (2,38 %), paramètre de stratégie qui sera un levier de l'étape suivante.

| Profil | Pertes de crédit effectives | Rendement comptable 1-10 | Taux servi 1-10 | Rachat 1-10 | PM à 10 ans | Apports cumulés | Fonds propres min. 1-10 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Perte attendue réelle de 3 pb par an | 2,78 % | 2,29 % | 5,0 % | 679 | 0,0 | 52,3 |
| A | Perte attendue réelle de 10 pb par an | 2,71 % | 2,26 % | 5,0 % | 677 | 0,0 | 52,3 |
| A | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 1,96 % | 1,61 % | 7,9 % | 463 | 0,0 | 50,7 |
| A | Stress : tout le spread à 10 ans en pertes effectives | 0,80 % | 0,83 % | 14,2 % | 208 | 0,0 | 40,7 |
| B | Perte attendue réelle de 3 pb par an | 3,14 % | 2,38 % | 5,0 % | 685 | 0,0 | 58,6 |
| B | Perte attendue réelle de 10 pb par an | 3,08 % | 2,38 % | 5,0 % | 685 | 0,0 | 58,5 |
| B | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 2,82 % | 2,37 % | 5,0 % | 685 | 0,0 | 57,3 |
| B | Stress : tout le spread à 10 ans en pertes effectives | 2,11 % | 1,89 % | 6,3 % | 571 | 0,0 | 56,4 |
| C | Perte attendue réelle de 3 pb par an | 3,86 % | 2,50 % | 5,0 % | 693 | 0,0 | 70,2 |
| C | Perte attendue réelle de 10 pb par an | 3,80 % | 2,43 % | 5,0 % | 688 | 0,0 | 70,1 |
| C | Stress : 50 % du spread à 10 ans en pertes effectives (rapport d'intensités 2) | 3,29 % | 2,38 % | 5,0 % | 685 | 0,0 | 68,9 |
| C | Stress : tout le spread à 10 ans en pertes effectives | 2,99 % | 2,38 % | 5,0 % | 685 | 0,0 | 68,1 |

### 4.9 Vue prudentielle simplifiée (base avec VA)

Calcul pédagogique inspiré de la formule standard (`src/v5/solvabilite_v5.py`) : taux, actions, spread (part non souveraine, notation A), rachat ; absorption par les FDB ; marge de risque à 6 %. Hors calcul : risque opérationnel, absorption par les impôts différés, fonds excédentaires (borne haute indicative donnée à part).

| Profil | Référence | Crédit | Actif | BE | Marge de risque | Fonds propres | SCR | dont marché net | dont rachat net | Ratio | Ratio après impôts différés | Fonds excédentaires, borne haute |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Sans risque, 50 % | Décomposé | 899,8 | 901,3 | 18,0 | −19,5 | 87,1 | 67,3 | 37,0 | −22 % | −2 % | 18,5 |
| A | Sans risque | Décomposé | 899,8 | 913,4 | 13,8 | −27,5 | 85,7 | 70,4 | 31,3 | −32 % | −9 % | 18,5 |
| A | Sans risque | Lissé intégral | 899,8 | 907,0 | 14,6 | −21,8 | 93,4 | 74,1 | 35,1 | −23 % | −4 % | 18,5 |
| A | Proxy lissé sur 7 ans | Décomposé | 899,8 | 894,0 | 20,4 | −14,6 | 88,0 | 66,0 | 39,6 | −17 % | 2 % | 18,5 |
| B | Sans risque, 50 % | Décomposé | 992,8 | 917,8 | 23,4 | 51,5 | 86,1 | 71,0 | 34,1 | 60 % | 64 % | 29,7 |
| B | Sans risque | Décomposé | 992,8 | 937,7 | 14,7 | 40,4 | 75,9 | 64,9 | 26,2 | 53 % | 62 % | 29,7 |
| B | Sans risque | Lissé intégral | 992,8 | 923,3 | 17,1 | 52,4 | 84,3 | 70,3 | 32,1 | 62 % | 66 % | 29,7 |
| B | Proxy lissé sur 7 ans | Décomposé | 992,8 | 912,4 | 25,2 | 55,2 | 87,3 | 71,0 | 36,0 | 63 % | 66 % | 29,7 |
| C | Sans risque, 50 % | Décomposé | 1 028,8 | 929,4 | 20,4 | 79,0 | 85,4 | 74,2 | 27,5 | 93 % | 88 % | 14,8 |
| C | Sans risque | Décomposé | 1 028,8 | 951,4 | 10,7 | 66,8 | 73,4 | 66,8 | 17,8 | 91 % | 90 % | 14,8 |
| C | Sans risque | Lissé intégral | 1 028,8 | 935,3 | 14,4 | 79,2 | 81,7 | 71,8 | 24,8 | 97 % | 92 % | 14,8 |
| C | Proxy lissé sur 7 ans | Décomposé | 1 028,8 | 924,1 | 22,3 | 82,4 | 85,6 | 73,2 | 29,7 | 96 % | 91 % | 14,8 |

Lecture :

- **Écart massif avec la place.** Ratios approchés dans la convention centrale : −17 % (A), 63 % (B), 96 % (C), contre 239 % pour les organismes vie et mixtes au 30/06/2026. Même le profil C reste sous 100 %, et B, conçu pour être proche de la place sur la PPB, le taux technique et le taux servi, en est très loin en solvabilité.
- **Ce qui manque au calcul et jouerait en faveur des profils** : fonds excédentaires (jusqu'à 18,5 pour A, 29,7 pour B, 14,8 pour C), absorption par les impôts différés, ajustement symétrique du choc actions. Ce qui est peut-être trop sévère : un choc de spread en notation A sur 66 % des obligations (40,1 pour A, 39,3 pour B, 40,2 pour C de perte nette), et la règle de taux servi des V1 à V4, qui fait renoncer l'assureur à sa marge pour suivre la référence, ce qui réduit l'absorption par les FDB.
- **Ce qui vient des profils** : à l'ouverture, l'actif en valeur de marché est inférieur à la PM et à la PPB pour A et B ; leurs moins-values obligataires (-19 % et -13 % de la VNC) et leurs fonds propres comptables (4,5 % à 6 % de la PM) sont des paramètres fictifs que la donnée de place 2026 (ACPR n° 185, non lue) permettrait de confronter.
- **Choc de taux** : dans toutes les conventions calculées, c'est la hausse des taux qui coûte (perte nette de 12,7 pour A, 9,3 pour B, 13,7 pour C au centre), alors que la place gagne quand les taux montent. Le même écart apparaît dans les durations de la section 4.6.
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
| TVOG positive | 52 / 54 | presque toujours ; exceptions : B, figée, lissé intégral (−7,1) ; C, figée, lissé intégral (−8,1). L'équivalent certain n'est pas la trajectoire moyenne d'un modèle non linéaire : sans rachat lié aux taux, la dispersion des taux peut jouer en faveur de l'actionnaire |
| Signe de la valeur du profil A | 4 positives / 25 | **fragile : change de signe** (de −53,8 à 18,2) |
| Signe de la valeur du profil B | 24 positives / 25 | **fragile : change de signe** (de −12,7 à 101,3) |
| Signe de la valeur du profil C | 25 positives / 25 | toujours positive (de 3,7 à 126,2) |
| Classement des références par valeur | 1 classement(s) différent(s) sur 9 | identique pour tous les profils et crédits |
| Signe de la sensibilité de la valeur aux taux | OAT - 2 pts -, Sans risque -, Sans risque, 50 % -, Proxy lissé sur 7 ans -, Livret A ±, Figée + | **fragile : change de signe avec la référence** |

Classement des références, de la valeur la plus basse à la plus haute (convention décomposée) : A : OAT - 2 pts < Sans risque < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée ; B : OAT - 2 pts < Sans risque < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée ; C : OAT - 2 pts < Sans risque < Livret A < Sans risque, 50 % < Proxy lissé sur 7 ans < Figée.

## 6. Profil A : assureur en difficulté ou conséquence des hypothèses ?

Trois lectures, à ne pas confondre :

1. **Comptable** : le profil A est solvable. Ses fonds propres comptables (45) et sa réserve de capitalisation (5) sont positifs, et aucune perte n'est constatée à l'ouverture.
2. **Valeur de marché à l'ouverture** : l'actif en valeur de marché ne couvre pas la PM et la PPB. L'écart vaut −125,2 pour A (−47,2 pour B, 8,8 pour C). Comme un assuré qui rachète reçoit sa PM sans supporter les moins-values, A ne tient que si ses assurés restent : c'est la définition d'un assureur exposé au rachat massif.
3. **Valeur économique simplifiée** (actif - BE, sans VA, avant impôt et marge de risque) : de −53,8 à 18,2 selon les conventions. Elle est négative dans 21 combinaisons sur 25, et vaut −5,9 ± 5,9 dans la convention centrale proposée. Elle n'est positive qu'avec une référence figée (aucun rachat lié aux taux) ou avec un spread entièrement lissé et une référence lissée, et reste alors au plus de 18,2, soit moins de la moitié des fonds propres comptables.

**Apports de capital (risque neutre, convention centrale)** : un apport dans 50 % des scénarios ; valeur actuelle moyenne 23,6, médiane 0,9, q95 98,5, q99 175,2.
Les apports sont tardifs : aucun avant 5 ans, 7 % des scénarios en ont un avant 10 ans, première année médiane 16. Ils viennent surtout de deux sources. Dans les 20 % de scénarios où le bloc souverain fait défaut avant 10 ans (probabilité risque neutre), 93 % demandent un apport (moyenne 63,4), contre 40 % sans défaut (moyenne 13,8). Côté taux, 65 % des scénarios du tiers des taux 10 ans les plus hauts en année 5 demandent un apport, contre 42 % dans le tiers le plus bas : cela s'explique par la référence des assurés, qui suit les taux, et par les ventes d'obligations en moins-value pour payer les rachats.

**Probabilité réelle** : sur la trajectoire centrale (taux et spreads figés, perte attendue de 3 pb), A sert 2,29 % en moyenne sur 10 ans, au niveau du premier quartile de place (2,3 %). Ses rachats restent à 5,0 % et il n'a besoin d'aucun apport (fonds propres minimaux de 52,3). Même si tout le spread devenait une perte effective, il servirait 0,83 %, ses rachats monteraient à 14,2 % par an et sa PM tomberait à 208 en 10 ans, mais il garderait des fonds propres de 40,7 au minimum, sans apport sur cette trajectoire.

**Vue prudentielle simplifiée** (base avec VA, marge de risque, SCR approché) : fonds propres de −14,6, SCR de 88,0, ratio approché de −17 % (fonds excédentaires non comptés, borne haute indicative de 18,5). Le ratio de place est de 239 % pour les organismes vie et mixtes au 30/06/2026.

**Conclusion.** Le profil A n'est pas un assureur normalement viable, et il ne faut pas le présenter ainsi. Comptablement solvable et sans besoin de capital sur une trajectoire réelle centrale, il n'a plus de coussin économique : sa valeur est proche de zéro ou négative, et il demande des apports dans une large part des scénarios risque neutre, dans les scénarios de hausse des taux et de défaut souverain. Une partie de ce résultat est construite : ses moins-values obligataires (-19 % de la VNC) sont volontairement en haut de fourchette, et la donnée de place 2026 manque (ACPR n° 185 non lue). Une autre partie vient du modèle : en risque neutre, les produits comptables sont nets de tout le coût du spread, si bien que le taux servi et les rachats risque neutre ne sont pas des prévisions. Proposition : garder A comme profil de stress, qualifié d'**assureur fragile, au seuil de la recapitalisation**, et analyser ses stratégies sous contrainte de capital (apports, plan de redressement) plutôt que comme celles d'un assureur en régime normal.

## 7. Convention centrale proposée et stress à conserver

**Convention centrale proposée (à valider)**

| Élément | Choix | Justification |
| --- | --- | --- |
| Valorisation | Base sans VA ; VA en vue réglementaire seulement | Valeur économique sans effet réglementaire ; effet VA présenté à part (+10,8 pour A, +9,0 pour B, +8,7 pour C) |
| Forme des pertes de crédit | Décomposée : 80 % du spread en défaut par saut (recouvrement 40 %, bloc souverain de 26 %), 20 % en coût hors défaut lissé | Prix inchangés et absence d'arbitrage vérifiée ; forme cohérente avec un risque souverain concentré et peu probable, et avec un crédit d'entreprise diversifié ; part de crédit appuyée sur le CDS France |
| Probabilité réelle | Perte attendue de 3 pb par an ; le reste du spread est une prime | Défauts historiques par notation et composition du portefeuille de place ; la prime n'est jamais comptée comme de la valeur |
| Référence des assurés | Proxy comportemental fictif (et non taux servi observé) : taux sans risque 10 ans lissé (1/7 par an), niveau initial 2,88 % (hypothèse) | Cohérente en risque neutre (un concurrent investi dans les mêmes titres gagne le taux sans risque et renouvelle progressivement son portefeuille). Les taux servis observés bougent lentement (2,63 % en 2024 et en 2025 alors que l'OAT 10 ans moyenne passe de 3,0 % à 3,4 %). Sensibilité aux taux intermédiaire : duration du BE de 3,2 à 4,7 ans, contre 0,1 à 1,9 avec une transmission immédiate |
| Rachat structurel | À trancher : 5 % (V1 à V4) ou 4,4 % (taux observé de 2025, identique pour les trois profils) | Effet sur la valeur stochastique dans l'erreur de Monte-Carlo (+1,4 pour A, +1,7 pour B, +1,6 pour C) ; aucun calage propre au profil A |

Valeurs dans cette convention : A −5,9 ± 5,9 (TVOG 23,4, apports dans 50 % des scénarios), B 68,5 ± 5,4 (TVOG 26,7, apports dans 12 % des scénarios), C 94,2 ± 5,1 (TVOG 26,0, apports dans 8 % des scénarios).

**Avant les métriques de rentabilité**, deux écarts avec la place restent à traiter. D'abord la solvabilité : les ratios approchés (section 4.9) sont très inférieurs aux 239 % de la place. Il faudra compléter la vue prudentielle (fonds excédentaires, impôts différés, ajustement symétrique) et confronter les fonds propres et les moins-values des profils à l'ACPR n° 185 dès que le document sera disponible.

Ensuite la sensibilité aux taux. Même la référence lissée donne une valeur qui baisse quand les taux montent (−0,29 par pb pour A, −0,21 par pb pour B, −0,26 par pb pour C), alors que la place observe l'inverse (ACPR n° 181). L'écart peut venir de la loi de rachat (paramètres des V1 à V4, non recalés), de la règle de taux servi (cible égale à la référence moins 0,5 point) ou de l'absence de fonds excédentaires et d'impôts différés. Il faudra le traiter avant d'optimiser les stratégies d'adossement.

**Stress à conserver pour la suite de la V5**

| Stress | Paramétrage | Ce qu'il teste |
| --- | --- | --- |
| Transmission immédiate des taux longs | Référence sans risque, beta = 1 | Rachats dynamiques en hausse des taux (valeur de A : −24,5 contre −5,9 au centre) |
| Référence figée | Pas de rachat lié aux taux | Borne opposée ; isole le risque de garantie et de taux servi |
| Livret A | Référence pilotée par le taux court | Concurrence de l'épargne réglementée (valeur de A : −17,2) |
| Spread intégralement lissé | Convention initiale | Transfert maximal des pertes de crédit aux assurés par le taux servi |
| Spread intégralement par saut, bloc unique | Tout le portefeuille fait défaut d'un coup | Concentration extrême (valeur de B : −12,7 ± 8,5) ; erreur de Monte-Carlo élevée, à recalculer avec plus de scénarios |
| Recouvrement 63 % | Décote souveraine moyenne de 37 % | Sensibilité au recouvrement (effet modéré) |
| Pertes effectives de 50 % du spread | Probabilité réelle, 10 ans | Assureur qui subit vraiment une partie du risque souverain : taux servi, rachats, fonds propres |
| Défaut souverain déterministe | Défaut du bloc de 26 % en année 2, recouvrement 40 % (perte de 15,6 % des obligations) | Événement unique, lisible, pour comparer les stratégies (à construire) |
| Niveau initial de la référence à 2,63 % | Dernier taux servi moyen observé | Le niveau de 2,88 % est une hypothèse |
| Chocs de la formule standard | Taux, actions, spread, rachat massif (vue prudentielle) | Capital et absorption par les FDB |

## 8. Limites restantes

- **Monte-Carlo.** Le défaut par saut augmente la variance : la demi-largeur de l'intervalle de la fuite atteint 5,7 avec 1 000 scénarios, et de 12,1 à 17,3 pour le bloc unique. Les fuites sont positives dans 73 variantes sur 75 (mêmes tirages de taux et de défaut partout), toujours à l'intérieur de leur intervalle de confiance à 95 % (au plus 0,86 fois sa demi-largeur). Les écarts de valeur entre spread lissé et spread par saut (de 6,9 à 23,5) dépassent cette erreur ; le bloc unique demande plus de scénarios.
- **Rachats risque neutre et rachats observés.** Les rachats moyens risque neutre (de 6 % à 19 % par an sur 10 ans selon le profil et les conventions) dépassent le taux observé de 4,4 %. Ce n'est pas une contradiction : en risque neutre, les produits comptables sont nets du coût du spread. Mais la loi de rachat dynamique (paramètres des V1 à V4) n'est calée sur aucune donnée de place, et les quartiles de rachat par organisme (ACPR n° 179) n'ont pas pu être lus.
- **Part de crédit du spread (kappa = 0,8).** C'est une hypothèse : le CDS France est coté en dollars (prime de dévaluation non mesurée), sa structure par terme au-delà de 5 ans n'est pas disponible, et les dates diffèrent (CDS du 29/10, TEC du 04/11).
- **Défaut par saut simplifié.** Recouvrement de 40 % (convention de cotation non vérifiée en ligne), blocs indépendants, réinvestissement immédiat dans le même portefeuille (défauts répétés possibles), ni migration de notation ni spread stochastique : la courbe de spread reste celle du 04/11/2026, sans dynamique propre.
- **Un seul spread pour toutes les obligations.** Souverains, financières et entreprises partagent le spread OAT.
- **Probabilité réelle.** Taux et spreads figés, prime actions fictive de 3 % : ces trajectoires servent à la plausibilité, pas à la prévision.
- **Vue prudentielle.** Choc de taux appliqué à la courbe avec VA, ajustement symétrique nul, spread en notation A sur 66 % des obligations, pas de risque opérationnel, pas d'absorption par les impôts différés ni de fonds excédentaires : c'est un ordre de grandeur, pas un ratio de solvabilité.
- **Données de place manquantes.** ACPR n° 185 (moins-values latentes au 30/06/2026) et quartiles de rachat de l'ACPR n° 179 : les paramètres correspondants des profils restent fictifs.
- **Avant impôt.** L'impôt est codé et testé mais pas appliqué.

