"""Génère docs/V5_SYNTHESE_AVANT_OPTIMISATION.md depuis resultats/v5_synthese.json et
resultats/v5_calibration_credit.json. Les phrases sont écrites ici ; les chiffres viennent des fichiers."""

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import conventions as cv  # noqa: E402

S = json.loads((RACINE / "resultats" / "v5_synthese.json").read_text(encoding="utf-8"))
K = json.loads((RACINE / "resultats" / "v5_calibration_credit.json").read_text(encoding="utf-8"))
C = cv.charger()
N = "ABC"
Q, EC, RE, PR, AT = S["q"], S["ec"], S["reel"], S["prudentiel"], S["attribution"]
LIB = {p: n for p, n in zip(N, ("Assureur historique sous pression", "Assureur intermédiaire", "Assureur plus récemment investi"))}


def f(x, dec=1):
    if round(x, dec) == 0:
        x = 0.0  # pas de « −0 »
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def pb(x, dec=0):
    return f(1e4 * x, dec) + " pb"


def q(p, nom="centre"):
    return Q[f"{p}|{nom}"]


def ec(p, nom="centre"):
    return EC[f"{p}|{nom}"]


def tvog(p, nom="centre"):
    cle = nom if f"{p}|{nom}" in EC else "centre"
    return q(p, nom)["be"] - ec(p, cle)["be"]


def dv(p, nom):
    return q(p, nom)["valeur"] - q(p)["valeur"]


L = []
A = L.append
A("# V5 : synthèse avant l'optimisation des stratégies ALM\n")
A("Généré par `scripts/v5_rapport_synthese.py` depuis `resultats/v5_synthese.json` (`scripts/v5_synthese.py`) et "
  "`resultats/v5_calibration_credit.json` (`scripts/v5_calibration_credit.py`). Unités fictives : 1 unité = 10 M€, PM initiale de 1 000. "
  f"{f(S['n_scenarios'], 0)} scénarios, valorisation risque neutre au 31/10/2026, base sans VA sauf mention, valeurs avant impôt sauf dans la vue prudentielle. "
  "**Les trois profils sont fictifs** et ne sont pas ajustés pour être rentables ou solvables. Aucune stratégie n'est optimisée ici.\n")
A("Le PDF de l'ACPR n° 185 n'a pas pu être consulté : ses chiffres ne sont utilisés que lorsqu'ils sont repris par une source secondaire, et signalés comme tels.\n")

# ------------------------------------------------------------------------------------------------
A("## 1. Conventions centrales retenues pour la suite (provisoires)\n")
A("| Élément | Convention | Statut | Fragilité |\n| --- | --- | --- | --- |")
A("| Valorisation | Base sans VA ; la VA est une vue réglementaire | Choix de méthode | Faible |")
A(f"| Spread des obligations | Spread zéro-coupon OAT par bootstrap du TEC ({pb(K['tec_vers_zero']['10']['spread_bootstrap'])} à 10 ans, contre {pb(K['tec_vers_zero']['10']['spread_modele'])} avec le TEC pris comme zéro-coupon) | Calibré | Moyenne : interpolation entre six maturités observées, pas de TEC à 1 an |")
A(f"| Part de crédit du spread | kappa = {f(C['calibration_kappa']['central'], 2)} | Calibré sur le CDS et le quanto publié | **Forte** : quanto France à 5 ans non observé |")
A("| Forme des pertes risque neutre | 70 % par saut (recouvrement 40 %), 30 % hors défaut lissé | Hypothèse | Moyenne |")
A(f"| Structure de défaut | 50 blocs, copule gaussienne à un facteur, rho = {f(C['correlation_copule']['valeur'], 1)} ; bloc souverain de 26 % et bloc unique en stress | Hypothèse | **Forte** : la France est un émetteur unique pour 26 % des obligations |")
A("| Probabilité réelle | Probabilité de défaut de 0,061 % par an et par bloc, recouvrement 50 % | Calibré (défauts d'entreprises par notation) | Forte pour le souverain français de 2026 |")
A(f"| Référence des assurés | **Proxy comportemental fictif** : taux sans risque 10 ans lissé sur 7 ans, niveau initial {pct(cv.niveau_initial_central(), 2)} | Hypothèse | **Forte** ; confrontée à une référence composite à niveaux observés |")
A(f"| Rachat structurel | 4,4 % au sens de l'ACPR (paramètre du modèle {pct(cv.rachat_structurel_acpr(), 3)}) ; 5 % en sensibilité | Observé, converti | Moyenne : dénominateur ACPR imprécis, année de rachats bas |")
A("| Loi de rachat dynamique | Paramètres des V1 à V4, entre les corridors minimal et maximal de l'ONC 2013 | Hypothèse | Forte : non calée sur des données |")
A("")

# ------------------------------------------------------------------------------------------------
A("## 2. Calibration du risque souverain\n")
A("### 2.1 Du TEC aux taux zéro-coupon\n")
A("Le TEC est un rendement au pair. Le prendre comme taux zéro-coupon sous-estime le spread quand la courbe monte. Le bootstrap (coupons annuels, TEC interpolés entre les maturités observées) corrige l'écart :\n")
A("| Maturité | TEC | Zéro-coupon OAT | Spread, TEC comme zéro-coupon | Spread zéro-coupon | Écart |\n| ---: | ---: | ---: | ---: | ---: | ---: |")
for k, v in K["tec_vers_zero"].items():
    if k == "1":
        continue
    A(f"| {k} ans | {pct(v['tec'], 2)} | {pct(v['zero_bootstrap'], 2)} | {pb(v['spread_modele'])} | {pb(v['spread_bootstrap'])} | {f(v['ecart_pb'], 1)} pb |")
A("\nSous 2 ans, faute de TEC à 1 an, le spread est prolongé à plat. Les conventions de sécurisation (codes commençant par « k ») utilisent le spread zéro-coupon ; les premières variantes gardent l'ancien, pour rester reproductibles.\n")

A("### 2.2 Des spreads aux intensités de défaut\n")
A("Règles, pour une année t (de t - 1 à t) :\n")
A("- spread cumulé : H(t) = s(t) x t, avec s le spread zéro-coupon continu ;")
A("- coût risque neutre de l'année : dH(t) = H(t) - H(t - 1), soit le spread à terme d'un an ; il est partagé entre crédit (kappa x dH) et hors défaut ((1 - kappa) x dH) ;")
A("- probabilité risque neutre de défaut d'un bloc : p(t) = (1 - exp(-kappa x dH(t))) / (1 - R), si bien que 1 - p(t) x (1 - R) = exp(-kappa x dH(t)) : la perte moyenne reproduit exactement le prix de marché ;")
A("- facteur de nominal moyen de l'année : exp(-(1 - kappa) x dH(t)) x (1 - p(t) x (1 - R)) = exp(-dH(t)).\n")
lc = K["intensites"][f"kappa={C['calibration_kappa']['central']}|R=0.4"]
A(f"Convention centrale (kappa = {f(C['calibration_kappa']['central'], 1)}, R = 40 %) :\n")
A("| Année | Spread cumulé H | Coût de l'année dH | dont crédit | dont hors défaut | Probabilité de défaut de l'année | Probabilité cumulée |\n| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for t, v in lc.items():
    A(f"| {t} | {pb(v['H'])} | {pb(v['increment_total'])} | {pb(v['increment_credit'])} | {pb(v['increment_hors_defaut'])} | {pct(v['pd_annuelle'], 2)} | {pct(v['pd_cumulee'], 1)} |")
A("\nLe coût de l'année croît avec le temps parce que les spreads zéro-coupon montent avec la maturité : le spread à terme dépasse le spread comptant. C'est ce coût à terme, et non le spread affiché, que la valorisation risque neutre fait payer chaque année.\n")
c5 = K["cds"]
A("### 2.3 Contrôle avec le CDS à 5 ans\n")
A(f"Triangle du crédit : CDS ≈ intensité x (1 - R). Avec le CDS de {pb(c5['cds_5_ans'])} et R = 40 %, l'intensité vaut {pct(c5['intensite_triangle_R40'], 2)} par an, soit une probabilité cumulée de {pct(c5['pd_cumulee_5_ans_triangle'], 1)} sur 5 ans. "
  f"Le modèle donne {pct(c5['pd_cumulee_5_ans_modele_kappa_1'], 1)} si tout le spread est du crédit (kappa = 1) et {pct(c5['pd_cumulee_5_ans_modele_kappa_central'], 1)} avec kappa = {f(C['calibration_kappa']['central'], 1)}. "
  "Le premier chiffre recoupe le CDS : la structure du modèle (spread zéro-coupon, recouvrement en valeur de marché) est cohérente avec la cotation. L'écart restant tient à la convention de recouvrement, au type de rendement et aux dates.\n")
kc = C["calibration_kappa"]
A("### 2.4 Part de crédit kappa : maturité, type de rendement, devise\n")
A(f"- **Maturité** : seul le CDS à 5 ans est disponible ; il est comparé au spread zéro-coupon à 5 ans ({pb(kc['spread_5_ans_bootstrap'], 1)}). Au-delà, kappa est supposé constant (hypothèse).")
A("- **Type de rendement** : le CDS est une prime courante ; le spread du modèle est un spread zéro-coupon continu. À 5 ans, l'écart entre les deux reste de second ordre devant l'effet de devise.")
A(f"- **Devise** : le CDS France est coté en dollars. En cas de défaut, l'euro devrait se déprécier, si bien qu'un CDS en dollars vaut plus qu'un CDS en euros. Le quanto relatif publié vaut environ {pct(kc['d_france_1_an']['d'], 0)} pour la France à 1 an et jusqu'à {pct(kc['d_allemagne_5_ans']['d'], 0)} pour l'Allemagne à 5 ans (Augustin, Chernov et Song). "
  f"D'où kappa = (1 - d) x CDS / spread : {f(kc['d_france_1_an']['kappa'], 2)} avec d = 28 %, {f(kc['d_allemagne_5_ans']['kappa'], 2)} avec d = 44 %, {f(kc['sans_quanto']['kappa'], 2)} sans quanto. Valeur centrale 0,7 ; sensibilités 0,55 et 1.")
A("- **Dates** : CDS du 29/10, TEC du 04/11 ; le CDS est passé de 104 à 91 pb en une semaine, soit une incertitude d'environ ±0,1 sur kappa.\n")
A("### 2.5 Liquidité et prime de risque\n")
bd = K["bund"]
A(f"- **Composante hors défaut (30 % du spread)** : elle regroupe la liquidité relative, l'offre de titres et le risque de change non lié au défaut. Repère : le Bund à 10 ans (environ {pct(bd['bund_10_estime'], 2)}, TEC moins l'écart OAT-Bund) cote près de la courbe sans risque EIOPA ({pct(bd['eiopa_zc_10'], 2)}). Un émetteur presque sans risque de défaut ne porte donc pas de prime hors défaut notable au-dessus de cette courbe. La composante hors défaut de l'OAT est la part du spread que le CDS en euros n'explique pas, pas une mesure directe de liquidité. En valorisation, elle reste un coût risque neutre (absence d'arbitrage) ; en probabilité réelle, c'est une prime.")
cmp_ = K["risque_neutre_et_reel"]
A(f"- **Prime de risque de crédit** : c'est l'écart entre la perte risque neutre et la perte réelle. Les probabilités de « 3,3 % » et « 0,06 % » ne mesurent pas la même chose. La première ({pct(cmp_['pd_rn_annuelle_annee_10'], 2)} avec le spread zéro-coupon) est la probabilité d'un bloc **l'année 10**, tirée du spread **à terme**. Sa moyenne sur 10 ans vaut {pct(cmp_['pd_rn_moyenne_10_ans'], 2)} par an. "
  f"La seconde ({pct(cmp_['pd_reelle_annuelle'], 3)}) est un taux de défaut historique moyen d'entreprises notées comme le portefeuille de place (S&P, 1981-2024), et non une mesure propre au souverain français de 2026. "
  f"Sur une base comparable (moyennes annuelles sur 10 ans), le rapport vaut environ {f(cmp_['rapport_pd_moyennes'], 0)}, contre un rapport publié de {f(cmp_['rapport_publie_zone_euro'], 0)} pour les souverains de la zone euro. "
  "Il y a deux lectures. Soit le marché paie en 2026 une forte prime pour un risque de queue politique et budgétaire. Soit la probabilité réelle historique sous-estime le risque actuel. Le stress « rapport de 2 » en probabilité réelle couvre la seconde lecture.\n")
A("### 2.6 Intensité, recouvrement et blocs\n")
A("L'intensité ne dépend pas de la taille des blocs : chaque bloc a la même probabilité p(t). La perte moyenne de l'année est donc identique quelle que soit la structure. Seule la concentration change :\n")
A("| Structure | Blocs | Plus gros bloc | Perte si ce bloc fait défaut (R = 40 %) | Probabilité risque neutre de défaut de ce bloc sur 10 ans | Probabilité réelle |\n| --- | ---: | ---: | ---: | ---: | ---: |")
noms = {"granulaire_50": "50 blocs égaux", "souverain_et_granulaire_50": "Souverain 26 % + 50 blocs", "souverain_et_diversifie": "Souverain 26 % + 20 blocs", "un": "Bloc unique"}
for k, v in K["blocs"].items():
    A(f"| {noms[k]} | {v['nombre']} | {pct(v['poids_max'], 0)} | {pct(v['perte_du_plus_gros_bloc_R40'], 1)} des obligations | {pct(v['probabilite_rn_defaut_plus_gros_bloc_10_ans'], 1)} | {pct(v['probabilite_reelle_defaut_plus_gros_bloc_10_ans'], 2)} |")
A("\nLa copule gaussienne (rho = 0,2) garde la probabilité de chaque bloc mais regroupe les défauts dans les mêmes années. Le recouvrement joue en sens inverse de l'intensité : un recouvrement de 63 % au lieu de 40 % donne des défauts plus fréquents mais moins coûteux, pour la même perte moyenne.\n")

A("### 2.7 Valeur selon la structure de défaut et la part de crédit\n")
rows = [("Spread entièrement lissé", "credit_lisse"), ("50 blocs indépendants", "structure_granulaire_independant"), ("**50 blocs corrélés (centre)**", "centre"),
        ("Souverain 26 % + 50 blocs corrélés", "structure_souverain_granulaire_correle"), ("Souverain 26 % + 20 blocs (corrélé par bloc)", "structure_souverain_bloc"),
        ("Bloc unique", "structure_bloc_unique"), ("kappa = 0,55", "credit_kappa_55"), ("kappa = 1", "credit_kappa_100"), ("Recouvrement 63 %", "credit_recouvrement_63")]
A("| Convention | " + " | ".join(f"Valeur {p}" for p in N) + " | " + " | ".join(f"Apports {p}" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(6)) + " |")
for lib, nom in rows:
    A(f"| {lib} | " + " | ".join(f"{f(q(p, nom)['valeur'])} ± {f(q(p, nom)['ic_be'])}" for p in N) + " | " + " | ".join(pct(q(p, nom)['part_scenarios_avec_apport'], 0) for p in N) + " |")
A("")

A("### 2.8 D'où vient la baisse de valeur avec le défaut par saut\n")
A("Test d'attribution, mêmes tirages, spread lissé contre spread par saut (bloc souverain de 26 %), référence centrale :\n")
A("| Profil | Passif | Valeur, spread lissé | Valeur, saut | Écart | BE garanti, lissé | BE garanti, saut | FDB, lissé | FDB, saut |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
libc = {"C0": "Indépendant des actifs (taux servi = TMG, sans participation ni rachat dynamique)", "C1": "Participation et TMG, sans rachat dynamique", "C2": "Modèle complet"}
for p in "AB":
    for cfg in ("C0", "C1", "C2"):
        a, b = AT[f"{p}|{cfg}|k_lisse_bootstrap"], AT[f"{p}|{cfg}|k70_souverain_bloc"]
        A(f"| {p} | {libc[cfg]} | {f(a['valeur'])} | {f(b['valeur'])} | {f(b['valeur'] - a['valeur'])} | {f(a['be_garanti'])} | {f(b['be_garanti'])} | {f(a['fdb'])} | {f(b['fdb'])} |")
a0, b0 = AT["B|C0|k_lisse_bootstrap"], AT["B|C0|k70_souverain_bloc"]
A(f"\nQuand le passif ne dépend pas des actifs, la forme des pertes ne change rien à la valeur (écart de {f(b0['valeur'] - a0['valeur'], 2)} pour B, BE identiques scénario par scénario ; test `test_passif_independant_des_actifs_meme_be_quelle_que_soit_la_forme_des_pertes`). "
  "La comptabilisation des défauts ne crée donc ni ne détruit de valeur, ce que confirment aussi les fuites nulles. La baisse apparaît dès que la participation et le TMG entrent en jeu ("
  + ", ".join(f"{f(AT[f'{p}|C1|k70_souverain_bloc']['valeur'] - AT[f'{p}|C1|k_lisse_bootstrap']['valeur'])} pour {p}" for p in "AB")
  + ") ; dans le modèle complet, les rachats dynamiques la réduisent ("
  + ", ".join(f"{f(AT[f'{p}|C2|k70_souverain_bloc']['valeur'] - AT[f'{p}|C2|k_lisse_bootstrap']['valeur'])} pour {p}" for p in "AB")
  + "), parce qu'ils rendent déjà le passif très non linéaire en spread lissé. "
  "Le mécanisme est une asymétrie : les années sans défaut, l'excédent de produits est partagé à 85 % avec les assurés ; les années de défaut, la perte sous le TMG et la marge abandonnée restent à l'actionnaire. Concentrer les pertes transfère donc de la valeur de l'actionnaire vers les assurés.\n")

# ------------------------------------------------------------------------------------------------
A("## 3. Rachats et comportement des assurés\n")
r = C["rachats"]["taux_rachat_structurel_central"]
A("### 3.1 Taux structurel de 4,4 % et cohérence avec l'ACPR n° 179\n")
A("- **Définition ACPR** : rachats de l'année rapportés aux provisions de N-1, supports en euros rachetables, décès et arbitrages exclus (graphique 7 et notes). Le n° 179 ne précise ni la nature des provisions (PM ou provisions techniques), ni le périmètre exact des contrats non rachetables.")
A(f"- **Définition du modèle** : le taux s'applique aux PM revalorisées nettes des décès. Rachats / PM d'ouverture = taux x (1 + taux servi) x (1 - taux de décès). D'où le paramètre {pct(r['parametre_modele'], 3)} = 4,4 % / (1,0263 x 0,99), avec le taux servi moyen de 2025.")
A("- **Vérification** : rachats de l'année 1 rapportés à la PM d'ouverture, équivalent certain : " + ", ".join(f"{pct(ec(p)['rachats_sur_pm_ouverture_annee_1'], 2)} ({p})" for p in N) + " (le léger écart vient du taux servi de l'année 1 des profils, différent de 2,63 %).")
A("- **Pas de double comptage** : " + C["rachats"]["absence_de_double_comptage"] + " Dans les trois profils, la composante dynamique de l'année 1 est nulle : taux de rachat de l'année 1 = " + ", ".join(f"{pct(ec(p)['taux_rachat_annee_1'], 3)} ({p})" for p in N) + ".")
A("- **Réserve** : 2025 est une année de rachats bas (4,8 % en 2024). Le taux de 5 % reste en sensibilité.\n")
A("### 3.2 Probabilité réelle et risque neutre\n")
A("| | Valorisation (risque neutre) | Projection de plausibilité (probabilité réelle) |\n| --- | --- | --- |")
A("| Loi de comportement | Même loi (rachat structurel et dynamique) : c'est une hypothèse de comportement réel, appliquée telle quelle | Même loi |")
A("| Ce qui change | Les trajectoires de taux servi et de référence sont risque neutre : produits nets de tout le coût du spread, actions au taux sans risque | Produits nets de la seule perte réelle, prime actions, taux sans prime de terme |")
A("| Référence des assurés | Moteur risque neutre (taux sans risque) : un concurrent investi dans les mêmes titres gagne le taux sans risque en risque neutre | Même moteur, trajectoires réelles |")
A("| Prix du risque de comportement | Absent du BE ; il figure dans la marge de risque et le SCR de rachat | Sans objet |")
A("| Lecture des rachats | Pas une prévision | Ordre de grandeur à confronter aux 4,4 % observés |")
A("")
A("### 3.3 Référence des assurés : proxy fictif et référence composite observée\n")
comp = C["references_assures"]["composite_observe"]["composantes"]
A("Référence composite (niveaux observés, délais et coefficients paramétrés, **poids fictifs**) : " + " ; ".join(
    f"{k['nom']} ({pct(k['poids'], 0)} ; niveau {pct(k['niveau_initial'], 2)} ; transmission {'immédiate' if k['lissage'] == 1 else 'lissée sur ' + f(1 / k['lissage'], 0) + ' ans'} ; coefficient de réaction {f(k['beta'], 1)})" for k in comp)
  + f". Niveau initial : {pct(ec('A', 'reference_composite_observe')['reference_annee_1'], 3)}, sans calage sur 2,88 %.\n")
refs = [("Proxy lissé sur 3 ans", "reference_lisse_3"), ("Proxy lissé sur 5 ans", "reference_lisse_5"), ("**Proxy lissé sur 7 ans (centre)**", "centre"),
        ("Proxy lissé sur 10 ans", "reference_lisse_10"), ("Composite à niveaux observés", "reference_composite_observe"),
        ("Transmission immédiate (sans risque 10 ans)", "reference_sans_risque_immediate"), ("Référence figée", "reference_figee"),
        ("Réaction faible (corridor minimal ONC)", "reaction_onc_min"), ("Réaction forte (corridor maximal ONC)", "reaction_onc_max"),
        ("Rachat structurel 5 %", "rachat_structurel_5")]
A("| Référence ou loi | " + " | ".join(f"Valeur {p}" for p in N) + " | " + " | ".join(f"Rachat 1-10 {p}" for p in N) + " | " + " | ".join(f"Duration BE {p}" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(9)) + " |")
for lib, nom in refs:
    e = [EC.get(f"{p}|{nom}") for p in N]
    A(f"| {lib} | " + " | ".join(f"{f(q(p, nom)['valeur'])} ± {f(q(p, nom)['ic_be'])}" for p in N) + " | " + " | ".join(pct(q(p, nom)['taux_rachat_moyen_1_10']) for p in N)
      + " | " + " | ".join(f(x['duration_effective_be']) if x else "" for x in e) + " |")
A("")

# ------------------------------------------------------------------------------------------------
A("## 4. Synthèse par profil\n")
for p in N:
    c, e = q(p), ec(p)
    rc, rs = RE[f"{p}|central"], RE[f"{p}|stress_rapport_2"]
    pa, pv = PR[f"{p}|avec_va"], PR[f"{p}|sans_va"]
    A(f"### Profil {p} : {LIB[p]}\n")
    A("| Rubrique | Indicateur | Valeur |\n| --- | --- | ---: |")
    A(f"| Valeur actionnaire | Actif - BE stochastique (avant impôt) | {f(c['valeur'])} ± {f(c['ic_be'])} |")
    vs = [Q[f"{p}|{nom}"]["valeur"] for nom in S["sensibilites"] if nom not in ("spread_plus_100", "base_avec_va")]
    A(f"| | Fourchette selon les conventions testées (hors chocs et hors VA) | de {f(min(vs))} à {f(max(vs))} |")
    A(f"| | Équivalent certain | {f(e['valeur'])} |")
    A(f"| BE et TVOG | BE stochastique | {f(c['be'])} |")
    A(f"| | TVOG (BE stochastique - équivalent certain) | {f(tvog(p))} |")
    A(f"| | FDB | {f(c['fdb'])} |")
    A("| Rachats | Structurel (sens ACPR) | 4,4 % |")
    A(f"| | Année 1, risque neutre / réel (paramètre du modèle ; {pct(e['rachats_sur_pm_ouverture_annee_1'], 2)} au sens de l'ACPR) | {pct(c['taux_rachat_annee_1'], 2)} / {pct(rc['taux_rachat_annee_1_moyen'], 2)} |")
    A(f"| | Moyenne années 1 à 10, risque neutre / réel | {pct(c['taux_rachat_moyen_1_10'])} / {pct(rc['taux_rachat_moyen_1_10'])} |")
    A(f"| Liquidité | Sorties annuelles maximales sur 10 ans, q99 (risque neutre / réel) | {pct(c['sorties_max_1_10_q99'], 0)} / {pct(rc['sorties_max_1_10_q99'], 0)} |")
    A(f"| | Moins-values réalisées sur 10 ans, q99 (risque neutre / réel) | {f(c['moins_values_realisees_1_10_q99'])} / {f(rc['moins_values_realisees_1_10_q99'])} |")
    A(f"| Besoins de financement | Apports, risque neutre : part des scénarios, valeur actuelle moyenne, q99 | {pct(c['part_scenarios_avec_apport'], 0)} ; {f(c['va_apports_moyenne'])} ; {f(c['va_apports_q99'])} |")
    A(f"| | Apports, réel : probabilité sur 10 ans, sur l'horizon | {pct(rc['apports_10']['probabilite'], 1)} ; {pct(rc['apports_60']['probabilite'], 1)} |")
    A(f"| | Fonds propres comptables négatifs avant 10 ans, réel central / stress | {pct(rc['fonds_propres_negatifs_10'], 1)} / {pct(rs['fonds_propres_negatifs_10'], 1)} |")
    A(f"| Capital | SCR approché, base sans VA (capital économique approché) | {f(pv['scr'])} |")
    A(f"| | Fonds propres de niveau 1, base avec VA (dont fonds excédentaires) | {f(pa['fonds_propres_niveau_1'])} ({f(pa['fonds_excedentaires'])}) |")
    A(f"| | SCR approché / MCR approché, base avec VA | {f(pa['scr'])} / {f(pa['mcr'])} |")
    A(f"| | **Indicateur de couverture simplifié du SCR** (sans impôts différés actifs ; avec ; sans fonds excédentaires) | **{pct(pa['indicateur_couverture_scr'], 0)}** ; {pct(pa['indicateur_couverture_scr_avec_ida'], 0)} ; {pct(pa['indicateur_couverture_scr_sans_fe'], 0)} |")
    A(f"| | Indicateur de couverture simplifié du MCR | {pct(pa['indicateur_couverture_mcr'], 0)} |")
    A(f"| Sensibilités de la valeur | Spread +100 pb instantané | {f(dv(p, 'spread_plus_100'))} |")
    A(f"| | Défaut : bloc souverain de 26 % / bloc unique | {f(dv(p, 'structure_souverain_bloc'))} / {f(dv(p, 'structure_bloc_unique'))} |")
    A(f"| | Part de crédit 0,55 / 1 | {f(dv(p, 'credit_kappa_55'))} / {f(dv(p, 'credit_kappa_100'))} |")
    A(f"| | Référence : lissage 3 ans / 10 ans / composite observée / immédiate | {f(dv(p, 'reference_lisse_3'))} / {f(dv(p, 'reference_lisse_10'))} / {f(dv(p, 'reference_composite_observe'))} / {f(dv(p, 'reference_sans_risque_immediate'))} |")
    A(f"| | Réaction faible / forte (ONC) | {f(dv(p, 'reaction_onc_min'))} / {f(dv(p, 'reaction_onc_max'))} |")
    A(f"| | Rachat structurel 5 % ; base avec VA | {f(dv(p, 'rachat_structurel_5'))} ; {f(dv(p, 'base_avec_va'))} |")
    A("")

# ------------------------------------------------------------------------------------------------
A("## 5. Vue prudentielle complétée\n")
A("Fonds propres éligibles de niveau 1 = actif - BE - marge de risque + fonds excédentaires - impôts différés passifs. Les impôts différés actifs (niveau 3, plafonnés à 15 % du SCR) ne sont pas reconnus au centre, faute de démonstration de recouvrabilité (l'ACPR exige un horizon de profits futurs inférieur à 5 ans, justifié au-delà). "
  "Fonds excédentaires : approche simplifiée de l'ACPR, la PPB admissible entre en PM au bout de huit ans puis sort au rythme des prestations projetées. La PPB admissible est prise égale à la PPB comptable : les profils n'ont ni montants préaffectés ni dotations de plus de sept ans à redistribuer (paramètre fictif). "
  "SCR : taux, actions (39 %, ajustement symétrique nul), spread (part non souveraine de 66 %, ventilée par qualité de crédit selon la place), rachat (hausse, baisse, massif), mortalité (+15 %), frais (+10 %, sans inflation), opérationnel (0,45 % des provisions, plafonné à 30 % du BSCR) ; absorption par les FDB (hors fonds excédentaires) et par les impôts différés passifs. "
  "MCR : formule linéaire vie réduite aux contrats avec participation (3,7 % des prestations garanties - 5,2 % des FDB), entre 25 % et 45 % du SCR.\n")
A("| Profil | Base | Actif | BE | Marge de risque | Fonds excédentaires | Impôts différés passifs | Fonds propres niveau 1 | SCR | dont marché net | dont vie nette | Ajustement FDB | Ajustement impôts | Opérationnel | MCR | Indicateur SCR | Indicateur MCR |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for p in N:
    for base in ("sans_va", "avec_va"):
        x = PR[f"{p}|{base}"]
        A(f"| {p} | {'avec VA' if base == 'avec_va' else 'sans VA'} | {f(x['actif'])} | {f(x['be'])} | {f(x['marge_de_risque'])} | {f(x['fonds_excedentaires'])} | {f(x['impots_differes_passif'])} | {f(x['fonds_propres_niveau_1'])} | {f(x['scr'])} | {f(x['scr_net']['marche'])} | {f(x['scr_net']['vie'])} | {f(x['ajustement_tp'])} | {f(x['ajustement_impots_differes'])} | {f(x['risque_operationnel'])} | {f(x['mcr'])} | {pct(x['indicateur_couverture_scr'], 0)} | {pct(x['indicateur_couverture_mcr'], 0)} |")
A("")
A("**Pertes nettes par choc (base avec VA)**\n")
chocs = ("taux_hausse", "taux_baisse", "actions", "spread", "rachats_hausse", "rachats_baisse", "rachat_massif", "mortalite", "frais")
A("| Profil | " + " | ".join(c.replace("_", " ") for c in chocs) + " |\n| --- | " + " | ".join("---:" for _ in chocs) + " |")
for p in N:
    A(f"| {p} | " + " | ".join(f(PR[f'{p}|avec_va']['pertes_nettes'][c]) for c in chocs) + " |")
A("")
A("**Repères de place** : taux de couverture du SCR de 250 % pour l'ensemble des organismes et de 240 % pour les autres organismes vie et mixtes (hors bancassureurs) fin 2025 (ACPR n° 181), "
  "250 % et 239 % au 30/06/2026 (ACPR n° 185, chiffres repris par la presse), 221 % puis 219 % pour les bancassureurs. Ces ratios intègrent la VA et la mesure transitoire sur les provisions techniques, et reposent sur des modèles complets, souvent des modèles internes. "
  "L'indicateur simplifié ne prend pas la mesure transitoire et n'a pas été ajusté pour s'en approcher : l'écart est un résultat, pas un défaut de calibrage.\n")

# ------------------------------------------------------------------------------------------------
pa, ra, rs_ = PR["A|avec_va"], RE["A|central"], RE["A|stress_rapport_2"]
A("## 6. Profil A : besoins de capital risque neutre et recapitalisation réelle\n")
A(f"- **Risque neutre** (valorisation) : un apport dans {pct(q('A')['part_scenarios_avec_apport'], 0)} des scénarios, de valeur actuelle moyenne {f(q('A')['va_apports_moyenne'])} (q99 {f(q('A')['va_apports_q99'])}). Ce chiffre mesure le coût, pour l'actionnaire, de l'option de défaut de l'actif et des garanties ; ce n'est pas une probabilité de recapitalisation.")
A(f"- **Probabilité réelle** : apport (actif épuisé) avec une probabilité de {pct(ra['apports_10']['probabilite'], 1)} sur 10 ans et {pct(ra['apports_60']['probabilite'], 1)} sur l'horizon ; fonds propres comptables négatifs avant 10 ans dans {pct(ra['fonds_propres_negatifs_10'], 1)} des scénarios (seuil comptable de recapitalisation). "
  f"En stress (probabilités réelles égales à la moitié des probabilités risque neutre) : {pct(rs_['apports_10']['probabilite'], 1)} et {pct(rs_['apports_60']['probabilite'], 1)} d'apports, {pct(rs_['fonds_propres_negatifs_10'], 1)} de fonds propres négatifs avant 10 ans.")
A(f"- **Liquidité extrême** (réel, 10 ans) : sorties annuelles maximales de {pct(ra['sorties_max_1_10_q99'], 0)} au q99, moins-values réalisées de {f(ra['moins_values_realisees_1_10_q99'])} au q99 ; elles dépassent la réserve de capitalisation dans {pct(ra['part_mv_realisees_au_dela_rc'], 0)} des scénarios.")
for nom, lib in (("rachat_structurel_5", "rachat structurel de 5 %"), ("reference_sans_risque_immediate", "transmission immédiate des taux"), ("structure_souverain_bloc", "bloc souverain de 26 %")):
    x = RE[f"A|{nom}"]
    A(f"- Effet des conventions en probabilité réelle, {lib} : apports sur l'horizon {pct(x['apports_60']['probabilite'], 1)}, fonds propres négatifs avant 10 ans {pct(x['fonds_propres_negatifs_10'], 1)}, rachat moyen {pct(x['taux_rachat_moyen_1_10'])}.")
A(f"- **Vue prudentielle simplifiée** : indicateur de couverture du SCR de {pct(pa['indicateur_couverture_scr'], 0)} (avec impôts différés actifs reconnus : {pct(pa['indicateur_couverture_scr_avec_ida'], 0)} ; sans fonds excédentaires : {pct(pa['indicateur_couverture_scr_sans_fe'], 0)}) et du MCR de {pct(pa['indicateur_couverture_mcr'], 0)}.\n")
A("**Lecture.** Le profil A reste un cas de fragilité financière : sa valeur économique est faible et très sensible aux conventions, et il couvre mal son SCR approché. "
  "Mais l'indicateur prudentiel est simplifié (pas de mesure transitoire, pas de modèle interne, pas de reconnaissance d'impôts différés actifs, fonds excédentaires par l'approche simplifiée). Une couverture insuffisante ne vaut donc pas constat d'insolvabilité réglementaire. "
  "Elle signale qu'un tel assureur relèverait d'un plan de rétablissement si un calcul complet la confirmait. En probabilité réelle, il honore ses engagements dans la très grande majorité des scénarios : sa fragilité vient de l'absence de coussin, pas d'une défaillance attendue.\n")

# ------------------------------------------------------------------------------------------------
A("## 7. Hypothèses les plus fragiles\n")
fr = [("Référence des assurés", "proxy fictif ; écart entre lissages 3 et 10 ans : " + ", ".join(f"{f(q(p, 'reference_lisse_10')['valeur'] - q(p, 'reference_lisse_3')['valeur'])} ({p})" for p in N)),
      ("Loi de rachat dynamique", "écart entre corridors ONC minimal et maximal : " + ", ".join(f"{f(q(p, 'reaction_onc_min')['valeur'] - q(p, 'reaction_onc_max')['valeur'])} ({p})" for p in N)),
      ("Structure de défaut", "écart entre 50 blocs corrélés et bloc souverain de 26 % : " + ", ".join(f"{f(-dv(p, 'structure_souverain_bloc'))} ({p})" for p in N)
       + " ; avec le bloc unique : " + ", ".join(f"{f(-dv(p, 'structure_bloc_unique'))} ({p})" for p in N)),
      ("Spread", "élargissement instantané de 100 pb : " + ", ".join(f"{f(dv(p, 'spread_plus_100'))} ({p})" for p in N)),
      ("Part de crédit kappa", "écart entre 0,55 et 1 : " + ", ".join(f"{f(q(p, 'credit_kappa_55')['valeur'] - q(p, 'credit_kappa_100')['valeur'])} ({p})" for p in N)),
      ("Probabilité réelle de défaut souverain", "historique d'entreprises, rapport de 30 avec le risque neutre contre 2 publié"),
      ("Indicateur prudentiel", "sans mesure transitoire, ajustement symétrique nul, spread ventilé selon la place, fonds excédentaires simplifiés"),
      ("Données de place manquantes", "ACPR n° 185 (moins-values 2026, composition des fonds propres et du SCR), quartiles de rachat du n° 179")]
A("| Hypothèse | Pourquoi elle compte |\n| --- | --- |")
for a_, b_ in fr:
    A(f"| {a_} | {b_} |")
A("")
import argparse as _argparse  # noqa: E402
_ap = _argparse.ArgumentParser()
_ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_SYNTHESE_AVANT_OPTIMISATION.md"))
Path(_ap.parse_args().sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit : docs/V5_SYNTHESE_AVANT_OPTIMISATION.md")
