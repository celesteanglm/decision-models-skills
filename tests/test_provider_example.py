"""The copied fictional provider example runs from a clean, unrelated directory."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples" / "custom_provider"
SKILL = REPO / "skills" / "email-queue-routing"


class ProviderExampleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.example = root / "copied-example"
        self.skill = root / "copied-skill"
        self.cwd = root / "unrelated-working-directory"
        self.cwd.mkdir()
        shutil.copytree(EXAMPLE, self.example)
        shutil.copytree(SKILL, self.skill)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.endswith("_API_KEY") and "TOKEN" not in key.upper()}
        self.env.pop("PYTHONPATH", None)

    def tearDown(self):
        self.temp.cleanup()

    def run_scenario(self, scenario=None):
        command = [sys.executable, str(self.example / "run.py"),
                   "--config", str(self.skill / "decision.json"),
                   "--input", str(self.skill / "examples" / "input.json")]
        if scenario:
            command.extend(("--scenario", scenario))
        return subprocess.run(command, cwd=self.cwd, env=self.env, text=True,
                              capture_output=True, check=False)

    def test_offline_default_maps_billing_and_preserves_native_metadata(self):
        completed = self.run_scenario()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertTrue(output["synthetic"])
        self.assertEqual(output["mode"], "offline-example")
        self.assertEqual(output["result"]["choice"], "billing")
        self.assertEqual(output["result"]["action"], "recommend")
        self.assertEqual(output["response"]["model"], "fictional-model-v1")
        self.assertEqual(output["response"]["usage"]["input_tokens"], 41)
        self.assertEqual(output["response"]["raw_response"]["usage"]["source"], "synthetic fixture")

    def test_missing_native_confidence_escalates_without_inventing_it(self):
        completed = self.run_scenario("missing-confidence")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual(output["result"]["action"], "review")
        self.assertIn("confidence_missing", output["result"]["reasons"])
        self.assertNotIn("confidence", output["response"]["answers"]["decision"])
        self.assertEqual(output["response"]["answers"]["decision"]["probabilities"]["billing"], 0.9)

    def test_malformed_provider_choice_returns_structured_error(self):
        completed = self.run_scenario("malformed-answer")
        self.assertEqual(completed.returncode, 2)
        error = json.loads(completed.stderr)
        self.assertTrue(error["synthetic"])
        self.assertEqual(error["error"]["code"], "invalid_response")
        self.assertEqual(error["error"]["message"], "selected choice was not supplied")


if __name__ == "__main__":
    unittest.main()
