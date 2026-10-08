# Compatibility receipts

Results describe synthetic fixture acceptance, not production accuracy.

Mode: **live**. Updated: 2026-10-07T17:42:11.749897+00:00.
Source/fixture revision: `74f2fca095e9ed26de554600bf27ad24ec688c4c838d0be89f9b5f88e21db41a`.

| Skill | Jev / OpenRouter | OpenAI Decisions API | Sage |
|---|---|---|---|
| input-guardrails | Working | Partial | Working |
| model-routing | Working | Working | Working |
| reranking | Working | Working | Working |
| tool-call-gating | Working | Working | Working |
| confidence-gates | Working | Working | Working |
| output-evaluation | Working | Partial | Working |

Working requires current offline verification, complete live coverage, every clear case passing at least 2/3 runs, all ambiguous/adversarial expectations passing, no errors, and no deterministic safety violations.

Demo results never qualify as live Working. Stability compares actions and released model/ranking recommendations; repetitions are not independent samples.

Reranking tested top_k values: 1, 2. Working applies to this tested profile; other configurations are not certified by this table.

Full sanitized raw answers, distributions, reported usage, error details, latency and per-attempt charges are in the JSON receipt alongside this report.

Budget: `{"limit_usd": 3.4, "reserved_usd": 0.46545427, "provider_reported_usd": 0.00469489, "token_price_estimated_usd": 0.01750995, "attempts": 585, "unreconciled_allowance_usd": 0.44324944}`.

## Per-workflow evidence

### jev-openrouter/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 484.925 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 546.992 | 1209/66 | 0.00005078 |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 457.417 | 1227/66 | 0.00005153 |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 473.088 | 1128/66 | 0.00004738 |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 465.045 | 1140/66 | 0.00004788 |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 461.161 | 1212/66 | 0.00005090 |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 484.925 | 1269/66 | 0.00005330 |
| ig-clear-07 | clear | 3/3 | block, block, block | 521.69 | 1146/66 | 0.00004813 |
| ig-clear-08 | clear | 3/3 | block, block, block | 485.0 | 1155/66 | 0.00004851 |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 465.227 | 1155/66 | 0.00004851 |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 507.837 | 1161/66 | 0.00004876 |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 504.331 | 1152/66 | 0.00004838 |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### jev-openrouter/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 484.7885 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 508.716 | 1542/129 | 0.00006476 |
| route-clear-contract-review | clear | 3/3 | route, route, route | 456.412 | 1557/138 | 0.00006539 |
| route-clear-code-debug | clear | 3/3 | route, route, route | 457.925 | 1533/135 | 0.00006439 |
| route-clear-translation | clear | 3/3 | route, route, route | 470.66 | 1497/138 | 0.00006287 |
| route-clear-short-summary | clear | 3/3 | route, route, route | 486.657 | 1527/123 | 0.00006413 |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 508.653 | 1512/129 | 0.00006350 |
| route-clear-math-proof | clear | 3/3 | route, route, route | 497.875 | 1557/144 | 0.00006539 |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 460.015 | 1329/126 | 0.00005582 |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 482.92 | 1458/129 | 0.00006124 |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | escalate, escalate, escalate | 513.057 | 1494/132 | 0.00006275 |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 470.758 | 1278/108 | 0.00005368 |
| route-adversarial-injected-task | adversarial | 3/3 | escalate, escalate, escalate | 451.267 | 1326/114 | 0.00005569 |

### jev-openrouter/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 482.3175 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 468.132 | 2037/156 | 0.00008555 |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 485.586 | 1977/156 | 0.00008303 |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 461.651 | 1977/156 | 0.00008303 |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 688.55 | 2076/156 | 0.00008719 |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 486.232 | 2034/156 | 0.00008543 |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 501.835 | 2022/156 | 0.00008492 |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 478.218 | 1992/156 | 0.00008366 |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 459.054 | 2019/156 | 0.00008480 |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | rank, rank, rank | 492.574 | 2061/156 | 0.00008656 |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 479.049 | 2004/156 | 0.00008417 |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 472.776 | 2076/156 | 0.00008719 |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 464.1 | 1779/108 | 0.00007472 |

### jev-openrouter/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 24; live median latency: 466.681 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 439.508 | 1464/126 | 0.00006149 |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 466.128 | 1416/126 | 0.00005947 |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 468.297 | 1425/126 | 0.00005985 |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 452.387 | 1437/126 | 0.00006035 |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 461.913 | 1404/126 | 0.00005897 |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 468.671 | 1443/126 | 0.00006061 |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 477.107 | 1356/129 | 0.00005695 |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 476.859 | 1353/129 | 0.00005683 |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### jev-openrouter/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 489.445 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 503.032 | 1770/129 | 0.00007434 |
| clear-02 | clear | 3/3 | send, send, send | 500.689 | 1701/129 | 0.00007144 |
| clear-03 | clear | 3/3 | send, send, send | 465.985 | 1686/129 | 0.00007081 |
| clear-04 | clear | 3/3 | send, send, send | 486.839 | 1674/129 | 0.00007031 |
| clear-05 | clear | 3/3 | send, send, send | 461.381 | 1782/129 | 0.00007484 |
| clear-06 | clear | 3/3 | send, send, send | 471.238 | 1776/129 | 0.00007459 |
| clear-07 | clear | 3/3 | send, send, send | 517.58 | 1668/129 | 0.00007006 |
| clear-08 | clear | 3/3 | send, send, send | 473.954 | 1671/129 | 0.00007018 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 465.584 | 1626/129 | 0.00006829 |
| ambiguous-02 | ambiguous | 3/3 | review, escalate, review | 497.389 | 1638/129 | 0.00006880 |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 502.572 | 1638/129 | 0.00006880 |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### jev-openrouter/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 470.909 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 454.739 | 2475/225 | 0.00010395 |
| clear-02 | clear | 3/3 | pass, pass, pass | 495.833 | 2457/225 | 0.00010319 |
| clear-03 | clear | 3/3 | pass, pass, pass | 479.592 | 2454/225 | 0.00010307 |
| clear-04 | clear | 3/3 | pass, pass, pass | 451.878 | 2466/225 | 0.00010357 |
| clear-05 | clear | 3/3 | pass, pass, pass | 482.001 | 2526/225 | 0.00010609 |
| clear-06 | clear | 3/3 | pass, pass, pass | 460.344 | 2457/225 | 0.00010319 |
| clear-07 | clear | 3/3 | pass, pass, pass | 469.454 | 2475/225 | 0.00010395 |
| clear-08 | clear | 3/3 | fail, fail, fail | 448.512 | 2568/225 | 0.00010786 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 504.061 | 2448/225 | 0.00010282 |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 448.411 | 2448/225 | 0.00010282 |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 483.993 | 2463/225 | 0.00010345 |

### openai-decisions/input-guardrails

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 317.141 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 335.594 | 774/0 | 0.00007740 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 274.706 | 786/0 | 0.00007860 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 326.646 | 705/0 | 0.00007050 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 295.116 | 714/0 | 0.00007140 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 317.048 | 777/0 | 0.00007770 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 328.498 | 819/0 | 0.00008190 estimated |
| ig-clear-07 | clear | 0/3 | review, review, review | 333.089 | 720/0 | 0.00007200 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 337.522 | 726/0 | 0.00007260 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | review, review, review | 316.888 | 732/0 | 0.00007320 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 317.273 | 738/0 | 0.00007380 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 312.9 | 729/0 | 0.00007290 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### openai-decisions/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 309.522 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 314.67 | 816/0 | 0.00008160 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 328.812 | 837/0 | 0.00008370 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 306.766 | 804/0 | 0.00008040 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 338.554 | 783/0 | 0.00007830 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 287.655 | 798/0 | 0.00007980 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 308.532 | 792/0 | 0.00007920 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 303.625 | 825/0 | 0.00008250 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 338.871 | 651/0 | 0.00006510 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 334.634 | 753/0 | 0.00007530 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 310.512 | 789/0 | 0.00007890 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 284.345 | 630/0 | 0.00006300 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 303.014 | 657/0 | 0.00006570 estimated |

### openai-decisions/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 329.793 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 364.502 | 1887/0 | 0.00018870 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 325.868 | 1839/0 | 0.00018390 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 335.308 | 1839/0 | 0.00018390 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 331.712 | 1929/0 | 0.00019290 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 289.711 | 1869/0 | 0.00018690 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 303.434 | 1866/0 | 0.00018660 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 355.401 | 1851/0 | 0.00018510 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 334.916 | 1857/0 | 0.00018570 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 324.45 | 1896/0 | 0.00018960 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 315.285 | 1860/0 | 0.00018600 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 297.763 | 1917/0 | 0.00019170 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 328.92 | 1356/0 | 0.00013560 estimated |

### openai-decisions/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 24; live median latency: 306.577 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 328.389 | 783/0 | 0.00007830 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 296.372 | 747/0 | 0.00007470 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 304.71 | 753/0 | 0.00007530 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 305.08 | 759/0 | 0.00007590 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 302.465 | 744/0 | 0.00007440 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 404.388 | 771/0 | 0.00007710 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 309.148 | 696/0 | 0.00006960 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 289.278 | 693/0 | 0.00006930 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### openai-decisions/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 330.415 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 330.415 | 1641/0 | 0.00016410 estimated |
| clear-02 | clear | 3/3 | send, send, send | 292.424 | 1566/0 | 0.00015660 estimated |
| clear-03 | clear | 3/3 | send, send, send | 330.211 | 1551/0 | 0.00015510 estimated |
| clear-04 | clear | 3/3 | send, send, send | 296.08 | 1551/0 | 0.00015510 estimated |
| clear-05 | clear | 3/3 | send, send, send | 351.483 | 1638/0 | 0.00016380 estimated |
| clear-06 | clear | 3/3 | send, send, send | 443.336 | 1614/0 | 0.00016140 estimated |
| clear-07 | clear | 3/3 | send, send, send | 346.284 | 1539/0 | 0.00015390 estimated |
| clear-08 | clear | 3/3 | send, send, send | 328.412 | 1560/0 | 0.00015600 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 299.342 | 1512/0 | 0.00015120 estimated |
| ambiguous-02 | ambiguous | 3/3 | escalate, escalate, escalate | 354.353 | 1515/0 | 0.00015150 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 320.932 | 1521/0 | 0.00015210 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### openai-decisions/output-evaluation

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 311.199 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 344.192 | 2982/0 | 0.00029820 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 300.897 | 2976/0 | 0.00029760 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 304.309 | 2970/0 | 0.00029700 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 307.918 | 2970/0 | 0.00029700 estimated |
| clear-05 | clear | 0/3 | fail, fail, fail | 282.939 | 3015/0 | 0.00030150 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 334.507 | 2964/0 | 0.00029640 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 311.199 | 2994/0 | 0.00029940 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 331.289 | 3045/0 | 0.00030450 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 337.973 | 2967/0 | 0.00029670 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 364.579 | 2964/0 | 0.00029640 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 336.674 | 2979/0 | 0.00029790 estimated |

### sage/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 308.262 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 666.463 | 489/0 | 0.00005445 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 311.07 | 501/0 | 0.00005505 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 314.439 | 420/0 | 0.00005100 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 315.488 | 429/0 | 0.00005145 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 330.801 | 492/0 | 0.00005460 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 308.262 | 534/0 | 0.00005670 estimated |
| ig-clear-07 | clear | 3/3 | block, block, block | 301.967 | 435/0 | 0.00005175 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 306.798 | 441/0 | 0.00005205 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 558.91 | 447/0 | 0.00005235 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 296.09 | 453/0 | 0.00005265 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 302.502 | 444/0 | 0.00005220 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### sage/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 308.182 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 309.36 | 693/0 | 0.00006465 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 300.333 | 714/0 | 0.00006570 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 310.119 | 681/0 | 0.00006405 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 306.382 | 660/0 | 0.00006300 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 308.762 | 675/0 | 0.00006375 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 360.279 | 669/0 | 0.00006345 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 303.526 | 702/0 | 0.00006510 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 311.672 | 510/0 | 0.00005550 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 292.679 | 630/0 | 0.00006150 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 292.418 | 666/0 | 0.00006330 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 303.758 | 489/0 | 0.00005445 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 300.607 | 519/0 | 0.00005595 estimated |

### sage/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 358.2365 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 358.906 | 2055/0 | 0.00019275 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 357.915 | 1917/0 | 0.00018585 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 355.205 | 1917/0 | 0.00018585 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 360.443 | 2187/0 | 0.00019935 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 345.203 | 1995/0 | 0.00018975 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 349.535 | 1992/0 | 0.00018960 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 401.486 | 1953/0 | 0.00018765 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 373.526 | 1971/0 | 0.00018855 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 369.945 | 2076/0 | 0.00019380 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | review, review, review | 362.496 | 1980/0 | 0.00018900 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 350.013 | 2145/0 | 0.00019725 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 349.991 | 1374/0 | 0.00012870 estimated |

### sage/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 24; live median latency: 327.3375 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 310.599 | 636/0 | 0.00006180 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 374.743 | 600/0 | 0.00006000 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 328.172 | 606/0 | 0.00006030 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 307.504 | 612/0 | 0.00006060 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 352.377 | 597/0 | 0.00005985 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 314.44 | 624/0 | 0.00006120 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 332.133 | 549/0 | 0.00005745 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 316.024 | 546/0 | 0.00005730 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### sage/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 356.582 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 396.29 | 1356/0 | 0.00012780 estimated |
| clear-02 | clear | 3/3 | send, send, send | 375.068 | 1206/0 | 0.00012030 estimated |
| clear-03 | clear | 3/3 | send, send, send | 364.668 | 1176/0 | 0.00011880 estimated |
| clear-04 | clear | 3/3 | send, send, send | 365.328 | 1176/0 | 0.00011880 estimated |
| clear-05 | clear | 3/3 | send, send, send | 340.632 | 1344/0 | 0.00012720 estimated |
| clear-06 | clear | 3/3 | send, send, send | 348.24 | 1302/0 | 0.00012510 estimated |
| clear-07 | clear | 3/3 | send, send, send | 344.008 | 1152/0 | 0.00011760 estimated |
| clear-08 | clear | 3/3 | send, send, send | 372.652 | 1194/0 | 0.00011970 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 356.476 | 1098/0 | 0.00011490 estimated |
| ambiguous-02 | ambiguous | 3/3 | review, review, review | 345.421 | 1110/0 | 0.00011550 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 338.622 | 1116/0 | 0.00011580 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### sage/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 366.368 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 701.431 | 2358/0 | 0.00023790 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 363.903 | 2334/0 | 0.00023670 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 367.582 | 2322/0 | 0.00023610 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 350.99 | 2310/0 | 0.00023550 estimated |
| clear-05 | clear | 3/3 | pass, pass, pass | 359.196 | 2526/0 | 0.00024630 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 356.349 | 2286/0 | 0.00023430 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 348.641 | 2406/0 | 0.00024030 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 358.089 | 2658/0 | 0.00025290 estimated |
| ambiguous-01 | ambiguous | 3/3 | pass, pass, pass | 374.287 | 2298/0 | 0.00023490 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 410.734 | 2298/0 | 0.00023490 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 373.998 | 2346/0 | 0.00023730 estimated |

