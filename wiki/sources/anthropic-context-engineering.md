---
type: source
title: "Anthropic - context engineering & token/latency levers (docs)"
source-url: https://platform.claude.com/docs/en/build-with-claude/context-editing
source-kind: docs
author: Anthropic
published: 2026
ingested: 2026-06-23
created: 2026-06-23
updated: 2026-06-23
tags: [topic/llm, context-engineering, tokens, latency, prompt-caching, primary-source]
status: verified
---

# Anthropic - context engineering & token/latency levers (docs)

Anthropic's current API surface gives concrete, composable levers for cutting **tokens and latency at the same time** -
the menu of "method mutations" BSB's RSI loop draws candidate levers from ([[wiki/syntheses/bsb-rsi-loop]]). These are
the moves a markdown-wiki agent can actually adopt, each measurable by `scripts/token_report.py` and wall-clock.

## Key claims

- **Server-side context editing** (beta `context-management-2025-06-27`): `clear_tool_uses_20250919` clears old tool
  results with no inference cost, measured **48-67% peak-token reduction** in Anthropic's cookbook; `exclude_tools`
  keeps named tools (e.g. `memory`) intact. For BSB: clear `WebFetch`/`Read` results after they are distilled into a
  lean source page, keeping the page (the persistent artifact) and dropping the raw bulk.
- **Prompt caching**: cache reads cost **0.1x** base input price and cut latency **up to ~85%** for long stable
  prefixes; 5-min writes (1.25x, break-even 1 read) or 1-hour (2.0x, break-even 2 reads). For BSB: cache the stable
  CLAUDE.md + schema prefix so every session after the first hits cache. Caveat: a speed switch (fast<->standard) or
  any change before the breakpoint busts the cache.
- **Sub-agent context isolation**: subagents pass lightweight artifact references back, not full tool output, keeping
  the orchestrator context small - Anthropic's multi-agent research system (Opus lead + Sonnet subagents) is the
  reference design. Token volume explains **~80% of quality variance** in those evals; multi-agent uses ~15x the
  tokens of chat, so naive fan-out on simple tasks is a net loss.
- **Model tiering** (Haiku<Sonnet<Opus, ~5x cost spread) routed per workflow step typically yields **30-50% cost
  reduction** at equal quality. **Fast mode** raises Opus output tokens/sec up to ~2.5x (gain is on throughput, not
  time-to-first-token).
- Caveat for the metric: the Opus 4.7+ tokenizer emits up to **~35% more tokens** for the same text than older models,
  so token baselines must be normalized by model generation before comparing across time.

## Connections

- Supplies the cost/latency levers in [[wiki/syntheses/bsb-rsi-loop]]; the isolation/fan-out pattern is the same one
  [[wiki/entities/graphify]]-style traversal and BSB's research workflow already exploit.
- Token/latency are the two minimized objectives in [[wiki/concepts/multi-objective-optimization]].
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://platform.claude.com/docs/en/build-with-claude/context-editing ; https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools
- https://platform.claude.com/docs/en/build-with-claude/prompt-caching ; https://platform.claude.com/docs/en/build-with-claude/fast-mode ; https://platform.claude.com/docs/en/about-claude/pricing
- https://www.anthropic.com/engineering/multi-agent-research-system (sub-agent isolation; token = 80% of quality variance)
