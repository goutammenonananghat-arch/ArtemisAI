from functools import wraps
from typing import Callable, TypeVar, Any

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        SimpleSpanProcessor(ConsoleSpanExporter())
    )
    _tracer = trace.get_tracer(__name__)
except Exception:  # pragma: no cover - optional dependency
    _tracer = None

F = TypeVar("F", bound=Callable[..., Any])


def traced(func: F) -> F:
    """Decorator to create a span around ``func`` if tracing is available."""

    if _tracer is None:
        return func

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        with _tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
