#!/usr/bin/env python3
"""Bridge graphify outputs into the source lint loop (BSB CLAUDE.md s3.4).

This tool does NOT run graphify itself -- the ``/graphify`` skill produces the
artifacts. ``graphify_sync.py`` only *reads* what graphify already wrote and
turns it into actionable lint work:

  ./graphify-out/graph.json       (node/edge graph)
  ./graphify-out/GRAPH_REPORT.md  (human-readable graphify report)

If neither file is present it prints guidance and exits 0 (this is not an
error -- you simply have not run ``/graphify`` yet).

From ``graph.json`` it derives:
  (a) god/hub nodes  -- the top-N nodes by degree. For each it checks whether a
      ``wiki/concepts/<slug>.md`` or ``wiki/entities/<slug>.md`` page exists,
      and lists the MISSING ones as candidate hub pages to stub.
  (b) orphan nodes   -- nodes with degree 0.
  (c) from GRAPH_REPORT.md it surfaces the "Surprising Connections" and
      "Suggested Questions" sections, quoted verbatim if found.

Output is a markdown report to stdout. With ``--write`` it also writes a lint
stub to ``wiki/syntheses/lint-graph-YYYY-MM-DD.md`` (never overwrites; appends
a numeric suffix if the file already exists).

The JSON shape is treated defensively: it tries common keys (``nodes`` /
``edges``; node ``id`` / ``label`` / ``name`` / ``slug``; ``degree`` if
present, otherwise computed from edges via ``source`` / ``target`` / ``from`` /
``to`` / endpoint pairs).

Python 3.10+, standard library only. Run from the repository root::

    python scripts/graphify_sync.py            # report to stdout
    python scripts/graphify_sync.py --write     # also write the lint stub
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

# The graph report contains arrows (->) and other non-ASCII; on a Windows
# cp1252 console a bare print() would crash. Force UTF-8 on stdout/stderr.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

GRAPHIFY_DIR = "graphify-out"
GRAPH_JSON = "graph.json"
GRAPH_REPORT = "GRAPH_REPORT.md"

DEFAULT_TOP_N = 15

# Sections we quote verbatim from GRAPH_REPORT.md when present.
REPORT_SECTIONS = ["Surprising Connections", "Suggested Questions"]


def slugify(text: str) -> str:
    """Kebab-case ASCII slug equal to a BSB filename."""
    text = text.strip().lower()
    # Drop accents crudely by ASCII-encoding; keep alnum, space, hyphen.
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def load_graph(path: str) -> dict | None:
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WARNING: could not parse {path}: {exc}", file=sys.stderr)
        return None


def _as_list(data: dict, *keys: str) -> list:
    for k in keys:
        v = data.get(k)
        if isinstance(v, list):
            return v
    return []


def _node_id(node) -> str | None:
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        for k in ("id", "name", "label", "slug", "title", "key"):
            if k in node and node[k] not in (None, ""):
                return str(node[k])
    return None


def _node_label(node) -> str:
    if isinstance(node, dict):
        for k in ("label", "name", "title", "id", "slug"):
            if k in node and node[k] not in (None, ""):
                return str(node[k])
    return str(node)


def _edge_endpoints(edge) -> tuple[str | None, str | None]:
    if isinstance(edge, dict):
        src = None
        dst = None
        for k in ("source", "from", "src", "start", "u", "a"):
            if k in edge:
                src = _node_id(edge[k]) if isinstance(edge[k], (dict,)) else str(edge[k])
                break
        for k in ("target", "to", "dst", "end", "v", "b"):
            if k in edge:
                dst = _node_id(edge[k]) if isinstance(edge[k], (dict,)) else str(edge[k])
                break
        return src, dst
    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
        return str(edge[0]), str(edge[1])
    return None, None


def extract_nodes_edges(graph: dict):
    """Return (id->label map, degree map) defensively from any graph shape."""
    raw_nodes = _as_list(graph, "nodes", "vertices", "entities")
    raw_edges = _as_list(graph, "edges", "links", "relationships", "relations")

    labels: dict[str, str] = {}
    declared_degree: dict[str, int] = {}
    source_files: dict[str, str] = {}
    for node in raw_nodes:
        nid = _node_id(node)
        if nid is None:
            continue
        labels[nid] = _node_label(node)
        if isinstance(node, dict):
            sf = node.get("source_file") or node.get("source-file") or node.get("file")
            if sf:
                source_files[nid] = str(sf).replace("\\", "/")
            for dk in ("degree", "deg", "connections"):
                if isinstance(node.get(dk), (int, float)):
                    declared_degree[nid] = int(node[dk])
                    break

    computed_degree: dict[str, int] = {nid: 0 for nid in labels}
    for edge in raw_edges:
        src, dst = _edge_endpoints(edge)
        for endpoint in (src, dst):
            if endpoint is None:
                continue
            labels.setdefault(endpoint, endpoint)
            computed_degree[endpoint] = computed_degree.get(endpoint, 0) + 1

    # Prefer declared degree when present, else computed.
    degree: dict[str, int] = {}
    for nid in labels:
        if nid in declared_degree:
            degree[nid] = declared_degree[nid]
        else:
            degree[nid] = computed_degree.get(nid, 0)

    return labels, degree, source_files


def existing_pages(repo_root: str) -> dict[str, str]:
    """Map every wiki page's filename slug -> its repo-relative wikilink target
    (path without .md), across ALL wiki subfolders (not just concepts/entities).
    A god node "has a page" if its source_file resolves OR its label slug matches
    one of these — so MOC/source/cheatsheet pages are no longer false 'missing'."""
    out: dict[str, str] = {}
    wiki = os.path.join(repo_root, "wiki")
    for dirpath, _dirs, files in os.walk(wiki):
        for fn in files:
            if not fn.lower().endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), repo_root).replace("\\", "/")
            out.setdefault(os.path.splitext(fn)[0], rel[:-3])
    return out


def extract_report_sections(report_text: str) -> dict[str, str]:
    """Return {section_title: quoted_body} for the sections of interest."""
    out: dict[str, str] = {}
    lines = report_text.splitlines()
    # Find headings and their levels.
    headings = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2).strip()))

    for idx, (line_no, level, title) in enumerate(headings):
        for wanted in REPORT_SECTIONS:
            if wanted.lower() in title.lower():
                # Body runs until the next heading of same-or-higher level.
                end = len(lines)
                for j in range(idx + 1, len(headings)):
                    nxt_line, nxt_level, _ = headings[j]
                    if nxt_level <= level:
                        end = nxt_line
                        break
                body = "\n".join(lines[line_no + 1:end]).strip()
                out[wanted] = body
    return out


def build_report(repo_root: str, top_n: int) -> tuple[str, dict]:
    graph_path = os.path.join(repo_root, GRAPHIFY_DIR, GRAPH_JSON)
    report_path = os.path.join(repo_root, GRAPHIFY_DIR, GRAPH_REPORT)

    graph = load_graph(graph_path)
    report_text = ""
    if os.path.isfile(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as fh:
                report_text = fh.read()
        except OSError as exc:
            print(f"WARNING: could not read {report_path}: {exc}", file=sys.stderr)

    ctx = {"have_graph": graph is not None, "have_report": bool(report_text)}

    if graph is None and not report_text:
        guidance = (
            f"No graphify artifacts found under ./{GRAPHIFY_DIR}/.\n\n"
            f"Expected ./{GRAPHIFY_DIR}/{GRAPH_JSON} and/or "
            f"./{GRAPHIFY_DIR}/{GRAPH_REPORT}.\n"
            "Run the /graphify skill first to generate the knowledge graph, "
            "then re-run this tool to derive hub-page candidates and orphans."
        )
        return guidance, ctx

    labels: dict[str, str] = {}
    degree: dict[str, int] = {}
    source_files: dict[str, str] = {}
    if graph is not None:
        labels, degree, source_files = extract_nodes_edges(graph)

    pages = existing_pages(repo_root)  # slug -> wiki/folder/slug

    # God/hub nodes: top-N by degree (desc), tie-break by label.
    ranked = sorted(
        labels.keys(),
        key=lambda nid: (-degree.get(nid, 0), labels[nid].lower()),
    )
    hubs = ranked[:top_n]
    missing_hubs = []
    present_hubs = []
    for nid in hubs:
        label = labels[nid]
        target = None
        sf = source_files.get(nid)
        if sf and os.path.isfile(os.path.join(repo_root, sf)):
            target = sf[:-3] if sf.lower().endswith(".md") else sf
        if target is None:
            slug = slugify(label)
            if slug in pages:
                target = pages[slug]
        if target:
            present_hubs.append((label, target, degree.get(nid, 0)))
        else:
            missing_hubs.append((label, slugify(label), degree.get(nid, 0)))

    orphans = sorted(
        (labels[nid] for nid in labels if degree.get(nid, 0) == 0),
        key=str.lower,
    )

    sections = extract_report_sections(report_text) if report_text else {}

    today = datetime.date.today().isoformat()
    lines: list[str] = []
    lines.append(f"# Graphify Lint Sync ({today})")
    lines.append("")
    lines.append(
        "Derived from graphify outputs (CLAUDE.md s3.4). graphify-out present: "
        f"graph.json={ctx['have_graph']}, GRAPH_REPORT.md={ctx['have_report']}."
    )
    lines.append("")

    lines.append(f"## God / hub nodes (top {top_n} by degree)")
    lines.append("")
    if not labels:
        lines.append("No nodes found in graph.json.")
    else:
        lines.append("### Missing hub pages (candidate stubs)")
        if missing_hubs:
            for label, slug, deg in missing_hubs:
                target = f"wiki/concepts/{slug}" if slug else "(unsluggable)"
                lines.append(f"- {label} (degree {deg}) -> create [[{target}]]")
        else:
            lines.append("- none; all top hubs already have pages.")
        lines.append("")
        lines.append("### Existing hub pages")
        if present_hubs:
            for label, target, deg in present_hubs:
                lines.append(f"- {label} (degree {deg}) -> [[{target}]]")
        else:
            lines.append("- none.")
    lines.append("")

    lines.append("## Orphan graph nodes (degree 0)")
    lines.append("")
    if orphans:
        for label in orphans:
            lines.append(f"- {label}")
    else:
        lines.append("- none.")
    lines.append("")

    for wanted in REPORT_SECTIONS:
        lines.append(f"## {wanted}")
        lines.append("")
        if wanted in sections and sections[wanted].strip():
            lines.append(f"Quoted from {GRAPH_REPORT}:")
            lines.append("")
            for ln in sections[wanted].splitlines():
                lines.append(f"> {ln}" if ln.strip() else ">")
        else:
            lines.append(f"_Not found in {GRAPH_REPORT}._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n", ctx


def write_stub(repo_root: str, report_md: str) -> str:
    today = datetime.date.today().isoformat()
    out_dir = os.path.join(repo_root, "wiki", "syntheses")
    os.makedirs(out_dir, exist_ok=True)

    base = f"lint-graph-{today}"
    candidate = os.path.join(out_dir, f"{base}.md")
    n = 1
    while os.path.exists(candidate):
        n += 1
        candidate = os.path.join(out_dir, f"{base}-{n}.md")

    slug = os.path.splitext(os.path.basename(candidate))[0]
    frontmatter = "\n".join([
        "---",
        f"title: Graphify Lint Sync {today}",
        "type: synthesis",
        "status: stub",
        f"slug: {slug}",
        f"created: {today}",
        "tags: [lint, graphify]",
        "sources: []",
        "---",
    ])
    summary = (
        "Auto-generated lint synthesis derived from the latest graphify run. "
        "It lists missing hub pages, orphan nodes, and surfaced graph "
        "questions so they can be turned into properly sourced wiki pages. "
        "This page is a stub and is not source-grounded yet; it must be "
        "filled with real, cited sources before it can pass the lint gate."
    )

    # Demote the embedded report's H1 so the page keeps a single H1 (BSB rule).
    embedded = re.sub(r"(?m)^# ", "## ", report_md.strip())

    body = "\n\n".join([
        frontmatter,
        f"# Graphify Lint Sync {today}",
        summary,
        embedded,
        "## Sources",
        "- (stub) No external sources yet; populate per CLAUDE.md s1.5 before "
        "promoting beyond status: stub.",
    ])

    with open(candidate, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body.rstrip() + "\n")
    return candidate


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="graphify_sync.py",
        description=(
            "Bridge graphify outputs (graphify-out/) into the source lint "
            "loop: derive missing hub pages, orphan nodes, and surfaced "
            "graph questions. Does NOT run graphify itself."
        ),
    )
    parser.add_argument(
        "root", nargs="?", default=".",
        help="Repository root (default: .).",
    )
    parser.add_argument(
        "--top-n", type=int, default=DEFAULT_TOP_N,
        help=f"Number of god/hub nodes by degree (default: {DEFAULT_TOP_N}).",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Also write a lint stub to wiki/syntheses/lint-graph-YYYY-MM-DD.md.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    repo_root = os.path.abspath(args.root)

    report_md, ctx = build_report(repo_root, args.top_n)
    print(report_md)

    if args.write and (ctx["have_graph"] or ctx["have_report"]):
        path = write_stub(repo_root, report_md)
        rel = os.path.relpath(path, repo_root).replace("\\", "/")
        print(f"\nWrote lint stub: {rel}")
    elif args.write:
        print(
            "\n--write skipped: no graphify artifacts to synthesize.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
