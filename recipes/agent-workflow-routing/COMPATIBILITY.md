# Backend compatibility

**Working with:** ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

| Backend | Result | Tested model | Passed checks |
|---|---|---|---|
| Jev / OpenRouter | Working | typesafe/jev-1.13-20260917 | 36/36 |
| Decisions API | Working | gpt-6-luna | 36/36 |
| Sage | Working | levanto-sage-v1.3 | 36/36 |

Tested: 2026-10-08T11:24:50.801230+00:00. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.

Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.

## Failures and unsupported backends

All recorded checks passed on the listed backends.

## Evidence

[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/blob/115b4881a7ea3f7194bc838cd3395d74e94c2c82/reports/community-recipes.json) is retained outside the current source tree. Historical runs remain available at an immutable commit; new runs should use a CI artifact or versioned release asset.

Receipt SHA-256: d06ec4e5406bd0d41be45941bda0105e19088a8189aace936f32f68761793af1.
Fixture revision: d9b79e3fd39efaded0b6853780b905c605e167cac55bec73426e5411caad831b.
Runtime revision: 65c5f5661fc5be6f5984dc757ea57fe34f600b65c32277fc2cc6ffef6f80aa3b.
