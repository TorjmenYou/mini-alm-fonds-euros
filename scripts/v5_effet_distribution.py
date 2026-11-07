"""V5 : effet de la politique de distribution sur le BE d'ouverture (gestion passive).

Usage : python scripts/v5_effet_distribution.py [--n 500] [--processus 2]
Écrit resultats/v5_effet_distribution.json : BE de la base avec VA (celle de la vue prudentielle), avec et
sans politique de distribution, sur les mêmes scénarios, pour le bilan initial et le bilan recapitalisé, et
l'intervalle de confiance du niveau du BE (erreur Monte-Carlo de la vue prudentielle à n scénarios).
Avec la règle de taux servi des V1 à V4, l'assureur renonce à sa marge pour approcher la cible : les
revenus des fonds propres conservés peuvent alors financer une partie du taux servi.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.gse import demi_intervalle  # noqa: E402
from src.stochastique import projeter_stochastique  # noqa: E402
from src.v5 import bases, conventions as cv, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402

CREDIT, REFERENCE = "k70_granulaire_correle", "taux_servi_marche"
ANNEES = (5, 10, 20)


def be_par_scenario(p, apport, distribution, n):
    h = stg.appliquer_strategie(cv.appliquer(hypotheses_profil(p), REFERENCE, "sans_va", rachat_structurel="acpr"), "passive", apport)
    h["comportement"] = cv.comportement(REFERENCE, "avec_va")
    if not distribution:
        h["strategie_alm"].pop("distribution")
    g, cr = bases.gse(h, "avec_va", cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=n)
    res = projeter_stochastique(h, g, credit=cr, detail=True)
    ps, tr = res["par_scenario"], res["trajectoires"]
    moyennes = {col: tr[col].groupby(level="annee").mean() for col in ("rendement_comptable", "taux_servi")}
    return ps["be"].to_numpy(), ps["fdb"].to_numpy(), {col: {t: float(m.loc[t]) for t in ANNEES} for col, m in moyennes.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    consolidation = RACINE / "resultats" / "v5_consolidation.json"
    if consolidation.exists():  # apport de la gestion passive à 100 % de la comparaison consolidée
        besoins = {p: v["besoin"]["1.0"] for k, v in json.loads(consolidation.read_text(encoding="utf-8"))["capital"].items() for p in [k.split("|")[0]] if k.endswith("|passive")}
    else:
        besoins = {p: v["besoin_apport"]["1.0"] for p, v in json.loads((RACINE / "resultats" / "v5_strategies.json").read_text(encoding="utf-8"))["capital"].items()}
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        f = {(p, base, d): ex.submit(be_par_scenario, p, apport, d, a.n)
             for p in "ABC" for base, apport in (("initial", 0.0), ("recapitalise", besoins[p])) for d in (True, False)}
        v = {k: x.result() for k, x in f.items()}
    sortie = {"n_scenarios": a.n, "apports_recapitalisation": besoins, "resultats": {}}
    for p in "ABC":
        for base in ("initial", "recapitalise"):
            (be1, fdb1, m1), (be0, fdb0, m0) = v[(p, base, True)], v[(p, base, False)]
            e = be1 - be0
            sortie["resultats"][f"{p}|{base}"] = {"be_avec_distribution": float(be1.mean()), "be_sans_distribution": float(be0.mean()),
                                                  "demi_intervalle_95_be": float(demi_intervalle(be1)),
                                                  "ecart_be": float(e.mean()), "demi_intervalle_95": float(demi_intervalle(e)),
                                                  "fdb_avec_distribution": float(fdb1.mean()), "fdb_sans_distribution": float(fdb0.mean()),
                                                  **{f"ecart_{col}_{t}": m1[col][t] - m0[col][t] for col in m1 for t in ANNEES}}
    chemin = RACINE / "resultats" / "v5_effet_distribution.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
