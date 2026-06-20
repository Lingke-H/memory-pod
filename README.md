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

Furnish one prompt:

```bash
python -m memory_pod.cli augment --profile alice --debug "help me prepare for this interview"
```

## Checks

```bash
python -m compileall src tests scripts
pytest
```

## macOS Note

Tier 1 and Tier 2 use global hotkeys and simulated keypresses. macOS may require
Accessibility permission for the terminal or Python app running the daemon.

## Privacy Boundary

Memory Pod never reads third-party cloud memory or login sessions. Memory comes
only from local files the user points at and optional local write-back.
