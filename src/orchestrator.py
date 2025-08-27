"""Orchestrator module with permission prompts, metrics, tracing, and audit logging."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, List, Tuple, Protocol

# ---- Structured logging, metrics, tracing, secrets ---------------------------
from logging_setup import JsonFormatter, setup_logging
from metrics import start_metrics_server, track_metrics
from security.secrets_manager import SecretsManager
from tracing import traced


class Skill(Protocol):
    """Protocol all skills must follow."""

    def can_handle(self, intent: str) -> bool:
        """Return True if the skill can handle the intent."""
        ...

    def execute(self, payload: dict) -> Any:
        """Perform the skill's action using ``payload``."""
        ...


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

# Optional: secrets manager for privileged helpers
_secrets = SecretsManager()

# Registry storing (skill, privileged) pairs
_registry: List[Tuple[Skill, bool]] = []


def register_skill(skill: Skill, *, privileged: bool = False) -> None:
    """Register a skill for later dispatch."""
    _registry.append((skill, privileged))


def _confirm(message: str) -> bool:
    response = input(f"{message} (y/n): ").strip().lower()
    return response == "y"


@traced
@track_metrics
def _run(func: Callable[..., Any], *args: Any, privileged: bool = False, **kwargs: Any) -> Any:
    """Execute ``func`` optionally requiring privilege confirmation.

    When ``privileged`` is True, the user is prompted for confirmation
    before execution. The attempt is JSON-audit-logged to ``logs/security.log``.
    """
    if privileged:
        if not _confirm(f"Privileged action '{func.__name__}' requested. Proceed?"):
            _logger.info("Denied privileged command", extra={"function": func.__name__})
            print("Action cancelled.")
            return None
        _logger.info("Approved privileged command", extra={"function": func.__name__})
    return func(*args, **kwargs)


@traced
@track_metrics
def dispatch(intent: str, payload: dict) -> Any:
    """Dispatch ``payload`` to the first registered skill that can handle it."""
    for skill, privileged in _registry:
        if skill.can_handle(intent):
            return _run(skill.execute, payload, privileged=privileged)
    raise ValueError(f"No skill found for intent '{intent}'")


# Optional helper to store a secret with privilege guard
@traced
@track_metrics
def store_secret(name: str, secret: str) -> None:
    _run(lambda: _secrets.store(name, secret), privileged=True)
