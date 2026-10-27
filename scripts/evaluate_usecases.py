"""Evaluate staged text use cases; reserve full coverage before paid attempts."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import threading

from decision_models.contracts import DecisionError
from decision_models.evaluation import Budget, acceptance, source_hash, summarize
from decision_models.use_cases import prepare_use_case
from scripts.usecase_reference import execute_custom, read_config, usecase_adapter
from scripts.verified_catalog import artifacts, runtime_revision

RATES = {
    "sage": {"source": "https://docs.levanto.ai/pricing", "checked_at": "2026-10-27", "input_per_million": .05, "output_per_million": 10},
    "jev-openrouter": {"source": "https://openrouter.ai/typesafe/jev-1.13", "checked_at": "2026-10-27", "input_per_million": .042, "output_per_million": 0},
    "openai-decisions": {"source": "https://developers.openai.com/api/docs/guides/decisions", "checked_at": "2026-10-27", "input_per_million": .1, "output_per_million": 0},
}


# Failed or ambiguous attempts retain their full reservation.
UsecaseBudget = Budget


def entries(folder):
    result = []
    for path in sorted(Path(folder).iterdir()):
        if not (path / "SKILL.md").exists() or not (path / "decision.json").is_file():
            continue
        config = read_config(path)
        cases = json.loads((path / "fixtures/acceptance.json").read_text())
        if len(cases) != 12 or Counter(c["category"] for c in cases) != {"clear": 8, "ambiguous": 2, "adversarial": 2} or len({c["id"] for c in cases}) != 12:
            raise DecisionError("invalid_request", "need twelve unique 8/2/2 fixtures")
        result.append((path, config, cases))
    return result


def payloads(folder, config, data, provider):
    if data.get("permission_granted") is not True:
        return []
    if prepare_use_case(config, data) is not None:
        return []
    adapter = usecase_adapter(provider)
    return [adapter.build_payload(data["state"], [config["question"]], adapter.default_model)]


def evaluate(repo, candidate_root, output, mode, limit, historical_bound, ids=None):
    if mode not in ("demo", "live") or type(historical_bound) not in (int, float) or not math.isfinite(historical_bound) or not 0 <= historical_bound <= 5:
        raise DecisionError("invalid_request", "invalid mode or historical cost bound")
    Budget(limit, RATES)
    candidates = entries(candidate_root)
    if ids is not None:
        if not ids or not set(ids) <= {c["id"] for _, c, _ in candidates}:
            raise DecisionError("invalid_request", "unknown or empty candidate selection")
        candidates = [entry for entry in candidates if entry[1]["id"] in ids]
    if not candidates:
        raise DecisionError("invalid_request", "no candidates selected")
    providers = tuple(RATES)
    plans = {}
    for provider in providers:
        ledger = UsecaseBudget(5, RATES)
        for folder, config, cases in candidates:
            for case in cases:
                for payload in payloads(folder, config, case["input"], provider):
                    for _ in range(3):
                        ledger.reserve(provider, payload)
        plans[provider] = ledger.snapshot()
    forecast = sum(p["reserved_usd"] for p in plans.values())
    if forecast > limit or historical_bound + forecast > 5:
        raise DecisionError("budget_exhausted", "complete selected coverage cannot fit; no requests sent")
    marker = json.loads((repo / "reports/offline.json").read_text())
    offline_ok = marker.get("passed") is True and marker.get("source_hash") == source_hash(repo)
    if mode == "live" and not offline_ok:
        raise DecisionError("offline_verification_required", "run current offline verification")
    journal = output.with_suffix(".jsonl")
    if output.exists() or journal.exists():
        raise DecisionError("invalid_request", "existing evidence paths are immutable")
    output.parent.mkdir(parents=True, exist_ok=True)
    reference_files = {name: hashlib.sha256((repo / name).read_bytes()).hexdigest() for name in
                       ("scripts/usecase_reference.py", "scripts/evaluate_usecases.py")}
    receipt = {"schema_version": 1, "mode": mode, "started_at": datetime.now(timezone.utc).isoformat(),
               "source_hash": source_hash(repo), "runtime_revision": runtime_revision(repo), "repetitions": 3,
               "rates": RATES, "preflight": {"providers": plans, "reserved_usd": forecast, "historical_bound_usd": historical_bound,
                  "policy": "Completed reservations retired. Historical bound includes charges, an estimate cushion, and retained allowances for rejected or unknown-charge attempts. Full new coverage reserved."},
               "fixtures": {c["id"]: hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest() for _, c, cases in candidates},
               "evaluated_artifacts": {c["id"]: artifacts(folder) for folder, c, _ in candidates},
               "reference_artifacts": reference_files, "rows": []}
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    lock = threading.Lock()
    def backend(provider):
        ledger = UsecaseBudget(plans[provider]["reserved_usd"] + 1e-8, RATES)
        rows, stop = [], False
        for folder, config, cases in candidates:
            if stop:
                break
            for case in cases:
                if stop:
                    break
                for repetition in range(1, 4):
                    row = {"provider": provider, "skill": config["id"],
                           "case_id": case["id"], "category": case["category"], "repetition": repetition,
                           "expected": case["expected"], "safety_violation": False}
                    before = ledger.attempts
                    ledger.latest_charge = ledger.latest_raw = None
                    charges = []
                    def record(p, raw):
                        ledger.record(p, raw)
                        charges.append(ledger.latest_charge)
                    try:
                        result = execute_custom(folder, provider, case["input"], mode=mode,
                            demo_answers=case.get("demo_answers"), before_attempt=ledger.reserve if mode == "live" else None,
                            after_attempt=record if mode == "live" else None)
                        passed, failures = acceptance(result, case["expected"])
                        row.update(output=result, passed=passed, failures=failures,
                                   safety_violation=result["executed_action"] or (case["input"].get("permission_granted") is not True and result["result"]["action"] != "deny"))
                    except DecisionError as exc:
                        row.update(error=exc.as_dict(), passed=False)
                        if ledger.latest_raw is not None:
                            row["raw_response"] = ledger.latest_raw
                        # A scheduled repetition is also a retry. Stop on every
                        # protocol/service failure rather than rebill ambiguity.
                        stop = True
                    row.update(attempts=ledger.attempts - before, charges=charges)
                    with lock:
                        with journal.open("a") as handle:
                            handle.write(json.dumps(row) + "\n")
                            handle.flush()
                    rows.append(row)
                    if stop:
                        break
        return provider, rows, ledger.snapshot()
    budgets = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for provider, rows, snapshot in pool.map(backend, providers):
            receipt["rows"].extend(rows)
            budgets[provider] = snapshot
    receipt["budgets"] = budgets
    receipt["budget"] = {key: sum(b[key] for b in budgets.values()) for key in
                         ("reserved_usd", "provider_reported_usd", "token_price_estimated_usd", "attempts", "unreconciled_allowance_usd")}
    receipt["summary"] = summarize(receipt["rows"], providers, [c["id"] for _, c, _ in candidates], 3, mode, offline_ok)
    receipt["updated_at"] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path, default=Path("research/candidates"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ids", nargs="+", help="evaluate only named use-case folders")
    parser.add_argument("--mode", choices=("demo", "live"), default="demo")
    parser.add_argument("--budget", type=float, default=2.5)
    parser.add_argument("--historical-bound", type=float, required=True)
    args = parser.parse_args()
    result = evaluate(Path.cwd(), args.candidates, args.output, args.mode, args.budget, args.historical_bound, args.ids)
    print(json.dumps({"summary": {k: v["status"] for k, v in result["summary"].items()}, "budget": result["budget"]}, indent=2))
