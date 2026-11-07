"""Modèles de crédit de la V5 : forme des pertes risque neutre, à prix de marché inchangés.

Principe (docs/V5_METHODOLOGIE.md, docs/V5_CONVENTIONS.md) : dans la valorisation économique, sans
frictions, l'absence d'arbitrage impose que tout le spread soit un coût risque neutre. Sinon, un
investisseur qui garde le titre jusqu'à l'échéance encaisserait la part « non crédit » sans risque.
Ce qui reste libre, et que ce module paramètre, c'est la forme de ce coût :

- part lissée : perte constatée chaque année et dans chaque scénario (convention de la V5 initiale) ;
- part par saut : défaut d'un bloc d'émetteurs, avec une probabilité risque neutre et un
  recouvrement R en valeur de marché ; les pertes se concentrent sur peu de scénarios.

Pour un bloc et une année, la probabilité de défaut p est choisie pour que le facteur de nominal
moyen soit exactement celui du spread : 1 - p (1 - R) = exp(-dH_saut), donc
p = (1 - exp(-dH_saut)) / (1 - R). Les tirages de défaut sont indépendants des taux : le prix de
chaque obligation, et donc l'absence de valeur créée à l'achat, sont inchangés (tests).

La probabilité p est risque neutre. La perte attendue réelle est un autre paramètre
(src/v5/conventions.py, mesure « trajectoire ») : elle ne sert qu'aux projections en probabilité
réelle, jamais à la valorisation.
"""

import math
from statistics import NormalDist

import numpy as np

from ..courbes import SpreadCredit


class CreditSaut(SpreadCredit):
    """Spread d'un portefeuille obligataire, avec une part de la perte risque neutre par saut.

    part_saut : fraction de H (spread cumulé de marché) traitée par défaut ; le reste est lissé ;
    recouvrement : R, en fraction de la valeur de marché du bloc qui fait défaut ;
    blocs : poids des blocs d'émetteurs qui font défaut ensemble (somme 1) ; après un défaut, la
      valeur recouvrée est réinvestie dans le même portefeuille diversifié (les poids reviennent) ;
    graine : graine des tirages de défaut (indépendants des tirages du générateur de scénarios) ;
    correlation : None, blocs indépendants ; sinon rho d'une copule gaussienne à un facteur : le bloc g
      fait défaut l'année t si racine(rho) Z_t + racine(1 - rho) e_tg < Phi^-1(p_t). La probabilité
      de chaque bloc reste p_t (prix inchangés) ; seule la dépendance entre blocs change ;
    pd_reelle, recouvrement_reel : probabilité de défaut annuelle et recouvrement en probabilité
      réelle, pour les projections de plausibilité (mesure « trajectoire ») ; jamais pour valoriser.

    Le décalage de courbe d'une base de valorisation (VA) est porté par la part lissée : il ne
    change ni l'intensité de défaut, ni le recouvrement.
    """

    def __init__(self, spread, part_saut=1.0, recouvrement=0.4, blocs=(1.0,), graine=2027, horizon=60,
                 correlation=None, pd_reelle=None, recouvrement_reel=None, facteur_pd_reelle=None):
        super().__init__(spread)
        if correlation is not None and not 0.0 <= correlation < 1.0:
            raise ValueError(f"correlation doit être dans [0, 1) : {correlation!r}")
        self.correlation = correlation
        # Probabilité réelle : soit une probabilité annuelle fixe, soit une fraction de la probabilité
        # risque neutre (rapport d'intensités), avec son propre recouvrement.
        self.pd_reelle, self.facteur_pd_reelle = pd_reelle, facteur_pd_reelle
        self.recouvrement_reel = recouvrement if recouvrement_reel is None else recouvrement_reel
        if not 0.0 <= part_saut <= 1.0:
            raise ValueError(f"part_saut doit être entre 0 et 1 : {part_saut!r}")
        if not 0.0 <= recouvrement < 1.0:
            raise ValueError(f"recouvrement doit être dans [0, 1) : {recouvrement!r}")
        if abs(sum(blocs) - 1.0) > 1e-12 or min(blocs) <= 0:
            raise ValueError(f"Les poids des blocs doivent être positifs et sommer à 1 : {blocs!r}")
        self.part_saut, self.recouvrement = float(part_saut), float(recouvrement)
        self.blocs = np.array(blocs, dtype=float)
        self.graine, self.horizon = graine, horizon
        self.ajustements_base = []  # décalages de courbe de base (VA) : part lissée seulement
        self.tirages = None  # uniformes (horizon x nombre de blocs) d'un scénario ; None : perte moyenne

    @classmethod
    def depuis(cls, credit, **options):
        """Même spread de marché qu'un SpreadCredit existant (points et chocs), nouvelle forme de perte."""
        c = cls(dict(credit.points), **options)
        c.ajustements = list(credit.ajustements)
        return c

    def copie(self):
        c = CreditSaut.__new__(CreditSaut)
        c.__dict__.update(self.__dict__)
        c.points, c.ajustements, c.ajustements_base = list(self.points), list(self.ajustements), list(self.ajustements_base)
        c._cache = dict(self._cache)
        c._cache_marche = dict(getattr(self, "_cache_marche", {}))
        return c

    # --- Spread cumulé ---------------------------------------------------------
    def H_marche(self, u):
        """Spread cumulé de marché (points et chocs), hors décalage de base."""
        cache = self.__dict__.setdefault("_cache_marche", {})
        if u not in cache:
            cache[u] = self.s(u) * u + sum(f(u) for f in self.ajustements)
        return cache[u]

    def H(self, u):
        if u not in self._cache:
            self._cache[u] = self.H_marche(u) + sum(f(u) for f in self.ajustements_base)
        return self._cache[u]

    def choquer(self, choc, date=0):
        super().choquer(choc, date)
        self._cache_marche = {}

    def rebaser(self, courbe_marche, courbe_base):
        self.ajustements_base.append(lambda u: (math.log(courbe_base.zc(u)) - math.log(courbe_marche.zc(u))) if u > 0 else 0.0)
        self._cache = {}
        return self

    # --- Pertes -----------------------------------------------------------------
    def increments(self, t):
        """(dH total, dH par saut, dH lissé) de l'année t, de t - 1 à t."""
        d_total = self.H(t) - self.H(t - 1)
        d_saut = self.part_saut * (self.H_marche(t) - self.H_marche(t - 1))
        return d_total, d_saut, d_total - d_saut

    def probabilite_defaut(self, t):
        """Probabilité risque neutre de défaut d'un bloc dans l'année t."""
        _, d_saut, _ = self.increments(t)
        if d_saut <= 0:
            return 0.0
        p = (1 - math.exp(-d_saut)) / (1 - self.recouvrement)
        if p > 1:
            raise ValueError(f"Intensité incompatible avec le recouvrement (p = {p:.3f} > 1) en année {t}")
        return p

    def _defauts(self, t, p):
        """Blocs en défaut l'année t pour une probabilité marginale p (tirages du scénario)."""
        if self.correlation is None:
            return self.tirages[t - 1] < p
        if p <= 0:
            return np.zeros(len(self.blocs), dtype=bool)
        rho = self.correlation
        z, e = self.tirages[t - 1, 0], self.tirages[t - 1, 1:]
        return math.sqrt(rho) * z + math.sqrt(1 - rho) * e < NormalDist().inv_cdf(min(p, 1 - 1e-15))

    def facteur_saut(self, t):
        """Facteur de nominal de l'année t dû aux défauts : tiré si tirages, sinon sa moyenne."""
        _, d_saut, _ = self.increments(t)
        if self.tirages is None or d_saut <= 0:
            return math.exp(-d_saut)
        p = self.probabilite_defaut(t)
        return 1.0 - (1.0 - self.recouvrement) * float(self.blocs[self._defauts(t, p)].sum())

    # --- Probabilité réelle (plausibilité, jamais de valorisation) -------------------------
    def probabilite_defaut_reelle(self, t):
        if self.pd_reelle is not None:
            return self.pd_reelle
        if self.facteur_pd_reelle is not None:
            return self.facteur_pd_reelle * self.probabilite_defaut(t)
        raise ValueError("Aucune probabilité de défaut réelle définie")

    def perte_realisee_reelle(self, t):
        """Fraction du nominal perdue l'année t en probabilité réelle (défauts par bloc, sans part lissée)."""
        p = self.probabilite_defaut_reelle(t)
        if self.tirages is None:
            return p * (1.0 - self.recouvrement_reel)
        return (1.0 - self.recouvrement_reel) * float(self.blocs[self._defauts(t, p)].sum())

    def perte_realisee(self, t):
        """Fraction du nominal survivant perdue dans l'année t (lissée et par saut)."""
        _, _, d_lisse = self.increments(t)
        return 1.0 - math.exp(-d_lisse) * self.facteur_saut(t)

    def pour_scenario(self, j, n):
        """Copie munie des tirages de défaut du scénario j sur n (paires antithétiques j, j + n/2,
        comme le générateur de scénarios)."""
        c = self.copie()
        if self.part_saut > 0 or self.pd_reelle is not None or self.facteur_pd_reelle is not None:
            k = j % (n // 2)
            rng = np.random.default_rng([self.graine, k])
            if self.correlation is None:
                u = rng.random((self.horizon, len(self.blocs)))
                c.tirages = u if j < n // 2 else 1.0 - u
            else:  # facteur commun en colonne 0, facteurs propres ensuite
                z = rng.standard_normal((self.horizon, len(self.blocs) + 1))
                c.tirages = z if j < n // 2 else -z
        return c
