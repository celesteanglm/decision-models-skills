# Plugging in another decision model

Recipes describe a decision and its policy separately from the provider endpoint and model. Their question, evidence, and expected outcomes do not name Jev. The CLI currently supplies three native adapters: Jev/OpenRouter, OpenAI Decisions, and Sage SystemOne. `--model` selects a model implementing the chosen adapter's protocol; it does not convert an arbitrary chat model into a decision model.

## Native adapter interface

The Python runner accepts a custom adapter without changing the recipe or adding repository imports to a copied folder:

```python
from decision_models.recipes import execute_recipe, load_recipe

# MyAdapter is application-owned, installed code implementing the interface below.
adapter = MyAdapter()
result = execute_recipe(
    load_recipe("/path/to/copied/recipe.json"),
    "my-small-decision-model",
    {"state": {"content": "Evidence to classify"}, "permission_granted": True},
    mode="live",
    adapter=adapter,
)
```

An adapter supplies `endpoint`, `key_env`, `default_model`, `build_payload(state, questions, model)`, and `parse_response(raw, questions)`. Authentication and HTTP transport stay in the shared runner. `transport=` remains injectable for independent contract tests. Adapters must preserve the resolved model, native usage, full raw response, distributions, refusals, and native confidence without recomputing confidence. See [contracts.py](../src/decision_models/contracts.py) and the [three native adapters](../src/decision_models/providers/).

This hook is for trusted application code; the CLI does not import executable modules from untrusted recipe files. The built-in evaluation CLI can evaluate its three named adapters. Only a Working result for a specific skill receives a positive compatibility label. A custom adapter needs independent golden contract tests and live fixture receipts; the existing compatibility labels do not transfer to it.

## Different output capabilities

Native decision distributions, classifier logits, reranker relevance scores, and a chat model's generated confidence are different signals. The current canonical contract requires actual choice probabilities. A model that returns only a label or arbitrary score is not compatible simply because its endpoint accepts OpenAI-style messages. Do not invent a distribution or treat generated self-confidence as calibrated probability to make it pass validation.

A future chat/classifier adapter should explicitly declare whether it supplies labels, distributions, scores, or calibrated confidence. Policies must review or decline workflows whose required evidence is absent. Provider hosting, model identity/version, question type, and workflow thresholds should remain separate, with evaluation tied to the exact combination.

## Composing a small/large cascade

The decision model chooses or evaluates; a separately configured executor writes or reasons. These recipes return recommendations and do not invoke an executor. An application can compose deterministic eligibility checks, a small-model decision, its selected worker, and a quality/review gate. Evaluate the complete cascade against both a large-model-only and small-model-only baseline on held-out tasks, including fallback cost and end-to-end latency.

The [research record](../research/README.md) also retains fine-tuning and alternate-hosting references as roadmap inspiration. No alternate model or hosting setup is labeled Working without its own receipts.
