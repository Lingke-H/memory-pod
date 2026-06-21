"""Ingest local `.md` and `.txt` files into the local memory store."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from memory_pod.config import PROFILES_DIR, SUPPORTED_INGEST_SUFFIXES
from memory_pod.embeddings import Embedder, get_embedder
from memory_pod.memory_store import (
    MemoryRecord,
    load_records,
    replace_records_for_sources,
)


@dataclass(frozen=True)
class IngestResult:
    profile: str
    records_written: int
    store_path: Path


def ingest_path(
    profile: str,
    source_path: Path | str,
    profiles_root: Path = PROFILES_DIR,
    embedder: Embedder | None = None,
) -> IngestResult:
    """Read local text files, chunk them, embed chunks, and upsert records."""

    path = Path(source_path).expanduser().resolve()
    files = list(iter_text_files(path))
    if not files:
        raise FileNotFoundError(f"No .md or .txt files found at {path}")
    sources_to_replace = _sources_to_replace(profile, path, files, profiles_root)

    chunks: list[tuple[Path, str]] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        for chunk in chunk_text(text):
            chunks.append((file_path, chunk))

    local_embedder = embedder or get_embedder()
    vectors = local_embedder.embed(chunk for _, chunk in chunks)
    embedder_id = local_embedder.identity

    records = []
    for (file_path, chunk), vector in zip(chunks, vectors, strict=True):
        records.append(
            MemoryRecord(
                id=make_record_id(file_path, chunk),
                type="note_chunk",
                text=chunk,
                tags=[file_path.stem],
                weight=1.0,
                created_at=datetime.now(UTC).isoformat(),
                source=str(file_path),
                embedder=embedder_id,
                embedding=vector.astype(float).tolist(),
            )
        )

    written_path = replace_records_for_sources(
        profile,
        sources_to_replace,
        records,
        profiles_root,
    )
    return IngestResult(profile=profile, records_written=len(records), store_path=written_path)


def iter_text_files(path: Path) -> Iterable[Path]:
    if path.is_file() and path.suffix.lower() in SUPPORTED_INGEST_SUFFIXES:
        yield path
        return

    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if child.is_file() and child.suffix.lower() in SUPPORTED_INGEST_SUFFIXES:
                yield child


def chunk_text(text: str, max_chars: int = 900) -> list[str]:
    """Split Markdown-ish text by headings and paragraphs."""

    sections = re.split(r"\n(?=#{1,6}\s+)", text)
    chunks: list[str] = []
    for section in sections:
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", section) if part.strip()]
        current = ""
        for paragraph in paragraphs:
            if not current:
                current = paragraph
            elif len(current) + len(paragraph) + 2 <= max_chars:
                current = f"{current}\n\n{paragraph}"
            else:
                chunks.append(current)
                current = paragraph
        if current:
            chunks.append(current)

    return [chunk for chunk in chunks if chunk.strip()]


def make_record_id(file_path: Path, chunk: str) -> str:
    digest = hashlib.sha256(f"{file_path}:{chunk}".encode("utf-8")).hexdigest()[:16]
    return f"chunk_{digest}"


def _sources_to_replace(
    profile: str,
    source_path: Path,
    files: list[Path],
    profiles_root: Path,
) -> set[str]:
    sources = {str(file_path) for file_path in files}
    if source_path.is_file():
        return sources

    root = source_path.resolve()
    for record in load_records(profile, profiles_root):
        if record.type == "manual_memory" or not record.source or record.source == "manual":
            continue
        try:
            source = Path(record.source).resolve()
        except (OSError, RuntimeError):
            continue
        if source == root or root in source.parents:
            sources.add(record.source)
    return sources
