"""Variantes de convention de l'audit actuariel de la V5 (docs/V5_AUDIT_CONVENTIONS.md).

Convention de référence de la V5.1 : participation aux résultats avec sa composante technique (compte de
participation simplifié, data/v5/profils/profils.json, rubrique commun.participation_technique), impôt
calculé après coup et déduit de la valeur. Chaque variante modifie une copie des hypothèses.

- « pb_financiere_seule » : convention de la V5.0 publiée le 07/11/2026 ; la participation minimale ne porte
  que sur les produits financiers (85 % de leur quote-part), l'assureur garde tout le solde technique
  (chargements - frais). Sert à la comparaison avant/après, sur les mêmes scénarios.
- « impot_projete » : l'impôt de chaque exercice est calculé dans la projection (mêmes règles que
  src/v5/fiscalite.py, déficits reportables compris), déduit des fonds propres avant la distribution et
  payé par l'actif en fin d'année ; la valeur déduit l'impôt payé, une seule fois.

Composante technique (src/strategie.py, participation_technique) : lecture simplifiée de l'article
A.132-11, I, et de l'article A.132-12 du code des assurances. Solde technique = chargements prélevés -
frais de gestion et d'acquisition ; l'assureur garde 10 % du solde créditeur ; un solde débiteur entre en
totalité au compte et le solde débiteur du compte est reporté sur l'exercice suivant. Les contrats
modélisés sont des contrats d'épargne individuels (catégories 4 et 5 de l'article A.344-2) : le seuil de
4,5 % des primes des catégories 3 et 6 (contrats en cas de décès) ne s'applique pas.
"""

import copy

PART_ASSUREUR_SOLDE_TECHNIQUE = 0.10  # A.132-11, I : 10 % du solde créditeur des éléments techniques

VARIANTES = ("reference", "pb_financiere_seule", "impot_projete")


def appliquer_variante(h, nom):
    if nom not in VARIANTES:
        raise ValueError(f"Variante inconnue : {nom}")
    h = copy.deepcopy(h)
    if nom == "pb_financiere_seule":
        h["strategie"].pop("participation_technique", None)
    if nom == "impot_projete":
        h["fiscalite"]["impot_dans_projection"] = True
    return h
