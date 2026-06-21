# Demo Runbook — Portable Pods

## Pre-Demo

```bash
git checkout main
git pull --ff-only
source .venv/bin/activate
make check
make pod-demo
make demo-setup
```

Grant the Terminal Accessibility permission before the live popup. Keep one
terminal ready with `make popup`.

`make pod-demo` is an isolated proof that exports, imports, docks, and retrieves
inside a temporary directory. `make demo-setup` seeds the persistent local Pod
store used by the popup, so the live Dock can see Base `jiahan` and Shared
`senior-review`.

For a first-run product walkthrough rather than the frozen judge script, run
`make onboard`. It creates a private My Pod from a few "about you" answers and
loads starter Expert Pods. Keep this as the answer to "where does the user's
memory come from?" without changing the main three-minute demo path.

## Three-Minute Story

### Act 1 — Own and Carry

Run:

```bash
make pod-demo
```

Say:

> “This is not another model-owned memory. It is an inspectable Pod the author
> can carry and share as a file.”

Point out that `.mpod` contains explicit playbook records but no embedding or
absolute private path. Author identity is self-declared.

### Act 2 — Dock, Don’t Copy a Brain

Show Base-only, then Base + Senior Architecture Review. Point to the retrieved
Pod IDs and the different sections for private context and shared guidance.

Say:

> “The recipient keeps their own preferences. The shared Pod contributes an
> explicit review playbook; it does not replace their identity.”

Show the unrelated marathon task returning zero Shared Playbook memories. This
is the proof that Memory Pod is dynamic retrieval, not a static mega-prompt.

### Act 3 — Same Pod, Any Model

Run `make demo-setup`, then `make popup`, press `Option + Enter`, and Dock the
Shared Pod. Uncheck one retrieved context row and show the furnished prompt
rebuilding immediately. Copy it and paste the same approved context into ChatGPT
and Claude side by side. Do not auto-send.

**Optional flourish — in-place injection:** instead of copy/paste, run
`make os-loop`, focus the AI's input box, press `Option + Enter`, and the
furnished prompt is pasted in place (never submitted). Use on ONE site only and
keep a screen recording as a fallback; if it misbehaves live, fall back to the
popup copy flow above.

## Fallbacks

- Hotkey ignored: verify Terminal under macOS Privacy & Security > Accessibility.
- Popup unavailable: run `memory-pod augment --base-pod ... --shared-pod ... --debug`.
- Model cache unavailable: the deterministic local hashing fallback still
  works and rejects records with no real lexical overlap.
- Any presentation issue: `make pod-demo` alone proves Own, Carry, Dock, and
  selective retrieval.

## Legacy Demos

```bash
make demo
make demo-learn
```

These remain useful supporting demos, but the main v1.1 story is Portable Pods.
