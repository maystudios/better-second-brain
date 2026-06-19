# auto-research Integration (BSB §3.5)

How the `auto-research` skill makes the Brain's *method* improve over time. Karpathy's wiki pattern keeps the synthesis fresh but leaves the *schema* - the conventions in [[CLAUDE]], the page templates, the lint rules - static. `auto-research` is the loop that closes that gap: it researches authoritative best-practice sources, proposes a cited rewrite of a target markdown file, and validates the rewrite with an automatic eval loop before anything is accepted. Running it periodically against the Brain's own rulebook is what lets the method compound instead of ossifying.

## What auto-research does, at a high level

`auto-research` improves an existing markdown file (a `SKILL.md`, a `CLAUDE.md`, a subagent definition, a slash-command, or any prompt-shaped doc). Its loop:

1. **Research.** It dispatches parallel specialist sub-agents (docs-expert, repo-expert, blog-expert, community-expert) against authoritative sources and caches the findings per topic.
2. **Propose.** It writes a *cited* rewrite of the target file, grounded in what the sub-agents found rather than from memory.
3. **Validate.** It runs format checks plus a Karpathy-style **binary eval loop** (each candidate is scored pass/fail against explicit criteria; it explores N hypotheses per iteration via beam search) and an optional **trigger-eval** that scores whether a skill's description fires on the right user prompts.
4. **Gate.** It stops at a final confirmation gate, presenting a before-and-after score and the full source list. Nothing is merged without approval.

## BSB usage

### 1. Improve the SCHEMA - run it against CLAUDE.md

Periodically point `auto-research` at [[CLAUDE]] to fold in newer PKM, Obsidian, and LLM-wiki best practices (for example, changes in Obsidian Bases syntax, new Zettelkasten/PARA guidance, or refinements to Karpathy's wiki pattern). The proposed diff is **not** applied automatically: it goes through the §7 approval gate, and once accepted you add a `schema` entry to [[log]] recording what changed and why. This keeps the rulebook evolving on evidence, with a paper trail.

### 2. Improve PAGE FORMATS - run it against templates/

Point it at `templates/` and at the page-format section of [[CLAUDE]] to refine the frontmatter keys, section ordering, and the required `## Sources` discipline as best practices shift. Same flow: cited rewrite -> eval loop -> approval -> log entry.

### 3. Cadence and guardrails

- **Cadence:** run a schema/format pass on a deliberate schedule (e.g. quarterly, or when a major Obsidian/PKM release lands), not continuously. Method changes should be rare and considered.
- **Never relax the research-discipline gate.** §1.5 is the floor. `auto-research` may propose tightening or clarifying it, but a proposed diff that *weakens* the requirement to ground pages in real, cited sources is rejected at the gate, full stop.
- **Keep changes minimal.** Prefer the smallest rewrite that captures the new best practice. Large rewrites are harder to review and harder to trust.
- **Everything is git-reviewed.** The proposed diff is reviewed as a normal change; the eval score informs the decision but does not replace human approval.

## Concrete invocation

Improve the schema file:

```text
/auto-research improve C:/Users/conta/Documents/Second Brain/CLAUDE.md
```

Or, in natural language inside a Claude Code session: "use auto-research to improve CLAUDE.md with the latest PKM and Obsidian best practices."

### Reading the before/after score

At the gate, `auto-research` reports a before score and an after score from its binary eval loop (the fraction of eval criteria the file passes), plus the source list behind the rewrite. Read it like this:

- **After clearly higher than before:** the rewrite genuinely satisfies more criteria - a candidate worth merging, pending your review of the actual diff.
- **After roughly equal to before:** the rewrite is cosmetic; decline it to avoid churn.
- **After lower, or sources thin/uncited:** reject. A drop or weak sourcing means the proposal failed its own eval or was not properly grounded - exactly the case §1.5 exists to catch.

The score is a signal, not a verdict. The diff and its sources are what you approve.

## Why this is the compounding loop

Karpathy's wiki pattern compounds *knowledge*: every new source improves the synthesis. `auto-research` compounds *method*: every pass improves the conventions that govern how that synthesis is written. Together they mean the Brain gets better at *being a brain*, not just fuller - and the §1.5 gate guarantees that improvement never comes at the cost of grounding.

## Sources

- `auto-research` skill (installed; loop, sub-agents, binary eval, trigger-eval, confirmation gate) - local skill definition
- Andrej Karpathy, "LLM Wiki" gist (the wiki pattern whose method this loop keeps current) - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Andrej Karpathy, "LLM Knowledge Bases" (X post, primary announcement; not directly fetchable behind login) - https://x.com/karpathy/status/2039805659525644595
