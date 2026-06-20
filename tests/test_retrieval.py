import numpy as np

from memory_pod.embeddings import HashingEmbedder
from memory_pod.ingest import chunk_text, ingest_path
from memory_pod.memory_store import MemoryRecord, load_records, write_records
from memory_pod.retrieval import retrieve


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
    assert records[0].embedder == "hashing-v1:384"


def test_retrieval_reembeds_when_embedder_identity_changes(tmp_path):
    profiles_root = tmp_path / "profiles"
    memory_file = profiles_root / "alice" / "memory.md"
    memory_file.parent.mkdir(parents=True)
    memory_file.write_text("Alice writes AI safety applications.", encoding="utf-8")

    ingest_path("alice", memory_file, profiles_root=profiles_root, embedder=HashingEmbedder())
    records = load_records("alice", profiles_root=profiles_root)
    records[0].embedder = "other-vector-space"
    from memory_pod.memory_store import write_records

    write_records("alice", records, profiles_root=profiles_root)

    results = retrieve(
        "write AI application",
        profile="alice",
        profiles_root=profiles_root,
        embedder=HashingEmbedder(),
    )

    assert results


def test_retrieval_filters_low_relevance_scores(tmp_path):
    profiles_root = tmp_path / "profiles"
    write_records(
        "alice",
        [
            _record("strong", "Alice is writing an AI safety application.", [1.0, 0.0]),
            _record("weak", "Alice likes unrelated breakfast notes.", [0.01, 0.99995]),
        ],
        profiles_root=profiles_root,
    )

    results = retrieve(
        "write this application",
        profile="alice",
        profiles_root=profiles_root,
        embedder=_StaticEmbedder(),
    )

    assert [result.record.id for result in results] == ["strong"]


def test_retrieval_all_low_scores_returns_empty(tmp_path):
    profiles_root = tmp_path / "profiles"
    write_records(
        "alice",
        [_record("weak", "Alice likes unrelated breakfast notes.", [0.01, 0.99995])],
        profiles_root=profiles_root,
    )

    results = retrieve(
        "write this application",
        profile="alice",
        profiles_root=profiles_root,
        embedder=_StaticEmbedder(),
    )

    assert results == []


def test_retrieval_allows_custom_min_score_for_debugging(tmp_path):
    profiles_root = tmp_path / "profiles"
    write_records(
        "alice",
        [_record("weak", "Alice likes unrelated breakfast notes.", [0.01, 0.99995])],
        profiles_root=profiles_root,
    )

    results = retrieve(
        "write this application",
        profile="alice",
        profiles_root=profiles_root,
        embedder=_StaticEmbedder(),
        min_score=0.0,
    )

    assert [result.record.id for result in results] == ["weak"]


def _record(record_id: str, text: str, embedding: list[float]) -> MemoryRecord:
    return MemoryRecord(
        id=record_id,
        text=text,
        embedder=_StaticEmbedder.identity,
        embedding=embedding,
    )


class _StaticEmbedder:
    identity = "static-test-v1"

    def embed(self, texts):
        text_list = list(texts)
        return np.array([[1.0, 0.0] for _ in text_list], dtype=np.float32)
