---
type: source
title: "MayPaintworks multi-agent and evidence-gate observations"
source-path: "C:/Users/conta/Documents/ChatGPT/tf-wt-celshader2/RUNDOWN.md"
source-kind: docs
author: MayPaintworks build and verification run
published: 2026-09-01
ingested: 2026-09-01
created: 2026-09-01
updated: 2026-09-01
tags: [software/workflow, multi-agent, measurement, testing, primary-observation]
status: verified
---

# MayPaintworks multi-agent and evidence-gate observations

Primary-observation ledger from a multi-agent Unreal plugin run, restricted here to methods that
transfer to software work outside Unreal.

## Key claims

- Three whole-file sweeps occurred in one shared worktree. One message described a small header edit
  but committed 637 changed shader lines, leaving clean `HEAD` uncompilable while dirty local files
  masked the break. A filename-only staged check did not expose the payload; the diffstat did.
- A checker that cannot read its input must return a distinct incomplete state, not CLEAN. Likewise,
  a capture directory observed during a legitimate post-job processing window is undecidable until
  the producer's completion evidence exists.
- A metric change is not validated because it rescues a target. The new metric must leave the null
  null; otherwise it would rescue anything.
- A guard that cannot fail naturally needs a deliberate mutation on a copy. Controls that pass old
  and new implementations are non-regression evidence, not evidence of the fix.
- Provenance after exposure is anchored by a commit predating exposure, not by a current symbol that
  may have been renamed.

## Connections

- The Git mechanism is grounded by [[wiki/sources/git-commit-pathspec]],
  [[wiki/sources/git-add-patch]], and [[wiki/sources/git-diff-review]].
- Generalised in [[wiki/concepts/shared-worktree-commit-integrity]].
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: `C:/Users/conta/Documents/ChatGPT/tf-wt-celshader2/RUNDOWN.md` — current-run header above `# PRIOR RUN — CelPaint`
- PRIMARY: `C:/Users/conta/Documents/ChatGPT/tf-wt-celshader2/evidence/paintworks/verifier/P_resume_state_verifier.md`
- PRIMARY: `C:/Users/conta/Documents/ChatGPT/tf-wt-celshader2/evidence/paintworks/handoff/P2a_fix_report.md`
- PRIMARY: `C:/Users/conta/Documents/ChatGPT/tf-wt-celshader2/evidence/paintworks/handoff/P2a_lines_orchestrator_ruling.md`
