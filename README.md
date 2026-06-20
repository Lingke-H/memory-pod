# Memory Pod

Memory Pod is a local-first personal memory engine for hackathon prototyping.
It ingests local memory files, retrieves relevant context, and furnishes vague
AI prompts with private user-owned memory.

Read [PROJECT_DESCRIPTION_V3.md](PROJECT_DESCRIPTION_V3.md) before coding. It is
the source of truth for scope, tier boundaries, and demo priorities.

## Current Scaffold

- `src/memory_pod/os_loop.py`: Tier 2 clipboard injection boilerplate.
- `src/memory_pod/__init__.py`: package scaffold.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Early Smoke Check

```bash
python -m py_compile src/memory_pod/os_loop.py
```

On macOS, OS-level hotkeys and simulated keypresses require Accessibility
permission for the terminal or Python app running the daemon.

