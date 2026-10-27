import argparse
import hashlib
import json
from pathlib import Path

from decision_models.evaluation import source_hash
from scripts.verified_catalog import (
    artifacts, backend_results, compatibility_markdown,
    EVIDENCE_SCOPE, LAYOUT_ORIGINS, REFERENCE_HELPERS_BY_MODALITY, runtime_revision, sha256,
    json_digest, verify_integration_update,
)


def build_manifest(repo, folder, receipt, receipt_hash, evidence_url, *, history_url=None, history_hash=None):
    assert receipt["mode"] == "live" and receipt["repetitions"] == 3, "live evidence required"
    assert receipt_hash not in LAYOUT_ORIGINS, "historical receipts require the recorded layout migration"
    fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
    fixture_revision = hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()
    assert receipt["fixtures"][folder.name] == fixture_revision, "fixtures differ from evaluated cases"
    backends = backend_results(receipt, folder.name)
    assert any(b["status"] == "Working" for b in backends.values()), "no Working backend"
    if "evaluated_artifacts" in receipt:
        modality = receipt.get("input_modality", "text")
        assert modality in REFERENCE_HELPERS_BY_MODALITY, "unknown input modality"
        assert set(receipt.get("reference_artifacts", {})) == REFERENCE_HELPERS_BY_MODALITY[modality], "incomplete reference helper set"
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
    if receipt.get("input_modality") == "image":
        result["input_modality"] = "image"
        notes = json.loads((folder / "image.json").read_text()).get("evaluation_notes")
        if notes:
            assert history_url and history_url.startswith("https://") and history_hash, "development history is required"
            result["evaluation_notes"] = notes
            result["development_history"] = {"url": history_url, "sha256": history_hash}
    return result


def apply_integration_update(repo, receipt_path, evidence_url):
    assert evidence_url.startswith("https://"), "HTTPS evidence URL required"
    proof = json.loads(receipt_path.read_text())
    proof_hash = sha256(receipt_path)
    pending = []
    for path in sorted((repo / "skills").glob("*/compatibility.json")):
        manifest = json.loads(path.read_text())
        assert manifest["artifacts"] == artifacts(path.parent), "reference artifacts changed"
        manifest["integration_update"] = dict(
            {key: proof[key] for key in ("previous_runtime_revision", "runtime_revision",
                "previous_reference_artifacts", "current_reference_artifacts", "golden_sha256",
                "payload_and_policy_cases", "actual_archived_response_replays", "deterministic_replays", "paid_requests")},
            kind="offline-reference-upgrade", artifacts_sha256=json_digest(manifest["artifacts"]),
            evidence_url=evidence_url, evidence_sha256=proof_hash)
        verify_integration_update(repo, manifest, {proof_hash: proof})
        pending.append((path.parent, manifest))
    assert set(proof["artifacts"]) == {folder.name for folder, _ in pending}, "incomplete integration skill coverage"
    for folder, manifest in pending:
        write_manifest(folder, manifest)
    return len(pending)


def write_manifest(folder, manifest):
    (folder / "compatibility.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (folder / "COMPATIBILITY.md").write_text(compatibility_markdown(manifest))


def main():
    parser = argparse.ArgumentParser(description="Record compatibility summaries from a retained live test run.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--ids", nargs="+", help="publish only specified qualifying folders")
    parser.add_argument("--evidence-url", help="retained HTTPS audit URL, such as an immutable Git commit or CI artifact")
    parser.add_argument("--upgrade-receipt", type=Path, help="offline comparison proof; preserves existing live results")
    parser.add_argument("--upgrade-url", help="immutable HTTPS location of the offline comparison proof")
    parser.add_argument("--history-receipt", type=Path, help="retained development history for revised image instructions")
    parser.add_argument("--history-url", help="immutable HTTPS location of the development history")
    args = parser.parse_args()
    if args.upgrade_receipt:
        assert args.upgrade_url and not args.receipt and not args.ids, "an integration update requires its URL and all existing skills"
        count = apply_integration_update(args.repo, args.upgrade_receipt, args.upgrade_url)
        print(f"Recorded {count} offline integration comparisons; live results and dates are unchanged.")
        return
    assert args.receipt and args.evidence_url, "live receipt and evidence URL required"
    assert not args.upgrade_url, "upgrade URL requires an upgrade receipt"
    assert args.evidence_url.startswith("https://"), "HTTPS evidence URL required"
    receipt = json.loads(args.receipt.read_text())
    assert receipt["source_hash"] == source_hash(args.repo) or "evaluated_artifacts" in receipt, "receipt is not for this checkout"
    receipt_hash = sha256(args.receipt)
    assert bool(args.history_receipt) == bool(args.history_url), "history receipt and URL must be supplied together"
    history_hash = None
    if args.history_receipt:
        history = json.loads(args.history_receipt.read_text())
        assert history["final_receipt_sha256"] == receipt_hash, "history refers to another final evaluation"
        assert history["fixtures"] == receipt["fixtures"], "history fixtures differ"
        history_hash = sha256(args.history_receipt)
    folders = sorted(p.parent for p in (args.repo / "skills").glob("*/SKILL.md"))
    if args.ids:
        assert set(args.ids) <= {p.name for p in folders}, "unknown publication folder"
        folders = [p for p in folders if p.name in args.ids]
    pending = [(folder, build_manifest(args.repo, folder, receipt, receipt_hash, args.evidence_url,
                history_url=args.history_url, history_hash=history_hash)) for folder in folders]
    for folder, manifest in pending:
        write_manifest(folder, manifest)
    print(f"Published {len(pending)} local compatibility summaries. Run offline verification again.")


if __name__ == "__main__":
    main()
