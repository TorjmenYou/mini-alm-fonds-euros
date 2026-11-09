"""Génère docs/V5_SYNTHESE_FINALE.md : synthèse économique finale de la V5, par profil, depuis
resultats/v5_consolidation.json (portefeuille fermé) et resultats/v5_collecte.json (collecte nouvelle).
Les phrases sont écrites ici ; tous les chiffres et tous les jugements de robustesse viennent des
résultats, des seuils de lecture fixés à l'avance (data/v5/strategies/strategies.json, rubrique lecture)
et des critères de src/v5/collecte.py. Aucune stratégie n'est désignée optimale.

Usage : python scripts/v5_synthese_finale.py [--sortie docs/V5_SYNTHESE_FINALE.md]
"""

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import collecte as col, strategies as stg  # noqa: E402

N = "ABC"
COURT = {"passive": "Passive", "reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}
POLITIQUES = ("taux_servi_marge", "taux_servi_competitif", "taux_servi_competitif_preservant")
SENS_CONSO = ("reaction_onc_max", "reference_immediate", "defaut_bloc_souverain")
SENS_LIB = {"reaction_onc_max": "la loi de rachat ONC maximale", "reference_immediate": "la transmission immédiate des taux à la référence",
            "defaut_bloc_souverain": "le défaut corrélé par bloc souverain"}
POL = {"taux_servi_marge": "la politique de marge", "taux_servi_competitif": "la politique compétitive"}
COURT_SENS = {"e0_moins_50pb": "e0 = −0,5 point", "horizon_30": "collecte pendant 30 ans", "horizon_60": "collecte pendant 60 ans"}

ap = argparse.ArgumentParser()
ap.add_argument("--collecte", default=str(RACINE / "resultats" / "v5_collecte.json"))
ap.add_argument("--consolidation", default=str(RACINE / "resultats" / "v5_consolidation.json"))
ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_SYNTHESE_FINALE.md"))
ap.add_argument("--json", default=str(RACINE / "resultats" / "v5_synthese_finale.json"))
ARGS = ap.parse_args()
R = json.loads(Path(ARGS.collecte).read_text(encoding="utf-8"))
K = json.loads(Path(ARGS.consolidation).read_text(encoding="utf-8"))
REC = json.loads((RACINE / "resultats" / "v5_reconciliation_collecte.json").read_text(encoding="utf-8"))
SC = REC["seuil_cout_capital"]
D = stg.charger()
P = col.charger()
LECT = D["lecture"]
RE_EXIGE = D["rentabilite_reelle"]["rendement_exige"]["valeur"]
CODES = R["strategies"]
AUTRES = [c for c in CODES if c != "passive"]
INT, ELA = R["intensites"], R["elasticites"]
C0C, ETAM = INT["centrale"], ELA["moderee"]
GRILLE = [(c0, eta) for c0 in INT.values() for eta in ELA.values()]
SENS = [s for s in P["sensibilites"] if not s.startswith("_")]
GRILLE_S = [(c0, eta) for c0 in (INT["centrale"], INT["forte"]) for eta in (ELA["moderee"], ELA["soutenue"])]


def f(x, dec=1):
    if round(x, dec) == 0:
        x = 0.0
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def feta(eta):
    return f(eta, 2 if round(eta, 1) != eta else 1)


def minuscule(t):
    return t[:1].lower() + t[1:]


def k(*parts):
    return "|".join(str(x) for x in parts)


def scr(p):
    return K["prudentiel"][f"{p}|passive"]["apport_0"]["scr"]


def seuil(p):
    return LECT["valeur_nette_pct_scr"] * scr(p)


def rn(p, c, c0=0, eta=0):
    return R["risque_neutre"][k(p, c, c0, eta)]


def ec(p, c, c0, eta):
    return R["ecarts"][k(p, c, c0, eta)]


def re_(p, c, c0=0, eta=0):
    return R["reel"][k(p, c, c0, eta)]


def onc(p, c, eta):
    return R["sensibilite_onc_max"][k(p, c, C0C, eta)]


def besoin(p, c):
    return K["capital"][f"{p}|{c}"]["besoin"]["1.0"]


def ecarts_totaux(p, c):
    """Grille principale (trois intensités, cinq élasticités) et loi ONC maximale (intensité centrale)."""
    return [ec(p, c, c0, eta)["totale"] for c0, eta in GRILLE] + [onc(p, c, eta)["ecart_totale"] for eta in ELA.values()]


def ecarts_hypotheses(p, c):
    return [R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"] for s in SENS for c0, eta in GRILLE_S]


def robustesse(p, c):
    return col.robustesse(ecarts_totaux(p, c), seuil(p))


def plage(v):
    return f"de {f(min(x['moyenne'] for x in v))} à {f(max(x['moyenne'] for x in v))}"


def lectures(v, seuil_):
    """Lectures distinctes d'un ensemble d'écarts appariés : signe de l'effet mesuré, significativité
    (intervalle à 95 % excluant zéro), importance (significatif et moyenne au-delà du seuil) et borne de
    l'intervalle au-delà du seuil (condition de robustesse)."""
    n = len(v)
    pos = sum(x["moyenne"] > 0 for x in v)
    sig = sum(abs(x["moyenne"]) > x["demi_intervalle_95"] for x in v)
    imp_m = sum(abs(x["moyenne"]) > x["demi_intervalle_95"] and abs(x["moyenne"]) >= seuil_ for x in v)
    imp = sum(abs(x["moyenne"]) - x["demi_intervalle_95"] >= seuil_ for x in v)
    signe = "positif partout" if pos == n else ("négatif partout" if pos == 0 else f"positif dans {pos} sur {n}")
    return n, signe, sig, imp_m, imp


def contraires(v_cfg):
    """Écarts de signe contraire à la majorité, avec leur configuration : [(libellé, écart)]."""
    pos = sum(x["moyenne"] > 0 for _, x in v_cfg)
    maj = 1 if 2 * pos >= len(v_cfg) else -1
    return [(lib, x) for lib, x in v_cfg if x["moyenne"] * maj < 0]


def cellules(p, c):
    """Écarts de valeur totale sur la grille, sous ONC maximale et sous les hypothèses de collecte, étiquetés."""
    sortie = [(f"c0 {pct(c0, 0)}, eta {feta(eta)}", ec(p, c, c0, eta)["totale"]) for c0, eta in GRILLE]
    sortie += [(f"ONC maximale, eta {feta(eta)}", onc(p, c, eta)["ecart_totale"]) for eta in ELA.values()]
    if c in ("taux_servi_marge", "taux_servi_competitif"):  # hypothèses de collecte testées pour ces politiques
        sortie += [(f"{COURT_SENS[s]}, c0 {pct(c0, 0)}, eta {feta(eta)}", R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"]) for s in SENS for c0, eta in GRILLE_S]
    return sortie


def phrase_signe(couples):
    """Phrase sur le signe des écarts de politiques de taux servi, toutes configurations confondues."""
    nets, faibles = [], []
    for p, c in couples:
        verdict = col.robustesse([x for _, x in cellules(p, c)], seuil(p))
        if verdict == "change de signe selon les hypothèses":
            nets.append(f"{POL[c]} ({p})")
        elif "là où il est significatif" in verdict:
            faibles += [f"{POL[c]} pour {p}, {lib} : {f(x['moyenne'])} ± {f(x['demi_intervalle_95'])}" for lib, x in contraires(cellules(p, c))]
    phr = []
    if nets:
        phr.append("Le signe de l'écart change, avec des écarts significatifs de part et d'autre, pour " + ", ".join(nets) + " : le classement de portefeuille fermé n'y est pas une conclusion générale.")
    if faibles:
        if len(faibles) == 1:
            phr.append(f"Un seul écart de signe contraire apparaît, sans être significatif ({faibles[0]}) : il ne suffit pas à établir un changement de signe, mais l'avantage n'y est plus démontré.")
        else:
            phr.append("Des écarts de signe contraire apparaissent sans être significatifs (" + " ; ".join(faibles) + ") : ils ne suffisent pas à établir un changement de signe, mais l'avantage n'y est plus démontré.")
    return " ".join(phr) if phr else "Le signe des écarts résiste à ces hypothèses ; leur ampleur, non."


def lecture_json(m, seuil_, sens, ns=False):
    """Même règle que qualif, sous forme structurée (pour les figures)."""
    lec = "neutre" if ns or abs(m) < seuil_ else ("favorable" if m * sens > 0 else "défavorable")
    return {"lecture": lec, "ecart": m, "non_significatif": bool(ns)}


def qualif(m, seuil_, sens, fmt, ns=False):
    if ns or abs(m) < seuil_:
        return f"neutre ({fmt(m)}{', ns' if ns else ''})"
    return ("favorable" if m * sens > 0 else "défavorable") + f" ({fmt(m)})"


L = []
A = L.append
A("# V5 : synthèse économique finale\n")
A("Trois profils fictifs de fonds euros, huit stratégies ALM, deux vues : le portefeuille fermé (`docs/V5_STRATEGIES.md`, `docs/V5_SYNTHESE_STRATEGIES.md`) et la collecte nouvelle sensible au taux servi relatif (`docs/V5_COLLECTE.md`). "
  "Généré par `scripts/v5_synthese_finale.py` depuis `resultats/v5_consolidation.json`, `resultats/v5_collecte.json` et `resultats/v5_reconciliation_collecte.json`. Unités fictives : 1 unité = 10 M€.\n")
A("**Statut.** Étude exploratoire sur des profils fictifs, conditionnelle aux hypothèses ; ce n'est pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. "
  "Les probabilités de recapitalisation sont conditionnelles au modèle. Valeur risque neutre et rentabilité en probabilité réelle restent séparées. **Aucune stratégie n'est désignée optimale.**\n")
A(f"**Base commune et lecture.** Chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (vue prudentielle sur la base avec VA) ; sa valeur (risque neutre, base sans VA) est nette de cet apport. Un écart est significatif si son intervalle apparié à 95 % exclut zéro ; il est important s'il est significatif et dépasse {pct(LECT['valeur_nette_pct_scr'], 0)} du SCR simplifié du profil pour la valeur et l'apport "
  f"({', '.join(f'{f(seuil(p))} pour {p}' for p in N)}), {f(1e4 * LECT['rendement_fonds_propres_pt'], 0)} pb pour la rentabilité, {f(LECT['ecart_taux_servi_pb'], 0)} pb pour le taux servi, {pct(LECT['moins_values_realisees_pct_scr'], 0)} du SCR pour les moins-values réalisées. "
  f"« Robuste » : la borne de l'intervalle apparié à 95 % dépasse le seuil d'importance, avec le même signe, dans toutes les configurations de la grille de collecte (c0 de {pct(min(INT.values()), 0)} à {pct(max(INT.values()), 0)}, eta en {len(ELA)} points de {feta(min(ELA.values()))} à {feta(max(ELA.values()))}) et sous la loi de rachat ONC maximale (intensité centrale). "
  "Les hypothèses du modèle de collecte lui-même (e0, horizon de collecte) sont testées à part (section 2).\n")

# ------------------------------------------------------------------------------------------------
A("## 1. Ce que l'étude établit\n")
A("Quatre lectures distinctes, jamais interchangeables : l'**effet mesuré** est l'écart moyen de valeur totale à la gestion passive, dont le signe (baisse ou gain de valeur moyen) est lu configuration par configuration ; il est **significatif** si son intervalle apparié à 95 % exclut zéro ; il est **important** (économiquement matériel) s'il est significatif et si sa moyenne dépasse le seuil d'importance, ou seuil de matérialité, 2 % du SCR simplifié du profil ; la conclusion est **robuste aux hypothèses testées** si la borne de l'intervalle dépasse ce seuil, avec le même signe, dans toutes les configurations. "
  "Un changement de signe n'est retenu que si des écarts significatifs de signes opposés existent. Les verdicts des tableaux sont les lectures du moteur (`src/v5/collecte.py`) ; en langage courant : « défavorable, robuste » est une baisse de valeur robuste aux hypothèses testées, « favorable, robuste » un gain de valeur robuste, « toujours négatif (positif), non robuste » une baisse (un gain) de valeur moyen dans toutes les configurations, non robuste, « change de signe selon les hypothèses » un résultat dont le signe dépend des hypothèses. "
  "« Non robuste » ne signifie pas « non significatif » : les colonnes du tableau comptent séparément les configurations significatives, importantes et à borne au-delà du seuil.\n")
_couverts = sorted({q for q in N for c in K["strategies"] if K["prudentiel"][f"{q}|{c}"]["apport_0"]["indicateur_couverture_scr"] >= 1})
A("- **Capital à l'ouverture** : " + ("aucune stratégie n'atteint 100 % du SCR simplifié sans apport" if not _couverts else
   "sans apport, l'indicateur simplifié dépasse déjà 100 % pour " + ", ".join(
       f"{q} ({sum(K['prudentiel'][f'{q}|{c}']['apport_0']['indicateur_couverture_scr'] >= 1 for c in K['strategies'])} stratégies sur {len(K['strategies'])})" for q in _couverts)
   + ", dont l'apport estimé est nul") + ". Apport de la gestion passive [intervalle à 95 %] : "
  + " ; ".join(f"{p} {f(besoin(p, 'passive'))} [{f(K['capital'][f'{p}|passive']['incertitude']['1.0']['q025'])} ; {f(K['capital'][f'{p}|passive']['incertitude']['1.0']['q975'])}]" for p in N)
  + ". La collecte ne change pas ce besoin : il est calculé sur l'existant en extinction, dans la frontière des contrats (vue simplifiée, qui ne reprend pas les effets de la collecte sur les hypothèses de projection de l'existant).")
A("- **Coût de la recapitalisation** : un apport n'est jamais un profit ; recapitaliser à 100 % coûte à l'actionnaire " + ", ".join(
    f"{f(K['risque_neutre'][f'{p}|passive|0']['valeur_nette'] - K['risque_neutre'][f'{p}|passive|1.0']['valeur_nette'])} ({p})" for p in N) + " de valeur (impôt et participation sur les revenus du capital).")
v_ex = {p: rn(p, "passive")["valeur_existant"]["moyenne"] for p in N}
A("- **Valeur de l'existant** (gestion passive, capital à 100 %) : " + ", ".join(f"{f(v)} ({p})" for p, v in v_ex.items())
  + (". " + ", ".join(p for p, v in v_ex.items() if v < 0) + " : l'existant détruit de la valeur pour l'actionnaire une fois recapitalisé." if any(v < 0 for v in v_ex.values()) else "."))
van = {p: [rn(p, "passive", c0, eta)["valeur_affaires_nouvelles"]["moyenne"] for c0, eta in GRILLE] for p in N}
# part de la variation d'impôt dans la valeur avant impôt des affaires nouvelles (gestion passive, collecte centrale modérée)
part_impot = [-rn(p, "passive", C0C, ETAM)["impot_supplementaire"]["moyenne"]
              / (rn(p, "passive", C0C, ETAM)["valeur_affaires_nouvelles"]["moyenne"] - rn(p, "passive", C0C, ETAM)["impot_supplementaire"]["moyenne"]) for p in N]
marges = {p: [rn(p, "passive", c0, eta)["marge_affaires_nouvelles"] for c0, eta in GRILLE] for p in N}
A("- **Valeur des affaires nouvelles** (gestion passive) : " + " ; ".join(f"{p} de {f(min(v))} à {f(max(v))}, marge de {pct(min(marges[p]))} à {pct(max(marges[p]))} de la VA des primes" for p, v in van.items())
  + ". Elle dépend d'abord de l'intensité et de l'élasticité, qui fixent le volume collecté ; la variation d'impôt représente " + " à ".join(pct(v, 0) for v in (min(part_impot), max(part_impot)))
  + " de la valeur avant impôt (collecte centrale modérée), bien plus que le taux nominal de l'impôt sur les sociétés, et l'origine de cet écart n'est pas isolée (une explication possible : l'impôt sur les revenus du capital retenu avec la croissance). "
  "C'est une valeur avant coût explicite de mobilisation du capital additionnel : une charge frictionnelle annuelle de " + " à ".join(pct(v, 1) for v in (min(SC[p]["kappa_seuil"] for p in N), max(SC[p]["kappa_seuil"] for p in N)))
  + " du SCR proxy des affaires nouvelles suffirait à l'annuler en collecte centrale (analyse de seuil, `docs/V5_COLLECTE.md`, section 8). "
  "Seule cette valeur s'interprète : sa répartition entre les flux des contrats nouveaux et la variation du BE de l'existant déplace les transferts entre générations d'assurés sans les isoler.")
rob = {c: [robustesse(p, c) for p in N] for c in AUTRES}
A("- **Réinvestissement progressif** : " + ("écart de valeur totale à la gestion passive sans effet important pour les trois profils" if all(r == "sans effet important" for r in rob["reinvestissement_progressif"]) else
                                          "écart de valeur totale à la gestion passive : " + ", ".join(f"{r} ({p})" for p, r in zip(N, rob["reinvestissement_progressif"])))
  + f" ; en portefeuille fermé, l'écart de A est statistiquement significatif (contrôle sur tirages indépendants : {f(K['controle_reinvestissement']['ecart_moyen'], 2)} ± {f(K['controle_reinvestissement']['demi_intervalle_95'], 2)}) mais économiquement négligeable.")
cc = REC["capital_croissance"]
sup = {p: [v["scr_supplementaire_proportionnel"] for v in cc[k(p, "passive")]["collecte_centrale"].values()] for p in N}
A("- **Capital de la croissance** (ordre de grandeur, `docs/V5_COLLECTE.md`, section 8) : à SCR proportionnel à la PM, la collecte centrale demanderait à 10 ans un SCR supplémentaire de "
  + ", ".join(f"{f(min(v))} à {f(max(v))} ({p})" for p, v in sup.items()) + " pour la gestion passive selon l'élasticité, à comparer à l'apport d'ouverture (" + ", ".join(f"{f(besoin(p, 'passive'))} ({p})" for p in N) + "). "
  "La politique de distribution retient en même temps des fonds propres comptables : " + ", ".join(
      f"{f(cc[k(p, 'passive')]['collecte_centrale']['moderee']['fonds_propres_10_mediane'] - cc[k(p, 'passive')]['fonds_propres_10_mediane_extinction'])} ({p})" for p in N)
  + " de plus à 10 ans (médianes, élasticité modérée, contre un SCR supplémentaire de " + ", ".join(f"{f(cc[k(p, 'passive')]['collecte_centrale']['moderee']['scr_supplementaire_proportionnel'])} ({p})" for p in N)
  + ") : ce SCR n'appelle donc pas un apport du même montant, mais fonds propres comptables et prudentiels ne coïncident pas. "
  "**Aucune stratégie ne garantit la conformité prudentielle future** : l'apport d'ouverture couvre l'existant en extinction à la date d'évaluation, le SCR n'est pas projeté.")
mo, pl = REC["modele"], REC["place_2025"]["en_pct_pm_debut"]
A(f"- **Intensité centrale** : c0 = {pct(C0C, 0)} redonne la collecte nette de la place en 2025 ({pct(min(mo[p]['collecte_nette']['annee_1'] for p in N), 2)} la première année dans le modèle, {pct(pl['collecte_nette'], 2)} observés), pas ses flux bruts ({pct(pl['collecte_brute'], 1)} de primes, {pct(pl['prestations_implicites'], 1)} de sorties) ni la croissance de la PM ; "
  "le modèle n'a ni prélèvements sociaux ni arbitrages (`docs/V5_COLLECTE.md`, section 1).")
A("")
A(f"**Écart de valeur totale à la gestion passive, sur la grille de collecte et sous ONC maximale** ({len(GRILLE)} configurations de collecte et {len(ELA)} sous ONC maximale, soit {len(GRILLE) + len(ELA)} par profil) :\n")
A("| Stratégie | Profil | Effet mesuré (de ... à ...) | Signe | Significatif | Important | Borne au-delà du seuil | Verdict |\n| --- | --- | --- | --- | ---: | ---: | ---: | --- |")
SORTIE_JSON = {"_objet": "Lectures de la synthèse finale (écarts à la gestion passive, capital à 100 %), écrites par scripts/v5_synthese_finale.py ; "
               "elles alimentent les figures (scripts/v5_figures.py).", "seuils": {p: seuil(p) for p in N}, "valeur_totale": {}, "matrice": {}}
for c in AUTRES:
    for p in N:
        v = ecarts_totaux(p, c)
        n, signe, sig, imp_m, imp = lectures(v, seuil(p))
        A(f"| {COURT[c]} | {p} | {plage(v)} | {signe} | {sig} sur {n} | {imp_m} sur {n} | {imp} sur {n} | {robustesse(p, c)} |")
        centre = ec(p, c, C0C, ETAM)["totale"]
        SORTIE_JSON["valeur_totale"][k(p, c)] = {"min": min(x["moyenne"] for x in v), "max": max(x["moyenne"] for x in v), "n": n, "significatifs": sig, "importants": imp_m,
                                                 "bornes_au_dela_du_seuil": imp, "verdict": robustesse(p, c), "centre": centre,
                                                 "existant_ferme": ec(p, c, 0, 0)["existant"]}
A("")

# ------------------------------------------------------------------------------------------------
A("## 2. La politique de marge avec collecte\n")
for p in N:
    fe = ec(p, "taux_servi_marge", 0, 0)["existant"]["moyenne"]
    cases = {eta: ec(p, "taux_servi_marge", C0C, eta) for eta in ELA.values()}
    etats = {eta: col.etat_majorant(e["affaires_nouvelles"]) for eta, e in cases.items()}
    pire = min(ecarts_totaux(p, "taux_servi_marge"), key=lambda e: e["moyenne"] - e["demi_intervalle_95"])
    A(f"- **{p}** : avantage de {f(fe)} en portefeuille fermé ; avec la collecte centrale, écart de valeur totale à la gestion passive " + ", ".join(f"{f(e['totale']['moyenne'])} ± {f(e['totale']['demi_intervalle_95'])} (eta {feta(eta)})" for eta, e in cases.items())
      + " ; sous ONC maximale " + ", ".join(f"{f(onc(p, 'taux_servi_marge', eta)['ecart_totale']['moyenne'])} (eta {feta(eta)})" for eta in ELA.values())
      + f". Cas le moins favorable : {f(pire['moyenne'])} ± {f(pire['demi_intervalle_95'])}. Majorant (intensité centrale) : " + ", ".join(f"{v} pour eta {feta(eta)}" for eta, v in etats.items())
      + f". Verdict sur la grille : **{robustesse(p, 'taux_servi_marge')}**.")
marges_p = {p: rn(p, "passive", C0C, ETAM)["marge_affaires_nouvelles"] for p in N}
seuils_m, gap = {}, {}
for p in N:
    perte = rn(p, "passive", C0C, ETAM)["va_primes"]["moyenne"] - rn(p, "taux_servi_marge", C0C, ETAM)["va_primes"]["moyenne"]
    seuils_m[p] = ec(p, "taux_servi_marge", 0, 0)["existant"]["moyenne"] / perte if perte > 0 else float("nan")
    gap[p] = re_(p, "taux_servi_marge", C0C, ETAM)["ecart_taux_servi_reference_1_10"] - re_(p, "passive", C0C, ETAM)["ecart_taux_servi_reference_1_10"]
verdicts = {p: robustesse(p, "taux_servi_marge") for p in N}
A("\n**" + ("Pourquoi l'avantage résiste sur la grille" if all(v == "favorable, robuste" for v in verdicts.values()) else "Ce qui explique l'avantage mesuré sur la grille") + ".** Trois éléments, mesurés. "
  "(1) L'écart de taux servi effectivement réalisé entre la politique de marge et la gestion passive est faible : " + ", ".join(f"{f(1e4 * v, 0)} pb ({p})" for p, v in gap.items())
  + " en moyenne sur 10 ans (probabilité réelle, élasticité modérée), bien moins que le point d'écart des cibles, car la participation minimale (compte de participation simplifié) et les reprises de PPB limitent la baisse ; la perte de collecte en est d'autant réduite. "
  "(2) La marge des affaires nouvelles est mince : " + ", ".join(f"{pct(m)} ({p})" for p, m in marges_p.items())
  + " de la VA des primes pour la gestion passive, alors que l'avantage ne serait annulé, au premier ordre, qu'avec une marge de " + ", ".join(f"{pct(s)} ({p})" for p, s in seuils_m.items()) + " sur les primes perdues. "
  "(3) La gestion passive sert elle-même 0,5 point sous la référence : avec e0 = 0, une élasticité forte lui retire aussi une grande partie de sa collecte. Ce troisième point est une conséquence du choix de e0 et de la conception de la gestion passive, pas un mécanisme indépendant.\n")
A("**Ce que l'avantage doit aux hypothèses du modèle de collecte** (écart de valeur totale à la gestion passive, intensités centrale et forte, élasticités modérée et soutenue) :\n")
for p in N:
    lig = []
    for s in SENS:
        cas = [R["sensibilites_collecte"][k(s, p, "taux_servi_marge", c0, eta)]["ecart_totale"] for c0, eta in GRILLE_S]
        lig.append(f"{COURT_SENS[s]} : {col.robustesse(cas, seuil(p))} ({plage(cas)})")
    A(f"- **{p}** : " + " ; ".join(lig) + ".")
imprecis = [(s, p, c, c0, eta) for s in SENS for p in N for c in ("taux_servi_marge", "taux_servi_competitif") for c0, eta in GRILLE_S
            if R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"]["demi_intervalle_95"] > 5 * seuil(p)]
if imprecis:
    hi = max(R["sensibilites_collecte"][k(*x)]["ecart_totale"]["demi_intervalle_95"] for x in imprecis)
    forte = sum(x[3] == INT["forte"] for x in imprecis)
    A(f"\n{len(imprecis)} cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à {f(hi)}), dont {forte} à l'intensité forte, toutes avec une collecte de "
      + " ou ".join(sorted({COURT_SENS[x[0]].replace('collecte pendant ', '') for x in imprecis})) + " : la PM y croît pendant des décennies, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche de conclure dans un sens ou dans l'autre.")
tous = {p: col.robustesse(ecarts_totaux(p, "taux_servi_marge") + ecarts_hypotheses(p, "taux_servi_marge"), seuil(p)) for p in N}
A("\nSur l'ensemble des configurations testées (grille, ONC maximale, e0 et horizon de collecte), le verdict est : " + ", ".join(f"{v} ({p})" for p, v in tous.items()) + ". "
  "g_min = 0 n'est pas testé. **La politique de marge n'est pas qualifiée d'optimale** : son avantage dépend de l'élasticité, non calibrée, de e0 et de l'horizon de collecte ; le modèle ne fait pas racheter l'existant au-delà de la loi de rachat dynamique quand la compétitivité baisse ; "
  "il ignore les effets commerciaux et de réputation d'un taux servi durablement inférieur à la référence (écart moyen de " + ", ".join(f"{f(1e4 * re_(p, 'taux_servi_marge', C0C, ETAM)['ecart_taux_servi_reference_1_10'], 0)} pb ({p})" for p in N)
  + " sur 10 ans en probabilité réelle) ; et la valeur actionnaire n'est qu'une des dimensions de la section 3.\n")
def decalage(c, s):
    """Écart moyen de valeur totale (profils et configurations) sous l'hypothèse s, et au centre."""
    cfg = [(c0, eta) for c0, eta in GRILLE_S if c0 == C0C]  # intensité centrale : les cellules à 10 % sur 30 ou 60 ans sont trop imprécises
    sous = [R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"]["moyenne"] for p in N for c0, eta in cfg]
    centre = [ec(p, c, c0, eta)["totale"]["moyenne"] for p in N for c0, eta in cfg]
    return sum(centre) / len(centre), sum(sous) / len(sous)


comp_h = {p: col.robustesse(ecarts_hypotheses(p, "taux_servi_competitif"), seuil(p)) for p in N}
A("**Politique compétitive sous ces hypothèses** : " + ", ".join(f"{v} ({p}, {plage(ecarts_hypotheses(p, 'taux_servi_competitif'))})" for p, v in comp_h.items()) + ".\n")
A("**Déplacement moyen de l'écart de valeur totale** (trois profils, intensité centrale, élasticités modérée et soutenue), du centre à chaque hypothèse : " + " ; ".join(
    f"{POL[c]} : " + ", ".join(f"{COURT_SENS[s]} de {f(decalage(c, s)[0])} à {f(decalage(c, s)[1])}" for s in SENS) for c in ("taux_servi_marge", "taux_servi_competitif"))
  + ". " + phrase_signe([(p, c) for p in N for c in ("taux_servi_marge", "taux_servi_competitif")]) + "\n")

# ------------------------------------------------------------------------------------------------
A("## 3. Synthèse par profil\n")
A(f"Tous les chiffres des tableaux sont des écarts à la gestion passive, capital à 100 %. Valeur de l'existant : portefeuille fermé (intervalle apparié). Affaires nouvelles et indicateurs réels : collecte centrale (c0 = {pct(C0C, 0)}), élasticité modérée (eta = {feta(ETAM)}). "
  "Valeur totale : verdict sur la grille et sous ONC maximale. Rentabilité, compétitivité (taux servi moyen du fonds) et liquidité en probabilité réelle, sans intervalle ; capital : apport à 100 % (intervalle de rééchantillonnage).\n")
for p in N:
    x0 = K["prudentiel"][f"{p}|passive"]["apport_0"]
    r0c = re_(p, "passive", C0C, ETAM)
    A(f"### Profil {p}\n")
    A(f"Indicateur de couverture simplifié du SCR sans apport : {pct(x0['indicateur_couverture_scr'], 0)}. Gestion passive avec collecte centrale modérée : valeur de l'existant {f(v_ex[p])}, valeur des affaires nouvelles {f(rn(p, 'passive', C0C, ETAM)['valeur_affaires_nouvelles']['moyenne'])}, "
      f"rendement réel des fonds propres {pct(r0c['rendement_fonds_propres_1_10_agrege'])} ({'sous le' if r0c['rendement_fonds_propres_1_10_agrege'] < RE_EXIGE else 'au-dessus du'} rendement exigé fictif de {pct(RE_EXIGE, 0)}), "
      f"écart du taux servi à la référence de {f(1e4 * r0c['ecart_taux_servi_reference_1_10'], 0)} pb, collecte 1-10 de {f(r0c['collecte_1_10_moyenne'])} (réel).\n")
    A("| Stratégie | Écart de valeur de l'existant | Écart de valeur des affaires nouvelles | Écart de valeur totale (grille et ONC) | Rentabilité | Compétitivité | Liquidité | Capital à l'ouverture |\n| --- | --- | --- | --- | --- | --- | --- | --- |")
    for c in AUTRES:
        e0 = ec(p, c, 0, 0)["existant"]
        ean = ec(p, c, C0C, ETAM)["affaires_nouvelles"]
        r = re_(p, c, C0C, ETAM)
        kp = K["capital"][f"{p}|{c}"]["ecart_passive"]["1.0"]
        SORTIE_JSON["matrice"][k(p, c)] = {
            "existant": lecture_json(e0["moyenne"], seuil(p), 1, abs(e0["moyenne"]) <= e0["demi_intervalle_95"]),
            "affaires_nouvelles": lecture_json(ean["moyenne"], seuil(p), 1, abs(ean["moyenne"]) <= ean["demi_intervalle_95"]),
            "valeur_totale": {"lecture": robustesse(p, c)},
            "rentabilite": lecture_json(r["rendement_fonds_propres_1_10_agrege"] - r0c["rendement_fonds_propres_1_10_agrege"], LECT["rendement_fonds_propres_pt"], 1),
            "competitivite": lecture_json(r["ecart_taux_servi_reference_1_10"] - r0c["ecart_taux_servi_reference_1_10"], LECT["ecart_taux_servi_pb"] / 1e4, 1),
            "liquidite": lecture_json(r["moins_values_realisees_1_10_q99"] - r0c["moins_values_realisees_1_10_q99"], LECT["moins_values_realisees_pct_scr"] * scr(p), -1),
            "capital_ouverture": lecture_json(besoin(p, c) - besoin(p, "passive"), LECT["apport_pct_scr"] * scr(p), -1, kp["q025"] <= 0 <= kp["q975"]),
        }
        A(f"| {COURT[c]} | {qualif(e0['moyenne'], seuil(p), 1, f, abs(e0['moyenne']) <= e0['demi_intervalle_95'])} | {qualif(ean['moyenne'], seuil(p), 1, f, abs(ean['moyenne']) <= ean['demi_intervalle_95'])} | {robustesse(p, c)} ({plage(ecarts_totaux(p, c))}) | "
          f"{qualif(r['rendement_fonds_propres_1_10_agrege'] - r0c['rendement_fonds_propres_1_10_agrege'], LECT['rendement_fonds_propres_pt'], 1, lambda v: f(100 * v, 2) + ' pt')} | "
          f"{qualif(r['ecart_taux_servi_reference_1_10'] - r0c['ecart_taux_servi_reference_1_10'], LECT['ecart_taux_servi_pb'] / 1e4, 1, lambda v: f(1e4 * v, 0) + ' pb')} | "
          f"{qualif(r['moins_values_realisees_1_10_q99'] - r0c['moins_values_realisees_1_10_q99'], LECT['moins_values_realisees_pct_scr'] * scr(p), -1, f)} | "
          f"{qualif(besoin(p, c) - besoin(p, 'passive'), LECT['apport_pct_scr'] * scr(p), -1, f, kp['q025'] <= 0 <= kp['q975'])} |")
    A("")
    fav = [c for c in AUTRES if robustesse(p, c) == "favorable, robuste"]
    defav = [c for c in AUTRES if robustesse(p, c) == "défavorable, robuste"]
    dep = [c for c in AUTRES if robustesse(p, c) not in ("favorable, robuste", "défavorable, robuste", "sans effet important")]
    A("**Lecture.**\n")
    if fav:
        A("- **Gain de valeur totale robuste aux hypothèses testées** (grille et ONC) : " + ", ".join(COURT[c] for c in fav) + ". Il reste conditionnel aux hypothèses de comportement, non calibrées, et se paie sur d'autres dimensions (tableau).")
    if defav:
        A("- **Baisse de valeur totale robuste aux hypothèses testées** : " + ", ".join(COURT[c] for c in defav) + ".")
    if dep:
        A("- **Résultat qui dépend des hypothèses** (signe, importance ou précision) : " + ", ".join(f"{COURT[c]} ({robustesse(p, c)})" for c in dep) + ".")
    tetes = [max(CODES, key=lambda c: rn(p, c, c0, eta)["valeur_totale"]["moyenne"]) for c0, eta in GRILLE] + \
            [max(CODES, key=lambda c: onc(p, c, eta)["valeur_totale"]["moyenne"]) for eta in ELA.values()]
    noms = sorted(set(tetes), key=CODES.index)
    tetes_sens = {s: max(CODES, key=lambda c: K["sensibilites"][f"{p}|{c}|{s}"]["valeur_nette"]) for s in SENS_CONSO}
    autres_tetes = {s: c for s, c in tetes_sens.items() if c not in noms}
    A("- **Premier rang de la valeur totale** : " + ", ".join(f"{COURT[c]} ({tetes.count(c)} configurations sur {len(tetes)})" for c in noms)
      + (f" ; en portefeuille fermé, il passe à {', '.join(COURT[c] for c in autres_tetes.values())} sous " + ", ".join(SENS_LIB[s] for s in autres_tetes) if autres_tetes else "")
      + (". **Il change avec les hypothèses.**" if len(noms) > 1 or autres_tetes else ". Même premier rang sur la grille, mais conditionnel aux hypothèses non calibrées (élasticité, e0, horizon de collecte, loi de rachat) : il n'est pas présenté comme optimal."))
    A("")

# ------------------------------------------------------------------------------------------------
A("## 4. Ce que l'étude ne permet pas de conclure\n")
amp = {c: plage([x for p in N for x in ecarts_totaux(p, c) + ecarts_hypotheses(p, c)]) for c in ("taux_servi_marge", "taux_servi_competitif")}
for x in [
    "**Élasticité de la collecte et forme de la réaction** : aucune donnée vérifiée. Sur l'ensemble des configurations testées (y compris les cellules imprécises à 30 et 60 ans), l'écart de valeur totale va " + " ; ".join(f"{amp[c]} pour {POL[c]}" for c in amp)
    + ". " + phrase_signe([(p, c) for p in N for c in ("taux_servi_marge", "taux_servi_competitif")]),
    "**Comportement de rachat** : la loi centrale vient des V1 à V4, les corridors ONC de 2013 servent de sensibilité ; aucune donnée 2026 ne les calibre ; la perte de compétitivité ne fait pas racheter l'existant au-delà de cette loi.",
    "**Capital futur** : le SCR n'est pas projeté ; le capital de la croissance n'est estimé qu'en ordre de grandeur (SCR proportionnel à la PM) ; fonds propres comptables et prudentiels ne coïncident pas ; aucune stratégie ne garantit la conformité prudentielle future.",
    "**Flux de la place** : c0 = 6 % ne fait qu'approcher la collecte nette de 2025 (" + f"{pct(mo['B']['collecte_nette']['annee_1'], 2)} de la PM contre {pct(pl['collecte_nette'], 2)}" + "), sur une seule année, avec des flux bruts plus faibles ; prélèvements sociaux et arbitrages ne sont pas modélisés.",
    "**Lecture statistique** : les intervalles à 95 % sont calculés cellule par cellule, ils ne sont pas simultanés : sur l'ensemble des stratégies, profils et hypothèses, quelques écarts peuvent paraître significatifs par hasard ; « robuste » est un critère descriptif, interne à la grille testée.",
    "**Liquidité** : quantiles à 99 % estimés sur 1 000 scénarios en probabilité réelle, soit une dizaine de scénarios dans la queue, sans intervalle de confiance ; les écarts proches du seuil sont fragiles.",
    "**Mécanismes absents** : inflation et attractivité du taux servi réel, arbitrages entre fonds euros et unités de compte, migration de notation des obligations, comportement de rachat propre aux contrats nouveaux (même loi que l'existant), politique de distribution fondée sur la couverture du SCR plutôt que sur un ratio comptable ; chacun peut modifier le classement des politiques de taux servi.",
    "**Données de marché** : courbe sans risque EIOPA du 31/10/2026 (observée) ; spread des obligations hypothétique, égal à la moyenne de long terme des spreads publiée par l'EIOPA pour la notation A, et non un spread de marché observé à cette date : les niveaux de valeur et de capital en dépendent, les comparaisons de stratégies partagent le même marché.",
    ("**Vue prudentielle** : indicateurs simplifiés (base avec VA, risque opérationnel par la seule formule sur provisions, ni contrepartie, ni concentration, ni immobilier, ni change, impôts différés actifs non reconnus), pas de mesure transitoire ; ce ne sont pas des ratios réglementaires. "
     "Elle est calculée en extinction, sans les effets de la collecte sur les hypothèses de projection de l'existant ; la réserve de capitalisation suit le principe de l'article R.351-2-1 du Code des assurances sans en reproduire toutes les modalités."),
    "**Valeur des affaires nouvelles** : hors Solvabilité II, avant coût explicite de mobilisation du capital additionnel ; seuls les coûts frictionnels du capital comptable retenu (impôt et participation sur ses revenus) sont déduits ; le coût du capital immobilisé pour le SCR supplémentaire n'est mesuré que par un seuil, et aucune marge pour risques non couvrables n'est déduite.",
]:
    A(f"- {x}")
A("")
VLN = [p for p in N if abs(REC["variantes_liquidation"][p]["rc_initiale_nulle_sans_retention"]["residu_pct_va_primes"]) < 0.001]
A("## 5. Contrôles et corrections\n")
A("**Reproductibilité.** Sur un clone propre du dépôt, tous les tests passent, les documents et les figures se régénèrent à l'identique depuis les résultats versionnés, "
  "et un échantillon de résultats recalculé sans cache est identique aux résultats versionnés (`docs/V5_REPRODUCTION.md`).\n")
A("**Correction ayant modifié des résultats.** Une première version de la répartition de l'intérêt entre générations créditait les contrats nouveaux au-delà de l'intérêt décidé quand le plancher de TMG du fonds était juste atteint (profil A). "
  "Elle est corrigée, couverte par un test de non-régression, et les résultats concernés ont été recalculés.\n")
A("**Contrôles complémentaires.** Grille d'élasticité densifiée (0,75 et 1,0), e0 et horizon de collecte testés à part, loi de rachat ONC maximale appliquée aux huit stratégies ; "
  "critères de lecture complets (significatif, important, robuste ; « non concluant » pour des signes mêlés sans écart significatif ; « sans effet important » seulement si l'intervalle entier reste sous le seuil ; changement de signe retenu seulement s'il repose sur des écarts significatifs) ; "
  "variantes de liquidation du contrat sans marge explicite, qui ramènent son résidu sous 0,1 % des primes pour " + " et ".join(VLN) + " et en identifient la cause pour " + ", ".join(p for p in N if p not in VLN) + " ; "
  "seuil de coût du capital des affaires nouvelles ; traitement de la réserve de capitalisation confronté à l'article R.351-2-1 du Code des assurances.\n")
A("Ces contrôles vérifient la cohérence interne du modèle et la reproductibilité des résultats ; ils ne constituent pas une validation actuarielle indépendante.\n")
Path(ARGS.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
Path(ARGS.json).write_text(json.dumps(SORTIE_JSON, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("écrit :", ARGS.sortie)
