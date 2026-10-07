"""Adapter for Levanto Sage's SystemOne decisions endpoint.

The adapter performs only deterministic wire conversion. HTTP, credentials,
timeouts, and retries belong to the shared runtime.
"""

from decision_models.contracts import DecisionError, validate_questions, validate_response


class Adapter:
    name = "sage"
    endpoint = "https://sage.levanto.ai/v1/systemone"
    key_env = "SAGE_API_KEY"
    default_model = "levanto-sage-v1.3"

    def build_payload(self, state, questions, model=None):
        """Map provider-neutral questions to Sage's named SystemOne question map."""
        validate_questions(questions)
        native = {}
        for question in questions:
            kind = question["kind"]
            item = {"type": {"predicate": "noul", "choice": "choice", "score": "score"}[kind],
                    "instructions": question["instructions"]}
            if kind == "choice":
                if len(question["options"]) > 120:
                    raise DecisionError("invalid_request", "Sage choice supports at most 120 options")
                item["criteria"] = dict(question["options"])
            elif kind == "score":
                if len(question["levels"]) > 26:
                    raise DecisionError("invalid_request", "Sage score supports at most 26 levels")
                item["criteria"] = list(question["levels"])
            elif question.get("criteria") is not None:
                criteria = question["criteria"]
                if (not isinstance(criteria, dict) or set(criteria) != {"true", "false"}
                        or any(not isinstance(value, str) or not value.strip()
                               for value in criteria.values())):
                    raise DecisionError("invalid_request", "predicate criteria must describe true and false")
                item["criteria"] = dict(criteria)
            native[question["name"]] = item

        return {
            "model": model or self.default_model,
            "state": state,
            "questions": native,
            "reasoning": "off",
        }

    def parse_response(self, raw, questions):
        """Convert native named answers while retaining provider confidence verbatim."""
        validate_questions(questions)
        if not isinstance(raw, dict):
            raise DecisionError("invalid_response", "Sage response must be an object")
        model = raw.get("model")
        if not isinstance(model, str) or not model:
            raise DecisionError("invalid_response", "Sage response is missing its resolved model")
        native_answers = raw.get("answers")
        if not isinstance(native_answers, dict):
            raise DecisionError("invalid_response", "Sage response is missing answers")
        expected_names = {question["name"] for question in questions}
        if set(native_answers) != expected_names:
            raise DecisionError("invalid_response", "answer names do not match questions")

        answers = {}
        for question in questions:
            name, kind = question["name"], question["kind"]
            answer = native_answers.get(name)
            if not isinstance(answer, dict):
                raise DecisionError("invalid_response", f"Sage answer {name!r} must be an object")
            if answer.get("status") == "refusal" or answer.get("type") == "refusal":
                answers[name] = {"kind": kind, "status": "refusal"}
                continue

            native_kind = answer.get("type", answer.get("kind"))
            if native_kind not in ({"noul", "predicate"} if kind == "predicate" else {kind}):
                raise DecisionError("invalid_response", f"Sage answer {name!r} has the wrong type")
            canonical = {"kind": kind, "status": "answered"}
            if kind == "predicate":
                value = answer.get("noul", answer.get("probability_true"))
                if value is None:
                    raise DecisionError("invalid_response", f"Sage predicate {name!r} is missing noul")
                canonical["probability_true"] = value
            elif kind == "choice":
                choice = answer.get("choice")
                probabilities = answer.get("probabilities")
                if choice is None or probabilities is None:
                    raise DecisionError("invalid_response", f"Sage choice {name!r} is incomplete")
                canonical.update(choice=choice, probabilities=probabilities)
                if "confidence" in answer:
                    canonical["confidence"] = answer["confidence"]
            else:
                score = answer.get("score")
                probabilities = answer.get("probabilities")
                if score is None or probabilities is None:
                    raise DecisionError("invalid_response", f"Sage score {name!r} is incomplete")
                canonical.update(score=score, probabilities=probabilities)
                if "confidence" in answer:
                    canonical["confidence"] = answer["confidence"]
                if "legend" in answer:
                    canonical["legend"] = answer["legend"]
            answers[name] = canonical

        response = {
            "model": model,
            "answers": answers,
            "usage": raw.get("usage"),
            "raw_response": raw,
        }
        return validate_response(response, questions)
