# Task Board

This is the hackathon execution board. Keep it short and honest.

## Now

### Engine: Local Write-Back

Owner: Engine lane

Files:

- `src/memory_pod/memory_store.py`
- `src/memory_pod/augment.py` or new `src/memory_pod/remember.py`
- `tests/`

Acceptance:

- Add `remember(text, profile)` with no cloud calls.
- Store records in the same local JSONL profile store.
- Add CLI-ready function surface, but CLI wiring can be a separate interaction
  task.
- `make check` passes.

Suggested branch:

```bash
feat/engine-remember-writeback
```

### Interaction: Popup Debug View

Owner: Interaction lane

Files:

- `src/memory_pod/hotkey_popup.py`
- maybe `src/memory_pod/cli.py`

Acceptance:

- Popup uses `augment_for_profile(...)`, not raw `augment(...)`, where debug data
  is needed.
- Popup shows final furnished prompt plus retrieved memories and scores.
- Copy still works.
- No vector store internals are imported.
- `make check` passes.

Suggested branch:

```bash
feat/interaction-popup-debug
```

## Next

### Interaction: CLI `remember`

Owner: Interaction lane after Engine lands `remember()`

Acceptance:

- `python -m memory_pod.cli remember --profile alice "..."` writes local memory.
- `augment --debug` can retrieve the newly remembered text.

### Engine: Smarter Prompt Assembly

Owner: Engine lane

Acceptance:

- Keep `augment(raw_prompt: str) -> str` unchanged.
- Add rule-based local structure for task intent and memory categories.
- No external LLM or cloud call.

### Interaction: Demo Recording

Owner: Interaction lane

Acceptance:

- Record Tier 0 compare demo.
- Record Tier 1 popup demo.
- Record Tier 2 dry-run only if stable.

## Done

- Tier 0 local file ingest -> embed -> retrieve -> augment.
- Same prompt / different user compare demo.
- Embedder mismatch protection.
- `compare --reingest`.
- Tier 2 default dry-run.

