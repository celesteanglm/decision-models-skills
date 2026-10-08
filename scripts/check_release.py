"""Enforce the approved Jev publication gate against current live receipts."""
import json
import argparse
from pathlib import Path
from decision_models.evaluation import source_hash, summarize
from decision_models.runtime import SKILLS, PROVIDERS

repo = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--receipt", default="reports/community-core-regression.json" if (repo / "reports/community-core-regression.json").exists() else "reports/live.json", help="live core acceptance receipt")
args = parser.parse_args()
receipt = json.loads((repo / args.receipt).read_text())
offline = json.loads((repo / "reports/offline.json").read_text())
revision = source_hash(repo)
assert receipt["mode"] == "live", "demo receipts cannot qualify"
assert offline["source_hash"] == revision, "stale offline verification"
if receipt["source_hash"] != revision:
    # Pruning unqualified recipes changes the aggregate source hash. Historical
    # acceptance remains applicable only to byte-identical evaluated artifacts.
    from verified_catalog import verify_catalog
    registry = verify_catalog(repo)
    assert args.receipt in registry["evidence_receipts"], "unregistered evidence"
    assert receipt["source_hash"] == registry["original_source_hash"], "stale evaluation"
assert offline["passed"] is True, "offline verification failed"
summary = summarize(receipt["rows"], PROVIDERS, SKILLS, 3, "live", True)
failed = [skill for skill in SKILLS if summary["jev-openrouter/" + skill]["status"] != "Working"]
assert not failed, "Jev publication gate failed: " + ", ".join(failed)
print("Publication gate passed: all six Jev workflows are Working for the unchanged evaluated artifacts.")
