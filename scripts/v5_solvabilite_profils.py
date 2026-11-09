"""V5 : vue prudentielle simplifiée des trois profils (base avec VA), pour plusieurs conventions.

Usage : python scripts/v5_solvabilite_profils.py [--n 1000] [--processus 2]
Écrit resultats/v5_solvabilite_profils.json. Calcul pédagogique (src/v5/solvabilite_v5.py), qui ne
prétend pas reproduire un bilan prudentiel réel.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import conventions as cv  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.solvabilite_v5 import scr_simplifie  # noqa: E402

CONVENTIONS = (("sans_risque", "lisse_integral"), ("sans_risque", "decompose"),
               ("sans_risque_demi", "decompose"), ("taux_servi_marche", "decompose"))


def calcul(p, reference, credit, n):
    h = cv.appliquer(hypotheses_profil(p), reference, "avec_va")
    r = scr_simplifie(h, credit, "avec_va", n=n)
    from src.v5.solvabilite_v5 import ppb_admissible_fonds_excedentaires
    r["fonds_excedentaires_borne_haute"] = ppb_admissible_fonds_excedentaires(h) * (1 - 0.25 * 1.033)  # PPB admissible nette d'impôt : borne haute indicative
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    sortie = {"objet": "Vue prudentielle simplifiée (base avec VA), unités fictives, 1 unité = 10 M EUR", "n_scenarios": a.n, "resultats": {}}
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        taches = {ex.submit(calcul, p, r, k, a.n): f"{p}|{r}|{k}" for p in "ABC" for r, k in CONVENTIONS}
        for i, f in enumerate(as_completed(taches), 1):
            sortie["resultats"][taches[f]] = f.result()
            print(f"{i}/{len(taches)} {taches[f]}", flush=True)
    sortie["resultats"] = dict(sorted(sortie["resultats"].items()))
    chemin = RACINE / "resultats" / "v5_solvabilite_profils.json"
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
