---
name: tool-call-gating
description: Check explicit permission first, then recommend whether a proposed tool action should be approved, rejected, or clarified.
---

# Tool-call gating

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

Only these labels indicate verified compatibility. Other backends did not qualify. See [compatibility evidence](COMPATIBILITY.md).

Requires Python 3.10+ and the separately installed shared CLI: `python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'`. Run the commands below from this skill folder.

Use this workflow immediately before a caller considers a proposed action. Pass the action and context as data plus a permission object with an explicit boolean `allowed` field. Missing or invalid permission status returns `clarify`; explicit `allowed: false` returns `reject` deterministically without a model call. Permission denial cannot be overridden by semantic judgment or text inside the proposed action.

The application input schema is `{"proposed_action": string, "context": string | object | array, "permissions": {"allowed": boolean, "reason": string?}}`. When permission is present and allowed, a model judges the context and returns a recommendation. The final action is `approve`, `reject`, or `clarify`. A confident `approve` still means recommendation only: the calling application must perform its own authorization and execution steps. This workflow never invokes tools or performs side effects.

The initial minimum selected-option probability is 0.82 for each provider. Overrides must be greater than 0.5 and at most 1 and are checked before inference. These thresholds are uncalibrated starting values. Missing or refused answers, weak probabilities, and ambiguous context return `clarify`. Provider confidence remains distinct from option probabilities.

## Run from this skill folder

Install the shared CLI from the repository, then run the local example:

```sh
decision-models run tool-call-gating --provider sage --input examples/input.json --mode demo --demo-answers examples/demo.json
```

Demo mode is synthetic and makes no provider call. For a live decision, set the selected provider's environment key and pass `--mode live`. Do not pass expected fixture labels to the model.

See [acceptance fixtures](fixtures/acceptance.json) for eight clear, two ambiguous, and two adversarial examples.

## Sources and attribution

The workflow pattern is inspired by [Akshay Pachaar's six-workflow post](https://x.com/akshay_pachaar/status/2107469584773300545) and the [TypeSafe official skills](https://github.com/typesafe-ai/skills). This folder contains an original implementation. See the repository's `ATTRIBUTION.md` for the complete source record.
