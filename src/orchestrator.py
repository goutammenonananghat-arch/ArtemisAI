"""Orchestrator module with permission prompts, metrics and tracing."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Any

from logging_setup import JsonFormatter, setup_logging
from metrics import start_metrics_server, track_metrics
from security.secrets_manager import SecretsManager
from tracing import traced

# ---------------------------------------------------------------------------
# Global logging/metrics setup
setup_logging()
start_metrics_server()

# Configure audit logging to a file using JSON structure
LOG_PATH = Path("logs/security.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_logger = logging.getLogger("security")
_logger.setLevel(logging.INFO)
_file_handler = logging.FileHandler(LOG_PATH)
_file_handler.setFormatter(JsonFormatter())
_logger.addHandler(_file_handler)


class Orchestrator:
    """Coordinate operations, prompting for privilege where required."""

    def __init__(self) -> None:
        self.secrets = SecretsManager()

    def _confirm(self, message: str) -> bool:
        response = input(f"{message} (y/n): ").strip().lower()
        return response == "y"

    @traced
    @track_metrics
    def run(self, func: Callable[..., Any], *args: Any, privileged: bool = False, **kwargs: Any) -> Any:
        """Execute ``func`` optionally requiring privilege.

        When ``privileged`` is True, the user is prompted for confirmation
        before execution.  The attempt is logged to ``logs/security.log``.
        """
        if privileged:
            if not self._confirm(
                f"Privileged action '{func.__name__}' requested. Proceed?"
            ):
                _logger.info("Denied privileged command", extra={"function": func.__name__})
                print("Action cancelled.")
                return None
            _logger.info("Approved privileged command", extra={"function": func.__name__})
        return func(*args, **kwargs)

    # Example sensitive operation ------------------------------------------------
    @traced
    @track_metrics
    def store_secret(self, name: str, secret: str) -> None:
        """Store a credential securely after confirmation."""
        self.run(lambda: self.secrets.store(name, secret), privileged=True)
