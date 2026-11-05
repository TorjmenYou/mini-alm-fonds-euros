"""Projection sur l'ensemble des scénarios du GSE : Best Estimate et TVOG (V2)."""

import copy

import numpy as np
import pandas as pd

from .gse import GSE, demi_intervalle
from .projection import indicateurs, projeter, scenario


def projeter_stochastique(h, gse=None, choc_rachats=0.0, rachat_massif=0.0):
    """Projette le fonds sur chaque scénario et agrège les résultats.

    Renvoie :
    - par_scenario : un tableau d'indicateurs par trajectoire (BE, fuite...) ;
    - trajectoires : toutes les projections, indexées par (scénario, année) ;
    - moyennes : les trajectoires moyennes année par année ;
    - quantiles : les quantiles 5 % et 95 % de quelques variables ;
    - synthese : BE moyen, intervalle de confiance, fuite moyenne.
    """
    gse = gse or GSE(h)
    resultats, trajectoires = [], []
    for eco in gse.scenarios():
        df = projeter(h, eco, choc_rachats=choc_rachats, rachat_massif=rachat_massif, detail=False)
        resultats.append(indicateurs(df))
        trajectoires.append(df)

    par_scenario = pd.DataFrame(resultats)
    empile = pd.concat(trajectoires, keys=range(len(trajectoires)), names=["scenario", "annee"])
    variables = ["taux_10ans", "taux_servi", "taux_rachat", "pm", "ppb", "fonds_propres", "prestations"]
    moyennes = empile[variables].groupby(level="annee").mean()
    quantiles = empile[variables].groupby(level="annee").quantile([0.05, 0.95]).unstack()

    synthese = {"vm_actif_initial": par_scenario["vm_actif_initial"].iloc[0], "n_scenarios": len(par_scenario)}
    for col in ["be", "be_prestations", "be_frais", "be_garanti", "fdb", "fuite", "va_apports"]:
        synthese[col] = par_scenario[col].mean()
        synthese["ic_" + col] = demi_intervalle(par_scenario[col])
    synthese["valeur_assureur"] = synthese["vm_actif_initial"] - synthese["be"]
    # Situations à surveiller : apport de capital de l'assureur, fonds propres
    # comptables négatifs à un moment de la projection
    apports = empile["apport_assureur"].groupby(level="scenario").sum()
    fp_min = empile["fonds_propres"].groupby(level="scenario").min()
    synthese["part_scenarios_avec_apport"] = float((apports > 0).mean())
    synthese["part_scenarios_fp_negatifs"] = float((fp_min < 0).mean())
    return {"par_scenario": par_scenario, "trajectoires": empile, "moyennes": moyennes,
            "quantiles": quantiles, "synthese": synthese}


def tvog(h, resultat_stochastique):
    """Valeur temps des options et garanties : BE stochastique - BE équivalent certain.

    L'équivalent certain est le scénario déterministe où tous les actifs
    rapportent les taux forward de la courbe initiale (ici, le scénario central
    de la V1, courbe plate). L'écart mesure le coût des comportements
    asymétriques du passif face aux marchés ; decomposer_tvog en isole les sources.
    """
    be_ec = indicateurs(projeter(h, scenario(h, "central")))["be"]
    be_sto = resultat_stochastique["synthese"]["be"]
    return {"be_equivalent_certain": be_ec, "be_stochastique": be_sto, "tvog": be_sto - be_ec,
            "ic_tvog": resultat_stochastique["synthese"]["ic_be"]}


MECANISMES = {
    "plancher_tmg": "Plancher de taux servi (TMG)",
    "rachats_dynamiques": "Rachats dynamiques",
    "lissage_ppb": "Lissage par la PPB",
}


def variante(h, actifs):
    """Copie des hypothèses avec seulement les mécanismes de `actifs` en marche.

    - plancher_tmg désactivé : le taux servi peut descendre sous le TMG ;
    - rachats_dynamiques désactivés : rachats structurels seulement ;
    - lissage_ppb désactivé : plus aucune dotation à la PPB, le stock initial
      est redistribué normalement.
    """
    hv = copy.deepcopy(h)
    if "plancher_tmg" not in actifs:
        hv["strategie"]["appliquer_plancher_tmg"] = False
    if "rachats_dynamiques" not in actifs:
        hv["rachats_dynamiques"]["rc_max"] = 0.0
        hv["rachats_dynamiques"]["rc_min"] = 0.0
    if "lissage_ppb" not in actifs:
        hv["strategie"]["plafond_ppb_pct_pm"] = 0.0
    return hv


def decomposer_tvog(h, n=None):
    """TVOG pour les 8 combinaisons de mécanismes, et part de chacun (valeurs de Shapley).

    Les 8 combinaisons tournent sur les mêmes tirages. La valeur de Shapley d'un
    mécanisme est la moyenne de sa contribution marginale sur tous les ordres
    d'activation possibles : les effets d'interaction sont ainsi répartis à
    parts égales, au lieu d'être attribués au dernier mécanisme ajouté.
    Renvoie (tableau des 8 combinaisons, tableau de Shapley).
    """
    import itertools
    from math import factorial

    noms = list(MECANISMES)
    tvogs, lignes = {}, []
    for k in range(len(noms) + 1):
        for actifs in itertools.combinations(noms, k):
            hv = variante(h, set(actifs))
            res = projeter_stochastique(hv, GSE(hv, n=n))
            t = tvog(hv, res)
            tvogs[frozenset(actifs)] = t["tvog"]
            lignes.append({**{MECANISMES[m]: (m in actifs) for m in noms}, **t})
    combinaisons = pd.DataFrame(lignes)

    shapley = {}
    for m in noms:
        autres = [x for x in noms if x != m]
        valeur = 0.0
        for k in range(len(autres) + 1):
            poids = factorial(k) * factorial(len(noms) - k - 1) / factorial(len(noms))
            for sous in itertools.combinations(autres, k):
                s0 = frozenset(sous)
                valeur += poids * (tvogs[s0 | {m}] - tvogs[s0])
        shapley[MECANISMES[m]] = valeur
    shapley["Sans aucun des trois mécanismes"] = tvogs[frozenset()]
    shapley["TVOG du modèle complet"] = tvogs[frozenset(noms)]
    return combinaisons, pd.Series(shapley, name="TVOG")
