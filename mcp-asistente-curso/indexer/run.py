"""Orquesta el pipeline de indexación completo, en orden. Entrypoint de index.yml (§5.1).

ingest.py -> manifest.py (diff) -> chunk.py -> utils/embeddings.py -> graph.py -> utils/gcs.py

TODO (Fase 3): implementar la orquestación end-to-end.
"""
