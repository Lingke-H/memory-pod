from pathlib import Path

from scripts.seed_pod_demo import seed_pod_demo
from memory_pod.embeddings import HashingEmbedder
from memory_pod.memory_store import load_records
from memory_pod.pods import get_pod_manifest


def test_seed_pod_demo_creates_live_base_shared_and_export(tmp_path):
    export_path = tmp_path / "dist" / "senior-review.mpod"

    result = seed_pod_demo(
        pods_root=tmp_path / "pods",
        export_path=export_path,
        embedder=HashingEmbedder(),
    )

    assert get_pod_manifest("jiahan", tmp_path / "pods").kind == "private"
    assert get_pod_manifest("senior-review", tmp_path / "pods").kind == "shared"
    assert load_records("jiahan", tmp_path / "pods")
    assert load_records("senior-review", tmp_path / "pods")
    assert result.export_path == export_path
    assert export_path.exists()
