"""Recalcule les indicateurs publiés dans le README et la documentation.

Usage : python scripts/resultats_reference.py
Écrit resultats/indicateurs.json (1 000 scénarios, graine des hypothèses).
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.hypotheses import charger_hypotheses  # noqa: E402
from src.projection import indicateurs, projeter, scenario  # noqa: E402
from src.prophet.epargne import construire  # noqa: E402
from src.prophet.tables import scenario_depuis_projection  # noqa: E402
from src.solvabilite import calculer_scr  # noqa: E402
from src.stochastique import decomposer_tvog, projeter_stochastique, tvog  # noqa: E402


def flottants(d):
    return {k: (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v) for k, v in d.items()}


def main():
    h = charger_hypotheses()
    out = {"V1": {}, "V4": {}}
    for nom in ["central", "hausse_taux_200pb", "baisse_taux_100pb", "krach_actions_25pc"]:
        df = projeter(h, scenario(h, nom))
        out["V1"][nom] = flottants(indicateurs(df)) | {"pm_annee_10": float(df.loc[10, "pm"]),
                                                       "ppb_annee_10": float(df.loc[10, "ppb"])}
        r = construire(scenario_depuis_projection(df, h)).calculer().xs(0, level="annee")
        out["V4"][nom] = {"va_sorties": float(r["VA_SORTIES"].sum()), "va_cout_tmg": float(r["VA_COUT_TMG"].sum())}

    res = projeter_stochastique(h)
    out["V2"] = flottants(res["synthese"]) | flottants(tvog(h, res))
    _, shapley = decomposer_tvog(h)
    out["V2"]["decomposition_tvog"] = {k: float(v) for k, v in shapley.items()}

    s = calculer_scr(h)
    out["V3"] = {
        "pertes_nettes": flottants(s["pertes_nettes"]), "ic_pertes_nettes": flottants(s["ic_pertes_nettes"]),
        "pertes_brutes": flottants(s["pertes_brutes"]), "ic_pertes_brutes": flottants(s["ic_pertes_brutes"]),
        "fdb": flottants(s["fdb"]), "sens_retenus": s["sens_retenus"],
        "scr_net": flottants(s["scr_net"]), "scr_brut": flottants(s["scr_brut"]),
        "ajustement_tp": float(s["ajustement_tp"]), "scr": float(s["scr"]),
        "bilans": {k: flottants(v) for k, v in s["bilans"].items()},
        "controles": {"fdb_negatives": s["controles"]["fdb_negatives"],
                      "ajustement_plafonne_par_fdb": bool(s["controles"]["ajustement_plafonne_par_fdb"]),
                      "marge_avant_plafond_fdb": float(s["controles"]["marge_avant_plafond_fdb"]),
                      "part_scenarios_avec_apport": s["controles"]["part_scenarios_avec_apport"]},
    }
    sortie = Path(__file__).resolve().parents[1] / "resultats" / "indicateurs.json"
    sortie.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("écrit :", sortie)


if __name__ == "__main__":
    main()
