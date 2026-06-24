# Collaboration Guide

Memory Pod follows [PROJECT_DESCRIPTION_V4.md](../PROJECT_DESCRIPTION_V4.md).
If another document conflicts with that product constitution, v4 wins.

## Working Boundary

- **Engine:** storage, ingest, embeddings, retrieval, prompt assembly, and the
  public `augment()` / `remember()` contracts.
- **Interaction:** CLI, Pod Dock, OS hotkeys, onboarding, and demo scripts that
  consume the public engine contracts.
- Agree on public signatures before making a change that crosses this boundary.
- Keep Shared Pod guidance advisory and keep personal write-back limited to a
  private writable Base Pod.

## Shared Files

Coordinate edits to `README.md`, `ROADMAP.md`, `pyproject.toml`,
`requirements.txt`, and the public interfaces in `src/memory_pod/augment.py`.

## Branch and Commit Practice

Use focused branches and commits. The conventional Codex branch prefix is
`codex/`; human contributors may follow the repository's existing naming
convention. Do not commit generated Pod stores, model caches, `.env`, or build
artifacts.

## Verification Before Handoff

```bash
source .venv/bin/activate
make check
make pod-demo
git status --short
```

Run macOS hotkey checks manually when interaction code changes. Never treat a
manual prompt injection as successful unless the prompt remains unsubmitted for
user review.

Use [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) to record the branch, scope,
contract changes, verification evidence, and remaining risks.
