"""V5 : consolidation de la comparaison des stratégies ALM sur une base de capital commune.

Usage : python scripts/v5_consolidation.py [--n-prudentiel 2000] [--n 1000] [--tirages 1000] [--processus 2]
                                           [--variante reference]
Écrit resultats/v5_consolidation.json (reprise possible : les calculs déjà faits sont relus depuis le
cache, par défaut resultats/cache_v5/, non versionné). Avec --variante (src/v5/variantes_audit.py,
autre que « reference »), écrit resultats/v5_audit_consolidation_<variante>.json, mêmes scénarios.

1. Vue prudentielle simplifiée à n_prudentiel scénarios (base avec VA), pour chaque profil et chaque
   stratégie, en deux points d'apport (0 et un apport proche du besoin à 125 %). Besoins d'apport à 100 %
   et 150 % du SCR simplifié par interpolation linéaire, propres à chaque stratégie. Incertitude
   Monte-Carlo par rééchantillonnage des paires antithétiques, les mêmes paires pour les deux points et
   pour tous les chocs (mêmes scénarios).
2. Vérification de l'interpolation : vue prudentielle recalculée aux apports obtenus (gestion passive à
   100 % et 150 %, politique de marge à 100 %).
3. Base de capital commune : chaque stratégie reçoit l'apport qui porte son propre indicateur à la
   cible (100 % ou 150 %). Valeur nette risque neutre (nette de cet apport et de l'impôt), écarts appariés
   à la gestion passive, indicateurs en probabilité réelle. Bilan initial (sans apport) en complément.
4. Sensibilités de la valeur nette à la base 100 % (apports du centre) : réaction ONC maximale,
   transmission immédiate des taux, défaut corrélé par bloc souverain.
5. Contrôle de l'écart du réinvestissement progressif sur des tirages indépendants (profil A, base 100 %).
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
from src.v5 import bases, conventions as cv, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402
from src.v5.reel import projeter_reel_stochastique  # noqa: E402
from src.v5.solvabilite_v5 import bilan_prudentiel, reagreger  # noqa: E402
from src.v5.variantes_audit import VARIANTES, appliquer_variante  # noqa: E402

CREDIT = "k70_granulaire_correle"
REFERENCE = "taux_servi_marche"
CIBLES = (1.0, 1.5)
SENSIBILITES = {"reaction_onc_max": {"loi": "onc_max"}, "reference_immediate": {"reference": "sans_risque"},
                "defaut_bloc_souverain": {"credit": "k70_souverain_bloc"}}
GRAINES_CONTROLE = (4049, 9173)
CLES_PRUDENTIELLES = ("actif", "be", "ic_be", "fdb", "marge_de_risque", "fonds_excedentaires", "ppb_admissible", "ppb_comptable", "impots_differes_passif",
                      "fonds_propres_niveau_1", "fonds_propres_comptables", "scr", "mcr", "mcr_detail", "scr_net", "scr_brut",
                      "ajustement_tp", "ajustement_impots_differes", "risque_operationnel", "pertes_nettes",
                      "indicateur_couverture_scr", "indicateur_couverture_mcr")


def hypotheses(p, code, apport=0.0, reference=REFERENCE, loi=None, variante="reference"):
    h = cv.appliquer(hypotheses_profil(p), reference, "sans_va", rachat_structurel="acpr", loi_rachat=loi)
    h = stg.appliquer_strategie(h, code, apport)
    return h if variante == "reference" else appliquer_variante(h, variante)


def t_prudentiel(p, code, apport, n, variante="reference"):
    h = hypotheses(p, code, apport, variante=variante)
    h["comportement"] = cv.comportement(REFERENCE, "avec_va")  # référence calée sur la base avec VA
    r = bilan_prudentiel(h, CREDIT, "avec_va", n=n, echantillons=True)
    return {"resume": {k: r[k] for k in CLES_PRUDENTIELLES}, "tirages": r["_tirages"], "contexte": r["_contexte"]}


def t_rn(p, code, apport, n, sens=None, graines=None, variante="reference"):
    o = SENSIBILITES.get(sens, {})
    h = hypotheses(p, code, apport, o.get("reference", REFERENCE), o.get("loi"), variante)
    credit = cv.credit_valorisation(o.get("credit", CREDIT), "sans_va", h["horizon_annees"])
    r = stg.resume_risque_neutre(h, credit, "sans_va", n, valeurs=True, graines=graines)
    v = r.pop("_valeurs_nettes")
    return {"resume": r, "valeurs": v}


def t_reel(p, code, apport, n, variante="reference"):
    h = cv.hypotheses_reelles_stochastiques(hypotheses(p, code, apport, variante=variante))
    g, _ = bases.gse(h, "sans_va", None, n=n)
    tr = projeter_reel_stochastique(h, g, cv.credit_reel(CREDIT, "central", h["horizon_annees"]), cv.prime_actions_reelle())
    return {"resume": stg.resume_reel(h, tr, stg.charger()["rentabilite_reelle"]["rendement_exige"]["valeur"])}


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
    """taches : {clé: (fonction, arguments)} ; renvoie {clé: résultat}, en relisant le cache."""
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


def indicateurs_reechantillon(r, idx):
    x = reagreger({"_tirages": r["tirages"], "_contexte": r["contexte"]}, idx)
    return x["fonds_propres_niveau_1"], x["scr"], x["mcr"]


def besoin(of0, scr0, of1, scr1, k1, cible):
    pa, pb = (of1 - of0) / k1, (scr1 - scr0) / k1
    return max((cible * scr0 - of0) / (pa - cible * pb), 0.0)


def intervalle(x):
    x = np.asarray(x)
    return {"q025": float(np.quantile(x, 0.025)), "q975": float(np.quantile(x, 0.975)), "ecart_type": float(x.std(ddof=1))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-prudentiel", type=int, default=2000)
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--tirages", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    ap.add_argument("--cache", default=str(RACINE / "resultats" / "cache_v5"))
    ap.add_argument("--sortie", default=None)
    ap.add_argument("--variante", default="reference", choices=VARIANTES)
    a = ap.parse_args()
    variante = a.variante
    if a.sortie is None:
        a.sortie = str(RACINE / "resultats" / ("v5_consolidation.json" if variante == "reference" else f"v5_audit_consolidation_{variante}.json"))
    codes = list(stg.charger()["strategies"])
    cache = Cache(Path(a.cache) / (f"np{a.n_prudentiel}_n{a.n}" + ("" if variante == "reference" else f"_{variante}")))
    ancien = json.loads((RACINE / "resultats" / "v5_strategies.json").read_text(encoding="utf-8"))
    sortie = {"n_scenarios_prudentiel": a.n_prudentiel, "n_scenarios": a.n, "tirages_reechantillonnage": a.tirages, "credit": CREDIT,
              "reference": REFERENCE, "cibles": list(CIBLES), "strategies": codes, "prudentiel": {}, "capital": {}, "verification": {},
              "risque_neutre": {}, "reel": {}, "ecarts": {}, "sensibilites": {}, "controle_reinvestissement": {}}
    if variante != "reference":
        sortie["variante"] = variante
    chemin = Path(a.sortie)

    def ecrire():
        chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")

    rng = np.random.default_rng(20261106)
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        # 1. Deux points d'apport par profil et stratégie
        k1 = {}
        for p in "ABC":
            x = ancien["capital"][p]["apport_0"]
            k_passive = max((1.25 * x["scr"] - x["fonds_propres_niveau_1"]) / 0.97, 20.0)
            for c in codes:
                y = ancien["resultats"].get(f"{p}|initial|{c}", {}).get("prudentiel")
                k1[(p, c)] = max((1.25 * y["scr"] - y["fonds_propres_niveau_1"]) / 0.97, 20.0) if y else k_passive
        print("1. vue prudentielle, deux points d'apport", flush=True)
        taches = {f"prudentiel|{p}|{c}|{pt}": (t_prudentiel, (p, c, 0.0 if pt == 0 else k1[(p, c)], a.n_prudentiel, variante))
                  for p in "ABC" for c in codes for pt in (0, 1)}
        pru = executer(ex, cache, taches)
        moitie = a.n_prudentiel // 2
        idx = rng.integers(0, moitie, size=(a.tirages, moitie))  # mêmes rééchantillons pour toutes les stratégies
        echantillons = {}
        for p in "ABC":
            for c in codes:
                r0, r1, kk = pru[f"prudentiel|{p}|{c}|0"], pru[f"prudentiel|{p}|{c}|1"], k1[(p, c)]
                s0, s1 = r0["resume"], r1["resume"]
                b = {str(t): besoin(s0["fonds_propres_niveau_1"], s0["scr"], s1["fonds_propres_niveau_1"], s1["scr"], kk, t) for t in CIBLES}
                ech = {"of": [], "scr": [], "ratio": [], "ratio_mcr": [], **{str(t): [] for t in CIBLES}}
                for i in range(a.tirages):
                    of0, scr0, mcr0 = indicateurs_reechantillon(r0, idx[i])
                    of1, scr1, _ = indicateurs_reechantillon(r1, idx[i])
                    ech["of"].append(of0)
                    ech["scr"].append(scr0)
                    ech["ratio"].append(of0 / scr0)
                    ech["ratio_mcr"].append(of0 / mcr0)
                    for t in CIBLES:
                        ech[str(t)].append(besoin(of0, scr0, of1, scr1, kk, t))
                sortie["prudentiel"][f"{p}|{c}"] = {"apport_0": s0, "apport_1": s1, "apport_1_montant": kk,
                                                    "incertitude_apport_0": {k: intervalle(ech[k]) for k in ("of", "scr", "ratio", "ratio_mcr")},
                                                    "demi_intervalle_be_apport_0": float(demi_intervalle(r0["tirages"]["base"]["be"]))}
                echantillons[(p, c)] = ech
                sortie["capital"][f"{p}|{c}"] = {"besoin": b, "incertitude": {t: intervalle(ech[t]) for t in b},
                                                 "pente_fonds_propres": (s1["fonds_propres_niveau_1"] - s0["fonds_propres_niveau_1"]) / kk,
                                                 "pente_scr": (s1["scr"] - s0["scr"]) / kk}
            for c in codes:  # écarts à la gestion passive sur les mêmes rééchantillons
                ref, ech = echantillons[(p, "passive")], echantillons[(p, c)]
                sortie["capital"][f"{p}|{c}"]["ecart_passive"] = {t: intervalle(np.subtract(ech[t], ref[t])) for t in map(str, CIBLES)}
                sortie["prudentiel"][f"{p}|{c}"]["ecart_ratio_passive"] = intervalle(np.subtract(ech["ratio"], ref["ratio"]))
            print(p, "besoins (passive)", {t: round(v, 1) for t, v in sortie["capital"][f"{p}|passive"]["besoin"].items()}, flush=True)
        del pru
        ecrire()

        # 2. Vérification de l'interpolation
        print("2. vérification de l'interpolation", flush=True)
        # passive aux deux cibles, politique de marge pour les trois profils, et toutes les stratégies de A à 100 % :
        # pour A, le plafond de l'absorption par les FDB rend la relation entre apport et indicateur non linéaire
        verif = [(p, "passive", t) for p in "ABC" for t in CIBLES] + [(p, "taux_servi_marge", 1.0) for p in "ABC"] \
            + [("A", c, 1.0) for c in codes if c not in ("passive", "taux_servi_marge")]
        taches = {f"verification|{p}|{c}|{t}": (t_prudentiel, (p, c, sortie["capital"][f"{p}|{c}"]["besoin"][str(t)], a.n_prudentiel, variante)) for p, c, t in verif}
        for cle, r in executer(ex, cache, taches).items():
            _, p, c, t = cle.split("|")
            sortie["verification"][f"{p}|{c}|{t}"] = {"apport": sortie["capital"][f"{p}|{c}"]["besoin"][t],
                                                     "indicateur_couverture_scr": r["resume"]["indicateur_couverture_scr"],
                                                     "fonds_propres_niveau_1": r["resume"]["fonds_propres_niveau_1"], "scr": r["resume"]["scr"]}
        ecrire()

        # 3. Base de capital commune (et bilan initial)
        print("3. valeur et rentabilité sur la base de capital commune", flush=True)
        apports = {(p, c, "0"): 0.0 for p in "ABC" for c in codes}
        apports.update({(p, c, str(t)): sortie["capital"][f"{p}|{c}"]["besoin"][str(t)] for p in "ABC" for c in codes for t in CIBLES})
        taches = {}
        for (p, c, base), k in apports.items():
            taches[f"rn|{p}|{c}|{base}"] = (t_rn, (p, c, k, a.n, None, None, variante))
            taches[f"reel|{p}|{c}|{base}"] = (t_reel, (p, c, k, a.n, variante))
        res = executer(ex, cache, taches)
        for (p, c, base) in apports:
            q, re = res[f"rn|{p}|{c}|{base}"], res[f"reel|{p}|{c}|{base}"]
            sortie["risque_neutre"][f"{p}|{c}|{base}"] = q["resume"]
            sortie["reel"][f"{p}|{c}|{base}"] = re["resume"]
            e = q["valeurs"] - res[f"rn|{p}|passive|{base}"]["valeurs"]
            sortie["ecarts"][f"{p}|{c}|{base}"] = {"ecart_moyen": float(e.mean()), "demi_intervalle_95": float(demi_intervalle(e)) if c != "passive" else 0.0}
        ecrire()

        # 4. Sensibilités de la valeur à la base 100 %
        print("4. sensibilités", flush=True)
        taches = {f"sens|{p}|{c}|{s}": (t_rn, (p, c, apports[(p, c, "1.0")], a.n, s, None, variante)) for p in "ABC" for c in codes for s in SENSIBILITES}
        sens = executer(ex, cache, taches)
        for p in "ABC":
            for s in SENSIBILITES:
                for c in codes:
                    e = sens[f"sens|{p}|{c}|{s}"]["valeurs"] - sens[f"sens|{p}|passive|{s}"]["valeurs"]
                    sortie["sensibilites"][f"{p}|{c}|{s}"] = {"valeur_nette": sens[f"sens|{p}|{c}|{s}"]["resume"]["valeur_nette"], "ecart_moyen": float(e.mean()),
                                                               "demi_intervalle_95": float(demi_intervalle(e)) if c != "passive" else 0.0}
        ecrire()

        # 5. Contrôle du réinvestissement progressif sur des tirages indépendants
        print("5. contrôle du réinvestissement progressif", flush=True)
        taches = {f"controle|A|{c}": (t_rn, ("A", c, apports[("A", c, "1.0")], 2 * a.n, None, GRAINES_CONTROLE, variante)) for c in ("passive", "reinvestissement_progressif")}
        ctl = executer(ex, cache, taches)
        e = ctl["controle|A|reinvestissement_progressif"]["valeurs"] - ctl["controle|A|passive"]["valeurs"]
        sortie["controle_reinvestissement"] = {"graines": list(GRAINES_CONTROLE), "n_scenarios": 2 * a.n, "ecart_moyen": float(e.mean()),
                                               "demi_intervalle_95": float(demi_intervalle(e)),
                                               "valeur_nette_passive": ctl["controle|A|passive"]["resume"]["valeur_nette"]}
    ecrire()
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
