"""Runtime upgrades preserve original evidence and reject incomplete comparisons."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.publish_compatibility import apply_integration_update
from scripts.verified_catalog import verify_catalog

REPO = Path(__file__).resolve().parents[1]


class IntegrationEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / 'repo'
        self.repo.mkdir()
        for name in ('src', 'skills', 'scripts'):
            shutil.copytree(REPO / name, self.repo / name)
        shutil.copy2(REPO / 'README.md', self.repo)
        self.path = self.repo / 'skills/email-queue-routing/compatibility.json'
        self.manifest = json.loads(self.path.read_text())

    def test_historical_runtime_cannot_silently_drop_upgrade_evidence(self):
        self.manifest.pop('integration_update')
        self.path.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(AssertionError, 'runtime changed since evaluation'):
            verify_catalog(self.repo)

    def test_modified_helper_cannot_inherit_historical_labels(self):
        helper = self.repo / 'scripts/image_reference.py'
        helper.write_text(helper.read_text() + '\n# changed helper\n')
        with self.assertRaisesRegex(AssertionError, 'reference helper changed since integration audit'):
            verify_catalog(self.repo)

    def test_incomplete_replay_proof_leaves_every_summary_untouched(self):
        update = copy.deepcopy(self.manifest['integration_update'])
        golden = json.loads((self.repo / 'scripts/reference-contracts.json').read_text())
        proof = dict(update, kind='reference-upgrade-audit', identical=True,
                     actual_archived_response_replays=0, artifacts=golden['artifacts'],
                     receipts=[{'path': name, 'sha256': digest} for name, digest in golden['receipt_sha256'].items()])
        path = Path(self.temporary.name) / 'incomplete-proof.json'
        path.write_text(json.dumps(proof))
        before = {p: p.read_bytes() for p in (self.repo / 'skills').glob('*/compatibility.json')}
        with self.assertRaisesRegex(AssertionError, 'incomplete integration replays'):
            apply_integration_update(self.repo, path, 'https://example.invalid/incomplete-proof.json')
        self.assertEqual(before, {p: p.read_bytes() for p in before})
