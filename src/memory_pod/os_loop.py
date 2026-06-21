"""OS-level hotkey loop for Memory Pod.

This Tier 2 module intentionally knows almost nothing about the memory engine.
It owns only the global hotkey, clipboard handoff, and keyboard macro. The
memory layer stays behind the augment() contract.
"""

from __future__ import annotations

import argparse
import logging
import platform
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pynput import keyboard
import pyperclip

from memory_pod.augment import augment, augment_for_profile, augment_for_stack
from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.pods import PodStack
from memory_pod.remember import remember

LOGGER = logging.getLogger("memory_pod.os_loop")


def build_augment_fn(
    base_pod: str = DEFAULT_PROFILE,
    shared_pod: str | None = None,
    pods_root: Path = PROFILES_DIR,
) -> Callable[[str], str]:
    """Furnish raw input from a Base Pod (+ optional Shared Pod).

    Returns a ``str -> str`` callable that the hotkey loop pastes back in place.
    Keeps the OS layer behind the public augment contract — it never touches the
    store or retrieval internals directly.
    """

    def _augment(raw_prompt: str) -> str:
        if shared_pod:
            stack = PodStack(base_pod=base_pod, shared_pod=shared_pod)
            return augment_for_stack(raw_prompt, stack, pods_root=pods_root).furnished_prompt
        return augment_for_profile(
            raw_prompt, profile=base_pod, profiles_root=pods_root
        ).furnished_prompt

    return _augment


def build_remember_fn(
    base_pod: str = DEFAULT_PROFILE,
    pods_root: Path = PROFILES_DIR,
) -> Callable[[str], str]:
    """Build the explicit OS hotkey write-back function for a private Base Pod."""

    def _remember(raw_text: str) -> str:
        cleaned = raw_text.strip()
        if not cleaned:
            return "No text captured to remember."
        record = remember(
            cleaned,
            profile=base_pod,
            source="os-hotkey",
            profiles_root=pods_root,
        )
        return f"Remembered in {base_pod}: {record.id}"

    return _remember


@dataclass(frozen=True)
class HotkeyConfig:
    hotkey: str = "<alt>+<enter>"
    remember_hotkey: str = "<ctrl>+<shift>+<enter>"
    cut_wait_s: float = 0.18
    paste_wait_s: float = 0.12
    clipboard_timeout_s: float = 1.25
    submit_after_paste: bool = False
    restore_clipboard_after_s: float | None = None


class MemoryPodHotkeyLoop:
    """Global hotkey listener that expands selected input using the clipboard."""

    def __init__(
        self,
        augment_fn: Callable[[str], str] = augment,
        remember_fn: Callable[[str], str] | None = None,
        config: HotkeyConfig | None = None,
    ) -> None:
        self.augment = augment_fn
        self.remember = remember_fn
        self.config = config or HotkeyConfig()
        self.controller = keyboard.Controller()
        self._lock = threading.Lock()

    def start(self) -> None:
        self._warn_for_macos_permissions()
        hotkeys = {self.config.hotkey: self._on_augment_hotkey}
        if self.remember is not None:
            if self.config.remember_hotkey == self.config.hotkey:
                LOGGER.warning(
                    "Remember hotkey matches augment hotkey; explicit remember is disabled."
                )
            else:
                hotkeys[self.config.remember_hotkey] = self._on_remember_hotkey

        LOGGER.info("Starting Memory Pod hotkey loop: %s", ", ".join(hotkeys))
        with keyboard.GlobalHotKeys(hotkeys) as listener:
            listener.join()

    def _on_augment_hotkey(self) -> None:
        self._start_worker(self._expand_active_input, "augmentation")

    def _on_remember_hotkey(self) -> None:
        self._start_worker(self._remember_active_input, "remember")

    def _start_worker(self, target: Callable[[], None], action: str) -> None:
        if not self._lock.acquire(blocking=False):
            LOGGER.warning("Ignoring %s hotkey while previous action is running.", action)
            return

        worker = threading.Thread(target=target, daemon=True)
        worker.start()

    def _expand_active_input(self) -> None:
        try:
            original_clipboard, raw_text = self._capture_focused_text(cut=True)

            if not raw_text:
                LOGGER.warning("No text was captured after Cmd+A/Cmd+X; restoring clipboard.")
                self._safe_copy(original_clipboard)
                return

            LOGGER.info("Captured %d characters for augmentation.", len(raw_text))
            augmented_text = self.augment(raw_text)
            if not augmented_text or not augmented_text.strip():
                LOGGER.error("Augment function returned empty text; restoring original input.")
                augmented_text = raw_text

            self._safe_copy(augmented_text)
            time.sleep(self.config.paste_wait_s)
            self._press_combo(keyboard.Key.cmd, "v")

            if self.config.submit_after_paste:
                time.sleep(self.config.paste_wait_s)
                self.controller.press(keyboard.Key.enter)
                self.controller.release(keyboard.Key.enter)

            if self.config.restore_clipboard_after_s is not None:
                threading.Timer(
                    self.config.restore_clipboard_after_s,
                    lambda: self._safe_copy(original_clipboard),
                ).start()

        except Exception:
            LOGGER.exception("Memory Pod expansion failed.")
        finally:
            self._lock.release()

    def _remember_active_input(self) -> None:
        try:
            if self.remember is None:
                LOGGER.warning("Remember hotkey pressed, but no remember function is configured.")
                return

            original_clipboard, raw_text = self._capture_focused_text(cut=False)
            self._safe_copy(original_clipboard)

            if not raw_text:
                LOGGER.warning("No text was captured after Cmd+A/Cmd+C; input was unchanged.")
                return

            LOGGER.info("Captured %d characters for explicit remember.", len(raw_text))
            status = self.remember(raw_text)
            LOGGER.info(status)
        except Exception:
            LOGGER.exception("Memory Pod remember hotkey failed.")
        finally:
            self._lock.release()

    def _capture_focused_text(self, *, cut: bool) -> tuple[str, str]:
        original_clipboard = self._safe_paste()

        self._press_combo(keyboard.Key.cmd, "a")
        time.sleep(self.config.paste_wait_s)
        self._press_combo(keyboard.Key.cmd, "x" if cut else "c")

        raw_text = self._wait_for_clipboard_change(
            previous_value=original_clipboard,
            timeout_s=self.config.clipboard_timeout_s,
        ).strip()
        return original_clipboard, raw_text

    def _press_combo(self, modifier: keyboard.Key, key: str) -> None:
        """Press a macOS command-key combo like Cmd+A, Cmd+X, or Cmd+V."""
        with self.controller.pressed(modifier):
            self.controller.press(key)
            self.controller.release(key)

    def _wait_for_clipboard_change(self, previous_value: str, timeout_s: float) -> str:
        deadline = time.monotonic() + timeout_s
        latest = self._safe_paste()

        while time.monotonic() < deadline:
            latest = self._safe_paste()
            if latest != previous_value:
                return latest
            time.sleep(0.04)

        return latest

    @staticmethod
    def _safe_paste() -> str:
        try:
            value = pyperclip.paste()
            return value if isinstance(value, str) else ""
        except pyperclip.PyperclipException:
            LOGGER.exception("Could not read from clipboard.")
            return ""

    @staticmethod
    def _safe_copy(text: str) -> None:
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException:
            LOGGER.exception("Could not write to clipboard.")
            raise

    @staticmethod
    def _warn_for_macos_permissions() -> None:
        if platform.system() != "Darwin":
            LOGGER.warning("This hotkey loop is optimized for macOS; current OS may differ.")
            return

        LOGGER.info(
            "macOS requires Accessibility permission for the terminal/Python app running "
            "this daemon. If hotkeys or key presses fail, enable it in System Settings."
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="memory-pod-os-loop",
        description=(
            "Tier 2 in-place injection. A global hotkey grabs the focused input box "
            "(Cmd+A/Cmd+X), furnishes it with your Pod context, and pastes it back. "
            "It NEVER auto-submits — you review and press Enter yourself."
        ),
    )
    parser.add_argument(
        "--base-pod", default=DEFAULT_PROFILE, help="Private Base Pod to furnish from."
    )
    parser.add_argument(
        "--shared-pod", default=None, help="Optional read-only Shared Pod to dock."
    )
    parser.add_argument(
        "--hotkey", default=HotkeyConfig.hotkey, help="Global hotkey, e.g. '<alt>+<enter>'."
    )
    parser.add_argument(
        "--remember-hotkey",
        default=HotkeyConfig.remember_hotkey,
        help="Explicit remember hotkey, e.g. '<ctrl>+<shift>+<enter>'.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    docked = args.base_pod + (f" + {args.shared_pod}" if args.shared_pod else "")
    LOGGER.info("Docked for injection: %s", docked)
    LOGGER.warning(
        "SAFETY: use on ONE target site (ChatGPT OR Claude web). This pastes the "
        "furnished prompt in place and does NOT submit — review it, then press Enter."
    )
    LOGGER.info(
        "Learning is explicit: %s copies the focused input into your private Base Pod "
        "without cutting, pasting, or submitting.",
        args.remember_hotkey,
    )

    augment_fn = build_augment_fn(base_pod=args.base_pod, shared_pod=args.shared_pod)
    remember_fn = build_remember_fn(base_pod=args.base_pod)
    # submit_after_paste stays False: the constitution forbids automatic submission.
    config = HotkeyConfig(hotkey=args.hotkey, remember_hotkey=args.remember_hotkey)
    MemoryPodHotkeyLoop(
        augment_fn=augment_fn,
        remember_fn=remember_fn,
        config=config,
    ).start()


if __name__ == "__main__":
    main()
