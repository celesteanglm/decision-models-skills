"""Adapter for OpenRouter's alpha.decisions API."""

from __future__ import annotations

from typing import Any

from decision_models.contracts import DecisionError, fail, validate_questions, validate_response


class Adapter:
    """Map the shared decision contract to OpenRouter's native keyed format."""

    name = "jev-openrouter"
    endpoint = "https://openrouter.ai/api/alpha/decisions"
    key_env = "OPENROUTER_API_KEY"
    default_model = "typesafe/jev-1.13"

    def build_payload(self, state: dict[str, Any], questions: list[dict[str, Any]], model: str) -> dict[str, Any]:
        validate_questions(questions)
        if not isinstance(state, dict):
            raise DecisionError("invalid_request", "state must be an object")
        if not isinstance(model, str) or not model.strip():
            raise DecisionError("invalid_request", "model must be a nonempty string")

        native_questions: dict[str, dict[str, Any]] = {}
        for question in questions:
            kind = question["kind"]
            native: dict[str, Any] = {
                "instructions": question["instructions"],
                "type": {"predicate": "noul", "choice": "choice", "score": "score"}[kind],
            }
            if kind == "predicate":
                if "criteria" in question:
                    criteria = question["criteria"]
                    if (
                        not isinstance(criteria, dict)
                        or set(criteria) != {"true", "false"}
                        or any(not isinstance(value, str) or not value.strip() for value in criteria.values())
                    ):
                        raise DecisionError(
                            "invalid_request", "predicate criteria must describe true and false"
                        )
                    native["criteria"] = dict(criteria)
            elif kind == "choice":
                native["criteria"] = dict(question["options"])
            else:
                native["criteria"] = list(question["levels"])
            native_questions[question["name"]] = native

        return {"model": model, "questions": native_questions, "state": state}

    def parse_response(self, raw: dict[str, Any], questions: list[dict[str, Any]]) -> dict[str, Any]:
        validate_questions(questions)
        if not isinstance(raw, dict):
            fail("response must be an object")
        model = raw.get("model")
        native_answers = raw.get("answers")
        if not isinstance(model, str) or not model.strip():
            fail("missing resolved model")
        if not isinstance(native_answers, dict):
            fail("missing answers object")
        if set(native_answers) != {question["name"] for question in questions}:
            fail("answer names do not match questions")

        canonical_answers: dict[str, dict[str, Any]] = {}
        for question in questions:
            name, kind = question["name"], question["kind"]
            native = native_answers[name]
            if not isinstance(native, dict):
                fail("answer must be an object")

            if _is_refusal(native):
                canonical_answers[name] = {"kind": kind, "status": "refusal"}
                continue

            native_type = {"predicate": "noul", "choice": "choice", "score": "score"}[kind]
            if native.get("type") != native_type:
                fail("answer type does not match question")

            answer: dict[str, Any] = {"kind": kind, "status": "answered"}
            if kind == "predicate":
                if "noul" not in native:
                    fail("missing predicate noul probability")
                answer["probability_true"] = native["noul"]
            else:
                probabilities = native.get("probabilities")
                if not isinstance(probabilities, dict):
                    fail("missing probabilities object")
                answer["probabilities"] = dict(probabilities)
                if "confidence" in native:
                    answer["confidence"] = native["confidence"]
                if kind == "choice":
                    if "choice" not in native:
                        fail("missing selected choice")
                    answer["choice"] = native["choice"]
                else:
                    if "score" not in native:
                        fail("missing score")
                    answer["score"] = native["score"]
                    if "legend" in native:
                        answer["legend"] = native["legend"]
            canonical_answers[name] = answer

        response = {
            "model": model,
            "answers": canonical_answers,
            "usage": raw.get("usage"),
            "raw_response": raw,
        }
        return validate_response(response, questions)


def _is_refusal(native: dict[str, Any]) -> bool:
    """Recognize explicit refusal markers without guessing from answer content."""
    return (
        native.get("status") == "refusal"
        or native.get("type") == "refusal"
        or native.get("refusal") is True
        or isinstance(native.get("refusal"), str)
    )
