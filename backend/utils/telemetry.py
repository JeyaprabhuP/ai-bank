"""
OpenTelemetry setup. Exports traces to console by default.
Swap the ConsoleSpanExporter for an OTLPSpanExporter pointed at
Grafana Tempo / Jaeger / etc. later without touching business logic.
"""
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

logger = logging.getLogger("banking_ai_platform")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


def setup_telemetry(app):
    resource = Resource.create({"service.name": "banking-ai-platform-backend"})
    provider = TracerProvider(resource=resource)
    #provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    return trace.get_tracer("banking_ai_platform")


tracer = trace.get_tracer("banking_ai_platform")
