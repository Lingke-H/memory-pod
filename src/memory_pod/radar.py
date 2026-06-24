"""Explicit boundary for the out-of-scope Terminal Radar concept.

PROJECT_DESCRIPTION_V4 excludes social similarity ranking from the MVP. Keep
this module as a named boundary for historical prototypes without presenting it
as an implemented capability.
"""

from __future__ import annotations


def resonance_report() -> str:
    return (
        "Terminal Radar is intentionally outside the current MVP scope.\n"
        "Use the implemented local Base Pod and Shared Pod workflows instead."
    )
