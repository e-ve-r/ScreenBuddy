#!/usr/bin/env python3
"""A small, local computer-use agent powered by Ollama and PyAutoGUI.

The agent uses Moondream to describe screenshots and Llama 3.2 to choose a
single, validated GUI action at a time.  It can open Chrome, search the web,
capture the visible results, and save a text summary without a cloud API.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import platform
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
NOTES_CREATE_SCRIPT = r'''
on run argv
    set noteTitle to item 1 of argv
    set noteHTML to item 2 of argv
    set imageFiles to {}
    repeat with imageIndex from 3 to (count of argv)
        set end of imageFiles to (POSIX file (item imageIndex of argv)) as alias
    end repeat
    tell application "Notes"
        activate
        set targetAccount to default account
        set targetFolder to default folder of targetAccount
        set newNote to make new note at targetFolder with properties {body:noteHTML}
        show newNote
        set createdID to id of newNote
        set createdName to name of newNote
        set createdText to plaintext of newNote
        set createdLength to count characters of createdText
        set imageCount to 0
        repeat with imageFile in imageFiles
            set savedImage to make new attachment at newNote with data (contents of imageFile)
            if (id of savedImage) is not "" then set imageCount to imageCount + 1
        end repeat
    end tell
    return createdID & linefeed & createdName & linefeed & (imageCount as text) & linefeed & createdText
end run
'''.strip()
NOTIFICATION_SCRIPT = r'''
on run argv
    display notification (item 2 of argv) with title (item 1 of argv) sound name "Glass"
end run
'''.strip()
ALLOWED_ACTIONS = {
    "move_mouse",
    "click",
    "double_click",
    "type_text",
    "press",
    "hotkey",
    "scroll",
    "wait",
    "finish",
}
ALLOWED_KEYS = {"enter", "tab", "esc", "escape", "space", "home", "end", "pageup", "pagedown"}
ALLOWED_HOTKEYS = {
    ("command", "l"),
    ("ctrl", "l"),
    ("command", "a"),
    ("ctrl", "a"),
}


class AgentError(RuntimeError):
    pass


def normalize_action(value: dict[str, Any]) -> dict[str, Any]:
    """Handle a common small-model alias without weakening action validation."""
    result = {key: item for key, item in value.items() if item is not None}
    if "action" not in result and result.get("type") in ALLOWED_ACTIONS:
        result["action"] = result.pop("type")
    return result


def ollama_vision(
    base_url: str,
    model: str,
    prompt: str,
    image_path: Path,
    timeout: int = 180,
) -> str:
    """Run a vision prompt through Ollama's completion endpoint.

    Moondream's Ollama package is a completion/vision model and may return an
    empty assistant content value through /api/chat, so vision uses /api/generate.
    """
    encoded_image = base64.b64encode(image_path.read_bytes()).decode("ascii")
    # Moondream's prompt template is sensitive to the verb used here. Starting
    # literally with this phrase avoids immediate empty/EOS responses.
    prompts = [
        f"Describe the image. {prompt}",
        "Describe the image",
    ]
    for attempt, current_prompt in enumerate(prompts):
        payload = {
            "model": model,
            "prompt": current_prompt,
            "images": [encoded_image],
            "stream": False,
            "options": {"temperature": 0 if attempt == 0 else 0.1, "num_predict": 512},
        }
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.load(response)
        except urllib.error.URLError as exc:
            raise AgentError(
                f"Could not reach Ollama at {base_url}. Start it with `ollama serve`. ({exc})"
            ) from exc
        text = body.get("response") if isinstance(body, dict) else None
        if isinstance(text, str) and text.strip():
            return text.strip()

    # Moondream sometimes emits EOS immediately for blank/sparse screenshots.
    # That is a valid observation, not a reason to terminate the whole workflow.
    return ""


def ollama_tool_action(base_url: str, model: str, prompt: str, timeout: int = 180) -> dict[str, Any]:
    """Ask Ollama for one native function call and return its arguments."""
    tool = {
        "type": "function",
        "function": {
            "name": "computer_action",
            "description": "Perform exactly one safe mouse or keyboard action on the computer.",
            "parameters": {
                "type": "object",
                "required": ["action", "reason"],
                "properties": {
                    "action": {"type": "string", "enum": sorted(ALLOWED_ACTIONS)},
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "text": {"type": "string"},
                    "key": {"type": "string"},
                    "keys": {"type": "array", "items": {"type": "string"}},
                    "amount": {"type": "integer"},
                    "seconds": {"type": "number"},
                    "reason": {"type": "string"},
                },
            },
        },
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "tools": [tool],
        "stream": False,
        "options": {"temperature": 0},
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.load(response)
    except urllib.error.URLError as exc:
        raise AgentError(
            f"Could not reach Ollama at {base_url}. Start it with `ollama serve`. ({exc})"
        ) from exc

    message = body.get("message", {}) if isinstance(body, dict) else {}
    calls = message.get("tool_calls", []) if isinstance(message, dict) else []
    if calls:
        function = calls[0].get("function", {})
        if function.get("name") != "computer_action":
            raise AgentError(f"Planner called an unknown tool: {function.get('name')!r}")
        arguments = function.get("arguments", {})
        if isinstance(arguments, str):
            return normalize_action(extract_json(arguments))
        if isinstance(arguments, dict):
            return normalize_action(arguments)
        raise AgentError(f"Planner supplied invalid tool arguments: {arguments!r}")

    # Some older Ollama/model combinations emit the requested object as content.
    content = message.get("content", "") if isinstance(message, dict) else ""
    return normalize_action(extract_json(content))


def ollama_text(base_url: str, model: str, prompt: str, timeout: int = 180,
                json_mode: bool = False) -> str:
    """Generate plain text with a local Ollama chat model."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0 if json_mode else 0.2, "num_ctx": 8192},
    }
    if json_mode:
        payload["format"] = "json"
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.load(response)
    except urllib.error.URLError as exc:
        raise AgentError(f"Could not ask the drafting model for findings: {exc}") from exc
    text = body.get("message", {}).get("content") if isinstance(body, dict) else None
    if not isinstance(text, str) or not text.strip():
        raise AgentError("The drafting model returned no text")
    return text.strip()


def ollama_model_names(base_url: str, timeout: int = 10) -> set[str]:
    request = urllib.request.Request(f"{base_url.rstrip('/')}/api/tags", method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.load(response)
    except urllib.error.URLError as exc:
        raise AgentError(
            f"Could not reach Ollama at {base_url}. Start it with `ollama serve`. ({exc})"
        ) from exc
    models = body.get("models", []) if isinstance(body, dict) else []
    return {
        model["name"]
        for model in models
        if isinstance(model, dict) and isinstance(model.get("name"), str)
    }


def require_models(base_url: str, required: set[str], timeout: int) -> None:
    available = ollama_model_names(base_url, min(timeout, 10))
    missing = sorted(required - available)
    if missing:
        commands = "\n".join(f"  ollama pull {name}" for name in missing)
        raise AgentError(f"Missing required Ollama model(s). Install them with:\n{commands}")


def extract_json(text: str) -> dict[str, Any]:
    """Parse a model response even if it wrapped JSON in Markdown."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise AgentError(f"Planner did not return JSON: {text}")
        try:
            value = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise AgentError(f"Planner returned invalid JSON: {text}") from exc
    if not isinstance(value, dict):
        raise AgentError(f"Planner returned a non-object JSON value: {value!r}")
    return value


@dataclass
class ScreenState:
    width: int
    height: int
    screenshot_width: int
    screenshot_height: int
    screenshot_path: Path
    visual_description: str


class ComputerUseAgent:
    def __init__(self, args: argparse.Namespace) -> None:
        try:
            import pyautogui  # type: ignore
        except ImportError as exc:
            raise AgentError(
                "PyAutoGUI is not installed. Run `python3 -m pip install -r requirements.txt`."
            ) from exc

        self.pg = pyautogui
        self.args = args
        self.pg.FAILSAFE = True
        self.pg.PAUSE = args.action_pause
        self.artifact_dir = Path(args.artifact_dir).expanduser().resolve()
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.history: list[dict[str, Any]] = []
        self.allowed_text: str | None = None
        self.allow_task_fragments = False
        self.status_path = self.artifact_dir.parent / "run_status.json"

    def update_status(self, state: str, message: str, **details: Any) -> None:
        """Atomically publish machine-readable progress for the current run."""
        payload = {
            "state": state,
            "message": message,
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            **details,
        }
        temporary = self.status_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(self.status_path)

    @staticmethod
    def notify(title: str, message: str) -> None:
        """Send a best-effort macOS notification without hiding task failures."""
        if platform.system() != "Darwin":
            return
        try:
            result = subprocess.run(
                ["osascript", "-e", NOTIFICATION_SCRIPT, "--", title, message],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"Notification warning: {exc}", file=sys.stderr)
            return
        if result.returncode != 0:
            print(f"Notification warning: {result.stderr.strip()}", file=sys.stderr)

    def take_screenshot(self, step: int) -> ScreenState:
        path = self.artifact_dir / f"step-{step:02d}.png"
        image = self.pg.screenshot()
        image.save(path)
        width, height = self.pg.size()
        if width <= 0 or height <= 0:
            raise AgentError(
                "No usable display was detected. Run this from a logged-in desktop session "
                "and grant the terminal Accessibility and Screen Recording permissions."
            )
        prompt = f"""
Analyze this desktop screenshot for a computer-control agent. The logical
screen is {width}x{height}; the screenshot bitmap is {image.width}x{image.height}.
Describe the current app, visible text, page state, and interactive elements.
For each useful clickable target, estimate its CENTER in logical screen pixels
as (x, y), with origin at the top-left. Focus on Chrome controls, the address
bar, search fields, buttons, and signs that a web search has loaded. Be concise.
""".strip()
        description = ollama_vision(
            self.args.ollama_url,
            self.args.vision_model,
            prompt,
            path,
            timeout=self.args.timeout,
        )
        if not description:
            shortcut = "Command+L" if platform.system() == "Darwin" else "Ctrl+L"
            description = (
                "Moondream returned no text after two attempts; the screenshot is likely "
                "blank or visually sparse. Do not guess mouse coordinates. Chrome was just "
                f"launched, so use the safe address-bar shortcut {shortcut} and continue from "
                "the recent action history."
            )
        return ScreenState(width, height, image.width, image.height, path, description)

    def plan_action(self, goal: str, state: ScreenState, step: int) -> dict[str, Any]:
        recent = json.dumps(self.history[-6:], ensure_ascii=False)
        prompt = f"""
You are the action planner for a local desktop computer-use agent.

GOAL: {goal}
STEP: {step} of {self.args.max_steps}
OS: {platform.system()}
LOGICAL SCREEN SIZE: {state.width}x{state.height}
RECENT ACTIONS: {recent}

VISION MODEL'S SCREEN DESCRIPTION:
{state.visual_description}

Choose exactly ONE next action by calling the computer_action tool once. Use one argument schema:
{{"action":"move_mouse","x":int,"y":int,"reason":"..."}}
{{"action":"click","x":int,"y":int,"reason":"..."}}
{{"action":"double_click","x":int,"y":int,"reason":"..."}}
{{"action":"type_text","text":"...","reason":"..."}}
{{"action":"press","key":"enter|tab|esc|...","reason":"..."}}
{{"action":"hotkey","keys":["command","l"],"reason":"..."}}
{{"action":"scroll","amount":int,"reason":"..."}}
{{"action":"wait","seconds":number,"reason":"..."}}
{{"action":"finish","reason":"..."}}

Rules:
- Coordinates MUST be inside the logical screen and should be target centers.
- Use click only when the vision description gives a sufficiently clear target.
- Prefer keyboard shortcuts for stable controls (for example address bar).
- You may click ordinary navigation links and submit search boxes needed for the
  user's request. Never use terminal/shell, close apps, download files, submit
  account/contact/job-application/payment forms, log in, purchase anything, or
  interact with password/payment prompts.
- If the result page visibly contains the requested search results, finish.
- Never repeat the immediately previous action. After Command+L, type the exact
  query from GOAL. After typing it, press Enter. After Enter, wait for loading.
""".strip()
        return ollama_tool_action(
            self.args.ollama_url,
            self.args.planner_model,
            prompt,
            timeout=self.args.timeout,
        )

    def validate_action(self, action: dict[str, Any], state: ScreenState) -> None:
        name = action.get("action")
        if name not in ALLOWED_ACTIONS:
            raise AgentError(f"Planner chose unsupported action: {name!r}")
        if name in {"move_mouse", "click", "double_click"}:
            x, y = action.get("x"), action.get("y")
            if not isinstance(x, int) or not isinstance(y, int):
                raise AgentError(f"Mouse action requires integer coordinates: {action}")
            if not (0 <= x < state.width and 0 <= y < state.height):
                raise AgentError(f"Unsafe out-of-bounds coordinates: ({x}, {y})")
        if name == "type_text":
            text = action.get("text")
            if not isinstance(text, str):
                raise AgentError("type_text requires text")
            exact_match = self.allowed_text is None or text == self.allowed_text
            task_fragment = (
                self.allow_task_fragments
                and self.allowed_text is not None
                and len(text.strip()) >= 2
                and text.casefold() in self.allowed_text.casefold()
            )
            if not exact_match and not task_fragment:
                raise AgentError(
                    "Blocked model-generated text that was not supplied by the user request"
                )
        if name == "hotkey":
            keys = action.get("keys")
            if not isinstance(keys, list) or not keys or not all(isinstance(k, str) for k in keys):
                raise AgentError("hotkey requires a non-empty string list")
            normalized = tuple(k.lower() for k in keys)
            if normalized not in ALLOWED_HOTKEYS:
                raise AgentError(f"Blocked hotkey outside the safety allowlist: {keys}")
        if name == "press":
            key = action.get("key")
            if not isinstance(key, str) or key.lower() not in ALLOWED_KEYS:
                raise AgentError(f"Blocked key outside the safety allowlist: {key!r}")
        if name == "wait":
            seconds = action.get("seconds", 1)
            if not isinstance(seconds, (int, float)) or not 0 <= seconds <= 10:
                raise AgentError("wait must be between 0 and 10 seconds")

    def recover_repeated_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Keep the safe address-bar sequence moving despite small-model loops."""
        if self.history:
            last = self.history[-1]
            if last.get("action") == "hotkey" and tuple(last.get("keys", [])) in ALLOWED_HOTKEYS:
                if action.get("action") != "type_text" or action.get("text") != self.allowed_text:
                    return {
                        "action": "type_text",
                        "text": self.allowed_text or "",
                        "reason": "Recovery: address bar is focused; type the query now",
                    }
            if last.get("action") == "type_text" and not (
                action.get("action") == "press" and action.get("key") == "enter"
            ):
                return {
                    "action": "press",
                    "key": "enter",
                    "reason": "Recovery: query is typed; submit it now",
                }
            if (
                last.get("action") == "press"
                and last.get("key") == "enter"
                and action.get("action") in {"hotkey", "type_text", "press"}
            ):
                return {
                    "action": "wait",
                    "seconds": 2,
                    "reason": "Recovery: query was submitted; wait for loading",
                }

        current = {key: value for key, value in action.items() if key != "reason"}
        previous = (
            {key: value for key, value in self.history[-1].items() if key != "reason"}
            if self.history
            else None
        )
        if current != previous:
            return action

        name = action.get("action")
        if name == "hotkey" and tuple(action.get("keys", [])) in ALLOWED_HOTKEYS:
            return {
                "action": "type_text",
                "text": self.allowed_text or "",
                "reason": "Recovery: address bar is focused; type the query now",
            }
        if name == "type_text":
            return {
                "action": "press",
                "key": "enter",
                "reason": "Recovery: query is typed; submit it now",
            }
        if name == "press" and action.get("key") == "enter":
            return {
                "action": "wait",
                "seconds": 2,
                "reason": "Recovery: Enter was pressed; wait for loading",
            }
        return action

    def execute(self, action: dict[str, Any]) -> bool:
        name = action["action"]
        if self.args.dry_run:
            print(f"DRY RUN: {json.dumps(action, ensure_ascii=False)}")
            return name == "finish"
        if name == "move_mouse":
            self.pg.moveTo(action["x"], action["y"], duration=0.25)
        elif name == "click":
            self.pg.click(action["x"], action["y"])
        elif name == "double_click":
            self.pg.doubleClick(action["x"], action["y"], interval=0.12)
        elif name == "type_text":
            self.pg.write(action["text"], interval=self.args.key_interval)
        elif name == "press":
            self.pg.press(action["key"])
        elif name == "hotkey":
            self.pg.hotkey(*action["keys"])
        elif name == "scroll":
            self.pg.scroll(int(action.get("amount", 0)))
        elif name == "wait":
            time.sleep(float(action.get("seconds", 1)))
        return name == "finish"

    def launch_chrome(self) -> None:
        """Open Chrome reliably, then leave all browser input to PyAutoGUI."""
        if self.args.dry_run:
            print("DRY RUN: launch Chrome")
            return
        if platform.system() == "Darwin":
            try:
                subprocess.run(["open", "-a", "Google Chrome"], check=True)
            except (OSError, subprocess.CalledProcessError) as exc:
                raise AgentError(f"Could not launch Google Chrome: {exc}") from exc
            time.sleep(self.args.launch_wait)
            return
        elif platform.system() == "Windows":
            self.pg.press("win")
        else:
            self.pg.hotkey("ctrl", "alt", "t")
            time.sleep(1)
            self.pg.write("google-chrome", interval=0.05)
            self.pg.press("enter")
            time.sleep(self.args.launch_wait)
            return
        time.sleep(0.7)
        self.pg.write("Google Chrome", interval=0.08)
        self.pg.press("enter")
        time.sleep(self.args.launch_wait)

    def draft_in_notes(self, query: str, findings: str, custom_task: bool = False,
                       attachments: list[Path] | None = None) -> str:
        """Create and verify an Apple Notes note through its scripting API."""
        if self.args.dry_run:
            print("DRY RUN: create a new Apple Notes note with the drafted findings")
            return "dry-run"
        if platform.system() != "Darwin":
            raise AgentError("Apple Notes output is only available on macOS")
        prefix = "Task findings: " if custom_task else "Search findings: "
        title = prefix + " ".join(query.splitlines()).strip()
        escaped_title = html.escape(title)
        escaped_findings = html.escape(findings).replace("\n", "<br>")
        note_html = f"<h1>{escaped_title}</h1><div>{escaped_findings}</div>"
        try:
            result = subprocess.run(
                ["osascript", "-e", NOTES_CREATE_SCRIPT, "--", title, note_html,
                 *[str(p.resolve()) for p in (attachments or [])]],
                capture_output=True,
                text=True,
                check=True,
                timeout=60,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            detail = getattr(exc, "stderr", "") or str(exc)
            raise AgentError(
                "Could not create the Apple Notes note. If macOS asks whether Terminal may "
                f"control Notes, choose Allow. Details: {detail.strip()}"
            ) from exc

        parts = result.stdout.strip().splitlines()
        if len(parts) < 4:
            raise AgentError(f"Notes did not return creation verification: {result.stdout!r}")
        note_id, saved_title, saved_length_text = parts[0], parts[1], parts[2]
        try:
            attachment_count = int(saved_length_text)
        except ValueError as exc:
            raise AgentError(f"Notes returned an invalid content length: {saved_length_text!r}") from exc
        stored_text = " ".join("\n".join(parts[3:]).split())
        expected_text = " ".join(findings.split())
        if (not note_id or saved_title != title or expected_text not in stored_text
                or attachment_count != len(attachments or [])):
            raise AgentError(
                "Apple Notes created an incomplete note; verification failed "
                f"(title={saved_title!r}, attachments={attachment_count})"
            )
        return note_id

    def run_task(self, query: str, custom_task: bool = False) -> Path:
        goal = (
            query
            if custom_task
            else f'Open Chrome, search the web for "{query}", and stop when results are visible.'
        )
        self.allowed_text = query
        self.allow_task_fragments = custom_task
        task_mode = "custom" if custom_task else "search"
        self.update_status("running", "Launching Chrome", request=query, mode=task_mode)
        if not self.args.no_launch:
            self.launch_chrome()

        finished = False
        final_state: ScreenState | None = None
        for step in range(1, self.args.max_steps + 1):
            self.update_status(
                "running",
                f"Analyzing browser step {step} of {self.args.max_steps}",
                request=query,
                mode=task_mode,
                step=step,
                max_steps=self.args.max_steps,
            )
            state = self.take_screenshot(step)
            final_state = state
            print(f"\nStep {step} vision:\n{state.visual_description}")
            action = self.plan_action(goal, state, step)
            recovered_action = self.recover_repeated_action(action)
            if recovered_action != action:
                print(f"Step {step} recovery: repeated action replaced with safe next step")
                action = recovered_action
            self.validate_action(action, state)
            print(f"Step {step} action: {json.dumps(action, ensure_ascii=False)}")
            self.history.append(action)
            if self.execute(action):
                finished = True
                break

        submitted = any(
            item.get("action") == "press" and item.get("key") == "enter"
            for item in self.history
        )
        if not finished and not self.args.dry_run and not submitted:
            raise AgentError(f"Goal was not completed within {self.args.max_steps} steps")
        if not finished and submitted:
            print(
                f"Planner did not finish within {self.args.max_steps} steps; "
                "capturing the submitted search page anyway."
            )
        if final_state is None:
            raise AgentError("No screenshot was captured")

        if not self.args.dry_run:
            time.sleep(1)
            final_state = self.take_screenshot(self.args.max_steps + 1)

        self.update_status("running", "Drafting findings", request=query, mode=task_mode)
        extraction_prompt = f"""
Describe the image and read this browser screenshot. The user's request was:
{query!r}. Transcribe the useful visible page content, including titles,
listings, snippets, and URLs/domains where legible. Do not invent hidden or
illegible text. Then add a short plain-language summary. Return plain text.
""".strip()
        captured = ollama_vision(
            self.args.ollama_url,
            self.args.vision_model,
            extraction_prompt,
            final_state.screenshot_path,
            timeout=self.args.timeout,
        )
        if not captured:
            captured = (
                "Moondream could not read any visible text from the final screenshot. "
                "Inspect the screenshot path above or rerun with Chrome maximized and at 100% zoom."
            )
        draft_prompt = f"""
Draft concise findings for an Apple Notes note.
User request: {query}

Source material captured from the visible search-results page:
{captured}

Use only the supplied source material. Organize it with a short overview,
bulleted key findings, and a Sources section containing any visible domains or
URLs. Clearly say when the visible material is insufficient. Return plain text
without a title because the Notes note receives its title separately.
""".strip()
        try:
            findings = ollama_text(
                self.args.ollama_url,
                self.args.planner_model,
                draft_prompt,
                timeout=self.args.timeout,
            )
        except AgentError as exc:
            print(f"Drafting warning: {exc}; using the raw captured findings")
            findings = captured
        output = Path(self.args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        header = (
            f"{'Task' if custom_task else 'Query'}: {query}\n"
            f"Captured: {datetime.now().astimezone().isoformat(timespec='seconds')}\n"
            f"Screenshot: {final_state.screenshot_path}\n\n"
        )
        output.write_text(header + findings + "\n", encoding="utf-8")
        note_id: str | None = None
        if not self.args.no_notes:
            self.update_status(
                "running", "Creating and verifying Apple Notes note", request=query, mode=task_mode
            )
            note_id = self.draft_in_notes(query, findings, custom_task=custom_task)
            print(f"Drafted and verified a new Apple Notes note ({note_id}).")
        completion_message = "Apple Notes draft created" if note_id else "Text findings saved"
        self.update_status(
            "complete",
            completion_message,
            request=query,
            mode=task_mode,
            note_id=note_id,
            backup_file=str(output),
        )
        self.notify("Browser task complete", f"{completion_message}: {query}")
        print("\a\n========== TASK COMPLETE ==========")
        print(completion_message)
        print(f"Status: {self.status_path}")
        print("===================================")
        return output

    def run_search(self, query: str) -> Path:
        """Backward-compatible fixed web-search entry point."""
        return self.run_task(query, custom_task=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="The web search query to type into Chrome")
    parser.add_argument(
        "--task",
        help='A custom browser task, for example: "go to LinkedIn and search for new job roles"',
    )
    parser.add_argument("--output", default="artifacts/browser_output.txt")
    parser.add_argument("--engine", choices=["browser", "visual"], default="browser")
    parser.add_argument("--start-url", default="", help="Explicit website, useful for unfamiliar site names")
    parser.add_argument("--max-pages", type=int, default=4, help="Number of relevant source articles")
    parser.add_argument("--include-images", action="store_true", help="Attach source-page screenshots to Notes")
    parser.add_argument("--headless", action="store_true", help="Run research Chrome without a visible window")
    parser.add_argument("--verification-timeout", type=int, default=300,
                        help="Seconds to wait for you to complete a browser verification (default: 300)")
    parser.add_argument("--artifact-dir", default="artifacts/screenshots")
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--vision-model", default="moondream:latest")
    parser.add_argument("--planner-model", default="llama3.2:latest")
    parser.add_argument("--max-steps", type=int, default=12)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--launch-wait", type=float, default=3.0)
    parser.add_argument("--action-pause", type=float, default=0.35)
    parser.add_argument("--key-interval", type=float, default=0.03)
    parser.add_argument("--countdown", type=int, default=5)
    parser.add_argument("--no-launch", action="store_true", help="Use an already-open Chrome window")
    parser.add_argument("--no-notes", action="store_true", help="Skip creating an Apple Notes note")
    parser.add_argument("--dry-run", action="store_true", help="Plan actions but do not control input")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if bool(args.query) == bool(args.task):
        print("error: provide either a search query or --task, but not both", file=sys.stderr)
        return 2
    request = args.task or args.query
    assert request is not None
    if args.max_steps < 1 or not 1 <= args.max_pages <= 12 or args.verification_timeout < 1:
        print("error: --max-steps and --verification-timeout must be positive; --max-pages must be 1 to 12", file=sys.stderr)
        return 2
    agent: ComputerUseAgent | None = None
    try:
        agent = ComputerUseAgent(args)
        agent.update_status("running", "Checking Ollama and required models", request=request)
        required = {args.planner_model}
        if args.engine == "visual":
            required.add(args.vision_model)
        require_models(args.ollama_url, required, args.timeout)
        if not args.dry_run:
            print("Research will begin. Press Ctrl-C or use the GUI Stop button to stop."
                  if args.engine == "browser" else
                  "Computer control will begin. Move the mouse to a corner or press Ctrl-C to stop.")
            for remaining in range(args.countdown, 0, -1):
                print(f"Starting in {remaining}...", flush=True)
                time.sleep(1)
        if args.engine == "browser":
            from browser_research import BrowserResearch
            output = BrowserResearch(agent).run(request)
        else:
            output = agent.run_task(request, custom_task=bool(args.task))
        print(f"\nSaved captured browser content to: {output}")
        return 0
    except KeyboardInterrupt:
        if agent is not None:
            agent.update_status("failed", "Aborted by user", request=request)
            agent.notify("Browser task stopped", f"Aborted: {request}")
        print("\nAborted by user.", file=sys.stderr)
        return 130
    except AgentError as exc:
        if agent is not None:
            agent.update_status("failed", str(exc), request=request)
            agent.notify("Browser task failed", str(exc)[:180])
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # PyAutoGUI's FailSafeException intentionally lands here too.
        if agent is not None:
            message = f"{type(exc).__name__}: {exc}"
            agent.update_status("failed", message, request=request)
            agent.notify("Browser task failed", message[:180])
        print(f"stopped: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
