"""Liquidation de la PPB quand le portefeuille s'éteint.

Convention du modèle : la PPB appartient collectivement aux assurés. Tant qu'il
reste des contrats, elle est redistribuée selon la stratégie (reprises, règle
des 8 ans) et un rachat partiel ne la fait pas sortir. Quand il ne reste plus
aucun contrat, la PPB restante est versée aux derniers assurés à la date de
leurs dernières prestations, comme à l'horizon de projection.

Les valeurs attendues sont calculées à la main à partir du bilan initial, sans
réutiliser les fonctions de calcul du modèle.
"""

import pytest

from src.projection import indicateurs, projeter, scenario


def test_rachat_total_a_l_ouverture_ppb_versee_en_t0(h):
    pm0, ppb0 = h["bilan_initial"]["pm"], h["bilan_initial"]["ppb"]
    df = projeter(h, scenario(h, "central"), rachat_massif=1.0)
    # Rachats et PPB sont payés à la même date, t = 0, sans actualisation
    assert df.loc[0, "prestations"] == pytest.approx(pm0 + ppb0, abs=1e-9)
    assert df.loc[0, "ppb_versee_extinction"] == pytest.approx(ppb0, abs=1e-9)
    # Après t = 0, plus rien n'est dû aux assurés
    assert df.loc[1:, "prestations"].abs().max() < 1e-9
    assert df.loc[1:, "ppb"].abs().max() < 1e-9
    ind = indicateurs(df)
    assert ind["be"] == pytest.approx(pm0 + ppb0, abs=1e-9)
    assert ind["be_garanti"] == pytest.approx(pm0, abs=1e-9)
    assert ind["fdb"] == pytest.approx(ppb0, abs=1e-9)
    assert ind["valeur_assureur"] == pytest.approx(df.attrs["vm_apres_choc"] - pm0 - ppb0, abs=1e-9)


def test_rachat_partiel_a_l_ouverture_ppb_conservee(h):
    """Un rachat massif partiel ne liquide pas la PPB : les contrats restants en bénéficient."""
    pm0, ppb0 = h["bilan_initial"]["pm"], h["bilan_initial"]["ppb"]
    df = projeter(h, scenario(h, "central"), rachat_massif=0.4)
    assert df.loc[0, "prestations"] == pytest.approx(0.4 * pm0, abs=1e-9)
    assert df.loc[0, "ppb_versee_extinction"] == 0.0
    assert df.loc[1, "ppb"] > 0


def test_dotation_de_l_annee_d_extinction_versee_a_la_meme_date(h):
    """Rachat total en année 1 dans un scénario où la stratégie dote la PPB cette année-là.

    La dotation de l'année ne doit pas rester en provision, sans assuré, pour
    être versée l'année suivante : elle est versée avec les dernières prestations.
    """
    df = projeter(h, scenario(h, "baisse_taux_100pb"), choc_rachats=19.0)
    assert df.loc[1, "taux_rachat"] == 1.0 and df.loc[1, "pm"] == 0.0
    assert df.loc[1, "dotation_ppb"] > 1.0  # le cas étudié est bien celui d'une dotation
    ppb0 = h["bilan_initial"]["ppb"]
    attendu = ppb0 - df.loc[1, "reprise_ppb"] + df.loc[1, "dotation_ppb"]
    assert df.loc[1, "ppb_versee_extinction"] == pytest.approx(attendu, abs=1e-9)
    assert df.loc[1, "ppb"] == pytest.approx(0.0, abs=1e-9)
    assert df.loc[2:, "prestations"].abs().max() < 1e-9
    assert df["ecart_bilan"].dropna().abs().max() < 1e-7
