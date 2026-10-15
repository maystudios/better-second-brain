"""Behavioral tests for the optional local retrieval-first stage (docs/local-search.md).

No network: the Jev transport is the deterministic ChoiceFixture and the
embedding backend is a stub. The single real-model smoke test is skipped unless
the optional packages import and BSB_LOCAL_SMOKE=1 is set.
"""
import contextlib
import hashlib
import importlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from test_jev_branching import ChoiceFixture
except ImportError:  # pragma: no cover - package-style test discovery
    from tests.test_jev_branching import ChoiceFixture

REPO = Path(__file__).resolve().parents[1]
API_KEY_LIKE = 'apikey_' + '0' * 32 + '_' + '1' * 64


class StubEmbedder:
    """Deterministic vectors: a marker in the text selects the direction."""

    name = 'stub-embedder'
    directions = {'VEC_A': [1.0, 0.0, 0.0], 'VEC_B': [0.0, 1.0, 0.0], 'VEC_C': [0.0, 0.6, 0.8]}

    def __init__(self, query_vector=(0.1, 0.99, 0.0)):
        self.query_vector = list(query_vector)
        self.calls = []

    def encode(self, texts):
        self.calls.append(list(texts))
        out = []
        for text in texts:
            if text.startswith('task: search result | query: '):
                out.append(self.query_vector)
                continue
            vector = [0.01, 0.01, 0.01]
            for marker, direction in self.directions.items():
                if marker in text:
                    vector = direction
            out.append(vector)
        return out


class LocalTestCase(unittest.TestCase):
    def setUp(self):
        self.local = importlib.import_module('scripts.bsb_local_search')
        self.search = importlib.import_module('scripts.bsb_jev_search')
        self.core = importlib.import_module('scripts.bsb_jev')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'brain'
        self.state = Path(self.tmp.name) / 'state'
        (self.root / 'wiki').mkdir(parents=True)
        (self.root / '.bsb-jev').mkdir()
        env = patch.dict(os.environ, {'BSB_LOCAL_STATE': str(self.state)})
        env.start()
        self.addCleanup(env.stop)
        for name in ('BSB_LOCAL_BACKEND', 'BSB_LOCAL_MODEL', 'BSB_LOCAL_PAGES', 'BSB_LOCAL_SEEDS',
                     'BSB_LOCAL_MIN_MARGIN', 'BSB_LOCAL_MIN_COVERAGE'):
            os.environ.pop(name, None)
        self.config()

    def config(self, **fields):
        data = {'enabled': True, 'search_roots': ['wiki'], 'model': 'jev-1.13.0', 'timeout': 1.0}
        data.update(fields)
        (self.root / '.bsb-jev/config.json').write_text(json.dumps(data), encoding='utf-8')

    def page(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8', newline='')
        return path

    def engine(self, **kwargs):
        return self.local.LocalSearch(self.root, **kwargs)

    def query(self, text, limit=5, **kwargs):
        with self.engine(**kwargs) as engine:
            return engine.search(text, limit=limit)

    def paths(self, result):
        return [r['path'] for r in result['results']]


class IndexingTests(LocalTestCase):
    def test_chunks_carry_heading_path_and_exact_line_ranges(self):
        text = ('---\ntitle: Sample\n---\n# Sample\nIntro text.\n\n## Setup\nInstall step.\n'
                '```sh\n# not a heading\n```\n### Detail\nDeep text.\n')
        _, chunks = self.local.chunk_markdown(text)
        self.assertEqual([(c['heading'], c['start_line'], c['end_line']) for c in chunks],
                         [('Sample', 4, 5), ('Sample > Setup', 7, 11), ('Sample > Setup > Detail', 12, 13)])
        lines = text.splitlines()
        for chunk in chunks:
            self.assertEqual(chunk['text'], '\n'.join(lines[chunk['start_line'] - 1:chunk['end_line']]))

    def test_incremental_update_tracks_create_change_touch_delete(self):
        a = self.page('wiki/a.md', '# Alpha\nzebra stripes.\n')
        self.page('wiki/b.md', '# Beta\nunrelated words.\n')
        with self.engine() as engine:
            first = engine.update()
            self.assertEqual((first['added'], first['pages']), (2, 2))
            self.assertEqual(self.paths(engine.search('zebra', update=False)), ['wiki/a.md'])
            a.write_text('# Alpha\ngiraffe necks are long.\n', encoding='utf-8', newline='')
            second = engine.update()
            self.assertEqual((second['changed'], second['unchanged']), (1, 1))
            self.assertEqual(engine.search('zebra', update=False)['results'], [])
            self.assertEqual(self.paths(engine.search('giraffe', update=False)), ['wiki/a.md'])
            stamp = time.time() + 5
            os.utime(a, (stamp, stamp))
            third = engine.update()
            self.assertEqual((third['touched'], third['changed']), (1, 0))
            a.unlink()
            fourth = engine.update()
            self.assertEqual((fourth['removed'], fourth['pages']), (1, 1))
            self.assertEqual(engine.search('giraffe', update=False)['results'], [])

    def test_search_refreshes_index_on_every_call(self):
        self.page('wiki/a.md', '# Alpha\nplain text.\n')
        self.assertEqual(self.query('okapi')['results'], [])
        self.page('wiki/new.md', '# New\nThe okapi is shy.\n')
        self.assertEqual(self.paths(self.query('okapi')), ['wiki/new.md'])

    def test_secret_and_excluded_files_are_never_indexed(self):
        for name in ('wiki/.env.md', 'wiki/prod.key.md', 'wiki/cert.pem.md', 'wiki/store.pfx.md',
                     'wiki/.obsidian/a.md', 'wiki/.trash/b.md', 'wiki/.git/c.md', 'wiki/.bsb-jev/d.md',
                     'wiki/sub/.hidden.md', 'raw/outside.md'):
            self.page(name, '# Hidden\nsecretword appears here.\n')
        self.page('wiki/leak.md', f'# Leak\nsecretword {API_KEY_LIKE}\n')
        self.page('wiki/ok.md', '# Ok\nvisible text only.\n')
        result = self.query('secretword')
        self.assertEqual(result['results'], [])
        with self.engine() as engine:
            indexed = [r[0] for r in engine.conn.execute('SELECT path FROM pages')]
            report = engine.update()
        self.assertEqual(indexed, ['wiki/ok.md'])
        self.assertGreaterEqual(report['skipped']['hidden_or_secret_name'], 5)
        self.assertGreaterEqual(report['skipped']['excluded_dirs'], 4)

    def test_hidden_or_excluded_configured_roots_are_refused(self):
        for folder in ('wiki/.git', 'wiki/.obsidian', 'wiki/.trash', 'wiki/.bsb-jev', 'wiki/sub/.hidden'):
            self.page(f'{folder}/private.md', '# Private\nsecretword inside an excluded folder.\n')
        for folder in ('wiki/.git', 'wiki/.obsidian', 'wiki/.trash', 'wiki/.bsb-jev', 'wiki/sub/.hidden'):
            with self.subTest(root=folder), self.assertRaises(ValueError):
                self.local.LocalSearch(self.root, roots=[folder]).close()
        self.config(local_first=True, search_roots=['wiki/.git'])
        found = self.search.find('secretword', repo_root=self.root, dry_run=True)
        self.assertEqual((found['source'], found['local']['reason']), ('jev', 'local_unavailable:ValueError'))
        self.assertNotIn('private', json.dumps(found.get('local', {})))

    def test_scan_skips_candidates_with_an_excluded_component(self):
        self.page('wiki/.git/private.md', '# Private\nsecretword.\n')
        with self.engine() as engine:
            engine.roots = ['wiki/.git']  # defence in depth below the root check
            files, skipped, _ = engine.scan()
        self.assertEqual(files, [])
        self.assertEqual(skipped['excluded_dirs'], 1)

    def test_secret_markdown_variants_are_never_indexed(self):
        secret = ('credentials.json.md', 'id_rsa.md', 'id_ed25519.md', 'id_ecdsa.md', '.env.production.md',
                  'server.pem.md', 'tls.key.md', 'cert.pfx.md', 'bundle.p12.md', 'gcp-credentials.json.md')
        for name in secret:
            self.assertTrue(self.local._secret_name(name), name)
        for name in ('credential-rotation.md', 'keyboard.md', 'notes.md', 'pem-format.md'):
            self.assertFalse(self.local._secret_name(name), name)
        for name in secret:
            self.page('wiki/' + name, '# Leak\nsecretword appears here.\n')
        self.assertEqual(self.query('secretword')['results'], [])

    def test_status_reports_pending_changes_without_updating(self):
        self.page('wiki/a.md', '# Alpha\nzebra.\n')
        with self.engine() as engine:
            engine.update()
        self.page('wiki/b.md', '# Beta\nokapi.\n')
        with self.engine() as engine:
            status = engine.status()
        self.assertEqual((status['pages'], status['pending_changes']), (1, 1))
        self.assertEqual(status['api_calls'], 0)


class RankingTests(LocalTestCase):
    def test_bm25_ranks_the_page_with_the_rare_terms_first(self):
        self.page('wiki/target.md', '# Notes\nThe quorum lease renewal uses a quorum lease timer.\n')
        for i in range(5):
            self.page(f'wiki/other{i}.md', f'# Other {i}\nA general note about timers and renewal.\n')
        result = self.query('How does quorum lease renewal work?')
        self.assertEqual(result['results'][0]['path'], 'wiki/target.md')
        self.assertEqual(result['results'][0]['keyword_rank'], 1)
        self.assertGreater(result['results'][0]['keyword_score'], result['results'][1]['keyword_score'])

    def test_exact_title_and_alias_beat_repeated_body_mentions(self):
        self.page('wiki/concepts/quokka-protocol.md',
                  '---\ntitle: Quokka Protocol\naliases:\n  - QP handshake\n---\n# Quokka Protocol\nA short definition.\n')
        self.page('wiki/notes/diary.md', '# Diary\n' + 'I discussed the quokka protocol and the QP handshake.\n' * 12)
        by_title = self.query('What is the Quokka Protocol?')
        self.assertEqual(by_title['results'][0]['path'], 'wiki/concepts/quokka-protocol.md')
        self.assertEqual(by_title['results'][0]['name_match'], 'exact')
        self.assertEqual(by_title['confidence']['rule'], 'exact_name')
        by_alias = self.query('QP handshake')
        self.assertEqual(by_alias['results'][0]['path'], 'wiki/concepts/quokka-protocol.md')

    def test_wikilink_display_name_routes_to_the_link_target(self):
        self.page('wiki/entities/x7.md', '# X7\nInternal codename page.\n')
        self.page('wiki/notes/log.md', '# Log\nWe shipped [[wiki/entities/x7|Nebula Engine]] after the Nebula Engine review.\n')
        result = self.query('Nebula Engine')
        self.assertEqual(result['results'][0]['path'], 'wiki/entities/x7.md')
        self.assertEqual(result['results'][0]['name_match'], 'exact')

    def test_confidence_thresholds_are_configurable(self):
        self.page('wiki/target.md', '# Notes\nThe quorum lease renewal uses a quorum lease timer.\n')
        self.page('wiki/other.md', '# Other\nA renewal note.\n')
        question = 'quorum lease renewal'
        loose = dict(self.local.DEFAULTS, local_min_margin=0.0, local_min_coverage=0.0)
        strict = dict(loose, local_min_margin=0.99)
        with self.engine() as engine:
            engine.update()
            self.assertEqual(engine.search(question, update=False, options=loose)['confidence']['rule'],
                             'keyword_margin')
            decision = engine.search(question, update=False, options=strict)['confidence']
            self.assertFalse(decision['confident'])
            self.assertEqual(decision['reason'], 'keyword_margin_below_threshold')
            coverage = dict(loose, local_min_coverage=1.0)
            decision = engine.search(question + ' absentword', update=False, options=coverage)['confidence']
            self.assertEqual(decision['reason'], 'term_coverage_below_threshold')


class BackendTests(LocalTestCase):
    def test_rrf_fuses_ranks_and_boosts_exact_names(self):
        fused = self.local.rrf({'keyword': ['a', 'b'], 'vector': ['b', 'c']})
        self.assertEqual([p for p, _ in fused], ['b', 'a', 'c'])
        self.assertAlmostEqual(dict(fused)['b'], 1 / 62 + 1 / 61)
        boosted = self.local.rrf({'keyword': ['a', 'b']}, boost=['b'])
        self.assertEqual(boosted[0][0], 'b')

    def test_hybrid_fusion_and_route_agreement_with_stub_embedder(self):
        self.page('wiki/p1.md', '# One\norbit orbit orbit telemetry VEC_A\n')
        self.page('wiki/p2.md', '# Two\norbit telemetry VEC_B\n')
        self.page('wiki/p3.md', '# Three\nunrelated VEC_C\n')
        with self.engine(embedder=StubEmbedder()) as engine:
            result = engine.search('orbit telemetry')
        self.assertEqual(result['backend'], 'hybrid')
        ranks = {r['path']: (r['keyword_rank'], r['vector_rank']) for r in result['results']}
        self.assertEqual(ranks['wiki/p1.md'], (1, 3))
        self.assertEqual(ranks['wiki/p2.md'], (2, 1))
        self.assertEqual(self.paths(result), ['wiki/p2.md', 'wiki/p1.md', 'wiki/p3.md'])
        self.assertFalse(result['confidence']['confident'])
        self.assertEqual(result['confidence']['reason'], 'routes_disagree')
        with self.engine(embedder=StubEmbedder(query_vector=(1.0, 0.0, 0.0))) as engine:
            agreed = engine.search('orbit telemetry')
        self.assertEqual(agreed['results'][0]['path'], 'wiki/p1.md')
        self.assertEqual(agreed['confidence']['rule'], 'route_agreement')

    def test_prompts_float32_matrix_and_incremental_embedding(self):
        self.page('wiki/p1.md', '# One\norbit VEC_A\n')
        self.page('wiki/p2.md', '---\ntitle: Second\n---\n# Two\norbit VEC_B\n')
        stub = StubEmbedder()
        with self.engine(embedder=stub) as engine:
            report = engine.update()
            self.assertEqual(report['vectors'], {'embedded': 2, 'rows': 2, 'dim': 3})
            documents = [t for batch in stub.calls for t in batch]
            self.assertIn('title: One | text: # One\norbit VEC_A', documents)
            self.assertIn('title: Second | text: # Two\norbit VEC_B', documents)
            engine.search('orbit', update=False)
            self.assertEqual(stub.calls[-1], ['task: search result | query: orbit'])
            self.page('wiki/p2.md', '---\ntitle: Second\n---\n# Two\norbit changed VEC_B\n')
            self.assertEqual(engine.update()['vectors']['embedded'], 1)
        data = (self.state / 'vectors.f32').read_bytes()
        meta = json.loads((self.state / 'vectors.json').read_text(encoding='utf-8'))
        self.assertEqual((meta['dtype'], meta['dim'], len(meta['keys'])), ('float32', 3, 2))
        self.assertEqual(len(data), 2 * 3 * 4)

    def test_missing_optional_packages_fall_back_to_keyword(self):
        self.page('wiki/a.md', '# Alpha\nzebra stripes.\n')
        with patch.object(self.local, 'packages_available', return_value=False):
            result = self.query('zebra', backend='hybrid')
            self.assertEqual(result['backend'], 'keyword')
            self.assertEqual(result['backend_fallback'], 'optional_packages_missing')
            self.assertEqual(self.paths(result), ['wiki/a.md'])
            self.config(local_first=True, local_backend='hybrid', enabled=False)
            found = self.search.find('What are zebra stripes?', repo_root=self.root)
        self.assertEqual(found['local']['backend'], 'keyword')
        self.assertEqual(found['local']['backend_fallback'], 'optional_packages_missing')

    @unittest.skipUnless(os.environ.get('BSB_LOCAL_SMOKE') == '1', 'set BSB_LOCAL_SMOKE=1 to load the real model')
    def test_real_embedding_model_smoke(self):
        if not importlib.import_module('scripts.bsb_local_search').packages_available():
            self.skipTest('sentence-transformers / torch not installed')
        self.page('wiki/a.md', '# Parking\nThe valet parks the car in the garage.\n')
        self.page('wiki/b.md', '# Weather\nRain falls in spring.\n')
        result = self.query('Where does the valet put vehicles?', backend='hybrid')
        self.assertEqual(result['backend'], 'hybrid', result.get('backend_fallback'))
        self.assertIn(result['dtype'], {'bfloat16', 'float32'})
        self.assertEqual(result['results'][0]['path'], 'wiki/a.md')


class FindLocalFirstTests(LocalTestCase):
    def setUp(self):
        super().setUp()
        self.page('wiki/concepts/quokka-protocol.md',
                  '---\ntitle: Quokka Protocol\n---\n# Quokka Protocol\nEVIDENCE: The handshake has three steps.\n')
        self.page('wiki/concepts/zebra-registry.md', '# Zebra Registry\nEVIDENCE: Registry entries expire daily.\n')
        self.page('wiki/notes/a.md', '# Notes A\nEVIDENCE: shared ambiguous wording about lanterns.\n')
        self.page('wiki/notes/b.md', '# Notes B\nEVIDENCE: shared ambiguous wording about lanterns.\n')

    def no_transport(self, *args):
        self.fail('Jev transport must not be called')

    def assert_page_bytes(self, page):
        data = (self.root / page['path']).read_bytes()
        self.assertEqual(page['text'], data.decode('utf-8'))
        self.assertEqual(page['file_sha256'], hashlib.sha256(data).hexdigest())
        self.assertTrue(page['full_page'])

    def test_confident_local_returns_full_pages_without_key_or_transport(self):
        self.config(local_first=True)
        with patch.object(self.core, 'load_api_key', side_effect=AssertionError('credential loaded')):
            result = self.search.find('What is the Quokka Protocol?', repo_root=self.root,
                                      transport=self.no_transport)
        self.assertEqual((result['status'], result['source'], result['api_calls']), ('local', 'local', 0))
        self.assertEqual(result['pages'][0]['path'], 'wiki/concepts/quokka-protocol.md')
        for page in result['pages']:
            self.assert_page_bytes(page)
        self.assertLessEqual(len(result['pages']), 3)
        self.assertIsNone(result['session_id'])
        self.assertEqual(result['local']['decisions']['n1']['rule'], 'exact_name')
        self.assertFalse(result['coverage']['global_absence_proven'])
        packet = self.search.caller_result(result)
        self.assertEqual((packet['source'], packet['api_calls']), ('local', 0))
        self.assertEqual(packet['evidence_refs'][0]['relation'], 'local_match')

    def test_each_explicit_need_must_be_confident(self):
        self.config(local_first=True)
        both = self.search.find('Compare the protocols', needs=['Quokka Protocol', 'Zebra Registry'],
                                repo_root=self.root, transport=self.no_transport)
        self.assertEqual(both['status'], 'local')
        self.assertEqual({r['need_id'] for r in both['evidence_refs']}, {'n1', 'n2'})
        self.assertTrue({'wiki/concepts/quokka-protocol.md', 'wiki/concepts/zebra-registry.md'}
                        <= {p['path'] for p in both['pages']})
        service = ChoiceFixture()
        mixed = self.search.find('Compare', needs=['Quokka Protocol', 'ambiguous lanterns wording'],
                                 repo_root=self.root, transport=service, api_key='fixture')
        self.assertEqual(mixed['source'], 'jev')
        self.assertTrue(mixed['local']['decisions']['n1']['confident'])
        self.assertFalse(mixed['local']['decisions']['n2']['confident'])

    def test_output_budget_never_drops_a_needs_evidence_silently(self):
        self.config(local_first=True)
        filler = 'routine ledger entry without any further detail\n' * 4300  # ~210 KB per page
        for name in ('Alpha', 'Beta', 'Gamma'):
            self.page(f'wiki/ledgers/{name.lower()}-ledger.md', f'# {name} Ledger\n' + filler)
        needs = ['Alpha Ledger', 'Beta Ledger', 'Gamma Ledger']
        with patch.dict(os.environ, {'BSB_LOCAL_PAGES': '1'}):
            three = self.search.find('Compare', needs=needs, repo_root=self.root, dry_run=True,
                                     transport=self.no_transport)
            two = self.search.find('Compare', needs=needs[:2], repo_root=self.root, dry_run=True,
                                   transport=self.no_transport)
        self.assertTrue(all(d['confident'] for d in three['local']['decisions'].values()))
        self.assertNotEqual(three['status'], 'local')
        self.assertEqual((three.get('source'), three['local']['reason']), ('jev', 'local_output_budget'))
        self.assertEqual(two['status'], 'local')
        self.assertEqual(two['unresolved_needs'], [])
        self.assertEqual({p['path'] for p in two['pages']},
                         {'wiki/ledgers/alpha-ledger.md', 'wiki/ledgers/beta-ledger.md'})

    def test_not_confident_falls_through_to_jev_with_local_seeds_first(self):
        self.config(local_first=True)
        service = ChoiceFixture()
        result = self.search.find('ambiguous lanterns wording', repo_root=self.root,
                                  transport=service, api_key='fixture')
        self.assertEqual(result['source'], 'jev')
        self.assertFalse(result['local']['confident'])
        self.assertEqual(result['local']['reason'], 'not_confident')
        self.assertGreater(result['api_calls'], 0)
        top = result['local']['candidates']['n1'][0]['path']
        self.assertEqual(service.calls[0]['state']['operation'], 'branch_evidence')
        self.assertEqual(service.calls[0]['state']['page']['path'], top)
        self.assertGreaterEqual(result['coverage']['seeded_pages'], 1)
        evaluated = [p['state']['page']['path'] for p in service.evidence_calls]
        self.assertEqual(len(evaluated), len(set(evaluated)))

    def test_dry_run_runs_the_local_stage_offline(self):
        self.config(local_first=True)
        with patch.object(self.core, 'load_api_key', side_effect=AssertionError('credential loaded')):
            fell = self.search.find('ambiguous lanterns wording', repo_root=self.root, dry_run=True,
                                    transport=self.no_transport)
            local = self.search.find('What is the Quokka Protocol?', repo_root=self.root, dry_run=True,
                                     transport=self.no_transport)
        self.assertEqual((fell['status'], fell.get('source'), fell['api_calls']), ('dry_run', 'jev', 0))
        self.assertIn('candidates', fell.get('local', {}))
        self.assertEqual(local['status'], 'local')

    def test_environment_overrides_settings_without_writing_config(self):
        self.config(local_first=True)
        before = (self.root / '.bsb-jev/config.json').read_bytes()
        with patch.dict(os.environ, {'BSB_LOCAL_PAGES': '1'}):
            one = self.search.find('What is the Quokka Protocol?', repo_root=self.root,
                                   transport=self.no_transport)
        self.assertEqual(len(one['pages']), 1)
        with patch.dict(os.environ, {'BSB_LOCAL_BACKEND': 'bogus'}):
            bad = self.search.find('What is the Quokka Protocol?', repo_root=self.root, dry_run=True)
        self.assertEqual((bad['source'], bad['local']['reason']), ('jev', 'local_unavailable:ValueError'))
        self.assertEqual((self.root / '.bsb-jev/config.json').read_bytes(), before)

    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = self.core.main(['--root', str(self.root), *args])
        return code, json.loads(output.getvalue())

    def test_cli_flags_override_config_per_call(self):
        self.config(local_first=True, enabled=False)
        with patch.object(self.local, 'LocalSearch', side_effect=AssertionError('local stage ran')):
            code, out = self.run_cli('find', 'What is the Quokka Protocol?', '--no-local')
        self.assertEqual((code, out['status']), (0, 'disabled'))
        self.assertNotIn('source', out)
        self.config(enabled=False)
        code, out = self.run_cli('find', 'What is the Quokka Protocol?', '--local-first')
        self.assertEqual((code, out['status'], out['source'], out['api_calls']), (0, 'local', 'local', 0))
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.core.main(['--root', str(self.root), 'find', 'x', '--local-first', '--no-local'])

    def test_default_off_keeps_the_existing_route_and_packet(self):
        os.environ.pop('BSB_LOCAL_STATE', None)
        with patch.object(self.local, 'LocalSearch', side_effect=AssertionError('local stage ran')):
            result = self.search.find('What is the Quokka Protocol?', repo_root=self.root,
                                      transport=ChoiceFixture(), api_key='fixture')
            reference = self.search._jev_find('What is the Quokka Protocol?', repo_root=self.root,
                                              transport=ChoiceFixture(), api_key='fixture')
        self.assertNotIn('source', result)
        self.assertNotIn('local', result)
        self.assertNotIn('seeded_pages', result['coverage'])
        self.assertEqual({k: v for k, v in result.items() if k != 'session_id'},
                         {k: v for k, v in reference.items() if k != 'session_id'})
        self.assertNotIn('source', self.search.caller_result(result))
        self.assertFalse((self.root / '.bsb-local').exists())


class ConfigHookInstallerTests(LocalTestCase):
    def test_configure_sets_and_validates_local_keys(self):
        self.core.configure_gateway(self.root, local={'local_first': True, 'local_pages': 2,
                                                      'local_backend': 'hybrid'})
        cfg = self.core.get_config(self.root)
        self.assertEqual((cfg['local_first'], cfg['local_pages'], cfg['local_backend']), (True, 2, 'hybrid'))
        for fields in ({'local_first': 'yes'}, {'local_backend': 'gpu'}, {'local_pages': 0},
                       {'local_seeds': True}, {'local_min_margin': 1.5}, {'local_min_coverage': float('nan')}):
            with self.subTest(fields=fields):
                self.config(**fields)
                with self.assertRaises(ValueError):
                    self.core.get_config(self.root)
        self.config()
        with self.assertRaises(ValueError):
            self.core.configure_gateway(self.root, local={'local_unknown': 1})

    def test_hook_allows_local_flags_and_protects_local_code_and_state(self):
        hook = importlib.import_module('scripts.bsb_jev_hook')
        self.config(enforce_reads=True)

        def shell(command):
            return hook.evaluate_tool_call({'tool_name': 'Bash', 'tool_input': {'command': command},
                                            'cwd': str(self.root)}, host='claude', repo_root=self.root)

        def denied(result):
            return result.get('hookSpecificOutput', {}).get('permissionDecision') == 'deny'

        self.assertEqual(shell('python scripts/bsb_jev.py find "q" --local-first'), {})
        self.assertEqual(shell('python scripts/bsb_jev.py find "q" --no-local --dry-run'), {})
        self.assertTrue(denied(shell('python scripts/bsb_jev.py find "q" --local-first --no-local')))
        self.assertTrue(denied(shell('python scripts/bsb_jev.py find "q" --local-first --local-first')))
        write = hook.evaluate_tool_call({'tool_name': 'Write', 'tool_input': {
            'file_path': 'scripts/bsb_local_search.py', 'content': 'tamper'}}, repo_root=self.root)
        self.assertTrue(denied(write))
        poison = hook.evaluate_tool_call({'tool_name': 'Write', 'tool_input': {
            'file_path': str(self.root / '.bsb-local/index.sqlite'), 'content': 'fake'}}, repo_root=self.root)
        self.assertTrue(denied(poison))

    def test_installer_ships_local_search_and_ignores_its_state(self):
        install = importlib.import_module('scripts.install_jev')
        (self.root / 'CLAUDE.md').write_text('Rules.\n', encoding='utf-8')
        manifest = install.install(self.root, enabled=False)
        for name in ('scripts/bsb_local_search.py', 'docs/local-search.md'):
            self.assertTrue((self.root / name).is_file(), name)
            self.assertIn(name, manifest['hashes'])
        self.assertIn('.bsb-local/', (self.root / '.gitignore').read_text(encoding='utf-8').splitlines())
        self.assertIn('--no-local', (self.root / 'CLAUDE.md').read_text(encoding='utf-8'))


class CliContractTests(LocalTestCase):
    def test_search_cli_json_contract_and_state_override(self):
        page = self.page('wiki/concepts/quokka-protocol.md', '---\ntitle: Quokka Protocol\n---\n# Quokka Protocol\nThree steps.\n')
        self.page('wiki/other.md', '# Other\nQuokka sightings.\n')
        env = dict(os.environ, BSB_LOCAL_STATE=str(self.state))
        process = subprocess.run([sys.executable, str(REPO / 'scripts/bsb_local_search.py'), '--root', str(self.root),
                                  'search', 'Quokka Protocol', '--json', '--limit', '1'],
                                 capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(process.returncode, 0, process.stderr)
        out = json.loads(process.stdout)
        for key in ('status', 'query', 'terms', 'backend', 'requested_backend', 'backend_fallback',
                    'results', 'confidence', 'index', 'latency_ms', 'api_calls'):
            self.assertIn(key, out)
        self.assertEqual((out['status'], out['backend'], out['api_calls']), ('ok', 'keyword', 0))
        self.assertEqual(len(out['results']), 1)
        item = out['results'][0]
        self.assertEqual(item['path'], 'wiki/concepts/quokka-protocol.md')
        self.assertEqual(item['file_sha256'], hashlib.sha256(page.read_bytes()).hexdigest())
        for key in ('rank', 'title', 'score', 'heading', 'start_line', 'end_line', 'snippet',
                    'keyword_rank', 'keyword_score', 'name_match', 'term_coverage'):
            self.assertIn(key, item)
        self.assertEqual(set(out['confidence']), {'confident', 'rule', 'reason', 'signals'})
        self.assertTrue((self.state / 'index.sqlite').is_file())
        self.assertFalse((self.root / '.bsb-local').exists())


if __name__ == '__main__':
    unittest.main()
