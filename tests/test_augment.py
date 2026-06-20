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
