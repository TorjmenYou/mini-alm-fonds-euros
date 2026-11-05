"""Projection du passif : un model point épargne euro (étape 2)."""


def taux_rachat_conjoncturel(ecart, p):
    """Loi de rachats conjoncturels proposée par l'ACPR (2013), en paliers.

    ecart = taux servi - taux attendu par l'assuré.
    p : paramètres alpha < beta <= 0 <= gamma < delta, rc_max, rc_min.
    - très en dessous du marché (ecart < alpha) : rachats supplémentaires maximaux ;
    - entre beta et gamma : zone d'indifférence, pas de rachat supplémentaire ;
    - au-dessus du marché : les assurés rachètent moins que d'habitude (rc_min < 0).
    """
    a, b, g, d = p["alpha"], p["beta"], p["gamma"], p["delta"]
    if ecart < a:
        return p["rc_max"]
    if ecart < b:
        return p["rc_max"] * (ecart - b) / (a - b)
    if ecart <= g:
        return 0.0
    if ecart <= d:
        return p["rc_min"] * (ecart - g) / (d - g)
    return p["rc_min"]


def taux_rachat_total(taux_servi_precedent, taux_attendu, h):
    """Rachat structurel + rachat conjoncturel, borné entre 0 et 100 %.

    Le rachat de l'année t dépend du taux servi l'année précédente : c'est ce que
    l'assuré connaît quand il décide. Cela évite aussi une circularité dans la
    boucle (le taux servi de l'année dépend des produits financiers, eux-mêmes
    dépendants des ventes d'actifs pour payer les rachats).
    """
    structurel = h["passif"]["taux_rachat_structurel"]
    conj = taux_rachat_conjoncturel(taux_servi_precedent - taux_attendu, h["rachats_dynamiques"])
    return min(1.0, max(0.0, structurel + conj))


def verifier_probabilite(nom, valeur):
    """Refuse explicitement une probabilité hors de [0, 1]."""
    if not 0.0 <= valeur <= 1.0:
        raise ValueError(f"{nom} doit être une probabilité entre 0 et 1, reçu : {valeur!r}")


def projeter_passif_un_an(pm_debut, taux_servi, taux_deces, taux_rachat):
    """Une année de projection du model point.

    Convention de calendrier : la PM est revalorisée au taux servi, puis les
    sorties sont payées en fin d'année, sur la PM revalorisée.

    Convention de risques concurrents (décès et rachat) :
    - taux_deces est une probabilité de décès « indépendante », lue dans une
      table de mortalité : elle s'applique à tous les assurés ;
    - taux_rachat est un taux de rachat mesuré parmi les assurés en vie (taux
      d'expérience rapporté aux contrats en vigueur) : il s'applique aux survivants.
    D'où : décès = PM_reval x q ; rachats = (PM_reval - décès) x r ;
    PM_fin = PM_reval x (1 - q) x (1 - r), toujours positive ou nulle.
    """
    verifier_probabilite("taux_deces", taux_deces)
    verifier_probabilite("taux_rachat", taux_rachat)
    if pm_debut < 0:
        raise ValueError(f"PM de début d'année négative : {pm_debut!r}")
    if taux_servi <= -1.0:
        raise ValueError(f"Taux servi impossible : {taux_servi!r}")
    interets = pm_debut * taux_servi
    pm_revalorisee = pm_debut + interets
    deces = pm_revalorisee * taux_deces
    rachats = (pm_revalorisee - deces) * taux_rachat
    pm_fin = pm_revalorisee - deces - rachats
    return {
        "pm_debut": pm_debut,
        "interets": interets,
        "deces": deces,
        "rachats": rachats,
        "pm_fin": pm_fin,
    }
