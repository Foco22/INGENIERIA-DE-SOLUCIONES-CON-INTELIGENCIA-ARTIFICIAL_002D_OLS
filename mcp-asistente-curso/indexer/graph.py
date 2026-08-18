"""Markdown -> entidades/relaciones (extracción con LLM), merge en graph.json. Ver plan.md §4.1, paso 5.

El grafo es un `networkx.DiGraph`. Cada nodo y cada arista guardan de qué
PDF(s) vinieron (`clases`/`fuentes`, un set de `PdfSource.archivo`) — así
una entidad mencionada en varias clases queda como un solo nodo, no
duplicado, y el diff-aware processing puede "retractar" limpiamente la
contribución de un PDF que cambió antes de fusionar su versión nueva (sin
esto, un PDF editado dejaría nodos/aristas viejos y obsoletos colgando).

La fusión es por nombre normalizado (minúsculas, espacios colapsados) para
que "RAG" y "rag" no generen dos nodos.
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from utils.llm import extract_graph
from utils.paths import REPO_ROOT, PdfSource

GRAPH_PATH = REPO_ROOT / "mcp-asistente-curso" / "data" / "graph.json"


def normalize_concepto(nombre: str) -> str:
    """Minúsculas + espacios colapsados — misma clave usada como id de nodo.

    Pública porque server/retrieval.py (§4.2) la reusa para detectar, con la
    misma regla, qué conceptos del grafo aparecen mencionados en una query.
    """
    return " ".join(nombre.strip().lower().split())


def load_graph(path: Path = GRAPH_PATH) -> nx.DiGraph:
    """Carga el grafo previo desde disco. Vacío si no existe (primera corrida)."""
    if not path.exists():
        return nx.DiGraph()
    data = json.loads(path.read_text(encoding="utf-8"))
    graph = nx.DiGraph()
    for node in data["nodes"]:
        graph.add_node(node["id"], nombre=node["nombre"], clases=set(node["clases"]))
    for edge in data["edges"]:
        graph.add_edge(edge["origen"], edge["destino"], tipo=edge["tipo"], fuentes=set(edge["fuentes"]))
    return graph


def save_graph(graph: nx.DiGraph, path: Path = GRAPH_PATH) -> None:
    data = {
        "nodes": [
            {"id": node_id, "nombre": attrs["nombre"], "clases": sorted(attrs["clases"])}
            for node_id, attrs in graph.nodes(data=True)
        ],
        "edges": [
            {"origen": u, "destino": v, "tipo": attrs["tipo"], "fuentes": sorted(attrs["fuentes"])}
            for u, v, attrs in graph.edges(data=True)
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def retract_source(graph: nx.DiGraph, archivo: str) -> None:
    """Quita del grafo la contribución de `archivo` (in-place).

    Un nodo/arista que solo existía por ese PDF se elimina; uno que también
    viene de otras fuentes se mantiene, solo pierde esa referencia. Se llama
    antes de re-fusionar un PDF que cambió, para no dejar entidades/relaciones
    obsoletas de su versión anterior.
    """
    for _, _, attrs in graph.edges(data=True):
        attrs["fuentes"].discard(archivo)
    stale_edges = [(u, v) for u, v, attrs in graph.edges(data=True) if not attrs["fuentes"]]
    graph.remove_edges_from(stale_edges)

    for _, attrs in graph.nodes(data=True):
        attrs["clases"].discard(archivo)
    stale_nodes = [n for n, attrs in graph.nodes(data=True) if not attrs["clases"]]
    graph.remove_nodes_from(stale_nodes)  # también elimina cualquier arista que quedara colgando


def merge_source_into_graph(graph: nx.DiGraph, markdown: str, source: PdfSource) -> None:
    """Extrae entidades/relaciones de un documento y las fusiona en `graph` (in-place).

    Llamar `retract_source(graph, source.archivo)` antes si `source` ya tenía
    una contribución previa (reprocesamiento de un PDF modificado).
    """
    nodes, edges = extract_graph(markdown)

    def _ensure_node(nombre: str) -> str:
        key = normalize_concepto(nombre)
        if graph.has_node(key):
            graph.nodes[key]["clases"].add(source.archivo)
        else:
            graph.add_node(key, nombre=nombre, clases={source.archivo})
        return key

    for node in nodes:
        if normalize_concepto(node.nombre):
            _ensure_node(node.nombre)

    for edge in edges:
        origen_key, destino_key = normalize_concepto(edge.origen), normalize_concepto(edge.destino)
        if not origen_key or not destino_key:
            continue
        _ensure_node(edge.origen)
        _ensure_node(edge.destino)
        if graph.has_edge(origen_key, destino_key):
            graph[origen_key][destino_key]["fuentes"].add(source.archivo)
            graph[origen_key][destino_key]["tipo"] = edge.tipo  # última fuente gana el "tipo"
        else:
            graph.add_edge(origen_key, destino_key, tipo=edge.tipo, fuentes={source.archivo})
