# Installation and use

## Install the shared CLI

The CLI is a Python package separate from the portable skill folders. Install it from the repository's actual `main` branch:

```sh
python3 -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

For development from a local checkout:

```sh
cd decision-models-skills
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

This installs the `decision-models` executable. It can be run from any current working directory. Commands that refer to repository examples must use paths valid from that directory; use absolute paths when calling it elsewhere. No `PYTHONPATH`, repository-root import, or editable installation is required.

## Use a copied skill folder

Copy one of `skills/input-guardrails`, `skills/model-routing`, `skills/reranking`, `skills/tool-call-gating`, `skills/confidence-gates`, or `skills/output-evaluation` into the destination project. The folder carries its `SKILL.md`, input/demo examples, and acceptance fixtures. It does not carry the package or CLI. Install the shared CLI separately using the command above, then pass paths to the copied examples. From the skill folder, for instance:

```sh
decision-models run reranking \
  --provider jev-openrouter \
  --input examples/input.json \
  --mode demo \
  --demo-answers examples/demo.json
```

## Run a live request

Demo mode requires a hand-authored answer file and never contacts a provider. For live mode, omit `--demo-answers`, specify `--mode live`, and set the chosen provider's key in the process environment:

| Provider name | Environment variable |
| --- | --- |
| `jev-openrouter` | `OPENROUTER_API_KEY` |
| `openai-decisions` | `OPENAI_API_KEY` |
| `sage` | `SAGE_API_KEY` |

Example:

```sh
export SAGE_API_KEY='…'
decision-models run confidence-gates \
  --provider sage \
  --input examples/input.json \
  --mode live
```

The CLI does not load `.env` files. `.env.example` lists variable names only. Never put credentials in a checked-in file. Live calls may incur charges; no paid call is required to run the demo.

## Evaluate and render

From the repository root, the default fixture evaluation is offline:

```sh
decision-models evaluate --repo . --mode demo --output reports/evaluation.json
```

Demo evaluation labels every provider/skill pair `Not tested` and returns exit status 1 by design; hand-authored synthetic answers are not live compatibility evidence. Before any live evaluation, run the offline/packaging verification that creates the required receipt:

```sh
python3 scripts/verify.py
```

To create a Markdown report from its receipt:

```sh
decision-models report --input reports/evaluation.json --output reports/evaluation.md
```

For live evaluation, specify the provider(s), `--mode live`, `--rates reports/rates.json`, and the total budget. The evaluator defaults to three repetitions; those repetitions of the 12 cases per skill are workflow checks, not independent statistical samples. Treat the $5 default live budget as a spending ceiling.
