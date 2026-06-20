from memory_pod.cli import _needs_ingest
from memory_pod.memory_store import MemoryRecord, write_records


def test_needs_ingest_when_store_missing(tmp_path):
    profiles_root = tmp_path / "profiles"
    memory_file = profiles_root / "alice" / "memory.md"
    memory_file.parent.mkdir(parents=True)
    memory_file.write_text("Alice memory", encoding="utf-8")

    assert _needs_ingest("alice", memory_file, profiles_root=profiles_root)


def test_needs_ingest_skips_unchanged_store(tmp_path):
    profiles_root = tmp_path / "profiles"
    memory_file = profiles_root / "alice" / "memory.md"
    memory_file.parent.mkdir(parents=True)
    memory_file.write_text("Alice memory", encoding="utf-8")
    write_records("alice", [MemoryRecord(id="m1", text="Alice memory")], profiles_root)

    assert not _needs_ingest("alice", memory_file, profiles_root=profiles_root)
