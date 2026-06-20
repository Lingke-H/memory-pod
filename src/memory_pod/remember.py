"""Local write-back helpers for Memory Pod."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.embeddings import get_embedder
from memory_pod.memory_store import MemoryRecord, upsert_records


def remember(
    text: str,
    profile: str = DEFAULT_PROFILE,
    tags: list[str] | None = None,
    source: str = "manual",
    profiles_root: Path = PROFILES_DIR,
) -> MemoryRecord:
    """Write one local memory record into the user's local profile store."""

    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Cannot remember empty text.")

    local_embedder = get_embedder()
    vector = local_embedder.embed([cleaned_text])[0]
    record = MemoryRecord(
        id=make_memory_id(profile=profile, source=source, text=cleaned_text),
        type="manual_memory",
        text=cleaned_text,
        tags=list(tags or []),
        weight=1.0,
        created_at=datetime.now(UTC).isoformat(),
        source=source,
        embedder=local_embedder.identity,
        embedding=vector.astype(float).tolist(),
    )
    upsert_records(profile, [record], profiles_root)
    return record


def make_memory_id(profile: str, source: str, text: str) -> str:
    digest = hashlib.sha256(f"{profile}:{source}:{text}".encode("utf-8")).hexdigest()[:16]
    return f"manual_{digest}"
