"""Vue prudentielle simplifiée des profils V5 : bilan Solvabilité II approché et SCR approché.

Objet : séparer la « valeur économique simplifiée » (actif - BE, base sans VA, avant impôt et
avant marge de risque) d'une lecture prudentielle (base avec VA, marge de risque, SCR, impôts
différés). Calcul pédagogique inspiré de la formule standard (règles de 2026), qui reprend les
mécanismes de la V3 (src/solvabilite.py) sur la courbe EIOPA et les obligations risquées :

- taux : chocs relatifs des articles 166 et 167, appliqués directement à la courbe de la base
  (approximation : la formule les applique à la courbe de base avant ajout de la VA) ;
- actions : choc de type 1 de 39 %, ajustement symétrique pris nul (valeur d'octobre 2026 non lue) ;
- spread (article 176) : part non souveraine des obligations, qualité de crédit 2 (notation A), selon
  la duration modifiée ; les souverains de l'EEE ne portent pas de charge ; le choc est appliqué
  comme un élargissement instantané du spread de tout le portefeuille, calé pour produire la perte
  de valeur de marché de la formule ;
- rachat : hausse et baisse de 50 %, rachat massif de 40 % ;
- agrégation : corrélations de marché de l'article 164 (A = 0 si la hausse des taux est retenue,
  0,5 sinon ; actions et spread 0,75), marché et vie 0,25 ;
- capacité d'absorption des provisions techniques par les FDB (article 206(1)), méthode de la V3 ;
- marge de risque au coût du capital de 6 % sur le SCR de rachat, écoulé avec la PM moyenne.
Cette première version (`scr_simplifie`) ne calcule ni le risque opérationnel, ni la mortalité et les
frais, ni l'absorption par les impôts différés, ni les fonds excédentaires.

La vue prudentielle des résultats finaux (`bilan_prudentiel`, scripts/v5_consolidation.py) les ajoute :
chocs de mortalité et de frais agrégés au module vie, risque opérationnel par la formule sur provisions,
fonds excédentaires (PPB admise en fonds propres par l'arrêté du 24/12/2019, après déduction de la génération
restituée l'exercice suivant, selon la fiche technique de l'ACPR ; valorisée par l'approche simplifiée de cette
fiche), impôts différés passifs et leur capacité d'absorption, marge de risque sur le SCR vie net et opérationnel,
MCR. L'ajustement pour absorption par les provisions techniques est borné par FDB − fonds excédentaires : les
fonds excédentaires ne sont plus des provisions techniques (article 91 de la directive) et ne peuvent pas absorber
une seconde fois les pertes qu'ils couvrent déjà en fonds propres. Restent hors calcul
(liste dans la docstring de `bilan_prudentiel`) : mesure transitoire, contrepartie, concentration,
immobilier, change, inflation des frais, ajustement symétrique actions, impôts différés actifs.
"""

import copy
import math

from ..gse import GSE
from ..solvabilite import ajustement_absorption, courbes_choquees, marge_de_risque
from ..stochastique import projeter_stochastique
from . import bases, conventions as cv

PART_NON_SOUVERAINE = 0.66  # ACPR n° 181 : souverains 19 % des placements, obligations 56 % (19 + 27 + 10)


def facteur_spread_cqs2(duration):
    """Article 176, qualité de crédit 2 : facteur de choc selon la duration modifiée."""
    d = duration
    if d <= 5:
        return 0.014 * d
    if d <= 10:
        return 0.07 + 0.007 * (d - 5)
    if d <= 15:
        return 0.105 + 0.005 * (d - 10)
    if d <= 20:
        return 0.13 + 0.005 * (d - 15)
    return min(0.155 + 0.005 * (d - 20), 1.0)


def agreger_marche(taux, actions, spread, sens_taux):
    a = 0.0 if sens_taux == "taux_hausse" else 0.5
    m = (taux**2 + actions**2 + spread**2 + 2 * a * taux * actions + 2 * a * taux * spread + 2 * 0.75 * actions * spread)
    return math.sqrt(m)


def bscr(pertes, sens_taux, sens_rachat):
    taux, actions, spread = (max(pertes[k], 0.0) for k in (sens_taux, "actions", "spread"))
    rachat = max(pertes[sens_rachat], 0.0)
    marche = agreger_marche(taux, actions, spread, sens_taux)
    return {"taux": taux, "actions": actions, "spread": spread, "marche": marche, "rachat": rachat,
            "bscr": math.sqrt(marche**2 + rachat**2 + 2 * 0.25 * marche * rachat)}


def choc_spread_calibre(h, credit, base, courbe):
    """Élargissement parallèle du spread qui fait perdre aux obligations la perte de la formule standard."""
    from ..actif import Portefeuille

    p = Portefeuille(h, credit=bases.credit_sur_base(credit, base))
    vm = p.vm_obligations(courbe)
    bas, haut = copy.deepcopy(p), copy.deepcopy(p)
    bas.choc_spread(-0.0001)
    haut.choc_spread(0.0001)
    dmod = (bas.vm_obligations(courbe) - haut.vm_obligations(courbe)) / (0.0002 * vm)
    perte = PART_NON_SOUVERAINE * vm * facteur_spread_cqs2(dmod)
    # résolution par dichotomie de l'élargissement qui produit cette perte
    lo, hi = 0.0, 0.2
    for _ in range(60):
        mid = (lo + hi) / 2
        q = copy.deepcopy(p)
        q.choc_spread(mid)
        if vm - q.vm_obligations(courbe) < perte:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2, perte, dmod


def scr_simplifie(h, credit_code, base="avec_va", n=1000, cout_capital=0.06):
    """Bilan prudentiel et SCR approchés d'un jeu d'hypothèses (référence des assurés déjà appliquée)."""
    s2 = h["solvabilite2"]
    c0 = bases.courbe_base(base)
    hausse, baisse = courbes_choquees(c0, s2["choc_taux"])
    credit = cv.credit_valorisation(credit_code, "sans_va", h["horizon_annees"])
    choc, perte_spread, dmod = choc_spread_calibre(h, credit, base, c0)
    credit_choque = credit.copie()
    credit_choque.choquer(choc)

    def lancer(courbe=None, credit_=credit, **kw):
        options = {k: kw.pop(k) for k in ("choc_rachats", "rachat_massif") if k in kw}
        if courbe is None:
            g, cr = bases.gse(h, base, credit_, n=n, **kw)
        else:  # choc de taux : mêmes tirages, courbe choquée ; spread inchangé au-dessus de la courbe choquée
            g, cr = GSE(h, courbe=courbe, courbe_avant_choc=c0, n=n, **kw), bases.credit_sur_base(credit_, base)
        return projeter_stochastique(h, g, credit=cr, **options)

    runs = {
        "base": lancer(),
        "taux_hausse": lancer(courbe=hausse), "taux_baisse": lancer(courbe=baisse),
        "actions": lancer(choc_actions=s2["choc_actions"]),
        "spread": lancer(credit_=credit_choque),
        "rachats_hausse": lancer(choc_rachats=s2["choc_rachats_hausse"]),
        "rachats_baisse": lancer(choc_rachats=s2["choc_rachats_baisse"]),
        "rachat_massif": lancer(rachat_massif=s2["rachat_massif"]),
    }
    synth = {k: r["synthese"] for k, r in runs.items()}
    fp = {k: s["vm_actif_initial"] - s["be"] for k, s in synth.items()}
    fdb = {k: s["fdb"] for k, s in synth.items()}
    nette = {k: fp["base"] - fp[k] for k in fp if k != "base"}
    brute = {k: nette[k] + fdb["base"] - fdb[k] for k in nette}
    sens_taux = max(("taux_hausse", "taux_baisse"), key=lambda k: nette[k])
    sens_rachat = max(("rachats_hausse", "rachats_baisse", "rachat_massif"), key=lambda k: nette[k])
    net, brut = bscr(nette, sens_taux, sens_rachat), bscr(brute, sens_taux, sens_rachat)
    adj = ajustement_absorption(brut["bscr"], net["bscr"], fdb["base"])
    scr = brut["bscr"] + adj
    pm_moy = runs["base"]["moyennes"]["pm"]
    scr_projetes = [net["rachat"] * pm_moy.loc[t] / pm_moy.loc[0] for t in range(h["horizon_annees"])]
    mr = marge_de_risque(scr_projetes, c0, {"cout_du_capital": cout_capital, "lambda": None, "plancher_lambda": None})
    b = h["bilan_initial"]
    fonds_propres = fp["base"] - mr
    taux_is = 0.25 * (1 + 0.033)  # 25 % et contribution sociale de 3,3 % (abattement négligeable à cette échelle)
    impots_differes = taux_is * (fonds_propres - (b["fonds_propres"] + b["reserve_capitalisation"]))
    return {
        "base": base, "credit": credit_code, "n_scenarios": n,
        "actif": synth["base"]["vm_actif_initial"], "be": synth["base"]["be"], "ic_be": synth["base"]["ic_be"],
        "fdb": fdb["base"], "marge_de_risque": mr,
        "fonds_propres_avant_impots_differes": fonds_propres,
        "impots_differes_passif_si_positif": impots_differes,
        "fonds_propres_apres_impots_differes": fonds_propres - impots_differes,
        "pertes_nettes": nette, "pertes_brutes": brute, "sens_retenus": {"taux": sens_taux, "rachat": sens_rachat},
        "scr_net": net, "scr_brut": brut, "ajustement_tp": adj, "scr": scr,
        "choc_spread": {"elargissement": choc, "perte_formule_standard": perte_spread, "duration_modifiee": dmod,
                        "part_non_souveraine": PART_NON_SOUVERAINE},
        "ratio_avant_impots_differes": fonds_propres / scr if scr > 0 else float("inf"),
        "ratio_apres_impots_differes": (fonds_propres - impots_differes) / scr if scr > 0 else float("inf"),
        "part_scenarios_avec_apport": {k: s["part_scenarios_avec_apport"] for k, s in synth.items()},
    }


# --- Vue prudentielle complétée (palier de sécurisation avant l'optimisation) --------------------

TAUX_IS = 0.25 * (1 + 0.033)  # 25 % et contribution sociale de 3,3 % (abattement négligeable à cette échelle)
NOTATIONS = {"cqs1": 0.20, "cqs2": 0.61, "cqs3": 0.18, "cqs4": 0.01}  # ACPR n° 181, graphique 14 (T4 2025)
CORR_VIE = {("rachat", "mortalite"): 0.0, ("rachat", "frais"): 0.5, ("mortalite", "frais"): 0.25}


def facteur_spread(cqs, d):
    """Article 176 : facteur de choc des obligations selon la qualité de crédit et la duration modifiée."""
    tables = {  # (a, b) par tranche : facteur = a + b x (d - borne basse)
        "cqs1": [(0.0, 0.011), (0.055, 0.006), (0.085, 0.005), (0.11, 0.005), (0.135, 0.005)],
        "cqs2": [(0.0, 0.014), (0.07, 0.007), (0.105, 0.005), (0.13, 0.005), (0.155, 0.005)],
        "cqs3": [(0.0, 0.025), (0.125, 0.015), (0.20, 0.01), (0.25, 0.01), (0.30, 0.005)],
        "cqs4": [(0.0, 0.045), (0.225, 0.025), (0.35, 0.018), (0.44, 0.005), (0.465, 0.005)],
    }
    bornes = [0, 5, 10, 15, 20]
    i = max(k for k, b in enumerate(bornes) if d >= b) if d > 0 else 0
    a, b = tables[cqs][i]
    return min(a + b * (d - bornes[i]), 1.0)


def ppb_admissible_fonds_excedentaires(h):
    """PPB comptable admissible en fonds excédentaires (fiche technique de l'ACPR, calcul des fonds propres
    prudentiels au titre de la PPB) : le stock d'ouverture moins la génération qui doit être restituée
    l'exercice suivant. Les deux autres exclusions de la fiche (participation déjà affectée mais non créditée,
    enveloppe de l'article A.132-3) n'ont pas d'équivalent dans le modèle : elles sont supposées nulles.
    Avec le stock d'ouverture réparti uniformément sur les générations (PPB), la déduction vaut un huitième."""
    from ..strategie import PPB
    ppb = PPB(h["bilan_initial"]["ppb"], h["strategie"]["duree_max_ppb_ans"])
    return ppb.stock - ppb.reprise_obligatoire()


def fonds_excedentaires(ppb_admissible, prestations, courbe, annee_entree=8):
    """Approche simplifiée de l'ACPR (annexe 2 de la fiche) : la PPB admissible entre en PM au bout de huit ans,
    puis sort au rythme des prestations projetées, actualisées avec la courbe sans risque."""
    flux = {t: v for t, v in prestations.items() if t > annee_entree and v > 0}
    total = sum(flux.values())
    if total <= 0:
        return 0.0
    return ppb_admissible * sum(v / total * courbe.zc(t) for t, v in flux.items())


def mcr(scr, tp_garanties, fdb, amcr=0.4):
    """Article 251 (vie), réduit aux contrats avec participation aux bénéfices :
    MCR linéaire = max(0 ; 3,7 % x provisions des prestations garanties - 5,2 % x FDB), sans capital
    sous risque (la prestation décès d'un contrat d'épargne est la PM) ; MCR combiné = linéaire encadré
    entre 25 % et 45 % du SCR ; MCR = max(combiné ; plancher absolu de 4 M€, soit 0,4 unité).
    tp_garanties = BE - FDB (prestations garanties et frais) ; fdb hors fonds excédentaires."""
    return mcr_detail(scr, tp_garanties, fdb, amcr)["mcr"]


def mcr_detail(scr, tp_garanties, fdb, amcr=0.4):
    termes = {"garanties": 0.037 * max(tp_garanties, 0.0), "fdb": -0.052 * max(fdb, 0.0)}
    lineaire = max(termes["garanties"] + termes["fdb"], 0.0)
    plancher, plafond = 0.25 * scr, 0.45 * scr
    combine = min(max(lineaire, plancher), plafond)
    m = max(combine, amcr)
    contrainte = "minimum absolu" if m > combine else ("plancher de 25 % du SCR" if lineaire < plancher else
                                                        ("plafond de 45 % du SCR" if lineaire > plafond else "MCR linéaire"))
    return {"termes_lineaires": termes, "lineaire": lineaire, "plancher_25": plancher, "plafond_45": plafond,
            "combine": combine, "minimum_absolu": amcr, "mcr": m, "contrainte_active": contrainte}


def bilan_prudentiel(h, credit_code, base="avec_va", n=1000, cout_capital=0.06, echantillons=False):
    """Bilan prudentiel et indicateur de couverture simplifiés (référence des assurés déjà appliquée).

    Hors calcul, signalé : risque opérationnel par la seule formule sur provisions, mesure transitoire
    sur les provisions techniques, risque de contrepartie, concentration, immobilier, change,
    inflation des frais, ajustement symétrique actions (pris nul), reconnaissance d'impôts différés
    actifs (non reconnus, faute de démonstration de recouvrabilité ; sensibilité fournie).

    echantillons=True ajoute « _tirages » (BE et FDB par scénario pour chaque choc, mêmes scénarios
    pour tous les chocs) et « _contexte » : `reagreger` recalcule alors tous les indicateurs sur un
    rééchantillon de paires antithétiques, pour mesurer l'incertitude Monte-Carlo.
    """
    from ..projection import projeter
    from .scenarios import ScenarioCourbe

    # Frontière des contrats : la vue prudentielle porte sur l'existant en extinction. Une section de
    # collecte nouvelle (contrats futurs, hors frontière) est ignorée.
    if h.get("collecte"):
        h = {k: v for k, v in h.items() if k != "collecte"}
    s2 = h["solvabilite2"]
    c0 = bases.courbe_base(base)
    hausse, baisse = courbes_choquees(c0, s2["choc_taux"])
    credit = cv.credit_valorisation(credit_code, "sans_va", h["horizon_annees"])

    # Choc de spread : perte de la formule standard sur la part non souveraine, par qualité de crédit
    from ..actif import Portefeuille
    p = Portefeuille(h, credit=bases.credit_sur_base(credit, base))
    vm = p.vm_obligations(c0)
    bas, haut = copy.deepcopy(p), copy.deepcopy(p)
    bas.choc_spread(-0.0001)
    haut.choc_spread(0.0001)
    dmod = (bas.vm_obligations(c0) - haut.vm_obligations(c0)) / (0.0002 * vm)
    perte_spread = PART_NON_SOUVERAINE * vm * sum(w * facteur_spread(q, dmod) for q, w in NOTATIONS.items())
    lo, hi = 0.0, 0.3
    for _ in range(60):
        mid = (lo + hi) / 2
        q = copy.deepcopy(p)
        q.choc_spread(mid)
        lo, hi = (mid, hi) if vm - q.vm_obligations(c0) < perte_spread else (lo, mid)
    credit_choque = credit.copie()
    credit_choque.choquer((lo + hi) / 2)

    tirages = {}

    def lancer(cle, hh=h, courbe=None, credit_=credit, **kw):
        options = {k: kw.pop(k) for k in ("choc_rachats", "rachat_massif") if k in kw}
        if courbe is None:
            g, cr = bases.gse(hh, base, credit_, n=n, **kw)
        else:
            g, cr = GSE(hh, courbe=courbe, courbe_avant_choc=c0, n=n, **kw), bases.credit_sur_base(credit_, base)
        r = projeter_stochastique(hh, g, credit=cr, **options)
        if echantillons:
            ps = r["par_scenario"]
            tirages[cle] = {"vm": float(ps["vm_actif_initial"].iloc[0]), "be": ps["be"].to_numpy(), "fdb": ps["fdb"].to_numpy(),
                            "be_garanti": ps["be_garanti"].to_numpy()}
        return r["synthese"]

    h_mort, h_frais = copy.deepcopy(h), copy.deepcopy(h)
    h_mort["passif"]["taux_deces"] *= 1.15
    h_frais["passif"]["frais_gestion_encours"] *= 1.10
    synth = {
        "base": lancer("base"), "taux_hausse": lancer("taux_hausse", courbe=hausse), "taux_baisse": lancer("taux_baisse", courbe=baisse),
        "actions": lancer("actions", choc_actions=s2["choc_actions"]), "spread": lancer("spread", credit_=credit_choque),
        "rachats_hausse": lancer("rachats_hausse", choc_rachats=s2["choc_rachats_hausse"]),
        "rachats_baisse": lancer("rachats_baisse", choc_rachats=s2["choc_rachats_baisse"]),
        "rachat_massif": lancer("rachat_massif", rachat_massif=s2["rachat_massif"]),
        "mortalite": lancer("mortalite", hh=h_mort), "frais": lancer("frais", hh=h_frais),
    }

    # Projection centrale (équivalent certain sur la courbe de la base) : rythme des prestations
    df = projeter(h, ScenarioCourbe("ec", h["horizon_annees"], c0), credit=bases.credit_sur_base(credit, base))
    ppb_adm = ppb_admissible_fonds_excedentaires(h)
    contexte = {"base": base, "credit": credit_code, "n_scenarios": n, "cout_capital": cout_capital, "courbe": c0,
                "ppb_admissible": ppb_adm, "fonds_excedentaires": fonds_excedentaires(ppb_adm, df["prestations"].to_dict(), c0),
                "pm": [float(df["pm"].loc[t]) for t in range(h["horizon_annees"] + 1)], "bilan_initial": copy.deepcopy(h["bilan_initial"]),
                "choc_spread": {"perte_formule_standard": perte_spread, "duration_modifiee": dmod, "part_non_souveraine": PART_NON_SOUVERAINE}}
    sortie = _agreger(synth, contexte)
    if echantillons:
        sortie["_tirages"], sortie["_contexte"] = tirages, contexte
    return sortie


def reagreger(resultat, indices_paires):
    """Indicateurs recalculés sur un rééchantillon de paires antithétiques (j, j + n/2), les mêmes
    paires pour tous les chocs (mêmes scénarios) ; resultat vient de bilan_prudentiel(..., echantillons=True)."""
    moitie = resultat["_contexte"]["n_scenarios"] // 2
    synth = {}
    for k, t in resultat["_tirages"].items():
        paires = {c: (t[c][:moitie] + t[c][moitie:]) / 2 for c in ("be", "fdb", "be_garanti")}
        synth[k] = {"vm_actif_initial": t["vm"], "be": float(paires["be"][indices_paires].mean()), "fdb": float(paires["fdb"][indices_paires].mean()),
                    "be_garanti": float(paires["be_garanti"][indices_paires].mean()), "ic_be": float("nan"), "part_scenarios_avec_apport": float("nan")}
    return _agreger(synth, resultat["_contexte"])


def _agreger(synth, ctx):
    """Du résultat moyen de chaque choc aux indicateurs (SCR, fonds propres, MCR, marge de risque)."""
    fp = {k: s["vm_actif_initial"] - s["be"] for k, s in synth.items()}
    fdb = {k: s["fdb"] for k, s in synth.items()}
    nette = {k: fp["base"] - fp[k] for k in fp if k != "base"}
    brute = {k: nette[k] + fdb["base"] - fdb[k] for k in nette}
    sens_taux = max(("taux_hausse", "taux_baisse"), key=lambda k: nette[k])
    sens_rachat = max(("rachats_hausse", "rachats_baisse", "rachat_massif"), key=lambda k: nette[k])

    def bscr_complet(pertes):
        m = {k: max(pertes[k], 0.0) for k in (sens_taux, "actions", "spread")}
        marche = agreger_marche(m[sens_taux], m["actions"], m["spread"], sens_taux)
        v = {"rachat": max(pertes[sens_rachat], 0.0), "mortalite": max(pertes["mortalite"], 0.0), "frais": max(pertes["frais"], 0.0)}
        vie2 = sum(x * x for x in v.values()) + 2 * sum(rho * v[a] * v[b] for (a, b), rho in CORR_VIE.items())
        vie = math.sqrt(vie2)
        return {"taux": m[sens_taux], "actions": m["actions"], "spread": m["spread"], "marche": marche,
                **v, "vie": vie, "bscr": math.sqrt(marche**2 + vie**2 + 2 * 0.25 * marche * vie)}

    net, brut = bscr_complet(nette), bscr_complet(brute)
    base_s = synth["base"]
    fe, c0 = ctx["fonds_excedentaires"], ctx["courbe"]
    adj_tp = -max(min(brut["bscr"] - net["bscr"], base_s["fdb"] - fe), 0.0)
    op = min(0.3 * brut["bscr"], 0.0045 * base_s["be"])

    # Marge de risque : SCR non couvrable (souscription vie nette et opérationnel), écoulé avec la PM moyenne
    pm = ctx["pm"]
    nh0 = net["vie"] + op
    projetes = [nh0 * pm[t] / pm[0] for t in range(len(pm) - 1)]
    mr = marge_de_risque(projetes, c0, {"cout_du_capital": ctx["cout_capital"], "lambda": None, "plancher_lambda": None})
    mr_2027 = marge_de_risque(projetes, c0, {"cout_du_capital": 0.0475, "lambda": 0.96, "plancher_lambda": 0.5})

    b = ctx["bilan_initial"]
    actif_net = base_s["vm_actif_initial"] - base_s["be"] - mr
    fp_comptables = b["fonds_propres"] + b.get("apport_initial", 0.0) + b["reserve_capitalisation"]
    impots = TAUX_IS * (actif_net - fp_comptables)  # > 0 : passif d'impôt différé
    idp, ida = max(impots, 0.0), max(-impots, 0.0)
    adj_dt = -min(idp, TAUX_IS * max(brut["bscr"] + adj_tp + op, 0.0))
    scr = brut["bscr"] + adj_tp + op + adj_dt
    tier1 = actif_net + fe - idp
    tier3 = min(ida, 0.15 * scr)  # impôts différés actifs : niveau 3, plafonnés à 15 % du SCR, non reconnus au centre
    md = mcr_detail(scr, base_s["be"] - base_s["fdb"], base_s["fdb"] - fe)
    m = md["mcr"]
    return {
        "base": ctx["base"], "credit": ctx["credit"], "n_scenarios": ctx["n_scenarios"],
        "actif": base_s["vm_actif_initial"], "be": base_s["be"], "ic_be": base_s["ic_be"], "fdb": base_s["fdb"],
        "be_garanti": base_s["be_garanti"], "marge_de_risque": mr, "marge_de_risque_2027": mr_2027,
        "fonds_excedentaires": fe, "ppb_admissible": ctx.get("ppb_admissible", b["ppb"]), "ppb_comptable": b["ppb"],
        "impots_differes_passif": idp, "impots_differes_actif_non_reconnus": ida,
        "fonds_propres_niveau_1": tier1, "fonds_propres_niveau_3_si_reconnus": tier3,
        "pertes_nettes": nette, "pertes_brutes": brute, "sens_retenus": {"taux": sens_taux, "rachat": sens_rachat},
        "scr_net": net, "scr_brut": brut, "ajustement_tp": adj_tp, "ajustement_impots_differes": adj_dt,
        "risque_operationnel": op, "scr": scr, "mcr": m, "mcr_detail": md, "fonds_propres_comptables": fp_comptables,
        "actif_net_avant_impots": actif_net, "bscr_brut": brut["bscr"], "bscr_net": net["bscr"],
        "choc_spread": ctx["choc_spread"],
        "indicateur_couverture_scr": tier1 / scr if scr > 0 else float("inf"),
        "indicateur_couverture_scr_avec_ida": (tier1 + tier3) / scr if scr > 0 else float("inf"),
        "indicateur_couverture_scr_sans_fe": (tier1 - fe) / scr if scr > 0 else float("inf"),
        "indicateur_couverture_mcr": tier1 / m,
        "part_scenarios_avec_apport_base": base_s["part_scenarios_avec_apport"],
    }
