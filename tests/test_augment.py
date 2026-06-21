from memory_pod.augment import augment_for_profile
from memory_pod.embeddings import HashingEmbedder
from memory_pod.ingest import ingest_path


def test_augment_uses_local_profile_memory(tmp_path):
    profiles_root = tmp_path / "profiles"
    memory_file = profiles_root / "alice" / "memory.md"
    memory_file.parent.mkdir(parents=True)
    memory_file.write_text("Alice writes concise AI safety research applications.", encoding="utf-8")

    ingest_path("alice", memory_file, profiles_root=profiles_root, embedder=HashingEmbedder())

    result = augment_for_profile(
        "help me write this application",
        profile="alice",
        profiles_root=profiles_root,
    )

    assert "[Hidden Context]" in result.furnished_prompt
    assert "Relevant Facts:" in result.furnished_prompt
    assert "Style And Response Guidance:" in result.furnished_prompt
    assert "AI safety" in result.furnished_prompt


def test_augment_returns_raw_prompt_when_retrieval_filters_everything(tmp_path, monkeypatch):
    def fake_retrieve(*args, **kwargs):
        return []

    monkeypatch.setattr("memory_pod.augment.retrieve", fake_retrieve)

    result = augment_for_profile("hello", profile="alice", profiles_root=tmp_path)

    assert result.memories == []
    assert result.furnished_prompt == "hello"


def test_augment_preserves_blank_prompt_as_empty_state(tmp_path):
    raw_prompt = "  \n "

    result = augment_for_profile(raw_prompt, profile="alice", profiles_root=tmp_path)

    assert result.raw_prompt == raw_prompt
    assert result.memories == []
    assert result.furnished_prompt == raw_prompt


def test_augment_missing_profile_returns_raw_prompt(tmp_path):
    result = augment_for_profile("hello", profile="missing", profiles_root=tmp_path)

    assert result.memories == []
    assert result.furnished_prompt == "hello"
