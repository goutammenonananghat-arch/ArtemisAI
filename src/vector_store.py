"""Semantic vector store using FAISS when available with JSON fallback."""
from __future__ import annotations

import json
import math
import hashlib
from pathlib import Path
from typing import Any, Dict, List

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
    import numpy as np  # type: ignore
    _FAISS = True
except Exception:  # pragma: no cover - faiss absent
    faiss = None  # type: ignore
    np = None  # type: ignore
    _FAISS = False


class VectorStore:
    """Persisted store supporting rudimentary semantic search."""

    def __init__(self, path: Path, dim: int = 128) -> None:
        self.path = path
        self.dim = dim
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.vectors: List[List[float]] = []
        self.use_faiss = _FAISS
        if self.use_faiss:
            self.index = faiss.IndexFlatIP(dim)  # type: ignore[assignment]
        self._load()

    # ------------------------------------------------------------------
    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for token in text.lower().split():
            h = int(hashlib.md5(token.encode()).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm:
            vec = [v / norm for v in vec]
        return vec

    # ------------------------------------------------------------------
    def _load(self) -> None:
        if not self.path.exists():
            return
        data = json.loads(self.path.read_text())
        self.texts = data.get("texts", [])
        self.metadatas = data.get("metadatas", [])
        self.vectors = data.get("vectors", [])
        if self.use_faiss and self.vectors:
            arr = np.array(self.vectors, dtype="float32")  # type: ignore[call-arg]
            self.index.add(arr)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"texts": self.texts, "metadatas": self.metadatas, "vectors": self.vectors}
        self.path.write_text(json.dumps(data))

    # ------------------------------------------------------------------
    def add(self, text: str, metadata: Dict[str, Any] | None = None) -> None:
        metadata = metadata or {}
        emb = self._embed(text)
        self.texts.append(text)
        self.metadatas.append(metadata)
        self.vectors.append(emb)
        if self.use_faiss:
            self.index.add(np.array([emb], dtype="float32"))  # type: ignore[call-arg]
        self._save()

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.texts:
            return []
        emb = self._embed(query)
        if self.use_faiss:
            scores, idxs = self.index.search(np.array([emb], dtype="float32"), top_k)  # type: ignore[call-arg]
            results = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx == -1:
                    continue
                results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadatas[idx],
                    "score": float(score),
                })
            return results
        scores = [sum(a * b for a, b in zip(emb, vec)) for vec in self.vectors]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [
            {"text": self.texts[i], "metadata": self.metadatas[i], "score": float(s)}
            for i, s in ranked
        ]
