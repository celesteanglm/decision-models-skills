# Optional Python reference implementation contract

This contract governs the maintainer reference code, not installation or use of the model-agnostic SKILL.md instructions. The reference uses Python 3.10+ and the standard library.

## Provider modules

Each `providers/<name>.py` exports `Adapter` with class attributes `name`, `endpoint`, `key_env`, `default_model`; methods `build_payload(state, questions, model)` and `parse_response(raw, questions)`.

Canonical questions are dictionaries: `{name, kind, instructions}` where kind is `predicate`, `choice` (plus `options: {string: description}`), or `score` (plus `levels: [description]`). Predicate can have `criteria: {true: description, false: description}`. All identifiers/options are strings, ordering is stable.

Canonical response: `{model: resolved model string, answers: {name: answer}, usage: native usage or null, raw_response: raw}`. Answer: `{kind, status: "answered"}` plus `probability_true` for predicate, `choice`/`probabilities`/optional native `confidence` for choice, `score`/`probabilities`/optional native `confidence`/optional `legend` for score. Score probability keys are zero-based index strings. Refusal: `{kind: original kind, status: "refusal"}`. Do not invent confidence or cost. Return `validate_response(response, questions)` from shared contracts. Raise `DecisionError("invalid_response", safe message)` for malformed native responses. No network/auth logic in adapters.

## Workflow modules

Each `workflows/<underscore_name>.py` exports `build(data)` returning `{state, questions, early_result}`. `early_result` is null or a final policy outcome requiring no inference. `decide(data, response)` returns a JSON-compatible policy result. Include `action` as a string and stable `reasons` list. Each workflow owns its input validation, fixed documented thresholds, and policy. Never execute side effects. Catch refusals/missing required confidence with review outcomes. Threshold overrides, if supported, must be validated (0..1 finite values); defaults are separate per provider via data `_provider` set by runtime. Do not put labels or demo answers in state. JSON input files contain only application inputs.

All skills include standalone `SKILL.md`, `examples/input.json`, `examples/demo.json`, and `fixtures/acceptance.json`. Demo JSON contains canonical `answers` ONLY; runtime provides synthetic model and validates them. Each acceptance fixture: `{id, category: clear|ambiguous|adversarial, input: application inputs, expected: {actions: [...], ...}, demo_answers: canonical answer map}`. Exactly 8 clear, 2 ambiguous, 2 adversarial per skill. Expectations remain outside model inputs. Reranking can add `expected.top_id`; evaluator can add `expected.metric_ranges`. Every fixture must independently define expected behavior/rationale. Root may revise fixture design before freezing. Skill names/slugs: input-guardrails, model-routing, reranking, tool-call-gating, confidence-gates, output-evaluation.

Maintainer example: `python -m decision_models decide --config skills/<id>/decision.json`. Install the optional reference package for this maintainer command. Users can install or reference the Markdown skill folders independently; they do not require this package or a global console command.

## Image reference adapter

`scripts/image_reference.py` implements the separate [image schema version 2](DECISION_CONTRACT.md#image-schema-version-2). Its Sage adapter uses `/decide/batch` with `content.kind: image`, a local image encoded as a data URI, and optional caption text. Canonical predicate, choice, and score questions map to native YesNo, Choice, and Scale questions. The public batch endpoint selects the model. The adapter checks the resolved model against `levanto-sage-v1.4` and rejects drift.

The adapter preserves raw answers, native usage, distributions, and fractional scores. Image Choice has native probabilities but no separate confidence. The policy uses selected-option probability and leaves confidence unavailable. An abstention produces review. Malformed responses and unsupported backends produce explicit errors.

Permission checks precede file reads and inference. Images must be PNG, JPEG, or WebP within the configured asset root, at most 4 MiB decoded, with a maximum edge of 8192 pixels and at most 4096 squared pixels. Remote URLs and paths escaping the root are rejected. Neither captions nor image text can grant permission. Recommendations never execute actions.

The standalone helper imports only the optional installed reference package. It can run from another working directory with a copied skill folder. The Markdown instructions themselves need only an agent that can inspect images. Sage is the bundled native image adapter. Another backend can supply `adapter=` without editing the runner, using its own wire mapping and the same local-image checks. Its compatibility label still requires independent qualification.

## Third-party text adapter and runnable example

[`examples/custom_provider/`](examples/custom_provider/README.md) is the complete offline example for a fictional fourth text backend. It maps canonical state/questions in `build_payload`, maps the provider-shaped answer in `parse_response`, and calls `execute_use_case` with the adapter injected. Its transport accepts only an `offline://` endpoint and returns synthetic fixtures. The runner's response-parsing path receives a temporary test sentinel rather than a real credential. The example needs no API access or repository-root imports. Copy the example and a complete skill folder, install this package in your application environment, then follow its README command from any working directory.

For your own text integration, implement the same adapter surface (`name`, `endpoint`, `key_env`, `default_model`, `build_payload`, and `parse_response`). Map every field explicitly. Preserve the raw provider response and native usage; copy native probabilities and confidence only when supplied. If a required native metric is absent, leave it absent so the skill's policy can route to review. Do not infer calibrated confidence, probabilities, or cost from free-form text. A malformed answer should raise `DecisionError("invalid_response", safe_message)`.

Call `execute_use_case(..., adapter=your_adapter, transport=your_transport)` in your own application. The runtime reads the credential named by `key_env` from the process environment and passes it to the transport. A custom transport can support SDKs or non-Bearer authentication. Keep transport and authentication code in your application; the copied skill folder remains independent. Use an explicit model ID. A call to a real provider can be billable. Inspect the offline mapping and confirm an authorized budget before making one. The example transport cannot select a live service.

The generic `execute(..., adapter=..., policy=...)` runtime seam follows the same boundary for general workflows. A custom confidence-gates provider needs trusted policy with `send` and `escalate_below`; a custom output-evaluation provider needs `grounded`, `relevant`, `helpfulness`, and `fail_below`. Image integrations use `execute_image(..., adapter=..., model=...)` and must preserve the same local pixel-content restrictions and canonical response validation. These seams permit an application-specific integration; the fictional example does not qualify a provider, add one to the built-in catalog, or provide an image backend.
