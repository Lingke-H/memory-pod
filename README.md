# Memory Pod

[中文版本](#中文文档)

> **Own your Pod. Dock it anywhere. Share only what you choose.**

Built for the **2026 AI Hackathon at UC Berkeley**, Memory Pod explores a simple
idea: the useful context an AI learns about you should not be trapped inside one
AI product.

## Overview

### The problem

AI assistants become more useful when they know how you work, what you care
about, and what context matters to the task. Today, that memory usually stays
inside one provider's account. Moving to another model often means starting over
or manually rebuilding the same context.

Sharing useful working knowledge has a similar problem. A checklist or review
framework may be valuable, but copying an opaque mega-prompt gives the receiver
little visibility into what they are adopting or sending onward.

### What Memory Pod does

Memory Pod keeps explicit context in local, inspectable containers and lets you
use that context with different AI products. You can keep your own private
memory, receive a separate shared playbook, choose what is relevant, and review
the exact material before it becomes part of a prompt.

The project does not copy a person or transfer tacit expertise. It carries
written facts, preferences, examples, principles, and checklists that remain
visible and under the user's control.

### The experience in three steps

1. **Own or receive context.** Build a private memory from local notes, or
   inspect and import a portable Shared Pod.
2. **Dock and review.** Select your Base Pod and an optional Shared Pod; Memory
   Pod retrieves only the context relevant to the current request.
3. **Use it anywhere.** Deselect anything you do not want to share, then copy or
   paste the furnished prompt into the AI product you choose. Memory Pod never
   submits it automatically.

## Project Status

Memory Pod is a working hackathon MVP v1.1, not a production-hardened service.
The local engine, Portable Pods, CLI, onboarding, review-first macOS Pod Dock,
explicit write-back, optional local polishing, demo tooling, and automated tests
are implemented.

The primary path is deliberately review-first. OS-level in-place injection is
available as an optional macOS demonstration, but the reliable fallback is
always the visible copy-and-paste flow.

## Key Concepts

| Term | Meaning |
| --- | --- |
| **Base Pod** | Your private, writable memory. |
| **Shared Pod** | A playbook, checklist, task lens, or example set designed to be shared. Imported Shared Pods are read-only. |
| **Pod Dock** | The control that activates one Base Pod and, in this MVP, at most one Shared Pod for a task. |
| **`.mpod`** | A readable portable file for carrying a Shared Pod without embeddings or absolute local paths. |
| **Furnished prompt** | Your request plus the relevant context you reviewed and approved. |

The current product boundary is defined by
[PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md).

## Quick Start

Create a private My Pod from a short onboarding flow, install the starter Shared
Pods, and open the review-first Pod Dock:

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make onboard
make popup
```

Press `Option + Enter`, choose a Base Pod and an optional Shared Pod, enter a
request, review the retrieved context, and copy the furnished prompt. The popup
does not submit anything to an AI service.

## Core Workflows

### Create and Ingest a Private Base Pod

```bash
memory-pod pod create --name "Jiahan" --id jiahan --kind private
memory-pod ingest --pod jiahan ~/Documents/notes
memory-pod remember --pod jiahan --tag preference \
  "Prefer concise explanations with concrete examples."
```

Only `.md` and `.txt` files are ingested. Re-ingesting a source reconciles its
stored chunks while preserving explicit manual memories.

### Create and Export a Shared Pod

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

A locally authored Shared Pod should contain material intended for sharing.
Private Base Pods cannot be exported as Shared Pods.

### Inspect and Import a Shared Pod

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

Inspect an `.mpod` before importing it. Use `--replace` only when intentionally
replacing an imported Pod with the same ID. Imported content is re-embedded
locally and remains read-only.

### Dock Context and Furnish a Prompt

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

`--debug` shows the retrieved records and scores. Omit `--shared-pod` for a
Base-only request. The legacy `--profile` option remains a Base Pod alias.

To copy legacy repository profile stores into the current Application Support
location without deleting the sources, run:

```bash
memory-pod pod migrate-legacy
```

## Desktop Interaction on macOS

### Review-First Pod Dock

```bash
make popup
```

The Pod Dock supports Pod selection, `.mpod` import and export, retrieval
inspection, per-record deselection, explicit remembering, and copying. `Polish
Locally` may use a local Ollama instance to rewrite the reviewed prompt; if
Ollama is unavailable or fails, the inspected furnished prompt remains
unchanged.

The popup's **Confirm → Hotkey** action stores the active Pod selection locally
for a running OS loop.

### Optional In-Place Injection

```bash
make demo-setup
make os-loop

# Override the frozen demo Pods:
make os-loop BASE_POD=jiahan SHARED_POD=senior-review
```

Focus one AI text box and press `Option + Enter`. The loop cuts the focused
text, furnishes it, and pastes it back without pressing Enter or submitting.
Use one target site at a time, grant Accessibility permission in advance, and
keep a recording as a presentation fallback.

While the loop is running, `Control + Shift + Enter` explicitly saves focused
text to the private Base Pod. This path copies rather than cuts, restores the
clipboard, and does not paste, submit, or learn in the background.

## CLI Reference

| Command | Purpose |
| --- | --- |
| `memory-pod ingest [--pod ID] PATH` | Ingest local `.md` and `.txt` sources. |
| `memory-pod augment [--base-pod ID] [--shared-pod ID] [--debug] PROMPT` | Retrieve context and furnish a prompt. |
| `memory-pod compare [--debug] [--reingest] PROMPT` | Run the legacy Alice/Bob comparison demo. |
| `memory-pod remember [--pod ID] [--tag TAG] TEXT` | Explicitly write local memory; `--tag` may be repeated. |
| `memory-pod pod create ...` | Create a private or shared local Pod. |
| `memory-pod pod list` | List available Pods. |
| `memory-pod pod inspect FILE.mpod` | Preview a portable Shared Pod. |
| `memory-pod pod import [--replace] FILE.mpod` | Import a Shared Pod read-only. |
| `memory-pod pod export POD_ID --output FILE.mpod` | Export a locally authored Shared Pod. |
| `memory-pod pod migrate-legacy` | Copy legacy demo stores into the current Pod home. |

Run `memory-pod COMMAND --help` or `memory-pod pod COMMAND --help` for complete
arguments.

## Demo Commands

| Command | Demonstrates |
| --- | --- |
| `make onboard` | First-run private memory and starter Shared Pods. |
| `make pod-demo` | Isolated Own → Carry → Dock → selective retrieval flow. |
| `make demo-setup` | Persistent Pods for the popup and OS-loop demo. |
| `make judge` | Frozen presentation sequence. |
| `make demo` | The same prompt with different private memories. |
| `make demo-reingest` | Legacy comparison with forced source refresh. |
| `make demo-learn` | Explicit local write-back followed by retrieval. |

Presentation guidance and fallbacks are in
[docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md).

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

The stable engine boundary is:

```python
augment(raw_prompt: str) -> str
augment_for_profile(...) -> AugmentResult
augment_for_stack(raw_prompt: str, stack: PodStack, ...) -> AugmentResult
furnish_selected(raw_prompt: str, memories, stack: PodStack, ...) -> str
```

Legacy profile-oriented interfaces remain supported for compatibility.

## Architecture

| Area | Primary modules | Responsibility |
| --- | --- | --- |
| Configuration | `config.py` | Local paths, defaults, and supported source types. |
| Pod policy and portability | `pods.py` | Manifests, Base/Shared boundaries, and `.mpod` import/export. |
| Storage and ingest | `memory_store.py`, `ingest.py` | Atomic JSONL persistence and source reconciliation. |
| Local representation | `embeddings.py` | Cached sentence-transformers model and deterministic hashing fallback. |
| Retrieval | `retrieval.py` | Relevance scoring, lexical guard, and embedder compatibility. |
| Prompt furnishing | `prompt_assembly.py`, `augment.py` | Context separation, selection, and stable augmentation APIs. |
| Write-back | `remember.py` | Explicit private Base Pod writes. |
| Interfaces | `cli.py`, `hotkey_popup.py`, `os_loop.py` | CLI, review-first Dock, and optional keyboard automation. |
| Optional local polish | `llm.py`, `rewriter.py` | Ollama availability and failure-tolerant rewriting. |

## Privacy and Trust Boundary

Memory Pod is local-first, not an end-to-end secrecy system. Pod databases,
embeddings, retrieval, onboarding answers, and optional Ollama polishing remain
on the local machine. Memory Pod does not read third-party AI memory, browser
login sessions, or cloud conversation history.

Portable `.mpod` files omit embeddings and absolute source paths. Imported
Shared Pods are read-only, author metadata is self-declared rather than
cryptographically verified, and personal write-back is limited to a private
writable Base Pod. Shared context is advisory; it must not override the user's
request, higher-priority instructions, or safety and privacy boundaries.

Once a user sends a furnished prompt to ChatGPT, Claude, or another provider,
the approved context in that prompt leaves the local machine and becomes subject
to that provider's policies. Review content before import and again before
sending it externally.

## Requirements

- Python 3.11 or later.
- `pip` and `make` for the documented workflow.
- macOS for the supported Pod Dock and global-hotkey experience. Core CLI
  behavior may run elsewhere when its Python dependencies are available.
- Terminal or Python Accessibility permission for global hotkeys and simulated
  keyboard input.
- Optional: a local Ollama instance for `Polish Locally`.

## Installation

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

`make` prefers `.venv/bin/python` when it exists. Override it with
`make check PYTHON=/path/to/python` when necessary.

Pods are stored by default at:

```text
~/Library/Application Support/Memory Pod/pods/
```

Set `MEMORY_POD_HOME` to choose another local directory.

## Repository Structure

```text
.
├── src/memory_pod/       # Application and engine modules
├── tests/                # Automated tests
├── scripts/              # Onboarding, seeding, and demo entry points
├── data/                 # Demo sources and starter playbooks
├── docs/                 # Runbook, collaboration, status, and handoff docs
├── PROJECT_DESCRIPTION_V4.md
├── Makefile
├── pyproject.toml
└── requirements.txt
```

Runtime Pod stores, `.mpod` distributions, virtual environments, model caches,
and secrets are excluded from version control.

## Development and Verification

```bash
source .venv/bin/activate
make check
```

`make check` compiles the Python sources and runs the complete pytest suite.
Focused alternatives include `make compile`, `make test`, and:

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_pods.py -q
```

Read [docs/COLLABORATION.md](docs/COLLABORATION.md) before changing the engine
and interaction boundary. Use
[docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md) when transferring work.

## Configuration

Memory Pod reads configuration from the process environment; it does not load
`.env.example` automatically.

| Variable | Default | Purpose |
| --- | --- | --- |
| `MEMORY_POD_HOME` | `~/Library/Application Support/Memory Pod` | Root for Pod stores, onboarding state, and active Dock selection. |
| `MEMORY_POD_PROFILE` | `alice` | Backward-compatible default for legacy profile APIs. |
| `MEMORY_POD_MODEL` | `all-MiniLM-L6-v2` | Name of the locally cached sentence-transformers model. |

## Troubleshooting

- **Missing `pynput` or `pyperclip`:** run `make setup`, then activate `.venv`
  or use `.venv/bin/python` directly.
- **The sentence-transformers model is not cached:** retrieval uses the local
  deterministic hashing fallback. Run `python scripts/download_model.py` only
  when the semantic model is required and network access is intentional.
- **Ollama is unavailable:** skip `Polish Locally`; the reviewed furnished
  prompt remains usable.
- **The hotkey is ignored:** allow Terminal or the Python host under macOS
  **System Settings → Privacy & Security → Accessibility**, then restart it.
- **No context is retrieved:** verify the selected Base Pod, inspect `--debug`,
  ingest relevant `.md` or `.txt` material, and use a related prompt.
- **Legacy data is missing:** run `memory-pod pod migrate-legacy`.
- **An imported Pod cannot be edited:** this is intentional; create a new local
  Shared Pod for revisions.

## Known Limitations

- The MVP supports one Base Pod and at most one Shared Pod at a time.
- There is no cloud synchronization, account system, P2P discovery, or Pod
  marketplace.
- There is no browser extension or automatic screen/chat monitoring.
- Memory Pod never auto-submits prompts.
- Terminal Radar/social similarity ranking and autonomous agent networks are
  outside the current scope.
- `.mpod` identity and authorship are not cryptographically authenticated.
- Global hotkeys require manual macOS permissions and are less portable than the
  CLI and review-first copy flow.

## Documentation

- [Product constitution v4](PROJECT_DESCRIPTION_V4.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md)
- [Collaboration guide](docs/COLLABORATION.md)
- [Project status snapshot](docs/TASK_BOARD.md)
- [Handoff template](docs/HANDOFF_TEMPLATE.md)
- [Historical roadmap](ROADMAP.md)

---

## 中文文档

[Back to English](#memory-pod)

Memory Pod 诞生于 **2026 AI Hackathon at UC Berkeley**。它探索一个直接的
问题：AI 已经了解并用于帮助你的上下文，不应被锁在某一个 AI 产品中。

### 项目概述

#### 现有问题

AI 助手只有在了解你的工作方式、关注点和当前任务背景时，才能提供更有针对性的
帮助。但这些记忆通常保存在单一服务商的账号中。切换模型时，用户往往需要重新
解释自己，或手动重建同一套上下文。

分享工作方法也有类似问题。检查清单或评审框架可能很有价值，但一段不透明的超长
提示词无法让接收者清楚知道自己采用了什么、又会向外部 AI 发送什么。

#### Memory Pod 的解决方式

Memory Pod 将明确的上下文保存在本地、可检查的容器中，并允许用户在不同 AI
产品中使用这些内容。你可以保留自己的私有记忆，单独接收他人分享的工作手册，
选择与任务相关的部分，并在发送前检查实际进入提示词的内容。

它不会复制一个人或转移隐性经验。它携带的是可见、可检查并由用户控制的事实、
偏好、示例、原则和检查清单。

#### 三步使用流程

1. **拥有或接收上下文。** 从本地笔记建立私有记忆，或检查并导入 Portable
   Shared Pod。
2. **Dock 并审阅。** 选择 Base Pod 和可选 Shared Pod；Memory Pod 只检索与
   当前请求相关的上下文。
3. **在任意 AI 中使用。** 取消选择不希望分享的内容，再把增强提示词复制或粘贴
   到所选 AI 产品中。Memory Pod 不会自动提交。

### 当前状态

Memory Pod 是可运行的 Hackathon MVP v1.1，并非已经完成生产级加固的服务。
本地引擎、Portable Pods、CLI、首次引导、审阅优先的 macOS Pod Dock、显式
写回、可选本地润色、演示工具和自动化测试均已实现。

推荐主路径始终是审阅优先。操作系统级原位注入可用于 macOS 演示，但更可靠的
备用方案仍是可见的复制粘贴流程。

### 核心概念

| 术语 | 含义 |
| --- | --- |
| **Base Pod** | 用户私有且可写的记忆。 |
| **Shared Pod** | 用于分享的工作手册、检查清单、任务视角或示例集合；导入后为只读。 |
| **Pod Dock** | 为任务启用一个 Base Pod；当前 MVP 最多再启用一个 Shared Pod。 |
| **`.mpod`** | 不包含向量和绝对本地路径的可读 Portable Shared Pod 文件。 |
| **增强提示词** | 用户请求与已经审阅批准的相关上下文组合而成的提示词。 |

当前产品边界以
[PROJECT_DESCRIPTION_V4.md](PROJECT_DESCRIPTION_V4.md) 为准。

### 快速开始

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make onboard
make popup
```

按 `Option + Enter`，选择 Base Pod 和可选 Shared Pod，输入请求，检查检索到的
上下文，然后复制增强提示词。弹窗不会向 AI 服务自动提交内容。

### 核心工作流

#### 创建并导入私有 Base Pod

```bash
memory-pod pod create --name "Jiahan" --id jiahan --kind private
memory-pod ingest --pod jiahan ~/Documents/notes
memory-pod remember --pod jiahan --tag preference \
  "Prefer concise explanations with concrete examples."
```

系统只导入 `.md` 和 `.txt`。重新导入同一来源会同步其分块，同时保留显式手动
记忆。

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

本地创建的 Shared Pod 应只包含明确计划分享的内容。私有 Base Pod 不能作为
Shared Pod 导出。

#### 检查并导入 Shared Pod

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

导入前应先检查 `.mpod`。只有在明确替换同 ID 的现有导入 Pod 时才使用
`--replace`。导入内容会在本地重新生成向量，并保持只读。

#### Dock 上下文并生成增强提示词

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

`--debug` 显示检索记录与分数。只使用 Base Pod 时省略 `--shared-pod`。旧版
`--profile` 继续作为 Base Pod 的兼容别名。

如需非破坏性迁移旧版 profile 数据，可运行：

```bash
memory-pod pod migrate-legacy
```

### macOS 桌面交互

#### 审阅优先的 Pod Dock

```bash
make popup
```

Pod Dock 支持 Pod 选择、`.mpod` 导入导出、检索检查、逐条取消选择、显式记忆
写回和复制。`Polish Locally` 可调用本地 Ollama 润色已经审阅的提示词；若
Ollama 不可用或失败，原增强提示词保持不变。

弹窗中的 **Confirm → Hotkey** 会在本地保存活动 Pod 选择，供正在运行的 OS
loop 使用。

#### 可选的输入框原位注入

```bash
make demo-setup
make os-loop

# 覆盖固定演示 Pods：
make os-loop BASE_POD=jiahan SHARED_POD=senior-review
```

聚焦一个 AI 文本框并按 `Option + Enter`。程序会剪切当前文本、增强内容并粘贴
回原位置，但不会按 Enter 或提交提示词。一次只在一个网站使用，提前授予辅助
功能权限，并为演示保留录屏备用方案。

OS loop 运行时，`Control + Shift + Enter` 会把聚焦文本显式保存到私有 Base
Pod。该路径使用复制而非剪切，会恢复剪贴板，也不会粘贴、提交或后台学习。

### CLI 命令参考

| 命令 | 用途 |
| --- | --- |
| `memory-pod ingest [--pod ID] PATH` | 导入本地 `.md` 和 `.txt`。 |
| `memory-pod augment [--base-pod ID] [--shared-pod ID] [--debug] PROMPT` | 检索上下文并生成增强提示词。 |
| `memory-pod compare [--debug] [--reingest] PROMPT` | 运行旧版 Alice/Bob 对比演示。 |
| `memory-pod remember [--pod ID] [--tag TAG] TEXT` | 显式写入本地记忆；`--tag` 可重复。 |
| `memory-pod pod create ...` | 创建私有或共享本地 Pod。 |
| `memory-pod pod list` | 列出可用 Pods。 |
| `memory-pod pod inspect FILE.mpod` | 预览 Portable Shared Pod。 |
| `memory-pod pod import [--replace] FILE.mpod` | 以只读方式导入 Shared Pod。 |
| `memory-pod pod export POD_ID --output FILE.mpod` | 导出本地创建的 Shared Pod。 |
| `memory-pod pod migrate-legacy` | 将旧版演示数据复制到当前 Pod 目录。 |

使用 `memory-pod COMMAND --help` 或 `memory-pod pod COMMAND --help` 查看完整参数。

### 演示命令

| 命令 | 展示内容 |
| --- | --- |
| `make onboard` | 首次创建私有记忆并安装入门 Shared Pods。 |
| `make pod-demo` | 隔离环境中的 Own → Carry → Dock → 选择性检索。 |
| `make demo-setup` | 为弹窗与 OS loop 准备持久化演示 Pods。 |
| `make judge` | 固定的展示流程。 |
| `make demo` | 同一提示词结合不同私有记忆。 |
| `make demo-reingest` | 强制刷新来源后的旧版对比演示。 |
| `make demo-learn` | 显式本地写回及后续检索。 |

演示指南与降级方案见 [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md)。

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

稳定引擎边界包括 `augment()`、`augment_for_profile()`、
`augment_for_stack()` 和 `furnish_selected()`；旧版 profile 接口继续保留兼容性。

### 系统架构

| 领域 | 主要模块 | 职责 |
| --- | --- | --- |
| 配置 | `config.py` | 本地路径、默认值和来源类型。 |
| Pod 策略与可移植性 | `pods.py` | Manifest、Base/Shared 边界和 `.mpod` 导入导出。 |
| 存储与导入 | `memory_store.py`, `ingest.py` | 原子 JSONL 持久化和来源同步。 |
| 本地表示 | `embeddings.py` | 已缓存语义模型与确定性哈希回退。 |
| 检索 | `retrieval.py` | 相关性、词法保护和向量模型兼容。 |
| 提示词增强 | `prompt_assembly.py`, `augment.py` | 上下文分隔、选择和稳定 API。 |
| 写回 | `remember.py` | 显式写入私有 Base Pod。 |
| 交互 | `cli.py`, `hotkey_popup.py`, `os_loop.py` | CLI、审阅优先弹窗与键盘自动化。 |
| 本地润色 | `llm.py`, `rewriter.py` | Ollama 检测和容错润色。 |

### 隐私与信任边界

Memory Pod 是本地优先系统，但不是端到端保密系统。Pod 数据库、向量、检索、
引导问答和可选 Ollama 润色保留在本机。它不读取第三方 AI 的云端记忆、浏览器
登录会话或云端对话历史。

`.mpod` 不包含向量或绝对本地源路径。导入的 Shared Pod 为只读，作者信息由
创建者自行声明而未经过密码学验证，个人记忆只能写入私有可写的 Base Pod。
Shared Pod 内容仅供参考，不能覆盖用户请求、更高优先级指令或安全隐私边界。

当用户把增强提示词发送给 ChatGPT、Claude 或其他服务时，经批准的上下文会
离开本机，并受相应服务商政策约束。导入前和向外发送前都应检查实际内容。

### 环境要求

- Python 3.11 或更高版本。
- 使用本文工作流时需要 `pip` 和 `make`。
- 推荐使用 macOS 运行 Pod Dock 与全局快捷键；依赖可用时，核心 CLI 也可能
  在其他系统运行。
- 全局快捷键与模拟键盘输入需要为 Terminal 或 Python 宿主授予辅助功能权限。
- 可选：本地 Ollama，用于 `Polish Locally`。

### 安装

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

`.venv/bin/python` 存在时，`make` 会优先使用它。必要时可通过
`make check PYTHON=/path/to/python` 覆盖。

Pod 默认保存在：

```text
~/Library/Application Support/Memory Pod/pods/
```

可通过 `MEMORY_POD_HOME` 修改本地目录。

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

运行时 Pod 存储、`.mpod`、虚拟环境、模型缓存和敏感配置不应进入版本控制。

### 开发与验证

```bash
source .venv/bin/activate
make check
```

`make check` 会编译 Python 源码并运行完整 pytest 测试集。也可使用
`make compile`、`make test`，或：

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_pods.py -q
```

修改引擎与交互边界前请阅读
[docs/COLLABORATION.md](docs/COLLABORATION.md)；交接可使用
[docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md)。

### 配置项

Memory Pod 直接读取进程环境变量，不会自动加载 `.env.example`。

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `MEMORY_POD_HOME` | `~/Library/Application Support/Memory Pod` | Pod 存储、引导状态与活动 Dock 选择的根目录。 |
| `MEMORY_POD_PROFILE` | `alice` | 旧版 profile API 的兼容默认值。 |
| `MEMORY_POD_MODEL` | `all-MiniLM-L6-v2` | 本地缓存的 sentence-transformers 模型名称。 |

### 故障排查

- **缺少 `pynput` 或 `pyperclip`：**运行 `make setup`，再激活 `.venv` 或直接
  使用 `.venv/bin/python`。
- **语义模型未缓存：**系统使用确定性的本地哈希回退。只有在明确允许联网且需要
  语义模型时才运行 `python scripts/download_model.py`。
- **Ollama 不可用：**跳过 `Polish Locally`；经审阅的增强提示词仍可直接使用。
- **快捷键无响应：**在 macOS“系统设置 → 隐私与安全性 → 辅助功能”中允许
  Terminal 或 Python 宿主，然后重启进程。
- **没有检索到上下文：**确认 Base Pod，检查 `--debug`，导入相关 `.md` 或
  `.txt`，并使用与内容相关的请求。
- **旧版数据缺失：**运行 `memory-pod pod migrate-legacy`。
- **导入的 Pod 无法编辑：**这是预期行为；如需修改，请创建新的本地 Shared Pod。

### 已知限制

- MVP 同时仅支持一个 Base Pod 和最多一个 Shared Pod。
- 不提供云同步、账号系统、P2P 发现或 Pod 市场。
- 不提供浏览器扩展，也不会自动监控屏幕或聊天。
- Memory Pod 不会自动提交提示词。
- Terminal Radar/社交相似度排名及自治 Agent 网络不在当前范围内。
- `.mpod` 身份和作者信息没有密码学认证。
- 全局快捷键需要手动授予 macOS 权限，其可移植性低于 CLI 和审阅优先流程。

### 相关文档

- [产品章程 v4](PROJECT_DESCRIPTION_V4.md)
- [演示手册](docs/DEMO_RUNBOOK.md)
- [协作指南](docs/COLLABORATION.md)
- [项目状态快照](docs/TASK_BOARD.md)
- [交接模板](docs/HANDOFF_TEMPLATE.md)
- [历史路线图](ROADMAP.md)
