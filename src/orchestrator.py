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

    # Example sensitive operation ------------------------------------------------
    def store_secret(self, name: str, secret: str) -> None:
        """Store a credential securely after confirmation."""
        self.run(lambda: self.secrets.store(name, secret), privileged=True)

    # LLM interaction ----------------------------------------------------------
    def stream_chat(self, prompt: str, model: str = "gpt-3.5-turbo"):
        """Yield a language model response token-by-token.

        Parameters
        ----------
        prompt:
            The user prompt to send to the model.
        model:
            LLM model identifier understood by the OpenAI API.

        Yields
        ------
        str
            Successive chunks of the model response as they arrive.
        """
        try:
            import openai
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("openai package is required for streaming chat") from exc

        api_key = self.secrets.retrieve("openai_api_key")
        if api_key:
            openai.api_key = api_key

        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        for chunk in response:
            delta = chunk["choices"][0]["delta"].get("content")
            if delta:
                yield delta
