"""Stratégies ALM de la V5 et mesures de comparaison (première comparaison exploratoire).

Principes (docs/V5_STRATEGIES.md) :
- même bilan initial pour toutes les stratégies d'un profil : la stratégie ne change que les règles
  de gestion à partir de l'ouverture (allocation cible, réinvestissement, taux servi, repositionnement) ;
- mêmes scénarios économiques et mêmes tirages de défaut pour toutes les stratégies ;
- un apport de capital est une sortie de l'actionnaire, jamais un profit : la valeur nette déduit
  l'apport initial et la valeur actuelle des apports ultérieurs ;
- valorisation risque neutre et rentabilité en probabilité réelle restent séparées.
"""

import copy
import json
from pathlib import Path

import numpy as np

from ..stochastique import projeter_stochastique
from . import bases
from .fiscalite import impot_annuel

FICHIER = Path(__file__).resolve().parents[2] / "data" / "v5" / "strategies" / "strategies.json"


def charger():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def appliquer_strategie(h, code, apport_initial=0.0):
    """Hypothèses d'une stratégie : le portefeuille d'ouverture reste celui du profil."""
    h = copy.deepcopy(h)
    a = h["actif"]
    a.setdefault("allocation_initiale", dict(a["allocation_cible"]))
    for cle, valeur in charger()["strategies"][code]["modifications"].items():
        if cle == "actif.monetaire_cible":
            alloc = dict(a["allocation_cible"])
            ecart = valeur - alloc["monetaire"]
            alloc["monetaire"] = valeur
            alloc["actions"] = max(alloc["actions"] - ecart, 0.0)
            alloc["obligations"] = 1.0 - alloc["monetaire"] - alloc["actions"]
            a["allocation_cible"] = alloc
            continue
        cible = h
        *chemin, feuille = cle.split(".")
        for c in chemin:
            cible = cible.setdefault(c, {})
        cible[feuille] = copy.deepcopy(valeur)
    if apport_initial:
        h["bilan_initial"]["apport_initial"] = float(apport_initial)
    # Politique de distribution commune à toutes les stratégies : les fonds propres comptables sont
    # maintenus à leur niveau initial rapporté à la PM (apport compris) ; l'excédent est distribué.
    b = h["bilan_initial"]
    alm = h.setdefault("strategie_alm", {})
    alm["distribution"] = {"fonds_propres_pct_pm": (b["fonds_propres"] + b.get("apport_initial", 0.0)) / b["pm"],
                           "part_distribuee": alm.get("part_distribuee", 1.0)}
    # Plancher de PPB des reprises volontaires, exprimé en part du ratio PPB / PM d'ouverture
    if "plancher_ppb_part_initiale" in alm:
        h["strategie"]["plancher_ppb_pct_pm"] = alm["plancher_ppb_part_initiale"] * b["ppb"] / b["pm"]
    h["strategie_code"] = code
    return h


def impots_par_scenario(resultats, unite):
    """Impôt annuel (25 % et contribution sociale, déficits reportables) sur une matrice de résultats
    (scénarios x années 1..T)."""
    impots = np.zeros_like(resultats)
    for j in range(resultats.shape[0]):
        report = 0.0
        for t in range(resultats.shape[1]):
            total, _, _, report = impot_annuel(float(resultats[j, t]), 1e12, report, unite)
            impots[j, t] = total
    return impots


def resume_risque_neutre(h, credit, base="sans_va", n=1000, valeurs=False, graines=None):
    """Valeur nette risque neutre et indicateurs des assurés et de la liquidité.
    valeurs=True ajoute « _valeurs_nettes » (valeur nette par scénario, pour les écarts appariés) ;
    graines=(générateur, défauts) remplace les graines pour un contrôle sur des tirages indépendants."""
    options = {"graine": graines[0]} if graines else {}
    g, cr = bases.gse(h, base, credit, n=n, **options)
    if graines and hasattr(cr, "graine"):
        cr.graine = graines[1]
    res = projeter_stochastique(h, g, credit=cr, detail=True)
    s, tr = res["synthese"], res["trajectoires"]
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731
    ans = list(range(1, 11))
    T = h["horizon_annees"]
    resultat = lecture("resultat_assureur")[list(range(1, T + 1))].to_numpy()
    defl = lecture("deflateur")[list(range(1, T + 1))].to_numpy()
    impots = impots_par_scenario(resultat, h["fiscalite"]["unite_monetaire_eur"])
    va_impots = (impots * defl).sum(axis=1)
    rachat, servi, ref = lecture("taux_rachat"), lecture("taux_servi"), lecture("taux_10ans")
    pm, prest, pmv = lecture("pm"), lecture("prestations"), lecture("pmv_obligataires_realisees")
    sorties = prest[ans].to_numpy() / pm[[a - 1 for a in ans]].to_numpy()
    mv = -np.minimum(pmv[ans].to_numpy(), 0.0).sum(axis=1)
    apport0 = h["bilan_initial"].get("apport_initial", 0.0)
    valeur = s["valeur_assureur"]
    va_div = float(res["par_scenario"]["va_dividendes"].mean())
    return {
        "va_dividendes": va_div, "va_residuel_final": valeur - va_div + s["va_apports"] - s["fuite"],
        "actif": s["vm_actif_initial"], "be": s["be"], "ic_be": s["ic_be"], "fdb": s["fdb"], "fuite": s["fuite"], "ic_fuite": s["ic_fuite"],
        "valeur_avant_impot": valeur, "apport_initial": apport0, "va_apports_ulterieurs": s["va_apports"],
        "va_impots": float(va_impots.mean()),
        "valeur_nette": valeur - apport0 - float(va_impots.mean()),  # apports ultérieurs déjà déduits dans actif - BE
        "part_scenarios_avec_apport": s["part_scenarios_avec_apport"],
        "taux_servi_moyen_1_10": float(servi[ans].to_numpy().mean()),
        "ecart_taux_servi_reference_1_10": float((servi[ans].to_numpy() - ref[ans].to_numpy()).mean()),
        "taux_rachat_moyen_1_10": float(rachat[ans].to_numpy().mean()),
        "taux_rachat_max_1_10_q95": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.95)),
        "sorties_max_1_10_q99": float(np.quantile(sorties.max(axis=1), 0.99)),
        "moins_values_realisees_1_10_moyenne": float(mv.mean()), "moins_values_realisees_1_10_q99": float(np.quantile(mv, 0.99)),
        "pm_annee_10_moyenne": float(pm[10].mean()),
        **({"_valeurs_nettes": (res["par_scenario"]["vm_actif_initial"] - res["par_scenario"]["be"]).to_numpy() - apport0 - va_impots} if valeurs else {}),
    }


def resume_reel(h, tr, rendement_exige):
    """Indicateurs en probabilité réelle (conditionnels aux hypothèses du modèle), après impôt."""
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731
    ans = list(range(1, 11))
    res = lecture("resultat_assureur")[ans].to_numpy()
    impots = impots_par_scenario(res, h["fiscalite"]["unite_monetaire_eur"])
    net = res - impots
    fp = lecture("fonds_propres")
    fp_debut = fp[[a - 1 for a in ans]].to_numpy()
    apports = lecture("apport_assureur")
    denominateur = fp_debut.sum(axis=1)
    valides = denominateur > 0
    roe = net.sum(axis=1)[valides] / denominateur[valides]  # scénarios où les fonds propres restent positifs en moyenne
    servi, ref, rachat = lecture("taux_servi"), lecture("taux_10ans"), lecture("taux_rachat")
    pm, prest, pmv = lecture("pm"), lecture("prestations"), lecture("pmv_obligataires_realisees")
    sorties = prest[ans].to_numpy() / pm[[a - 1 for a in ans]].to_numpy()
    mv = -np.minimum(pmv[ans].to_numpy(), 0.0).sum(axis=1)
    T = apports.columns.max()
    a10 = apports[ans].to_numpy().sum(axis=1)
    aT = apports[list(range(1, T + 1))].to_numpy().sum(axis=1)
    return {
        "resultat_net_moyen_annuel_1_10": float(net.mean()),
        "rendement_fonds_propres_1_10_agrege": float(net.sum() / denominateur.sum()),
        "rendement_fonds_propres_1_10_median": float(np.median(roe)), "rendement_fonds_propres_1_10_q05": float(np.quantile(roe, 0.05)),
        "part_scenarios_fonds_propres_non_positifs": float(1 - valides.mean()),
        "ecart_au_rendement_exige": float(net.sum() / denominateur.sum() - rendement_exige),
        "dividendes_1_10_moyen": float(lecture("dividendes")[ans].to_numpy().sum(axis=1).mean()),
        "part_annees_en_perte_1_10": float((net < 0).mean()),
        "fonds_propres_annee_10_mediane": float(fp[10].median()),
        "probabilite_apport_10": float((a10 > 1e-9).mean()), "probabilite_apport_horizon": float((aT > 1e-9).mean()),
        "apports_horizon_q99": float(np.quantile(aT, 0.99)),
        "probabilite_fonds_propres_negatifs_10": float((fp[ans].to_numpy().min(axis=1) < 0).mean()),
        "taux_servi_moyen_1_10": float(servi[ans].to_numpy().mean()),
        "ecart_taux_servi_reference_1_10": float((servi[ans].to_numpy() - ref[ans].to_numpy()).mean()),
        "taux_rachat_moyen_1_10": float(rachat[ans].to_numpy().mean()),
        "taux_rachat_max_1_10_q99": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.99)),
        "sorties_max_1_10_q99": float(np.quantile(sorties.max(axis=1), 0.99)),
        "moins_values_realisees_1_10_q99": float(np.quantile(mv, 0.99)),
        "part_mv_realisees_au_dela_rc": float((mv > h["bilan_initial"]["reserve_capitalisation"]).mean()),
        "pm_annee_10_mediane": float(pm[10].median()),
    }
