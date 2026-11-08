"""V5 : les chiffres principaux du README, rédigés à la main, correspondent aux résultats versionnés.

Chaque valeur est recalculée depuis resultats/*.json, formatée comme dans le README (virgule décimale,
signe moins typographique) et recherchée dans son texte. Un résultat recalculé sans mise à jour du
README fait échouer le test. Correspondances détaillées : docs/V5_REPRODUCTION.md, section 6.
"""

import json
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
README = (RACINE / "README.md").read_text(encoding="utf-8")


def lire(nom):
    return json.loads((RACINE / "resultats" / nom).read_text(encoding="utf-8"))


K, R, REC, S = lire("v5_consolidation.json"), lire("v5_collecte.json"), lire("v5_reconciliation_collecte.json"), lire("v5_synthese_finale.json")
AU = lire("v5_audit_conventions.json")


def f(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def attendus():
    a = {}
    for p in "ABC":
        a[f"indicateur sans apport {p}"] = f"{100 * K['prudentiel'][f'{p}|passive']['apport_0']['indicateur_couverture_scr']:.0f} %"
        besoin = K["capital"][f"{p}|passive"]["besoin"]["1.0"]
        a[f"apport {p}"] = f(besoin) if besoin > 1e-9 else f"{p} couvre déjà son SCR simplifié sans apport"
        a[f"valeur de l'existant {p}"] = f(R["risque_neutre"][f"{p}|passive|0|0"]["valeur_existant"]["moyenne"])
    a["valeur de A avant recapitalisation"] = f(K["risque_neutre"]["A|passive|0"]["valeur_nette"])
    a["coût de la recapitalisation de A"] = f(K["risque_neutre"]["A|passive|0"]["valeur_nette"] - K["risque_neutre"]["A|passive|1.0"]["valeur_nette"])
    nb = [R["risque_neutre"][f"{p}|passive|0.06|0.5"]["valeur_affaires_nouvelles"]["moyenne"] for p in "ABC"]
    a["affaires nouvelles centrales"] = f"{f(min(nb))} à {f(max(nb))}"
    grille = [R["risque_neutre"][f"{p}|passive|{c0}|{eta}"]["valeur_affaires_nouvelles"]["moyenne"]
              for p in "ABC" for c0 in R["intensites"].values() for eta in R["elasticites"].values()]
    a["affaires nouvelles grille"] = f"{f(min(grille))} à {f(max(grille))}"
    for p in "AB":
        a[f"capital repositionnement {p}"] = "+" + f(K["capital"][f"{p}|repositionnement"]["besoin"]["1.0"] - K["capital"][f"{p}|passive"]["besoin"]["1.0"])
    a["capital repositionnement C"] = "+" + f(K["capital"]["C|repositionnement"]["besoin"]["1.0"] - K["capital"]["C|passive"]["besoin"]["1.0"])
    m = [S["valeur_totale"][f"{p}|taux_servi_marge"] for p in "ABC"]
    a["plage politique de marge"] = f"{f(min(x['min'] for x in m))} à {f(max(x['max'] for x in m))}"
    a["bornes sous le seuil"] = " ; ".join(f"{x['n'] - x['bornes_au_dela_du_seuil']}" for x in m)
    gap = [1e4 * (R["reel"][f"{p}|taux_servi_marge|0.06|0.5"]["ecart_taux_servi_reference_1_10"] - R["reel"][f"{p}|passive|0.06|0.5"]["ecart_taux_servi_reference_1_10"]) for p in "ABC"]
    a["baisse réalisée du taux servi"] = f"{-max(gap):.0f} à {-min(gap):.0f} pb"
    ec = [1e4 * R["reel"][f"{p}|taux_servi_marge|0.06|0.5"]["ecart_taux_servi_reference_1_10"] for p in "ABC"]
    a["écart à la référence"] = f"{f(max(ec), 0)} à {f(min(ec), 0)} pb"
    x = R["sensibilites_collecte"]["e0_moins_50pb|C|taux_servi_marge|0.1|1.0"]["ecart_totale"]
    a["cellule de C"] = f"{f(x['moyenne'])} ± {f(x['demi_intervalle_95'])}"
    cc = REC["capital_croissance"]
    sup = [v["scr_supplementaire_proportionnel"] for p in "ABC" for v in cc[f"{p}|passive"]["collecte_centrale"].values()]
    a["SCR de la croissance"] = f"{min(sup):.0f} à {max(sup):.0f} unités"
    fp = [cc[f"{p}|passive"]["collecte_centrale"]["moderee"]["fonds_propres_10_mediane"] - cc[f"{p}|passive"]["fonds_propres_10_mediane_extinction"] for p in "ABC"]
    a["fonds propres retenus"] = f"+{min(fp):.0f} à +{max(fp):.0f}"
    a["collecte nette modèle"] = f"{f(100 * REC['modele']['B']['collecte_nette']['annee_1'], 2)} %"
    a["collecte nette place"] = f"{f(100 * REC['place_2025']['en_pct_pm_debut']['collecte_nette'], 2)} %"
    kappa = [REC["seuil_cout_capital"][p]["kappa_seuil"] for p in "ABC"]
    a["seuil de coût du capital"] = f"{f(100 * min(kappa))} % à {f(100 * max(kappa))} % par an"
    pa = AU["participation"]
    e = [-pa[p]["v5_1"]["ecart_valeurs_nettes"]["moyenne"] for p in "ABC"]
    a["correction à capital égal"] = f"{f(e[0])} (A), {f(e[1])} (B) et {f(e[2])} (C)"
    return a


# Formes attendues dans le README, construites à partir des valeurs recalculées.
FORMES = {
    "bornes sous le seuil": lambda v: "dans {} (A), {} (B) et {} (C) configurations sur 20".format(*v.split(" ; ")),
}


@pytest.mark.parametrize("cle,valeur", sorted(attendus().items()))
def test_chiffre_du_readme_conforme_aux_resultats(cle, valeur):
    texte = FORMES.get(cle, lambda v: v)(valeur)
    assert texte in README, f"README : « {texte} » ({cle}) introuvable ; mettre à jour le README ou docs/V5_REPRODUCTION.md"


def test_nombre_de_tests_annonce():
    import subprocess
    import sys
    sortie = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"], cwd=RACINE,
                            capture_output=True, text=True).stdout
    n = sum(int(l.rsplit(": ", 1)[1]) for l in sortie.splitlines() if ": " in l and l.rsplit(": ", 1)[1].isdigit())
    assert f"{n} tests" in README
