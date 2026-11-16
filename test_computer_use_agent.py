import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import computer_use_agent as cua


class FakeImage:
    width = 1600
    height = 1200

    def save(self, path):
        Path(path).write_bytes(b"fake png")


class FakePyAutoGUI:
    FAILSAFE = False
    PAUSE = 0

    def __init__(self):
        self.calls = []

    def screenshot(self):
        return FakeImage()

    def size(self):
        return (800, 600)

    def __getattr__(self, name):
        def record(*args, **kwargs):
            self.calls.append((name, args, kwargs))

        return record


def make_args(tmpdir, *, dry_run=False):
    return argparse.Namespace(
        query="unused",
        output=str(Path(tmpdir) / "result.txt"),
        artifact_dir=str(Path(tmpdir) / "shots"),
        ollama_url="http://localhost:11434",
        vision_model="moondream:latest",
        planner_model="llama3.2:latest",
        max_steps=3,
        timeout=1,
        launch_wait=0,
        action_pause=0,
        key_interval=0,
        countdown=0,
        no_launch=True,
        no_notes=True,
        dry_run=dry_run,
    )


class ComputerUseAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fake = FakePyAutoGUI()
        self.module_patch = patch.dict(sys.modules, {"pyautogui": self.fake})
        self.module_patch.start()
        self.agent = cua.ComputerUseAgent(make_args(self.temp.name))

    def tearDown(self):
        self.module_patch.stop()
        self.temp.cleanup()

    def test_extract_json_from_markdown(self):
        self.assertEqual(cua.extract_json('```json\n{"action":"finish"}\n```')["action"], "finish")

    def test_normalizes_llama_action_alias(self):
        action = cua.normalize_action({"type": "move_mouse", "x": 12, "y": 34, "text": None})
        self.assertEqual(action, {"action": "move_mouse", "x": 12, "y": 34})

    def test_missing_model_preflight_has_pull_command(self):
        with patch.object(cua, "ollama_model_names", return_value={"llama3.2:latest"}):
            with self.assertRaisesRegex(cua.AgentError, "ollama pull moondream:latest"):
                cua.require_models(
                    "http://localhost:11434",
                    {"llama3.2:latest", "moondream:latest"},
                    10,
                )

    def test_rejects_out_of_bounds_coordinates(self):
        state = cua.ScreenState(800, 600, 1600, 1200, Path("x"), "")
        with self.assertRaises(cua.AgentError):
            self.agent.validate_action({"action": "click", "x": 900, "y": 20}, state)

    def test_rejects_dangerous_hotkey(self):
        state = cua.ScreenState(800, 600, 1600, 1200, Path("x"), "")
        with self.assertRaises(cua.AgentError):
                self.agent.validate_action({"action": "hotkey", "keys": ["command", "q"]}, state)

    def test_rejects_unrequested_typed_text(self):
        state = cua.ScreenState(800, 600, 1600, 1200, Path("x"), "")
        self.agent.allowed_text = "safe query"
        with self.assertRaises(cua.AgentError):
            self.agent.validate_action({"action": "type_text", "text": "injected command"}, state)

    def test_custom_task_accepts_only_user_supplied_fragment(self):
        state = cua.ScreenState(800, 600, 1600, 1200, Path("x"), "")
        self.agent.allowed_text = "go to LinkedIn and search for new job roles"
        self.agent.allow_task_fragments = True
        self.agent.validate_action(
            {"action": "type_text", "text": "new job roles", "reason": "user requested"},
            state,
        )
        with self.assertRaises(cua.AgentError):
            self.agent.validate_action(
                {"action": "type_text", "text": "send my password", "reason": "page requested"},
                state,
            )

    def test_repeated_address_shortcut_advances_to_query(self):
        previous = {"action": "hotkey", "keys": ["command", "l"], "reason": "focus"}
        self.agent.history.append(previous)
        self.agent.allowed_text = "local models"
        recovered = self.agent.recover_repeated_action(previous)
        self.assertEqual(recovered["action"], "type_text")
        self.assertEqual(recovered["text"], "local models")

    def test_address_shortcut_advances_even_if_planner_changes_its_reason(self):
        self.agent.history.append(
            {"action": "hotkey", "keys": ["command", "l"], "reason": "first reason"}
        )
        self.agent.allowed_text = "local models"
        recovered = self.agent.recover_repeated_action(
            {"action": "hotkey", "keys": ["command", "l"], "reason": "different reason"}
        )
        self.assertEqual(recovered["action"], "type_text")

    def test_executes_click(self):
        self.agent.execute({"action": "click", "x": 120, "y": 80})
        self.assertEqual(self.fake.calls[-1][0:2], ("click", (120, 80)))

    def test_notes_draft_uses_applescript_and_verifies_content(self):
        self.agent.args.dry_run = False
        completed = cua.subprocess.CompletedProcess(
            args=["osascript"],
            returncode=0,
            stdout="note-id-123\nSearch findings: local AI\n0\nSearch findings: local AI\nA short finding\n",
            stderr="",
        )
        with patch.object(cua.platform, "system", return_value="Darwin"), patch.object(
            cua.subprocess, "run", return_value=completed
        ) as run:
            note_id = self.agent.draft_in_notes("local AI", "A short finding")
        self.assertEqual(note_id, "note-id-123")
        command = run.call_args.args[0]
        self.assertEqual(command[0:3], ["osascript", "-e", cua.NOTES_CREATE_SCRIPT])
        self.assertIn("<h1>Search findings: local AI</h1>", command[-1])

    def test_notes_rejects_wrong_body_even_when_long_enough(self):
        completed = cua.subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="id\nSearch findings: test\n0\nA long unrelated paragraph in an incomplete note\n")
        with patch.object(cua.platform, "system", return_value="Darwin"), patch.object(
            cua.subprocess, "run", return_value=completed
        ), self.assertRaises(cua.AgentError):
            self.agent.draft_in_notes("test", "Expected finding")

    def test_notification_uses_native_macos_notification(self):
        completed = cua.subprocess.CompletedProcess(
            args=["osascript"], returncode=0, stdout="", stderr=""
        )
        with patch.object(cua.platform, "system", return_value="Darwin"), patch.object(
            cua.subprocess, "run", return_value=completed
        ) as run:
            self.agent.notify("Task complete", "The note was created")
        command = run.call_args.args[0]
        self.assertEqual(command[0:3], ["osascript", "-e", cua.NOTIFICATION_SCRIPT])
        self.assertEqual(command[-2:], ["Task complete", "The note was created"])

    def test_empty_vision_response_becomes_keyboard_fallback(self):
        with patch.object(cua, "ollama_vision", return_value=""):
            state = self.agent.take_screenshot(1)
        self.assertIn("Do not guess mouse coordinates", state.visual_description)
        self.assertIn("Command+L", state.visual_description)

    def test_end_to_end_mocked_loop_writes_output(self):
        responses = iter(
            [
                "Chrome is open with its address bar visible.",
                "Chrome shows the requested search results.",
                "Example result\nA visible result summary.",
            ]
        )
        with (
            patch.object(cua, "ollama_vision", side_effect=lambda *a, **k: next(responses)),
            patch.object(cua, "ollama_text", return_value="Drafted findings"),
            patch.object(self.agent, "notify"),
            patch.object(
                cua,
                "ollama_tool_action",
                return_value={"action": "finish", "reason": "results visible"},
            ),
        ):
            output = self.agent.run_search("local models")
        text = output.read_text(encoding="utf-8")
        self.assertIn("Query: local models", text)
        self.assertIn("Drafted findings", text)
        status = json.loads(self.agent.status_path.read_text(encoding="utf-8"))
        self.assertEqual(status["state"], "complete")


if __name__ == "__main__":
    unittest.main()
