"""Memory API combining key/value and semantic stores with decay."""
from __future__ import annotations

import math
import time
from pathlib import Path
from typing import List

from kv_store import KVStore
from vector_store import VectorStore

DATA_DIR = Path("data")
KV_PATH = DATA_DIR / "kv_store.json"
VEC_PATH = DATA_DIR / "vector_store.json"
DECAY_SECONDS = 60 * 60 * 24  # one day

_kv = KVStore(KV_PATH)
_vec = VectorStore(VEC_PATH)


def _decay(ts: float, now: float) -> float:
    return math.exp(-(now - ts) / DECAY_SECONDS)


def write_memory(key: str, text: str) -> None:
    """Persist ``text`` under ``key`` and index for semantic search."""
    ts = time.time()
    _kv.set(key, {"text": text, "timestamp": ts})
    _vec.add(text, {"key": key, "timestamp": ts})


def retrieve_memory(query: str, top_k: int = 5) -> List[str]:
    """Retrieve memories relevant to ``query`` with time decay."""
    now = time.time()
    results = []
    item = _kv.get(query)
    if isinstance(item, dict) and "timestamp" in item:
        results.append({"text": item["text"], "score": _decay(item["timestamp"], now)})
    for res in _vec.search(query, top_k):
        ts = res.get("metadata", {}).get("timestamp", now)
        score = res["score"] * _decay(ts, now)
        results.append({"text": res["text"], "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return [r["text"] for r in results[:top_k]]
