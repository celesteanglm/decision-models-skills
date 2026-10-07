"""Proposed offline tests for reranking top_k semantics; run against the patch."""
import unittest
from decision_models.contracts import DecisionError
from decision_models.workflows import reranking


def score(level, confidence):
    return {
        "kind": "score", "status": "answered", "score": level,
        "probabilities": {str(i): (1.0 if i == level else 0.0) for i in range(5)},
        **({} if confidence is None else {"confidence": confidence}),
    }


class RerankingTopKTests(unittest.TestCase):
    def test_selected_low_confidence_requires_review(self):
        data = {"query": "q", "top_k": 1, "passages": [
            {"id": "best", "text": "best evidence"}, {"id": "other", "text": "other evidence"}]}
        response = {"answers": {"passage_0": score(4, .59), "passage_1": score(2, .99)}}
        result = reranking.decide(data, response)
        self.assertEqual(result["action"], "review")
        self.assertIn({"id": "best", "reason": "confidence_below_threshold"}, result["review_ids"])

    def test_unselected_low_confidence_can_rank_top_one_with_explicit_review_annotation(self):
        data = {"query": "q", "top_k": 1, "passages": [
            {"id": "best", "text": "best evidence"}, {"id": "other", "text": "other evidence"}]}
        response = {"answers": {"passage_0": score(4, .9), "passage_1": score(2, .2)}}
        result = reranking.decide(data, response)
        self.assertEqual(result["action"], "rank")
        self.assertEqual(result["ranked_ids"], ["best"])
        self.assertEqual(result["scores"], {"best": 1.0, "other": .5})
        self.assertEqual(result["confidence"], {"best": .9, "other": .2})
        self.assertEqual(result["review_ids"], [{"id": "other", "reason": "confidence_below_threshold"}])

    def test_default_top_k_requires_confidence_for_every_released_passage(self):
        data = {"query": "q", "passages": [
            {"id": "a", "text": "a"}, {"id": "b", "text": "b"}]}
        response = {"answers": {"passage_0": score(4, .9), "passage_1": score(1, None)}}
        result = reranking.decide(data, response)
        self.assertEqual(result["action"], "review")
        self.assertEqual(result["review_ids"], [{"id": "b", "reason": "confidence_missing"}])

    def test_exact_duplicate_text_shares_fractional_score_and_stable_tie(self):
        data = {"query": "q", "top_k": 3, "passages": [
            {"id": "first", "text": "identical"}, {"id": "lower", "text": "different"},
            {"id": "duplicate", "text": "identical"}]}
        prepared = reranking.build(data)
        self.assertEqual([q["name"] for q in prepared["questions"]], ["passage_0", "passage_1"])
        fractional = {"kind": "score", "status": "answered", "score": 2.75,
                      "probabilities": {"0": 0, "1": 0, "2": .25, "3": .75, "4": 0}, "confidence": .9}
        result = reranking.decide(data, {"answers": {"passage_0": fractional, "passage_1": score(1, .9)}})
        self.assertEqual(result["ranked_ids"], ["first", "duplicate", "lower"])
        self.assertEqual(result["scores"], {"first": .6875, "duplicate": .6875, "lower": .25})

    def test_top_k_must_be_integer_between_one_and_count(self):
        for value in (0, 3, 1.5, True, "1"):
            with self.subTest(value=value), self.assertRaises(DecisionError):
                reranking.build({"query": "q", "top_k": value, "passages": [
                    {"id": "a", "text": "a"}, {"id": "b", "text": "b"}]})

    def test_missing_answer_or_refusal_returns_review(self):
        data = {"query": "q", "top_k": 1, "passages": [{"id": "a", "text": "a"}]}
        self.assertEqual(reranking.decide(data, {"answers": {}})["action"], "review")
        self.assertEqual(reranking.decide(data, {"answers": {"passage_0": {"status": "refusal"}}})["action"], "review")


if __name__ == "__main__":
    unittest.main()
