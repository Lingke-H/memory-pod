"""Public Memory Pod augmentation contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.prompt_assembly import assemble_prompt, format_debug
from memory_pod.retrieval import RetrievalResult, retrieve


@dataclass(frozen=True)
class AugmentResult:
    raw_prompt: str
    profile: str
    memories: list[RetrievalResult]
    furnished_prompt: str

    def debug_text(self) -> str:
        return format_debug(self.raw_prompt, self.memories, self.furnished_prompt)


def augment(raw_prompt: str) -> str:
    """Return a memory-furnished prompt for the user's raw prompt."""

    return augment_for_profile(raw_prompt, profile=DEFAULT_PROFILE).furnished_prompt


def augment_for_profile(
    raw_prompt: str,
    profile: str,
    top_k: int = 5,
    profiles_root: Path = PROFILES_DIR,
) -> AugmentResult:
    memories = retrieve(raw_prompt, profile=profile, top_k=top_k, profiles_root=profiles_root)
    furnished_prompt = assemble_prompt(raw_prompt, memories)
    return AugmentResult(
        raw_prompt=raw_prompt,
        profile=profile,
        memories=memories,
        furnished_prompt=furnished_prompt,
    )
