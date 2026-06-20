from memory_pod.embeddings import HashingEmbedder
from memory_pod.ingest import chunk_text, ingest_path
from memory_pod.memory_store import load_records


def test_chunk_text_splits_markdown_sections():
    chunks = chunk_text("# A\n\none\n\n# B\n\ntwo")

    assert chunks == ["# A\n\none", "# B\n\ntwo"]


def test_ingest_writes_local_jsonl_store(tmp_path):
    profiles_root = tmp_path / "profiles"
    memory_file = profiles_root / "bob" / "memory.md"
    memory_file.parent.mkdir(parents=True)
    memory_file.write_text("Bob cares about B2B ROI and sales copy.", encoding="utf-8")

    result = ingest_path("bob", memory_file, profiles_root=profiles_root, embedder=HashingEmbedder())
    records = load_records("bob", profiles_root=profiles_root)

    assert result.records_written == 1
    assert records[0].source == str(memory_file.resolve())
