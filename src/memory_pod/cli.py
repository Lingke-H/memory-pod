"""Command-line interface for the Memory Pod hackathon demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_pod.augment import augment_for_profile
from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.ingest import ingest_path
from memory_pod.memory_store import store_path
from memory_pod.remember import remember


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
    compare_parser.add_argument("--reingest", action="store_true")

    remember_parser = subparsers.add_parser(
        "remember",
        help="Save a new local memory into a profile (write-back).",
    )
    remember_parser.add_argument("text")
    remember_parser.add_argument("--profile", default=DEFAULT_PROFILE)
    remember_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="Optional tag for this memory; repeat for multiple tags.",
    )

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

    if args.command == "remember":
        record = remember(args.text, profile=args.profile, tags=args.tags or [])
        print(f"✓ Remembered for '{args.profile}': {record.id}")
        print(f"  {record.text}")
        return

    if args.command == "compare":
        run_compare(args.prompt, debug=args.debug, reingest=args.reingest)


def run_compare(prompt: str, *, debug: bool = True, reingest: bool = False) -> None:
    """Run the marquee "same prompt, different memory" demo for alice and bob.

    Shared entry point so the judge demo (scripts/judge_demo.py) produces output
    identical to `make demo`.
    """
    _ensure_demo_profiles_ingested(force=reingest)
    print("#" * 72)
    print("# MEMORY POD — same prompt, different memory")
    print(f'# Prompt: "{prompt}"')
    print("#" * 72)
    print()
    for profile in ("alice", "bob"):
        result = augment_for_profile(prompt, profile=profile)
        print("=" * 72)
        print(f"PROFILE: {profile}")
        print("=" * 72)
        print(result.debug_text() if debug else result.furnished_prompt)
        print()


def _ensure_demo_profiles_ingested(force: bool = False, profiles_root: Path = PROFILES_DIR) -> None:
    for profile in ("alice", "bob"):
        memory_file = profiles_root / profile / "memory.md"
        if memory_file.exists() and (force or _needs_ingest(profile, memory_file, profiles_root)):
            ingest_path(profile=profile, source_path=memory_file, profiles_root=profiles_root)


def _needs_ingest(profile: str, memory_file: Path, profiles_root: Path = PROFILES_DIR) -> bool:
    path = store_path(profile, profiles_root)
    return not path.exists() or path.stat().st_mtime < memory_file.stat().st_mtime


if __name__ == "__main__":
    main()
