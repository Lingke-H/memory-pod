# Memory Pod — Historical Optimization and Delegation Roadmap

> **Status:** Historical hackathon planning document. Several items below have
> already been implemented, and individual status notes may not reflect the final
> repository state. Use [PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md)
> for current product scope and [README.md](README.md) for verified setup and usage.

## Context

Tier 0 (the local memory engine) is complete and working (commit `70659bb`).
The guiding architectural seam for everything below is the **`augment()`
contract** (`src/memory_pod/augment.py`). Everything *behind* it (retrieval,
embeddings, assembly, storage) is one person's domain; everything that *calls* it
(CLI, popup, clipboard loop) is the other's. This matches the constitution's
rule: "keep agent work separated by files/modules."

---

## Part 1 — Optimizations (correctness + speed)

### 1.1 Fix the embedder-mismatch hazard (HIGHEST PRIORITY — protects the demo)
`embeddings.get_embedder()` falls back to `HashingEmbedder` when the
`all-MiniLM-L6-v2` model isn't cached locally. If a profile was **ingested** with
one embedder and later **queried** with a different one, the vectors live in
different spaces → retrieval returns garbage with no error. On stage this looks
like "the personalization broke."
- **Fix:** stamp each record with the embedder identity at ingest time (add an
  `embedder` field to `MemoryRecord` in `memory_store.py`, set in `ingest.py`).
  In `retrieval.py`, detect a mismatch between the active embedder and stored
  records and either (a) re-embed on the fly or (b) emit a loud warning telling
  the user to re-ingest. Reuse the existing `get_embedder()` and `MemoryRecord`
  plumbing.
- **Status:** implemented after this roadmap was fetched. Mismatched records are
  re-embedded on the fly so retrieval stays correct even if the local model cache
  changes between ingest and query.

### 1.2 Stop `compare` from re-ingesting every run
`cli._ensure_demo_profiles_ingested()` re-ingests (and re-embeds) alice + bob on
**every** `compare` call. It's idempotent (content-hashed IDs in
`ingest.make_record_id`) but wasteful and adds latency to the marquee demo.
- **Fix:** skip ingest when the store already exists and the source `memory.md`
  is unchanged (compare file mtime vs. `store_path` mtime via
  `memory_store.store_path`). Keep a `--reingest` flag to force it for the "it
  just learned" demo.
- **Status:** implemented. `compare` skips unchanged demo stores and supports
  `--reingest` for forced refreshes.

### 1.3 Cache the per-profile memory matrix
`retrieval._memory_vectors()` rebuilds and re-normalizes the full NumPy matrix on
every call, even though stored embeddings are already normalized. Cheap to cache.
- **Fix:** memoize the stacked matrix per `(profile, store mtime)` so repeated
  popup/CLI calls are instant.

### 1.4 Minor depth (optional, only if ahead)
- Add chunk overlap in `ingest.chunk_text` (currently hard splits at 900 chars,
  no overlap) to improve recall.
- `weight` is uniformly `1.0` today, so the weighting in `retrieval.retrieve` is
  a no-op — populate weights at ingest (e.g. headings/preferences weighted
  higher) or note it's reserved.

---

## Part 2 — Four Features (ordered by wow-per-hour)

### 2.1 Write-back / Source B — "it just learned that!" (SAFE, HIGH WOW)
After a furnish, optionally append the new fact/exchange to the local store so
memory grows.
- **Engine side:** add a `remember(text, profile, ...)` helper that builds a
  `MemoryRecord` and calls the existing `memory_store.upsert_records()`. Keep it
  minimal — append one record, no complex auto-extraction (constitution forbids
  it in 24h).
- **Interaction side:** expose it as a CLI `remember` subcommand / `--remember`
  flag in `cli.py` and a "Remember" button in the popup.
- **Demo:** tell it a new fact → re-ask → watch the new memory get retrieved.

### 2.2 Popup debug view — make the magic visible (SAFE, LOW EFFORT)
`hotkey_popup.py` currently calls `augment()` and shows only the final text.
- **Fix:** switch it to `augment_for_profile(...)` and render
  `AugmentResult.memories` (each with its similarity score) in a panel — reuse
  the existing `prompt_assembly.format_debug()` output or iterate `.memories`
  directly. Mirrors the CLI `--debug` so judges see retrieved memories + scores
  in the GUI.

### 2.3 Tier 2 `os_loop` dry-run polish (FLASHIEST, RISKIEST LIVE)
`os_loop.py` already calls the real `from memory_pod.augment import augment`.
- **Fix:** keep `HotkeyConfig.submit_after_paste = False` by default (dry-run:
  paste the furnished prompt, user presses Enter) so nothing auto-fires on stage.
- **Status:** implemented. Tier 2 now defaults to dry-run behavior.
- **Constitution requirements:** target exactly ONE site (Claude web OR ChatGPT
  web), and **record a successful run as a mandatory fallback** before demo. If
  it misbehaves live, play the recording and fall back to the Tier 1 popup.

### 2.4 Smarter prompt assembly — depth under scrutiny (MOST WORK, LEAST VISUAL)
`prompt_assembly.assemble_prompt()` currently concatenates retrieved memories
under `[Hidden Context]`.
- **Fix:** add a lightweight intent + missing-info step (the constitution's hours
  6–9 goal: "intent → missing-info detection → memory fill → rebuild"). Keep it
  rule-based/local (detect task type, then structure the hidden context as
  persona + style + relevant facts) — no external LLM call, stays local-first.
  **Must not change the `augment()` signature.**

---

## Part 3 — Delegation between 2 people (the `augment()` seam)

The clean split is **behind vs. in front of `augment()`**, giving each person
disjoint files so they can work fully in parallel with minimal merge conflicts.

### Person A — "Engine" (everything behind `augment()`)
**Owns:** `prompt_assembly.py`, `retrieval.py`, `embeddings.py`,
`memory_store.py`, `ingest.py`, `augment.py`, `tests/`
**Tasks:** Opt 1.1 embedder-stamp + mismatch handling, Opt 1.3 matrix caching,
Opt 1.4 (if time), Feature 2.1 storage (`remember()` helper), Feature 2.4
smarter assembly, and tests for all of it.
**Delivers a stable interface contract:** `augment_for_profile(prompt, profile)`
returns an `AugmentResult` with `.furnished_prompt` and `.memories` (each
carrying a similarity score); plus `remember(text, profile)`.

### Person B — "Interaction & Demo" (everything that calls `augment()`)
**Owns:** `hotkey_popup.py`, `os_loop.py`, `cli.py`, `scripts/`, `README.md`,
demo recordings
**Tasks:** Feature 2.2 popup debug view, Feature 2.1 surfaces (CLI
`remember`/`--remember` + popup "Remember" button), Feature 2.3 Tier 2 wiring +
dry-run + screen recording, Opt 1.2 `compare` skip-reingest, demo script polish.
**Constraint (from constitution):** interaction code only calls `augment()` /
`augment_for_profile()` / `remember()` — it never reaches into the vector store
or retrieval internals.

### Coordination
- **Single shared contract** = the `AugmentResult` shape + `remember()`
  signature. Agree on it first (15 min), then both work independently.
- Only `cli.py` is a light coupling point (B owns it but consumes A's
  `remember()`); resolve by A landing `remember()` early.
- Suggested order: A ships Opt 1.1 (de-risks the whole demo) and the contract
  first; B builds the popup debug view and `compare` polish against the existing
  contract in parallel; both converge on write-back; Tier 2 last (riskiest,
  optional).

---

## Verification

```bash
# Setup
cd "/Users/huangjiahan/Documents/2026 Cal Hack"
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python scripts/download_model.py        # pre-cache model (or rely on hashing fallback)

# Tier 0 regression + new engine tests (Person A)
pytest
python -m compileall src tests scripts

# Marquee demo (Opt 1.1/1.2, should be fast + correct)
python -m memory_pod.cli compare --debug "help me write this application"
# alice = academic/AI-safety framing, bob = B2B/founder framing, with scores

# Write-back "it just learned" (Feature 2.1)
python -m memory_pod.cli remember --profile alice "Alice just won a Rhodes scholarship."
python -m memory_pod.cli augment --profile alice --debug "help me write my bio"
# new memory should appear in retrieved set

# Popup debug view (Feature 2.2) — manual, macOS Accessibility on
python -m memory_pod.hotkey_popup     # Alt+Enter → type → see memories+scores → Copy / Remember

# Tier 2 dry-run (Feature 2.3) — manual, ONE site, record it
python -m memory_pod.os_loop          # confirm dry-run pastes furnished prompt, no auto-submit
```

**Demo-day guardrails (from constitution):** pre-download the model; record a
successful Tier 2 run as fallback; Tier 0 `compare` is the must-survive demo — if
anything else breaks, fall back to it.
