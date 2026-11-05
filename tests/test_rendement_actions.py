"""Décomposition du rendement total des actions en dividende et variation de cours.

Le scénario donne un facteur de rendement total G (valeur de fin / valeur de
début, dividende compris). Quel que soit G, le dividende plus la valeur
ex-dividende doivent redonner exactement G fois la valeur de début : la
décomposition ne doit ni créer ni détruire de valeur, même quand la perte
dépasse le rendement du dividende (G < d).
"""

import pytest

from src.actif import Portefeuille
from src.courbes import CourbePlate
from src.gse import ScenarioDeterministe
from src.projection import indicateurs, projeter


@pytest.mark.parametrize("facteur", [1.25, 1.03, 0.5, 0.03, 0.02, 0.01, 0.0])
def test_conservation_de_la_valeur_des_actions(h, facteur):
    port = Portefeuille(h)
    vm0, d = port.actions_vm, h["economie"]["rendement_dividende_actions"]
    rev = port.encaisser_revenus(CourbePlate(0.03), facteur)
    assert rev["dividendes"] + port.actions_vm == pytest.approx(vm0 * facteur, abs=1e-12)
    assert rev["dividendes"] >= 0 and port.actions_vm >= 0
    if facteur >= d:
        # Cas usuel, inchangé : dividende de d x valeur de début, le reste en cours
        assert rev["dividendes"] == pytest.approx(d * vm0, abs=1e-12)


def test_perte_superieure_a_100_pc_refusee(h):
    with pytest.raises(ValueError):
        Portefeuille(h).encaisser_revenus(CourbePlate(0.03), -0.05)


class KrachAnnee1(ScenarioDeterministe):
    """Courbe plate à r ; les actions rapportent G l'année 1, puis r."""

    def __init__(self, T, r, facteur):
        super().__init__("krach_annee_1", T, r, r)
        self.facteur_annee_1 = facteur

    def facteur_actions(self, t):
        return self.facteur_annee_1 if t == 1 else 1 + self.r


@pytest.mark.parametrize("facteur", [0.5, 0.03, 0.01, 0.0])
def test_valeur_perdue_egale_a_la_perte_des_actions(h, facteur):
    """Tous les actifs rapportent r, sauf les actions l'année 1 : la valeur perdue
    (« fuite ») doit être exactement la perte des actions, actualisée d'un an :
    VM actions initiale x (1 + r - G) / (1 + r)."""
    r = h["economie"]["taux_sans_risque"]
    vm_actions0 = Portefeuille(h).actions_vm
    df = projeter(h, KrachAnnee1(h["horizon_annees"], r, facteur))
    attendu = vm_actions0 * (1 + r - facteur) / (1 + r)
    assert indicateurs(df)["fuite"] == pytest.approx(attendu, abs=1e-7)
