"""Optional reference runner for newly evaluated provider-neutral text skills."""
import json
from pathlib import Path

from decision_models.recipes import execute_recipe
from decision_models.runtime import adapter_for


def read_config(folder):
    return json.loads((Path(folder) / "recipe.json").read_text())


def usecase_adapter(provider):
    adapter = adapter_for(provider)
    if provider == "sage":
        # Advertised by authenticated /v1/models on 2026-10-27.
        # Preserve the historical reference runtime and its v1.3 evidence.
        adapter.default_model = "levanto-sage-v1.4"
    return adapter


def execute_custom(folder, provider, data, **kwargs):
    return execute_recipe(read_config(folder), provider, data,
                          adapter=usecase_adapter(provider), **kwargs)
