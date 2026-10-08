"""Check skill-local compatibility summaries without downloading raw test runs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from decision_models.evaluation import summarize
from decision_models.runtime import SKILLS

PROVIDERS = ("jev-openrouter", "openai-decisions", "sage")
SLUGS = {"jev-openrouter": "Jev%20%2F%20OpenRouter", "openai-decisions": "Decisions%20API", "sage": "Sage"}
NAMES = {"jev-openrouter": "Jev / OpenRouter", "openai-decisions": "Decisions API", "sage": "Sage"}
EVIDENCE_SCOPE = {"reference_implementation": "python-native-apis", "instruction_only": "Not evaluated"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def runtime_revision(repo):
    digest = hashlib.sha256()
    for path in sorted((Path(repo) / "src").rglob("*.py")):
        digest.update(str(path.relative_to(repo)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def artifacts(folder):
    return {str(path.relative_to(folder)): sha256(path)
            for path in sorted(folder.rglob("*.json")) if path.name != "compatibility.json"}


def badge(provider):
    return f"![{NAMES[provider]}: Working](https://img.shields.io/badge/{SLUGS[provider]}-Working-brightgreen)"


def backend_results(receipt, item_id):
    """Retain acceptance counts and failure reasons, without prompts or outputs."""
    result = {}
    for provider in PROVIDERS:
        recorded = receipt["summary"].get(provider + "/" + item_id, {})
        summary = summarize(receipt["rows"], [provider], [item_id], 3,
                            receipt["mode"], recorded.get("offline_passed") is True)[provider + "/" + item_id]
        cases = {}
        for case_id, case in summary["cases"].items():
            rows = [r for r in receipt["rows"] if r["provider"] == provider
                    and r["skill"] == item_id and r["case_id"] == case_id]
            cases[case_id] = {k: case[k] for k in ("category", "passes", "runs", "errors")}
            cases[case_id]["failures"] = dict(Counter(reason for row in rows for reason in row.get("failures", [])))
        result[provider] = {
            "status": summary["status"], "offline_passed": summary["offline_passed"],
            "resolved_models": summary["resolved_models"], "live_requests": summary["live_requests"],
            "live_outputs": sum(r.get("output", {}).get("source") == "live" for r in receipt["rows"]
                                if r["provider"] == provider and r["skill"] == item_id),
            "safety_violations": summary["safety_violations"], "errors": summary["errors"],
            "stable_cases": summary["stable_cases"], "cases": cases,
        }
    return result


def qualification(backend, fixtures):
    cases = backend["cases"]
    categories = {case["id"]: case["category"] for case in fixtures}
    assert set(cases) <= set(categories), "unknown compatibility case"
    for case_id, case in cases.items():
        assert case["category"] == categories[case_id], "case category differs"
        for key in ("passes", "runs", "errors"):
            assert type(case[key]) is int and 0 <= case[key] <= 3, "invalid case counts"
        assert case["passes"] <= case["runs"] and case["errors"] <= case["runs"], "invalid pass/error counts"
    assert type(backend["live_outputs"]) is int and 0 <= backend["live_outputs"] <= sum(c["runs"] for c in cases.values())
    assert type(backend["offline_passed"]) is bool
    assert type(backend["safety_violations"]) is int and backend["safety_violations"] >= 0
    assert all(type(count) is int and count > 0 for count in backend["errors"].values())
    assert sum(backend["errors"].values()) == sum(c["errors"] for c in cases.values()), "error counts differ"
    complete = len(cases) == 12 and all(c["runs"] == 3 for c in cases.values())
    clear_ok = sum(c["passes"] >= 2 for c in cases.values() if c["category"] == "clear")
    edge_ok = all(c["passes"] == 3 for c in cases.values() if c["category"] != "clear")
    live = backend["live_outputs"] > 0
    if not cases:
        return "Not tested"
    if complete and clear_ok == 8 and edge_ok and not backend["errors"] and not backend["safety_violations"] and backend["offline_passed"] and live:
        return "Working"
    return "Blocked" if backend["errors"] and not live else "Partial"


def compatibility_markdown(manifest):
    working = [p for p in PROVIDERS if manifest["backends"][p]["status"] == "Working"]
    lines = ["# Recorded reference implementation results",
             "", "These runs tested the optional Python reference implementation against native decision APIs. They did not evaluate the model-agnostic SKILL.md instructions on an agent's current model. No listed provider, Python package, or CLI is required to use the skill.",
             "", "**Reference implementation — Working with:** " + " ".join(badge(p) for p in working),
             "", "| Backend | Result | Tested model | Passed checks |",
             "|---|---|---|---|"]
    for provider in PROVIDERS:
        backend = manifest["backends"][provider]
        status = "Not qualified (Partial)" if backend["status"] == "Partial" else backend["status"]
        passed = sum(c["passes"] for c in backend["cases"].values())
        runs = sum(c["runs"] for c in backend["cases"].values())
        lines.append(f"| {NAMES[provider]} | {status} | {', '.join(backend['resolved_models']) or 'Not tested'} | {passed}/{runs} |")
    lines += ["", f"Tested: {manifest['tested_at']}. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.",
              "", "Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.",
              "", "## Failures and unsupported backends", ""]
    failures = False
    for provider in PROVIDERS:
        backend = manifest["backends"][provider]
        failed = [f"{case_id}: {case['passes']}/{case['runs']} passed ({', '.join(case['failures']) or 'service error'})"
                  for case_id, case in backend["cases"].items() if case["passes"] != case["runs"]]
        if failed or backend["status"] != "Working":
            failures = True
            lines.append(f"- **{NAMES[provider]} ({backend['status']}):** " + ("; ".join(failed) or "See the recorded service errors or incomplete coverage in compatibility.json."))
    if not failures:
        lines.append("All recorded checks passed on the listed backends.")
    evidence = manifest["evidence"]
    lines += ["", "## Evidence", "", "[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.",
              "", f"[Raw live test run]({evidence['url']}) is retained outside the current source tree. Historical runs remain available at an immutable commit; new runs should use a CI artifact or versioned release asset.",
              "", f"Receipt SHA-256: {evidence['sha256']}.",
              f"Fixture revision: {manifest['fixture_revision']}.",
              f"Runtime revision: {manifest['runtime_revision']}."]
    return "\n".join(lines) + "\n"


def verify_catalog(repo, receipts=()):
    """Offline consistency checks; optionally audit against downloaded raw runs."""
    repo = Path(repo)
    registry = {"skills": {}, "recipes": {}}
    revision = runtime_revision(repo)
    raw = {sha256(path): json.loads(Path(path).read_text()) for path in receipts}
    for kind in registry:
        folders = sorted(p.parent for p in (repo / kind).glob("*/SKILL.md"))
        if kind == "skills":
            assert {p.name for p in folders} == set(SKILLS), "core skill folders differ"
        else:
            assert folders, "no use-case skills"
            assert {p.name for p in folders} == {p.parent.name for p in (repo / kind).glob("*/recipe.json")}, "recipe folders differ"
        assert {p.name for p in folders} == {p.parent.name for p in (repo / kind).glob("*/compatibility.json")}, "compatibility folders differ"
        for folder in folders:
            manifest = json.loads((folder / "compatibility.json").read_text())
            assert manifest["schema_version"] == 1 and manifest["id"] == folder.name and manifest["kind"] == kind
            assert manifest["mode"] == "live" and manifest["repetitions"] == 3, "synthetic evidence cannot qualify"
            assert manifest["scope"] == EVIDENCE_SCOPE, "reference evidence cannot qualify instruction-only use"
            assert manifest["runtime_revision"] == revision, "runtime changed since evaluation"
            assert manifest["artifacts"] == artifacts(folder), f"unverified artifacts: {folder.name}"
            fixtures = json.loads((folder / "fixtures/acceptance.json").read_text())
            assert len(fixtures) == 12 and Counter(c["category"] for c in fixtures) == {"clear": 8, "ambiguous": 2, "adversarial": 2}
            assert len({c["id"] for c in fixtures}) == 12
            assert manifest["fixture_revision"] == hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest()
            evidence = manifest["evidence"]
            assert evidence["url"].startswith("https://") and re.fullmatch(r"[a-f0-9]{64}", evidence["sha256"])
            assert re.fullmatch(r"[a-f0-9]{64}", evidence["source_hash"]) and manifest["tested_at"]
            assert set(manifest["backends"]) == set(PROVIDERS)
            statuses = {p: qualification(manifest["backends"][p], fixtures) for p in PROVIDERS}
            assert statuses == {p: manifest["backends"][p]["status"] for p in PROVIDERS}, "unsupported status"
            working = [p for p in PROVIDERS if statuses[p] == "Working"]
            assert working, f"{folder.name} has no Working backend"
            if evidence["sha256"] in raw:
                receipt = raw[evidence["sha256"]]
                assert receipt["source_hash"] == evidence["source_hash"]
                assert receipt["mode"] == "live" and receipt["repetitions"] == 3
                assert receipt["fixtures"][folder.name] == manifest["fixture_revision"]
                assert manifest["backends"] == backend_results(receipt, folder.name), "summary differs from raw evidence"
            skill = (folder / "SKILL.md").read_text()
            labels = re.findall(r"https://img\.shields\.io/badge/([^\s)]+)-Working-brightgreen", skill)
            assert not labels, f"unsupported badge in model-agnostic instructions: {folder.name}"
            assert "[compatibility evidence](COMPATIBILITY.md)" in skill
            assert (folder / "COMPATIBILITY.md").read_text() == compatibility_markdown(manifest), f"stale compatibility page: {folder.name}"
            assert f"]({kind}/{folder.name}/SKILL.md)" in (repo / "README.md").read_text(), f"skill missing from README: {folder.name}"
            registry[kind][folder.name] = {"working_backends": working, "statuses": statuses, "manifest": manifest}
        listed = re.findall(r"\]\(" + kind + r"/([^/]+)/SKILL\.md\)", (repo / "README.md").read_text())
        assert set(listed) == set(registry[kind]) and len(listed) == len(set(listed)), "README catalog differs from installed folders"
    expected_digests = {entry["manifest"]["evidence"]["sha256"] for entries in registry.values() for entry in entries.values()}
    assert set(raw) <= expected_digests, "raw receipt not referenced by a published skill"
    return registry


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", action="append", default=[], help="optional downloaded raw receipt to audit (repeatable)")
    args = parser.parse_args()
    result = verify_catalog(Path(__file__).resolve().parents[1], args.receipt)
    print(f"Verified local summaries for {len(result['recipes'])} use-case skills and {len(result['skills'])} core skills.")
