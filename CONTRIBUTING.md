# Contributing

Contributions should keep the six standalone skill folders usable when copied into another project and should preserve the provider-neutral response contract.

Before proposing a change:

1. Read `IMPLEMENTATION_CONTRACT.md` and the affected skill's `SKILL.md`.
2. Keep expected labels and policy outcomes out of model input.
3. Document policy changes, thresholds, provider wire changes, and attribution in the relevant docs.
4. Include source and license notices when material is copied or adapted; do not imply that inspiration alone is code reuse.
5. Use offline hand-authored demo answers for examples. Label them synthetic and do not present them as provider results.

The package targets Python 3.10+ and uses only the standard library at runtime. Provider credentials must remain in environment variables and must never be committed. Live evaluations can make paid requests; document the provider, model, budget, rates source, and evidence when reporting them. The default evaluation budget is US$5 total, and three repetitions of 12 cases per skill are not independent statistical samples.

Changes to compatibility claims should point to the exact endpoint and model used, the timestamped receipt or other evidence, and the scope of what was exercised. A successful API smoke check does not establish that every workflow is compatible or that a threshold is calibrated.
