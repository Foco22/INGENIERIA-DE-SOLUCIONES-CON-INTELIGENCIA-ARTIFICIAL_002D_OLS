import os

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

_configured = False


def setup_telemetry() -> None:
    """Envia trazas del agente a Grafana Cloud via OTLP.

    Lee OTEL_EXPORTER_OTLP_ENDPOINT y OTEL_EXPORTER_OTLP_HEADERS del entorno.
    Si no estan definidas, no hace nada.
    """
    global _configured
    if _configured or not os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return

    resource = Resource.create(
        {"service.name": os.getenv("OTEL_SERVICE_NAME", "agente-matematico")}
    )
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    LangChainInstrumentor().instrument(tracer_provider=provider)
    _configured = True


def record_error(session_id: str, node: str, error: Exception) -> None:
    """Emite un span de error con la sesion y el nodo donde fallo, para rastrearlo en Grafana."""
    tracer = trace.get_tracer("agente-matematico.errores")
    with tracer.start_as_current_span(f"error_{node}") as span:
        span.set_attribute("session.id", session_id)
        span.set_attribute("error.node", node)
        span.set_attribute("error.type", type(error).__name__)
        span.record_exception(error)
        span.set_status(Status(StatusCode.ERROR, f"{type(error).__name__}: {error}"))
