from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import re
import unittest
from unittest.mock import Mock, patch

from decision_models.contracts import DecisionError
from examples.sage_image_model_selection import AllowedSageImageAdapter
from scripts.evaluate_images import ImageBudget
from scripts.image_reference import SageImageAdapter, execute_image


QUESTION = {"name": "decision", "kind": "choice", "instructions": "Check the named button.",
            "options": {"visible": "Fully visible", "review": "Unclear"}}


def raw_response(model):
    return {"meta": {"model": model, "usage": {"input_tokens": 100, "image_tokens": 50,
                                               "billed_input_tokens": 150, "output_tokens": 0}},
            "results": [{"answers": [{"ok": True, "result": {
                "id": "decision", "kind": "choice", "meta": {"model": model},
                "result": {"chosen": "visible", "probability": 0.9,
                           "probabilities": [{"option": "visible", "probability": 0.9},
                                             {"option": "review", "probability": 0.1}]}}}]}]}


class SageImageModelSelectionTests(unittest.TestCase):
    def test_documented_example_runs_and_reserves_budget_before_transport(self):
        readme = (Path(__file__).resolve().parents[1] / 'README.md').read_text()
        snippet = re.search(r'<!-- example: sage-image -->\n```python\n(.*?)\n```', readme, re.S)[1]
        raw = raw_response('levanto-sage-2')
        probabilities = raw['results'][0]['answers'][0]['result']['result']['probabilities']
        probabilities[1]['probability'] = 0.05
        probabilities.append({'option': 'not_visible', 'probability': 0.05})
        for limit in (0.10, 0.01):
            with self.subTest(limit=limit):
                transport = Mock(return_value=raw)
                budget = ImageBudget(limit=limit, historical_bound=0)
                def run(*args, **kwargs):
                    return execute_image(*args, transport=transport, **kwargs)
                with patch.dict(os.environ, {'SAGE_API_KEY': 'synthetic-test-only'}), \
                     patch('scripts.image_reference.execute_image', side_effect=run), \
                     patch('scripts.evaluate_images.ImageBudget', return_value=budget), \
                     redirect_stdout(io.StringIO()):
                    if limit == 0.01:
                        with self.assertRaises(DecisionError) as error:
                            exec(compile(snippet, 'README.md image example', 'exec'), {})
                        self.assertEqual(error.exception.code, 'budget_exhausted')
                        transport.assert_not_called()
                    else:
                        scope = {}
                        exec(compile(snippet, 'README.md image example', 'exec'), scope)
                        transport.assert_called_once()
                        self.assertEqual(scope['result']['response']['model'], 'levanto-sage-2')
                        self.assertEqual(budget.attempts, 1)
                        self.assertEqual(budget.held, 0)

    def test_allowed_versions_preserve_resolved_identity_usage_and_native_probability(self):
        adapter = AllowedSageImageAdapter(["levanto-sage-v1.4", "levanto-sage-2"])
        for model in adapter.allowed_models:
            with self.subTest(model=model):
                raw = raw_response(model)
                result = adapter.parse_response(raw, [QUESTION])
                self.assertEqual(result["model"], model)
                self.assertEqual(result["raw_response"], raw)
                self.assertEqual(result["usage"], raw["meta"]["usage"])
                self.assertEqual(result["answers"]["decision"]["probability"], 0.9)
                self.assertIsNone(result["answers"]["decision"]["confidence"])
        payload = adapter.build_payload({"kind": "image", "media": "data:image/png;base64,cGl4ZWxz"},
                                        [QUESTION], adapter.default_model)
        self.assertNotIn("model", payload)
        self.assertEqual(SageImageAdapter.default_model, "levanto-sage-v1.4")

    def test_unknown_versions_and_conflicting_per_answer_models_are_rejected(self):
        adapter = AllowedSageImageAdapter(["levanto-sage-2"])
        for raw in (raw_response("unexpected-model"), raw_response("levanto-sage-v1.4")):
            with self.assertRaises(DecisionError) as error:
                adapter.parse_response(raw, [QUESTION])
            self.assertEqual(error.exception.code, "model_mismatch")
        raw = raw_response("levanto-sage-2")
        raw["results"][0]["answers"][0]["result"]["meta"]["model"] = "unexpected-model"
        with self.assertRaises(DecisionError) as error:
            adapter.parse_response(raw, [QUESTION])
        self.assertEqual(error.exception.code, "model_mismatch")

    def test_invalid_allowlists_and_malformed_responses_fail_explicitly(self):
        for models in ([], "levanto-sage-2", [None], [""], [" "], [" levanto-sage-2"], ["levanto-sage-2 "]):
            with self.subTest(models=models), self.assertRaises(DecisionError):
                AllowedSageImageAdapter(models)
        adapter = AllowedSageImageAdapter(["levanto-sage-2"])
        for raw in (None, {}, {"meta": None}):
            with self.subTest(raw=raw), self.assertRaises(DecisionError) as error:
                adapter.parse_response(raw, [QUESTION])
            self.assertEqual(error.exception.code, "invalid_response")
        raw = raw_response("levanto-sage-2")
        raw["results"][0]["answers"][0]["result"]["result"]["probability"] = 0.8
        with self.assertRaises(DecisionError) as error:
            adapter.parse_response(raw, [QUESTION])
        self.assertEqual(error.exception.code, "invalid_response")
