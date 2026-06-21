from memory_pod.hotkey_popup import (
    available_pod_choices,
    format_polish_status,
    format_value_summary,
    pod_face,
)
from memory_pod.memory_store import MemoryRecord
from memory_pod.pods import PodManifest, PodStack
from memory_pod.rewriter import RewriteResult
from memory_pod.retrieval import RetrievalResult


def _mem(pod_id: str) -> RetrievalResult:
    return RetrievalResult(
        record=MemoryRecord(id=pod_id, text="x"), score=0.2, pod_id=pod_id
    )


def test_pod_face_is_deterministic_and_nonempty():
    assert pod_face("jiahan") == pod_face("jiahan")
    assert pod_face("jiahan")
    assert pod_face("") == "📦"


def test_value_summary_counts_base_and_shared():
    stack = PodStack(base_pod="jiahan", shared_pod="senior-review")
    memories = [_mem("jiahan"), _mem("jiahan"), _mem("senior-review")]

    summary = format_value_summary(memories, stack)

    assert "2 of your memories" in summary
    assert "1 shared playbook item" in summary


def test_value_summary_base_only_omits_shared_playbook():
    stack = PodStack(base_pod="jiahan")

    summary = format_value_summary([_mem("jiahan")], stack)

    assert "1 of your memories" in summary
    assert "shared playbook" not in summary


def test_available_pod_choices_excludes_shared_pods_from_base_selector():
    pods = [
        PodManifest(id="jiahan", name="Jiahan", kind="private"),
        PodManifest(id="local-shared", name="Shared", kind="shared"),
        PodManifest(
            id="imported-shared",
            name="Imported",
            kind="shared",
            read_only=True,
            origin="imported",
        ),
    ]

    base_choices, shared_choices = available_pod_choices(pods, current_base="jiahan")

    assert base_choices == ["jiahan"]
    assert shared_choices == ["(None)", "local-shared", "imported-shared"]


def test_format_polish_status_reports_local_ai_success():
    result = RewriteResult(
        text="Clean prompt",
        used_local_ai=True,
        note="Polished locally with llama3.2.",
    )

    assert format_polish_status(result) == (
        "Polished locally with llama3.2. Review before sending."
    )


def test_format_polish_status_reports_fallback_note():
    result = RewriteResult(
        text="Original prompt",
        used_local_ai=False,
        note="Local AI unavailable; using furnished prompt.",
    )

    assert format_polish_status(result) == "Local AI unavailable; using furnished prompt."
