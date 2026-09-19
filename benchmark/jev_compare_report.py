"""Audit accounting, prepare blinded grading, and publish a public summary.

python benchmark/jev_compare_report.py .bsb-jev/comparison --prepare-grading
python benchmark/jev_compare_report.py .bsb-jev/comparison --grades PATH --publish DIR
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def usage_totals(main, jev):
    if not main or any(not isinstance(u, dict) or 'input_tokens' not in u or
                       'output_tokens' not in u for u in [*main, *jev]):
        raise ValueError('Missing measured usage; cannot claim zero cost')
    i = sum(u['input_tokens'] for u in main)
    cached = sum(u.get('cached_input_tokens', 0) for u in main)
    writes = sum(u.get('cache_write_input_tokens', 0) for u in main)
    o = sum(u['output_tokens'] for u in main)
    reasoning = sum(u.get('reasoning_output_tokens', 0) for u in main)
    if cached+writes > i or reasoning > o or min(i, cached, writes, o, reasoning) < 0:
        raise ValueError('Inconsistent usage subsets')
    # Historical adapter may expose separately billed cache usage. Current API
    # returns input_tokens/output_tokens only; retain separate counters visibly.
    ji = sum(u['input_tokens'] for u in jev)
    jc = sum(u.get('cached_input_tokens', 0) for u in jev)
    jo = sum(u['output_tokens'] for u in jev)
    jev_usd = (ji+jc)*.042/1e6
    return {'main_input': i, 'main_cached_input': cached, 'main_cache_write_input': writes,
            'main_output': o, 'main_reasoning_output': reasoning, 'main_tokens': i+o,
            'jev_input': ji, 'jev_cached_input_separate': jc, 'jev_output': jo,
            'all_model_tokens': i+o+ji+jc+jo, 'jev_usd': jev_usd,
            'usd_uncached': (i*.2+o*1.2)/1e6+jev_usd,
            'usd_cache_aware': ((i-cached-writes)*.2+cached*.02+writes*.25+o*1.2)/1e6+jev_usd}


def arm_summary(rows):
    totals = usage_totals([u for r in rows for u in r['usage']],
                          [u for r in rows for u in r['jev_usage']])
    grades = [sum(r['grade'][k] for k in ('correctness', 'citation', 'faithfulness')) for r in rows]
    solved = sum(g == 6 and r['valid'] for g,r in zip(grades, rows))
    return {**totals, 'n': len(rows), 'valid': sum(r['valid'] for r in rows),
            'quality_mean': statistics.mean(grades), 'solved': solved,
            'usd_per_solved': totals['usd_uncached']/solved if solved else None,
            'page_tokens': sum(r['page_tokens'] for r in rows),
            'page_tokens_mean': statistics.mean(r['page_tokens'] for r in rows),
            'jev_calls': sum(r['jev_calls'] for r in rows),
            'seconds_sum': sum(r['seconds']+r['retrieval_seconds'] for r in rows),
            'end_to_end_seconds_median': statistics.median(r['seconds']+r['retrieval_seconds'] for r in rows)}


def prepare_grading(out, rows):
    root = Path(__file__).resolve().parents[1]
    gold = {q['id']:q for q in load(root/'benchmark/large/questions.json')['questions']}
    shuffled = list(rows)
    random.Random(4919).shuffle(shuffled)
    mapping, blind = {}, []
    for i,r in enumerate(shuffled):
        bid = f'answer-{i+1:03d}'
        mapping[bid] = r['task']
        q = gold[r['question_id']]
        retrieval = load(out/'tasks'/r['task']/'retrieval.json')
        sources = {p['path']:p['text'] for p in retrieval['pages']}
        checks = []
        for c in r.get('citation_checks', []):
            text = sources.get(c['path'], '')
            offset = text.find(c['quote']) if c['quote'] else -1
            checks.append({**c, 'surrounding_text': text[max(0,offset-250):offset+len(c['quote'])+250]
                           if offset >= 0 else '',
                           'full_source_if_quote_not_exact': text if offset < 0 else ''})
        entry = {'id': bid, 'question_id': q['id'], 'question': q['q'],
                      'gold': q['gold'], 'gold_source': q['source'],
                      'answer': r.get('answer'), 'valid': r['valid'], 'citation_checks': checks}
        # Hide source layout names as well as arm names; exact-quote checks were
        # performed against the unmodified original source before anonymization.
        encoded = json.dumps(entry, ensure_ascii=False)
        for n, path in enumerate(sorted(sources, key=len, reverse=True), 1):
            encoded = encoded.replace(path, f'page-{n}')
        blind.append(json.loads(encoded))
    dump(out/'blind-map.json', mapping)
    dump(out/'blind-answers.json', blind)


def aggregate(out, grades_path, publish):
    rows = load(out/'results.json')
    mapping = load(out/'blind-map.json')
    entries = load(grades_path)
    grades = entries['grades'] if isinstance(entries, dict) else entries
    if {g['id'] for g in grades} != set(mapping) or len(grades) != len(mapping):
        raise ValueError('Incomplete or duplicate blinded grading IDs')
    grade_by_task = {}
    for grade in grades:
        if any(type(grade.get(k)) is not int or grade[k] not in (0,1,2)
               for k in ('correctness','citation','faithfulness')):
            raise ValueError('Grade outside frozen rubric')
        grade_by_task[mapping[grade['id']]] = grade
    for r in rows:
        r['grade'] = grade_by_task[r['task']]
        r['accounting'] = usage_totals(r['usage'], r['jev_usage'])
        r['question_type'] = {1:'recall', 2:'recall', 11:'freshness', 12:'freshness',
                              13:'freshness', 14:'unsupported'}.get(r['question_id'], 'detail')
    arms = sorted({r['arm'] for r in rows})
    if len(rows) != 70 or set(arms) != {'vanilla','full','lean','full-jev','lean-jev'}:
        raise ValueError('Incomplete experiment')
    for arm in arms:
        if sorted(r['question_id'] for r in rows if r['arm']==arm) != list(range(1,15)):
            raise ValueError('Question matrix mismatch')
    summary = {a: arm_summary([r for r in rows if r['arm']==a]) for a in arms}
    for a in arms:
        subset = [r for r in rows if r['arm']==a]
        summary[a]['dimension_means'] = {k:statistics.mean(r['grade'][k] for r in subset)
            for k in ('correctness','citation','faithfulness')}
        summary[a]['category_quality'] = {k:statistics.mean(sum(r['grade'][d] for d in
            ('correctness','citation','faithfulness')) for r in subset if r['question_type']==k)
            for k in ('recall','detail','freshness','unsupported')}
        summary[a]['usd_uncached_median'] = statistics.median(r['accounting']['usd_uncached'] for r in subset)
        for metric in ('retrieval_seconds','seconds'):
            values = sorted(r[metric] for r in subset)
            label = 'answer_seconds' if metric == 'seconds' else metric
            summary[a][label+'_median'] = statistics.median(values)
            summary[a][label+'_p95_nearest_rank'] = values[-1]  # ceil(.95 * 14) == 14
    pairs = {}
    for arm, base in [('full','vanilla'), ('lean','vanilla'), ('full-jev','full'),
                      ('lean-jev','lean'), ('full-jev','vanilla'), ('lean-jev','vanilla')]:
        a,b = summary[arm],summary[base]
        key = arm+'_vs_'+base
        pairs[key] = {m: 100*(a[m]/b[m]-1) if b[m] and a[m] is not None else None for m in
                     ('main_tokens','main_input','page_tokens','all_model_tokens',
                      'usd_uncached','usd_cache_aware','usd_per_solved','usd_uncached_median')}
        pairs[key]['quality_delta'] = a['quality_mean']-b['quality_mean']
        byq = {r['question_id']:r for r in rows if r['arm']==base}
        pairs[key]['quality_regressions'] = [r['question_id'] for r in rows if r['arm']==arm and
            sum(r['grade'][k] for k in ('correctness','citation','faithfulness')) <
            sum(byq[r['question_id']]['grade'][k] for k in ('correctness','citation','faithfulness'))]
        dimensions = ('correctness', 'citation', 'faithfulness')
        pairs[key]['per_question_deltas'] = [{
            'question_id': r['question_id'],
            **{k: r['grade'][k]-byq[r['question_id']]['grade'][k] for k in dimensions},
            'usd_uncached': r['accounting']['usd_uncached']-byq[r['question_id']]['accounting']['usd_uncached'],
            'usd_uncached_percent': 100*(r['accounting']['usd_uncached']/byq[r['question_id']]['accounting']['usd_uncached']-1)
        } for r in rows if r['arm']==arm]
        pairs[key]['dimension_regressions'] = {k: [d['question_id'] for d in
            pairs[key]['per_question_deltas'] if d[k] < 0] for k in dimensions}
        pairs[key]['paired_median_cost_change_percent'] = statistics.median(
            d['usd_uncached_percent'] for d in pairs[key]['per_question_deltas'])
    result = {'arms': summary, 'paired_changes_percent': pairs,
              'prices_usd_per_million': {'luna_input': .2, 'luna_cached_input': .02,
                  'luna_cache_write_input': .25, 'luna_output': 1.2, 'jev_input': .042, 'jev_output': 0},
              'price_sources': ['https://developers.openai.com/api/docs/models/gpt-5.6-luna',
                                'https://docs.typesafe.ai/models']}
    dump(publish/'summary.json', result)
    dump(publish/'results.json', rows)
    manifest = load(out/'manifest.json')
    manifest['publication_tool_hashes'] = {name: hashlib.sha256(
        (Path(__file__).parent/name).read_bytes()).hexdigest()
        for name in ('jev_compare.py', 'jev_compare_report.py')}
    dump(publish/'manifest.json', manifest)
    dump(publish/'grades.json', grades)
    # Public artifacts only contain the shipped public fixture and answer results.
    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('out', type=Path)
    p.add_argument('--prepare-grading', action='store_true')
    p.add_argument('--grades', type=Path)
    p.add_argument('--publish', type=Path)
    args = p.parse_args()
    if args.prepare_grading:
        prepare_grading(args.out, load(args.out/'results.json'))
    if args.grades:
        aggregate(args.out, args.grades, args.publish)


if __name__ == '__main__':
    main()
