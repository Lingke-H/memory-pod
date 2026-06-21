from memory_pod.embeddings import HashingEmbedder
from memory_pod.llm import ollama_available
from memory_pod.memory_store import load_records
from memory_pod.onboarding import (
    about_you_facts,
    complete_about_you,
    is_onboarded,
    mark_onboarded,
)
from memory_pod.pods import get_pod_manifest


def test_first_run_flag(tmp_path):
    assert is_onboarded(tmp_path) is False
    mark_onboarded(tmp_path)
    assert is_onboarded(tmp_path) is True


def test_about_you_facts_use_bucketed_phrasing():
    joined = " ".join(
        about_you_facts("Eddy", "a stats student", "a hackathon project", "short")
    )
    assert "Eddy" in joined
    assert "current project" in joined  # -> Relevant Facts bucket
    assert "prefers short answers" in joined  # -> Style bucket


def test_complete_about_you_creates_base_pod_and_remembers(tmp_path, monkeypatch):
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())

    pod_id = complete_about_you(
        "Eddy", "a stats student", "a hackathon project", "short", pods_root=tmp_path
    )

    assert get_pod_manifest(pod_id, tmp_path) is not None
    texts = " ".join(record.text for record in load_records(pod_id, tmp_path))
    assert "hackathon project" in texts
    assert "prefers short answers" in texts


def test_complete_about_you_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr("memory_pod.remember.get_embedder", lambda: HashingEmbedder())

    pod_id = complete_about_you("Eddy", style="short", pods_root=tmp_path)
    complete_about_you("Eddy", style="short", pods_root=tmp_path)  # must not crash

    ids = [record.id for record in load_records(pod_id, tmp_path)]
    assert len(ids) == len(set(ids))  # stable ids -> no duplicates


def test_ollama_available_false_when_down():
    assert ollama_available("http://localhost:1", timeout=0.3) is False
