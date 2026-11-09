"""Génère docs/V5_COLLECTE.md depuis resultats/v5_collecte.json (scripts/v5_collecte.py) et
resultats/v5_consolidation.json. Les phrases sont écrites ici ; tous les chiffres et tous les jugements
(signe, importance, robustesse, majorant) viennent des résultats et des critères de src/v5/collecte.py.

Usage : python scripts/v5_rapport_collecte.py [--entree resultats/v5_collecte.json] [--sortie docs/V5_COLLECTE.md]
"""

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import collecte as col, strategies as stg  # noqa: E402
from src.v5.profils import hypotheses_profil  # noqa: E402

N = "ABC"
COURT = {"passive": "Passive", "reinvestissement_progressif": "Réinvestissement progressif", "repositionnement": "Repositionnement",
         "taux_servi_competitif": "Taux servi compétitif", "taux_servi_marge": "Taux servi de marge", "liquidite_defensive": "Liquidité défensive",
         "taux_servi_competitif_preservant": "Compétitif préservant la PPB", "distribution_retention": "Rétention de capital"}
POLITIQUES = ("taux_servi_marge", "taux_servi_competitif", "taux_servi_competitif_preservant")
NOMS_ELA = {"nulle": "nulle", "moderee": "modérée", "intermediaire": "intermédiaire", "soutenue": "soutenue", "forte": "forte"}


def f(x, dec=1):
    if round(x, dec) == 0:
        x = 0.0
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def pm_(s, dec=1):
    return f"{f(s['moyenne'], dec)} ± {f(s['demi_intervalle_95'], dec)}"


def minuscule(t):
    return t[:1].lower() + t[1:]


ap = argparse.ArgumentParser()
ap.add_argument("--entree", default=str(RACINE / "resultats" / "v5_collecte.json"))
ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_COLLECTE.md"))
ARGS = ap.parse_args()
R = json.loads(Path(ARGS.entree).read_text(encoding="utf-8"))
K = json.loads((RACINE / "resultats" / "v5_consolidation.json").read_text(encoding="utf-8"))
REC = json.loads((RACINE / "resultats" / "v5_reconciliation_collecte.json").read_text(encoding="utf-8"))
SC = REC["seuil_cout_capital"]
P = col.charger()
LECT = stg.charger()["lecture"]
CODES = R["strategies"]
AUTRES = [c for c in CODES if c != "passive"]
INT, ELA = R["intensites"], R["elasticites"]
C0C, ETAM = INT["centrale"], ELA["moderee"]
GRILLE = [(c0, eta) for c0 in INT.values() for eta in ELA.values()]
SENS = {k: v for k, v in P["sensibilites"].items() if not k.startswith("_")}
COURT_SENS = {"e0_moins_50pb": "e0 = −0,5 point", "horizon_30": "collecte 30 ans", "horizon_60": "collecte 60 ans"}


def k(*parts):
    return "|".join(str(x) for x in parts)


def rn(p, c, c0=0, eta=0):
    return R["risque_neutre"][k(p, c, c0, eta)]


def ec(p, c, c0, eta):
    return R["ecarts"][k(p, c, c0, eta)]


def re_(p, c, c0=0, eta=0):
    return R["reel"][k(p, c, c0, eta)]


def onc(p, c, eta):
    return R["sensibilite_onc_max"][k(p, c, C0C, eta)]


def scr(p):
    return K["prudentiel"][f"{p}|passive"]["apport_0"]["scr"]


def seuil(p):
    return LECT["valeur_nette_pct_scr"] * scr(p)


def lecture(s, p):
    m, h = s["moyenne"], s["demi_intervalle_95"]
    if abs(m) <= h:
        return "ns"
    if abs(m) < seuil(p):
        return "+, non important" if m > 0 else "−, non important"
    if abs(m) - h < seuil(p):
        return "**+**, borne sous le seuil" if m > 0 else "**−**, borne sous le seuil"
    return "**+**" if m > 0 else "**−**"


def libelle(c0, eta):
    return f"c0 {pct(c0, 0)}, eta {f(eta, 2 if round(eta, 1) != eta else 1)}"


def feta(eta):
    return f(eta, 2 if round(eta, 1) != eta else 1)


def ecarts_grille(p, c):
    """Écarts de valeur totale sur toute la grille et sous ONC maximale (intensité centrale)."""
    return [ec(p, c, c0, eta)["totale"] for c0, eta in GRILLE] + [onc(p, c, eta)["ecart_totale"] for eta in ELA.values()]


def robustesse(p, c):
    return col.robustesse(ecarts_grille(p, c), seuil(p))


L = []
A = L.append

# ------------------------------------------------------------------------------------------------
A("# V5 : collecte nouvelle et stratégies ALM\n")
A(f"Généré par `scripts/v5_rapport_collecte.py` depuis `resultats/v5_collecte.json` (`scripts/v5_collecte.py`), `resultats/v5_consolidation.json` et `resultats/v5_reconciliation_collecte.json` (`scripts/v5_reconciliation_collecte.py`). Spécification : `docs/V5_SPECIFICATION_COLLECTE.md`. "
  f"Risque neutre : {f(R['n_scenarios'], 0)} scénarios, base sans VA, mêmes scénarios et mêmes tirages de défaut pour toutes les stratégies, intensités et élasticités. Unités fictives : 1 unité = 10 M€. "
  "**Profils fictifs, première version volontairement simple du modèle de collecte : analyse exploratoire, conditionnelle aux hypothèses, ce n'est pas une recommandation.**\n")
A("**Base de capital commune.** Chaque stratégie garde l'apport qui porte son propre indicateur de couverture simplifié du SCR à 100 % (`docs/V5_STRATEGIES.md`, section 2). Cet apport est calculé sur l'existant en extinction, dans la frontière des contrats : la collecte ne le modifie pas (test `test_vue_prudentielle_dans_la_frontiere_des_contrats`). "
  "C'est une convention simplifiée : la vue prudentielle exclut les primes et les contrats futurs, mais aussi les effets que la collecte peut avoir sur les hypothèses de projection de l'existant (politique d'investissement, produits financiers, frais), que ce document analyse séparément dans la vue économique ; un calcul Solvabilité II complet peut devoir en tenir compte.\n")
A("**Trois valeurs, toujours séparées** (risque neutre, nettes de l'apport, des apports ultérieurs et de l'impôt) :\n")
A("- *valeur de l'existant* : portefeuille en extinction (c0 = 0), c'est la valeur nette des documents précédents ;")
A("- *valeur des affaires nouvelles* (valeur de franchise, hors Solvabilité II) = valeur totale - valeur de l'existant, sur les mêmes scénarios ;")
A("- *valeur totale* pour l'actionnaire, avec collecte.\n")
A("La valeur des affaires nouvelles se répartit, scénario par scénario, entre trois termes : les **flux des contrats nouveaux** (VA des primes - BE des contrats nouveaux, c'est-à-dire ce que ces contrats reçoivent dans le fonds mutualisé), "
  "la **variation du BE de l'existant**, comptée pour l'actionnaire, et l'**impôt supplémentaire**. Seule la somme s'interprète comme une valeur : un transfert entre générations d'assurés (PPB d'ouverture, coupons anciens, garanties) déplace les deux premiers termes en sens inverse, sans changer la somme (section 6).\n")
A("**Lecture des écarts** à la gestion passive (mêmes scénarios, intervalle apparié à 95 %) : « ns » non significatif ; « +, non important » ou « −, non important » significatif mais sous le seuil d'importance "
  f"({pct(LECT['valeur_nette_pct_scr'], 0)} du SCR simplifié du profil : " + ", ".join(f"{f(seuil(p))} pour {p}" for p in N) + ") ; **+** ou **−** au-delà du seuil, « borne sous le seuil » si la borne de l'intervalle ne le dépasse pas. "
  "« Robuste » : borne de l'intervalle au-delà du seuil dans toutes les configurations (trois intensités, cinq élasticités, et la loi de rachat ONC maximale à l'intensité centrale).\n")

# ------------------------------------------------------------------------------------------------
A("## 1. Hypothèses de collecte et contrôles\n")
A("| Paramètre | Valeur | Statut |\n| --- | --- | --- |")
for nom, v in INT.items():
    x = P["intensites"][nom]
    A(f"| Intensité {nom} c0 | {pct(v, 0)} de la PM par an | {x['statut']}" + (f" : {x['regle']}" if "regle" in x else (f" : {x['note']}" if "note" in x else "")) + " |")
for nom, v in ELA.items():
    A(f"| Élasticité {NOMS_ELA.get(nom, nom)} eta | {feta(v)} par point de taux servi relatif | {P['elasticites'][nom]['statut']} |")
A(f"| Horizon de collecte | {P['horizon_collecte_ans']['valeur']} ans, puis extinction ; sensibilités à 30 et 60 ans | {P['horizon_collecte_ans']['statut']} |")
A(f"| Réaction g(e) | g = min({f(P['reaction']['g_max']['valeur'], 0)} ; max({f(P['reaction']['g_min']['valeur'], 0)} ; 1 + eta x (e - e0) / 1 point)), e = taux servi sur les contrats nouveaux - référence | fictif |")
A(f"| e0 | {pct(P['reaction']['e0']['valeur'], 1)} ; sensibilité -0,5 point | {P['reaction']['e0']['statut']} : {P['reaction']['e0']['note']} |")
cn = P["contrats_nouveaux"]
A(f"| Contrats nouveaux | TMG {pct(cn['tmg']['valeur'], 1)}, chargement sur prime {pct(cn['chargement_prime']['valeur'], 1)}, frais d'acquisition {pct(cn['frais_acquisition_prime']['valeur'], 1)} de la prime ; chargements et frais sur encours, loi de rachat et mortalité de l'existant | fictif |")
A("")
A("Sources des agrégats observés : " + " ; ".join(P["sources"].values()) + ". Ces agrégats portent sur une seule année.\n")

# Réconciliation des flux 2025 (scripts/v5_reconciliation_collecte.py)
PL, MO = REC["place_2025"], REC["modele"]
PP = PL["en_pct_pm_debut"]
A("### Réconciliation avec les flux de la place en 2025\n")
A("En % de la PM de début d'année. Place : encours des contrats individuels en euros (ACPR), flux des supports en euros (France Assureurs), périmètres non strictement identiques ; observé, sauf les intérêts crédités (taux moyen appliqué à la moyenne des PM de début et de fin, approximation), les prélèvements sociaux "
  f"({pct(PL['taux_prelevements_sociaux'], 1)} des intérêts, prélevés chaque année) et les autres mouvements (résidu de l'identité). Modèle : gestion passive, intensité centrale c0 = {pct(REC['c0_central'], 0)}, eta = 0 (donc g = 1), "
  f"probabilité réelle, {f(REC['n_scenarios_reels'], 0)} scénarios ; année 1 et moyenne des années 1 à 10. Calcul : `scripts/v5_reconciliation_collecte.py`, `resultats/v5_reconciliation_collecte.json`.\n")
A("| Poste | Place 2025, Md€ | Place 2025, % PM | Modèle, année 1 (A / B / C) | Modèle, moyenne 1-10 (A / B / C) |\n| --- | ---: | ---: | ---: | ---: |")


def mod(cle):
    return (" / ".join(pct(MO[p][cle]["annee_1"], 2) for p in N), " / ".join(pct(MO[p][cle]["moyenne_1_10"], 2) for p in N))


for lib, md, cp, cm in [
    ("Collecte brute", PL["collecte_brute"], PP["collecte_brute"], "collecte_brute"),
    ("Prestations (décès et rachats)", -PL["prestations_implicites"], -PP["prestations_implicites"], "prestations"),
    ("**Collecte nette**", PL["collecte_nette"], PP["collecte_nette"], "collecte_nette"),
    ("Intérêts crédités (avant prélèvements sociaux)", PL["interets_credites_approx"], PP["interets_credites_approx"], "interets_credites"),
    ("Prélèvements sociaux", -PL["prelevements_sociaux_approx"], -PP["prelevements_sociaux_approx"], None),
    ("Autres mouvements (résidu : périmètres, arbitrages, transferts)", PL["autres_mouvements_residu"], PP["autres_mouvements_residu"], None),
    ("**Variation de la PM**", PL["pm_fin"] - PL["pm_debut"], PP["variation_pm"], "variation_pm"),
]:
    if cm == "prestations":
        m1 = " / ".join(pct(-MO[p][cm]["annee_1"], 2) for p in N)
        m10 = " / ".join(pct(-MO[p][cm]["moyenne_1_10"], 2) for p in N)
    elif cm:
        m1, m10 = mod(cm)
    else:
        m1 = m10 = "non modélisé"
    A(f"| {lib} | {f(md)} | {pct(cp, 2)} | {m1} | {m10} |")
A(f"| PM de début ; de fin | {f(PL['pm_debut'], 0)} ; {f(PL['pm_fin'], 0)} | | | |")
A("")
sorties_mod = [MO[p]["prestations"]["annee_1"] for p in N]
nette_mod = [MO[p]["collecte_nette"]["annee_1"] for p in N]
croiss_mod = [MO[p]["variation_pm"]["annee_1"] for p in N]
servi_mod = [MO[p]["interets_credites"]["annee_1"] for p in N]
nette_forte = INT["forte"] - sum(sorties_mod) / len(sorties_mod)


def entre(vals, dec=2):
    a, b = pct(min(vals), dec), pct(max(vals), dec)
    return a if a == b else f"{a} à {b}"


A(f"**Lecture.** Avec c0 = {pct(INT['centrale'], 0)} et g = 1, le modèle approche la collecte nette de la place à environ 0,1 point près, malgré des périmètres et des flux différents ({entre(nette_mod)} la première année, contre {pct(PP['collecte_nette'], 2)}), "
  f"mais avec des flux bruts plus faibles : {pct(INT['centrale'], 1)} de primes et environ {pct(sum(sorties_mod) / len(sorties_mod), 1)} de sorties, contre {pct(PP['collecte_brute'], 1)} et {pct(PP['prestations_implicites'], 1)} pour la place. "
  f"La PM du modèle croît d'environ {pct(min(croiss_mod), 1)} la première année, contre {pct(PP['variation_pm'], 1)} observés : le modèle ne comprend ni prélèvements sociaux ({pct(PP['prelevements_sociaux_approx'], 2)} de la PM) ni autres mouvements ({pct(-PP['autres_mouvements_residu'], 2)}), "
  f"ce que compensent en partie des intérêts crédités plus faibles ({entre(servi_mod)} de la PM d'ouverture pour la gestion passive, contre environ {pct(PP['interets_credites_approx'], 2)} pour la place, approchés par le taux moyen de {pct(PL['taux_revalorisation'], 2)} appliqué à la PM moyenne).\n")
A(f"**Interprétation de c0 = {pct(INT['centrale'], 0)}.** c0 est l'intensité brute qui, compte tenu des sorties du modèle, redonne la collecte nette observée en 2025. Ce n'est ni un calibrage des flux bruts, ni un calibrage de la croissance de la PM, "
  "et une seule année ne mesure pas une collecte durable. Deux conséquences : la PM projetée, existant comme affaires nouvelles, est un peu surestimée, faute de prélèvements sociaux (qui réduiraient aussi les chargements futurs) ; "
  f"le volume brut des entrées et des sorties est plus faible que sur le marché, ce qui réduit le rôle des primes dans la liquidité. À l'intensité forte (c0 = {pct(INT['forte'], 0)}), les mêmes sorties donnent une collecte nette d'environ {pct(nette_forte, 1)} de la PM par an avec g = 1, "
  f"soit bien plus que les {pct(PP['collecte_nette'], 1)} observés : c'est une borne haute.\n")

CE, VL = REC["contrat_equitable"], REC["variantes_liquidation"]
A("### Contrat sans marge explicite dans le fonds mutualisé : origine du résidu\n")
A("Équivalent certain, gestion passive, participation de 100 %, sans PPB, chargement, frais, frais d'acquisition ni TMG, c0 = 6 %, eta = 0 (identifiant `contrat_equitable` dans les résultats). "
  "Sans marge explicite, la valeur pour l'actionnaire n'est pas nulle pour autant : elle dépend des conventions de partage et de liquidation du modèle. "
  "Le résidu mesuré, avant impôt, s'attribue exactement aux postes de fin de projection (VA des dividendes et valeurs actualisées des postes du bilan comptable final, écarts avec et sans affaires nouvelles) :\n")
A("| Profil | VA des primes | Résidu | en % des primes | VA des dividendes | Fonds propres finaux | Dividende à payer final | Réserve de capitalisation finale | Plus-values latentes finales non partagées | Moins-values obligataires réalisées (VA) : extinction / avec collecte |\n| --- | " + " | ".join("---:" for _ in range(9)) + " |")
for p in N:
    x, a_ = CE[p], CE[p]["attribution"]
    A(f"| {p} | {f(x['va_primes'])} | {f(x['residu'], 2)} | {pct(x['residu_pct_va_primes'], 2)} | {f(a_['va_dividendes'], 2)} | {f(a_['fonds_propres_final'], 2)} | {f(a_['dividende_a_payer_final'], 2)} | "
      f"{f(a_['reserve_capitalisation_finale'], 2)} | {f(a_['pvl_finales_non_partagees'], 2)} | {f(x['pmv_obligataires_realisees_va']['ferme'], 2)} / {f(x['pmv_obligataires_realisees_va']['avec_collecte'], 2)} |")
A("")
A("**Lecture.** Le résidu ne vient pas d'une création de valeur à l'actif (fuite nulle, primes investies au prix du marché) : c'est un transfert des assurés vers l'actionnaire, produit par des règles du modèle. "
  "(1) La politique de distribution garde les fonds propres comptables à leur ratio d'ouverture sur la PM : la croissance retient du capital, dont la quote-part des produits financiers revient à l'actionnaire, hors participation. "
  "(2) Les primes financent les sorties : le fonds vend moins d'obligations en moins-value ; la réserve de capitalisation n'absorbe plus ces pertes et son solde reste à l'actionnaire en fin de projection (A et C). "
  "(3) La part des plus-values latentes finales non rendue aux assurés croît avec l'actif. "
  "Cette réconciliation comptable montre où se trouve la valeur dans le modèle ; elle ne démontre pas, à elle seule, que son attribution est économiquement juste.\n")
A("**Réserve de capitalisation.** Dans le modèle, les plus ou moins-values obligataires réalisées sont portées à la réserve de capitalisation, hors assiette de la participation ; au-delà de la réserve, les moins-values passent dans le résultat financier de l'année suivante ; "
  "en fin de projection, les assurés reçoivent la PM, la PPB et leur part des plus-values latentes, et le solde de la réserve reste à l'actionnaire. "
  "Ce traitement suit le principe de l'article R.351-2-1 du Code des assurances : le calcul du BE tient compte des dotations et reprises de la réserve constituée à la date de calcul pendant la durée des engagements, "
  "et la valeur actuelle attendue de son solde en fin d'engagements est intégrée à la réserve de réconciliation, en fonds propres de base de niveau 1. "
  "Le modèle n'en reproduit pas toutes les modalités : il ne distingue pas la réserve constituée à la date de calcul des dotations futures. "
  "L'attribution des postes ci-dessus résulte donc des conventions de partage et de liquidation retenues ; ce n'est pas une validation réglementaire de leur propriété.\n")
NOMS_VL = {"rc_initiale_nulle": "Réserve initiale nulle", "sans_retention": "Sans rétention des fonds propres", "rc_initiale_nulle_sans_retention": "Les deux"}
A("**Variantes de liquidation.** Même cas, en retirant l'une ou l'autre des deux conventions : réserve de capitalisation d'ouverture reclassée en fonds propres comptables (actif inchangé), "
  "fonds propres comptables positifs distribués chaque année (la croissance ne retient plus de capital comptable), ou les deux. "
  "Les plus-values latentes d'ouverture restent celles du profil : les annuler demanderait un autre portefeuille, ce qui n'est pas fait. Résidu avant impôt (en % de la VA des primes) :\n")
A("| Profil | Cas de base | " + " | ".join(NOMS_VL.values()) + " | Les deux : apports évités (VA) |\n| --- | " + " | ".join("---:" for _ in range(5)) + " |")
for p in N:
    v = VL[p]
    les_deux = v["rc_initiale_nulle_sans_retention"]
    A(f"| {p} | {f(CE[p]['residu'], 2)} ({pct(CE[p]['residu_pct_va_primes'], 2)}) | " + " | ".join(f"{f(v[n]['residu'], 2)} ({pct(v[n]['residu_pct_va_primes'], 2)})" for n in NOMS_VL)
      + f" | {f(les_deux['attribution']['va_apports'], 2)} |")
A("")
neutres = [p for p in N if abs(VL[p]["rc_initiale_nulle_sans_retention"]["residu_pct_va_primes"]) < 0.001]
persist = [p for p in N if p not in neutres]
txt = "**Lecture.** "
if neutres:
    txt += (f"Sans réserve de capitalisation initiale ni rétention de capital, le résidu disparaît pour {' et '.join(neutres)} (" + " et ".join(f"{pct(VL[p]['rc_initiale_nulle_sans_retention']['residu_pct_va_primes'], 2)} des primes pour {p}" for p in neutres)
            + ") : il venait bien de ces deux conventions. ")
retention_seule = [p for p in N if VL[p]["sans_retention"]["residu"] > CE[p]["residu"]]
if retention_seule:
    txt += (f"Retirer la seule rétention l'augmente ({', '.join(retention_seule)}) : distribuer les fonds propres réduit l'actif, le fonds vend davantage d'obligations pour payer les sorties, "
            "et la réserve de capitalisation, qui absorbe ces moins-values en extinction, est davantage préservée par la collecte ; sa quote-part des produits financiers, hors participation (seule celle des provisions techniques y entre), revient à l'actionnaire. ")
for p in persist:
    x = VL[p]["rc_initiale_nulle_sans_retention"]
    ans = x["annees_avec_apport_ferme"]
    pmv = (f"en extinction, {p} vend des obligations en moins-value (VA {f(x['pmv_obligataires_realisees_va']['ferme'], 1)}, contre "
           f"{f(x['pmv_obligataires_realisees_va']['avec_collecte'], 1)} avec collecte)")
    if abs(x["attribution"]["va_apports"]) >= 0.5 * abs(x["residu"]):
        txt += (f"Pour {p}, le résidu persiste ({pct(x['residu_pct_va_primes'], 2)}), presque entièrement sous forme d'apports évités ({f(x['attribution']['va_apports'], 2)}) : "
                f"{pmv}, le taux servi atteint son plancher de {pct(x['taux_servi_min_ferme'], 0)} et, la participation ne pouvant être négative, "
                f"l'actionnaire porte les pertes au-delà de la réserve par des apports" + (f" (chaque année à partir de l'année {ans[0]})" if ans and ans == list(range(ans[0], ans[-1] + 1)) else "") + ". ")
    else:
        txt += (f"Pour {p}, le résidu persiste ({pct(x['residu_pct_va_primes'], 2)}), surtout sous forme de fonds propres finaux ({f(x['attribution']['fonds_propres_final'], 2)}) : "
                f"{pmv} ; reportées sur l'exercice suivant, ces moins-values rendent certains résultats financiers négatifs et, la participation ne pouvant être négative, "
                "l'actionnaire porte ces pertes : ses fonds propres comptables finissent négatifs dans le portefeuille fermé, sans apport. ")
    txt += ("Les primes nouvelles financent les sorties et évitent ces ventes. "
            f"C'est l'asymétrie du partage (participation jamais négative) appliquée aux moins-values latentes d'ouverture de {p}"
            + (", les plus fortes des trois profils" if x["pmvl_obligations_ouverture"] == min(VL[q]["rc_initiale_nulle_sans_retention"]["pmvl_obligations_ouverture"] for q in N) else "")
            + f" ({f(x['pmvl_obligations_ouverture'], 1)}) : un mécanisme contractuel du modèle, pas une fuite de valorisation. ")
txt += "Ce test n'est pas une preuve complète de neutralité : un seul scénario, une seule intensité, sans élasticité ; le seuil de 1 % est un choix.\n"
A(txt)
A("**Contrôles** (`tests/test_v5_collecte.py` et ce calcul) :\n")
A("- **cas limites** : c0 = 0 redonne exactement le portefeuille fermé, colonne par colonne, pour trois élasticités ; eta = 0 et c0 > 0 donnent C(t) = c0 x PM(t - 1) exactement, pour deux politiques de taux servi différentes (deux tests distincts) ;")
A("- **comptabilisation** (cas cantonné) : contrats crédités au taux sans risque du scénario, sans chargement, frais, garantie ni option, sur un compte séparé ; leur valeur est nulle par construction, ce qui contrôle la comptabilisation des primes, des prestations et de l'actualisation, sans exercer le fonds mutualisé ;")
_mr = [R["risque_neutre"][f"{p}|passive|0.06|0.0"]["marge_affaires_nouvelles"] for p in N]
A("- **contrat sans marge explicite dans le fonds mutualisé** (équivalent certain, sans chargement, frais, TMG ni PPB, participation de 100 %) : valeur des affaires nouvelles inférieure à 1 % de la VA des primes avant impôt (" + ", ".join(f"{pct(CE[p]['residu_pct_va_primes'], 2)} pour {p}" for p in N) + "), contre " + " à ".join(pct(x, 1) for x in (min(_mr), max(_mr))) + " après impôt pour les contrats réalistes (risque neutre, c0 = 6 %, eta = 0, gestion passive) ; le résidu est attribué ci-dessus, et la variante sans réserve initiale ni rétention le ramène sous 0,1 % pour " + " et ".join(neutres) + " ;")
A("- **absence d'arbitrage à l'actif** : sur l'équivalent certain, les primes investies au prix du marché ne créent ni ne détruisent de valeur (fuite inférieure à 1e-8), bilan équilibré chaque année ;")
A("- **garanties** : quand le plancher de TMG du fonds est atteint exactement, la répartition de l'intérêt conserve l'intérêt décidé (test de non-régression ; une première version, corrigée depuis, créditait alors les contrats nouveaux au taux moyen, au-delà de l'intérêt décidé, dans 189 des 112 809 décisions d'un échantillon de contrôle des profils A et B, toutes pour le profil A ; les résultats ont été recalculés) ;")
A(f"- **identité de la décomposition** : vraie par construction ; écart arithmétique maximal de {R['controles']['ecart_max_decomposition']:.0e}. Fuite moyenne au plus égale à {f(R['controles']['fuite_moyenne_max_en_demi_intervalles'], 1)} fois son demi-intervalle Monte-Carlo.\n")

# ------------------------------------------------------------------------------------------------
A("## 2. Gestion passive : valeur de l'existant, des affaires nouvelles et valeur totale\n")
A("Moyennes risque neutre ± demi-intervalle à 95 %. Marge : valeur des affaires nouvelles rapportée à la VA des primes.\n")
for p in N:
    v0 = rn(p, "passive")
    A(f"**Profil {p}** (apport {f(R['apports'][k(p, 'passive')])}, valeur de l'existant {pm_(v0['valeur_existant'])})\n")
    A("| Collecte | VA des primes | Flux des contrats nouveaux | Variation du BE de l'existant | Impôt supplémentaire | **Valeur des affaires nouvelles** | Marge | Valeur totale | Collecte 1-10 (RN) | PM année 10 (RN) |\n| --- | " + " | ".join("---:" for _ in range(9)) + " |")
    for c0, eta in GRILLE:
        x = rn(p, "passive", c0, eta)
        A(f"| {libelle(c0, eta)} | {f(x['va_primes']['moyenne'])} | {f(x['flux_contrats_nouveaux']['moyenne'])} | {f(x['variation_be_existant']['moyenne'])} | {f(x['impot_supplementaire']['moyenne'])} | "
          f"**{pm_(x['valeur_affaires_nouvelles'])}** | {pct(x['marge_affaires_nouvelles'])} | {pm_(x['valeur_totale'])} | {f(x['collecte_1_10_moyenne'])} | {f(x['pm_annee_10_moyenne'], 0)} |")
    A(f"| Extinction (c0 = 0) | - | - | - | - | - | - | {pm_(v0['valeur_existant'])} | - | {f(v0['pm_annee_10_moyenne'], 0)} |")
    A("")
neg = [(p, c0, eta) for p in N for c0, eta in GRILLE if rn(p, "passive", c0, eta)["valeur_affaires_nouvelles"]["moyenne"] < 0]
impot = {}
for p in N:
    x = rn(p, "passive", C0C, ETAM)
    avant = x["flux_contrats_nouveaux"]["moyenne"] + x["variation_be_existant"]["moyenne"]
    b = hypotheses_profil(p)["bilan_initial"]
    impot[p] = (-x["impot_supplementaire"]["moyenne"] / avant if avant > 0 else float("nan"), (b["fonds_propres"] + R["apports"][k(p, "passive")]) / b["pm"])
A("**Lecture.** " + ("Les affaires nouvelles de la gestion passive ont une valeur positive dans toutes les configurations testées. " if not neg else
                     "Les affaires nouvelles de la gestion passive ont une valeur négative pour : " + ", ".join(f"{p} ({libelle(c0, eta)})" for p, c0, eta in neg) + ". ")
  + "La variation d'impôt représente " + ", ".join(f"{pct(v[0], 0)} ({p})" for p, v in impot.items()) + " de la valeur avant impôt (intensité centrale, élasticité modérée), bien plus que le taux nominal de l'impôt sur les sociétés. "
  "L'origine de cet écart n'est pas isolée : une explication possible est l'impôt sur les revenus du capital que la politique de distribution retient avec la croissance, au ratio d'ouverture fonds propres et apport sur PM (" + ", ".join(f"{pct(v[1])} pour {p}" for p, v in impot.items()) + ") ; la décomposition ne sépare pas cet effet. "
  "C'est une valeur **avant coût explicite de mobilisation du capital additionnel** : seuls l'impôt et la participation sur les revenus des fonds propres conservés sont déduits ; pas de marge pour risques non couvrables, frais d'acquisition fictifs. "
  "Une charge frictionnelle annuelle de " + ", ".join(f"{pct(SC[p]['kappa_seuil'], 1)} ({p})" for p in N) + " du SCR proxy des affaires nouvelles suffirait à annuler la valeur centrale (analyse de seuil, section 8).\n")

# ------------------------------------------------------------------------------------------------
A("## 3. La politique de marge reste-t-elle avantageuse ?\n")
A("Écarts de la politique de marge (taux servi visé égal à la référence moins 1 point) à la gestion passive, mêmes scénarios. « Majorant » : l'avantage en portefeuille fermé majore l'avantage avec collecte si l'écart de valeur des affaires nouvelles est significativement négatif (« oui ») ; « non » s'il est significativement positif ; « indéterminé » s'il reste dans son intervalle. "
  "Marge qui annulerait l'avantage : avantage en portefeuille fermé rapporté à la VA des primes perdues par la politique de marge, à comparer à la marge effective des affaires nouvelles de la gestion passive ; indicateur de premier ordre, qui ignore le gain de marge sur les contrats encore collectés.\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Collecte | Existant (portefeuille fermé) | Affaires nouvelles | **Valeur totale** | Lecture | Majorant ? | Facteur de collecte moyen 1-10 (marge / passive) | Marge qui annulerait l'avantage / marge de la gestion passive |\n| --- | ---: | ---: | ---: | --- | --- | ---: | ---: |")
    for c0, eta in GRILLE:
        e = ec(p, "taux_servi_marge", c0, eta)
        perte = rn(p, "passive", c0, eta)["va_primes"]["moyenne"] - rn(p, "taux_servi_marge", c0, eta)["va_primes"]["moyenne"]
        seuil_marge = (f"{pct(e['existant']['moyenne'] / perte)} / {pct(rn(p, 'passive', c0, eta)['marge_affaires_nouvelles'])}"
                       if perte > 0.01 * rn(p, "passive", c0, eta)["va_primes"]["moyenne"] else "-")
        A(f"| {libelle(c0, eta)} | {pm_(e['existant'])} | {pm_(e['affaires_nouvelles'])} | **{pm_(e['totale'])}** | {lecture(e['totale'], p)} | {col.etat_majorant(e['affaires_nouvelles'])} | "
          f"{f(rn(p, 'taux_servi_marge', c0, eta)['facteur_collecte_moyen_1_10'], 2)} / {f(rn(p, 'passive', c0, eta)['facteur_collecte_moyen_1_10'], 2)} | {seuil_marge} |")
    for eta in ELA.values():
        s = onc(p, "taux_servi_marge", eta)
        A(f"| ONC max., {libelle(C0C, eta)} | {pm_(s['ecart_existant'])} | {pm_(s['ecart_affaires_nouvelles'])} | **{pm_(s['ecart_totale'])}** | {lecture(s['ecart_totale'], p)} | {col.etat_majorant(s['ecart_affaires_nouvelles'])} | - | - |")
    A("")
A("**Lecture.**\n")
for p in N:
    e_eta = {eta: ec(p, "taux_servi_marge", C0C, eta)["totale"] for eta in ELA.values()}
    pire = min(ecarts_grille(p, "taux_servi_marge"), key=lambda e: e["moyenne"] - e["demi_intervalle_95"])
    A(f"- **{p}** : {robustesse(p, 'taux_servi_marge')} ; écart de valeur totale à l'intensité centrale de " + ", ".join(f"{f(v['moyenne'])} (eta {feta(eta)})" for eta, v in e_eta.items())
      + f", contre {f(ec(p, 'taux_servi_marge', 0, 0)['existant']['moyenne'])} en portefeuille fermé ; cas le moins favorable de la grille : {pm_(pire)}.")
etats = {eta: [col.etat_majorant(ec(p, "taux_servi_marge", c0, eta)["affaires_nouvelles"]) for p in N for c0 in INT.values()] for eta in ELA.values()}
A("\n**Majorant**, par élasticité (neuf cas chacune : trois profils, trois intensités) : " + " ; ".join(
    f"eta {feta(eta)} : {v.count('oui')} oui, {v.count('non')} non, {v.count('indéterminé')} indéterminés" for eta, v in etats.items()) + ". ")
ratios = [abs(ec(p, "taux_servi_marge", c0, eta)["affaires_nouvelles"]["moyenne"]) / abs(ec(p, "taux_servi_marge", 0, 0)["existant"]["moyenne"]) for p in N for c0, eta in GRILLE]
mono = {(p, c0): [ec(p, "taux_servi_marge", c0, eta)["totale"]["moyenne"] for eta in ELA.values()] for p in N for c0 in INT.values()}
non_mono = [x for x, v in mono.items() if not (all(a >= b for a, b in zip(v, v[1:])) or all(a <= b for a, b in zip(v, v[1:])))]
A("Avec une élasticité nulle, la politique de marge collecte presque autant que la gestion passive et gagne sa marge sur les contrats nouveaux : l'avantage fermé n'est pas un majorant. "
  f"Aux élasticités plus fortes, l'écart de valeur des affaires nouvelles est le plus souvent négatif ou indéterminé. Il atteint au plus {pct(max(ratios), 0)} de l'avantage sur l'existant (médiane {pct(sorted(ratios)[len(ratios) // 2], 0)}). "
  + (f"L'avantage n'évolue pas de façon monotone avec l'élasticité dans {len(non_mono)} des {len(mono)} couples profil et intensité : les deux politiques servent sous la référence et perdent toutes deux de la collecte quand eta augmente." if non_mono
     else "L'avantage évolue de façon monotone avec l'élasticité pour chaque profil et chaque intensité.") + "\n")

# ------------------------------------------------------------------------------------------------
A("## 4. Hypothèses du modèle de collecte qui peuvent conduire la conclusion\n")
A("Trois choix peuvent produire mécaniquement la conclusion : e0 = 0 (la gestion passive, qui sert 0,5 point sous la référence, collecte déjà moins que c0), l'horizon de collecte de 10 ans, et g_min = 0. "
  "Les deux premiers sont testés ci-dessous (gestion passive et politiques de taux servi, intensités centrale et forte, élasticités modérée et soutenue) ; l'existant en extinction ne dépend pas de ces hypothèses. "
  "Avec e0 = −0,5 point, la collecte « normale » c0 x PM est atteinte en servant 0,5 point sous la référence, comme la gestion passive ; les horizons de 30 et 60 ans prolongent la collecte au-delà de 10 ans.\n")
for c in ("taux_servi_marge", "taux_servi_competitif"):
    A(f"**{COURT[c]}**, écart de valeur totale à la gestion passive (écart de valeur des affaires nouvelles entre parenthèses)\n")
    grille_s = [(c0, eta) for c0 in (INT["centrale"], INT["forte"]) for eta in (ELA["moderee"], ELA["soutenue"])]
    A("| Profil | Hypothèse | " + " | ".join(libelle(c0, eta) for c0, eta in grille_s) + " |\n| --- | --- | " + " | ".join("---:" for _ in grille_s) + " |")
    for p in N:
        A(f"| {p} | centrale | " + " | ".join(f"{pm_(ec(p, c, c0, eta)['totale'])} ({f(ec(p, c, c0, eta)['affaires_nouvelles']['moyenne'])})" for c0, eta in grille_s) + " |")
        for s, v in SENS.items():
            A(f"| {p} | {COURT_SENS.get(s, s)} | " + " | ".join(f"{pm_(R['sensibilites_collecte'][k(s, p, c, c0, eta)]['ecart_totale'])} ({f(R['sensibilites_collecte'][k(s, p, c, c0, eta)]['ecart_affaires_nouvelles']['moyenne'])})" for c0, eta in grille_s) + " |")
    A("")
for c in ("taux_servi_marge", "taux_servi_competitif"):
    lig = []
    for p in N:
        cas = [R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"] for s in SENS for c0 in (INT["centrale"], INT["forte"]) for eta in (ELA["moderee"], ELA["soutenue"])]
        lig.append(f"{p} : {col.robustesse(cas, seuil(p))} (de {f(min(x['moyenne'] for x in cas))} à {f(max(x['moyenne'] for x in cas))})")
    A(f"- **{COURT[c]}** sous ces hypothèses : " + " ; ".join(lig) + ".")
bruit = [(s, p, c, c0, eta) for s in SENS for p in N for c in ("taux_servi_marge", "taux_servi_competitif") for c0, eta in [(x, y) for x in (INT["centrale"], INT["forte"]) for y in (ELA["moderee"], ELA["soutenue"])]
         if R["sensibilites_collecte"][k(s, p, c, c0, eta)]["ecart_totale"]["demi_intervalle_95"] > 5 * seuil(p)]
if bruit:
    pires = max(R["sensibilites_collecte"][k(*b)]["ecart_totale"]["demi_intervalle_95"] for b in bruit)
    A(f"\n**Précision.** {len(bruit)} cellules ont un demi-intervalle supérieur à cinq fois le seuil d'importance (jusqu'à {f(pires)}), dont {sum(b[3] == INT['forte'] for b in bruit)} à l'intensité forte, toutes avec une collecte de "
      + " ou ".join(sorted({COURT_SENS[b[0]].replace('collecte ', '') for b in bruit})) + f". Sur plusieurs décennies de collecte, la valeur est dominée par quelques scénarios et l'erreur Monte-Carlo empêche toute conclusion ; à l'intensité forte, la collecte nette atteint en outre environ {pct(nette_forte, 1)} de la PM par an quand g est proche de 1 (section 1), ce qui est peu plausible au regard des {pct(PP['collecte_nette'], 1)} observés en 2025.")
A("\ng_min = 0 n'est pas testé : une collecte négative reviendrait à des rachats supplémentaires, que la loi de rachat dynamique traite déjà. La conclusion dépend donc de e0 et de l'horizon de collecte dans la mesure indiquée ci-dessus, et de g_min par construction.\n")

# ------------------------------------------------------------------------------------------------
A("## 5. Les huit stratégies avec collecte\n")
A("Écart de valeur totale à la gestion passive ± intervalle apparié, intensité centrale, puis robustesse sur toute la grille (trois intensités, cinq élasticités, loi de rachat ONC maximale à l'intensité centrale).\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Stratégie | Portefeuille fermé | " + " | ".join(f"eta {feta(eta)}" for eta in ELA.values()) + " | ONC max., eta modérée | Robustesse de l'écart de valeur totale |\n| --- | ---: | " + " | ".join("---:" for _ in ELA) + " | ---: | --- |")
    for c in AUTRES:
        A(f"| {COURT[c]} | {pm_(ec(p, c, 0, 0)['existant'])} | " + " | ".join(pm_(ec(p, c, C0C, eta)["totale"]) for eta in ELA.values()) + f" | {pm_(onc(p, c, ETAM)['ecart_totale'])} | {robustesse(p, c)} |")
    tetes = {(c0, eta): max(CODES, key=lambda c: rn(p, c, c0, eta)["valeur_totale"]["moyenne"]) for c0, eta in GRILLE}
    tetes_onc = {eta: max(CODES, key=lambda c: onc(p, c, eta)["valeur_totale"]["moyenne"]) for eta in ELA.values()}
    tete_fermee = max(CODES, key=lambda c: rn(p, c)["valeur_existant"]["moyenne"])
    toutes = list(tetes.values()) + list(tetes_onc.values())
    distinctes = sorted(set(toutes), key=CODES.index)
    A("\nPlus forte valeur totale selon la configuration : " + ", ".join(f"{COURT[c]} ({toutes.count(c)} configurations sur {len(toutes)})" for c in distinctes)
      + f" ; en portefeuille fermé : {COURT[tete_fermee]}. " + ("**Le premier rang change avec les hypothèses.**" if len(distinctes) > 1 else "Le premier rang ne change pas sur la grille.") + "\n")

# ------------------------------------------------------------------------------------------------
A("## 6. Effet sur l'existant et répartition des garanties\n")
A("Variation du BE de l'existant, comptée pour l'actionnaire : - (BE de l'existant avec collecte - BE en extinction). Négative : la collecte enrichit les assurés existants (primes placées à des taux supérieurs au rendement comptable, qui relèvent le taux servi commun) ; positive : elle les dilue. Gestion passive, intensité centrale :\n")
A("| Profil | " + " | ".join(f"eta {feta(eta)}" for eta in ELA.values()) + " |\n| --- | " + " | ".join("---:" for _ in ELA) + " |")
for p in N:
    A(f"| {p} | " + " | ".join(pm_(rn(p, "passive", C0C, eta)["variation_be_existant"]) for eta in ELA.values()) + " |")
dg = R["diagnostic_garanties"]
A("\n**Transferts entre générations d'assurés.** Les contrats nouveaux reçoivent le taux servi commun, donc une part de la PPB d'ouverture et du rendement des obligations anciennes. Quand le taux commun passe sous le TMG de l'existant, l'existant reçoit son TMG et les contrats nouveaux le reste : ils financent alors une partie de la garantie de l'existant. "
  "Part des années-scénarios 2 à 10 où les contrats nouveaux sont crédités sous l'existant (intensité centrale, élasticité modérée) : " + " ; ".join(
      f"{p} {pct(dg[k(p, 'passive')]['part_annees_nouveaux_sous_existant_2_10'], 0)} en gestion passive, {pct(dg[k(p, 'taux_servi_marge')]['part_annees_nouveaux_sous_existant_2_10'], 0)} en politique de marge"
      + (f" (écart moyen de {f(1e4 * dg[k(p, 'passive')]['ecart_moyen_si_sous_existant'], 0)} pb ces années-là)" if dg[k(p, 'passive')]['part_annees_nouveaux_sous_existant_2_10'] > 0 else "") for p in N)
  + ". Ces transferts apparaissent dans les flux des contrats nouveaux et, en sens inverse, dans la variation du BE de l'existant : ni l'un ni l'autre terme ne les isole, seule la valeur des affaires nouvelles (leur somme) est interprétable.\n")

# ------------------------------------------------------------------------------------------------
A("## 7. Probabilité réelle (intensité centrale)\n")
A(f"Indicateurs non actualisés, conditionnels aux hypothèses (taux sans prime de terme, prime actions fictive, défauts aux probabilités réelles), base 100 %, c0 = {pct(C0C, 0)}. Sorties nettes : prestations et frais moins primes, rapportés à la PM de début d'année ; quantile 99 % du maximum sur 10 ans. "
  "Probabilité d'apport : sur tout l'horizon de projection (60 ans). Écart du taux servi : moyenne du fonds (tous contrats) et contrats nouveaux, ceux qui déterminent la collecte.\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Stratégie | eta | Collecte 1-10 | PM année 10 (médiane) | Rendement des fonds propres 1-10 | Dividendes 1-10 | Fonds propres année 10 (médiane) | Probabilité d'apport sur 60 ans | Écart du taux servi à la référence : fonds / contrats nouveaux | Moins-values réalisées q99 | Sorties nettes max. q99 |\n| --- | --- | " + " | ".join("---:" for _ in range(9)) + " |")
    for c in ("passive",) + POLITIQUES:
        for lab, (c0, eta) in [("fermé", (0, 0))] + [(feta(eta), (C0C, eta)) for eta in ELA.values()]:
            r = re_(p, c, c0, eta)
            nouveaux = f"{f(1e4 * r['ecart_taux_servi_nouveaux_reference_1_10'], 0)} pb" if "ecart_taux_servi_nouveaux_reference_1_10" in r else "-"
            A(f"| {COURT[c]} | {lab} | {f(r['collecte_1_10_moyenne'])} | {f(r['pm_annee_10_mediane'], 0)} | {pct(r['rendement_fonds_propres_1_10_agrege'])} | {f(r['dividendes_1_10_moyen'])} | {f(r['fonds_propres_annee_10_mediane'])} | "
              f"{pct(r['probabilite_apport_horizon'], 1)} | {f(1e4 * r['ecart_taux_servi_reference_1_10'], 0)} pb / {nouveaux} | {f(r['moins_values_realisees_1_10_q99'])} | {pct(r['sorties_nettes_max_1_10_q99'])} |")
    A("")
A("Autres stratégies : `resultats/v5_collecte.json`, rubrique `reel`. Les sorties nettes maximales identiques d'une ligne à l'autre pour A correspondent au plafond de la loi de rachat dynamique, atteint dans les scénarios les plus défavorables.\n")
liq = []
for p in N:
    r0, r1 = re_(p, "passive"), re_(p, "passive", C0C, ETAM)
    liq.append(f"{p} : moins-values réalisées q99 {f(r0['moins_values_realisees_1_10_q99'])} en extinction, {f(r1['moins_values_realisees_1_10_q99'])} avec collecte ; sorties nettes max. q99 {pct(r0['sorties_nettes_max_1_10_q99'])} et {pct(r1['sorties_nettes_max_1_10_q99'])}")
A("**Liquidité** (gestion passive, élasticité modérée) : " + " ; ".join(liq) + ". Les primes financent une partie des sorties et réduisent les ventes d'obligations en moins-value.\n")
gap = {p: re_(p, "taux_servi_marge", C0C, ETAM)["ecart_taux_servi_reference_1_10"] - re_(p, "passive", C0C, ETAM)["ecart_taux_servi_reference_1_10"] for p in N}
A("**Écart de taux servi effectivement réalisé** entre la politique de marge et la gestion passive (moyenne du fonds, années 1 à 10, élasticité modérée) : " + ", ".join(f"{f(1e4 * v, 0)} pb ({p})" for p, v in gap.items())
  + ", bien moins que le point d'écart des cibles : la participation minimale (compte de participation simplifié) et les reprises de PPB limitent la baisse effective du taux servi, donc la perte de collecte.\n")

# ------------------------------------------------------------------------------------------------
A("## 8. Capital\n")
A("- **Besoin à l'ouverture** : inchangé par la collecte, par construction (vue prudentielle simplifiée en extinction, section 1). Apports à 100 % : " + " ; ".join(
    f"{p} : " + ", ".join(f"{minuscule(COURT[c])} {f(R['apports'][k(p, c)])}" for c in ("passive",) + POLITIQUES) for p in N) + ".")
cap = []
for p in N:
    r0, r1 = re_(p, "passive"), re_(p, "passive", C0C, ETAM)
    cap.append(f"{p} : fonds propres médians à 10 ans {f(r0['fonds_propres_annee_10_mediane'])} en extinction, {f(r1['fonds_propres_annee_10_mediane'])} avec collecte ; dividendes 1-10 {f(r0['dividendes_1_10_moyen'])} et {f(r1['dividendes_1_10_moyen'])}")
A("- **Capital retenu par la croissance** (gestion passive, élasticité modérée, probabilité réelle) : la politique de distribution maintient les fonds propres à leur cible en % de la PM ; la croissance de la PM retient donc du capital et réduit les dividendes. " + " ; ".join(cap) + ".")
CC = REC["capital_croissance"]
A("- **Capital de la croissance, ordre de grandeur** : en supposant le SCR simplifié proportionnel à la PM, au ratio d'ouverture de chaque stratégie (SCR à 100 % de couverture / PM d'ouverture), "
  "l'écart de PM médiane à 10 ans entre la collecte centrale et l'extinction (probabilité réelle) demanderait le SCR supplémentaire ci-dessous. Ce n'est pas une projection du SCR : le profil de risque change avec la duration, la PPB, les plus-values latentes et l'allocation. "
  "SCR à 100 % : contrôle direct quand il existe, sinon interpolation linéaire en fonction de l'apport, comme pour le besoin d'apport de la consolidation.\n")
A("| Profil | Stratégie | Apport à l'ouverture (écart à la gestion passive) | SCR / PM d'ouverture | SCR supplémentaire à 10 ans : eta " + " / ".join(feta(e) for e in ELA.values()) + " | Écart à la gestion passive, eta modérée |\n| --- | --- | ---: | ---: | ---: | ---: |")
inverse = []
for p in N:
    base = CC[k(p, "passive")]["collecte_centrale"]["moderee"]["scr_supplementaire_proportionnel"]
    for c in CODES:
        x = CC[k(p, c)]
        sup = {n: v["scr_supplementaire_proportionnel"] for n, v in x["collecte_centrale"].items()}
        d_ouv = R["apports"][k(p, c)] - R["apports"][k(p, "passive")]
        d_cro = sup["moderee"] - base
        A(f"| {p} | {COURT[c]} | {f(R['apports'][k(p, c)])} ({'-' if c == 'passive' else f(d_ouv)}) | {pct(x['scr_sur_pm0'], 1)} | {' / '.join(f(v) for v in sup.values())} | {'-' if c == 'passive' else f(d_cro)} |")
        if c != "passive" and abs(d_ouv) >= seuil(p) and abs(d_cro) >= seuil(p) and (d_ouv > 0) != (d_cro > 0):
            inverse.append(f"{COURT[c]} ({p} : {f(d_ouv)} à l'ouverture, {f(d_cro)} pour la croissance)")
A("")
A("  La croissance demande un capital du même ordre que l'apport d'ouverture de B et C (eta modérée), et il dépend d'abord de l'élasticité. "
  + ("Pour " + ", ".join(inverse) + ", l'écart de capital à l'ouverture et l'écart de capital de la croissance vont en sens contraire : la comparaison des besoins à l'ouverture ne suffit pas à classer les stratégies en capital. " if inverse else "")
  + "La politique de distribution retient des fonds propres comptables au ratio d'ouverture (point précédent) : ce SCR supplémentaire n'appelle donc pas un apport du même montant, mais fonds propres comptables et fonds propres prudentiels ne coïncident pas (plus ou moins-values latentes, marge de risque, absorption par les provisions techniques, impôts différés).")
A("- **Seuil de coût du capital des affaires nouvelles** (analyse de seuil, aucun coût retenu ; gestion passive, collecte centrale, eta modérée, mêmes scénarios risque neutre que la valeur publiée). "
  "Capital proxy, scénario par scénario : K(t) = SCR à 100 % / PM d'ouverture x (PM avec collecte - PM en extinction). Une charge frictionnelle kappa x K(t - 1), payée en fin d'année t et actualisée au déflateur, réduit la valeur des affaires nouvelles de kappa x S, "
  "avec S = somme sur t de E[D(t) K(t - 1)] ; le seuil kappa* = valeur / S est la charge annuelle qui l'annulerait. kappa est une charge supplémentaire hypothétique, nette des coûts déjà valorisés (impôt et participation sur les revenus du capital comptable retenu) : "
  "ce n'est ni le rendement exigé en probabilité réelle, ni le taux de la marge de risque Solvabilité II, qui ont d'autres usages (`docs/V5_METHODOLOGIE.md`, section 3).\n")
A("| Profil | Valeur des affaires nouvelles ± IC 95 % | SCR / PM d'ouverture | S, VA du capital proxy | kappa* | kappa* aux bornes de l'intervalle |\n| --- | ---: | ---: | ---: | ---: | ---: |")
for p in N:
    x = SC[p]
    A(f"| {p} | {f(x['van_affaires_nouvelles'])} ± {f(x['van_demi_intervalle_95'])} | {pct(x['scr_sur_pm0'], 1)} | {f(x['va_capital_proxy'], 0)} | {pct(x['kappa_seuil'], 1)} | {pct(x['kappa_seuil_bornes'][0], 1)} à {pct(x['kappa_seuil_bornes'][1], 1)} |")
A("")
A("  Lecture : une charge frictionnelle supérieure à environ " + " à ".join(pct(v, 1) for v in (min(SC[p]['kappa_seuil'] for p in N), max(SC[p]['kappa_seuil'] for p in N)))
  + " par an du capital proxy suffirait à annuler la valeur centrale des affaires nouvelles. Le seuil hérite des limites du proxy (SCR proportionnel à la PM, au ratio d'ouverture) et ne dit pas quelle charge est la bonne.")
A("- **Aucune stratégie ne garantit la conformité prudentielle future.** L'apport à l'ouverture porte l'indicateur simplifié à 100 % pour l'existant en extinction, à la date d'évaluation ; le SCR n'est pas projeté, la couverture des années suivantes n'est pas mesurée, et un apport futur éventuel n'est compté qu'en probabilité réelle, sans lien avec un ratio cible.\n")

# ------------------------------------------------------------------------------------------------
A("## 9. Limites\n")
for x in [
    "**Modèle volontairement simple** : collecte proportionnelle à la PM, réaction linéaire encadrée, une seule génération agrégée de contrats nouveaux, même taux servi au-dessus des garanties pour tous les contrats, même loi de rachat ; la perte de compétitivité ne fait pas racheter l'existant au-delà de la loi de rachat dynamique.",
    "**Élasticité fictive** : aucune donnée vérifiée ne mesure la réaction de la collecte au taux servi relatif ; la grille de 0 à 1,5 est une plage testée en cinq points, pas une estimation.",
    "**Intensités** : dérivées d'agrégats de place d'une seule année (France Assureurs, ACPR), aux périmètres non strictement identiques ; c0 = 6 % redonne la collecte nette de 2025, pas ses flux bruts ni la croissance de la PM ; 10 % est une borne haute ; elles ne calibrent aucun profil.",
    "**Flux absents du modèle** : prélèvements sociaux, arbitrages entre supports et transferts ; la PM projetée est un peu surestimée.",
    "**Valeur des affaires nouvelles** : hors Solvabilité II ; avant coût explicite de mobilisation du capital additionnel (seuil seulement, section 8), sans marge pour risques non couvrables, frais d'acquisition fictifs ; horizon de collecte de 10 ans au centre (30 et 60 ans en sensibilité).",
    "**Contrat sans marge explicite** : son résidu dépend des conventions de partage et de liquidation (réserve de capitalisation, plus-values latentes finales, rétention de capital, plancher du taux servi) ; le traitement de la réserve suit le principe de l'article R.351-2-1 du Code des assurances sans en reproduire toutes les modalités.",
    "**Vue prudentielle** : calculée en extinction ; les effets de la collecte sur les hypothèses de projection de l'existant n'y sont pas repris.",
    "**Décomposition** : seule la valeur des affaires nouvelles s'interprète ; ses termes déplacent les transferts entre générations d'assurés sans les isoler.",
    "**Capital** : besoin à l'ouverture en extinction ; SCR futur non projeté ; capital de la croissance estimé seulement en ordre de grandeur (SCR proportionnel à la PM) ; aucune stratégie ne garantit la conformité prudentielle future.",
]:
    A(f"- {x}")
A("")
Path(ARGS.sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit :", ARGS.sortie)
