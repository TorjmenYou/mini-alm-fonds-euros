"""Bibliothèque de variables du passif épargne euro (V4).

Chaque variable est écrite pour une année t quelconque, sur tous les model
points à la fois. Convention : une variable de flux en t porte sur l'année t,
de la date t-1 à la date t ; une variable de stock en t est sa valeur à la date t.
"""

import numpy as np

from ..passif import taux_rachat_conjoncturel
from .moteur import Bibliotheque, Modele
from .tables import charger

epargne = Bibliotheque()
v = epargne.variable

# Paramètres de la loi de rachats conjoncturels (ACPR 2013), comme en V1 à V3
LOI_CONJONCTURELLE = {"alpha": -0.04, "beta": -0.01, "gamma": 0.01, "delta": 0.03,
                      "rc_max": 0.30, "rc_min": -0.05}


# --- Caractéristiques des contrats ------------------------------------------

@v("AGE", "Âge atteint à la date t")
def _(m, t):
    return m.colonne("age") + t


@v("ANCIENNETE", "Ancienneté atteinte à la date t")
def _(m, t):
    return m.colonne("anciennete") + t


@v("TMG", "Taux minimum garanti du contrat")
def _(m, t):
    return m.colonne("tmg")


# --- Hypothèses lues dans les tables -----------------------------------------

@v("QX", "Probabilité de décès dans l'année t, à l'âge de début d'année")
def _(m, t):
    # Table de mortalité : qx = probabilité qu'une personne d'âge x décède avant
    # x + 1, indépendamment des rachats. Au-delà du dernier âge de la table, on
    # lit la dernière ligne (qx = 1 à 120 ans).
    if t == 0:
        return 0.0
    return m.tables["mortalite"].lire(m("AGE", t - 1), "qx")


@v("TX_RACHAT_STRUCT", "Taux de rachat structurel, selon l'ancienneté atteinte et le produit")
def _(m, t):
    if t == 0:
        return 0.0
    return m.tables["rachats"].lire(m("ANCIENNETE", t), m.colonne("produit"))


# --- Scénario économique reçu de l'actif-passif ------------------------------

@v("TAUX_FONDS", "Taux servi par le fonds l'année t (scénario)")
def _(m, t):
    return m.scenario.at[t, "taux_servi"]


@v("TAUX_ATTENDU", "Taux attendu par les assurés l'année t (scénario)")
def _(m, t):
    return m.scenario.at[t, "taux_attendu"]


@v("TAUX_ACTU", "Taux d'actualisation de l'année t (scénario)")
def _(m, t):
    return m.scenario.at[t, "taux_actualisation"]


# --- Revalorisation et comportements ------------------------------------------

@v("TAUX_SERVI", "Taux crédité au contrat : taux du fonds, au moins le TMG")
def _(m, t):
    return np.maximum(m("TAUX_FONDS", t), m("TMG", t))


@v("TX_RACHAT_CONJ", "Rachat conjoncturel : écart entre le taux servi en t-1 et le taux attendu en t")
def _(m, t):
    if t == 0:
        return 0.0
    ecart = m("TAUX_SERVI", t - 1) - m("TAUX_ATTENDU", t)
    return np.array([taux_rachat_conjoncturel(e, LOI_CONJONCTURELLE) for e in ecart])


@v("TX_RACHAT", "Taux de rachat total, borné entre 0 et 100 %")
def _(m, t):
    return np.clip(m("TX_RACHAT_STRUCT", t) + m("TX_RACHAT_CONJ", t), 0.0, 1.0)


# --- Projection de la provision mathématique ---------------------------------

@v("PM_DEBUT", "PM en début d'année t")
def _(m, t):
    return m("PM_FIN", t - 1) if t > 0 else 0.0


@v("INTERETS", "Intérêts crédités dans l'année")
def _(m, t):
    return m("PM_DEBUT", t) * m("TAUX_SERVI", t)


@v("PM_REVAL", "PM revalorisée, avant sorties")
def _(m, t):
    return m("PM_DEBUT", t) + m("INTERETS", t)


@v("DECES", "Capitaux décès payés en fin d'année")
def _(m, t):
    return m("PM_REVAL", t) * m("QX", t)


@v("RACHATS", "Rachats payés en fin d'année, sur la PM des survivants")
def _(m, t):
    # Risques concurrents : le taux de rachat s'applique aux assurés en vie
    return (m("PM_REVAL", t) - m("DECES", t)) * m("TX_RACHAT", t)


@v("PRESTATIONS", "Décès + rachats")
def _(m, t):
    return m("DECES", t) + m("RACHATS", t)


@v("PM_FIN", "PM en fin d'année t")
def _(m, t):
    if t == 0:
        return m.colonne("pm")
    return m("PM_REVAL", t) - m("PRESTATIONS", t)


@v("NB_DECES", "Nombre de contrats sortis par décès dans l'année")
def _(m, t):
    if t == 0:
        return 0.0
    return m("NB_CONTRATS", t - 1) * m("QX", t)


@v("NB_RACHATS", "Nombre de contrats rachetés dans l'année, parmi les survivants")
def _(m, t):
    if t == 0:
        return 0.0
    return (m("NB_CONTRATS", t - 1) - m("NB_DECES", t)) * m("TX_RACHAT", t)


@v("NB_CONTRATS", "Nombre de contrats en vigueur à la date t")
def _(m, t):
    if t == 0:
        return m.colonne("nb_contrats")
    return m("NB_CONTRATS", t - 1) - m("NB_DECES", t) - m("NB_RACHATS", t)


# --- Chargements, frais et coût des garanties --------------------------------

@v("CHARGEMENTS", "Chargements sur encours prélevés par l'assureur")
def _(m, t):
    return m.param["chargements_encours"] * m("PM_DEBUT", t)


@v("FRAIS", "Frais de gestion : en % de l'encours, plus un coût par contrat indexé sur l'inflation")
def _(m, t):
    if t == 0:
        return 0.0
    p = m.param
    par_contrat = p["frais_par_contrat_euros"] / p["unite_montants_euros"] * (1 + p["inflation_frais"]) ** (t - 1)
    return p["frais_encours"] * m("PM_DEBUT", t) + par_contrat * m("NB_CONTRATS", t - 1)


@v("COUT_TMG", "Intérêts crédités au-delà du taux du fonds, pour respecter le TMG")
def _(m, t):
    return np.maximum(m("TMG", t) - m("TAUX_FONDS", t), 0.0) * m("PM_DEBUT", t)


# --- Valeurs actuelles (récurrence vers l'arrière) ----------------------------

@v("VA_SORTIES", "Valeur à la date t des prestations et frais futurs, plus la PM rendue à l'horizon")
def _(m, t):
    if t == m.T:
        return m("PM_FIN", t)
    flux = m("PRESTATIONS", t + 1) + m("FRAIS", t + 1) + m("VA_SORTIES", t + 1)
    return flux / (1 + m("TAUX_ACTU", t + 1))


@v("VA_COUT_TMG", "Valeur à la date t du coût futur des TMG")
def _(m, t):
    if t == m.T:
        return 0.0
    return (m("COUT_TMG", t + 1) + m("VA_COUT_TMG", t + 1)) / (1 + m("TAUX_ACTU", t + 1))


def construire(scenario, dossier=None):
    """Assemble un modèle prêt à tourner à partir d'un dossier de tables et d'un scénario."""
    model_points, tables, parametres = charger(dossier) if dossier else charger()
    return Modele(epargne, model_points, tables, parametres, scenario)
