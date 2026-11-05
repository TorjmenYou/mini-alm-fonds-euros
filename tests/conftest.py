"""Données partagées par les tests."""

import pandas as pd
import pytest

from src.hypotheses import charger_hypotheses


@pytest.fixture(scope="session")
def h():
    return charger_hypotheses()


def scenario_constant(T, taux_servi=0.02, taux_attendu=0.03, taux_actualisation=0.03):
    """Scénario de taux servi constant pour faire tourner le passif de la V4 seul."""
    return pd.DataFrame({
        "taux_servi": [taux_servi] * (T + 1),
        "taux_attendu": [taux_attendu] * (T + 1),
        "taux_actualisation": [0.0] + [taux_actualisation] * T,
    })
