# V5 : reproduction des résultats et traçabilité

Ce document explique comment vérifier, puis recalculer, les résultats de la V5 à partir des seuls fichiers du dépôt, et d'où vient chaque figure et chaque chiffre clé du README.

## 1. Ce que contient le dépôt

| Dossier | Contenu | Produit par |
| --- | --- | --- |
| `data/`, `data/v5/` | Données de marché observées, paramètres calibrés, profils et hypothèses fictifs, avec leur statut ([registre](V5_HYPOTHESES.md)) | Saisie documentée ; `scripts/v5_extraire_eiopa.py` pour la courbe EIOPA, `scripts/v5_spread_hypothetique.py` pour le spread hypothétique (LTAS publiées par l'EIOPA) |
| `resultats/v5_*.json` | Résultats des calculs de la V5.1, versionnés | Scripts de calcul (section 4) |
| `resultats/v5_0/` | Résultats de la V5.0 publiée le 07/11/2026 (participation financière seule), conservés pour la comparaison avant/après de [V5_AUDIT_CONVENTIONS.md](V5_AUDIT_CONVENTIONS.md) | Copie de quatre fichiers de la V5.0 (consolidation, collecte, synthèse finale, réconciliation), qui ne contiennent que des résultats agrégés. Calculés avec les données de marché de la V5.0, retirées du dépôt : ils ne se reproduisent pas depuis la V5.1 ; l'effet de la seule participation est recalculé à données de marché identiques par la variante `pb_financiere_seule` (`src/v5/variantes_audit.py`) |
| `docs/V5_*.md` | Rapports et synthèses, sauf `V5_METHODOLOGIE.md`, `V5_SPECIFICATION_COLLECTE.md` et `V5_REPRODUCTION.md` (ce document), rédigés à la main | Générateurs (`scripts/v5_rapport_*.py`, `v5_synthese_*.py`, `v5_registre_hypotheses.py`), depuis `resultats/` et `data/` uniquement |
| `figures/v5/*.png` | Figures du README | `scripts/v5_figures.py`, depuis `resultats/` et `data/` uniquement |
| `resultats/cache_v5/` | Tirages par scénario, pour reprendre un calcul interrompu | Non versionné ; supprimable |

Aucun chiffre des documents générés n'est saisi à la main : les phrases sont écrites dans les générateurs, les nombres et les jugements (signe, importance, robustesse) viennent des fichiers de résultats et des seuils de `data/v5/strategies/strategies.json`. Les chiffres du README et de ce document sont rédigés à la main ; `tests/test_v5_readme.py` vérifie les principaux contre les résultats.

## 2. Environnement

- Python 3.13 et les versions figées de `requirements.txt` (`pip install -r requirements.txt`) ; pour les tests, `requirements-dev.txt` y ajoute openpyxl, qui ne sert qu'à lire le classeur officiel de l'EIOPA.
- Résultats produits sous Linux, sur 2 cœurs. Les calculs sont déterministes : sur une autre plateforme ou avec d'autres versions de numpy, de très petits écarts d'arrondi restent possibles ; ils ne doivent pas dépasser l'ordre de l'arrondi machine.
- Police Inter facultative pour les figures (repli sur DejaVu Sans) : le rendu change, pas les valeurs.

## 3. Trois niveaux de vérification

| Niveau | Commande | Durée indicative | Ce qui est vérifié |
| --- | --- | --- | --- |
| 1. Cohérence | `python -m pytest` | environ une minute | Tous les tests : formules, invariants comptables, absence d'arbitrage, non-régression des V1 à V4, cas limites de la collecte, et **concordance octet pour octet** de chaque document généré avec sa régénération depuis les résultats versionnés (`tests/test_v5_documents.py`), chiffres principaux du README (`tests/test_v5_readme.py`) |
| 1 bis. Régénération | `python scripts/v5_documents.py`, puis `git status` | moins d'une minute | Documents et figures reproduits depuis `resultats/` : aucun fichier suivi ne doit changer (les PNG peuvent différer si la police n'est pas la même) |
| 2. Recalcul ciblé | `python scripts/v5_verifier_reproduction.py` | environ 2 minutes | 17 valeurs recalculées sans cache avec les fonctions des scripts de production (consolidation, collecte risque neutre et réelle, flux du modèle, contrat sans marge explicite et sa variante de liquidation, capital de la croissance, seuil de coût du capital) et comparées aux résultats versionnés ; écart toléré 10⁻⁹, rapporté à max(1, valeur) |
| 2 bis. Vue prudentielle | `python scripts/v5_verifier_reproduction.py --prudentiel` | environ 4 minutes de plus | SCR simplifié, fonds propres et indicateur de couverture du profil B sans apport, sur 2 000 scénarios |
| 3. Recalcul complet | section 4 | plusieurs heures | Tous les résultats |

Résultat dans l'environnement de développement : 17 valeurs sur 17 reproduites à l'identique au niveau 2 ; 20 sur 20 avec le niveau 2 bis (les trois indicateurs prudentiels du profil B).

## 4. Recalcul complet, dans l'ordre

Chaque script reprend depuis `resultats/cache_v5/` les calculs déjà faits ; pour un recalcul intégral, supprimer d'abord ce dossier. Durées mesurées sur 2 cœurs lors du recalcul complet de la V5.1 (novembre 2026), sans cache au départ ; la consolidation, la collecte et l'audit reprennent depuis leur cache s'ils sont interrompus.

| Étape | Script | Écrit | Lit | Durée |
| --- | --- | --- | --- | --- |
| 0 (facultatif) | `v5_extraire_eiopa.py <archive> <date> <url>` | `data/v5/marche/eiopa_rfr_20261031_*` | archive officielle EIOPA (non versionnée ; empreinte SHA-256 dans la fiche de provenance) | |
| 0 (données) | `v5_spread_hypothetique.py --archive EIOPA_RFR_20261031.zip` | `data/v5/marche/spread_hypothetique_20261031.json` | archive EIOPA du 31/10/2026 (empreinte contrôlée) | quelques secondes |
| 1 | `v5_calibration_credit.py` | `v5_calibration_credit.json` | `data/v5/` | moins d'une seconde |
| 2 | `v5_bilans_initiaux.py` | `v5_bilans_initiaux.json` | `data/` | environ 1 min |
| 3 | `v5_comparaison_conventions.py`, `v5_solvabilite_profils.py`, `v5_diagnostic_profil_a.py` | `v5_comparaison_conventions.json`, `v5_solvabilite_profils.json`, `v5_diagnostic_profil_a.json` | `data/` | environ 8 min, 8 min et 1 min |
| 4 | `v5_synthese.py` | `v5_synthese.json` | `data/` | environ 17 min |
| 5 | `v5_strategies.py`, puis `v5_strategies_ecarts.py` et `v5_strategies_mecanismes.py` | `v5_strategies.json`, `v5_strategies_ecarts.json`, `v5_strategies_mecanismes.json` | `data/` ; `v5_strategies.json` pour les écarts | environ 50 min, 6 min et 1 min |
| 6 | `v5_consolidation.py` | `v5_consolidation.json` | `v5_strategies.json` (points d'apport de départ) | environ 2 h 40 |
| 7 | `v5_effet_distribution.py` | `v5_effet_distribution.json` | `v5_consolidation.json`, `v5_strategies.json` | environ 1 min |
| 8 | `v5_collecte.py` | `v5_collecte.json` | `v5_consolidation.json` (apports à 100 %) | environ 1 h 35 |
| 9 | `v5_reconciliation_collecte.py` | `v5_reconciliation_collecte.json` | `v5_collecte.json`, `v5_consolidation.json`, `data/v5/collecte/` | environ 2 min |
| 10 | `v5_audit_conventions.py` | `v5_audit_conventions.json` | `v5_consolidation.json` (apports de la V5.1) | environ 25 min |
| 11 | `v5_documents.py` | `docs/V5_*.md` générés, `resultats/v5_synthese_finale.json`, `figures/v5/` | tous les résultats ci-dessus, et `resultats/v5_0/` pour l'audit | moins d'une minute |

**Graines.** Générateur de scénarios : graine 2026 (`data/hypotheses.json`, `gse.graine`), paires antithétiques. Tirages de défaut : graine 2027 (`src/v5/credit.py`), indépendants du générateur, appariés entre stratégies. Rééchantillonnage de la vue prudentielle : graine 20261106 (`scripts/v5_consolidation.py`). Contrôle sur tirages indépendants : graines 4049 et 9173. Mêmes scénarios et mêmes défauts pour toutes les stratégies, intensités et élasticités.

## 5. Traçabilité des figures

| Figure | Fonction de `scripts/v5_figures.py` | Données lues | Nature |
| --- | --- | --- | --- |
| `contexte_taux.png` | `contexte_taux` | `data/v5/marche/eiopa_rfr_20261031_eur.csv` (colonnes `taux_sans_va`, `taux_avec_va`, maturités 1 à 50) ; `data/v5/marche/spread_hypothetique_20261031.json` (`spread_continu`) | observé (EIOPA) et hypothèse (spread) |
| `reconciliation_collecte.png` | `reconciliation` | `resultats/v5_reconciliation_collecte.json` : `place_2025.en_pct_pm_debut` ; `modele.B.<poste>.annee_1` | observé (place, dont approximations signalées) et simulé (modèle) |
| `capital_valeur_profils.png` | `capital_valeur` | `resultats/v5_consolidation.json` : `capital.<P>|passive.besoin.1.0`, `incertitude.1.0.q025`, `q975` ; `resultats/v5_collecte.json` : `risque_neutre.<P>|passive|0|0.valeur_existant.moyenne`, `risque_neutre.<P>|passive|0.06|0.5.valeur_affaires_nouvelles.moyenne` | simulé |
| `ecarts_valeur_totale.png` | `ecarts_valeur_totale` | `resultats/v5_synthese_finale.json` : `valeur_totale.<P>|<stratégie>` (min, max, verdict, centre) et `seuils` ; valeurs issues de `v5_collecte.json` (`ecarts`, `sensibilite_onc_max`) | simulé |
| `marge_elasticite.png` | `marge_elasticite` | `resultats/v5_collecte.json` : `ecarts.<P>|taux_servi_marge|0.06|<eta>.totale`, `sensibilite_onc_max.<P>|taux_servi_marge|0.06|<eta>.ecart_totale`, `ecarts.<P>|taux_servi_marge|0|0.existant` ; seuils de `v5_synthese_finale.json` | simulé |
| `matrice_arbitrages.png` | `matrice` | `resultats/v5_synthese_finale.json` : `matrice.<P>|<stratégie>.<dimension>` | simulé |

## 6. Traçabilité des chiffres clés du README

| Chiffre | Valeur | Fichier et clé |
| --- | --- | --- |
| Indicateur de couverture simplifié sans apport | 12 % / 71 % / 103 % | `v5_consolidation.json` : `prudentiel.<P>|passive.apport_0.indicateur_couverture_scr` |
| Apport pour 100 % (gestion passive) | 101,0 / 27,6 / 0,0 (C couvre son SCR simplifié sans apport) | `v5_consolidation.json` : `capital.<P>|passive.besoin.1.0` |
| Valeur de l'existant de A avant recapitalisation ; coût de la recapitalisation à 100 % | 4,5 ; 9,9 | `v5_consolidation.json` : `risque_neutre.A|passive|0.valeur_nette` ; différence avec `risque_neutre.A|passive|1.0.valeur_nette` |
| Valeur de l'existant recapitalisé | −5,4 / 57,5 / 82,8 | `v5_collecte.json` : `risque_neutre.<P>|passive|0|0.valeur_existant.moyenne` |
| Valeur des affaires nouvelles, collecte centrale | 6,2 / 8,6 / 10,7 | `v5_collecte.json` : `risque_neutre.<P>|passive|0.06|0.5.valeur_affaires_nouvelles.moyenne` |
| Marge des affaires nouvelles (gestion passive) | 2,8 % / 2,7 % / 2,9 % | `v5_collecte.json` : `risque_neutre.<P>|passive|0.06|0.5.marge_affaires_nouvelles` |
| Capital supplémentaire du repositionnement à l'ouverture | +19,2 (A), +20,1 (B), +2,2 (C) | `v5_consolidation.json` : `capital.<P>|repositionnement.besoin.1.0` moins celui de la gestion passive |
| Politique de marge, plage de l'écart de valeur totale | −3,0 à 9,8 | `v5_synthese_finale.json` : `valeur_totale.<P>|taux_servi_marge.min`, `max` |
| Baisse réalisée du taux servi, marge contre passive | −37 / −14 / −5 pb | `v5_collecte.json` : `reel.<P>|taux_servi_marge|0.06|0.5.ecart_taux_servi_reference_1_10` moins celui de `reel.<P>|passive|0.06|0.5` |
| Écart du taux servi de marge à la référence | −93 / −53 / −26 pb | `v5_collecte.json` : `reel.<P>|taux_servi_marge|0.06|0.5.ecart_taux_servi_reference_1_10` |
| SCR supplémentaire de la croissance à 10 ans (gestion passive) | 11 à 66 | `v5_reconciliation_collecte.json` : `capital_croissance.<P>|passive.collecte_centrale.<élasticité>.scr_supplementaire_proportionnel` |
| Seuil de coût du capital des affaires nouvelles (collecte centrale) | 2,0 % à 2,5 % par an | `v5_reconciliation_collecte.json` : `seuil_cout_capital.<P>.kappa_seuil` |
| Collecte nette, modèle contre place | 0,59 % contre 0,69 % | `v5_reconciliation_collecte.json` : `modele.<P>.collecte_nette.annee_1` ; `place_2025.en_pct_pm_debut.collecte_nette` |
| Fonds propres comptables retenus par la croissance (gestion passive, eta = 0,5) | +62 (A), +33 (B), +28 (C) | `v5_reconciliation_collecte.json` : `capital_croissance.<P>|passive.collecte_centrale.moderee.fonds_propres_10_mediane` moins `fonds_propres_10_mediane_extinction` |
| Configurations où la borne de la politique de marge passe sous le seuil | 6 / 8 / 13 sur 20 | `v5_synthese_finale.json` : `n` moins `bornes_au_dela_du_seuil` de `valeur_totale.<P>|taux_servi_marge` |
| Écart de C de signe contraire (e0 = −0,5 point, c0 = 10 %, eta = 1) | −7,1 ± 3,4 | `v5_collecte.json` : `sensibilites_collecte.e0_moins_50pb|C|taux_servi_marge|0.1|1.0.ecart_totale` |
| Verdicts et comptes (repositionnement, politiques compétitives, réinvestissement, rétention) | |
| Effet de la correction de la participation (à capital et marché identiques) | | `v5_audit_conventions.json` : `participation`, `participation_strategies` ; comparaison complète : `docs/V5_AUDIT_CONVENTIONS.md` | `v5_synthese_finale.json` : `valeur_totale.<P>|<stratégie>.verdict`, `significatifs`, `importants`, `bornes_au_dela_du_seuil` |

`<P>` désigne le profil (A, B ou C). Les autres chiffres des documents se retrouvent de la même façon : chaque document généré indique en tête le script et les fichiers de résultats dont il provient.
