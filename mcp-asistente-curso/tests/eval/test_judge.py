"""Tests de eval/judge.py: LLM-as-judge por lotes. Ver plan.md §4.5.

get_pendientes_de_evaluar/update_scores (Supabase) y evaluar_interaccion
(DeepSeek) van simulados — no llaman a nada real, corre en ms.
"""

from __future__ import annotations

import eval.judge as judge_mod


def test_run_evalua_cada_pendiente_y_escribe_los_scores(monkeypatch) -> None:
    pendientes = [
        {"id": "id-1", "query": "¿qué es RAG?", "fragmentos": [{"texto": "RAG es..."}], "respuesta": "RAG es una técnica..."},
        {"id": "id-2", "query": "¿qué es un LLM?", "fragmentos": [{"texto": "Un LLM es..."}], "respuesta": None},
    ]
    monkeypatch.setattr(judge_mod, "get_pendientes_de_evaluar", lambda limit: pendientes)
    monkeypatch.setattr(judge_mod, "evaluar_interaccion", lambda query, fragmentos_texto, respuesta: (0.9, 0.8 if respuesta else None))
    actualizaciones = []
    monkeypatch.setattr(
        judge_mod,
        "update_scores",
        lambda interaccion_id, relevancia_score, fundamentacion_score: actualizaciones.append(
            (interaccion_id, relevancia_score, fundamentacion_score)
        ),
    )

    n = judge_mod.run()

    assert n == 2
    assert actualizaciones == [("id-1", 0.9, 0.8), ("id-2", 0.9, None)]


def test_run_pasa_los_textos_de_los_fragmentos_no_los_dicts_completos(monkeypatch) -> None:
    pendientes = [{"id": "id-1", "query": "q", "fragmentos": [{"texto": "a"}, {"texto": "b"}], "respuesta": None}]
    monkeypatch.setattr(judge_mod, "get_pendientes_de_evaluar", lambda limit: pendientes)
    llamadas = []
    monkeypatch.setattr(
        judge_mod,
        "evaluar_interaccion",
        lambda query, fragmentos_texto, respuesta: llamadas.append(fragmentos_texto) or (0.5, None),
    )
    monkeypatch.setattr(judge_mod, "update_scores", lambda *a, **kw: None)

    judge_mod.run()

    assert llamadas == [["a", "b"]]


def test_run_sin_pendientes_no_llama_a_evaluar(monkeypatch) -> None:
    monkeypatch.setattr(judge_mod, "get_pendientes_de_evaluar", lambda limit: [])
    llamadas = []
    monkeypatch.setattr(judge_mod, "evaluar_interaccion", lambda *a, **kw: llamadas.append(1) or (0.0, None))
    monkeypatch.setattr(judge_mod, "update_scores", lambda *a, **kw: None)

    n = judge_mod.run()

    assert n == 0
    assert llamadas == []


def test_run_respeta_el_limit(monkeypatch) -> None:
    limites = []
    monkeypatch.setattr(judge_mod, "get_pendientes_de_evaluar", lambda limit: limites.append(limit) or [])

    judge_mod.run(limit=10)

    assert limites == [10]
