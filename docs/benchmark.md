# Benchmark: Is BSB Actually Better Than a Vanilla LLM Wiki?

BSB claims to beat a plain Karpathy-style LLM wiki on cross-linking, freshness, and trustworthy citation. This page describes a concrete, runnable experiment to *measure* that claim instead of asserting it: two arms built from the same raw corpus, a fixed question set, a scoring rubric, and an honest protocol that records negative results too. The output of a run is a synthesis page at [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]].

The point of writing this down is the same as the research-discipline gate (CLAUDE.md §1.5): a claim that BSB is better is itself a claim, and it must be supported by evidence, not memory.

> **Results so far (2026-06-19).** This benchmark has been run three times (`uv`, `MCP`, `Ruff`), and a third arm -
> **`bsb-lean`** (the optimized fill mode, CLAUDE.md §2.1) - was added. Headlines: BSB beats a vanilla wiki by
> **+5-12%**, driven by *citation/verifiability*; reading a wiki is **2-18× cheaper** than reading raw; and
> **`bsb-lean` matches full-BSB quality at -66% fill tokens**. Full tables + honest caveats:
> **[`../benchmark/RESULTS.md`](../benchmark/RESULTS.md)**.

## The two arms

Both arms ingest the **same `raw/` corpus** so the only variable is the system, not the inputs.

- **Arm A - Vanilla Karpathy wiki.** Build a plain LLM wiki from `raw/` using only the base pattern: three layers (raw / wiki / schema), manual ingest, no graphify graph, no auto-research improve loop, no self-healing lint. This is the control.
- **Arm B - Full BSB.** The same corpus, but with the BSB layers enabled: the graphify knowledge graph, the auto-research improve loop, self-healing freshness lint, and the source-lint gate.

Keep both arms in separate working copies (for example separate folders or git branches) so neither contaminates the other, and freeze the corpus before you start.

## The question set

Write **15-25 questions** over the bootstrap corpus, deliberately mixing three categories so the benchmark exercises the specific places BSB is supposed to win:

1. **Single-source recall (about one third).** Facts answerable from one document. Tests basic correctness; both arms should do well, so this is the floor.
   - Example: "What is the PyPI package name for graphify?" (Answer: `graphifyy`, double-y.)
2. **Multi-hop synthesis (about one third).** Questions that require connecting two or more sources written separately. This is where graphify's cross-links should help.
   - Example: "Which BSB layer addresses retrieval and which addresses traversal, and how do they differ?" (qmd vs. graphify.)
3. **Freshness / 'is this still current' (about one third).** Questions whose correct answer is that a claim may be outdated, or that depend on the latest version of a source. This is where self-healing lint should help.
   - Example: "Is Obsidian Bases still a community plugin?" (No - it shipped as a *core* plugin in Obsidian 1.9, 2025-05-21. A stale wiki may still say "community plugin.")

Store the question set alongside the synthesis page so a re-run uses the identical set. Note expected answers and the source that supports each, so scoring is not from the grader's memory.

## The rubric

Score every answer, from both arms, on four axes. Use a small integer scale (0-2) per axis so totals are easy to compare.

| Axis | What it measures | 0 | 1 | 2 |
| --- | --- | --- | --- | --- |
| **Correctness** | Is the answer factually right vs. the corpus? | Wrong | Partly right | Fully right |
| **Citation quality** | Does it cite a real, checkable source for its claim? | No citation / fabricated | Cites but imprecise | Cites the correct real source |
| **Freshness** | Does it catch outdated claims when they exist? | Repeats stale claim | Hedges vaguely | Flags the outdated claim correctly |
| **Token cost** | Tokens consumed to produce the answer | record the raw number | - | - |

Correctness, citation, and freshness are quality axes (higher is better). Token cost is recorded as a raw number per answer (lower is better) and reported separately - do not fold it into the quality score. A cheaper wrong answer is not a better answer.

Citation quality is the axis most likely to expose the difference: an unconstrained vanilla wiki can produce a confident answer with a fabricated or absent source, which should score 0 here even when correctness is 2.

## The protocol (lightweight, agent-runnable)

An agent can run this end-to-end using the workflow/agent harness:

1. **Freeze the corpus.** Snapshot `raw/`. Both arms use exactly this snapshot.
2. **Build Arm A.** Ingest the frozen corpus into a vanilla wiki (base pattern only).
3. **Build Arm B.** Ingest the same corpus into full BSB (all layers on; run the improve loop and lint to convergence).
4. **Ask the question set against each arm.** For each question, record: the answer text, the four rubric scores, and the token cost. Ask the same question to both arms before moving on, to keep grading conditions comparable.
5. **Grade blind where possible.** Have the grader score answers without knowing which arm produced them (strip arm labels), to reduce bias toward the expected winner.
6. **Aggregate.** Mean score per axis per arm, plus the token-cost distribution per arm. Break results out by question category (recall / synthesis / freshness) - BSB is expected to win mostly on synthesis and freshness, and the per-category split tells you whether that prediction held.
7. **Write it up** in [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]].

## Recording results

The synthesis page at [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]] should contain, with normal BSB frontmatter and a closing `## Sources` section:

- The frozen corpus identifier (commit hash or snapshot date) and the exact question set.
- A per-axis results table for Arm A and Arm B, plus the per-category breakdown.
- Token cost per arm (total and per-answer mean).
- A short narrative of where each arm won and lost, with concrete examples.
- A clear verdict - including "no significant difference" or "vanilla won on axis X" if that is what the data shows.

## The honesty rule and small-N caveats

- **Report negative results.** If BSB ties or loses on an axis, that goes in the synthesis verbatim. A benchmark that can only confirm the hypothesis is marketing, not measurement. This is the same discipline the rest of BSB runs on.
- **Acknowledge small N.** 15-25 questions over one bootstrap corpus is a small sample. Treat results as directional, not statistically significant; do not report false-precision percentages. State the N and the corpus on the page so a reader can weigh the result.
- **Re-run on changes.** When the corpus or the layers change, re-run the same question set and append a dated result, so the page shows a trend rather than a single frozen claim.

## Sources

- Karpathy, "LLM Wiki" gist (the vanilla pattern that Arm A reproduces) - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- graphify (the cross-link/traversal layer tested in Arm B) - https://github.com/safishamsi/graphify
- qmd (the retrieval layer referenced in the synthesis question) - https://github.com/tobi/qmd
- Obsidian Bases as a core plugin in 1.9, 2025-05-21 (basis for the freshness example) - https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/
- Atlan, "LLM Wiki vs RAG Knowledge Base" (limits to weigh when interpreting results) - https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/
