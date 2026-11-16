#!/usr/bin/env python3
"""Tk GUI for configuring and monitoring the local computer-use agent."""

from __future__ import annotations

import json
import queue
import signal
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
AGENT_SCRIPT = ROOT / "computer_use_agent.py"
PREFERENCES = ROOT / ".computer_use_gui.json"

DEFAULTS: dict[str, Any] = {
    "mode": "Web search",
    "request": "",
    "vision_model": "moondream:latest",
    "planner_model": "llama3.2:latest",
    "ollama_url": "http://127.0.0.1:11434",
    "max_steps": "20",
    "timeout": "180",
    "countdown": "5",
    "output": "artifacts/browser_output.txt",
    "artifact_dir": "artifacts/screenshots",
    "launch_chrome": True,
    "create_notes": True,
    "dry_run": False,
    "start_url": "",
    "max_pages": "4",
    "include_images": False,
}


def build_command(
    settings: dict[str, Any],
    *,
    python: str = sys.executable,
    script: Path = AGENT_SCRIPT,
) -> list[str]:
    request = str(settings.get("request", "")).strip()
    if not request:
        raise ValueError("Enter a search query or browser task.")
    try:
        max_steps = int(settings.get("max_steps", 20))
        timeout = int(settings.get("timeout", 180))
        countdown = int(settings.get("countdown", 5))
        max_pages = int(settings.get("max_pages", 4))
    except (TypeError, ValueError) as exc:
        raise ValueError("Steps, timeout, and countdown must be whole numbers.") from exc
    if max_steps < 1 or timeout < 1 or countdown < 0:
        raise ValueError("Steps and timeout must be positive; countdown cannot be negative.")
    if not 1 <= max_pages <= 12:
        raise ValueError("Source articles must be between 1 and 12.")

    command = [python, "-u", str(script)]
    if settings.get("mode") == "Custom browser task":
        command.extend(["--task", request])
    else:
        command.append(request)
    command.extend(
        [
            "--vision-model",
            str(settings.get("vision_model") or DEFAULTS["vision_model"]),
            "--planner-model",
            str(settings.get("planner_model") or DEFAULTS["planner_model"]),
            "--ollama-url",
            str(settings.get("ollama_url") or DEFAULTS["ollama_url"]),
            "--max-steps",
            str(max_steps),
            "--timeout",
            str(timeout),
            "--countdown",
            str(countdown),
            "--output",
            str(settings.get("output") or DEFAULTS["output"]),
            "--artifact-dir",
            str(settings.get("artifact_dir") or DEFAULTS["artifact_dir"]),
        ]
    )
    if not settings.get("launch_chrome", True):
        command.append("--no-launch")
    if not settings.get("create_notes", True):
        command.append("--no-notes")
    if settings.get("dry_run", False):
        command.append("--dry-run")
    command.extend(["--engine", "browser", "--max-pages", str(max_pages)])
    if settings.get("start_url", "").strip():
        command.extend(["--start-url", settings["start_url"].strip()])
    if settings.get("include_images", False):
        command.append("--include-images")
    return command


class AgentGUI:
    def __init__(self) -> None:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk

        self.tk = tk
        self.ttk = ttk
        self.filedialog = filedialog
        self.messagebox = messagebox
        self.root = tk.Tk()
        self.root.title("Local Computer-Use Agent")
        self.root.geometry("900x760")
        self.root.minsize(760, 620)
        self.process: subprocess.Popen[str] | None = None
        self.output_queue: queue.Queue[str | None] = queue.Queue()
        self.stopped_by_user = False
        self.last_status_text = ""
        self.vars: dict[str, Any] = {}
        self._build()
        self._load_preferences()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(100, self._poll)

    def _build(self) -> None:
        tk, ttk = self.tk, self.ttk
        outer = ttk.Frame(self.root, padding=14)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(1, weight=1)

        ttk.Label(outer, text="Local Computer-Use Agent", font=("Helvetica", 19, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )

        self.vars["mode"] = tk.StringVar(value=DEFAULTS["mode"])
        ttk.Label(outer, text="Task type").grid(row=1, column=0, sticky="w", padx=(0, 10))
        mode = ttk.Combobox(
            outer,
            textvariable=self.vars["mode"],
            values=("Web search", "Custom browser task"),
            state="readonly",
            width=26,
        )
        mode.grid(row=1, column=1, sticky="ew")

        ttk.Label(outer, text="Request").grid(row=2, column=0, sticky="nw", pady=(10, 0))
        self.request_box = tk.Text(outer, height=4, wrap="word")
        self.request_box.grid(row=2, column=1, columnspan=2, sticky="nsew", pady=(10, 0))
        outer.rowconfigure(2, weight=0)

        examples = (
            'Search example: "latest local AI news"   •   Custom task example: '
            '"go to LinkedIn and search for new job roles"'
        )
        ttk.Label(outer, text=examples, foreground="#555").grid(
            row=3, column=1, columnspan=2, sticky="w", pady=(4, 12)
        )

        settings_frame = ttk.LabelFrame(outer, text="Models and run settings", padding=10)
        settings_frame.grid(row=4, column=0, columnspan=3, sticky="ew")
        for column in (1, 3):
            settings_frame.columnconfigure(column, weight=1)

        fields = [
            ("vision_model", "Vision model", 0, 0),
            ("planner_model", "Planner model", 0, 2),
            ("ollama_url", "Ollama URL", 1, 0),
            ("max_steps", "Maximum steps", 1, 2),
            ("timeout", "Model timeout (s)", 2, 0),
            ("countdown", "Start countdown (s)", 2, 2),
            ("start_url", "Website (optional)", 3, 0),
            ("max_pages", "Source articles", 3, 2),
        ]
        for key, label, row, column in fields:
            self.vars[key] = tk.StringVar(value=str(DEFAULTS[key]))
            ttk.Label(settings_frame, text=label).grid(
                row=row, column=column, sticky="w", padx=(0, 8), pady=4
            )
            ttk.Entry(settings_frame, textvariable=self.vars[key]).grid(
                row=row, column=column + 1, sticky="ew", padx=(0, 14), pady=4
            )

        files_frame = ttk.LabelFrame(outer, text="Output", padding=10)
        files_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(12, 0))
        files_frame.columnconfigure(1, weight=1)
        self.vars["output"] = tk.StringVar(value=DEFAULTS["output"])
        self.vars["artifact_dir"] = tk.StringVar(value=DEFAULTS["artifact_dir"])
        ttk.Label(files_frame, text="Backup text file").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ttk.Entry(files_frame, textvariable=self.vars["output"]).grid(row=0, column=1, sticky="ew")
        ttk.Button(files_frame, text="Choose…", command=self._choose_output).grid(row=0, column=2, padx=(8, 0))
        ttk.Label(files_frame, text="Screenshot folder").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))
        ttk.Entry(files_frame, textvariable=self.vars["artifact_dir"]).grid(row=1, column=1, sticky="ew", pady=(8, 0))
        ttk.Button(files_frame, text="Choose…", command=self._choose_artifacts).grid(row=1, column=2, padx=(8, 0), pady=(8, 0))

        options = ttk.Frame(outer)
        options.grid(row=6, column=0, columnspan=3, sticky="w", pady=10)
        for key, label, value in (
            ("include_images", "Attach page images", False),
            ("create_notes", "Create and verify Apple Notes draft", True),
            ("dry_run", "Dry run (no mouse or keyboard input)", False),
        ):
            self.vars[key] = tk.BooleanVar(value=value)
            ttk.Checkbutton(options, text=label, variable=self.vars[key]).pack(side="left", padx=(0, 18))

        controls = ttk.Frame(outer)
        controls.grid(row=7, column=0, columnspan=3, sticky="ew")
        self.run_button = ttk.Button(controls, text="Run task", command=self._start)
        self.run_button.pack(side="left")
        self.stop_button = ttk.Button(controls, text="Stop", command=self._stop, state="disabled")
        self.stop_button.pack(side="left", padx=8)
        ttk.Button(controls, text="Open Notes", command=lambda: subprocess.Popen(["open", "-a", "Notes"])).pack(side="left")
        ttk.Button(controls, text="Open backup", command=self._open_backup).pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(outer, textvariable=self.status_var, font=("Helvetica", 12, "bold")).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(12, 5)
        )
        self.log = tk.Text(outer, height=16, wrap="word", state="disabled")
        self.log.grid(row=9, column=0, columnspan=3, sticky="nsew")
        outer.rowconfigure(9, weight=1)

    def _settings(self) -> dict[str, Any]:
        settings = {key: variable.get() for key, variable in self.vars.items()}
        settings["request"] = self.request_box.get("1.0", "end").strip()
        return settings

    def _load_preferences(self) -> None:
        if not PREFERENCES.exists():
            return
        try:
            saved = json.loads(PREFERENCES.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for key, value in saved.items():
            if key == "request":
                self.request_box.delete("1.0", "end")
                self.request_box.insert("1.0", str(value))
            elif key in self.vars:
                self.vars[key].set(value)

    def _save_preferences(self, settings: dict[str, Any]) -> None:
        PREFERENCES.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")

    def _choose_output(self) -> None:
        path = self.filedialog.asksaveasfilename(
            title="Choose backup text file", defaultextension=".txt", filetypes=[("Text", "*.txt")]
        )
        if path:
            self.vars["output"].set(path)

    def _choose_artifacts(self) -> None:
        path = self.filedialog.askdirectory(title="Choose screenshot folder")
        if path:
            self.vars["artifact_dir"].set(path)

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _start(self) -> None:
        if self.process is not None:
            return
        settings = self._settings()
        try:
            command = build_command(settings)
            self._save_preferences(settings)
        except (ValueError, OSError) as exc:
            self.messagebox.showerror("Cannot start", str(exc))
            return
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self._append_log("Starting:\n" + " ".join(command) + "\n\n")
        self.stopped_by_user = False
        self.last_status_text = ""
        self.active_dry_run = bool(settings.get("dry_run"))
        try:
            self.process = subprocess.Popen(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except OSError as exc:
            self.process = None
            self.messagebox.showerror("Could not start", str(exc))
            return
        self.status_var.set("Running…")
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._read_output, daemon=True).start()

    def _read_output(self) -> None:
        assert self.process is not None and self.process.stdout is not None
        for line in self.process.stdout:
            self.output_queue.put(line)
        self.process.wait()
        self.output_queue.put(None)

    def _status_path(self) -> Path:
        artifact_dir = Path(str(self.vars["artifact_dir"].get())).expanduser()
        if not artifact_dir.is_absolute():
            artifact_dir = ROOT / artifact_dir
        return artifact_dir.resolve().parent / "run_status.json"

    def _poll(self) -> None:
        while True:
            try:
                item = self.output_queue.get_nowait()
            except queue.Empty:
                break
            if item is None:
                code = self.process.returncode if self.process else 1
                if self.stopped_by_user:
                    self.status_var.set("Stopped by user")
                elif code == 0 and self.active_dry_run:
                    self.status_var.set("Dry run finished — no research or note created")
                elif code == 0:
                    self.status_var.set("Complete — Notes/output verified")
                else:
                    self.status_var.set(f"Failed (exit code {code})")
                self.process = None
                self.run_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
            else:
                self._append_log(item)

        if self.process is not None:
            try:
                status = json.loads(self._status_path().read_text(encoding="utf-8"))
                display = f"{status.get('state', 'running').title()}: {status.get('message', '')}"
                if display != self.last_status_text:
                    self.status_var.set(display)
                    self.last_status_text = display
            except (OSError, json.JSONDecodeError):
                pass
        self.root.after(150, self._poll)

    def _stop(self) -> None:
        if self.process is None:
            return
        self.stopped_by_user = True
        self.process.send_signal(signal.SIGINT)
        self.status_var.set("Stopping…")

    def _open_backup(self) -> None:
        path = Path(str(self.vars["output"].get())).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            self.messagebox.showinfo("Backup", "No backup file has been created yet.")
            return
        subprocess.Popen(["open", str(path)])

    def _on_close(self) -> None:
        if self.process is not None and not self.messagebox.askyesno(
            "Task is running", "Stop the current task and close the window?"
        ):
            return
        if self.process is not None:
            self.process.send_signal(signal.SIGINT)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    try:
        AgentGUI().run()
        return 0
    except Exception as exc:
        print(f"Could not start GUI: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
