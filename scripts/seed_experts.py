"""Seed bundled starter Shared Playbook Pods into the local Pod store.

    make seed-experts
"""

from __future__ import annotations

from memory_pod.onboarding import seed_experts


def main() -> None:
    seeded = seed_experts()
    print("Seeded starter Shared Playbooks: " + ", ".join(seeded))


if __name__ == "__main__":
    main()
