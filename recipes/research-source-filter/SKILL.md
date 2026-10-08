---
name: research-source-filter
description: Assess whether a source excerpt is useful for a stated research brief before synthesis.
---

# Research Source Filter

Use this portable recipe to make one narrow choice from supplied text. It recommends a label and does not execute follow-up work. Run the hand-authored demonstration from this folder with:

```sh
decision-models recipe --recipe ./recipe.json --provider sage --input ./examples/input.json --demo-answers ./examples/demo.json --mode demo
```

`examples/input.json` and `examples/demo.json` are demo-only materials; acceptance cases are in `fixtures/acceptance.json`. Live mode uses the same command with `--mode live` and without `--demo-answers`; credentials stay in the environment.

The decision requires explicit Boolean permission and non-empty `state.content`. Missing evidence or genuinely ambiguous evidence should lead to review. Native confidence and selected-option probability are separate; both use the fixed 0.65 threshold. Synthetic examples do not calibrate any provider or model.

## Source and limits

This is a text-based screening recommendation, not fact-checking or a comprehensive literature review. It does not verify citations, open links, search other sources, or produce a research brief.

See [RESOURCES.md](RESOURCES.md) for source attribution and the adaptation boundary.
