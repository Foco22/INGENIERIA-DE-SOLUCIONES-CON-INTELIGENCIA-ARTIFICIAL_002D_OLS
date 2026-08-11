"""Definición de la tool MCP `buscar_contenido` y de `reportar_interaccion`.

Cada llamada de consulta inserta en Supabase vía utils/supabase.py y
devuelve `interaccion_id` (plan.md §4.5). `detalle_pruebas` vive en
server/pruebas.py (wrapper delgado sobre retrieval.py).

TODO (Fase 4): buscar_contenido.
TODO (Fase 8): reportar_interaccion + logging a Supabase.
"""