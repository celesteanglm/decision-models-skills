---
name: retrieved-instruction-screening
description: Recommend whether retrieved material should be isolated before use as evidence.
---

# Screen instructions embedded in retrieved text

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen)

Only these labels indicate verified compatibility. Other backends did not qualify. See [compatibility evidence](COMPATIBILITY.md).

Use this recipe for a bounded recommendation on supplied text. Read [recipe.json](recipe.json) for the fixed menu, evidence requirements, and probability/confidence thresholds.

Install the shared CLI separately with `python -m pip install git+https://github.com/celesteanglm/decision-models-skills.git`. Copy this whole folder into `.agents/skills/retrieved-instruction-screening` or a directory of your choice. From any working directory, substitute absolute paths to the copied files:

```sh
decision-models recipe --recipe /path/to/retrieved-instruction-screening/recipe.json --provider jev-openrouter --mode demo --input /path/to/retrieved-instruction-screening/examples/input.json --demo-answers /path/to/retrieved-instruction-screening/examples/demo.json
```

The [input](examples/input.json) and [hand-authored demo](examples/demo.json) work without credentials. To test a real backend, use `--mode live`, omit `--demo-answers`, and supply its environment credential. Use a backend labeled Working above. `--model` selects a model implementing that adapter’s protocol; arbitrary chat models need a compatible adapter.

Permission must be explicitly granted outside state. Missing evidence, uncertainty, or refusal yields review. The output never executes an action. Production thresholds require model-specific representative evaluation; see the [12 synthetic acceptance cases](fixtures/acceptance.json).

Text-only recommendation on supplied evidence. No account access, generation, image interpretation, tool execution, or reproduction of the source application and its performance. Synthetic thresholds are not production calibration.

Inspiration only; implementation, prose, and fixtures are independently authored. A concrete retrieval-focused adaptation of the input-guardrail pattern credited to Akshay Pachaar.

- https://x.com/akshay_pachaar/status/2107469584773300545
