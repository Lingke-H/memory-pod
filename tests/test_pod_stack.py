import pytest

from memory_pod.augment import augment_for_stack, furnish_selected
from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import MemoryRecord, write_records
from memory_pod.pods import PodStack, create_pod


def test_stack_retrieves_base_and_shared_context(tmp_path, monkeypatch):
    _seed_stack(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    result = augment_for_stack(
        "Review this API design and keep the explanation concise.",
        PodStack(base_pod="jiahan", shared_pod="senior-review"),
        pods_root=tmp_path,
    )

    assert result.active_pods == ("jiahan", "senior-review")
    assert {memory.pod_id for memory in result.memories} == {"jiahan", "senior-review"}
    assert "Private User Context (Jiahan)" in result.furnished_prompt
    assert "Docked Shared Playbook (Senior Review)" in result.furnished_prompt


def test_shared_playbook_is_not_injected_for_unrelated_query(tmp_path, monkeypatch):
    _seed_stack(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    result = augment_for_stack(
        "Plan a marathon breakfast.",
        PodStack(base_pod="jiahan", shared_pod="senior-review"),
        pods_root=tmp_path,
    )

    assert all(memory.pod_id != "senior-review" for memory in result.memories)
    assert "Docked Shared Playbook" not in result.furnished_prompt


def test_furnish_selected_removes_unchecked_memory(tmp_path, monkeypatch):
    _seed_stack(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())
    stack = PodStack(base_pod="jiahan", shared_pod="senior-review")
    result = augment_for_stack("Review this API design.", stack, pods_root=tmp_path)
    base_only = [memory for memory in result.memories if memory.pod_id == "jiahan"]

    rebuilt = furnish_selected(
        result.raw_prompt,
        base_only,
        stack,
        pods_root=tmp_path,
    )

    assert "Private User Context" in rebuilt
    assert "Docked Shared Playbook" not in rebuilt
    assert "failure modes" not in rebuilt


def test_stack_rejects_private_pod_in_shared_slot(tmp_path):
    create_pod("Jiahan", pod_id="jiahan", pods_root=tmp_path)
    create_pod("Not Shared", pod_id="private-advice", pods_root=tmp_path)

    with pytest.raises(ValueError, match="not a Shared Pod"):
        augment_for_stack(
            "Review this API.",
            PodStack(base_pod="jiahan", shared_pod="private-advice"),
            pods_root=tmp_path,
        )


def test_stack_rejects_shared_pod_in_base_slot(tmp_path):
    create_pod("Senior Review", kind="shared", pod_id="senior-review", pods_root=tmp_path)

    with pytest.raises(PermissionError, match="private writable Base Pod"):
        augment_for_stack(
            "Review this API.",
            PodStack(base_pod="senior-review"),
            pods_root=tmp_path,
        )


def _seed_stack(pods_root):
    embedder = HashingEmbedder()
    create_pod("Jiahan", pod_id="jiahan", pods_root=pods_root)
    create_pod(
        "Senior Review",
        kind="shared",
        pod_id="senior-review",
        pods_root=pods_root,
    )
    write_records(
        "jiahan",
        [
            _record(
                "base",
                "Jiahan prefers concise API design explanations.",
                embedder,
            )
        ],
        profiles_root=pods_root,
    )
    write_records(
        "senior-review",
        [
            _record(
                "shared",
                "Review API failure modes and explicit boundaries before implementation.",
                embedder,
            )
        ],
        profiles_root=pods_root,
    )


def _record(record_id, text, embedder):
    vector = embedder.embed([text])[0]
    return MemoryRecord(
        id=record_id,
        text=text,
        embedder=embedder.identity,
        embedding=vector.astype(float).tolist(),
    )
