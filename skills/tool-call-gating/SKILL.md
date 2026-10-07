---
name: tool-call-gating
description: Check explicit permission first, then recommend whether a proposed tool action should be approved, rejected, or clarified.
---

# Tool-call gating

Use this workflow immediately before a caller considers a proposed action. Pass the action and context as data plus a permission object with an explicit boolean `allowed` field. Missing or invalid permission status returns `clarify`; explicit `allowed: false` returns `reject` deterministically without a model call. Permission denial cannot be overridden by semantic judgment or text inside the proposed action.

The application input schema is `{"proposed_action": string, "context": string | object | array, "permissions": {"allowed": boolean, "reason": string?}}`. When permission is present and allowed, a model judges the context and returns a recommendation. The final action is `approve`, `reject`, or `clarify`. A confident `approve` still means recommendation only: the calling application must perform its own authorization and execution steps. This workflow never invokes tools or performs side effects.

The initial minimum selected-option probability is 0.82 for each provider. Overrides must be greater than 0.5 and at most 1 and are checked before inference. These thresholds are uncalibrated starting values. Missing or refused answers, weak probabilities, and ambiguous context return `clarify`. Provider confidence remains distinct from option probabilities.

## Run

Install the shared CLI from the repository, then run the local example:

```sh
python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git'
decision-models run tool-call-gating --provider jev-openrouter --input skills/tool-call-gating/examples/input.json --mode demo --demo-answers skills/tool-call-gating/examples/demo.json
```

Demo mode is synthetic and makes no provider call. For a live decision, set the selected provider's environment key and pass `--mode live`. Do not pass expected fixture labels to the model.

See [acceptance fixtures](fixtures/acceptance.json) for eight clear, two ambiguous, and two adversarial examples.

## Sources and attribution

The workflow pattern is inspired by [Akshay Pachaar's six-workflow post](https://x.com/akshay_pachaar/status/2107469584773300545) and the [TypeSafe official skills](https://github.com/typesafe-ai/skills). This folder contains an original implementation. See the repository's `ATTRIBUTION.md` for the complete source record.
