# V5 : synthèse avant l'optimisation des stratégies ALM

Généré par `scripts/v5_rapport_synthese.py` depuis `resultats/v5_synthese.json` (`scripts/v5_synthese.py`) et `resultats/v5_calibration_credit.json` (`scripts/v5_calibration_credit.py`). Unités fictives : 1 unité = 10 M€, PM initiale de 1 000. 1 000 scénarios, valorisation risque neutre au 31/10/2026, base sans VA sauf mention, valeurs avant impôt sauf dans la vue prudentielle. **Les trois profils sont fictifs** et ne sont pas ajustés pour être rentables ou solvables. Aucune stratégie n'est optimisée ici.

Le PDF de l'ACPR n° 185 n'a pas pu être consulté : ses chiffres ne sont utilisés que lorsqu'ils sont repris par une source secondaire, et signalés comme tels.

## 1. Conventions centrales retenues pour la suite (provisoires)

| Élément | Convention | Statut | Fragilité |
| --- | --- | --- | --- |
| Valorisation | Base sans VA ; la VA est une vue réglementaire | Choix de méthode | Faible |
| Spread des obligations | Moyenne de long terme des spreads publiée par l'EIOPA, notation A (81 pb à 2 ans, 126 pb à 10 ans, 128 pb à 30 ans) | Hypothèse | **Forte** : pas un spread de marché observé au 31/10/2026 |
| Part de crédit du spread | kappa = 0,70 | Hypothèse | **Forte** : non recoupée avec des cotations de marché |
| Forme des pertes risque neutre | 70 % par saut (recouvrement 40 %), 30 % hors défaut lissé | Hypothèse | Moyenne |
| Structure de défaut | 50 blocs, copule gaussienne à un facteur, rho = 0,2 ; bloc souverain de 26 % et bloc unique en stress | Hypothèse | **Forte** : la France est un émetteur unique pour 26 % des obligations |
| Probabilité réelle | Probabilité de défaut de 0,061 % par an et par bloc, recouvrement 50 % | Calibré (défauts d'entreprises par notation) | Moyenne : moyennes historiques |
| Référence des assurés | **Proxy comportemental fictif** : taux sans risque 10 ans lissé sur 7 ans, niveau initial 2,85 % | Hypothèse | **Forte** ; confrontée à une référence composite |
| Rachat structurel | 4,4 % au sens de l'ACPR (paramètre du modèle 4,331 %) ; 5 % en sensibilité | Observé, converti | Moyenne : dénominateur ACPR imprécis, année de rachats bas |
| Loi de rachat dynamique | Paramètres des V1 à V4, entre les corridors minimal et maximal de l'ONC 2013 | Hypothèse | Forte : non calée sur des données |

## 2. Traitement du risque de crédit

### 2.1 Spread des obligations

Le spread des obligations détenues est une hypothèse, construite sans donnée d'indice de taux souverain : la moyenne de long terme des spreads (LTAS) que l'EIOPA publie avec la courbe sans risque, pour la notation la plus représentée du portefeuille obligataire des assureurs (A), moyenne des séries financières et non financières, convertie en spread continu au-dessus de la courbe EIOPA sans VA (`data/v5/marche/spread_hypothetique_20261031.json`). C'est un spread « normal », hors période de tension, et non un spread de marché observé au 31/10/2026.

| Maturité | Taux EIOPA sans VA | Spread hypothétique | Taux des obligations du modèle |
| ---: | ---: | ---: | ---: |
| 1 an | 3,14 % | 81 pb | 3,97 % |
| 2 ans | 3,27 % | 81 pb | 4,11 % |
| 5 ans | 3,29 % | 105 pb | 4,38 % |
| 10 ans | 3,35 % | 126 pb | 4,66 % |
| 20 ans | 3,35 % | 128 pb | 4,68 % |
| 30 ans | 3,30 % | 128 pb | 4,63 % |

### 2.2 Des spreads aux intensités de défaut

Règles, pour une année t (de t - 1 à t) :

- spread cumulé : H(t) = s(t) x t, avec s le spread zéro-coupon continu ;
- coût risque neutre de l'année : dH(t) = H(t) - H(t - 1), soit le spread à terme d'un an ; il est partagé entre crédit (kappa x dH) et hors défaut ((1 - kappa) x dH) ;
- probabilité risque neutre de défaut d'un bloc : p(t) = (1 - exp(-kappa x dH(t))) / (1 - R), si bien que 1 - p(t) x (1 - R) = exp(-kappa x dH(t)) : la perte moyenne reproduit exactement le prix de marché ;
- facteur de nominal moyen de l'année : exp(-(1 - kappa) x dH(t)) x (1 - p(t) x (1 - R)) = exp(-dH(t)).

Convention centrale (kappa = 0,7, R = 40 %) :

| Année | Spread cumulé H | Coût de l'année dH | dont crédit | dont hors défaut | Probabilité de défaut de l'année | Probabilité cumulée |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 81 pb | 81 pb | 56 pb | 24 pb | 0,94 % | 0,9 % |
| 2 | 161 pb | 80 pb | 56 pb | 24 pb | 0,94 % | 1,9 % |
| 3 | 260 pb | 99 pb | 69 pb | 30 pb | 1,15 % | 3,0 % |
| 5 | 527 pb | 149 pb | 104 pb | 45 pb | 1,72 % | 6,0 % |
| 7 | 831 pb | 152 pb | 106 pb | 45 pb | 1,76 % | 9,3 % |
| 10 | 1 258 pb | 149 pb | 104 pb | 45 pb | 1,72 % | 13,7 % |
| 15 | 1 914 pb | 128 pb | 89 pb | 38 pb | 1,48 % | 20,1 % |
| 20 | 2 553 pb | 128 pb | 90 pb | 38 pb | 1,49 % | 25,8 % |
| 30 | 3 832 pb | 128 pb | 89 pb | 38 pb | 1,48 % | 36,1 % |

Le coût de l'année suit le spread à terme : il dépasse le spread comptant tant que le spread zéro-coupon monte avec la maturité, puis le rejoint quand la courbe de spread devient plate. C'est ce coût à terme, et non le spread affiché, que la valorisation risque neutre fait payer chaque année.

### 2.3 Part de crédit kappa

- **Hypothèse** : Part du spread traitée comme perte de défaut en risque neutre (le reste est une perte lissée, hors défaut). Hypothèse : 0,7 au centre ; bornes 0,55 et 1 testées en sensibilité. Elle n'est plus recoupée avec des cotations de marché : le spread des obligations est lui-même une hypothèse. Ce n'est pas une estimation du risque de défaut des émetteurs, souverains ou entreprises : kappa répartit seulement le spread hypothétique entre une perte par défaut et une perte hors défaut.
- **Maturité** : kappa est supposé constant sur toutes les maturités.

### 2.4 Liquidité et prime de risque

- **Composante hors défaut (30 % du spread)** : elle regroupe la liquidité relative et l'offre de titres. En valorisation, elle reste un coût risque neutre (absence d'arbitrage) ; en probabilité réelle, c'est une prime.
- **Prime de risque de crédit** : c'est l'écart entre la perte risque neutre et la perte réelle. Les probabilités de « 1,7 % » et « 0,06 % » ne mesurent pas la même chose. La première (1,72 %) est la probabilité d'un bloc **l'année 10**, tirée du spread **à terme**. Sa moyenne sur 10 ans vaut 1,46 % par an. La seconde (0,061 %) est un taux de défaut historique moyen d'entreprises notées comme le portefeuille de place (S&P, 1981-2024), et non une mesure propre à un émetteur. Sur une base comparable (moyennes annuelles sur 10 ans), le rapport vaut environ 24, contre un rapport publié de 2 pour les souverains de la zone euro. Le spread retenu rémunère donc surtout autre chose qu'une perte attendue historique (prime de risque, composante hors défaut), à moins que la probabilité réelle historique sous-estime le risque. Le stress « rapport de 2 » en probabilité réelle couvre cette seconde lecture.

### 2.5 Intensité, recouvrement et blocs

L'intensité ne dépend pas de la taille des blocs : chaque bloc a la même probabilité p(t). La perte moyenne de l'année est donc identique quelle que soit la structure. Seule la concentration change :

| Structure | Blocs | Plus gros bloc | Perte si ce bloc fait défaut (R = 40 %) | Probabilité risque neutre de défaut de ce bloc sur 10 ans | Probabilité réelle |
| --- | ---: | ---: | ---: | ---: | ---: |
| Souverain 26 % + 20 blocs | 21 | 26 % | 15,6 % des obligations | 13,7 % | 0,61 % |
| 50 blocs égaux | 50 | 2 % | 1,2 % des obligations | 13,7 % | 0,61 % |
| Souverain 26 % + 50 blocs | 51 | 26 % | 15,6 % des obligations | 13,7 % | 0,61 % |
| Bloc unique | 1 | 100 % | 60,0 % des obligations | 13,7 % | 0,61 % |

La copule gaussienne (rho = 0,2) garde la probabilité de chaque bloc mais regroupe les défauts dans les mêmes années. Le recouvrement joue en sens inverse de l'intensité : un recouvrement de 63 % au lieu de 40 % donne des défauts plus fréquents mais moins coûteux, pour la même perte moyenne.

### 2.6 Valeur selon la structure de défaut et la part de crédit

| Convention | Valeur A | Valeur B | Valeur C | Apports A | Apports B | Apports C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Spread entièrement lissé | 15,9 ± 6,4 | 88,7 ± 6,1 | 116,1 ± 5,4 | 30 % | 2 % | 1 % |
| 50 blocs indépendants | 12,4 ± 7,1 | 85,2 ± 6,1 | 113,6 ± 5,6 | 35 % | 3 % | 2 % |
| **50 blocs corrélés (centre)** | 9,0 ± 7,1 | 77,9 ± 6,0 | 106,1 ± 5,7 | 37 % | 5 % | 2 % |
| Souverain 26 % + 50 blocs corrélés | 7,7 ± 7,1 | 72,5 ± 6,1 | 98,1 ± 5,8 | 36 % | 10 % | 7 % |
| Souverain 26 % + 20 blocs (corrélé par bloc) | 8,1 ± 6,5 | 75,1 ± 5,8 | 101,4 ± 6,1 | 39 % | 10 % | 7 % |
| Bloc unique | −7,6 ± 7,4 | 42,4 ± 6,3 | 62,9 ± 6,6 | 41 % | 35 % | 33 % |
| kappa = 0,55 | 10,9 ± 7,0 | 80,7 ± 6,0 | 108,8 ± 5,7 | 35 % | 4 % | 2 % |
| kappa = 1 | 5,3 ± 7,1 | 72,2 ± 6,0 | 99,8 ± 5,8 | 41 % | 7 % | 3 % |
| Recouvrement 63 % | 10,4 ± 6,8 | 80,6 ± 5,8 | 108,6 ± 5,6 | 35 % | 4 % | 2 % |

### 2.7 D'où vient la baisse de valeur avec le défaut par saut

Test d'attribution, mêmes tirages, spread lissé contre spread par saut (bloc souverain de 26 %), référence centrale :

| Profil | Passif | Valeur, spread lissé | Valeur, saut | Écart | BE garanti, lissé | BE garanti, saut | FDB, lissé | FDB, saut |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Indépendant des actifs (taux servi = TMG, sans participation ni rachat dynamique) | 195,6 | 195,6 | 0,0 | 663,4 | 663,4 | 0,0 | 0,0 |
| A | Participation et TMG, sans rachat dynamique | 66,9 | 46,3 | −20,6 | 663,4 | 663,4 | 121,3 | 140,7 |
| A | Modèle complet | 15,9 | 8,1 | −7,7 | 807,6 | 787,3 | 50,3 | 74,3 |
| B | Indépendant des actifs (taux servi = TMG, sans participation ni rachat dynamique) | 309,6 | 309,6 | 0,0 | 640,3 | 640,3 | 0,0 | 0,0 |
| B | Participation et TMG, sans rachat dynamique | 106,5 | 92,6 | −13,9 | 640,3 | 640,3 | 191,2 | 204,3 |
| B | Modèle complet | 88,7 | 75,1 | −13,6 | 700,4 | 700,1 | 157,7 | 171,5 |

Quand le passif ne dépend pas des actifs, la forme des pertes ne change rien à la valeur (écart de 0,00 pour B, BE identiques scénario par scénario ; test `test_passif_independant_des_actifs_meme_be_quelle_que_soit_la_forme_des_pertes`). La comptabilisation des défauts ne crée donc ni ne détruit de valeur, ce que confirment aussi les fuites nulles. La baisse apparaît dès que la participation et le TMG entrent en jeu (−20,6 pour A, −13,9 pour B) ; dans le modèle complet, les rachats dynamiques la réduisent (−7,7 pour A, −13,6 pour B), parce qu'ils rendent déjà le passif très non linéaire en spread lissé. Le mécanisme est une asymétrie : les années sans défaut, l'excédent de produits est partagé à 85 % avec les assurés ; les années de défaut, la perte sous le TMG et la marge abandonnée restent à l'actionnaire. Concentrer les pertes transfère donc de la valeur de l'actionnaire vers les assurés.

## 3. Rachats et comportement des assurés

### 3.1 Taux structurel de 4,4 % et cohérence avec l'ACPR n° 179

- **Définition ACPR** : rachats de l'année rapportés aux provisions de N-1, supports en euros rachetables, décès et arbitrages exclus (graphique 7 et notes). Le n° 179 ne précise ni la nature des provisions (PM ou provisions techniques), ni le périmètre exact des contrats non rachetables.
- **Définition du modèle** : le taux s'applique aux PM revalorisées nettes des décès. Rachats / PM d'ouverture = taux x (1 + taux servi) x (1 - taux de décès). D'où le paramètre 4,331 % = 4,4 % / (1,0263 x 0,99), avec le taux servi moyen de 2025.
- **Vérification** : rachats de l'année 1 rapportés à la PM d'ouverture, équivalent certain : 4,39 % (A), 4,39 % (B), 4,39 % (C) (le léger écart vient du taux servi de l'année 1 des profils, différent de 2,63 %).
- **Pas de double comptage** : Le taux observé de 2025 est un taux total. Il est pris comme structurel parce que, pour l'assureur moyen, l'écart entre taux servi et référence est resté dans la zone neutre de la loi dynamique ([-1 point, +1 point] dans les paramètres centraux) : la composante dynamique de 2025 est nulle. Ce n'est plus vrai avec le corridor maximal de l'ONC (zone neutre commençant à 0) : dans cette sensibilité, une partie du taux observé serait comptée deux fois. Dans les trois profils, la composante dynamique de l'année 1 est nulle : taux de rachat de l'année 1 = 4,331 % (A), 4,331 % (B), 4,331 % (C).
- **Réserve** : 2025 est une année de rachats bas (4,8 % en 2024). Le taux de 5 % reste en sensibilité.

### 3.2 Probabilité réelle et risque neutre

| | Valorisation (risque neutre) | Projection de plausibilité (probabilité réelle) |
| --- | --- | --- |
| Loi de comportement | Même loi (rachat structurel et dynamique) : c'est une hypothèse de comportement réel, appliquée telle quelle | Même loi |
| Ce qui change | Les trajectoires de taux servi et de référence sont risque neutre : produits nets de tout le coût du spread, actions au taux sans risque | Produits nets de la seule perte réelle, prime actions, taux sans prime de terme |
| Référence des assurés | Moteur risque neutre (taux sans risque) : un concurrent investi dans les mêmes titres gagne le taux sans risque en risque neutre | Même moteur, trajectoires réelles |
| Prix du risque de comportement | Absent du BE ; il figure dans la marge de risque et le SCR de rachat | Sans objet |
| Lecture des rachats | Pas une prévision | Ordre de grandeur à confronter aux 4,4 % observés |

### 3.3 Référence des assurés : proxy fictif et référence composite

Référence composite (niveaux observés pour les fonds euros et le livret A, hypothétique pour les obligations ; délais et coefficients paramétrés, **poids fictifs**) : Fonds euros concurrents (60 % ; niveau 2,63 % ; transmission lissée sur 7 ans ; coefficient de réaction 1,0) ; Livret A (25 % ; niveau 1,70 % ; transmission immédiate ; coefficient de réaction 0,5) ; Placements obligataires directs (obligations à 10 ans du modèle) (15 % ; niveau 4,66 % ; transmission immédiate ; coefficient de réaction 1,0). Niveau initial : 2,702 %, sans calage sur 2,85 %.

| Référence ou loi | Valeur A | Valeur B | Valeur C | Rachat 1-10 A | Rachat 1-10 B | Rachat 1-10 C | Duration BE A | Duration BE B | Duration BE C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Proxy lissé sur 3 ans | −0,5 ± 7,6 | 66,8 ± 6,7 | 93,8 ± 6,6 | 12,5 % | 8,3 % | 7,3 % | 1,7 | 3,0 | 5,7 |
| Proxy lissé sur 5 ans | 5,3 ± 7,4 | 73,9 ± 6,4 | 101,7 ± 6,1 | 11,8 % | 7,4 % | 6,6 % | 2,6 | 4,1 | 6,7 |
| **Proxy lissé sur 7 ans (centre)** | 9,0 ± 7,1 | 77,9 ± 6,0 | 106,1 ± 5,7 | 11,2 % | 7,0 % | 6,3 % | 3,2 | 4,8 | 7,3 |
| Proxy lissé sur 10 ans | 12,6 ± 6,4 | 81,2 ± 5,4 | 109,6 ± 5,1 | 10,7 % | 6,7 % | 6,0 % | 3,9 | 5,6 | 7,5 |
| Composite | 9,4 ± 6,7 | 78,9 ± 5,7 | 105,8 ± 5,7 | 10,9 % | 7,0 % | 6,3 % | 2,6 | 6,0 | 5,6 |
| Transmission immédiate (sans risque 10 ans) | −12,6 ± 8,0 | 50,9 ± 7,1 | 76,6 ± 7,2 | 14,0 % | 10,3 % | 9,3 % | 0,9 | 1,4 | 6,0 |
| Référence figée | 28,7 ± 2,1 | 93,0 ± 2,6 | 120,1 ± 3,1 | 9,6 % | 6,2 % | 5,5 % | 7,0 | 12,0 | 12,5 |
| Réaction faible (corridor minimal ONC) | 42,8 ± 7,4 | 93,7 ± 6,2 | 117,3 ± 5,7 | 5,0 % | 4,7 % | 4,6 % | 6,6 | 6,7 | 7,3 |
| Réaction forte (corridor maximal ONC) | −21,8 ± 3,3 | 47,4 ± 4,0 | 77,9 ± 4,4 | 21,8 % | 14,5 % | 12,9 % | 3,0 | 4,3 | 4,4 |
| Rachat structurel 5 % | 5,3 ± 6,3 | 73,1 ± 5,3 | 100,8 ± 5,1 | 12,2 % | 7,8 % | 7,1 % | 3,3 | 4,7 | 6,8 |

## 4. Synthèse par profil

### Profil A : Assureur historique sous pression

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | 9,0 ± 7,1 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de −21,8 à 42,8 |
| | Équivalent certain | 32,0 |
| BE et TVOG | BE stochastique | 899,4 |
| | TVOG (BE stochastique - équivalent certain) | 23,0 |
| | FDB | 67,9 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 11,2 % / 5,6 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 36 % / 35 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 171,4 / 91,6 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 37 % ; 13,4 ; 102,5 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,2 % ; 1,3 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 0,9 % / 5,0 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 114,9 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | 10,8 (12,3) |
| | SCR approché / MCR approché, base avec VA | 118,0 / 29,5 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **9 %** ; 20 % ; −1 % |
| | Indicateur de couverture simplifié du MCR | 37 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −50,5 |
| | Défaut : bloc souverain de 26 % / bloc unique | −0,9 / −16,6 |
| | Part de crédit 0,55 / 1 | 1,9 / −3,7 |
| | Référence : lissage 3 ans / 10 ans / composite / immédiate | −9,5 / 3,6 / 0,4 / −21,6 |
| | Réaction faible / forte (ONC) | 33,8 / −30,8 |
| | Rachat structurel 5 % ; base avec VA | −3,7 ; 11,7 |

### Profil B : Assureur intermédiaire

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | 77,9 ± 6,0 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de 42,4 à 93,7 |
| | Équivalent certain | 106,0 |
| BE et TVOG | BE stochastique | 919,7 |
| | TVOG (BE stochastique - équivalent certain) | 28,1 |
| | FDB | 164,5 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 7,0 % / 4,3 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 36 % / 14 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 75,5 / 6,1 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 5 % ; 2,7 ; 49,4 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,0 % ; 0,1 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 0,0 % / 0,4 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 92,9 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | 66,4 (14,9) |
| | SCR approché / MCR approché, base avec VA | 96,6 / 24,1 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **69 %** ; 72 % ; 53 % |
| | Indicateur de couverture simplifié du MCR | 275 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −46,9 |
| | Défaut : bloc souverain de 26 % / bloc unique | −2,8 / −35,5 |
| | Part de crédit 0,55 / 1 | 2,8 / −5,7 |
| | Référence : lissage 3 ans / 10 ans / composite / immédiate | −11,1 / 3,3 / 1,0 / −27,0 |
| | Réaction faible / forte (ONC) | 15,7 / −30,5 |
| | Rachat structurel 5 % ; base avec VA | −4,9 ; 11,6 |

### Profil C : Assureur plus récemment investi

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | 106,1 ± 5,7 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de 62,9 à 120,1 |
| | Équivalent certain | 130,2 |
| BE et TVOG | BE stochastique | 934,6 |
| | TVOG (BE stochastique - équivalent certain) | 24,1 |
| | FDB | 215,7 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 6,3 % / 4,2 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 36 % / 11 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 92,6 / 10,9 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 2 % ; 1,7 ; 27,5 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,0 % ; 0,1 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 0,0 % / 0,2 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 88,8 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | 86,3 (7,4) |
| | SCR approché / MCR approché, base avec VA | 89,3 / 22,3 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **97 %** ; 97 % ; 88 % |
| | Indicateur de couverture simplifié du MCR | 387 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −52,0 |
| | Défaut : bloc souverain de 26 % / bloc unique | −4,7 / −43,1 |
| | Part de crédit 0,55 / 1 | 2,7 / −6,3 |
| | Référence : lissage 3 ans / 10 ans / composite / immédiate | −12,3 / 3,6 / −0,3 / −29,4 |
| | Réaction faible / forte (ONC) | 11,2 / −28,2 |
| | Rachat structurel 5 % ; base avec VA | −5,3 ; 10,5 |

## 5. Vue prudentielle complétée

Fonds propres éligibles de niveau 1 = actif - BE - marge de risque + fonds excédentaires - impôts différés passifs. Les impôts différés actifs (niveau 3, plafonnés à 15 % du SCR) ne sont pas reconnus au centre, faute de démonstration de recouvrabilité (l'ACPR exige un horizon de profits futurs inférieur à 5 ans, justifié au-delà). Fonds excédentaires : approche simplifiée de l'ACPR, la PPB admissible entre en PM au bout de huit ans puis sort au rythme des prestations projetées. La PPB admissible est prise égale à la PPB comptable : les profils n'ont ni montants préaffectés ni dotations de plus de sept ans à redistribuer (paramètre fictif). SCR : taux, actions (39 %, ajustement symétrique nul), spread (part non souveraine de 66 %, ventilée par qualité de crédit selon la place), rachat (hausse, baisse, massif), mortalité (+15 %), frais (+10 %, sans inflation), opérationnel (0,45 % des provisions, plafonné à 30 % du BSCR) ; absorption par les FDB (hors fonds excédentaires) et par les impôts différés passifs. MCR : formule linéaire vie réduite aux contrats avec participation (3,7 % des prestations garanties - 5,2 % des FDB), entre 25 % et 45 % du SCR.

| Profil | Base | Actif | BE | Marge de risque | Fonds excédentaires | Impôts différés passifs | Fonds propres niveau 1 | SCR | dont marché net | dont vie nette | Ajustement FDB | Ajustement impôts | Opérationnel | MCR | Indicateur SCR | Indicateur MCR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | sans VA | 908,4 | 899,4 | 18,7 | 13,0 | 0,0 | 3,4 | 114,9 | 70,3 | 39,8 | −54,9 | 0,0 | 4,0 | 28,7 | 3 % | 12 % |
| A | avec VA | 908,4 | 887,6 | 22,2 | 12,3 | 0,0 | 10,8 | 118,0 | 72,4 | 44,7 | −68,2 | 0,0 | 4,0 | 29,5 | 9 % | 37 % |
| B | sans VA | 997,6 | 919,7 | 31,8 | 15,9 | 0,0 | 62,1 | 92,9 | 72,7 | 35,9 | −116,1 | 0,0 | 4,1 | 23,2 | 67 % | 267 % |
| B | avec VA | 997,6 | 908,1 | 38,0 | 14,9 | 0,0 | 66,4 | 96,6 | 73,8 | 40,3 | −120,4 | 0,0 | 4,1 | 24,1 | 69 % | 275 % |
| C | sans VA | 1 040,7 | 934,6 | 29,4 | 7,8 | 3,0 | 81,5 | 88,8 | 76,4 | 27,9 | −151,2 | −3,0 | 4,2 | 22,2 | 92 % | 367 % |
| C | avec VA | 1 040,7 | 924,1 | 32,8 | 7,4 | 4,8 | 86,3 | 89,3 | 76,3 | 32,3 | −154,5 | −4,8 | 4,2 | 22,3 | 97 % | 387 % |

**Pertes nettes par choc (base avec VA)**

| Profil | taux hausse | taux baisse | actions | spread | rachats hausse | rachats baisse | rachat massif | mortalite | frais |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 14,6 | 0,2 | 29,1 | 46,4 | 25,9 | −44,0 | 43,0 | 0,9 | 3,1 |
| B | 7,8 | 5,2 | 34,1 | 44,2 | 21,9 | −37,3 | 38,8 | 1,3 | 2,8 |
| C | 12,1 | 1,7 | 34,7 | 45,8 | 20,9 | −36,3 | 31,0 | 1,4 | 2,3 |

**Repères de place** : taux de couverture du SCR de 250 % pour l'ensemble des organismes et de 240 % pour les autres organismes vie et mixtes (hors bancassureurs) fin 2025 (ACPR n° 181), 250 % et 239 % au 30/06/2026 (ACPR n° 185, chiffres repris par la presse), 221 % puis 219 % pour les bancassureurs. Ces ratios intègrent la VA et la mesure transitoire sur les provisions techniques, et reposent sur des modèles complets, souvent des modèles internes. L'indicateur simplifié ne prend pas la mesure transitoire et n'a pas été ajusté pour s'en approcher : l'écart est un résultat, pas un défaut de calibrage.

## 6. Profil A : besoins de capital risque neutre et recapitalisation réelle

- **Risque neutre** (valorisation) : un apport dans 37 % des scénarios, de valeur actuelle moyenne 13,4 (q99 102,5). Ce chiffre mesure le coût, pour l'actionnaire, de l'option de défaut de l'actif et des garanties ; ce n'est pas une probabilité de recapitalisation.
- **Probabilité réelle** : apport (actif épuisé) avec une probabilité de 0,2 % sur 10 ans et 1,3 % sur l'horizon ; fonds propres comptables négatifs avant 10 ans dans 0,9 % des scénarios (seuil comptable de recapitalisation). En stress (probabilités réelles égales à la moitié des probabilités risque neutre) : 0,9 % et 4,8 % d'apports, 5,0 % de fonds propres négatifs avant 10 ans.
- **Liquidité extrême** (réel, 10 ans) : sorties annuelles maximales de 35 % au q99, moins-values réalisées de 91,6 au q99 ; elles dépassent la réserve de capitalisation dans 25 % des scénarios.
- Effet des conventions en probabilité réelle, rachat structurel de 5 % : apports sur l'horizon 1,8 %, fonds propres négatifs avant 10 ans 1,3 %, rachat moyen 6,6 %.
- Effet des conventions en probabilité réelle, transmission immédiate des taux : apports sur l'horizon 12,7 %, fonds propres négatifs avant 10 ans 12,3 %, rachat moyen 10,3 %.
- Effet des conventions en probabilité réelle, bloc souverain de 26 % : apports sur l'horizon 1,4 %, fonds propres négatifs avant 10 ans 1,4 %, rachat moyen 5,6 %.
- **Vue prudentielle simplifiée** : indicateur de couverture du SCR de 9 % (avec impôts différés actifs reconnus : 20 % ; sans fonds excédentaires : −1 %) et du MCR de 37 %.

**Lecture.** Le profil A reste un cas de fragilité financière : sa valeur économique est faible et très sensible aux conventions, et il couvre mal son SCR approché. Mais l'indicateur prudentiel est simplifié (pas de mesure transitoire, pas de modèle interne, pas de reconnaissance d'impôts différés actifs, fonds excédentaires par l'approche simplifiée). Une couverture insuffisante ne vaut donc pas constat d'insolvabilité réglementaire. Elle signale qu'un tel assureur relèverait d'un plan de rétablissement si un calcul complet la confirmait. En probabilité réelle, il honore ses engagements dans la très grande majorité des scénarios : sa fragilité vient de l'absence de coussin, pas d'une défaillance attendue.

## 7. Hypothèses les plus fragiles

| Hypothèse | Pourquoi elle compte |
| --- | --- |
| Référence des assurés | proxy fictif ; écart entre lissages 3 et 10 ans : 13,1 (A), 14,4 (B), 15,9 (C) |
| Loi de rachat dynamique | écart entre corridors ONC minimal et maximal : 64,6 (A), 46,3 (B), 39,4 (C) |
| Structure de défaut | écart entre 50 blocs corrélés et bloc souverain de 26 % : 0,9 (A), 2,8 (B), 4,7 (C) ; avec le bloc unique : 16,6 (A), 35,5 (B), 43,1 (C) |
| Spread | élargissement instantané de 100 pb : −50,5 (A), −46,9 (B), −52,0 (C) |
| Part de crédit kappa | écart entre 0,55 et 1 : 5,5 (A), 8,5 (B), 9,0 (C) |
| Probabilité réelle de défaut | taux historique d'entreprises notées comme le portefeuille ; rapport d'environ 24 avec le risque neutre (section 2.4), contre 2 publié pour les souverains de la zone euro |
| Indicateur prudentiel | sans mesure transitoire, ajustement symétrique nul, spread ventilé selon la place, fonds excédentaires simplifiés |
| Données de place manquantes | ACPR n° 185 (moins-values 2026, composition des fonds propres et du SCR), quartiles de rachat du n° 179 |

