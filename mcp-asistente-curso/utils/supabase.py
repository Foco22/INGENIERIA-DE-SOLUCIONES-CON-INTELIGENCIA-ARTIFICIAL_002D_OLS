"""Cliente de Supabase: insert/select/update sobre la tabla `interacciones`.

Usado por server/tools.py (insert al final de cada tool call) y por
eval/judge.py (select + update de scores) — ver plan.md §4.5, eval/schema.sql.

**Desviación del diseño original:** el plan pedía dos keys separadas — una de
solo-insert para el server (Cloud Run, RLS-limitada) y otra de select/update
para eval/judge.py (privilegiada, nunca expuesta a estudiantes). En la
práctica, la `sb_publishable_...` (key nueva de Supabase, equivalente a la
`anon` vieja) no logra insertar en este proyecto pese a una policy de RLS
correcta (probado con curl directo: HTTP 401 sin causa clara) — parece un
problema de la Data API de Supabase con su sistema nuevo de keys, no de esta
app. Mientras se resuelve, las dos funciones de acá usan la misma
`SUPABASE_SERVICE_ROLE_KEY` (bypassa RLS) — el server en Cloud Run queda con
más privilegio del que debería tener sobre esta tabla. Pendiente volver a
separarlas en `SUPABASE_ANON_KEY` (insert) + `SUPABASE_SERVICE_ROLE_KEY`
(select/update) apenas se entienda el problema — ver ESTADO.md.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

_TABLE = "interacciones"


@lru_cache(maxsize=1)
def _client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])


def insert_interaccion(
    tool: str,
    query: str,
    fragmentos: list[dict[str, Any]],
    conceptos_relacionados: list[dict[str, Any]] | None = None,
    latencia_ms: int | None = None,
) -> str:
    """Inserta una fila y devuelve su id — el `interaccion_id` que ve el estudiante (§4.5 nivel 1)."""
    row = {
        "tool": tool,
        "query": query,
        "fragmentos": fragmentos,
        "conceptos_relacionados": conceptos_relacionados,
        "latencia_ms": latencia_ms,
    }
    response = _client().table(_TABLE).insert(row).execute()
    return response.data[0]["id"]


def reportar_respuesta(interaccion_id: str, respuesta: str, util: bool | None) -> None:
    """UPDATE de una fila ya insertada con la respuesta final que vio el estudiante (§4.5 nivel 2, `reportar_interaccion`)."""
    _client().table(_TABLE).update(
        {
            "respuesta": respuesta,
            "util": util,
            "reportado_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", interaccion_id).execute()


def get_pendientes_de_evaluar(limit: int = 50) -> list[dict[str, Any]]:
    """Filas sin evaluar todavía (`evaluado_at is null`) — usado por eval/judge.py."""
    response = (
        _client()
        .table(_TABLE)
        .select("id, query, fragmentos, respuesta")
        .is_("evaluado_at", "null")
        .limit(limit)
        .execute()
    )
    return response.data


def update_scores(
    interaccion_id: str, relevancia_score: float, fundamentacion_score: float | None
) -> None:
    """Escribe los scores del LLM-as-judge y marca la fila como evaluada — usado por eval/judge.py."""
    _client().table(_TABLE).update(
        {
            "relevancia_score": relevancia_score,
            "fundamentacion_score": fundamentacion_score,
            "evaluado_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", interaccion_id).execute()