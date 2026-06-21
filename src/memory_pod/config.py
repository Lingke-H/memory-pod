"""Configuration helpers for Memory Pod."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
DATA_DIR = REPO_ROOT / "data"
DEMO_PROFILES_DIR = DATA_DIR / "profiles"
LEGACY_PROFILES_DIR = DEMO_PROFILES_DIR

DEFAULT_MEMORY_POD_HOME = Path.home() / "Library" / "Application Support" / "Memory Pod"
MEMORY_POD_HOME = Path(
    os.getenv("MEMORY_POD_HOME", str(DEFAULT_MEMORY_POD_HOME))
).expanduser()
PODS_DIR = MEMORY_POD_HOME / "pods"

# Backward-compatible name for the original profile-based Engine API.
PROFILES_DIR = PODS_DIR

DEFAULT_PROFILE = os.getenv("MEMORY_POD_PROFILE", "alice")
DEFAULT_MODEL_NAME = os.getenv("MEMORY_POD_MODEL", "all-MiniLM-L6-v2")
MEMORY_STORE_FILENAME = "memories.jsonl"
POD_MANIFEST_FILENAME = "pod.json"

SUPPORTED_INGEST_SUFFIXES = {".md", ".txt"}
