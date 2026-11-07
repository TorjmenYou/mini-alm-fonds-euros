# Données de la V5

Chaque donnée porte un statut, écrit dans le fichier ; les trois statuts de base sont les suivants (le statut **hypothèse**, défini en fin de page, s'y ajoute, et certaines lignes précisent une variante : source secondaire, conversion par une règle écrite, sensibilité, stress) :

| Statut | Définition | Exemples |
| --- | --- | --- |
| **Observé** | Publié par une source officielle, daté, avec sa référence exacte (et l'empreinte du fichier quand il y en a un) | Courbe sans risque EIOPA au 31/10/2026 |
| **Calibré** | Paramètre choisi pour reproduire un ordre de grandeur observé ; la source et la règle de calibrage sont indiquées | Spread des obligations détenues, taux de rachat de référence |
| **Fictif** | Hypothèse de modélisation sans prétention de représenter un organisme réel, testée en sensibilité | Bilans et portefeuilles des profils d'assureur |

## Catalogue

| Fichier | Statut | Contenu | Source |
| --- | --- | --- | --- |
| `marche/eiopa_rfr_20261031_eur.csv` | Observé | Courbe sans risque de la zone euro, taux zéro-coupon de 1 à 150 ans, sans et avec correction pour volatilité | EIOPA, publication mensuelle du 05/11/2026, archive `EIOPA_RFR_20261031.zip` ; extraction par `scripts/v5_extraire_eiopa.py` |
| `marche/eiopa_rfr_20261031_provenance.json` | Observé | Fiche de traçabilité : URL, empreinte SHA-256 de l'archive, identifiant de la courbe, paramètres (UFR 3,30 %, LLP 20 ans, CRA 10 pb, VA 20 pb) | Même source |
| `marche/spread_oat_20261104.json` | Calibré | Spread zéro-coupon des OAT au-dessus de la courbe EIOPA sans VA (35 pb à 2 ans, 147 pb à 10 ans, 202 pb à 30 ans) | TEC du 04/11/2026 (oblig.fr), courbe EIOPA du 31/10/2026 ; TEC pris comme taux zéro-coupon |
| `marche/spread_oat_20261104_zc.json` | Calibré | Spread zéro-coupon des OAT par bootstrap du TEC (coupons annuels), 2 à 30 ans : 35 pb à 2 ans, 159 pb à 10 ans, 228 pb à 30 ans | TEC du 04/11/2026 et courbe EIOPA du 31/10/2026 ; écrit par `scripts/v5_calibration_credit.py` |
| `profils/profils.json` | Fictif, avec quelques paramètres observés ou calibrés | Trois profils d'assureur (A historique sous pression, B intermédiaire, C plus récemment investi) : bilans, poches obligataires par génération, garanties, taux servis ; statut de chaque paramètre indiqué | Voir `profils/confrontation_acpr.md` |
| `profils/confrontation_acpr.md` | Observé (place) | Ordres de grandeur publiés (ACPR, Banque de France, France Assureurs) confrontés aux profils, et liste des données non trouvées | Publications citées dans le fichier |
| `conventions/conventions.json` | Observé, calibré, hypothèse ou fictif selon la ligne | Décomposition du spread OAT (CDS, notations, défauts historiques, recouvrements), conventions de crédit comparées (forme lissée ou par saut), pertes attendues réelles, références des assurés, taux de rachat de place | Sources indiquées ligne par ligne |
| `strategies/strategies.json` | Fictif | Stratégies ALM comparées (gestion passive, réinvestissement progressif, repositionnement, politiques de taux servi, liquidité défensive), cibles de couverture, rendement exigé fictif | Choix de modélisation |
| `collecte/collecte.json` | Fictif, avec une intensité dérivée d'agrégats observés | Collecte nouvelle sensible au taux servi relatif : intensités c0, élasticités eta, réaction g(e), contrats nouveaux, sensibilités (e0, horizon de collecte) | France Assureurs (via le Cercle de l'Épargne) et ACPR n° 180 pour l'intensité centrale ; réconciliation : `docs/V5_COLLECTE.md`, section 1 |
| `conventions/marche_acpr.json` | Observé (place) | Observations ACPR utilisées pour la plausibilité : rachats (n° 179), taux servis et leur dispersion (n° 180), solvabilité 2026 (n° 185, source secondaire) | Publications citées dans le fichier |

Dans `conventions/conventions.json`, le statut **hypothèse** désigne un choix de modélisation justifié mais non observé (par exemple la part de crédit du spread ou le niveau initial de la référence des assurés). Il est distinct du statut fictif, réservé aux paramètres sans ancrage.
