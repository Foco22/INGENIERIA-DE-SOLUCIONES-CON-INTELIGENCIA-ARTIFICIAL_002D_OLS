"""Tests de server/tools.py: buscar_contenido, detalle_pruebas, reportar_interaccion. Ver plan.md §4.3-4.5.

`buscar()` (retrieval) e `insert_interaccion`/`reportar_respuesta` (Supabase)
van simulados (monkeypatch) — no llaman a OpenAI/Supabase, corre en ms.
"""

from __future__ import annotations

import server.tools as tools_mod
from utils.models import ConceptoRelacionado, Fragmento


def _fake_buscar(fragmentos=None, conceptos=None):
    return lambda query, tipo, experiencia=None, clase=None: (fragmentos or [], conceptos or [])


def test_buscar_contenido_devuelve_interaccion_id_y_resultados(monkeypatch) -> None:
    frag = Fragmento(texto="RAG es...", experiencia="E1", clase="Clase 1.1", archivo="a.pdf", score=0.9)
    concepto = ConceptoRelacionado(nodo="RAG", tipo_relacion="usa", concepto_relacionado="Embeddings", clase_donde_aparece="Clase 1.1")
    monkeypatch.setattr(tools_mod, "buscar", _fake_buscar([frag], [concepto]))
    monkeypatch.setattr(tools_mod, "insert_interaccion", lambda **kwargs: "id-123")

    resultado = tools_mod.buscar_contenido("¿qué es RAG?")

    assert resultado["interaccion_id"] == "id-123"
    assert resultado["fragmentos"] == [
        {"texto": "RAG es...", "experiencia": "E1", "clase": "Clase 1.1", "archivo": "a.pdf", "score": 0.9}
    ]
    assert resultado["conceptos_relacionados"][0]["nodo"] == "RAG"


def test_buscar_contenido_pasa_tipo_clase_fijo_a_buscar(monkeypatch) -> None:
    llamadas = []
    monkeypatch.setattr(
        tools_mod, "buscar", lambda query, tipo, experiencia=None, clase=None: (llamadas.append(tipo) or ([], []))
    )
    monkeypatch.setattr(tools_mod, "insert_interaccion", lambda **kwargs: "id-123")

    tools_mod.buscar_contenido("q", experiencia="Experiencia de Aprendizaje 1", clase="Clase 1.1")

    assert llamadas == ["clase"]


def test_buscar_contenido_loguea_con_los_fragmentos_y_conceptos_correctos(monkeypatch) -> None:
    frag = Fragmento(texto="t", experiencia="E1", clase=None, archivo="a.pdf", score=0.5)
    monkeypatch.setattr(tools_mod, "buscar", _fake_buscar([frag], []))
    inserts = []
    monkeypatch.setattr(
        tools_mod,
        "insert_interaccion",
        lambda **kwargs: inserts.append(kwargs) or "id-123",
    )

    tools_mod.buscar_contenido("q")

    assert inserts[0]["tool"] == "buscar_contenido"
    assert inserts[0]["query"] == "q"
    assert inserts[0]["fragmentos"][0]["archivo"] == "a.pdf"
    assert isinstance(inserts[0]["latencia_ms"], int)


def test_detalle_pruebas_pasa_tipo_evaluacion_fijo(monkeypatch) -> None:
    llamadas = []
    monkeypatch.setattr(
        tools_mod,
        "buscar",
        lambda query, tipo, experiencia=None, clase=None: (llamadas.append(tipo) or ([], [])),
    )
    monkeypatch.setattr(tools_mod, "insert_interaccion", lambda **kwargs: "id-123")

    tools_mod.detalle_pruebas("¿qué entra en la prueba?")

    assert llamadas == ["evaluacion"]


def test_detalle_pruebas_no_expone_conceptos_relacionados_ni_clase(monkeypatch) -> None:
    frag = Fragmento(texto="Pauta...", experiencia="Experiencia de Aprendizaje 1", clase=None, archivo="eval.pdf", score=0.8)
    concepto = ConceptoRelacionado(nodo="RAG", tipo_relacion="usa", concepto_relacionado="Embeddings", clase_donde_aparece="Clase 1.1")
    monkeypatch.setattr(
        tools_mod, "buscar", lambda query, tipo, experiencia=None, clase=None: ([frag], [concepto])
    )
    monkeypatch.setattr(tools_mod, "insert_interaccion", lambda **kwargs: "id-123")

    resultado = tools_mod.detalle_pruebas("¿qué entra en la prueba?")

    assert resultado == {
        "interaccion_id": "id-123",
        "fragmentos": [
            {"texto": "Pauta...", "experiencia": "Experiencia de Aprendizaje 1", "archivo": "eval.pdf", "score": 0.8}
        ],
    }


def test_detalle_pruebas_pasa_none_de_conceptos_al_insertar(monkeypatch) -> None:
    monkeypatch.setattr(tools_mod, "buscar", lambda query, tipo, experiencia=None, clase=None: ([], []))
    inserts = []
    monkeypatch.setattr(
        tools_mod, "insert_interaccion", lambda **kwargs: inserts.append(kwargs) or "id-123"
    )

    tools_mod.detalle_pruebas("q")

    assert inserts[0]["tool"] == "detalle_pruebas"
    assert inserts[0]["conceptos_relacionados"] is None


def test_reportar_interaccion_llama_a_reportar_respuesta(monkeypatch) -> None:
    llamadas = []
    monkeypatch.setattr(
        tools_mod,
        "reportar_respuesta",
        lambda interaccion_id, respuesta, util: llamadas.append((interaccion_id, respuesta, util)),
    )

    resultado = tools_mod.reportar_interaccion("id-123", respuesta="RAG es una técnica...", util=True)

    assert resultado == {"ok": True}
    assert llamadas == [("id-123", "RAG es una técnica...", True)]