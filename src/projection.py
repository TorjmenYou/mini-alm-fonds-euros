"""Boucle actif-passif année par année et indicateurs de sortie.

La boucle est la même pour les scénarios déterministes (V1), stochastiques (V2)
et choqués (V3) : seul change le scénario économique qu'on lui donne.
"""

import pandas as pd

from .actif import Portefeuille
from .gse import ScenarioDeterministe
from .passif import ReferenceAssures, projeter_passif_un_an, reaction_collecte, repartir_taux_servi, taux_rachat_total
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


def projeter(h, eco=None, choc_rachats=0.0, rachat_massif=0.0, detail=True, credit=None):
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

    port = Portefeuille(h, credit=credit)
    reference = ReferenceAssures(h)  # taux de référence des assurés (V5 : éventuellement lissé)
    ppb = PPB(h["bilan_initial"]["ppb"], h["strategie"]["duree_max_ppb_ans"])
    pm = h["bilan_initial"]["pm"]
    fonds_propres = h["bilan_initial"]["fonds_propres"] + h["bilan_initial"].get("apport_initial", 0.0)  # V5 : apport initial
    reserve_capi = h["bilan_initial"].get("reserve_capitalisation", 0.0)
    # Moins-values réalisées non couvertes par la réserve de capitalisation (et
    # plus ou moins-values actions des ventes forcées) : elles passent en
    # résultat financier, donc dans l'assiette de la participation, l'année suivante.
    report = 0.0
    # V5 : politique de distribution (facultative). Les fonds propres comptables au-delà d'une cible en %
    # de la PM sont déclarés en dividende en fin d'année (en totalité, ou pour une part si une partie est
    # retenue) et versés l'année suivante avec les prestations.
    distribution = (h.get("strategie_alm") or {}).get("distribution")
    dividende_a_payer = 0.0
    taux_servi_prec = p["taux_servi_initial"]
    # Projection « garantie » en parallèle : mêmes décès et rachats, mais PM
    # revalorisée au seul TMG, sans participation. Sert à isoler les FDB.
    pm_garantie = pm
    # V5 : collecte nouvelle facultative (data/v5/collecte, docs/V5_SPECIFICATION_COLLECTE.md). Deux
    # ensembles de contrats suivis séparément : l'existant (pm_e) et les contrats nouveaux (pm_n).
    # Mode « mutualise » : un seul fonds (actif, PPB, participation), pm = pm_e + pm_n. Mode
    # « cantonne_sans_risque » (cas neutre des tests) : contrats nouveaux crédités au taux sans risque du
    # scénario, sur un compte séparé, sans chargement, frais ni garantie ; le fonds n'est pas modifié.
    collecte = h.get("collecte")
    cantonne = bool(collecte) and collecte.get("mode", "mutualise") == "cantonne_sans_risque"
    if collecte:
        cn = collecte["contrats_nouveaux"]
        if cantonne and (cn["chargement_prime"] or cn["frais_acquisition_prime"]):
            raise ValueError("Mode cantonné (cas neutre) : chargement sur prime et frais d'acquisition doivent être nuls")
        pm_e, pm_n = pm, 0.0
        taux_servi_prec_n = taux_servi_prec  # taux servi l'an dernier sur les contrats nouveaux (publié)

    c_init = eco.courbe_initiale
    lignes = [{
        "annee": 0, "taux_10ans": c_init.taux_zc(10), "deflateur": 1.0, "pm": pm, "ppb": ppb.stock,
        "reserve_capitalisation": reserve_capi, "fonds_propres": fonds_propres,
        "vnc_actif": port.vnc_totale(), "vm_actif": port.vm_totale(c_init),
        "pmvl_obligations": port.vm_obligations(c_init) - port.vnc_obligations(),
        "pvl_actions": port.pvl_actions(), "taux_servi": taux_servi_prec, "prestations": 0.0, "frais": 0.0,
        "apport_assureur": 0.0, "dividendes": 0.0, "pm_garantie": pm_garantie, "prestations_garanties": 0.0,
        "ppb_versee_extinction": 0.0,
    }]

    # Chocs instantanés à l'ouverture : actions, puis rachat massif éventuel
    port.choc_actions(eco.choc_actions)
    vm_apres_choc = port.vm_totale(eco.courbe(0))
    # V5 : repositionnement obligataire à l'ouverture (vente des plus petits coupons, rachat au prix du
    # marché par le rééquilibrage). La moins-value réalisée passe par la réserve de capitalisation,
    # puis, au-delà, par le résultat financier de l'année 1 ; la valeur de marché est inchangée.
    repositionnement = (h.get("strategie_alm") or {}).get("repositionnement")
    if repositionnement:
        pmv_rep = port.vendre_coupons_bas(eco.courbe(0), repositionnement["part"])
        reeq = port.reequilibrer(eco.courbe(0), alloc)
        reserve_capi += pmv_rep + reeq["pmv_obligations"]
        report += min(reserve_capi, 0.0)
        reserve_capi = max(reserve_capi, 0.0)
        lignes[0]["pmv_repositionnement"] = pmv_rep
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

    if collecte:
        pm_e = pm  # après un éventuel rachat massif à l'ouverture

    for t in range(1, eco.T + 1):
        courbe_debut, courbe_fin = eco.courbe(t - 1), eco.courbe(t)
        taux_attendu = reference.taux(courbe_debut, port.courbe_obligations(courbe_debut))  # défaut : zéro-coupon 10 ans
        pm_debut = pm
        vnc_debut = port.vnc_totale()

        # 1. Rachats : l'assuré compare le taux servi l'an dernier au marché
        taux_rachat = _taux_rachat_choque(taux_rachat_total(taux_servi_prec, taux_attendu, h), choc_rachats)
        if collecte:
            pm_e_debut, pm_n_debut = pm_e, pm_n
            taux_rachat_n = _taux_rachat_choque(taux_rachat_total(taux_servi_prec_n, taux_attendu, h), choc_rachats)
            ecart_collecte = taux_servi_prec_n - taux_attendu
            g = reaction_collecte(ecart_collecte, collecte)
            prime = collecte["c0"] * (pm_debut + (pm_n_debut if cantonne else 0.0)) * g if t <= collecte["horizon_collecte_ans"] else 0.0

        # 2. Revenus financiers de l'année
        rev = port.encaisser_revenus(courbe_debut, eco.facteur_actions(t))
        pmv_allegement = port.alleger_actions(courbe_fin, alloc)
        produits_courants = (rev["coupons"] + rev["dividendes"] + rev["interets_monetaires"]
                             + pmv_allegement + report - rev["pertes_credit"])
        report_integre, report = report, 0.0

        # 3. Stratégie de taux servi
        part_provisions = min(1.0, (pm_debut + ppb.stock) / vnc_debut) if vnc_debut > 0 else 1.0
        hd = h
        if collecte and not cantonne and pm_n_debut > 0:
            # TMG moyen du fonds, pondéré par les PM : le plancher porte sur la somme des garanties
            hd = dict(h, passif=dict(p, tmg=(pm_e_debut * p["tmg"] + pm_n_debut * cn["tmg"]) / pm_debut))
        st = decider_taux_servi(produits_courants, pm_debut, ppb, port.pvl_actions(), taux_attendu, hd, part_provisions)
        pv_real = port.realiser_pv_actions(st["pv_actions_realisees"])
        produits_financiers = produits_courants + pv_real
        ppb.reprendre(st["reprise_ppb"])

        # 4. Passif
        frais_acquisition = 0.0
        if collecte and not cantonne:
            # Intérêt crédité réparti entre l'existant et les contrats nouveaux : max(x, TMG de l'ensemble)
            if pm_n_debut > 0 and h["strategie"].get("appliquer_plancher_tmg", True):
                _, (ts_e, ts_n) = repartir_taux_servi(st["interets_bruts"] - p["chargements_encours"] * pm_debut,
                                                      [(pm_e_debut, p["tmg"]), (pm_n_debut, cn["tmg"])])
            else:
                ts_e = ts_n = st["taux_servi"]
            ps_e = projeter_passif_un_an(pm_e_debut, ts_e, p["taux_deces"], taux_rachat)
            ps_n = projeter_passif_un_an(pm_n_debut, ts_n, p["taux_deces"], taux_rachat_n)
            ps = {k: ps_e[k] + ps_n[k] for k in ("interets", "deces", "rachats", "pm_fin")}
            # Primes de fin d'année : la PM des contrats nouveaux reçoit la prime nette du chargement
            pm_e, pm_n = ps_e["pm_fin"], ps_n["pm_fin"] + prime * (1 - cn["chargement_prime"])
            ps["pm_fin"] = pm_e + pm_n
            prestations_n, frais_acquisition = ps_n["deces"] + ps_n["rachats"], cn["frais_acquisition_prime"] * prime
        else:
            ps = projeter_passif_un_an(pm_debut, st["taux_servi"], p["taux_deces"], taux_rachat)
        if cantonne:
            # Cas neutre : taux sans risque du scénario (celui des déflateurs), compte séparé égal à la PM
            taux_sans_risque = eco.deflateur(t - 1) / eco.deflateur(t) - 1
            ps_n = projeter_passif_un_an(pm_n_debut, taux_sans_risque, p["taux_deces"], taux_rachat_n)
            pm_n = ps_n["pm_fin"] + prime
            prestations_n, ts_n = ps_n["deces"] + ps_n["rachats"], taux_sans_risque
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
            if collecte and not cantonne:
                pm_e = pm_n = 0.0
        frais = p["frais_gestion_encours"] * pm_debut + frais_acquisition

        # 5. Prestations, frais et rééquilibrage
        dividende_verse, dividende_a_payer = dividende_a_payer, 0.0
        port.payer(prestations + frais + dividende_verse - (prime if collecte and not cantonne else 0.0))
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
        if collecte and not cantonne:
            resultat += cn["chargement_prime"] * prime  # part de la prime non portée en PM
        # (la PPB versée à l'extinction sort de la PPB et du bilan, sans toucher
        # au résultat ; la dotation de l'année reste une charge de l'assureur,
        # qu'elle soit mise en provision ou versée tout de suite)
        fonds_propres += resultat + reeq["apport"]
        if distribution:
            excedent = fonds_propres - distribution["fonds_propres_pct_pm"] * pm
            if excedent > 0:
                dividende_a_payer = distribution.get("part_distribuee", 1.0) * excedent  # < 1 : rétention d'une partie
                fonds_propres -= dividende_a_payer
        ppb.vieillir_et_doter(dotation_en_stock)
        taux_servi_prec = st["taux_servi"]
        if collecte:
            if not cantonne:
                taux_servi_prec = ts_e
            taux_servi_prec_n = ts_n

        ligne = {
            "annee": t, "taux_10ans": taux_attendu, "deflateur": eco.deflateur(t),
            "taux_servi": st["taux_servi"], "taux_rachat": taux_rachat,
            "pm": pm, "prestations": prestations, "frais": frais, "ppb": ppb.stock,
            "fonds_propres": fonds_propres, "vm_actif": port.vm_totale(courbe_fin),
            "resultat_assureur": resultat, "apport_assureur": reeq["apport"],
            "dividendes": dividende_verse, "dividende_a_payer": dividende_a_payer,
            "pm_garantie": pm_garantie, "prestations_garanties": pg["deces"] + pg["rachats"],
        }
        if collecte:
            # Contrats nouveaux : primes, prestations, frais d'encours et d'acquisition, PM ; en mode
            # mutualisé, ces montants sont compris dans les colonnes du fonds (« dont »). La PPB versée à une
        # éventuelle extinction n'est pas répartie entre les deux ensembles (cas non rencontré, négligeable).
            frais_n = (0.0 if cantonne else p["frais_gestion_encours"] * pm_n_debut + frais_acquisition)
            ligne.update({"primes": prime, "facteur_collecte": g, "ecart_collecte": ecart_collecte,
                          "pm_nouveaux": pm_n, "pm_existant": pm - (0.0 if cantonne else pm_n),
                          "prestations_nouveaux": prestations_n, "frais_nouveaux": frais_n,
                          "taux_servi_existant": taux_servi_prec, "taux_servi_nouveaux": ts_n,
                          "taux_rachat_nouveaux": taux_rachat_n})
            if not cantonne and pm_n_debut > 0:
                ligne["taux_rachat"] = (pm_e_debut * taux_rachat + pm_n_debut * taux_rachat_n) / pm_debut
        if detail:
            vnc = port.vnc_totale()
            ligne.update({
                "taux_cible": st["taux_cible"], "deces": ps["deces"], "rachats": ps["rachats"],
                "produits_financiers": produits_financiers, "pertes_credit": rev["pertes_credit"],
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
                "ecart_bilan": vnc - (pm + ppb.stock + reserve_capi + fonds_propres + report + dividende_a_payer),
            })
        lignes.append(ligne)

    # Fin de projection : les assurés récupèrent leur PM, leur PPB et leur part
    # des plus-values latentes restantes (85 % de la quote-part des provisions)
    vnc_fin = port.vnc_totale()
    part_fin = min(1.0, (pm + ppb.stock) / vnc_fin) if vnc_fin > 0 else 0.0
    pvl_fin = max(port.vm_totale(eco.courbe(eco.T)) - vnc_fin, 0.0)
    lignes[-1]["part_pvl_assures_fin"] = h["strategie"]["participation_minimale"] * part_fin * pvl_fin

    if collecte:
        lignes[0].update({"primes": 0.0, "facteur_collecte": float("nan"), "ecart_collecte": float("nan"), "pm_nouveaux": 0.0,
                          "pm_existant": lignes[0]["pm"], "prestations_nouveaux": 0.0, "frais_nouveaux": 0.0,
                          "taux_servi_existant": lignes[0]["taux_servi"], "taux_servi_nouveaux": lignes[0]["taux_servi"],
                          "taux_rachat_nouveaux": float("nan")})
    df = pd.DataFrame(lignes).set_index("annee")
    if collecte:
        df.attrs["collecte"] = "cantonnee" if cantonne else "mutualisee"
    df.attrs["vm_apres_choc"] = vm_apres_choc
    df.attrs["scenario"] = eco.nom
    df.attrs["mesure"] = port.mesure
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
    if df.attrs.get("mesure", "risque_neutre") != "risque_neutre":
        raise ValueError("Projection en mesure « trajectoire » (pertes de crédit réelles) : aucune valorisation "
                         "n'est permise, la prime de risque du spread serait comptée comme de la valeur.")
    T = df.index[-1]
    d = df["deflateur"]
    fin = df.loc[T]
    va_prestations = (df["prestations"] * d).sum()
    be_frais = (df["frais"] * d).sum()
    be_prestations = va_prestations + (fin["pm"] + fin["ppb"] + fin["part_pvl_assures_fin"]) * d.loc[T]
    be_garanti = (df["prestations_garanties"] * d).sum() + fin["pm_garantie"] * d.loc[T]
    vm0 = df.attrs["vm_apres_choc"]
    va_apports = (df["apport_assureur"] * d).sum()
    va_dividendes = (df["dividendes"] * d).sum() if "dividendes" in df else 0.0  # V5 : versés pendant la projection
    be = be_prestations + be_frais
    collecte = {}
    if "primes" in df:
        # V5 : collecte nouvelle. Valeur pour l'actionnaire = actif initial + VA des primes - BE de tous les
        # contrats. BE des contrats nouveaux : leurs prestations, frais d'encours et d'acquisition, leur PM
        # finale et leur part (au prorata des PM) de la PPB et des plus-values latentes finales.
        cantonnee = df.attrs.get("collecte") == "cantonnee"
        va_primes = (df["primes"] * d).sum()
        part_n = 0.0 if cantonnee or fin["pm"] <= 0 else fin["pm_nouveaux"] / fin["pm"]
        be_prestations_n = ((df["prestations_nouveaux"] * d).sum()
                            + (fin["pm_nouveaux"] + part_n * (fin["ppb"] + fin["part_pvl_assures_fin"])) * d.loc[T])
        be_n = be_prestations_n + (df["frais_nouveaux"] * d).sum()
        if cantonnee:  # compte séparé : hors du fonds, ajouté aux flux et à l'actif final
            va_prestations += (df["prestations_nouveaux"] * d).sum()
            vm_final_hors_fonds = fin["pm_nouveaux"]
            be_existant, be_prestations_e, be = be, be_prestations, be + be_n
        else:
            vm_final_hors_fonds = 0.0
            be_existant, be_prestations_e = be - be_n, be_prestations - be_prestations_n
        # va_primes_moins_be_nouveaux : flux des contrats nouveaux dans le fonds ; seul, il n'isole pas les
        # transferts entre générations d'assurés (ils déplacent aussi le BE de l'existant, en sens inverse)
        collecte = {"va_primes": va_primes, "be_nouveaux": be_n, "be_existant": be_existant,
                    "va_primes_moins_be_nouveaux": va_primes - be_n}
        vm_final = fin["vm_actif"] + vm_final_hors_fonds
        valeur = vm0 + va_primes - be
        fuite = vm0 + va_primes - (va_prestations + (df["frais"] * d).sum() + va_dividendes - va_apports + vm_final * d.loc[T])
        fdb = be_prestations_e - be_garanti
    else:
        valeur = vm0 - be
        fuite = vm0 - (va_prestations + be_frais + va_dividendes - va_apports + fin["vm_actif"] * d.loc[T])
        fdb = be_prestations - be_garanti
    return {
        "vm_actif_initial": vm0,
        "be": be,
        "be_prestations": be_prestations,
        "be_frais": be_frais,
        "be_garanti": be_garanti,
        "fdb": fdb,
        "valeur_assureur": valeur,
        "fuite": fuite,
        "va_apports": va_apports,
        "va_dividendes": va_dividendes,
        "pm_residuelle_pct": fin["pm"] / df.loc[0, "pm"],
        **collecte,
    }
