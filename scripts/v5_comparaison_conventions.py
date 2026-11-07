"""V5 : comparaison croisée des conventions de crédit et de comportement, sur les trois profils fictifs.

Usage : python scripts/v5_comparaison_conventions.py [--n 1000] [--processus 2]
Écrit resultats/v5_comparaison_conventions.json (docs/V5_CONVENTIONS.md est généré à partir de ce fichier
par scripts/v5_rapport_conventions.py).

Trois blocs de calculs :
1. valorisation risque neutre, stochastique (1 000 scénarios, base sans VA sauf mention) : BE, TVOG,
   valeur actionnaire, rachats, liquidité, apports de capital, pour chaque profil x référence x crédit ;
2. équivalent certain et durations effectives, par profil x référence ;
3. trajectoires centrales en probabilité réelle (aucune valeur calculée), par profil x référence x
   perte attendue réelle.
Toutes les valeurs sont en unités fictives (1 unité = 10 M EUR), avant impôt.
"""

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.projection import indicateurs, projeter  # noqa: E402
from src.stochastique import projeter_stochastique  # noqa: E402
from src.v5 import bases, conventions as cv  # noqa: E402
from src.v5.profils import courbe_decalee, hypotheses_profil  # noqa: E402
from src.v5.scenarios import ScenarioCourbe  # noqa: E402

REFERENCES = ("oat_moins_2", "sans_risque", "sans_risque_demi", "taux_servi_marche", "livret_a", "figee")
CREDITS = ("lisse_integral", "saut_integral", "decompose")
REELLES = ("central", "haute", "stress_50", "stress_100")


def variantes():
    """(profil, référence, crédit, options) des projections stochastiques."""
    v = [(p, r, k, {}) for p in "ABC" for r in REFERENCES for k in CREDITS]
    for p in "ABC":
        v += [(p, "sans_risque", k, {}) for k in ("decompose_recouvrement_63", "saut_bloc_unique")]
        v += [(p, "sans_risque", k, {"niveau": 0.0263}) for k in ("lisse_integral", "decompose")]
        v += [(p, "sans_risque", k, {"rachat_structurel": 0.044}) for k in ("lisse_integral", "decompose")]
        v += [(p, "sans_risque", "decompose", {"base": "avec_va"})]
    return v


def cle(p, r, k, o):
    suffixe = "".join(f"|{a}={b}" for a, b in sorted(o.items()))
    return f"{p}|{r}|{k}{suffixe}"


def hyp(p, r, o):
    return cv.appliquer(hypotheses_profil(p), r, o.get("base", "sans_va"), o.get("niveau"), o.get("rachat_structurel"))


def equivalent_certain(h, base="sans_va", decalage=0.0):
    c = bases.courbe_base(base)
    if decalage:
        c = courbe_decalee(c, decalage)
    eco = ScenarioCourbe("ec", h["horizon_annees"], c, courbe_avant_choc=bases.courbe_base(base))
    df = projeter(h, eco, credit=bases.credit_sur_base(cv.credit_valorisation("lisse_integral"), base))
    return df, indicateurs(df)


def resume_ec(p, r, o):
    h = hyp(p, r, o)
    base = o.get("base", "sans_va")
    df, ind = equivalent_certain(h, base)
    bas, haut = equivalent_certain(h, base, -0.0005)[1], equivalent_certain(h, base, 0.0005)[1]
    return {
        "be": ind["be"], "valeur": ind["valeur_assureur"], "fuite": ind["fuite"],
        "taux_servi_moyen_1_10": float(df.loc[1:10, "taux_servi"].mean()),
        "taux_rachat_moyen_1_10": float(df.loc[1:10, "taux_rachat"].mean()),
        "taux_rachat_moyen_1_20": float(df.loc[1:20, "taux_rachat"].mean()),
        "reference_annee_1": float(df.loc[1, "taux_10ans"]), "reference_annee_10": float(df.loc[10, "taux_10ans"]),
        "pm_annee_10": float(df.loc[10, "pm"]), "apports_cumules": float(df["apport_assureur"].sum()),
        "duration_effective_be": -(haut["be"] - bas["be"]) / (0.001 * ind["be"]),
        "duration_effective_actif": -(haut["vm_actif_initial"] - bas["vm_actif_initial"]) / (0.001 * ind["vm_actif_initial"]),
        "valeur_par_pb": (haut["valeur_assureur"] - bas["valeur_assureur"]) / 10,
    }


def resume_stochastique(p, r, k, o, n):
    t0 = time.time()
    h = hyp(p, r, o)
    base = o.get("base", "sans_va")
    g, credit = bases.gse(h, base, cv.credit_valorisation(k, "sans_va", h["horizon_annees"]), n=n)  # gse() réexprime sur la base
    res = projeter_stochastique(h, g, credit=credit, detail=True)
    s, ps, tr = res["synthese"], res["par_scenario"], res["trajectoires"]
    lecture = lambda col: tr[col].unstack("annee")  # noqa: E731  (scénarios x années)
    rachat, servi, pm, prest = lecture("taux_rachat"), lecture("taux_servi"), lecture("pm"), lecture("prestations")
    apports, pmv = lecture("apport_assureur"), lecture("pmv_obligataires_realisees")
    pertes_credit = lecture("pertes_credit")
    ans = list(range(1, 11))
    sorties = prest[ans].to_numpy() / pm[[a - 1 for a in ans]].to_numpy()
    mv_realisees = -np.minimum(pmv[ans].to_numpy(), 0.0).sum(axis=1)
    va = ps["va_apports"].to_numpy()
    avec = apports.to_numpy()[:, 1:] > 1e-9
    premiere = np.where(avec.any(axis=1), avec.argmax(axis=1) + 1, 0)
    rc0 = h["bilan_initial"]["reserve_capitalisation"]
    out = {
        "be": s["be"], "ic_be": s["ic_be"], "valeur": s["valeur_assureur"], "fdb": s["fdb"],
        "fuite": s["fuite"], "ic_fuite": s["ic_fuite"],
        "taux_rachat_annee_1": float(rachat[1].mean()), "taux_rachat_moyen_1_10": float(rachat[ans].to_numpy().mean()),
        "taux_rachat_max_1_10_q95": float(np.quantile(rachat[ans].to_numpy().max(axis=1), 0.95)),
        "taux_servi_moyen_1_10": float(servi[ans].to_numpy().mean()),
        "pm_annee_10_moyenne": float(pm[10].mean()),
        "sorties_max_1_10_q95": float(np.quantile(sorties.max(axis=1), 0.95)),
        "moins_values_realisees_1_10_moyenne": float(mv_realisees.mean()),
        "moins_values_realisees_1_10_q95": float(np.quantile(mv_realisees, 0.95)),
        "part_scenarios_mv_realisees_au_dela_rc": float((mv_realisees > rc0).mean()),
        "pertes_credit_1_10_moyenne": float(pertes_credit[ans].to_numpy().sum(axis=1).mean()),
        "pertes_credit_1_10_q99": float(np.quantile(pertes_credit[ans].to_numpy().sum(axis=1), 0.99)),
        "va_apports_moyenne": float(va.mean()), "part_scenarios_avec_apport": s["part_scenarios_avec_apport"],
        "va_apports_quantiles": {q: float(np.quantile(va, float(q))) for q in ("0.5", "0.75", "0.9", "0.95", "0.99")},
        "va_apports_moyenne_si_apport": float(va[va > 1e-9].mean()) if (va > 1e-9).any() else 0.0,
        "premiere_annee_apport_mediane": float(np.median(premiere[premiere > 0])) if (premiere > 0).any() else None,
        "part_apport_avant_10_ans": float(((premiere > 0) & (premiere <= 10)).mean()),
        "duree_s": round(time.time() - t0, 1),
    }
    if hasattr(credit, "probabilite_defaut"):
        survie = np.cumprod([1 - credit.probabilite_defaut(t) for t in range(1, 31)])
        out["probabilite_defaut_bloc_10_ans_rn"] = float(1 - survie[9])
        out["probabilite_defaut_bloc_30_ans_rn"] = float(1 - survie[29])
        out["probabilite_defaut_bloc_annee_10_rn"] = credit.probabilite_defaut(10)
    return out


def resume_reel(p, r, code):
    h = cv.hypotheses_reelles(cv.appliquer(hypotheses_profil(p), r), code)
    df = projeter(h, cv.scenario_reel(h))
    ans = slice(1, 10)
    return {
        "perte_attendue_reelle": h["actif"]["credit"]["perte_attendue_reelle"],
        "taux_servi_moyen_1_10": float(df.loc[ans, "taux_servi"].mean()),
        "taux_servi_annee_1": float(df.loc[1, "taux_servi"]),
        "taux_rachat_annee_1": float(df.loc[1, "taux_rachat"]), "taux_rachat_moyen_1_10": float(df.loc[ans, "taux_rachat"].mean()),
        "rendement_comptable_moyen_1_10": float(df.loc[ans, "rendement_comptable"].mean()),
        "pm_annee_10": float(df.loc[10, "pm"]), "apports_cumules_1_10": float(df.loc[ans, "apport_assureur"].sum()),
        "apports_cumules": float(df["apport_assureur"].sum()),
        "fonds_propres_min_1_10": float(df.loc[ans, "fonds_propres"].min()),
        "fonds_propres_annee_10": float(df.loc[10, "fonds_propres"]),
        "pertes_credit_1_10": float(df.loc[ans, "pertes_credit"].sum()),
        "resultat_moyen_1_10": float(df.loc[ans, "resultat_assureur"].mean()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--processus", type=int, default=2)
    a = ap.parse_args()
    sortie = {"unites": "unités fictives, 1 unité = 10 M EUR ; avant impôt", "n_scenarios": a.n,
              "stochastique": {}, "equivalent_certain": {}, "reel": {}}

    # Équivalent certain et trajectoires réelles : rapides
    opts_ec = [{}, {"niveau": 0.0263}, {"rachat_structurel": 0.044}, {"base": "avec_va"}]
    for p in "ABC":
        for r in REFERENCES:
            sortie["equivalent_certain"][cle(p, r, "ec", {})] = resume_ec(p, r, {})
            for code in REELLES:
                sortie["reel"][f"{p}|{r}|{code}"] = resume_reel(p, r, code)
        for o in opts_ec[1:]:
            sortie["equivalent_certain"][cle(p, "sans_risque", "ec", o)] = resume_ec(p, "sans_risque", o)
    print("équivalents certains et trajectoires réelles : faits", flush=True)

    chemin = RACINE / "resultats" / "v5_comparaison_conventions.json"
    with ProcessPoolExecutor(max_workers=a.processus) as ex:
        taches = {ex.submit(resume_stochastique, p, r, k, o, a.n): cle(p, r, k, o) for p, r, k, o in variantes()}
        for i, f in enumerate(as_completed(taches), 1):
            sortie["stochastique"][taches[f]] = f.result()
            print(f"{i}/{len(taches)} {taches[f]} ({f.result()['duree_s']} s)", flush=True)
            if i % 10 == 0:
                chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    sortie["stochastique"] = dict(sorted(sortie["stochastique"].items()))
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)


if __name__ == "__main__":
    main()
