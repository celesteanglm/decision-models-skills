"""Offline contract tests using independent OpenRouter-native examples."""

import unittest

from decision_models.contracts import DecisionError
from decision_models.providers.openrouter import Adapter


QUESTIONS = [
    {
        "name": "is_bug",
        "kind": "predicate",
        "instructions": "Is the customer describing a defect?",
        "criteria": {
            "true": "Unexpected behavior is described.",
            "false": "The customer asks a question or requests a feature.",
        },
    },
    {
        "name": "team",
        "kind": "choice",
        "instructions": "Which team should own the ticket?",
        "options": {"account": "Login and profile issues.", "payments": "Billing issues."},
    },
    {
        "name": "urgency",
        "kind": "score",
        "instructions": "How urgent is the ticket?",
        "levels": ["Can wait", "This week", "Blocking now"],
    },
]

NATIVE_RESPONSE = {
    "answers": {
        "is_bug": {"noul": 0.93, "type": "noul"},
        "team": {
            "choice": "payments",
            "confidence": 0.81,
            "probabilities": {"account": 0.12, "payments": 0.88},
            "type": "choice",
        },
        "urgency": {
            "confidence": 0.77,
            "legend": {"0": "Can wait", "1": "This week", "2": "Blocking now"},
            "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7},
            "score": 1.6,
            "type": "score",
        },
    },
    "id": "gen-dec-test-01",
    "model": "typesafe/jev-1.13-20261001",
    "provider": "TypeSafe",
    "usage": {"cost": 0.00002, "input_tokens": 80, "output_tokens": 32},
}


class OpenRouterAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = Adapter()

    def test_metadata_and_native_keyed_request(self):
        self.assertEqual(self.adapter.name, "jev-openrouter")
        self.assertEqual(self.adapter.endpoint, "https://openrouter.ai/api/alpha/decisions")
        self.assertEqual(self.adapter.key_env, "OPENROUTER_API_KEY")
        self.assertEqual(self.adapter.default_model, "typesafe/jev-1.13")

        payload = self.adapter.build_payload(
            {"ticket": "Checkout fails after clicking Pay."}, QUESTIONS, "typesafe/jev-1.13"
        )
        self.assertEqual(payload["model"], "typesafe/jev-1.13")
        self.assertEqual(payload["state"], {"ticket": "Checkout fails after clicking Pay."})
        self.assertEqual(
            payload["questions"],
            {
                "is_bug": {
                    "instructions": "Is the customer describing a defect?",
                    "type": "noul",
                    "criteria": QUESTIONS[0]["criteria"],
                },
                "team": {
                    "instructions": "Which team should own the ticket?",
                    "type": "choice",
                    "criteria": QUESTIONS[1]["options"],
                },
                "urgency": {
                    "instructions": "How urgent is the ticket?",
                    "type": "score",
                    "criteria": QUESTIONS[2]["levels"],
                },
            },
        )

    def test_parse_preserves_native_values_and_normalizes_answers(self):
        result = self.adapter.parse_response(NATIVE_RESPONSE, QUESTIONS)
        self.assertEqual(result["model"], "typesafe/jev-1.13-20261001")
        self.assertIs(result["raw_response"], NATIVE_RESPONSE)
        self.assertEqual(result["usage"], NATIVE_RESPONSE["usage"])
        self.assertEqual(result["answers"]["is_bug"]["probability_true"], 0.93)
        self.assertEqual(result["answers"]["team"]["choice"], "payments")
        self.assertEqual(result["answers"]["team"]["confidence"], 0.81)
        self.assertEqual(result["answers"]["urgency"]["score"], 1.6)
        self.assertEqual(result["answers"]["urgency"]["probabilities"], {"0": 0.1, "1": 0.2, "2": 0.7})
        self.assertEqual(result["answers"]["urgency"]["legend"], NATIVE_RESPONSE["answers"]["urgency"]["legend"])

    def test_predicate_request_without_optional_criteria(self):
        payload = self.adapter.build_payload(
            {"text": "hello"},
            [{"name": "safe", "kind": "predicate", "instructions": "Is this safe?"}],
            "model-x",
        )
        self.assertEqual(payload["questions"]["safe"], {
            "instructions": "Is this safe?", "type": "noul"
        })

    def test_explicit_refusal_is_preserved(self):
        raw = {
            "model": "typesafe/jev-1.13",
            "answers": {
                "is_bug": {"type": "refusal", "refusal": "Cannot classify."},
                "team": NATIVE_RESPONSE["answers"]["team"],
                "urgency": NATIVE_RESPONSE["answers"]["urgency"],
            },
        }
        response = self.adapter.parse_response(raw, QUESTIONS)
        self.assertEqual(response["answers"]["is_bug"], {"kind": "predicate", "status": "refusal"})

    def test_wrong_answer_names_and_missing_fields_are_rejected(self):
        wrong_names = dict(NATIVE_RESPONSE, answers={"unexpected": {}})
        with self.assertRaises(DecisionError):
            self.adapter.parse_response(wrong_names, QUESTIONS)

        missing_predicate = {
            "model": "typesafe/jev-1.13",
            "answers": {
                "is_bug": {"type": "noul"},
                "team": NATIVE_RESPONSE["answers"]["team"],
                "urgency": NATIVE_RESPONSE["answers"]["urgency"],
            },
        }
        with self.assertRaises(DecisionError):
            self.adapter.parse_response(missing_predicate, QUESTIONS)

    def test_invalid_choice_score_and_confidence_are_rejected(self):
        for field, value in (("choice", "security"), ("confidence", 1.1)):
            with self.subTest(field=field):
                raw = {**NATIVE_RESPONSE, "answers": {**NATIVE_RESPONSE["answers"],
                    "team": {**NATIVE_RESPONSE["answers"]["team"], field: value}}}
                with self.assertRaises(DecisionError):
                    self.adapter.parse_response(raw, QUESTIONS)

        raw = {**NATIVE_RESPONSE, "answers": {**NATIVE_RESPONSE["answers"],
            "urgency": {**NATIVE_RESPONSE["answers"]["urgency"], "score": 1.4}}}
        with self.assertRaises(DecisionError):
            self.adapter.parse_response(raw, QUESTIONS)

    def test_bad_request_inputs_are_rejected(self):
        with self.assertRaises(DecisionError):
            self.adapter.build_payload([], QUESTIONS, "model-x")
        with self.assertRaises(DecisionError):
            self.adapter.build_payload({}, QUESTIONS, " ")
        malformed = [{"name": "safe", "kind": "predicate", "instructions": "Is this safe?",
                      "criteria": {"true": "Safe."}}]
        with self.assertRaises(DecisionError):
            self.adapter.build_payload({}, malformed, "model-x")


if __name__ == "__main__":
    unittest.main()
