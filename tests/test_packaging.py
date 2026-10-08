import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
class PackagingTests(unittest.TestCase):
    def test_all_skills_have_valid_frontmatter_and_referenced_local_assets(self):
        for skill_dir in sorted((REPO / "skills").iterdir()):
            if not skill_dir.is_dir():
                continue
            skill = skill_dir.name
            source = (skill_dir / "SKILL.md").read_text()
            match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", source, flags=re.S)
            self.assertIsNotNone(match, skill)
            frontmatter = match.group(1)
            fields = dict(re.findall(r"^(name|description):\s*(.+)$", frontmatter, flags=re.M))
            self.assertEqual(fields.get("name"), skill)
            self.assertTrue(fields.get("description", "").strip(), skill)
            for rel in ("examples/input.json", "examples/demo.json", "fixtures/acceptance.json"):
                path = skill_dir / rel
                self.assertTrue(path.is_file(), f"{skill}: missing {rel}")
                json.loads(path.read_text())
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                local = target.split("#", 1)[0]
                self.assertTrue((skill_dir / local).resolve().is_file(), f"{skill}: broken reference {target}")

    def test_optional_reference_implementation_accepts_copied_core_inputs(self):
        with tempfile.TemporaryDirectory(prefix="skill-copy-") as temp:
            root = Path(temp)
            for source in sorted((REPO / "skills").iterdir()):
                if not source.is_dir():
                    continue
                skill_copy = root / source.name
                shutil.copytree(source, skill_copy)
                with self.subTest(skill=source.name):
                    output = subprocess.run(
                        [sys.executable, "-m", "decision_models", "run", source.name, "--provider", "sage",
                         "--input", "examples/input.json", "--mode", "demo",
                         "--demo-answers", "examples/demo.json"],
                        cwd=skill_copy, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
                        text=True, capture_output=True, timeout=30,
                    )
                    self.assertEqual(output.returncode, 0, output.stderr + output.stdout)
                    result = json.loads(output.stdout)
                    self.assertEqual(result["skill"], source.name)
                    self.assertIn(result["source"], ("demo", "deterministic"))
                    self.assertFalse(result["executed_action"])
                    self.assertIsInstance(result["result"]["action"], str)


if __name__ == "__main__":
    unittest.main()
