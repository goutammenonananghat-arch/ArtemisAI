"""Skill orchestration with permission prompts and audit logging."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, List, Tuple, Protocol


class Skill(Protocol):
    """Protocol all skills must follow."""

    def can_handle(self, intent: str) -> bool:
        """Return True if the skill can handle the intent."""

        ...

    def execute(self, payload: dict) -> Any:
        """Perform the skill's action using ``payload``."""

        ...


# ---------------------------------------------------------------------------
# Configure audit logging
LOG_PATH = Path("logs/security.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
_logger = logging.getLogger("security")
_logger.setLevel(logging.INFO)
_handler = logging.FileHandler(LOG_PATH)
_formatter = logging.Formatter("%(asctime)s - %(message)s")
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)

# Registry storing (skill, privileged) pairs
_registry: List[Tuple[Skill, bool]] = []


def register_skill(skill: Skill, *, privileged: bool = False) -> None:
    """Register a skill for later dispatch."""

    _registry.append((skill, privileged))


def _confirm(message: str) -> bool:
    response = input(f"{message} (y/n): ").strip().lower()
    return response == "y"


def _run(func: Callable[..., Any], *args: Any, privileged: bool = False, **kwargs: Any) -> Any:
    """Execute ``func`` optionally requiring privilege confirmation."""

    if privileged:
        if not _confirm(f"Privileged action '{func.__name__}' requested. Proceed?"):
            _logger.info("Denied privileged command '%s'", func.__name__)
            print("Action cancelled.")
            return None
        _logger.info("Approved privileged command '%s'", func.__name__)
    return func(*args, **kwargs)


def dispatch(intent: str, payload: dict) -> Any:
    """Dispatch ``payload`` to the first registered skill that can handle it."""

    for skill, privileged in _registry:
        if skill.can_handle(intent):
            return _run(skill.execute, payload, privileged=privileged)
    raise ValueError(f"No skill found for intent '{intent}'")

