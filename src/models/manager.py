"""Dispatch requests to model backends."""
from __future__ import annotations

import time
from importlib import import_module
from typing import Any, Callable, Dict, Tuple

# Map model identifiers to their generation callables
_BACKENDS: Dict[str, str] = {
    "gemini": "models.gemini.generate",
}


def _get_backend(path: str) -> Callable[[str, Dict[str, Any] | None], Tuple[str, int]]:
    """Return the backend callable from an import path."""
    module_name, func_name = path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, func_name)


def run(task: str, context: Dict[str, Any] | None, model_id: str = "gemini") -> Tuple[str, Dict[str, float]]:
    """Execute a model backend and return the result with metadata.

    Parameters
    ----------
    task:
        Prompt or instruction for the model.
    context:
        Additional information for generation.
    model_id:
        Identifier of the model backend to use.  Defaults to ``"gemini"``.

    Returns
    -------
    tuple
        A tuple of the generated response and a metadata dictionary
        containing ``tokens`` and ``latency``.
    """
    if model_id not in _BACKENDS:
        raise ValueError(f"Unsupported model_id '{model_id}'")

    generate = _get_backend(_BACKENDS[model_id])
    start = time.perf_counter()
    response, tokens = generate(task, context)
    latency = time.perf_counter() - start
    metadata = {"tokens": float(tokens), "latency": latency}
    return response, metadata
