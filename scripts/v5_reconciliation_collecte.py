"""V5 : réconciliation des flux de collecte, résidu du contrat sans marge explicite, capital de la croissance
et seuil de coût du capital des affaires nouvelles.

Usage : python scripts/v5_reconciliation_collecte.py [--n 1000]
Écrit resultats/v5_reconciliation_collecte.json. Aucune nouvelle hypothèse de modèle : les données de
place viennent de data/v5/collecte/collecte.json (sources citées), les flux du modèle d'une projection en
probabilité réelle de la gestion passive (intensité centrale, eta = 0, donc g = 1), les besoins de capital
de resultats/v5_consolidation.json et les PM projetées de resultats/v5_collecte.json.

1. Place (observé, 2025 ; encours des contrats individuels en euros, flux des supports en euros) : PM de début et de fin, collecte brute et nette,
   intérêts crédités (taux moyen x PM moyenne, approximation), prélèvements sociaux, autres mouvements
   (résidu). Tout en % de la PM de début d'année.
2. Modèle (simulé) : mêmes postes en % de la PM de début d'année, année 1 et moyenne des années 1 à 10.
3. Contrat sans marge explicite dans le fonds mutualisé (équivalent certain ; identifiant
   « contrat_equitable » dans les résultats) : valeur des affaires nouvelles avant impôt, attribution de
   ce résidu aux postes comptables de fin de projection, et variantes de liquidation (réserve de
   capitalisation initiale nulle, fonds propres comptables non retenus, les deux).
4. Capital de la croissance (ordre de grandeur, pas une projection du SCR) : SCR simplifié à 100 % de
   couverture rapporté à la PM d'ouverture, appliqué à l'écart de PM médiane à 10 ans entre la collecte
   centrale et l'extinction.
5. Seuil de coût du capital des affaires nouvelles (analyse de seuil, aucun coût retenu) : charge
   frictionnelle annuelle sur un capital proxy qui annulerait la valeur centrale des affaires nouvelles,
   sur les scénarios risque neutre de cette valeur.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np


RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.projection import indicateurs, projeter  # noqa: E402
from src.v5 import bases, collecte as col, conventions as cv, strategies as stg  # noqa: E402
from src.v5.courbes_marche import courbe_eiopa  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.reel import projeter_reel_stochastique  # noqa: E402
from src.v5.scenarios import ScenarioCourbe  # noqa: E402

CREDIT = "k70_granulaire_correle"
REFERENCE = "taux_servi_marche"
C0_CENTRAL = 0.06
ETA_CENTRALE = 0.5

def hypotheses(p, code, apport, c0=0.0, eta=0.0):
    h = cv.appliquer(hypotheses_profil(p), REFERENCE, "sans_va", rachat_structurel="acpr")
    h = stg.appliquer_strategie(h, code, apport)
    return col.appliquer_collecte(h, c0, eta) if c0 else h


def place():
    """Agrégats de place 2025 (data/v5/collecte/collecte.json, rubrique place_2025) et postes dérivés."""
    donnees = col.charger()["place_2025"]
    x = {k: v["valeur"] for k, v in donnees.items() if not k.startswith("_")}
    pm0 = x["pm_debut"]
    x["prestations_implicites"] = x["collecte_brute"] - x["collecte_nette"]
    x["pm_moyenne"] = 0.5 * (x["pm_debut"] + x["pm_fin"])
    x["interets_credites_approx"] = x["taux_revalorisation"] * x["pm_moyenne"]
    x["prelevements_sociaux_approx"] = x["taux_prelevements_sociaux"] * x["interets_credites_approx"]
    x["autres_mouvements_residu"] = (x["pm_fin"] - pm0 - x["collecte_nette"] - x["interets_credites_approx"]
                                     + x["prelevements_sociaux_approx"])
    pct = {k: x[k] / pm0 for k in ("collecte_brute", "prestations_implicites", "collecte_nette", "interets_credites_approx",
                                    "prelevements_sociaux_approx", "autres_mouvements_residu")}
    pct["variation_pm"] = x["pm_fin"] / pm0 - 1
    x["en_pct_pm_debut"] = pct
    x["statut"] = {"observe": ["pm_debut", "pm_fin", "collecte_brute", "collecte_nette", "taux_revalorisation", "taux_prelevements_sociaux"],
                   "derive": ["prestations_implicites", "pm_moyenne", "interets_credites_approx", "prelevements_sociaux_approx"],
                   "residu": ["autres_mouvements_residu"]}
    x["sources"] = {k: v["source"] for k, v in donnees.items() if not k.startswith("_")}
    x["notes"] = ("Intérêts crédités approchés par le taux moyen appliqué à la moyenne des PM de début et de fin ; "
                  "encours : contrats individuels en euros (ACPR) ; flux : supports en euros (France Assureurs), "
                  "périmètres non strictement identiques ; le résidu regroupe les écarts de périmètre, les arbitrages "
                  "entre supports et les transferts.")
    return x


def flux_modele(p, apport, n):
    """Flux en % de la PM de début d'année, gestion passive, intensité centrale, eta = 0 (g = 1), réel."""
    h = cv.hypotheses_reelles_stochastiques(hypotheses(p, "passive", apport, C0_CENTRAL, 0.0))
    g, _ = bases.gse(h, "sans_va", None, n=n)
    tr = projeter_reel_stochastique(h, g, cv.credit_reel(CREDIT, "central", h["horizon_annees"]), cv.prime_actions_reelle())
    lec = lambda c: tr[c].unstack("annee")  # noqa: E731
    ans = list(range(1, 11))
    pm = lec("pm")
    debut = pm[[a - 1 for a in ans]].to_numpy()
    primes, deces, rachats = (lec(c)[ans].to_numpy() for c in ("primes", "deces", "rachats"))
    prest = lec("prestations")[ans].to_numpy()
    if lec("ppb_versee_extinction")[ans].to_numpy().any():
        raise AssertionError("PPB versée à l'extinction pendant les années 1 à 10 : l'identité des flux ne s'applique pas")
    fin = pm[ans].to_numpy()
    # Identité de la PM du modèle : PM(t) = PM(t - 1) + intérêts crédités - décès - rachats + primes portées
    # en PM (prime x (1 - chargement sur prime)), les primes étant versées en fin d'année.
    primes_en_pm = primes * (1.0 - h["collecte"]["contrats_nouveaux"]["chargement_prime"])
    interets = fin - debut - primes_en_pm + prest
    postes = {"collecte_brute": primes, "prestations": prest, "dont_deces": deces, "dont_rachats": rachats,
              "collecte_nette": primes - prest, "interets_credites": interets, "variation_pm": fin - debut}
    sortie = {}
    for k, v in postes.items():
        r = v / debut
        sortie[k] = {"annee_1": float(r[:, 0].mean()), "moyenne_1_10": float(r.mean())}
    sortie["taux_servi_moyen"] = {"annee_1": float(lec("taux_servi")[1].mean()),
                                  "moyenne_1_10": float(lec("taux_servi")[ans].to_numpy().mean())}
    return sortie


def termes_fin(d):
    T = d.index.max()
    D, f = d["deflateur"], d.loc[T]
    report = f["vnc_actif"] - f["pm"] - f["ppb"] - f["reserve_capitalisation"] - f["fonds_propres"] - f["dividende_a_payer"]
    pvl = f["vm_actif"] - f["vnc_actif"]
    return {"va_dividendes": float((d["dividendes"] * D).sum()), "va_apports": float(-(d["apport_assureur"] * D).sum()),
            "fonds_propres_final": float(f["fonds_propres"] * D[T]), "dividende_a_payer_final": float(f["dividende_a_payer"] * D[T]),
            "reserve_capitalisation_finale": float(f["reserve_capitalisation"] * D[T]), "report_final": float(report * D[T]),
            "pvl_finales_non_partagees": float((pvl - f["part_pvl_assures_fin"]) * D[T])}


def contrat_equitable(p, rc_initiale_nulle=False, sans_retention=False):
    """Contrat sans marge explicite : fonds mutualisé, équivalent certain, participation 100 %, sans PPB,
    chargement, frais ni TMG. Valeur des affaires nouvelles (avant impôt) et son attribution aux postes de
    fin de projection.

    Variantes de liquidation : rc_initiale_nulle reclasse la réserve de capitalisation d'ouverture en fonds
    propres comptables (actif inchangé, cible de distribution du profil inchangée) ; sans_retention
    distribue chaque année tous les fonds propres comptables positifs (cible nulle), si bien que la
    croissance ne retient plus de capital comptable. Les plus-values latentes d'ouverture restent celles du
    profil : les annuler demanderait un autre portefeuille."""
    h = hypotheses(p, "passive", 0.0)
    h["strategie"].update(participation_minimale=1.0, plafond_ppb_pct_pm=0.0)
    h["passif"].update(chargements_encours=0.0, frais_gestion_encours=0.0, tmg=0.0)
    if rc_initiale_nulle:
        b = h["bilan_initial"]
        b["fonds_propres"] += b["reserve_capitalisation"]
        b["reserve_capitalisation"] = 0.0
    if sans_retention:
        h["strategie_alm"]["distribution"]["fonds_propres_pct_pm"] = 0.0
    run = lambda x: projeter(x, ScenarioCourbe("ec", x["horizon_annees"], courbe_eiopa()),  # noqa: E731
                             credit=cv.credit_valorisation(CREDIT), detail=True)
    d0 = run(h)
    d1 = run(col.appliquer_collecte(h, C0_CENTRAL, 0.0, frais_acquisition_prime=0.0, chargement_prime=0.0))
    i0, i1 = indicateurs(d0), indicateurs(d1)
    t0, t1 = termes_fin(d0), termes_fin(d1)
    residu = i1["valeur_assureur"] - i0["valeur_assureur"]
    attribution = {k: t1[k] - t0[k] for k in t0}
    va = lambda d, c: float((d[c] * d["deflateur"]).sum())  # noqa: E731
    return {
        "va_primes": i1["va_primes"], "residu": residu, "residu_pct_va_primes": residu / i1["va_primes"],
        "attribution": attribution, "somme_attribution_plus_fuite": sum(attribution.values()) + i1["fuite"] - i0["fuite"],
        "fuite": {"ferme": i0["fuite"], "avec_collecte": i1["fuite"]},
        "pmv_obligataires_realisees_va": {"ferme": va(d0, "pmv_obligataires_realisees"), "avec_collecte": va(d1, "pmv_obligataires_realisees")},
        "pmvl_obligations_ouverture": float(d0.loc[0, "pmvl_obligations"]),
        "flux_contrats_nouveaux": i1["va_primes_moins_be_nouveaux"],
        "va_apports": {"ferme": va(d0, "apport_assureur"), "avec_collecte": va(d1, "apport_assureur")},
        "annees_avec_apport_ferme": [int(t) for t in d0.index[d0["apport_assureur"] > 1e-9]],
        "taux_servi_min_ferme": float(d0["taux_servi"].iloc[1:].min()),
    }


VARIANTES_LIQUIDATION = {"rc_initiale_nulle": {"rc_initiale_nulle": True},
                         "sans_retention": {"sans_retention": True},
                         "rc_initiale_nulle_sans_retention": {"rc_initiale_nulle": True, "sans_retention": True}}


def variantes_liquidation(p):
    return {nom: contrat_equitable(p, **kw) for nom, kw in VARIANTES_LIQUIDATION.items()}


def scr_a_100(K, p, code):
    """SCR simplifié à 100 % de couverture : contrôle direct s'il existe, sinon interpolation linéaire en
    fonction de l'apport, comme pour le besoin d'apport de la consolidation (SCR sans apport + pente du SCR
    x apport à 100 %)."""
    v = K["verification"].get(f"{p}|{code}|1.0")
    if v is not None:
        return v["scr"], "contrôle à 100 %"
    c = K["capital"][f"{p}|{code}"]
    return K["prudentiel"][f"{p}|{code}"]["apport_0"]["scr"] + c["pente_scr"] * c["besoin"]["1.0"], "interpolation linéaire en l'apport"


def capital_croissance(R, K):
    """Ordre de grandeur : SCR à 100 % / PM0 x (PM médiane à 10 ans avec collecte - en extinction).
    Hypothèse : SCR proportionnel à la PM, au ratio d'ouverture ; ce n'est pas une projection du SCR."""
    sortie = {}
    for p in "ABC":
        pm0 = hypotheses_profil(p)["bilan_initial"]["pm"]
        for code in R["strategies"]:
            scr, methode = scr_a_100(K, p, code)
            ratio = scr / pm0
            ferme = R["reel"][f"{p}|{code}|0|0"]
            lignes = {}
            for nom, eta in R["elasticites"].items():
                x = R["reel"].get(f"{p}|{code}|{C0_CENTRAL}|{eta}")
                if x is None:
                    continue
                dpm = x["pm_annee_10_mediane"] - ferme["pm_annee_10_mediane"]
                lignes[nom] = {"eta": eta, "pm_10_mediane": x["pm_annee_10_mediane"], "ecart_pm_10": dpm,
                               "scr_supplementaire_proportionnel": ratio * dpm,
                               "fonds_propres_10_mediane": x["fonds_propres_annee_10_mediane"]}
            sortie[f"{p}|{code}"] = {"pm0": pm0, "scr_100": scr, "methode_scr_100": methode, "scr_sur_pm0": ratio,
                                     "pm_10_mediane_extinction": ferme["pm_annee_10_mediane"],
                                     "fonds_propres_10_mediane_extinction": ferme["fonds_propres_annee_10_mediane"],
                                     "collecte_centrale": lignes}
    return sortie


def seuil_cout_capital(R, K, p, n):
    """Analyse de seuil, pas un coût du capital retenu. Capital proxy des affaires nouvelles, scénario par
    scénario : K(t) = SCR à 100 % / PM0 x (PM avec collecte - PM en extinction), mêmes scénarios risque
    neutre que la valeur publiée (gestion passive, c0 central, eta modérée, base sans VA). Une charge
    frictionnelle kappa x K(t - 1), payée en fin d'année t et actualisée au déflateur, réduit la valeur des
    affaires nouvelles de kappa x S, avec S = somme sur t de E^Q[D(t) K(t - 1)]. Seuil : kappa* = VAN / S.

    kappa est une charge supplémentaire hypothétique, nette des coûts déjà valorisés (impôt et participation
    sur les revenus du capital comptable retenu) ; ce n'est ni le rendement exigé en probabilité réelle, ni
    le taux de la marge de risque Solvabilité II, qui ont d'autres usages."""
    apport = R["apports"][f"{p}|passive"]
    h0 = hypotheses(p, "passive", apport)
    h1 = hypotheses(p, "passive", apport, C0_CENTRAL, ETA_CENTRALE)
    credit = cv.credit_valorisation(CREDIT, "sans_va", h1["horizon_annees"])
    x0 = col.projection_risque_neutre(h0, credit, n=n)
    x1 = col.projection_risque_neutre(h1, credit, n=n)
    van = col.decomposer(x1, x0)["valeur_affaires_nouvelles"]
    T = h1["horizon_annees"]
    lire = lambda x, c, ans: col._lecture(x["trajectoires"], c)[ans].to_numpy()  # noqa: E731
    d0, d1 = lire(x0, "deflateur", list(range(1, T + 1))), lire(x1, "deflateur", list(range(1, T + 1)))
    if np.abs(d0 - d1).max() > 1e-12:
        raise AssertionError("Seuil de coût du capital : les deux projections n'ont pas les mêmes scénarios")
    dpm = lire(x1, "pm", list(range(T))) - lire(x0, "pm", list(range(T)))
    scr, methode = scr_a_100(K, p, "passive")
    pm0 = hypotheses_profil(p)["bilan_initial"]["pm"]
    s = (scr / pm0) * (dpm * d1).sum(axis=1)
    publiee = R["risque_neutre"][f"{p}|passive|{C0_CENTRAL}|{ETA_CENTRALE}"]["valeur_affaires_nouvelles"]
    m, hw = float(van.mean()), publiee["demi_intervalle_95"]  # intervalle publié (paires antithétiques)
    if abs(m - publiee["moyenne"]) > 1e-6 * max(1.0, abs(publiee["moyenne"])):
        raise AssertionError(f"Seuil de coût du capital, {p} : VAN recalculée {m} différente de la valeur publiée {publiee['moyenne']}")
    S = float(s.mean())
    return {"c0": C0_CENTRAL, "eta": ETA_CENTRALE, "n_scenarios": n, "van_affaires_nouvelles": m,
            "van_demi_intervalle_95": hw, "scr_100": scr, "methode_scr_100": methode, "scr_sur_pm0": scr / pm0,
            "va_capital_proxy": S, "kappa_seuil": m / S, "kappa_seuil_bornes": [(m - hw) / S, (m + hw) / S]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--sortie", default=str(RACINE / "resultats" / "v5_reconciliation_collecte.json"))
    a = ap.parse_args()
    R = json.loads((RACINE / "resultats" / "v5_collecte.json").read_text(encoding="utf-8"))
    K = json.loads((RACINE / "resultats" / "v5_consolidation.json").read_text(encoding="utf-8"))
    sortie = {
        "n_scenarios_reels": a.n, "c0_central": C0_CENTRAL,
        "place_2025": place(),
        "modele": {p: flux_modele(p, R["apports"][f"{p}|passive"], a.n) for p in "ABC"},
        "contrat_equitable": {p: contrat_equitable(p) for p in "ABC"},
        "variantes_liquidation": {p: variantes_liquidation(p) for p in "ABC"},
        "capital_croissance": capital_croissance(R, K),
        "seuil_cout_capital": {p: seuil_cout_capital(R, K, p, R["n_scenarios"]) for p in "ABC"},
    }
    Path(a.sortie).write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"écrit {a.sortie}")


if __name__ == "__main__":
    main()
