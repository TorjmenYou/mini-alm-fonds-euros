"""V5 : conventions de crédit (défaut par saut, décomposition), probabilité réelle, références des assurés.

Le test central reste l'absence d'arbitrage : quelle que soit la forme des pertes risque neutre
(lissée, par saut, recouvrement, concentration), un titre acheté à son prix de marché rapporte
en moyenne exactement le taux sans risque, et les prix sont ceux du marché.
"""

import copy
import math

import numpy as np
import pytest

from src.actif import Portefeuille
from src.courbes import CourbePlate, SpreadCredit
from src.passif import ReferenceAssures
from src.projection import indicateurs, projeter
from src.stochastique import projeter_stochastique
from src.v5 import bases, conventions as cv
from src.v5.courbes_marche import courbe_eiopa, spread_obligations
from src.v5.credit import CreditSaut
from src.v5.profils import hypotheses_profil
from src.v5.scenarios import ScenarioCourbe

R = 0.032
POINTS = {1: 0.004, 10: 0.015}


def portefeuille_une_obligation(h, credit, coupon=0.045, maturite=12, nominal=100.0):
    h2 = copy.deepcopy(h)
    h2["bilan_initial"].update(pm=nominal, ppb=0.0, fonds_propres=0.0)
    h2["actif"]["allocation_cible"] = {"obligations": 1.0, "actions": 0.0, "monetaire": 0.0}
    h2["actif"]["lignes_obligataires"] = [{"nominal": nominal, "coupon": coupon, "maturite": maturite}]
    h2["actif"]["credit"] = {"spread": POINTS, "mesure": "risque_neutre"}
    return Portefeuille(h2, credit=credit)


@pytest.mark.parametrize("part_saut,recouvrement,blocs", [(1.0, 0.4, (1.0,)), (0.8, 0.4, (0.26,) + (0.037,) * 20),
                                                          (0.8, 0.63, (0.5, 0.5)), (0.3, 0.0, (1.0,))])
def test_facteur_moyen_de_saut_egal_au_spread(part_saut, recouvrement, blocs):
    """Pour chaque année : 1 - p (1 - R) = exp(-dH_saut), donc facteur moyen = exp(-dH) total."""
    c = CreditSaut(POINTS, part_saut=part_saut, recouvrement=recouvrement, blocs=blocs)
    for t in range(1, 31):
        d_total, d_saut, d_lisse = c.increments(t)
        p = c.probabilite_defaut(t)
        assert 1 - p * (1 - recouvrement) == pytest.approx(math.exp(-d_saut), rel=1e-13)
        assert math.exp(-d_lisse) * math.exp(-d_saut) == pytest.approx(math.exp(-d_total), rel=1e-13)
        assert c.perte_realisee(t) == pytest.approx(SpreadCredit(POINTS).taux_perte(t), rel=1e-12)  # sans tirages


@pytest.mark.parametrize("part_saut,recouvrement", [(1.0, 0.4), (0.8, 0.63)])
def test_saut_memes_prix_de_marche(h, part_saut, recouvrement):
    c = CourbePlate(R)
    lisse = portefeuille_une_obligation(h, SpreadCredit(POINTS))
    saut = portefeuille_une_obligation(h, CreditSaut(POINTS, part_saut=part_saut, recouvrement=recouvrement))
    assert saut.vm_obligations(c) == pytest.approx(lisse.vm_obligations(c), rel=1e-14)


def test_saut_detention_au_prix_de_marche_rapporte_le_taux_sans_risque_en_moyenne(h):
    """Monte-Carlo sur les seuls tirages de défaut (taux fixes) : richesse finale moyenne = v0 (1 + R)^12,
    à trois erreurs types près ; un titre par saut n'est donc pas une source de valeur."""
    c = CourbePlate(R)
    credit = CreditSaut(POINTS, part_saut=1.0, recouvrement=0.4, horizon=12)
    n = 4000
    finales = []
    for j in range(n):
        p = portefeuille_une_obligation(h, credit.pour_scenario(j, n))
        v0 = p.vm_totale(c)
        for _ in range(12):
            p.encaisser_revenus(c, 1 + R)
        finales.append(p.vm_totale(c))
    finales = np.array(finales)
    paires = (finales[: n // 2] + finales[n // 2:]) / 2
    erreur = paires.std(ddof=1) / math.sqrt(len(paires))
    assert abs(finales.mean() - v0 * (1 + R) ** 12) < 3 * erreur
    assert (finales < 0.9 * v0 * (1 + R) ** 12).mean() > 0.05  # les pertes sont bien concentrées


def test_saut_rebasage_va_porte_par_la_part_lissee():
    sans_va, avec_va = courbe_eiopa(), courbe_eiopa(avec_va=True)
    c = CreditSaut.depuis(spread_obligations(), part_saut=0.8, recouvrement=0.4)
    r = bases.credit_sur_base(c, "avec_va")
    for t in (1, 5, 10, 30):
        assert r.probabilite_defaut(t) == pytest.approx(c.probabilite_defaut(t), rel=1e-14)
        assert avec_va.zc(t) * math.exp(-r.H(t)) == pytest.approx(sans_va.zc(t) * math.exp(-c.H(t)), rel=1e-12)


def test_recouvrement_incompatible_refuse():
    c = CreditSaut({1: 0.8}, part_saut=1.0, recouvrement=0.6)  # p = (1 - exp(-0,8)) / 0,4 > 1
    with pytest.raises(ValueError):
        c.probabilite_defaut(1)


def test_conventions_memes_prix_et_equivalent_certain_identique():
    """Toutes les conventions de crédit : mêmes prix de marché et même équivalent certain (perte moyenne)."""
    h = cv.appliquer(hypotheses_profil("B"), "sans_risque")
    conventions = cv.charger()["conventions_credit"]
    valeurs = {}
    for code in conventions:
        eco, _ = bases.equivalent_certain(h, "sans_va", None)
        df = projeter(h, eco, credit=cv.credit_valorisation(code))
        ind = indicateurs(df)
        assert abs(ind["fuite"]) < 1e-8, code
        valeurs[code] = (ind["vm_actif_initial"], ind["be"])
    ref = valeurs["lisse_integral"]  # un seul spread : mêmes prix de marché pour toutes les conventions
    for code, v in valeurs.items():
        assert v[0] == pytest.approx(ref[0], rel=1e-12) and v[1] == pytest.approx(ref[1], rel=1e-10), code


@pytest.mark.lent
def test_saut_aucune_fuite_en_stochastique():
    h = cv.appliquer(hypotheses_profil("B"), "sans_risque")
    g, cr = bases.gse(h, "sans_va", cv.credit_valorisation("saut_integral"))
    s = projeter_stochastique(h, g, credit=cr)["synthese"]
    assert abs(s["fuite"]) <= 2 * s["ic_fuite"]


# --- Probabilité réelle ---------------------------------------------------------------------------

def test_probabilite_reelle_interdit_la_valorisation_et_fige_les_spreads():
    h = cv.hypotheses_reelles(hypotheses_profil("B"), "stress_50")
    assert h["actif"]["credit"]["perte_attendue_reelle"] == pytest.approx(0.5 * spread_obligations().s(10))
    eco = cv.scenario_reel(h)
    df = projeter(h, eco)
    with pytest.raises(ValueError):
        indicateurs(df)
    p = Portefeuille(h)
    p.annee = 7
    assert p.courbe_obligations(courbe_eiopa()).zc(10) == pytest.approx(courbe_eiopa().zc(10) * math.exp(-spread_obligations().H(10)), rel=1e-14)
    assert eco.courbe(25) is eco.courbe(0)


def test_spreads_figes_refuses_en_risque_neutre():
    h = hypotheses_profil("B")
    h["actif"]["credit"]["spreads_figes"] = True
    with pytest.raises(ValueError):
        Portefeuille(h)


# --- Références des assurés -----------------------------------------------------------------------

def test_reference_sans_risque_dynamique_egale_l_ancienne_formule():
    """beta = 1 : niveau + (zc10(t) - zc10(0)) = zc10(t) + ajustement, avec ajustement = niveau - zc10(0)."""
    h = hypotheses_profil("B")
    hd = cv.appliquer(h, "sans_risque")
    hs = copy.deepcopy(h)
    hs["comportement"] = {"reference": "zc10_sans_risque", "ajustement": hd["comportement"]["niveau_initial"] - courbe_eiopa().taux_zc(10)}
    eco = ScenarioCourbe("ec", h["horizon_annees"], courbe_eiopa())
    a, b = projeter(hd, eco, credit=spread_obligations()), projeter(hs, eco, credit=spread_obligations())
    assert np.allclose(a["taux_10ans"].to_numpy(), b["taux_10ans"].to_numpy(), rtol=0, atol=1e-15)
    assert a.loc[1, "taux_10ans"] == pytest.approx(cv.niveau_initial_central(), abs=1e-15)


class _Courbe:
    def __init__(self, r10, r1):
        self.r10, self.r1 = r10, r1

    def taux_zc(self, k):
        return self.r10

    def taux_1an(self):
        return self.r1


def test_reference_lissee_livret_a_et_figee():
    base = {"reference": "dynamique", "niveau_initial": 0.03, "valeur_initiale_moteur": 0.035}
    lisse = ReferenceAssures({"comportement": dict(base, moteur="lisse", lissage=0.25)})
    assert lisse.taux(_Courbe(0.035, 0.0)) == pytest.approx(0.03)
    assert lisse.taux(_Courbe(0.055, 0.0)) == pytest.approx(0.03 + 0.25 * 0.02)
    assert lisse.taux(_Courbe(0.055, 0.0)) == pytest.approx(0.03 + (1 - 0.75 ** 2) * 0.02)
    la = ReferenceAssures({"comportement": dict(base, moteur="livret_a", valeur_initiale_moteur=0.03, livret_a_initial=0.017,
                                                part_court=0.5, plancher=0.005)})
    assert la.taux(_Courbe(0.0, 0.05)) == pytest.approx(0.03 + 0.5 * 0.02)
    assert la.taux(_Courbe(0.0, -0.02)) == pytest.approx(0.03 + (0.005 - 0.017))  # plancher du livret A
    fige = ReferenceAssures({"comportement": dict(base, moteur="fige")})
    assert fige.taux(_Courbe(0.09, 0.09)) == 0.03


def test_reference_independante_de_la_base_en_t0():
    for code in ("sans_risque", "taux_servi_marche", "livret_a"):
        for base in bases.BASES:
            h = cv.appliquer(hypotheses_profil("C"), code, base)
            eco, cr = bases.equivalent_certain(h, base, spread_obligations())
            assert projeter(h, eco, credit=cr).loc[1, "taux_10ans"] == pytest.approx(cv.niveau_initial_central(), abs=1e-14), (code, base)
