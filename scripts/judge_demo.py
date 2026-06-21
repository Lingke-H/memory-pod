"""Three-minute judge demo — the frozen live presentation path.

Runs the two must-survive terminal demos back-to-back with timed act banners,
then cues the presenter for the live Tier 1 popup. Everything here calls the
exact same code paths as `make demo` and `make demo-learn`, so the output is
identical to what the runbook promises — no new features, just a locked script.

    make judge

Press Enter to advance between acts (gives the presenter pacing control). When
run non-interactively (piped/CI) the gates are skipped and all acts run through.
"""

from __future__ import annotations

import demo_learn  # same scripts/ directory; on sys.path when run as a script

from memory_pod.cli import run_compare

# Same prompt as `make demo`, so Act 1 is byte-identical to the runbook.
DEMO_PROMPT = "help me write this application"


def _banner(line1: str, line2: str) -> None:
    print("\n" + "=" * 72)
    print(f"# {line1}")
    print(f"# {line2}")
    print("=" * 72 + "\n")


def _gate(message: str) -> None:
    try:
        input(message)
    except EOFError:
        print()  # non-interactive run: just continue


def main() -> None:
    _banner(
        "MEMORY POD — 3-MINUTE JUDGE DEMO",
        "Local-first personal memory. Your memory, not the model you happen to use.",
    )
    _gate(">> Press Enter to start ACT 1 ...")

    _banner("ACT 1 (0:00-1:00) — Same prompt, DIFFERENT memory", f'Prompt: "{DEMO_PROMPT}"')
    print('Say: "Alice and Bob type the SAME vague prompt. Watch the furnished prompts diverge."\n')
    run_compare(DEMO_PROMPT, debug=True)
    print(">> Point out: Alice = academic / AI-safety framing; Bob = B2B founder / sales framing.")
    _gate("\n>> Press Enter to start ACT 2 ...")

    _banner("ACT 2 (1:00-2:00) — It just learned that", "Teach a brand-new fact, then watch it get retrieved.")
    print('Say: "Memory grows locally. I teach it one fact, and the next prompt uses it."\n')
    demo_learn.main()
    _gate("\n>> Press Enter for ACT 3 (live popup) ...")

    _banner(
        "ACT 3 (2:00-3:00) — Live Tier 1 popup",
        "In a second terminal: make popup",
    )
    print("Presenter steps:")
    print("  1. Press Option+Enter to summon the popup.")
    print("  2. Type a vague prompt, click Furnish — retrieved memories + scores appear.")
    print("  3. Click Copy — status line confirms it's on the clipboard; paste into any model.")
    print("  4. (Optional) Type a fact, click Remember — status line confirms local write-back.")
    print("\nFALLBACK: if the hotkey or popup misbehaves, immediately run:")
    print("    make demo  &&  make demo-learn")
    print("\n" + "=" * 72)
    print("# END — Your memory should belong to you, not the model you happen to use today.")
    print("=" * 72)


if __name__ == "__main__":
    main()
