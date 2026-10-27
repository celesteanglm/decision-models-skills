"""Publish compact skill-local summaries from a retained live test run."""
import argparse
import hashlib
import json
from pathlib import Path

from decision_models.evaluation import source_hash
from scripts.verified_catalog import (
    artifacts, backend_results, compatibility_markdown,
    EVIDENCE_SCOPE, REFERENCE_HELPERS, runtime_revision, sha256,
)


def build_manifest(repo, folder, receipt, receipt_hash, evidence_url):
    assert receipt["mode"] == "live" and receipt["repetitions"] == 3, "live evidence required"
    fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
    fixture_revision = hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()
    assert receipt["fixtures"][folder.name] == fixture_revision, "fixtures differ from evaluated cases"
    backends = backend_results(receipt, folder.name)
    assert any(b["status"] == "Working" for b in backends.values()), "no Working backend"
    if "evaluated_artifacts" in receipt:
        assert set(receipt.get("reference_artifacts", {})) == REFERENCE_HELPERS, "incomplete reference helper set"
        assert receipt["runtime_revision"] == runtime_revision(repo), "reference runtime changed"
        assert receipt["evaluated_artifacts"][folder.name] == artifacts(folder), "scoped artifacts changed"
        for relative, digest in receipt["reference_artifacts"].items():
            assert sha256(repo / relative) == digest, "reference helper changed"
    result = {
        "schema_version": 1, "id": folder.name, "kind": folder.parent.name,
        "scope": dict(EVIDENCE_SCOPE),
        "mode": "live", "tested_at": receipt["updated_at"], "repetitions": 3,
        "fixture_revision": fixture_revision, "runtime_revision": runtime_revision(repo),
        "artifacts": artifacts(folder),
        "evidence": {"url": evidence_url, "sha256": receipt_hash, "source_hash": receipt["source_hash"]},
        "backends": backends,
    }
    if "reference_artifacts" in receipt:
        result["reference_artifacts"] = receipt["reference_artifacts"]
    return result


def write_manifest(folder, manifest):
    (folder / "compatibility.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (folder / "COMPATIBILITY.md").write_text(compatibility_markdown(manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--kind", choices=("skills", "recipes"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", help="publish only specified qualifying folders")
    parser.add_argument("--evidence-url", required=True, help="retained HTTPS CI artifact or versioned release asset")
    args = parser.parse_args()
    assert args.evidence_url.startswith("https://"), "HTTPS evidence URL required"
    receipt = json.loads(args.receipt.read_text())
    # Check before writing metadata, which itself participates in source_hash.
    assert receipt["source_hash"] == source_hash(args.repo) or "evaluated_artifacts" in receipt, "receipt is not for this checkout"
    receipt_hash = sha256(args.receipt)
    folders = sorted(p.parent for p in (args.repo / args.kind).glob("*/SKILL.md"))
    if args.ids:
        assert set(args.ids) <= {p.name for p in folders}, "unknown publication folder"
        folders = [p for p in folders if p.name in args.ids]
    pending = [(folder, build_manifest(args.repo, folder, receipt, receipt_hash, args.evidence_url)) for folder in folders]
    for folder, manifest in pending:
        write_manifest(folder, manifest)
    print(f"Published {len(pending)} local compatibility summaries. Run offline verification again.")


if __name__ == "__main__":
    main()
