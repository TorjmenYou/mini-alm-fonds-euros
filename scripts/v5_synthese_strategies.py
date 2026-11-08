"""Génère docs/V5_SYNTHESE_STRATEGIES.md : synthèse exécutive des stratégies ALM, par profil, depuis
resultats/v5_consolidation.json. Les phrases sont écrites ici ; tous les chiffres viennent des résultats.
Aucune stratégie n'est désignée gagnante : la synthèse indique, dimension par dimension, ce que chaque
stratégie change par rapport à la gestion passive, et si l'écart de valeur résiste aux sensibilités.

Usage : python scripts/v5_synthese_strategies.py [--entree resultats/v5_consolidation.json] [--sortie docs/V5_SYNTHESE_STRATEGIES.md]
"""

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import strategies as stg  # noqa: E402

N = "ABC"
COURT = {"passive": "Passive", "reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}
SENS = {"reaction_onc_max": "réaction forte des assurés (ONC max.)", "reference_immediate": "transmission immédiate des taux à la référence",
        "defaut_bloc_souverain": "défaut corrélé par bloc souverain"}

ap = argparse.ArgumentParser()
ap.add_argument("--entree", default=str(RACINE / "resultats" / "v5_consolidation.json"))
ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_SYNTHESE_STRATEGIES.md"))
ARGS = ap.parse_args()
C = json.loads(Path(ARGS.entree).read_text(encoding="utf-8"))
LECT = stg.charger()["lecture"]
RE_EXIGE = stg.charger()["rentabilite_reelle"]["rendement_exige"]["valeur"]
CODES = C["strategies"]
AUTRES = [c for c in CODES if c != "passive"]
B = "1.0"  # base de capital commune de la synthèse : chaque stratégie à 100 % du SCR simplifié


def f(x, dec=1):
    if round(x, dec) == 0:
        x = 0.0
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def x0(p, c="passive"):
    return C["prudentiel"][f"{p}|{c}"]["apport_0"]


def scr(p):
    return x0(p)["scr"]


def rn(p, c, b=B):
    return C["risque_neutre"][f"{p}|{c}|{b}"]


def re_(p, c, b=B):
    return C["reel"][f"{p}|{c}|{b}"]


def ecart(p, c, b=B):
    e = C["ecarts"][f"{p}|{c}|{b}"]
    return e["ecart_moyen"], e["demi_intervalle_95"]


def besoin(p, c, t="1.0"):
    return C["capital"][f"{p}|{c}"]["besoin"][t]


def dims(p, c):
    """Par dimension : écart à la passive, significativité (None si non mesurée), seuil d'importance,
    sens favorable (+1 si une hausse est favorable) et format."""
    k = C["capital"][f"{p}|{c}"]["ecart_passive"]["1.0"]
    m_v, h_v = ecart(p, c)
    return {
        "Valeur actionnaire": (m_v, abs(m_v) > h_v, LECT["valeur_nette_pct_scr"] * scr(p), 1, lambda x: f(x)),
        "Rentabilité": (re_(p, c)["rendement_fonds_propres_1_10_agrege"] - re_(p, "passive")["rendement_fonds_propres_1_10_agrege"], None, LECT["rendement_fonds_propres_pt"], 1, lambda x: f(100 * x, 2) + " pt"),
        "Compétitivité": (re_(p, c)["ecart_taux_servi_reference_1_10"] - re_(p, "passive")["ecart_taux_servi_reference_1_10"], None, LECT["ecart_taux_servi_pb"] / 1e4, 1, lambda x: f(1e4 * x, 0) + " pb"),
        "Liquidité": (re_(p, c)["moins_values_realisees_1_10_q99"] - re_(p, "passive")["moins_values_realisees_1_10_q99"], None, LECT["moins_values_realisees_pct_scr"] * scr(p), -1, lambda x: f(x)),
        "Capital": (besoin(p, c) - besoin(p, "passive"), not (k["q025"] <= 0.0 <= k["q975"]), LECT["apport_pct_scr"] * scr(p), -1, lambda x: f(x)),
    }


def qualifier(m, significatif, seuil, sens, fmt):
    if significatif is False:
        return f"neutre ({fmt(m)}, ns)"
    if abs(m) < seuil:
        return f"neutre ({fmt(m)})"
    return ("favorable" if m * sens > 0 else "défavorable") + f" ({fmt(m)})"


def robuste(p, c):
    m1, h1 = ecart(p, c, "1.0")
    m2, h2 = ecart(p, c, "1.5")
    seuil = LECT["valeur_nette_pct_scr"] * scr(p)
    if not (abs(m1) > max(h1, seuil) and abs(m2) > max(h2, seuil) and m1 * m2 > 0):
        return False
    return all(C["sensibilites"][f"{p}|{c}|{s}"]["ecart_moyen"] * m1 > 0 and abs(C["sensibilites"][f"{p}|{c}|{s}"]["ecart_moyen"]) > C["sensibilites"][f"{p}|{c}|{s}"]["demi_intervalle_95"] for s in SENS)


L = []
A = L.append
A("# V5 : synthèse exécutive des stratégies ALM\n")
A("Trois profils fictifs de fonds euros, huit stratégies, une base de capital commune : chaque stratégie reçoit l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 %, et sa valeur est nette de cet apport. "
  "Détail, méthode et limites : `docs/V5_STRATEGIES.md` ; généré par `scripts/v5_synthese_strategies.py` depuis `resultats/v5_consolidation.json`. Unités fictives : 1 unité = 10 M€.\n")
A("**À lire avant les tableaux.** Analyse exploratoire, pas une recommandation. Les indicateurs prudentiels sont simplifiés et ne sont pas des ratios réglementaires. Le portefeuille est fermé : la perte ou le gain de collecte d'une politique de taux servi n'y est pas compté (collecte nouvelle : `docs/V5_COLLECTE.md`). "
  "Les probabilités de recapitalisation sont conditionnelles aux hypothèses du modèle. Aucune stratégie n'est désignée gagnante.\n")
A(f"**Cinq dimensions, écarts à la gestion passive.** Valeur actionnaire : valeur nette risque neutre (après apport, apports ultérieurs et impôt). Rentabilité : rendement des fonds propres comptables en probabilité réelle, années 1 à 10. "
  f"Compétitivité : écart du taux servi à la référence des assurés (réel). Liquidité : moins-values réalisées sur 10 ans, quantile 99 % (réel). Capital : apport nécessaire pour 100 % du SCR simplifié. "
  f"« Neutre » : écart sous le seuil d'importance fixé à l'avance ({pct(LECT['valeur_nette_pct_scr'], 0)} du SCR pour la valeur et l'apport, {f(1e4 * LECT['rendement_fonds_propres_pt'], 0)} pb de rentabilité, {f(LECT['ecart_taux_servi_pb'], 0)} pb de taux servi, {pct(LECT['moins_values_realisees_pct_scr'], 0)} du SCR de moins-values) ou non significatif (ns : intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle n'ont pas d'intervalle). "
  "« Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital (100 % et 150 %) et sous les trois sensibilités testées (" + ", ".join(SENS.values()) + ").\n")

# ------------------------------------------------------------------------------------------------
A("## Constats communs aux trois profils\n")
_couverts = [f"{p}, {c}" for p in N for c in C["strategies"]
             if C["prudentiel"][f"{p}|{c}"]["apport_0"]["indicateur_couverture_scr"] >= 1]
A("- **Capital** : " + ("aucune stratégie n'atteint 100 % du SCR simplifié sans apport" if not _couverts else
   f"sans apport, l'indicateur atteint 100 % du SCR simplifié pour {len(_couverts)} couples profil-stratégie sur {len(N) * len(C['strategies'])} ("
   + ", ".join(f"profil {q} : toutes sauf le repositionnement" if sum(x.startswith(q + ",") for x in _couverts) == len(C["strategies"]) - 1 and f"{q}, repositionnement" not in _couverts
                         else f"profil {q} : {sum(x.startswith(q + ',') for x in _couverts)} stratégies" for q in sorted({x.split(',')[0] for x in _couverts})) + "), dont l'apport estimé est donc nul")
  + ". Apport nécessaire en gestion passive, avec son intervalle à 95 % : "
  + " ; ".join(f"{p} {f(besoin(p, 'passive'))} [{f(C['capital'][f'{p}|passive']['incertitude']['1.0']['q025'])} ; {f(C['capital'][f'{p}|passive']['incertitude']['1.0']['q975'])}]" for p in N)
  + ". Recapitaliser coûte de la valeur à l'actionnaire (impôt et participation sur les revenus du capital) : " + ", ".join(f"{f(rn(p, 'passive', '0')['valeur_nette'] - rn(p, 'passive')['valeur_nette'])} ({p})" for p in N) + ".")
plancher_mcr = [p for p in N if x0(p)["mcr_detail"]["contrainte_active"] == "plancher de 25 % du SCR"]
if plancher_mcr:
    A(f"- **MCR** : le plancher de 25 % du SCR s'applique ({', '.join(plancher_mcr)}) ; les indicateurs MCR élevés reflètent ce plancher, pas une marge de sécurité propre.")
reinv = [(p, *ecart(p, "reinvestissement_progressif")) for p in N]
sous_seuil = all(abs(m) < LECT["valeur_nette_pct_scr"] * scr(p) for p, m, _ in reinv)
ctl = C["controle_reinvestissement"]
A("- **Réinvestissement progressif** : écarts de valeur " + ", ".join(f"{f(m, 2)} ± {f(h, 2)} ({p})" for p, m, h in reinv)
  + f" ; pour A, l'écart se retrouve sur des tirages indépendants ({f(ctl['ecart_moyen'], 2)} ± {f(ctl['demi_intervalle_95'], 2)}, {f(ctl['n_scenarios'], 0)} scénarios)"
  + (f" ; tous sous le seuil d'importance de {pct(LECT['valeur_nette_pct_scr'], 0)} du SCR. Il n'est pas économiquement distinguable de la gestion passive, même quand l'écart est statistiquement significatif." if sous_seuil
     else f" ; au moins un écart dépasse le seuil d'importance de {pct(LECT['valeur_nette_pct_scr'], 0)} du SCR (détail dans `docs/V5_STRATEGIES.md`, section 4)."))
marge = [(p, ecart(p, "taux_servi_marge")[0], C["sensibilites"][f"{p}|taux_servi_marge|reaction_onc_max"]["ecart_moyen"]) for p in N]
marge_en_tete = [p for p in N if max(CODES, key=lambda c: rn(p, c)["valeur_nette"]) == "taux_servi_marge"]
A("- **Politique de marge** : " + (f"la plus forte valeur actionnaire au centre ({', '.join(marge_en_tete)})" if marge_en_tete else "pas en tête de la valeur au centre")
  + ", au prix d'un taux servi plus bas ; écart de valeur au centre puis sous une réaction forte des assurés : "
  + ", ".join(f"{f(m)} puis {f(s)} ({p})" for p, m, s in marge) + ". Le portefeuille fermé ne compte pas la collecte : ce résultat n'est ni une conclusion ni, par principe, un majorant (avec collecte : `docs/V5_COLLECTE.md` et `docs/V5_SYNTHESE_FINALE.md`).")
comp = [(p, ecart(p, "taux_servi_competitif")[0], re_(p, "taux_servi_competitif")["ecart_taux_servi_reference_1_10"] - re_(p, "passive")["ecart_taux_servi_reference_1_10"]) for p in N]
A("- **Politique compétitive** : écart de valeur et gain de taux servi par rapport à la gestion passive : " + ", ".join(f"{f(m)} et {f(1e4 * t, 0)} pb ({p})" for p, m, t in comp) + ".")
pres = []
pres_dr, pres_dv = {}, {}
for p in N:
    dv = rn(p, "taux_servi_competitif_preservant")["valeur_nette"] - rn(p, "taux_servi_competitif")["valeur_nette"]
    dt = re_(p, "taux_servi_competitif_preservant")["ecart_taux_servi_reference_1_10"] - re_(p, "taux_servi_competitif")["ecart_taux_servi_reference_1_10"]
    dr = rn(p, "taux_servi_competitif_preservant")["taux_rachat_moyen_1_10"] - rn(p, "taux_servi_competitif")["taux_rachat_moyen_1_10"]
    pres.append(f"{f(dv)} de valeur, {f(1e4 * dt, 0)} pb de taux servi, {f(1e4 * dr, 0)} pb de rachat ({p})")
    pres_dr[p], pres_dv[p] = dr, dv
baisse_rachat = [p for p in N if 1e4 * pres_dr[p] <= -0.5]
gain_net = [p for p in N if pres_dv[p] > LECT["valeur_nette_pct_scr"] * scr(p)]
A("- **Préserver la PPB** dans la politique compétitive (variante comparée à la version de base, mêmes scénarios) : " + " ; ".join(pres)
  + ". Les rachats baissent" + ("" if len(baisse_rachat) == len(N) else (" pour " + " et ".join(baisse_rachat) if baisse_rachat else " peu"))
  + " ; les gains de taux servi et de valeur restent modestes" + (", sauf pour " + " et ".join(gain_net) if gain_net else "")
  + " (détail : `docs/V5_STRATEGIES.md`, section 5). Le coût en valeur de la politique compétitive par rapport à la gestion passive demeure.")
ret = [(p, ecart(p, "distribution_retention")[0], re_(p, "distribution_retention")["rendement_fonds_propres_1_10_agrege"] - re_(p, "passive")["rendement_fonds_propres_1_10_agrege"]) for p in N]
A("- **Rétention de capital** : écart de valeur et de rentabilité " + ", ".join(f"{f(m)} et {f(100 * r, 2)} pt ({p})" for p, m, r in ret)
  + ". Le capital conservé supporte l'impôt et partage ses revenus avec les assurés, et dilue le rendement des fonds propres. Son bénéfice attendu, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR.")
ld = [(p, ecart(p, "liquidite_defensive")[0], re_(p, "liquidite_defensive")["rendement_fonds_propres_1_10_agrege"] - re_(p, "passive")["rendement_fonds_propres_1_10_agrege"]) for p in N]
ld_imp = [p for p, m, _ in ld if abs(m) > max(ecart(p, "liquidite_defensive")[1], LECT["valeur_nette_pct_scr"] * scr(p))]
A("- **Liquidité défensive** : écart de valeur risque neutre et de rentabilité réelle " + ", ".join(f"{f(m)} et {f(100 * r, 2)} pt ({p})" for p, m, r in ld)
  + (". Les deux mesures vont en sens opposés : moins d'actions réduit le coût des options en risque neutre et fait perdre la prime actions en probabilité réelle"
     + (f" ; le gain de valeur n'est important que pour {', '.join(ld_imp)}" if ld_imp else " ; le gain de valeur n'est important pour aucun profil") if all(m > 0 > r for _, m, r in ld) else "")
  + ". Valeur risque neutre et rentabilité réelle sont donc présentées séparément, jamais combinées.\n")

# ------------------------------------------------------------------------------------------------
for p in N:
    x = x0(p)
    inc = C["prudentiel"][f"{p}|passive"]["incertitude_apport_0"]["ratio"]
    A(f"## Profil {p}\n")
    A(f"Point de départ (gestion passive, sans apport) : fonds propres de niveau 1 de {f(x['fonds_propres_niveau_1'])} pour un SCR simplifié de {f(x['scr'])}, indicateur de {pct(x['indicateur_couverture_scr'], 0)} [{pct(inc['q025'], 0)} ; {pct(inc['q975'], 0)}]. "
      f"Apport pour 100 % : {f(besoin(p, 'passive'))} ; pour 150 % : {f(besoin(p, 'passive', '1.5'))}. À 100 %, valeur nette de {f(rn(p, 'passive')['valeur_nette'])}, rendement réel des fonds propres de {pct(re_(p, 'passive')['rendement_fonds_propres_1_10_agrege'])} ({'sous le' if re_(p, 'passive')['rendement_fonds_propres_1_10_agrege'] < RE_EXIGE else 'au-dessus du'} rendement exigé fictif de {pct(RE_EXIGE, 0)}), "
      f"taux servi moyen de {pct(re_(p, 'passive')['taux_servi_moyen_1_10'], 2)} ({f(1e4 * re_(p, 'passive')['ecart_taux_servi_reference_1_10'], 0)} pb sous la référence).\n")
    A("| Stratégie | Valeur actionnaire | Rentabilité | Compétitivité | Liquidité | Capital | Écart de valeur robuste |\n| --- | --- | --- | --- | --- | --- | --- |")
    q = {}
    for c in AUTRES:
        d = dims(p, c)
        q[c] = {k: qualifier(*v) for k, v in d.items()}
        rob = ("oui, favorable" if ecart(p, c)[0] > 0 else "oui, défavorable") if robuste(p, c) else "non"
        A(f"| {COURT[c]} | " + " | ".join(q[c].values()) + f" | {rob} |")
    A("")
    favorables = {c: [k for k, v in q[c].items() if v.startswith("favorable")] for c in AUTRES}
    defavorables = {c: [k for k, v in q[c].items() if v.startswith("défavorable")] for c in AUTRES}
    compromis = [c for c in AUTRES if favorables[c] and defavorables[c]]
    sans_effet = [c for c in AUTRES if not favorables[c] and not defavorables[c]]
    domines = [c for c in AUTRES if defavorables[c] and not favorables[c]]
    meilleure = max(CODES, key=lambda c: rn(p, c)["valeur_nette"])
    A("**Lecture.**\n")
    if compromis:
        A("- **Compromis** : " + " ; ".join(f"{COURT[c]} améliore {', '.join(k.lower() for k in favorables[c])} mais dégrade {', '.join(k.lower() for k in defavorables[c])}" for c in compromis) + ".")
    if domines:
        A("- **Défavorables sans contrepartie mesurée** sur les cinq dimensions, à capital égal : " + ", ".join(COURT[c] for c in domines)
          + (" (pour la rétention, le bénéfice attendu sur la couverture des années suivantes n'est pas mesuré)" if "distribution_retention" in domines else "") + ".")
    if sans_effet:
        A("- **Sans effet important** : " + ", ".join(COURT[c] for c in sans_effet) + ".")
    tetes = {s: max(CODES, key=lambda c: C["sensibilites"][f"{p}|{c}|{s}"]["valeur_nette"]) for s in SENS}
    change = len(set(tetes.values()) | {meilleure}) > 1
    A(f"- **Valeur** : la plus forte valeur nette au centre est celle de « {COURT[meilleure]} »" + (", " + ("et ce rang tient sous les trois sensibilités testées" if not change else
      "mais le premier rang change : " + " ; ".join(f"« {COURT[t]} » sous {SENS[s]}" for s, t in tetes.items() if t != meilleure)) if meilleure != "passive" else "")
      + (". " + ("Son avance sur la gestion passive reste importante et de même signe pour les deux cibles de capital et sous les trois sensibilités, mais elle est mesurée en portefeuille fermé (avec collecte : `docs/V5_COLLECTE.md`)." if robuste(p, meilleure)
                 else "Son avance sur la gestion passive n'est pas robuste à toutes les hypothèses testées.") if meilleure != "passive" else ".")
      + " Aucune stratégie n'est désignée gagnante.")
    A("")

# ------------------------------------------------------------------------------------------------
A("## Ce qui manque pour conclure\n")
A("1. **Collecte nouvelle sensible au taux servi relatif** : traitée dans `docs/V5_COLLECTE.md` ; la synthèse économique finale (`docs/V5_SYNTHESE_FINALE.md`) réunit les deux vues.")
A("2. **Comportement des assurés** : aucune donnée 2026 ne calibre la réaction aux écarts de taux ; les corridors ONC de 2013 restent une plage de sensibilité.")
A("3. **Vue prudentielle complète** : modules non modélisés, mesure transitoire, ajustement symétrique, impôts différés actifs ; les indicateurs restent indicatifs.")
A("4. **ACPR n° 185** : non consulté ; aucun chiffre de place n'a servi à ajuster les profils.\n")
Path(ARGS.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit :", ARGS.sortie)
