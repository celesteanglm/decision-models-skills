"""Portable, offline contracts for published image skills."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from decision_models.evaluation import acceptance
from scripts.image_reference import execute_image, load_config


REPO = Path(__file__).resolve().parents[1]
SKILLS = REPO / "skills"
SCRIPT = REPO / "scripts" / "image_reference.py"


class PublishedImageSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.configs = sorted(SKILLS.glob("*/image.json"))

    def test_every_image_skill_has_frozen_twelve_case_set_and_local_png_assets(self):
        self.assertTrue(self.configs)
        for config_path in self.configs:
            folder = config_path.parent
            with self.subTest(skill=folder.name):
                config = load_config(folder)
                self.assertEqual(config["schema_version"], 2)
                self.assertEqual(config["input_modality"], "image")
                self.assertFalse((folder / "decision.json").exists())
                fixtures = json.loads((folder / "fixtures" / "acceptance.json").read_text())
                self.assertEqual(len(fixtures), 12)
                self.assertEqual({case["category"] for case in fixtures},
                                 {"clear", "ambiguous", "adversarial"})
                self.assertEqual(sum(case["category"] == "clear" for case in fixtures), 8)
                self.assertEqual(sum(case["category"] == "ambiguous" for case in fixtures), 2)
                self.assertEqual(sum(case["category"] == "adversarial" for case in fixtures), 2)
                ids = [case["id"] for case in fixtures]
                self.assertEqual(len(ids), len(set(ids)))
                for case in fixtures:
                    image_ref = case["input"]["state"]["image"]
                    self.assertTrue(image_ref.lower().endswith(".png"), image_ref)
                    image = (folder / image_ref).resolve()
                    self.assertTrue(image.is_relative_to(folder.resolve()), image_ref)
                    self.assertTrue(image.is_file(), image_ref)
                    self.assertEqual(image.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", image_ref)

    def test_all_frozen_demos_satisfy_acceptance_without_inspecting_denied_images(self):
        for config_path in self.configs:
            folder = config_path.parent
            config = load_config(folder)
            cases = json.loads((folder / "fixtures" / "acceptance.json").read_text())
            for case in cases:
                with self.subTest(skill=folder.name, case=case["id"]):
                    result = execute_image(
                        folder,
                        "sage",
                        case["input"],
                        mode="demo",
                        demo_answers=case.get("demo_answers"),
                    )
                    passed, failures = acceptance(result, case["expected"])
                    self.assertTrue(passed, (case["id"], failures, result["result"]))
                    self.assertFalse(result["executed_action"])
                    if case["input"].get("permission_granted") is False:
                        self.assertEqual(result["result"]["action"], "deny")
                        self.assertIsNone(result["image"])
                        self.assertEqual(result["attempts"], 0)
                        self.assertEqual(result["source"], "deterministic")

    def test_skill_publishes_full_image_decision_menu_and_portable_references(self):
        for config_path in self.configs:
            folder = config_path.parent
            config = load_config(folder)
            skill = (folder / "SKILL.md").read_text()
            for label in config["question"]["options"]:
                self.assertRegex(skill, rf"(?m)^- `{re.escape(label)}`:")
            local_targets = []
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", skill):
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                local_targets.append(target)
                local = (folder / target.split("#", 1)[0]).resolve()
                self.assertTrue(local.is_relative_to(folder.resolve()), target)
                self.assertTrue(local.is_file(), target)
            self.assertTrue(local_targets, folder.name)
            self.assertIn("fixtures/acceptance.json", local_targets)

    def test_copied_skill_assets_run_from_another_directory_with_direct_script_demo(self):
        self.assertEqual(len(self.configs), 1)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            copied = root / ".agents" / "skills" / self.configs[0].parent.name
            shutil.copytree(self.configs[0].parent, copied)
            elsewhere = root / "elsewhere"
            elsewhere.mkdir()
            env = dict(os.environ)
            for key in ("PYTHONPATH", "SAGE_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"):
                env.pop(key, None)
            command = [sys.executable, "-I", str(SCRIPT), "--folder", str(copied),
                       "--input", str(copied / "examples" / "input.json"), "--mode", "demo",
                       "--demo-answers", str(copied / "examples" / "demo.json")]
            completed = subprocess.run(command, cwd=elsewhere, env=env,
                                       capture_output=True, text=True, check=False, timeout=30)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            output = json.loads(completed.stdout)
            self.assertEqual(output["result"]["action"], "recommend")
            self.assertFalse(output["executed_action"])
            self.assertEqual(output["response"]["answers"]["decision"]["choice"], "visible")


if __name__ == "__main__":
    unittest.main()
