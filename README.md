# Mini-modèle ALM fonds euros

[![Tests](https://github.com/TorjmenYou/mini-alm-fonds-euros/actions/workflows/tests.yml/badge.svg)](https://github.com/TorjmenYou/mini-alm-fonds-euros/actions/workflows/tests.yml)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

Un modèle actif-passif (ALM) simplifié d'un fonds euros d'assurance vie, écrit en Python. Il couvre la chaîne complète :
- projection du fonds ;
- valorisation des engagements envers les assurés (Best Estimate) ;
- coût des options et garanties (TVOG) ;
- bilan Solvabilité II simplifié ;
- réécriture du passif à la manière d'un outil de modélisation actuarielle comme Prophet.

Données et hypothèses fictives.

> **Usage.** Projet de démonstration, destiné à expliquer les mécanismes d'un modèle ALM. Ce n'est pas un outil de calcul prudentiel : le SCR et le rapport fonds propres / SCR calculés ici s'inspirent de la formule standard sans en être une application complète (voir [Limites](#limites)).

## Pourquoi ce modèle

Un fonds euros garantit le capital des assurés et leur reverse une partie des produits financiers de l'assureur. Pour piloter ce fonds, l'assureur doit répondre à trois questions :

| Question | Ce que le modèle calcule |
| --- | --- |
| Combien valent mes engagements envers les assurés, dans tous les scénarios de marché ? | Best Estimate stochastique |
| Combien me coûtent les garanties et le droit de rachat des assurés ? | TVOG et sa décomposition |
| Combien de capital dois-je détenir face aux chocs de marché et de rachat ? | SCR simplifié et marge de risque |

Ces trois réponses dépendent de l'interaction entre l'actif (obligations, actions) et le passif (taux servi, participation aux bénéfices, rachats). C'est cette interaction que le modèle rend visible.

## Ce que montre ce projet

**Modélisation actuarielle**
- **Fonds euros et participation aux bénéfices.**
  - Taux servi, participation minimale, PPB suivie par génération avec reprise obligatoire à 8 ans, réserve de capitalisation.
  - Rachats structurels et dynamiques (loi proposée par l'ACPR en 2013), décès et rachats en risques concurrents.
- **Valorisation cohérente avec le marché.**
  - Générateur de scénarios économiques : taux de Hull-White à un facteur, calé sur la courbe initiale, et actions log-normales.
  - Déflateurs exacts au pas annuel, tirages antithétiques, tests de martingale et de fuite.
- **Solvabilité II, version simplifiée.**
  - Chocs de taux par maturité, choc actions, chocs de rachat.
  - Pertes nettes par projection stochastique sous choc ; pertes brutes reconstruites à partir de la variation des FDB ; capacité d'absorption des pertes des provisions techniques ; marge de risque.
- **Analyse.** Décomposition de la TVOG par mécanisme (valeurs de Shapley) et étude de convergence Monte-Carlo.

**Python et qualité logicielle**
- **Code.** Modulaire (passif, actif, stratégie, GSE, projection, Solvabilité II) ; NumPy et pandas.
- **Moteur de variables à la Prophet.** Formules indexées par t, ordre de calcul déduit des dépendances, détection des dépendances circulaires.
- **Contrôles.**
  - 145 tests automatisés (pytest) : invariants comptables, cas limites, valeurs calculées à la main, cohérence entre versions.
  - Intégration continue avec GitHub Actions.
- **Reproductibilité.** Graine fixe, dépendances figées, résultats publiés recalculés par script et vérifiés par un test de non-régression.

## Résultats principaux

PM initiale de 1 000, courbe plate à 3 %, projection sur 60 ans, 1 000 scénarios stochastiques. Les intervalles sont à 95 %.

| Indicateur | Valeur |
| --- | ---: |
| Valeur de marché de l'actif | 1 078,2 |
| Best Estimate stochastique | 987,4 ± 6,2 |
| dont prestations discrétionnaires futures (FDB) | 178,6 ± 2,0 |
| BE équivalent certain (scénario déterministe) | 966,7 |
| TVOG | 20,6 ± 6,2 (2,1 % du BE) |
| SCR simplifié (nBSCR) | 35,6 |
| Marge de risque (coût du capital de 6 %) | 8,5 |
| Fonds propres | 82,3 |
| **Fonds propres / SCR simplifié** | **231 %** |

Lecture des résultats :
- **Risques.** Le risque actions domine (26,4), devant le rachat massif (14,0) et la hausse des taux (12,9).
- **TVOG.** Elle vient surtout des rachats dynamiques : les assurés rachètent quand les taux montent, au moment où leur épargne vaut moins que sa valeur comptable.
- **Précision.** Avec 10 000 scénarios : BE = 988,2 ± 1,6 et TVOG = 21,5 ± 1,6.
- **Sensibilité 2027.** Avec les seuls paramètres de marge de risque applicables au 30/01/2027 (coût du capital de 4,75 %, facteur max(0,96^t ; 50 %)), la marge de risque passe à 5,1 et le rapport à 241 %. Ce n'est pas un calcul selon le régime révisé.

![Du SCR par risque au SCR simplifié](figures/scr.png)

## Les quatre versions

### V1 : projection déterministe

Chaque année, le modèle enchaîne six étapes :
1. **Rachats** : structurels et conjoncturels, selon l'écart entre le taux servi l'an passé et le taux à 10 ans.
2. **Revenus financiers** : coupons, dividendes, intérêts, remboursements.
3. **Taux servi.**
   - Planchers : participation minimale et reprise obligatoire de la PPB.
   - Si besoin, leviers dans l'ordre : reprise de PPB, plus-values actions, marge de l'assureur.
   - En cas d'excédent : dotation à la PPB, jusqu'à un plafond.
4. **Passif** : revalorisation de la PM, puis décès et rachats.
5. **Prestations et frais**, puis rééquilibrage de l'actif.
6. **Contrôle** : bilan comptable vérifié chaque année.

| Scénario | BE | Valeur pour l'assureur (actif - BE) |
| --- | ---: | ---: |
| Central | 966,7 | 111,5 |
| Taux +200 pb | 932,1 | 63,3 |
| Taux -100 pb | 981,0 | 143,4 |
| Actions -25 % | 953,7 | 94,5 |

![Quatre scénarios déterministes](figures/scenarios.png)

### V2 : Best Estimate stochastique et TVOG

- **Taux** : modèle de Hull-White à un facteur, calé sur la courbe initiale, simulé exactement au pas annuel.
- **Actions** : rendement log-normal en univers risque neutre.
- **Scénarios** : 1 000, en variables antithétiques.
- **Contrôles** : tests de martingale sur les zéro-coupons, une obligation revendue et les actions ; test de fuite (aucune valeur créée ni perdue).
- **Décomposition de la TVOG** : les 8 combinaisons de trois mécanismes, sur les mêmes tirages, puis les valeurs de Shapley.

| Mécanisme | Contribution à la TVOG |
| --- | ---: |
| Rachats dynamiques | +29,9 |
| Plancher de taux servi | +3,1 |
| Lissage par la PPB | -5,0 |
| Modèle sans ces trois mécanismes | -7,4 |
| **TVOG du modèle complet** | **20,6** |

![Convergence du BE](figures/convergence_be.png)

### V3 : bilan Solvabilité II simplifié

**Principe.**
- Chaque choc relance la projection stochastique complète sur les mêmes tirages : c'est le calcul net, où la stratégie de taux servi et de PPB s'adapte au choc.
- **La perte brute n'est pas projetée séparément.** Elle est reconstruite à partir de la perte nette et de la variation des FDB, sans projection brute indépendante.

**Chocs.**
- Taux : chocs relatifs par maturité (règlement délégué (UE) 2015/35, art. 166 et 167).
- Actions : -39 %.
- Rachats : ×1,5 ; ×0,5 ; rachat massif de 40 %.

**Pertes.**
- Perte nette = fonds propres économiques de base - fonds propres économiques après choc.
- Perte brute = perte nette + (FDB de base - FDB après choc). C'est la perte à valeur des FDB inchangée (art. 83(1)(c)), obtenue par la méthode de l'orientation 2 des orientations EIOPA sur la capacité d'absorption des pertes. Les prestations garanties sous choc reprennent les sorties du calcul net.
- Le scénario de taux et le scénario de rachat sont retenus sur la perte nette (art. 165(2) et 142(7)).

**Agrégation.**
- Corrélations de la formule standard.
- Ajustement de l'article 206 : Adj = -max(min(BSCR - nBSCR, FDB), 0).

| Choc | Perte nette | Perte brute | FDB après choc |
| --- | ---: | ---: | ---: |
| Taux à la hausse (retenu) | 12,9 ± 2,9 | 20,6 ± 3,0 | 171,0 |
| Taux à la baisse | 0,0 ± 3,8 | 10,0 ± 3,6 | 168,6 |
| Actions -39 % | 26,4 ± 0,6 | 66,7 ± 0,9 | 138,3 |
| Rachats ×1,5 | 10,1 ± 1,4 | 41,4 ± 1,6 | 147,3 |
| Rachats ×0,5 | -25,2 ± 2,3 | -88,5 ± 2,6 | 241,8 |
| Rachat massif 40 % (retenu) | 14,0 ± 2,2 | 71,0 ± 2,5 | 121,5 |

**Résultat.**
- BSCR brut : 111,4 ; nBSCR : 35,6 ; ajustement : -75,8.
- Le plafond des FDB (178,6) n'est pas atteint : le SCR simplifié est égal au nBSCR. Le calcul brut ne sert donc qu'à vérifier ce plafond.

### V4 : le passif « à la Prophet »

**Organisation.**
- Les model points et les tables d'hypothèses (mortalité, rachats par ancienneté, frais) sont séparés des formules, et contrôlés à la lecture.
- Chaque variable est une formule écrite pour une année t.
- Un petit moteur déduit l'ordre de calcul, produit l'arbre des variables et refuse les dépendances circulaires.

**Résultats.**
- Sur un jeu de tables qui reproduit le model point de la V1, la V4 retrouve son passif à 10⁻⁹ près.
- Sur six model points, elle fait apparaître le pic de rachats fiscal à 8 ans et le coût des taux minimums garantis quand les taux baissent.

![Tables d'hypothèses de la V4](figures/tables_v4.png)

## Limites

- **Périmètre Solvabilité II.**
  - Seuls les risques de taux, d'actions et de rachat sont modélisés.
  - Absents : spread, immobilier, change, mortalité, frais, catastrophe, risque opérationnel, impôts différés.
  - Pas de courbe EIOPA, et le régime révisé applicable au 30/01/2027 n'est pas implémenté.
- **Participation aux bénéfices.** Approchée par sa part financière ; le compte de participation réglementaire n'est pas reproduit.
- **GSE.** Un facteur de taux, volatilités constantes non calibrées sur des prix d'options, corrélation taux / actions nulle.
- **Perte brute.** Reconstruite à partir de la perte nette et de la variation des FDB, sans projection brute indépendante.
- **Modèle.**
  - Un seul model point en V1 à V3, courbe initiale plate, frais proportionnels à l'encours.
  - La V4 ne modélise que le passif.
- **Validation.** Les contrôles vérifient la cohérence interne du modèle ; aucune validation indépendante n'a été réalisée.

Le détail des corrections apportées pendant le développement, des contrôles et des limites est dans [docs/AMELIORATIONS_ET_LIMITES.md](docs/AMELIORATIONS_ET_LIMITES.md).

## Démarrage rapide

Python 3.13, dépendances figées dans `requirements.txt` :

```bash
pip install -r requirements.txt
python -m pytest                        # 145 tests, environ une minute
python -m pytest -m "not lent"          # sans les projections stochastiques complètes
python scripts/resultats_reference.py   # recalcule resultats/indicateurs.json
python scripts/convergence.py           # 1 000 à 10 000 scénarios, 5 à 6 minutes
jupyter notebook notebooks/
```

Les résultats sont reproductibles à graine fixée (`gse.graine` dans `data/hypotheses.json`). Les notebooks fonctionnent aussi dans Google Colab : ils clonent le dépôt s'ils ne le trouvent pas.

## Organisation du dépôt

| Dossier | Contenu |
| --- | --- |
| `src/` | Passif, actif, stratégie de taux servi et PPB, courbes, GSE, boucle de projection, BE stochastique et TVOG, Solvabilité II |
| `src/prophet/` | Moteur de variables, lecture des tables, bibliothèque du passif épargne (V4) |
| `data/` | Hypothèses (V1 à V3), model points et tables d'hypothèses (V4) |
| `tests/` | Tests automatisés |
| `scripts/` | Recalcul des résultats publiés, étude de convergence |
| `resultats/` | Indicateurs de référence et convergence |
| `notebooks/` | Un notebook par version, avec analyses et graphiques |
| `docs/` | [Méthodologie](docs/METHODOLOGIE.md) ; [améliorations, contrôles et limites](docs/AMELIORATIONS_ET_LIMITES.md) |

## Glossaire

| Terme | Définition |
| --- | --- |
| PM | Provision mathématique : l'épargne des assurés, en valeur comptable |
| PPB | Provision pour participation aux bénéfices : participation mise en réserve, à redistribuer sous 8 ans |
| BE | Best Estimate : valeur actuelle probable des flux futurs dus aux assurés, frais compris |
| TVOG | Valeur temps des options et garanties : écart entre le BE stochastique et le BE d'un scénario déterministe |
| FDB | Prestations discrétionnaires futures : part du BE qui correspond à la participation future |
| SCR | Capital de solvabilité requis ; nBSCR : SCR de base net de la capacité d'absorption des provisions techniques |

## Historique

Ce dépôt publie la version consolidée du modèle (novembre 2026). Le développement a commencé en septembre 2026. Les corrections apportées pendant la phase de vérification sont résumées dans [docs/AMELIORATIONS_ET_LIMITES.md](docs/AMELIORATIONS_ET_LIMITES.md). L'historique de travail détaillé est conservé dans un dépôt privé.

## Licence

Distribué sous licence MIT : voir [LICENSE](LICENSE).

## Auteur

Youssef Torjmen, ingénieur en mathématiques appliquées (actuariat) · [LinkedIn](https://www.linkedin.com/in/torjmen-youssef)
