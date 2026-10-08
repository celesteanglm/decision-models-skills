# Portable community recipes

Recipes are independently authored, text-only demonstrations of a bounded decision from a credited community use case. They recommend a label; they never connect accounts, execute tools, send messages, move files, or call a generative executor. A demo of the decision is not a reproduction or benchmark of the source application.

Each `recipes/<id>/` contains `SKILL.md`, `recipe.json`, `examples/input.json`, `examples/demo.json`, and `fixtures/acceptance.json`. The separately installed CLI runs copied folders from any directory:

```sh
decision-models recipe --recipe /path/to/copied/recipe.json --provider sage --input /path/to/copied/examples/input.json --demo-answers /path/to/copied/examples/demo.json --mode demo
```

Live mode uses the same command with `--mode live` and without `--demo-answers`. Credentials are environment-only. Native provider selection and optional `--model` are separate from the portable recipe. Native confidence and probabilities remain distinct; typed output is not proof of correctness. Other small models need a compatible adapter and fresh model-specific evaluation.

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
