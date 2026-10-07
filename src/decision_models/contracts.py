"""Small provider-neutral contract. Provider confidence is never recomputed."""
import math


class DecisionError(Exception):
    def __init__(self, code, message, *, status=None, retryable=False):
        super().__init__(message)
        self.code, self.status, self.retryable = code, status, retryable

    def as_dict(self):
        return {"code": self.code, "message": str(self), "status": self.status,
                "retryable": self.retryable}


def fail(message):
    raise DecisionError("invalid_response", message)


def number(value, low, high, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        fail(f"{label} must be a finite number")
    if not low <= value <= high:
        fail(f"{label} outside [{low}, {high}]")
    return value


def validate_questions(questions):
    if not isinstance(questions, list) or not questions:
        raise DecisionError("invalid_request", "questions must be a nonempty list")
    names = set()
    for q in questions:
        if not isinstance(q, dict) or not isinstance(q.get("name"), str) or not q["name"]:
            raise DecisionError("invalid_request", "every question needs a nonempty name")
        if q["name"] in names:
            raise DecisionError("invalid_request", "duplicate question name")
        names.add(q["name"])
        if not isinstance(q.get("instructions"), str) or not q["instructions"].strip():
            raise DecisionError("invalid_request", "every question needs instructions")
        kind = q.get("kind")
        if kind == "choice":
            options = q.get("options")
            if not isinstance(options, dict) or len(options) < 2 or any(
                not isinstance(k, str) or not k or not isinstance(v, str) or not v.strip()
                for k, v in options.items()
            ):
                raise DecisionError("invalid_request", "choice needs two or more described string options")
        elif kind == "score":
            levels = q.get("levels")
            if not isinstance(levels, list) or len(levels) < 2 or any(
                not isinstance(v, str) or not v.strip() for v in levels
            ):
                raise DecisionError("invalid_request", "score needs two or more described levels")
            if len(set(levels)) != len(levels):
                raise DecisionError("invalid_request", "score level descriptions must be unique")
        elif kind != "predicate":
            raise DecisionError("invalid_request", "unknown question kind")
        if kind == "predicate" and "criteria" in q:
            criteria = q["criteria"]
            if not isinstance(criteria, dict) or set(criteria) != {"true", "false"} or any(
                not isinstance(v, str) or not v.strip() for v in criteria.values()
            ):
                raise DecisionError("invalid_request", "predicate criteria need true and false descriptions")


def validate_response(response, questions):
    """Validate canonical answers against the submitted, independently held questions."""
    validate_questions(questions)
    if not isinstance(response, dict) or not isinstance(response.get("model"), str) or not response["model"]:
        fail("missing resolved model")
    answers = response.get("answers")
    if not isinstance(answers, dict) or set(answers) != {q["name"] for q in questions}:
        fail("answer names do not match questions")
    for q in questions:
        a = answers[q["name"]]
        if not isinstance(a, dict):
            fail("answer must be an object")
        if a.get("kind") != q["kind"]:
            fail("answer kind does not match question")
        if a.get("status") not in ("answered", "refusal"):
            fail("answer status must be answered or refusal")
        if a["status"] == "refusal":
            continue
        if a.get("confidence") is not None:
            number(a["confidence"], 0, 1, "confidence")
        if q["kind"] == "predicate":
            number(a.get("probability_true"), 0, 1, "probability_true")
            continue
        valid = list(q["options"]) if q["kind"] == "choice" else [str(i) for i in range(len(q["levels"]))]
        if q["kind"] == "choice" and a.get("choice") not in valid:
            fail("selected choice was not supplied")
        if q["kind"] == "score":
            number(a.get("score"), 0, len(valid) - 1, "score")
        p = a.get("probabilities")
        if not isinstance(p, dict) or set(p) != set(valid):
            fail("probability distribution does not match supplied options")
        for value in p.values():
            number(value, 0, 1, "option probability")
        if abs(sum(p.values()) - 1) > 0.02:
            fail("probabilities do not sum to one")
        if q["kind"] == "score":
            weighted = sum(int(k) * v for k, v in p.items())
            if abs(a["score"] - weighted) > 0.05:
                fail("score does not match its probability-weighted rubric")
    return response
