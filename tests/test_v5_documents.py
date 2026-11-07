"""V5 : les documents versionnés correspondent exactement aux résultats versionnés.

Chaque générateur de document est relancé dans un dossier temporaire à partir de resultats/*.json et de
data/ ; sa sortie doit être identique, octet pour octet, au document versionné. Un chiffre modifié à la
main dans un document, ou un résultat recalculé sans régénérer le document, fait échouer le test. Les
figures sont produites dans un dossier temporaire (contrôle d'exécution : le rendu des PNG dépend des
polices installées, il n'est pas comparé octet pour octet).
"""

import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "scripts"))
from v5_documents import GENERATEURS  # noqa: E402

DOCUMENTS = [(s, c) for s, c in GENERATEURS if c.endswith(".md")]


def lancer(script, *args):
    subprocess.run([sys.executable, str(RACINE / "scripts" / f"{script}.py"), *args], check=True, cwd=RACINE,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


@pytest.mark.parametrize("script,cible", DOCUMENTS, ids=[c for _, c in DOCUMENTS])
def test_document_identique_a_sa_regeneration(script, cible, tmp_path):
    sortie = tmp_path / Path(cible).name
    args = ["--sortie", str(sortie)]
    if script == "v5_synthese_finale":
        args += ["--json", str(tmp_path / "v5_synthese_finale.json")]
    lancer(script, *args)
    assert sortie.read_text(encoding="utf-8") == (RACINE / cible).read_text(encoding="utf-8"), \
        f"{cible} ne correspond plus aux résultats : relancer python scripts/v5_documents.py"
    if script == "v5_synthese_finale":
        assert (tmp_path / "v5_synthese_finale.json").read_text(encoding="utf-8") == \
            (RACINE / "resultats" / "v5_synthese_finale.json").read_text(encoding="utf-8")


def test_figures_produites_depuis_les_resultats(tmp_path):
    lancer("v5_figures", "--sortie", str(tmp_path))
    attendues = {p.name for p in (RACINE / "figures" / "v5").glob("*.png")}
    assert attendues and attendues == {p.name for p in tmp_path.glob("*.png")}


def test_liens_relatifs_vers_des_fichiers_existants():
    """Liens relatifs du README et des documents : chaque fichier visé existe."""
    import re
    manquants = []
    for doc in [RACINE / "README.md", *sorted((RACINE / "docs").glob("*.md"))]:
        for lien in re.findall(r"\]\((?!https?://|#|mailto:)([^)]+)\)", doc.read_text(encoding="utf-8")):
            cible = (doc.parent / lien.split("#")[0]).resolve()
            if not cible.exists():
                manquants.append(f"{doc.name} -> {lien}")
    assert not manquants, manquants
