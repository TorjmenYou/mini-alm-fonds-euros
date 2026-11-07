"""Scénarios de la V5."""

import math

from ..courbes import CourbeForward


class ScenarioCourbe:
    """Scénario déterministe cohérent avec une courbe initiale quelconque (équivalent certain, V5).

    Les taux futurs sont les taux forward de la courbe initiale (après choc éventuel) :
    courbe(t) = P(0, t+.) / P(0, t), déflateur D(t) = P(0, t), actions au taux forward à 1 an.
    Sur une courbe plate, il coïncide avec le ScenarioDeterministe de la V1.
    """

    def __init__(self, nom, T, courbe, courbe_avant_choc=None, choc_actions=0.0):
        self.nom, self.T, self.choc_actions = nom, T, choc_actions
        self._courbe0 = courbe
        self.courbe_initiale = courbe_avant_choc if courbe_avant_choc is not None else courbe

    def courbe(self, t):
        return CourbeForward(self._courbe0, t)

    def facteur_actions(self, t):
        return self._courbe0.zc(t - 1) / self._courbe0.zc(t)

    def deflateur(self, t):
        return self._courbe0.zc(t)


class ScenarioReel:
    """Trajectoire centrale en probabilité réelle (V5), pour la plausibilité des projections.

    Hypothèse de marche aléatoire : la courbe des taux reste celle de l'ouverture (pas de taux
    forward), et les actions rapportent le taux à 1 an plus une prime de risque actions. Aucune
    valorisation n'est permise sur ce scénario : il se combine avec la mesure de crédit
    « trajectoire » (pertes attendues réelles), pour laquelle indicateurs() refuse tout calcul de valeur.
    """

    mesure = "reelle"

    def __init__(self, nom, T, courbe, prime_actions=0.0, choc_actions=0.0):
        self.nom, self.T, self.choc_actions = nom, T, choc_actions
        self._courbe0 = self.courbe_initiale = courbe
        self.prime_actions = prime_actions

    def courbe(self, t):
        return self._courbe0

    def facteur_actions(self, t):
        return 1 / self._courbe0.zc(1) + self.prime_actions

    def deflateur(self, t):
        return float("nan")  # pas d'actualisation en probabilité réelle


class ScenarioReelStochastique:
    """Scénario stochastique en probabilité réelle (V5) : taux du générateur, actions avec prime de risque.

    Hypothèses : prime de terme nulle (les taux suivent la dynamique du générateur, dont la tendance est
    celle des forwards EIOPA, quasi plats) ; rendement des actions = rendement du générateur x exp(prime).
    Aucune actualisation : ce scénario sert aux distributions réelles (apports, liquidité), jamais à valoriser.
    """

    mesure = "reelle"

    def __init__(self, scenario, prime_actions=0.0):
        self.s, self.prime = scenario, prime_actions
        self.nom, self.T, self.choc_actions = f"reel_{scenario.nom}", scenario.T, scenario.choc_actions
        self.courbe_initiale = scenario.courbe_initiale

    def courbe(self, t):
        return self.s.courbe(t)

    def facteur_actions(self, t):
        return self.s.facteur_actions(t) * math.exp(self.prime)

    def deflateur(self, t):
        return float("nan")
