# Agente Matemático con Evaluación

Clase 3.1 - Ingeniería de Soluciones con Inteligencia Artificial

## ¿Qué es este proyecto?

Un agente de IA que resuelve operaciones matemáticas usando **herramientas (tools)**.

En vez de que el modelo calcule directamente, el agente llama a funciones reales:

```
Usuario: "¿Cuánto es (10 - 4) * 4?"

Agente:
  1. Llama a restar(10, 4)     → 6
  2. Llama a multiplicar(6, 4) → 24
  3. Responde: 24
```

Esto permite medir si el agente toma las **decisiones correctas**, no solo si da la respuesta correcta.

---

## Herramientas disponibles

| Tool | Qué hace |
|---|---|
| `sumar(a, b)` | Suma dos números |
| `restar(a, b)` | Resta b de a |
| `multiplicar(a, b)` | Multiplica dos números |
| `dividir(a, b)` | Divide a entre b |

---

## Cómo correr el agente

```bash
streamlit run app.py
```

---

## Cómo correr la evaluación

```bash
python -m evals.test_eval
```

Genera dos métricas por cada caso en `evals/evals.json`:

- **Tool Call Accuracy**: ¿llamó a las tools correctas con los argumentos correctos?
- **Agent Goal Accuracy**: ¿la respuesta final es numéricamente correcta? (evaluado por un juez LLM)

---

## Variables de entorno

Crear un archivo `.env` con:
```
OPENAI_API_KEY=...
```

---

## Actividad

### Parte 1 — Agregar más casos de evaluación

El archivo `evals/evals.json` tiene actualmente 2 casos. Tu tarea es llegar a **10 casos**.

Cada caso tiene esta estructura:

```json
{
  "pregunta": "¿Cuánto es 9 * 3?",
  "respuesta_esperada": "27",
  "tools_esperadas": [
    { "tool": "multiplicar", "args": { "a": 9, "b": 3 } }
  ]
}
```

Incluye casos variados: solo suma, solo resta, solo división, operaciones combinadas, división por cero, números decimales, etc.

### Parte 2 — Agregar métrica de latencia

En `evals/test_eval.py`, mide cuánto tiempo demora el agente en responder cada pregunta y reporta el promedio al final.

**Pista:** usa `time.time()` antes y después de llamar al agente:

El resultado final debería verse así:

```
============================================================
RESULTADO FINAL
============================================================
  Tool Call Accuracy  (promedio): 1.00
  Agent Goal Accuracy (promedio): 1.00
  Latencia promedio              : 2.34s
============================================================
```

