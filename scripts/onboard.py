"""Runnable first-run onboarding for Memory Pod (terminal version).

    make onboard

Walks a new user through: local-AI check -> starter Shared Playbooks -> a few
"about you" questions that become your private Base Pod.
"""

from __future__ import annotations

from memory_pod.llm import DEFAULT_MODEL, ollama_available
from memory_pod.onboarding import (
    ABOUT_YOU_QUESTIONS,
    complete_about_you,
    mark_onboarded,
    seed_experts,
)


def _ask(question: str) -> str:
    try:
        return input(f"  {question} ").strip()
    except EOFError:
        return ""


def main() -> None:
    print("=" * 64)
    print("  MEMORY POD — Welcome")
    print("  Create My Pod, load starter Shared Playbooks, then Dock them anywhere.")
    print("  Everything stays on your computer.")
    print("=" * 64)

    # 1/3 — Local AI check (never blocks).
    if ollama_available():
        print("\n[1/3] Local AI: found (Ollama). ✓")
    else:
        print("\n[1/3] Local AI: not found.")
        print(f"      Optional, free: install Ollama, then `ollama pull {DEFAULT_MODEL}`.")
        print("      You can skip this — everything still works without it.")

    # 2/3 — Starter Shared Playbooks.
    print("\n[2/3] Loading starter Shared Playbooks...")
    playbooks = seed_experts()
    print("      Ready: " + ", ".join(p.replace("-", " ").title() for p in playbooks) + " ✓")

    # 3/3 — About you (press Enter to skip any).
    print("\n[3/3] Tell me about you (press Enter to skip any):")
    answers = {key: _ask(question) for key, question in ABOUT_YOU_QUESTIONS}
    base_pod = complete_about_you(
        answers.get("name", ""),
        answers.get("role", ""),
        answers.get("working_on", ""),
        answers.get("style", ""),
    )
    mark_onboarded()

    print("\n" + "=" * 64)
    print(f"  Done. Your Base Pod is '{base_pod}'. ✓")
    print(
        "  Next: run `make popup`, pick Base '{0}' + a starter Shared Playbook, "
        "then Furnish.".format(base_pod)
    )
    print("=" * 64)


if __name__ == "__main__":
    main()
