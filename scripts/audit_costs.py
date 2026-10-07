"""Reconcile all retained live runs without making provider requests."""
import json
from datetime import datetime, timezone
from pathlib import Path


def main():
    reports = Path(__file__).resolve().parents[1] / "reports"
    runs = []
    totals = {"provider_reported_usd": 0.0, "token_price_estimated_usd": 0.0,
              "attempts": 0, "unknown_charge_attempts": 0}

    def charge(provider, response, rates):
        usage = response.get("usage") or {}
        if isinstance(usage.get("cost"), (int, float)):
            return "provider_reported_usd", usage["cost"], 0
        if "input_tokens" not in usage or "output_tokens" not in usage:
            return None, 0.0, 0
        output = usage["output_tokens"]
        floor = len(response.get("answers", {})) if provider == "sage" else 0
        rate = rates[provider]
        estimate = (usage["input_tokens"] * rate["input_per_million"] +
                    max(output, floor) * rate["output_per_million"]) / 1_000_000
        return "token_price_estimated_usd", estimate, max(0, floor - output)

    for filename in ("baseline.json", "v2.json", "v3.json", "live.json"):
        receipt = json.loads((reports / filename).read_text())
        record = {"receipt": filename, "source_hash": receipt["source_hash"],
                  "fixture_evaluations": len(receipt["rows"]),
                  "reserved_usd": receipt["budget"]["reserved_usd"],
                  "provider_reported_usd": 0.0, "token_price_estimated_usd": 0.0,
                  "attempts": receipt["budget"]["attempts"],
                  "unknown_charge_attempts": 0, "sage_output_floor_tokens": 0}
        for row in receipt["rows"]:
            output = row.get("output", {})
            if output.get("source") != "live":
                record["unknown_charge_attempts"] += row.get("attempts", 0)
                continue
            kind, amount, floor = charge(row["provider"], output["response"], receipt["rates"])
            if kind:
                record[kind] += amount
                record["sage_output_floor_tokens"] += floor
            else:
                record["unknown_charge_attempts"] += output.get("attempts", 1)
        for key in totals:
            totals[key] += record[key]
        runs.append(record)
    rates = json.loads((reports / "rates.json").read_text())
    smoke = {"receipt": "smoke.json", "attempts": 0, "reserved_usd": 0.001,
             "provider_reported_usd": 0.0, "token_price_estimated_usd": 0.0,
             "unknown_charge_attempts": 0, "sage_output_floor_tokens": 0}
    for row in json.loads((reports / "smoke.json").read_text()):
        kind, amount, floor = charge(row["provider"], row["response"], rates)
        smoke["attempts"] += 1
        if kind:
            smoke[kind] += amount
            smoke["sage_output_floor_tokens"] += floor
        else:
            smoke["unknown_charge_attempts"] += 1
    for key in totals:
        totals[key] += smoke[key]
    runs.append(smoke)
    reserved = sum(run["reserved_usd"] for run in runs)
    combined = totals["provider_reported_usd"] + totals["token_price_estimated_usd"]
    assert reserved <= 5 and combined <= reserved, "cumulative budget exceeded"
    result = {"checked_at": datetime.now(timezone.utc).isoformat(), "limit_usd": 5,
              "reserved_usd": round(reserved, 8), **totals,
              "combined_reported_and_estimated_usd": round(combined, 8), "runs": runs,
              "notes": ["Token-price estimates are not provider invoices.",
                        "Sage estimates include its documented one-output-token-per-answer floor; native zero output usage is preserved in receipts.",
                        "The baseline receipt predates floor accounting; this reconciliation applies it without rewriting historical receipts.",
                        "Smoke has a conservative US$0.001 allowance; all evaluation reservations include failed attempts."]}
    (reports / "costs.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
