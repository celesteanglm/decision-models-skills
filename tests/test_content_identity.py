import json
import unittest
from pathlib import Path

from decision_models.runtime import workflow_for


REPO = Path(__file__).resolve().parents[1]


def score(score_value, confidence=0.9):
    low = int(score_value)
    high = min(4, low + 1)
    fraction = score_value - low
    probabilities = {str(index): 0.0 for index in range(5)}
    probabilities[str(low)] = 1.0 - fraction
    probabilities[str(high)] += fraction
    return {"kind": "score", "status": "answered", "score": score_value,
            "probabilities": probabilities, "confidence": confidence}


class ContentIdentityTests(unittest.TestCase):
    def test_identical_exact_text_shares_one_question_and_one_fractional_score(self):
        workflow = workflow_for("reranking")
        data = {"query": "Find the relevant passage", "passages": [
            {"id": "first-copy", "text": "Exact same evidence."},
            {"id": "second-copy", "text": "Exact same evidence."},
            {"id": "different", "text": "Different evidence."},
        ]}
        prepared = workflow.build(data)
        self.assertEqual([question["name"] for question in prepared["questions"]],
                         ["passage_0", "passage_2"])
        shared = score(2.5)
        response = {"model": "test", "answers": {"passage_0": shared, "passage_2": score(2.5)}}
        result = workflow.decide(data, response)
        self.assertEqual(result["ranked_ids"], ["first-copy", "second-copy", "different"])
        self.assertEqual(result["top_id"] if "top_id" in result else result["ranked_ids"][0], "first-copy")
        self.assertEqual(result["scores"], {"first-copy": 0.625, "second-copy": 0.625, "different": 0.625})

    def test_reranking_fixture_answers_are_keyed_by_unique_exact_text(self):
        cases = json.loads((REPO / "skills/reranking/fixtures/acceptance.json").read_text())
        for case in cases:
            passages = case["input"]["passages"]
            first_index = {}
            for index, passage in enumerate(passages):
                first_index.setdefault(passage["text"], index)
            expected_names = {f"passage_{index}" for index in first_index.values()}
            with self.subTest(case=case["id"]):
                self.assertEqual(set(case["demo_answers"]), expected_names)


if __name__ == "__main__":
    unittest.main()
