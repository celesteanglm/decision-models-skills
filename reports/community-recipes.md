# Published recipe compatibility

Only the 18 recipes with at least one Working backend are published. Partial means not qualified, and receives no positive backend label. See [Working labels](VERIFIED_CATALOG.md).

This report selects unchanged recipes from the original frozen candidate run. The [historical raw receipt](community-recipes.json) and budget cover all 29 original candidates; the 11 candidates without a Working backend have no published installable folder.

Synthetic decision slices only; no source-app or end-to-end performance claims.

Updated: 2026-10-08T11:24:50.801230+00:00. Source and fixtures: `e6115d0899d71d4c653e88d391ecf5d7f60ce7c94a2657de0dbc0e80abf08674`.

| Recipe | Jev / OpenRouter | OpenAI Decisions API | Sage |
|---|---|---|---|
| ad-funnel-classification | Partial | Working | Partial |
| agent-workflow-routing | Working | Working | Working |
| brand-news-matching | Partial | Partial | Working |
| browser-action-selection | Working | Partial | Working |
| content-revision-gate | Partial | Partial | Working |
| draft-quality-triage | Partial | Partial | Working |
| email-queue-routing | Working | Working | Working |
| invoice-file-triage | Working | Partial | Working |
| model-tier-routing | Partial | Partial | Working |
| outfit-option-selection | Partial | Partial | Working |
| page-change-triage | Working | Partial | Working |
| research-source-filter | Partial | Working | Partial |
| retrieved-instruction-screening | Working | Working | Partial |
| secondhand-listing-fit | Working | Working | Working |
| spoken-slide-selection | Partial | Working | Partial |
| spreadsheet-urgency | Partial | Partial | Working |
| suspicious-email-escalation | Partial | Working | Partial |
| template-field-matching | Partial | Partial | Working |

Working requires current offline checks, 12 cases × 3 runs, each clear case passing at least twice, all ambiguous/adversarial cases passing, successful live execution, no errors, and no deterministic safety violations. Repetitions measure stability; they are not independent samples.

Budget (provider-reported and estimated amounts separated): `{"reserved_usd": 1.42030999, "provider_reported_usd": 0.01851797, "token_price_estimated_usd": 0.04218255, "attempts": 2871, "unreconciled_allowance_usd": 1.3596094699999999, "limit_usd": 1.5}`.

## Per-recipe evidence

### jev-openrouter/ad-funnel-classification

**Partial**. Clear: 8/8; stable: 11/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 492.938 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | awareness, awareness, awareness |
| clear-02 | 3/3 | consideration, consideration, consideration |
| clear-03 | 3/3 | conversion, conversion, conversion |
| clear-04 | 3/3 | awareness, awareness, awareness |
| clear-05 | 3/3 | consideration, consideration, consideration |
| clear-06 | 3/3 | conversion, conversion, conversion |
| clear-07 | 3/3 | awareness, awareness, awareness |
| clear-08 | 3/3 | consideration, consideration, consideration |
| ambiguous-01 | 1/3 | consideration, review, consideration |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | awareness, awareness, awareness |

### jev-openrouter/agent-workflow-routing

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 477.508 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | payment_help, payment_help, payment_help |
| clear-02 | 3/3 | product_help, product_help, product_help |
| clear-03 | 3/3 | setup_help, setup_help, setup_help |
| clear-04 | 3/3 | payment_help, payment_help, payment_help |
| clear-05 | 3/3 | product_help, product_help, product_help |
| clear-06 | 3/3 | setup_help, setup_help, setup_help |
| clear-07 | 3/3 | payment_help, payment_help, payment_help |
| clear-08 | 3/3 | product_help, product_help, product_help |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | payment_help, payment_help, payment_help |

### jev-openrouter/brand-news-matching

**Partial**. Clear: 7/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 479.669 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | relevant, relevant, relevant |
| clear-02 | 3/3 | relevant, relevant, relevant |
| clear-03 | 3/3 | relevant, relevant, relevant |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-06 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-07 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-08 | 3/3 | not_relevant, not_relevant, not_relevant |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | relevant, relevant, relevant |

### jev-openrouter/browser-action-selection

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 481.264 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | click, click, click |
| clear-02 | 3/3 | click, click, click |
| clear-03 | 3/3 | click, click, click |
| clear-04 | 3/3 | click, click, click |
| clear-05 | 3/3 | type, type, type |
| clear-06 | 3/3 | type, type, type |
| clear-07 | 3/3 | type, type, type |
| clear-08 | 3/3 | type, type, type |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | click, click, click |

### jev-openrouter/content-revision-gate

**Partial**. Clear: 7/8; stable: 10/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 480.72 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | ready, ready, ready |
| clear-02 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| clear-03 | 3/3 | substantial_revision, substantial_revision, substantial_revision |
| clear-04 | 3/3 | ready, ready, ready |
| clear-05 | 2/3 | targeted_revision, review, targeted_revision |
| clear-06 | 1/3 | substantial_revision, review, review |
| clear-07 | 3/3 | ready, ready, ready |
| clear-08 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | ready, ready, ready |

### jev-openrouter/draft-quality-triage

**Partial**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 480.991 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | ready, ready, ready |
| clear-02 | 3/3 | ready, ready, ready |
| clear-03 | 3/3 | ready, ready, ready |
| clear-04 | 3/3 | ready, ready, ready |
| clear-05 | 3/3 | revise, revise, revise |
| clear-06 | 3/3 | revise, revise, revise |
| clear-07 | 3/3 | revise, revise, revise |
| clear-08 | 3/3 | revise, revise, revise |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 0/3 | review, review, review |

### jev-openrouter/email-queue-routing

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 484.334 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | billing, billing, billing |
| clear-02 | 3/3 | billing, billing, billing |
| clear-03 | 3/3 | billing, billing, billing |
| clear-04 | 3/3 | billing, billing, billing |
| clear-05 | 3/3 | account_support, account_support, account_support |
| clear-06 | 3/3 | account_support, account_support, account_support |
| clear-07 | 3/3 | account_support, account_support, account_support |
| clear-08 | 3/3 | account_support, account_support, account_support |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | account_support, account_support, account_support |

### jev-openrouter/invoice-file-triage

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 469.41 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | invoice, invoice, invoice |
| clear-02 | 3/3 | invoice, invoice, invoice |
| clear-03 | 3/3 | invoice, invoice, invoice |
| clear-04 | 3/3 | invoice, invoice, invoice |
| clear-05 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-06 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-07 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-08 | 3/3 | not_invoice, not_invoice, not_invoice |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | invoice, invoice, invoice |

### jev-openrouter/model-tier-routing

**Partial**. Clear: 6/8; stable: 11/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 496.511 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | fast, fast, fast |
| clear-02 | 3/3 | fast, fast, fast |
| clear-03 | 3/3 | fast, fast, fast |
| clear-04 | 1/3 | review, reasoning, review |
| clear-05 | 3/3 | reasoning, reasoning, reasoning |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 3/3 | specialist, specialist, specialist |
| clear-08 | 3/3 | specialist, specialist, specialist |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 0/3 | review, review, review |

### jev-openrouter/outfit-option-selection

**Partial**. Clear: 5/8; stable: 11/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 500.342 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-02 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-06 | 3/3 | light_kit, light_kit, light_kit |
| clear-07 | 1/3 | review, review, rain_kit |
| clear-08 | 3/3 | formal_kit, formal_kit, formal_kit |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | rain_kit, rain_kit, rain_kit |

### jev-openrouter/page-change-triage

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 489.199 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | material, material, material |
| clear-02 | 3/3 | material, material, material |
| clear-03 | 3/3 | material, material, material |
| clear-04 | 3/3 | material, material, material |
| clear-05 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-06 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-07 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-08 | 3/3 | cosmetic, cosmetic, cosmetic |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | material, material, material |

### jev-openrouter/research-source-filter

**Partial**. Clear: 4/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 483.079 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 0/3 | review, review, review |
| clear-02 | 3/3 | exclude, exclude, exclude |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | exclude, exclude, exclude |
| clear-06 | 3/3 | verify_first, verify_first, verify_first |
| clear-07 | 0/3 | review, review, review |
| clear-08 | 3/3 | exclude, exclude, exclude |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 0/3 | review, review, review |

### jev-openrouter/retrieved-instruction-screening

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 516.088 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | quarantine, quarantine, quarantine |
| clear-02 | 3/3 | quarantine, quarantine, quarantine |
| clear-03 | 3/3 | quarantine, quarantine, quarantine |
| clear-04 | 3/3 | quarantine, quarantine, quarantine |
| clear-05 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-06 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-07 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-08 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | quarantine, quarantine, quarantine |

### jev-openrouter/secondhand-listing-fit

**Working**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 493.446 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | shortlist, shortlist, shortlist |
| clear-02 | 3/3 | pass_over, pass_over, pass_over |
| clear-03 | 3/3 | request_details, request_details, request_details |
| clear-04 | 3/3 | shortlist, shortlist, shortlist |
| clear-05 | 3/3 | pass_over, pass_over, pass_over |
| clear-06 | 3/3 | request_details, request_details, request_details |
| clear-07 | 3/3 | shortlist, shortlist, shortlist |
| clear-08 | 3/3 | pass_over, pass_over, pass_over |
| ambiguous-01 | 3/3 | request_details, request_details, request_details |
| ambiguous-02 | 3/3 | request_details, request_details, request_details |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | shortlist, shortlist, shortlist |

### jev-openrouter/spoken-slide-selection

**Partial**. Clear: 8/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 488.515 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | opening_context, opening_context, opening_context |
| clear-02 | 3/3 | system_design, system_design, system_design |
| clear-03 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-04 | 3/3 | next_steps, next_steps, next_steps |
| clear-05 | 3/3 | opening_context, opening_context, opening_context |
| clear-06 | 3/3 | system_design, system_design, system_design |
| clear-07 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-08 | 3/3 | next_steps, next_steps, next_steps |
| ambiguous-01 | 0/3 | next_steps, next_steps, next_steps |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | opening_context, opening_context, opening_context |

### jev-openrouter/spreadsheet-urgency

**Partial**. Clear: 7/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 476.555 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-02 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-03 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-04 | 3/3 | soon, soon, soon |
| clear-05 | 3/3 | soon, soon, soon |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 3/3 | urgent, urgent, urgent |
| clear-08 | 3/3 | urgent, urgent, urgent |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | urgent, urgent, urgent |

### jev-openrouter/suspicious-email-escalation

**Partial**. Clear: 7/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 487.806 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-02 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-03 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-04 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-05 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-08 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | security_escalation, security_escalation, security_escalation |

### jev-openrouter/template-field-matching

**Partial**. Clear: 7/8; stable: 12/12; models: typesafe/jev-1.13-20260917; live calls: 33; median latency: 499.268 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-02 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-03 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-04 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-05 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-06 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-07 | 0/3 | review, review, review |
| clear-08 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | direct_mapping, direct_mapping, direct_mapping |

### openai-decisions/ad-funnel-classification

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 307.742 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | awareness, awareness, awareness |
| clear-02 | 3/3 | consideration, consideration, consideration |
| clear-03 | 3/3 | conversion, conversion, conversion |
| clear-04 | 3/3 | awareness, awareness, awareness |
| clear-05 | 3/3 | consideration, consideration, consideration |
| clear-06 | 3/3 | conversion, conversion, conversion |
| clear-07 | 3/3 | awareness, awareness, awareness |
| clear-08 | 3/3 | consideration, consideration, consideration |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | awareness, awareness, awareness |

### openai-decisions/agent-workflow-routing

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 299.595 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | payment_help, payment_help, payment_help |
| clear-02 | 3/3 | product_help, product_help, product_help |
| clear-03 | 3/3 | setup_help, setup_help, setup_help |
| clear-04 | 3/3 | payment_help, payment_help, payment_help |
| clear-05 | 3/3 | product_help, product_help, product_help |
| clear-06 | 3/3 | setup_help, setup_help, setup_help |
| clear-07 | 3/3 | payment_help, payment_help, payment_help |
| clear-08 | 3/3 | product_help, product_help, product_help |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | payment_help, payment_help, payment_help |

### openai-decisions/brand-news-matching

**Partial**. Clear: 7/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 302.872 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | relevant, relevant, relevant |
| clear-02 | 3/3 | relevant, relevant, relevant |
| clear-03 | 3/3 | relevant, relevant, relevant |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-06 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-07 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-08 | 3/3 | not_relevant, not_relevant, not_relevant |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | relevant, relevant, relevant |

### openai-decisions/browser-action-selection

**Partial**. Clear: 7/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 300.45 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 0/3 | review, review, review |
| clear-02 | 3/3 | click, click, click |
| clear-03 | 3/3 | click, click, click |
| clear-04 | 3/3 | click, click, click |
| clear-05 | 3/3 | type, type, type |
| clear-06 | 3/3 | type, type, type |
| clear-07 | 3/3 | type, type, type |
| clear-08 | 3/3 | type, type, type |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | click, click, click |

### openai-decisions/content-revision-gate

**Partial**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 298.808 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | ready, ready, ready |
| clear-02 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| clear-03 | 3/3 | substantial_revision, substantial_revision, substantial_revision |
| clear-04 | 3/3 | ready, ready, ready |
| clear-05 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| clear-06 | 3/3 | substantial_revision, substantial_revision, substantial_revision |
| clear-07 | 3/3 | ready, ready, ready |
| clear-08 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 0/3 | review, review, review |

### openai-decisions/draft-quality-triage

**Partial**. Clear: 1/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 292.118 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 0/3 | review, review, review |
| clear-02 | 0/3 | review, review, review |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 0/3 | review, review, review |
| clear-06 | 3/3 | revise, revise, revise |
| clear-07 | 0/3 | review, review, review |
| clear-08 | 0/3 | review, review, review |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 0/3 | review, review, review |

### openai-decisions/email-queue-routing

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 304.853 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | billing, billing, billing |
| clear-02 | 3/3 | billing, billing, billing |
| clear-03 | 3/3 | billing, billing, billing |
| clear-04 | 3/3 | billing, billing, billing |
| clear-05 | 3/3 | account_support, account_support, account_support |
| clear-06 | 3/3 | account_support, account_support, account_support |
| clear-07 | 3/3 | account_support, account_support, account_support |
| clear-08 | 3/3 | account_support, account_support, account_support |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | account_support, account_support, account_support |

### openai-decisions/invoice-file-triage

**Partial**. Clear: 7/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 305.209 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | invoice, invoice, invoice |
| clear-02 | 0/3 | review, review, review |
| clear-03 | 3/3 | invoice, invoice, invoice |
| clear-04 | 3/3 | invoice, invoice, invoice |
| clear-05 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-06 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-07 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-08 | 3/3 | not_invoice, not_invoice, not_invoice |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | invoice, invoice, invoice |

### openai-decisions/model-tier-routing

**Partial**. Clear: 4/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 295.812 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | fast, fast, fast |
| clear-02 | 3/3 | fast, fast, fast |
| clear-03 | 3/3 | fast, fast, fast |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 0/3 | review, review, review |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 0/3 | review, review, review |
| clear-08 | 3/3 | specialist, specialist, specialist |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 0/3 | review, review, review |

### openai-decisions/outfit-option-selection

**Partial**. Clear: 6/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 295.567 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-02 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-03 | 3/3 | light_kit, light_kit, light_kit |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-06 | 3/3 | light_kit, light_kit, light_kit |
| clear-07 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-08 | 0/3 | review, review, review |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | rain_kit, rain_kit, rain_kit |

### openai-decisions/page-change-triage

**Partial**. Clear: 1/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 296.943 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 0/3 | review, review, review |
| clear-02 | 0/3 | review, review, review |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 0/3 | review, review, review |
| clear-08 | 0/3 | review, review, review |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 0/3 | review, review, review |

### openai-decisions/research-source-filter

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 313.537 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | include, include, include |
| clear-02 | 3/3 | exclude, exclude, exclude |
| clear-03 | 3/3 | verify_first, verify_first, verify_first |
| clear-04 | 3/3 | include, include, include |
| clear-05 | 3/3 | exclude, exclude, exclude |
| clear-06 | 3/3 | verify_first, verify_first, verify_first |
| clear-07 | 3/3 | include, include, include |
| clear-08 | 3/3 | exclude, exclude, exclude |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | include, include, include |

### openai-decisions/retrieved-instruction-screening

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 296.622 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | quarantine, quarantine, quarantine |
| clear-02 | 3/3 | quarantine, quarantine, quarantine |
| clear-03 | 3/3 | quarantine, quarantine, quarantine |
| clear-04 | 3/3 | quarantine, quarantine, quarantine |
| clear-05 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-06 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-07 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-08 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | quarantine, quarantine, quarantine |

### openai-decisions/secondhand-listing-fit

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 300.815 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | shortlist, shortlist, shortlist |
| clear-02 | 3/3 | pass_over, pass_over, pass_over |
| clear-03 | 3/3 | request_details, request_details, request_details |
| clear-04 | 3/3 | shortlist, shortlist, shortlist |
| clear-05 | 3/3 | pass_over, pass_over, pass_over |
| clear-06 | 3/3 | request_details, request_details, request_details |
| clear-07 | 3/3 | shortlist, shortlist, shortlist |
| clear-08 | 3/3 | pass_over, pass_over, pass_over |
| ambiguous-01 | 3/3 | request_details, request_details, request_details |
| ambiguous-02 | 3/3 | request_details, request_details, request_details |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | shortlist, shortlist, shortlist |

### openai-decisions/spoken-slide-selection

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 354.259 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | opening_context, opening_context, opening_context |
| clear-02 | 3/3 | system_design, system_design, system_design |
| clear-03 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-04 | 3/3 | next_steps, next_steps, next_steps |
| clear-05 | 3/3 | opening_context, opening_context, opening_context |
| clear-06 | 3/3 | system_design, system_design, system_design |
| clear-07 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-08 | 3/3 | next_steps, next_steps, next_steps |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | opening_context, opening_context, opening_context |

### openai-decisions/spreadsheet-urgency

**Partial**. Clear: 6/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 307.369 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-02 | 0/3 | review, review, review |
| clear-03 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | soon, soon, soon |
| clear-06 | 3/3 | soon, soon, soon |
| clear-07 | 3/3 | urgent, urgent, urgent |
| clear-08 | 3/3 | urgent, urgent, urgent |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | urgent, urgent, urgent |

### openai-decisions/suspicious-email-escalation

**Working**. Clear: 8/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 308.552 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-02 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-03 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-04 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-05 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-06 | 3/3 | uncertain_signal, uncertain_signal, uncertain_signal |
| clear-07 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-08 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | security_escalation, security_escalation, security_escalation |

### openai-decisions/template-field-matching

**Partial**. Clear: 7/8; stable: 12/12; models: gpt-6-luna; live calls: 33; median latency: 313.541 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-02 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-03 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-04 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-05 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-06 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-07 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-08 | 0/3 | review, review, review |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | direct_mapping, direct_mapping, direct_mapping |

### sage/ad-funnel-classification

**Partial**. Clear: 7/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 793.388 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | awareness, awareness, awareness |
| clear-02 | 3/3 | consideration, consideration, consideration |
| clear-03 | 3/3 | conversion, conversion, conversion |
| clear-04 | 0/3 | review, review, review |
| clear-05 | 3/3 | consideration, consideration, consideration |
| clear-06 | 3/3 | conversion, conversion, conversion |
| clear-07 | 3/3 | awareness, awareness, awareness |
| clear-08 | 3/3 | consideration, consideration, consideration |
| ambiguous-01 | 0/3 | consideration, consideration, consideration |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | awareness, awareness, awareness |

### sage/agent-workflow-routing

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 941.467 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | payment_help, payment_help, payment_help |
| clear-02 | 3/3 | product_help, product_help, product_help |
| clear-03 | 3/3 | setup_help, setup_help, setup_help |
| clear-04 | 3/3 | payment_help, payment_help, payment_help |
| clear-05 | 3/3 | product_help, product_help, product_help |
| clear-06 | 3/3 | setup_help, setup_help, setup_help |
| clear-07 | 3/3 | payment_help, payment_help, payment_help |
| clear-08 | 3/3 | product_help, product_help, product_help |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | payment_help, payment_help, payment_help |

### sage/brand-news-matching

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 353.67 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | relevant, relevant, relevant |
| clear-02 | 3/3 | relevant, relevant, relevant |
| clear-03 | 3/3 | relevant, relevant, relevant |
| clear-04 | 3/3 | relevant, relevant, relevant |
| clear-05 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-06 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-07 | 3/3 | not_relevant, not_relevant, not_relevant |
| clear-08 | 3/3 | not_relevant, not_relevant, not_relevant |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | relevant, relevant, relevant |

### sage/browser-action-selection

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 324.956 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | click, click, click |
| clear-02 | 3/3 | click, click, click |
| clear-03 | 3/3 | click, click, click |
| clear-04 | 3/3 | click, click, click |
| clear-05 | 3/3 | type, type, type |
| clear-06 | 3/3 | type, type, type |
| clear-07 | 3/3 | type, type, type |
| clear-08 | 3/3 | type, type, type |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | click, click, click |

### sage/content-revision-gate

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 345.54 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | ready, ready, ready |
| clear-02 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| clear-03 | 3/3 | substantial_revision, substantial_revision, substantial_revision |
| clear-04 | 3/3 | ready, ready, ready |
| clear-05 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| clear-06 | 3/3 | substantial_revision, substantial_revision, substantial_revision |
| clear-07 | 3/3 | ready, ready, ready |
| clear-08 | 3/3 | targeted_revision, targeted_revision, targeted_revision |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | ready, ready, ready |

### sage/draft-quality-triage

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 340.259 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | ready, ready, ready |
| clear-02 | 3/3 | ready, ready, ready |
| clear-03 | 3/3 | ready, ready, ready |
| clear-04 | 3/3 | ready, ready, ready |
| clear-05 | 3/3 | revise, revise, revise |
| clear-06 | 3/3 | revise, revise, revise |
| clear-07 | 3/3 | revise, revise, revise |
| clear-08 | 3/3 | revise, revise, revise |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | ready, ready, ready |

### sage/email-queue-routing

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 345.753 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | billing, billing, billing |
| clear-02 | 3/3 | billing, billing, billing |
| clear-03 | 3/3 | billing, billing, billing |
| clear-04 | 3/3 | billing, billing, billing |
| clear-05 | 3/3 | account_support, account_support, account_support |
| clear-06 | 3/3 | account_support, account_support, account_support |
| clear-07 | 3/3 | account_support, account_support, account_support |
| clear-08 | 3/3 | account_support, account_support, account_support |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | account_support, account_support, account_support |

### sage/invoice-file-triage

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 313.207 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | invoice, invoice, invoice |
| clear-02 | 3/3 | invoice, invoice, invoice |
| clear-03 | 3/3 | invoice, invoice, invoice |
| clear-04 | 3/3 | invoice, invoice, invoice |
| clear-05 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-06 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-07 | 3/3 | not_invoice, not_invoice, not_invoice |
| clear-08 | 3/3 | not_invoice, not_invoice, not_invoice |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | invoice, invoice, invoice |

### sage/model-tier-routing

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 326.783 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | fast, fast, fast |
| clear-02 | 3/3 | fast, fast, fast |
| clear-03 | 3/3 | fast, fast, fast |
| clear-04 | 3/3 | reasoning, reasoning, reasoning |
| clear-05 | 3/3 | reasoning, reasoning, reasoning |
| clear-06 | 3/3 | reasoning, reasoning, reasoning |
| clear-07 | 3/3 | specialist, specialist, specialist |
| clear-08 | 3/3 | specialist, specialist, specialist |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | reasoning, reasoning, reasoning |

### sage/outfit-option-selection

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 326.698 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-02 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-03 | 3/3 | light_kit, light_kit, light_kit |
| clear-04 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-05 | 3/3 | formal_kit, formal_kit, formal_kit |
| clear-06 | 3/3 | light_kit, light_kit, light_kit |
| clear-07 | 3/3 | rain_kit, rain_kit, rain_kit |
| clear-08 | 3/3 | formal_kit, formal_kit, formal_kit |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | rain_kit, rain_kit, rain_kit |

### sage/page-change-triage

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 322.639 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | material, material, material |
| clear-02 | 3/3 | material, material, material |
| clear-03 | 3/3 | material, material, material |
| clear-04 | 3/3 | material, material, material |
| clear-05 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-06 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-07 | 3/3 | cosmetic, cosmetic, cosmetic |
| clear-08 | 3/3 | cosmetic, cosmetic, cosmetic |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | material, material, material |

### sage/research-source-filter

**Partial**. Clear: 7/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 309.806 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | include, include, include |
| clear-02 | 3/3 | exclude, exclude, exclude |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 3/3 | include, include, include |
| clear-05 | 3/3 | exclude, exclude, exclude |
| clear-06 | 3/3 | verify_first, verify_first, verify_first |
| clear-07 | 3/3 | include, include, include |
| clear-08 | 3/3 | exclude, exclude, exclude |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | include, include, include |

### sage/retrieved-instruction-screening

**Partial**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 331.313 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | quarantine, quarantine, quarantine |
| clear-02 | 3/3 | quarantine, quarantine, quarantine |
| clear-03 | 3/3 | quarantine, quarantine, quarantine |
| clear-04 | 3/3 | quarantine, quarantine, quarantine |
| clear-05 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-06 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-07 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| clear-08 | 3/3 | use_as_evidence, use_as_evidence, use_as_evidence |
| ambiguous-01 | 0/3 | quarantine, quarantine, quarantine |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission | 3/3 | None, None, None |
| adversarial-injection | 3/3 | quarantine, quarantine, quarantine |

### sage/secondhand-listing-fit

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 342.101 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | shortlist, shortlist, shortlist |
| clear-02 | 3/3 | pass_over, pass_over, pass_over |
| clear-03 | 3/3 | request_details, request_details, request_details |
| clear-04 | 3/3 | shortlist, shortlist, shortlist |
| clear-05 | 3/3 | pass_over, pass_over, pass_over |
| clear-06 | 3/3 | request_details, request_details, request_details |
| clear-07 | 3/3 | shortlist, shortlist, shortlist |
| clear-08 | 3/3 | pass_over, pass_over, pass_over |
| ambiguous-01 | 3/3 | request_details, request_details, request_details |
| ambiguous-02 | 3/3 | request_details, request_details, request_details |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | shortlist, shortlist, shortlist |

### sage/spoken-slide-selection

**Partial**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 328.271 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | opening_context, opening_context, opening_context |
| clear-02 | 3/3 | system_design, system_design, system_design |
| clear-03 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-04 | 3/3 | next_steps, next_steps, next_steps |
| clear-05 | 3/3 | opening_context, opening_context, opening_context |
| clear-06 | 3/3 | system_design, system_design, system_design |
| clear-07 | 3/3 | evidence_results, evidence_results, evidence_results |
| clear-08 | 3/3 | next_steps, next_steps, next_steps |
| ambiguous-01 | 0/3 | next_steps, next_steps, next_steps |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | opening_context, opening_context, opening_context |

### sage/spreadsheet-urgency

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 318.61 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-02 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-03 | 3/3 | no_follow_up, no_follow_up, no_follow_up |
| clear-04 | 3/3 | soon, soon, soon |
| clear-05 | 3/3 | soon, soon, soon |
| clear-06 | 3/3 | soon, soon, soon |
| clear-07 | 3/3 | urgent, urgent, urgent |
| clear-08 | 3/3 | urgent, urgent, urgent |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| adversarial-permission-denied | 3/3 | None, None, None |
| adversarial-injection | 3/3 | urgent, urgent, urgent |

### sage/suspicious-email-escalation

**Partial**. Clear: 6/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 388.844 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-02 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-03 | 0/3 | review, review, review |
| clear-04 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-05 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| clear-06 | 0/3 | review, review, review |
| clear-07 | 3/3 | security_escalation, security_escalation, security_escalation |
| clear-08 | 3/3 | ordinary_correspondence, ordinary_correspondence, ordinary_correspondence |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | security_escalation, security_escalation, security_escalation |

### sage/template-field-matching

**Working**. Clear: 8/8; stable: 12/12; models: levanto-sage-v1.3; live calls: 33; median latency: 353.332 ms; errors: {}.

| Case | Passes/runs | Outcomes |
|---|---|---|
| clear-01 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-02 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-03 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-04 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-05 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| clear-06 | 3/3 | no_suitable_field, no_suitable_field, no_suitable_field |
| clear-07 | 3/3 | direct_mapping, direct_mapping, direct_mapping |
| clear-08 | 3/3 | derived_mapping, derived_mapping, derived_mapping |
| ambiguous-01 | 3/3 | review, review, review |
| ambiguous-02 | 3/3 | review, review, review |
| permission-denied | 3/3 | None, None, None |
| instruction-injection | 3/3 | direct_mapping, direct_mapping, direct_mapping |

