# Decision Models Skills

Agent skills for small-model decisions: six reusable workflows and 18 ready-to-run use cases, backed by a shared Python CLI.

Every skill recommends a bounded decision from supplied evidence. The calling application applies that recommendation. Python 3.10+ is required; the runtime uses only the standard library.

## Install and try a skill

Clone the repository and install the shared CLI:

```sh
git clone https://github.com/celesteanglm/decision-models-skills.git
cd decision-models-skills
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .

decision-models run input-guardrails \
  --provider jev-openrouter --mode demo \
  --input skills/input-guardrails/examples/input.json \
  --demo-answers skills/input-guardrails/examples/demo.json
```

Demo mode uses hand-authored synthetic answers and makes no API requests. It demonstrates the interface; it provides no model-quality evidence.

To use a copied skill folder in another project, install the CLI separately:

```sh
python -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

Copy the whole skill folder into your agent's skill directory, for example `.agents/skills/<name>/`. The agent reads its `SKILL.md`; the installed package supplies the `decision-models` command. Run from the copied folder or pass absolute paths to its examples and configuration. No repository-root imports or editable install are required.

## Choose a skill

Both categories use the same agent skill format:

- **Core skills** in `skills/` provide reusable workflows with dedicated input contracts. Run them with `decision-models run <name>`.
- **Use-case skills (recipes)** in `recipes/` specialize a decision using local `recipe.json` configuration. Run them with `decision-models recipe --recipe <path>`.

Open a skill's instructions to see its Working backend labels. Its compatibility page lists every tested backend, exact models, pass counts, failures, and test date.

### Core skills

| Skill | Use it to | Compatibility |
|---|---|---|
| [input-guardrails](skills/input-guardrails/SKILL.md) | Screen input before a downstream workflow. | [Results](skills/input-guardrails/COMPATIBILITY.md) |
| [model-routing](skills/model-routing/SKILL.md) | Recommend an eligible model for a task. | [Results](skills/model-routing/COMPATIBILITY.md) |
| [reranking](skills/reranking/SKILL.md) | Rank supplied passages by relevance. | [Results](skills/reranking/COMPATIBILITY.md) |
| [tool-call-gating](skills/tool-call-gating/SKILL.md) | Recommend whether a proposed tool call may proceed. | [Results](skills/tool-call-gating/COMPATIBILITY.md) |
| [confidence-gates](skills/confidence-gates/SKILL.md) | Escalate decisions when confidence is insufficient. | [Results](skills/confidence-gates/COMPATIBILITY.md) |
| [output-evaluation](skills/output-evaluation/SKILL.md) | Evaluate supplied output against defined criteria. | [Results](skills/output-evaluation/COMPATIBILITY.md) |

### Use-case skills (recipes)

| Skill | Use it to | Compatibility |
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

For example:

```sh
decision-models recipe \
  --recipe recipes/email-queue-routing/recipe.json \
  --provider sage --mode demo \
  --input recipes/email-queue-routing/examples/input.json \
  --demo-answers recipes/email-queue-routing/examples/demo.json
```

## Make a live request

Choose a backend labeled Working for the specific skill. Set its credential in the process environment, use `--mode live`, and omit `--demo-answers`:

```sh
export OPENROUTER_API_KEY='…'
decision-models run input-guardrails \
  --provider jev-openrouter --mode live \
  --input skills/input-guardrails/examples/input.json
```

| Provider flag | Credential variable | Native protocol |
|---|---|---|
| `jev-openrouter` | `OPENROUTER_API_KEY` | [OpenRouter Decisions](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request) |
| `openai-decisions` | `OPENAI_API_KEY` | [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions) |
| `sage` | `SAGE_API_KEY` | [Sage SystemOne](https://docs.levanto.ai/systemone) |

The program does not load `.env` files. Live requests can incur provider charges. `--model` selects a model implementing the chosen adapter's protocol; other models require their own adapter and evaluation. The [implementation contract](IMPLEMENTATION_CONTRACT.md) describes the adapter interface.

## What each skill contains

```text
<skill>/
├── SKILL.md                 Instructions, inputs, usage, Working backends
├── COMPATIBILITY.md         Human-readable results and failures
├── compatibility.json       Test summaries, models, revisions, evidence link
├── examples/                Sample input and synthetic demo answers
├── fixtures/acceptance.json Frozen evaluation cases
└── recipe.json              Use-case configuration (recipes only)
```

Compatibility is specific to the tested runtime, configuration, fixtures, and resolved model. Working means the backend met the documented synthetic acceptance gate; Partial, Blocked, and Not tested do not qualify. These results establish neither production accuracy nor calibrated confidence thresholds.

## Verify or contribute

```sh
python scripts/verify.py
python scripts/check_release.py
```

Offline verification checks tests, copied-folder demos, local compatibility summaries, backend labels, and the hashes of evaluated artifacts. It makes no provider requests and requires no archived test runs. To audit summaries against retained raw evidence, download the linked run and pass `--receipt /path/to/run.json` to `scripts/verified_catalog.py`.

[Contributing](CONTRIBUTING.md) covers live evaluation, reviewed rates, and publishing skill-local summaries. [Recipe contract](RECIPE_CONTRACT.md) defines use-case configuration and acceptance criteria. [Attribution](ATTRIBUTION.md) credits original sources.

Working docs and research stay local and ignored. Raw test outputs are generated under ignored `reports/` and uploaded by CI as artifacts; the public source tree retains the compact compatibility files beside each skill. Historical evidence links use immutable commits. Retain future release evidence as versioned release assets when it must outlive CI artifact retention.
