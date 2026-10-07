import os
import unittest
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.runtime import execute


class RuntimeTests(unittest.TestCase):
    def test_invalid_inputs_and_demo_answer_files_fail_closed(self):
        with self.assertRaises(DecisionError):
            execute("missing", "sage", {})
        with self.assertRaises(DecisionError):
            execute("input-guardrails", "sage", [], mode="demo")
        with self.assertRaises(DecisionError):
            execute("input-guardrails", "sage", {"prompt": "ok", "policy": {"description": "p"}},
                    mode="demo")
        with self.assertRaises(DecisionError):
            execute("input-guardrails", "sage", {}, mode="live", retries=3)

    def test_deterministic_permission_decisions_precede_credentials_and_transport(self):
        denied = {"proposed_action": "delete everything", "context": "", "permissions": {"allowed": False}}
        with patch.dict(os.environ, {}, clear=True):
            result = execute("tool-call-gating", "sage", denied, mode="live",
                             transport=lambda *args: self.fail("transport called"),
                             before_attempt=lambda *args: self.fail("attempt hook called"))
        self.assertEqual(result["source"], "deterministic")
        self.assertEqual(result["result"]["action"], "reject")
        self.assertEqual(result["attempts"], 0)

    def test_known_failed_or_unknown_action_marker_fails_before_transport(self):
        for marker, results in (("[[action:refund]]", [{"action_id": "refund", "status": "failed"}]),
                                ("[[action:missing]]", [])):
            data = {"request": "Did you issue the refund?", "response": f"Refund completed {marker}",
                    "evidence": ["Ticket received"], "tool_results": results}
            with self.subTest(marker=marker), patch.dict(os.environ, {}, clear=True):
                result = execute("output-evaluation", "sage", data, mode="live",
                                 transport=lambda *args: self.fail("transport called"),
                                 before_attempt=lambda *args: self.fail("attempt hook called"))
            self.assertEqual(result["source"], "deterministic")
            self.assertEqual(result["result"]["action"], "fail")
            self.assertEqual(result["attempts"], 0)

    def test_live_request_captures_payload_and_provider_key_without_mutating_input(self):
        data = {"proposed_action": "draft a summary", "context": "source provided",
                "permissions": {"allowed": True}}
        original = dict(data)
        seen = []

        def transport(endpoint, payload, key, timeout):
            seen.append((endpoint, payload, key, timeout))
            return {"model": "resolved", "answers": {"recommendation": {
                "type": "choice", "choice": "approve",
                "probabilities": {"approve": 0.9, "reject": 0.05, "clarify": 0.05}}}}

        with patch.dict(os.environ, {"SAGE_API_KEY": "test-only"}, clear=True):
            result = execute("tool-call-gating", "sage", data, mode="live", transport=transport)
        self.assertEqual(data, original)
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["response"]["model"], "resolved")
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][2:], ("test-only", 20))
        self.assertNotIn("expected", str(seen[0][1]))

    def test_only_explicit_rate_limit_is_retried(self):
        calls = []

        def rate_limited(*args):
            calls.append(args)
            if len(calls) == 1:
                raise DecisionError("rate_limited", "429", status=429, retryable=True)
            return {"model": "resolved", "answers": {"recommendation": {
                "type": "choice", "choice": "approve",
                "probabilities": {"approve": 0.9, "reject": 0.05, "clarify": 0.05}}}}

        before, after = [], []
        with patch.dict(os.environ, {"SAGE_API_KEY": "test-only"}, clear=True), patch("decision_models.runtime.time.sleep"):
            result = execute("tool-call-gating", "sage", {
                "proposed_action": "draft", "context": "authorized", "permissions": {"allowed": True}},
                mode="live", retries=1, transport=rate_limited,
                before_attempt=lambda *args: before.append(args), after_attempt=lambda *args: after.append(args))
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(before), 2)
        self.assertEqual(len(after), 1)

    def test_ambiguous_timeout_is_never_retried(self):
        calls = []

        def timeout(*args):
            calls.append(args)
            raise DecisionError("timeout", "charge status unknown", retryable=False)

        with patch.dict(os.environ, {"SAGE_API_KEY": "test-only"}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("tool-call-gating", "sage", {
                    "proposed_action": "draft", "context": "authorized", "permissions": {"allowed": True}},
                    mode="live", retries=2, transport=timeout)
        self.assertEqual(caught.exception.code, "timeout")
        self.assertEqual(len(calls), 1)

    def test_missing_credentials_fail_before_transport(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(DecisionError) as caught:
                execute("tool-call-gating", "sage", {
                    "proposed_action": "draft", "context": "authorized", "permissions": {"allowed": True}},
                    mode="live", transport=lambda *args: self.fail("transport called"))
        self.assertEqual(caught.exception.code, "missing_credentials")


if __name__ == "__main__":
    unittest.main()
