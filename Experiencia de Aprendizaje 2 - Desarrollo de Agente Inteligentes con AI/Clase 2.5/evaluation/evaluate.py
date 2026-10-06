import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

# Debe ir antes de importar el agente: ChatOpenAI lee OPENAI_API_KEY al crearse.
load_dotenv()

from agent_app.agent import graph, llm
from agent_app.prompts import JUDGE_SYSTEM_PROMPT

EVAL_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(EVAL_DIR, "dataset.json")
RESULTS_DIR = os.path.join(EVAL_DIR, "results")


class Judgement(BaseModel):
    correct: bool
    reason: str


judge = llm.with_structured_output(Judgement)


def run_agent(question: str) -> dict:
    # Un thread nuevo por pregunta: ninguna respuesta depende de la conversación anterior.
    thread_id = str(uuid.uuid4())
    config = {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id, "eval": True},
        "run_name": "eval_question",
        "recursion_limit": 10,
    }
    result = graph.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    return {
        "answer": result["messages"][-1].content,
        "tool_used": result["tool_used"],
        # Nombres distintos de tools llamadas (una tool llamada 2 veces, ej. por año, cuenta una vez).
        "tools_called": sorted({c["name"] for c in result["tool_calls"]}),
        "tool_calls": result["tool_calls"],
        "retrieved_pages": [f"{d['year']}-p{d['page']}" for d in result["retrieved_docs"]],
    }


def judge_answer(item: dict, answer: str) -> Judgement:
    content = (
        f"Categoría: {item['category']}\n"
        f"Pregunta: {item['question']}\n"
        f"Respuesta esperada: {item['expected_answer']}\n"
        f"Respuesta del agente: {answer}"
    )
    return judge.invoke([{"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                         {"role": "user", "content": content}])


def summarize(rows: list[dict]) -> dict:
    n = len(rows)
    summary = {
        "total": n,
        "tool_accuracy": sum(r["tool_correct"] for r in rows) / n,
        "answer_accuracy": sum(r["answer_correct"] for r in rows) / n,
        "by_category": {},
    }
    for cat in sorted({r["category"] for r in rows}):
        sub = [r for r in rows if r["category"] == cat]
        summary["by_category"][cat] = {
            "n": len(sub),
            "tool_accuracy": sum(r["tool_correct"] for r in sub) / len(sub),
            "answer_accuracy": sum(r["answer_correct"] for r in sub) / len(sub),
        }
    return summary


def load_dataset() -> list[dict]:
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)


def evaluate_item(item: dict) -> dict:
    """Corre el agente sobre una pregunta y la juzga. Lo usan este script y la pestaña de Streamlit."""
    out = run_agent(item["question"])
    verdict = judge_answer(item, out["answer"])
    return {
        **item,
        **out,
        # Se comparan nombres, no solo "usó / no usó": con varias tools, llamar la equivocada es un error.
        # [] esperado = no debía llamar ninguna tool.
        "tool_correct": out["tools_called"] == sorted(set(item["expected_tools"])),
        "answer_correct": verdict.correct,
        "judge_reason": verdict.reason,
    }


def save_results(summary: dict, rows: list[dict]) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"run_{datetime.now():%Y%m%d_%H%M%S}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "rows": rows}, f, ensure_ascii=False, indent=2)
    return path


def main() -> None:
    rows = []
    for item in load_dataset():
        row = evaluate_item(item)
        rows.append(row)
        print(f"{item['id']} [{item['category']:<14}] "
              f"tool {'✔' if row['tool_correct'] else '✘'} (esperadas={item['expected_tools']} llamadas={row['tools_called']}) | "
              f"answer {'✔' if row['answer_correct'] else '✘'} | {item['question'][:60]}")

    summary = summarize(rows)
    print("\n========== RESULTADOS ==========")
    print(f"Tool Accuracy:   {summary['tool_accuracy']:.1%}")
    print(f"Answer Accuracy: {summary['answer_accuracy']:.1%}")
    print("\nPor categoría:")
    for cat, m in summary["by_category"].items():
        print(f"  {cat:<15} n={m['n']:<3} tool={m['tool_accuracy']:.1%}  answer={m['answer_accuracy']:.1%}")

    print(f"\nDetalle guardado en {save_results(summary, rows)}")


if __name__ == "__main__":
    main()
