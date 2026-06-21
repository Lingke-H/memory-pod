"""Portable Pod metadata, storage, import, export, and migration."""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import numpy as np

from memory_pod.config import (
    LEGACY_PROFILES_DIR,
    POD_MANIFEST_FILENAME,
    PODS_DIR,
)
from memory_pod.embeddings import Embedder, get_embedder
from memory_pod.memory_store import (
    MemoryRecord,
    load_records,
    profile_dir,
    store_path,
    write_records,
)

PORTABLE_FORMAT = "memory-pod"
PORTABLE_SCHEMA_VERSION = 1
MAX_PORTABLE_BYTES = 1024 * 1024
MAX_PORTABLE_RECORDS = 200
MAX_PORTABLE_TEXT_CHARS = 4000
POD_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
LOGGER = logging.getLogger("memory_pod.pods")


@dataclass(frozen=True)
class PodManifest:
    id: str
    name: str
    kind: Literal["private", "shared"] = "private"
    author: str = ""
    purpose: str = ""
    version: str = "1.0"
    read_only: bool = False
    origin: Literal["local", "imported"] = "local"
    created_at: str = ""
    content_hash: str | None = None

    @classmethod
    def from_json(cls, payload: dict) -> "PodManifest":
        pod_id = _validate_pod_id(str(payload["id"]))
        kind = str(payload.get("kind", "private"))
        origin = str(payload.get("origin", "local"))
        if kind not in {"private", "shared"}:
            raise ValueError(f"Unsupported Pod kind: {kind}")
        if origin not in {"local", "imported"}:
            raise ValueError(f"Unsupported Pod origin: {origin}")
        name = str(payload.get("name", pod_id)).strip()
        if not name:
            raise ValueError("Pod name cannot be empty.")
        return cls(
            id=pod_id,
            name=name,
            kind=kind,
            author=str(payload.get("author", "")),
            purpose=str(payload.get("purpose", "")),
            version=str(payload.get("version", "1.0")),
            read_only=bool(payload.get("read_only", False)),
            origin=origin,
            created_at=str(payload.get("created_at", "")),
            content_hash=payload.get("content_hash"),
        )

    def to_json(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class PodStack:
    base_pod: str
    shared_pod: str | None = None

    @property
    def active_pods(self) -> tuple[str, ...]:
        return (self.base_pod,) + ((self.shared_pod,) if self.shared_pod else ())


@dataclass(frozen=True)
class PortablePod:
    manifest: PodManifest
    records: list[dict]
    content_hash: str
    source_path: Path


def pod_manifest_path(pod_id: str, pods_root: Path = PODS_DIR) -> Path:
    return profile_dir(_validate_pod_id(pod_id), pods_root) / POD_MANIFEST_FILENAME


def create_pod(
    name: str,
    kind: Literal["private", "shared"] = "private",
    author: str = "",
    purpose: str = "",
    pod_id: str | None = None,
    pods_root: Path = PODS_DIR,
) -> PodManifest:
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("Pod name cannot be empty.")
    clean_id = _validate_pod_id(pod_id or _slugify(clean_name))
    if kind not in {"private", "shared"}:
        raise ValueError(f"Unsupported Pod kind: {kind}")

    path = profile_dir(clean_id, pods_root)
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Pod '{clean_id}' already exists.")

    manifest = PodManifest(
        id=clean_id,
        name=clean_name,
        kind=kind,
        author=author.strip(),
        purpose=purpose.strip(),
        created_at=datetime.now(UTC).isoformat(),
    )
    _write_manifest(manifest, pods_root)
    return manifest


def get_pod_manifest(pod_id: str, pods_root: Path = PODS_DIR) -> PodManifest | None:
    clean_id = _validate_pod_id(pod_id)
    path = pod_manifest_path(clean_id, pods_root)
    if path.exists():
        return PodManifest.from_json(json.loads(path.read_text(encoding="utf-8")))

    legacy_dir = profile_dir(clean_id, pods_root)
    if legacy_dir.exists() and store_path(clean_id, pods_root).exists():
        return PodManifest(id=clean_id, name=clean_id.replace("-", " ").title())
    return None


def list_pods(pods_root: Path = PODS_DIR) -> list[PodManifest]:
    if not pods_root.exists():
        return []
    manifests = []
    for child in sorted(pods_root.iterdir()):
        if not child.is_dir() or not POD_ID_RE.fullmatch(child.name):
            continue
        try:
            manifest = get_pod_manifest(child.name, pods_root)
        except (OSError, KeyError, TypeError, ValueError) as exc:
            LOGGER.warning("Skipping unreadable Pod manifest %s: %s", child.name, exc)
            continue
        if manifest is not None:
            manifests.append(manifest)
    return sorted(manifests, key=lambda item: (item.kind, item.name.lower()))


def export_pod(
    pod_id: str,
    output_path: Path | str,
    pods_root: Path = PODS_DIR,
) -> Path:
    manifest = _require_manifest(pod_id, pods_root)
    if manifest.kind != "shared" or manifest.origin != "local" or manifest.read_only:
        raise PermissionError("Only locally created, writable Shared Pods can be exported.")

    records = [_portable_record(record) for record in load_records(pod_id, pods_root)]
    portable_manifest = {
        "id": manifest.id,
        "name": manifest.name,
        "kind": "shared",
        "author": manifest.author,
        "purpose": manifest.purpose,
        "version": manifest.version,
        "created_at": manifest.created_at,
    }
    content_hash = _content_hash(portable_manifest, records)
    payload = {
        "format": PORTABLE_FORMAT,
        "schema_version": PORTABLE_SCHEMA_VERSION,
        "pod": portable_manifest,
        "records": records,
        "content_hash": content_hash,
    }

    path = Path(output_path).expanduser()
    if path.suffix.lower() != ".mpod":
        path = path.with_suffix(".mpod")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def inspect_pod(path: Path | str) -> PortablePod:
    source_path = Path(path).expanduser().resolve()
    raw = source_path.read_bytes()
    if len(raw) > MAX_PORTABLE_BYTES:
        raise ValueError("Pod file exceeds the 1 MiB MVP limit.")

    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Pod file must contain a JSON object.")
    if payload.get("format") != PORTABLE_FORMAT:
        raise ValueError("Not a Memory Pod file.")
    if payload.get("schema_version") != PORTABLE_SCHEMA_VERSION:
        raise ValueError("Unsupported Memory Pod schema version.")
    if not isinstance(payload.get("pod"), dict) or not isinstance(payload.get("records"), list):
        raise ValueError("Pod file must contain pod metadata and records.")
    if len(payload["records"]) > MAX_PORTABLE_RECORDS:
        raise ValueError("Pod file exceeds the 200-record MVP limit.")

    portable_manifest = dict(payload["pod"])
    if portable_manifest.get("kind") != "shared":
        raise ValueError("Portable Pods must declare kind='shared'.")
    portable_manifest["kind"] = "shared"
    portable_manifest["origin"] = "imported"
    portable_manifest["read_only"] = True
    manifest = PodManifest.from_json(portable_manifest)
    records = [_validate_portable_record(item) for item in payload["records"]]
    expected_hash = _content_hash(payload["pod"], records)
    if payload.get("content_hash") != expected_hash:
        raise ValueError("Pod content hash does not match its contents.")

    return PortablePod(
        manifest=manifest,
        records=records,
        content_hash=expected_hash,
        source_path=source_path,
    )


def import_pod(
    path: Path | str,
    replace: bool = False,
    pods_root: Path = PODS_DIR,
    embedder: Embedder | None = None,
) -> PodManifest:
    portable = inspect_pod(path)
    existing = get_pod_manifest(portable.manifest.id, pods_root)
    if existing is not None:
        if existing.content_hash == portable.content_hash:
            return existing
        if existing.origin != "imported":
            raise FileExistsError(
                f"A local Pod named '{portable.manifest.id}' already exists and cannot be replaced."
            )
        if not replace:
            raise FileExistsError(
                f"Imported Pod '{portable.manifest.id}' already exists; use replace=True to update it."
            )

    local_embedder = embedder or get_embedder()
    texts = [record["text"] for record in portable.records]
    vectors = np.asarray(local_embedder.embed(texts), dtype=np.float32)
    if vectors.ndim != 2 or vectors.shape[0] != len(texts) or not np.all(np.isfinite(vectors)):
        raise ValueError("Local embedder returned invalid vectors while importing Pod.")

    records = []
    for item, vector in zip(portable.records, vectors, strict=True):
        source_label = item.get("source_label")
        source = f"mpod:{portable.manifest.id}"
        if source_label:
            source = f"{source}:{source_label}"
        records.append(
            MemoryRecord(
                id=item["id"],
                type=item["type"],
                text=item["text"],
                tags=item["tags"],
                weight=item["weight"],
                created_at=item["created_at"],
                source=source,
                embedder=local_embedder.identity,
                embedding=vector.astype(float).tolist(),
            )
        )

    imported_manifest = PodManifest(
        **{
            **portable.manifest.to_json(),
            "content_hash": portable.content_hash,
        }
    )
    write_records(imported_manifest.id, records, pods_root)
    _write_manifest(imported_manifest, pods_root)
    return imported_manifest


def migrate_legacy_profiles(
    legacy_root: Path = LEGACY_PROFILES_DIR,
    pods_root: Path = PODS_DIR,
) -> list[PodManifest]:
    if not legacy_root.exists() or legacy_root.resolve() == pods_root.resolve():
        return []

    migrated = []
    for child in sorted(legacy_root.iterdir()):
        if not child.is_dir() or not POD_ID_RE.fullmatch(child.name):
            continue
        if not store_path(child.name, legacy_root).exists():
            continue
        if get_pod_manifest(child.name, pods_root) is not None:
            continue

        records = load_records(child.name, legacy_root)
        write_records(child.name, records, pods_root)
        manifest = PodManifest(
            id=child.name,
            name=child.name.replace("-", " ").title(),
            created_at=datetime.now(UTC).isoformat(),
        )
        _write_manifest(manifest, pods_root)
        migrated.append(manifest)
    return migrated


def pod_is_writable(pod_id: str, pods_root: Path = PODS_DIR) -> bool:
    try:
        manifest = get_pod_manifest(pod_id, pods_root)
    except (OSError, KeyError, TypeError, ValueError):
        return False
    return manifest is None or not manifest.read_only


def _require_manifest(pod_id: str, pods_root: Path) -> PodManifest:
    manifest = get_pod_manifest(pod_id, pods_root)
    if manifest is None:
        raise FileNotFoundError(f"Pod '{pod_id}' does not exist.")
    return manifest


def _write_manifest(manifest: PodManifest, pods_root: Path) -> Path:
    path = pod_manifest_path(manifest.id, pods_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.to_json(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def _portable_record(record: MemoryRecord) -> dict:
    source_label = None
    if record.source:
        source_label = Path(record.source).name
    return {
        "id": record.id,
        "type": record.type,
        "text": record.text,
        "tags": list(record.tags),
        "weight": record.weight,
        "created_at": record.created_at,
        "source_label": source_label,
    }


def _validate_portable_record(payload: object) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Every Pod record must be an object.")
    text = str(payload.get("text", "")).strip()
    if not text:
        raise ValueError("Pod records cannot contain empty text.")
    if len(text) > MAX_PORTABLE_TEXT_CHARS:
        raise ValueError("Pod record exceeds the 4,000-character MVP limit.")
    record_id = str(payload.get("id", "")).strip()
    if not record_id:
        raise ValueError("Pod records require an id.")
    tags = payload.get("tags", [])
    if not isinstance(tags, list):
        raise ValueError("Pod record tags must be a list.")
    weight = float(payload.get("weight", 1.0))
    if not np.isfinite(weight):
        raise ValueError("Pod record weight must be finite.")
    source_label = payload.get("source_label")
    if source_label is not None:
        source_label = Path(str(source_label)).name
    return {
        "id": record_id,
        "type": str(payload.get("type", "note_chunk")),
        "text": text,
        "tags": [str(tag) for tag in tags],
        "weight": weight,
        "created_at": str(payload.get("created_at", datetime.now(UTC).isoformat())),
        "source_label": source_label,
    }


def _content_hash(pod_payload: dict, records: list[dict]) -> str:
    canonical = json.dumps(
        {"pod": pod_payload, "records": records},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_pod_id(pod_id: str) -> str:
    if not POD_ID_RE.fullmatch(pod_id):
        raise ValueError(
            "Pod id must use lowercase letters, numbers, and hyphens (maximum 64 characters)."
        )
    return pod_id


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:64]
    if not slug:
        raise ValueError("Pod name must contain at least one letter or number.")
    return slug
