"""Moteur de calcul « à la Prophet » (V4).

Dans Prophet, un modèle est une liste de variables. Chacune a une formule
écrite pour une année t quelconque, qui peut appeler d'autres variables en t,
en t-1 (projection vers l'avant) ou en t+1 (actualisation vers l'arrière).
L'ordre de calcul n'est jamais écrit à la main : le moteur le déduit des
appels entre variables.

Ce moteur reproduit ce principe :
- une variable = un nom, une description, une formule f(m, t) ;
- m("NOM", t) renvoie la valeur de la variable en t pour tous les model
  points à la fois (un vecteur), calculée une seule fois puis mise en cache ;
- les dépendances sont enregistrées au fil des appels (« arbre des variables ») ;
- une dépendance circulaire (A en t appelle B en t qui appelle A en t) est
  détectée et signalée, comme le ferait Prophet à la compilation.
"""

from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Variable:
    nom: str
    description: str
    formule: callable


class Bibliotheque:
    """Ensemble de définitions de variables (l'équivalent d'une bibliothèque Prophet)."""

    def __init__(self):
        self.variables = {}

    def variable(self, nom, description):
        def enregistrer(formule):
            if nom in self.variables:
                raise ValueError(f"Variable définie deux fois : {nom}")
            self.variables[nom] = Variable(nom, description, formule)
            return formule
        return enregistrer


class DependanceCirculaire(Exception):
    pass


class Modele:
    """Un modèle prêt à tourner : bibliothèque + model points + tables + paramètres."""

    def __init__(self, bibliotheque, model_points, tables, parametres, scenario):
        self.bib = bibliotheque
        self.mp = model_points.reset_index(drop=True)
        self.tables = tables
        self.param = parametres
        self.scenario = scenario
        self.T = parametres["horizon_annees"]
        self.n = len(self.mp)
        self._cache = {}
        self._pile = []  # appels en cours : (variable, t)
        self.dependances = defaultdict(set)

    def __call__(self, nom, t):
        if nom not in self.bib.variables:
            raise KeyError(f"Variable inconnue : {nom}")
        if self._pile:
            self.dependances[self._pile[-1][0]].add(nom)
        cle = (nom, t)
        if cle in self._cache:
            return self._cache[cle]
        if cle in self._pile:
            chaine = " -> ".join(f"{v}({u})" for v, u in self._pile[self._pile.index(cle):] + [cle])
            raise DependanceCirculaire(chaine)
        self._pile.append(cle)
        try:
            valeur = self.bib.variables[nom].formule(self, t)
        finally:
            self._pile.pop()
        valeur = np.broadcast_to(np.asarray(valeur, dtype=float), (self.n,)).copy()
        self._cache[cle] = valeur
        return valeur

    def colonne(self, nom):
        """Champ d'une ligne de model points, sous forme de vecteur."""
        return self.mp[nom].to_numpy()

    def calculer(self, noms=None):
        """Calcule les variables demandées (toutes par défaut) de t = 0 à T.

        Renvoie un tableau long : une ligne par (model point, année), une
        colonne par variable, comme un fichier de résultats Prophet.
        """
        noms = noms or list(self.bib.variables)
        resultats = {nom: np.array([self(nom, t) for t in range(self.T + 1)]) for nom in noms}
        index = pd.MultiIndex.from_product([self.mp["id"], range(self.T + 1)], names=["model_point", "annee"])
        return pd.DataFrame({nom: v.T.ravel() for nom, v in resultats.items()}, index=index)

    def arbre_des_variables(self):
        """Pour chaque variable : sa description et les variables qu'elle appelle."""
        return pd.DataFrame([
            {"variable": nom, "description": v.description,
             "appelle": ", ".join(sorted(self.dependances.get(nom, [])))}
            for nom, v in self.bib.variables.items()
        ]).set_index("variable")
