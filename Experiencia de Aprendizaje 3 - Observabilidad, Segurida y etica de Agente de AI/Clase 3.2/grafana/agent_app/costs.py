import os

from opentelemetry import trace


def get_model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.5")


def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Costo en USD segun los precios por 1M de tokens definidos en .env."""
    price_in = float(os.getenv("PRICE_INPUT_PER_1M", "0"))
    price_out = float(os.getenv("PRICE_OUTPUT_PER_1M", "0"))
    return (prompt_tokens * price_in + completion_tokens * price_out) / 1_000_000


def summarize_usage(usage: dict) -> dict:
    """Suma el uso de todas las llamadas al LLM de una pregunta.

    `usage` es el dict {modelo: usage_metadata} que entrega get_usage_metadata_callback.
    """
    prompt = sum(u.get("input_tokens", 0) for u in usage.values())
    completion = sum(u.get("output_tokens", 0) for u in usage.values())
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": prompt + completion,
        "cost_usd": calculate_cost(prompt, completion),
    }


def request_failed(messages: list) -> bool:
    """True si en la pregunta actual fallo una tool o el nodo del agente.

    Revisa los mensajes desde la ultima pregunta del usuario hacia adelante.
    """
    for msg in reversed(messages):
        if msg.type == "human":
            break
        if msg.type == "tool" and getattr(msg, "status", None) == "error":
            return True
        if msg.type == "ai" and msg.additional_kwargs.get("error"):
            return True
    return False


def record_cost(session_id: str, question: str, summary: dict, failed: bool = False) -> None:
    """Emite un span 'costo_pregunta' (uno por pregunta) para que el dashboard lo consulte en Tempo."""
    tracer = trace.get_tracer("agente-matematico.costos")
    with tracer.start_as_current_span("costo_pregunta") as span:
        span.set_attribute("session.id", session_id)
        span.set_attribute("input.value", question)
        span.set_attribute("llm.model", get_model_name())
        span.set_attribute("cost.prompt_tokens", summary["prompt_tokens"])
        span.set_attribute("cost.completion_tokens", summary["completion_tokens"])
        span.set_attribute("cost.total_tokens", summary["total_tokens"])
        span.set_attribute("cost.usd", summary["cost_usd"])
        span.set_attribute("request.failed", 1 if failed else 0)
