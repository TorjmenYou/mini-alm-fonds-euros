"""Courbes de taux : prix zéro-coupon et taux dérivés.

Toute la projection ne demande à une courbe que des prix zéro-coupon
P(t, t+k), notés zc(k). Le reste s'en déduit :
- taux à 1 an (rémunération du monétaire) ;
- taux à 10 ans (taux attendu par les assurés, proxy de l'OAT 10 ans) ;
- taux de coupon au pair (obligations neuves achetées au pair).
"""

import math
from functools import lru_cache


class Courbe:
    def zc(self, k):
        raise NotImplementedError

    def taux_zc(self, k):
        """Taux actuariel (composé annuellement) de maturité k."""
        return self.zc(k) ** (-1 / k) - 1

    def taux_1an(self):
        return 1 / self.zc(1) - 1

    def taux_pair(self, n):
        """Coupon qui fait coter au pair une obligation de maturité n."""
        return (1 - self.zc(n)) / sum(self.zc(k) for k in range(1, n + 1))


class CourbePlate(Courbe):
    """Courbe plate au taux actuariel r : P(t, t+k) = (1 + r)^-k."""

    def __init__(self, r):
        self.r = r

    def zc(self, k):
        return (1 + self.r) ** (-k)


class CourbeZeroCoupon(Courbe):
    """Courbe donnée par ses taux zéro-coupon actuariels aux maturités 1, 2, ..., K ans.

    Au-delà de la dernière maturité, le dernier taux est prolongé (extrapolation plate).
    """

    def __init__(self, taux):
        self.taux = [float(r) for r in taux]
        if not self.taux:
            raise ValueError("Courbe vide")
        if any(r <= -1 for r in self.taux):
            raise ValueError("Taux zéro-coupon inférieur ou égal à -100 %")
        self._zc = [1.0] + [(1 + r) ** (-k) for k, r in enumerate(self.taux, start=1)]

    @classmethod
    def plate(cls, r, maturite_max=150):
        return cls([r] * maturite_max)

    def taux_maturite(self, k):
        return self.taux[min(int(k), len(self.taux)) - 1]

    def zc(self, k):
        k = int(k)
        if k < len(self._zc):
            return self._zc[k]
        return (1 + self.taux[-1]) ** (-k)


class SpreadCredit:
    """Structure par terme du spread d'un émetteur risqué (V5), en composition continue.

    s(k) est le spread zéro-coupon de maturité k observé en t = 0, au-dessus de la courbe de
    référence (interpolation linéaire entre les points donnés, extrapolation plate). On travaille
    sur le spread cumulé H(u) = s(u) x u : le prix risqué d'un flux de date u vaut
    P_ref(0, u) x exp(-H(u)), et la courbe risquée vue en t vaut P_ref(t, t+k) x exp(-[H(t+k) - H(t)]).
    En risque neutre, H est l'intensité de perte cumulée (défaut x perte en cas de défaut, convention
    de recouvrement en valeur de marché) : c'est elle qui rend le prix de marché cohérent avec les flux.
    """

    def __init__(self, spread):
        if isinstance(spread, dict):
            points = sorted((float(k), float(v)) for k, v in spread.items())
        else:
            points = [(1.0, float(spread))]
        self.points = points
        self.ajustements = []  # fonctions u -> correction additive de H(u)
        self._cache = {}

    def copie(self):
        c = SpreadCredit.__new__(SpreadCredit)
        c.points, c.ajustements, c._cache = list(self.points), list(self.ajustements), dict(self._cache)
        return c

    def s(self, u):
        pts = self.points
        if u <= pts[0][0]:
            return pts[0][1]
        if u >= pts[-1][0]:
            return pts[-1][1]
        for (a, sa), (b, sb) in zip(pts, pts[1:]):
            if a <= u <= b:
                return sa + (u - a) / (b - a) * (sb - sa)

    def H(self, u):
        if u not in self._cache:
            self._cache[u] = self.s(u) * u + sum(f(u) for f in self.ajustements)
        return self._cache[u]

    def choquer(self, choc, date=0):
        """Déplacement parallèle du spread de choc à partir de la date donnée (élargissement si choc > 0)."""
        self.ajustements.append(lambda u, c=float(choc), d=date: c * max(u - d, 0.0))
        self._cache = {}

    def rebaser(self, courbe_marche, courbe_base):
        """Même prix risqué, exprimé au-dessus d'une autre courbe de référence (par exemple avec VA) :
        H'(u) = H(u) + ln P_base(0, u) - ln P_marché(0, u)."""
        self.ajustements.append(lambda u: (math.log(courbe_base.zc(u)) - math.log(courbe_marche.zc(u))) if u > 0 else 0.0)
        self._cache = {}
        return self

    def taux_perte(self, t):
        """Perte attendue en risque neutre de l'année t (de t - 1 à t), en fraction du nominal survivant."""
        return 1 - math.exp(-(self.H(t) - self.H(t - 1)))


class CourbeAvecSpread(Courbe):
    """Courbe d'un émetteur risqué vue en t : P(t, t+k) x exp(-[H(t+k) - H(t)]) (V5).

    spread : SpreadCredit, ou un nombre (spread constant)."""

    def __init__(self, base, spread, t=0):
        self.base, self.t = base, int(t)
        self.credit = spread if isinstance(spread, SpreadCredit) else SpreadCredit(spread)

    def zc(self, k):
        return self.base.zc(k) * math.exp(-(self.credit.H(self.t + k) - self.credit.H(self.t)))


class CourbeForward(Courbe):
    """Courbe vue en t dans un monde déterministe cohérent avec la courbe initiale (V5) :
    P(t, t+k) = P(0, t+k) / P(0, t)."""

    def __init__(self, base, t):
        self.base, self.t = base, int(t)

    def zc(self, k):
        return self.base.zc(self.t + k) / self.base.zc(self.t)


@lru_cache(maxsize=None)
def variance_integrale(a, sigma, duree):
    """V(t, t + duree) : variance de l'intégrale du facteur x entre t et t + duree (Hull-White)."""
    if duree == 0:
        return 0.0
    return sigma**2 / a**2 * (duree + 2 / a * math.exp(-a * duree)
                              - 1 / (2 * a) * math.exp(-2 * a * duree) - 3 / (2 * a))


class CourbeHullWhite(Courbe):
    """Courbe à la date t dans le modèle de Hull-White à un facteur.

    Le taux court s'écrit r(t) = x(t) + phi(t), où x suit un processus
    d'Ornstein-Uhlenbeck (dx = -a x dt + sigma dW, x(0) = 0) et phi(t) est
    choisi pour retrouver exactement la courbe initiale P(0, .). Prix d'un
    zéro-coupon (Brigo et Mercurio, modèle G1++) :

        P(t, T) = P(0, T) / P(0, t) x exp(1/2 [V(t,T) - V(0,T) + V(0,t)] - B(t,T) x(t))

    avec B(t, T) = (1 - exp(-a (T - t))) / a. La courbe initiale peut être plate
    (un taux) ou quelconque (CourbeZeroCoupon, par exemple une courbe choquée).
    """

    def __init__(self, t, x, courbe_initiale, a, sigma):
        if not isinstance(courbe_initiale, Courbe):
            courbe_initiale = CourbeZeroCoupon.plate(courbe_initiale)
        self.t, self.x, self.p0, self.a, self.sigma = t, x, courbe_initiale, a, sigma
        # Taux court instantané (utile pour l'affichage)
        f0 = -math.log(courbe_initiale.zc(t + 1) / courbe_initiale.zc(t))
        self.r = x + f0

    def zc(self, k):
        a, s, t, T = self.a, self.sigma, self.t, self.t + k
        B = (1 - math.exp(-a * k)) / a
        ajustement = 0.5 * (variance_integrale(a, s, k) - variance_integrale(a, s, T) + variance_integrale(a, s, t))
        return self.p0.zc(T) / self.p0.zc(t) * math.exp(ajustement - B * self.x)
