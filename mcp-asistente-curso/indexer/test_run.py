"""Tests de indexer/run.py (build_index): diff-aware chunking+embeddings.

Usa fuentes sintéticas y un embed_documents falso (sin cargar el modelo real
de utils/embeddings.py) para que corra en segundos, no minutos. El único I/O
real es un .md de prueba bajo data/markdown/ — se limpia al final del test.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import indexer.run as run_mod
from utils.paths import REPO_ROOT, PdfSource


def _source(nombre: str) -> PdfSource:
    return PdfSource(
        path=REPO_ROOT / "Experiencia de Aprendizaje 1" / "Clase 1.1" / f"_test_fixture_{nombre}.pdf",
        tipo="clase",
        experiencia="Experiencia de Aprendizaje 1",
        clase="Clase 1.1",
    )


@pytest.fixture
def fake_source(monkeypatch):
    """Fuente de prueba con su .md real en disco (se limpia al terminar)."""
    source = _source("a")
    source.markdown_path.parent.mkdir(parents=True, exist_ok=True)
    source.markdown_path.write_text("# Tema A\n" + "x" * 100, encoding="utf-8")
    monkeypatch.setattr(run_mod, "embed_documents", lambda texts: [[0.0, 1.0] for _ in texts])
    yield source
    source.markdown_path.unlink(missing_ok=True)


def test_primera_corrida_embebe_lo_reprocesado(tmp_path: Path, fake_source, monkeypatch) -> None:
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [fake_source])
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    chunks_path = tmp_path / "chunks.parquet"

    run_mod.build_index(manifest_path=tmp_path / "manifest.json", chunks_path=chunks_path)

    df = pd.read_parquet(chunks_path)
    assert len(df) == 1
    assert df.iloc[0]["heading"] == "Tema A"
    assert df.iloc[0]["archivo"] == fake_source.archivo


def test_pdf_sin_cambios_pero_sin_chunks_se_embebe_igual(tmp_path: Path, fake_source, monkeypatch) -> None:
    """Bootstrap: el manifest dice 'sin cambios', pero chunks.parquet está vacío."""
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [])  # nada cambió
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    chunks_path = tmp_path / "chunks.parquet"  # no existe -> vacío

    run_mod.build_index(manifest_path=tmp_path / "manifest.json", chunks_path=chunks_path)

    df = pd.read_parquet(chunks_path)
    assert len(df) == 1


def test_pdf_ya_indexado_y_sin_cambios_no_se_reembebe(tmp_path: Path, fake_source, monkeypatch) -> None:
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    chunks_path = tmp_path / "chunks.parquet"

    # Corrida 1: se indexa.
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [fake_source])
    run_mod.build_index(manifest_path=tmp_path / "manifest.json", chunks_path=chunks_path)

    # Corrida 2: nada cambió, ya está en el parquet -> no debería volver a llamar embed_documents.
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [])
    calls = []
    monkeypatch.setattr(run_mod, "embed_documents", lambda texts: calls.append(texts) or [])
    run_mod.build_index(manifest_path=tmp_path / "manifest.json", chunks_path=chunks_path)

    assert calls == []
    assert len(pd.read_parquet(chunks_path)) == 1  # sin duplicados
