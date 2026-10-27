"""Freeze and verify offline reference-runtime compatibility evidence.

Baseline export is intentionally tied to the frozen checkout and runs in a
separate interpreter with that checkout's ``src`` first on ``PYTHONPATH``.
No provider transport is used by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


BASELINE_COMMIT = "0d93d0e10c177e1f0341284de1a1c3cf2745aa46"
OLD_RUNTIME_REVISION = "90c3e703d2a656d7aed3087ef4a4f07b130f1c03de7de8af4d72265eaeb823bb"
OLD_HELPER_SHA256 = {
    "scripts/usecase_reference.py": "358b4c8623376f31b800333b5c102507c2ea038d86fa0431bbe30fd08d954d1f",
    "scripts/evaluate_usecases.py": "c7087d9bd7131c015a3453dc6e33d6fda6fcc4b980f4d384486fcc46774d5b29",
    "scripts/image_reference.py": "316045eb4a83bb718c8be19fe53c5b605378ea74a5c2bf83ade8f1dc059d6f5e",
    "scripts/evaluate_images.py": "05a7aade07f9d11a82f3cf1dfc3745cd0db8fa92471ced5b206050f4b9ed93ec",
}
RECEIPTS = (
    "reports/general-skills-regression.json",
    "reports/community-use-cases.json",
    "reports/sage-published-live-20261027.json",
    "reports/sage-images-live-20261027-r3.json",
)
TEXT_PROVIDERS = ("jev-openrouter", "openai-decisions", "sage")
HELPERS = (
    "scripts/usecase_reference.py",
    "scripts/evaluate_usecases.py",
    "scripts/image_reference.py",
    "scripts/evaluate_images.py",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_revision(repo: Path) -> str:
    h = hashlib.sha256()
    for path in sorted((repo / "src").rglob("*.py")):
        h.update(str(path.relative_to(repo)).encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def reference_artifacts(repo: Path) -> dict[str, str]:
    return {name: file_digest(repo / name) for name in HELPERS}


def skill_artifacts(folder: Path) -> dict[str, str]:
    paths = set(folder.rglob("*.json"))
    paths.update(path for path in (folder / "images").rglob("*") if path.is_file())
    result = {}
    for path in sorted(paths):
        if path.name == "compatibility.json":
            continue
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError(f"skill asset escapes folder: {path}")
        result[str(path.relative_to(folder))] = file_digest(path)
    return result


def _load_helper(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load reference helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _worker(repo: Path) -> dict[str, Any]:
    """Run only inside an isolated process whose PYTHONPATH is repo/src."""
    repo = repo.resolve()
    import decision_models
    if not Path(decision_models.__file__).resolve().is_relative_to((repo / "src").resolve()):
        raise RuntimeError("baseline worker imported decision_models outside selected source tree")
    from decision_models.contracts import DecisionError
    from decision_models.runtime import adapter_for, execute as execute_builtin, workflow_for
    from decision_models.use_cases import execute_use_case, prepare_use_case

    usecase_ref = _load_helper(repo / "scripts/usecase_reference.py", "_audit_usecase_reference")
    image_ref = _load_helper(repo / "scripts/image_reference.py", "_audit_image_reference")
    skills_root = repo / "skills"
    contract_rows: list[dict[str, Any]] = []
    folders = sorted(path for path in skills_root.iterdir() if (path / "SKILL.md").is_file())
    for folder in folders:
        if (folder / "decision.json").is_file():
            config = usecase_ref.read_config(folder)
            cases = json.loads((folder / "fixtures/acceptance.json").read_text(encoding="utf-8"))
            for provider in TEXT_PROVIDERS:
                scoped = folder.name in ("study-tool-selection", "research-enrichment-gate")
                adapter = usecase_ref.usecase_adapter(provider) if scoped else adapter_for(provider)
                for case in cases:
                    data = case["input"]
                    valid = data.get("permission_granted") is True and prepare_use_case(config, data) is None
                    payload_hash = None
                    if valid:
                        payload = adapter.build_payload(data["state"], [config["question"]], adapter.default_model)
                        payload_hash = digest(payload)
                    try:
                        kwargs = {"mode": "demo", "demo_answers": case.get("demo_answers")}
                        output = (usecase_ref.execute_custom(folder, provider, data, **kwargs) if scoped else
                                  execute_use_case(config, provider, data, **kwargs))
                    except DecisionError as exc:
                        output = {"error": exc.as_dict()}
                    response = output.get("response") if isinstance(output, dict) else None
                    contract_rows.append({
                        "skill": config["id"], "provider": provider, "case_id": case["id"],
                        "request_sha256": payload_hash,
                        "policy_sha256": digest(config.get("policy")),
                        "answers_sha256": digest(response.get("answers")) if response else None,
                        "decision_sha256": digest(output.get("result", output.get("error"))) if isinstance(output, dict) else digest(output),
                    })
        elif (folder / "image.json").is_file():
            config = image_ref.load_config(folder)
            cases = json.loads((folder / "fixtures/acceptance.json").read_text(encoding="utf-8"))
            adapter = image_ref.SageImageAdapter()
            for case in cases:
                data = case["input"]
                prepared = image_ref.prepare_image(folder, data)
                request_hash = None
                if prepared["content"] is not None:
                    request_hash = digest(adapter.build_payload(prepared["content"], [config["question"]], adapter.default_model))
                try:
                    output = image_ref.execute_image(folder, "sage", data, mode="demo",
                                                     demo_answers=case.get("demo_answers"))
                except DecisionError as exc:
                    output = {"error": exc.as_dict()}
                response = output.get("response") if isinstance(output, dict) else None
                contract_rows.append({
                    "skill": config["id"], "provider": "sage", "case_id": case["id"],
                    "request_sha256": request_hash,
                    "policy_sha256": digest(config.get("policy", config.get("question"))),
                    "answers_sha256": digest(response.get("answers")) if response else None,
                    "decision_sha256": digest(output.get("result", output.get("error"))) if isinstance(output, dict) else digest(output),
                })
        else:
            # Six built-in workflow skills share the provider/runtime boundary
            # but keep their historical adapter defaults and fixture topology.
            skill = folder.name
            cases = json.loads((folder / "fixtures/acceptance.json").read_text(encoding="utf-8"))
            workflow = workflow_for(skill)
            for provider in TEXT_PROVIDERS:
                adapter = adapter_for(provider)
                for case in cases:
                    data = case["input"]
                    request_hash = None
                    prepared = workflow.build(dict(data, _provider=provider, _policy=None))
                    if prepared.get("early_result") is None:
                        request_hash = digest(adapter.build_payload(prepared["state"], prepared["questions"], adapter.default_model))
                    try:
                        output = execute_builtin(skill, provider, data, mode="demo",
                                                 demo_answers=case.get("demo_answers"))
                    except DecisionError as exc:
                        output = {"error": exc.as_dict()}
                    response = output.get("response") if isinstance(output, dict) else None
                    contract_rows.append({
                        "skill": skill, "provider": provider, "case_id": case["id"],
                        "request_sha256": request_hash,
                        "policy_sha256": digest(case.get("policy", data.get("policy"))),
                        "answers_sha256": digest(response.get("answers")) if response else None,
                        "decision_sha256": digest(output.get("result", output.get("error"))) if isinstance(output, dict) else digest(output),
                    })
    return {
        "contracts": sorted(contract_rows, key=lambda r: (r["skill"], r["provider"], r["case_id"])),
        "skill_count": len(folders),
        "runtime_revision": runtime_revision(repo),
        "reference_artifacts": reference_artifacts(repo),
        "artifacts": {path.name: skill_artifacts(path) for path in folders},
    }


def _run_worker(repo: Path) -> dict[str, Any]:
    script = Path(__file__).resolve()
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo.resolve() / "src")
    proc = subprocess.run([sys.executable, str(script), "--worker", "--repo", str(repo.resolve())],
                          cwd=repo, env=env, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"contract worker failed ({proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def collect_contracts(repo: str | Path) -> dict[str, Any]:
    """Collect this checkout's request, policy, demo-answer and decision hashes."""
    return _run_worker(Path(repo))


def _check_contract_coverage(value: dict[str, Any]) -> None:
    contracts = value.get("contracts")
    if not isinstance(contracts, list) or len(contracts) != 948:
        raise ValueError(f"expected 948 contract rows, found {len(contracts) if isinstance(contracts, list) else 'invalid'}")
    keys = [(r.get("skill"), r.get("provider"), r.get("case_id")) for r in contracts]
    if len(set(keys)) != 948:
        raise ValueError("contract rows do not have unique skill/provider/case coverage")
    if value.get("skill_count") != 27 or len(value.get("artifacts", {})) != 27:
        raise ValueError("expected exactly 27 published skills in the contract inventory")


def export_baseline(repo: str | Path, output: str | Path,
                    receipt_root: str | Path = Path.cwd()) -> dict[str, Any]:
    repo = Path(repo).resolve()
    value = _run_worker(repo)
    _check_contract_coverage(value)
    if value["runtime_revision"] != OLD_RUNTIME_REVISION:
        raise ValueError("frozen runtime source hash differs from the published image receipt revision")
    if value["reference_artifacts"] != OLD_HELPER_SHA256:
        raise ValueError("frozen reference helper hashes differ from the approved source snapshot")
    golden = {
        "schema_version": 1,
        "kind": "reference-upgrade-golden",
        "baseline_commit": BASELINE_COMMIT,
        "previous_runtime_revision": value["runtime_revision"],
        "previous_reference_artifacts": value["reference_artifacts"],
        "skill_count": value["skill_count"],
        "payload_and_policy_cases": len(value["contracts"]),
        "contracts": value["contracts"],
        "artifacts": value["artifacts"],
        "contract_sha256": digest(value["contracts"]),
        "receipt_sha256": {Path(name).name: file_digest(Path(receipt_root) / name) for name in RECEIPTS},
    }
    Path(output).write_text(json.dumps(golden, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return golden


def verify_demo_contracts(repo: str | Path, golden: dict[str, Any]) -> dict[str, Any]:
    current = collect_contracts(repo)
    _check_contract_coverage(current)
    expected = golden.get("contracts")
    if not isinstance(expected, list) or len(expected) != 948:
        raise ValueError("golden contract coverage is incomplete")
    if digest(expected) != golden.get("contract_sha256"):
        raise ValueError("golden contract digest is invalid")
    if current["contracts"] != expected:
        old = {(x["skill"], x["provider"], x["case_id"]): x for x in expected}
        now = {(x["skill"], x["provider"], x["case_id"]): x for x in current["contracts"]}
        changed = [key for key in sorted(old) if old[key] != now.get(key)]
        raise ValueError(f"request/policy/demo decision contracts changed: {changed[:8]}")
    if current["artifacts"] != golden.get("artifacts"):
        raise ValueError("skill configuration, example, fixture or image artifacts changed")
    return current


def _normalized_result(output: dict[str, Any]) -> dict[str, Any]:
    response = output.get("response")
    return {"result": output.get("result"), "response": response}


def _replay_worker(repo: Path, items: list[dict[str, Any]]) -> list[str]:
    script = Path(__file__).resolve()
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo.resolve() / "src")
    with tempfile.TemporaryDirectory(prefix="reference-upgrade-") as temp_dir:
        input_path = Path(temp_dir) / "replays.json"
        input_path.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        proc = subprocess.run([sys.executable, str(script), "--replay-worker", "--repo", str(repo.resolve()),
                               "--replay-input", str(input_path)], cwd=repo, env=env,
                              text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"replay worker failed ({proc.returncode}): {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def _with_synthetic_credential(key_env: str, operation):
    existed = key_env in os.environ
    prior = os.environ.get(key_env)
    os.environ[key_env] = "offline-synthetic-audit-credential"
    try:
        return operation()
    finally:
        if existed:
            os.environ[key_env] = prior
        else:
            os.environ.pop(key_env, None)


def _replay_one(repo: Path, row: dict[str, Any], raw: dict[str, Any], mode: str) -> dict[str, Any]:
    source = str((repo / "src").resolve())
    if source not in sys.path:
        sys.path.insert(0, source)
    from decision_models.contracts import DecisionError
    skill = row.get("skill") or row.get("recipe") or row.get("output", {}).get("skill") or row.get("output", {}).get("recipe")
    folder = repo / "skills" / skill
    if (folder / "decision.json").is_file():
        ref = _load_helper(repo / "scripts/usecase_reference.py", f"_audit_replay_usecase_{mode}")
        provider = row["provider"]
        data = _fixture_input(folder, row.get("case_id"))
        model = row.get("output", {}).get("requested_model")
        def fake_transport(_endpoint, _payload, _key, _timeout):
            return raw
        adapter = ref.usecase_adapter(provider)
        return _with_synthetic_credential(adapter.key_env, lambda: ref.execute_custom(
            folder, provider, data, mode="live", model=model, transport=fake_transport))
    if not (folder / "image.json").is_file():
        from decision_models.runtime import execute as execute_builtin
        provider = row["provider"]
        adapter = __import__("decision_models.runtime", fromlist=["adapter_for"]).adapter_for(provider)
        data = _fixture_input(folder, row.get("case_id"))
        return _with_synthetic_credential(adapter.key_env, lambda: execute_builtin(
            skill, provider, data, mode="live", model=row.get("output", {}).get("requested_model"),
            transport=lambda _endpoint, _payload, _key, _timeout: raw))
    ref = _load_helper(repo / "scripts/image_reference.py", f"_audit_replay_image_{mode}")
    data = _fixture_input(folder, row.get("case_id"))
    def fake_transport(_endpoint, _payload, _key, _timeout):
        return raw
    adapter = ref.SageImageAdapter()
    return _with_synthetic_credential(adapter.key_env, lambda: ref.execute_image(
        folder, "sage", data, mode="live", transport=fake_transport))


def _fixture_input(folder: Path, case_id: str | None) -> dict[str, Any]:
    cases = json.loads((folder / "fixtures/acceptance.json").read_text(encoding="utf-8"))
    case = next((item for item in cases if item.get("id") == case_id), None)
    if case is None:
        raise ValueError(f"receipt references unknown fixture {folder.name}/{case_id}")
    return case["input"]


def audit_receipts(repo: str | Path, golden: dict[str, Any], receipts: list[str | Path],
                   baseline_root: str | Path) -> tuple[int, int, list[dict[str, Any]]]:
    repo = Path(repo).resolve()
    if len(receipts) != 4:
        raise ValueError("explicit receipt audit requires all four archived receipts")
    if {Path(value).name for value in receipts} != {Path(name).name for name in RECEIPTS}:
        raise ValueError("explicit receipt audit requires the complete pinned four-receipt set")
    rows_total, deterministic_total, details, replay_items = 0, 0, [], []
    replay_hashes: list[str] = []
    for given in receipts:
        path = Path(given).resolve()
        if not path.is_file():
            raise ValueError(f"receipt not found: {path}")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        rows = receipt.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"receipt has no rows list: {path}")
        replayed = deterministic_replayed = skipped = 0
        skipped_counts = {"error_or_no_output": 0, "unpublished_skill": 0, "no_native_response": 0}
        for row in rows:
            output = row.get("output") if isinstance(row, dict) else None
            response = output.get("response") if isinstance(output, dict) else None
            raw = response.get("raw_response") if isinstance(response, dict) else None
            if raw is None:
                raw = row.get("raw_response") if isinstance(row, dict) else None
            if row.get("error") or not isinstance(raw, dict) or not isinstance(output, dict):
                if isinstance(output, dict) and output.get("source") == "deterministic" and not row.get("error"):
                    raw = None
                    deterministic = True
                else:
                    skipped += 1
                    skipped_counts["error_or_no_output"] += 1
                    continue
            else:
                deterministic = False
            skill = row.get("skill") or row.get("recipe") or output.get("skill") or output.get("recipe")
            if skill not in golden["artifacts"]:
                skipped += 1
                skipped_counts["unpublished_skill"] += 1
                continue
            if not deterministic and (not isinstance(raw, dict) or not isinstance(output, dict)):
                skipped += 1
                skipped_counts["no_native_response"] += 1
                continue
            try:
                replayed_output = _replay_one(repo, row, raw, f"receipt{len(details)}")
            except Exception as exc:
                raise ValueError(f"archived native response failed current-runtime replay for {skill}/{row.get('case_id')}: {exc}") from exc
            archived_hash = digest(_normalized_result(output))
            replayed_hash = digest(_normalized_result(replayed_output))
            if archived_hash != replayed_hash:
                raise ValueError(f"archived native response changed behavior for {skill}/{row.get('case_id')}/{row.get('provider')}")
            replay_hashes.append(replayed_hash)
            replay_items.append({"row": row, "raw": raw})
            if deterministic:
                deterministic_replayed += 1
            else:
                replayed += 1
        expected_sha = golden.get("receipt_sha256", {}).get(path.name)
        if expected_sha is None:
            raise ValueError(f"golden does not pin receipt content: {path.name}")
        rows_total += replayed
        deterministic_total += deterministic_replayed
        details.append({"path": path.name, "sha256": file_digest(path), "rows": len(rows),
                        "replayed": replayed, "deterministic_replays": deterministic_replayed,
                        "skipped": skipped, "skipped_by_reason": skipped_counts,
                        "receipt_identity_verified": expected_sha == file_digest(path)})
        if expected_sha != file_digest(path):
            raise ValueError(f"receipt bytes differ from frozen native evidence: {path.name}")
    if rows_total == 0:
        raise ValueError("no archived native responses were replayed")
    baseline_root = Path(baseline_root).resolve()
    if runtime_revision(baseline_root) != golden.get("previous_runtime_revision"):
        raise ValueError("archived replay comparison requires the frozen previous runtime source")
    old_hashes = _replay_worker(baseline_root, replay_items)
    if len(old_hashes) != len(replay_hashes):
        raise ValueError("previous-runtime replay worker returned incomplete coverage")
    if old_hashes != replay_hashes:
        mismatches = [i for i, (old, now) in enumerate(zip(old_hashes, replay_hashes)) if old != now]
        raise ValueError(f"archived native response differs between previous and current runtime at replay indices {mismatches[:8]}")
    # The worker compares both kinds of archived behavior, while only rows that
    # consumed a recorded native response count as archived response replays.
    return rows_total, deterministic_total, details


def audit(repo: str | Path, golden: dict[str, Any], receipts: list[str | Path] | None = None,
          baseline_root: str | Path | None = None) -> dict[str, Any]:
    repo = Path(repo).resolve()
    current = verify_demo_contracts(repo, golden)
    if receipts and baseline_root is None:
        raise ValueError("--baseline-root is required when explicit archived receipts are audited")
    replayed, deterministic_replays, receipt_details = (
        audit_receipts(repo, golden, receipts, baseline_root) if receipts else (0, 0, [])
    )
    return {
        "schema_version": 1,
        "kind": "reference-upgrade-audit",
        "previous_runtime_revision": golden["previous_runtime_revision"],
        "runtime_revision": current["runtime_revision"],
        "previous_reference_artifacts": golden["previous_reference_artifacts"],
        "current_reference_artifacts": current["reference_artifacts"],
        "skill_count": current["skill_count"],
        "payload_and_policy_cases": len(current["contracts"]),
        "actual_archived_response_replays": replayed,
        "deterministic_replays": deterministic_replays,
        "paid_requests": 0,
        "identical": True,
        "golden_sha256": digest(golden),
        "decision_contracts_frozen": len(current["contracts"]),
        "reference_artifacts_frozen": len(golden["previous_reference_artifacts"]),
        "artifacts_frozen": sum(len(files) for files in current["artifacts"].values()),
        "artifacts": current["artifacts"],
        "receipts": receipt_details,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--receipt-root", type=Path, default=Path.cwd())
    parser.add_argument("--export-baseline", action="store_true")
    parser.add_argument("--golden", type=Path, default=Path(__file__).with_name("reference-contracts.json"))
    parser.add_argument("--receipts", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--replay-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--replay-input", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(_worker(args.repo), ensure_ascii=False))
        return 0
    if args.replay_worker:
        if args.replay_input is None:
            parser.error("--replay-worker requires --replay-input")
        items = json.loads(args.replay_input.read_text(encoding="utf-8"))
        hashes = []
        for index, item in enumerate(items):
            output = _replay_one(args.repo.resolve(), item["row"], item["raw"], f"batch{index}")
            hashes.append(digest(_normalized_result(output)))
        print(json.dumps(hashes))
        return 0
    if args.export_baseline:
        if args.baseline_root is None:
            parser.error("--export-baseline requires --baseline-root")
        golden = export_baseline(args.baseline_root, args.golden, args.receipt_root)
        print(json.dumps({"golden": str(args.golden), "contracts": len(golden["contracts"]),
                          "runtime_revision": golden["previous_runtime_revision"]}, indent=2))
        return 0
    golden = json.loads(args.golden.read_text(encoding="utf-8"))
    report = audit(args.repo, golden, args.receipts, args.baseline_root)
    output_path = args.output or (args.repo / "reports/reference-upgrade-audit.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in (
        "previous_runtime_revision", "runtime_revision", "skill_count", "payload_and_policy_cases",
        "actual_archived_response_replays", "paid_requests", "identical", "golden_sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
