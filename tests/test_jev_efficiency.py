"""Independent regressions for bounded Jev request overhead.

These tests exercise the frozen v2 efficiency contract without making network
calls.  The transport fixture is reused only for deterministic gateway
control-flow checks.
"""
import copy
import hashlib
import importlib
import json
import tempfile
import unittest
from pathlib import Path

try:
    from test_jev_branching import ChoiceFixture
except ImportError:  # pragma: no cover - package-style test discovery
    from tests.test_jev_branching import ChoiceFixture


class JevEfficiencyTests(unittest.TestCase):
    def setUp(self):
        self.search = importlib.import_module('scripts.bsb_jev_search')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'wiki').mkdir()
        (self.root / '.bsb-jev').mkdir()
        (self.root / '.bsb-jev/config.json').write_text(json.dumps({
            'enabled': True,
            'search_roots': ['wiki'],
            'model': 'jev-1.13.0',
            'timeout': 1.0,
        }), encoding='utf-8')

    def page(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')
        return path

    def find(self, query='How does this work?', service=None, **kwargs):
        return self.search.find(query, repo_root=self.root,
                                transport=service or ChoiceFixture(),
                                api_key='fixture', **kwargs)

    def test_heading_rich_text_packs_to_byte_bound_without_splitting_at_headings(self):
        prefix = ''.join(
            f'context line {i:03d}: ' + ('x' * 48) + '\n'
            for i in range(60)
        )
        headings = ''.join(
            f'# Section {i:03d}\nsection detail {i:03d}: ' + ('y' * 36) + '\n'
            for i in range(30)
        )
        text = prefix + headings

        self.assertGreater(len(prefix.encode('utf-8')), 1000)
        self.assertLessEqual(len(text.encode('utf-8')), self.search.CHUNK_BYTES)

        blocks = self.search._blocks(text)

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]['text'], text)
        self.assertEqual(blocks[0]['start_line'], 1)
        self.assertEqual(blocks[0]['end_line'], len(text.splitlines()))
        self.assertLessEqual(len(blocks[0]['text'].encode('utf-8')), self.search.CHUNK_BYTES)
        self.assertFalse(blocks[0].get('oversized', False))

    def test_heading_rich_page_needs_one_evidence_request_when_under_chunk_bound(self):
        prefix = ''.join(
            f'context line {i:03d}: ' + ('x' * 48) + '\n'
            for i in range(60)
        )
        headings = ''.join(
            f'# Section {i:03d}\nsection detail {i:03d}: ' + ('y' * 36) + '\n'
            for i in range(28)
        )
        text = prefix + headings + 'EVIDENCE: the final section contains the answer.\n'
        self.assertLessEqual(len(text.encode('utf-8')), self.search.CHUNK_BYTES)
        self.page('wiki/heading-rich.md', text)
        service = ChoiceFixture()

        result = self.find(service=service, max_calls=24)

        self.assertEqual(len(service.evidence_calls), 1)
        self.assertEqual(result['coverage']['unread_chunks'], 0)
        self.assertTrue(result['evidence_refs'])
        self.assertEqual(result['pages'][0]['text'], text)

    def test_oversized_line_remains_explicitly_unread_without_losing_neighbors(self):
        oversized = 'Z' * (self.search.CHUNK_BYTES + 1) + '\n'
        text = 'before\n' + oversized + 'after\n'

        blocks = self.search._blocks(text)

        self.assertEqual([block.get('oversized', False) for block in blocks],
                         [False, True, False])
        self.assertEqual(''.join(block['text'] for block in blocks), text)
        self.assertEqual((blocks[1]['start_line'], blocks[1]['end_line']), (2, 2))
        self.assertEqual(blocks[1]['text'], oversized)
        self.assertEqual(blocks[0]['text'], 'before\n')
        self.assertEqual(blocks[2]['text'], 'after\n')

    def test_oversized_line_marks_search_incomplete_even_when_later_evidence_is_found(self):
        oversized = 'Z' * (self.search.CHUNK_BYTES + 1) + '\n'
        text = '# Topic\n' + oversized + 'EVIDENCE: answer follows the unread line.\n'
        self.page('wiki/oversized.md', text)

        result = self.find(service=ChoiceFixture(), max_calls=24)

        self.assertGreater(result['coverage']['unread_chunks'], 0)
        self.assertFalse(result['coverage']['search_complete'])
        self.assertEqual(result['pages'][0]['text'], text)
        self.assertTrue(result['evidence_refs'])

    def test_caller_result_keeps_sources_refs_conflicts_gaps_coverage_and_session(self):
        selected_text = '# Selected\nEVIDENCE: exact source bytes.\n'
        selected_hash = hashlib.sha256(selected_text.encode('utf-8')).hexdigest()
        detailed = {
            'status': 'partial',
            'session_id': 'nav-0123456789abcdef0123456789abcdef',
            'pages': [{
                'path': 'wiki/selected.md',
                'text': selected_text,
                'file_sha256': selected_hash,
                'full_page': True,
                'title': 'Verbose catalog title',
                'bytes': len(selected_text.encode('utf-8')),
            }],
            'evidence_refs': [{
                'path': 'wiki/selected.md',
                'file_sha256': selected_hash,
                'need_id': 'n1',
                'start_line': 2,
                'end_line': 2,
                'relation': 'full',
                'provisional': True,
                'full_page_returned': True,
            }],
            'conflicts': [{
                'path': 'wiki/contrary.md',
                'file_sha256': 'c' * 64,
                'need_id': 'n1',
                'start_line': 4,
                'end_line': 8,
                'relation': 'contrary',
                'provisional': True,
                'full_page_returned': False,
            }],
            'unresolved_needs': ['What remains unknown?'],
            'coverage': {
                'catalog_pages': 3,
                'evaluated_pages': 2,
                'unvisited_pages': 1,
                'unread_chunks': 1,
                'search_complete': False,
                'stop_reason': 'request_budget',
                'global_absence_proven': False,
                'output_omitted_pages': 1,
                'returned_bytes': len(selected_text.encode('utf-8')),
            },
            'omitted_pages': [{
                'path': 'wiki/contrary.md',
                'file_sha256': 'c' * 64,
                'title': 'Verbose omitted title',
                'bytes': 9000,
            }],
            # These are local diagnostics and must not cross the caller boundary.
            'usage': [{'input_tokens': 900, 'output_tokens': 40}],
            'api_calls': 7,
            'model': 'jev-1.13.0',
            'trace': [{'operation': 'branch_evidence', 'answers': {}}],
            'diagnostics': {'probabilities': {'full': 1.0}},
        }
        original = copy.deepcopy(detailed)

        compact = self.search.caller_result(detailed)

        self.assertEqual(detailed, original)
        for key in ('status', 'session_id', 'unresolved_needs', 'coverage'):
            self.assertIn(key, compact)
            self.assertEqual(compact[key], detailed[key])
        self.assertEqual(compact['pages'][0]['path'], 'wiki/selected.md')
        self.assertEqual(compact['pages'][0]['text'], selected_text)
        self.assertEqual(compact['pages'][0]['file_sha256'], selected_hash)
        self.assertTrue(compact['pages'][0].get('full_page', True))
        self.assertEqual(
            {(ref['path'], ref['file_sha256'], ref['need_id'], ref['start_line'],
              ref['end_line'], ref['relation']) for ref in compact['evidence_refs']},
            {('wiki/selected.md', selected_hash, 'n1', 2, 2, 'full')},
        )
        self.assertEqual(
            {(ref['path'], ref['file_sha256'], ref['need_id'], ref['start_line'],
              ref['end_line'], ref['relation']) for ref in compact['conflicts']},
            {('wiki/contrary.md', 'c' * 64, 'n1', 4, 8, 'contrary')},
        )
        self.assertEqual(compact['omitted_pages'][0]['path'], 'wiki/contrary.md')
        self.assertEqual(compact['omitted_pages'][0]['file_sha256'], 'c' * 64)
        for key in ('usage', 'api_calls', 'model', 'trace', 'diagnostics'):
            self.assertNotIn(key, compact)
        for page in compact['pages'] + compact['omitted_pages']:
            self.assertNotIn('title', page)
            self.assertNotIn('bytes', page)


if __name__ == '__main__':
    unittest.main()
