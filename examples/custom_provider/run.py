#!/usr/bin/env python3
"""Run a synthetic, offline custom-provider mapping against a copied skill."""
import argparse
import json
import os
import sys
from functools import partial
from pathlib import Path
from unittest.mock import patch

from decision_models.contracts import DecisionError
from decision_models.use_cases import execute_use_case, load_use_case

from adapter import ExampleAdapter, offline_transport


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="copied skill decision.json")
    parser.add_argument("--input", required=True, help="application input JSON")
    parser.add_argument("--scenario", choices=("recommend-billing", "missing-confidence", "malformed-answer"),
                        default="recommend-billing")
    args = parser.parse_args(argv)

    try:
        config = load_use_case(args.config)
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        adapter = ExampleAdapter()
        # The runtime exercises request/response mapping when mode is live. Here
        # its transport is fixed offline and receives a synthetic sentinel only.
        with patch.dict(os.environ, {adapter.key_env: "OFFLINE-EXAMPLE-NOT-A-CREDENTIAL"}):
            output = execute_use_case(config, adapter.name, data, mode="live", adapter=adapter,
                                      transport=partial(offline_transport, scenario=args.scenario))
        report = {"provider": adapter.name, "mode": "offline-example", "synthetic": True,
                  "requested_model": adapter.default_model,
                  "result": output["result"], "response": output["response"]}
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except DecisionError as exc:
        print(json.dumps({"error": exc.as_dict(), "synthetic": True}, sort_keys=True), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        error = DecisionError("invalid_request", "cannot read valid config or input JSON")
        print(json.dumps({"error": error.as_dict(), "synthetic": True}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
