import json
from pathlib import Path
import unittest

from decision_models.contracts import DecisionError, validate_questions, validate_response
from decision_models.workflows import confidence_gates, output_evaluation

ROOT = Path(__file__).parents[1]


def load_fixture(slug, fixture_id):
    entries = json.loads((ROOT / "skills" / slug / "fixtures" / "acceptance.json").read_text())
    return next(item for item in entries if item["id"] == fixture_id)


def canonical_response(questions, answers):
    response = {"model": "test-model", "answers": answers, "usage": None, "raw_response": None}
    return validate_response(response, questions)


class EvaluationWorkflowTests(unittest.TestCase):
    def test_acceptance_fixtures_have_required_balance_and_policy_outcomes(self):
        for slug, workflow in (("confidence-gates", confidence_gates), ("output-evaluation", output_evaluation)):
            items = json.loads((ROOT / "skills" / slug / "fixtures/acceptance.json").read_text())
            self.assertEqual(len(items), 12)
            self.assertEqual({cat: sum(x["category"] == cat for x in items) for cat in ("clear", "ambiguous", "adversarial")}, {
                "clear": 8, "ambiguous": 2, "adversarial": 2
            })
            for item in items:
                prepared = workflow.build(item["input"])
                if prepared["early_result"] is not None:
                    result = prepared["early_result"]
                else:
                    validate_questions(prepared["questions"])
                    response = canonical_response(prepared["questions"], item["demo_answers"])
                    result = workflow.decide(item["input"], response)
                self.assertIn(result["action"], item["expected"]["actions"], item["id"])
                self.assertTrue(item["expected"].get("rationale"))

    def test_confidence_gate_reviews_missing_evidence_before_inference(self):
        data = {"draft": "A statement", "evidence": [], "rubric": ["Supported"]}
        result = confidence_gates.build(data)
        self.assertEqual(result["questions"], [])
        self.assertEqual(result["early_result"], {"action": "review", "reasons": ["no_evidence_supplied"]})

    def test_confidence_gate_uses_provider_specific_thresholds_and_escalates_high_risk(self):
        data = {"draft": "Claim", "evidence": ["Evidence"], "rubric": ["criterion"], "risk_level": "routine"}
        prepared = confidence_gates.build(data)
        response = canonical_response(prepared["questions"], {
            "evidence_support": {"kind": "predicate", "status": "answered", "probability_true": .85},
            "rubric_satisfied": {"kind": "predicate", "status": "answered", "probability_true": .90},
        })
        self.assertEqual(confidence_gates.decide(dict(data, _provider="jev-openrouter"), response)["action"], "review")
        self.assertEqual(confidence_gates.decide(dict(data, _provider="sage"), response)["action"], "send")
        high_risk = confidence_gates.build(dict(data, risk_level="high"))
        self.assertEqual(high_risk["questions"], [])
        self.assertEqual(high_risk["early_result"]["action"], "escalate")

    def test_confidence_refusal_returns_review(self):
        data = {"draft": "Claim", "evidence": ["Evidence"], "rubric": ["criterion"]}
        prepared = confidence_gates.build(data)
        response = {"answers": {"evidence_support": {"status": "refusal"}, "rubric_satisfied": {"status": "answered"}}}
        self.assertEqual(confidence_gates.decide(data, response)["action"], "review")

    def test_output_evaluation_keeps_metrics_separate_and_checks_action_markers(self):
        fixture = load_fixture("output-evaluation", "clear-05")
        prepared = output_evaluation.build(fixture["input"])
        response = canonical_response(prepared["questions"], fixture["demo_answers"])
        result = output_evaluation.decide(fixture["input"], response)
        self.assertEqual(result["action"], "pass")
        self.assertEqual(set(result["metrics"]), {
            "grounded_probability", "relevant_probability", "action_honest_probability", "helpfulness_score"
        })
        bad = dict(fixture["input"], response="Done. [[action:missing]]")
        self.assertEqual(output_evaluation.decide(bad, response)["action"], "fail")

    def test_output_evaluation_checks_natural_language_action_claims_against_results(self):
        fixture = load_fixture("output-evaluation", "clear-08")
        prepared = output_evaluation.build(fixture["input"])
        instructions = next(q["instructions"] for q in prepared["questions"] if q["name"] == "action_honest")
        self.assertIn("ordinary natural-language", instructions)
        response = canonical_response(prepared["questions"], fixture["demo_answers"])
        result = output_evaluation.decide(fixture["input"], response)
        self.assertEqual(result["action"], "fail")
        self.assertEqual(fixture["input"]["tool_results"][0]["action_id"], "refund-lookup-R-41")

    def test_output_refusal_and_malformed_action_claim_are_review_or_fail(self):
        data = {"request": "Do it", "response": "Done", "evidence": [], "tool_results": []}
        prepared = output_evaluation.build(data)
        refusal = {"answers": {name: {"status": "refusal"} for name in ("grounded", "relevant", "action_honest", "helpfulness")}}
        self.assertEqual(output_evaluation.decide(data, refusal)["action"], "review")
        answers = {
            "grounded": {"kind": "predicate", "status": "answered", "probability_true": .9},
            "relevant": {"kind": "predicate", "status": "answered", "probability_true": .9},
            "action_honest": {"kind": "predicate", "status": "answered", "probability_true": .9},
            "helpfulness": {"kind": "score", "status": "answered", "score": 3, "probabilities": {"0":0,"1":0,"2":0,"3":1,"4":0}},
        }
        response = canonical_response(prepared["questions"], answers)
        malformed = dict(data, response="Done [[action:incomplete")
        self.assertEqual(output_evaluation.decide(malformed, response)["action"], "fail")

    def test_workflows_reject_invalid_application_inputs(self):
        with self.assertRaises(DecisionError):
            confidence_gates.build({"draft": "x", "evidence": [""], "rubric": ["ok"]})
        with self.assertRaises(DecisionError):
            output_evaluation.build({"request": "x", "response": "y", "evidence": [], "tool_results": [{"action_id": "a", "status": "unknown"}]})


if __name__ == "__main__":
    unittest.main()
