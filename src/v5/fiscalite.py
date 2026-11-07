"""Impôt sur les sociétés de la V5 (option activée par défaut dans les métriques de valeur).

Règles en vigueur pour les exercices 2026 et suivants, telles que modélisées :
- taux normal de 25 % (CGI, art. 219, I) ; le taux réduit de 15 % ne concerne que les entreprises
  de moins de 10 M EUR de chiffre d'affaires, jamais un assureur-vie de la taille des profils ;
- contribution sociale de 3,3 % de l'impôt diminué d'un abattement de 763 000 EUR par période de
  douze mois (CGI, art. 235 ter ZC), dont sont exonérées les entreprises de moins de 7 630 000 EUR
  de chiffre d'affaires détenues à 75 % au moins par des personnes physiques ;
- la contribution exceptionnelle sur les bénéfices des grandes entreprises (loi de finances pour 2025,
  art. 48, prorogée par la loi de finances pour 2026, art. 12) ne vise que les deux premiers exercices
  clos à compter du 31/12/2025 : elle ne s'applique pas aux exercices projetés, ouverts après le 31/10/2026.
  Une reconduction envisagée par le projet de loi de finances pour 2027 n'est pas modélisée (texte non adopté).
- déficits reportables en avant (CGI, art. 209, I) : imputation plafonnée à 1 M EUR, majoré de 50 %
  du bénéfice qui excède ce montant ; pas de report en arrière (option non retenue).

Les montants du modèle sont en unités fictives : unite_monetaire_eur convertit une unité en euros,
pour appliquer les seuils exprimés en euros (abattement, plafond d'imputation, chiffre d'affaires).
"""

TAUX_NORMAL = 0.25
TAUX_CONTRIBUTION_SOCIALE = 0.033
ABATTEMENT_CONTRIBUTION_SOCIALE_EUR = 763_000
SEUIL_CA_CONTRIBUTION_SOCIALE_EUR = 7_630_000
PLAFOND_IMPUTATION_DEFICITS_EUR = 1_000_000


def impot_annuel(resultat, chiffre_affaires, deficit_reportable, unite_monetaire_eur,
                 exoneration_pme_possible=False):
    """Impôt d'un exercice de douze mois, en unités du modèle.

    resultat : résultat fiscal de l'exercice (avant imputation des déficits) ;
    chiffre_affaires : pour le seuil d'exonération de la contribution sociale ;
    deficit_reportable : stock de déficits antérieurs (positif) ;
    exoneration_pme_possible : vrai seulement si la condition de détention du capital par des
    personnes physiques est remplie (jamais pour les profils de la V5).
    Renvoie (impot_total, impot_societes, contribution_sociale, nouveau_deficit_reportable).
    """
    u = unite_monetaire_eur
    if resultat <= 0:
        return 0.0, 0.0, 0.0, deficit_reportable - resultat
    plafond = PLAFOND_IMPUTATION_DEFICITS_EUR / u + 0.5 * max(resultat - PLAFOND_IMPUTATION_DEFICITS_EUR / u, 0.0)
    imputation = min(deficit_reportable, resultat, plafond)
    base = resultat - imputation
    impot_societes = TAUX_NORMAL * base
    exonere = exoneration_pme_possible and chiffre_affaires * u < SEUIL_CA_CONTRIBUTION_SOCIALE_EUR
    contribution = 0.0 if exonere else TAUX_CONTRIBUTION_SOCIALE * max(impot_societes - ABATTEMENT_CONTRIBUTION_SOCIALE_EUR / u, 0.0)
    return impot_societes + contribution, impot_societes, contribution, deficit_reportable - imputation
