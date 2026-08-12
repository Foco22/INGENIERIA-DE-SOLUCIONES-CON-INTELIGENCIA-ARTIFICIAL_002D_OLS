"""Tests de server/retrieval.py: búsqueda híbrida (vector + grafo). Ver plan.md §4.2.

embed_query va simulado (monkeypatch) — no llama a la API de OpenAI, así que
corre en milisegundos. _index y _load_graph también van simulados con datos
sintéticos, en vez de leer data/chunks.parquet y data/graph.json reales.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
import pytest

import server.retrieval as retrieval_mod


def _index_de(rows: list[dict]) -> tuple[pd.DataFrame, np.ndarray]:
    df = pd.DataFrame(rows)
    matrix = np.array(df["embedding"].tolist(), dtype=np.float32) if rows else np.empty((0, 0), dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return df, (matrix / norms if rows else matrix)


@pytest.fixture(autouse=True)
def _sin_index_real(monkeypatch):
    """Por default, ningún test toca el parquet/grafo real ni los modelos."""
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de([]))
    monkeypatch.setattr(retrieval_mod, "_load_graph", lambda: nx.DiGraph())
    monkeypatch.setattr(retrieval_mod, "_archivo_a_clase", lambda: {})
    monkeypatch.setattr(retrieval_mod, "embed_query", lambda q: [1.0, 0.0])


def _fila(archivo: str, tipo: str = "clase", experiencia: str = "Experiencia de Aprendizaje 1", clase: str | None = "Clase 1.1", embedding=(1.0, 0.0)) -> dict:
    return {"texto": f"texto de {archivo}", "experiencia": experiencia, "clase": clase, "tipo": tipo, "archivo": archivo, "embedding": list(embedding)}


# --- (a) vectorial ---------------------------------------------------------


def test_vectorial_filtra_por_tipo(monkeypatch) -> None:
    rows = [_fila("clase.pdf", tipo="clase"), _fila("prueba.pdf", tipo="evaluacion", clase=None)]
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de(rows))

    fragmentos, _ = retrieval_mod.buscar("q", tipo="clase")

    assert [f.archivo for f in fragmentos] == ["clase.pdf"]


def test_vectorial_filtra_por_experiencia_y_clase(monkeypatch) -> None:
    rows = [
        _fila("a.pdf", experiencia="Experiencia de Aprendizaje 1", clase="Clase 1.1"),
        _fila("b.pdf", experiencia="Experiencia de Aprendizaje 1", clase="Clase 1.2"),
        _fila("c.pdf", experiencia="Experiencia de Aprendizaje 2", clase="Clase 2.1"),
    ]
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de(rows))

    fragmentos, _ = retrieval_mod.buscar("q", tipo="clase", experiencia="Experiencia de Aprendizaje 1", clase="Clase 1.2")

    assert [f.archivo for f in fragmentos] == ["b.pdf"]


def test_vectorial_ordena_por_similitud_de_coseno_descendente(monkeypatch) -> None:
    rows = [_fila("lejano.pdf", embedding=(0.1, 0.9)), _fila("cercano.pdf", embedding=(0.99, 0.1))]
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de(rows))
    monkeypatch.setattr(retrieval_mod, "embed_query", lambda q: [1.0, 0.0])

    fragmentos, _ = retrieval_mod.buscar("q", tipo="clase")

    assert [f.archivo for f in fragmentos] == ["cercano.pdf", "lejano.pdf"]
    assert fragmentos[0].score > fragmentos[1].score


def test_vectorial_respeta_tope_de_fragmentos_finales(monkeypatch) -> None:
    rows = [_fila(f"{i}.pdf") for i in range(retrieval_mod._TOP_N + 3)]
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de(rows))

    fragmentos, _ = retrieval_mod.buscar("q", tipo="clase")

    assert len(fragmentos) == retrieval_mod._TOP_N


def test_vectorial_sin_chunks_del_tipo_no_llama_a_embed_query(monkeypatch) -> None:
    rows = [_fila("prueba.pdf", tipo="evaluacion", clase=None)]
    monkeypatch.setattr(retrieval_mod, "_index", lambda: _index_de(rows))
    llamadas = []
    monkeypatch.setattr(retrieval_mod, "embed_query", lambda q: llamadas.append(q) or [1.0, 0.0])

    fragmentos, _ = retrieval_mod.buscar("q", tipo="clase")

    assert fragmentos == []
    assert llamadas == []


# --- (b) grafo ---------------------------------------------------------


def _grafo_rag_embeddings() -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_node("rag", nombre="RAG", clases={"a.pdf"})
    graph.add_node("embeddings", nombre="Embeddings", clases={"a.pdf"})
    graph.add_edge("rag", "embeddings", tipo="usa", fuentes={"a.pdf"})
    return graph


def test_grafo_detecta_concepto_mencionado_y_devuelve_su_vecino(monkeypatch) -> None:
    monkeypatch.setattr(retrieval_mod, "_load_graph", _grafo_rag_embeddings)
    monkeypatch.setattr(retrieval_mod, "_archivo_a_clase", lambda: {"a.pdf": "Clase 1.1"})

    _, conceptos = retrieval_mod.buscar("¿qué es RAG?", tipo="clase")

    assert len(conceptos) == 1
    assert conceptos[0].nodo == "RAG"
    assert conceptos[0].concepto_relacionado == "Embeddings"
    assert conceptos[0].tipo_relacion == "usa"
    assert conceptos[0].clase_donde_aparece == "Clase 1.1"


def test_grafo_matchea_tambien_por_vecinos_entrantes(monkeypatch) -> None:
    # La query menciona "Embeddings" (destino de la arista), no "RAG" (origen)
    # -> igual debe encontrar la relación, recorriendo predecessors.
    monkeypatch.setattr(retrieval_mod, "_load_graph", _grafo_rag_embeddings)
    monkeypatch.setattr(retrieval_mod, "_archivo_a_clase", lambda: {"a.pdf": "Clase 1.1"})

    _, conceptos = retrieval_mod.buscar("explícame los embeddings", tipo="clase")

    assert len(conceptos) == 1
    assert conceptos[0].nodo == "Embeddings"
    assert conceptos[0].concepto_relacionado == "RAG"


def test_grafo_no_matchea_concepto_no_mencionado(monkeypatch) -> None:
    monkeypatch.setattr(retrieval_mod, "_load_graph", _grafo_rag_embeddings)

    _, conceptos = retrieval_mod.buscar("¿cómo configuro Docker?", tipo="clase")

    assert conceptos == []


def test_grafo_vacio_no_explota(monkeypatch) -> None:
    monkeypatch.setattr(retrieval_mod, "_load_graph", lambda: nx.DiGraph())

    _, conceptos = retrieval_mod.buscar("¿qué es RAG?", tipo="clase")

    assert conceptos == []


def test_grafo_clase_donde_aparece_junta_varias_fuentes(monkeypatch) -> None:
    graph = nx.DiGraph()
    graph.add_node("rag", nombre="RAG", clases={"a.pdf", "b.pdf"})
    graph.add_node("embeddings", nombre="Embeddings", clases={"a.pdf", "b.pdf"})
    graph.add_edge("rag", "embeddings", tipo="usa", fuentes={"a.pdf", "b.pdf"})
    monkeypatch.setattr(retrieval_mod, "_load_graph", lambda: graph)
    monkeypatch.setattr(retrieval_mod, "_archivo_a_clase", lambda: {"a.pdf": "Clase 1.1", "b.pdf": "Clase 1.2"})

    _, conceptos = retrieval_mod.buscar("¿qué es RAG?", tipo="clase")

    assert conceptos[0].clase_donde_aparece == "Clase 1.1, Clase 1.2"