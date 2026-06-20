"""Command-line interface for the Memory Pod hackathon demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_pod.augment import augment_for_profile
from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.ingest import ingest_path


def main() -> None:
    parser = argparse.ArgumentParser(prog="memory-pod")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest local .md/.txt memory files.")
    ingest_parser.add_argument("path", type=Path)
    ingest_parser.add_argument("--profile", default=DEFAULT_PROFILE)

    augment_parser = subparsers.add_parser("augment", help="Furnish a prompt with local memory.")
    augment_parser.add_argument("prompt")
    augment_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    augment_parser.add_argument("--debug", action="store_true")

    compare_parser = subparsers.add_parser(
        "compare",
        help="Run the same prompt against alice and bob demo profiles.",
    )
    compare_parser.add_argument("prompt")
    compare_parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.command == "ingest":
        result = ingest_path(profile=args.profile, source_path=args.path)
        print(f"Ingested {result.records_written} chunks for profile '{result.profile}'.")
        print(f"Store: {result.store_path}")
        return

    if args.command == "augment":
        result = augment_for_profile(args.prompt, profile=args.profile)
        print(result.debug_text() if args.debug else result.furnished_prompt)
        return

    if args.command == "compare":
        _ensure_demo_profiles_ingested()
        for profile in ("alice", "bob"):
            result = augment_for_profile(args.prompt, profile=profile)
            print("=" * 72)
            print(f"PROFILE: {profile}")
            print("=" * 72)
            print(result.debug_text() if args.debug else result.furnished_prompt)
            print()


def _ensure_demo_profiles_ingested() -> None:
    for profile in ("alice", "bob"):
        memory_file = PROFILES_DIR / profile / "memory.md"
        if memory_file.exists():
            ingest_path(profile=profile, source_path=memory_file)


if __name__ == "__main__":
    main()

