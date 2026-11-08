"""V5.1, audit des conventions : composante technique de la participation et impôt payé dans la
projection, mesurés sur les mêmes scénarios (docs/V5_AUDIT_CONVENTIONS.md).

Usage : python scripts/v5_audit_conventions.py [--n 1000] [--n-prudentiel 2000] [--processus 2]
Écrit resultats/v5_audit_conventions.json (reprise depuis resultats/cache_v5/audit_n{n}/).

1. Gestion passive des trois profils, à l'apport de la V5.1 pour 100 % (resultats/v5_consolidation.json,
   même capital et mêmes données de marché pour les deux conventions) : convention de la V5.0 (participation
   financière seule) contre V5.1 (compte de participation avec sa composante technique) ; valeur nette risque
   neutre, BE, FDB, taux servi, dotations et reprises de PPB ; écarts appariés, scénario par scénario
   (incertitude Monte-Carlo de l'écart de convention). Contrôle : la convention de la V5.1 reproduit la valeur
   de resultats/v5_consolidation.json.
1 bis. Huit stratégies : effet de la correction à capital constant (apport de la V5.1, mêmes scénarios,
   écarts appariés) et écarts à la gestion passive sous les deux conventions.
1 ter. Solde technique débiteur : avec collecte (frais d'acquisition au compte), fréquence des années à solde
   technique négatif, des comptes débiteurs reportés et des compléments ; respect du TMG.
2. Sensibilité de l'écart au niveau des frais de gestion (paramètre fictif), profil B.
3. Impôt payé dans la projection (variante), gestion passive, aux apports de la V5.1 : valeur, BE, taux
   servi, rentabilité des fonds propres en probabilité réelle, vue prudentielle simplifiée.
4. Impôt payé dans la projection, huit stratégies, apports de la V5.1 : écart de valeur nette à la
   gestion passive, comparé à celui de la convention de référence (mêmes scénarios).
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "scripts"))
import v5_consolidation as conso  # noqa: E402
from src.gse import demi_intervalle  # noqa: E402
from src.stochastique import projeter_stochastique  # noqa: E402
from src.v5 import bases, collecte as col, conventions as cv, strategies as stg  # noqa: E402

FRAIS = (0.005, 0.006)  # sensibilité : frais de gestion sur encours (0,4 % au centre, paramètre fictif)


def t_detail(p, code, apport, n, variante, frais=None):
    """Projection risque neutre détaillée : valeur nette par scénario et diagnostics de participation."""
    h = conso.hypotheses(p, code, apport, variante=variante)
    if frais is not None:
        h["passif"]["frais_gestion_encours"] = frais
    credit = cv.credit_valorisation(conso.CREDIT, "sans_va", h["horizon_annees"])
    g, cr = bases.gse(h, "sans_va", credit, n=n)
    res = projeter_stochastique(h, g, credit=cr, detail=True)
    tr, ps = res["trajectoires"], res["par_scenario"]
    T = h["horizon_annees"]
    ans_T, ans = list(range(1, T + 1)), list(range(1, 11))
    lire = lambda col, a=ans: tr[col].unstack("annee")[a].to_numpy()  # noqa: E731
    defl = lire("deflateur", ans_T)
    impots = stg.impots_des_trajectoires(tr, h, ans_T)
    va_impots = (impots * defl).sum(axis=1)
    valeurs = (ps["vm_actif_initial"] - ps["be"]).to_numpy() - h["bilan_initial"].get("apport_initial", 0.0) - va_impots
    pm_debut = tr["pm"].unstack("annee")[[a - 1 for a in ans]].to_numpy()
    dot, rep = lire("dotation_ppb"), lire("reprise_ppb")
    sortie = {
        "valeurs_nettes": valeurs, "be": ps["be"].to_numpy(), "fdb": ps["fdb"].to_numpy(), "fuite": ps["fuite"].to_numpy(),
        "va_impots": va_impots, "va_dividendes": ps["va_dividendes"].to_numpy(),
        "taux_servi_1_10": lire("taux_servi").mean(axis=1),
        "dotation_ppb_pct_pm_1_10": (dot / pm_debut).mean(axis=1), "reprise_ppb_pct_pm_1_10": (rep / pm_debut).mean(axis=1),
        "ppb_pct_pm_10": (tr["ppb"].unstack("annee")[10] / tr["pm"].unstack("annee")[10]).to_numpy(),
        "part_annees_avec_dotation_1_10": (dot > 1e-12).mean(axis=1),
        "abandon_marge_1_10": lire("abandon_marge").sum(axis=1), "complement_tmg_1_10": lire("complement_tmg").sum(axis=1),
        "resultat_avant_impot_1_10": lire("resultat_assureur").sum(axis=1),
    }
    if "pb_minimale" in tr:
        complement = lire("complement_reglementaire_pb")
        sortie["part_annees_avec_complement_1_10"] = (complement > 1e-9).mean(axis=1)
        sortie["complement_pct_pm_1_10"] = (complement / pm_debut).mean(axis=1)
        sortie["solde_debiteur_max"] = tr["solde_debiteur_compte_pb"].unstack("annee").to_numpy().max(axis=1)
    return sortie


def t_debiteur(p, code, apport, n, c0, eta):
    """V5.1 avec collecte : solde technique (chargements - frais, frais d'acquisition des contrats nouveaux
    compris), comptes débiteurs reportés, compléments, TMG (risque neutre, mêmes scénarios)."""
    h = col.appliquer_collecte(conso.hypotheses(p, code, apport), c0, eta)
    credit = cv.credit_valorisation(conso.CREDIT, "sans_va", h["horizon_annees"])
    g, cr = bases.gse(h, "sans_va", credit, n=n)
    tr = projeter_stochastique(h, g, credit=cr, detail=True)["trajectoires"]
    ans = list(range(1, 11))
    lire = lambda col_, a=ans: tr[col_].unstack("annee")[a].to_numpy()  # noqa: E731
    pm_debut = tr["pm"].unstack("annee")[[a - 1 for a in ans]].to_numpy()
    pa, cn = h["passif"], h["collecte"]["contrats_nouveaux"]
    technique = (pa["chargements_encours"] - pa["frais_gestion_encours"]) * pm_debut + (cn["chargement_prime"] - cn["frais_acquisition_prime"]) * lire("primes")
    debit, complement = lire("solde_debiteur_compte_pb"), lire("complement_reglementaire_pb")
    tmg_moyen = (lire("pm_existant", [a - 1 for a in ans]) * pa["tmg"] + lire("pm_nouveaux", [a - 1 for a in ans]) * cn["tmg"]) / pm_debut
    return {"part_annees_solde_technique_negatif_1_10": float((technique < 0).mean()),
            "solde_technique_min_pct_pm": float((technique / pm_debut).min()),
            "part_annees_compte_debiteur_1_10": float((debit > 1e-9).mean()), "compte_debiteur_max": float(debit.max()),
            "part_annees_avec_complement_1_10": float((complement > 1e-9).mean()),
            "ecart_min_taux_servi_tmg_moyen": float((lire("taux_servi") - tmg_moyen).min()),
            "ecart_bilan_max": float(np.nanmax(np.abs(tr["ecart_bilan"].to_numpy())))}


def t_prudentiel(p, code, apport, n, variante):
    r = conso.t_prudentiel(p, code, apport, n, variante)
    return r["resume"]


class Cache(conso.Cache):
    pass


def executer(ex, cache, taches):
    sortie, futurs = {}, {}
    for cle, (fn, args) in taches.items():
        x = cache.lire(cle)
        if x is None:
            futurs[ex.submit(fn, *args)] = cle
        else:
            sortie[cle] = x
    for i, f in enumerate(as_completed(futurs), 1):
        cle = futurs[f]
        sortie[cle] = f.result()
        cache.ecrire(cle, sortie[cle])
        print(f"  {i}/{len(futurs)} {cle}", flush=True)
    return sortie


def stat(x):
    x = np.asarray(x, dtype=float)
    return {"moyenne": float(x.mean()), "demi_intervalle_95": float(demi_intervalle(x))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--n-prudentiel", type=int, default=2000)
    ap.add_argument("--processus", type=int, default=2)
    ap.add_argument("--cache", default=str(RACINE / "resultats" / "cache_v5"))
    a = ap.parse_args()
    v51 = json.loads((RACINE / "resultats" / "v5_consolidation.json").read_text(encoding="utf-8"))
    codes = v51["strategies"]
    collecte_d = col.charger()
    configurations = [(collecte_d["intensites"]["centrale"]["c0"], collecte_d["elasticites"]["moderee"]["eta"]),
                      (collecte_d["intensites"]["forte"]["c0"], collecte_d["elasticites"]["forte"]["eta"])]
    apports_51 = {(p, c): v51["capital"][f"{p}|{c}"]["besoin"]["1.0"] for p in "ABC" for c in codes}
    cache = Cache(Path(a.cache) / f"audit_n{a.n}")
    sortie = {"n_scenarios": a.n, "n_scenarios_prudentiel": a.n_prudentiel,
              "apports_v5_1": {f"{p}|{c}": k for (p, c), k in apports_51.items()}, "frais_sensibilite": list(FRAIS),
              "participation": {}, "participation_strategies": {}, "compte_debiteur": {}, "frais": {}, "impot": {}, "reel_impot": {}, "prudentiel_impot": {}, "strategies_impot": {},
              "controles": {}}

    # La convention de référence (V5.1) à l'apport de la V5.1 sert aux deux audits : participation et impôt.
    taches = {}
    for p in "ABC":
        taches[f"pb|{p}|pb_financiere_seule"] = (t_detail, (p, "passive", apports_51[(p, "passive")], a.n, "pb_financiere_seule"))
        for v in ("reference", "impot_projete"):
            taches[f"impot|{p}|{v}"] = (t_detail, (p, "passive", apports_51[(p, "passive")], a.n, v))
            taches[f"reel|{p}|{v}"] = (conso.t_reel, (p, "passive", apports_51[(p, "passive")], a.n, v))
        taches[f"prudentiel|{p}|impot_projete"] = (t_prudentiel, (p, "passive", apports_51[(p, "passive")], a.n_prudentiel, "impot_projete"))
        for c in codes:
            if c != "passive":
                for v in ("pb_financiere_seule", "reference", "impot_projete"):
                    taches[f"strategie|{p}|{c}|{v}"] = (t_detail, (p, c, apports_51[(p, c)], a.n, v))
            for c0, eta in configurations:
                taches[f"debiteur|{p}|{c}|{c0}|{eta}"] = (t_debiteur, (p, c, apports_51[(p, c)], a.n, c0, eta))
    for fr in FRAIS:
        for v in ("pb_financiere_seule", "reference"):
            taches[f"frais|B|{fr}|{v}"] = (t_detail, ("B", "passive", apports_51[("B", "passive")], a.n, v, fr))
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        res = executer(ex, cache, taches)

    def ligne(x, ref=None):
        out = {k: stat(val) for k, val in x.items() if k != "solde_debiteur_max"}
        if "solde_debiteur_max" in x:
            out["part_scenarios_avec_solde_debiteur"] = float((x["solde_debiteur_max"] > 1e-9).mean())
        if ref is not None:
            for k in ("valeurs_nettes", "be", "fdb", "taux_servi_1_10", "va_impots", "va_dividendes", "ppb_pct_pm_10"):
                out[f"ecart_{k}"] = stat(x[k] - ref[k])
        return out

    for p in "ABC":
        avant, apres = res[f"pb|{p}|pb_financiere_seule"], res[f"impot|{p}|reference"]
        sortie["participation"][p] = {"v5_0": ligne(avant), "v5_1": ligne(apres, avant)}
        ref, imp = res[f"impot|{p}|reference"], res[f"impot|{p}|impot_projete"]
        sortie["impot"][p] = {"reference": ligne(ref), "impot_projete": ligne(imp, ref)}
        sortie["reel_impot"][p] = {v: res[f"reel|{p}|{v}"]["resume"] for v in ("reference", "impot_projete")}
        sortie["prudentiel_impot"][p] = {
            "reference": {k: v51["verification"][f"{p}|passive|1.0"][k] for k in ("indicateur_couverture_scr", "fonds_propres_niveau_1", "scr")},
            "impot_projete": {k: res[f"prudentiel|{p}|impot_projete"][k] for k in ("indicateur_couverture_scr", "fonds_propres_niveau_1", "scr", "be", "fdb")}}
        for c in codes:
            if c == "passive":
                continue
            xr, xi = res[f"strategie|{p}|{c}|reference"]["valeurs_nettes"], res[f"strategie|{p}|{c}|impot_projete"]["valeurs_nettes"]
            sortie["strategies_impot"][f"{p}|{c}"] = {
                "valeur_nette_reference": float(xr.mean()), "valeur_nette_impot_projete": float(xi.mean()),
                "ecart_passive_reference": stat(xr - ref["valeurs_nettes"]), "ecart_passive_impot_projete": stat(xi - imp["valeurs_nettes"])}
    reproduction = 0.0
    for p in "ABC":
        k0 = {c: (res[f"pb|{p}|pb_financiere_seule"], res[f"impot|{p}|reference"]) if c == "passive"
              else (res[f"strategie|{p}|{c}|pb_financiere_seule"], res[f"strategie|{p}|{c}|reference"]) for c in codes}
        pa0, pa1 = k0["passive"]
        for c in codes:
            avant, apres = k0[c]
            v51_k1 = v51["risque_neutre"][f"{p}|{c}|1.0"]["valeur_nette"]
            reproduction = max(reproduction, abs(float(apres["valeurs_nettes"].mean()) - v51_k1))
            sortie["participation_strategies"][f"{p}|{c}"] = {
                "apport_v5_1": apports_51[(p, c)], "valeur_convention_v5_0": float(avant["valeurs_nettes"].mean()), "valeur_v5_1": v51_k1,
                "effet_capital_constant": stat(apres["valeurs_nettes"] - avant["valeurs_nettes"]),
                "ecart_passive_convention_v5_0": stat(avant["valeurs_nettes"] - pa0["valeurs_nettes"]),
                "ecart_passive_v5_1": stat(apres["valeurs_nettes"] - pa1["valeurs_nettes"])}
            for c0, eta in configurations:
                sortie["compte_debiteur"][f"{p}|{c}|{c0}|{eta}"] = res[f"debiteur|{p}|{c}|{c0}|{eta}"]
    for fr in FRAIS:
        avant, apres = res[f"frais|B|{fr}|pb_financiere_seule"], res[f"frais|B|{fr}|reference"]
        sortie["frais"][str(fr)] = {"v5_0": ligne(avant), "v5_1": ligne(apres, avant)}
    sortie["controles"]["ecart_max_reproduction_v5_1"] = reproduction
    chemin = RACINE / "resultats" / "v5_audit_conventions.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("écrit :", chemin, "; reproduction de la V5.1 :", sortie["controles"]["ecart_max_reproduction_v5_1"])


if __name__ == "__main__":
    main()
