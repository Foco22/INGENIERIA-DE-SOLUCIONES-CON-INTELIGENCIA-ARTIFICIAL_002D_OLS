"""El grafo de LangGraph: un nodo propio (`evaluator`) mas el ToolNode.

    START -> evaluator -> tools -> evaluator -> ... -> END

El ciclo deja que el agente encadene evaluate_offer y despues save_evaluation.
`route_after_tools` corta apenas se guarda, para no gastar un turno en despedirse.

Se compila una vez por corrida: la oferta entra por el state, no por el closure.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.llm import get_llm
from src.models import CandidateProfile
from src.prompts import EVALUATOR_SYSTEM_PROMPT
from src.states import EvaluationState
from src.tools import TOOLS


def build_evaluator_graph(profile: CandidateProfile):
    """Compila el grafo. El perfil va en el system prompt: es el mismo para todas las ofertas."""
    llm = get_llm().bind_tools(TOOLS)
    system = SystemMessage(
        EVALUATOR_SYSTEM_PROMPT.format(profile_block=profile.to_prompt_block())
    )

    def evaluator(state: EvaluationState) -> dict:
        """El unico nodo propio: lee la oferta y decide score y comentario."""
        return {"messages": [llm.invoke([system, *state["messages"]])]}

    graph = StateGraph(EvaluationState)
    graph.add_node("evaluator", evaluator)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "evaluator")
    # tools_condition: si el modelo llamo una tool va a "tools", si no, termina.
    graph.add_conditional_edges("evaluator", tools_condition)
    # Tras guardar se termina; si solo evaluo, vuelve para que llame save_evaluation.
    graph.add_conditional_edges(
        "tools", route_after_tools, {"evaluator": "evaluator", END: END}
    )

    return graph.compile()


def route_after_tools(state: EvaluationState) -> str:
    """Cierra el ciclo apenas se guarda: sin esto el agente gastaria un turno en despedirse."""
    return END if state.get("saved") else "evaluator"
