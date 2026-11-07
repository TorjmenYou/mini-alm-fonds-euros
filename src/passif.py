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


def taux_attendu_assures(courbe, h, courbe_obligations=None):
    """Taux auquel l'assuré compare son taux servi (V5 : référence paramétrable).

    Par défaut (V1 à V4) : taux zéro-coupon 10 ans de la courbe sans risque, proxy de l'OAT 10 ans.
    Section facultative « comportement » des hypothèses :
    - reference = "zc10_sans_risque" (défaut), "zc10_obligations" (courbe des obligations
      détenues, référence + spread, fournie par le portefeuille) ou "fixe" (taux_fixe, par exemple un
      taux de livret ou un taux concurrent observé) ;
    - ajustement : écart additif appliqué à la référence (0 par défaut).
    """
    c = h.get("comportement")
    if not c:
        return courbe.taux_zc(10)
    reference = c.get("reference", "zc10_sans_risque")
    if reference == "zc10_sans_risque":
        taux = courbe.taux_zc(10)
    elif reference == "zc10_obligations":
        taux = (courbe_obligations or courbe).taux_zc(10)
    elif reference == "fixe":
        taux = c["taux_fixe"]
    else:
        raise ValueError(f"Référence de taux attendu inconnue : {reference!r}")
    return taux + c.get("ajustement", 0.0)


class ReferenceAssures:
    """Taux de référence des assurés année après année (V5), avec un état si la référence est lissée.

    Sans « reference »: « dynamique » dans la section comportement, délègue à taux_attendu_assures
    (V1 à V4 et premières variantes V5 inchangées). Référence dynamique :
        référence(t) = niveau_initial + beta x (X(t) - X0)
    où X est le moteur de la référence, lu sur la courbe de début d'année :
    - « zc10_sans_risque » : taux zéro-coupon 10 ans sans risque ;
    - « zc10_obligations » : taux zéro-coupon 10 ans de la courbe des obligations détenues ;
    - « lisse » : taux sans risque 10 ans lissé, X(t) = (1 - w) X(t-1) + w zc10(t), rendement
      comptable d'un portefeuille concurrent qui se renouvelle au rythme w (taux servi du marché) ;
    - « livret_a » : taux du livret A, LA(t) = max(plancher, LA0 + part_court x (taux 1 an(t) - taux 1 an initial)),
      formule réglementaire (moyenne de l'€STR et de l'inflation, inflation figée) ; référence(t) =
      niveau_initial + beta x (LA(t) - LA0) ;
    - « fige » : référence constante ;
    - « composite » : moyenne pondérée de composantes, chacune avec son niveau initial (observé),
      son moteur (taux 10 ans sans risque ou taux 1 an), son délai de transmission (lissage w, 1
      si immédiat), son coefficient de réaction beta et un plancher éventuel :
      composante_i(t) = max(plancher_i, niveau_i + beta_i x (X_i lissé(t) - X_i(0))).
    X0 (« valeur_initiale_moteur ») est lu sur la courbe de marché de la base, avant tout choc : un choc
    de taux déplace donc la référence, et une base avec VA ne la change pas.
    """

    def __init__(self, h):
        self.h = h
        c = h.get("comportement") or {}
        self.dynamique = c.get("reference") == "dynamique"
        if self.dynamique:
            self.moteur = c["moteur"]
            if self.moteur not in ("zc10_sans_risque", "zc10_obligations", "lisse", "livret_a", "fige", "composite"):
                raise ValueError(f"Moteur de référence inconnu : {self.moteur!r}")
            if self.moteur == "composite":
                self.composantes = [dict(k) for k in c["composantes"]]
                if abs(sum(k["poids"] for k in self.composantes) - 1.0) > 1e-12:
                    raise ValueError("Les poids des composantes de la référence doivent sommer à 1")
                for k in self.composantes:
                    if k["moteur"] not in ("zc10_sans_risque", "taux_1an"):
                        raise ValueError(f"Moteur de composante inconnu : {k['moteur']!r}")
                    k["etat"] = k["valeur_initiale_moteur"]
            self.niveau = c["niveau_initial"]
            self.beta = c.get("beta", 1.0)
            self.x0 = c.get("valeur_initiale_moteur", 0.0)
            self.w = c.get("lissage", 0.0)
            self.etat = self.x0
            self.la0, self.plancher, self.part_court = c.get("livret_a_initial"), c.get("plancher", 0.005), c.get("part_court", 0.5)

    def taux(self, courbe, courbe_obligations=None):
        if not self.dynamique:
            return taux_attendu_assures(courbe, self.h, courbe_obligations)
        m = self.moteur
        if m == "fige":
            return self.niveau
        if m == "composite":
            total = 0.0
            for k in self.composantes:
                x = courbe.taux_zc(10) if k["moteur"] == "zc10_sans_risque" else courbe.taux_1an()
                w = k.get("lissage", 1.0)
                k["etat"] = (1 - w) * k["etat"] + w * x
                v = k["niveau_initial"] + k.get("beta", 1.0) * (k["etat"] - k["valeur_initiale_moteur"])
                total += k["poids"] * max(k.get("plancher", -1.0), v)
            return total
        if m == "zc10_sans_risque":
            x = courbe.taux_zc(10)
        elif m == "zc10_obligations":
            x = (courbe_obligations or courbe).taux_zc(10)
        elif m == "lisse":
            self.etat = (1 - self.w) * self.etat + self.w * courbe.taux_zc(10)
            x = self.etat
        else:  # livret_a
            la = max(self.plancher, self.la0 + self.part_court * (courbe.taux_1an() - self.x0))
            return self.niveau + self.beta * (la - self.la0)
        return self.niveau + self.beta * (x - self.x0)


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


def reaction_collecte(ecart, c):
    """V5 : facteur de collecte g(e) appliqué à c0 x PM (data/v5/collecte/collecte.json).

    e = taux servi sur les contrats nouveaux l'an dernier - référence des assurés. g = 1 dans une zone
    neutre de demi-largeur zone_neutre autour de e0 ; au-delà, linéaire de pente eta par point de taux
    (1 point = 0,01), mesurée depuis le bord de la zone, puis encadrée entre g_min et g_max.
    eta = 0 : collecte indépendante du taux servi relatif (g = 1).
    """
    d = ecart - c.get("e0", 0.0)
    z = c.get("zone_neutre", 0.0)
    if abs(d) <= z:
        return 1.0
    d = d - z if d > 0 else d + z
    return min(c.get("g_max", 2.0), max(c.get("g_min", 0.0), 1.0 + c["eta"] * d / 0.01))


def repartir_taux_servi(interets_nets, ensembles):
    """V5 : répartit l'intérêt crédité net de chargements entre des ensembles de contrats d'un même fonds.

    ensembles : liste de (PM de début d'année, TMG). Chaque ensemble reçoit max(x, son TMG), avec le même
    x pour tous, tel que la somme des intérêts crédités soit égale à interets_nets. Suppose interets_nets
    au moins égal à la somme des PM x TMG (le plancher de TMG du fonds le garantit) : sinon, erreur, car
    aucune répartition ne conserverait l'intérêt. Renvoie (x, taux par ensemble). Sans PM, x vaut 0.
    """
    total = sum(pm for pm, _ in ensembles)
    if total <= 0:
        return 0.0, [0.0 for _ in ensembles]
    garanti = sum(pm * tmg for pm, tmg in ensembles)
    if interets_nets < garanti - 1e-9 * max(1.0, abs(garanti)):
        raise ValueError(f"Intérêt crédité ({interets_nets!r}) inférieur à la somme des garanties ({garanti!r})")
    # x est cherché par paliers : les ensembles dont le TMG dépasse x reçoivent leur TMG, les autres x
    tmgs = sorted({tmg for _, tmg in ensembles}, reverse=True)
    for k, seuil in enumerate(tmgs + [float("-inf")]):
        au_tmg = [(pm, tmg) for pm, tmg in ensembles if tmg > seuil]
        libres = total - sum(pm for pm, _ in au_tmg)
        if libres <= 0:
            continue
        x = (interets_nets - sum(pm * tmg for pm, tmg in au_tmg)) / libres
        if x >= seuil - 1e-10:  # tolérance d'arrondi quand le plancher de TMG du fonds est juste atteint
            x = max(x, seuil) if seuil > float("-inf") else x
            return x, [max(x, tmg) for _, tmg in ensembles]
    raise AssertionError("répartition du taux servi introuvable")  # inaccessible si l'intérêt couvre les garanties


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
