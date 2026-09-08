"""Definición de las tools MCP: buscar_contenido, detalle_pruebas, reportar_interaccion.

Las dos tools de consulta comparten la misma infraestructura de retrieval
(server/retrieval.py, §4.2) y el mismo logging a Supabase (`_insertar`,
utils/supabase.py, §4.5) — la única diferencia entre ellas es qué `tipo`
de contenido queda fijo y qué campos exponen en la salida (ver plan.md §4.3
tabla). No hay dos pipelines ni dos mecanismos de logging separados.
"""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any

from server.retrieval import buscar
from utils.supabase import insert_interaccion, reportar_respuesta


def _insertar(
    tool: str,
    query: str,
    fragmentos: list[dict[str, Any]],
    conceptos_relacionados: list[dict[str, Any]] | None,
    latencia_ms: int,
) -> str:
    """Wrapper delgado sobre insert_interaccion — un solo lugar que arma la fila
    para las dos tools de consulta (buscar_contenido y detalle_pruebas)."""
    return insert_interaccion(
        tool=tool,
        query=query,
        fragmentos=fragmentos,
        conceptos_relacionados=conceptos_relacionados,
        latencia_ms=latencia_ms,
    )


def buscar_contenido(query: str, experiencia: str | None = None, clase: str | None = None) -> dict[str, Any]:
    """Busca contenido de las clases del curso (tipo="clase" fijo). Ver plan.md §4.3.

    `experiencia`/`clase` acotan la búsqueda vectorial a una Experiencia de
    Aprendizaje o clase puntual (ej. "qué vimos en la clase 2.3"); si se
    omiten, busca en todo el corpus de clases.
    """
    t0 = time.monotonic()
    fragmentos, conceptos = buscar(query, tipo="clase", experiencia=experiencia, clase=clase)
    latencia_ms = round((time.monotonic() - t0) * 1000)

    fragmentos_dict = [asdict(f) for f in fragmentos]
    conceptos_dict = [asdict(c) for c in conceptos]
    interaccion_id = _insertar("buscar_contenido", query, fragmentos_dict, conceptos_dict, latencia_ms)

    return {
        "interaccion_id": interaccion_id,
        "fragmentos": fragmentos_dict,
        "conceptos_relacionados": conceptos_dict,
    }


def detalle_pruebas(query: str, experiencia: str | None = None) -> dict[str, Any]:
    """Busca información de pruebas/evaluaciones del curso (tipo="evaluacion" fijo). Ver plan.md §4.3, §4.4.

    Sin `clase`: las evaluaciones aplican a toda una Experiencia de
    Aprendizaje, no a una clase puntual (utils/paths.py: PdfSource.clase es
    None para tipo="evaluacion"). Sin conceptos_relacionados en la salida:
    `buscar()` igual corre la búsqueda en el grafo (server/retrieval.py no la
    condiciona por `tipo`), pero esa señal no aporta acá — el grafo sale de
    conceptos técnicos de las clases, no de la pauta de una evaluación.
    """
    t0 = time.monotonic()
    fragmentos, _conceptos = buscar(query, tipo="evaluacion", experiencia=experiencia)
    latencia_ms = round((time.monotonic() - t0) * 1000)

    fragmentos_dict = [
        {"texto": f.texto, "experiencia": f.experiencia, "archivo": f.archivo, "score": f.score}
        for f in fragmentos
    ]
    interaccion_id = _insertar("detalle_pruebas", query, fragmentos_dict, None, latencia_ms)

    return {"interaccion_id": interaccion_id, "fragmentos": fragmentos_dict}


def reportar_interaccion(interaccion_id: str, respuesta: str, util: bool | None = None) -> dict[str, Any]:
    """Reporta la respuesta final que el cliente le dio al estudiante (§4.5 nivel 2, best-effort).

    Llamala una sola vez por turno, con el `interaccion_id` de la ÚLTIMA tool
    de consulta usada en ese turno (buscar_contenido o detalle_pruebas) — ver
    plan.md §4.3 para el razonamiento de por qué es "la última" y no todas.
    """
    reportar_respuesta(interaccion_id, respuesta=respuesta, util=util)
    return {"ok": True}