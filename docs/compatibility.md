# Provider compatibility contract

This table records the exact endpoint, default model, and environment key used by the checked-in adapters. A caller may override the model with `--model`. The package translates its shared question and answer schema to each provider's native schema and validates the mapped response. See [`IMPLEMENTATION_CONTRACT.md`](../IMPLEMENTATION_CONTRACT.md) for the shared canonical contract.

| CLI provider | Endpoint | Default model | Environment key | Provider documentation |
| --- | --- | --- | --- | --- |
| `jev-openrouter` | `https://openrouter.ai/api/alpha/decisions` | `typesafe/jev-1.13` | `OPENROUTER_API_KEY` | [OpenRouter Decisions API overview](https://openrouter.ai/skills/) |
| `openai-decisions` | `https://api.openai.com/v1/decisions` | `gpt-6-luna` | `OPENAI_API_KEY` | [OpenAI Decisions guide](https://developers.openai.com/api/docs/guides/decisions); [create reference](https://developers.openai.com/api/reference/resources/decisions/methods/create) |
| `sage` | `https://sage.levanto.ai/v1/systemone` | `levanto-sage-v1.3` | `SAGE_API_KEY` | [Sage SystemOne and pricing](https://docs.levanto.ai/systemone#pricing) |

## Canonical mapping

The shared question types are `predicate`, `choice`, and `score`. OpenRouter and Sage represent predicates as `noul`; OpenAI uses `predicate`. Choice options map to keyed criteria for OpenRouter and Sage, and to a `choices` array for OpenAI. Ordered score levels map to criteria lists for OpenRouter and Sage, and to `levels` for OpenAI. All adapters return canonical answers with the resolved model and provider usage when present. Provider-native confidence is retained as a separate field; it is never substituted for predicate probability or choice/score probability.

## Evidence and scope

The generated [compatibility report](../reports/COMPATIBILITY.md) is the source of current implementation results and their statuses. Read its specific receipts and limitations; this contract table alone does not claim that any endpoint or model is currently reachable or that all six workflows have passed live checks. A primitive mapping smoke check exercises only predicate, choice, and score conversion. It does not establish workflow quality, calibrated thresholds, or production readiness.

Pricing varies by provider, model, and plan. The rates snapshot in [`../reports/rates.json`](../reports/rates.json) was checked on 2026-10-08 and carries its source URLs. Check the provider pages directly before budgeting a live run: [OpenRouter Jev model pricing](https://openrouter.ai/typesafe/jev-1.13), [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions), and [Levanto Sage SystemOne pricing](https://docs.levanto.ai/systemone#pricing).
