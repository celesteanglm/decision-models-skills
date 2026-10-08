# Decision Models Skills

Six small Python workflows turn a defined decision into a structured provider request, validate the response, and apply a documented policy. The supported workflows are input guardrails, model routing, passage reranking, tool-call gating, confidence gates, and output evaluation.

This project requires Python 3.10 or newer and has no runtime dependencies beyond the Python standard library. It supports Jev through OpenRouter, OpenAI Decisions, and Levanto Sage SystemOne. The shared CLI is installed separately from the portable `skills/<name>/` folders. You can copy a skill folder into another project and use it there once the CLI is installed and available on `PATH`.

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

## Verified results

Live acceptance on 2026-10-08 marks all six Jev/OpenRouter and Sage workflows **Working**. OpenAI Decisions has four **Working** workflows; input guardrails and output evaluation are **Partial**. The [generated compatibility table and per-case evidence](reports/COMPATIBILITY.md) record the resolved models, fixture revision, usage, latency, and repeated-run stability. Reranking evidence covers the requested `top_k=1` and `top_k=2` profiles; it does not certify every full-list configuration.

Clean wheel installs pass 89 tests and 18 copied-skill demos on both Python 3.10 and 3.12. All retained live iterations and smoke calls total approximately **US$0.110 in provider-reported and token-estimated costs**, with US$2.324 conservatively reserved against the US$5 limit. See [cost reconciliation](reports/costs.json) and [evaluation history](docs/evaluation-history.md). Estimates are not provider invoices.

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
