import pytest

from memory_pod.augment import augment_for_profile
from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import load_records
from memory_pod.remember import make_memory_id, remember


@pytest.fixture(autouse=True)
def use_hashing_embedder(monkeypatch):
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())


def test_remember_writes_manual_memory_record(tmp_path):
    profiles_root = tmp_path / "profiles"

    record = remember(
        "Alice prefers concise AI safety writing.",
        profile="alice",
        tags=["preference", "writing"],
        profiles_root=profiles_root,
    )
    records = load_records("alice", profiles_root=profiles_root)

    assert len(records) == 1
    assert records[0].id == record.id
    assert records[0].type == "manual_memory"
    assert records[0].text == "Alice prefers concise AI safety writing."
    assert records[0].tags == ["preference", "writing"]
    assert records[0].source == "manual"
    assert records[0].embedder == "hashing-v1:384"
    assert records[0].embedding


def test_remembered_memory_is_retrievable_by_augment(tmp_path):
    profiles_root = tmp_path / "profiles"
    remember(
        "Alice recently won a Rhodes scholarship.",
        profile="alice",
        tags=["bio"],
        profiles_root=profiles_root,
    )

    result = augment_for_profile(
        "help me write my scholarship bio",
        profile="alice",
        profiles_root=profiles_root,
    )

    assert result.memories
    assert "Rhodes scholarship" in result.furnished_prompt


def test_remember_uses_stable_id_to_prevent_unbounded_duplicates(tmp_path):
    profiles_root = tmp_path / "profiles"
    text = "Alice wants crisp technical writing."

    first = remember(text, profile="alice", profiles_root=profiles_root)
    second = remember(text, profile="alice", profiles_root=profiles_root)
    records = load_records("alice", profiles_root=profiles_root)

    assert first.id == second.id
    assert first.id == make_memory_id("alice", "manual", text)
    assert len(records) == 1


def test_remember_rejects_empty_text(tmp_path):
    with pytest.raises(ValueError, match="empty text"):
        remember("   ", profile="alice", profiles_root=tmp_path / "profiles")
