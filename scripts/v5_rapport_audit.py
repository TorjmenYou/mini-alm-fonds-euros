"""Génère docs/V5_AUDIT_CONVENTIONS.md : audit des conventions de la V5 (participation aux résultats, données
de marché, impôt, précision des apports) et comparaison de la V5.0 publiée le 07/11/2026 à la V5.1.

Lit resultats/v5_0/ (résultats de la V5.0, conservés pour la comparaison), les résultats de la V5.1
(v5_consolidation.json, v5_collecte.json, v5_synthese_finale.json, v5_reconciliation_collecte.json),
v5_audit_conventions.json (scripts/v5_audit_conventions.py) et data/v5/marche/spread_hypothetique_20261031.json.
Les phrases sont écrites ici ; tous les chiffres et toutes les comparaisons viennent de ces fichiers.

Usage : python scripts/v5_rapport_audit.py [--sortie docs/V5_AUDIT_CONVENTIONS.md]
"""

import argparse
import json
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import strategies as stg  # noqa: E402
from src.v5.solvabilite_v5 import TAUX_IS, mcr_detail  # noqa: E402

N = "ABC"
COURT = {"passive": "Passive", "reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}

ap = argparse.ArgumentParser()
ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_AUDIT_CONVENTIONS.md"))
ARGS = ap.parse_args()


def lire(*chemin):
    return json.loads(RACINE.joinpath("resultats", *chemin).read_text(encoding="utf-8"))


K0, K1 = lire("v5_0", "v5_consolidation.json"), lire("v5_consolidation.json")
C0, C1 = lire("v5_0", "v5_collecte.json"), lire("v5_collecte.json")
F0, F1 = lire("v5_0", "v5_synthese_finale.json"), lire("v5_synthese_finale.json")
R0, R1 = lire("v5_0", "v5_reconciliation_collecte.json"), lire("v5_reconciliation_collecte.json")
AU = lire("v5_audit_conventions.json")
B1 = lire("v5_bilans_initiaux.json")["profils"]
SPREAD = json.loads((RACINE / "data" / "v5" / "marche" / "spread_hypothetique_20261031.json").read_text(encoding="utf-8"))
CODES = K1["strategies"]
PROFILS = json.loads((RACINE / "data" / "v5" / "profils" / "profils.json").read_text(encoding="utf-8"))
CHG = PROFILS["commun"]["passif"]["chargements_encours"]
FRAIS = json.loads((RACINE / "data" / "hypotheses.json").read_text(encoding="utf-8"))["passif"]["frais_gestion_encours"]
PART = PROFILS["commun"]["participation_technique"]["part_assureur"]
KAPPA = json.loads((RACINE / "data" / "v5" / "conventions" / "conventions.json").read_text(encoding="utf-8"))["conventions_credit"][K1["credit"]]["part_saut"]
AUTRES = [c for c in CODES if c != "passive"]
LECT = stg.charger()["lecture"]


def f(x, dec=1, signe=False):
    if round(x, dec) == 0:
        x = 0.0
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")
    return ("+" + s) if signe and x > 0 else s


def pct(x, dec=1, signe=False):
    return f(100 * x, dec, signe) + " %"


def sci(x):
    """Petit nombre en notation scientifique (contrôles numériques)."""
    if x == 0:
        return "0"
    e = math.floor(math.log10(abs(x)))
    exp = str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{f(x / 10 ** e, 1)} × 10{exp}"


def nb_changements(n):
    return "aucun changement de signe" if n == 0 else f"{n} changement{'s' if n > 1 else ''} de signe"


def ent(n):
    return f"{int(n):,}".replace(",", " ")


def pb(x, dec=0, signe=False):
    return f(1e4 * x, dec, signe) + " pb"


def ic(m, d, dec=1):
    return f"{f(m, dec, True)} ± {f(d, dec)}"


def minuscule(t):
    return t[:1].lower() + t[1:]


def rel(a, b):
    return pct((b - a) / abs(a), 1, True) if abs(a) > 1e-9 else "n. s."


L = []
A = L.append


def tableau(entetes, lignes, aligne=None):
    aligne = aligne or ["---"] + ["---:"] * (len(entetes) - 1)
    A("| " + " | ".join(entetes) + " |")
    A("| " + " | ".join(aligne) + " |")
    for ligne in lignes:
        A("| " + " | ".join(str(x) for x in ligne) + " |")
    A("")


# ------------------------------------------------------------------------------------------ données
def rn(K, p, c="passive", base="1.0"):
    return K["risque_neutre"][f"{p}|{c}|{base}"]


def besoin(K, p, c="passive", t="1.0"):
    return K["capital"][f"{p}|{c}"]["besoin"][t]


def couverture0(K, p, c="passive"):
    return K["prudentiel"][f"{p}|{c}"]["apport_0"]


def nb(C, p, c="passive", c0="0.06", eta="0.5"):
    return C["risque_neutre"][f"{p}|{c}|{c0}|{eta}"]


def existant(C, p, c="passive"):
    return C["risque_neutre"][f"{p}|{c}|0|0"]["valeur_existant"]["moyenne"]


PA = AU["participation"]
PS = AU["participation_strategies"]
seuil = F1["seuils"]
SP = SPREAD["spread_continu"]
PUB = SPREAD["donnees_publiees"]
CONV = json.loads((RACINE / "data" / "v5" / "conventions" / "conventions.json").read_text(encoding="utf-8"))
NIVEAU_REF = CONV["references_assures"]["_niveau_initial"]["valeur"]

# ------------------------------------------------------------------------------------------ document
A("# V5.1 : audit des conventions, données de marché et comparaison avec la V5.0")
A("")
A("> Document généré par `scripts/v5_rapport_audit.py` à partir de `resultats/v5_0/` (résultats de la V5.0 publiée le 07/11/2026, "
  "conservés pour la comparaison), des résultats de la V5.1 (`resultats/v5_consolidation.json`, `v5_collecte.json`, `v5_synthese_finale.json`, "
  "`v5_reconciliation_collecte.json`), de `resultats/v5_audit_conventions.json` et de `data/v5/marche/spread_hypothetique_20261031.json`. "
  "Montants en unités de 10 M€. Profils fictifs ; indicateurs Solvabilité II simplifiés, qui ne sont pas des ratios réglementaires.")
A("")
A("Un audit indépendant de la V5.0 a relevé deux questions actuarielles (participation aux résultats, impôt dans la projection) "
  "et des points de présentation (courbes de taux, précision des apports). La revue des données de marché a ajouté un point de conformité : "
  "la V5.0 utilisait des indices de taux de l'État dont la redistribution est soumise à autorisation. Ce document reprend chacun de ces points : "
  "textes ou conventions, vérification sur le code, mesure de l'effet, décision. La V5.1 change deux choses : la participation aux résultats "
  "(compte de participation avec sa composante technique) et le spread des obligations détenues (hypothèse construite à partir de paramètres "
  "publiés par l'EIOPA). Les V1 à V4 ne changent pas.")
A("")

# 1. Synthèse
ep = {p: PA[p]["v5_1"]["ecart_valeurs_nettes"] for p in N}
eimp = {p: AU["impot"][p]["impot_projete"]["ecart_valeurs_nettes"] for p in N}
verifs = {k: v["indicateur_couverture_scr"] for k, v in K1["verification"].items() if k.endswith("|1.0") and v["apport"] > 1e-9}
v0 = {p: rn(K0, p)["valeur_nette"] for p in N}
v1 = {p: rn(K1, p)["valeur_nette"] for p in N}
A("## 1. Synthèse")
A("")
tableau(["Point", "Constat initial", "Vérification", "Erreur ou limite", "Correction", "Effet économique"], [
    ("Participation aux résultats", "minimum de 85 % de la quote-part des produits financiers seulement",
     "articles A.132-11 à A.132-16 ; moteur, `src/strategie.py`", "**erreur confirmée** : composante technique du compte absente",
     "V5.1 : compte simplifié et plancher de la participation de l'exercice",
     "valeur, à capital et marché identiques : " + ", ".join(f"{p} {f(ep[p]['moyenne'], 1, True)}" for p in N) + " ; taux servi en hausse"),
    ("Données de marché", "spread des obligations calé sur des indices de taux de l'État (TEC), dates différentes de la courbe EIOPA",
     "conditions de réutilisation des sources", "**conformité** : redistribution des indices soumise à l'autorisation de leur administrateur",
     "V5.1 : spread hypothétique construit à partir des moyennes de long terme publiées par l'EIOPA ; plus aucune donnée d'indice",
     "niveaux de valeur et de capital modifiés (section 4) ; comparaisons de stratégies sur un même marché"),
    ("Impôt dans la projection", "impôt calculé après coup, non décaissé", "identités de flux, variante payée chaque année (tests)",
     "**convention**, sans double comptage ; dividendes de la projection avant impôt", "aucune : convention documentée, variante disponible",
     "valeur : " + ", ".join(f"{p} {f(eimp[p]['moyenne'], 2, True)}" for p in N)),
    ("Apports visant 100 %", "indicateur recalculé de 99,5 % à 101,6 % (V5.0)", "recalcul direct aux apports interpolés",
     "**limite** : interpolation linéaire", "formulation « apport estimé visant 100 % »",
     f"indicateur recalculé de {pct(min(verifs.values()))} à {pct(max(verifs.values()))} (V5.1)"),
], ["---"] * 6)
A("Valeur de l'existant recapitalisé à 100 %, gestion passive : " + ", ".join(f"{p} {f(v0[p])} en V5.0, {f(v1[p])} en V5.1" for p in N)
  + ". L'écart cumule les deux changements ; la section 4 sépare l'effet de la participation, mesuré à capital et marché identiques.")
A("")

# 2. Participation
A("## 2. Participation aux résultats")
A("")
A("### 2.1 Textes")
A("")
A("Code des assurances (Légifrance ; versions en vigueur au 07/11/2026, lues dans leur traduction publiée par french-business-law.com, "
  "Légifrance n'étant pas accessible depuis l'environnement de calcul) :")
A("")
A("- **A.132-11, I** : la participation minimale est déterminée globalement à partir d'un compte de participation aux résultats. Au crédit : "
  "les éléments techniques (solde de souscription, charges d'acquisition et de gestion nettes), 85 % du solde du compte financier, le solde de "
  "réassurance cédée. Au débit : la part de l'assureur dans les bénéfices techniques, égale au plus élevé de 10 % du solde créditeur des "
  "éléments techniques et de 4,5 % des primes des catégories 3 et 6, et, le cas échéant, le solde débiteur de l'exercice précédent.")
A("- **A.132-12** : le montant minimal de la participation de l'exercice est le solde créditeur de ce compte, diminué des intérêts crédités "
  "aux provisions mathématiques (et augmenté, contrat par contrat, d'un complément pour les contrats dont le taux garanti dépasse le taux moyen servi).")
A("- **A.132-13 et A.132-14** : solde financier et quote-part des produits afférente aux provisions techniques.")
A("- **A.132-16** : la participation mise en provision (PPB) est redistribuée dans les huit exercices suivants.")
A("- **A.344-2** : catégories de contrats ; 3 : contrats individuels d'assurance temporaire décès ; 6 : contrats collectifs en cas de décès. "
  "Les contrats d'épargne en euros modélisés relèvent des catégories 4 et 5 : le seuil de 4,5 % des primes ne s'applique pas.")
A("")
A("### 2.2 Composantes réglementaires et moteur")
A("")
tableau(["Composante", "Règle", "V5.0", "V5.1"], [
    ("Solde financier", "85 % de la quote-part des produits nets afférente aux provisions", "modélisé : 85 % x (PM + PPB) / actif comptable x produits positifs",
     "identique ; les plus-values actions réalisées entrent au compte de l'exercice"),
    ("Chargements prélevés", "éléments techniques, au crédit", "**absents du compte** : gardés en totalité par l'assureur", "au compte (sur encours et sur primes)"),
    ("Frais de gestion et d'acquisition", "éléments techniques, au débit", "absents du compte", "au compte"),
    ("Part de l'assureur", "plus élevé de 10 % du solde technique créditeur et de 4,5 % des primes des catégories 3 et 6", "100 % du solde technique",
     "10 % du solde créditeur ; solde débiteur en totalité au compte"),
    ("Résultat de mortalité", "solde de souscription", "absent : le décès verse la PM", "absent (simplification)"),
    ("Réassurance cédée", "au compte", "absente", "absente (simplification)"),
    ("Solde débiteur du compte", "reporté sur l'exercice suivant", "absent", "reporté ; un solde financier négatif n'est pas reporté (comme en V5.0)"),
    ("Intérêts techniques et garanties", "déduits du solde pour obtenir la participation", "taux servi et TMG dans les intérêts crédités ; le complément de TMG est payé par l'assureur",
     "idem, le complément de TMG compte dans la participation de l'exercice"),
    ("Plancher", "participation de l'exercice au moins égale au solde créditeur", "plancher financier seulement",
     "plancher sur intérêts crédités + dotation à la PPB - reprises de PPB"),
    ("PPB", "redistribution sous 8 ans", "modélisée par génération", "inchangée"),
    ("Complément contrat par contrat (A.132-12)", "contrats à taux garanti supérieur au taux moyen", "absent", "absent (un seul taux servi par ensemble de contrats)"),
], ["---"] * 4)
A(f"Les paramètres du modèle donnent un solde technique d'environ {pct(CHG - FRAIS, 2)} de la PM : chargements de {pct(CHG, 2)} (observés, moyenne de place) moins "
  f"frais de {pct(FRAIS, 2)} (fictifs, valeur des V1 à V4), dont l'assureur garde {pct(PART, 0)} quand le solde est créditeur. Ce solde n'est pas en lui-même un montant distribuable : il entre au compte, et le compte ne "
  "fixe qu'un minimum. Quand la participation que décide déjà la politique de taux servi (abandon de marge, complément de TMG, plus-values "
  "réalisées) dépasse le compte, la V5.1 ne change rien. Le complément ne joue que les années où la participation de l'exercice serait "
  "restée sous le compte : il sert d'abord le taux cible s'il n'est pas atteint, puis remplace des reprises volontaires de PPB, puis est doté à la PPB.")
A("")
A("### 2.3 Effet à capital et marché identiques (gestion passive, mêmes scénarios)")
A("")
A(f"Les deux conventions sont projetées avec les données de marché de la V5.1 et l'apport estimé de la V5.1 pour 100 % "
  f"({', '.join(f'{p} {f(AU['apports_v5_1'][p + '|passive'])}' for p in N)}), sur {ent(AU['n_scenarios'])} scénarios risque neutre ; écarts appariés "
  "scénario par scénario, avec leur intervalle à 95 % (incertitude Monte-Carlo de l'écart, distincte de l'incertitude de convention). "
  "« Convention V5.0 » : participation aux seuls produits financiers. Contrôle : la convention de la V5.1 reproduit les valeurs de "
  f"`resultats/v5_consolidation.json` (écart maximal {sci(AU['controles']['ecart_max_reproduction_v5_1'])}).")
A("")
lignes = []
for p in N:
    a, b = PA[p]["v5_0"], PA[p]["v5_1"]
    lignes.append((f"**{p}**", f(a["valeurs_nettes"]["moyenne"]), f(b["valeurs_nettes"]["moyenne"]),
                   ic(b["ecart_valeurs_nettes"]["moyenne"], b["ecart_valeurs_nettes"]["demi_intervalle_95"], 2),
                   rel(a["valeurs_nettes"]["moyenne"], b["valeurs_nettes"]["moyenne"]),
                   f(b["ecart_be"]["moyenne"], 1, True), f(b["ecart_fdb"]["moyenne"], 1, True),
                   pb(b["ecart_taux_servi_1_10"]["moyenne"], 1, True)))
tableau(["Profil", "Valeur nette, convention V5.0", "Valeur nette V5.1", "Écart", "Écart relatif", "BE", "FDB", "Taux servi, années 1 à 10"], lignes)
lignes = []
for p in N:
    a, b = PA[p]["v5_0"], PA[p]["v5_1"]
    lignes.append((f"**{p}**", f"{pct(a['dotation_ppb_pct_pm_1_10']['moyenne'], 2)} → {pct(b['dotation_ppb_pct_pm_1_10']['moyenne'], 2)}",
                   f"{pct(a['reprise_ppb_pct_pm_1_10']['moyenne'], 2)} → {pct(b['reprise_ppb_pct_pm_1_10']['moyenne'], 2)}",
                   f"{pct(a['ppb_pct_pm_10']['moyenne'], 2)} → {pct(b['ppb_pct_pm_10']['moyenne'], 2)}",
                   f"{f(a['abandon_marge_1_10']['moyenne'])} → {f(b['abandon_marge_1_10']['moyenne'])}",
                   pct(b["part_annees_avec_complement_1_10"]["moyenne"], 0), pct(b["complement_pct_pm_1_10"]["moyenne"], 3),
                   pct(b.get("part_scenarios_avec_solde_debiteur", 0.0), 1)))
tableau(["Profil", "Dotation PPB / PM (an, 1 à 10)", "Reprise PPB / PM", "PPB / PM, année 10", "Marge abandonnée, cumul 1 à 10",
         "Années avec complément", "Complément / PM (an)", "Scénarios avec solde débiteur"], lignes)
CD = AU["compte_debiteur"]
neg = max(x["part_annees_solde_technique_negatif_1_10"] for x in CD.values())
deb = max(x["part_annees_compte_debiteur_1_10"] for x in CD.values())
tmg_min = min(x["ecart_min_taux_servi_tmg_moyen"] for x in CD.values())
A(f"Solde technique débiteur : avec collecte (frais d'acquisition des contrats nouveaux au compte), sur les huit stratégies, les trois profils "
  f"et deux configurations (collecte centrale, collecte forte et élasticité forte), la part maximale d'années à solde technique négatif est de "
  f"{pct(neg, 1)} et celle des comptes débiteurs reportés de {pct(deb, 1)} ; le solde technique annuel le plus bas vaut "
  f"{pct(min(x['solde_technique_min_pct_pm'] for x in CD.values()), 3)} de la PM. "
  + ("Le cas débiteur ne se présente donc pas dans les configurations publiées ; il est vérifié par des tests dédiés (report du solde, "
     "participation minimale nulle, TMG respecté, reprise obligatoire de PPB faite). " if deb == 0 else
     "Les tests dédiés vérifient le report du solde, la participation minimale nulle, le TMG et la reprise obligatoire de PPB. ")
  + ("Le taux servi n'est jamais inférieur au TMG moyen du portefeuille : le plus petit écart vaut "
     f"{sci(abs(tmg_min)) if abs(tmg_min) > 0 else '0'} en valeur absolue (arrondi numérique), le plancher du TMG étant atteint certaines années."
     if tmg_min > -1e-12 else f"Écart minimal du taux servi au TMG moyen : {pb(tmg_min, 2, True)}."))
A("")
A("Lecture : la convention de la V5.0 laissait la participation de l'exercice sous le compte réglementaire simplifié dans une part importante "
  "des années ; le complément va surtout à la PPB et au taux servi, et réduit d'autant le résultat de l'assureur. L'effet est nettement "
  "supérieur à l'incertitude Monte-Carlo de l'écart : c'est un effet de convention, pas du bruit.")
A("")
A("### 2.4 Sensibilité au niveau des frais (paramètre fictif)")
A("")
lignes = [(f"{pct(FRAIS, 2)} (centre)", f(PA["B"]["v5_1"]["ecart_valeurs_nettes"]["moyenne"], 2, True), pb(PA["B"]["v5_1"]["ecart_taux_servi_1_10"]["moyenne"], 1, True))]
for fr, x in AU["frais"].items():
    lignes.append((pct(float(fr), 2), f(x["v5_1"]["ecart_valeurs_nettes"]["moyenne"], 2, True), pb(x["v5_1"]["ecart_taux_servi_1_10"]["moyenne"], 1, True)))
tableau(["Frais de gestion sur encours (profil B)", "Écart de valeur, V5.1 - convention V5.0", "Écart de taux servi"], lignes)
A(f"Plus les frais sont proches des chargements ({pct(CHG, 2)}), plus le solde technique et donc l'effet de la correction sont petits. Le niveau "
  f"central de {pct(FRAIS, 2)} n'est pas calibré : l'effet mesuré dépend de cette hypothèse, pas seulement de la règle.")
A("")
A("### 2.5 Stratégies : effet de la correction à capital constant")
A("")
A("Pour chaque stratégie, à son apport estimé de la V5.1 pour 100 % et avec les données de marché de la V5.1 : valeur nette sous les deux "
  "conventions (écart apparié sur les mêmes scénarios), puis écart à la gestion passive sous chaque convention.")
A("")
lignes = []
for p in N:
    for c in CODES:
        x = PS[f"{p}|{c}"]
        lignes.append((f"{p}, {COURT[c]}", f(x["apport_v5_1"]), f(x["valeur_convention_v5_0"]), f(x["valeur_v5_1"]),
                       ic(x["effet_capital_constant"]["moyenne"], x["effet_capital_constant"]["demi_intervalle_95"], 2),
                       rel(x["valeur_convention_v5_0"], x["valeur_v5_1"])))
tableau(["Profil, stratégie", "Apport pour 100 % (V5.1)", "Valeur nette, convention V5.0", "Valeur nette V5.1", "Effet de la correction", "Relatif"], lignes)
lignes = []
for p in N:
    for c in AUTRES:
        x = PS[f"{p}|{c}"]
        e0, e1 = x["ecart_passive_convention_v5_0"], x["ecart_passive_v5_1"]
        lignes.append((f"{p}, {COURT[c]}", ic(e0["moyenne"], e0["demi_intervalle_95"]), ic(e1["moyenne"], e1["demi_intervalle_95"])))
tableau(["Écart à la gestion passive (portefeuille fermé)", "Convention V5.0", "V5.1"], lignes)
signes_pb = sum(1 for p in N for c in AUTRES if (PS[f"{p}|{c}"]["ecart_passive_convention_v5_0"]["moyenne"] > 0) != (PS[f"{p}|{c}"]["ecart_passive_v5_1"]["moyenne"] > 0))
A(f"Signe de l'écart à la gestion passive : {nb_changements(signes_pb)} sur {len(N) * len(AUTRES)} couples profil-stratégie du fait de la seule correction.")
A("")

# 3. Données de marché
A("## 3. Données de marché")
A("")
A("### 3.1 Courbe sans risque EIOPA (observée)")
A("")
A("La courbe sans risque de l'EIOPA au 31/10/2026 (zéro-coupon, dérivée des swaps, ajustement pour risque de crédit déduit, extrapolée vers "
  "l'UFR) actualise les engagements ; la correction pour volatilité (VA) ne s'y ajoute que dans la vue prudentielle. Elle est reprise telle "
  "que publiée (archive contrôlée par son empreinte SHA-256). Les publications de l'EIOPA sont réutilisables avec mention de la source ; "
  "pour un contenu adapté, l'EIOPA demande en outre un avertissement, reproduit dans `data/v5/README.md` et dans la fiche du spread.")
A("")
A("### 3.2 Spread des obligations détenues (hypothèse)")
A("")
A("- **Point de départ.** La V5.0 calait le spread des obligations sur les TEC du 04/11/2026, indices de taux de l'État calculés et "
  "administrés par Euronext Paris, et une courbe zéro-coupon qui en était dérivée. Leur redistribution est soumise à une autorisation écrite "
  "préalable. Une transformation (conversion en zéro-coupon, écart à une autre courbe) ne lève pas cette condition : la V5.1 retire du dépôt "
  "les valeurs d'indice, les courbes dérivées et les figures qui permettaient de les reconstituer.")
A("- **Sources examinées.** Les courbes de rendement de la zone euro publiées par la BCE (et reprises par Eurostat) sont estimées à partir de "
  "prix fournis par un tiers (EuroMTS) ; la politique de réutilisation des statistiques du SEBC exclut les données de tiers sans autorisation "
  "et n'autorise pas de modification : elles ne sont pas retenues. L'EIOPA publie, dans la même archive mensuelle que la courbe sans risque, "
  "les moyennes de long terme des spreads (LTAS) par notation, réutilisables avec mention de la source : elles servent d'ancrage.")
A(f"- **Construction.** {SPREAD['justification']} Règle : {SPREAD['regle']}.")
A("- **Statut.** Les LTAS sont des paramètres publiés (observés) ; leur emploi comme spread courant, le choix de la notation et la moyenne "
  "des séries financières et non financières sont des hypothèses. Ce n'est pas un spread de marché observé au 31/10/2026 : en période de "
  "tension sur les spreads, le spread de marché serait plus élevé.")
A("")
mats = ("1", "2", "5", "10", "15", "20", "30")
tableau(["Maturité"] + [f"{m} an{'s' if m != '1' else ''}" for m in mats], [
    ["LTAS, obligations financières notées A (EIOPA)"] + [pct(PUB["EUR_Financials_2"][m], 2) for m in mats],
    ["LTAS, obligations non financières notées A (EIOPA)"] + [pct(PUB["EUR_Non-Financials_2"][m], 2) for m in mats],
    ["Spread hypothétique du modèle (continu)"] + [pb(SP[m]) for m in mats],
])
A(f"- **Usage dans le moteur.** Le spread sert à trois choses : (1) le prix de marché à l'ouverture des obligations détenues, qui "
  "représentent tout le portefeuille obligataire, souverains et entreprises (simplification) ; (2) en risque neutre, une intensité de perte "
  f"qui rend tout le spread coûteux (absence d'arbitrage) : une part kappa = {f(KAPPA, 1)} passe par des défauts de blocs d'émetteurs, le reste "
  "est une perte lissée ; (3) en probabilité réelle, seule une perte de défaut historique est constatée, l'écart étant une prime de risque. "
  "Le choc de spread de la vue prudentielle porte sur la part non souveraine. La part kappa est une hypothèse, testée de 0,55 à 1 ; ce n'est pas une estimation du risque de défaut des émetteurs, souverains ou entreprises : kappa répartit seulement le spread hypothétique entre une perte par défaut et une perte hors défaut.")
A(f"- **Autres paramètres liés.** Le niveau initial de la référence des assurés ({pct(NIVEAU_REF, 2)}) est une hypothèse, au milieu de la fourchette "
  "des taux servis attendus pour 2026 (2,8 % à 2,9 %, estimations de place) ; les coupons des générations d'obligations des profils fictifs "
  "sont des hypothèses d'ordre de grandeur, sans valeur d'indice reproduite.")
A("")
A("Valeur économique simplifiée = valeur de marché des actifs - BE ; fonds propres prudentiels simplifiés = actifs - BE - marge de risque + fonds excédentaires - impôts différés passifs (le SCR est une exigence de capital, pas un passif). Leur réaction à une variation des taux dépend des "
  "sensibilités respectives des obligations et des engagements, ces dernières dépendant elles-mêmes de la participation, des garanties et "
  "des rachats : ce point est mesuré par la vue prudentielle (chocs de taux), pas par le niveau des courbes.")
A("")
A("### 3.3 PPB et fonds excédentaires dans la vue prudentielle\n")
A("Toute la PPB est dans le BE (reprises créditées puis prestations, stock final, extinction). Une partie de la PPB d'ouverture est en outre admise "
  "en fonds excédentaires (FE) de niveau 1, selon la fiche technique de l'ACPR (calcul des fonds propres prudentiels au titre de la PPB) : "
  "montant admissible = stock d'ouverture moins la génération qui doit être restituée l'exercice suivant, soit un huitième du stock sous l'hypothèse "
  "de générations uniformes ; les deux autres exclusions de la fiche (participation déjà affectée mais non créditée, enveloppe de l'article A.132-3) "
  "sont supposées nulles, car le modèle n'a pas ces mécanismes (hypothèse, pas un fait vérifié). Valorisation par la méthode simplifiée de l'annexe 2 "
  "de la fiche : intégration aux PM au bout de huit ans, sortie au rythme des prestations de la projection centrale, actualisation sur la courbe EIOPA.\n")
A("**Reclassement.** Fonds propres de niveau 1 = actif − BE − marge de risque + FE − impôts différés passifs, ce qui équivaut à retirer FE du BE : "
  "le BE brut du moteur et le BE après reclassement sont donnés ci-dessous. **Absence de double comptage.** L'ajustement pour absorption par les provisions "
  "techniques vaut −max(min(BSCR brut − BSCR net, FDB − FE), 0) (article 206 du règlement délégué, FDB nets des fonds excédentaires, qui ne sont plus des "
  "provisions techniques : article 91 de la directive) ; le MCR utilise FDB − FE ; le SCR brut ne dépend pas de FE ; les impôts différés ne sont pas retraités. "
  "Quand le plafond FDB − FE mord, le reclassement déplace le même montant des fonds propres vers l'absorption reconnue : le surplus (fonds propres − SCR) "
  "est invariant et l'apport visant 100 % ne dépend pas du montant admis ; quand il ne mord pas, le SCR est invariant et les fonds propres montent de FE. "
  "Les indicateurs « PPB entière » ci-dessous sont re-agrégés sans scénario à partir des résultats stockés (même formule que le moteur ; contrôle : avec FE inchangé, "
  "la re-agrégation reproduit exactement les valeurs publiées). Gestion passive, sans apport, V5.1 :\n")


def reagreger_fe(x, fe):
    """Indicateurs prudentiels pour un autre montant de fonds excédentaires, à partir des agrégats stockés (formule de _agreger)."""
    net, brut, fdb, op = x["scr_net"]["bscr"], x["scr_brut"]["bscr"], x["fdb"], x["risque_operationnel"]
    actif_net = x["actif"] - x["be"] - x["marge_de_risque"]
    idp = max(TAUX_IS * (actif_net - x["fonds_propres_comptables"]), 0.0)
    adj_tp = -max(min(brut - net, fdb - fe), 0.0)
    adj_dt = -min(idp, TAUX_IS * max(brut + adj_tp + op, 0.0))
    scr = brut + adj_tp + op + adj_dt
    return {"tier1": actif_net + fe - idp, "scr": scr, "mcr": mcr_detail(scr, x["be"] - fdb, fdb - fe)["mcr"], "absorption_bornee": fdb - fe < brut - net}


def besoin_lineaire(of0, scr0, of1, scr1, k1, cible):
    pa, pb = (of1 - of0) / k1, (scr1 - scr0) / k1
    return max((cible * scr0 - of0) / (pa - cible * pb), 0.0)


lignes_fe, lignes_fe2, fe_txt = [], [], {}
for p in N:
    P1 = K1["prudentiel"][f"{p}|passive"]
    x0, x1, kk = P1["apport_0"], P1["apport_1"], P1["apport_1_montant"]
    for x in (x0, x1):
        r = reagreger_fe(x, x["fonds_excedentaires"])
        assert abs(r["scr"] - x["scr"]) < 1e-9 and abs(r["tier1"] - x["fonds_propres_niveau_1"]) < 1e-9 and abs(r["mcr"] - x["mcr"]) < 1e-9
    ppb0, adm = B1[p]["comptable"]["passif"]["ppb"], x0["ppb_admissible"]
    fe0, t1, scr = x0["fonds_excedentaires"], x0["fonds_propres_niveau_1"], x0["scr"]
    ratio = ppb0 / adm  # PPB entière admise
    r0, r1 = reagreger_fe(x0, ratio * fe0), reagreger_fe(x1, ratio * x1["fonds_excedentaires"])
    b_pub = K1["capital"][f"{p}|passive"]["besoin"]["1.0"]
    b_ent = besoin_lineaire(r0["tier1"], r0["scr"], r1["tier1"], r1["scr"], kk, 1.0)
    fe_txt[p] = {"b_pub": b_pub, "b_ent": b_ent, "cov": t1 / scr, "cov_ent": r0["tier1"] / r0["scr"], "cov_sans": (t1 - fe0) / scr, "bornee": r0["absorption_bornee"]}
    lignes_fe.append((f"**{p}**", f(ppb0), f(ppb0 - adm), f(adm), f(fe0), pct(fe0 / adm, 0), f(x0["be"]), f(x0["be"] - fe0)))
    lignes_fe2.append((f"**{p}**", f(t1), f(scr), pct(fe0 / t1, 0), pct(t1 / scr, 1), pct((t1 - fe0) / scr, 1), f(b_pub),
                       pct(r0["tier1"] / r0["scr"], 1), f(b_ent), "oui" if r0["absorption_bornee"] else "non"))
tableau(["Profil", "PPB comptable", "Exclusion : génération à échéance", "PPB admissible", "Fonds excédentaires (FE)", "FE / PPB admissible",
         "BE brut (moteur)", "BE après reclassement"], lignes_fe)
tableau(["Profil", "Fonds propres de niveau 1", "SCR simplifié", "FE / fonds propres", "Couverture", "Couverture sans FE", "Apport pour 100 %",
         "Couverture si la PPB entière était admise", "Apport pour 100 % si la PPB entière était admise", "Plafond FDB − FE actif"], lignes_fe2)
_a, _b, _c = fe_txt["A"], fe_txt["B"], fe_txt["C"]
A("Lecture. " + (f"Pour A, le plafond FDB − FE mord : admettre la PPB entière relèverait la couverture ({pct(_a['cov_ent'], 1)} contre {pct(_a['cov'], 1)}) sans changer l'apport visant 100 % "
  f"({f(_a['b_ent'])} contre {f(_a['b_pub'])}). " if _a["bornee"] else f"Pour A, admettre la PPB entière porterait l'apport visant 100 % de {f(_a['b_pub'])} à {f(_a['b_ent'])}. ")
  + f"Pour B, le SCR ne dépend pas de FE et l'apport visant 100 % serait de {f(_b['b_ent'])} au lieu de {f(_b['b_pub'])} avec la PPB entière. "
  + f"Pour C, la couverture sans apport est de {pct(_c['cov'], 1)} ({pct(_c['cov_ent'], 1)} avec la PPB entière, {pct(_c['cov_sans'], 1)} sans fonds excédentaires) : "
  + ("C couvre son SCR simplifié sans apport grâce aux fonds excédentaires. " if _c["cov"] >= 1 > _c["cov_sans"] else "")
  + "Approximation à garder en tête : exclusions (2) et (3) supposées nulles, montant de FE figé dans tous les chocs.")
A("")

# 4. Avant / après
A("## 4. Avant et après : V5.0 publiée et V5.1")
A("")
A("Chaque version avec son propre capital et ses propres données de marché. La colonne « dont participation » reprend l'effet de la "
  "correction mesuré à capital et marché identiques (section 2.3) ; le reste de l'écart vient des données de marché, de la convention des fonds excédentaires (V5.0 : PPB d'ouverture admise en totalité ; V5.1 : déduction de la génération restituée l'exercice suivant) et du recalibrage du capital.")
A("")
lignes = []
for p in N:
    lignes += [
        (f"**{p}** indicateur de couverture sans apport", pct(couverture0(K0, p)["indicateur_couverture_scr"], 1), pct(couverture0(K1, p)["indicateur_couverture_scr"], 1),
         pct(couverture0(K1, p)["indicateur_couverture_scr"] - couverture0(K0, p)["indicateur_couverture_scr"], 1, True).replace(" %", " pt"), "", ""),
        (f"{p} : SCR simplifié sans apport", f(couverture0(K0, p)["scr"]), f(couverture0(K1, p)["scr"]),
         f(couverture0(K1, p)["scr"] - couverture0(K0, p)["scr"], 1, True), rel(couverture0(K0, p)["scr"], couverture0(K1, p)["scr"]), ""),
        (f"{p} : fonds propres simplifiés sans apport", f(couverture0(K0, p)["fonds_propres_niveau_1"]), f(couverture0(K1, p)["fonds_propres_niveau_1"]),
         f(couverture0(K1, p)["fonds_propres_niveau_1"] - couverture0(K0, p)["fonds_propres_niveau_1"], 1, True),
         rel(couverture0(K0, p)["fonds_propres_niveau_1"], couverture0(K1, p)["fonds_propres_niveau_1"]), ""),
        (f"{p} : apport estimé pour 100 %", f(besoin(K0, p)), f(besoin(K1, p)), f(besoin(K1, p) - besoin(K0, p), 1, True), rel(besoin(K0, p), besoin(K1, p)), ""),
        (f"{p} : apport estimé pour 150 %", f(besoin(K0, p, t="1.5")), f(besoin(K1, p, t="1.5")), f(besoin(K1, p, t="1.5") - besoin(K0, p, t="1.5"), 1, True),
         rel(besoin(K0, p, t="1.5"), besoin(K1, p, t="1.5")), ""),
        (f"{p} : BE à 100 %", f(rn(K0, p)["be"]), f(rn(K1, p)["be"]), f(rn(K1, p)["be"] - rn(K0, p)["be"], 1, True), rel(rn(K0, p)["be"], rn(K1, p)["be"]),
         f(PA[p]["v5_1"]["ecart_be"]["moyenne"], 1, True)),
        (f"{p} : taux servi moyen, années 1 à 10 (risque neutre)", pct(rn(K0, p)["taux_servi_moyen_1_10"], 2), pct(rn(K1, p)["taux_servi_moyen_1_10"], 2),
         pb(rn(K1, p)["taux_servi_moyen_1_10"] - rn(K0, p)["taux_servi_moyen_1_10"], 0, True), "", pb(PA[p]["v5_1"]["ecart_taux_servi_1_10"]["moyenne"], 0, True)),
        (f"{p} : valeur de l'existant avant recapitalisation", f(rn(K0, p, base="0")["valeur_nette"]), f(rn(K1, p, base="0")["valeur_nette"]),
         f(rn(K1, p, base="0")["valeur_nette"] - rn(K0, p, base="0")["valeur_nette"], 1, True), rel(rn(K0, p, base="0")["valeur_nette"], rn(K1, p, base="0")["valeur_nette"]), ""),
        (f"{p} : valeur de l'existant recapitalisé à 100 %", f(v0[p]), f(v1[p]), f(v1[p] - v0[p], 1, True), rel(v0[p], v1[p]), f(ep[p]["moyenne"], 1, True)),
        (f"{p} : valeur des affaires nouvelles (c0 = 6 %, eta = 0,5)", f(nb(C0, p)["valeur_affaires_nouvelles"]["moyenne"]), f(nb(C1, p)["valeur_affaires_nouvelles"]["moyenne"]),
         f(nb(C1, p)["valeur_affaires_nouvelles"]["moyenne"] - nb(C0, p)["valeur_affaires_nouvelles"]["moyenne"], 1, True),
         rel(nb(C0, p)["valeur_affaires_nouvelles"]["moyenne"], nb(C1, p)["valeur_affaires_nouvelles"]["moyenne"]), ""),
        (f"{p} : marge des affaires nouvelles", pct(nb(C0, p)["marge_affaires_nouvelles"]), pct(nb(C1, p)["marge_affaires_nouvelles"]),
         pct(nb(C1, p)["marge_affaires_nouvelles"] - nb(C0, p)["marge_affaires_nouvelles"], 1, True).replace(" %", " pt"), "", ""),
        (f"{p} : seuil de coût du capital des affaires nouvelles", pct(R0["seuil_cout_capital"][p]["kappa_seuil"]), pct(R1["seuil_cout_capital"][p]["kappa_seuil"]),
         pct(R1["seuil_cout_capital"][p]["kappa_seuil"] - R0["seuil_cout_capital"][p]["kappa_seuil"], 2, True).replace(" %", " pt"), "", ""),
    ]
tableau(["Gestion passive", "V5.0", "V5.1", "Écart absolu", "Écart relatif", "dont participation"], lignes)


def d_prud(p, cle):
    a, b = couverture0(K0, p)[cle], couverture0(K1, p)[cle]
    return (b["bscr"] - a["bscr"]) if isinstance(a, dict) else (b - a)


A("Lecture du besoin de capital (gestion passive, sans apport) : variations de la V5.0 à la V5.1 des FDB (" +
  ", ".join(f"{p} {f(d_prud(p, 'fdb'), 1, True)}" for p in N) + "), de l'ajustement pour la capacité d'absorption des pertes des provisions "
  "techniques (" + ", ".join(f"{p} {f(d_prud(p, 'ajustement_tp'), 1, True)}" for p in N) + "), du BSCR (" +
  ", ".join(f"{p} {f(d_prud(p, 'scr_brut'), 1, True)}" for p in N) + "), des fonds propres (" +
  ", ".join(f"{p} {f(d_prud(p, 'fonds_propres_niveau_1'), 1, True)}" for p in N) + ") et du SCR (" +
  ", ".join(f"{p} {f(d_prud(p, 'scr'), 1, True)}" for p in N) + "). L'apport estimé pour 100 % résulte de ces deux derniers mouvements.")
A("")
grille = lambda C: [C["risque_neutre"][f"{p}|passive|{c0}|{eta}"]["valeur_affaires_nouvelles"]["moyenne"]  # noqa: E731
                    for p in N for c0 in C["intensites"].values() for eta in C["elasticites"].values()]
A(f"Valeur des affaires nouvelles sur toute la grille de collecte (gestion passive, trois profils) : de {f(min(grille(C0)))} à {f(max(grille(C0)))} "
  f"en V5.0, de {f(min(grille(C1)))} à {f(max(grille(C1)))} en V5.1. Avec la composante technique, les frais d'acquisition des contrats "
  "nouveaux entrent au compte de participation : quand le complément joue, les assurés en supportent une partie.")
A("")
A("### 4.1 Lectures de valeur totale (collecte et rachat)")
A("")
A("Capital porté à 100 % pour chaque stratégie et chaque version ; lecture de l'écart de valeur totale à la gestion passive sur les 20 "
  "configurations de collecte et de rachat (critères fixés à l'avance, `strategies.json`).")
A("")
lignes, changements = [], []
for p in N:
    for c in AUTRES:
        w0, w1 = F0["valeur_totale"][f"{p}|{c}"], F1["valeur_totale"][f"{p}|{c}"]
        d0 = besoin(K0, p, c) - besoin(K0, p)
        d1 = besoin(K1, p, c) - besoin(K1, p)
        meme = w0["verdict"] == w1["verdict"]
        if not meme:
            changements.append((p, c, w0["verdict"], w1["verdict"]))
        lignes.append((f"{p}, {COURT[c]}", f"{f(d0, 1, True)} / {f(d1, 1, True)}", f"{f(w0['min'])} à {f(w0['max'])}", f"{f(w1['min'])} à {f(w1['max'])}",
                       w0["verdict"], w1["verdict"] + ("" if meme else " **(changé)**")))
tableau(["Profil, stratégie", "Capital supplémentaire à l'ouverture, V5.0 / V5.1", "Valeur totale V5.0 (plage)",
         "Valeur totale V5.1 (plage)", "Lecture V5.0", "Lecture V5.1"], lignes)
if changements:
    A("Lectures modifiées : " + " ; ".join(f"{p}, {minuscule(COURT[c])} : « {a} » devient « {b} »" for p, c, a, b in changements) + ".")
else:
    A("Aucune lecture de valeur totale ne change de la V5.0 à la V5.1.")
A("")
signes = sum(1 for p in N for c in AUTRES if (K0["ecarts"][f"{p}|{c}|1.0"]["ecart_moyen"] > 0) != (K1["ecarts"][f"{p}|{c}|1.0"]["ecart_moyen"] > 0))
A(f"Signe de l'écart moyen sur le portefeuille fermé, de la V5.0 à la V5.1 : {nb_changements(signes)} sur {len(N) * len(AUTRES)} couples profil-stratégie.")
A("")

# 5. Fiscalité
A("## 5. Impôt sur les sociétés dans la projection")
A("")
A("### 5.1 Fonctions et identités")
A("")
tableau(["Fonction", "Rôle", "Constat"], [
    ("`projection.projeter`", "résultat avant impôt, fonds propres comptables, distribution", "le résultat avant impôt alimente les fonds propres ; la distribution porte sur l'excédent avant impôt"),
    ("`fiscalite.impot_annuel`", "25 %, contribution sociale, déficits reportables (art. 209)", "règles vérifiées par les tests de la V5"),
    ("`strategies.impots_par_scenario`, `resume_risque_neutre`, `collecte.projection_risque_neutre`", "impôt après coup, VA déduite de la valeur",
     "déduit une seule fois ; le BE ne contient pas d'impôt"),
    ("`strategies.resume_reel`", "rentabilité après impôt en probabilité réelle", "résultat net = résultat avant impôt - impôt, rapporté aux fonds propres d'ouverture avant impôt"),
    ("`solvabilite_v5`", "impôts différés à l'ouverture", "indépendants de la convention de calendrier (bilan d'ouverture)"),
], ["---"] * 3)
A("Convention de référence (inchangée en V5.1) : valeur nette = VA des dividendes avant impôt + VA du résidu final - apport initial - VA des "
  "apports ultérieurs - VA de l'impôt + fuite. Aucun impôt n'est compté deux fois : il est soustrait une fois de la valeur et n'apparaît ni "
  "dans le BE ni dans les flux de la projection. La limite est de présentation : les fonds propres et les dividendes de la projection sont "
  "avant impôt, et l'impôt ne réduit pas l'actif investi.")
A("")
A("Variante « impôt projeté » (`src/v5/variantes_audit.py`) : l'impôt de l'exercice est calculé dans la boucle (mêmes règles, déficits "
  "compris), déduit des fonds propres avant la distribution et payé par l'actif en fin d'exercice, à la date des prestations, donc avec le "
  "même déflateur que le calcul après coup ; la valeur déduit l'impôt payé, une fois. Tests (`tests/test_v5_audit_conventions.py`) : bilan "
  "équilibré chaque année et fuite nulle sur l'équivalent certain, impôt payé égal au calcul après coup sur les mêmes résultats, fonds "
  "propres(t) = fonds propres(t - 1) + résultat - impôt + apport - dividende déclaré, déficits reportables, sortie de trésorerie, identité de "
  "décomposition de la valeur.")
A("")
A("### 5.2 Effets (V5.1, gestion passive, apports de la V5.1, mêmes scénarios)")
A("")
lignes = []
for p in N:
    r, i = AU["impot"][p]["reference"], AU["impot"][p]["impot_projete"]
    rr, ri = AU["reel_impot"][p]["reference"], AU["reel_impot"][p]["impot_projete"]
    pr = AU["prudentiel_impot"][p]
    lignes.append((f"**{p}**", ic(i["ecart_valeurs_nettes"]["moyenne"], i["ecart_valeurs_nettes"]["demi_intervalle_95"], 2),
                   rel(r["valeurs_nettes"]["moyenne"], i["valeurs_nettes"]["moyenne"]), f(i["ecart_be"]["moyenne"], 2, True),
                   pb(i["ecart_taux_servi_1_10"]["moyenne"], 1, True), f"{f(r['va_dividendes']['moyenne'])} → {f(i['va_dividendes']['moyenne'])}",
                   f"{pct(rr['rendement_fonds_propres_1_10_agrege'], 2)} → {pct(ri['rendement_fonds_propres_1_10_agrege'], 2)}",
                   f"{pct(pr['reference']['indicateur_couverture_scr'], 1)} → {pct(pr['impot_projete']['indicateur_couverture_scr'], 1)}"))
tableau(["Profil", "Écart de valeur nette", "Relatif", "BE", "Taux servi", "VA des dividendes", "Rentabilité des fonds propres (réel)", "Indicateur à l'apport de la V5.1"], lignes)
ecarts_strat = [abs(x["ecart_passive_impot_projete"]["moyenne"] - x["ecart_passive_reference"]["moyenne"]) for x in AU["strategies_impot"].values()]
signes_impot = sum(1 for x in AU["strategies_impot"].values() if (x["ecart_passive_impot_projete"]["moyenne"] > 0) != (x["ecart_passive_reference"]["moyenne"] > 0))
A(f"Stratégies (portefeuille fermé, 100 %) : l'écart à la gestion passive change au plus de {f(max(ecarts_strat), 2)} unité avec l'impôt projeté ; "
  f"{nb_changements(signes_impot)} sur {len(ecarts_strat)}. Les dividendes de la variante sont après impôt, d'où leur baisse ; la valeur bouge peu, "
  "car le total des sorties (impôt et dividendes) est presque le même et que l'actif investi ne baisse que de l'impôt payé un an plus tôt.")
A("")
A("Décision : la convention après coup est conservée. Elle ne crée ni double comptage ni omission dans la valeur, et la variante n'en change "
  "aucune conclusion. Les documents précisent que les dividendes et fonds propres projetés sont avant impôt.")
A("")

# 6. Capital
A("## 6. Précision des apports visant 100 %")
A("")
A("Le besoin est interpolé linéairement entre deux calculs de la vue prudentielle (sans apport et avec un apport proche du besoin à 125 %), "
  "puis vérifié par un recalcul direct au besoin obtenu. Écart d'apport estimé : (1 - indicateur) x SCR / (pente des fonds propres - pente du "
  "SCR) ; effet sur la valeur : cet écart multiplié par le coût de la recapitalisation par unité d'apport du profil (passive).")
A("")
cout = {p: (rn(K1, p, base="1.0")["valeur_nette"] - rn(K1, p, base="0")["valeur_nette"]) / besoin(K1, p) for p in N if besoin(K1, p) > 1e-9}
lignes, deltas, sans_apport = [], [], []
for k, v in K1["verification"].items():
    p, c, t = k.split("|")
    cap = K1["capital"][f"{p}|{c}"]
    cible = float(t)
    vv0 = K0["verification"].get(k)
    if v["apport"] <= 1e-9 and v["indicateur_couverture_scr"] >= cible:
        sans_apport.append(f"{p}, {minuscule(COURT[c])} ({pct(v['indicateur_couverture_scr'], 1)})")
        lignes.append((f"{p}, {COURT[c]}, {pct(cible, 0)}", f(v["apport"]), pct(vv0["indicateur_couverture_scr"], 1) if vv0 else "",
                       pct(v["indicateur_couverture_scr"], 1), "sans objet", "sans objet"))
        continue
    delta = (cible * v["scr"] - v["fonds_propres_niveau_1"]) / (cap["pente_fonds_propres"] - cible * cap["pente_scr"])
    effet = delta * cout[p] if p in cout else 0.0
    deltas.append(abs(effet))
    lignes.append((f"{p}, {COURT[c]}, {pct(cible, 0)}", f(v["apport"]), pct(vv0["indicateur_couverture_scr"], 1) if vv0 else "",
                   pct(v["indicateur_couverture_scr"], 1), f(delta, 2, True), f(effet, 2, True)))
tableau(["Profil, stratégie, cible", "Apport V5.1", "Indicateur recalculé V5.0", "Indicateur recalculé V5.1", "Écart d'apport estimé", "Effet sur la valeur"], lignes)
if sans_apport:
    A("Sans apport, l'indicateur dépasse déjà la cible pour " + ", ".join(sans_apport) + " : l'apport estimé est nul et l'écart est sans objet.")
    A("")
A(f"Coût de la recapitalisation par unité d'apport (V5.1, passive) : {', '.join(f'{p} {f(cout[p], 3)}' for p in N if p in cout)}. L'effet sur la valeur ne dépasse pas "
  f"{f(max(deltas), 2)} unité, " + ("bien en deçà" if max(deltas) < 0.5 * min(seuil.values()) else "en deçà" if max(deltas) < min(seuil.values()) else "au-delà")
  + f" du seuil d'importance ({pct(LECT['valeur_nette_pct_scr'], 0)} du SCR, soit {', '.join(f'{f(seuil[p], 1)}' for p in N)}). Une recherche de racine "
  "coûterait plusieurs recalculs de la vue prudentielle par stratégie : la méthode est conservée et les apports sont présentés comme des "
  "**estimations visant 100 %**, pas comme des montants réglementaires exacts.")
A("")

# 7. Classement des conclusions
A("## 7. Nature des principales conclusions")
A("")
A("A : identité mathématique ou comptable vérifiée ; B : résultat de simulation correct sous les hypothèses du modèle ; C : conclusion "
  "économique robuste dans les configurations testées ; D : hypothèse fictive, approximation ou résultat non calibré.")
A("")
vt = F1["valeur_totale"]
robustes = [f"{p}, {minuscule(COURT[c])}" for p in N for c in AUTRES if vt[f"{p}|{c}"]["verdict"].endswith(", robuste") and "non robuste" not in vt[f"{p}|{c}"]["verdict"]]
favorables = [f"{p}, {minuscule(COURT[c])}" for p in N for c in AUTRES if vt[f"{p}|{c}"]["verdict"].startswith("favorable, robuste")]
signe_A = "négative" if existant(C1, "A") < 0 else "positive"
tableau(["Conclusion", "Nature", "V5.1"], [
    ("Bilan équilibré chaque année, fuite nulle sur l'équivalent certain, absence d'arbitrage, impôt compté une fois", "A", "vérifié par les tests"),
    ("Participation de l'exercice au moins égale au compte simplifié (V5.1)", "A", "vérifié par les tests"),
    (f"Le bilan hérité conditionne le capital nécessaire et la valeur (valeur de A recapitalisé {signe_A})", "B",
     f"A {f(existant(C1, 'A'))}, B {f(existant(C1, 'B'))}, C {f(existant(C1, 'C'))}"),
    ("Baisses de valeur totale robustes aux hypothèses testées", "C", " ; ".join(robustes) if robustes else "aucune"),
    ("Aucune stratégie n'apporte de gain de valeur robuste aux hypothèses testées", "C", "confirmé" if not favorables else "à revoir : " + ", ".join(favorables)),
    ("Politique de marge : lecture sur la grille", "C et D", "lecture : " + ", ".join(f"{p} « {vt[f'{p}|taux_servi_marge']['verdict']} »" for p in N)),
    ("Niveaux de valeur, de capital et de valeur des affaires nouvelles", "B et D", "dépendent des profils fictifs, du spread hypothétique, des frais fictifs et de l'élasticité"),
    ("Indicateurs de couverture du SCR", "D", "simplifiés, pas des ratios réglementaires"),
    ("Élasticité de la collecte, loi de rachat, référence des assurés", "D", "non calibrées ; grille et sensibilités"),
    ("Spread des obligations", "D", "hypothèse : moyenne de long terme publiée par l'EIOPA (notation A), pas un spread de marché observé"),
], ["---", "---", "---"])

# 8. Limites
A("## 8. Ce qui reste simplifié")
A("")
A("- Compte de participation : un seul canton, pas de résultat de mortalité ni de réassurance, solde financier négatif non reporté, pas de "
  "complément contrat par contrat ; frais de gestion fictifs, dont dépend l'ampleur de la composante technique.")
A("- Spread des obligations : hypothèse de spread de long terme, identique pour toutes les obligations (souverains et entreprises), figé, "
  "sans dynamique propre ni migration de notation ; part de crédit kappa supposée.")
A("- Impôt après coup : dividendes et fonds propres de la projection avant impôt (variante disponible, effet mesuré).")
A(f"- Apports estimés par interpolation : indicateur recalculé entre {pct(min(verifs.values()))} et {pct(max(verifs.values()))} pour une cible de 100 %.")
A("- Incertitude Monte-Carlo : intervalles par cellule, non simultanés ; incertitude de convention mesurée par les écarts de ce document, "
  "pas par ces intervalles.")
A("")

Path(ARGS.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit :", ARGS.sortie)
