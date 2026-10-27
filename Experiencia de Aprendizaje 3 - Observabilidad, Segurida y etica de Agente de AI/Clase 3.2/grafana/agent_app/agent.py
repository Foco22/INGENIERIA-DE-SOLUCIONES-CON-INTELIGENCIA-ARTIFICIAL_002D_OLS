from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, AIMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from agent_app.tools import sumar, restar, multiplicar, dividir, buscar_en_internet
from agent_app.prompts import AGENT_SYSTEM_PROMPT
from agent_app.telemetry import setup_telemetry, record_error
from agent_app.costs import get_model_name

load_dotenv()
setup_telemetry()

tools = [sumar, restar, multiplicar, dividir, buscar_en_internet]
llm = ChatOpenAI(model=get_model_name(), temperature=0).bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    system = SystemMessage(content=AGENT_SYSTEM_PROMPT)
    try:
        response = llm.invoke([system] + state["messages"])
    except Exception as e:
        record_error(config["configurable"]["thread_id"], "agent", e)
        response = AIMessage(
            content="Lo siento, tuve un problema al procesar tu pregunta. Intenta de nuevo.",
            additional_kwargs={"error": True},
        )
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


tool_node = ToolNode(tools, handle_tool_errors=True)

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    END: END,
})
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)