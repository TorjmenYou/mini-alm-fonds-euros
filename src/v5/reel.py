"""Projections stochastiques en probabilité réelle (V5) : distributions de plausibilité, sans valorisation.

Chaque scénario combine une trajectoire de taux du générateur, un rendement actions augmenté d'une
prime de risque et des défauts tirés avec les probabilités réelles (src/v5/credit.py). La mesure de
crédit est « trajectoire » : indicateurs() refuse tout calcul de valeur sur ces projections.

Indicateurs produits (montants non actualisés, en unités fictives) :
- apports : trésorerie apportée par l'actionnaire quand l'actif est épuisé (règle de liquidité du modèle) ;
- fonds propres comptables négatifs : seuil comptable de recapitalisation ;
- sorties annuelles, moins-values réalisées sur ventes d'obligations, pertes de crédit.
"""

import numpy as np
import pandas as pd

from ..projection import projeter
from .scenarios import ScenarioReelStochastique


def projeter_reel_stochastique(h, gse, credit, prime_actions):
    if h["actif"]["credit"].get("mesure") != "trajectoire":
        raise ValueError("Projection réelle : la mesure de crédit doit être « trajectoire »")
    scenarios = gse.scenarios()
    dfs = []
    for j, s in enumerate(scenarios):
        eco = ScenarioReelStochastique(s, prime_actions)
        dfs.append(projeter(h, eco, credit=credit.pour_scenario(j, len(scenarios)), detail=True))
    return pd.concat(dfs, keys=range(len(dfs)), names=["scenario", "annee"])


def resume_reel(h, tr, horizons=(10, 20)):
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731
    apports, fp, rachat = lecture("apport_assureur"), lecture("fonds_propres"), lecture("taux_rachat")
    servi, pm, prest = lecture("taux_servi"), lecture("pm"), lecture("prestations")
    pmv, pertes = lecture("pmv_obligataires_realisees"), lecture("pertes_credit")
    T = apports.columns.max()
    out = {"n": int(apports.shape[0])}
    for H in horizons + (T,):
        cols = [c for c in apports.columns if 1 <= c <= H]
        a = apports[cols].to_numpy().sum(axis=1)
        out[f"apports_{H}"] = {"probabilite": float((a > 1e-9).mean()), "moyenne": float(a.mean()),
                               "q95": float(np.quantile(a, 0.95)), "q99": float(np.quantile(a, 0.99)),
                               "moyenne_si_apport": float(a[a > 1e-9].mean()) if (a > 1e-9).any() else 0.0}
        out[f"fonds_propres_negatifs_{H}"] = float((fp[cols].to_numpy().min(axis=1) < 0).mean())
    ans = [c for c in apports.columns if 1 <= c <= 10]
    sorties = prest[ans].to_numpy() / pm[[a - 1 for a in ans]].to_numpy()
    mv = -np.minimum(pmv[ans].to_numpy(), 0.0).sum(axis=1)
    pc = pertes[ans].to_numpy().sum(axis=1)
    out.update({
        "fonds_propres_min_1_10_q05": float(np.quantile(fp[ans].to_numpy().min(axis=1), 0.05)),
        "fonds_propres_min_1_10_q01": float(np.quantile(fp[ans].to_numpy().min(axis=1), 0.01)),
        "fonds_propres_annee_10_mediane": float(fp[10].median()),
        "taux_rachat_annee_1_moyen": float(rachat[1].mean()),
        "taux_rachat_moyen_1_10": float(rachat[ans].to_numpy().mean()),
        "taux_rachat_max_1_10_q95": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.95)),
        "taux_rachat_max_1_10_q99": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.99)),
        "taux_servi_moyen_1_10": float(servi[ans].to_numpy().mean()),
        "taux_servi_1_10_q05": float(np.quantile(servi[ans].to_numpy().mean(axis=1), 0.05)),
        "sorties_max_1_10_q99": float(np.quantile(sorties.max(axis=1), 0.99)),
        "moins_values_realisees_1_10_moyenne": float(mv.mean()), "moins_values_realisees_1_10_q99": float(np.quantile(mv, 0.99)),
        "part_mv_realisees_au_dela_rc": float((mv > h["bilan_initial"]["reserve_capitalisation"]).mean()),
        "pertes_credit_1_10_moyenne": float(pc.mean()), "pertes_credit_1_10_q99": float(np.quantile(pc, 0.99)),
        "part_scenarios_avec_defaut_1_10": float((pc > 1e-9).mean()),
        "pm_annee_10_mediane": float(pm[10].median()),
    })
    return out
