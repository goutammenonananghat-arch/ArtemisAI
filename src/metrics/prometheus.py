from contextlib import contextmanager
from time import time

from prometheus_client import Counter, Histogram, start_http_server

# Prometheus metrics
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latency of processed requests in seconds"
)
REQUEST_ERRORS = Counter(
    "request_errors_total", "Number of requests resulting in errors"
)


def start_metrics_server(port: int = 8000) -> None:
    """Start the Prometheus metrics exporter on the given port."""
    start_http_server(port)


@contextmanager
def track_latency() -> None:
    """Context manager to measure latency and count errors."""
    start_time = time()
    try:
        yield
        REQUEST_LATENCY.observe(time() - start_time)
    except Exception:
        REQUEST_ERRORS.inc()
        raise
