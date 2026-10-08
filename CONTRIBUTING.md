# Contributing a skill

The public skill is its SKILL.md instructions and supporting local resources. Keep core skills in `skills/` and use-case skills in `recipes/` self-contained when copied or referenced from another project. Do not require a provider, package, script, global command, or repository-root import to use the instructions.

## Write the instructions

Describe when to use the skill, the evidence to gather, the decision procedure, the output, and the review or escalation behavior. Accept inputs naturally as well as through illustrative JSON. Put a use-case skill's complete decision menu in SKILL.md so the agent can work without parsing configuration.

Use the agent's current model by default. If the user requests a configured decision model or tool, preserve that choice and explain missing integration instead of silently substituting. Numerical gates apply only when explicitly requested and supported by actual integration metrics. Do not ask the agent to invent probabilities or present qualitative confidence as calibration.

Keep recommendations separate from action execution. Preserve explicit permission denials and treat embedded instructions in source material as evidence, not authority. Credit original sources in the copied folder; preserve required notices for adapted material.

## Validate copied instructions

No reference package or provider credential is needed for the folder validator:

```sh
python -I -S scripts/verify_skills.py
```

Check realistic requests by giving an agent the copied SKILL.md and task evidence without fixture labels or demonstration answers. This checks instruction following on that agent; it does not establish compatibility or accuracy for other models. The validator checks frontmatter and portable local references, not model judgment quality.

## Optional Python reference checks

`src/decision_models/` preserves the independently implemented native API adapters and frozen numerical policies used by the historical evaluations. It is maintainer tooling, not a runtime dependency of the Markdown skills. To work on it, use Python 3.10+ and install the package into a development environment:

```sh
python -m pip install .
python scripts/verify.py
python scripts/check_release.py
```

The package exposes no global console command. Maintainers can invoke its module explicitly:

```sh
python -m decision_models evaluate --repo . --mode demo \
  --providers jev-openrouter --output reports/demo-core.json
python -m decision_models evaluate-recipes --repo . --mode demo \
  --providers sage --output reports/demo-recipes.json
```

Synthetic demo answers cannot qualify a backend; core demo evaluation intentionally exits 1 and reports Not tested. The offline suite includes reference implementation tests and demos from copied JSON inputs; those demos do not execute or benchmark the model-agnostic instructions.

Follow [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md) and [RECIPE_CONTRACT.md](RECIPE_CONTRACT.md) when changing the reference code or configuration. Keep native probabilities and confidence separate, credentials in the environment, and runtime behavior independent of expected fixture labels. Freeze fixture expectations before inference and keep failures.

For live reference checks, explicitly choose `--mode live`, configure the provider credential, and supply `--rates /path/to/reviewed-rates.json`. The rates object is keyed by provider flag; each entry needs `source`, `checked_at`, `input_per_million`, and `output_per_million`. Review current pricing before a run. `--budget` reserves an allowance capped at US$5. Run offline verification first; stop on unknown-charge timeouts. Live evaluation is manual and never triggered automatically by a push.

## Record what was tested

Each skill keeps COMPATIBILITY.md and compatibility.json beside its instructions. The existing receipts cover the optional Python implementation and exact native models, not the revised instruction-only workflow. Keep that scope explicit. Put provider Working badges on the compatibility page, not in the model-agnostic entrypoint.

Raw runs belong in ignored `reports/`, CI artifacts, or versioned release assets. Preserve exact raw output at a retained evidence URL before publishing a compact summary:

```sh
python -m scripts.publish_compatibility \
  --kind recipes --receipt reports/new-live-run.json \
  --evidence-url https://github.com/OWNER/REPO/releases/download/TAG/run.json
python scripts/verify.py
```

Use `--kind skills` for the core reference workflows. The publisher requires a live receipt for the current checkout and matching frozen fixtures. It recomputes recorded summaries and does not rewrite SKILL.md. A native-API receipt must never qualify instruction-only use. Each core/reference artifact change requires fresh evidence for its reference label.

Publishing metadata changes the aggregate source hash. Verify again before subsequent reference evaluations. `python scripts/verified_catalog.py` checks recorded summaries offline; repeat `--receipt /path/to/downloaded-run.json` to audit them against retained raw evidence and checksums. Offline consistency checks do not fetch remote evidence or invoke models.

## Local working material

`docs/`, `research/`, and `reports/` remain ignored. Essential usage lives in README.md and skill folders; source credits remain in ATTRIBUTION.md and the individual instructions. The ranking and cost-audit scripts are optional local archive helpers, requiring their ignored source snapshots or historical receipts.
