"""Adapter for OpenAI's Decisions API.

Native request and response shapes follow the public Decisions API reference:
https://developers.openai.com/api/docs/guides/decisions
https://developers.openai.com/api/reference/resources/decisions/methods/create
"""

import json

from decision_models.contracts import DecisionError, fail, validate_questions, validate_response


class Adapter:
    name = "openai-decisions"
    endpoint = "https://api.openai.com/v1/decisions"
    key_env = "OPENAI_API_KEY"
    default_model = "gpt-6-luna"

    def build_payload(self, state, questions, model):
        validate_questions(questions)
        if not isinstance(model, str) or not model.strip():
            raise DecisionError("invalid_request", "model must be a nonempty string")

        # A state object is sent as stable JSON text because Decisions accepts
        # textual shared evidence. Preserve an already-written text input.
        if isinstance(state, str):
            input_text = state
        else:
            try:
                input_text = json.dumps(
                    state, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                    allow_nan=False,
                )
            except (TypeError, ValueError) as exc:
                raise DecisionError("invalid_request", "state must be JSON serializable") from exc

        native_questions = []
        for question in questions:
            kind = question["kind"]
            instructions = question["instructions"]
            if kind == "predicate" and isinstance(question.get("criteria"), dict):
                criteria = question["criteria"]
                additions = []
                for value in ("true", "false"):
                    description = criteria.get(value)
                    if isinstance(description, str) and description.strip():
                        additions.append(f"{value.capitalize()} means: {description}")
                if additions:
                    instructions += "\n" + "\n".join(additions)

            native = {
                "type": kind,
                "name": question["name"],
                "instructions": instructions,
            }
            if kind == "choice":
                native["choices"] = [
                    {"value": value, "description": description}
                    for value, description in question["options"].items()
                ]
            elif kind == "score":
                native["levels"] = [
                    {"label": description, "description": description}
                    for description in question["levels"]
                ]
            native_questions.append(native)

        return {"model": model, "input": input_text, "questions": native_questions}

    def parse_response(self, raw, questions):
        validate_questions(questions)
        if not isinstance(raw, dict):
            fail("response must be an object")
        model = raw.get("model")
        if not isinstance(model, str) or not model.strip():
            fail("missing resolved model")
        native_answers = raw.get("answers")
        if not isinstance(native_answers, list) or len(native_answers) != len(questions):
            fail("answers must contain exactly one entry per question")

        answers = {}
        for question, native in zip(questions, native_answers):
            name = question["name"]
            if not isinstance(native, dict) or native.get("name") != name:
                fail("answer names or order do not match questions")
            native_type = native.get("type")
            kind = question["kind"]
            if native_type == "refusal":
                answers[name] = {"kind": kind, "status": "refusal"}
                continue
            if native_type != kind:
                fail("answer type does not match question")

            answer = {"kind": kind, "status": "answered"}
            if kind == "predicate":
                answer["probability_true"] = native.get("probability")
            else:
                probability_items = native.get("probabilities")
                if not isinstance(probability_items, list):
                    fail("probabilities must be an array")
                expected = (
                    list(question["options"])
                    if kind == "choice"
                    else list(range(len(question["levels"])))
                )
                probabilities = {}
                seen = set()
                expected_labels = question.get("levels", [])
                for item in probability_items:
                    if not isinstance(item, dict):
                        fail("probability entry must be an object")
                    value = item.get("value")
                    if kind == "choice":
                        if not isinstance(value, str) or value not in expected:
                            fail("probability value was not supplied")
                        key = value
                    else:
                        if isinstance(value, bool) or not isinstance(value, int):
                            fail("score probability value must be an integer index")
                        if value < 0 or value >= len(expected):
                            fail("score probability value was not supplied")
                        key = str(value)
                        label = item.get("label")
                        if label != expected_labels[value]:
                            fail("score probability label does not match supplied level")
                    if key in seen:
                        fail("duplicate probability value")
                    seen.add(key)
                    probabilities[key] = item.get("probability")
                if seen != {str(value) if kind == "score" else value for value in expected}:
                    fail("probability values do not match supplied options")
                answer["probabilities"] = probabilities
                if "confidence" in native:
                    answer["confidence"] = native["confidence"]
                if kind == "choice":
                    answer["choice"] = native.get("choice")
                else:
                    answer["score"] = native.get("score")
                    answer["legend"] = list(question["levels"])

            answers[name] = answer

        response = {
            "model": model,
            "answers": answers,
            "usage": raw.get("usage"),
            "raw_response": raw,
        }
        return validate_response(response, questions)
