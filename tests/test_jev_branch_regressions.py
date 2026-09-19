"""Regression tests for the final Jev branching review findings."""
import hashlib
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from test_jev_branching import ChoiceFixture
except ImportError:  # pragma: no cover - package-style test discovery
    from tests.test_jev_branching import ChoiceFixture


class _RetentionFixture(ChoiceFixture):
    """Make the second retention page conflict only when prior evidence is supplied."""

    def __init__(self):
        self.previous_by_page = {}
        self._current_previous = {}
        super().__init__(conflict=self._conflict, before=self._before)

    def _before(self, payload):
        state = payload['state']
        if state['operation'] != 'branch_evidence':
            return
        path = state['page']['path']
        self.previous_by_page[path] = state.get('previous_evidence', {})
        self._current_previous = state.get('previous_evidence', {})

    def _conflict(self, text, need):
        if '90 days' in text and self._current_previous.get(need):
            return 'present'
        return 'absent'


class JevBranchRegressionTests(unittest.TestCase):
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

    def find(self, query='What is the retention period?', service=None, **kwargs):
        return self.search.find(query, repo_root=self.root,
                                transport=service or ChoiceFixture(),
                                api_key='fixture', **kwargs)

    def test_conflict_judgment_receives_bounded_previous_supporting_evidence(self):
        self.page('wiki/a-30-days.md',
                  '# Retention baseline\nEVIDENCE: Records are retained for 30 days.\n')
        self.page('wiki/b-90-days.md',
                  '# Retention update\nEVIDENCE: Records are retained for 90 days.\n')
        service = _RetentionFixture()

        result = self.find(service=service)

        later_previous = service.previous_by_page.get('wiki/b-90-days.md', {})
        self.assertIn('n1', later_previous)
        self.assertTrue(later_previous['n1'])
        prior = later_previous['n1'][0]
        self.assertEqual(prior['path'], 'wiki/a-30-days.md')
        self.assertIn('30 days', prior['text'])
        self.assertTrue({'path', 'text', 'start_line', 'end_line', 'file_sha256'}
                        <= set(prior))
        self.assertLessEqual(prior['end_line'] - prior['start_line'] + 1, 8)
        self.assertEqual(prior['file_sha256'],
                         hashlib.sha256((self.root / prior['path']).read_bytes()).hexdigest())
        self.assertTrue(any(ref['path'] == 'wiki/b-90-days.md'
                            for ref in result['conflicts']))

    def test_output_budget_keeps_compact_conflicts_and_omitted_page_descriptors(self):
        self.page('wiki/a-support.md', '# Support\nEVIDENCE: Recovery succeeds.\n')
        contrary = self.page('wiki/b-contrary.md',
                             '# Exception\nCONTRARY: Recovery fails when the journal is missing.\n')
        service = ChoiceFixture()

        with patch.object(self.search, 'MAX_RETURN_BYTES', 1):
            result = self.find(service=service)

        self.assertFalse(result['pages'])
        omitted = result['omitted_pages']
        self.assertTrue(omitted)
        omitted_contrary = [item for item in omitted
                            if item['path'] == 'wiki/b-contrary.md']
        self.assertTrue(omitted_contrary)
        descriptor = omitted_contrary[0]
        self.assertEqual(descriptor['file_sha256'],
                         hashlib.sha256(contrary.read_bytes()).hexdigest())
        self.assertNotIn('text', descriptor)
        self.assertNotIn('full_page', descriptor)
        self.assertNotIn('CONTRARY', json.dumps(descriptor))
        self.assertTrue(any(item['path'] == 'wiki/b-contrary.md'
                            for item in result['conflicts']))
        self.assertNotIn('CONTRARY: Recovery fails when the journal is missing.',
                         json.dumps(result['conflicts']))

    def test_invalid_optional_index_marks_catalog_incomplete_and_keeps_allowed_pages(self):
        self.page('wiki/allowed.md', '# Allowed\nEVIDENCE: The allowed page is readable.\n')
        (self.root / 'index.md').write_bytes(b'# Catalog\ninvalid utf-8: \xff\xfe\n')

        result = self.find()

        self.assertEqual(result['coverage'].get('index_status'), 'unreadable')
        self.assertFalse(result['coverage']['scan_complete'])
        self.assertEqual([page['path'] for page in result['pages']], ['wiki/allowed.md'])


if __name__ == '__main__':
    unittest.main()
