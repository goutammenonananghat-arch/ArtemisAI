from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def configure_tracing(service_name: str = "ArtemisAI") -> None:
    """Configure OpenTelemetry tracing for the service."""
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


def get_tracer(name: str) -> trace.Tracer:
    """Return a tracer for the given module name."""
    return trace.get_tracer(name)
