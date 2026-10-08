"""Enforce the six-core-workflow Jev publication gate from local summaries."""
import argparse
import json
from pathlib import Path

from decision_models.evaluation import source_hash
from decision_models.runtime import SKILLS
from verified_catalog import verify_catalog


def main():
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", action="append", default=[],
                        help="optional downloaded raw evidence to audit (repeatable)")
    args = parser.parse_args()
    offline = json.loads((repo / "reports/offline.json").read_text())
    assert offline["passed"] is True and offline["source_hash"] == source_hash(repo), "stale offline verification"
    registry = verify_catalog(repo, args.receipt)
    failed = [skill for skill in SKILLS if registry["skills"][skill]["statuses"]["jev-openrouter"] != "Working"]
    assert not failed, "Jev publication gate failed: " + ", ".join(failed)
    print("Publication gate passed: all six Jev core workflows are Working for the unchanged evaluated artifacts.")


if __name__ == "__main__":
    main()
