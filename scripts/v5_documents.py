"""V5 : régénère tous les documents et toutes les figures à partir des résultats versionnés.

Usage : python scripts/v5_documents.py
Aucune simulation n'est relancée : chaque générateur lit resultats/*.json et data/, puis écrit docs/ et
figures/v5/. Après un `git checkout` propre, cette commande ne doit modifier aucun fichier
(tests/test_v5_documents.py le vérifie générateur par générateur).
"""

import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

# Ordre : la synthèse finale écrit resultats/v5_synthese_finale.json, lu par les figures.
GENERATEURS = [
    ("v5_registre_hypotheses", "docs/V5_HYPOTHESES.md"),
    ("v5_rapport_bilans", "docs/V5_BILANS_INITIAUX.md"),
    ("v5_rapport_conventions", "docs/V5_CONVENTIONS.md"),
    ("v5_rapport_synthese", "docs/V5_SYNTHESE_AVANT_OPTIMISATION.md"),
    ("v5_rapport_strategies", "docs/V5_STRATEGIES.md"),
    ("v5_synthese_strategies", "docs/V5_SYNTHESE_STRATEGIES.md"),
    ("v5_rapport_collecte", "docs/V5_COLLECTE.md"),
    ("v5_synthese_finale", "docs/V5_SYNTHESE_FINALE.md"),
    ("v5_rapport_audit", "docs/V5_AUDIT_CONVENTIONS.md"),
    ("v5_figures", "figures/v5/"),
]


def main():
    for script, cible in GENERATEURS:
        print(f"{script} -> {cible}", flush=True)
        subprocess.run([sys.executable, str(RACINE / "scripts" / f"{script}.py")], check=True, cwd=RACINE, stdout=subprocess.DEVNULL)
    print("documents et figures régénérés")


if __name__ == "__main__":
    main()
