"""Sample connector for a weather API."""
from __future__ import annotations

from typing import Dict

from .external_service import ExternalService


class WeatherService(ExternalService):
    """Retrieve weather information for a location."""

    def __init__(self, orchestrator, token: str | None = None, rate_limit: int = 60) -> None:
        super().__init__(token=token, rate_limit=rate_limit)
        orchestrator.register_skill("weather.get_forecast", self.get_forecast)

    # ------------------------------------------------------------------
    def get_forecast(self, location: str) -> Dict[str, str]:
        """Return a simple forecast for ``location``."""
        self._check_rate_limit()
        return {"location": location, "forecast": "sunny"}
