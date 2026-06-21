from memory_pod.active_dock import write_active_dock
from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import MemoryRecord, load_records, write_records
from memory_pod.os_loop import HotkeyConfig, build_augment_fn, build_remember_fn
from memory_pod.pods import create_pod
from memory_pod.rewriter import RewriteResult

PROMPT = "Review this API design and keep the explanation concise."


def _rec(record_id, text, embedder):
    vector = embedder.embed([text])[0]
    return MemoryRecord(
        id=record_id,
        text=text,
        embedder=embedder.identity,
        embedding=vector.astype(float).tolist(),
    )


def _seed(pods_root):
    embedder = HashingEmbedder()
    create_pod("Jiahan", pod_id="jiahan", pods_root=pods_root)
    create_pod("Senior Review", kind="shared", pod_id="senior-review", pods_root=pods_root)
    write_records(
        "jiahan",
        [_rec("base", "Jiahan prefers concise API design explanations.", embedder)],
        profiles_root=pods_root,
    )
    write_records(
        "senior-review",
        [_rec("shared", "Review API failure modes and explicit boundaries first.", embedder)],
        profiles_root=pods_root,
    )


def test_build_augment_fn_base_only(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    furnished = build_augment_fn(
        base_pod="jiahan", pods_root=tmp_path, polish=False, follow_active_dock=False
    )(PROMPT)

    assert "[Hidden Context]" in furnished
    assert "Docked Shared Pod Context" not in furnished


def test_build_augment_fn_docks_shared_pod(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    furnished = build_augment_fn(
        base_pod="jiahan",
        shared_pod="senior-review",
        pods_root=tmp_path,
        polish=False,
        follow_active_dock=False,
    )(PROMPT)

    assert "Private User Context" in furnished
    assert "Docked Shared Pod Context" in furnished


def test_build_augment_fn_polishes_when_enabled(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())
    monkeypatch.setattr(
        "memory_pod.os_loop.polish_locally",
        lambda raw, furnished, *a, **k: RewriteResult(
            text="POLISHED", used_local_ai=True, note=""
        ),
    )

    result = build_augment_fn(
        base_pod="jiahan", pods_root=tmp_path, polish=True, follow_active_dock=False
    )(PROMPT)

    assert result == "POLISHED"


def test_build_augment_fn_no_polish_returns_furnished(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    furnished = build_augment_fn(
        base_pod="jiahan", pods_root=tmp_path, polish=False, follow_active_dock=False
    )(PROMPT)

    assert "[Hidden Context]" in furnished


def _seed_second_base(pods_root):
    embedder = HashingEmbedder()
    create_pod("Alice", pod_id="alice", pods_root=pods_root)
    write_records(
        "alice",
        [_rec("alice-base", "Alice researches AI safety and formal verification.", embedder)],
        profiles_root=pods_root,
    )


def test_build_augment_fn_follows_active_dock(tmp_path, monkeypatch):
    _seed(tmp_path)
    _seed_second_base(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    fn = build_augment_fn(
        base_pod="jiahan",
        pods_root=tmp_path,
        polish=False,
        follow_active_dock=True,
        home=tmp_path,
    )
    write_active_dock("alice", home=tmp_path)

    furnished = fn(PROMPT)

    assert "AI safety" in furnished
    assert "concise API design" not in furnished


def test_build_augment_fn_uses_launch_pod_without_active_dock(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    fn = build_augment_fn(
        base_pod="jiahan",
        pods_root=tmp_path,
        polish=False,
        follow_active_dock=True,
        home=tmp_path,
    )

    furnished = fn(PROMPT)

    assert "concise API design" in furnished


def test_build_remember_fn_writes_os_hotkey_memory(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())

    status = build_remember_fn(base_pod="jiahan", pods_root=tmp_path)(
        "I prefer review comments that name concrete failure modes."
    )

    records = load_records("jiahan", profiles_root=tmp_path)
    remembered = [record for record in records if record.source == "os-hotkey"]
    assert remembered
    assert remembered[0].type == "manual_memory"
    assert remembered[0].text == "I prefer review comments that name concrete failure modes."
    assert "Remembered" in status


def test_build_remember_fn_ignores_empty_text(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())

    status = build_remember_fn(base_pod="jiahan", pods_root=tmp_path)("   \n")

    records = load_records("jiahan", profiles_root=tmp_path)
    assert all(record.source != "os-hotkey" for record in records)
    assert "No text" in status


def test_build_remember_fn_rejects_shared_base_pod(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())

    try:
        build_remember_fn(base_pod="senior-review", pods_root=tmp_path)(
            "Shared Pods must stay read-only."
        )
    except PermissionError as exc:
        assert "private writable" in str(exc)
    else:
        raise AssertionError("shared Pod remember unexpectedly succeeded")


def test_hotkey_config_has_distinct_augment_and_remember_hotkeys():
    config = HotkeyConfig()

    assert config.hotkey == "<alt>+<enter>"
    assert config.remember_hotkey == "<ctrl>+<shift>+<enter>"
    assert config.hotkey != config.remember_hotkey
