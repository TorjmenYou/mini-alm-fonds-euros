"""Générateur de scénarios économiques (étape V2).

Un scénario économique fournit, pour chaque année t de 0 à T :
- courbe(t) : la courbe des taux en t (prix zéro-coupon) ;
- facteur_actions(t) : le rendement total des actions sur l'année t (de t-1 à t) ;
- deflateur(t) : le facteur d'actualisation stochastique D(t), avec D(0) = 1.

Taux : Hull-White à un facteur, calé exactement sur la courbe initiale
(plate par défaut, ou quelconque, par exemple une courbe choquée).
Actions : rendement log-normal, de tendance le taux court (monde risque neutre).
La simulation est exacte au pas annuel : on tire conjointement le facteur de
taux x(t+1) et son intégrale sur l'année, ce qui donne un déflateur sans biais
de discrétisation (seule reste l'erreur de Monte-Carlo).
"""

import math

import numpy as np

from .courbes import CourbeHullWhite, CourbePlate, CourbeZeroCoupon, variance_integrale


class ScenarioDeterministe:
    """Scénario à courbe plate (V1) : tous les actifs rapportent r."""

    def __init__(self, nom, T, r_avant_choc, r, choc_actions=0.0):
        self.nom, self.T, self.choc_actions = nom, T, choc_actions
        self.courbe_initiale = CourbePlate(r_avant_choc)
        self._courbe = CourbePlate(r)
        self.r = r

    def courbe(self, t):
        return self._courbe

    def facteur_actions(self, t):
        return 1 + self.r

    def deflateur(self, t):
        return (1 + self.r) ** (-t)


class ScenarioStochastique:
    """Une trajectoire du GSE (vue sur les tableaux simulés)."""

    def __init__(self, gse, j):
        self.gse, self.j = gse, j
        self.nom, self.T, self.choc_actions = f"{gse.nom}#{j}", gse.T, gse.choc_actions
        self.courbe_initiale = gse.courbe_avant_choc

    def courbe(self, t):
        g = self.gse
        return CourbeHullWhite(t, g.x[self.j, t], g.courbe0, g.a, g.sigma)

    def facteur_actions(self, t):
        return self.gse.rendements_actions[self.j, t]

    def deflateur(self, t):
        return self.gse.deflateurs[self.j, t]


class GSE:
    """Simule n trajectoires de taux (Hull-White) et d'actions."""

    def __init__(self, h, r0=None, nom="stochastique", choc_actions=0.0, n=None, graine=None, courbe=None,
                 courbe_avant_choc=None):
        """r0 : taux plat de la courbe initiale (par défaut celui des hypothèses) ;
        courbe : courbe initiale quelconque, prioritaire sur r0 ;
        courbe_avant_choc : courbe de l'ouverture avant un éventuel choc (V5 : courbe de marché),
        par défaut la courbe plate des hypothèses."""
        g = h["gse"]
        self.nom, self.T, self.choc_actions = nom, h["horizon_annees"], choc_actions
        self.courbe_avant_choc = (courbe_avant_choc if courbe_avant_choc is not None
                                  else CourbeZeroCoupon.plate(h["economie"]["taux_sans_risque"]))
        if courbe is not None:
            self.courbe0 = courbe
        else:
            self.courbe0 = CourbeZeroCoupon.plate(h["economie"]["taux_sans_risque"] if r0 is None else r0)
        self.a, self.sigma, self.vol_actions = g["hw_a"], g["hw_sigma"], g["vol_actions"]
        self.n = n or g["nb_scenarios"]
        assert self.n % 2 == 0, "Nombre de scénarios pair (variables antithétiques)"
        self._simuler(graine if graine is not None else g["graine"])

    def _simuler(self, graine):
        a, s, sa, T, n = self.a, self.sigma, self.vol_actions, self.T, self.n
        p0 = self.courbe0.zc
        V0 = lambda t: variance_integrale(a, s, t)
        rng = np.random.default_rng(graine)
        z = rng.standard_normal((n // 2, T, 3))
        z = np.concatenate([z, -z])  # variables antithétiques

        # Lois conjointes de (x(t+1), intégrale de x sur [t, t+1]) sur un pas d'un an
        e1, e2 = math.exp(-a), math.exp(-2 * a)
        B1 = (1 - e1) / a
        var_x = s**2 * (1 - e2) / (2 * a)
        var_i = s**2 / a**2 * (1 - 2 * B1 + (1 - e2) / (2 * a))
        cov = s**2 / (2 * a**2) * (1 - e1) ** 2
        chol = np.linalg.cholesky(np.array([[var_x, cov], [cov, var_i]]))

        self.x = np.zeros((n, T + 1))
        self.deflateurs = np.ones((n, T + 1))
        self.rendements_actions = np.ones((n, T + 1))
        for t in range(T):
            eps = z[:, t, :2] @ chol.T
            integrale_x = self.x[:, t] * B1 + eps[:, 1]
            self.x[:, t + 1] = self.x[:, t] * e1 + eps[:, 0]
            # Intégrale de phi sur [t, t+1] : elle garantit E[D(t)] = P(0, t)
            integrale_phi = math.log(p0(t) / p0(t + 1)) + 0.5 * (V0(t + 1) - V0(t))
            taux_cumule = integrale_phi + integrale_x
            self.deflateurs[:, t + 1] = self.deflateurs[:, t] * np.exp(-taux_cumule)
            self.rendements_actions[:, t + 1] = np.exp(taux_cumule - sa**2 / 2 + sa * z[:, t, 2])

    def scenarios(self):
        return [ScenarioStochastique(self, j) for j in range(self.n)]

    def test_martingale(self, maturite_obligation=10):
        """Moyennes actualisées : elles doivent valoir 1 à l'erreur de Monte-Carlo près.

        - zéro-coupon de maturité t : E[D(t)] / P(0, t) ;
        - zéro-coupon de maturité t + 10 détenu jusqu'en t, puis revendu au prix
          du modèle : E[D(t) x P(t, t+10)] / P(0, t+10). Valide la formule de
          prix des obligations utilisée pour valoriser le portefeuille ;
        - indice actions (dividendes réinvestis) : E[D(t) x S(t)] / S(0).
        Renvoie les ratios et la demi-largeur de l'intervalle de confiance à 95 %.
        """
        t = np.arange(self.T + 1)
        m = maturite_obligation
        p0 = np.vectorize(self.courbe0.zc)
        zc = self.deflateurs / p0(t)
        prix = np.array([[CourbeHullWhite(u, self.x[j, u], self.courbe0, self.a, self.sigma).zc(m)
                          for u in t] for j in range(self.n)])
        obligation = self.deflateurs * prix / p0(t + m)
        actions = self.deflateurs * np.cumprod(self.rendements_actions, axis=1)
        return {
            "annee": t,
            "zero_coupon": zc.mean(axis=0), "ic_zero_coupon": demi_intervalle(zc),
            "obligation": obligation.mean(axis=0), "ic_obligation": demi_intervalle(obligation),
            "actions": actions.mean(axis=0), "ic_actions": demi_intervalle(actions),
        }


def demi_intervalle(valeurs):
    """Demi-largeur de l'intervalle de confiance à 95 % d'une moyenne Monte-Carlo.

    Avec des variables antithétiques, les tirages j et j + n/2 ne sont pas
    indépendants : l'écart-type se calcule sur les n/2 moyennes de paires.
    Fonctionne sur un vecteur (n,) ou un tableau (n, T).
    """
    v = np.asarray(valeurs, dtype=float)
    moitie = v.shape[0] // 2
    paires = (v[:moitie] + v[moitie:]) / 2
    return 1.96 * paires.std(axis=0, ddof=1) / math.sqrt(moitie)
