# Recorded reference implementation results

These runs tested the optional Python reference implementation against native decision APIs. They did not evaluate the model-agnostic SKILL.md instructions on an agent's current model. No listed provider, Python package, or CLI is required to use the skill.

**Reference implementation — Working with:** ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

| Backend | Result | Tested model | Passed checks |
|---|---|---|---|
| Jev / OpenRouter | Not qualified (Partial) | typesafe/jev-1.13-20260917 | 33/36 |
| Decisions API | Not qualified (Partial) | gpt-6-luna | 33/36 |
| Sage | Working | levanto-sage-v1.3 | 36/36 |

**Sage availability:** this v1.3 result is historical. On 2026-10-27 the live deployment advertised v1.4 and rejected v1.3. The recorded result does not qualify v1.4; use an explicitly evaluated version and configuration.

Tested: 2026-10-08T11:24:50.801230+00:00. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.

Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.

## Failures and unsupported backends

- **Jev / OpenRouter (Partial):** clear-05: 2/3 passed (action, choice); clear-06: 1/3 passed (action, choice)
- **Decisions API (Partial):** instruction-injection: 0/3 passed (action, choice)

## Evidence

[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/blob/7b0e764a4e15d43be4e252365780b2393fdfa7f6/community-use-cases.json) is retained outside the main source tree for optional audit. Receipts can live at an immutable Git commit or a retained CI artifact; GitHub Releases are not required. Using the skill and running offline checks do not download this receipt.

Receipt SHA-256: d06ec4e5406bd0d41be45941bda0105e19088a8189aace936f32f68761793af1.
Fixture revision: f78663b8ad43bc4819648d0d5b9a3c2bc0e1e2264dfa2cd5e331a50e87f587da.
Runtime revision: 90c3e703d2a656d7aed3087ef4a4f07b130f1c03de7de8af4d72265eaeb823bb.

## Layout verification

The live results above predate the unified skills directory. An offline check of 936 provider-request and demo-policy contracts, plus 2,808 replays of archived native responses, confirmed identical requests, permissions, numerical gates, and recommendations after the path and naming changes. This migration made no paid requests and is not a new live evaluation.

[Migration audit](https://github.com/celesteanglm/decision-models-skills/blob/7b0e764a4e15d43be4e252365780b2393fdfa7f6/unified-layout-audit.json) (SHA-256: 69a859f7e0af3cd74011e50e4c806ec74f983458ed1c32fb978b3c8ef1a4fecc) preserves the verification record and original runtime revision.
