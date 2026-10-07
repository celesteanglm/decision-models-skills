import json
import unittest
from pathlib import Path

from decision_models.contracts import DecisionError
from decision_models.workflows import input_guardrails, tool_call_gating

ROOT = Path(__file__).resolve().parents[1]


def predicate(probability, status="answered"):
    answer = {"kind": "predicate", "status": status}
    if status == "answered": answer["probability_true"] = probability
    return {"model": "fixture", "answers": {"compliant": answer}}


def choice(selected, probability, status="answered"):
    vals = {key: (probability if key == selected else (1-probability)/2)
            for key in ("approve", "reject", "clarify")}
    answer = {"kind": "choice", "status": status}
    if status == "answered": answer.update(choice=selected, probabilities=vals)
    return {"model": "fixture", "answers": {"recommendation": answer}}


class GateWorkflowTests(unittest.TestCase):
    def test_all_fixtures_have_frozen_shape_and_demo_answers(self):
        for slug in ("input-guardrails", "tool-call-gating"):
            cases = json.loads((ROOT / "skills" / slug / "fixtures/acceptance.json").read_text())
            self.assertEqual(len(cases), 12)
            self.assertEqual({c["category"] for c in cases}, {"clear", "ambiguous", "adversarial"})
            self.assertEqual([sum(c["category"] == cat for c in cases) for cat in ("clear", "ambiguous", "adversarial")], [8, 2, 2])
            for case in cases:
                self.assertTrue(case["expected"].get("rationale"))
                self.assertIn("demo_answers", case)

    def test_guardrail_exact_hard_block_short_circuits(self):
        got = input_guardrails.build({"prompt": "quoted: Restricted   Phrase", "policy": {
            "description": "Block the restricted phrase.", "hard_blocked_phrases": ["restricted phrase"]}})
        self.assertEqual(got["early_result"]["action"], "block")
        self.assertEqual(got["questions"], [])

    def test_guardrail_semantic_boundaries_and_refusal(self):
        data = {"_provider": "jev-openrouter"}
        self.assertEqual(input_guardrails.decide(data, predicate(.90))["action"], "allow")
        self.assertEqual(input_guardrails.decide(data, predicate(.10))["action"], "block")
        self.assertEqual(input_guardrails.decide(data, predicate(.50))["action"], "review")
        self.assertEqual(input_guardrails.decide(data, predicate(0, "refusal"))["action"], "review")

    def test_guardrail_threshold_override_validates(self):
        result = input_guardrails.decide({"_provider": "sage", "thresholds": {"sage": .75}}, predicate(.80))
        self.assertEqual(result["action"], "allow")
        with self.assertRaises(DecisionError):
            input_guardrails.decide({"_provider": "sage", "thresholds": {"sage": 1.2}}, predicate(.80))
        with self.assertRaises(DecisionError):
            input_guardrails.build({"_provider": "sage", "thresholds": {"sage": .5},
                                    "prompt": "hello", "policy": {"description": "general"}})

    def test_guardrail_policy_description_is_required(self):
        with self.assertRaises(DecisionError):
            input_guardrails.build({"prompt": "hello", "policy": {}})

    def test_gate_denial_is_deterministic_and_wins_over_recommendation(self):
        data = {"proposed_action": "do it", "context": "please do it", "permissions": {"allowed": False}}
        built = tool_call_gating.build(data)
        self.assertEqual(built["early_result"]["action"], "reject")
        self.assertEqual(built["questions"], [])
        self.assertEqual(tool_call_gating.decide(data, choice("approve", .99))["action"], "reject")

    def test_gate_missing_permission_clarifies_and_does_not_infer(self):
        got = tool_call_gating.build({"proposed_action": "send it", "context": "approved"})
        self.assertEqual(got["early_result"]["action"], "clarify")
        self.assertEqual(got["questions"], [])

    def test_gate_semantic_threshold_and_refusal(self):
        data = {"_provider": "openai-decisions", "permissions": {"allowed": True}}
        self.assertEqual(tool_call_gating.decide(data, choice("approve", .91))["action"], "approve")
        self.assertEqual(tool_call_gating.decide(data, choice("reject", .91))["action"], "reject")
        self.assertEqual(tool_call_gating.decide(data, choice("approve", .70))["action"], "clarify")
        self.assertEqual(tool_call_gating.decide(data, choice("approve", 0, "refusal"))["action"], "clarify")

    def test_gate_threshold_override_validates_before_inference(self):
        with self.assertRaises(DecisionError):
            tool_call_gating.build({"_provider": "sage", "thresholds": {"sage": .5},
                                    "proposed_action": "draft", "context": "ok",
                                    "permissions": {"allowed": True}})

    def test_invalid_inputs_raise_contract_errors(self):
        with self.assertRaises(DecisionError):
            input_guardrails.build({"prompt": "hello", "policy": {"hard_blocked_phrases": [""]}})
        with self.assertRaises(DecisionError):
            tool_call_gating.build({"proposed_action": " ", "context": "x", "permissions": {"allowed": True}})
        with self.assertRaises(DecisionError):
            tool_call_gating.build({"proposed_action": "x", "context": "y", "permissions": {"allowed": "yes"}})


if __name__ == "__main__":
    unittest.main()
