"""Cohérence entre les versions : V1 (déterministe), V2 (stochastique), V4 (passif à la Prophet)."""

import copy

import pytest

from src.gse import GSE
from src.projection import indicateurs, projeter, scenario
from src.stochastique import projeter_stochastique


def test_v2_sans_volatilite_retrouve_la_v1(h):
    """Avec une volatilité quasi nulle, chaque scénario stochastique se confond avec l'équivalent certain de la V1.

    Le Hull-White calé sur la courbe plate redonne alors exactement les taux forward, et les actions rapportent le taux sans risque.
    """
    hs = copy.deepcopy(h)
    hs["gse"]["hw_sigma"] = 1e-9
    hs["gse"]["vol_actions"] = 1e-9
    sto = projeter_stochastique(hs, GSE(hs, n=4))["synthese"]
    v1 = indicateurs(projeter(h, scenario(h, "central")))
    for cle in ("be", "be_prestations", "be_frais", "be_garanti", "fdb"):
        assert sto[cle] == pytest.approx(v1[cle], rel=1e-6), cle


def test_choc_nul_identique_au_scenario_de_base(h):
    eco = scenario(h, "central")
    a = indicateurs(projeter(h, eco))
    b = indicateurs(projeter(h, eco, choc_rachats=0.0, rachat_massif=0.0))
    assert a == b


def test_fdb_et_be_garanti_coherents(h):
    """BE des prestations = BE garanti + FDB ; avec un TMG à 0 et un taux servi positif, les FDB sont positives."""
    for nom in ("central", "hausse_taux_200pb", "baisse_taux_100pb", "krach_actions_25pc"):
        ind = indicateurs(projeter(h, scenario(h, nom)))
        assert ind["be_prestations"] == pytest.approx(ind["be_garanti"] + ind["fdb"])
        assert ind["fdb"] > 0
        assert ind["be"] == pytest.approx(ind["be_prestations"] + ind["be_frais"])


def test_be_garanti_egal_au_be_si_aucune_participation(h):
    """Si le fonds ne sert que le TMG et ne garde aucune PPB, il n'y a pas de prestation discrétionnaire."""
    hs = copy.deepcopy(h)
    hs["bilan_initial"]["ppb"] = 0.0
    hs["strategie"]["participation_minimale"] = 0.0
    hs["strategie"]["abandon_marge_assureur"] = False
    hs["passif"]["taux_servi_initial"] = 0.0
    hs["strategie"]["ecart_taux_cible"] = -1.0  # taux cible ramené au TMG
    ind = indicateurs(projeter(hs, scenario(hs, "central")))
    assert ind["fdb"] == pytest.approx(0.0, abs=1e-9)
