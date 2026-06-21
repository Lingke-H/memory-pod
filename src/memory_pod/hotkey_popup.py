"""Tier 1 hotkey popup.

This safe interaction layer summons Memory Pod's own small input window instead
of hijacking another app's input box. It only calls the public contract
(augment_for_profile and remember); it does not know anything about the memory
store or retrieval internals. The popup shows the retrieved memories and their
similarity scores so the personalization is visible during a demo, and a
"Remember" button writes a new memory back locally for the "it just learned"
moment.

macOS note: Tk/NSWindow must live on the main thread, so the window is built
once on the main thread and `root.mainloop()` runs there. The global hotkey
listener runs on its own thread and only *marshals* a "show window" request back
to the main thread via `root.after(...)`. Creating the window from the listener
thread crashes with "NSWindow should only be instantiated on the main thread!".
"""

from __future__ import annotations

import logging
import platform
import tkinter as tk
from tkinter import ttk

import pyperclip
from pynput import keyboard

from memory_pod.augment import augment_for_profile
from memory_pod.config import DEFAULT_PROFILE
from memory_pod.remember import remember

LOGGER = logging.getLogger("memory_pod.hotkey_popup")


class HotkeyPopup:
    def __init__(
        self, hotkey: str = "<alt>+<enter>", profile: str = DEFAULT_PROFILE
    ) -> None:
        self.hotkey = hotkey
        self.profile = profile
        self.root: tk.Tk | None = None
        self._prompt: tk.Text | None = None

    def start(self) -> None:
        self._warn_for_macos_permissions()

        # Build the window once, on the main thread, then hide it until summoned.
        self.root = tk.Tk()
        self._build_ui(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self._hide)
        self.root.withdraw()

        listener = keyboard.GlobalHotKeys({self.hotkey: self._on_hotkey})
        listener.start()
        LOGGER.info("Listening for %s — press it to summon the popup.", self.hotkey)
        try:
            self.root.mainloop()
        finally:
            listener.stop()

    def _on_hotkey(self) -> None:
        # Runs on the listener thread: hand the work back to the Tk main thread.
        if self.root is not None:
            self.root.after(0, self._show)

    def _show(self) -> None:
        assert self.root is not None
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        if self._prompt is not None:
            self._prompt.focus_force()

    def _hide(self) -> None:
        if self.root is not None:
            self.root.withdraw()

    def _build_ui(self, root: tk.Tk) -> None:
        root.title(f"Memory Pod ({self.profile})")
        root.geometry("720x560")

        prompt = tk.Text(root, height=6, wrap="word")
        prompt.pack(fill="x", padx=12, pady=(12, 6))
        self._prompt = prompt

        ttk.Label(root, text="Furnished prompt").pack(anchor="w", padx=12)
        output = tk.Text(root, height=10, wrap="word")
        output.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        ttk.Label(root, text="Retrieved memories (similarity scores)").pack(anchor="w", padx=12)
        memories = tk.Text(root, height=8, wrap="word")
        memories.pack(fill="both", expand=True, padx=12, pady=(0, 6))

        status = tk.StringVar(value=f"Profile: {self.profile}")

        def furnish() -> None:
            raw = prompt.get("1.0", "end").strip()
            if not raw:
                status.set("Type a prompt in the top box, then click Furnish.")
                return
            result = augment_for_profile(raw, profile=self.profile)

            output.delete("1.0", "end")
            output.insert("1.0", result.furnished_prompt)

            memories.delete("1.0", "end")
            if result.memories:
                for index, item in enumerate(result.memories, start=1):
                    snippet = " ".join(item.record.text.split())
                    memories.insert("end", f"{index}. score={item.score:.3f}  {snippet}\n")
                status.set(f"✓ Furnished — {len(result.memories)} memorie(s) retrieved. Click Copy to use it.")
            else:
                memories.insert("1.0", "(no memories retrieved)")
                status.set("✓ Furnished — no matching memories retrieved.")

        def copy_output() -> None:
            text = output.get("1.0", "end").strip()
            if not text:
                status.set("Nothing to copy yet — click Furnish first.")
                return
            pyperclip.copy(text)
            status.set("✓ Copied furnished prompt to clipboard.")

        def remember_input() -> None:
            text = prompt.get("1.0", "end").strip()
            if not text:
                status.set("Type a fact in the top box, then click Remember.")
                return
            record = remember(text, profile=self.profile, source="popup")
            snippet = " ".join(record.text.split())
            status.set(f"✓ Remembered for '{self.profile}': {snippet}")

        buttons = ttk.Frame(root)
        buttons.pack(fill="x", padx=12, pady=(6, 4))
        ttk.Button(buttons, text="Furnish", command=furnish).pack(side="left")
        ttk.Button(buttons, text="Copy", command=copy_output).pack(side="left", padx=8)
        ttk.Button(buttons, text="Remember", command=remember_input).pack(side="left")
        ttk.Button(buttons, text="Close", command=self._hide).pack(side="right")

        ttk.Label(root, textvariable=status, anchor="w").pack(
            fill="x", padx=12, pady=(0, 12)
        )

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
