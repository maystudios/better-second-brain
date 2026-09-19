"""Reconcile all selector, answer, and Jev calls in the v2 experiment."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import jev_compare as base
from jev_compare_report import load, dump, usage_totals


def event_usage(folder):
    events=[json.loads(line) for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()
            if line.startswith('{')]
    assert not any(e.get('item',{}).get('type') in {'command_execution','mcp_tool_call','web_search','file_change'} for e in events)
    return [e['usage'] for e in events if e.get('type')=='turn.completed']


def audit(out):
    rows=load(out/'results.json')
    assert len(rows)==70 and {(r['arm'],r['question_id']) for r in rows} == {(a,n) for a in base.ARMS for n in range(1,15)}
    manifest=load(out/'manifest.json')
    v2=load(out/'v2-manifest.json')
    assert v2['search_sha256']==base.sha((base.ROOT/'scripts/bsb_jev_search.py').read_bytes())
    assert v2['runner_sha256']==base.sha((Path(__file__).parent/'jev_compare_v2.py').read_bytes())
    assert v2['protocol_sha256']==base.sha((Path(__file__).parent/'jev-efficiency-v2-protocol.md').read_bytes())
    checks=[]; sessions=set(); total_calls=0
    for r in rows:
        folder=out/'tasks'/r['task']; vault=folder/'vault'
        assert load(folder/'result.json')==r and r['valid'] and r['tool_events']==0
        expected=manifest['snapshots'][base.ARMS[r['arm']]]
        actual={p.relative_to(vault).as_posix():base.sha(p.read_bytes()) for p in (vault/'wiki').rglob('*.md')}
        assert actual==expected['hashes']
        source=base.ROOT/'benchmark/large'/base.ARMS[r['arm']]
        assert actual=={p.relative_to(source).as_posix():base.sha(p.read_bytes()) for p in (source/'wiki').rglob('*.md')}
        assert expected['index_sha256']==base.sha((vault/'index.md').read_bytes())
        answer_usage=event_usage(folder/'answering')
        assert answer_usage==r['answer_usage']
        assert load(folder/'answering/answer.json')==r['answer']
        assert set(r['answer'])=={'answer','uncertainty','evidence'}
        retrieval=load(folder/'retrieval.json')
        packet=load(folder/'caller-packet.json')
        delivered={p['path']:p['text'] for p in retrieval['pages']}
        for p in retrieval['pages']:
            assert p['text']==(vault/p['path']).read_bytes().decode('utf-8')
            assert p['file_sha256']==base.sha((vault/p['path']).read_bytes())
        prompt=(folder/'answering/prompt.txt').read_text(encoding='utf-8')
        payload=json.loads(prompt[len(base.PROMPT)+1:])
        assert payload['retrieval']==packet
        if r['arm'].endswith('-jev'):
            assert r['selector_usage']==[]
            compact=base.bsb_jev_search.caller_result(retrieval)
            if compact.get('session_id'):compact['session_id']='benchmark-session'
            assert compact==packet
            sid=retrieval['session_id']; assert sid and sid not in sessions
            sessions.add(sid)
            receipt=load(vault/'.bsb-jev'/f'{sid}.json')
            assert receipt['branching']['usage']==r['jev_usage']
        else:
            assert event_usage(folder/'selection')==r['selector_usage']
            selected=load(folder/'selection/answer.json')['paths']
            assert selected==r['paths'] and len(set(selected))==len(selected) and len(selected)<=3
        assert r['usage']==r['selector_usage']+answer_usage
        assert retrieval['usage']==r['jev_usage'] and len(r['jev_usage'])==r['jev_calls']
        total_calls+=len(r['usage'])
        usage_totals(r['usage'],r['jev_usage'])
        for c in r['citation_checks']:
            assert c['path_delivered']==(c['path'] in delivered)
            assert c['quote_exact']==(bool(c['quote'].strip()) and c['quote'] in delivered.get(c['path'],''))
            if not c['quote_exact']:checks.append({'task':r['task'],'path':c['path'],'quote_exact':False})
    assert total_calls==112 and len(sessions)==28
    result={'passed':True,'terminal_rows':70,'main_calls':total_calls,'selector_calls':42,
            'answer_calls':70,'jev_calls':sum(r['jev_calls'] for r in rows),'unique_jev_receipts':28,
            'all_usage_reconciled':True,'source_hashes_verified':True,'no_answer_tools':True,
            'gold_sha256':base.sha((base.ROOT/'benchmark/large/questions.json').read_bytes()),
            'quote_check_failures':checks}
    dump(out/'audit.json',result)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out',type=Path)
    print(json.dumps(audit(parser.parse_args().out),indent=2))
