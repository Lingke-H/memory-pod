"""Command-line interface for the Memory Pod hackathon demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from memory_pod.augment import augment_for_profile, augment_for_stack
from memory_pod.config import DEFAULT_PROFILE, DEMO_PROFILES_DIR, PROFILES_DIR
from memory_pod.ingest import ingest_path
from memory_pod.memory_store import store_path
from memory_pod.pods import (
    PodStack,
    create_pod,
    export_pod,
    import_pod,
    inspect_pod,
    list_pods,
    migrate_legacy_profiles,
)
from memory_pod.remember import remember


def main() -> None:
    parser = argparse.ArgumentParser(prog="memory-pod")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest local .md/.txt memory files.")
    ingest_parser.add_argument("path", type=Path)
    ingest_parser.add_argument("--profile", "--pod", dest="profile", default=DEFAULT_PROFILE)

    augment_parser = subparsers.add_parser("augment", help="Furnish a prompt with local memory.")
    augment_parser.add_argument("prompt")
    augment_parser.add_argument("--profile", default=None, help="Legacy alias for --base-pod.")
    augment_parser.add_argument("--base-pod", default=None)
    augment_parser.add_argument("--shared-pod", default=None)
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
    remember_parser.add_argument("--profile", "--pod", dest="profile", default=DEFAULT_PROFILE)
    remember_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="Optional tag for this memory; repeat for multiple tags.",
    )

    pod_parser = subparsers.add_parser("pod", help="Create, inspect, and carry Memory Pods.")
    pod_subparsers = pod_parser.add_subparsers(dest="pod_command", required=True)

    pod_create = pod_subparsers.add_parser("create", help="Create a local Pod.")
    pod_create.add_argument("--name", required=True)
    pod_create.add_argument("--id", dest="pod_id", default=None)
    pod_create.add_argument("--kind", choices=("private", "shared"), default="private")
    pod_create.add_argument("--author", default="")
    pod_create.add_argument("--purpose", default="")

    pod_subparsers.add_parser("list", help="List local and imported Pods.")

    pod_inspect = pod_subparsers.add_parser("inspect", help="Preview a portable .mpod file.")
    pod_inspect.add_argument("path", type=Path)

    pod_import = pod_subparsers.add_parser("import", help="Import a portable .mpod file.")
    pod_import.add_argument("path", type=Path)
    pod_import.add_argument("--replace", action="store_true")

    pod_export = pod_subparsers.add_parser("export", help="Export a local Shared Pod.")
    pod_export.add_argument("pod_id")
    pod_export.add_argument("--output", type=Path, required=True)

    pod_subparsers.add_parser(
        "migrate-legacy",
        help="Copy legacy repo profile stores into Application Support.",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        result = ingest_path(profile=args.profile, source_path=args.path)
        print(f"Ingested {result.records_written} chunks for profile '{result.profile}'.")
        print(f"Store: {result.store_path}")
        return

    if args.command == "augment":
        base_pod = args.base_pod or args.profile or DEFAULT_PROFILE
        result = (
            augment_for_stack(
                args.prompt,
                stack=PodStack(base_pod=base_pod, shared_pod=args.shared_pod),
            )
            if args.shared_pod
            else augment_for_profile(args.prompt, profile=base_pod)
        )
        print(result.debug_text() if args.debug else result.furnished_prompt)
        return

    if args.command == "remember":
        record = remember(args.text, profile=args.profile, tags=args.tags or [])
        print(f"✓ Remembered for '{args.profile}': {record.id}")
        print(f"  {record.text}")
        return

    if args.command == "compare":
        run_compare(args.prompt, debug=args.debug, reingest=args.reingest)
        return

    if args.command == "pod":
        _run_pod_command(args)


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
        memory_file = DEMO_PROFILES_DIR / profile / "memory.md"
        if memory_file.exists() and (force or _needs_ingest(profile, memory_file, profiles_root)):
            ingest_path(profile=profile, source_path=memory_file, profiles_root=profiles_root)


def _needs_ingest(profile: str, memory_file: Path, profiles_root: Path = PROFILES_DIR) -> bool:
    path = store_path(profile, profiles_root)
    return not path.exists() or path.stat().st_mtime < memory_file.stat().st_mtime


def _run_pod_command(args) -> None:
    if args.pod_command == "create":
        manifest = create_pod(
            name=args.name,
            kind=args.kind,
            author=args.author,
            purpose=args.purpose,
            pod_id=args.pod_id,
        )
        print(f"Created {manifest.kind} Pod '{manifest.name}' ({manifest.id}).")
        return

    if args.pod_command == "list":
        pods = list_pods()
        if not pods:
            print("No Pods found.")
            return
        for pod in pods:
            access = "read-only" if pod.read_only else "writable"
            print(f"{pod.id}\t{pod.kind}\t{access}\t{pod.name}")
        return

    if args.pod_command == "inspect":
        portable = inspect_pod(args.path)
        pod = portable.manifest
        print(f"Pod: {pod.name} ({pod.id})")
        print(f"Author: {pod.author or 'Unspecified'} (not verified)")
        print(f"Purpose: {pod.purpose or 'Unspecified'}")
        print(f"Version: {pod.version}")
        print(f"Records: {len(portable.records)}")
        for index, record in enumerate(portable.records, start=1):
            tags = ", ".join(record["tags"]) if record["tags"] else "none"
            print(f"{index}. [{record['type']}] {record['text']}")
            print(f"   Tags: {tags}")
        return

    if args.pod_command == "import":
        manifest = import_pod(args.path, replace=args.replace)
        print(f"Imported read-only Shared Pod '{manifest.name}' ({manifest.id}).")
        return

    if args.pod_command == "export":
        path = export_pod(args.pod_id, args.output)
        print(f"Exported Shared Pod to {path}")
        return

    if args.pod_command == "migrate-legacy":
        migrated = migrate_legacy_profiles()
        if not migrated:
            print("No legacy profile stores needed migration.")
            return
        for pod in migrated:
            print(f"Migrated legacy profile '{pod.id}' into a private Pod.")


if __name__ == "__main__":
    main()
