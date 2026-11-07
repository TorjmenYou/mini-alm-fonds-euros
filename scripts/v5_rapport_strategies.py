"""Génère docs/V5_STRATEGIES.md depuis resultats/v5_consolidation.json (scripts/v5_consolidation.py),
v5_strategies_mecanismes.json, v5_effet_distribution.json, v5_synthese.json et v5_strategies.json.
Les phrases sont écrites ici ; tous les chiffres viennent des fichiers de résultats et de données.

Usage : python scripts/v5_rapport_strategies.py [--entree resultats/v5_consolidation.json] [--sortie docs/V5_STRATEGIES.md]
"""

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.actif import Portefeuille  # noqa: E402
from src.v5 import conventions as cv, strategies as stg  # noqa: E402
from src.v5.courbes_marche import courbe_eiopa  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402

N = "ABC"
COURT = {"passive": "Passive", "reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}
SENS = {"reaction_onc_max": "Réaction forte (ONC max.)", "reference_immediate": "Transmission immédiate des taux", "defaut_bloc_souverain": "Défaut corrélé par bloc souverain"}
SENS_RACHAT = {"rachats_hausse": "choc de hausse des rachats", "rachats_baisse": "choc de baisse des rachats", "rachat_massif": "rachat massif de 40 %"}
BASES = {"0": "bilan initial, sans apport", "1.0": "capital porté à 100 % du SCR simplifié", "1.5": "capital porté à 150 % du SCR simplifié"}


def f(x, dec=1):
    if round(x, dec) == 0:
        x = 0.0
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def majuscule(t):
    return t[:1].upper() + t[1:]


def charger(nom):
    return json.loads((RACINE / "resultats" / nom).read_text(encoding="utf-8"))


ap = argparse.ArgumentParser()
ap.add_argument("--entree", default=str(RACINE / "resultats" / "v5_consolidation.json"))
ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_STRATEGIES.md"))
ARGS = ap.parse_args()
C = json.loads(Path(ARGS.entree).read_text(encoding="utf-8"))
D = stg.charger()
LECT = D["lecture"]
CODES = C["strategies"]
AUTRES = [c for c in CODES if c != "passive"]
M = charger("v5_strategies_mecanismes.json")
DIST = charger("v5_effet_distribution.json")["resultats"]
SYN = charger("v5_synthese.json")["prudentiel"]
ANC = charger("v5_strategies.json")
RE_EXIGE = D["rentabilite_reelle"]["rendement_exige"]["valeur"]


def pru(p, c="passive"):
    return C["prudentiel"][f"{p}|{c}"]


def x0(p, c="passive"):
    return pru(p, c)["apport_0"]


def cap(p, c="passive"):
    return C["capital"][f"{p}|{c}"]


def rn(p, c, base):
    return C["risque_neutre"][f"{p}|{c}|{base}"]


def re_(p, c, base):
    return C["reel"][f"{p}|{c}|{base}"]


def ecart(p, c, base):
    e = C["ecarts"][f"{p}|{c}|{base}"]
    return e["ecart_moyen"], e["demi_intervalle_95"]


def scr_ref(p):
    return x0(p)["scr"]


def ic(i, dec=1, echelle=1.0):
    return f"[{f(echelle * i['q025'], dec)} ; {f(echelle * i['q975'], dec)}]"


def lecture_valeur(p, c, base):
    """Significativité statistique (intervalle apparié) et importance économique (seuil en % du SCR)."""
    m, h = ecart(p, c, base)
    if abs(m) <= h:
        return "non significatif"
    return "important" if abs(m) >= LECT["valeur_nette_pct_scr"] * scr_ref(p) else "significatif, non important"


L = []
A = L.append

# ------------------------------------------------------------------------------------------------
A("# V5 : capital et stratégies ALM, comparaison consolidée\n")
A(f"Généré par `scripts/v5_rapport_strategies.py` depuis `resultats/v5_consolidation.json` (`scripts/v5_consolidation.py`). Unités fictives : 1 unité = 10 M€. "
  f"Vue prudentielle simplifiée : {f(C['n_scenarios_prudentiel'], 0)} scénarios, base avec VA, incertitude par {f(C['tirages_reechantillonnage'], 0)} rééchantillonnages des paires antithétiques. "
  f"Risque neutre et probabilité réelle : {f(C['n_scenarios'], 0)} scénarios. Conventions centrales : `docs/V5_SYNTHESE_AVANT_OPTIMISATION.md`, section 1. "
  "Synthèse courte : `docs/V5_SYNTHESE_STRATEGIES.md`. **Profils fictifs. Analyse exploratoire, conditionnelle aux hypothèses : ce n'est pas une recommandation.**\n")
A("**Aucun indicateur de ce document n'est un ratio réglementaire.** L'« indicateur de couverture simplifié » est un calcul pédagogique inspiré de la formule standard, sans mesure transitoire, sans modèle interne et sans les modules non modélisés (section 9).\n")
A("**ACPR n° 185** : la page officielle (https://acpr.banque-france.fr/en/node/1925405) et le PDF n'ont pas pu être consultés. Aucun chiffre n'en est tiré ; les repères de place cités ailleurs viennent de l'ACPR n° 181 et, pour le 30/06/2026, de chiffres repris par la presse. Les profils ne sont pas ajustés pour reproduire la moyenne sectorielle.\n")
A("**Lecture des écarts.** Un écart à la gestion passive est *statistiquement significatif* s'il dépasse son intervalle de confiance apparié à 95 % (mêmes scénarios pour toutes les stratégies). Il est *économiquement important* s'il dépasse aussi un seuil fixé avant la lecture des résultats "
  f"(`data/v5/strategies/strategies.json`, rubrique `lecture`) : {pct(LECT['valeur_nette_pct_scr'], 0)} du SCR simplifié du profil pour la valeur nette et l'apport, {f(1e4 * LECT['rendement_fonds_propres_pt'], 0)} pb pour le rendement des fonds propres, "
  f"{f(LECT['ecart_taux_servi_pb'], 0)} pb pour le taux servi, {f(1e4 * LECT['taux_rachat_pt'], 0)} pb pour le taux de rachat, {f(100 * LECT['probabilite_apport_pt'], 1)} point pour une probabilité d'apport, {pct(LECT['moins_values_realisees_pct_scr'], 0)} du SCR pour les moins-values réalisées.\n")

# ------------------------------------------------------------------------------------------------
A("## 1. SCR et MCR simplifiés (gestion passive, bilan initial)\n")
A("### 1.1 Des fonds propres comptables aux fonds propres de niveau 1\n")
A("| | A | B | C |\n| --- | ---: | ---: | ---: |")
walk = {}
for p in N:
    h = stg.appliquer_strategie(cv.appliquer(hypotheses_profil(p), C["reference"], rachat_structurel="acpr"), "passive")
    port = Portefeuille(h, credit=cv.credit_valorisation(C["credit"]))
    c0 = courbe_eiopa()
    x, b = x0(p), h["bilan_initial"]
    walk[p] = {"fp": b["fonds_propres"] + b["reserve_capitalisation"], "pmvl_obl": port.vm_obligations(c0) - port.vnc_obligations(),
               "pvl_act": port.actions_vm - port.actions_vnc, "prov_moins_be": b["pm"] + b["ppb"] - x["be"], "mr": x["marge_de_risque"],
               "fe": x["fonds_excedentaires"], "idp": x["impots_differes_passif"], "of": x["fonds_propres_niveau_1"],
               "fp_pct_pm": b["fonds_propres"] / b["pm"], "mv_pct_vnc": -(port.vm_obligations(c0) - port.vnc_obligations()) / port.vnc_obligations()}
    w = walk[p]
    assert abs(w["fp"] + w["pmvl_obl"] + w["pvl_act"] + w["prov_moins_be"] - w["mr"] + w["fe"] - w["idp"] - w["of"]) < 1e-6, p
for lib, k in [("Fonds propres comptables et réserve de capitalisation", "fp"), ("Moins-values latentes obligataires", "pmvl_obl"),
               ("Plus-values latentes actions", "pvl_act"), ("PM + PPB - BE (base avec VA)", "prov_moins_be"), ("- Marge de risque (6 %)", "mr"),
               ("+ Fonds excédentaires", "fe"), ("- Impôts différés passifs", "idp"), ("**Fonds propres de niveau 1**", "of")]:
    A(f"| {lib} | " + " | ".join(f((-1 if k in ('mr', 'idp') else 1) * walk[p][k]) for p in N) + " |")
A("| Intervalle à 95 % des fonds propres de niveau 1 (erreur Monte-Carlo) | " + " | ".join(ic(pru(p)["incertitude_apport_0"]["of"]) for p in N) + " |")
A("\nIdentité vérifiée par le générateur : actif - BE - marge de risque + fonds excédentaires - impôts différés passifs = somme des lignes ci-dessus.\n")

A("### 1.2 Le SCR simplifié et ce qui le détermine\n")
A("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for lib, g in [("Taux (sens retenu)", lambda x: x["scr_net"]["taux"]), ("Actions (39 %)", lambda x: x["scr_net"]["actions"]), ("Spread (part non souveraine)", lambda x: x["scr_net"]["spread"]),
               ("Marché après diversification", lambda x: x["scr_net"]["marche"]), ("Rachat (sens retenu)", lambda x: x["scr_net"]["rachat"]),
               ("Mortalité + frais", lambda x: x["scr_net"]["mortalite"] + x["scr_net"]["frais"]), ("Vie après diversification", lambda x: x["scr_net"]["vie"]),
               ("BSCR net (après actions de gestion)", lambda x: x["scr_net"]["bscr"]), ("BSCR brut (FDB figées)", lambda x: x["scr_brut"]["bscr"]),
               ("Ajustement pour absorption par les FDB", lambda x: x["ajustement_tp"]), ("Risque opérationnel", lambda x: x["risque_operationnel"]),
               ("Ajustement pour impôts différés", lambda x: x["ajustement_impots_differes"]), ("**SCR simplifié**", lambda x: x["scr"])]:
    A(f"| {lib} | " + " | ".join(f(g(x0(p))) for p in N) + " |")
A("| Intervalle à 95 % du SCR | " + " | ".join(ic(pru(p)["incertitude_apport_0"]["scr"]) for p in N) + " |")
A("| **Indicateur de couverture simplifié du SCR** | " + " | ".join(pct(x0(p)['indicateur_couverture_scr'], 0) for p in N) + " |")
A("| Intervalle à 95 % de l'indicateur | " + " | ".join(ic(pru(p)["incertitude_apport_0"]["ratio"], 0, 100) + " %" for p in N) + " |")
A("| Insuffisance (SCR - fonds propres de niveau 1) | " + " | ".join(f(x0(p)['scr'] - x0(p)['fonds_propres_niveau_1']) for p in N) + " |")
A("")
A("**Ce qui détermine les insuffisances :**\n")
for p in N:
    x, w = x0(p), walk[p]
    rach = max(SENS_RACHAT, key=lambda k: x["pertes_nettes"][k])
    plafond = x["scr_brut"]["bscr"] - x["scr_net"]["bscr"] > x["fdb"] - x["fonds_excedentaires"] + 1e-9
    A(f"- **{p}** : fonds propres comptables de {pct(w['fp_pct_pm'])} de la PM, moins-values obligataires latentes de {pct(w['mv_pct_vnc'])} de la VNC obligataire ({f(w['pmvl_obl'])}), "
      f"partiellement compensées par l'écart provisions - BE ({f(w['prov_moins_be'])}) ; marge de risque de {f(w['mr'])}. "
      f"SCR dominé par le spread ({f(x['scr_net']['spread'])}), les actions ({f(x['scr_net']['actions'])}) et le rachat ({f(x['scr_net']['rachat'])}, {SENS_RACHAT[rach]}). "
      + ("L'absorption par les FDB atteint son plafond (FDB - fonds excédentaires) : le SCR dépend directement du niveau des FDB." if plafond else "L'absorption par les FDB n'atteint pas son plafond."))
A("")

A("### 1.3 Le MCR : formule linéaire, corridor et minimum absolu\n")
A("MCR linéaire = max(0 ; 3,7 % x (BE - FDB) - 5,2 % x (FDB - fonds excédentaires)) ; MCR combiné = MCR linéaire encadré entre 25 % et 45 % du SCR ; MCR = max(MCR combiné ; 0,4 unité). "
  "Chaque terme est calculé, puis comparé au corridor et au minimum absolu (test `test_mcr_encadre`, qui couvre les quatre contraintes possibles).\n")
A("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for lib, g in [("3,7 % x (BE - FDB)", lambda x: x["mcr_detail"]["termes_lineaires"]["garanties"]), ("- 5,2 % x FDB hors fonds excédentaires", lambda x: x["mcr_detail"]["termes_lineaires"]["fdb"]),
               ("MCR linéaire", lambda x: x["mcr_detail"]["lineaire"]), ("25 % du SCR", lambda x: x["mcr_detail"]["plancher_25"]), ("45 % du SCR", lambda x: x["mcr_detail"]["plafond_45"]),
               ("Minimum absolu", lambda x: x["mcr_detail"]["minimum_absolu"]), ("**MCR simplifié**", lambda x: x["mcr"])]:
    A(f"| {lib} | " + " | ".join(f(g(x0(p))) for p in N) + " |")
A("| Contrainte active | " + " | ".join(x0(p)['mcr_detail']['contrainte_active'] for p in N) + " |")
A("| Indicateur de couverture simplifié du MCR [IC 95 %] | " + " | ".join(pct(x0(p)['indicateur_couverture_mcr'], 0) + " " + ic(pru(p)["incertitude_apport_0"]["ratio_mcr"], 0, 100) for p in N) + " |")
A("")
plancher = [p for p in N if x0(p)["mcr_detail"]["contrainte_active"] == "plancher de 25 % du SCR"]
A("**Lecture.** " + (f"Pour {', '.join(plancher)}, le MCR linéaire est inférieur à 25 % du SCR : le plancher s'applique, et l'indicateur MCR vaut alors quatre fois l'indicateur SCR. " if plancher else "")
  + "Le terme des FDB abaisse le MCR linéaire d'autant plus que la participation future est importante. "
  + ("Le minimum absolu ne joue pour aucun profil. " if all(x0(p)["mcr_detail"]["contrainte_active"] != "minimum absolu" for p in N) else "Le minimum absolu joue pour au moins un profil. ")
  + ("Les indicateurs MCR élevés ne témoignent donc pas d'une marge de sécurité propre : ils reflètent le plancher du corridor." if plancher else "") + "\n")

A("### 1.4 Rapprochement avec les calculs précédents\n")
A("| | A | B | C |\n| --- | ---: | ---: | ---: |")
A(f"| Indicateur SCR, synthèse avant optimisation ({f(SYN['A|avec_va']['n_scenarios'], 0)} scénarios, sans distribution) | " + " | ".join(pct(SYN[f'{p}|avec_va']['indicateur_couverture_scr'], 0) for p in N) + " |")
A(f"| Indicateur SCR, première comparaison des stratégies ({f(ANC['n_scenarios_prudentiel'], 0)} scénarios) | " + " | ".join(pct(ANC['capital'][p]['apport_0']['indicateur_couverture_scr'], 0) for p in N) + " |")
A(f"| Indicateur SCR, ce document ({f(C['n_scenarios_prudentiel'], 0)} scénarios) [IC 95 %] | " + " | ".join(pct(x0(p)['indicateur_couverture_scr'], 0) + " " + ic(pru(p)["incertitude_apport_0"]["ratio"], 0, 100) for p in N) + " |")
A("| Effet de la politique de distribution sur le BE (mêmes scénarios) | " + " | ".join(f"{f(DIST[f'{p}|initial']['ecart_be'])} ± {f(DIST[f'{p}|initial']['demi_intervalle_95'])}" for p in N) + " |")
A("")
A("Les écarts entre ces trois calculs viennent de l'erreur Monte-Carlo du niveau du BE (même générateur, jeux de scénarios de tailles différentes) et de la politique de distribution introduite avec les stratégies. "
  "Mécanisme de cette dernière : la participation est calculée sur la quote-part des produits financiers, au rendement comptable moyen de tout l'actif. Sans distribution, les résultats conservés sont réinvestis aux taux du marché, qui dépassent en moyenne les coupons anciens dans les scénarios risque neutre ; "
  "le rendement comptable moyen monte, et les assurés en reçoivent leur quote-part. La distribution supprime cet effet : taux servi un peu plus bas les années de hausse des taux, FDB et BE plus faibles"
  + (f" (profil B, année 10 : rendement comptable {f(1e4 * DIST['B|initial']['ecart_rendement_comptable_10'], 0)} pb, taux servi {f(1e4 * DIST['B|initial']['ecart_taux_servi_10'], 0)} pb)" if "ecart_rendement_comptable_10" in DIST["B|initial"] else "")
  + ". Aucun paramètre n'a été ajusté pour se rapprocher d'un repère de place.\n")

# ------------------------------------------------------------------------------------------------
A("## 2. Capital nécessaire, par stratégie\n")
A("L'apport est versé en trésorerie à l'ouverture et investi ensuite au prix du marché ; le portefeuille existant ne change pas. Pour chaque stratégie, les fonds propres de niveau 1 et le SCR sont calculés pour deux apports, puis interpolés linéairement. "
  "L'intervalle à 95 % vient du rééchantillonnage des paires de scénarios (mêmes rééchantillons pour les deux apports, pour tous les chocs et pour toutes les stratégies).\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Stratégie | Indicateur SCR sans apport [IC 95 %] | Apport pour 100 % [IC 95 %] | Écart à la passive [IC 95 %] | Apport pour 150 % [IC 95 %] | Écart à la passive [IC 95 %] |\n| --- | ---: | ---: | ---: | ---: | ---: |")
    for c in CODES:
        k, x = cap(p, c), pru(p, c)
        A(f"| {COURT[c]} | {pct(x['apport_0']['indicateur_couverture_scr'], 0)} {ic(x['incertitude_apport_0']['ratio'], 0, 100)} | "
          f"{f(k['besoin']['1.0'])} {ic(k['incertitude']['1.0'])} | " + ("-" if c == "passive" else f"{f(k['besoin']['1.0'] - cap(p)['besoin']['1.0'])} {ic(k['ecart_passive']['1.0'])}") + " | "
          f"{f(k['besoin']['1.5'])} {ic(k['incertitude']['1.5'])} | " + ("-" if c == "passive" else f"{f(k['besoin']['1.5'] - cap(p)['besoin']['1.5'])} {ic(k['ecart_passive']['1.5'])}") + " |")
    A("")
A("**Vérification de l'interpolation** (vue prudentielle recalculée à l'apport obtenu, mêmes scénarios). L'erreur d'apport est estimée au premier ordre : "
  "(indicateur obtenu - cible) x SCR obtenu / (pente des fonds propres - cible x pente du SCR) ; positive, l'apport interpolé est trop élevé.\n")
A("| Profil, stratégie, cible | Apport interpolé | Indicateur obtenu | Erreur d'apport estimée |\n| --- | ---: | ---: | ---: |")
err_interp = {}
for cle, v in C["verification"].items():
    p, c, t = cle.split("|")
    k = cap(p, c)
    err_interp[cle] = (v["indicateur_couverture_scr"] - float(t)) * v["scr"] / (k["pente_fonds_propres"] - float(t) * k["pente_scr"])
    A(f"| {p}, {COURT[c]}, {pct(float(t), 0)} | {f(v['apport'])} | {pct(v['indicateur_couverture_scr'], 1)} | {f(err_interp[cle])} |")
A("")
pire = max(err_interp, key=lambda k: abs(err_interp[k]))
hors_a = [k for k in err_interp if not k.startswith("A|")]
demi_ic = max((cap(p, c)["incertitude"][t]["q975"] - cap(p, c)["incertitude"][t]["q025"]) / 2 for p in N for c in CODES for t in ("1.0", "1.5"))
cout_unitaire = (rn("A", "passive", "0")["valeur_nette"] - rn("A", "passive", "1.0")["valeur_nette"]) / cap("A")["besoin"]["1.0"]
demi_ic_min = min((cap(p, c)["incertitude"][t]["q975"] - cap(p, c)["incertitude"][t]["q025"]) / 2 for p in N for c in CODES for t in ("1.0", "1.5"))
sans_apport = [(p, c) for p in N for c in CODES if x0(p, c)["indicateur_couverture_scr"] >= 1.0]
A(("**Aucune stratégie n'atteint 100 % sans apport, pour aucun profil.** " if not sans_apport else "Stratégies à 100 % sans apport : " + ", ".join(f"{COURT[c]} ({p})" for p, c in sans_apport) + ". ")
  + f"Deux erreurs entourent les besoins d'apport. L'erreur Monte-Carlo (demi-largeur des intervalles ci-dessus) va de {f(demi_ic_min)} à {f(demi_ic)} unités. "
  + (f"L'erreur d'interpolation atteint au plus {f(max(abs(err_interp[k]) for k in hors_a))} unité pour B et C ; elle est plus forte pour A ({f(abs(err_interp[pire]))} au plus, "
     f"pour « {COURT[pire.split('|')[1]]} »), dont la relation entre apport et indicateur n'est pas linéaire (plafond de l'absorption par les FDB, section 8). " if pire.startswith("A|")
     else f"L'erreur d'interpolation atteint au plus {f(abs(err_interp[pire]))} unité sur les points vérifiés. ")
  + f"Les apports utilisés ensuite sont les apports interpolés, non corrigés, pour garder une règle identique pour toutes les stratégies. Ces erreurs pèsent peu sur la valeur : le coût net de portage de la gestion passive est d'environ {f(cout_unitaire, 2)} par unité d'apport pour A (section 2.1), soit moins de {f(cout_unitaire * max(abs(e) for e in err_interp.values()), 1)} de valeur nette pour l'erreur d'interpolation la plus forte. "
  "Les **écarts** de besoin entre stratégies, calculés sur les mêmes rééchantillons, sont plus précis que les besoins eux-mêmes.\n")

A("### 2.1 Fonds propres existants, apports, distributions et coûts de financement\n")
A("Quatre flux sont tenus séparément : (1) les fonds propres existants, déjà dans l'actif d'ouverture ; (2) les apports, initial et ultérieurs (le modèle apporte la trésorerie manquante quand tous les actifs ont été vendus), qui sont des sorties pour l'actionnaire et jamais des produits ; "
  "(3) les distributions : les fonds propres comptables sont ramenés chaque année à leur niveau d'ouverture rapporté à la PM, apport compris, l'excédent étant versé l'année suivante (la variante « rétention » n'en verse que la moitié) ; "
  "(4) le coût de financement : impôt sur les revenus du capital immobilisé et participation sur ces revenus. Aucun coût d'émission n'est appliqué. "
  "Valeur nette = actif - BE - apport initial - VA de l'impôt = VA des dividendes + VA du résidu final - apport initial - VA des apports ultérieurs - VA de l'impôt (à l'écart Monte-Carlo près).\n")
A("| Profil, base (gestion passive) | VA des dividendes | VA du résidu final | - Apport initial | - VA des apports ultérieurs | - VA de l'impôt | Écart Monte-Carlo | **Valeur nette** | Coût net de portage de l'apport |\n| --- | " + " | ".join("---:" for _ in range(8)) + " |")
for p in N:
    for base in ("0", "1.0", "1.5"):
        q = rn(p, "passive", base)
        assert abs(q["va_dividendes"] + q["va_residuel_final"] - q["apport_initial"] - q["va_apports_ulterieurs"] - q["va_impots"] + q["fuite"] - q["valeur_nette"]) < 1e-6
        cout = "-" if base == "0" else f(rn(p, "passive", "0")["valeur_nette"] - q["valeur_nette"])
        A(f"| {p}, {BASES[base]} | {f(q['va_dividendes'])} | {f(q['va_residuel_final'])} | {f(-q['apport_initial'])} | {f(-q['va_apports_ulterieurs'])} | {f(-q['va_impots'])} | {f(q['fuite'])} | **{f(q['valeur_nette'])}** | {cout} |")
A("")
A("Le coût net de portage est la valeur nette perdue en recapitalisant : impôt et participation sur les revenus du capital supplémentaire, diminués de la baisse des apports ultérieurs. Positif, il signifie que l'apport réduit la valeur risque neutre de l'actionnaire, même s'il est nécessaire pour respecter la contrainte.\n")

# ------------------------------------------------------------------------------------------------
A("## 3. Comparaison sur une base de capital commune\n")
A("| Code | Stratégie | Règles |\n| --- | --- | --- |")
for c in CODES:
    v = D["strategies"][c]
    A(f"| `{c}` | {v['libelle']} | {v['description']} |")
A("\n**Base de capital commune** : pour une cible donnée (100 % ou 150 % du SCR simplifié), chaque stratégie reçoit l'apport qui porte *son propre* indicateur à la cible (section 2). La valeur nette déduit cet apport : une stratégie qui consomme plus de capital le paie. "
  "Mêmes bilans initiaux, mêmes scénarios économiques et mêmes tirages de défaut pour toutes les stratégies. Portefeuille fermé : aucune collecte nouvelle ; la collecte sensible au taux servi est traitée dans `docs/V5_COLLECTE.md`.\n")
for base in ("1.0", "1.5"):
    A(f"### 3.{1 if base == '1.0' else 2} {majuscule(BASES[base])}\n")
    for p in N:
        A(f"**Profil {p}**\n")
        A("| Stratégie | Apport | Valeur nette (RN) | Écart à la passive ± IC 95 % | Lecture | Rendement des fonds propres 1-10 (réel) | Dividendes 1-10 (réel) | Probabilité d'apport ultérieur sur 60 ans (réel) | Taux servi 1-10 (réel) | Écart à la référence (réel) | Rachat 1-10 (RN / réel) | Rachat annuel max. q99 (réel) | Moins-values réalisées q99 (réel) |\n| --- | " + " | ".join("---:" for _ in range(12)) + " |")
        for c in CODES:
            q, r = rn(p, c, base), re_(p, c, base)
            m, h = ecart(p, c, base)
            A(f"| {COURT[c]} | {f(q['apport_initial'])} | {f(q['valeur_nette'])} | " + ("-" if c == "passive" else f"{f(m)} ± {f(h)}") + f" | {'-' if c == 'passive' else lecture_valeur(p, c, base)} | "
              f"{pct(r['rendement_fonds_propres_1_10_agrege'])} | {f(r['dividendes_1_10_moyen'])} | {pct(r['probabilite_apport_horizon'], 1)} | {pct(r['taux_servi_moyen_1_10'], 2)} | {f(1e4 * r['ecart_taux_servi_reference_1_10'], 0)} pb | "
              f"{pct(q['taux_rachat_moyen_1_10'])} / {pct(r['taux_rachat_moyen_1_10'])} | {pct(r['taux_rachat_max_1_10_q99'], 0)} | {f(r['moins_values_realisees_1_10_q99'])} |")
        A("")
A(f"Rendement des fonds propres : résultat net d'impôt rapporté aux fonds propres comptables d'ouverture de chaque année, agrégé sur les scénarios, à comparer à un rendement exigé fictif de {pct(RE_EXIGE, 0)}. Les indicateurs réels n'ont pas d'intervalle apparié ; leurs écarts entre stratégies portent sur les mêmes scénarios.\n")

# ------------------------------------------------------------------------------------------------
A("## 4. Réinvestissement progressif : significativité et importance\n")
ctl = C["controle_reinvestissement"]
mA, hA = ecart("A", "reinvestissement_progressif", "1.0")
seuil_A = LECT["valeur_nette_pct_scr"] * scr_ref("A")
A("Écart de valeur nette à la gestion passive ± intervalle apparié à 95 % :\n")
A("| Profil | Bilan initial | Base 100 % | Base 150 % |\n| --- | ---: | ---: | ---: |")
for p in N:
    A(f"| {p} | " + " | ".join(f"{f(ecart(p, 'reinvestissement_progressif', b)[0], 2)} ± {f(ecart(p, 'reinvestissement_progressif', b)[1], 2)}" for b in ("0", "1.0", "1.5")) + " |")
A("")
A(f"Contrôle sur des tirages indépendants (profil A, base 100 %, {f(ctl['n_scenarios'], 0)} scénarios, autres graines pour les scénarios et les défauts) : {f(ctl['ecart_moyen'], 2)} ± {f(ctl['demi_intervalle_95'], 2)}.\n")
confirme = abs(ctl["ecart_moyen"]) > ctl["demi_intervalle_95"] and ctl["ecart_moyen"] * mA > 0
A(f"- **Statistiquement**, l'écart du profil A sur la base 100 % ({f(mA, 2)} ± {f(hA, 2)}) " + ("est significatif" if abs(mA) > hA else "n'est pas significatif")
  + (" et se retrouve sur des tirages indépendants." if confirme else " ; le contrôle sur tirages indépendants ne le confirme pas avec la même netteté."))
A(f"- **Économiquement**, il est faible : {pct(abs(mA) / x0('A')['be'], 2)} du BE et {pct(abs(mA) / scr_ref('A'), 1)} du SCR simplifié, pour un seuil d'importance de {f(seuil_A)} ({pct(LECT['valeur_nette_pct_scr'], 0)} du SCR). "
  f"Il est aussi petit devant l'incertitude du besoin d'apport du profil (intervalle de largeur {f(cap('A')['incertitude']['1.0']['q975'] - cap('A')['incertitude']['1.0']['q025'])}) et devant les écarts des politiques de taux servi.")
A("- **Mécanisme** : l'écart n'apparaît que lorsque des achats obligataires importants passent par l'échelle de maturités, comme le réinvestissement de l'apport de A ; sur le bilan initial, les flux réinvestis sont faibles devant le stock obligataire.")
A("- **Conclusion** : " + ("le réinvestissement progressif est statistiquement distinguable de la gestion passive pour A recapitalisé, mais pas économiquement distinguable avec les seuils retenus." if abs(mA) > hA and abs(mA) < seuil_A
                          else "voir les chiffres ci-dessus ; la conclusion de la première comparaison est à revoir.") + "\n")

# ------------------------------------------------------------------------------------------------
A("## 5. Deux variantes : politique compétitive préservant la PPB, rétention de capital\n")
A("Politique compétitive préservant la PPB : même cible que la politique compétitive (la référence), mais reprises volontaires limitées à 25 % par an de la part de la PPB qui dépasse la moitié du ratio PPB / PM d'ouverture. "
  "Rétention : règles de la gestion passive, la moitié seulement de l'excédent annuel de fonds propres est distribuée. Base 100 %, écarts à la gestion passive :\n")
A("| Profil | Stratégie | Valeur nette ± IC | Lecture | Apport à 100 % | Écart du taux servi à la référence (réel) | Rachat 1-10 RN | Probabilité d'apport sur 60 ans (réel) | Rendement des fonds propres (réel) |\n| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |")
for p in N:
    for c in ("taux_servi_competitif", "taux_servi_competitif_preservant", "distribution_retention"):
        m, h = ecart(p, c, "1.0")
        r0, r1 = re_(p, "passive", "1.0"), re_(p, c, "1.0")
        A(f"| {p} | {COURT[c]} | {f(m)} ± {f(h)} | {lecture_valeur(p, c, '1.0')} | {f(cap(p, c)['besoin']['1.0'] - cap(p)['besoin']['1.0'])} | {f(1e4 * (r1['ecart_taux_servi_reference_1_10'] - r0['ecart_taux_servi_reference_1_10']), 0)} pb | "
          f"{f(1e4 * (rn(p, c, '1.0')['taux_rachat_moyen_1_10'] - rn(p, 'passive', '1.0')['taux_rachat_moyen_1_10']), 0)} pb | {f(100 * (r1['probabilite_apport_horizon'] - r0['probabilite_apport_horizon']), 1)} pt | {f(100 * (r1['rendement_fonds_propres_1_10_agrege'] - r0['rendement_fonds_propres_1_10_agrege']), 2)} pt |")
A("")
if any("taux_servi_competitif_preservant" in k for k in M["resultats"]):
    A("Trajectoires risque neutre (bilan initial), gestion passive / compétitive / compétitive préservant la PPB :\n")
    A("| Profil | Année | PPB / PM | Part des scénarios hors zone neutre | Taux de rachat |\n| --- | ---: | ---: | ---: | ---: |")
    for p in N:
        for t in (1, 5, 8, 10, 20):
            v = [M["resultats"][f"{p}|{c}"][str(t)] for c in ("passive", "taux_servi_competitif", "taux_servi_competitif_preservant")]
            A(f"| {p} | {t} | " + " / ".join(pct(x['ppb_pm'], 2) for x in v) + " | " + " / ".join(pct(x['part_hors_zone_neutre'], 0) for x in v) + " | " + " / ".join(pct(x['taux_rachat'], 1) for x in v) + " |")
    A("")
A("**Lecture.**\n")
lig, gain_ts, gain_v, baisse_r = [], [], [], []
for p in N:
    comp, pres = "taux_servi_competitif", "taux_servi_competitif_preservant"
    dv = rn(p, pres, "1.0")["valeur_nette"] - rn(p, comp, "1.0")["valeur_nette"]
    dt = re_(p, pres, "1.0")["ecart_taux_servi_reference_1_10"] - re_(p, comp, "1.0")["ecart_taux_servi_reference_1_10"]
    dr = rn(p, pres, "1.0")["taux_rachat_moyen_1_10"] - rn(p, comp, "1.0")["taux_rachat_moyen_1_10"]
    lig.append(f"{p} : {f(dv)} de valeur, {f(1e4 * dt, 0)} pb de taux servi, {f(1e4 * dr, 0)} pb de rachat")
    gain_ts += [p] if 1e4 * dt >= LECT["ecart_taux_servi_pb"] else []
    gain_v += [p] if dv >= LECT["valeur_nette_pct_scr"] * scr_ref(p) else []
    baisse_r += [p] if -dr >= LECT["taux_rachat_pt"] else []
A("- **Préserver la PPB, par rapport à la politique compétitive de base** (" + " ; ".join(lig) + " ; mêmes scénarios, sans intervalle calculé pour cet écart) : garder une partie de la PPB pour les années où la référence monte "
  + (f"réduit nettement les rachats ({', '.join(baisse_r)})" if baisse_r else "ne réduit pas nettement les rachats")
  + (f" ; le gain d'écart à la référence n'est important que pour {', '.join(gain_ts)}" if gain_ts and len(gain_ts) < 3 else (" et améliore l'écart à la référence" if gain_ts else " ; le gain d'écart à la référence reste sous le seuil"))
  + (f", et la valeur ne s'améliore nettement que pour {', '.join(gain_v)}. " if gain_v and len(gain_v) < 3 else (", et la valeur s'améliore. " if gain_v else ", sans gain de valeur important. "))
  + "Le coût en valeur par rapport à la gestion passive demeure : la politique reste compétitive, donc moins de participation non servie revient à l'actionnaire.")
ret_imp = [p for p in N for b in ("1.0", "1.5") if lecture_valeur(p, "distribution_retention", b) == "important"]
A("- **Rétention** : la valeur baisse un peu (impôt et participation sur les revenus du capital conservé, rendement comptable relevé et partagé avec les assurés, section 1.4) ; "
  + (f"l'écart ne dépasse le seuil d'importance que pour {', '.join(sorted(set(ret_imp)))} à 150 %, au niveau du seuil. " if ret_imp else "l'écart reste sous le seuil d'importance. ")
  + "Le rendement des fonds propres baisse davantage, car le capital conservé dilue le résultat. Le bénéfice attendu de la rétention, une couverture plus élevée dans les années suivantes, n'est pas mesuré : le modèle ne projette pas le SCR. "
  "La rétention ne réduit pas l'apport initial nécessaire ; elle réduit un peu la probabilité d'apport ultérieur.\n")

# ------------------------------------------------------------------------------------------------
A("## 6. Matrice de décision exploratoire\n")
A("Écarts à la gestion passive sur la base de capital commune, A / B / C. En gras : écart important (au-delà du seuil de lecture) ; « ns » : écart non significatif (intervalle apparié pour la valeur, intervalle de rééchantillonnage pour l'apport ; les écarts en probabilité réelle et de rachat n'ont pas d'intervalle). "
  "« Écart de valeur robuste » : écart de valeur important, de même signe pour les deux cibles de capital et sous les trois sensibilités de la section 7.\n")
DIM = [("Valeur actionnaire (RN)", lambda p, c, b: (ecart(p, c, b)[0], ecart(p, c, b)[1], LECT["valeur_nette_pct_scr"] * scr_ref(p)), lambda x: f(x)),
       ("Rentabilité (réel)", lambda p, c, b: (re_(p, c, b)["rendement_fonds_propres_1_10_agrege"] - re_(p, "passive", b)["rendement_fonds_propres_1_10_agrege"], 0.0, LECT["rendement_fonds_propres_pt"]), lambda x: f(100 * x, 2) + " pt"),
       ("Compétitivité : taux servi (réel)", lambda p, c, b: (re_(p, c, b)["ecart_taux_servi_reference_1_10"] - re_(p, "passive", b)["ecart_taux_servi_reference_1_10"], 0.0, LECT["ecart_taux_servi_pb"] / 1e4), lambda x: f(1e4 * x, 0) + " pb"),
       ("Rachats (RN)", lambda p, c, b: (rn(p, c, b)["taux_rachat_moyen_1_10"] - rn(p, "passive", b)["taux_rachat_moyen_1_10"], 0.0, LECT["taux_rachat_pt"]), lambda x: f(1e4 * x, 0) + " pb"),
       ("Liquidité : moins-values réalisées q99 (réel)", lambda p, c, b: (re_(p, c, b)["moins_values_realisees_1_10_q99"] - re_(p, "passive", b)["moins_values_realisees_1_10_q99"], 0.0, LECT["moins_values_realisees_pct_scr"] * scr_ref(p)), lambda x: f(x)),
       ("Capital : apport nécessaire", lambda p, c, b: (cap(p, c)["besoin"][b] - cap(p)["besoin"][b], cap(p, c)["ecart_passive"][b], LECT["apport_pct_scr"] * scr_ref(p)), lambda x: f(x)),
       ("Capital : probabilité d'apport ultérieur sur 60 ans (réel)", lambda p, c, b: (re_(p, c, b)["probabilite_apport_horizon"] - re_(p, "passive", b)["probabilite_apport_horizon"], 0.0, LECT["probabilite_apport_pt"]), lambda x: f(100 * x, 1) + " pt")]


def cellule(c, g, fmt, b):
    sortie = []
    for p in N:
        m, h, seuil = g(p, c, b)
        t = fmt(m)
        # h : demi-intervalle apparié (valeur) ou intervalle de rééchantillonnage (apport) ; 0 si non mesuré
        ns = (h["q025"] <= 0.0 <= h["q975"]) if isinstance(h, dict) else (h and abs(m) <= h)
        if ns:
            t += " ns"
        elif abs(m) >= seuil:
            t = f"**{t}**"
        sortie.append(t)
    return " / ".join(sortie)


def robuste(p, c):
    m1, h1 = ecart(p, c, "1.0")
    m2, h2 = ecart(p, c, "1.5")
    seuil = LECT["valeur_nette_pct_scr"] * scr_ref(p)
    if not (abs(m1) > max(h1, seuil) and abs(m2) > max(h2, seuil) and m1 * m2 > 0):
        return False
    return all(C["sensibilites"][f"{p}|{c}|{s}"]["ecart_moyen"] * m1 > 0 and abs(C["sensibilites"][f"{p}|{c}|{s}"]["ecart_moyen"]) > C["sensibilites"][f"{p}|{c}|{s}"]["demi_intervalle_95"] for s in SENS)


for b in ("1.0", "1.5"):
    A(f"**{majuscule(BASES[b])}**\n")
    A("| Stratégie | " + " | ".join(d[0] for d in DIM) + " | Écart de valeur robuste (profils) |\n| --- | " + " | ".join("---:" for _ in DIM) + " | --- |")
    for c in AUTRES:
        A(f"| {COURT[c]} | " + " | ".join(cellule(c, g, fmt, b) for _, g, fmt in DIM) + " | " + (", ".join(p for p in N if robuste(p, c)) or "aucun profil") + " |")
    A("")
A("Sens de lecture : une valeur, une rentabilité ou un écart de taux servi positifs sont favorables ; des rachats, des moins-values réalisées, un apport ou une probabilité d'apport positifs sont défavorables.\n")

# ------------------------------------------------------------------------------------------------
A("## 7. Sensibilité de la valeur aux hypothèses fragiles (base 100 %)\n")
A("Écart de valeur nette à la gestion passive ± intervalle apparié, avec les apports du centre. Les besoins d'apport ne sont pas recalculés sous chaque sensibilité.\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Stratégie | Centre | " + " | ".join(SENS.values()) + " |\n| --- | ---: | " + " | ".join("---:" for _ in SENS) + " |")
    for c in AUTRES:
        m, h = ecart(p, c, "1.0")
        A(f"| {COURT[c]} | {f(m)} ± {f(h)} | " + " | ".join(f"{f(C['sensibilites'][f'{p}|{c}|{s}']['ecart_moyen'])} ± {f(C['sensibilites'][f'{p}|{c}|{s}']['demi_intervalle_95'])}" for s in SENS) + " |")
    tete = {"centre": max(CODES, key=lambda c: rn(p, c, "1.0")["valeur_nette"])}
    tete.update({s: max(CODES, key=lambda c: C["sensibilites"][f"{p}|{c}|{s}"]["valeur_nette"]) for s in SENS})
    A("\nPlus forte valeur nette : " + " ; ".join(f"{'Centre' if s == 'centre' else SENS[s]} : {COURT[t]}" for s, t in tete.items())
      + (". **Le premier rang change avec les hypothèses.**" if len(set(tete.values())) > 1 else ". Le premier rang ne change pas sous ces trois sensibilités.") + "\n")

# ------------------------------------------------------------------------------------------------
A("## 8. Mécanismes\n")
A("- **Politique de marge** : transfert de la participation non servie vers l'actionnaire, dont le seul coût en portefeuille fermé est le surcroît de rachats dynamiques, borné par la zone neutre et le plafond de la loi de rachat. L'avantage fermé n'est pas, par principe, un majorant : avec une collecte sensible au taux servi, il l'est seulement si la valeur des affaires nouvelles de la politique de marge est inférieure à celle de la gestion passive (`docs/V5_COLLECTE.md`, section 3).")
_m = lambda c, t: M["resultats"][f"B|{c}"][str(t)]
A("- **Politique compétitive** : la PPB est consommée tôt ; quand la référence monte, l'écart sort plus souvent de la zone neutre et les rachats remontent"
  + (f" (profil B, année 8 : PPB de {pct(_m('taux_servi_competitif', 8)['ppb_pm'], 2)} de la PM contre {pct(_m('passive', 8)['ppb_pm'], 2)}, {pct(_m('taux_servi_competitif', 8)['part_hors_zone_neutre'], 0)} des scénarios hors zone neutre contre {pct(_m('passive', 8)['part_hors_zone_neutre'], 0)})"
     if "B|taux_servi_competitif_preservant" in M["resultats"] else "")
  + ". La variante préservant la PPB garde un stock plus élevé les premières années"
  + (f" (année 5 : {pct(_m('taux_servi_competitif_preservant', 5)['ppb_pm'], 2)} contre {pct(_m('taux_servi_competitif', 5)['ppb_pm'], 2)})" if "B|taux_servi_competitif_preservant" in M["resultats"] else "")
  + " ; le plancher ne limite que les reprises volontaires, et la reprise obligatoire des dotations de plus de 8 ans fait ensuite fortement baisser le stock"
  + (f" ({pct(_m('taux_servi_competitif_preservant', 8)['ppb_pm'], 2)} à l'année 8)" if "B|taux_servi_competitif_preservant" in M["resultats"] else "")
  + ", ce qui borne l'effet de la variante (section 5).")
A("- **Repositionnement** : vente au prix de marché, mais la moins-value réalisée passe par la réserve de capitalisation puis par le résultat, tandis que les coupons plus élevés rachetés ensuite reviennent pour au moins 85 % aux assurés : l'actionnaire supporte la perte et partage le gain.")
A("- **Liquidité défensive** : en risque neutre, moins de volatilité réduit le coût des options (garantie et asymétrie de la participation) ; en probabilité réelle, la prime actions fictive est perdue.")
A("- **Rétention de capital** : plus de fonds propres conservés, donc moins d'apports ultérieurs, mais davantage d'impôt sur leurs revenus et un rendement comptable plus élevé partagé avec les assurés (section 1.4).")
xa, xc, xm = x0("A"), x0("A", "taux_servi_competitif"), x0("A", "taux_servi_marge")
A("- **Plafond de l'absorption par les FDB** (profil A) : quand l'absorption atteint son plafond (FDB - fonds excédentaires), le SCR vaut le BSCR brut moins ce plafond, plus le risque opérationnel ; toute baisse des FDB l'augmente à l'unité. "
  f"La politique compétitive abaisse le BSCR brut de A ({f(xc['scr_brut']['bscr'])} contre {f(xa['scr_brut']['bscr'])}) et demande moins de capital ; la politique de marge abaisse les FDB ({f(xm['fdb'])} contre {f(xa['fdb'])}) et en demande davantage. "
  + ("Pour B et C, l'absorption n'est pas plafonnée et la politique de marge demande moins de capital. Le sens de l'effet d'une stratégie sur le capital dépend donc du profil." if all(cap(p, "taux_servi_marge")["besoin"]["1.0"] < cap(p)["besoin"]["1.0"] for p in "BC") else "") + "\n")

# ------------------------------------------------------------------------------------------------
A("## 9. Limites\n")
for x in [
    "**Indicateurs simplifiés** : pas de mesure transitoire, ajustement symétrique nul, modules non modélisés (contrepartie, concentration, immobilier, change), marge de risque probablement surestimée, fonds excédentaires par l'approche simplifiée, impôts différés actifs non reconnus.",
    "**Portefeuille fermé** : aucune collecte nouvelle dans ce document. La collecte sensible au taux servi relatif est traitée dans `docs/V5_COLLECTE.md` (spécification : `docs/V5_SPECIFICATION_COLLECTE.md`).",
    "**Comportement des assurés** : loi de rachat dynamique des V1 à V4 au centre, corridors ONC de 2013 en sensibilité ; aucune donnée 2026 ne calibre la réaction des assurés.",
    "**Stratégies non optimisées** : un jeu de paramètres par famille et deux variantes ; une seule politique de distribution de base.",
    "**Interpolation des besoins d'apport** entre deux points, vérifiée par recalcul pour " + ", ".join(f"{COURT[c][:1].lower() + COURT[c][1:]} ({', '.join(sorted({k.split('|')[0] for k in C['verification'] if k.split('|')[1] == c}))})" for c in CODES if any(k.split('|')[1] == c for k in C["verification"])) + " ; apports interpolés non corrigés ; les sensibilités de la section 7 gardent les apports du centre.",
    "**Probabilité réelle** : taux sans prime de terme, spreads figés, prime actions fictive de 3 %, défauts aux taux historiques ; probabilités de recapitalisation conditionnelles à ces hypothèses ; écarts réels sans intervalle apparié.",
    "**Coûts de financement** : impôt et participation sur les revenus du capital ; ni coût d'émission, ni dette subordonnée, ni prime de rendement exigée intégrée à la valeur risque neutre.",
    "**ACPR n° 185** non lu.",
]:
    A(f"- {x}")
A("")
Path(ARGS.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit :", ARGS.sortie)
