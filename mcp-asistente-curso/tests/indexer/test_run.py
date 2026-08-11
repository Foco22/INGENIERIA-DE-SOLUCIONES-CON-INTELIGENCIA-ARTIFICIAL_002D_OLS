"""Tests de indexer/run.py (build_index): diff-aware chunking+embeddings+grafo.

Usa fuentes sintéticas, un embed_documents falso y un merge_source_into_graph
falso (sin cargar el modelo de embeddings ni llamar a Groq) para que corra en
segundos, no minutos. El único I/O real es un .md de prueba bajo
data/markdown/ — se limpia al final del test.
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
    monkeypatch.setattr(
        run_mod, "merge_source_into_graph", lambda graph, markdown, src: graph.add_node(src.archivo, nombre=src.archivo, clases={src.archivo})
    )
    # Como retract_source real (usa .discard, no explota si el nodo no está todavía).
    monkeypatch.setattr(
        run_mod, "retract_source", lambda graph, archivo: graph.remove_node(archivo) if archivo in graph else None
    )

    yield source
    source.markdown_path.unlink(missing_ok=True)


def _paths(tmp_path: Path) -> dict:
    return {
        "manifest_path": tmp_path / "manifest.json",
        "chunks_path": tmp_path / "chunks.parquet",
        "graph_path": tmp_path / "graph.json",
    }


def test_primera_corrida_embebe_y_grafica_lo_reprocesado(tmp_path: Path, fake_source, monkeypatch) -> None:
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [fake_source])
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    paths = _paths(tmp_path)

    run_mod.build_index(**paths)

    df = pd.read_parquet(paths["chunks_path"])
    assert len(df) == 1
    assert df.iloc[0]["heading"] == "Tema A"
    assert df.iloc[0]["archivo"] == fake_source.archivo

    graph = run_mod.load_graph(paths["graph_path"])
    assert fake_source.archivo in graph.nodes


def test_pdf_sin_cambios_pero_sin_chunks_ni_grafo_se_procesa_igual(
    tmp_path: Path, fake_source, monkeypatch
) -> None:
    """Bootstrap: el manifest dice 'sin cambios', pero el parquet/grafo están vacíos."""
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [])  # nada cambió
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    paths = _paths(tmp_path)  # ninguno de los dos índices existe todavía

    run_mod.build_index(**paths)

    assert len(pd.read_parquet(paths["chunks_path"])) == 1
    assert fake_source.archivo in run_mod.load_graph(paths["graph_path"]).nodes


def test_pdf_ya_indexado_y_sin_cambios_no_se_reprocesa(tmp_path: Path, fake_source, monkeypatch) -> None:
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    paths = _paths(tmp_path)

    # Corrida 1: se indexa.
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [fake_source])
    run_mod.build_index(**paths)

    # Corrida 2: nada cambió, ya está en el parquet y en el grafo -> no se debería
    # volver a llamar embed_documents ni merge_source_into_graph.
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [])
    embed_calls = []
    graph_calls = []
    monkeypatch.setattr(run_mod, "embed_documents", lambda texts: embed_calls.append(texts) or [])
    monkeypatch.setattr(
        run_mod, "merge_source_into_graph", lambda graph, markdown, src: graph_calls.append(src)
    )
    run_mod.build_index(**paths)

    assert embed_calls == []
    assert graph_calls == []
    assert len(pd.read_parquet(paths["chunks_path"])) == 1  # sin duplicados


def test_pdf_reprocesado_retracta_su_version_vieja_del_grafo(tmp_path: Path, fake_source, monkeypatch) -> None:
    monkeypatch.setattr(run_mod, "iter_all_pdfs", lambda: [fake_source])
    paths = _paths(tmp_path)

    # Corrida 1: se indexa y queda en el grafo.
    monkeypatch.setattr(run_mod, "ingest_all", lambda manifest_path: [fake_source])
    run_mod.build_index(**paths)
    assert fake_source.archivo in run_mod.load_graph(paths["graph_path"]).nodes

    # Corrida 2: el PDF "cambió" (ingest_all lo devuelve de nuevo) -> retract_source
    # debe llamarse antes de volver a fusionar.
    calls = []
    monkeypatch.setattr(run_mod, "retract_source", lambda graph, archivo: calls.append(archivo))
    monkeypatch.setattr(
        run_mod, "merge_source_into_graph", lambda graph, markdown, src: graph.add_node(src.archivo, nombre=src.archivo, clases={src.archivo})
    )
    run_mod.build_index(**paths)

    assert calls == [fake_source.archivo]
