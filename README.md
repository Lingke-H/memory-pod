# Memory Pod

> **Own your Pod. Dock it anywhere. Share only what you choose.**

Memory Pod is a local-first, inspectable context layer for furnishing prompts
across AI products. It stores explicit user-owned memory and shareable
playbooks in local Pods, retrieves context relevant to the current task, and
shows the selected material before the user sends anything to an AI provider.

The current product scope is defined by
[PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md).

## Overview

AI assistants usually keep memory inside one vendor's account. Memory Pod moves
that context into transparent local containers:

- A **Base Pod** is the user's private, writable memory.
- A **Shared Pod** is an explicit playbook, checklist, task lens, or set of
  examples that can be carried as an `.mpod` file.
- The **Pod Dock** activates one Base Pod and, in the current MVP, at most one
  Shared Pod for a task.
- A **furnished prompt** combines the user's request with reviewed, relevant
  context. Memory Pod copies or injects it but never submits it automatically.

Memory Pod does not claim to copy a person, transfer tacit expertise, or make an
AI “think like” a Shared Pod author. It carries written context that remains
visible and subject to user review.

## Project Status

This repository contains a working hackathon MVP v1.1 rather than a
production-hardened application. The local engine, Portable Pods, CLI, first-run
onboarding, review-first macOS Pod Dock, explicit write-back, optional local
polishing, demo tooling, and automated tests are implemented.

The primary supported path is review-first: retrieve context, inspect or
deselect it, copy the furnished prompt, and submit it manually. OS-level
in-place injection is available as an optional macOS demo path and should have a
recorded fallback for presentations.

## Core Capabilities

- Ingest local Markdown and text files into a private or locally authored Pod.
- Store memory records and embeddings in local JSONL files.
- Use a locally cached sentence-transformers model, with a deterministic local
  hashing fallback when the model is unavailable.
- Protect retrieval when stored records and the active embedder use different
  vector spaces.
- Create, list, inspect, import, export, and migrate Pods from the CLI.
- Export Shared Pods as readable `.mpod` files without embeddings or absolute
  local source paths.
- Import Shared Pods as read-only context and re-embed their records locally.
- Retrieve from one private Base Pod and an optional Shared Pod.
- Keep private context separate from advisory Shared Pod guidance in the
  furnished prompt.
- Review and deselect individual retrieved records before copying.
- Explicitly save new memory to a private writable Base Pod.
- Optionally polish a reviewed furnished prompt through local Ollama with a safe
  fallback when Ollama is unavailable.

## How It Works

```text
Local .md/.txt files
        │
        ▼
Ingest and local embedding ──► local JSONL Pod store
                                      │
Raw prompt ──► relevance retrieval ◄──┘
        │
        ▼
Private Base context + advisory Shared context
        │
        ▼
User review / deselection ──► copy or paste ──► user submits manually
```

Memory Pod's main engine boundary is the stable augmentation interface:

```python
augment(raw_prompt: str) -> str
augment_for_profile(...) -> AugmentResult
augment_for_stack(raw_prompt: str, stack: PodStack, ...) -> AugmentResult
furnish_selected(raw_prompt: str, memories, stack: PodStack, ...) -> str
```

Legacy profile-oriented interfaces remain supported for backward
compatibility.

## Privacy and Trust Boundary

Memory Pod is local-first, not an end-to-end secrecy system.

- Pod databases, embeddings, retrieval, onboarding answers, and optional Ollama
  polishing remain on the local machine.
- Memory Pod does not read third-party AI memory, browser login sessions, or
  cloud conversation history.
- Portable `.mpod` files exclude embeddings and absolute source paths.
- Imported Shared Pods are read-only. Personal write-back is limited to a
  private writable Base Pod.
- Shared Pod content is advisory and must not override the user's request,
  higher-priority instructions, or safety and privacy boundaries.
- `.mpod` author metadata is self-declared and is not cryptographically
  verified.
- When a user sends a furnished prompt to ChatGPT, Claude, or another provider,
  the approved context in that prompt leaves the local machine and becomes
  subject to that provider's policies.

Review Shared Pod content before import and review retrieved records before
sending them externally.

## Requirements

- Python 3.11 or later.
- `pip` and `make` for the documented development workflow.
- macOS for the supported Pod Dock/global-hotkey experience. Core CLI behavior
  may run on other systems where the Python dependencies are available, but the
  OS automation is optimized for macOS.
- Terminal or Python Accessibility permission for global hotkeys and simulated
  keyboard input.
- Optional: Ollama running locally for `Polish Locally`.

## Installation

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

`make` prefers `.venv/bin/python` when the repository virtual environment
exists. Override it explicitly when necessary:

```bash
make check PYTHON=/path/to/python
```

By default, Pods are stored at:

```text
~/Library/Application Support/Memory Pod/pods/
```

Set `MEMORY_POD_HOME` to use a different local data directory.

## Quick Start

Create a private My Pod from a short onboarding flow and install the starter
Shared Pods:

```bash
make onboard
memory-pod pod list
```

Open the review-first macOS Pod Dock:

```bash
make popup
```

Press `Option + Enter`, select a Base Pod and an optional Shared Pod, enter a
request, review the retrieved records, and copy the furnished prompt.

## Core Workflows

### Create and Ingest a Private Base Pod

```bash
memory-pod pod create \
  --name "Jiahan" \
  --id jiahan \
  --kind private

memory-pod ingest --pod jiahan ~/Documents/notes
memory-pod remember --pod jiahan --tag preference \
  "Prefer concise explanations with concrete examples."
```

Only `.md` and `.txt` files are ingested. Re-ingesting a source reconciles its
stored chunks while preserving explicit manual memories.

### Create and Export a Shared Pod

A locally authored Shared Pod should contain material intended for sharing,
such as an architecture-review playbook:

```bash
memory-pod pod create \
  --name "Senior Architecture Review" \
  --id senior-review \
  --kind shared \
  --author "Alice" \
  --purpose "Architecture and pull-request review"

memory-pod ingest --pod senior-review ./architecture-playbook.md
memory-pod pod export senior-review --output Senior-Review.mpod
```

Private Base Pods cannot be exported as Shared Pods.

### Inspect and Import a Shared Pod

Inspect an `.mpod` before importing it:

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

Use `memory-pod pod import --replace ...` only when intentionally replacing an
existing imported Pod with the same ID. Imported records receive a generic
source label and local embeddings; the imported Pod is read-only.

### Dock Context and Furnish a Prompt

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

`--debug` exposes retrieved records and scores for inspection. For a Base-only
request, omit `--shared-pod`. The legacy `--profile` option remains an alias for
the Base Pod.

To copy legacy repository profile stores into the current Application Support
location without deleting their sources:

```bash
memory-pod pod migrate-legacy
```

## Desktop Interaction on macOS

### Review-First Pod Dock

```bash
make popup
```

The Pod Dock supports Base/Shared selection, `.mpod` import and export,
retrieval inspection, per-record deselection, explicit remembering, and copying
the final prompt. It does not submit to an AI service.

`Polish Locally` is optional. If Ollama is reachable, it rewrites the reviewed
furnished prompt into cleaner copy-ready text. If Ollama is missing, slow, or
returns invalid output, Memory Pod retains the inspected furnished prompt.

The popup's **Confirm → Hotkey** action writes the current Pod selection locally
so a running OS loop can use it on the next invocation.

### Optional In-Place Injection

Prepare deterministic demo Pods, then launch the OS loop:

```bash
make demo-setup
make os-loop

# Override the default demo Pods:
make os-loop BASE_POD=jiahan SHARED_POD=senior-review
```

Focus one AI text box and press `Option + Enter`. The loop selects and cuts the
focused text, furnishes it with the active Pods, and pastes the result back. It
never presses Enter or submits the prompt. Use one target site at a time, grant
Accessibility permission in advance, and retain a screen recording as a demo
fallback.

Pass `--no-follow-active-dock` when invoking `memory_pod.os_loop` directly to
pin the launch-time Pod selection instead of following the popup.

### Explicit Local Write-Back

While the OS loop is running, press `Control + Shift + Enter` in a focused text
box to save that text to the private Base Pod. This path uses copy rather than
cut, restores the previous clipboard, and does not paste, submit, or learn in
the background.

## CLI Reference

| Command | Purpose |
| --- | --- |
| `memory-pod ingest [--pod ID] PATH` | Ingest local `.md`/`.txt` sources. |
| `memory-pod augment [--base-pod ID] [--shared-pod ID] [--debug] PROMPT` | Retrieve context and furnish a prompt. |
| `memory-pod compare [--debug] [--reingest] PROMPT` | Run the legacy Alice/Bob comparison demo. |
| `memory-pod remember [--pod ID] [--tag TAG] TEXT` | Explicitly write local memory; repeat `--tag` as needed. |
| `memory-pod pod create ...` | Create a private or shared local Pod. |
| `memory-pod pod list` | List available Pods. |
| `memory-pod pod inspect FILE.mpod` | Preview a portable Shared Pod. |
| `memory-pod pod import [--replace] FILE.mpod` | Import a Shared Pod read-only. |
| `memory-pod pod export POD_ID --output FILE.mpod` | Export a local Shared Pod. |
| `memory-pod pod migrate-legacy` | Copy legacy demo profile stores into the current Pod home. |

Run `memory-pod COMMAND --help` or `memory-pod pod COMMAND --help` for the full
argument list.

## Demo Commands

| Command | Demonstrates |
| --- | --- |
| `make onboard` | First-run private memory plus starter Shared Pods. |
| `make pod-demo` | Isolated Own → Carry → Dock → selective retrieval flow. |
| `make demo-setup` | Persistent Pods for the popup and OS-loop demo. |
| `make judge` | Frozen presentation sequence. |
| `make demo` | Same prompt with different private memories. |
| `make demo-reingest` | Legacy comparison with forced source refresh. |
| `make demo-learn` | Explicit local write-back and subsequent retrieval. |

The presentation script, fallbacks, and manual checks are documented in
[docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md).

## Architecture

| Area | Primary modules | Responsibility |
| --- | --- | --- |
| Configuration | `config.py` | Local paths, defaults, supported source types. |
| Pod policy and portability | `pods.py` | Manifests, Base/Shared boundaries, `.mpod` import/export. |
| Storage and ingest | `memory_store.py`, `ingest.py` | Atomic JSONL persistence and source reconciliation. |
| Local representation | `embeddings.py` | Cached local model and hashing fallback. |
| Retrieval | `retrieval.py` | Relevance scoring, lexical guard, embedder compatibility. |
| Prompt furnishing | `prompt_assembly.py`, `augment.py` | Context separation, selection, and stable augmentation APIs. |
| Write-back | `remember.py` | Explicit private Base Pod memory writes. |
| Interfaces | `cli.py`, `hotkey_popup.py`, `os_loop.py` | CLI, review-first Dock, optional keyboard automation. |
| Optional local polish | `llm.py`, `rewriter.py` | Ollama availability and failure-tolerant rewriting. |

## Repository Structure

```text
.
├── src/memory_pod/       # Application and engine modules
├── tests/                # Automated unit and integration-level tests
├── scripts/              # Onboarding, seeding, and demo entry points
├── data/                 # Checked-in demo sources and starter playbooks
├── docs/                 # Runbook, collaboration, status, and handoff docs
├── PROJECT_DESCRIPTION_V4.md
├── Makefile
├── pyproject.toml
└── requirements.txt
```

Runtime Pod stores, generated `.mpod` distributions, virtual environments,
model caches, and secrets are intentionally excluded from version control.

## Development and Verification

```bash
source .venv/bin/activate
make check
```

`make check` performs bytecode compilation followed by the complete pytest
suite. Useful focused commands include:

```bash
make compile
make test
PYTHONPATH=src .venv/bin/python -m pytest tests/test_pods.py -q
```

Before changing engine/interaction boundaries, read
[docs/COLLABORATION.md](docs/COLLABORATION.md). Use
[docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md) when transferring work.

## Configuration

Memory Pod reads these environment variables directly from the process
environment; it does not automatically load `.env.example`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MEMORY_POD_HOME` | `~/Library/Application Support/Memory Pod` | Root for Pod stores, onboarding state, and active Dock selection. |
| `MEMORY_POD_PROFILE` | `alice` | Backward-compatible default for legacy profile APIs. |
| `MEMORY_POD_MODEL` | `all-MiniLM-L6-v2` | Name of the locally cached sentence-transformers model. |

Use `.env.example` as a reference and export values in the shell or process
launcher before starting Memory Pod.

## Troubleshooting

- **Tests report missing `pynput` or `pyperclip`:** run `make setup`, then use
  `.venv/bin/python` or activate `.venv`. `make` automatically prefers the
  repository virtual environment when it exists.
- **The sentence-transformers model is not cached:** retrieval falls back to the
  deterministic local hashing embedder. Run `python scripts/download_model.py`
  in advance only when the semantic model is required and network access is
  intentionally available.
- **Ollama is unavailable:** skip `Polish Locally`; the reviewed furnished
  prompt remains usable and unchanged.
- **The hotkey is ignored:** allow the Terminal or Python host under macOS
  **System Settings → Privacy & Security → Accessibility**, then restart the
  process.
- **No context is retrieved:** verify the selected Base Pod, inspect `--debug`
  output, ingest relevant `.md` or `.txt` material, and use a prompt with real
  lexical or semantic overlap.
- **Legacy profile data is missing from the Pod Dock:** run
  `memory-pod pod migrate-legacy`.
- **An imported Pod cannot be edited:** this is intentional. Imported Shared
  Pods are read-only; create a new locally authored Shared Pod for revisions.

## Known Limitations

- The MVP supports one Base Pod and at most one Shared Pod at a time.
- There is no cloud synchronization, account system, P2P discovery, or Pod
  marketplace.
- There is no browser extension or automatic screen/chat monitoring.
- Memory Pod does not auto-submit prompts.
- Terminal Radar/social similarity ranking and autonomous agent networks are
  outside the current scope.
- `.mpod` identity and authorship are not cryptographically authenticated.
- Global hotkeys and keyboard automation require manual macOS permissions and
  remain less portable than the CLI and review-first copy flow.

## Documentation

- [Product constitution v4](PROJECT_DESCRIPTION_V4.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md)
- [Collaboration guide](docs/COLLABORATION.md)
- [Project status snapshot](docs/TASK_BOARD.md)
- [Handoff template](docs/HANDOFF_TEMPLATE.md)
- [Historical roadmap](ROADMAP.md)

---

## 中文文档

### 项目概述

Memory Pod 是一个本地优先、可检查、可跨 AI 产品使用的上下文层。它将
用户明确拥有的记忆与可分享的工作方法保存在本地 Pod 中，根据当前任务
检索相关内容，并在任何信息发送给外部 AI 服务前向用户展示待使用的上下文。

当前产品范围以
[PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md) 为准。

Memory Pod 使用以下核心概念：

- **Base Pod**：用户私有且可写的基础记忆。
- **Shared Pod**：可通过 `.mpod` 文件携带的显式工作手册、检查清单、任务视角
  或示例集合。
- **Pod Dock**：为当前任务启用一个 Base Pod；现阶段 MVP 最多再启用一个
  Shared Pod。
- **增强提示词（furnished prompt）**：用户原始请求与经过审阅的相关上下文
  组合而成的提示词。Memory Pod 可以复制或注入该提示词，但不会自动提交。

Memory Pod 不声称复制一个人、转移隐性经验，或让 AI “像 Shared Pod 作者一样
思考”。它携带的是可见、可检查、可由用户决定是否采用的书面上下文。

### 当前状态

本仓库实现了可运行的 Hackathon MVP v1.1，并非已经完成生产级加固的应用。
本地引擎、Portable Pods、CLI、首次使用引导、审阅优先的 macOS Pod Dock、
显式记忆写回、可选本地润色、演示工具和自动化测试均已实现。

推荐主流程是：检索上下文、检查或取消选择内容、复制增强提示词，再由用户手动
提交。操作系统级原位注入属于可选的 macOS 演示路径，公开演示前应保留录屏
备用方案。

### 核心能力

- 将本地 Markdown 和文本文件导入私有 Pod 或本地创建的 Shared Pod。
- 使用本地 JSONL 文件保存记忆记录和向量。
- 优先使用本地已缓存的 sentence-transformers 模型；模型不可用时回退到
  确定性的本地哈希向量。
- 检测并处理存储记录与当前查询模型不一致的向量空间。
- 通过 CLI 创建、列出、检查、导入、导出和迁移 Pod。
- 将 Shared Pod 导出为可读的 `.mpod`，其中不包含向量和绝对本地源路径。
- 以只读方式导入 Shared Pod，并在本地重新生成向量。
- 同时从一个私有 Base Pod 和一个可选 Shared Pod 检索上下文。
- 在增强提示词中分隔私有上下文与仅供参考的 Shared Pod 指导。
- 复制前逐项检查并取消选择检索结果。
- 将新记忆显式写入私有、可写的 Base Pod。
- 可选调用本地 Ollama 润色；Ollama 不可用时安全保留原增强提示词。

### 工作原理

```text
本地 .md/.txt 文件
        │
        ▼
导入与本地向量化 ──► 本地 JSONL Pod 存储
                              │
原始提示词 ──► 相关性检索 ◄──┘
        │
        ▼
私有 Base 上下文 + 参考性 Shared 上下文
        │
        ▼
用户审阅/取消选择 ──► 复制或粘贴 ──► 用户手动提交
```

引擎以稳定的 `augment()`、`augment_for_profile()`、
`augment_for_stack()` 和 `furnish_selected()` 接口为边界；旧版 profile 接口继续
保留兼容性。

### 隐私与信任边界

Memory Pod 是本地优先系统，但不等同于端到端保密系统。

- Pod 数据库、向量、检索、引导问答和可选 Ollama 润色保留在本机。
- Memory Pod 不读取第三方 AI 的云端记忆、浏览器登录会话或云端对话历史。
- `.mpod` 不包含向量或绝对本地源路径。
- 导入的 Shared Pod 为只读；个人记忆只能写入私有、可写的 Base Pod。
- Shared Pod 内容仅供参考，不得覆盖用户请求、更高优先级指令或安全与隐私边界。
- `.mpod` 的作者信息由创建者自行声明，未经过密码学验证。
- 当用户把增强提示词发送给 ChatGPT、Claude 或其他服务时，其中经用户批准的
  上下文会离开本机，并受相应服务商政策约束。

导入前应检查 Shared Pod，发送前应再次检查实际选中的检索内容。

### 环境要求

- Python 3.11 或更高版本。
- 使用本文开发流程时需要 `pip` 和 `make`。
- 推荐使用 macOS 运行 Pod Dock 与全局快捷键。核心 CLI 在依赖可用的其他
  系统上也可能运行，但操作系统自动化主要针对 macOS。
- 全局快捷键与模拟键盘输入需要为 Terminal 或 Python 宿主授予辅助功能权限。
- 可选：本地运行 Ollama，以使用 `Polish Locally`。

### 安装

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

当 `.venv/bin/python` 存在时，`make` 会优先使用它；也可通过
`make check PYTHON=/path/to/python` 显式覆盖。

Pod 默认保存在：

```text
~/Library/Application Support/Memory Pod/pods/
```

可通过 `MEMORY_POD_HOME` 修改本地数据根目录。

### 快速开始

```bash
make onboard
memory-pod pod list
make popup
```

首次引导会创建私有 My Pod 并加载入门 Shared Pods。打开 Pod Dock 后按
`Option + Enter`，选择 Base Pod 和可选 Shared Pod，输入请求，检查检索内容，
然后复制增强提示词。

### 核心工作流

#### 创建并导入私有 Base Pod

```bash
memory-pod pod create --name "Jiahan" --id jiahan --kind private
memory-pod ingest --pod jiahan ~/Documents/notes
memory-pod remember --pod jiahan --tag preference \
  "Prefer concise explanations with concrete examples."
```

只会导入 `.md` 和 `.txt` 文件。重新导入同一来源时会同步更新其分块，同时保留
用户显式写入的手动记忆。

#### 创建并导出 Shared Pod

```bash
memory-pod pod create \
  --name "Senior Architecture Review" \
  --id senior-review \
  --kind shared \
  --author "Alice" \
  --purpose "Architecture and pull-request review"

memory-pod ingest --pod senior-review ./architecture-playbook.md
memory-pod pod export senior-review --output Senior-Review.mpod
```

Shared Pod 应只包含明确计划分享的工作方法、清单或示例。私有 Base Pod 不能
作为 Shared Pod 导出。

#### 检查并导入 Shared Pod

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

应先检查再导入。只有在明确要替换同 ID 的现有导入 Pod 时才使用
`memory-pod pod import --replace ...`。导入记录会使用通用来源标记并在本地生成
向量；导入 Pod 保持只读。

#### Dock 上下文并生成增强提示词

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

`--debug` 会显示检索记录和分数。只使用 Base Pod 时省略 `--shared-pod`。
旧版 `--profile` 仍是 Base Pod 的兼容别名。

如需将仓库中的旧版 profile 存储非破坏性复制到当前 Application Support
目录，可运行：

```bash
memory-pod pod migrate-legacy
```

### macOS 桌面交互

#### 审阅优先的 Pod Dock

```bash
make popup
```

Pod Dock 支持 Base/Shared 选择、`.mpod` 导入导出、检索结果检查、逐条取消选择、
显式记忆写回和最终提示词复制；它不会向任何 AI 服务自动提交内容。

`Polish Locally` 为可选功能。Ollama 可访问时，它会把经审阅的增强提示词润色为
更整洁的可复制文本；若 Ollama 缺失、超时或返回无效内容，Memory Pod 会保留
原增强提示词。

弹窗中的 **Confirm → Hotkey** 会把当前 Pod 选择写入本地，使正在运行的 OS
loop 在下一次快捷键操作时使用该选择。

#### 可选的输入框原位注入

```bash
make demo-setup
make os-loop

# 覆盖默认演示 Pods：
make os-loop BASE_POD=jiahan SHARED_POD=senior-review
```

聚焦一个 AI 文本框并按 `Option + Enter`。程序会选择并剪切当前文本，使用已
启用的 Pods 增强内容，再粘贴回原位置。它不会按 Enter，也不会提交提示词。
一次只在一个目标网站使用，提前授予辅助功能权限，并为演示保留录屏备用方案。

直接启动 `memory_pod.os_loop` 时可传入 `--no-follow-active-dock`，以固定启动时
的 Pod 选择，不跟随弹窗更新。

#### 显式本地写回

OS loop 运行时，在聚焦文本框中按 `Control + Shift + Enter`，可将文本保存到
私有 Base Pod。该流程使用复制而非剪切，会恢复之前的剪贴板，不会粘贴、提交
或在后台自动学习。

### CLI 命令参考

| 命令 | 用途 |
| --- | --- |
| `memory-pod ingest [--pod ID] PATH` | 导入本地 `.md`/`.txt`。 |
| `memory-pod augment [--base-pod ID] [--shared-pod ID] [--debug] PROMPT` | 检索上下文并生成增强提示词。 |
| `memory-pod compare [--debug] [--reingest] PROMPT` | 运行旧版 Alice/Bob 对比演示。 |
| `memory-pod remember [--pod ID] [--tag TAG] TEXT` | 显式写入本地记忆；`--tag` 可重复。 |
| `memory-pod pod create ...` | 创建私有或共享本地 Pod。 |
| `memory-pod pod list` | 列出可用 Pods。 |
| `memory-pod pod inspect FILE.mpod` | 预览 Portable Shared Pod。 |
| `memory-pod pod import [--replace] FILE.mpod` | 以只读方式导入 Shared Pod。 |
| `memory-pod pod export POD_ID --output FILE.mpod` | 导出本地 Shared Pod。 |
| `memory-pod pod migrate-legacy` | 将旧演示 profile 存储复制到当前 Pod 目录。 |

使用 `memory-pod COMMAND --help` 或 `memory-pod pod COMMAND --help` 查看完整参数。

### 演示命令

| 命令 | 展示内容 |
| --- | --- |
| `make onboard` | 首次创建私有记忆并安装入门 Shared Pods。 |
| `make pod-demo` | 隔离环境中的 Own → Carry → Dock → 选择性检索流程。 |
| `make demo-setup` | 为弹窗与 OS loop 准备持久化演示 Pods。 |
| `make judge` | 固定的展示流程。 |
| `make demo` | 同一提示词结合不同私有记忆。 |
| `make demo-reingest` | 强制刷新来源后的旧版对比演示。 |
| `make demo-learn` | 显式本地写回及后续检索。 |

演示脚本、降级方案与手动检查见
[docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md)。

### 系统架构

| 领域 | 主要模块 | 职责 |
| --- | --- | --- |
| 配置 | `config.py` | 本地路径、默认值和支持的来源类型。 |
| Pod 策略与可移植性 | `pods.py` | Manifest、Base/Shared 边界和 `.mpod` 导入导出。 |
| 存储与导入 | `memory_store.py`, `ingest.py` | 原子 JSONL 持久化和来源同步。 |
| 本地表示 | `embeddings.py` | 已缓存本地模型与哈希回退。 |
| 检索 | `retrieval.py` | 相关性、词法保护和向量模型兼容。 |
| 提示词增强 | `prompt_assembly.py`, `augment.py` | 上下文分隔、选择和稳定 API。 |
| 写回 | `remember.py` | 显式写入私有 Base Pod。 |
| 交互 | `cli.py`, `hotkey_popup.py`, `os_loop.py` | CLI、审阅优先弹窗与可选键盘自动化。 |
| 本地润色 | `llm.py`, `rewriter.py` | Ollama 检测和容错润色。 |

### 仓库结构

```text
.
├── src/memory_pod/       # 应用与引擎模块
├── tests/                # 自动化测试
├── scripts/              # 引导、数据准备与演示入口
├── data/                 # 演示来源与入门工作手册
├── docs/                 # 演示、协作、状态与交接文档
├── PROJECT_DESCRIPTION_V4.md
├── Makefile
├── pyproject.toml
└── requirements.txt
```

运行时 Pod 存储、生成的 `.mpod`、虚拟环境、模型缓存与敏感配置均不应进入版本
控制。

### 开发与验证

```bash
source .venv/bin/activate
make check
```

`make check` 会先执行编译检查，再运行完整 pytest 测试集。也可使用：

```bash
make compile
make test
PYTHONPATH=src .venv/bin/python -m pytest tests/test_pods.py -q
```

修改引擎与交互边界前，请阅读
[docs/COLLABORATION.md](docs/COLLABORATION.md)；交接工作可使用
[docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md)。

### 配置项

Memory Pod 直接读取进程环境变量，不会自动加载 `.env.example`。

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `MEMORY_POD_HOME` | `~/Library/Application Support/Memory Pod` | Pod 存储、引导状态与活动 Dock 选择的根目录。 |
| `MEMORY_POD_PROFILE` | `alice` | 旧版 profile API 的兼容默认值。 |
| `MEMORY_POD_MODEL` | `all-MiniLM-L6-v2` | 本地缓存的 sentence-transformers 模型名称。 |

请将 `.env.example` 作为参考，并在启动 Memory Pod 前通过 shell 或进程启动器
导出所需变量。

### 故障排查

- **测试提示缺少 `pynput` 或 `pyperclip`：**运行 `make setup`，随后激活
  `.venv` 或直接使用 `.venv/bin/python`。仓库虚拟环境存在时，`make` 会自动
  优先使用它。
- **sentence-transformers 模型未缓存：**系统会回退到确定性的本地哈希向量。
  只有在明确允许联网且需要语义模型时，才提前运行
  `python scripts/download_model.py`。
- **Ollama 不可用：**跳过 `Polish Locally`；经审阅的增强提示词仍会保持原样
  可用。
- **快捷键无响应：**在 macOS 的“系统设置 → 隐私与安全性 → 辅助功能”中允许
  Terminal 或 Python 宿主，然后重启进程。
- **没有检索到上下文：**确认 Base Pod 选择，检查 `--debug` 输出，导入相关
  `.md`/`.txt`，并确保提示词与存储内容具有真实的词法或语义关联。
- **Pod Dock 中看不到旧 profile 数据：**运行 `memory-pod pod migrate-legacy`。
- **无法修改导入的 Pod：**这是预期行为。导入的 Shared Pod 为只读；如需修改，
  请创建新的本地 Shared Pod。

### 已知限制

- MVP 同时仅支持一个 Base Pod 和最多一个 Shared Pod。
- 不提供云同步、账号系统、P2P 发现或 Pod 市场。
- 不提供浏览器扩展，也不会自动监控屏幕或聊天。
- 不会自动提交提示词。
- Terminal Radar/社交相似度排名及自治 Agent 网络不在当前范围内。
- `.mpod` 身份和作者信息没有密码学认证。
- 全局快捷键与键盘自动化需要手动授予 macOS 权限，其可移植性低于 CLI 和
  审阅优先的复制流程。

### 相关文档

- [产品章程 v4](PROJECT_DESCRIPTION_V4.md)
- [演示手册](docs/DEMO_RUNBOOK.md)
- [协作指南](docs/COLLABORATION.md)
- [项目状态快照](docs/TASK_BOARD.md)
- [交接模板](docs/HANDOFF_TEMPLATE.md)
- [历史路线图](ROADMAP.md)
