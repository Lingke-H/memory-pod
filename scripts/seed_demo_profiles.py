"""Re-ingest the checked-in alice/bob memory.md demo profiles."""

from __future__ import annotations

from memory_pod.config import DEMO_PROFILES_DIR, PROFILES_DIR
from memory_pod.ingest import ingest_path


def main() -> None:
    for profile in ("alice", "bob"):
        result = ingest_path(
            profile,
            DEMO_PROFILES_DIR / profile / "memory.md",
            profiles_root=PROFILES_DIR,
        )
        print(f"{profile}: {result.records_written} chunks -> {result.store_path}")


if __name__ == "__main__":
    main()
