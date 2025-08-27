"""Alerting utilities with simple channel adapters.

This module exposes a :func:`send` function which routes a message to a
channel specific adapter.  Adapters for text-to-speech (TTS), mobile push
notifications and email are provided as basic examples.  Each adapter simply
prints to stdout but is structured so real integrations can be swapped in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Protocol


class AlertAdapter(Protocol):
    """Protocol for alert channel adapters."""

    def send(self, message: str) -> None:
        """Deliver ``message`` through the channel."""


@dataclass
class TTSAdapter:
    """Convert the message to speech."""

    def send(self, message: str) -> None:  # pragma: no cover - placeholder
        print(f"[TTS] {message}")


@dataclass
class PushAdapter:
    """Push a notification to a mobile device."""

    def send(self, message: str) -> None:  # pragma: no cover - placeholder
        print(f"[PUSH] {message}")


@dataclass
class EmailAdapter:
    """Send the message via email."""

    def send(self, message: str) -> None:  # pragma: no cover - placeholder
        print(f"[EMAIL] {message}")


_ADAPTERS: Dict[str, AlertAdapter] = {
    "tts": TTSAdapter(),
    "push": PushAdapter(),
    "email": EmailAdapter(),
}


def send(channel: str, message: str) -> None:
    """Dispatch ``message`` to the specified ``channel``.

    Parameters
    ----------
    channel:
        One of ``"tts"``, ``"push"`` or ``"email"``.
    message:
        Text to deliver.
    """

    adapter = _ADAPTERS.get(channel)
    if adapter is None:
        raise ValueError(f"Unknown alert channel: {channel}")
    adapter.send(message)

