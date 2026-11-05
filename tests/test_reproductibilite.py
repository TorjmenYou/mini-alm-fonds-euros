"""Reproductibilité des simulations et construction des tirages antithétiques."""

import numpy as np
import pytest

from src.gse import GSE, demi_intervalle
from src.stochastique import projeter_stochastique


def test_meme_graine_memes_scenarios(h):
    a, b = GSE(h, n=100), GSE(h, n=100)
    assert np.array_equal(a.x, b.x)
    assert np.array_equal(a.deflateurs, b.deflateurs)
    assert np.array_equal(a.rendements_actions, b.rendements_actions)


def test_graines_differentes_scenarios_differents(h):
    assert not np.array_equal(GSE(h, n=100, graine=1).x, GSE(h, n=100, graine=2).x)


def test_tirages_antithetiques(h):
    """La trajectoire j + n/2 est le miroir de la trajectoire j : facteur de taux opposé."""
    g = GSE(h, n=200)
    assert np.allclose(g.x[:100], -g.x[100:])


def test_nombre_de_scenarios_impair_refuse(h):
    with pytest.raises(AssertionError):
        GSE(h, n=101)


def test_be_reproductible(h):
    s1 = projeter_stochastique(h, GSE(h, n=40))["synthese"]
    s2 = projeter_stochastique(h, GSE(h, n=40))["synthese"]
    assert s1["be"] == s2["be"]


def test_intervalle_antithetique():
    """Sur des paires parfaitement anticorrélées, la moyenne de chaque paire est exacte : intervalle nul."""
    v = np.concatenate([np.arange(1.0, 51.0), -np.arange(1.0, 51.0)])
    assert demi_intervalle(v) == pytest.approx(0.0)
    # Sur des tirages indépendants, l'intervalle est celui de la moyenne de paires
    rng = np.random.default_rng(0)
    w = rng.standard_normal(10_000)
    paires = (w[:5000] + w[5000:]) / 2
    assert demi_intervalle(w) == pytest.approx(1.96 * paires.std(ddof=1) / np.sqrt(5000))
