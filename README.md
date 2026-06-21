# Memory Pod

Memory Pod is a local-first, inspectable context layer that works across AI
models. Create private and shareable Pods, Dock the context needed for a task,
approve the retrieved snippets, and copy the furnished prompt into any AI.

Read [PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md) before coding.

> **Own your Pod. Dock it anywhere. Share only what you choose.**

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
make setup
```

User Pods live under:

```text
~/Library/Application Support/Memory Pod/pods/
```

Set `MEMORY_POD_HOME` to override that location. Existing repo profile stores
can be copied non-destructively with:

```bash
memory-pod pod migrate-legacy
```

## First Run

Create your private My Pod and load the starter Expert Pods:

```bash
make onboard
```

Onboarding asks a few "about you" questions, writes the answers into your
private Base Pod, and seeds replaceable starter Expert Pods such as lawyer,
accountant, financial advisor, management consultant, marketing strategist, and
HR specialist. These starter Pods carry general professional best-practices (not
licensed advice) and are demos of the `.mpod` sharing model; a real expert can
replace them by exporting their own Shared Pod file.

If you only want to refresh the starter Expert Pods later:

```bash
make seed-experts
```

## Create Pods

Create a private Base Pod and ingest local notes:

```bash
memory-pod pod create --name "Jiahan" --id jiahan --kind private
memory-pod ingest --pod jiahan ~/Documents/notes
```

Create an explicit Expert Playbook that is safe to share:

```bash
memory-pod pod create \
  --name "Senior Architecture Review" \
  --id senior-review \
  --kind shared \
  --author "Alice" \
  --purpose "Architecture and PR review"

memory-pod ingest --pod senior-review ./architecture-playbook.md
memory-pod pod export senior-review --output Senior-Review.mpod
```

Preview and import a received Pod:

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

## Dock Context

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

The legacy `--profile` and `augment(raw_prompt)` interfaces remain supported.

Launch the macOS Pod Dock:

```bash
make popup
```

Press `Option + Enter`, select a Base and optional Shared Pod, review or
deselect retrieved context, then copy the furnished prompt. `Polish Locally`
can optionally ask local Ollama to turn the reviewed furnished prompt into a
cleaner copy-ready prompt; if Ollama is not running, the inspected furnished
prompt stays unchanged. The popup never auto-submits.

### In-place injection into an AI input box (Tier 2)

For a "no copy/paste" flow, a global hotkey can grab the focused input box,
furnish it with your Pod context, and paste it back in place:

```bash
make os-loop
# or choose pods explicitly:
PYTHONPATH=src python -m memory_pod.os_loop --base-pod jiahan --shared-pod senior-review
```

The default `make os-loop` target uses the frozen demo Pods from `make
demo-setup` (`jiahan + senior-review`) so it works reliably during a live demo.
Use `BASE_POD=... SHARED_POD=...` or the popup's **Confirm → Hotkey** button to
switch to your onboarded Base Pod and an industry Expert Pod.

Press the hotkey (`Option + Enter`) while your cursor is in the AI's text box.
It does `Cmd+A / Cmd+X`, furnishes the text, and pastes the result back. It
**never submits** — you review it and press Enter yourself. Use it on **one**
target site (ChatGPT *or* Claude web), grant Terminal Accessibility permission,
and keep a screen recording as a fallback. Not a browser extension.

To switch which Pods the hotkey uses **without restarting the daemon**, open the
popup (`make popup`), pick a Base/Shared Pod, and click **Confirm → Hotkey**. The
running OS loop picks up the new selection on the next `Option + Enter`. (Pass
`--no-follow-active-dock` to pin the launch pods instead.)

The OS loop does not learn automatically. To explicitly save the focused input
into your private Base Pod, press `Control + Shift + Enter`. That path uses
`Cmd+A / Cmd+C`, writes one local memory with source `os-hotkey`, restores your
clipboard, and does not paste or submit anything.

## Demos

```bash
make onboard       # First-run: create My Pod + starter Expert Pods
make pod-demo      # Own -> Carry -> Dock -> selective retrieval
make demo          # Same prompt, different private memories
make demo-learn    # Local write-back
make judge         # Frozen presentation path
```

See [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md).

## Checks

```bash
make check
```

## Privacy Boundary

The Pod store, embeddings, retrieval, and optional Ollama polishing stay local.
Portable `.mpod` files do not contain embeddings or absolute source paths. When
you copy and send a furnished or polished prompt to ChatGPT, Claude, or another
provider, the context snippets you approved become part of that prompt and
therefore leave your machine.
