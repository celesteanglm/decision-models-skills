"""Offline contract tests for canonical staged text-use-case evaluation."""
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch

from decision_models.contracts import DecisionError
from decision_models.evaluation import source_hash
from scripts import evaluate_usecases as evaluator
from scripts.evaluate_usecases import evaluate, payloads


def synthetic_use_case():
    return {
        "schema_version": 1,
        "id": "synthetic-candidate",
        "title": "Synthetic candidate",
        "description": "Offline test candidate.",
        "source_urls": ["https://example.invalid/source"],
        "inspiration": "Original synthetic configuration.",
        "limitations": "No actions or external calls.",
        "required_state_fields": ["content"],
        "question": {
            "name": "decision", "kind": "choice", "instructions": "Choose from supplied evidence.",
            "options": {"alpha": "First option.", "beta": "Second option.", "review": "Insufficient evidence."},
        },
        "policy": {"confidence_threshold": 0.65, "probability_threshold": 0.65, "review_choice": "review"},
    }


def fixture(case_id="case-01", *, content="Short synthetic evidence.", expected_label="alpha"):
    return {
        "id": case_id,
        "category": "clear",
        "input": {"permission_granted": True, "state": {"content": content}},
        "expected": {"actions": ["recommend"], "choice": expected_label},
        "demo_answers": {},
    }


def planned_payload(_folder, _config, _data, _provider):
    return [{"state": {"content": "synthetic"}, "questions": [{"name": "decision"}]}]


def temp_repo(root):
    repo = Path(root) / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "placeholder.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "scripts").mkdir()
    (repo / "scripts" / "usecase_reference.py").write_text("# synthetic reference\n", encoding="utf-8")
    (repo / "scripts" / "evaluate_usecases.py").write_text("# synthetic evaluator\n", encoding="utf-8")
    (repo / "reports").mkdir()
    (repo / "reports" / "offline.json").write_text(
        json.dumps({"passed": True, "source_hash": source_hash(repo)}), encoding="utf-8")
    return repo


def success_result(*, source="demo", raw=None):
    response = {"model": "offline-test-model", "usage": {"input_tokens": 1, "output_tokens": 1}}
    if raw is not None:
        response["raw_response"] = raw
    return {
        "result": {"action": "recommend", "choice": "alpha"},
        "executed_action": False,
        "attempts": 1,
        "latency_ms": 1.0,
        "response": response,
        "source": source,
    }


class ProviderCounter:
    """Thread-safe counter for evaluator's concurrent provider workers."""
    def __init__(self):
        self._counts = {}
        self._lock = threading.Lock()

    def increment(self, key):
        with self._lock:
            self._counts[key] = self._counts.get(key, 0) + 1

    def get(self, key):
        with self._lock:
            return self._counts.get(key, 0)


class UsecaseEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = temp_repo(self.root)
        self.candidate = self.root / "candidate"
        self.candidate.mkdir()
        (self.candidate / "SKILL.md").write_text("# Synthetic\n", encoding="utf-8")
        self.config = synthetic_use_case()
        (self.candidate / "decision.json").write_text(json.dumps(self.config), encoding="utf-8")
        self.cases = [fixture()]

    def tearDown(self):
        self.temp.cleanup()

    def entries_patch(self, cases=None, config=None):
        return patch.object(evaluator, "entries", return_value=[
            (self.candidate, config or self.config, list(cases if cases is not None else self.cases))
        ])

    def test_budget_preflight_rejects_full_coverage_before_any_execution(self):
        # Model a complete selected case set whose three-provider coverage cannot fit.
        cases = [fixture(f"case-{i:02}") for i in range(1, 13)]
        for index, item in enumerate(cases):
            item["category"] = "clear" if index < 8 else "ambiguous" if index < 10 else "adversarial"
        output = self.root / "too-small.json"
        called = Mock(side_effect=AssertionError("preflight must precede all execution"))
        with self.entries_patch(cases), patch.object(evaluator, "payloads", side_effect=planned_payload), \
                patch.object(evaluator, "execute_custom", called):
            with self.assertRaises(DecisionError) as caught:
                evaluate(self.repo, self.root / "candidate-root", output, "demo", 1e-10, 0.0)
        self.assertEqual(caught.exception.code, "budget_exhausted")
        called.assert_not_called()
        self.assertFalse(output.exists())
        self.assertFalse(output.with_suffix(".jsonl").exists())

    def test_negative_or_nonfinite_limits_and_historical_bounds_reject_before_execution(self):
        invalid = [-0.1, float("nan"), float("inf"), float("-inf")]
        for field in ("limit", "historical_bound"):
            for value in invalid:
                with self.subTest(field=field, value=value):
                    output = self.root / f"invalid-{field}-{str(value).replace('-', 'm')}.json"
                    called = Mock(return_value=success_result())
                    kwargs = {"limit": 2.5, "historical_bound": 0.0}
                    kwargs[field] = value
                    with self.entries_patch(), patch.object(evaluator, "payloads", side_effect=planned_payload), \
                            patch.object(evaluator, "execute_custom", called):
                        with self.assertRaises(DecisionError) as caught:
                            evaluate(self.repo, self.root / "candidate-root", output, "demo", **kwargs)
                    self.assertEqual(caught.exception.code, "invalid_request")
                    called.assert_not_called()
                    self.assertFalse(output.exists())

    def test_existing_receipt_or_journal_refuses_before_any_execution(self):
        for preexisting in ("receipt", "journal"):
            with self.subTest(path=preexisting):
                output = self.root / f"immutable-{preexisting}.json"
                target = output if preexisting == "receipt" else output.with_suffix(".jsonl")
                target.write_text("preserve this evidence\n", encoding="utf-8")
                called = Mock(side_effect=AssertionError("immutable paths must be checked first"))
                with self.entries_patch(), patch.object(evaluator, "payloads", side_effect=planned_payload), \
                        patch.object(evaluator, "execute_custom", called):
                    with self.assertRaises(DecisionError) as caught:
                        evaluate(self.repo, self.root / "candidate-root", output, "demo", 2.5, 0.0)
                self.assertEqual(caught.exception.code, "invalid_request")
                called.assert_not_called()
                self.assertEqual(target.read_text(encoding="utf-8"), "preserve this evidence\n")

    def test_timeout_stops_same_backend_repetitions_and_other_backends_continue(self):
        output = self.root / "timeouts.json"
        calls = ProviderCounter()
        raw = {"usage": {"input_tokens": 2, "output_tokens": 1}, "opaque": "retained"}

        def run(folder, provider, data, *, mode, before_attempt, after_attempt, **kwargs):
            calls.increment(provider)
            before_attempt(provider, planned_payload(folder, self.config, data, provider)[0])
            if provider == "sage":
                # A response was received and charged, but the request then timed out.
                after_attempt(provider, raw)
                raise DecisionError("timeout", "synthetic timeout after response")
            after_attempt(provider, raw)
            return success_result(source="live", raw=raw)

        with self.entries_patch(), patch.object(evaluator, "payloads", side_effect=planned_payload), \
                patch.object(evaluator, "execute_custom", side_effect=run):
            receipt = evaluate(self.repo, self.root / "candidate-root", output, "live", 2.5, 0.0)

        counts = {provider: calls.get(provider) for provider in evaluator.RATES}
        self.assertEqual(counts, {"sage": 1, "jev-openrouter": 3, "openai-decisions": 3})
        rows = receipt["rows"]
        self.assertEqual(sum(row["provider"] == "sage" for row in rows), 1)
        failed = next(row for row in rows if row["provider"] == "sage")
        self.assertEqual(failed["error"]["code"], "timeout")
        self.assertEqual(failed["charges"][0]["kind"], "token_price_estimate")
        self.assertEqual(failed["raw_response"], raw)
        self.assertEqual(sum(row["provider"] == "jev-openrouter" for row in rows), 3)
        self.assertEqual(sum(row["provider"] == "openai-decisions" for row in rows), 3)

    def test_payloads_exclude_expected_labels_and_fixture_metadata(self):
        secret = "SECRET_EXPECTED_LABEL"
        data = {
            "permission_granted": True,
            "state": {"content": "A supplied evidence passage."},
            "expected": {"choice": secret},
            "category": "hidden-fixture-category",
            "demo_answers": {"decision": {"choice": secret}},
            "fixture_id": "hidden-case-42",
        }

        for provider in evaluator.RATES:
            with self.subTest(provider=provider):
                built = payloads(self.candidate, self.config, data, provider)
                self.assertEqual(len(built), 1)
                serialized = json.dumps(built[0], sort_keys=True)
                self.assertIn("A supplied evidence passage.", serialized)
                for hidden in (secret, "expected", "demo_answers", "hidden-fixture-category", "hidden-case-42"):
                    self.assertNotIn(hidden, serialized)

    def test_mocked_usage_charge_and_raw_response_are_preserved(self):
        output = self.root / "charges.json"
        calls = ProviderCounter()
        raw = {"usage": {"input_tokens": 3, "output_tokens": 2}, "opaque": {"trace": "raw-provider-value"}}
        untouched = json.loads(json.dumps(raw))

        def run(folder, provider, data, *, mode, before_attempt, after_attempt, **kwargs):
            calls.increment(provider)
            before_attempt(provider, planned_payload(folder, self.config, data, provider)[0])
            after_attempt(provider, raw)
            return success_result(source="live", raw=raw)

        with self.entries_patch(), patch.object(evaluator, "payloads", side_effect=planned_payload), \
                patch.object(evaluator, "execute_custom", side_effect=run):
            receipt = evaluate(self.repo, self.root / "candidate-root", output, "live", 2.5, 0.0)

        self.assertEqual(raw, untouched)
        self.assertEqual(calls.get("sage"), 3)
        self.assertTrue(all(row["charges"] for row in receipt["rows"]))
        for row in receipt["rows"]:
            self.assertEqual(row["charges"][0]["kind"], "token_price_estimate")
            self.assertEqual(row["output"]["response"]["raw_response"], untouched)
        self.assertGreater(receipt["budget"]["token_price_estimated_usd"], 0)


if __name__ == "__main__":
    unittest.main()
