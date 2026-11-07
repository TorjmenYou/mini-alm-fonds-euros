"""V5 : vérifie que les résultats versionnés se reproduisent à partir du code et des données du dépôt.

Usage : python scripts/v5_verifier_reproduction.py [--prudentiel] [--tolerance 1e-9]
Recalcule, sans cache, un échantillon de cellules des résultats principaux avec les fonctions mêmes des
scripts qui les ont produits, et les compare aux valeurs de resultats/*.json. Les calculs sont
déterministes (graines fixes, tirages appariés) : l'écart attendu est nul, à l'arrondi machine près.

Cellules vérifiées (environ 2 minutes sur 2 cœurs ; --prudentiel ajoute environ 4 minutes) :
1. consolidation : valeur nette risque neutre du profil B, gestion passive, capital à 100 % ;
2. collecte : valeur de l'existant, valeur totale et valeur des affaires nouvelles du profil B (gestion
   passive, c0 = 6 %, eta = 0,5) ; écart de valeur totale de la politique de marge du profil A (mêmes
   hypothèses) ; PM médiane à 10 ans et collecte 1-10 en probabilité réelle (profil B) ;
3. réconciliation : flux de place 2025, collecte nette du modèle (profil B, année 1), résidu du contrat
   sans marge explicite (trois profils) et de sa variante de liquidation (profil A), capital de la
   croissance (gestion passive, élasticité modérée) et seuil de coût du capital (profil B) ;
4. avec --prudentiel : SCR simplifié, fonds propres et indicateur de couverture du profil B sans apport
   (2 000 scénarios, base avec VA).
Écart mesuré : |recalculé - versionné| / max(1, |versionné|), donc relatif au-delà de 1 et absolu en dessous.
Code de sortie 1 si un écart dépasse la tolérance.
"""

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import collecte as col  # noqa: E402


def module(nom):
    spec = importlib.util.spec_from_file_location(nom, RACINE / "scripts" / f"{nom}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def lire(nom):
    return json.loads((RACINE / "resultats" / nom).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prudentiel", action="store_true", help="vérifie aussi une cellule de la vue prudentielle (environ 4 minutes)")
    ap.add_argument("--tolerance", type=float, default=1e-9, help="écart toléré, rapporté à max(1, |valeur versionnée|)")
    a = ap.parse_args()
    cons, coll, rec = module("v5_consolidation"), module("v5_collecte"), module("v5_reconciliation_collecte")
    K, R, REC = lire("v5_consolidation.json"), lire("v5_collecte.json"), lire("v5_reconciliation_collecte.json")
    lignes = []

    def comparer(libelle, calcule, versionne):
        ecart = abs(calcule - versionne) / max(1.0, abs(versionne))
        lignes.append((libelle, calcule, versionne, ecart))
        print(f"{'OK ' if ecart <= a.tolerance else 'ÉCART'} {libelle} : recalculé {calcule:.10g}, versionné {versionne:.10g}", flush=True)

    t0 = time.time()
    # 1. Consolidation
    apport_b = K["capital"]["B|passive"]["besoin"]["1.0"]
    q = cons.t_rn("B", "passive", apport_b, K["n_scenarios"])
    comparer("consolidation, B passive, valeur nette à 100 %", q["resume"]["valeur_nette"], K["risque_neutre"]["B|passive|1.0"]["valeur_nette"])

    # 2. Collecte
    n, c0, eta = R["n_scenarios"], R["intensites"]["centrale"], R["elasticites"]["moderee"]
    rn = {}
    for p, c in (("B", "passive"), ("A", "passive"), ("A", "taux_servi_marge")):
        rn[(p, c, 0)] = coll.t_rn(p, c, R["apports"][f"{p}|{c}"], n, 0.0, 0.0)["par_scenario"] if (p, c) == ("B", "passive") else None
        rn[(p, c, c0)] = coll.t_rn(p, c, R["apports"][f"{p}|{c}"], n, c0, eta)["par_scenario"]
    ref = R["risque_neutre"][f"B|passive|{c0}|{eta}"]
    comparer("collecte, B passive, valeur de l'existant", float(np.mean(rn[("B", "passive", 0)]["valeur_nette"])), ref["valeur_existant"]["moyenne"])
    comparer("collecte, B passive, valeur totale", float(np.mean(rn[("B", "passive", c0)]["valeur_nette"])), ref["valeur_totale"]["moyenne"])
    dec = col.decomposer(rn[("B", "passive", c0)], rn[("B", "passive", 0)])
    comparer("collecte, B passive, valeur des affaires nouvelles", float(dec["valeur_affaires_nouvelles"].mean()), ref["valeur_affaires_nouvelles"]["moyenne"])
    e = rn[("A", "taux_servi_marge", c0)]["valeur_nette"] - rn[("A", "passive", c0)]["valeur_nette"]
    comparer("collecte, A marge - passive, écart de valeur totale", float(e.mean()), R["ecarts"][f"A|taux_servi_marge|{c0}|{eta}"]["totale"]["moyenne"])
    r = coll.t_reel("B", "passive", R["apports"]["B|passive"], n, c0, eta)
    comparer("collecte, B passive, PM médiane à 10 ans (réel)", r["pm_annee_10_mediane"], R["reel"][f"B|passive|{c0}|{eta}"]["pm_annee_10_mediane"])
    comparer("collecte, B passive, collecte 1-10 (réel)", r["collecte_1_10_moyenne"], R["reel"][f"B|passive|{c0}|{eta}"]["collecte_1_10_moyenne"])

    # 3. Réconciliation
    pl = rec.place()
    comparer("réconciliation, autres mouvements 2025 (Md€)", pl["autres_mouvements_residu"], REC["place_2025"]["autres_mouvements_residu"])
    flux = rec.flux_modele("B", R["apports"]["B|passive"], REC["n_scenarios_reels"])
    comparer("réconciliation, B, collecte nette du modèle, année 1", flux["collecte_nette"]["annee_1"], REC["modele"]["B"]["collecte_nette"]["annee_1"])
    for p in "ABC":
        comparer(f"réconciliation, contrat sans marge explicite {p}, résidu", rec.contrat_equitable(p)["residu"], REC["contrat_equitable"][p]["residu"])
    comparer("réconciliation, variante de liquidation A, résidu", rec.contrat_equitable("A", rc_initiale_nulle=True, sans_retention=True)["residu"],
             REC["variantes_liquidation"]["A"]["rc_initiale_nulle_sans_retention"]["residu"])
    cc = rec.capital_croissance(R, K)
    for p in "ABC":
        comparer(f"capital de la croissance, {p} passive, eta modérée", cc[f"{p}|passive"]["collecte_centrale"]["moderee"]["scr_supplementaire_proportionnel"],
                 REC["capital_croissance"][f"{p}|passive"]["collecte_centrale"]["moderee"]["scr_supplementaire_proportionnel"])
    comparer("seuil de coût du capital, B, kappa*", rec.seuil_cout_capital(R, K, "B", R["n_scenarios"])["kappa_seuil"], REC["seuil_cout_capital"]["B"]["kappa_seuil"])

    # 4. Vue prudentielle (facultatif)
    if a.prudentiel:
        x = cons.t_prudentiel("B", "passive", 0.0, K["n_scenarios_prudentiel"])["resume"]
        v = K["prudentiel"]["B|passive"]["apport_0"]
        for cle in ("scr", "fonds_propres_niveau_1", "indicateur_couverture_scr"):
            comparer(f"prudentiel, B passive sans apport, {cle}", x[cle], v[cle])

    mauvais = [l for l in lignes if l[3] > a.tolerance]
    print(f"\n{len(lignes) - len(mauvais)} valeurs reproduites sur {len(lignes)} (tolérance {a.tolerance:g}), {time.time() - t0:.0f} s.")
    sys.exit(1 if mauvais else 0)


if __name__ == "__main__":
    main()
