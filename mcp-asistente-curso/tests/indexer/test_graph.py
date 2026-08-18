"""Tests de la fusión del grafo (indexer/graph.py). Ver plan.md §4.1, paso 5.

`extract_graph` va simulado (monkeypatch) — no llama a DeepSeek, así que corre
en milisegundos y no depende de DEEPSEEK_API_KEY.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

import indexer.graph as graph_mod
from utils.models import GraphEdge, GraphNode
from utils.paths import REPO_ROOT, PdfSource


def _source(nombre: str) -> PdfSource:
    return PdfSource(
        path=REPO_ROOT / "Experiencia de Aprendizaje 1" / "Clase 1.1" / f"{nombre}.pdf",
        tipo="clase",
        experiencia="Experiencia de Aprendizaje 1",
        clase="Clase 1.1",
    )


def _fake_extraction(nodes: list[GraphNode], edges: list[GraphEdge]):
    return lambda markdown: (nodes, edges)


def test_merge_agrega_nodos_y_aristas(monkeypatch) -> None:
    monkeypatch.setattr(
        graph_mod,
        "extract_graph",
        _fake_extraction(
            [GraphNode("RAG"), GraphNode("Embeddings")],
            [GraphEdge("RAG", "usa", "Embeddings")],
        ),
    )
    graph = nx.DiGraph()
    source = _source("a")

    graph_mod.merge_source_into_graph(graph, "markdown", source)

    assert set(graph.nodes) == {"rag", "embeddings"}
    assert graph.has_edge("rag", "embeddings")
    assert graph.nodes["rag"]["clases"] == {source.archivo}


def test_merge_normaliza_nombres_case_insensitive(monkeypatch) -> None:
    graph = nx.DiGraph()
    graph.add_node("rag", nombre="RAG", clases={"otro.pdf"})

    monkeypatch.setattr(graph_mod, "extract_graph", _fake_extraction([GraphNode("rag")], []))
    graph_mod.merge_source_into_graph(graph, "markdown", _source("a"))

    assert len(graph.nodes) == 1  # "rag" y "RAG" son el mismo nodo
    assert graph.nodes["rag"]["clases"] == {"otro.pdf", _source("a").archivo}


def test_dos_fuentes_para_la_misma_entidad_no_se_pierden_al_retractar_una(monkeypatch) -> None:
    graph = nx.DiGraph()
    source_a, source_b = _source("a"), _source("b")

    monkeypatch.setattr(graph_mod, "extract_graph", _fake_extraction([GraphNode("RAG")], []))
    graph_mod.merge_source_into_graph(graph, "md", source_a)
    graph_mod.merge_source_into_graph(graph, "md", source_b)
    assert graph.nodes["rag"]["clases"] == {source_a.archivo, source_b.archivo}

    graph_mod.retract_source(graph, source_a.archivo)

    assert "rag" in graph.nodes  # sigue existiendo, source_b todavía lo menciona
    assert graph.nodes["rag"]["clases"] == {source_b.archivo}


def test_retractar_la_unica_fuente_elimina_el_nodo(monkeypatch) -> None:
    graph = nx.DiGraph()
    source = _source("a")
    monkeypatch.setattr(graph_mod, "extract_graph", _fake_extraction([GraphNode("RAG")], []))
    graph_mod.merge_source_into_graph(graph, "md", source)

    graph_mod.retract_source(graph, source.archivo)

    assert "rag" not in graph.nodes


def test_retractar_elimina_aristas_obsoletas() -> None:
    graph = nx.DiGraph()
    graph.add_node("rag", nombre="RAG", clases={"a.pdf"})
    graph.add_node("embeddings", nombre="Embeddings", clases={"a.pdf"})
    graph.add_edge("rag", "embeddings", tipo="usa", fuentes={"a.pdf"})

    graph_mod.retract_source(graph, "a.pdf")

    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0


def test_save_y_load_roundtrip(tmp_path: Path, monkeypatch) -> None:
    graph = nx.DiGraph()
    monkeypatch.setattr(
        graph_mod,
        "extract_graph",
        _fake_extraction([GraphNode("RAG"), GraphNode("Embeddings")], [GraphEdge("RAG", "usa", "Embeddings")]),
    )
    graph_mod.merge_source_into_graph(graph, "md", _source("a"))

    path = tmp_path / "graph.json"
    graph_mod.save_graph(graph, path)
    loaded = graph_mod.load_graph(path)

    assert set(loaded.nodes) == set(graph.nodes)
    assert set(loaded.edges) == set(graph.edges)
    assert loaded.nodes["rag"]["clases"] == graph.nodes["rag"]["clases"]
    assert loaded["rag"]["embeddings"]["fuentes"] == graph["rag"]["embeddings"]["fuentes"]


def test_load_graph_vacio_si_no_existe(tmp_path: Path) -> None:
    graph = graph_mod.load_graph(tmp_path / "no_existe.json")
    assert graph.number_of_nodes() == 0
