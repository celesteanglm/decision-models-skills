# Installation and use

## Install the shared CLI

Requires Python 3.10+ and Git. Provider credentials are needed only for live mode. An agent host is optional when running the CLI directly.

The CLI is a Python package separate from the portable skill folders. Install it from the repository's actual `main` branch:

```sh
python3 -m pip install 'decision-models-skills @ git+https://github.com/celesteanglm/decision-models-skills.git@main'
```

To obtain the skill folders and install the CLI in a virtual environment:

```sh
git clone https://github.com/celesteanglm/decision-models-skills.git
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

## Install a skill for Codex

The repository's `skills/` directory is a distribution collection. Cloning it or installing the Python package does not automatically activate those folders in an agent. Codex discovers project skills under `.agents/skills/` and user-wide skills under `~/.agents/skills/`. See [OpenAI's skill authoring and discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

For example, from this repository's root, with the CLI installed and its virtual environment activated, copy one skill into an existing project:

```sh
mkdir -p ../my-project/.agents/skills
cp -R skills/input-guardrails ../my-project/.agents/skills/
cd ../my-project
decision-models run input-guardrails \
  --provider jev-openrouter \
  --input .agents/skills/input-guardrails/examples/input.json \
  --mode demo \
  --demo-answers .agents/skills/input-guardrails/examples/demo.json
```

Replace `../my-project` with the destination project. Copy the whole skill folder, including its examples and fixtures. Repeat the copy for other skills as needed. Run Codex in that project and mention `$input-guardrails`, or ask it to perform a task matching the skill description. For example: `Use $input-guardrails to run its supplied example in demo mode with jev-openrouter.` Codex loads `SKILL.md`; the installed CLI performs the workflow. Keep the virtual environment active so the CLI is on `PATH`.

Community recipes use the same folder discovery convention. For example, copy `recipes/context-retention` into `.agents/skills/context-retention`, then invoke `$context-retention` in the agent. Its direct CLI command uses `recipe` and the copied configuration:

```sh
decision-models recipe \
  --recipe .agents/skills/context-retention/recipe.json \
  --provider sage --mode demo \
  --input .agents/skills/context-retention/examples/input.json \
  --demo-answers .agents/skills/context-retention/examples/demo.json
```

Copy the complete recipe folder. Its source links, policy, examples, and fixtures remain available without the research catalog or repository checkout. The shared CLI remains a separate dependency.

To make the skill available across projects, copy it to `~/.agents/skills/input-guardrails` instead. Other agent hosts have their own discovery paths; consult their documentation before copying folders.

## Repository structure and distribution

A folder with a valid `SKILL.md` is sufficient for an instruction-only skill. Add scripts, references, examples, or assets when the workflow needs them. Keep detailed human setup instructions here rather than repeating a tutorial inside every skill. In this collection, the shared CLI is an explicit dependency, and copied skills use local example paths so they work without repository-root imports.

The current repository supports manual folder installation and a separate Python CLI. [OpenAI recommends plugins](https://learn.chatgpt.com/docs/build-skills#distribute-skills-with-plugins) for packaged distribution of reusable skill bundles. Plugin packaging is a separate distribution option; this repository does not currently provide a plugin manifest or one-click plugin installation.

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

For the 29 community recipes, use a new output filename for each immutable run:

```sh
decision-models evaluate-recipes --repo . --mode demo \
  --providers jev-openrouter openai-decisions sage \
  --output reports/recipe-demo.json
```

Recipe demo evaluation exits successfully and labels all compatibility cells `Not tested`. Live mode requires the current offline receipt and a reviewed rates file. It preflights complete coverage before dispatch; `--budget 1.5` covered all three backends at the recorded rates. It writes an append-only attempt journal plus consolidated JSON and Markdown receipts. A live run with any cell below Working exits 1 while preserving evidence. The default recipe budget is US$1; a run that cannot fit dispatches no requests.
