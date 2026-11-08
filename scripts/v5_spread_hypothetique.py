"""V5.1 : spread hypothétique des obligations détenues, construit à partir de paramètres publiés par l'EIOPA.

Usage : python scripts/v5_spread_hypothetique.py --archive <EIOPA_RFR_20261031.zip>
Écrit data/v5/marche/spread_hypothetique_20261031.json.

Le spread des obligations détenues n'est pas une donnée de marché observée : c'est une hypothèse, construite
sans aucune donnée d'indice de taux souverain. Elle reprend la moyenne de long terme des spreads (« long term
average spread », LTAS) que l'EIOPA publie avec la courbe sans risque, dans la même archive mensuelle
(classeur PD_CoD, feuille LTAS_Corps) :
- série : obligations en euros d'échelon de qualité de crédit 2 (notation A), la notation la plus représentée
  du portefeuille obligataire des assureurs français (61 % au T4 2025, ACPR, Analyses et synthèses n° 181) ;
- moyenne simple des séries « financières » et « non financières » (répartition du portefeuille entre les deux
  non retenue : hypothèse) ;
- conversion en spread continu au-dessus de la courbe EIOPA sans VA du même jour :
  s(k) = ln(1 + r(k) + LTAS(k)) - ln(1 + r(k)), k = 1 à 30 ans, plat au-delà.
L'archive est contrôlée par son empreinte SHA-256 (data/v5/marche/eiopa_rfr_20261031_provenance.json).
"""

import argparse
import hashlib
import io
import json
import math
import sys
import zipfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5.courbes_marche import DOSSIER_MARCHE, courbe_eiopa, provenance  # noqa: E402

SERIES = ("EUR_Financials_2", "EUR_Non-Financials_2")
ATTRIBUTION = ("Source: EIOPA - European Insurance and Occupational Pensions Authority. This document has been drafted using "
               "material downloaded from EIOPA website. EIOPA does not endorse this publication and in no way is liable for "
               "copyright or other intellectual property rights infringements nor for any damages caused to third-parties "
               "through this publication.")


def lire_ltas(archive):
    import openpyxl
    with zipfile.ZipFile(archive) as z:
        nom = [n for n in z.namelist() if n.endswith("_PD_CoD.xlsx")]
        if len(nom) != 1:
            raise ValueError(f"Classeur PD_CoD introuvable ou ambigu : {z.namelist()}")
        wb = openpyxl.load_workbook(io.BytesIO(z.read(nom[0])), read_only=True, data_only=True)
    lignes = list(wb["LTAS_Corps"].iter_rows(min_row=1, max_row=120, values_only=True))
    entete = [l for l in lignes if l[1] == "Issuer"][0]
    maturites = [int(x) for x in entete[2:] if isinstance(x, (int, float))]
    series = {}
    for l in lignes:
        if l[1] in SERIES:
            series[l[1]] = {m: float(v) / 100 for m, v in zip(maturites, l[2:])}
    if set(series) != set(SERIES) or maturites != list(range(1, 31)):
        raise ValueError("Séries LTAS ou maturités inattendues")
    return nom[0], series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True, help="archive EIOPA_RFR_20261031.zip publiée par l'EIOPA")
    a = ap.parse_args()
    prov = provenance()
    empreinte = hashlib.sha256(Path(a.archive).read_bytes()).hexdigest()
    if empreinte != prov["sha256_archive"]:
        raise SystemExit(f"Empreinte inattendue : {empreinte} (attendu {prov['sha256_archive']})")
    classeur, series = lire_ltas(a.archive)
    eiopa = courbe_eiopa()
    ltas = {k: (series[SERIES[0]][k] + series[SERIES[1]][k]) / 2 for k in range(1, 31)}
    spread = {str(k): round(math.log(1 + eiopa.taux_zc(k) + ltas[k]) - math.log(1 + eiopa.taux_zc(k)), 8) for k in range(1, 31)}
    fiche = {
        "statut": "hypothèse",
        "objet": "Spread hypothétique (composition continue) des obligations détenues par les assureurs fictifs, au-dessus de la courbe "
                 "sans risque EIOPA sans VA du 31/10/2026. Ce n'est pas un spread de marché observé à cette date.",
        "regle": "LTAS = moyenne simple des séries EUR_Financials_2 et EUR_Non-Financials_2 (échelon de qualité de crédit 2, notation A) ; "
                 "s(k) = ln(1 + r_EIOPA(k) + LTAS(k)) - ln(1 + r_EIOPA(k)), k = 1 à 30 ans ; plat au-delà de 30 ans",
        "justification": "Les obligations du modèle représentent l'ensemble du portefeuille obligataire des assureurs (souverains et entreprises). "
                         "Leur spread est une hypothèse de spread « normal », hors période de tension : la moyenne de long terme publiée par "
                         "l'EIOPA pour la notation la plus représentée du portefeuille des assureurs français (A+ à A- : 61 % au T4 2025, ACPR, "
                         "Analyses et synthèses n° 181). Aucune donnée d'indice de taux souverain n'est utilisée.",
        "donnees_publiees": {
            "source": "EIOPA, Risk-free interest rate term structures du 31/10/2026, archive " + prov["archive"] + ", classeur "
                      + classeur + ", feuille LTAS_Corps (Long term average of spreads, assets other than central government bonds)",
            "url": prov["url"], "sha256_archive": prov["sha256_archive"], "unite": "décimal (le classeur publie des pourcentages)",
            "EUR_Financials_2": {str(k): round(v, 8) for k, v in series[SERIES[0]].items()},
            "EUR_Non-Financials_2": {str(k): round(v, 8) for k, v in series[SERIES[1]].items()},
            "statut": "observé (paramètres publiés par l'EIOPA, repris tels quels)",
        },
        "parametres_hypothetiques": {
            "choix_de_la_serie": "échelon de qualité de crédit 2 (notation A)",
            "poids_financieres_non_financieres": [0.5, 0.5],
            "usage_d_une_moyenne_de_long_terme_comme_spread_courant": True,
        },
        "spread_continu": spread,
        "interpolation": "linéaire entre les maturités entières, plate au-delà de 30 ans",
        "usage": "prix de marché des obligations détenues et rendement de réinvestissement ; en risque neutre, intensité de perte cumulée "
                 "H(u) = s(u) x u (part kappa en défauts de blocs, le reste en perte lissée)",
        "conditions_de_reutilisation": ATTRIBUTION,
    }
    chemin = DOSSIER_MARCHE / "spread_hypothetique_20261031.json"
    chemin.write_text(json.dumps(fiche, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("écrit :", chemin)
    print({k: round(1e4 * float(spread[str(k)]), 1) for k in (1, 2, 5, 10, 15, 20, 30)}, "pb")


if __name__ == "__main__":
    main()
