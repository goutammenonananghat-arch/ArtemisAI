"""Base class for connectors to external APIs."""
from __future__ import annotations

import time
from typing import Optional


class ExternalService:
    """Handle auth tokens and simple rate limiting.

    Parameters
    ----------
    token:
        Authentication token used for API requests.
    rate_limit:
        Maximum number of calls allowed per minute.
    """

    def __init__(self, token: Optional[str] = None, rate_limit: int = 60) -> None:
        self.token = token
        self.rate_limit = rate_limit
        self._call_times: list[float] = []

    # ------------------------------------------------------------------
    def authenticate(self, token: str) -> None:
        """Store a token for later requests."""
        self.token = token

    # ------------------------------------------------------------------
    def _check_rate_limit(self) -> None:
        """Raise ``RuntimeError`` if the rate limit is exceeded."""
        now = time.time()
        self._call_times = [t for t in self._call_times if now - t < 60]
        if len(self._call_times) >= self.rate_limit:
            raise RuntimeError("Rate limit exceeded")
        self._call_times.append(now)
