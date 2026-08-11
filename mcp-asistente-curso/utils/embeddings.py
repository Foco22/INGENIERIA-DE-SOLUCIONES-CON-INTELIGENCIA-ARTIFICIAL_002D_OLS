"""Wrapper de embeddings y reranker, ambos locales y gratis. Ver plan.md §4.2.

Usa `fastembed` (ONNX Runtime) en vez de `sentence-transformers` (que requiere
`torch`) — mismo problema que con `docling`: instalar `sentence-transformers`
acá se colgó más de 3 minutos resolviendo dependencias sin ni empezar a
descargar. `fastembed` resuelve en segundos (usa el mismo `onnxruntime` que
ya trae `pymupdf4llm`).

Modelo de embeddings: `intfloat/multilingual-e5-large` (no hay build ONNX de
`BAAI/bge-m3` en fastembed) — mismo orden de tamaño/calidad, 100 idiomas,
1024 dims. Los modelos E5 requieren los prefijos "query: "/"passage: " para
rendir bien — no es opcional, es parte del protocolo de uso del modelo.

Reranker: `BAAI/bge-reranker-base`, tal como estaba definido en el plan —
ese sí está disponible en fastembed.

Usado por indexer/run.py (embeddings, indexación) y server/retrieval.py
(embeddings de la query + rerank, en tiempo real).
"""

from __future__ import annotations

from functools import lru_cache

from fastembed import TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder

_EMBED_MODEL = "intfloat/multilingual-e5-large"
_RERANK_MODEL = "BAAI/bge-reranker-base"


@lru_cache(maxsize=1)
def _embedder() -> TextEmbedding:
    return TextEmbedding(_EMBED_MODEL)


@lru_cache(maxsize=1)
def _reranker() -> TextCrossEncoder:
    return TextCrossEncoder(_RERANK_MODEL)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embeddings para texto que se va a indexar (chunks, §4.1 paso 4)."""
    prefixed = [f"passage: {t}" for t in texts]
    return [vector.tolist() for vector in _embedder().embed(prefixed)]


def embed_query(text: str) -> list[float]:
    """Embedding de una query de búsqueda (§4.2)."""
    return next(iter(_embedder().embed([f"query: {text}"]))).tolist()


def rerank(query: str, documents: list[str]) -> list[float]:
    """Scores de relevancia query-documento — más alto es más relevante (§4.2)."""
    return list(_reranker().rerank(query, documents))
