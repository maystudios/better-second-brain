# Validation on a real, pre-existing second brain (368 pages)

The benchmarks in [`RESULTS.md`](./RESULTS.md) build a corpus from scratch. This one is stronger evidence: BSB's
graph layer was applied to a **real, already-existing, vanilla-Karpathy second brain** — a 368-page game-development
LLM-wiki built by hand over months, in a domain BSB knows nothing about — to test whether the method transfers to
brains other people already have.

*(The vault is private user content and is not included in this repo; only the methodology and numbers are.)*

## What was done

1. Copied the untouched 368-page vault (concepts 201, sources 59, entities 40, games 35, topics 18, …).
2. Ran `/graphify` over it → a **382-node, 2,161-edge, 9-community** knowledge graph. The god nodes came out as the
   real pillars of the vault (the GAS/Lyra technical cluster, Horror Game Design, Level Design). **graphify ran
   cleanly at this scale** — confirming the method works on a real, large, third-party brain.
3. Answered **7 grounded questions** (2 single-hop, 4 multi-hop/interconnection, 1 broad design-spec) two ways, with
   the **same model and effort**:
   - **normal** — vanilla Karpathy: read `index.md`, follow wikilinks, read pages in full.
   - **improved** — run `graphify query` to locate the right pages, read only those (no `index.md`).
4. Scored both arms against a grounded gold answer set, and measured token cost two ways.

## Result

| Metric | normal | improved | improved |
|---|--:|--:|--:|
| **Real tokens** (full run) | 378,720 | 291,961 | **−23%** |
| **Read-footprint** (pages loaded, tiktoken) | 166,821 | 72,707 | **−56% (2.29×)** |
| `index.md` re-reads | 7 × ≈9.7k tok | 0 | eliminated |

- **Quality: the graph arm ties or beats the read-everything arm on all 7 questions.** Six are full-mark parity
  (including every multi-hop interconnection question — the GAS damage-pipeline chain, the cross-game audio-cue
  grouping, the three-game wayfinding comparison, the monster-coupling cluster).
- The single broadest task ("synthesize ~20 specific pages into a design spec, cite each") needed a **coverage-aware
  query strategy** — query per sub-topic, traverse each concept to its exemplar page via `graphify explain`/`path`,
  then a completeness check. With it, the graph arm reached parity with reading the whole corpus at **−38% tokens**.
  That lesson is now baked into the method ([`../docs/graphify-integration.md`](../docs/graphify-integration.md),
  `CLAUDE.md` §3.2).

## Honest caveats

- Small N (7 questions, one vault, one model). Directional, not a leaderboard.
- The broadest "cite everything" task is hard for *either* arm — neither hits perfect coverage; the graph's edge is
  reaching the same answer for far fewer tokens, not infinite recall.
- Scoring is sensitive to **judge variance** — compare arms with a single head-to-head judge (we did).
- This exercised the **read/query + graph** side. The *fill*-side gains (lean §2.1, the §1.5 research gate,
  self-heal) apply going forward / via a one-time backfill, since a pre-existing vault's pages aren't lean or
  source-graded.

**Bottom line:** the BSB method transfers to a real, existing Karpathy-style brain — same answer quality at roughly
half the read cost — and the one rough edge it surfaced was fixed and folded back into the method.
