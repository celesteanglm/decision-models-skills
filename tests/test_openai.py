import unittest

from decision_models.contracts import DecisionError
from decision_models.providers.openai import Adapter


class OpenAIAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = Adapter()
        self.questions = [
            {
                "name": "safe",
                "kind": "predicate",
                "instructions": "Does the request comply?",
                "criteria": {"true": "No disallowed content", "false": "Contains disallowed content"},
            },
            {
                "name": "route",
                "kind": "choice",
                "instructions": "Choose a team.",
                "options": {"billing": "Payment questions", "support": "Product help"},
            },
            {
                "name": "severity",
                "kind": "score",
                "instructions": "Rate impact.",
                "levels": ["Minor issue", "Major issue"],
            },
        ]

    def test_build_payload_maps_all_question_types_and_stabilizes_state(self):
        payload = self.adapter.build_payload(
            {"z": 2, "a": {"second": True, "first": "x"}}, self.questions, "gpt-6-luna"
        )
        self.assertEqual(payload["model"], "gpt-6-luna")
        self.assertEqual(payload["input"], '{"a":{"first":"x","second":true},"z":2}')
        self.assertEqual(
            [question["type"] for question in payload["questions"]],
            ["predicate", "choice", "score"],
        )
        self.assertEqual(payload["questions"][0]["name"], "safe")
        self.assertIn("True means: No disallowed content", payload["questions"][0]["instructions"])
        self.assertEqual(
            payload["questions"][1]["choices"],
            [
                {"value": "billing", "description": "Payment questions"},
                {"value": "support", "description": "Product help"},
            ],
        )
        self.assertEqual(
            payload["questions"][2]["levels"],
            [
                {"label": "Minor issue", "description": "Minor issue"},
                {"label": "Major issue", "description": "Major issue"},
            ],
        )

    def test_build_payload_preserves_text_input(self):
        payload = self.adapter.build_payload("plain evidence", self.questions, "gpt-6-luna")
        self.assertEqual(payload["input"], "plain evidence")

    def test_parse_response_maps_predicate_choice_fractional_score_and_usage(self):
        raw = {
            "model": "gpt-6-luna-2026-09-15",
            "answers": [
                {"type": "predicate", "name": "safe", "probability": 0.91},
                {
                    "type": "choice",
                    "name": "route",
                    "choice": "billing",
                    "probabilities": [
                        {"value": "billing", "probability": 0.8},
                        {"value": "support", "probability": 0.2},
                    ],
                    "confidence": 0.77,
                },
                {
                    "type": "score",
                    "name": "severity",
                    "score": 0.25,
                    "probabilities": [
                        {"value": 0, "label": "Minor issue", "probability": 0.75},
                        {"value": 1, "label": "Major issue", "probability": 0.25},
                    ],
                    "confidence": 0.6,
                },
            ],
            "usage": {"input_tokens": 27, "output_tokens": 8},
        }
        result = self.adapter.parse_response(raw, self.questions)
        self.assertEqual(result["model"], "gpt-6-luna-2026-09-15")
        self.assertEqual(result["answers"]["safe"]["probability_true"], 0.91)
        self.assertEqual(result["answers"]["route"]["probabilities"], {"billing": 0.8, "support": 0.2})
        self.assertEqual(result["answers"]["route"]["confidence"], 0.77)
        self.assertEqual(result["answers"]["severity"]["score"], 0.25)
        self.assertEqual(result["answers"]["severity"]["probabilities"], {"0": 0.75, "1": 0.25})
        self.assertEqual(result["answers"]["severity"]["legend"], ["Minor issue", "Major issue"])
        self.assertEqual(result["usage"], raw["usage"])
        self.assertIs(result["raw_response"], raw)

    def test_parse_response_maps_explicit_refusal_to_original_question_kind(self):
        raw = {
            "model": "gpt-6-luna",
            "answers": [
                {"type": "refusal", "name": "safe"},
                {
                    "type": "choice",
                    "name": "route",
                    "choice": "billing",
                    "probabilities": [
                        {"value": "billing", "probability": 1.0},
                        {"value": "support", "probability": 0.0},
                    ],
                },
                {"type": "refusal", "name": "severity"},
            ],
        }
        result = self.adapter.parse_response(raw, self.questions)
        self.assertEqual(result["answers"]["safe"], {"kind": "predicate", "status": "refusal"})
        self.assertEqual(result["answers"]["severity"], {"kind": "score", "status": "refusal"})

    def test_rejects_name_mismatch_and_reordered_answers(self):
        for names in (
            ["different", "route", "severity"],
            ["route", "safe", "severity"],
        ):
            raw = {
                "model": "gpt-6-luna",
                "answers": [
                    {"type": "refusal", "name": names[0]},
                    {"type": "refusal", "name": names[1]},
                    {"type": "refusal", "name": names[2]},
                ],
            }
            with self.subTest(names=names), self.assertRaises(DecisionError):
                self.adapter.parse_response(raw, self.questions)

    def test_rejects_missing_answer_wrong_probability_and_wrong_score_label(self):
        invalid_payloads = [
            {"model": "gpt-6-luna", "answers": []},
            {
                "model": "gpt-6-luna",
                "answers": [
                    {"type": "predicate", "name": "safe", "probability": 2.0},
                    {"type": "refusal", "name": "route"},
                    {"type": "refusal", "name": "severity"},
                ],
            },
            {
                "model": "gpt-6-luna",
                "answers": [
                    {"type": "refusal", "name": "safe"},
                    {"type": "refusal", "name": "route"},
                    {
                        "type": "score", "name": "severity", "score": 0,
                        "probabilities": [
                            {"value": 0, "label": "wrong", "probability": 1.0},
                            {"value": 1, "label": "Major issue", "probability": 0.0},
                        ],
                    },
                ],
            },
        ]
        for raw in invalid_payloads:
            with self.subTest(raw=raw), self.assertRaises(DecisionError):
                self.adapter.parse_response(raw, self.questions)


if __name__ == "__main__":
    unittest.main()
