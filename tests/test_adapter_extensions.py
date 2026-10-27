import os
import unittest
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.runtime import execute


class TextAdapter:
    endpoint = "https://example.invalid/decide"
    key_env = "CUSTOM_TEST_KEY"
    default_model = "custom-text-model"

    def build_payload(self, state, questions, model):
        return {"input": state, "questions": questions, "model": model}

    def parse_response(self, raw, questions):
        return raw


class AdapterExtensionTests(unittest.TestCase):
    def test_custom_adapter_executes_general_workflow_with_fake_transport(self):
        seen = []

        def fake_transport(endpoint, payload, key, timeout):
            seen.append((endpoint, payload, key, timeout))
            return {"model": "resolved-custom", "answers": {"compliant": {
                "kind": "predicate", "status": "answered", "probability_true": 0.93}}}

        data = {"prompt": "A harmless request", "policy": {"description": "Allow ordinary requests."}}
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            result = execute("input-guardrails", "custom-provider", data, mode="live",
                             adapter=TextAdapter(), transport=fake_transport)
        self.assertEqual(result["result"]["action"], "allow")
        self.assertEqual(result["response"]["model"], "resolved-custom")
        self.assertEqual(seen[0][0], "https://example.invalid/decide")
        self.assertEqual(seen[0][2:], ("test-key", 20))
        self.assertEqual(seen[0][1]["input"]["prompt"], "A harmless request")

    def test_malformed_custom_canonical_response_fails_at_runtime_boundary(self):
        class BadAdapter(TextAdapter):
            def parse_response(self, raw, questions):
                return {"model": "bad", "answers": {}}

        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("input-guardrails", "custom-provider", {
                    "prompt": "A harmless request", "policy": {"description": "Allow ordinary requests."}},
                    mode="live", adapter=BadAdapter(), transport=lambda *args: {})
        self.assertEqual(caught.exception.code, "invalid_response")

    def test_unknown_provider_confidence_policy_is_required_before_attempt(self):
        attempts = []
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("confidence-gates", "custom-provider", {
                    "draft": "A statement", "evidence": ["Evidence"], "rubric": ["Supported"]},
                    mode="live", adapter=TextAdapter(), transport=lambda *args: {},
                    before_attempt=lambda *args: attempts.append(args))
        self.assertEqual(caught.exception.code, "invalid_request")
        self.assertEqual(attempts, [])

    def test_custom_confidence_policy_is_trusted_and_controls_unknown_provider(self):
        class ConfidenceAdapter(TextAdapter):
            def parse_response(self, raw, questions):
                return {"model": "resolved-custom", "answers": {
                    q["name"]: {"kind": "predicate", "status": "answered",
                                "probability_true": (0.89 if q["name"] == "evidence_support" else 0.99)}
                    for q in questions}}

        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            result = execute("confidence-gates", "custom-provider", {
                "draft": "A statement", "evidence": ["Evidence"], "rubric": ["Supported"]},
                mode="live", adapter=ConfidenceAdapter(), transport=lambda *args: {},
                policy={"send": 0.9, "escalate_below": 0.2})
        self.assertEqual(result["result"]["action"], "review")
        self.assertEqual(result["result"]["reasons"], ["evidence_or_rubric_below_send_threshold"])

    def test_input_cannot_spoof_runtime_policy(self):
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            result = execute("confidence-gates", "custom-provider", {
                "draft": "A statement", "evidence": ["Evidence"], "rubric": ["Supported"],
                "_policy": {"send": 0, "escalate_below": 1}},
                mode="live", adapter=TextAdapter(), policy={"send": 1, "escalate_below": 0},
                transport=lambda endpoint, payload, key, timeout: {
                    "model": "resolved", "answers": {
                        "evidence_support": {"kind": "predicate", "status": "answered", "probability_true": 0.9},
                        "rubric_satisfied": {"kind": "predicate", "status": "answered", "probability_true": 0.9}}})
        self.assertEqual(result["result"]["action"], "review")
        self.assertEqual(result["result"]["thresholds"], {"send": 1, "escalate_below": 0})

    def test_custom_output_policy_can_pass_and_review_without_registry_edits(self):
        data = {"request": "Summarize", "response": "A supported summary.",
                "evidence": ["Source facts."], "tool_results": []}
        answers = {name: {"kind": "predicate", "status": "answered", "probability_true": 0.9}
                   for name in ("grounded", "relevant", "action_honest")}
        answers["helpfulness"] = {"kind": "score", "status": "answered", "score": 4,
                                  "probabilities": {str(i): float(i == 4) for i in range(5)}}
        for threshold, expected in ((0.85, "pass"), (0.95, "review")):
            with self.subTest(threshold=threshold), \
                 patch.dict(os.environ, {"CUSTOM_TEST_KEY": "synthetic-test"}, clear=True):
                output = execute("output-evaluation", "custom-provider", data, mode="live",
                                 adapter=TextAdapter(),
                                 policy={"grounded": threshold, "relevant": threshold,
                                         "helpfulness": 3.5, "fail_below": 0.2},
                                 transport=lambda *args: {"model": "custom", "answers": answers})
            self.assertEqual(output["result"]["action"], expected)

    def test_invalid_custom_policy_is_rejected_before_request_reservation(self):
        cases = [
            ("confidence-gates", {"draft": "A", "evidence": ["A"], "rubric": ["Supported"]},
             {"send": 0.9, "escalate_below": True}),
            ("confidence-gates", {"draft": "A", "evidence": ["A"], "rubric": ["Supported"]},
             {"send": 0.2, "escalate_below": 0.3}),
            ("output-evaluation", {"request": "A", "response": "A", "evidence": [], "tool_results": []},
             {"grounded": 0.9, "relevant": 0.9, "helpfulness": float('nan'), "fail_below": 0.2}),
        ]
        for skill, data, policy in cases:
            calls = []
            with self.subTest(skill=skill, policy=policy), self.assertRaises(DecisionError) as caught:
                execute(skill, "custom-provider", data, mode="live", adapter=TextAdapter(), policy=policy,
                        before_attempt=lambda *args: calls.append("reserved"),
                        transport=lambda *args: calls.append("network"))
            self.assertEqual(caught.exception.code, "invalid_request")
            self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
