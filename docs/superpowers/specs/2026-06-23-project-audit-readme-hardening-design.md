# Memory Pod Project Audit and README Hardening Design

## Goal

Bring the existing Memory Pod repository to a reliable, internally consistent,
demo-ready state without adding product features or changing its established
local-first behavior. The final README will be a professional, comprehensive,
bilingual reference with English first and Chinese second.

## Verified Current State

- The repository implements the v4 Portable Pods and Pod Dock product model.
- The project virtual environment is usable on Python 3.13.9.
- The complete automated suite passes in that environment: 90 tests passed.
- `make check` can accidentally use a system Python without the declared runtime
  dependencies, even when a working `.venv` exists in the repository.
- `ROADMAP.md`, `docs/COLLABORATION.md`, and `docs/TASK_BOARD.md` still contain
  v3-era source-of-truth language or task statuses that no longer describe the
  implemented repository accurately.
- `.env.example` exposes only legacy profile/model settings and does not explain
  the current storage-home convention.
- The working tree contains four untracked duplicate-looking files whose names
  contain ` 2`. They differ from the tracked files and are user-owned content.

## Scope

### In Scope

1. Make local development and verification commands more deterministic.
2. Align active project documentation with `PROJECT_DESCRIPTION_V4.md`.
3. Refresh configuration examples to match current supported behavior.
4. Replace `README.md` with an accurate English-and-Chinese project reference.
5. Verify tests, compilation, command help, and documentation links.

### Out of Scope

- New retrieval, Pod, synchronization, marketplace, browser-extension, or agent
  features.
- Changes to public product behavior or stable Python interfaces.
- UI redesign or automatic prompt submission.
- Destructive cleanup of local stores, caches, or untracked files.
- Editing or deleting `README 2.md`, `docs/DEMO_RUNBOOK 2.md`,
  `scripts/judge_demo 2.py`, or `src/memory_pod/hotkey_popup 2.py`.

## Approach

Use a targeted hardening pass rather than README-only editing or broad
refactoring. The implementation will preserve the working architecture and
focus on reproducibility, factual documentation, and clean operator guidance.

## Planned Changes

### Development Workflow

Update the Makefile's Python selection so repository commands prefer
`.venv/bin/python` when that interpreter exists, while preserving an explicit
`PYTHON=...` override and a usable fallback for initial setup. Add focused tests
for the selection contract before changing the Makefile.

### Configuration Example

Update `.env.example` to document current supported variables, including the
storage-home override and local embedding model selection. Retain legacy profile
compatibility only where it is still supported by the code.

### Documentation Reconciliation

- Treat `PROJECT_DESCRIPTION_V4.md` as the active product source of truth.
- Mark historical planning documents clearly when retaining their original
  context.
- Update collaboration and task-status language so completed capabilities are
  not presented as pending work.
- Keep implementation details and demo instructions consistent with the actual
  CLI and Makefile targets.

### Bilingual README

The English section will appear first, followed by a complete Chinese section.
Both versions will cover the same substantive information:

1. Product overview and value proposition.
2. Current status and implemented capabilities.
3. Trust, privacy, and sharing boundaries.
4. Architecture and end-to-end data flow.
5. Platform and system requirements.
6. Installation and first-run setup.
7. Base Pod and Shared Pod workflows.
8. CLI command reference and desktop interaction modes.
9. Demo and development commands.
10. Repository structure.
11. Testing and verification.
12. Troubleshooting.
13. Known limitations and out-of-scope features.
14. Related project documentation.

Commands will be copied from verified entry points rather than inferred from
older planning documents. Claims about privacy will distinguish local storage
and retrieval from the moment a user sends approved context to an external AI
provider.

## Architecture and Data Flow

No architecture change is planned. Documentation will describe the existing
flow accurately:

1. Local Markdown or text is ingested into a Base or locally authored Shared
   Pod.
2. Records and embeddings are stored in local JSONL Pod stores.
3. Retrieval selects relevant records for a raw prompt.
4. Prompt assembly separates private Base context from advisory Shared context.
5. The user reviews and optionally deselects context.
6. Memory Pod copies or injects the furnished prompt but never submits it.
7. Any approved context leaves the local boundary only when the user sends the
   resulting prompt to another provider.

## Error Handling and Safety

- Make targets must fail with normal command errors and must not silently install
  or mutate dependencies during verification.
- Documentation must state macOS Accessibility requirements for global hotkeys.
- Ollama polishing must be described as optional, local, and failure-tolerant.
- Imported Shared Pods must be described as read-only and author metadata as
  self-declared rather than cryptographically verified.
- No cleanup command will run against the user's untracked duplicate files.

## Verification

The hardening pass is complete only when all applicable checks succeed:

1. Focused tests for Makefile Python selection.
2. Full `make check` using the repository virtual environment.
3. CLI help smoke tests for the top-level and Pod subcommands.
4. README link and referenced-path validation.
5. Search for stale active-document references to the v3 source of truth.
6. Review of `git diff` confirming that untracked duplicate files were untouched.

Manual macOS hotkey interaction is outside automated verification; the README
will identify its permission and platform requirements explicitly.

## Acceptance Criteria

- Existing product behavior and public interfaces remain unchanged.
- The full automated suite passes.
- A new contributor can set up, verify, and run the implemented workflows using
  the README alone.
- English and Chinese README sections are complete, structurally parallel, and
  technically consistent.
- Active documentation points to the v4 product constitution.
- User-owned untracked files remain unchanged and untracked.
