"""V5 : collecte nouvelle sensible au taux servi relatif (première version volontairement simple).

Spécification : docs/V5_SPECIFICATION_COLLECTE.md ; paramètres : data/v5/collecte/collecte.json ;
mécanique annuelle : src/projection.py (section « collecte » des hypothèses).

Mesures, toujours sur les mêmes scénarios :
- valeur de l'existant : valeur nette en extinction (c0 = 0), dans la frontière des contrats ; c'est aussi
  la base de la vue prudentielle, qui ignore la collecte ;
- valeur des affaires nouvelles (valeur de franchise, hors Solvabilité II) = valeur totale avec
  collecte - valeur de l'existant, répartie scénario par scénario entre les flux des contrats nouveaux
  (VA des primes - BE des contrats nouveaux), la variation du BE de l'existant et l'impôt
  supplémentaire ; seule la somme s'interprète (voir decomposer) ;
- probabilité réelle : collecte, PM, rentabilité, dividendes, apports et liquidité, sans valorisation.
"""

import copy
import json
from pathlib import Path

import numpy as np

from ..stochastique import projeter_stochastique
from . import bases
from .strategies import impots_par_scenario

FICHIER = Path(__file__).resolve().parents[2] / "data" / "v5" / "collecte" / "collecte.json"


def charger():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def section(c0, eta, mode="mutualise", **remplacements):
    """Section « collecte » des hypothèses, à partir des paramètres du fichier."""
    d = charger()
    r = {k: v["valeur"] for k, v in d["reaction"].items()}
    cn = {k: v["valeur"] for k, v in d["contrats_nouveaux"].items() if not k.startswith("_")}
    s = {"c0": float(c0), "eta": float(eta), "mode": mode, "horizon_collecte_ans": d["horizon_collecte_ans"]["valeur"],
         "contrats_nouveaux": cn, **r}
    for cle, valeur in remplacements.items():
        if cle in cn:
            s["contrats_nouveaux"][cle] = valeur
        else:
            s[cle] = valeur
    return s


def appliquer_collecte(h, c0, eta, mode="mutualise", **remplacements):
    h = copy.deepcopy(h)
    h["collecte"] = section(c0, eta, mode, **remplacements)
    return h


def _lecture(tr, col):
    return tr[col].unstack("annee")


def projection_risque_neutre(h, credit, base="sans_va", n=1000):
    """Projection stochastique risque neutre et grandeurs par scénario (valeur nette, BE, impôt)."""
    g, cr = bases.gse(h, base, credit, n=n)
    res = projeter_stochastique(h, g, credit=cr, detail=False)
    tr, ps = res["trajectoires"], res["par_scenario"]
    T = h["horizon_annees"]
    ans = list(range(1, T + 1))
    resultat = _lecture(tr, "resultat_assureur")[ans].to_numpy()
    defl = _lecture(tr, "deflateur")[ans].to_numpy()
    va_impots = (impots_par_scenario(resultat, h["fiscalite"]["unite_monetaire_eur"]) * defl).sum(axis=1)
    apport0 = h["bilan_initial"].get("apport_initial", 0.0)
    va_primes = ps["va_primes"].to_numpy() if "va_primes" in ps else np.zeros(len(ps))
    sortie = {
        "vm0": float(ps["vm_actif_initial"].iloc[0]), "apport_initial": apport0,
        "be": ps["be"].to_numpy(), "va_primes": va_primes, "va_impots": va_impots,
        "valeur_nette": ps["vm_actif_initial"].to_numpy() + va_primes - ps["be"].to_numpy() - apport0 - va_impots,
        "fuite": ps["fuite"].to_numpy(), "trajectoires": tr,
    }
    if "be_nouveaux" in ps:
        sortie.update(be_nouveaux=ps["be_nouveaux"].to_numpy(), be_existant=ps["be_existant"].to_numpy())
    else:
        sortie.update(be_nouveaux=np.zeros(len(ps)), be_existant=ps["be"].to_numpy())
    return sortie


def decomposer(avec, ferme):
    """Décomposition, scénario par scénario, de la valeur des affaires nouvelles.

    avec : projection avec collecte ; ferme : mêmes hypothèses, c0 = 0 (extinction), mêmes scénarios.
    valeur totale - valeur de l'existant = flux des contrats nouveaux + variation du BE de l'existant
    + impôt supplémentaire, avec :
    - flux des contrats nouveaux = VA des primes - BE des contrats nouveaux (ce que reçoivent les
      contrats nouveaux dans le fonds mutualisé) ;
    - variation du BE de l'existant = -(BE de l'existant avec collecte - BE en extinction) ;
    - impôt supplémentaire = -(VA de l'impôt avec collecte - VA de l'impôt en extinction).
    L'identité tient par construction (BE de l'existant = BE total - BE des contrats nouveaux) ; la
    vérification ne contrôle que l'arithmétique. Seule la somme s'interprète comme une valeur : un
    transfert entre générations d'assurés déplace les deux premiers termes en sens inverse.
    """
    flux = avec["va_primes"] - avec["be_nouveaux"]
    existant = -(avec["be_existant"] - ferme["be"])
    impot = -(avec["va_impots"] - ferme["va_impots"])
    van = avec["valeur_nette"] - ferme["valeur_nette"]
    ecart = np.abs(van - (flux + existant + impot)).max()
    if ecart > 1e-6:
        raise AssertionError(f"Décomposition de la valeur des affaires nouvelles non exacte (écart {ecart:.2e})")
    return {"valeur_affaires_nouvelles": van, "flux_contrats_nouveaux": flux, "variation_be_existant": existant,
            "impot_supplementaire": impot}


def indicateurs_risque_neutre(x):
    """Moyennes risque neutre de collecte et de PM (montants non actualisés), sur une projection."""
    tr = x["trajectoires"]
    ans = list(range(1, 11))
    sortie = {"pm_annee_10_moyenne": float(_lecture(tr, "pm")[10].mean()),
              "taux_rachat_moyen_1_10": float(_lecture(tr, "taux_rachat")[ans].to_numpy().mean())}
    if "primes" in tr:
        sortie.update(collecte_1_10_moyenne=float(_lecture(tr, "primes")[ans].to_numpy().sum(axis=1).mean()),
                      facteur_collecte_moyen_1_10=float(_lecture(tr, "facteur_collecte")[ans].to_numpy().mean()),
                      pm_nouveaux_annee_10_moyenne=float(_lecture(tr, "pm_nouveaux")[10].mean()))
    return sortie


def diagnostic_garanties(x):
    """Part des années-scénarios 1 à 10 où les contrats nouveaux sont crédités sous l'existant (le TMG de
    l'existant contraint alors la répartition), et écart moyen sur ces années."""
    tr = x["trajectoires"]
    ans = list(range(2, 11))  # année 1 : aucun contrat nouveau en début d'année
    n, e = _lecture(tr, "taux_servi_nouveaux")[ans].to_numpy(), _lecture(tr, "taux_servi_existant")[ans].to_numpy()
    sous = n < e - 1e-12
    return {"part_annees_nouveaux_sous_existant_2_10": float(sous.mean()),
            "ecart_moyen_si_sous_existant": float((e - n)[sous].mean()) if sous.any() else 0.0}


def indicateurs_reels(h, tr):
    """Collecte, croissance et liquidité en probabilité réelle (montants non actualisés, conditionnels)."""
    ans = list(range(1, 11))
    pm = _lecture(tr, "pm")
    prest, frais = _lecture(tr, "prestations"), _lecture(tr, "frais")
    primes = _lecture(tr, "primes") if "primes" in tr else prest * 0.0
    sorties_nettes = (prest[ans].to_numpy() + frais[ans].to_numpy() - primes[ans].to_numpy()) / pm[[a - 1 for a in ans]].to_numpy()
    sortie_nouveaux = {}
    if "taux_servi_nouveaux" in tr:
        sortie_nouveaux["ecart_taux_servi_nouveaux_reference_1_10"] = float(
            (_lecture(tr, "taux_servi_nouveaux")[ans].to_numpy() - _lecture(tr, "taux_10ans")[ans].to_numpy()).mean())
    return {
        **sortie_nouveaux,
        "collecte_1_10_moyenne": float(primes[ans].to_numpy().sum(axis=1).mean()),
        "collecte_1_10_q05": float(np.quantile(primes[ans].to_numpy().sum(axis=1), 0.05)),
        "pm_annee_10_mediane": float(pm[10].median()),
        "sorties_nettes_max_1_10_q99": float(np.quantile(sorties_nettes.max(axis=1), 0.99)),
    }


# --- Lecture des écarts (critères communs aux rapports) ----------------------------------------------

def etat_majorant(ecart_affaires_nouvelles):
    """L'avantage d'une stratégie en portefeuille fermé majore-t-il son avantage avec collecte ? Oui si
    l'écart de valeur des affaires nouvelles à la gestion passive est significativement négatif, non s'il
    est significativement positif, indéterminé sinon (écart dans son intervalle apparié à 95 %)."""
    m, h = ecart_affaires_nouvelles["moyenne"], ecart_affaires_nouvelles["demi_intervalle_95"]
    return "oui" if m + h < 0 else ("non" if m - h > 0 else "indéterminé")


def robustesse(ecarts, seuil):
    """Lecture d'un ensemble d'écarts appariés {moyenne, demi_intervalle_95} sur une grille d'hypothèses.

    Trois notions distinctes : un écart est significatif si son intervalle apparié à 95 % exclut zéro ;
    important s'il est significatif et si sa moyenne dépasse le seuil ; robuste s'il est, dans toutes les
    configurations, de même signe avec la borne de l'intervalle au-delà du seuil. « Sans effet important »
    exige que l'intervalle entier reste sous le seuil partout (une moyenne faible mais imprécise ne suffit
    pas). « Non robuste » : même signe partout, ou partout où l'écart est significatif, mais borne sous le
    seuil dans au moins une configuration. Un changement de signe n'est retenu que si des écarts
    significatifs des deux signes existent ; sans écart significatif et avec des signes mêlés, la lecture
    est « non concluant »."""
    if all(e["moyenne"] - e["demi_intervalle_95"] >= seuil for e in ecarts):
        return "favorable, robuste"
    if all(e["moyenne"] + e["demi_intervalle_95"] <= -seuil for e in ecarts):
        return "défavorable, robuste"
    if all(abs(e["moyenne"]) + e["demi_intervalle_95"] < seuil for e in ecarts):
        return "sans effet important"
    if all(e["moyenne"] > 0 for e in ecarts):
        return "toujours positif, non robuste"
    if all(e["moyenne"] < 0 for e in ecarts):
        return "toujours négatif, non robuste"
    significatifs = [e for e in ecarts if abs(e["moyenne"]) > e["demi_intervalle_95"]]
    positifs = any(e["moyenne"] > 0 for e in significatifs)
    negatifs = any(e["moyenne"] < 0 for e in significatifs)
    if positifs and negatifs:
        return "change de signe selon les hypothèses"
    if positifs:
        return "positif là où il est significatif, non robuste"
    if negatifs:
        return "négatif là où il est significatif, non robuste"
    return "non concluant (aucun écart significatif, signes mêlés)"
