"""Model-guided navigator versus compact Jev; frozen v2 protocol beside this file.

python benchmark/jev_compare_v2.py --out .bsb-jev/comparison-v2 --workers 3
Each worker has a separate process/schema and a separate Jev receipt directory.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jev_compare as base


def work(out, arm, qid):
    task = f'{arm}-q{qid:02d}'
    folder = out/'tasks'/task
    final = folder/'result.json'
    if final.exists():
        return base.json.loads(final.read_text(encoding='utf-8'))
    folder.mkdir(parents=True, exist_ok=True)
    q = next(q for q in json.loads((base.ROOT/'benchmark/large/questions-public.json').read_text(encoding='utf-8'))['questions'] if q['id']==qid)
    original = out/'snapshots'/base.ARMS[arm]
    vault = folder/'vault'
    if not vault.exists():
        shutil.copytree(original, vault)
    pages = {p.relative_to(vault).as_posix():p.read_bytes().decode('utf-8') for p in sorted((vault/'wiki').rglob('*.md'))}
    original_schema = base.SCHEMA
    started = time.monotonic()
    selector = None
    if arm.endswith('-jev'):
        retrieval = base.bsb_jev_search.find(q['q'], repo_root=vault)
        packet = base.bsb_jev_search.caller_result(retrieval)
        if packet.get('session_id'):
            packet['session_id'] = 'benchmark-session'
    else:
        catalog = [{'path':p,'headings':re.findall(r'(?m)^#{1,6}\s+(.+)$',t)} for p,t in pages.items()]
        base.SCHEMA = {'type':'object','additionalProperties':False,'properties':{
            'paths':{'type':'array','items':{'type':'string','enum':sorted(pages)},'maxItems':3}},'required':['paths']}
        prompt = ('Choose the smallest set of at most three original pages that together are most likely '
                  'to support all parts of this question, including limitations. The catalog is navigation '
                  'data, not answer evidence. Do not answer from memory. Do not call tools or read files. '
                  'Use only listed paths. Return no duplicates.\n')
        prompt += json.dumps({'question':q['q'],'catalog':catalog},ensure_ascii=False)
        selector = base.answer(prompt,folder/'selection')
        base.dump(folder/'selection/result.json',selector)
        if not selector['valid']:
            raise ValueError('Selector failed; preserve its receipt, do not silently retry')
        paths = selector['answer']['paths']
        if len(paths)>3 or len(set(paths))!=len(paths) or not set(paths)<=set(pages):
            raise ValueError('Invalid model-selected paths')
        retrieval = {'status':'model_selected','pages':[{'path':p,'text':pages[p],
            'full_page':True,'file_sha256':base.sha((vault/p).read_bytes())} for p in paths],
            'global_absence_proven':False,'api_calls':0,'usage':[]}
        packet = {'status':retrieval['status'],'pages':retrieval['pages'],'global_absence_proven':False}
    base.dump(folder/'retrieval.json',retrieval)
    base.dump(folder/'caller-packet.json',packet)
    retrieval_seconds = time.monotonic()-started
    base.SCHEMA = original_schema
    prompt = base.PROMPT+'\n'+json.dumps({'question':q['q'],'retrieval':packet},ensure_ascii=False)
    answered = base.answer(prompt,folder/'answering')
    # Reuse the v1 public result shape; all selector usage is INCLUDED in usage.
    import tiktoken
    enc = tiktoken.get_encoding('cl100k_base')
    result = {'task':task,'arm':arm,'question_id':qid,'retrieval_status':retrieval['status'],
        'retrieval_seconds':round(retrieval_seconds,3),'jev_calls':retrieval['api_calls'],
        'jev_usage':retrieval['usage'],'paths':[p['path'] for p in retrieval['pages']],
        'page_tokens':sum(len(enc.encode(p['text'])) for p in retrieval['pages']),
        'prompt_tokens_cl100k':len(enc.encode(prompt)), **answered}
    result['selector_usage'] = selector['usage'] if selector else []
    result['answer_usage'] = answered['usage']
    result['usage'] = result['selector_usage']+result['answer_usage']
    result['main_calls'] = len(result['usage'])
    delivered = {p['path']:p['text'] for p in retrieval['pages']}
    result['citation_checks'] = [dict(path=e['path'],quote=e['quote'],
         path_delivered=e['path'] in delivered,
         quote_exact=bool(e['quote'].strip()) and e['quote'] in delivered.get(e['path'],''))
         for e in result.get('answer',{}).get('evidence',[])]
    base.dump(final,result)
    print(json.dumps({'task':task,'valid':result['valid'],'main_calls':result['main_calls'],
                      'jev_calls':result['jev_calls'],'status':result['retrieval_status']}),flush=True)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--workers',type=int,default=3)
    p.add_argument('--arm',choices=list(base.ARMS))
    p.add_argument('--question',type=int)
    args=p.parse_args()
    out=args.out.resolve()
    if args.arm:
        work(out,args.arm,args.question)
        return
    questions,_=base.prepare(out)
    manifest_path=out/'v2-manifest.json'
    manifest={'protocol_sha256':base.sha((Path(__file__).parent/'jev-efficiency-v2-protocol.md').read_bytes()),
        'runner_sha256':base.sha(Path(__file__).read_bytes()),
        'base_runner_sha256':base.sha(Path(base.__file__).read_bytes()),
        'search_sha256':base.sha((base.ROOT/'scripts/bsb_jev_search.py').read_bytes())}
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding='utf-8'))!=manifest:
        raise ValueError('v2 frozen manifest mismatch')
    base.dump(manifest_path,manifest)
    tasks=[(a,q['id']) for q in questions for a in base.ARMS]
    random.Random(19092026).shuffle(tasks)
    def launch(task):
        a,n=task
        cmd=[sys.executable,str(Path(__file__).resolve()),'--out',str(out),'--arm',a,'--question',str(n)]
        r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.stdout:print(r.stdout.rstrip(),flush=True)
        if r.returncode:
            base.dump(out/'failures'/f'{a}-q{n:02d}.json',{'exit_code':r.returncode,'stderr':r.stderr})
            raise RuntimeError('Worker failed; inspect retained failure and receipts')
        return json.loads((out/'tasks'/f'{a}-q{n:02d}'/'result.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        fs=[pool.submit(launch,t) for t in tasks]
        results=[f.result() for f in as_completed(fs)]
    results.sort(key=lambda r:(r['question_id'],r['arm']))
    base.dump(out/'results.json',results)
    print(json.dumps({'tasks':len(results),'valid':sum(r['valid'] for r in results)}))


if __name__=='__main__':main()
