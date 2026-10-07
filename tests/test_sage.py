import unittest

from decision_models.contracts import DecisionError
from decision_models.providers.sage import Adapter


class SageAdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter = Adapter()
        self.questions = [
            {"name": "is_safe", "kind": "predicate", "instructions": "Is this safe?",
             "criteria": {"true": "No risk", "false": "Any risk"}},
            {"name": "route", "kind": "choice", "instructions": "Choose a team.",
             "options": {"billing": "Payments", "support": "Product help"}},
            {"name": "quality", "kind": "score", "instructions": "Rate quality.",
             "levels": ["Poor", "Fair", "Good"]},
        ]

    def test_builds_named_native_questions_and_defaults(self):
        payload = self.adapter.build_payload({"text": "example"}, self.questions)
        self.assertEqual(payload["model"], "levanto-sage-v1.3")
        self.assertEqual(payload["reasoning"], "off")
        self.assertEqual(payload["state"], {"text": "example"})
        self.assertEqual(payload["questions"]["is_safe"], {
            "type": "noul", "instructions": "Is this safe?",
            "criteria": {"true": "No risk", "false": "Any risk"},
        })
        self.assertEqual(payload["questions"]["route"], {
            "type": "choice", "instructions": "Choose a team.",
            "criteria": {"billing": "Payments", "support": "Product help"},
        })
        self.assertEqual(payload["questions"]["quality"], {
            "type": "score", "instructions": "Rate quality.",
            "criteria": ["Poor", "Fair", "Good"],
        })

    def test_build_allows_predicate_without_criteria_and_custom_model(self):
        question = [{"name": "flag", "kind": "predicate", "instructions": "Is it present?"}]
        payload = self.adapter.build_payload("state", question, "custom-sage")
        self.assertEqual(payload["model"], "custom-sage")
        self.assertEqual(payload["questions"]["flag"], {
            "type": "noul", "instructions": "Is it present?",
        })
        invalid = [{"name": "flag", "kind": "predicate", "instructions": "Check.",
                    "criteria": {"true": "yes", "false": " "}}]
        with self.assertRaisesRegex(DecisionError, "predicate criteria"):
            self.adapter.build_payload("state", invalid)

    def test_maps_native_answers_and_preserves_confidence_and_usage(self):
        raw = {
            "model": "levanto-sage-v1.3+build7",
            "answers": {
                "is_safe": {"type": "noul", "noul": 0.75},
                "route": {"type": "choice", "choice": "billing",
                          "probabilities": {"billing": 0.7, "support": 0.3},
                          "confidence": 0.61},
                "quality": {"type": "score", "score": 1.5,
                            "probabilities": {"0": 0.25, "1": 0, "2": 0.75},
                            "confidence": 0.75, "legend": {"0": "Poor", "1": "Fair", "2": "Good"}},
            },
            "usage": {"input_tokens": 12, "output_tokens": 0},
        }
        result = self.adapter.parse_response(raw, self.questions)
        self.assertEqual(result["model"], "levanto-sage-v1.3+build7")
        self.assertEqual(result["answers"]["is_safe"]["probability_true"], 0.75)
        self.assertEqual(result["answers"]["route"]["confidence"], 0.61)
        self.assertEqual(result["answers"]["quality"]["confidence"], 0.75)
        self.assertEqual(result["answers"]["quality"]["score"], 1.5)
        self.assertEqual(result["usage"], raw["usage"])
        self.assertIs(result["raw_response"], raw)

    def test_maps_explicit_refusal_without_fabricating_answer(self):
        questions = [{"name": "flag", "kind": "predicate", "instructions": "Is it true?"}]
        result = self.adapter.parse_response({
            "model": "sage-resolved",
            "answers": {"flag": {"type": "refusal", "message": "cannot determine"}},
        }, questions)
        self.assertEqual(result["answers"]["flag"], {"kind": "predicate", "status": "refusal"})

    def test_refusal_false_is_not_a_refusal(self):
        questions = [{"name": "flag", "kind": "predicate", "instructions": "Is it true?"}]
        result = self.adapter.parse_response({
            "model": "sage-resolved",
            "answers": {"flag": {"type": "noul", "noul": 0.8, "refusal": False}},
        }, questions)
        self.assertEqual(result["answers"]["flag"]["probability_true"], 0.8)

    def test_rejects_unrequested_answer_names(self):
        questions = [{"name": "flag", "kind": "predicate", "instructions": "Is it true?"}]
        with self.assertRaisesRegex(DecisionError, "answer names do not match"):
            self.adapter.parse_response({
                "model": "sage-resolved",
                "answers": {
                    "flag": {"type": "noul", "noul": 0.8},
                    "unexpected": {"type": "noul", "noul": 0.2},
                },
            }, questions)

    def test_rejects_missing_model_and_incomplete_answers(self):
        with self.assertRaisesRegex(DecisionError, "resolved model"):
            self.adapter.parse_response({"resolved_model": "sage", "answers": {}}, self.questions)
        with self.assertRaisesRegex(DecisionError, "missing answers"):
            self.adapter.parse_response({"model": "sage"}, self.questions)

    def test_rejects_null_answers_and_invalid_probability_values(self):
        raw = {"model": "sage", "answers": {
            "is_safe": {"type": "noul", "noul": None},
            "route": {"type": "choice", "choice": "billing",
                      "probabilities": {"billing": 0.7, "support": 0.3}},
            "quality": {"type": "score", "score": 1,
                        "probabilities": {"0": 0, "1": 1, "2": 0}},
        }}
        with self.assertRaises(DecisionError):
            self.adapter.parse_response(raw, self.questions)
        raw["answers"]["is_safe"]["noul"] = 0.5
        raw["answers"]["route"]["probabilities"]["support"] = 1.2
        with self.assertRaises(DecisionError):
            self.adapter.parse_response(raw, self.questions)

    def test_sage_option_limits_are_enforced(self):
        too_many_options = [{"name": "pick", "kind": "choice", "instructions": "Pick.",
                             "options": {f"o{i}": f"Option {i}" for i in range(121)}}]
        with self.assertRaisesRegex(DecisionError, "120 options"):
            self.adapter.build_payload("state", too_many_options)
        too_many_levels = [{"name": "rate", "kind": "score", "instructions": "Rate.",
                            "levels": [f"L{i}" for i in range(27)]}]
        with self.assertRaisesRegex(DecisionError, "26 levels"):
            self.adapter.build_payload("state", too_many_levels)


if __name__ == "__main__":
    unittest.main()
