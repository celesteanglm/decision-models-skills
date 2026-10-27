"""A fresh checkout verifies local compatibility without archived raw runs."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.publish_compatibility import build_manifest
from scripts.verified_catalog import (
    compatibility_markdown, PROVIDERS, qualification, sha256, verify_catalog,
)

REPO = Path(__file__).resolve().parents[1]
USE_CASE = "model-tier-routing"


def copy_inputs(root):
    repo = Path(root) / "repo"
    repo.mkdir()
    for directory in ("src", "skills", "scripts"):
        shutil.copytree(REPO / directory, repo / directory)
    shutil.copy2(REPO / "README.md", repo / "README.md")
    return repo


def change_manifest(repo, edit):
    folder = repo / "skills" / USE_CASE
    path = folder / "compatibility.json"
    manifest = json.loads(path.read_text())
    edit(manifest)
    path.write_text(json.dumps(manifest))
    (folder / "COMPATIBILITY.md").write_text(compatibility_markdown(manifest))
    return manifest


class VerifiedCatalogTests(unittest.TestCase):
    def test_fresh_tree_has_no_reports_docs_or_research_dependency(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            registry = verify_catalog(repo)
            self.assertEqual(set(registry), {"skills"})
            self.assertEqual(len(registry["skills"]), 26)
            self.assertEqual(len(list((repo / "skills").glob("*/decision.json"))), 20)
            self.assertFalse(any((repo / name).exists() for name in ("docs", "research", "reports")))
            self.assertEqual(registry["skills"][USE_CASE]["working_backends"], ["sage"])

    def test_every_status_is_derived_from_recorded_acceptance_counts(self):
        registry = verify_catalog(REPO)
        for item_id, entry in registry["skills"].items():
            fixtures = json.loads((REPO / "skills" / item_id / "fixtures/acceptance.json").read_text())
            self.assertTrue(entry["working_backends"])
            for provider in PROVIDERS:
                backend = entry["manifest"]["backends"][provider]
                self.assertEqual(backend["status"], qualification(backend, fixtures))

    def test_rejects_promoting_partial_backend_without_passing_counts(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            change_manifest(repo, lambda m: m["backends"]["jev-openrouter"].update(status="Working"))
            with self.assertRaisesRegex(AssertionError, "unsupported status"):
                verify_catalog(repo)

    def test_rejects_working_badge_for_partial_backend(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            skill = repo / "skills" / USE_CASE / "SKILL.md"
            skill.write_text(skill.read_text() + "\n![Unsupported](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen)\n")
            with self.assertRaisesRegex(AssertionError, "unsupported badge"):
                verify_catalog(repo)

    def test_reference_receipt_cannot_claim_instruction_only_qualification(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            change_manifest(repo, lambda m: m['scope'].update(instruction_only='Working'))
            with self.assertRaisesRegex(AssertionError, 'reference evidence cannot qualify instruction-only'):
                verify_catalog(repo)

    def test_rejects_stale_human_readable_results(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            page = repo / "skills" / USE_CASE / "COMPATIBILITY.md"
            page.write_text(page.read_text().replace("Not qualified (Partial)", "Working"))
            with self.assertRaisesRegex(AssertionError, "stale compatibility"):
                verify_catalog(repo)

    def test_rejects_configuration_example_and_fixture_drift(self):
        for relative in ("decision.json", "examples/input.json", "fixtures/acceptance.json"):
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as root:
                repo = copy_inputs(root)
                path = repo / "skills" / USE_CASE / relative
                path.write_text(path.read_text() + " \n")
                with self.assertRaisesRegex(AssertionError, "unverified artifacts"):
                    verify_catalog(repo)

    def test_rejects_runtime_changes(self):
        for helpers in ({}, {"scripts/usecase_reference.py": sha256(REPO / "scripts/usecase_reference.py")}):
            with self.subTest(helpers=helpers), tempfile.TemporaryDirectory() as root:
                repo = copy_inputs(root)
                change_manifest(repo, lambda m: m.update(reference_artifacts=helpers))
                with self.assertRaisesRegex(AssertionError, "incomplete reference helper set"):
                    verify_catalog(repo)
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            path = repo / "src/decision_models/use_cases.py"
            path.write_text(path.read_text() + "\n")
            with self.assertRaisesRegex(AssertionError, "runtime changed"):
                verify_catalog(repo)

    def test_rejects_missing_summary_and_dangling_catalog_entry(self):
        for remove_folder in (False, True):
            with self.subTest(folder=remove_folder), tempfile.TemporaryDirectory() as root:
                repo = copy_inputs(root)
                folder = repo / "skills" / USE_CASE
                if remove_folder:
                    shutil.rmtree(folder)
                else:
                    (folder / "compatibility.json").unlink()
                with self.assertRaises(AssertionError):
                    verify_catalog(repo)

    def test_rejects_missing_layout_migration_for_historical_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            folder = repo / "skills" / USE_CASE
            path = folder / "compatibility.json"
            manifest = json.loads(path.read_text())
            self.assertIn("migration", manifest)
            manifest.pop("migration")
            path.write_text(json.dumps(manifest))
            (folder / "COMPATIBILITY.md").write_text(compatibility_markdown(manifest))
            with self.assertRaisesRegex(AssertionError, "missing layout migration"):
                verify_catalog(repo)

    def test_rejects_demo_evidence_and_negative_counts(self):
        for edit in (lambda m: m.update(mode="demo"),
                     lambda m: next(iter(m["backends"]["sage"]["cases"].values())).update(passes=-1)):
            with tempfile.TemporaryDirectory() as root:
                repo = copy_inputs(root)
                change_manifest(repo, edit)
                with self.assertRaises(AssertionError):
                    verify_catalog(repo)

    def test_optional_raw_audit_rejects_summary_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            manifest = json.loads((repo / "skills" / USE_CASE / "compatibility.json").read_text())
            receipt = {
                "mode": "live", "repetitions": 3, "rows": [], "summary": {},
                "source_hash": manifest["evidence"]["source_hash"],
                "fixtures": {USE_CASE: manifest["fixture_revision"]},
            }
            path = Path(root) / "raw.json"
            path.write_text(json.dumps(receipt))
            change_manifest(repo, lambda m: m["evidence"].update(sha256=sha256(path)))
            with self.assertRaisesRegex(AssertionError, "summary differs"):
                verify_catalog(repo, [path])

    def test_optional_raw_audit_rejects_unreferenced_or_tampered_receipt(self):
        with tempfile.TemporaryDirectory() as root:
            repo = copy_inputs(root)
            path = Path(root) / "unrelated.json"
            path.write_text("{}")
            with self.assertRaisesRegex(AssertionError, "not referenced"):
                verify_catalog(repo, [path])

    def test_migration_audit_rejects_missing_helper_hashes(self):
        for helpers in ({}, {"scripts/usecase_reference.py": sha256(REPO / "scripts/usecase_reference.py")}):
            with self.subTest(helpers=helpers), tempfile.TemporaryDirectory() as root:
                repo = copy_inputs(root)
                manifest = json.loads((repo / "skills" / USE_CASE / "compatibility.json").read_text())
                migration = manifest["migration"]
                proof = {field: migration[field] for field in (
                    "kind", "previous_runtime_revision", "runtime_revision",
                    "payload_and_policy_cases", "archived_response_replays", "paid_requests")}
                proof.update(identical=True, skill_count=26,
                             decision_contracts={USE_CASE: migration["contract_sha256"]},
                             reference_artifacts=helpers)
                path = Path(root) / "migration.json"
                path.write_text(json.dumps(proof))
                change_manifest(repo, lambda m: m["migration"].update(evidence_sha256=sha256(path)))
                with self.assertRaisesRegex(AssertionError, "incomplete migration helper set"):
                    verify_catalog(repo, migration_receipts=[path])

    def test_publisher_refuses_synthetic_evidence(self):
        with self.assertRaisesRegex(AssertionError, "live evidence"):
            build_manifest(REPO, REPO / "skills" / USE_CASE,
                           {"mode": "demo", "repetitions": 3}, "a" * 64, "https://example.com/run")


if __name__ == "__main__":
    unittest.main()
