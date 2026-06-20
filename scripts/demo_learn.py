"""One-command "it just learned" demo.

Remembers a brand-new fact into a throwaway local profile, then runs augment to
show that the next prompt immediately retrieves it. Uses a temporary profiles
directory so it never touches the checked-in demo data, and works offline via
the hashing-embedder fallback.

    make demo-learn
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from memory_pod.augment import augment_for_profile
from memory_pod.remember import remember

PROFILE = "demo"
# Fact and prompt share vocabulary ("marathon", "training") so the demo retrieves
# reliably with BOTH the real model and the offline hashing-embedder fallback.
FACT = "I am training for the Boston Marathon and want to finish it under 4 hours."
PROMPT = "help me write a marathon training plan"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        profiles_root = Path(tmp) / "profiles"

        print("=" * 72)
        print("MEMORY POD — 'it just learned that' demo")
        print("=" * 72)
        print(f"\n1) Teaching the system a NEW fact via remember():\n   {FACT!r}\n")
        remember(FACT, profile=PROFILE, source="demo", profiles_root=profiles_root)

        print(f"2) Now asking an unrelated-looking prompt:\n   {PROMPT!r}\n")
        result = augment_for_profile(PROMPT, profile=PROFILE, profiles_root=profiles_root)

        print("3) The furnished prompt now uses the freshly remembered memory:\n")
        print(result.debug_text())


if __name__ == "__main__":
    main()
