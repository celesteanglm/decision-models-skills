# Decision Models Skills

Model-agnostic agent skills for bounded decisions, routing, and evaluation. Choose among six core skills and 18 use-case skills, install or reference the folder, and ask your agent to use it.

## Use a skill

Copy a folder from `skills/` or `recipes/` into your agent's supported skill directory, or point the agent at its `SKILL.md`. For example:

> Use the email-queue-routing skill at /path/to/email-queue-routing/SKILL.md. Recommend a queue for this email: “Please explain the duplicate charge on my latest invoice.”

The agent follows the instructions using its current model. If you want a specific decision model or already have a model tool configured, name it in your request. The skill leaves that integration to your agent's existing setup. If a specifically requested integration is unavailable, the agent should explain the missing configuration.

Using these instructions requires no Python installation, API key, package installation, separate CLI, or bundled executable. An optional external model tool has its own runtime, credentials, and access requirements.

## Choose a skill

Both categories use the same `SKILL.md` format:

- **Core skills** in `skills/` describe reusable decision procedures.
- **Use-case skills (recipes)** in `recipes/` include a task-specific decision menu and examples. Their `recipe.json` is optional reference configuration.

Each entrypoint explains the needed evidence, decision procedure, result, and review or escalation behavior. The result is a recommendation; executing an action is a separate request and authorization decision.

### Core skills

| Skill | Use it to | Recorded reference checks |
|---|---|---|
| [input-guardrails](skills/input-guardrails/SKILL.md) | Screen input before a downstream workflow. | [Results](skills/input-guardrails/COMPATIBILITY.md) |
| [model-routing](skills/model-routing/SKILL.md) | Recommend an eligible model for a task. | [Results](skills/model-routing/COMPATIBILITY.md) |
| [reranking](skills/reranking/SKILL.md) | Rank supplied passages by relevance. | [Results](skills/reranking/COMPATIBILITY.md) |
| [tool-call-gating](skills/tool-call-gating/SKILL.md) | Recommend whether a proposed tool call may proceed. | [Results](skills/tool-call-gating/COMPATIBILITY.md) |
| [confidence-gates](skills/confidence-gates/SKILL.md) | Escalate decisions when confidence is insufficient. | [Results](skills/confidence-gates/COMPATIBILITY.md) |
| [output-evaluation](skills/output-evaluation/SKILL.md) | Evaluate supplied output against defined criteria. | [Results](skills/output-evaluation/COMPATIBILITY.md) |

### Use-case skills (recipes)

| Skill | Use it to | Recorded reference checks |
|---|---|---|
| [ad-funnel-classification](recipes/ad-funnel-classification/SKILL.md) | Classify ad copy by the customer-journey stage suggested by its text. | [Results](recipes/ad-funnel-classification/COMPATIBILITY.md) |
| [agent-workflow-routing](recipes/agent-workflow-routing/SKILL.md) | Recommend a configured workflow from an incoming customer request. | [Results](recipes/agent-workflow-routing/COMPATIBILITY.md) |
| [brand-news-matching](recipes/brand-news-matching/SKILL.md) | Classify whether a news item is relevant to a supplied brand brief. | [Results](recipes/brand-news-matching/COMPATIBILITY.md) |
| [browser-action-selection](recipes/browser-action-selection/SKILL.md) | Choose a bounded browser step from the current page and task evidence. | [Results](recipes/browser-action-selection/COMPATIBILITY.md) |
| [content-revision-gate](recipes/content-revision-gate/SKILL.md) | Assess a draft’s clarity and specificity and recommend whether it needs focused revision. | [Results](recipes/content-revision-gate/COMPATIBILITY.md) |
| [draft-quality-triage](recipes/draft-quality-triage/SKILL.md) | Classify a draft against its stated goal and available feedback. | [Results](recipes/draft-quality-triage/COMPATIBILITY.md) |
| [email-queue-routing](recipes/email-queue-routing/SKILL.md) | Recommend a handling queue for one email using its request and context. | [Results](recipes/email-queue-routing/COMPATIBILITY.md) |
| [invoice-file-triage](recipes/invoice-file-triage/SKILL.md) | Recommend whether a file appears to be an invoice and has enough metadata for a safe filing review. | [Results](recipes/invoice-file-triage/COMPATIBILITY.md) |
| [model-tier-routing](recipes/model-tier-routing/SKILL.md) | Choose among supplied model tiers using task complexity and explicit constraints. | [Results](recipes/model-tier-routing/COMPATIBILITY.md) |
| [outfit-option-selection](recipes/outfit-option-selection/SKILL.md) | Select a supplied outfit description using explicit weather and occasion constraints. | [Results](recipes/outfit-option-selection/COMPATIBILITY.md) |
| [page-change-triage](recipes/page-change-triage/SKILL.md) | Compare two supplied page excerpts for a change that matters to the stated monitoring goal. | [Results](recipes/page-change-triage/COMPATIBILITY.md) |
| [research-source-filter](recipes/research-source-filter/SKILL.md) | Assess whether a source excerpt is useful for a stated research brief before synthesis. | [Results](recipes/research-source-filter/COMPATIBILITY.md) |
| [retrieved-instruction-screening](recipes/retrieved-instruction-screening/SKILL.md) | Recommend whether retrieved material should be isolated before use as evidence. | [Results](recipes/retrieved-instruction-screening/COMPATIBILITY.md) |
| [secondhand-listing-fit](recipes/secondhand-listing-fit/SKILL.md) | Compare a used-item listing with explicit purchase criteria and recommend whether it merits attention. | [Results](recipes/secondhand-listing-fit/COMPATIBILITY.md) |
| [spoken-slide-selection](recipes/spoken-slide-selection/SKILL.md) | Recommend which described slide best matches a short spoken passage. | [Results](recipes/spoken-slide-selection/COMPATIBILITY.md) |
| [spreadsheet-urgency](recipes/spreadsheet-urgency/SKILL.md) | Classify a row from its stated deadline, status, and impact. | [Results](recipes/spreadsheet-urgency/COMPATIBILITY.md) |
| [suspicious-email-escalation](recipes/suspicious-email-escalation/SKILL.md) | Classify email text for fraud or phishing indicators and identify when security review is warranted. | [Results](recipes/suspicious-email-escalation/COMPATIBILITY.md) |
| [template-field-matching](recipes/template-field-matching/SKILL.md) | Recommend source fields that can populate requested template fields based on names and supplied definitions. | [Results](recipes/template-field-matching/COMPATIBILITY.md) |


## Plug in a model

The instructions define what to assess and what to return. They do not select a vendor, endpoint, or executable.

- Use the agent's current model for a qualitative decision based on the supplied evidence.
- Request an existing model/tool integration when you want to delegate the judgment. Preserve the user's chosen model and tool configuration.
- Require numerical gates only when the chosen integration supplies the needed native metric. Missing required metrics lead to review or escalation; the agent must not invent probabilities or reinterpret self-reported confidence as calibration.

For example:

> Use the input-guardrails skill to assess this prompt against the supplied policy. Use my configured decision-model tool, and return review if it cannot supply the probability required by my policy.

## What each folder contains

```text
<skill>/
├── SKILL.md                 Self-contained instructions for the agent
├── COMPATIBILITY.md         Recorded optional-reference checks and limitations
├── compatibility.json       Machine-readable reference evidence
├── examples/                Illustrative inputs and synthetic reference answers
├── fixtures/acceptance.json Frozen reference-implementation evaluation cases
└── recipe.json              Optional reference configuration (recipes only)
```

The inputs may be supplied naturally; the JSON examples illustrate information to provide, not a required transport format. Expected fixture labels and synthetic demo answers are maintainer evaluation material, not evidence for a live decision.

## What has been tested

Each folder's compatibility page records exact models, pass counts, failures, dates, and evidence links for the optional Python reference implementation against native decision APIs. Working labels apply to that evaluated implementation and its frozen artifacts.

Those historical receipts do not benchmark the revised instruction-only skills on an arbitrary agent or model. The instructions are model-agnostic; decision quality still depends on the model, evidence, and task. No listed backend is required to use a skill.

## Maintain the reference implementation

`src/decision_models/` contains optional Python code used to reproduce API contracts, numerical policies, and reference evaluation. It is maintainer tooling; agents using the Markdown skills do not install or import it. The package exposes no global console command.

See [Contributing](CONTRIBUTING.md) for folder validation and optional Python checks, [Recipe contract](RECIPE_CONTRACT.md) for reference configuration, [Implementation contract](IMPLEMENTATION_CONTRACT.md) for the optional adapters, and [Attribution](ATTRIBUTION.md) for original sources.

Working docs and research stay local and ignored. Raw test outputs go to ignored `reports/` or CI artifacts; compact reference evidence stays beside each skill.
