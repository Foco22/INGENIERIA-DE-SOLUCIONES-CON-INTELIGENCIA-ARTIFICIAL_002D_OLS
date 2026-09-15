"""Prueba el grafo completo sin llamar a OpenAI ni gastar tokens.

Usa un perfil temporal y un modelo falso que llama save_evaluation con un score fijo. Asi se
ejercita de verdad el grafo (evaluator -> tools_condition -> ToolNode -> DB), no solo el loop.

    python tests/smoke_test.py
"""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

RUN_ID = "smoke-test"

FAKE_PROFILE = {
    "name": "Test",
    "current_title": "Data Scientist",
    "experience": {"total_years": 3.5, "years_by_skill": {"python": 3.5}},
    "industries": ["retail"],
    "leadership": {"has_led": False},
    "education": {"max_level": "bachelor"},
    "languages": {"spanish": "nativo"},
    "preferences": {"work_mode": ["hybrid"], "deal_breakers": ["turnos rotativos"]},
}


class FakeScoringModel(BaseChatModel):
    """Modelo falso: un solo turno, llama save_evaluation con todo.

    Tras guardar el grafo termina solo. Un segundo turno significaria que la tool rechazo
    (no deberia, los datos son validos) o que el grafo no corto: en ambos casos el test falla.
    """

    @property
    def _llm_type(self) -> str:
        return "fake-scoring"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "FakeScoringModel":
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        tool_results = [m for m in messages if isinstance(m, ToolMessage)]
        if tool_results:
            raise AssertionError(
                f"Turno extra: la tool respondio '{tool_results[-1].content}' y el grafo "
                "deberia haber terminado."
            )

        score = 3 + (len(str(messages[-1].content)) % 8)
        call = {
            "name": "save_evaluation",
            "args": {
                "score": score,
                "review": f"Score {score}: modelo falso del smoke test.",
                "strengths": ["python"],
                "gaps": ["spark"],
                "deal_breaker": None,
            },
            "id": "call_save",
        }
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content="", tool_calls=[call]))]
        )


def _use_temp_profile() -> None:
    """Apunta el loader a un perfil temporal: no toca data/."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    profile_path = tmp / "profile.json"
    cv_path = tmp / "cv.md"
    profile_path.write_text(json.dumps(FAKE_PROFILE), encoding="utf-8")
    cv_path.write_text("# CV\nData scientist con 3.5 anios.", encoding="utf-8")

    import src.utils.profile.loader as profile_loader

    profile_loader.PROFILE_PATH = profile_path
    profile_loader.CV_PATH = cv_path


def _use_fake_model() -> None:
    """Reemplaza solo el LLM: el grafo, las tools y la DB son los de verdad."""
    import src.agents.graph as graph

    graph.get_llm = lambda: FakeScoringModel()


def _sample_jobs(n: int = 5) -> tuple[list, dict[str, str]]:
    """Toma n ofertas cualquiera (evaluadas o no) y recuerda su status para restaurarlo."""
    from src.utils.db.database import get_connection
    from src.utils.db.repository import _row_to_offer

    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY date_posted DESC LIMIT ?", (n,)).fetchall()
    return [_row_to_offer(r) for r in rows], {r["id"]: r["status"] for r in rows}


def _cleanup(original_status: dict[str, str] | None = None) -> None:
    """Borra lo que escribio el test y deja cada oferta con el status que tenia."""
    from src.utils.db.database import get_connection

    with get_connection() as conn:
        conn.execute("DELETE FROM evaluations WHERE run_id = ?", (RUN_ID,))
        conn.execute("DELETE FROM runs WHERE run_id = ?", (RUN_ID,))
        for job_id, status in (original_status or {}).items():
            conn.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))


def main() -> int:
    _use_temp_profile()
    _use_fake_model()

    from src.agents.agent import evaluate_offers
    from src.utils.db import repository
    from src.utils.profile.loader import load_profile

    _cleanup()  # por si quedo basura de una corrida anterior

    jobs, original_status = _sample_jobs(5)
    if not jobs:
        print("No hay ofertas en la DB. Corre antes: python main.py ingest --from-csv")
        return 1

    print(f"Ofertas a evaluar: {len(jobs)}")
    evaluations, errors = evaluate_offers(jobs, load_profile(), run_id=RUN_ID)
    print(f"Evaluadas: {len(evaluations)} | errores: {errors}")

    df = repository.get_evaluations_df(RUN_ID)
    expected = ["score", "band_label", "strengths", "gaps", "job_url", "date_posted"]
    missing = [c for c in expected if c not in df.columns]

    print(f"DataFrame de la UI: {len(df)} filas | faltan columnas: {missing or 'ninguna'}")
    print(df[["score", "band_label", "title"]].to_string(index=False))

    ok = len(evaluations) == len(jobs) and not missing and not errors
    _cleanup(original_status)
    print("Status de las ofertas restaurado.")
    print("\nOK" if ok else "\nFALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
