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
