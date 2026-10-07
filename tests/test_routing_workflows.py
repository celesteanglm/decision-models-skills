import json
import unittest
from pathlib import Path

from decision_models.contracts import DecisionError, validate_questions, validate_response
from decision_models.workflows import model_routing, reranking

ROOT = Path(__file__).resolve().parents[1]


class RoutingWorkflowTests(unittest.TestCase):
    def test_frozen_fixtures_have_expected_mix_and_execute(self):
        for slug, workflow in (("model-routing", model_routing), ("reranking", reranking)):
            fixtures = json.loads((ROOT / "skills" / slug / "fixtures/acceptance.json").read_text())
            self.assertEqual(len(fixtures), 12)
            self.assertEqual({kind: sum(x["category"] == kind for x in fixtures) for kind in ("clear", "ambiguous", "adversarial")},
                             {"clear": 8, "ambiguous": 2, "adversarial": 2})
            for fixture in fixtures:
                with self.subTest(slug=slug, fixture=fixture["id"]):
                    prepared = workflow.build(dict(fixture["input"], _provider="jev-openrouter"))
                    if prepared["early_result"] is not None:
                        result = prepared["early_result"]
                    else:
                        validate_questions(prepared["questions"])
                        response = {"model": "synthetic-test", "answers": fixture["demo_answers"], "usage": None}
                        validate_response(response, prepared["questions"])
                        result = workflow.decide(dict(fixture["input"], _provider="jev-openrouter"), response)
                    self.assertIn(result["action"], fixture["expected"]["actions"])
                    if "model_id" in fixture["expected"]:
                        self.assertEqual(result.get("model_id"), fixture["expected"]["model_id"])
                    if "top_id" in fixture["expected"] and result["action"] == "rank":
                        self.assertEqual(result["ranked_ids"][0], fixture["expected"]["top_id"])
                    if "ranked_ids" in fixture["expected"]:
                        self.assertEqual(result["ranked_ids"], fixture["expected"]["ranked_ids"])
                    if "forbidden_actions" in fixture["expected"]:
                        forbidden = fixture["expected"]["forbidden_actions"]
                        self.assertNotIn(result.get("model_id"), forbidden)
                        if result.get("ranked_ids"):
                            self.assertNotIn(result["ranked_ids"][0], forbidden)

    def test_routing_budget_is_deterministic_and_choice_is_allowlisted(self):
        data = {"task": "task", "eligible_models": [
            {"id": "cheap", "description": "cheap", "cost_per_1k_tokens": 0.1},
            {"id": "costly", "description": "costly", "cost_per_1k_tokens": 2}], "max_cost_per_1k_tokens": 0.5}
        prepared = model_routing.build(data)
        self.assertEqual(list(prepared["questions"][0]["options"]), ["cheap", "escalate"])
        response = {"answers": {"model_choice": {"kind": "choice", "status": "answered", "choice": "costly", "confidence": .99}}}
        result = model_routing.decide(data, response)
        self.assertEqual(result["action"], "escalate")
        self.assertEqual(result["reasons"], ["ineligible_model_rejected"])

    def test_low_or_missing_confidence_escalates_or_reviews(self):
        route = {"task": "x", "eligible_models": [{"id": "m", "description": "general"}]}
        self.assertEqual(model_routing.decide(route, {"answers": {"model_choice": {"status": "answered", "choice": "m", "confidence": .2}}})["action"], "escalate")
        rank = {"query": "x", "passages": [{"id": "a", "text": "text"}]}
        answer = {"kind": "score", "status": "answered", "score": 3}
        self.assertEqual(reranking.decide(rank, {"answers": {"passage_0": answer}})["action"], "review")
        answer["confidence"] = .2
        self.assertEqual(reranking.decide(rank, {"answers": {"passage_0": answer}})["action"], "review")

    def test_reranking_is_stable_on_ties_and_never_changes_passage_membership(self):
        data = {"query": "q", "passages": [{"id": "z", "text": "z"}, {"id": "a", "text": "a"}]}
        answer = {"kind": "score", "status": "answered", "score": 2, "confidence": .9,
                  "probabilities": {"0": 0, "1": 0, "2": 1, "3": 0, "4": 0}}
        result = reranking.decide(data, {"answers": {"passage_0": answer, "passage_1": answer}})
        self.assertEqual(result["ranked_ids"], ["z", "a"])
        self.assertEqual(set(result["ranked_ids"]), {"z", "a"})

    def test_invalid_threshold_and_duplicate_identifiers_are_rejected(self):
        with self.assertRaises(DecisionError):
            model_routing.build({"task": "x", "eligible_models": [], "confidence_threshold": float("nan")})
        with self.assertRaises(DecisionError):
            reranking.build({"query": "q", "passages": [{"id": "x", "text": "a"}, {"id": "x", "text": "b"}]})
        with self.assertRaises(DecisionError):
            model_routing.build({"task": "x", "eligible_models": [{"id": "escalate", "description": "reserved"}]})


if __name__ == "__main__":
    unittest.main()
