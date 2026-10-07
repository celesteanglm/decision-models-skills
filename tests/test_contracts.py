import math
import unittest

from decision_models.contracts import DecisionError, validate_questions, validate_response


QUESTIONS = [
    {"name": "ok", "kind": "predicate", "instructions": "Is it true?"},
    {"name": "pick", "kind": "choice", "instructions": "Choose one.",
     "options": {"a": "First", "b": "Second"}},
    {"name": "rating", "kind": "score", "instructions": "Rate it.",
     "levels": ["Low", "Middle", "High"]},
]


def valid_response():
    return {
        "model": "resolved-model",
        "answers": {
            "ok": {"kind": "predicate", "status": "answered", "probability_true": 0.75},
            "pick": {"kind": "choice", "status": "answered", "choice": "a",
                     "probabilities": {"a": 0.75, "b": 0.25}},
            "rating": {"kind": "score", "status": "answered", "score": 1,
                       "probabilities": {"0": 0.25, "1": 0.5, "2": 0.25}},
        }, "usage": None, "raw_response": None,
    }


class ContractTests(unittest.TestCase):
    def test_valid_typed_response_round_trips(self):
        response = valid_response()
        self.assertIs(validate_response(response, QUESTIONS), response)

    def test_refusal_keeps_question_kind_without_fabricating_values(self):
        response = valid_response()
        response["answers"]["ok"] = {"kind": "predicate", "status": "refusal"}
        self.assertIs(validate_response(response, QUESTIONS), response)
        for invalid in ({"kind": "choice", "status": "refusal"},
                        {"kind": "predicate"},
                        {"kind": "predicate", "status": "unknown"}):
            response = valid_response()
            response["answers"]["ok"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(DecisionError):
                validate_response(response, QUESTIONS)

    def test_question_shape_and_unique_names_are_enforced(self):
        invalid_sets = [[], [{"name": "x", "kind": "other", "instructions": "x"}],
                        [QUESTIONS[0], dict(QUESTIONS[0])],
                        [{"name": "x", "kind": "choice", "instructions": "x", "options": {"a": ""}}],
                        [{"name": "x", "kind": "score", "instructions": "x", "levels": ["only"]}],
                        [{"name": "x", "kind": "score", "instructions": "x", "levels": ["same", "same"]}],
                        [{"name": "x", "kind": "predicate", "instructions": "x",
                          "criteria": {"true": "yes"}}],
                        [{"name": "x", "kind": "predicate", "instructions": "x",
                          "criteria": {"true": "yes", "false": " "}}]]
        for questions in invalid_sets:
            with self.subTest(questions=questions), self.assertRaises(DecisionError):
                validate_questions(questions)

    def test_answer_names_kind_and_answer_object_are_exact(self):
        mutations = [
            lambda r: r["answers"].pop("pick"),
            lambda r: r["answers"].update(extra={"kind": "predicate", "status": "refusal"}),
            lambda r: r["answers"].update(pick=None),
            lambda r: r["answers"]["pick"].update(kind="score"),
            lambda r: r.update(model=""),
        ]
        for mutate in mutations:
            response = valid_response()
            mutate(response)
            with self.subTest(response=response), self.assertRaises(DecisionError):
                validate_response(response, QUESTIONS)

    def test_probabilities_reject_nonfinite_bool_out_of_range_and_bad_mass(self):
        bad_values = [float("nan"), float("inf"), True, -0.01, 1.01]
        for value in bad_values:
            response = valid_response()
            response["answers"]["ok"]["probability_true"] = value
            with self.subTest(value=value), self.assertRaises(DecisionError):
                validate_response(response, QUESTIONS)
        for distribution in ({"a": 0.4, "b": 0.4}, {"a": 0.7, "unknown": 0.3},
                             {"a": float("nan"), "b": 0}, {"a": True, "b": 0}):
            response = valid_response()
            response["answers"]["pick"]["probabilities"] = distribution
            with self.subTest(distribution=distribution), self.assertRaises(DecisionError):
                validate_response(response, QUESTIONS)

    def test_choice_score_confidence_and_weighted_score_are_checked(self):
        mutations = [
            lambda a: a.update(choice="unoffered"),
            lambda a: a.update(confidence=math.inf),
            lambda a: a.update(confidence=True),
        ]
        for mutate in mutations:
            response = valid_response()
            mutate(response["answers"]["pick"])
            with self.subTest(response=response), self.assertRaises(DecisionError):
                validate_response(response, QUESTIONS)
        response = valid_response()
        response["answers"]["rating"]["score"] = 2
        with self.assertRaises(DecisionError):
            validate_response(response, QUESTIONS)
        response = valid_response()
        response["answers"]["rating"]["score"] = True
        with self.assertRaises(DecisionError):
            validate_response(response, QUESTIONS)


if __name__ == "__main__":
    unittest.main()
