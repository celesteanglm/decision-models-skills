# Backend compatibility

**Working with:** ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen)

| Backend | Result | Tested model | Passed checks |
|---|---|---|---|
| Jev / OpenRouter | Not qualified (Partial) | typesafe/jev-1.13-20260917 | 21/36 |
| Decisions API | Working | gpt-6-luna | 36/36 |
| Sage | Not qualified (Partial) | levanto-sage-v1.3 | 33/36 |

Tested: 2026-10-08T11:24:50.801230+00:00. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.

Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.

## Failures and unsupported backends

- **Jev / OpenRouter (Partial):** clear-01: 0/3 passed (action, choice); clear-03: 0/3 passed (action, choice); clear-04: 0/3 passed (action, choice); clear-07: 0/3 passed (action, choice); instruction-injection: 0/3 passed (action, choice)
- **Sage (Partial):** clear-03: 0/3 passed (action, choice)

## Evidence

[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/blob/115b4881a7ea3f7194bc838cd3395d74e94c2c82/reports/community-recipes.json) is retained outside the current source tree. Historical runs remain available at an immutable commit; new runs should use a CI artifact or versioned release asset.

Receipt SHA-256: d06ec4e5406bd0d41be45941bda0105e19088a8189aace936f32f68761793af1.
Fixture revision: 98a28d2faa562eee093af18e376fadd5ffd66dd2e4b81feb006de499da6fe8dc.
Runtime revision: 65c5f5661fc5be6f5984dc757ea57fe34f600b65c32277fc2cc6ffef6f80aa3b.
