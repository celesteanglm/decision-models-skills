# Verified backend compatibility

**Working with:** ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen)

Only Working results receive positive backend labels. Partial means the backend did not meet the frozen acceptance criteria and is not verified for this skill.

| Backend | Qualification | Tested model |
|---|---|---|
| Jev / OpenRouter | Not qualified (Partial) | typesafe/jev-1.13-20260917 |
| Decisions API | Not qualified (Partial) | gpt-6-luna |
| Sage | Working | levanto-sage-v1.3 |

Tested: 2026-10-08. Fixtures: `b446a2ba0066f9f3ccca56787e2ad07a94ae2e3e1bf36621b676fd303127d49f`.
Historical evaluated source: `e6115d0899d71d4c653e88d391ecf5d7f60ce7c94a2657de0dbc0e80abf08674`.

[Immutable live receipt](https://github.com/celesteanglm/decision-models-skills/blob/115b4881a7ea3f7194bc838cd3395d74e94c2c82/reports/community-recipes.json) contains all 12 cases × 3 runs per backend, raw outputs, failures, latency, usage, and costs.

Working describes these frozen synthetic text cases, not production accuracy or calibration. The published catalog retains unchanged decision code, recipe configuration, examples, and fixtures; only inclusion and documentation changed.
