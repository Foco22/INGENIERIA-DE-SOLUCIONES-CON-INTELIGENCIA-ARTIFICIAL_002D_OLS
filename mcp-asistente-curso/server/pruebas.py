"""Tool MCP `detalle_pruebas`: wrapper delgado sobre retrieval.py con tipo="evaluacion" fijo.

Ver plan.md §4.4. Misma infraestructura de retrieval que buscar_contenido
(server/tools.py), expuesta como tool separada para que el modelo del
cliente la distinga sin tener que recordar un parámetro `tipo`.

TODO (Fase 7): detalle_pruebas.
"""