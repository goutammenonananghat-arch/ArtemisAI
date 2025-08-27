"""Simple secrets manager with XOR-based encryption.

This module provides a ``SecretsManager`` class capable of storing
and retrieving credentials in an encrypted file.  It avoids external
dependencies by using a very small XOR cipher.  While this should not
be considered production‑grade cryptography, it satisfies environments
where third‑party packages are unavailable.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional


class SecretsManager:
    """Store and retrieve secrets with basic symmetric encryption.

    Parameters
    ----------
    key_path: str or Path
        Location where the encryption key is stored.
    storage_path: str or Path
        File path where encrypted secrets are persisted.
    """

    def __init__(self, key_path: str | Path = "secret.key", storage_path: str | Path = "secrets.dat") -> None:
        self.key_path = Path(key_path)
        self.storage_path = Path(storage_path)
        self.key = self._load_or_create_key()

    # ------------------------------------------------------------------
    # Key management
    def _load_or_create_key(self) -> bytes:
        """Return the encryption key, creating one if missing."""
        if self.key_path.exists():
            return self.key_path.read_bytes()
        key = os.urandom(32)
        self.key_path.write_bytes(key)
        return key

    # ------------------------------------------------------------------
    # Encryption helpers
    def _xor_bytes(self, data: bytes) -> bytes:
        """XOR ``data`` with the secret key.

        This function both encrypts and decrypts since XOR is symmetric.
        """
        key = self.key
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    # ------------------------------------------------------------------
    # Persistence helpers
    def _load_all(self) -> Dict[str, str]:
        if not self.storage_path.exists():
            return {}
        encrypted = self.storage_path.read_bytes()
        decrypted = self._xor_bytes(encrypted)
        return json.loads(decrypted.decode("utf-8"))

    def _save_all(self, data: Dict[str, str]) -> None:
        raw = json.dumps(data).encode("utf-8")
        encrypted = self._xor_bytes(raw)
        self.storage_path.write_bytes(encrypted)

    # ------------------------------------------------------------------
    # Public API
    def store(self, name: str, secret: str) -> None:
        """Store a secret under ``name``."""
        data = self._load_all()
        data[name] = secret
        self._save_all(data)

    def retrieve(self, name: str) -> Optional[str]:
        """Retrieve secret ``name`` if present."""
        data = self._load_all()
        return data.get(name)
