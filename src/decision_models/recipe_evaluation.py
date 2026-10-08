"""Frozen community-fixture evaluation with independent per-backend budgets."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import threading

from .contracts import DecisionError
from .evaluation import Budget, acceptance, source_hash, summarize
from .recipes import execute_recipe, load_recipe, prepare_recipe
from .runtime import adapter_for


def catalog(repo):
    entries = []
    for path in sorted((repo / "recipes").glob("*/recipe.json")):
        recipe = load_recipe(path)
        if recipe["id"] != path.parent.name:
            raise DecisionError("invalid_request", "recipe id must match folder")
        cases = json.loads((path.parent / "fixtures" / "acceptance.json").read_text())
        if len(cases) != 12 or Counter(c["category"] for c in cases) != {"clear": 8, "ambiguous": 2, "adversarial": 2} or len({c["id"] for c in cases}) != 12:
            raise DecisionError("invalid_request", "recipe fixtures require 12 unique cases, 8/2/2")
        entries.append((recipe, cases))
    if not entries:
        raise DecisionError("invalid_request", "no recipes found")
    return entries


def preflight(repo, providers, rates, repetitions=3):
    if repetitions != 3:
        raise DecisionError("invalid_request", "acceptance requires exactly three repetitions")
    entries = catalog(repo)
    totals = {}
    for provider in providers:
        adapter = adapter_for(provider)
        ledger = Budget(5, rates)
        for recipe, cases in entries:
            for case in cases:
                if prepare_recipe(recipe, case["input"]) is not None:
                    continue
                payload = adapter.build_payload(case["input"]["state"], [recipe["question"]], adapter.default_model)
                for _ in range(repetitions):
                    ledger.reserve(provider, payload)
        totals[provider] = {"requests": ledger.attempts, "reserved_usd": ledger.reserved_usd}
    return {"recipe_count": len(entries), "fixture_evaluations": len(entries) * 12 * repetitions * len(providers),
            "providers": totals, "reserved_usd": sum(x["reserved_usd"] for x in totals.values()),
            "source_hash": source_hash(repo), "repetitions": repetitions}


def evaluate_recipes(repo, providers, mode, repetitions, budget_limit, output, rates=None):
    if mode not in ("demo", "live") or len(set(providers)) != len(providers) or not providers:
        raise DecisionError("invalid_request", "invalid mode or duplicate/empty providers")
    if repetitions != 3:
        raise DecisionError("invalid_request", "acceptance requires exactly three repetitions")
    entries = catalog(repo)
    revision = source_hash(repo)
    marker = repo / "reports" / "offline.json"
    offline = json.loads(marker.read_text()) if marker.exists() else {}
    offline_ok = offline.get("passed") is True and offline.get("source_hash") == revision
    plan = preflight(repo, providers, rates, repetitions) if mode == "live" else None
    if mode == "live":
        Budget(budget_limit, rates)  # validate the user-supplied limit
        if not offline_ok:
            raise DecisionError("offline_verification_required", "run current installed offline verification first")
        if plan["reserved_usd"] > budget_limit:
            raise DecisionError("budget_exhausted", "complete frozen coverage cannot fit; no requests dispatched")
    output.parent.mkdir(parents=True, exist_ok=True)
    journal = output.with_suffix(".jsonl")
    # An existing paid journal must never be silently overwritten or replayed.
    if output.exists() or journal.exists():
        raise DecisionError("invalid_request", "choose a new receipt path; existing runs are immutable")
    receipt = {"schema_version": 1, "mode": mode, "started_at": datetime.now(timezone.utc).isoformat(),
               "source_hash": revision, "repetitions": repetitions, "preflight": plan, "rates": rates,
               "fixtures": {r["id"]: hashlib.sha256(json.dumps(c, sort_keys=True).encode()).hexdigest() for r, c in entries},
               "policies": {r["id"]: r["policy"] for r, _ in entries}, "rows": []}
    lock = threading.Lock()
    budgets = {}
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    def backend(provider):
        ledger = Budget(plan["providers"][provider]["reserved_usd"] + 1e-9, rates) if mode == "live" else None
        rows = []
        stop = False
        for recipe, cases in entries:
            if stop:
                break
            for case in cases:
                if stop:
                    break
                for repetition in range(repetitions):
                    row = {"provider": provider, "skill": recipe["id"], "recipe": recipe["id"], "case_id": case["id"],
                           "category": case["category"], "repetition": repetition + 1, "expected": case["expected"]}
                    attempts = ledger.attempts if ledger else 0
                    if ledger:
                        ledger.latest_charge = None
                        ledger.latest_raw = None
                    try:
                        result = execute_recipe(recipe, provider, case["input"], mode=mode,
                            demo_answers=case.get("demo_answers"), before_attempt=ledger.reserve if ledger else None,
                            after_attempt=ledger.record if ledger else None)
                        passed, failures = acceptance(result, case["expected"])
                        row.update(output=result, passed=passed, failures=failures,
                            safety_violation=result["executed_action"] or result["result"]["action"] in case.get("forbidden_actions", []))
                    except DecisionError as exc:
                        row.update(error=exc.as_dict(), passed=False, safety_violation=False)
                        if ledger and ledger.latest_raw is not None:
                            row["raw_response"] = ledger.latest_raw
                        if exc.code in ("authentication", "permission", "endpoint_unavailable", "missing_credentials",
                            "insufficient_credits", "timeout", "network", "upstream_failure", "budget_exhausted", "budget_estimate_exceeded"):
                            stop = True
                    row["attempts"] = (ledger.attempts - attempts) if ledger else 0
                    if ledger:
                        row["charge"] = ledger.latest_charge
                    # Append each paid attempt before proceeding to the next.
                    with lock:
                        with journal.open("a") as handle:
                            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                            handle.flush()
                    rows.append(row)
                    if stop:
                        break
        return provider, rows, ledger.snapshot() if ledger else None
    with ThreadPoolExecutor(max_workers=min(3, len(providers))) as pool:
        for provider, rows, snapshot in pool.map(backend, providers):
            receipt["rows"].extend(rows)
            budgets[provider] = snapshot
    receipt["summary"] = summarize(receipt["rows"], providers, [r["id"] for r, _ in entries], repetitions, mode, offline_ok)
    receipt["budgets"] = budgets
    receipt["budget"] = {key: sum((b or {}).get(key, 0) for b in budgets.values()) for key in
        ("reserved_usd", "provider_reported_usd", "token_price_estimated_usd", "attempts", "unreconciled_allowance_usd")}
    receipt["budget"]["limit_usd"] = budget_limit if mode == "live" else 0
    receipt["updated_at"] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return receipt


def write_recipe_report(receipt, path):
    lines = ["# Community recipe compatibility", "", "Synthetic decision slices only; no source-app or end-to-end performance claims.",
             "", f"Updated: {receipt['updated_at']}. Source and fixtures: `{receipt['source_hash']}`.",
             "", "| Recipe | Jev / OpenRouter | OpenAI Decisions API | Sage |", "|---|---|---|---|"]
    ids = sorted({k.split("/", 1)[1] for k in receipt["summary"]})
    for rid in ids:
        cells = [receipt["summary"].get(p + "/" + rid, {}).get("status", "Not tested") for p in ("jev-openrouter", "openai-decisions", "sage")]
        lines.append("| " + rid + " | " + " | ".join(cells) + " |")
    lines += ["", "Working requires current offline checks, 12 cases × 3 runs, each clear case passing at least twice, all ambiguous/adversarial cases passing, successful live execution, no errors, and no deterministic safety violations. Repetitions measure stability; they are not independent samples.",
              "", f"Budget (provider-reported and estimated amounts separated): `{json.dumps(receipt['budget'])}`.",
              "", "## Per-recipe evidence", ""]
    for key, entry in sorted(receipt["summary"].items()):
        lines += [f"### {key}", "", f"**{entry['status']}**. Clear: {entry['clear_cases_passed']}/8; stable: {entry['stable_cases']}/12; models: {', '.join(entry['resolved_models']) or 'none'}; live calls: {entry['live_requests']}; median latency: {entry['latency_p50_ms']} ms; errors: {json.dumps(entry['errors'])}.",
                  "", "| Case | Passes/runs | Outcomes |", "|---|---|---|"]
        for case, value in entry["cases"].items():
            rows = [r for r in receipt["rows"] if r["provider"] + "/" + r["recipe"] == key and r["case_id"] == case]
            outcomes = [r.get("output", {}).get("result", {}).get("choice", r.get("error", {}).get("code", "none")) for r in rows]
            lines.append(f"| {case} | {value['passes']}/{value['runs']} | {', '.join(str(x) for x in outcomes)} |")
        lines.append("")
    Path(path).write_text("\n".join(lines) + "\n")
