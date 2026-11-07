"""Indicateurs de synthèse des projections V5 (risque neutre), partagés par les scripts de comparaison."""

import time

import numpy as np

from ..projection import indicateurs, projeter
from ..stochastique import projeter_stochastique
from . import bases
from .profils import courbe_decalee
from .scenarios import ScenarioCourbe


def equivalent_certain(h, credit, base="sans_va", decalage=0.0):
    """Équivalent certain (perte de crédit moyenne) sur la courbe de la base, éventuellement décalée."""
    c = bases.courbe_base(base)
    if decalage:
        c = courbe_decalee(c, decalage)
    eco = ScenarioCourbe("ec", h["horizon_annees"], c, courbe_avant_choc=bases.courbe_base(base))
    df = projeter(h, eco, credit=bases.credit_sur_base(credit, base))
    return df, indicateurs(df)


def resume_ec(h, credit, base="sans_va"):
    df, ind = equivalent_certain(h, credit, base)
    bas, haut = equivalent_certain(h, credit, base, -0.0005)[1], equivalent_certain(h, credit, base, 0.0005)[1]
    return {
        "be": ind["be"], "valeur": ind["valeur_assureur"], "vm_actif": ind["vm_actif_initial"], "fuite": ind["fuite"],
        "taux_servi_moyen_1_10": float(df.loc[1:10, "taux_servi"].mean()),
        "taux_rachat_annee_1": float(df.loc[1, "taux_rachat"]),
        "rachats_sur_pm_ouverture_annee_1": float(df.loc[1, "rachats"] / df.loc[0, "pm"]),
        "taux_rachat_moyen_1_10": float(df.loc[1:10, "taux_rachat"].mean()),
        "reference_annee_1": float(df.loc[1, "taux_10ans"]), "reference_annee_10": float(df.loc[10, "taux_10ans"]),
        "duration_effective_be": -(haut["be"] - bas["be"]) / (0.001 * ind["be"]),
        "duration_effective_actif": -(haut["vm_actif_initial"] - bas["vm_actif_initial"]) / (0.001 * ind["vm_actif_initial"]),
        "valeur_par_pb": (haut["valeur_assureur"] - bas["valeur_assureur"]) / 10,
    }


def resume_stochastique(h, credit, base="sans_va", n=1000):
    t0 = time.time()
    g, cr = bases.gse(h, base, credit, n=n)
    res = projeter_stochastique(h, g, credit=cr, detail=True)
    s, ps, tr = res["synthese"], res["par_scenario"], res["trajectoires"]
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731
    rachat, servi, pm, prest = lecture("taux_rachat"), lecture("taux_servi"), lecture("pm"), lecture("prestations")
    apports, pmv, pertes, fp = lecture("apport_assureur"), lecture("pmv_obligataires_realisees"), lecture("pertes_credit"), lecture("fonds_propres")
    ans = list(range(1, 11))
    sorties = prest[ans].to_numpy() / pm[[a - 1 for a in ans]].to_numpy()
    mv = -np.minimum(pmv[ans].to_numpy(), 0.0).sum(axis=1)
    va = ps["va_apports"].to_numpy()
    valeur = ps["vm_actif_initial"].to_numpy() - ps["be"].to_numpy()
    avec = apports.to_numpy()[:, 1:] > 1e-9
    premiere = np.where(avec.any(axis=1), avec.argmax(axis=1) + 1, 0)
    return {
        "be": s["be"], "ic_be": s["ic_be"], "valeur": s["valeur_assureur"], "vm_actif": s["vm_actif_initial"],
        "valeur_q05_par_scenario": float(np.quantile(valeur, 0.05)), "fdb": s["fdb"], "be_garanti": s["be_garanti"],
        "fuite": s["fuite"], "ic_fuite": s["ic_fuite"],
        "taux_rachat_annee_1": float(rachat[1].mean()), "taux_rachat_moyen_1_10": float(rachat[ans].to_numpy().mean()),
        "taux_rachat_max_1_10_q95": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.95)),
        "taux_servi_moyen_1_10": float(servi[ans].to_numpy().mean()),
        "sorties_max_1_10_q95": float(np.quantile(sorties.max(axis=1), 0.95)),
        "sorties_max_1_10_q99": float(np.quantile(sorties.max(axis=1), 0.99)),
        "moins_values_realisees_1_10_moyenne": float(mv.mean()), "moins_values_realisees_1_10_q99": float(np.quantile(mv, 0.99)),
        "part_mv_realisees_au_dela_rc": float((mv > h["bilan_initial"]["reserve_capitalisation"]).mean()),
        "pertes_credit_1_10_moyenne": float(pertes[ans].to_numpy().sum(axis=1).mean()),
        "pertes_credit_1_10_q99": float(np.quantile(pertes[ans].to_numpy().sum(axis=1), 0.99)),
        "va_apports_moyenne": float(va.mean()), "part_scenarios_avec_apport": s["part_scenarios_avec_apport"],
        "va_apports_q95": float(np.quantile(va, 0.95)), "va_apports_q99": float(np.quantile(va, 0.99)),
        "part_apport_avant_10_ans": float(((premiere > 0) & (premiere <= 10)).mean()),
        "part_fonds_propres_negatifs_10_ans": float((fp[ans].to_numpy().min(axis=1) < 0).mean()),
        "duree_s": round(time.time() - t0, 1),
    }
