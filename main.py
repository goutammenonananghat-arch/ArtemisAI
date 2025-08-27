"""Entry point for interactive chat session."""
from __future__ import annotations

from src.orchestrator import Orchestrator
from src.chat_interface import ChatInterface


def main() -> None:
    orchestrator = Orchestrator()
    chat = ChatInterface(orchestrator)
    chat.chat()


if __name__ == "__main__":
    main()
