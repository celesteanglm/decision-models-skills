---
name: draft-quality-triage
description: Classify a draft against its stated goal and available feedback.
---

# Decide whether a draft is ready for another revision

Use this portable recipe to recommend one bounded label from text evidence. It does not perform the recommended action. Missing or conflicting evidence should lead to review.

The recipe configuration and examples are local to this folder: [recipe](recipe.json), [sample input](examples/input.json), [hand-authored demo answer](examples/demo.json), and [acceptance fixtures](fixtures/acceptance.json). The demo answer is illustrative configuration, not model output or calibration evidence.

Install the shared CLI in a Python 3.10+ environment:

```sh
python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

Run the copied recipe from any working directory by passing its paths explicitly:

```sh
decision-models recipe --recipe /path/to/copied/draft-quality-triage/recipe.json --provider sage --input /path/to/copied/draft-quality-triage/examples/input.json --demo-answers /path/to/copied/draft-quality-triage/examples/demo.json --mode demo
```

For live inference, use the same command with `--mode live` and omit `--demo-answers`. Credentials are supplied through the provider environment. The recipe holds its confidence and selected-probability thresholds at 0.65; these are fixed operating gates, not a model-calibration claim. Provider confidence and the selected option probability remain distinct signals. A typed result does not establish correctness.

This is a text-only decision slice inspired by the [original community post](https://x.com/robj3d3/status/2100722975645598191). It does not reproduce the source application, its speed or cost claims, or its reported outcomes. It cannot verify live state or authorize, send, move, click, or execute anything. A host application must independently enforce permissions and validate any later action.
