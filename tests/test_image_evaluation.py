import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from decision_models.contracts import DecisionError
from decision_models.evaluation import source_hash
from scripts.evaluate_images import ImageBudget, evaluate
from scripts.image_reference import SageImageAdapter, execute_image, prepare_image
from tests.test_image_reference import image_config, native_raw, png_bytes


class ImageEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        (self.repo / 'scripts').mkdir(parents=True)
        (self.repo / 'reports').mkdir()
        for name in ('image_reference.py', 'evaluate_images.py'):
            (self.repo / 'scripts' / name).write_text('# test-only helper\n')
        self.folder = self.root / 'candidate'
        (self.folder / 'images').mkdir(parents=True)
        (self.folder / 'fixtures').mkdir()
        self.config = image_config()
        (self.folder / 'image.json').write_text(json.dumps(self.config))
        (self.folder / 'images' / 'sample.png').write_bytes(png_bytes())
        self.data = {'permission_granted': True, 'state': {'content': 'Inspect the named button.', 'image': 'images/sample.png'}}
        self.cases = [{'id': f'case-{i}', 'category': 'clear' if i < 8 else 'ambiguous' if i < 10 else 'adversarial',
                       'input': copy.deepcopy(self.data), 'expected': {'actions': ['recommend'], 'choice': 'visible'}}
                      for i in range(12)]
        (self.folder / 'fixtures' / 'acceptance.json').write_text(json.dumps(self.cases))
        (self.repo / 'reports' / 'offline.json').write_text(json.dumps({'passed': True, 'source_hash': source_hash(self.repo)}))
        self.output = self.root / 'run.json'
        self.payload = SageImageAdapter().build_payload(prepare_image(self.folder, self.data)['content'], [self.config['question']])

    def test_invalid_budget_values_are_rejected(self):
        for value in (True, -1, float('nan'), float('inf'), 6):
            with self.subTest(value=value), self.assertRaises(DecisionError):
                ImageBudget(5, value)
        for value in (True, 0, -1, float('nan'), 6):
            with self.subTest(limit=value), self.assertRaises(DecisionError):
                ImageBudget(value, 0)

    def test_full_coverage_is_reserved_before_any_dispatch(self):
        with patch('scripts.evaluate_images.execute_image') as run:
            with self.assertRaises(DecisionError) as error:
                evaluate(self.repo, self.folder, self.output, mode='live', historical_bound=4.99)
        self.assertEqual(error.exception.code, 'budget_exhausted')
        run.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_billed_input_includes_images_without_counting_them_twice(self):
        budget = ImageBudget(5, 0)
        budget.reserve('sage', self.payload)
        raw = {'meta': {'usage': {'billed_input_tokens': 200, 'input_tokens': 100, 'image_tokens': 100, 'output_tokens': 0}}}
        budget.record('sage', raw)
        self.assertAlmostEqual(budget.estimated, (200 * 0.05 + 10) / 1_000_000)
        self.assertEqual(budget.snapshot()['held_attempt_allowance_usd'], 0)
        self.assertEqual(budget.latest_raw, raw)

    def test_failed_usage_settlement_keeps_the_allowance(self):
        budget = ImageBudget(5, 0.4)
        budget.reserve('sage', self.payload)
        with self.assertRaises(DecisionError) as error:
            budget.record('sage', {'meta': {}})
        self.assertEqual(error.exception.code, 'invalid_usage')
        self.assertEqual(budget.snapshot()['held_attempt_allowance_usd'], round(budget.reserved, 9))
        self.assertGreater(budget.snapshot()['conservative_total_bound_usd'], 0.4)

    def test_charge_above_allowance_is_recorded_before_stopping(self):
        budget = ImageBudget(5, 0)
        budget.reserve('sage', self.payload)
        with self.assertRaises(DecisionError) as error:
            budget.record('sage', {'meta': {'usage': {'cost': 0.9}}})
        self.assertEqual(error.exception.code, 'budget_estimate_exceeded')
        self.assertEqual(budget.snapshot()['provider_reported_usd'], 0.9)
        self.assertEqual(budget.snapshot()['held_attempt_allowance_usd'], 0)

    def test_timeout_stops_repetitions_and_retains_the_unknown_charge_allowance(self):
        def timeout(folder, provider, data, **kwargs):
            kwargs['before_attempt'](provider, self.payload)
            raise DecisionError('timeout', 'unknown charge')
        run = Mock(side_effect=timeout)
        with patch('scripts.evaluate_images.execute_image', run):
            receipt = evaluate(self.repo, self.folder, self.output, mode='live', historical_bound=0)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(len(receipt['rows']), 1)
        self.assertEqual(receipt['budget']['attempts'], 1)
        self.assertGreater(receipt['budget']['held_attempt_allowance_usd'], 0)
        self.assertEqual(receipt['summary']['sage/' + self.config['id']]['status'], 'Blocked')
        self.assertTrue(self.output.with_suffix('.jsonl').is_file())

    def test_stale_offline_marker_and_existing_receipts_cannot_dispatch(self):
        (self.repo / 'reports' / 'offline.json').write_text(json.dumps({'passed': True, 'source_hash': 'stale'}))
        with patch('scripts.evaluate_images.execute_image') as run:
            with self.assertRaises(DecisionError) as error:
                evaluate(self.repo, self.folder, self.output, mode='live', historical_bound=0)
        self.assertEqual(error.exception.code, 'offline_verification_required')
        run.assert_not_called()
        for existing in (self.output, self.output.with_suffix('.jsonl')):
            existing.write_text('original')
            with patch('scripts.evaluate_images.execute_image') as run:
                with self.assertRaises(DecisionError):
                    evaluate(self.repo, self.folder, self.output)
            self.assertEqual(existing.read_text(), 'original')
            run.assert_not_called()
            existing.unlink()

    def test_live_call_requires_an_explicit_cumulative_bound(self):
        with patch('scripts.evaluate_images.execute_image') as run:
            with self.assertRaises(DecisionError) as error:
                evaluate(self.repo, self.folder, self.output, mode='live')
        self.assertEqual(error.exception.code, 'invalid_request')
        run.assert_not_called()

    def test_malformed_choice_is_journaled_with_raw_usage_and_stops_without_retry(self):
        raw = native_raw(usage={'billed_input_tokens': 200, 'input_tokens': 100,
                                'image_tokens': 100, 'output_tokens': 1})
        raw['results'][0]['answers'] = [raw['results'][0]['answers'][1]]
        raw['results'][0]['answers'][0]['result']['result']['chosen'] = []
        transport = Mock(return_value=raw)

        def run(*args, **kwargs):
            return execute_image(*args, transport=transport, **kwargs)

        with patch.dict(os.environ, {'SAGE_API_KEY': 'synthetic-test-only'}, clear=True), \
             patch('scripts.evaluate_images.execute_image', side_effect=run):
            receipt = evaluate(self.repo, self.folder, self.output, mode='live', historical_bound=0)
        transport.assert_called_once()
        self.assertEqual(len(receipt['rows']), 1)
        row = receipt['rows'][0]
        self.assertEqual(row['error']['code'], 'invalid_response')
        self.assertEqual(row['raw_response'], raw)
        self.assertEqual(row['attempts'], 1)
        self.assertIsNotNone(row['charge'])
        self.assertEqual(json.loads(self.output.read_text())['rows'][0]['error']['code'], 'invalid_response')
        events = [json.loads(line) for line in self.output.with_suffix('.jsonl').read_text().splitlines()]
        self.assertEqual(events[0]['event'], 'reserved')
        self.assertEqual(events[1]['raw_response'], raw)
