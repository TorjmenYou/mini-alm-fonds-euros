"""Projection du portefeuille : obligations, actions, monétaire (étape 3).

Chaque actif est suivi en valeur nette comptable (VNC, ce qui compte pour les
produits financiers et la participation aux bénéfices) et en valeur de marché
(VM, ce qui compte pour la richesse latente et la valorisation).
"""

from dataclasses import dataclass

from .courbes import CourbeAvecSpread, SpreadCredit


@dataclass
class LigneObligataire:
    """Obligation à taux fixe, achetée au pair (VNC = nominal)."""

    nominal: float
    coupon: float
    maturite: int  # années restantes
    vnc: float

    def valeur_marche(self, courbe):
        """Valeur actuelle des flux restants, actualisés sur la courbe de taux."""
        coupons = sum(self.coupon * self.nominal * courbe.zc(k) for k in range(1, self.maturite + 1))
        return coupons + self.nominal * courbe.zc(self.maturite)

    def valeur_marche_zc(self, zc):
        """Même calcul, sur des prix zéro-coupon déjà calculés (zc[k] pour k = 1, 2, ...) : mêmes opérations,
        dans le même ordre, donc le même résultat au bit près."""
        coupons = sum(self.coupon * self.nominal * zc[k] for k in range(1, self.maturite + 1))
        return coupons + self.nominal * zc[self.maturite]


class Portefeuille:
    def __init__(self, h, credit=None):
        b = h["bilan_initial"]
        total = b["pm"] + b["ppb"] + b["fonds_propres"] + b.get("reserve_capitalisation", 0.0)
        a = h["actif"]
        # V5 : le portefeuille d'ouverture suit l'allocation initiale du profil ; une stratégie peut fixer
        # une autre allocation cible, atteinte ensuite par les rééquilibrages (bilan initial identique).
        repartition_vnc = {classe: poids * total for classe, poids in a.get("allocation_initiale", a["allocation_cible"]).items()}
        if "lignes_obligataires" in a:
            # V5 : portefeuille historique lu ligne par ligne (titres achetés au pair, VNC = nominal).
            # Les actions suivent leur poids cible ; le monétaire complète l'actif comptable.
            self.obligations = []
            for l in a["lignes_obligataires"]:
                vnc = l.get("vnc", l["nominal"])
                if abs(vnc - l["nominal"]) > 1e-9 or l["maturite"] < 1 or l["nominal"] < 0:
                    raise ValueError(f"Ligne obligataire non prise en charge (achat au pair, maturité >= 1 an) : {l}")
                self.obligations.append(LigneObligataire(float(l["nominal"]), float(l["coupon"]), int(l["maturite"]), float(vnc)))
            repartition_vnc["monetaire"] = total - self.vnc_obligations() - repartition_vnc["actions"]
            if repartition_vnc["monetaire"] < -1e-9:
                raise ValueError("Les lignes obligataires et les actions dépassent l'actif comptable initial")
        else:
            n = a["echelle_maturites_ans"]
            # Échelle obligataire : n lignes de même nominal, maturités 1 à n ans
            self.obligations = [
                LigneObligataire(repartition_vnc["obligations"] / n, a["coupon_obligations_initiales"], m, repartition_vnc["obligations"] / n)
                for m in range(1, n + 1)
            ]
        self.actions_vnc = repartition_vnc["actions"]
        self.actions_vm = repartition_vnc["actions"] * (1 + a["pvl_initiale_actions"])
        self.monetaire = repartition_vnc["monetaire"]  # VNC = VM, y compris la trésorerie
        # V5 : apport de capital initial, versé en trésorerie (aucune plus-value créée, actifs existants inchangés)
        self.monetaire += float(b.get("apport_initial", 0.0))
        # V5 : échelle de réinvestissement {maturité: poids} ; par défaut, une seule maturité
        self.echelle = {int(k): float(v) for k, v in (a.get("echelle_reinvestissement") or {}).items()}
        self.dividende = h["economie"]["rendement_dividende_actions"]
        self.maturite_reinvestissement = a["maturite_reinvestissement_ans"]
        # V5 : obligations d'émetteurs risqués valorisées sur la courbe de référence + spread.
        # Deux mesures, jamais mélangées (docs/V5_METHODOLOGIE.md) :
        # - « risque_neutre » (valorisation) : la perte constatée chaque année est l'intensité de perte
        #   risque neutre tirée du spread, si bien qu'un titre acheté à son prix de marché a une valeur
        #   actuelle nette nulle ; c'est la seule mesure qui autorise un calcul de valeur ;
        # - « trajectoire » (projection comptable) : la perte constatée est la perte attendue réelle,
        #   paramètre explicite ; le reste du spread est une prime de risque, pas de la valeur créée.
        c = a.get("credit")
        self.credit = credit.copie() if credit is not None else (SpreadCredit(c["spread"]) if c else None)
        self.mesure = (c or {}).get("mesure", "risque_neutre")
        if self.mesure not in ("risque_neutre", "trajectoire"):
            raise ValueError(f"Mesure de crédit inconnue : {self.mesure!r}")
        self.perte_reelle = float((c or {}).get("perte_attendue_reelle", 0.0))
        # Projection en probabilité réelle à spreads figés : la courbe des obligations vue en t reste
        # celle de t = 0 (pas de spread à terme), comme les taux du scénario réel (V5).
        self.spreads_figes = bool((c or {}).get("spreads_figes", False))
        if self.spreads_figes and self.mesure != "trajectoire":
            raise ValueError("Les spreads figés ne sont permis qu'en mesure « trajectoire » (aucune valorisation)")
        self.annee = 0

    def courbe_obligations(self, courbe):
        """Courbe de valorisation des obligations : la courbe de référence, ou la courbe risquée vue en t (V5)."""
        if self.credit is None:
            return courbe
        return CourbeAvecSpread(courbe, self.credit, 0 if self.spreads_figes else self.annee)

    def taux_perte_credit(self):
        """Fraction du nominal perdue sur l'année en cours (V5)."""
        if self.credit is None:
            return 0.0
        if self.mesure == "trajectoire":
            if getattr(self.credit, "pd_reelle", None) is not None or getattr(self.credit, "facteur_pd_reelle", None) is not None:
                return self.credit.perte_realisee_reelle(self.annee)  # V5 : défauts réels par bloc
            return self.perte_reelle
        if hasattr(self.credit, "perte_realisee"):  # V5 : part de la perte par saut (src/v5/credit.py)
            return self.credit.perte_realisee(self.annee)
        return self.credit.taux_perte(self.annee)

    def choc_spread(self, choc):
        """Élargissement instantané du spread à la date courante (V5) : revalorise les obligations détenues."""
        if self.credit is None:
            self.credit = SpreadCredit(0.0)
        self.credit.choquer(choc, self.annee)

    # --- Lecture ---------------------------------------------------------
    def _zc_obligations(self, courbe):
        """Prix zéro-coupon de la courbe de valorisation des obligations, calculés une fois par appel."""
        c = self.courbe_obligations(courbe)
        m = max((l.maturite for l in self.obligations), default=0)
        return [1.0] + [c.zc(k) for k in range(1, m + 1)]

    def vm_obligations(self, courbe):
        zc = self._zc_obligations(courbe)
        return sum(l.valeur_marche_zc(zc) for l in self.obligations)

    def vnc_obligations(self):
        return sum(l.vnc for l in self.obligations)

    def vnc_totale(self):
        return self.vnc_obligations() + self.actions_vnc + self.monetaire

    def vm_totale(self, courbe):
        return self.vm_obligations(courbe) + self.actions_vm + self.monetaire

    def pvl_actions(self):
        """Plus-values latentes actions, mobilisables pour servir un taux."""
        return max(self.actions_vm - self.actions_vnc, 0.0)

    # --- Événements de l'année -------------------------------------------
    def choc_actions(self, choc):
        """Choc instantané sur la valeur de marché des actions (ex. -0,25)."""
        self.actions_vm *= 1 + choc

    def encaisser_revenus(self, courbe_debut, rendement_actions):
        """Coupons, dividendes, intérêts monétaires et remboursements de l'année.

        Tout est encaissé en trésorerie (poche monétaire). Renvoie les revenus
        comptables, qui forment les produits financiers de l'année.

        - le monétaire rapporte le taux à 1 an observé en début d'année ;
        - les actions ont un rendement total donné par le scénario : facteur
          G = valeur de fin, dividende compris / valeur de début. Le dividende
          vaut d x valeur de début, plafonné à la valeur totale de fin G x valeur
          de début ; le reste est la valeur ex-dividende du cours. Dividende +
          cours = G x valeur de début dans tous les cas, et le cours n'est
          jamais négatif. Le plafond ne joue que si G < d (perte de plus de
          98 % avec d = 2 %). Un facteur négatif (perte de plus de 100 %) est
          refusé.
        """
        if rendement_actions < 0:
            raise ValueError(f"facteur de rendement total des actions négatif ({rendement_actions}) : "
                             "perte de plus de 100 %, impossible pour une action")
        interets_monetaires = self.monetaire * courbe_debut.taux_1an()
        valeur_fin = self.actions_vm * rendement_actions
        dividendes = min(self.actions_vm * self.dividende, valeur_fin)
        self.actions_vm = valeur_fin - dividendes

        # V5 : pertes de crédit de l'année, constatées avant le paiement des coupons
        self.annee += 1
        pertes_credit, taux_perte = 0.0, self.taux_perte_credit()
        if taux_perte:
            for ligne in self.obligations:
                pertes_credit += ligne.vnc * taux_perte
                ligne.nominal *= 1 - taux_perte
                ligne.vnc *= 1 - taux_perte

        coupons, remboursements = 0.0, 0.0
        restantes = []
        for ligne in self.obligations:
            coupons += ligne.coupon * ligne.nominal
            ligne.maturite -= 1
            if ligne.maturite == 0:
                remboursements += ligne.nominal  # remboursée au pair : pas de plus ou moins-value
            else:
                restantes.append(ligne)
        self.obligations = restantes

        self.monetaire += interets_monetaires + dividendes + coupons + remboursements
        return {
            "coupons": coupons,
            "dividendes": dividendes,
            "interets_monetaires": interets_monetaires,
            "remboursements": remboursements,
            "pertes_credit": pertes_credit,
        }

    def alleger_actions(self, courbe, allocation):
        """Ramène les actions à leur poids cible si elles le dépassent.

        Fait après l'encaissement des revenus de l'année et avant le choix du
        taux servi : la plus ou moins-value réalisée entre dans les produits
        financiers de l'année.
        """
        cible = allocation["actions"] * self.vm_totale(courbe)
        if self.actions_vm <= cible or self.actions_vm <= 0:
            return 0.0
        part = (self.actions_vm - cible) / self.actions_vm
        pmv = part * (self.actions_vm - self.actions_vnc)
        self.monetaire += part * self.actions_vm
        self.actions_vm *= 1 - part
        self.actions_vnc *= 1 - part
        return pmv

    def realiser_pv_actions(self, montant):
        """Réalise des plus-values actions (vente puis rachat des mêmes titres).

        La VM ne change pas, la VNC monte : la plus-value passe des latentes
        aux produits financiers de l'année.
        """
        montant = min(montant, self.pvl_actions())
        self.actions_vnc += montant
        return montant

    def payer(self, montant):
        self.monetaire -= montant

    def vendre_coupons_bas(self, courbe, part):
        """V5 : vend, au prix de marché, une part de la VNC obligataire en commençant par les plus petits
        coupons (repositionnement). Renvoie la plus ou moins-value réalisée ; le produit va en trésorerie."""
        a_vendre = part * self.vnc_obligations()
        zc = self._zc_obligations(courbe)
        pmv = 0.0
        for ligne in sorted(self.obligations, key=lambda l: (l.coupon, -l.maturite)):
            if a_vendre <= 1e-12:
                break
            q = min(1.0, a_vendre / ligne.vnc) if ligne.vnc > 0 else 0.0
            vm = ligne.valeur_marche_zc(zc)
            pmv += q * (vm - ligne.vnc)
            self.monetaire += q * vm
            a_vendre -= q * ligne.vnc
            ligne.nominal *= 1 - q
            ligne.vnc *= 1 - q
        self.obligations = [l for l in self.obligations if l.nominal > 1e-12]
        return pmv

    def reequilibrer(self, courbe, allocation):
        """Ramène le portefeuille vers l'allocation cible, en valeur de marché.

        - actions : on complète si elles sont sous la cible (l'excédent éventuel
          est vendu l'année suivante, avant le choix du taux servi : voir alleger_actions) ;
        - monétaire : ramené à sa cible ;
        - obligations : on vend au prorata de chaque ligne si besoin de liquidité
          (plus ou moins-values réalisées, renvoyées pour la réserve de
          capitalisation), ou on achète une obligation neuve au pair, au taux du marché
          (coupon au pair de la courbe du moment).
        Règle de liquidité : les prestations sont toujours payées. Si, après la
        vente de toutes les obligations puis des actions nécessaires, la
        trésorerie reste négative, l'assureur apporte le capital manquant
        (« apport ») : la trésorerie revient à zéro et l'apport est renvoyé pour
        être enregistré en fonds propres. Aucun emprunt implicite ne subsiste.

        Renvoie les plus ou moins-values réalisées et l'apport éventuel.
        """
        total = self.vm_totale(courbe)
        pmv_obligations, pv_actions = 0.0, 0.0

        cible_actions = allocation["actions"] * total
        if self.actions_vm < cible_actions:
            achat = cible_actions - self.actions_vm
            self.actions_vm += achat
            self.actions_vnc += achat
            self.monetaire -= achat

        cible_monetaire = allocation["monetaire"] * total
        cible_obligations = total - self.actions_vm - cible_monetaire
        vm_obl = self.vm_obligations(courbe)

        courbe_obl = self.courbe_obligations(courbe)
        if vm_obl > 0 and vm_obl > cible_obligations + 1e-9:
            part = min(1.0, (vm_obl - max(cible_obligations, 0.0)) / vm_obl)
            zc = self._zc_obligations(courbe)
            for ligne in self.obligations:
                vm_ligne = ligne.valeur_marche_zc(zc)
                pmv_obligations += part * (vm_ligne - ligne.vnc)
                self.monetaire += part * vm_ligne
                ligne.nominal *= 1 - part
                ligne.vnc *= 1 - part
            self.obligations = [l for l in self.obligations if l.nominal > 1e-12]
        elif vm_obl < cible_obligations - 1e-9:
            achat = cible_obligations - vm_obl
            for n, poids in (self.echelle.items() if self.echelle else [(self.maturite_reinvestissement, 1.0)]):
                self.obligations.append(LigneObligataire(poids * achat, courbe_obl.taux_pair(n), n, poids * achat))
            self.monetaire -= achat

        # Cas extrême : plus assez d'obligations pour couvrir les sorties
        if self.monetaire < 0 and self.actions_vm > 0:
            part = min(1.0, -self.monetaire / self.actions_vm)
            pv_actions = part * (self.actions_vm - self.actions_vnc)
            self.monetaire += part * self.actions_vm
            self.actions_vm *= 1 - part
            self.actions_vnc *= 1 - part

        # Actif épuisé : apport de capital de l'assureur
        apport = 0.0
        if self.monetaire < -1e-9:
            apport = -self.monetaire
        if self.monetaire < 0:
            self.monetaire = 0.0

        return {"pmv_obligations": pmv_obligations, "pv_actions_reequilibrage": pv_actions, "apport": apport}
