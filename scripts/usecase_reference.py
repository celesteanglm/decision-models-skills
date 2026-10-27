"""Optional reference runner for newly evaluated provider-neutral text skills."""
import json
from pathlib import Path

from decision_models.use_cases import execute_use_case
from decision_models.runtime import adapter_for


def read_config(folder):
    return json.loads((Path(folder) / "decision.json").read_text())


def usecase_adapter(provider):
    adapter = adapter_for(provider)
    if provider == "sage":
        # Advertised by authenticated /v1/models on 2026-10-27.
        # Preserve the historical reference runtime and its v1.3 evidence.
        adapter.default_model = "levanto-sage-v1.4"
    return adapter


def execute_custom(folder, provider, data, **kwargs):
    return execute_use_case(read_config(folder), provider, data,
                          adapter=usecase_adapter(provider), **kwargs)
