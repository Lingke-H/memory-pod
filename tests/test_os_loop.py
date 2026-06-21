from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import MemoryRecord, write_records
from memory_pod.os_loop import build_augment_fn
from memory_pod.pods import create_pod

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

    furnished = build_augment_fn(base_pod="jiahan", pods_root=tmp_path)(PROMPT)

    assert "[Hidden Context]" in furnished
    assert "Docked Shared Playbook" not in furnished


def test_build_augment_fn_docks_shared_pod(tmp_path, monkeypatch):
    _seed(tmp_path)
    monkeypatch.setattr("memory_pod.retrieval.get_embedder", lambda: HashingEmbedder())

    furnished = build_augment_fn(
        base_pod="jiahan", shared_pod="senior-review", pods_root=tmp_path
    )(PROMPT)

    assert "Private User Context" in furnished
    assert "Docked Shared Playbook" in furnished
