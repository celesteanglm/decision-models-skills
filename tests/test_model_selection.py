"""Current live entrypoints require intentional Sage model selection."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from decision_models.cli import main
from decision_models.contracts import DecisionError
from decision_models.evaluation import evaluate_fixtures
from decision_models.runtime import validate_model_selection
from decision_models.use_case_evaluation import evaluate_use_cases, preflight

REPO = Path(__file__).resolve().parents[1]


class ModelSelectionTests(unittest.TestCase):
    def test_sage_live_commands_fail_before_loading_input_or_dispatch(self):
        commands = [
            ["run", "input-guardrails", "--provider", "sage", "--input", "missing", "--mode", "live"],
            ["decide", "--provider", "sage", "--config", "missing", "--input", "missing", "--mode", "live"],
            ["smoke", "--provider", "sage"],
            ["evaluate", "--providers", "sage", "--repo", "missing", "--output", "missing", "--mode", "live"],
            ["evaluate-use-cases", "--providers", "sage", "--repo", "missing", "--output", "missing", "--mode", "live"],
        ]
        for command in commands:
            with self.subTest(command=command), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(command), 2)
            error = json.loads(output.getvalue())["error"]
            self.assertEqual(error["code"], "invalid_request")
            self.assertIn("explicit model", error["message"])

    def test_explicit_model_is_forwarded_by_both_evaluation_commands(self):
        for command, target in (("evaluate", "decision_models.evaluation.evaluate_fixtures"),
                                ("evaluate-use-cases", "decision_models.use_case_evaluation.evaluate_use_cases")):
            with self.subTest(command=command), patch(target, return_value={"summary": {}, "budget": {}}) as evaluate, \
                 patch("decision_models.use_case_evaluation.write_use_case_report"), \
                 contextlib.redirect_stdout(io.StringIO()):
                code = main([command, "--repo", ".", "--providers", "sage", "--model", "levanto-sage-v1.4",
                             "--output", "unused.json", "--mode", "demo"])
                self.assertEqual(code, 0)
                self.assertEqual(evaluate.call_args.kwargs["model"], "levanto-sage-v1.4")

    def test_library_evaluators_also_reject_implicit_historical_sage_model(self):
        for evaluator in (evaluate_fixtures, evaluate_use_cases):
            with self.subTest(evaluator=evaluator.__name__), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(DecisionError) as caught:
                    evaluator(Path(temp), ["sage"], "live", 3, 5, Path(temp) / "receipt.json")
                self.assertEqual(caught.exception.code, "invalid_request")
                self.assertFalse((Path(temp) / "receipt.json").exists())

    def test_model_override_cannot_accidentally_apply_to_multiple_providers(self):
        for model in ("shared-model", "", 4):
            with self.subTest(model=model), self.assertRaises(DecisionError):
                validate_model_selection(["sage", "jev-openrouter"], "live", model)
        validate_model_selection(["sage"], "live", "levanto-sage-v1.4")
        validate_model_selection(["jev-openrouter"], "live", None)

    def test_preflight_builds_the_same_explicit_model_that_execution_uses(self):
        from decision_models.runtime import adapter_for
        adapter = adapter_for("sage")
        built = []
        original = adapter.build_payload

        def capture(state, questions, model):
            built.append(model)
            return original(state, questions, model)

        rates = {"sage": {"source": "synthetic", "checked_at": "2026-10-28",
                           "input_per_million": 0.01, "output_per_million": 0.01}}
        with patch.object(adapter, "build_payload", side_effect=capture), \
             patch("decision_models.use_case_evaluation.adapter_for", return_value=adapter):
            preflight(REPO, ["sage"], rates, model="levanto-sage-v1.4")
        self.assertTrue(built)
        self.assertEqual(set(built), {"levanto-sage-v1.4"})
