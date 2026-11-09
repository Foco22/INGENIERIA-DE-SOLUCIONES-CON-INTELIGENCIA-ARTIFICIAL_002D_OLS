from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
import os
from typing import TypedDict, Annotated, Optional
from datetime import date
from dotenv import load_dotenv

from agent_app.tools import rag_search
from agent_app.prompts import AGENT_SYSTEM_PROMPT, QUERY_REFORMULATION_PROMPT
from agent_app.guardrails import run_guardrails


load_dotenv()

MODEL = "gpt-4o-mini"

tools = [rag_search]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    is_offensive: Optional[bool]
    is_prompt_injection: Optional[bool]
    is_off_topic: Optional[bool]
    is_academic_dishonesty: Optional[bool]
    is_pii: Optional[bool]


def _get_llm(model: str):
    return ChatOpenAI(
        model=model,
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    ).bind_tools(tools)


def _get_query_llm(model: str):
    return ChatOpenAI(
        model=model,
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    )


def check_guardrails(state: AgentState, config: RunnableConfig) -> AgentState:
    """Run the 5 input guardrail evaluators in parallel on the last user message."""
    model = config.get("configurable", {}).get("model", MODEL)

    last_human = next(
        (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
        None,
    )
    if last_human is None:
        return {
            "is_offensive": False,
            "is_prompt_injection": False,
            "is_off_topic": False,
            "is_academic_dishonesty": False,
            "is_pii": False,
        }

    results = run_guardrails(last_human.content, model)
    return results


def route_after_guardrails(state: AgentState) -> str:
    if (
        state.get("is_offensive")
        or state.get("is_prompt_injection")
        or state.get("is_off_topic")
        or state.get("is_academic_dishonesty")
        or state.get("is_pii")
    ):
        return "blocked"
    return "agent"


def blocked_response(state: AgentState) -> AgentState:
    return {
        "messages": [
            AIMessage(
                content=(
                    "Lo siento, no puedo responder a esa consulta. "
                    "El mensaje fue bloqueado por las políticas de uso."
                )
            )
        ]
    }


def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    model = config.get("configurable", {}).get("model", MODEL)
    today = date.today().strftime("%Y-%m-%d")
    system = SystemMessage(content=AGENT_SYSTEM_PROMPT + f"\n\nFecha de hoy: {today}")
    response = _get_llm(model).invoke([system] + state["messages"])
    return {"messages": [response]}


def generate_query(state: AgentState, config: RunnableConfig) -> AgentState:
    """Reformulates the conversation history into an optimized search query."""
    model = config.get("configurable", {}).get("model", MODEL)
    conversation = "\n".join(
        f"{m.type}: {m.content}" for m in state["messages"] if m.content
    )
    prompt = [
        SystemMessage(content=QUERY_REFORMULATION_PROMPT),
        SystemMessage(content=f"Conversation:\n{conversation}"),
    ]
    result = _get_query_llm(model).invoke(prompt)
    search_query = result.content.strip()

    last_message = state["messages"][-1]
    updated_tool_calls = [
        {**tc, "args": {"query": search_query}}
        for tc in last_message.tool_calls
    ]
    updated_message = AIMessage(
        id=last_message.id,
        content=last_message.content,
        tool_calls=updated_tool_calls,
    )
    return {"messages": [updated_message]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "generate_query"
    return END


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("check_guardrails", check_guardrails)
graph.add_node("blocked_response", blocked_response)
graph.add_node("agent", call_model)
graph.add_node("generate_query", generate_query)
graph.add_node("tools", tool_node)

graph.set_entry_point("check_guardrails")
graph.add_conditional_edges("check_guardrails", route_after_guardrails, {
    "blocked": "blocked_response",
    "agent": "agent",
})
graph.add_edge("blocked_response", END)
graph.add_conditional_edges("agent", should_continue, {
    "generate_query": "generate_query",
    END: END,
})
graph.add_edge("generate_query", "tools")
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)