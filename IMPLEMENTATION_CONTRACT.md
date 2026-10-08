# Optional Python reference implementation contract

This contract governs the maintainer reference code, not installation or use of the model-agnostic SKILL.md instructions. The reference uses Python 3.10+ and the standard library.

## Provider modules

Each `providers/<name>.py` exports `Adapter` with class attributes `name`, `endpoint`, `key_env`, `default_model`; methods `build_payload(state, questions, model)` and `parse_response(raw, questions)`.

Canonical questions are dictionaries: `{name, kind, instructions}` where kind is `predicate`, `choice` (plus `options: {string: description}`), or `score` (plus `levels: [description]`). Predicate can have `criteria: {true: description, false: description}`. All identifiers/options are strings, ordering is stable.

Canonical response: `{model: resolved model string, answers: {name: answer}, usage: native usage or null, raw_response: raw}`. Answer: `{kind, status: "answered"}` plus `probability_true` for predicate, `choice`/`probabilities`/optional native `confidence` for choice, `score`/`probabilities`/optional native `confidence`/optional `legend` for score. Score probability keys are zero-based index strings. Refusal: `{kind: original kind, status: "refusal"}`. Do not invent confidence or cost. Return `validate_response(response, questions)` from shared contracts. Raise `DecisionError("invalid_response", safe message)` for malformed native responses. No network/auth logic in adapters.

## Workflow modules

Each `workflows/<underscore_name>.py` exports `build(data)` returning `{state, questions, early_result}`. `early_result` is null or a final policy outcome requiring no inference. `decide(data, response)` returns a JSON-compatible policy result. Include `action` as a string and stable `reasons` list. Each workflow owns its input validation, fixed documented thresholds, and policy. Never execute side effects. Catch refusals/missing required confidence with review outcomes. Threshold overrides, if supported, must be validated (0..1 finite values); defaults are separate per provider via data `_provider` set by runtime. Do not put labels or demo answers in state. JSON input files contain only application inputs.

All skills include standalone `SKILL.md`, `examples/input.json`, `examples/demo.json`, and `fixtures/acceptance.json`. Demo JSON contains canonical `answers` ONLY; runtime provides synthetic model and validates them. Each acceptance fixture: `{id, category: clear|ambiguous|adversarial, input: application inputs, expected: {actions: [...], ...}, demo_answers: canonical answer map}`. Exactly 8 clear, 2 ambiguous, 2 adversarial per skill. Expectations remain outside model inputs. Reranking can add `expected.top_id`; evaluator can add `expected.metric_ranges`. Every fixture must independently define expected behavior/rationale. Root may revise fixture design before freezing. Skill names/slugs: input-guardrails, model-routing, reranking, tool-call-gating, confidence-gates, output-evaluation.

Maintainer example: `python -m decision_models run <slug> --provider jev-openrouter --input /path/examples/input.json --mode demo --demo-answers /path/examples/demo.json`. Live mode omits synthetic answers and uses `--mode live`. Install the optional reference package for these maintainer commands. Users can install or reference the Markdown skill folders independently; they do not require this package or a global console command.
