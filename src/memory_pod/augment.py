"""Public Memory Pod augmentation contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.pods import PodStack, get_pod_manifest, require_private_writable_pod
from memory_pod.prompt_assembly import assemble_prompt, assemble_stack_prompt, format_debug
from memory_pod.retrieval import RetrievalResult, retrieve


@dataclass(frozen=True)
class AugmentResult:
    raw_prompt: str
    profile: str
    memories: list[RetrievalResult]
    furnished_prompt: str
    active_pods: tuple[str, ...] = ()

    def debug_text(self) -> str:
        return format_debug(
            self.raw_prompt,
            self.memories,
            self.furnished_prompt,
            self.active_pods,
        )


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
        active_pods=(profile,),
    )


def augment_for_stack(
    raw_prompt: str,
    stack: PodStack,
    top_k: int = 5,
    pods_root: Path = PROFILES_DIR,
) -> AugmentResult:
    require_private_writable_pod(stack.base_pod, pods_root)
    if stack.shared_pod:
        shared_manifest = get_pod_manifest(stack.shared_pod, pods_root)
        if shared_manifest is None:
            raise FileNotFoundError(f"Shared Pod '{stack.shared_pod}' does not exist.")
        if shared_manifest.kind != "shared":
            raise ValueError(f"Pod '{stack.shared_pod}' is not a Shared Pod.")

    base_memories = retrieve(
        raw_prompt,
        profile=stack.base_pod,
        top_k=top_k,
        profiles_root=pods_root,
    )
    shared_memories = (
        retrieve(
            raw_prompt,
            profile=stack.shared_pod,
            top_k=top_k,
            profiles_root=pods_root,
        )
        if stack.shared_pod
        else []
    )
    memories = _merge_stack_results(base_memories, shared_memories, stack, top_k)
    furnished_prompt = furnish_selected(raw_prompt, memories, stack, pods_root)
    return AugmentResult(
        raw_prompt=raw_prompt,
        profile=stack.base_pod,
        memories=memories,
        furnished_prompt=furnished_prompt,
        active_pods=stack.active_pods,
    )


def furnish_selected(
    raw_prompt: str,
    memories: list[RetrievalResult],
    stack: PodStack,
    pods_root: Path = PROFILES_DIR,
) -> str:
    pod_names = {}
    for pod_id in stack.active_pods:
        try:
            manifest = get_pod_manifest(pod_id, pods_root)
        except (OSError, KeyError, TypeError, ValueError):
            manifest = None
        pod_names[pod_id] = manifest.name if manifest else pod_id
    return assemble_stack_prompt(raw_prompt, memories, stack, pod_names)


def _merge_stack_results(
    base_memories: list[RetrievalResult],
    shared_memories: list[RetrievalResult],
    stack: PodStack,
    top_k: int,
) -> list[RetrievalResult]:
    deduplicated = []
    seen_text = set()
    for result in [*base_memories, *shared_memories]:
        normalized = " ".join(result.record.text.lower().split())
        if normalized in seen_text:
            continue
        seen_text.add(normalized)
        deduplicated.append(result)

    return sorted(
        deduplicated,
        key=lambda item: (item.score, item.pod_id == stack.base_pod),
        reverse=True,
    )[: max(top_k, 0)]
