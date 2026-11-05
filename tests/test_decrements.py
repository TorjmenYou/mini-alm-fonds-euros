"""Décès et rachats : risques concurrents, non-négativité, conservation (V1 et V4)."""

import itertools

import numpy as np
import pandas as pd
import pytest

from conftest import scenario_constant
from src.passif import projeter_passif_un_an
from src.prophet.epargne import epargne
from src.prophet.moteur import Modele
from src.prophet.tables import DOSSIER, charger

GRILLE = [0.0, 0.01, 0.3, 0.5, 0.99, 1.0]


@pytest.mark.parametrize("q, r", list(itertools.product(GRILLE, GRILLE)))
def test_v1_sorties_positives_et_conservation(q, r):
    res = projeter_passif_un_an(100.0, 0.03, q, r)
    assert res["deces"] >= 0 and res["rachats"] >= 0 and res["pm_fin"] >= -1e-12
    # Conservation : PM début + intérêts = décès + rachats + PM fin
    assert 100.0 + res["interets"] == pytest.approx(res["deces"] + res["rachats"] + res["pm_fin"])
    assert res["pm_fin"] == pytest.approx(103.0 * (1 - q) * (1 - r))


@pytest.mark.parametrize("argument, valeur", [("taux_deces", 1.2), ("taux_deces", -0.1),
                                              ("taux_rachat", 1.5), ("taux_rachat", -0.01)])
def test_v1_refuse_les_probabilites_invalides(argument, valeur):
    kwargs = {"pm_debut": 100.0, "taux_servi": 0.02, "taux_deces": 0.01, "taux_rachat": 0.05}
    kwargs[argument] = valeur
    with pytest.raises(ValueError, match=argument):
        projeter_passif_un_an(**kwargs)


def modele_v4(model_points, T, **scenario):
    mp, tables, param = charger()
    param = dict(param, horizon_annees=T)
    return Modele(epargne, model_points, tables, param, scenario_constant(T, **scenario))


def model_points_extremes():
    """Âges et anciennetés extrêmes, dont des contrats proches de la fin de table (120 ans)."""
    return pd.DataFrame([
        (1, "Épargne individuelle", 20, 0, 100, 10.0, 0.00),
        (2, "Épargne individuelle", 95, 30, 50, 10.0, 0.02),
        (3, "Épargne individuelle", 110, 8, 10, 10.0, 0.00),
        (4, "Épargne individuelle", 118, 40, 5, 10.0, 0.00),
        (5, "Retraite collective", 119, 2, 5, 10.0, 0.00),
        (6, "Épargne individuelle", 125, 50, 5, 10.0, 0.00),
    ], columns=["id", "produit", "age", "anciennete", "nb_contrats", "pm", "tmg"])


@pytest.mark.parametrize("T", [1, 10, 60, 110])
@pytest.mark.parametrize("taux", [0.0, 0.03, 0.08])
def test_v4_invariants(T, taux):
    mp = pd.concat([charger()[0], model_points_extremes().assign(id=lambda d: d["id"] + 100)])
    r = modele_v4(mp, T, taux_servi=taux, taux_attendu=0.03).calculer()
    for col in ["PM_FIN", "DECES", "RACHATS", "PRESTATIONS", "NB_CONTRATS", "NB_DECES", "NB_RACHATS"]:
        assert (r[col] >= -1e-12).all(), col
    # Conservation de la PM et du nombre de contrats, année par année
    flux = r.loc[(slice(None), slice(1, None)), :]
    assert np.allclose(flux["PM_DEBUT"] + flux["INTERETS"], flux["PRESTATIONS"] + flux["PM_FIN"])
    nb_debut = r["NB_CONTRATS"].groupby(level="model_point").shift(1).loc[flux.index]
    assert np.allclose(nb_debut, flux["NB_DECES"] + flux["NB_RACHATS"] + flux["NB_CONTRATS"])


def test_v4_pm_par_contrat_coherente():
    """PM et nombre de contrats subissent les mêmes sorties : la PM moyenne n'évolue que par la revalorisation."""
    r = modele_v4(charger()[0], 30, taux_servi=0.02).calculer()
    flux = r.loc[(slice(None), slice(1, None)), :]
    nb_debut = r["NB_CONTRATS"].groupby(level="model_point").shift(1).loc[flux.index]
    vivant = flux["NB_CONTRATS"] > 1e-9
    moyenne_fin = flux["PM_FIN"][vivant] / flux["NB_CONTRATS"][vivant]
    moyenne_debut = (flux["PM_DEBUT"] / nb_debut)[vivant] * (1 + flux["TAUX_SERVI"][vivant])
    assert np.allclose(moyenne_fin, moyenne_debut)


def test_v4_extinction_a_la_fin_de_table():
    """À 120 ans et au-delà, qx = 1 : tout le monde décède, la PM s'éteint exactement, sans rachat."""
    r = modele_v4(model_points_extremes(), 5).calculer()
    for mp_id in (4, 5, 6):
        x = r.xs(mp_id, level="model_point")
        an_fin = int(np.argmax(x["QX"].to_numpy() >= 1.0))
        assert x["PM_FIN"].iloc[an_fin] == 0.0
        assert x["RACHATS"].iloc[an_fin] == 0.0
        assert x["NB_CONTRATS"].iloc[an_fin] == 0.0


def test_v4_refuse_une_table_invalide(tmp_path):
    import shutil
    for f in DOSSIER.glob("*.*"):
        shutil.copy(f, tmp_path / f.name)
    table = pd.read_csv(tmp_path / "table_mortalite.csv")
    table.loc[50, "qx"] = 1.4
    table.to_csv(tmp_path / "table_mortalite.csv", index=False)
    with pytest.raises(ValueError, match="probabilités"):
        charger(tmp_path)
