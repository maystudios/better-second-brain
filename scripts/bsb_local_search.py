#!/usr/bin/env python3
"""Optional local retrieval-first search for a Better Second Brain.

Standard library only by default. The ``keyword`` backend indexes heading
chunks of the brain's Markdown pages into SQLite FTS5 (BM25) and adds an exact
title / alias / wikilink-name route. The optional ``hybrid`` backend adds dense
vectors from ``sentence-transformers`` + ``torch`` (only when both import) and
fuses the routes with reciprocal-rank fusion (RRF). Nothing here calls a
network API; the hybrid backend only loads a model that sentence-transformers
can already reach (set ``HF_HUB_OFFLINE=1`` to forbid downloads).

The index lives in ``<root>/.bsb-local/`` (override with ``BSB_LOCAL_STATE``)
and is refreshed incrementally (size, mtime, then SHA-256) on every search.

Ranks and the confidence rule are uncalibrated retrieval heuristics. A
confident result means "these are the strongest local candidates", never that
they answer the question or that other pages are irrelevant.

CLI::

    python scripts/bsb_local_search.py index [--rebuild]
    python scripts/bsb_local_search.py search "<question>" [--json] [--limit N]
    python scripts/bsb_local_search.py status
"""
from __future__ import annotations

import argparse
import array
import hashlib
import importlib.util
import json
import math
import os
import re
import sqlite3
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from . import bsb_jev as core
except ImportError:
    import bsb_jev as core

SCHEMA_VERSION = 1
STATE_ENV = 'BSB_LOCAL_STATE'
DEFAULT_STATE_DIR = '.bsb-local'
BACKENDS = core.LOCAL_BACKENDS
DEFAULTS = core.LOCAL_DEFAULTS
QUERY_PROMPT = 'task: search result | query: {q}'
DOCUMENT_PROMPT = 'title: {title} | text: {content}'
TOKENIZER = 'porter unicode61 remove_diacritics 2'
# Chunk FTS5 bm25() column weights for (sub-heading path, body prose, bare-wikilink slugs).
# The page's title/aliases/slug live in a separate one-row-per-page FTS table, because
# FTS5 bm25 normalises by whole-row length: a title copied into every chunk row would
# make the shortest chunk of a title-matching page win regardless of its content.
BM25_WEIGHTS = (1.5, 1.0, 0.3)
TITLE_WEIGHT = 1.0
SECOND_CHUNK_WEIGHT = 0.25
RRF_K = 60
CHUNK_CHARS = 1600
MAX_TERMS = 32
MAX_CHUNK_ROWS = 400
MAX_PAGE_BYTES = 256 * 1024
MAX_SCAN_FILES = 10000
MAX_SCAN_BYTES = 20 * 1024 * 1024
SNIPPET_CHARS = 400
EMBED_BATCH = 16
EXCLUDED_DIRS = {'.git', '.bsb-jev', '.bsb-local', '.obsidian', '.trash'}
# Secret-looking names are matched on the basename with any Markdown suffix removed,
# so `id_rsa.md` or `credentials.json.md` are refused like `id_rsa` or `credentials.json`.
SECRET_SUFFIXES = {'.pem', '.key', '.pfx', '.p12', '.dpapi'}
SECRET_BASENAMES = {name.casefold() for name in core.SECRET_FILE_PATTERNS} | {
    'credentials.json', 'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519', '.netrc', '.pgpass', '.npmrc', '.pypirc'}
SECRET_PREFIXES = ('.env', 'id_rsa', 'id_dsa', 'id_ecdsa', 'id_ed25519')
STOPWORDS = frozenset('''
a an the and or but for nor so yet of to in on at by as is are was were be been being am do does did done
this that these those it its it's i me my we our you your he him his she her they them their what when
where which who whom whose how why can could should would will shall may might must than then there here
into onto from with without about also according specific not no yes if else any all some each every
has have had having get got use used using via per vs
der die das den dem des ein eine einer eines einem einen und oder aber mit von zur zum im am ist sind war
waren wie was wer wem wen welche welcher welches warum wieso weshalb aus auf bei sich auch fuer für nach
vor werden wird wurde wurden kann können konnte soll sollen muss müssen nicht kein keine es er sie wir ihr
ich du dass daß zu in an als um über unter durch gibt gilt
'''.split())

_HEADING = re.compile(r'^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$')
_FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')
_LINK = re.compile(r'\[\[([^\]]+)\]\]')
_WORD = re.compile(r'[^\W_]+')


class LocalSearchUnavailable(RuntimeError):
    """The local index cannot run on this interpreter (for example no FTS5)."""


# -----------------------------------------------------------------------------
# Settings, text normalisation and chunking
# -----------------------------------------------------------------------------

def settings(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Local-first settings: Jev config keys, then ``BSB_<KEY>`` environment overrides.

    Every key except ``local_first`` can be overridden per process (for example
    ``BSB_LOCAL_BACKEND=hybrid`` or ``BSB_LOCAL_PAGES=2``), so a brain can be
    measured without writing into its config. Values are validated like config.
    """
    cfg = cfg or {}
    merged = {key: cfg.get(key, default) for key, default in DEFAULTS.items()}
    for key, default in DEFAULTS.items():
        raw = os.environ.get('BSB_' + key.upper(), '').strip()
        if key == 'local_first' or not raw:
            continue
        if isinstance(default, int):
            merged[key] = int(raw)
        elif isinstance(default, float):
            merged[key] = float(raw)
        else:
            merged[key] = raw.lower() if key == 'local_backend' else raw
    core.validate_local_config(merged)
    return merged


def fold(text: str) -> str:
    """Casefold and strip diacritics (consistent with FTS5 remove_diacritics)."""
    decomposed = unicodedata.normalize('NFKD', text)
    return ''.join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def content_tokens(text: str) -> List[str]:
    """Ordered content words: folded, stopwords and 1-character tokens removed."""
    tokens = _WORD.findall(fold(text))
    content = [t for t in tokens if len(t) > 1 and t not in STOPWORDS]
    return content or tokens


def query_terms(text: str) -> List[str]:
    return list(dict.fromkeys(content_tokens(text)))[:MAX_TERMS]


def _contains(sequence: Sequence[str], part: Sequence[str]) -> bool:
    n = len(part)
    return any(list(sequence[i:i + n]) == list(part) for i in range(len(sequence) - n + 1))


def _trim(lines: List[str], start: int, end: int) -> Tuple[int, int]:
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return start, end


def chunk_markdown(text: str) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Split Markdown into heading-path chunks with 1-based inclusive line ranges.

    Frontmatter is skipped (title/aliases are indexed separately), fenced code
    is never read as a heading, long sections are split at line boundaries and
    a heading-only section is merged into the chunk that follows it.
    """
    lines = text.splitlines()
    body = 0
    if lines and lines[0].strip() == '---':
        for i in range(1, len(lines)):
            if lines[i].strip() in ('---', '...'):
                body = i + 1
                break
    sections: List[Tuple[str, int, int]] = []
    headings: List[str] = []
    stack: List[Tuple[int, str]] = []
    path, start, fence = '', body, None
    for i in range(body, len(lines)):
        marker = _FENCE.match(lines[i])
        if marker:
            char = marker.group(1)[0]
            fence = char if fence is None else (None if char == fence else fence)
            continue
        if fence:
            continue
        match = _HEADING.match(lines[i])
        if not match or not match.group(2).strip():
            continue
        if i > start:
            sections.append((path, start, i))
        level, title = len(match.group(1)), match.group(2).strip()
        headings.append(title)
        stack = [item for item in stack if item[0] < level] + [(level, title)]
        path, start = ' > '.join(t for _, t in stack), i
    sections.append((path, start, len(lines)))

    chunks: List[Dict[str, Any]] = []
    pending: Optional[Tuple[int, int]] = None  # heading-only lines waiting for content

    def emit(heading: str, a: int, b: int) -> None:
        nonlocal pending
        a, b = _trim(lines, a, b)
        if a >= b:
            return
        if pending is not None:
            a = pending[0]
            pending = None
        chunks.append({'heading': heading, 'start_line': a + 1, 'end_line': b,
                       'text': '\n'.join(lines[a:b])})

    for heading, a, b in sections:
        a, b = _trim(lines, a, b)
        if a >= b:
            continue
        if b - a == 1 and _HEADING.match(lines[a]) and pending is None:
            pending = (a, b)
            continue
        window_start, size = a, 0
        for j in range(a, b):
            n = len(lines[j]) + 1
            if j > window_start and size + n > CHUNK_CHARS:
                emit(heading, window_start, j)
                window_start, size = j, 0
            size += n
        emit(heading, window_start, b)
    if pending is not None:
        a, b = pending
        chunks.append({'heading': path, 'start_line': a + 1, 'end_line': b, 'text': '\n'.join(lines[a:b])})
    if not chunks:
        chunks.append({'heading': '', 'start_line': 1, 'end_line': max(1, len(lines)), 'text': ''})
    return headings, chunks


def keyword_body(text: str) -> Tuple[str, str]:
    """Split FTS text into prose and link words.

    ``[[target|display]]`` keeps its display text in the prose; a bare
    ``[[wiki/x/slug]]`` contributes only its slug words, to a low-weight
    column, so short citation/link lists do not outrank the defining text.
    """
    slugs: List[str] = []

    def replace(match):
        parts = match.group(1).split('|', 1)
        slugs.append(re.sub(r'[-_]+', ' ', parts[0].split('#', 1)[0].rstrip('/').rsplit('/', 1)[-1]))
        return parts[1] if len(parts) > 1 and parts[1].strip() else ' '
    prose = _LINK.sub(replace, text)
    return prose, ' '.join(slugs)


def document_text(title: str, chunk_text: str) -> str:
    return DOCUMENT_PROMPT.format(title=title or 'none', content=chunk_text)


def _is_link(path: Path) -> bool:
    return path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction())


def _secret_name(name: str) -> bool:
    lowered = Path(name).name.casefold()
    for markdown in ('.markdown', '.md'):
        if lowered.endswith(markdown):
            lowered = lowered[:-len(markdown)]
            break
    if lowered in SECRET_BASENAMES or lowered.startswith(SECRET_PREFIXES) or lowered.endswith('credentials.json'):
        return True
    return any(suffix in SECRET_SUFFIXES for suffix in Path(lowered).suffixes)


def _excluded_component(rel: str) -> Optional[str]:
    """The first hidden or excluded path component of a relative path, else None."""
    for part in Path(rel).parts:
        if part.startswith('.') or part.casefold() in EXCLUDED_DIRS:
            return part
    return None


def state_dir(root: Path, create: bool = True) -> Path:
    """Index state folder: $BSB_LOCAL_STATE, else <root>/.bsb-local."""
    override = os.environ.get(STATE_ENV, '').strip()
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
    else:
        path = root / DEFAULT_STATE_DIR
    if _is_link(path):
        raise ValueError('Linked local search state refused')
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


# -----------------------------------------------------------------------------
# Optional semantic backend
# -----------------------------------------------------------------------------

def packages_available() -> bool:
    """True when the optional embedding packages can be imported (not imported here)."""
    return all(importlib.util.find_spec(name) is not None for name in ('torch', 'sentence_transformers'))


class SentenceTransformerEmbedder:
    """sentence-transformers encoder; bf16 on CUDA, fp32 on CPU, never fp16."""

    def __init__(self, model_name: str):
        import torch
        from sentence_transformers import SentenceTransformer

        try:  # keep stderr quiet for agent callers; purely cosmetic
            from transformers.utils import logging as hf_logging
            hf_logging.disable_progress_bar()
        except Exception:
            pass
        cuda = torch.cuda.is_available()
        dtype = torch.bfloat16 if cuda else torch.float32
        device = 'cuda' if cuda else 'cpu'

        def load(source):
            try:
                return SentenceTransformer(source, device=device, model_kwargs={'dtype': dtype})
            except TypeError:  # older transformers spell it torch_dtype
                return SentenceTransformer(source, device=device, model_kwargs={'torch_dtype': dtype})

        try:
            model = load(model_name)
        except OSError:
            # Offline cache without a refs/main entry: use its single cached snapshot.
            snapshot = _cached_snapshot(model_name)
            if snapshot is None:
                raise
            model = load(snapshot)
        self.model = model
        self.name = model_name
        self.device = device
        self.dtype = str(dtype).replace('torch.', '')

    def encode(self, texts: List[str]) -> List[List[float]]:
        # Prompts are already applied by the caller; prompt='' prevents a second one.
        vectors = self.model.encode(list(texts), prompt='', batch_size=EMBED_BATCH,
                                    normalize_embeddings=True, convert_to_numpy=True,
                                    show_progress_bar=False)
        return [[float(x) for x in row] for row in vectors]


def _cached_snapshot(model_name: str) -> Optional[str]:
    """The only snapshot folder of ``org/name`` in the Hugging Face cache, else None."""
    if '/' not in model_name or Path(model_name).exists():
        return None
    try:
        from huggingface_hub.constants import HF_HUB_CACHE
    except ImportError:
        return None
    folder = Path(HF_HUB_CACHE) / ('models--' + model_name.replace('/', '--')) / 'snapshots'
    snapshots = [p for p in folder.iterdir() if p.is_dir()] if folder.is_dir() else []
    return str(snapshots[0]) if len(snapshots) == 1 else None


def load_embedder(model_name: str):
    """Load the real embedder. Raises ImportError when optional packages are missing."""
    if not packages_available():
        raise ImportError('sentence-transformers and torch are required for the hybrid backend')
    return SentenceTransformerEmbedder(model_name)


def _normalise(vector: Sequence[float]) -> List[float]:
    values = [float(x) for x in vector]
    norm = math.sqrt(sum(x * x for x in values))
    if not math.isfinite(norm) or norm == 0:
        raise ValueError('Embedding vector is zero or not finite')
    return [x / norm for x in values]


def _similarities(flat: array.array, dim: int, query: List[float]) -> List[float]:
    try:
        import numpy

        matrix = numpy.frombuffer(flat.tobytes(), dtype=numpy.float32).reshape(-1, dim)
        return [float(x) for x in matrix @ numpy.asarray(query, dtype=numpy.float32)]
    except ImportError:
        rows = len(flat) // dim
        return [sum(a * b for a, b in zip(flat[i * dim:(i + 1) * dim], query)) for i in range(rows)]


def rrf(rankings: Dict[str, List[str]], k: int = RRF_K,
        boost: Optional[Iterable[str]] = None) -> List[Tuple[str, float]]:
    """Reciprocal-rank fusion: score(p) = sum over routes of 1 / (k + rank).

    Each page in ``boost`` (exact title/alias/slug/link-name matches) gets one
    extra rank-1 term, so an exact name is never out-voted by a single route.
    """
    scores: Dict[str, float] = {path: 1.0 / (k + 1) for path in (boost or ())}
    for ordered in rankings.values():
        for rank, path in enumerate(ordered, 1):
            scores[path] = scores.get(path, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))


# -----------------------------------------------------------------------------
# Index
# -----------------------------------------------------------------------------

class LocalSearch:
    """Incremental SQLite FTS5 index over configured roots, plus optional vectors."""

    def __init__(self, root, roots: Optional[List[str]] = None, backend: Optional[str] = None,
                 model: Optional[str] = None, embedder=None, state: Optional[Path] = None):
        self.root = core.resolve_repo_root(root)
        options = settings(core.get_config(self.root))
        self.roots = list(roots) if roots is not None else core.get_config(self.root)['search_roots']
        if not self.roots or any(not isinstance(r, str) for r in self.roots):
            raise ValueError('Invalid search roots')
        for name in self.roots:
            core._safe_path(self.root, name)
            if _excluded_component(name):
                # A configured root inside .git/.obsidian/.trash/.bsb-jev/... would bypass the
                # per-directory pruning below, so it is refused outright.
                raise ValueError(f'Hidden or excluded search root refused: {name}')
        self.requested_backend = backend or options['local_backend']
        if self.requested_backend not in BACKENDS:
            raise ValueError(f'Unknown local backend: {self.requested_backend!r}')
        self.model_name = model or options['local_model']
        self.state = Path(state) if state is not None else state_dir(self.root)
        self.state.mkdir(parents=True, exist_ok=True)
        self.db_path = self.state / 'index.sqlite'
        self.backend, self.fallback, self.embedder = 'keyword', None, embedder
        self._resolved = embedder is not None or self.requested_backend == 'keyword'
        if embedder is not None:
            self.backend = 'hybrid'
        self.conn = None
        self.conn = self._connect()

    def _ensure_backend(self) -> None:
        """Load the optional embedder once; any failure degrades to keyword, never breaks."""
        if self._resolved:
            return
        self._resolved = True
        try:
            self.embedder = load_embedder(self.model_name)
            self.backend = 'hybrid'
        except ImportError:
            self.fallback = 'optional_packages_missing'
        except Exception as exc:  # model not cached, CUDA failure, ...
            self.fallback = f'embedding_backend_failed:{type(exc).__name__}'

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self) -> None:
        if getattr(self, 'conn', None) is not None:
            self.conn.close()
            self.conn = None

    def backend_info(self) -> Dict[str, Any]:
        info = {'backend': self.backend if self._resolved else 'not_loaded',
                'requested_backend': self.requested_backend, 'backend_fallback': self.fallback}
        if self.backend == 'hybrid':
            info['model'] = getattr(self.embedder, 'name', self.model_name)
            for attribute in ('device', 'dtype'):
                if hasattr(self.embedder, attribute):
                    info[attribute] = getattr(self.embedder, attribute)
        return info

    def _connect(self) -> sqlite3.Connection:
        for attempt in (1, 2):
            conn = sqlite3.connect(str(self.db_path), timeout=30, isolation_level=None)
            try:
                self._ensure_schema(conn)
                return conn
            except (LocalSearchUnavailable, sqlite3.OperationalError):
                conn.close()  # e.g. "database is locked": never delete a live index
                raise
            except sqlite3.DatabaseError:
                conn.close()  # "file is not a database" / corrupt image: rebuild once
                if attempt == 2:
                    raise
                self._remove_db()
        raise AssertionError('unreachable')

    def _remove_db(self) -> None:
        for suffix in ('', '-journal', '-wal', '-shm'):
            Path(str(self.db_path) + suffix).unlink(missing_ok=True)

    def _ensure_schema(self, conn: sqlite3.Connection) -> None:
        conn.execute('CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        root_row = conn.execute("SELECT value FROM meta WHERE key='root'").fetchone()
        if row is not None and (row[0] != str(SCHEMA_VERSION) or
                                (root_row is not None and root_row[0] != str(self.root))):
            # Schema or brain changed: rebuild from scratch rather than mix states.
            for table in ('chunks_fts', 'names_fts', 'chunks', 'links', 'pages', 'meta'):
                conn.execute(f'DROP TABLE IF EXISTS {table}')
            conn.execute('CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            (self.state / 'vectors.json').unlink(missing_ok=True)
            (self.state / 'vectors.f32').unlink(missing_ok=True)
        conn.execute('CREATE TABLE IF NOT EXISTS pages(path TEXT PRIMARY KEY, size INTEGER NOT NULL, '
                     'mtime_ns INTEGER NOT NULL, sha256 TEXT NOT NULL, title TEXT NOT NULL, '
                     'aliases TEXT NOT NULL)')
        conn.execute('CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, path TEXT NOT NULL, '
                     'ordinal INTEGER NOT NULL, heading TEXT NOT NULL, start_line INTEGER NOT NULL, '
                     'end_line INTEGER NOT NULL, text TEXT NOT NULL, embed_key TEXT NOT NULL)')
        conn.execute('CREATE INDEX IF NOT EXISTS chunks_path ON chunks(path)')
        conn.execute('CREATE TABLE IF NOT EXISTS links(src TEXT NOT NULL, target TEXT NOT NULL, '
                     'display TEXT NOT NULL)')
        conn.execute('CREATE INDEX IF NOT EXISTS links_src ON links(src)')
        try:
            conn.execute('CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING '
                         f"fts5(heading, body, links, tokenize='{TOKENIZER}')")
            conn.execute('CREATE VIRTUAL TABLE IF NOT EXISTS names_fts USING '
                         f"fts5(names, tokenize='{TOKENIZER}')")
        except sqlite3.OperationalError as exc:
            if 'fts5' in str(exc).lower():
                raise LocalSearchUnavailable('sqlite_fts5_unavailable') from None
            raise
        conn.execute("INSERT OR REPLACE INTO meta VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
        conn.execute("INSERT OR REPLACE INTO meta VALUES('root', ?)", (str(self.root),))

    # -- scanning ----------------------------------------------------------
    def scan(self) -> Tuple[List[Tuple[str, Path, int, int]], Dict[str, int], bool]:
        """Visible Markdown files under the roots: (relative path, path, size, mtime_ns)."""
        files: List[Tuple[str, Path, int, int]] = []
        skipped = {'excluded_dirs': 0, 'hidden_or_secret_name': 0, 'linked': 0, 'oversized': 0}
        seen, total, complete = set(), 0, True
        for name in self.roots:
            folder = core._safe_path(self.root, name)
            if not folder.is_dir():
                complete = False
                continue
            for parent, dirs, names in os.walk(folder, followlinks=False):
                keep = []
                for directory in sorted(dirs):
                    candidate = Path(parent) / directory
                    if directory.startswith('.') or directory.casefold() in EXCLUDED_DIRS:
                        skipped['excluded_dirs'] += 1
                    elif _is_link(candidate):
                        skipped['linked'] += 1
                        complete = False
                    else:
                        keep.append(directory)
                dirs[:] = keep
                for filename in sorted(names):
                    if not filename.lower().endswith('.md'):
                        continue
                    path = Path(parent) / filename
                    rel = path.relative_to(self.root).as_posix()
                    if rel in seen:
                        continue
                    seen.add(rel)
                    if _excluded_component(Path(rel).parent.as_posix()):
                        skipped['excluded_dirs'] += 1
                        continue
                    if filename.startswith('.') or _secret_name(filename):
                        skipped['hidden_or_secret_name'] += 1
                        continue
                    if _is_link(path):
                        skipped['linked'] += 1
                        complete = False
                        continue
                    try:
                        stat = path.stat()
                    except OSError:
                        complete = False
                        continue
                    if stat.st_size > MAX_PAGE_BYTES:
                        skipped['oversized'] += 1
                        complete = False
                        continue
                    if len(files) >= MAX_SCAN_FILES or total + stat.st_size > MAX_SCAN_BYTES:
                        complete = False
                        return files, skipped, complete
                    total += stat.st_size
                    files.append((rel, path, stat.st_size, stat.st_mtime_ns))
        return files, skipped, complete

    # -- incremental update ------------------------------------------------
    def update(self, rebuild: bool = False) -> Dict[str, Any]:
        started = time.perf_counter()
        self._ensure_backend()
        files, skipped, complete = self.scan()
        skipped = dict(skipped, secret_content=0, unreadable=0)
        counts = {'added': 0, 'changed': 0, 'removed': 0, 'unchanged': 0, 'touched': 0}
        conn = self.conn
        conn.execute('BEGIN IMMEDIATE')
        try:
            if rebuild:
                for table in ('chunks_fts', 'names_fts', 'chunks', 'links', 'pages'):
                    conn.execute(f'DELETE FROM {table}')
            known = {row[0]: row[1:] for row in conn.execute('SELECT path, size, mtime_ns, sha256 FROM pages')}
            current = set()
            for rel, path, size, mtime_ns in files:
                previous = known.get(rel)
                if previous is not None and previous[0] == size and previous[1] == mtime_ns:
                    counts['unchanged'] += 1
                    current.add(rel)
                    continue
                try:
                    data = path.read_bytes()
                    if len(data) > MAX_PAGE_BYTES:
                        raise ValueError('grew past limit')
                    text = data.decode('utf-8-sig')
                except (OSError, UnicodeError, ValueError):
                    skipped['unreadable'] += 1
                    complete = False
                    continue
                if core.SECRET_CONTENT_REGEX.search(text) or '\x00' in text:
                    skipped['secret_content'] += 1
                    continue
                digest = hashlib.sha256(data).hexdigest()
                current.add(rel)
                if previous is not None and previous[2] == digest:
                    conn.execute('UPDATE pages SET size=?, mtime_ns=? WHERE path=?', (size, mtime_ns, rel))
                    counts['touched'] += 1
                    continue
                self._index_page(conn, rel, text, size, mtime_ns, digest)
                counts['changed' if previous is not None else 'added'] += 1
            for rel in set(known) - current:
                self._delete_page(conn, rel)
                counts['removed'] += 1
            conn.execute("INSERT OR REPLACE INTO meta VALUES('roots', ?)", (json.dumps(self.roots),))
            conn.execute("INSERT OR REPLACE INTO meta VALUES('updated_at', ?)", (str(time.time()),))
            conn.execute('COMMIT')
        except BaseException:
            conn.execute('ROLLBACK')
            raise
        report = {**counts, 'pages': conn.execute('SELECT COUNT(*) FROM pages').fetchone()[0],
                  'chunks': conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0],
                  'skipped': skipped, 'scan_complete': complete}
        if self.backend == 'hybrid':
            report['vectors'] = self.sync_vectors()
        report['update_ms'] = round((time.perf_counter() - started) * 1000, 2)
        return report

    def _delete_page(self, conn: sqlite3.Connection, rel: str) -> None:
        conn.execute('DELETE FROM chunks_fts WHERE rowid IN (SELECT id FROM chunks WHERE path=?)', (rel,))
        conn.execute('DELETE FROM names_fts WHERE rowid IN (SELECT rowid FROM pages WHERE path=?)', (rel,))
        conn.execute('DELETE FROM chunks WHERE path=?', (rel,))
        conn.execute('DELETE FROM links WHERE src=?', (rel,))
        conn.execute('DELETE FROM pages WHERE path=?', (rel,))

    def _index_page(self, conn, rel, text, size, mtime_ns, digest) -> None:
        self._delete_page(conn, rel)
        meta = core._metadata(text)
        headings, chunks = chunk_markdown(text)
        stem = Path(rel).stem
        title = meta.get('title') or (headings[0] if headings else stem)
        aliases = [a for a in meta.get('aliases', []) if a]
        names = ' '.join([title, *aliases, re.sub(r'[-_]+', ' ', stem)])
        cursor = conn.execute('INSERT INTO pages VALUES(?,?,?,?,?,?)',
                              (rel, size, mtime_ns, digest, title, json.dumps(aliases, ensure_ascii=False)))
        conn.execute('INSERT INTO names_fts(rowid, names) VALUES(?,?)', (cursor.lastrowid, names))
        for ordinal, chunk in enumerate(chunks):
            key = hashlib.sha256(document_text(title, chunk['text']).encode('utf-8')).hexdigest()
            cursor = conn.execute('INSERT INTO chunks(path, ordinal, heading, start_line, end_line, text, '
                                  'embed_key) VALUES(?,?,?,?,?,?,?)',
                                  (rel, ordinal, chunk['heading'], chunk['start_line'], chunk['end_line'],
                                   chunk['text'], key))
            # The page title is already in the title column; keep only sub-headings here
            # so a short section is not rewarded merely for repeating the page title.
            parts = chunk['heading'].split(' > ') if chunk['heading'] else []
            sub = ' > '.join(parts[1:] if parts and parts[0] == title else parts)
            prose, slugs = keyword_body(chunk['text'])
            conn.execute('INSERT INTO chunks_fts(rowid, heading, body, links) VALUES(?,?,?,?)',
                         (cursor.lastrowid, sub, prose, slugs))
        for link in _LINK.findall(text):
            parts = link.split('|', 1)
            target = parts[0].split('#', 1)[0].strip()
            display = parts[1].strip() if len(parts) > 1 else ''
            if target:
                conn.execute('INSERT INTO links VALUES(?,?,?)', (rel, target, display))

    # -- vectors -----------------------------------------------------------
    def _load_vectors(self) -> Tuple[Dict[str, int], array.array, int]:
        meta_path, data_path = self.state / 'vectors.json', self.state / 'vectors.f32'
        empty: Tuple[Dict[str, int], array.array, int] = ({}, array.array('f'), 0)
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
            if meta.get('model') != getattr(self.embedder, 'name', None) or meta.get('schema') != SCHEMA_VERSION:
                return empty
            dim, keys = int(meta['dim']), list(meta['keys'])
            flat = array.array('f')
            flat.frombytes(data_path.read_bytes())
            if sys.byteorder == 'big':
                flat.byteswap()
            if dim <= 0 or len(flat) != dim * len(keys):
                return empty
            return {key: i for i, key in enumerate(keys)}, flat, dim
        except (OSError, ValueError, KeyError, TypeError):
            return empty

    def sync_vectors(self) -> Dict[str, Any]:
        """Embed only new/changed chunks; keep one float32 row per unique chunk text."""
        rows, flat, dim = self._load_vectors()
        records = self.conn.execute('SELECT c.embed_key, p.title, c.text FROM chunks c '
                                    'JOIN pages p ON p.path = c.path ORDER BY c.id').fetchall()
        wanted = list(dict.fromkeys(r[0] for r in records))
        texts = {r[0]: document_text(r[1], r[2]) for r in records}
        missing = [key for key in wanted if key not in rows]
        fresh: Dict[str, List[float]] = {}
        for start in range(0, len(missing), EMBED_BATCH * 4):
            batch = missing[start:start + EMBED_BATCH * 4]
            vectors = self.embedder.encode([texts[key] for key in batch])
            if len(vectors) != len(batch):
                raise ValueError('Embedder returned a wrong number of vectors')
            for key, vector in zip(batch, vectors):
                fresh[key] = _normalise(vector)
        if fresh:
            dims = {len(v) for v in fresh.values()}
            if len(dims) != 1:
                raise ValueError('Embedder returned inconsistent dimensions')
            if rows and dims != {dim}:
                # Same model name, different width: discard the stale matrix and re-embed all.
                (self.state / 'vectors.json').unlink(missing_ok=True)
                return self.sync_vectors()
            dim = dims.pop()
        unchanged = not missing and len(rows) == len(wanted)
        if not unchanged:
            out = array.array('f')
            for key in wanted:
                if key in fresh:
                    out.extend(fresh[key])
                else:
                    i = rows[key]
                    out.extend(flat[i * dim:(i + 1) * dim])
            data = array.array('f', out)
            if sys.byteorder == 'big':
                data.byteswap()
            core._atomic(self.state / 'vectors.f32', data.tobytes())
            meta = {'schema': SCHEMA_VERSION, 'model': getattr(self.embedder, 'name', None), 'dim': dim,
                    'dtype': 'float32', 'byteorder': 'little', 'keys': wanted,
                    'query_prompt': QUERY_PROMPT, 'document_prompt': DOCUMENT_PROMPT}
            core._atomic(self.state / 'vectors.json', json.dumps(meta).encode('utf-8'))
        return {'embedded': len(fresh), 'rows': len(wanted), 'dim': dim}

    # -- routes ------------------------------------------------------------
    def _keyword(self, terms: List[str]) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
        if not terms:
            return [], {}
        expression = ' OR '.join('"%s"' % t for t in terms)
        weights = ', '.join(str(w) for w in BM25_WEIGHTS)
        rows = self.conn.execute(
            f'SELECT c.path, c.id, -bm25(chunks_fts, {weights}) FROM chunks_fts '
            f'JOIN chunks c ON c.id = chunks_fts.rowid WHERE chunks_fts MATCH ? '
            f'ORDER BY bm25(chunks_fts, {weights}) LIMIT ?', (expression, MAX_CHUNK_ROWS)).fetchall()
        titles = self.conn.execute(
            'SELECT p.path, -bm25(names_fts) FROM names_fts JOIN pages p ON p.rowid = names_fts.rowid '
            'WHERE names_fts MATCH ?', (expression,)).fetchall()
        pages: Dict[str, Dict[str, Any]] = {}
        for path, chunk_id, score in rows:
            entry = pages.setdefault(path, {'scores': [], 'chunk': chunk_id, 'title_score': 0.0})
            entry['scores'].append(float(score))
        for path, score in titles:
            pages.setdefault(path, {'scores': [], 'chunk': None, 'title_score': 0.0})['title_score'] = float(score)
        for entry in pages.values():
            s = entry['scores']
            entry['score'] = ((s[0] if s else 0.0) + SECOND_CHUNK_WEIGHT * (s[1] if len(s) > 1 else 0.0)
                              + TITLE_WEIGHT * entry['title_score'])
        ordered = sorted(pages, key=lambda p: (-pages[p]['score'], p))
        return ordered, pages

    def _coverage(self, terms: List[str], paths: Iterable[str]) -> Dict[str, float]:
        paths = list(paths)
        hits = {p: 0 for p in paths}
        if not terms:
            return {p: 0.0 for p in paths}
        for term in terms:
            found = {r[0] for r in self.conn.execute(
                'SELECT DISTINCT c.path FROM chunks_fts JOIN chunks c ON c.id = chunks_fts.rowid '
                'WHERE chunks_fts MATCH ? UNION SELECT p.path FROM names_fts '
                'JOIN pages p ON p.rowid = names_fts.rowid WHERE names_fts MATCH ?',
                ('"%s"' % term, '"%s"' % term))}
            for p in paths:
                hits[p] += p in found
        return {p: hits[p] / len(terms) for p in paths}

    def _names(self, sequence: List[str]) -> List[Tuple[str, str, str]]:
        """Exact/phrase matches of title, alias, slug or wikilink display name."""
        keys: Dict[str, set] = {}
        names: Dict[str, List[str]] = {}
        for path, title, aliases in self.conn.execute('SELECT path, title, aliases FROM pages'):
            p = Path(path)
            alias_list = json.loads(aliases)
            for key in (path, p.with_suffix('').as_posix(), p.stem, title, *alias_list):
                keys.setdefault(key.casefold(), set()).add(path)
            names[path] = [title, *alias_list, re.sub(r'[-_]+', ' ', p.stem)]
        for target, display in self.conn.execute("SELECT target, display FROM links WHERE display != ''"):
            hits = keys.get(target.casefold(), set())
            if len(hits) == 1:
                names[next(iter(hits))].append(display)
        matches = []
        for path, candidates in names.items():
            best: Optional[Tuple[str, str, int]] = None
            for name in candidates:
                tokens = content_tokens(name)
                if not tokens:
                    continue
                if tokens == sequence:
                    best = ('exact', name, len(tokens))
                    break
                if len(''.join(tokens)) >= 4 and _contains(sequence, tokens):
                    if best is None or len(tokens) > best[2]:
                        best = ('phrase', name, len(tokens))
            if best:
                matches.append((path, best[0], best[1], best[2]))
        matches.sort(key=lambda m: (m[1] != 'exact', -m[3], m[0]))
        return [(path, kind, name) for path, kind, name, _ in matches]

    def _vector(self, query: str) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
        rows, flat, dim = self._load_vectors()
        if not rows:
            return [], {}
        vector = _normalise(self.embedder.encode([QUERY_PROMPT.format(q=query)])[0])
        if len(vector) != dim:
            raise ValueError('Query embedding dimension differs from the index')
        sims = _similarities(flat, dim, vector)
        pages: Dict[str, Dict[str, Any]] = {}
        for chunk_id, path, key in self.conn.execute('SELECT id, path, embed_key FROM chunks'):
            if key not in rows:
                continue
            sim = sims[rows[key]]
            entry = pages.get(path)
            if entry is None or sim > entry['score']:
                pages[path] = {'score': sim, 'chunk': chunk_id}
        ordered = sorted(pages, key=lambda p: (-pages[p]['score'], p))
        return ordered, pages

    # -- search ------------------------------------------------------------
    def search(self, query: str, limit: int = 5, update: bool = True,
               options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        started = time.perf_counter()
        if not isinstance(query, str) or not query.strip() or len(query) > 8192:
            raise ValueError('Query must contain 1..8192 characters')
        if core.SECRET_CONTENT_REGEX.search(query):
            raise ValueError('Secret-looking query refused')
        if type(limit) is not int or not 1 <= limit <= 50:
            raise ValueError('Limit must be an integer in 1..50')
        options = options or settings(core.get_config(self.root))
        self._ensure_backend()
        report = self.update() if update else None
        terms = query_terms(query)
        sequence = content_tokens(query)
        keyword_order, keyword = self._keyword(terms)
        name_hits = self._names(sequence)
        routes: Dict[str, List[str]] = {'keyword': keyword_order, 'names': [p for p, _, _ in name_hits]}
        vector_order, vector = ([], {})
        if self.backend == 'hybrid':
            vector_order, vector = self._vector(query)
            routes['vector'] = vector_order
        fused = rrf(routes, boost=[p for p, kind, _ in name_hits if kind == 'exact'])
        top = fused[:limit]
        coverage = self._coverage(terms, [p for p, _ in top])
        name_of = {p: (kind, name) for p, kind, name in name_hits}
        info = {r[0]: r[1:] for r in self.conn.execute('SELECT path, sha256, title FROM pages')}
        results = []
        for rank, (path, score) in enumerate(top, 1):
            chunk_id = (keyword.get(path) or {}).get('chunk') or (vector.get(path) or {}).get('chunk')
            if chunk_id is None:
                row = self.conn.execute('SELECT id FROM chunks WHERE path=? ORDER BY ordinal LIMIT 1',
                                        (path,)).fetchone()
                chunk_id = row[0] if row else None
            chunk = self.conn.execute('SELECT heading, start_line, end_line, text FROM chunks WHERE id=?',
                                      (chunk_id,)).fetchone() if chunk_id is not None else ('', 1, 1, '')
            item = {'rank': rank, 'path': path, 'title': info[path][1], 'score': round(score, 6),
                    'file_sha256': info[path][0], 'heading': chunk[0], 'start_line': chunk[1],
                    'end_line': chunk[2], 'snippet': chunk[3][:SNIPPET_CHARS],
                    'keyword_rank': keyword_order.index(path) + 1 if path in keyword else None,
                    'keyword_score': round(keyword[path]['score'], 6) if path in keyword else None,
                    'name_match': name_of.get(path, (None,))[0],
                    'term_coverage': round(coverage.get(path, 0.0), 4)}
            if self.backend == 'hybrid':
                item['vector_rank'] = vector_order.index(path) + 1 if path in vector else None
                item['vector_score'] = round(vector[path]['score'], 6) if path in vector else None
            results.append(item)
        confidence = decide(results, keyword_order, keyword, name_hits, self.backend, options, len(terms))
        output = {'status': 'ok' if results else 'no_results', 'query': query, 'terms': terms,
                  **self.backend_info(), 'results': results, 'confidence': confidence, 'api_calls': 0}
        if report is not None:
            output['index'] = report
        output['latency_ms'] = round((time.perf_counter() - started) * 1000, 2)
        return output

    # -- status ------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        files, skipped, complete = self.scan()
        known = {r[0]: r[1:] for r in self.conn.execute('SELECT path, size, mtime_ns FROM pages')}
        names = {f[0] for f in files}
        pending = sum(1 for rel, _, size, mtime in files if known.get(rel) != (size, mtime))
        vectors = {}
        meta_path = self.state / 'vectors.json'
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding='utf-8'))
                vectors = {'model': meta.get('model'), 'rows': len(meta.get('keys', [])), 'dim': meta.get('dim')}
            except (OSError, ValueError):
                vectors = {'error': 'unreadable'}
        return {'status': 'ok', 'root': str(self.root), 'roots': self.roots, 'state_dir': str(self.state),
                'schema_version': SCHEMA_VERSION, 'tokenizer': TOKENIZER,
                'pages': self.conn.execute('SELECT COUNT(*) FROM pages').fetchone()[0],
                'chunks': self.conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0],
                'pending_changes': pending + len(set(known) - names), 'scan_complete': complete,
                'skipped': skipped, 'vectors': vectors, 'packages_available': packages_available(),
                **self.backend_info(), 'api_calls': 0}


def decide(results: List[Dict[str, Any]], keyword_order: List[str], keyword: Dict[str, Dict[str, Any]],
           name_hits: List[Tuple[str, str, str]], backend: str, options: Dict[str, Any],
           term_count: int) -> Dict[str, Any]:
    """Documented, configurable confidence rule (first matching rule wins).

    1. exact_name: the top page's title/alias/slug/wikilink name equals the
       question's content words, or is the only page whose name occurs in it.
    2. route_agreement (hybrid): keyword and vector routes both rank it first.
    3. keyword_margin: the keyword route ranks it first, its BM25 page score
       leads the second page by >= local_min_margin (relative) and it contains
       >= local_min_coverage of the question's content words.
    """
    margin = None
    if keyword_order:
        first = keyword[keyword_order[0]]['score']
        second = keyword[keyword_order[1]]['score'] if len(keyword_order) > 1 else 0.0
        margin = (first - second) / first if first > 0 else 0.0
    signals = {'terms': term_count, 'keyword_margin': None if margin is None else round(margin, 4),
               'name_matches': len(name_hits), 'top_path': results[0]['path'] if results else None}
    if not results or term_count == 0:
        return {'confident': False, 'rule': None, 'reason': 'no_results', 'signals': signals}
    top = results[0]
    signals.update(term_coverage=top['term_coverage'], keyword_rank=top['keyword_rank'],
                   name_match=top['name_match'])
    if backend == 'hybrid':
        signals['vector_rank'] = top.get('vector_rank')
    if top['name_match'] == 'exact' or (top['name_match'] == 'phrase' and len(name_hits) == 1):
        return {'confident': True, 'rule': 'exact_name', 'reason': None, 'signals': signals}
    if backend == 'hybrid' and top['keyword_rank'] == 1 and top.get('vector_rank') == 1:
        return {'confident': True, 'rule': 'route_agreement', 'reason': None, 'signals': signals}
    if top['keyword_rank'] == 1 and margin is not None and margin >= options['local_min_margin'] \
            and top['term_coverage'] >= options['local_min_coverage']:
        return {'confident': True, 'rule': 'keyword_margin', 'reason': None, 'signals': signals}
    if top['keyword_rank'] != 1:
        reason = 'routes_disagree' if backend == 'hybrid' else 'top_not_keyword_first'
    elif margin is None or margin < options['local_min_margin']:
        reason = 'keyword_margin_below_threshold'
    else:
        reason = 'term_coverage_below_threshold'
    return {'confident': False, 'rule': None, 'reason': reason, 'signals': signals}


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def _print(text: str) -> None:
    encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
    sys.stdout.write(text.encode(encoding, errors='replace').decode(encoding, errors='replace') + '\n')


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--root', default=argparse.SUPPRESS, help='Brain root (default: discover from cwd)')
    common.add_argument('--roots', default=argparse.SUPPRESS, help='Comma-separated roots (default: Jev search_roots)')
    common.add_argument('--backend', choices=BACKENDS, default=argparse.SUPPRESS,
                        help='keyword (stdlib) or hybrid (needs sentence-transformers + torch)')
    common.add_argument('--model', default=argparse.SUPPRESS, help='Embedding model for hybrid')
    parser = argparse.ArgumentParser(prog='bsb_local_search', description=__doc__.split('\n\n')[0],
                                     parents=[common])
    sub = parser.add_subparsers(dest='command', required=True)
    p_index = sub.add_parser('index', parents=[common], help='Create or incrementally refresh the index')
    p_index.add_argument('--rebuild', action='store_true', help='Drop and rebuild the keyword index')
    p_search = sub.add_parser('search', parents=[common], help='Search (refreshes the index first)')
    p_search.add_argument('query')
    p_search.add_argument('--json', action='store_true', help='Print the JSON result')
    p_search.add_argument('--limit', type=int, default=5, help='Pages to return (1..50)')
    sub.add_parser('status', parents=[common], help='Index status and pending changes (JSON)')
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = core.resolve_repo_root(getattr(args, 'root', None))
        roots = getattr(args, 'roots', None)
        roots = [r.strip() for r in roots.split(',') if r.strip()] if roots else None
        with LocalSearch(root, roots=roots, backend=getattr(args, 'backend', None),
                         model=getattr(args, 'model', None)) as engine:
            if args.command == 'index':
                report = engine.update(rebuild=args.rebuild)
                print(json.dumps({'status': 'ok', **engine.backend_info(), 'index': report, 'api_calls': 0}))
            elif args.command == 'status':
                print(json.dumps(engine.status()))
            else:
                result = engine.search(args.query, limit=args.limit)
                if args.json:
                    print(json.dumps(result))
                else:
                    decision = result['confidence']
                    fallback = f" (fallback: {result['backend_fallback']})" if result['backend_fallback'] else ''
                    _print(f"backend={result['backend']}{fallback} confident={decision['confident']} "
                           f"rule={decision['rule'] or decision['reason']} latency_ms={result['latency_ms']}")
                    for item in result['results']:
                        _print(f"{item['rank']:>2}. {item['path']}:{item['start_line']}-{item['end_line']}"
                               f"  [{item['title']}]  {item['heading']}")
    except Exception as exc:
        sys.stderr.write(f'Error: {core.sanitize_text(str(exc))}\n')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
