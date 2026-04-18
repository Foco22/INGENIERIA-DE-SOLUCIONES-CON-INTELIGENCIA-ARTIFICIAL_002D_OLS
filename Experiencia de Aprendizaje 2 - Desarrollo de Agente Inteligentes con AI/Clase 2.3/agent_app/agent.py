from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from typing import TypedDict, Annotated
from datetime import date
from dotenv import load_dotenv

from agent_app.tools import rag_search, schedule_meeting, get_available_slots, get_next_date_for_weekday
from agent_app.prompts import AGENT_SYSTEM_PROMPT, QUERY_REFORMULATION_PROMPT, APPROVAL_INTERPRETATION_PROMPT

load_dotenv()

tools = [rag_search, get_next_date_for_weekday, get_available_slots, schedule_meeting]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools(tools)
query_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState) -> AgentState:
    today = date.today().strftime("%Y-%m-%d")
    system = SystemMessage(content=AGENT_SYSTEM_PROMPT + f"\n\nFecha de hoy: {today}")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


def generate_query(state: AgentState) -> AgentState:
    """Reformulates the conversation history into an optimized search query."""
    conversation = "\n".join(
        f"{m.type}: {m.content}" for m in state["messages"] if m.content
    )
    prompt = [
        SystemMessage(content=QUERY_REFORMULATION_PROMPT),
        SystemMessage(content=f"Conversation:\n{conversation}"),
    ]
    result = query_llm.invoke(prompt)
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


def _interpret_approval(user_response: str) -> bool:
    result = query_llm.invoke([
        SystemMessage(content=APPROVAL_INTERPRETATION_PROMPT),
        SystemMessage(content=f"User response: {user_response}"),
    ])
    return result.content.strip().lower() == "yes"


def human_approval(state: AgentState) -> AgentState:
    """Pauses execution and asks the user to confirm the meeting."""
    last_message = state["messages"][-1]
    tool_call = last_message.tool_calls[0]

    user_response = interrupt({
        "question": "¿Confirmas agendar esta reunión?",
        "meeting": tool_call["args"],
    })

    if not _interpret_approval(user_response):
        updated_ai = AIMessage(
            id=last_message.id,
            content=last_message.content,
            tool_calls=[],
        )
        cancel_msg = ToolMessage(
            content="Reunión cancelada por el usuario.",
            tool_call_id=tool_call["id"],
        )
        return {"messages": [updated_ai, cancel_msg]}

    return {}


def after_approval(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, ToolMessage):
        return "agent"
    return "tools"


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_name = last_message.tool_calls[0]["name"]
        if tool_name == "rag_search":
            return "generate_query"
        if tool_name == "schedule_meeting":
            return "human_approval"
        return "tools"
    return END


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("generate_query", generate_query)
graph.add_node("human_approval", human_approval)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "generate_query": "generate_query",   # rag_search
    "tools": "tools",                     # cualquier otra tool
    "human_approval": "human_approval",   # schedule_meeting
    END: END,
})
graph.add_edge("generate_query", "tools")
graph.add_conditional_edges("human_approval", after_approval, {
    "tools": "tools",
    "agent": "agent",
})
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)