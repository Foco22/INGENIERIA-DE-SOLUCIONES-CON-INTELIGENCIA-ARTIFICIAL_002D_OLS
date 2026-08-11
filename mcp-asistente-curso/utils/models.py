"""Estructuras de datos compartidas entre indexer/, server/ y eval/.

Ver plan.md §6. Se definen acá para que el shape de un chunk/fragmento sea
el mismo en el índice (GCS), en la respuesta de las tools MCP y en las
filas de Supabase — evita que se desalineen con el tiempo.

TODO (Fase 3): GraphNode, GraphEdge.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """Un fragmento del contenido de un PDF, listo para embeber (plan.md §4.1, paso 3).

    Un chunk = una sección del markdown (todo lo que cae bajo un heading, de
    cualquier nivel, hasta el siguiente). Los headings del OCR no son
    jerárquicos de verdad (mezclan #/##/###/#### casi al azar según tamaño
    de fuente detectado en el slide) — la jerarquía real Experiencia -> Clase
    viene de la metadata del PDF fuente, no de anidar niveles de heading.
    """

    texto: str
    heading: str  # título de la sección/slide a la que pertenece (para contexto y cita)
    experiencia: str
    clase: str | None  # None para tipo="evaluacion"
    tipo: str  # "clase" | "evaluacion"
    archivo: str  # cita: ruta relativa del PDF fuente
    indice: int  # posición del chunk dentro de su PDF (0-based)

    @property
    def chunk_id(self) -> str:
        """Id determinístico y estable — permite upsert en el índice vectorial.

        Depende solo de (archivo, índice), no del texto: como el diff-aware
        processing (§4.1 paso 2) reprocesa un PDF entero cuando cambia, no
        chunk por chunk, no hace falta que el id cambie si solo cambia el
        texto de un chunk existente.
        """
        return hashlib.sha256(f"{self.archivo}::{self.indice}".encode()).hexdigest()[:16]
