---
type: source
title: "Git commit pathspec documentation"
source-url: https://git-scm.com/docs/git-commit
source-kind: docs
author: Git project
published: 2026-06-29
ingested: 2026-09-01
created: 2026-09-01
updated: 2026-09-01
tags: [software/git, version-control, commits, primary-source]
status: verified
---

# Git commit pathspec documentation

Git's primary manual for what `git commit` records from the index, working tree, and path arguments.

## Key claims

- A plain `git commit` records the current index; listing tracked paths instead records the current
  contents of those files and ignores unrelated changes already staged.
- A commit pathspec selects files. It does not express hunk ownership inside a selected file.
- `--dry-run` previews included, excluded, and untracked paths, but a path list alone does not show
  the size or meaning of the selected files' changes.

## Connections

- Grounds [[wiki/concepts/shared-worktree-commit-integrity]].
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://git-scm.com/docs/git-commit
