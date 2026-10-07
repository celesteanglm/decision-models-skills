import json
import math
import os
import unittest
from collections import Counter
from pathlib import Path
import tempfile
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models import evaluation
from decision_models.evaluation import Budget, acceptance, evaluate_fixtures, summarize
from decision_models.runtime import PROVIDERS, SKILLS, adapter_for, execute, workflow_for


REPO = Path(__file__).resolve().parents[1]
RATES = {
    "sage": {"source": "reviewed fixture", "checked_at": "2026-10-08",
             "input_per_million": 1.0, "output_per_million": 2.0}
}


class EvaluationTests(unittest.TestCase):
    def test_every_fixture_has_independent_shape_and_repeated_demo_acceptance(self):
        all_rows = 0
        for skill in SKILLS:
            path = REPO / "skills" / skill / "fixtures" / "acceptance.json"
            cases = json.loads(path.read_text())
            all_rows += len(cases)
            self.assertEqual(len(cases), 12, skill)
            self.assertEqual(Counter(row["category"] for row in cases),
                             {"clear": 8, "ambiguous": 2, "adversarial": 2}, skill)
            self.assertEqual(len({row["id"] for row in cases}), 12, skill)
            for case in cases:
                with self.subTest(skill=skill, case=case["id"]):
                    self.assertIsInstance(case["input"], dict)
                    self.assertTrue(case["expected"].get("actions"))
                    built = workflow_for(skill).build(dict(case["input"], _provider="sage"))
                    for provider in PROVIDERS:
                        for _ in range(3):
                            response = execute(skill, provider, case["input"], mode="demo",
                                               demo_answers=case["demo_answers"])
                            self.assertTrue(acceptance(response, case["expected"])[0],
                                            (provider, case["id"], response["result"], case["expected"]))
        self.assertEqual(all_rows, 72)

    def test_expected_labels_are_excluded_from_all_provider_request_payloads(self):
        for skill in SKILLS:
            cases = json.loads((REPO / "skills" / skill / "fixtures" / "acceptance.json").read_text())
            for case in cases:
                with self.subTest(skill=skill, case=case["id"]):
                    built = workflow_for(skill).build(dict(case["input"], _provider="sage"))
                    if built["early_result"] is not None:
                        continue
                    for provider in ("jev-openrouter", "openai-decisions", "sage"):
                        payload = adapter_for(provider).build_payload(
                            built["state"], built["questions"], adapter_for(provider).default_model)
                        serialized = json.dumps(payload, sort_keys=True)
                        self.assertNotIn("\"expected\"", serialized)
                        forbidden_keys = {"expected", "demo_answers", "category", "rationale", "fixture_id"}
                        def keys(value):
                            if isinstance(value, dict):
                                for item, child in value.items():
                                    yield item
                                    yield from keys(child)
                            elif isinstance(value, list):
                                for child in value:
                                    yield from keys(child)
                        self.assertTrue(forbidden_keys.isdisjoint(keys(payload)))
                        self.assertNotIn(json.dumps(case["expected"], sort_keys=True), serialized)

    def test_budget_reserves_before_attempt_and_retains_failed_attempt_allowance(self):
        budget = Budget(0.02, RATES)
        payload = {"state": {"evidence": "café"}, "questions": [{"name": "q"}]}
        budget.reserve("sage", payload)
        before_failure = budget.snapshot()
        self.assertEqual(before_failure["attempts"], 1)
        self.assertGreater(before_failure["reserved_usd"], 0)
        self.assertIsNone(budget.latest_charge)
        budget.record("sage", {"error": "network error"})
        self.assertEqual(budget.snapshot()["reserved_usd"], before_failure["reserved_usd"])
        self.assertEqual(budget.snapshot()["attempts"], 1)

    def test_reported_charge_above_reservations_is_a_hard_stop(self):
        budget = Budget(0.01, RATES)
        budget.reserve("sage", {"state": "tiny", "questions": [{"name": "q"}]})
        with self.assertRaises(DecisionError) as caught:
            budget.record("sage", {"usage": {"cost": 1.0}})
        self.assertEqual(caught.exception.code, "budget_estimate_exceeded")

    def test_budget_actual_estimated_and_exhaustion_semantics(self):
        budget = Budget(0.01, RATES)
        payload = {"state": "tiny", "questions": [{"name": "q"}]}
        budget.reserve("sage", payload)
        reserved = budget.snapshot()["reserved_usd"]
        budget.record("sage", {"usage": {"cost": 0.000001}})
        self.assertEqual(budget.snapshot()["provider_reported_usd"], 0.000001)
        self.assertEqual(budget.latest_charge["kind"], "provider_reported")
        budget.reserve("sage", payload)
        budget.record("sage", {"usage": {"input_tokens": 10, "output_tokens": 4}})
        self.assertEqual(budget.latest_charge["kind"], "token_price_estimate")
        self.assertGreater(budget.snapshot()["token_price_estimated_usd"], 0)
        self.assertEqual(budget.snapshot()["attempts"], 2)
        self.assertGreaterEqual(budget.snapshot()["reserved_usd"], reserved)
        with self.assertRaises(DecisionError) as caught:
            Budget(0.00000001, RATES).reserve("sage", payload)
        self.assertEqual(caught.exception.code, "budget_exhausted")
        with self.assertRaises(DecisionError) as caught:
            budget.reserve("sage", {"state": "x" * 25_000, "questions": [{"name": "q"}]})
        self.assertEqual(caught.exception.code, "invalid_request")

    def test_budget_rejects_unreviewed_or_invalid_rates(self):
        for rates in (None, {}, {"sage": {"input_per_million": 1, "output_per_million": 1}},
                      {"sage": {"source": "x", "checked_at": "y", "input_per_million": math.nan,
                                "output_per_million": 1}}):
            budget = Budget(1, rates or {})
            with self.subTest(rates=rates), self.assertRaises(DecisionError):
                budget.reserve("sage", {"state": {}, "questions": [{}]})

    def test_summary_requires_edge_case_unanimity_offline_pass_and_live_evidence(self):
        rows = []
        for i in range(12):
            category = "clear" if i < 8 else ("ambiguous" if i < 10 else "adversarial")
            for repetition in range(1, 4):
                rows.append({"provider": "sage", "skill": "input-guardrails", "case_id": str(i),
                             "category": category, "passed": True, "repetition": repetition,
                             "output": {"source": "live", "latency_ms": 10,
                                        "attempts": 1, "response": {"model": "resolved"},
                                        "result": {"action": "allow"}}})
        working = summarize(rows, ["sage"], ["input-guardrails"], 3, "live", True)["sage/input-guardrails"]
        self.assertEqual(working["status"], "Working")
        self.assertEqual(working["clear_cases_passed"], 8)
        self.assertEqual(working["live_requests"], 36)
        self.assertEqual(summarize(rows, ["sage"], ["input-guardrails"], 3, "demo", True)
                         ["sage/input-guardrails"]["status"], "Not tested")
        self.assertEqual(summarize(rows, ["sage"], ["input-guardrails"], 3, "live", False)
                         ["sage/input-guardrails"]["status"], "Partial")
        for row in rows:
            row["output"]["source"] = "deterministic"
        self.assertEqual(summarize(rows, ["sage"], ["input-guardrails"], 3, "live", True)
                         ["sage/input-guardrails"]["status"], "Partial")
        rows[0]["passed"] = False
        rows[1]["passed"] = False
        rows[2]["passed"] = False
        self.assertEqual(summarize(rows, ["sage"], ["input-guardrails"], 3, "live", True)
                         ["sage/input-guardrails"]["status"], "Partial")

    def test_summary_distinguishes_provider_block_from_partial_after_live_success(self):
        error_row = {"provider": "sage", "skill": "input-guardrails", "case_id": "x",
                     "category": "clear", "error": {"code": "authentication"}}
        status = summarize([error_row], ["sage"], ["input-guardrails"], 3, "live", True)
        self.assertEqual(status["sage/input-guardrails"]["status"], "Blocked")
        error_row["output"] = {"source": "live", "latency_ms": 10, "attempts": 1,
                                "result": {"action": "allow"}}
        status = summarize([error_row], ["sage"], ["input-guardrails"], 3, "live", True)
        self.assertEqual(status["sage/input-guardrails"]["status"], "Partial")

    def test_evaluation_receipt_keeps_expected_labels_separate_from_demo_execution(self):
        case_path = REPO / "skills" / "input-guardrails" / "fixtures" / "acceptance.json"
        original_read_text = Path.read_text
        canary = "private-expected-label-canary-97cc"
        seen = []

        def read_text(path, *args, **kwargs):
            content = original_read_text(path, *args, **kwargs)
            if Path(path).resolve() == case_path.resolve():
                rows = json.loads(content)
                rows[0]["expected"]["sentinel"] = canary
                return json.dumps(rows)
            return content

        runtime_execute = execute

        def capture(skill, provider, data, **kwargs):
            self.assertNotIn(canary, json.dumps(data))
            built = workflow_for(skill).build(dict(data, _provider=provider))
            if built["early_result"] is None:
                payload = adapter_for(provider).build_payload(
                    built["state"], built["questions"], adapter_for(provider).default_model)
                self.assertNotIn(canary, json.dumps(payload))
            seen.append(data)
            return runtime_execute(skill, provider, data, **kwargs)

        with tempfile.TemporaryDirectory(prefix="evaluation-receipt-") as temp:
            receipt_path = Path(temp) / "receipt.json"
            with patch.object(Path, "read_text", read_text), patch.object(evaluation, "execute", capture):
                receipt = evaluate_fixtures(REPO, ["sage"], "demo", 3, 1.0, receipt_path,
                                            skills=["input-guardrails"])
            loaded = json.loads(receipt_path.read_text())
        self.assertEqual(len(seen), 36)
        self.assertEqual(len(receipt["rows"]), 36)
        self.assertEqual(loaded["summary"]["sage/input-guardrails"]["status"], "Not tested")
        self.assertIsNone(loaded["budget"])
        self.assertTrue(any(canary in json.dumps(row.get("expected")) for row in loaded["rows"]))

    def test_live_evaluation_refuses_stale_offline_receipt_before_any_paid_attempt(self):
        with tempfile.TemporaryDirectory(prefix="stale-offline-") as temp:
            copied = Path(temp) / "repo"
            copied.mkdir()
            # The evaluator needs the fixture tree but uses this deliberately stale hash.
            (copied / "skills").symlink_to(REPO / "skills", target_is_directory=True)
            (copied / "src").symlink_to(REPO / "src", target_is_directory=True)
            reports = copied / "reports"
            reports.mkdir()
            (reports / "offline.json").write_text('{"passed": true, "source_hash": "stale"}')
            calls = []
            with patch.dict(os.environ, {"SAGE_API_KEY": "test-only"}, clear=True), \
                 patch.object(evaluation, "execute", side_effect=lambda *args, **kwargs: calls.append(args)):
                with self.assertRaises(DecisionError) as caught:
                    evaluate_fixtures(copied, ["sage"], "live", 3, 1.0,
                                      Path(temp) / "receipt.json", RATES, ["input-guardrails"])
            self.assertEqual(caught.exception.code, "offline_verification_required")
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
