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

## Demo 3 — "It Just Learned" (write-back)

Goal: prove the memory grows. Teach a brand-new fact, then watch the next prompt
use it. Self-contained (throwaway profile, no setup, works offline):

```bash
make demo-learn
```

Expected: the furnished prompt for `"help me write a marathon training plan"`
now contains the marathon-training fact that was remembered one step earlier.

CLI variant (any profile):

```bash
PYTHONPATH=src python -m memory_pod.cli remember --profile alice "Alice just won a Rhodes scholarship."
PYTHONPATH=src python -m memory_pod.cli augment --profile alice --debug "help me write my bio"
```

## Demo 4 — Tier 1 Popup

```bash
PYTHONPATH=src python -m memory_pod.hotkey_popup
```

Press `Option + Enter`, then:

1. Type a vague prompt → **Furnish** → the furnished prompt and the retrieved
   memories with similarity scores both appear.
2. **Copy** → paste into a model.
3. **Remember** → type a fact in the top box and click Remember to write it back
   locally (the status line confirms). Furnish again to show it was learned.

If macOS hotkeys fail, use the CLI demo immediately.

## Demo 5 — Tier 2 Dry-Run Only

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

