"""Estructuras de datos compartidas entre indexer/, server/ y eval/.

Ver plan.md §6. Se definen acá para que el shape de un chunk/fragmento sea
el mismo en el índice (GCS), en la respuesta de las tools MCP y en las
filas de Supabase — evita que se desalineen con el tiempo.

TODO (Fase 2): Chunk, Fragmento.
TODO (Fase 3): GraphNode, GraphEdge.
"""
