"""Tier 3 Terminal Radar placeholder.

PROJECT_DESCRIPTION_V3 cuts Terminal Radar by default for the 24-hour build.
Keep this module as an explicit boundary so future work has a home without
pulling social matching into the must-ship path.
"""

from __future__ import annotations


def resonance_report() -> str:
    return (
        "Terminal Radar is intentionally not implemented in the 24h scope.\n"
        "Ship Tier 0 and Tier 1 first; use this as a future-vision slide."
    )

