"""Orquesta el pipeline de indexación completo, en orden. Entrypoint de index.yml (§5.1).

ingest.py -> manifest.py (diff) -> chunk.py -> utils/embeddings.py -> graph.py -> utils/gcs.py

Implementado hasta ahora (Fases 2-3): ingesta + chunking + embeddings -> data/chunks.parquet,
y extracción del grafo de conocimiento -> data/graph.json. Diff-aware de punta a punta — un
PDF sin cambios ni se re-chunkea/re-embebe ni se re-extrae su grafo; uno que sí cambió primero
"retracta" su contribución vieja del grafo (indexer.graph.retract_source) antes de fusionar
la nueva, para no dejar entidades/relaciones obsoletas colgando.

TODO (Fase 3, resto): publicación a GCS (utils/gcs.py).
"""

from __future__ import annotations

from pathlib import Path

import groq
import pandas as pd

from indexer.chunk import chunk_markdown
from indexer.graph import GRAPH_PATH, load_graph, merge_source_into_graph, retract_source, save_graph
from indexer.ingest import ingest_all
from indexer.manifest import MANIFEST_PATH
from utils.embeddings import embed_documents
from utils.paths import REPO_ROOT, iter_all_pdfs

CHUNKS_PATH = REPO_ROOT / "mcp-asistente-curso" / "data" / "chunks.parquet"

_CHUNK_COLUMNS = [
    "chunk_id",
    "texto",
    "heading",
    "experiencia",
    "clase",
    "tipo",
    "archivo",
    "indice",
    "embedding",
]


def _load_chunks(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=_CHUNK_COLUMNS)
    return pd.read_parquet(path)


def _archivos_en_grafo(graph) -> set[str]:
    archivos: set[str] = set()
    for _, attrs in graph.nodes(data=True):
        archivos |= attrs["clases"]
    return archivos


def build_index(
    manifest_path: Path = MANIFEST_PATH,
    chunks_path: Path = CHUNKS_PATH,
    graph_path: Path = GRAPH_PATH,
) -> None:
    """Ingesta + chunking + embeddings + grafo, diff-aware. Ver plan.md §4.1, pasos 1-5.

    "Necesita reprocesarse" es la unión de dos cosas, tanto para el parquet como
    para el grafo: los PDFs que ingest_all() acaba de reprocesar (cambiaron) y
    los que, aunque no cambiaron, todavía no tienen contenido en el índice
    correspondiente (primera corrida, o ese índice se perdió/no existe) — si
    no, un índice vacío nunca se llenaría para PDFs ya "al día" según el manifest.
    """
    reprocessed = ingest_all(manifest_path)
    reprocessed_archivos = {source.archivo for source in reprocessed}
    all_sources = iter_all_pdfs()

    existing_chunks = _load_chunks(chunks_path)
    indexed_archivos = set(existing_chunks["archivo"]) if not existing_chunks.empty else set()
    missing_chunks = [
        s for s in all_sources if s.archivo not in indexed_archivos and s.archivo not in reprocessed_archivos
    ]
    to_embed = list(reprocessed) + missing_chunks

    graph = load_graph(graph_path)
    graphed_archivos = _archivos_en_grafo(graph)
    missing_graph = [
        s for s in all_sources if s.archivo not in graphed_archivos and s.archivo not in reprocessed_archivos
    ]
    to_extract = list(reprocessed) + missing_graph

    if not to_embed and not to_extract:
        print("Nada que reprocesar.")
        return

    # --- Chunks + embeddings (§4.1 pasos 3-4) ---
    if to_embed:
        if missing_chunks:
            print(f"+ {len(missing_chunks)} PDFs sin cambios pero sin chunks todavía (primera corrida).")
        new_rows: list[dict] = []
        for source in to_embed:
            markdown = source.markdown_path.read_text(encoding="utf-8")
            chunks = chunk_markdown(markdown, source)
            if not chunks:
                continue
            embeddings = embed_documents([c.texto for c in chunks])
            for chunk, embedding in zip(chunks, embeddings):
                new_rows.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "texto": chunk.texto,
                        "heading": chunk.heading,
                        "experiencia": chunk.experiencia,
                        "clase": chunk.clase,
                        "tipo": chunk.tipo,
                        "archivo": chunk.archivo,
                        "indice": chunk.indice,
                        "embedding": embedding,
                    }
                )

        embedded_archivos = {source.archivo for source in to_embed}
        kept = existing_chunks[~existing_chunks["archivo"].isin(embedded_archivos)] if not existing_chunks.empty else existing_chunks
        updated_chunks = pd.concat([kept, pd.DataFrame(new_rows, columns=_CHUNK_COLUMNS)], ignore_index=True)
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        updated_chunks.to_parquet(chunks_path, index=False)
        print(f"{len(updated_chunks)} chunks totales en {chunks_path}")

    # --- Grafo de conocimiento (§4.1 paso 5) ---
    if to_extract:
        if missing_graph:
            print(f"+ {len(missing_graph)} PDFs sin cambios pero sin grafo todavía (primera corrida).")
        try:
            for i, source in enumerate(to_extract, start=1):
                print(f"[grafo {i}/{len(to_extract)}] {source.archivo}")
                markdown = source.markdown_path.read_text(encoding="utf-8")
                if source.archivo in reprocessed_archivos:
                    retract_source(graph, source.archivo)  # PDF cambió: saca su versión vieja primero
                merge_source_into_graph(graph, markdown, source)
                save_graph(graph, graph_path)  # guarda tras cada PDF: un error a mitad de camino no pierde lo ya hecho
        except groq.RateLimitError as e:
            print(f"Límite de Groq alcanzado, se detiene acá (progreso guardado): {e}")
            print("Reintentar más tarde retoma solo los PDFs que faltan (diff-aware).")
            return
        print(f"{graph.number_of_nodes()} nodos, {graph.number_of_edges()} aristas en {graph_path}")


if __name__ == "__main__":
    build_index()
