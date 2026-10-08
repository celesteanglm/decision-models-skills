# Decision Models Skills

Portable skills and community recipes for small-model decisions, routing, and evaluation.

Six small Python workflows turn a defined decision into a structured provider request, validate the response, and apply a documented policy. The supported workflows are input guardrails, model routing, passage reranking, tool-call gating, confidence gates, and output evaluation.

This project requires Python 3.10 or newer and has no runtime dependencies beyond the Python standard library. It includes native adapters for Jev through OpenRouter, OpenAI Decisions, and Levanto Sage SystemOne. Use each skill’s Working labels to select a verified backend. The shared CLI is installed separately from the portable `skills/<name>/` folders. You can copy a skill folder into another project and use it there once the CLI is installed and available on `PATH`.

Every result is a recommendation for the calling application. These workflows do not execute tools, select and invoke a model, publish content, or apply a decision. The initial thresholds are workflow-specific, provider-specific starting values and have not been calibrated. Review and calibrate them on a representative development set before relying on them in production.

## What a skill contains

A skill is a folder of instructions that an agent loads when the task matches its description. `SKILL.md` is the required entrypoint: YAML `name` and `description` tell the agent when to use it, and the Markdown body explains the inputs, workflow, and outputs. Supporting files are optional. These skills include runnable examples and acceptance fixtures because they call a shared, tested Python implementation.

```text
skills/input-guardrails/
├── SKILL.md                 Agent instructions and when to use them
├── examples/input.json      Example workflow input
├── examples/demo.json       Synthetic answers for a credential-free demo
└── fixtures/acceptance.json Evaluation cases and expected outcomes
```

The repository README explains setup for people; each `SKILL.md` contains instructions for an agent. Installing the Python package supplies the CLI. Copying a skill folder supplies the agent instructions. Both are needed for these workflows. See [installation and invocation](docs/installation.md) for the complete path from clone to a first demo.

## Community use cases

[18 published decision recipes](research/README.md) cover browser actions, routing, email triage, field matching, page changes, research filtering, and other text workflows. Every included recipe qualified as **Working on at least one backend**. Eleven candidates that qualified on none were removed. Positive labels below identify only passing backends; every other backend is unqualified for that recipe.

The research inspected 36 posts dated 8 September–8 October 2026. The published recipes credit 17 original posts selected using usefulness, reproducibility, source evidence, and timestamped engagement. Games and posts below 100 likes or 10,000 views were excluded. X search required login, so this is a ranked discovered sample.

| Recipe | Working with |
|---|---|
| [ad-funnel-classification](recipes/ad-funnel-classification/SKILL.md) | ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) |
| [agent-workflow-routing](recipes/agent-workflow-routing/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [brand-news-matching](recipes/brand-news-matching/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [browser-action-selection](recipes/browser-action-selection/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [content-revision-gate](recipes/content-revision-gate/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [draft-quality-triage](recipes/draft-quality-triage/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [email-queue-routing](recipes/email-queue-routing/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [invoice-file-triage](recipes/invoice-file-triage/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [model-tier-routing](recipes/model-tier-routing/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [outfit-option-selection](recipes/outfit-option-selection/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [page-change-triage](recipes/page-change-triage/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [research-source-filter](recipes/research-source-filter/SKILL.md) | ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) |
| [retrieved-instruction-screening](recipes/retrieved-instruction-screening/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) |
| [secondhand-listing-fit](recipes/secondhand-listing-fit/SKILL.md) | ![Jev / OpenRouter: Working](https://img.shields.io/badge/Jev%20%2F%20OpenRouter-Working-brightgreen) ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [spoken-slide-selection](recipes/spoken-slide-selection/SKILL.md) | ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) |
| [spreadsheet-urgency](recipes/spreadsheet-urgency/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |
| [suspicious-email-escalation](recipes/suspicious-email-escalation/SKILL.md) | ![Decisions API: Working](https://img.shields.io/badge/Decisions%20API-Working-brightgreen) |
| [template-field-matching](recipes/template-field-matching/SKILL.md) | ![Sage: Working](https://img.shields.io/badge/Sage-Working-brightgreen) |

Each copied folder includes `SKILL.md`, local `COMPATIBILITY.md`, trusted `recipe.json`, examples, frozen fixtures, and original source links. The compatibility page names the exact tested models and non-qualifying backends. These are independently authored text recommendations inspired by credited authors.

```sh
decision-models recipe \
  --recipe recipes/email-queue-routing/recipe.json \
  --provider sage --mode demo \
  --input recipes/email-queue-routing/examples/input.json \
  --demo-answers recipes/email-queue-routing/examples/demo.json
```

For live mode, select a backend labeled Working for that recipe, omit `--demo-answers`, set its environment credential, and pass `--mode live`. Copy the whole folder and use absolute paths from another directory. See [installation](docs/installation.md), [full Working-label catalog](reports/VERIFIED_CATALOG.md), [per-case evidence](reports/community-recipes.md), and [other model adapters](docs/model-adapters.md).

## Verification

The retained recipes have **7 Jev/OpenRouter**, **8 Decisions API**, and **13 Sage** Working labels. Workflow routing, email queue routing, and listing fit qualify on all three. Partial results receive no Working label. The [qualification registry](reports/catalog.json) enforces that every published recipe has a passing backend and that labels match the live receipts.

The six core workflows also carry per-folder labels: Jev/OpenRouter and Sage qualify on all six; Decisions qualifies on model routing, reranking, tool-call gating, and confidence gates. Its input guardrails and output evaluation did not qualify. See [core evidence](reports/COMPATIBILITY.md).

Qualification uses the original frozen 12-case × 3-run evaluation on unchanged artifacts. The original candidate run made 2,871 real API calls; excluded candidates remain in historical audit receipts. Catalog pruning and label corrections made no additional paid calls. Synthetic acceptance and repeated-run stability do not establish production accuracy or calibration.

Clean installations pass 112 tests and 44 demos of labeled skill/backend pairs on Python 3.10 and 3.12. [Offline evidence](reports/catalog-offline.json) covers copied-folder portability, inclusion rules, backend labels, and unchanged evaluated artifacts. All retained live iterations total approximately **US$0.206 reported/estimated**, with **US$4.537 conservatively reserved** under US$5. See [cost reconciliation](reports/costs.json) and [evaluation history](docs/evaluation-history.md).

## Install the CLI

From any directory, install the package directly from the repository's `main` branch:

```sh
python3 -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

To download the skill folders as well, clone the repository and install in a virtual environment:

```sh
git clone https://github.com/celesteanglm/decision-models-skills.git
cd decision-models-skills
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

The install creates the `decision-models` command. You do not need to run from the repository root, set `PYTHONPATH`, or use an editable install. A copied skill folder contains instructions and JSON examples, but not the shared Python package or CLI; install the CLI separately as above.

## Run an offline demo

From the repository root, for example:

```sh
decision-models run input-guardrails \
  --provider jev-openrouter \
  --input skills/input-guardrails/examples/input.json \
  --mode demo \
  --demo-answers skills/input-guardrails/examples/demo.json
```

The demo answer files are hand-authored synthetic examples. Demo mode makes no provider call and the CLI labels the result as synthetic. They illustrate the workflow shape; they are not model outputs, evaluation evidence, or an accuracy claim. From a copied skill directory, the relative paths can instead be `examples/input.json` and `examples/demo.json`.

## Make a live request

Set only the key for the selected provider in the environment, then omit `--demo-answers` and explicitly choose `--mode live`:

```sh
export OPENROUTER_API_KEY='…'
decision-models run input-guardrails \
  --provider jev-openrouter \
  --input skills/input-guardrails/examples/input.json \
  --mode live
```

The other keys are `OPENAI_API_KEY` for `openai-decisions` and `SAGE_API_KEY` for `sage`. See [`.env.example`](.env.example) for the names. The program reads keys from process environment variables; it does not load `.env` files. Do not commit secrets. Live requests can incur provider charges.

The exact endpoint, default model, and response mapping contract are listed in [Compatibility](docs/compatibility.md). Provider endpoints, model access, and response behavior can change; consult the generated [compatibility report](reports/COMPATIBILITY.md) for the evidence actually collected in this checkout. Its statuses describe only the checks recorded there.

## Evaluate fixtures

Each skill has 12 frozen acceptance cases: eight clear, two ambiguous, and two adversarial. The expected outcomes are evaluation metadata and are not sent as model input. Evaluation defaults to demo mode, three repetitions, and a $5 budget for live mode:

```sh
decision-models evaluate \
  --repo . \
  --providers jev-openrouter openai-decisions sage \
  --mode demo \
  --repetitions 3 \
  --output reports/evaluation.json
```

The 12 cases and their three repetitions are workflow checks, not 36 independent statistical samples. For live evaluation, review the current provider rates and provide a rates JSON file with `--rates reports/rates.json`; the configured total budget is a guardrail, not a prediction of final cost. No paid requests are needed for the documented demos.

Demo evaluation intentionally reports providers as `Not tested` and exits with status 1 because demo answers are synthetic, not live compatibility evidence. Run `python3 scripts/verify.py` before any live evaluation; it creates the offline/packaging receipt required by the live evaluator.

To render a report from an evaluation receipt:

```sh
decision-models report --input reports/evaluation.json --output reports/evaluation.md
```

See [`docs/installation.md`](docs/installation.md) for copy-and-install details, [`docs/compatibility.md`](docs/compatibility.md) for wire contracts and evidence boundaries, and [`ATTRIBUTION.md`](ATTRIBUTION.md) for source and license notes.
