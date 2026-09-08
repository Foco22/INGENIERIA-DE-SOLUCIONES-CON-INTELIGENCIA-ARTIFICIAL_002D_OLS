"""Tests de utils/supabase.py: insert/select/update sobre `interacciones`. Ver plan.md §4.5.

`_client()` va simulado (monkeypatch) con un cliente falso en memoria que
imita la interfaz encadenable de supabase-py (.table().insert().execute(),
etc.) — no llama a Supabase, así que corre en milisegundos.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import utils.supabase as supabase_mod


@dataclass
class _Response:
    data: list[dict[str, Any]]


class _FakeQuery:
    def __init__(self, table: "_FakeTable") -> None:
        self._table = table
        self._op: str | None = None
        self._payload: dict[str, Any] | None = None
        self._filters: dict[str, Any] = {}

    def insert(self, row: dict[str, Any]) -> "_FakeQuery":
        self._op = "insert"
        self._payload = row
        return self

    def update(self, row: dict[str, Any]) -> "_FakeQuery":
        self._op = "update"
        self._payload = row
        return self

    def select(self, *_args: Any) -> "_FakeQuery":
        self._op = "select"
        return self

    def eq(self, col: str, value: Any) -> "_FakeQuery":
        self._filters[col] = ("eq", value)
        return self

    def is_(self, col: str, value: Any) -> "_FakeQuery":
        self._filters[col] = ("is", value)
        return self

    def limit(self, _n: int) -> "_FakeQuery":
        return self

    def execute(self) -> _Response:
        if self._op == "insert":
            row = {**self._payload, "id": str(uuid.uuid4())}
            self._table.rows.append(row)
            return _Response(data=[row])
        if self._op == "update":
            actualizadas = []
            for row in self._table.rows:
                if all(row.get(col) == val for col, (kind, val) in self._filters.items() if kind == "eq"):
                    row.update(self._payload)
                    actualizadas.append(row)
            return _Response(data=actualizadas)
        if self._op == "select":
            filtradas = []
            for row in self._table.rows:
                ok = True
                for col, (kind, val) in self._filters.items():
                    if kind == "is" and val == "null" and row.get(col) is not None:
                        ok = False
                if ok:
                    filtradas.append(row)
            return _Response(data=filtradas)
        raise AssertionError("execute() sin operación seteada")


class _FakeTable:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def query(self) -> _FakeQuery:
        return _FakeQuery(self)


@dataclass
class _FakeClient:
    tables: dict[str, _FakeTable] = field(default_factory=dict)

    def table(self, name: str) -> _FakeQuery:
        return self.tables.setdefault(name, _FakeTable()).query()


def _con_cliente_falso(monkeypatch) -> _FakeClient:
    client = _FakeClient()
    monkeypatch.setattr(supabase_mod, "_client", lambda: client)
    return client


def test_insert_interaccion_devuelve_el_id(monkeypatch) -> None:
    client = _con_cliente_falso(monkeypatch)

    interaccion_id = supabase_mod.insert_interaccion(
        tool="buscar_contenido", query="¿qué es RAG?", fragmentos=[{"archivo": "a.pdf"}]
    )

    assert interaccion_id
    fila = client.tables["interacciones"].rows[0]
    assert fila["id"] == interaccion_id
    assert fila["query"] == "¿qué es RAG?"
    assert fila["tool"] == "buscar_contenido"


def test_reportar_respuesta_actualiza_la_fila_correcta(monkeypatch) -> None:
    client = _con_cliente_falso(monkeypatch)
    interaccion_id = supabase_mod.insert_interaccion(tool="buscar_contenido", query="q", fragmentos=[])

    supabase_mod.reportar_respuesta(interaccion_id, respuesta="RAG es...", util=True)

    fila = client.tables["interacciones"].rows[0]
    assert fila["respuesta"] == "RAG es..."
    assert fila["util"] is True
    assert fila["reportado_at"] is not None


def test_get_pendientes_de_evaluar_solo_trae_las_no_evaluadas(monkeypatch) -> None:
    client = _con_cliente_falso(monkeypatch)
    id_pendiente = supabase_mod.insert_interaccion(tool="buscar_contenido", query="q1", fragmentos=[])
    id_evaluada = supabase_mod.insert_interaccion(tool="buscar_contenido", query="q2", fragmentos=[])
    supabase_mod.update_scores(id_evaluada, relevancia_score=0.9, fundamentacion_score=None)

    pendientes = supabase_mod.get_pendientes_de_evaluar()

    assert [p["id"] for p in pendientes] == [id_pendiente]


def test_update_scores_marca_evaluado_at(monkeypatch) -> None:
    client = _con_cliente_falso(monkeypatch)
    interaccion_id = supabase_mod.insert_interaccion(tool="buscar_contenido", query="q", fragmentos=[])

    supabase_mod.update_scores(interaccion_id, relevancia_score=0.8, fundamentacion_score=0.7)

    fila = client.tables["interacciones"].rows[0]
    assert fila["relevancia_score"] == 0.8
    assert fila["fundamentacion_score"] == 0.7
    assert fila["evaluado_at"] is not None
