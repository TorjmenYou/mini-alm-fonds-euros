"""Bases de valorisation de la V5.

- « sans_va » (base économique, par défaut) : courbe sans risque EIOPA de base. Le générateur de
  scénarios est calé sur elle, les engagements sont actualisés avec elle, et tout actif acheté à son
  prix de marché a une valeur actuelle nette nulle.
- « avec_va » (base réglementaire, sensibilité) : courbe EIOPA avec correction pour volatilité
  (directive 2009/138/CE, art. 77 quinquies ; application soumise à l'accord du superviseur).
  Comme dans la pratique de place, le générateur est calé sur la courbe avec VA ; les actifs restent
  à leur prix de marché (le spread des obligations est réexprimé au-dessus de la courbe avec VA).
  La baisse du BE qui en résulte est un effet réglementaire : elle n'est jamais présentée comme
  de la valeur économique créée.
"""

from ..courbes import SpreadCredit
from ..gse import GSE
from .courbes_marche import courbe_eiopa
from .scenarios import ScenarioCourbe

BASES = ("sans_va", "avec_va")
DATE_COURBE = "20261031"


def courbe_base(base, date=DATE_COURBE):
    if base not in BASES:
        raise ValueError(f"Base de valorisation inconnue : {base!r}")
    return courbe_eiopa(date, avec_va=(base == "avec_va"))


def credit_sur_base(credit, base, date=DATE_COURBE):
    """Spread des obligations détenues, défini au-dessus de la courbe sans VA (prix de marché),
    réexprimé au-dessus de la courbe de la base pour conserver les mêmes prix de marché."""
    credit = credit.copie() if credit is not None else SpreadCredit(0.0)
    if base == "sans_va":
        return credit
    return credit.rebaser(courbe_eiopa(date), courbe_base(base, date))


def equivalent_certain(h, base="sans_va", credit=None, date=DATE_COURBE, nom=None):
    """Scénario déterministe sur les forwards de la courbe de la base, et spread réexprimé."""
    c = courbe_base(base, date)
    return ScenarioCourbe(nom or f"equivalent_certain_{base}", h["horizon_annees"], c), credit_sur_base(credit, base, date)


def gse(h, base="sans_va", credit=None, date=DATE_COURBE, **options):
    """Générateur de scénarios calé sur la courbe de la base, et spread réexprimé."""
    c = courbe_base(base, date)
    return GSE(h, courbe=c, courbe_avant_choc=c, **options), credit_sur_base(credit, base, date)
