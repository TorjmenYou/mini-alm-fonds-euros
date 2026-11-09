"""V5 : tests de non-arbitrage indépendants, bases de valorisation et fiscalité.

Les prix de référence sont recalculés ici par des formules fermées écrites dans le test, sans passer
par les classes de courbes du modèle : une erreur commune au code et au test est ainsi peu probable.

Principe vérifié : en risque neutre, un actif acheté à son prix de marché a une valeur actuelle nette
nulle, quel que soit son spread. Le spread rémunère la perte attendue risque neutre ; le compter à la
fois dans l'actualisation et dans les flux (ou l'oublier dans l'un des deux) créerait ou détruirait
de la valeur : c'est la double comptabilisation que ces tests interdisent.
"""

import copy
import math

import numpy as np
import pytest

from src.actif import Portefeuille
from src.courbes import CourbePlate, SpreadCredit
from src.gse import GSE
from src.projection import indicateurs, projeter
from src.v5 import bases
from src.v5.courbes_marche import courbe_eiopa, spread_obligations
from src.v5.fiscalite import impot_annuel

R = 0.032  # taux sans risque plat (actuariel) des tests analytiques
POINTS = {1: 0.004, 10: 0.015}  # spread continu : 40 pb à 1 an, 150 pb à 10 ans, interpolation linéaire, plat ensuite


def H_analytique(u):
    """Spread cumulé recalculé à la main : s(u) x u, s linéaire de 1 à 10 ans, plat ailleurs."""
    s = 0.004 if u <= 1 else (0.015 if u >= 10 else 0.004 + (u - 1) / 9 * 0.011)
    return s * u


def prix_analytique(nominal, coupon, maturite, t=0):
    """Prix en t d'une obligation risquée survivante (convention de recouvrement en valeur de marché)."""
    flux = [(k, coupon * nominal) for k in range(1, maturite - t + 1)]
    flux[-1] = (flux[-1][0], flux[-1][1] + nominal)
    return sum(f * (1 + R) ** (-k) * math.exp(-(H_analytique(t + k) - H_analytique(t))) for k, f in flux)


def portefeuille_une_obligation(h, coupon=0.045, maturite=12, nominal=100.0, credit=None, mesure="risque_neutre"):
    h2 = copy.deepcopy(h)
    h2["bilan_initial"].update(pm=nominal, ppb=0.0, fonds_propres=0.0)
    h2["actif"]["allocation_cible"] = {"obligations": 1.0, "actions": 0.0, "monetaire": 0.0}
    h2["actif"]["lignes_obligataires"] = [{"nominal": nominal, "coupon": coupon, "maturite": maturite}]
    h2["actif"]["credit"] = {"spread": credit if credit is not None else POINTS, "mesure": mesure, "perte_attendue_reelle": 0.0}
    return Portefeuille(h2)


# --- Obligation risquée : prix et flux connus analytiquement -----------------------------------

def test_prix_de_marche_egal_a_la_formule_fermee(h):
    p = portefeuille_une_obligation(h)
    assert p.vm_obligations(CourbePlate(R)) == pytest.approx(prix_analytique(100.0, 0.045, 12), rel=1e-12)


def test_detention_au_prix_de_marche_rapporte_exactement_le_taux_sans_risque(h):
    """Achat au prix de marché, détention jusqu'à l'échéance, coupons placés au taux sans risque :
    la richesse (obligation survivante + trésorerie) croît exactement au taux sans risque chaque année,
    donc la valeur actuelle nette de l'achat est nulle. Une double prise en compte du spread
    (actualisation et pertes) ferait croître la richesse à R - s ; son oubli, à R + s."""
    c = CourbePlate(R)
    p = portefeuille_une_obligation(h)
    v0 = p.vm_totale(c)
    for t in range(1, 13):
        p.encaisser_revenus(c, 1 + R)
        assert p.vm_totale(c) == pytest.approx(v0 * (1 + R) ** t, rel=1e-12), t
        if t < 12:  # valeur de l'obligation survivante : formule fermée sur le nominal survivant
            survivant = 100.0 * math.exp(-H_analytique(t))
            assert p.vm_obligations(c) == pytest.approx(prix_analytique(survivant, 0.045, 12, t), rel=1e-12), t
    assert p.vm_totale(c) * (1 + R) ** (-12) - v0 == pytest.approx(0.0, abs=1e-10)


def test_pertes_cumulees_egales_au_spread_cumule(h):
    """Pas de double comptabilisation : la perte de nominal cumulée sur la vie du titre est exactement
    1 - exp(-H(T)), ni plus (perte et décote comptées deux fois) ni moins."""
    c = CourbePlate(R)
    p = portefeuille_une_obligation(h, maturite=10)
    for _ in range(9):
        p.encaisser_revenus(c, 1 + R)
    assert p.obligations[0].nominal == pytest.approx(100.0 * math.exp(-H_analytique(9)), rel=1e-12)


def test_spread_nul_retrouve_l_obligation_sans_risque(h):
    c = CourbePlate(R)
    p = portefeuille_une_obligation(h, credit=0.0)
    v0 = p.vm_totale(c)
    for _ in range(5):
        p.encaisser_revenus(c, 1 + R)
    assert p.vm_totale(c) == pytest.approx(v0 * (1 + R) ** 5, rel=1e-12)


def test_trajectoire_prime_visible_en_comptabilite_mais_pas_valorisable(h):
    """Sans perte réelle, le titre rapporte plus que le taux sans risque en comptabilité : c'est la prime
    de risque, rémunération d'un risque porté, pas une valeur actuelle nette positive."""
    c = CourbePlate(R)
    p = portefeuille_une_obligation(h, mesure="trajectoire")
    v0 = p.vm_totale(c)
    for _ in range(5):
        p.encaisser_revenus(c, 1 + R)
    assert p.vm_totale(c) > v0 * (1 + R) ** 5


@pytest.mark.lent
def test_martingale_d_un_zero_coupon_risque_sous_hull_white(h):
    """E[D(t) x valeur en t du zéro-coupon risqué survivant] = prix de marché en t = 0."""
    c0 = courbe_eiopa("20261031")
    gse = GSE(h, courbe=c0, courbe_avant_choc=c0)
    credit = SpreadCredit(POINTS)
    T = 30
    prix0 = c0.zc(T) * math.exp(-credit.H(T))
    for t in (5, 15, 25):
        valeurs = np.array([gse.deflateurs[j, t] * math.exp(-credit.H(t)) * gse.scenarios()[j].courbe(t).zc(T - t)
                            * math.exp(-(credit.H(T) - credit.H(t))) for j in range(gse.n)])
        paires = (valeurs[: gse.n // 2] + valeurs[gse.n // 2:]) / 2  # paires antithétiques
        ic = 1.96 * paires.std(ddof=1) / math.sqrt(len(paires))
        assert abs(valeurs.mean() / prix0 - 1) <= 2 * ic / prix0 + 1e-12, t


# --- Bases de valorisation : sans VA et avec VA ---------------------------------------------------

def test_bases_meme_prix_de_marche_des_actifs_et_aucune_fuite(h):
    h2 = copy.deepcopy(h)
    h2["comportement"] = {"reference": "zc10_obligations"}
    res = {}
    for base in bases.BASES:
        eco, credit = bases.equivalent_certain(h2, base, credit=spread_obligations())
        df = projeter(h2, eco, credit=credit)
        res[base] = (df, indicateurs(df))
        assert abs(res[base][1]["fuite"]) < 1e-8, base
    # Les actifs sont à leur prix de marché dans les deux bases : seule l'actualisation du passif change.
    assert res["avec_va"][1]["vm_actif_initial"] == pytest.approx(res["sans_va"][1]["vm_actif_initial"], rel=1e-12)
    # Le taux de référence des assurés (courbe des obligations détenues) ne dépend pas de la base.
    assert res["avec_va"][0].loc[1, "taux_10ans"] == pytest.approx(res["sans_va"][0].loc[1, "taux_10ans"], rel=1e-12)
    # La VA réduit le BE : effet réglementaire, à présenter à part.
    assert res["avec_va"][1]["be"] < res["sans_va"][1]["be"]


def test_rebasage_conserve_les_prix_risques():
    sans_va, avec_va = courbe_eiopa("20261031"), courbe_eiopa("20261031", avec_va=True)
    credit = spread_obligations()
    rebase = bases.credit_sur_base(credit, "avec_va")
    for u in (1, 5, 10, 30, 60):
        assert avec_va.zc(u) * math.exp(-rebase.H(u)) == pytest.approx(sans_va.zc(u) * math.exp(-credit.H(u)), rel=1e-12)


# --- Fiscalité ------------------------------------------------------------------------------------

def test_impot_taux_normal_et_contribution_sociale():
    u = 10_000_000  # 1 unité = 10 M EUR
    total, is_, cs, report = impot_annuel(10.0, 300.0, 0.0, u)  # résultat 100 M EUR, chiffre d'affaires 3 Md EUR
    assert is_ == pytest.approx(2.5)                               # 25 %
    assert cs == pytest.approx(0.033 * (2.5 - 0.0763))             # 3,3 % au-delà de 763 000 EUR d'impôt
    assert total / 10.0 == pytest.approx(0.25 + 0.033 * (0.25 - 0.0763 / 10.0))
    assert report == 0.0


def test_contribution_sociale_sous_les_seuils_et_exoneration_pme():
    u = 1.0  # unités en euros
    assert impot_annuel(2_000_000, 50e6, 0.0, u)[2] == 0.0          # impôt de 500 000 EUR < abattement
    assert impot_annuel(5_000_000, 5e6, 0.0, u, exoneration_pme_possible=True)[2] == 0.0
    assert impot_annuel(5_000_000, 5e6, 0.0, u)[2] > 0.0            # condition de détention non remplie


def test_deficits_reportables_plafonnes():
    u = 1.0
    assert impot_annuel(-3e6, 1e9, 0.0, u)[3] == 3e6
    total, is_, cs, report = impot_annuel(5e6, 1e9, 10e6, u)       # imputation : 1 M + 50 % x 4 M = 3 M
    assert is_ == pytest.approx(0.25 * 2e6) and report == pytest.approx(7e6)
