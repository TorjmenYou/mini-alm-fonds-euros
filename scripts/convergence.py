"""Étude de convergence Monte-Carlo du BE stochastique et de la TVOG.

Usage : python scripts/convergence.py [n1 n2 ...]
Écrit resultats/convergence.csv. Graine fixe (celle des hypothèses) pour chaque taille.
"""

import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.gse import GSE  # noqa: E402
from src.hypotheses import charger_hypotheses  # noqa: E402
from src.stochastique import projeter_stochastique, tvog  # noqa: E402


def main(tailles):
    h = charger_hypotheses()
    lignes = []
    for n in tailles:
        debut = time.perf_counter()
        res = projeter_stochastique(h, GSE(h, n=n))
        duree = time.perf_counter() - debut
        s, t = res["synthese"], tvog(h, res)
        lignes.append({
            "scenarios": n, "be": s["be"], "ic95_be": s["ic_be"], "ecart_type_estimateur_be": s["ic_be"] / 1.96,
            "tvog": t["tvog"], "fdb": s["fdb"], "ic95_fdb": s["ic_fdb"],
            "fuite": s["fuite"], "ic95_fuite": s["ic_fuite"],
            "part_scenarios_avec_apport": s["part_scenarios_avec_apport"], "duree_s": duree,
        })
        print(lignes[-1], flush=True)
    sortie = Path(__file__).resolve().parents[1] / "resultats" / "convergence.csv"
    pd.DataFrame(lignes).to_csv(sortie, index=False, float_format="%.6f")
    print("écrit :", sortie)


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]] or [1000, 2000, 5000, 10000])
