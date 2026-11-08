"""Profils d'assureur fictifs de la V5 (data/v5/profils/profils.json) et indicateurs de bilan initial.

Construction d'un profil :
- passif : PM, PPB, réserve de capitalisation, fonds propres comptables, taux garanti, taux servi ;
- portefeuille obligataire : des poches par génération d'achat ; chaque poche a un coupon (ancrage de
  sa génération) et des maturités résiduelles réparties uniformément sur un intervalle d'années ;
  le nominal de la poche est sa part du portefeuille obligataire comptable ; titres achetés au pair ;
- actions et monétaire : poids cibles ; le monétaire complète l'actif comptable ;
- obligations valorisées sur la courbe EIOPA sans VA + spread hypothétique (moyenne de long terme publiée par l'EIOPA), en risque neutre.
"""

import copy
import json
from pathlib import Path

from ..courbes import CourbeZeroCoupon
from ..hypotheses import charger_hypotheses
from .courbes_marche import spread_obligations

FICHIER = Path(__file__).resolve().parents[2] / "data" / "v5" / "profils" / "profils.json"


def charger_profils():
    return json.loads(FICHIER.read_text(encoding="utf-8"))


def lignes_obligataires(profil, ancrages, total_comptable, decalage_coupons=None):
    """Lignes (nominal, coupon, maturité) des poches d'un profil. decalage_coupons : {millésime: écart}."""
    vnc_obligations = profil["actif"]["allocation_cible"]["obligations"] * total_comptable
    parts = sum(p["part"] for p in profil["poches_obligataires"])
    if abs(parts - 1.0) > 1e-9:
        raise ValueError(f"Les parts des poches obligataires doivent sommer à 1 (somme : {parts})")
    lignes = []
    for p in profil["poches_obligataires"]:
        m0, m1 = p["maturite_residuelle"]
        maturites = list(range(m0, m1 + 1))
        coupon = (ancrages[p["millesime"]]["coupon"] + ancrages.get("_prime_achat", {}).get("valeur", 0.0)
                  + (decalage_coupons or {}).get(p["millesime"], 0.0))
        for m in maturites:
            lignes.append({"nominal": p["part"] * vnc_obligations / len(maturites), "coupon": coupon, "maturite": m,
                           "millesime": p["millesime"]})
    return lignes


def hypotheses_profil(nom, modifications=None, decalage_coupons=None):
    """Hypothèses complètes du profil : celles des V1 à V4, puis les paramètres communs, puis le profil."""
    donnees = charger_profils()
    profil = copy.deepcopy(donnees["profils"][nom])
    for cle, valeur in (modifications or {}).items():  # ex. {"bilan_initial.ppb": 20.0}
        cible = profil
        *chemin, feuille = cle.split(".")
        for c in chemin:
            cible = cible.setdefault(c, {})
        cible[feuille] = valeur
    h = charger_hypotheses()
    commun = donnees["commun"]
    h["bilan_initial"] = {k: profil["bilan_initial"][k] for k in ("pm", "ppb", "reserve_capitalisation", "fonds_propres")}
    h["passif"].update(chargements_encours=commun["passif"]["chargements_encours"], **profil["passif"])
    h["actif"].update(allocation_cible=profil["actif"]["allocation_cible"],
                      pvl_initiale_actions=profil["actif"]["pvl_initiale_actions"],
                      maturite_reinvestissement_ans=profil["actif"]["maturite_reinvestissement_ans"])
    total = sum(h["bilan_initial"].values())
    h["actif"]["lignes_obligataires"] = lignes_obligataires(profil, donnees["ancrages_coupons"], total, decalage_coupons)
    h["actif"]["credit"] = {"spread": dict(spread_obligations().points), "mesure": commun["credit"]["mesure"]}  # base sans VA
    h["comportement"] = {k: v for k, v in (profil.get("comportement") or commun["comportement"]).items() if k != "statut"}
    h["fiscalite"] = {"unite_monetaire_eur": donnees["unite_monetaire_eur"]}
    # V5.1 : composante technique du compte de participation (src/strategie.py, participation_technique)
    pt = commun.get("participation_technique")
    if pt:
        h["strategie"]["participation_technique"] = {"part_assureur": pt["part_assureur"]}
    h["profil"] = {"nom": nom, "libelle": profil["nom"]}
    return h


def credit_profil():
    return spread_obligations()


def courbe_decalee(courbe, decalage):
    """Déplacement parallèle des taux zéro-coupon (pour les durations effectives)."""
    return CourbeZeroCoupon([r + decalage for r in courbe.taux])


def duration_macaulay_obligations(port, courbe):
    """Duration de Macaulay du portefeuille obligataire, sur la courbe de valorisation des obligations."""
    c = port.courbe_obligations(courbe)
    num = den = 0.0
    for l in port.obligations:
        for k in range(1, l.maturite + 1):
            flux = l.coupon * l.nominal + (l.nominal if k == l.maturite else 0.0)
            num += k * flux * c.zc(k)
            den += flux * c.zc(k)
    return num / den
