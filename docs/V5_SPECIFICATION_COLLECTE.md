# V5 : spécification du modèle de collecte nouvelle

Ce document fixe le modèle simplifié de collecte nouvelle de la V5 : la collecte, la séparation des contrats existants et nouveaux dans un fonds mutualisé, les mesures de valeur, les interactions entre générations d'assurés et les contrôles d'absence d'arbitrage. Paramètres et statuts : `data/v5/collecte/collecte.json` ; méthodologie : [V5_METHODOLOGIE.md](V5_METHODOLOGIE.md), section 9 ; résultats : [V5_COLLECTE.md](V5_COLLECTE.md).

## 1. Pourquoi tester la collecte avant toute conclusion sur le taux servi

Sans collecte, le modèle projette un portefeuille fermé. Une baisse du taux servi n'y coûte que par les rachats dynamiques, bornés par la zone neutre et le plafond de la loi de rachat ; elle ne coûte rien en collecte. **Aucune politique de baisse du taux servi n'est qualifiée d'optimale sans que son avantage ait été testé avec une collecte sensible au taux servi relatif.** L'avantage mesuré en portefeuille fermé n'est pas, par principe, un majorant de l'avantage avec collecte : la section 6 donne les conditions sous lesquelles il l'est, et elles sont vérifiées numériquement.

## 2. Collecte

- **Collecte brute** de l'année t, pour t compris entre 1 et l'horizon de collecte H (10 ans, fictif), nulle ensuite : C(t) = c0 x PM(t - 1) x g(e(t - 1)). PM(t - 1) est la PM totale du fonds en début d'année ; e(t - 1) est l'écart entre le taux servi l'an dernier sur les contrats nouveaux et la référence des assurés de début d'année, le même écart que celui de la loi de rachat.
- **Réaction** : g(e) = min(g_max ; max(g_min ; 1 + eta x (e - e0) / 1 point)), avec e0 = 0 (un assureur qui sert le taux du marché collecte c0 x PM), g_min = 0 (pas de collecte négative : les sorties passent par les rachats) et g_max = 2. Une zone neutre de largeur réglable autour de e0 est disponible, nulle par défaut.
- **Deux cas limites distincts**, chacun couvert par un test de non-régression indépendant :
  1. **c0 = 0** : portefeuille fermé, aucune collecte. La projection doit être identique, colonne par colonne, à celle du modèle sans collecte, quel que soit eta.
  2. **eta = 0 et c0 > 0** : collecte positive mais indépendante du taux servi relatif. C(t) = c0 x PM(t - 1) exactement, pour toutes les stratégies ; deux politiques de taux servi différentes ne diffèrent alors que par leur effet sur la PM.
- **Intensités** : c0 = 3 % (fictif, faible) ; 6 % (dérivé d'agrégats observés d'une seule année : collecte nette 2025 des supports en euros d'environ +0,7 % de l'encours, ajoutée aux sorties du modèle d'environ 5,3 % par an) ; 10 % (borne haute : collecte brute 2025 rapportée à l'encours, environ 116,9 / 1 178 Md€ ; les sorties de la place dépassent celles du modèle, si bien qu'avec g = 1 ce niveau donnerait une collecte nette d'environ +4,6 % de la PM par an, contre +0,7 % observés). c0 = 6 % redonne la collecte nette observée, pas les flux bruts de la place ni la croissance de sa PM (réconciliation : `docs/V5_COLLECTE.md`, section 1). Ces ordres de grandeur ne calibrent aucun profil.
- **Élasticité** : eta = 0 ; 0,5 (1 point de taux servi en moins réduit la collecte de moitié) ; 0,75 ; 1,0 ; 1,5. Valeurs fictives : aucune donnée vérifiée ne mesure l'élasticité de la collecte au taux servi relatif. eta n'est jamais réglé pour obtenir un classement ; la grille est densifiée entre 0,5 et 1,5, où se trouve le cas le moins favorable.

## 3. Cohortes séparées, fonds mutualisé

- **Deux ensembles de contrats suivis séparément** : l'existant (TMG du profil) et les affaires nouvelles (toutes les générations de 1 à H, agrégées, car elles ont les mêmes caractéristiques). Pour chacun : PM, décès, rachats, frais, intérêts crédités, PM et part de PPB et de plus-values latentes revenant aux assurés à l'horizon.
- **Contrats nouveaux** (hypothèses fictives) : TMG nul, mêmes chargements et frais sur encours que l'existant, même loi de rachat et même mortalité, chargement sur prime nul, frais d'acquisition de 1 % de la prime.
- **Primes** : encaissées en fin d'année, avec les prestations, puis investies selon l'allocation cible au prix du marché. Les frais d'acquisition et le chargement sur prime passent par le résultat de l'année.
- **Fonds mutualisé** : un seul actif, une seule PPB, une seule participation. Le taux servi de l'année est décidé sur la PM totale, avec un TMG moyen pondéré par les PM ; l'intérêt crédité est ensuite réparti de façon que chaque ensemble reçoive au moins son TMG : taux servi = max(x ; TMG de l'ensemble), x étant le même pour tous. Chaque ensemble rachète selon son propre taux servi passé.
- **Capital** : la politique de distribution maintient les fonds propres comptables à leur cible en % de la PM totale ; la croissance de la PM retient donc du capital, ce qui réduit les dividendes.

## 4. Mesures séparées

1. **BE de l'existant, vue prudentielle et besoin de capital à l'ouverture** : en extinction (c0 = 0), dans la frontière des contrats Solvabilité II. Ni primes futures, ni contrats futurs. La vue prudentielle ignore toute section de collecte (test dédié) ; c'est une convention simplifiée, qui ne reprend pas les effets de la collecte sur les hypothèses de projection de l'existant. Les contrats existants du modèle n'ont pas de versements futurs : cette simplification est signalée.
2. **Valeur des affaires nouvelles** (valeur de franchise, risque neutre, explicitement hors Solvabilité II), différence entre la valeur totale avec collecte et la valeur de l'existant en extinction, sur les mêmes scénarios. Elle se répartit, scénario par scénario (identité vraie par construction), entre trois termes ; seule leur somme s'interprète, car un transfert entre générations d'assurés déplace les deux premiers en sens inverse :
   - **flux des contrats nouveaux** = VA des primes - BE des contrats nouveaux (prestations, frais d'encours et d'acquisition, PM et part finales) : ce que ces contrats reçoivent dans le fonds mutualisé ;
   - **variation du BE de l'existant** = - (BE de l'existant avec collecte - BE de l'existant en extinction) : ce que l'actionnaire gagne ou perd sur l'existant du fait de la collecte ;
   - **impôt supplémentaire** = - (VA de l'impôt avec collecte - VA de l'impôt en extinction).
3. **Probabilité réelle** : collecte, PM, rendement des fonds propres, dividendes, apports, liquidité (moins-values réalisées, sorties nettes des primes), conditionnels aux hypothèses.

## 5. Interactions par l'actif mutualisé (transferts entre générations d'assurés)

- **Rendement comptable** : les primes sont placées aux taux du moment. Si ces taux dépassent le rendement comptable du portefeuille, la collecte relève le taux servi de l'existant (variation du BE de l'existant défavorable à l'actionnaire, favorable aux assurés existants) ; sinon elle le dilue.
- **PPB** : la PPB d'ouverture appartient au fonds ; les contrats nouveaux en reçoivent une part par le taux servi commun.
- **Quote-part des provisions** : la participation porte sur une assiette qui grossit avec la PM.
- **Liquidité** : les primes financent une partie des sorties, ce qui réduit les ventes forcées et les moins-values réalisées.
- **TMG** : le plancher porte sur la somme des garanties ; quand le taux commun passe sous le TMG de l'existant, l'existant reçoit son TMG et les contrats nouveaux, de TMG nul, le reste : ils financent alors une partie de la garantie de l'existant. Ce transfert apparaît dans les deux premiers termes de la décomposition, en sens inverse.

## 6. Absence d'arbitrage et conditions d'un majorant

- **Contrôle de comptabilisation** (cas cantonné, test) : contrats nouveaux crédités au taux sans risque du scénario, sans chargement, frais, garantie ni option, sur un compte monétaire séparé. Leur valeur est nulle par construction ; le test contrôle la comptabilisation des primes, des prestations et de l'actualisation, scénario par scénario, sans exercer le fonds mutualisé.
- **Contrat sans marge explicite dans le fonds mutualisé** (test ; identifiant `contrat_equitable` dans les résultats) : sans chargement, frais, TMG ni PPB, participation de 100 %, équivalent certain : la valeur des affaires nouvelles doit rester inférieure à 1 % de la VA des primes, contre plus de 5 % pour les contrats réalistes ; le résidu vient des conventions de partage et de liquidation, que des variantes identifient.
- **Actif mutualisé** (test) : sur l'équivalent certain, les primes investies au prix du marché ne créent ni ne détruisent de valeur (fuite nulle à 1e-8 près).
- **Contrats réalistes** : leur valeur à l'ouverture peut être positive ou négative (marges, frais d'acquisition, coût du TMG et de l'asymétrie de la participation, interactions). Elle est mesurée, pas contrainte.
- **Majorant** : l'avantage de valeur d'une stratégie sur la gestion passive en portefeuille fermé majore son avantage avec collecte si et seulement si l'écart de valeur des affaires nouvelles entre la stratégie et la gestion passive est négatif ou nul ; il est lu comme « oui », « non » ou « indéterminé » selon son intervalle apparié. Ce n'est pas le cas si eta est nul (la stratégie de marge gagne aussi sa marge sur les contrats nouveaux) ; aux élasticités plus fortes, le résultat n'est pas monotone, car la gestion passive, qui sert elle-même sous la référence, perd aussi sa collecte. Il est vérifié pour chaque profil, intensité et élasticité.
- **Critère de lecture** : un écart de valeur totale n'est dit robuste que si la borne de son intervalle apparié à 95 % dépasse le seuil d'importance pour toutes les intensités, toutes les élasticités et la loi de rachat ONC maximale. Les hypothèses du modèle de collecte qui peuvent conduire la conclusion (e0, horizon de collecte, g_min) sont testées à part ou signalées.

## 7. Fichiers

Code : `src/v5/collecte.py` et la mécanique dans `src/projection.py` ; paramètres dans `data/v5/collecte/collecte.json`, tests `tests/test_v5_collecte.py`, résultats `resultats/v5_collecte.json` (`scripts/v5_collecte.py`), rapport `docs/V5_COLLECTE.md` et synthèse économique finale.
