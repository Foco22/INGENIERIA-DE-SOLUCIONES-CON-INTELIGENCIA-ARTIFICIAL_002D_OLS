"""Wrapper del cliente LLM (Groq, gratis) usado para tareas offline.

Usado por indexer/graph.py (extracción de entidades/relaciones, plan.md §4.1)
y por eval/judge.py (LLM-as-judge, plan.md §4.5). Nunca se llama en tiempo
de consulta de un estudiante — solo en el pipeline de indexación (CI) y en
el chequeo de calidad programado (cron).

TODO (Fase 3): función de extracción de grafo.
TODO (Fase 8): función de evaluación (judge).
"""
