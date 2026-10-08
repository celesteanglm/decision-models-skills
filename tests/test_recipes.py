"""Acceptance and runner-contract coverage for portable decision recipes."""
import copy
import json
import os
import re
import unittest
from pathlib import Path
from unittest.mock import Mock

from decision_models.contracts import DecisionError
from decision_models.recipes import execute_recipe, load_recipe, prepare_recipe


REPO = Path(__file__).resolve().parents[1]
RECIPES = REPO / "recipes"
RECIPE_PATHS = sorted(RECIPES.glob("*/recipe.json"))


def answer_for(recipe, choice, *, confidence=0.95, probability=0.97, status="answered"):
    options = recipe["question"]["options"]
    other_probability = (1 - probability) / (len(options) - 1)
    return {"decision": {
        "kind": "choice", "status": status, "choice": choice,
        "probabilities": {label: probability if label == choice else other_probability
                          for label in options},
        "confidence": confidence,
    }}


def sage_raw(recipe, *, choice=None, confidence=0.95, probability=0.97,
             status="answered", model="sage-resolved-test-model", usage=None):
    options = recipe["question"]["options"]
    selected = choice or next(label for label in options if label != "review")
    other_probability = (1 - probability) / (len(options) - 1)
    result = {"model": model, "usage": usage, "answers": {"decision": {
        "type": "choice", "choice": selected,
        "probabilities": {label: probability if label == selected else other_probability
                          for label in options},
        "confidence": confidence,
    }}}
    if status == "refusal":
        result["answers"]["decision"] = {"type": "refusal"}
    return result


class RecipeFixtureTests(unittest.TestCase):
    def test_every_recipe_has_frozen_acceptance_set_and_hand_authored_demo_answers(self):
        self.assertTrue(RECIPE_PATHS, "recipe folders should be discovered dynamically")
        for recipe_path in RECIPE_PATHS:
            recipe_dir = recipe_path.parent
            with self.subTest(recipe=recipe_dir.name):
                recipe = load_recipe(recipe_path)
                self.assertEqual(recipe["id"], recipe_dir.name)
                fixtures_path = recipe_dir / "fixtures" / "acceptance.json"
                example_input_path = recipe_dir / "examples" / "input.json"
                demo_path = recipe_dir / "examples" / "demo.json"
                fixtures = json.loads(fixtures_path.read_text(encoding="utf-8"))
                self.assertIsInstance(fixtures, list)
                self.assertEqual(len(fixtures), 12)
                categories = [case["category"] for case in fixtures]
                self.assertEqual(categories.count("clear"), 8)
                self.assertEqual(categories.count("ambiguous"), 2)
                self.assertEqual(categories.count("adversarial"), 2)
                self.assertEqual(len({case["id"] for case in fixtures}), 12)

                example_input = json.loads(example_input_path.read_text(encoding="utf-8"))
                demo = json.loads(demo_path.read_text(encoding="utf-8"))
                self.assertIsInstance(example_input.get("state"), dict)
                self.assertIsInstance(demo.get("decision"), dict)
                self.assertEqual(set(demo["decision"]["probabilities"]),
                                 set(recipe["question"]["options"]))

                denied = []
                injected = []
                for case in fixtures:
                    self.assertIn("id", case)
                    self.assertIsInstance(case.get("input"), dict)
                    self.assertIsInstance(case.get("expected"), dict)
                    self.assertIsInstance(case.get("expected", {}).get("actions"), list)
                    result = execute_recipe(
                        recipe, "sage", case["input"], mode="demo",
                        demo_answers=case.get("demo_answers"),
                    )
                    self.assertIn(result["result"]["action"], case["expected"]["actions"])
                    if "choice" in case["expected"]:
                        self.assertEqual(result["result"]["choice"], case["expected"]["choice"])
                    self.assertFalse(result["executed_action"])
                    if case["category"] == "adversarial":
                        if case["input"].get("permission_granted") is False:
                            denied.append(case)
                        content = json.dumps(case["input"].get("state", {})).lower()
                        if (case["input"].get("permission_granted") is True and any(
                                phrase in content for phrase in
                                ("ignore", "disregard", "skip verification"))):
                            injected.append(case)
                self.assertEqual(len(denied), 1, recipe_dir.name)
                self.assertEqual(denied[0]["expected"]["actions"], ["deny"])
                self.assertEqual(len(injected), 1, recipe_dir.name)
                self.assertIn("recommend", injected[0]["expected"]["actions"], recipe_dir.name)

    def test_recipe_metadata_and_local_skill_references_are_portable(self):
        self.assertTrue(RECIPE_PATHS)
        for recipe_path in RECIPE_PATHS:
            recipe_dir = recipe_path.parent
            with self.subTest(recipe=recipe_dir.name):
                recipe = load_recipe(recipe_path)
                for field in ("title", "description", "inspiration", "limitations"):
                    self.assertTrue(recipe[field].strip())
                self.assertTrue(recipe["source_urls"])
                self.assertTrue(all(url.startswith("https://") for url in recipe["source_urls"]))
                allowed_skills = {"reranking", "confidence-gates", "input-guardrails",
                                  "model-routing", "tool-call-gating", "output-evaluation"}
                self.assertTrue(recipe["related_skills"])
                self.assertEqual(len(recipe["related_skills"]), len(set(recipe["related_skills"])))
                self.assertLessEqual(set(recipe["related_skills"]), allowed_skills)
                skill_path = recipe_dir / "SKILL.md"
                self.assertTrue(skill_path.is_file())
                skill = skill_path.read_text(encoding="utf-8")
                self.assertIn(recipe["title"], skill)
                local_references = []
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", skill):
                    if target.startswith(("https://", "http://", "#", "mailto:")):
                        continue
                    local_references.append(target)
                    local_path = (recipe_dir / target.split("#", 1)[0]).resolve()
                    self.assertTrue(local_path.is_relative_to(recipe_dir.resolve()), target)
                    self.assertTrue(local_path.is_file(), f"{recipe_dir.name}: broken reference {target}")
                self.assertTrue(local_references, f"{recipe_dir.name}: SKILL.md should reference local assets")
                for skill_name in recipe["related_skills"]:
                    self.assertTrue((REPO / "skills" / skill_name / "SKILL.md").is_file(), skill_name)
                for relative in ("examples/input.json", "examples/demo.json", "fixtures/acceptance.json"):
                    self.assertTrue((recipe_dir / relative).is_file(), relative)


class RecipeRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not RECIPE_PATHS:
            raise AssertionError("no recipe.json files found")
        cls.recipe = load_recipe(RECIPE_PATHS[0])
        cls.valid_input = {"state": {field: "A realistic evidence document for this decision."
                                      for field in cls.recipe["required_state_fields"]},
                           "permission_granted": True}
        cls.label = next(label for label in cls.recipe["question"]["options"] if label != "review")

    def test_permission_requires_explicit_boolean_true_and_never_calls_transport(self):
        for value in (False, None, "true", 1):
            data = copy.deepcopy(self.valid_input)
            if value is None:
                del data["permission_granted"]
            else:
                data["permission_granted"] = value
            transport = Mock(side_effect=AssertionError("transport must not run"))
            result = execute_recipe(self.recipe, "sage", data, mode="live", transport=transport)
            self.assertEqual(result["result"]["action"], "deny")
            self.assertEqual(result["attempts"], 0)
            self.assertIsNone(result["response"])
            transport.assert_not_called()

    def test_missing_empty_or_non_json_evidence_returns_review_or_explicit_error_without_transport(self):
        for state in (None, {}, {self.recipe["required_state_fields"][0]: ""},
                      {self.recipe["required_state_fields"][0]: []},
                      {self.recipe["required_state_fields"][0]: {}}):
            data = {"permission_granted": True, "state": state}
            transport = Mock(side_effect=AssertionError("transport must not run"))
            result = execute_recipe(self.recipe, "sage", data, mode="live", transport=transport)
            self.assertEqual(result["result"]["action"], "review")
            self.assertEqual(result["result"]["reasons"], ["missing_evidence"])
            transport.assert_not_called()
        data = copy.deepcopy(self.valid_input)
        data["state"][self.recipe["required_state_fields"][0]] = float("nan")
        with self.assertRaises(DecisionError) as raised:
            prepare_recipe(self.recipe, data)
        self.assertEqual(raised.exception.code, "invalid_request")

    def test_confidence_and_selected_probability_are_independent_inclusive_gates(self):
        boundary = answer_for(self.recipe, self.label, confidence=0.65, probability=0.65)
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=boundary)
        self.assertEqual(result["result"]["action"], "recommend")

        low_probability = answer_for(self.recipe, self.label, confidence=0.90, probability=0.64)
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=low_probability)
        self.assertEqual(result["result"]["action"], "review")
        self.assertIn("probability_below_threshold", result["result"]["reasons"])
        self.assertNotIn("confidence_below_threshold", result["result"]["reasons"])

        low_confidence = answer_for(self.recipe, self.label, confidence=0.64, probability=0.90)
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=low_confidence)
        self.assertEqual(result["result"]["action"], "review")
        self.assertIn("confidence_below_threshold", result["result"]["reasons"])
        self.assertNotIn("probability_below_threshold", result["result"]["reasons"])

    def test_missing_confidence_selected_review_and_refusal_require_review(self):
        no_confidence = answer_for(self.recipe, self.label)
        del no_confidence["decision"]["confidence"]
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=no_confidence)
        self.assertEqual(result["result"]["action"], "review")
        self.assertIn("confidence_missing", result["result"]["reasons"])

        selected_review = answer_for(self.recipe, "review")
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=selected_review)
        self.assertEqual(result["result"]["action"], "review")
        self.assertIn("model_requested_review", result["result"]["reasons"])

        refusal = {"decision": {"kind": "choice", "status": "refusal"}}
        result = execute_recipe(self.recipe, "sage", self.valid_input, demo_answers=refusal)
        self.assertEqual(result["result"]["action"], "review")
        self.assertEqual(result["result"]["reasons"], ["provider_refusal"])

    def test_request_contains_only_evidence_and_trusted_question_not_fixture_expectations(self):
        fixture = json.loads((RECIPE_PATHS[0].parent / "fixtures" / "acceptance.json").read_text())[0]
        captured = {}

        def transport(endpoint, payload, key, timeout):
            captured.update(endpoint=endpoint, payload=payload, key=key, timeout=timeout)
            return sage_raw(self.recipe, choice=self.label)

        prior = os.environ.get("SAGE_API_KEY")
        os.environ["SAGE_API_KEY"] = "test-key"
        try:
            result = execute_recipe(self.recipe, "sage", fixture["input"], mode="live",
                                    transport=transport, model="requested-alias")
        finally:
            if prior is None:
                os.environ.pop("SAGE_API_KEY", None)
            else:
                os.environ["SAGE_API_KEY"] = prior

        self.assertEqual(set(captured["payload"]), {"model", "state", "questions", "reasoning"})
        self.assertEqual(captured["payload"]["model"], "requested-alias")
        self.assertEqual(captured["payload"]["state"], fixture["input"]["state"])
        self.assertEqual(captured["payload"]["questions"], {"decision": {
            "type": "choice", "instructions": self.recipe["question"]["instructions"],
            "criteria": self.recipe["question"]["options"],
        }})
        self.assertEqual(captured["payload"]["reasoning"], "off")
        self.assertEqual(result["requested_model"], "requested-alias")

    def test_resolved_model_native_usage_and_raw_response_are_preserved(self):
        usage = {"input_tokens": 37, "output_tokens": 8, "provider_extension": "kept"}
        raw = sage_raw(self.recipe, choice=self.label, model="resolved-model-v7", usage=usage)
        prior = os.environ.get("SAGE_API_KEY")
        os.environ["SAGE_API_KEY"] = "test-key"
        try:
            result = execute_recipe(self.recipe, "sage", self.valid_input, mode="live",
                                    transport=lambda *_args: raw, model="requested-model")
        finally:
            if prior is None:
                os.environ.pop("SAGE_API_KEY", None)
            else:
                os.environ["SAGE_API_KEY"] = prior
        self.assertEqual(result["response"]["model"], "resolved-model-v7")
        self.assertEqual(result["response"]["usage"], usage)
        self.assertIs(result["response"]["raw_response"], raw)

    def test_injected_adapter_supports_new_provider_and_demo_and_denial_never_use_transport(self):
        usage = {"input_tokens": 41, "output_tokens": 6, "sdk_cost_units": 3}
        raw = {"resolved_model": "community-model-4", "native_usage": usage,
               "selected": self.label}

        class CommunitySdkAdapter:
            default_model = "community-model-default"
            endpoint = "https://sdk.example.invalid/decision"
            key_env = "COMMUNITY_SDK_TEST_KEY"

            def __init__(self):
                self.payloads = []
                self.parsed = []

            def build_payload(self, state, questions, model):
                payload = {"sdk_model": model, "sdk_state": state,
                           "sdk_question": questions[0]}
                self.payloads.append(payload)
                return payload

            def parse_response(self, response, questions):
                self.parsed.append(response)
                options = questions[0]["options"]
                selected = response["selected"]
                other = 0.03 / (len(options) - 1)
                return {"model": response["resolved_model"],
                        "usage": response["native_usage"], "raw_response": response,
                        "answers": {"decision": {
                            "kind": "choice", "status": "answered", "choice": selected,
                            "probabilities": {label: 0.97 if label == selected else other
                                              for label in options},
                            "confidence": 0.95,
                        }}}

        adapter = CommunitySdkAdapter()
        transport = Mock(return_value=raw)
        prior = os.environ.get(adapter.key_env)
        os.environ[adapter.key_env] = "dummy-sdk-key"
        try:
            live = execute_recipe(self.recipe, "community-sdk", self.valid_input, mode="live",
                                  transport=transport, model="community-request-alias", adapter=adapter)

            self.assertEqual(live["provider"], "community-sdk")
            self.assertEqual(live["requested_model"], "community-request-alias")
            self.assertEqual(live["response"]["model"], "community-model-4")
            self.assertEqual(live["response"]["usage"], usage)
            self.assertIs(live["response"]["raw_response"], raw)
            self.assertEqual(adapter.payloads[0]["sdk_state"], self.valid_input["state"])
            transport.assert_called_once()

            transport.reset_mock(side_effect=True, return_value=True)
            adapter.payloads.clear()
            adapter.parsed.clear()
            demo = execute_recipe(self.recipe, "community-sdk", self.valid_input, mode="demo",
                                  demo_answers=answer_for(self.recipe, self.label),
                                  transport=transport, adapter=adapter)
            self.assertEqual(demo["result"]["choice"], self.label)
            self.assertEqual(demo["source"], "demo")
            transport.assert_not_called()
            self.assertEqual(adapter.payloads, [])
            self.assertEqual(adapter.parsed, [])

            denied_transport = Mock(side_effect=AssertionError("permission denial must not dispatch"))
            for permission in (False, None):
                denied_input = copy.deepcopy(self.valid_input)
                if permission is None:
                    denied_input.pop("permission_granted")
                else:
                    denied_input["permission_granted"] = permission
                denied = execute_recipe(self.recipe, "community-sdk", denied_input, mode="live",
                                        transport=denied_transport, adapter=adapter)
                self.assertEqual(denied["result"]["action"], "deny")
                self.assertEqual(denied["attempts"], 0)
            denied_transport.assert_not_called()
        finally:
            if prior is None:
                os.environ.pop(adapter.key_env, None)
            else:
                os.environ[adapter.key_env] = prior

    def test_authentication_failure_timeout_and_malformed_response_are_explicit_single_attempts(self):
        prior = os.environ.pop("SAGE_API_KEY", None)
        try:
            transport = Mock()
            with self.assertRaises(DecisionError) as raised:
                execute_recipe(self.recipe, "sage", self.valid_input, mode="live", transport=transport)
            self.assertEqual(raised.exception.code, "missing_credentials")
            transport.assert_not_called()
        finally:
            if prior is not None:
                os.environ["SAGE_API_KEY"] = prior

        prior = os.environ.get("SAGE_API_KEY")
        os.environ["SAGE_API_KEY"] = "test-key"
        try:
            for error_code, raw in (("authentication", DecisionError("authentication", "rejected")),
                                    ("timeout", DecisionError("timeout", "charge status unknown"))):
                transport = Mock(side_effect=raw)
                with self.subTest(error=error_code):
                    with self.assertRaises(DecisionError) as raised:
                        execute_recipe(self.recipe, "sage", self.valid_input, mode="live", transport=transport)
                    self.assertEqual(raised.exception.code, error_code)
                    transport.assert_called_once()

            transport = Mock(return_value={"model": "resolved", "answers": {"wrong": {}}})
            with self.assertRaises(DecisionError) as raised:
                execute_recipe(self.recipe, "sage", self.valid_input, mode="live", transport=transport)
            self.assertEqual(raised.exception.code, "invalid_response")
            transport.assert_called_once()
        finally:
            if prior is None:
                os.environ.pop("SAGE_API_KEY", None)
            else:
                os.environ["SAGE_API_KEY"] = prior


if __name__ == "__main__":
    unittest.main()
