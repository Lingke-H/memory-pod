"""Tier 1 hotkey popup.

This safe interaction layer summons Memory Pod's own small input window instead
of hijacking another app's input box. It only calls augment(); it does not know
anything about the memory store or retrieval internals.
"""

from __future__ import annotations

import logging
import platform
import threading
import tkinter as tk
from tkinter import ttk

import pyperclip
from pynput import keyboard

from memory_pod.augment import augment

LOGGER = logging.getLogger("memory_pod.hotkey_popup")


class HotkeyPopup:
    def __init__(self, hotkey: str = "<alt>+<enter>") -> None:
        self.hotkey = hotkey
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
        root.title("Memory Pod")
        root.geometry("720x420")
        root.attributes("-topmost", True)

        prompt = tk.Text(root, height=7, wrap="word")
        prompt.pack(fill="x", padx=12, pady=(12, 6))

        output = tk.Text(root, height=12, wrap="word")
        output.pack(fill="both", expand=True, padx=12, pady=6)

        def furnish() -> None:
            raw = prompt.get("1.0", "end").strip()
            if not raw:
                return
            output.delete("1.0", "end")
            output.insert("1.0", augment(raw))

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

