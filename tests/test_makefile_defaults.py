from pathlib import Path


def test_os_loop_defaults_match_demo_setup_pods():
    makefile = Path("Makefile").read_text(encoding="utf-8")

    assert "BASE_POD ?= jiahan" in makefile
    assert "SHARED_POD ?= senior-review" in makefile
