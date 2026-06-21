import json

import pytest

from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import MemoryRecord, load_records, write_records
from memory_pod.pods import (
    create_pod,
    export_pod,
    import_pod,
    inspect_pod,
    migrate_legacy_profiles,
    list_pods,
)
from memory_pod.remember import remember


def test_shared_pod_round_trip_strips_private_vector_data(tmp_path):
    sender_root = tmp_path / "sender"
    receiver_root = tmp_path / "receiver"
    create_pod(
        "Senior Architecture Review",
        kind="shared",
        author="Alice",
        purpose="Architecture review",
        pod_id="senior-review",
        pods_root=sender_root,
    )
    write_records(
        "senior-review",
        [
            MemoryRecord(
                id="principle-1",
                type="principle",
                text="Prefer explicit API boundaries over shared mutable state.",
                tags=["architecture"],
                source="private/notes/architecture.md",
                embedder="private-vector-space",
                embedding=[1.0, 0.0],
            )
        ],
        profiles_root=sender_root,
    )

    exported = export_pod("senior-review", tmp_path / "Senior Review", sender_root)
    payload = json.loads(exported.read_text(encoding="utf-8"))

    assert exported.suffix == ".mpod"
    assert "embedding" not in payload["records"][0]
    assert "embedder" not in payload["records"][0]
    assert "source_label" not in payload["records"][0]
    assert "private/notes" not in exported.read_text(encoding="utf-8")

    imported = import_pod(
        exported,
        pods_root=receiver_root,
        embedder=HashingEmbedder(),
    )
    records = load_records("senior-review", receiver_root)

    assert imported.read_only is True
    assert imported.origin == "imported"
    assert records[0].embedder == "hashing-v1:384"
    assert records[0].embedding
    assert records[0].source == "mpod:senior-review"


def test_private_pod_cannot_be_exported(tmp_path):
    create_pod("Private", pod_id="private", pods_root=tmp_path)

    with pytest.raises(PermissionError, match="Shared Pods"):
        export_pod("private", tmp_path / "private.mpod", tmp_path)


def test_import_is_idempotent_and_imported_pod_is_read_only(tmp_path, monkeypatch):
    sender_root = tmp_path / "sender"
    receiver_root = tmp_path / "receiver"
    create_pod("Review", kind="shared", pod_id="review", pods_root=sender_root)
    write_records(
        "review",
        [MemoryRecord(id="one", text="Review API failure modes before implementation.")],
        profiles_root=sender_root,
    )
    exported = export_pod("review", tmp_path / "review.mpod", sender_root)

    first = import_pod(exported, pods_root=receiver_root, embedder=HashingEmbedder())
    second = import_pod(exported, pods_root=receiver_root, embedder=HashingEmbedder())

    assert first == second
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())
    with pytest.raises(PermissionError, match="read-only"):
        remember("Do not mutate this Pod.", profile="review", profiles_root=receiver_root)


def test_inspect_rejects_modified_content(tmp_path):
    root = tmp_path / "pods"
    create_pod("Review", kind="shared", pod_id="review", pods_root=root)
    write_records(
        "review",
        [MemoryRecord(id="one", text="Original guidance.")],
        profiles_root=root,
    )
    exported = export_pod("review", tmp_path / "review.mpod", root)
    payload = json.loads(exported.read_text(encoding="utf-8"))
    payload["records"][0]["text"] = "Tampered guidance."
    exported.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="content hash"):
        inspect_pod(exported)


def test_migrate_legacy_profiles_copies_without_deleting_source(tmp_path):
    legacy_root = tmp_path / "legacy"
    pods_root = tmp_path / "pods"
    write_records(
        "alice",
        [MemoryRecord(id="one", text="Alice has local memory.")],
        profiles_root=legacy_root,
    )

    migrated = migrate_legacy_profiles(legacy_root, pods_root)

    assert [pod.id for pod in migrated] == ["alice"]
    assert load_records("alice", pods_root)[0].text == "Alice has local memory."
    assert load_records("alice", legacy_root)[0].text == "Alice has local memory."


def test_catalog_skips_corrupt_manifest(tmp_path):
    broken = tmp_path / "broken" / "pod.json"
    broken.parent.mkdir(parents=True)
    broken.write_text("not json", encoding="utf-8")

    assert list_pods(tmp_path) == []
