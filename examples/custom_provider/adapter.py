"""Illustrative wire mapping for a fictional fourth provider; never calls a service."""
from decision_models.contracts import DecisionError, validate_response


class ExampleAdapter:
    name = "fictional-fourth-provider"
    endpoint = "offline://fictional-fourth-provider"
    key_env = "UNUSED_OFFLINE_EXAMPLE_KEY"
    default_model = "fictional-model-v1"

    def build_payload(self, state, questions, model):
        """Map canonical state/questions to this fictional provider's wire shape."""
        if len(questions) != 1 or questions[0].get("kind") != "choice":
            raise DecisionError("invalid_request", "example adapter accepts one choice question")
        question = questions[0]
        return {
            "model_name": model,
            "context": state,
            "task": {
                "question_id": question["name"],
                "instruction": question["instructions"],
                "choices": question["options"],
            },
        }

    def parse_response(self, raw, questions):
        """Map native answer/distribution/usage through without estimating metrics."""
        if not isinstance(raw, dict) or not isinstance(raw.get("resolved_model"), str):
            raise DecisionError("invalid_response", "provider response is missing resolved_model")
        records = raw.get("decisions")
        if not isinstance(records, list) or len(records) != len(questions):
            raise DecisionError("invalid_response", "provider response has the wrong decision count")
        answers = {}
        for question, record in zip(questions, records):
            if not isinstance(record, dict) or record.get("question_id") != question["name"]:
                raise DecisionError("invalid_response", "provider decision does not match submitted question")
            if question["kind"] != "choice":
                raise DecisionError("invalid_response", "example adapter only maps choice answers")
            answer = {
                "kind": "choice",
                "status": "answered",
                "choice": record.get("selected"),
                "probabilities": record.get("distribution"),
            }
            # Confidence is copied only when this fictional native response has it.
            if "confidence" in record:
                answer["confidence"] = record["confidence"]
            answers[question["name"]] = answer
        canonical = {"model": raw["resolved_model"], "answers": answers,
                    "usage": raw.get("usage"), "raw_response": raw}
        return validate_response(canonical, questions)


def offline_transport(endpoint, payload, api_key, timeout=20, *, scenario="recommend-billing"):
    """Return fixed synthetic fixtures; reject every endpoint except the offline URI."""
    if endpoint != "offline://fictional-fourth-provider" or api_key != "OFFLINE-EXAMPLE-NOT-A-CREDENTIAL":
        raise DecisionError("invalid_request", "offline example transport cannot contact a service")
    choice_keys = list(payload["task"]["choices"])
    if "billing" not in choice_keys:
        raise DecisionError("invalid_request", "offline billing scenario needs a billing choice")
    other_choices = [choice for choice in choice_keys if choice != "billing"]
    probabilities = {choice: (0.90 if choice == "billing" else 0.10 / len(other_choices))
                     for choice in choice_keys}
    record = {"question_id": payload["task"]["question_id"], "selected": "billing",
              "distribution": probabilities}
    if scenario == "recommend-billing":
        record["confidence"] = 0.92
    elif scenario == "malformed-answer":
        record["selected"] = "not-a-supplied-option"
        # No confidence or probability is fabricated to rescue the invalid answer.
    elif scenario != "missing-confidence":
        raise DecisionError("invalid_request", "unknown offline scenario")
    return {"resolved_model": payload["model_name"], "decisions": [record],
            "usage": {"input_tokens": 41, "output_tokens": 7, "source": "synthetic fixture"}}
