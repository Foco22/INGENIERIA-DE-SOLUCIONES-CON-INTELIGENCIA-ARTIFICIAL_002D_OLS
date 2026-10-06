# Clase 2.5 — Agente RAG sobre los estados financieros de Abastible

Agente LangGraph con una tool de RAG (`buscar_estados_financieros`) sobre los estados financieros
consolidados de Abastible 2021–2025, con interfaz Streamlit y evaluación por **Tool Accuracy** y
**Answer Accuracy**. La especificación completa está en `CLAUDE.md`.

## Cómo ejecutar

```bash
pip install -r requirements.txt
# .env con OPENAI_API_KEY (y opcionalmente LangSmith)

python -m agent_app.ingest        # 1. construye vectorstore/abastible.json (una vez)
streamlit run app.py              # 2. pestañas "💬 Chat" (con trazabilidad) y "📊 Evaluación"
python -m evaluation.evaluate     # 3. (opcional) la misma evaluación desde la terminal
```

## Grafo

```
START ──► reset ──► agent ──(¿tool_calls?)──► tools ──► agent
                         └──────────────────► END
```

- **State:** `messages`, `tool_used`, `tool_calls`, `retrieved_docs`.
- **reset:** limpia la trazabilidad del turno.
- **agent:** `gpt-4o-mini` con la tool enlazada decide si buscar o responder directo.
- **tools:** ejecuta la búsqueda y registra argumentos y documentos recuperados.

## Dataset (`evaluation/dataset.json`)

20 preguntas: 10 `rag` (deben usar la tool), 5 `no_tool` y 5 `falso_positivo` (parecen requerir
la tool pero no deben usarla). Las respuestas esperadas de `rag` están verificadas en `markdown/`.

## Métricas

- **Tool Accuracy:** % de preguntas donde los **nombres** de las tools llamadas coinciden con
  `expected_tools` (`[]` = no debía llamar ninguna).
- **Answer Accuracy:** % de respuestas correctas según un LLM-as-judge (`JUDGE_SYSTEM_PROMPT`).

Los resultados por corrida quedan en `evaluation/results/run_<timestamp>.json`.
