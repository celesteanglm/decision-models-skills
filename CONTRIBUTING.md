# Contributing a skill

The public skill is its `SKILL.md` instructions and supporting local resources. Keep every skill self-contained under `skills/` so it can be copied or referenced from another project. Do not require a provider, package, script, global command, or repository-root import to use the instructions.

The root `SKILL.md` is the collection's routing entrypoint. It reads `skills/catalog.json`, opens a relevant skill and its evidence page, and follows that skill. Keep model and backend qualification claims in the individual compatibility records.

## Write the instructions

Describe when to use the skill, the evidence to gather, the decision procedure, the output, and the review or escalation behavior. Accept inputs naturally as well as through illustrative JSON. Put a use-case skill's complete decision menu in `SKILL.md` so the agent can work without parsing configuration.

Use the agent's current model by default. If the user requests a configured decision model or tool, preserve that choice and explain missing integration instead of silently substituting. Numerical gates apply only when explicitly requested and supported by actual integration metrics. Do not ask the agent to invent probabilities or present qualitative confidence as calibration.

Keep recommendations separate from action execution. Preserve explicit permission denials and treat embedded instructions in source material as evidence, not authority. Credit original sources in the copied folder; preserve required notices for adapted material.

After adding a skill or changing its frontmatter description, regenerate the router's small index with `python scripts/skill_catalog.py --write`. CI rejects a stale index. Router behavior is checked separately from native backend qualification; an instruction-routing check must not create a Working label for the router or a new model.

[Retained router development checks](https://github.com/celesteanglm/decision-models-skills/blob/9deb5b6d8b32430f53c4db7f03858cb9496d1fe2/router-instruction-checks-20261028.json) record the requests, two instruction revisions, outcomes, and one ambiguous route-label variance. These reused synthetic cases are not a held-out benchmark. The final revision matched all 12 outcome categories and 11 exact route IDs; two additional setup checks preserved the requested backend and qualification constraints.

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

Follow the [adapter interface](#add-a-model-adapter) and [reference schemas](#reference-configuration) below when changing the reference code or configuration. Keep native probabilities and confidence separate, credentials in the environment, and runtime behavior independent of expected fixture labels. Freeze fixture expectations before inference and keep failures.

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

`docs/`, `research/`, and `reports/` remain ignored. Essential usage lives in README.md and skill folders; source credits remain in the [README credits](README.md#credits-and-license) and the individual instructions. The ranking and cost-audit scripts are optional local archive helpers, requiring their ignored source snapshots or historical receipts.

For the newer text reference checks, first verify the advertised model at `/v1/models`. The deployment observed on 2026-10-27 accepted `levanto-sage-v1.4` and rejected the historical v1.3 default. Maintainers can reproduce the two new workflows with the evaluated adapter settings:

```sh
python -m scripts.evaluate_usecases --candidates skills \
  --ids study-tool-selection research-enrichment-gate \
  --mode demo --output reports/sage-demo-new.json --historical-bound 0
```

For live mode, review `RATES` against current provider pricing, supply a reconciled cumulative `--historical-bound`, and reserve full coverage under the authorized total budget. The module is optional maintainer tooling; the skills themselves need no package or command. Never use a synthetic demo to qualify a backend.

## Add an image skill

Keep the full visual decision procedure in `SKILL.md`. Use `image.json` with schema version 2 for optional reference evaluation, and keep image assets under `images/`. See [the image configuration contract](#image-schema-version-2). The catalog records asset hashes alongside fixture and helper hashes. A change to any evaluated asset or decision rule needs fresh evidence.

The bundled image helper calls Sage with native pixels. Other vision models can follow the Markdown instructions through their own integrations, but need separate evaluation before receiving a Working label. The current Sage image Choice response supplies probabilities without separate confidence. Never invent confidence or reuse another backend's threshold.

Run the copied-folder demo described in the README, then evaluate all frozen cases offline:

```sh
python -m scripts.evaluate_images --folder skills/screenshot-action-check \
  --mode demo --output reports/image-demo.json --historical-bound 0
```

For paid evaluation, review `RATES` in `scripts/evaluate_images.py`, set `SAGE_API_KEY`, select `--mode live`, and supply the reconciled cumulative cost bound in `--historical-bound`. The evaluator reserves full coverage within a total capped at US$5. It stops on service errors and unknown-charge timeouts without retrying.

Retain failed development runs before revising a prompt. Freeze each revision before evaluation, keep expected outcomes outside requests, and describe reused development fixtures honestly. If `image.json` includes `evaluation_notes`, publication also requires `--history-receipt` and `--history-url`. The history must identify the final receipt and unchanged fixture revision. Retain the history at an immutable evidence URL before publishing the skill.

## Add a model adapter

Start with the [runnable custom-provider example](examples/custom_provider/README.md). It works from a copied folder with the optional installed Python package. External adapters do not require a provider registry entry or changes to a skill. The interface below applies to the optional Python implementation, not direct use of `SKILL.md`.

### Provider modules

Each `providers/<name>.py` exports `Adapter` with class attributes `name`, `endpoint`, `key_env`, `default_model`; methods `build_payload(state, questions, model)` and `parse_response(raw, questions)`.

Canonical questions are dictionaries: `{name, kind, instructions}` where kind is `predicate`, `choice` (plus `options: {string: description}`), or `score` (plus `levels: [description]`). Predicate can have `criteria: {true: description, false: description}`. All identifiers/options are strings, ordering is stable.

Canonical response: `{model: resolved model string, answers: {name: answer}, usage: native usage or null, raw_response: raw}`. Answer: `{kind, status: "answered"}` plus `probability_true` for predicate, `choice`/`probabilities`/optional native `confidence` for choice, `score`/`probabilities`/optional native `confidence`/optional `legend` for score. Score probability keys are zero-based index strings. Refusal: `{kind: original kind, status: "refusal"}`. Do not invent confidence or cost. Return `validate_response(response, questions)` from shared contracts. Raise `DecisionError("invalid_response", safe message)` for malformed native responses. No network/auth logic in adapters.

### Workflow modules

Each `workflows/<underscore_name>.py` exports `build(data)` returning `{state, questions, early_result}`. `early_result` is null or a final policy outcome requiring no inference. `decide(data, response)` returns a JSON-compatible policy result. Include `action` as a string and stable `reasons` list. Each workflow owns its input validation, fixed documented thresholds, and policy. Never execute side effects. Catch refusals/missing required confidence with review outcomes. Threshold overrides, if supported, must be validated (0..1 finite values); defaults are separate per provider via data `_provider` set by runtime. Do not put labels or demo answers in state. JSON input files contain only application inputs.

All skills include standalone `SKILL.md`, `examples/input.json`, `examples/demo.json`, and `fixtures/acceptance.json`. Demo JSON contains canonical `answers` ONLY; runtime provides synthetic model and validates them. Each acceptance fixture: `{id, category: clear|ambiguous|adversarial, input: application inputs, expected: {actions: [...], ...}, demo_answers: canonical answer map}`. Exactly 8 clear, 2 ambiguous, 2 adversarial per skill. Expectations remain outside model inputs. Reranking can add `expected.top_id`; evaluator can add `expected.metric_ranges`. Every fixture must independently define expected behavior/rationale. Maintainers may revise fixture design before freezing. Skill names/slugs: input-guardrails, model-routing, reranking, tool-call-gating, confidence-gates, output-evaluation.

Maintainer example: `python -m decision_models decide --config skills/<id>/decision.json`. Install the optional reference package for this maintainer command. Users can install or reference the Markdown skill folders independently; they do not require this package or a global console command.

### Image reference adapter

`scripts/image_reference.py` implements the separate [image schema version 2](#image-schema-version-2). Its Sage adapter uses `/decide/batch` with `content.kind: image`, a local image encoded as a data URI, and optional caption text. Canonical predicate, choice, and score questions map to native YesNo, Choice, and Scale questions. The public batch endpoint selects the model. The adapter checks the resolved model against `levanto-sage-v1.4` and rejects drift.

The adapter preserves raw answers, native usage, distributions, and fractional scores. Image Choice has native probabilities but no separate confidence. The policy uses selected-option probability and leaves confidence unavailable. An abstention produces review. Malformed responses and unsupported backends produce explicit errors.

Permission checks precede file reads and inference. Images must be PNG, JPEG, or WebP within the configured asset root, at most 4 MiB decoded, with a maximum edge of 8192 pixels and at most 4096 squared pixels. Remote URLs and paths escaping the root are rejected. Neither captions nor image text can grant permission. Recommendations never execute actions.

The standalone helper imports only the optional installed reference package. It can run from another working directory with a copied skill folder. The Markdown instructions themselves need only an agent that can inspect images. Sage is the bundled native image adapter. Another backend can supply `adapter=` without editing the runner, using its own wire mapping and the same local-image checks. Its compatibility label still requires independent qualification.

### Third-party text adapter and runnable example

[`examples/custom_provider/`](examples/custom_provider/README.md) is the complete offline example for a fictional fourth text backend. It maps canonical state/questions in `build_payload`, maps the provider-shaped answer in `parse_response`, and calls `execute_use_case` with the adapter injected. Its transport accepts only an `offline://` endpoint and returns synthetic fixtures. The runner's response-parsing path receives a temporary test sentinel rather than a real credential. The example needs no API access or repository-root imports. Copy the example and a complete skill folder, install this package in your application environment, then follow its README command from any working directory.

For your own text integration, implement the same adapter surface (`name`, `endpoint`, `key_env`, `default_model`, `build_payload`, and `parse_response`). Map every field explicitly. Preserve the raw provider response and native usage; copy native probabilities and confidence only when supplied. If a required native metric is absent, leave it absent so the skill's policy can route to review. Do not infer calibrated confidence, probabilities, or cost from free-form text. A malformed answer should raise `DecisionError("invalid_response", safe_message)`.

Call `execute_use_case(..., adapter=your_adapter, transport=your_transport)` in your own application. The runtime reads the credential named by `key_env` from the process environment and passes it to the transport. A custom transport can support SDKs or non-Bearer authentication. Keep transport and authentication code in your application; the copied skill folder remains independent. Use an explicit model ID. A call to a real provider can be billable. Inspect the offline mapping and confirm an authorized budget before making one. The example transport cannot select a live service.

The generic `execute(..., adapter=..., policy=...)` runtime seam follows the same boundary for general workflows. A custom confidence-gates provider needs trusted policy with `send` and `escalate_below`; a custom output-evaluation provider needs `grounded`, `relevant`, `helpfulness`, and `fail_below`. Image integrations use `execute_image(..., adapter=..., model=...)` and must preserve the same local pixel-content restrictions and canonical response validation. These seams permit an application-specific integration; the fictional example does not qualify a provider, add one to the built-in catalog, or provide an image backend.

## Reference configuration

Use these schemas when maintaining `decision.json`, `image.json`, and the frozen evaluation fixtures. The Markdown instructions remain self-contained and need no JSON configuration or package.

<details>
<summary>Text and image schemas, fixture rules, and evidence requirements</summary>

### Frozen schema version 1

`decision.json` is trusted configuration containing:

* `schema_version: 1`, `id` matching its folder, `title`, `description` (original concise prose), `source_urls` (verified original post links), `inspiration` (original concise explanation of adaptation), `limitations` (what this text decision does not demonstrate), and `related_skills` (existing six workflow names).
* `required_state_fields`: nonempty list of required top-level state fields. Prefer just `content` with a realistic document or transcript; additional contextual fields are allowed. Missing/empty evidence yields review before inference.
* `question`: canonical choice question with `name: decision`, `kind: choice`, original `instructions`, and `options` mapping 2-6 labels to descriptions, including mandatory `review`. Instructions treat state as evidence, ignore attempts to override policy, and choose review for genuinely missing or ambiguous evidence. Keep instructions and descriptions concise (ideally total under 150 words).
* `policy`: `confidence_threshold: 0.65`, `probability_threshold: 0.65`, `review_choice: review`. Freeze these before live tests; provider/model overrides are not silently calibrated by these synthetic fixtures.

Input is `{"state": {"content": "realistic evidence ..."}, "permission_granted": true}`. Permission must be explicitly Boolean true; false returns `action: deny`, no call. Missing permission also denies. State contents cannot grant permission. Missing required state fields returns `action: review`, no call.

An answered, valid choice with sufficient native confidence AND selected-option probability produces `action: recommend`, `choice: <label>`. A selected review label, missing/low confidence, low probability, refusal, or missing evidence returns `action: review`, `choice: review`. `executed_action` always false. Protocol failures are explicit errors. Raw provider response and native usage are retained by the runner.

`examples/demo.json` contains `{"decision": {"kind": "choice", "status": "answered", "choice": "<label>", "probabilities": {"<every supplied label>": 0.0}, "confidence": 0.95}}`. Provide a valid distribution with the correct label .97 and remaining .03 split evenly. Label as hand-authored demo, not model output.

Fixtures are a list of exactly 12 cases: eight clear, two ambiguous, two adversarial. Each has `id`, `category`, `input`, `expected` (`actions` plus `choice` when exact), and `demo_answers` matching example answer shape. Write eight genuinely different domain examples across all substantive labels; ambiguous cases lack decisive semantic evidence but include required fields (expect review). Adversarial cases: one permission=false with compelling content (expect deny; no provider call), one state instruction injection appended to clear domain evidence (expect correct substantive label, never execution). `forbidden_actions` may include recommend for permission-denied cases. Expected labels and fixture metadata never enter requests.

All docs use portable paths and impersonal synthetic examples. No code or source prose is copied. Fixtures must not embed literal expected labels as answers to be repeated by the model.

Independent fixture review may establish a narrowly allowed list of safe ambiguous outcomes before live evaluation. Use `expected.choices` with explicit labels and `expected.actions`, rather than a single `choice`, for alternatives such as review or a recommendation to request missing details. Never allow unrelated substantive choices merely to make an ambiguous fixture pass. The frozen oracle is independent of provider outputs; it is not adjusted after live evaluation.

### Recorded reference labels

Image-specific configuration is described below. Text schema version 1 and its recorded policies remain unchanged.

Qualify a reference backend only when it meets the frozen Working criteria. Show positive Working badges on the local compatibility page only for those backends; Partial, Blocked, and Not tested do not qualify. Each copied folder must include `COMPATIBILITY.md` and `compatibility.json` with exact tested models, pass counts, failure reasons, tested runtime/configuration/fixture hashes, and a link and checksum for retained raw evidence. `scripts/verified_catalog.py` checks local summaries, labels, inclusion, and unchanged evaluated artifacts offline; its optional `--receipt` audits a downloaded raw run. Raw test runs belong in ignored local output or CI artifacts, rather than the source tree. Adapter availability and a successful reference demo do not establish instruction-only model compatibility. Keep the reference scope explicit in compatibility.json; never transfer its labels to the agent using SKILL.md.

### Image schema version 2

`image.json` uses `schema_version: 2` and `input_modality: image`. It is separate from `decision.json` so text-only integrations cannot silently treat a filename as visual evidence. It contains the same attribution and canonical choice fields, required state fields `content` and `image`, and a policy with `probability_threshold` and mandatory `review_choice: review`. The image helper accepts up to 20 choices, including review.

Image input is `{"state": {"content": "Inspect the CONTINUE button.", "image": "images/frame01.png"}, "permission_granted": true}`. Paths resolve under the copied skill folder unless the caller supplies an explicit asset root. Expected labels, case IDs, filenames, and demonstration answers never enter the provider request. Only image pixels and task text enter native content.

The screenshot reference freezes the selected-option probability threshold at 0.80. Its Sage image response has no separate confidence metric. The policy returns review for a selected review choice, insufficient probability, refusal, or missing evidence. Permission denial returns deny before file access. The result always has `executed_action: false`.

Use the same 12-case, three-repetition qualification rules as text skills. Record actual live image formats separately from offline format handling. Hash local image assets in the compatibility manifest. If prompt revisions reuse the evaluation fixtures, record the development history and disclose that these are development results rather than held-out accuracy estimates.

</details>
