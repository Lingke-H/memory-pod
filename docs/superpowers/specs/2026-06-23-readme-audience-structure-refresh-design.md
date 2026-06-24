# Memory Pod README Audience and Structure Refresh Design

## Goal

Make the README immediately understandable to both hackathon visitors and
developers while preserving the technical accuracy, bilingual coverage, and
trust boundaries established by the current documentation.

## Audience

The README serves two equally important audiences:

1. Hackathon judges and first-time visitors who need to understand the problem,
   product, and value within the opening screenfuls.
2. Developers and potential contributors who need verified setup, architecture,
   interfaces, testing, and operational constraints.

The structure will use progressive disclosure: plain-language product context
first, practical usage second, and detailed technical reference third.

## Background and Attribution

The opening will state that Memory Pod was built for the **2026 AI Hackathon at
UC Berkeley**. This is project context, not a claim of institutional endorsement,
award status, or official university sponsorship.

## Opening Experience

Immediately below the title:

- Keep the existing product tagline.
- Add a visible `[中文版本](#中文文档)` shortcut.
- Add one concise hackathon-attribution sentence.
- Explain in plain language that AI memory is usually trapped inside one tool,
  while Memory Pod lets users keep explicit context locally, review it, and use
  it across AI products.

The opening must answer three questions without requiring knowledge of Pods,
embeddings, JSONL, or retrieval systems:

1. What problem exists?
2. What does Memory Pod do?
3. What does the user actually do with it?

Product terminology will be introduced only after those answers.

## Information Architecture

### English Section

1. Title, tagline, Chinese shortcut, and hackathon context.
2. Plain-language overview: problem, solution, and a three-step user flow.
3. Project status and a concise explanation of Base Pod, Shared Pod, and Pod
   Dock.
4. Quick start and core workflows for users.
5. Desktop interaction and CLI reference.
6. Professional technical sections: architecture, data flow, privacy/trust,
   configuration, repository structure, and verification.
7. Known limitations and related documentation.

### Chinese Section

The Chinese section will mirror the English section's meaning and progression,
not merely retain the old order. It will begin with a visible return shortcut to
the English section and repeat the UC Berkeley hackathon background accurately.
Commands, paths, API names, environment variables, and product terms remain
unchanged.

## Style Rules

- Use short paragraphs in the lead-in; define technical terms after the product
  has been explained in ordinary language.
- Prefer prose for product purpose, background, status, and trust explanations.
- Use one numbered sequence for the primary user flow.
- Use tables for command reference, configuration, architecture ownership, and
  other repeated-field comparisons.
- Reserve bullets for requirements, troubleshooting, and limitations where
  independent scan-friendly items are materially clearer.
- Avoid duplicating the same capability list in the overview, status, and
  architecture sections.
- Keep technical claims precise and avoid promotional overstatement.

## Content Preservation

The refresh must retain the following verified facts:

- Memory Pod is local-first and inspectable.
- The MVP supports one private writable Base Pod and at most one Shared Pod.
- Imported Shared Pods are read-only and author metadata is self-declared.
- Portable `.mpod` files omit embeddings and absolute local source paths.
- Memory Pod never auto-submits a prompt.
- Approved context leaves the local boundary when the user sends it to an
  external AI provider.
- The documented CLI, Make targets, environment variables, system requirements,
  troubleshooting guidance, and links remain accurate.

## Validation

Automated documentation tests will be extended to require the top-level Chinese
shortcut and the UC Berkeley hackathon statement. Existing bilingual-order and
local-link checks must continue to pass. The full repository test suite and
Markdown link validation will be run after editing.

## Acceptance Criteria

- A first-time reader can identify the problem, solution, and core workflow from
  the opening sections without understanding implementation terminology.
- The repository is explicitly and accurately contextualized as a project built
  for the 2026 AI Hackathon at UC Berkeley.
- The Chinese shortcut appears before the first English section heading and
  resolves to the Chinese section.
- The Chinese section provides a reciprocal shortcut to the English opening.
- Bullet-heavy introductory sections are replaced by concise prose, a numbered
  workflow, or compact tables.
- Technical sections remain professional, complete, and consistent with the
  implementation.
- No product behavior or public interface changes.
