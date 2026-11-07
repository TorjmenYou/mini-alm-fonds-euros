# V5 : synthèse avant l'optimisation des stratégies ALM

Généré par `scripts/v5_rapport_synthese.py` depuis `resultats/v5_synthese.json` (`scripts/v5_synthese.py`) et `resultats/v5_calibration_credit.json` (`scripts/v5_calibration_credit.py`). Unités fictives : 1 unité = 10 M€, PM initiale de 1 000. 1 000 scénarios, valorisation risque neutre au 31/10/2026, base sans VA sauf mention, valeurs avant impôt sauf dans la vue prudentielle. **Les trois profils sont fictifs** et ne sont pas ajustés pour être rentables ou solvables. Aucune stratégie n'est optimisée ici.

Le PDF de l'ACPR n° 185 n'a pas pu être consulté : ses chiffres ne sont utilisés que lorsqu'ils sont repris par une source secondaire, et signalés comme tels.

## 1. Conventions centrales retenues pour la suite (provisoires)

| Élément | Convention | Statut | Fragilité |
| --- | --- | --- | --- |
| Valorisation | Base sans VA ; la VA est une vue réglementaire | Choix de méthode | Faible |
| Spread des obligations | Spread zéro-coupon OAT par bootstrap du TEC (159 pb à 10 ans, contre 147 pb avec le TEC pris comme zéro-coupon) | Calibré | Moyenne : interpolation entre six maturités observées, pas de TEC à 1 an |
| Part de crédit du spread | kappa = 0,70 | Calibré sur le CDS et le quanto publié | **Forte** : quanto France à 5 ans non observé |
| Forme des pertes risque neutre | 70 % par saut (recouvrement 40 %), 30 % hors défaut lissé | Hypothèse | Moyenne |
| Structure de défaut | 50 blocs, copule gaussienne à un facteur, rho = 0,2 ; bloc souverain de 26 % et bloc unique en stress | Hypothèse | **Forte** : la France est un émetteur unique pour 26 % des obligations |
| Probabilité réelle | Probabilité de défaut de 0,061 % par an et par bloc, recouvrement 50 % | Calibré (défauts d'entreprises par notation) | Forte pour le souverain français de 2026 |
| Référence des assurés | **Proxy comportemental fictif** : taux sans risque 10 ans lissé sur 7 ans, niveau initial 2,88 % | Hypothèse | **Forte** ; confrontée à une référence composite à niveaux observés |
| Rachat structurel | 4,4 % au sens de l'ACPR (paramètre du modèle 4,331 %) ; 5 % en sensibilité | Observé, converti | Moyenne : dénominateur ACPR imprécis, année de rachats bas |
| Loi de rachat dynamique | Paramètres des V1 à V4, entre les corridors minimal et maximal de l'ONC 2013 | Hypothèse | Forte : non calée sur des données |

## 2. Calibration du risque souverain

### 2.1 Du TEC aux taux zéro-coupon

Le TEC est un rendement au pair. Le prendre comme taux zéro-coupon sous-estime le spread quand la courbe monte. Le bootstrap (coupons annuels, TEC interpolés entre les maturités observées) corrige l'écart :

| Maturité | TEC | Zéro-coupon OAT | Spread, TEC comme zéro-coupon | Spread zéro-coupon | Écart |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 ans | 3,64 % | 3,64 % | 35 pb | 35 pb | 0,0 pb |
| 3 ans | 3,84 % | 3,85 % | 54 pb | 54 pb | −0,7 pb |
| 5 ans | 4,24 % | 4,27 % | 92 pb | 95 pb | 3,2 pb |
| 7 ans | 4,50 % | 4,55 % | 114 pb | 121 pb | 6,7 pb |
| 10 ans | 4,88 % | 5,00 % | 147 pb | 159 pb | 11,8 pb |
| 15 ans | 5,17 % | 5,36 % | 170 pb | 188 pb | 18,1 pb |
| 20 ans | 5,30 % | 5,53 % | 186 pb | 208 pb | 21,3 pb |
| 30 ans | 5,41 % | 5,68 % | 202 pb | 228 pb | 25,2 pb |

Sous 2 ans, faute de TEC à 1 an, le spread est prolongé à plat. Les conventions de sécurisation (codes commençant par « k ») utilisent le spread zéro-coupon ; les premières variantes gardent l'ancien, pour rester reproductibles.

### 2.2 Des spreads aux intensités de défaut

Règles, pour une année t (de t - 1 à t) :

- spread cumulé : H(t) = s(t) x t, avec s le spread zéro-coupon continu ;
- coût risque neutre de l'année : dH(t) = H(t) - H(t - 1), soit le spread à terme d'un an ; il est partagé entre crédit (kappa x dH) et hors défaut ((1 - kappa) x dH) ;
- probabilité risque neutre de défaut d'un bloc : p(t) = (1 - exp(-kappa x dH(t))) / (1 - R), si bien que 1 - p(t) x (1 - R) = exp(-kappa x dH(t)) : la perte moyenne reproduit exactement le prix de marché ;
- facteur de nominal moyen de l'année : exp(-(1 - kappa) x dH(t)) x (1 - p(t) x (1 - R)) = exp(-dH(t)).

Convention centrale (kappa = 0,7, R = 40 %) :

| Année | Spread cumulé H | Coût de l'année dH | dont crédit | dont hors défaut | Probabilité de défaut de l'année | Probabilité cumulée |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 35 pb | 35 pb | 25 pb | 11 pb | 0,41 % | 0,4 % |
| 2 | 71 pb | 35 pb | 25 pb | 11 pb | 0,41 % | 0,8 % |
| 3 | 161 pb | 90 pb | 63 pb | 27 pb | 1,04 % | 1,9 % |
| 5 | 475 pb | 179 pb | 126 pb | 54 pb | 2,08 % | 5,4 % |
| 7 | 845 pb | 197 pb | 138 pb | 59 pb | 2,28 % | 9,4 % |
| 10 | 1 589 pb | 276 pb | 193 pb | 83 pb | 3,19 % | 17,0 % |
| 15 | 2 815 pb | 286 pb | 200 pb | 86 pb | 3,30 % | 28,1 % |
| 20 | 4 156 pb | 296 pb | 207 pb | 89 pb | 3,41 % | 38,6 % |
| 30 | 6 829 pb | 291 pb | 204 pb | 87 pb | 3,36 % | 55,1 % |

Le coût de l'année croît avec le temps parce que les spreads zéro-coupon montent avec la maturité : le spread à terme dépasse le spread comptant. C'est ce coût à terme, et non le spread affiché, que la valorisation risque neutre fait payer chaque année.

### 2.3 Contrôle avec le CDS à 5 ans

Triangle du crédit : CDS ≈ intensité x (1 - R). Avec le CDS de 91 pb et R = 40 %, l'intensité vaut 1,52 % par an, soit une probabilité cumulée de 7,3 % sur 5 ans. Le modèle donne 7,6 % si tout le spread est du crédit (kappa = 1) et 5,4 % avec kappa = 0,7. Le premier chiffre recoupe le CDS : la structure du modèle (spread zéro-coupon, recouvrement en valeur de marché) est cohérente avec la cotation. L'écart restant tient à la convention de recouvrement, au type de rendement et aux dates.

### 2.4 Part de crédit kappa : maturité, type de rendement, devise

- **Maturité** : seul le CDS à 5 ans est disponible ; il est comparé au spread zéro-coupon à 5 ans (95,0 pb). Au-delà, kappa est supposé constant (hypothèse).
- **Type de rendement** : le CDS est une prime courante ; le spread du modèle est un spread zéro-coupon continu. À 5 ans, l'écart entre les deux reste de second ordre devant l'effet de devise.
- **Devise** : le CDS France est coté en dollars. En cas de défaut, l'euro devrait se déprécier, si bien qu'un CDS en dollars vaut plus qu'un CDS en euros. Le quanto relatif publié vaut environ 28 % pour la France à 1 an et jusqu'à 44 % pour l'Allemagne à 5 ans (Augustin, Chernov et Song). D'où kappa = (1 - d) x CDS / spread : 0,69 avec d = 28 %, 0,54 avec d = 44 %, 0,96 sans quanto. Valeur centrale 0,7 ; sensibilités 0,55 et 1.
- **Dates** : CDS du 29/10, TEC du 04/11 ; le CDS est passé de 104 à 91 pb en une semaine, soit une incertitude d'environ ±0,1 sur kappa.

### 2.5 Liquidité et prime de risque

- **Composante hors défaut (30 % du spread)** : elle regroupe la liquidité relative, l'offre de titres et le risque de change non lié au défaut. Repère : le Bund à 10 ans (environ 3,25 %, TEC moins l'écart OAT-Bund) cote près de la courbe sans risque EIOPA (3,35 %). Un émetteur presque sans risque de défaut ne porte donc pas de prime hors défaut notable au-dessus de cette courbe. La composante hors défaut de l'OAT est la part du spread que le CDS en euros n'explique pas, pas une mesure directe de liquidité. En valorisation, elle reste un coût risque neutre (absence d'arbitrage) ; en probabilité réelle, c'est une prime.
- **Prime de risque de crédit** : c'est l'écart entre la perte risque neutre et la perte réelle. Les probabilités de « 3,3 % » et « 0,06 % » ne mesurent pas la même chose. La première (3,19 % avec le spread zéro-coupon) est la probabilité d'un bloc **l'année 10**, tirée du spread **à terme**. Sa moyenne sur 10 ans vaut 1,85 % par an. La seconde (0,061 %) est un taux de défaut historique moyen d'entreprises notées comme le portefeuille de place (S&P, 1981-2024), et non une mesure propre au souverain français de 2026. Sur une base comparable (moyennes annuelles sur 10 ans), le rapport vaut environ 30, contre un rapport publié de 2 pour les souverains de la zone euro. Il y a deux lectures. Soit le marché paie en 2026 une forte prime pour un risque de queue politique et budgétaire. Soit la probabilité réelle historique sous-estime le risque actuel. Le stress « rapport de 2 » en probabilité réelle couvre la seconde lecture.

### 2.6 Intensité, recouvrement et blocs

L'intensité ne dépend pas de la taille des blocs : chaque bloc a la même probabilité p(t). La perte moyenne de l'année est donc identique quelle que soit la structure. Seule la concentration change :

| Structure | Blocs | Plus gros bloc | Perte si ce bloc fait défaut (R = 40 %) | Probabilité risque neutre de défaut de ce bloc sur 10 ans | Probabilité réelle |
| --- | ---: | ---: | ---: | ---: | ---: |
| Souverain 26 % + 20 blocs | 21 | 26 % | 15,6 % des obligations | 17,0 % | 0,61 % |
| 50 blocs égaux | 50 | 2 % | 1,2 % des obligations | 17,0 % | 0,61 % |
| Souverain 26 % + 50 blocs | 51 | 26 % | 15,6 % des obligations | 17,0 % | 0,61 % |
| Bloc unique | 1 | 100 % | 60,0 % des obligations | 17,0 % | 0,61 % |

La copule gaussienne (rho = 0,2) garde la probabilité de chaque bloc mais regroupe les défauts dans les mêmes années. Le recouvrement joue en sens inverse de l'intensité : un recouvrement de 63 % au lieu de 40 % donne des défauts plus fréquents mais moins coûteux, pour la même perte moyenne.

### 2.7 Valeur selon la structure de défaut et la part de crédit

| Convention | Valeur A | Valeur B | Valeur C | Apports A | Apports B | Apports C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Spread entièrement lissé | −0,1 ± 6,4 | 84,3 ± 6,0 | 111,1 ± 5,2 | 46 % | 3 % | 2 % |
| 50 blocs indépendants | −3,0 ± 7,1 | 80,2 ± 6,0 | 107,9 ± 5,3 | 50 % | 4 % | 2 % |
| **50 blocs corrélés (centre)** | −6,2 ± 7,0 | 72,0 ± 5,7 | 98,4 ± 4,9 | 52 % | 7 % | 5 % |
| Souverain 26 % + 50 blocs corrélés | −7,7 ± 6,9 | 65,8 ± 6,1 | 89,9 ± 5,5 | 49 % | 13 % | 9 % |
| Souverain 26 % + 20 blocs (corrélé par bloc) | −7,0 ± 6,6 | 69,7 ± 6,1 | 94,8 ± 5,6 | 52 % | 12 % | 8 % |
| Bloc unique | −26,0 ± 7,5 | 25,8 ± 6,5 | 44,4 ± 6,7 | 56 % | 49 % | 47 % |
| kappa = 0,55 | −4,2 ± 6,8 | 75,1 ± 5,9 | 101,7 ± 5,1 | 53 % | 6 % | 4 % |
| kappa = 1 | −10,4 ± 7,1 | 64,9 ± 5,8 | 90,1 ± 5,4 | 55 % | 11 % | 8 % |
| Recouvrement 63 % | −4,9 ± 7,0 | 75,2 ± 5,7 | 101,5 ± 5,3 | 51 % | 7 % | 4 % |

### 2.8 D'où vient la baisse de valeur avec le défaut par saut

Test d'attribution, mêmes tirages, spread lissé contre spread par saut (bloc souverain de 26 %), référence centrale :

| Profil | Passif | Valeur, spread lissé | Valeur, saut | Écart | BE garanti, lissé | BE garanti, saut | FDB, lissé | FDB, saut |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Indépendant des actifs (taux servi = TMG, sans participation ni rachat dynamique) | 181,0 | 181,0 | 0,0 | 663,4 | 663,4 | 0,0 | 0,0 |
| A | Participation et TMG, sans rachat dynamique | 61,3 | 38,2 | −23,1 | 663,4 | 663,4 | 112,9 | 134,6 |
| A | Modèle complet | −0,1 | −7,0 | −6,8 | 813,5 | 796,6 | 46,9 | 67,1 |
| B | Indépendant des actifs (taux servi = TMG, sans participation ni rachat dynamique) | 299,6 | 299,6 | 0,0 | 640,3 | 640,3 | 0,0 | 0,0 |
| B | Participation et TMG, sans rachat dynamique | 110,8 | 93,7 | −17,1 | 640,3 | 640,3 | 177,6 | 193,8 |
| B | Modèle complet | 84,3 | 69,7 | −14,6 | 724,8 | 718,3 | 132,7 | 152,3 |

Quand le passif ne dépend pas des actifs, la forme des pertes ne change rien à la valeur (écart de 0,00 pour B, BE identiques scénario par scénario ; test `test_passif_independant_des_actifs_meme_be_quelle_que_soit_la_forme_des_pertes`). La comptabilisation des défauts ne crée donc ni ne détruit de valeur, ce que confirment aussi les fuites nulles. La baisse apparaît dès que la participation et le TMG entrent en jeu (−23,1 pour A, −17,1 pour B) ; dans le modèle complet, les rachats dynamiques la réduisent (−6,8 pour A, −14,6 pour B), parce qu'ils rendent déjà le passif très non linéaire en spread lissé. Le mécanisme est une asymétrie : les années sans défaut, l'excédent de produits est partagé à 85 % avec les assurés ; les années de défaut, la perte sous le TMG et la marge abandonnée restent à l'actionnaire. Concentrer les pertes transfère donc de la valeur de l'actionnaire vers les assurés.

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

### 3.3 Référence des assurés : proxy fictif et référence composite observée

Référence composite (niveaux observés, délais et coefficients paramétrés, **poids fictifs**) : Fonds euros concurrents (60 % ; niveau 2,63 % ; transmission lissée sur 7 ans ; coefficient de réaction 1,0) ; Livret A (25 % ; niveau 1,70 % ; transmission immédiate ; coefficient de réaction 0,5) ; Placements obligataires directs (OAT 10 ans) (15 % ; niveau 4,88 % ; transmission immédiate ; coefficient de réaction 1,0). Niveau initial : 2,735 %, sans calage sur 2,88 %.

| Référence ou loi | Valeur A | Valeur B | Valeur C | Rachat 1-10 A | Rachat 1-10 B | Rachat 1-10 C | Duration BE A | Duration BE B | Duration BE C |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Proxy lissé sur 3 ans | −15,5 ± 7,6 | 62,2 ± 6,5 | 87,0 ± 6,0 | 12,8 % | 9,0 % | 8,3 % | 1,3 | 1,9 | 3,1 |
| Proxy lissé sur 5 ans | −9,8 ± 7,3 | 68,4 ± 6,2 | 94,2 ± 5,5 | 12,1 % | 8,2 % | 7,6 % | 2,3 | 3,0 | 3,7 |
| **Proxy lissé sur 7 ans (centre)** | −6,2 ± 7,0 | 72,0 ± 5,7 | 98,4 ± 4,9 | 11,6 % | 7,8 % | 7,2 % | 3,1 | 3,9 | 4,3 |
| Proxy lissé sur 10 ans | −2,7 ± 6,3 | 75,1 ± 5,0 | 101,8 ± 4,4 | 11,2 % | 7,4 % | 7,0 % | 3,9 | 4,9 | 5,5 |
| Composite à niveaux observés | −5,7 ± 6,6 | 74,0 ± 5,6 | 99,0 ± 5,3 | 11,3 % | 7,7 % | 7,2 % | 3,3 | 5,0 | 5,8 |
| Transmission immédiate (sans risque 10 ans) | −26,9 ± 8,0 | 47,4 ± 6,9 | 70,8 ± 6,5 | 14,2 % | 10,9 % | 10,3 % | −0,1 | 0,5 | 2,8 |
| Référence figée | 14,3 ± 1,9 | 87,9 ± 2,5 | 112,7 ± 3,0 | 10,1 % | 6,8 % | 6,4 % | 7,2 | 10,7 | 13,4 |
| Réaction faible (corridor minimal ONC) | 31,9 ± 7,5 | 92,4 ± 6,2 | 115,4 ± 5,3 | 5,2 % | 4,8 % | 4,8 % | 5,6 | 5,9 | 6,0 |
| Réaction forte (corridor maximal ONC) | −36,4 ± 3,1 | 41,5 ± 3,5 | 68,9 ± 3,4 | 22,4 % | 15,8 % | 14,7 % | 3,0 | 4,1 | 5,0 |
| Rachat structurel 5 % | −9,8 ± 6,2 | 67,3 ± 5,0 | 93,2 ± 4,4 | 12,6 % | 8,6 % | 8,1 % | 3,2 | 4,0 | 4,4 |

## 4. Synthèse par profil

### Profil A : Assureur historique sous pression

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | −6,2 ± 7,0 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de −36,4 à 31,9 |
| | Équivalent certain | 16,5 |
| BE et TVOG | BE stochastique | 900,0 |
| | TVOG (BE stochastique - équivalent certain) | 22,8 |
| | FDB | 62,3 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 11,6 % / 5,9 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 35 % / 35 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 190,5 / 103,1 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 52 % ; 21,0 ; 132,1 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,3 % ; 1,2 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 1,0 % / 4,9 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 113,8 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | −0,2 (14,9) |
| | SCR approché / MCR approché, base avec VA | 118,1 / 29,5 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **0 %** ; 14 % ; −13 % |
| | Indicateur de couverture simplifié du MCR | −1 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −48,8 |
| | Défaut : bloc souverain de 26 % / bloc unique | −0,7 / −19,8 |
| | Part de crédit 0,55 / 1 | 2,1 / −4,1 |
| | Référence : lissage 3 ans / 10 ans / composite observée / immédiate | −9,2 / 3,5 / 0,6 / −20,6 |
| | Réaction faible / forte (ONC) | 38,1 / −30,2 |
| | Rachat structurel 5 % ; base avec VA | −3,6 ; 12,4 |

### Profil B : Assureur intermédiaire

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | 72,0 ± 5,7 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de 25,8 à 92,4 |
| | Équivalent certain | 97,2 |
| BE et TVOG | BE stochastique | 915,7 |
| | TVOG (BE stochastique - équivalent certain) | 25,2 |
| | FDB | 146,5 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 7,8 % / 4,4 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 36 % / 15 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 80,4 / 7,2 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 7 % ; 3,5 ; 60,3 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,0 % ; 0,0 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 0,0 % / 0,4 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 96,9 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | 69,7 (18,7) |
| | SCR approché / MCR approché, base avec VA | 102,3 / 25,6 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **68 %** ; 72 % ; 50 % |
| | Indicateur de couverture simplifié du MCR | 273 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −47,9 |
| | Défaut : bloc souverain de 26 % / bloc unique | −2,3 / −46,2 |
| | Part de crédit 0,55 / 1 | 3,1 / −7,1 |
| | Référence : lissage 3 ans / 10 ans / composite observée / immédiate | −9,8 / 3,1 / 2,0 / −24,6 |
| | Réaction faible / forte (ONC) | 20,4 / −30,5 |
| | Rachat structurel 5 % ; base avec VA | −4,6 ; 13,2 |

### Profil C : Assureur plus récemment investi

| Rubrique | Indicateur | Valeur |
| --- | --- | ---: |
| Valeur actionnaire | Actif - BE stochastique (avant impôt) | 98,4 ± 4,9 |
| | Fourchette selon les conventions testées (hors chocs et hors VA) | de 44,4 à 115,4 |
| | Équivalent certain | 121,8 |
| BE et TVOG | BE stochastique | 923,0 |
| | TVOG (BE stochastique - équivalent certain) | 23,4 |
| | FDB | 186,7 |
| Rachats | Structurel (sens ACPR) | 4,4 % |
| | Année 1, risque neutre / réel (paramètre du modèle ; 4,39 % au sens de l'ACPR) | 4,33 % / 4,33 % |
| | Moyenne années 1 à 10, risque neutre / réel | 7,2 % / 4,3 % |
| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | 36 % / 14 % |
| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | 106,8 / 13,1 |
| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | 5 % ; 2,0 ; 38,1 |
| | Apports, réel : probabilité sur 10 ans, sur l'horizon | 0,0 % ; 0,0 % |
| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | 0,0 % / 0,3 % |
| Capital | SCR approché, base sans VA (capital économique approché) | 99,9 |
| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | 80,3 (8,7) |
| | SCR approché / MCR approché, base avec VA | 102,0 / 25,5 |
| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **79 %** ; 79 % ; 70 % |
| | Indicateur de couverture simplifié du MCR | 315 % |
| Sensibilités de la valeur | Spread +100 pb instantané | −54,4 |
| | Défaut : bloc souverain de 26 % / bloc unique | −3,5 / −53,9 |
| | Part de crédit 0,55 / 1 | 3,3 / −8,3 |
| | Référence : lissage 3 ans / 10 ans / composite observée / immédiate | −11,4 / 3,4 / 0,6 / −27,6 |
| | Réaction faible / forte (ONC) | 17,1 / −29,5 |
| | Rachat structurel 5 % ; base avec VA | −5,2 ; 12,0 |

## 5. Vue prudentielle complétée

Fonds propres éligibles de niveau 1 = actif - BE - marge de risque + fonds excédentaires - impôts différés passifs. Les impôts différés actifs (niveau 3, plafonnés à 15 % du SCR) ne sont pas reconnus au centre, faute de démonstration de recouvrabilité (l'ACPR exige un horizon de profits futurs inférieur à 5 ans, justifié au-delà). Fonds excédentaires : approche simplifiée de l'ACPR, la PPB admissible entre en PM au bout de huit ans puis sort au rythme des prestations projetées. La PPB admissible est prise égale à la PPB comptable : les profils n'ont ni montants préaffectés ni dotations de plus de sept ans à redistribuer (paramètre fictif). SCR : taux, actions (39 %, ajustement symétrique nul), spread (part non souveraine de 66 %, ventilée par qualité de crédit selon la place), rachat (hausse, baisse, massif), mortalité (+15 %), frais (+10 %, sans inflation), opérationnel (0,45 % des provisions, plafonné à 30 % du BSCR) ; absorption par les FDB (hors fonds excédentaires) et par les impôts différés passifs. MCR : formule linéaire vie réduite aux contrats avec participation (3,7 % des prestations garanties - 5,2 % des FDB), entre 25 % et 45 % du SCR.

| Profil | Base | Actif | BE | Marge de risque | Fonds excédentaires | Impôts différés passifs | Fonds propres niveau 1 | SCR | dont marché net | dont vie nette | Ajustement FDB | Ajustement impôts | Opérationnel | MCR | Indicateur SCR | Indicateur MCR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | sans VA | 893,8 | 900,0 | 18,5 | 15,4 | 0,0 | −9,4 | 113,8 | 69,6 | 39,3 | −46,9 | 0,0 | 4,1 | 28,5 | −8 % | −33 % |
| A | avec VA | 893,8 | 887,7 | 21,3 | 14,9 | 0,0 | −0,2 | 118,1 | 71,9 | 44,6 | −57,6 | 0,0 | 4,0 | 29,5 | 0 % | −1 % |
| B | sans VA | 987,7 | 915,7 | 28,0 | 20,0 | 0,0 | 64,0 | 96,9 | 76,3 | 37,1 | −102,1 | 0,0 | 4,1 | 24,2 | 66 % | 264 % |
| B | avec VA | 987,7 | 902,5 | 34,1 | 18,7 | 0,0 | 69,7 | 102,3 | 78,7 | 42,4 | −106,1 | 0,0 | 4,1 | 25,6 | 68 % | 273 % |
| C | sans VA | 1 021,4 | 923,0 | 30,7 | 9,4 | 0,7 | 76,3 | 99,9 | 83,0 | 32,6 | −135,7 | −0,7 | 4,2 | 25,0 | 76 % | 306 % |
| C | avec VA | 1 021,4 | 911,0 | 36,5 | 8,7 | 2,3 | 80,3 | 102,0 | 83,8 | 37,8 | −140,7 | −2,3 | 4,1 | 25,5 | 79 % | 315 % |

**Pertes nettes par choc (base avec VA)**

| Profil | taux hausse | taux baisse | actions | spread | rachats hausse | rachats baisse | rachat massif | mortalite | frais |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 12,1 | 1,0 | 29,8 | 45,7 | 26,3 | −47,1 | 42,7 | 0,9 | 3,6 |
| B | 9,2 | 2,8 | 37,6 | 45,9 | 23,1 | −41,3 | 39,8 | 1,2 | 4,7 |
| C | 14,7 | −2,1 | 39,6 | 48,5 | 23,1 | −41,9 | 35,0 | 1,4 | 5,0 |

**Repères de place** : taux de couverture du SCR de 250 % pour l'ensemble des organismes et de 240 % pour les autres organismes vie et mixtes (hors bancassureurs) fin 2025 (ACPR n° 181), 250 % et 239 % au 30/06/2026 (ACPR n° 185, chiffres repris par la presse), 221 % puis 219 % pour les bancassureurs. Ces ratios intègrent la VA et la mesure transitoire sur les provisions techniques, et reposent sur des modèles complets, souvent des modèles internes. L'indicateur simplifié ne prend pas la mesure transitoire et n'a pas été ajusté pour s'en approcher : l'écart est un résultat, pas un défaut de calibrage.

## 6. Profil A : besoins de capital risque neutre et recapitalisation réelle

- **Risque neutre** (valorisation) : un apport dans 52 % des scénarios, de valeur actuelle moyenne 21,0 (q99 132,1). Ce chiffre mesure le coût, pour l'actionnaire, de l'option de défaut de l'actif et des garanties ; ce n'est pas une probabilité de recapitalisation.
- **Probabilité réelle** : apport (actif épuisé) avec une probabilité de 0,3 % sur 10 ans et 1,2 % sur l'horizon ; fonds propres comptables négatifs avant 10 ans dans 1,0 % des scénarios (seuil comptable de recapitalisation). En stress (probabilités réelles égales à la moitié des probabilités risque neutre) : 0,7 % et 5,3 % d'apports, 4,9 % de fonds propres négatifs avant 10 ans.
- **Liquidité extrême** (réel, 10 ans) : sorties annuelles maximales de 35 % au q99, moins-values réalisées de 103,1 au q99 ; elles dépassent la réserve de capitalisation dans 28 % des scénarios.
- Effet des conventions en probabilité réelle, rachat structurel de 5 % : apports sur l'horizon 2,1 %, fonds propres négatifs avant 10 ans 1,5 %, rachat moyen 6,9 %.
- Effet des conventions en probabilité réelle, transmission immédiate des taux : apports sur l'horizon 13,0 %, fonds propres négatifs avant 10 ans 12,5 %, rachat moyen 10,7 %.
- Effet des conventions en probabilité réelle, bloc souverain de 26 % : apports sur l'horizon 1,3 %, fonds propres négatifs avant 10 ans 1,4 %, rachat moyen 5,9 %.
- **Vue prudentielle simplifiée** : indicateur de couverture du SCR de 0 % (avec impôts différés actifs reconnus : 14 % ; sans fonds excédentaires : −13 %) et du MCR de −1 %.

**Lecture.** Le profil A reste un cas de fragilité financière : sa valeur économique est faible et très sensible aux conventions, et il couvre mal son SCR approché. Mais l'indicateur prudentiel est simplifié (pas de mesure transitoire, pas de modèle interne, pas de reconnaissance d'impôts différés actifs, fonds excédentaires par l'approche simplifiée). Une couverture insuffisante ne vaut donc pas constat d'insolvabilité réglementaire. Elle signale qu'un tel assureur relèverait d'un plan de rétablissement si un calcul complet la confirmait. En probabilité réelle, il honore ses engagements dans la très grande majorité des scénarios : sa fragilité vient de l'absence de coussin, pas d'une défaillance attendue.

## 7. Hypothèses les plus fragiles

| Hypothèse | Pourquoi elle compte |
| --- | --- |
| Référence des assurés | proxy fictif ; écart entre lissages 3 et 10 ans : 12,7 (A), 12,9 (B), 14,8 (C) |
| Loi de rachat dynamique | écart entre corridors ONC minimal et maximal : 68,3 (A), 51,0 (B), 46,5 (C) |
| Structure de défaut | écart entre 50 blocs corrélés et bloc souverain de 26 % : 0,7 (A), 2,3 (B), 3,5 (C) ; avec le bloc unique : 19,8 (A), 46,2 (B), 53,9 (C) |
| Spread | élargissement instantané de 100 pb : −48,8 (A), −47,9 (B), −54,4 (C) |
| Part de crédit kappa | écart entre 0,55 et 1 : 6,2 (A), 10,2 (B), 11,6 (C) |
| Probabilité réelle de défaut souverain | historique d'entreprises, rapport de 30 avec le risque neutre contre 2 publié |
| Indicateur prudentiel | sans mesure transitoire, ajustement symétrique nul, spread ventilé selon la place, fonds excédentaires simplifiés |
| Données de place manquantes | ACPR n° 185 (moins-values 2026, composition des fonds propres et du SCR), quartiles de rachat du n° 179 |

