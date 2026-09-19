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

## Query and advice

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
| Antigravity | `.agents/hooks.json` | Native search/write tools |
| Claude Code | `.claude/settings.json` | Grep, Edit, Write |
| Codex | `.codex/hooks.json` | apply_patch and matching native tools |

The hook blocks direct protected writes and native wiki searches, directing
agents to this gateway. Full-page reads remain available. Turning Jev off makes
the hook neutral; `configure --uninstall-hooks` removes only this integration.
Other handlers are preserved. Codex must trust/review the repository hooks in
its host UI before they run. Host support and trust settings matter: installed
files alone do not prove active interception.

Antigravity denial was verified with a real Gemini tool call. Claude/Codex
payloads and installers have process/contract tests; their live model sessions
were not verified in this pilot. Arbitrary shell commands, external processes
and specialized tools can bypass native hooks. Instructions prohibit that
bypass, but this is not an OS sandbox or a guarantee against a malicious agent.
Local signatures likewise protect against accidental/tampered plan data, not
an actor that can rewrite the gateway and its local signing key.

Validation: `python -m unittest discover -s tests -p '*jev*.py'`.
For another brain, freeze questions and evidence before comparing complete
answers, citation coverage, abstention, total tokens, latency and paid calls.
Keep experiments on snapshots; never tune away a failed quality gate.
