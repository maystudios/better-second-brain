---
type: source
title: "Git diff review documentation"
source-url: https://git-scm.com/docs/git-diff
source-kind: docs
author: Git project
published: 2026-06-29
ingested: 2026-09-01
created: 2026-09-01
updated: 2026-09-01
tags: [software/git, version-control, code-review, primary-source]
status: verified
---

# Git diff review documentation

Git's primary manual for comparing working-tree, index, and committed states.

## Key claims

- Plain `git diff` compares the working tree with the index; `git diff --cached` compares the index
  with `HEAD`, which is the staged commit candidate.
- `--name-only` reports only changed paths. `--stat` reports per-file scale, while the default patch
  shows the actual hunks.
- File-set, change-scale, and patch-content review are distinct checks and answer different questions.

## Connections

- Grounds the review ladder in [[wiki/concepts/shared-worktree-commit-integrity]].
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://git-scm.com/docs/git-diff
