# Offline custom provider example

This example connects a fictional fourth text provider to the existing `execute_use_case` runner. It builds a provider-shaped request, parses a provider-shaped response, and applies the copied skill's policy. The fixed offline transport returns synthetic responses and cannot contact a service. No API key is needed.

## Run it

Use Python 3.10 or newer. Clone the repository and install the optional package in a virtual environment:

```sh
git clone https://github.com/celesteanglm/decision-models-skills.git
cd decision-models-skills
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

Copy the complete example and skill to a temporary project. Use fresh destination folders:

```sh
cp -R examples/custom_provider /tmp/custom_provider
cp -R skills/email-queue-routing /tmp/email-queue-routing
cd /tmp
```

From there (or any other working directory), run:

```sh
python /tmp/custom_provider/run.py \
  --config /tmp/email-queue-routing/decision.json \
  --input /tmp/email-queue-routing/examples/input.json
```

The default scenario prints a synthetic `billing` recommendation. Try the other response paths:

```sh
python /tmp/custom_provider/run.py --config /tmp/email-queue-routing/decision.json \
  --input /tmp/email-queue-routing/examples/input.json --scenario missing-confidence
python /tmp/custom_provider/run.py --config /tmp/email-queue-routing/decision.json \
  --input /tmp/email-queue-routing/examples/input.json --scenario malformed-answer
```

Check these fields in the output:

| Scenario | Expected result | Exit code |
|---|---|---|
| Default | `result.action: recommend`, `result.choice: billing` | 0 |
| `missing-confidence` | `result.action: review`, reason `confidence_missing` | 0 |
| `malformed-answer` | `error.code: invalid_response` | 2 |

The missing-confidence case goes to review because the skill requires native confidence. Neither path invents a missing metric. The successful response preserves native usage and the original raw answer. Every report is labeled `synthetic: true` and `mode: offline-example`. This example gives the runtime a temporary test sentinel instead of a real credential, then restores the environment.

The example uses the installed `decision_models` package and imports no files from the repository at runtime. Copy the skill folder intact. A `SKILL.md` alone remains usable with an agent, but this optional Python example needs the package installed in your application environment.

## Connect your own model

Keep the example offline. Create a separate adapter in your application using `adapter.py` as a guide:

1. Set `name`, `endpoint`, `key_env`, and `default_model` to your integration's values.
2. Map the canonical question and evidence to the provider's request format in `build_payload`.
3. Map its resolved model, answers, native distributions, confidence when available, raw response, and usage in `parse_response`. Validate the result with `validate_response`.
4. Run your mapping with a fake transport first. Keep permission denials and missing-metric review behavior intact.
5. After approving a live-test budget, call the same runner from your application with your adapter and a real transport. The default transport uses JSON over HTTP with Bearer authentication. For another authentication scheme or SDK, inject a transport with signature `(endpoint, payload, api_key, timeout)`.

The [README's Jev and Sage examples](../../README.md#connect-a-provider-once) show actual built-in adapter calls with explicit models. Keep credentials in the environment. A new adapter does not require a provider registry entry or changes to a copied skill. It still needs independent tests before it earns a Working label.

For the six general workflows, inject the adapter into `decision_models.runtime.execute`. Supply an explicit `policy=` for a new confidence-gates or output-evaluation provider. For images, inject a vision adapter into `scripts.image_reference.execute_image` from a repository checkout. It receives validated image pixels and task text, using the same local file restrictions. See the [implementation contract](../../IMPLEMENTATION_CONTRACT.md#third-party-text-adapter-and-runnable-example) for method signatures and policy fields. The optional package installs the core Python runtime; repository image helpers are separate scripts.
