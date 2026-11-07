"""V5 : démonstration de la calibration du risque de crédit souverain (tableaux déterministes).

Usage : python scripts/v5_calibration_credit.py
Écrit resultats/v5_calibration_credit.json :
1. du TEC (taux de rendement au pair) aux taux zéro-coupon : erreur de l'approximation « TEC = zéro-coupon » ;
2. des spreads aux intensités : spread cumulé H, incréments annuels, probabilités de défaut risque neutre
   d'un bloc selon la part de crédit kappa et le recouvrement ;
3. contrôle avec le CDS à 5 ans (triangle du crédit) ;
4. risque neutre et probabilité réelle sur des bases comparables ;
5. articulation entre intensité, recouvrement et part des blocs.
"""

import json
import math
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import conventions as cv  # noqa: E402
from src.v5.courbes_marche import courbe_eiopa, spread_oat  # noqa: E402
from src.v5.credit import CreditSaut  # noqa: E402

C = cv.charger()
spread_tec = spread_oat()
eiopa = courbe_eiopa()
MATURITES = (1, 2, 3, 5, 7, 10, 15, 20, 30)


def tec_interpole(k, tec):
    pts = sorted((int(a), b) for a, b in tec.items())
    if k <= pts[0][0]:
        return pts[0][1]
    if k >= pts[-1][0]:
        return pts[-1][1]
    for (a, ya), (b, yb) in zip(pts, pts[1:]):
        if a <= k <= b:
            return ya + (k - a) / (b - a) * (yb - ya)


def bootstrap_zero(tec, kmax=30):
    """Taux zéro-coupon actuariels d'une courbe de rendements au pair à coupons annuels."""
    zc = {}
    for k in range(1, kmax + 1):
        c = tec_interpole(k, tec)
        somme = sum(zc[j] for j in range(1, k))
        zc[k] = (1 - c * somme) / (1 + c)
    return {k: zc[k] ** (-1 / k) - 1 for k in zc}


donnees_tec = json.loads((RACINE / "data" / "v5" / "marche" / "spread_oat_20261104.json").read_text(encoding="utf-8"))["donnees_observees"]["TEC_04_11_2026"]
zero_oat = bootstrap_zero(donnees_tec)
approx = {k: {"tec": tec_interpole(k, donnees_tec), "zero_bootstrap": zero_oat[k],
              "spread_modele": spread_tec.s(k),
              "spread_bootstrap": math.log(1 + zero_oat[k]) - math.log(1 + eiopa.taux_zc(k))} for k in MATURITES}
for v in approx.values():
    v["ecart_pb"] = 1e4 * (v["spread_bootstrap"] - v["spread_modele"])

# Fiche du spread zéro-coupon par bootstrap (2 à 30 ans ; plat en dessous de 2 ans, faute de TEC à 1 an)
fiche = {"statut": "calibré", "objet": "Spread zéro-coupon (composition continue) des OAT au-dessus de la courbe EIOPA sans VA au 31/10/2026, taux zéro-coupon OAT obtenus par bootstrap du TEC du 04/11/2026",
         "regle": "TEC interpolés linéairement entre les maturités observées (2, 5, 10, 15, 20 et 30 ans), coupons annuels, bootstrap des prix zéro-coupon ; s(k) = ln(1 + z_OAT(k)) - ln(1 + r_EIOPA(k)) ; plat en dessous de 2 ans et au-delà de 30 ans",
         "source": "data/v5/marche/spread_oat_20261104.json (TEC observés) et courbe EIOPA du 31/10/2026",
         "spread_continu": {str(k): round(math.log(1 + zero_oat[k]) - math.log(1 + eiopa.taux_zc(k)), 8) for k in range(2, 31)}}
(RACINE / "data" / "v5" / "marche" / "spread_oat_20261104_zc.json").write_text(json.dumps(fiche, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
spread = spread_oat(methode="bootstrap")  # spread des conventions de sécurisation

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

cds = C["observations"]["cds_france_5_ans"]["valeur"]
triangle = {"cds_5_ans": cds, "intensite_triangle_R40": cds / 0.6, "pd_cumulee_5_ans_triangle": 1 - math.exp(-5 * cds / 0.6),
            "pd_cumulee_5_ans_modele_kappa_1": intensites[f"kappa={kc['haut']}|R=0.4"][5]["pd_cumulee"],
            "pd_cumulee_5_ans_modele_kappa_central": intensites[f"kappa={kc['central']}|R=0.4"][5]["pd_cumulee"],
            "spread_5_ans": spread.s(5)}

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

sortie = {"tec_vers_zero": approx, "intensites": intensites, "cds": triangle, "risque_neutre_et_reel": comparaison,
          "blocs": blocs, "kappa": kc,
          "bund": {"tec_10": C["observations"]["tec_10_ans"]["valeur"], "oat_bund": C["observations"]["spread_oat_bund_10_ans"]["valeur"],
                   "bund_10_estime": C["observations"]["tec_10_ans"]["valeur"] - C["observations"]["spread_oat_bund_10_ans"]["valeur"],
                   "eiopa_zc_10": eiopa.taux_zc(10), "reserve": "TEC du 04/11 et écart OAT-Bund du 30/10 ; rendement au pair et taux zéro-coupon mélangés"}}
chemin = RACINE / "resultats" / "v5_calibration_credit.json"
chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
print("écrit :", chemin)
print(json.dumps({"ecart_pb": {k: round(v["ecart_pb"], 1) for k, v in approx.items()}, "cds": triangle, "comparaison": comparaison}, indent=1, default=float))
