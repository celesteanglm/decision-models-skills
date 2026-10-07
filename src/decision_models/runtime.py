"""Integration seam between independently implemented providers and workflows."""
import importlib
import json
import os
import time
from .contracts import DecisionError, validate_questions, validate_response
from .transport import http_transport

SKILLS = ("input-guardrails", "model-routing", "reranking", "tool-call-gating", "confidence-gates", "output-evaluation")
PROVIDERS = {"jev-openrouter": "openrouter", "openai-decisions": "openai", "sage": "sage"}


def adapter_for(provider):
    if provider not in PROVIDERS:
        raise DecisionError("invalid_request", "unknown provider")
    return importlib.import_module("decision_models.providers." + PROVIDERS[provider]).Adapter()


def workflow_for(skill):
    if skill not in SKILLS:
        raise DecisionError("invalid_request", "unknown skill")
    return importlib.import_module("decision_models.workflows." + skill.replace("-", "_"))


def execute(skill, provider, data, *, mode="demo", demo_answers=None, model=None,
            transport=http_transport, before_attempt=None, after_attempt=None, retries=0):
    if not isinstance(data, dict):
        raise DecisionError("invalid_request", "workflow input must be a JSON object")
    if mode not in ("demo", "live") or not 0 <= retries <= 2:
        raise DecisionError("invalid_request", "invalid mode or retry count")
    adapter, workflow = adapter_for(provider), workflow_for(skill)
    inputs = dict(data, _provider=provider)
    prepared = workflow.build(inputs)
    out = {"skill": skill, "provider": provider, "mode": mode, "executed_action": False,
           "requested_model": model or adapter.default_model}
    if prepared.get("early_result") is not None:
        return dict(out, result=prepared["early_result"], source="deterministic", response=None, latency_ms=0, attempts=0)
    questions = prepared["questions"]
    validate_questions(questions)
    payload = adapter.build_payload(prepared["state"], questions, model or adapter.default_model)
    try:
        json.dumps(payload, allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise DecisionError("invalid_request", "input must contain finite JSON values") from exc
    start = time.perf_counter()
    attempts = 0
    if mode == "demo":
        if demo_answers is None:
            raise DecisionError("invalid_request", "demo mode requires an explicit hand-authored answer file")
        response = validate_response({"model": "DEMO-hand-authored-not-model-output", "answers": demo_answers,
                                      "usage": None, "raw_response": None}, questions)
    else:
        key = os.environ.get(adapter.key_env)
        if not key:
            raise DecisionError("missing_credentials", f"set {adapter.key_env} for live mode")
        for attempt in range(retries + 1):
            if before_attempt:
                before_attempt(provider, payload)
            attempts += 1
            try:
                raw = transport(adapter.endpoint, payload, key, 20)
                # Record usage even when subsequent answer validation fails.
                if after_attempt:
                    after_attempt(provider, raw)
                response = adapter.parse_response(raw, questions)
                break
            except DecisionError as exc:
                if not exc.retryable or attempt >= retries:
                    raise
                # Only explicit rate limiting is eligible, never ambiguous paid timeouts.
                time.sleep(min(2, attempt + 1))
    result = workflow.decide(inputs, response)
    if not isinstance(result, dict) or not isinstance(result.get("action"), str):
        raise DecisionError("invalid_response", "workflow did not return a policy action")
    return dict(out, result=result, source="demo" if mode == "demo" else "live",
                response=response, latency_ms=round((time.perf_counter()-start)*1000, 3), attempts=attempts)
