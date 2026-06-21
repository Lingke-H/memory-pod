"""Frozen three-minute Portable Pods presentation path."""

from __future__ import annotations

import pod_demo


def _banner(line1: str, line2: str) -> None:
    print("\n" + "=" * 72)
    print(f"# {line1}")
    print(f"# {line2}")
    print("=" * 72 + "\n")


def _gate(message: str) -> None:
    try:
        input(message)
    except EOFError:
        print()


def main() -> None:
    _banner(
        "MEMORY POD — PORTABLE PODS",
        "Own your Pod. Dock it anywhere. Share only what you choose.",
    )
    _gate(">> Press Enter to start ACT 1 ...")

    _banner(
        "ACT 1 (0:00-1:30) — Own, Carry, Dock",
        "Export an inspectable playbook, import it read-only, retrieve it locally.",
    )
    pod_demo.main()
    _gate("\n>> Press Enter for ACT 2 ...")

    _banner(
        "ACT 2 (1:30-2:15) — One Pod, Any Model",
        "Paste the same approved context into ChatGPT and Claude side by side.",
    )
    print("Presenter steps:")
    print("  1. Point to the Base and Shared Pod provenance in the debug output.")
    print("  2. Copy the furnished prompt into ChatGPT and Claude.")
    print("  3. Say: The model changes; the user-owned context does not.")
    _gate("\n>> Press Enter for ACT 3 ...")

    _banner(
        "ACT 3 (2:15-3:00) — Live Pod Dock",
        "In a second terminal: make popup",
    )
    print("Presenter steps:")
    print("  1. Press Option+Enter and Dock Base + Shared.")
    print("  2. Furnish a prompt; provenance, score, and snippet appear.")
    print("  3. Uncheck one context row; the prompt rebuilds immediately.")
    print("  4. Copy only. The user remains responsible for sending.")
    print("\nFALLBACK: run make pod-demo.")
    print("\n" + "=" * 72)
    print("# END — Dock the right context to any model.")
    print("=" * 72)


if __name__ == "__main__":
    main()
