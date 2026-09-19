"""Progressive full-page reading with local receipts and bounded graph expansion.

Receipts prevent accidental bypass through this gateway, not a hostile local user.
Model classifications prioritize work; neither scores nor sessions prove absence.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import uuid
from pathlib import Path

try:
    from . import bsb_jev as core
except ImportError:
    import bsb_jev as core

MAX_SCAN_FILES = 10000
MAX_SCAN_BYTES = 20 * 1024 * 1024
MAX_PAGE_BYTES = 256 * 1024
MAX_STEPS = 4


def _allowed(root, name):
    path = core._safe_path(root, name)
    if path.suffix.lower() != '.md' or any(p.startswith('.') for p in Path(name).parts):
        raise ValueError('Only visible Markdown within configured search roots is readable')
    if not any(path.is_relative_to(core._safe_path(root, r)) for r in core.get_config(root)['search_roots']):
        raise ValueError('Page outside configured search roots')
    return path


def _document(root, name):
    path = _allowed(root, name)
    if path.stat().st_size > MAX_PAGE_BYTES:
        raise ValueError('Oversized page; use an explicitly reviewed external reading route')
    data = path.read_bytes()
    if len(data) > MAX_PAGE_BYTES:
        raise ValueError('Page grew past the read limit')
    content = data.decode('utf-8-sig')
    if core.SECRET_CONTENT_REGEX.search(content) or '\x00' in content:
        raise ValueError('Secret-looking or binary page refused')
    meta = core._metadata(content)
    return {'path': name, 'title': meta.get('title') or path.stem,
            'file_sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}, content, meta


def catalog(repo_root):
    """Local bounded scan, including explicit coverage on excluded/unreadable files."""
    root = core.resolve_repo_root(repo_root)
    docs, seen, size, incomplete = [], set(), 0, False
    roots = core.get_config(root)['search_roots']
    for name in roots:
        folder = core._safe_path(root, name)
        if not folder.is_dir():
            incomplete = True
            continue
        for parent, dirs, files in os.walk(folder, followlinks=False):
            safe_dirs = []
            for d in sorted(dirs):
                p = Path(parent) / d
                if d.startswith('.') or p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
                    incomplete = True
                else:
                    safe_dirs.append(d)
            dirs[:] = safe_dirs
            for filename in sorted(files):
                if not filename.lower().endswith('.md'):
                    continue
                path = Path(parent) / filename
                rel = path.relative_to(root).as_posix()
                if rel in seen:
                    continue
                if len(seen) >= MAX_SCAN_FILES or size >= MAX_SCAN_BYTES:
                    return docs, {'roots': roots, 'files_scanned': len(seen), 'bytes_scanned': size,
                                  'scan_complete': False, 'global_absence_proven': False}
                seen.add(rel)
                try:
                    descriptor, text, meta = _document(root, rel)
                    if size + descriptor['bytes'] > MAX_SCAN_BYTES:
                        incomplete = True
                        continue
                    size += descriptor['bytes']
                    docs.append((descriptor, text, meta))
                except (ValueError, OSError, UnicodeError):
                    incomplete = True
    return docs, {'roots': roots, 'files_scanned': len(seen), 'bytes_scanned': size,
                  'scan_complete': not incomplete, 'global_absence_proven': False}


def _save(session, root):
    session['plan_signature'] = core._signature(session, root)
    core._atomic(core._state(root) / (session['session_id'] + '.json'), core._jsonbytes(session))


def _load(session_id, root):
    if not isinstance(session_id, str) or not re.fullmatch(r'nav-[0-9a-f]{32}', session_id):
        raise ValueError('Invalid navigation session')
    import json
    path = core._state(root) / (session_id + '.json')
    if path.is_symlink() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('Unsafe navigation receipt')
    session = json.loads(path.read_bytes())
    if not hmac.compare_digest(session.get('plan_signature', ''), core._signature(session, root)):
        raise ValueError('Tampered navigation receipt')
    if session.get('roots') != core.get_config(root)['search_roots']:
        raise ValueError('Search roots changed; start a fresh navigation session')
    # Every descriptor was hashed when it entered the session.  Rejecting a
    # changed deferred page here prevents a later `next` call from refreshing
    # its descriptor and silently laundering a stale receipt.
    for name, descriptor in session.get('documents', {}).items():
        try:
            current, _text, _meta = _document(root, name)
        except Exception:
            raise ValueError('A catalogued page is unavailable; start a fresh navigation session') from None
        if current['file_sha256'] != descriptor.get('file_sha256'):
            raise ValueError('A catalogued page changed since retrieval; start a fresh navigation session')
    return session


def _session(query, needs, descriptors, offered, root):
    return {'session_id': 'nav-' + uuid.uuid4().hex, 'query': query, 'needs': needs,
            'roots': core.get_config(root)['search_roots'],
            'documents': {d['path']: d for d in descriptors}, 'offered': list(offered),
            'read': [], 'frontier': [], 'steps': 0, 'bytes_read': 0}


def _compact(plan):
    # Classifier windows and per-choice distributions are diagnostic artifacts,
    # not additional context the answerer must ingest on every navigation step.
    return {k: v for k, v in plan.items() if k not in {'excerpts'}}


def source(literal, repo_root=None, dry_run=False):
    """Case-insensitive literal occurrence/title/alias search. No paid model call."""
    root = core.resolve_repo_root(repo_root)
    if not isinstance(literal, str) or not literal.strip() or len(literal) > 4096 or core.SECRET_CONTENT_REGEX.search(literal):
        raise ValueError('Source lookup requires a non-secret literal of 1..4096 characters')
    docs, coverage = catalog(root)
    needle = literal.strip().casefold()
    matches = []
    for descriptor, content, meta in docs:
        identifiers = [descriptor['path'], descriptor['title'], *meta.get('aliases', [])]
        identity = any(needle == x.casefold() for x in identifiers)
        if identity or needle in content.casefold():
            matches.append(dict(descriptor, match='identifier' if identity else 'literal_occurrence'))
    coverage['matched_files'] = len(matches)
    coverage['meaning'] = 'Literal occurrence only, within reported roots and scan limits; not semantic proof.'
    if len(matches) > 256:
        raise ValueError('More than 256 literal matches; use a more specific source identifier')
    session = _session(literal, [literal], matches, [x['path'] for x in matches], root)
    if not dry_run:
        _save(session, root)
    return {'status': 'exact_local', 'session_id': None if dry_run else session['session_id'],
            'matches': matches, 'coverage': coverage, 'api_calls': 0}


def _links(text, root):
    # Resolve exact full paths and unique title/alias/slug links. Ambiguity is preserved.
    docs, _ = catalog(root)
    names = {}
    for d, _, meta in docs:
        p = Path(d['path'])
        for key in [d['path'], p.with_suffix('').as_posix(), p.stem, d['title'], *meta.get('aliases', [])]:
            names.setdefault(key.casefold(), set()).add(d['path'])
    found = set()
    for link in re.findall(r'\[\[([^\]]+)\]\]', text):
        key = link.split('|')[0].split('#')[0].strip().casefold()
        found.update(names.get(key, set()))
        # Preserve a syntactically safe full-path link even when its target is
        # currently missing. The next step can report and prune that link
        # without making it look like global absence.
        if not names.get(key) and '/' in key:
            candidate = key if key.endswith('.md') else key + '.md'
            try:
                safe = core._safe_path(root, candidate).relative_to(root).as_posix()
                if any(safe == r or safe.startswith(r.rstrip('/') + '/')
                       for r in core.get_config(root).get('search_roots', [])):
                    found.add(safe)
            except Exception:
                pass
    return sorted(found)


def read_page(session_id, path, repo_root=None):
    """Return one offered page in full, hash-checked, plus safe outgoing links."""
    root = core.resolve_repo_root(repo_root)
    with core._TransactionLock(root):
        session = _load(session_id, root)
        if path not in session['offered']:
            raise ValueError('Page not offered; use next or a specific source lookup first')
        descriptor, content, _ = _document(root, path)
        if descriptor['file_sha256'] != session['documents'][path]['file_sha256']:
            raise ValueError('Page changed since retrieval; start a fresh session')
        links = _links(content, root)
        if path not in session['read']:
            session['read'].append(path)
        session['bytes_read'] += descriptor['bytes']
        session['frontier'] = sorted(set(session['frontier'] + links) - set(session['read']))
        _save(session, root)
    return {**descriptor, 'text': content, 'links': links, 'full_page': True,
            'session_id': session_id, 'total_bytes_returned': session['bytes_read']}


def navigate(query, needs, repo_root=None, dry_run=False, transport=None, api_key=None):
    try:
        from .bsb_jev_focus import focus
    except ImportError:
        from bsb_jev_focus import focus
    root = core.resolve_repo_root(repo_root)
    plan = focus(query, needs, root, dry_run=dry_run, transport=transport, api_key=api_key)
    docs = plan['initial'] + plan['deferred']
    session = _session(query, needs, docs, [d['path'] for d in plan['initial']], root)
    session['reviews'] = [plan]
    if not dry_run:
        _save(session, root)
    return {**_compact(plan), 'session_id': None if dry_run else session['session_id'],
            'next_command': 'read <session_id> <offered path>; next <session_id> for gaps/links'}


def next_step(session_id, repo_root=None, needs=None, dry_run=False, transport=None, api_key=None):
    """Classify an unread graph frontier, then retain deferred candidates for later."""
    try:
        from .bsb_jev_focus import focus
    except ImportError:
        from bsb_jev_focus import focus
    root = core.resolve_repo_root(repo_root)
    with core._TransactionLock(root):
        session = _load(session_id, root)
        if session['steps'] >= MAX_STEPS:
            return {'status': 'step_limit', 'session_id': session_id,
                    'unread': [p for p in session['documents'] if p not in session['read']],
                    'coverage': 'Bound reached, not absence. Start a narrower navigation/source lookup.'}
        offered = set(session.get('offered', []))
        read = set(session.get('read', []))
        # A page already offered is waiting for a full read; do not spend the
        # step budget classifying it again. New graph links and deferred pages
        # are the deterministic frontier for this step.
        paths = list(dict.fromkeys(
            [p for p in session.get('frontier', []) if p not in offered and p not in read]
            + [p for p in session.get('documents', {}) if p not in offered and p not in read]
        ))
        unread_offered = [p for p in session.get('offered', []) if p not in read]
        if not paths and unread_offered:
            return {'status': 'read_offered_first', 'session_id': session_id,
                    'offered_unread': unread_offered,
                    'coverage': 'Initial pages remain available for full-page reading; no absence claim.'}
        paths = paths[:16]
        if not paths:
            return {'status': 'frontier_exhausted', 'session_id': session_id,
                    'coverage': 'Only this visited frontier is exhausted. No global absence claim.'}
        candidates = []
        skipped = []
        for i, path in enumerate(paths):
            try:
                candidates.append(dict(_document(root, path)[0], id=f'c{i+1}'))
            except Exception:
                skipped.append(path)
        if skipped:
            session['frontier'] = [p for p in session.get('frontier', []) if p not in skipped]
            session.setdefault('skipped_paths', []).extend(p for p in skipped if p not in session.get('skipped_paths', []))
        if not candidates:
            session['steps'] += 1
            _save(session, root)
            return {'status': 'frontier_unreadable', 'session_id': session_id,
                    'step': session['steps'], 'skipped_paths': skipped,
                    'coverage': 'Unreadable linked pages were skipped; no absence claim.'}
        plan = focus(session['query'], needs or session['needs'], root, candidates=candidates,
                     dry_run=dry_run, transport=transport, api_key=api_key)
        if not dry_run:
            for d in plan['initial'] + plan['deferred']:
                session['documents'][d['path']] = d
            session['offered'] = list(dict.fromkeys(session['offered'] + [d['path'] for d in plan['initial']]))
            session['steps'] += 1
            session.setdefault('reviews', []).append(plan)
            _save(session, root)
    result = {**_compact(plan), 'session_id': session_id, 'step': session['steps']}
    if skipped:
        result['skipped_paths'] = skipped
    return result
