"""
Evaluacion del agente matematico.

Metricas implementadas (equivalentes a RAGAS):
- Tool Call Accuracy  : % de tools correctas llamadas (nombre + args)
- Agent Goal Accuracy : juez LLM que decide si la respuesta final es correcta
"""

import json
import uuid
import asyncio
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import time

from agent_app.agent import app

load_dotenv()

EVALS_PATH = Path(__file__).parent / "evals.json"
judge_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── Correr el agente ─────────────────────────────────────────────────────────

def run_agent(pregunta: str) -> list:
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = app.invoke({"messages": [HumanMessage(content=pregunta)]}, config=config)
    return result["messages"]


# ── Extraer tool calls realizadas ────────────────────────────────────────────

def extract_tool_calls(messages: list) -> list:
    """Retorna lista de {name, args} de cada tool call ejecutada."""
    calls = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                calls.append({"name": tc["name"], "args": tc["args"]})
    return calls


def get_final_answer(messages: list) -> str:
    """Retorna el contenido del ultimo mensaje del agente."""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return ""


# ── Metricas ─────────────────────────────────────────────────────────────────

def tool_call_accuracy(actual: list, expected: list) -> float:
    """
    Compara las tool calls reales vs esperadas en orden.
    Puntaje: fraccion de tools esperadas que coinciden en nombre y args.
    """
    if not expected:
        return 1.0

    correct = 0
    for i, exp in enumerate(expected):
        if i >= len(actual):
            break
        name_ok = actual[i]["name"] == exp["tool"]
        args_ok = all(
            str(actual[i]["args"].get(k)) == str(v)
            for k, v in exp["args"].items()
        )
        if name_ok and args_ok:
            correct += 1

    return correct / len(expected)


def agent_goal_accuracy(pregunta: str, respuesta_final: str, respuesta_esperada: str) -> float:
    """
    Usa GPT como juez para decidir si la respuesta final logra el objetivo.
    Retorna 1.0 si es correcta, 0.0 si no.
    """
    prompt = f"""Compara el resultado esperado con la respuesta del agente.
Si son numericamente iguales responde "si", si no responde "no".

Resultado esperado: {respuesta_esperada}
Respuesta del agente: {respuesta_final}

Responde SOLO con "si" o "no"."""

    print(f"   [DEBUG] Prompt juez enviado con esperado={repr(respuesta_esperada)} y agente={repr(respuesta_final)}")
    result = judge_llm.invoke(prompt)
    answer = result.content.strip().lower().rstrip(".")
    print(f"   [DEBUG] Juez respondio: {repr(answer)}")
    return 1.0 if answer in ("si", "sí", "yes") else 0.0


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    evals = json.loads(EVALS_PATH.read_text(encoding="utf-8"))

    tool_scores = []
    goal_scores = []
    latencies   = []

    print("=" * 60)
    print("Evaluacion del Agente Matematico")
    print("=" * 60)

    for i, caso in enumerate(evals):
        pregunta          = caso["pregunta"]
        respuesta_esperada = caso["respuesta_esperada"]
        tools_esperadas   = caso["tools_esperadas"]

        print(f"\n[{i+1}] {pregunta}")

        time_start = time.time()
        messages      = run_agent(pregunta)
        time_end = time.time()
        elapsed = time_end - time_start

        actual_calls  = extract_tool_calls(messages)
        final_answer  = get_final_answer(messages)

        t_score = tool_call_accuracy(actual_calls, tools_esperadas)
        g_score = agent_goal_accuracy(pregunta, final_answer, respuesta_esperada)

        tool_scores.append(t_score)
        goal_scores.append(g_score)
        latencies.append(elapsed)

        for c in actual_calls:
            print(f"   Tool llamada      : {c}")

        print(f"   Respuesta agente  : {final_answer}")
        print(f"   Latencia          : {elapsed:.2f}s")
        print(f"   Tool Call Accuracy : {t_score:.2f}")
        print(f"   Agent Goal Accuracy: {g_score:.2f}")

    avg_tool    = sum(tool_scores) / len(tool_scores)
    avg_goal    = sum(goal_scores) / len(goal_scores)
    avg_latency = sum(latencies)   / len(latencies)

    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    print(f"  Tool Call Accuracy  (promedio): {avg_tool:.2f}")
    print(f"  Agent Goal Accuracy (promedio): {avg_goal:.2f}")
    print(f"  Latencia promedio             : {avg_latency:.2f}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
