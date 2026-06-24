# Memory Pod README Audience and Structure Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the bilingual README so first-time visitors understand Memory Pod quickly while developers retain a rigorous technical reference.

**Architecture:** Change documentation only. Introduce a plain-language opening and reciprocal language shortcuts, move from capability-list repetition to progressive disclosure, and preserve all verified commands, technical boundaries, and bilingual content.

**Tech Stack:** GitHub-flavored Markdown, pytest documentation-contract tests, existing Python 3.11+ project tooling.

## Global Constraints

- State that Memory Pod was built for the **2026 AI Hackathon at UC Berkeley** without implying endorsement, sponsorship, or an award.
- Serve hackathon visitors and developers equally through progressive disclosure.
- Keep English first and Chinese second.
- Add `[中文版本](#中文文档)` before the first English section heading and a reciprocal `[Back to English](#memory-pod)` link at the start of the Chinese section.
- Use plain language before introducing Pod, embedding, JSONL, or retrieval terminology.
- Preserve verified commands, privacy claims, product limits, and public API names.
- Do not change product code or behavior.
- Do not edit the four pre-existing untracked duplicate files.

---

### Task 1: Define the README Opening and Navigation Contract

**Files:**
- Modify: `tests/test_documentation.py`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: rendered Markdown text from `README.md`.
- Produces: regression checks for hackathon attribution, language shortcuts, plain-language opening structure, and removal of the duplicated capability-list section.

- [ ] **Step 1: Add failing documentation tests**

Append the following tests:

```python
def test_readme_opening_has_hackathon_context_and_chinese_shortcut():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    opening = readme[: readme.index("## Overview")]

    assert "[中文版本](#中文文档)" in opening
    assert "2026 AI Hackathon at UC Berkeley" in opening


def test_readme_uses_progressive_plain_language_structure():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "### The problem" in readme
    assert "### What Memory Pod does" in readme
    assert "### The experience in three steps" in readme
    assert "## Key Concepts" in readme
    assert "## Core Capabilities" not in readme


def test_chinese_section_has_reciprocal_navigation_and_context():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = readme[readme.index("## 中文文档") :]

    assert "[Back to English](#memory-pod)" in chinese
    assert "2026 AI Hackathon at UC Berkeley" in chinese
    assert "#### 现有问题" in chinese
    assert "#### Memory Pod 的解决方式" in chinese
    assert "#### 三步使用流程" in chinese
    assert "### 核心概念" in chinese
```

- [ ] **Step 2: Run the focused tests and verify the intended failure**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: the existing four tests pass; the three new tests fail because the current README lacks the new attribution, navigation, and progressive-disclosure headings.

---

### Task 2: Restructure and Rewrite the Bilingual README

**Files:**
- Modify: `README.md`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the existing verified commands and technical reference, plus the approved redesign specification.
- Produces: one English-first, Chinese-second README for both nontechnical visitors and developers.

- [ ] **Step 1: Replace the English opening with a plain-language lead-in**

Use this exact order before setup material:

```markdown
# Memory Pod

[中文版本](#中文文档)

> **Own your Pod. Dock it anywhere. Share only what you choose.**

Built for the **2026 AI Hackathon at UC Berkeley**, Memory Pod explores a simple
idea: the useful context an AI learns about you should not be trapped inside one
AI product.

## Overview

### The problem
### What Memory Pod does
### The experience in three steps
## Project Status
## Key Concepts
```

Under `The problem`, explain vendor-bound AI memory in two short paragraphs.
Under `What Memory Pod does`, explain local, inspectable context and cross-tool
prompt furnishing without using implementation terms in the first sentence.
Under `The experience in three steps`, use one numbered list: build/receive a
Pod, Dock and review relevant context, then copy or inject the furnished prompt
for manual submission. Use a compact table under `Key Concepts` for Base Pod,
Shared Pod, Pod Dock, `.mpod`, and furnished prompt.

- [ ] **Step 2: Reorder English content for progressive disclosure**

Keep this section sequence after `Key Concepts`:

```markdown
## Quick Start
## Core Workflows
## Desktop Interaction on macOS
## CLI Reference
## Demo Commands
## How It Works
## Architecture
## Privacy and Trust Boundary
## Requirements
## Installation
## Repository Structure
## Development and Verification
## Configuration
## Troubleshooting
## Known Limitations
## Documentation
## 中文文档
```

Move existing content rather than dropping facts. Keep prose for overview,
status, data flow, and privacy explanations. Retain tables for concepts, CLI,
demos, architecture, and configuration. Retain bullets only for requirements,
troubleshooting, and limitations.

- [ ] **Step 3: Mirror the structure in Chinese**

Start the Chinese section with:

```markdown
## 中文文档

[Back to English](#memory-pod)

Memory Pod 诞生于 **2026 AI Hackathon at UC Berkeley**。它探索一个直接的
问题：AI 已经了解并用于帮助你的上下文，不应被锁在某一个 AI 产品中。

### 项目概述

#### 现有问题
#### Memory Pod 的解决方式
#### 三步使用流程
### 当前状态
### 核心概念
```

Then mirror the English progression: quick start, workflows, desktop, CLI,
demos, how it works, architecture, privacy, requirements, installation,
repository structure, development, configuration, troubleshooting, limitations,
and related documents. Preserve literal commands, paths, variable names, API
names, and product terms.

- [ ] **Step 4: Run the documentation contract**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: all seven documentation tests pass.

- [ ] **Step 5: Inspect structure and list usage**

Run:

```bash
rg -n '^## |^### |^#### ' README.md
rg -n '^- ' README.md
```

Expected: the English and Chinese headings follow the approved progression;
introductory capability bullets are gone; remaining bullets appear only in
requirements, troubleshooting, and limitations or in the related-document list.

- [ ] **Step 6: Commit the README refresh**

```bash
git add README.md tests/test_documentation.py
git commit -m "docs: clarify readme story and navigation"
```

---

### Task 3: Verify the Final Documentation and Repository

**Files:**
- Verify: `README.md`
- Verify: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the refreshed README and existing project suite.
- Produces: evidence that navigation, links, commands, compilation, and tests remain valid.

- [ ] **Step 1: Run the full verification suite**

Run:

```bash
make check
```

Expected: compilation succeeds and the complete pytest suite passes with 99 tests.

- [ ] **Step 2: Smoke-test documented entry points**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m memory_pod.cli --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m memory_pod.cli pod --help
make -n onboard
make -n popup
make -n os-loop
```

Expected: CLI help exits successfully and each Make dry run resolves through `.venv/bin/python` to an existing entry point.

- [ ] **Step 3: Verify branch scope and preserved user files**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; only README/test changes are part of the
implementation commit, while the four named duplicate files remain untracked
and untouched.
