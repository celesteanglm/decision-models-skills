"""Publish compact skill-local summaries from a retained live test run."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from decision_models.evaluation import source_hash
from scripts.verified_catalog import (
    artifacts, backend_results, badge, compatibility_markdown,
    PROVIDERS, runtime_revision, sha256,
)


def build_manifest(repo, folder, receipt, receipt_hash, evidence_url):
    assert receipt["mode"] == "live" and receipt["repetitions"] == 3, "live evidence required"
    fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
    fixture_revision = hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()
    assert receipt["fixtures"][folder.name] == fixture_revision, "fixtures differ from evaluated cases"
    backends = backend_results(receipt, folder.name)
    assert any(b["status"] == "Working" for b in backends.values()), "no Working backend"
    return {
        "schema_version": 1, "id": folder.name, "kind": folder.parent.name,
        "mode": "live", "tested_at": receipt["updated_at"], "repetitions": 3,
        "fixture_revision": fixture_revision, "runtime_revision": runtime_revision(repo),
        "artifacts": artifacts(folder),
        "evidence": {"url": evidence_url, "sha256": receipt_hash, "source_hash": receipt["source_hash"]},
        "backends": backends,
    }


def write_manifest(folder, manifest):
    (folder / "compatibility.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (folder / "COMPATIBILITY.md").write_text(compatibility_markdown(manifest))
    skill = folder / "SKILL.md"
    working = [p for p in PROVIDERS if manifest["backends"][p]["status"] == "Working"]
    text, count = re.subn(r"^\*\*Working with:\*\*.*$",
                         "**Working with:** " + " ".join(badge(p) for p in working),
                         skill.read_text(), flags=re.MULTILINE)
    assert count == 1, "skill needs one Working-with line"
    skill.write_text(text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--kind", choices=("skills", "recipes"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--evidence-url", required=True, help="retained HTTPS CI artifact or versioned release asset")
    args = parser.parse_args()
    assert args.evidence_url.startswith("https://"), "HTTPS evidence URL required"
    receipt = json.loads(args.receipt.read_text())
    # Check before writing metadata, which itself participates in source_hash.
    assert receipt["source_hash"] == source_hash(args.repo), "receipt is not for this checkout"
    receipt_hash = sha256(args.receipt)
    pending = [(folder, build_manifest(args.repo, folder, receipt, receipt_hash, args.evidence_url))
               for folder in sorted(p.parent for p in (args.repo / args.kind).glob("*/SKILL.md"))]
    for folder, manifest in pending:
        write_manifest(folder, manifest)
    print(f"Published {len(pending)} local compatibility summaries. Run offline verification again.")


if __name__ == "__main__":
    main()
