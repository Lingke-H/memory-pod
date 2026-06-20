"""OS-level hotkey loop for Memory Pod.

This module intentionally knows almost nothing about the memory engine. It owns
only the global hotkey, clipboard handoff, and keyboard macro. The memory layer
must stay behind the augment_memory() function until the real augment() contract
is wired in.
"""

from __future__ import annotations

import logging
import platform
import threading
import time
from dataclasses import dataclass
from typing import Callable

import pyperclip
from pynput import keyboard

LOGGER = logging.getLogger("memory_pod.os_loop")


def augment_memory(text: str) -> str:
    """Temporary stand-in for memory_pod.augment.augment(raw_prompt)."""
    return (
        "[Hidden Context]\n"
        "- Demo memory: the user prefers concise, context-aware answers.\n\n"
        "[User Query]\n"
        f"{text}"
    )


@dataclass(frozen=True)
class HotkeyConfig:
    hotkey: str = "<alt>+<enter>"
    cut_wait_s: float = 0.18
    paste_wait_s: float = 0.12
    clipboard_timeout_s: float = 1.25
    submit_after_paste: bool = True
    restore_clipboard_after_s: float | None = None


class MemoryPodHotkeyLoop:
    """Global hotkey listener that expands selected input using the clipboard."""

    def __init__(
        self,
        augment: Callable[[str], str] = augment_memory,
        config: HotkeyConfig | None = None,
    ) -> None:
        self.augment = augment
        self.config = config or HotkeyConfig()
        self.controller = keyboard.Controller()
        self._lock = threading.Lock()

    def start(self) -> None:
        self._warn_for_macos_permissions()
        LOGGER.info("Starting Memory Pod hotkey loop: %s", self.config.hotkey)
        with keyboard.GlobalHotKeys({self.config.hotkey: self._on_hotkey}) as listener:
            listener.join()

    def _on_hotkey(self) -> None:
        if not self._lock.acquire(blocking=False):
            LOGGER.warning("Ignoring hotkey press while previous expansion is running.")
            return

        worker = threading.Thread(target=self._expand_active_input, daemon=True)
        worker.start()

    def _expand_active_input(self) -> None:
        try:
            original_clipboard = self._safe_paste()

            self._press_combo(keyboard.Key.cmd, "a")
            time.sleep(self.config.paste_wait_s)
            self._press_combo(keyboard.Key.cmd, "x")

            raw_text = self._wait_for_clipboard_change(
                previous_value=original_clipboard,
                timeout_s=self.config.clipboard_timeout_s,
            ).strip()

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    MemoryPodHotkeyLoop().start()


if __name__ == "__main__":
    main()
