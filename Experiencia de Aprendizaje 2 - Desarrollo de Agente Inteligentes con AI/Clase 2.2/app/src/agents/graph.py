"""El grafo de LangGraph: un nodo propio (`evaluator`) mas el ToolNode.

    START -> evaluator -> tools -> END

`evaluator` es la unica llamada al LLM: ahi se generan el score y el review, como argumentos
del tool call. `tools` ejecuta save_evaluation, que valida y guarda. Si la tool rechaza (score
fuera de rango, modalidad mal usada), el grafo vuelve al evaluador para que corrija.

Se compila una vez por corrida: la oferta entra por el state, no por el closure.
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from src.utils.llm import get_llm
from src.utils.models import CandidateProfile
from src.agents.prompts import EVALUATOR_SYSTEM_PROMPT
from src.agents.states import EvaluationState
from src.agents.tools import TOOLS


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
    # tools_condition: si el modelo llamo la tool va a "tools", si no, termina.
    graph.add_conditional_edges("evaluator", tools_condition)
    # Guardado -> fin. Rechazado -> el modelo corrige y vuelve a llamar.
    graph.add_conditional_edges(
        "tools", route_after_tools, {"evaluator": "evaluator", END: END}
    )

    return graph.compile()


def route_after_tools(state: EvaluationState) -> str:
    """Termina si la tool guardo; si la rechazo, el evaluador tiene que corregir."""
    return END if state.get("evaluation") else "evaluator"
