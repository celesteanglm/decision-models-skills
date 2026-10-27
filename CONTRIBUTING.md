# Contributing a skill

The public skill is its `SKILL.md` instructions and supporting local resources. Keep every skill self-contained under `skills/` so it can be copied or referenced from another project. Do not require a provider, package, script, global command, or repository-root import to use the instructions.

## Write the instructions

Describe when to use the skill, the evidence to gather, the decision procedure, the output, and the review or escalation behavior. Accept inputs naturally as well as through illustrative JSON. Put a use-case skill's complete decision menu in `SKILL.md` so the agent can work without parsing configuration.

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
  --providers jev-openrouter --output reports/demo-general.json
python -m decision_models evaluate-use-cases --repo . --mode demo \
  --providers sage --model levanto-sage-v1.4 --output reports/demo-use-cases.json
python -m decision_models decide --config skills/study-tool-selection/decision.json \
  --provider sage --input skills/study-tool-selection/examples/input.json \
  --model levanto-sage-v1.4 --mode demo \
  --demo-answers skills/study-tool-selection/examples/demo.json
```

Synthetic demo answers cannot qualify a backend; core demo evaluation intentionally exits 1 and reports Not tested. The offline suite includes reference implementation tests and demos from copied JSON inputs; those demos do not execute or benchmark the model-agnostic instructions.

Follow [IMPLEMENTATION_CONTRACT.md](IMPLEMENTATION_CONTRACT.md) and [DECISION_CONTRACT.md](DECISION_CONTRACT.md) when changing the reference code or configuration. Keep native probabilities and confidence separate, credentials in the environment, and runtime behavior independent of expected fixture labels. Freeze fixture expectations before inference and keep failures.

For live reference checks, explicitly choose `--mode live`, configure the provider credential, and supply `--rates /path/to/reviewed-rates.json`. The rates object is keyed by provider flag; each entry needs `source`, `checked_at`, `input_per_million`, and `output_per_million`. Review current pricing before a run. `--budget` reserves an allowance capped at US$5. Run offline verification first; stop on unknown-charge timeouts. Live evaluation is manual and never triggered automatically by a push.

Sage live commands require an explicit `--model`, including evaluation and smoke commands. Use `--providers sage --model levanto-sage-v1.4` for the current text deployment recorded here. A model override selects exactly one provider per run. The bundled v1.3 default remains historical for reproducing archived contracts; live onboarding never selects it implicitly. Selecting v1.4 does not transfer old v1.3 compatibility results or guarantee that every skill passes on v1.4.

## Record what was tested

Each skill keeps COMPATIBILITY.md and compatibility.json beside its instructions. The existing receipts cover the optional Python implementation and exact native models, not the revised instruction-only workflow. Keep that scope explicit. Put provider Working badges on the compatibility page, not in the model-agnostic entrypoint.

No GitHub Release or version tag is needed to install, test, contribute, or record compatibility. Raw runs belong in ignored `reports/`, retained CI artifacts, or a separate Git audit branch. Keep raw reports out of `main`. The `chore/test-evidence` branch retains the newer sanitized receipts; use an exact commit ID in public audit links rather than a moving branch URL. CI artifacts can expire, so retain a permanent copy before removing the only public evidence source.

Preserve exact raw output at a retained evidence URL before recording a compact summary:

```sh
python -m scripts.publish_compatibility \
  --receipt reports/new-live-run.json \
  --ids my-qualified-skill \
  --evidence-url https://github.com/OWNER/REPO/blob/COMMIT/run.json
python scripts/verify.py
```

The publisher targets the unified `skills/` collection. It requires a live receipt for the current checkout, or a scoped receipt whose recorded runtime, helper code, local configuration, examples, and fixtures still match byte-for-byte. Use `--ids` to update only selected qualifying folders; omit it to include all qualifying folders. Failed candidates stay outside the published catalog. It recomputes recorded summaries and does not rewrite `SKILL.md`. A native-API receipt must never qualify instruction-only use. Changes to reference artifacts require fresh evidence for their reference labels.

Publishing metadata changes the aggregate source hash. Verify again before subsequent reference evaluations. `python scripts/verified_catalog.py` checks recorded summaries offline; repeat `--receipt /path/to/downloaded-run.json` to audit them against retained raw evidence and checksums. Offline consistency checks do not fetch remote evidence or invoke models.

For the unified layout migration, `--migration-receipt /path/to/downloaded-audit.json` additionally checks the retained offline audit against the local decision contracts, runtime, helper code, and recorded counts. Historical native labels retain their original dates and require this migration metadata. Future changes to decision behavior need fresh live evidence; a folder move alone can be verified with frozen request/policy contracts and archived-response replay.

## Preserve evidence when changing integration code

The runtime upgrade audit compares the current code with the frozen source snapshot at `0d93d0e10c177e1f0341284de1a1c3cf2745aa46`. Its committed golden contains hashes, not raw provider responses. CI checks all 948 request and policy cases. The full audit also replays four pinned native receipts against both runtimes, keeping 2,598 native responses separate from 246 deterministic outcomes.

Run `python -m scripts.audit_reference_upgrade --help` for the full comparison. Supply `--baseline-root` pointing to a checkout of that commit, all four downloaded receipts in `--receipts`, and a new `--output` path. The audit rejects changed fixtures, image assets, requests, answers, or recommendations. New adapters and stricter errors need their own tests; unchanged historical checks do not qualify them.

Retain the sanitized comparison on the evidence branch, then record its immutable URL:

```sh
python -m scripts.publish_compatibility \
  --upgrade-receipt reports/reference-upgrade-audit.json \
  --upgrade-url https://github.com/OWNER/REPO/blob/COMMIT/reference-upgrade.json
python scripts/verify.py
python scripts/verified_catalog.py --upgrade-receipt reports/reference-upgrade-audit.json
```

This operation appends comparison metadata without changing original test dates, model names, outcomes, or thresholds. It requires complete evidence before writing any summary. Do not regenerate the golden from current output to make a changed behavior pass. A changed decision needs fresh qualification.

## Local working material

`docs/`, `research/`, and `reports/` remain ignored. Essential usage lives in README.md and skill folders; source credits remain in ATTRIBUTION.md and the individual instructions. The ranking and cost-audit scripts are optional local archive helpers, requiring their ignored source snapshots or historical receipts.

For the newer text reference checks, first verify the advertised model at `/v1/models`. The deployment observed on 2026-10-27 accepted `levanto-sage-v1.4` and rejected the historical v1.3 default. Maintainers can reproduce the two new workflows with the evaluated adapter settings:

```sh
python -m scripts.evaluate_usecases --candidates skills \
  --ids study-tool-selection research-enrichment-gate \
  --mode demo --output reports/sage-demo-new.json --historical-bound 0
```

For live mode, review `RATES` against current provider pricing, supply a reconciled cumulative `--historical-bound`, and reserve full coverage under the authorized total budget. The module is optional maintainer tooling; the skills themselves need no package or command. Never use a synthetic demo to qualify a backend.

## Add an image skill

Keep the full visual decision procedure in `SKILL.md`. Use `image.json` with schema version 2 for optional reference evaluation, and keep image assets under `images/`. See [the image configuration contract](DECISION_CONTRACT.md#image-schema-version-2). The catalog records asset hashes alongside fixture and helper hashes. A change to any evaluated asset or decision rule needs fresh evidence.

The bundled image helper calls Sage with native pixels. Other vision models can follow the Markdown instructions through their own integrations, but need separate evaluation before receiving a Working label. The current Sage image Choice response supplies probabilities without separate confidence. Never invent confidence or reuse another backend's threshold.

Run the copied-folder demo described in the README, then evaluate all frozen cases offline:

```sh
python -m scripts.evaluate_images --folder skills/screenshot-action-check \
  --mode demo --output reports/image-demo.json --historical-bound 0
```

For paid evaluation, review `RATES` in `scripts/evaluate_images.py`, set `SAGE_API_KEY`, select `--mode live`, and supply the reconciled cumulative cost bound in `--historical-bound`. The evaluator reserves full coverage within a total capped at US$5. It stops on service errors and unknown-charge timeouts without retrying.

Retain failed development runs before revising a prompt. Freeze each revision before evaluation, keep expected outcomes outside requests, and describe reused development fixtures honestly. If `image.json` includes `evaluation_notes`, publication also requires `--history-receipt` and `--history-url`. The history must identify the final receipt and unchanged fixture revision. Retain the history at an immutable evidence URL before publishing the skill.
