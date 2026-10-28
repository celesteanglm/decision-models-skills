"""Optional connection for a Sage deployment that selects its image model."""
from decision_models.contracts import DecisionError
from scripts.image_reference import SageImageAdapter


class AllowedSageImageAdapter(SageImageAdapter):
    """Accept only explicitly allowed resolved versions; preserve their actual IDs."""

    default_model = "sage-server-selected"

    def __init__(self, allowed_models):
        if (not isinstance(allowed_models, (list, tuple, set, frozenset))
                or not allowed_models
                or any(not isinstance(model, str) or not model.strip() or model != model.strip()
                       for model in allowed_models)):
            raise DecisionError("invalid_request", "configure a nonempty set of allowed Sage model IDs")
        self.allowed_models = frozenset(allowed_models)

    def parse_response(self, raw, questions):
        if not isinstance(raw, dict) or not isinstance(raw.get("meta"), dict):
            raise DecisionError("invalid_response", "Sage response is missing model metadata")
        resolved = raw["meta"].get("model")
        if not isinstance(resolved, str) or resolved not in self.allowed_models:
            raise DecisionError("model_mismatch", "Sage resolved a model outside the configured allowlist")
        pinned = SageImageAdapter()
        pinned.default_model = resolved
        return pinned.parse_response(raw, questions)
