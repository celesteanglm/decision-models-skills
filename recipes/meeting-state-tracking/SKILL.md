---
name: meeting-state-tracking
description: Summarize the current conversational state from a short meeting excerpt.
---

# Meeting State Tracking

Use this portable recipe to make one narrow choice from supplied text. It recommends a label and does not execute follow-up work. Run the hand-authored demonstration from this folder with:

```sh
decision-models recipe --recipe ./recipe.json --provider sage --input ./examples/input.json --demo-answers ./examples/demo.json --mode demo
```

`examples/input.json` and `examples/demo.json` are demo-only materials; acceptance cases are in `fixtures/acceptance.json`. Live mode uses the same command with `--mode live` and without `--demo-answers`; credentials stay in the environment.

The decision requires explicit Boolean permission and non-empty `state.content`. Missing evidence or genuinely ambiguous evidence should lead to review. Native confidence and selected-option probability are separate; both use the fixed 0.65 threshold. Synthetic examples do not calibrate any provider or model.

## Source and limits

A short transcript may omit tone, prior context, or later turns. Semantic signals are not proof of participant intent; this does not measure people, record a meeting, or declare consensus beyond the supplied excerpt.

See [RESOURCES.md](RESOURCES.md) for source attribution and the adaptation boundary.
