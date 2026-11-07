"""Conventions comparées en V5 : référence des assurés, forme des pertes de crédit, probabilité réelle.

Les paramètres et leurs statuts sont dans data/v5/conventions/conventions.json ; la comparaison et
ses conclusions dans docs/V5_CONVENTIONS.md. Trois familles, jamais mélangées :

- valorisation (risque neutre) : tout le spread est un coût risque neutre ; la convention fixe sa
  forme (lissée ou par saut, recouvrement, concentration) ; les prix de marché sont inchangés ;
- projection en probabilité réelle : seule la perte attendue réelle est constatée, le reste du
  spread est une prime ; aucune valeur n'est calculée sur ces trajectoires ;
- comportement des assurés : référence de taux à laquelle ils comparent le taux servi.
"""

import copy
import json
from pathlib import Path

from ..courbes import CourbeAvecSpread
from . import bases
from .courbes_marche import courbe_eiopa, spread_oat
from .credit import CreditSaut
from .scenarios import ScenarioReel

FICHIER = Path(__file__).resolve().parents[2] / "data" / "v5" / "conventions" / "conventions.json"


def charger():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def poids_blocs(nom, donnees=None):
    b = (donnees or charger())["blocs"][nom]
    if isinstance(b, list):
        return tuple(b)
    n = b["diversifie"]["nombre_de_blocs"]
    souverain = (b["souverain"],) if b["souverain"] > 0 else ()
    return souverain + (b["diversifie"]["part"] / n,) * n


# --- Crédit : valorisation -----------------------------------------------------------------------

def credit_valorisation(code, base="sans_va", horizon=60):
    """Spread OAT de marché avec la forme de perte de la convention, réexprimé sur la base."""
    d = charger()
    k = d["conventions_credit"][code]
    marche = spread_oat(methode=k.get("spread", "tec"))
    if k["part_saut"] == 0.0:
        return bases.credit_sur_base(marche, base)  # convention initiale : SpreadCredit, perte lissée
    c = CreditSaut.depuis(marche, part_saut=k["part_saut"], recouvrement=k["recouvrement"],
                          blocs=poids_blocs(k["blocs"], d), horizon=horizon, correlation=k.get("correlation"))
    return bases.credit_sur_base(c, base)


def credit_reel(code_valorisation, code_reel, horizon=60):
    """Défauts en probabilité réelle sur la structure de blocs d'une convention de valorisation
    (mêmes blocs, même corrélation), pour les projections stochastiques de plausibilité."""
    d = charger()
    k = d["conventions_credit"][code_valorisation]
    r = d["conventions_reelles_stochastiques"][code_reel]
    return CreditSaut.depuis(spread_oat(methode=k.get("spread", "tec")), part_saut=max(k["part_saut"], 1e-12), recouvrement=k["recouvrement"],
                             blocs=poids_blocs(k["blocs"], d), horizon=horizon, correlation=k.get("correlation"),
                             pd_reelle=r.get("pd_reelle"), facteur_pd_reelle=r.get("facteur_pd_reelle"),
                             recouvrement_reel=r["recouvrement_reel"])


def hypotheses_reelles_stochastiques(h):
    """Mesure « trajectoire » à spreads figés ; les pertes viennent du modèle de crédit réel passé à projeter()."""
    h = copy.deepcopy(h)
    h["actif"]["credit"] = dict(h["actif"]["credit"], mesure="trajectoire", perte_attendue_reelle=0.0, spreads_figes=True)
    return h


def prime_actions_reelle():
    return charger()["conventions_reelles"]["prime_actions"]["valeur"]


# --- Crédit : probabilité réelle ------------------------------------------------------------------

def perte_reelle(code):
    r = charger()["conventions_reelles"][code]
    if "perte_attendue_reelle" in r:
        return r["perte_attendue_reelle"]
    return r["part_spread_10_ans"] * spread_oat().s(10)


def hypotheses_reelles(h, code):
    """Hypothèses d'une projection en probabilité réelle : pertes attendues réelles, spreads figés."""
    h = copy.deepcopy(h)
    h["actif"]["credit"] = dict(h["actif"]["credit"], mesure="trajectoire", perte_attendue_reelle=perte_reelle(code),
                                spreads_figes=True)
    return h


def scenario_reel(h):
    prime = charger()["conventions_reelles"]["prime_actions"]["valeur"]
    return ScenarioReel("reel_central", h["horizon_annees"], courbe_eiopa(), prime_actions=prime)


# --- Référence des assurés ------------------------------------------------------------------------

def niveau_initial_central():
    return charger()["references_assures"]["_niveau_initial"]["valeur"]


def comportement(code, base="sans_va", niveau=None):
    """Section « comportement » des hypothèses pour une référence, calée sur la courbe de la base.

    Le moteur initial X0 est lu sur la courbe de marché de la base, avant tout choc."""
    r = charger()["references_assures"][code]
    if "comportement" in r:  # ancienne référence, statique
        return dict(r["comportement"])
    c0 = bases.courbe_base(base)
    moteur = r["moteur"]
    if moteur in ("zc10_sans_risque", "lisse"):
        x0 = c0.taux_zc(10)
    elif moteur == "livret_a":
        x0 = c0.taux_1an()
    else:
        x0 = 0.0
    if moteur == "composite":
        comps = []
        for k in r["composantes"]:
            k = {a: b for a, b in k.items() if a != "statut"}
            k["valeur_initiale_moteur"] = c0.taux_zc(10) if k["moteur"] == "zc10_sans_risque" else c0.taux_1an()
            comps.append(k)
        n0 = sum(k["poids"] * max(k.get("plancher", -1.0), k["niveau_initial"]) for k in comps)
        return {"reference": "dynamique", "moteur": "composite", "niveau_initial": n0, "composantes": comps}
    out = {"reference": "dynamique", "moteur": moteur, "niveau_initial": niveau if niveau is not None else niveau_initial_central(),
           "beta": r.get("beta", 1.0), "valeur_initiale_moteur": x0}
    for cle in ("lissage", "livret_a_initial", "part_court", "plancher"):
        if cle in r:
            out[cle] = r[cle]
    return out


def appliquer(h, reference, base="sans_va", niveau=None, rachat_structurel=None, loi_rachat=None):
    """Référence des assurés, rachat structurel (valeur ou « acpr ») et loi de rachat dynamique
    (« onc_min », « onc_max » ou dictionnaire de paramètres)."""
    h = copy.deepcopy(h)
    h["comportement"] = comportement(reference, base, niveau)
    if rachat_structurel == "acpr":
        rachat_structurel = rachat_structurel_acpr()
    if rachat_structurel is not None:
        h["passif"]["taux_rachat_structurel"] = rachat_structurel
    if loi_rachat is not None:
        params = charger()["observations"]["corridors_onc_2013"][loi_rachat.split("_")[1]] if isinstance(loi_rachat, str) else loi_rachat
        h["rachats_dynamiques"] = dict(h["rachats_dynamiques"], **params)
    return h


def rachat_structurel_acpr():
    """Paramètre du modèle qui reproduit 4,4 % de rachats au sens de l'ACPR (rachats / provisions d'ouverture)."""
    return charger()["rachats"]["taux_rachat_structurel_central"]["parametre_modele"]


def taux_oat_10_ans_initial():
    """Contrôle : niveau en t = 0 de l'ancienne référence (OAT 10 ans - 2 points)."""
    return CourbeAvecSpread(courbe_eiopa(), spread_oat()).taux_zc(10) - 0.02
