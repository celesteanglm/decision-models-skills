# Evaluation history

These runs are diagnostic iterations on a synthetic development fixture suite. The fixtures and prompts were refined after observed failures, so the results are useful for tracking these iterations but do not generalize to production workloads. Repeated calls to the same cases measure consistency; they are not independent samples. None of the statuses below establishes production accuracy or calibrated thresholds.

## Baseline

The baseline exposed failures across all three providers. Clear examples sometimes received review or the wrong action, ambiguous and adversarial cases were inconsistent, and exact duplicate passages were not reliably handled. See [`BASELINE.md`](../reports/BASELINE.md) and its [`receipt`](../reports/baseline.json).

## V2

V2 made fixture evidence self-contained and strengthened field references, action scope, and historical context. Exact duplicate content shares one provider score and a stable input-order tie break. This improved several provider/workflow results, while reranking and confidence gates still had failures for Jev. The run summary was Jev: four workflows Working; OpenAI: model routing, reranking, and tool-call gating Working; Sage: all six Working. See [`V2.md`](../reports/V2.md), the [`V2 receipt`](../reports/v2.json), and the [`V2 fixture snapshot`](../reports/v2-fixtures.json).

## V3

V3 added scoped reranking profiles for requested `top_k` values 1 and 2, with clearer confidence cases tied to specific source records. Numeric thresholds remained unchanged. The duplicate-tie oracle now accepts review or the two requested items in stable input order; it previously required all three items. The V3 report marks all six Jev workflows Working, four OpenAI workflows Working (input guardrails and output evaluation remain Partial), and all six Sage workflows Working. These results apply to the tested reranking profiles; the default full-ranking confidence remains unchanged, and other configurations are not certified. Exact duplicate scoring establishes content identity and stable ordering, rather than general duplicate discrimination. See [`V3.md`](../reports/V3.md), the [`V3 receipt`](../reports/v3.json), and the [`V3 fixture snapshot`](../reports/v3-fixtures.json).

## V4

V4 changes transport handling: sanitize abrupt disconnect errors and stop a backend after a failure with unknown charge status. Its preflight records that fixtures, prompts, and thresholds are identical to V3. The completed final run again marks all six Jev workflows Working, four OpenAI workflows Working, and all six Sage workflows Working. There were zero service errors and zero deterministic safety-boundary violations. OpenAI input guardrails and output evaluation remain Partial. See the [V4 live receipt](../reports/v4.json); the compatibility table now shows the latest core regression. See the [`V4 preflight`](../reports/v4-preflight.json) and [`V4 fixture snapshot`](../reports/v4-fixtures.json).

## Neutral fixture revision

A later documentation cleanup replaced synthetic place and timezone identifiers with neutral examples, including UTC meeting times. The same text substitutions were applied to historical fixture snapshots. Historical receipts retain their original source and fixture digests, so those digests do not describe the edited snapshots. Their model outputs remain unchanged. The current fixtures are frozen separately and receive fresh acceptance evidence; thresholds, expected outcomes, and workflow code are unchanged.

The refreshed neutral-fixture run marks all six Jev and Sage workflows Working and four OpenAI workflows Working. OpenAI input guardrails and output evaluation remain Partial. There were zero service errors and zero deterministic safety-boundary violations. See the [neutral-fixture live receipt](../reports/live.json) and [neutral preflight](../reports/neutral-preflight.json). The previous final run remains in [V4.json](../reports/v4.json).

## Fresh Jev/OpenRouter and Sage rerun

An additional real-API run used the unchanged current fixtures: 12 cases per skill, three repetitions per backend. It made 390 HTTP calls and performed 42 deterministic checks. Both backends qualify as Working for all six workflows. Jev passed 215/216 expectations (one clear confidence-gate case passed 2/3); Sage passed 216/216. Stable recommendations occurred in 70/72 Jev cases and 72/72 Sage cases. No service errors or deterministic safety-boundary violations occurred. See the [fresh report](../reports/JEV_SAGE_RETEST.md), [raw receipt](../reports/jev-sage-retest.json), and [preflight](../reports/retest-preflight.json).

## Community recipes and current core regression

The dated research contribution adds 29 independently authored text decision recipes from 26 ranked original posts. An independent Luna review assessed all 348 cases without expected labels; corrections and narrowly safe ambiguous alternatives were frozen before paid dispatch. This is model-assisted fixture review, not human gold labels. No expected label, threshold, prompt, or decision runtime changed after live dispatch. See the [review record](../research/fixture-review.json) and [preflight](../reports/community-preflight.json).

All 29 recipes ran 12 cases three times per backend: 3,132 evaluations, including 2,871 paid HTTP requests and 261 deterministic permission checks. Jev has 7 Working and 22 Partial recipes; Decisions has 8 Working and 21 Partial; Sage has 13 Working and 16 Partial. Recommendation stability was 339/348 cases for Jev and 348/348 for both Decisions and Sage. Stability includes consistent failures; it is separate from correctness. No service errors or deterministic safety violations occurred. All Partial outcomes remain visible in the [compatibility report](../reports/community-recipes.md), [raw receipt](../reports/community-recipes.json), and [summary](../reports/community-summary.json).

A fresh regression of the six original workflows on the same source revision performed 648 evaluations and 585 HTTP requests. All six Jev and Sage workflows remain Working; Decisions input guardrails and output evaluation remain Partial, with its other four workflows Working. The [current core table](../reports/COMPATIBILITY.md) now points to [that exact receipt](../reports/community-core-regression.json). The approved Jev publication gate passes.

Clean non-editable wheel installations on Python 3.10.13 and 3.12.10 each passed 107 tests and 105 copied-folder demos without credentials or repository-root imports. The two new live runs cost approximately US$0.083 in reported and token-estimated amounts. Across all retained iterations, the reconciled total is US$0.206 and the conservative reserved allowance is US$4.537, below US$5; see [cost reconciliation](../reports/costs.json). Estimates are not invoices.

## Publication qualification correction

The initial candidate publication included recipes that were Partial on every backend. The published catalog now excludes those 11 installable recipe folders and retains 18 recipes with at least one Working backend. Positive badges are derived only from Working results, both in the catalog and each copied skill. Each folder includes a compatibility page naming the exact tested models and unqualified backends. The raw candidate receipts remain immutable historical audit evidence, not a supported-use-case catalog.

No decision code, recipe JSON, examples, thresholds, or fixtures changed. All 110 retained evaluated artifacts were checked byte-for-byte against publication commit `115b4881a7ea3f7194bc838cd3395d74e94c2c82`. Pruning changes the aggregate source hash, so qualification is verified using immutable receipt hashes and the scoped artifact manifest in [catalog.json](../reports/catalog.json), rather than relabeling historical receipts as fresh runs. No additional paid calls were made. [The verified catalog](../reports/VERIFIED_CATALOG.md) is the current publication record.
