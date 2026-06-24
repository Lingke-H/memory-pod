from pathlib import Path


def test_os_loop_defaults_match_demo_setup_pods():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "BASE_POD ?= jiahan" in makefile
    assert "SHARED_POD ?= senior-review" in makefile


def test_makefile_prefers_repo_virtualenv_with_system_fallback():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert (
        "PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)"
        in makefile
    )
