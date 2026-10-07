"""Enforce the approved Jev publication gate against current live receipts."""
import json
from pathlib import Path
from decision_models.evaluation import source_hash, summarize
from decision_models.runtime import SKILLS, PROVIDERS

repo = Path(__file__).resolve().parents[1]
receipt = json.loads((repo / "reports/live.json").read_text())
offline = json.loads((repo / "reports/offline.json").read_text())
revision = source_hash(repo)
assert receipt["mode"] == "live", "demo receipts cannot qualify"
assert receipt["source_hash"] == offline["source_hash"] == revision, "stale verification"
assert offline["passed"] is True, "offline verification failed"
summary = summarize(receipt["rows"], PROVIDERS, SKILLS, 3, "live", True)
failed = [skill for skill in SKILLS if summary["jev-openrouter/" + skill]["status"] != "Working"]
assert not failed, "Jev publication gate failed: " + ", ".join(failed)
print("Publication gate passed: all six Jev workflows are Working on the current revision.")
