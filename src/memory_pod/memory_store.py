"""Local JSONL memory storage."""

from __future__ import annotations

import json
import tempfile
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
    payload = "\n".join(lines) + ("\n" if lines else "")
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_file.write(payload)
        temp_path = Path(temp_file.name)
    temp_path.replace(path)
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


def replace_records_for_sources(
    profile: str,
    sources: set[str],
    new_records: Iterable[MemoryRecord],
    profiles_root: Path = PROFILES_DIR,
) -> Path:
    replacement = list(new_records)
    existing = []
    for record in load_records(profile, profiles_root):
        if record.type == "manual_memory" or record.source == "manual":
            existing.append(record)
            continue
        if record.source in sources:
            continue
        existing.append(record)
    return write_records(profile, [*existing, *replacement], profiles_root)
