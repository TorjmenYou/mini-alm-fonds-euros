"""V5 : première comparaison exploratoire des stratégies ALM sur les trois profils fictifs.

Usage : python scripts/v5_strategies.py [--n 1000] [--n-prudentiel 500] [--processus 2]
Écrit resultats/v5_strategies.json :
1. besoin d'apport initial pour porter l'indicateur de couverture simplifié du SCR à 100 % et 150 %
   (gestion passive, interpolation entre deux apports calculés, vérification au point à 100 %) ;
2. pour chaque profil, stratégie et base de capital (bilan initial, bilan recapitalisé à 100 %) :
   valorisation risque neutre (valeur nette des apports et de l'impôt), projection en probabilité
   réelle (rentabilité, recapitalisation, liquidité), vue prudentielle simplifiée à l'ouverture ;
3. sensibilité du classement risque neutre à trois conventions fragiles.
Conventions centrales : docs/V5_SYNTHESE_AVANT_OPTIMISATION.md, section 1.
"""

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import bases, conventions as cv, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.reel import projeter_reel_stochastique  # noqa: E402
from src.v5.solvabilite_v5 import bilan_prudentiel  # noqa: E402

CREDIT = "k70_granulaire_correle"
REFERENCE = "taux_servi_marche"
SENSIBILITES = {"reaction_onc_max": {"loi": "onc_max"}, "reference_immediate": {"reference": "sans_risque"},
                "defaut_bloc_souverain": {"credit": "k70_souverain_bloc"}}


def hypotheses(p, code, apport=0.0, reference=REFERENCE, loi=None):
    h = cv.appliquer(hypotheses_profil(p), reference, "sans_va", rachat_structurel="acpr", loi_rachat=loi)
    return stg.appliquer_strategie(h, code, apport)


def t_prudentiel(p, code, apport, n):
    h = hypotheses(p, code, apport)
    # la référence doit être calée sur la base avec VA pour la vue prudentielle
    h["comportement"] = cv.comportement(REFERENCE, "avec_va")
    r = bilan_prudentiel(h, CREDIT, "avec_va", n=n)
    return {k: r[k] for k in ("actif", "be", "fdb", "marge_de_risque", "fonds_excedentaires", "impots_differes_passif",
                              "impots_differes_actif_non_reconnus", "fonds_propres_niveau_1", "fonds_propres_comptables",
                              "scr", "mcr", "mcr_detail", "scr_net", "scr_brut", "ajustement_tp", "ajustement_impots_differes",
                              "risque_operationnel", "pertes_nettes", "indicateur_couverture_scr", "indicateur_couverture_mcr",
                              "indicateur_couverture_scr_avec_ida", "indicateur_couverture_scr_sans_fe", "actif_net_avant_impots")}


def t_q(p, code, apport, n, sens=None):
    o = SENSIBILITES.get(sens, {})
    h = hypotheses(p, code, apport, o.get("reference", REFERENCE), o.get("loi"))
    credit = cv.credit_valorisation(o.get("credit", CREDIT), "sans_va", h["horizon_annees"])
    return stg.resume_risque_neutre(h, credit, "sans_va", n)


def t_reel(p, code, apport, n):
    h = cv.hypotheses_reelles_stochastiques(hypotheses(p, code, apport))
    g, _ = bases.gse(h, "sans_va", None, n=n)
    tr = projeter_reel_stochastique(h, g, cv.credit_reel(CREDIT, "central", h["horizon_annees"]), cv.prime_actions_reelle())
    return stg.resume_reel(h, tr, stg.charger()["rentabilite_reelle"]["rendement_exige"]["valeur"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--n-prudentiel", type=int, default=500)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    codes = list(stg.charger()["strategies"])
    sortie = {"n_scenarios": a.n, "n_scenarios_prudentiel": a.n_prudentiel, "credit": CREDIT, "reference": REFERENCE,
              "capital": {}, "resultats": {}, "sensibilites": {}}
    chemin = RACINE / "resultats" / "v5_strategies.json"
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        # 1. Besoin d'apport (gestion passive) : deux points, puis interpolation linéaire
        zero = {p: ex.submit(t_prudentiel, p, "passive", 0.0, a.n_prudentiel) for p in "ABC"}
        zero = {p: f.result() for p, f in zero.items()}
        k1 = {p: max(zero[p]["scr"] - zero[p]["fonds_propres_niveau_1"], 20.0) for p in "ABC"}
        un = {p: ex.submit(t_prudentiel, p, "passive", k1[p], a.n_prudentiel) for p in "ABC"}
        un = {p: f.result() for p, f in un.items()}
        for p in "ABC":
            of0, scr0 = zero[p]["fonds_propres_niveau_1"], zero[p]["scr"]
            pa = (un[p]["fonds_propres_niveau_1"] - of0) / k1[p]
            pb = (un[p]["scr"] - scr0) / k1[p]
            besoin = {str(t): max((t * scr0 - of0) / (pa - t * pb), 0.0) for t in stg.charger()["capital"]["cibles_couverture_scr"]}
            sortie["capital"][p] = {"apport_0": zero[p], "apport_1": un[p], "apport_1_montant": k1[p],
                                    "pente_fonds_propres": pa, "pente_scr": pb, "besoin_apport": besoin}
            print(p, "besoins d'apport", {k: round(v, 1) for k, v in besoin.items()}, flush=True)
        chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")

        # 2. Grille des stratégies, bilans initial et recapitalisé
        taches = {}
        for p in "ABC":
            kp = sortie["capital"][p]["besoin_apport"]["1.0"]
            for base, apport in (("initial", 0.0), ("recapitalise", kp)):
                for code in codes:
                    cle = f"{p}|{base}|{code}"
                    taches[ex.submit(t_prudentiel, p, code, apport, a.n_prudentiel)] = (cle, "prudentiel")
                    taches[ex.submit(t_q, p, code, apport, a.n)] = (cle, "risque_neutre")
                    taches[ex.submit(t_reel, p, code, apport, a.n)] = (cle, "reel")
            for sens in SENSIBILITES:
                for code in codes:
                    taches[ex.submit(t_q, p, code, 0.0, a.n, sens)] = (f"{p}|{sens}|{code}", "sensibilite")
        for i, f in enumerate(as_completed(taches), 1):
            cle, groupe = taches[f]
            if groupe == "sensibilite":
                sortie["sensibilites"][cle] = f.result()
            else:
                sortie["resultats"].setdefault(cle, {})[groupe] = f.result()
            print(f"{i}/{len(taches)} {groupe} {cle}", flush=True)
            if i % 12 == 0:
                chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    sortie["resultats"] = dict(sorted(sortie["resultats"].items()))
    sortie["sensibilites"] = dict(sorted(sortie["sensibilites"].items()))
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
