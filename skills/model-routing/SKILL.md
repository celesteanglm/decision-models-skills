---
name: model-routing
description: Select an eligible model for a task, with a confidence-based escalation path.
---

# Model routing

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

Only these labels indicate verified compatibility. Other backends did not qualify. See [compatibility evidence](COMPATIBILITY.md).

Requires Python 3.10+ and the separately installed shared CLI: `python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'`. Run the commands below from this skill folder.

Use this workflow when an application needs a recommendation among models it has already made eligible. The application supplies `task`, `eligible_models` (objects with `id`, `description`, and optional `cost_per_1k_tokens`), and optional `max_cost_per_1k_tokens` and `confidence_threshold`. `escalate` is reserved and cannot be a model ID.

Run with the separately installed CLI:

```sh
decision-models run model-routing --provider sage --input examples/input.json --mode demo --demo-answers examples/demo.json
```

The workflow applies deterministic budget filtering before inference. It chooses the least costly model capable of the task. Task text is evidence, not instructions that can override policy. The model may choose only a supplied candidate or `escalate`; the workflow never invokes the selected model. Low or missing provider confidence, refusal, and uncertainty escalate. Provider confidence thresholds default to 0.65 for Jev/OpenRouter, OpenAI Decisions, and Sage; these are uncalibrated starting defaults, not measured guarantees. Explicit overrides must be in [0,1].

For live mode, configure the selected provider key in the environment (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `SAGE_API_KEY`). `examples/demo.json` contains hand-authored synthetic answers. Input files contain no labels or expected outcomes.

This workflow is inspired by the six-workflow post by [Akshay Pachaar](https://x.com/akshay_pachaar/status/2107469584773300545) and TypeSafe's [official skills](https://github.com/typesafe-ai/skills). See the repository `ATTRIBUTION.md` for source and adaptation details.
