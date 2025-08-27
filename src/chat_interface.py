"""Simple terminal chat interface with optional speech hooks."""
from __future__ import annotations

from typing import Callable, Iterable, Optional


class ChatInterface:
    """Interactive chat session that streams model replies.

    Parameters
    ----------
    orchestrator:
        Instance capable of returning an iterable of response chunks via
        ``stream_chat``.
    speech_to_text:
        Optional callable converting spoken audio to text input.
    text_to_speech:
        Optional callable that vocalises text output.
    """

    def __init__(
        self,
        orchestrator,
        speech_to_text: Optional[Callable[[], str]] = None,
        text_to_speech: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.speech_to_text = speech_to_text
        self.text_to_speech = text_to_speech

    # ------------------------------------------------------------------
    def _read_input(self) -> str:
        """Return user input either from keyboard or speech."""
        if self.speech_to_text is not None:
            return self.speech_to_text()
        return input("You: ")

    def _deliver_chunk(self, chunk: str) -> None:
        """Display one chunk of model output and optionally speak it."""
        print(chunk, end="", flush=True)
        if self.text_to_speech is not None:
            self.text_to_speech(chunk)

    def chat(self) -> None:
        """Main interactive chat loop."""
        while True:
            try:
                prompt = self._read_input()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not prompt:
                continue
            stream: Iterable[str] = self.orchestrator.stream_chat(prompt)
            for piece in stream:
                self._deliver_chunk(piece)
            print()
