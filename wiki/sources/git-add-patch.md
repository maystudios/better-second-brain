---
type: source
title: "Git add and interactive patch documentation"
source-url: https://git-scm.com/docs/git-add
source-kind: docs
author: Git project
published: 2026-06-29
ingested: 2026-09-01
created: 2026-09-01
updated: 2026-09-01
tags: [software/git, version-control, staging, primary-source]
status: verified
---

# Git add and interactive patch documentation

Git's primary manual for staging whole files or selected hunks in the index.

## Key claims

- `git add <path>` stages that file's contents as they exist when the command runs; later edits need
  another add to enter the index.
- `git add -p` lets the user review and stage individual hunks between the index and working tree.
- Interactive mode can split or edit hunks and includes a diff view of what will be committed.

## Connections

- Supplies the hunk-level alternative in [[wiki/concepts/shared-worktree-commit-integrity]].
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://git-scm.com/docs/git-add
