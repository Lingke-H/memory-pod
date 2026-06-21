"""First-run onboarding logic for Memory Pod.

Pure, GUI-agnostic helpers so the wizard screens stay thin and the logic is
unit-testable. Turns a few "about you" answers into a private Base Pod, and
tracks whether the user has already onboarded.
"""

from __future__ import annotations

from pathlib import Path

from memory_pod.config import EXPERTS_DIR, MEMORY_POD_HOME, PODS_DIR
from memory_pod.ingest import ingest_path
from memory_pod.pods import _slugify, create_pod, get_pod_manifest
from memory_pod.remember import remember

ONBOARDED_FLAG = ".onboarded"

# (key, on-screen question), shown in order by the wizard.
ABOUT_YOU_QUESTIONS: list[tuple[str, str]] = [
    ("name", "What's your name?"),
    ("role", "What do you do?"),
    ("working_on", "What are you working on right now?"),
    ("style", "How do you like answers — short or detailed?"),
]


def is_onboarded(home: Path = MEMORY_POD_HOME) -> bool:
    return (home / ONBOARDED_FLAG).exists()


def mark_onboarded(home: Path = MEMORY_POD_HOME) -> None:
    home.mkdir(parents=True, exist_ok=True)
    (home / ONBOARDED_FLAG).write_text("ok\n", encoding="utf-8")


def about_you_facts(
    name: str, role: str = "", working_on: str = "", style: str = ""
) -> list[str]:
    """Turn the answers into memory lines phrased so prompt-assembly buckets them
    sensibly (``current project`` -> Facts, ``prefers`` -> Style)."""
    clean_name = (name or "You").strip()
    facts = [f"The user's name is {clean_name}."]
    if role.strip():
        facts.append(f"{clean_name} is {role.strip()}.")
    if working_on.strip():
        facts.append(f"{clean_name}'s current project: {working_on.strip()}.")
    if style.strip():
        facts.append(f"{clean_name} prefers {style.strip()} answers.")
    return facts


def complete_about_you(
    name: str,
    role: str = "",
    working_on: str = "",
    style: str = "",
    *,
    pods_root: Path = PODS_DIR,
    notes_file: Path | None = None,
) -> str:
    """Create (or reuse) the user's private Base Pod and remember their answers.

    Idempotent: re-running reuses the existing Pod and, thanks to stable record
    ids, does not duplicate facts. Returns the Base Pod id.
    """
    clean_name = (name or "").strip()
    # _slugify raises on empty / non-alphanumeric names, so guard before calling.
    try:
        pod_id = _slugify(clean_name) if clean_name else "me"
    except ValueError:
        pod_id = "me"
    if get_pod_manifest(pod_id, pods_root) is None:
        create_pod(clean_name or "You", kind="private", pod_id=pod_id, pods_root=pods_root)

    for fact in about_you_facts(name, role, working_on, style):
        remember(fact, profile=pod_id, source="onboarding", profiles_root=pods_root)

    if notes_file is not None:
        ingest_path(profile=pod_id, source_path=Path(notes_file), profiles_root=pods_root)

    return pod_id


def seed_experts(
    experts_dir: Path = EXPERTS_DIR,
    pods_root: Path = PODS_DIR,
    embedder=None,
) -> list[str]:
    """Import bundled starter Expert Pods as ready-to-dock Shared Pods.

    Idempotent: existing starter Expert Pods are re-ingested (source
    reconciliation keeps them current) rather than recreated. Returns the seeded
    pod ids.
    """
    seeded: list[str] = []
    for playbook in sorted(experts_dir.glob("*.md")):
        pod_id = playbook.stem
        name = pod_id.replace("-", " ").title()
        if get_pod_manifest(pod_id, pods_root) is None:
            create_pod(
                name,
                kind="shared",
                author="Memory Pod (starter)",
                purpose=f"Starter {name} playbook from common best-practices.",
                pod_id=pod_id,
                pods_root=pods_root,
            )
        kwargs = {"embedder": embedder} if embedder is not None else {}
        ingest_path(profile=pod_id, source_path=playbook, profiles_root=pods_root, **kwargs)
        seeded.append(pod_id)
    return seeded
