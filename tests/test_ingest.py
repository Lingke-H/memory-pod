from memory_pod.embeddings import HashingEmbedder
from memory_pod.ingest import ingest_path
from memory_pod.memory_store import MemoryRecord, load_records, write_records


def test_reingesting_edited_file_removes_stale_chunks(tmp_path):
    source = tmp_path / "memory.md"
    source.write_text("Current project: old checkout API.", encoding="utf-8")

    ingest_path("jiahan", source, profiles_root=tmp_path, embedder=HashingEmbedder())
    source.write_text("Current project: new checkout API.", encoding="utf-8")
    ingest_path("jiahan", source, profiles_root=tmp_path, embedder=HashingEmbedder())

    texts = [record.text for record in load_records("jiahan", tmp_path)]
    assert texts == ["Current project: new checkout API."]


def test_reingesting_directory_removes_chunks_for_deleted_files(tmp_path):
    source_dir = tmp_path / "notes"
    source_dir.mkdir()
    keep = source_dir / "keep.md"
    delete = source_dir / "delete.md"
    keep.write_text("Keep this API guidance.", encoding="utf-8")
    delete.write_text("Delete this stale deployment note.", encoding="utf-8")

    ingest_path("jiahan", source_dir, profiles_root=tmp_path, embedder=HashingEmbedder())
    delete.unlink()
    ingest_path("jiahan", source_dir, profiles_root=tmp_path, embedder=HashingEmbedder())

    texts = [record.text for record in load_records("jiahan", tmp_path)]
    assert texts == ["Keep this API guidance."]


def test_reingest_preserves_manual_memories(tmp_path):
    source = tmp_path / "memory.md"
    source.write_text("Current project: checkout API.", encoding="utf-8")
    write_records(
        "jiahan",
        [
            MemoryRecord(
                id="manual-one",
                type="manual_memory",
                text="Jiahan prefers concise examples.",
                source="manual",
            )
        ],
        profiles_root=tmp_path,
    )

    ingest_path("jiahan", source, profiles_root=tmp_path, embedder=HashingEmbedder())

    texts = {record.text for record in load_records("jiahan", tmp_path)}
    assert "Jiahan prefers concise examples." in texts
    assert "Current project: checkout API." in texts
