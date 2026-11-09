"""V5.1, audit des conventions : composante technique du compte de participation (convention de référence
de la V5.1) et impôt payé dans la projection (variante facultative), src/v5/variantes_audit.py.
La variante « pb_financiere_seule » reproduit la convention de la V5.0."""

import numpy as np
import pandas as pd
import pytest

from src.projection import indicateurs, projeter
from src.strategie import decider_taux_servi, participation_technique
from src.v5 import collecte as col, conventions as cv, strategies as stg
from src.v5.courbes_marche import courbe_eiopa
from src.v5.fiscalite import impot_annuel
from src.v5.profils import hypotheses_profil
from src.v5.scenarios import ScenarioCourbe
from src.v5.variantes_audit import PART_ASSUREUR_SOLDE_TECHNIQUE, appliquer_variante

CREDIT = "k70_granulaire_correle"


def h_profil(p="B", code="passive", apport=0.0):
    h = cv.appliquer(hypotheses_profil(p), "taux_servi_marche", rachat_structurel="acpr")
    return stg.appliquer_strategie(h, code, apport)


def ec(h):
    df = projeter(h, ScenarioCourbe("ec", h["horizon_annees"], courbe_eiopa()), credit=cv.credit_valorisation(CREDIT))
    return df, indicateurs(df)


# --- Participation technique -------------------------------------------------------------------------

def test_participation_technique_part_assureur_et_solde_debiteur():
    assert participation_technique(10.0, 0.0, 0.10) == pytest.approx(9.0)  # solde créditeur : 90 % au compte
    assert participation_technique(-4.0, 0.0, 0.10) == pytest.approx(-4.0)  # solde débiteur : en totalité
    assert participation_technique(10.0, 3.0, 0.10) == pytest.approx(6.0)  # report du solde débiteur antérieur
    assert PART_ASSUREUR_SOLDE_TECHNIQUE == 0.10


class _PPB:
    def __init__(self, stock):
        self.generations = [stock / 8] * 8

    @property
    def stock(self):
        return sum(self.generations)

    def reprise_obligatoire(self):
        return self.generations[0]


def test_contribution_nulle_ou_absente_meme_decision():
    h = h_profil("B")
    for pf in (10.0, 30.0, 60.0, -5.0):
        a = decider_taux_servi(pf, 1000.0, _PPB(40.0), 5.0, 0.03, h, 0.9)
        b = decider_taux_servi(pf, 1000.0, _PPB(40.0), 5.0, 0.03, h, 0.9, 0.0)
        assert b["complement_reglementaire"] == 0.0, pf  # la règle financière seule est déjà respectée
        a.pop("pb_minimale"), b.pop("pb_minimale")  # compte : plus-values réalisées comprises
        assert a == b, pf


def _participation_de_l_exercice(s):
    """Intérêts crédités (TMG compris) + dotation à la PPB - reprises de PPB (participations antérieures)."""
    return s["interets_bruts"] - s["reprise_ppb"] + s["dotation_ppb"]


def test_plancher_atteint_la_participation_technique_va_a_la_ppb():
    """Plancher financier supérieur au besoin : la composante technique (90 % du solde créditeur) va en
    totalité aux assurés, ici en dotation à la PPB (taux cible déjà atteint, PPB sous son plafond)."""
    h = h_profil("B")
    pm, tr = 1000.0, 2.3
    a = decider_taux_servi(60.0, pm, _PPB(10.0), 0.0, 0.0, h, 0.9)
    b = decider_taux_servi(60.0, pm, _PPB(10.0), 0.0, 0.0, h, 0.9, participation_technique(tr, 0.0, 0.10))
    assert a["abandon_marge"] == 0.0 and a["dotation_ppb"] > 0  # branche du plancher suffisant
    assert _participation_de_l_exercice(b) - _participation_de_l_exercice(a) == pytest.approx(0.9 * tr, rel=1e-12)
    assert b["dotation_ppb"] - a["dotation_ppb"] == pytest.approx(0.9 * tr, rel=1e-12)
    assert b["interets_bruts"] == pytest.approx(a["interets_bruts"], rel=1e-12)
    assert b["pb_minimale"] - a["pb_minimale"] == pytest.approx(0.9 * tr, rel=1e-12)
    assert b["complement_reglementaire"] == pytest.approx(0.9 * tr, rel=1e-12)


def test_besoin_couvert_par_reprise_la_participation_technique_la_remplace():
    """Plancher insuffisant, besoin couvert par une reprise volontaire de PPB : à intérêts crédités égaux,
    la participation de l'exercice remplace une partie de la reprise (la PPB reste aux assurés)."""
    h = h_profil("B")
    a = decider_taux_servi(22.0, 1000.0, _PPB(60.0), 0.0, 0.03, h, 0.9)
    b = decider_taux_servi(22.0, 1000.0, _PPB(60.0), 0.0, 0.03, h, 0.9, participation_technique(2.3, 0.0, 0.10))
    assert a["reprise_ppb"] > 7.5 and a["abandon_marge"] == 0.0  # reprise au-delà de l'obligatoire (60 / 8)
    assert b["interets_bruts"] == pytest.approx(a["interets_bruts"], rel=1e-12)
    assert b["reprise_ppb"] == pytest.approx(a["reprise_ppb"] - 0.9 * 2.3, rel=1e-12)


def test_marge_abandonnee_couvre_deja_la_composante_technique():
    """Besoin non couvert, l'assureur abandonne sa marge financière (2,7) : la participation de l'exercice
    dépasse déjà le compte (85 % des produits + 90 % du solde technique), aucun complément."""
    h = h_profil("B")
    a = decider_taux_servi(20.0, 1000.0, _PPB(60.0), 0.0, 0.04, h, 0.9)
    b = decider_taux_servi(20.0, 1000.0, _PPB(60.0), 0.0, 0.04, h, 0.9, participation_technique(2.3, 0.0, 0.10))
    assert a["taux_servi"] < a["taux_cible"] and a["abandon_marge"] > 0.9 * 2.3
    assert b["complement_reglementaire"] == 0.0
    for k in ("interets_bruts", "reprise_ppb", "dotation_ppb", "abandon_marge"):
        assert b[k] == a[k], k


def test_marge_abandonnee_insuffisante_complement_vers_le_taux_cible():
    """Produits financiers faibles : la marge abandonnée (1,08) ne couvre pas 90 % du solde technique (2,07) ;
    le complément (0,99) est crédité, le taux cible n'étant pas atteint."""
    h = h_profil("B")
    a = decider_taux_servi(8.0, 1000.0, _PPB(60.0), 0.0, 0.04, h, 0.9)
    b = decider_taux_servi(8.0, 1000.0, _PPB(60.0), 0.0, 0.04, h, 0.9, participation_technique(2.3, 0.0, 0.10))
    assert a["complement_tmg"] == 0.0 and a["taux_servi"] < a["taux_cible"]
    attendu = 0.9 * 2.3 - a["abandon_marge"]
    assert b["complement_reglementaire"] == pytest.approx(attendu, rel=1e-12)
    assert b["interets_bruts"] - a["interets_bruts"] == pytest.approx(attendu, rel=1e-12)
    assert _participation_de_l_exercice(b) == pytest.approx(b["pb_minimale"], rel=1e-12)


def test_solde_debiteur_reporte():
    h = h_profil("B")
    s = decider_taux_servi(1.0, 1000.0, _PPB(60.0), 0.0, 0.0, h, 0.9, participation_technique(-5.0, 0.0, 0.10))
    assert s["pb_minimale"] == 0.0 and s["solde_debiteur"] == pytest.approx(5.0 - 0.85 * 0.9 * 1.0, rel=1e-12)
    assert s["complement_reglementaire"] == 0.0


@pytest.mark.parametrize("pf,ta", [(60.0, 0.0), (22.0, 0.03), (20.0, 0.04), (8.0, 0.04), (35.0, 0.06), (-3.0, 0.02)])
def test_participation_de_l_exercice_jamais_sous_le_compte(pf, ta):
    h = h_profil("B")
    s = decider_taux_servi(pf, 1000.0, _PPB(60.0), 4.0, ta, h, 0.9, participation_technique(2.3, 0.0, 0.10))
    assert _participation_de_l_exercice(s) >= s["pb_minimale"] - 1e-9
    assert s["reprise_ppb"] >= 60.0 / 8 - 1e-12  # la reprise obligatoire est toujours faite


@pytest.mark.parametrize("p", ["A", "B", "C"])
def test_participation_technique_bilan_equilibre_et_aucune_fuite(p):
    h = h_profil(p, apport=20.0)
    df, ind = ec(h)
    assert df["ecart_bilan"].abs().max() < 1e-8
    assert abs(ind["fuite"]) < 1e-8
    assert (df["pb_minimale"] >= 0).all() and (df["solde_debiteur_compte_pb"] >= 0).all()


def test_participation_technique_resultat_de_l_assureur():
    """Résultat de l'assureur = produits financiers - intérêts nets - dotation + reprise - frais, y compris
    dans la variante : la composante technique passe par la participation, sans autre écriture."""
    h = h_profil("B", apport=30.0)
    df, _ = ec(h)
    p = h["passif"]
    d = df.loc[1:]
    interets_nets = d["taux_servi"] * d["pm"].shift(1, fill_value=df.loc[0, "pm"])
    res = d["produits_financiers"] - interets_nets - d["dotation_ppb"] + d["reprise_ppb"] - d["frais"]
    assert np.allclose(res, d["resultat_assureur"], atol=1e-9)
    assert np.allclose(d["frais"], p["frais_gestion_encours"] * df["pm"].shift(1).loc[1:], rtol=1e-12)


def test_participation_technique_baisse_la_valeur_et_releve_le_taux_servi():
    h = h_profil("B", apport=30.0)
    df0, i0 = ec(appliquer_variante(h, "pb_financiere_seule"))
    df1, i1 = ec(h)
    assert i1["valeur_assureur"] < i0["valeur_assureur"]
    assert df1.loc[1:10, "taux_servi"].mean() >= df0.loc[1:10, "taux_servi"].mean()
    # le transfert ne dépasse pas la valeur actuelle de 90 % du solde technique, sur tout l'horizon
    p = h["passif"]
    d = df0["deflateur"].loc[1:]
    borne = 0.9 * (p["chargements_encours"] - p["frais_gestion_encours"]) * (df1["pm"].shift(1).loc[1:] * d).sum()
    assert i0["valeur_assureur"] - i1["valeur_assureur"] <= borne * 1.05


# --- Impôt payé dans la projection -------------------------------------------------------------------

@pytest.mark.parametrize("p", ["A", "B", "C"])
def test_impot_projete_bilan_et_tresorerie_conserves(p):
    h = appliquer_variante(h_profil(p, apport=20.0), "impot_projete")
    df, ind = ec(h)
    assert df["ecart_bilan"].abs().max() < 1e-8  # fonds propres après impôt = actif - provisions
    assert abs(ind["fuite"]) < 1e-8  # l'impôt payé est une sortie de l'identité de conservation
    assert ind["va_impots_payes"] == pytest.approx((df["impots"] * df["deflateur"]).sum(), rel=1e-12)


def test_impot_projete_egal_au_calcul_apres_coup_sur_les_memes_resultats():
    """Pas de double comptage : l'impôt payé dans la projection est celui que le calcul après coup
    donnerait sur les mêmes résultats avant impôt (mêmes règles, déficits reportables compris)."""
    h = appliquer_variante(h_profil("A", apport=40.0), "impot_projete")
    df, _ = ec(h)
    res = df.loc[1:, "resultat_assureur"].to_numpy()[None, :]
    apres_coup = stg.impots_par_scenario(res, h["fiscalite"]["unite_monetaire_eur"])[0]
    assert np.allclose(df.loc[1:, "impots"].to_numpy(), apres_coup, rtol=0, atol=1e-12)
    tr = pd.concat([df], keys=[0], names=["scenario", "annee"])
    ans = list(range(1, h["horizon_annees"] + 1))
    assert np.allclose(stg.impots_des_trajectoires(tr, h, ans)[0], df.loc[ans, "impots"].to_numpy())


def test_impot_projete_articulation_resultat_net_dividendes_fonds_propres():
    """fonds propres(t) = fonds propres(t-1) + résultat avant impôt - impôt + apport - dividende déclaré."""
    h = appliquer_variante(h_profil("C", apport=10.0), "impot_projete")
    assert (h.get("strategie_alm") or {}).get("distribution")  # la gestion passive distribue l'excédent
    df, _ = ec(h)
    d = df.loc[1:]
    fp_prec = df["fonds_propres"].shift(1).loc[1:]
    attendu = fp_prec + d["resultat_assureur"] - d["impots"] + d["apport_assureur"] - d["dividende_a_payer"]
    assert np.allclose(attendu, d["fonds_propres"], atol=1e-9)
    # dividende déclaré en t, versé en t+1
    assert np.allclose(df["dividende_a_payer"].fillna(0.0).shift(1).loc[1:], d["dividendes"], atol=1e-12)


def test_impot_projete_deficits_reportables():
    h = appliquer_variante(h_profil("A"), "impot_projete")
    df, _ = ec(h)
    u = h["fiscalite"]["unite_monetaire_eur"]
    report = 0.0
    for t in df.index[1:]:
        total, _, _, report = impot_annuel(float(df.loc[t, "resultat_assureur"]), 1e12, report, u)
        assert df.loc[t, "impots"] == pytest.approx(total, abs=1e-12)
        if df.loc[t, "resultat_assureur"] <= 0:
            assert df.loc[t, "impots"] == 0.0


def test_impot_projete_sort_de_l_actif():
    """Sans distribution, l'actif de la variante, net des provisions mathématiques, est inférieur à celui de
    la référence d'un montant de l'ordre des impôts cumulés (les revenus de ces montants en plus, la
    participation en moins). Net des PM : un taux servi à peine différent peut modifier les rachats
    dynamiques, qui changent l'actif et les PM du même montant."""
    h = h_profil("B", apport=30.0)
    h["strategie_alm"] = dict(h.get("strategie_alm") or {}, distribution=None)
    df0, _ = ec(h)
    df1, _ = ec(appliquer_variante(h, "impot_projete"))
    ecart = ((df0["vnc_actif"] - df0["pm"]) - (df1["vnc_actif"] - df1["pm"])).loc[1:]
    cumul = df1["impots"].cumsum().loc[1:]
    assert (ecart > 0).iloc[-1] and (ecart.loc[1:5] / cumul.loc[1:5]).between(0.9, 1.2).all()


def test_valeur_nette_deduit_l_impot_une_seule_fois():
    """Variante : valeur nette = actif - BE - apport - VA de l'impôt payé ; l'identité de décomposition
    (dividendes, résidu final, apports, impôt, fuite) reste exacte."""
    h = appliquer_variante(h_profil("B", apport=29.5), "impot_projete")
    credit = cv.credit_valorisation(CREDIT, "sans_va", h["horizon_annees"])
    q = stg.resume_risque_neutre(h, credit, "sans_va", n=20)
    assert abs(q["va_dividendes"] + q["va_residuel_final"] - q["apport_initial"] - q["va_apports_ulterieurs"]
               - q["va_impots"] + q["fuite"] - q["valeur_nette"]) < 1e-9
    x = col.projection_risque_neutre(h, credit, n=20)
    assert np.allclose(x["valeur_nette"], x["vm0"] - x["be"] - x["apport_initial"] - x["va_impots"])


def test_convention_de_reference_et_variantes():
    """Référence de la V5.1 : participation technique (10 % du solde créditeur à l'assureur), impôt après
    coup ; « pb_financiere_seule » retire la composante technique (V5.0) ; les variantes copient h."""
    h = h_profil("B", apport=29.5)
    assert h["strategie"]["participation_technique"] == {"part_assureur": PART_ASSUREUR_SOLDE_TECHNIQUE}
    assert not h["fiscalite"].get("impot_dans_projection")
    df, _ = ec(h)
    assert "impots" not in df and "pb_minimale" in df
    h0 = appliquer_variante(h, "pb_financiere_seule")
    assert "participation_technique" not in h0["strategie"] and "participation_technique" in h["strategie"]
    df0, _ = ec(h0)
    assert "pb_minimale" not in df0
    with pytest.raises(ValueError):
        appliquer_variante(h, "inconnue")


# --- Solde technique débiteur, garanties et reprises de PPB (projection complète) ---------------------

def test_solde_technique_debiteur_report_tmg_et_bilan():
    """Cas extrême construit pour le test (frais d'acquisition fictifs de 45 % des primes, collecte forte
    pendant 10 ans) : le solde technique devient débiteur au-delà de la part financière ; le compte est
    débiteur et reporté d'un exercice sur l'autre, puis diminue dès que les comptes annuels redeviennent
    créditeurs (fin de la collecte) ; la participation minimale est alors nulle, le taux servi reste au moins égal au TMG moyen, le bilan
    reste équilibré et la fuite nulle. Dans les configurations publiées, le solde technique reste créditeur
    (resultats/v5_audit_conventions.json, rubrique compte_debiteur)."""
    h = col.appliquer_collecte(h_profil("A", apport=110.0), 0.10, 0.0, frais_acquisition_prime=0.45)
    df, ind = ec(h)
    p, cn = h["passif"], h["collecte"]["contrats_nouveaux"]
    d = df.loc[1:]
    pm_debut = df["pm"].shift(1).loc[1:]
    technique = (p["chargements_encours"] - p["frais_gestion_encours"]) * pm_debut + (cn["chargement_prime"] - cn["frais_acquisition_prime"]) * d["primes"]
    assert (technique < 0).any()
    debiteur = d["solde_debiteur_compte_pb"] > 1e-12
    horizon = h["collecte"]["horizon_collecte_ans"]
    report = d["solde_debiteur_compte_pb"]
    assert (technique.loc[1:horizon] < 0).all() and report.loc[1:horizon].is_monotonic_increasing
    assert report.loc[horizon + 1] > 0  # reporté au-delà de la collecte
    assert (report.loc[horizon + 1:].diff().dropna() <= 1e-9).all()  # imputé sur les comptes créditeurs suivants
    assert (d.loc[debiteur, "pb_minimale"] == 0.0).all() and (d.loc[debiteur, "complement_reglementaire_pb"] == 0.0).all()
    tmg = (df["pm_existant"].shift(1).loc[1:] * p["tmg"] + df["pm_nouveaux"].shift(1).loc[1:] * cn["tmg"]) / pm_debut
    assert (d["taux_servi"] >= tmg - 1e-12).all()
    assert df["ecart_bilan"].abs().max() < 1e-8 and abs(ind["fuite"]) < 1e-8


@pytest.mark.parametrize("tr", [2.3, 0.0, -1.0, -20.0])
def test_tmg_et_reprise_obligatoire_quel_que_soit_le_compte(tr):
    """Compte créditeur, nul ou débiteur : le taux servi ne descend pas sous le TMG et la reprise obligatoire
    de la PPB (génération de 8 ans) est toujours faite."""
    h = h_profil("A")
    tmg = h["passif"]["tmg"]
    for pf in (2.0, 15.0, 40.0):
        s = decider_taux_servi(pf, 1000.0, _PPB(48.0), 0.0, 0.02, h, 0.9, participation_technique(tr, 0.0, 0.10))
        assert s["taux_servi"] >= tmg - 1e-12
        assert s["reprise_ppb"] >= 48.0 / 8 - 1e-12
        assert _participation_de_l_exercice(s) >= s["pb_minimale"] - 1e-9
