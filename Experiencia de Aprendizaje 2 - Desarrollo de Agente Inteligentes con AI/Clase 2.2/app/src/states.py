"""El state del grafo: los mensajes mas lo que las dos tools necesitan compartir."""

from __future__ import annotations

from langgraph.graph import MessagesState

from src.models import Evaluation, JobOffer


class EvaluationState(MessagesState):
    """MessagesState + el contexto de la oferta que se esta evaluando.

    `job` y `run_id` los pone el caller, no el modelo: por eso las tools los leen del state
    con InjectedState en vez de recibirlos como argumentos.
    """

    job: JobOffer
    run_id: str
    draft: Evaluation | None   # lo que dejo evaluate_offer, pendiente de guardar
    saved: bool                # True cuando save_evaluation ya escribio en la DB
