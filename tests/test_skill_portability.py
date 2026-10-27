"""Copied instruction packs load without the reference package or Python sites."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.verify_skills import verify_folder

REPO = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO / 'skills'
FOLDERS = sorted(p.parent for p in SKILL_ROOT.glob('*/SKILL.md'))


def readme_catalog_ids(section):
    readme = (REPO / 'README.md').read_text()
    selected = readme.split(f"### {section}\n", 1)[1].split("\n### ", 1)[0]
    return re.findall(r"^\|\s*\[[^]]+\]\(skills/([^/]+)/SKILL\.md\)", selected, re.MULTILINE)


class SkillPortabilityTests(unittest.TestCase):
    def test_catalog_uses_one_root_for_readme_and_canonical_skill_folders(self):
        general_ids = readme_catalog_ids("General skills")
        use_case_ids = readme_catalog_ids("Use-case skills")
        text_configs = list(SKILL_ROOT.glob("*/decision.json"))
        image_configs = list(SKILL_ROOT.glob("*/image.json"))
        self.assertEqual(len(general_ids), 6)
        self.assertEqual(len(text_configs), 20)
        self.assertEqual(len(image_configs), 1)
        self.assertEqual(len(use_case_ids), len(text_configs) + len(image_configs))
        catalog_ids = general_ids + use_case_ids
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        self.assertEqual(set(catalog_ids), {folder.name for folder in FOLDERS})
        self.assertEqual(len(FOLDERS), len(general_ids) + len(text_configs) + len(image_configs))
        self.assertTrue(all(folder.is_dir() for folder in FOLDERS))
        self.assertEqual(len(text_configs), 20)
        other_roots = {
            root.name for root in REPO.iterdir()
            if root.is_dir() and root.name != 'skills' and not root.name.startswith('.')
            and any(root.glob('*/SKILL.md'))
        }
        self.assertEqual(other_roots, set())
        for folder in FOLDERS:
            expected = {'compatibility.json'}
            if (folder / 'decision.json').is_file():
                expected.add('decision.json')
            if (folder / 'image.json').is_file():
                expected.add('image.json')
            self.assertEqual({path.name for path in folder.glob('*.json')}, expected,
                             folder.name)

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
            if not (folder / 'decision.json').is_file():
                continue
            use_case = json.loads((folder / 'decision.json').read_text())
            text = (folder / 'SKILL.md').read_text()
            for label in use_case['question']['options']:
                self.assertIn('`' + label + '`', text, (folder.name, label))


if __name__ == '__main__':
    unittest.main()
