---
name: model-routing
description: Select an eligible model for a task, with a confidence-based escalation path.
---

# Model routing

Recommend an eligible model for a supplied task using the caller's capability, cost, and other constraints.

## Inputs

Accept the task, eligible models with IDs and capability descriptions, and any budget or capability requirements. Model costs are optional supplied facts. The agent making this recommendation and the models being considered for the task are separate roles.

## Procedure

1. Identify required capabilities and filter out candidates that violate explicit constraints. Use only supplied capability and cost information.
2. If no eligible candidate remains, return `escalate` with the unmet constraint.
3. Compare the remaining candidates with the task. Choose the least costly capable candidate when comparable costs are supplied. Otherwise choose a clearly supported capability match and disclose that cost ordering is unknown.
4. Return `escalate` if the supplied descriptions cannot establish a capable candidate or material constraints conflict. If equally suitable candidates remain, use a user-specified tie-break rule or request clarification.
5. If the caller requires a native confidence gate, apply that gate only to an actual supported confidence field; escalate when it is missing. Direct assessment does not require a confidence number.

## Return

Return `action` as `route` or `escalate`, `model_id` as a supplied candidate ID or null, concise `reasons`, supporting `evidence`, and `missing_information`. Never invent a model ID or invoke the chosen model as part of this skill.

## Model choice

Use the agent's current model to follow these instructions. If the user requests a particular decision model or supplies an existing model tool, use that integration within the user's configured access. If the requested integration is unavailable, explain what is missing rather than silently substituting another model. This skill requires no package installation, command-line tool, or bundled executable.

Apply a numerical gate only when the user requests it and the selected integration supplies the required metric. Keep native probabilities, native confidence, rubric scores, and qualitative judgments distinct. If a required metric is absent, use the review or escalation outcome and identify the missing metric; do not invent probabilities or treat self-reported confidence as calibrated.

## Examples and recorded checks

[Sample input](examples/input.json) illustrates the available evidence fields. [Acceptance cases](fixtures/acceptance.json) and [synthetic demo answers](examples/demo.json) support maintainer evaluation; expected labels and demo answers are not evidence for a user's decision.

The [compatibility evidence](COMPATIBILITY.md) describes the optional Python reference implementation with specific native APIs. These results do not certify instruction-only use with the agent's current model or make those backends a requirement.

## Sources

- Workflow inspiration: [Akshay Pachaar](https://x.com/akshay_pachaar/status/2107469584773300545) and [TypeSafe's skills](https://github.com/typesafe-ai/skills). These instructions are independently authored.
