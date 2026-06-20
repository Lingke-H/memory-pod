"""Top-k local memory retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from memory_pod.embeddings import Embedder, get_embedder
from memory_pod.config import PROFILES_DIR
from memory_pod.memory_store import MemoryRecord, load_records


@dataclass(frozen=True)
class RetrievalResult:
    record: MemoryRecord
    score: float


def retrieve(
    raw_prompt: str,
    profile: str,
    top_k: int = 5,
    embedder: Embedder | None = None,
    profiles_root: Path = PROFILES_DIR,
) -> list[RetrievalResult]:
    records = [record for record in load_records(profile, profiles_root) if record.text.strip()]
    if not records:
        return []

    local_embedder = embedder or get_embedder()
    query_vector = local_embedder.embed([raw_prompt])[0]
    memory_vectors = _memory_vectors(records, local_embedder)

    scores = memory_vectors @ query_vector
    weighted_scores = scores * np.array([record.weight for record in records], dtype=np.float32)
    best_indexes = np.argsort(weighted_scores)[::-1][:top_k]

    return [
        RetrievalResult(record=records[index], score=float(weighted_scores[index]))
        for index in best_indexes
        if float(weighted_scores[index]) > 0
    ]


def _memory_vectors(records: list[MemoryRecord], embedder: Embedder) -> np.ndarray:
    missing_texts = [record.text for record in records if record.embedding is None]
    missing_vectors = iter(embedder.embed(missing_texts)) if missing_texts else iter(())

    vectors = []
    for record in records:
        if record.embedding is None:
            vector = next(missing_vectors)
        else:
            vector = np.array(record.embedding, dtype=np.float32)
        norm = np.linalg.norm(vector)
        vectors.append(vector / norm if norm > 0 else vector)

    return np.vstack(vectors).astype(np.float32)
