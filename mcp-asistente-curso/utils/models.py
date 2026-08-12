"""Estructuras de datos compartidas entre indexer/, server/ y eval/.

Ver plan.md §6. Se definen acá para que el shape de un chunk/fragmento sea
el mismo en el índice (GCS), en la respuesta de las tools MCP y en las
filas de Supabase — evita que se desalineen con el tiempo.
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


@dataclass(frozen=True)
class GraphNode:
    """Una entidad extraída de un documento, antes de fusionarse en el grafo global.

    Ver plan.md §4.1, paso 5. La fusión (indexer/graph.py) agrupa por nombre
    normalizado, así que "RAG" y "rag" terminan siendo el mismo nodo — acá
    solo se guarda el nombre tal como lo devolvió el LLM.
    """

    nombre: str


@dataclass(frozen=True)
class GraphEdge:
    """Una relación entre dos entidades, extraída de un documento (plan.md §4.1, paso 5)."""

    origen: str
    tipo: str
    destino: str


@dataclass(frozen=True)
class Fragmento:
    """Un resultado de la búsqueda vectorial: un chunk + su score de relevancia.

    Ver plan.md §4.2. Mismo shape para `buscar_contenido` y `detalle_pruebas`
    (server/tools.py, server/pruebas.py) — solo cambia qué `tipo` de chunk
    (clase/evaluacion) alimentó la búsqueda.
    """

    texto: str
    experiencia: str
    clase: str | None  # None para tipo="evaluacion", igual que en Chunk
    archivo: str
    score: float


@dataclass(frozen=True)
class ConceptoRelacionado:
    """Una relación del grafo de conocimiento relevante a una query (plan.md §4.2).

    Sale del traversal de vecinos en graph.json a partir de los conceptos
    detectados en la query — es una señal distinta a los Fragmento (relación
    entre conceptos, no texto), no compite en el mismo ranking.
    """

    nodo: str
    tipo_relacion: str
    concepto_relacionado: str
    clase_donde_aparece: str  # clase(s) donde aparece esta relación, unidas por ", " si son varias
