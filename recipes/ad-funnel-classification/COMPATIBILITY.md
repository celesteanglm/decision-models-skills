# Verified backend compatibility

**Working with:** ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen)

Only Working results receive positive backend labels. Partial means the backend did not meet the frozen acceptance criteria and is not verified for this skill.

| Backend | Qualification | Tested model |
|---|---|---|
| Jev / OpenRouter | Not qualified (Partial) | typesafe/jev-1.13-20260917 |
| Decisions API | Working | gpt-6-luna |
| Sage | Not qualified (Partial) | levanto-sage-v1.3 |

Tested: 2026-10-08. Fixtures: `1a756edddf8002eff2b115dc05cd66217eebd21e8dc9add8734a44b0a18d1280`.
Historical evaluated source: `e6115d0899d71d4c653e88d391ecf5d7f60ce7c94a2657de0dbc0e80abf08674`.

[Immutable live receipt](https://github.com/celesteanglm/decision-models-skills/blob/115b4881a7ea3f7194bc838cd3395d74e94c2c82/reports/community-recipes.json) contains all 12 cases × 3 runs per backend, raw outputs, failures, latency, usage, and costs.

Working describes these frozen synthetic text cases, not production accuracy or calibration. The published catalog retains unchanged decision code, recipe configuration, examples, and fixtures; only inclusion and documentation changed.
