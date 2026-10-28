"""Scoped compatibility publishing rejects evidence drift and stays selective."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from decision_models.evaluation import source_hash
from scripts.publish_compatibility import build_manifest, main as publish_main
from scripts.verified_catalog import PROVIDERS, artifacts, runtime_revision, sha256


REPO = Path(__file__).resolve().parents[1]
PUBLISHED = "model-tier-routing"
UNSELECTED = "email-queue-routing"
HELPERS = ("scripts/usecase_reference.py", "scripts/evaluate_usecases.py")
EVIDENCE_URL = "https://example.invalid/retained/synthetic-receipt.json"


def copy_repo(root):
    repo = Path(root) / "repo"
    repo.mkdir()
    for directory in ("src", "skills", "scripts"):
        shutil.copytree(REPO / directory, repo / directory)
    shutil.copy2(REPO / "README.md", repo / "README.md")
    return repo


def fixture_revision(folder):
    fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
    return hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()


def receipt_for(repo, item_id=PUBLISHED, *, fail_clear=False):
    folder = repo / "skills" / item_id
    fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
    revision = fixture_revision(folder)
    rows = []
    for provider in PROVIDERS:
        for case in fixtures:
            for repetition in range(1, 4):
                passed = not (fail_clear and case["category"] == "clear" and case["id"] == "clear-08")
                rows.append({
                    "provider": provider,
                    "skill": item_id,
                    "case_id": case["id"],
                    "category": case["category"],
                    "repetition": repetition,
                    "passed": passed,
                    "output": {
                        "source": "live",
                        "result": {"action": "recommend", "choice": "synthetic"},
                        "response": {"model": "synthetic-test-model"},
                        "latency_ms": 1,
                    },
                })
    return {
        "mode": "live",
        "repetitions": 3,
        "updated_at": "2026-10-27T00:00:00+00:00",
        "source_hash": source_hash(repo),
        "runtime_revision": runtime_revision(repo),
        "fixtures": {item_id: revision},
        "evaluated_artifacts": {item_id: artifacts(folder)},
        "reference_artifacts": {helper: sha256(repo / helper) for helper in HELPERS},
        "rows": rows,
        "summary": {f"{provider}/{item_id}": {"offline_passed": True} for provider in PROVIDERS},
    }


def build(repo, receipt):
    folder = repo / "skills" / PUBLISHED
    return build_manifest(repo, folder, receipt, "a" * 64, EVIDENCE_URL)


class PublishScopeTests(unittest.TestCase):
    def test_identical_scoped_files_helpers_and_runtime_are_accepted_without_raw_reports(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_repo(root)
            receipt = receipt_for(repo)
            manifest = build(repo, receipt)
            self.assertEqual(manifest["reference_artifacts"], receipt["reference_artifacts"])
            self.assertEqual(manifest["artifacts"], receipt["evaluated_artifacts"][PUBLISHED])
            self.assertFalse(any((repo / name).exists() for name in ("reports", "docs", "research")))

    def test_helper_configuration_fixture_and_runtime_drift_are_rejected(self):
        for helpers in ({}, {HELPERS[0]: sha256(REPO / HELPERS[0])}):
            with self.subTest(helpers=helpers), tempfile.TemporaryDirectory() as root:
                repo = copy_repo(root)
                receipt = receipt_for(repo)
                receipt["reference_artifacts"] = helpers
                with self.assertRaisesRegex(AssertionError, "incomplete reference helper set"):
                    build(repo, receipt)
        mutations = {
            "helper": (HELPERS[0], "\n# helper drift\n", "reference helper changed"),
            "configuration": (f"skills/{PUBLISHED}/decision.json", " ", "scoped artifacts changed"),
            "fixtures": (f"skills/{PUBLISHED}/fixtures/acceptance.json", None, "fixtures differ from evaluated cases"),
            "runtime": ("src/decision_models/use_cases.py", "\n# runtime drift\n", "reference runtime changed"),
        }
        for name, (relative, suffix, message) in mutations.items():
            with self.subTest(file=name), tempfile.TemporaryDirectory() as root:
                repo = copy_repo(root)
                receipt = receipt_for(repo)
                path = repo / relative
                if suffix is None:
                    fixtures = json.loads(path.read_text())
                    fixtures[0]["input"]["state"]["content"] += " changed"
                    path.write_text(json.dumps(fixtures))
                else:
                    path.write_text(path.read_text() + suffix)
                with self.assertRaisesRegex(AssertionError, message):
                    build(repo, receipt)

    def test_selective_publication_does_not_touch_unselected_manifests(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_repo(root)
            receipt = receipt_for(repo)
            receipt_path = Path(root) / "synthetic-receipt.json"
            receipt_path.write_text(json.dumps(receipt))
            before = {
                relative: (repo / relative).read_bytes()
                for relative in (
                    f"skills/{UNSELECTED}/compatibility.json",
                    f"skills/{UNSELECTED}/COMPATIBILITY.md",
                )
            }
            arguments = [
                "publish_compatibility.py", "--repo", str(repo),
                "--receipt", str(receipt_path), "--evidence-url", EVIDENCE_URL,
                "--ids", PUBLISHED,
            ]
            with patch.object(sys, "argv", arguments):
                publish_main()
            for relative, original in before.items():
                self.assertEqual((repo / relative).read_bytes(), original)
            published = json.loads((repo / "skills" / PUBLISHED / "compatibility.json").read_text())
            self.assertEqual(published["id"], PUBLISHED)
            self.assertEqual(set(published["reference_artifacts"]), set(HELPERS))

    def test_publisher_refuses_receipt_with_no_working_backend(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_repo(root)
            receipt = receipt_for(repo, fail_clear=True)
            with self.assertRaisesRegex(AssertionError, "no Working backend"):
                build(repo, receipt)

    def test_publisher_cannot_drop_the_migration_from_historical_results(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_repo(root)
            folder = repo / "skills" / PUBLISHED
            previous = json.loads((folder / "compatibility.json").read_text())
            with self.assertRaisesRegex(AssertionError, "historical receipts require the recorded layout migration"):
                build_manifest(repo, folder, receipt_for(repo), previous["evidence"]["sha256"], EVIDENCE_URL)

    def test_invalid_batch_leaves_all_existing_summaries_untouched(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_repo(root)
            receipt = receipt_for(repo, UNSELECTED)
            invalid = receipt_for(repo, PUBLISHED, fail_clear=True)
            for field in ("fixtures", "evaluated_artifacts", "summary"):
                receipt[field].update(invalid[field])
            receipt["rows"].extend(invalid["rows"])
            path = Path(root) / "synthetic-receipt.json"
            path.write_text(json.dumps(receipt))
            folders = [repo / "skills" / skill for skill in (UNSELECTED, PUBLISHED)]
            before = {p: p.read_bytes() for folder in folders
                      for p in (folder / "compatibility.json", folder / "COMPATIBILITY.md")}
            arguments = ["publish_compatibility.py", "--repo", str(repo),
                         "--receipt", str(path), "--evidence-url", EVIDENCE_URL,
                         "--ids", UNSELECTED, PUBLISHED]
            with patch.object(sys, "argv", arguments), self.assertRaisesRegex(AssertionError, "no Working backend"):
                publish_main()
            self.assertEqual({p: p.read_bytes() for p in before}, before)


if __name__ == "__main__":
    unittest.main()
