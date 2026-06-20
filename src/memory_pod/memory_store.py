"""Local JSONL memory storage."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from memory_pod.config import MEMORY_STORE_FILENAME, PROFILES_DIR


@dataclass
class MemoryRecord:
    id: str
    text: str
    type: str = "note_chunk"
    tags: list[str] = field(default_factory=list)
    weight: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    source: str | None = None
    embedder: str | None = None
    embedding: list[float] | None = None

    @classmethod
    def from_json(cls, payload: dict) -> "MemoryRecord":
        return cls(
            id=str(payload["id"]),
            text=str(payload["text"]),
            type=str(payload.get("type", "note_chunk")),
            tags=list(payload.get("tags", [])),
            weight=float(payload.get("weight", 1.0)),
            created_at=str(payload.get("created_at", datetime.now(UTC).isoformat())),
            source=payload.get("source"),
            embedder=payload.get("embedder"),
            embedding=payload.get("embedding"),
        )

    def to_json(self) -> dict:
        return asdict(self)


def profile_dir(profile: str, profiles_root: Path = PROFILES_DIR) -> Path:
    return profiles_root / profile


def store_path(profile: str, profiles_root: Path = PROFILES_DIR) -> Path:
    return profile_dir(profile, profiles_root) / MEMORY_STORE_FILENAME


def load_records(profile: str, profiles_root: Path = PROFILES_DIR) -> list[MemoryRecord]:
    path = store_path(profile, profiles_root)
    if not path.exists():
        return []

    records: list[MemoryRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(MemoryRecord.from_json(json.loads(line)))
    return records


def write_records(
    profile: str,
    records: Iterable[MemoryRecord],
    profiles_root: Path = PROFILES_DIR,
) -> Path:
    path = store_path(profile, profiles_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record.to_json(), ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return path


def upsert_records(
    profile: str,
    new_records: Iterable[MemoryRecord],
    profiles_root: Path = PROFILES_DIR,
) -> Path:
    existing = {record.id: record for record in load_records(profile, profiles_root)}
    for record in new_records:
        existing[record.id] = record
    return write_records(profile, existing.values(), profiles_root)
