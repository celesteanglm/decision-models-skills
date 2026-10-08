"""Portable, attributed decision slices. No action executor is present."""
import json
import re
import time
from pathlib import Path
import os

from .contracts import DecisionError, number, validate_questions, validate_response
from .runtime import adapter_for
from .transport import http_transport


def load_recipe(path):
    try:
        recipe = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DecisionError("invalid_request", "cannot read valid recipe JSON") from exc
    return validate_recipe(recipe)


def validate_recipe(recipe):
    if not isinstance(recipe, dict) or type(recipe.get("schema_version")) is not int or recipe["schema_version"] != 1:
        raise DecisionError("invalid_request", "recipe schema_version must be 1")
    if not isinstance(recipe.get("id"), str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", recipe["id"]):
        raise DecisionError("invalid_request", "invalid recipe id")
    for field in ("title", "description", "inspiration", "limitations"):
        if not isinstance(recipe.get(field), str) or not recipe[field].strip():
            raise DecisionError("invalid_request", f"recipe needs {field}")
    sources = recipe.get("source_urls")
    if not isinstance(sources, list) or not sources or any(not isinstance(s, str) or not s.startswith("https://") for s in sources):
        raise DecisionError("invalid_request", "recipe needs HTTPS source URLs")
    fields = recipe.get("required_state_fields")
    if not isinstance(fields, list) or not fields or any(not isinstance(f, str) or not f for f in fields) or len(set(fields)) != len(fields):
        raise DecisionError("invalid_request", "recipe needs unique required state fields")
    q = recipe.get("question")
    validate_questions([q])
    if q.get("kind") != "choice" or q.get("name") != "decision" or "review" not in q["options"] or len(q["options"]) > 6:
        raise DecisionError("invalid_request", "recipe needs a decision choice with review and at most six options")
    policy = recipe.get("policy")
    if not isinstance(policy, dict) or policy.get("review_choice") != "review":
        raise DecisionError("invalid_request", "recipe needs review policy")
    for field in ("confidence_threshold", "probability_threshold"):
        try:
            number(policy.get(field), 0, 1, field)
        except DecisionError as exc:
            raise DecisionError("invalid_request", "invalid recipe threshold") from exc
    return recipe


def prepare_recipe(recipe, data):
    validate_recipe(recipe)
    if not isinstance(data, dict):
        raise DecisionError("invalid_request", "recipe input must be an object")
    if data.get("permission_granted") is not True:
        return {"action": "deny", "choice": None, "reasons": ["permission_not_granted"]}
    state = data.get("state")
    if not isinstance(state, dict) or any(
        field not in state or state[field] is None or (isinstance(state[field], str) and not state[field].strip()) or state[field] == [] or state[field] == {}
        for field in recipe["required_state_fields"]
    ):
        return {"action": "review", "choice": "review", "reasons": ["missing_evidence"]}
    try:
        json.dumps(state, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise DecisionError("invalid_request", "state must be finite JSON") from exc
    return None


def recipe_decision(recipe, response):
    answer = response["answers"]["decision"]
    if answer["status"] == "refusal":
        return {"action": "review", "choice": "review", "reasons": ["provider_refusal"]}
    confidence = answer.get("confidence")
    choice = answer["choice"]
    probability = answer["probabilities"][choice]
    policy = recipe["policy"]
    reasons = []
    if choice == "review":
        reasons.append("model_requested_review")
    if confidence is None:
        reasons.append("confidence_missing")
    elif confidence < policy["confidence_threshold"]:
        reasons.append("confidence_below_threshold")
    if probability < policy["probability_threshold"]:
        reasons.append("probability_below_threshold")
    return {"action": "review" if reasons else "recommend", "choice": "review" if reasons else choice,
            "reasons": reasons or ["bounded_recommendation"], "confidence": confidence,
            "selected_probability": probability}


def execute_recipe(recipe, provider, data, *, mode="demo", demo_answers=None, model=None,
                   transport=http_transport, before_attempt=None, after_attempt=None, adapter=None):
    if mode not in ("demo", "live"):
        raise DecisionError("invalid_request", "invalid recipe mode")
    early = prepare_recipe(recipe, data)
    adapter = adapter_for(provider) if adapter is None else adapter
    out = {"recipe": recipe["id"], "provider": provider, "mode": mode,
           "requested_model": model or adapter.default_model, "executed_action": False}
    if early is not None:
        return dict(out, result=early, source="deterministic", response=None, latency_ms=0, attempts=0)
    questions = [recipe["question"]]
    started = time.perf_counter()
    if mode == "demo":
        if not isinstance(demo_answers, dict):
            raise DecisionError("invalid_request", "demo requires explicit hand-authored answers")
        response = validate_response({"model": "DEMO-hand-authored-not-model-output", "answers": demo_answers,
                                      "usage": None, "raw_response": None}, questions)
    else:
        key = os.environ.get(adapter.key_env)
        if not key:
            raise DecisionError("missing_credentials", f"set {adapter.key_env} for live mode")
        # Only state and the trusted question enter inference. Permissions and
        # fixture expectations are never serialized into provider requests.
        payload = adapter.build_payload(data["state"], questions, model or adapter.default_model)
        if before_attempt:
            before_attempt(provider, payload)
        raw = transport(adapter.endpoint, payload, key, 20)
        if after_attempt:
            after_attempt(provider, raw)
        response = adapter.parse_response(raw, questions)
    return dict(out, result=recipe_decision(recipe, response), source=mode, response=response,
                latency_ms=round((time.perf_counter() - started) * 1000, 3), attempts=int(mode == "live"))
