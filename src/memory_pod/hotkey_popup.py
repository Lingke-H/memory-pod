"""Tier 1 hotkey popup.

This safe interaction layer summons Memory Pod's own small input window instead
of hijacking another app's input box. It only calls the public augment contract
(augment_for_profile); it does not know anything about the memory store or
retrieval internals. The popup also shows the retrieved memories and their
similarity scores so the personalization is visible during a demo.
"""

from __future__ import annotations

import logging
import platform
import threading
import tkinter as tk
from tkinter import ttk

import pyperclip
from pynput import keyboard

from memory_pod.augment import augment_for_profile
from memory_pod.config import DEFAULT_PROFILE

LOGGER = logging.getLogger("memory_pod.hotkey_popup")


class HotkeyPopup:
    def __init__(
        self, hotkey: str = "<alt>+<enter>", profile: str = DEFAULT_PROFILE
    ) -> None:
        self.hotkey = hotkey
        self.profile = profile
        self._visible = threading.Event()

    def start(self) -> None:
        self._warn_for_macos_permissions()
        with keyboard.GlobalHotKeys({self.hotkey: self._show_popup}) as listener:
            listener.join()

    def _show_popup(self) -> None:
        if self._visible.is_set():
            return
        self._visible.set()
        threading.Thread(target=self._run_window, daemon=True).start()

    def _run_window(self) -> None:
        root = tk.Tk()
        root.title(f"Memory Pod ({self.profile})")
        root.geometry("720x560")
        root.attributes("-topmost", True)

        prompt = tk.Text(root, height=6, wrap="word")
        prompt.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(root, text="Furnished prompt").pack(anchor="w", padx=12)
        output = tk.Text(root, height=10, wrap="word")
        output.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        ttk.Label(root, text="Retrieved memories (similarity scores)").pack(anchor="w", padx=12)
        memories = tk.Text(root, height=8, wrap="word")
        memories.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        def furnish() -> None:
            raw = prompt.get("1.0", "end").strip()
            if not raw:
                return
            result = augment_for_profile(raw, profile=self.profile)

            output.delete("1.0", "end")
            output.insert("1.0", result.furnished_prompt)

            memories.delete("1.0", "end")
            if result.memories:
                for index, item in enumerate(result.memories, start=1):
                    snippet = " ".join(item.record.text.split())
                    memories.insert("end", f"{index}. score={item.score:.3f}  {snippet}\n")
            else:
                memories.insert("1.0", "(no memories retrieved)")

        def copy_output() -> None:
            pyperclip.copy(output.get("1.0", "end").strip())

        buttons = ttk.Frame(root)
        buttons.pack(fill="x", padx=12, pady=(6, 12))
        ttk.Button(buttons, text="Furnish", command=furnish).pack(side="left")
        ttk.Button(buttons, text="Copy", command=copy_output).pack(side="left", padx=8)
        ttk.Button(buttons, text="Close", command=root.destroy).pack(side="right")

        def on_close() -> None:
            self._visible.clear()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)
        root.mainloop()
        self._visible.clear()

    @staticmethod
    def _warn_for_macos_permissions() -> None:
        if platform.system() == "Darwin":
            LOGGER.info(
                "macOS may require Accessibility permission for global hotkeys. "
                "Enable it for the terminal or Python app if the hotkey is ignored."
            )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    HotkeyPopup().start()


if __name__ == "__main__":
    main()

