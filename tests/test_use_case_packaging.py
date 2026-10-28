"""The optional Python reference accepts copied use_case inputs from any cwd."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
USE_CASE_DIRS = sorted(path.parent for path in (REPO / "skills").glob("*/decision.json"))


class UseCasePackagingTests(unittest.TestCase):
    def test_each_copied_use_case_runs_by_absolute_paths_from_unrelated_directory(self):
        self.assertTrue(USE_CASE_DIRS, "use_case folders should be discovered dynamically")
        with tempfile.TemporaryDirectory(prefix="use_case-portability-") as temp:
            root = Path(temp)
            unrelated_cwd = root / "elsewhere"
            unrelated_cwd.mkdir()
            credentials = {"SAGE_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"}
            clean_env = {key: value for key, value in os.environ.items()
                         if key not in credentials | {"PYTHONPATH", "PYTHONHOME"}}
            for source in USE_CASE_DIRS:
                copied = root / "copied-use_cases" / source.name
                with self.subTest(use_case=source.name):
                    shutil.copytree(source, copied)
                    use_case_file = copied / "decision.json"
                    input_file = copied / "examples" / "input.json"
                    demo_file = copied / "examples" / "demo.json"
                    completed = subprocess.run(
                    [sys.executable, "-m", "decision_models", "decide",
                         "--config", str(use_case_file),
                         "--provider", "sage", "--input", str(input_file),
                         "--demo-answers", str(demo_file), "--mode", "demo"],
                        cwd=unrelated_cwd, env=clean_env, text=True,
                        capture_output=True, timeout=30,
                    )
                    self.assertEqual(completed.returncode, 0,
                                     completed.stderr + completed.stdout)
                    result = json.loads(completed.stdout)
                    self.assertEqual(result["skill"], source.name)
                    self.assertEqual(result["source"], "demo")
                    self.assertFalse(result["executed_action"])
                    self.assertIn(result["result"]["action"], ("recommend", "review", "deny"))


if __name__ == "__main__":
    unittest.main()
