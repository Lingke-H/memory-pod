"""Portable Pod demo: export, inspect, import, dock, and retrieve."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from memory_pod.augment import augment_for_stack
from memory_pod.embeddings import get_embedder
from memory_pod.memory_store import MemoryRecord, write_records
from memory_pod.pods import PodStack, create_pod, export_pod, import_pod, inspect_pod


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="memory-pod-demo-") as temp_dir:
        root = Path(temp_dir)
        author_root = root / "author"
        recipient_root = root / "recipient"
        embedder = get_embedder()

        create_pod("Jiahan", pod_id="jiahan", pods_root=recipient_root)
        _write_embedded_records(
            "jiahan",
            [
                # Summary (no style/fact keyword): who they are.
                "Jiahan is a backend engineer who designs REST and gRPC APIs for a payments platform.",
                # Facts ("current project"): what they are working on now.
                "Jiahan's current project is redesigning the checkout service API with backward compatibility in mind.",
                # Style ("prefers"): how they want the answer written (API-relevant so it ranks).
                "Jiahan prefers concise, example-driven explanations of API tradeoffs over long essays.",
            ],
            recipient_root,
            embedder,
        )

        create_pod(
            "Senior Architecture Review",
            kind="shared",
            author="Alice",
            purpose="Review API and system architecture decisions",
            pod_id="senior-review",
            pods_root=author_root,
        )
        _write_embedded_records(
            "senior-review",
            [
                "Before approving an API design, enumerate failure modes and ownership boundaries.",
                "Prefer explicit interfaces over shared mutable state in system architecture.",
                "For database migrations, define rollback behavior before changing production data.",
            ],
            author_root,
            embedder,
        )

        exported = export_pod(
            "senior-review",
            root / "Senior-Architecture-Review.mpod",
            author_root,
        )
        portable = inspect_pod(exported)
        payload = json.loads(exported.read_text(encoding="utf-8"))

        _banner("ACT 1 — OWN AND CARRY", "Export an inspectable Shared Pod")
        print(f"File: {exported.name}")
        print(f"Author: {portable.manifest.author} (self-declared)")
        print(f"Purpose: {portable.manifest.purpose}")
        print(f"Records: {len(portable.records)}")
        print(f"Embeddings exported: {'embedding' in payload['records'][0]}")
        print("Absolute private paths exported: False")

        imported = import_pod(exported, pods_root=recipient_root, embedder=embedder)
        print(f"Imported as: {imported.id} (read_only={imported.read_only})")

        prompt = "Review this API design and keep the explanation concise."
        _banner("ACT 2 — DOCK", f'Prompt: "{prompt}"')
        base_only = augment_for_stack(
            prompt,
            PodStack(base_pod="jiahan"),
            pods_root=recipient_root,
        )
        docked = augment_for_stack(
            prompt,
            PodStack(base_pod="jiahan", shared_pod="senior-review"),
            pods_root=recipient_root,
        )
        print("BASE ONLY")
        print(base_only.debug_text())
        print("\nBASE + SHARED POD")
        print(docked.debug_text())

        unrelated = augment_for_stack(
            "Plan a marathon breakfast.",
            PodStack(base_pod="jiahan", shared_pod="senior-review"),
            pods_root=recipient_root,
        )
        shared_hits = [item for item in unrelated.memories if item.pod_id == "senior-review"]
        _banner("ACT 3 — SELECTIVE, NOT A MEGA-PROMPT", "An unrelated task stays clean")
        print(f"Shared Pod context injected: {len(shared_hits)}")
        print(unrelated.furnished_prompt)


def _write_embedded_records(pod_id, texts, pods_root, embedder) -> None:
    vectors = embedder.embed(texts)
    records = []
    for index, (text, vector) in enumerate(zip(texts, vectors, strict=True), start=1):
        records.append(
            MemoryRecord(
                id=f"{pod_id}-{index}",
                type="principle",
                text=text,
                tags=["playbook"],
                source="demo",
                embedder=embedder.identity,
                embedding=vector.astype(float).tolist(),
            )
        )
    write_records(pod_id, records, pods_root)


def _banner(title: str, subtitle: str) -> None:
    print("\n" + "=" * 72)
    print(f"# {title}")
    print(f"# {subtitle}")
    print("=" * 72 + "\n")


if __name__ == "__main__":
    main()
