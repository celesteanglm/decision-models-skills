# Evaluation history

These runs are diagnostic iterations on a synthetic development fixture suite. The fixtures and prompts were refined after observed failures, so the results are useful for tracking these iterations but do not generalize to production workloads. Repeated calls to the same cases measure consistency; they are not independent samples. None of the statuses below establishes production accuracy or calibrated thresholds.

## Baseline

The baseline exposed failures across all three providers. Clear examples sometimes received review or the wrong action, ambiguous and adversarial cases were inconsistent, and exact duplicate passages were not reliably handled. See [`BASELINE.md`](../reports/BASELINE.md) and its [`receipt`](../reports/baseline.json).

## V2

V2 made fixture evidence self-contained and strengthened field references, action scope, and historical context. Exact duplicate content shares one provider score and a stable input-order tie break. This improved several provider/workflow results, while reranking and confidence gates still had failures for Jev. The run summary was Jev: four workflows Working; OpenAI: model routing, reranking, and tool-call gating Working; Sage: all six Working. See [`V2.md`](../reports/V2.md), the [`V2 receipt`](../reports/v2.json), and the [`V2 fixture snapshot`](../reports/v2-fixtures.json).

## V3

V3 added scoped reranking profiles for requested `top_k` values 1 and 2, with clearer confidence cases tied to specific source records. Numeric thresholds remained unchanged. The duplicate-tie oracle now accepts review or the two requested items in stable input order; it previously required all three items. The V3 report marks all six Jev workflows Working, four OpenAI workflows Working (input guardrails and output evaluation remain Partial), and all six Sage workflows Working. These results apply to the tested reranking profiles; the default full-ranking confidence remains unchanged, and other configurations are not certified. Exact duplicate scoring establishes content identity and stable ordering, rather than general duplicate discrimination. See [`V3.md`](../reports/V3.md), the [`V3 receipt`](../reports/v3.json), and the [`V3 fixture snapshot`](../reports/v3-fixtures.json).

## V4

V4 changes transport handling: sanitize abrupt disconnect errors and stop a backend after a failure with unknown charge status. Its preflight records that fixtures, prompts, and thresholds are identical to V3. The completed final run again marks all six Jev workflows Working, four OpenAI workflows Working, and all six Sage workflows Working. There were zero service errors and zero deterministic safety-boundary violations. OpenAI input guardrails and output evaluation remain Partial. See the [final report](../reports/COMPATIBILITY.md) and [live receipt](../reports/live.json). See the [`V4 preflight`](../reports/v4-preflight.json) and [`V4 fixture snapshot`](../reports/v4-fixtures.json).

## Neutral fixture revision

A later documentation cleanup replaced synthetic place and timezone identifiers with neutral examples, including UTC meeting times. The same text substitutions were applied to historical fixture snapshots. Historical receipts retain their original source and fixture digests, so those digests do not describe the edited snapshots. Their model outputs remain unchanged. The current fixtures are frozen separately and receive fresh acceptance evidence; thresholds, expected outcomes, and workflow code are unchanged.

The refreshed neutral-fixture run marks all six Jev and Sage workflows Working and four OpenAI workflows Working. OpenAI input guardrails and output evaluation remain Partial. There were zero service errors and zero deterministic safety-boundary violations. See the [current live receipt](../reports/live.json) and [neutral preflight](../reports/neutral-preflight.json). The previous final run remains in [V4.json](../reports/v4.json).

## Fresh Jev/OpenRouter and Sage rerun

An additional real-API run used the unchanged current fixtures: 12 cases per skill, three repetitions per backend. It made 390 HTTP calls and performed 42 deterministic checks. Both backends qualify as Working for all six workflows. Jev passed 215/216 expectations (one clear confidence-gate case passed 2/3); Sage passed 216/216. Stable recommendations occurred in 70/72 Jev cases and 72/72 Sage cases. No service errors or deterministic safety-boundary violations occurred. See the [fresh report](../reports/JEV_SAGE_RETEST.md), [raw receipt](../reports/jev-sage-retest.json), and [preflight](../reports/retest-preflight.json).
