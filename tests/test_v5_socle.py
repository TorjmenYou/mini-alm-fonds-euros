"""V5, socle : courbe EIOPA, courbe des obligations détenues, portefeuille historique, comportement.

Chaque extension est désactivée par défaut (non-régression des V1 à V4 : test_non_regression.py).
Ici, on vérifie que chacune fait ce qu'elle annonce et reste cohérente avec le marché.
"""

import copy
import math

import numpy as np
import pytest

from src.actif import Portefeuille
from src.courbes import CourbeAvecSpread, CourbeForward, CourbeZeroCoupon
from src.gse import GSE
from src.passif import taux_attendu_assures
from src.projection import indicateurs, projeter, scenario
from src.stochastique import projeter_stochastique
from src.v5.courbes_marche import courbe_eiopa, lire_classeur_eiopa, provenance
from src.v5.scenarios import ScenarioCourbe


@pytest.fixture(scope="module")
def eiopa():
    return courbe_eiopa("20261031")


def projeter_courbe(h, courbe):
    return projeter(h, ScenarioCourbe("marche", h["horizon_annees"], courbe))


# --- Courbe EIOPA ----------------------------------------------------------------------------

def test_courbe_eiopa_lue_et_tracee(eiopa):
    fiche = provenance("20261031")
    assert fiche["statut"] == "observé"
    assert fiche["identifiant_courbe"].startswith("EUR_31_10_2026")
    assert len(fiche["sha256_archive"]) == 64
    assert len(eiopa.taux) == 150
    assert all(-0.01 < r < 0.10 for r in eiopa.taux)
    # La courbe avec correction pour volatilité doit dépasser la courbe de base de la VA
    # (en points de base dans la fiche) sur la partie liquide, jusqu'au dernier point liquide (LLP).
    avec_va = courbe_eiopa("20261031", avec_va=True)
    va = fiche["parametres_avec_va"]["VA"] / 10_000
    llp = fiche["parametres_sans_va"]["LLP"]
    for k in range(1, llp + 1):
        assert avec_va.taux[k - 1] - eiopa.taux[k - 1] == pytest.approx(va, abs=1e-9)


def test_lecture_du_classeur_eiopa(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "RFR_spot_no_VA"
    ws.append([None, None, None, None])
    ws.append([None, "Main menu", "Euro", "Austria"])
    ws.append([None, None, "EUR_TEST", "AT_TEST"])
    for nom, v in [("Coupon_freq", 1), ("LLP", 20), ("Convergence", 40), ("UFR", 3.3), ("alpha", 0.1), ("CRA", 10), ("VA", None)]:
        ws.append([None, nom, v, v])
    for k in range(1, 151):
        ws.append([None, k, 0.02 + k / 1e5, 0.0])
    chemin = tmp_path / "test_Term_Structures.xlsx"
    wb.save(chemin)
    lu = lire_classeur_eiopa(chemin)
    assert lu["identifiant"] == "EUR_TEST" and lu["parametres"]["UFR"] == 3.3
    assert lu["taux"][0] == pytest.approx(0.02001) and len(lu["taux"]) == 150
    with pytest.raises(ValueError):
        lire_classeur_eiopa(chemin, zone="Japan")


# --- Courbes dérivées -------------------------------------------------------------------------

def test_courbe_avec_spread(eiopa):
    assert all(CourbeAvecSpread(eiopa, 0.0).zc(k) == eiopa.zc(k) for k in range(1, 61))
    s = 0.015
    for k in (1, 10, 30):
        assert CourbeAvecSpread(eiopa, s).zc(k) / eiopa.zc(k) == pytest.approx(math.exp(-s * k), rel=1e-12)
    assert CourbeAvecSpread(eiopa, s).taux_pair(10) > eiopa.taux_pair(10)


def test_courbe_forward(eiopa):
    for t in (0, 5, 20):
        for k in (1, 10):
            assert CourbeForward(eiopa, t).zc(k) * eiopa.zc(t) == pytest.approx(eiopa.zc(t + k), rel=1e-12)


def test_scenario_courbe_retrouve_la_v1_sur_courbe_plate(h):
    ref = indicateurs(projeter(h, scenario(h, "central")))
    v5 = indicateurs(projeter_courbe(h, CourbeZeroCoupon.plate(h["economie"]["taux_sans_risque"])))
    for cle in ("be", "valeur_assureur", "fdb", "fuite"):
        assert v5[cle] == pytest.approx(ref[cle], rel=1e-9, abs=1e-9), cle


# --- Cohérence avec le marché sur la courbe EIOPA ----------------------------------------------

def test_aucune_fuite_sur_la_courbe_eiopa(h, eiopa):
    assert abs(indicateurs(projeter_courbe(h, eiopa))["fuite"]) < 1e-8


def test_obligations_risquees_au_prix_de_marche_en_risque_neutre(h, eiopa):
    """Spread entièrement traité comme intensité de perte risque neutre : aucune valeur créée."""
    h2 = copy.deepcopy(h)
    h2["actif"]["credit"] = {"spread": {2: 0.0035, 10: 0.0147, 30: 0.0202}}
    df = projeter_courbe(h2, eiopa)
    assert abs(indicateurs(df)["fuite"]) < 1e-8
    assert df["ecart_bilan"].abs().max() < 1e-6


def test_mesure_trajectoire_interdit_toute_valorisation(h, eiopa):
    """En mesure « trajectoire », la perte constatée est la perte réelle (ici nulle) : le spread entre
    en totalité dans les produits comptables, mais aucune valeur ne peut être calculée sur cette base."""
    h2 = copy.deepcopy(h)
    h2["actif"]["credit"] = {"spread": 0.015, "mesure": "trajectoire", "perte_attendue_reelle": 0.0}
    df = projeter_courbe(h2, eiopa)
    h3 = copy.deepcopy(h)
    h3["actif"]["credit"] = {"spread": 0.015}
    df_rn = projeter_courbe(h3, eiopa)
    assert df.loc[1:10, "taux_servi"].mean() > df_rn.loc[1:10, "taux_servi"].mean()  # rendement comptable plus élevé
    with pytest.raises(ValueError):
        indicateurs(df)


def test_choc_de_spread_revalorise_les_obligations(h, eiopa):
    h2 = copy.deepcopy(h)
    h2["actif"]["credit"] = {"spread": 0.015}
    p = Portefeuille(h2)
    avant = p.vm_obligations(eiopa)
    p.choc_spread(0.01)
    assert p.vm_obligations(eiopa) < avant


# --- Portefeuille historique ------------------------------------------------------------------

def lignes_echelle(h):
    a, b = h["actif"], h["bilan_initial"]
    total = b["pm"] + b["ppb"] + b["fonds_propres"]
    n, vnc = a["echelle_maturites_ans"], a["allocation_cible"]["obligations"] * total
    return [{"nominal": vnc / n, "coupon": a["coupon_obligations_initiales"], "maturite": m} for m in range(1, n + 1)]


def test_lignes_identiques_a_l_echelle_redonnent_la_v1(h):
    h2 = copy.deepcopy(h)
    h2["actif"]["lignes_obligataires"] = lignes_echelle(h)
    ref, v5 = indicateurs(projeter(h, scenario(h, "central"))), indicateurs(projeter(h2, scenario(h2, "central")))
    for cle in ("be", "valeur_assureur", "fdb", "fuite"):
        assert v5[cle] == pytest.approx(ref[cle], rel=1e-9, abs=1e-9), cle


def test_portefeuille_historique_et_reserve_de_capitalisation(h, eiopa):
    h2 = copy.deepcopy(h)
    h2["bilan_initial"]["reserve_capitalisation"] = 20.0
    h2["actif"]["lignes_obligataires"] = [
        {"nominal": 300.0, "coupon": 0.005, "maturite": 6},
        {"nominal": 300.0, "coupon": 0.012, "maturite": 9},
        {"nominal": 300.0, "coupon": 0.035, "maturite": 12},
    ]
    p = Portefeuille(h2)
    assert p.vnc_totale() == pytest.approx(1110.0)
    assert p.vm_obligations(eiopa) < p.vnc_obligations()  # anciennes lignes à faible coupon : moins-values latentes
    df = projeter_courbe(h2, eiopa)
    assert df.loc[0, "reserve_capitalisation"] == 20.0
    assert df["ecart_bilan"].abs().max() < 1e-6
    assert abs(indicateurs(df)["fuite"]) < 1e-8
    with pytest.raises(ValueError):
        h3 = copy.deepcopy(h2)
        h3["actif"]["lignes_obligataires"][0]["nominal"] = 2000.0
        Portefeuille(h3)


# --- Comportement des assurés -----------------------------------------------------------------

def test_taux_attendu_parametrable(h, eiopa):
    assert taux_attendu_assures(eiopa, h) == eiopa.taux_zc(10)
    h2 = copy.deepcopy(h)
    h2["comportement"] = {"reference": "fixe", "taux_fixe": 0.024, "ajustement": -0.002}
    assert taux_attendu_assures(eiopa, h2) == pytest.approx(0.022)
    h2["comportement"] = {"reference": "zc10_obligations"}
    assert taux_attendu_assures(eiopa, h2, CourbeAvecSpread(eiopa, 0.015)) > eiopa.taux_zc(10)
    h2["comportement"] = {"reference": "inconnue"}
    with pytest.raises(ValueError):
        taux_attendu_assures(eiopa, h2)


# --- Stochastique sur la courbe EIOPA ----------------------------------------------------------

@pytest.mark.lent
def test_gse_cale_sur_eiopa_martingale_et_fuite(h, eiopa):
    gse = GSE(h, courbe=eiopa, courbe_avant_choc=eiopa)
    m = gse.test_martingale()
    for cle in ("zero_coupon", "obligation", "actions"):
        assert np.all(np.abs(np.asarray(m[cle]) - 1) <= np.asarray(m["ic_" + cle]) * 1.5), cle
    h2 = copy.deepcopy(h)
    h2["actif"]["credit"] = {"spread": {2: 0.0035, 10: 0.0147, 30: 0.0202}}
    res = projeter_stochastique(h2, GSE(h2, courbe=eiopa, courbe_avant_choc=eiopa))
    s = res["synthese"]
    assert abs(s["fuite"]) <= 2 * s["ic_fuite"]
