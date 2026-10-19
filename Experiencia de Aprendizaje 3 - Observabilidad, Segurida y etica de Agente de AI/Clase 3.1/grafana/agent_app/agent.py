from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from agent_app.tools import sumar, restar, multiplicar, dividir
from agent_app.prompts import AGENT_SYSTEM_PROMPT
from agent_app.telemetry import setup_telemetry

load_dotenv()
setup_telemetry()

tools = [sumar, restar, multiplicar, dividir]
llm = ChatOpenAI(model="gpt-5.5", temperature=0).bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState) -> AgentState:
    system = SystemMessage(content=AGENT_SYSTEM_PROMPT)
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


tool_node = ToolNode(tools)

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