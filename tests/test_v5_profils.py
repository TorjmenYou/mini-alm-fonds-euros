"""V5 : profils d'assureur fictifs, bilans initiaux et réconciliations."""

import pytest

from src.actif import Portefeuille
from src.projection import indicateurs, projeter
from src.v5 import bases
from src.v5.profils import charger_profils, credit_profil, hypotheses_profil

PROFILS = ("A", "B", "C")


@pytest.mark.parametrize("nom", PROFILS)
def test_bilan_comptable_equilibre(nom):
    h = hypotheses_profil(nom)
    p = Portefeuille(h, credit=credit_profil())
    assert p.vnc_totale() == pytest.approx(sum(h["bilan_initial"].values()), rel=1e-12)
    assert p.monetaire >= 0 and all(l.nominal > 0 and l.maturite >= 1 for l in p.obligations)


@pytest.mark.parametrize("nom", PROFILS)
@pytest.mark.parametrize("base", bases.BASES)
def test_reconciliation_et_coherence_actif_passif(nom, base):
    """Valeur actionnaire = fonds propres comptables + plus ou moins-values latentes
    + (provisions comptables - BE), et fuite nulle : actifs et engagements sont valorisés
    avec les mêmes déflateurs."""
    h = hypotheses_profil(nom)
    eco, credit = bases.equivalent_certain(h, base, credit=credit_profil())
    df = projeter(h, eco, credit=credit)
    ind = indicateurs(df)
    p = Portefeuille(h, credit=credit)
    c0 = eco.courbe(0)
    b = h["bilan_initial"]
    pmvl = p.vm_totale(c0) - p.vnc_totale()
    marche = b["fonds_propres"] + pmvl + (b["pm"] + b["ppb"] + b["reserve_capitalisation"] - ind["be"])
    assert marche == pytest.approx(ind["valeur_assureur"], abs=1e-9)
    assert abs(ind["fuite"]) < 1e-8
    assert df["ecart_bilan"].abs().max() < 1e-6


def test_prix_de_marche_des_actifs_identiques_dans_les_deux_bases():
    for nom in PROFILS:
        h = hypotheses_profil(nom)
        vm = {}
        for base in bases.BASES:
            eco, credit = bases.equivalent_certain(h, base, credit=credit_profil())
            vm[base] = Portefeuille(h, credit=credit).vm_totale(eco.courbe(0))
        assert vm["avec_va"] == pytest.approx(vm["sans_va"], rel=1e-12), nom


def test_ordre_des_profils_sur_les_moins_values_et_les_coupons():
    """Le récit des profils se retrouve dans les chiffres : A a les coupons les plus faibles et les
    moins-values relatives les plus fortes, C l'inverse."""
    res = {}
    for nom in PROFILS:
        h = hypotheses_profil(nom)
        eco, credit = bases.equivalent_certain(h, "sans_va", credit=credit_profil())
        p = Portefeuille(h, credit=credit)
        coupon = sum(l.coupon * l.nominal for l in p.obligations) / sum(l.nominal for l in p.obligations)
        res[nom] = (coupon, p.vm_obligations(eco.courbe(0)) / p.vnc_obligations() - 1)
    assert res["A"][0] < res["B"][0] < res["C"][0]
    assert res["A"][1] < res["B"][1] < res["C"][1] < 0


def test_profils_declares_fictifs_et_statuts_presents():
    d = charger_profils()
    assert "FICTIFS" in d["objet"]
    for millesime, a in d["ancrages_coupons"].items():
        if not millesime.startswith("_"):
            assert a["statut"] == "calibré" and a["observations"]
