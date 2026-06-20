# Collaboration Guide

This repo follows `PROJECT_DESCRIPTION_V3.md`. If anything here conflicts with
that constitution, the constitution wins.

## Working Rule

Two people should work on opposite sides of the `augment()` contract:

- **Engine owner:** everything behind `augment()`.
- **Interaction owner:** everything that calls `augment()`.

Do not casually edit files owned by the other lane. If a change must cross the
boundary, agree on the public function signature first, then make the smallest
cross-lane edit possible.

## Lane A — Engine

Primary files:

- `src/memory_pod/augment.py`
- `src/memory_pod/prompt_assembly.py`
- `src/memory_pod/retrieval.py`
- `src/memory_pod/embeddings.py`
- `src/memory_pod/memory_store.py`
- `src/memory_pod/ingest.py`
- `tests/test_augment.py`
- `tests/test_retrieval.py`

Start here:

```bash
git checkout main
git pull --ff-only
git checkout -b feat/engine-remember-writeback
```

First task: implement local-only `remember(text, profile)` write-back and tests.

## Lane B — Interaction And Demo

Primary files:

- `src/memory_pod/hotkey_popup.py`
- `src/memory_pod/os_loop.py`
- `src/memory_pod/cli.py`
- `scripts/`
- `README.md`
- `docs/DEMO_RUNBOOK.md`

Start here:

```bash
git checkout main
git pull --ff-only
git checkout -b feat/interaction-popup-debug
```

First task: show retrieved memories and similarity scores in the Tier 1 popup.

## Shared Files

Avoid editing these at the same time:

- `ROADMAP.md`
- `README.md`
- `pyproject.toml`
- `requirements.txt`

If a shared file needs an update, make it in a small standalone commit.

## Before Every Commit

Run:

```bash
make check
make demo
make clean
```

Generated `memories.jsonl` files must not be committed. Demo seed files
`data/profiles/*/memory.md` are allowed in git.

