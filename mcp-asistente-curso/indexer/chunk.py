"""Markdown -> chunks. Ver plan.md §4.1, paso 3.

Cada chunk = una sección del markdown (todo lo que cae bajo un heading, de
cualquier nivel, hasta el siguiente). No se intenta anidar por nivel de
heading (#/##/###) porque en los PDFs reales del curso no es jerárquico de
verdad — son slides convertidos con OCR, y el nivel de heading detectado
depende del tamaño de fuente del título, no de una estructura lógica. La
jerarquía real (Experiencia -> Clase) ya viene de PdfSource, no hace falta
sacarla del markdown.

Umbrales calibrados sobre el corpus real (27 PDFs, 394 secciones):
mediana 371 caracteres, p75 729, máximo observado 8658.
"""

from __future__ import annotations

import re

from utils.models import Chunk
from utils.paths import PdfSource

_HEADING_LINE_RE = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)

_MIN_CHARS = 40  # secciones más cortas que esto se funden con la siguiente
_MAX_CHARS = 2000  # secciones más largas que esto se dividen por párrafo


def _split_by_heading(markdown: str) -> list[tuple[str, str]]:
    """[(heading, contenido), ...]. El contenido antes del primer heading se
    descarta (suele ser portada/metadata sin valor de búsqueda, ver ejemplo
    real en Clase 1.1.md: nombre del docente, semestre, etc.)."""
    matches = list(_HEADING_LINE_RE.finditer(markdown))
    sections = []
    for i, m in enumerate(matches):
        heading = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
        content = markdown[start:end].strip()
        sections.append((heading, content))
    return sections


def _merge_small(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Funde secciones muy cortas (heading casi sin contenido) con la siguiente,
    concatenando también el heading para no perder ese contexto."""
    merged: list[tuple[str, str]] = []
    pending_heading: str | None = None
    pending_content = ""
    for heading, content in sections:
        if pending_heading is not None:
            heading = f"{pending_heading} / {heading}"
            content = f"{pending_content}\n\n{content}".strip()
        if len(content) < _MIN_CHARS:
            pending_heading, pending_content = heading, content
            continue
        pending_heading, pending_content = None, ""
        merged.append((heading, content))
    if pending_heading is not None:
        merged.append((pending_heading, pending_content))
    return merged


def _split_large(heading: str, content: str) -> list[tuple[str, str]]:
    """Si una sección supera _MAX_CHARS, la parte por párrafo (no a mitad de
    párrafo — si un solo párrafo ya supera el máximo, queda como un chunk grande)."""
    if len(content) <= _MAX_CHARS:
        return [(heading, content)]

    paragraphs = content.split("\n\n")
    parts: list[str] = []
    buffer = ""
    for p in paragraphs:
        if buffer and len(buffer) + len(p) > _MAX_CHARS:
            parts.append(buffer.strip())
            buffer = ""
        buffer = f"{buffer}\n\n{p}".strip()
    if buffer:
        parts.append(buffer.strip())

    if len(parts) == 1:
        return [(heading, parts[0])]
    return [(f"{heading} (parte {i + 1}/{len(parts)})", c) for i, c in enumerate(parts)]


def chunk_markdown(markdown: str, source: PdfSource) -> list[Chunk]:
    """Convierte el markdown de un PdfSource en su lista de Chunk."""
    sections = _merge_small(_split_by_heading(markdown))

    chunks: list[Chunk] = []
    for heading, content in sections:
        for sub_heading, sub_content in _split_large(heading, content):
            if not sub_content:
                continue
            chunks.append(
                Chunk(
                    texto=sub_content,
                    heading=sub_heading,
                    experiencia=source.experiencia,
                    clase=source.clase,
                    tipo=source.tipo,
                    archivo=source.archivo,
                    indice=len(chunks),
                )
            )
    return chunks
