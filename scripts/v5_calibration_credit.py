"""V5 : démonstration du traitement du risque de crédit (tableaux déterministes).

Usage : python scripts/v5_calibration_credit.py
Écrit resultats/v5_calibration_credit.json :
1. des spreads aux intensités : spread cumulé H, incréments annuels, probabilités de défaut risque neutre
   d'un bloc selon la part de crédit kappa et le recouvrement ;
2. risque neutre et probabilité réelle sur des bases comparables ;
3. articulation entre intensité, recouvrement et part des blocs.
Le spread des obligations est l'hypothèse de data/v5/marche/spread_hypothetique_20261031.json
(scripts/v5_spread_hypothetique.py) ; aucune donnée d'indice de taux souverain n'est utilisée.
"""

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import conventions as cv  # noqa: E402
from src.v5.courbes_marche import courbe_eiopa, spread_obligations  # noqa: E402
from src.v5.credit import CreditSaut  # noqa: E402

C = cv.charger()
eiopa = courbe_eiopa()
spread = spread_obligations()
MATURITES = (1, 2, 3, 5, 7, 10, 15, 20, 30)

kc = C["calibration_kappa"]
intensites = {}
for kappa, rec in ((kc["central"], 0.4), (kc["bas"], 0.4), (kc["haut"], 0.4), (kc["central"], 0.63)):
    c = CreditSaut(dict(spread.points), part_saut=kappa, recouvrement=rec)
    survie, lignes = 1.0, {}
    for t in range(1, 31):
        p = c.probabilite_defaut(t)
        survie *= 1 - p
        if t in MATURITES:
            d_total, d_saut, d_lisse = c.increments(t)
            lignes[t] = {"H": spread.H(t), "increment_total": d_total, "increment_credit": d_saut, "increment_hors_defaut": d_lisse,
                         "pd_annuelle": p, "pd_cumulee": 1 - survie}
    intensites[f"kappa={kappa}|R={rec}"] = lignes

pd_reel = C["decomposition_spread_10_ans"]["probabilite_defaut_reelle_annuelle"]["valeur"]
lc = intensites[f"kappa={kc['central']}|R=0.4"]
comparaison = {
    "pd_rn_annuelle_annee_10": lc[10]["pd_annuelle"], "pd_rn_moyenne_10_ans": 1 - (1 - lc[10]["pd_cumulee"]) ** 0.1,
    "pd_rn_moyenne_spot_10_ans": kc["central"] * spread.s(10) / 0.6,
    "pd_reelle_annuelle": pd_reel, "pd_reelle_cumulee_10_ans": 1 - (1 - pd_reel) ** 10,
    "perte_rn_annuelle_spot_10_ans": kc["central"] * spread.s(10), "perte_reelle_annuelle": pd_reel * 0.5,
    "rapport_pd_moyennes": (1 - (1 - lc[10]["pd_cumulee"]) ** 0.1) / pd_reel,
    "rapport_publie_zone_euro": C["observations"]["rapport_intensites_risque_neutre_sur_reelles"]["valeur"],
}
blocs = {}
for nom in ("souverain_et_diversifie", "granulaire_50", "souverain_et_granulaire_50", "un"):
    w = cv.poids_blocs(nom)
    blocs[nom] = {"nombre": len(w), "poids_max": max(w), "perte_du_plus_gros_bloc_R40": max(w) * 0.6,
                  "probabilite_rn_defaut_plus_gros_bloc_10_ans": lc[10]["pd_cumulee"],
                  "probabilite_reelle_defaut_plus_gros_bloc_10_ans": 1 - (1 - pd_reel) ** 10,
                  "perte_attendue_annuelle_identique": True}

sortie = {"spread": {str(k): spread.s(k) for k in MATURITES}, "eiopa_zc": {str(k): eiopa.taux_zc(k) for k in MATURITES},
          "intensites": intensites, "risque_neutre_et_reel": comparaison, "blocs": blocs, "kappa": kc}
chemin = RACINE / "resultats" / "v5_calibration_credit.json"
chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
print("écrit :", chemin)
print(json.dumps({"comparaison": comparaison}, indent=1, default=float))
