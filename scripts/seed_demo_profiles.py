"""Re-ingest the checked-in alice/bob memory.md demo profiles."""

from __future__ import annotations

from memory_pod.config import PROFILES_DIR
from memory_pod.ingest import ingest_path


def main() -> None:
    for profile in ("alice", "bob"):
        result = ingest_path(profile, PROFILES_DIR / profile / "memory.md")
        print(f"{profile}: {result.records_written} chunks -> {result.store_path}")


if __name__ == "__main__":
    main()

