"""Orchestrator module with permission prompts and audit logging."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Any

from security.secrets_manager import SecretsManager

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


class Orchestrator:
    """Coordinate operations, prompting for privilege where required."""

    def __init__(self) -> None:
        self.secrets = SecretsManager()
        self.skills: dict[str, Callable[..., Any]] = {}

    def _confirm(self, message: str) -> bool:
        response = input(f"{message} (y/n): ").strip().lower()
        return response == "y"

    def run(self, func: Callable[..., Any], *args: Any, privileged: bool = False, **kwargs: Any) -> Any:
        """Execute ``func`` optionally requiring privilege.

        When ``privileged`` is True, the user is prompted for confirmation
        before execution.  The attempt is logged to ``logs/security.log``.
        """
        if privileged:
            if not self._confirm(f"Privileged action '{func.__name__}' requested. Proceed?"):
                _logger.info("Denied privileged command '%s'", func.__name__)
                print("Action cancelled.")
                return None
            _logger.info("Approved privileged command '%s'", func.__name__)
        return func(*args, **kwargs)

    # ------------------------------------------------------------------
    def register_skill(self, name: str, func: Callable[..., Any]) -> None:
        """Register ``func`` under ``name`` for later dispatch."""
        self.skills[name] = func

    def dispatch(self, name: str, *args: Any, privileged: bool = False, **kwargs: Any) -> Any:
        """Execute a previously registered skill by ``name``."""
        if name not in self.skills:
            raise KeyError(f"Unknown skill '{name}'")
        return self.run(self.skills[name], *args, privileged=privileged, **kwargs)

    # Example sensitive operation ------------------------------------------------
    def store_secret(self, name: str, secret: str) -> None:
        """Store a credential securely after confirmation."""
        self.run(lambda: self.secrets.store(name, secret), privileged=True)
