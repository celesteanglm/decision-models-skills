"""The collection entrypoint and generated index remain portable and current."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.skill_catalog import build_catalog, verify_catalog
from scripts.verify_skills import verify_folder

REPO = Path(__file__).resolve().parents[1]


class SkillRouterTests(unittest.TestCase):
    def copied_collection(self, root):
        destination = Path(root) / 'copied-collection'
        destination.mkdir()
        shutil.copy2(REPO / 'SKILL.md', destination)
        shutil.copytree(REPO / 'skills', destination / 'skills')
        return destination

    def test_catalog_describes_every_available_skill_and_points_to_its_evidence(self):
        verify_catalog(REPO)
        catalog = build_catalog(REPO)
        ids = {p.parent.name for p in (REPO / 'skills').glob('*/SKILL.md')}
        self.assertEqual({row['id'] for row in catalog['skills']}, ids)
        self.assertEqual(len(catalog['skills']), len(ids))
        for row in catalog['skills']:
            with self.subTest(skill=row['id']):
                self.assertEqual(row['skill_path'], f"skills/{row['id']}/SKILL.md")
                self.assertEqual(row['compatibility_path'], f"skills/{row['id']}/COMPATIBILITY.md")
                self.assertEqual(row['input_modality'], 'image' if (REPO / 'skills' / row['id'] / 'image.json').exists() else 'text')
                self.assertNotIn('working_backends', row)

    def test_entrypoint_and_catalog_validate_after_copy_without_package_or_checkout(self):
        with tempfile.TemporaryDirectory() as root:
            copied = self.copied_collection(root)
            self.assertEqual(verify_folder(copied, expected_name='decision-models-skills'), 'decision-models-skills')
            scripts = copied / 'scripts'
            scripts.mkdir()
            for name in ('skill_catalog.py', 'verify_skills.py'):
                shutil.copy2(REPO / 'scripts' / name, scripts / name)
            elsewhere = Path(root) / 'elsewhere'
            elsewhere.mkdir()
            completed = subprocess.run([sys.executable, '-I', '-S', str(scripts / 'skill_catalog.py')],
                                       cwd=elsewhere, capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse((copied / 'src').exists())

    def test_changed_skill_description_requires_regenerating_the_index(self):
        with tempfile.TemporaryDirectory() as root:
            copied = self.copied_collection(root)
            path = copied / 'skills/email-queue-routing/SKILL.md'
            path.write_text(path.read_text().replace('description: ', 'description: Updated '))
            with self.assertRaisesRegex(ValueError, 'stale routing catalog'):
                verify_catalog(copied)
            (copied / 'skills/catalog.json').write_text(json.dumps(build_catalog(copied)))
            verify_catalog(copied)

    def test_missing_or_forged_catalog_targets_are_rejected(self):
        for edit in ('missing', 'outside'):
            with self.subTest(edit=edit), tempfile.TemporaryDirectory() as root:
                copied = self.copied_collection(root)
                path = copied / 'skills/catalog.json'
                catalog = json.loads(path.read_text())
                if edit == 'missing':
                    catalog['skills'].pop()
                else:
                    catalog['skills'][0]['skill_path'] = '../unrelated/SKILL.md'
                path.write_text(json.dumps(catalog))
                with self.assertRaisesRegex(ValueError, 'stale routing catalog'):
                    verify_catalog(copied)

    def test_router_cases_reference_real_skills_and_keep_the_oracle_separate(self):
        cases = json.loads((REPO / 'tests/fixtures/skill-router-cases.json').read_text())['cases']
        ids = {row['id'] for row in build_catalog(REPO)['skills']}
        self.assertEqual(len({case['id'] for case in cases}), len(cases))
        for case in cases:
            self.assertIsInstance(case['input'], str)
            self.assertIn(case['expected']['skill_id'], ids | {None})
            self.assertIn(case['expected']['outcome'], {'complete', 'needs_input', 'needs_setup', 'deny', 'out_of_scope'})
