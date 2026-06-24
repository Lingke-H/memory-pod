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

Memory Pod 诞生于 **2026 AI Hackathon at UC Berkeley**。我们想解决一个很
实际的问题：那些让 AI 更懂你的上下文，不该被困在某一个产品里。

### 项目概述

#### 现有问题

AI 助手越了解你的工作方式、关注点和任务背景，给出的帮助通常就越贴合需求。
但这些记忆往往被保存在某一家服务商的账号里。换一个模型，用户常常又要从头介绍
自己，重新补充同样的背景。

分享工作方法也面临类似问题。一份检查清单或评审框架或许很有价值，但如果它只是
一段不透明的超长提示词，接收者既难以看清其中包含什么，也无法确定最终会把哪些
内容发送给外部 AI。

#### Memory Pod 的解决方式

Memory Pod 把明确的上下文保存在本地、可查看的 Pod 中，让同一份上下文能够在
不同的 AI 产品之间使用。你可以保留自己的私有记忆，也可以单独接收他人分享的
工作手册；系统只检索当前任务需要的内容，并在发送前把实际采用的上下文完整展示
出来。

Memory Pod 不会“复制”一个人，也无法转移隐性经验。它所承载的是用户能够查看、
理解并控制的事实、偏好、示例、原则和检查清单。

#### 三步使用流程

1. **建立或接收上下文。** 从本地笔记创建私有记忆，或者先查看、再导入
   Portable Shared Pod。
2. **Dock 并审阅。** 选择 Base Pod 和可选的 Shared Pod；Memory Pod 只会
   检索与当前请求相关的内容。
3. **在任意 AI 中使用。** 取消勾选不想分享的内容，再把增强提示词复制或回填到
   目标 AI 产品中。Memory Pod 不会替你提交。

### 当前状态

Memory Pod 目前是一个可以实际运行的 Hackathon MVP v1.1，尚未按照生产环境
标准全面加固。本地引擎、Portable Pods、CLI、首次使用引导、审阅优先的 macOS
Pod Dock、主动保存记忆、可选的本地润色、演示工具和自动化测试都已经实现。

目前最稳妥的使用方式是先审阅、再发送。macOS 上也支持直接回填输入框，但该功能
主要用于演示；遇到问题时，仍建议使用更直观可靠的复制粘贴流程。

### 核心概念

| 术语 | 含义 |
| --- | --- |
| **Base Pod** | 属于用户个人、可以持续写入的私有记忆。 |
| **Shared Pod** | 用于分享的工作手册、检查清单、任务视角或示例集合；导入后保持只读。 |
| **Pod Dock** | 为当前任务启用一个 Base Pod；现阶段最多再搭配一个 Shared Pod。 |
| **`.mpod`** | 可直接查看的 Portable Shared Pod 文件，不包含向量或本机绝对路径。 |
| **增强提示词** | 用户原始请求与已审阅、已批准的相关上下文组合而成的提示词。 |

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

完成安装后，按 `Option + Enter` 打开 Pod Dock。选择 Base Pod 和可选的
Shared Pod，输入请求并检查检索结果，然后复制增强提示词。Pod Dock 不会把内容
自动提交给任何 AI 服务。

### 核心工作流

#### 创建并导入私有 Base Pod

```bash
memory-pod pod create --name "Jiahan" --id jiahan --kind private
memory-pod ingest --pod jiahan ~/Documents/notes
memory-pod remember --pod jiahan --tag preference \
  "Prefer concise explanations with concrete examples."
```

Memory Pod 只导入 `.md` 和 `.txt` 文件。重新导入同一来源时，会更新对应内容；
用户主动保存的新记忆不会受到影响。

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

本地创建的 Shared Pod 应当只包含你明确准备分享的内容。私有 Base Pod 不能
导出为 Shared Pod。

#### 检查并导入 Shared Pod

```bash
memory-pod pod inspect Senior-Review.mpod
memory-pod pod import Senior-Review.mpod
memory-pod pod list
```

导入前请先查看 `.mpod` 的内容。只有在确实需要替换同 ID 的已导入 Pod 时，才
使用 `--replace`。导入后，Memory Pod 会在本机重新生成向量，Pod 仍保持只读。

#### Dock 上下文并生成增强提示词

```bash
memory-pod augment \
  --base-pod jiahan \
  --shared-pod senior-review \
  --debug \
  "Review this API design"
```

`--debug` 会显示检索到的记录及其分数。只使用 Base Pod 时，可以省略
`--shared-pod`。旧版 `--profile` 参数仍然可用，作用等同于指定 Base Pod。

如需保留原文件并迁移旧版 profile 数据，可运行：

```bash
memory-pod pod migrate-legacy
```

### macOS 桌面交互

#### 审阅优先的 Pod Dock

```bash
make popup
```

Pod Dock 支持选择 Pod、导入和导出 `.mpod`、查看检索结果、逐条取消勾选、
主动保存为记忆，以及复制最终提示词。`Polish Locally` 可以调用本机 Ollama，
对已经审阅的提示词做进一步润色；如果 Ollama 未启动或处理失败，Memory Pod
会直接保留原来的增强提示词。

点击 **Confirm → Hotkey** 后，Pod Dock 会在本地记录当前选中的 Pod，正在
运行的 OS loop 会在下一次触发时读取这项选择。

#### 可选：直接回填当前输入框

```bash
make demo-setup
make os-loop

# 覆盖固定演示 Pods：
make os-loop BASE_POD=jiahan SHARED_POD=senior-review
```

把光标放在一个 AI 输入框中，然后按 `Option + Enter`。程序会选中并剪切当前
文本，补充相关上下文后再回填输入框，但不会按下 Enter，也不会替你提交。建议
一次只在一个网站上使用，并提前授予辅助功能权限；公开演示时最好准备一段录屏
作为备用。

OS loop 运行时，按 `Control + Shift + Enter` 可以把输入框中的文字主动保存为
记忆。这个操作只会复制文本，并在完成后恢复原有的剪贴板内容；不会自动回填、
提交，也不会在后台持续学习。

### CLI 命令参考

| 命令 | 用途 |
| --- | --- |
| `memory-pod ingest [--pod ID] PATH` | 导入本地 `.md` 和 `.txt` 文件。 |
| `memory-pod augment [--base-pod ID] [--shared-pod ID] [--debug] PROMPT` | 检索上下文并生成增强提示词。 |
| `memory-pod compare [--debug] [--reingest] PROMPT` | 运行旧版 Alice/Bob 对比演示。 |
| `memory-pod remember [--pod ID] [--tag TAG] TEXT` | 主动写入一条本地记忆；`--tag` 可以重复使用。 |
| `memory-pod pod create ...` | 创建私有或共享本地 Pod。 |
| `memory-pod pod list` | 列出可用 Pods。 |
| `memory-pod pod inspect FILE.mpod` | 查看 Portable Shared Pod 的内容。 |
| `memory-pod pod import [--replace] FILE.mpod` | 以只读方式导入 Shared Pod。 |
| `memory-pod pod export POD_ID --output FILE.mpod` | 导出本地创建的 Shared Pod。 |
| `memory-pod pod migrate-legacy` | 把旧版演示数据复制到当前 Pod 目录。 |

使用 `memory-pod COMMAND --help` 或 `memory-pod pod COMMAND --help` 查看完整参数。

### 演示命令

| 命令 | 展示内容 |
| --- | --- |
| `make onboard` | 首次创建私有记忆，并安装示例 Shared Pods。 |
| `make pod-demo` | 在隔离环境中演示 Own → Carry → Dock → 选择性检索。 |
| `make demo-setup` | 为 Pod Dock 和 OS loop 准备持久化演示 Pods。 |
| `make judge` | 固定的展示流程。 |
| `make demo` | 同一提示词结合不同私有记忆。 |
| `make demo-reingest` | 强制刷新数据来源后运行旧版对比演示。 |
| `make demo-learn` | 主动保存记忆，并验证后续检索结果。 |

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

引擎对外提供稳定的 `augment()`、`augment_for_profile()`、
`augment_for_stack()` 和 `furnish_selected()` 接口；旧版 profile 接口继续兼容。

### 系统架构

| 领域 | 主要模块 | 职责 |
| --- | --- | --- |
| 配置 | `config.py` | 管理本地路径、默认值和支持的数据来源。 |
| Pod 策略与可移植性 | `pods.py` | 管理 Manifest、Base/Shared 边界，以及 `.mpod` 的导入导出。 |
| 存储与导入 | `memory_store.py`, `ingest.py` | 以原子方式写入 JSONL，并处理来源更新。 |
| 向量表示 | `embeddings.py` | 使用本地缓存的语义模型，并在模型不可用时回退到确定性哈希方案。 |
| 检索 | `retrieval.py` | 计算相关性、执行词法保护，并兼容不同向量模型。 |
| 提示词增强 | `prompt_assembly.py`, `augment.py` | 分隔和筛选上下文，并提供稳定的公开接口。 |
| 记忆写入 | `remember.py` | 把用户主动保存的内容写入私有 Base Pod。 |
| 交互 | `cli.py`, `hotkey_popup.py`, `os_loop.py` | 提供 CLI、审阅优先的 Pod Dock 和可选的键盘自动化。 |
| 本地润色 | `llm.py`, `rewriter.py` | 检测 Ollama，并提供带降级机制的本地润色。 |

### 隐私与信任边界

本地优先并不等于端到端保密。Pod 数据、向量、检索过程、首次引导中的回答，以及
可选的 Ollama 润色都留在本机。Memory Pod 不会读取第三方 AI 的云端记忆、
浏览器登录状态或云端对话记录。

`.mpod` 不包含向量或本机绝对路径。导入的 Shared Pod 始终为只读；作者信息由
创建者自行填写，未经密码学验证。个人记忆只能写入私有且可写的 Base Pod。
Shared Pod 中的内容仅供参考，不能覆盖用户请求、更高优先级的指令，以及既定的
安全和隐私边界。

一旦用户把增强提示词发送给 ChatGPT、Claude 或其他外部 AI 服务，其中获准
使用的上下文也会离开本机，并受相应服务商的政策约束。因此，无论导入 `.mpod`
还是向外发送提示词，都应先检查具体内容。

### 环境要求

- Python 3.11 或更高版本。
- 按本文流程安装和运行时，需要 `pip` 和 `make`。
- Pod Dock 和全局快捷键主要面向 macOS；如果依赖齐全，核心 CLI 也可以在其他
  系统上运行。
- 使用全局快捷键和模拟键盘输入前，需要为 Terminal 或 Python 进程授予辅助
  功能权限。
- 如需使用 `Polish Locally`，还需要在本机运行 Ollama。

### 安装

```bash
git clone https://github.com/Lingke-H/memory-pod.git
cd memory-pod
python3 -m venv .venv
source .venv/bin/activate
make setup
make check
```

如果 `.venv/bin/python` 存在，`make` 会优先使用它。需要指定其他解释器时，
可运行 `make check PYTHON=/path/to/python`。

Pod 默认保存在：

```text
~/Library/Application Support/Memory Pod/pods/
```

可以通过 `MEMORY_POD_HOME` 修改数据目录。

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

运行时生成的 Pod 数据、`.mpod` 文件、虚拟环境、模型缓存和敏感配置都不应提交
到版本控制系统。

### 开发与验证

```bash
source .venv/bin/activate
make check
```

`make check` 会先编译 Python 源码，再运行完整的 pytest 测试集。也可以单独
使用 `make compile`、`make test`，或运行：

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/test_pods.py -q
```

修改引擎与交互层之间的接口前，请先阅读
[docs/COLLABORATION.md](docs/COLLABORATION.md)；交接工作可使用
[docs/HANDOFF_TEMPLATE.md](docs/HANDOFF_TEMPLATE.md)。

### 配置项

Memory Pod 直接读取进程环境变量，不会自动载入 `.env.example`。

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `MEMORY_POD_HOME` | `~/Library/Application Support/Memory Pod` | Pod 数据、首次引导状态和当前 Dock 选择的根目录。 |
| `MEMORY_POD_PROFILE` | `alice` | 旧版 profile API 的兼容默认值。 |
| `MEMORY_POD_MODEL` | `all-MiniLM-L6-v2` | 本机缓存的 sentence-transformers 模型名称。 |

### 故障排查

- **提示缺少 `pynput` 或 `pyperclip`：**运行 `make setup`，然后激活 `.venv`，
  或直接使用 `.venv/bin/python`。
- **本机没有缓存语义模型：**Memory Pod 会改用确定性的本地哈希方案。只有在确实
  需要语义模型并允许联网时，才运行 `python scripts/download_model.py`。
- **Ollama 不可用：**可以跳过 `Polish Locally`；已经审阅的增强提示词仍可正常
  使用。
- **快捷键没有反应：**在 macOS 的“系统设置 → 隐私与安全性 → 辅助功能”中允许
  Terminal 或对应的 Python 进程，然后重新启动程序。
- **没有检索到上下文：**确认所选 Base Pod 是否正确，查看 `--debug` 输出，
  导入相关的 `.md` 或 `.txt` 文件，并确保请求与内容确实相关。
- **看不到旧版数据：**运行 `memory-pod pod migrate-legacy`。
- **无法编辑导入的 Pod：**这是预期行为。需要修改时，请创建一个新的本地
  Shared Pod。

### 已知限制

- MVP 同时只能启用一个 Base Pod 和最多一个 Shared Pod。
- 暂不提供云同步、账号系统、P2P 发现或 Pod 市场。
- 没有浏览器扩展，也不会自动监控屏幕或聊天内容。
- Memory Pod 不会自动提交提示词。
- Terminal Radar、社交相似度排名和自治 Agent 网络不在本期范围内。
- `.mpod` 中的身份和作者信息没有经过密码学认证。
- 全局快捷键依赖 macOS 辅助功能权限，可移植性不如 CLI 和复制粘贴流程。

### 相关文档

- [产品章程 v4](PROJECT_DESCRIPTION_V4.md)
- [演示手册](docs/DEMO_RUNBOOK.md)
- [协作指南](docs/COLLABORATION.md)
- [项目状态快照](docs/TASK_BOARD.md)
- [交接模板](docs/HANDOFF_TEMPLATE.md)
- [历史路线图](ROADMAP.md)
