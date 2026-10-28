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
REFERENCE_HELPERS = {"scripts/usecase_reference.py", "scripts/evaluate_usecases.py"}
REFERENCE_HELPERS_BY_MODALITY = {
    "text": REFERENCE_HELPERS,
    "image": {"scripts/image_reference.py", "scripts/evaluate_images.py"},
}
LAYOUT_ORIGINS = {
    "217f4374ee1a7ef7097129a726076206e379fe9815e17637d2c79df3a0015c59",
    "d06ec4e5406bd0d41be45941bda0105e19088a8189aace936f32f68761793af1",
    "1e870cc4c0e1bfc75e94e103f856bde5935fdbb73bd1b20401d189a5a8c361ff",
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def verify_integration_update(repo, manifest, audits):
    update = manifest["integration_update"]
    golden = json.loads((repo / "scripts/reference-contracts.json").read_text())
    assert update["kind"] == "offline-reference-upgrade" and update["paid_requests"] == 0, "invalid integration update"
    assert update["previous_runtime_revision"] == manifest["runtime_revision"] == golden["previous_runtime_revision"], "historical runtime differs"
    assert update["runtime_revision"] == runtime_revision(repo), "runtime changed since integration audit"
    assert update["golden_sha256"] == json_digest(golden), "integration golden changed"
    assert update["artifacts_sha256"] == json_digest(manifest["artifacts"]) == json_digest(golden["artifacts"][manifest["id"]]), "integration artifacts differ"
    assert update["previous_reference_artifacts"] == golden["previous_reference_artifacts"], "historical helpers differ"
    assert set(update["current_reference_artifacts"]) == set(golden["previous_reference_artifacts"]), "incomplete integration helper set"
    for relative, digest in update["current_reference_artifacts"].items():
        path = (repo / relative).resolve()
        assert path.is_relative_to(repo.resolve()) and sha256(path) == digest, "reference helper changed since integration audit"
    assert update["payload_and_policy_cases"] == len(golden["contracts"]) == golden["payload_and_policy_cases"], "incomplete integration contracts"
    assert update["actual_archived_response_replays"] == 2598 and update["deterministic_replays"] == 246, "incomplete integration replays"
    assert update["evidence_url"].startswith("https://") and re.fullmatch(r"[a-f0-9]{64}", update["evidence_sha256"]), "invalid integration evidence"
    if update["evidence_sha256"] in audits:
        proof = audits[update["evidence_sha256"]]
        assert proof["kind"] == "reference-upgrade-audit" and proof["identical"] is True, "integration behavior differs"
        for field in ("previous_runtime_revision", "runtime_revision", "previous_reference_artifacts",
                      "current_reference_artifacts", "payload_and_policy_cases", "actual_archived_response_replays",
                      "deterministic_replays", "paid_requests", "golden_sha256"):
            assert proof[field] == update[field], "integration summary differs from raw evidence"
        assert proof["artifacts"][manifest["id"]] == manifest["artifacts"], "integration proof artifacts differ"
        assert {Path(item["path"]).name: item["sha256"] for item in proof["receipts"]} == golden["receipt_sha256"], "integration receipt set differs"
    return update["previous_reference_artifacts"]


def runtime_revision(repo):
    digest = hashlib.sha256()
    for path in sorted((Path(repo) / "src").rglob("*.py")):
        digest.update(str(path.relative_to(repo)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def artifacts(folder):
    paths = set(folder.rglob("*.json"))
    paths.update(p for p in (folder / "images").rglob("*") if p.is_file())
    assert all(p.resolve().is_relative_to(folder.resolve()) for p in paths), "asset escapes skill folder"
    return {str(path.relative_to(folder)): sha256(path)
            for path in sorted(paths) if path.name != "compatibility.json"}


def decision_contract(folder):
    folder = Path(folder)
    value = {"fixtures": json.loads((folder / "fixtures/acceptance.json").read_text()),
             "examples": {p.name: json.loads(p.read_text()) for p in sorted((folder / "examples").glob("*.json"))}}
    if (folder / "decision.json").is_file():
        config = json.loads((folder / "decision.json").read_text())
        value["decision"] = {k: config[k] for k in ("id", "required_state_fields", "question", "policy")}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def badge(provider):
    return f"![{NAMES[provider]}: Working](https://img.shields.io/badge/{SLUGS[provider]}-Working-brightgreen)"


def backend_results(receipt, item_id):
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
    if "levanto-sage-v1.3" in manifest["backends"]["sage"]["resolved_models"]:
        lines += ["", "**Sage availability:** this v1.3 result is historical. On 2026-10-27 the live deployment advertised v1.4 and rejected v1.3. The recorded result does not qualify v1.4; use an explicitly evaluated version and configuration."]
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
            detail = "; ".join(failed) or "See the recorded service errors or incomplete coverage in compatibility.json."
            if backend["status"] == "Not tested":
                detail = "No evaluation results are recorded for this backend."
            lines.append(f"- **{NAMES[provider]} ({backend['status']}):** " + detail)
    if not failures:
        lines.append("All recorded checks passed on the listed backends.")
    evidence = manifest["evidence"]
    lines += ["", "## Evidence", "", "[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.",
              "", f"[Raw live test run]({evidence['url']}) is retained outside the main source tree for optional audit. Receipts can live at an immutable Git commit or a retained CI artifact; GitHub Releases are not required. Using the skill and running offline checks do not download this receipt.",
              "", f"Receipt SHA-256: {evidence['sha256']}.",
              f"Fixture revision: {manifest['fixture_revision']}.",
              f"Runtime revision: {manifest['runtime_revision']}."]
    if manifest.get("input_modality") == "image":
        lines += ["", "## Image reference scope", "", "This run sent actual local PNG pixels to Sage's public image API. JPEG and WebP input handling has offline contract coverage; those formats were not qualified by this live run. Other backends have no image results here and receive no Working label.",
                  "", "This image Choice API reports native selected-option probability without a separate confidence value. The frozen workflow uses a probability threshold of 0.80 and records confidence as unavailable. It recommends visibility only; it does not test enabled state, clickability, or application behavior.",
                  "", "The optional image runner reads image.json. The text runner rejects that schema rather than sending an image filename as text. No Python package or command is needed to follow the SKILL.md instructions with a vision-capable agent."]
        if manifest.get("development_history"):
            history = manifest["development_history"]
            lines += ["", "## Development runs", "", manifest["evaluation_notes"],
                      "", f"[Earlier results and frozen prompt revisions]({history['url']}) (SHA-256: {history['sha256']}). The first two runs were Partial; only the final configuration qualifies as Working."]
    elif manifest.get("reference_artifacts"):
        lines += ["", "## Recorded adapter configuration", "", "The additional reference-helper hashes in compatibility.json bind this result to the evaluated adapter settings. The new Sage checks explicitly selected v1.4 after the deployment rejected the historical v1.3 default. To reproduce an individual Sage case with the optional Python package, pass `--model levanto-sage-v1.4` to `python -m decision_models decide --config decision.json`. The SKILL.md instructions require no Python package or vendor runtime."]
    if manifest.get("migration"):
        migration = manifest["migration"]
        lines += ["", "## Layout verification", "", "The live results above predate the unified skills directory. An offline check of 936 provider-request and demo-policy contracts, plus 2,808 replays of archived native responses, confirmed identical requests, permissions, numerical gates, and recommendations after the path and naming changes. This migration made no paid requests and is not a new live evaluation.",
                  "", f"[Migration audit]({migration['evidence_url']}) (SHA-256: {migration['evidence_sha256']}) preserves the verification record and original runtime revision."]
    if manifest.get("integration_update"):
        update = manifest["integration_update"]
        lines += ["", "## Integration update", "",
                  "The current runners add external adapters and structured error handling. An offline comparison against the recorded source snapshot matched 948 request and policy contracts, 2,598 archived native responses, and 246 deterministic outcomes. The original models, test dates, fixtures, and thresholds above remain unchanged. This comparison made no provider calls and does not qualify a different model or an external adapter.",
                  "", f"[Runtime comparison audit]({update['evidence_url']}) (SHA-256: {update['evidence_sha256']})."]
    return "\n".join(lines) + "\n"


def verify_catalog(repo, receipts=(), migration_receipts=(), upgrade_receipts=()):
    repo = Path(repo)
    entries = {}
    skill_root = repo / "skills"
    readme = (repo / "README.md").read_text()
    revision = runtime_revision(repo)
    raw = {sha256(path): json.loads(Path(path).read_text()) for path in receipts}
    migrations = {sha256(path): json.loads(Path(path).read_text()) for path in migration_receipts}
    upgrades = {sha256(path): json.loads(Path(path).read_text()) for path in upgrade_receipts}
    used_migrations = set()
    used_upgrades = set()
    folders = sorted(p.parent for p in skill_root.glob("*/SKILL.md"))
    names = {p.name for p in folders}
    assert set(SKILLS) <= names, "general skill folders differ"
    configured = {p.parent.name for pattern in ("*/decision.json", "*/image.json") for p in skill_root.glob(pattern)}
    assert names - set(SKILLS) == configured, "decision configuration folders differ"
    assert {p.name for p in folders} == {p.parent.name for p in skill_root.glob("*/compatibility.json")}, "compatibility folders differ"
    for folder in folders:
        manifest = json.loads((folder / "compatibility.json").read_text())
        modality = manifest.get("input_modality", "text")
        assert modality in REFERENCE_HELPERS_BY_MODALITY, "unknown input modality"
        assert (folder / "image.json").is_file() == (modality == "image"), "image configuration differs"
        if modality == "image":
            image_config = json.loads((folder / "image.json").read_text())
            assert image_config["schema_version"] == 2 and image_config["input_modality"] == "image", "invalid image configuration"
            assert not (folder / "decision.json").exists(), "multiple reference configurations"
            if image_config.get("evaluation_notes"):
                assert manifest.get("evaluation_notes") == image_config["evaluation_notes"], "development notes differ"
                history = manifest["development_history"]
                assert history["url"].startswith("https://") and re.fullmatch(r"[a-f0-9]{64}", history["sha256"]), "invalid development history"
        assert manifest["schema_version"] == 1 and manifest["id"] == folder.name and manifest["kind"] == "skills"
        assert manifest["mode"] == "live" and manifest["repetitions"] == 3, "synthetic evidence cannot qualify"
        assert manifest["scope"] == EVIDENCE_SCOPE, "reference evidence cannot qualify instruction-only use"
        historical_helpers = None
        if "integration_update" in manifest:
            historical_helpers = verify_integration_update(repo, manifest, upgrades)
            used_upgrades.add(manifest["integration_update"]["evidence_sha256"])
        else:
            assert manifest["runtime_revision"] == revision, "runtime changed since evaluation"
        if manifest["evidence"]["sha256"] in LAYOUT_ORIGINS:
            assert "migration" in manifest, "missing layout migration"
        if "migration" in manifest:
            migration = manifest["migration"]
            contract_revision = decision_contract(folder)
            assert migration["kind"] == "layout-and-naming-only" and migration["paid_requests"] == 0, "invalid layout migration"
            assert migration["runtime_revision"] == manifest["runtime_revision"], "migration runtime changed"
            assert migration["contract_sha256"] == contract_revision, "migrated decision contract changed"
            assert migration["payload_and_policy_cases"] == 936 and migration["archived_response_replays"] == 2808, "incomplete migration verification"
            assert migration["evidence_url"].startswith("https://") and re.fullmatch(r"[a-f0-9]{64}", migration["evidence_sha256"]), "invalid migration evidence"
            assert re.fullmatch(r"[a-f0-9]{64}", migration["previous_runtime_revision"]), "missing historical runtime revision"
            proof_hash = migration["evidence_sha256"]
            used_migrations.add(proof_hash)
            if proof_hash in migrations:
                proof = migrations[proof_hash]
                for field in ("kind", "previous_runtime_revision", "runtime_revision", "payload_and_policy_cases", "archived_response_replays", "paid_requests"):
                    assert proof[field] == migration[field], "migration summary differs from raw evidence"
                assert proof["identical"] is True and proof["skill_count"] == len(proof["decision_contracts"]), "incomplete migration evidence"
                assert proof["decision_contracts"][folder.name] == contract_revision, "migration contract differs from raw evidence"
                assert set(proof["reference_artifacts"]) == REFERENCE_HELPERS, "incomplete migration helper set"
                for relative, digest in proof["reference_artifacts"].items():
                    observed = historical_helpers.get(relative) if historical_helpers else sha256(repo / relative)
                    assert relative in REFERENCE_HELPERS and observed == digest, "migration helper changed"
        if "reference_artifacts" in manifest:
            assert set(manifest["reference_artifacts"]) == REFERENCE_HELPERS_BY_MODALITY[modality], "incomplete reference helper set"
        for relative, digest in manifest.get("reference_artifacts", {}).items():
            path = (repo / relative).resolve()
            observed = historical_helpers.get(relative) if historical_helpers else sha256(path)
            assert path.is_relative_to(repo.resolve()) and path.is_file() and observed == digest, "reference helper changed since evaluation"
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
        if modality == "image":
            assert working == ["sage"], "image backend has no evaluated adapter"
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
        assert f"](skills/{folder.name}/SKILL.md)" in readme, f"skill missing from README: {folder.name}"
        entries[folder.name] = {"working_backends": working, "statuses": statuses, "manifest": manifest}
    linked = re.findall(r"\]\(skills/([^/]+)/SKILL\.md\)", readme)
    assert set(linked) <= set(entries), "README links to an unknown skill"
    listed = re.findall(r"^\|\s*\[[^\]]+\]\(skills/([^/]+)/SKILL\.md\)\s*\|", readme, re.MULTILINE)
    assert set(listed) == set(entries) and len(listed) == len(set(listed)), "README catalog differs from installed folders"
    expected_digests = {entry["manifest"]["evidence"]["sha256"] for entry in entries.values()}
    assert set(raw) <= expected_digests, "raw receipt not referenced by a published skill"
    assert set(migrations) <= used_migrations, "migration receipt not referenced by a published skill"
    assert set(upgrades) <= used_upgrades, "integration receipt not referenced by a published skill"
    return {"skills": entries}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify recorded backend results and optional audit receipts.")
    parser.add_argument("--receipt", action="append", default=[], help="optional downloaded raw receipt to audit (repeatable)")
    parser.add_argument("--migration-receipt", action="append", default=[], help="optional downloaded layout audit to verify (repeatable)")
    parser.add_argument("--upgrade-receipt", action="append", default=[], help="optional downloaded runtime comparison audit (repeatable)")
    args = parser.parse_args()
    result = verify_catalog(Path(__file__).resolve().parents[1], args.receipt, args.migration_receipt, args.upgrade_receipt)
    print(f"Verified local summaries for {len(result['skills'])} skills.")
