"""V5 : stratégies ALM avec collecte nouvelle sensible au taux servi relatif.

Usage : python scripts/v5_collecte.py [--n 1000] [--processus 2]
Écrit resultats/v5_collecte.json (reprise possible depuis le cache resultats/cache_v5/collecte_n{n}/).

Base de capital commune à 100 % du SCR simplifié : chaque stratégie garde l'apport de
resultats/v5_consolidation.json, calculé sur l'existant en extinction (frontière des contrats) ; la
collecte ne le modifie pas. Mêmes scénarios et mêmes tirages de défaut pour toutes les stratégies, toutes
les intensités et toutes les élasticités.

1. Risque neutre : pour chaque profil et stratégie, l'existant en extinction (c0 = 0), puis chaque
   intensité c0 et chaque élasticité eta. Valeur de l'existant, valeur des affaires nouvelles et sa
   décomposition exacte, valeur totale ; écarts appariés à la gestion passive.
2. Probabilité réelle (intensité centrale, trois élasticités, et extinction) : collecte, PM,
   rentabilité, dividendes, apports, liquidité.
1 bis. Hypothèses du modèle de collecte : e0 = -0,5 point, horizon de collecte de 30 et 60 ans.
3. Sensibilité : loi de rachat ONC maximale, huit stratégies, intensité centrale.
"""

import argparse
import json
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.gse import demi_intervalle  # noqa: E402
from src.v5 import bases, collecte as col, conventions as cv, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.reel import projeter_reel_stochastique  # noqa: E402

CREDIT = "k70_granulaire_correle"
REFERENCE = "taux_servi_marche"
STRATEGIES_HYPOTHESES = ("passive", "taux_servi_marge", "taux_servi_competitif")


def hypotheses(p, code, apport, loi=None, c0=0.0, eta=0.0, remplacements=None):
    h = cv.appliquer(hypotheses_profil(p), REFERENCE, "sans_va", rachat_structurel="acpr", loi_rachat=loi)
    h = stg.appliquer_strategie(h, code, apport)
    return col.appliquer_collecte(h, c0, eta, **(remplacements or {})) if c0 else h


def t_rn(p, code, apport, n, c0, eta, loi=None, remplacements=None):
    h = hypotheses(p, code, apport, loi, c0, eta, remplacements)
    x = col.projection_risque_neutre(h, cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=n)
    ind = col.indicateurs_risque_neutre(x)
    x.pop("trajectoires")
    return {"par_scenario": x, "indicateurs": ind}


def t_diag(p, code, apport, n, c0, eta):
    h = hypotheses(p, code, apport, None, c0, eta)
    x = col.projection_risque_neutre(h, cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=n)
    return col.diagnostic_garanties(x)


def t_reel(p, code, apport, n, c0, eta):
    h = cv.hypotheses_reelles_stochastiques(hypotheses(p, code, apport, None, c0, eta))
    g, _ = bases.gse(h, "sans_va", None, n=n)
    tr = projeter_reel_stochastique(h, g, cv.credit_reel(CREDIT, "central", h["horizon_annees"]), cv.prime_actions_reelle())
    r = stg.resume_reel(h, tr, stg.charger()["rentabilite_reelle"]["rendement_exige"]["valeur"])
    r.update(col.indicateurs_reels(h, tr))
    return r


class Cache:
    def __init__(self, dossier):
        self.dossier = Path(dossier)
        self.dossier.mkdir(parents=True, exist_ok=True)

    def chemin(self, cle):
        return self.dossier / (cle.replace("|", "__") + ".pkl")

    def lire(self, cle):
        c = self.chemin(cle)
        return pickle.loads(c.read_bytes()) if c.exists() else None

    def ecrire(self, cle, valeur):
        self.chemin(cle).write_bytes(pickle.dumps(valeur))


def executer(ex, cache, taches):
    sortie, futurs = {}, {}
    for cle, (fn, args) in taches.items():
        x = cache.lire(cle)
        if x is None:
            futurs[ex.submit(fn, *args)] = cle
        else:
            sortie[cle] = x
    for i, f in enumerate(as_completed(futurs), 1):
        cle = futurs[f]
        sortie[cle] = f.result()
        cache.ecrire(cle, sortie[cle])
        print(f"  {i}/{len(futurs)} {cle}", flush=True)
    return sortie


def stat(x):
    x = np.asarray(x, dtype=float)
    return {"moyenne": float(x.mean()), "demi_intervalle_95": float(demi_intervalle(x))}


def cle(*parts):
    return "|".join(str(x) for x in parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    ap.add_argument("--cache", default=str(RACINE / "resultats" / "cache_v5"))
    ap.add_argument("--sortie", default=str(RACINE / "resultats" / "v5_collecte.json"))
    a = ap.parse_args()
    d = col.charger()
    codes = list(stg.charger()["strategies"])
    intensites = {k: v["c0"] for k, v in d["intensites"].items()}
    elasticites = {k: v["eta"] for k, v in d["elasticites"].items()}
    c0_central = intensites["centrale"]
    conso = json.loads((RACINE / "resultats" / "v5_consolidation.json").read_text(encoding="utf-8"))
    apports = {(p, c): conso["capital"][f"{p}|{c}"]["besoin"]["1.0"] for p in "ABC" for c in codes}
    cache = Cache(Path(a.cache) / f"collecte_n{a.n}")
    sortie = {"n_scenarios": a.n, "credit": CREDIT, "reference": REFERENCE, "strategies": codes, "intensites": intensites,
              "elasticites": elasticites, "base_capital": "apport propre à chaque stratégie pour 100 % du SCR simplifié (existant en extinction)",
              "apports": {cle(p, c): k for (p, c), k in apports.items()}, "risque_neutre": {}, "ecarts": {}, "reel": {},
              "sensibilite_onc_max": {}, "sensibilites_collecte": {}, "diagnostic_garanties": {}, "controles": {}}

    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        # 1. Risque neutre
        print("1. risque neutre", flush=True)
        taches = {cle("rn", p, c, 0, 0): (t_rn, (p, c, apports[(p, c)], a.n, 0.0, 0.0)) for p in "ABC" for c in codes}
        taches.update({cle("rn", p, c, c0, eta): (t_rn, (p, c, apports[(p, c)], a.n, c0, eta))
                       for p in "ABC" for c in codes for c0 in intensites.values() for eta in elasticites.values()})
        rn = executer(ex, cache, taches)
        ecart_decomposition, fuite = 0.0, []
        for p in "ABC":
            for c in codes:
                ferme = rn[cle("rn", p, c, 0, 0)]["par_scenario"]
                sortie["risque_neutre"][cle(p, c, 0, 0)] = {"valeur_existant": stat(ferme["valeur_nette"]), **rn[cle("rn", p, c, 0, 0)]["indicateurs"]}
                fuite.append(abs(ferme["fuite"].mean()) / max(demi_intervalle(ferme["fuite"]), 1e-12))
                for c0 in intensites.values():
                    for eta in elasticites.values():
                        avec = rn[cle("rn", p, c, c0, eta)]["par_scenario"]
                        dec = col.decomposer(avec, ferme)
                        ecart_decomposition = max(ecart_decomposition, float(np.abs(dec["valeur_affaires_nouvelles"] - dec["flux_contrats_nouveaux"] - dec["variation_be_existant"] - dec["impot_supplementaire"]).max()))
                        fuite.append(abs(avec["fuite"].mean()) / max(demi_intervalle(avec["fuite"]), 1e-12))
                        sortie["risque_neutre"][cle(p, c, c0, eta)] = {
                            "valeur_existant": stat(ferme["valeur_nette"]), "valeur_totale": stat(avec["valeur_nette"]),
                            **{k: stat(v) for k, v in dec.items()}, "va_primes": stat(avec["va_primes"]),
                            "marge_affaires_nouvelles": float(dec["valeur_affaires_nouvelles"].mean() / avec["va_primes"].mean()),
                            **rn[cle("rn", p, c, c0, eta)]["indicateurs"]}
            # Écarts appariés à la gestion passive, mêmes scénarios
            for c in codes:
                fp, fc = rn[cle("rn", p, "passive", 0, 0)]["par_scenario"], rn[cle("rn", p, c, 0, 0)]["par_scenario"]
                sortie["ecarts"][cle(p, c, 0, 0)] = {"existant": stat(fc["valeur_nette"] - fp["valeur_nette"])}
                for c0 in intensites.values():
                    for eta in elasticites.values():
                        ap_, ac = rn[cle("rn", p, "passive", c0, eta)]["par_scenario"], rn[cle("rn", p, c, c0, eta)]["par_scenario"]
                        sortie["ecarts"][cle(p, c, c0, eta)] = {
                            "existant": stat(fc["valeur_nette"] - fp["valeur_nette"]),
                            "affaires_nouvelles": stat((ac["valeur_nette"] - fc["valeur_nette"]) - (ap_["valeur_nette"] - fp["valeur_nette"])),
                            "totale": stat(ac["valeur_nette"] - ap_["valeur_nette"])}
        sortie["controles"] = {"ecart_max_decomposition": ecart_decomposition,
                               "fuite_moyenne_max_en_demi_intervalles": float(max(fuite))}

        # 1 bis. Hypothèses du modèle de collecte (e0, horizon de collecte) ; l'existant en extinction ne
        # dépend pas de ces hypothèses : il est repris de la grille principale (mêmes scénarios)
        print("1 bis. hypothèses de collecte", flush=True)
        sens = {k: v["remplacements"] for k, v in d["sensibilites"].items() if not k.startswith("_")}
        grille_s = [(c0, eta) for c0 in (intensites["centrale"], intensites["forte"]) for eta in (elasticites["moderee"], elasticites["soutenue"])]
        taches = {cle("hyp", s, p, c, c0, eta): (t_rn, (p, c, apports[(p, c)], a.n, c0, eta, None, rempl))
                  for s, rempl in sens.items() for p in "ABC" for c in STRATEGIES_HYPOTHESES for c0, eta in grille_s}
        hyp = executer(ex, cache, taches)
        for s in sens:
            for p in "ABC":
                for c in STRATEGIES_HYPOTHESES:
                    fc, fp = rn[cle("rn", p, c, 0, 0)]["par_scenario"], rn[cle("rn", p, "passive", 0, 0)]["par_scenario"]
                    for c0, eta in grille_s:
                        ac, ap_ = hyp[cle("hyp", s, p, c, c0, eta)]["par_scenario"], hyp[cle("hyp", s, p, "passive", c0, eta)]["par_scenario"]
                        sortie["sensibilites_collecte"][cle(s, p, c, c0, eta)] = {
                            "valeur_affaires_nouvelles": stat(ac["valeur_nette"] - fc["valeur_nette"]), "va_primes": stat(ac["va_primes"]),
                            "ecart_existant": stat(fc["valeur_nette"] - fp["valeur_nette"]),
                            "ecart_affaires_nouvelles": stat((ac["valeur_nette"] - fc["valeur_nette"]) - (ap_["valeur_nette"] - fp["valeur_nette"])),
                            "ecart_totale": stat(ac["valeur_nette"] - ap_["valeur_nette"])}
        del rn, hyp

        # 1 ter. Répartition des garanties entre l'existant et les contrats nouveaux
        taches = {cle("diag", p, c): (t_diag, (p, c, apports[(p, c)], a.n, c0_central, elasticites["moderee"])) for p in "ABC" for c in ("passive", "taux_servi_marge")}
        for k, v in executer(ex, cache, taches).items():
            sortie["diagnostic_garanties"][k.split("|", 1)[1]] = v

        # 2. Probabilité réelle (intensité centrale)
        print("2. probabilité réelle", flush=True)
        taches = {cle("reel2", p, c, 0, 0): (t_reel, (p, c, apports[(p, c)], a.n, 0.0, 0.0)) for p in "ABC" for c in codes}
        taches.update({cle("reel2", p, c, c0_central, eta): (t_reel, (p, c, apports[(p, c)], a.n, c0_central, eta))
                       for p in "ABC" for c in codes for eta in elasticites.values()})
        for k, v in executer(ex, cache, taches).items():
            sortie["reel"][k.split("|", 1)[1]] = v

        # 3. Sensibilité à la loi de rachat ONC maximale (intensité centrale)
        print("3. sensibilité ONC maximale", flush=True)
        taches = {cle("onc", p, c, 0, 0): (t_rn, (p, c, apports[(p, c)], a.n, 0.0, 0.0, "onc_max")) for p in "ABC" for c in codes}
        taches.update({cle("onc", p, c, c0_central, eta): (t_rn, (p, c, apports[(p, c)], a.n, c0_central, eta, "onc_max"))
                       for p in "ABC" for c in codes for eta in elasticites.values()})
        onc = executer(ex, cache, taches)
        for p in "ABC":
            fp = onc[cle("onc", p, "passive", 0, 0)]["par_scenario"]
            for c in codes:
                fc = onc[cle("onc", p, c, 0, 0)]["par_scenario"]
                sortie["sensibilite_onc_max"][cle(p, c, 0, 0)] = {"valeur_existant": stat(fc["valeur_nette"]), "ecart_existant": stat(fc["valeur_nette"] - fp["valeur_nette"])}
                for eta in elasticites.values():
                    ap_, ac = onc[cle("onc", p, "passive", c0_central, eta)]["par_scenario"], onc[cle("onc", p, c, c0_central, eta)]["par_scenario"]
                    dec = col.decomposer(ac, fc)
                    sortie["sensibilite_onc_max"][cle(p, c, c0_central, eta)] = {
                        "valeur_existant": stat(fc["valeur_nette"]), "valeur_totale": stat(ac["valeur_nette"]),
                        "valeur_affaires_nouvelles": stat(dec["valeur_affaires_nouvelles"]),
                        "ecart_existant": stat(fc["valeur_nette"] - fp["valeur_nette"]),
                        "ecart_affaires_nouvelles": stat((ac["valeur_nette"] - fc["valeur_nette"]) - (ap_["valeur_nette"] - fp["valeur_nette"])),
                        "ecart_totale": stat(ac["valeur_nette"] - ap_["valeur_nette"])}
    chemin = Path(a.sortie)
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
