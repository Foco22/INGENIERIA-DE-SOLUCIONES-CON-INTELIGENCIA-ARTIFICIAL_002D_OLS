"""El state del grafo: los mensajes mas el contexto de la oferta y el resultado."""

from __future__ import annotations

from langgraph.graph import MessagesState

from src.utils.models import Evaluation, JobOffer


class EvaluationState(MessagesState):
    """MessagesState + el contexto de la oferta que se esta evaluando.

    `job` y `run_id` los pone el caller, no el modelo: por eso la tool los lee del state
    con InjectedState en vez de recibirlos como argumentos.
    """

    job: JobOffer
    run_id: str
    evaluation: Evaluation | None   # lo que guardo save_evaluation; None si no la llamo
