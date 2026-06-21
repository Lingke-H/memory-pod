"""Seed bundled starter Shared Pods into the local Pod store.

    make seed-experts
"""

from __future__ import annotations

from memory_pod.onboarding import seed_experts


def main() -> None:
    seeded = seed_experts()
    print("Seeded starter Shared Pods: " + ", ".join(seeded))


if __name__ == "__main__":
    main()
