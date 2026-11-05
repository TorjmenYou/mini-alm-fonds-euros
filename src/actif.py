"""Projection du portefeuille : obligations, actions, monétaire (étape 3).

Chaque actif est suivi en valeur nette comptable (VNC, ce qui compte pour les
produits financiers et la participation aux bénéfices) et en valeur de marché
(VM, ce qui compte pour la richesse latente et la valorisation).
"""

from dataclasses import dataclass


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


class Portefeuille:
    def __init__(self, h):
        repartition_vnc = {
            classe: poids * (h["bilan_initial"]["pm"] + h["bilan_initial"]["ppb"] + h["bilan_initial"]["fonds_propres"])
            for classe, poids in h["actif"]["allocation_cible"].items()
        }
        a = h["actif"]
        n = a["echelle_maturites_ans"]
        # Échelle obligataire : n lignes de même nominal, maturités 1 à n ans
        self.obligations = [
            LigneObligataire(repartition_vnc["obligations"] / n, a["coupon_obligations_initiales"], m, repartition_vnc["obligations"] / n)
            for m in range(1, n + 1)
        ]
        self.actions_vnc = repartition_vnc["actions"]
        self.actions_vm = repartition_vnc["actions"] * (1 + a["pvl_initiale_actions"])
        self.monetaire = repartition_vnc["monetaire"]  # VNC = VM, y compris la trésorerie
        self.dividende = h["economie"]["rendement_dividende_actions"]
        self.maturite_reinvestissement = a["maturite_reinvestissement_ans"]

    # --- Lecture ---------------------------------------------------------
    def vm_obligations(self, courbe):
        return sum(l.valeur_marche(courbe) for l in self.obligations)

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

        if vm_obl > 0 and vm_obl > cible_obligations + 1e-9:
            part = min(1.0, (vm_obl - max(cible_obligations, 0.0)) / vm_obl)
            for ligne in self.obligations:
                vm_ligne = ligne.valeur_marche(courbe)
                pmv_obligations += part * (vm_ligne - ligne.vnc)
                self.monetaire += part * vm_ligne
                ligne.nominal *= 1 - part
                ligne.vnc *= 1 - part
            self.obligations = [l for l in self.obligations if l.nominal > 1e-12]
        elif vm_obl < cible_obligations - 1e-9:
            achat = cible_obligations - vm_obl
            n = self.maturite_reinvestissement
            self.obligations.append(LigneObligataire(achat, courbe.taux_pair(n), n, achat))
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
