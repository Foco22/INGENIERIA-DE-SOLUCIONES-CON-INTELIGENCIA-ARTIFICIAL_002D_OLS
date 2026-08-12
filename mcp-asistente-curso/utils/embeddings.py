"""Wrapper de embeddings (OpenAI, API). Ver plan.md §4.2.

Antes corría 100% local con `fastembed` (ONNX): sin costo por query, pero el
modelo (multilingual-e5-large, >1GB) se descarga a un caché efímero (`/tmp`
en este entorno) — cada vez que ese caché se pierde (reboot, contenedor
nuevo en Cloud Run), la primera query paga varios minutos de descarga antes
de poder responder. Para un servidor que debe responder rápido a preguntas
de estudiantes, ese costo de arranque no es aceptable. Se migró a la API de
OpenAI (`text-embedding-ada-002`): sin modelo que descargar/cargar, latencia
de red típica en vez de descarga de ~1GB, costo por token insignificante
para el volumen de este curso.

**Importante:** el mismo modelo se usa para indexar (`embed_documents`,
indexer/run.py) y para embeber la query en tiempo real (`embed_query`,
server/retrieval.py) — si cambia el modelo, hay que re-embeber todo
`data/chunks.parquet` desde cero, los vectores de otro modelo no son
comparables entre sí (ni siquiera tienen las mismas dimensiones).

No hay reranker: se sacó el cross-encoder local (`bge-reranker-base`, mismo
problema de descarga que el embedder) — los fragmentos finales quedan
ordenados solo por similitud de coseno contra el embedding de la query
(server/retrieval.py). Menos preciso que con rerank, pero sin modelos
locales que mantener.

Requiere OPENAI_API_KEY en el entorno (o en un .env local, vía python-dotenv).
"""

from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_MODEL = "text-embedding-ada-002"


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    return OpenAI(timeout=30.0, max_retries=2)  # usa OPENAI_API_KEY del entorno


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embeddings para texto que se va a indexar (chunks, §4.1 paso 4)."""
    if not texts:
        return []
    response = _client().embeddings.create(model=_MODEL, input=texts)
    return [item.embedding for item in response.data]


def embed_query(text: str) -> list[float]:
    """Embedding de una query de búsqueda (§4.2)."""
    return _client().embeddings.create(model=_MODEL, input=[text]).data[0].embedding
