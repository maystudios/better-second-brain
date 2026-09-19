"""Independent behavioral acceptance tests for docs/jev-branching-contract.md.

The deterministic Choice service exercises gateway behavior, not model quality.
These tests were authored against the frozen interface before implementation.
"""
import hashlib
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class ChoiceFixture:
    """Respond to declared Choice criteria, and record every service boundary."""

    def __init__(self, coverage=None, conflict=None, route=None, before=None):
        self.calls = []
        self.coverage = coverage or (lambda text, need: 'full' if 'EVIDENCE' in text else 'none')
        self.conflict = conflict or (lambda text, need: 'present' if 'CONTRARY' in text else 'absent')
        self.route = route
        self.before = before

    def __call__(self, payload, key, model, timeout):
        self.calls.append(payload)
        if self.before:
            self.before(payload)
        state = payload['state']
        operation = state['operation']
        answers = {}
        blocks = state.get('blocks', {})
        text = '\n'.join(block['text'] for block in blocks.values())
        for qid, question in payload['questions'].items():
            choices = list(question['criteria'])
            need = qid.rsplit('_', 1)[-1]
            if operation == 'branch_route':
                candidates = [item for item in choices if item != 'none']
                choice = self.route(state, candidates) if self.route else candidates[0]
            elif qid.startswith('coverage_'):
                choice = self.coverage(text, need)
            elif qid.startswith('conflict_'):
                choice = self.conflict(text, need)
            elif qid.startswith('location_'):
                matching = [bid for bid, block in blocks.items()
                            if 'EVIDENCE' in block['text'] or 'CONTRARY' in block['text']]
                choice = matching[0] if matching else ('none' if 'none' in choices else choices[0])
            else:
                raise AssertionError(f'Unexpected question {qid}')
            if choice not in choices:
                raise AssertionError(f'Invalid fixture choice {choice}: {choices}')
            answers[qid] = {
                'type': 'choice', 'choice': choice, 'confidence': 1.0,
                'probabilities': {item: float(item == choice) for item in choices},
            }
        return {'model': model, 'answers': answers,
                'usage': {'input_tokens': 11, 'output_tokens': 2}}

    @property
    def evidence_calls(self):
        return [p for p in self.calls if p['state']['operation'] == 'branch_evidence']


class BranchingContractTests(unittest.TestCase):
    def setUp(self):
        self.search = importlib.import_module('scripts.bsb_jev_search')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'wiki').mkdir()
        (self.root / '.bsb-jev').mkdir()
        self.config()

    def config(self, enabled=True):
        (self.root / '.bsb-jev/config.json').write_text(json.dumps({
            'enabled': enabled, 'search_roots': ['wiki'],
            'model': 'jev-1.13.0', 'timeout': 1.0,
        }), encoding='utf-8')

    def page(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')
        return path

    def find(self, query='How does this work?', needs=None, service=None, **kwargs):
        return self.search.find(query, needs=needs, repo_root=self.root,
                                transport=service or ChoiceFixture(), api_key='fixture', **kwargs)

    def assert_output(self, result):
        for key in ('status', 'session_id', 'pages', 'evidence_refs', 'conflicts',
                    'unresolved_needs', 'coverage', 'usage', 'api_calls'):
            self.assertIn(key, result)
        self.assertFalse(result['coverage']['global_absence_proven'])
        self.assertEqual(len(result['pages']), len({p['path'] for p in result['pages']}))
        for page in result['pages']:
            data = (self.root / page['path']).read_bytes()
            self.assertEqual(page['text'], data.decode('utf-8'))
            self.assertTrue(page['full_page'])
            self.assertEqual(page['file_sha256'], hashlib.sha256(data).hexdigest())

    def test_german_paraphrase_admits_unindexed_unlinked_english_page(self):
        self.page('wiki/synchronization.md', '# Replication\nEVIDENCE: A replica applies a durable operation journal.\n')
        self.page('index.md', '# Catalog\nNo entries yet.\n')
        service = ChoiceFixture()
        result = self.find('Wie bleiben verteilte Kopien nach einem Ausfall gleich?',
                           needs=['Welche Schritte ermöglichen die Wiederherstellung?'], service=service)
        self.assert_output(result)
        self.assertEqual([p['path'] for p in result['pages']], ['wiki/synchronization.md'])
        self.assertTrue(result['evidence_refs'])
        self.assertFalse(result['unresolved_needs'])
        self.assertEqual(service.calls[0]['state']['operation'], 'branch_route')
        self.assertIn('Wiederherstellung', json.dumps(service.calls, ensure_ascii=False))

    def test_internally_backtracks_after_first_dead_end_and_follows_cycle_once(self):
        self.page('wiki/a.md', '# First branch\nHistorical background only. [[wiki/b]]\n')
        self.page('wiki/b.md', '# Second branch\nEVIDENCE: Durable checkpoint. [[wiki/a]]\n')
        service = ChoiceFixture()
        result = self.find(service=service)
        self.assert_output(result)
        self.assertIn('wiki/b.md', [p['path'] for p in result['pages']])
        self.assertGreaterEqual(len(service.evidence_calls), 2)
        evaluated = [p['state']['page']['path'] for p in service.evidence_calls]
        self.assertEqual(len(evaluated), len(set(evaluated)))
        self.assertLessEqual(result['api_calls'], 24)

    def test_all_explicit_needs_are_evaluated_independently(self):
        self.page('wiki/a.md', '# Recovery\nEVIDENCE: A checkpoint restores the state.\n')
        service = ChoiceFixture(coverage=lambda text, need: 'full' if need == 'n1' else 'none')
        result = self.find(needs=['How is recovery performed?', 'How is secrecy guaranteed?'], service=service)
        self.assert_output(result)
        self.assertTrue(result['unresolved_needs'])
        self.assertNotEqual(result['status'], 'ready')
        questions = set().union(*(p['questions'] for p in service.evidence_calls))
        self.assertTrue({'coverage_n1', 'coverage_n2', 'conflict_n1', 'conflict_n2'} <= questions)

    def test_evidence_at_end_of_long_page_is_reached_and_references_exact_lines(self):
        content = '# Log\n' + ''.join(f'Background entry {i:04d}: routine maintenance.\n' for i in range(1500))
        content += 'EVIDENCE: Recovery is available from the durable journal.\n'
        self.page('wiki/long.md', content)
        service = ChoiceFixture()
        result = self.find(service=service, max_calls=24)
        self.assert_output(result)
        self.assertTrue(result['evidence_refs'])
        self.assertEqual(result['pages'][0]['text'], content)
        self.assertTrue(any('durable journal' in block['text'] for p in service.evidence_calls
                            for block in p['state']['blocks'].values()))
        refs = [r for r in result['evidence_refs'] if r['path'] == 'wiki/long.md']
        self.assertTrue(any(r['start_line'] <= 1502 <= r['end_line'] for r in refs))
        for ref in refs:
            self.assertEqual(ref['file_sha256'], result['pages'][0]['file_sha256'])

    def test_conflicts_are_retained_separately_from_complete_support(self):
        self.page('wiki/a.md', '# Support\nEVIDENCE: Recovery always succeeds.\n')
        self.page('wiki/b.md', '# Exception\nCONTRARY: Recovery fails when the journal is missing.\n')
        result = self.find(service=ChoiceFixture())
        self.assert_output(result)
        self.assertEqual({p['path'] for p in result['pages']}, {'wiki/a.md', 'wiki/b.md'})
        self.assertTrue(result['conflicts'])
        self.assertIn('wiki/b.md', json.dumps(result['conflicts']))
        self.assertTrue(result['evidence_refs'])

    def test_unknown_is_retained_and_never_becomes_complete(self):
        self.page('wiki/a.md', '# Inconclusive\nEVIDENCE: The observation has not been reproduced.\n')
        service = ChoiceFixture(coverage=lambda *args: 'unknown', conflict=lambda *args: 'unknown')
        result = self.find(service=service)
        self.assert_output(result)
        self.assertTrue(result['pages'])
        self.assertTrue(result['unresolved_needs'])
        self.assertIn(result['status'], ('partial', 'unresolved'))

    def test_hard_call_budget_leaves_uncertainty_visible(self):
        for i in range(5):
            self.page(f'wiki/p{i}.md', '# Topic\nEVIDENCE: Relevant details.\n')
        service = ChoiceFixture()
        result = self.find(service=service, max_calls=1)
        self.assert_output(result)
        self.assertLessEqual(len(service.calls), 1)
        self.assertEqual(result['api_calls'], len(service.calls))
        self.assertNotEqual(result['status'], 'ready')
        self.assertTrue(result['unresolved_needs'])
        self.assertIn('unvisited', json.dumps(result['coverage']).lower())

    def test_hard_page_budget_reports_remaining_alternatives(self):
        for i in range(4):
            self.page(f'wiki/p{i}.md', '# Topic\nEVIDENCE: Relevant details.\n')
        service = ChoiceFixture()
        result = self.find(service=service, max_pages=1)
        self.assert_output(result)
        self.assertLessEqual(len({p['state']['page']['path'] for p in service.evidence_calls}), 1)
        self.assertNotEqual(result['status'], 'ready')
        self.assertIn('unvisited', json.dumps(result['coverage']).lower())

    def test_invalid_service_response_never_fabricates_success(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant details.\n')
        for response in ({'answers': {}}, {'model': 'jev-1.13.0', 'answers': {'invented': {}}}, None):
            with self.subTest(response=response):
                result = self.find(service=lambda *args: response)
                self.assert_output(result)
                self.assertIn(result['status'], ('unavailable', 'partial'))
                self.assertFalse(result['evidence_refs'])
                self.assertTrue(result['unresolved_needs'])

    def test_service_failure_is_explicit_and_does_not_invoke_fallback(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant details.\n')
        def failing(*args):
            raise RuntimeError('fixture service unavailable')
        result = self.find(service=failing)
        self.assert_output(result)
        self.assertIn(result['status'], ('unavailable', 'partial'))
        self.assertFalse(result['evidence_refs'])
        self.assertEqual(result['api_calls'], 1)

    def test_missing_credentials_return_unavailable_without_network(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant details.\n')
        with patch('scripts.bsb_jev.load_api_key', return_value=None):
            result = self.search.find('question', repo_root=self.root,
                                      transport=lambda *args: self.fail('network without credentials'))
        self.assert_output(result)
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['api_calls'], 0)
        self.assertTrue(result['unresolved_needs'])

    def test_disabled_and_dry_run_do_not_load_credentials_or_call_service(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant details.\n')
        def forbidden(*args):
            self.fail('Network call in disabled/dry run')
        with patch('scripts.bsb_jev.load_api_key', side_effect=AssertionError('credential access')):
            self.config(False)
            disabled = self.search.find('question', repo_root=self.root, transport=forbidden)
            self.config(True)
            dry = self.search.find('question', repo_root=self.root, dry_run=True, transport=forbidden)
        for result, expected in ((disabled, 'disabled'), (dry, 'dry_run')):
            self.assert_output(result)
            self.assertEqual(result['status'], expected)
            self.assertEqual(result['api_calls'], 0)

    def test_links_cannot_exfiltrate_files_outside_allowed_roots(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant. [[../private]] [[raw/secret]] [[wiki/../../private]]\n')
        self.page('private.md', 'PRIVATE_SENTINEL_DO_NOT_SEND')
        self.page('raw/secret.md', 'RAW_SENTINEL_DO_NOT_SEND')
        service = ChoiceFixture()
        result = self.find(service=service)
        self.assert_output(result)
        sent = json.dumps(service.calls)
        self.assertNotIn('PRIVATE_SENTINEL_DO_NOT_SEND', sent)
        self.assertNotIn('RAW_SENTINEL_DO_NOT_SEND', sent)
        self.assertEqual([p['path'] for p in result['pages']], ['wiki/a.md'])

    def test_change_during_service_evaluation_invalidates_snapshot(self):
        path = self.page('wiki/a.md', '# Topic\nEVIDENCE: Original facts.\n')
        def mutate(payload):
            if payload['state']['operation'] == 'branch_evidence':
                path.write_text('# Topic\nChanged after snapshot.\n', encoding='utf-8')
        result = self.find(service=ChoiceFixture(before=mutate))
        self.assertEqual(result['status'], 'stale')
        self.assertFalse(result['coverage']['global_absence_proven'])
        self.assertFalse(result['evidence_refs'])

    def test_public_result_omits_model_distributions_and_diagnostic_payloads(self):
        self.page('wiki/a.md', '# Topic\nEVIDENCE: Relevant details.\n')
        result = self.find()
        self.assert_output(result)
        def check(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key, ('probabilities', 'confidence', 'questions', 'answers', 'diagnostics'))
                    check(child)
            elif isinstance(value, list):
                for child in value:
                    check(child)
        check(result)
        self.assertLess(len(json.dumps(result)) - len(result['pages'][0]['text']), 10000)

    def test_long_page_budget_reports_unread_chunks(self):
        self.page('wiki/long.md', '# Log\n' + 'Background entry with maintenance detail.\n' * 1500
                  + 'EVIDENCE: Actual answer is at the end.\n')
        service = ChoiceFixture()
        result = self.find(service=service, max_calls=3)
        self.assert_output(result)
        self.assertLessEqual(len(service.calls), 3)
        self.assertGreater(result['coverage']['unread_chunks'], 0)
        self.assertFalse(result['coverage']['search_complete'])
        self.assertNotEqual(result['status'], 'ready')

    def test_full_coverage_without_a_source_location_cannot_prove_completion(self):
        self.page('wiki/a.md', '# Topic\nUnsupported service assertion.\n')
        result = self.find(service=ChoiceFixture(coverage=lambda *args: 'full'))
        self.assert_output(result)
        self.assertTrue(result['unresolved_needs'])
        self.assertNotEqual(result['status'], 'ready')
        self.assertFalse(result['evidence_refs'])


if __name__ == '__main__':
    unittest.main()
