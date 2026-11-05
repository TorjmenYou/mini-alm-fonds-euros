"""Liquidité, financement des prestations et invariants comptables (V1)."""

import copy

import numpy as np
import pytest

from src.gse import ScenarioDeterministe
from src.projection import indicateurs, projeter, scenario


def scenarios_extremes(h):
    T, r0 = h["horizon_annees"], h["economie"]["taux_sans_risque"]
    return {
        "taux +700 pb": ScenarioDeterministe("hausse_extreme", T, r0, r0 + 0.07),
        "taux -500 pb": ScenarioDeterministe("baisse_extreme", T, r0, r0 - 0.05),
        "actions -90 %": ScenarioDeterministe("krach_extreme", T, r0, r0, -0.90),
    }


def verifier_invariants(df):
    proj = df.loc[1:]
    assert df["ecart_bilan"].dropna().abs().max() < 1e-7, "bilan comptable déséquilibré"
    for col in ["pm", "ppb", "reserve_capitalisation", "prestations", "frais", "apport_assureur",
                "vm_obligations", "vm_actions", "monetaire", "vnc_actif"]:
        assert (proj[col] >= -1e-9).all(), f"{col} négatif"
    assert abs(indicateurs(df)["fuite"]) < 1e-6 * df.attrs["vm_apres_choc"], "valeur créée ou détruite"


@pytest.mark.parametrize("nom", ["taux +700 pb", "taux -500 pb", "actions -90 %"])
def test_scenarios_extremes(h, nom):
    verifier_invariants(projeter(h, scenarios_extremes(h)[nom]))


@pytest.mark.parametrize("choc_rachats, rachat_massif", [(0.0, 1.0), (0.0, 0.4), (3.0, 0.0), (-0.5, 0.0)])
def test_rachats_extremes(h, choc_rachats, rachat_massif):
    df = projeter(h, scenario(h, "hausse_taux_200pb"), choc_rachats=choc_rachats, rachat_massif=rachat_massif)
    verifier_invariants(df)
    if rachat_massif == 1.0:
        # Rachat total : la PM et la PPB restante sortent toutes deux en t = 0
        # (une version antérieure du modèle ne versait la PPB qu'en t = 1)
        assert df.loc[0, "prestations"] == pytest.approx(h["bilan_initial"]["pm"] + h["bilan_initial"]["ppb"])
        assert df.loc[1:, "pm"].abs().max() < 1e-9


def test_fonds_sous_dote_finance_par_apport(h):
    """Actif très inférieur à la PM : les prestations sont payées, l'assureur apporte le manque, sans emprunt implicite."""
    hs = copy.deepcopy(h)
    hs["bilan_initial"]["fonds_propres"] = -900.0
    df = projeter(hs, scenario(hs, "central"))
    verifier_invariants(df)
    assert df["apport_assureur"].sum() > 0
    ind = indicateurs(df)
    # Sans actif suffisant, la valeur pour l'assureur est négative et égale aux apports actualisés, au signe près
    assert ind["valeur_assureur"] == pytest.approx(-ind["va_apports"], abs=1e-4)


@pytest.mark.parametrize("nom", ["central", "hausse_taux_200pb", "baisse_taux_100pb", "krach_actions_25pc"])
def test_pas_d_apport_dans_les_scenarios_usuels(h, nom):
    df = projeter(h, scenario(h, nom))
    verifier_invariants(df)
    assert df["apport_assureur"].abs().max() == 0.0


def test_generations_de_ppb_reprises_sous_8_ans(h):
    """Aucune dotation de PPB ne reste plus de 8 ans : la reprise obligatoire est contrôlée à chaque vieillissement."""
    from src.strategie import PPB
    ppb = PPB(40.0, 8)
    for annee in range(30):
        ppb.reprendre(ppb.reprise_obligatoire())
        ppb.vieillir_et_doter(5.0 + annee)
        assert len(ppb.generations) == 8 and min(ppb.generations) >= 0
    with pytest.raises(AssertionError):
        ppb.vieillir_et_doter(1.0)  # la génération de 8 ans n'a pas été reprise
