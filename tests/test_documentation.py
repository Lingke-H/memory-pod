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
