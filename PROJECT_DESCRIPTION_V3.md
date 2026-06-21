# Memory Pod — Project Constitution v3

> **Superseded for new work:** MVP v1.1 terminology and scope now live in
> [PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md). Keep this document as
> the historical v1.0 constitution and tier rationale.

> Project-level context for Codex / Claude Code during a **24-hour hackathon**.
> Read this before every coding task. The goal is to protect the product thesis,
> tier boundaries, demo reliability, and the local-first privacy promise.
>
> **Changes from v2:** scope tightened to 24h; memory source now explicitly comes
> from the user's own local files (`memory.md`, notes); a hard red line added
> against touching any third-party cloud memory; tier priority clarified so the
> local engine is the only "must-survive" core and all OS injection is bonus;
> Terminal Radar demoted to "do not build unless absurdly ahead of schedule."

---

## 1. What We Are Building

We are building **Memory Pod**: a **local-first personal memory engine** that
solves AI **context fragmentation**. Today, a user becomes a stranger every time
they move between ChatGPT, Claude, Cursor, Notion, email, or a new conversation.
Memory Pod keeps a private, vectorized memory of the user **on their own machine**,
retrieves the most relevant memories for the current prompt, and turns a vague
prompt into a personalized, context-rich one.

The product thesis:

> **Your memory should belong to you, not to the model you happen to use today.**

Memory Pod is not a generic prompt optimizer. It is a portable, user-owned
personal memory layer.

---

## 2. Core Differentiator

Generic prompt enhancers produce similar outputs for everyone. Memory Pod
produces different outputs because it uses **local personal memory**.

The killer demo:

1. Two local user profiles exist on the same laptop.
2. Both users type the same vague prompt, such as:
   `"help me write this application"`
3. Memory Pod retrieves different memories for each user.
4. The final furnished prompt becomes deeply personalized:
   - User A: research-focused, academic, AI safety context.
   - User B: founder-focused, concise, B2B product context.

If a feature does not strengthen this memory-driven personalization story, it is
out of scope for the hackathon.

---

## 3. Where Memory Comes From (READ THIS — it was the missing piece)

Memory Pod's memory has exactly two legitimate sources. Both are 100% local.

### Source A — Import the user's own local files (PRIMARY)

The main way memory enters the system is by **ingesting the user's existing local
documents**: a `memory.md`, Obsidian/notes vault, journal, or a `CLAUDE.md`-style
context file. The user points Memory Pod at a file or folder; we read it, chunk
it, embed each chunk, and store it locally.

This is standard RAG ingestion:

```
local .md / .txt file(s) -> split into chunks (by heading/paragraph)
  -> embed each chunk -> store in local vector store
```

Why this matters: it means the user does NOT hand-type memories one by one. It
plugs directly into the `memory.md` / `CLAUDE.md` culture people already know,
and it reinforces the local-first story — their notes never leave the machine.

The seed demo profiles (alice/bob) are themselves just `memory.md`-style files we
wrote in advance — so the demo data and the "import a local file" feature are the
same mechanism.

### Source B — Write-back from usage (LIGHT, optional accent)

After a furnish, optionally append the new exchange to the local store so it
"grows." Build only a minimal version: append one record, show in the demo that
"it just remembered that." Do NOT build complex auto-extraction in 24h.

### What memory must NEVER come from

See Hard Constraints (Section 6). In short: **never read, scrape, or connect to
any third-party cloud memory** (ChatGPT memory, Claude memory, etc.). It is not
technically reliable, it violates their terms, and it destroys our entire
local-first thesis.

---

## 4. Build Tiers (priority = "what must survive," not "what looks coolest")

**Defining rule: Tier 0 is the ONLY must-survive core. Every OS-level injection
feature (Tier 1 and Tier 2) is a bonus. The project must be complete, deep, and
demo-able with Tier 0 alone.**

Rationale: the team has no prior OS-automation experience and demos on macOS,
where global-hotkey + keyboard simulation + clipboard hijacking is the most
fragile, permission-gated path. We refuse to bet the project on it.

### Tier 0 — Local Memory Engine (MUST work first, zero OS risk)

- **Ingest local files** (Source A): read `.md`/`.txt` -> chunk -> embed -> store.
- Local memory records stored in SQLite or JSONL.
- Local embeddings through `sentence-transformers` (`all-MiniLM-L6-v2`).
- Retrieval through ChromaDB, FAISS, or a NumPy cosine-similarity fallback.
- Stable public API:

```python
def augment(raw_prompt: str) -> str:
    """Return a memory-furnished prompt for the user's raw prompt."""
```

Minimum memory record schema (for hand-seeded / write-back records):

```json
{
  "id": "m_001",
  "type": "preference",
  "text": "User prefers concise, technically precise explanations.",
  "tags": ["writing_style"],
  "weight": 0.9,
  "created_at": "2026-06-20T12:00:00"
}
```

Tier 0 MUST include a debug mode that shows: raw prompt, retrieved memories,
similarity scores, final furnished prompt. (Judges love seeing the system think.)

### Tier 1 — Local Hotkey Popup (safe "Zero-UI", build only after Tier 0 is callable)

The SAFE interaction layer. A global hotkey (`pynput`) summons **our own minimal
floating input window** (NOT hijacking another app's input box). User types ->
`augment()` -> one-click copy, or paste into the previous window.

This deliberately avoids the contenteditable / async-clipboard hell of true
in-place injection.

Tier 1 must handle: macOS Accessibility permission failures (detect + tell the
user), re-entrant hotkey presses, and a dry-run mode (copy only, never auto-send).

### Tier 2 — True In-Place Clipboard Injection (STRETCH, only if Tier 0+1 stable)

The flashy version from earlier drafts:
`Cmd+A -> Cmd+X -> read clipboard -> augment -> write clipboard -> Cmd+V -> Enter`.

Constraints if attempted:
- Target **exactly one** environment (Claude web OR ChatGPT web — pick one).
- Handle: empty clipboard after cut, slow clipboard propagation, ghost inputs
  (tune sleeps), re-entrancy, Accessibility permission failure.
- **A screen recording of a successful run is mandatory before demo.** If it acts
  up live, play the recording and fall back to Tier 1.

### Tier 3 — Terminal Radar (DEFAULT: DO NOT BUILD in 24h)

Cut by default. Only touch it if Tier 0+1 are done, polished, demoed, and there
are hours to spare. If shown at all, it can be a single static ASCII slide framed
as "future vision," not running code.

---

## 5. Python Project Structure

```text
memory-pod/
  PROJECT_DESCRIPTION_V3.md
  README.md
  requirements.txt
  data/
    profiles/
      alice/
        memory.md          # seed profile = a real memory.md-style file
      bob/
        memory.md
  src/
    memory_pod/
      __init__.py
      cli.py
      config.py
      augment.py           # owns public augment(raw_prompt) -> str
      ingest.py            # NEW: read local .md/.txt -> chunk -> embed -> store
      memory_store.py      # load/write local memories
      embeddings.py        # local embedding model + numpy fallback
      retrieval.py         # top-k semantic search
      prompt_assembly.py   # retrieved memories -> hidden context -> furnished prompt
      hotkey_popup.py      # Tier 1: hotkey + own popup window
      os_loop.py           # Tier 2 ONLY: clipboard hijack macro
      radar.py             # Tier 3 ONLY: do not build by default
  tests/
    test_augment.py
    test_retrieval.py
  scripts/
    download_model.py      # run in first 2 hours
    seed_demo_profiles.py
```

Interaction code (`hotkey_popup.py`, `os_loop.py`) must not reach into vector DB
internals. It only calls `augment()`.

---

## 6. Hard Constraints

- **Local-first is sacred.** User memory must not leave the machine.
- **No cloud memory storage.**
- **🚫 RED LINE: never read, scrape, connect to, or reverse-engineer any
  third-party cloud memory or login session** (ChatGPT memory, Claude memory,
  Notion AI memory, etc.). Memory comes ONLY from the user's own local files
  (Section 3, Source A) or local write-back (Source B). If a task seems to
  require this, STOP and flag it.
- **No Chrome extension.**
- **No separate web UI for the core product.**
- **macOS is the demo platform.** All OS code must account for Accessibility
  permission; pre-verify hotkey capture works before building on top of it.
- **Pre-download the embedding model in the first 2 hours.** Never assume network
  at demo time.
- **Tier 0 is the only must-survive core.** All OS injection is bonus.
- **Tier 2 targets one site only, if attempted, with a recorded fallback.**
- **Terminal Radar is cut by default.**
- **Keep agent work separated by files/modules** (two agents run in parallel).
- **Never silently violate the `augment()` contract.**

---

## 7. Demo Script

### Demo 1 — Same Prompt, Different Memory (THE MAIN EVENT)

```bash
python -m memory_pod.cli augment --profile alice "help me write this application"
python -m memory_pod.cli augment --profile bob   "help me write this application"
```

Show: same raw prompt, different retrieved memories (with similarity scores via
debug mode), different final prompts.

### Demo 2 — Import a Local Memory File (proves Source A)

```bash
python -m memory_pod.cli ingest --profile alice ./data/profiles/alice/memory.md
```

Show: a plain `memory.md` becomes searchable memory. Optionally add one new line
to the file, re-ingest, and show the next furnish reflects it ("it just learned").

### Demo 3 — Hotkey Popup (Tier 1)

1. Press `Option + Enter` anywhere -> Memory Pod popup appears.
2. Type a vague prompt -> furnished prompt shown -> one-click copy.
3. Paste into Claude/ChatGPT.

### Demo 4 — In-Place Injection (Tier 2, ONLY if stable; else play recording)

Press hotkey in Claude/ChatGPT, watch it select/cut/augment/paste. Dry-run
variant: it pastes the furnished prompt and the user presses Enter manually.

---

## 8. Judging Story

Pitch as infrastructure, not a chatbot:

1. AI tools remember inside silos.
2. People work across many tools.
3. Memory Pod makes memory portable, local, and user-owned — fed by the notes
   you already keep.
4. It works where the user already types.
5. The same prompt becomes personalized because the system remembers the person.

Do not pitch "prompt optimization." Pitch:

> **A local, user-owned memory layer for every AI interface.**

---

## 9. What To Cut First (24h triage)

If time is short, cut in this order:

1. Terminal Radar — entirely (already cut by default).
2. Tier 2 true in-place auto-submit (fall back to Tier 1 popup + copy/paste).
3. ChromaDB/FAISS, if NumPy cosine retrieval already works.
4. Memory write-back (Source B accent).
5. Fancy memory editing UI.

Do NOT cut:

- Local file ingestion (Source A) — it's how memory gets in.
- Local memory retrieval.
- Personalized prompt assembly.
- The same-prompt / different-user demo (Demo 1).
- A stable way to copy or paste the furnished prompt.

---

## 10. Suggested 24h Timeline

| Hours | Work | Risk |
|-------|------|------|
| 0–2 | Setup; **pre-download embedding model**; ChromaDB/NumPy store smoke test; verify macOS hotkey permission early | low |
| 2–6 | Tier 0: ingest `memory.md` -> chunk -> embed -> retrieve -> `augment()` (dummy assembly first) | low |
| 6–9 | Prompt assembly quality (intent -> missing-info detection -> memory fill -> rebuild) | med |
| 9–13 | Tier 1: `pynput` hotkey + own popup window, wired to `augment()` | med |
| 13–14 | **Checkpoint:** Tier 0+1 stable? yes -> attempt Tier 2; no -> polish demo | — |
| 14–18 | Tier 2 on ONE site, OR (fallback) build Demo 1/2 polish + debug view | high |
| 18–21 | Demo script + **record successful runs as fallback** | — |
| 21–24 | Pitch, buffer, sleep (keep the buffer — do not debug to the wire) | — |
