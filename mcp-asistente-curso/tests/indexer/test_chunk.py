"""Tests del chunking (indexer/chunk.py). Ver plan.md §4.1, paso 3.

Markdown sintético, no depende de PDFs reales ni de ingest.py.
"""

from __future__ import annotations

from indexer.chunk import chunk_markdown
from utils.paths import REPO_ROOT, PdfSource


def _source(tipo: str = "clase") -> PdfSource:
    # PdfSource.archivo necesita una ruta bajo REPO_ROOT para poder calcular
    # la relativa; no hace falta que el archivo exista de verdad en disco.
    clase = "Clase 1.1" if tipo == "clase" else None
    return PdfSource(
        path=REPO_ROOT / "Experiencia de Aprendizaje 1" / "Clase 1.1" / "Clase 1.1.pdf",
        tipo=tipo,
        experiencia="Experiencia de Aprendizaje 1",
        clase=clase,
    )


def test_split_basico_por_heading() -> None:
    markdown = "# Intro\ncontenido de la intro, con largo suficiente para no fundirse.\n\n## Tema 1\ncontenido del tema 1, también con largo suficiente."
    chunks = chunk_markdown(markdown, _source())

    assert [c.heading for c in chunks] == ["Intro", "Tema 1"]
    assert all(c.experiencia == "Experiencia de Aprendizaje 1" for c in chunks)
    assert all(c.clase == "Clase 1.1" for c in chunks)


def test_contenido_antes_del_primer_heading_se_descarta() -> None:
    markdown = "esto es ruido de portada, nombre del docente, etc.\n\n# Tema real\ncontenido del tema, con largo suficiente para no fundirse con nada."
    chunks = chunk_markdown(markdown, _source())

    assert len(chunks) == 1
    assert chunks[0].heading == "Tema real"
    assert "ruido de portada" not in chunks[0].texto


def test_secciones_cortas_se_funden_con_la_siguiente() -> None:
    markdown = "# Muy corto\nabc\n\n## Con contenido real\n" + ("x" * 100)
    chunks = chunk_markdown(markdown, _source())

    assert len(chunks) == 1
    assert chunks[0].heading == "Muy corto / Con contenido real"
    assert "abc" in chunks[0].texto


def test_seccion_larga_se_divide_por_parrafo() -> None:
    parrafo = "y" * 1500
    markdown = f"# Tema largo\n{parrafo}\n\n{parrafo}\n\n{parrafo}"
    chunks = chunk_markdown(markdown, _source())

    assert len(chunks) > 1
    assert all("Tema largo (parte" in c.heading for c in chunks)
    assert all(len(c.texto) <= 2000 for c in chunks)


def test_chunk_id_estable_y_unico() -> None:
    markdown = "# A\n" + ("a" * 50) + "\n\n# B\n" + ("b" * 50)
    chunks = chunk_markdown(markdown, _source())

    assert chunks[0].chunk_id != chunks[1].chunk_id
    # mismo (archivo, índice) -> mismo id, sin importar el texto
    assert chunks[0].chunk_id == chunk_markdown(markdown, _source())[0].chunk_id


def test_sin_headings_no_produce_chunks() -> None:
    markdown = "solo texto plano, sin ningún heading en todo el documento."
    chunks = chunk_markdown(markdown, _source())

    assert chunks == []


def test_evaluacion_no_tiene_clase() -> None:
    markdown = "# Pauta\n" + ("x" * 100)
    chunks = chunk_markdown(markdown, _source(tipo="evaluacion"))

    assert chunks[0].tipo == "evaluacion"
    assert chunks[0].clase is None
