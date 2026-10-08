# Compatibility receipts

Results describe synthetic fixture acceptance, not production accuracy.

Mode: **live**. Updated: 2026-10-08T02:04:51.409146+00:00.
Source/fixture revision: `7d2e35dc7b5474a9a0a2bd01adee1c4a2c2e1f64deb33d7ebcc7c869ca540c20`.

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

Budget: `{"limit_usd": 3.0, "reserved_usd": 0.46542022, "provider_reported_usd": 0.00469262, "token_price_estimated_usd": 0.01750485, "attempts": 585, "unreconciled_allowance_usd": 0.44322275}`.

## Per-workflow evidence

### jev-openrouter/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 515.931 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 516.123 | 1209/66 | 0.00005078 |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 582.158 | 1227/66 | 0.00005153 |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 493.55 | 1128/66 | 0.00004738 |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 539.467 | 1140/66 | 0.00004788 |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 487.048 | 1212/66 | 0.00005090 |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 533.578 | 1269/66 | 0.00005330 |
| ig-clear-07 | clear | 3/3 | block, block, block | 573.488 | 1146/66 | 0.00004813 |
| ig-clear-08 | clear | 3/3 | block, block, block | 494.76 | 1155/66 | 0.00004851 |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 514.75 | 1155/66 | 0.00004851 |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 542.426 | 1161/66 | 0.00004876 |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 499.011 | 1152/66 | 0.00004838 |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### jev-openrouter/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 498.445 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 475.544 | 1542/129 | 0.00006476 |
| route-clear-contract-review | clear | 3/3 | route, route, route | 545.943 | 1557/138 | 0.00006539 |
| route-clear-code-debug | clear | 3/3 | route, route, route | 546.107 | 1533/135 | 0.00006439 |
| route-clear-translation | clear | 3/3 | route, route, route | 477.285 | 1497/138 | 0.00006287 |
| route-clear-short-summary | clear | 3/3 | route, route, route | 525.495 | 1527/123 | 0.00006413 |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 484.462 | 1512/129 | 0.00006350 |
| route-clear-math-proof | clear | 3/3 | route, route, route | 504.703 | 1557/144 | 0.00006539 |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 511.199 | 1329/126 | 0.00005582 |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 506.053 | 1458/129 | 0.00006124 |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | escalate, escalate, escalate | 466.72 | 1494/132 | 0.00006275 |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 456.198 | 1278/108 | 0.00005368 |
| route-adversarial-injected-task | adversarial | 3/3 | escalate, escalate, escalate | 572.271 | 1326/114 | 0.00005569 |

### jev-openrouter/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 493.4695 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 499.091 | 2037/156 | 0.00008555 |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 500.06 | 1977/156 | 0.00008303 |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 488.565 | 1977/156 | 0.00008303 |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 489.669 | 2076/156 | 0.00008719 |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 522.288 | 2034/156 | 0.00008543 |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 491.616 | 2022/156 | 0.00008492 |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 491.466 | 1992/156 | 0.00008366 |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 495.323 | 2019/156 | 0.00008480 |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | rank, rank, rank | 514.832 | 2061/156 | 0.00008656 |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 483.806 | 2004/156 | 0.00008417 |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 473.738 | 2076/156 | 0.00008719 |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 516.028 | 1743/108 | 0.00007321 |

### jev-openrouter/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 24; live median latency: 504.473 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 498.596 | 1455/126 | 0.00006111 |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 512.093 | 1416/126 | 0.00005947 |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 492.011 | 1425/126 | 0.00005985 |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 503.223 | 1428/126 | 0.00005998 |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 479.994 | 1404/126 | 0.00005897 |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 547.991 | 1443/126 | 0.00006061 |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 547.112 | 1356/129 | 0.00005695 |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 528.048 | 1353/129 | 0.00005683 |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### jev-openrouter/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 487.841 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 542.346 | 1770/129 | 0.00007434 |
| clear-02 | clear | 3/3 | send, send, send | 461.267 | 1701/129 | 0.00007144 |
| clear-03 | clear | 3/3 | send, send, send | 542.006 | 1686/129 | 0.00007081 |
| clear-04 | clear | 3/3 | send, send, send | 485.192 | 1674/129 | 0.00007031 |
| clear-05 | clear | 3/3 | send, send, send | 541.826 | 1782/129 | 0.00007484 |
| clear-06 | clear | 3/3 | send, send, send | 537.856 | 1776/129 | 0.00007459 |
| clear-07 | clear | 3/3 | send, send, send | 487.841 | 1668/129 | 0.00007006 |
| clear-08 | clear | 3/3 | send, send, send | 483.376 | 1671/129 | 0.00007018 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 509.148 | 1626/129 | 0.00006829 |
| ambiguous-02 | ambiguous | 3/3 | escalate, review, escalate | 469.624 | 1638/129 | 0.00006880 |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 619.06 | 1638/129 | 0.00006880 |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### jev-openrouter/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 11/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 506.322 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 2/3 | review, pass, pass | 529.729 | 2475/225 | 0.00010395 |
| clear-02 | clear | 3/3 | pass, pass, pass | 506.322 | 2457/225 | 0.00010319 |
| clear-03 | clear | 3/3 | pass, pass, pass | 464.036 | 2454/225 | 0.00010307 |
| clear-04 | clear | 3/3 | pass, pass, pass | 480.269 | 2466/225 | 0.00010357 |
| clear-05 | clear | 3/3 | pass, pass, pass | 501.709 | 2526/225 | 0.00010609 |
| clear-06 | clear | 3/3 | pass, pass, pass | 476.077 | 2457/225 | 0.00010319 |
| clear-07 | clear | 3/3 | pass, pass, pass | 601.872 | 2475/225 | 0.00010395 |
| clear-08 | clear | 3/3 | fail, fail, fail | 590.432 | 2568/225 | 0.00010786 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 490.255 | 2448/225 | 0.00010282 |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 501.47 | 2448/225 | 0.00010282 |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 530.869 | 2463/225 | 0.00010345 |

### openai-decisions/input-guardrails

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 306.847 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 437.322 | 774/0 | 0.00007740 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 296.537 | 786/0 | 0.00007860 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 306.468 | 705/0 | 0.00007050 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 309.284 | 714/0 | 0.00007140 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 336.951 | 777/0 | 0.00007770 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 306.847 | 819/0 | 0.00008190 estimated |
| ig-clear-07 | clear | 0/3 | review, review, review | 314.065 | 720/0 | 0.00007200 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 307.79 | 726/0 | 0.00007260 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | review, review, review | 291.996 | 732/0 | 0.00007320 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 282.257 | 738/0 | 0.00007380 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 313.677 | 729/0 | 0.00007290 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### openai-decisions/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 305.6645 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 301.695 | 816/0 | 0.00008160 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 295.455 | 837/0 | 0.00008370 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 305.624 | 804/0 | 0.00008040 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 330.418 | 783/0 | 0.00007830 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 289.967 | 798/0 | 0.00007980 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 289.39 | 792/0 | 0.00007920 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 324.855 | 825/0 | 0.00008250 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 315.13 | 651/0 | 0.00006510 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 323.273 | 753/0 | 0.00007530 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 375.718 | 789/0 | 0.00007890 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 363.74 | 630/0 | 0.00006300 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 308.047 | 657/0 | 0.00006570 estimated |

### openai-decisions/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 36; live median latency: 306.40999999999997 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 321.001 | 1887/0 | 0.00018870 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 313.032 | 1839/0 | 0.00018390 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 318.58 | 1839/0 | 0.00018390 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 322.256 | 1929/0 | 0.00019290 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 306.732 | 1869/0 | 0.00018690 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 308.166 | 1866/0 | 0.00018660 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 309.407 | 1851/0 | 0.00018510 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 291.688 | 1857/0 | 0.00018570 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 300.755 | 1896/0 | 0.00018960 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 296.527 | 1860/0 | 0.00018600 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 302.462 | 1917/0 | 0.00019170 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 294.75 | 1344/0 | 0.00013440 estimated |

### openai-decisions/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 24; live median latency: 302.1575 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 311.71 | 774/0 | 0.00007740 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 306.691 | 747/0 | 0.00007470 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 301.816 | 753/0 | 0.00007530 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 324.68 | 750/0 | 0.00007500 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 309.06 | 744/0 | 0.00007440 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 284.536 | 771/0 | 0.00007710 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 302.499 | 696/0 | 0.00006960 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 297.231 | 693/0 | 0.00006930 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### openai-decisions/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 319.909 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 324.259 | 1641/0 | 0.00016410 estimated |
| clear-02 | clear | 3/3 | send, send, send | 297.832 | 1566/0 | 0.00015660 estimated |
| clear-03 | clear | 3/3 | send, send, send | 301.318 | 1551/0 | 0.00015510 estimated |
| clear-04 | clear | 3/3 | send, send, send | 319.909 | 1551/0 | 0.00015510 estimated |
| clear-05 | clear | 3/3 | send, send, send | 346.924 | 1638/0 | 0.00016380 estimated |
| clear-06 | clear | 3/3 | send, send, send | 336.339 | 1614/0 | 0.00016140 estimated |
| clear-07 | clear | 3/3 | send, send, send | 664.782 | 1539/0 | 0.00015390 estimated |
| clear-08 | clear | 3/3 | send, send, send | 324.973 | 1560/0 | 0.00015600 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 318.045 | 1512/0 | 0.00015120 estimated |
| ambiguous-02 | ambiguous | 3/3 | escalate, escalate, escalate | 304.392 | 1515/0 | 0.00015150 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 294.272 | 1521/0 | 0.00015210 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### openai-decisions/output-evaluation

Status: **Partial**; clear cases: 7/8; stable cases: 12/12; offline passed: True.
Resolved models: gpt-6-luna. Errors: `{}`.
Live attempts: 33; live median latency: 319.542 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 307.221 | 2982/0 | 0.00029820 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 319.646 | 2976/0 | 0.00029760 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 338.333 | 2970/0 | 0.00029700 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 302.702 | 2970/0 | 0.00029700 estimated |
| clear-05 | clear | 0/3 | fail, fail, fail | 310.869 | 3015/0 | 0.00030150 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 328.043 | 2964/0 | 0.00029640 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 330.804 | 2994/0 | 0.00029940 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 303.464 | 3045/0 | 0.00030450 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 311.896 | 2967/0 | 0.00029670 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 324.256 | 2964/0 | 0.00029640 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 338.118 | 2979/0 | 0.00029790 estimated |

### sage/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 346.853 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 313.719 | 489/0 | 0.00005445 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 384.788 | 501/0 | 0.00005505 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 352.179 | 420/0 | 0.00005100 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 396.665 | 429/0 | 0.00005145 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 374.31 | 492/0 | 0.00005460 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 370.396 | 534/0 | 0.00005670 estimated |
| ig-clear-07 | clear | 3/3 | block, block, block | 346.853 | 435/0 | 0.00005175 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 343.45 | 441/0 | 0.00005205 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 329.501 | 447/0 | 0.00005235 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 339.345 | 453/0 | 0.00005265 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 336.523 | 444/0 | 0.00005220 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### sage/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 341.0685 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 351.932 | 693/0 | 0.00006465 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 309.191 | 714/0 | 0.00006570 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 344.445 | 681/0 | 0.00006405 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 327.485 | 660/0 | 0.00006300 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 340.331 | 675/0 | 0.00006375 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 333.009 | 669/0 | 0.00006345 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 335.405 | 702/0 | 0.00006510 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 371.113 | 510/0 | 0.00005550 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 329.846 | 630/0 | 0.00006150 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 354.707 | 666/0 | 0.00006330 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 373.509 | 489/0 | 0.00005445 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 306.49 | 519/0 | 0.00005595 estimated |

### sage/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 400.10450000000003 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 395.264 | 2055/0 | 0.00019275 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 368.513 | 1917/0 | 0.00018585 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 499.237 | 1917/0 | 0.00018585 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 511.528 | 2187/0 | 0.00019935 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 394.394 | 1995/0 | 0.00018975 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 471.328 | 1992/0 | 0.00018960 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 405.994 | 1953/0 | 0.00018765 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 373.836 | 1971/0 | 0.00018855 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 380.309 | 2076/0 | 0.00019380 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | review, review, review | 369.158 | 1980/0 | 0.00018900 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 407.134 | 2145/0 | 0.00019725 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 416.676 | 1350/0 | 0.00012750 estimated |

### sage/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 24; live median latency: 381.03549999999996 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 368.996 | 627/0 | 0.00006135 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 358.841 | 600/0 | 0.00006000 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 339.818 | 606/0 | 0.00006030 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 407.494 | 603/0 | 0.00006015 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 352.056 | 597/0 | 0.00005985 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 415.858 | 624/0 | 0.00006120 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 394.285 | 549/0 | 0.00005745 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 399.838 | 546/0 | 0.00005730 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### sage/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 381.267 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 386.021 | 1356/0 | 0.00012780 estimated |
| clear-02 | clear | 3/3 | send, send, send | 382.316 | 1206/0 | 0.00012030 estimated |
| clear-03 | clear | 3/3 | send, send, send | 387.195 | 1176/0 | 0.00011880 estimated |
| clear-04 | clear | 3/3 | send, send, send | 483.598 | 1176/0 | 0.00011880 estimated |
| clear-05 | clear | 3/3 | send, send, send | 361.213 | 1344/0 | 0.00012720 estimated |
| clear-06 | clear | 3/3 | send, send, send | 344.201 | 1302/0 | 0.00012510 estimated |
| clear-07 | clear | 3/3 | send, send, send | 372.972 | 1152/0 | 0.00011760 estimated |
| clear-08 | clear | 3/3 | send, send, send | 381.267 | 1194/0 | 0.00011970 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 370.323 | 1098/0 | 0.00011490 estimated |
| ambiguous-02 | ambiguous | 3/3 | review, review, review | 381.896 | 1110/0 | 0.00011550 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 354.556 | 1116/0 | 0.00011580 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### sage/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 404.851 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 375.56 | 2358/0 | 0.00023790 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 412.633 | 2334/0 | 0.00023670 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 399.308 | 2322/0 | 0.00023610 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 393.386 | 2310/0 | 0.00023550 estimated |
| clear-05 | clear | 3/3 | pass, pass, pass | 474.18 | 2526/0 | 0.00024630 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 397.368 | 2286/0 | 0.00023430 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 389.374 | 2406/0 | 0.00024030 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 401.814 | 2658/0 | 0.00025290 estimated |
| ambiguous-01 | ambiguous | 3/3 | pass, pass, pass | 416.629 | 2298/0 | 0.00023490 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 805.686 | 2298/0 | 0.00023490 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 738.395 | 2346/0 | 0.00023730 estimated |

