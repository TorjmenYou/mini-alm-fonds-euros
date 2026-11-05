"""Contrôles du modèle : à lancer avec `python -m pytest` depuis la racine du dépôt."""

import pytest

from src.hypotheses import actif_initial, charger_hypotheses
from src.passif import projeter_passif_un_an, taux_rachat_conjoncturel
from src.projection import indicateurs, projeter, scenario

SCENARIOS = ["central", "hausse_taux_200pb", "baisse_taux_100pb", "krach_actions_25pc"]


@pytest.fixture(scope="module")
def h():
    return charger_hypotheses()


@pytest.fixture(scope="module")
def resultats(h):
    return {nom: projeter(h, scenario(h, nom)) for nom in SCENARIOS}


# Étape 1 : bilan initial
def test_actif_initial(h):
    a = actif_initial(h)
    assert a["total"] == pytest.approx(1090.0)
    assert a["obligations"] == pytest.approx(926.5)
    assert a["actions"] == pytest.approx(109.0)
    assert a["monetaire"] == pytest.approx(54.5)


# Étape 2 : une année de passif, taux servi 2 %, décès 1 %, rachats 5 %.
# Risques concurrents : les rachats portent sur les survivants,
# soit 1 020 x 0,99 x 0,05 = 50,49 (51,0 quand les rachats portaient sur toute la PM revalorisée).
def test_passif_un_an():
    r = projeter_passif_un_an(1000.0, 0.02, 0.01, 0.05)
    assert r["interets"] == pytest.approx(20.0)
    assert r["deces"] == pytest.approx(10.2)
    assert r["rachats"] == pytest.approx(50.49)
    assert r["pm_fin"] == pytest.approx(1020.0 * 0.99 * 0.95)


# Loi de rachats conjoncturels : un point par palier
@pytest.mark.parametrize("ecart, attendu", [
    (-0.05, 0.30), (-0.025, 0.15), (0.0, 0.0), (0.02, -0.025), (0.05, -0.05),
])
def test_paliers_rachats(h, ecart, attendu):
    assert taux_rachat_conjoncturel(ecart, h["rachats_dynamiques"]) == pytest.approx(attendu)


# Le bilan comptable reste équilibré chaque année :
# VNC de l'actif = PM + PPB + réserve de capitalisation + fonds propres
@pytest.mark.parametrize("nom", SCENARIOS)
def test_bilan_equilibre(resultats, nom):
    assert resultats[nom]["ecart_bilan"].abs().max() < 1e-8


# Test de fuite : aucune valeur ne se crée ni ne se perd dans la projection
@pytest.mark.parametrize("nom", SCENARIOS)
def test_fuite_nulle(resultats, nom):
    ind = indicateurs(resultats[nom])
    assert abs(ind["fuite"]) < 1e-6 * ind["vm_actif_initial"]


@pytest.mark.parametrize("nom", SCENARIOS)
def test_garanties_respectees(h, resultats, nom):
    df = resultats[nom].loc[1:]
    assert (df["taux_servi"] >= h["passif"]["tmg"] - 1e-12).all()
    assert (df["ppb"] >= -1e-9).all()


# Hausse des taux : rachats massifs l'année du choc et ventes d'obligations en moins-value
def test_cercle_vicieux_hausse_des_taux(resultats):
    an1 = resultats["hausse_taux_200pb"].loc[1]
    assert an1["taux_rachat"] == pytest.approx(0.20)
    assert an1["pmv_obligataires_realisees"] < 0


# --- V2 : générateur de scénarios et projection stochastique -----------------

from src.courbes import CourbeHullWhite, CourbePlate
from src.gse import GSE
from src.stochastique import projeter_stochastique, tvog


def test_courbe_hull_white_initiale(h):
    """En t = 0, la courbe Hull-White redonne la courbe initiale plate."""
    r0, g = h["economie"]["taux_sans_risque"], h["gse"]
    c = CourbeHullWhite(0, 0.0, r0, g["hw_a"], g["hw_sigma"])
    for k in (1, 5, 10, 30):
        assert c.zc(k) == pytest.approx(CourbePlate(r0).zc(k), rel=1e-12)
    assert c.taux_pair(10) == pytest.approx(r0)


# Tolérance : 3 écarts-types de l'estimateur (l'IC à 95 % vaut 1,96 écart-type)
TROIS_ECARTS_TYPES = 3 / 1.96


def test_martingale(h):
    """Zéro-coupons, obligation revendue et actions actualisés : moyenne = 1 à l'erreur de Monte-Carlo près."""
    m = GSE(h).test_martingale()
    for cle in ("zero_coupon", "obligation", "actions"):
        ecart = abs(m[cle][1:] - 1)
        assert (ecart <= TROIS_ECARTS_TYPES * m["ic_" + cle][1:] + 1e-12).all(), cle


@pytest.fixture(scope="module")
def stochastique(h):
    return projeter_stochastique(h, GSE(h, n=200))


def test_fuite_stochastique(stochastique):
    s = stochastique["synthese"]
    assert abs(s["fuite"]) <= TROIS_ECARTS_TYPES * s["ic_fuite"]


def test_bilan_equilibre_stochastique(h):
    from src.projection import projeter
    for eco in GSE(h, n=20).scenarios():
        assert projeter(h, eco)["ecart_bilan"].abs().max() < 1e-8


def test_tvog_positive(h, stochastique):
    """Les garanties et les rachats dynamiques ont un coût : BE stochastique > BE équivalent certain."""
    assert tvog(h, stochastique)["tvog"] > 0


# --- V4 : passif « à la Prophet » ---------------------------------------------

from src.prophet.epargne import construire
from src.prophet.moteur import Bibliotheque, DependanceCirculaire, Modele
from src.prophet.tables import DOSSIER, scenario_depuis_projection


@pytest.mark.parametrize("nom", ["central", "hausse_taux_200pb"])
def test_v4_reproduit_le_passif_v1(h, resultats, nom):
    """Avec un model point et des tables plates, la V4 retrouve exactement le passif de la V1."""
    df = resultats[nom]
    r = construire(scenario_depuis_projection(df, h), DOSSIER / "validation").calculer()
    assert abs(r["PM_FIN"].to_numpy() - df["pm"].to_numpy()).max() < 1e-9
    assert abs(r["PRESTATIONS"].to_numpy() - df["prestations"].to_numpy()).max() < 1e-9
    d = df["deflateur"]
    va_v1 = ((df["prestations"] + df["frais"]) * d).sum() + df["pm"].iloc[-1] * d.iloc[-1]
    assert r["VA_SORTIES"].iloc[0] == pytest.approx(va_v1, rel=1e-12)


def test_v4_detecte_une_dependance_circulaire(h, resultats):
    bib = Bibliotheque()

    @bib.variable("A", "appelle B à la même date")
    def _(m, t):
        return m("B", t)

    @bib.variable("B", "appelle A à la même date")
    def _(m, t):
        return m("A", t)

    from src.prophet.tables import charger
    mp, tables, param = charger(DOSSIER / "validation")
    m = Modele(bib, mp, tables, param, scenario_depuis_projection(resultats["central"], h))
    with pytest.raises(DependanceCirculaire):
        m("A", 1)


def courbe_pentue():
    """Courbe non plate (pentue, avec une bosse) pour tester le calage du Hull-White."""
    from src.courbes import CourbeZeroCoupon
    return CourbeZeroCoupon([0.015 + 0.002 * k - 0.00004 * k**2 for k in range(1, 31)])


def test_hull_white_cale_sur_une_courbe_quelconque(h):
    g = h["gse"]
    p0 = courbe_pentue()
    c = CourbeHullWhite(0, 0.0, p0, g["hw_a"], g["hw_sigma"])
    for k in (1, 7, 15, 30, 45):
        assert c.zc(k) == pytest.approx(p0.zc(k), rel=1e-12)


def test_martingale_sur_courbe_quelconque(h):
    m = GSE(h, courbe=courbe_pentue()).test_martingale()
    for cle in ("zero_coupon", "obligation", "actions"):
        assert (abs(m[cle][1:] - 1) <= TROIS_ECARTS_TYPES * m["ic_" + cle][1:] + 1e-12).all(), cle
