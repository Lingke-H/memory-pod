"""Tier 1 hotkey popup with a local Base + Shared Pod Dock."""

from __future__ import annotations

import hashlib
import logging
import platform
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pyperclip
from pynput import keyboard

from memory_pod.active_dock import write_active_dock
from memory_pod.augment import augment_for_stack, furnish_selected
from memory_pod.config import DEFAULT_PROFILE, PROFILES_DIR
from memory_pod.llm import ollama_available
from memory_pod.onboarding import (
    ABOUT_YOU_QUESTIONS,
    complete_about_you,
    is_onboarded,
    mark_onboarded,
    seed_experts,
)
from memory_pod.pods import (
    PodManifest,
    PodStack,
    export_pod,
    import_pod,
    inspect_pod,
    list_pods,
    pod_is_private_writable,
)
from memory_pod.remember import remember
from memory_pod.rewriter import RewriteResult, polish_locally

LOGGER = logging.getLogger("memory_pod.hotkey_popup")
NO_SHARED_POD = "(None)"

# A stable little "face" per Pod so the Dock reads as people/playbooks, not ids.
_POD_FACES = ("🧑‍💻", "⚙️", "📦", "⚖️", "📣", "🧠", "📚", "🎯", "🛠️", "🔬", "✍️", "🚀")


def pod_face(pod_id: str) -> str:
    """Deterministic emoji for a Pod id (same id -> same face, no stored state)."""
    if not pod_id:
        return "📦"
    digest = hashlib.md5(pod_id.encode("utf-8")).digest()
    return _POD_FACES[digest[0] % len(_POD_FACES)]


def format_value_summary(memories, stack: PodStack) -> str:
    """One-line 'why this prompt is better' summary of what got used."""
    base_n = sum(1 for m in memories if m.pod_id == stack.base_pod)
    if stack.shared_pod:
        shared_n = sum(1 for m in memories if m.pod_id == stack.shared_pod)
        return (
            f"💡 Built from {base_n} of your memories "
            f"+ {shared_n} shared playbook item(s)."
        )
    return f"💡 Built from {base_n} of your memories."


def format_polish_status(result: RewriteResult) -> str:
    if result.used_local_ai:
        return f"{result.note} Review before sending."
    return result.note


def available_pod_choices(
    pods: list[PodManifest],
    current_base: str,
) -> tuple[list[str], list[str]]:
    by_id = {pod.id: pod for pod in pods}
    base = [
        pod.id
        for pod in pods
        if pod.kind == "private" and not pod.read_only
    ]
    if current_base and current_base not in base and current_base not in by_id:
        base.insert(0, current_base)
    shared = [pod.id for pod in pods if pod.kind == "shared"]
    return base, [NO_SHARED_POD, *shared]


class HotkeyPopup:
    def __init__(
        self,
        hotkey: str = "<alt>+<enter>",
        profile: str = DEFAULT_PROFILE,
        pods_root: Path = PROFILES_DIR,
    ) -> None:
        self.hotkey = hotkey
        self.profile = profile
        self.pods_root = pods_root
        self.root: tk.Tk | None = None
        self._prompt: tk.Text | None = None
        self._output: tk.Text | None = None
        self._memory_rows: ttk.Frame | None = None
        self._base_selector: ttk.Combobox | None = None
        self._shared_selector: ttk.Combobox | None = None
        self._base_var: tk.StringVar | None = None
        self._shared_var: tk.StringVar | None = None
        self._status: tk.StringVar | None = None
        self._value: tk.StringVar | None = None
        self._memory_vars: list[tuple[tk.BooleanVar, object]] = []
        self._last_raw = ""
        self._last_stack: PodStack | None = None
        self._wizard_open = False

    def start(self) -> None:
        self._warn_for_macos_permissions()
        self.root = tk.Tk()
        self._build_ui(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self._hide)
        self.root.withdraw()

        listener = keyboard.GlobalHotKeys({self.hotkey: self._on_hotkey})
        listener.start()
        LOGGER.info("Listening for %s — press it to summon the Pod Dock.", self.hotkey)
        try:
            self.root.mainloop()
        finally:
            listener.stop()

    def _on_hotkey(self) -> None:
        if self.root is not None:
            self.root.after(0, self._show)

    def _show(self) -> None:
        assert self.root is not None
        self._refresh_pod_choices()
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        if self._prompt is not None:
            self._prompt.focus_force()
        self._maybe_onboard()

    def _hide(self) -> None:
        if self.root is not None:
            self.root.withdraw()

    # ----- First-run onboarding wizard -------------------------------------

    def _maybe_onboard(self) -> None:
        if self._wizard_open or is_onboarded(self.pods_root.parent):
            return
        self._open_onboarding_wizard()

    def _open_onboarding_wizard(self) -> None:
        assert self.root is not None
        self._wizard_open = True
        dialog = tk.Toplevel(self.root)
        dialog.title("Welcome to Memory Pod")
        dialog.geometry("580x600")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Welcome to Memory Pod", font=("", 16, "bold")).pack(
            anchor="w", padx=16, pady=(16, 2)
        )
        ttk.Label(
            dialog,
            text="Furnish your prompts with your memory + a shared playbook.\n"
            "Everything stays on your computer.",
            justify="left",
        ).pack(anchor="w", padx=16)

        ai = "found ✓" if ollama_available() else "not found (optional — install Ollama for AI polish)"
        ttk.Label(dialog, text=f"Local AI: {ai}").pack(anchor="w", padx=16, pady=(10, 0))

        playbooks_var = tk.StringVar(value="Loading starter playbooks…")
        ttk.Label(dialog, textvariable=playbooks_var).pack(anchor="w", padx=16, pady=(4, 8))

        ttk.Label(
            dialog, text="Tell me about you (optional — skip any):", font=("", 12, "bold")
        ).pack(anchor="w", padx=16, pady=(8, 4))
        entries: dict[str, tk.StringVar] = {}
        for key, question in ABOUT_YOU_QUESTIONS:
            ttk.Label(dialog, text=question).pack(anchor="w", padx=16)
            var = tk.StringVar()
            ttk.Entry(dialog, textvariable=var, width=56).pack(anchor="w", padx=16, pady=(0, 6))
            entries[key] = var

        status = tk.StringVar(value="")
        ttk.Label(dialog, textvariable=status, anchor="w").pack(fill="x", padx=16, pady=(4, 0))

        buttons = ttk.Frame(dialog)
        buttons.pack(fill="x", padx=16, pady=12)
        finish_btn = ttk.Button(buttons, text="Finish")
        finish_btn.pack(side="right")
        ttk.Button(
            buttons,
            text="Skip",
            command=lambda: self._finish_onboarding(dialog, {}, status, finish_btn),
        ).pack(side="right", padx=8)
        finish_btn.configure(
            command=lambda: self._finish_onboarding(
                dialog, {key: var.get() for key, var in entries.items()}, status, finish_btn
            )
        )

        # Seed the starter playbooks in the background so the window opens instantly.
        def seed_worker() -> None:
            try:
                ids = seed_experts(pods_root=self.pods_root)
                msg = "Playbooks ready: " + ", ".join(
                    i.replace("-", " ").title() for i in ids
                ) + " ✓"
            except Exception as exc:  # noqa: BLE001 - surface any seed failure in the UI
                msg = f"Playbooks: could not load ({exc})"
            if self.root is not None:
                self.root.after(0, lambda: playbooks_var.set(msg))

        threading.Thread(target=seed_worker, daemon=True).start()

    def _finish_onboarding(self, dialog, answers, status, finish_btn) -> None:
        finish_btn.configure(state="disabled")
        status.set("Setting up…")

        def worker() -> None:
            base_pod = None
            try:
                if answers.get("name", "").strip():
                    base_pod = complete_about_you(
                        answers.get("name", ""),
                        answers.get("role", ""),
                        answers.get("working_on", ""),
                        answers.get("style", ""),
                        pods_root=self.pods_root,
                    )
                mark_onboarded(self.pods_root.parent)
            except Exception as exc:  # noqa: BLE001 - surface setup failure in the UI
                if self.root is not None:
                    self.root.after(
                        0,
                        lambda: (status.set(f"Setup error: {exc}"), finish_btn.configure(state="normal")),
                    )
                return
            if self.root is not None:
                self.root.after(0, lambda: self._complete_onboarding(dialog, base_pod))

        threading.Thread(target=worker, daemon=True).start()

    def _complete_onboarding(self, dialog, base_pod) -> None:
        self._wizard_open = False
        if base_pod and self._base_var is not None:
            self._refresh_pod_choices()
            self._base_var.set(base_pod)
            self._set_dock_status()
            self._set_status(f"Welcome! Your Base Pod '{base_pod}' is ready.")
        try:
            dialog.grab_release()
        except tk.TclError:
            pass
        dialog.destroy()

    def _build_ui(self, root: tk.Tk) -> None:
        root.title("Memory Pod — Pod Dock")
        root.geometry("820x700")
        root.minsize(720, 620)

        dock = ttk.Frame(root)
        dock.pack(fill="x", padx=12, pady=(12, 8))
        ttk.Label(dock, text="Base Pod").grid(row=0, column=0, sticky="w")
        self._base_var = tk.StringVar(value=self.profile)
        base_selector = ttk.Combobox(
            dock,
            textvariable=self._base_var,
            state="readonly",
            width=24,
        )
        base_selector.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        base_selector.bind("<<ComboboxSelected>>", self._on_dock_change)
        base_selector.configure(postcommand=self._refresh_pod_choices)
        self._base_selector = base_selector

        ttk.Label(dock, text="Shared Pod").grid(row=0, column=1, sticky="w")
        self._shared_var = tk.StringVar(value=NO_SHARED_POD)
        shared_selector = ttk.Combobox(
            dock,
            textvariable=self._shared_var,
            state="readonly",
            width=24,
        )
        shared_selector.grid(row=1, column=1, sticky="ew", padx=(0, 8))
        shared_selector.bind("<<ComboboxSelected>>", self._on_dock_change)
        shared_selector.configure(postcommand=self._refresh_pod_choices)
        self._shared_selector = shared_selector

        ttk.Button(dock, text="Import Pod", command=self._choose_import).grid(
            row=1, column=2, padx=(0, 8)
        )
        ttk.Button(dock, text="Share Pod", command=self._share_pod).grid(row=1, column=3)
        ttk.Button(
            dock, text="Confirm → Hotkey", command=self._confirm_hotkey_pod
        ).grid(row=1, column=4, padx=(8, 0))
        dock.columnconfigure(0, weight=1)
        dock.columnconfigure(1, weight=1)

        ttk.Label(root, text="Prompt").pack(anchor="w", padx=12)
        self._prompt = tk.Text(root, height=5, wrap="word")
        self._prompt.pack(fill="x", padx=12, pady=(2, 8))

        ttk.Label(
            root, text="Furnished prompt  (copy this whole block → paste into ChatGPT / Claude)"
        ).pack(anchor="w", padx=12)
        self._output = tk.Text(root, height=11, wrap="word")
        self._output.pack(fill="both", expand=True, padx=12, pady=(2, 8))

        ttk.Label(root, text="Context selected for sharing").pack(anchor="w", padx=12)
        self._memory_rows = ttk.Frame(root)
        self._memory_rows.pack(fill="x", padx=12, pady=(2, 8))

        buttons = ttk.Frame(root)
        buttons.pack(fill="x", padx=12, pady=(2, 6))
        ttk.Button(buttons, text="Furnish", command=self._furnish).pack(side="left")
        ttk.Button(buttons, text="Polish Locally", command=self._polish_locally).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(buttons, text="Copy", command=self._copy_output).pack(
            side="left", padx=8
        )
        ttk.Button(buttons, text="Remember in Base", command=self._remember_input).pack(
            side="left"
        )
        ttk.Button(buttons, text="Close", command=self._hide).pack(side="right")

        self._value = tk.StringVar()
        ttk.Label(root, textvariable=self._value, anchor="w").pack(
            fill="x", padx=12, pady=(0, 2)
        )
        self._status = tk.StringVar()
        ttk.Label(root, textvariable=self._status, anchor="w").pack(
            fill="x", padx=12, pady=(0, 12)
        )
        self._refresh_pod_choices(base_selector, shared_selector)
        self._set_dock_status()

    def _refresh_pod_choices(self, base_selector=None, shared_selector=None) -> None:
        pods = list_pods(self.pods_root)
        assert self._base_var is not None and self._shared_var is not None
        current_base = self._base_var.get() or self.profile
        base_choices, shared_choices = available_pod_choices(pods, current_base)

        base_selector = base_selector or self._base_selector
        shared_selector = shared_selector or self._shared_selector
        if base_selector is not None:
            base_selector.configure(values=base_choices)
        if shared_selector is not None:
            shared_selector.configure(values=shared_choices)

        if self._base_var.get() not in base_choices and base_choices:
            self._base_var.set(base_choices[0])
        if self._shared_var.get() not in shared_choices:
            self._shared_var.set(NO_SHARED_POD)

    def _current_stack(self) -> PodStack:
        assert self._base_var is not None and self._shared_var is not None
        shared = self._shared_var.get()
        return PodStack(
            base_pod=self._base_var.get(),
            shared_pod=None if shared == NO_SHARED_POD else shared,
        )

    def _on_dock_change(self, _event=None) -> None:
        self._set_dock_status()

    def _confirm_hotkey_pod(self) -> None:
        """Point the running OS-loop hotkey at the currently selected pods.

        Writes the shared active-dock file the daemon re-reads each Option+Enter,
        so the global hotkey switches person without restarting the daemon.
        """
        stack = self._current_stack()
        write_active_dock(
            stack.base_pod, stack.shared_pod, home=self.pods_root.parent
        )
        label = f"{pod_face(stack.base_pod)} {stack.base_pod}"
        if stack.shared_pod:
            label += f" + {pod_face(stack.shared_pod)} {stack.shared_pod}"
        self._set_status(f"Option+Enter now uses {label} — no restart needed.")

    def _set_dock_status(self) -> None:
        if self._status is None:
            return
        stack = self._current_stack()
        label = f"{pod_face(stack.base_pod)} {stack.base_pod}"
        if stack.shared_pod:
            label += f" + {pod_face(stack.shared_pod)} {stack.shared_pod}"
        self._status.set(f"Docked: {label}")

    def _furnish(self) -> None:
        assert self._prompt is not None and self._output is not None
        raw = self._prompt.get("1.0", "end").strip()
        if not raw:
            self._set_status("Type a prompt, then click Furnish.")
            return

        stack = self._current_stack()
        result = augment_for_stack(raw, stack, pods_root=self.pods_root)
        self._last_raw = raw
        self._last_stack = stack
        self._set_output(result.furnished_prompt)
        self._render_memories(result.memories)
        self._set_value(result.memories, stack)
        if result.memories:
            self._set_status(
                f"Furnished with {len(result.memories)} context item(s). "
                "Click Copy, then paste into your AI."
            )
        else:
            self._set_status(
                "No context matched this prompt yet — Remember a fact or ingest a "
                "file into this Base Pod, then Furnish again. (The prompt below is "
                "still copy-ready.)"
            )

    def _render_memories(self, memories) -> None:
        assert self._memory_rows is not None
        for child in self._memory_rows.winfo_children():
            child.destroy()
        self._memory_vars = []
        if not memories:
            ttk.Label(self._memory_rows, text="No matching context retrieved.").pack(
                anchor="w"
            )
            return

        for result in memories:
            selected = tk.BooleanVar(value=True)
            snippet = " ".join(result.record.text.split())
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            label = f"{pod_face(result.pod_id)} [{result.pod_id}] {result.score:.3f}  {snippet}"
            ttk.Checkbutton(
                self._memory_rows,
                text=label,
                variable=selected,
                command=self._rebuild_selected,
            ).pack(anchor="w", fill="x")
            self._memory_vars.append((selected, result))

    def _rebuild_selected(self) -> None:
        if self._last_stack is None:
            return
        selected = [result for variable, result in self._memory_vars if variable.get()]
        furnished = furnish_selected(
            self._last_raw,
            selected,
            self._last_stack,
            pods_root=self.pods_root,
        )
        self._set_output(furnished)
        self._set_value(selected, self._last_stack)
        self._set_status(f"Using {len(selected)} approved context item(s).")

    def _copy_output(self) -> None:
        assert self._output is not None
        text = self._output.get("1.0", "end").strip()
        if not text:
            self._set_status("Nothing to copy yet — click Furnish first.")
            return
        pyperclip.copy(text)
        self._set_status("Copied. Review it once more before sending to any AI.")

    def _polish_locally(self) -> None:
        assert self._prompt is not None and self._output is not None
        raw = self._last_raw or self._prompt.get("1.0", "end").strip()
        furnished = self._output.get("1.0", "end").strip()
        if not furnished:
            self._set_status("Nothing to polish yet — click Furnish first.")
            return

        self._set_status("Polishing locally...")

        def worker() -> None:
            result = polish_locally(raw, furnished)
            if self.root is not None:
                self.root.after(0, lambda: self._apply_polish_result(result))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_polish_result(self, result: RewriteResult) -> None:
        self._set_output(result.text)
        self._set_status(format_polish_status(result))

    def _remember_input(self) -> None:
        assert self._prompt is not None
        text = self._prompt.get("1.0", "end").strip()
        if not text:
            self._set_status("Type a fact, then click Remember in Base.")
            return
        try:
            record = remember(
                text,
                profile=self._current_stack().base_pod,
                source="popup",
                profiles_root=self.pods_root,
            )
        except (PermissionError, ValueError) as exc:
            self._set_status(str(exc))
            return
        self._set_status(f"Remembered in Base: {' '.join(record.text.split())}")

    def _choose_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Preview a Memory Pod",
            filetypes=[("Memory Pod", "*.mpod"), ("All files", "*")],
        )
        if not path:
            return
        try:
            portable = inspect_pod(path)
        except (OSError, UnicodeError, ValueError) as exc:
            messagebox.showerror("Cannot open Pod", str(exc))
            return
        self._show_import_preview(portable)

    def _show_import_preview(self, portable) -> None:
        assert self.root is not None
        dialog = tk.Toplevel(self.root)
        dialog.title("Import Pod — Preview")
        dialog.geometry("680x480")
        dialog.transient(self.root)
        dialog.grab_set()

        pod = portable.manifest
        summary = (
            f"{pod.name}\n"
            f"ID: {pod.id}\n"
            f"Author: {pod.author or 'Unspecified'} (not verified)\n"
            f"Purpose: {pod.purpose or 'Unspecified'}\n"
            f"Version: {pod.version}\n"
            f"Records: {len(portable.records)}\n"
            "Imported Pods are read-only and re-embedded locally.\n\n"
        )
        preview = tk.Text(dialog, wrap="word")
        preview.pack(fill="both", expand=True, padx=12, pady=12)
        preview.insert("end", summary)
        for index, record in enumerate(portable.records, start=1):
            tags = ", ".join(record["tags"]) if record["tags"] else "none"
            preview.insert("end", f"{index}. [{record['type']}] {record['text']}\n\n")
            preview.insert("end", f"Tags: {tags}\n\n")
        preview.configure(state="disabled")

        buttons = ttk.Frame(dialog)
        buttons.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="right")

        def confirm_import() -> None:
            try:
                manifest = import_pod(portable.source_path, pods_root=self.pods_root)
            except FileExistsError as exc:
                if "local Pod" in str(exc):
                    messagebox.showerror("Import blocked", str(exc))
                    return
                if not messagebox.askyesno("Replace imported Pod?", f"{exc}\n\nReplace it?"):
                    return
                try:
                    manifest = import_pod(
                        portable.source_path,
                        replace=True,
                        pods_root=self.pods_root,
                    )
                except (FileExistsError, OSError, ValueError) as replace_exc:
                    messagebox.showerror("Import failed", str(replace_exc))
                    return
            except (OSError, ValueError) as exc:
                messagebox.showerror("Import failed", str(exc))
                return
            assert self._shared_var is not None
            self._refresh_pod_choices()
            self._shared_var.set(manifest.id)
            self._set_dock_status()
            self._set_status(f"Imported and docked read-only Pod: {manifest.name}")
            dialog.destroy()

        ttk.Button(buttons, text="Import and Dock", command=confirm_import).pack(
            side="right", padx=(0, 8)
        )

    def _share_pod(self) -> None:
        assert self._shared_var is not None
        pod_id = self._shared_var.get()
        if pod_id == NO_SHARED_POD:
            self._set_status("Dock a locally created Shared Pod before sharing it.")
            return
        path = filedialog.asksaveasfilename(
            title="Share a Memory Pod",
            defaultextension=".mpod",
            filetypes=[("Memory Pod", "*.mpod")],
            initialfile=f"{pod_id}.mpod",
        )
        if not path:
            return
        try:
            exported = export_pod(pod_id, path, self.pods_root)
        except (FileNotFoundError, PermissionError, ValueError) as exc:
            self._set_status(str(exc))
            return
        self._set_status(f"Exported inspectable Pod: {exported}")

    def _set_output(self, text: str) -> None:
        assert self._output is not None
        self._output.delete("1.0", "end")
        self._output.insert("1.0", text)

    def _set_value(self, memories, stack: PodStack) -> None:
        if self._value is not None:
            self._value.set(format_value_summary(memories, stack))

    def _set_status(self, text: str) -> None:
        if self._status is not None:
            self._status.set(text)

    @staticmethod
    def _warn_for_macos_permissions() -> None:
        if platform.system() == "Darwin":
            LOGGER.info(
                "macOS requires Accessibility permission for global hotkeys. "
                "Enable it for the terminal or Python app if the hotkey is ignored."
            )


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    HotkeyPopup().start()


if __name__ == "__main__":
    main()
