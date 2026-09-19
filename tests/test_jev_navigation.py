import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import bsb_jev_navigation as nav


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'wiki').mkdir()
        (self.root / '.bsb-jev').mkdir()
        (self.root / '.bsb-jev/config.json').write_text('{"enabled":false}')
        (self.root / 'wiki/a.md').write_text('---\ntitle: Alpha\naliases: [First]\n---\nExact https://example.org/source\n[[wiki/b]]\n')
        (self.root / 'wiki/b.md').write_text('# Beta\nComplementary configuration.\n')

    def tearDown(self):
        self.tmp.cleanup()

    def set_enabled(self, enabled=True):
        (self.root / '.bsb-jev/config.json').write_text(json.dumps({
            'enabled': bool(enabled), 'search_roots': ['wiki'],
            'model': 'jev-1.13.0', 'timeout': 1.0,
        }))

    def test_exact_source_has_local_receipt_and_full_page_read(self):
        with patch('scripts.bsb_jev.load_api_key', side_effect=AssertionError('network')):
            result = nav.source('https://example.org/source', self.root)
            self.assertEqual(result['coverage']['matched_files'], 1)
            self.assertEqual(result['api_calls'], 0)
            page = nav.read_page(result['session_id'], 'wiki/a.md', self.root)
        self.assertEqual(page['text'], (self.root / 'wiki/a.md').read_bytes().decode('utf-8'))
        self.assertEqual(page['links'], ['wiki/b.md'])
        self.assertFalse(result['coverage']['global_absence_proven'])

    def test_stale_and_unoffered_pages_refused(self):
        result = nav.source('First', self.root)
        with self.assertRaises(ValueError):
            nav.read_page(result['session_id'], 'wiki/b.md', self.root)
        (self.root / 'wiki/a.md').write_text('Changed')
        with self.assertRaises(ValueError):
            nav.read_page(result['session_id'], 'wiki/a.md', self.root)

    def test_missing_literal_is_scoped_not_global(self):
        result = nav.source('absent-source', self.root)
        self.assertEqual(result['matches'], [])
        self.assertTrue(result['coverage']['scan_complete'])
        self.assertEqual(result['coverage']['files_scanned'], 2)
        self.assertFalse(result['coverage']['global_absence_proven'])

    def test_session_tampering_and_traversal_rejected(self):
        result = nav.source('Alpha', self.root)
        path = self.root / '.bsb-jev' / (result['session_id'] + '.json')
        data = json.loads(path.read_text()); data['offered'] += ['wiki/b.md']
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            nav.read_page(result['session_id'], 'wiki/b.md', self.root)
        with self.assertRaises(ValueError):
            nav.read_page('../../secret', '../secret', self.root)

    def test_dry_source_has_no_state_mutation(self):
        before = sorted(p.name for p in (self.root / '.bsb-jev').iterdir())
        result = nav.source('First', self.root, dry_run=True)
        self.assertIsNone(result['session_id'])
        self.assertEqual(before, sorted(p.name for p in (self.root / '.bsb-jev').iterdir()))

    def test_unsafe_link_and_raw_outside_roots_are_not_followed(self):
        (self.root / 'wiki/a.md').write_text('Alpha [[../outside]] [[raw/private]] [[wiki/b]]')
        result = nav.source('Alpha', self.root)
        page = nav.read_page(result['session_id'], 'wiki/a.md', self.root)
        self.assertEqual(page['links'], ['wiki/b.md'])

    def test_source_cap_reports_truncation(self):
        with patch.object(nav, 'MAX_SCAN_FILES', 1):
            result = nav.source('Alpha', self.root)
        self.assertFalse(result['coverage']['scan_complete'])

    def test_next_follows_link_and_reads_entire_new_page_offline(self):
        result = nav.source('Alpha', self.root)
        nav.read_page(result['session_id'], 'wiki/a.md', self.root)
        with patch('scripts.bsb_jev.load_api_key', side_effect=AssertionError('off must stay local')):
            step = nav.next_step(result['session_id'], self.root)
        self.assertEqual([d['path'] for d in step['initial']], ['wiki/b.md'])
        page = nav.read_page(result['session_id'], 'wiki/b.md', self.root)
        self.assertIn('Complementary configuration.', page['text'])

    def test_changing_roots_invalidates_old_session(self):
        result = nav.source('Alpha', self.root)
        (self.root / '.bsb-jev/config.json').write_text('{"enabled":false,"search_roots":["other"]}')
        with self.assertRaises(ValueError):
            nav.read_page(result['session_id'], 'wiki/a.md', self.root)

    def test_navigation_dry_run_keeps_no_receipts(self):
        before = sorted(p.name for p in (self.root / '.bsb-jev').iterdir())
        with patch('scripts.bsb_jev.load_api_key', side_effect=AssertionError('no credential')):
            plan = nav.navigate('Alpha', ['Which source?'], self.root, dry_run=True)
        self.assertIsNone(plan['session_id'])
        self.assertNotIn('excerpts', plan)
        self.assertEqual(before, sorted(p.name for p in (self.root / '.bsb-jev').iterdir()))

    def test_changed_deferred_page_rejects_next_without_resigning(self):
        result = nav.source('Alpha', self.root)
        (self.root / 'wiki/a.md').write_text('Changed')
        with self.assertRaises(ValueError):
            nav.next_step(result['session_id'], self.root)

    def test_recommended_next_advances_through_deferred_pages_without_repeating(self):
        for name in ('c.md', 'd.md'):
            (self.root / 'wiki' / name).write_text('topic context without the exact answer\n')
        self.set_enabled(True)

        def transport(payload, key, model, timeout):
            answers = {}
            for qid, _question in payload['questions'].items():
                document_id, _need_id = qid.rsplit(':', 1)
                document = payload['state']['documents'][document_id]['text']
                choice = 'direct' if document_id == 'c1' and 'Exact' in document else 'none'
                probabilities = {v: 0.0 for v in ('direct', 'partial', 'contrary', 'none', 'unknown')}
                probabilities[choice] = 1.0
                answers[qid] = {'type': 'choice', 'choice': choice, 'confidence': 0.9, 'probabilities': probabilities}
            return {'model': 'jev-1.13.0', 'answers': answers, 'usage': {'input_tokens': 1, 'output_tokens': 1}}

        # Make the exact page lexical rank first and keep the other two as the
        # deferred pool. The navigation layer must not re-offer the first page.
        (self.root / 'wiki/a.md').write_text('Exact topic answer\n[[wiki/c]]\n')
        first = nav.navigate('topic', ['What is the exact answer?'], self.root, transport=transport, api_key='test-key')
        self.assertEqual([d['path'] for d in first['initial']], ['wiki/a.md'])
        nav.read_page(first['session_id'], 'wiki/a.md', self.root)
        second = nav.next_step(first['session_id'], self.root, transport=transport, api_key='test-key')
        self.assertEqual([d['path'] for d in second['initial']], ['wiki/c.md'])
        nav.read_page(first['session_id'], 'wiki/c.md', self.root)
        third = nav.next_step(first['session_id'], self.root, transport=transport, api_key='test-key')
        self.assertEqual([d['path'] for d in third['initial']], ['wiki/d.md'])

    def test_unreadable_frontier_is_pruned_so_later_links_can_progress(self):
        (self.root / 'wiki/a.md').write_text('topic [[wiki/missing]] [[wiki/b]]\n')
        (self.root / 'wiki/b.md').write_text('topic second page\n')
        self.set_enabled(False)
        first = nav.source('[[wiki/b]]', self.root)
        nav.read_page(first['session_id'], 'wiki/a.md', self.root)
        step = nav.next_step(first['session_id'], self.root)
        self.assertIn('wiki/missing.md', step.get('skipped_paths', []))
        self.assertEqual(step['status'], 'disabled')
        nav.read_page(first['session_id'], 'wiki/b.md', self.root)


if __name__ == '__main__':
    unittest.main()
