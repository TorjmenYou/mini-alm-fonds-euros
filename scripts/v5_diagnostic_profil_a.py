"""V5 : diagnostic du profil A (valeur actionnaire négative ou proche de zéro).

Usage : python scripts/v5_diagnostic_profil_a.py [--n 1000]
Écrit resultats/v5_diagnostic_profil_a.json. Pour chaque convention étudiée : apports de capital par
scénario (valeur actuelle, première année), ventilés selon qu'un défaut du bloc souverain survient
avant 10 ans et selon le niveau du taux sans risque 10 ans en année 5 (tiers des scénarios).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.stochastique import projeter_stochastique  # noqa: E402
from src.v5 import bases, conventions as cv  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402

CONVENTIONS = (("taux_servi_marche", "decompose"), ("taux_servi_marche", "lisse_integral"),
               ("sans_risque", "decompose"), ("figee", "decompose"), ("oat_moins_2", "lisse_integral"))


def resume(va, masque):
    if masque.sum() == 0:
        return {"n": 0}
    v = va[masque]
    return {"n": int(masque.sum()), "part_avec_apport": float((v > 1e-9).mean()), "va_moyenne": float(v.mean()),
            "q95": float(np.quantile(v, 0.95))}


def diagnostic(reference, credit_code, n):
    h = cv.appliquer(hypotheses_profil("A"), reference)
    g, credit = bases.gse(h, "sans_va", cv.credit_valorisation(credit_code, "sans_va", h["horizon_annees"]), n=n)
    res = projeter_stochastique(h, g, credit=credit)
    va = res["par_scenario"]["va_apports"].to_numpy()
    apports = res["trajectoires"]["apport_assureur"].unstack("annee").to_numpy()[:, 1:]
    avec = apports > 1e-9
    premiere = np.where(avec.any(axis=1), avec.argmax(axis=1) + 1, 0)
    taux5 = np.array([eco.courbe(5).taux_zc(10) for eco in g.scenarios()])
    tiers = np.quantile(taux5, [1 / 3, 2 / 3])
    out = {"reference": reference, "credit": credit_code, "n": n,
           "ensemble": resume(va, np.ones(n, bool)),
           "premiere_annee_apport": {"q25": float(np.quantile(premiere[premiere > 0], 0.25)) if (premiere > 0).any() else None,
                                     "mediane": float(np.median(premiere[premiere > 0])) if (premiere > 0).any() else None,
                                     "part_avant_5_ans": float(((premiere > 0) & (premiere <= 5)).mean()),
                                     "part_avant_10_ans": float(((premiere > 0) & (premiere <= 10)).mean())},
           "taux_10_ans_annee_5_tiers": [float(x) for x in tiers],
           "par_taux": {"bas": resume(va, taux5 <= tiers[0]), "moyen": resume(va, (taux5 > tiers[0]) & (taux5 <= tiers[1])),
                        "haut": resume(va, taux5 > tiers[1])}}
    if hasattr(credit, "probabilite_defaut"):
        p = np.array([credit.probabilite_defaut(t) for t in range(1, 11)])
        defaut = np.array([(credit.pour_scenario(j, n).tirages[:10, 0] < p).any() for j in range(n)])
        out["par_defaut_souverain_avant_10_ans"] = {"avec": resume(va, defaut), "sans": resume(va, ~defaut)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    a = ap.parse_args()
    sortie = {"objet": "Diagnostic des apports de capital du profil A (risque neutre, base sans VA)", "resultats": {}}
    for r, k in CONVENTIONS:
        sortie["resultats"][f"{r}|{k}"] = diagnostic(r, k, a.n)
        print(r, k, "fait", flush=True)
    chemin = RACINE / "resultats" / "v5_diagnostic_profil_a.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
