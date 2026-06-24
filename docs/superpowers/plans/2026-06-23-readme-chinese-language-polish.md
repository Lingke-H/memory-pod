# Memory Pod README Chinese Language Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the Chinese README in concise, professional, natural Simplified Chinese while preserving every command, link, technical fact, and product boundary.

**Architecture:** Edit only the Chinese section of `README.md` and its documentation contract. Keep the English section and information hierarchy unchanged; use a test-first terminology guard followed by semantic and command/link verification.

**Tech Stack:** GitHub-flavored Markdown, Simplified Chinese technical prose, pytest documentation tests.

## Global Constraints

- Use a concise, professional, restrained tone suitable for open-source readers and technical hackathon judges.
- Keep `Base Pod`, `Shared Pod`, `Pod Dock`, `.mpod`, CLI, Ollama, JSONL, and API unchanged.
- Preserve commands, paths, environment variables, Markdown links, section order, and all technical boundaries.
- Do not edit the English README or product source code.
- Do not add claims, features, or omissions relative to the English section.
- Do not edit the four pre-existing untracked duplicate files.

---

### Task 1: Add a Chinese Language-Quality Contract

**Files:**
- Modify: `tests/test_documentation.py`
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the Chinese substring beginning at `## 中文文档`.
- Produces: a regression test that rejects known translation-like wording and requires the approved natural terminology.

- [ ] **Step 1: Add the failing test**

Append:

```python
def test_chinese_readme_uses_natural_product_language():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = readme[readme.index("## 中文文档") :]

    for awkward_phrase in (
        "显式写回",
        "输入框原位注入",
        "本地表示",
        "容错润色",
        "活动 Pod 选择",
        "该路径使用复制而非剪切",
    ):
        assert awkward_phrase not in chinese

    for natural_phrase in (
        "主动保存为记忆",
        "直接回填当前输入框",
        "向量表示",
        "带降级机制的本地润色",
        "当前选中的 Pod",
    ):
        assert natural_phrase in chinese
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: the seven existing tests pass and the new language-quality test fails on the current translation-like phrases.

---

### Task 2: Rewrite the Chinese README as Native Technical Prose

**Files:**
- Modify: `README.md` from `## 中文文档` to end of file
- Test: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the English README as the factual source and the existing Chinese section as the command/link source.
- Produces: a semantically equivalent Chinese section written in natural Simplified Chinese.

- [ ] **Step 1: Rewrite the lead-in and product explanation**

Keep the existing headings, but rewrite the prose with these exact editorial directions:

```text
Opening: Memory Pod 诞生于 2026 AI Hackathon at UC Berkeley。它想解决一个很实际的问题：那些让 AI 更懂你的上下文，不该被困在某一个产品里。

Problem: explain that switching AI products forces users to repeat preferences and background; explain that opaque long prompts make shared methods hard to inspect.

Solution: explain that Memory Pod stores explicit context locally, separates private memory from shared playbooks, retrieves only relevant content, and lets the user inspect it before sending.
```

Use “用户主动保存的新记忆” instead of “显式写回”, “直接回填当前输入框” instead of “输入框原位注入”, and “审阅优先” consistently.

- [ ] **Step 2: Rewrite workflow and desktop sections**

Preserve every fenced command exactly. Rewrite surrounding copy so that:

- “重新导入同一来源会同步更新对应内容” replaces “同步其分块”.
- Imported Shared Pods are described as “导入后保持只读”.
- `Confirm → Hotkey` saves “当前选中的 Pod”.
- The optional hotkey section is headed `#### 可选：直接回填当前输入框`.
- The remember hotkey “复制文本、恢复原剪贴板内容，不会自动粘贴或提交”.

- [ ] **Step 3: Rewrite technical reference with natural terminology**

Keep the CLI and demo tables' commands unchanged. In the architecture table use:

```markdown
| 向量表示 | `embeddings.py` | 使用本地缓存的语义模型，并在模型不可用时回退到确定性哈希方案。 |
| 本地润色 | `llm.py`, `rewriter.py` | 检测 Ollama，并提供带降级机制的本地润色。 |
```

Use “来源更新” instead of “来源同步”, “兼容不同向量模型” instead of “向量模型兼容”, and “稳定的公开接口” instead of “稳定 API” where prose allows.

- [ ] **Step 4: Rewrite privacy, requirements, troubleshooting, and limitations**

Preserve every factual boundary while using direct Chinese:

- “本地优先并不等于端到端保密”.
- “一旦用户把增强提示词发送给外部 AI 服务，其中获准使用的上下文也会离开本机”.
- “作者信息未经密码学验证”.
- “全局快捷键依赖 macOS 辅助功能权限，可移植性不如 CLI 和复制粘贴流程”.

Avoid repeated “系统会”, “该路径”, “当前范围”, and “显式”.

- [ ] **Step 5: Run the documentation tests and verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src .venv/bin/python -m pytest tests/test_documentation.py -q
```

Expected: all eight documentation tests pass.

- [ ] **Step 6: Verify commands and links remain present**

Run:

```bash
rg -n '^```bash$|memory-pod|make |PROJECT_DESCRIPTION_V4|docs/' README.md
git diff --check
```

Expected: documented commands and local links remain in both language sections; no whitespace errors.

- [ ] **Step 7: Commit the language polish**

```bash
git add README.md tests/test_documentation.py
git commit -m "docs: polish Chinese readme language"
```

---

### Task 3: Verify the Complete Repository

**Files:**
- Verify: `README.md`
- Verify: `tests/test_documentation.py`

**Interfaces:**
- Consumes: the polished Chinese section.
- Produces: final test, scope, and preservation evidence.

- [ ] **Step 1: Run the full project checks**

Run:

```bash
make check
```

Expected: compilation succeeds and all 100 pytest tests pass.

- [ ] **Step 2: Inspect final scope**

Run:

```bash
git diff --check
git status --short
```

Expected: the implementation commit changes only `README.md` and
`tests/test_documentation.py`; the four pre-existing duplicate files remain
untracked and untouched in the main working directory.
