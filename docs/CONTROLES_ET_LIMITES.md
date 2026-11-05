# Contrôles, limites et corrections du modèle

Ce document s'adresse à un lecteur extérieur. Il présente trois choses :
- comment les résultats du modèle sont contrôlés ;
- ce que le modèle ne fait pas ;
- les corrections intégrées au modèle et leur effet sur les résultats.

Les équations et les conventions sont décrites dans [METHODOLOGIE.md](METHODOLOGIE.md).

## Contrôles en place

- **Tests automatisés.** 145 tests (pytest), lancés à chaque push par l'intégration continue.
- **Invariants comptables.** Chaque année : bilan équilibré, conservation des flux, pas de PM, de PPB ni d'actif négatifs, test de fuite nul (aucune valeur créée ni perdue).
- **GSE.**
  - Tests de martingale sur le zéro-coupon, l'obligation revendue au prix du modèle et les actions.
  - Calage du modèle de Hull-White vérifié sur une courbe plate et sur une courbe pentue.
- **Cohérence entre versions.**
  - Avec une volatilité quasi nulle, le BE stochastique retrouve celui de la V1.
  - La V4 reproduit le passif de la V1 à 10⁻⁹ près.
- **Valeurs calculées à la main.** Agrégation Solvabilité II, ajustement de l'article 206, extinction du portefeuille, rendements extrêmes.
- **Non-régression.**
  - Les chiffres publiés (`resultats/indicateurs.json`) sont recalculés par `scripts/resultats_reference.py`.
  - Un test vérifie qu'ils correspondent au code.
- **Convergence Monte-Carlo.** Étude de 1 000 à 10 000 scénarios (`resultats/convergence.csv`).

Ces contrôles vérifient la cohérence interne du modèle. **Ils ne remplacent pas une validation indépendante** (comparaison à un outil de place ou revue par un tiers), qui n'a pas été réalisée.

## Limites

| Domaine | Limite |
| --- | --- |
| Participation aux bénéfices | La participation minimale est approchée par 85 % de la quote-part financière afférente aux provisions. Le compte de participation des articles A132-11 à A132-14 du Code des assurances n'est pas reproduit (solde technique, prélèvement de l'assureur, report du solde débiteur). |
| Courbe | Courbe plate à 3 %, sans la courbe EIOPA ni son extrapolation. |
| GSE | Un facteur de taux. Volatilités constantes, non calibrées sur des prix d'options. Corrélation taux / actions nulle. Taux négatifs non bornés. |
| Modules Solvabilité II | Seuls les risques de taux, d'actions et de rachat sont modélisés. Absents : spread, immobilier, change, mortalité, frais, catastrophe, risque opérationnel, impôts différés. L'ajustement symétrique actions est pris nul. |
| Régime révisé (applicable au 30/01/2027) | Non implémenté, dont la nouvelle méthode de choc de taux. Seuls les paramètres de marge de risque (coût du capital de 4,75 %, facteur max(0,96^t ; 50 %)) font l'objet d'une sensibilité. |
| Perte brute | Déduite de la perte nette par la variation des FDB (orientation EIOPA 2). Les prestations garanties sous choc reprennent les sorties du calcul net : aucun calcul brut direct, à flux de FDB figés, n'est fait. Tant que le plafond de l'article 206 n'est pas atteint (marge de 102,8 ici), le SCR ne dépend pas de ce calcul. |
| PPB | Entièrement dans le BE, sans reconnaissance en fonds excédentaires. À l'extinction, sa liquidation suit une convention de modélisation : elle est versée aux derniers assurés. |
| Rachats | Un seul model point en V1 à V3, sans sélection des contrats concernés par le rachat massif. |
| Précision Monte-Carlo | Avec 1 000 scénarios, la TVOG n'est connue qu'à environ 30 % près (±6,2). Avec 10 000 scénarios : TVOG = 21,5 ± 1,6. |
| Fonds propres | Capitalisés sans distribution ; négatifs dans environ 1 % des scénarios stochastiques. Pas de provision pour dépréciation durable ni de PRE. |
| V4 | Passif seul, sans couplage avec l'actif. Table de mortalité fictive (Gompertz-Makeham). |

Le rapport fonds propres / SCR simplifié **n'est pas un ratio de solvabilité réglementaire**. Il sert à comparer des versions du modèle ou des stratégies entre elles.

## Corrections intégrées au modèle

Les vérifications du modèle ont mis au jour les anomalies ci-dessous, qui ont été corrigées. Pour chacune, un test reproduit le cas concerné et vérifie la correction.

| Domaine | Problème constaté | Correction | Contrôle |
| --- | --- | --- | --- |
| Décès et rachats | Rachats calculés sur toute la PM revalorisée : PM négative possible aux grands âges (V4) | Risques concurrents, les rachats portant sur les survivants : PM fin = PM revalorisée × (1 - q) × (1 - ρ) | Conservation des flux et non-négativité sur une grille de q et ρ, âges de 95 à 125 ans |
| Liquidité | Trésorerie négative sans signal quand l'actif était épuisé (emprunt implicite) | Apport explicite de l'assureur, enregistré en fonds propres et compté dans le test de fuite | Scénarios extrêmes : taux +700 pb et -500 pb, actions -90 %, rachat de 100 % |
| Extinction du portefeuille | PPB non versée, ou versée un an trop tard, quand tous les contrats sortent | PPB versée aux derniers assurés à la date de leurs dernières prestations ; un rachat partiel ne la fait pas sortir | Montants et dates attendus, calculés à la main |
| FDB | BE garanti calculé avec d'autres sorties que le BE | Projection garantie avec les mêmes décès et rachats ; FDB = BE des prestations - BE garanti | Identités du BE ; FDB nulles sans participation |
| Rendement des actions | Pour une perte de plus de 98 % sur un an, le dividende créait de la valeur | Dividende plafonné à la valeur totale de fin d'année ; un rendement inférieur à -100 % est refusé | Conservation de la valeur sur une grille de rendements ; valeur perdue exacte dans un krach |
| Chocs de taux | Choc parallèle de ±100 pb | Chocs relatifs par maturité (règlement délégué (UE) 2015/35, art. 166 et 167) | Valeurs des chocs par maturité, plancher, taux négatifs |
| SCR | SCR net seulement | SCR brut et net, ajustement de l'article 206 plafonné par les FDB, scénario retenu sur le net (art. 165(2) et 142(7)) | Agrégation et ajustement vérifiés sur des valeurs calculées à la main ; cas analytique sans FDB (brut = net) |
| Marge de risque | Coût du capital de la révision (4,75 %) appliqué avant sa date d'application | Coût du capital de 6 % (règles en vigueur en 2026) ; paramètres de 2027 présentés comme une sensibilité | Formule de l'article 37 testée |
| TVOG | Contributions mesurées en retirant un mécanisme à la fois | Plan factoriel complet (8 combinaisons) et valeurs de Shapley | La somme des contributions redonne la TVOG |

**Effet sur les principaux résultats** (1 000 scénarios) :

| Indicateur | Avant corrections | Après corrections |
| --- | ---: | ---: |
| BE équivalent certain | 967,0 | 966,7 |
| BE stochastique | 987,6 | 987,4 ± 6,2 |
| TVOG | 20,6 | 20,6 ± 6,2 |
| Marge de risque | 6,6 (coût du capital de 4,75 %) | 8,5 (6 %) |
| Fonds propres / SCR simplifié | 237 % (BSCR net seul) | 231 % |

Les FDB ont aussi changé de définition (275,3 → 178,6) : les deux valeurs ne sont pas comparables.
