# Branching retrieval v1 — acceptance contract

Frozen for the implementation requested on 2026-09-19. Existing source, write and rollback
gates remain. This is a retrieval feature, not a claim of measured token savings.

Public Python entry point: `scripts.bsb_jev_search.find(query, needs=None, repo_root=None,
dry_run=False, transport=None, api_key=None, max_calls=24, max_pages=12)`.
CLI: `python scripts/bsb_jev.py find "question" [--need "subquestion"]
[--max-calls N] [--max-pages N] [--dry-run]`.

1. Build a bounded catalog from all allowed Markdown pages plus index/MOC relationships.
   No lexical overlap is required for admission. Include unindexed/unlinked pages.
2. Jev selects branches using descriptors before the gateway evaluates full page text
   (bounded contiguous chunks for large pages). Code owns all reads and traversal.
   A single find call internally backtracks and follows links without caller read turns.
3. Keep unvisited alternatives, prevent cycles/repeated page evaluation and enforce
   hard request/page budgets. Report incomplete catalog, unread text and unvisited pages.
4. Evaluate explicit needs (or the original question by default), evidence adequacy and
   conflicts separately. Selection confidence cannot prove answer completeness or absence.
   Retain discovered conflicting and uncertain evidence. Return exact source line/hash
   references and unique full selected pages; no generated claims or snippets as facts.
5. Public output: `status`, `session_id`, `pages` (path, text, full_page, file_sha256),
   `evidence_refs`, `conflicts`, `unresolved_needs`, `coverage`, `usage`, `api_calls`.
   Model diagnostics/full distributions stay in ignored local receipts, not the response.
   Status values include `ready` (provisional), `partial`, `unresolved`, `disabled`,
   `dry_run`, `unavailable`, `stale`. All outputs keep `global_absence_proven: false`.
6. Disabled/dry-run perform zero network calls. Invalid credentials/service responses
   produce explicit unavailable/partial results, never fabricated success or silent
   expensive-agent fallback. Path/link restrictions and snapshot freshness remain enforced.
7. CLI, strict gateway allowlist, installers and enabled-agent instructions expose find.
   Existing source/navigate/read/next/query and mutation contracts remain compatible.
   The activated route delegates index traversal to the gateway and requires the caller
   to read returned full-page content, sources and unresolved needs.
8. Verify with red-before-green behavioral tests and independent review. Run a bounded
   live TypeSafe fixture trial separately from mocked control-flow tests. Real quality,
   host enforcement and end-to-end savings claims require separate measured evidence.

Work graph (efficient): controller implements search engine; independent acceptance lane
owns new search tests; integration lane owns hooks/installers/docs; independent final
review checks this contract and result after machine gates. Attempt cap three before
reframing. Jev routing selected inherited Codex with low concentration (0.05); controller
retained that available candidate. Consultation used 694 input / 38 output tokens.
