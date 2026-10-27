"""Independent pre-move contract hashes preserve decision behavior across layout changes."""
import hashlib
import json
from pathlib import Path
import unittest

from decision_models.runtime import SKILLS, adapter_for, execute, workflow_for
from decision_models.use_cases import execute_use_case, prepare_use_case
from scripts.usecase_reference import execute_custom, usecase_adapter

REPO = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((REPO / 'tests/fixtures/layout-contracts.json').read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode()).hexdigest()


class LayoutContractTests(unittest.TestCase):
    def test_frozen_examples_fixtures_and_decision_contracts_are_unchanged(self):
        folders = {p.parent.name: p.parent for p in (REPO / 'skills').glob('*/SKILL.md')}
        self.assertEqual(set(folders), set(GOLDEN['artifact_contracts']))
        for skill, expected in GOLDEN['artifact_contracts'].items():
            with self.subTest(skill=skill):
                folder = folders[skill]
                observed = {'fixtures': digest(json.loads((folder / 'fixtures/acceptance.json').read_text())),
                            'examples': {p.name: digest(json.loads(p.read_text()))
                                         for p in sorted((folder / 'examples').glob('*.json'))}}
                if (folder / 'decision.json').is_file():
                    config = json.loads((folder / 'decision.json').read_text())
                    observed['decision'] = digest({k: config[k] for k in
                                                    ('id', 'required_state_fields', 'question', 'policy')})
                self.assertEqual(observed, expected)

    def test_native_requests_and_policy_outcomes_match_pre_move_golden_hashes(self):
        self.assertEqual(len(GOLDEN['contracts']), 26 * 3 * 12)
        expected = {(skill, provider, case['id'])
                    for skill in GOLDEN['artifact_contracts']
                    for provider in ('jev-openrouter', 'openai-decisions', 'sage')
                    for case in json.loads((REPO / 'skills' / skill / 'fixtures/acceptance.json').read_text())}
        observed = {(c['skill'], c['provider'], c['case_id']) for c in GOLDEN['contracts']}
        self.assertEqual(observed, expected)
        self.assertEqual(len(observed), len(GOLDEN['contracts']))
        for contract in GOLDEN['contracts']:
            skill, provider = contract['skill'], contract['provider']
            folder = REPO / 'skills' / skill
            cases = json.loads((folder / 'fixtures/acceptance.json').read_text())
            case = next(c for c in cases if c['id'] == contract['case_id'])
            with self.subTest(skill=skill, provider=provider, case=case['id']):
                kwargs = {'mode': 'demo', 'demo_answers': case.get('demo_answers')}
                if skill in SKILLS:
                    adapter = adapter_for(provider)
                    built = workflow_for(skill).build(dict(case['input'], _provider=provider))
                    payload = None if built.get('early_result') is not None else adapter.build_payload(
                        built['state'], built['questions'], adapter.default_model)
                    result = execute(skill, provider, case['input'], **kwargs)
                else:
                    config = json.loads((folder / 'decision.json').read_text())
                    scoped = skill in ('study-tool-selection', 'research-enrichment-gate')
                    adapter = usecase_adapter(provider) if scoped else adapter_for(provider)
                    payload = None if prepare_use_case(config, case['input']) is not None else adapter.build_payload(
                        case['input']['state'], [config['question']], adapter.default_model)
                    result = (execute_custom(folder, provider, case['input'], **kwargs) if scoped else
                              execute_use_case(config, provider, case['input'], **kwargs))
                self.assertEqual(digest(payload), contract['payload_sha256'])
                self.assertEqual(digest(result['result']), contract['policy_sha256'])
