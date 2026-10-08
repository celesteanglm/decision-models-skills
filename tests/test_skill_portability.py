"""Copied instruction packs load without the reference package or Python sites."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_skills import verify_folder

REPO = Path(__file__).resolve().parents[1]
FOLDERS = sorted(p.parent for kind in ('skills', 'recipes') for p in (REPO / kind).glob('*/SKILL.md'))


class SkillPortabilityTests(unittest.TestCase):
    def test_copied_instruction_folders_validate_with_no_package_or_site_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            shutil.copy2(REPO / 'scripts/verify_skills.py', root / 'scripts/verify_skills.py')
            for source in FOLDERS:
                shutil.copytree(source, root / source.parent.name / source.name)
            result = subprocess.run([sys.executable, '-I', '-S', str(root / 'scripts/verify_skills.py')],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn(str(len(FOLDERS)), result.stdout)
            self.assertFalse((root / 'src').exists())
            result = subprocess.run([sys.executable, '-I', '-S', '-c',
                                     'import importlib.util; assert importlib.util.find_spec("decision_models") is None'],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_required_references_must_travel_with_the_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / FOLDERS[0].name
            shutil.copytree(FOLDERS[0], folder)
            (folder / 'examples/input.json').unlink()
            with self.assertRaisesRegex(AssertionError, 'nonportable reference'):
                verify_folder(folder)

    def test_each_use_case_declares_its_complete_frozen_decision_menu(self):
        for folder in FOLDERS:
            if not (folder / 'recipe.json').is_file():
                continue
            recipe = json.loads((folder / 'recipe.json').read_text())
            text = (folder / 'SKILL.md').read_text()
            for label in recipe['question']['options']:
                self.assertIn('`' + label + '`', text, (folder.name, label))


if __name__ == '__main__':
    unittest.main()
