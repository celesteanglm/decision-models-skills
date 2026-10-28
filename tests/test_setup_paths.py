"""Run the documented installs in isolated project and personal skill locations."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from scripts.skill_catalog import verify_catalog
from scripts.verify_skills import verify_folder

REPO = Path(__file__).resolve().parents[1]
README = (REPO / 'README.md').read_text()


def setup_command(path):
    match = re.search(rf'<!-- setup: {path} -->\n```sh\n(.*?)\n```', README, re.S)
    if not match:
        raise AssertionError(f'missing runnable setup: {path}')
    # Pass the actual destination as a shell argument, including paths with spaces.
    return match[1].replace('"/path/to/your-project/.agents/skills"', '"$1"')


class SetupPathTests(unittest.TestCase):
    def test_readme_installs_standalone_or_collection_for_both_hosts_and_scopes(self):
        for mode in ('individual', 'collection'):
            for location in ('project/.agents/skills', 'project/.claude/skills',
                             'home/.agents/skills', 'home/.claude/skills'):
                with self.subTest(mode=mode, location=location), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / 'fresh setup with spaces'
                    source = root / 'download'
                    source.mkdir(parents=True)
                    if mode == 'individual':
                        # The entire available download is one skill: no router or catalog.
                        shutil.copytree(REPO / 'skills/email-queue-routing',
                                        source / 'skills/email-queue-routing')
                        name = 'email-queue-routing'
                    else:
                        shutil.copy2(REPO / 'SKILL.md', source)
                        shutil.copytree(REPO / 'skills', source / 'skills')
                        name = 'decision-models-skills'
                    destination = root / location
                    env = {k: v for k, v in os.environ.items()
                           if k not in ('OPENROUTER_API_KEY', 'SAGE_API_KEY',
                                        'OPENAI_API_KEY', 'PYTHONPATH')}
                    command = ['sh', '-eu', '-c', setup_command(mode),
                               'readme-setup', str(destination)]
                    result = subprocess.run(command, cwd=source, env=env,
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    installed = destination / name
                    # The download can now disappear; all local references must still resolve.
                    shutil.rmtree(source)
                    self.assertEqual(verify_folder(installed), name)
                    if mode == 'collection':
                        verify_catalog(installed)
                        for child in (installed / 'skills').glob('*/SKILL.md'):
                            verify_folder(child.parent)
                    else:
                        self.assertFalse((installed / 'skills').exists())
                        self.assertFalse((destination / 'decision-models-skills').exists())
                    self.assertFalse((installed / 'src').exists())
                    self.assertFalse((installed / 'scripts').exists())
                    self.assertFalse((installed / '.git').exists())

    def test_repeating_setup_preserves_an_existing_installation(self):
        for mode, name in (('individual', 'email-queue-routing'),
                           ('collection', 'decision-models-skills')):
            for symlink in (False, True):
                with self.subTest(mode=mode, symlink=symlink), tempfile.TemporaryDirectory() as tmp:
                    destination = Path(tmp) / 'skills'
                    destination.mkdir()
                    installed = destination / name
                    if symlink:
                        # A broken link is still an existing user-owned installation.
                        installed.symlink_to(Path(tmp) / 'missing-target', target_is_directory=True)
                    else:
                        installed.mkdir()
                        (installed / 'SKILL.md').write_text('user-maintained instructions\n')
                    result = subprocess.run(
                        ['sh', '-eu', '-c', setup_command(mode),
                         'readme-setup', str(destination)], cwd=tmp,
                        capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    if symlink:
                        self.assertTrue(installed.is_symlink())
                        self.assertFalse(installed.exists())
                    else:
                        self.assertEqual((installed / 'SKILL.md').read_text(),
                                         'user-maintained instructions\n')
                        self.assertEqual(list(installed.iterdir()), [installed / 'SKILL.md'])


if __name__ == '__main__':
    unittest.main()
