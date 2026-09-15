"""La tool del agente: entregar y guardar la evaluacion.

La tool NO evalua: el score y el review los genera el LLM al llenar los argumentos (eso pasa en
graph.py, dentro de llm.invoke). La tool es el formulario que obliga a estructurar la respuesta,
la aduana que la valida, y el paso que la guarda. `job` y `run_id` no son argumentos del modelo:
se leen del state con InjectedState.
"""

from __future__ import annotations

import re
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.utils.config import PROMPT_VERSION, band_for, settings
from src.utils.db import repository
from src.utils.models import Evaluation


@tool
def save_evaluation(
    score: int,
    review: str,
    strengths: list[str],
    gaps: list[str],
    deal_breaker: str | None = None,
    *,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Entrega y guarda tu evaluacion de esta oferta. Llamala una sola vez, cuando ya decidiste.

    Args:
        score: que tanto le calza la oferta al candidato, de 1 a 10.
        review: por que ese score, en espanol, entre 3 y 5 lineas.
        strengths: lista corta de lo que calza, con evidencia de la oferta y del CV.
        gaps: lista corta de lo que le falta al candidato para esta oferta.
        deal_breaker: el deal breaker que la descarta, o null si no hay ninguno.
    """
    if not 1 <= score <= 10:
        return _reply(tool_call_id, f"Score invalido: {score}. Tiene que ser de 1 a 10. Corrigelo.")

    rejected = _deal_breaker_misuse(deal_breaker, gaps, state["job"].description)
    if rejected:
        return _reply(tool_call_id, rejected)

    evaluation = Evaluation(
        job_id=state["job"].id,
        run_id=state["run_id"],
        score=score,
        band=band_for(score),  # la banda la decide el codigo, no el modelo
        review=review,
        strengths=strengths,
        gaps=gaps,
        deal_breaker=deal_breaker,
        model=settings.openai_model,
        prompt_version=PROMPT_VERSION,
    )
    repository.save_evaluation(evaluation)
    return _reply(
        tool_call_id,
        f"Guardada: {score}/10 ({evaluation.band}).",
        evaluation=evaluation,
    )


def _reply(tool_call_id: str, text: str, **state_updates) -> Command:
    """Responde al modelo y, de paso, actualiza el state del grafo."""
    return Command(
        update={"messages": [ToolMessage(text, tool_call_id=tool_call_id)], **state_updates}
    )


# La modalidad es una preferencia blanda. El modelo tiende a inflarla: la inventa cuando el aviso
# no la declara (is_remote=False de JobSpy solo significa "no marcada como remota") y la convierte
# en deal breaker. Prohibirlo en el prompt no alcanzo, asi que se verifica en codigo.
MODALITY_WORDS = ("presencial", "on-site", "on site", "onsite", "en oficina", "modalidad",
                  "remoto", "remota", "hibrido", "hibrida", "híbrido", "híbrida", "teletrabajo")


def _mentions_modality(text: str | None) -> bool:
    return any(w in (text or "").lower() for w in MODALITY_WORDS)


# El modelo tambien usa el deal breaker "junior" como comodin para cualquier mal calce: marco como
# junior un "Lider Estrategico de IA" que pedia 7 anios. Se exige evidencia en el aviso.
JUNIOR_WORDS = ("junior", "jr.", "jr ", "trainee", "practicante", "recien egresad", "recién egresad",
                "sin experiencia", "primer empleo", "entry level", "entry-level")
YEARS_PATTERN = re.compile(r"(\d+)\s*(?:\+|o m[aá]s)?\s*a[nñ]os")


def _offer_is_junior(description: str | None) -> bool:
    """True si el aviso dice junior con esas palabras, o pide 2 anios o menos."""
    text = (description or "").lower()
    if any(w in text for w in JUNIOR_WORDS):
        return True
    years = [int(y) for y in YEARS_PATTERN.findall(text)]
    return bool(years) and min(years) <= 2


def _deal_breaker_misuse(deal_breaker: str | None, gaps: list[str], description: str | None) -> str | None:
    """Devuelve el reclamo al modelo si uso un deal breaker sin evidencia; None si esta ok."""
    db = (deal_breaker or "").lower()
    claims_junior = any(w in db for w in ("junior", "seniority", "senior", "nivel"))
    if claims_junior and not _offer_is_junior(description):
        return (
            "Rechazado: pusiste el deal breaker de seniority, pero el aviso no dice junior, "
            "trainee ni practicante, y no pide 2 anios o menos. Que el rol no calce, sea de otra "
            "area o pida MAS seniority no es un deal breaker: es un score bajo con sus gaps. "
            "Vuelve a llamar save_evaluation con deal_breaker en null."
        )
    if _mentions_modality(deal_breaker):
        return (
            "Rechazado: la modalidad de trabajo nunca es deal breaker para este candidato. "
            "Vuelve a llamar save_evaluation con deal_breaker en null y el score que corresponda "
            "por el calce con el rol."
        )
    if any(_mentions_modality(g) for g in gaps) and not _mentions_modality(description):
        return (
            "Rechazado: pusiste la modalidad como gap, pero el aviso no la declara en ninguna "
            "parte. Que el portal no la marque como remota no significa nada. Vuelve a llamar "
            "save_evaluation sin ese gap y sin mencionar la modalidad en el review."
        )
    return None


TOOLS = [save_evaluation]
