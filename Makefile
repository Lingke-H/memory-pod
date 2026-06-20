.PHONY: setup check test compile seed demo demo-reingest clean

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

clean:
	rm -rf .pytest_cache
	rm -rf src/memory_pod/__pycache__ tests/__pycache__ scripts/__pycache__
	rm -f data/profiles/*/memories.jsonl

