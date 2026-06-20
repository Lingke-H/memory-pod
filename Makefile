.PHONY: setup check test compile seed demo demo-reingest demo-learn judge popup clean

PYTHON ?= python

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

check: compile test

compile:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) -m compileall src tests scripts

test:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) -m pytest

seed:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) scripts/seed_demo_profiles.py

demo:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) -m memory_pod.cli compare --debug "help me write this application"

demo-reingest:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) -m memory_pod.cli compare --reingest --debug "help me write this application"

demo-learn:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) scripts/demo_learn.py

judge:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) scripts/judge_demo.py

popup:
	PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src $(PYTHON) -m memory_pod.hotkey_popup

clean:
	rm -rf .pytest_cache
	rm -rf src/memory_pod/__pycache__ tests/__pycache__ scripts/__pycache__
	rm -f data/profiles/*/memories.jsonl

