# Memory Pod — Product Constitution v4

> Source of truth for MVP v1.1: Portable Pods + Pod Dock.

## Product Thesis

Memory Pod is a local-first, inspectable context layer that works across AI
models. It does not claim to copy a person, transfer tacit expertise, or generate
better prompts by itself. It retrieves the right explicit context, shows the
user what will be shared, and packages that context for any model.

> **Own your Pod. Dock it anywhere. Share only what you choose.**

## Product Language

- **Pod:** a bounded local context container.
- **Base Pod:** the user's writable private memory.
- **Shared Pod:** an explicit, shareable playbook; imported copies are read-only.
- **Pod Dock:** the control that activates a Base Pod and optional Shared Pod.
- **Docked Pods:** the context sources active for the current task.
- **`.mpod`:** a transparent portable Shared Pod file.

Avoid “share your brain,” “AI thinks like me,” and “transfer ten years of
experience.” A Shared Pod carries written principles, examples, checklists, and
decision frameworks—not identity or tacit judgment.

## MVP v1.1 Workflow

1. Create a private Base Pod and ingest local `.md` / `.txt` files.
2. Create a separate Shared Pod containing an explicit Expert Playbook.
3. Export the Shared Pod as an inspectable `.mpod` file.
4. Send it through AirDrop or any ordinary file channel.
5. The recipient previews it, imports it read-only, and re-embeds it locally.
6. Dock it beside their Base Pod.
7. Memory Pod retrieves relevant context from both Pods.
8. The user deselects anything they do not want to share, then copies the
   furnished prompt into ChatGPT, Claude, Cursor, or another AI.

## Trust Boundary

- The Pod database, embeddings, and retrieval stay local.
- Memory Pod never reads third-party cloud memory or login sessions.
- `.mpod` files never contain embeddings or absolute local source paths.
- `.mpod` author metadata is self-declared and not cryptographically verified.
- Imported Shared Pods are read-only.
- `remember()` writes only to the user's Base Pod.
- When the user sends a furnished prompt to an AI provider, the approved context
  snippets in that prompt leave the machine. Local-first is not end-to-end
  secrecy after the user chooses to send content.

## Stable Product Contracts

```python
augment(raw_prompt: str) -> str
augment_for_profile(...) -> AugmentResult
augment_for_stack(raw_prompt: str, stack: PodStack, ...) -> AugmentResult
furnish_selected(raw_prompt: str, memories, stack, ...) -> str
```

The original `augment()` and profile APIs remain backward compatible. The MVP
supports one Base Pod plus at most one Shared Pod. Focus Pods and larger Pod
Stacks are future work.

## Demo Proof

The primary demo must prove all four claims:

1. **Own:** the context exists as local records.
2. **Carry:** a Shared Pod exports as a readable `.mpod` with no vectors or
   private paths.
3. **Dock:** the recipient imports and retrieves it locally beside their Base.
4. **Selective:** unrelated tasks inject no Shared Playbook context, and the
   user can deselect individual memories before copying.

The furnished prompt can then be pasted into two different AI products to show
that the context is portable and not locked to one model.

## Explicitly Out of Scope

- P2P discovery or a profile marketplace
- Cloud synchronization or accounts
- Terminal Radar / social similarity ranking
- Automatic screen or chat monitoring
- Automatic prompt submission
- Chrome extensions
- Autonomous agent networks
- ChromaDB / FAISS migration without a measured scale need
