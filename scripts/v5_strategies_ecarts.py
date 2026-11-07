"""V5 : précision des écarts de valeur nette entre stratégies (tirages communs).

Usage : python scripts/v5_strategies_ecarts.py [--n 1000] [--processus 2]
Écrit resultats/v5_strategies_ecarts.json : pour chaque profil, base de capital et stratégie, l'écart
moyen de valeur nette risque neutre à la gestion passive et son demi-intervalle de confiance à 95 %
calculé sur les écarts scénario par scénario (mêmes scénarios économiques et mêmes tirages de défaut),
par paires antithétiques (src.gse.demi_intervalle).
La valeur nette par scénario est actif - BE - apport initial - VA de l'impôt du scénario.
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

CREDIT = "k70_granulaire_correle"
REFERENCE = "taux_servi_marche"


def valeurs_par_scenario(p, code, apport, n):
    h = stg.appliquer_strategie(cv.appliquer(hypotheses_profil(p), REFERENCE, "sans_va", rachat_structurel="acpr"), code, apport)
    g, cr = bases.gse(h, "sans_va", cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=n)
    res = projeter_stochastique(h, g, credit=cr, detail=True)
    tr, ps = res["trajectoires"], res["par_scenario"]
    T = h["horizon_annees"]
    lecture = lambda col: tr[col].unstack("annee")[list(range(1, T + 1))].to_numpy()  # noqa: E731
    impots = stg.impots_par_scenario(lecture("resultat_assureur"), h["fiscalite"]["unite_monetaire_eur"])
    va_impots = (impots * lecture("deflateur")).sum(axis=1)
    return (ps["vm_actif_initial"] - ps["be"]).to_numpy() - apport - va_impots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    capital = json.loads((RACINE / "resultats" / "v5_strategies.json").read_text(encoding="utf-8"))["capital"]
    codes = list(stg.charger()["strategies"])
    taches = {}
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        for p in "ABC":
            for base, apport in (("initial", 0.0), ("recapitalise", capital[p]["besoin_apport"]["1.0"])):
                for code in codes:
                    taches[(p, base, code)] = ex.submit(valeurs_par_scenario, p, code, apport, a.n)
        v = {k: f.result() for k, f in taches.items()}
    sortie = {"n_scenarios": a.n, "credit": CREDIT, "reference": REFERENCE, "ecarts": {}}
    for (p, base, code), x in v.items():
        e = x - v[(p, base, "passive")]
        sortie["ecarts"][f"{p}|{base}|{code}"] = {"valeur_nette": float(x.mean()), "ecart_moyen": float(e.mean()),
                                                  "demi_intervalle_95": float(demi_intervalle(e)) if code != "passive" else 0.0}
    chemin = RACINE / "resultats" / "v5_strategies_ecarts.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
