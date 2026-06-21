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
deselect retrieved context, then copy the furnished prompt. The popup never
auto-submits.

## Demos

```bash
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

The Pod store, embeddings, and retrieval stay local. Portable `.mpod` files do
not contain embeddings or absolute source paths. When you copy and send a
furnished prompt to ChatGPT, Claude, or another provider, the context snippets
you approved become part of that prompt and therefore leave your machine.
