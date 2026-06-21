"""Seed persistent Pods for the live Pod Dock demo."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from memory_pod.config import PODS_DIR, REPO_ROOT
from memory_pod.embeddings import Embedder, get_embedder
from memory_pod.memory_store import MemoryRecord, write_records
from memory_pod.pods import create_pod, export_pod, get_pod_manifest


@dataclass(frozen=True)
class DemoSetupResult:
    pods_root: Path
    export_path: Path


def seed_pod_demo(
    pods_root: Path = PODS_DIR,
    export_path: Path | None = None,
    embedder: Embedder | None = None,
) -> DemoSetupResult:
    """Create deterministic live demo Pods in the same store used by the popup."""

    export_path = export_path or (REPO_ROOT / "dist" / "senior-review.mpod")
    local_embedder = embedder or get_embedder()

    _ensure_pod("Jiahan", "private", "jiahan", pods_root)
    _ensure_pod(
        "Senior Architecture Review",
        "shared",
        "senior-review",
        pods_root,
        author="Alice",
        purpose="Review API and system architecture decisions",
    )

    _write_embedded_records(
        "jiahan",
        [
            (
                "base-1",
                "Jiahan is a backend engineer designing REST and gRPC APIs for a payments platform.",
                ["identity", "api"],
                "profile_fact",
            ),
            (
                "base-2",
                "Jiahan's current project is redesigning the checkout service API with backward compatibility in mind.",
                ["project", "api"],
                "project_fact",
            ),
            (
                "base-3",
                "Jiahan prefers concise, example-driven explanations of API tradeoffs over long essays.",
                ["preference", "style"],
                "preference",
            ),
        ],
        pods_root,
        local_embedder,
    )
    _write_embedded_records(
        "senior-review",
        [
            (
                "review-1",
                "Before approving an API design, enumerate failure modes and ownership boundaries.",
                ["api", "review"],
                "principle",
            ),
            (
                "review-2",
                "Prefer explicit interfaces over shared mutable state in system architecture.",
                ["architecture", "interfaces"],
                "principle",
            ),
            (
                "review-3",
                "For database migrations, define rollback behavior before changing production data.",
                ["database", "migration"],
                "principle",
            ),
        ],
        pods_root,
        local_embedder,
    )

    exported = export_pod("senior-review", export_path, pods_root)
    return DemoSetupResult(pods_root=pods_root, export_path=exported)


def _ensure_pod(
    name: str,
    kind: str,
    pod_id: str,
    pods_root: Path,
    author: str = "",
    purpose: str = "",
) -> None:
    manifest = get_pod_manifest(pod_id, pods_root)
    if manifest is None:
        create_pod(
            name,
            kind=kind,  # type: ignore[arg-type]
            author=author,
            purpose=purpose,
            pod_id=pod_id,
            pods_root=pods_root,
        )
        return
    if manifest.kind != kind or manifest.read_only:
        raise PermissionError(
            f"Pod '{pod_id}' already exists but is not a writable local {kind} Pod."
        )


def _write_embedded_records(
    pod_id: str,
    items: list[tuple[str, str, list[str], str]],
    pods_root: Path,
    embedder: Embedder,
) -> None:
    texts = [text for _, text, _, _ in items]
    vectors = embedder.embed(texts)
    records = []
    for (record_id, text, tags, record_type), vector in zip(items, vectors, strict=True):
        records.append(
            MemoryRecord(
                id=record_id,
                type=record_type,
                text=text,
                tags=tags,
                source="demo-setup",
                embedder=embedder.identity,
                embedding=vector.astype(float).tolist(),
            )
        )
    write_records(pod_id, records, pods_root)


def main() -> None:
    result = seed_pod_demo()
    print(f"Seeded live Pod Dock data in: {result.pods_root}")
    print(f"Exported demo Shared Pod: {result.export_path}")
    print("Next: run `make popup`, then choose Base `jiahan` and Shared `senior-review`.")


if __name__ == "__main__":
    main()
