"""Chequeos automáticos de la conversión PDF -> Markdown. Ver plan.md §4.1.

Umbrales calibrados corriendo la conversión real sobre el corpus del repo
(27 PDFs: clases + evaluaciones) — no son números arbitrarios. Con
`pymupdf4llm` el ratio markdown/texto-plano observado fue 1.28-2.65 (usa
OCR por página, así que normalmente extrae MÁS texto que `pypdf`, no
menos) y los headings detectados fueron 12-28 por PDF.
"""

from __future__ import annotations

import pytest
from pypdf import PdfReader

from indexer.ingest import pdf_to_markdown
from utils.paths import PdfSource, iter_all_pdfs

_MIN_LENGTH_RATIO = 0.3  # piso laxo: solo para atrapar fallos casi totales
_MIN_HEADINGS = 1


def _plain_text_length(source: PdfSource) -> int:
    reader = PdfReader(str(source.path))
    return sum(len(page.extract_text() or "") for page in reader.pages)


@pytest.fixture(scope="module")
def all_sources() -> list[PdfSource]:
    sources = iter_all_pdfs()
    assert sources, "no se encontró ningún PDF (¿corriste esto fuera del repo?)"
    return sources


def test_encuentra_las_dos_fuentes(all_sources: list[PdfSource]) -> None:
    tipos = {s.tipo for s in all_sources}
    assert tipos == {"clase", "evaluacion"}
    assert sum(1 for s in all_sources if s.tipo == "evaluacion") == 3


@pytest.mark.parametrize(
    "source",
    iter_all_pdfs(),
    ids=lambda s: s.archivo,
)
def test_conversion_pdf_a_markdown(source: PdfSource) -> None:
    result = pdf_to_markdown(source)

    assert result.markdown.strip(), f"{source.archivo}: markdown vacío"
    assert not result.has_replacement_chars, (
        f"{source.archivo}: contiene '�' (señal de mala extracción/encoding)"
    )
    assert result.heading_count >= _MIN_HEADINGS, (
        f"{source.archivo}: {result.heading_count} headings, se esperaba >= {_MIN_HEADINGS}"
    )

    plain_len = _plain_text_length(source)
    if plain_len > 0:
        ratio = len(result.markdown) / plain_len
        assert ratio >= _MIN_LENGTH_RATIO, (
            f"{source.archivo}: ratio texto md/plano = {ratio:.2f}, se esperaba >= {_MIN_LENGTH_RATIO}"
        )