"""V5 : conventions de sécurisation avant l'optimisation (copule de défaut, probabilité réelle,
référence composite, rachat structurel au sens de l'ACPR, spread zéro-coupon, vue prudentielle)."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from src.actif import Portefeuille
from src.courbes import CourbePlate
from src.passif import ReferenceAssures
from src.projection import indicateurs, projeter
from src.stochastique import projeter_stochastique
from src.v5 import bases, conventions as cv
from src.v5.courbes_marche import courbe_eiopa, spread_obligations
from src.v5.credit import CreditSaut
from src.v5.profils import hypotheses_profil
from src.v5.solvabilite_v5 import facteur_spread, fonds_excedentaires, mcr

RACINE = Path(__file__).resolve().parents[1]
R = 0.032
POINTS = {1: 0.004, 10: 0.015}


def une_obligation(h, credit, maturite=12):
    h2 = copy.deepcopy(h)
    h2["bilan_initial"].update(pm=100.0, ppb=0.0, fonds_propres=0.0)
    h2["actif"]["allocation_cible"] = {"obligations": 1.0, "actions": 0.0, "monetaire": 0.0}
    h2["actif"]["lignes_obligataires"] = [{"nominal": 100.0, "coupon": 0.045, "maturite": maturite}]
    h2["actif"]["credit"] = {"spread": POINTS, "mesure": "risque_neutre"}
    return Portefeuille(h2, credit=credit)


# --- Copule de défaut -----------------------------------------------------------------------------

def test_copule_conserve_la_probabilite_de_chaque_bloc():
    c = CreditSaut(POINTS, part_saut=1.0, recouvrement=0.4, blocs=(0.02,) * 50, correlation=0.3, horizon=10)
    n = 2000
    freq = np.zeros(10)
    for j in range(n):
        cj = c.pour_scenario(j, n)
        for t in range(1, 11):
            freq[t - 1] += cj._defauts(t, c.probabilite_defaut(t)).mean()
    freq /= n
    for t in range(1, 11):
        p = c.probabilite_defaut(t)
        assert abs(freq[t - 1] - p) < 4 * math.sqrt(p * (1 - p) / (50 * n)) * 3, t  # marge pour la corrélation


def test_copule_concentre_les_pertes_sans_changer_leur_moyenne():
    pertes = {}
    for rho in (None, 0.5):
        c = CreditSaut(POINTS, part_saut=1.0, recouvrement=0.4, blocs=(0.02,) * 50, correlation=rho, horizon=10)
        pertes[rho] = np.array([c.pour_scenario(j, 4000).perte_realisee(10) for j in range(4000)])
    attendu = CreditSaut(POINTS).perte_realisee(10)
    for rho, v in pertes.items():
        assert abs(v.mean() - attendu) < 4 * v.std() / math.sqrt(len(v)), rho
    assert pertes[0.5].std() > 2 * pertes[None].std()


def test_copule_detention_au_prix_de_marche_rapporte_le_taux_sans_risque(h):
    c = CourbePlate(R)
    credit = CreditSaut(POINTS, part_saut=1.0, recouvrement=0.4, blocs=(0.02,) * 50, correlation=0.2, horizon=12)
    n = 2000
    finales = []
    for j in range(n):
        p = une_obligation(h, credit.pour_scenario(j, n))
        v0 = p.vm_totale(c)
        for _ in range(12):
            p.encaisser_revenus(c, 1 + R)
        finales.append(p.vm_totale(c))
    finales = np.array(finales)
    paires = (finales[: n // 2] + finales[n // 2:]) / 2
    assert abs(finales.mean() - v0 * (1 + R) ** 12) < 3 * paires.std(ddof=1) / math.sqrt(len(paires))


# --- Attribution : un passif indépendant des actifs ne voit pas la forme des pertes --------------

def test_passif_independant_des_actifs_meme_be_quelle_que_soit_la_forme_des_pertes():
    h = cv.appliquer(hypotheses_profil("B"), "taux_servi_marche", rachat_structurel="acpr")
    h["rachats_dynamiques"].update(rc_max=0.0, rc_min=0.0)
    h["strategie"].update(participation_minimale=0.0, abandon_marge_assureur=False, ecart_taux_cible=-1.0)
    be = {}
    for code in ("k_lisse_bootstrap", "k70_souverain_bloc", "k70_granulaire_correle"):
        g, cr = bases.gse(h, "sans_va", cv.credit_valorisation(code), n=20)
        be[code] = projeter_stochastique(h, g, credit=cr)["par_scenario"]["be"].to_numpy()
    for code, v in be.items():
        assert np.allclose(v, be["k_lisse_bootstrap"], rtol=0, atol=1e-9), code


# --- Probabilité réelle -----------------------------------------------------------------------------

def test_defauts_reels_moyenne_et_interdiction_de_valoriser():
    c = cv.credit_reel("k70_granulaire_correle", "central")
    assert c.perte_realisee_reelle(5) == pytest.approx(0.00061 * 0.5)
    s = cv.credit_reel("k70_granulaire_correle", "stress_rapport_2")
    assert s.probabilite_defaut_reelle(10) == pytest.approx(0.5 * s.probabilite_defaut(10))
    h = cv.hypotheses_reelles_stochastiques(hypotheses_profil("A"))
    from src.v5.scenarios import ScenarioCourbe
    df = projeter(h, ScenarioCourbe("ec", h["horizon_annees"], courbe_eiopa()), credit=c.pour_scenario(0, 2))
    with pytest.raises(ValueError):
        indicateurs(df)


# --- Références des assurés ------------------------------------------------------------------------

class _Courbe:
    def __init__(self, r10, r1):
        self.r10, self.r1 = r10, r1

    def taux_zc(self, k):
        return self.r10

    def taux_1an(self):
        return self.r1


def test_reference_composite_formule():
    comps = [{"poids": 0.6, "niveau_initial": 0.0263, "moteur": "zc10_sans_risque", "lissage": 0.5, "beta": 1.0, "valeur_initiale_moteur": 0.03},
             {"poids": 0.4, "niveau_initial": 0.017, "moteur": "taux_1an", "lissage": 1.0, "beta": 0.5, "plancher": 0.005, "valeur_initiale_moteur": 0.02}]
    ref = ReferenceAssures({"comportement": {"reference": "dynamique", "moteur": "composite", "niveau_initial": 0.0, "composantes": comps}})
    assert ref.taux(_Courbe(0.03, 0.02)) == pytest.approx(0.6 * 0.0263 + 0.4 * 0.017)
    assert ref.taux(_Courbe(0.05, -0.02)) == pytest.approx(0.6 * (0.0263 + 0.5 * 0.02) + 0.4 * 0.005)  # lissage, plancher


def test_reference_composite_niveau_initial_et_independant_de_la_base():
    for base in bases.BASES:
        h = cv.appliquer(hypotheses_profil("B"), "composite_observe", base)
        assert h["comportement"]["niveau_initial"] == pytest.approx(0.6 * 0.0263 + 0.25 * 0.017 + 0.15 * cv.taux_obligations_10_ans_initial())
        eco, cr = bases.equivalent_certain(h, base, spread_obligations())
        assert projeter(h, eco, credit=cr).loc[1, "taux_10ans"] == pytest.approx(h["comportement"]["niveau_initial"], abs=1e-14)


def test_rachat_structurel_au_sens_de_l_acpr():
    """Rachats / PM d'ouverture = paramètre x (1 + taux servi) x (1 - décès) = 4,4 % avec le taux servi de 2025."""
    p = cv.rachat_structurel_acpr()
    assert p * (1 + 0.0263) * (1 - 0.01) == pytest.approx(0.044, abs=1e-6)  # paramètre arrondi à 10^-6
    h = cv.appliquer(hypotheses_profil("B"), "taux_servi_marche", rachat_structurel="acpr")
    eco, cr = bases.equivalent_certain(h, "sans_va", cv.credit_valorisation("k70_granulaire_correle"))
    df = projeter(h, eco, credit=cr)
    servi = df.loc[1, "taux_servi"]
    assert df.loc[1, "taux_rachat"] == pytest.approx(p)  # aucune composante dynamique en année 1
    assert df.loc[1, "rachats"] / df.loc[0, "pm"] == pytest.approx(p * (1 + servi) * (1 - 0.01), rel=1e-12)


# --- Spread hypothétique des obligations ------------------------------------------------------------

def test_spread_hypothetique_reproduit_les_ltas_publies_par_l_eiopa():
    """s(k) = ln(1 + r(k) + LTAS(k)) - ln(1 + r(k)), LTAS = moyenne des séries A financières et non financières."""
    fiche = json.loads((RACINE / "data" / "v5" / "marche" / "spread_hypothetique_20261031.json").read_text(encoding="utf-8"))
    assert fiche["statut"] == "hypothèse"
    pub, s, e = fiche["donnees_publiees"], spread_obligations(), courbe_eiopa()
    for k in range(1, 31):
        ltas = (pub["EUR_Financials_2"][str(k)] + pub["EUR_Non-Financials_2"][str(k)]) / 2
        r = e.taux_zc(k)
        assert (1 + r) * math.exp(s.s(k)) - (1 + r) == pytest.approx(ltas, abs=2e-8), k
    assert s.s(50) == pytest.approx(s.s(30))  # plat au-delà de 30 ans


def test_aucune_donnee_d_indice_de_taux_souverain_dans_les_donnees_de_marche():
    noms = sorted(f.name for f in (RACINE / "data" / "v5" / "marche").iterdir())
    assert noms == ["eiopa_rfr_20261031_eur.csv", "eiopa_rfr_20261031_provenance.json", "spread_hypothetique_20261031.json"]
    for f in (RACINE / "data" / "v5").rglob("*.json"):
        texte = f.read_text(encoding="utf-8")
        assert "TEC" not in texte and "oblig.fr" not in texte, f.name


# --- Vue prudentielle -------------------------------------------------------------------------------

def test_facteurs_de_spread_par_qualite_de_credit():
    assert facteur_spread("cqs1", 5) == pytest.approx(0.055)
    assert facteur_spread("cqs1", 10) == pytest.approx(0.085)
    assert facteur_spread("cqs2", 7) == pytest.approx(0.084)
    assert facteur_spread("cqs3", 7) == pytest.approx(0.155)
    assert facteur_spread("cqs4", 7) == pytest.approx(0.275)


def test_fonds_excedentaires_approche_simplifiee():
    c = CourbePlate(0.01)
    prest = {t: 10.0 for t in range(1, 21)}
    attendu = 80 * sum(1.01 ** (-t) for t in range(9, 21)) / 12  # entrée en PM en année 8, sorties uniformes ensuite
    assert fonds_excedentaires(80, prest, c) == pytest.approx(attendu)
    assert fonds_excedentaires(80, prest, c) < 80


def test_mcr_encadre():
    assert mcr(100, 1000, 100) == pytest.approx(0.037 * 1000 - 0.052 * 100)  # 31,8 entre 25 et 45
    assert mcr(100, 100, 0) == pytest.approx(25.0)
    assert mcr(100, 5000, 0) == pytest.approx(45.0)
    assert mcr(1.0, 0, 0) == pytest.approx(0.4)
    assert mcr(100, 100, 5000) == pytest.approx(25.0)  # linéaire négatif ramené à 0, puis plancher
    from src.v5.solvabilite_v5 import mcr_detail
    assert mcr_detail(100, 1000, 100)["contrainte_active"] == "MCR linéaire"
    assert mcr_detail(100, 100, 0)["contrainte_active"] == "plancher de 25 % du SCR"
    assert mcr_detail(100, 5000, 0)["contrainte_active"] == "plafond de 45 % du SCR"
    assert mcr_detail(1.0, 0, 0)["contrainte_active"] == "minimum absolu"
