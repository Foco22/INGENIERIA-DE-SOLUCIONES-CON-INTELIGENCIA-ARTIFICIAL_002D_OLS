"""Orquestacion: recorre las ofertas y corre el grafo sobre cada una.

El grafo vive en graph.py y las tools en tools.py. Aca solo esta el loop y el manejo de errores.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from src.config import PROMPT_VERSION
from src.db import repository
from src.db.database import init_db
from src.graph import build_evaluator_graph
from src.models import CandidateProfile, Evaluation, JobOffer
from src.profile.loader import profile_hash
from src.prompts import EVALUATION_USER_PROMPT

logger = logging.getLogger(__name__)


def new_run_id() -> str:
    """Id de corrida legible: fecha + sufijo corto."""
    return f"{datetime.now():%Y%m%d-%H%M}-{uuid.uuid4().hex[:4]}"


def evaluate_offer(graph, job: JobOffer, run_id: str) -> Evaluation | None:
    """Evalua UNA oferta. Devuelve la evaluacion guardada, o None si el agente no la guardo."""
    final_state = graph.invoke(
        {
            "messages": [("user", EVALUATION_USER_PROMPT.format(job_block=job.to_prompt_block()))],
            "job": job,          # las tools lo leen con InjectedState
            "run_id": run_id,
            "draft": None,
            "saved": False,
        },
        {"recursion_limit": 10},  # evaluar + guardar; de sobra
    )
    return final_state["draft"] if final_state.get("saved") else None


def evaluate_offers(
    jobs: list[JobOffer],
    profile: CandidateProfile,
    run_id: str | None = None,
) -> tuple[list[Evaluation], list[str]]:
    """Recorre las ofertas, una por una. Un fallo no bota la corrida."""
    init_db()
    run_id = run_id or new_run_id()
    repository.start_run(run_id, profile_hash(profile), PROMPT_VERSION)

    graph = build_evaluator_graph(profile)  # una vez, sirve para todas las ofertas
    evaluations: list[Evaluation] = []
    errors: list[str] = []

    for job in jobs:
        if repository.is_evaluated(job.id, run_id):
            logger.info("Ya evaluada en esta corrida, se salta: %s", job.title)
            continue
        try:
            evaluation = evaluate_offer(graph, job, run_id)
        except Exception as exc:
            logger.warning("Fallo evaluando '%s': %s", job.title, exc)
            repository.set_job_status(job.id, "error")
            errors.append(f"{job.title}: {exc}")
            continue

        if evaluation is None:
            # Evaluo pero no guardo, o no llamo ninguna tool: la oferta queda pendiente.
            logger.warning("El agente no guardo la evaluacion de '%s'", job.title)
            errors.append(f"{job.title}: el agente no llamo save_evaluation")
            continue

        logger.info("%s -> %d (%s)", job.title, evaluation.score, evaluation.band)
        evaluations.append(evaluation)

    repository.finish_run(run_id, len(evaluations))
    return evaluations, errors
