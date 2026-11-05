"""Tables d'hypothèses et chargement d'un jeu de données (V4).

Comme dans Prophet, les hypothèses vivent dans des fichiers séparés des
formules : changer une table ne demande pas de toucher au code.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

DOSSIER = Path(__file__).resolve().parents[2] / "data" / "v4"


class Table:
    """Table indexée par une clé entière (âge, ancienneté...), une colonne par produit.

    Au-delà de la dernière clé, on lit la dernière ligne (la table est prolongée
    par sa dernière valeur) ; en deçà de la première, la première ligne.
    """

    def __init__(self, df, cle, probabilites=True):
        self.cle = cle
        self.df = df.set_index(cle).sort_index()
        self.min, self.max = self.df.index.min(), self.df.index.max()
        if self.df.index.has_duplicates or list(self.df.index) != list(range(self.min, self.max + 1)):
            raise ValueError(f"Table indexée par {cle} : les clés doivent être des entiers contigus sans doublon")
        if self.df.isna().any().any():
            raise ValueError(f"Table indexée par {cle} : valeurs manquantes")
        if probabilites and ((self.df < 0) | (self.df > 1)).any().any():
            raise ValueError(f"Table indexée par {cle} : probabilités hors de [0, 1]")

    def lire(self, cles, colonnes):
        """Une valeur par model point : la ligne vient de `cles`, la colonne de `colonnes`."""
        cles = np.clip(np.asarray(cles, dtype=int), self.min, self.max)
        if isinstance(colonnes, str):
            return self.df.loc[cles, colonnes].to_numpy()
        return np.array([self.df.at[c, col] for c, col in zip(cles, colonnes)])


def charger(dossier=DOSSIER):
    """Lit model points, tables et paramètres d'un dossier."""
    dossier = Path(dossier)
    with open(dossier / "parametres.json", encoding="utf-8") as f:
        parametres = json.load(f)
    tables = {
        "mortalite": Table(pd.read_csv(dossier / "table_mortalite.csv"), "age"),
        "rachats": Table(pd.read_csv(dossier / "table_rachats.csv"), "anciennete"),
    }
    model_points = pd.read_csv(dossier / "model_points.csv")
    return model_points, tables, parametres


def scenario_depuis_projection(df, h):
    """Transforme une projection des V1 à V3 en scénario pour le passif de la V4.

    Dans Prophet, le passif reçoit le taux servi de l'ALS (le module actif-passif).
    Ici, le scénario fournit pour chaque année : le taux servi par le fonds, le
    taux attendu par les assurés (taux à 10 ans) et le taux d'actualisation
    de l'année (déduit du déflateur).
    """
    d = df["deflateur"]
    taux_actualisation = (d.shift(1) / d - 1).fillna(0.0)
    taux_servi = df["taux_servi"].copy()
    taux_servi.loc[0] = h["passif"]["taux_servi_initial"]
    return pd.DataFrame({
        "taux_servi": taux_servi,
        "taux_attendu": df["taux_10ans"],
        "taux_actualisation": taux_actualisation,
    })
