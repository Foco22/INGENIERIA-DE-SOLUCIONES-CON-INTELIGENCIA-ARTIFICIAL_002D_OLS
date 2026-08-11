"""Wrapper de embeddings (BAAI/bge-m3, local, gratis) y del reranker (bge-reranker-base).

Usado por indexer/chunk.py (indexación, ver plan.md §4.1) y por
server/retrieval.py (embedding de la query en tiempo real, ver plan.md §4.2).
Mismo modelo en ambos lados para no desalinear el espacio vectorial.

TODO (Fase 2): función de embedding para indexación.
TODO (Fase 4): función de rerank para retrieval en el server.
"""
