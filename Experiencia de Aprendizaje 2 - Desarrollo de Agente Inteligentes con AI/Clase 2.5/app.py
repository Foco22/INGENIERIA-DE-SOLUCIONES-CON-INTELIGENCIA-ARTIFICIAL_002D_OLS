import os
import uuid
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Debe ir antes de importar el agente: ChatOpenAI lee OPENAI_API_KEY al crearse.
load_dotenv()

from agent_app.agent import graph
from evaluation.evaluate import load_dataset, evaluate_item, summarize, save_results


def show_trace(trace: dict) -> None:
    with st.expander("🔧 Trazabilidad"):
        if not trace["tool_used"]:
            st.write("No se invocó ninguna tool: respuesta directa del LLM.")
            return
        for call in trace["tool_calls"]:
            st.write(f"**Tool:** `{call['name']}`")
            st.json(call["args"])
        st.write(f"**Documentos recuperados:** {len(trace['retrieved_docs'])}")
        show_validations(trace.get("validations", []))
        for doc in trace["retrieved_docs"]:
            st.caption(f"Abastible {doc['year']} — página {doc['page']}")
            st.text(doc["content"][:800])


def show_validations(validations: list[dict]) -> None:
    for i, v in enumerate(validations, start=1):
        icon = "✅" if v["supported"] else "❌"
        st.write(f"**Validador (intento {i}):** {icon} {v['reason']}")
        if not v["supported"]:
            st.caption(f"Respuesta descartada: {v['answer']}")


def show_metrics(summary: dict, rows: list[dict]) -> None:
    col_tool, col_answer = st.columns(2)
    col_tool.metric("Tool Accuracy", f"{summary['tool_accuracy']:.0%}",
                    help="% de preguntas donde el agente usó (o no) la tool como se esperaba.")
    col_answer.metric("Answer Accuracy", f"{summary['answer_accuracy']:.0%}",
                      help="% de respuestas correctas según el LLM-as-judge.")

    st.subheader("Por categoría")
    st.dataframe(
        pd.DataFrame([
            {"categoría": cat, "preguntas": m["n"],
             "tool_accuracy": f"{m['tool_accuracy']:.0%}", "answer_accuracy": f"{m['answer_accuracy']:.0%}"}
            for cat, m in summary["by_category"].items()
        ]),
        hide_index=True, width="stretch",
    )

    st.subheader("Detalle por pregunta")
    st.dataframe(
        pd.DataFrame([
            {"id": r["id"], "categoría": r["category"], "pregunta": r["question"],
             "tools esperadas": ", ".join(r["expected_tools"]) or "—",
             "tools llamadas": ", ".join(r["tools_called"]) or "—",
             "tool ✔": "✅" if r["tool_correct"] else "❌",
             "answer ✔": "✅" if r["answer_correct"] else "❌"}
            for r in rows
        ]),
        hide_index=True, width="stretch",
    )

    # Trazabilidad completa de cada pregunta: qué buscó, qué respondió y por qué el juez decidió así.
    for r in rows:
        icon = "✅" if r["tool_correct"] and r["answer_correct"] else "❌"
        with st.expander(f"{icon} {r['id']} · {r['question']}"):
            st.write(f"**Respuesta del agente:** {r['answer']}")
            st.write(f"**Respuesta esperada:** {r['expected_answer']}")
            st.write(f"**Juez:** {r['judge_reason']}")
            if r["tool_calls"]:
                st.write("**Llamadas a la tool:**")
                st.json(r["tool_calls"])
                st.caption("Páginas recuperadas: " + ", ".join(r["retrieved_pages"]))
            show_validations(r.get("validations", []))


st.set_page_config(page_title="Asistente Abastible", layout="wide")
st.title("Asistente Abastible")

tab_chat, tab_eval = st.tabs(["💬 Chat", "📊 Evaluación"])


# ---------- Pestaña Chat ----------
with tab_chat:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "history" not in st.session_state:
        st.session_state.history = []

    # Nuevo thread = nueva memoria en LangGraph y nuevo thread en LangSmith.
    caption_col, button_col = st.columns([3, 1], vertical_alignment="center")
    caption_col.caption(f"Estados financieros consolidados 2021–2025 · Thread: `{st.session_state.thread_id}`")
    if button_col.button("🔄 Nuevo thread", width="stretch"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

    messages_box = st.container()
    for msg in st.session_state.history:
        with messages_box.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("trace"):
                show_trace(msg["trace"])

    if prompt := st.chat_input("¿Qué quieres saber sobre los estados financieros de Abastible?"):
        st.session_state.history.append({"role": "user", "content": prompt})
        with messages_box.chat_message("user"):
            st.write(prompt)

        with messages_box.chat_message("assistant"):
            with st.spinner("Procesando..."):
                config = {
                    "configurable": {"thread_id": st.session_state.thread_id},
                    "metadata": {"thread_id": st.session_state.thread_id},
                    "run_name": "chat_turn",
                    "recursion_limit": 20,
                }
                result = graph.invoke({"messages": [HumanMessage(content=prompt)]}, config=config)

            answer = result["messages"][-1].content
            trace = {
                "tool_used": result["tool_used"],
                "tool_calls": result["tool_calls"],
                "retrieved_docs": result["retrieved_docs"],
                "validations": result.get("validations", []),
            }
            st.write(answer)
            show_trace(trace)

        st.session_state.history.append({"role": "assistant", "content": answer, "trace": trace})


# ---------- Pestaña Evaluación ----------
with tab_eval:
    dataset = load_dataset()
    st.write(f"Dataset: **{len(dataset)} preguntas** · métricas: **Tool Accuracy** y **Answer Accuracy**")
    with st.expander("Ver dataset"):
        st.dataframe(pd.DataFrame(dataset), hide_index=True, width="stretch")

    if st.button("▶️ Correr evaluación", type="primary"):
        rows = []
        progress = st.progress(0.0, text="Iniciando...")
        for i, item in enumerate(dataset, start=1):
            progress.progress((i - 1) / len(dataset), text=f"{item['id']}: {item['question']}")
            rows.append(evaluate_item(item))
        progress.progress(1.0, text="Evaluación terminada")

        summary = summarize(rows)
        path = save_results(summary, rows)
        # Se guarda en sesión para que los resultados sigan visibles al usar el chat.
        st.session_state.eval_result = {"summary": summary, "rows": rows,
                                        "path": os.path.basename(path)}

    if "eval_result" in st.session_state:
        result = st.session_state.eval_result
        st.caption(f"Resultados guardados en `evaluation/results/{result['path']}`")
        show_metrics(result["summary"], result["rows"])
