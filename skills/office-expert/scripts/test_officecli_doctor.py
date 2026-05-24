#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("officecli_doctor.py")


class OfficeCliDoctorTests(unittest.TestCase):
    def run_doctor(self, env):
        merged_env = os.environ.copy()
        merged_env.update(env)
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=Path(__file__).parents[2],
            env=merged_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.stderr, "")
        return completed.returncode, json.loads(completed.stdout)

    def test_reports_unavailable_when_command_is_missing(self):
        code, payload = self.run_doctor({"OFFICECLI_COMMAND": "definitely-missing-officecli-command"})
        self.assertEqual(code, 1)
        self.assertFalse(payload["available"])
        self.assertEqual(payload["command"], "definitely-missing-officecli-command")
        self.assertIn("not found", payload["reason"])
        self.assertIn("Install OfficeCLI", payload["guidance"])

    def test_reports_available_for_configured_python_command(self):
        code, payload = self.run_doctor({"OFFICECLI_COMMAND": sys.executable})
        self.assertEqual(code, 0)
        self.assertTrue(payload["available"])
        self.assertEqual(payload["command"], sys.executable)
        self.assertTrue(payload["version"])
        self.assertEqual(payload["source"], "OFFICECLI_COMMAND")

    def test_reports_available_for_windows_exe_without_suffix(self):
        executable = Path(sys.executable)
        if executable.suffix.lower() != ".exe":
            self.skipTest("Windows .exe suffix behavior only")
        without_suffix = str(executable.with_suffix(""))
        code, payload = self.run_doctor({"OFFICECLI_COMMAND": without_suffix})
        self.assertEqual(code, 0)
        self.assertTrue(payload["available"])
        self.assertEqual(payload["command"], without_suffix)
        self.assertEqual(payload["resolvedCommand"], sys.executable)


if __name__ == "__main__":
    unittest.main()
