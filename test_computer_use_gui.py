import unittest
from pathlib import Path

from computer_use_gui import DEFAULTS, build_command


class GUICommandTests(unittest.TestCase):
    def test_builds_custom_task_with_user_options(self):
        settings = {
            **DEFAULTS,
            "mode": "Custom browser task",
            "request": "go to LinkedIn and search for new job roles",
            "max_steps": "24",
            "create_notes": True,
            "launch_chrome": False,
        }
        command = build_command(settings, python="python", script=Path("agent.py"))
        self.assertEqual(command[0:3], ["python", "-u", "agent.py"])
        self.assertIn("--task", command)
        self.assertIn("go to LinkedIn and search for new job roles", command)
        self.assertIn("--no-launch", command)
        self.assertNotIn("--no-notes", command)

    def test_builds_web_search_and_no_notes(self):
        settings = {**DEFAULTS, "request": "local AI", "create_notes": False}
        command = build_command(settings, python="python", script=Path("agent.py"))
        self.assertIn("local AI", command)
        self.assertIn("--no-notes", command)
        self.assertNotIn("--task", command)

    def test_rejects_empty_request(self):
        with self.assertRaises(ValueError):
            build_command({**DEFAULTS, "request": ""})


if __name__ == "__main__":
    unittest.main()

