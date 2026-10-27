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

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/releases/download/sage-usecases-2026-10-27/sage-published-live-20261027.json) is retained outside the current source tree. Historical runs remain available at an immutable commit; new runs should use a CI artifact or versioned release asset.

Receipt SHA-256: 1e870cc4c0e1bfc75e94e103f856bde5935fdbb73bd1b20401d189a5a8c361ff.
Fixture revision: 7acd42eaf2318a6d42b2eeea04ff531314ca1077e6da630ad9ff70dfc11e5eb7.
Runtime revision: 65c5f5661fc5be6f5984dc757ea57fe34f600b65c32277fc2cc6ffef6f80aa3b.

## Recorded adapter configuration

The additional reference-helper hashes in compatibility.json bind this result to the evaluated adapter settings. The new Sage checks explicitly selected v1.4 after the deployment rejected the historical v1.3 default. To reproduce an individual Sage case with the optional Python package, pass `--model levanto-sage-v1.4` to `python -m decision_models recipe`. The SKILL.md instructions require no Python package or vendor runtime.
