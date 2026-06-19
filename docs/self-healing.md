# Self-Healing (BSB §3.6)

The autonomous correctness loop. The premise is simple and follows directly from the §1.5 research-discipline gate: because every page in the Brain cites its sources, the Brain can re-verify itself. A page is not a static assertion - it is a claim plus the URLs that back it. That makes each page checkable, and a checkable page is a fixable page. Self-healing is the loop that re-fetches those sources, detects where a page has drifted from reality, and re-grounds it - visibly, with a log entry, and within autonomy limits you set.

## DETECT

A heal pass re-fetches each page's cited sources and diffs the current source against what the page asserts. It flags:

- **Superseded versions** - the page documents version *N*, the source's current release is *N+1* (or the source itself is marked deprecated/superseded).
- **Changed APIs / signatures** - a function signature, flag, default, or endpoint the page documents no longer matches the current source.
- **Dead or redirected URLs** - a cited link 404s, times out, or 301-redirects to a different canonical location.
- **Unsupported claims** - the source no longer says what the page attributes to it (text changed, section removed). Never silently keep a claim the source dropped.
- **Source-grade tier failures** - pages that fail the grading run `scripts/lint_sources.py --strict` (e.g. a claim resting only on a community/secondary source where a primary is now required).
- **graphify low-confidence edges** - `AMBIGUOUS` or otherwise low-confidence edges from graphify (§3.4) that touch the page, indicating a relationship the corpus does not firmly support.

## REPAIR

When a page is flagged, the repair is *not* a silent overwrite:

1. **Re-ground in current sources.** Re-read the live source and rewrite the affected claim to match it, keeping the citation pointed at the now-current URL.
2. **Bump metadata.** Update `stack-versions` and the `updated` date in the frontmatter.
3. **Record the correction visibly in the body.** Add a short, dated note in the page body stating what changed (old -> new) and which source confirmed it. The history must be legible to a reader, not buried in a diff.
4. **Append a `heal` log entry** to [[log]] describing the page, the detected drift, and the fix.

This preserves §1.5: a healed page is still fully grounded, and the change is auditable.

## Autonomy levels

Each heal action runs at one of three levels. The **default is level 2**, and any area can override it (set a stricter or looser level per folder/topic):

- **Level 1 - report-only.** Detect and report drift; make no edits. Use for sensitive or high-stakes areas.
- **Level 2 - fix-on-approval (default).** Propose the re-grounded edit and the log entry; a human approves before it lands.
- **Level 3 - autonomous.** Apply the fix without prompting - *only* for high-confidence, well-sourced corrections, the canonical case being a version bump confirmed verbatim by the official changelog.

**Hard floor:** no level ever auto-fixes below the research-discipline floor. If a repair would require asserting something not supported by a real, current source, the loop stops and downgrades to report-only regardless of the configured level. Level 3 is for mechanical, source-confirmed corrections, never for inventing replacement claims.

## Worked example

A cheatsheet page documents a library at `v3.x`. A heal pass re-fetches the cited official changelog and detects a new major release, `v4.0`, with two of the documented flags renamed.

- **Detect:** `stack-versions` says `3.4`; the changelog's latest tag is `4.0.1`; two cited flag names no longer appear in the current docs. Flagged as *superseded version* + *changed signatures*.
- **Classify autonomy:** the version number itself is confirmed verbatim by the official changelog -> the version bump qualifies for level 3. The flag *renames*, however, require rewriting example commands and re-reading the migration guide -> those drop to level 2 (fix-on-approval), because they are substantive rewrites rather than a mechanical bump.
- **Repair:** bump `stack-versions` to `4.0.1` and `updated` to `2026-06-19`; rewrite the two flags against the current docs; add a body note: "Updated 2026-06-19: bumped 3.4 -> 4.0.1; `--old-flag` renamed to `--new-flag` per the v4 migration guide (cited below)."; append a `heal` entry to [[log]].

The reader sees exactly what changed and why, and the citation now points at the current source.

## Suggested schedule

- **Monthly heal pass** across the wiki at the default level 2, surfacing a batch of proposals to review.
- **Trigger on graphify drift** - when a graphify `--update` (§3.4) introduces new `AMBIGUOUS` edges or shifts god nodes, run a targeted heal pass over the affected pages rather than waiting for the monthly cycle.

This is the loop that answers the obvious question directly: *a doc in the Brain has an error - the Brain detects it against its own cited sources and fixes it, visibly and on the record.*

## Sources

- Andrej Karpathy, "LLM Wiki" gist (cross-references and flagged contradictions as a maintained property of the wiki) - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- graphify repository (the AMBIGUOUS/low-confidence audit trail this loop consumes) - https://github.com/safishamsi/graphify
- LLM-Wiki vs RAG, on freshness and manual-lint limitations a self-healing loop addresses - https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/
