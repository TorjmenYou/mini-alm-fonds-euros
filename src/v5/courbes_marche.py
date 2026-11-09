"""Courbes de marché de la V5 : courbe sans risque EIOPA et courbe des obligations détenues.

Statuts des données, jamais mélangés (voir data/v5/README.md) :
- observé : courbe EIOPA publiée (fichier officiel, empreinte SHA-256 conservée) ;
- hypothèse : spread des obligations détenues au-dessus de la courbe sans risque (moyenne de long terme
  publiée par l'EIOPA, pas un spread de marché observé) ;
- fictif : portefeuilles et bilans des profils d'assureur.
"""

import csv
import io
import json
import zipfile
from pathlib import Path

from ..courbes import CourbeZeroCoupon, SpreadCredit

DOSSIER_MARCHE = Path(__file__).resolve().parents[2] / "data" / "v5" / "marche"


def lire_classeur_eiopa(chemin, feuille="RFR_spot_no_VA", zone="Euro"):
    """Lit une courbe dans le classeur « Term_Structures » de l'EIOPA (archive .zip ou fichier .xlsx).

    Disposition du classeur (publication mensuelle de l'EIOPA) : ligne 2, noms des zones
    (« Euro », « Austria »...) ; ligne 3, identifiant de la courbe ; lignes 4 à 10, paramètres
    (Coupon_freq, LLP, Convergence, UFR, alpha, CRA, VA) ; puis maturités 1 à 150 en colonne B.
    Renvoie {"identifiant", "parametres", "taux": [r_1, ..., r_150]} (taux zéro-coupon actuariels).
    """
    import openpyxl

    chemin = Path(chemin)
    if chemin.suffix.lower() == ".zip":
        with zipfile.ZipFile(chemin) as z:
            noms = [n for n in z.namelist() if n.endswith("_Term_Structures.xlsx")]
            if len(noms) != 1:
                raise ValueError(f"Classeur Term_Structures introuvable ou ambigu dans {chemin.name} : {noms}")
            contenu = io.BytesIO(z.read(noms[0]))
    else:
        contenu = chemin
    wb = openpyxl.load_workbook(contenu, read_only=True, data_only=True)
    lignes = list(wb[feuille].iter_rows(min_row=1, max_row=170, values_only=True))
    colonne = [i for i, v in enumerate(lignes[1]) if v == zone]
    if len(colonne) != 1:
        raise ValueError(f"Zone {zone!r} introuvable ou ambiguë dans la feuille {feuille}")
    c = colonne[0]
    parametres = {lignes[i][1]: lignes[i][c] for i in range(3, 10)}
    taux = {l[1]: l[c] for l in lignes[10:] if isinstance(l[1], int)}
    maturites = sorted(taux)
    if maturites != list(range(1, len(maturites) + 1)) or len(maturites) < 60:
        raise ValueError("Maturités inattendues dans le classeur EIOPA")
    return {"identifiant": lignes[2][c], "parametres": parametres, "taux": [float(taux[k]) for k in maturites]}


def courbe_eiopa(date="20261031", avec_va=False):
    """Courbe sans risque EIOPA (zone euro) enregistrée dans data/v5/marche, en CourbeZeroCoupon."""
    chemin = DOSSIER_MARCHE / f"eiopa_rfr_{date}_eur.csv"
    colonne = "taux_avec_va" if avec_va else "taux_sans_va"
    with open(chemin, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    return CourbeZeroCoupon([float(l[colonne]) for l in lignes])


def provenance(date="20261031"):
    """Métadonnées de traçabilité de la courbe EIOPA (source, empreinte, paramètres)."""
    return json.loads((DOSSIER_MARCHE / f"eiopa_rfr_{date}_provenance.json").read_text(encoding="utf-8"))


def spread_obligations(date="20261031"):
    """Spread hypothétique des obligations détenues (SpreadCredit), au-dessus de la courbe EIOPA sans VA.
    Statut « hypothèse » : moyenne de long terme des spreads publiée par l'EIOPA (LTAS, notation A),
    fiche spread_hypothetique_<date>.json écrite par scripts/v5_spread_hypothetique.py. Ce n'est pas un
    spread de marché observé ; aucune donnée d'indice de taux souverain n'est utilisée."""
    fiche = json.loads((DOSSIER_MARCHE / f"spread_hypothetique_{date}.json").read_text(encoding="utf-8"))
    return SpreadCredit({int(k): v for k, v in fiche["spread_continu"].items()})
