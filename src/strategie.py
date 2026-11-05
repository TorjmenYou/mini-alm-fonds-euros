"""Stratégie de taux servi : participation aux bénéfices, PPB, plus-values (étape 4)."""


class PPB:
    """Provision pour participation aux bénéfices, suivie par génération.

    Chaque dotation doit être redistribuée aux assurés sous 8 ans : on garde
    donc les montants par année de dotation (generations[0] = la plus ancienne,
    à reprendre obligatoirement cette année).
    """

    def __init__(self, montant_initial, duree_max):
        # Hypothèse : le stock initial est réparti uniformément sur les 8 générations
        self.generations = [montant_initial / duree_max] * duree_max

    @property
    def stock(self):
        return sum(self.generations)

    def reprise_obligatoire(self):
        return self.generations[0]

    def reprendre(self, montant):
        """Reprise FIFO : on consomme d'abord les dotations les plus anciennes."""
        reste = montant
        for i, g in enumerate(self.generations):
            pris = min(g, reste)
            self.generations[i] -= pris
            reste -= pris
            if reste <= 1e-12:
                break

    def vieillir_et_doter(self, dotation):
        """Fin d'année : la génération la plus ancienne sort, la dotation entre."""
        assert self.generations[0] < 1e-9, "La génération de plus de 8 ans aurait dû être reprise"
        self.generations = self.generations[1:] + [dotation]


def decider_taux_servi(produits_financiers, pm, ppb, pvl_actions, taux_attendu, h, part_provisions=1.0):
    """Fixe le taux servi de l'année et les mouvements de PPB.

    Raisonnement en intérêts « bruts de chargements » : l'assureur crédite
    (taux servi + chargements) x PM, puis prélève ses chargements sur encours.

    Seule la quote-part des produits financiers afférente aux provisions
    techniques (part_provisions = (PM + PPB) / actif en VNC) entre dans la
    participation : les revenus des actifs qui représentent les fonds propres
    restent à l'assureur.

    1. Planchers : la reprise obligatoire de la PPB (dotations de 8 ans) et la
       participation minimale (85 % des produits financiers).
    2. Si ces planchers suffisent à servir le taux cible, l'excédent de
       participation est doté à la PPB, dans la limite d'un plafond (en % de la
       PM) ; au-delà, il est servi tout de suite.
    3. Sinon, on comble l'écart dans cet ordre : reprise de PPB (plafonnée),
       réalisation de plus-values actions, abandon d'une partie de la marge de
       l'assureur.
    4. Le taux servi ne descend jamais sous le TMG : l'assureur paie la différence.
    """
    p, s = h["passif"], h["strategie"]
    chg = p["chargements_encours"]
    taux_cible = max(p["tmg"], taux_attendu + s["ecart_taux_cible"])
    if pm <= 0:
        # Plus aucun contrat : rien à créditer. La PPB restante est versée à
        # l'extinction du portefeuille (voir projection.projeter).
        return {"taux_cible": taux_cible, "taux_servi": 0.0, "interets_bruts": 0.0, "reprise_ppb": 0.0,
                "dotation_ppb": 0.0, "pv_actions_realisees": 0.0, "abandon_marge": 0.0, "complement_tmg": 0.0}
    besoin = (taux_cible + chg) * pm

    reprise_obligatoire = ppb.reprise_obligatoire()
    taux_pb = s["participation_minimale"] * part_provisions
    pb_minimale = taux_pb * max(produits_financiers, 0.0)

    interets = reprise_obligatoire
    reprise, dotation, pv_realisees, abandon_marge = reprise_obligatoire, 0.0, 0.0, 0.0

    if interets + pb_minimale >= besoin:
        part_creditee = max(besoin - interets, 0.0)
        interets += part_creditee
        dotation = pb_minimale - part_creditee
        # Au-delà du plafond de PPB, l'excédent est servi tout de suite aux assurés
        stock_apres = ppb.stock - reprise_obligatoire + dotation
        excedent = min(dotation, max(stock_apres - s["plafond_ppb_pct_pm"] * pm, 0.0))
        dotation -= excedent
        interets += excedent
    else:
        interets += pb_minimale
        manque = besoin - interets

        # a. Reprise de PPB, plafonnée à une fraction du stock restant
        stock_restant = ppb.stock - reprise_obligatoire
        reprise_vol = min(manque, s["reprise_ppb_max_par_an"] * stock_restant)
        reprise += reprise_vol
        interets += reprise_vol
        manque -= reprise_vol

        # b. Réalisation de plus-values actions (les assurés en reçoivent leur part)
        if manque > 0 and taux_pb > 0:
            pv_realisees = min(manque / taux_pb, pvl_actions)
            interets += taux_pb * pv_realisees
            manque -= taux_pb * pv_realisees

        # c. L'assureur renonce à tout ou partie de sa marge sur les produits
        #    financiers des provisions (15 % de leur quote-part)
        if manque > 0 and s["abandon_marge_assureur"]:
            marge = (1 - s["participation_minimale"]) * part_provisions * max(produits_financiers + pv_realisees, 0.0)
            abandon_marge = min(manque, marge)
            interets += abandon_marge

    # Plancher du TMG, financé par l'assureur (désactivable pour mesurer son coût)
    complement_tmg = 0.0
    if s.get("appliquer_plancher_tmg", True):
        plancher = (p["tmg"] + chg) * pm
        complement_tmg = max(plancher - interets, 0.0)
        interets += complement_tmg

    taux_servi = interets / pm - chg if pm > 0 else 0.0
    return {
        "taux_cible": taux_cible,
        "taux_servi": taux_servi,
        "interets_bruts": interets,
        "reprise_ppb": reprise,
        "dotation_ppb": dotation,
        "pv_actions_realisees": pv_realisees,
        "abandon_marge": abandon_marge,
        "complement_tmg": complement_tmg,
    }
