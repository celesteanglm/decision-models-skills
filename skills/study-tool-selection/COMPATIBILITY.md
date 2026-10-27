# Recorded reference implementation results

These runs tested the optional Python reference implementation against native decision APIs. They did not evaluate the model-agnostic SKILL.md instructions on an agent's current model. No listed provider, Python package, or CLI is required to use the skill.

**Reference implementation — Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

| Backend | Result | Tested model | Passed checks |
|---|---|---|---|
| Jev / OpenRouter | Working | typesafe/jev-1.13-20260917 | 36/36 |
| Decisions API | Not qualified (Partial) | gpt-6-luna | 30/36 |
| Sage | Working | levanto-sage-v1.4 | 36/36 |

Tested: 2026-10-27T01:56:26.794735+00:00. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.

Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.

## Failures and unsupported backends

- **Decisions API (Partial):** clear-01: 0/3 passed (action, choice); clear-07: 0/3 passed (action, choice)

## Evidence

[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/blob/7b0e764a4e15d43be4e252365780b2393fdfa7f6/sage-published-live-20261027.json) is retained outside the main source tree for optional audit. Receipts can live at an immutable Git commit or a retained CI artifact; GitHub Releases are not required. Using the skill and running offline checks do not download this receipt.

Receipt SHA-256: 1e870cc4c0e1bfc75e94e103f856bde5935fdbb73bd1b20401d189a5a8c361ff.
Fixture revision: 7acd42eaf2318a6d42b2eeea04ff531314ca1077e6da630ad9ff70dfc11e5eb7.
Runtime revision: 90c3e703d2a656d7aed3087ef4a4f07b130f1c03de7de8af4d72265eaeb823bb.

## Recorded adapter configuration

The additional reference-helper hashes in compatibility.json bind this result to the evaluated adapter settings. The new Sage checks explicitly selected v1.4 after the deployment rejected the historical v1.3 default. To reproduce an individual Sage case with the optional Python package, pass `--model levanto-sage-v1.4` to `python -m decision_models decide --config decision.json`. The SKILL.md instructions require no Python package or vendor runtime.

## Layout verification

The live results above predate the unified skills directory. An offline check of 936 provider-request and demo-policy contracts, plus 2,808 replays of archived native responses, confirmed identical requests, permissions, numerical gates, and recommendations after the path and naming changes. This migration made no paid requests and is not a new live evaluation.

[Migration audit](https://github.com/celesteanglm/decision-models-skills/blob/7b0e764a4e15d43be4e252365780b2393fdfa7f6/unified-layout-audit.json) (SHA-256: 69a859f7e0af3cd74011e50e4c806ec74f983458ed1c32fb978b3c8ef1a4fecc) preserves the verification record and original runtime revision.

## Integration update

The current runners add external adapters and structured error handling. An offline comparison against the recorded source snapshot matched 948 request and policy contracts, 2,598 archived native responses, and 246 deterministic outcomes. The original models, test dates, fixtures, and thresholds above remain unchanged. This comparison made no provider calls and does not qualify a different model or an external adapter.

[Runtime comparison audit](https://github.com/celesteanglm/decision-models-skills/blob/8164fd03d33cca9f1f8f645a1a92b96b7cfafa83/reference-upgrade-20261028.json) (SHA-256: 72c938b2555b8898659fbdab9692598e05d5c58afde9700d18e0a2f8b8a2f1bd).
