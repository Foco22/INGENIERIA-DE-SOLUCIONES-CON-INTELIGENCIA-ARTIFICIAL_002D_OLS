"""Orquesta el pipeline de indexación completo, en orden. Entrypoint de index.yml (§5.1).

ingest.py -> manifest.py (diff) -> chunk.py -> utils/embeddings.py -> graph.py -> utils/gcs.py

Implementado hasta ahora (Fase 2): ingesta + chunking + embeddings -> data/chunks.parquet,
diff-aware de punta a punta — no solo el `.md` (eso ya lo hacía ingest_all()), también el
chunking y el embedding: los PDFs sin cambios ni siquiera se re-chunkean ni re-embeben, sus
filas del parquet se mantienen tal cual.

TODO (Fase 3): grafo de conocimiento (graph.py) + publicación a GCS (utils/gcs.py).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from indexer.chunk import chunk_markdown
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


def build_index(manifest_path: Path = MANIFEST_PATH, chunks_path: Path = CHUNKS_PATH) -> None:
    """Ingesta + chunking + embeddings, diff-aware. Ver plan.md §4.1, pasos 1-4.

    "Necesita re-chunkear/re-embeber" es la unión de dos cosas: los PDFs que
    ingest_all() acaba de reprocesar (cambiaron) y los que, aunque no cambiaron,
    todavía no tienen ninguna fila en chunks.parquet (primera corrida, o el
    parquet se perdió/no existe) — si no, un chunks.parquet vacío nunca se
    llenaría para PDFs que ya estaban "al día" según el manifest.
    """
    reprocessed = ingest_all(manifest_path)
    existing = _load_chunks(chunks_path)

    indexed_archivos = set(existing["archivo"]) if not existing.empty else set()
    reprocessed_archivos = {source.archivo for source in reprocessed}
    missing = [s for s in iter_all_pdfs() if s.archivo not in indexed_archivos and s.archivo not in reprocessed_archivos]

    to_embed = list(reprocessed) + missing
    if not to_embed:
        print("Nada que re-chunkear/re-embeber.")
        return
    if missing:
        print(f"+ {len(missing)} PDFs sin cambios pero sin chunks todavía (primera corrida del índice).")

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

    # Reemplaza las filas de los PDFs recién embebidos; conserva intactas las del resto.
    embedded_archivos = {source.archivo for source in to_embed}
    kept = existing[~existing["archivo"].isin(embedded_archivos)] if not existing.empty else existing
    updated = pd.concat([kept, pd.DataFrame(new_rows, columns=_CHUNK_COLUMNS)], ignore_index=True)

    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    updated.to_parquet(chunks_path, index=False)
    print(f"{len(updated)} chunks totales en {chunks_path}")


if __name__ == "__main__":
    build_index()
