"""Catalog-first, bounded depth-first Jev retrieval.

Code owns traversal; Jev only chooses known IDs and judges supplied evidence.
The returned full pages are evidence for the caller, never a generated answer.
"""
from __future__ import annotations

import hashlib
import re
import time
from pathlib import Path

try:
    from . import bsb_jev as core, bsb_jev_navigation as nav
except ImportError:
    import bsb_jev as core
    import bsb_jev_navigation as nav

MAX_OPTIONS = 24
CHUNK_BYTES = 8000
MAX_RETURN_BYTES = 512 * 1024
MAX_SECONDS = 120
LINK = re.compile(r'\[\[([^\]]+)\]\]')


def _clip(text, size):
    return text.encode('utf-8')[:size].decode('utf-8', errors='ignore')


def _choice(instructions, criteria):
    return {'type': 'choice', 'instructions': core.UNTRUSTED_DATA_NOTICE + ' ' + instructions,
            'criteria': criteria}


def _validate(query, needs, max_calls, max_pages):
    if not isinstance(query, str) or not query.strip() or len(query) > 4096:
        raise ValueError('Question must contain 1..4096 characters')
    needs = [query] if needs is None else needs
    if not isinstance(needs, (list, tuple)) or not 1 <= len(needs) <= 6:
        raise ValueError('Supply 1..6 evidence needs')
    if any(not isinstance(n, str) or not n.strip() or len(n) > 4096 for n in needs):
        raise ValueError('Each evidence need must contain 1..4096 characters')
    if core.SECRET_CONTENT_REGEX.search(query + '\n'.join(needs)):
        raise ValueError('Secret-looking query refused')
    for value, maximum in ((max_calls, 96), (max_pages, 48)):
        if type(value) is not int or not 1 <= value <= maximum:
            raise ValueError(f'Budget must be an integer in 1..{maximum}')
    return {f'n{i+1}': n for i, n in enumerate(needs)}


def _build_catalog(root):
    """Resolve index/MOC relationships once; keep every scanned page reachable."""
    scanned, coverage = nav.catalog(root)
    pages, names, nodes = {}, {}, {}
    for i, (descriptor, text, meta) in enumerate(scanned):
        name = descriptor['path']
        headings = re.findall(r'(?m)^#{1,6}\s+(.+)$', text)
        title = meta.get('title') or (headings[0] if headings else descriptor['title'])
        descriptor = dict(descriptor, title=title)
        node_id = f'p{i+1}'
        pages[name] = {'descriptor': descriptor, 'text': text, 'id': node_id}
        nodes[node_id] = {'id': node_id, 'kind': 'page', 'path': name, 'title': title,
                          'description': ' | '.join([*meta.get('aliases', []), *headings])}
        for key in (name, Path(name).with_suffix('').as_posix(), Path(name).stem,
                    title, *meta.get('aliases', [])):
            names.setdefault(key.casefold(), set()).add(node_id)

    def resolve(text):
        ids = []
        for link in LINK.findall(text):
            key = link.split('|')[0].split('#')[0].strip().casefold()
            ids.extend(sorted(names.get(key, ())))
        return list(dict.fromkeys(ids))

    for node in nodes.values():
        node['children'] = resolve(pages[node['path']]['text'])

    index_path = core._safe_path(root, 'index.md')
    index_text, index_hash = '', None
    coverage['index_status'] = 'missing'
    try:
        if index_path.exists():
            if index_path.stat().st_size > nav.MAX_PAGE_BYTES:
                raise ValueError('Oversized index')
            data = index_path.read_bytes()
            if len(data) > nav.MAX_PAGE_BYTES:
                raise ValueError('Index grew past limit')
            index_hash = hashlib.sha256(data).hexdigest()
            index_text = data.decode('utf-8-sig')
            if core.SECRET_CONTENT_REGEX.search(index_text) or '\x00' in index_text:
                raise ValueError('Unsafe index text')
            coverage['index_status'] = 'read'
    except (OSError, UnicodeError, ValueError):
        index_text = ''
        coverage['scan_complete'] = False
        coverage['index_status'] = 'unreadable'

    roots, indexed = [], set()
    heading, lines = 'Index', []

    def add_section():
        text = '\n'.join(lines)
        children = resolve(text)
        if not children:
            return
        nid = f'g{len(nodes)+1}'
        nodes[nid] = {'id': nid, 'kind': 'index', 'title': heading,
                      'description': text, 'children': children}
        roots.append(nid)
        indexed.update(children)
        for line in lines:
            for child in resolve(line):
                # Use real index text, not a generated synopsis.
                nodes[child]['description'] += ' | ' + line

    for line in index_text.splitlines():
        if re.match(r'^#{1,6}\s', line):
            add_section()
            heading, lines = line.lstrip('# ').strip(), []
        else:
            lines.append(line)
    add_section()
    rest = [p['id'] for p in pages.values() if p['id'] not in indexed]
    if rest:
        nid = f'g{len(nodes)+1}'
        nodes[nid] = {'id': nid, 'kind': 'index', 'title': 'Additional catalog pages',
                      'description': 'Pages absent from the index; inspect for missing evidence.',
                      'children': rest}
        roots.append(nid)
    nodes['root'] = {'id': 'root', 'kind': 'index', 'title': 'Knowledge catalog',
                     'description': 'Start from index sections; preserve alternative branches.',
                     'children': roots}

    # Wide catalogs become a balanced hierarchy without losing any IDs. Each
    # bucket exposes child titles, so synthetic levels still carry real meaning.
    def bucket(children):
        result = []
        for start in range(0, len(children), MAX_OPTIONS):
            group = children[start:start+MAX_OPTIONS]
            nid = f'b{len(nodes)+1}'
            title = ' / '.join(nodes[c]['title'] for c in group)
            nodes[nid] = {'id': nid, 'kind': 'catalog_group', 'title': _clip(title, 180),
                          'description': title, 'children': group}
            result.append(nid)
        return result

    for node in list(nodes.values()):
        children = node['children']
        while len(children) > MAX_OPTIONS:
            children = bucket(children)
        node['children'] = children
    return pages, nodes, coverage, index_hash


def _blocks(text):
    """Contiguous source line blocks; never silently truncate a long line."""
    blocks, current, size, start = [], [], 0, 1
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        n = len(line.encode('utf-8'))
        if current and size+n > CHUNK_BYTES:
            blocks.append({'start_line': start, 'end_line': number-1, 'text': ''.join(current)})
            current, size, start = [], 0, number
        if n > CHUNK_BYTES:
            if current:
                blocks.append({'start_line': start, 'end_line': number-1, 'text': ''.join(current)})
                current, size = [], 0
            # A pathological single line remains represented and is reported
            # unread rather than treated as unrelated evidence.
            blocks.append({'start_line': number, 'end_line': number, 'text': line,
                           'oversized': True})
            start = number+1
        else:
            current.append(line)
            size += n
    if current:
        blocks.append({'start_line': start, 'end_line': start+len(current)-1, 'text': ''.join(current)})
    return blocks


class _Budget(Exception):
    pass


class _Search:
    def __init__(self, root, query, needs, cfg, transport, key, max_calls, max_pages):
        self.root, self.query, self.needs, self.cfg = root, query, needs, cfg
        self.transport, self.key = transport, key
        self.max_calls, self.max_pages = max_calls, max_pages
        self.calls, self.started = 0, time.monotonic()
        self.usage, self.trace = [], []
        self.selected, self.refs, self.conflicts = {}, [], []
        self.supported, self.visited, self.expanded = set(), set(), set()
        self.unread_chunks = 0
        self.previous_evidence = {}
        self.comparison_truncated = False
        self.stop_reason = 'frontier_exhausted'

    def call(self, state, questions):
        elapsed = time.monotonic()-self.started
        if self.calls >= self.max_calls or elapsed >= MAX_SECONDS:
            self.stop_reason = 'request_budget' if self.calls >= self.max_calls else 'time_budget'
            raise _Budget()
        payload = {'model': self.cfg['model'], 'state': state, 'questions': questions}
        # Redact credentials from all outgoing strings, even in page metadata.
        def scrub(value):
            if isinstance(value, str):
                return core.sanitize_text(value, self.key)
            if isinstance(value, dict):
                return {k: scrub(v) for k, v in value.items()}
            if isinstance(value, list):
                return [scrub(v) for v in value]
            return value
        payload = scrub(payload)
        if len(core._jsonbytes(payload)) > core.MAX_PAYLOAD_SIZE_BYTES:
            self.stop_reason = 'packet_budget'
            raise _Budget()
        self.calls += 1
        cfg = dict(self.cfg, timeout=min(self.cfg['timeout'], max(.1, MAX_SECONDS-elapsed)))
        started = time.monotonic()
        try:
            result = core._review(payload, cfg, self.transport, self.key)
        except ValueError:
            self.trace.append({'operation': state['operation'], 'status': 'unavailable',
                               'latency_ms': round((time.monotonic()-started)*1000, 2)})
            raise
        self.usage.append(result['usage'])
        self.trace.append({'operation': state['operation'], 'answers': result['answers'],
                           'page': state.get('page', {}).get('path'), 'branch': state.get('branch'),
                           'latency_ms': round((time.monotonic()-started)*1000, 2)})
        return result['answers']

    def route(self, node, children, nodes):
        options = {}
        for child in children:
            item = nodes[child]
            options[child] = {k: _clip(str(item[k]), 380 if k == 'description' else 180)
                              for k in ('id', 'kind', 'path', 'title', 'description') if k in item}
        state = {'operation': 'branch_route', 'query': self.query, 'needs': self.needs,
                 'branch': node['title'], 'context': _clip(node['description'], 1000),
                 'options': options}
        criteria = {child: None for child in children}
        criteria['none'] = 'No promising branch among these options; other branches remain possible.'
        questions = {}
        for nid in self.needs:
            questions['route_'+nid] = _choice(
                f'For `needs.{nid}`, which option is most likely to contain useful original evidence? '
                'Match meaning across languages; titles are navigation hints, not answer evidence.', criteria)
        questions['counterevidence'] = _choice(
            'Which option is most likely to contain a relevant exception or contrary evidence for '
            '`query`? Choose none if no option suggests it.', criteria)
        answers = self.call(state, questions)
        # Round-robin ranks preserve candidates for every need. Probabilities are
        # only compared within this sibling set, never across independent calls.
        ranked, preferred = [], set()
        lists = []
        for answer in answers.values():
            order = sorted(children, key=lambda n: -answer['probabilities'][n])
            lists.append(order)
            if answer['choice'] != 'none':
                preferred.update(order[:2])
        for i in range(len(children)):
            for order in lists:
                if order[i] not in ranked:
                    ranked.append(order[i])
        return [(nid, nid in preferred) for nid in ranked]

    def evaluate(self, page):
        descriptor, text = page['descriptor'], page['text']
        chunks = _blocks(text)
        retain, complete = False, True
        for index, block in enumerate(chunks):
            if block.get('oversized'):
                self.unread_chunks += 1
                complete, retain = False, True
                continue
            # Exact line IDs inside a bounded contiguous chunk. This makes the
            # returned location a selection of original bytes, not generated prose.
            lines = block['text'].splitlines(keepends=True)
            blocks = {}
            for offset in range(0, len(lines), 8):
                start = block['start_line']+offset
                blocks[f'L{start}'] = {'text': ''.join(lines[offset:offset+8]),
                                       'start_line': start,
                                       'end_line': min(start+7, block['end_line'])}
            # Keep Choice option count below the API limit on very short lines.
            if len(blocks) > 200:
                blocks = {f'L{block["start_line"]}': {k: block[k] for k in ('text', 'start_line', 'end_line')}}
            prior, prior_bytes = {}, 0
            for nid, evidence in self.previous_evidence.items():
                for item in reversed(evidence):
                    if prior_bytes + len(core._jsonbytes(item)) > 4000:
                        self.comparison_truncated = True
                        continue
                    prior.setdefault(nid, []).append(item)
                    prior_bytes += len(core._jsonbytes(item))
            state = {'operation': 'branch_evidence', 'query': self.query,
                     'needs': self.needs, 'page': descriptor, 'blocks': blocks,
                     'previous_evidence': prior}
            questions = {}
            for nid in self.needs:
                questions['coverage_'+nid] = _choice(
                    f'Does the supplied original text directly answer `needs.{nid}`? '
                    'Use only this text. Topic similarity or a link to another page is not an answer.',
                    {'full': 'The requested information is explicitly supported in the supplied text.',
                     'partial': 'Useful evidence but a material part of the need is missing.',
                     'none': 'This text does not address the need.',
                     'unknown': 'Cannot establish adequacy from the supplied text.'})
                questions['conflict_'+nid] = _choice(
                    f'Does the current page contain a relevant exception, limitation or contradiction '
                    f'to `previous_evidence.{nid}`, or to a premise or apparent answer to `needs.{nid}`? '
                    'Compare the actual source claims, including different values answering a neutral '
                    'question. Judge independently of support. Previous evidence may be incomplete.',
                    {'present': 'Relevant contrary evidence or an important limitation is stated.',
                     'absent': 'No relevant contrary evidence is apparent in this text.',
                     'unknown': 'Cannot determine whether the supplied text conflicts.'})
                questions['location_'+nid] = _choice(
                    f'Which source block best supports, partially answers or challenges `needs.{nid}`? '
                    'Select none if no source block supports such a judgment.',
                    {**{bid: None for bid in blocks}, 'none': 'No supporting or contrary source block.'})
            try:
                answers = self.call(state, questions)
            except (_Budget, ValueError):
                self.unread_chunks += len(chunks)-index
                # Do not lose prior evidence/unknown text when later chunks fail.
                self.selected[descriptor['path']] = page
                raise
            for nid in self.needs:
                coverage = answers['coverage_'+nid]
                conflict = answers['conflict_'+nid]
                location = answers['location_'+nid]['choice']
                relation = coverage['choice']
                if relation in {'full', 'partial', 'unknown'} or conflict['choice'] != 'absent':
                    retain = True
                if location in blocks and (relation in {'full', 'partial'} or conflict['choice'] == 'present'):
                    source = blocks[location]
                    ref = {k: descriptor[k] for k in ('path', 'file_sha256')}
                    ref.update(need_id=nid, start_line=source['start_line'], end_line=source['end_line'],
                               relation=relation, provisional=True)
                    self.refs.append(ref)
                    if relation in {'full', 'partial'}:
                        self.previous_evidence.setdefault(nid, []).append(
                            {**{k: ref[k] for k in ('path', 'file_sha256', 'start_line', 'end_line')},
                             'text': source['text']})
                    if conflict['choice'] == 'present':
                        # The whole evaluated chunk is the conflict context; the
                        # chosen best block may instead have been the support.
                        self.conflicts.append(dict(ref, relation='contrary',
                                                   start_line=block['start_line'], end_line=block['end_line']))
                    # A concentration threshold is a conservative routing heuristic,
                    # not a calibrated correctness probability or final acceptance.
                    if relation == 'full' and coverage['confidence'] >= .5:
                        self.supported.add(nid)
                elif relation == 'full':
                    retain = True  # Missing location cannot establish coverage.
                if conflict['choice'] == 'present' and location not in blocks:
                    self.conflicts.append({**descriptor, 'need_id': nid, 'relation': 'contrary',
                                           'start_line': block['start_line'], 'end_line': block['end_line'],
                                           'provisional': True})
        if retain:
            self.selected[descriptor['path']] = page
        return complete


def find(query, needs=None, repo_root=None, dry_run=False, transport=None, api_key=None,
         max_calls=24, max_pages=12, local_first=None):
    """Navigate index -> branches -> full evidence internally in one caller turn.

    ``local_first`` None follows the config key ``local_first`` (default off);
    True/False override it for this call. When on, a confident local search
    returns its pages with zero API calls and without loading a credential;
    otherwise the Jev route runs with the local candidates evaluated first.
    """
    validated = _validate(query, needs, max_calls, max_pages)
    if type(dry_run) is not bool:
        raise ValueError('dry_run must be boolean')
    if local_first is not None and type(local_first) is not bool:
        raise ValueError('local_first must be boolean or None')
    root = core.resolve_repo_root(repo_root)
    if local_first is None:
        local_first = core.get_config(root).get('local_first') is True
    if not local_first:
        return _jev_find(query, needs, root, dry_run, transport, api_key, max_calls, max_pages)
    stage =_local_stage(root, core.get_config(root), query, validated, explicit=needs is not None)
    if stage['result'] is not None:
        return stage['result']
    result = _jev_find(query, needs, root, dry_run, transport, api_key, max_calls, max_pages,
                       seeds=stage['seeds'])
    result['source'] = 'jev'
    result['local'] = stage['summary']
    return result


def _round_robin(lists, limit):
    chosen = []
    for i in range(max((len(x) for x in lists), default=0)):
        for items in lists:
            if i < len(items) and items[i] not in chosen and len(chosen) < limit:
                chosen.append(items[i])
    return chosen


def _local_stage(root, cfg, query, needs, explicit):
    """Optional retrieval-first stage. Never loads a credential or calls a transport."""
    started = time.perf_counter()
    summary = {'confident': False, 'evidence_judged': False}
    try:
        try:
            from . import bsb_local_search as local
        except ImportError:
            import bsb_local_search as local
        options = local.settings(cfg)
        depth = max(options['local_pages'], options['local_seeds'], 1)
        decisions, found = {}, {}
        with local.LocalSearch(root, roots=cfg['search_roots'], backend=options['local_backend'],
                               model=options['local_model']) as engine:
            report = engine.update()
            for nid, need in needs.items():
                # Explicit needs are fragments; keep the question as their context.
                text = f'{query}\n{need}' if explicit else need
                outcome = engine.search(text, limit=depth, update=False, options=options)
                decisions[nid] = outcome['confidence']
                found[nid] = outcome['results']
            summary.update(engine.backend_info())
    except Exception as exc:  # the local stage is optional; it must never break find
        summary.update(reason=f'local_unavailable:{type(exc).__name__}',
                       latency_ms=round((time.perf_counter() - started) * 1000, 2))
        return {'result': None, 'seeds': [], 'summary': summary}
    confident = all(d['confident'] for d in decisions.values())
    summary.update(confident=confident, decisions=decisions,
                   candidates={nid: [{k: r[k] for k in ('rank', 'path', 'title', 'score', 'start_line', 'end_line')}
                                     for r in rows] for nid, rows in found.items()},
                   index={k: report[k] for k in ('pages', 'chunks', 'added', 'changed', 'removed', 'scan_complete')})
    seeds = _round_robin([[r['path'] for r in rows] for rows in found.values()], options['local_seeds'])

    def fall_through(reason):
        summary.update(confident=False, reason=reason,
                       latency_ms=round((time.perf_counter() - started) * 1000, 2))
        return {'result': None, 'seeds': seeds, 'summary': summary}

    if not confident:
        return fall_through('not_confident')
    indexed = {r['path']: r['file_sha256'] for rows in found.values() for r in rows}
    chosen = _round_robin([[r['path'] for r in rows[:options['local_pages']]] for rows in found.values()],
                          options['local_pages'] * len(found))
    pages, omitted, returned_bytes = [], [], 0
    for path in chosen:
        try:
            descriptor, text, _ = nav._document(root, path)
        except (ValueError, OSError, UnicodeError):
            return fall_through('local_page_unreadable')
        if descriptor['file_sha256'] != indexed[path]:
            return fall_through('local_page_changed')
        if returned_bytes + descriptor['bytes'] > MAX_RETURN_BYTES:
            omitted.append(descriptor)
            continue
        pages.append({**descriptor, 'text': text, 'full_page': True})
        returned_bytes += descriptor['bytes']
    returned = {p['path'] for p in pages}
    # Each need was judged confident on its top page; if the byte budget dropped that
    # page, the need is not resolved by what is returned, so let Jev handle the call.
    unresolved = [needs[nid] for nid, rows in found.items() if not rows or rows[0]['path'] not in returned]
    if not pages or unresolved:
        summary['unresolved_needs'] = unresolved
        return fall_through('local_output_budget')
    refs = [{'path': r['path'], 'file_sha256': r['file_sha256'], 'need_id': nid,
             'start_line': r['start_line'], 'end_line': r['end_line'], 'relation': 'local_match',
             'provisional': True, 'full_page_returned': r['path'] in returned}
            for nid, rows in found.items() for r in rows[:options['local_pages']]
            if r['path'] in returned or any(o['path'] == r['path'] for o in omitted)]
    summary.update(reason=None, pages_returned=len(pages),
                   latency_ms=round((time.perf_counter() - started) * 1000, 2),
                   next_step='Read every returned page in full. Local ranks are not evidence judgments; '
                             'if these pages do not answer every need, run find again with --no-local.')
    coverage = {'roots': cfg['search_roots'], 'catalog_pages': report['pages'],
                'scan_complete': report['scan_complete'], 'evaluated_pages': 0,
                'unvisited_pages': report['pages'], 'unread_chunks': 0, 'search_complete': False,
                'stop_reason': 'output_budget' if omitted else 'local_confident',
                'global_absence_proven': False, 'output_omitted_pages': len(omitted),
                'returned_bytes': returned_bytes}
    result = {'status': 'local', 'source': 'local', 'session_id': None, 'pages': pages,
              'evidence_refs': refs, 'omitted_pages': omitted, 'needs': needs, 'conflicts': [],
              'unresolved_needs': [], 'coverage': coverage, 'usage': [], 'api_calls': 0,
              'model': cfg['model'], 'full_page_read_required': True, 'review_required': True,
              'global_absence_proven': False, 'local': summary}
    return {'result': result, 'seeds': seeds, 'summary': summary}


def _jev_find(query, needs=None, repo_root=None, dry_run=False, transport=None, api_key=None,
              max_calls=24, max_pages=12, seeds=None):
    """The Jev catalog route; ``seeds`` are page paths evaluated before the root traversal."""
    needs = _validate(query, needs, max_calls, max_pages)
    if type(dry_run) is not bool:
        raise ValueError('dry_run must be boolean')
    root = core.resolve_repo_root(repo_root)
    cfg = core.get_config(root)
    pages, nodes, scan, index_hash = _build_catalog(root)
    coverage = {**scan, 'catalog_pages': len(pages), 'evaluated_pages': 0,
                'unvisited_pages': len(pages), 'unread_chunks': 0, 'search_complete': False,
                'stop_reason': 'not_started', 'global_absence_proven': False}
    result = {'status': 'disabled', 'session_id': None, 'pages': [], 'evidence_refs': [],
              'omitted_pages': [], 'needs': needs,
              'conflicts': [], 'unresolved_needs': list(needs.values()), 'coverage': coverage,
              'usage': [], 'api_calls': 0, 'model': cfg['model'],
              'full_page_read_required': True, 'review_required': True,
              'global_absence_proven': False}
    if dry_run or not cfg['enabled']:
        result['status'] = 'dry_run' if dry_run else 'disabled'
        coverage['stop_reason'] = result['status']
        return result
    key = api_key or core.load_api_key()
    if not key:
        result['status'] = 'unavailable'
        coverage['stop_reason'] = 'credential_unavailable'
        return result
    if not isinstance(key, str) or key in query or any(key in n for n in needs.values()):
        raise ValueError('Invalid or secret-bearing request')
    # Omit secret-bearing pages entirely; never return those bytes to the caller.
    if any(key in page['text'] for page in pages.values()):
        result['status'] = 'unavailable'
        coverage['stop_reason'] = 'credential_in_source'
        return result
    search = _Search(root, query, needs, cfg, transport, key, max_calls, max_pages)
    stack = [('root', True)]
    unavailable = False
    seeded = 0
    try:
        # Optional local candidates are evaluated first; traversal then continues
        # from the root as usual, skipping re-evaluation of those pages.
        for path in seeds or ():
            if path not in pages or path in search.visited:
                continue
            if len(search.visited) >= max_pages:
                search.stop_reason = 'page_budget'
                break
            search.visited.add(path)
            seeded += 1
            search.evaluate(pages[path])
        while stack:
            if time.monotonic()-search.started >= MAX_SECONDS:
                search.stop_reason = 'time_budget'
                break
            node_id, preferred = stack.pop()
            if node_id in search.expanded:
                continue
            if search.supported == set(needs) and not preferred:
                # Keep preferred alternative paths for possible counterevidence.
                if not any(p for n, p in stack if n not in search.expanded):
                    search.stop_reason = 'evidence_found_alternatives_retained'
                    break
                continue
            node = nodes[node_id]
            if node['kind'] == 'page' and node['path'] not in search.visited:
                if len(search.visited) >= max_pages:
                    search.stop_reason = 'page_budget'
                    break
                path = node['path']
                search.visited.add(path)
                search.evaluate(pages[path])
            search.expanded.add(node_id)
            children = [c for c in node['children'] if c not in search.expanded]
            if children:
                order = search.route(node, children, nodes)
                stack.extend(reversed([(child, preferred and selected) for child, selected in order]))
    except _Budget:
        pass
    except ValueError:
        unavailable = True
        search.stop_reason = 'service_unavailable_or_invalid'

    coverage.update(evaluated_pages=len(search.visited),
                    unvisited_pages=len(pages)-len(search.visited),
                    unread_chunks=search.unread_chunks, stop_reason=search.stop_reason,
                    conflict_comparison_truncated=search.comparison_truncated)
    if seeds is not None:
        coverage['seeded_pages'] = seeded
    coverage['search_complete'] = bool(scan['scan_complete'] and not coverage['unvisited_pages']
                                       and not search.unread_chunks and not unavailable)
    result.update(api_calls=search.calls, usage=search.usage,
                  unresolved_needs=[text for nid, text in needs.items() if nid not in search.supported])

    # Recheck the complete catalog used for routing, including index changes and
    # newly created pages. A stale routing snapshot must never mint a fresh receipt.
    try:
        fresh, _, fresh_scan, fresh_index = _build_catalog(root)
    except (ValueError, OSError, UnicodeError):
        result['status'] = 'stale'
        coverage['stop_reason'] = 'catalog_unavailable'
        coverage['search_complete'] = False
        result['unresolved_needs'] = list(needs.values())
        return result
    hashes = lambda entries: {p: v['descriptor']['file_sha256'] for p, v in entries.items()}
    if hashes(fresh) != hashes(pages) or fresh_index != index_hash or fresh_scan != scan:
        result['status'] = 'stale'
        coverage['stop_reason'] = 'catalog_changed'
        coverage['search_complete'] = False
        result['unresolved_needs'] = list(needs.values())
        return result

    returned = []
    returned_bytes = 0
    omitted = []
    contrary_paths = {r['path'] for r in search.conflicts}
    ordered = sorted(search.selected.items(), key=lambda item: item[0] not in contrary_paths)
    for path, page in ordered:
        if returned_bytes + page['descriptor']['bytes'] > MAX_RETURN_BYTES:
            omitted.append(path)
            continue
        returned.append({**page['descriptor'], 'text': page['text'], 'full_page': True})
        returned_bytes += page['descriptor']['bytes']
    returned_paths = {p['path'] for p in returned}
    refs = [dict(r, full_page_returned=r['path'] in returned_paths) for r in search.refs]
    conflicts = [dict(r, full_page_returned=r['path'] in returned_paths) for r in search.conflicts]
    if omitted:
        coverage['stop_reason'] = 'output_budget'
        result['unresolved_needs'] = list(needs.values())
    coverage['output_omitted_pages'] = len(omitted)
    coverage['returned_bytes'] = returned_bytes
    result.update(pages=returned, evidence_refs=refs, conflicts=conflicts,
                  omitted_pages=[pages[p]['descriptor'] for p in omitted])
    limited = search.stop_reason in {'request_budget', 'time_budget', 'page_budget', 'packet_budget'}
    result['status'] = ('unavailable' if unavailable and not returned else
                        'partial' if returned and (result['unresolved_needs'] or conflicts or
                                                  unavailable or search.unread_chunks or limited or omitted or
                                                  search.comparison_truncated or not scan['scan_complete']) else
                        'ready' if returned else 'unresolved')
    offered_paths = sorted(returned_paths | set(omitted))
    descriptors = [pages[p]['descriptor'] for p in offered_paths]
    session = nav._session(query, list(needs.values()), descriptors, offered_paths, root)
    session['read'] = list(returned_paths)
    session['bytes_read'] = returned_bytes
    session['frontier'] = sorted({nodes[c]['path'] for p in returned_paths
                                 for c in nodes[pages[p]['id']]['children']
                                 if nodes[c]['kind'] == 'page' and nodes[c]['path'] not in returned_paths})
    session['branching'] = {'coverage': coverage, 'unvisited_paths': sorted(set(pages)-search.visited),
                            'trace': search.trace, 'usage': search.usage,
                            'evidence_refs': refs, 'conflicts': conflicts}
    with core._TransactionLock(root):
        nav._save(session, root)
    result['session_id'] = session['session_id']
    return result


def caller_result(result):
    """Source-complete caller packet; detailed API metrics stay in the receipt.

    Keep self-contained source hashes while omitting per-call accounting and
    catalog metadata. No source or contrary evidence is trimmed for savings.
    """
    pages = [{k:p[k] for k in ('path','file_sha256','text','full_page') if k in p}
             for p in result['pages']]
    omitted = [{k:p[k] for k in ('path','file_sha256') if k in p}
               for p in result.get('omitted_pages', [])]

    def refs(items):
        output = []
        for item in items:
            ref = {k:item[k] for k in ('path','file_sha256','need_id','start_line','end_line','relation') if k in item}
            output.append(ref)
        return output

    output = {'status': result['status'], 'session_id': result.get('session_id'),
              'pages': pages, 'evidence_refs': refs(result['evidence_refs']),
              'conflicts': refs(result['conflicts']), 'omitted_pages': omitted,
              'needs': result.get('needs', {}), 'unresolved_needs': result['unresolved_needs'],
              'coverage': result['coverage'], 'global_absence_proven': False,
              'full_page_read_required': True, 'review_required': True}
    if 'source' in result:
        # Only present when the local-first stage ran; the default packet is unchanged.
        output.update(source=result['source'], api_calls=result.get('api_calls', 0),
                      local=result.get('local'))
    return output
