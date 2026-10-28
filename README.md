# Decision Models Skills

Model-agnostic agent skills for bounded decisions, routing, and evaluation. Choose among six general skills and 21 use-case skills, install or reference the folder, and ask your agent to use it.

## Start here

The skills are portable instructions: the same self-contained folder can guide different agents and decision-model integrations. Start with the `SKILL.md`; a provider or package is optional.

1. **Choose the task and check its evidence.** Browse the groups below and open the skill that matches your task. Read its `SKILL.md` and `COMPATIBILITY.md` to understand required inputs, review behavior, and exactly which backend and model were checked. A compatibility result applies to the recorded integration and artifacts; it does not guarantee the same result on every model.
2. **Get or copy the complete folder.** Clone or download this repository, then copy the complete `skills/<skill-id>/` folder to a skill directory supported by your agent. Include examples, local assets, and other referenced files. If your agent can use a file directly, point it to `skills/<skill-id>/SKILL.md` instead.
3. **Give the agent your own input and criteria.** Describe the task and the evidence to consider in plain language. State what a good result means and any constraints. The JSON example illustrates the fields; it is optional unless your integration requires JSON. Keep examples and expected fixture answers separate from real decision evidence.
4. **Choose how to make the decision.** Let the agent use its current model for qualitative use, or request a decision-model tool that is already configured in your agent. Naming a model does not connect an API, provide credentials, or switch the model running your agent conversation. If the requested integration is not configured, ask the agent to identify what is missing instead of silently substituting another backend.
5. **Try a harmless example and inspect the result.** Start with the skill's sample or another low-stakes input. Compare the answer with the skill's decision menu and review rules. For a backend, check `COMPATIBILITY.md` for its exact model, date, native metrics, and limitations; do not treat a result from one backend as proof for another. For a skill that requires an image, use an agent or backend that accepts and can inspect image inputs.

Using `SKILL.md` with the agent's current model requires no Python installation, API key, package, separate CLI, or bundled executable. If you connect an API directly, keep its key in an environment variable, not in prompts or source files.

### Try it with a configured model

Replace the path and model tool in this example:

```text
Use /path/to/email-queue-routing/SKILL.md.
Make the decision with my configured Jev/OpenRouter tool.
Input: "I was billed twice for the same order. Which queue should handle this?"
Return the recommendation and reason. Do not send an email or take an action.
If the tool is unavailable, explain the missing setup. Do not substitute another provider.
```

To try the skill before connecting an API, replace the model-tool line with "Use your current model."

For this example, the expected recommendation is `billing` because the email describes a duplicate charge. The skill returns a recommendation without sending a message.

To try another model, change the model-tool line and keep the task, input, and skill rules the same. Run your example again and compare the outcome. A Working label from one backend does not transfer to the new one.

### Optional: connect a custom provider

The complete [offline custom-provider example](examples/custom_provider/README.md) shows the request and response mapping for a fictional fourth backend. It runs with the copied `email-queue-routing` skill from any working directory and needs no API key or network access. Its responses are synthetic, not evidence about a real provider.

### Connect a provider once

Your agent needs a configured model tool, or you can connect an adapter in your own application. An API key alone does not create that connection. Ask your coding agent to follow the [adapter guide](CONTRIBUTING.md#add-a-model-adapter) when connecting a new provider.

The optional Python tools use these environment variables:

| Provider | Environment variable | Setup reference |
|---|---|---|
| Jev through OpenRouter | `OPENROUTER_API_KEY` | [OpenRouter API](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request) |
| OpenAI Decisions API | `OPENAI_API_KEY` | [Decisions API guide](https://developers.openai.com/api/docs/guides/decisions) |
| Sage | `SAGE_API_KEY` | [Sage quickstart](https://docs.levanto.ai/decision-model/quickstart) |

Keep keys in the environment. Do not paste them into prompts or commit them. Your agent's connector may use its own credential setup. Check the chosen skill's results before selecting a backend and model version.

The built-in Jev/OpenRouter and Sage adapters can be called from your own application with an explicit model and environment-only key. Live calls may incur provider charges; run them only with an authorized budget. After installing this package and copying the skill, set `OPENROUTER_API_KEY` in your process environment and use:

```python
from decision_models.runtime import adapter_for
from decision_models.use_cases import execute_use_case, load_use_case

skill = load_use_case("/path/to/email-queue-routing/decision.json")
data = {"permission_granted": True, "state": {"content": "A customer asks why an invoice was charged twice."}}
result = execute_use_case(skill, "jev-openrouter", data, mode="live",
                          model="typesafe/jev-1.13", adapter=adapter_for("jev-openrouter"))
```

For Sage v1.4, set `SAGE_API_KEY` in the process environment and use the same copied skill and input:

```python
result = execute_use_case(skill, "sage", data, mode="live",
                          model="levanto-sage-v1.4", adapter=adapter_for("sage"))
```

Keep `mode="live"` explicit. Do not put credentials in a prompt, input file, source file, or command history.

For a new connection, give your coding agent this brief:

```text
Connect this copied skill to [provider/model] in my project.
Read its SKILL.md and the Add a model adapter section in CONTRIBUTING.md.
Keep the decision question, labels, permission checks, and review rules unchanged.
Use credentials from the environment and keep integration code outside the skill folder.
Show the request/response mapping and run an offline example first.
Preserve raw answers, usage, native probabilities, and native confidence as distinct fields.
Report unsupported inputs or missing required metrics. Do not invent them.
Before a paid test, show the expected cost and ask for a budget.
```

## Choose a skill

Everything listed below is an installable skill. The two groups differ in scope, not format or installation:

- **General skills** in `skills/` describe reusable decision procedures. Use model routing, for example, when you need to choose a model for a task in your own application.
- **Use-case skills** in `skills/` apply a decision procedure to a specific task. Study-tool selection, for example, chooses among flashcards, quizzes, summaries, and other study activities.

Both groups live under `skills/` and have self-contained `SKILL.md` instructions, local examples, and compatibility evidence. A text use-case skill may include `decision.json`; an image skill may include `image.json` and local images. These files support optional reference checks. The agent follows `SKILL.md` without installing the Python tools.

Each entrypoint explains the needed evidence, decision procedure, result, and review or escalation behavior. The result is a recommendation; executing an action is a separate request and authorization decision.

### General skills

| Skill | Use it to | Recorded reference checks |
|---|---|---|
| [input-guardrails](skills/input-guardrails/SKILL.md) | Screen input before a downstream workflow. | [Results](skills/input-guardrails/COMPATIBILITY.md) |
| [model-routing](skills/model-routing/SKILL.md) | Recommend an eligible model for a task. | [Results](skills/model-routing/COMPATIBILITY.md) |
| [reranking](skills/reranking/SKILL.md) | Rank supplied passages by relevance. | [Results](skills/reranking/COMPATIBILITY.md) |
| [tool-call-gating](skills/tool-call-gating/SKILL.md) | Recommend whether a proposed tool call may proceed. | [Results](skills/tool-call-gating/COMPATIBILITY.md) |
| [confidence-gates](skills/confidence-gates/SKILL.md) | Escalate decisions when confidence is insufficient. | [Results](skills/confidence-gates/COMPATIBILITY.md) |
| [output-evaluation](skills/output-evaluation/SKILL.md) | Evaluate supplied output against defined criteria. | [Results](skills/output-evaluation/COMPATIBILITY.md) |

### Use-case skills

| Skill | Use it to | Recorded reference checks |
|---|---|---|
| [ad-funnel-classification](skills/ad-funnel-classification/SKILL.md) | Classify ad copy by the customer-journey stage suggested by its text. | [Results](skills/ad-funnel-classification/COMPATIBILITY.md) |
| [agent-workflow-routing](skills/agent-workflow-routing/SKILL.md) | Recommend a configured workflow from an incoming customer request. | [Results](skills/agent-workflow-routing/COMPATIBILITY.md) |
| [brand-news-matching](skills/brand-news-matching/SKILL.md) | Classify whether a news item is relevant to a supplied brand brief. | [Results](skills/brand-news-matching/COMPATIBILITY.md) |
| [browser-action-selection](skills/browser-action-selection/SKILL.md) | Choose a bounded browser step from the current page and task evidence. | [Results](skills/browser-action-selection/COMPATIBILITY.md) |
| [content-revision-gate](skills/content-revision-gate/SKILL.md) | Assess a draft’s clarity and specificity and recommend whether it needs focused revision. | [Results](skills/content-revision-gate/COMPATIBILITY.md) |
| [draft-quality-triage](skills/draft-quality-triage/SKILL.md) | Classify a draft against its stated goal and available feedback. | [Results](skills/draft-quality-triage/COMPATIBILITY.md) |
| [email-queue-routing](skills/email-queue-routing/SKILL.md) | Recommend a handling queue for one email using its request and context. | [Results](skills/email-queue-routing/COMPATIBILITY.md) |
| [invoice-file-triage](skills/invoice-file-triage/SKILL.md) | Recommend whether a file appears to be an invoice and has enough metadata for a safe filing review. | [Results](skills/invoice-file-triage/COMPATIBILITY.md) |
| [model-tier-routing](skills/model-tier-routing/SKILL.md) | Choose among supplied model tiers using task complexity and explicit constraints. | [Results](skills/model-tier-routing/COMPATIBILITY.md) |
| [outfit-option-selection](skills/outfit-option-selection/SKILL.md) | Select a supplied outfit description using explicit weather and occasion constraints. | [Results](skills/outfit-option-selection/COMPATIBILITY.md) |
| [page-change-triage](skills/page-change-triage/SKILL.md) | Compare two supplied page excerpts for a change that matters to the stated monitoring goal. | [Results](skills/page-change-triage/COMPATIBILITY.md) |
| [research-enrichment-gate](skills/research-enrichment-gate/SKILL.md) | Recommend whether supplied research evidence can be reused or needs refreshing. | [Results](skills/research-enrichment-gate/COMPATIBILITY.md) |
| [research-source-filter](skills/research-source-filter/SKILL.md) | Assess whether a source excerpt is useful for a stated research brief before synthesis. | [Results](skills/research-source-filter/COMPATIBILITY.md) |
| [retrieved-instruction-screening](skills/retrieved-instruction-screening/SKILL.md) | Recommend whether retrieved material should be isolated before use as evidence. | [Results](skills/retrieved-instruction-screening/COMPATIBILITY.md) |
| [screenshot-action-check](skills/screenshot-action-check/SKILL.md) | Inspect screenshot pixels for a named button that is visible, clipped, covered, or unclear. | [Results](skills/screenshot-action-check/COMPATIBILITY.md) |
| [secondhand-listing-fit](skills/secondhand-listing-fit/SKILL.md) | Compare a used-item listing with explicit purchase criteria and recommend whether it merits attention. | [Results](skills/secondhand-listing-fit/COMPATIBILITY.md) |
| [spoken-slide-selection](skills/spoken-slide-selection/SKILL.md) | Recommend which described slide best matches a short spoken passage. | [Results](skills/spoken-slide-selection/COMPATIBILITY.md) |
| [spreadsheet-urgency](skills/spreadsheet-urgency/SKILL.md) | Classify a row from its stated deadline, status, and impact. | [Results](skills/spreadsheet-urgency/COMPATIBILITY.md) |
| [study-tool-selection](skills/study-tool-selection/SKILL.md) | Distinguish study-tool requests from ordinary chat and recommend one activity. | [Results](skills/study-tool-selection/COMPATIBILITY.md) |
| [suspicious-email-escalation](skills/suspicious-email-escalation/SKILL.md) | Classify email text for fraud or phishing indicators and identify when security review is warranted. | [Results](skills/suspicious-email-escalation/COMPATIBILITY.md) |
| [template-field-matching](skills/template-field-matching/SKILL.md) | Recommend source fields that can populate requested template fields based on names and supplied definitions. | [Results](skills/template-field-matching/COMPATIBILITY.md) |


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
├── decision.json            Optional text reference configuration
├── image.json               Optional image reference configuration
└── images/                  Local image assets, when needed
```

The inputs may be supplied naturally; the JSON examples illustrate information to provide, not a required transport format. Expected fixture labels and synthetic demo answers are maintainer evaluation material, not evidence for a live decision.

## Use an image skill

Copy `skills/screenshot-action-check/` with its images, then give a vision-capable agent the image and the button to inspect:

```text
Use /path/to/screenshot-action-check/SKILL.md.
Inspect the attached screenshot. Is the CONTINUE button fully visible and unobstructed?
Review if the target is ambiguous or the image is unclear. Do not click anything.
```

The reference workflow qualifies on Sage v1.4 with PNG fixtures. JPEG and WebP handling has offline contract tests; those formats have no live qualification here. Jev/OpenRouter and Decisions API have no image qualification in this repository. Text-only agents must report that they cannot inspect the image.

For optional Python reproduction, install the reference package from this checkout as described in [Contributing](CONTRIBUTING.md), then run from the repository root:

```sh
python scripts/image_reference.py --folder skills/screenshot-action-check \
  --input skills/screenshot-action-check/examples/input.json \
  --mode demo --demo-answers skills/screenshot-action-check/examples/demo.json
```

This demo is offline and uses hand-authored answers. For a real Sage call, set `SAGE_API_KEY`, select `--mode live`, and omit `--demo-answers`. Use an explicitly authorized test budget. The runner accepts PNG, JPEG, and WebP files under the skill folder, or under an explicit `--asset-root`; it rejects remote image URLs and paths that escape that folder.

## What has been tested

Each folder's compatibility page records exact models, pass counts, failures, dates, and evidence links for the optional Python reference implementation against native decision APIs. Working labels apply to that evaluated implementation and its frozen artifacts.

The new study-tool and enrichment-gate reference checks qualify on Sage **v1.4** and Jev/OpenRouter; Decisions API did not qualify. Older Sage v1.3 results are historical: the live deployment rejected that model on 2026-10-27. Exact tested versions and qualifications are recorded beside each skill.

Those historical receipts do not benchmark the revised instruction-only skills on an arbitrary agent or model. The instructions are model-agnostic; decision quality still depends on the model, evidence, and task. No listed backend is required to use a skill.

The unified directory layout was checked offline against 936 frozen provider-request and demo-policy contracts, plus 2,808 replays of archived native responses. Each compatibility page links the migration audit. This preserves the recorded reference results across naming changes; it is not a new live evaluation.

The adapter and error-handling update also matched 948 frozen request and policy checks, 2,598 archived native responses, and 246 deterministic outcomes against the earlier runtime. Each compatibility page links that comparison separately. New providers and model versions still need independent qualification.

## Maintain the reference implementation

`src/decision_models/` contains optional Python code used to reproduce API contracts, numerical policies, and reference evaluation. It is maintainer tooling; agents using the Markdown skills do not install or import it. The package exposes no global console command.

See [Contributing](CONTRIBUTING.md) for validation, model adapters, reference schemas, and compatibility evidence. Original sources are credited [below](#credits-and-license) and within each skill.

## Optional: connect a Python adapter

Start with the [runnable custom-provider example](examples/custom_provider/README.md). It injects a fictional adapter into `execute_use_case`, maps a different request and response format, and demonstrates recommendation, missing-confidence review, and malformed-answer handling offline. No provider registry edits are needed.

For your application, `execute_use_case` and the general `execute` function accept `adapter=MyAdapter()`. The image helper accepts the same argument with a vision-capable adapter. The adapter supplies `name`, `endpoint`, `key_env`, and `default_model`, plus `build_payload(state, questions, model)` and `parse_response(raw, questions)`. For images, the first argument is validated pixel content. General confidence gates and output evaluation require an explicit policy for a new provider so it does not inherit another model's numerical thresholds.

`parse_response` returns the canonical response described in the [adapter guide](CONTRIBUTING.md#add-a-model-adapter), including the resolved model, answer map, native usage, and original raw response. Preserve native choice or score probability distributions and native confidence as separate fields. Do not invent either. Put API credentials in the environment variable named by `key_env`. See [Contributing](CONTRIBUTING.md) before changing the optional reference implementation. Every new backend needs its own tests before receiving a Working label.

Compact reference evidence stays beside each skill. Raw test outputs stay in ignored `reports/` or retained CI artifacts.

## Credits and license

This project uses the [MIT License](LICENSE). The implementation, instructions, and synthetic fixtures are independently authored. The sources below are credited for ideas and API references, not endorsement or reproduced performance. Each skill also carries its original source links so credits travel with copied folders. Preserve original notices if contributing adapted material.

<details>
<summary>Original workflows, community sources, and Sage examples</summary>

- **Six-workflow inspiration:** Akshay Pachaar's [workflow post](https://x.com/akshay_pachaar/status/2107469584773300545) and [Jev article](https://x.com/i/article/2102087107410002345), plus [TypeSafe's official skills](https://github.com/typesafe-ai/skills).
- **Community discovery:** [awesome-jev](https://github.com/yibie/awesome-jev), [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills), [jev-agent-skill](https://github.com/yuyang2230/jev-agent-skill), and the [Jev AI Dev collection](https://jevai.dev/user-cases/). Their code, prose, and examples were not incorporated. AI Edge is credited for the original research, inbox, and content workflow article, and Miles Deutscher for sharing it. The relevant skills link the original posts.
- **Evaluation ideas:** [jev-as-judge](https://github.com/patchy631/jev-as-judge). Review on 2026-10-08 found no visible license, so it is credited for ideas only. No code, prose, or test cases were copied or adapted.
- **Study-tool routing:** [Leap's case study](https://levanto.ai/case-study/leap-study-tool-routing), by Leap, Alessandro Rutigliano, and the Levanto Team. The skill does not reproduce their dataset, multi-tool implementation, or reported accuracy.
- **Research decision gates:** [Capacitr's case study](https://levanto.ai/case-study/capacitr-market-signal-decision-gates), by Capacitr, Utkarsh Bhimte, and the Levanto Team. The independently authored skill executes no research or financial action and reproduces no claimed savings.
- **Image inspection:** [Levanto's image API documentation](https://docs.levanto.ai/decision-model/images) and [Austin Griffith's Sage Wisdom gallery](https://github.com/austintgriffith/sage-wisdom). Credit Levanto for the image interface and Austin Griffith for application examples. No Sage Wisdom code, prose, images, or performance claims were copied. Screenshot assets and their renderer are original.
- **Research leads:** [Marco De Rossi](https://x.com/marco_derossi), [Levanto Labs](https://x.com/levantolabs), and [Big Iron Chris](https://x.com/bigironchris).
- **Provider references:** [OpenRouter Decisions API](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request), [OpenAI Decisions API](https://developers.openai.com/api/docs/guides/decisions), and [Sage SystemOne](https://docs.levanto.ai/systemone).

Source popularity and customer-reported results do not establish compatibility. Only independently evaluated skills with at least one Working backend enter the catalog. Earlier Partial image evaluations remain in the retained development history; their reused synthetic fixtures are not a held-out benchmark.

</details>
