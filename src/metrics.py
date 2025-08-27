import time
from functools import wraps
from typing import Callable, TypeVar, Any

from prometheus_client import Counter, Histogram, start_http_server

# Metrics definitions
REQUEST_LATENCY = Histogram(
    "function_latency_seconds", "Latency of function calls", ["function"]
)
REQUEST_ERRORS = Counter(
    "function_errors_total", "Total errors", ["function"]
)

_METRICS_STARTED = False


def start_metrics_server(port: int = 8000) -> None:
    """Expose metrics on the given port."""
    global _METRICS_STARTED
    if not _METRICS_STARTED:
        start_http_server(port)
        _METRICS_STARTED = True


F = TypeVar("F", bound=Callable[..., Any])


def track_metrics(func: F) -> F:
    """Decorator to record latency and errors for ``func``."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            REQUEST_ERRORS.labels(func.__name__).inc()
            REQUEST_LATENCY.labels(func.__name__).observe(time.perf_counter() - start)
            raise
        REQUEST_LATENCY.labels(func.__name__).observe(time.perf_counter() - start)
        return result

    return wrapper  # type: ignore[return-value]
