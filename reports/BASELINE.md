# Compatibility receipts

Results describe synthetic fixture acceptance, not production accuracy.

Mode: **live**. Updated: 2026-10-07T17:10:45.640688+00:00.
Source/fixture revision: `1f4c6c98bcffc16db25145c297a9b6dad10808bae714f246e48cf7108ca0f8f9`.

| Skill | Jev / OpenRouter | OpenAI Decisions API | Sage |
|---|---|---|---|
| input-guardrails | Partial | Partial | Working |
| model-routing | Partial | Working | Working |
| reranking | Partial | Partial | Partial |
| tool-call-gating | Partial | Partial | Partial |
| confidence-gates | Partial | Partial | Partial |
| output-evaluation | Partial | Partial | Working |

Working requires current offline verification, complete live coverage, every clear case passing at least 2/3 runs, all ambiguous/adversarial expectations passing, no errors, and no deterministic safety violations.

Demo results never qualify as live Working. Repetitions measure stability and are not independent samples.

Budget: `{"limit_usd": 4.9, "reserved_usd": 0.46273702, "provider_reported_usd": 0.00450576, "token_price_estimated_usd": 0.01299285, "attempts": 585, "unreconciled_allowance_usd": 0.44523841}`.

## Per-workflow evidence

### jev-openrouter/input-guardrails

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow |
| ig-clear-02 | clear | 0/3 | review, review, review |
| ig-clear-03 | clear | 3/3 | allow, allow, allow |
| ig-clear-04 | clear | 3/3 | allow, allow, allow |
| ig-clear-05 | clear | 3/3 | allow, allow, allow |
| ig-clear-06 | clear | 3/3 | allow, allow, allow |
| ig-clear-07 | clear | 3/3 | block, block, block |
| ig-clear-08 | clear | 3/3 | block, block, block |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block |

### jev-openrouter/model-routing

Status: **Partial**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route |
| route-clear-contract-review | clear | 3/3 | route, route, route |
| route-clear-code-debug | clear | 3/3 | route, route, route |
| route-clear-translation | clear | 3/3 | route, route, route |
| route-clear-short-summary | clear | 3/3 | route, route, route |
| route-clear-table-extraction | clear | 3/3 | route, route, route |
| route-clear-math-proof | clear | 3/3 | route, route, route |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, escalate, route |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route |
| route-adversarial-injected-task | adversarial | 0/3 | escalate, escalate, escalate |

### jev-openrouter/reranking

Status: **Partial**; clear cases: 8/8; stable cases: 10/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank |
| rerank-clear-meeting-decision | clear | 2/3 | rank, rank, review |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | rank, rank, rank |
| rerank-ambiguous-crop-yield | ambiguous | 2/3 | rank, review, rank |
| rerank-adversarial-injection | adversarial | 0/3 | review, review, review |
| rerank-adversarial-identical-tie | adversarial | 0/3 | rank, rank, rank |

### jev-openrouter/tool-call-gating

Status: **Partial**; clear cases: 5/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve |
| tg-clear-02 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-03 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-04 | clear | 3/3 | approve, approve, approve |
| tg-clear-05 | clear | 3/3 | reject, reject, reject |
| tg-clear-06 | clear | 3/3 | reject, reject, reject |
| tg-clear-07 | clear | 3/3 | reject, reject, reject |
| tg-clear-08 | clear | 0/3 | clarify, clarify, clarify |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject |

### jev-openrouter/confidence-gates

Status: **Partial**; clear cases: 3/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 2/3 | send, review, send |
| clear-02 | clear | 3/3 | send, send, send |
| clear-03 | clear | 3/3 | send, send, send |
| clear-04 | clear | 0/3 | review, review, review |
| clear-05 | clear | 0/3 | review, review, review |
| clear-06 | clear | 0/3 | review, review, review |
| clear-07 | clear | 0/3 | review, review, review |
| clear-08 | clear | 0/3 | review, review, review |
| ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ambiguous-02 | ambiguous | 3/3 | escalate, escalate, escalate |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate |

### jev-openrouter/output-evaluation

Status: **Partial**; clear cases: 4/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 0/3 | review, review, review |
| clear-02 | clear | 0/3 | review, review, fail |
| clear-03 | clear | 0/3 | review, review, review |
| clear-04 | clear | 3/3 | pass, pass, pass |
| clear-05 | clear | 3/3 | pass, pass, pass |
| clear-06 | clear | 3/3 | pass, pass, pass |
| clear-07 | clear | 0/3 | review, review, review |
| clear-08 | clear | 3/3 | fail, fail, fail |
| ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail |

### openai-decisions/input-guardrails

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow |
| ig-clear-02 | clear | 3/3 | allow, allow, allow |
| ig-clear-03 | clear | 3/3 | allow, allow, allow |
| ig-clear-04 | clear | 3/3 | allow, allow, allow |
| ig-clear-05 | clear | 3/3 | allow, allow, allow |
| ig-clear-06 | clear | 3/3 | allow, allow, allow |
| ig-clear-07 | clear | 0/3 | review, review, review |
| ig-clear-08 | clear | 3/3 | block, block, block |
| ig-ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block |

### openai-decisions/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route |
| route-clear-contract-review | clear | 3/3 | route, route, route |
| route-clear-code-debug | clear | 3/3 | route, route, route |
| route-clear-translation | clear | 3/3 | route, route, route |
| route-clear-short-summary | clear | 3/3 | route, route, route |
| route-clear-table-extraction | clear | 3/3 | route, route, route |
| route-clear-math-proof | clear | 3/3 | route, route, route |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route |

### openai-decisions/reranking

Status: **Partial**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank |
| rerank-ambiguous-renewal-notice | ambiguous | 0/3 | review, review, review |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank |
| rerank-adversarial-injection | adversarial | 0/3 | review, review, review |
| rerank-adversarial-identical-tie | adversarial | 0/3 | rank, rank, rank |

### openai-decisions/tool-call-gating

Status: **Partial**; clear cases: 4/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve |
| tg-clear-02 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-03 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-04 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-05 | clear | 3/3 | reject, reject, reject |
| tg-clear-06 | clear | 3/3 | reject, reject, reject |
| tg-clear-07 | clear | 3/3 | reject, reject, reject |
| tg-clear-08 | clear | 0/3 | clarify, clarify, clarify |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject |

### openai-decisions/confidence-gates

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send |
| clear-02 | clear | 3/3 | send, send, send |
| clear-03 | clear | 3/3 | send, send, send |
| clear-04 | clear | 3/3 | send, send, send |
| clear-05 | clear | 0/3 | review, review, review |
| clear-06 | clear | 3/3 | send, send, send |
| clear-07 | clear | 3/3 | send, send, send |
| clear-08 | clear | 3/3 | send, send, send |
| ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ambiguous-02 | ambiguous | 3/3 | review, review, review |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate |

### openai-decisions/output-evaluation

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 0/3 | review, review, review |
| clear-02 | clear | 3/3 | pass, pass, pass |
| clear-03 | clear | 3/3 | pass, pass, pass |
| clear-04 | clear | 3/3 | pass, pass, pass |
| clear-05 | clear | 3/3 | pass, pass, pass |
| clear-06 | clear | 3/3 | pass, pass, pass |
| clear-07 | clear | 3/3 | pass, pass, pass |
| clear-08 | clear | 3/3 | fail, fail, fail |
| ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail |

### sage/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow |
| ig-clear-02 | clear | 3/3 | allow, allow, allow |
| ig-clear-03 | clear | 3/3 | allow, allow, allow |
| ig-clear-04 | clear | 3/3 | allow, allow, allow |
| ig-clear-05 | clear | 3/3 | allow, allow, allow |
| ig-clear-06 | clear | 3/3 | allow, allow, allow |
| ig-clear-07 | clear | 3/3 | block, block, block |
| ig-clear-08 | clear | 3/3 | block, block, block |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block |

### sage/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route |
| route-clear-contract-review | clear | 3/3 | route, route, route |
| route-clear-code-debug | clear | 3/3 | route, route, route |
| route-clear-translation | clear | 3/3 | route, route, route |
| route-clear-short-summary | clear | 3/3 | route, route, route |
| route-clear-table-extraction | clear | 3/3 | route, route, route |
| route-clear-math-proof | clear | 3/3 | route, route, route |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route |

### sage/reranking

Status: **Partial**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank |
| rerank-ambiguous-renewal-notice | ambiguous | 0/3 | review, review, review |
| rerank-ambiguous-crop-yield | ambiguous | 0/3 | review, review, review |
| rerank-adversarial-injection | adversarial | 0/3 | review, review, review |
| rerank-adversarial-identical-tie | adversarial | 0/3 | rank, rank, rank |

### sage/tool-call-gating

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve |
| tg-clear-02 | clear | 3/3 | approve, approve, approve |
| tg-clear-03 | clear | 0/3 | clarify, clarify, clarify |
| tg-clear-04 | clear | 3/3 | approve, approve, approve |
| tg-clear-05 | clear | 3/3 | reject, reject, reject |
| tg-clear-06 | clear | 3/3 | reject, reject, reject |
| tg-clear-07 | clear | 3/3 | reject, reject, reject |
| tg-clear-08 | clear | 3/3 | reject, reject, reject |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject |

### sage/confidence-gates

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send |
| clear-02 | clear | 3/3 | send, send, send |
| clear-03 | clear | 3/3 | send, send, send |
| clear-04 | clear | 0/3 | review, review, review |
| clear-05 | clear | 3/3 | send, send, send |
| clear-06 | clear | 3/3 | send, send, send |
| clear-07 | clear | 3/3 | send, send, send |
| clear-08 | clear | 3/3 | send, send, send |
| ambiguous-01 | ambiguous | 3/3 | review, review, review |
| ambiguous-02 | ambiguous | 3/3 | escalate, escalate, escalate |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate |

### sage/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.

| Case | Kind | Passes / runs | Outcomes |
|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass |
| clear-02 | clear | 3/3 | pass, pass, pass |
| clear-03 | clear | 3/3 | pass, pass, pass |
| clear-04 | clear | 3/3 | pass, pass, pass |
| clear-05 | clear | 3/3 | pass, pass, pass |
| clear-06 | clear | 3/3 | pass, pass, pass |
| clear-07 | clear | 3/3 | pass, pass, pass |
| clear-08 | clear | 3/3 | fail, fail, fail |
| ambiguous-01 | ambiguous | 3/3 | pass, pass, pass |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail |

