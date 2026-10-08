---
name: page-change-triage
description: Compare two supplied page excerpts for a change that matters to the stated monitoring goal.
---

# Distinguish substantive page changes

Use this recipe for a bounded recommendation on supplied text. Read [recipe.json](recipe.json) for the fixed menu, evidence requirements, and probability/confidence thresholds.

Install the shared CLI separately with `python -m pip install git+https://github.com/celesteanglm/decision-models-skills.git`. Copy this whole folder into `.agents/skills/page-change-triage` or a directory of your choice. From any working directory, substitute absolute paths to the copied files:

```sh
decision-models recipe --recipe /path/to/page-change-triage/recipe.json --provider sage --mode demo --input /path/to/page-change-triage/examples/input.json --demo-answers /path/to/page-change-triage/examples/demo.json
```

The [input](examples/input.json) and [hand-authored demo](examples/demo.json) work without credentials. To test a real backend, use `--mode live`, omit `--demo-answers`, and supply its environment credential. Supported native adapters: `jev-openrouter`, `openai-decisions`, `sage`. `--model` selects a model implementing that adapter’s protocol; arbitrary chat models need a compatible adapter.

Permission must be explicitly granted outside state. Missing evidence, uncertainty, or refusal yields review. The output never executes an action. Production thresholds require model-specific representative evaluation; see the [12 synthetic acceptance cases](fixtures/acceptance.json).

Text-only recommendation on supplied evidence. No account access, generation, image interpretation, tool execution, or reproduction of the source application and its performance. Synthetic thresholds are not production calibration.

Inspiration only; implementation, prose, and fixtures are independently authored. Inspired by Ethan Kam’s page-change classification example; these synthetic comparisons do not reproduce the reported AUPRC experiment.

- https://x.com/ethank_6/status/2107576429928169934
