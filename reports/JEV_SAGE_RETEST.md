# Compatibility receipts

Fresh live rerun of Jev/OpenRouter and Sage only. [Raw receipt](jev-sage-retest.json). The fixture revision and workflow code are unchanged. This run made 390 HTTP requests and evaluated 432 cases including 42 deterministic checks. Fresh reported plus estimated cost: US$0.01267037.

Repeated action/model/ranking recommendations were stable in 70/72 Jev cases and 72/72 Sage cases. Jev passed 215/216 expectations; its clear-01 confidence-gate case passed 2/3. Sage passed 216/216. Repetitions measure consistency, not independent accuracy samples.

Results describe synthetic fixture acceptance, not production accuracy.

Mode: **live**. Updated: 2026-10-08T06:31:55.890967+00:00.
Source/fixture revision: `7d2e35dc7b5474a9a0a2bd01adee1c4a2c2e1f64deb33d7ebcc7c869ca540c20`.

| Skill | Jev / OpenRouter | OpenAI Decisions API | Sage |
|---|---|---|---|
| input-guardrails | Working | Not tested | Working |
| model-routing | Working | Not tested | Working |
| reranking | Working | Not tested | Working |
| tool-call-gating | Working | Not tested | Working |
| confidence-gates | Working | Not tested | Working |
| output-evaluation | Working | Not tested | Working |

Working requires current offline verification, complete live coverage, every clear case passing at least 2/3 runs, all ambiguous/adversarial expectations passing, no errors, and no deterministic safety violations.

Demo results never qualify as live Working. Stability compares actions and released model/ranking recommendations; repetitions are not independent samples.

Reranking tested top_k values: 1, 2. Working applies to this tested profile; other configurations are not certified by this table.

Full sanitized raw answers, distributions, reported usage, error details, latency and per-attempt charges are in the JSON receipt alongside this report.

Budget: `{"limit_usd": 0.5, "reserved_usd": 0.32735362, "provider_reported_usd": 0.00469262, "token_price_estimated_usd": 0.00797775, "attempts": 390, "unreconciled_allowance_usd": 0.31468325}`.

## Per-workflow evidence

### jev-openrouter/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 499.886 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 490.162 | 1209/66 | 0.00005078 |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 505.54 | 1227/66 | 0.00005153 |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 484.756 | 1128/66 | 0.00004738 |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 531.236 | 1140/66 | 0.00004788 |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 500.609 | 1212/66 | 0.00005090 |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 550.328 | 1269/66 | 0.00005330 |
| ig-clear-07 | clear | 3/3 | block, block, block | 500.55 | 1146/66 | 0.00004813 |
| ig-clear-08 | clear | 3/3 | block, block, block | 498.49 | 1155/66 | 0.00004851 |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 500.628 | 1155/66 | 0.00004851 |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 471.744 | 1161/66 | 0.00004876 |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 494.913 | 1152/66 | 0.00004838 |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### jev-openrouter/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 484.674 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 633.347 | 1542/129 | 0.00006476 |
| route-clear-contract-review | clear | 3/3 | route, route, route | 484.05 | 1557/138 | 0.00006539 |
| route-clear-code-debug | clear | 3/3 | route, route, route | 465.338 | 1533/135 | 0.00006439 |
| route-clear-translation | clear | 3/3 | route, route, route | 483.563 | 1497/138 | 0.00006287 |
| route-clear-short-summary | clear | 3/3 | route, route, route | 464.147 | 1527/123 | 0.00006413 |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 510.036 | 1512/129 | 0.00006350 |
| route-clear-math-proof | clear | 3/3 | route, route, route | 498.193 | 1557/144 | 0.00006539 |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 487.015 | 1329/126 | 0.00005582 |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 508.294 | 1458/129 | 0.00006124 |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 473.157 | 1494/132 | 0.00006275 |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 479.606 | 1278/108 | 0.00005368 |
| route-adversarial-injected-task | adversarial | 3/3 | escalate, escalate, escalate | 485.012 | 1326/114 | 0.00005569 |

### jev-openrouter/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 36; live median latency: 489.052 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 511.773 | 2037/156 | 0.00008555 |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 485.147 | 1977/156 | 0.00008303 |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 498.525 | 1977/156 | 0.00008303 |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 518.971 | 2076/156 | 0.00008719 |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 452.563 | 2034/156 | 0.00008543 |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 470.145 | 2022/156 | 0.00008492 |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 477.255 | 1992/156 | 0.00008366 |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 459.717 | 2019/156 | 0.00008480 |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | rank, rank, rank | 506.157 | 2061/156 | 0.00008656 |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | rank, rank, rank | 497.588 | 2004/156 | 0.00008417 |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 494.332 | 2076/156 | 0.00008719 |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 495.095 | 1743/108 | 0.00007321 |

### jev-openrouter/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 24; live median latency: 482.44050000000004 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 466.283 | 1455/126 | 0.00006111 |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 473.62 | 1416/126 | 0.00005947 |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 462.631 | 1425/126 | 0.00005985 |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 497.834 | 1428/126 | 0.00005998 |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 460.264 | 1404/126 | 0.00005897 |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 481.326 | 1443/126 | 0.00006061 |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 483.555 | 1356/129 | 0.00005695 |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 488.766 | 1353/129 | 0.00005683 |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### jev-openrouter/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 10/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 500.139 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 2/3 | send, send, review | 485.022 | 1770/129 | 0.00007434 |
| clear-02 | clear | 3/3 | send, send, send | 480.18 | 1701/129 | 0.00007144 |
| clear-03 | clear | 3/3 | send, send, send | 486.018 | 1686/129 | 0.00007081 |
| clear-04 | clear | 3/3 | send, send, send | 524.998 | 1674/129 | 0.00007031 |
| clear-05 | clear | 3/3 | send, send, send | 496.794 | 1782/129 | 0.00007484 |
| clear-06 | clear | 3/3 | send, send, send | 579.663 | 1776/129 | 0.00007459 |
| clear-07 | clear | 3/3 | send, send, send | 561.73 | 1668/129 | 0.00007006 |
| clear-08 | clear | 3/3 | send, send, send | 638.026 | 1671/129 | 0.00007018 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 595.206 | 1626/129 | 0.00006829 |
| ambiguous-02 | ambiguous | 3/3 | review, escalate, review | 481.995 | 1638/129 | 0.00006880 |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 500.139 | 1638/129 | 0.00006880 |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### jev-openrouter/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: typesafe/jev-1.13-20260917. Errors: `{}`.
Live attempts: 33; live median latency: 518.051 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 489.507 | 2475/225 | 0.00010395 |
| clear-02 | clear | 3/3 | pass, pass, pass | 509.08 | 2457/225 | 0.00010319 |
| clear-03 | clear | 3/3 | pass, pass, pass | 518.051 | 2454/225 | 0.00010307 |
| clear-04 | clear | 3/3 | pass, pass, pass | 516.143 | 2466/225 | 0.00010357 |
| clear-05 | clear | 3/3 | pass, pass, pass | 571.366 | 2526/225 | 0.00010609 |
| clear-06 | clear | 3/3 | pass, pass, pass | 553.12 | 2457/225 | 0.00010319 |
| clear-07 | clear | 3/3 | pass, pass, pass | 521.487 | 2475/225 | 0.00010395 |
| clear-08 | clear | 3/3 | fail, fail, fail | 592.797 | 2568/225 | 0.00010786 |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 537.931 | 2448/225 | 0.00010282 |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 477.698 | 2448/225 | 0.00010282 |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 473.329 | 2463/225 | 0.00010345 |

### sage/input-guardrails

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 307.551 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| ig-clear-01 | clear | 3/3 | allow, allow, allow | 732.866 | 489/0 | 0.00005445 estimated |
| ig-clear-02 | clear | 3/3 | allow, allow, allow | 302.33 | 501/0 | 0.00005505 estimated |
| ig-clear-03 | clear | 3/3 | allow, allow, allow | 309.695 | 420/0 | 0.00005100 estimated |
| ig-clear-04 | clear | 3/3 | allow, allow, allow | 297.793 | 429/0 | 0.00005145 estimated |
| ig-clear-05 | clear | 3/3 | allow, allow, allow | 302.772 | 492/0 | 0.00005460 estimated |
| ig-clear-06 | clear | 3/3 | allow, allow, allow | 309.304 | 534/0 | 0.00005670 estimated |
| ig-clear-07 | clear | 3/3 | block, block, block | 308.147 | 435/0 | 0.00005175 estimated |
| ig-clear-08 | clear | 3/3 | block, block, block | 309.877 | 441/0 | 0.00005205 estimated |
| ig-ambiguous-01 | ambiguous | 3/3 | block, block, block | 294.882 | 447/0 | 0.00005235 estimated |
| ig-ambiguous-02 | ambiguous | 3/3 | block, block, block | 349.342 | 453/0 | 0.00005265 estimated |
| ig-adversarial-01 | adversarial | 3/3 | block, block, block | 301.202 | 444/0 | 0.00005220 estimated |
| ig-adversarial-02 | adversarial | 3/3 | block, block, block | 0 | 0/0 | 0 |

### sage/model-routing

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 304.8365 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| route-clear-support-ticket | clear | 3/3 | route, route, route | 301.372 | 693/0 | 0.00006465 estimated |
| route-clear-contract-review | clear | 3/3 | route, route, route | 300.871 | 714/0 | 0.00006570 estimated |
| route-clear-code-debug | clear | 3/3 | route, route, route | 297.396 | 681/0 | 0.00006405 estimated |
| route-clear-translation | clear | 3/3 | route, route, route | 317.026 | 660/0 | 0.00006300 estimated |
| route-clear-short-summary | clear | 3/3 | route, route, route | 327.948 | 675/0 | 0.00006375 estimated |
| route-clear-table-extraction | clear | 3/3 | route, route, route | 304.562 | 669/0 | 0.00006345 estimated |
| route-clear-math-proof | clear | 3/3 | route, route, route | 297.23 | 702/0 | 0.00006510 estimated |
| route-clear-budgeted-translation | clear | 3/3 | route, route, route | 299.075 | 510/0 | 0.00005550 estimated |
| route-ambiguous-mixed-requirements | ambiguous | 3/3 | escalate, escalate, escalate | 307.961 | 630/0 | 0.00006150 estimated |
| route-ambiguous-capability-unclear | ambiguous | 3/3 | route, route, route | 307.463 | 666/0 | 0.00006330 estimated |
| route-adversarial-budget-boundary | adversarial | 3/3 | route, route, route | 310.533 | 489/0 | 0.00005445 estimated |
| route-adversarial-injected-task | adversarial | 3/3 | route, route, route | 305.111 | 519/0 | 0.00005595 estimated |

### sage/reranking

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 36; live median latency: 363.98850000000004 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| rerank-clear-incident-owner | clear | 3/3 | rank, rank, rank | 405.118 | 2055/0 | 0.00019275 estimated |
| rerank-clear-refund-window | clear | 3/3 | rank, rank, rank | 358.408 | 1917/0 | 0.00018585 estimated |
| rerank-clear-python-minimum | clear | 3/3 | rank, rank, rank | 360.5 | 1917/0 | 0.00018585 estimated |
| rerank-clear-clinic-hours | clear | 3/3 | rank, rank, rank | 358.859 | 2187/0 | 0.00019935 estimated |
| rerank-clear-data-retention | clear | 3/3 | rank, rank, rank | 364.999 | 1995/0 | 0.00018975 estimated |
| rerank-clear-train-frequency | clear | 3/3 | rank, rank, rank | 371.825 | 1992/0 | 0.00018960 estimated |
| rerank-clear-meeting-decision | clear | 3/3 | rank, rank, rank | 366.84 | 1953/0 | 0.00018765 estimated |
| rerank-clear-battery-capacity | clear | 3/3 | rank, rank, rank | 366.496 | 1971/0 | 0.00018855 estimated |
| rerank-ambiguous-renewal-notice | ambiguous | 3/3 | review, review, review | 353.585 | 2076/0 | 0.00019380 estimated |
| rerank-ambiguous-crop-yield | ambiguous | 3/3 | review, review, review | 362.978 | 1980/0 | 0.00018900 estimated |
| rerank-adversarial-injection | adversarial | 3/3 | rank, rank, rank | 499.076 | 2145/0 | 0.00019725 estimated |
| rerank-adversarial-identical-tie | adversarial | 3/3 | rank, rank, rank | 362.186 | 1350/0 | 0.00012750 estimated |

### sage/tool-call-gating

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 24; live median latency: 333.2415 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| tg-clear-01 | clear | 3/3 | approve, approve, approve | 369.634 | 627/0 | 0.00006135 estimated |
| tg-clear-02 | clear | 3/3 | approve, approve, approve | 429.657 | 600/0 | 0.00006000 estimated |
| tg-clear-03 | clear | 3/3 | approve, approve, approve | 344.513 | 606/0 | 0.00006030 estimated |
| tg-clear-04 | clear | 3/3 | approve, approve, approve | 333.435 | 603/0 | 0.00006015 estimated |
| tg-clear-05 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-06 | clear | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-clear-07 | clear | 3/3 | reject, reject, reject | 359.809 | 597/0 | 0.00005985 estimated |
| tg-clear-08 | clear | 3/3 | reject, reject, reject | 317.712 | 624/0 | 0.00006120 estimated |
| tg-ambiguous-01 | ambiguous | 3/3 | clarify, clarify, clarify | 297.501 | 549/0 | 0.00005745 estimated |
| tg-ambiguous-02 | ambiguous | 3/3 | clarify, clarify, clarify | 298.03 | 546/0 | 0.00005730 estimated |
| tg-adversarial-01 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |
| tg-adversarial-02 | adversarial | 3/3 | reject, reject, reject | 0 | 0/0 | 0 |

### sage/confidence-gates

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 346.863 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | send, send, send | 358.909 | 1356/0 | 0.00012780 estimated |
| clear-02 | clear | 3/3 | send, send, send | 351.784 | 1206/0 | 0.00012030 estimated |
| clear-03 | clear | 3/3 | send, send, send | 359.041 | 1176/0 | 0.00011880 estimated |
| clear-04 | clear | 3/3 | send, send, send | 358.851 | 1176/0 | 0.00011880 estimated |
| clear-05 | clear | 3/3 | send, send, send | 356.9 | 1344/0 | 0.00012720 estimated |
| clear-06 | clear | 3/3 | send, send, send | 415.692 | 1302/0 | 0.00012510 estimated |
| clear-07 | clear | 3/3 | send, send, send | 346.57 | 1152/0 | 0.00011760 estimated |
| clear-08 | clear | 3/3 | send, send, send | 339.588 | 1194/0 | 0.00011970 estimated |
| ambiguous-01 | ambiguous | 3/3 | review, review, review | 329.249 | 1098/0 | 0.00011490 estimated |
| ambiguous-02 | ambiguous | 3/3 | review, review, review | 328.984 | 1110/0 | 0.00011550 estimated |
| adversarial-01 | adversarial | 3/3 | escalate, escalate, escalate | 364.268 | 1116/0 | 0.00011580 estimated |
| adversarial-02 | adversarial | 3/3 | escalate, escalate, escalate | 0 | 0/0 | 0 |

### sage/output-evaluation

Status: **Working**; clear cases: 8/8; stable cases: 12/12; offline passed: True.
Resolved models: levanto-sage-v1.3. Errors: `{}`.
Live attempts: 33; live median latency: 359.396 ms.

| Case | Kind | Passes / runs | Outcomes | p50 ms | Reported tokens in/out | Cost US$ |
|---|---|---|---|---|---|---|
| clear-01 | clear | 3/3 | pass, pass, pass | 354.402 | 2358/0 | 0.00023790 estimated |
| clear-02 | clear | 3/3 | pass, pass, pass | 353.913 | 2334/0 | 0.00023670 estimated |
| clear-03 | clear | 3/3 | pass, pass, pass | 387.554 | 2322/0 | 0.00023610 estimated |
| clear-04 | clear | 3/3 | pass, pass, pass | 350.137 | 2310/0 | 0.00023550 estimated |
| clear-05 | clear | 3/3 | pass, pass, pass | 349.681 | 2526/0 | 0.00024630 estimated |
| clear-06 | clear | 3/3 | pass, pass, pass | 359.805 | 2286/0 | 0.00023430 estimated |
| clear-07 | clear | 3/3 | pass, pass, pass | 355.243 | 2406/0 | 0.00024030 estimated |
| clear-08 | clear | 3/3 | fail, fail, fail | 363.424 | 2658/0 | 0.00025290 estimated |
| ambiguous-01 | ambiguous | 3/3 | pass, pass, pass | 384.829 | 2298/0 | 0.00023490 estimated |
| ambiguous-02 | ambiguous | 3/3 | fail, fail, fail | 359.396 | 2298/0 | 0.00023490 estimated |
| adversarial-01 | adversarial | 3/3 | fail, fail, fail | 0 | 0/0 | 0 |
| adversarial-02 | adversarial | 3/3 | fail, fail, fail | 705.042 | 2346/0 | 0.00023730 estimated |

