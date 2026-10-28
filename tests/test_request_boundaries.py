import os
import unittest
from pathlib import Path
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.runtime import execute
from decision_models.transport import encode_payload, http_transport
from decision_models.use_cases import execute_use_case, load_use_case


class RequestBoundaryTests(unittest.TestCase):
    def test_non_json_values_nonfinite_numbers_and_invalid_utf8_fail_before_determinism_or_hooks(self):
        cases = (
            {"prompt": "ordinary", "context": {"bad": float("nan")}, "permissions": {"allowed": False}},
            {"prompt": "ordinary", "context": {"bad": {1, 2}}, "permissions": {"allowed": False}},
            {"prompt": "\ud800", "policy": {"description": "safe"}},
        )
        for data in cases:
            calls = []
            with self.subTest(data=data), self.assertRaises(DecisionError) as caught:
                execute("input-guardrails", "sage", data, mode="live",
                        before_attempt=lambda *args: calls.append("reservation"),
                        transport=lambda *args: calls.append("network"))
            self.assertEqual(caught.exception.code, "invalid_request")
            self.assertEqual(calls, [])

    def test_invalid_payload_from_adapter_fails_before_attempt_hook(self):
        class InvalidPayloadAdapter:
            endpoint = "https://example.invalid"
            key_env = "CUSTOM_TEST_KEY"
            default_model = "custom"

            def build_payload(self, state, questions, model):
                return {"set": {"not", "json"}}

        calls = []
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("input-guardrails", "custom", {
                    "prompt": "hello", "policy": {"description": "safe"}}, mode="live",
                    adapter=InvalidPayloadAdapter(), before_attempt=lambda *args: calls.append("reservation"),
                    transport=lambda *args: calls.append("network"))
        self.assertEqual(caught.exception.code, "invalid_request")
        self.assertEqual(calls, [])

    def test_use_case_utf8_validation_happens_before_attempt_hook(self):
        use_case_path = sorted((Path(__file__).resolve().parents[1] / "skills").glob("*/decision.json"))[0]
        use_case = load_use_case(use_case_path)
        data = {"permission_granted": True,
                "state": {field: "evidence" for field in use_case["required_state_fields"]},
                "extra": "\ud800"}
        calls = []
        with self.assertRaises(DecisionError) as caught:
            execute_use_case(use_case, "sage", data, mode="live",
                             before_attempt=lambda *args: calls.append("reservation"),
                             transport=lambda *args: calls.append("network"))
        self.assertEqual(caught.exception.code, "invalid_request")
        self.assertEqual(calls, [])

    def test_transport_uses_the_same_finite_utf8_json_validator(self):
        for payload in ({"x": float("nan")}, {"x": {1}}, {"x": "\ud800"}):
            with self.subTest(payload=payload), self.assertRaises(DecisionError) as caught:
                encode_payload(payload)
            self.assertEqual(caught.exception.code, "invalid_request")
        with patch("decision_models.transport.urllib.request.build_opener") as opener:
            with self.assertRaises(DecisionError):
                http_transport("https://example.invalid", {"x": "\ud800"}, "test")
            opener.assert_not_called()

    def test_unknown_output_provider_requires_policy_before_reservation(self):
        class Adapter:
            endpoint = "https://example.invalid"
            key_env = "CUSTOM_TEST_KEY"
            default_model = "custom"

            def build_payload(self, state, questions, model):
                return {"state": state, "questions": questions}

        calls = []
        with patch.dict(os.environ, {"CUSTOM_TEST_KEY": "test-key"}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("output-evaluation", "custom", {
                    "request": "Summarize", "response": "The answer.", "evidence": [], "tool_results": []},
                    mode="live", adapter=Adapter(), before_attempt=lambda *args: calls.append("reservation"),
                    transport=lambda *args: calls.append("network"))
        self.assertEqual(caught.exception.code, "invalid_request")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
