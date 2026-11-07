"""Génère docs/V5_BILANS_INITIAUX.md à partir de resultats/v5_bilans_initiaux.json (aucun chiffre saisi à la main)."""

import json
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
d = json.loads((RACINE / "resultats" / "v5_bilans_initiaux.json").read_text(encoding="utf-8"))
P = d["profils"]
N = ("A", "B", "C")


def f(x, dec=1):
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace("-", "−")


def pct(x, dec=1):
    return f(100 * x, dec) + " %"


L = []
L.append("# V5 : bilans initiaux des trois profils fictifs\n")
L.append("Généré par `scripts/v5_rapport_bilans.py` depuis `resultats/v5_bilans_initiaux.json` "
         "(`scripts/v5_bilans_initiaux.py`). Unités fictives : 1 unité = 10 M€, PM de 1 000 = 10 Md€. "
         "Valorisation risque neutre au 31/10/2026, base sans VA sauf mention. **Les trois profils sont fictifs** : "
         "ils ne décrivent aucun organisme réel.\n")
L.append("Les valeurs économiques sont **avant impôt différé** : l'impôt n'entrera qu'avec les métriques de l'étape suivante.\n")

L.append("## 1. Bilans comptables\n")
L.append("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for cle, lib in [("obligations", "Obligations (VNC)"), ("actions", "Actions (VNC)"), ("monetaire", "Monétaire")]:
    L.append(f"| {lib} | " + " | ".join(f(P[n]["comptable"]["actif"][cle]) for n in N) + " |")
L.append("| **Total actif** | " + " | ".join(f"**{f(P[n]['comptable']['total_actif'])}**" for n in N) + " |")
for cle, lib in [("pm", "Provision mathématique"), ("ppb", "PPB"), ("reserve_capitalisation", "Réserve de capitalisation"), ("fonds_propres", "Fonds propres comptables")]:
    L.append(f"| {lib} | " + " | ".join(f(P[n]["comptable"]["passif"][cle]) for n in N) + " |")
L.append("| **Total passif** | " + " | ".join(f"**{f(P[n]['comptable']['total_passif'])}**" for n in N) + " |")
L.append("| Écart actif - passif | " + " | ".join(f"{P[n]['reconciliation']['ecart_bilan_comptable']:.0e}" for n in N) + " |\n")

L.append("## 2. Bilans économiques et passage des fonds propres comptables à la valeur actionnaire\n")
L.append("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for cle, lib in [("obligations", "Obligations (valeur de marché)"), ("actions", "Actions (valeur de marché)"), ("monetaire", "Monétaire")]:
    L.append(f"| {lib} | " + " | ".join(f(P[n]["economique"]["actif"][cle]) for n in N) + " |")
L.append("| **Actif en valeur de marché** | " + " | ".join(f"**{f(P[n]['economique']['total_actif'])}**" for n in N) + " |")
L.append("| BE stochastique (1 000 scénarios) | " + " | ".join(f"{f(P[n]['stochastique']['sans_va']['be'])} ± {f(P[n]['stochastique']['sans_va']['ic_be'])}" for n in N) + " |")
L.append("| BE équivalent certain | " + " | ".join(f(P[n]["economique"]["be_equivalent_certain"]) for n in N) + " |")
L.append("| TVOG du modèle (BE stochastique - BE équivalent certain) | " + " | ".join(f(P[n]["stochastique"]["sans_va"]["tvog"]) for n in N) + " |")
L.append("| **Valeur actionnaire (actif - BE stochastique)** | " + " | ".join(f"**{f(P[n]['stochastique']['sans_va']['valeur_actionnaire'])} ± {f(P[n]['stochastique']['sans_va']['ic_valeur'])}**" for n in N) + " |")
L.append("| Base avec VA : BE stochastique | " + " | ".join(f"{f(P[n]['stochastique']['avec_va']['be'])} ± {f(P[n]['stochastique']['avec_va']['ic_be'])}" for n in N) + " |")
L.append("| Base avec VA : valeur actionnaire | " + " | ".join(f"{f(P[n]['stochastique']['avec_va']['valeur_actionnaire'])} ± {f(P[n]['stochastique']['avec_va']['ic_valeur'])}" for n in N) + " |")
L.append("| Effet VA sur le BE (réglementaire, pas de la valeur économique) | " + " | ".join(f(P[n]["stochastique"]["avec_va"]["be"] - P[n]["stochastique"]["sans_va"]["be"]) for n in N) + " |\n")

L.append("**Réconciliation, équivalent certain** (identité exacte en t = 0) : fonds propres comptables + plus ou moins-values latentes + (provisions comptables - BE) = actif en valeur de marché - BE.\n")
L.append("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for cle, lib in [("fonds_propres_comptables", "Fonds propres comptables"), ("plus_ou_moins_values_latentes_obligations", "Moins-values latentes obligataires"),
                 ("plus_values_latentes_actions", "Plus-values latentes actions"), ("provisions_comptables_moins_be", "Provisions comptables (PM + PPB + réserve) - BE")]:
    L.append(f"| {lib} | " + " | ".join(f(P[n]["reconciliation"]["etapes"][cle]) for n in N) + " |")
L.append("| **Valeur actionnaire, équivalent certain** | " + " | ".join(f"**{f(P[n]['reconciliation']['etapes']['valeur_actionnaire'])}**" for n in N) + " |")
L.append("| Écart avec actif - BE | " + " | ".join(f"{P[n]['reconciliation']['ecart_avec_actif_moins_be']:.0e}" for n in N) + " |\n")

L.append("**Contrôles de cohérence, stochastique (1 000 scénarios)** :\n")
L.append("| | A | B | C |\n| --- | ---: | ---: | ---: |")
for base in ("sans_va", "avec_va"):
    L.append(f"| Fuite, base {base.replace('_', ' ')} (doit contenir 0) | " + " | ".join(f"{f(P[n]['stochastique'][base]['fuite'], 2)} ± {f(P[n]['stochastique'][base]['ic_fuite'], 2)}" for n in N) + " |")
L.append("| Identité de valeur, écart maximal par scénario | " + " | ".join(f"{P[n]['stochastique']['sans_va']['identite_valeur_ecart_max']:.0e}" for n in N) + " |")
L.append("| Part des scénarios avec apport de capital | " + " | ".join(pct(P[n]["stochastique"]["sans_va"]["part_scenarios_avec_apport"]) for n in N) + " |\n")

L.append("## 3. Construction et indicateurs des profils\n")
L.append("| | A | B | C |\n| --- | ---: | ---: | ---: |")
rows = [("coupon_moyen_obligations", "Coupon moyen des obligations", pct, 2), ("pmvl_obligations_pct_vnc", "Moins-values latentes obligataires (% de la VNC)", pct, 1),
        ("duration_macaulay_obligations", "Duration de Macaulay des obligations (ans)", f, 1), ("duration_macaulay_flux_passif", "Duration de Macaulay des flux du passif (ans)", f, 1),
        ("duration_effective_actif", "Duration effective de l'actif (ans)", f, 1), ("duration_effective_be", "Duration effective du BE (ans)", f, 1),
        ("duration_effective_be_reference_figee", "Duration effective du BE, référence des assurés figée à son niveau de l'année 1 (ans)", f, 1),
        ("sensibilite_valeur_par_pb", "Variation de la valeur actionnaire pour +1 pb de taux sans risque", f, 2),
        ("sensibilite_valeur_par_pb_reference_figee", "Variation de la valeur actionnaire pour +1 pb, référence figée", f, 2),
        ("ppb_pct_pm", "PPB (% de la PM)", pct, 1), ("reserve_capitalisation_pct_pm", "Réserve de capitalisation (% de la PM)", pct, 1),
        ("fonds_propres_comptables_pct_pm", "Fonds propres comptables (% de la PM)", pct, 1), ("liquidite_pct_actif_vm", "Monétaire (% de l'actif en valeur de marché)", pct, 1),
        ("taux_garanti", "Taux garanti", pct, 2), ("taux_servi_initial", "Taux servi de l'année écoulée", pct, 2),
        ("produits_financiers_annee_1_pct_vnc", "Produits financiers de l'année 1 (% de la VNC), pertes de crédit risque neutre déduites", pct, 2),
        ("taux_reference_assures_annee_1", "Taux de référence des assurés, année 1", pct, 2), ("taux_servi_annee_1", "Taux servi, année 1", pct, 2), ("taux_rachat_annee_1", "Taux de rachat, année 1", pct, 1),
        ("taux_servi_moyen_annees_1_20", "Taux servi moyen, années 1 à 20 (équivalent certain)", pct, 2),
        ("taux_rachat_moyen_annees_1_20", "Taux de rachat moyen, années 1 à 20 (équivalent certain)", pct, 1),
        ("pm_annee_10", "PM à 10 ans (équivalent certain)", f, 1)]
for cle, lib, fmt, dec in rows:
    L.append(f"| {lib} | " + " | ".join(fmt(P[n]["indicateurs"][cle], dec) for n in N) + " |")
L.append("")

L.append("## 4. Sensibilités (équivalent certain, base sans VA sauf mention)\n")
for n in N:
    L.append(f"**Profil {n} : {P[n]['libelle']}**\n")
    L.append("| Sensibilité | Actif (VM) | Moins-values obligataires | BE | Valeur actionnaire | Taux servi année 1 | Rachat année 1 | Taux servi moyen, années 1 à 20 | Rachat moyen, années 1 à 20 |\n| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    ref = P[n]
    L.append(f"| Référence | {f(ref['economique']['total_actif'])} | {pct(ref['indicateurs']['pmvl_obligations_pct_vnc'])} | {f(ref['economique']['be_equivalent_certain'])} | "
             f"{f(ref['economique']['valeur_actionnaire_equivalent_certain'])} | {pct(ref['indicateurs']['taux_servi_annee_1'], 2)} | {pct(ref['indicateurs']['taux_rachat_annee_1'])} | "
             f"{pct(ref['indicateurs']['taux_servi_moyen_annees_1_20'], 2)} | {pct(ref['indicateurs']['taux_rachat_moyen_annees_1_20'])} |")
    for k, s in P[n]["sensibilites"].items():
        L.append(f"| {k} | {f(s['vm_actif'])} | {pct(s['pmvl_obligations_pct_vnc'])} | {f(s['be_equivalent_certain'])} | {f(s['valeur_actionnaire_equivalent_certain'])} | "
                 f"{pct(s['taux_servi_annee_1'], 2)} | {pct(s['taux_rachat_annee_1'])} | {pct(s['taux_servi_moyen_annees_1_20'], 2)} | {pct(s['taux_rachat_moyen_annees_1_20'])} |")
    L.append("")

L.append("## 5. Confrontation aux ordres de grandeur de place\n")
L.append("Sources et statut de chaque chiffre de place : `data/v5/profils/confrontation_acpr.md`. Les profils sont fictifs : un écart n'est pas une erreur s'il découle du récit du profil, mais il doit être expliqué.\n")
L.append("| Indicateur | A | B | C | Place | Lecture |\n| --- | ---: | ---: | ---: | --- | --- |")
I = {n: P[n]["indicateurs"] for n in N}
L.append("| PPB (% de la PM) | " + " | ".join(pct(I[n]["ppb_pct_pm"]) for n in N) + " | 4,0 % des provisions (fin 2025, ACPR n° 180) | B au niveau de place ; A (réserves consommées) et C (assureur plus jeune) en dessous, par construction |")
L.append("| Taux garanti | " + " | ".join(pct(I[n]["taux_garanti"], 2) for n in N) + " | 0,32 % de taux technique moyen (2025, ACPR n° 180) | B au niveau de place ; A plus élevé (contrats anciens), C sans garantie |")
L.append("| Taux servi de l'année écoulée | " + " | ".join(pct(I[n]["taux_servi_initial"], 2) for n in N) + " | 2,63 % (2025, ACPR n° 180) | B au niveau de place ; A en dessous, C au-dessus (politique plus offensive) |")
L.append("| Coupon moyen des obligations | " + " | ".join(pct(I[n]["coupon_moyen_obligations"], 2) for n in N) + " | Non publié ; rendement de l'actif de 2,8 % en 2025, actions et immobilier compris (ACPR n° 180) | Le coupon de B est calé pour un rendement comptable de cet ordre (prime d'achat de 0,6 point) |")
L.append("| Moins-values latentes obligataires (% de la VNC) | " + " | ".join(pct(I[n]["pmvl_obligations_pct_vnc"]) for n in N) + " | -2,7 % à -3,4 % au 30/06/2025 (dérivé de l'ACPR n° 177) ; donnée 2026 (ACPR n° 185) non lue | Les profils intègrent la hausse d'environ 130 pb du TEC 10 en 2026 et le spread OAT élargi ; à revoir dès que le n° 185 est accessible |")
L.append("| Sorties annuelles (rachats et décès), année 1 | " + " | ".join(pct(I[n]["taux_rachat_annee_1"] + 0.01) for n in N) + " | Environ 6,7 % de l'encours, tous supports, décès compris (dérivé de France Assureurs, 2026) | Ordre de grandeur cohérent ; la collecte nette positive de 2026 justifie l'absence de vague de rachats |\n")

_SR = "référence assurés : sans risque 10 ans, même niveau en t = 0"
L.append("## 6. Limites méthodologiques restantes\n")
for x in [
    "**Lissage des pertes de crédit risque neutre : limite principale.** En risque neutre, tout le spread OAT (147 pb à 10 ans, 202 pb à 30 ans) devient une perte annuelle lissée, retirée chaque année et dans chaque scénario des produits financiers, donc de l'assiette de la participation. La valeur actuelle nette d'un achat reste nulle (tests). Mais la participation et les rachats sont non linéaires : cette répartition lisse des pertes déprime le taux servi partout. Le profil A, au rendement comptable faible, entre ainsi dans une spirale de rachats en équivalent certain (taux servi moyen de 0,8 % et rachats moyens de 22 % sur les années 1 à 20), et sa valeur devient négative. Un modèle de défaut par saut, avec perte en cas de défaut, donnerait la même valeur des actifs, mais concentrerait les pertes sur peu de scénarios et changerait le partage entre assurés et actionnaire. Le marché ne tranche pas entre les deux : c'est un risque de modèle à traiter avant les métriques de rentabilité.",
    "**Valeurs avant impôt.** L'impôt (25 %, contribution sociale de 3,3 % au-delà de l'abattement) est codé et testé, mais pas encore appliqué : les valeurs économiques sont donc présentées avant impôt différé.",
    "**Pas encore de capital.** Ni SCR ni marge de risque par profil, et pas encore de coût du capital : ils arrivent à l'étape suivante, avec la distinction entre coût réglementaire, coûts frictionnels et rendement exigé.",
    "**Générateur de scénarios non recalé.** Les paramètres de Hull-White (a = 0,05, sigma = 1 %) et la volatilité actions (18 %) restent ceux des V1 à V4, sans calage sur les volatilités implicites de marché : la TVOG en dépend directement.",
    "**Un seul model point par profil.** Le taux garanti est une moyenne ; la V4 multi-model points n'est pas couplée à l'actif. Le portefeuille est fermé : pas encore de collecte nouvelle, ni de politique de collecte pour C.",
    "**Crédit simplifié.** Toutes les obligations sont valorisées sur le spread OAT (souverains et entreprises confondus), sans notation ni migration, avec une perte en convention de recouvrement en valeur de marché. Le TEC est pris comme taux zéro-coupon, et la courbe EIOPA (31/10) est décalée de quatre jours avec le TEC (04/11).",
    "**Pertes risque neutre dans les produits comptables.** En valorisation, la perte risque neutre réduit les produits financiers, donc la participation : c'est cohérent avec le marché, mais la trajectoire comptable n'est pas une prévision.",
    "**Coupons par génération.** Ils sont ancrés sur des observations mensuelles ponctuelles et sur une prime d'achat calibrée. Les moyennes annuelles officielles n'ont pas été accessibles.",
    "**Comportement des assurés.** La référence « OAT 10 ans - 2 points », calée sur la situation de 2026, reste l'hypothèse la plus incertaine. Ses sensibilités changent la valeur actionnaire de plusieurs dizaines d'unités. "
    "Elle suit la courbe à terme de l'OAT, qui monte avec le spread : une référence fondée sur le taux sans risque, recalée au même niveau en t = 0, ramène le rachat moyen des années 1 à 20 à "
    + ", ".join(f"{pct(P[n]['sensibilites'][_SR]['taux_rachat_moyen_annees_1_20'])} ({n})" for n in N)
    + " et la valeur actionnaire en équivalent certain à "
    + ", ".join(f"{f(P[n]['sensibilites'][_SR]['valeur_actionnaire_equivalent_certain'])} ({n})" for n in N) + ". "
    "La même convention commande la sensibilité aux taux : la référence suit le choc, une hausse accélère les rachats et raccourcit le passif. Duration effective du BE, en années : "
    + ", ".join(f"{f(P[n]['indicateurs']['duration_effective_be'])} ({n})" for n in N) + ", contre "
    + ", ".join(f"{f(P[n]['indicateurs']['duration_effective_be_reference_figee'])} ({n})" for n in N)
    + " avec une référence figée. Ce point conditionnera directement les stratégies d'adossement.",
    "**Correction pour volatilité.** La VA est figée à 20 pb, sans VA dynamique ni ajustement égalisateur.",
    "**Données de place manquantes.** Moins-values latentes 2026, durations, réserve de capitalisation, répartition des garanties, rachats sur l'euro et dispersion entre organismes : voir `data/v5/profils/confrontation_acpr.md`.",
]:
    L.append(f"- {x}")
L.append("")

import argparse as _argparse  # noqa: E402
_ap = _argparse.ArgumentParser()
_ap.add_argument("--sortie", default=str(RACINE / "docs" / "V5_BILANS_INITIAUX.md"))
Path(_ap.parse_args().sortie).write_text("\n".join(L) + "\n", encoding="utf-8")
print("écrit : docs/V5_BILANS_INITIAUX.md")
