# Compatibility receipts

Results describe synthetic fixture acceptance, not production accuracy.

Evidence: [current core regression JSON](community-core-regression.json).

Mode: **live**. Updated: 2026-10-08T11:20:54.775708+00:00.
Source/fixture revision: `e6115d0899d71d4c653e88d391ecf5d7f60ce7c94a2657de0dbc0e80abf08674`.

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

Budget: `{"limit_usd": 0.5, "reserved_usd": 0.46542022, "provider_reported_usd": 0.00469262, "token_price_estimated_usd": 0.01750485, "attempts": 585, "unreconciled_allowance_usd": 0.44322275}`.

## Per-workflow evidence

### jev-openrouter/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 478.78 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 562.166 | 1209/66 | 0.00005078 |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 471.396 | 1227/66 | 0.00005153 |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 453.681 | 1128/66 | 0.00004738 |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 498.506 | 1140/66 | 0.00004788 |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 491.96 | 1212/66 | 0.00005090 |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 486.975 | 1269/66 | 0.00005330 |
| ig-clear-07 | clear | 3/3 | block, block, block | 452.058 | 1146/66 | 0.00004813 |
| ig-clear-08 | clear | 3/3 | block, block, block | 478.78 | 1155/66 | 0.00004851 |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 449.343 | 1155/66 | 0.00004851 |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 484.763 | 1161/66 | 0.00004876 |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 486.359 | 1152/66 | 0.00004838 |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### jev-openrouter/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 482.8215 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 468.594 | 1542/129 | 0.00006476 |
| route-clear-contract-review | clear | 3/3 | route, route, route | 495.41 | 1557/138 | 0.00006539 |
| route-clear-code-debug | clear | 3/3 | route, route, route | 475.405 | 1533/135 | 0.00006439 |
| route-clear-translation | clear | 3/3 | route, route, route | 456.292 | 1497/138 | 0.00006287 |
| route-clear-short-summary | clear | 3/3 | route, route, route | 474.231 | 1527/123 | 0.00006413 |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 475.659 | 1512/129 | 0.00006350 |
| route-clear-math-proof | clear | 3/3 | route, route, route | 508.229 | 1557/144 | 0.00006539 |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 514.913 | 1329/126 | 0.00005582 |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 528.629 | 1458/129 | 0.00006124 |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | escalate, escalate, escalate | 597.287 | 1494/132 | 0.00006275 |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 483.01 | 1278/108 | 0.00005368 |
| route-adversarial-injected-task | adversarial | 3/3 | escalate, route, escalate | 451.912 | 1326/114 | 0.00005569 |

### jev-openrouter/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 480.73 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 479.94 | 2037/156 | 0.00008555 |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 460.012 | 1977/156 | 0.00008303 |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 487.766 | 1977/156 | 0.00008303 |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 466.913 | 2076/156 | 0.00008719 |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 497.311 | 2034/156 | 0.00008543 |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 460.262 | 2022/156 | 0.00008492 |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 480.637 | 1992/156 | 0.00008366 |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 475.263 | 2019/156 | 0.00008480 |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | rank, rank, rank | 491.668 | 2061/156 | 0.00008656 |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 631.134 | 2004/156 | 0.00008417 |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 487.995 | 2076/156 | 0.00008719 |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 525.235 | 1743/108 | 0.00007321 |

### jev-openrouter/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 24; live median latency: 467.18899999999996 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 454.03 | 1455/126 | 0.00006111 |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 497.551 | 1416/126 | 0.00005947 |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 459.154 | 1425/126 | 0.00005985 |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 471.156 | 1428/126 | 0.00005998 |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 488.108 | 1404/126 | 0.00005897 |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 474.722 | 1443/126 | 0.00006061 |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 461.063 | 1356/129 | 0.00005695 |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 446.055 | 1353/129 | 0.00005683 |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### jev-openrouter/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 477.914 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 488.041 | 1770/129 | 0.00007434 |
| clear-02 | clear | 3/3 | send, send, send | 460.308 | 1701/129 | 0.00007144 |
| clear-03 | clear | 3/3 | send, send, send | 542.88 | 1686/129 | 0.00007081 |
| clear-04 | clear | 3/3 | send, send, send | 471.787 | 1674/129 | 0.00007031 |
| clear-05 | clear | 3/3 | send, send, send | 478.798 | 1782/129 | 0.00007484 |
| clear-06 | clear | 3/3 | send, send, send | 448.015 | 1776/129 | 0.00007459 |
| clear-07 | clear | 3/3 | send, send, send | 459.435 | 1668/129 | 0.00007006 |
| clear-08 | clear | 3/3 | send, send, send | 463.979 | 1671/129 | 0.00007018 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 488.335 | 1626/129 | 0.00006829 |
| ambiguous-02 | ambiguous | 3/3 | review, review, escalate | 502.63 | 1638/129 | 0.00006880 |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 487.752 | 1638/129 | 0.00006880 |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### jev-openrouter/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 471.23 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 2/3 | review, pass, pass | 477.721 | 2475/225 | 0.00010395 |
| clear-02 | clear | 3/3 | pass, pass, pass | 461.842 | 2457/225 | 0.00010319 |
| clear-03 | clear | 3/3 | pass, pass, pass | 467.867 | 2454/225 | 0.00010307 |
| clear-04 | clear | 3/3 | pass, pass, pass | 481.15 | 2466/225 | 0.00010357 |
| clear-05 | clear | 3/3 | pass, pass, pass | 471.23 | 2526/225 | 0.00010609 |
| clear-06 | clear | 3/3 | pass, pass, pass | 477.529 | 2457/225 | 0.00010319 |
| clear-07 | clear | 3/3 | pass, pass, pass | 451.726 | 2475/225 | 0.00010395 |
| clear-08 | clear | 3/3 | fail, fail, fail | 465.261 | 2568/225 | 0.00010786 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 476.235 | 2448/225 | 0.00010282 |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 533.661 | 2448/225 | 0.00010282 |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 470.238 | 2463/225 | 0.00010345 |

### openai-decisions/input-guardrails

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 298.201 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 294.963 | 774/0 | 0.00007740 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 298.201 | 786/0 | 0.00007860 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 311.968 | 705/0 | 0.00007050 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 305.238 | 714/0 | 0.00007140 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 313.783 | 777/0 | 0.00007770 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 314.203 | 819/0 | 0.00008190 estimated |
| ig-clear-07 | clear | 0/3 | review, review, review | 280.204 | 720/0 | 0.00007200 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 280.086 | 726/0 | 0.00007260 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | review, review, review | 296.172 | 732/0 | 0.00007320 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 278.127 | 738/0 | 0.00007380 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 299.062 | 729/0 | 0.00007290 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### openai-decisions/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 289.06 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 291.082 | 816/0 | 0.00008160 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 289.107 | 837/0 | 0.00008370 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 268.109 | 804/0 | 0.00008040 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 281.091 | 783/0 | 0.00007830 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 278.347 | 798/0 | 0.00007980 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 334.294 | 792/0 | 0.00007920 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 278.963 | 825/0 | 0.00008250 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 283.98 | 651/0 | 0.00006510 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 286.235 | 753/0 | 0.00007530 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 290.951 | 789/0 | 0.00007890 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 372.556 | 630/0 | 0.00006300 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 290.138 | 657/0 | 0.00006570 estimated |

### openai-decisions/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 297.616 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 299.288 | 1887/0 | 0.00018870 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 301.337 | 1839/0 | 0.00018390 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 289.582 | 1839/0 | 0.00018390 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 316.327 | 1929/0 | 0.00019290 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 291.589 | 1869/0 | 0.00018690 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 310.539 | 1866/0 | 0.00018660 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 283.943 | 1851/0 | 0.00018510 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 283.129 | 1857/0 | 0.00018570 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 325.24 | 1896/0 | 0.00018960 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 306.908 | 1860/0 | 0.00018600 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 296.528 | 1917/0 | 0.00019170 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 279.662 | 1344/0 | 0.00013440 estimated |

### openai-decisions/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 24; live median latency: 297.4695 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 300.521 | 774/0 | 0.00007740 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 318.641 | 747/0 | 0.00007470 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 278.645 | 753/0 | 0.00007530 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 281.826 | 750/0 | 0.00007500 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 280.134 | 744/0 | 0.00007440 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 305.747 | 771/0 | 0.00007710 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 308.346 | 696/0 | 0.00006960 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 295.272 | 693/0 | 0.00006930 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### openai-decisions/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 291.423 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 290.75 | 1641/0 | 0.00016410 estimated |
| clear-02 | clear | 3/3 | send, send, send | 291.423 | 1566/0 | 0.00015660 estimated |
| clear-03 | clear | 3/3 | send, send, send | 305.265 | 1551/0 | 0.00015510 estimated |
| clear-04 | clear | 3/3 | send, send, send | 323.408 | 1551/0 | 0.00015510 estimated |
| clear-05 | clear | 3/3 | send, send, send | 281.162 | 1638/0 | 0.00016380 estimated |
| clear-06 | clear | 3/3 | send, send, send | 300.057 | 1614/0 | 0.00016140 estimated |
| clear-07 | clear | 3/3 | send, send, send | 286.672 | 1539/0 | 0.00015390 estimated |
| clear-08 | clear | 3/3 | send, send, send | 292.743 | 1560/0 | 0.00015600 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 361.38 | 1512/0 | 0.00015120 estimated |
| ambiguous-02 | ambiguous | 3/3 | escalate, escalate, escalate | 290.98 | 1515/0 | 0.00015150 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 290.799 | 1521/0 | 0.00015210 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### openai-decisions/output-evaluation

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 299.522 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 297.125 | 2982/0 | 0.00029820 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 281.629 | 2976/0 | 0.00029760 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 310.311 | 2970/0 | 0.00029700 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 341.065 | 2970/0 | 0.00029700 estimated |
| clear-05 | clear | 0/3 | fail, fail, fail | 284.821 | 3015/0 | 0.00030150 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 299.522 | 2964/0 | 0.00029640 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 309.317 | 2994/0 | 0.00029940 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 347.991 | 3045/0 | 0.00030450 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 301.877 | 2967/0 | 0.00029670 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 276.07 | 2964/0 | 0.00029640 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 315.469 | 2979/0 | 0.00029790 estimated |

### sage/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 344.054 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 338.821 | 489/0 | 0.00005445 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 380.124 | 501/0 | 0.00005505 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 339.819 | 420/0 | 0.00005100 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 433.093 | 429/0 | 0.00005145 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 323.877 | 492/0 | 0.00005460 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 326.01 | 534/0 | 0.00005670 estimated |
| ig-clear-07 | clear | 3/3 | block, block, block | 363.906 | 435/0 | 0.00005175 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 329.853 | 441/0 | 0.00005205 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 468.541 | 447/0 | 0.00005235 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 344.054 | 453/0 | 0.00005265 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 318.861 | 444/0 | 0.00005220 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### sage/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 328.8765 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 332.472 | 693/0 | 0.00006465 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 328.566 | 714/0 | 0.00006570 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 448.392 | 681/0 | 0.00006405 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 328.207 | 660/0 | 0.00006300 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 312.215 | 675/0 | 0.00006375 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 458.704 | 669/0 | 0.00006345 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 315.148 | 702/0 | 0.00006510 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 384.251 | 510/0 | 0.00005550 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 349.369 | 630/0 | 0.00006150 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 380.107 | 666/0 | 0.00006330 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 329.064 | 489/0 | 0.00005445 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 313.19 | 519/0 | 0.00005595 estimated |

### sage/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 371.28549999999996 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 395.508 | 2055/0 | 0.00019275 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 359.626 | 1917/0 | 0.00018585 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 363.945 | 1917/0 | 0.00018585 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 367.267 | 2187/0 | 0.00019935 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 382.101 | 1995/0 | 0.00018975 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 348.856 | 1992/0 | 0.00018960 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 454.829 | 1953/0 | 0.00018765 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 418.746 | 1971/0 | 0.00018855 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 508.526 | 2076/0 | 0.00019380 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | review, review, review | 410.43 | 1980/0 | 0.00018900 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 368.728 | 2145/0 | 0.00019725 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 367.381 | 1350/0 | 0.00012750 estimated |

### sage/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 24; live median latency: 351.16549999999995 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 322.261 | 627/0 | 0.00006135 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 419.029 | 600/0 | 0.00006000 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 406.01 | 606/0 | 0.00006030 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 339.12 | 603/0 | 0.00006015 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 346.423 | 597/0 | 0.00005985 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 348.326 | 624/0 | 0.00006120 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 300.782 | 549/0 | 0.00005745 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 365.135 | 546/0 | 0.00005730 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### sage/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 351.943 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 363.0 | 1356/0 | 0.00012780 estimated |
| clear-02 | clear | 3/3 | send, send, send | 427.777 | 1206/0 | 0.00012030 estimated |
| clear-03 | clear | 3/3 | send, send, send | 374.214 | 1176/0 | 0.00011880 estimated |
| clear-04 | clear | 3/3 | send, send, send | 355.326 | 1176/0 | 0.00011880 estimated |
| clear-05 | clear | 3/3 | send, send, send | 360.792 | 1344/0 | 0.00012720 estimated |
| clear-06 | clear | 3/3 | send, send, send | 334.696 | 1302/0 | 0.00012510 estimated |
| clear-07 | clear | 3/3 | send, send, send | 344.806 | 1152/0 | 0.00011760 estimated |
| clear-08 | clear | 3/3 | send, send, send | 337.716 | 1194/0 | 0.00011970 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 329.573 | 1098/0 | 0.00011490 estimated |
| ambiguous-02 | ambiguous | 3/3 | review, review, review | 332.707 | 1110/0 | 0.00011550 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 332.74 | 1116/0 | 0.00011580 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### sage/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 365.568 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 371.755 | 2358/0 | 0.00023790 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 358.783 | 2334/0 | 0.00023670 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 350.851 | 2322/0 | 0.00023610 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 347.222 | 2310/0 | 0.00023550 estimated |
| clear-05 | clear | 3/3 | pass, pass, pass | 346.618 | 2526/0 | 0.00024630 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 369.804 | 2286/0 | 0.00023430 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 400.979 | 2406/0 | 0.00024030 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 455.761 | 2658/0 | 0.00025290 estimated |
| ambiguous-01 | ambiguous | 3/3 | pass, pass, pass | 411.811 | 2298/0 | 0.00023490 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 382.727 | 2298/0 | 0.00023490 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 404.736 | 2346/0 | 0.00023730 estimated |

