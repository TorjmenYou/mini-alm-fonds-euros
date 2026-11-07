"""V5 : bilans initiaux des trois profils fictifs, réconciliations, durations et sensibilités.

Usage : python scripts/v5_bilans_initiaux.py [--rapide]
Écrit resultats/v5_bilans_initiaux.json. --rapide : sans les projections stochastiques.
Toutes les valeurs sont en unités fictives (1 unité = 10 M EUR) et en risque neutre.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.actif import Portefeuille  # noqa: E402
from src.gse import demi_intervalle  # noqa: E402
from src.projection import indicateurs, projeter  # noqa: E402
from src.stochastique import projeter_stochastique  # noqa: E402
from src.courbes import CourbeAvecSpread  # noqa: E402
from src.v5 import bases  # noqa: E402
from src.v5.courbes_marche import courbe_eiopa  # noqa: E402
from src.v5.profils import credit_profil, courbe_decalee, duration_macaulay_obligations, hypotheses_profil  # noqa: E402
from src.v5.scenarios import ScenarioCourbe  # noqa: E402

RAPIDE = "--rapide" in sys.argv


def flux_passif(df):
    T = df.index[-1]
    cf = (df["prestations"] + df["frais"]).copy()
    cf.loc[T] += df.loc[T, "pm"] + df.loc[T, "ppb"] + df.loc[T, "part_pvl_assures_fin"]
    return cf


def bilan(h, base="sans_va", credit=None, decalage=0.0):
    """Bilan initial et indicateurs déterministes (équivalent certain) d'un jeu d'hypothèses."""
    credit = credit_profil() if credit is None else credit
    c = bases.courbe_base(base)
    if decalage:
        c = courbe_decalee(c, decalage)
    credit_b = bases.credit_sur_base(credit, base)
    eco = ScenarioCourbe("ec", h["horizon_annees"], c)
    port = Portefeuille(h, credit=credit_b)
    c0 = eco.courbe(0)
    b = h["bilan_initial"]
    vnc = {"obligations": port.vnc_obligations(), "actions": port.actions_vnc, "monetaire": port.monetaire}
    vm = {"obligations": port.vm_obligations(c0), "actions": port.actions_vm, "monetaire": port.monetaire}
    df = projeter(h, eco, credit=credit_b)
    ind = indicateurs(df)
    cf, d = flux_passif(df), df["deflateur"]
    t = cf.index.to_numpy()
    nominal = sum(l.nominal for l in port.obligations)
    return {
        "comptable": {"actif": vnc, "total_actif": sum(vnc.values()), "passif": dict(b), "total_passif": sum(b.values())},
        "economique": {"actif": vm, "total_actif": sum(vm.values()), "be_equivalent_certain": ind["be"],
                       "valeur_actionnaire_equivalent_certain": ind["valeur_assureur"], "fuite": ind["fuite"]},
        "indicateurs": {
            "coupon_moyen_obligations": sum(l.coupon * l.nominal for l in port.obligations) / nominal,
            "pmvl_obligations": vm["obligations"] - vnc["obligations"],
            "pmvl_obligations_pct_vnc": vm["obligations"] / vnc["obligations"] - 1,
            "pvl_actions": vm["actions"] - vnc["actions"],
            "duration_macaulay_obligations": duration_macaulay_obligations(port, c0),
            "duration_macaulay_flux_passif": float((t * cf * d).sum() / (cf * d).sum()),
            "ppb_pct_pm": b["ppb"] / b["pm"], "reserve_capitalisation_pct_pm": b["reserve_capitalisation"] / b["pm"],
            "fonds_propres_comptables_pct_pm": b["fonds_propres"] / b["pm"],
            "liquidite_pct_actif_vm": vm["monetaire"] / sum(vm.values()),
            "taux_garanti": h["passif"]["tmg"], "taux_servi_initial": h["passif"]["taux_servi_initial"],
            "taux_reference_assures_annee_1": float(df.loc[1, "taux_10ans"]),
            "taux_servi_annee_1": float(df.loc[1, "taux_servi"]), "taux_rachat_annee_1": float(df.loc[1, "taux_rachat"]),
            "taux_servi_moyen_annees_1_20": float(df.loc[1:20, "taux_servi"].mean()),
            "taux_rachat_moyen_annees_1_20": float(df.loc[1:20, "taux_rachat"].mean()),
            "pm_annee_10": float(df.loc[10, "pm"]),
            "pertes_credit_risque_neutre_annee_1_pct_vnc_obligations": float(df.loc[1, "pertes_credit"] / vnc["obligations"]) if "pertes_credit" in df else None,
            "produits_financiers_annee_1_pct_vnc": float(df.loc[1, "produits_financiers"] / df.loc[0, "vnc_actif"]) if "produits_financiers" in df else None,
        },
    }


def reconciliation(r):
    """Passage des fonds propres comptables à la valeur actionnaire (identité exacte en t = 0)."""
    c, e, i = r["comptable"], r["economique"], r["indicateurs"]
    p = c["passif"]
    provisions = p["pm"] + p["ppb"] + p["reserve_capitalisation"]
    etapes = {
        "fonds_propres_comptables": p["fonds_propres"],
        "plus_ou_moins_values_latentes_obligations": i["pmvl_obligations"],
        "plus_values_latentes_actions": i["pvl_actions"],
        "provisions_comptables_moins_be": provisions - e["be_equivalent_certain"],
    }
    etapes["valeur_actionnaire"] = sum(etapes.values())
    ecart = etapes["valeur_actionnaire"] - e["valeur_actionnaire_equivalent_certain"]
    return {"etapes": etapes, "ecart_avec_actif_moins_be": ecart, "ecart_bilan_comptable": c["total_actif"] - c["total_passif"]}


def stochastique(h, base):
    gse, credit_b = bases.gse(h, base, credit=credit_profil())
    t0 = time.time()
    res = projeter_stochastique(h, gse, credit=credit_b)
    ps, traj, s = res["par_scenario"], res["trajectoires"], res["synthese"]
    T = h["horizon_annees"]
    fin = traj.xs(T, level="annee")
    residu = fin["deflateur"] * (fin["vm_actif"] - fin["pm"] - fin["ppb"] - fin["part_pvl_assures_fin"])
    valeur = ps["vm_actif_initial"] - ps["be"]
    identite = valeur - (residu.to_numpy() - ps["va_apports"] + ps["fuite"])
    be_ec = bilan(h, base)["economique"]["be_equivalent_certain"]  # équivalent certain sur la même courbe
    return {"be": s["be"], "ic_be": s["ic_be"], "be_equivalent_certain": be_ec, "tvog": s["be"] - be_ec,
            "fdb": s["fdb"], "valeur_actionnaire": float(valeur.mean()), "ic_valeur": float(demi_intervalle(valeur)),
            "fuite": s["fuite"], "ic_fuite": s["ic_fuite"], "va_apports": s["va_apports"],
            "part_scenarios_avec_apport": s["part_scenarios_avec_apport"],
            "identite_valeur_ecart_max": float(np.abs(identite).max()), "duree_s": round(time.time() - t0, 1)}


# Référence fondée sur le taux sans risque, recalée pour donner en t = 0 le même niveau que la
# référence centrale « OAT 10 ans - 2 points » : seule la dynamique future diffère.
_AJUST_SANS_RISQUE = (CourbeAvecSpread(courbe_eiopa(), credit_profil()).taux_zc(10) - 0.02) - courbe_eiopa().taux_zc(10)

SENSIBILITES = {
    "spread +50 pb": {"credit_decalage": 0.005},
    "spread -50 pb": {"credit_decalage": -0.005},
    "coupons 2015-2021 +50 pb": {"coupons": {"2015_2021": 0.005}},
    "coupons 2015-2021 -25 pb": {"coupons": {"2015_2021": -0.0025}},
    "prime d'achat -40 pb (toutes générations)": {"coupons": {m: -0.004 for m in ("avant_2012", "2012_2014", "2015_2021", "2022_2023", "2024_2025", "2026")}},
    "prime d'achat +20 pb (toutes générations)": {"coupons": {m: 0.002 for m in ("avant_2012", "2012_2014", "2015_2021", "2022_2023", "2024_2025", "2026")}},
    "PPB x 0,5": {"ppb_facteur": 0.5},
    "PPB x 1,5": {"ppb_facteur": 1.5},
    "référence assurés : OAT 10 ans (ajustement 0)": {"comportement": {"reference": "zc10_obligations", "ajustement": 0.0}},
    "référence assurés : OAT 10 ans - 1 pt": {"comportement": {"reference": "zc10_obligations", "ajustement": -0.01}},
    "référence assurés : OAT 10 ans - 3 pts": {"comportement": {"reference": "zc10_obligations", "ajustement": -0.03}},
    "référence assurés : livret A 1,7 % fixe": {"comportement": {"reference": "fixe", "taux_fixe": 0.017}},
    "référence assurés : sans risque 10 ans, même niveau en t = 0": {"comportement": {"reference": "zc10_sans_risque", "ajustement": _AJUST_SANS_RISQUE}},
    "taux garanti +0,30 pt": {"tmg_decalage": 0.003},
    "base avec VA": {"base": "avec_va"},
}


def sensibilite(nom, regle):
    h = hypotheses_profil(nom, decalage_coupons=regle.get("coupons"))
    if "ppb_facteur" in regle:
        h["bilan_initial"]["ppb"] *= regle["ppb_facteur"]
        h["actif"]["lignes_obligataires"] = hypotheses_profil(nom, {"bilan_initial.ppb": h["bilan_initial"]["ppb"]},
                                                              regle.get("coupons"))["actif"]["lignes_obligataires"]
    if "comportement" in regle:
        h["comportement"] = regle["comportement"]
    if "tmg_decalage" in regle:
        h["passif"]["tmg"] += regle["tmg_decalage"]
    credit = credit_profil()
    if "credit_decalage" in regle:
        credit.choquer(regle["credit_decalage"])
    r = bilan(h, regle.get("base", "sans_va"), credit)
    return {"vm_actif": r["economique"]["total_actif"], "pmvl_obligations_pct_vnc": r["indicateurs"]["pmvl_obligations_pct_vnc"],
            "be_equivalent_certain": r["economique"]["be_equivalent_certain"],
            "valeur_actionnaire_equivalent_certain": r["economique"]["valeur_actionnaire_equivalent_certain"],
            "taux_rachat_annee_1": r["indicateurs"]["taux_rachat_annee_1"], "taux_servi_annee_1": r["indicateurs"]["taux_servi_annee_1"],
            "taux_rachat_moyen_annees_1_20": r["indicateurs"]["taux_rachat_moyen_annees_1_20"],
            "taux_servi_moyen_annees_1_20": r["indicateurs"]["taux_servi_moyen_annees_1_20"]}


sortie = {"unites": "unités fictives, 1 unité = 10 M EUR ; risque neutre ; base sans VA sauf mention", "profils": {}}
for nom in "ABC":
    h = hypotheses_profil(nom)
    r = bilan(h)
    ref_bas, ref_haut = bilan(h, decalage=-0.0005), bilan(h, decalage=0.0005)
    eff = lambda cle: -(ref_haut["economique"][cle] - ref_bas["economique"][cle]) / (0.001 * r["economique"][cle])  # noqa: E731
    r["indicateurs"]["duration_effective_actif"] = eff("total_actif")
    r["indicateurs"]["duration_effective_be"] = eff("be_equivalent_certain")
    r["indicateurs"]["sensibilite_valeur_par_pb"] = (ref_haut["economique"]["valeur_actionnaire_equivalent_certain"]
                                                     - ref_bas["economique"]["valeur_actionnaire_equivalent_certain"]) / 10
    # Même calcul avec une référence des assurés figée à son niveau de l'année 1 : isole l'effet des
    # rachats dynamiques (la référence suit le choc de taux) sur la duration du passif.
    hf = dict(h, comportement={"reference": "fixe", "taux_fixe": r["indicateurs"]["taux_reference_assures_annee_1"]})
    rf, fb, fh = bilan(hf), bilan(hf, decalage=-0.0005), bilan(hf, decalage=0.0005)
    r["indicateurs"]["duration_effective_be_reference_figee"] = -(fh["economique"]["be_equivalent_certain"] - fb["economique"]["be_equivalent_certain"]) / (
        0.001 * rf["economique"]["be_equivalent_certain"])
    r["indicateurs"]["sensibilite_valeur_par_pb_reference_figee"] = (fh["economique"]["valeur_actionnaire_equivalent_certain"]
                                                                     - fb["economique"]["valeur_actionnaire_equivalent_certain"]) / 10
    r["reconciliation"] = reconciliation(r)
    r["avec_va"] = {"be_equivalent_certain": bilan(h, "avec_va")["economique"]["be_equivalent_certain"]}
    r["sensibilites"] = {k: sensibilite(nom, v) for k, v in SENSIBILITES.items()}
    if not RAPIDE:
        r["stochastique"] = {base: stochastique(h, base) for base in bases.BASES}
    r["libelle"] = h["profil"]["libelle"]
    sortie["profils"][nom] = r
    print(nom, "fait", flush=True)

chemin = RACINE / "resultats" / ("v5_bilans_initiaux_rapide.json" if RAPIDE else "v5_bilans_initiaux.json")
chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
print("écrit :", chemin)
