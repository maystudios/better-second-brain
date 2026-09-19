"""Reconcile the completed trial against source snapshots and raw CLI receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev_compare as runner


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def audit(out):
    manifest = load(out/'manifest.json')
    rows = load(out/'results.json')
    expected = {(a,n) for a in runner.ARMS for n in range(1,15)}
    assert len(rows)==70 and {(r['arm'],r['question_id']) for r in rows} == expected
    assert manifest['protocol_sha256'] == runner.sha((runner.ROOT/'benchmark/jev-comparison-protocol.md').read_bytes())
    assert manifest['search_sha256'] == runner.sha((runner.ROOT/'scripts/bsb_jev_search.py').read_bytes())
    qs = runner.ROOT/'benchmark/large/questions-public.json'
    assert manifest['questions_sha256'] == runner.sha(qs.read_bytes())
    questions = {q['id']:q['q'] for q in load(qs)['questions']}
    for arm, m in manifest['snapshots'].items():
        root = out/'snapshots'/arm
        actual = {p.relative_to(root).as_posix():runner.sha(p.read_bytes()) for p in (root/'wiki').rglob('*.md')}
        assert actual == m['hashes'], 'Snapshot changed or contains extra Markdown'
        original = runner.ROOT/'benchmark/large'/arm
        assert actual == {p.relative_to(original).as_posix():runner.sha(p.read_bytes())
                          for p in (original/'wiki').rglob('*.md')}
        assert runner.sha((root/'index.md').read_bytes()) == m['index_sha256']
    sessions = set()
    bad_quotes = []
    for r in rows:
        task = out/'tasks'/r['task']
        assert load(task/'result.json') == r
        events = [json.loads(line) for line in (task/'events.jsonl').read_text(encoding='utf-8').splitlines()
                  if line.startswith('{')]
        assert [e['usage'] for e in events if e.get('type')=='turn.completed'] == r['usage']
        assert r['valid'] and r['exit_code']==0 and r['tool_events']==0
        assert load(task/'answer.json') == r['answer']
        answer = r['answer']
        assert set(answer) == {'answer','uncertainty','evidence'}
        assert isinstance(answer['answer'],str) and isinstance(answer['uncertainty'],str)
        assert isinstance(answer['evidence'],list)
        retrieval = load(task/'retrieval.json')
        assert retrieval['usage'] == r['jev_usage'] and retrieval['api_calls'] == r['jev_calls']
        assert len(retrieval['usage']) == r['jev_calls'], 'Unreconciled Jev calls'
        snapshot = out/'snapshots'/runner.ARMS[r['arm']]
        for page in retrieval['pages']:
            data = (snapshot/page['path']).read_bytes()
            assert runner.sha(data) == page['file_sha256']
            assert data.decode('utf-8') == page['text']
        packet = json.loads((task/'prompt.txt').read_text(encoding='utf-8')[len(runner.PROMPT)+1:])
        assert set(packet) == {'question','retrieval'} and packet['question']==questions[r['question_id']]
        expected_packet = dict(retrieval)
        if 'session_id' in expected_packet:
            expected_packet['session_id'] = 'benchmark-session' if expected_packet['session_id'] else None
        assert packet['retrieval'] == expected_packet
        if r['arm'].endswith('-jev'):
            sid = retrieval['session_id']
            assert sid and sid not in sessions
            sessions.add(sid)
            receipt = load(snapshot/'.bsb-jev'/f'{sid}.json')
            assert receipt['branching']['usage'] == r['jev_usage']
        for c in r['citation_checks']:
            if not c['path_delivered'] or not c['quote_exact']:
                bad_quotes.append({'task':r['task'], 'path':c['path'],
                                   'path_delivered':c['path_delivered'], 'quote_exact':c['quote_exact']})
    import tiktoken
    result = {'passed': True, 'terminal_rows':len(rows), 'unique_jev_receipts':len(sessions),
              'answer_calls':sum(len(r['usage']) for r in rows),
              'jev_calls':sum(r['jev_calls'] for r in rows),
              'source_hashes_verified':True, 'no_extra_snapshot_pages':True,
              'all_usage_reconciled':True, 'no_answer_tools':True,
              'gold_sha256':runner.sha((runner.ROOT/'benchmark/large/questions.json').read_bytes()),
              'runner_sha256':runner.sha(Path(runner.__file__).read_bytes()),
              'tokenizer_version':tiktoken.__version__, 'quote_check_failures':bad_quotes}
    runner.dump(out/'audit.json', result)
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path)
    print(json.dumps(audit(parser.parse_args().out),indent=2))
