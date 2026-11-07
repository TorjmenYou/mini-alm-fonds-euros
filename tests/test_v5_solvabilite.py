"""V5 : briques de la vue prudentielle simplifiée (src/v5/solvabilite_v5.py)."""

import math

import pytest

from src.actif import Portefeuille
from src.v5 import bases, conventions as cv
from src.v5.profils import hypotheses_profil
from src.v5.solvabilite_v5 import PART_NON_SOUVERAINE, agreger_marche, bscr, choc_spread_calibre, facteur_spread_cqs2


def test_facteur_spread_qualite_2():
    assert facteur_spread_cqs2(3) == pytest.approx(0.042)
    assert facteur_spread_cqs2(5) == pytest.approx(0.07)
    assert facteur_spread_cqs2(7) == pytest.approx(0.084)
    assert facteur_spread_cqs2(10) == pytest.approx(0.105)
    assert facteur_spread_cqs2(12) == pytest.approx(0.115)
    assert facteur_spread_cqs2(25) == pytest.approx(0.18)


def test_agregation_marche_et_bscr():
    # hausse des taux : A = 0, seule la corrélation actions-spread de 0,75 joue
    assert agreger_marche(3.0, 4.0, 0.0, "taux_hausse") == pytest.approx(5.0)
    assert agreger_marche(0.0, 1.0, 1.0, "taux_hausse") == pytest.approx(math.sqrt(3.5))
    assert agreger_marche(1.0, 1.0, 0.0, "taux_baisse") == pytest.approx(math.sqrt(3.0))
    pertes = {"taux_hausse": 3.0, "taux_baisse": -1.0, "actions": 4.0, "spread": 0.0, "rachat_massif": 2.0}
    b = bscr(pertes, "taux_hausse", "rachat_massif")
    assert b["bscr"] == pytest.approx(math.sqrt(25 + 4 + 2 * 0.25 * 5 * 2))


def test_choc_spread_calibre_reproduit_la_perte_de_la_formule():
    h = cv.appliquer(hypotheses_profil("B"), "sans_risque", "avec_va")
    credit = cv.credit_valorisation("decompose")
    c0 = bases.courbe_base("avec_va")
    choc, perte, dmod = choc_spread_calibre(h, credit, "avec_va", c0)
    p = Portefeuille(h, credit=bases.credit_sur_base(credit, "avec_va"))
    vm = p.vm_obligations(c0)
    q = Portefeuille(h, credit=bases.credit_sur_base(credit, "avec_va"))
    q.choc_spread(choc)
    assert vm - q.vm_obligations(c0) == pytest.approx(perte, rel=1e-8)
    assert perte == pytest.approx(PART_NON_SOUVERAINE * vm * facteur_spread_cqs2(dmod))
