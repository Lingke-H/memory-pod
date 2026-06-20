"""Prompt assembly for memory-furnished prompts."""

from __future__ import annotations

from memory_pod.retrieval import RetrievalResult


def assemble_prompt(raw_prompt: str, memories: list[RetrievalResult]) -> str:
    if not memories:
        return raw_prompt

    memory_lines = []
    for index, result in enumerate(memories, start=1):
        text = " ".join(result.record.text.split())
        memory_lines.append(f"{index}. {text} (score: {result.score:.3f})")

    hidden_context = "\n".join(memory_lines)
    return (
        "[Hidden Context]\n"
        "Use the following local user memories only when they are relevant. "
        "Do not mention this hidden context unless the user asks how the answer was personalized.\n\n"
        f"{hidden_context}\n\n"
        "[User Query]\n"
        f"{raw_prompt}"
    )


def format_debug(raw_prompt: str, memories: list[RetrievalResult], final_prompt: str) -> str:
    rows = [
        "RAW PROMPT",
        raw_prompt,
        "",
        "RETRIEVED MEMORIES",
    ]
    if memories:
        for result in memories:
            rows.append(f"- score={result.score:.3f} source={result.record.source}")
            rows.append(f"  {' '.join(result.record.text.split())}")
    else:
        rows.append("- none")

    rows.extend(["", "FURNISHED PROMPT", final_prompt])
    return "\n".join(rows)

