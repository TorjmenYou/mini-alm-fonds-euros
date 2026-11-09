"""V5 : collecte nouvelle sensible au taux servi relatif (docs/V5_SPECIFICATION_COLLECTE.md).

Deux cas limites distincts, testés séparément : c0 = 0 redonne exactement le portefeuille fermé ;
eta = 0 avec c0 > 0 donne une collecte positive mais indépendante du taux servi relatif. Puis : contrôle
de comptabilisation sur un cas cantonné (valeur nulle par construction), contrat sans marge explicite dans
le fonds mutualisé (valeur presque nulle, résidu borné et expliqué par une variante de liquidation), absence d'arbitrage des primes investies au prix du
marché, identité de la décomposition, frontière des contrats de la vue prudentielle, séparation des deux
ensembles de contrats et respect de leurs garanties.
"""

import numpy as np
import pytest

from src.passif import reaction_collecte, repartir_taux_servi
from src.projection import indicateurs, projeter
from src.v5 import bases, collecte as col, conventions as cv, strategies as stg
from src.v5.courbes_marche import courbe_eiopa
from src.v5.profils import hypotheses_profil
from src.v5.scenarios import ScenarioCourbe

CREDIT = "k70_granulaire_correle"
COLONNES_COLLECTE = ("primes", "pm_nouveaux", "prestations_nouveaux", "frais_nouveaux")


def h_profil(p="B", code="passive", apport=0.0):
    h = cv.appliquer(hypotheses_profil(p), "taux_servi_marche", "sans_va", rachat_structurel="acpr")
    return stg.appliquer_strategie(h, code, apport)


def ec(h):
    return projeter(h, ScenarioCourbe("ec", h["horizon_annees"], courbe_eiopa()), credit=cv.credit_valorisation(CREDIT))


def scenarios_stochastiques(h, n=8):
    g, cr = bases.gse(h, "sans_va", cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=n)
    return g.scenarios(), cr


# --- Fonctions élémentaires ------------------------------------------------------------------------

def test_reaction_de_la_collecte():
    c = {"eta": 0.5, "e0": 0.0, "zone_neutre": 0.0, "g_min": 0.0, "g_max": 2.0}
    assert reaction_collecte(0.0, c) == 1.0
    assert reaction_collecte(-0.01, c) == pytest.approx(0.5)  # un point sous la référence : moitié moins
    assert reaction_collecte(-0.05, c) == 0.0  # plancher g_min
    assert reaction_collecte(0.05, c) == 2.0  # plafond g_max
    assert reaction_collecte(-0.03, dict(c, eta=0.0)) == 1.0  # eta = 0 : indépendante de l'écart
    z = dict(c, zone_neutre=0.005)
    assert reaction_collecte(-0.004, z) == 1.0
    assert reaction_collecte(-0.015, z) == pytest.approx(0.5)  # pente mesurée depuis le bord de la zone


def test_repartition_du_taux_servi_entre_garanties():
    ens = [(600.0, 0.006), (400.0, 0.0)]
    # Taux moyen au-dessus des deux TMG : même taux pour tous
    x, (a, b) = repartir_taux_servi(0.02 * 1000.0, ens)
    assert x == pytest.approx(0.02) and a == pytest.approx(0.02) and b == pytest.approx(0.02)
    # Taux moyen entre les deux TMG : l'existant reçoit son TMG, les nouveaux le reste
    x, (a, b) = repartir_taux_servi(0.005 * 1000.0, ens)
    assert a == pytest.approx(0.006) and b == pytest.approx((5.0 - 600.0 * 0.006) / 400.0)
    assert 600.0 * a + 400.0 * b == pytest.approx(5.0)
    assert b >= 0.0
    # Intérêt inférieur à la somme des garanties : aucune répartition ne le conserve, erreur explicite
    with pytest.raises(ValueError):
        repartir_taux_servi(3.0, ens)


# --- Cas limites : deux tests de non-régression indépendants --------------------------------------

@pytest.mark.parametrize("p,code,eta", [("A", "passive", 0.0), ("B", "taux_servi_marge", 0.5), ("C", "taux_servi_competitif", 1.5)])
def test_c0_nul_redonne_exactement_le_portefeuille_ferme(p, code, eta):
    """c0 = 0 : aucune collecte, pour trois élasticités. Toutes les colonnes du modèle sans collecte
    sont identiques, à l'équivalent certain et sur des scénarios stochastiques avec défauts."""
    h = h_profil(p, code, 20.0)
    hc = col.appliquer_collecte(h, 0.0, eta)
    paires = [(ec(h), ec(hc))]
    scen, cr = scenarios_stochastiques(h, n=4)
    scen_c, cr_c = scenarios_stochastiques(hc, n=4)
    for j in range(len(scen)):
        paires.append((projeter(h, scen[j], credit=cr.pour_scenario(j, len(scen))),
                       projeter(hc, scen_c[j], credit=cr_c.pour_scenario(j, len(scen_c)))))
    for d0, d1 in paires:
        assert (d0[d0.columns] - d1[d0.columns]).abs().max().max() == 0.0
        for c in COLONNES_COLLECTE:
            assert (d1[c] == 0.0).all(), c
        assert indicateurs(d1)["valeur_assureur"] == indicateurs(d0)["valeur_assureur"]
        assert indicateurs(d1)["be_existant"] == indicateurs(d0)["be"]


def test_eta_nul_collecte_positive_independante_du_taux_servi():
    """eta = 0 et c0 > 0 : C(t) = c0 x PM(t - 1) exactement pendant l'horizon de collecte, puis 0, pour
    deux politiques de taux servi différentes ; avec eta > 0, la politique qui sert moins collecte moins."""
    c0 = 0.06
    H = col.charger()["horizon_collecte_ans"]["valeur"]
    df = {code: ec(col.appliquer_collecte(h_profil("B", code), c0, 0.0)) for code in ("passive", "taux_servi_marge")}
    for code, d in df.items():
        assert (d.loc[1:H, "facteur_collecte"] == 1.0).all(), code
        assert np.allclose(d.loc[1:H, "primes"].to_numpy(), c0 * d.loc[0:H - 1, "pm"].to_numpy(), rtol=1e-14, atol=0), code
        assert (d.loc[H + 1:, "primes"] == 0.0).all(), code
        assert (d.loc[1:H, "primes"] > 0).all(), code
    # Les taux servis diffèrent (la politique de marge sert moins en moyenne), la collecte rapportée à la PM non
    assert df["taux_servi_marge"].loc[1:H, "taux_servi"].mean() < df["passive"].loc[1:H, "taux_servi"].mean()
    assert not np.allclose(df["taux_servi_marge"].loc[1:H, "taux_servi"], df["passive"].loc[1:H, "taux_servi"])
    sensible = {code: ec(col.appliquer_collecte(h_profil("B", code), c0, 0.5)) for code in ("passive", "taux_servi_marge")}
    ratio = {code: (d.loc[2:H, "primes"] / d.loc[1:H - 1, "pm"].to_numpy()).mean() for code, d in sensible.items()}
    assert ratio["taux_servi_marge"] < ratio["passive"] < c0


# --- Absence d'arbitrage ---------------------------------------------------------------------------

def test_cas_cantonne_controle_de_comptabilisation():
    """Contrats nouveaux crédités au taux sans risque du scénario, sans chargement, frais, garantie ni
    option, cantonnés sur un compte séparé : leur valeur est nulle par construction (le compte croît au
    taux des déflateurs). Le test contrôle la comptabilisation des primes, des prestations, de la PM finale
    et de l'actualisation, scénario par scénario, et que l'existant reste identique ; il n'exerce pas le
    fonds mutualisé (voir le test suivant)."""
    h = h_profil("B", "passive", 20.0)
    hn = col.appliquer_collecte(h, 0.10, 0.5, mode="cantonne_sans_risque", frais_acquisition_prime=0.0, chargement_prime=0.0)
    scen, cr = scenarios_stochastiques(h, n=6)
    scen_n, cr_n = scenarios_stochastiques(hn, n=6)
    for j in range(len(scen)):
        d0 = projeter(h, scen[j], credit=cr.pour_scenario(j, len(scen)))
        dn = projeter(hn, scen_n[j], credit=cr_n.pour_scenario(j, len(scen_n)))
        i0, i_n = indicateurs(d0), indicateurs(dn)
        assert i_n["va_primes"] > 10.0
        assert abs(i_n["va_primes_moins_be_nouveaux"]) < 1e-9 * i_n["va_primes"], j
        assert i_n["be_existant"] == i0["be"], j
        assert i_n["valeur_assureur"] == pytest.approx(i0["valeur_assureur"], abs=1e-9 * i_n["va_primes"]), j
        assert (d0[d0.columns] - dn[d0.columns]).abs().max().max() == 0.0
    with pytest.raises(ValueError):  # le mode cantonné n'applique ni chargement ni frais : il les refuse
        ec(col.appliquer_collecte(h, 0.10, 0.5, mode="cantonne_sans_risque"))


@pytest.mark.parametrize("p", ["A", "B", "C"])
def test_contrat_sans_marge_explicite_dans_le_fonds_mutualise_presque_neutre(p):
    """Contrat sans marge explicite : fonds mutualisé, équivalent certain, sans chargement, frais, frais
    d'acquisition, TMG ni PPB, avec une participation de 100 %. La valeur des affaires nouvelles (avant
    impôt) est presque nulle, alors que celle des contrats réalistes atteint plusieurs % de la VA des primes.
    Le résidu, borné ici à 1 % de la VA des primes, vient des conventions de partage et de liquidation
    (réserve de capitalisation, revenus de la quote-part des fonds propres retenus, plus-values latentes
    finales). Les deux termes de la décomposition, eux, ne sont pas neutres : un transfert entre
    générations d'assurés, qui croît avec les moins-values latentes d'ouverture, les déplace en sens
    inverse (chacun dépasse le résidu de leur somme) ; seule leur somme s'interprète.

    Variante de liquidation (réserve d'ouverture reclassée en fonds propres, fonds propres comptables
    positifs distribués chaque année) : le résidu disparaît pour B et C ; pour A, il est fait de pertes
    évitées à l'actionnaire. En extinction, A réalise des moins-values ; reportées sur l'exercice suivant,
    elles rendent certains résultats financiers négatifs et, la participation ne pouvant être négative,
    l'actionnaire les porte (par des apports, ou par des fonds propres comptables négatifs en fin de
    projection, selon le calibrage). La collecte finance les sorties et évite ces ventes."""
    h = h_profil(p)
    h["strategie"].update(participation_minimale=1.0, plafond_ppb_pct_pm=0.0)
    h["passif"].update(chargements_encours=0.0, frais_gestion_encours=0.0, tmg=0.0)
    i0 = indicateurs(ec(h))
    i1 = indicateurs(ec(col.appliquer_collecte(h, 0.06, 0.0, frais_acquisition_prime=0.0, chargement_prime=0.0)))
    van = i1["valeur_assureur"] - i0["valeur_assureur"]
    assert abs(van) < 0.01 * i1["va_primes"]
    assert i1["va_primes_moins_be_nouveaux"] > abs(van)  # les termes pris seuls ne sont pas neutres
    realiste = col.appliquer_collecte(h_profil(p), 0.06, 0.0)
    i2, i20 = indicateurs(ec(realiste)), indicateurs(ec(h_profil(p)))
    assert i2["valeur_assureur"] - i20["valeur_assureur"] > 0.05 * i2["va_primes"]

    b = h["bilan_initial"]
    b["fonds_propres"], b["reserve_capitalisation"] = b["fonds_propres"] + b["reserve_capitalisation"], 0.0
    h["strategie_alm"]["distribution"]["fonds_propres_pct_pm"] = 0.0
    d0, d1 = ec(h), ec(col.appliquer_collecte(h, 0.06, 0.0, frais_acquisition_prime=0.0, chargement_prime=0.0))
    i0, i1 = indicateurs(d0), indicateurs(d1)
    van = i1["valeur_assureur"] - i0["valeur_assureur"]
    apports = lambda d: float((d["apport_assureur"] * d["deflateur"]).sum())  # noqa: E731
    fp_final = lambda d: float(d["fonds_propres"].iloc[-1] * d["deflateur"].iloc[-1])  # noqa: E731
    if p == "A":
        assert van > 0.001 * i1["va_primes"]
        assert d0["pmv_obligataires_realisees"].sum() < -10 * van and d1["pmv_obligataires_realisees"].sum() > -1e-9
        assert (apports(d0) - apports(d1)) + (fp_final(d1) - fp_final(d0)) > 0.9 * van
    else:
        assert abs(van) < 0.001 * i1["va_primes"]


@pytest.mark.parametrize("p,code", [("A", "passive"), ("B", "taux_servi_marge"), ("C", "liquidite_defensive")])
def test_primes_investies_au_prix_du_marche_sans_fuite(p, code):
    """Fonds mutualisé, contrats réalistes : sur l'équivalent certain, actif initial + VA des primes =
    VA des sorties + VA de l'actif final (fuite nulle), bilan équilibré chaque année."""
    for c0, eta in ((0.06, 0.0), (0.10, 1.5)):
        d = ec(col.appliquer_collecte(h_profil(p, code, 20.0), c0, eta))
        i = indicateurs(d)
        assert i["va_primes"] > 0
        assert abs(i["fuite"]) < 1e-8, (c0, eta)
        assert d["ecart_bilan"].abs().max() < 1e-8, (c0, eta)


def test_contrats_realistes_valeur_mesuree_et_sensible_aux_marges():
    """La valeur propre des contrats réalistes n'est pas contrainte : elle baisse avec les frais
    d'acquisition, monte avec un chargement sur prime, de l'écart attendu à l'équivalent certain."""
    h = h_profil("B")
    v = {k: indicateurs(ec(col.appliquer_collecte(h, 0.06, 0.0, **kw)))
         for k, kw in {"centre": {}, "sans_frais": {"frais_acquisition_prime": 0.0}, "chargement": {"chargement_prime": 0.02}}.items()}
    va = v["centre"]["va_primes"]
    cle = "va_primes_moins_be_nouveaux"
    assert v["sans_frais"][cle] == pytest.approx(v["centre"][cle] + 0.01 * va, rel=0.05)
    assert v["chargement"][cle] > v["centre"][cle]


# --- Décomposition, cohortes et frontière des contrats ---------------------------------------------

def test_identite_de_la_decomposition_de_la_valeur_des_affaires_nouvelles():
    """L'identité tient par construction (BE de l'existant = BE total - BE des contrats nouveaux) : le test
    vérifie l'arithmétique et le branchement des projections, pas un résultat économique."""
    h = h_profil("A", "taux_servi_marge", 20.0)
    ferme = col.projection_risque_neutre(h, cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=8)
    avec = col.projection_risque_neutre(col.appliquer_collecte(h, 0.06, 0.5), cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"]), n=8)
    d = col.decomposer(avec, ferme)  # lève une erreur si l'identité n'est pas exacte
    assert np.allclose(d["valeur_affaires_nouvelles"], d["flux_contrats_nouveaux"] + d["variation_be_existant"] + d["impot_supplementaire"], atol=1e-9)
    assert (avec["va_primes"] > 0).all()


def test_ensembles_de_contrats_separes_et_garanties_respectees():
    h = h_profil("A", "passive", 20.0)  # TMG de l'existant : 0,6 %
    hc = col.appliquer_collecte(h, 0.06, 0.5)
    scen, cr = scenarios_stochastiques(hc, n=6)
    for j in range(len(scen)):
        d = projeter(hc, scen[j], credit=cr.pour_scenario(j, len(scen)))
        assert np.allclose(d["pm"], d["pm_existant"] + d["pm_nouveaux"], rtol=1e-12, atol=1e-9)
        assert (d.loc[1:, "taux_servi_existant"] >= h["passif"]["tmg"] - 1e-12).all()
        assert (d.loc[1:, "taux_servi_nouveaux"] >= 0.0 - 1e-12).all()
        assert (d["prestations_nouveaux"] <= d["prestations"] + 1e-9).all()
        assert d["ecart_bilan"].abs().max() < 1e-8


def test_vue_prudentielle_dans_la_frontiere_des_contrats():
    """La vue prudentielle porte sur l'existant en extinction : une section de collecte est ignorée."""
    from src.v5.solvabilite_v5 import bilan_prudentiel
    h = h_profil("C", "passive", 10.0)
    h["comportement"] = cv.comportement("taux_servi_marche", "avec_va")
    sans = bilan_prudentiel(h, CREDIT, "avec_va", n=8)
    avec = bilan_prudentiel(col.appliquer_collecte(h, 0.10, 1.5), CREDIT, "avec_va", n=8)
    for k in ("be", "scr", "mcr", "fonds_propres_niveau_1", "indicateur_couverture_scr"):
        assert avec[k] == sans[k], k


def test_repartition_quand_le_plancher_de_tmg_du_fonds_est_juste_atteint():
    """Non-régression (correction du 06/11/2026) : profil A (TMG de 0,6 %), politique de marge, collecte
    forte et loi de rachat ONC maximale, cas où le plancher de TMG du fonds est atteint exactement.
    L'intérêt réparti doit rester conservé (bilan équilibré) et les contrats nouveaux ne jamais être
    crédités sous leur garantie ; une ancienne version les créditait au taux moyen, au-delà de l'intérêt
    décidé."""
    from src.v5.profils import hypotheses_profil as hp
    h = cv.appliquer(hp("A"), "taux_servi_marche", "sans_va", rachat_structurel="acpr", loi_rachat="onc_max")
    hc = col.appliquer_collecte(stg.appliquer_strategie(h, "taux_servi_marge", 118.6), 0.10, 1.5)
    scen, cr = scenarios_stochastiques(hc, n=20)
    plancher_atteint = 0
    for j in range(len(scen)):
        d = projeter(hc, scen[j], credit=cr.pour_scenario(j, len(scen)))
        assert d["ecart_bilan"].abs().max() < 1e-7, j
        assert (d.loc[1:, "taux_servi_nouveaux"] >= -1e-12).all(), j
        plancher_atteint += int(((d.loc[2:, "taux_servi_nouveaux"].abs() < 1e-12) & (d.loc[2:, "pm_nouveaux"] > 0)).sum())
    assert plancher_atteint > 0  # le cas limite est bien exercé
    x, (a, b) = repartir_taux_servi(3.6 * (1 - 1e-15), [(600.0, 0.006), (400.0, 0.0)])
    assert a == pytest.approx(0.006) and b == 0.0


def test_lecture_des_ecarts_significativite_importance_robustesse():
    """Critères de lecture : robuste seulement si la borne dépasse le seuil partout ; un écart de signe
    contraire non significatif ne suffit pas à établir un changement de signe."""
    e = lambda m, h: {"moyenne": m, "demi_intervalle_95": h}  # noqa: E731
    assert col.robustesse([e(5, 1), e(4, 1)], 2) == "favorable, robuste"
    assert col.robustesse([e(-5, 1), e(-4, 1)], 2) == "défavorable, robuste"
    assert col.robustesse([e(5, 1), e(2.5, 1)], 2) == "toujours positif, non robuste"
    assert col.robustesse([e(1, 0.1), e(-1, 0.1)], 2) == "sans effet important"
    assert col.robustesse([e(1, 3.0), e(1.5, 0.2)], 2) == "toujours positif, non robuste"  # moyenne faible mais imprécise
    assert col.robustesse([e(3, 4), e(-3, 4)], 2) == "non concluant (aucun écart significatif, signes mêlés)"
    assert col.robustesse([e(5, 1), e(-1.6, 2.6)], 2) == "positif là où il est significatif, non robuste"
    assert col.robustesse([e(-5, 1), e(1.0, 3.0)], 2) == "négatif là où il est significatif, non robuste"
    assert col.robustesse([e(5, 1), e(-3, 1)], 2) == "change de signe selon les hypothèses"
    assert col.etat_majorant(e(-2, 1)) == "oui" and col.etat_majorant(e(2, 1)) == "non" and col.etat_majorant(e(0.5, 1)) == "indéterminé"
