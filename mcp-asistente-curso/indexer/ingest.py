"""PDF -> Markdown. Ver plan.md §4.1.

Usa `pymupdf4llm` como conversor. El plan original consideraba `docling` como
primera opción (mejor con tablas/estructura compleja), pero instalarlo acá
resultó impráctico: su árbol de dependencias (torch, easyocr, transformers)
tardó más de 30s solo en resolverse. `pymupdf4llm` se instala en segundos,
no necesita GPU/modelos pesados, y preserva headings y tablas razonablemente
bien (ver la validación manual en indexer/test_ingest.py). Si más adelante
un PDF con diagramas/tablas complejas sale mal, se puede reevaluar `docling`
puntualmente para esos casos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pymupdf4llm

from indexer.manifest import MANIFEST_PATH, changed_sources, load_manifest, save_manifest
from utils.paths import PdfSource, iter_all_pdfs

_REPLACEMENT_CHAR = "�"  # '�' -- señal de mala extracción/encoding
_HEADING_RE = re.compile(r"^#{1,6}\s+\S", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|.+\|\s*$", re.MULTILINE)


@dataclass(frozen=True)
class IngestResult:
    """Markdown convertido de un PdfSource, con las señales que usa la validación (§4.1)."""

    source: PdfSource
    markdown: str

    @property
    def heading_count(self) -> int:
        return len(_HEADING_RE.findall(self.markdown))

    @property
    def has_replacement_chars(self) -> bool:
        return _REPLACEMENT_CHAR in self.markdown

    @property
    def has_table(self) -> bool:
        return bool(_TABLE_ROW_RE.search(self.markdown))


def pdf_to_markdown(source: PdfSource) -> IngestResult:
    """Convierte un PDF a Markdown, preservando headings. Ver plan.md §4.1, paso 1."""
    markdown = pymupdf4llm.to_markdown(str(source.path))
    return IngestResult(source=source, markdown=markdown)


def write_markdown(result: IngestResult) -> None:
    """Escribe el .md convertido en su ruta espejo bajo data/markdown/ — se comitea al repo."""
    output_path = result.source.markdown_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.markdown, encoding="utf-8")


def ingest_all(manifest_path: Path = MANIFEST_PATH) -> list[PdfSource]:
    """Convierte y escribe el .md de los PDFs nuevos/modificados (diff-aware, §4.1 paso 2).

    Los PDFs cuyo hash no cambió desde la última corrida (según `manifest_path`)
    se saltan por completo — ni se reconvierten ni se re-escribe su .md.

    Devuelve las fuentes que sí se reprocesaron — indexer/run.py (Fase 2+) la usa
    para saber a cuáles hay que re-chunkear/re-embeber, sin recalcular el diff dos veces.
    """
    sources = iter_all_pdfs()
    previous_manifest = load_manifest(manifest_path)
    to_process, current_manifest = changed_sources(sources, previous_manifest)

    skipped = len(sources) - len(to_process)
    print(f"{len(to_process)} nuevos/modificados, {skipped} sin cambios (de {len(sources)} totales).")

    for i, source in enumerate(to_process, start=1):
        print(f"[{i}/{len(to_process)}] {source.archivo}")
        result = pdf_to_markdown(source)
        write_markdown(result)

    save_manifest(current_manifest, manifest_path)
    return to_process


if __name__ == "__main__":
    ingest_all()