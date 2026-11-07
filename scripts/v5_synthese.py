"""V5 : calculs de la synthèse avant optimisation (conventions de sécurisation).

Usage : python scripts/v5_synthese.py [--n 1000] [--processus 2]
Écrit resultats/v5_synthese.json :
- risque neutre, stochastique : convention centrale et sensibilités (référence, délai de lissage,
  réaction des assurés, rachat structurel, part de crédit, recouvrement, structure de défaut, spread, VA) ;
- équivalents certains et durations ;
- attribution de la baisse de valeur due au défaut par saut (passif figé, participation sans
  rachats dynamiques, modèle complet) ;
- probabilité réelle, stochastique : apports, fonds propres négatifs, liquidité ;
- vue prudentielle complétée (bases sans et avec VA).
"""

import argparse
import copy
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import bases, conventions as cv  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.reel import projeter_reel_stochastique, resume_reel  # noqa: E402
from src.v5.solvabilite_v5 import bilan_prudentiel  # noqa: E402
from src.v5.syntheses import resume_ec, resume_stochastique  # noqa: E402

CENTRE = {"reference": "taux_servi_marche", "credit": "k70_granulaire_correle", "rachat": "acpr", "loi": None, "base": "sans_va"}
SENSIBILITES = {
    "centre": {},
    "reference_lisse_3": {"reference": "lisse_3"}, "reference_lisse_5": {"reference": "lisse_5"},
    "reference_lisse_10": {"reference": "lisse_10"}, "reference_composite_observe": {"reference": "composite_observe"},
    "reference_sans_risque_immediate": {"reference": "sans_risque"}, "reference_figee": {"reference": "figee"},
    "reaction_onc_min": {"loi": "onc_min"}, "reaction_onc_max": {"loi": "onc_max"},
    "rachat_structurel_5": {"rachat": 0.05},
    "credit_kappa_55": {"credit": "k55_granulaire_correle"}, "credit_kappa_100": {"credit": "k100_granulaire_correle"},
    "credit_recouvrement_63": {"credit": "k70_granulaire_correle_r63"},
    "credit_lisse": {"credit": "k_lisse_bootstrap"},
    "structure_granulaire_independant": {"credit": "k70_granulaire_independant"},
    "structure_souverain_granulaire_correle": {"credit": "k70_souverain_granulaire_correle"},
    "structure_souverain_bloc": {"credit": "k70_souverain_bloc"},
    "structure_bloc_unique": {"credit": "k70_bloc_unique"},
    "spread_plus_100": {"choc_spread": 0.01},
    "base_avec_va": {"base": "avec_va"},
}
REELLES = {"central": {}, "stress_rapport_2": {"reel": "stress_rapport_2"}, "rachat_structurel_5": {"rachat": 0.05},
           "reference_sans_risque_immediate": {"reference": "sans_risque"}, "structure_souverain_bloc": {"credit": "k70_souverain_bloc"}}


def conv(o):
    c = dict(CENTRE)
    c.update(o)
    return c


def hypotheses(p, c):
    return cv.appliquer(hypotheses_profil(p), c["reference"], c["base"], rachat_structurel=c["rachat"], loi_rachat=c["loi"])


def credit_de(c, h):
    cr = cv.credit_valorisation(c["credit"], "sans_va", h["horizon_annees"])
    if c.get("choc_spread"):
        cr = cr.copie()
        cr.choquer(c["choc_spread"])
    return cr


def tache_q(p, nom, n):
    c = conv(SENSIBILITES[nom])
    h = hypotheses(p, c)
    return resume_stochastique(h, credit_de(c, h), c["base"], n)


def attribution_h(h, config):
    """C0 : passif indépendant des actifs ; C1 : participation et TMG, sans rachats dynamiques ; C2 : complet."""
    h = copy.deepcopy(h)
    if config in ("C0", "C1"):
        h["rachats_dynamiques"].update(rc_max=0.0, rc_min=0.0)
    if config == "C0":
        h["strategie"].update(participation_minimale=0.0, abandon_marge_assureur=False, ecart_taux_cible=-1.0)
    return h


def tache_attribution(p, config, credit, n):
    c = conv({"credit": credit})
    h = attribution_h(hypotheses(p, c), config)
    r = resume_stochastique(h, credit_de(c, h), "sans_va", n)
    return {k: r[k] for k in ("be", "ic_be", "valeur", "fdb", "be_garanti", "fuite", "ic_fuite", "part_scenarios_avec_apport")}


def tache_reel(p, nom, n):
    o = REELLES[nom]
    c = conv({k: v for k, v in o.items() if k != "reel"})
    h = cv.hypotheses_reelles_stochastiques(hypotheses(p, c))
    g, _ = bases.gse(h, "sans_va", None, n=n)
    tr = projeter_reel_stochastique(h, g, cv.credit_reel(c["credit"], o.get("reel", "central"), h["horizon_annees"]), cv.prime_actions_reelle())
    return resume_reel(h, tr)


def tache_prudentiel(p, base, n):
    c = conv({"base": base})
    h = hypotheses(p, c)
    return bilan_prudentiel(h, c["credit"], base, n=n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    sortie = {"unites": "unités fictives, 1 unité = 10 M EUR ; avant impôt sauf vue prudentielle", "n_scenarios": a.n,
              "centre": CENTRE, "sensibilites": SENSIBILITES, "reelles": REELLES,
              "q": {}, "ec": {}, "attribution": {}, "reel": {}, "prudentiel": {}}
    for p in "ABC":
        for nom, o in SENSIBILITES.items():
            if nom.startswith(("credit_", "structure_", "spread_")) and nom != "credit_lisse":
                continue  # l'équivalent certain ne dépend que du spread moyen
            c = conv(o)
            h = hypotheses(p, c)
            sortie["ec"][f"{p}|{nom}"] = resume_ec(h, credit_de(c, h), c["base"])
    print("équivalents certains : faits", flush=True)
    chemin = RACINE / "resultats" / "v5_synthese.json"
    taches = {}
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        for p in "ABC":
            for base in ("sans_va", "avec_va"):
                taches[ex.submit(tache_prudentiel, p, base, a.n)] = ("prudentiel", f"{p}|{base}")
        for p in "ABC":
            for nom in SENSIBILITES:
                taches[ex.submit(tache_q, p, nom, a.n)] = ("q", f"{p}|{nom}")
            for nom in REELLES:
                taches[ex.submit(tache_reel, p, nom, a.n)] = ("reel", f"{p}|{nom}")
        for p in "AB":
            for config in ("C0", "C1", "C2"):
                for credit in ("k_lisse_bootstrap", "k70_souverain_bloc"):
                    taches[ex.submit(tache_attribution, p, config, credit, a.n)] = ("attribution", f"{p}|{config}|{credit}")
        for i, f in enumerate(as_completed(taches), 1):
            groupe, cle = taches[f]
            sortie[groupe][cle] = f.result()
            print(f"{i}/{len(taches)} {groupe} {cle}", flush=True)
            if i % 10 == 0:
                chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    for g in ("q", "attribution", "reel", "prudentiel"):
        sortie[g] = dict(sorted(sortie[g].items()))
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
