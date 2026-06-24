# Memory Pod Project Audit and README Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Memory Pod repository reproducible, internally consistent, and professionally documented in English and Chinese without adding product features.

**Architecture:** Preserve the current local JSONL, local-embedding, retrieval, prompt-assembly, Pod Dock, and review-first interaction architecture. Limit implementation changes to deterministic developer tooling and documentation/configuration reconciliation; verify every documented workflow against existing entry points.

**Tech Stack:** Python 3.11+, GNU Make-compatible Makefile syntax, pytest, Markdown, local JSONL Pod stores, optional Tkinter/pynput/pyperclip desktop interaction.

## Global Constraints

- `PROJECT_DESCRIPTION_V4.md` is the active product source of truth.
- Do not add product features or change stable Python interfaces.
- Do not add cloud storage, cloud retrieval, automatic monitoring, or automatic prompt submission.
- English README content must appear before the complete Chinese version.
- Do not edit or delete `README 2.md`, `docs/DEMO_RUNBOOK 2.md`, `scripts/judge_demo 2.py`, or `src/memory_pod/hotkey_popup 2.py`.
- Preserve an explicit `PYTHON=...` Make override and a system-Python fallback when `.venv/bin/python` does not exist.
- Run tests with `PYTHONDONTWRITEBYTECODE=1` so verification does not create tracked noise.

---

### Task 1: Make Verification Select the Repository Virtual Environment

**Files:**
- Modify: `tests/test_makefile_defaults.py`
- Modify: `Makefile`

**Interfaces:**
- Consumes: repository-local `.venv/bin/python` when present; caller-provided `PYTHON` when explicitly set.
- Produces: the Make variable `PYTHON`, resolving to `.venv/bin/python` when available and `python` otherwise.

- [ ] **Step 1: Add a failing Makefile-selection test**

Append this test to `tests/test_makefile_defaults.py`:

```python
def test_makefile_prefers_repo_virtualenv_with_system_fallback():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert (
        "PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)"
        in makefile
    )
```

- [ ] **Step 2: Run the focused test and confirm the contract is absent**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_makefile_defaults.py -q
```

Expected: one failure in `test_makefile_prefers_repo_virtualenv_with_system_fallback` because the Makefile currently contains `PYTHON ?= python`.

- [ ] **Step 3: Implement deterministic Python selection**

Replace the Makefile assignment with:

```make
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)
```

This preserves command-line and environment overrides because GNU Make's `?=` assigns only when `PYTHON` is undefined.

- [ ] **Step 4: Run the focused test and exercise both Make paths**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_makefile_defaults.py -q
make -n test
make -n test PYTHON=/usr/bin/python3
```

Expected: both tests pass; the first dry run begins with `.venv/bin/python`; the override dry run begins with `/usr/bin/python3`.

- [ ] **Step 5: Commit the tooling fix**

```bash
git add Makefile tests/test_makefile_defaults.py
git commit -m "build: prefer repository virtualenv"
```

---

### Task 2: Add Documentation Consistency Contracts

**Files:**
- Create: `tests/test_documentation.py`

**Interfaces:**
- Consumes: active Markdown documents and `.env.example` in the repository root.
- Produces: automated checks for v4 authority, supported configuration keys, bilingual README ordering, and valid local Markdown links.

- [ ] **Step 1: Create failing documentation-contract tests**

Create `tests/test_documentation.py` with:

```python
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_active_project_docs_reference_v4_source_of_truth():
    active_docs = (
        ROOT / "README.md",
        ROOT / "ROADMAP.md",
        ROOT / "docs" / "COLLABORATION.md",
        ROOT / "docs" / "TASK_BOARD.md",
    )

    for path in active_docs:
        text = path.read_text(encoding="utf-8")
        assert "PROJECT_DESCRIPTION_V4.md" in text, path


def test_env_example_lists_supported_configuration_keys():
    lines = {
        line.split("=", 1)[0]
        for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#") and "=" in line
    }

    assert lines == {
        "MEMORY_POD_HOME",
        "MEMORY_POD_MODEL",
        "MEMORY_POD_PROFILE",
    }


def test_readme_is_english_first_and_contains_complete_chinese_section():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert readme.index("## Overview") < readme.index("## 中文文档")
    assert "### 项目概述" in readme
    assert "### 隐私与信任边界" in readme
    assert "### 故障排查" in readme


def test_readme_local_markdown_links_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme)

    for target in targets:
        if "://" in target or target.startswith("#"):
            continue
        path_text = target.split("#", 1)[0]
        assert (ROOT / path_text).exists(), target
```

- [ ] **Step 2: Run the tests and confirm they detect current drift**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: failures identify missing v4 references in active planning documents, the incomplete environment example, and the missing full Chinese README section. The existing README-link test portion may already pass.

- [ ] **Step 3: Commit the red documentation contracts with their implementation task**

Do not commit failing tests alone. Keep this file in the working tree for Tasks 3 and 4, then include it in the Task 4 documentation commit after all assertions pass.

---

### Task 3: Reconcile Configuration and Active Project Documents

**Files:**
- Modify: `.env.example`
- Modify: `ROADMAP.md`
- Modify: `docs/COLLABORATION.md`
- Modify: `docs/TASK_BOARD.md`
- Modify: `src/memory_pod/radar.py`

**Interfaces:**
- Consumes: supported variables from `memory_pod.config` and v4 scope from `PROJECT_DESCRIPTION_V4.md`.
- Produces: truthful operator configuration and active-document status without changing runtime behavior.

- [ ] **Step 1: Refresh the environment example**

Replace `.env.example` with:

```dotenv
# Optional: override the local Memory Pod data directory.
# Default on macOS: ~/Library/Application Support/Memory Pod
MEMORY_POD_HOME=~/Library/Application Support/Memory Pod

# Backward-compatible default profile used by legacy profile commands.
MEMORY_POD_PROFILE=alice

# Local sentence-transformers model name. Memory Pod never downloads it during
# normal retrieval; when it is not cached, the deterministic hashing fallback is used.
MEMORY_POD_MODEL=all-MiniLM-L6-v2
```

- [ ] **Step 2: Mark the roadmap as historical and point to v4**

Replace the introductory block at the top of `ROADMAP.md` with:

```markdown
# Memory Pod — Historical Optimization and Delegation Roadmap

> **Status:** Historical hackathon planning document. Several items below have
> already been implemented, and individual status notes may not reflect the final
> repository state. Use [PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md)
> for current product scope and [README.md](README.md) for verified setup and usage.
```

Retain the remaining historical content because it records design rationale, but do not present v3 as current authority.

- [ ] **Step 3: Rewrite the collaboration guide around current boundaries**

Replace `docs/COLLABORATION.md` with a concise guide containing these exact sections and rules:

```markdown
# Collaboration Guide

Memory Pod follows [PROJECT_DESCRIPTION_V4.md](../PROJECT_DESCRIPTION_V4.md).
If another document conflicts with that product constitution, v4 wins.

## Working Boundary

- **Engine:** storage, ingest, embeddings, retrieval, prompt assembly, and the
  public `augment()` / `remember()` contracts.
- **Interaction:** CLI, Pod Dock, OS hotkeys, onboarding, and demo scripts that
  consume the public engine contracts.
- Agree on public signatures before making a change that crosses this boundary.
- Keep Shared Pod guidance advisory and keep personal write-back limited to a
  private writable Base Pod.

## Shared Files

Coordinate edits to `README.md`, `ROADMAP.md`, `pyproject.toml`,
`requirements.txt`, and the public interfaces in `src/memory_pod/augment.py`.

## Branch and Commit Practice

Use focused branches and commits. The conventional Codex branch prefix is
`codex/`; human contributors may follow the repository's existing naming
convention. Do not commit generated Pod stores, model caches, `.env`, or build
artifacts.

## Verification Before Handoff

```bash
source .venv/bin/activate
make check
make pod-demo
git status --short
```

Run macOS hotkey checks manually when interaction code changes. Never treat a
manual prompt injection as successful unless the prompt remains unsubmitted for
user review.

Use [HANDOFF_TEMPLATE.md](HANDOFF_TEMPLATE.md) to record the branch, scope,
contract changes, verification evidence, and remaining risks.
```

- [ ] **Step 4: Replace the stale task board with an honest status snapshot**

Rewrite `docs/TASK_BOARD.md` so it links to `../PROJECT_DESCRIPTION_V4.md`, records the implemented engine, Portable Pods, Pod Dock, onboarding, write-back, local polishing fallback, CLI, OS loop, and automated tests as complete, and lists only these remaining operational items:

```markdown
## Operational Follow-Up

- Record and retain a known-good macOS hotkey demo fallback.
- Perform a clean-machine setup rehearsal before a public demonstration.
- Treat broader Pod stacks, cloud synchronization, marketplaces, browser
  extensions, and autonomous agents as out of scope unless the product
  constitution is deliberately revised.
```

The document must state that it is a status snapshot, not a feature backlog.

- [ ] **Step 5: Align the Radar boundary copy with v4**

In `src/memory_pod/radar.py`, replace v3/Tier terminology with the v4 boundary:

```python
"""Explicit boundary for the out-of-scope Terminal Radar concept.

PROJECT_DESCRIPTION_V4 excludes social similarity ranking from the MVP. Keep
this module as a named boundary for historical prototypes without presenting it
as an implemented capability.
"""
```

Keep `main()` behavior and exit status unchanged; update its message to direct users to the implemented local Pod workflows instead of Tier 0/Tier 1 wording.

- [ ] **Step 6: Run the applicable partial checks**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py::test_active_project_docs_reference_v4_source_of_truth tests/test_documentation.py::test_env_example_lists_supported_configuration_keys -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m compileall -q src/memory_pod/radar.py
```

Expected: both documentation tests pass and compilation exits successfully. README bilingual assertions remain red until Task 4.

---

### Task 4: Replace README with a Verified Bilingual Reference

**Files:**
- Modify: `README.md`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: actual commands from `Makefile` and `memory_pod.cli`, current v4 product language, storage paths from `memory_pod.config`, and safety behavior from the Pod Dock and OS loop.
- Produces: one canonical README with professional English documentation first and a substantively equivalent Chinese version second.

- [ ] **Step 1: Write the English reference**

Replace the existing README English content with the following section sequence:

```markdown
# Memory Pod

> Own your Pod. Dock it anywhere. Share only what you choose.

## Overview
## Project Status
## Core Capabilities
## How It Works
## Privacy and Trust Boundary
## Requirements
## Installation
## Quick Start
## Core Workflows
### Create and Ingest a Private Base Pod
### Create and Export a Shared Pod
### Inspect and Import a Shared Pod
### Dock Context and Furnish a Prompt
## Desktop Interaction on macOS
### Review-First Pod Dock
### Optional In-Place Injection
### Explicit Local Write-Back
## CLI Reference
## Demo Commands
## Architecture
## Repository Structure
## Development and Verification
## Configuration
## Troubleshooting
## Known Limitations
## Documentation
## 中文文档
```

Populate every English section with verified facts:

- Local-first and inspectable context, one private writable Base Pod plus at most one Shared Pod in the MVP.
- `.mpod` carries readable records and metadata but excludes embeddings and absolute source paths; imported Shared Pods are read-only; author metadata is self-declared.
- Local storage/retrieval does not mean data remains local after the user sends an approved furnished prompt to an external provider.
- Python 3.11+, macOS for global-hotkey flows, and Accessibility permission for the Terminal/Python host.
- Exact setup commands: create `.venv`, activate it, `make setup`, `make check`, and `make onboard`.
- Exact Pod commands demonstrated by current CLI: create, ingest, export, inspect, import, list, migrate legacy, augment, remember.
- Pod Dock uses `Option + Enter`, supports context deselection, copies without submitting, and optionally uses local Ollama polishing with safe fallback.
- OS loop uses `Option + Enter` to replace focused input and `Control + Shift + Enter` for explicit write-back; neither path auto-submits.
- Demo targets: `make pod-demo`, `make demo-setup`, `make judge`, `make demo`, and `make demo-learn`.
- Architecture modules: configuration, Pods, storage/ingest, embeddings/retrieval, assembly/augmentation, remember, CLI, popup, OS loop, and optional rewriter.
- Configuration table for `MEMORY_POD_HOME`, `MEMORY_POD_PROFILE`, and `MEMORY_POD_MODEL`.
- Troubleshooting for wrong interpreter, model cache fallback, Ollama unavailability, ignored hotkeys, empty retrieval, and legacy stores.
- Explicit limitations copied from v4: no cloud sync/accounts, marketplace, browser extension, automatic screen/chat monitoring, automatic submission, or autonomous-agent network.
- Direct links to `PROJECT_DESCRIPTION_V4.md`, `docs/DEMO_RUNBOOK.md`, `docs/COLLABORATION.md`, `docs/TASK_BOARD.md`, and `docs/HANDOFF_TEMPLATE.md`.

- [ ] **Step 2: Write the complete Chinese reference after the English version**

Under `## 中文文档`, mirror the English information with these headings:

```markdown
### 项目概述
### 当前状态
### 核心能力
### 工作原理
### 隐私与信任边界
### 环境要求
### 安装
### 快速开始
### 核心工作流
#### 创建并导入私有 Base Pod
#### 创建并导出 Shared Pod
#### 检查并导入 Shared Pod
#### Dock 上下文并生成增强提示词
### macOS 桌面交互
#### 审阅优先的 Pod Dock
#### 可选的输入框原位注入
#### 显式本地写回
### CLI 命令参考
### 演示命令
### 系统架构
### 仓库结构
### 开发与验证
### 配置项
### 故障排查
### 已知限制
### 相关文档
```

Use the product terms `Pod`, `Base Pod`, `Shared Pod`, `Pod Dock`, and `.mpod` consistently rather than inventing incompatible translations. Translate explanations and safety boundaries fully; commands, paths, environment-variable names, and public API names remain unchanged.

- [ ] **Step 3: Run documentation tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: all four tests pass.

- [ ] **Step 4: Smoke-test every documented command surface**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m memory_pod.cli --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m memory_pod.cli pod --help
make -n onboard
make -n pod-demo
make -n demo-setup
make -n popup
make -n os-loop
```

Expected: both CLI help commands exit 0 and list the documented subcommands; each Make dry run resolves to an existing script or module and uses `.venv/bin/python` by default.

- [ ] **Step 5: Commit documentation and consistency changes**

```bash
git add .env.example README.md ROADMAP.md docs/COLLABORATION.md docs/TASK_BOARD.md src/memory_pod/radar.py tests/test_documentation.py
git commit -m "docs: publish bilingual project reference"
```

---

### Task 5: Perform the Final Repository Audit

**Files:**
- Verify: all tracked files changed by Tasks 1-4
- Preserve: the four named untracked duplicate files

**Interfaces:**
- Consumes: the hardened repository state.
- Produces: objective completion evidence and a concise progress/gap report.

- [ ] **Step 1: Run the complete automated verification**

Run:

```bash
make check
```

Expected: compilation succeeds and the full pytest suite passes with the new test count.

- [ ] **Step 2: Check Markdown references and stale authority language**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
rg -n "follows.*PROJECT_DESCRIPTION_V3|V3.*source of truth|PROJECT_DESCRIPTION_V3.*source of truth" README.md ROADMAP.md docs src/memory_pod
```

Expected: documentation tests pass and `rg` returns no active source-of-truth claim for v3. Historical v3 files and archived design records may still contain their original version labels.

- [ ] **Step 3: Inspect the final diff and working-tree preservation**

Run:

```bash
git diff --check HEAD~2..HEAD
git status --short
```

Expected: no whitespace errors; the only untracked files are still `README 2.md`, `docs/DEMO_RUNBOOK 2.md`, `scripts/judge_demo 2.py`, and `src/memory_pod/hotkey_popup 2.py`, unchanged and uncommitted.

- [ ] **Step 4: Review README parity manually**

Compare the English and Chinese heading sequences and verify that both cover product status, workflows, privacy, commands, architecture, testing, configuration, troubleshooting, limitations, and related documents. Confirm that neither language overstates local privacy after context is sent to an external provider.

- [ ] **Step 5: Prepare the completion report**

Report:

- Verified project progress and implemented capability groups.
- Gaps found and exactly how they were resolved.
- Full test count and command evidence.
- Files intentionally preserved and remaining manual macOS checks.
- Links to `README.md`, the design, and this implementation plan.
