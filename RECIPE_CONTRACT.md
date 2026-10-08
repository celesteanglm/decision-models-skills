# Optional recipe reference configuration

Use-case skills are self-contained SKILL.md instructions. They can be followed with the agent's current model or a user-selected model tool, without a package, executable, or JSON configuration. Put the full decision menu, inputs, procedure, result, and review behavior in the entrypoint.

`recipe.json` describes the frozen native-API decision and numerical policy exercised by the optional Python reference implementation. It is not required to use the Markdown skill, and its thresholds do not apply automatically to arbitrary agent models. The schemas below are reference-runtime contracts.

Maintainers can exercise a copied reference configuration with the optional installed Python package:

```sh
python -m decision_models recipe --recipe /path/to/copied/recipe.json --provider sage --input /path/to/copied/examples/input.json --demo-answers /path/to/copied/examples/demo.json --mode demo
```

Live reference mode uses `--mode live` without synthetic answers and environment-only credentials. See [CONTRIBUTING.md](CONTRIBUTING.md). A valid typed output is not proof of correctness, and native confidence is distinct from probabilities.

## Frozen schema version 1

`recipe.json` is trusted configuration containing:

* `schema_version: 1`, `id` matching its folder, `title`, `description` (original concise prose), `source_urls` (verified original post links), `inspiration` (original concise explanation of adaptation), `limitations` (what this text decision does not demonstrate), and `related_skills` (existing six workflow names).
* `required_state_fields`: nonempty list of required top-level state fields. Prefer just `content` with a realistic document or transcript; additional contextual fields are allowed. Missing/empty evidence yields review before inference.
* `question`: canonical choice question with `name: decision`, `kind: choice`, original `instructions`, and `options` mapping 2-6 labels to descriptions, including mandatory `review`. Instructions treat state as evidence, ignore attempts to override policy, and choose review for genuinely missing or ambiguous evidence. Keep instructions and descriptions concise (ideally total under 150 words).
* `policy`: `confidence_threshold: 0.65`, `probability_threshold: 0.65`, `review_choice: review`. Freeze these before live tests; provider/model overrides are not silently calibrated by these synthetic fixtures.

Input is `{"state": {"content": "realistic evidence ..."}, "permission_granted": true}`. Permission must be explicitly Boolean true; false returns `action: deny`, no call. Missing permission also denies. State contents cannot grant permission. Missing required state fields returns `action: review`, no call.

An answered, valid choice with sufficient native confidence AND selected-option probability produces `action: recommend`, `choice: <label>`. A selected review label, missing/low confidence, low probability, refusal, or missing evidence returns `action: review`, `choice: review`. `executed_action` always false. Protocol failures are explicit errors. Raw provider response and native usage are retained by the runner.

`examples/demo.json` contains `{"decision": {"kind": "choice", "status": "answered", "choice": "<label>", "probabilities": {"<every supplied label>": 0.0}, "confidence": 0.95}}`. Provide a valid distribution with the correct label .97 and remaining .03 split evenly. Label as hand-authored demo, not model output.

Fixtures are a list of exactly 12 cases: eight clear, two ambiguous, two adversarial. Each has `id`, `category`, `input`, `expected` (`actions` plus `choice` when exact), and `demo_answers` matching example answer shape. Write eight genuinely different domain examples across all substantive labels; ambiguous cases lack decisive semantic evidence but include required fields (expect review). Adversarial cases: one permission=false with compelling content (expect deny; no provider call), one state instruction injection appended to clear domain evidence (expect correct substantive label, never execution). `forbidden_actions` may include recommend for permission-denied cases. Expected labels and fixture metadata never enter requests.

All docs use portable paths and impersonal synthetic examples. No code or source prose is copied. Fixtures must not embed literal expected labels as answers to be repeated by the model. This contract is owned by the consolidating agent.

Independent fixture review may establish a narrowly allowed list of safe ambiguous outcomes before live evaluation. Use `expected.choices` with explicit labels and `expected.actions`, rather than a single `choice`, for alternatives such as review or a recommendation to request missing details. Never allow unrelated substantive choices merely to make an ambiguous fixture pass. The frozen oracle is independent of provider outputs; it is not adjusted after live evaluation.

## Recorded reference labels

Qualify a reference backend only when it meets the frozen Working criteria. Show positive Working badges on the local compatibility page only for those backends; Partial, Blocked, and Not tested do not qualify. Each copied folder must include `COMPATIBILITY.md` and `compatibility.json` with exact tested models, pass counts, failure reasons, tested runtime/configuration/fixture hashes, and a link and checksum for retained raw evidence. `scripts/verified_catalog.py` checks local summaries, labels, inclusion, and unchanged evaluated artifacts offline; its optional `--receipt` audits a downloaded raw run. Raw test runs belong in ignored local output or CI artifacts, rather than the source tree. Adapter availability and a successful reference demo do not establish instruction-only model compatibility. Keep the reference scope explicit in compatibility.json; never transfer its labels to the agent using SKILL.md.
