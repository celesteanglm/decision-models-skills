"""Publication labels must remain tied to frozen live receipts and artifacts."""
import hashlib
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.verified_catalog import PROVIDERS, SLUGS, verify_catalog


REPO = Path(__file__).resolve().parents[1]
RECEIPTS = ("reports/community-recipes.json", "reports/community-core-regression.json")


def copy_verification_inputs(root):
    """Copy only the inputs consumed by verify_catalog into a disposable tree."""
    target = Path(root) / "repo"
    target.mkdir()
    for directory in ("src", "skills", "recipes"):
        shutil.copytree(REPO / directory, target / directory)
    reports = target / "reports"
    reports.mkdir()
    for relative in (*RECEIPTS, "reports/catalog.json", "reports/VERIFIED_CATALOG.md"):
        shutil.copy2(REPO / relative, target / relative)
    shutil.copy2(REPO / "README.md", target / "README.md")
    return target


def badge_slugs(path):
    return set(re.findall(
        r"https://img\.shields\.io/badge/([^\s)]+)-Working-brightgreen",
        path.read_text(encoding="utf-8"),
    ))


class VerifiedCatalogTests(unittest.TestCase):
    def test_catalog_labels_match_receipts_folders_artifacts_and_local_evidence(self):
        registry = verify_catalog(REPO)
        recipe_receipt = json.loads((REPO / RECEIPTS[0]).read_text(encoding="utf-8"))
        skill_receipt = json.loads((REPO / RECEIPTS[1]).read_text(encoding="utf-8"))

        self.assertEqual(registry["schema_version"], 1)
        self.assertEqual(registry["original_source_hash"], recipe_receipt["source_hash"])
        self.assertEqual(registry["original_source_hash"], skill_receipt["source_hash"])
        self.assertEqual(set(registry["recipes"]), {
            path.parent.name for path in (REPO / "recipes").glob("*/recipe.json")
        })
        self.assertEqual(set(registry["skills"]), {
            path.parent.parent.name for path in (REPO / "skills").glob("*/fixtures/acceptance.json")
        })

        for relative, expected_hash in registry["evidence_receipts"].items():
            actual_hash = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, relative)

        for relative, expected_hash in registry["verified_artifacts"].items():
            actual_hash = hashlib.sha256((REPO / relative).read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, relative)

        for kind, receipt in (("recipes", recipe_receipt), ("skills", skill_receipt)):
            for item_id, entry in registry[kind].items():
                with self.subTest(kind=kind, item=item_id):
                    statuses = {
                        provider: receipt["summary"][f"{provider}/{item_id}"]["status"]
                        for provider in PROVIDERS
                    }
                    working = [provider for provider in PROVIDERS
                               if statuses[provider] == "Working"]
                    self.assertTrue(working)
                    self.assertEqual(entry["statuses"], statuses)
                    self.assertEqual(entry["working_backends"], working)

                    folder = REPO / kind / item_id
                    fixtures = json.loads(
                        (folder / "fixtures/acceptance.json").read_text(encoding="utf-8")
                    )
                    fixture_hash = hashlib.sha256(
                        json.dumps(fixtures, sort_keys=True).encode()
                    ).hexdigest()
                    self.assertEqual(entry["fixture_revision"], fixture_hash)
                    self.assertEqual(entry["fixture_revision"], receipt["fixtures"][item_id])

                    skill_doc = folder / "SKILL.md"
                    compatibility = folder / "COMPATIBILITY.md"
                    skill_text = skill_doc.read_text(encoding="utf-8")
                    self.assertIn("[compatibility evidence](COMPATIBILITY.md)", skill_text)
                    self.assertTrue(compatibility.is_file())
                    self.assertEqual(badge_slugs(skill_doc), {SLUGS[p] for p in working})
                    self.assertEqual(badge_slugs(compatibility), {SLUGS[p] for p in working})

    def test_catalog_rejects_an_included_recipe_without_a_working_backend(self):
        with tempfile.TemporaryDirectory(prefix="catalog-no-working-") as temp:
            repo = copy_verification_inputs(temp)
            catalog_path = repo / "reports/catalog.json"
            registry = json.loads(catalog_path.read_text(encoding="utf-8"))
            recipe_id = next(iter(registry["recipes"]))
            registry["recipes"][recipe_id]["working_backends"] = []
            catalog_path.write_text(json.dumps(registry), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_catalog(repo)

    def test_catalog_rejects_a_working_badge_for_a_partial_backend(self):
        with tempfile.TemporaryDirectory(prefix="catalog-invalid-badge-") as temp:
            repo = copy_verification_inputs(temp)
            registry = json.loads((repo / "reports/catalog.json").read_text(encoding="utf-8"))
            recipe_id = next(
                item_id for item_id, entry in registry["recipes"].items()
                if any(status != "Working" for status in entry["statuses"].values())
            )
            entry = registry["recipes"][recipe_id]
            partial_provider = next(
                provider for provider, status in entry["statuses"].items()
                if status != "Working"
            )
            doc_path = repo / "recipes" / recipe_id / "SKILL.md"
            doc_path.write_text(
                doc_path.read_text(encoding="utf-8")
                + f"\n![Unsupported Working badge](https://img.shields.io/badge/{SLUGS[partial_provider]}-Working-brightgreen)\n",
                encoding="utf-8",
            )
            with self.assertRaises(AssertionError):
                verify_catalog(repo)

    def test_catalog_rejects_a_partial_backend_badge_in_the_public_readme(self):
        with tempfile.TemporaryDirectory(prefix="catalog-readme-badge-") as temp:
            repo = copy_verification_inputs(temp)
            registry = json.loads((repo / "reports/catalog.json").read_text(encoding="utf-8"))
            recipe_id = next(
                item_id for item_id, entry in registry["recipes"].items()
                if any(status != "Working" for status in entry["statuses"].values())
            )
            partial_provider = next(
                provider for provider, status in registry["recipes"][recipe_id]["statuses"].items()
                if status != "Working"
            )
            readme = repo / "README.md"
            lines = readme.read_text(encoding="utf-8").splitlines()
            row_index = next(i for i, line in enumerate(lines)
                             if line.startswith(f"| [{recipe_id}]("))
            row = lines[row_index]
            self.assertTrue(row.endswith("|"), row)
            lines[row_index] = (
                row[:-1].rstrip()
                + f" ![Unqualified Working badge](https://img.shields.io/badge/{SLUGS[partial_provider]}-Working-brightgreen) |"
            )
            readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_catalog(repo)

    def test_catalog_rejects_fixture_changes_and_recipe_folder_drift(self):
        with tempfile.TemporaryDirectory(prefix="catalog-fixture-drift-") as temp:
            repo = copy_verification_inputs(temp)
            recipe_id = next(iter(json.loads(
                (repo / "reports/catalog.json").read_text(encoding="utf-8")
            )["recipes"]))
            fixture_path = repo / "recipes" / recipe_id / "fixtures/acceptance.json"
            fixture_path.write_text(fixture_path.read_text(encoding="utf-8") + "\n ",
                                    encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_catalog(repo)

        with tempfile.TemporaryDirectory(prefix="catalog-folder-drift-") as temp:
            repo = copy_verification_inputs(temp)
            recipe_id = next(iter(json.loads(
                (repo / "reports/catalog.json").read_text(encoding="utf-8")
            )["recipes"]))
            shutil.rmtree(repo / "recipes" / recipe_id)
            with self.assertRaises(AssertionError):
                verify_catalog(repo)


if __name__ == "__main__":
    unittest.main()
