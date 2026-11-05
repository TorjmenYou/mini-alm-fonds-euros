"""Calculs Solvabilité II simplifiés (V3) : chocs, agrégation, absorption, marge de risque."""

import copy
import math

import pytest

from src.courbes import CourbeZeroCoupon
from src.solvabilite import (agreger, ajustement_absorption, assembler_scr, calculer_scr, courbes_choquees,
                             facteur_choc, marge_de_risque)


@pytest.fixture(scope="module")
def chocs(h):
    return h["solvabilite2"]["choc_taux"]


@pytest.mark.parametrize("m, s_up, s_down", [(0.5, 0.70, 0.75), (1, 0.70, 0.75), (10, 0.42, 0.31),
                                             (20, 0.26, 0.29), (55, 0.23, 0.245), (90, 0.20, 0.20), (120, 0.20, 0.20)])
def test_facteurs_de_choc_et_interpolation(chocs, m, s_up, s_down):
    assert facteur_choc(m, chocs["maturites"], chocs["s_hausse"]) == pytest.approx(s_up)
    assert facteur_choc(m, chocs["maturites"], chocs["s_baisse"]) == pytest.approx(s_down)


def test_courbes_choquees(chocs):
    up, down = courbes_choquees(CourbeZeroCoupon.plate(0.03), chocs)
    assert up.taux_maturite(1) == pytest.approx(0.03 * 1.70)
    assert up.taux_maturite(10) == pytest.approx(0.03 * 1.42)
    assert up.taux_maturite(30) == pytest.approx(0.04)  # plancher : hausse d'au moins 1 point
    assert down.taux_maturite(10) == pytest.approx(0.03 * (1 - 0.31))
    # Un taux négatif n'est pas choqué à la baisse
    _, down_neg = courbes_choquees(CourbeZeroCoupon.plate(-0.005), chocs)
    assert down_neg.taux_maturite(5) == pytest.approx(-0.005)


def test_agregation():
    marche, bscr = agreger(3.0, 4.0, 0.0, 0.0, 0.25)
    assert marche == pytest.approx(5.0) and bscr == pytest.approx(5.0)
    marche, bscr = agreger(3.0, 4.0, 12.0, 0.5, 0.25)
    assert marche == pytest.approx(math.sqrt(9 + 16 + 12))
    assert bscr == pytest.approx(math.sqrt(marche**2 + 144 + 0.5 * marche * 12))


def test_marge_de_risque_regimes():
    courbe = CourbeZeroCoupon.plate(0.0)
    scr = [10.0] * 30
    assert marge_de_risque(scr, courbe, {"cout_du_capital": 0.06, "lambda": None, "plancher_lambda": None}) == pytest.approx(18.0)
    attendu = 0.0475 * sum(max(0.96**t, 0.5) * 10.0 for t in range(30))
    assert marge_de_risque(scr, courbe, {"cout_du_capital": 0.0475, "lambda": 0.96, "plancher_lambda": 0.5}) == pytest.approx(attendu)


# --- Pertes brutes, capacité d'absorption (art. 206) : chiffres calculés à la main ---

S2_CORR = {"correlation_taux_actions_baisse": 0.5, "correlation_marche_vie": 0.25}
FP_CHOQUES = {"base": 100.0, "taux_hausse": 90.0, "taux_baisse": 95.0, "actions": 80.0,
              "rachats_hausse": 92.0, "rachats_baisse": 105.0, "rachat_massif": 88.0}
# Pertes nettes : taux_hausse 10, taux_baisse 5, actions 20, rachats_hausse 8, rachats_baisse -5, rachat_massif 12


def fdb_choquees(base, baisses):
    return {"base": base} | {nom: base - b for nom, b in baisses.items()}


def test_ajustement_absorption_article_206():
    assert ajustement_absorption(100.0, 60.0, 30.0) == -30.0   # plafonné par les FDB
    assert ajustement_absorption(100.0, 60.0, 50.0) == -40.0   # BSCR - nBSCR
    assert ajustement_absorption(50.0, 60.0, 30.0) == 0.0      # jamais positif


def test_brut_pris_sur_le_scenario_retenu_en_net():
    """Le brut préférerait la baisse des taux et la hausse des rachats ; le net retient
    la hausse des taux et le rachat massif. Le brut doit suivre le net (art. 165(2), 142(7))."""
    fdb = fdb_choquees(50.0, {"taux_hausse": 5, "taux_baisse": 20, "actions": 15,
                              "rachats_hausse": 20, "rachats_baisse": -10, "rachat_massif": 6})
    r = assembler_scr(FP_CHOQUES, fdb, S2_CORR)
    assert r["sens_retenus"] == {"taux": "taux_hausse", "rachat": "rachat_massif"}
    assert r["pertes_brutes"]["taux_baisse"] == pytest.approx(25.0)      # plus forte que la hausse (15)...
    assert r["scr_brut"]["taux"] == pytest.approx(15.0)                  # ... mais c'est la hausse qui est prise
    assert r["scr_brut"]["rachat"] == pytest.approx(18.0)                # massif (18), pas la hausse (28)
    # Net : taux 10, actions 20, rachat 12, A = 0
    marche_net = math.sqrt(10**2 + 20**2)
    nbscr = math.sqrt(marche_net**2 + 12**2 + 2 * 0.25 * marche_net * 12)
    # Brut : taux 15, actions 35, rachat 18, A = 0
    marche_brut = math.sqrt(15**2 + 35**2)
    bscr = math.sqrt(marche_brut**2 + 18**2 + 2 * 0.25 * marche_brut * 18)
    assert r["scr_net"]["bscr"] == pytest.approx(nbscr) and r["scr_brut"]["bscr"] == pytest.approx(bscr)
    assert r["ajustement_tp"] == pytest.approx(-(bscr - nbscr))          # 18,1 < FDB de 50
    assert r["scr"] == pytest.approx(nbscr) and not r["plafond_fdb_atteint"]


def test_plafond_des_fdb_atteint():
    fdb = fdb_choquees(12.0, {"taux_hausse": 5, "taux_baisse": 12, "actions": 12,
                              "rachats_hausse": 12, "rachats_baisse": -10, "rachat_massif": 6})
    r = assembler_scr(FP_CHOQUES, fdb, S2_CORR)
    marche_brut = math.sqrt(15**2 + 32**2)
    bscr = math.sqrt(marche_brut**2 + 18**2 + 2 * 0.25 * marche_brut * 18)
    assert r["scr_brut"]["bscr"] == pytest.approx(bscr)
    assert r["plafond_fdb_atteint"] and r["ajustement_tp"] == pytest.approx(-12.0)
    assert r["scr"] == pytest.approx(bscr - 12.0)


def test_correlation_a_quand_la_baisse_des_taux_est_retenue():
    fp = FP_CHOQUES | {"taux_hausse": 97.0, "taux_baisse": 94.0}   # pertes nettes 3 et 6
    r = assembler_scr(fp, fdb_choquees(50.0, {nom: 0.0 for nom in fp if nom != "base"}), S2_CORR)
    assert r["sens_retenus"]["taux"] == "taux_baisse"
    assert r["scr_net"]["marche"] == pytest.approx(math.sqrt(6**2 + 20**2 + 2 * 0.5 * 6 * 20))
    # FDB inchangées dans tous les scénarios : brut = net, aucun ajustement
    assert r["scr_brut"]["bscr"] == pytest.approx(r["scr_net"]["bscr"]) and r["ajustement_tp"] == 0.0


@pytest.fixture(scope="module")
def sans_participation(h):
    """Fonds sans aucune prestation discrétionnaire : pas de participation, pas de
    PPB, pas d'abandon de marge, TMG nul. Le taux servi est toujours égal au TMG,
    donc les FDB sont nulles par construction dans tous les scénarios."""
    hz = copy.deepcopy(h)
    hz["strategie"]["participation_minimale"] = 0.0
    hz["strategie"]["abandon_marge_assureur"] = False
    hz["bilan_initial"]["ppb"] = 0.0
    hz["passif"]["tmg"] = 0.0
    return calculer_scr(hz, n=20)


def test_fdb_nulles_brut_egal_net(sans_participation):
    r = sans_participation
    for nom, v in r["fdb"].items():
        assert abs(v) < 1e-9, nom
    for nom in r["pertes_nettes"]:
        assert r["pertes_brutes"][nom] == pytest.approx(r["pertes_nettes"][nom], abs=1e-9)
    assert r["ajustement_tp"] == 0.0
    assert r["scr"] == pytest.approx(r["scr_net"]["bscr"]) == pytest.approx(r["scr_brut"]["bscr"])


def test_sensibilite_2027_ne_change_que_la_marge_de_risque(sans_participation):
    b = sans_participation["bilans"]
    actuel, sensi = b["regles_2026"], b["sensibilite_mr_2027"]
    assert sensi["be"] == actuel["be"] and sensi["scr"] == actuel["scr"]
    assert sensi["fonds_propres"] - actuel["fonds_propres"] == pytest.approx(actuel["marge_risque"] - sensi["marge_risque"])
    assert "Sensibilité" in sensi["libelle"] and "inchangés" in sensi["libelle"]


@pytest.mark.lent
def test_calcul_complet(h):
    r = calculer_scr(h, n=200)
    # Absorption : |Adj| <= FDB, SCR = BSCR + Adj, SCR = nBSCR quand le plafond n'est pas atteint
    assert -r["ajustement_tp"] <= r["fdb"]["base"] + 1e-9
    assert r["scr"] == pytest.approx(r["scr_brut"]["bscr"] + r["ajustement_tp"])
    if not r["controles"]["ajustement_plafonne_par_fdb"]:
        assert r["scr"] == pytest.approx(r["scr_net"]["bscr"])
    assert r["controles"]["fdb_negatives"] == []
    # Perte brute recalculée directement, scénario par scénario : variation de
    # l'actif moins variation de la part non discrétionnaire du BE (BE - FDB)
    base = r["runs"]["base"]
    for nom, perte in r["pertes_brutes"].items():
        choc = r["runs"][nom]
        hors_fdb = lambda run: (run["par_scenario"]["be"] - run["par_scenario"]["fdb"]).mean()
        directe = (base["synthese"]["vm_actif_initial"] - choc["synthese"]["vm_actif_initial"]) \
            - (hors_fdb(base) - hors_fdb(choc))
        assert perte == pytest.approx(directe, abs=1e-9), nom
        assert r["ic_pertes_brutes"][nom] > 0
    # La sensibilité aux paramètres de marge de risque 2027 donne une marge plus faible
    assert r["marges_de_risque"]["sensibilite_mr_2027"] < r["marges_de_risque"]["regles_2026"]
    for b in r["bilans"].values():
        assert b["fonds_propres"] == pytest.approx(b["actif"] - b["be"] - b["marge_risque"])
