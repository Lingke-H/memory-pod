"""Local LLM helpers (Ollama).

Keeps the optional local-model dependency behind one small module so the rest of
the app degrades gracefully when Ollama isn't installed/running.
"""

from __future__ import annotations

import urllib.request

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


def ollama_available(host: str = DEFAULT_OLLAMA_HOST, timeout: float = 0.7) -> bool:
    """Return True if a local Ollama server is reachable.

    Never raises — a down/absent server simply returns False so callers can fall
    back to the non-LLM template path.
    """
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False
