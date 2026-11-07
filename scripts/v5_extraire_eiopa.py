"""Extrait la courbe sans risque EIOPA (zone euro) d'une publication mensuelle officielle.

Usage : python scripts/v5_extraire_eiopa.py <EIOPA_RFR_AAAAMMJJ.zip> <date_publication AAAA-MM-JJ> <url>
Écrit data/v5/marche/eiopa_rfr_<AAAAMMJJ>_eur.csv (taux sans et avec correction pour volatilité)
et la fiche de provenance (empreinte SHA-256 de l'archive, identifiant et paramètres de la courbe).
"""

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.v5.courbes_marche import DOSSIER_MARCHE, lire_classeur_eiopa  # noqa: E402

archive, date_publication, url = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
date = re.search(r"EIOPA_RFR_(\d{8})", archive.name).group(1)
sans_va = lire_classeur_eiopa(archive, "RFR_spot_no_VA")
avec_va = lire_classeur_eiopa(archive, "RFR_spot_with_VA")
DOSSIER_MARCHE.mkdir(parents=True, exist_ok=True)
with open(DOSSIER_MARCHE / f"eiopa_rfr_{date}_eur.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["maturite", "taux_sans_va", "taux_avec_va"])
    for k, (a, b) in enumerate(zip(sans_va["taux"], avec_va["taux"]), start=1):
        w.writerow([k, repr(a), repr(b)])
fiche = {
    "statut": "observé",
    "source": "EIOPA, Risk-free interest rate term structures, publication mensuelle",
    "url": url,
    "date_reference": f"{date[:4]}-{date[4:6]}-{date[6:]}",
    "date_publication": date_publication,
    "archive": "EIOPA_RFR_" + date + ".zip",
    "sha256_archive": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "classeur": f"EIOPA_RFR_{date}_Term_Structures.xlsx",
    "feuilles": {"taux_sans_va": "RFR_spot_no_VA", "taux_avec_va": "RFR_spot_with_VA"},
    "zone": "Euro",
    "identifiant_courbe": sans_va["identifiant"],
    "parametres_sans_va": sans_va["parametres"],
    "parametres_avec_va": avec_va["parametres"],
    "nature_des_taux": "taux zéro-coupon actuariels (composition annuelle), maturités 1 à 150 ans, en décimal",
}
(DOSSIER_MARCHE / f"eiopa_rfr_{date}_provenance.json").write_text(json.dumps(fiche, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("Courbe", sans_va["identifiant"], "écrite ;", len(sans_va["taux"]), "maturités")
