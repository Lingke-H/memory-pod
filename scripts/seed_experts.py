"""Seed bundled starter Expert Pods into the local Pod store as Shared Pods.

    make seed-experts
"""

from __future__ import annotations

from memory_pod.onboarding import seed_experts


def main() -> None:
    seeded = seed_experts()
    print("Seeded starter Expert Pods: " + ", ".join(seeded))


if __name__ == "__main__":
    main()
