"""Independent fresh-context grading: receives no arm map, costs or raw results."""
import argparse
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev_compare as runner

GRADE_SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'grades': {'type': 'array', 'items': {'type': 'object', 'additionalProperties': False,
        'properties': {'id': {'type': 'string'},
                       'correctness': {'type': 'integer', 'enum': [0,1,2]},
                       'citation': {'type': 'integer', 'enum': [0,1,2]},
                       'faithfulness': {'type': 'integer', 'enum': [0,1,2]},
                       'reason': {'type': 'string'}},
        'required': ['id','correctness','citation','faithfulness','reason']}}},
    'required': ['grades']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('blind_answers', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--batches', action='store_true', help='Grade each question in a separate context (3 workers)')
    args = p.parse_args()
    prompt = '''You are an independent blinded grader of historical documentation QA.
No tools, web, files or external knowledge. You receive shuffled answers without
system/arm identities or costs. Grade EACH answer independently against its gold
and the verified cited quotations and surrounding source text. Page identifiers
are anonymized; quote_exact/path_delivered were checked before anonymization.
Do not reward length or cautious wording by itself. Equivalent paraphrases and
semantically complete alternatives receive full correctness; do not require
every incidental word in the gold unless the question asks for it.
Frozen rubric, integer 0-2 per dimension:
Correctness: 2 covers all requested gold facts, 1 partly correct or abstains on a
required fact, 0 wrong core answer. Citation: 2 relevant checkable support for all
material claims, 1 incomplete support, 0 absent/fabricated/non-supporting.
Faithfulness: 2 no unsupported assertion or false completeness, 1 minor
overstatement, 0 material unsupported claim. Abstention can be faithful but not
automatically correct/complete. A quote_exact false may be harmless whitespace
variation: assess the available evidence rather than automatically calling it
fabricated. Distinguish source ambiguity from confident unsupported claims.
Do not grade answer quality from retrieval status. Grade the facts and support.
Return one grade for every input ID exactly once, with a concise reason naming
the fact or support that loses points. Do not infer or label the tested systems.
'''
    runner.SCHEMA = GRADE_SCHEMA
    if args.batches:
        entries = json.loads(args.blind_answers.read_text(encoding='utf-8'))
        def grade_question(qid):
            group = [e for e in entries if e['question_id']==qid]
            folder = args.out.resolve()/f'q{qid:02d}'
            result = runner.answer(prompt+json.dumps(group,ensure_ascii=False),folder)
            runner.dump(folder/'grading-result.json',result)
            print(json.dumps({'question_id':qid,'valid':result['valid']}),flush=True)
            if not result['valid']:
                raise ValueError('Invalid grading batch')
            if {g['id'] for g in result['answer']['grades']} != {e['id'] for e in group}:
                raise ValueError('Grading ID mismatch')
            return result
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(grade_question,qid) for qid in sorted({e['question_id'] for e in entries})]
            batches = [f.result() for f in as_completed(futures)]
        runner.dump(args.out/'answer.json',{'grades':[g for b in batches for g in b['answer']['grades']]})
        runner.dump(args.out/'grading-result.json',{'valid':True,'usage':[u for b in batches for u in b['usage']],
                    'seconds_sum':sum(b['seconds'] for b in batches),'batches':len(batches)})
        return
    prompt += args.blind_answers.read_text(encoding='utf-8')
    result = runner.answer(prompt, args.out.resolve())
    runner.dump(args.out/'grading-result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k != 'answer'}, indent=2))
    if not result['valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
