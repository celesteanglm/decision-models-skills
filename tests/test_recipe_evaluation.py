"""Frozen recipe evaluation's coverage, outcome oracle, and stop conditions."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.evaluation import acceptance
from decision_models.recipe_evaluation import (
    catalog,
    evaluate_recipes,
    preflight,
    source_hash,
)
from decision_models.runtime import adapter_for
from decision_models.recipes import prepare_recipe
import decision_models.recipe_evaluation as recipe_evaluation


REPO = Path(__file__).resolve().parents[1]
RATES = {"sage": {"source": "synthetic test rate", "checked_at": "2026-10-08",
                   "input_per_million": 0.01, "output_per_million": 0.01}}


def copied_recipe_repo(root):
    repo = root / "recipe-repo"
    shutil.copytree(REPO / "recipes", repo / "recipes")
    reports = repo / "reports"
    reports.mkdir()
    (reports / "offline.json").write_text(json.dumps({
        "passed": True, "source_hash": source_hash(repo),
    }), encoding="utf-8")
    return repo


class RecipeEvaluationTests(unittest.TestCase):
    def test_preflight_reserves_full_three_run_coverage_and_skips_deterministic_inputs(self):
        entries = catalog(REPO)
        plan = preflight(REPO, ["sage"], RATES, repetitions=3)
        expected_attempts = sum(
            3 for recipe, cases in entries for case in cases
            if prepare_recipe(recipe, case["input"]) is None
        )
        self.assertEqual(plan["recipe_count"], len(entries))
        self.assertEqual(plan["fixture_evaluations"], len(entries) * 12 * 3)
        self.assertEqual(plan["providers"]["sage"]["requests"], expected_attempts)
        self.assertGreater(expected_attempts, 0)
        self.assertGreater(plan["providers"]["sage"]["reserved_usd"], 0)
        self.assertAlmostEqual(
            plan["reserved_usd"], plan["providers"]["sage"]["reserved_usd"]
        )

    def test_budget_shortfall_fails_before_any_recipe_dispatch(self):
        with tempfile.TemporaryDirectory(prefix="recipe-budget-gate-") as temp:
            repo = copied_recipe_repo(Path(temp))
            output = Path(temp) / "receipt.json"
            with patch.object(recipe_evaluation, "execute_recipe") as execute:
                with self.assertRaises(DecisionError) as raised:
                    evaluate_recipes(repo, ["sage"], "live", 3, 0.000001,
                                     output, rates=RATES)
            self.assertEqual(raised.exception.code, "budget_exhausted")
            execute.assert_not_called()
            self.assertFalse(output.exists())

    def test_acceptance_checks_expected_choice_and_stability_includes_choice(self):
        passed, failures = acceptance(
            {"result": {"action": "recommend", "choice": "approved"}},
            {"actions": ["recommend"], "choice": "rejected"},
        )
        self.assertFalse(passed)
        self.assertEqual(failures, ["choice"])

        rows = []
        for case_index in range(12):
            for repetition in range(3):
                choice = "first" if case_index else ("first" if repetition < 2 else "second")
                rows.append({
                    "provider": "sage", "skill": "sample-recipe", "recipe": "sample-recipe",
                    "case_id": f"case-{case_index}", "category": "clear", "repetition": repetition + 1,
                    "passed": True, "safety_violation": False,
                    "output": {"source": "live", "latency_ms": 4,
                               "response": {"model": "resolved-test-model"},
                               "result": {"action": "recommend", "choice": choice}},
                })
        summary = recipe_evaluation.summarize(
            rows, ["sage"], ["sample-recipe"], 3, "live", offline_passed=True,
        )["sage/sample-recipe"]
        self.assertEqual(summary["stable_cases"], 11)

    def test_allowed_choices_can_retain_safe_ambiguity_without_accepting_other_actions(self):
        expected = {"actions": ["review", "recommend"],
                    "choices": ["review", "clarify"]}
        for safe_choice in ("review", "clarify"):
            with self.subTest(choice=safe_choice):
                self.assertEqual(acceptance(
                    {"result": {"action": "review", "choice": safe_choice}}, expected,
                ), (True, []))

        self.assertEqual(acceptance(
            {"result": {"action": "recommend", "choice": "approve"}}, expected,
        ), (False, ["choice"]))

    def test_unknown_charge_timeout_stops_backend_without_repeating_the_fixture(self):
        with tempfile.TemporaryDirectory(prefix="recipe-timeout-stop-") as temp:
            root = Path(temp)
            repo = copied_recipe_repo(root)
            output = root / "receipt.json"
            calls = []

            def unknown_charge_timeout(recipe, provider, data, *, before_attempt=None, **_kwargs):
                calls.append((recipe["id"], data))
                payload = adapter_for(provider).build_payload(
                    data["state"], [recipe["question"]], adapter_for(provider).default_model,
                )
                before_attempt(provider, payload)
                raise DecisionError("timeout", "charge status is unknown")

            with patch.object(recipe_evaluation, "execute_recipe", side_effect=unknown_charge_timeout):
                receipt = evaluate_recipes(repo, ["sage"], "live", 3, 5,
                                           output, rates=RATES)

            self.assertEqual(len(calls), 1)
            self.assertEqual(len(receipt["rows"]), 1)
            row = receipt["rows"][0]
            self.assertEqual(row["error"]["code"], "timeout")
            self.assertEqual(row["attempts"], 1)
            self.assertIsNone(row["charge"])
            self.assertEqual(receipt["budgets"]["sage"]["attempts"], 1)
            journal_rows = output.with_suffix(".jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(journal_rows), 1)

    def test_malformed_fixture_catalog_is_rejected_before_evaluation(self):
        source = next((REPO / "recipes").glob("*/recipe.json")).parent
        with tempfile.TemporaryDirectory(prefix="bad-recipe-fixture-") as temp:
            repo = Path(temp) / "repo"
            recipe_target = repo / "recipes" / source.name
            shutil.copytree(source, recipe_target)
            fixtures_path = recipe_target / "fixtures" / "acceptance.json"
            fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
            fixtures.pop()
            fixtures_path.write_text(json.dumps(fixtures), encoding="utf-8")
            with self.assertRaises(DecisionError) as raised:
                catalog(repo)
            self.assertEqual(raised.exception.code, "invalid_request")

    def test_frozen_fixture_choices_are_explicit_and_belong_to_the_recipe_menu(self):
        for recipe, cases in catalog(REPO):
            menu = set(recipe["question"]["options"])
            substantive = menu - {"review"}
            with self.subTest(recipe=recipe["id"]):
                for case in cases:
                    expected = case["expected"]
                    if case["category"] == "clear":
                        self.assertIn("choice", expected, case["id"])
                        self.assertIn(expected["choice"], substantive, case["id"])
                    elif case["category"] == "ambiguous":
                        allowed = ([expected["choice"]] if "choice" in expected
                                   else expected.get("choices"))
                        self.assertIsInstance(allowed, list, case["id"])
                        self.assertTrue(allowed, case["id"])
                        self.assertLessEqual(set(allowed), menu, case["id"])
                    elif case["category"] == "adversarial":
                        if case["input"].get("permission_granted") is False:
                            self.assertEqual(expected["actions"], ["deny"], case["id"])
                            self.assertIsNone(expected.get("choice"), case["id"])
                        else:
                            self.assertIs(case["input"].get("permission_granted"), True, case["id"])
                            self.assertEqual(expected["actions"], ["recommend"], case["id"])
                            self.assertIn("choice", expected, case["id"])
                            self.assertIn(expected["choice"], substantive, case["id"])


if __name__ == "__main__":
    unittest.main()
