# Méthodologie du mini-modèle ALM fonds euros

Ce document décrit les équations réellement implémentées, version par version, avec leurs hypothèses, leurs paramètres, leurs simplifications et les tests qui les valident. Les résultats chiffrés sont dans le [README](../README.md) et dans `resultats/indicateurs.json`. Les principales corrections apportées au modèle, ses contrôles et ses limites sont résumés dans [AMELIORATIONS_ET_LIMITES.md](AMELIORATIONS_ET_LIMITES.md).

Conventions communes :
- pas de temps annuel ; un flux « de l'année t » court de la date t-1 à la date t et il est payé en fin d'année ;
- taux actuariels (composés annuellement), sauf le taux court du modèle de Hull-White, qui est continu ;
- montants dans une unité monétaire fictive (PM initiale = 1 000), en millions d'euros pour la V4 ;
- toutes les hypothèses sont dans `data/hypotheses.json` (V1 à V3) et dans `data/v4/` (V4).

---

## V1 : projection actif-passif déterministe

**Objectif.** Rendre visible la boucle actif-passif d'un fonds euros sur un chemin de taux.

### Passif (`src/passif.py`)

Pour une année t, avec PM la provision mathématique de début d'année, TS le taux servi net, q le taux de décès et ρ le taux de rachat :

- PM revalorisée = PM × (1 + TS)
- décès = PM revalorisée × q
- rachats = (PM revalorisée − décès) × ρ
- PM de fin = PM revalorisée × (1 − q) × (1 − ρ)

**Risques concurrents.** q est une probabilité de décès « indépendante », comme celle d'une table de mortalité. ρ est un taux de rachat mesuré parmi les assurés en vie, comme un taux d'expérience rapporté aux contrats en vigueur : il ne s'applique donc qu'aux survivants. La PM de fin est toujours positive ou nulle, et PM + intérêts = décès + rachats + PM de fin.

**Taux de rachat de l'année t** = min(1, max(0, ρ structurel + ρ conjoncturel)). La partie conjoncturelle suit la loi en paliers proposée par l'ACPR (2013) :
- elle est fonction de l'écart e = TS(t−1) − taux attendu(t) ;
- elle vaut ρ_max si e < α ;
- elle est linéaire entre α et β ;
- elle est nulle entre β et γ ;
- elle est linéaire entre γ et δ ;
- elle vaut ρ_min au-delà de δ.

Les rachats dépendent du taux servi de l'année précédente, celui que connaît l'assuré. Cela évite toute circularité dans la boucle.

### Actif (`src/actif.py`)

L'actif comprend une échelle obligataire (10 lignes au pair), des actions et du monétaire. Chaque ligne est suivie en valeur nette comptable (VNC) et en valeur de marché (VM).

- Obligation : VM = Σ coupon × nominal × P(t, t+k) + nominal × P(t, t+m), avec P les prix zéro-coupon de la courbe.
- Monétaire : il rapporte le taux à 1 an du début d'année.
- Actions : le scénario donne le facteur de rendement total G (valeur de fin, dividende compris / valeur de début). Dividende = min(2 % × VM de début ; G × VM de début), et VM ex-dividende = G × VM de début - dividende. Le total vaut toujours G × VM de début et le cours n'est jamais négatif. Le plafond ne joue que si G < 2 %, c'est-à-dire pour une perte de plus de 98 %. Un facteur négatif est refusé (erreur explicite).
- Ordre des opérations dans l'année :
  1. encaissement des revenus ;
  2. vente des actions au-delà de leur poids cible, avec une plus ou moins-value qui entre dans les produits financiers ;
  3. décision de taux servi ;
  4. paiement des prestations et des frais ;
  5. rééquilibrage vers 85 % d'obligations, 10 % d'actions et 5 % de monétaire, en valeur de marché.
- Ventes d'obligations : au prorata des lignes. La plus ou moins-value réalisée va à la réserve de capitalisation (RC). Si la RC est épuisée, la moins-value restante entre dans les produits financiers de l'année suivante, donc dans l'assiette de la participation.
- Réinvestissement : obligation à 10 ans au pair, au coupon au pair de la courbe du moment.

**Règle de liquidité.** Les prestations et les frais sont toujours payés. Si la trésorerie reste négative après la vente de toutes les obligations puis des actions nécessaires, l'assureur apporte le capital manquant (`apport_assureur`). Cet apport est ajouté aux fonds propres, et aucun emprunt implicite ne subsiste.

### Taux servi, participation et PPB (`src/strategie.py`)

**Ce qu'impose le Code des assurances, de façon simplifiée dans le modèle :**
- *Participation minimale, articles A132-11 à A132-14* : le modèle retient 85 % de la quote-part des produits financiers afférente aux provisions, soit (PM + PPB) / actif en VNC. Le compte de participation réglementaire est plus complet : solde technique, prélèvement de l'assureur (le plus élevé de 10 % du solde créditeur et de 4,5 % de certaines primes), report du solde débiteur, déduction des intérêts techniques. Le modèle ne le reproduit pas : c'est une approximation assumée.
- *Délai de distribution, article A132-16* : chaque dotation à la PPB est redistribuée au plus tard au bout de 8 ans. La PPB est suivie par génération, la reprise obligatoire de la génération de 8 ans est vérifiée à chaque vieillissement, et les reprises consomment les dotations les plus anciennes en premier.
- *Taux minimum garanti* : le taux servi ne descend pas sous le TMG, et l'assureur paie l'écart.

**Hypothèses de gestion propres au modèle :**
- Taux cible : taux à 10 ans du scénario - 0,5 point.
- Leviers si les planchers ne suffisent pas, dans cet ordre :
  1. reprise de PPB, plafonnée à 25 % du stock par an ;
  2. réalisation de plus-values actions ;
  3. abandon d'une partie de la marge de l'assureur (15 % de la quote-part financière).
- En cas d'excédent : dotation de la PPB jusqu'à 6 % de la PM, puis le surplus est servi.
- Extinction du portefeuille : quand la PM est nulle, plus rien n'est crédité, et la PPB restante est versée aux assurés à la date de leurs dernières prestations.
  - Rachat total à l'ouverture (rachat massif de 100 %) : la PPB est versée en t = 0, avec les rachats.
  - Extinction en cours de projection : la PPB restante et la dotation décidée pour l'année sont versées en fin d'année, avec les derniers rachats. La dotation n'est pas mise en provision, puisqu'il ne reste aucun contrat pour la recevoir plus tard.
  - Rachat partiel (par exemple le rachat massif de 40 % de la V3) : la PPB ne sort pas, elle reste aux contrats en vigueur. La valeur de rachat d'un contrat est sa PM.
  - C'est une convention du modèle. Le Code des assurances impose de redistribuer la PPB aux assurés sous 8 ans (article A132-16), sans en attacher une part à chaque contrat. Une autre convention possible serait une redistribution aux assurés sortis selon le calendrier des 8 ans : elle laisserait à l'assureur la valeur temps de la PPB.

**Résultat de l'assureur** = produits financiers - intérêts crédités nets - dotation de PPB + reprise de PPB - frais. Les chargements sur encours (0,7 %) restent à l'assureur ; les frais de gestion valent 0,4 % de l'encours.

### Indicateurs (`src/projection.py`)

Les valeurs sont actualisées avec le déflateur D(t) du scénario.

- **BE** = BE des prestations + BE des frais.
  - BE des prestations : Σ D(t) × (décès + rachats + PPB versée à l'extinction), plus, à l'horizon T, D(T) × (PM + PPB + part des plus-values latentes revenant aux assurés).
  - BE des frais : Σ D(t) × frais.
- **BE garanti.** C'est la valeur d'une projection parallèle qui garde les mêmes décès et les mêmes rachats que la projection complète, mais revalorise la PM au seul TMG. Il comprend les prestations garanties actualisées et la PM garantie restante à l'horizon.
- **FDB** (prestations discrétionnaires futures) = BE des prestations - BE garanti. À comportement des assurés identique, c'est la valeur de la participation aux bénéfices future, y compris la PPB.
- **Test de fuite** = VM initiale de l'actif - [Σ D(t) × (prestations + frais - apports) + D(T) × VM de l'actif à l'horizon]. Il est nul sur un scénario déterministe cohérent avec le marché, et nul en moyenne sur un jeu de scénarios risque neutre. Il vérifie qu'aucune valeur n'est créée ni perdue.

**Horizon.** 60 ans : il reste environ 10 % de la PM, et allonger l'horizon ne modifie presque plus le BE.

**Tests :**
- `tests/test_modele.py` : étapes 1 et 2, paliers de rachat, bilan, fuite, garanties ;
- `tests/test_decrements.py` ;
- `tests/test_liquidite.py` : scénarios extrêmes, fonds sous-doté, extinction, PPB à 8 ans ;
- `tests/test_extinction_ppb.py` : date et montant de la PPB versée au rachat total (en t = 0 et en cours de projection), PPB conservée au rachat partiel ;
- `tests/test_rendement_actions.py` : dividende + cours = G × VM de début pour G de 0 à 1,25, et valeur perdue égale à la perte exacte des actions dans un scénario de krach.

---

## V2 : scénarios stochastiques, Best Estimate et TVOG

**Objectif.** Valoriser les options et garanties du passif en univers risque neutre.

### Générateur de scénarios (`src/gse.py`, `src/courbes.py`)

**Taux : Hull-White à un facteur.** On pose r(t) = x(t) + φ(t), avec dx = -a x dt + σ dW et x(0) = 0. La fonction φ est calée exactement sur la courbe initiale P(0, .), qu'elle soit plate ou quelconque (courbe choquée de la V3). Le prix zéro-coupon s'écrit (Brigo et Mercurio, modèle G1++) :

$$P(t,T) = \frac{P(0,T)}{P(0,t)}\exp\Big(\tfrac12\,[V(t,T) - V(0,T) + V(0,t)] - B(t,T)\,x(t)\Big)$$

avec :
- B(t,T) = (1 - e^{-a(T-t)}) / a ;
- V(t,T) = σ²/a² [T - t + (2/a) e^{-a(T-t)} - (1/2a) e^{-2a(T-t)} - 3/(2a)].

**Simulation exacte au pas annuel.** On tire conjointement x(t+1) et l'intégrale de x sur l'année, selon une loi normale bivariée de variances et covariance connues (factorisation de Cholesky). Le déflateur se met à jour par :

D(t+1) = D(t) × exp(-∫φ - ∫x), avec ∫ₜᵗ⁺¹ φ = ln(P(0,t) / P(0,t+1)) + ½ [V(0,t+1) - V(0,t)]

Ainsi E[D(t)] = P(0,t) exactement : aucun biais de discrétisation.

**Actions.** Le rendement total de l'année vaut exp(∫r - σ_S²/2 + σ_S Z). Le choc Z est indépendant des taux : c'est une simplification, la corrélation taux-actions étant prise nulle.

**Tirages.** 500 paires antithétiques (Z, -Z), avec une graine fixe dans les hypothèses. Les intervalles de confiance se calculent sur les moyennes de paires, puisque les deux tirages d'une paire ne sont pas indépendants.

**Tests de martingale.** Les trois moyennes suivantes doivent valoir 1 à l'erreur de Monte-Carlo près :
- E[D(t)] / P(0,t) ;
- E[D(t) P(t,t+10)] / P(0,t+10), qui valide la formule de prix des obligations ;
- E[D(t) S(t)] / S(0).

### BE stochastique et TVOG (`src/stochastique.py`)

- **BE stochastique** : moyenne sur les scénarios des BE par scénario, avec son intervalle de confiance à 95 %.
- **BE équivalent certain** : BE du scénario déterministe où tous les actifs rapportent les taux forward de la courbe initiale, c'est-à-dire le scénario central de la V1.
- **TVOG** = BE stochastique - BE équivalent certain.
- **Décomposition.** Trois mécanismes sont activés ou désactivés : le plancher de TMG, les rachats dynamiques et le lissage par la PPB. Les 8 combinaisons tournent sur les mêmes tirages. La part de chaque mécanisme est sa valeur de Shapley, c'est-à-dire sa contribution marginale moyenne sur tous les ordres d'activation. Les interactions sont ainsi réparties à parts égales au lieu d'être attribuées à un seul mécanisme.

**Convergence.** Le script `scripts/convergence.py` relance le calcul avec 1 000, 2 000, 5 000 et 10 000 scénarios. Il donne l'estimation, l'erreur standard, l'intervalle de confiance et le temps de calcul (`resultats/convergence.csv`).

**Tests :**
- `tests/test_modele.py` : martingales, fuite, TVOG ;
- `tests/test_reproductibilite.py` ;
- `tests/test_coherence_versions.py` : la V2 sans volatilité retrouve la V1.

---

## V3 : Solvabilité II simplifié

**Objectif.** Illustrer le calcul du SCR par chocs et réévaluation stochastique. **Ce n'est pas un calcul réglementaire complet.**

### Ce qui suit la formule standard (`src/solvabilite.py`)

| Élément | Règle appliquée | Référence |
| --- | --- | --- |
| Choc de taux | r + max(r × s_hausse(m), 1 point) ; r × (1 - s_baisse(m)) si r > 0, sinon pas de choc ; interpolation linéaire entre 20 et 90 ans | Règlement délégué (UE) 2015/35, art. 166 et 167, version applicable jusqu'au 29/01/2027 |
| Actions de type 1 | -39 %, ajustement symétrique pris nul | Art. 169 et 172 |
| Rachat | taux × 1,5 (plafond 100 %), taux × 0,5 (au plus -20 points), rachat massif de 40 % | Art. 142 |
| Choix du scénario | taux et rachat : celui qui donne la plus forte perte nette (calculée selon l'art. 206(2)) ; le brut est pris sur le même scénario | Art. 165(2) et 142(7) |
| Agrégation | corrélation taux / actions A = 0 si la hausse est retenue, 0,5 sinon ; marché / vie 0,25 | Art. 164 ; directive 2009/138/CE, annexe IV |
| Absorption par les provisions techniques | Adj = -max(min(BSCR - nBSCR, FDB), 0) | Art. 206(1) |
| Perte brute | perte à valeur des FDB inchangée, obtenue en ajoutant à la perte nette la baisse des FDB | Art. 83(1)(c) ; orientations EIOPA-BoS-14/177, orientation 2 (paragraphe 1.14) |
| Marge de risque | CoC × Σ f(t) × SCR(t) × P(0, t+1). Règles de 2026 (calcul retenu) : CoC = 6 %, f = 1. Sensibilité : CoC = 4,75 %, f(t) = max(0,96^t ; 50 %), seuls paramètres repris du régime révisé | Art. 37 et 39 ; règlement délégué (UE) 2026/269 (adopté le 29/10/2025, applicable au 30/01/2027) pour la sensibilité |

### Méthode

**Pertes sous choc.** Chaque choc relance la projection stochastique complète, sur les mêmes tirages que la base.
- **Perte nette** = fonds propres économiques de base - fonds propres choqués, où fonds propres économiques = VM de l'actif - BE. Sous choc, le modèle ajuste le taux servi et la PPB (actions de gestion).
- **Perte brute** = perte nette + (FDB de base - FDB choquées).
  - C'est la perte quand le choc ne change pas la valeur des FDB, comme le demande l'article 83(1)(c) pour le calcul brut. En effet, BE choqué brut = BE choqué - FDB choquées + FDB de base.
  - C'est aussi la méthode de l'orientation 2 des orientations EIOPA sur la capacité d'absorption des pertes : on recalcule les FDB sous le choc, et l'on ajoute leur écart au bilan de base au besoin net. L'orientation 2 ajoute cet écart au besoin net, c'est-à-dire à max(perte nette ; 0) ; le modèle l'ajoute à la perte nette. Les deux coïncident dès que la perte nette est positive, ce qui est le cas pour les trois scénarios retenus.
  - **Limite.** Les prestations garanties sous choc reprennent les sorties du calcul net, rachats dynamiques compris. Un calcul brut direct (orientation 1 : flux de FDB figés, seules les prestations garanties réactualisées) pourrait donner d'autres sorties. Ce calcul n'est pas réalisé, et l'écart entre les deux méthodes n'est pas mesuré.
  - **Portée.** Tant que le plafond n'est pas atteint, SCR = BSCR + Adj = nBSCR : le SCR ne dépend pas du calcul brut, qui ne sert qu'à vérifier le plafond.
- **Précision.** Les intervalles à 95 % des pertes sont calculés sur les écarts scénario par scénario (mêmes tirages) : écarts de BE pour la perte nette, écarts de BE - FDB pour la perte brute.

**Agrégation et SCR.**
- **SCR simplifié** = BSCR brut + Adj.
- **Fonds propres** = VM de l'actif - BE - marge de risque.

**Marge de risque.** Le SCR non couvrable retenu est le SCR de rachat après absorption, projeté au rythme d'écoulement de la PM moyenne.

**Sensibilité « paramètres de marge de risque 2027 ».** Elle remplace seulement le coût du capital et le facteur de décroissance par ceux du règlement délégué (UE) 2026/269. Les chocs (dont la nouvelle méthode de choc de taux), la courbe, les modules et le SCR restent ceux des règles de 2026. Ce n'est donc pas un calcul selon le régime applicable au 30/01/2027 : seule la marge de risque, et par suite les fonds propres, diffèrent du calcul retenu.

### Ce qui est exclu ou simplifié

- **Courbe** : plate à 3 %, sans la courbe EIOPA ni son extrapolation réglementaire.
- **Régime révisé** (règlement délégué (UE) 2026/269) : non implémenté. La nouvelle méthode de choc de taux et les autres changements ne sont pas modélisés ; seuls les paramètres de marge de risque font l'objet d'une sensibilité.
- **Modules absents** : spread, immobilier, change, mortalité, frais, catastrophe, risque opérationnel ; pas d'ajustement pour impôts différés.
- **Ajustement symétrique actions** : pris nul.
- **Contrats concernés par les chocs de rachat** : le modèle n'a qu'un seul model point, sans sélection contrat par contrat.
- **PPB** : elle reste entièrement dans le BE. Elle n'est pas reconnue en fonds excédentaires, ce que permettent l'arrêté du 24 décembre 2019 et la doctrine de l'ACPR.

Le rapport fonds propres / SCR simplifié **n'est donc pas un ratio de solvabilité réglementaire**.

**Tests :** `tests/test_solvabilite.py`. Tables de chocs, interpolation, agrégation, marge de risque ; assemblage du SCR sur des chiffres calculés à la main (choix des scénarios sur le net, brut pris sur le même scénario, corrélation A, plafond atteint ou non) ; cas analytique sans prestation discrétionnaire, où les FDB sont nulles et brut = net ; la sensibilité 2027 ne modifie que la marge de risque. Ces tests vérifient la cohérence interne du calcul : ce n'est pas une validation indépendante.

---

## V4 : le passif « à la Prophet »

**Objectif.** Montrer l'organisation d'un modèle actuariel de production :
- model points et tables d'hypothèses séparés des formules ;
- variables définies pour un t quelconque ;
- moteur qui résout les dépendances.

### Moteur (`src/prophet/moteur.py`)

- Chaque variable est une formule f(m, t), calculée sur tous les model points à la fois.
- Chaque valeur est mise en cache.
- Les dépendances sont enregistrées et publiées sous forme d'« arbre des variables ».
- Une dépendance circulaire à une même date est détectée, et la chaîne fautive est indiquée.

### Variables du passif (`src/prophet/epargne.py`)

Mêmes conventions qu'en V1. En plus :
- QX vient de la table de mortalité (âge en début d'année ; au-delà de 120 ans, qx = 1).
- Le rachat structurel dépend de l'ancienneté et du produit.
- Le nombre de contrats suit les mêmes sorties que la PM.
- Les frais comprennent une part en pourcentage de l'encours et un coût par contrat indexé sur l'inflation.
- Coût des TMG : (TMG - taux du fonds)⁺ × PM.
- Valeur actuelle des sorties, par récurrence vers l'arrière : VA(T) = PM(T) et VA(t) = [prestations(t+1) + frais(t+1) + VA(t+1)] / (1 + taux(t+1)).

### Tables (`src/prophet/tables.py`)

À la lecture, on vérifie que les clés sont des entiers contigus, sans valeur manquante et avec des probabilités dans [0, 1]. Au-delà de la dernière clé, on lit la dernière ligne.

### Portée de la validation

La V4 reproduit **le passif isolé** de la V1 : avec un model point et des tables plates, on obtient la même PM, les mêmes prestations et la même valeur actuelle des sorties, à 10⁻⁹ près. Le taux servi lui est imposé à partir d'une projection actif-passif déterministe (celle de la V1 dans le notebook), comme Prophet le recevrait de son module actif-passif (ALS). Il n'y a **pas de couplage** : les rachats du portefeuille de la V4 ne rétroagissent pas sur l'actif. Un couplage complet est une évolution possible, non réalisée.

**Tests :**
- `tests/test_modele.py` : reproduction de la V1, dépendance circulaire ;
- `tests/test_decrements.py` : non-négativité, conservation, âges extrêmes, tables invalides.
