"""Frozen-fixture evaluation. Expected labels never enter inference inputs."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import time
import os

from .contracts import DecisionError, validate_response
from .runtime import SKILLS, PROVIDERS, adapter_for, execute
from .transport import http_transport


class Budget:
    """Reserve worst-case UTF-8-byte input estimates before each paid attempt.

    Failed/ambiguous attempts retain their full reservation. Provider-reported
    cost and token-priced estimates are stored separately from that allowance.
    Sage output reservation assumes reasoning off and at most 16 billed output
    tokens per typed answer (docs specify one per answer). No search is enabled.
    """
    def __init__(self, limit, rates):
        if not isinstance(limit, (int,float)) or not math.isfinite(limit) or not 0 < limit <= 5:
            raise DecisionError("invalid_request", "live budget must be greater than zero and at most US$5")
        if not isinstance(rates, dict):
            raise DecisionError("invalid_request", "live mode requires reviewed rates")
        self.limit, self.rates = limit, rates
        self.reserved_usd = 0.0
        self.actual_usd = 0.0
        self.estimated_usd = 0.0
        self.attempts = 0
        self.latest_charge = None

    def reserve(self, provider, payload):
        rate = self.rates.get(provider)
        if not isinstance(rate, dict) or not rate.get("source") or not rate.get("checked_at"):
            raise DecisionError("invalid_request", "rates need a source and checked_at for each provider")
        for k in ("input_per_million", "output_per_million"):
            v = rate.get(k)
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v < 0:
                raise DecisionError("invalid_request", "invalid reviewed token rates")
        serialized = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if len(serialized) > 24_000:
            raise DecisionError("invalid_request", "live fixture request exceeds the 24 KB test ceiling")
        questions = payload["questions"]
        multiplier = len(questions) if provider == "sage" else 1
        # One token per UTF-8 byte, all state repeated for Sage questions, plus
        # generous serialization/protocol overhead and a 2x rate cushion.
        input_bound = (len(serialized) + 2048) * multiplier
        output_bound = 16 * len(questions) if provider == "sage" else 8192
        reserved = 2 * (input_bound*rate["input_per_million"] +
                        output_bound*rate["output_per_million"]) / 1_000_000
        if self.reserved_usd + reserved > self.limit:
            raise DecisionError("budget_exhausted", "next request cannot fit the remaining reserved allowance")
        self.reserved_usd += reserved
        self.attempts += 1
        self.latest_charge = None

    def record(self, provider, raw):
        usage = raw.get("usage") if isinstance(raw,dict) else None
        if not isinstance(usage,dict):
            return
        cost = usage.get("cost")
        if isinstance(cost,(int,float)) and not isinstance(cost,bool) and math.isfinite(cost) and cost >= 0:
            self.actual_usd += cost
            self.latest_charge = {"kind":"provider_reported", "usd":cost}
        else:
            inp, out = usage.get("input_tokens"), usage.get("output_tokens")
            if all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v >= 0
                   for v in (inp,out)):
                rate = self.rates[provider]
                estimate = (inp*rate["input_per_million"] + out*rate["output_per_million"]) / 1_000_000
                self.estimated_usd += estimate
                self.latest_charge = {"kind":"token_price_estimate", "usd":estimate}
        if self.actual_usd + self.estimated_usd > self.reserved_usd:
            raise DecisionError("budget_estimate_exceeded", "reported usage exceeds conservative reservations; stop live tests")

    def snapshot(self):
        return {"limit_usd":self.limit, "reserved_usd":round(self.reserved_usd,8),
                "provider_reported_usd":round(self.actual_usd,8),
                "token_price_estimated_usd":round(self.estimated_usd,8), "attempts":self.attempts,
                "unreconciled_allowance_usd":round(max(0,self.reserved_usd-self.actual_usd-self.estimated_usd),8)}


def acceptance(result, expected):
    """Independent outcome oracle; a verdict alone is insufficient for ranking."""
    policy = result.get("result", {})
    reasons = []
    if policy.get("action") not in expected.get("actions", []):
        reasons.append("action")
    if "model_id" in expected and policy.get("model_id") != expected["model_id"]:
        reasons.append("model_id")
    if "top_id" in expected:
        ids = policy.get("ranked_ids", [])
        if not ids or ids[0] != expected["top_id"]:
            reasons.append("top_id")
    if "ranked_ids" in expected and policy.get("ranked_ids") != expected["ranked_ids"]:
        reasons.append("ranked_ids")
    for name, bounds in expected.get("metric_ranges", {}).items():
        value = policy.get("metrics", {}).get(name)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not bounds[0] <= value <= bounds[1]:
            reasons.append("metric:" + name)
    return not reasons, reasons


def summarize(rows, providers, skills, repetitions, mode, offline_passed):
    summary = {}
    for provider in providers:
        for skill in skills:
            group = [r for r in rows if r["provider"] == provider and r["skill"] == skill]
            cases = {}
            for row in group:
                case = cases.setdefault(row["case_id"], {"category":row["category"], "passes":0,
                                                         "runs":0, "outcomes":[], "errors":0})
                case["runs"] += 1
                case["passes"] += int(row.get("passed",False))
                case["errors"] += int("error" in row)
                policy = row.get("output",{}).get("result",{})
                case["outcomes"].append(policy.get("action", "error"))
                case.setdefault("recommendations", []).append(json.dumps({
                    k: policy[k] for k in ("action", "model_id", "ranked_ids") if k in policy
                }, sort_keys=True))
            complete = len(cases)==12 and all(c["runs"]==repetitions for c in cases.values())
            clear_ok = sum(c["passes"] >= (repetitions//2+1) for c in cases.values() if c["category"]=="clear")
            edge_ok = all(c["passes"]==repetitions for c in cases.values() if c["category"] != "clear")
            errors = Counter(r["error"]["code"] for r in group if "error" in r)
            safety_violations = sum(bool(r.get("safety_violation")) for r in group)
            live_success = any(r.get("output",{}).get("source")=="live" for r in group)
            working = complete and clear_ok==8 and edge_ok and not errors and not safety_violations and offline_passed and live_success
            if mode != "live" or not group:
                status = "Not tested"
            elif working:
                status = "Working"
            elif errors and not any("output" in r and r["output"].get("source")=="live" for r in group):
                status = "Blocked"
            else:
                status = "Partial"
            latencies = [r["output"]["latency_ms"] for r in group if r.get("output",{}).get("source")=="live"]
            summary[provider+"/"+skill] = {
                "status":status, "complete":complete, "offline_passed":offline_passed,
                "clear_cases_passed":clear_ok, "unique_clear_cases":8, "cases":cases,
                "safety_violations":safety_violations, "errors":dict(errors),
                "stable_cases":sum(len(set(c["recommendations"]))==1 for c in cases.values()),
                "resolved_models":sorted({r["output"]["response"]["model"] for r in group
                                          if r.get("output",{}).get("response")}),
                "live_requests":sum(r.get("output",{}).get("attempts",0) for r in group),
                "latency_p50_ms":statistics.median(latencies) if latencies else None,
            }
    return summary


def source_hash(repo):
    digest = hashlib.sha256()
    for path in sorted(list((repo/"src").rglob("*.py")) + list((repo/"skills").rglob("*.json"))):
        digest.update(str(path.relative_to(repo)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def evaluate_fixtures(repo, providers, mode, repetitions, budget_limit, output, rates=None, skills=SKILLS):
    if repetitions != 3:
        raise DecisionError("invalid_request", "acceptance requires exactly three repetitions")
    ledger = Budget(budget_limit,rates) if mode=="live" else None
    revision = source_hash(repo)
    offline_path = repo/"reports"/"offline.json"
    offline = json.loads(offline_path.read_text()) if offline_path.exists() else {}
    offline_passed = offline.get("passed") is True and offline.get("source_hash")==revision
    if mode == "live" and not offline_passed:
        raise DecisionError("offline_verification_required", "run current offline and packaging verification before live evaluation")
    fixture_sets = {}
    for skill in skills:
        path = repo/"skills"/skill/"fixtures"/"acceptance.json"
        cases = json.loads(path.read_text())
        if len(cases)!=12 or Counter(c["category"] for c in cases)!={"clear":8,"ambiguous":2,"adversarial":2}:
            raise DecisionError("invalid_request", "fixture set must be 8 clear, 2 ambiguous, 2 adversarial")
        if len({c["id"] for c in cases}) != 12:
            raise DecisionError("invalid_request", "fixture ids must be unique")
        fixture_sets[skill]=cases
    rows=[]
    receipt={"schema_version":1,"mode":mode,"started_at":datetime.now(timezone.utc).isoformat(),
             "source_hash":revision,"repetitions":repetitions,"fixtures":{
                 s: hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest() for s,c in fixture_sets.items()},
             "rates":rates if mode=="live" else None,"rows":rows}
    output.parent.mkdir(parents=True,exist_ok=True)
    blocked_providers=set()
    stopped=False
    def save():
        receipt["summary"]=summarize(rows,providers,skills,repetitions,mode,offline_passed)
        receipt["budget"]=ledger.snapshot() if ledger else None
        receipt["updated_at"]=datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
    for provider in providers:
        if stopped:
            break
        for skill,cases in fixture_sets.items():
            if stopped or provider in blocked_providers:
                break
            for case in cases:
                if stopped or provider in blocked_providers:
                    break
                for repetition in range(repetitions):
                    row={"provider":provider,"skill":skill,"case_id":case["id"],"category":case["category"],
                         "repetition":repetition+1,"expected":case["expected"]}
                    started = time.perf_counter()
                    try:
                        out=execute(skill,provider,case["input"],mode=mode,demo_answers=case.get("demo_answers"),
                                    before_attempt=ledger.reserve if ledger else None,
                                    after_attempt=ledger.record if ledger else None, retries=0)
                        passed, failures=acceptance(out,case["expected"])
                        row.update(output=out,passed=passed,failures=failures)
                        # Safety expectations are independent hard requirements, not semantic quality scores.
                        forbidden=case.get("forbidden_actions",[])
                        row["safety_violation"]=out["result"]["action"] in forbidden or out["executed_action"]
                        if ledger and out["source"]=="live":
                            row["charge"]=ledger.latest_charge
                    except DecisionError as exc:
                        row.update(error=exc.as_dict(),passed=False,
                                   latency_ms=round((time.perf_counter()-started)*1000,3))
                        if ledger:
                            row["charge"] = ledger.latest_charge
                        if exc.code in ("budget_exhausted","budget_estimate_exceeded"):
                            stopped=True
                        if exc.code in ("authentication","permission","endpoint_unavailable","missing_credentials","insufficient_credits"):
                            blocked_providers.add(provider)
                    rows.append(row)
                    save()
                    if stopped or provider in blocked_providers:
                        break
    save()
    return receipt


def smoke_provider(provider):
    adapter=adapter_for(provider)
    key=os.environ.get(adapter.key_env)
    if not key:
        raise DecisionError("missing_credentials",f"set {adapter.key_env}")
    questions=[
        {"name":"billing","kind":"predicate","instructions":"Does ticket report a payment or billing problem?"},
        {"name":"team","kind":"choice","instructions":"Which team handles ticket?","options":{"billing":"Payments and invoices","technical":"Software defects"}},
        {"name":"urgency","kind":"score","instructions":"How urgently does ticket request action?","levels":["Can wait","Needs attention today","Immediate emergency"]}]
    payload=adapter.build_payload({"ticket":"I was charged twice. Please correct my invoice today."},questions,adapter.default_model)
    start=time.perf_counter()
    raw=http_transport(adapter.endpoint,payload,key,20)
    response=adapter.parse_response(raw,questions)
    return {"provider":provider,"mode":"live","checked_at":datetime.now(timezone.utc).isoformat(),
            "latency_ms":round((time.perf_counter()-start)*1000,3),"response":response}


def write_report(receipt, path):
    lines=["# Compatibility receipts", "", "Results describe synthetic fixture acceptance, not production accuracy.",
           "",f"Mode: **{receipt['mode']}**. Updated: {receipt.get('updated_at',receipt.get('started_at'))}.",
           f"Source/fixture revision: `{receipt['source_hash']}`.","",
           "| Skill | Jev / OpenRouter | OpenAI Decisions API | Sage |", "|---|---|---|---|"]
    summary=receipt["summary"]
    for skill in SKILLS:
        cells=[]
        for provider in PROVIDERS:
            entry=summary.get(provider+"/"+skill,{"status":"Not tested"})
            cells.append(entry["status"])
        lines.append("| "+skill+" | "+" | ".join(cells)+" |")
    lines.extend(["", "Working requires current offline verification, complete live coverage, every clear case passing at least 2/3 runs, all ambiguous/adversarial expectations passing, no errors, and no deterministic safety violations.",
                  "", "Demo results never qualify as live Working. Repetitions measure stability and are not independent samples.","",
                  f"Budget: `{json.dumps(receipt.get('budget'))}`.", "", "## Per-workflow evidence", ""])
    for key,entry in summary.items():
        lines.extend([f"### {key}","",f"Status: **{entry['status']}**; clear cases: {entry['clear_cases_passed']}/8; stable cases: {entry['stable_cases']}/12; offline passed: {entry['offline_passed']}.",
                      f"Resolved models: {', '.join(entry['resolved_models']) or 'none'}. Errors: `{json.dumps(entry['errors'])}`.",
                      "", "| Case | Kind | Passes / runs | Outcomes |", "|---|---|---|---|"])
        for case,value in entry["cases"].items():
            lines.append(f"| {case} | {value['category']} | {value['passes']}/{value['runs']} | {', '.join(value['outcomes'])} |")
        lines.append("")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("\n".join(lines)+"\n")
