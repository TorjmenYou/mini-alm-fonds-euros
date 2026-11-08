"""Figures de la V5, produites uniquement à partir des fichiers de données et de résultats versionnés.

Usage : python scripts/v5_figures.py [--sortie figures/v5]
Lit : data/v5/marche/ (courbe EIOPA, spread hypothétique), resultats/v5_consolidation.json, resultats/v5_collecte.json,
resultats/v5_reconciliation_collecte.json, resultats/v5_synthese_finale.json. Aucune simulation n'est
relancée : chaque point d'une figure est une valeur de ces fichiers (traçabilité : docs/V5_REPRODUCTION.md).

1. contexte_taux.png : courbe EIOPA au 31/10/2026 sans et avec VA (observées) et courbe des obligations du modèle
   (EIOPA sans VA et spread hypothétique) ;
2. reconciliation_collecte.png : flux de la place en 2025 et flux du modèle (c0 = 6 %, g = 1) ;
3. capital_valeur_profils.png : apport à 100 % du SCR simplifié et valeurs de la gestion passive ;
4. ecarts_valeur_totale.png : écart de valeur totale à la gestion passive, plage sur 20 configurations ;
5. marge_elasticite.png : politique de marge, écart de valeur totale selon l'élasticité de la collecte ;
6. matrice_arbitrages.png : lectures par dimension (valeur, rentabilité, compétitivité, liquidité, capital).
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import logging

import matplotlib

matplotlib.use("Agg")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # repli de police silencieux
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib import font_manager  # noqa: E402

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))

N = "ABC"
COURT = {"reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}
NOMS_PROFILS = {"A": "A : historique sous pression", "B": "B : intermédiaire", "C": "C : plus récemment investi"}

# Palette (méthode dataviz, instance de référence) : surface, encres, trois teintes catégorielles
# validées toutes paires (profils), pôles divergents bleu / rouge et gris neutre (lectures).
FOND, ENCRE, ENCRE2, DISCRET, GRILLE = "#fcfcfb", "#0b0b0b", "#52514e", "#8a8984", "#e6e5e0"
PROFIL = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a"}
FAV, DEFAV, NEUTRE = "#2a78d6", "#e34948", "#b9b8b1"
FAV_CLAIR, DEFAV_CLAIR, NEUTRE_CLAIR = "#d5e4f7", "#f8d6d5", "#f0efec"

for _police in font_manager.findSystemFonts():  # Inter si elle est installée, sinon DejaVu Sans
    if Path(_police).name.startswith("Inter-"):
        font_manager.fontManager.addfont(_police)
plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10.5, "figure.facecolor": FOND, "axes.facecolor": FOND,
    "savefig.facecolor": FOND, "axes.edgecolor": GRILLE, "axes.labelcolor": ENCRE2, "axes.titlecolor": ENCRE,
    "axes.titlesize": 11.5, "axes.titleweight": "semibold", "axes.titlelocation": "left", "xtick.color": ENCRE2, "ytick.color": ENCRE2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRILLE, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "legend.frameon": False, "axes.unicode_minus": True,
})


def fr(x, dec=1, signe=False):
    s = f"{x:+,.{dec}f}" if signe else f"{x:,.{dec}f}"
    return s.replace(",", " ").replace(".", ",").replace("-", "−")


def lire(chemin):
    return json.loads((RACINE / chemin).read_text(encoding="utf-8"))


def note(fig, texte, y=0.01):
    fig.text(0.01, y, texte, ha="left", va="bottom", fontsize=8.5, color=DISCRET)


def sauver(fig, sortie, nom):
    chemin = sortie / nom
    fig.savefig(chemin, dpi=200)
    plt.close(fig)
    return chemin


# 1. Contexte de taux ------------------------------------------------------------------------------
def contexte_taux(sortie):
    with open(RACINE / "data" / "v5" / "marche" / "eiopa_rfr_20261031_eur.csv", encoding="utf-8") as fh:
        lignes = [r for r in csv.DictReader(fh) if int(r["maturite"]) <= 50]
    m = [int(r["maturite"]) for r in lignes]
    sans = [100 * float(r["taux_sans_va"]) for r in lignes]
    avec = [100 * float(r["taux_avec_va"]) for r in lignes]
    from src.courbes import CourbeAvecSpread
    from src.v5.courbes_marche import courbe_eiopa, spread_obligations
    oblig = CourbeAvecSpread(courbe_eiopa(), spread_obligations())
    ob = [100 * oblig.taux_zc(k) for k in m]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.2)
    ax.plot(m, sans, color=FAV, lw=2, label="EIOPA sans VA (observée)")
    ax.plot(m, avec, color=FAV, lw=2, ls=(0, (4, 2)), label="EIOPA avec VA (VA de 20 pb, observée)")
    ax.plot(m, ob, color=DEFAV, lw=2, label="Obligations du modèle : EIOPA sans VA + spread hypothétique")
    for k in (10, 30):
        ax.annotate(fr(ob[k - 1], 2) + " %", (k, ob[k - 1]), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=ENCRE2)
    ax.annotate(fr(sans[9], 2) + " %", (10, sans[9]), textcoords="offset points", xytext=(0, -15), ha="center", fontsize=9, color=ENCRE2)
    ax.set_xlim(0, 51)
    ax.set_ylim(2.5, 5.5)
    ax.set_xlabel("Maturité (ans)")
    ax.set_ylabel("Taux zéro-coupon (%)")
    ax.yaxis.set_major_formatter(lambda v, _: fr(v, 1))
    ax.set_title("Courbe sans risque EIOPA au 31/10/2026 et courbe des obligations du modèle")
    ax.legend(loc="lower right", fontsize=9.5)
    note(fig, "EIOPA : taux zéro-coupon observés (composition annuelle), UFR 3,30 %, LLP 20 ans. Spread des obligations : hypothèse, moyenne de long terme\n"
              "des spreads publiée par l'EIOPA (notation A), pas un spread de marché observé (data/v5/marche/spread_hypothetique_20261031.json). Source : EIOPA.")
    return sauver(fig, sortie, "contexte_taux.png")


# 2. Réconciliation de la collecte --------------------------------------------------------------------
def reconciliation(sortie):
    rec = lire("resultats/v5_reconciliation_collecte.json")
    pl, mo = rec["place_2025"]["en_pct_pm_debut"], rec["modele"]["B"]
    postes = [("Collecte brute", pl["collecte_brute"], mo["collecte_brute"]["annee_1"]),
              ("Prestations", -pl["prestations_implicites"], -mo["prestations"]["annee_1"]),
              ("Collecte nette", pl["collecte_nette"], mo["collecte_nette"]["annee_1"]),
              ("Intérêts crédités", pl["interets_credites_approx"], mo["interets_credites"]["annee_1"]),
              ("Prélèvements sociaux", -pl["prelevements_sociaux_approx"], None),
              ("Autres mouvements", pl["autres_mouvements_residu"], None),
              ("Variation de la PM", pl["variation_pm"], mo["variation_pm"]["annee_1"])]
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    fig.subplots_adjust(left=0.2, right=0.97, top=0.9, bottom=0.2)
    y = list(range(len(postes)))[::-1]
    h = 0.36
    for i, (lib, vp, vm) in enumerate(postes):
        ax.barh(y[i] + h / 2, 100 * vp, height=h - 0.04, color=DISCRET, label="Place 2025 (observé ou dérivé, voir la note)" if i == 0 else None)
        ax.text(100 * vp + (0.12 if vp >= 0 else -0.12), y[i] + h / 2, fr(100 * vp, 2) + " %", va="center", ha="left" if vp >= 0 else "right", fontsize=8.5, color=ENCRE2)
        if vm is None:
            ax.text(0.12, y[i] - h / 2, "non modélisé", va="center", ha="left", fontsize=8.5, color=DISCRET, style="italic")
        else:
            ax.barh(y[i] - h / 2, 100 * vm, height=h - 0.04, color=FAV, label="Modèle, profil B, année 1 (simulé)" if i == 0 else None)
            ax.text(100 * vm + (0.12 if vm >= 0 else -0.12), y[i] - h / 2, fr(100 * vm, 2) + " %", va="center", ha="left" if vm >= 0 else "right", fontsize=8.5, color=ENCRE2)
    ax.set_yticks(y, [p[0] for p in postes])
    ax.axvline(0, color=ENCRE2, lw=0.8)
    ax.set_xlim(-11.5, 12.5)
    ax.xaxis.set_major_formatter(lambda v, _: fr(v, 0) + " %")
    ax.grid(axis="y", visible=False)
    ax.set_title("Collecte 2025 : la place et le modèle (en % de la PM de début d'année)")
    ax.legend(loc="lower left", fontsize=9)
    note(fig, "Place, observé : encours des contrats individuels en euros (ACPR n° 180), flux des supports en euros (France Assureurs). Dérivé : intérêts\n"
              "(2,63 % x PM moyenne), prélèvements sociaux (17,2 % des intérêts), autres mouvements (résidu). Modèle : gestion passive, c0 = 6 %, g = 1,\n"
              "probabilité réelle (resultats/v5_reconciliation_collecte.json).")
    return sauver(fig, sortie, "reconciliation_collecte.png")


# 3. Capital et valeur par profil -------------------------------------------------------------------
def capital_valeur(sortie):
    K, R = lire("resultats/v5_consolidation.json"), lire("resultats/v5_collecte.json")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 4.4), gridspec_kw={"width_ratios": [1, 1.35]})
    fig.subplots_adjust(left=0.07, right=0.98, top=0.8, bottom=0.2, wspace=0.28)
    for i, p in enumerate(N):
        c = K["capital"][f"{p}|passive"]
        v, lo, hi = c["besoin"]["1.0"], c["incertitude"]["1.0"]["q025"], c["incertitude"]["1.0"]["q975"]
        a1.bar(i, v, width=0.6, color=PROFIL[p])
        a1.errorbar(i, v, yerr=[[v - lo], [hi - v]], color=ENCRE, capsize=4, lw=1)
        a1.text(i, hi + 3, fr(v), ha="center", va="bottom", fontsize=9.5, color=ENCRE)
    a1.set_xticks(range(3), [NOMS_PROFILS[p].split(" : ")[0] for p in N])
    a1.set_ylim(0, 135)
    a1.grid(axis="x", visible=False)
    a1.set_title("Apport pour 100 % du SCR simplifié")
    a1.set_ylabel("Unités (1 unité = 10 M€)")
    x = range(3)
    ex = [R["risque_neutre"][f"{p}|passive|0|0"]["valeur_existant"]["moyenne"] for p in N]
    nb = [R["risque_neutre"][f"{p}|passive|0.06|0.5"]["valeur_affaires_nouvelles"]["moyenne"] for p in N]
    w = 0.36
    a2.bar([i - w / 2 for i in x], ex, width=w - 0.03, color=DISCRET, label="Valeur de l'existant")
    a2.bar([i + w / 2 for i in x], nb, width=w - 0.03, color=FAV, label="Valeur des affaires nouvelles")
    for i in x:
        a2.text(i - w / 2, ex[i] + (2 if ex[i] >= 0 else -2), fr(ex[i]), ha="center", va="bottom" if ex[i] >= 0 else "top", fontsize=9.5, color=ENCRE)
        a2.text(i + w / 2, nb[i] + 2, fr(nb[i]), ha="center", va="bottom", fontsize=9.5, color=ENCRE)
    a2.axhline(0, color=ENCRE2, lw=0.8)
    a2.set_xticks(list(x), [NOMS_PROFILS[p] for p in N], fontsize=9)
    a2.set_ylim(-35, 90)
    a2.grid(axis="x", visible=False)
    a2.set_title("Gestion passive : valeurs pour l'actionnaire")
    a2.legend(loc="upper left", fontsize=9)
    fig.suptitle("Même marché, bilans différents : capital à l'ouverture et valeur", x=0.07, ha="left", fontsize=12.5, fontweight="semibold", color=ENCRE)
    note(fig, "Apport : vue prudentielle simplifiée, base avec VA, intervalle à 95 % par rééchantillonnage ; indicateur simplifié, pas un ratio réglementaire. Valeurs : risque neutre,\n"
              "base sans VA, nettes de l'apport et de l'impôt ; affaires nouvelles : c0 = 6 %, eta = 0,5. Profils fictifs (resultats/v5_consolidation.json, resultats/v5_collecte.json).")
    return sauver(fig, sortie, "capital_valeur_profils.png")


# 4. Écarts de valeur totale ------------------------------------------------------------------------
def couleur_verdict(v):
    if v == "défavorable, robuste":
        return DEFAV, "Défavorable, robuste"
    if v == "favorable, robuste":
        return FAV, "Favorable, robuste"
    if v == "sans effet important":
        return NEUTRE, "Sans effet important"
    return ENCRE2, "Dépend des hypothèses (signe, importance ou précision)"


def ecarts_valeur_totale(sortie):
    S = lire("resultats/v5_synthese_finale.json")
    codes = list(COURT)
    fig, axes = plt.subplots(1, 3, figsize=(11, 5.7), sharey=True)
    fig.subplots_adjust(left=0.19, right=0.99, top=0.84, bottom=0.31, wspace=0.08)
    vus = {}
    for ax, p in zip(axes, N):
        s = S["seuils"][p]
        ax.axvspan(-s, s, color=NEUTRE_CLAIR, zorder=0)
        ax.axvline(0, color=ENCRE2, lw=0.8)
        for j, c in enumerate(codes):
            x = S["valeur_totale"][f"{p}|{c}"]
            yy = len(codes) - 1 - j
            col, lib = couleur_verdict(x["verdict"])
            vus[lib] = col
            ax.plot([x["min"], x["max"]], [yy, yy], color=col, lw=5, solid_capstyle="round", alpha=0.55)
            m, hh = x["centre"]["moyenne"], x["centre"]["demi_intervalle_95"]
            ax.errorbar(m, yy, xerr=hh, fmt="o", color=col, ms=6, mec=FOND, mew=1.2, capsize=2.5, lw=1)
        ax.set_title(NOMS_PROFILS[p], fontsize=10.5)
        ax.set_xlim(-32, 18)
        ax.grid(axis="y", visible=False)
        ax.xaxis.set_major_formatter(lambda v, _: fr(v, 0))
    axes[0].set_yticks(range(len(codes)), [COURT[c] for c in codes][::-1])
    axes[1].set_xlabel("Écart de valeur totale à la gestion passive (unités)")
    poignees = [Patch(color=c, label=l) for l, c in vus.items()] + [Patch(color=NEUTRE_CLAIR, label="Zone sous le seuil d'importance (2 % du SCR)")]
    fig.legend(handles=poignees, loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.58, 0.085))
    fig.suptitle("Ce qui résiste aux hypothèses de collecte et de rachat, et ce qui n'y résiste pas", x=0.01, ha="left", fontsize=12.5, fontweight="semibold", color=ENCRE)
    note(fig, "Barre : plage des écarts moyens sur 20 configurations (c0 de 3 % à 10 %, eta de 0 à 1,5, loi de rachat ONC maximale). Point : configuration centrale (c0 = 6 %, eta = 0,5)\n"
              "et intervalle apparié à 95 %. Robuste : borne de l'intervalle au-delà du seuil dans toutes les configurations. Risque neutre, capital à 100 %, profils fictifs (resultats/v5_synthese_finale.json).")
    return sauver(fig, sortie, "ecarts_valeur_totale.png")


# 5. Politique de marge et élasticité --------------------------------------------------------------
def marge_elasticite(sortie):
    R, S = lire("resultats/v5_collecte.json"), lire("resultats/v5_synthese_finale.json")
    etas = list(R["elasticites"].values())
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.3), sharey=True)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.8, bottom=0.27, wspace=0.08)
    for ax, p in zip(axes, N):
        e = [R["ecarts"][f"{p}|taux_servi_marge|0.06|{eta}"]["totale"] for eta in etas]
        o = [R["sensibilite_onc_max"][f"{p}|taux_servi_marge|0.06|{eta}"]["ecart_totale"] for eta in etas]
        ferme = R["ecarts"][f"{p}|taux_servi_marge|0|0"]["existant"]["moyenne"]
        s = S["seuils"][p]
        ax.axhspan(-s, s, color=NEUTRE_CLAIR, zorder=0)
        ax.axhline(0, color=ENCRE2, lw=0.8)
        ax.axhline(ferme, color=DISCRET, lw=1.2, ls=(0, (1, 2)), label="Portefeuille fermé")
        ax.fill_between(etas, [x["moyenne"] - x["demi_intervalle_95"] for x in e], [x["moyenne"] + x["demi_intervalle_95"] for x in e], color=PROFIL[p], alpha=0.18, lw=0)
        ax.plot(etas, [x["moyenne"] for x in e], color=PROFIL[p], lw=2, marker="o", ms=5, mec=FOND, label="Collecte centrale (c0 = 6 %)")
        ax.plot(etas, [x["moyenne"] for x in o], color=PROFIL[p], lw=1.5, ls=(0, (4, 2)), label="Idem, loi de rachat ONC maximale")
        ax.text(etas[-1], ferme + 0.4, "fermé " + fr(ferme), ha="right", va="bottom", fontsize=8.5, color=DISCRET)
        ax.set_title(NOMS_PROFILS[p], fontsize=10.5)
        ax.set_xticks(etas, [fr(x, 2 if round(x, 1) != x else 1) for x in etas])
        ax.set_ylim(-3, 16)
        ax.grid(axis="x", visible=False)
        ax.set_xlabel("Élasticité eta de la collecte")
    axes[0].set_ylabel("Écart de valeur totale (unités)")
    h = [Line2D([], [], color=DISCRET, lw=1.2, ls=(0, (1, 2))), Line2D([], [], color=ENCRE2, lw=2, marker="o", ms=5, mec=FOND),
         Line2D([], [], color=ENCRE2, lw=1.5, ls=(0, (4, 2))), Patch(color=NEUTRE_CLAIR)]
    l = ["Portefeuille fermé", "Collecte centrale (c0 = 6 %), bande à 95 %", "Idem, loi de rachat ONC maximale", "Sous le seuil d'importance"]
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.53, 0.08))
    fig.suptitle("Politique de marge : écart positif sur la grille, ampleur liée à la réaction de la collecte", x=0.01, ha="left", fontsize=12, fontweight="semibold", color=ENCRE)
    note(fig, "Écart à la gestion passive, risque neutre, capital à 100 %, tirages appariés. eta : non calibrée, plage testée. Hypothèses de collecte hors de cette grille\n"
              "(e0, horizon de collecte) : docs/V5_SYNTHESE_FINALE.md, section 2. Profils fictifs (resultats/v5_collecte.json).")
    return sauver(fig, sortie, "marge_elasticite.png")


# 6. Matrice des arbitrages ---------------------------------------------------------------------------
DIM = [("existant", "Valeur de\nl'existant"), ("affaires_nouvelles", "Affaires\nnouvelles"), ("valeur_totale", "Valeur totale\n(20 config.)"),
       ("rentabilite", "Rentabilité\n(réel)"), ("competitivite", "Taux servi\n(réel)"), ("liquidite", "Liquidité\n(réel)"), ("capital_ouverture", "Capital à\nl'ouverture")]


def cellule(dim, x):
    if dim == "valeur_totale":
        v = x["lecture"]
        return {"défavorable, robuste": (DEFAV_CLAIR, "défavorable\nrobuste"), "favorable, robuste": (FAV_CLAIR, "favorable\nrobuste"),
                "sans effet important": (NEUTRE_CLAIR, "sans effet"), "change de signe selon les hypothèses": ("#ffffff", "change\nde signe"),
                "toujours positif, non robuste": ("#ffffff", "positif\nnon robuste"), "toujours négatif, non robuste": ("#ffffff", "négatif\nnon robuste"),
                "positif là où il est significatif, non robuste": ("#ffffff", "positif si\nsignificatif"),
                "négatif là où il est significatif, non robuste": ("#ffffff", "négatif si\nsignificatif"),
                "non concluant (aucun écart significatif, signes mêlés)": ("#ffffff", "non\nconcluant")}[v]
    lec, e = x["lecture"], x["ecart"]
    if dim == "rentabilite":
        txt = fr(100 * e, 2, True) + " pt"
    elif dim == "competitivite":
        txt = fr(1e4 * e, 0, True) + " pb"
    else:
        txt = fr(e, 1, True)
    if x.get("non_significatif"):
        txt += " ns"
    return {"favorable": FAV_CLAIR, "défavorable": DEFAV_CLAIR, "neutre": NEUTRE_CLAIR}[lec], f"{lec}\n{txt}"


def matrice(sortie):
    S = lire("resultats/v5_synthese_finale.json")
    codes = list(COURT)
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 13.2))
    fig.subplots_adjust(left=0.2, right=0.99, top=0.91, bottom=0.07, hspace=0.32)
    for ax, p in zip(axes, N):
        for j, c in enumerate(codes):
            for i, (dim, _) in enumerate(DIM):
                fond, txt = cellule(dim, S["matrice"][f"{p}|{c}"][dim])
                ax.add_patch(plt.Rectangle((i + 0.03, len(codes) - 1 - j + 0.04), 0.94, 0.92, color=fond, ec=GRILLE, lw=0.8))
                ax.text(i + 0.5, len(codes) - 1 - j + 0.5, txt, ha="center", va="center", fontsize=8, color=ENCRE, linespacing=1.15)
        ax.set_xlim(0, len(DIM))
        ax.set_ylim(0, len(codes))
        ax.set_xticks([i + 0.5 for i in range(len(DIM))], [d[1] for d in DIM], fontsize=8.5)
        ax.xaxis.tick_top()
        ax.set_yticks([j + 0.5 for j in range(len(codes))], [COURT[c] for c in codes][::-1], fontsize=9)
        ax.tick_params(length=0)
        ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(f"Profil {NOMS_PROFILS[p]}", pad=34, fontsize=11)
    fig.suptitle("Arbitrages : écarts à la gestion passive, dimension par dimension", x=0.01, y=0.985, ha="left", fontsize=13, fontweight="semibold", color=ENCRE)
    note(fig, "Bleu : favorable ; rouge : défavorable ; gris : sous le seuil d'importance ou non significatif (ns) ; blanc : la valeur totale dépend des hypothèses. Valeurs en unités\n"
              "(1 unité = 10 M€), rentabilité en points, taux servi en points de base ; liquidité : moins-values réalisées q99 sur 1 000 scénarios, sans intervalle (une hausse est défavorable) ;\n"
              "capital : apport à 100 %. Collecte centrale (c0 = 6 %, eta = 0,5) pour les affaires nouvelles et la probabilité réelle. Profils fictifs (resultats/v5_synthese_finale.json).", y=0.005)
    return sauver(fig, sortie, "matrice_arbitrages.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", default=str(RACINE / "figures" / "v5"))
    a = ap.parse_args()
    sortie = Path(a.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    for fn in (contexte_taux, reconciliation, capital_valeur, ecarts_valeur_totale, marge_elasticite, matrice):
        print("écrit :", fn(sortie))


if __name__ == "__main__":
    main()
