"""Sample connector for Google Calendar."""
from __future__ import annotations

from typing import Dict, List

from .external_service import ExternalService


class GoogleCalendarService(ExternalService):
    """Fetch events from a Google Calendar."""

    def __init__(self, orchestrator, token: str, rate_limit: int = 60) -> None:
        super().__init__(token=token, rate_limit=rate_limit)
        # Register as a skill for the orchestrator
        orchestrator.register_skill("google_calendar.list_events", self.list_events)

    # ------------------------------------------------------------------
    def list_events(self) -> List[Dict[str, str]]:
        """Return a list of upcoming events.

        This implementation returns static data as an example.
        """
        self._check_rate_limit()
        if not self.token:
            raise RuntimeError("Missing auth token")
        return [
            {"summary": "Team Standup", "time": "2023-09-30T10:00:00"},
            {"summary": "Dentist Appointment", "time": "2023-09-30T15:00:00"},
        ]
