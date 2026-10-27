# Recorded reference implementation results

These runs tested the optional Python reference implementation against native decision APIs. They did not evaluate the model-agnostic SKILL.md instructions on an agent's current model. No listed provider, Python package, or CLI is required to use the skill.

**Reference implementation — Working with:** ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

| Backend | Result | Tested model | Passed checks |
|---|---|---|---|
| Jev / OpenRouter | Not tested | Not tested | 0/0 |
| Decisions API | Not tested | Not tested | 0/0 |
| Sage | Working | levanto-sage-v1.4 | 36/36 |

Tested: 2026-10-27T16:01:23.862367+00:00. Twelve frozen cases (eight clear, two ambiguous, two adversarial), three repetitions per backend. Counts include deterministic permission/evidence checks; they are not all API calls.

Working requires complete coverage, a majority pass on every clear case, all ambiguous/adversarial checks passing, no service errors or permission violations, offline verification, and live model outputs. Partial did not meet that gate; Blocked could not obtain live outputs; Not tested has no results. These synthetic cases do not establish production accuracy or calibrated thresholds.

## Failures and unsupported backends

- **Jev / OpenRouter (Not tested):** No evaluation results are recorded for this backend.
- **Decisions API (Not tested):** No evaluation results are recorded for this backend.

## Evidence

[Machine-readable summary](compatibility.json) records case counts, failure reasons, exact models, and hashes of the tested runtime, local configuration, examples, and fixtures.

[Raw live test run](https://github.com/celesteanglm/decision-models-skills/blob/2fc0dc92de0c6aae0ea87818b749440cf4824677/sage-images-live-20261027-r3.json) is retained outside the main source tree for optional audit. Receipts can live at an immutable Git commit or a retained CI artifact; GitHub Releases are not required. Using the skill and running offline checks do not download this receipt.

Receipt SHA-256: adacc280bda50bc089442168ca2960fdae9af05366effa463b8084c8ea8ab63f.
Fixture revision: 61af95b4b73b95c0ecda982d20e4341e03d8cae826c1c6b5415c10a6c601d68e.
Runtime revision: 90c3e703d2a656d7aed3087ef4a4f07b130f1c03de7de8af4d72265eaeb823bb.

## Image reference scope

This run sent actual local PNG pixels to Sage's public image API. JPEG and WebP input handling has offline contract coverage; those formats were not qualified by this live run. Other backends have no image results here and receive no Working label.

This image Choice API reports native selected-option probability without a separate confidence value. The frozen workflow uses a probability threshold of 0.80 and records confidence as unavailable. It recommends visibility only; it does not test enabled state, clickability, or application behavior.

The optional image runner reads image.json. The text runner rejects that schema rather than sending an image filename as text. No Python package or command is needed to follow the SKILL.md instructions with a vision-capable agent.

## Development runs

Three development wordings used the same frozen fixtures and 0.80 threshold. Preliminary runs failed clipped-button or washed-out-preview checks and are retained. These reused development cases are not a held-out production benchmark.

[Earlier results and frozen prompt revisions](https://github.com/celesteanglm/decision-models-skills/blob/2fc0dc92de0c6aae0ea87818b749440cf4824677/image-evaluation-history.json) (SHA-256: 8db35dfe7b45597270520e30e3c27a2dc84fbbaad5f7832963323a291c64e41b). The first two runs were Partial; only the final configuration qualifies as Working.
