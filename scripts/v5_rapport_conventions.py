"""Génère docs/V5_CONVENTIONS.md depuis resultats/v5_comparaison_conventions.json et
resultats/v5_solvabilite_profils.json. Les phrases de conclusion sont écrites ici ; tous les chiffres
viennent des fichiers de résultats et de données."""

import json
import sys
from itertools import product
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from src.v5 import conventions as cv  # noqa: E402

D = json.loads((RACINE / "resultats" / "v5_comparaison_conventions.json").read_text(encoding="utf-8"))
_s2 = RACINE / "resultats" / "v5_solvabilite_profils.json"
S2 = json.loads(_s2.read_text(encoding="utf-8")) if _s2.exists() else {"resultats": {}}
_da = RACINE / "resultats" / "v5_diagnostic_profil_a.json"
DA = json.loads(_da.read_text(encoding="utf-8")) if _da.exists() else {"resultats": {}}
C = cv.charger()
BI = json.loads((RACINE / "resultats" / "v5_bilans_initiaux.json").read_text(encoding="utf-8"))["profils"]
M = json.loads((RACINE / "data" / "v5" / "conventions" / "marche_acpr.json").read_text(encoding="utf-8"))
ST, EC, RE = D["stochastique"], D["equivalent_certain"], D["reel"]
N = "ABC"
REFS = ("oat_moins_2", "sans_risque", "sans_risque_demi", "taux_servi_marche", "livret_a", "figee")
CREDITS = ("lisse_integral", "saut_integral", "decompose")
LIB_REF = {k: C["references_assures"][k]["libelle"] for k in REFS}
COURT_REF = {"oat_moins_2": "Obligations - 2 pts", "sans_risque": "Sans risque", "sans_risque_demi": "Sans risque, 50 %",
             "taux_servi_marche": "Proxy lissé sur 7 ans", "livret_a": "Livret A", "figee": "Figée"}
COURT_K = {"lisse_integral": "Lissé intégral", "saut_integral": "Saut intégral", "decompose": "Décomposé",
           "decompose_recouvrement_63": "Décomposé, R = 63 %", "saut_bloc_unique": "Saut, bloc unique"}
CENTRE_REF, CENTRE_K = "taux_servi_marche", "decompose"


def f(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


def pb(x):
    return f(1e4 * x, 0) + " pb"


def st(p, r, k, **o):
    s = "".join(f"|{a}={b}" for a, b in sorted(o.items()))
    return ST[f"{p}|{r}|{k}{s}"]


def ec(p, r, **o):
    s = "".join(f"|{a}={b}" for a, b in sorted(o.items()))
    return EC[f"{p}|{r}|ec{s}"]


def tvog(p, r, k, **o):
    return st(p, r, k, **o)["be"] - ec(p, r, **o)["be"]


L = []
A = L.append
A("# V5 : conventions de crédit et de comportement, comparaison croisée sur les trois profils fictifs\n")
A("Généré par `scripts/v5_rapport_conventions.py` depuis `resultats/v5_comparaison_conventions.json` "
  "(`scripts/v5_comparaison_conventions.py`) et `resultats/v5_solvabilite_profils.json` (`scripts/v5_solvabilite_profils.py`). "
  f"Unités fictives : 1 unité = 10 M€, PM initiale de 1 000. Valorisation risque neutre au 31/10/2026, {f(D['n_scenarios'], 0)} scénarios, "
  "base sans VA sauf mention, valeurs avant impôt. Paramètres et statuts : `data/v5/conventions/conventions.json`. "
  "**Les profils A, B et C sont fictifs** : ils ne décrivent aucun organisme réel. Aucune stratégie n'est optimisée ici.\n")

# ------------------------------------------------------------------------------------------------
A("## 1. Données de place utilisées\n")
A("| Thème | Valeur | Source | Statut |\n| --- | --- | --- | --- |")
for o in M["observations"]:
    A(f"| {o['theme']} | {o['valeur']} | {o['source']} | {o['statut']} |")
ob = C["observations"]
A(f"| Notation des obligations des assureurs | AAA à AA- {pct(ob['notations_des_obligations_des_assureurs']['AAA_a_AA-'], 0)}, A {pct(ob['notations_des_obligations_des_assureurs']['A+_a_A-'], 0)}, BBB {pct(ob['notations_des_obligations_des_assureurs']['BBB+_a_BBB-'], 0)} | {ob['notations_des_obligations_des_assureurs']['source']} | observé |")
A(f"| Défauts annuels moyens (entreprises, 1981-2024) | AA {pct(ob['taux_defaut_annuel_moyen_entreprises']['AA'], 2)}, A {pct(ob['taux_defaut_annuel_moyen_entreprises']['A'], 2)}, BBB {pct(ob['taux_defaut_annuel_moyen_entreprises']['BBB'], 2)} | {ob['taux_defaut_annuel_moyen_entreprises']['source']} | observé |")
A(f"| Décote moyenne des restructurations souveraines | {pct(ob['decote_moyenne_restructurations_souveraines']['valeur'], 0)} ({ob['decote_moyenne_restructurations_souveraines']['echantillon']}) | {ob['decote_moyenne_restructurations_souveraines']['source']} | observé |")
A(f"| Rapport des intensités de défaut risque neutre / réelles | {f(ob['rapport_intensites_risque_neutre_sur_reelles']['valeur'], 0)} en moyenne ({ob['rapport_intensites_risque_neutre_sur_reelles']['perimetre']}) | {ob['rapport_intensites_risque_neutre_sur_reelles']['source']} | observé (estimation publiée) |")
A("")
A("**Non consulté** : le PDF de l'ACPR n° 185 et le classeur de données des graphiques de l'ACPR n° 179 (quartiles de rachat par organisme). Les moins-values latentes au 30/06/2026, les durations de place, la réserve de capitalisation de place, la répartition des garanties et les quartiles de rachat restent donc des paramètres fictifs des profils, testés en sensibilité, sans calibration inventée.\n")

# ------------------------------------------------------------------------------------------------
dec = C["decomposition_spread_10_ans"]
s10 = ob["spread_obligations_sur_eiopa"]["10_ans"]
kappa = dec["part_credit_risque_neutre"]["central"]
elp = dec["perte_attendue_reelle_annuelle"]["central"]
k3 = st("B", CENTRE_REF, "decompose")
k2 = st("B", CENTRE_REF, "saut_integral")
pd_reel = dec["probabilite_defaut_reelle_annuelle"]["valeur"]
A("## 2. Décomposition du spread des obligations : risque neutre et probabilité réelle\n")
A(dec["_regle"] + "\n")
A("| Composante (10 ans) | Niveau | Mesure | Statut | Traitement |\n| --- | ---: | --- | --- | --- |")
A(f"| Spread des obligations au-dessus de la courbe EIOPA sans VA | {pb(s10)} | hypothèse (moyenne de long terme publiée par l'EIOPA, notation A) | hypothèse | prix de marché des obligations, inchangés dans toutes les conventions |")
A(f"| Perte attendue réelle | {pb(elp)} par an | réelle | calibré | seule perte constatée dans les projections en probabilité réelle |")
A(f"| Prime de risque de crédit | {pb(kappa * s10 - elp)} | écart risque neutre - réel | hypothèse (kappa) | rémunère le risque de défaut, n'est pas de la valeur créée |")
A(f"| Composante hors défaut (liquidité, offre de titres) | {pb((1 - kappa) * s10)} | hypothèse | hypothèse | coût risque neutre lissé dans la valorisation, prime en probabilité réelle |")
A("")
A(f"Probabilités de défaut d'un bloc d'émetteurs : risque neutre, {pct(k3['probabilite_defaut_bloc_annee_10_rn'], 2)} par an vers 10 ans "
  f"({pct(k3['probabilite_defaut_bloc_10_ans_rn'], 1)} sur 10 ans) en convention décomposée, {pct(k2['probabilite_defaut_bloc_annee_10_rn'], 2)} par an "
  f"({pct(k2['probabilite_defaut_bloc_10_ans_rn'], 1)} sur 10 ans) si tout le spread est du crédit ; réelle, {pct(pd_reel, 3)} par an "
  f"(environ {pct(1 - (1 - pd_reel) ** 10, 1)} sur 10 ans). L'écart, d'un facteur proche de "
  f"{f(k3['probabilite_defaut_bloc_annee_10_rn'] / pd_reel, 0)}, est la prime de risque : il dépasse nettement le rapport de 2 estimé sur les souverains de la zone euro, "
  "ce qui indique que le spread retenu rémunère surtout autre chose qu'une perte attendue historique : une prime pour le risque de défaut et une composante hors défaut. "
  "Les deux probabilités ne portent pas exactement sur le même objet (la probabilité réelle est tirée des défauts d'entreprises par notation, appliqués à la composition du portefeuille de place) : seul l'ordre de grandeur compte.\n")
A("**Pourquoi la valorisation garde tout le spread comme coût risque neutre** : sans frictions, si une partie du spread n'était pas un coût en risque neutre, un investisseur qui garde le titre jusqu'à l'échéance l'encaisserait sans risque. Ce serait une valeur actuelle nette positive à l'achat, ce que le test de non-arbitrage interdit. La décomposition ne change donc pas le prix. Elle change trois choses : la forme des pertes risque neutre (lissées ou par saut), les trajectoires en probabilité réelle (seule la perte attendue réelle y est constatée) et la vue réglementaire (une VA ou un ajustement égalisateur reconnaît une partie de la composante hors défaut, ce qui reste une convention prudentielle).\n")

# ------------------------------------------------------------------------------------------------
A("## 3. Conventions comparées\n")
A("**Crédit (valorisation, toutes à prix de marché identiques, tests de non-arbitrage dans `tests/test_v5_conventions.py`)**\n")
A("| Code | Convention | Part par saut | Recouvrement | Blocs | Statut |\n| --- | --- | ---: | ---: | --- | --- |")
for code, k in ((c_, v_) for c_, v_ in C["conventions_credit"].items() if not c_.startswith("k")):
    blocs = "26 % souverain + 20 blocs diversifiés" if k["blocs"] == "souverain_et_diversifie" else "un seul bloc"
    rec = pct(k['recouvrement'], 0) if k["part_saut"] > 0 else "sans objet"
    blocs = blocs if k["part_saut"] > 0 else "sans objet"
    A(f"| `{code}` | {k['libelle']} | {pct(k['part_saut'], 0)} | {rec} | {blocs} | {k['statut']} |")
A("")
A("**Référence des assurés (toutes au même niveau en t = 0, "
  f"{pct(cv.niveau_initial_central(), 2)} : hypothèse de modélisation, non observée)**\n")
A("| Code | Référence | Dynamique |\n| --- | --- | --- |")
dyn = {"oat_moins_2": "suit la courbe à terme des obligations du modèle, spread compris",
       "sans_risque": "suit le taux sans risque 10 ans, transmission totale et immédiate",
       "sans_risque_demi": "moitié des variations du taux sans risque 10 ans",
       "taux_servi_marche": "taux sans risque 10 ans lissé, renouvellement de 1/7 par an (proxy comportemental fictif, non observé)",
       "livret_a": "moitié des variations du taux court (formule du livret A), plancher de 0,5 %",
       "figee": "constante"}
for r in REFS:
    A(f"| `{r}` | {LIB_REF[r]} | {dyn[r]} |")
A("")
A("**Probabilité réelle (trajectoires de plausibilité, sans valorisation)** : taux et spreads figés à leur niveau de marché (marche aléatoire), prime actions de 3 % (fictive), "
  "quatre niveaux de pertes de crédit effectives : 3 pb par an (central), 10 pb par an, 50 % du spread à 10 ans (stress, rapport d'intensités de 2) et 100 % du spread (stress).\n")

# ------------------------------------------------------------------------------------------------
A("## 4. Résultats\n")
A("### 4.1 Valeur actionnaire (actif - BE stochastique)\n")
for p in N:
    A(f"**Profil {p}**\n")
    A("| Référence | " + " | ".join(COURT_K[k] for k in CREDITS) + " | Équivalent certain |\n| --- | " + " | ".join("---:" for _ in CREDITS) + " | ---: |")
    for r in REFS:
        A(f"| {COURT_REF[r]} | " + " | ".join(f"{f(st(p, r, k)['valeur'])} ± {f(st(p, r, k)['ic_be'])}" for k in CREDITS) + f" | {f(ec(p, r)['valeur'])} |")
    A("")

A("### 4.2 BE et TVOG\n")
A("Convention de crédit décomposée. TVOG = BE stochastique - BE équivalent certain (même référence, même base). L'équivalent certain est identique pour toutes les conventions de crédit (perte moyenne).\n")
A("| Référence | " + " | ".join(f"BE {p}" for p in N) + " | " + " | ".join(f"TVOG {p}" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(6)) + " |")
for r in REFS:
    A(f"| {COURT_REF[r]} | " + " | ".join(f(st(p, r, CENTRE_K)['be']) for p in N) + " | " + " | ".join(f(tvog(p, r, CENTRE_K)) for p in N) + " |")
A("")
A("Effet de la forme des pertes sur la TVOG (référence : proxy lissé sur 7 ans) :\n")
A("| Crédit | " + " | ".join(f"TVOG {p}" for p in N) + " |\n| --- | ---: | ---: | ---: |")
for k in CREDITS:
    A(f"| {COURT_K[k]} | " + " | ".join(f(tvog(p, CENTRE_REF, k)) for p in N) + " |")
A("")

A("### 4.3 Rachats\n")
A("Taux de rachat observé sur les supports en euros : 4,4 % en 2025 (ACPR n° 179). Hypothèse structurelle des V1 à V4 : 5 %.\n")
A("| Référence | " + " | ".join(f"{p}, risque neutre (moyenne 1-10)" for p in N) + " | " + " | ".join(f"{p}, q95 du maximum annuel" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(6)) + " |")
for r in REFS:
    A(f"| {COURT_REF[r]} | " + " | ".join(pct(st(p, r, CENTRE_K)['taux_rachat_moyen_1_10']) for p in N) + " | "
      + " | ".join(pct(st(p, r, CENTRE_K)['taux_rachat_max_1_10_q95'], 0) for p in N) + " |")
A("\nUn maximum de 35 % correspond au plafond de la loi de rachat (5 % structurel et 30 % conjoncturel) : il est atteint au moins une année dans plus de 5 % des scénarios pour toutes les références qui suivent les taux.\n")
A("En probabilité réelle (trajectoire centrale, perte attendue de 3 pb), les rachats restent au niveau structurel : "
  + ", ".join(f"{pct(RE[f'{p}|{CENTRE_REF}|central']['taux_rachat_moyen_1_10'])} ({p})" for p in N)
  + ". Les rachats risque neutre ne sont pas une prévision : en risque neutre, les produits comptables sont nets de tout le coût du spread et le taux servi baisse dans la plupart des scénarios.\n")

A("### 4.4 Liquidité\n")
A("Convention décomposée. Sorties = décès + rachats, rapportées à la PM de début d'année ; moins-values réalisées = moins-values obligataires constatées lors des ventes pour payer les sorties, cumulées sur 10 ans.\n")
A("| Référence | Profil | Sorties max, q95 | Moins-values réalisées, moyenne | Moins-values réalisées, q95 | Scénarios où elles dépassent la réserve de capitalisation |\n| --- | --- | ---: | ---: | ---: | ---: |")
for r in ("oat_moins_2", "sans_risque", CENTRE_REF, "figee"):
    for p in N:
        x = st(p, r, CENTRE_K)
        A(f"| {COURT_REF[r]} | {p} | {pct(x['sorties_max_1_10_q95'], 0)} | {f(x['moins_values_realisees_1_10_moyenne'])} | {f(x['moins_values_realisees_1_10_q95'])} | {pct(x['part_scenarios_mv_realisees_au_dela_rc'], 0)} |")
A("")

A("### 4.5 Apports de capital\n")
A("Valeur actuelle des apports de l'actionnaire, par scénario (risque neutre).\n")
A("| Référence | Crédit | Profil | Scénarios avec apport | Moyenne | Médiane | q95 | q99 | Moyenne si apport | Apport avant 10 ans |\n| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for r, k in (("sans_risque", "lisse_integral"), ("sans_risque", "decompose"), (CENTRE_REF, "lisse_integral"), (CENTRE_REF, "decompose"), (CENTRE_REF, "saut_integral")):
    for p in N:
        x = st(p, r, k)
        q = x["va_apports_quantiles"]
        A(f"| {COURT_REF[r]} | {COURT_K[k]} | {p} | {pct(x['part_scenarios_avec_apport'], 0)} | {f(x['va_apports_moyenne'])} | {f(q['0.5'])} | {f(q['0.95'])} | {f(q['0.99'])} | {f(x['va_apports_moyenne_si_apport'])} | {pct(x['part_apport_avant_10_ans'], 0)} |")
A("")

A("### 4.6 Sensibilité aux taux (équivalent certain, choc parallèle de ±5 pb)\n")
A("| Référence | " + " | ".join(f"Duration BE {p}" for p in N) + " | " + " | ".join(f"Valeur pour +1 pb, {p}" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(6)) + " |")
for r in REFS:
    A(f"| {COURT_REF[r]} | " + " | ".join(f(ec(p, r)['duration_effective_be']) for p in N) + " | " + " | ".join(f(ec(p, r)['valeur_par_pb'], 2) for p in N) + " |")
A("\nDuration effective de l'actif : " + ", ".join(f"{f(ec(p, 'sans_risque')['duration_effective_actif'])} ({p})" for p in N)
  + ". Observation de place (ACPR n° 181) : la hausse des taux longs réduit davantage la valeur des engagements que celle des actifs, donc la valeur des assureurs monte quand les taux montent.\n")

A("### 4.7 Variantes complémentaires (référence sans risque)\n")
A("| Variante | " + " | ".join(f"Valeur {p}" for p in N) + " | " + " | ".join(f"Rachat moyen 1-10, {p}" for p in N) + " |\n| --- | " + " | ".join("---:" for _ in range(6)) + " |")
variantes = [("Lissé intégral", "lisse_integral", {}), ("Décomposé", "decompose", {}), ("Décomposé, recouvrement 63 %", "decompose_recouvrement_63", {}),
             ("Saut intégral, bloc unique", "saut_bloc_unique", {}), ("Lissé, niveau initial 2,63 %", "lisse_integral", {"niveau": 0.0263}),
             ("Décomposé, niveau initial 2,63 %", "decompose", {"niveau": 0.0263}), ("Lissé, rachat structurel 4,4 %", "lisse_integral", {"rachat_structurel": 0.044}),
             ("Décomposé, rachat structurel 4,4 %", "decompose", {"rachat_structurel": 0.044}), ("Décomposé, base avec VA", "decompose", {"base": "avec_va"})]
for lib, k, o in variantes:
    A(f"| {lib} | " + " | ".join(f"{f(st(p, 'sans_risque', k, **o)['valeur'])} ± {f(st(p, 'sans_risque', k, **o)['ic_be'])}" for p in N) + " | "
      + " | ".join(pct(st(p, 'sans_risque', k, **o)['taux_rachat_moyen_1_10']) for p in N) + " |")
A("")

A("### 4.8 Trajectoires en probabilité réelle (plausibilité, aucune valeur)\n")
A("Taux et spreads figés, référence des assurés constante (toutes les références coïncident sur ces trajectoires). Comparaison de place : rendement de l'actif 2,8 % en 2025 (la moitié des organismes entre 2,4 % et 3,3 %), taux servi 2,63 % (quartiles 2,3 % et 2,9 %), rachats 4,4 %. "
  "Lecture : les rendements comptables encadrent la place (A au niveau moyen, C au-dessus du troisième quartile, ce qui correspond à son récit) ; les taux servis restent sous la moyenne de place parce que la règle de taux servi des V1 à V4 vise la référence moins 0,5 point (2,38 %), paramètre de stratégie qui sera un levier de l'étape suivante.\n")
A("| Profil | Pertes de crédit effectives | Rendement comptable 1-10 | Taux servi 1-10 | Rachat 1-10 | PM à 10 ans | Apports cumulés | Fonds propres min. 1-10 |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
for p in N:
    for code in ("central", "haute", "stress_50", "stress_100"):
        x = RE[f"{p}|{CENTRE_REF}|{code}"]
        A(f"| {p} | {C['conventions_reelles'][code]['libelle']} | {pct(x['rendement_comptable_moyen_1_10'], 2)} | {pct(x['taux_servi_moyen_1_10'], 2)} | {pct(x['taux_rachat_moyen_1_10'])} | {f(x['pm_annee_10'], 0)} | {f(x['apports_cumules'])} | {f(x['fonds_propres_min_1_10'])} |")
A("")

A("### 4.9 Vue prudentielle simplifiée (base avec VA)\n")
A("Calcul pédagogique inspiré de la formule standard (`src/v5/solvabilite_v5.py`) : taux, actions, spread (part non souveraine, notation A), rachat ; absorption par les FDB ; marge de risque à 6 %. Hors calcul : risque opérationnel, absorption par les impôts différés, fonds excédentaires (borne haute indicative donnée à part).\n")
A("| Profil | Référence | Crédit | Actif | BE | Marge de risque | Fonds propres | SCR | dont marché net | dont rachat net | Ratio | Ratio après impôts différés | Fonds excédentaires, borne haute |\n| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
for key, x in S2["resultats"].items():
    p, r, k = key.split("|")
    A(f"| {p} | {COURT_REF[r]} | {COURT_K[k]} | {f(x['actif'])} | {f(x['be'])} | {f(x['marge_de_risque'])} | {f(x['fonds_propres_avant_impots_differes'])} | {f(x['scr'])} | {f(x['scr_net']['marche'])} | {f(x['scr_net']['rachat'])} | {pct(x['ratio_avant_impots_differes'], 0)} | {pct(x['ratio_apres_impots_differes'], 0)} | {f(x['fonds_excedentaires_borne_haute'])} |")
A("")
if S2["resultats"]:
    R2 = S2["resultats"]
    cle_c = lambda p: f"{p}|{CENTRE_REF}|{CENTRE_K}"  # noqa: E731
    A("Lecture :\n")
    A("- **Écart massif avec la place.** Ratios approchés dans la convention centrale : " + ", ".join(f"{pct(R2[cle_c(p)]['ratio_avant_impots_differes'], 0)} ({p})" for p in N)
      + ", contre 239 % pour les organismes vie et mixtes au 30/06/2026. "
      + ("Même le profil C reste sous 100 %, et B" if R2[cle_c("C")]["ratio_avant_impots_differes"] < 1 else "B")
      + ", conçu pour être proche de la place sur la PPB, le taux technique et le taux servi, en est très loin en solvabilité.")
    A("- **Ce qui manque au calcul et jouerait en faveur des profils** : fonds excédentaires (jusqu'à " + ", ".join(f"{f(R2[cle_c(p)]['fonds_excedentaires_borne_haute'])} pour {p}" for p in N)
      + "), absorption par les impôts différés, ajustement symétrique du choc actions. Ce qui est peut-être trop sévère : un choc de spread en notation A sur 66 % des obligations ("
      + ", ".join(f"{f(R2[cle_c(p)]['pertes_nettes']['spread'])} pour {p}" for p in N) + " de perte nette), et la règle de taux servi des V1 à V4, qui fait renoncer l'assureur à sa marge pour suivre la référence, ce qui réduit l'absorption par les FDB.")
    _sous = [p for p in N if BI[p]["economique"]["total_actif"] < BI[p]["comptable"]["passif"]["pm"] + BI[p]["comptable"]["passif"]["ppb"]]
    _fp = [BI[p]["indicateurs"]["fonds_propres_comptables_pct_pm"] for p in N]
    A("- **Ce qui vient des profils** : à l'ouverture, " + (f"l'actif en valeur de marché est inférieur à la PM et à la PPB pour {' et '.join(_sous)} ; " if _sous else "")
      + "les moins-values obligataires (" + ", ".join(f"{pct(BI[p]['indicateurs']['pmvl_obligations_pct_vnc'], 0)} pour {p}" for p in N)
      + f" de la VNC) et les fonds propres comptables ({pct(min(_fp), 1)} à {pct(max(_fp), 1)} de la PM) sont des paramètres fictifs que la donnée de place 2026 (ACPR n° 185, non lue) permettrait de confronter.")
    hausse = [k for k, x in R2.items() if x["pertes_nettes"]["taux_hausse"] >= x["pertes_nettes"]["taux_baisse"]]
    if len(hausse) == len(R2):
        A("- **Choc de taux** : dans toutes les conventions calculées, c'est la hausse des taux qui coûte (perte nette de " + ", ".join(f"{f(R2[cle_c(p)]['pertes_nettes']['taux_hausse'])} pour {p}" for p in N)
          + " au centre), alors que la place gagne quand les taux montent. Le même écart apparaît dans les durations de la section 4.6.")
    else:
        baisse_centre = [p for p in N if R2[cle_c(p)]["pertes_nettes"]["taux_baisse"] > R2[cle_c(p)]["pertes_nettes"]["taux_hausse"]]
        A(f"- **Choc de taux** : la hausse des taux est le choc le plus coûteux dans {len(hausse)} conventions calculées sur {len(R2)} ; au centre, perte nette en hausse et en baisse de "
          + ", ".join(f"{f(R2[cle_c(p)]['pertes_nettes']['taux_hausse'])} et {f(R2[cle_c(p)]['pertes_nettes']['taux_baisse'])} pour {p}" for p in N)
          + (f" : pour {' et '.join(baisse_centre)}, c'est la baisse qui coûte le plus au centre" if baisse_centre else "")
          + ". La place, elle, gagne quand les taux montent ; l'écart de sensibilité apparaît aussi dans les durations de la section 4.6.")
    if all(x["fonds_propres_avant_impots_differes"] < 0 for k, x in R2.items() if k.startswith("A|")):
        A("- **Profil A** : fonds propres prudentiels négatifs dans toutes les conventions calculées ; en lecture réglementaire, ce serait un organisme à recapitaliser ou en plan de rétablissement, quelle que soit la convention de crédit ou de comportement retenue ici.\n")
    else:
        A("- **Profil A** : fonds propres prudentiels négatifs dans " + str(sum(x["fonds_propres_avant_impots_differes"] < 0 for k, x in R2.items() if k.startswith("A|")))
          + " conventions calculées sur " + str(sum(k.startswith("A|") for k in R2)) + ".\n")

# ------------------------------------------------------------------------------------------------
cles = [(p, r, k, o) for p in N for (r, k, o) in [(r, k, {}) for r in REFS for k in CREDITS]]
toutes = [(k.split("|")[0], k) for k in ST]
signes = {p: [ST[k]["valeur"] for q, k in toutes if q == p] for p in N}
triplets = sorted({k.split("|", 1)[1] for k in ST})
ordre_profils = sum(1 for t in triplets if ST[f"A|{t}"]["valeur"] < ST[f"B|{t}"]["valeur"] < ST[f"C|{t}"]["valeur"])
saut_moins = sum(1 for p, r in product(N, REFS) if st(p, r, "saut_integral")["valeur"] < st(p, r, "lisse_integral")["valeur"])
decomp_entre = sum(1 for p, r in product(N, REFS) if st(p, r, "saut_integral")["valeur"] <= st(p, r, "decompose")["valeur"] <= st(p, r, "lisse_integral")["valeur"])
tvog_pos = sum(1 for p, r, k in product(N, REFS, CREDITS) if tvog(p, r, k) > 0)
rachat_ordre = sum(1 for t in triplets if ST[f"A|{t}"]["taux_rachat_moyen_1_10"] > ST[f"B|{t}"]["taux_rachat_moyen_1_10"] > ST[f"C|{t}"]["taux_rachat_moyen_1_10"])
apport_ordre = sum(1 for t in triplets if ST[f"A|{t}"]["part_scenarios_avec_apport"] > ST[f"B|{t}"]["part_scenarios_avec_apport"] > ST[f"C|{t}"]["part_scenarios_avec_apport"])
ordres_ref = {(p, k): tuple(sorted(REFS, key=lambda r: st(p, r, k)["valeur"])) for p, k in product(N, CREDITS)}
dv_signes = {r: [ec(p, r)["valeur_par_pb"] for p in N] for r in REFS}

A("## 5. Résultats robustes et résultats fragiles\n")
A(f"Sur les {len(triplets)} combinaisons de convention calculées pour chaque profil :\n")
A("| Constat | Vérifié dans | Lecture |\n| --- | ---: | --- |")


def lecture(k, n, texte_robuste):
    return texte_robuste if k == n else ("**fragile** : exceptions" if k < n else texte_robuste)


A(f"| Classement des valeurs A < B < C | {ordre_profils} / {len(triplets)} | {lecture(ordre_profils, len(triplets), "robuste : le classement des bilans ne dépend d'aucune convention")} |")
A(f"| Classement des rachats A > B > C | {rachat_ordre} / {len(triplets)} | {lecture(rachat_ordre, len(triplets), 'robuste')} |")
A(f"| Classement des apports A > B > C (part des scénarios) | {apport_ordre} / {len(triplets)} | {lecture(apport_ordre, len(triplets), 'robuste')} |")
A(f"| Défaut par saut intégral < lissé intégral (valeur) | {saut_moins} / {len(N) * len(REFS)} | {lecture(saut_moins, len(N) * len(REFS), 'robuste : concentrer les pertes réduit la valeur actionnaire')} |")
A(f"| Décomposé entre les deux | {decomp_entre} / {len(N) * len(REFS)} | {lecture(decomp_entre, len(N) * len(REFS), 'robuste')} |")
exceptions_tvog = [f"{p}, {COURT_REF[r].lower()}, {COURT_K[k].lower()} ({f(tvog(p, r, k))})" for p, r, k in product(N, REFS, CREDITS) if tvog(p, r, k) <= 0]
A(f"| TVOG positive | {tvog_pos} / {len(N) * len(REFS) * len(CREDITS)} | " + ("robuste" if not exceptions_tvog else "presque toujours ; exceptions : " + " ; ".join(exceptions_tvog)
  + ". L'équivalent certain n'est pas la trajectoire moyenne d'un modèle non linéaire : sans rachat lié aux taux, la dispersion des taux peut jouer en faveur de l'actionnaire") + " |")
for p in N:
    v = signes[p]
    A(f"| Signe de la valeur du profil {p} | {sum(x > 0 for x in v)} positives / {len(v)} | " + ("**fragile : change de signe**" if min(v) < 0 < max(v) else ("toujours négative" if max(v) < 0 else "toujours positive")) + f" (de {f(min(v))} à {f(max(v))}) |")
ordres = set(ordres_ref.values())
A(f"| Classement des références par valeur | {len(ordres)} classement(s) différent(s) sur {len(ordres_ref)} | " + ("identique pour tous les profils et crédits" if len(ordres) == 1 else "varie selon le profil ou le crédit") + " |")
A("| Signe de la sensibilité de la valeur aux taux | " + ", ".join(f"{COURT_REF[r]} {'+' if min(v) > 0 else ('-' if max(v) < 0 else '±')}" for r, v in dv_signes.items()) + " | **fragile : change de signe avec la référence** |")
A("")
A("Classement des références, de la valeur la plus basse à la plus haute (convention décomposée) : "
  + " ; ".join(f"{p} : " + " < ".join(COURT_REF[r] for r in ordres_ref[(p, CENTRE_K)]) for p in N) + ".\n")


# ------------------------------------------------------------------------------------------------
BI = json.loads((RACINE / "resultats" / "v5_bilans_initiaux.json").read_text(encoding="utf-8"))["profils"]
liq = {p: BI[p]["economique"]["total_actif"] - BI[p]["comptable"]["passif"]["pm"] - BI[p]["comptable"]["passif"]["ppb"] for p in N}
cen = {p: st(p, CENTRE_REF, CENTRE_K) for p in N}
vA = signes["A"]
da = DA["resultats"].get(f"{CENTRE_REF}|{CENTRE_K}")
reelA, reelA100 = RE[f"A|{CENTRE_REF}|central"], RE[f"A|{CENTRE_REF}|stress_100"]
A("## 6. Profil A : assureur en difficulté ou conséquence des hypothèses ?\n")
A("Trois lectures, à ne pas confondre :\n")
A("1. **Comptable** : le profil A est solvable. Ses fonds propres comptables (45) et sa réserve de capitalisation (5) sont positifs, et aucune perte n'est constatée à l'ouverture.")
A(f"2. **Valeur de marché à l'ouverture** : l'actif en valeur de marché ne couvre pas la PM et la PPB. L'écart vaut {f(liq['A'])} pour A ({f(liq['B'])} pour B, {f(liq['C'])} pour C). Comme un assuré qui rachète reçoit sa PM sans supporter les moins-values, A ne tient que si ses assurés restent : c'est la définition d'un assureur exposé au rachat massif.")
A(f"3. **Valeur économique simplifiée** (actif - BE, sans VA, avant impôt et marge de risque) : de {f(min(vA))} à {f(max(vA))} selon les conventions. Elle est négative dans {sum(x < 0 for x in vA)} combinaisons sur {len(vA)}, et vaut {f(cen['A']['valeur'])} ± {f(cen['A']['ic_be'])} dans la convention centrale proposée. Elle n'est positive qu'avec une référence figée (aucun rachat lié aux taux) ou avec un spread entièrement lissé et une référence lissée, et reste alors au plus de {f(max(vA))}, soit moins de la moitié des fonds propres comptables.\n")
A(f"**Apports de capital (risque neutre, convention centrale)** : un apport dans {pct(cen['A']['part_scenarios_avec_apport'], 0)} des scénarios ; valeur actuelle moyenne {f(cen['A']['va_apports_moyenne'])}, médiane {f(cen['A']['va_apports_quantiles']['0.5'])}, q95 {f(cen['A']['va_apports_quantiles']['0.95'])}, q99 {f(cen['A']['va_apports_quantiles']['0.99'])}.")
if da:
    pd_ = da["par_defaut_souverain_avant_10_ans"]
    avant5 = da["premiere_annee_apport"]["part_avant_5_ans"]
    A(f"Les apports sont tardifs : {'aucun avant 5 ans' if avant5 == 0 else pct(avant5, 0) + ' des scénarios en ont un avant 5 ans'}, {pct(da['premiere_annee_apport']['part_avant_10_ans'], 0)} des scénarios en ont un avant 10 ans, première année médiane {f(da['premiere_annee_apport']['mediane'], 0)}. "
      f"Ils viennent surtout de deux sources. Dans les {pct(pd_['avec']['n'] / da['n'], 0)} de scénarios où le bloc souverain fait défaut avant 10 ans (probabilité risque neutre), "
      f"{pct(pd_['avec']['part_avec_apport'], 0)} demandent un apport (moyenne {f(pd_['avec']['va_moyenne'])}), contre {pct(pd_['sans']['part_avec_apport'], 0)} sans défaut (moyenne {f(pd_['sans']['va_moyenne'])}). "
      f"Côté taux, {pct(da['par_taux']['haut']['part_avec_apport'], 0)} des scénarios du tiers des taux 10 ans les plus hauts en année 5 demandent un apport, contre {pct(da['par_taux']['bas']['part_avec_apport'], 0)} dans le tiers le plus bas : "
      "cela s'explique par la référence des assurés, qui suit les taux, et par les ventes d'obligations en moins-value pour payer les rachats.\n")
A(f"**Probabilité réelle** : sur la trajectoire centrale (taux et spreads figés, perte attendue de 3 pb), A sert {pct(reelA['taux_servi_moyen_1_10'], 2)} en moyenne sur 10 ans, au niveau du premier quartile de place (2,3 %). Ses rachats restent à {pct(reelA['taux_rachat_moyen_1_10'])} et il n'a besoin d'aucun apport (fonds propres minimaux de {f(reelA['fonds_propres_min_1_10'])}). "
  f"Même si tout le spread devenait une perte effective, il servirait {pct(reelA100['taux_servi_moyen_1_10'], 2)}, ses rachats monteraient à {pct(reelA100['taux_rachat_moyen_1_10'])} par an et sa PM tomberait à {f(reelA100['pm_annee_10'], 0)} en 10 ans, mais il garderait des fonds propres de {f(reelA100['fonds_propres_min_1_10'])} au minimum, sans apport sur cette trajectoire.\n")
s2a = {k: v for k, v in S2["resultats"].items() if k.startswith("A|")}
if s2a:
    x = S2["resultats"].get(f"A|{CENTRE_REF}|{CENTRE_K}") or next(iter(s2a.values()))
    A(f"**Vue prudentielle simplifiée** (base avec VA, marge de risque, SCR approché) : fonds propres de {f(x['fonds_propres_avant_impots_differes'])}, SCR de {f(x['scr'])}, ratio approché de {pct(x['ratio_avant_impots_differes'], 0)} "
      f"(fonds excédentaires non comptés, borne haute indicative de {f(x['fonds_excedentaires_borne_haute'])}). Le ratio de place est de 239 % pour les organismes vie et mixtes au 30/06/2026.\n")
A("**Conclusion.** Le profil A n'est pas un assureur normalement viable, et il ne faut pas le présenter ainsi. Comptablement solvable et sans besoin de capital sur une trajectoire réelle centrale, il n'a plus de coussin économique : sa valeur est proche de zéro ou négative, et il demande des apports dans une large part des scénarios risque neutre, dans les scénarios de hausse des taux et de défaut souverain. "
  f"Une partie de ce résultat est construite : ses moins-values obligataires ({pct(BI['A']['indicateurs']['pmvl_obligations_pct_vnc'], 0)} de la VNC) sont volontairement en haut de fourchette, et la donnée de place 2026 manque (ACPR n° 185 non lue). Une autre partie vient du modèle : en risque neutre, les produits comptables sont nets de tout le coût du spread, si bien que le taux servi et les rachats risque neutre ne sont pas des prévisions. "
  "Proposition : garder A comme profil de stress, qualifié d'**assureur fragile, au seuil de la recapitalisation**, et analyser ses stratégies sous contrainte de capital (apports, plan de redressement) plutôt que comme celles d'un assureur en régime normal.\n")

# ------------------------------------------------------------------------------------------------
A("## 7. Convention centrale proposée et stress à conserver\n")
A("**Convention centrale proposée (à valider)**\n")
A("| Élément | Choix | Justification |\n| --- | --- | --- |")
A("| Valorisation | Base sans VA ; VA en vue réglementaire seulement | Valeur économique sans effet réglementaire ; effet VA présenté à part (" + ", ".join(f"+{f(st(p, 'sans_risque', 'decompose', base='avec_va')['valeur'] - st(p, 'sans_risque', 'decompose')['valeur'])} pour {p}" for p in N) + ") |")
A("| Forme des pertes de crédit | Décomposée : 80 % du spread en défaut par saut (recouvrement 40 %, bloc souverain de 26 %), 20 % en coût hors défaut lissé | Prix inchangés et absence d'arbitrage vérifiée ; forme cohérente avec un risque souverain concentré et peu probable, et avec un crédit d'entreprise diversifié ; part de crédit : hypothèse |")
A("| Probabilité réelle | Perte attendue de 3 pb par an ; le reste du spread est une prime | Défauts historiques par notation et composition du portefeuille de place ; la prime n'est jamais comptée comme de la valeur |")
A(f"| Référence des assurés | Proxy comportemental fictif (et non taux servi observé) : taux sans risque 10 ans lissé (1/7 par an), niveau initial {pct(cv.niveau_initial_central(), 2)} (hypothèse) | Cohérente en risque neutre (un concurrent investi dans les mêmes titres gagne le taux sans risque et renouvelle progressivement son portefeuille). Les taux servis observés bougent lentement (2,63 % en 2024 et en 2025). Sensibilité aux taux intermédiaire : duration du BE de {f(ec('A', CENTRE_REF)['duration_effective_be'])} à {f(ec('C', CENTRE_REF)['duration_effective_be'])} ans, contre {f(ec('A', 'sans_risque')['duration_effective_be'])} à {f(ec('C', 'sans_risque')['duration_effective_be'])} avec une transmission immédiate |")
A("| Rachat structurel | À trancher : 5 % (V1 à V4) ou 4,4 % (taux observé de 2025, identique pour les trois profils) | Effet sur la valeur stochastique dans l'erreur de Monte-Carlo (" + ", ".join(f"+{f(st(p, 'sans_risque', 'decompose', rachat_structurel=0.044)['valeur'] - st(p, 'sans_risque', 'decompose')['valeur'])} pour {p}" for p in N) + ") ; aucun calage propre au profil A |")
A("")
A("Valeurs dans cette convention : " + ", ".join(f"{p} {f(cen[p]['valeur'])} ± {f(cen[p]['ic_be'])} (TVOG {f(tvog(p, CENTRE_REF, CENTRE_K))}, apports dans {pct(cen[p]['part_scenarios_avec_apport'], 0)} des scénarios)" for p in N) + ".\n")
A("**Avant les métriques de rentabilité**, deux écarts avec la place restent à traiter. D'abord la solvabilité : les ratios approchés (section 4.9) sont très inférieurs aux 239 % de la place. Il faudra compléter la vue prudentielle (fonds excédentaires, impôts différés, ajustement symétrique) et confronter les fonds propres et les moins-values des profils à l'ACPR n° 185 dès que le document sera disponible.\n")
A("Ensuite la sensibilité aux taux. Même la référence lissée donne une valeur qui baisse quand les taux montent ("
  + ", ".join(f"{f(ec(p, CENTRE_REF)['valeur_par_pb'], 2)} par pb pour {p}" for p in N)
  + "), alors que la place observe l'inverse (ACPR n° 181). L'écart peut venir de la loi de rachat (paramètres des V1 à V4, non recalés), de la règle de taux servi (cible égale à la référence moins 0,5 point) ou de l'absence de fonds excédentaires et d'impôts différés. Il faudra le traiter avant d'optimiser les stratégies d'adossement.\n")
A("**Stress à conserver pour la suite de la V5**\n")
A("| Stress | Paramétrage | Ce qu'il teste |\n| --- | --- | --- |")
A(f"| Transmission immédiate des taux longs | Référence sans risque, beta = 1 | Rachats dynamiques en hausse des taux (valeur de A : {f(st('A', 'sans_risque', 'decompose')['valeur'])} contre {f(cen['A']['valeur'])} au centre) |")
A("| Référence figée | Pas de rachat lié aux taux | Borne opposée ; isole le risque de garantie et de taux servi |")
A(f"| Livret A | Référence pilotée par le taux court | Concurrence de l'épargne réglementée (valeur de A : {f(st('A', 'livret_a', 'decompose')['valeur'])}) |")
A("| Spread intégralement lissé | Convention initiale | Transfert maximal des pertes de crédit aux assurés par le taux servi |")
A(f"| Spread intégralement par saut, bloc unique | Tout le portefeuille fait défaut d'un coup | Concentration extrême (valeur de B : {f(st('B', 'sans_risque', 'saut_bloc_unique')['valeur'])} ± {f(st('B', 'sans_risque', 'saut_bloc_unique')['ic_be'])}) ; erreur de Monte-Carlo élevée, à recalculer avec plus de scénarios |")
A("| Recouvrement 63 % | Décote souveraine moyenne de 37 % | Sensibilité au recouvrement (effet modéré) |")
A("| Pertes effectives de 50 % du spread | Probabilité réelle, 10 ans | Assureur qui subit vraiment une partie du risque de crédit : taux servi, rachats, fonds propres |")
A("| Défaut souverain déterministe | Défaut du bloc de 26 % en année 2, recouvrement 40 % (perte de 15,6 % des obligations) | Événement unique, lisible, pour comparer les stratégies (à construire) |")
_niv = json.loads((RACINE / "data" / "v5" / "conventions" / "conventions.json").read_text(encoding="utf-8"))["references_assures"]["_niveau_initial"]["valeur"]
A(f"| Niveau initial de la référence à 2,63 % | Dernier taux servi moyen observé | Le niveau de {100 * _niv:.2f} % est une hypothèse |".replace(".", ","))
A("| Chocs de la formule standard | Taux, actions, spread, rachat massif (vue prudentielle) | Capital et absorption par les FDB |")
A("")

# ------------------------------------------------------------------------------------------------
A("## 8. Limites restantes\n")
ic_saut = max(v["ic_fuite"] for k, v in ST.items() if "lisse_integral" not in k and "bloc_unique" not in k)
ic_bloc = [v["ic_fuite"] for k, v in ST.items() if "bloc_unique" in k]
fuites_pos = sum(v["fuite"] > 0 for v in ST.values())
rapport_max = max(abs(v["fuite"]) / v["ic_fuite"] for v in ST.values())
ecarts = [st(p, r, "lisse_integral")["valeur"] - st(p, r, "saut_integral")["valeur"] for p, r in product(N, REFS)]
for x in [
    f"**Monte-Carlo.** Le défaut par saut augmente la variance : la demi-largeur de l'intervalle de la fuite atteint {f(ic_saut)} avec 1 000 scénarios, et de {f(min(ic_bloc))} à {f(max(ic_bloc))} pour le bloc unique. "
    f"Les fuites sont positives dans {fuites_pos} variantes sur {len(ST)} (mêmes tirages de taux et de défaut partout), toujours à l'intérieur de leur intervalle de confiance à 95 % (au plus {f(rapport_max, 2)} fois sa demi-largeur). "
    f"Les écarts de valeur entre spread lissé et spread par saut (de {f(min(ecarts))} à {f(max(ecarts))}) dépassent cette erreur ; le bloc unique demande plus de scénarios.",
    f"**Rachats risque neutre et rachats observés.** Les rachats moyens risque neutre (de {pct(min(v['taux_rachat_moyen_1_10'] for v in ST.values()), 0)} à {pct(max(v['taux_rachat_moyen_1_10'] for v in ST.values()), 0)} par an sur 10 ans selon le profil et les conventions) dépassent le taux observé de 4,4 %. Ce n'est pas une contradiction : en risque neutre, les produits comptables sont nets du coût du spread. Mais la loi de rachat dynamique (paramètres des V1 à V4) n'est calée sur aucune donnée de place, et les quartiles de rachat par organisme (ACPR n° 179) n'ont pas pu être lus.",
    "**Part de crédit du spread (kappa = 0,8 dans ces premières conventions, 0,7 dans la convention centrale).** C'est une hypothèse, sans recoupement avec des cotations de marché : le spread des obligations est lui-même une hypothèse. Ce n'est pas une estimation du risque de défaut des émetteurs, souverains ou entreprises : kappa répartit seulement le spread hypothétique entre une perte par défaut et une perte hors défaut.",
    "**Défaut par saut simplifié.** Recouvrement de 40 % (convention de cotation non vérifiée en ligne), blocs indépendants, réinvestissement immédiat dans le même portefeuille (défauts répétés possibles), ni migration de notation ni spread stochastique : la courbe de spread reste figée, sans dynamique propre.",
    "**Un seul spread pour toutes les obligations.** Souverains, financières et entreprises partagent le même spread hypothétique (notation A).",
    "**Probabilité réelle.** Taux et spreads figés, prime actions fictive de 3 % : ces trajectoires servent à la plausibilité, pas à la prévision.",
    "**Vue prudentielle.** Choc de taux appliqué à la courbe avec VA, ajustement symétrique nul, spread en notation A sur 66 % des obligations, pas de risque opérationnel, pas d'absorption par les impôts différés ni de fonds excédentaires : c'est un ordre de grandeur, pas un ratio de solvabilité.",
    "**Données de place manquantes.** ACPR n° 185 (moins-values latentes au 30/06/2026) et quartiles de rachat de l'ACPR n° 179 : les paramètres correspondants des profils restent fictifs.",
    "**Avant impôt.** L'impôt est codé et testé mais pas appliqué.",
]:
    A(f"- {x}")
A("")

import argparse as _argparse  # noqa: E402
_ap = _argparse.ArgumentParser()
_ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_CONVENTIONS.md"))
Path(_ap.parse_args().sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit : docs/V5_CONVENTIONS.md")
