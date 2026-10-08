# Contributing a skill

Core skills in `skills/` and use-case skills in `recipes/` share the same agent skill format. Keep each folder usable when copied into another project with the shared CLI installed separately.

## Add or change a use case

1. Define a bounded text decision and evidence the calling application can provide. Follow the [recipe contract](RECIPE_CONTRACT.md). Add local SKILL.md, recipe.json, examples, and 12 fixtures: eight clear, two ambiguous, two adversarial.
2. Credit the exact original source in the skill and configuration. State whether it inspired the idea or supplied adapted material. Preserve required notices for copied material; a public post alone is not a reuse license.
3. Define expected behavior before inference, have a reviewer assess the evidence without seeing expected labels, then freeze the oracle and thresholds. Never tune expected labels to make a backend pass.
4. Run `python scripts/verify.py`. This checks installed CLI behavior, copied folders, unit tests, and compatibility consistency without credentials.
5. Run live acceptance with reviewed rates and a new output path. Keep failed outcomes as well as successes. Retain raw output in ignored `reports/`, CI artifacts, or a versioned release asset.
6. Publish `compatibility.json` and `COMPATIBILITY.md` beside each skill. Include positive badges only for Working backends. At least one backend must qualify before a skill is published.

Changes to the six core workflows must follow [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md). Preserve Python 3.10+, the standard-library-only runtime, separate probability/confidence signals, and environment-only credentials. Each compatibility summary binds results to the exact runtime, configuration, examples, and fixtures. A change to those artifacts requires new evidence; a successful demo is not live acceptance.

## Run evaluations

Raw runs are generated output. Do not commit them. Run offline verification before live evaluation; it writes the current packaging receipt into ignored `reports/offline.json`.

```sh
python scripts/verify.py
decision-models evaluate --repo . --mode demo \
  --providers jev-openrouter --output reports/demo-core.json
decision-models evaluate-recipes --repo . --mode demo \
  --providers sage --output reports/demo-recipes.json
```

Core demo evaluation intentionally exits 1 and labels compatibility Not tested because synthetic answers cannot qualify a backend. Use a new output path for every recipe evaluation.

For live mode, explicitly select `--mode live`, configure the provider credential, and supply `--rates /path/to/reviewed-rates.json`. The rates file is an object keyed by provider flag; each provider entry must contain `source` (provider pricing URL), `checked_at` (review timestamp), and nonnegative numeric `input_per_million` and `output_per_million` USD rates. Populate these from current provider pricing before a run. `--budget` is a reserved allowance, capped at US$5. Stop on unknown-charge timeouts.

The manual live GitHub workflow accepts the reviewed rates JSON as an input and uploads raw results as artifacts. Live evaluation is never triggered automatically by a push. Retain release evidence as versioned release assets when it must outlive CI artifact retention.

## Publish compatibility results

First retain the exact raw live receipt at the evidence URL. Then generate summaries for the affected category from that receipt:

```sh
python -m scripts.publish_compatibility \
  --kind recipes --receipt reports/new-live-run.json \
  --evidence-url https://github.com/OWNER/REPO/releases/download/TAG/run.json
python scripts/verify.py
python scripts/check_release.py
```

Use `--kind skills` for core workflows. The publisher requires a live receipt for the current checkout and matching frozen fixtures; it recomputes summaries from the recorded rows. A receipt with only one tested provider leaves other providers Not tested. Evaluate and publish each category before starting the next: publishing metadata changes the aggregate source hash, so subsequent runs need a fresh offline verification receipt.

`python scripts/verified_catalog.py` checks local summaries offline. Add repeatable `--receipt /path/to/downloaded-run.json` arguments to audit them against retained raw evidence and its checksum. Offline consistency checks do not fetch the remote evidence or re-run model inference.

## Extend a provider

Adapters export `endpoint`, `key_env`, `default_model`, `build_payload(state, questions, model)`, and `parse_response(raw, questions)`; see [the implementation contract](IMPLEMENTATION_CONTRACT.md) and [native adapters](src/decision_models/providers/). The Python `execute_recipe` runner accepts a trusted application-owned `adapter=` and injectable `transport=`. The CLI uses its three named native adapters; `--model` does not convert an arbitrary chat model into a decision model.

Preserve resolved model identity, native usage, raw responses, distributions, refusals, and native confidence. Do not invent probabilities or confidence for unsupported output capabilities. New adapters require independent golden contract tests and fresh live acceptance; existing labels do not transfer.

## Local working material

`docs/`, `research/`, and `reports/` are ignored and absent from a fresh checkout. Essential usage lives in README.md and individual skill folders; original source credits remain in ATTRIBUTION.md and each use-case skill. `scripts/rank_sources.py` and `scripts/audit_costs.py` are optional local archive helpers and require their ignored source snapshots or historical receipts. They are not prerequisites for installing, running, or verifying published skills.
