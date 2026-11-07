"""Génère docs/V5_HYPOTHESES.md : registre des données et hypothèses de la V5, avec leur statut.

Usage : python scripts/v5_registre_hypotheses.py [--sortie docs/V5_HYPOTHESES.md]
Lit uniquement les fichiers de données (data/hypotheses.json, data/v5/**). Aucune valeur n'est saisie ici :
le registre recopie les valeurs, les statuts et les sources tels qu'ils figurent dans les fichiers, pour
que chaque hypothèse puisse être retrouvée, discutée et modifiée à un seul endroit.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
DATA = RACINE / "data"


def lire(chemin):
    return json.loads((DATA / chemin).read_text(encoding="utf-8"))


def f(x, dec=2):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")
    return s


def pct(x, dec=2):
    return f(100 * x, dec) + " %"


def texte(v):
    """Valeur lisible d'un champ de donnée (nombre, liste, dictionnaire court)."""
    if v is None:
        return "aucun"
    if isinstance(v, bool):
        return "oui" if v else "non"
    if isinstance(v, (int, float)):
        return f"{v:g}".replace(".", ",")
    if isinstance(v, dict):
        return " ; ".join(f"{k} : {texte(x)}" for k, x in v.items())
    if isinstance(v, list):
        return ", ".join(texte(x) for x in v)
    return str(v).replace("|", "/")


def lignes_statut(d, exclure=("statut", "source", "sources", "note", "regle", "reserve", "reserves", "justification", "observations")):
    """Toutes les entrées d'un fichier qui portent un champ « statut » : chemin, valeurs, statut, source."""
    sortie = []

    def parcourir(x, chemin):
        if isinstance(x, dict):
            if "statut" in x:
                valeurs = {k: v for k, v in x.items() if k not in exclure and not k.startswith("_")}
                source = " ; ".join(str(x[k]) for k in ("source", "regle", "note", "observations", "justification") if k in x)
                sortie.append((chemin, texte(valeurs) if valeurs else "", str(x["statut"]), source))
            for k, v in x.items():
                if k != "statut":
                    parcourir(v, f"{chemin}.{k}" if chemin else k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                parcourir(v, f"{chemin}[{i}]")

    parcourir(d, "")
    return sortie


def tableau(A, entetes, lignes):
    A("| " + " | ".join(entetes) + " |\n| " + " | ".join("---" for _ in entetes) + " |")
    for l in lignes:
        A("| " + " | ".join(str(c).replace("\n", " ").replace("|", "/") for c in l) + " |")
    A("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_HYPOTHESES.md"))
    a = ap.parse_args()
    L = []
    A = L.append
    base = lire("hypotheses.json")
    prof = lire("v5/profils/profils.json")
    conv = lire("v5/conventions/conventions.json")
    strat = lire("v5/strategies/strategies.json")
    coll = lire("v5/collecte/collecte.json")
    place = lire("v5/conventions/marche_acpr.json")
    prov = lire("v5/marche/eiopa_rfr_20261031_provenance.json")
    spread = lire("v5/marche/spread_oat_20261104.json")
    spread_zc = lire("v5/marche/spread_oat_20261104_zc.json")

    A("# V5 : registre des données et des hypothèses\n")
    A("Généré par `scripts/v5_registre_hypotheses.py` à partir des seuls fichiers de `data/` : chaque valeur, chaque statut et chaque source sont recopiés tels qu'ils figurent dans ces fichiers. "
      "Pour modifier une hypothèse, on modifie le fichier de données, puis on relance les calculs concernés (`docs/V5_REPRODUCTION.md`).\n")
    A("**Statuts.** *Observé* : publié par une source officielle, daté, référencé. *Calibré* : choisi pour reproduire un ordre de grandeur observé, avec sa règle. "
      "*Hypothèse* : choix de modélisation justifié mais non observé. *Fictif* : sans ancrage, testé en sensibilité quand il conduit les conclusions. "
      "Les trois profils d'assureur sont fictifs : ils ne décrivent aucun organisme réel. Unité : 1 unité = 10 M€.\n")

    # 1. Marché ---------------------------------------------------------------------------------
    A("## 1. Données de marché au 31/10/2026\n")
    with open(DATA / "v5" / "marche" / "eiopa_rfr_20261031_eur.csv", encoding="utf-8") as fh:
        courbe = {int(r["maturite"]): r for r in csv.DictReader(fh)}
    A(f"**Courbe sans risque EIOPA** ({prov['statut']}) : {prov['source']}, date de référence {prov['date_reference']}, publiée le {prov['date_publication']} ; identifiant `{prov['identifiant_courbe']}` ; "
      f"archive `{prov['archive']}`, empreinte SHA-256 `{prov['sha256_archive']}`. {prov['nature_des_taux'][:1].upper() + prov['nature_des_taux'][1:]}. "
      f"Paramètres : UFR {texte(prov['parametres_sans_va']['UFR'])} %, LLP {prov['parametres_sans_va']['LLP']} ans, convergence {prov['parametres_sans_va']['Convergence']} ans, ajustement pour risque de crédit {prov['parametres_sans_va']['CRA']} pb, "
      f"correction pour volatilité {prov['parametres_avec_va']['VA']} pb (alpha {texte(prov['parametres_sans_va']['alpha'])} sans VA, {texte(prov['parametres_avec_va']['alpha'])} avec VA). Fichier : `data/v5/marche/eiopa_rfr_20261031_eur.csv`.\n")
    tableau(A, ["Maturité", "Sans VA", "Avec VA"], [(f"{m} an{'s' if m > 1 else ''}", pct(float(courbe[m]["taux_sans_va"])), pct(float(courbe[m]["taux_avec_va"]))) for m in (1, 2, 5, 10, 20, 30, 50) if m in courbe])
    tec = spread["donnees_observees"]["TEC_04_11_2026"]
    A(f"**Taux de l'État français** (observé) : TEC du 04/11/2026, {spread['donnees_observees']['source_TEC']}.\n")
    tableau(A, ["Maturité"] + [f"{m} ans" for m in tec], [["TEC"] + [pct(v) for v in tec.values()],
                                                          ["Spread par bootstrap du TEC (convention centrale des résultats finaux)"] + [pct(spread_zc["spread_continu"][m]) for m in tec],
                                                          ["Spread avec le TEC pris comme zéro-coupon (convention initiale)"] + [pct(spread["spread_continu"][m]) for m in tec]])
    A(f"Spreads en composition continue au-dessus de la courbe EIOPA sans VA. **Convention centrale** (crédit `k70_granulaire_correle`, résultats finaux) : spread par bootstrap ({spread_zc['statut']}) : {spread_zc['regle']}. "
      f"**Convention initiale** (bilans initiaux et premières comparaisons de conventions, `docs/V5_CONVENTIONS.md`) : {spread['regle']} ({spread['statut']}). {spread['ecart_de_dates']}. Interpolation : {spread['interpolation']}. Usage : {spread['usage']}.\n")

    # 2. Profils --------------------------------------------------------------------------------
    A("## 2. Profils d'assureur (fictifs)\n")
    statut_unite = prof["unite_monetaire_statut"]
    A(prof["objet"] + f" Date d'arrêté : {prof['date_arrete']}. Unité monétaire ({statut_unite.split(' : ', 1)[0]}) : {statut_unite.split(' : ', 1)[-1]}.\n")
    lignes = []
    for nom, p in prof["profils"].items():
        b, pa, ac = p["bilan_initial"], p["passif"], p["actif"]
        poches = ", ".join(f"{x['millesime'].replace('_', '-')} {pct(x['part'], 0)} ({x['maturite_residuelle'][0]} à {x['maturite_residuelle'][1]} ans)" for x in p["poches_obligataires"])
        lignes.append((f"**{nom}** : {p['nom']}", f(b["pm"], 0), f(b["ppb"], 0), f(b["reserve_capitalisation"], 0), f(b["fonds_propres"], 0), pct(pa["tmg"]), pct(pa["taux_servi_initial"]),
                       " / ".join(pct(v, 0) for v in ac["allocation_cible"].values()), pct(ac["pvl_initiale_actions"], 0), f"{ac['maturite_reinvestissement_ans']} ans", poches))
    tableau(A, ["Profil", "PM", "PPB", "Réserve de capitalisation", "Fonds propres", "TMG moyen", "Taux servi initial", "Obligations / actions / monétaire", "Plus-values latentes actions", "Maturité de réinvestissement", "Générations d'obligations (part, maturités résiduelles)"], lignes)
    for nom, p in prof["profils"].items():
        A(f"- **{nom}** : {p['recit']}")
    A("")
    A("**Statut des paramètres de profil** : " + " ; ".join(f"*{k}* : {v}" for k, v in prof["statuts_des_parametres_de_profil"].items()) + ".\n")
    anc = prof["ancrages_coupons"]
    A(f"**Coupons d'achat par génération** : {anc['_methode']}\n")
    tableau(A, ["Génération", "Coupon", "Statut", "Observations"], [(k.replace("_", "-"), pct(v["coupon"]), v["statut"], v["observations"]) for k, v in anc.items() if not k.startswith("_")])
    if "_prime_achat" in anc:
        A(f"Prime d'achat : {pct(anc['_prime_achat']['valeur'])} ({anc['_prime_achat']['statut']}) : {anc['_prime_achat']['justification']}\n")
    com = prof["commun"]
    A("**Paramètres communs aux trois profils** :\n")
    A(f"- crédit : {com['credit']['statut']} ;")
    A(f"- référence des assurés (ancienne convention) : {com['comportement']['statut']} ;")
    A(f"- chargements sur encours : {pct(com['passif']['chargements_encours'])}, {com['passif']['statut_chargements']} ;")
    A(f"- frais de gestion : {com['frais_gestion_statut']}.\n")

    # 3. Moteur hérité --------------------------------------------------------------------------
    A("## 3. Paramètres du moteur hérités des V1 à V4\n")
    A("Fichier `data/hypotheses.json`. Les profils remplacent le bilan, l'allocation, les garanties et les chargements ; la convention centrale de la V5 remplace le rachat structurel (section 4). Les autres paramètres sont repris tels quels.\n")
    pa, rd, st, g = base["passif"], base["rachats_dynamiques"], base["strategie"], base["gse"]
    tableau(A, ["Paramètre", "Valeur", "Statut"], [
        ("Horizon de projection", f"{base['horizon_annees']} ans", "hypothèse V1 à V4"),
        ("Taux de décès", pct(pa["taux_deces"]), "fictif (V1 à V4)"),
        ("Frais de gestion sur encours", pct(pa["frais_gestion_encours"]), "fictif (V1 à V4)"),
        ("Rachat structurel des V1 à V4 (remplacé en V5)", pct(pa["taux_rachat_structurel"]), "hypothèse V1 à V4"),
        ("Loi de rachat dynamique (paliers, ACPR 2013)", f"alpha {pct(rd['alpha'])}, beta {pct(rd['beta'])}, gamma {pct(rd['gamma'])}, delta {pct(rd['delta'])}, RC max {pct(rd['rc_max'], 0)}, RC min {pct(rd['rc_min'], 0)}", "paramètres centraux fixés dans les V1 à V4 ; corridors ONC de 2013 en sensibilité"),
        ("Écart du taux servi visé à la référence (gestion passive)", pct(st["ecart_taux_cible"]), "fictif (V1 à V4)"),
        ("Participation minimale aux produits financiers", pct(st["participation_minimale"], 0), "règle réglementaire, simplifiée (produits afférents aux provisions)"),
        ("Durée maximale de la PPB, reprise annuelle maximale, plafond", f"{st['duree_max_ppb_ans']} ans, {pct(st['reprise_ppb_max_par_an'], 0)}, {pct(st['plafond_ppb_pct_pm'], 0)} de la PM", "durée réglementaire ; reprise et plafond fictifs"),
        ("Générateur de scénarios", f"Hull-White a = {texte(g['hw_a'])}, sigma = {texte(g['hw_sigma'])} ; volatilité actions {pct(g['vol_actions'], 0)} ; {f(g['nb_scenarios'], 0)} scénarios, graine {g['graine']}", "fictif (V1 à V4), calé sur la courbe de la base"),
        ("Rendement de dividende des actions", pct(base["economie"]["rendement_dividende_actions"]), "fictif (V1 à V4)"),
    ])

    # 4. Conventions ----------------------------------------------------------------------------
    A("## 4. Conventions de crédit, de comportement et de probabilité réelle\n")
    A(f"Fichier `data/v5/conventions/conventions.json` ({conv['objet'].rstrip('.')}). Comparaison chiffrée : `docs/V5_CONVENTIONS.md`. Chaque ligne porte le statut écrit dans le fichier.\n")
    A("**Convention centrale des résultats finaux** (`scripts/v5_consolidation.py`, `scripts/v5_collecte.py`) : crédit `k70_granulaire_correle` (70 % du spread en défaut par saut, 50 blocs corrélés, recouvrement 40 %, spread par bootstrap) ; référence des assurés `taux_servi_marche` (taux sans risque 10 ans lissé sur 7 ans, niveau initial 2,88 %) ; rachat structurel converti du taux ACPR de 4,4 % ; valorisation sur la base sans VA, vue prudentielle sur la base avec VA. Les autres lignes sont des sensibilités.\n")
    tableau(A, ["Entrée", "Valeurs", "Statut", "Source ou règle"], lignes_statut(conv))

    # 5. Stratégies -----------------------------------------------------------------------------
    A("## 5. Stratégies ALM et règles de lecture (fictives)\n")
    A(f"Fichier `data/v5/strategies/strategies.json`. {strat['objet']}\n")
    tableau(A, ["Code", "Stratégie", "Description"], [(f"`{k}`", v["libelle"], v["description"]) for k, v in strat["strategies"].items()])
    lect = strat["lecture"]
    A(f"**Seuils de lecture.** {lect['_regle'].replace('Seuils de lecture des écarts à la gestion passive. ', '')}\n")
    tableau(A, ["Seuil", "Valeur"], [(k, texte(v)) for k, v in lect.items() if not k.startswith("_")])
    A(f"**Rendement exigé par l'actionnaire** : {pct(strat['rentabilite_reelle']['rendement_exige']['valeur'], 0)}, {strat['rentabilite_reelle']['rendement_exige']['statut']}.\n")

    # 6. Collecte -------------------------------------------------------------------------------
    A("## 6. Collecte nouvelle\n")
    A(f"Fichier `data/v5/collecte/collecte.json`. {coll['objet']} Réconciliation avec les flux de 2025 : `docs/V5_COLLECTE.md`, section 1.\n")
    tableau(A, ["Entrée", "Valeurs", "Statut", "Source ou règle"], lignes_statut(coll))
    A("Sources : " + " ; ".join(coll["sources"].values()) + "\n")

    # 7. Place ----------------------------------------------------------------------------------
    A("## 7. Observations de place (plausibilité, pas de calibrage des profils)\n")
    A("Fichier `data/v5/conventions/marche_acpr.json` et `data/v5/profils/confrontation_acpr.md`.\n")
    tableau(A, ["Thème", "Valeur", "Statut", "Source"], [(o.get("theme", ""), o.get("valeur", ""), o.get("statut", ""), o.get("source", "")) for o in place.get("observations", [])])

    # 8. Non modélisé ---------------------------------------------------------------------------
    A("## 8. Ce que le modèle ne représente pas\n")
    for x in [
        "les prélèvements sociaux, les arbitrages entre supports et les transferts de contrats ;",
        "un SCR projeté : le besoin de capital est mesuré à l'ouverture, sur l'existant en extinction ;",
        "dans la vue prudentielle : la mesure transitoire sur les provisions techniques, les risques de contrepartie, de concentration, d'immobilier et de change, l'inflation des frais, l'ajustement symétrique actions et les impôts différés actifs ; le risque opérationnel n'y est calculé que par la formule sur provisions ;",
        "dans la valeur des affaires nouvelles : un coût explicite du capital additionnel (seulement un seuil, `docs/V5_COLLECTE.md`, section 8) et une marge pour risques non couvrables ;",
        "dans la vue prudentielle : les effets de la collecte sur les hypothèses de projection de l'existant (calcul en extinction) ;",
        "les effets commerciaux et de réputation d'un taux servi durablement inférieur à la référence, et le rachat de l'existant au-delà de la loi de rachat dynamique ;",
        "une calibration de l'élasticité de la collecte ou de la loi de rachat sur des données de 2026 : aucune n'a été trouvée.",
    ]:
        A(f"- {x}")
    A("")
    Path(a.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("écrit :", a.sortie)


if __name__ == "__main__":
    main()
