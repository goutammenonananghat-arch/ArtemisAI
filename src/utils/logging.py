import json
import logging
from typing import Optional

from opentelemetry import trace


class JsonFormatter(logging.Formatter):
    """Format log records as JSON, including trace context if available."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        base = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach trace information if a span is active
        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.is_valid:
            base["trace_id"] = format(ctx.trace_id, "032x")
            base["span_id"] = format(ctx.span_id, "016x")
        if record.exc_info:
            base["exception"] = self.formatException(record.exc_info)
        return json.dumps(base)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application logging with JSON output.

    Parameters
    ----------
    level:
        Logging level for the root logger. Defaults to ``logging.INFO``.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger.

    Calling this ensures the logging system is configured before use.
    """
    if not logging.getLogger().handlers:
        configure_logging()
    return logging.getLogger(name)
