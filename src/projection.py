"""Boucle actif-passif année par année et indicateurs de sortie.

La boucle est la même pour les scénarios déterministes (V1), stochastiques (V2)
et choqués (V3) : seul change le scénario économique qu'on lui donne.
"""

import pandas as pd

from .actif import Portefeuille
from .gse import ScenarioDeterministe
from .passif import projeter_passif_un_an, taux_rachat_total
from .strategie import PPB, decider_taux_servi


def scenario(h, nom="central"):
    """Scénarios déterministes de la V1 : courbe plate, chocs instantanés à l'ouverture."""
    r = h["economie"]["taux_sans_risque"]
    definitions = {
        "central": (0.0, 0.0),
        "hausse_taux_200pb": (+0.02, 0.0),
        "baisse_taux_100pb": (-0.01, 0.0),
        "krach_actions_25pc": (0.0, -0.25),
    }
    choc_taux, choc_actions = definitions[nom]
    return ScenarioDeterministe(nom, h["horizon_annees"], r, r + choc_taux, choc_actions)


def _taux_rachat_choque(taux, choc):
    """Choc de rachat Solvabilité II, appliqué au taux de rachat de chaque année.

    Hausse : +50 % du taux, plafonné à 100 %. Baisse : -50 %, sans baisser de
    plus de 20 points.
    """
    if choc > 0:
        return min(1.0, taux * (1 + choc))
    if choc < 0:
        return max(taux * (1 + choc), taux - 0.20)
    return taux


def projeter(h, eco=None, choc_rachats=0.0, rachat_massif=0.0, detail=True):
    """Projette le fonds euros sur un scénario économique.

    Ordre des opérations dans l'année t (de t-1 à t) :
      1. taux de rachat (structurel + conjoncturel, selon le taux servi en t-1
         et le taux à 10 ans observé en début d'année) ;
      2. revenus financiers : coupons, dividendes, intérêts, remboursements,
         et vente des actions au-delà de leur poids cible ;
      3. stratégie : taux servi, PPB, plus-values actions réalisées ;
      4. passif : revalorisation de la PM, décès, rachats ;
      5. paiement des prestations et des frais, rééquilibrage de l'actif ;
      6. résultat de l'assureur, mise à jour de la PPB et des fonds propres.
    """
    eco = eco or scenario(h)
    p = h["passif"]
    alloc = h["actif"]["allocation_cible"]

    port = Portefeuille(h)
    ppb = PPB(h["bilan_initial"]["ppb"], h["strategie"]["duree_max_ppb_ans"])
    pm = h["bilan_initial"]["pm"]
    fonds_propres = h["bilan_initial"]["fonds_propres"]
    reserve_capi = 0.0
    # Moins-values réalisées non couvertes par la réserve de capitalisation (et
    # plus ou moins-values actions des ventes forcées) : elles passent en
    # résultat financier, donc dans l'assiette de la participation, l'année suivante.
    report = 0.0
    taux_servi_prec = p["taux_servi_initial"]
    # Projection « garantie » en parallèle : mêmes décès et rachats, mais PM
    # revalorisée au seul TMG, sans participation. Sert à isoler les FDB.
    pm_garantie = pm

    c_init = eco.courbe_initiale
    lignes = [{
        "annee": 0, "taux_10ans": c_init.taux_zc(10), "deflateur": 1.0, "pm": pm, "ppb": ppb.stock,
        "reserve_capitalisation": reserve_capi, "fonds_propres": fonds_propres,
        "vnc_actif": port.vnc_totale(), "vm_actif": port.vm_totale(c_init),
        "pmvl_obligations": port.vm_obligations(c_init) - port.vnc_obligations(),
        "pvl_actions": port.pvl_actions(), "taux_servi": taux_servi_prec, "prestations": 0.0, "frais": 0.0,
        "apport_assureur": 0.0, "pm_garantie": pm_garantie, "prestations_garanties": 0.0,
        "ppb_versee_extinction": 0.0,
    }]

    # Chocs instantanés à l'ouverture : actions, puis rachat massif éventuel
    port.choc_actions(eco.choc_actions)
    vm_apres_choc = port.vm_totale(eco.courbe(0))
    if rachat_massif:
        sortie = rachat_massif * pm
        pm -= sortie
        # Rachat total : plus aucun contrat. La PPB restante est versée aux
        # assurés sortants à la même date que leurs rachats (t = 0), comme à
        # l'extinction en cours de projection. Un rachat partiel ne la fait pas
        # sortir : elle reste aux contrats en vigueur.
        ppb_t0 = 0.0
        if pm <= 1e-9:
            ppb_t0 = ppb.stock
            ppb.reprendre(ppb_t0)
            pm = 0.0
        port.payer(sortie + ppb_t0)
        reeq = port.reequilibrer(eco.courbe(0), alloc)
        reserve_capi += reeq["pmv_obligations"]
        report += min(reserve_capi, 0.0) + reeq["pv_actions_reequilibrage"]
        reserve_capi = max(reserve_capi, 0.0)
        fonds_propres += reeq["apport"]
        lignes[0]["prestations"] = sortie + ppb_t0
        lignes[0]["ppb_versee_extinction"] = ppb_t0
        lignes[0]["apport_assureur"] = reeq["apport"]
        lignes[0]["prestations_garanties"] = rachat_massif * pm_garantie
        pm_garantie *= 1 - rachat_massif

    for t in range(1, eco.T + 1):
        courbe_debut, courbe_fin = eco.courbe(t - 1), eco.courbe(t)
        taux_attendu = courbe_debut.taux_zc(10)  # proxy de l'OAT 10 ans
        pm_debut = pm
        vnc_debut = port.vnc_totale()

        # 1. Rachats : l'assuré compare le taux servi l'an dernier au marché
        taux_rachat = _taux_rachat_choque(taux_rachat_total(taux_servi_prec, taux_attendu, h), choc_rachats)

        # 2. Revenus financiers de l'année
        rev = port.encaisser_revenus(courbe_debut, eco.facteur_actions(t))
        pmv_allegement = port.alleger_actions(courbe_fin, alloc)
        produits_courants = (rev["coupons"] + rev["dividendes"] + rev["interets_monetaires"]
                             + pmv_allegement + report)
        report_integre, report = report, 0.0

        # 3. Stratégie de taux servi
        part_provisions = min(1.0, (pm_debut + ppb.stock) / vnc_debut) if vnc_debut > 0 else 1.0
        st = decider_taux_servi(produits_courants, pm_debut, ppb, port.pvl_actions(), taux_attendu, h, part_provisions)
        pv_real = port.realiser_pv_actions(st["pv_actions_realisees"])
        produits_financiers = produits_courants + pv_real
        ppb.reprendre(st["reprise_ppb"])

        # 4. Passif
        ps = projeter_passif_un_an(pm_debut, st["taux_servi"], p["taux_deces"], taux_rachat)
        pg = projeter_passif_un_an(pm_garantie, p["tmg"], p["taux_deces"], taux_rachat)
        pm_garantie = pg["pm_fin"]
        pm = ps["pm_fin"]
        prestations = ps["deces"] + ps["rachats"]
        # Extinction du portefeuille : la PPB restante, qui appartient aux
        # assurés, leur est versée avec les dernières prestations. La dotation
        # décidée pour l'année est versée à la même date : sans contrat, elle
        # ne peut plus être mise en provision pour être redistribuée plus tard.
        ppb_versee, dotation_en_stock = 0.0, st["dotation_ppb"]
        if pm <= 1e-9:
            ppb_versee = ppb.stock + st["dotation_ppb"]
            ppb.reprendre(ppb.stock)
            dotation_en_stock = 0.0
            prestations += ppb_versee
            pm = 0.0
        frais = p["frais_gestion_encours"] * pm_debut

        # 5. Prestations, frais et rééquilibrage
        port.payer(prestations + frais)
        reeq = port.reequilibrer(courbe_fin, alloc)

        # Les plus ou moins-values obligataires réalisées vont à la réserve de
        # capitalisation ; au-delà, la perte est reportée en produits financiers.
        reserve_capi += reeq["pmv_obligations"]
        perte_hors_reserve = min(reserve_capi, 0.0)
        reserve_capi -= perte_hors_reserve
        report = perte_hors_reserve + reeq["pv_actions_reequilibrage"]

        # 6. Résultat de l'assureur : produits financiers - intérêts crédités nets
        #    - mouvement de PPB - frais (les chargements restent à l'assureur)
        interets_nets = st["interets_bruts"] - p["chargements_encours"] * pm_debut
        resultat = (produits_financiers - interets_nets - st["dotation_ppb"] + st["reprise_ppb"] - frais)
        # (la PPB versée à l'extinction sort de la PPB et du bilan, sans toucher
        # au résultat ; la dotation de l'année reste une charge de l'assureur,
        # qu'elle soit mise en provision ou versée tout de suite)
        fonds_propres += resultat + reeq["apport"]
        ppb.vieillir_et_doter(dotation_en_stock)
        taux_servi_prec = st["taux_servi"]

        ligne = {
            "annee": t, "taux_10ans": taux_attendu, "deflateur": eco.deflateur(t),
            "taux_servi": st["taux_servi"], "taux_rachat": taux_rachat,
            "pm": pm, "prestations": prestations, "frais": frais, "ppb": ppb.stock,
            "fonds_propres": fonds_propres, "vm_actif": port.vm_totale(courbe_fin),
            "resultat_assureur": resultat, "apport_assureur": reeq["apport"],
            "pm_garantie": pm_garantie, "prestations_garanties": pg["deces"] + pg["rachats"],
        }
        if detail:
            vnc = port.vnc_totale()
            ligne.update({
                "taux_cible": st["taux_cible"], "deces": ps["deces"], "rachats": ps["rachats"],
                "produits_financiers": produits_financiers,
                "rendement_comptable": produits_financiers / vnc_debut if vnc_debut > 0 else float("nan"),
                "pv_actions_realisees": pv_real, "dotation_ppb": st["dotation_ppb"],
                "reprise_ppb": st["reprise_ppb"],
                "pmv_obligataires_realisees": reeq["pmv_obligations"],
                "reserve_capitalisation": reserve_capi,
                "abandon_marge": st["abandon_marge"], "complement_tmg": st["complement_tmg"],
                "vnc_actif": vnc,
                "pmvl_obligations": port.vm_obligations(courbe_fin) - port.vnc_obligations(),
                "pvl_actions": port.pvl_actions(),
                "vm_obligations": port.vm_obligations(courbe_fin), "vm_actions": port.actions_vm,
                "monetaire": port.monetaire,
                "report_produits_financiers": report_integre, "ppb_versee_extinction": ppb_versee,
                "ecart_bilan": vnc - (pm + ppb.stock + reserve_capi + fonds_propres + report),
            })
        lignes.append(ligne)

    # Fin de projection : les assurés récupèrent leur PM, leur PPB et leur part
    # des plus-values latentes restantes (85 % de la quote-part des provisions)
    vnc_fin = port.vnc_totale()
    part_fin = min(1.0, (pm + ppb.stock) / vnc_fin) if vnc_fin > 0 else 0.0
    pvl_fin = max(port.vm_totale(eco.courbe(eco.T)) - vnc_fin, 0.0)
    lignes[-1]["part_pvl_assures_fin"] = h["strategie"]["participation_minimale"] * part_fin * pvl_fin

    df = pd.DataFrame(lignes).set_index("annee")
    df.attrs["vm_apres_choc"] = vm_apres_choc
    df.attrs["scenario"] = eco.nom
    return df


def indicateurs(df):
    """Valeurs actuelles sur un scénario (déflateurs du scénario).

    - BE = BE des prestations + BE des frais :
        * prestations : décès, rachats, PPB versée à l'extinction, et ce qui
          revient encore aux assurés à l'horizon (PM, PPB, part des plus-values
          latentes) ;
        * frais : frais de gestion de l'assureur ;
    - BE garanti : prestations de la projection « garantie » (mêmes sorties,
      PM revalorisée au seul TMG), plus la PM garantie restante à l'horizon ;
    - FDB = BE des prestations - BE garanti : valeur des prestations futures
      discrétionnaires (participation aux bénéfices), à comportement des
      assurés identique ;
    - fuite : valeur de marché initiale - (sorties actualisées - apports de
      l'assureur actualisés + actif final actualisé). Nulle sur un scénario
      déterministe cohérent avec le marché, nulle en moyenne sur un jeu de
      scénarios stochastiques.
    """
    T = df.index[-1]
    d = df["deflateur"]
    fin = df.loc[T]
    va_prestations = (df["prestations"] * d).sum()
    be_frais = (df["frais"] * d).sum()
    be_prestations = va_prestations + (fin["pm"] + fin["ppb"] + fin["part_pvl_assures_fin"]) * d.loc[T]
    be_garanti = (df["prestations_garanties"] * d).sum() + fin["pm_garantie"] * d.loc[T]
    vm0 = df.attrs["vm_apres_choc"]
    va_apports = (df["apport_assureur"] * d).sum()
    be = be_prestations + be_frais
    return {
        "vm_actif_initial": vm0,
        "be": be,
        "be_prestations": be_prestations,
        "be_frais": be_frais,
        "be_garanti": be_garanti,
        "fdb": be_prestations - be_garanti,
        "valeur_assureur": vm0 - be,
        "fuite": vm0 - (va_prestations + be_frais - va_apports + fin["vm_actif"] * d.loc[T]),
        "va_apports": va_apports,
        "pm_residuelle_pct": fin["pm"] / df.loc[0, "pm"],
    }
