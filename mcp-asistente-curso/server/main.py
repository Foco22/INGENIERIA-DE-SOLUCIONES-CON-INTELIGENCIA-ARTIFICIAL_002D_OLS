"""Entrypoint del servidor MCP (streamable-http).

Declara el Server MCP con sus `instructions` (plan.md §4.3, §4.5 — instruye
al modelo del cliente a llamar reportar_interaccion), registra las tools de
server/tools.py y server/pruebas.py, y expone la app ASGI para Cloud Run
(escuchando en el puerto de la env var PORT).

TODO (Fase 5): server MCP + instructions + auth (server/auth.py) + descarga
del índice al arrancar (utils/gcs.py).
"""
