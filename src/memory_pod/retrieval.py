"""Top-k local memory retrieval."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from memory_pod.embeddings import Embedder, get_embedder, lexical_keys
from memory_pod.config import PROFILES_DIR
from memory_pod.memory_store import MemoryRecord, load_records

LOGGER = logging.getLogger("memory_pod.retrieval")
DEFAULT_MIN_RELEVANCE_SCORE = 0.025


@dataclass(frozen=True)
class RetrievalResult:
    record: MemoryRecord
    score: float
    pod_id: str | None = None


def retrieve(
    raw_prompt: str,
    profile: str,
    top_k: int = 5,
    embedder: Embedder | None = None,
    profiles_root: Path = PROFILES_DIR,
    min_score: float = DEFAULT_MIN_RELEVANCE_SCORE,
) -> list[RetrievalResult]:
    if not raw_prompt.strip() or top_k <= 0:
        return []

    try:
        records = [
            record for record in load_records(profile, profiles_root) if record.text.strip()
        ]
    except (OSError, KeyError, TypeError, ValueError) as exc:
        LOGGER.warning("Could not read local memories for profile %s: %s", profile, exc)
        return []
    if not records:
        return []

    local_embedder = embedder or get_embedder()
    try:
        embedded_query = local_embedder.embed([raw_prompt])
    except Exception as exc:
        LOGGER.warning("Embedder %s could not embed the query: %s", local_embedder.identity, exc)
        return []
    query_vectors = _valid_embeddings(embedded_query, expected_rows=1)
    if query_vectors is None:
        LOGGER.warning("Embedder %s returned an invalid query vector.", local_embedder.identity)
        return []

    query_vector = query_vectors[0]
    query_norm = np.linalg.norm(query_vector)
    if query_norm == 0:
        return []
    query_vector = query_vector / query_norm

    memory_vectors = _memory_vectors(
        records,
        local_embedder,
        expected_dimensions=query_vector.size,
    )
    if memory_vectors is None:
        return []

    scores = memory_vectors @ query_vector
    weights = np.array([record.weight for record in records], dtype=np.float32)
    weighted_scores = np.full_like(scores, -np.inf)
    valid_weights = np.isfinite(weights)
    weighted_scores[valid_weights] = scores[valid_weights] * weights[valid_weights]
    if local_embedder.identity.startswith("hashing-v1:"):
        query_keys = lexical_keys(raw_prompt)
        lexical_matches = np.array(
            [bool(query_keys & lexical_keys(record.text)) for record in records]
        )
        weighted_scores[~lexical_matches] = -np.inf
    best_indexes = np.argsort(weighted_scores)[::-1][:top_k]

    return [
        RetrievalResult(
            record=records[index],
            score=float(weighted_scores[index]),
            pod_id=profile,
        )
        for index in best_indexes
        if np.isfinite(weighted_scores[index]) and float(weighted_scores[index]) >= min_score
    ]


def _memory_vectors(
    records: list[MemoryRecord],
    embedder: Embedder,
    expected_dimensions: int,
) -> np.ndarray | None:
    active_embedder = embedder.identity
    cached_vectors = [
        _cached_vector(record, active_embedder, expected_dimensions) for record in records
    ]
    texts_to_embed = [
        record.text for record, vector in zip(records, cached_vectors) if vector is None
    ]
    if texts_to_embed:
        try:
            embedded_memories = embedder.embed(texts_to_embed)
        except Exception as exc:
            LOGGER.warning("Embedder %s could not embed local memories: %s", active_embedder, exc)
            return None
        fresh_embeddings = _valid_embeddings(
            embedded_memories,
            expected_rows=len(texts_to_embed),
            expected_dimensions=expected_dimensions,
        )
    else:
        fresh_embeddings = np.zeros((0, expected_dimensions), dtype=np.float32)
    if fresh_embeddings is None:
        LOGGER.warning("Embedder %s returned invalid memory vectors.", active_embedder)
        return None
    fresh_vectors = iter(fresh_embeddings)

    vectors = []
    for record, cached_vector in zip(records, cached_vectors):
        if cached_vector is None:
            if record.embedding is not None and record.embedder != active_embedder:
                LOGGER.info(
                    "Re-embedding memory %s because it was stored with %s but active embedder is %s.",
                    record.id,
                    record.embedder,
                    active_embedder,
                )
            elif record.embedding is not None:
                LOGGER.info("Re-embedding memory %s because its cached vector is invalid.", record.id)
            vector = next(fresh_vectors)
        else:
            vector = cached_vector
        norm = np.linalg.norm(vector)
        vectors.append(vector / norm if norm > 0 else vector)

    return np.vstack(vectors).astype(np.float32)


def _cached_vector(
    record: MemoryRecord,
    active_embedder: str,
    expected_dimensions: int,
) -> np.ndarray | None:
    if record.embedding is None or record.embedder != active_embedder:
        return None

    try:
        vector = np.asarray(record.embedding, dtype=np.float32)
    except (TypeError, ValueError):
        return None
    if (
        vector.ndim != 1
        or vector.size != expected_dimensions
        or not np.all(np.isfinite(vector))
    ):
        return None
    return vector


def _valid_embeddings(
    embeddings: object,
    expected_rows: int,
    expected_dimensions: int | None = None,
) -> np.ndarray | None:
    try:
        vectors = np.asarray(embeddings, dtype=np.float32)
    except (TypeError, ValueError):
        return None
    if (
        vectors.ndim != 2
        or vectors.shape[0] != expected_rows
        or vectors.shape[1] == 0
        or (expected_dimensions is not None and vectors.shape[1] != expected_dimensions)
        or not np.all(np.isfinite(vectors))
    ):
        return None
    return vectors
