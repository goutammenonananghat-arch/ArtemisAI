"""Placeholder Gemini backend."""
from __future__ import annotations

from typing import Any, Dict, Tuple


def generate(task: str, context: Dict[str, Any] | None = None) -> Tuple[str, int]:
    """Generate a dummy response for ``task``.

    This simple placeholder echoes the task and returns a naive token
    count based on whitespace splitting.  Real implementations would
    call the Gemini API.
    """
    context = context or {}
    response = f"Echo: {task}"
    tokens = len(task.split())
    return response, tokens
