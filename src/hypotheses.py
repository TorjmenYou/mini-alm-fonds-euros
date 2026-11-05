"""Chargement des hypothèses et construction du bilan initial (étape 1)."""

import json
from pathlib import Path

CHEMIN_PAR_DEFAUT = Path(__file__).resolve().parent.parent / "data" / "hypotheses.json"


def charger_hypotheses(chemin=CHEMIN_PAR_DEFAUT):
    """Lit le fichier JSON des hypothèses et renvoie un dictionnaire."""
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def actif_initial(h):
    """Répartit l'actif initial (en valeur comptable) selon l'allocation cible.

    À l'ouverture, l'actif comptable couvre exactement le passif :
    PM + PPB + fonds propres.
    """
    allocation = h["actif"]["allocation_cible"]
    assert abs(sum(allocation.values()) - 1.0) < 1e-9, "L'allocation doit sommer à 100 %"

    bilan = h["bilan_initial"]
    total = bilan["pm"] + bilan["ppb"] + bilan["fonds_propres"]
    repartition = {classe: total * poids for classe, poids in allocation.items()}
    repartition["total"] = total
    return repartition
