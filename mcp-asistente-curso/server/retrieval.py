"""Búsqueda híbrida (vectorial + grafo). Ver plan.md §4.2.

Función compartida por buscar_contenido (tipo="clase") y detalle_pruebas
(tipo="evaluacion", server/pruebas.py) — mismo mecanismo, tipo distinto fijo.

Por cada llamada corren dos búsquedas independientes sobre la misma query:

- (a) Vectorial: embedding de la query (OpenAI, utils/embeddings.py) ->
  similitud coseno contra los chunks ya embebidos (data/chunks.parquet),
  filtrada por tipo/experiencia/clase si se pidió -> top-N por score. Sin
  reranker (se sacó el cross-encoder local — mismo problema de descarga que
  el embedder, ver utils/embeddings.py): el orden final es directo por
  similitud de coseno, no pasa por un segundo modelo.
- (b) Grafo: qué nodos de graph.json aparecen mencionados (por nombre, texto
  plano) en la query -> vecinos directos (entrantes y salientes) de esos
  nodos. Sin LLM en tiempo de consulta: el match es determinístico, texto
  contra texto, con la misma normalización que usa indexer/graph.py para
  fusionar nodos (normalize_concepto) — así "RAG" en la query encuentra el
  nodo "rag" del grafo.

(a) y (b) no compiten en el mismo ranking -- son señales de tipo distinto
(texto vs. relaciones entre conceptos) -- se devuelven como dos listas
separadas para que el modelo del cliente arme su respuesta con ambas.
"""

from __future__ import annotations

import re
from functools import lru_cache

import networkx as nx
import numpy as np
import pandas as pd

from indexer.graph import GRAPH_PATH, load_graph, normalize_concepto
from indexer.run import CHUNKS_PATH
from utils.embeddings import embed_query
from utils.models import ConceptoRelacionado, Fragmento
from utils.paths import iter_all_pdfs

_TOP_N = 5  # fragmentos finales de la búsqueda vectorial (sin reranker, ver utils/embeddings.py)

# Tope de conceptos matcheados en la query (los nombres más largos/específicos
# ganan si hay más de _GRAPH_MAX_CONCEPTOS) y de vecinos por concepto, para
# que una query genérica no arrastre medio grafo.
_GRAPH_MAX_CONCEPTOS = 5
_GRAPH_MAX_VECINOS_POR_CONCEPTO = 8


def buscar(
    query: str, tipo: str, experiencia: str | None = None, clase: str | None = None
) -> tuple[list[Fragmento], list[ConceptoRelacionado]]:
    """Punto de entrada de la búsqueda híbrida. `tipo`: "clase" | "evaluacion"."""
    fragmentos = _buscar_vectorial(query, tipo, experiencia, clase)
    conceptos = _buscar_grafo(query)
    return fragmentos, conceptos


# --- (a) Vectorial ------------------------------------------------------


@lru_cache(maxsize=1)
def _index() -> tuple[pd.DataFrame, np.ndarray]:
    """Chunks indexados + su matriz de embeddings normalizada (para coseno = dot).

    Cacheado en memoria: se recarga una sola vez por proceso, no en cada
    llamada de tool. Igual que utils/embeddings.py hace con los modelos.
    """
    df = pd.read_parquet(CHUNKS_PATH)
    matrix = np.array(df["embedding"].tolist(), dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return df, matrix / norms


def _unitario(vector: list[float]) -> np.ndarray:
    v = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(v)
    return v / norm if norm else v


def _buscar_vectorial(query: str, tipo: str, experiencia: str | None, clase: str | None) -> list[Fragmento]:
    df, matrix = _index()
    if df.empty:  # índice vacío (ej. antes de la primera corrida de indexer/run.py)
        return []

    mask = (df["tipo"] == tipo).to_numpy()
    if experiencia:
        mask &= (df["experiencia"] == experiencia).to_numpy()
    if clase:
        mask &= (df["clase"] == clase).to_numpy()
    if not mask.any():
        return []

    filtrados = df[mask].reset_index(drop=True)
    sims = matrix[mask] @ _unitario(embed_query(query))
    top_n = min(_TOP_N, len(filtrados))
    orden = np.argsort(-sims)[:top_n]

    resultados: list[Fragmento] = []
    for i in orden:
        row = filtrados.iloc[int(i)]
        resultados.append(
            Fragmento(
                texto=row["texto"],
                experiencia=row["experiencia"],
                clase=row["clase"],
                archivo=row["archivo"],
                score=float(sims[i]),
            )
        )
    return resultados


# --- (b) Grafo ------------------------------------------------------------


def _load_graph() -> nx.DiGraph:
    return load_graph(GRAPH_PATH)


@lru_cache(maxsize=1)
def _archivo_a_clase() -> dict[str, str]:
    """PdfSource.archivo -> nombre a mostrar (clase, o experiencia si no hay clase puntual)."""
    return {source.archivo: source.clase or source.experiencia for source in iter_all_pdfs()}


def _representante_clase(fuentes: set[str], archivo_a_clase: dict[str, str]) -> str:
    nombres = sorted({archivo_a_clase.get(f, f) for f in fuentes})
    return ", ".join(nombres)


def _conceptos_mencionados(graph: nx.DiGraph, query: str) -> list[tuple[str, str]]:
    """[(node_id, nombre), ...] de los nodos del grafo mencionados en la query.

    Match determinístico texto-contra-texto (sin LLM, ver docstring del
    módulo): nombre normalizado del nodo como palabra completa dentro de la
    query normalizada. Nodos de una sola letra/símbolo no matchean (evita
    falsos positivos de conceptos casi vacíos).
    """
    query_norm = normalize_concepto(query)
    matches = [
        (node_id, attrs["nombre"])
        for node_id, attrs in graph.nodes(data=True)
        if len(node_id) > 1 and re.search(rf"\b{re.escape(node_id)}\b", query_norm)
    ]
    # Conceptos más largos/específicos primero (ej. "prompt engineering" antes que "prompt").
    matches.sort(key=lambda par: len(par[0]), reverse=True)
    return matches[:_GRAPH_MAX_CONCEPTOS]


def _buscar_grafo(query: str) -> list[ConceptoRelacionado]:
    graph = _load_graph()
    if graph.number_of_nodes() == 0:
        return []

    archivo_a_clase = _archivo_a_clase()
    resultados: list[ConceptoRelacionado] = []
    vistos: set[tuple[str, str, str]] = set()

    for node_id, nombre in _conceptos_mencionados(graph, query):
        vecinos = list(graph.successors(node_id)) + list(graph.predecessors(node_id))
        for vecino_id in vecinos[:_GRAPH_MAX_VECINOS_POR_CONCEPTO]:
            clave = tuple(sorted((node_id, vecino_id))) + (node_id,)
            if clave in vistos:
                continue
            vistos.add(clave)

            if graph.has_edge(node_id, vecino_id):
                attrs = graph[node_id][vecino_id]
            else:
                attrs = graph[vecino_id][node_id]

            resultados.append(
                ConceptoRelacionado(
                    nodo=nombre,
                    tipo_relacion=attrs["tipo"],
                    concepto_relacionado=graph.nodes[vecino_id]["nombre"],
                    clase_donde_aparece=_representante_clase(attrs["fuentes"], archivo_a_clase),
                )
            )
    return resultados