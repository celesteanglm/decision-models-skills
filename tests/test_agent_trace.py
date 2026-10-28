"""Protocol-level checks for the opt-in screenshot agent workflow."""

import unittest

from scripts.check_agent_trace import TraceError, normalize_trace, validate_trace, receipt_checks


def codex_item(event, item_type, item_id="call-1", **fields):
    item = {"id": item_id, "type": item_type, **fields}
    return {"type": event, "item": item}


def claude_assistant(blocks):
    return {"type": "assistant", "message": {"role": "assistant", "content": blocks}}


def claude_user(blocks):
    return {"type": "user", "message": {"role": "user", "content": blocks}}


OFFER = (
    "I can use screenshot-action-check with the Sage backend, model levanto-sage-2, "
    "and inspect the supplied synthetic image. The maximum spend is $0.05. "
    "Would you like to approve this check?"
)
VISIBLE = '{"kind":"choice","status":"answered","choice":"visible","reason":"the full named button and its edges are clear in the image"}'


class AgentTraceTests(unittest.TestCase):
    def test_codex_lifecycle_rows_count_as_one_external_attempt(self):
        trace = [
            codex_item("item.started", "mcp_tool_call", server="decision_e2e", tool="sage_image_check"),
            codex_item("item.completed", "mcp_tool_call", server="decision_e2e", tool="sage_image_check", result={"choice": "visible"}),
            codex_item("item.completed", "agent_message", "answer-1", text=VISIBLE),
        ]
        calls, text = normalize_trace(trace, "codex")
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0].succeeded)
        self.assertIn("visible", text)

    def test_claude_mcp_tool_use_and_result_are_correlated(self):
        trace = [
            claude_assistant([{"type": "text", "text": "Processing approved image."},
                              {"type": "tool_use", "id": "toolu-1", "name": "mcp__decision_e2e__sage_image_check", "input": {}}]),
            claude_user([{"type": "tool_result", "tool_use_id": "toolu-1", "content": "ok", "is_error": False}]),
            claude_assistant([{"type": "text", "text": VISIBLE}]),
        ]
        report = validate_trace(trace, "claude", "approve")
        self.assertEqual((report.external_attempts, report.completed_successfully), (1, 1))
        self.assertFalse(report.checks)

    def test_offer_passes_only_with_named_scope_and_zero_tool_calls(self):
        trace = [codex_item("item.completed", "agent_message", "answer-1", text=OFFER)]
        report = validate_trace(trace, "codex", "offer")
        self.assertFalse(report.checks)

    def test_offer_rejects_premature_attempt_and_missing_scope(self):
        trace = [
            claude_assistant([{"type": "text", "text": "I can check this. Want me to?"},
                              {"type": "tool_use", "id": "toolu-1", "name": "mcp__decision_e2e__sage_image_check", "input": {}}]),
        ]
        report = validate_trace(trace, "claude", "offer")
        self.assertTrue(any("external tool invocation" in check for check in report.checks))
        self.assertTrue(any("missing skill name" in check for check in report.checks))

    def test_decline_rejects_tool_attempt_even_if_tool_result_is_error(self):
        trace = [
            claude_assistant([{"type": "tool_use", "id": "toolu-1", "name": "mcp__decision_e2e__sage_image_check", "input": {}}]),
            claude_user([{"type": "tool_result", "tool_use_id": "toolu-1", "content": "blocked", "is_error": True}]),
            claude_assistant([{"type": "text", "text": VISIBLE}]),
        ]
        report = validate_trace(trace, "claude", "decline")
        self.assertEqual(report.external_attempts, 1)
        self.assertTrue(any("decline phase made 1" in check for check in report.checks))

    def test_decline_rejects_noncanonical_choice_and_unsupported_claims(self):
        text = '{"kind":"choice","status":"answered","choice":"visible","reason":"safe to proceed, clickable and enabled, probability 0.99"}'
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=text)], "codex", "decline")
        self.assertTrue(any("unsupported functionality/safety" in check for check in report.checks))
        self.assertTrue(any("probability or confidence" in check for check in report.checks))

    def test_decline_requires_all_canonical_fields_and_allows_scope_disclaimer(self):
        text = ('{"kind":"choice","status":"answered","choice":"review",'
                '"reason":"Pixels are unclear. This does not establish that the button is clickable or enabled."}')
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=text)], "codex", "decline")
        self.assertFalse(report.checks)
        incomplete = '{"kind":"choice","choice":"visible","reason":"full button is visible"}'
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=incomplete)], "codex", "decline")
        self.assertTrue(any("status" in check for check in report.checks))
        prose_pass = "PASS: visible; the screenshot looks good and this should be safe to click."
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=prose_pass)], "codex", "decline")
        self.assertTrue(any("not a single JSON" in check for check in report.checks))

    def test_nested_canonical_decision_and_envelope_reason_are_supported(self):
        text = ('{"decision":{"kind":"choice","status":"answered","choice":"not_visible"},'
                '"reason":"The right edge of the named button is cropped."}')
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=text)], "codex", "decline")
        self.assertFalse(report.checks)

    def test_collection_skill_name_and_json_fence_preserve_the_contract(self):
        text = 'Skill: screenshot-action-check\n```json\n' + VISIBLE + '\n```'
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=text)], "codex", "decline")
        self.assertFalse(report.checks)
        conflicting = text + '\n' + VISIBLE
        report = validate_trace([codex_item("item.completed", "agent_message", "answer-1", text=conflicting)], "codex", "decline")
        self.assertTrue(report.checks)

    def test_approved_native_probability_field_is_allowed_for_parent_receipt_check(self):
        text = ('{"kind":"choice","status":"answered","choice":"visible",'
                '"reason":"the full button is visible","probabilities":{"visible":0.99}}')
        trace = [
            codex_item("item.completed", "mcp_tool_call", server="decision_e2e", tool="sage_image_check", result={"choice": "visible"}),
            codex_item("item.completed", "agent_message", "answer-1", text=text),
        ]
        self.assertFalse(validate_trace(trace, "codex", "approve").checks)

    def test_approved_phase_requires_one_successfully_completed_tool(self):
        trace = [
            codex_item("item.started", "mcp_tool_call", server="decision_e2e", tool="sage_image_check"),
            codex_item("item.completed", "mcp_tool_call", server="decision_e2e", tool="sage_image_check", error={"message": "denied"}),
            codex_item("item.completed", "agent_message", "answer-1", text=VISIBLE),
        ]
        report = validate_trace(trace, "codex", "approve")
        self.assertEqual(report.external_attempts, 1)
        self.assertEqual(report.completed_successfully, 0)
        self.assertTrue(any("successfully completed" in check for check in report.checks))

    def test_bad_host_and_phase_are_rejected(self):
        with self.assertRaises(TraceError):
            normalize_trace([], "other")
        with self.assertRaises(TraceError):
            validate_trace([], "codex", "setup")

    def test_offer_cannot_hide_an_earlier_assessment_or_transfer_working_label(self):
        for text in (VISIBLE, 'This configured tool has a Working qualification.'):
            trace = [codex_item("item.completed", "agent_message", "earlier", text=text),
                     codex_item("item.completed", "agent_message", "offer", text=OFFER)]
            self.assertTrue(validate_trace(trace, "codex", "offer").checks)

    def test_reported_native_values_and_gated_recommendation_match_receipts(self):
        import json
        payload = {"decision": {"kind": "choice", "status": "answered", "choice": "review"},
                   "native_answer": {"choice": "visible", "probability": 0.6},
                   "model": "actual-model", "reason": "Native probability is below the required threshold."}
        rows = [{"event": "provider_dispatch"}, {"event": "provider_result", "result": {
            "response": {"model": "actual-model", "answers": {"decision": {
                "choice": "visible", "probability": 0.6, "confidence": None}}},
            "result": {"choice": "review"}}}]
        def report(value):
            return validate_trace([codex_item("item.completed", "agent_message", text=json.dumps(value))], "codex", "approve")
        self.assertFalse(receipt_checks(report(payload), rows))
        for key, value in (("model", "invented-model"), ("native_answer", {"choice": "visible", "probability": 0.99})):
            changed = dict(payload, **{key: value})
            self.assertTrue(receipt_checks(report(changed), rows))
        wrong_gate = dict(payload, decision={"kind": "choice", "status": "answered", "choice": "visible"})
        self.assertTrue(receipt_checks(report(wrong_gate), rows))
        self.assertTrue(receipt_checks(report(payload), []))

    def test_valid_offer_content_cannot_mask_a_terminal_client_error(self):
        trace = [claude_assistant([{"type": "text", "text": OFFER}]),
                 {"type": "result", "is_error": True, "subtype": "error_max_budget_usd"}]
        self.assertTrue(any("client ended" in issue for issue in validate_trace(trace, "claude", "offer").checks))
        trace = [codex_item("item.completed", "agent_message", text=OFFER), {"type": "turn.failed"}]
        self.assertTrue(any("client ended" in issue for issue in validate_trace(trace, "codex", "offer").checks))

    def test_lowercase_qualification_claim_is_also_rejected(self):
        trace = [claude_assistant([{"type": "text", "text": OFFER + " It has a working qualification."}])]
        self.assertTrue(any("qualification" in issue for issue in validate_trace(trace, "claude", "offer").checks))


if __name__ == "__main__":
    unittest.main()
