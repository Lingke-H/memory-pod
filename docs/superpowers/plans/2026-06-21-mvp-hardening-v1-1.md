# Memory Pod MVP v1.1 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden Memory Pod v1.0 into a safer, repeatable v1.1 demo/trial build.

**Architecture:** Keep the existing local JSONL + Tkinter Pod Dock architecture. Add centralized Pod policy helpers, atomic store writes, ingest source reconciliation, portable Pod metadata sanitization, a persistent demo setup command, and stronger prompt trust wording.

**Tech Stack:** Python, pytest, Tkinter, JSONL stores, local embeddings.

## Global Constraints

- Preserve review-first UX; no automatic prompt sending.
- Do not add P2P, marketplace, cloud sync, Chrome extension, ChromaDB/FAISS migration, or agent networks.
- Keep `augment(raw_prompt: str) -> str` public contract unchanged.
- Use TDD for behavior changes: write failing tests first, verify failure, implement, verify pass.

---

### Task 1: Pod Write Boundaries

**Files:**
- Modify: `src/memory_pod/pods.py`
- Modify: `src/memory_pod/remember.py`
- Modify: `src/memory_pod/augment.py`
- Modify: `src/memory_pod/hotkey_popup.py`
- Test: `tests/test_pod_stack.py`
- Test: `tests/test_remember.py`
- Test: `tests/test_popup_helpers.py`

**Interfaces:**
- Produces: `pod_is_private_writable(pod_id: str, pods_root: Path = PODS_DIR) -> bool`
- Produces: `require_private_writable_pod(pod_id: str, pods_root: Path = PODS_DIR) -> None`

- [ ] Write failing tests for Shared Pod write rejection and Base Pod filtering.
- [ ] Run targeted tests and confirm failures are about missing/private Pod policy.
- [ ] Add policy helpers in `pods.py`.
- [ ] Use helpers in `remember()`, `augment_for_stack()`, and popup Base options.
- [ ] Run targeted tests and confirm pass.

### Task 2: Portable Pod Privacy And Preview

**Files:**
- Modify: `src/memory_pod/pods.py`
- Modify: `src/memory_pod/cli.py`
- Modify: `src/memory_pod/hotkey_popup.py`
- Test: `tests/test_pods.py`
- Test: `tests/test_cli_pods.py`

**Interfaces:**
- Existing `.mpod` schema version remains `1`.
- Exported records keep `id`, `type`, `text`, `tags`, `weight`, and `created_at`.
- Exported records must not include `source_label`, `embedding`, `embedder`, or local source paths.

- [ ] Write failing tests for path-free export, generic imported source, and tag-visible inspect output.
- [ ] Run targeted tests and confirm failures.
- [ ] Remove source label export/import handling.
- [ ] Add tags and unverified-author note to CLI/popup preview.
- [ ] Run targeted tests and confirm pass.

### Task 3: Atomic Store Writes And Ingest Reconciliation

**Files:**
- Modify: `src/memory_pod/memory_store.py`
- Modify: `src/memory_pod/ingest.py`
- Test: `tests/test_memory_store.py`
- Test: `tests/test_ingest.py`

**Interfaces:**
- Produces: `replace_records_for_sources(profile: str, sources: set[str], new_records: Iterable[MemoryRecord], profiles_root: Path = PROFILES_DIR) -> Path`

- [ ] Write failing tests for edited file re-ingest, deleted directory file cleanup, manual memory preservation, and valid JSONL after writes.
- [ ] Run targeted tests and confirm failures.
- [ ] Implement atomic `write_records()` using same-directory temp file and `replace()`.
- [ ] Implement `replace_records_for_sources()`.
- [ ] Update `ingest_path()` to reconcile the discovered source set.
- [ ] Run targeted tests and confirm pass.

### Task 4: Persistent Demo Setup

**Files:**
- Create: `scripts/seed_pod_demo.py`
- Modify: `Makefile`
- Modify: `docs/DEMO_RUNBOOK.md`
- Test: `tests/test_demo_setup.py`

**Interfaces:**
- Produces Make target: `demo-setup`
- Produces script: `PYTHONPATH=src python scripts/seed_pod_demo.py`

- [ ] Write failing test for persistent demo setup helper or script behavior.
- [ ] Run targeted test and confirm failure.
- [ ] Add idempotent demo seeding script for live Pod Dock state.
- [ ] Add `demo-setup` Make target.
- [ ] Update runbook to distinguish `pod-demo` from live `demo-setup`.
- [ ] Run targeted test and `make demo-setup`.

### Task 5: Prompt Trust Hardening

**Files:**
- Modify: `src/memory_pod/prompt_assembly.py`
- Test: `tests/test_prompt_assembly.py`
- Test: `tests/test_pod_stack.py`

**Interfaces:**
- No public API changes.
- Stack prompt must separate private Base context from advisory Shared Pod context.

- [ ] Write failing test for advisory Shared Pod wording.
- [ ] Run targeted test and confirm failure.
- [ ] Update stack prompt copy.
- [ ] Run targeted tests and confirm pass.

### Task 6: Full Verification And Commit

**Files:**
- All touched files.

- [ ] Run `make check`.
- [ ] Run `make demo`.
- [ ] Run `make demo-learn`.
- [ ] Run `make pod-demo`.
- [ ] Run `make demo-setup`.
- [ ] Run `git diff --check`.
- [ ] Run `make clean`.
- [ ] Commit implementation changes with `[mvp] Harden portable Pod demo and write boundaries`.

