from memory_pod.memory_store import MemoryRecord, load_records, write_records


def test_write_records_produces_loadable_jsonl(tmp_path):
    write_records(
        "jiahan",
        [
            MemoryRecord(id="one", text="First memory."),
            MemoryRecord(id="two", text="Second memory."),
        ],
        profiles_root=tmp_path,
    )

    records = load_records("jiahan", tmp_path)

    assert [record.id for record in records] == ["one", "two"]
    assert [record.text for record in records] == ["First memory.", "Second memory."]
