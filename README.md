# Memory Pod

Memory Pod is a local-first personal memory engine for hackathon prototyping. It
ingests local `memory.md` / `.txt` files, retrieves relevant context, and
furnishes vague AI prompts with private user-owned memory.

Read [PROJECT_DESCRIPTION_V3.md](PROJECT_DESCRIPTION_V3.md) before coding. It is
the source of truth for scope, tier boundaries, and demo priorities.

## Scope

- Tier 0: local file ingestion, local embedding, retrieval, and `augment()`.
- Tier 1: safe hotkey popup that calls `augment()`.
- Tier 2: true clipboard injection only as a stretch.
- Tier 3: Terminal Radar is intentionally cut by default.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Or use:

```bash
make setup
```

## Collaboration

- [Collaboration guide](docs/COLLABORATION.md)
- [Task board](docs/TASK_BOARD.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md)
- [Handoff template](docs/HANDOFF_TEMPLATE.md)

The repo is split across two lanes:

- Engine: everything behind `augment()`.
- Interaction: everything that calls `augment()`.

## Demo Commands

Ingest the checked-in demo memory files:

```bash
python -m memory_pod.cli ingest --profile alice ./data/profiles/alice/memory.md
python -m memory_pod.cli ingest --profile bob ./data/profiles/bob/memory.md
```

Run the main "same prompt, different memory" demo:

```bash
python -m memory_pod.cli compare --debug "help me write this application"
```

Or:

```bash
make demo
```

Furnish one prompt:

```bash
python -m memory_pod.cli augment --profile alice --debug "help me prepare for this interview"
```

Run the frozen 3-minute judge demo (compare → "it just learned" → live popup cue):

```bash
make judge
```

See the [Demo runbook](docs/DEMO_RUNBOOK.md#3-minute-judge-script) for the spoken
script, timing, and fallbacks.

## Checks

```bash
python -m compileall src tests scripts
pytest
```

Or:

```bash
make check
```

## macOS Note

Tier 1 and Tier 2 use global hotkeys and simulated keypresses. macOS may require
Accessibility permission for the terminal or Python app running the daemon.

## Privacy Boundary

Memory Pod never reads third-party cloud memory or login sessions. Memory comes
only from local files the user points at and optional local write-back.
