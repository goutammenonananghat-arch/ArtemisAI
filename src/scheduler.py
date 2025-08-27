"""Very small scheduler capable of sending delayed alerts."""

from __future__ import annotations

import threading
import time

from alerts import send


class Scheduler:
    """Execute callbacks after a delay."""

    def alert_in(self, delay: float, channel: str, message: str) -> None:
        """Send ``message`` to ``channel`` after ``delay`` seconds."""

        def _task() -> None:
            time.sleep(delay)
            send(channel, message)

        threading.Thread(target=_task, daemon=True).start()

