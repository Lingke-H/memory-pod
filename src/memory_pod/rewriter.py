"""Optional local prompt polishing with Ollama.

This module is deliberately outside the core furnish path. If local Ollama is
missing or slow, Memory Pod keeps the inspected furnished prompt unchanged.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from memory_pod.llm import DEFAULT_MODEL, DEFAULT_OLLAMA_HOST, ollama_available


@dataclass(frozen=True)
class RewriteResult:
    text: str
    used_local_ai: bool
    note: str


def build_rewrite_prompt(raw_prompt: str, furnished_prompt: str) -> str:
    """Build the local-LLM instruction for a clean, copy-ready prompt."""

    return f"""You are polishing a prompt locally before the user copies it into another AI.

Goal:
- Turn the furnished prompt into one clean, copy-ready prompt.
- Preserve the user's intent.
- Use only facts already present in the raw prompt or furnished prompt; do not invent facts.
- Keep any safety/privacy boundary from the furnished prompt.
- Do not include markdown fences, analysis, or commentary.

Raw prompt:
{raw_prompt.strip()}

Furnished prompt:
{furnished_prompt.strip()}

Output one clean, copy-ready prompt only."""


def polish_locally(
    raw_prompt: str,
    furnished_prompt: str,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_OLLAMA_HOST,
    timeout: float = 8.0,
) -> RewriteResult:
    """Use a local Ollama model to polish a furnished prompt, with safe fallback."""

    fallback = furnished_prompt.strip()
    if not fallback:
        return RewriteResult(
            text="",
            used_local_ai=False,
            note="Nothing to polish yet — click Furnish first.",
        )

    if not ollama_available(host=host, timeout=min(timeout, 0.7)):
        return RewriteResult(
            text=fallback,
            used_local_ai=False,
            note="Local AI unavailable; using furnished prompt.",
        )

    prompt = build_rewrite_prompt(raw_prompt, fallback)
    try:
        rewritten = _ollama_generate(prompt, model=model, host=host, timeout=timeout).strip()
    except (OSError, ValueError, urllib.error.URLError, TimeoutError):
        return RewriteResult(
            text=fallback,
            used_local_ai=False,
            note="Local AI failed; using furnished prompt.",
        )

    if not rewritten:
        return RewriteResult(
            text=fallback,
            used_local_ai=False,
            note="Local AI returned empty text; using furnished prompt.",
        )

    return RewriteResult(
        text=rewritten,
        used_local_ai=True,
        note=f"Polished locally with {model}.",
    )


def _ollama_generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    host: str = DEFAULT_OLLAMA_HOST,
    timeout: float = 8.0,
) -> str:
    payload = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    text = data.get("response", "")
    if not isinstance(text, str):
        raise ValueError("Ollama response field was not text.")
    return text
