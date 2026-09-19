"""Small live Jev contract trial on public synthetic data, never private vaults.

Run: python benchmark/jev_branching_smoke.py --out .bsb-jev/branching-smoke.json
Makes at most 60 TypeSafe calls. This is not an end-to-end cost benchmark.
"""
import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import bsb_jev_search as search


PAGES = {
    'wiki/moc/storage.md': '# Persistent storage\n[[wiki/journal]]\n[[wiki/checkpoint]]\n',
    'wiki/moc/access.md': '# Account access\n[[wiki/session]]\n[[wiki/caution]]\n',
    'wiki/journal.md': '# Crash recovery\nThe database records acknowledged writes in a durable write-ahead journal. After a crash it replays that journal after loading the most recent checkpoint.\n',
    'wiki/checkpoint.md': '# Checkpoint configuration\nSet checkpoint_interval_seconds=60 to save a state snapshot every minute. Journal replay is still needed to recover newer writes.\n',
    'wiki/session.md': '# Session renewal\nAn authenticated session is renewed by exchanging a refresh token for a fresh access token.\n',
    'wiki/caution.md': '# Refresh token restrictions\nA revoked refresh token cannot renew a session. The user must authenticate again.\n',
    'wiki/theme.md': '# Color theme\nThe settings screen offers light and dark color themes.\n',
    'wiki/orphan.md': '# Export shortcut\nPress Ctrl+Shift+E to export a Markdown archive.\n',
}
INDEX = '# Index\n## Storage\n[[wiki/moc/storage]] - Database persistence and recovery.\n## Account access\n[[wiki/moc/access]] - Login and renewal.\n## Appearance\n[[wiki/theme]] - Colors.\n'
CASES = [
    {'id': 'german-unindexed', 'query': 'Mit welcher Tastenkombination sichere ich alle Notizen als Markdown-Archiv?',
     'needs': None, 'required_paths': ['wiki/orphan.md']},
    {'id': 'two-page-recovery', 'query': 'How do writes survive a crash and how do I configure snapshots?',
     'needs': ['How are acknowledged writes recovered after a crash?', 'What exact setting saves a snapshot every minute?'],
     'required_paths': ['wiki/journal.md', 'wiki/checkpoint.md']},
    {'id': 'missing-answer', 'query': 'Which AES encryption key length protects the backups?',
     'needs': None, 'required_paths': [], 'must_be_unresolved': True},
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix='bsb-branch-live-') as folder:
        root = Path(folder)
        for name, text in {**PAGES, 'index.md': INDEX}.items():
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        (root/'.bsb-jev').mkdir()
        (root/'.bsb-jev/config.json').write_text(json.dumps({'enabled': True, 'timeout': 15}), encoding='utf-8')
        for case in CASES:
            started = time.monotonic()
            result = search.find(case['query'], case['needs'], root, max_calls=20, max_pages=8)
            paths = [p['path'] for p in result['pages']]
            source_ok = all(p['text'] == (root/p['path']).read_bytes().decode('utf-8')
                            for p in result['pages'])
            # Freeze observable criteria before live execution, no model grader.
            passed = (set(case['required_paths']).issubset(paths) and source_ok
                      and result['status'] not in {'unavailable', 'stale'}
                      and (not case.get('must_be_unresolved') or bool(result['unresolved_needs'])))
            row = {'id': case['id'], 'passed': passed, 'status': result['status'], 'paths': paths,
                   'api_calls': result['api_calls'], 'usage': result['usage'],
                   'coverage': result['coverage'], 'evidence_refs': result['evidence_refs'],
                   'conflicts': result['conflicts'], 'unresolved_needs': result['unresolved_needs'],
                   'seconds': round(time.monotonic()-started, 3)}
            results.append(row)
            print(json.dumps(row, ensure_ascii=False), flush=True)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'cases': results, 'claim': 'Synthetic retrieval smoke only; no cost or production-quality claim'}, indent=2, ensure_ascii=False), encoding='utf-8')
    return 0 if all(row['passed'] for row in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
