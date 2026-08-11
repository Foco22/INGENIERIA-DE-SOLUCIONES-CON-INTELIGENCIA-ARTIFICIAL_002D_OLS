"""Helpers para recorrer las fuentes de PDFs del repo y extraer su metadata.

Reconoce dos fuentes (plan.md §4.1, §4.4):
- "Experiencia de Aprendizaje */Clase */*.pdf"  -> tipo="clase"
- "evaluaciones/*.pdf"                          -> tipo="evaluacion"
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# mcp-asistente-curso/utils/paths.py -> el repo root queda 3 niveles arriba.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Los .md convertidos se comitean al repo (decisión explícita — no van gitignored),
# reflejando la misma estructura que su PDF fuente.
MARKDOWN_ROOT = Path(__file__).resolve().parent.parent / "data" / "markdown"

_EXPERIENCIA_RE = re.compile(r"^(Experiencia de Aprendizaje \d+)")
_CLASE_RE = re.compile(r"^(Clase \d+\.\d+)")


def _extract_experiencia(name: str) -> str:
    """De 'Experiencia de Aprendizaje 2 - Desarrollo de...' o el stem de un PDF
    de evaluaciones/, saca solo 'Experiencia de Aprendizaje 2'."""
    match = _EXPERIENCIA_RE.match(name)
    return match.group(1) if match else name


def _extract_clase(name: str) -> str:
    """De 'Clase 2.3' saca 'Clase 2.3' (por si el nombre de carpeta trae algo extra)."""
    match = _CLASE_RE.match(name)
    return match.group(1) if match else name


@dataclass(frozen=True)
class PdfSource:
    """Un PDF fuente con su metadata de ubicación (plan.md §4.1, §4.4)."""

    path: Path
    tipo: str  # "clase" | "evaluacion"
    experiencia: str
    clase: str | None  # None para tipo="evaluacion"

    @property
    def archivo(self) -> str:
        """Ruta relativa al repo — la cita que se devuelve en los fragmentos de las tools."""
        return str(self.path.relative_to(REPO_ROOT))

    @property
    def markdown_path(self) -> Path:
        """Ruta del .md convertido para este PDF (se comitea al repo, plan.md §4.1)."""
        return MARKDOWN_ROOT / self.path.relative_to(REPO_ROOT).with_suffix(".md")


def iter_clase_pdfs(repo_root: Path = REPO_ROOT) -> list[PdfSource]:
    """PDFs bajo 'Experiencia de Aprendizaje */Clase */*.pdf' -> tipo='clase'.

    Incluye todos los PDFs dentro de cada carpeta Clase */ (el archivo principal
    'Clase X.Y.pdf' y cualquier PDF de sub-tema, ej. '1.2.1 Técnicas de...pdf').
    """
    sources: list[PdfSource] = []
    for experiencia_dir in sorted(repo_root.glob("Experiencia de Aprendizaje *")):
        if not experiencia_dir.is_dir():
            continue
        experiencia = _extract_experiencia(experiencia_dir.name)
        for clase_dir in sorted(experiencia_dir.glob("Clase *")):
            if not clase_dir.is_dir():
                continue
            clase = _extract_clase(clase_dir.name)
            for pdf in sorted(clase_dir.glob("*.pdf")):
                sources.append(
                    PdfSource(path=pdf, tipo="clase", experiencia=experiencia, clase=clase)
                )
    return sources


def iter_evaluacion_pdfs(repo_root: Path = REPO_ROOT) -> list[PdfSource]:
    """PDFs bajo 'evaluaciones/*.pdf' -> tipo='evaluacion', uno por Experiencia."""
    sources: list[PdfSource] = []
    evaluaciones_dir = repo_root / "evaluaciones"
    for pdf in sorted(evaluaciones_dir.glob("*.pdf")):
        experiencia = _extract_experiencia(pdf.stem)
        sources.append(PdfSource(path=pdf, tipo="evaluacion", experiencia=experiencia, clase=None))
    return sources


def iter_all_pdfs(repo_root: Path = REPO_ROOT) -> list[PdfSource]:
    """Todas las fuentes de PDF del repo (clases + evaluaciones) — usado por indexer/run.py."""
    return iter_clase_pdfs(repo_root) + iter_evaluacion_pdfs(repo_root)
