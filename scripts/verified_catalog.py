"""Verify published labels against immutable live evidence and unchanged artifacts."""
import hashlib
import json
from pathlib import Path
import re

from decision_models.evaluation import summarize

PROVIDERS = ("jev-openrouter", "openai-decisions", "sage")
SLUGS = {"jev-openrouter": "Jev%20%2F%20OpenRouter", "openai-decisions": "Decisions%20API", "sage": "Sage"}
NAMES = {"jev-openrouter": "Jev / OpenRouter", "openai-decisions": "Decisions API", "sage": "Sage"}


def artifact_paths(repo):
    return sorted([*repo.joinpath("src").rglob("*.py"),
                   *repo.joinpath("skills").rglob("*.json"),
                   *repo.joinpath("recipes").rglob("*.json")])


def badge(provider):
    return f"![{NAMES[provider]}: Working](https://img.shields.io/badge/{SLUGS[provider]}-Working-brightgreen)"


def verify_catalog(repo):
    repo = Path(repo)
    registry = json.loads((repo / "reports/catalog.json").read_text())
    assert registry["schema_version"] == 1
    paths = artifact_paths(repo)
    assert {str(p.relative_to(repo)) for p in paths} == set(registry["verified_artifacts"]), "artifact scope changed"
    for path in paths:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == registry["verified_artifacts"][str(path.relative_to(repo))], f"unverified artifact: {path.name}"
    for filename, digest in registry["evidence_receipts"].items():
        assert hashlib.sha256((repo / filename).read_bytes()).hexdigest() == digest, "historical receipt changed"
    for kind, receipt_name in (("recipes", "community-recipes.json"), ("skills", "community-core-regression.json")):
        receipt = json.loads((repo / "reports" / receipt_name).read_text())
        assert receipt["mode"] == "live" and receipt["source_hash"] == registry["original_source_hash"]
        summaries = summarize(receipt["rows"], PROVIDERS, list(receipt["fixtures"]), 3, "live", True)
        actual = {p.parent.parent.name for p in (repo / kind).glob("*/fixtures/acceptance.json")}
        assert actual == set(registry[kind]), f"{kind} catalog differs from installed folders"
        for rid, entry in registry[kind].items():
            statuses = {p: summaries[p + "/" + rid]["status"] for p in PROVIDERS}
            working = [p for p in PROVIDERS if statuses[p] == "Working"]
            assert working, f"{rid} has no Working backend"
            assert entry["statuses"] == statuses and entry["working_backends"] == working, f"unsupported labels: {rid}"
            fixtures = json.loads((repo / kind / rid / "fixtures/acceptance.json").read_text())
            digest = hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()
            assert digest == entry["fixture_revision"] == receipt["fixtures"][rid], f"fixtures changed: {rid}"
            skill = (repo / kind / rid / "SKILL.md").read_text()
            labels = re.findall(r"https://img\.shields\.io/badge/([^\s)]+)-Working-brightgreen", skill)
            assert set(labels) == {SLUGS[p] for p in working}, f"badge labels differ: {rid}"
            assert "[compatibility evidence](COMPATIBILITY.md)" in skill
            compatibility = (repo / kind / rid / "COMPATIBILITY.md").read_text()
            labels = re.findall(r"https://img\.shields\.io/badge/([^\s)]+)-Working-brightgreen", compatibility)
            assert set(labels) == {SLUGS[p] for p in working}, f"compatibility labels differ: {rid}"
            for page in (["README.md", "reports/VERIFIED_CATALOG.md"] if kind == "recipes" else ["reports/VERIFIED_CATALOG.md"]):
                rows = [line for line in (repo / page).read_text().splitlines() if line.startswith("| [" + rid + "](")]
                assert len(rows) == 1, f"catalog row missing or duplicated: {rid}"
                labels = re.findall(r"https://img\.shields\.io/badge/([^\s)]+)-Working-brightgreen", rows[0])
                assert set(labels) == {SLUGS[p] for p in working}, f"published labels differ: {rid}"
    return registry


if __name__ == "__main__":
    result = verify_catalog(Path(__file__).resolve().parents[1])
    print(f"Verified {len(result['recipes'])} recipes and {len(result['skills'])} core skills; labels match live evidence.")
