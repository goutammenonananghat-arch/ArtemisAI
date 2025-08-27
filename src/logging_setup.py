import json
import logging
import sys
from pathlib import Path
from typing import Optional


class JsonFormatter(logging.Formatter):
    """Format logs as JSON."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        # Include any extra fields set on the record.
        for key, value in record.__dict__.items():
            if key not in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
            }:
                log_record[key] = value
        return json.dumps(log_record)


def setup_logging(log_file: Optional[Path] = None) -> None:
    """Configure root logger to output JSON."""

    formatter = JsonFormatter()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
