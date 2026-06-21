"""Shared 'active dock' selection between the popup and the OS-loop daemon.

The Pod Dock popup and the Tier-2 ``os_loop`` hotkey daemon are separate
processes. This module is the tiny bridge between them: the popup writes the
currently selected Base/Shared Pod to a small JSON file under MEMORY_POD_HOME,
and the daemon re-reads it on each Option+Enter so the global hotkey follows the
popup without a restart.

Deliberately defensive — a missing or corrupt file yields ``None`` so callers
fall back to their launch pods instead of crashing the hotkey loop.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from memory_pod.config import MEMORY_POD_HOME

ACTIVE_DOCK_FILENAME = "active_dock.json"


@dataclass(frozen=True)
class ActiveDock:
    base_pod: str
    shared_pod: str | None = None


def active_dock_path(home: Path = MEMORY_POD_HOME) -> Path:
    return home / ACTIVE_DOCK_FILENAME


def write_active_dock(
    base_pod: str,
    shared_pod: str | None = None,
    home: Path = MEMORY_POD_HOME,
) -> None:
    """Persist the active Base/Shared Pod selection for the hotkey daemon."""
    home.mkdir(parents=True, exist_ok=True)
    payload = {"base_pod": base_pod, "shared_pod": shared_pod}
    active_dock_path(home).write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def read_active_dock(home: Path = MEMORY_POD_HOME) -> ActiveDock | None:
    """Return the active dock selection, or ``None`` if unset/unreadable."""
    path = active_dock_path(home)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    base_pod = data.get("base_pod")
    if not isinstance(base_pod, str) or not base_pod.strip():
        return None
    shared_pod = data.get("shared_pod")
    if not isinstance(shared_pod, str) or not shared_pod.strip():
        shared_pod = None
    return ActiveDock(base_pod=base_pod, shared_pod=shared_pod)
