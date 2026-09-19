# Optional Jev gateway

Jev is a small TypeSafe classification model. This layer uses it to prioritize
local knowledge candidates and review bounded maintenance diffs. It does not
replace the agent, the instance schema, full-page reading, or source checking.
New installations default to **off**. Disabled queries make no API calls.

## Install and configure

Python 3.10+ and the standard library are sufficient. From the brain root:

```sh
python scripts/init_brain.py --jev on
python scripts/bsb_jev.py configure --status
python scripts/bsb_jev.py configure --enabled off
python scripts/bsb_jev.py configure --enabled on --install-hooks
python scripts/bsb_jev.py configure --enforce-reads on --install-hooks
```

To upgrade an existing brain without reinitializing its notes or domain rules,
run this from an updated Better Second Brain checkout:

```sh
python scripts/install_jev.py --target /path/to/existing-brain --enabled on --hooks
```

The upgrader backs up all managed files under `.bsb-jev/install-backups/`, copies
the gateway, appends a small instruction block, and merges hook configuration.
It does not rewrite wiki pages, raw sources, or historical logs. Review the
returned manifest. Use `--dry-run` to list changes without writing anything.
Explicit `--roots brain/observations,brain/claims,brain/moc` supports a read-only
harness lookup adapter; that layout is not reinitialized as a BSB wiki.

Set `TYPESAFE_API_KEY` through your secret manager/environment. On Windows an
existing per-user DPAPI file at `~/.config/harness-workflow/typesafe-key.dpapi`
is also supported; `TYPESAFE_KEY_FILE` overrides that encrypted file location.
Never put keys into tracked config, prompts, requests, or notes. The gateway
sends selected snippets, search questions, or exact mutation diffs plus cited
source excerpts to `https://api.typesafe.ai/v1/systemone`. It does not upload
the entire vault. The pinned default model is `jev-1.13.0`.

### Cost accounting

TypeSafe currently lists Jev at `$0.042` per million input tokens; output tokens
are free. The gateway reports Jev input, cached-input and output usage so a caller
can calculate its own addition. On the 2026-09-19 Luna navigation trial, 174,726
reported input/cached-input tokens correspond to about `$0.0073` at that list
price. The figure is an API list-price estimate, not a subscription or host quota
charge. Keep the expensive model's input and output usage beside Jev's usage when
comparing a complete task. See [TypeSafe's model reference](https://docs.typesafe.ai/models)
for the current price and billing rule.

## Query and advice

### Progressive reading (experimental, opt-in)

The progressive path lets Jev choose which complete pages to read for explicit
subquestions. A local scanner supplies bounded candidates; Jev classifies each
page's question-focused windows as direct, partial, contrary, unrelated or unknown.
The gateway offers an initial set covering the needs, retaining contrary evidence.
It keeps the remaining descriptors available without returning all their full text.

```sh
python scripts/bsb_jev.py navigate "Why are replicated updates delayed?" --need "Cause of delay" --need "Exact configuration fix"
python scripts/bsb_jev.py read nav-<id> wiki/cheatsheets/example.md
python scripts/bsb_jev.py next nav-<id> --need "Missing configuration detail"
python scripts/bsb_jev.py source "https://example.org/specific-source"
```

Use the session ID and offered paths actually returned by the command. `read`
returns a whole page, verifies its recorded hash, and discovers outgoing wikilinks.
`next` asks Jev about unread linked pages and deferred candidates. Repeat for
unanswered needs; do not confuse provisional coverage with a verified answer.
There are at most four expansion steps per session, sixteen candidates per step
and eight bounded Jev requests per step. At the bound, narrow the question or use
an explicitly reviewed alternative retrieval route; do not conclude absence.
Disabled/API-failure plans offer the full bounded pool. `--dry-run` sends nothing.

`source` performs case-insensitive **literal** occurrence and title/alias lookup
locally, with zero API calls. It returns scan coverage, matching paths and a
session ID whose matches can be read in full. A hit means the literal appears,
not that the surrounding statement is true.
No hit is scoped to scanned Markdown in configured roots, with explicit exclusions
and size limits. Neither 10% nor 50% model confidence establishes global absence.

This follows TypeSafe's [hierarchical classification pattern](https://docs.typesafe.ai/cookbooks/hierarchical_classification)
while retaining alternatives for retrieval. The caller must still verify full
pages, citations and missing evidence. Classifier diagnostics stay in ignored
local navigation receipts; the normal command response omits excerpt copies and
per-choice distributions to avoid loading them into the expensive agent context.

```sh
python scripts/bsb_jev.py query "Which pages explain this decision?" --json
python scripts/bsb_jev.py advise placement "New information about topic X" --json
python scripts/bsb_jev.py advise link "Connections between X and Y" --json
python scripts/bsb_jev.py advise unlink "Check whether X still relates to Y" --json
python scripts/bsb_jev.py advise delete wiki/concepts/obsolete.md --json
python scripts/bsb_jev.py advise evidence_check "Claim to investigate" --json
python scripts/bsb_jev.py advise error_triage "Failure to investigate" --json
```

Queries use bounded BM25-style lexical retrieval with title/alias weighting,
one candidate per document, then Jev classifications. **All candidates in that
bounded pool are returned by default**, including unknown, low-ranked, and
contradictory evidence. `priority_ids` identifies where to start reading.
`--limit` changes that priority count. Full-page reads are still required.
The advice commands prioritize potentially relevant local evidence; they do
not autonomously prove claims, create links, or authorize deletion.

No-hit results and low scores never establish global absence. Expand terms,
read indexes and linked pages, or use another authorized retrieval route when
coverage is inadequate. The candidate pool is at most 16 documents; scanning
is bounded to 10,000 Markdown files / 20 MiB, excluding oversized files, hidden
folders and linked paths. Query output reports coverage limitations. API or
credential failure returns the entire lexical pool with `status: fallback`.

`--dry-run` sends nothing. `--prune` is an explicit experimental option;
the [Gemini pilot](../benchmark/JEV-2026-09-19.md) failed the quality gate for
hard pruning. No production quality improvement or net token saving is claimed.
Probability/confidence is the model's classification score, not calibrated
proof that a source exists or that a statement is true.

## Reversible maintenance

Read the full affected pages and actual sources first. Build a request JSON
with `reason` and 1–8 `mutations`. Each mutation has `action`, `path`, optional
`content`, `citations`, and the current SHA-256 `base_hash` for existing files.
Paths are relative, forward-slash paths. Example insert:

```json
{
  "reason": "Record a source-grounded concept requested by the user",
  "mutations": [{
    "action": "insert",
    "path": "wiki/concepts/example.md",
    "content": "# Example\nA verified statement. [[wiki/sources/source]]\n",
    "citations": [{"path": "raw/source.md", "start_line": 1, "end_line": 8}]
  }]
}
```

This minimal example describes the transport format, not the required page
schema: preserve the instance's frontmatter, provenance, source-count floor,
language, link convention and indexes. Insert/edit require actual local source
paths or line spans, not citation strings invented by the model. Jev sees the
exact diff and those excerpts (24 KiB total request cap); split larger changes.

```sh
python scripts/bsb_jev.py plan request.json --out reviewed-plan.json
python scripts/bsb_jev.py apply reviewed-plan.json --approve --dry-run
python scripts/bsb_jev.py apply reviewed-plan.json --approve
python scripts/bsb_jev.py rollback plan-<identifier>
```

`--approve` records the caller's review of this exact plan. Existing task
authorization can satisfy that review; it does not inherently require another
user confirmation. Enabled mutations require a successful Jev `ready` review;
outages or uncertain/rejected reviews stop writes. A review is advisory and
never a substitute for schema/source validation by the calling agent.

Use `edit` to add/remove links. Removing a referenced page requires unlinking
all live backlinks in the same transaction (or beforehand). Index/roadmap edits
are supported. Logs support only `append`; pass only the new suffix as content.
Raw sources and schema files cannot be changed by this gateway. Historical logs
are excluded from live backlink checks so an old event can mention a removed
page without preventing future maintenance.

Plans are locally signed and checked against their stored canonical copy.
Apply rechecks target and evidence hashes, final backlinks, and append-only
history. All backups precede changes. Failures attempt byte-exact restoration
and report incomplete restoration explicitly. Rollback refuses to overwrite
subsequent edits, including a recreated deleted file. A plan cannot be replayed.
Operations serialize through `.bsb-jev/operation.lock`; inspect interrupted
work and backups before manually clearing a stale crash lock. Multi-file writes
are recoverable but are not a filesystem-wide atomic transaction.

## Hooks and enforcement boundary

Enabling with `--install-hooks` merges these native configurations:

| Host | Configuration | Gate |
| --- | --- | --- |
| Antigravity | `.agents/hooks.json` | Supported native search/write/read/shell tools |
| Claude Code | `.claude/settings.json` | Grep, Edit, Write, Read, Bash |
| Codex | `.codex/hooks.json` | apply_patch and matching native read/search/shell tools |

The basic hook blocks direct protected writes and native wiki searches. With
`enforce_reads` enabled, supported native wiki reads and arbitrary shell commands
are also routed through the gateway; narrowly parsed gateway commands remain
available. New `init_brain.py --jev on` and the existing-brain installer enable
this stricter mode. Read schema/index/roadmap instructions normally; retrieve wiki
evidence through session receipts. Turning Jev off makes
the hook neutral; `configure --uninstall-hooks` removes only this integration.
Other handlers are preserved. Codex must trust/review the repository hooks in
its host UI before they run. Host support and trust settings matter: installed
files alone do not prove active interception.

Explicit reads of immutable `raw/` sources remain available for primary-source
grounding; they are not general wiki search. Schema/index/roadmap and files outside
the protected brain content also remain readable. Source-count gates still apply.

Antigravity denial was verified with a real Gemini tool call. Claude/Codex
payloads and installers have process/contract tests; their live model sessions
were not verified in this pilot. Unsupported wrappers, external processes and
specialized tools can bypass native hooks. Instructions prohibit that
bypass, but this is not an OS sandbox or a guarantee against a malicious agent.
Local signatures likewise protect against accidental/tampered plan data, not
an actor that can rewrite the gateway and its local signing key.

Change policy from your **own terminal**, since strict agent shell hooks refuse
configuration changes that would disable themselves:

```sh
python scripts/bsb_jev.py configure --enabled off
python scripts/bsb_jev.py configure --enabled on --enforce-reads on --install-hooks
python scripts/bsb_jev.py configure --enforce-reads off
```

The last command keeps Jev enabled with the earlier search/write hooks. Strict
mode intentionally limits general-purpose shell work in that brain task; switch
it off for repository administration. This is host enforcement, not an OS sandbox.

Validation: `python -m unittest discover -s tests -p '*jev*.py'`.
For another brain, freeze questions and evidence before comparing complete
answers, citation coverage, abstention, total tokens, latency and paid calls.
Keep experiments on snapshots; never tune away a failed quality gate.
