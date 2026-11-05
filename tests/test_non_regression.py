"""Non-régression : les indicateurs publiés (resultats/indicateurs.json) sont ceux que calcule le code.

Si une modification change volontairement un résultat, relancer
`python scripts/resultats_reference.py`, puis justifier l'écart dans
docs/AMELIORATIONS_ET_LIMITES.md. Un écart non expliqué est une régression.
"""

import json
from pathlib import Path

import pytest

from src.projection import indicateurs, projeter, scenario
from src.prophet.epargne import construire
from src.prophet.tables import scenario_depuis_projection
from src.stochastique import projeter_stochastique, tvog

REFERENCE = json.loads((Path(__file__).resolve().parents[1] / "resultats" / "indicateurs.json").read_text(encoding="utf-8"))
SCENARIOS = list(REFERENCE["V1"])
TOLERANCE = dict(rel=1e-9, abs=1e-9)


@pytest.mark.parametrize("nom", SCENARIOS)
def test_v1_et_v4_deterministes(h, nom):
    df = projeter(h, scenario(h, nom))
    calcule = indicateurs(df) | {"pm_annee_10": df.loc[10, "pm"], "ppb_annee_10": df.loc[10, "ppb"]}
    for cle, attendu in REFERENCE["V1"][nom].items():
        assert calcule[cle] == pytest.approx(attendu, **TOLERANCE), cle

    r = construire(scenario_depuis_projection(df, h)).calculer().xs(0, level="annee")
    assert r["VA_SORTIES"].sum() == pytest.approx(REFERENCE["V4"][nom]["va_sorties"], **TOLERANCE)
    assert r["VA_COUT_TMG"].sum() == pytest.approx(REFERENCE["V4"][nom]["va_cout_tmg"], **TOLERANCE)


@pytest.mark.lent
def test_v2_stochastique(h):
    res = projeter_stochastique(h)
    calcule = res["synthese"] | tvog(h, res)
    for cle in ("be", "ic_be", "be_garanti", "fdb", "fuite", "va_apports", "tvog", "part_scenarios_avec_apport"):
        assert calcule[cle] == pytest.approx(REFERENCE["V2"][cle], **TOLERANCE), cle
