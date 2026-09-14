"""Prueba el grafo completo sin llamar a OpenAI ni gastar tokens.

Usa un perfil temporal y un modelo falso que siempre llama save_evaluation. Asi se ejercita de
verdad el grafo (nodo evaluator -> tools_condition -> ToolNode -> DB), no solo el loop.

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
    """Modelo falso que encadena las dos tools, como haria el agente real.

    Turno 1: evaluate_offer. Turno 2: save_evaluation. Tras guardar el grafo termina solo,
    asi que un tercer turno seria una llamada de mas: si ocurre, el test falla.
    """

    @property
    def _llm_type(self) -> str:
        return "fake-scoring"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "FakeScoringModel":
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        tool_results = [m for m in messages if isinstance(m, ToolMessage)]

        if not tool_results:
            score = 3 + (len(str(messages[-1].content)) % 8)
            call = {
                "name": "evaluate_offer",
                "args": {
                    "score": score,
                    "review": f"Score {score}: modelo falso del smoke test.",
                    "strengths": ["python"],
                    "gaps": ["spark"],
                    "deal_breaker": None,
                },
                "id": "call_evaluate",
            }
        elif len(tool_results) == 1:
            call = {"name": "save_evaluation", "args": {}, "id": "call_save"}
        else:
            raise AssertionError(
                "Turno extra tras guardar: el grafo deberia haber terminado en route_after_tools."
            )

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

    import src.profile.loader as profile_loader

    profile_loader.PROFILE_PATH = profile_path
    profile_loader.CV_PATH = cv_path


def _use_fake_model() -> None:
    """Reemplaza solo el LLM: el grafo, las tools y la DB son los de verdad."""
    import src.graph as graph

    graph.get_llm = lambda: FakeScoringModel()


def _cleanup(job_ids: list[str] | None = None) -> None:
    """Borra lo que escribio el test y devuelve las ofertas a pending.

    Incluye las que quedaron en 'error': si no, un test fallido deja ofertas trancadas.
    """
    from src.db.database import get_connection

    with get_connection() as conn:
        conn.execute(
            "UPDATE jobs SET status = 'pending' WHERE id IN "
            "(SELECT job_id FROM evaluations WHERE run_id = ?)",
            (RUN_ID,),
        )
        if job_ids:
            marks = ",".join("?" * len(job_ids))
            conn.execute(f"UPDATE jobs SET status = 'pending' WHERE id IN ({marks})", job_ids)
        conn.execute("DELETE FROM evaluations WHERE run_id = ?", (RUN_ID,))
        conn.execute("DELETE FROM runs WHERE run_id = ?", (RUN_ID,))


def main() -> int:
    _use_temp_profile()
    _use_fake_model()

    from src.agent import evaluate_offers
    from src.db import repository
    from src.profile.loader import load_profile

    _cleanup()  # por si quedo basura de una corrida anterior

    jobs = repository.get_pending_jobs(limit=5)
    if not jobs:
        print("No hay ofertas pendientes. Corre antes: python main.py ingest --from-csv")
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
    _cleanup([job.id for job in jobs])
    print(f"Pendientes tras limpiar: {len(repository.get_pending_jobs())}")
    print("\nOK" if ok else "\nFALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
