"""Wrapper del cliente LLM (DeepSeek) usado para tareas offline.

Usado por indexer/graph.py (extracción de entidades/relaciones, plan.md §4.1)
y por eval/judge.py (LLM-as-judge, plan.md §4.5). Nunca se llama en tiempo
de consulta de un estudiante — solo en el pipeline de indexación (CI) y en
el chequeo de calidad programado (cron).

DeepSeek expone una API compatible con el SDK de OpenAI (solo cambia
base_url), así que reusamos el cliente `openai` en vez de un SDK propio.
Es pago por token (no hay tier gratis como Groq), pero muy barato — el
corpus completo del curso cuesta fracciones de centavo. Sin el tope de
100K tokens/día que forzaba el bootstrap a correr en varias tandas.

Requiere DEEPSEEK_API_KEY en el entorno (o en un .env local, vía python-dotenv).
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

from utils.models import GraphEdge, GraphNode

load_dotenv()

_MODEL = "deepseek-chat"
_BASE_URL = "https://api.deepseek.com"

# Margen generoso: el PDF más largo del corpus real convierte a ~24K caracteres
# de markdown; esto solo actúa como tope de seguridad, no se espera que se use.
_MAX_INPUT_CHARS = 60_000

_EXTRACTION_SYSTEM_PROMPT = """Eres un asistente que extrae conceptos técnicos y sus relaciones de material educativo sobre Inteligencia Artificial, para construir un grafo de conocimiento.

Del contenido de un documento del curso (en markdown, convertido de un PDF), extrae:
1. entidades: conceptos, técnicas, frameworks o herramientas técnicas relevantes que se explican, enseñan o se requiere aplicar (ej. "RAG", "Embeddings", "Transformers", "LangGraph"). NO incluyas nombres propios de personas ni empresas (ej. "OpenAI", "Google", nombres de docentes), ni metadata administrativa del curso (semestre, porcentajes de evaluación, plazos).
2. relaciones: relaciones directas entre esas entidades, con un tipo breve (ej. "usa", "es parte de", "depende de", "es una técnica de").

Devuelve SOLO un JSON con este formato exacto, sin texto adicional:
{"entidades": ["concepto1", "concepto2"], "relaciones": [{"origen": "concepto1", "tipo": "usa", "destino": "concepto2"}]}

Si no hay conceptos técnicos relevantes, devuelve {"entidades": [], "relaciones": []}."""

_JUDGE_SYSTEM_PROMPT = """Eres un evaluador de calidad para un asistente de búsqueda del contenido de un curso.

Te dan la pregunta de un estudiante, los fragmentos de texto que un sistema de búsqueda le devolvió, y opcionalmente la respuesta final que un asistente le dio a partir de esos fragmentos. Evaluá:
1. relevancia: 0.0 a 1.0 — qué tan relevantes son los fragmentos para responder la pregunta.
2. fundamentacion: 0.0 a 1.0, o null si no se te dio una respuesta — qué tan bien fundamentada está la respuesta en esos fragmentos (penalizá si afirma algo que los fragmentos no dicen).

Devuelve SOLO un JSON con este formato exacto, sin texto adicional:
{"relevancia": 0.0, "fundamentacion": 0.0}

Si no hay respuesta para evaluar, "fundamentacion" debe ser null."""


@lru_cache(maxsize=1)
def _client() -> OpenAI:
    # timeout explícito: sin esto, una llamada colgada (red, rate limit, etc.)
    # puede bloquear el pipeline de indexación indefinidamente.
    return OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=_BASE_URL,
        timeout=30.0,
        max_retries=2,
    )


def extract_graph(markdown: str) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Extrae entidades y relaciones técnicas de un documento. Ver plan.md §4.1, paso 5.

    Corre sobre el markdown completo del PDF (no chunk por chunk): le da al LLM
    contexto completo para identificar relaciones reales entre conceptos, y son
    muchas menos llamadas (una por PDF, no una por chunk).
    """
    response = _client().chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": markdown[:_MAX_INPUT_CHARS]},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    nodes = [GraphNode(nombre=n) for n in data.get("entidades", []) if n and n.strip()]
    edges = [
        GraphEdge(origen=r["origen"], tipo=r["tipo"], destino=r["destino"])
        for r in data.get("relaciones", [])
        if r.get("origen") and r.get("destino")
    ]
    return nodes, edges


def evaluar_interaccion(
    query: str, fragmentos_texto: list[str], respuesta: str | None
) -> tuple[float, float | None]:
    """LLM-as-judge de una interacción: (relevancia, fundamentacion). Ver plan.md §4.5, eval/judge.py.

    `fundamentacion` viene None si `respuesta` es None (nivel 2 de §4.5 es
    best-effort — no todas las interacciones tienen una respuesta reportada).
    """
    contenido = f"Pregunta del estudiante: {query}\n\nFragmentos devueltos:\n"
    contenido += "\n---\n".join(fragmentos_texto) if fragmentos_texto else "(ninguno)"
    if respuesta:
        contenido += f"\n\nRespuesta que le dio el asistente: {respuesta}"
    else:
        contenido += "\n\n(no hay respuesta reportada todavía — evaluá solo relevancia, fundamentacion debe ser null)"

    response = _client().chat.completions.create(
        model=_MODEL,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": contenido},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    return float(data["relevancia"]), (float(data["fundamentacion"]) if data.get("fundamentacion") is not None else None)
