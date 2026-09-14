"""Las dos tools del agente: evaluar y guardar.

Dos funciones a secas. `job` y `run_id` no son argumentos del modelo: las tools los leen del
state con InjectedState, y devuelven un Command para escribir de vuelta en el.
"""

from __future__ import annotations

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.config import PROMPT_VERSION, band_for, settings
from src.db import repository
from src.models import Evaluation


@tool
def evaluate_offer(
    score: int,
    review: str,
    strengths: list[str],
    gaps: list[str],
    deal_breaker: str | None = None,
    *,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Registra tu evaluacion de esta oferta. Es el primer paso, antes de guardar.

    Args:
        score: que tanto le calza la oferta al candidato, de 1 a 10.
        review: por que ese score, en espanol, entre 3 y 5 lineas.
        strengths: lista corta de lo que calza, con evidencia de la oferta y del CV.
        gaps: lista corta de lo que le falta al candidato para esta oferta.
        deal_breaker: el deal breaker que la descarta, o null si no hay ninguno.
    """
    if not 1 <= score <= 10:
        return _reply(tool_call_id, f"Score invalido: {score}. Tiene que ser de 1 a 10. Corrigelo.")

    job = state["job"]
    unsupported = _unsupported_modality_claim(deal_breaker, job.description)
    if unsupported:
        return _reply(tool_call_id, unsupported)

    band = band_for(score)  # la banda la decide el codigo, no el modelo
    evaluation = Evaluation(
        job_id=state["job"].id,
        run_id=state["run_id"],
        score=score,
        band=band,
        review=review,
        strengths=strengths,
        gaps=gaps,
        deal_breaker=deal_breaker,
        model=settings.openai_model,
        prompt_version=PROMPT_VERSION,
    )
    return _reply(
        tool_call_id,
        f"Evaluacion registrada: {score}/10 ({band}). "
        "Todavia no esta guardada: llama save_evaluation ahora.",
        draft=evaluation,
    )


@tool
def save_evaluation(
    *,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Guarda en la base de datos la evaluacion que registraste. Es el ultimo paso."""
    evaluation = state.get("draft")
    if evaluation is None:
        return _reply(tool_call_id, "No hay nada que guardar: primero llama evaluate_offer.")

    repository.save_evaluation(evaluation)
    return _reply(
        tool_call_id,
        f"Guardada en la base de datos: {evaluation.score}/10 ({evaluation.band}).",
        saved=True,
    )


def _reply(tool_call_id: str, text: str, **state_updates) -> Command:
    """Responde al modelo y, de paso, actualiza el state del grafo."""
    return Command(
        update={"messages": [ToolMessage(text, tool_call_id=tool_call_id)], **state_updates}
    )


# El campo is_remote de JobSpy vale False cuando el portal no marca la oferta como remota, que es
# casi siempre: los avisos chilenos rara vez declaran modalidad. El modelo tiende a leer eso como
# "100% presencial" e inventar un deal breaker. Prohibirlo en el prompt no alcanzo (15 de 18 casos
# igual lo inventaron), asi que se verifica contra el texto del aviso.
MODALITY_WORDS = ("presencial", "on-site", "on site", "onsite", "en oficina")


def _unsupported_modality_claim(deal_breaker: str | None, description: str | None) -> str | None:
    """Devuelve el reclamo al modelo si dice 'presencial' y el aviso no lo dice; None si esta ok."""
    if not deal_breaker or not any(w in deal_breaker.lower() for w in MODALITY_WORDS):
        return None
    if any(w in (description or "").lower() for w in MODALITY_WORDS):
        return None
    return (
        "Rechazado: pusiste un deal breaker de modalidad, pero el aviso no dice en ninguna parte "
        "que sea presencial. Que el portal no la marque como remota no significa nada. "
        "Vuelve a llamar evaluate_offer con deal_breaker en null y el score que corresponda "
        "por el calce real, sin castigar la modalidad."
    )


TOOLS = [evaluate_offer, save_evaluation]
