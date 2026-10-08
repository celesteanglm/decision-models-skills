---
name: email-queue-routing
description: Recommend a handling queue for one email using its request and context.
---

# Route an email to a review queue

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

Only these labels indicate verified compatibility. Other backends did not qualify. See [compatibility evidence](COMPATIBILITY.md).

Use this portable recipe to recommend one bounded label from text evidence. It does not perform the recommended action. Missing or conflicting evidence should lead to review.

The recipe configuration and examples are local to this folder: [recipe](recipe.json), [sample input](examples/input.json), [hand-authored demo answer](examples/demo.json), and [acceptance fixtures](fixtures/acceptance.json). The demo answer is illustrative configuration, not model output or calibration evidence.

Install the shared CLI in a Python 3.10+ environment:

```sh
python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

Run the copied recipe from any working directory by passing its paths explicitly:

```sh
decision-models recipe --recipe /path/to/copied/email-queue-routing/recipe.json --provider sage --input /path/to/copied/email-queue-routing/examples/input.json --demo-answers /path/to/copied/email-queue-routing/examples/demo.json --mode demo
```

For live inference, use the same command with `--mode live` and omit `--demo-answers`. Credentials are supplied through the provider environment. The recipe holds its confidence and selected-probability thresholds at 0.65; these are fixed operating gates, not a model-calibration claim. Provider confidence and the selected option probability remain distinct signals. A typed result does not establish correctness.

This is a text-only decision slice inspired by the [original community post](https://x.com/rileybrown/status/2100404532119269426). It does not reproduce the source application, its speed or cost claims, or its reported outcomes. It cannot verify live state or authorize, send, move, click, or execute anything. A host application must independently enforce permissions and validate any later action.
