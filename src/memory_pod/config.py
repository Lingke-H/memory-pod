"""Configuration helpers for Memory Pod.

The defaults are intentionally local-only. Profile data lives under the repo's
`data/profiles` directory unless the caller passes explicit paths in tests or
future app wiring.
"""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
DATA_DIR = REPO_ROOT / "data"
PROFILES_DIR = DATA_DIR / "profiles"

DEFAULT_PROFILE = os.getenv("MEMORY_POD_PROFILE", "alice")
DEFAULT_MODEL_NAME = os.getenv("MEMORY_POD_MODEL", "all-MiniLM-L6-v2")
MEMORY_STORE_FILENAME = "memories.jsonl"

SUPPORTED_INGEST_SUFFIXES = {".md", ".txt"}

