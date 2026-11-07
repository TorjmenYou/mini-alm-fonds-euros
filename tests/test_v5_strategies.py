"""V5 : mécanique des stratégies ALM et des apports de capital."""

import numpy as np
import pytest

from src.actif import Portefeuille
from src.projection import indicateurs, projeter
from src.v5 import conventions as cv, strategies as stg
from src.v5.courbes_marche import courbe_eiopa
from src.v5.fiscalite import impot_annuel
from src.v5.profils import hypotheses_profil
from src.v5.scenarios import ScenarioCourbe

CREDIT = "k70_granulaire_correle"


def h_profil(p="A"):
    return cv.appliquer(hypotheses_profil(p), "taux_servi_marche", rachat_structurel="acpr")


def ec(h):
    df = projeter(h, ScenarioCourbe("ec", h["horizon_annees"], courbe_eiopa()), credit=cv.credit_valorisation(CREDIT))
    return df, indicateurs(df)


def test_meme_bilan_initial_pour_toutes_les_strategies():
    c0 = courbe_eiopa()
    ref = Portefeuille(stg.appliquer_strategie(h_profil(), "passive"), credit=cv.credit_valorisation(CREDIT))
    for code in stg.charger()["strategies"]:
        p = Portefeuille(stg.appliquer_strategie(h_profil(), code), credit=cv.credit_valorisation(CREDIT))
        assert p.vm_totale(c0) == pytest.approx(ref.vm_totale(c0), rel=1e-14), code
        assert p.vnc_totale() == pytest.approx(ref.vnc_totale(), rel=1e-14), code
        assert p.actions_vm == pytest.approx(ref.actions_vm, rel=1e-14), code


def test_apport_initial_en_tresorerie_n_est_pas_un_profit():
    """L'apport augmente l'actif et les fonds propres comptables de son montant exact, sans plus-value ;
    la valeur nette de l'apport (valeur - apport) ne dépasse pas la valeur sans apport de plus d'un écart
    de comportement (taux servi) : ici elle est même légèrement inférieure."""
    h0, K = stg.appliquer_strategie(h_profil("B"), "passive"), 50.0
    hk = stg.appliquer_strategie(h_profil("B"), "passive", K)
    c0 = courbe_eiopa()
    p0, pk = Portefeuille(h0, credit=cv.credit_valorisation(CREDIT)), Portefeuille(hk, credit=cv.credit_valorisation(CREDIT))
    assert pk.vm_totale(c0) - p0.vm_totale(c0) == pytest.approx(K, rel=1e-12)
    assert pk.pvl_actions() == pytest.approx(p0.pvl_actions(), rel=1e-12)
    dfk, ik = ec(hk)
    _, i0 = ec(h0)
    assert dfk.loc[0, "fonds_propres"] == pytest.approx(h0["bilan_initial"]["fonds_propres"] + K)
    assert abs(ik["fuite"]) < 1e-8 and abs(dfk["ecart_bilan"]).max() < 1e-8
    assert ik["valeur_assureur"] - K < i0["valeur_assureur"] + 1e-9


def test_repositionnement_vend_les_petits_coupons_au_prix_de_marche():
    h = stg.appliquer_strategie(h_profil("A"), "repositionnement")
    c0 = courbe_eiopa()
    p = Portefeuille(h, credit=cv.credit_valorisation(CREDIT))
    vm0, vnc0 = p.vm_totale(c0), p.vnc_obligations()
    coupons = sorted({l.coupon for l in p.obligations})
    pmv = p.vendre_coupons_bas(c0, 0.25)
    assert p.vm_totale(c0) == pytest.approx(vm0, rel=1e-12)  # vente au prix de marché : valeur inchangée
    assert p.vnc_obligations() == pytest.approx(0.75 * vnc0, rel=1e-12)
    assert pmv < 0
    assert min(l.coupon for l in p.obligations if l.nominal > 1e-9) >= coupons[0]
    df, ind = ec(h)
    assert df.loc[0, "pmv_repositionnement"] == pytest.approx(pmv, rel=1e-12)
    assert abs(ind["fuite"]) < 1e-8 and abs(df["ecart_bilan"]).max() < 1e-8


def test_echelle_de_reinvestissement():
    h = stg.appliquer_strategie(h_profil("C"), "reinvestissement_progressif")
    p = Portefeuille(h, credit=cv.credit_valorisation(CREDIT))
    n0 = len(p.obligations)
    p.monetaire += 100.0
    p.reequilibrer(courbe_eiopa(), h["actif"]["allocation_cible"])
    nouvelles = p.obligations[n0:]
    assert sorted(l.maturite for l in nouvelles) == [3, 5, 7, 10, 15]
    assert len({round(l.nominal, 9) for l in nouvelles}) == 1
    courbe_obl = p.courbe_obligations(courbe_eiopa())
    for l in nouvelles:
        assert l.coupon == pytest.approx(courbe_obl.taux_pair(l.maturite), rel=1e-14)


def test_impots_avec_report_des_deficits():
    res = np.array([[-3e6, 5e6, 1e6, 2e6]])
    imp = stg.impots_par_scenario(res, 1.0)
    report, attendu = 0.0, []
    for r in res[0]:
        total, _, _, report = impot_annuel(r, 1e12, report, 1.0)
        attendu.append(total)
    assert np.allclose(imp[0], attendu)
    assert imp[0, 0] == 0.0 and imp[0, 1] < 0.258 * 5e6


def test_distribution_de_l_excedent_de_fonds_propres():
    """Politique de distribution : fuite nulle avec les dividendes, bilan équilibré, fonds propres
    ramenés à leur cible en % de la PM, aucun dividende sans politique de distribution."""
    h = stg.appliquer_strategie(h_profil("C"), "passive", 30.0)
    df, ind = ec(h)
    assert abs(ind["fuite"]) < 1e-8 and abs(df["ecart_bilan"]).max() < 1e-8
    cible = h["strategie_alm"]["distribution"]["fonds_propres_pct_pm"]
    declares = df["dividende_a_payer"] > 0
    assert declares.any()
    assert np.allclose(df.loc[declares, "fonds_propres"], cible * df.loc[declares, "pm"])
    assert ind["va_dividendes"] > 0
    sans = stg.appliquer_strategie(h_profil("C"), "passive", 30.0)
    sans["strategie_alm"].pop("distribution")
    _, i2 = ec(sans)
    assert abs(i2["fuite"]) < 1e-8
    assert i2["va_dividendes"] == 0.0


def test_retention_ne_distribue_que_la_part_prevue_de_l_excedent():
    """Rétention : la moitié de l'excédent sur la cible est distribuée, l'autre reste en fonds propres."""
    h = stg.appliquer_strategie(h_profil("C"), "distribution_retention", 30.0)
    assert h["strategie_alm"]["distribution"]["part_distribuee"] == 0.5
    df, ind = ec(h)
    assert abs(ind["fuite"]) < 1e-8 and abs(df["ecart_bilan"]).max() < 1e-8
    cible = h["strategie_alm"]["distribution"]["fonds_propres_pct_pm"]
    declares = df["dividende_a_payer"] > 0
    assert declares.any()
    # dividende = 0,5 x (fonds propres avant distribution - cible) = fonds propres après distribution - cible
    assert np.allclose(df.loc[declares, "dividende_a_payer"], df.loc[declares, "fonds_propres"] - cible * df.loc[declares, "pm"])
    _, i_passive = ec(stg.appliquer_strategie(h_profil("C"), "passive", 30.0))
    assert ind["va_dividendes"] < i_passive["va_dividendes"]


class _PPB:
    def __init__(self, stock, obligatoire=0.0):
        self.stock, self._obligatoire = stock, obligatoire

    def reprise_obligatoire(self):
        return self._obligatoire


def test_plancher_de_ppb_limite_les_reprises_volontaires():
    from src.strategie import decider_taux_servi
    h = stg.appliquer_strategie(h_profil("B"), "taux_servi_competitif_preservant")
    b = h["bilan_initial"]
    plancher = h["strategie"]["plancher_ppb_pct_pm"]
    assert plancher == pytest.approx(0.5 * b["ppb"] / b["pm"])
    pm = 1000.0
    for stock in (0.5 * plancher * pm, 2 * plancher * pm, 5 * plancher * pm):
        st = decider_taux_servi(0.0, pm, _PPB(stock), 0.0, 0.05, h)  # aucun produit financier : besoin non couvert
        assert st["reprise_ppb"] == pytest.approx(0.25 * max(stock - plancher * pm, 0.0))
    sans = stg.appliquer_strategie(h_profil("B"), "taux_servi_competitif")
    assert "plancher_ppb_pct_pm" not in sans["strategie"]
    st = decider_taux_servi(0.0, pm, _PPB(10.0), 0.0, 0.05, sans)
    assert st["reprise_ppb"] == pytest.approx(0.5 * 10.0)  # comportement inchangé sans plancher
