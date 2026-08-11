"""Búsqueda híbrida (vectorial + grafo) + rerank. Ver plan.md §4.2.

Función compartida por buscar_contenido (tipo="clase") y detalle_pruebas
(tipo="evaluacion", server/pruebas.py) — mismo mecanismo, tipo distinto fijo.

TODO (Fase 4): búsqueda vectorial (utils/embeddings.py) + traversal de grafo
+ rerank + fusión de fragmentos y conceptos_relacionados en la salida.
"""
