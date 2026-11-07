"""V5 : mécanismes des politiques de taux servi (risque neutre, bilan initial).

Usage : python scripts/v5_strategies_mecanismes.py [--n 1000] [--processus 2]
Écrit resultats/v5_strategies_mecanismes.json : par profil et politique de taux servi, moyennes par
année du taux de rachat, de l'écart du taux servi à la référence, de la part des scénarios où l'écart
dépasse -1 point (sortie de la zone neutre de la loi de rachat dynamique) et du stock de PPB rapporté à la PM.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.stochastique import projeter_stochastique  # noqa: E402
from src.v5 import bases, conventions as cv, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402

CODES = ("passive", "taux_servi_competitif", "taux_servi_competitif_preservant", "taux_servi_marge")
ANNEES = (1, 2, 3, 5, 8, 10, 15, 20)


def mecanismes(p, code, n):
    h = stg.appliquer_strategie(cv.appliquer(hypotheses_profil(p), "taux_servi_marche", "sans_va", rachat_structurel="acpr"), code)
    g, cr = bases.gse(h, "sans_va", cv.credit_valorisation("k70_granulaire_correle", "sans_va", h["horizon_annees"]), n=n)
    tr = projeter_stochastique(h, g, credit=cr, detail=True)["trajectoires"]
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731
    rachat, ecart = lecture("taux_rachat"), lecture("taux_servi") - lecture("taux_10ans")
    ppb_pm = lecture("ppb") / lecture("pm")
    seuil = h["rachats_dynamiques"]["beta"]
    return {str(t): {"taux_rachat": float(rachat[t].mean()), "ecart_reference": float(ecart[t].mean()),
                     "part_hors_zone_neutre": float((ecart[t] < seuil).mean()), "ppb_pm": float(ppb_pm[t].mean())} for t in ANNEES}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        f = {(p, c): ex.submit(mecanismes, p, c, a.n) for p in "ABC" for c in CODES}
        sortie = {"n_scenarios": a.n, "annees": list(ANNEES), "resultats": {f"{p}|{c}": x.result() for (p, c), x in f.items()}}
    chemin = RACINE / "resultats" / "v5_strategies_mecanismes.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
