# Demo Runbook

The must-survive demo is Tier 0. Tier 1 and Tier 2 are bonuses.

## Pre-Demo Setup

```bash
git checkout main
git pull --ff-only
python -m venv .venv
source .venv/bin/activate
make setup
python scripts/download_model.py
make check
make demo-reingest
make clean
```

If the embedding model cannot be downloaded, the hashing fallback still works.
Do not debug network during judging.

## Demo 1 — Main Event

Goal: prove that the same vague prompt becomes personalized through local memory.

```bash
make demo
```

Expected:

- Alice retrieves AI safety / academic application context.
- Bob retrieves B2B founder / sales context.
- Debug output shows sources and similarity scores.

## Demo 2 — Local File Ingest

```bash
PYTHONPATH=src python -m memory_pod.cli ingest --profile alice ./data/profiles/alice/memory.md
PYTHONPATH=src python -m memory_pod.cli augment --profile alice --debug "help me prepare this application"
```

Show that `memory.md` is the source of truth.

## Demo 3 — Tier 1 Popup

```bash
PYTHONPATH=src python -m memory_pod.hotkey_popup
```

Press `Option + Enter`, type a vague prompt, furnish, copy, paste into a model.

If macOS hotkeys fail, use the CLI demo immediately.

## Demo 4 — Tier 2 Dry-Run Only

```bash
PYTHONPATH=src python -m memory_pod.os_loop
```

Use only on one target site. It should paste the furnished prompt and not submit
automatically.

Mandatory fallback:

- Keep a screen recording of one successful Tier 2 run.
- If live automation behaves strangely, stop and return to Tier 1 or CLI.

## Reset

```bash
make clean
make demo-reingest
```

