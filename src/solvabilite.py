"""Bilan Solvabilité II simplifié : chocs, SCR brut et net, marge de risque (V3).

Ce module produit un calcul pédagogique inspiré de la formule standard. Il ne
prétend pas à la conformité réglementaire. Ce qui suit la formule standard :

- choc de taux, articles 166 et 167 du règlement délégué (UE) 2015/35, version
  applicable jusqu'au 29/01/2027 : chocs relatifs par maturité sur les taux
  zéro-coupon, hausse d'au moins 1 point, pas de baisse d'un taux négatif ;
- choc actions de type 1 de 39 % (article 169), ajustement symétrique pris nul ;
- risque de rachat (article 142) : hausse de 50 % des taux (plafond 100 %),
  baisse de 50 % (au plus 20 points), rachat massif de 40 % ;
- choix du scénario de taux et du scénario de rachat d'après la perte nette,
  c'est-à-dire calculée selon l'article 206(2) ; le besoin brut est pris sur
  le même scénario (articles 165(2) et 142(7)) ;
- agrégation : corrélation taux / actions A = 0 si la hausse des taux est
  retenue, 0,5 sinon (article 164) ; corrélation marché / vie 0,25 (annexe IV
  de la directive) ;
- capacité d'absorption des pertes des provisions techniques (article 206(1)) :
  Adj = -max(min(BSCR - nBSCR, FDB), 0) ;
- marge de risque (article 37) : règles en vigueur en 2026 (coût du capital de
  6 %, article 39), et une sensibilité aux seuls paramètres de marge de risque
  du règlement délégué (UE) 2026/269 (4,75 % et facteur max(0,96^t ; 50 %),
  applicables à partir du 30/01/2027). Cette sensibilité ne change rien
  d'autre : chocs, courbe, modules et SCR restent ceux des règles de 2026. Ce
  n'est pas un calcul selon le régime révisé.

Calcul de chaque perte : chaque choc relance la projection stochastique
complète, sur les mêmes tirages que la base, pour que l'écart mesure l'effet du
choc et non le bruit de Monte-Carlo.
- perte nette = fonds propres économiques de base - fonds propres choqués, le
  modèle ajustant taux servi et PPB sous choc (actions de gestion) ;
- perte brute = perte nette + (FDB de base - FDB choquées). C'est la perte
  quand le scénario ne change pas la valeur des FDB (article 83(1)(c)), et
  c'est la méthode de l'orientation 2 des orientations EIOPA sur la capacité
  d'absorption des pertes (EIOPA-BoS-14/177, paragraphe 1.14). Limite : les
  prestations garanties sous choc reprennent les sorties (décès, rachats
  dynamiques) du calcul net ; un calcul brut direct, à flux de FDB figés
  (orientation 1, paragraphe 1.12), pourrait donner d'autres sorties. L'écart
  entre les deux n'est pas mesuré.

Ce qui reste hors du calcul : risques de spread, d'immobilier, de change, de
mortalité, de frais et de catastrophe, risque opérationnel, ajustement pour
impôts différés, nouvelle méthode de choc de taux de la révision (non
implémentée), extrapolation réglementaire de la courbe, sélection des contrats
concernés par le rachat massif (article 142(6)).
"""

import math

from .courbes import CourbeZeroCoupon
from .gse import GSE, demi_intervalle
from .stochastique import projeter_stochastique


# --- Chocs de taux -------------------------------------------------------------

def facteur_choc(maturite, maturites, valeurs):
    """Choc relatif à une maturité donnée : en dessous de 1 an, la valeur à 1 an ;
    au-delà de la dernière maturité, la dernière valeur ; entre deux, interpolation linéaire."""
    if maturite <= maturites[0]:
        return valeurs[0]
    if maturite >= maturites[-1]:
        return valeurs[-1]
    for (m0, v0), (m1, v1) in zip(zip(maturites, valeurs), zip(maturites[1:], valeurs[1:])):
        if m0 <= maturite <= m1:
            return v0 + (maturite - m0) / (m1 - m0) * (v1 - v0)
    raise ValueError(maturite)


def courbes_choquees(courbe, parametres, maturite_max=150):
    """Courbes choquées à la hausse et à la baisse (articles 166 et 167, régime en vigueur en 2026).

    Hausse : r + max(r x s_hausse(m), 1 point). Baisse : r x (1 - s_baisse(m)) si r > 0, inchangé sinon.
    """
    m, up, down = parametres["maturites"], parametres["s_hausse"], parametres["s_baisse"]
    hausse, baisse = [], []
    for k in range(1, maturite_max + 1):
        r = courbe.taux_maturite(k)
        hausse.append(r + max(r * facteur_choc(k, m, up), parametres["hausse_minimale"]))
        baisse.append(r * (1 - facteur_choc(k, m, down)) if r > 0 else r)
    return CourbeZeroCoupon(hausse), CourbeZeroCoupon(baisse)


# --- Agrégation et marge de risque ------------------------------------------

def agreger(scr_taux, scr_actions, scr_rachat, rho_taux_actions, rho_marche_vie):
    """SCR marché puis BSCR, avec les corrélations de la formule standard."""
    marche = math.sqrt(scr_taux**2 + scr_actions**2 + 2 * rho_taux_actions * scr_taux * scr_actions)
    bscr = math.sqrt(marche**2 + scr_rachat**2 + 2 * rho_marche_vie * marche * scr_rachat)
    return marche, bscr


def marge_de_risque(scr_projetes, courbe, regime):
    """Marge de risque (article 37) : coût du capital x somme des SCR futurs actualisés.

    scr_projetes[t] : SCR non couvrable projeté à la date t (t = 0, 1, ...).
    Avec lambda (paramètres du règlement délégué (UE) 2026/269) : chaque SCR(t)
    est multiplié par max(lambda^t, plancher). Sans lambda : facteur 1.
    """
    total = 0.0
    for t, scr in enumerate(scr_projetes):
        facteur = 1.0
        if regime["lambda"] is not None:
            facteur = max(regime["lambda"] ** t, regime["plancher_lambda"])
        total += facteur * scr * courbe.zc(t + 1)
    return regime["cout_du_capital"] * total


def ajustement_absorption(bscr, nbscr, fdb):
    """Article 206(1) : Adj = -max(min(BSCR - nBSCR, FDB), 0)."""
    return -max(min(bscr - nbscr, fdb), 0.0)


CHOCS_TAUX = ("taux_hausse", "taux_baisse")
CHOCS_RACHAT = ("rachats_hausse", "rachats_baisse", "rachat_massif")


def assembler_scr(fonds_propres, fdb, s2):
    """Des résultats par scénario au SCR simplifié, sans aucune projection.

    fonds_propres[nom], fdb[nom] : fonds propres économiques (actif - BE) et FDB
    de chaque scénario, base comprise. Fonction pure, testable sur des chiffres
    calculés à la main.
    - perte nette = FP base - FP choqué ; perte brute = perte nette + (FDB base -
      FDB choquées), c'est-à-dire la perte à valeur des FDB inchangée ;
    - besoin par sous-module = max(perte, 0) ;
    - scénario de taux et scénario de rachat choisis sur la perte nette, la
      perte brute étant prise sur le même scénario (art. 165(2) et 142(7)) ;
    - même corrélation A dans les agrégations brute et nette, puisqu'elle
      dépend du scénario de taux retenu (art. 164).
    """
    chocs = [nom for nom in fonds_propres if nom != "base"]
    nette = {nom: fonds_propres["base"] - fonds_propres[nom] for nom in chocs}
    brute = {nom: nette[nom] + (fdb["base"] - fdb[nom]) for nom in chocs}

    sens_taux = max(CHOCS_TAUX, key=lambda k: nette[k])
    sens_rachat = max(CHOCS_RACHAT, key=lambda k: nette[k])
    rho_ta = 0.0 if sens_taux == "taux_hausse" else s2["correlation_taux_actions_baisse"]
    rho_mv = s2["correlation_marche_vie"]

    def modules(pertes):
        taux = max(pertes[sens_taux], 0.0)
        actions = max(pertes["actions"], 0.0)
        rachat = max(pertes[sens_rachat], 0.0)
        marche, bscr = agreger(taux, actions, rachat, rho_ta, rho_mv)
        return {"taux": taux, "actions": actions, "marche": marche, "rachat": rachat, "bscr": bscr}

    net, brut = modules(nette), modules(brute)
    adj = ajustement_absorption(brut["bscr"], net["bscr"], fdb["base"])
    return {
        "pertes_nettes": nette, "pertes_brutes": brute,
        "sens_retenus": {"taux": sens_taux, "rachat": sens_rachat},
        "scr_net": net, "scr_brut": brut, "ajustement_tp": adj, "scr": brut["bscr"] + adj,
        "plafond_fdb_atteint": brut["bscr"] - net["bscr"] > fdb["base"],
        "marge_avant_plafond": fdb["base"] - (brut["bscr"] - net["bscr"]),
    }


# --- Calcul complet ------------------------------------------------------------

def calculer_scr(h, n=None, verbeux=False):
    s2 = h["solvabilite2"]
    courbe_base = CourbeZeroCoupon.plate(h["economie"]["taux_sans_risque"])
    courbe_hausse, courbe_baisse = courbes_choquees(courbe_base, s2["choc_taux"])

    def lancer(nom, **kw):
        options = {k: kw.pop(k) for k in ("choc_rachats", "rachat_massif") if k in kw}
        res = projeter_stochastique(h, GSE(h, nom=nom, n=n, **kw), **options)
        if verbeux:
            print(f"{nom} : BE = {res['synthese']['be']:.1f}")
        return res

    runs = {
        "base": lancer("base"),
        "taux_hausse": lancer("taux_hausse", courbe=courbe_hausse),
        "taux_baisse": lancer("taux_baisse", courbe=courbe_baisse),
        "actions": lancer("actions", choc_actions=s2["choc_actions"]),
        "rachats_hausse": lancer("rachats_hausse", choc_rachats=s2["choc_rachats_hausse"]),
        "rachats_baisse": lancer("rachats_baisse", choc_rachats=s2["choc_rachats_baisse"]),
        "rachat_massif": lancer("rachat_massif", rachat_massif=s2["rachat_massif"]),
    }
    synth = {nom: r["synthese"] for nom, r in runs.items()}

    # Fonds propres économiques (avant marge de risque) et FDB de chaque scénario
    fp = {nom: s["vm_actif_initial"] - s["be"] for nom, s in synth.items()}
    fdb = {nom: s["fdb"] for nom, s in synth.items()}
    a = assembler_scr(fp, fdb, s2)
    nette, brute, net, brut = a["pertes_nettes"], a["pertes_brutes"], a["scr_net"], a["scr_brut"]

    # Précision Monte-Carlo des pertes : tirages appariés (mêmes scénarios dans
    # la base et sous choc), donc intervalles calculés sur les écarts scénario
    # par scénario. Perte nette : écarts de BE. Perte brute : écarts de la part
    # non discrétionnaire du BE (BE - FDB = BE garanti + BE des frais).
    def par_scenario(nom, col):
        return runs[nom]["par_scenario"][col].to_numpy()

    def hors_fdb(nom):
        return par_scenario(nom, "be") - par_scenario(nom, "fdb")

    ic_nette = {nom: demi_intervalle(par_scenario(nom, "be") - par_scenario("base", "be")) for nom in nette}
    ic_brute = {nom: demi_intervalle(hors_fdb(nom) - hors_fdb("base")) for nom in brute}

    # Marge de risque : SCR non couvrable = SCR de rachat après absorption,
    # projeté au rythme d'écoulement de la PM moyenne
    pm_moy = runs["base"]["moyennes"]["pm"]
    scr_projetes = [net["rachat"] * pm_moy.loc[t] / pm_moy.loc[0] for t in range(h["horizon_annees"])]
    marges = {nom: marge_de_risque(scr_projetes, courbe_base, regime)
              for nom, regime in s2["marge_de_risque"].items()}

    # Un bilan par jeu de paramètres de marge de risque : seule la marge de
    # risque change d'un bilan à l'autre, BE et SCR sont communs
    base, scr = synth["base"], a["scr"]
    bilans = {}
    for nom, mr in marges.items():
        fonds_propres = base["vm_actif_initial"] - base["be"] - mr
        bilans[nom] = {
            "libelle": s2["marge_de_risque"][nom]["libelle"],
            "actif": base["vm_actif_initial"], "be": base["be"], "dont_fdb": fdb["base"],
            "marge_risque": mr, "fonds_propres": fonds_propres, "scr": scr,
            "fonds_propres_sur_scr": fonds_propres / scr if scr > 0 else float("inf"),
        }

    controles = {
        "fdb_negatives": [nom for nom, v in fdb.items() if v < 0],
        "ajustement_plafonne_par_fdb": a["plafond_fdb_atteint"],
        "marge_avant_plafond_fdb": a["marge_avant_plafond"],
        "part_scenarios_avec_apport": {nom: s["part_scenarios_avec_apport"] for nom, s in synth.items()},
    }
    return {
        "runs": runs, "courbes": {"base": courbe_base, "hausse": courbe_hausse, "baisse": courbe_baisse},
        "fonds_propres_economiques": fp, "fdb": fdb,
        "pertes_nettes": nette, "ic_pertes_nettes": ic_nette,
        "pertes_brutes": brute, "ic_pertes_brutes": ic_brute,
        "sens_retenus": a["sens_retenus"],
        "scr_net": net, "scr_brut": brut, "ajustement_tp": a["ajustement_tp"], "scr": a["scr"],
        "marges_de_risque": marges, "bilan": bilans[s2["regime_marge_de_risque"]], "bilans": bilans,
        "controles": controles,
    }
