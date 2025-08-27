"""Simple persistent key/value store backed by JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class KVStore:
    """A tiny JSON backed key/value store."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text())

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data))

    def set(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key`` and persist immediately."""
        self.data[key] = value
        self._save()

    def get(self, key: str, default: Any | None = None) -> Any:
        """Retrieve a value by ``key`` returning ``default`` when missing."""
        return self.data.get(key, default)
