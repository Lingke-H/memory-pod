# Project Status Snapshot

This document records the verified repository state; it is not a speculative
feature backlog. Current scope is governed by
[PROJECT_DESCRIPTION_V4.md](../PROJECT_DESCRIPTION_V4.md).

## Implemented

- Local Markdown and text ingestion into JSONL-backed Pod stores.
- Local sentence-transformer embeddings with a deterministic hashing fallback.
- Embedder-mismatch protection and relevance-aware retrieval.
- Private writable Base Pods and explicit Shared Pods.
- Inspectable `.mpod` export, preview, import, and local re-embedding.
- Read-only boundaries for imported Shared Pods.
- Base-plus-Shared Pod Docking with separately framed prompt context.
- Selective context review and deselection before copying.
- Explicit local `remember()` write-back into private Base Pods.
- CLI workflows for ingest, augment, compare, remember, and Pod management.
- First-run onboarding and persistent demo seeding.
- A review-first macOS Pod Dock that never auto-submits.
- Optional local Ollama polishing with a safe furnished-prompt fallback.
- Optional OS-level in-place injection and explicit write-back hotkeys.
- Automated coverage for storage, retrieval, Pod policy, prompt assembly, CLI,
  onboarding, popup helpers, OS-loop helpers, and demo setup.

## Operational Follow-Up

- Record and retain a known-good macOS hotkey demo fallback.
- Perform a clean-machine setup rehearsal before a public demonstration.
- Treat broader Pod stacks, cloud synchronization, marketplaces, browser
  extensions, and autonomous agents as out of scope unless the product
  constitution is deliberately revised.

## Verification

```bash
source .venv/bin/activate
make check
make pod-demo
```

Manual macOS hotkey behavior still requires Accessibility permission and a
foreground interaction check; it cannot be established by unit tests alone.
